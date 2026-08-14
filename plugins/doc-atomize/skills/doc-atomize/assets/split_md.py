#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""doc-atomize — 대용량 마크다운을 무손실로 원자 분할하고 검색 인덱스를 생성한다.

설계 원칙
  1. 무손실: 조각 본문은 원본 바이트를 그대로 옮긴다(요약 금지). 재조립하면 원본과 동일.
  2. 결정적: 같은 입력·같은 옵션이면 항상 같은 결과. 의미 판단(요약/키워드/라우팅)은 LLM 몫.
  3. metadata.json이 정본: index.md는 metadata.json에서 생성되는 뷰. 큐레이션은 metadata에 남는다.

서브커맨드
  split   <src.md> --out <dir>   신규 분할
  verify  <dir>                  재조립 sha256 대조 + 구조 무결성 검사
  reindex <dir>                  metadata.json → <doc-id>.index.md 재생성
  update  <dir>                  원본 변경분만 재분할 (큐레이션 보존)

의존성 없음 (Python 3.8+ 표준 라이브러리만).
"""

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import date

TOOL_VERSION = "1.0.0"

# ── 기본 크기 정책 (줄 수 기준) ────────────────────────────────────────────
DEFAULT_MIN_LINES = 40      # 이 미만이면 인접 형제와 병합 후보
DEFAULT_MAX_LINES = 250     # 이 초과면 하위 헤딩으로 하강
DEFAULT_HARD_MAX = 400      # 하위 헤딩이 없어도 이 초과면 문단 폴백 분할

ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:\s+(.*?))?\s*$")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*(.*)$")
CODE_SPAN = re.compile(r"`([^`\n]{1,40})`")
UPPER_ID = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
PART_ID = re.compile(r"\b[A-Za-z]{1,6}[0-9]{2,}[A-Za-z0-9\-]*\b")
STOPWORDS = {
    "NOTE", "TODO", "FIXME", "WARN", "WARNING", "THE", "AND", "FOR", "NOT",
    "YES", "MUST", "SHALL", "TBD", "N/A", "NA", "OK", "PDF", "MD",
}


# ══════════════════════════════════════════════════════════════════════════
# 입출력 유틸
# ══════════════════════════════════════════════════════════════════════════

def read_source(path):
    """원본을 읽어 정규화한다. 반환: (lines, meta)

    정규화 = BOM 제거 + CRLF/CR → LF. 무손실 보증은 '정규화 후' 기준이며,
    원본 바이트 sha256(raw)은 변경 감지용으로 따로 보관한다.
    """
    with open(path, "rb") as f:
        raw = f.read()
    raw_sha = hashlib.sha256(raw).hexdigest()

    text = raw.decode("utf-8-sig")
    if "\r\n" in text:
        line_ending = "crlf"
    elif "\r" in text:
        line_ending = "cr"
    else:
        line_ending = "lf"
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    had_trailing_nl = text.endswith("\n")
    body = text[:-1] if had_trailing_nl else text
    lines = body.split("\n") if body != "" else []

    meta = {
        "source_sha256_raw": raw_sha,
        "source_sha256_normalized": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "line_ending": line_ending,
        "trailing_newline": had_trailing_nl,
        "total_lines": len(lines),
        "bytes": len(raw),
    }
    return lines, meta


def join_lines(lines, trailing_newline):
    out = "\n".join(lines)
    if trailing_newline:
        out += "\n"
    return out


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ══════════════════════════════════════════════════════════════════════════
# 마크다운 파싱 — 코드펜스를 인식하는 헤딩 스캐너
# ══════════════════════════════════════════════════════════════════════════

def scan_headings(lines):
    """펜스 밖의 ATX 헤딩만 수집한다. 반환: [(line_idx, level, text)]

    - 코드펜스(``` / ~~~) 내부의 '#'는 헤딩이 아니다.
    - 문서 선두 YAML 프론트매터(--- ... ---) 내부도 제외한다.
    - setext 헤딩(=== / ---)은 표·수평선과 구별이 모호해 인식하지 않는다(문서화된 한계).
    """
    headings = []
    fence = None            # (char, length)
    in_frontmatter = False

    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue

        m = FENCE_OPEN.match(line)
        if m:
            marker = m.group(1)
            char, length = marker[0], len(marker)
            if fence is None:
                fence = (char, length)
                continue
            # 닫는 펜스: 같은 문자 + 같거나 긴 길이 + info string 없음
            if char == fence[0] and length >= fence[1] and not m.group(2).strip():
                fence = None
            continue
        if fence is not None:
            continue

        hm = ATX_HEADING.match(line)
        if hm:
            text = (hm.group(2) or "").strip().rstrip("#").strip()
            headings.append((i, len(hm.group(1)), text))
    return headings


def frontmatter_span(lines):
    """선두 YAML 프론트매터의 줄 범위 [start, end_exclusive). 없으면 None."""
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return (0, i + 1)
    return None


# ══════════════════════════════════════════════════════════════════════════
# 분할 — 헤딩 우선 + 크기 가드 하이브리드
# ══════════════════════════════════════════════════════════════════════════

class Chunk(object):
    __slots__ = ("start", "end", "level", "title", "path", "parent_key", "kind")

    def __init__(self, start, end, level, title, path, parent_key, kind="section"):
        self.start = start          # 0-based, inclusive
        self.end = end              # 0-based, exclusive
        self.level = level
        self.title = title
        self.path = path            # 헤딩 빵부스러기 리스트
        self.parent_key = parent_key
        self.kind = kind            # section | preamble | overflow

    @property
    def nlines(self):
        return self.end - self.start


def detect_base_level(headings):
    """분할 기준 레벨 자동 판정: 2회 이상 등장하는 가장 얕은 레벨."""
    if not headings:
        return 2
    counts = {}
    for _, lvl, _ in headings:
        counts[lvl] = counts.get(lvl, 0) + 1
    for lvl in sorted(counts):
        if counts[lvl] >= 2:
            return lvl
    return min(counts)


def _children(headings, level, start, end):
    """[start, end) 안의 `level` 레벨 헤딩 목록."""
    return [h for h in headings if h[1] == level and start <= h[0] < end]


def _paragraph_split(lines, start, end, max_lines):
    """헤딩이 없는 과대 구간을 빈 줄(펜스 밖) 경계로 쪼갠다."""
    fence = None
    breakpoints = []
    for i in range(start, end):
        line = lines[i]
        m = FENCE_OPEN.match(line)
        if m:
            marker = m.group(1)
            char, length = marker[0], len(marker)
            if fence is None:
                fence = (char, length)
            elif char == fence[0] and length >= fence[1] and not m.group(2).strip():
                fence = None
            continue
        if fence is None and line.strip() == "":
            breakpoints.append(i)

    spans = []
    cur = start
    for bp in breakpoints:
        if bp - cur >= max_lines:
            spans.append((cur, bp + 1))
            cur = bp + 1
    if cur < end:
        spans.append((cur, end))
    return spans or [(start, end)]


def split_region(lines, headings, start, end, level, path, parent_key, limits, out):
    """[start, end) 구간을 `level` 헤딩 기준으로 분할해 out에 chunk를 append."""
    max_lines, hard_max = limits["max_lines"], limits["hard_max"]
    kids = _children(headings, level, start, end)

    if not kids:
        # 더 하강할 헤딩이 없다 → 크기만 보고 문단 폴백
        if end - start > hard_max:
            for k, (s, e) in enumerate(_paragraph_split(lines, start, end, max_lines)):
                title = path[-1] if path else "(문서 머리)"
                out.append(Chunk(s, e, level - 1, title if k == 0 else title + " (계속)",
                                 list(path), parent_key, "section" if k == 0 else "overflow"))
        else:
            out.append(Chunk(start, end, level - 1, path[-1] if path else "(문서 머리)",
                             list(path), parent_key))
        return

    # 첫 자식 헤딩 앞의 도입부
    intro_end = kids[0][0]
    if intro_end > start:
        out.append(Chunk(start, intro_end, level - 1, (path[-1] if path else "(문서 머리)"),
                         list(path), parent_key, "preamble" if not path else "section"))

    for idx, (hidx, hlvl, htext) in enumerate(kids):
        seg_end = kids[idx + 1][0] if idx + 1 < len(kids) else end
        child_path = list(path) + [htext]
        child_parent_key = tuple(path)
        if seg_end - hidx > max_lines and level < 6:
            split_region(lines, headings, hidx, seg_end, level + 1,
                         child_path, child_parent_key, limits, out)
        else:
            out.append(Chunk(hidx, seg_end, hlvl, htext, child_path, child_parent_key))


def _combine_title(a, b):
    """병합된 조각의 제목 — 흡수된 절이 목차에서 실종되지 않도록 결합한다."""
    if a.kind == "preamble":
        return b.title
    if " + " in a.title:
        return a.title if a.title.endswith("…") else a.title + " + …"
    return "%s + %s" % (a.title, b.title)


def merge_small(chunks, limits, base_level):
    """작은 인접 조각을 같은 부모 아래에서만 병합한다(순서·연속성 보존).

    최상위(base_level) 절끼리의 병합은 임계값을 절반으로 낮춘다 — 장(章) 단위가
    통째로 다른 장에 흡수되면 목차 번호가 끊겨 사람이 문서를 못 따라간다.
    """
    min_lines, max_lines = limits["min_lines"], limits["max_lines"]
    top_min = max(1, min_lines // 2)
    merged = []
    for ch in chunks:
        if not merged:
            merged.append(ch)
            continue
        prev = merged[-1]
        both_top = (prev.level <= base_level and ch.level <= base_level
                    and prev.kind != "preamble")
        threshold = top_min if both_top else min_lines
        joinable = (
            prev.end == ch.start
            and prev.parent_key == ch.parent_key
            and (prev.nlines < threshold or ch.nlines < threshold)
            and prev.nlines + ch.nlines <= max_lines
            and ch.kind != "overflow"
        )
        if joinable:
            title = _combine_title(prev, ch)
            prev.end = ch.end
            if prev.kind == "preamble" and ch.kind != "preamble":
                # 머리말이 첫 절에 흡수되면 그 절의 정체성을 따른다
                prev.path = ch.path
                prev.level = ch.level
                prev.kind = ch.kind
            prev.title = title
        else:
            merged.append(ch)
    return merged


def build_chunks(lines, headings, limits, base_level):
    if not headings:
        chunks = []
        for k, (s, e) in enumerate(_paragraph_split(lines, 0, len(lines), limits["max_lines"])):
            chunks.append(Chunk(s, e, 1, "(문서 머리)" if k == 0 else "(계속)", [], (),
                                "preamble" if k == 0 else "overflow"))
        return chunks
    out = []
    split_region(lines, headings, 0, len(lines), base_level, [], (), limits, out)
    out = [c for c in out if c.end > c.start]
    return merge_small(out, limits, base_level)


# ══════════════════════════════════════════════════════════════════════════
# 슬러그 / 키워드 / 요약 초안
# ══════════════════════════════════════════════════════════════════════════

CJK = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣ぀-ヿ一-鿿]")


def slugify(text, style="auto", maxlen=48):
    text = re.sub(r"`([^`]*)`", r"\1", text or "")
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = unicodedata.normalize("NFC", text).strip()

    ascii_slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

    # auto: CJK가 섞인 제목은 ASCII 슬러그가 의미를 잃으므로 원문을 보존한다(식별성 우선).
    #       ascii 스타일은 파일명 ASCII만 허용하는 환경용 강제 옵션.
    if style == "ascii" or not CJK.search(text):
        return (ascii_slug[:maxlen].strip("-") or "section")

    uni = re.sub(r"[\s.]+", "-", text)
    uni = re.sub(r"[^0-9A-Za-z가-힣ㄱ-ㅎㅏ-ㅣ぀-ヿ一-鿿\-]", "", uni)
    uni = re.sub(r"-{2,}", "-", uni).strip("-")
    return (uni[:maxlen].strip("-") or ascii_slug[:maxlen].strip("-") or "section")


def extract_keywords(body_lines, title, limit=8):
    text = "\n".join(body_lines)
    freq = {}

    def bump(tok, weight=1):
        tok = tok.strip()
        if not tok or len(tok) < 3 or len(tok) > 40:
            return
        if tok.upper() in STOPWORDS:
            return
        key = tok.lower()
        cur = freq.get(key)
        if cur is None or len(tok) > len(cur[0]):
            freq[key] = [tok, cur[1] + weight if cur else weight]
        else:
            cur[1] += weight

    for m in CODE_SPAN.finditer(text):
        tok = m.group(1)
        if not re.search(r"[\s|]", tok):
            bump(tok, 2)
    for m in UPPER_ID.finditer(text):
        bump(m.group(0), 1)
    for m in PART_ID.finditer(text):
        bump(m.group(0), 2)
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9_]{2,}", title or ""):
        bump(m.group(0), 3)

    ranked = sorted(freq.values(), key=lambda kv: (-kv[1], kv[0].lower()))
    return [tok for tok, _ in ranked[:limit]]


def inner_headings(body_lines, own_title, limit=24):
    """조각이 품고 있는 하위/흡수 헤딩 목록 [[제목, 레벨], ...] (자기 제목 제외).

    작은 절이 병합되어도 목차에서 사라지지 않게 하는 근거 데이터다.
    레벨을 함께 남기는 이유: 인덱스에서 잘라낼 때 장(章) 수준 헤딩을 먼저 살리기 위해.
    """
    out, seen = [], set()
    for i, (idx, lvl, txt) in enumerate(scan_headings(body_lines)):
        if i == 0 and idx == 0 and txt == own_title:
            continue
        if txt and txt not in seen:
            seen.add(txt)
            out.append([txt, lvl])
    return out[:limit]


def draft_summary(body_lines, maxlen=90, headings=None):
    """첫 실질 문장을 요약 초안으로 뽑는다(LLM이 나중에 다듬는다)."""
    fence = None
    for line in body_lines:
        s = line.strip()
        m = FENCE_OPEN.match(line)
        if m:
            fence = None if fence else m.group(1)[0]
            continue
        if fence or not s:
            continue
        if s.startswith("#") or s.startswith("|") or s.startswith(">"):
            continue
        if s.startswith("---") or s.startswith("==="):
            continue
        s = re.sub(r"^[-*+]\s+", "", s)
        s = re.sub(r"^\d+\.\s+", "", s)
        s = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", s)
        s = re.sub(r"`([^`]*)`", r"\1", s)
        s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)
        s = s.strip()
        if len(s) < 4:
            continue
        return (s[: maxlen - 1] + "…") if len(s) > maxlen else s

    # 산문이 없는 조각(체크리스트·표 위주) 폴백
    if headings:
        s = " / ".join(h[0] for h in headings[:3])
        return (s[: maxlen - 1] + "…") if len(s) > maxlen else s
    for line in body_lines:
        s = line.strip()
        if s.startswith("|"):
            cols = [c.strip() for c in s.strip("|").split("|") if c.strip() and set(c.strip()) != {"-"}]
            if cols:
                s = "표: " + " · ".join(cols[:5])
                return (s[: maxlen - 1] + "…") if len(s) > maxlen else s
    return "(요약 필요)"


# ══════════════════════════════════════════════════════════════════════════
# 조각 파일 쓰기 / 읽기
# ══════════════════════════════════════════════════════════════════════════

def yaml_scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if s == "" or re.search(r'[:#\-\[\]{}&*!|>%@`"\']', s) or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def render_part(part, body_lines, doc_id, trailing_newline):
    fm = [
        "---",
        "id: %s" % yaml_scalar("%s/%s" % (doc_id, part["name"])),
        "doc: %s" % yaml_scalar(doc_id),
        "part: %s" % part["n"],
        "title: %s" % yaml_scalar(part["title"]),
        "path: %s" % yaml_scalar(" > ".join(part["path"]) if part["path"] else "(문서 머리)"),
        "source_lines: %s" % yaml_scalar("%d-%d" % (part["lines"][0], part["lines"][1])),
        "keywords: [%s]" % ", ".join(yaml_scalar(k) for k in part["keywords"]),
        "prev: %s" % yaml_scalar(part["prev"] or ""),
        "next: %s" % yaml_scalar(part["next"] or ""),
        "---",
        "",
    ]
    return "\n".join(fm) + join_lines(body_lines, trailing_newline)


def strip_part_frontmatter(text):
    """조각 파일에서 doc-atomize가 붙인 프론트매터 블록만 제거한다.

    파일 선두의 첫 '---' 블록만 벗겨내므로, 본문이 '---'로 시작해도 안전하다.
    """
    if not text.startswith("---\n"):
        return text
    idx = text.find("\n---\n", 3)
    if idx == -1:
        return text
    rest = text[idx + len("\n---\n"):]
    # 프론트매터 다음의 구분 빈 줄 1개 제거
    if rest.startswith("\n"):
        rest = rest[1:]
    return rest


# ══════════════════════════════════════════════════════════════════════════
# 인덱스 생성
# ══════════════════════════════════════════════════════════════════════════

RETRIEVAL_BLOCK = """## 조회 프로토콜

1. 아래 **라우팅 힌트** / **키워드 역색인**에서 후보 조각 1~3개를 고른다.
2. 해당 `parts/*.md`만 Read 한다. **원본 전체를 읽지 않는다.**
3. 미스면 `Grep <패턴> parts/` → 적중 파일만 Read. 그래도 부족하면 `source_lines` 범위로 원본을 offset/limit Read.
"""


def build_index_md(meta):
    doc_id = meta["id"]
    parts = meta["parts"]
    lines = []

    lines.append("---")
    for key in ("doc", "title", "source", "source_dir", "mode", "parts_count",
                "source_lines", "generated", "tool"):
        if key in meta["index_frontmatter"]:
            lines.append("%s: %s" % (key, yaml_scalar(meta["index_frontmatter"][key])))
    lines.append("---")
    lines.append("")
    lines.append("# %s — 원자 인덱스" % meta.get("title", doc_id))
    lines.append("")
    lines.append("> 원본 `%s` (%d줄)을 조각 %d개로 무손실 분할한 검색 인덱스. 조각 본문은 원본 그대로이며, 합치면 원본과 동일하다."
                 % (meta["source"], meta["source_total_lines"], len(parts)))
    lines.append("")
    lines.append(RETRIEVAL_BLOCK)

    lines.append("## 라우팅 힌트")
    lines.append("")
    hints = meta.get("routing_hints") or []
    if hints:
        lines.append("| 이런 질문이면 | 조각 |")
        lines.append("|---|---|")
        for h in hints:
            targets = ", ".join("[%s](parts/%s.md)" % (t.split("-")[0], t) for t in h["parts"])
            lines.append("| %s | %s |" % (h["question"], targets))
    else:
        lines.append("_(아직 채워지지 않음 — metadata.json의 `routing_hints`에 추가한 뒤 `--reindex`)_")
    lines.append("")

    lines.append("## 목차")
    lines.append("")
    base_depth = meta.get("base_level", 2)
    # 인덱스는 통째로 읽히는 파일이다 — 조각이 많을수록 하위 헤딩 노출을 줄여
    # 인덱스 자체가 컨텍스트를 잡아먹는 것을 막는다(장 수준 헤딩은 항상 보존).
    n = len(parts)
    contains_budget = 8 if n <= 25 else (5 if n <= 60 else 0)
    for p in parts:
        depth = max(0, len(p["path"]) - 1)
        indent = "  " * min(depth, 4)
        stale = " ⚠️" if p.get("summary_stale") else ""
        lines.append("%s- **%s** %s → [`%s`](parts/%s.md) `L%d-%d` — %s%s" % (
            indent, p["n"], p["title"], p["name"], p["name"],
            p["lines"][0], p["lines"][1], p["summary"], stale))
        contains = p.get("contains") or []
        if contains:
            # 장(章) 수준 헤딩은 잘라내지 않는다 — 병합된 장이 목차에서 실종되면
            # 인덱스가 "이 문서에 그 장이 없다"고 거짓말하는 셈이 된다.
            top = [h for h in contains if h[1] <= base_depth]
            rest = [h for h in contains if h[1] > base_depth]
            budget = max(0, contains_budget - len(top))
            picked = top + rest[:budget]
            picked.sort(key=lambda h: contains.index(h))
            if picked:
                shown = " · ".join(h[0] for h in picked)
                hidden = len(contains) - len(picked)
                if hidden > 0:
                    shown += " · …(%d개 더, 본문 참조)" % hidden
                lines.append("%s  ↳ %s" % (indent, shown))
    lines.append("")

    inv = {}
    for p in parts:
        for kw in p["keywords"]:
            inv.setdefault(kw.lower(), (kw, []))[1].append(p["n"])
    lines.append("## 키워드 역색인")
    lines.append("")
    if inv:
        ranked = sorted(inv.values(), key=lambda kv: (-len(kv[1]), kv[0].lower()))[:80]
        for kw, ns in sorted(ranked, key=lambda kv: kv[0].lower()):
            lines.append("- `%s` → %s" % (kw, ", ".join(ns)))
    else:
        lines.append("_(키워드 없음)_")
    lines.append("")

    lines.append("## 주의")
    lines.append("")
    lines.append("- 조각 본문은 **원본 그대로**다. 상대경로 이미지/링크는 원본 디렉토리(`%s`) 기준으로 해석하라."
                 % meta["index_frontmatter"].get("source_dir", "?"))
    lines.append("- 원본이 바뀌면 `split_md.py update <dir>`로 갱신한다. 요약/키워드/라우팅 큐레이션은 `metadata.json`이 정본이며 `--reindex`로 이 파일에 반영된다.")
    lines.append("")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════
# split
# ══════════════════════════════════════════════════════════════════════════

def make_parts(lines, chunks, doc_id, slug_style):
    used = {}
    parts = []
    for i, ch in enumerate(chunks, start=1):
        slug = slugify(ch.title, slug_style)
        key = slug.lower()
        if key in used:
            used[key] += 1
            slug = "%s-%d" % (slug, used[key])
        else:
            used[key] = 1
        name = "%03d-%s" % (i, slug)
        body = lines[ch.start:ch.end]
        contains = inner_headings(body, ch.title)
        parts.append({
            "n": "%03d" % i,
            "name": name,
            "file": "parts/%s.md" % name,
            "title": ch.title,
            "level": ch.level,
            "path": ch.path,
            "kind": ch.kind,
            "lines": [ch.start + 1, ch.end],       # 1-based inclusive
            "nlines": ch.nlines,
            "body_sha256": hashlib.sha256("\n".join(body).encode("utf-8")).hexdigest(),
            "contains": contains,
            "keywords": extract_keywords(body, ch.title),
            "summary": draft_summary(body, headings=contains),
            "summary_source": "auto",
            "prev": None,
            "next": None,
        })
    for i, p in enumerate(parts):
        p["prev"] = parts[i - 1]["name"] if i > 0 else None
        p["next"] = parts[i + 1]["name"] if i + 1 < len(parts) else None
    return parts


def assert_coverage(parts, total_lines):
    expect = 1
    for p in parts:
        if p["lines"][0] != expect:
            raise SystemExit("FATAL: 라인 커버리지 불연속 — %s 가 L%d 에서 시작 (기대 L%d)"
                             % (p["name"], p["lines"][0], expect))
        expect = p["lines"][1] + 1
    if total_lines and expect != total_lines + 1:
        raise SystemExit("FATAL: 라인 커버리지 미달 — 마지막 L%d, 원본 %d줄" % (expect - 1, total_lines))


def cmd_split(args):
    src = os.path.abspath(args.source)
    if not os.path.isfile(src):
        raise SystemExit("ERROR: 원본을 찾을 수 없음: %s" % src)

    lines, smeta = read_source(src)
    headings = scan_headings(lines)
    base_level = args.base_level if args.base_level else detect_base_level(headings)
    limits = {"min_lines": args.min_lines, "max_lines": args.max_lines, "hard_max": args.hard_max}

    doc_id = args.doc_id or slugify(os.path.splitext(os.path.basename(src))[0], "ascii")
    out_dir = os.path.abspath(args.out)
    if os.path.exists(out_dir) and os.listdir(out_dir) and not args.force:
        raise SystemExit("ERROR: 출력 디렉토리가 비어있지 않음: %s (--force로 덮어쓰기)" % out_dir)

    chunks = build_chunks(lines, headings, limits, base_level)
    parts = make_parts(lines, chunks, doc_id, args.slug)
    assert_coverage(parts, len(lines))

    title = args.title
    if not title:
        h1 = next((h for h in headings if h[1] == 1), None)
        title = h1[2] if h1 else doc_id

    # 조각 파일 쓰기
    parts_dir = os.path.join(out_dir, "parts")
    if args.force and os.path.isdir(parts_dir):
        for fn in os.listdir(parts_dir):
            if fn.endswith(".md"):
                os.remove(os.path.join(parts_dir, fn))
    for i, p in enumerate(parts):
        body = lines[p["lines"][0] - 1:p["lines"][1]]
        last = (i == len(parts) - 1)
        write_text(os.path.join(out_dir, p["file"]),
                   render_part(p, body, doc_id, smeta["trailing_newline"] if last else True))

    meta = {
        "id": doc_id,
        "title": title,
        "source": src,
        "source_dir": os.path.dirname(src),
        "mode": args.mode,
        "tool": "doc-atomize %s" % TOOL_VERSION,
        "generated": args.today or date.today().isoformat(),
        "base_level": base_level,
        "limits": limits,
        "slug_style": args.slug,
        "source_total_lines": smeta["total_lines"],
        "source_bytes": smeta["bytes"],
        "source_sha256_raw": smeta["source_sha256_raw"],
        "source_sha256_normalized": smeta["source_sha256_normalized"],
        "line_ending": smeta["line_ending"],
        "trailing_newline": smeta["trailing_newline"],
        "routing_hints": [],
        "parts": parts,
    }
    meta["index_frontmatter"] = {
        "doc": doc_id,
        "title": title,
        "source": src,
        "source_dir": meta["source_dir"],
        "mode": args.mode,
        "parts_count": len(parts),
        "source_lines": smeta["total_lines"],
        "generated": meta["generated"],
        "tool": meta["tool"],
    }

    write_text(os.path.join(out_dir, "%s.metadata.json" % doc_id),
               json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    write_text(os.path.join(out_dir, "%s.index.md" % doc_id), build_index_md(meta))

    ok, msg = verify_dir(out_dir)
    print("분할 완료: %s" % out_dir)
    print("  문서 ID     : %s" % doc_id)
    print("  원본        : %s (%d줄, %.1f KB)" % (src, smeta["total_lines"], smeta["bytes"] / 1024.0))
    print("  기준 레벨   : H%d (자동판정)" % base_level if not args.base_level else
          "  기준 레벨   : H%d" % base_level)
    print("  조각        : %d개 (최소 %d줄 / 최대 %d줄 / 평균 %.0f줄)" % (
        len(parts), min(p["nlines"] for p in parts), max(p["nlines"] for p in parts),
        sum(p["nlines"] for p in parts) / float(len(parts))))
    index_bytes = os.path.getsize(os.path.join(out_dir, "%s.index.md" % doc_id))
    print("  인덱스      : %s.index.md (%.1f KB, 원본의 %.0f%%)"
          % (doc_id, index_bytes / 1024.0, 100.0 * index_bytes / max(1, smeta["bytes"])))
    print("  무손실 검증 : %s" % msg)
    if len(parts) > 80:
        print("  ⚠️ 조각이 %d개로 많습니다 — 인덱스가 무거워집니다. --max-lines를 키워 재분할을 검토하세요."
              % len(parts))
    return 0 if ok else 2


# ══════════════════════════════════════════════════════════════════════════
# verify
# ══════════════════════════════════════════════════════════════════════════

def load_meta(out_dir):
    cands = [f for f in os.listdir(out_dir) if f.endswith(".metadata.json")]
    if not cands:
        raise SystemExit("ERROR: metadata.json을 찾을 수 없음: %s" % out_dir)
    with open(os.path.join(out_dir, cands[0]), encoding="utf-8") as f:
        return json.load(f), os.path.join(out_dir, cands[0])


def verify_dir(out_dir):
    meta, _ = load_meta(out_dir)
    problems = []

    # 1) 재조립 sha256 대조
    bodies = []
    for p in meta["parts"]:
        path = os.path.join(out_dir, p["file"])
        if not os.path.isfile(path):
            problems.append("조각 누락: %s" % p["file"])
            continue
        with open(path, encoding="utf-8") as f:
            bodies.append(strip_part_frontmatter(f.read()))
    if not problems:
        joined = "".join(
            b if b.endswith("\n") or i == len(bodies) - 1 else b + "\n"
            for i, b in enumerate(bodies))
        got = hashlib.sha256(joined.encode("utf-8")).hexdigest()
        if got != meta["source_sha256_normalized"]:
            problems.append("재조립 sha256 불일치 (기대 %s / 실제 %s)"
                            % (meta["source_sha256_normalized"][:12], got[:12]))

    # 2) 라인 커버리지
    try:
        assert_coverage(meta["parts"], meta["source_total_lines"])
    except SystemExit as e:
        problems.append(str(e))

    # 3) 고아 파일
    parts_dir = os.path.join(out_dir, "parts")
    listed = {p["file"] for p in meta["parts"]}
    if os.path.isdir(parts_dir):
        for fn in sorted(os.listdir(parts_dir)):
            if fn.endswith(".md") and ("parts/%s" % fn) not in listed:
                problems.append("메타에 없는 고아 조각: parts/%s" % fn)

    # 4) 인덱스 링크
    index_path = os.path.join(out_dir, "%s.index.md" % meta["id"])
    if not os.path.isfile(index_path):
        problems.append("인덱스 파일 없음: %s.index.md" % meta["id"])
    else:
        with open(index_path, encoding="utf-8") as f:
            idx = f.read()
        for link in re.findall(r"\(parts/([^)]+\.md)\)", idx):
            if not os.path.isfile(os.path.join(parts_dir, link)):
                problems.append("인덱스 깨진 링크: parts/%s" % link)

    # 5) 원본 드리프트 (경고)
    warn = ""
    if os.path.isfile(meta["source"]):
        with open(meta["source"], "rb") as f:
            cur = hashlib.sha256(f.read()).hexdigest()
        if cur != meta["source_sha256_raw"]:
            warn = " (경고: 원본이 분할 이후 변경됨 — update 필요)"
    else:
        warn = " (경고: 원본 경로 없음 — in-place 모드면 정상)"

    if problems:
        return False, "실패 %d건: %s" % (len(problems), "; ".join(problems[:5]))
    return True, "OK — 재조립 sha256 일치, 커버리지 %d줄 완전%s" % (meta["source_total_lines"], warn)


def cmd_verify(args):
    ok, msg = verify_dir(os.path.abspath(args.dir))
    print(("PASS: " if ok else "FAIL: ") + msg)
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# reindex / update
# ══════════════════════════════════════════════════════════════════════════

def cmd_reindex(args):
    out_dir = os.path.abspath(args.dir)
    meta, _ = load_meta(out_dir)
    write_text(os.path.join(out_dir, "%s.index.md" % meta["id"]), build_index_md(meta))
    print("인덱스 재생성: %s/%s.index.md (조각 %d개)" % (out_dir, meta["id"], len(meta["parts"])))
    return 0


def cmd_update(args):
    out_dir = os.path.abspath(args.dir)
    old, meta_path = load_meta(out_dir)
    src = os.path.abspath(args.source) if args.source else old["source"]
    if not os.path.isfile(src):
        raise SystemExit("ERROR: 원본을 찾을 수 없음: %s (--source로 새 경로 지정)" % src)

    with open(src, "rb") as f:
        cur_sha = hashlib.sha256(f.read()).hexdigest()
    if cur_sha == old["source_sha256_raw"] and not args.force:
        print("변경 없음 (sha256 동일) — 갱신 생략")
        return 0

    lines, smeta = read_source(src)
    headings = scan_headings(lines)
    base_level = old.get("base_level") or detect_base_level(headings)
    limits = old.get("limits") or {"min_lines": DEFAULT_MIN_LINES,
                                   "max_lines": DEFAULT_MAX_LINES,
                                   "hard_max": DEFAULT_HARD_MAX}
    chunks = build_chunks(lines, headings, limits, base_level)
    parts = make_parts(lines, chunks, old["id"], old.get("slug_style", "auto"))
    assert_coverage(parts, len(lines))

    # 큐레이션 승계: 슬러그(번호 제외) 기준 매칭
    def bare(name):
        return re.sub(r"^\d{3}-", "", name)

    old_by_slug = {bare(p["name"]): p for p in old["parts"]}
    added, changed, kept = [], [], []
    for p in parts:
        o = old_by_slug.get(bare(p["name"]))
        if not o:
            added.append(p["name"])
            continue
        if o.get("summary_source") == "curated":
            p["summary"] = o["summary"]
            p["summary_source"] = "curated"
            if o.get("body_sha256") != p["body_sha256"]:
                p["summary_stale"] = True
        if o.get("keywords_source") == "curated":
            p["keywords"] = o["keywords"]
            p["keywords_source"] = "curated"
        (changed if o.get("body_sha256") != p["body_sha256"] else kept).append(p["name"])
    removed = [n for n in old_by_slug if n not in {bare(p["name"]) for p in parts}]

    parts_dir = os.path.join(out_dir, "parts")
    if os.path.isdir(parts_dir):
        for fn in os.listdir(parts_dir):
            if fn.endswith(".md"):
                os.remove(os.path.join(parts_dir, fn))
    for i, p in enumerate(parts):
        body = lines[p["lines"][0] - 1:p["lines"][1]]
        last = (i == len(parts) - 1)
        write_text(os.path.join(out_dir, p["file"]),
                   render_part(p, body, old["id"], smeta["trailing_newline"] if last else True))

    new_meta = dict(old)
    new_meta.update({
        "source": src,
        "source_dir": os.path.dirname(src),
        "generated": args.today or date.today().isoformat(),
        "source_total_lines": smeta["total_lines"],
        "source_bytes": smeta["bytes"],
        "source_sha256_raw": smeta["source_sha256_raw"],
        "source_sha256_normalized": smeta["source_sha256_normalized"],
        "line_ending": smeta["line_ending"],
        "trailing_newline": smeta["trailing_newline"],
        "parts": parts,
    })
    fm = dict(new_meta.get("index_frontmatter") or {})
    fm.update({"source": src, "source_dir": new_meta["source_dir"],
               "parts_count": len(parts), "source_lines": smeta["total_lines"],
               "generated": new_meta["generated"]})
    new_meta["index_frontmatter"] = fm

    write_text(meta_path, json.dumps(new_meta, ensure_ascii=False, indent=2) + "\n")
    write_text(os.path.join(out_dir, "%s.index.md" % old["id"]), build_index_md(new_meta))

    ok, msg = verify_dir(out_dir)
    print("갱신 완료: %s" % out_dir)
    print("  추가 %d / 변경 %d / 유지 %d / 삭제 %d" % (len(added), len(changed), len(kept), len(removed)))
    for n in added[:10]:
        print("    + %s" % n)
    for n in changed[:10]:
        print("    ~ %s" % n)
    for n in removed[:10]:
        print("    - %s" % n)
    stale = [p["name"] for p in parts if p.get("summary_stale")]
    if stale:
        print("  ⚠️ 요약 재검토 필요: %s" % ", ".join(stale[:10]))
    print("  무손실 검증 : %s" % msg)
    return 0 if ok else 2


# ══════════════════════════════════════════════════════════════════════════

def main(argv=None):
    ap = argparse.ArgumentParser(prog="split_md.py", description="doc-atomize 무손실 마크다운 분할기")
    sub = ap.add_subparsers(dest="cmd")

    sp = sub.add_parser("split", help="신규 분할")
    sp.add_argument("source")
    sp.add_argument("--out", required=True, help="출력 디렉토리 (<doc-id>/)")
    sp.add_argument("--doc-id")
    sp.add_argument("--title")
    sp.add_argument("--min-lines", type=int, default=DEFAULT_MIN_LINES)
    sp.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    sp.add_argument("--hard-max", type=int, default=DEFAULT_HARD_MAX)
    sp.add_argument("--base-level", type=int, choices=[1, 2, 3, 4], default=None)
    sp.add_argument("--slug", choices=["auto", "ascii"], default="auto")
    sp.add_argument("--mode", choices=["derived", "in-place"], default="derived")
    sp.add_argument("--today", help="생성일 고정(재현 테스트용)")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_split)

    vp = sub.add_parser("verify", help="무손실·구조 검증")
    vp.add_argument("dir")
    vp.set_defaults(func=cmd_verify)

    rp = sub.add_parser("reindex", help="metadata.json → index.md 재생성")
    rp.add_argument("dir")
    rp.set_defaults(func=cmd_reindex)

    up = sub.add_parser("update", help="원본 변경분 반영")
    up.add_argument("dir")
    up.add_argument("--source", help="원본 경로가 바뀐 경우")
    up.add_argument("--today")
    up.add_argument("--force", action="store_true")
    up.set_defaults(func=cmd_update)

    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        ap.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
