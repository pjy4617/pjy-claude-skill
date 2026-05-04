# EPUB 추출 가이드

EPUB은 zip 컨테이너이므로 PowerShell 내장 `Expand-Archive`로 풀고 내부 XHTML을 Read한다 — 외부 도구 불요.

## 단계

### 1. zip 해제
```powershell
$tmp = "$env:TEMP\manual-digest\<id>"
New-Item -ItemType Directory -Force $tmp | Out-Null
Expand-Archive -LiteralPath "<abs>.epub" -DestinationPath $tmp -Force
```

### 2. 구조 식별
- `META-INF/container.xml` → root file 경로 (보통 `OEBPS/content.opf`)
- `content.opf`의 `<manifest>` → 모든 파일 목록
- `content.opf`의 `<spine>` → 챕터 순서

```powershell
[xml]$opf = Get-Content "$tmp\OEBPS\content.opf"
$opf.package.spine.itemref | ForEach-Object {
    $id = $_.idref
    $href = ($opf.package.manifest.item | Where-Object { $_.id -eq $id }).href
    "$tmp\OEBPS\$href"
}
```

### 3. 챕터 텍스트 읽기
순서대로 XHTML을 Read. 각 파일의 `<h1>`/`<h2>` → 섹션 헤딩.

### 4. 위치 포인터
- spine 순서 + 파일 내 `id` 앵커
- 표시 형식: `<spine-index>:<filename>#<anchor>`

```markdown
| § | 제목 | 위치 |
|---|------|------|
| 3장 | Introduction | `3:ch03.xhtml#intro` |
```

### 5. 정리
산출물 작성 완료 후 임시 폴더 자동 삭제:
```powershell
Remove-Item -Recurse -Force $tmp
```
`--keep-temp` 옵션 시 보존.

## 메타데이터

`content.opf`의 `<metadata>`:
- `<dc:title>` → title
- `<dc:creator>` → publisher/author
- `<dc:language>` → language (BCP47)
- `<dc:date>` → publication_date
- `<dc:identifier>` → ISBN 등

## 페이지 번호?

EPUB은 reflowable이라 고정 페이지가 없다. spine index + 챕터 내 위치(처음 100자 등)로 대체.

## V1 검증 상태

❌ 미검증 — 실제 EPUB 샘플로 추출 흐름 + 압축비 확인 필요.
