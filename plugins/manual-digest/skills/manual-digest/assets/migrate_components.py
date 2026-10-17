#!/usr/bin/env python3
"""프로젝트에 등록된 부품 다이제스트를 전역(~/.claude/manuals)으로 옮긴다.

요약을 다시 하지 않는다 — 다이제스트 폴더를 그대로 옮기고 메타데이터·카탈로그만 고친다.
무엇을 옮길지는 사람이(또는 메인 Claude가) 계획 파일에 적는다. 스크립트는 판단하지 않는다.

  plan    <project> [--json]            계획 초안 <project>/.claude/manuals/.migrate-plan.json 작성 + 표 출력
  apply   <project>                     계획대로 실행 (프로젝트 폴더는 지우지 않는다)
  cleanup <project>                     전역 사본을 확인한 뒤 옮긴 프로젝트 폴더만 지운다
  --selftest

공통 옵션: --global-root DIR (기본 ~/.claude/manuals), --scan-root DIR (기본 ~/Repos, 다른 프로젝트 겹침 탐색)

계획 파일의 action:
  review   초안 기본값. 그대로 두면 apply가 거부한다 (분류는 사람이 정한다)
  migrate  전역으로 복사 (원본 PDF도 source.* 로 복사, 없으면 다이제스트만)
  pointer  전역에 이미 있다 — target 의 별칭에 이 ID를 더하고 프로젝트 INDEX 줄만 전역을 가리키게 바꾼다
  keep     프로젝트에 남긴다 (보드 회로도·장비 매뉴얼 등)
"""
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicad_locate  # noqa: E402

CTX_RE = re.compile(r"본 보드|우리 보드|이 보드|후보|채택|우리 설계|본 설계")
ACTIONS = {"migrate", "pointer", "keep"}


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def catalog(root):
    """root 아래 */metadata.json → [(id, aliases, sha256, 경로)]"""
    out = []
    for m in glob.glob(os.path.join(root, "*", "metadata.json")):
        try:
            d = load(m)
        except (OSError, ValueError):
            continue
        out.append((d.get("id"), set(d.get("aliases") or []), d.get("sha256"), m))
    return out


def plan(project, groot, scan_root):
    mroot = os.path.join(project, ".claude", "manuals")
    gcat = catalog(groot)
    others = []
    for m in glob.glob(os.path.join(scan_root, "**", ".claude", "manuals"), recursive=True):
        if os.path.abspath(m) != os.path.abspath(mroot):
            others += catalog(m)
    items = []
    for m in sorted(glob.glob(os.path.join(mroot, "*", "metadata.json"))):
        d = load(m)
        if d.get("format") == "codebase":
            continue
        did, sha = d.get("id"), d.get("sha256")
        src = d.get("source") or ""
        dg = os.path.join(os.path.dirname(m), "digest.md")
        hits = []
        if os.path.isfile(dg):
            with open(dg, encoding="utf-8", errors="replace") as f:
                hits = [(n, line.strip()[:100]) for n, line in enumerate(f, 1) if CTX_RE.search(line)]

        def match(cat):
            return [{"id": i, "by": "sha256" if sha and s == sha else "id", "path": p,
                     "project": os.path.relpath(p.split("/.claude/manuals/")[0], scan_root)}
                    for i, a, s, p in cat if (sha and s == sha) or did == i or did in a]
        g = match(gcat)
        items.append({
            "id": did, "title": d.get("title"), "format": d.get("format"), "version": d.get("version"),
            "source_exists": os.path.isfile(src), "atomized": bool(d.get("atomized")),
            "context_hits": hits, "global_match": g, "other_projects": match(others),
            "action": "pointer" if g else "review", "target": g[0]["id"] if g else did, "aliases": [],
        })
    return items


def print_plan(items):
    print("%-28s %-8s %-5s %-4s %-26s %s" % ("id", "action", "원본", "문구", "전역", "다른 프로젝트"))
    for it in items:
        other = ", ".join(sorted({"%s:%s" % (o["project"], o["id"]) for o in it["other_projects"]})) or "-"
        print("%-28s %-8s %-5s %-4d %-26s %s" % (
            it["id"], it["action"], "있음" if it["source_exists"] else "없음", len(it["context_hits"]),
            ",".join(g["id"] for g in it["global_match"]) or "-", other))


def find_row(lines, did):
    pat = re.compile(r"^\|\s*`?%s`?\s*\|" % re.escape(did))
    return next((i for i, line in enumerate(lines) if pat.match(line)), None)


def insert_global_row(index_path, row):
    with open(index_path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    sep = next((i for i, line in enumerate(lines) if re.match(r"^\|\s*-", line)), None)
    if sep is None:
        lines += ["", "| ID | 제목 | 포맷 | 버전 | scope | digest | 분할 |",
                  "|----|------|------|------|-------|--------|------|", row]
    else:
        end = sep + 1
        while end < len(lines) and lines[end].startswith("|"):
            end += 1
        lines.insert(end, row)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def point_project_row(index_path, did, target, groot):
    """프로젝트 INDEX 의 그 줄을 전역 다이제스트를 가리키는 줄로 바꾼다 (프로젝트 메모 칸은 사람이 채운다)."""
    with open(index_path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    i = find_row(lines, did)
    if i is None:
        return False
    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    while len(cells) < 7:
        cells.append("")
    cells[1] = "[전역] " + re.sub(r"^\[전역\]\s*", "", cells[1])
    cells[4] = "global"
    cells[5] = "[digest.md](%s)" % os.path.join(groot, target, "digest.md")
    lines[i] = "| " + " | ".join(cells) + " |"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return True


def edit_frontmatter(digest, fields):
    """digest.md 프론트매터의 키를 바꾸거나 더한다. 본문은 건드리지 않는다."""
    if not os.path.isfile(digest):
        return
    with open(digest, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n([\s\S]*?)\n---\n", text)
    if not m:
        return
    fm = m.group(1)
    for key, val in fields.items():
        line = "%s: %s" % (key, val)
        if re.search(r"^%s:.*$" % key, fm, re.M):
            fm = re.sub(r"^%s:.*$" % key, line.replace("\\", "\\\\"), fm, count=1, flags=re.M)
        else:
            fm += "\n" + line
    with open(digest, "w", encoding="utf-8") as f:
        f.write("---\n" + fm + "\n---\n" + text[m.end():])


def retarget_paths(dst, origin, new_src):
    """본문(digest.md 프론트매터 아래·index.md)의 원본 경로를 전역 사본 경로로 바꾼다.
    안 바꾸면 "원본 핀포인트" 명령이 프로젝트 폴더를 가리켜, 프로젝트를 지우거나 옮기면 끊긴다."""
    for name in ("digest.md", "index.md"):
        path = os.path.join(dst, name)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = re.match(r"^---\n[\s\S]*?\n---\n", text)
        head = m.group(0) if m else ""
        body = text[len(head):]
        if origin in body:
            with open(path, "w", encoding="utf-8") as f:
                f.write(head + body.replace(origin, new_src))


def kicad_block(names, project):
    """ID·별칭을 대문자 심볼 이름으로 찾아본다. 못 찾으면 전부 null (등록은 계속)."""
    for n in names:
        r = kicad_locate.locate(n.upper(), None, project)
        if r["symbol"] and r["symbol"]["found"]:
            fp, mdl = r["footprint"], r["model"]
            warns = list(r["warnings"])
            if fp and not fp["found"]:  # 심볼이 가리키는 풋프린트를 라이브러리 표에서 못 찾음
                warns.append("풋프린트 위치 끊김: " + fp["ref"])
            return {"symbol": r["symbol"]["ref"],
                    "footprint": fp["ref"] if fp else None,
                    "model": mdl["raw"] if mdl and mdl.get("exists") else None,
                    "model_kind": "unknown", "checked_at": now(), "warnings": warns}
    return {"symbol": None, "footprint": None, "model": None, "model_kind": "unknown",
            "checked_at": now(), "warnings": []}


def apply(project, groot):
    mroot = os.path.join(project, ".claude", "manuals")
    pfile = os.path.join(mroot, ".migrate-plan.json")
    items = load(pfile)
    bad = [it["id"] for it in items if it["action"] not in ACTIONS]
    if bad:
        print("거부: action 이 정해지지 않은 항목 — " + ", ".join(bad))
        return 1
    os.makedirs(groot, exist_ok=True)
    gindex = os.path.join(groot, "INDEX.md")
    if not os.path.isfile(gindex):
        with open(gindex, "w", encoding="utf-8") as f:
            f.write("# Indexed Manuals (Global)\n\n## 등록된 매뉴얼\n\n"
                    "| ID | 제목 | 포맷 | 버전 | scope | digest | 분할 |\n"
                    "|----|------|------|------|-------|--------|------|\n")
    pindex = os.path.join(mroot, "INDEX.md")
    for it in items:
        did, target = it["id"], it.get("target") or it["id"]
        src_dir, dst = os.path.join(mroot, did), os.path.join(groot, target)
        if it["action"] == "keep":
            continue
        if it["action"] == "pointer":
            gm = os.path.join(dst, "metadata.json")
            if not os.path.isfile(gm):
                print("건너뜀 %s: 전역에 %s 가 없다" % (did, target))
                continue
            d = load(gm)
            al = set(d.get("aliases") or []) | set(it.get("aliases") or [])
            if did != target:
                al.add(did)
            d["aliases"] = sorted(al)
            save(gm, d)
            point_project_row(pindex, did, target, groot)
            print("pointer %s -> 전역 %s" % (did, target))
            continue
        if os.path.exists(dst):
            print("건너뜀 %s: 전역에 같은 ID 폴더가 이미 있다 — pointer 로 바꿀 것" % target)
            continue
        shutil.copytree(src_dir, dst)
        meta_path = os.path.join(dst, "metadata.json")
        d = load(meta_path)
        origin = d.get("source")
        if origin and os.path.isfile(origin):
            new_src = os.path.join(dst, "source" + os.path.splitext(origin)[1].lower())
            shutil.copy2(origin, new_src)
            d["source"] = new_src
            d.pop("source_missing", None)
            retarget_paths(dst, origin, new_src)
        else:  # 원본 없이 다이제스트만 옮긴다 — 원본 페이지 조회는 PDF를 다시 구해 --update 할 때까지 불가
            d["source"], d["source_missing"] = None, True
        aliases = set(d.get("aliases") or []) | set(it.get("aliases") or [])
        if did != target:
            aliases.add(did)
        d.update({"id": target, "scope": "global", "kind": "component", "origin": origin,
                  "aliases": sorted(aliases), "migrated_from": os.path.abspath(project), "migrated_at": now()})
        d["kicad"] = kicad_block([target] + sorted(aliases), project)
        save(meta_path, d)
        edit_frontmatter(os.path.join(dst, "digest.md"), {
            "id": target, "scope": "global", "kind": "component",
            "source": d["source"] or "(원본 미보관)", "origin": origin or "",
            "aliases": "[" + ", ".join(d["aliases"]) + "]"})
        insert_global_row(gindex, "| %s | [부품] %s | %s | %s | global | [digest.md](%s/digest.md) | %s |" % (
            target, d.get("title") or target, d.get("format") or "", d.get("version") or "", target,
            "분할" if d.get("atomized") else "-"))
        point_project_row(pindex, did, target, groot)
        notes = []
        if d.get("source_missing"):
            notes.append("원본 없음")
        if d.get("atomized"):
            notes.append("분할본 있음 — split_md.py update 필요")
        if it.get("context_hits"):
            notes.append("프로젝트 문구 %d줄 정리 필요" % len(it["context_hits"]))
        k = d["kicad"]
        notes.append("심볼 %s" % (k["symbol"] or "없음"))
        print("migrate %s%s  %s" % (did, "" if did == target else " -> " + target, "; ".join(notes)))
    return 0


def cleanup(project, groot):
    mroot = os.path.join(project, ".claude", "manuals")
    items = load(os.path.join(mroot, ".migrate-plan.json"))
    for it in items:
        if it["action"] not in ("migrate", "pointer"):
            continue
        g = os.path.join(groot, it.get("target") or it["id"])
        p = os.path.join(mroot, it["id"])
        if not (os.path.isfile(os.path.join(g, "digest.md")) and os.path.isfile(os.path.join(g, "metadata.json"))):
            print("남김 %s: 전역 사본을 확인하지 못했다" % it["id"])
            continue
        if os.path.isdir(p):
            shutil.rmtree(p)
            print("삭제 %s" % p)
    return 0


def selftest():
    tmp = tempfile.mkdtemp()
    proj, groot = os.path.join(tmp, "Repos", "kvm"), os.path.join(tmp, "global")
    other = os.path.join(tmp, "Repos", "elev", ".claude", "manuals", "tbd")
    os.makedirs(other)
    save(os.path.join(other, "metadata.json"), {"id": "tbd", "sha256": "S2"})
    pdf = os.path.join(tmp, "a.pdf")
    with open(pdf, "wb") as f:
        f.write(b"%PDF-1.4 test")
    mroot = os.path.join(proj, ".claude", "manuals")
    for did, src, sha, body in (("qqchip", pdf, "S1", "본 보드는 QSOP-16\ntext %s\n" % pdf), ("tbd", "/nope.pdf", "S2", "x\n"),
                                ("board", pdf, "S3", "x\n")):
        os.makedirs(os.path.join(mroot, did))
        save(os.path.join(mroot, did, "metadata.json"),
             {"id": did, "title": did.upper(), "format": "pdf", "version": "Rev 1", "source": src,
              "scope": "project", "sha256": sha})
        with open(os.path.join(mroot, did, "digest.md"), "w") as f:
            f.write("---\nid: %s\nsource: %s\nscope: project\n---\n# t\n%s" % (did, src, body))
    with open(os.path.join(mroot, "INDEX.md"), "w") as f:
        f.write("# I\n\n| ID | 제목 | 포맷 | 버전 | scope | digest | 분할 |\n|---|---|---|---|---|---|---|\n"
                "| qqchip | QQCHIP | pdf | Rev 1 | project | [digest.md](qqchip/digest.md) | - |\n"
                "| `tbd` | TBD | pdf | Rev 1 | project | [digest.md](tbd/digest.md) | - |\n"
                "| board | BOARD | pdf | Rev 1 | project | [digest.md](board/digest.md) | - |\n\n## 규칙\n")
    items = plan(proj, groot, os.path.join(tmp, "Repos"))
    by = {it["id"]: it for it in items}
    assert by["qqchip"]["context_hits"] and by["qqchip"]["action"] == "review"
    assert by["tbd"]["other_projects"] and not by["tbd"]["source_exists"]
    save(os.path.join(mroot, ".migrate-plan.json"), items)
    assert apply(proj, groot) == 1  # review 가 남아 있으면 거부
    by["qqchip"].update(action="migrate", aliases=["qqchip-x"])
    by["tbd"].update(action="migrate")
    by["board"].update(action="keep")
    save(os.path.join(mroot, ".migrate-plan.json"), items)
    assert apply(proj, groot) == 0
    g = load(os.path.join(groot, "qqchip", "metadata.json"))
    assert g["scope"] == "global" and g["kind"] == "component" and g["origin"] == pdf
    assert g["source"].endswith("qqchip/source.pdf") and os.path.isfile(g["source"]) and g["aliases"] == ["qqchip-x"]
    t = load(os.path.join(groot, "tbd", "metadata.json"))
    assert t["source"] is None and t["source_missing"] is True
    dg = open(os.path.join(groot, "qqchip", "digest.md")).read()
    assert "text %s/qqchip/source.pdf" % groot in dg and dg.count(pdf) == 1  # 본문 경로는 전역 사본으로, origin 줄만 남김
    assert "scope: global" in dg and "kind: component" in dg and "본 보드는 QSOP-16" in dg  # 문구는 사람이 정리
    gi = open(os.path.join(groot, "INDEX.md")).read()
    assert "| qqchip | [부품] QQCHIP |" in gi and "| tbd |" in gi
    pi = open(os.path.join(mroot, "INDEX.md")).read()
    assert "[전역] QQCHIP" in pi and "[전역] TBD" in pi and "| board | BOARD |" in pi and pi.endswith("## 규칙\n")
    # 두 번째 프로젝트: 같은 부품은 pointer, 별칭 추가
    p2 = os.path.join(tmp, "Repos", "p2", ".claude", "manuals", "qqchip2")
    os.makedirs(p2)
    save(os.path.join(p2, "metadata.json"), {"id": "qqchip2", "sha256": "S1", "format": "pdf"})
    with open(os.path.join(os.path.dirname(p2), "INDEX.md"), "w") as f:
        f.write("|ID|t|f|v|s|d|a|\n|-|-|-|-|-|-|-|\n| chip2 | C2 | pdf | r | project | [d](chip2/digest.md) | - |\n")
    it2 = plan(os.path.join(tmp, "Repos", "p2"), groot, os.path.join(tmp, "Repos"))
    assert it2[0]["action"] == "pointer" and it2[0]["target"] == "qqchip"
    save(os.path.join(os.path.dirname(p2), ".migrate-plan.json"), it2)
    apply(os.path.join(tmp, "Repos", "p2"), groot)
    assert "qqchip2" in load(os.path.join(groot, "qqchip", "metadata.json"))["aliases"]
    cleanup(proj, groot)
    assert not os.path.exists(os.path.join(mroot, "qqchip")) and os.path.isdir(os.path.join(mroot, "board"))
    shutil.rmtree(tmp)
    print("selftest OK")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0

    def opt(name, default):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default
    groot = os.path.abspath(os.path.expanduser(opt("--global-root", "~/.claude/manuals")))
    scan = os.path.abspath(os.path.expanduser(opt("--scan-root", "~/Repos")))
    if len(argv) < 2 or argv[0] not in ("plan", "apply", "cleanup"):
        print(__doc__)
        return 2
    project = os.path.abspath(os.path.expanduser(argv[1]))
    if argv[0] == "plan":
        items = plan(project, groot, scan)
        save(os.path.join(project, ".claude", "manuals", ".migrate-plan.json"), items)
        if "--json" in argv:
            print(json.dumps(items, ensure_ascii=False, indent=2))
        else:
            print_plan(items)
        return 0
    return apply(project, groot) if argv[0] == "apply" else cleanup(project, groot)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
