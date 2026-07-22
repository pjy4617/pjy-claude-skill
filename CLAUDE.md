# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

Claude Code 플러그인 마켓플레이스 서버. 하드웨어 개발 도메인(FPGA, MCU) 스킬과 에이전트를 GitHub 기반으로 배포한다.

마켓플레이스 이름: `pjy-skills`

## 체크항목
- 기능이 변경되거나 추가시 반드시 marketplace.json과 plugin.json이 업데이트되어야 합니다.
- **버전 업 필수**: 플러그인의 소스(스킬/에이전트/참조/템플릿/설명)가 변경되면 해당 `plugin.json`과 `marketplace.json`의 `version`을 **항상 함께 올린다** (두 곳 값 일치 필수). 마켓플레이스 `version`이 사용자 설치 버전보다 높아야 `/plugin` 업데이트로 감지되기 때문. SemVer 적용: 버그 수정/문서 보강 → patch, 기능 추가(하위호환) → minor, 호환 깨짐 → major.
- 플러그인을 신규 추가/이름 변경/제거할 때는 README.md(플러그인 카드·설치 섹션·폴더 구조·상세 가이드 링크)와 CLAUDE.md 아키텍처 트리도 함께 갱신.


## 아키텍처

```
.claude-plugin/marketplace.json    ← 마켓플레이스 진입점 (플러그인 목록)
assets/                            ← 마스코트 이미지 등 공용 에셋
plugins/
├── vivado/                        ← Vivado FPGA 플러그인 (13 스킬 + 6 에이전트)
│   ├── plugin.json
│   ├── skills/                    ← SKILL.md + 보조 파일 (TCL, JSON 등)
│   ├── agents/                    ← 에이전트 .md (setup 스킬이 .claude/agents/로 복사)
│   ├── claude-md/CLAUDE.md        ← 타겟 프로젝트용 CLAUDE.md 템플릿
│   ├── templates/                 ← 예제 RTL/TB/XDC/스크립트
│   └── docs/                      ← 사용 가이드
├── stm32f4/                       ← STM32F4 MCU 플러그인 (5 스킬 + 4 에이전트)
│   ├── plugin.json
│   ├── skills/
│   │   └── stm32f4-firmware/
│   │       ├── references/        ← 코딩 규칙, 페리페럴 패턴, 핀 검증 등
│   │       ├── references/af-tables/*.json  ← MCU별 AF 매핑 데이터 (F401/F407/F411/F429/F446)
│   │       └── assets/templates/  ← CMake, Makefile, 링커, OpenOCD, VS Code 템플릿
│   ├── agents/
│   ├── claude-md/CLAUDE.md
│   └── docs/
├── wmx3md/                        ← WMX3 모션 제어 모듈 플러그인 (8 스킬 + 6 에이전트)
│   ├── plugin.json
│   ├── skills/
│   │   └── wmx3-module-create/
│   │       ├── references/        ← 모듈 인터페이스, 빌드, IPC, 네이밍 등 11개 참조 문서
│   │       └── assets/templates/  ← 3-layer 모듈 스캐폴딩 템플릿 (C99 Core + C++ API + gtest)
│   ├── agents/
│   ├── claude-md/CLAUDE.md
│   └── docs/
├── wmx3app/                       ← WMX3.7 애플리케이션 개발 플러그인 (6 스킬 + 5 에이전트) — wmx3md(엔진 내부 모듈 rtdll)와 달리 WMX3 API를 호출하는 응용 프로그램 개발. Robot Option 다관절 로봇 제어(PTP/CP·충돌 감지)·EtherCAT ENI 파일 제작·ESI 분석 포함
│   ├── plugin.json
│   ├── skills/
│   │   ├── wmx3-app-design/       ← 요구사항 → 시스템 설계 (플랫폼 선택·축 구성·모션 기능 매핑·성능/안정성)
│   │   │   └── references/        ← architecture-core, platform-selection, motion-function-map, performance-stability, robot-option
│   │   ├── wmx3-app-implement/    ← C++/C# 구현 (초기화 시퀀스·에러 처리·3.6u3→3.7 마이그레이션)
│   │   │   └── references/        ← cpp-implementation, csharp-implementation, error-handling, v37-migration
│   │   ├── wmx3-app-test/         ← 시뮬레이터 플랫폼(SimuPlatform) 기반 테스트
│   │   │   └── references/        ← simulator-platform, test-strategy
│   │   ├── wmx3-app-review/       ← 기존 프로젝트 WMX3 사용 검토 (7카테고리 체크리스트)
│   │   │   └── references/        ← usage-review-checklist
│   │   ├── wmx3-app-eni/          ← EtherCAT ENI 파일 제작 (WMX3 전용 ENI·ec_network.def·슬레이브 ESI 분석·PDO/CANopen 매핑)
│   │   │   └── references/        ← eni-file-guide
│   │   └── wmx3-app-setup/        ← 에이전트 5종 + CLAUDE.md 설치
│   ├── agents/                    ← wmx3app-architect/implementer/test-engineer/usage-reviewer/eni-builder
│   ├── claude-md/CLAUDE.md
│   └── docs/
├── kicad/                         ← KiCad 회로도 플러그인 (5 스킬 + 4 에이전트)
│   ├── plugin.json
│   ├── skills/
│   │   ├── kicad-design/          ← PRD/설계사양서 → 회로도 생성
│   │   │   └── references/        ← S-expression 포맷 가이드
│   │   ├── kicad-review/          ← 8단계 회로도 설계 리뷰 + BOM 생성
│   │   │   └── references/        ← 체크리스트, 파싱 가이드, 데이터시트 검색
│   │   ├── kicad-analyze/         ← 회로(넷리스트)/PCB 정밀 분석 (ERC/DRC, 넷 추적, 트랙, SI/PI)
│   │   │   └── references/        ← Seeed MCP 도구 매핑·폴백, PCB 분석·SI/PI 가이드
│   │   ├── kicad-usage/           ← KiCad 10.0 *사용법* 안내 (공식 매뉴얼 다이제스트, How-to Q&A)
│   │   │   └── references/        ← INDEX + kicad-project / pcbnew-1~6 / gerbview / kicad-cli 다이제스트 (docs.kicad.org 10.0 HTML→한국어 요약)
│   │   └── kicad-setup/           ← 에이전트 설치 (--with-mcp로 Seeed MCP 등록 안내)
│   ├── agents/                    ← schematic-designer/reviewer/bom-generator/pcb-analyzer
│   ├── claude-md/CLAUDE.md
│   └── docs/
├── parallel-delegation/           ← 워크플로 플러그인 (2 스킬 + 3 에이전트, 도메인 없음)
│   ├── plugin.json
│   ├── skills/
│   │   ├── parallel-delegation/      ← 8단계 병렬 위임 절차
│   │   └── parallel-delegation-setup/ ← 3-role 누락분만 보충 설치
│   ├── agents/                       ← pd-implementer / pd-tester / pd-verifier
│   └── docs/
├── manual/                        ← Sphinx 문서화 플러그인 (4 스킬 + 4 에이전트)
│   ├── plugin.json
│   ├── skills/
│   │   └── manual-write/
│   │       └── references/        ← 다국어 네비게이션 템플릿 등
│   ├── agents/
│   ├── claude-md/CLAUDE.md
│   └── docs/
├── harness/                       ← 하네스 진화 플러그인 (2 스킬, 에이전트 없음, 메타 도구)
│   ├── plugin.json
│   ├── skills/
│   │   ├── harness-design/        ← CLAUDE.md/Permissions/Hooks/MCP/Subagent 6단계 진단·보강
│   │   └── harness-design-workspace/
│   └── (claude-md 없음 / setup 없음 — 현재 디렉토리 진단)
├── manual-digest/                 ← 대용량 매뉴얼 다이제스트 플러그인 (2 스킬, 에이전트 없음)
│   ├── plugin.json
│   ├── skills/
│   │   ├── manual-digest/         ← 인제스트/갱신/목록/삭제 (8단계 워크플로, 문서+codebase)
│   │   │   └── references/        ← 포맷별 추출 가이드 (PDF/HTML/EPUB/DOCX/CHM/TXT-MD/codebase)
│   │   └── manual-digest-setup/   ← MCP 등록 + 디렉토리 + CLAUDE.md 마커 1회 초기화
│   └── docs/USAGE_GUIDE.md
├── pcb-design-digest/             ← PCB 설계/제조 데이터 다이제스트 플러그인 (2 스킬 + 1 에이전트, 메타 도구) — 거버 팹출력 + PADS(.pcb/.asc) + KiCad(.kicad_pcb/.kicad_sch/.kicad_pro)
│   ├── plugin.json
│   ├── skills/
│   │   ├── pcb-design-digest/     ← 인제스트/갱신/목록/삭제 (8단계, 거버·PADS·KiCad 입력)
│   │   │   └── references/        ← pcb-design-digest-format.md(산출물 스키마) + gerber-extract.md/pads-extract.md/kicad-extract.md(입력군별 추출 절차)
│   │   └── pcb-design-digest-setup/ ← 에이전트 설치 + 디렉토리 + CLAUDE.md 마커 1회 초기화 (MCP 불필요)
│   ├── agents/                    ← pcb-design-analyst (깊은 PCB 분석 + 보드별 메모리 누적)
│   └── docs/USAGE_GUIDE.md
├── rlcontrol/                     ← 강화학습(RL) 제어 적용 플러그인 (5 스킬 + 4 에이전트, 도메인) — RL 적용 가능성 게이트(고전 제어 우선 판별)·알고리즘 설계·구현·성능/안전 테스트. 안전-크리티컬 전제(무제약 정책 실기 직배포 금지·시뮬레이터 우선)
│   ├── plugin.json
│   ├── skills/
│   │   ├── rl-assess/             ← RL 적용 가능성 검토 (게이트: MDP 정식화·고전 제어(PID/LQR/MPC) 대비·Go/No-Go 판정)
│   │   │   └── references/        ← mdp-formulation, feasibility-checklist, rl-vs-classical
│   │   ├── rl-design/             ← 알고리즘 검토·선정 + 환경/보상/안전 설계
│   │   │   └── references/        ← algorithm-catalog, algorithm-selection, reward-and-safety
│   │   ├── rl-implement/          ← Gymnasium 환경(5-튜플)·SB3/CleanRL 학습·ONNX 내보내기 + C#/C++ 구동 프로그램 추론 배포(정규화 패리티·구동측 안전 계층)
│   │   │   └── references/        ← environment-design, framework-guide, training-and-deployment, cross-language-deployment
│   │   ├── rl-test/               ← 성능·기능·안전 테스트 (다중 시드 통계·제약 위반율·sim-to-real)
│   │   │   └── references/        ← evaluation-protocol, functional-safety-tests
│   │   └── rl-setup/              ← 에이전트 4종 + CLAUDE.md 설치
│   ├── agents/                    ← rlctrl-feasibility-analyst/algorithm-designer/implementer/evaluator
│   ├── claude-md/CLAUDE.md
│   └── docs/USAGE_GUIDE.md
└── react-vite/                    ← React 19 + Vite 8 프론트엔드 플러그인 (2 스킬 + 6 에이전트)
    ├── plugin.json
    ├── skills/
    │   ├── react-vite-frontend/   ← 구현→검증 역할분리 워크플로 (범용+UI specialist 라우팅)
    │   │   └── references/        ← UI 라이브러리 가이드 (ui-fluent-ui.md / ui-shadcn-ui.md)
    │   └── react-vite-setup/      ← 에이전트 6종 + CLAUDE.md 설치
    ├── agents/                    ← 범용 program/qa-expert + Fluent·shadcn 라이브러리별 구현·QA specialist (6)
    ├── claude-md/CLAUDE.md
    └── docs/usage-guide.md
```

핵심 구조: 각 플러그인은 `plugin.json` + `skills/` 디렉토리를 가지며, `marketplace.json`이 이를 카탈로그로 등록한다. 에이전트는 마켓플레이스가 직접 지원하지 않으므로, `*-setup` 스킬이 사용자에게 프로젝트 경로를 질문한 뒤 해당 경로의 `.claude/agents/`로 복사하는 메커니즘을 사용한다.

## 스킬 파일 규칙

- 각 스킬은 `skills/<스킬명>/SKILL.md`에 YAML 프론트매터 + 마크다운 본문으로 구성
- 프론트매터 필수 필드: `name`, `description`, `user-invocable: true`, `allowed-tools`
- 에이전트는 `agents/<에이전트명>.md`에 프론트매터(`name`, `description`, `tools`, `model`) + 본문
- 모든 에이전트 모델은 `opus` 사용
- 보조 파일(JSON, TCL, Python 등)은 같은 스킬 디렉토리에 배치
- 템플릿 파일의 플레이스홀더: `{{PLACEHOLDER}}` 형식 통일 (Mustache 스타일 금지)

## 검증

> Windows에서는 `python3`/`python`이 MS Store alias로 잡혀 exit 49로 실패할 수 있다.
> PowerShell 대안: `Get-Content '.claude-plugin/marketplace.json' -Raw | ConvertFrom-Json | Out-Null`

```bash
# marketplace.json JSON 유효성
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"

# 모든 plugin.json 유효성
find plugins -name "plugin.json" -exec python3 -c "import json; json.load(open('{}')); print('OK: {}')" \;

# af-tables JSON 유효성
for f in plugins/stm32f4/skills/stm32f4-firmware/references/af-tables/*.json; do
  python3 -c "import json; json.load(open('$f')); print('OK: $(basename $f)')"
done

# 스킬/에이전트 상호 참조 검증 (잘못된 참조 탐지)
grep -r "wmx3-module-scaffold\|plugins/wmx3/" plugins/wmx3md/ && echo "FAIL: 잘못된 참조 발견" || echo "OK: 상호 참조 정상"
```

## 새 플러그인 추가 절차

플러그인 종류:
- **도메인 플러그인**(vivado/stm32f4/kicad/manual/wmx3md/wmx3app/rlcontrol): 특정 기술 도메인 작업. `claude-md/` 템플릿 + `*-setup`이 모든 에이전트 복사
- **워크플로 플러그인**(parallel-delegation): 도메인 무관 절차. `claude-md/` 없음 + `*-setup`이 누락분만 보충
- **메타 도구 플러그인**(harness/manual-digest/pcb-design-digest): Claude Code 자체 환경 또는 컨텍스트 관리 도구. `claude-md/` 없음, 에이전트도 0~필요 최소. `harness`는 setup 없음(현재 디렉토리 진단), `manual-digest`는 1회 환경 초기화용 setup만, `pcb-design-digest`는 거버 팹출력뿐 아니라 PADS(.pcb/.asc)·KiCad(.kicad_pcb/.kicad_sch/.kicad_pro)까지 인제스트하며 에이전트 1개(pcb-design-analyst) + 그것을 `.claude/agents/`로 설치하는 setup(MCP 불필요).

1. `plugins/<이름>/plugin.json` 생성 (`name`, `version`, `description`, `skills` 필드)
2. `plugins/<이름>/skills/<스킬명>/SKILL.md` 생성
3. `.claude-plugin/marketplace.json`의 `plugins` 배열에 항목 추가 (`name`, `source`, `description`, `version`)
4. 에이전트가 있으면 `plugins/<이름>/agents/` + `*-setup` 스킬 추가
5. 도메인 플러그인이면 `claude-md/CLAUDE.md` 템플릿 추가 (타겟 프로젝트용); 워크플로/메타 플러그인은 생략
6. README.md 갱신: 플러그인 카드 표 + 사전 준비 `<details>` + 설치 섹션 + "여러 플러그인 동시 설치" + 폴더 구조 + 상세 가이드 링크
7. CLAUDE.md 아키텍처 트리에 플러그인 디렉토리 항목 추가

## 언어 규칙

- 스킬/에이전트 본문, 주석, 문서: 한국어
- 프론트매터 `name` 필드, JSON 키: 영어 (kebab-case)
- `description` 필드: 한국어 (트리거 키워드 포함)

## 자주 만나는 함정

- `Glob`은 파일만 매치 — 디렉토리 확인은 PowerShell `Get-ChildItem -Directory` 또는 `ls`
- JSON 숫자에 `+` 접두사(`+587`) 금지 — 부호 표기는 문자열 필드(`"+1.4%"`)로
- Windows: `python3`/`python` 명령은 MS Store alias로 exit 49 가능 — PowerShell `ConvertFrom-Json` 권장
- 에이전트 이름은 플러그인별 prefix(`pd-`, `kicad-`, `stm32f4-`, `pcb-`)로 — OMC 및 타 플러그인 에이전트와의 이름 충돌 방지. 도메인 약어 prefix(예: `kicad-pcb-analyzer`, `pcb-design-analyst`)도 충돌 위험이 낮으면 허용

<!-- manual-digest:start -->
## 매뉴얼 다이제스트 사용 규칙

이 환경에는 외부 매뉴얼이 다이제스트로 등록되어 있다 (현재 1개) — 도메인 매뉴얼이 필요한 질문을 받으면:

1. `.claude/manuals/INDEX.md` (project) + `~/.claude/manuals/INDEX.md` (global) 양쪽 확인
2. 관련 매뉴얼의 `digest.md` 우선 참조 → 부족하면 `index.md` 페이지 포인터로 원본 핀포인트
3. 답변에 출처(§/p./scope) 명시
4. 인덱싱되지 않은 매뉴얼이면 `/manual-digest <path>` 등록 제안

PDF 핀포인트 추출: `mcp__pdf-reader__read_pdf` `pages: "<범위 또는 혼합 범위>"`
<!-- manual-digest:end -->
<!-- pcb-design-digest:start -->
## PCB 다이제스트 사용 규칙

이 환경에는 보드 PCB 데이터(거버/PADS/KiCad)가 다이제스트로 등록될 수 있다 (현재 0개) — 보드/PCB 정보가 필요한 질문을 받으면:

1. `.claude/pcb-designs/INDEX.md` (project) + `~/.claude/pcb-designs/INDEX.md` (global) 양쪽 확인
2. 관련 보드의 `digest.md` 우선 참조 → 부족하면 `index.md` 파일/라인/넷 포인터로 원본 핀포인트(Read/Grep, PADS 바이너리는 strings|grep)
3. 답변에 출처(파일·D-code/넷·scope) 명시
4. 깊은 분석(SI/PI·차동쌍·플레인 분할·제조성)은 `pcb-design-analyst` 에이전트 호출
5. 인덱싱되지 않은 보드면 `/pcb-design-digest <경로>` 등록 제안

거버·KiCad·PADS ASCII는 텍스트 — MCP·gerbv 불필요, Read/Grep으로 파싱. PADS 바이너리(.pcb)는 strings 부분 추출.
<!-- pcb-design-digest:end -->
