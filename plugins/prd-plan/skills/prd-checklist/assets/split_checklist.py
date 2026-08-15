#!/usr/bin/env python3
"""체크리스트를 마일스톤 단위 파일로 나눈다.

체크리스트는 자주 바뀌고 전수 집계로 읽히는 문서라 doc-atomize로 분할하지 않는다.
대신 커지면 마일스톤 단위로 파일을 나눈다 — 이 스크립트가 그 작업을 결정적으로 처리한다.

산출 구조:
    CHECKLIST-<slug>.md          인덱스 — 프론트매터·읽는 방법·선행 관계·파일 목록·진척 요약
    CHECKLIST-<slug>-M1.md       M1 항목 + M1에 해당하는 차단 표 행
    CHECKLIST-<slug>-M2.md       ...

CHK ID는 **건드리지 않는다**. 연번은 파일을 넘어 그대로 이어지며, 그래야
check_traceability.py 가 --checklist 를 여러 번 받아 전체로 집계할 수 있다.

사용:
    python3 split_checklist.py <체크리스트.md> [--out DIR] [--dry-run] [--force]

종료 코드:
    0  성공        1  검증 실패(항목 손실 등)        2  사용법 오류

Python 표준 라이브러리만 사용한다.
"""

import argparse
import os
import re
import sys

RE_CHK = re.compile(r"\*\*(CHK-\d{3,4})\*\*")
RE_MILESTONE = re.compile(r"^##\s+(M\d+)\s*[—\-–]\s*(.*)$")
RE_H2 = re.compile(r"^##\s+")
RE_FM = re.compile(r"^---\s*$")
# 차단 표의 CHK 참조:  | CHK-008~012 | ... |  또는  | CHK-045, CHK-046 | ... |
RE_CHK_ANY = re.compile(r"CHK-(\d{3,4})")


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().splitlines()


def parse(lines):
    """문서를 프론트매터 / 머리말 / 마일스톤 블록 / 꼬리 섹션으로 가른다."""
    front, body_start = [], 0
    if lines and RE_FM.match(lines[0]):
        for i in range(1, len(lines)):
            if RE_FM.match(lines[i]):
                front = lines[1:i]
                body_start = i + 1
                break

    preamble, milestones, tail = [], [], []
    cur = None          # {"id","title","lines"}
    section = "pre"
    for line in lines[body_start:]:
        m = RE_MILESTONE.match(line)
        if m:
            if cur:
                milestones.append(cur)
            cur = {"id": m.group(1), "title": m.group(2).strip(), "lines": [line]}
            section = "ms"
            continue
        if section == "ms" and RE_H2.match(line) and not RE_MILESTONE.match(line):
            milestones.append(cur)
            cur = None
            section = "tail"
            tail.append(line)
            continue
        if section == "pre":
            preamble.append(line)
        elif section == "ms":
            cur["lines"].append(line)
        else:
            tail.append(line)
    if cur:
        milestones.append(cur)
    return front, preamble, milestones, tail


def split_tail_by_milestone(tail, owner_of):
    """꼬리 섹션 중 차단 표 행을 소속 마일스톤별로 나눈다. (공통 꼬리, {ms: [행]})"""
    common, per = [], {}
    in_block_table = False
    for line in tail:
        if RE_H2.match(line):
            in_block_table = "차단" in line
            common.append(line)
            continue
        if in_block_table and line.strip().startswith("|"):
            ids = RE_CHK_ANY.findall(line)
            owners = {owner_of.get("CHK-" + i.zfill(3)) for i in ids}
            owners.discard(None)
            if len(owners) == 1:
                per.setdefault(owners.pop(), []).append(line)
                continue
        common.append(line)
    return common, per


def fm_set(front, key, value):
    out, done = [], False
    for line in front:
        if line.split(":")[0].strip() == key:
            out.append("{}: {}".format(key, value))
            done = True
        else:
            out.append(line)
    if not done:
        out.append("{}: {}".format(key, value))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="체크리스트를 마일스톤 단위 파일로 분리")
    ap.add_argument("checklist")
    ap.add_argument("--out", help="출력 디렉토리 (기본: 원본과 같은 위치)")
    ap.add_argument("--dry-run", action="store_true", help="쓰지 않고 계획만 출력")
    ap.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기 허용")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.checklist):
        print("파일을 찾을 수 없음: {}".format(args.checklist), file=sys.stderr)
        return 2

    lines = read(args.checklist)
    front, preamble, milestones, tail = parse(lines)
    if not milestones:
        print("마일스톤 구획(## M1 — 제목)을 찾지 못했습니다. 분리할 수 없습니다.", file=sys.stderr)
        return 2

    total_before = len(RE_CHK.findall("\n".join(lines)))
    owner_of = {}
    for ms in milestones:
        for cid in RE_CHK.findall("\n".join(ms["lines"])):
            owner_of[cid] = ms["id"]

    common_tail, per_tail = split_tail_by_milestone(tail, owner_of)

    out_dir = args.out or os.path.dirname(os.path.abspath(args.checklist))
    base = os.path.basename(args.checklist)
    stem = base[:-3] if base.endswith(".md") else base

    files = []
    for ms in milestones:
        body = list(ms["lines"])
        extra = per_tail.get(ms["id"], [])
        if extra:
            body += ["", "## 차단 항목 (이 마일스톤)", ""] + extra
        f = fm_set(list(front), "milestone", ms["id"])
        f = fm_set(f, "parent", stem)
        count = len(RE_CHK.findall("\n".join(body)))
        files.append({
            "path": os.path.join(out_dir, "{}-{}.md".format(stem, ms["id"])),
            "text": "---\n" + "\n".join(f) + "\n---\n" + "\n".join(body).rstrip() + "\n",
            "count": count, "id": ms["id"], "title": ms["title"],
        })

    idx_lines = list(preamble)
    idx_lines += ["## 마일스톤 파일", "",
                  "이 문서는 **인덱스**다. 항목은 아래 파일에 있고 CHK 연번은 파일을 넘어 이어진다.", "",
                  "| 마일스톤 | 파일 | 항목 수 |", "|---|---|---|"]
    for f in files:
        idx_lines.append("| {} — {} | [`{}`]({}) | {} |".format(
            f["id"], f["title"], os.path.basename(f["path"]), os.path.basename(f["path"]), f["count"]))
    idx_lines += ["", "전체 항목 {}건. 검증·진척 집계는 **모든 파일을 함께** 넘긴다:".format(total_before), "",
                  "```bash", "python3 check_traceability.py --prd <PRD> --plan <PLAN> \\"]
    for f in files:
        idx_lines.append("    --checklist {} \\".format(os.path.basename(f["path"])))
    idx_lines += ["    --status", "```", ""] + common_tail

    index = {"path": os.path.join(out_dir, base),
             "text": "---\n" + "\n".join(fm_set(list(front), "parts", len(files))) + "\n---\n"
                     + "\n".join(idx_lines).rstrip() + "\n"}

    total_after = sum(f["count"] for f in files)
    if total_after != total_before:
        print("검증 실패: 항목 수 불일치 (분리 전 {} / 분리 후 {})".format(total_before, total_after), file=sys.stderr)
        return 1
    dup = len(owner_of) != total_before
    if dup:
        print("검증 실패: CHK ID 중복 (고유 {} / 전체 {})".format(len(owner_of), total_before), file=sys.stderr)
        return 1

    print("분리 계획: {} → 인덱스 1 + 마일스톤 {}개".format(base, len(files)))
    for f in files:
        print("  {:>3}  {:<45} {:>4}건".format(f["id"], os.path.basename(f["path"]), f["count"]))
    print("  항목 보존: {} / {} (중복 0)".format(total_after, total_before))

    if args.dry_run:
        print("\n--dry-run — 파일을 쓰지 않았습니다.")
        return 0

    targets = [index] + files
    exists = [t["path"] for t in targets if os.path.exists(t["path"]) and t["path"] != os.path.abspath(args.checklist)]
    if exists and not args.force:
        print("\n이미 존재하는 파일이 있습니다 (--force 로 덮어쓰기):", file=sys.stderr)
        for e in exists:
            print("  " + e, file=sys.stderr)
        return 1

    for t in targets:
        with open(t["path"], "w", encoding="utf-8") as fh:
            fh.write(t["text"])
    print("\n작성 완료:")
    print("  인덱스: {}".format(index["path"]))
    for f in files:
        print("  {}: {}".format(f["id"], f["path"]))
    print("\n원본은 인덱스로 대체되었습니다. 항목 본문은 마일스톤 파일에 있습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
