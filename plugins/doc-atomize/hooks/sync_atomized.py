#!/usr/bin/env python3
"""원본이 수정되면 분할 조각을 자동 갱신하는 PostToolUse 훅.

Edit/Write/NotebookEdit 직후에 실행되어, 방금 고친 파일이 `doc-atomize`로
분할 등록된 문서인지 확인하고 맞으면 `split_md.py update`를 돌린다.

동작 원칙:
- **등록된 문서에만** 반응한다. `.claude/atomized/<id>/<id>.metadata.json`의
  `source`가 방금 고친 파일과 같을 때만 움직인다. 등록 전(검수 루프 중)에는
  아무 일도 하지 않는다 — 이는 prd-plan의 "검수 루프 중 분할 금지" 규칙과 맞물린다.
- **절대 실패하지 않는다.** 어떤 예외가 나도 exit 0으로 끝낸다. 문서 동기화 때문에
  사용자의 편집이 막히면 안 된다.
- 갱신 결과는 additionalContext로 돌려주어, 요약이 stale해진 조각을 모델이
  다시 다듬을 수 있게 한다.

Python 표준 라이브러리만 사용한다.
"""

import glob
import json
import os
import re
import subprocess
import sys

TIMEOUT_SEC = 25
MAX_ROOTS = 8


def emit(msg):
    """PostToolUse 훅 규약에 맞춰 컨텍스트를 돌려준다."""
    if not msg:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }, ensure_ascii=False))


def edited_path(payload):
    """훅 입력에서 편집된 파일 경로를 찾아낸다 (필드명이 버전에 따라 다를 수 있다)."""
    for container in (payload.get("tool_input"), payload.get("tool_response"), payload):
        if not isinstance(container, dict):
            continue
        for key in ("file_path", "filePath", "path", "notebook_path"):
            val = container.get(key)
            if isinstance(val, str) and val.strip():
                return val
    return None


def atomized_roots(target, cwd):
    """탐색할 .claude/atomized 디렉토리들 — 파일 위쪽으로 올라가며 + cwd + global."""
    roots, seen = [], set()

    def add(path):
        if path and os.path.isdir(path) and path not in seen:
            seen.add(path)
            roots.append(path)

    node = os.path.dirname(os.path.abspath(target))
    while True:
        add(os.path.join(node, ".claude", "atomized"))
        parent = os.path.dirname(node)
        if parent == node or len(roots) >= MAX_ROOTS:
            break
        node = parent
    if cwd:
        add(os.path.join(os.path.abspath(cwd), ".claude", "atomized"))
    add(os.path.expanduser("~/.claude/atomized"))
    return roots


def find_registration(target):
    """target을 원본으로 삼는 분할 디렉토리를 찾는다. (디렉토리, doc_id) 또는 None."""
    target = os.path.realpath(target)
    for root in atomized_roots(target, os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()):
        for meta in glob.glob(os.path.join(root, "*", "*.metadata.json")):
            try:
                with open(meta, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception:
                continue
            src = data.get("source")
            if not src:
                continue
            if os.path.realpath(os.path.expanduser(src)) == target:
                return os.path.dirname(meta), data.get("id") or os.path.basename(os.path.dirname(meta))
    return None


def find_split_md():
    """split_md.py 위치를 찾는다 — 환경변수 → 플러그인 캐시 → 개발 레포 순."""
    override = os.environ.get("DOC_ATOMIZE_SPLIT_MD")
    if override and os.path.isfile(override):
        return override

    # 이 훅 자신이 플러그인 안에 있으므로 형제 경로를 먼저 본다
    here = os.path.dirname(os.path.abspath(__file__))
    sibling = os.path.join(os.path.dirname(here), "skills", "doc-atomize", "assets", "split_md.py")
    if os.path.isfile(sibling):
        return sibling

    patterns = [
        os.path.expanduser("~/.claude/plugins/**/doc-atomize/**/skills/doc-atomize/assets/split_md.py"),
    ]
    found = []
    for pat in patterns:
        found.extend(glob.glob(pat, recursive=True))
    if not found:
        return None

    def version_key(path):
        nums = [int(x) for x in re.findall(r"/(\d+)\.(\d+)\.(\d+)/", path)[0]] if re.findall(r"/(\d+)\.(\d+)\.(\d+)/", path) else [0, 0, 0]
        return (nums, os.path.getmtime(path))

    try:
        found.sort(key=version_key, reverse=True)
    except Exception:
        found.sort(key=os.path.getmtime, reverse=True)
    return found[0]


def python_cmd():
    return [sys.executable] if sys.executable else ["python3"]


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except Exception:
        return 0

    target = edited_path(payload)
    if not target or not target.endswith((".md", ".markdown")):
        return 0
    if not os.path.isfile(target):
        return 0

    reg = find_registration(target)
    if not reg:
        return 0                      # 등록되지 않은 문서 — 아무 일도 하지 않는다
    doc_dir, doc_id = reg

    script = find_split_md()
    if not script:
        emit("[doc-atomize] `{}`의 분할본이 원본보다 오래됐을 수 있는데 split_md.py를 찾지 못해 "
             "자동 갱신하지 못했습니다. `/doc-atomize --update {}`를 실행하세요.".format(doc_id, doc_id))
        return 0

    try:
        proc = subprocess.run(
            python_cmd() + [script, "update", doc_dir],
            capture_output=True, text=True, timeout=TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        emit("[doc-atomize] `{}` 자동 갱신이 {}초 안에 끝나지 않았습니다. "
             "`/doc-atomize --update {}`로 직접 갱신하세요.".format(doc_id, TIMEOUT_SEC, doc_id))
        return 0
    except Exception as exc:
        emit("[doc-atomize] `{}` 자동 갱신 실패({}). `/doc-atomize --update {}`로 직접 갱신하세요."
             .format(doc_id, type(exc).__name__, doc_id))
        return 0

    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()

    if proc.returncode != 0:
        emit("[doc-atomize] `{}` 자동 갱신 실패 (exit {}). {}\n"
             "무손실이 깨졌을 수 있으니 `/doc-atomize --verify {}`로 확인하세요."
             .format(doc_id, proc.returncode, (err or out)[:300], doc_id))
        return 0

    if "변경 없음" in out or "동일" in out or not out:
        return 0                      # 내용이 그대로면 조용히 끝낸다

    msg = "[doc-atomize] 원본이 바뀌어 `{}` 분할본을 자동 갱신했습니다.\n{}".format(doc_id, out[:800])
    if "stale" in out.lower() or "⚠" in out:
        msg += ("\n→ ⚠️ 표시된 조각은 **본문이 바뀌었는데 요약은 이전 것**입니다. "
                "해당 조각의 요약을 다시 쓰고 `split_md.py reindex {}`를 실행하세요.".format(doc_dir))
    emit(msg)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)                   # 훅이 사용자의 편집을 막지 않는다
