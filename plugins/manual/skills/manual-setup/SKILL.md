---
name: manual-setup
description: "Manual 스킬 환경 초기 설정. 에이전트 4명과 CLAUDE.md를 프로젝트에 설치합니다. 플러그인 설치 후 최초 1회 실행 필요. 'manual 설정', 'manual setup', '문서화 에이전트 설치', '매뉴얼 초기 설정' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob
---

# Manual 스킬 환경 초기 설정

이 스킬은 Manual 플러그인의 에이전트와 CLAUDE.md를 현재 프로젝트에 설치합니다.

## 실행 절차

### 1단계: 플러그인 디렉토리 확인

`${CLAUDE_SKILL_DIR}` 기준으로 상위 디렉토리에서 `agents/`와 `claude-md/` 폴더를 찾습니다.

```
PLUGIN_DIR = ${CLAUDE_SKILL_DIR}/../../
```

### 2단계: 에이전트 설치

프로젝트 루트의 `.claude/agents/` 디렉토리에 4개 에이전트를 복사합니다.

```bash
mkdir -p .claude/agents
```

복사 대상 (PLUGIN_DIR/agents/ 아래):
- `sphinx-manual-writer.md` — Sphinx 문서화 전문가
- `manual-writer.md` — 프로그램 매뉴얼 작성 전문가
- `windows-manual-writer.md` — Windows 매뉴얼 전문가
- `manual-reviewer.md` — 매뉴얼 품질 리뷰 전문가

각 파일을 읽어서 `.claude/agents/`에 동일한 이름으로 작성합니다.
이미 존재하는 파일은 덮어쓰기 전에 사용자에게 확인합니다.

### 3단계: CLAUDE.md 병합

`PLUGIN_DIR/claude-md/CLAUDE.md`의 내용을 읽어서 프로젝트 `.claude/CLAUDE.md`에 추가합니다.

- `.claude/CLAUDE.md`가 없으면 새로 생성합니다.
- 이미 존재하면, `## Sphinx 문서화 프로젝트` 섹션이 있는지 확인합니다.
  - 있으면: "이미 설치되어 있습니다" 안내
  - 없으면: 파일 끝에 추가

### 4단계: Python 의존성 안내

```bash
pip install sphinx sphinx-rtd-theme myst-parser sphinx-copybutton
```

위 명령을 실행할지 사용자에게 확인합니다.

### 5단계: 설치 결과 보고

```
Manual 스킬 환경 설치 완료!

에이전트 (4명):
  ✅ sphinx-manual-writer   — Sphinx 문서화 전문가
  ✅ manual-writer          — 프로그램 매뉴얼 작성 전문가
  ✅ windows-manual-writer  — Windows 매뉴얼 전문가
  ✅ manual-reviewer        — 매뉴얼 품질 리뷰 전문가

스킬 (4개): 플러그인으로 이미 활성화됨
  manual-write, manual-build, manual-review, manual-setup

CLAUDE.md: ✅ Sphinx 문서화 설정 추가됨

시작하기:
  "이 프로젝트의 사용자 매뉴얼을 만들어줘" 로 시작하세요.
```
