#!/usr/bin/env python3
"""orca.yaml 정적 검사기 — Orca 워크트리 훅 전용.

PyYAML을 쓰지 않는다. Orca가 인식하는 orca.yaml은 최상위 키 4개와 블록 스칼라
위주의 좁은 서브셋이라 표준 라이브러리만으로 충분히 검사할 수 있고, 무엇보다
PyYAML이 없는 호스트에서 검사 자체가 불가능해지는 상황을 피하기 위해서다.

서브커맨드
  check   <orca.yaml>              구조 + 스크립트 안티패턴 검사 (기본)
  extract <orca.yaml> --hook setup|archive [--out FILE]
                                   블록 스칼라 본문만 추출 (드라이런 입력용)

종료 코드: 0 = CRITICAL 없음, 1 = CRITICAL 있음, 2 = 파일/인자 오류
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Orca가 인식하는 최상위 키. 이 밖의 키는 조용히 무시되므로 오타가 곧 기능 상실이다.
RECOGNIZED_TOP_KEYS = {"scripts", "issueCommand", "defaultTabs", "environmentRecipes"}
RECOGNIZED_SCRIPT_KEYS = {"setup", "archive"}

# 명령 위치(줄 시작 / 파이프·리스트 구분자 뒤 / 서브셸 시작)에서만 매칭시키기 위한 접두.
# 이것이 없으면 `cmake --preset ninja` 의 preset 이름이 ninja 빌드로 오탐된다.
CMD = r"(?:^|[;&|(]|&&|\|\||\bthen\b|\bdo\b|\belse\b)\s*(?:sudo\s+)?"

# 120초 예산에서 단독으로 위험한 명령들 (빌드/네트워크 대량 수신)
HEAVY_PATTERNS = [
    (r"\bcmake\s+--build\b", "cmake --build (전체 빌드)"),
    (CMD + r"ninja\b(?!\s+--version)", "ninja 빌드"),
    (CMD + r"make\b(?!\s*-(?:v|-version))", "make 빌드"),
    (r"\bcargo\s+(?:build|test)\b", "cargo build/test"),
    (r"\bgo\s+(?:build|test)\b", "go build/test"),
    (r"\bdotnet\s+(?:build|test|publish)\b", "dotnet build/test"),
    (r"\b(?:npm|pnpm|yarn|bun)\s+run\s+build\b", "프론트엔드 번들 빌드"),
    (r"\bdocker\s+(?:build|compose\s+up)\b", "docker 빌드/기동"),
    (CMD + r"\.?/?gradlew?\b", "gradle"),
    (CMD + r"(?:pytest|ctest)\b", "테스트 실행"),
    (r"\bgit\s+clone\b", "git clone (네트워크)"),
    (r"\bgit\s+lfs\s+(?:pull|fetch|checkout)\b", "git lfs 대용량 수신"),
]

# 워크트리를 넘어 원본/호스트를 훼손할 수 있는 명령들
DESTRUCTIVE_PATTERNS = [
    (r"\brm\s+-[rRf]*[rR][rRf]*\s+[\"']?(?:/|\$HOME|~|\$\{?ORCA_ROOT_PATH)", "레포 밖/메인 체크아웃을 향한 rm -rf"),
    (r"\bgit\s+clean\b", "git clean (미추적 파일 파괴)"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard"),
    (r"\bgit\s+checkout\s+(?:--\s+)?\.", "git checkout . (작업분 파괴)"),
    (r"\bgit\s+push\b", "git push (setup 훅에서 원격 조작)"),
    (r"\bsudo\b", "sudo (호스트 상태 변경)"),
    (r">\s*[\"']?\$\{?ORCA_ROOT_PATH", "메인 체크아웃으로의 출력 리다이렉션"),
]

SECRET_PATTERNS = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "개인키 원문"),
    (r"\bghp_[A-Za-z0-9]{20,}", "GitHub 토큰"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS 액세스 키"),
    (r"\bsk-[A-Za-z0-9]{20,}", "API 시크릿 키"),
    (r"(?i)\b(?:password|passwd|secret|api[_-]?key|token)\s*=\s*[\"'][^\"'$]{8,}[\"']", "하드코딩된 자격증명"),
]

HOST_PATH_PATTERNS = [
    (r"/home/[A-Za-z0-9._-]+/", "리눅스 홈 절대경로"),
    (r"/Users/[A-Za-z0-9._-]+/", "macOS 홈 절대경로"),
    (r"[A-Za-z]:\\\\?Users\\\\?", "Windows 홈 절대경로"),
]


class Finding:
    __slots__ = ("severity", "code", "line", "message", "fix")

    def __init__(self, severity, code, line, message, fix=""):
        self.severity = severity
        self.code = code
        self.line = line
        self.message = message
        self.fix = fix

    def as_dict(self):
        return {
            "severity": self.severity,
            "code": self.code,
            "line": self.line,
            "message": self.message,
            "fix": self.fix,
        }


SEVERITY_ORDER = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2, "INFO": 3}


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def strip_comment(line):
    """따옴표 밖의 # 이후를 잘라낸다 (거친 근사 — 구조 검사용으로 충분)."""
    out, quote = [], None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out)


KEY_RE = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_.-]*)\s*:(.*)$")


def parse_structure(lines):
    """최상위 키와 scripts 하위 훅의 위치·블록 본문을 뽑는다.

    반환: (top_keys, hooks, findings)
      top_keys : [(line_no, key)]
      hooks    : {name: {"line": n, "indicator": str, "body": str, "body_start": n}}
    """
    findings = []
    top_keys = []
    hooks = {}

    # 들여쓰기 탭 — YAML은 탭을 들여쓰기로 허용하지 않는다. Orca는 파싱 실패 시
    # 훅을 통째로 무시하므로 조용한 기능 상실이 된다.
    for i, raw in enumerate(lines, 1):
        if raw.startswith("\t") or re.match(r"^ *\t", raw):
            findings.append(
                Finding("CRITICAL", "YAML_TAB", i,
                        "들여쓰기에 탭이 있다 — YAML 파싱이 실패하고 Orca가 훅 전체를 무시한다",
                        "탭을 공백으로 바꾼다")
            )
            break

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        line_no = i + 1
        body = strip_comment(raw)
        if not body.strip():
            i += 1
            continue
        m = KEY_RE.match(body)
        if not m:
            i += 1
            continue
        indent, key, rest = len(m.group(1)), m.group(2), m.group(3).strip()

        if indent == 0:
            top_keys.append((line_no, key))
            if key != "scripts":
                i += 1
                continue
            # scripts 블록 안을 훑는다
            j = i + 1
            while j < n:
                sub_raw = lines[j]
                if not sub_raw.strip():
                    j += 1
                    continue
                sub_body = strip_comment(sub_raw)
                if not sub_body.strip():
                    j += 1
                    continue
                sm = KEY_RE.match(sub_body)
                if sm and len(sm.group(1)) == 0:
                    break  # 다음 최상위 키
                if not sm or len(sm.group(1)) == 0:
                    j += 1
                    continue
                sub_indent, sub_key, sub_rest = len(sm.group(1)), sm.group(2), sm.group(3).strip()
                if sub_indent == 0:
                    break
                if sub_key not in RECOGNIZED_SCRIPT_KEYS:
                    findings.append(
                        Finding("CRITICAL", "UNKNOWN_HOOK", j + 1,
                                f"scripts 하위의 '{sub_key}'는 인식되지 않는다 (setup·archive만 유효)",
                                "키 이름을 확인한다 — 오타는 조용히 무시된다")
                    )
                    j += 1
                    continue
                if sub_key in hooks:
                    findings.append(
                        Finding("CRITICAL", "DUP_HOOK", j + 1,
                                f"scripts.{sub_key}가 중복 정의됐다 — 뒤의 것만 남거나 파싱이 깨진다",
                                "중복 정의를 하나로 합친다")
                    )
                indicator = sub_rest
                body_lines, body_start = [], j + 2
                if indicator.startswith("|") or indicator.startswith(">"):
                    # 블록 스칼라 — 더 깊은 들여쓰기가 이어지는 동안 수집
                    k = j + 1
                    block_indent = None
                    while k < n:
                        cur = lines[k]
                        if not cur.strip():
                            body_lines.append("")
                            k += 1
                            continue
                        cur_indent = len(cur) - len(cur.lstrip(" "))
                        if cur_indent <= sub_indent:
                            break
                        if block_indent is None:
                            block_indent = cur_indent
                        body_lines.append(cur[block_indent:] if len(cur) >= block_indent else cur.lstrip(" "))
                        k += 1
                    if not body_lines or not any(b.strip() for b in body_lines):
                        findings.append(
                            Finding("CRITICAL", "EMPTY_BLOCK", j + 1,
                                    f"scripts.{sub_key}의 블록 스칼라 본문이 비어 있다",
                                    "본문을 한 단계 더 들여쓴다")
                        )
                    j = k
                elif indicator:
                    # 인라인 스칼라 — 한 줄짜리 명령. 허용되지만 확장성이 없다.
                    body_lines = [indicator.strip("\"'")]
                    findings.append(
                        Finding("INFO", "INLINE_SCALAR", j + 1,
                                f"scripts.{sub_key}가 인라인 한 줄이다",
                                "여러 단계로 늘어나면 블록 스칼라(|)나 tools/orca-setup.sh 분리를 쓴다")
                    )
                    j += 1
                else:
                    findings.append(
                        Finding("CRITICAL", "NO_INDICATOR", j + 1,
                                f"scripts.{sub_key}에 값이 없다",
                                "'setup: |' 형태의 블록 스칼라로 본문을 준다")
                    )
                    j += 1
                hooks[sub_key] = {
                    "line": j,
                    "indicator": indicator,
                    "body": "\n".join(body_lines).rstrip() + "\n" if body_lines else "",
                    "body_start": body_start,
                }
            i = j
            continue
        i += 1

    seen = set()
    for line_no, key in top_keys:
        if key not in RECOGNIZED_TOP_KEYS:
            findings.append(
                Finding("CRITICAL", "UNKNOWN_TOP_KEY", line_no,
                        f"최상위 키 '{key}'는 Orca가 인식하지 않는다 "
                        "(scripts · issueCommand · defaultTabs · environmentRecipes만 유효)",
                        "키를 제거하거나 올바른 이름으로 고친다 — 미인식 키는 조용히 무시된다")
            )
        if key in seen:
            findings.append(
                Finding("CRITICAL", "DUP_TOP_KEY", line_no, f"최상위 키 '{key}'가 중복됐다", "하나로 합친다")
            )
        seen.add(key)

    return top_keys, hooks, findings


def scan_script(name, body, body_start):
    """훅 본문의 안티패턴을 검사한다."""
    findings = []
    if not body.strip():
        return findings

    lines = body.splitlines()

    def line_no(idx):
        return body_start + idx

    # Orca는 생성하는 러너 앞에 `set -e`를 주입한다. 해제하지 않으면 첫 실패에서
    # 스크립트가 통째로 죽어 이후 단계가 전부 누락된다 (pnpm ERR_PNPM_IGNORED_BUILDS 실측).
    has_set_plus_e = re.search(r"^\s*set\s+[+-]?[^\n]*\+e|^\s*set\s+\+e", body, re.M) or re.search(
        r"^\s*set\s+\+[a-z]*e", body, re.M
    )
    delegates = re.search(r"^\s*(?:bash|sh|\.|source)\s+\S*orca[-_]setup\S*\.sh", body, re.M)
    if not has_set_plus_e:
        sev = "MINOR" if delegates else "MAJOR"
        msg = ("Orca가 주입하는 `set -e`를 해제하지 않았다 — 어떤 단계든 0이 아닌 종료코드를 내면 "
               "나머지 단계가 통째로 건너뛰어진다")
        if delegates:
            msg += " (외부 스크립트에 위임 중 — 그 스크립트에서 해제했는지 확인한다)"
        findings.append(Finding(sev, "SET_E_TRAP", body_start, msg, "본문 첫머리에 `set +e`를 둔다"))

    for idx, ln in enumerate(lines):
        code = strip_comment(ln)
        if not code.strip():
            continue
        for pat, label in DESTRUCTIVE_PATTERNS:
            if re.search(pat, code):
                findings.append(
                    Finding("CRITICAL", "DESTRUCTIVE", line_no(idx),
                            f"{name} 훅에 파괴적 명령: {label} — `{code.strip()[:80]}`",
                            "워크트리 안으로 범위를 좁히거나 제거한다")
                )
        for pat, label in SECRET_PATTERNS:
            if re.search(pat, code):
                findings.append(
                    Finding("CRITICAL", "SECRET", line_no(idx),
                            f"{name} 훅에 자격증명이 하드코딩된 것으로 보인다: {label} — orca.yaml은 커밋된다",
                            "메인 체크아웃의 미추적 파일에서 복사하는 방식으로 바꾼다")
                )
        for pat, label in HEAVY_PATTERNS:
            if re.search(pat, code):
                findings.append(
                    Finding("MAJOR", "TIMEOUT_RISK", line_no(idx),
                            f"{name} 훅에 무거운 단계: {label} — 120초 타임아웃을 넘길 수 있다",
                            "configure/의존성 설치까지만 남기고 빌드는 제외한다")
                )
        for pat, label in HOST_PATH_PATTERNS:
            if re.search(pat, code):
                findings.append(
                    Finding("MAJOR", "HOST_PATH", line_no(idx),
                            f"{name} 훅에 호스트 절대경로({label}) — 팀원의 다른 호스트에서 깨진다",
                            "$ORCA_ROOT_PATH · $ORCA_WORKTREE_PATH 로 대체한다")
                )

    # archive 훅에서 링크 해제 전 -L 검사를 하지 않으면 원본 디렉토리를 지울 수 있다.
    if name == "archive" and re.search(r"\brm\b", body):
        if not re.search(r"-L\s", body):
            findings.append(
                Finding("CRITICAL", "UNGUARDED_UNLINK", body_start,
                        "archive 훅이 -L(심볼릭 링크) 검사 없이 rm 한다 — "
                        "링크가 아니라 실제 디렉토리였다면 메인 체크아웃의 원본이 사라진다",
                        '`if [ -L "$p" ]; then rm -f "$p"; fi` 형태로 바꾼다')
            )

    # 워크트리 밖에서 실행될 위험 — cwd 고정 여부
    if not re.search(r"ORCA_WORKTREE_PATH", body) and not delegates:
        findings.append(
            Finding("MINOR", "NO_CWD_ANCHOR", body_start,
                    f"{name} 훅이 $ORCA_WORKTREE_PATH를 쓰지 않는다 — cwd 가정에 의존한다",
                    'WT="${ORCA_WORKTREE_PATH:-$PWD}"; cd "$WT" || exit 0 로 고정한다')
        )

    # 이식성 — bash 전용 스크립트는 Windows(cmd.exe) 호스트에서 실행되지 않는다.
    if not re.search(r"(?i)windows|ComSpec|MSYS|MINGW", body):
        findings.append(
            Finding("INFO", "WINDOWS", body_start,
                    f"{name} 훅에 Windows 분기가 없다 — Windows 호스트에서는 cmd.exe로 실행되어 동작하지 않는다",
                    "Windows에서 워크트리를 만드는 팀원이 생기면 분기 또는 주석 경고를 추가한다")
        )

    return findings


def bash_syntax_check(name, body):
    findings = []
    bash = shutil.which("bash")
    if not bash or not body.strip():
        return findings
    tmp = tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False, encoding="utf-8")
    try:
        tmp.write(body)
        tmp.close()
        proc = subprocess.run([bash, "-n", tmp.name], capture_output=True, text=True)
        if proc.returncode != 0:
            detail = (proc.stderr or "").strip().replace(tmp.name, f"<{name}>")
            findings.append(
                Finding("CRITICAL", "BASH_SYNTAX", 0,
                        f"{name} 훅이 bash 문법 오류다: {detail[:300]}",
                        "문법을 고친다 — 이 상태로는 훅이 즉시 실패한다")
            )
    finally:
        os.unlink(tmp.name)
    return findings


def cmd_check(args):
    if not os.path.isfile(args.path):
        print(f"파일을 찾을 수 없다: {args.path}", file=sys.stderr)
        return 2

    lines = read_lines(args.path)
    top_keys, hooks, findings = parse_structure(lines)

    for name, info in hooks.items():
        findings.extend(scan_script(name, info["body"], info["body_start"]))
        findings.extend(bash_syntax_check(name, info["body"]))

    if "scripts" not in {k for _, k in top_keys}:
        findings.append(
            Finding("MAJOR", "NO_SCRIPTS", 0, "scripts 키가 없다 — 워크트리 훅이 정의되지 않았다",
                    "scripts.setup을 추가한다")
        )
    elif "setup" not in hooks:
        findings.append(
            Finding("MAJOR", "NO_SETUP", 0, "scripts.setup이 없다", "setup 훅을 추가한다")
        )

    findings.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.line))
    counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITY_ORDER}

    if args.json:
        print(json.dumps({
            "file": args.path,
            "top_keys": [k for _, k in top_keys],
            "hooks": {k: {"lines": v["body"].count("\n")} for k, v in hooks.items()},
            "counts": counts,
            "findings": [f.as_dict() for f in findings],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"orca.yaml 검사: {args.path}")
        print(f"  최상위 키 : {', '.join(k for _, k in top_keys) or '(없음)'}")
        for k, v in hooks.items():
            print(f"  scripts.{k} : {v['body'].count(chr(10))}줄")
        print()
        if not findings:
            print("지적 사항 없음.")
        for f in findings:
            loc = f"L{f.line}" if f.line else "-"
            print(f"[{f.severity}] {loc} {f.code}: {f.message}")
            if f.fix:
                print(f"         → {f.fix}")
        print()
        print("요약: " + " · ".join(f"{s} {counts[s]}" for s in SEVERITY_ORDER))

    return 1 if counts["CRITICAL"] else 0


def cmd_extract(args):
    if not os.path.isfile(args.path):
        print(f"파일을 찾을 수 없다: {args.path}", file=sys.stderr)
        return 2
    _, hooks, _ = parse_structure(read_lines(args.path))
    if args.hook not in hooks:
        print(f"scripts.{args.hook} 훅이 없다", file=sys.stderr)
        return 2
    body = hooks[args.hook]["body"]
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(body)
        print(args.out)
    else:
        sys.stdout.write(body)
    return 0


def main():
    ap = argparse.ArgumentParser(description="orca.yaml 워크트리 훅 정적 검사기")
    sub = ap.add_subparsers(dest="cmd")

    p_check = sub.add_parser("check", help="구조 + 안티패턴 검사")
    p_check.add_argument("path")
    p_check.add_argument("--json", action="store_true")
    p_check.set_defaults(func=cmd_check)

    p_ext = sub.add_parser("extract", help="훅 본문 추출")
    p_ext.add_argument("path")
    p_ext.add_argument("--hook", default="setup", choices=sorted(RECOGNIZED_SCRIPT_KEYS))
    p_ext.add_argument("--out")
    p_ext.set_defaults(func=cmd_extract)

    args = ap.parse_args()
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
