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
- 변하는 데이터를 단순 수정하지 않고 **날짜별 snapshot**으로 저장한다.
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

### 4) 날짜별 비교

- 신규 상품
- 삭제 상품
- 가격 변동
- 순위 변동
- 리뷰 수 변동

### 5) API 조회

- 최신 snapshot 조회
- 특정 날짜 snapshot 조회
- 최근 2개 날짜 비교 결과 조회

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

## 4. 프로젝트 구조

```bash
crawler-real/
  app/
    controllers/
      compare_controller.py
      health_controller.py
      snapshot_controller.py

    core/
      config.py

    crawler/
      fetcher.py
      parser.py
      playwright_fetch.py

    db/
      database.py

    repositories/
      snapshot_repository.py

    services/
      compare_service.py
      crawl_service.py
      snapshot_service.py

    main.py

  ranking.html
  run_pipeline.py
  README.md
  .gitignore
```
