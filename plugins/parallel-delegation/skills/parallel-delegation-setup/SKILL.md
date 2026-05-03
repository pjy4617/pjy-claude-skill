---
name: parallel-delegation-setup
description: "parallel-delegation 워크플로의 3-role 에이전트(구현/테스트/구현품질검증)를 타겟 프로젝트에 설치합니다. 기존 .claude/agents/와 OMC 설치 여부를 스캔해 누락된 역할만 보충 설치하고, 사용자 정의 에이전트는 덮어쓰지 않습니다. '병렬 위임 설정', 'parallel-delegation 셋업', '3-role 에이전트 설치' 등 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# parallel-delegation 3-role 에이전트 설치

이 스킬은 parallel-delegation 워크플로가 권장하는 **구현 / 테스트 / 구현품질검증** 3-role 에이전트를 타겟 프로젝트의 `.claude/agents/`에 설치한다.

## 핵심 원칙

- **사용자 정의 에이전트가 항상 우선** — 기존 `.claude/agents/`에 같은 역할의 에이전트가 있으면 덮어쓰지 않음
- **OMC 호환** — OMC가 설치된 환경에서는 OMC 에이전트(executor / test-engineer / verifier)가 같은 역할을 수행하므로 안내만 하고 설치 생략 가능
- **누락분만 보충** — 빈 역할만 채움
- **번들 에이전트는 `pd-` prefix** — 기존 에이전트와 충돌 방지

## 설치 절차

### 1. 타겟 프로젝트 경로 확인

사용자에게 프로젝트 디렉토리 경로를 질문한다:

```
질문: "parallel-delegation 에이전트를 설치할 프로젝트 경로를 알려주세요. (예: /home/user/myproject)"
```

경로가 git 저장소 루트인지 또는 `.claude/` 디렉토리가 있을 위치인지 확인한다.

### 2. 환경 스캔

```bash
TARGET="$1"

# OMC 설치 여부 확인 (사용자 ~/.claude/plugins 또는 프로젝트 .claude/plugins)
OMC_FOUND=false
if [ -d "$HOME/.claude/plugins/cache/oh-my-claudecode" ] || \
   [ -d "$HOME/.claude/plugins/oh-my-claudecode" ] || \
   [ -d "$TARGET/.claude/plugins/oh-my-claudecode" ]; then
    OMC_FOUND=true
fi

# 기존 .claude/agents/ 스캔
mkdir -p "$TARGET/.claude/agents"
EXISTING_AGENTS=$(ls "$TARGET/.claude/agents/"*.md 2>/dev/null)
```

### 3. 역할 매핑

기존 에이전트의 frontmatter `description`에서 역할 키워드를 찾아 매핑한다.

| 역할 | 키워드 (description 검색) |
|------|------------------------|
| 구현 | "구현", "implement", "코드 작성", "리팩토링", "executor" |
| 테스트 | "테스트", "test", "TDD", "test-writer", "test-engineer" |
| 구현품질검증 | "검증", "verify", "리뷰", "review", "품질", "verifier", "QC" |

```bash
ROLE_IMPL=""
ROLE_TEST=""
ROLE_VERIFY=""

for agent_file in $EXISTING_AGENTS; do
    name=$(grep "^name:" "$agent_file" | sed 's/name:\s*//' | tr -d '"')
    desc=$(grep "^description:" "$agent_file" | head -1)

    if echo "$desc" | grep -qiE "구현|implement|코드 작성|리팩토링|executor"; then
        ROLE_IMPL="$ROLE_IMPL $name"
    fi
    if echo "$desc" | grep -qiE "테스트|test|TDD"; then
        ROLE_TEST="$ROLE_TEST $name"
    fi
    if echo "$desc" | grep -qiE "검증|verify|리뷰|review|품질|verifier|QC"; then
        ROLE_VERIFY="$ROLE_VERIFY $name"
    fi
done
```

### 4. 커버리지 매트릭스 출력

```
═══════════════════════════════════════════════════
  parallel-delegation 3-role 커버리지
═══════════════════════════════════════════════════

대상: {TARGET}
OMC 감지: {예/아니오}

| 역할          | 보유 에이전트              | 권장 조치        |
|--------------|--------------------------|----------------|
| 구현          | {ROLE_IMPL or 없음}        | {유지/설치}      |
| 테스트        | {ROLE_TEST or 없음}        | {유지/설치}      |
| 구현품질검증   | {ROLE_VERIFY or 없음}      | {유지/설치}      |
```

OMC가 감지되면 다음 안내를 추가한다:

```
[OMC 사용자 안내]
OMC가 감지되었습니다. OMC의 다음 에이전트가 같은 역할을 수행할 수 있습니다.
  - 구현: oh-my-claudecode:executor
  - 테스트: oh-my-claudecode:test-engineer
  - 구현품질검증: oh-my-claudecode:verifier

parallel-delegation 워크플로는 OMC 에이전트와도 자동 매칭되므로
번들(pd-*) 설치 없이 사용 가능합니다.
다만, pd-* 에이전트는 3-role 분리 원칙이 description과 본문에
명시되어 있어 매칭 정확도가 더 높을 수 있습니다.
```

### 5. 사용자 확인

```
어떻게 진행할까요?

  [1] 누락된 역할만 번들에서 설치 (권장)
       → 기존 사용자 정의 에이전트가 커버하는 역할은 건드리지 않음

  [2] 모든 역할에 번들 설치 (기존 에이전트와 공존)
       → pd-* 에이전트가 추가 옵션으로 카탈로그에 들어감
       → 메인 에이전트가 description 적합도로 선택

  [3] OMC 에이전트 사용 (번들 설치 안 함)
       → OMC가 있을 때만 권장. parallel-delegation은 OMC 에이전트와 매칭됨

  [4] 취소

선택: _
```

### 6. 선택에 따라 복사

```bash
case "$CHOICE" in
    1)
        # 누락된 역할만
        if [ -z "$ROLE_IMPL" ]; then
            cp agents/pd-implementer.md "$TARGET/.claude/agents/"
            echo "  설치: pd-implementer (구현)"
        else
            echo "  유지: $ROLE_IMPL (구현)"
        fi
        if [ -z "$ROLE_TEST" ]; then
            cp agents/pd-tester.md "$TARGET/.claude/agents/"
            echo "  설치: pd-tester (테스트)"
        else
            echo "  유지: $ROLE_TEST (테스트)"
        fi
        if [ -z "$ROLE_VERIFY" ]; then
            cp agents/pd-verifier.md "$TARGET/.claude/agents/"
            echo "  설치: pd-verifier (구현품질검증)"
        else
            echo "  유지: $ROLE_VERIFY (구현품질검증)"
        fi
        ;;
    2)
        cp agents/pd-implementer.md "$TARGET/.claude/agents/"
        cp agents/pd-tester.md "$TARGET/.claude/agents/"
        cp agents/pd-verifier.md "$TARGET/.claude/agents/"
        echo "  설치: pd-implementer, pd-tester, pd-verifier"
        ;;
    3)
        echo "번들 설치를 생략합니다. parallel-delegation 워크플로는"
        echo "기존 에이전트(OMC 포함)와 description 기반으로 자동 매칭됩니다."
        ;;
    4)
        echo "취소되었습니다."
        exit 0
        ;;
esac
```

### 7. 설치 확인

```bash
echo ""
echo "=== 설치 결과 ==="
ls -la "$TARGET/.claude/agents/"pd-*.md 2>/dev/null || \
    echo "  (번들 설치 없음 — 기존 에이전트 사용)"

echo ""
echo "전체 에이전트 카탈로그:"
ls "$TARGET/.claude/agents/"*.md 2>/dev/null | sed 's|.*/|  - |' | \
    sed 's|\.md$||'
```

### 8. 안내

```
설치가 완료되었습니다!

다음 단계:
  1. 타겟 프로젝트 디렉토리에서 Claude Code를 새로 실행하세요
     (세션 시작 시 .claude/agents/를 스캔합니다)

  2. 다음과 같이 요청하면 자동으로 3-role 분리 워크플로가 적용됩니다:
     - "이 기능 구현하고 테스트도 만들고 검증까지 해줘"
     - "병렬로 구현+테스트+검증 진행해줘"
     - "TDD로 진행" (pd-tester가 먼저 실패 테스트 → pd-implementer가 구현)

  3. parallel-delegation 워크플로 자체는 description에 매칭되는
     사용자 요청에서 자동 활성화되거나, 명시적으로 호출됩니다.

매칭 동작:
  메인 에이전트가 §2(에이전트 매칭)에서 .claude/agents/를 자동으로 훑어
  description이 가장 잘 맞는 에이전트를 고릅니다.
  사용자가 직접 만든 에이전트도 같은 메커니즘으로 자동 사용됩니다.

3-role 분리의 의의:
  같은 에이전트가 구현·테스트·검증을 모두 하면 자기 검증의 함정에 빠집니다
  (자기 코드의 약점을 자기가 못 봄). 역할을 분리하면 함정이 구조적으로
  차단되며, 산출물의 품질이 독립 시각에서 검증됩니다.
```

$ARGUMENTS
