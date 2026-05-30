## KiCad 회로도 도구 설정

이 프로젝트에는 KiCad 회로도 풀스택 도구가 설치되어 있습니다.

### 사용 가능한 스킬

- `/kicad-review` — 회로도 *설계* 분석, 데이터시트 비교 검증, BOM 생성을 통합 수행
- `/kicad-analyze` — 회로(넷리스트)/PCB 정밀 분석: ERC/DRC, 넷 추적, 트랙/라우팅, 신호·전원 무결성(SI/PI)
- `/kicad-design` — PRD/설계사양서 기반 KiCad 회로도 생성
- `/kicad-setup` — 에이전트를 다른 프로젝트에 설치 (`--with-mcp`로 Seeed MCP 등록 안내)

### 에이전트

- `kicad-schematic-reviewer` — 회로도 설계 리뷰 전문가 (8단계 체크리스트 + 데이터시트 비교)
- `kicad-bom-generator` — BOM 마크다운 생성 전문가
- `kicad-schematic-designer` — PRD 기반 회로도 설계 전문가
- `kicad-pcb-analyzer` — 회로/PCB 정밀 분석 전문가 (ERC/DRC, 넷 추적, 트랙, SI/PI)

### 워크플로우

```
[설계] PRD/설계사양서
  → kicad-design 스킬 트리거
  → kicad-schematic-designer 에이전트가 회로도 생성
  → .kicad_sch 파일 출력

[리뷰] 회로도 리뷰 요청
  → kicad-review 스킬 트리거
  → kicad-schematic-reviewer 에이전트가 8단계 리뷰 수행
  → kicad-bom-generator 에이전트가 BOM 마크다운 생성
  → 종합 보고서 출력

[분석] PCB/넷리스트 분석 요청 (DRC, 넷 추적, SI/PI 등)
  → kicad-analyze 스킬 트리거
  → kicad-pcb-analyzer 에이전트가 엔진 감지 후 정밀 분석
  → 회로/PCB/SI·PI 종합 분석 보고서 출력
```

### 분석 엔진 (kicad-analyze)

`kicad-analyze`는 가용한 엔진을 우선순위로 사용합니다:

1. **Seeed kicad-mcp-server** (`mcp__kicad__*`) — ERC/DRC, 넷 추적, 풋프린트/트랙, **SI/PI까지 정밀**
2. **kicad-cli** — `sch erc` / `pcb drc` / 넷리스트 (SI/PI 미지원)
3. **직접 파싱** — `.kicad_sch`/`.kicad_pcb` 텍스트 추출 (SI/PI 제한)

> SI/PI·정밀 트랙 분석을 쓰려면 `/kicad-setup --with-mcp`로 Seeed MCP를 등록하세요(KiCad 9.0+ 로컬 설치 전제).

### KiCad CLI

- `kicad-cli`가 설치되어 있으면 넷리스트/BOM 추출, PDF 내보내기, ERC/DRC 정확도가 높아집니다
- 없으면 `.kicad_sch`/`.kicad_pcb` 직접 파싱 모드로 동작합니다 (정확도 제한 경고 포함)
