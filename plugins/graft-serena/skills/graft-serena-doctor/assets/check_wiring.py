#!/usr/bin/env python3
"""graft + serena 병행 배선 점검 — 기본은 읽기 전용.

두 도구를 병행해 쓰려면 레포마다 세 가지가 맞아 있어야 한다. 하나라도
틀어지면 도구는 조용히 빈 결과를 돌려주고, 그 사실이 몇 주씩 안 보인다.

  A. graft  — CLI·MCP 등록·그래프 실존(INDEX.md)·그래프 신선도
  B. serena — 설치·.serena/project.yml·language_servers·조상 설정 간섭
  C. rtk    — 설치·이름 충돌·훅 등록

--fix 는 "파일을 고치면 끝나는 것"만 고친다(serena project.yml). 그래프
빌드와 패키지 설치는 명령만 출력한다 — 시간·네트워크를 쓰는 일은 사람이 건다.

사용법: check_wiring.py [--repo PATH] [--fix] [--json] [--strict] [--selftest]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

# 확장자 → serena language_servers 값.
# installed 는 이 머신의 ~/.serena/language_servers/static/ 기준 기대값이며,
# 실제 설치 여부는 아래 installed_language_servers() 가 다시 확인한다.
LANG_MAP = {
    "python": [".py", ".pyi"],
    "cpp": [".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"],
    "typescript": [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"],
    "vue": [".vue"],
    "csharp": [".cs"],
}
# LANG_MAP 에 없지만 serena 가 지원할 수 있는 코드 확장자 → 언어 이름.
# 여기 없는 확장자는 보고하지 않는다 — 세상의 확장자를 다 열거하는 것보다
# 아는 것만 말하는 편이 조용하다(.pdf·.rep 같은 데이터 파일이 섞여 들어온다).
OTHER_CODE_EXT = {".rs": "rust", ".go": "go", ".java": "java", ".rb": "ruby",
                  ".php": "php", ".kt": "kotlin", ".swift": "swift",
                  ".lua": "lua", ".scala": "scala", ".dart": "dart",
                  ".ex": "elixir", ".exs": "elixir", ".zig": "zig",
                  ".clj": "clojure"}
LANG_MIN_FILES = 3  # 이 개수 미만은 우연히 섞인 파일로 본다
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "graft", "build", "dist",
             "__pycache__", ".serena", ".claude", "target", "out"}

SEV_ORDER = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2, "INFO": 3}


class Report:
    def __init__(self):
        self.findings = []
        self.fixed = []
        self.notes = []

    def add(self, sev, code, msg, action=""):
        self.findings.append({"severity": sev, "code": code,
                              "message": msg, "action": action})

    def worst(self):
        return min((SEV_ORDER[f["severity"]] for f in self.findings), default=99)


# ── 공통 ────────────────────────────────────────────────────────
def run(cmd, cwd=None, timeout=60):
    """(exit, stdout) 반환. 실행 자체가 실패하면 (None, "")."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout)
        return p.returncode, p.stdout
    except (OSError, subprocess.SubprocessError):
        return None, ""


def count(v):
    """graft check 의 드리프트 필드는 항목 리스트다(빈 리스트여도 리스트).
    버전에 따라 개수로 올 수도 있어 둘 다 받는다."""
    if isinstance(v, list):
        return len(v)
    return v or 0


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def repo_files(repo: Path):
    """추적 파일 우선. git 레포가 아니면 walk 로 폴백한다."""
    code, out = run(["git", "ls-files"], cwd=str(repo))
    if code == 0 and out.strip():
        return [repo / line for line in out.splitlines() if line]
    files = []
    for root, dirs, names in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        files.extend(Path(root) / n for n in names)
    return files


def detect_languages(files):
    """(serena 언어 집합, 미매핑 확장자 카운터, 코드 파일 수)."""
    ext_count = Counter(f.suffix.lower() for f in files)
    langs, code_files = set(), 0
    for lang, exts in LANG_MAP.items():
        n = sum(ext_count.get(e, 0) for e in exts)
        code_files += n
        if n >= LANG_MIN_FILES:
            langs.add(lang)
    unmapped = Counter({e: n for e, n in ext_count.items()
                        if e in OTHER_CODE_EXT and n >= LANG_MIN_FILES})
    return langs, unmapped, code_files + sum(unmapped.values())


def installed_language_servers():
    d = Path.home() / ".serena" / "language_servers" / "static"
    if not d.is_dir():
        return None  # 알 수 없음 — 판단 보류
    names = {p.name.lower() for p in d.iterdir()}
    present = set()
    for lang, needle in (("python", "pyright"), ("cpp", "clangd"),
                         ("typescript", "typescript"), ("vue", "vue")):
        if any(needle in n for n in names):
            present.add(lang)
    return present


# ── A. graft ────────────────────────────────────────────────────
def check_graft(repo: Path, rep: Report, code_files: int):
    if not shutil.which("graft"):
        rep.add("MAJOR", "GRAFT_CLI_MISSING", "graft CLI 가 PATH 에 없다",
                "graft 를 설치하고 PATH 를 확인한다")
    # MCP 등록 — 전역 + 이 프로젝트 양쪽을 본다
    cj = load_json(Path.home() / ".claude.json") or {}
    servers = set(cj.get("mcpServers", {}))
    servers |= set(cj.get("projects", {}).get(str(repo), {})
                   .get("mcpServers", {}))
    if not any("graft" in s for s in servers):
        rep.add("MAJOR", "GRAFT_MCP_UNREGISTERED",
                "graft MCP 서버가 등록돼 있지 않다 — graft_* 도구를 못 부른다",
                "claude mcp add graft -- graft mcp")

    gdir, index = repo / "graft", repo / "graft" / "INDEX.md"
    doc_only = code_files < LANG_MIN_FILES
    if not index.is_file():
        if gdir.is_dir():
            # .cache 만 남은 상태 — 디렉토리가 있어 '있는 것처럼' 보인다
            rep.add("INFO" if doc_only else "MAJOR", "GRAFT_CACHE_ONLY",
                    "graft/ 는 있지만 INDEX.md 가 없다 — 그래프 본체가 없다"
                    + (" (심볼 없는 레포라 정상)" if doc_only else ""),
                    "" if doc_only else f"cd {repo} && graft build")
        else:
            rep.add("INFO" if doc_only else "MAJOR", "GRAFT_NO_GRAPH",
                    "graft 그래프가 없다"
                    + (" (심볼 없는 레포라 정상)" if doc_only else ""),
                    "" if doc_only else f"cd {repo} && graft build")
        return
    # 그래프가 있으면 신선도를 graft 자신에게 묻는다.
    # 주의: stale 이어도 exit 0 이라 JSON 을 파싱해야 한다.
    _, out = run(["graft", "check", "--json"], cwd=str(repo), timeout=120)
    data = None
    try:
        data = json.loads(out)
    except ValueError:
        pass
    if data is None:
        rep.notes.append("graft check 결과를 해석하지 못했다 — 신선도 판정 생략")
        return
    build = f"cd {repo} && graft build"
    # graft 산출물은 두 층이다. 한 층만 멀쩡한 경우가 실제로 흔하다.
    #   context — 파일 카드 (graft_file_api·repo_map 이 읽는다)
    #   graph   — 배선 그래프 (find_code·trace_calls 가 읽는다)
    ctx = data.get("context") or {}
    # 카드 실존은 파일을 세어 판정한다. check 의 context.missing 은
    # "graft/manifest.json 이 없다"는 뜻이고, 카드가 멀쩡한 그래프에서도
    # 참으로 나온다(구 버전으로 빌드된 그래프) — 그것으로 판정하면 전 레포 오탐이다.
    cards = sum(1 for f in (repo / "graft").rglob("*.md")
                if f.name != "INDEX.md")
    if cards == 0:
        rep.add("MAJOR", "GRAFT_CARDS_MISSING",
                "파일 카드가 한 장도 없다 — graft_file_api·graft_repo_map 이 빈다",
                build)
    if ctx.get("missing"):
        rep.add("INFO", "GRAFT_MANIFEST_ABSENT",
                f"graft/manifest.json 이 없어 카드 {cards}장의 내용 드리프트를 "
                "판정할 수 없다 (배선 그래프 판정은 그대로 유효하다)",
                f"판정까지 원하면 {build}")
    elif ctx.get("ok") is False:
        n = sum(count(ctx.get(k)) for k in
                ("contentDrift", "removed", "coverage", "indexDrift"))
        rep.add("MINOR", "GRAFT_CARDS_STALE",
                f"파일 카드가 소스보다 오래됐다 (불일치 {n}건)", build)

    graph = data.get("graph")
    if graph is None:
        rep.add("INFO", "GRAFT_WIRING_ABSENT",
                "배선 그래프(graph.json)가 없다 — 카드 층만 쓸 수 있다", build)
        return
    if graph.get("missing"):
        rep.add("MAJOR", "GRAFT_WIRING_MISSING",
                "배선 그래프가 비어 있다 — find_code·trace_calls 가 빈다", build)
    else:
        n = sum(count(graph.get(k))
                for k in ("added", "removed", "changed", "stale"))
        if n:
            rep.add("MINOR", "GRAFT_WIRING_STALE",
                    f"배선 그래프가 소스와 어긋났다 (변경 {n}건)", build)
    pending = count(graph.get("pending"))
    if pending:
        # --deep 은 LLM 패스라 키와 비용이 든다 — 고장이 아니라 선택이다
        rep.add("INFO", "GRAFT_DEEP_PENDING",
                f"심볼 {pending}개가 LLM 요약(--deep) 대기 — 요약·crux 없이 "
                "배선만 쓰는 상태다",
                f"필요하면 {build} --deep (LLM 키·비용 발생)")


# ── B. serena ───────────────────────────────────────────────────
def find_language_servers_block(lines):
    """(키 줄 인덱스, 블록 끝 인덱스, 인라인 값 여부). 없으면 (None, None, False).

    구 키 이름 `languages:` 도 받는다 — serena 가 `language_servers` 로 리네임한
    필드라 옛 설정 파일에 남아 있다. 못 읽으면 '비어 있다'로 오판한다.
    """
    for i, line in enumerate(lines):
        m = re.match(r"^(?:language_servers|languages):(.*)$", line)
        if not m:
            continue
        if m.group(1).strip():
            return i, i + 1, True
        j = i + 1
        while j < len(lines) and re.match(r"^\s*-\s+\S", lines[j]):
            j += 1
        return i, j, False
    return None, None, False


def patch_language_servers(text, langs):
    """language_servers 블록만 교체하고 나머지는 글자 그대로 보존한다."""
    block = ["language_servers:"] + [f"- {lang}" for lang in sorted(langs)]
    lines = text.splitlines()
    start, end, _ = find_language_servers_block(lines)
    if start is None:
        tail = "" if not lines or lines[-1].strip() == "" else "\n"
        return text + tail + "\n".join(block) + "\n"
    return "\n".join(lines[:start] + block + lines[end:]) + "\n"


def new_project_yml(name, langs):
    """최소 project.yml — 나머지 키는 serena 기본값에 맡긴다."""
    body = "\n".join(f"- {lang}" for lang in sorted(langs)) or "[]"
    joiner = "\n" if langs else " "
    return (f'project_name: "{name}"\n'
            f'encoding: "utf-8"\n'
            f'ignore_all_files_in_gitignore: true\n'
            f'language_servers:{joiner}{body}\n')


def read_configured_langs(path: Path):
    """project.yml 의 language_servers 값만 뽑는다 (PyYAML 불필요)."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    start, end, inline = find_language_servers_block(lines)
    if start is None:
        return None
    if inline:
        raw = lines[start].split(":", 1)[1].strip().strip("[]")
        return {v.strip().strip("'\"") for v in raw.split(",") if v.strip()}
    return {lines[i].split("-", 1)[1].strip().strip("'\"")
            for i in range(start + 1, end)}


def check_serena(repo: Path, rep: Report, langs, unmapped, do_fix):
    plugins = load_json(Path.home() / ".claude" / "plugins" /
                        "installed_plugins.json")
    cj = load_json(Path.home() / ".claude.json") or {}
    wired = ("serena" in json.dumps(plugins) if plugins else False) or \
            any("serena" in s for s in cj.get("mcpServers", {}))
    if not wired:
        rep.add("MAJOR", "SERENA_UNREGISTERED",
                "serena 가 플러그인·MCP 어느 쪽에도 보이지 않는다",
                "serena 플러그인 또는 MCP 서버를 등록한다")

    path = repo / ".serena" / "project.yml"
    # 조상 디렉토리의 project.yml — 자체 설정이 없을 때만 문제가 된다.
    # 자체 설정이 있으면 serena 는 그것으로 활성화하므로 상위는 무관하다.
    if not path.is_file():
        for parent in repo.parents:
            anc = parent / ".serena" / "project.yml"
            if anc.is_file():
                anc_langs = read_configured_langs(anc) or set()
                missing = langs - anc_langs
                rep.add("MAJOR" if missing else "INFO", "SERENA_ANCESTOR_COVER",
                        f"자체 설정이 없고 상위 {parent} 의 설정이 잡힌다 "
                        f"(language_servers: {sorted(anc_langs) or '없음'})"
                        + (f" — 이 레포의 {sorted(missing)} 를 못 띄운다"
                           if missing else ""),
                        "이 레포에 자체 .serena/project.yml 을 둔다"
                        if missing else "")
                break

    if not path.is_file():
        rep.add("MAJOR", "SERENA_NO_PROJECT",
                ".serena/project.yml 이 없다 — activate_project 가 실패한다",
                "--fix 로 생성")
        if do_fix and langs:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new_project_yml(repo.name, langs), encoding="utf-8")
            rep.fixed.append(f"생성: {path} (language_servers: {sorted(langs)})")
        return langs

    # project.local.yml 은 project.yml 을 **덮어쓴다**(serena 가 그렇게 로드한다).
    # 그래서 유효값도 수리 대상 파일도 local 쪽이다 — project.yml 을 고치면
    # 조용히 무시되는 '고친 척'이 된다.
    local = path.parent / "project.local.yml"
    local_langs = read_configured_langs(local) if local.is_file() else None
    if local_langs is not None:
        rep.add("INFO", "SERENA_LOCAL_OVERRIDE",
                f"project.local.yml 이 language_servers 를 덮어쓴다 "
                f"(유효값: {sorted(local_langs) or '비어 있음'})",
                "수리는 project.yml 이 아니라 이 파일에 한다")
        path = local
    configured = local_langs if local_langs is not None \
        else read_configured_langs(path)
    if not configured:
        # CLAUDE.md 기록된 고장 모양: 활성화가 0.0x초에 끝나고 심볼 도구가 전부 실패한다
        rep.add("CRITICAL", "SERENA_NO_LANGSERVER",
                "language_servers 가 비어 있다 — 언어 서버를 안 띄우므로 "
                "심볼 도구가 전부 실패한다 (활성화가 0.0x초에 끝나는 증상)",
                "--fix 로 탐지된 언어를 채운 뒤 serena MCP 재시작")
    else:
        missing = langs - configured
        if missing:
            rep.add("MAJOR", "SERENA_LANG_MISMATCH",
                    f"탐지된 언어 {sorted(missing)} 가 설정에 없다 "
                    f"(현재: {sorted(configured)})",
                    "--fix 로 추가한 뒤 serena MCP 재시작")
        unused = configured - langs - {"vue"}  # vue 는 ts 안에 섞여 잡히기 어렵다
        if unused:
            rep.add("INFO", "SERENA_LANG_UNUSED",
                    f"설정에 있으나 소스에서 안 잡힌 언어: {sorted(unused)}",
                    "쓰지 않으면 지워 활성화 시간을 줄인다")

    target = (configured or set()) | langs
    if do_fix and target and target != (configured or set()):
        shutil.copy2(path, str(path) + ".bak")
        path.write_text(patch_language_servers(
            path.read_text(encoding="utf-8"), target), encoding="utf-8")
        rep.fixed.append(f"수정: {path} → language_servers: {sorted(target)} "
                         f"(원본 {path.name}.bak)")

    if unmapped:
        rep.add("INFO", "SERENA_LANG_UNMAPPED",
                "language_servers 에 자동으로 넣지 않은 코드 언어: "
                + ", ".join(f"{OTHER_CODE_EXT[e]}({e} {n}개)"
                            for e, n in unmapped.most_common(5)),
                "쓰려면 language_servers 에 직접 추가한다 "
                "(serena 지원 여부는 확인이 필요하다)")

    present = installed_language_servers()
    if present is not None:
        nolocal = target - present
        if nolocal:
            rep.add("INFO", "SERENA_LS_NOT_LOCAL",
                    f"로컬에 언어 서버가 안 보이는 언어: {sorted(nolocal)}",
                    "첫 활성화가 오래 걸리거나 실패할 수 있다")
    return target


# ── C. rtk ──────────────────────────────────────────────────────
def check_rtk(rep: Report):
    if not shutil.which("rtk"):
        rep.add("MINOR", "RTK_MISSING", "rtk 가 PATH 에 없다",
                "rtk 를 설치한다 (없어도 graft/serena 는 동작한다)")
    else:
        # 이름 충돌 판별 — reachingforthejack/rtk(Rust Type Kit)에는 gain 이 없다
        code, _ = run(["rtk", "gain"], timeout=30)
        if code not in (0, None):
            rep.add("MAJOR", "RTK_NAME_COLLISION",
                    "rtk 가 있으나 `rtk gain` 이 실패한다 — 동명의 다른 rtk "
                    "(Rust Type Kit)일 수 있다",
                    "which rtk 로 바이너리를 확인한다")

    hooks = ""
    for f in ("settings.json", "settings.local.json"):
        p = Path.home() / ".claude" / f
        if p.is_file():
            hooks += json.dumps(load_json(p) or {}, ensure_ascii=False)
    if "rtk" not in hooks:
        rep.add("MINOR", "RTK_HOOK_MISSING",
                "rtk 재작성 훅이 ~/.claude/settings*.json 에 없다 — "
                "명령이 rtk 를 거치지 않아 절약이 안 걸린다",
                "rtk 훅을 등록한다")


# ── 출력 ────────────────────────────────────────────────────────
def render(rep: Report, repo: Path, langs, fixed_serena):
    print(f"레포: {repo}")
    print(f"탐지 언어: {sorted(langs) or '없음 (심볼 없는 레포)'}")
    print()
    if not rep.findings:
        print("배선 정상 — 지적 사항 없음")
    else:
        rep.findings.sort(key=lambda f: SEV_ORDER[f["severity"]])
        w = max(len(f["code"]) for f in rep.findings)
        for f in rep.findings:
            print(f"[{f['severity']:<8}] {f['code']:<{w}}  {f['message']}")
            if f["action"]:
                print(f"{'':>11}{'':<{w}}  → {f['action']}")
    for n in rep.notes:
        print(f"\n참고: {n}")
    if rep.fixed:
        print("\n수리한 것:")
        for f in rep.fixed:
            print(f"  - {f}")
        # 재활성화로는 안 고쳐진다 — 서버를 다시 띄워야 반영된다
        print("\n  serena MCP 서버를 재시작해야 반영된다 "
              "(activate_project 재호출로는 안 된다)")
    elif fixed_serena:
        print("\n(--fix 를 주면 serena project.yml 을 고친다. "
              "그래프 빌드·패키지 설치는 위 명령을 직접 실행한다)")


def selftest():
    t = 'project_name: "x"\nlanguage_servers:\n- cpp\nencoding: "utf-8"\n'
    out = patch_language_servers(t, {"cpp", "python"})
    assert out == ('project_name: "x"\nlanguage_servers:\n- cpp\n- python\n'
                   'encoding: "utf-8"\n'), out
    # 키가 없으면 뒤에 붙인다
    out = patch_language_servers('project_name: "x"\n', {"python"})
    assert out.endswith("language_servers:\n- python\n"), out
    # 인라인 값도 교체된다
    out = patch_language_servers("language_servers: [cpp]\nencoding: \"utf-8\"\n",
                                 {"python"})
    assert out == 'language_servers:\n- python\nencoding: "utf-8"\n', out
    # 값 읽기 — 블록 / 인라인 양쪽
    assert find_language_servers_block(["language_servers:", "- a", "- b",
                                        "x: 1"]) == (0, 3, False)
    # 구 키 이름도 읽고, 치환 시에는 새 이름으로 쓴다
    assert find_language_servers_block(["languages:", "- cpp"]) == (0, 2, False)
    out = patch_language_servers("languages:\n- cpp\n", {"cpp", "python"})
    assert out == "language_servers:\n- cpp\n- python\n", out
    # 드리프트 필드는 리스트로도 개수로도 온다 (실측: 같은 CLI 가 둘 다 준다)
    assert count([1, 2, 3]) == 3 and count([]) == 0
    assert count(7) == 7 and count(None) == 0 and count(0) == 0
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(add_help=True, description=__doc__)
    ap.add_argument("--repo")
    ap.add_argument("--fix", action="store_true",
                    help="serena project.yml 을 고친다 (백업 후)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="CRITICAL/MAJOR 가 있으면 exit 1")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0

    repo = Path(a.repo).resolve() if a.repo else None
    if repo is None:
        code, out = run(["git", "rev-parse", "--show-toplevel"])
        repo = Path(out.strip()).resolve() if code == 0 and out.strip() \
            else Path.cwd()
    if not repo.is_dir():
        print(f"경로 접근 실패: {repo}", file=sys.stderr)
        return 2

    rep = Report()
    files = repo_files(repo)
    langs, unmapped, code_files = detect_languages(files)
    # 코드가 전체의 한 줌뿐이면 문서 레포다(템플릿 몇 개로 코드 레포가 되지 않는다)
    if files and code_files / len(files) < 0.10:
        code_files = 0
    check_graft(repo, rep, code_files)
    target = check_serena(repo, rep, langs, unmapped, a.fix)
    check_rtk(rep)

    fixable = any(f["code"].startswith("SERENA_") and
                  f["code"] in ("SERENA_NO_PROJECT", "SERENA_NO_LANGSERVER",
                                "SERENA_LANG_MISMATCH")
                  for f in rep.findings)
    if a.json:
        print(json.dumps({"repo": str(repo), "languages": sorted(langs),
                          "serena_language_servers": sorted(target or []),
                          "findings": rep.findings, "fixed": rep.fixed,
                          "notes": rep.notes}, ensure_ascii=False, indent=2))
    else:
        render(rep, repo, langs, fixable and not a.fix)
    return 1 if (a.strict and rep.worst() <= SEV_ORDER["MAJOR"]) else 0


if __name__ == "__main__":
    sys.exit(main())
