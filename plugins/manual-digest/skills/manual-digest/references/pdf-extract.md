# PDF 추출 가이드

PDF 매뉴얼은 `@sylphx/pdf-reader-mcp` MCP의 `read_pdf` 도구로 처리한다. Claude의 내장 Read 도구는 Windows에서 `pdftoppm`(poppler) 부재로 실패하므로 MCP 경로가 표준이다.

**단, MCP는 유일한 경로가 아니다.** 아래 폴백 사다리를 반드시 순서대로 밟는다.

## 추출 경로 폴백 사다리 (순서 고정)

| 단계 | 경로 | 사용 조건 |
|------|------|-----------|
| L1 | `mcp__pdf-reader__read_pdf` | 기본 경로 |
| L2 | `pdftotext -layout` (Bash) | L1이 에러를 뱉거나 텍스트가 비었을 때 — **건너뛰기 금지** |
| L3 | 페이지 이미지 렌더링 후 육안 판독 | L1·L2가 **둘 다** 실패했을 때만 |

**금지: L1 실패를 곧바로 "이 PDF는 텍스트 레이어가 없다"로 판정하는 것.**
그 판정은 L2까지 실패한 뒤에만 내릴 수 있다.

### 실측 근거 (재발 방지)

`read_pdf`가 `invalid horizontal advance` 에러를 반환한 PDF 3건(TI 데이터시트 SLOS068AB,
XGZP6859A 도면, Cosmo 데이터시트)을 `pdftotext`로 재시도한 결과 **3건 모두 텍스트가 정상 추출**됐다.
이 에러는 PDF 손상 신호가 아니라 MCP 서버 쪽 폰트 메트릭 파싱 버그다.
비유하자면 책이 찢어진 게 아니라 스캐너가 고장 난 것이다.

L1 실패를 스캔본으로 오판하면 L3(이미지 판독)로 직행하게 되는데, 이 경로는
① 토큰이 페이지당 수십 배 비싸고 ② 표의 수치를 사람이 눈으로 옮겨 적는 것과 같아
**행을 잘못 짚을 위험이 텍스트 추출보다 구조적으로 높다**.

### L2: pdftotext 사용법

```bash
command -v pdftotext || echo "poppler 미설치"   # 먼저 가용성 확인

pdftotext -layout -enc UTF-8 "<abs>" -                    # 전체를 stdout으로
pdftotext -layout -enc UTF-8 -f 82 -l 83 "<abs>" -        # 82~83페이지만
```

- **`-layout`은 필수다.** 이 옵션이 없으면 표의 열 정렬이 무너져 어느 행의 값인지 알 수 없게 된다.
  데이터시트처럼 한 문서에 여러 부품 스펙 표가 있는 경우 치명적이다.
- `-f`/`-l`은 각각 시작·끝 페이지(1-based). 산발적 페이지는 호출을 나눈다
  (혼합 범위 문법은 L1 전용이다).
- 출력을 통째로 받지 않는다 — `| sed -n '120,180p'` 또는 `| grep -n -A5 "<섹션 제목>"`으로 구간만 받는다.
- **Windows**: poppler가 기본 포함되지 않는다. `scoop install poppler` 등으로 설치하거나,
  없으면 사용자에게 설치를 안내하고 L3로 내려간다.

### 추출 경로 기록

L2 이하를 썼으면 `digest.md` 프론트매터의 `extractor`에 실제 사용한 경로를 적는다
(`mcp-pdf-reader` / `pdftotext-layout` / `page-render`). L3(`page-render`)를 쓴 경우에는
**"수치는 육안 판독본이라 원본 대조가 필요하다"는 문장을 다이제스트 개요에 남긴다** —
읽는 쪽이 신뢰도를 알아야 하기 때문이다.

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

**스캔본 판정은 L1·L2를 모두 통과한 뒤에만 내린다.**

판정 절차:
1. `read_pdf`(L1)가 빈 텍스트 또는 에러 → 아직 판정하지 않는다
2. `pdftotext -layout`(L2)로 **서로 떨어진 3페이지 이상**을 표본 추출
3. 표본 전체가 페이지당 50자 미만이면 그때 스캔본으로 확정
4. L2가 정상 텍스트를 내면 스캔본이 아니다 — L2를 정식 추출 경로로 삼아 인제스트를 계속한다

스캔본으로 확정된 경우에만 "OCR 필요, V2 이후 지원" 명시 후 인제스트 중단.
poppler 미설치로 L2를 못 돌린 경우는 "판정 불가"이지 "스캔본"이 아니다 — 설치를 안내한다.

## 검증된 결과 (TwinCAT 3 I/O Manual)

| 항목 | 값 |
|------|------|
| 원본 | 168p, 6.29 MB |
| 다이제스트 | 18.6 KB (압축비 0.29%) |
| 추출 페이지 | 34/168 (20.2%) |
| 페이지 포인터 정확도 | ±0 (인쇄 페이지와 일치) |
| 메타데이터 자동 확보 | Title, Author, Subject, Keywords, Producer, Language ✓ |
