#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""manual-digest — PDF에서 필요한 부분만 뽑아내는 추출기 (PyMuPDF 기반).

큰 PDF를 통째로 읽지 않고 "먼저 지도를 보고, 필요한 페이지만 연다"를 위한 도구다.
목차(toc)로 문서의 뼈대를 훑고, 검색(find)으로 어느 페이지에 있는지만 먼저 확인한 뒤,
그 페이지만 text/tables 로 연다.

서브커맨드
  info   <pdf>                       메타데이터·페이지 수·목차 유무·텍스트 레이어 표본 판정
  toc    <pdf>                       목차 (PDF 내장 outline, 없으면 글꼴 크기 휴리스틱)
  text   <pdf> --pages "7-12,82"     지정 페이지 본문 (혼합 범위)
  tables <pdf> --pages "6"           지정 페이지의 표를 마크다운 표로
  find   <pdf> "<query>"             대소문자 무시 검색 → 페이지 열지도 (본문 미포함)
  render <pdf> --pages "1" --out DIR 페이지를 PNG 로 (육안 판독 전용)

의존성: Python 3.8+ 표준 라이브러리 + PyMuPDF(`pip install pymupdf`).
PyMuPDF 가 없으면 exit 2 로 끝낸다 — 호출하는 쪽은 이 코드를 보고 pdftotext 로 내려간다.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

try:
    import fitz  # PyMuPDF
except ImportError:  # PyMuPDF 미설치 — 호출자가 exit 2 를 보고 폴백한다
    fitz = None

TOOL_VERSION = "1.0.0"

EXIT_OK = 0
EXIT_ERROR = 1        # 파일 없음·페이지 범위 초과 등 사용자 오류
EXIT_NO_PYMUPDF = 2   # PyMuPDF 미설치 → L2(pdftotext) 폴백 신호

# 텍스트 레이어 판정: 표본 페이지의 평균 글자 수가 이 값 미만이면 스캔본 의심
SCAN_SUSPECT_CHARS = 50

# 휴리스틱 목차: 번호 절 패턴 (예: "3 개요", "3.1.2 설정 방법")
SECTION_NUM = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+\S")

# 번호만 있고 제목이 다음 줄로 넘어간 경우 (예: "10.1." + 줄바꿈 + "Data Log")
SECTION_NUM_ONLY = re.compile(r"^(\d+(?:\.\d+)*)\.?\s*$")

# 휴리스틱 목차: 본문 글꼴 + 이 값(pt) 이상이어야 제목 후보
DEFAULT_SIZE_DELTA = 2.0


# ── 공통 유틸 ──────────────────────────────────────────────────────────────

def die(msg, code=EXIT_ERROR):
    """오류 메시지를 stderr 에 쓰고 종료."""
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def require_fitz():
    """PyMuPDF 가용성 확인. 없으면 설치 안내 후 exit 2."""
    if fitz is None:
        print("ERROR: PyMuPDF(fitz)를 불러올 수 없습니다.", file=sys.stderr)
        print("       설치: pip install pymupdf", file=sys.stderr)
        print("       설치가 어려우면 pdftotext -layout 경로(L2)로 진행하십시오.",
              file=sys.stderr)
        sys.exit(EXIT_NO_PYMUPDF)


def open_pdf(path):
    """PDF 를 열어 Document 반환. 없거나 열 수 없으면 exit 1."""
    require_fitz()
    if not os.path.isfile(path):
        die(f"파일이 없습니다: {path}")
    try:
        return fitz.open(path)
    except Exception as e:  # 손상·암호화 등
        die(f"PDF 를 열 수 없습니다: {path} ({e})")


def parse_pages(spec, page_count):
    """'7-12,28-30,82' → [6,7,...,11,27,28,29,81] (0-based 인덱스, 오름차순 중복 제거).

    입력은 1-based 물리 페이지. 범위를 벗어나면 exit 1.
    """
    if not spec or not spec.strip():
        die("--pages 가 비었습니다 (예: \"7-12,28-30,82\")")
    out = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", chunk)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a > b:
                die(f"페이지 범위가 거꾸로입니다: {chunk}")
            rng = range(a, b + 1)
        elif chunk.isdigit():
            rng = [int(chunk)]
        else:
            die(f"페이지 표기를 해석할 수 없습니다: {chunk!r} (예: \"7-12,28-30,82\")")
        for p in rng:
            if p < 1 or p > page_count:
                die(f"페이지 범위 초과: {p} (이 PDF 는 1~{page_count})")
            out.append(p - 1)
    if not out:
        die("선택된 페이지가 없습니다")
    return sorted(set(out))


def page_label(doc, index):
    """물리 페이지(0-based)의 인쇄 표시 라벨. 없으면 None."""
    try:
        label = doc[index].get_label()
    except Exception:
        return None
    return label or None


def has_page_labels(doc):
    """페이지 라벨(인쇄 표시 페이지 번호) 정의 여부."""
    try:
        return bool(doc.get_page_labels())
    except Exception:
        return False


def emit(data, text_lines, as_json):
    """--json 이면 JSON, 아니면 텍스트 줄들을 출력."""
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for line in text_lines:
            print(line)


# ── info ───────────────────────────────────────────────────────────────────

def sample_indices(page_count, want=5):
    """텍스트 레이어 표본용으로 서로 떨어진 페이지 인덱스를 고른다."""
    if page_count <= want:
        return list(range(page_count))
    picks = {0, page_count - 1}
    for k in range(1, want - 1):
        picks.add(page_count * k // (want - 1))
    return sorted(i for i in picks if 0 <= i < page_count)


def cmd_info(args):
    doc = open_pdf(args.pdf)
    meta = doc.metadata or {}
    try:
        toc = doc.get_toc(simple=True)
    except Exception:
        toc = []

    samples = []
    for i in sample_indices(len(doc)):
        try:
            chars = len(doc[i].get_text("text").strip())
        except Exception:
            chars = 0
        samples.append({"page": i + 1, "chars": chars})
    avg = sum(s["chars"] for s in samples) / len(samples) if samples else 0
    text_layer = "텍스트 있음" if avg >= SCAN_SUSPECT_CHARS else "스캔본 의심"

    data = {
        "path": os.path.abspath(args.pdf),
        "page_count": len(doc),
        "encrypted": bool(doc.is_encrypted),
        "metadata": {k: meta.get(k) for k in
                     ("title", "author", "subject", "keywords",
                      "creator", "producer", "creationDate", "modDate")},
        "outline": {"present": bool(toc), "items": len(toc)},
        "page_labels": has_page_labels(doc),
        "text_layer": {"verdict": text_layer,
                       "avg_chars_per_sample_page": round(avg, 1),
                       "samples": samples},
    }
    doc.close()

    m = data["metadata"]
    lines = [
        f"파일: {data['path']}",
        f"페이지 수: {data['page_count']}",
        f"제목: {m.get('title') or '(없음)'}",
        f"저자: {m.get('author') or '(없음)'}",
        f"생성 도구: {m.get('producer') or '(없음)'} / {m.get('creator') or '(없음)'}",
        f"생성일: {m.get('creationDate') or '(없음)'}  수정일: {m.get('modDate') or '(없음)'}",
        f"암호화: {'예' if data['encrypted'] else '아니오'}",
        f"내장 목차(outline): {'있음 (%d항목)' % data['outline']['items'] if toc else '없음 → toc --heuristic 사용'}",
        f"페이지 라벨(인쇄 표시 번호): {'있음' if data['page_labels'] else '없음'}",
        f"텍스트 레이어: {text_layer} "
        f"(표본 {len(samples)}p 평균 {data['text_layer']['avg_chars_per_sample_page']}자)",
        "  표본: " + ", ".join(f"p.{s['page']}={s['chars']}자" for s in samples),
    ]
    emit(data, lines, args.json)
    return EXIT_OK


# ── toc ────────────────────────────────────────────────────────────────────

def body_font_size(doc, max_pages=None):
    """본문 글꼴 크기 = 글자 수로 가중한 최빈 span 크기(0.1pt 반올림)."""
    counter = Counter()
    pages = range(len(doc)) if max_pages is None else range(min(max_pages, len(doc)))
    for i in pages:
        try:
            d = doc[i].get_text("dict")
        except Exception:
            continue
        for block in d.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    txt = (span.get("text") or "").strip()
                    if txt:
                        counter[round(span.get("size", 0.0), 1)] += len(txt)
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def heuristic_toc(doc, min_size=None):
    """내장 목차가 없는 PDF 의 절 구조를 복원한다.

    판정 기준 두 가지를 모두 만족하는 줄만 제목으로 본다.
      ① 글꼴 크기가 본문보다 크다 (기본: 본문 + 2pt 이상)
      ② 번호 절 패턴으로 시작한다 (예: "3 개요", "3.1.2 설정")

    목차 페이지의 항목은 대개 본문 글꼴이라 ①에서 자동으로 걸러진다.
    번호와 제목이 두 줄로 나뉜 경우("10.1." 다음 줄에 "Data Log")는 이어 붙인다.
    반환: (항목 리스트, 본문 글꼴 크기, 적용 임계값)
    """
    body = body_font_size(doc)
    if body is None:
        return [], None, None
    threshold = float(min_size) if min_size is not None else body + DEFAULT_SIZE_DELTA

    items = []
    for i in range(len(doc)):
        try:
            d = doc[i].get_text("dict")
        except Exception:
            continue
        # 이 페이지에서 제목 글꼴 크기를 넘는 줄만 순서대로 모은다
        big = []
        for block in d.get("blocks", []):
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s.get("text") or "" for s in spans).strip()
                if not text:
                    continue
                size = max(round(s.get("size", 0.0), 1) for s in spans)
                if size >= threshold:
                    big.append((text, size))

        skip_next = False
        for j, (text, size) in enumerate(big):
            if skip_next:
                skip_next = False
                continue
            m = SECTION_NUM.match(text)
            if m:
                num, title = m.group(1), text
            else:
                m2 = SECTION_NUM_ONLY.match(text)
                if not m2 or j + 1 >= len(big):
                    continue
                nxt = big[j + 1][0]
                if SECTION_NUM.match(nxt) or SECTION_NUM_ONLY.match(nxt):
                    continue  # 다음 줄도 번호면 제목이 아니다
                num, title = m2.group(1), f"{text} {nxt}".strip()
                skip_next = True
            items.append({"level": num.count(".") + 1, "title": title,
                          "page": i + 1, "size": size})
    return items, body, threshold


def cmd_toc(args):
    doc = open_pdf(args.pdf)
    try:
        outline = doc.get_toc(simple=True)
    except Exception:
        outline = []

    use_heuristic = args.heuristic or not outline
    labels_on = has_page_labels(doc)

    if use_heuristic:
        items, body, threshold = heuristic_toc(doc, args.min_size)
        if body is None:
            doc.close()
            die("텍스트를 찾을 수 없어 목차를 복원할 수 없습니다 "
                "(스캔본 가능성 — info 로 텍스트 레이어를 먼저 확인하십시오)")
        source = "heuristic"
        header = (f"경로: 휴리스틱 (본문 글꼴 {body}pt, 제목 임계 {round(threshold, 1)}pt) "
                  f"— {len(items)}항목")
    else:
        items = [{"level": lvl, "title": title, "page": page}
                 for lvl, title, page in outline]
        source = "outline"
        header = f"경로: PDF 내장 outline — {len(items)}항목"

    if labels_on:
        for it in items:
            it["label"] = page_label(doc, it["page"] - 1)
    doc.close()

    data = {"path": os.path.abspath(args.pdf), "source": source,
            "count": len(items), "items": items}
    if use_heuristic:
        data["body_font_size"] = body
        data["size_threshold"] = round(threshold, 1)

    lines = [header]
    for it in items:
        indent = "  " * (it["level"] - 1)
        loc = f"p.{it['page']}"
        if it.get("label") and it["label"] != str(it["page"]):
            loc += f" (표시 {it['label']})"
        lines.append(f"{indent}{it['title']}  …  {loc}")
    emit(data, lines, args.json)
    return EXIT_OK


# ── text ───────────────────────────────────────────────────────────────────

def cmd_text(args):
    doc = open_pdf(args.pdf)
    idxs = parse_pages(args.pages, len(doc))
    pages = []
    lines = []
    for i in idxs:
        body = doc[i].get_text("text", sort=True) if args.sort else doc[i].get_text("text")
        pages.append({"page": i + 1, "text": body})
        lines.append(f"--- p.{i + 1} ---")
        lines.append(body.rstrip("\n"))
    doc.close()
    emit({"path": os.path.abspath(args.pdf), "pages": pages}, lines, args.json)
    return EXIT_OK


# ── tables ─────────────────────────────────────────────────────────────────

def md_escape(cell):
    """마크다운 표 셀로 안전하게: None→빈칸, 파이프 이스케이프, 줄바꿈 제거."""
    if cell is None:
        return ""
    return str(cell).replace("|", "\\|").replace("\n", " ").strip()


def table_to_markdown(rows):
    """셀 배열(행 리스트)을 마크다운 표 문자열 줄 리스트로."""
    if not rows:
        return []
    width = max(len(r) for r in rows)
    out = []
    for ri, row in enumerate(rows):
        cells = [md_escape(c) for c in row] + [""] * (width - len(row))
        out.append("| " + " | ".join(cells) + " |")
        if ri == 0:
            out.append("|" + "|".join([" --- "] * width) + "|")
    return out


def cmd_tables(args):
    doc = open_pdf(args.pdf)
    idxs = parse_pages(args.pages, len(doc))
    result = []
    lines = []
    for i in idxs:
        page = doc[i]
        try:
            found = page.find_tables()
            tables = [t.extract() for t in found.tables]
        except AttributeError:
            doc.close()
            die("이 PyMuPDF 버전에는 find_tables() 가 없습니다 "
                "(1.23 이상 필요: pip install -U pymupdf)")
        except Exception as e:
            tables = []
            lines.append(f"--- p.{i + 1} --- 표 검출 실패: {e}")
        result.append({"page": i + 1, "tables": tables})
        if not tables:
            lines.append(f"--- p.{i + 1} --- 표 없음")
            continue
        for ti, rows in enumerate(tables, 1):
            nrow = len(rows)
            ncol = max((len(r) for r in rows), default=0)
            lines.append(f"--- p.{i + 1} 표 {ti}/{len(tables)} ({nrow}행 x {ncol}열) ---")
            lines.extend(table_to_markdown(rows))
            lines.append("")
    doc.close()
    emit({"path": os.path.abspath(args.pdf), "pages": result}, lines, args.json)
    return EXIT_OK


# ── find ───────────────────────────────────────────────────────────────────

def cmd_find(args):
    doc = open_pdf(args.pdf)
    needle = args.query.lower()
    if not needle:
        doc.close()
        die("검색어가 비었습니다")

    hits = []
    total = 0
    for i in range(len(doc)):
        try:
            raw = doc[i].get_text("text")
        except Exception:
            continue
        low = raw.lower()
        count = low.count(needle)
        if not count:
            continue
        total += count
        entry = {"page": i + 1, "matches": count}
        if args.context:
            snippets = []
            start = 0
            while len(snippets) < count:
                pos = low.find(needle, start)
                if pos < 0:
                    break
                a = max(0, pos - args.context)
                b = min(len(raw), pos + len(needle) + args.context)
                snippets.append(" ".join(raw[a:b].split()))
                start = pos + len(needle)
            entry["snippets"] = snippets
        hits.append(entry)
    doc.close()

    shown = hits[:args.max] if args.max else hits
    data = {"path": os.path.abspath(args.pdf), "query": args.query,
            "pages_with_match": len(hits), "total_matches": total,
            "shown": len(shown), "hits": shown}

    lines = [f"검색어: {args.query!r} — {len(hits)}개 페이지, 총 {total}건"]
    for h in shown:
        lines.append(f"p.{h['page']}: {h['matches']}건")
        for sn in h.get("snippets", []):
            lines.append(f"    … {sn} …")
    if args.max and len(hits) > len(shown):
        lines.append(f"(--max {args.max} 로 {len(hits) - len(shown)}개 페이지 생략)")
    emit(data, lines, args.json)
    return EXIT_OK


# ── render ─────────────────────────────────────────────────────────────────

def cmd_render(args):
    doc = open_pdf(args.pdf)
    idxs = parse_pages(args.pages, len(doc))
    try:
        os.makedirs(args.out, exist_ok=True)
    except OSError as e:
        doc.close()
        die(f"출력 디렉토리를 만들 수 없습니다: {args.out} ({e})")

    stem = re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.splitext(os.path.basename(args.pdf))[0])
    files = []
    for i in idxs:
        pix = doc[i].get_pixmap(dpi=args.dpi)
        path = os.path.join(args.out, f"{stem}-p{i + 1:04d}.png")
        pix.save(path)
        files.append({"page": i + 1, "file": os.path.abspath(path),
                      "width": pix.width, "height": pix.height})
    doc.close()

    lines = [f"{len(files)}개 페이지를 {args.dpi}dpi PNG 로 저장했습니다."]
    lines += [f"p.{f['page']}: {f['file']} ({f['width']}x{f['height']})" for f in files]
    emit({"path": os.path.abspath(args.pdf), "dpi": args.dpi, "files": files},
         lines, args.json)
    return EXIT_OK


# ══════════════════════════════════════════════════════════════════════════

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="pdf_extract.py",
        description="manual-digest PDF 추출기 (PyMuPDF) — 필요한 페이지만 뽑는다")
    ap.add_argument("--version", action="version", version=f"pdf_extract.py {TOOL_VERSION}")
    sub = ap.add_subparsers(dest="cmd")

    ip = sub.add_parser("info", help="메타데이터·페이지 수·목차 유무·텍스트 레이어 표본 판정")
    ip.add_argument("pdf")
    ip.add_argument("--json", action="store_true", help="JSON 출력")
    ip.set_defaults(func=cmd_info)

    tp = sub.add_parser("toc", help="목차 — 내장 outline 우선, 없으면 글꼴 크기 휴리스틱")
    tp.add_argument("pdf")
    tp.add_argument("--heuristic", action="store_true",
                    help="내장 outline 이 있어도 휴리스틱으로 복원")
    tp.add_argument("--min-size", type=float,
                    help="제목 판정 글꼴 크기 임계값(pt) 직접 지정 (기본: 본문+2pt)")
    tp.add_argument("--json", action="store_true", help="JSON 출력")
    tp.set_defaults(func=cmd_toc)

    xp = sub.add_parser("text", help="지정 페이지 본문 추출 (혼합 범위)")
    xp.add_argument("pdf")
    xp.add_argument("--pages", required=True, metavar="SPEC",
                    help='1-based 물리 페이지 (예: "7-12,28-30,82")')
    xp.add_argument("--sort", action="store_true",
                    help="읽기 순서로 정렬 (다단 조판에서 유용)")
    xp.add_argument("--json", action="store_true", help="JSON 출력")
    xp.set_defaults(func=cmd_text)

    bp = sub.add_parser("tables", help="지정 페이지의 표를 마크다운 표로 추출")
    bp.add_argument("pdf")
    bp.add_argument("--pages", required=True, metavar="SPEC",
                    help='1-based 물리 페이지 (예: "6,42-43")')
    bp.add_argument("--json", action="store_true", help="셀 배열 JSON 출력")
    bp.set_defaults(func=cmd_tables)

    fp = sub.add_parser("find", help="대소문자 무시 검색 → 페이지 열지도 (기본은 본문 미포함)")
    fp.add_argument("pdf")
    fp.add_argument("query")
    fp.add_argument("--context", type=int, metavar="N",
                    help="매치 주변 N자 스니펫도 출력")
    fp.add_argument("--max", type=int, metavar="N", help="표시할 페이지 수 상한")
    fp.add_argument("--json", action="store_true", help="JSON 출력")
    fp.set_defaults(func=cmd_find)

    rp = sub.add_parser("render", help="페이지를 PNG 로 렌더링 (육안 판독 전용)")
    rp.add_argument("pdf")
    rp.add_argument("--pages", required=True, metavar="SPEC",
                    help='1-based 물리 페이지 (예: "1,5-6")')
    rp.add_argument("--dpi", type=int, default=110, help="해상도 (기본 110)")
    rp.add_argument("--out", required=True, metavar="DIR", help="PNG 출력 디렉토리")
    rp.add_argument("--json", action="store_true", help="JSON 출력")
    rp.set_defaults(func=cmd_render)

    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        ap.print_help()
        return EXIT_ERROR
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
