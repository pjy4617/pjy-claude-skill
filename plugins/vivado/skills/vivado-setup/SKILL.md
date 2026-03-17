---
name: vivado-setup
description: Vivado 스킬 환경 초기 설정. 에이전트 6명과 CLAUDE.md를 프로젝트에 설치합니다. 플러그인 설치 후 최초 1회 실행 필요. "vivado 설정", "vivado setup", "에이전트 설치", "vivado 초기 설정" 등의 요청에 자동 적용.
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob
argument-hint: [--with-templates]
---

# Vivado 스킬 환경 초기 설정

이 스킬은 Vivado 플러그인의 에이전트와 CLAUDE.md를 현재 프로젝트에 설치합니다.

## 실행 절차

### 1단계: 플러그인 디렉토리 확인

`${CLAUDE_SKILL_DIR}` 기준으로 상위 디렉토리에서 `agents/`와 `claude-md/` 폴더를 찾습니다.

```
PLUGIN_DIR = ${CLAUDE_SKILL_DIR}/../../
```

### 2단계: 에이전트 설치

프로젝트 루트의 `.claude/agents/` 디렉토리에 6개 에이전트를 복사합니다.

```bash
mkdir -p .claude/agents
```

복사 대상 (PLUGIN_DIR/agents/ 아래):
- `rtl-designer.md` — RTL 설계 전문가
- `rtl-reviewer.md` — RTL 코드 리뷰어
- `tb-reviewer.md` — 테스트벤치 리뷰어
- `pin-reviewer.md` — 핀 배치 검증자
- `timing-analyst.md` — 타이밍 분석가
- `kicad-xdc-gen.md` — KiCad→XDC 생성

각 파일을 읽어서 `.claude/agents/`에 동일한 이름으로 작성합니다.
이미 존재하는 파일은 덮어쓰기 전에 사용자에게 확인합니다.

### 3단계: CLAUDE.md 병합

`PLUGIN_DIR/claude-md/CLAUDE.md`의 내용을 읽어서 프로젝트 `.claude/CLAUDE.md`에 추가합니다.

- `.claude/CLAUDE.md`가 없으면 새로 생성합니다.
- 이미 존재하면, `## Vivado HDL Project` 섹션이 있는지 확인합니다.
  - 있으면: "이미 설치되어 있습니다" 안내
  - 없으면: 파일 끝에 추가

### 4단계: 프로젝트 디렉토리 생성

기본 디렉토리 구조를 생성합니다:

```bash
mkdir -p rtl tb constraints scripts build/{checkpoints,reports,output,logs}
```

### 5단계: 템플릿 설치 (선택)

`$ARGUMENTS`에 `--with-templates`가 포함되어 있으면:

`PLUGIN_DIR/templates/` 아래의 파일들을 프로젝트에 복사합니다:
- `templates/rtl/*` → `rtl/`
- `templates/tb/*` → `tb/`
- `templates/constraints/*` → `constraints/`
- `templates/scripts/*` → `scripts/`

이미 존재하는 파일은 건너뜁니다.

`--with-templates`가 없으면 이 단계를 건너뛰고 안내만 합니다:
> 예제 파일이 필요하면 `/vivado-setup --with-templates` 로 다시 실행하세요.

### 6단계: 설치 결과 보고

설치 결과를 다음 형식으로 출력합니다:

```
Vivado 스킬 환경 설치 완료!

에이전트 (6명):
  ✅ rtl-designer    — RTL 설계 전문가
  ✅ rtl-reviewer    — RTL 코드 리뷰어
  ✅ tb-reviewer     — 테스트벤치 리뷰어
  ✅ pin-reviewer    — 핀 배치 검증자
  ✅ timing-analyst  — 타이밍 분석가
  ✅ kicad-xdc-gen   — KiCad→XDC 생성

스킬 (12개): 플러그인으로 이미 활성화됨
  vivado-project, vivado-sim, vivado-synth, vivado-impl,
  vivado-bitstream, vivado-build-all, vivado-gui,
  rtl-review, tb-review, pin-review, kicad-xdc, kicad-review

CLAUDE.md: ✅ Vivado 프로젝트 설정 추가됨
디렉토리: ✅ rtl/ tb/ constraints/ scripts/ build/

시작하기:
  "ZedBoard용 프로젝트 만들어줘" 또는 원하는 보드명으로 시작하세요.
  사용 가이드: 플러그인 docs/Vivado-스킬-에이전트-사용가이드.md
```
