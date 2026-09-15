---
type: regex
target: {source: file, path: docs/plan/PLAN-eval.md}
match: not_contains
weight: 1
---
\d{1,2}\s*월\s*\d{1,2}\s*주차|\d{1,2}\s*월\s*(초|중순|말)|[Qq][1-4]\s*(분기|\d{4})
