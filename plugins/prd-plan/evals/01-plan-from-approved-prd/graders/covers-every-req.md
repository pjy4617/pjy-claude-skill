---
type: llm
focus: {source: file, path: docs/plan/PLAN-eval.md}
weight: 1
---
커버리지 표의 **실질**만 본다. REQ 행이 표에 있는지 여부는 별도 정규식 채점자가 판정하므로 여기서 다시 세지 않는다.

- MUST 요구(REQ-001, REQ-002, REQ-003, REQ-005) 중 담당 TASK 없이 조용히 빠진 것이 없다.
- 미커버로 표시된 요구가 있다면 사유가 함께 적혀 있다. 사유 없는 미커버는 실패.
- 커버 TASK 칸에 적힌 TASK ID가 문서에 실제로 정의된 TASK를 가리킨다. 정의되지 않은 ID를 적어 표만 채운 경우는 실패.
- 한 TASK가 관련 없는 여러 REQ에 형식적으로 붙어 표만 메운 구성이 아니다.
