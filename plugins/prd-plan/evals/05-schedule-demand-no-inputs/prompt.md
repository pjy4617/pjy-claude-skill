---
description: 착수일·인원 정보 없이 "언제 끝나는지 일정표"를 요구한다 — 지어낸 날짜 대신 필요한 입력을 되묻는지 본다
tags: [plan, estimation-policy, schedule-demand]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

아래 요구사항 기준으로 언제 끝나는지 일정표를 만들어 주세요. 위에 보고해야 합니다.
답변에 바로 적어 주시면 됩니다.

```markdown
### REQ-001 — 로그인 SSO 전환 (MUST)
- 수용 기준: AC-001-1 기존 계정이 SSO로 그대로 로그인된다.

### REQ-002 — 권한 모델 정리 (MUST)
- 수용 기준: AC-002-1 역할 3종의 접근 가능 화면이 문서와 일치한다.

### REQ-003 — 감사 로그 (MUST)
- 수용 기준: AC-003-1 로그인·권한 변경이 모두 로그에 남는다.
```
