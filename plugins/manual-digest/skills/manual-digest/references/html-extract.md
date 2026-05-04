# HTML 추출 가이드

HTML 매뉴얼은 Claude 내장 Read 도구로 직접 읽는다 — 외부 도구 불요.

## 도구

```
Read({ file_path: "<abs>.html", offset: <int>?, limit: <int>? })
```

대형 HTML은 offset/limit으로 부분 읽기.

## 단계

### 1. 구조 파싱
- `<title>` → 매뉴얼 제목
- `<h1>` ~ `<h6>` → 섹션 트리
- `id` 속성 → 위치 앵커 (`#section-id` 형태로 보존)
- `<nav>` / `<aside>` → 사이드바 목차 (있으면 우선 활용)

### 2. 본문 샘플링
- 각 `<h1>`/`<h2>` 섹션 도입 단락
- `<table>` / `<pre>` (코드/명세) 핵심
- `<figure>` 캡션 (이미지 자체는 추출하지 않음 — 위치만 기록)

### 3. 위치 포인터
HTML은 페이지 번호 대신 **앵커 ID** + **헤딩 위치** 사용:

```markdown
| § | 제목 | 앵커 |
|---|------|------|
| §3.2 | Configuration | `#config` |
| §4.1 | API Reference | `#api-ref` |
```

원본 핀포인트 추출 시:
- 브라우저: `file:///<path>.html#anchor`
- Claude Read: `Read({ file_path: "..." })` 후 grep으로 anchor 부근 찾기

## 다중 HTML 매뉴얼

여러 HTML 파일이 한 매뉴얼을 구성하는 경우 (Sphinx/MkDocs 산출물 등):
1. 진입점(`index.html`) 식별
2. `<nav>` 또는 `_sources/` 분석으로 파일 순서 추출
3. 각 페이지를 챕터로 매핑하여 섹션 트리 구성
4. 위치 포인터: `<file>.html#<anchor>`

## V1 검증 상태

❌ 미검증 — 실제 샘플로 압축비/정확도 확인 필요. 후보 매뉴얼:
- Bootstrap 공식 문서 HTML
- Python 표준 라이브러리 HTML 묶음
- Sphinx 산출 RST → HTML 매뉴얼
