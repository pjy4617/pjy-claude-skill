# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

Claude Code 플러그인 마켓플레이스 서버. 하드웨어 개발 도메인(FPGA, MCU) 스킬과 에이전트를 GitHub 기반으로 배포한다.

마켓플레이스 이름: `pjy-skills`

## 아키텍처

```
.claude-plugin/marketplace.json    ← 마켓플레이스 진입점 (플러그인 목록)
plugins/
├── vivado/                        ← Vivado FPGA 플러그인 (12 스킬 + 6 에이전트)
│   ├── plugin.json
│   ├── skills/                    ← SKILL.md + 보조 파일 (TCL, JSON 등)
│   ├── agents/                    ← 에이전트 .md (setup 스킬이 .claude/agents/로 복사)
│   ├── claude-md/CLAUDE.md        ← 타겟 프로젝트용 CLAUDE.md 템플릿
│   ├── templates/                 ← 예제 RTL/TB/XDC/스크립트
│   └── docs/                      ← 사용 가이드
└── stm32f4/                       ← STM32F4 MCU 플러그인 (4 스킬 + 2 에이전트)
    ├── plugin.json
    ├── skills/
    │   └── stm32f4-firmware/
    │       ├── references/        ← 코딩 규칙, 페리페럴 패턴, 핀 검증 등
    │       ├── references/af-tables/*.json  ← MCU별 AF 매핑 데이터 (F401/F407/F411/F429/F446)
    │       └── assets/templates/  ← CMake, Makefile, 링커, OpenOCD, VS Code 템플릿
    ├── agents/
    ├── claude-md/CLAUDE.md
    └── docs/
```

핵심 구조: 각 플러그인은 `plugin.json` + `skills/` 디렉토리를 가지며, `marketplace.json`이 이를 카탈로그로 등록한다. 에이전트는 마켓플레이스가 직접 지원하지 않으므로, `*-setup` 스킬이 `.claude/agents/`로 복사하는 메커니즘을 사용한다.

## 스킬 파일 규칙

- 각 스킬은 `skills/<스킬명>/SKILL.md`에 YAML 프론트매터 + 마크다운 본문으로 구성
- 프론트매터 필수 필드: `name`, `description`
- 에이전트는 `agents/<에이전트명>.md`에 프론트매터(`name`, `description`, `tools`, `model`) + 본문
- 모든 에이전트 모델은 `opus` 사용
- 보조 파일(JSON, TCL, Python 등)은 같은 스킬 디렉토리에 배치
- 템플릿 파일의 플레이스홀더: `{{PLACEHOLDER}}` 형식 통일 (Mustache 스타일 금지)

## 검증

```bash
# marketplace.json JSON 유효성
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"

# 모든 plugin.json 유효성
find plugins -name "plugin.json" -exec python3 -c "import json; json.load(open('{}')); print('OK: {}')" \;

# af-tables JSON 유효성
for f in plugins/stm32f4/skills/stm32f4-firmware/references/af-tables/*.json; do
  python3 -c "import json; json.load(open('$f')); print('OK: $(basename $f)')"
done
```

## 새 플러그인 추가 절차

1. `plugins/<이름>/plugin.json` 생성 (`name`, `version`, `description`, `skills` 필드)
2. `plugins/<이름>/skills/<스킬명>/SKILL.md` 생성
3. `.claude-plugin/marketplace.json`의 `plugins` 배열에 항목 추가 (`name`, `source`, `description`, `version`)
4. 에이전트가 있으면 `plugins/<이름>/agents/` + `*-setup` 스킬 추가
5. `claude-md/CLAUDE.md` 템플릿 추가 (타겟 프로젝트용)

## 언어 규칙

- 스킬/에이전트 본문, 주석, 문서: 한국어
- 프론트매터 `name` 필드, JSON 키: 영어 (kebab-case)
- `description` 필드: 한국어 (트리거 키워드 포함)
