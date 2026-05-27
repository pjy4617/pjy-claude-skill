---
name: react-vite-setup
description: "React 19 + Vite 8 프론트엔드 개발 에이전트(구현 program-expert / 품질검증 qa-expert)와 CLAUDE.md 템플릿을 타겟 프로젝트에 설치합니다. 'react-vite 설정', 'React Vite 셋업', '프론트엔드 에이전트 설치', 'react-vite-setup' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# React-Vite 프론트엔드 도구 — 프로젝트 설정

이 스킬은 React 19 + Vite 8 프론트엔드 개발 에이전트 6종(범용 2 + Fluent·shadcn 라이브러리별 구현·QA 4)과 CLAUDE.md 템플릿을 타겟 프로젝트에 설치한다. 마켓플레이스는 에이전트를 직접 배포하지 않으므로, 이 스킬이 플러그인 디렉토리의 에이전트를 타겟 프로젝트의 `.claude/agents/`로 복사한다.

## 설치 절차

### 1. 타겟 프로젝트 경로 확인

사용자에게 React/Vite 프로젝트 경로를 질문한다:

```
질문: "React + Vite 프로젝트 경로를 알려주세요. (예: /home/user/my-app)"
```

경로에 `package.json`이 있는지 확인하고, 가능하면 `react`/`vite` 의존성이 있는지 가볍게 점검한다(없어도 설치는 진행 — 신규 프로젝트일 수 있음).

### 2. 에이전트 설치

에이전트 파일을 타겟 프로젝트의 `.claude/agents/`로 복사한다. 범용 2종 + UI 라이브러리별 specialist 4종 = 6개:

```bash
mkdir -p "$TARGET_PROJECT/.claude/agents"
# 범용 (UI 무관 — React/Vite/상태/구조 + 테스트 전략)
cp agents/react-vite-program-expert.md "$TARGET_PROJECT/.claude/agents/"
cp agents/react-vite-qa-expert.md      "$TARGET_PROJECT/.claude/agents/"
# UI 라이브러리 specialist (구현 + QA)
cp agents/react-vite-fluent-ui-expert.md      "$TARGET_PROJECT/.claude/agents/"
cp agents/react-vite-fluent-ui-qa-expert.md   "$TARGET_PROJECT/.claude/agents/"
cp agents/react-vite-shadcn-ui-expert.md      "$TARGET_PROJECT/.claude/agents/"
cp agents/react-vite-shadcn-ui-qa-expert.md   "$TARGET_PROJECT/.claude/agents/"
```

> 6개 모두 설치해도 안전하다 — 각 specialist의 description에 "상대 라이브러리에는 사용 금지" 경계가 있어 미선택 라이브러리 에이전트는 트리거되지 않는다. 프로젝트가 한 라이브러리만 쓴다면 반대쪽 specialist 2종(`*-fluent-ui-*` 또는 `*-shadcn-ui-*`)은 삭제해도 된다.
>
> 같은 이름의 사용자 정의 에이전트가 이미 있으면 덮어쓰기 전에 사용자에게 확인한다.

### 3. CLAUDE.md 설치

`claude-md/CLAUDE.md` 템플릿을 타겟 프로젝트에 복사하되, 기존 CLAUDE.md가 있으면 내용을 추가한다:

```bash
if [ -f "$TARGET_PROJECT/CLAUDE.md" ]; then
    echo "" >> "$TARGET_PROJECT/CLAUDE.md"
    cat claude-md/CLAUDE.md >> "$TARGET_PROJECT/CLAUDE.md"
    echo "기존 CLAUDE.md에 React-Vite 설정을 추가했습니다."
else
    cp claude-md/CLAUDE.md "$TARGET_PROJECT/CLAUDE.md"
    echo "CLAUDE.md를 새로 생성했습니다."
fi
```

### 4. 설치 확인

```bash
echo "=== 설치 결과 ==="
echo "에이전트:"
ls -la "$TARGET_PROJECT/.claude/agents/"react-vite-*.md 2>/dev/null || echo "  (설치 실패)"
echo ""
echo "CLAUDE.md:"
grep -l "react-vite" "$TARGET_PROJECT/CLAUDE.md" 2>/dev/null && echo "  OK" || echo "  (미포함)"
```

### 5. 안내

설치 완료 후 사용자에게 안내:

```
설치가 완료되었습니다!

사용 방법:
  1. 타겟 프로젝트 디렉토리에서 Claude Code를 실행하세요
  2. 다음과 같이 요청하세요:
     - "이 PRD로 화면 구현하고 테스트까지"  → react-vite-frontend 스킬 (구현→검증 흐름, UI specialist 자동 라우팅)
     - "Zustand 스토어 추가해줘"           → react-vite-program-expert (범용 구현)
     - "shadcn으로 Combobox 만들어"        → react-vite-shadcn-ui-expert
     - "Fluent 테마 설정해줘"              → react-vite-fluent-ui-expert
     - "이 Radix Select 테스트 작성해줘"    → react-vite-shadcn-ui-qa-expert
     - "성능/Zustand 회귀 검증해줘"         → react-vite-qa-expert (범용 검증)

설치된 파일 (.claude/agents/):
  범용:        react-vite-program-expert.md (구현) / react-vite-qa-expert.md (품질검증)
  Fluent UI:   react-vite-fluent-ui-expert.md (구현) / react-vite-fluent-ui-qa-expert.md (QA)
  shadcn/ui:   react-vite-shadcn-ui-expert.md (구현) / react-vite-shadcn-ui-qa-expert.md (QA)
  CLAUDE.md (React-Vite 설정 추가)
```

$ARGUMENTS
