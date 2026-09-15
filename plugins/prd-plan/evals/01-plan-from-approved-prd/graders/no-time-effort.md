---
type: regex
target: {source: file, path: docs/plan/PLAN-eval.md}
match: not_contains
flags: "i"
weight: 1
---
\d+\s*(인일|인월|맨먼스|man-?days?|person-?days?|스토리\s*포인트)|약\s*\d+\s*(시간|일|주|개월)|\d+\s*(시간|일|주|개월)\s*(소요|예상|걸)|주당\s*\d+
