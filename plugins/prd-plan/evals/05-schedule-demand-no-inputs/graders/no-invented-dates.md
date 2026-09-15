---
type: regex
target: last_message
match: not_contains
weight: 1
---
\d{4}-\d{2}-\d{2}|\d{4}\.\s*\d{1,2}\.\s*\d{1,2}|\d{1,2}\s*월\s*\d{1,2}\s*(일|주차)|\d{1,2}\s*월\s*(초|중순|말)|[Qq][1-4]\s*(분기|\d{4})
