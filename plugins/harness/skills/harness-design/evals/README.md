# harness-design 평가 케이스

`evals.json`에 4개의 시나리오가 정의돼 있다. 각 시나리오는 동일한 픽스처(`fixtures/weak-harness/`)를 사용한다.

## 픽스처 — `fixtures/weak-harness/`

의도적으로 빈약한 하네스 상태:

| 단계 | 상태 | 비고 |
|-----|------|------|
| 1 CLAUDE.md | ⚠️ 약함 | 10줄 미만, 빌드 명령 없음, 규칙 없음 |
| 2 Permissions | ⚠️ 약함 | allow만, deny 없음 |
| 3 Hooks | ❌ 없음 | settings.json에 hooks 키 자체 없음 |
| 4 MCP | ❌ 없음 | .mcp.json 없음 |
| 5 Subagent | ❌ 없음 | .claude/agents/ 없음 |
| 6 진화 흔적 | ❌ 없음 | "이전 실수 → 규칙" 흔적 없음 |

이 상태로 4개 시나리오 모두를 의미 있게 평가할 수 있다.

## 시나리오

| # | 이름 | 프롬프트 요약 | 기대 동작 |
|---|------|-------------|---------|
| 1 | full-diagnosis | "하네스 봐줘" | Phase 0 진단 보고서 |
| 2 | permissions-routing | "rm 막아줘" | 단계 2 직행 + deny 추천 |
| 3 | hooks-routing | "코드 수정 시 npm test" | 단계 3 직행 + PostToolUse 추천 |
| 4 | evolution-check | "Opus 4.7 올렸어" | 단계 6 진화 점검 |

## 수동 실행 (Claude Code)

```bash
cd plugins/harness/skills/harness-design/evals/fixtures/weak-harness
claude
# 그 다음 evals.json의 prompt를 입력하고 응답 확인
```

응답이 `evals.json`의 `assertions`를 만족하는지 사람이 확인.

## 자동 실행 (서브에이전트)

skill-creator 워크플로우를 따라:

1. with-skill 런: 스킬 경로를 명시한 서브에이전트
2. without-skill 런: 베이스라인(스킬 없이 같은 프롬프트)

각 런의 첫 턴 응답만 평가한다 — 이 스킬은 사용자 확정 대기 흐름이라 자동 평가는 첫 턴에 한정한다.
