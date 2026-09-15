---
type: regex
target: {source: file, path: docs/plan/PLAN-eval.md}
match: contains
weight: 0.5
---
^(?=[\s\S]*근거 요구사항\**\s*[:：][^\n]*REQ-\d{3})(?=[\s\S]*선행\**\s*[:：])(?=[\s\S]*규모\**\s*[:：]\s*\**\s*(S|M|L|XL)\b)[\s\S]
