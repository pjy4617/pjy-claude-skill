---
type: regex
target: {source: file, path: .claude/manuals/acme-mx184rb-datasheet/digest.md}
match: contains
flags: m
---
^extractor:\s*(pymupdf|pdftotext-layout|page-render)\s*$
