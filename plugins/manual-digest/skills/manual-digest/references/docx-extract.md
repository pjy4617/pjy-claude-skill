# DOCX 추출 가이드

DOCX도 zip 컨테이너이므로 EPUB과 동일하게 `Expand-Archive`로 풀고 내부 XML을 Read한다.

## 단계

### 1. zip 해제
```powershell
$tmp = "$env:TEMP\manual-digest\<id>"
New-Item -ItemType Directory -Force $tmp | Out-Null
Expand-Archive -LiteralPath "<abs>.docx" -DestinationPath $tmp -Force
```

### 2. 핵심 파일

| 파일 | 용도 |
|------|------|
| `word/document.xml` | 본문 (모든 단락·표) |
| `word/styles.xml` | 스타일 정의 (`Heading1`~`Heading9` 매핑) |
| `docProps/core.xml` | 메타데이터 (title, creator, lastModifiedBy, created, modified) |
| `docProps/app.xml` | 앱 메타 (Pages, Words, Application) |

### 3. 헤딩 식별

`word/document.xml`에서 `<w:pStyle w:val="Heading1"/>` ~ `Heading9`로 섹션 트리 추출:

```xml
<w:p>
  <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
  <w:r><w:t>Chapter 1 Introduction</w:t></w:r>
</w:p>
```

PowerShell:
```powershell
[xml]$doc = Get-Content "$tmp\word\document.xml"
$ns = @{ w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main" }
Select-Xml -Xml $doc -Namespace $ns -XPath "//w:p[w:pPr/w:pStyle[@w:val[starts-with(., 'Heading')]]]"
```

### 4. 위치 포인터

DOCX는 페이지가 동적이라 **헤딩 번호** 기준 사용:

```markdown
| § | 제목 | 헤딩 레벨 | 단락 인덱스 |
|---|------|----------|------------|
| §1 | Introduction | Heading1 | 5 |
| §1.1 | Overview | Heading2 | 7 |
```

### 5. 메타데이터

```powershell
[xml]$core = Get-Content "$tmp\docProps\core.xml"
$core.coreProperties.title
$core.coreProperties.creator
$core.coreProperties.lastModifiedBy
```

### 6. 정리
임시 폴더 삭제. `--keep-temp` 시 보존.

## 표 / 이미지

- 표: `<w:tbl>` 구조 그대로 마크다운 `|`로 변환 (간단한 경우만)
- 이미지: `word/media/`에 별도 저장 — 다이제스트는 캡션 + 위치만 기록

## V1 검증 상태

❌ 미검증 — 실제 DOCX 샘플로 헤딩 추출 + 본문 청킹 확인 필요.
