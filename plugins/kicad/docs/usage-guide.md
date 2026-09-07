# KiCad 플러그인 사용 설명서

## 개요

KiCad 플러그인은 KiCad 회로/PCB의 **설계 · 리뷰 · 분석 · 제조 출력**과 **KiCad 사용법 안내**를 통합 지원하는 풀스택 도구입니다.
PRD(설계사양서)로부터 회로도를 생성하고, 생성된 회로도를 8단계로 검증하며, BOM(파트리스트)을 마크다운으로 출력하고, 넷리스트/PCB를 정밀 분석(ERC/DRC·넷 추적·배치·트랙/라우팅·SI/PI)한 뒤, 팹에 넘길 제조 데이터(거버·드릴·위치 파일·IPC-D-356·발주 BOM)까지 뽑습니다.
또한 **KiCad 10.0 공식 매뉴얼**(프로젝트 매니저·pcbnew·gerbview·kicad-cli)을 한국어 다이제스트로 번들해, "KiCad에서 X 어떻게 해?" 같은 프로그램 사용법 질문에도 `/kicad-usage`로 답합니다.

### 지원 도메인

- STM32 등 MCU 보드
- Xilinx/Intel FPGA 보드
- EtherCAT 슬레이브 보드
- IO 보드 / 센서 인터페이스
- 전원부 (Buck/LDO)
- Ethernet PHY / 트랜시버

---

## 설치

### 사전 요구사항

- Claude Code CLI
- KiCad 9.x 이상 (`kicad-cli` 명령어 사용 가능하면 최적, 없어도 동작 — 단 `/kicad-fabricate` 제조 출력은 `kicad-cli` 필수)
  - `/kicad-usage` 사용법 다이제스트는 **KiCad 10.0** 공식 문서 기준입니다(9.x도 대부분 호환, 일부 UI/기능 차이 가능)

### 플러그인 설치

```
# pjy-skills 마켓플레이스 등록 (최초 1회)
/plugin marketplace add pjy4617/pjy-claude-skill

# 플러그인 설치
/plugin install kicad@pjy-skills
```

### 에이전트 설치 (타겟 프로젝트)

KiCad 프로젝트가 있는 디렉토리에서:

```
/kicad-setup
```

질문에 따라 프로젝트 경로를 입력하면 에이전트 4개와 CLAUDE.md가 자동 설치됩니다.
PCB 트랙·존 기하 기반 정밀 분석(SI/PI 판정 포함)까지 하려면 `/kicad-setup --with-mcp`로 KiCAD-MCP-Server 등록을 안내받을 수 있습니다(KiCad 9.0+ 로컬 설치 + Node.js 18+ 전제).

설치되는 파일:
```
.claude/agents/
├── kicad-schematic-designer.md    (회로도 설계 에이전트)
├── kicad-schematic-reviewer.md    (회로도 리뷰 에이전트)
├── kicad-bom-generator.md         (BOM 생성 에이전트)
└── kicad-pcb-analyzer.md          (회로/PCB 분석 에이전트)
CLAUDE.md                          (KiCad 설정 추가)
```

---

## 스킬 목록

| 스킬 | 명령어 | 기능 |
|------|--------|------|
| 회로도 설계 | `/kicad-design` | PRD/설계사양서 → KiCad 회로도 생성 |
| 회로도 리뷰 | `/kicad-review` | 8단계 설계 리뷰 + BOM 생성 |
| 회로/PCB 분석 | `/kicad-analyze` | 넷리스트/PCB 정밀 분석: ERC/DRC, 회로도-보드 동기화 확인, 배치 검토, 넷 추적, 트랙/라우팅, 신호·전원 무결성(SI/PI) |
| 제조 출력 | `/kicad-fabricate` | DRC 게이트 → 거버·드릴·위치 파일·IPC-D-356·발주 BOM 생성 + 산출물 검증 |
| KiCad 사용법 | `/kicad-usage` | **KiCad 10.0 프로그램 자체의 사용법** 안내 (공식 매뉴얼 다이제스트: 프로젝트 매니저·pcbnew·gerbview·kicad-cli) |
| 프로젝트 설정 | `/kicad-setup` | 에이전트를 타겟 프로젝트에 설치 (`--with-mcp`로 KiCAD-MCP-Server 등록 안내) |

---

## 사용법 1: 회로도 설계 (`/kicad-design`)

PRD, 설계사양서, 블록다이어그램 등을 입력하면 KiCad 회로도(.kicad_sch)를 생성합니다.

### 사용 예시

```
"이 PRD 기반으로 KiCad 회로도 만들어줘"
"STM32F407 + Ethernet PHY 2포트 보드 설계해줘"
"M.2 폼팩터의 FPGA 카드 회로도 생성해줘"
"EtherCAT 슬레이브 IO 보드 회로 설계"
```

### 워크플로우

```
[1] 입력 분석
    PRD/설계사양서에서 기능, 인터페이스, 전원 요구사항을 추출합니다.
    → 요구사항 정리 결과를 사용자에게 보여주고 확인을 받습니다.

[2] 아키텍처 설계
    IC 선정, 전원 트리, 계층 구조를 설계합니다.
    사용자가 IC를 지정하지 않은 경우 후보를 제안합니다.

[3] 데이터시트 수집
    선정된 IC의 데이터시트를 웹에서 검색합니다.
    핀 배치, 권장 회로, 전기적 특성을 확보합니다.

[4] 회로도 생성
    KiCad 9.x 또는 10.x(대상 버전에 맞춤) 형식의 .kicad_sch 파일을 작성합니다.
    기능 블록별 서브시트로 분리합니다.

[5] 리뷰 및 보정
    생성된 회로도를 kicad-review 스킬로 검증합니다.
    호출 주체는 메인 세션입니다 — 서브에이전트가 스킬을 부르지 않으므로,
    designer 에이전트의 산출물을 받은 뒤 메인 세션이 kicad-review 를 실행합니다.
    ERROR 발견 시 수정 사항을 제시하고, 사용자 확인 후 수정합니다.
    .kicad_pro 프로젝트 파일도 함께 생성됩니다.

[6] 보드 생성 (선택)
    회로도의 풋프린트·넷을 .kicad_pcb 에 올립니다. 보드 외곽(테두리)과 배치는 사용자가 GUI 에서 합니다.
    KiCad GUI 의 Update PCB from Schematic(F8)에 해당하며, kicad-cli 에는 없는 기능이라
    KiCAD-MCP-Server 가 유일한 무 GUI 경로입니다.
```

#### 단계 6 (선택) 보드 생성의 전제

사용자가 요청했을 때만 수행하며, 아래를 하나라도 못 채우면 건너뜁니다.

| 전제 | 이유 |
|------|------|
| ERC 0 errors | 오류가 있는 회로도를 보드로 넘기면 보드에서 두 번 고쳐야 합니다 |
| 모든 `Footprint` 필드가 `fp-lib-table` 에서 풀림 | 풀리지 않는 풋프린트는 보드에 추가되지 않고 `skipped` 로 빠집니다 (kicad-review 2.5 통과 필요) |
| KiCAD-MCP-Server 등록 + pcbnew 가용 | 이 경로의 유일한 실행 수단입니다 |
| KiCad 10 사용자 | KiCad 9 는 건너뜁니다 — MCP 편집 도구가 파일을 10 포맷으로 다시 쓰면 9 에서 열 수 없게 됩니다 |
| KiCad GUI 에서 프로젝트가 닫혀 있음 | 보드 파일을 덮어쓰기 때문입니다 |

- 보드가 없으면 `create_board_from_schematic`, **이미 있으면 `sync_schematic_to_board`** 를 씁니다.
  기존 보드에 `create_board_from_schematic --overwrite` 를 쓰면 배치·배선이 전부 사라집니다.
- 산출물은 **풋프린트와 넷만 올라간 보드**입니다. 배치 도구는 호출하지 않습니다 — 보드 외곽은 기구 치수로,
  배치는 설계 판단으로 정해지는 것이라 사용자가 KiCad GUI 에서 합니다.
- 외곽 → 배치 → 배선을 마치고 `/kicad-analyze`(배치·배선 검토) → `/kicad-fabricate`(제조 출력)로 넘어갑니다.

### 라이브러리 사용 우선순위

| 우선순위 | 소스 | 대상 부품 |
|---------|------|----------|
| 1 | KiCad 기본 라이브러리 | 저항, 캐패시터, 인덕터, LED, 커넥터, 전원 심볼, 표준 MCU/Flash |
| 2 | 제조사 공식 라이브러리 | KiCad 기본에 없는 IC (SnapEDA, Ultra Librarian 등에서 검색) |
| 3 | 커스텀 심볼 | 위 두 소스에서 못 찾을 때만 데이터시트 기반 생성 |

### 입력 형식

다음 형식의 입력을 지원합니다:

- **HW PRD 문서** (`.md`, `.txt`, `.docx`) — 기능 요구사항, 인터페이스 목록
- **설계사양서** — 구체적 IC 지정, 핀 할당, 전원 레일
- **블록다이어그램** — 모듈 구성, 인터페이스 연결
- **구두 설명** — "STM32에 SPI Flash 하나 붙여줘" 같은 자연어

### 출력

- `.kicad_sch` 파일 (KiCad 9.x 또는 10.x — 생성 시 맞춘 대상 버전에서 바로 열 수 있음)
- 계층 구조인 경우 루트 + 서브시트 여러 파일
- `.kicad_pro` 프로젝트 파일 (필요 시)

### 생성 후 KiCad GUI 보정 (필수)

생성된 회로도는 **부품 선정, 회로 구조, 네트 정의, 디커플링 설계**가 완성된 상태이지만,
S-expression 직접 생성의 특성상 와이어-핀 좌표가 정확히 일치하지 않을 수 있습니다.

KiCad에서 열고 다음을 보정하세요:

1. **ERC 실행** (Inspect → Electrical Rules Checker) → 미연결 핀/와이어 확인
2. **와이어 끝점 스냅** → 핀에 정확히 연결되도록 드래그
3. **레이아웃 정리** → 부품 간격, 텍스트 겹침 조정

보정 시간은 **핀 수에 비례**합니다. 끝점 스냅은 핀 하나당 한 번이라 30핀 IC 하나면 끝점이 30개입니다.
이 텍스트 생성 경로는 **부품 20개(핀 100개) 이하 초안에서만 실용적**이며, 그 이상은 회로를 시트로 쪼개
시트당 부품 수를 20개 아래로 유지하거나, MCP 저작 경로(`batch_add_and_connect` + `lint_offgrid`)를 기다립니다
(MCP 저작 경로는 아직 스킬에 들어 있지 않은 후속 범위입니다).
스킬이 네트 레이블 기반으로 연결하므로 IC 간 논리적 연결은 어느 규모에서든 유지됩니다.

---

## 사용법 2: 회로도 리뷰 (`/kicad-review`)

기존 KiCad 회로도를 8단계로 검증하고, BOM을 마크다운으로 생성합니다.

### 사용 예시

```
"이 KiCad 회로도 리뷰해줘"
"hw/kicad 폴더의 회로도 검토하고 BOM 만들어줘"
"이 보드에 사용된 IC들 데이터시트 확인해서 문제 없는지 봐줘"
"파트리스트 마크다운으로 뽑아줘"
```

### 8단계 리뷰 워크플로우

```
[1] 프로젝트 탐색
    KiCad 프로젝트 파일과 서브시트 계층 구조를 파악합니다.

[2] 회로도 파싱
    kicad-cli 넷리스트 또는 .kicad_sch 직접 파싱으로
    부품, 핀, 네트, 값 정보를 추출합니다.

[3] PDF 시각적 검토
    회로도를 PDF로 내보내 멀티모달 분석을 수행합니다.
    와이어 연결 누락, 부품 겹침, 미배선 등 시각적 오류를 감지합니다.

[4] 제조사 공식 라이브러리 비교
    IC 심볼의 핀 번호/이름/풋프린트가 제조사 공식 라이브러리와
    일치하는지 검증합니다. 불일치 시 공식 라이브러리 다운로드 링크를 제공합니다.

[5] 텍스트 기반 설계 리뷰
    8개 카테고리 체크리스트를 적용합니다:
    - V. PDF 시각적 검토 (7항목) — 단계 3에서 수행
    - L. 라이브러리 비교 (5항목) — 단계 4에서 수행
    - A. 전원 설계 (8항목)
    - B. 핀 연결 완전성 (6항목)
    - C. 신호 무결성 (6항목)
    - D. 데이터시트 정합성 (8항목)
    - E. ERC 수준 검증 (5항목)
    - F. 도메인별 검증 (FPGA/MCU/PHY/EtherCAT 등, 가변)

[6] 데이터시트 비교
    주요 IC의 데이터시트를 웹 검색하여:
    - 절대 최대 정격 vs 설계 전압
    - 권장 회로 vs 실제 회로
    - 핀별 기능 설명 vs 회로도 연결
    을 대조합니다.

[7] BOM 마크다운 생성
    부품 목록을 카테고리별로 분류하고 마크다운 테이블로 출력합니다.
    같은 Value+Footprint 조합은 그룹핑, DNP 부품은 별도 테이블로 분리합니다.

[8] 종합 리뷰 보고서
    모든 결과를 통합한 보고서를 출력합니다.
    ERROR/WARN/OK 집계, 구체적 수정 조치, 데이터시트 근거를 포함합니다.
```

### 판정 기준

| 등급 | 의미 | 조치 |
|------|------|------|
| ERROR | 하드웨어 손상 또는 동작 불가 | 반드시 수정 |
| WARN | 동작하지만 잠재적 문제 | 문서화 또는 개선 권장 |
| OK | 이상 없음 | - |
| N/A | 해당 회로에 미적용 | - |

### 도메인 자동 감지

회로도에서 IC 파트넘버를 분석하여 도메인을 자동 감지하고, 해당 도메인의 추가 검증 항목을 적용합니다:

| 도메인 | 감지 패턴 | 추가 검증 |
|--------|----------|----------|
| FPGA (Xilinx/AMD) | `XC7*`, `XC6*`, `XCZU*` | 전원 레일 완전성, 컨피규레이션 핀, JTAG, 디커플링 캡 수량 |
| MCU (STM32) | `STM32*` | AF 매핑, BOOT/RESET, SWD, VCAP |
| Ethernet PHY | `DP83*`, `KSZ80*` | REXT, MDI 매칭, 모드 스트랩 |
| EtherCAT 슬레이브 | `LAN9252*`, `ET1100*` | PDI 인터페이스, EEPROM, SYNC/LATCH |
| 전원 IC | `TPS*`, `LM*`, `MP*` | 피드백 저항 분배비, 입출력 캡 ESR, 인덕터 |

### BOM 출력 형식

```markdown
# BOM (Bill of Materials)

**프로젝트**: M.2 Artix-7 EtherCAT
**총 부품 수**: 15종 / 38개

## IC

| # | Reference | Value | Footprint | Qty | Datasheet |
|---|-----------|-------|-----------|-----|-----------|
| 1 | U1 | TPS62130 | QFN-16 | 1 | [Link](...) |

## 캐패시터

| # | Reference | Value | Footprint | Qty | Datasheet |
|---|-----------|-------|-----------|-----|-----------|
| 1 | C1~C4 | 47μF/10V | 0805 | 4 | - |
| 2 | C11, C13, C16 | 100nF | 0402 | 3 | - |
```

---

## 사용법 3: KiCad 사용법 안내 (`/kicad-usage`)

KiCad **프로그램 자체**를 어떻게 쓰는지 묻는 How-to 질문에 답합니다. KiCad 10.0 공식 매뉴얼 4종을 한국어 다이제스트로 압축해 플러그인에 번들했으며, 매번 원문을 읽지 않고 다이제스트를 1차 참조원으로 사용합니다.

### 다른 스킬과의 차이

- `kicad-design`/`kicad-review`/`kicad-analyze` → 사용자의 **회로/PCB 파일**을 생성·리뷰·분석(작업 수행)
- `kicad-usage` → **KiCad라는 도구를 어떻게 쓰는가**를 안내(질의응답)

### 사용 예시

```
"KiCad에서 차동쌍 어떻게 배선해?"          → pcbnew §Routing differential pairs
"보드 스택업·임피던스 어디서 설정해?"        → pcbnew §Board setup (stackup)
"커스텀 DRC 룰(.kicad_dru) 문법 알려줘"      → pcbnew §Custom design rules
"거버·드릴 파일 어떻게 내보내?"              → pcbnew §Plotting / Drill files
"kicad-cli로 PCB DRC 돌리는 명령 뭐야?"      → kicad-cli (pcb drc)
"GerbView에서 D-code 어떻게 봐?"             → gerbview
"PCB 에디터 단축키 정리해줘"                 → pcbnew Actions reference
"KiCad 라이브러리 경로 어떻게 설정해?"       → kicad §Libraries configuration
```

### 답변 워크플로

```
[1] references/INDEX.md (토픽 → 파일·anchor 마스터 인덱스) 먼저 조회
     ↓  (깊은 키워드 검색: grep -ri "키워드" references/)
[2] 해당 다이제스트 파일 Read → 한국어로 답변 + 출처 명시
     예: "출처: pcbnew §Length tuning · pcbnew.html#length-tuning"
     ↓  (메뉴 경로·옵션명·단축키·CLI 플래그는 영어 원문 그대로 인용)
[3] 다이제스트로 부족할 때만 원문 URL(<원문>#anchor)을 WebFetch로 확인
```

### 번들 다이제스트 (KiCad 10.0, `skills/kicad-usage/references/`)

원본 매뉴얼 4종(아래 URL)을 한국어 다이제스트 **9개 + 마스터 INDEX**로 압축했으며, 원문 **544개 섹션을 100% anchor 커버**합니다.

| 파일 | 다루는 범위 | 원문 |
|------|------------|------|
| `INDEX.md` | 토픽 → 파일·anchor 마스터 인덱스 (**먼저 조회**) | — |
| `kicad-project.md` | 프로젝트 매니저, 설치/최초설정, 파일·폴더, 경로/환경변수/라이브러리, Jobsets, 템플릿, PCM, Preferences, 단축키 | <https://docs.kicad.org/10.0/en/kicad/kicad.html> |
| `pcbnew-1-setup-ui.md` | 화면/표시·선택, 보드 레이어/Appearance, PCB 생성, **Board Setup**(스택업·디자인 룰·넷클래스·제약) | <https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html> |
| `pcbnew-2-editing-routing.md` | 배치/그리기/그리드, 풋프린트/패드/**Zone**, **트랙·비아·차동쌍 배선**, **길이 튜닝**, Teardrops, 그래픽, Group/Array | ↑ pcbnew |
| `pcbnew-3-inspect-output.md` | Forward/Back annotation, **DRC**, 3D 뷰어, Net inspector, 타 EDA 임포트, **출력 생성**(Plot/Gerber/Drill/STEP/BOM), Design variants | ↑ pcbnew |
| `pcbnew-4-footprints.md` | 풋프린트 라이브러리/에디터(패드·필드·net tie·3D·wizard·체크), 멀티채널 레이아웃, 디자인 블록 | ↑ pcbnew |
| `pcbnew-5-advanced-rules.md` | 설정/커스터마이즈, Text variables/expressions, 그래픽·**커스텀 디자인 룰(.kicad_dru)**, Python 스크립팅, IDF | ↑ pcbnew |
| `pcbnew-6-hotkeys.md` | PCB Editor / 3D Viewer / Common **단축키** 전체 표 | ↑ pcbnew |
| `gerbview.md` | GerbView 거버/드릴 뷰어 — 인터페이스, 툴바, Layers Manager, 메뉴, 인쇄 | <https://docs.kicad.org/10.0/en/gerbview/gerbview.html> |
| `kicad-cli.md` | kicad-cli 명령행 — fp/jobset/pcb/sch/sym/version 서브커맨드와 옵션/플래그 | <https://docs.kicad.org/10.0/en/cli/cli.html> |

각 섹션 제목 끝의 `#anchor`로 원문을 핀포인트할 수 있습니다(예: `pcbnew.html#routing-tracks`). 다이제스트로 부족하면 원문 URL을 확인하고, 출처(파일·anchor)를 항상 명시합니다.

> 본 다이제스트는 **KiCad 10.0** 기준입니다. 9.x에서도 대부분 동일하나 일부 UI/기능이 다를 수 있습니다.

---

## 사용법 4: 제조 출력 (`/kicad-fabricate`)

배선이 끝난 보드에서 **팹(PCB 제조사)과 조립사에 넘길 파일**을 만듭니다.
비유하면 원고 교정이 끝난 책을 인쇄소에 넘기기 전 최종 파일 묶음을 싸는 작업입니다.

### 다른 스킬과의 차이

- `/kicad-analyze` → DRC/ERC를 **판정**하고 배치·배선·SI/PI를 분석합니다(보고서)
- `/kicad-fabricate` → 그 판정을 **게이트로 삼아** 팹에 넘길 **파일을 만듭니다**(산출물)

DRC error가 하나라도 있으면 아무것도 뽑지 않고 중단합니다.

### 사용 예시

```
"이 보드 거버 뽑아줘"
"JLCPCB 에 보낼 제조 파일 만들어줘"
"드릴 파일이랑 위치 파일 생성해줘"
"제조 출력 전에 DRC 랑 동기화 확인부터 해줘"
"IPC-D-356 전기 테스트 넷리스트 뽑아줘"
"발주용 BOM CSV 만들어줘"
```

### 워크플로우

```
[0] 전제 확인
    kicad-cli 필수. KiCad GUI에서 저장(Ctrl+S)했는지 확인합니다 —
    모든 export가 "디스크에 마지막으로 저장된 .kicad_pcb"를 읽기 때문입니다.
    산출물 디렉토리는 사용자가 지정합니다.

[1] DRC 게이트
    kicad-cli pcb drc --format json --severity-all --schematic-parity
    violations(error) / unconnected_items / schematic_parity 세 배열을 모두 봅니다.
    error가 있거나 미배선 넷이 남아 있으면 중단합니다.

[2] 존 채움
    미채움 존은 거버에 구리가 빠진 채로 나갑니다.
    사용자 동의를 받아 --refill-zones --save-board로 채워 저장합니다
    (GUI에서 그 보드가 닫힌 상태에서만).

[3] 회로도-보드 동기화 확인
    IPC-D-356(보드 정본)과 회로도 넷리스트를 diff 합니다.
    "회로도엔 있는데 보드에 없는 핀/넷" = Update PCB 미실행 → 중단.

[4] 거버      레이어 세트를 항상 명시합니다(생략하면 Courtyard·Fab까지 전부 나옵니다)
[5] 드릴      PTH/NPTH 분리 + 드릴 맵, 단위 mm
[6] 위치 파일 SMD only, DNP 제외, 드릴 원점 기준 CSV
[7] BOM       MPN/LCSC 열 포함 발주용 CSV
[8] 산출물 목록 · 검증 리포트 (파일 수·레이어·홀 수·DNP 제외 수·SHA256)
```

### 산출물

| 파일 | 내용 | 받는 곳 |
|------|------|--------|
| `*.gtl/.gbl/.gts/…` + `*.gbrjob` | 거버 (RS-274X/X2) | 팹 |
| `*-PTH.drl` / `*-NPTH.drl` + 드릴 맵 | Excellon 드릴 | 팹 |
| `*-pos.csv` | 위치 파일 (pick and place) | 조립사 |
| `*.ipc` | IPC-D-356 전기 테스트 넷리스트 | 팹 (플라잉 프로브) |
| `*-bom.csv` | 발주용 BOM | 구매/조립사 |
| `SHA256SUMS` | 산출물 체크섬 | 보관 |

팹별 프로파일(레이어 세트·X2 여부·드릴 포맷·위치 파일 헤더)과 검증 체크리스트 14항목은
`skills/kicad-fabricate/references/fabrication-outputs.md`에 있습니다.

### 주의

- **원점을 셋 다 맞춥니다.** 거버 `--use-drill-file-origin`, 드릴 `--drill-origin plot`,
  위치 파일 `--use-drill-file-origin`. 하나만 달라도 조립 좌표가 통째로 어긋납니다.
- **`--smd-only` 결과가 0행이면 THT 전용 보드입니다.** 0행 위치 파일은 보내지 않습니다.
- **회로도에 `MPN` 필드가 없으면 BOM의 MPN 열이 빕니다.** 이때 리포트에 "MPN 부재 — 발주용 아님"이 적힙니다.
- **회전 기준은 보정하지 않습니다.** KiCad 풋프린트의 0도 방향과 조립사 기준이 다를 수 있어, 확인 항목으로 남깁니다.

---

## 설계 → 리뷰 → 보드 → 분석 → 제조 연계

스킬을 순서대로 쓰면 PRD에서 제조 데이터까지 한 흐름으로 이어집니다:

```
1. PRD 작성
2. /kicad-design      → 회로도 생성
3. /kicad-review      → 리뷰 + BOM (메인 세션이 호출)
4. ERROR 수정 후 재리뷰 → ERROR=0 확인
5. /kicad-design 단계 6 (선택) → .kicad_pcb 에 풋프린트·넷 올리기
6. KiCad GUI 에서 보드 외곽(테두리) → 배치 → 배선 (사용자)
7. /kicad-analyze     → 동기화 확인 · 배치 검토 · DRC · SI/PI
8. /kicad-fabricate   → DRC 게이트 통과 후 제조 출력
```

`/kicad-design` 생성이 끝나면 **메인 세션이** `/kicad-review`를 호출합니다
(서브에이전트는 스킬을 부르지 않습니다).

7단계 `/kicad-analyze`에서 배선 전에 특히 도움이 되는 두 가지:

- **회로도-보드 동기화 확인(3.5)** — IPC-D-356과 회로도 넷리스트를 대조해
  "회로도는 고쳤는데 F8(Update PCB)을 안 돌린 보드"를 걸러냅니다.
  이걸 놓치면 이후 PCB 분석이 낡은 보드를 검사해 놓고 "정상"이라고 보고합니다.
- **배치 검토(4.1)** — 넷별 에어와이어 길이 합, 디커플링 캡 ↔ 전원 핀 거리,
  크리스탈 ↔ MCU 거리, 차동쌍 두 넷의 길이 차, 코트야드 겹침·클리어런스를 숫자로 봅니다.
  배치 단계에서 잡으면 배선 후 재작업이 없습니다. `suggest_placement`는 읽기(제안)로만 씁니다.

---

## kicad-cli 활용

`kicad-cli`가 설치되어 있으면 다음 기능이 향상됩니다:

| 기능 | kicad-cli 있을 때 | 없을 때 |
|------|-------------------|---------|
| 넷리스트 추출 | XML 넷리스트 (정확) | .kicad_sch 직접 파싱 (정확도 제한) |
| BOM 추출 | CSV 자동 추출 | 직접 파싱 |
| PDF 시각적 검토 | PDF 내보내기 → 멀티모달 분석 | 건너뜀 |
| 생성 파일 검증 | kicad-cli로 열기 테스트 | 괄호 균형 검사만 |
| 제조 출력(`/kicad-fabricate`) | 거버·드릴·위치·IPC-D-356·BOM 생성 | **불가** — 이 스킬은 kicad-cli가 없으면 시작하지 않습니다 |

### kicad-cli 설치 확인

```bash
kicad-cli --version
# 출력 예: 9.0.8
```

---

## 에이전트 상세

### kicad-schematic-designer

- **역할**: PRD 분석 → IC 선정 → 데이터시트 수집 → .kicad_sch 생성
- **트리거**: `/kicad-design` 스킬에서 위임
- **모델**: opus

### kicad-schematic-reviewer

- **역할**: 8단계 리뷰 (PDF 시각 검토 + 라이브러리 비교 + 체크리스트 + 데이터시트 대조)
- **트리거**: `/kicad-review` 스킬에서 위임
- **모델**: opus

### kicad-bom-generator

- **역할**: 넷리스트에서 BOM 추출 → 마크다운 포맷팅
- **트리거**: `/kicad-review` 스킬에서 위임
- **모델**: opus

### kicad-pcb-analyzer

- **역할**: 엔진 감지 → 회로(넷리스트)/PCB 정밀 분석 (넷 추적, ERC/DRC, 핀 충돌, 트랙/라우팅, SI/PI) → 분석 보고서
- **엔진**: KiCAD-MCP-Server(`mcp__<서버>__*`) → kicad-cli → 직접 파싱 폴백. `tools:` 미명시로 등록된 모든 도구 상속(MCP 포함)
- **트리거**: `/kicad-analyze` 스킬에서 위임
- **모델**: opus

---

## 참조 문서

플러그인 내부의 참조 문서 목록:

| 문서 | 위치 | 내용 |
|------|------|------|
| 리뷰 체크리스트 | `skills/kicad-review/references/review-checklist.md` | 8카테고리 검증 항목 (V+L+A~F) |
| KiCad 파싱 가이드 | `skills/kicad-review/references/kicad-parser.md` | S-expression 파싱 + 넷리스트 추출 |
| 데이터시트 검색 | `skills/kicad-review/references/datasheet-lookup.md` | 제조사별 웹 검색 전략 |
| S-expression 포맷 | `skills/kicad-design/references/kicad-schematic-format.md` | .kicad_sch 생성 포맷 가이드 |
| KiCad 사용법 인덱스 | `skills/kicad-usage/references/INDEX.md` | 토픽 → 다이제스트 파일·anchor 마스터 맵 (544 섹션) |
| KiCad 매뉴얼 다이제스트 | `skills/kicad-usage/references/*.md` | KiCad 10.0 공식 매뉴얼(kicad/pcbnew×6/gerbview/cli) 한국어 다이제스트 9종 |
| 제조 출력 프로파일 | `skills/kicad-fabricate/references/fabrication-outputs.md` | 팹별 프로파일(레이어 세트·X2·드릴·위치 파일) + 산출물 검증 체크리스트 14항목 |

---

## 다른 플러그인과의 관계

### stm32f4 플러그인의 `/kicad-stm32-review`

`pjy-skills` 마켓플레이스에는 STM32F4 전용 회로도 리뷰 스킬(`/kicad-stm32-review`)이 별도로 존재합니다.

| 항목 | `/kicad-review` (이 플러그인) | `/kicad-stm32-review` (stm32f4 플러그인) |
|------|-------------------------------|----------------------------------------|
| 대상 | 모든 도메인 (FPGA, MCU, PHY 등) | STM32F4 MCU 전용 |
| 체크리스트 | 8카테고리, 45+ 항목 (범용) | 8카테고리, 42항목 (STM32F4 특화) |
| AF 매핑 검증 | 도메인 F에서 기본 수준 | AF 테이블 JSON 기반 정밀 검증 |
| 펌웨어 연동 | 없음 | stm32f4-firmware 스킬과 연계 |

**사용 가이드**:
- STM32F4 MCU 보드를 설계하고 **펌웨어까지 연계**할 때 → `/kicad-stm32-review` 권장
- STM32가 아닌 보드, 또는 **FPGA/PHY/전원 등 다중 도메인 보드** → `/kicad-review` 권장
- 두 스킬을 동시에 설치해도 충돌하지 않습니다

### vivado 플러그인

vivado 플러그인에도 KiCad 연동 스킬이 있으나, FPGA 핀 배치와 XDC 파일 생성에 특화되어 있습니다. 회로도 전체 리뷰는 이 플러그인의 `/kicad-review`를 사용하세요.

---

## 자주 묻는 질문

### Q: KiCad가 설치되어 있어야 하나요?

kicad-cli 없이도 동작합니다. 다만 PDF 시각적 검토, 넷리스트 정확도, 생성 파일 검증이 제한됩니다.

### Q: 생성된 회로도를 KiCad에서 바로 열 수 있나요?

네, KiCad 9.x 또는 10.x(생성 시 맞춘 대상 버전) 형식으로 생성되므로 그대로 열 수 있습니다. 다만 **심볼은 파일에 임베드되지만 풋프린트는 임베드되지 않습니다.** `Footprint` 속성이 가리키는 라이브러리가 KiCad의 `fp-lib-table`에 등록돼 있어야 PCB로 넘어갑니다(등록돼 있지 않으면 Update PCB에서 "footprint not found"로 실패).

### Q: 기존 회로도를 수정할 수 있나요?

네, 기존 `.kicad_sch` 파일을 읽고 수정할 수 있습니다. "이 회로도에 SPI Flash 추가해줘" 같은 요청도 가능합니다.

### Q: 리뷰 결과에서 ERROR가 나오면?

보고서에 구체적 수정 방법이 포함됩니다. "C5를 100nF에서 1μF로 변경", "PB6/PB7에 4.7kΩ 풀업 저항 추가" 같은 조치를 따르면 됩니다.

### Q: 거버를 뽑았는데 파일이 너무 많이 나옵니다

`--layers`를 지정하지 않으면 사용 가능한 레이어를 **전부** 플롯합니다 — Courtyard·Fab·Adhesive·Margin·User_* 까지 나옵니다.
`/kicad-fabricate`는 레이어 세트를 항상 명시하므로 이 문제가 생기지 않습니다.
직접 `kicad-cli`를 쓸 때는 `--layers "F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts"` 처럼 세트를 적으세요.

### Q: Edge.Cuts 거버가 안 나옵니다

`--common-layers`(`--cl`)에만 넣었을 가능성이 큽니다. 이 옵션은 **별도 파일을 만들지 않고** 지정한 레이어를 다른 플롯 안에 겹쳐 그립니다.
외곽선을 독립 파일로 받으려면 `--layers` 쪽에 넣어야 합니다.

### Q: 거버 파일 이름이 F_Cu가 아니라 다른 이름입니다

보드에서 레이어 이름을 바꾸면 **출력 파일명도 그 이름을 따릅니다**(예: `F.Cu`를 `Top`으로 바꾼 보드 → `*-Top.gtl`).
`--layers`에 넘기는 이름은 반대로 항상 표준 이름(`F.Cu`, `In1.Cu`, `Edge.Cuts`)입니다.
그래서 산출물 검증은 파일명 문자열이 아니라 **파일 수와 실제 목록**으로 합니다.

### Q: 제조 출력에서 DRC error가 나서 중단됐습니다

의도된 동작입니다. DRC를 통과하지 못한 보드의 제조 파일은 만들지 않습니다.
`/kicad-analyze`로 위반 항목을 확인하고 KiCad에서 수정한 뒤, 저장하고 다시 `/kicad-fabricate`를 실행하세요.

### Q: 어떤 형식의 PRD를 넣어야 하나요?

마크다운, 텍스트, Word 문서 모두 가능합니다. 구두 설명("STM32에 Ethernet 2포트 보드 만들어줘")도 지원합니다. 다만 구체적인 사양이 있을수록 더 정확한 회로도가 생성됩니다.
