## KiCad 회로도 도구 설정

이 프로젝트에는 KiCad 회로도 풀스택 도구가 설치되어 있습니다.

### 사용 가능한 스킬

- `/kicad-review` — 회로도 *설계* 리뷰(ERC·풋프린트 해석·구조 린트 기계 판정 우선), 데이터시트 비교 검증, BOM 생성(MPN/LCSC 열, `--sourcing` 조달 조회)
- `/kicad-analyze` — 회로(넷리스트)/PCB 정밀 분석: ERC/DRC, 넷 추적, 트랙/라우팅, 신호·전원 무결성(SI/PI)
- `/kicad-design` — PRD/설계사양서 기반 KiCad 회로도 생성
- `/kicad-fabricate` — 제조 출력: DRC ERROR=0 게이트 → 존 채움 → 회로도-보드 동기화 확인 → 거버/드릴/위치 파일/IPC-D-356/BOM (kicad-cli 필수, MCP 병기)
- `/kicad-usage` — **KiCad 10.0 프로그램 자체의 사용법** 안내(공식 매뉴얼 다이제스트: 프로젝트 매니저·pcbnew·gerbview·kicad-cli). "차동쌍 어떻게 배선해?", "거버 어떻게 내보내?", "커스텀 DRC 룰 문법?", "단축키 알려줘" 같은 How-to 질문에 응답
- `/kicad-setup` — 에이전트를 다른 프로젝트에 설치 (`--with-mcp`로 KiCAD-MCP-Server 등록 안내)

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
  → kicad-schematic-reviewer 에이전트가 11단계 리뷰 수행
  → kicad-bom-generator 에이전트가 BOM 마크다운 생성
  → 종합 보고서 출력

[분석] PCB/넷리스트 분석 요청 (DRC, 넷 추적, SI/PI 등)
  → kicad-analyze 스킬 트리거
  → kicad-pcb-analyzer 에이전트가 엔진 감지 후 정밀 분석
  → 회로/PCB/SI·PI 종합 분석 보고서 출력
```

### 분석 엔진 (kicad-analyze)

`kicad-analyze`는 가용한 엔진을 우선순위로 사용합니다:

1. **KiCAD-MCP-Server** (`mcp__kicad__*`) — ERC/DRC, 넷 추적, 회로도 린트, 풋프린트/트랙·존 기하까지 **정밀**
2. **kicad-cli** — `sch erc` / `pcb drc` / 넷리스트 (트랙·존 기하 미지원). **ERC/DRC는 MCP 경로도 내부에서 kicad-cli를 부르므로 kicad-cli는 어느 경로든 필수**
3. **직접 파싱** — `.kicad_sch`/`.kicad_pcb` 텍스트 추출 (존 채움·정밀 통계 제한)

> 정밀 트랙·존 분석을 쓰려면 `/kicad-setup --with-mcp`로 KiCAD-MCP-Server를 등록하세요
> (KiCad 9.0+ 로컬 설치 + Node.js 18+ 전제).
>
> 이 서버에는 **SI/PI 전용 분석 도구가 없습니다.** 트랙·존·패드 기하를 받아 스킬이 직접 계산·판정합니다.
> 절대 임피던스와 IR drop은 `.kicad_pcb`의 `(setup (stackup ...))`에 `epsilon_r`·`thickness`가 있으면
> 그 값으로 근사 계산합니다(서버에 스택업 읽기 도구가 없어 파일에서 직접 파싱하므로 MCP 등록 여부와 무관).
> 스택업이 비어 있으면 "미수행 — Board Setup > Physical Stackup 미설정"으로 표기합니다.

### KiCad CLI

- `kicad-cli`가 설치되어 있으면 넷리스트/BOM 추출, PDF 내보내기, ERC/DRC 정확도가 높아집니다
- 없으면 `.kicad_sch`/`.kicad_pcb` 직접 파싱 모드로 동작합니다 (정확도 제한 경고 포함)
