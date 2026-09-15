---
description: 계획 수립이 아니라 코드 한 군데 수정 요청 — prd-plan 계열 스킬이 발동하면 안 된다
tags: [negative, no-fire]
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

이 함수에서 빈 리스트가 들어오면 ZeroDivisionError가 납니다. 어떻게 고치면 되나요? 고친 코드를 답변에 적어 주세요.

```python
def average_latency(samples):
    total = sum(s["latency_ms"] for s in samples)
    return total / len(samples)
```
