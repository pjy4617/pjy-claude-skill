# PDF 추출 가이드

PDF 매뉴얼은 `@sylphx/pdf-reader-mcp` MCP의 `read_pdf` 도구로 처리한다. Claude의 내장 Read 도구는 Windows에서 `pdftoppm`(poppler) 부재로 실패하므로 MCP 경로가 표준이다.

## 도구

```
mcp__pdf-reader__read_pdf
  sources:        [{ path: <abs>, pages: "<spec>" }]
  include_metadata:    bool
  include_page_count:  bool
  include_full_text:   bool   # pages 미지정 시
  include_tables:      bool   # 좌표 기반 테이블 검출
  include_images:      bool   # base64 이미지
```

## 페이지 인자 형식

| 형식 | 예시 | 의미 |
|------|------|------|
| 단일 | `"7"` | 7페이지만 |
| 범위 | `"7-12"` | 7~12페이지 |
| **혼합 범위** | `"7-12,28-30,82-83,166"` | 산발적 페이지를 한 번에 — **토큰 효율 결정적** |
| 배열 | `[7, 8, 28, 29]` | 정수 배열도 허용 |

## 인제스트 단계

### 1. 메타데이터 + 페이지 수 + TOC 위치 파악
```
read_pdf({
  sources: [{ path: "<abs>", pages: "1-5" }],
  include_metadata: true,
  include_page_count: true
})
```

수집되는 메타데이터:
- `info.Title`, `info.Author`, `info.Subject`, `info.Keywords`
- `info.CreationDate`, `info.ModDate`
- `info.Producer` (생성 도구), `info.Language`
- `num_pages`

### 2. TOC 페이지 추가 읽기
TOC가 1페이지 초과 시 (대형 매뉴얼), 추가 페이지를 읽어 전체 섹션 트리 추출.

### 3. 본문 샘플링
**모든 페이지를 읽지 않는다** — 핵심만 샘플링:
- 각 §의 introduction (1-2페이지)
- 핵심 개념·표·다이어그램 페이지
- 절차 섹션은 TOC 제목만으로 요약 충분

목표 커버리지: 전체의 ~20% (TwinCAT 168p 검증: 34페이지 = 20.2%로 충분)

```
read_pdf({
  sources: [{
    path: "<abs>",
    pages: "<섹션 도입 페이지들 혼합 범위>"
  }]
})
```

### 4. 페이지 포인터 정확도
`read_pdf`의 페이지 번호는 **PDF 내부 인덱스** 기준이다. 인쇄 표시 페이지가 다를 수 있으니 (예: 로마자 서문 페이지 별도) 다이제스트 작성 시 두 가지 모두 필요하면 명시.

## 대형 PDF (1000p+)

페이지 범위 청크 분할:
```
read_pdf({ sources: [{ path: "...", pages: "1-100" }] })   # 청크 1
read_pdf({ sources: [{ path: "...", pages: "101-200" }] }) # 청크 2
...
```

진행률을 사용자에게 표시하여 체감 시간 단축.

## 텍스트 레이어 없는 스캔 PDF

`read_pdf`가 빈 텍스트 반환 → "OCR 필요, V2 이후 지원" 명시 후 인제스트 중단.
검증 방법: 첫 페이지 추출 후 `text` 필드 길이 확인. 50자 미만이면 스캔본 의심.

## 검증된 결과 (TwinCAT 3 I/O Manual)

| 항목 | 값 |
|------|------|
| 원본 | 168p, 6.29 MB |
| 다이제스트 | 18.6 KB (압축비 0.29%) |
| 추출 페이지 | 34/168 (20.2%) |
| 페이지 포인터 정확도 | ±0 (인쇄 페이지와 일치) |
| 메타데이터 자동 확보 | Title, Author, Subject, Keywords, Producer, Language ✓ |
