# CHM 추출 가이드

CHM(Microsoft Compiled HTML)은 Windows 내장 `hh.exe -decompile`로 풀고 추출된 HTML을 Read한다.

## 사전 조건

- **Windows 전용** — `hh.exe`는 모든 Windows 버전에 기본 내장 (`C:\Windows\hh.exe`)
- 비-Windows는 V3 이후 (7-Zip 폴백 검토 중)

## 단계

### 1. 디컴파일

```powershell
$tmp = "$env:TEMP\manual-digest\<id>\extracted"
New-Item -ItemType Directory -Force $tmp | Out-Null
& hh.exe -decompile $tmp "<abs>.chm"
```

`hh.exe -decompile`는 비동기적이라 완료 대기 필요. 출력 디렉토리에 `.html`/`.hhc`/`.hhk` 파일이 나타날 때까지 폴링:

```powershell
$timeout = 30
$start = Get-Date
while (-not (Test-Path "$tmp\*.hhc") -and ((Get-Date) - $start).TotalSeconds -lt $timeout) {
    Start-Sleep -Milliseconds 500
}
```

### 2. 핵심 파일

| 파일 | 용도 |
|------|------|
| `*.hhc` | Table of Contents (HTML 형식) |
| `*.hhk` | Index (키워드 인덱스) |
| `*.htm`/`*.html` | 본문 토픽 |
| `*.css` | 스타일 (다이제스트엔 불요) |

### 3. TOC 파싱

`.hhc`는 HTML이지만 `<OBJECT>` 태그로 토픽 트리 표현:

```html
<UL>
  <LI><OBJECT type="text/sitemap">
    <param name="Name" value="Introduction">
    <param name="Local" value="intro.htm">
  </OBJECT>
  <UL>
    <LI><OBJECT ...><param name="Name" value="Overview">
                    <param name="Local" value="overview.htm"></OBJECT>
  </UL>
</UL>
```

PowerShell + 정규식 또는 HtmlAgilityPack(이미 .NET 환경에 있음):

```powershell
$hhc = Get-Content "$tmp\<file>.hhc" -Raw
$matches = [regex]::Matches($hhc, '<param\s+name="Name"\s+value="([^"]+)">.*?<param\s+name="Local"\s+value="([^"]+)">', 'Singleline')
foreach ($m in $matches) {
    [PSCustomObject]@{ Title = $m.Groups[1].Value; Local = $m.Groups[2].Value }
}
```

### 4. 본문 추출

각 토픽 HTML을 Read로 직접 읽음. HTML 추출 가이드(`html-extract.md`)와 동일한 방식.

### 5. 위치 포인터

CHM은 topic file + HTML anchor 조합:

```markdown
| § | 제목 | 토픽 파일 | 앵커 |
|---|------|----------|------|
| §3.2 | Configuration | `config.htm` | `#options` |
```

원본 핀포인트 추출:
- Windows: `hh.exe ms-its:<chm>::/<topic>.htm` (CHM viewer)
- 또는 추출된 HTML을 직접 Read

### 6. 정리
임시 폴더 삭제 (CHM 추출은 수십~수백 개 파일이 나오므로 디스크 정리 중요). `--keep-temp` 시 보존.

## 알려진 제약

- 일부 CHM은 보호되어 디컴파일 결과가 비어있는 경우가 있음 → 7-Zip 폴백 V2
- 비-ASCII 토픽 파일명은 인코딩 문제 가능 (CHM 자체가 windows-1252 등 사용 시)

## V1 검증 상태

❌ 미검증 — WMX3 SDK CHM 등으로 검증 예정. `hh.exe -decompile`의 비동기 동작과 빈 출력 케이스 처리 확인 필요.
