---
type: llm
focus: {source: file, path: docs/plan/PLAN-eval.md}
weight: 1
---
커버리지 표의 **실질**만 본다. REQ 행의 존재 여부는 별도 정규식 채점자가 판정한다.

- MUST 요구(REQ-001, REQ-002, REQ-003)가 담당 TASK 없이 조용히 빠지지 않았다.
- MAY 등급인 REQ-004를 이번 범위에서 빼는 것은 허용되지만, 뺐다는 사실과 사유가 문서에 적혀 있어야 한다. 사유 없이 비어 있으면 실패.
- 커버 TASK 칸에 적힌 TASK ID가 문서에 실제로 정의된 TASK를 가리킨다.
