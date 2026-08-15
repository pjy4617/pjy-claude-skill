# pjy-claude-skill

Claude Code 플러그인 마켓플레이스 — 하드웨어 개발 스킬·에이전트 + Claude Code 메타 도구 모음

> **"말하면 만들어 준다"** — FPGA 설계부터 MCU 펌웨어까지, Claude Code에서 자연어로 하드웨어 프로젝트를 개발합니다. 그리고 Claude Code 자체 환경(CLAUDE.md / Permissions / Hooks / MCP / Subagent)도 단계적으로 진화시킵니다.

---

## 포함된 플러그인

<table>
<tr>
<td align="center" width="25%">
<img src="assets/mascot-vivado.png" width="220" alt="Vivado Mascot"><br>
<b>Vivado FPGA</b><br>
RTL 설계 → 시뮬레이션 → 합성 → Bitstream<br>
13 스킬 + 6 에이전트
</td>
<td align="center" width="25%">
<img src="assets/mascot-stm32f4.png" width="220" alt="STM32F4 Mascot"><br>
<b>STM32F4 Firmware</b><br>
5단계 파이프라인 + KiCad 검증 + TDD + 빌드 실행 + 코드 리뷰 + QA<br>
5 스킬 + 4 에이전트
</td>
<td align="center" width="25%">
<img src="assets/mascot-wmx3md.png" width="220" alt="WMX3 Mascot"><br>
<b>WMX3 Motion Module</b><br>
3-Layer 모듈 스캐폴딩 + TDD + RT 코드 리뷰<br>
8 스킬 + 6 에이전트
</td>
</tr>
<tr>
<td align="center" width="25%">
<img src="assets/mascot-kicad.png" width="220" alt="KiCad Mascot"><br>
<b>KiCad Schematic</b><br>
PRD → 회로도 생성 + 8단계 리뷰 + BOM + 회로/PCB 분석(SI/PI) + KiCad 10.0 사용법 안내<br>
5 스킬 + 4 에이전트
</td>
<td align="center" width="25%">
<b>WMX3 Application</b><br>
WMX3.7 앱 설계 → C++/C# 구현 → 시뮬레이터 테스트 → 사용 검토(3.6u3→3.7 마이그레이션) + 로봇 옵션(PTP/CP·충돌 감지) + EtherCAT ENI 파일 제작·ESI 분석 + Config Export(파라미터 XML) 분석<br>
7 스킬 + 5 에이전트
</td>
</tr>
<tr>
<td align="center" width="25%">
<b>Sphinx Manual</b><br>
CHM/MD/DOCX → Sphinx 다국어(한/영/일) 매뉴얼 + 품질 리뷰<br>
4 스킬 + 4 에이전트
</td>
<td align="center" width="25%">
<b>Parallel Delegation</b><br>
서브에이전트 병렬 위임 워크플로 + 3-role 에이전트(구현/테스트/구현품질검증) (Claude Code 메타 도구)<br>
2 스킬 + 3 에이전트
</td>
<td align="center" width="25%">
<b>Claude Code Harness</b><br>
CLAUDE.md / Permissions / Hooks / MCP / Subagent / 진화 6단계 진단·진화 (Claude Code 메타 도구)<br>
1 스킬
</td>
</tr>
<tr>
<td align="center" width="25%">
<b>Manual Digest</b><br>
대용량 매뉴얼(PDF/HTML/EPUB/DOCX/CHM/MD) + 소스코드 디렉토리(codebase) 한 번 추출·요약 → ~0.3% 다이제스트만 1차 참조 (Claude Code 메타 도구)<br>
2 스킬
</td>
<td align="center" width="25%">
<b>React-Vite Frontend</b><br>
React 19 + Vite 8 + TS 프론트엔드 — Fluent UI v9 / shadcn/ui 택1, 범용 + UI별 구현·QA specialist 역할 분리<br>
2 스킬 + 6 에이전트
</td>
<td align="center" width="25%">
<b>PCB Design Digest</b><br>
거버/드릴 + PADS(.pcb/.asc) + KiCad(.kicad_pcb/.kicad_sch) 한 번 파싱·요약 → 수 KB 다이제스트만 1차 참조 + pcb-design-analyst 깊은 분석 (Claude Code 메타 도구)<br>
2 스킬 + 1 에이전트
</td>
</tr>
<tr>
<td align="center" width="25%">
<b>RL Control</b><br>
강화학습(RL) 제어 적용 검토(게이트: 고전 제어 우선 판별) → 알고리즘 설계 → Gymnasium/SB3 구현 → 성능·안전 테스트(다중 시드·sim-to-real) → ONNX·C#/C++ 추론 배포 → 운영 데이터 지속 개선<br>
6 스킬 + 4 에이전트
</td>
<td align="center" width="25%">
<b>Doc Atomize</b><br>
대용량 마크다운을 <b>무손실</b> 원자 분할(요약 아님 — 재조립 시 sha256 일치) + <code>&lt;doc-id&gt;.index.md</code> 검색 인덱스 → 질문마다 조각 1~3개만 읽기<br><b>원본을 고치면 훅이 바뀐 조각만 자동 재분할</b> (Claude Code 메타 도구)<br>
2 스킬 + 자동 갱신 훅
</td>
</tr>
<tr>
<td align="center" width="25%">
<b>Orca Worktree</b><br>
Orca 워크트리 생성 시 실행할 setup 훅(<code>orca.yaml</code>) 자동 작성 → 임시 워크트리 <b>실드라이런</b> 검증(소요시간·멱등성) + 프로젝트 설정 적합성 3축 점검 (Orca 메타 도구)<br>
3 스킬
</td>
<td align="center" width="25%">
<b>PRD Plan</b><br>
요구 인터뷰 → PRD → 실행 계획(WBS·의존·마일스톤) → 실행 체크리스트<br>
<b>30년 경력 PM 작성 에이전트 + 쓰기 권한 없는 PMO 검수 에이전트</b>로 자기검증 차단 · REQ→TASK→CHK 추적성 기계 검증<br>
5 스킬 + 2 에이전트
</td>
</tr>
</table>

---

## 스킬과 에이전트란?

Claude Code를 처음 사용한다면, 먼저 이 개념을 이해하세요.

### 스킬 = 작업 절차서

스킬은 Claude에게 **"이 작업은 이 순서로 해라"**라고 알려주는 레시피입니다.
사용자가 `/스킬명` 으로 직접 호출하거나, 대화 내용에 따라 자동으로 트리거됩니다.

```
사용자: "합성해줘"
Claude: (vivado-synth 스킬을 로드하고 정해진 TCL 절차를 실행)
```

### 에이전트 = 전문가

에이전트는 **별도 컨텍스트에서 독립적으로 작업하는 전문가**입니다.
메인 대화를 오염시키지 않고, 결과만 돌려줍니다.

```
사용자: "전체 리뷰해줘"
Claude: (RTL 리뷰어 + TB 리뷰어 + 핀 리뷰어 3명이 병렬로 작업 → 결과만 반환)
```

### 차이 한눈에 보기

| | 스킬 | 에이전트 |
|---|---|---|
| **비유** | 요리 레시피 | 전문 셰프 |
| **동작** | Claude가 레시피 보고 직접 실행 | 별도 전문가가 독립 작업 후 결과만 전달 |
| **언제 사용** | 정해진 절차가 있을 때 | 전문적 판단이 필요할 때 |

**사용할 때 구분할 필요 없습니다.** 원하는 것을 말하면 Claude가 알아서 판단합니다.

---

## 사전 준비

### 필수

- [Claude Code](https://claude.ai/code) 설치 및 실행 가능
- 터미널에서 `claude` 명령어 실행 가능

### 플러그인별 추가 요구사항

<details>
<summary><b>Vivado 플러그인</b></summary>

- AMD Vivado 2020.1 이상 (CLI batch 모드 지원)
- Linux 환경 (Ubuntu 20.04+, WSL2 포함)
- FPGA 보드 (시뮬레이션만 하면 보드 없이도 가능)
- KiCad 8.0+ (KiCad→XDC 자동 생성 사용 시, 선택 사항)

</details>

<details>
<summary><b>STM32F4 플러그인</b></summary>

- **STM32CubeIDE** 설치 (기본 — cmake, ninja, arm-none-eabi-gcc, STM32CubeProgrammer 번들)
- **VS Code** + **STM32 VS Code Extension** (ST 공식 확장)
- 또는 개별 설치: arm-none-eabi-gcc 10.3+, CMake 3.22+, Ninja 1.10+, OpenOCD 0.11+
- Linux 환경 (Ubuntu 20.04+, WSL2 포함)
- KiCad 8.0+ (회로도 검증 사용 시, 선택 사항)

</details>

<details>
<summary><b>WMX3 Motion Module 플러그인</b></summary>

- GCC 11+ (C99 + C++11 지원)
- CMake 3.16 이상
- Linux 환경 (Ubuntu 20.04+, WSL2 포함) 또는 Windows (Visual Studio 2022)
- WMX3 SDK (`LMX_INSTALLER_ROOT` 환경변수, 선택 사항 — 없어도 단위 테스트 가능)

</details>

<details>
<summary><b>WMX3 Application 플러그인</b></summary>

- WMX3 3.7 SDK (Soft Servo Systems / Movensys) — C++ 또는 .NET(WMX3ApiCLR) 개발 환경
- 실 하드웨어 없이도 시뮬레이터 플랫폼(SimuPlatform)으로 모션 검증 가능 — EtherCAT 실기는 선택 사항
- (선택) manual-digest 플러그인으로 `wmx37-user-manual-kr` 매뉴얼 다이제스트 등록 시 API 근거 참조 정확도 향상 — 다관절 로봇(Robot Option) 제어 시 `wmx3-robot-help-kr`도 함께 권장
- (주의) RT 공간 실시간 앱 개발(RTX SDK, VC++ 한정)은 WMX3·RTX 런타임 라이선스와 별도로 IntervalZero RTX SDK 라이선스 필요

</details>

<details>
<summary><b>Sphinx Manual 플러그인</b></summary>

- Python 3.8 이상
- `pip install sphinx sphinx-rtd-theme myst-parser sphinx-copybutton`
- LaTeX 패키지 (PDF 빌드 시, 선택 사항)
- `libchm-bin` 또는 `pychm` (CHM 파일 변환 시, 선택 사항)
- `pandoc` (DOCX 파일 변환 시, 선택 사항)

</details>

<details>
<summary><b>KiCad 플러그인</b></summary>

- KiCad 9.0+ (`kicad-cli` 명령어 사용 가능하면 최적, 없어도 동작)
- Linux 환경 (Ubuntu 20.04+, WSL2 포함)
- 인터넷 연결 (데이터시트 웹 검색용)
- (선택) [Seeed kicad-mcp-server](https://github.com/Seeed-Studio/kicad-mcp-server) — `kicad-analyze`의 PCB 신호/전원 무결성(SI/PI)·정밀 트랙 분석용. KiCad 9.0+ 로컬 설치 전제. 미등록 시 `kicad-cli`/직접 파싱으로 폴백

</details>

<details>
<summary><b>Parallel Delegation 플러그인</b></summary>

- Claude Code만 있으면 동작 (Agent 도구 활성)
- 선택: OMC(oh-my-claudecode) 설치 시 — 동일 역할의 OMC 에이전트(`executor` / `test-engineer` / `verifier`) 자동 인식·연동
- 선택: 사용자 정의 `.claude/agents/` — 같은 역할이 있으면 덮어쓰지 않고 누락분만 보충

</details>

<details>
<summary><b>Claude Code Harness 플러그인</b></summary>

- Claude Code만 있으면 동작 (외부 의존성 없음)
- 분석 대상: 프로젝트의 `CLAUDE.md`, `.claude/settings.json`, `.mcp.json`, `.claude/agents/`, `.claude/hooks/` (있는 만큼만 진단)
- **새 프로젝트보다 2~4주 이상 사용한 프로젝트에 더 효과적** — 진단할 데이터(반복 실수, 안 쓰이는 규칙)가 쌓인 후 도입 권장

</details>

<details>
<summary><b>Manual Digest 플러그인</b></summary>

- Claude Code + Node.js (npx 사용)
- PDF 추출용 MCP: `@sylphx/pdf-reader-mcp` — `manual-digest-setup` 스킬이 자동 등록
- Windows: `cmd /c npx -y @sylphx/pdf-reader-mcp` 래퍼 사용 (PowerShell 환경 안정성)
- 텍스트 레이어 없는 스캔 PDF는 미지원 (OCR은 V2 이후)
- 디스크 쓰기 권한: `<project>/.claude/manuals/` (project scope) 또는 `~/.claude/manuals/` (global scope)

</details>

<details>
<summary><b>React-Vite Frontend 플러그인</b></summary>

- Claude Code + Node.js 20.19+ 또는 22.12+ (Vite 8 요구사항)
- 대상 프로젝트: React 19 + Vite 8 + TypeScript (신규 스캐폴딩도 지원)
- UI 라이브러리: **Fluent UI v9** 또는 **shadcn/ui**(Radix+Tailwind) 중 프로젝트당 택1 — 감지/질문 후 그쪽 컨벤션만 적용 (혼용 금지)
- 권장 스택: Zustand+Immer / (선택) react-konva, @dnd-kit — 이미 다른 스택이 있으면 그쪽을 존중
- 선택: Context7 MCP 설치 시 라이브러리 API를 공식 문서로 확인

</details>

<details>
<summary><b>PCB Design Digest 플러그인</b></summary>

- Claude Code만 있으면 동작 — 거버/드릴/리포트와 PADS `.asc`·KiCad 소스는 전부 텍스트라 `Read`/`Grep`/`Bash`로 파싱 (**MCP 불필요**). PADS 바이너리 `.pcb`만 `strings`로 부분 추출
- 입력 ①거버: 팹 출력 폴더(`.pho`/`.gbr`/`.ger` RS-274X, `.drl`/`.txt` Excellon, `.rep`/`.lst` PADS 리포트, `.gbrjob` KiCad)
- 입력 ②PADS: `.pcb`(네이티브 바이너리 → 부분 추출) 또는 `.asc`(ASCII export → 전체 파싱)
- 입력 ③KiCad: `.kicad_pcb`/`.kicad_sch`/`.kicad_pro` (S-expression 텍스트 → 전체 파싱, 좌표는 항상 mm)
- 디스크 쓰기 권한: `<project>/.claude/pcb-designs/` (project scope) 또는 `~/.claude/pcb-designs/` (global scope)
- 깊은 분석용 `pcb-design-analyst` 에이전트는 `pcb-design-digest-setup`이 `.claude/agents/`로 설치 (신규 설치 시 세션 재시작)

</details>

<details>
<summary><b>RL Control 플러그인</b></summary>

- Claude Code만 있으면 적용 가능성 검토·설계·리뷰 워크플로는 동작 (코드 실행 불필요 — RL이 필요한지부터 판정하는 게이트가 핵심)
- 실제 학습·구현·평가까지 돌리려면 (**선택**): Python 3.10+, PyTorch, [Gymnasium](https://gymnasium.farama.org/), [Stable-Baselines3](https://stable-baselines3.readthedocs.io/) — 오프라인 RL은 d3rlpy, Safe RL은 omnisafe/safety-gymnasium
- 실시간 추론 배포 시 (선택): ONNX / ONNX Runtime
- 학습·평가 환경: 시뮬레이터 또는 로그 데이터 — 안전-크리티컬 장비는 **시뮬레이터 우선 검증 후 사람 감독 하 가드형 실기 전환**(무제약 정책 실기 직배포 금지)
- (선택) Context7 MCP 설치 시 Gymnasium/Stable-Baselines3 등 라이브러리 API를 공식 문서로 확인 — 버전별 세부 API는 단정하지 않고 확인 후 사용
- (선택) 장비가 WMX3 모션 제어 기반이면 `wmx3app`의 SimuPlatform을 Gymnasium 학습·평가 환경으로, `wmx3-app-test`의 실기 전환 체크리스트를 sim-to-real 게이트로 활용 가능

</details>

<details>
<summary><b>Doc Atomize 플러그인</b></summary>

- Claude Code + `python3` (3.8 이상, **표준 라이브러리만** — 추가 패키지·MCP·에이전트 없음)
- Windows: `python3`가 MS Store alias로 exit 49면 `py -3` 또는 `python` 사용
- 입력: 마크다운(`.md`/`.markdown`) — **300줄 이상**일 때 이득이 있습니다(그 미만은 인덱스 유지비가 더 큼)
- PDF/CHM/HTML 매뉴얼은 이 플러그인이 아니라 `manual-digest` 담당 (요약 vs 무손실 분할로 목적이 다름)
- 디스크 쓰기 권한: `<project>/.claude/atomized/` (project scope) 또는 `~/.claude/atomized/` (global scope)
- `--in-place`(원본 자리 재구성)는 git 저장소에서 **클린 상태 + 무손실 검증 통과**일 때만 원본을 제거합니다

</details>

<details>
<summary><b>Orca Worktree 플러그인</b></summary>

- [Orca](https://orca.stably.ai) 설치 + 대상 레포가 **git 저장소**(커밋 1개 이상 — 드라이런이 임시 워크트리를 만듭니다)
- `python3`(표준 라이브러리만) + `bash` — 추가 패키지·MCP·에이전트 없음
- Orca CLI는 선택입니다. 없거나 런타임이 꺼져 있어도 `orca.yaml` 작성·정적 검사·드라이런은 모두 동작하며, Orca 등록 상태 점검만 건너뜁니다
- **리눅스 주의**: bare `orca`는 GNOME Orca **스크린리더**로 잡힐 수 있습니다. `$ORCA_CLI_COMMAND` → `orca-dev` → `orca-ide` → `orca` 순으로 해석합니다
- 생성물(`orca.yaml`, `tools/orca-setup.sh`)은 **커밋해야 팀에 공유**됩니다 (Orca 앱의 로컬 훅은 그 호스트에만 남습니다)
- 훅은 Linux/macOS에서 `/bin/bash`, Windows에서 `%ComSpec%`(cmd.exe)로 실행됩니다 — bash 훅은 Windows 호스트에서 동작하지 않습니다
- setup 훅 예산은 **120초**입니다 (빌드·테스트는 넣지 않습니다)

</details>

<details>
<summary><b>PRD Plan 플러그인</b></summary>

- Claude Code만 있으면 동작합니다. 아래 둘은 **선택**입니다
- `python3`(표준 라이브러리만) — 추적성 검증 스크립트(`check_traceability.py`)용. 없으면 수동 대조로 대체합니다
- Windows: `python3`가 MS Store alias로 exit 49면 `py -3` 또는 `python` 사용
- `doc-atomize` 플러그인 — PRD/PLAN이 40KB를 넘을 때 무손실 분할용. 없으면 통독 폴백으로 동작합니다
- 문서 쓰기 권한: `<project>/docs/{prd,plan,checklist,reviews}` (다른 문서 구조를 쓰고 있으면 셋업이 물어봅니다)
- **에이전트 2종은 새 세션부터 인식**됩니다 — `/prd-setup` 직후 세션 재시작을 권합니다

</details>

---

## 설치 방법 (초보자 가이드)

### Step 1: 마켓플레이스 추가

Claude Code 터미널에서 다음을 입력합니다. **한 번만 하면 됩니다.**

```
/plugin marketplace add pjy4617/pjy-claude-skill
```

이렇게 하면 이 저장소가 마켓플레이스로 등록됩니다.

### Step 2: 원하는 플러그인 설치

#### Vivado (FPGA 개발) 설치

```
/plugin install vivado@pjy-skills
```

13개 스킬이 한 번에 활성화됩니다. 이후 에이전트를 설치합니다:

```
/vivado-setup
```

셋업 시 프로젝트 경로를 질문합니다. 지정한 경로에 6개 에이전트, CLAUDE.md, 디렉토리 구조(`rtl/`, `tb/`, `constraints/`, `scripts/`, `build/`)가 생성됩니다.

#### STM32F4 (MCU 펌웨어) 설치

```
/plugin install stm32f4@pjy-skills
```

5개 스킬이 한 번에 활성화됩니다. 이후 에이전트를 설치합니다:

```
/stm32f4-setup
```

셋업 시 프로젝트 경로를 질문합니다. 지정한 경로에 4개 에이전트, CLAUDE.md, 디렉토리 구조(`Core/`, `Drivers/`, `Middlewares/`, `Startup/`, `Linker/`, `build/`)가 생성됩니다.

#### WMX3 (모션 제어 모듈) 설치

```
/plugin install wmx3md@pjy-skills
```

8개 스킬이 한 번에 활성화됩니다. 이후 에이전트를 설치합니다:

```
/wmx3-setup
```

셋업 시 프로젝트 경로를 질문합니다. 지정한 경로에 6개 에이전트와 CLAUDE.md가 생성됩니다.

#### WMX3 Application (WMX3.7 애플리케이션 개발) 설치

```
/plugin install wmx3app@pjy-skills
```

6개 스킬이 한 번에 활성화됩니다. 이후 에이전트를 설치합니다:

```
/wmx3-app-setup
```

셋업 시 프로젝트 경로를 질문합니다. 지정한 경로에 5개 에이전트와 CLAUDE.md가 생성됩니다. wmx3md(엔진 내부 모듈 개발)와 달리 WMX3 API를 **호출하는 애플리케이션** 개발용입니다.

#### Manual (Sphinx 문서화) 설치

```
/plugin install manual@pjy-skills
```

4개 스킬이 한 번에 활성화됩니다. 이후 에이전트를 설치합니다:

```
/manual-setup
```

4개 에이전트와 CLAUDE.md가 설치됩니다.

#### KiCad (회로도 설계+리뷰) 설치

```
/plugin install kicad@pjy-skills
```

5개 스킬이 한 번에 활성화됩니다(설계·리뷰·분석·설정 + KiCad 사용법 안내 `/kicad-usage`). 이후 에이전트를 설치합니다:

```
/kicad-setup
```

셋업 시 프로젝트 경로를 질문합니다. 지정한 경로에 4개 에이전트와 CLAUDE.md가 생성됩니다.
PCB 신호/전원 무결성(SI/PI)까지 정밀 분석하려면 `/kicad-setup --with-mcp`로 Seeed kicad-mcp-server 등록을 안내받을 수 있습니다(KiCad 9.0+ 로컬 설치 전제).

#### Parallel Delegation (병렬 위임 워크플로) 설치

```
/plugin install parallel-delegation@pjy-skills
```

2개 스킬이 한 번에 활성화됩니다. 이후 3-role 에이전트를 설치합니다:

```
/parallel-delegation-setup
```

셋업 시 프로젝트 경로를 질문합니다. 기존 `.claude/agents/`와 OMC 설치 여부를 자동 스캔해 **누락된 역할만 보충 설치**합니다 (사용자 정의 에이전트 우선, 덮어쓰기 안 함). pd-implementer / pd-tester / pd-verifier 3개 에이전트가 설치됩니다.

#### Claude Code Harness 설치

```
/plugin install harness@pjy-skills
```

1개 스킬이 활성화됩니다. **별도 setup 명령 없음** — 자연어로 "내 프로젝트 하네스 봐줘"라고 말하면 진단이 시작됩니다. 프로젝트 경로 질문 없이 현재 디렉토리에서 동작합니다 (다른 플러그인과 다른 점).

#### Manual Digest (대용량 매뉴얼 다이제스트) 설치

```
/plugin install manual-digest@pjy-skills
```

2개 스킬이 활성화됩니다. **첫 사용 전 1회 환경 초기화 필수**:

```
/manual-digest-setup
```

PDF 추출용 MCP(`@sylphx/pdf-reader-mcp`)를 자동 등록하고 `.claude/manuals/` 디렉토리 + INDEX.md + CLAUDE.md 마커 블록을 생성합니다. **MCP 신규 등록 시 Claude Code 세션 재시작이 필요합니다.** idempotent — 여러 번 실행해도 안전하며 누락분만 보충합니다 (`--scope project|global|both`, `--mcp-only`, `--skip-mcp`, `--repair`, `--dry-run` 옵션).

#### React-Vite (React 19 프론트엔드 개발) 설치

```
/plugin install react-vite@pjy-skills
```

2개 스킬이 한 번에 활성화됩니다. 이후 에이전트를 설치합니다:

```
/react-vite-setup
```

셋업 시 프로젝트 경로를 질문합니다. 지정한 경로에 6개 에이전트(범용 구현/QA 2종 + Fluent UI·shadcn/ui 라이브러리별 구현·QA specialist 4종)와 CLAUDE.md가 생성됩니다. 프로젝트가 한 UI 라이브러리만 쓰면 반대쪽 specialist 2종은 삭제해도 됩니다.

#### PCB Design Digest (PCB 설계 다이제스트) 설치

```
/plugin install pcb-design-digest@pjy-skills
```

2개 스킬이 활성화됩니다. **첫 사용 전 1회 환경 초기화 필수**:

```
/pcb-design-digest-setup
```

`pcb-design-analyst` 에이전트를 `.claude/agents/`에 설치하고 `.claude/pcb-designs/` 디렉토리 + INDEX.md + CLAUDE.md 마커 블록을 생성합니다. **MCP는 불필요**하며(거버·PADS `.asc`·KiCad 소스는 텍스트 파싱, PADS 바이너리 `.pcb`만 `strings` 부분 추출), 에이전트 신규 설치 시 Claude Code 세션 재시작이 필요할 수 있습니다. 이후 `/pcb-design-digest <거버 폴더 | .pcb/.asc | .kicad_pcb/.kicad_sch>`로 보드를 등록하면, 다음부터 "이 보드 외곽 몇 mm야?" 같은 질문이 다이제스트만으로 즉시 처리됩니다. idempotent — `--scope project|global|both`, `--agent-only`, `--skip-agent`, `--repair`, `--dry-run` 옵션.

#### RL Control (강화학습 제어) 설치

```
/plugin install rlcontrol@pjy-skills
```

6개 스킬이 한 번에 활성화됩니다(적용 검토·설계·구현·테스트·지속 개선 + 설정). 이후 에이전트를 설치합니다:

```
/rl-setup
```

셋업 시 프로젝트 경로를 질문합니다. 지정한 경로에 4개 에이전트와 CLAUDE.md가 생성됩니다. 첫 관문인 `rl-assess`는 **강화학습이 정말 필요한지부터 냉정하게 판정**하며, 고전 제어(PID/LQR/MPC)로 충분하면 "RL 부적합 → 고전 제어 권장" 판정(No-Go)을 내릴 수 있습니다 — 이 게이트가 이 플러그인의 가장 큰 차별점입니다.

#### Doc Atomize (마크다운 원자 분할) 설치

```
/plugin install doc-atomize@pjy-skills
```

2개 스킬이 활성화됩니다. **첫 사용 전 1회 환경 초기화 필수**:

```
/doc-atomize-setup
```

`.claude/atomized/` 디렉토리 + INDEX.md + CLAUDE.md 마커 블록을 생성합니다. **MCP도 에이전트도 필요 없고**(Python 표준 라이브러리만 사용) 세션 재시작도 불필요합니다. 설치하면 **PostToolUse 훅**도 함께 켜져, 등록된 원본을 수정하는 즉시 바뀐 조각만 자동 재분할하고 무손실을 재검증합니다(등록 전 문서는 무반응, 훅이 실패해도 편집은 막히지 않음). 이후 `/doc-atomize <큰 .md>`로 문서를 등록하면, 다음부터 그 문서 질문은 인덱스 1개 + 조각 1~3개만 읽고 처리됩니다. `manual-digest`가 외부 매뉴얼을 **요약**해 등록한다면, 이쪽은 손안의 마크다운을 **무손실 분할**합니다 — 조각이 정본이라 원문 그대로 인용할 수 있습니다. `--in-place`로 repo 문서 자체를 재구성할 수도 있습니다(git 클린 + 무손실 검증 통과 시에만 원본 제거).

#### Orca Worktree (워크트리 setup 훅) 설치

```
/plugin install orca-worktree@pjy-skills
```

3개 스킬이 활성화됩니다. **셋업 스킬이 없어 설치 후 바로 사용**합니다(에이전트·MCP 불필요, `python3` + `bash`만 필요).

```
/orca-project-config     ← 현재 설정 상태부터 점검 (읽기 전용)
/orca-setup-build        ← setup 훅 생성 + 드라이런 검증
```

git 워크트리에는 **추적되는 파일만** 따라옵니다 — `node_modules`·`.venv`·`.env`·`.claude/settings.local.json`·대용량 참조 자산은 빠진 채 새 워크트리가 만들어집니다. 이 플러그인은 레포를 프로파일링해 그 준비를 대신할 `orca.yaml`의 `scripts.setup`을 작성하고, **임시 git 워크트리에 `ORCA_*` 환경변수를 주입해 실제로 돌려본 뒤**(소요시간·실패 단계·멱등성) 넘깁니다. Orca가 러너에 주입하는 `set -e`(해제 안 하면 첫 실패에서 나머지가 통째로 누락), 120초 타임아웃, YAML 파싱 실패 시 훅 전체 무시, `.gitignore`가 심볼릭 링크에 매칭되지 않는 문제 같은 실측된 함정을 기본으로 회피합니다.

#### PRD Plan (PRD → 계획 → 체크리스트) 설치

```
/plugin install prd-plan@pjy-skills
```

5개 스킬이 활성화됩니다. 이후 에이전트를 설치합니다:

```
/prd-setup
```

셋업 시 프로젝트 경로를 질문합니다. 지정한 경로에 **작성 에이전트(`prd-writer`)와 검수 에이전트(`prd-reviewer`) 2종**, CLAUDE.md 규약, `docs/{prd,plan,checklist,reviews}` 디렉토리가 생성됩니다.

이 플러그인의 핵심은 **역할 분리**입니다. 작성은 "30년 경력 PM" 페르소나가, 검수는 "PMO 게이트 심사관" 페르소나가 맡되 **검수자에게는 쓰기 권한이 없고 대화가 아니라 저장된 파일을 읽고 판정**합니다 — 작성자가 자기 문서를 스스로 통과시키는 경로가 구조적으로 막힙니다. 여기에 `REQ → TASK → CHK` 추적성을 `check_traceability.py`가 기계 검증해 **MUST 요구 미커버, 수용 기준 없는 요구, 근거 없는 작업, 선행 순환, 근거 없는 완료 표시**를 exit code로 잡아냅니다. 절대 날짜·시간 공수는 만들지 않고(상대 규모 S/M/L/XL), 모르는 값은 `OPEN-###` 미결 이슈로 남깁니다.

```
/prd-write 서보 모니터링 툴      ← 인터뷰 → PRD → 검수 루프 → 승인
/prd-plan docs/prd/PRD-x.md      ← WBS·의존·마일스톤
/prd-checklist docs/plan/PLAN-x.md   ← 체크리스트 (--status / --sync)
/prd-review <외부 문서>          ← 받은 문서 검수만 (읽기 전용)
```

#### 여러 플러그인 동시 설치

```
/plugin install vivado@pjy-skills
/plugin install stm32f4@pjy-skills
/plugin install wmx3md@pjy-skills
/plugin install wmx3app@pjy-skills
/plugin install manual@pjy-skills
/plugin install kicad@pjy-skills
/plugin install parallel-delegation@pjy-skills
/plugin install harness@pjy-skills
/plugin install manual-digest@pjy-skills
/plugin install react-vite@pjy-skills
/plugin install pcb-design-digest@pjy-skills
/plugin install rlcontrol@pjy-skills
/plugin install doc-atomize@pjy-skills
/plugin install orca-worktree@pjy-skills
/plugin install prd-plan@pjy-skills
```

각 플러그인은 독립적이므로 원하는 것만 설치할 수 있습니다.

### Step 3: 설치 확인

설치가 잘 되었는지 확인하려면:

```
/plugin list
```

설치된 스킬이 표시되면 성공입니다.

---

## 사용법

### <img src="assets/mascot-vivado.png" width="48" align="center"> Vivado 플러그인 — 이렇게 말하면 됩니다

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 프로젝트 생성 | "ZedBoard용 OLED 프로젝트 만들어줘" | vivado-project 스킬 |
| RTL 설계 | "SPI 제어 Verilog 모듈 만들어줘" | rtl-designer 에이전트 |
| 코드 리뷰 | "전체 리뷰해줘" | 3개 에이전트 병렬 (RTL+TB+Pin) |
| 시뮬레이션 | "시뮬레이션 돌려줘" | vivado-sim 스킬 |
| 합성 | "합성해줘" | vivado-synth 스킬 |
| Implementation | "impl 돌려줘" | vivado-impl 스킬 |
| Bitstream | "비트스트림 만들어줘" | vivado-bitstream 스킬 |
| 타이밍 문제 | "타이밍 분석해줘" | timing-analyst 에이전트 |
| GUI 확인 | "파형 보여줘" / "스키매틱 보여줘" | vivado-gui 스킬 |
| KiCad→XDC | "KiCad에서 XDC 만들어줘" | kicad-xdc-gen 에이전트 |
| 전체 빌드 | "합성부터 비트스트림까지 돌려줘" | vivado-build-all 스킬 |

#### Vivado 전체 워크플로우

```
"프로젝트 만들어줘"           ← vivado-project 스킬
    ↓
"모듈 만들어줘"               ← rtl-designer 에이전트
    ↓
"전체 리뷰해줘"               ← 3개 에이전트 병렬 검사
    ↓ (FAIL=0 될 때까지 반복)
"시뮬레이션 돌려줘"           ← vivado-sim 스킬
    ↓
"합성해줘"                    ← vivado-synth 스킬
    ↓
"impl 돌려줘"                 ← vivado-impl 스킬
    ↓
"비트스트림 만들어줘"         ← vivado-bitstream 스킬
    ↓
"FPGA에 다운로드해줘"         ← vivado-bitstream 스킬
```

---

### <img src="assets/mascot-stm32f4.png" width="48" align="center"> STM32F4 플러그인 — 이렇게 말하면 됩니다

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 펌웨어 생성 | "STM32F407로 SPI 코덱 펌웨어 만들어줘" | stm32f4-firmware 스킬 (5단계 파이프라인) |
| 회로도 검증 | "KiCad STM32 검토해줘" | kicad-stm32-review 스킬 + checker 에이전트 |
| 테스트 추가 | "테스트 추가해줘" | stm32f4-tdd 스킬 + test-writer 에이전트 |
| TDD 개발 | "TDD로 SPI 드라이버 만들어줘" | test-writer가 Red→Green→Refactor |
| 빌드 실행 | "빌드해줘" / "컴파일해줘" | stm32f4-build 스킬 (CMake+Ninja, CubeMX/CubeIDE 자동 변환) |
| 플래싱 | "빌드하고 플래싱해줘" | stm32f4-build --flash (STM32CubeProgrammer/OpenOCD) |
| 코드 리뷰 | "코드 리뷰해줘" | code-reviewer 에이전트 (34항목) |
| 최종 검수 | "릴리스 가능한지 확인해줘" | qa 에이전트 (PASS/CONDITIONAL/REJECT) |

#### STM32F4 전체 워크플로우

```
"KiCad STM32 검토해줘"        ← 회로도 핀 검증 (42항목), KiCad가 있을 때
    ↓ (ERROR=0 확인)
"이 회로도 기반으로 펌웨어 만들어줘"
    ↓
  Agent 1: 요구사항 분석      ← MCU, 클럭, 페리페럴, 핀 추출
  Agent 2: 아키텍처 설계      ← Bare-metal vs RTOS 판단
  Agent 3: 코드 생성          ← HAL 기반 소스코드
  Agent 4: 빌드 구성          ← CMake/Makefile + 링커 + OpenOCD + VS Code
  Agent 5: 코드 검토          ← 7개 카테고리 검증 (핀, 클럭, 메모리, 테스트 등)
    ↓ (ERROR → 해당 에이전트로 되돌아가 수정, 최대 3회)
"테스트 추가해줘"             ← Unity + FFF 호스트 기반 단위 테스트
    ↓
  cd test && make             ← PC에서 테스트 실행
    ↓
"빌드해줘"                    ← stm32f4-build (.cproject/Makefile → CMake 자동 변환 → 빌드)
    ↓
"코드 리뷰해줘"              ← code-reviewer (34항목 검사)
    ↓
"릴리스 가능한지 확인해줘"    ← qa 에이전트 (종합 판정)
```

---

### WMX3 Motion Module 플러그인 — 이렇게 말하면 됩니다

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 새 모듈 생성 | "CmdBuffer 모듈 만들어줘" | wmx3-module-create 스킬 (designer → generator → build-checker) |
| 빌드 | "빌드해줘" | wmx3-build 스킬 |
| API 추가 | "SetCmdBuffer API 추가해줘" | wmx3-module-add-api 스킬 |
| 테스트 작성 | "테스트 작성해줘" | wmx3-tdd 스킬 + test-writer 에이전트 |
| 코드 리뷰 | "코드 리뷰해줘" | wmx3-code-review 스킬 + code-reviewer 에이전트 |
| 문서 생성 | "API 문서 만들어줘" | wmx3-docs 스킬 + doc-writer 에이전트 |

#### WMX3 전체 워크플로우

```
"새 모듈 만들어줘"               ← wmx3-module-create (3-layer 스캐폴딩)
    ↓  designer → generator → build-checker
"빌드해줘"                       ← wmx3-build (Linux/Windows 자동 감지)
    ↓
"테스트 작성해줘"                ← wmx3-tdd (gtest/gmock)
    ↓
"코드 리뷰해줘"                  ← wmx3-code-review (RT 안전성 35항목)
    ↓ (CRITICAL=0, MAJOR=0 될 때까지 반복)
"API 문서 만들어줘"              ← wmx3-docs (4종 문서 자동 생성)
```

#### 3-Layer 아키텍처

```
사용자 애플리케이션 (C++ / C#)
    ↓ C++ 링크
Layer 2: <ModuleName>Api (C++11 정적 라이브러리)
    ↓ IPC (IMDll)
═══════════ 실시간 경계 ═══════════
Layer 1: <ModuleName> (C99 Core RTDLL/SO)
    ↓
WMX3 엔진 + IMLib + OSL
```

---

### WMX3 Application 플러그인 — 이렇게 말하면 됩니다

WMX3.7 라이브러리를 **사용하는 애플리케이션**(장비 제어 SW)을 설계 → C++/C# 구현 → 시뮬레이터 테스트 → 사용 검토 흐름으로 개발합니다. wmx3md(WMX3 엔진에 로드되는 내부 모듈 rtdll 개발)와 달리, WMX3 API를 **호출하는 응용 프로그램** 쪽을 담당합니다. 다관절 로봇은 로봇 옵션(Robot Option — PTP/CP·충돌 감지)으로 지원합니다.

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 시스템 설계 | "3축 갠트리 장비 WMX 시스템 설계해줘" | wmx3-app-design 스킬 + wmx3app-architect 에이전트 |
| C++/C# 구현 | "이 설계로 C++ 모션 프로그램 작성해줘" | wmx3-app-implement 스킬 + wmx3app-implementer 에이전트 |
| 테스트 | "시뮬레이터로 모션 테스트해줘" | wmx3-app-test 스킬 + wmx3app-test-engineer 에이전트 |
| 사용 검토 | "이 프로젝트 WMX3 사용법 점검해줘" | wmx3-app-review 스킬 + wmx3app-usage-reviewer 에이전트 |
| 3.7 마이그레이션 | "3.6u3 코드 3.7 이식 검토해줘" | wmx3-app-review / wmx3-app-implement |
| 로봇 제어 | "6축 로봇 PTP/CP 시스템 설계해줘" | wmx3-app-design / wmx3-app-implement (Robot Option) |
| ENI 파일 제작·ESI 분석 | "서보 4축 + IO 2대 구성 ENI 파일 만들어줘" / "보유 ESI 파일 분석해줘" | wmx3-app-eni 스킬 + wmx3app-eni-builder 에이전트 |
| Config Export 분석 | "wmx_parameters.xml 분석해줘" / "엔진 파라미터 export 검토해줘" | wmx3-app-config-xml-analy 스킬 (파서 + 안전 검토) |
| 에이전트 설치 | "wmx3app 설정해줘" | wmx3-app-setup 스킬 |

#### WMX3 Application 전체 워크플로우

```
"WMX 시스템 설계해줘"            ← wmx3-app-design (플랫폼 선택·축 구성·기능 매핑·성능/안정성 전략)
    ↓
"설계대로 구현해줘"              ← wmx3-app-implement (C++/C# 초기화 시퀀스·모션·에러 처리)
    ↓
"시뮬레이터로 테스트해줘"        ← wmx3-app-test (SimuPlatform — 실 HW 없이 모션 검증)
    ↓
"WMX3 사용법 점검해줘"           ← wmx3-app-review (7카테고리 체크리스트, CRITICAL/MAJOR/MINOR/INFO)

"엔진 파라미터 export 분석해줘"  ← wmx3-app-config-xml-analy (파라미터 export XML — 설정 축 식별·안전 일관성 검토)
```

> **wmx3md와의 차이**: wmx3md는 WMX3 엔진에 로드되는 **내부 모듈(rtdll) 개발**, wmx3app은 WMX3 API를 호출하는 **애플리케이션 개발**입니다.
>
> **manual-digest 연동 권장**: `/manual-digest`로 WMX3.7 매뉴얼(`wmx37-user-manual-kr`)을 등록하면 설계·구현·검토 시 API 근거를 다이제스트에서 1차 참조합니다. 다관절 로봇 제어를 다루면 로봇 매뉴얼(`wmx3-robot-help-kr`)도 함께 등록하세요.

---

### Sphinx Manual 플러그인 — 이렇게 말하면 됩니다

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 매뉴얼 생성 | "사용자 매뉴얼 만들어줘" | manual-write 스킬 (6단계 프로세스) |
| Doxygen 변환 | "MD 파일들을 Sphinx로 변환해줘" | sphinx-manual-writer 에이전트 |
| DOCX 변환 | "Word 문서를 Sphinx로 변환해줘" | manual-write 스킬 (Phase 1-E) |
| 빌드 | "매뉴얼 빌드해줘" | manual-build 스킬 |
| 품질 리뷰 | "매뉴얼 리뷰해줘" | manual-review 스킬 + reviewer 에이전트 |

#### Manual 전체 워크플로우

```
"매뉴얼 만들어줘"                 ← manual-write (Phase 1~6)
    ↓  소스 분석 → 구조 제안(승인) → Sphinx 초기화 → 내용 작성 → 빌드 → 검증
"매뉴얼 리뷰해줘"                 ← manual-review (6카테고리 100점)
    ↓  자동 수정 가능 이슈 → "수정할까요?" → 재빌드
"매뉴얼 빌드해줘"                 ← manual-build (HTML/PDF/EPUB, 다국어)
```

---

### <img src="assets/mascot-kicad.png" width="48" align="center"> KiCad 플러그인 — 이렇게 말하면 됩니다

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 회로도 생성 | "이 PRD로 회로도 만들어줘" | kicad-design 스킬 + designer 에이전트 |
| 회로도 리뷰 | "회로도 리뷰해줘" | kicad-review 스킬 + reviewer 에이전트 |
| BOM 생성 | "BOM 만들어줘" | kicad-review 스킬 + bom-generator 에이전트 |
| 데이터시트 비교 | "IC 데이터시트 확인해줘" | kicad-review 스킬 (단계 6) |
| PCB 분석 | "PCB 분석해줘 / DRC 돌려줘" | kicad-analyze 스킬 + pcb-analyzer 에이전트 |
| 넷 추적 | "+3V3 넷에 뭐 연결됐는지 추적해줘" | kicad-analyze 스킬 (단계 3) |
| 신호/전원 무결성 | "차동 페어 임피던스·길이 매칭 확인해줘" | kicad-analyze 스킬 (단계 5, Seeed MCP 권장) |
| 부품 변경 | "RJ45로 바꿔줘" | kicad-design 에이전트 (수정 모드) |
| **KiCad 사용법** | "차동쌍 어떻게 배선해? / 거버 어떻게 내보내? / 커스텀 DRC 룰 문법? / 단축키 알려줘" | **kicad-usage 스킬** (KiCad 10.0 매뉴얼 다이제스트) |
| 에이전트 설치 | "KiCad 설정해줘" | kicad-setup 스킬 (`--with-mcp`로 Seeed MCP 등록) |

#### KiCad 전체 워크플로우

```
"이 PRD로 회로도 만들어줘"       ← kicad-design (5단계)
    ↓  요구사항 분석 → IC 선정 → 데이터시트 수집 → .kicad_sch 생성 → 리뷰
"회로도 리뷰해줘"                ← kicad-review (8단계)
    ↓  PDF 시각 검토 → 라이브러리 비교 → 체크리스트 → 데이터시트 대조
"BOM 만들어줘"                   ← BOM 마크다운 생성
    ↓
KiCad GUI에서 와이어 보정 (5~15분)
    ↓
"ERROR 수정해줘"                 ← ERROR 항목 수정 후 재리뷰
    ↓ (ERROR=0 확인)
PCB 레이아웃 진행
    ↓
"PCB 분석해줘 / DRC 돌려줘"      ← kicad-analyze (6단계)
    ↓  넷 추적 → ERC/DRC → 트랙/라우팅 → 신호·전원 무결성(SI/PI)
       (Seeed MCP 등록 시 SI/PI 정밀, 없으면 kicad-cli/직접 파싱 폴백)
```

---

### Parallel Delegation 플러그인 — 이렇게 말하면 됩니다

여러 독립 작업을 **하나의 응답 메시지**에 다수 Agent 호출로 묶어 동시 실행하는 워크플로. 순차 실행 대비 벽시계 시간을 가장 느린 작업 하나의 길이로 압축합니다.

| 하고 싶은 것 | 이렇게 말하세요 | 동작 |
|-------------|---------------|------|
| 다부분 작업 동시 실행 | "A하고 B하고 C 한 번에 해줘" / "동시에" / "한꺼번에" | 메인이 단일 응답에 다수 Agent 호출 |
| 구현 + 테스트 분리 | "구현해줘 + 테스트도 추가" | pd-implementer + pd-tester 병렬 |
| 자기 검증 함정 차단 | "리뷰해줘" / "검증해줘" | pd-verifier — 구현·테스트와 분리된 시각 |
| 다파일 리팩토링 | "X 모듈 리팩토링하면서 테스트 갱신" | 다수 pd-implementer 병렬 |
| 3-role 에이전트 설치 | "병렬 위임 설정", "3-role 셋업" | parallel-delegation-setup 스킬 |

#### 3-role 분리 패턴

```
[메인 Claude]
    ↓ (단일 응답에 3개 Agent 호출 묶음)
    ├──[pd-implementer]── 구현 전담 ("어떻게 동작하게 할지")
    ├──[pd-tester]────── 테스트 전담 ("무엇이 옳은 동작인지")
    └──[pd-verifier]──── 구현품질검증 ("결과물이 사양·통합·품질을 만족?")
    ↓
결과 합성·검증 → 사용자
```

> **핵심: 메시지 단위 = 병렬 단위.** 하나의 응답에 묶인 Agent 호출만 동시 시작. 첫 호출 결과를 보고 두 번째를 호출하면 순차로 변해 시간 이득이 사라집니다.
>
> **OMC 호환**: oh-my-claudecode 설치 환경에선 OMC의 `executor` / `test-engineer` / `verifier`가 같은 역할을 수행 — 셋업 스킬이 자동 인식해 중복 설치를 피합니다.

---

### Claude Code Harness 플러그인 — 이렇게 말하면 됩니다

이 플러그인은 다른 플러그인과 달리 **하드웨어 도구가 아니라 Claude Code 자체 환경**(CLAUDE.md / Permissions / Hooks / MCP / Subagent / 진화 원칙)을 단계적으로 진단·강화합니다.

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 모드 |
|-------------|---------------|---------------|
| 전체 진단·보강 | "내 프로젝트 하네스 봐줘" / "어디 약해?" | 모드 A 전체 흐름 |
| 진단만 | "지금 상태만 알려줘. 변경은 하지 말고" | 모드 B 진단만 |
| 단일 단계 | "rm 같은 거 막아줘" / "코드 수정 시 npm test 자동" | 모드 C 특정 단계 |
| 진화 점검 | "Opus 4.7 올렸어, 점검해줘" / "오래된 규칙 정리" | 모드 D 진화 점검 |

#### 하네스 진화 워크플로우

```
"하네스 봐줘"                    ← Phase 0 진단 (6단계 ✅/⚠️/❌ + 우선순위 추천)
    ↓
"단계 2부터" / "rm 막아줘"       ← 5-step 패턴 ([a]현재상태 → [b]추천 → [c]확정대기 → [d]적용 → [e]다음 단계)
    ↓ (사용자 명시 승인 — "적용해" / "yes")
파일 Edit/Write 적용
    ↓
"다음 단계 진행"                 ← 의존성 순: deny → Hook → CLAUDE.md → Subagent
    ↓
정기 점검 루틴                   ← 월 1회 / 모델 업그레이드 후 / 마일스톤 종료 후
```

> **추천만 하고 임의로 적용하지 않습니다.** 명시적 승인("적용해" / "yes") 후에만 파일을 수정합니다.
>
> **새 프로젝트보다 기존 프로젝트 진화에 효과적**. 새 프로젝트는 `/init` + 2~4주 사용 후 도입을 권장합니다 — 자세한 내용은 [`plugins/harness/docs/usage-guide.md`](plugins/harness/docs/usage-guide.md).

---

### Manual Digest 플러그인 — 이렇게 말하면 됩니다

대용량 매뉴얼 **또는 소스코드 디렉토리**를 **한 번만** 추출·요약하여 마크다운 다이제스트로 저장하고, 이후 작업에서는 다이제스트(원본의 ~0.3% 크기)를 1차 참조하는 워크플로. 디테일이 필요할 때만 원본의 특정 페이지/섹션(문서) 또는 파일/심볼(코드)만 핀포인트로 다시 읽습니다 (실측: TwinCAT 168p 매뉴얼 6.29 MB → 18.6 KB; HMI Frontend 18,079 LOC → ~14 KB).

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬 |
|-------------|---------------|--------------|
| 환경 셋업(1회) | "manual-digest 셋업" / `/manual-digest-setup` | manual-digest-setup 스킬 |
| 매뉴얼 등록 | "이 PDF 등록해줘" / `/manual-digest <path>` | manual-digest 스킬 (8단계) |
| 코드베이스 등록 | "이 레포 코드 다이제스트 만들어줘" / `/manual-digest <dir>` | manual-digest 스킬 (`format: codebase`, MCP 불필요) |
| Global scope 등록 | `/manual-digest <path> --scope global` | 모든 프로젝트 공유 |
| 원본 변경 시 갱신 | `/manual-digest --update <id>` | 문서=sha256 / 코드=git ref 비교 → 변경분만 재요약 |
| 등록 매뉴얼 목록 | "등록된 매뉴얼 목록" / `/manual-digest --list` | INDEX.md 출력 |
| 매뉴얼 제거 | `/manual-digest --remove <id>` | 디렉토리 + INDEX.md + CLAUDE.md 카탈로그 갱신 |
| 자동 활용 | (도메인 매뉴얼 질문) | Claude가 INDEX.md → digest.md → 필요 시 원본 핀포인트 |

#### 지원 포맷

| 포맷 | 추출 도구 |
|------|-----------|
| PDF | `@sylphx/pdf-reader-mcp` MCP (`mcp__pdf-reader__read_pdf`) |
| HTML | Claude Read 직접 |
| TXT/MD | Claude Read 직접 |
| EPUB | PowerShell `Expand-Archive` → 내부 XHTML |
| DOCX | PowerShell `Expand-Archive` → `word/document.xml` |
| CHM | `hh.exe -decompile` (Windows 전용) |
| **codebase (디렉토리)** | **Claude Read/Grep/Glob + `find`/`git` (PDF MCP 불필요)** |

#### Manual Digest 전체 워크플로우

```
"manual-digest 셋업"             ← manual-digest-setup (MCP 등록 + 디렉토리 + CLAUDE.md 마커)
    ↓ (Claude Code 재시작)
"이 매뉴얼 등록해줘"              ← /manual-digest <path>
    ↓  ① 입력 검증 → ② ID 결정 → ③ 텍스트 추출 → ④ TOC 파싱
    ↓  ⑤ 섹션 청킹(~20% 샘플링) → ⑥ 계층 요약 → ⑦ 산출물 작성 → ⑧ 카탈로그 갱신
산출물: <scope>/.claude/manuals/<id>/{digest.md, index.md, metadata.json}
    ↓
(이후 매뉴얼 관련 질문)          ← Claude 자동 동작
    ↓  INDEX.md 확인 → digest.md 1차 참조 → 부족 시 index.md → 원본 페이지 핀포인트
    ↓  답변 + 출처 명시 (§/p./scope)
"원본 변경됨"                     ← /manual-digest --update <id> (sha256 비교, 변경분만)
```

#### Scope 결정 가이드

| 상황 | 권장 scope |
|------|-----------|
| 특정 보드 데이터시트, 프로젝트 전용 SDK | `project` (기본) |
| ARM Cortex-M TRM, C99 표준 등 표준 매뉴얼 | `global` |
| 여러 프로젝트 공유 라이브러리 매뉴얼 | `global` |

> **MCP 재시작 주의**: `manual-digest-setup`이 PDF MCP를 신규 등록하면 Claude Code 세션을 종료 후 다시 시작해야 `mcp__pdf-reader__read_pdf` 도구가 활성화됩니다.
>
> **CLAUDE.md 마커 블록**: 셋업이 `<!-- manual-digest:start --> ... <!-- manual-digest:end -->` 마커 사이에 사용 규칙을 주입합니다 — 마커 외부 콘텐츠는 절대 건드리지 않습니다. 손상 시 `/manual-digest-setup --repair`.

---

### React-Vite Frontend 플러그인 — 이렇게 말하면 됩니다

React 19 + Vite 8 + TypeScript 프론트엔드를 **구현 → 검증**의 역할 분리 흐름으로 개발합니다. **범용 에이전트**(React/Vite/상태/구조)와 **UI 라이브러리 specialist**(테마·컴포넌트·전용 테스트)를 **별도 패스**로 운용해, 한 에이전트가 자기 코드를 검증할 때 생기는 자기검증 함정을 차단합니다. UI 라이브러리는 **Fluent UI v9** 또는 **shadcn/ui** 중 프로젝트당 하나를 골라(감지/질문) 그쪽 specialist만 씁니다.

**에이전트 6종**: 범용 `react-vite-program-expert`/`react-vite-qa-expert` + Fluent `react-vite-fluent-ui-expert`/`react-vite-fluent-ui-qa-expert` + shadcn `react-vite-shadcn-ui-expert`/`react-vite-shadcn-ui-qa-expert`.

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|--------------|
| 환경 셋업 | "react-vite 셋업" / `/react-vite-setup` | react-vite-setup 스킬 |
| 기능 개발(구현→검증) | "이 PRD로 화면 구현하고 테스트까지 해줘" | react-vite-frontend 스킬 (specialist 자동 라우팅) |
| 범용 구현 | "Zustand 스토어에 액션 추가해줘" | react-vite-program-expert |
| Fluent UI 구현 | "Fluent 테마 설정/DataGrid 만들어" | react-vite-fluent-ui-expert |
| shadcn 구현 | "shadcn으로 Combobox 만들어" | react-vite-shadcn-ui-expert |
| UI 테스트 작성 | "이 Radix Select 테스트 작성해줘" | react-vite-shadcn-ui-qa-expert (Fluent이면 fluent-ui-qa) |
| 범용 검증 | "Zustand/성능 회귀 검증해줘" | react-vite-qa-expert |

#### 워크플로우

```
"이 기능 구현하고 테스트까지 해줘"   ← react-vite-frontend 스킬
    ↓  ① 컨텍스트 파악(package.json/PRD/UI 라이브러리 감지) → ② 분해(타입/스토어/컴포넌트)
    ↓  ③ 구현 위임 → 범용(program-expert) + UI specialist(fluent/shadcn-ui-expert)
    ↓  ④ npm run dev / tsc --noEmit 로 동작·타입 확인
    ↓  ⑤ 검증 위임 → 범용(qa-expert) + UI QA specialist (Vitest/RTL/Playwright/axe-core + 성능)
    ↓  ⑥ 지적사항 다시 해당 구현 에이전트로 반영 (⑤↔⑥ 반복)
```

---

### PCB Design Digest 플러그인 — 이렇게 말하면 됩니다

PCB 설계 입력 세 종류 — **①거버/드릴 출력 폴더 ②PADS 레이아웃(`.pcb`/`.asc`) ③KiCad 소스(`.kicad_pcb`/`.kicad_sch`)** — 을 **한 번만** 파싱·요약하여 마크다운 다이제스트로 저장하고, 이후 보드 질문("외곽 몇 mm?", "홀 몇 개?", "최소 트레이스 폭?", "넷 몇 개?")은 원본을 다시 파싱하지 않고 다이제스트(수 KB)를 1차 참조합니다. 디테일이 필요할 때만 원본의 특정 레이어/좌표/넷을 핀포인트로 재파싱하고, SI/PI·차동쌍·플레인 분할 같은 깊은 분석은 `pcb-design-analyst` 에이전트가 담당합니다. `manual-digest`의 PCB 버전 — 거버·PADS `.asc`·KiCad는 전부 텍스트라 **MCP 불필요**(PADS 바이너리 `.pcb`만 `strings` 부분 추출).

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|--------------|
| 환경 셋업(1회) | "pcb-design-digest 셋업" / `/pcb-design-digest-setup` | pcb-design-digest-setup 스킬 (에이전트 설치) |
| 거버/PADS/KiCad 등록 | "이 거버 폴더 등록해줘" / "이 .kicad_pcb 등록해줘" / `/pcb-design-digest <폴더 또는 파일>` | pcb-design-digest 스킬 (8단계) |
| Global scope 등록 | `/pcb-design-digest <폴더 또는 파일> --scope global` | 모든 프로젝트 공유 |
| 원본 변경 시 갱신 | `/pcb-design-digest --update <id>` | sha256 비교 → 변경 파일만 재파싱 |
| 등록 보드 목록 | "등록된 PCB 목록" / `/pcb-design-digest --list` | INDEX.md 출력 |
| 보드 제거 | `/pcb-design-digest --remove <id>` | 디렉토리 + INDEX.md + CLAUDE.md 갱신 |
| 깊은 분석 | "이 보드 SI/제조성 검토해줘" | pcb-design-analyst 에이전트 |
| 자동 활용 | (보드/PCB 질문) | Claude가 INDEX.md → digest.md → 필요 시 원본 핀포인트 |

#### 지원 입력 (`format` 자동 식별)

| 입력군 | 파일 | 추출 | 식별 근거 |
|--------|------|------|----------|
| 거버 (gerber) | `.pho`/`.gbr`/`.ger` (RS-274X) + `.drl`/`.txt` (Excellon) + `.rep`/`.lst`/`.gbrjob` | full (텍스트) | 거버 헤더 `G04 PADS`/`TF.GenerationSoftware,KiCad`, Excellon 헤더 |
| PADS (pads) | `.pcb` (네이티브 바이너리) | partial (`strings`) | 바이너리 시그니처 `PADS`/팹 스펙 문자열 |
| PADS (pads) | `.asc` (ASCII export) | full (텍스트) | `*PADS-...*` 텍스트 헤더 |
| KiCad (kicad) | `.kicad_pcb`/`.kicad_sch`/`.kicad_pro` | full (텍스트, 좌표 mm) | `(kicad_pcb …)` / `(kicad_sch …)` S-expr |

> 레거시(PADS 등) 거버 출력의 정상적 부재(전용 외곽 파일·`.gbrjob`·paste 거버 없음)는 Critical이 아니라 Info로 처리하고, 외곽은 동박/실크 폴리라인·좌표 bbox에서 추출합니다. PADS 바이너리 `.pcb`는 부분 추출(`extraction=partial`)이라 `.asc` export를 권장합니다.

#### PCB Design Digest 전체 워크플로우

```
"pcb-design-digest 셋업"         ← pcb-design-digest-setup (에이전트 설치 + 디렉토리 + CLAUDE.md 마커)
    ↓ (에이전트 신규 설치 시 Claude Code 재시작)
"이 거버 폴더/.pcb/.kicad_pcb 등록해줘"  ← /pcb-design-digest <폴더 또는 파일>
    ↓  ① 입력 검증·format 판별(gerber|pads|kicad) → ② ID 결정 → ③ 인벤토리 → ④ 단위/좌표 디코드
    ↓  ⑤ 깊은 파싱(pcb-design-analyst 위임 / 직접 파싱) → ⑥ sha256 → ⑦ 산출물 → ⑧ 카탈로그 갱신
산출물: <scope>/.claude/pcb-designs/<id>/{digest.md, index.md, metadata.json}
    ↓
(이후 보드/PCB 질문)            ← Claude 자동 동작
    ↓  INDEX.md 확인 → digest.md 1차 참조 → 부족 시 index.md → 원본 레이어/좌표/넷 핀포인트
    ↓  답변 + 출처 명시 (파일·D-code/넷·scope)
"원본 변경됨"                     ← /pcb-design-digest --update <id> (sha256 비교, 변경분만)
```

> **단위 혼재 주의**: PADS `.rep` Width는 mm, 본문 거버는 inch — 다이제스트는 inch·mm를 **둘 다** 병기합니다. 드릴 포맷 헤더가 없으면 동박 패드 플래시에 앵커링해 좌표 포맷을 역산 확정합니다. KiCad 소스는 좌표가 항상 mm, PADS 바이너리 `.pcb`는 좌표 포맷 불명(부분 추출).
>
> **CLAUDE.md 마커 블록**: 셋업이 `<!-- pcb-design-digest:start --> ... <!-- pcb-design-digest:end -->` 마커 사이에 사용 규칙을 주입합니다 — 마커 외부 콘텐츠는 건드리지 않습니다. 손상 시 `/pcb-design-digest-setup --repair`.

---

### RL Control 플러그인 — 이렇게 말하면 됩니다

강화학습(RL)을 장비/제어 시스템에 적용하는 워크플로를 **적용 가능성 검토(게이트) → 알고리즘 설계 → 구현 → 성능·안전 테스트 → 지속 개선(운영 데이터 재학습)** 흐름으로 진행합니다. 20년 이상 상용 장비 제어에 RL을 적용해 온 전문가 관점에서, 무엇보다 **RL이 정말 필요한지부터 냉정하게 판별**합니다 — 대부분의 제어 문제는 고전 제어(PID/LQR/MPC)로 충분하고, RL은 안전성·재현성·샘플효율·검증난이도 리스크를 들여오기 때문입니다. 안전-크리티컬 장비는 시뮬레이터 우선 검증 → 사람 감독 하 가드형 실기 전환을 전제로 합니다.

| 하고 싶은 것 | 이렇게 말하세요 | 동작하는 스킬/에이전트 |
|-------------|---------------|---------------------|
| 적용 가능성 검토(게이트) | "이 제어에 강화학습 쓸 수 있나 검토해줘" / "RL 타당성 검토" | rl-assess 스킬 + rlctrl-feasibility-analyst 에이전트 |
| MDP 정식화 | "이 문제 MDP로 정식화해줘" | rl-assess 스킬 (상태/행동/보상/에피소드 경계) |
| 알고리즘 선정·설계 | "SAC랑 PPO 중 뭐 써야 해?" / "보상 함수 설계해줘" | rl-design 스킬 + rlctrl-algorithm-designer 에이전트 |
| 안전 강화학습 설계 | "안전 제약 있는 RL 설계해줘" | rl-design 스킬 (제약 MDP·Lagrangian·shielding) |
| 환경·학습 구현 | "Gymnasium 환경 만들고 SB3로 학습해줘" | rl-implement 스킬 + rlctrl-implementer 에이전트 |
| 실시간 추론 배포 | "학습한 정책 ONNX로 배포해줘" / "C#/C++ 구동 프로그램에 배포해줘" | rl-implement 스킬 (안전 계층·추론 지연 예산·ONNX→C#/C++ 추론·정규화 패리티) |
| 성능·안전 테스트 | "정책 성능 평가해줘" / "sim-to-real 검증해줘" | rl-test 스킬 + rlctrl-evaluator 에이전트 |
| 지속 개선(운영 데이터 재학습) | "운영 데이터로 모델 더 학습해서 성능 높여줘" | rl-improve 스킬 (오프라인 재학습·champion/challenger·재배포 가드 게이트) |
| 에이전트 설치 | "rlcontrol 설정해줘" | rl-setup 스킬 |

#### RL Control 전체 워크플로우

```
"이 제어에 강화학습 쓸 수 있나 검토해줘"   ← rl-assess (MDP 정식화·고전 제어 대비·타당성 체크리스트)
    ↓  Go/No-Go 판정 — No면 고전 제어/하이브리드 권장, Go면 문제 규격서로
"알고리즘 검토·설계해줘"                     ← rl-design (알고리즘 선정·환경/보상/안전 설계)
    ↓
"환경 구현하고 학습해줘"                     ← rl-implement (Gymnasium 5-튜플·SB3/CleanRL·ONNX 배포)
    ↓
"성능·안전 테스트해줘"                       ← rl-test (다중 시드 통계·제약 위반율·강건성·sim-to-real)
    ↓ (PASS 시) 사람 감독 하 가드형 실기 전환
    ↓ (운영 후)
"운영 데이터로 모델 더 학습해줘"             ← rl-improve (수집→오프라인 재학습→재검증→가드형 재배포 루프)
```

> **RL을 쓰면 안 되는 경우가 있습니다.** `rl-assess` 게이트는 "안전 크리티컬 + 시뮬레이터 없음 + 온라인 탐색 불가" 같은 조건에서 **No-Go(고전 제어 권장)** 판정을 내립니다 — 이것이 이 플러그인의 핵심 차별점입니다.
>
> **Gymnasium API 주의**: 구 Gym의 4-튜플이 아니라 **5-튜플** — `reset(seed=...) -> (obs, info)`, `step(action) -> (obs, reward, terminated, truncated, info)`. 라이브러리 버전별 세부 API는 Context7/공식 문서로 확인합니다.
>
> **WMX3 연동**: 장비가 WMX3 모션 제어 기반이면 `wmx3app`의 SimuPlatform을 Gymnasium 학습·평가 환경으로, `wmx3-app-test`의 실기 전환 체크리스트를 sim-to-real 게이트로 활용할 수 있습니다.

---

### Doc Atomize 플러그인 — 이렇게 말하면 됩니다

대용량 마크다운을 **무손실로 원자 분할**하고 검색 인덱스를 만듭니다. 요약이 아니라 분할이므로 **조각을 합치면 원본과 sha256이 일치**하고, 조각 자체가 정본이라 원문 그대로 인용할 수 있습니다. 이후 그 문서에 대한 질문은 원본을 다시 읽지 않고 `인덱스 1개 + 조각 1~3개`로 처리됩니다.

| 상황 | 이렇게 말하세요 | 실행되는 것 |
|------|----------------|-------------|
| 환경 셋업(1회) | "doc-atomize 셋업" / `/doc-atomize-setup` | doc-atomize-setup 스킬 (디렉토리 + INDEX.md + CLAUDE.md 마커) |
| 문서 분할 | "이 md 파일 쪼개줘" / `/doc-atomize <file.md>` | doc-atomize 스킬 (8단계: 분할→무손실 검증→요약 큐레이션→카탈로그 등록) |
| repo 문서 재구성 | `/doc-atomize <file.md> --in-place` | 원본 자리에 인덱스+조각 생성 (git 클린 + 검증 통과 시에만 원본 제거) |
| Global scope 등록 | `/doc-atomize <file.md> --scope global` | 모든 프로젝트 공유 |
| 원본 변경 시 갱신 | **자동**(PostToolUse 훅) 또는 `/doc-atomize --update <id>` | sha256 비교 → 변경 조각만 재생성, 큐레이션 승계, ⚠️로 요약 재검토 표시 |
| 무손실 재검증 | `/doc-atomize --verify <id>` | 재조립 sha256 대조 + 커버리지·링크 검사 |
| 등록 문서 목록 | "등록된 문서 목록" / `/doc-atomize --list` | INDEX.md 출력 |
| 문서 제거 | `/doc-atomize --remove <id>` | 디렉토리 + INDEX.md 항목 갱신 |

```
"doc-atomize 셋업"                ← doc-atomize-setup (MCP·에이전트 불필요, 세션 재시작 불필요)

"이 PRD 매번 통째로 읽기 부담돼"    ← /doc-atomize docs/HW_PRD.md
"큰 마크다운 분할해줘"             ← 헤딩 우선 + 크기 가드 하이브리드 분할
"문서 원자화해줘"                  ← 조각 + <doc-id>.index.md 생성

"원본 바뀌었어"                    ← /doc-atomize --update <id> (변경 조각만, 요약은 ⚠️로 재검토 표시)
```

**실측** (884줄 / 41.7 KB PRD): 조각 13개(평균 68줄), 인덱스 7.9 KB. 원본 통째 읽기 41.7 KB → 인덱스 + 조각 1개 11.5 KB (**28%**).

> **manual-digest와 구분**: PDF/CHM 같은 외부 매뉴얼을 **요약**해 등록하는 것은 `manual-digest`(원본의 ~0.3%, 손실 있음), 손안의 큰 `.md`를 **무손실 분할**하는 것은 `doc-atomize`입니다.
>
> **인덱스 파일명 규칙**: 문서별 인덱스는 `index.md`가 아니라 `<doc-id>.index.md`입니다. 문서가 여러 개일 때 `index.md` 난립과 `INDEX.md`(마스터)와의 대소문자 혼동을 막고, `Glob **/*.index.md` 한 번으로 전 문서 인덱스를 열거할 수 있습니다.
>
> **300줄 미만은 분할하지 않습니다** — 인덱스 유지비가 이득보다 큽니다.

---

### Orca Worktree 플러그인 — 이렇게 말하면 됩니다

Orca가 새 워크트리를 만들 때 실행할 **setup 명령**을 레포에 맞게 작성하고, **임시 워크트리에서 실제로 돌려본 뒤** 넘깁니다. git 워크트리에는 추적되는 파일만 따라오므로 `node_modules`·`.venv`·`.env`·`.claude/settings.local.json`·대용량 참조 자산은 빠진 채 생성되고, 그대로 두면 새 워크트리에서 첫 명령이 실패합니다.

| 상황 | 이렇게 말하세요 | 실행되는 것 |
|------|----------------|-------------|
| 설정 상태 점검 | "orca 설정 확인해줘" / `/orca-project-config` | 3축 점검(Orca 등록 · 레포 내 설정 · 레포 특성 대비 갭), 읽기 전용 |
| Orca 등록·base ref 설정 | `/orca-project-config --setup` | `repo add` · `repo set-base-ref` · 워크트리 base path 안내·적용 |
| setup 훅 작성 | "Orca setup 스크립트 만들어줘" / `/orca-setup-build` | 8단계(프로파일링→비추적 스캔→예산 배분→작성→정적 검사→드라이런) |
| archive 훅도 함께 | `/orca-setup-build --archive` | setup이 만든 심볼릭 링크 정리 훅 (`-L` 가드 필수) |
| 기존 훅만 돌려보기 | `/orca-setup-build --dry-run-only` | 임시 워크트리 실행 + 소요시간 + 멱등성 재실행 |
| 기존 훅 진단 | "orca.yaml 검토해줘" / `/orca-setup-review` | 6카테고리 30항목 → CRITICAL/MAJOR/MINOR/INFO |

```
"Add a setup command to run when Orca creates new worktrees"   ← /orca-setup-build
"새 워크트리 만들 때마다 install 하기 귀찮아"                    ← /orca-setup-build
"orca 훅이 앞부분만 실행되고 끝나"                               ← /orca-setup-review (set -e 함정)
"설정이 이 프로젝트에 맞는지 봐줘"                               ← /orca-project-config
```

**기본으로 회피하는 실측 함정**

| 함정 | 증상 | 대응 |
|---|---|---|
| Orca가 러너에 `set -e` 주입 | 훅이 앞부분만 실행되고 조용히 끝남 | 본문 첫머리 `set +e` |
| YAML 파싱 실패 = 훅 **전체 무시** | 에러 없이 "훅이 안 돈다" | 구조 검사 게이트 |
| 120초 타임아웃 | 워크트리 생성이 중단됨 | 빌드 제외 + 드라이런 실측 |
| `.gitignore`가 심볼릭 링크에 매칭 안 됨 | 워크트리마다 `?? old` 잡음 | `info/exclude` 등록 |
| archive에서 `-L` 없는 `rm` | **메인 체크아웃의 원본이 사라짐** | 링크 확인 후에만 해제 |
| 분리 스크립트 미커밋 | 새 워크트리마다 훅 실패 | 추적 여부 점검 |

> **작성과 검토는 분리된 스킬입니다** — `orca-setup-build`가 쓰고 `orca-setup-review`가 읽기 전용으로 검토합니다. 같은 컨텍스트에서 자기가 쓴 스크립트를 자기가 승인하면 검토가 형식이 됩니다.
>
> **`orca.yaml`이 인식하는 최상위 키는 넷뿐입니다** — `scripts` · `issueCommand` · `defaultTabs` · `environmentRecipes`. 그 밖의 키는 **에러 없이 조용히 무시**되므로 오타가 곧 기능 상실입니다.

---

### PRD Plan 플러그인 — 이렇게 말하면 됩니다

| 하고 싶은 것 | 이렇게 말하세요 | 실행되는 것 |
|-------------|----------------|------------|
| 환경 셋업(1회) | "prd-plan 셋업" / `/prd-setup` | 에이전트 2종 + CLAUDE.md + `docs/` 디렉토리 |
| PRD 작성 | "서보 모니터링 툴 PRD 써줘" / `/prd-write <주제>` | 인터뷰 → 작성 위임 → 검수 위임 → 반영 루프 → 승인 |
| 실행 계획 | "이 PRD로 계획 세워줘" / `/prd-plan docs/prd/PRD-x.md` | **착수 확인 게이트** → WBS·의존 그래프·마일스톤·리스크·커버리지 매트릭스 |
| 체크리스트 | "체크리스트 만들어줘" / `/prd-checklist docs/plan/PLAN-x.md` | **착수 확인 게이트** → TASK당 구현/검증 항목 + AC 확인 항목 + 추적성 검증 |
| 진척 확인 | "진척 어때?" / `/prd-checklist --status <경로>` | 완료·차단·다음 착수 후보 집계 |
| 요구 변경 반영 | "요구 바뀌었어" / `/prd-checklist --sync <경로>` | 영향 항목에 ⚠️ + 재검증 항목 추가 |
| 받은 문서 검수 | "이 기획서 봐줘" / `/prd-review <경로>` | 읽기 전용 등급 리포트 (수정 안 함) |

```
"PRD 써줘"                      ← /prd-write (인터뷰는 메인 세션, 작성/검수는 분리된 에이전트)
"WBS 뽑아줘"                    ← /prd-plan
"체크리스트 만들어줘"            ← /prd-checklist
"이 PRD로 개발 시작해도 될까?"   ← /prd-review (착수 가능 / 보완 필요 / 재작성 권고)
```

**PRD 프로파일** — 요구 항목이 스택마다 다릅니다.

| profile / stack | 추가 필수 항목 | 다음 단계 |
|-----------------|----------------|-----------|
| `software` / `frontend` | 화면 목록, UI 라이브러리(Fluent vs shadcn 택1), 실시간 갱신 방식, 브라우저·해상도, 접근성 | react-vite |
| `software` / `backend` | 언어·런타임(C++/C#/Python), 실행 형태, 인터페이스 계약, 동시성·지연, 자원·실시간성(GC), 오류·복구 | 구현 |
| `software` / `full-stack` | 위 둘 + **API 인터페이스 계약 섹션** | react-vite + 백엔드 |
| `hardware-firmware` | 기능 요구 · 인터페이스 목록 · 성능 사양 · 전원 요구 | **kicad-design에 그대로 투입 가능** |
| `research-PoC` | 가설 · 판정 기준 · 실험 요구 · **중단 기준** | rlcontrol(rl-assess) |

**이 플러그인이 막는 것**

| 흔한 실패 | 이 플러그인의 차단 장치 |
|-----------|------------------------|
| 작성자가 자기 문서를 스스로 승인 | 검수 에이전트는 **쓰기 권한 없음**, 대화가 아닌 **파일**을 읽고 판정 |
| "빠르게", "안정적으로" 같은 측정 불가 기준 | 금지어 자가 검열 + AC 없는 요구사항 작성 금지(스크립트 ERROR) |
| 지어낸 일정 "3월 2주차, 3인일" | 절대 날짜·시간 공수 생성 금지, 상대 규모 S/M/L/XL만 |
| 모르는 값을 그럴싸하게 채움 | `(미정 — OPEN-###)` 미결 이슈로 강제 |
| "했다고 치는" 완료 | 완료 표시에 **근거 칸 필수** — 비면 exit 1 |
| 요구사항이 구현에서 누락 | MUST 요구 미커버 시 ERROR (`REQ → TASK → CHK` 기계 검증) |
| 미결이 남은 채 다음 단계로 떠밀림 | PLAN·체크리스트는 **착수 확인 게이트**로 시작 — 단계 전이는 사용자가 결정 |

> **OMC의 `plan`/`planner`와 다릅니다** — OMC는 세션 내 작업 계획(휘발성), 이쪽은 **저장되는 문서 + 검수 게이트 + 추적성**입니다. 체크리스트를 만든 뒤 실제 실행은 `parallel-delegation`이나 OMC에 넘기면 됩니다.

---

#### 펌웨어 생성 시 Claude가 물어보는 것들

정보가 부족하면 Claude가 순서대로 질문합니다:

1. **MCU** — "어떤 STM32F4 칩을 사용하시나요?" (미지정 시 자동 추천)
2. **HSE 주파수** — "외부 크리스탈이 몇 MHz인가요?" (기본: 8MHz)
3. **외부 IC** — "연결할 IC의 정확한 모델명은?" (필수 질문)
4. **핀 제약** — "사용할 수 없는 핀이 있나요?" (기본: 없음)
5. **전원 전압** — "3.3V인가요?" (기본: 3.3V)
6. **빌드 시스템** — "CMake? Makefile?" (기본: CMake)
7. **디버그 프로브** — "ST-Link v2? v3? J-Link?" (기본: ST-Link v2)

전부 답하지 않아도 됩니다. 미답변 항목은 기본값을 사용하고, 기본값 사용 사실을 명시합니다.

---

## 리뷰 결과 읽는 법

Vivado와 STM32F4 모두 동일한 3단계 등급을 사용합니다:

| 등급 | 의미 | 조치 |
|------|------|------|
| **ERROR** | 반드시 수정해야 함. 동작 불가 또는 하드웨어 손상 위험 | "FAIL 항목 수정해줘" |
| **WARN** | 동작은 하지만 잠재적 문제. 권장 수정 | 지금 안 고쳐도 됨 |
| **OK** / **PASS** | 이상 없음 | 다음 단계로 진행 |

리뷰에서 ERROR가 나오면:

```
사용자: "FAIL 항목 전부 수정해줘"
(수정 후)
사용자: "다시 리뷰해줘"
(FAIL=0이 될 때까지 반복)
```

---

## 지원하는 MCU / FPGA

### STM32F4 시리즈

| MCU | 최대 클럭 | Flash | 특징 |
|-----|----------|-------|------|
| F401 | 84MHz | 256KB | 최저가, USB, SPI4 |
| F411 | 100MHz | 512KB | 저가+USB, SPI3/4/5, SDIO |
| F407 | 168MHz | 1MB | 기준 MCU, CAN, ETH, DAC |
| F429 | 168MHz | 2MB | LCD(LTDC), FMC, Dual Bank Flash |
| F446 | 180MHz | 512KB | 최고 클럭, QUADSPI, SAI, FMPI2C |

각 MCU별로 **공식 데이터시트 기반 AF 매핑 JSON**이 포함되어 있어, 핀 검증 시 타겟 MCU에 맞는 정확한 검증이 이루어집니다.

### Vivado FPGA

boards.json에 등록된 보드를 지원합니다 (Arty A7, ZedBoard 등). 보드 추가도 가능합니다.

---

## 폴더 구조

```
pjy-claude-skill/
├── .claude-plugin/
│   └── marketplace.json           ← 마켓플레이스 카탈로그
├── plugins/
│   ├── vivado/                    ← Vivado FPGA 플러그인
│   │   ├── plugin.json
│   │   ├── skills/ (13개)         ← 스킬 (SKILL.md + 보조 파일)
│   │   ├── agents/ (6개)          ← 에이전트 (.md)
│   │   ├── claude-md/             ← 프로젝트 CLAUDE.md 템플릿
│   │   ├── templates/             ← 예제 RTL/TB/XDC
│   │   └── docs/                  ← 사용 가이드
│   ├── stm32f4/                   ← STM32F4 MCU 플러그인
│   │   ├── plugin.json
│   │   ├── skills/ (5개)
│   │   │   ├── stm32f4-firmware/  ← 5단계 파이프라인
│   │   │   │   ├── references/    ← 7개 참조 문서
│   │   │   │   ├── references/af-tables/  ← 5개 MCU AF 매핑 JSON
│   │   │   │   └── assets/templates/      ← 8개 빌드 템플릿
│   │   │   ├── kicad-stm32-review/        ← 회로도 검증 (42항목)
│   │   │   ├── stm32f4-tdd/              ← TDD (Unity+FFF)
│   │   │   ├── stm32f4-build/            ← 빌드 실행 (CMake+Ninja)
│   │   │   └── stm32f4-setup/            ← 환경 설정
│   │   ├── agents/ (4개)          ← checker, test-writer, code-reviewer, qa
│   │   ├── claude-md/
│   │   └── docs/
│   ├── wmx3md/                    ← WMX3 Motion Module 플러그인
│   │   ├── plugin.json
│   │   ├── skills/ (8개)          ← 모듈 생성, 빌드, API 추가, TDD, 리뷰, 문서, 배포
│   │   │   └── wmx3-module-create/
│   │   │       ├── assets/templates/  ← 3-layer 코드 템플릿
│   │   │       └── references/        ← 설계 가이드 (상태 머신, IPC, 네이밍 등)
│   │   ├── agents/ (6개)          ← designer, generator, build-checker, test-writer, code-reviewer, doc-writer
│   │   ├── claude-md/
│   │   └── docs/
│   ├── wmx3app/                   ← WMX3.7 애플리케이션 개발 플러그인
│   │   ├── plugin.json
│   │   ├── skills/ (7개)          ← 시스템 설계, C++/C# 구현, 테스트, 사용 검토, ENI 제작, Config Export 분석, 환경 설정
│   │   │   ├── wmx3-app-design/
│   │   │   │   └── references/    ← 아키텍처 코어, 플랫폼 선택, 모션 기능 매핑, 성능/안정성, 로봇 옵션
│   │   │   ├── wmx3-app-implement/
│   │   │   │   └── references/    ← C++/C# 구현, 에러 처리, v3.7 마이그레이션
│   │   │   ├── wmx3-app-test/
│   │   │   │   └── references/    ← 시뮬레이터 플랫폼, 테스트 전략
│   │   │   ├── wmx3-app-review/
│   │   │   │   └── references/    ← 사용 검토 체크리스트 (7카테고리)
│   │   │   ├── wmx3-app-eni/
│   │   │   │   └── references/    ← eni-file-guide (WMX3 전용 ENI·ec_network.def·ESI 분석·PDO/CANopen 매핑)
│   │   │   ├── wmx3-app-config-xml-analy/
│   │   │   │   ├── references/    ← config-export-format(필드 사전), config-analysis-checklist(A~G 검토)
│   │   │   │   └── assets/        ← parse_wmx_config.py (설정 축 식별·요약·자동 플래그·CSV)
│   │   │   └── wmx3-app-setup/
│   │   ├── agents/ (5개)          ← architect, implementer, test-engineer, usage-reviewer, eni-builder
│   │   ├── claude-md/
│   │   └── docs/USAGE_GUIDE.md
│   ├── manual/                    ← Sphinx 문서화 플러그인
│   │   ├── plugin.json
│   │   ├── skills/ (4개)          ← 문서 생성, 빌드, 리뷰, 환경 설정
│   │   │   └── manual-write/
│   │   │       └── references/    ← 다국어 네비게이션 템플릿
│   │   ├── agents/ (4개)          ← sphinx-manual-writer, manual-writer, windows-manual-writer, manual-reviewer
│   │   ├── claude-md/
│   │   └── docs/
│   ├── kicad/                     ← KiCad 회로도 플러그인
│   │   ├── plugin.json
│   │   ├── skills/ (5개)          ← 회로도 설계, 리뷰+BOM, 회로/PCB 분석, KiCad 사용법, 환경 설정
│   │   │   ├── kicad-design/      ← PRD → 회로도 생성
│   │   │   │   └── references/    ← S-expression 포맷 + .kicad_pro 가이드
│   │   │   ├── kicad-review/      ← 8단계 리뷰 + BOM 생성
│   │   │   │   └── references/    ← 체크리스트, 파싱, 데이터시트, Ethernet 프런트엔드
│   │   │   ├── kicad-analyze/     ← 회로/PCB 정밀 분석 (ERC/DRC, 넷 추적, SI/PI)
│   │   │   │   └── references/    ← Seeed MCP 도구 매핑, PCB 분석·SI/PI 가이드
│   │   │   ├── kicad-usage/       ← KiCad 10.0 사용법 안내 (공식 매뉴얼 다이제스트)
│   │   │   │   └── references/    ← kicad-project / pcbnew(6) / gerbview / kicad-cli 다이제스트 + INDEX
│   │   │   └── kicad-setup/
│   │   ├── agents/ (4개)          ← designer, reviewer, bom-generator, pcb-analyzer
│   │   ├── claude-md/
│   │   └── docs/
│   ├── parallel-delegation/       ← 서브에이전트 병렬 위임 플러그인 (메타 도구)
│   │   ├── plugin.json
│   │   ├── skills/ (2개)           ← 병렬 위임 워크플로 + 3-role 에이전트 셋업
│   │   ├── agents/ (3개)           ← pd-implementer, pd-tester, pd-verifier
│   │   └── docs/usage-guide.md
│   ├── harness/                   ← Claude Code 하네스 진화 플러그인 (메타 도구)
│   │   ├── plugin.json
│   │   ├── skills/
│   │   │   └── harness-design/    ← 6단계 진단·진화 메인 스킬 (Phase 0 + Phase 1~6)
│   │   │       ├── references/    ← 6개 단계별 가이드 (CLAUDE.md, Permissions, Hooks, MCP, Subagent, 진화)
│   │   │       └── evals/         ← 평가 케이스 (4 시나리오) + weak-harness 픽스처
│   │   └── docs/usage-guide.md    ← 사용 가이드 (모드별 흐름, 시나리오 예제, 함정)
│   ├── manual-digest/             ← 대용량 매뉴얼 다이제스트 플러그인 (메타 도구)
│   │   ├── plugin.json
│   │   ├── skills/ (2개)          ← 인제스트/갱신/목록/삭제 + 환경 1회 초기화
│   │   │   ├── manual-digest/
│   │   │   │   └── references/    ← 7개 포맷별 추출 가이드 (PDF/HTML/EPUB/DOCX/CHM/TXT-MD/codebase)
│   │   │   └── manual-digest-setup/
│   │   └── docs/USAGE_GUIDE.md    ← 사용 가이드 (빠른 시작, 명령어, scope, 트러블슈팅)
│   ├── pcb-design-digest/         ← PCB 설계 다이제스트 플러그인 (거버/PADS/KiCad, 메타 도구)
│   │   ├── plugin.json
│   │   ├── skills/ (2개)          ← 인제스트/갱신/목록/삭제 + 환경 1회 초기화(에이전트 설치)
│   │   │   ├── pcb-design-digest/
│   │   │   │   └── references/    ← 산출물 스키마(pcb-design-digest-format) + 추출 절차(gerber-extract/pads-extract/kicad-extract)
│   │   │   └── pcb-design-digest-setup/
│   │   ├── agents/ (1개)          ← pcb-design-analyst (깊은 PCB 분석 + 보드별 메모리)
│   │   └── docs/USAGE_GUIDE.md    ← 사용 가이드 (빠른 시작, 명령어, 지원 입력, 파싱 함정)
│   ├── rlcontrol/                 ← 강화학습(RL) 제어 적용 플러그인 (도메인)
│   │   ├── plugin.json
│   │   ├── skills/ (6개)          ← 적용 검토(게이트)·알고리즘 설계·구현·테스트·지속 개선 + 환경 설정
│   │   │   ├── rl-assess/         ← RL 적용 가능성 검토 (MDP 정식화·고전 제어 대비·Go/No-Go)
│   │   │   │   └── references/    ← mdp-formulation / feasibility-checklist / rl-vs-classical
│   │   │   ├── rl-design/         ← 알고리즘 선정 + 환경/보상/안전 설계
│   │   │   │   └── references/    ← algorithm-catalog / algorithm-selection / reward-and-safety
│   │   │   ├── rl-implement/      ← Gymnasium 환경(5-튜플)·SB3/CleanRL 학습·ONNX 배포
│   │   │   │   └── references/    ← environment-design / framework-guide / training-and-deployment / cross-language-deployment
│   │   │   ├── rl-test/           ← 다중 시드 성능·기능·안전 테스트 (sim-to-real)
│   │   │   │   └── references/    ← evaluation-protocol / functional-safety-tests
│   │   │   ├── rl-improve/        ← 운영 데이터 지속 개선 (오프라인 재학습·champion/challenger·재배포 게이트)
│   │   │   │   └── references/    ← continual-learning
│   │   │   └── rl-setup/
│   │   ├── agents/ (4개)          ← rlctrl-feasibility-analyst/algorithm-designer/implementer/evaluator
│   │   ├── claude-md/
│   │   └── docs/USAGE_GUIDE.md
│   ├── doc-atomize/               ← 마크다운 무손실 원자 분할 플러그인 (메타 도구)
│   │   ├── plugin.json
│   │   ├── skills/ (2개)          ← 분할/갱신/검증/목록/삭제 + 환경 1회 초기화
│   │   │   ├── doc-atomize/
│   │   │   │   ├── references/    ← split-rules(경계·병합·엣지케이스) / index-format(스키마) / retrieval-guide(조회 프로토콜)
│   │   │   │   └── assets/        ← split_md.py (split·verify·reindex·update, 표준 라이브러리만)
│   │   │   └── doc-atomize-setup/
│   │   ├── hooks/                 ← hooks.json + sync_atomized.py (원본 수정 시 자동 재분할)
│   │   └── docs/USAGE_GUIDE.md    ← 사용 가이드 (5분 사용법, 실측 절감, 옵션 튜닝, FAQ)
│   ├── orca-worktree/             ← Orca 워크트리 setup 훅 플러그인 (메타 도구, 에이전트 0)
│   │   ├── plugin.json
│   │   ├── skills/ (3개)          ← 훅 작성 + 프로젝트 설정/점검 + 훅 진단
│   │   │   ├── orca-setup-build/
│   │   │   │   ├── references/    ← orca-yaml-schema(키·훅·env·타임아웃) / repo-profiling(생태계별 단계·비용) / script-conventions(관용구·안티패턴)
│   │   │   │   └── assets/        ← check_orca_yaml.py(구조+안티패턴+bash -n) / dryrun_setup.sh(임시 워크트리 실행) / templates/
│   │   │   ├── orca-project-config/
│   │   │   │   ├── references/    ← project-setup-guide (설정 체크리스트·셀렉터·원격 호스트)
│   │   │   │   └── assets/        ← check_orca_project.sh (3축 점검, 읽기 전용)
│   │   │   └── orca-setup-review/
│   │   │       └── references/    ← review-checklist (6카테고리 30항목 + 등급 기준)
│   │   └── docs/USAGE_GUIDE.md    ← 사용 가이드 (함정 목록, 시작하기 4단계, 트러블슈팅)
│   ├── prd-plan/                  ← PRD → 계획 → 체크리스트 플러그인 (워크플로, 에이전트 2)
│   │   ├── plugin.json
│   │   ├── claude-md/CLAUDE.md    ← 문서 경로·ID 규약·절대 규칙·프로파일·라우팅표
│   │   ├── agents/ (2개)          ← prd-writer(30년 PM, 작성) / prd-reviewer(PMO 심사, 쓰기 권한 없음)
│   │   ├── skills/ (5개)
│   │   │   ├── prd-write/         ← 인터뷰(메인 세션) → 작성 → 검수 루프 → 승인
│   │   │   │   └── references/    ← prd-template-core(12섹션·REQ/AC 규격) / prd-profiles(software[frontend·backend·full-stack]·hardware-firmware·research-PoC) / interview-guide / quality-rubric(7카테고리·4등급·검수 경계) / large-doc-handling(doc-atomize 타이밍)
│   │   │   ├── prd-plan/          ← PRD → WBS·의존·마일스톤·리스크
│   │   │   │   └── references/    ← wbs-guide(TASK 규격·분해 원칙·커버리지 매트릭스) / estimation-policy(절대 날짜·시간 공수 금지)
│   │   │   ├── prd-checklist/     ← 체크리스트 생성 + --status(진척) + --sync(변경 동기화)
│   │   │   │   ├── references/    ← checklist-format (CHK 한 줄 규격·주체·완료 근거 칸)
│   │   │   │   └── assets/        ← check_traceability.py (REQ↔TASK↔CHK 검증, 표준 라이브러리만, exit code 게이트)
│   │   │   ├── prd-review/        ← 외부·기존 문서 검수만 (읽기 전용)
│   │   │   │   └── references/    ← review-checklist (형식 차이 처리·착수 가능성 5항 판정)
│   │   │   └── prd-setup/         ← 에이전트 2종 + CLAUDE.md + docs/ 디렉토리 설치
│   │   └── docs/USAGE_GUIDE.md    ← 사용 가이드 (OMC plan과의 차이, 흐름, 검증 코드표, FAQ)
│   └── react-vite/                ← React 19 + Vite 8 프론트엔드 플러그인
│       ├── plugin.json
│       ├── skills/ (2개)          ← 구현→검증 워크플로 + 에이전트 셋업
│       │   ├── react-vite-frontend/
│       │   │   └── references/    ← UI 라이브러리 가이드 (Fluent UI v9 / shadcn/ui)
│       │   └── react-vite-setup/
│       ├── agents/ (6개)          ← 범용 program/qa-expert + Fluent·shadcn 라이브러리별 구현·QA specialist
│       ├── claude-md/
│       └── docs/usage-guide.md
├── CLAUDE.md
├── README.md
└── .gitignore
```

---

## 자주 묻는 질문

### Q: 스킬을 하나만 설치할 수 있나요?

마켓플레이스 단위로 설치됩니다. `vivado` 플러그인을 설치하면 13개 스킬이 모두 활성화됩니다. 개별 스킬만 설치하는 것은 지원하지 않지만, 사용하지 않는 스킬은 트리거되지 않으므로 문제없습니다.

### Q: 여러 플러그인을 동시에 설치해도 되나요?

네. 각 플러그인은 완전히 독립적입니다.

### Q: 스킬/에이전트를 수정할 수 있나요?

네. 설치 후 `.claude/skills/` 또는 `.claude/agents/` 디렉토리의 마크다운 파일을 직접 편집하면 됩니다. 예를 들어 체크리스트에 프로젝트 특화 항목을 추가할 수 있습니다.

### Q: 셋업 시 프로젝트 경로를 물어보는 이유는?

각 플러그인의 `*-setup` 스킬은 에이전트, CLAUDE.md, 디렉토리 구조를 생성합니다. 현재 디렉토리가 아닌 다른 경로에 설치하고 싶을 수 있으므로, 셋업 시 경로를 질문합니다. 엔터만 누르면 현재 디렉토리에 설치됩니다.

### Q: 업데이트는 어떻게 하나요?

```
/install github:pjy4617/pjy-claude-skill
```

재설치가 곧 업데이트입니다. 최신 스킬이 자동으로 반영됩니다.

### Q: Windows에서도 사용할 수 있나요?

WSL2 환경에서 사용할 수 있습니다. 네이티브 Windows는 Vivado CLI와 arm-none-eabi-gcc의 경로 설정이 필요합니다.

### Q: KiCad가 없어도 되나요?

네. KiCad 관련 스킬은 `kicad-cli` 없이도 동작합니다. 다만 PDF 시각적 검토, 넷리스트 정확도, 생성 파일 검증이 제한됩니다. `kicad-cli`가 있으면 최적의 결과를 얻을 수 있습니다.

### Q: KiCad 플러그인으로 생성한 회로도를 바로 사용할 수 있나요?

KiCad 9.x에서 바로 열 수 있습니다. 다만 S-expression 직접 생성의 특성상 와이어-핀 좌표가 완벽하지 않을 수 있어, KiCad GUI에서 ERC 실행 후 와이어 보정(5~15분)이 필요합니다. 부품 선정, 회로 구조, 네트 정의는 완성된 상태입니다.

---

## 상세 가이드

각 플러그인의 상세 사용법은 아래 문서를 참고하세요:

- **Vivado**: [`plugins/vivado/docs/Vivado-스킬-에이전트-사용가이드.md`](plugins/vivado/docs/Vivado-스킬-에이전트-사용가이드.md)
- **STM32F4**: [`plugins/stm32f4/docs/USAGE_GUIDE.md`](plugins/stm32f4/docs/USAGE_GUIDE.md)
- **WMX3 Motion Module**: [`plugins/wmx3md/docs/USAGE_GUIDE.md`](plugins/wmx3md/docs/USAGE_GUIDE.md)
- **WMX3 Application**: [`plugins/wmx3app/docs/USAGE_GUIDE.md`](plugins/wmx3app/docs/USAGE_GUIDE.md)
- **Sphinx Manual**: [`plugins/manual/docs/USAGE_GUIDE.md`](plugins/manual/docs/USAGE_GUIDE.md)
- **KiCad**: [`plugins/kicad/docs/usage-guide.md`](plugins/kicad/docs/usage-guide.md)
- **Parallel Delegation**: [`plugins/parallel-delegation/docs/usage-guide.md`](plugins/parallel-delegation/docs/usage-guide.md)
- **Claude Code Harness**: [`plugins/harness/docs/usage-guide.md`](plugins/harness/docs/usage-guide.md)
- **Manual Digest**: [`plugins/manual-digest/docs/USAGE_GUIDE.md`](plugins/manual-digest/docs/USAGE_GUIDE.md)
- **React-Vite Frontend**: [`plugins/react-vite/docs/usage-guide.md`](plugins/react-vite/docs/usage-guide.md)
- **PCB Design Digest**: [`plugins/pcb-design-digest/docs/USAGE_GUIDE.md`](plugins/pcb-design-digest/docs/USAGE_GUIDE.md)
- **RL Control**: [`plugins/rlcontrol/docs/USAGE_GUIDE.md`](plugins/rlcontrol/docs/USAGE_GUIDE.md)
- **Doc Atomize**: [`plugins/doc-atomize/docs/USAGE_GUIDE.md`](plugins/doc-atomize/docs/USAGE_GUIDE.md)
- **Orca Worktree**: [`plugins/orca-worktree/docs/USAGE_GUIDE.md`](plugins/orca-worktree/docs/USAGE_GUIDE.md)
- **PRD Plan**: [`plugins/prd-plan/docs/USAGE_GUIDE.md`](plugins/prd-plan/docs/USAGE_GUIDE.md)

---

## 라이선스

MIT License
