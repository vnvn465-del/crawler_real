# Crawler Real

크롤링 데이터를
**수집 → 파싱 → 저장 → 날짜별 비교 → API 조회**까지 이어지는 흐름을 직접 구현한 백엔드 학습 프로젝트입니다.

이 프로젝트는  
**"매일 결과값이 바뀌는 데이터는 데이터베이스에 어떻게 저장해야 하는가?"**  
라는 질문에서 출발했습니다.

**시점별 snapshot 구조로 저장하고 비교하는 방식**을 직접 구현하는 데 초점을 두었습니다.

---

## 1. 프로젝트 목적

- HTML 데이터를 수집하고 필요한 정보를 파싱한다.
- 변하는 데이터를 **날짜별 snapshot**으로 저장한다.
- 이전 시점과 비교하여 **신규 / 삭제 / 가격 변동 / 순위 변동 / 리뷰 수 변동**을 확인한다.
- 저장된 결과를 FastAPI 기반 API로 조회할 수 있도록 구성한다.
- 코드를 controller / service / repository 구조로 분리해 유지보수 가능한 형태로 정리한다.

---

## 2. 주요 기능

### 1) 데이터 수집

- `httpx` 기반 정적 HTML 수집
- `Playwright` 기반 동적 렌더링 페이지 대응 구조 분리

### 2) 데이터 파싱

- BeautifulSoup를 사용해 상품 목록 파싱
- 상품 ID, 순위, 이름, 가격, 리뷰 수 추출

### 3) 데이터 저장

- SQLite 사용
- 상품 기본 정보와 날짜별 상태 정보를 분리 저장

### 5) API 조회

- 최신 snapshot 조회
- 특정 날짜 snapshot 조회

---

## 3. 기술 스택

- Python
- FastAPI
- SQLite
- httpx
- BeautifulSoup4
- lxml
- Playwright

---

## 실행

**1. 패키지 설치**

```
python -m pip install -r requirements.txt
```

**2. 수집 대상 페이지 서버 띄우기** (터미널 하나)

```
python -m http.server 8000
```

**3. 수집 실행** (터미널 하나 더)

```
python run_pipeline.py
```

잘 돌면 이렇게 나오고 종료코드 0을 반환합니다.

```
[저장 완료] snapshot_date=2026-09-20
[저장 건수] 3개
[fetch 방식] httpx
```

### 정적 페이지와 동적 페이지

config.py 파일의 `FETCH_MODE`로 수집 방식을 바꿀 수 있습니다. 기본은 httpx고, 자바스크립트로 그려지는 페이지는 playwright로 받습니다. 테스트용으로 `ranking_js.html`을 만들어뒀는데 같은 페이지인데 결과가 갈립니다.

```
# httpx
[수집 실패] ... 상품 노드가 0개입니다. (응답 길이 428자)

# playwright
[저장 건수] 3개
```

렌더링이 끝나는 시점은 시간으로 알 수 없어서, `wait_for_selector`로 "원하는 요소가 나타날 때까지" 기다리게 했습니다.

**4. API 서버 띄우기**

```
python -m uvicorn app.main:app --reload
```

http://127.0.0.1:8000/docs 에서 API를 직접 눌러볼 수 있습니다.

2번과 4번은 같은 포트를 쓰기 때문에 동시에 켜둘 수는 없습니다.

## API

| 경로                         | 설명                |
| ---------------------------- | ------------------- |
| `GET /`                      | 서버 상태           |
| `GET /snapshots/latest`      | 가장 최근 스냅샷    |
| `GET /snapshots/date/{date}` | 특정 날짜 스냅샷    |
| `GET /compare/latest`        | 최근 두 날짜 비교   |
| `GET /compare/{old}/{new}`   | 지정한 두 날짜 비교 |

비교 결과는 신규 / 삭제 / 가격 변동 / 순위 변동 / 리뷰 변동 다섯 가지로 나눠서 돌려줍니다.

## 만들면서 신경 쓴 것

### 파싱이 0건일 때 성공이라고 하지 않기

처음엔 상품을 못 찾으면 빈 리스트를 반환하게 했습니다. 그런데 그러면 "0건 수집"도 성공으로 넘어가서, 데이터가 조용히 비어가는 걸 모르게 되었습니다. 그래서 상품 노드가 0개면 `ParseError`를 던지게 했습니다. 일부만 깨졌을 때도 누락률이 30%를 넘으면 중단하고, 그 이하면 나머지는 살립니다.

셀렉터를 일부러 바꾸고 돌려보면 이렇게 나옵니다.

```
[수집 실패] 페이지 구조가 바뀌었거나 요청이 차단된 것으로 보입니다.
  원인: 상품 노드가 0개입니다. item 셀렉터('li.product')가 더 이상 맞지 않거나 ...
  → DB에는 아무것도 저장하지 않았습니다.
```

### 0과 NULL을 구분하기

리뷰 수가 "품절"처럼 숫자가 아닐 때 처음엔 0을 반환했습니다. 그런데 0은 "리뷰가 진짜 0개"라는 뜻이고, 못 읽은 건 NULL이어야 합니다. 둘을 섞으면 나중에 리뷰 변화를 계산할 때 엉뚱한 값이 나옵니다.

### 재실행해도 안전하게

같은 날짜에 파이프라인을 두 번 돌려도 값만 갱신되고 행이 중복되면 안 됐습니다. 처음엔 `INSERT OR REPLACE`를 썼는데, 이건 실제로는 DELETE 후 INSERT라서 나중에 컬럼을 추가하면 재실행할 때마다 그 값이 초기화됩니다. `ON CONFLICT DO UPDATE`로 바꿨습니다.

### 실패를 스케줄러가 알 수 있게

예외를 그냥 삼키면 스케줄러 입장에서는 성공으로 보입니다. `run_pipeline.py`는 예외를 잡아서 `exit 1`을 반환하고, 정상일 때만 0을 돌려줍니다.

### 인코딩

playwright로 바꾸니 상품 이름만 깨져서 나왔습니다. 서버가 `Content-Type`에 charset을 안 붙이고 HTML에도 `<meta charset>`이 없어서, httpx는 UTF-8로 가정했지만 브라우저는 windows-1252로 해석한 거였습니다. HTML에 `<meta charset="utf-8">`을 넣어서 해결했습니다.

## 4. 프로젝트 구조

```bash
app/
  main.py                    FastAPI 시작점
  core/config.py             설정 (URL, DB 경로, 타임아웃)
  crawler/
    fetcher.py               httpx로 HTML 받기
    playwright_fetch.py      브라우저로 HTML 받기 (선택)
    parser.py                HTML에서 상품 뽑기
  repositories/
    snapshot_repository.py   DB 저장 / 조회
  services/
    crawl_service.py         수집 -> 파싱 -> 저장
    snapshot_service.py      스냅샷 조회
    compare_service.py       날짜 비교
  controllers/               API 엔드포인트

ranking.html                 정적 테스트 페이지
ranking_js.html              JS로 그리는 테스트 페이지
run_pipeline.py              수집 실행
```
