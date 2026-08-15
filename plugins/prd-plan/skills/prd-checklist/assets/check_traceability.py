#!/usr/bin/env python3
"""PRD / PLAN / 체크리스트 추적성 검증기.

REQ(요구사항) -> TASK(작업) -> CHK(체크리스트 항목) 연결이 끊긴 곳을 찾는다.
Python 표준 라이브러리만 사용한다.

사용:
    python3 check_traceability.py --prd docs/prd/PRD-x.md \
                                  --plan docs/plan/PLAN-x.md \
                                  --checklist docs/checklist/CHECKLIST-x.md
    python3 check_traceability.py --checklist docs/checklist/CHECKLIST-x.md --status
    # 마일스톤 단위로 나눈 경우 — 전체 커버리지·진척을 한 번에 보려면 모두 넘긴다
    python3 check_traceability.py --plan PLAN-x.md \
        --checklist CHECKLIST-x-M1.md --checklist CHECKLIST-x-M2.md --status
    python3 check_traceability.py --prd ... --plan ... --json

종료 코드:
    0  ERROR 없음 (--strict 지정 시에는 WARN도 없어야 함)
    1  ERROR 있음
    2  사용법 오류 / 파일 없음

Windows에서 python3 가 MS Store alias로 exit 49를 내면 `py -3` 또는 `python` 사용.
"""

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------- 정규식

RE_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
RE_REQ_HEAD = re.compile(r"^#{1,6}\s*(REQ-\d{3})\b")
RE_TASK_HEAD = re.compile(r"^#{1,6}\s*(TASK-\d{3})\b")
RE_REQ_ID = re.compile(r"\bREQ-\d{3}\b")
RE_TASK_ID = re.compile(r"\bTASK-\d{3}\b")
RE_AC_ID = re.compile(r"\bAC-(\d{3})-\d+\b")
RE_AC_FULL = re.compile(r"\bAC-\d{3}-\d+\b")
RE_OPEN_ID = re.compile(r"\bOPEN-\d{3}\b")
# 수용 기준 "정의" 행:  - AC-001-1: 설명   (문장 중간의 AC-###-# 는 상호 참조이지 정의가 아니다)
RE_AC_DEF = re.compile(r"^\s*[-*]\s*\*{0,2}(AC-(\d{3})-\d+)\*{0,2}\s*[::]")
# 미결 이슈 표의 정의 행:  | OPEN-001 | 항목 | ...
RE_OPEN_DEF = re.compile(r"^\s*\|\s*\*{0,2}(OPEN-\d{3})\*{0,2}\s*\|")

RE_CHK_LINE = re.compile(
    r"^\s*[-*]\s*\[(?P<mark>[ xX~!])\]\s*\*\*(?P<id>CHK-\d{3})\*\*\s*"
    r"\((?P<tasks>[^)]*)\)\s*(?P<rest>.*)$"
)

RE_FIELD = re.compile(r"^\s*[-*]\s*\*\*(?P<key>[^*]+)\*\*\s*:\s*(?P<val>.*)$")
RE_EVIDENCE = re.compile(r"근거\s*:\s*(?P<val>.*?)(?:\s*[·|]\s*\S+\s*:|$)")
RE_OWNER = re.compile(r"주체\s*:\s*(?P<val>[^·|]+)")

# estimation-policy 위반 탐지
RE_ABS_DATE = re.compile(r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b|\d{1,2}\s*월\s*\d{1,2}\s*주차")
RE_EFFORT = re.compile(r"\d+\s*(?:인일|인월|man-?day|MD)\b|\d+\s*(?:시간|일|주|개월)\s*(?:소요|예상)")
# 문서 메타데이터 줄 — 일정 주장이 아니므로 정책 스캔에서 제외
RE_DOC_META = re.compile(
    r"(최종\s*갱신|최종\s*수정|작성일|갱신일|수정일|승인일|발행일|버전\s*이력|"
    r"last\s*updated?|updated?\s*(?:on|at)?|created|revision|approved_at|changelog)\s*[::]",
    re.IGNORECASE,
)

SIZES = {"S", "M", "L", "XL"}
STRENGTHS = {"MUST", "SHOULD", "MAY"}

MARK_STATE = {" ": "미착수", "~": "진행중", "x": "완료", "X": "완료", "!": "차단"}


# ---------------------------------------------------------------- 유틸

class Report:
    def __init__(self):
        self.errors = []
        self.warns = []
        self.infos = []

    def error(self, code, msg, loc=""):
        self.errors.append({"level": "ERROR", "code": code, "message": msg, "location": loc})

    def warn(self, code, msg, loc=""):
        self.warns.append({"level": "WARN", "code": code, "message": msg, "location": loc})

    def info(self, msg):
        self.infos.append(msg)

    @property
    def items(self):
        return self.errors + self.warns


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def split_blocks(lines, head_re):
    """head_re 로 시작하는 헤딩 블록을 {id: (시작줄번호, [본문줄])} 으로 자른다."""
    blocks = {}
    order = []
    current = None
    for idx, line in enumerate(lines, start=1):
        m = head_re.match(line)
        if m:
            current = m.group(1)
            if current in blocks:
                blocks[current][2].append(idx)  # 중복 정의 기록
            else:
                blocks[current] = (idx, [], [])
                order.append(current)
            continue
        if current and RE_HEADING.match(line) and not head_re.match(line):
            # 다른 헤딩을 만나면 블록 종료 (상위/동급 무관하게 보수적으로 끊는다)
            current = None
            continue
        if current:
            blocks[current][1].append(line)
    return blocks, order


def scan_lines(lines):
    """정책 위반 스캔 대상 줄만 (줄번호, 내용)으로 내보낸다.

    제외 대상:
      - YAML 프론트매터 블록
      - 펜스 코드블록(``` / ~~~) 내부 — 스키마·예시의 타임스탬프는 일정 주장이 아니다
      - 문서 메타데이터 줄(최종 갱신·작성일·승인일 등)
    """
    in_code = False
    fence = None
    in_front = False
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if idx == 1 and stripped == "---":
            in_front = True
            continue
        if in_front:
            if stripped == "---":
                in_front = False
            continue
        if in_code:
            if fence and stripped.startswith(fence):
                in_code = False
                fence = None
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = True
            fence = stripped[:3]
            continue
        if RE_DOC_META.search(line):
            continue
        yield idx, line


def fields_of(body):
    """- **키**: 값  형태의 필드를 dict로."""
    out = {}
    for line in body:
        m = RE_FIELD.match(line)
        if m:
            out[m.group("key").strip()] = m.group("val").strip()
    return out


def field_get(fields, *names):
    for name in names:
        for key, val in fields.items():
            if name in key:
                return val
    return None


# ---------------------------------------------------------------- 파서

def parse_prd(path, rep):
    lines = read_lines(path)
    blocks, order = split_blocks(lines, RE_REQ_HEAD)
    reqs = {}
    for rid in order:
        start, body, dups = blocks[rid]
        text = "\n".join(body)
        fields = fields_of(body)
        strength = (field_get(fields, "강도", "우선순위") or "").split()[0].upper() if field_get(fields, "강도", "우선순위") else ""
        state = field_get(fields, "상태") or ""
        reqs[rid] = {
            "line": start,
            "strength": strength if strength in STRENGTHS else "",
            "deleted": "삭제" in state,
            "has_ac": bool(RE_AC_FULL.search(text)) or ("수용 기준" in text and re.search(r"수용\s*기준\s*\**\s*:?\s*\n?\s*[-*]", text) is not None),
            "ac_ids": [m.group(1) for m in (RE_AC_DEF.match(l) for l in body) if m],
            "ac_prefixes": [m.group(2) for m in (RE_AC_DEF.match(l) for l in body) if m],
        }
        for dup in dups:
            rep.error("DUP_REQ", "REQ ID가 중복 정의됨: {}".format(rid), "{}:{}".format(path, dup))
    if not reqs:
        rep.warn("NO_REQ", "PRD에서 REQ 블록을 찾지 못함 (### REQ-001 — 제목 형식 확인)", path)
    return reqs


def parse_plan(path, rep):
    lines = read_lines(path)
    blocks, order = split_blocks(lines, RE_TASK_HEAD)
    tasks = {}
    for tid in order:
        start, body, dups = blocks[tid]
        fields = fields_of(body)
        basis_raw = field_get(fields, "근거") or ""
        prereq_raw = field_get(fields, "선행") or ""
        size = (field_get(fields, "규모") or "").strip().upper()
        tasks[tid] = {
            "line": start,
            "reqs": RE_REQ_ID.findall(basis_raw),
            "prereqs": RE_TASK_ID.findall(prereq_raw),
            "size": size if size in SIZES else "",
            "size_raw": size,
            "blocked": bool(field_get(fields, "차단")),
            "has_done_criteria": bool(field_get(fields, "완료 기준", "완료기준")),
        }
        for dup in dups:
            rep.error("DUP_TASK", "TASK ID가 중복 정의됨: {}".format(tid), "{}:{}".format(path, dup))

    # 정책 위반 스캔 — 코드블록·프론트매터·문서 메타데이터 줄은 제외한다.
    # (JSON 예시의 타임스탬프나 "최종 갱신: YYYY-MM-DD"는 일정 주장이 아니다)
    for idx, line in scan_lines(lines):
        if RE_ABS_DATE.search(line):
            rep.warn("ABS_DATE", "절대 날짜 표기 발견 (사용자 제공 값이면 '가정' 표에 출처와 함께 기재): {}".format(line.strip()[:70]), "{}:{}".format(path, idx))
        if RE_EFFORT.search(line):
            rep.warn("EFFORT", "시간 단위 공수 표기 발견 (규모는 S/M/L/XL): {}".format(line.strip()[:70]), "{}:{}".format(path, idx))

    if not tasks:
        rep.warn("NO_TASK", "PLAN에서 TASK 블록을 찾지 못함 (### TASK-001 — 제목 형식 확인)", path)
    return tasks


def check_ids(path, reqs, rep):
    """AC ID 접두가 소속 REQ와 일치하는지, OPEN 참조가 해소되는지 검사한다."""
    ac_defined = set()
    for rid, r in reqs.items():
        num = rid.split("-")[1]
        ac_defined.update(r["ac_ids"])
        for pref in set(r["ac_prefixes"]):
            if pref != num:
                rep.error("AC_PREFIX", "{}: 소속이 다른 번호의 수용 기준을 정의함(AC-{}-*)".format(rid, pref),
                          "{}:{}".format(path, r["line"]))

    lines = read_lines(path)
    # PRD 안의 AC 상호 참조도 실재해야 한다
    for idx, line in enumerate(lines, start=1):
        if RE_AC_DEF.match(line):
            continue
        for ac in RE_AC_FULL.findall(line):
            if ac not in ac_defined:
                rep.error("AC_BAD_REF", "정의되지 않은 수용 기준 {} 참조".format(ac), "{}:{}".format(path, idx))
    defined, def_line = {}, {}
    for idx, line in enumerate(lines, start=1):
        m = RE_OPEN_DEF.match(line)
        if m:
            oid = m.group(1)
            if oid in defined:
                rep.error("DUP_OPEN", "미결 이슈 ID가 중복 정의됨: {}".format(oid), "{}:{}".format(path, idx))
            defined[oid] = idx
            def_line[idx] = oid

    referenced = {}
    for idx, line in enumerate(lines, start=1):
        if idx in def_line:          # 자기 정의 행은 참조로 세지 않는다
            continue
        for oid in RE_OPEN_ID.findall(line):
            referenced.setdefault(oid, idx)

    for oid, idx in referenced.items():
        if oid not in defined:
            rep.error("OPEN_BAD_REF", "정의되지 않은 미결 이슈 {} 참조".format(oid), "{}:{}".format(path, idx))
    for oid, idx in defined.items():
        if oid not in referenced:
            rep.warn("OPEN_ORPHAN", "{}: 미결 표에만 있고 본문에 (미정 — {}) 표기가 없음 — 해당 절 독자가 미결을 모른다".format(oid, oid),
                     "{}:{}".format(path, idx))
    return ac_defined


def check_ac_refs(path, label, ac_defined, rep):
    """PLAN·체크리스트가 참조하는 AC가 PRD에 실재하는지 검사한다."""
    if not ac_defined:
        return
    for idx, line in enumerate(read_lines(path), start=1):
        for ac in RE_AC_FULL.findall(line):
            if ac not in ac_defined:
                rep.error("AC_BAD_REF", "{}: PRD에 없는 수용 기준 {} 참조".format(label, ac),
                          "{}:{}".format(path, idx))


def parse_checklist(path, rep, chks=None):
    """여러 파일을 누적 파싱한다 (마일스톤 단위 분리 지원)."""
    lines = read_lines(path)
    if chks is None:
        chks = {}
    seen_here = 0
    for idx, line in enumerate(lines, start=1):
        m = RE_CHK_LINE.match(line)
        if not m:
            continue
        cid = m.group("id")
        rest = m.group("rest")
        tasks = RE_TASK_ID.findall(m.group("tasks"))
        ev = RE_EVIDENCE.search(rest)
        owner = RE_OWNER.search(rest)
        entry = {
            "path": path,
            "line": idx,
            "mark": m.group("mark"),
            "state": MARK_STATE.get(m.group("mark"), "?"),
            "tasks": tasks,
            "evidence": (ev.group("val").strip() if ev else ""),
            "owner": (owner.group("val").strip() if owner else ""),
            "text": rest.strip(),
        }
        if cid in chks:
            prev = chks[cid]
            where = "{}:{}".format(prev["path"], prev["line"])
            if prev["path"] != path:
                rep.error("DUP_CHK", "CHK ID가 파일 간에 중복됨: {} (이미 {}) — 마일스톤 분리 시 연번을 이어서 부여한다".format(cid, where), "{}:{}".format(path, idx))
            else:
                rep.error("DUP_CHK", "CHK ID가 중복 정의됨: {}".format(cid), "{}:{}".format(path, idx))
        else:
            chks[cid] = entry
            seen_here += 1
    if seen_here == 0:
        rep.warn("NO_CHK", "체크리스트 항목을 찾지 못함 (- [ ] **CHK-001** (TASK-001) ... 형식 확인)", path)
    return chks


# ---------------------------------------------------------------- 검사

def find_cycles(tasks):
    """선행 의존 순환 탐지. 순환에 포함된 노드 목록들을 반환."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {t: WHITE for t in tasks}
    stack = []
    cycles = []

    def dfs(node):
        color[node] = GRAY
        stack.append(node)
        for nxt in tasks[node]["prereqs"]:
            if nxt not in tasks:
                continue
            if color[nxt] == GRAY:
                cycles.append(stack[stack.index(nxt):] + [nxt])
            elif color[nxt] == WHITE:
                dfs(nxt)
        stack.pop()
        color[node] = BLACK

    for node in tasks:
        if color[node] == WHITE:
            dfs(node)
    return cycles


def cross_check(reqs, tasks, chks, paths, rep):
    prd, plan, chkl = paths

    # TASK -> REQ
    if tasks and reqs is not None:
        for tid, t in tasks.items():
            loc = "{}:{}".format(plan, t["line"])
            if not t["reqs"]:
                rep.error("TASK_NO_BASIS", "{}: 근거 요구사항이 없음 (범위 밖 작업이거나 PRD 누락)".format(tid), loc)
            for rid in t["reqs"]:
                if rid not in reqs:
                    rep.error("TASK_BAD_REF", "{}: 존재하지 않는 요구사항 {} 참조".format(tid, rid), loc)
                elif reqs[rid]["deleted"]:
                    rep.warn("TASK_DELETED_REF", "{}: 삭제된 요구사항 {} 참조".format(tid, rid), loc)
            if not t["size"]:
                rep.warn("TASK_NO_SIZE", "{}: 규모 표기가 없거나 S/M/L/XL이 아님({})".format(tid, t["size_raw"] or "없음"), loc)
            elif t["size"] == "XL":
                rep.warn("TASK_XL", "{}: XL은 분해 대상 (L 이하로 쪼갠다)".format(tid), loc)
            if not t["has_done_criteria"]:
                rep.warn("TASK_NO_DONE", "{}: 완료 기준이 없음".format(tid), loc)
            for pre in t["prereqs"]:
                if pre not in tasks:
                    rep.error("TASK_BAD_PREREQ", "{}: 존재하지 않는 선행 작업 {}".format(tid, pre), loc)

        for cyc in find_cycles(tasks):
            rep.error("CYCLE", "선행 의존 순환: {}".format(" -> ".join(cyc)), plan)

    # REQ 커버리지
    if reqs and tasks:
        covered = set()
        for t in tasks.values():
            covered.update(t["reqs"])
        for rid, r in reqs.items():
            if r["deleted"] or rid in covered:
                continue
            loc = "{}:{}".format(prd, r["line"])
            if r["strength"] == "MUST":
                rep.error("MUST_UNCOVERED", "{}(MUST): 어떤 TASK도 커버하지 않음".format(rid), loc)
            else:
                rep.warn("REQ_UNCOVERED", "{}({}): 커버하는 TASK 없음 — 사유가 문서에 있어야 함".format(rid, r["strength"] or "강도미상"), loc)

    # REQ AC
    if reqs:
        for rid, r in reqs.items():
            if r["deleted"]:
                continue
            if not r["has_ac"]:
                rep.error("REQ_NO_AC", "{}: 수용 기준(AC)이 없음 — 완료 판정 불가".format(rid), "{}:{}".format(prd, r["line"]))
            if not r["strength"]:
                rep.warn("REQ_NO_STRENGTH", "{}: 강도(MUST/SHOULD/MAY) 표기 없음".format(rid), "{}:{}".format(prd, r["line"]))

    # CHK -> TASK
    if chks:
        for cid, c in chks.items():
            loc = "{}:{}".format(c.get("path", chkl), c["line"])
            if not c["tasks"]:
                rep.error("CHK_NO_TASK", "{}: 참조 TASK가 없음".format(cid), loc)
            if tasks:
                for tid in c["tasks"]:
                    if tid not in tasks:
                        rep.error("CHK_BAD_REF", "{}: 존재하지 않는 작업 {} 참조".format(cid, tid), loc)
            if not c["owner"]:
                rep.warn("CHK_NO_OWNER", "{}: 실행 주체 표기 없음".format(cid), loc)
            if c["mark"] in ("x", "X") and not c["evidence"]:
                rep.error("CHK_NO_EVIDENCE", "{}: 완료 표시인데 근거가 비어 있음".format(cid), loc)

    # TASK 커버리지 (체크리스트)
    if tasks and chks:
        covered = set()
        for c in chks.values():
            covered.update(c["tasks"])
        for tid, t in tasks.items():
            if tid not in covered:
                rep.warn("TASK_UNCHECKED", "{}: 체크리스트 항목이 없음".format(tid), "{}:{}".format(plan, t["line"]))


# ---------------------------------------------------------------- 출력

def status_summary(tasks, chks, reqs):
    total = len(chks)
    counts = {"완료": 0, "진행중": 0, "차단": 0, "미착수": 0}
    for c in chks.values():
        counts[c["state"]] = counts.get(c["state"], 0) + 1
    per_task = {}
    for c in chks.values():
        for tid in c["tasks"]:
            slot = per_task.setdefault(tid, {"total": 0, "완료": 0})
            slot["total"] += 1
            if c["state"] == "완료":
                slot["완료"] += 1
    done_tasks = [t for t, v in per_task.items() if v["total"] and v["total"] == v["완료"]]
    return {
        "checklist_total": total,
        "counts": counts,
        "progress_pct": round(100.0 * counts["완료"] / total, 1) if total else 0.0,
        "tasks_with_items": len(per_task),
        "tasks_done": len(done_tasks),
        "blocked_items": [c for c in chks if chks[c]["state"] == "차단"],
    }


def print_text(rep, stats, status):
    for item in rep.errors:
        print("ERROR [{}] {}{}".format(item["code"], item["message"],
                                       "  ({})".format(item["location"]) if item["location"] else ""))
    for item in rep.warns:
        print("WARN  [{}] {}{}".format(item["code"], item["message"],
                                       "  ({})".format(item["location"]) if item["location"] else ""))
    print("")
    print("문서: REQ {req} · TASK {task} · CHK {chk}".format(**stats))
    print("결과: ERROR {} / WARN {}".format(len(rep.errors), len(rep.warns)))
    if status:
        print("")
        print("진척: {완료}/{total} 완료 ({pct}%) · 진행중 {진행중} · 차단 {차단} · 미착수 {미착수}".format(
            total=status["checklist_total"], pct=status["progress_pct"], **status["counts"]))
        print("작업 완료: {}/{} TASK".format(status["tasks_done"], status["tasks_with_items"]))
        if status["blocked_items"]:
            print("차단 항목: {}".format(", ".join(sorted(status["blocked_items"]))))


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="PRD/PLAN/체크리스트 추적성 검증")
    ap.add_argument("--prd")
    ap.add_argument("--plan")
    ap.add_argument("--checklist", action="append", metavar="PATH",
                    help="체크리스트 경로. 마일스톤 단위로 나눴으면 여러 번 지정한다")
    ap.add_argument("--status", action="store_true", help="체크리스트 진척 요약 출력")
    ap.add_argument("--json", action="store_true", help="JSON으로 출력")
    ap.add_argument("--strict", action="store_true", help="WARN도 실패로 처리")
    args = ap.parse_args(argv)

    checklists = args.checklist or []
    given = [p for p in (args.prd, args.plan) if p] + checklists
    if not given:
        ap.error("--prd / --plan / --checklist 중 최소 하나가 필요합니다")
    for path in given:
        if not os.path.isfile(path):
            print("파일을 찾을 수 없음: {}".format(path), file=sys.stderr)
            return 2

    rep = Report()
    reqs = parse_prd(args.prd, rep) if args.prd else {}
    ac_defined = check_ids(args.prd, reqs, rep) if args.prd else set()
    tasks = parse_plan(args.plan, rep) if args.plan else {}
    chks = {}
    for cpath in checklists:
        parse_checklist(cpath, rep, chks)
    if args.plan:
        check_ac_refs(args.plan, "PLAN", ac_defined, rep)
    for cpath in checklists:
        check_ac_refs(cpath, "체크리스트", ac_defined, rep)

    cross_check(reqs if args.prd else None, tasks, chks,
                (args.prd or "", args.plan or "", checklists[0] if checklists else ""), rep)

    stats = {"req": len(reqs), "task": len(tasks), "chk": len(chks)}
    status = status_summary(tasks, chks, reqs) if (args.status and chks) else None
    if status and len(checklists) > 1:
        status["files"] = len(checklists)

    if args.json:
        print(json.dumps({
            "stats": stats,
            "errors": rep.errors,
            "warnings": rep.warns,
            "status": status,
            "ok": not rep.errors and (not args.strict or not rep.warns),
        }, ensure_ascii=False, indent=2))
    else:
        print_text(rep, stats, status)

    if rep.errors:
        return 1
    if args.strict and rep.warns:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
