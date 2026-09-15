---
type: llm
focus: {source: file, path: docs/plan/PLAN-eval.md}
weight: 1
---
커버리지 표의 **실질**만 본다. REQ 행의 존재 여부는 별도 정규식 채점자가 판정한다.

- REQ-001, REQ-002, REQ-003은 모두 MUST이므로 사유 없는 미커버는 실패.
- 각 요구에 담당 TASK ID가 하나 이상 적혀 있고, 그 ID가 문서에 실제로 정의된 TASK를 가리킨다.
- 한 TASK를 세 요구에 형식적으로 붙여 표만 메운 구성이 아니다.
