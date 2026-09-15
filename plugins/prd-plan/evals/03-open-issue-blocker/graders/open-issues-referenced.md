---
type: regex
target: {source: file, path: docs/plan/PLAN-eval.md}
match: contains
weight: 0.5
---
^(?=[\s\S]*OPEN-001\b)(?=[\s\S]*OPEN-002\b)[\s\S]
