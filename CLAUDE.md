# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

Claude Code 플러그인 마켓플레이스 서버. 하드웨어 개발 도메인(FPGA, MCU) 스킬과 에이전트를 GitHub 기반으로 배포한다.

마켓플레이스 이름: `pjy-skills`

## 체크항목
- 기능이 변경되거나 추가시 반드시 marketplace.json과 plugin.json이 업데이트되어야 합니다.
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
├── stm32f4/                       ← STM32F4 MCU 플러그인 (4 스킬 + 4 에이전트)
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
├── kicad/                         ← KiCad 회로도 플러그인 (3 스킬 + 3 에이전트)
│   ├── plugin.json
│   ├── skills/
│   │   ├── kicad-design/          ← PRD/설계사양서 → 회로도 생성
│   │   │   └── references/        ← S-expression 포맷 가이드
│   │   ├── kicad-review/          ← 8단계 회로도 리뷰 + BOM 생성
│   │   │   └── references/        ← 체크리스트, 파싱 가이드, 데이터시트 검색
│   │   └── kicad-setup/           ← 에이전트 설치
│   ├── agents/
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
└── manual-digest/                 ← 대용량 매뉴얼 다이제스트 플러그인 (2 스킬, 에이전트 없음)
    ├── plugin.json
    ├── skills/
    │   ├── manual-digest/         ← 인제스트/갱신/목록/삭제 (8단계 워크플로)
    │   │   └── references/        ← 포맷별 추출 가이드 (PDF/HTML/EPUB/DOCX/CHM/TXT-MD)
    │   └── manual-digest-setup/   ← MCP 등록 + 디렉토리 + CLAUDE.md 마커 1회 초기화
    └── docs/USAGE_GUIDE.md
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
- **도메인 플러그인**(vivado/stm32f4/kicad/manual/wmx3md): 특정 기술 도메인 작업. `claude-md/` 템플릿 + `*-setup`이 모든 에이전트 복사
- **워크플로 플러그인**(parallel-delegation): 도메인 무관 절차. `claude-md/` 없음 + `*-setup`이 누락분만 보충
- **메타 도구 플러그인**(harness/manual-digest): Claude Code 자체 환경 또는 컨텍스트 관리 도구. `claude-md/` 없음, 에이전트도 0~필요 최소. `harness`는 setup 없음(현재 디렉토리 진단), `manual-digest`는 1회 환경 초기화용 setup만.

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
- 에이전트 이름은 플러그인별 prefix(`pd-`, `kicad-`, `stm32f4-`)로 — OMC 및 타 플러그인 에이전트와의 이름 충돌 방지

<!-- manual-digest:start -->
## 매뉴얼 다이제스트 사용 규칙

이 환경에는 외부 매뉴얼이 다이제스트로 등록되어 있다 (현재 1개) — 도메인 매뉴얼이 필요한 질문을 받으면:

1. `.claude/manuals/INDEX.md` (project) + `~/.claude/manuals/INDEX.md` (global) 양쪽 확인
2. 관련 매뉴얼의 `digest.md` 우선 참조 → 부족하면 `index.md` 페이지 포인터로 원본 핀포인트
3. 답변에 출처(§/p./scope) 명시
4. 인덱싱되지 않은 매뉴얼이면 `/manual-digest <path>` 등록 제안

PDF 핀포인트 추출: `mcp__pdf-reader__read_pdf` `pages: "<범위 또는 혼합 범위>"`
<!-- manual-digest:end -->