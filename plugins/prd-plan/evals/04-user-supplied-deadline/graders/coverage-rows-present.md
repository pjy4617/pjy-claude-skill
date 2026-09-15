---
type: regex
target: {source: file, path: docs/plan/PLAN-eval.md}
match: contains
weight: 0.5
---
^(?=[\s\S]*\|\s*\**REQ-001\b)(?=[\s\S]*\|\s*\**REQ-002\b)(?=[\s\S]*\|\s*\**REQ-003\b)(?=[\s\S]*\|\s*\**REQ-004\b)[\s\S]
