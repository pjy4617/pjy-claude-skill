# 단계 3: 자동 검증 — Hooks

> Hooks는 도구 사용 전/후에 스크립트를 **자동 실행**한다. 클로드가 우회하려 해도 우회할 수 없다.
> CLAUDE.md에 "테스트 돌려"라고 적는 것 = 부탁. PostToolUse Hook으로 npm test 박는 것 = 강제 확인.

## 이 단계가 잡는 빈틈

- 클로드가 "테스트는 다음에"라며 검증 생략
- 코드 수정 후 lint/format 안 돌려서 PR 깨짐
- 커밋 전 secrets 검사 누락
- 매 작업 후 사용자가 일일이 확인해야 하는 검증을 자동화

## Hook 종류 (자주 쓰는 것 위주)

| 이벤트 | 시점 | 대표 용도 |
|-------|------|----------|
| `PreToolUse` | 도구 호출 직전 | 위험 명령 추가 검증, 입력 변환 |
| `PostToolUse` | 도구 호출 직후 | 테스트 자동 실행, lint, format |
| `UserPromptSubmit` | 사용자 입력 시 | 컨텍스트 주입 (예: 현재 brunch 정보) |
| `Stop` | 응답 종료 시 | 작업 요약, 알림 발송 |
| `Notification` | 권한 프롬프트 등 | 외부 알림 |

각 이벤트는 도구 매처(matcher)와 함께 정의한다. 예: `matcher: "Edit|Write"` → 파일 수정 도구에만 발동.

## 진단 체크리스트

settings.json의 `hooks` 키를 Read:

| 항목 | 양호 ✅ | 약함 ⚠️ | 없음 ❌ |
|------|--------|--------|---------|
| hooks 키 존재 | 있음 | 빈 객체 | 없음 |
| PostToolUse 검증 | Edit/Write 후 테스트/lint | matcher 부정확 | 없음 |
| PreToolUse 안전망 | 위험 명령 추가 검증 | 없음 | 없음 |
| 차단 로직 | 실패 시 exit 1로 차단 | warning만 | 없음 |
| 언어/플랫폼 적합성 | OS·셸과 일치 | 호환 문제 | - |

`.claude/hooks/` 스크립트 디렉토리도 함께 본다.

## settings.json hooks 구조

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "npm run lint --silent"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/check-bash.sh"
          }
        ]
      }
    ]
  }
}
```

스크립트 종료 코드:
- `0` — 통과, 클로드 진행
- `2` — 차단, stderr 메시지가 클로드에게 피드백으로 전달
- 그 외 — 경고만, 진행은 함

`exit 2`가 핵심이다 — 이게 "강제 확인"의 메커니즘이다. 실패하면 클로드가 결과를 받고 수정해야 한다.

## 추천 시나리오

### 시나리오 A: 코드 수정 → 테스트 자동 실행

가장 흔한 패턴. PostToolUse(Edit|Write) → npm test (또는 pytest 등):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "npm test --silent --bail",
            "timeout": 60000
          }
        ]
      }
    ]
  }
}
```

주의:
- 테스트가 느리면 흐름 방해. **빠른 테스트만** 자동 실행 (단위 테스트, lint)
- 통합/e2e는 수동 또는 Stop hook으로
- `timeout` 명시 — 무한 대기 방지

### 시나리오 B: Bash 추가 안전망 (PreToolUse)

deny로 못 잡는 컨텍스트 의존 검증:

```bash
# .claude/hooks/check-bash.sh
#!/usr/bin/env bash
set -e

# 클로드가 호출한 명령은 stdin으로 들어옴 (JSON)
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')

# 예: 프로덕션 DB에 접근하는 명령은 한 번 더 차단
if echo "$cmd" | grep -qE 'DATABASE_URL.*prod'; then
  echo "프로덕션 DB 명령 차단 — 단계 2 deny에 추가하거나 수동 실행" >&2
  exit 2
fi

exit 0
```

### 시나리오 C: 커밋 전 secrets 검사

PreToolUse에서 git commit 직전 검사:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/secrets-check.sh"
          }
        ]
      }
    ]
  }
}
```

```bash
# .claude/hooks/secrets-check.sh
#!/usr/bin/env bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')

# git commit 명령일 때만
if echo "$cmd" | grep -qE '^git commit'; then
  if git diff --cached | grep -qE '(api_key|secret|password|BEGIN PRIVATE KEY)'; then
    echo "스테이지에 시크릿 의심 패턴 발견 — 커밋 차단" >&2
    exit 2
  fi
fi

exit 0
```

### 시나리오 D: Stop hook으로 작업 요약

응답 종료 시 자동 알림:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "echo '✓ Claude turn complete' | osascript -e 'display notification \"\" with title \"Claude\"'"
          }
        ]
      }
    ]
  }
}
```

(macOS 예시. Windows는 PowerShell `BurntToast`, Linux는 `notify-send`)

## Hook 작성 5원칙

1. **빠를 것** — 5초 이상 걸리면 흐름 방해. 무거운 검증은 별도 실행
2. **명확한 차단/통과** — exit 0 또는 exit 2. 애매하게 warning만 띄우면 의미 약함
3. **stderr에 사람이 읽을 수 있는 메시지** — exit 2일 때 클로드가 그 메시지를 받아 수정
4. **부작용 최소화** — Hook이 git stash 같은 걸 자체 실행하면 사고 위험
5. **OS/셸 의존 명시** — 팀 환경 다르면 PowerShell/bash 별도 분기

## 진행 절차 (이 단계 진입 시)

1. 현재 settings.json hooks Read + `.claude/hooks/` 디렉토리 확인
2. 사용자에게 "어떤 검증을 강제하고 싶나요?" 묻기
   - 테스트 자동 실행?
   - 커밋 전 검사?
   - 위험 명령 추가 차단?
3. 시나리오 선택 후 추천 작성:
   - hook 정의 (settings.json diff)
   - 필요 시 보조 스크립트 (`.claude/hooks/*.sh` 본문)
4. 사용자 확정
5. 적용 후 **반드시 테스트 한 사이클**:
   - 의도적으로 hook이 발동할 행위 시뮬레이션
   - exit 2가 정말 차단하는지, 메시지가 제대로 전달되는지 확인

## 자주 발생하는 함정

- **너무 무거운 hook** — 5초+ 걸리는 검증은 흐름 끊고, 사용자가 hook을 비활성화하게 만든다
- **CLAUDE.md에 "테스트 돌려"만 적기** — 그건 단계 1. 강제하고 싶으면 hook 필요
- **exit 0만 쓰기** — 차단이 안 되면 부탁과 다를 바 없음
- **stdin JSON 파싱 누락** — 도구 입력은 stdin에 JSON으로 옴. `jq`로 파싱하거나 정규표현식
- **timeout 설정 누락** — 무한 대기 hook이 클로드를 멈춰버림
- **OS 무시** — `bash -c`는 Windows에선 안 됨. PowerShell 분기 필요할 수 있음
