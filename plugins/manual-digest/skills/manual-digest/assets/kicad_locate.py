#!/usr/bin/env python3
"""부품 다이제스트의 KiCad 파일(심볼·풋프린트·3D 모델) 위치를 찾고 확인한다.

파일을 복사하거나 만들지 않는다. KiCad 자체의 라이브러리 표(sym-lib-table / fp-lib-table)를
읽어 "어디에 있는가"만 답한다 — KiCad가 실제로 찾는 경로와 같은 경로를 보기 위해서다.

  locate --symbol <[lib:]name> --footprint <[lib:]name> [--project DIR] [--json]
      위치를 찾고 심볼 핀 번호와 풋프린트 패드 번호를 대조한다 (어긋나면 경고만, exit 0)
  verify <metadata.json> [--project DIR] [--json]
      metadata.json 의 kicad 칸에 적힌 위치가 지금도 유효한지 다시 확인한다
  --selftest
      임시 라이브러리로 자체 검사

표준 라이브러리만 쓴다.
"""
import json
import os
import re
import sys
import tempfile

LIB_RE = re.compile(r'\(lib\s+\(name\s+"([^"]+)"\)\s*\(type\s+"([^"]+)"\)\s*\(uri\s+"([^"]+)"\)')
VAR_RE = re.compile(r"\$\{([^}]+)\}")


def kicad_config_dir():
    """가장 높은 버전의 KiCad 사용자 설정 디렉토리. 없으면 None."""
    if sys.platform == "win32":
        base = os.path.join(os.environ.get("APPDATA", ""), "kicad")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Preferences/kicad")
    else:
        base = os.path.expanduser("~/.config/kicad")
    if not os.path.isdir(base):
        return None
    vers = [v for v in os.listdir(base) if re.fullmatch(r"\d+(\.\d+)*", v)]
    if not vers:
        return None
    vers.sort(key=lambda v: [int(x) for x in v.split(".")])
    return os.path.join(base, vers[-1])


def kicad_share_dir():
    for d in ("/usr/share/kicad", "/usr/local/share/kicad",
              "/Applications/KiCad/KiCad.app/Contents/SharedSupport"):
        if os.path.isdir(d):
            return d
    return None


def build_env(cfg, project):
    """${VAR} 치환표: KiCad 기본 경로 변수 < kicad_common.json 사용자 변수 < 프로세스 환경."""
    env = {}
    share = kicad_share_dir()
    if cfg and share:
        major = os.path.basename(cfg).split(".")[0]
        for key, sub in (("SYMBOL", "symbols"), ("FOOTPRINT", "footprints"),
                         ("3DMODEL", "3dmodels"), ("TEMPLATE", "template")):
            env["KICAD%s_%s_DIR" % (major, key)] = os.path.join(share, sub)
    if cfg:
        try:
            with open(os.path.join(cfg, "kicad_common.json"), encoding="utf-8") as f:
                env.update((json.load(f).get("environment") or {}).get("vars") or {})
        except (OSError, ValueError):
            pass
    env.update(os.environ)
    if project:
        env["KIPRJMOD"] = os.path.abspath(project)
    return env


def expand(path, env):
    return os.path.expanduser(VAR_RE.sub(lambda m: env.get(m.group(1), m.group(0)), path))


def read_table(path, env, seen=None):
    """lib 표를 읽어 [(nickname, uri)]. type "Table"(KiCad 10 중첩 표)은 따라 들어간다."""
    seen = seen if seen is not None else set()
    path = os.path.abspath(path)
    if path in seen or not os.path.isfile(path):
        return []
    seen.add(path)
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    libs = []
    for name, typ, uri in LIB_RE.findall(text):
        uri = expand(uri, env)
        if typ.lower() == "table":
            libs += read_table(uri, env, seen)
        else:
            libs.append((name, uri))
    return libs


def lib_tables(kind, project, env, cfg):
    """프로젝트 표가 전역 표보다 먼저 (KiCad와 같은 우선순위)."""
    libs = []
    if project:
        libs += read_table(os.path.join(project, kind), env)
    if cfg:
        libs += read_table(os.path.join(cfg, kind), env)
    return libs


def split_ref(ref):
    return ref.split(":", 1) if ":" in ref else (None, ref)


def symbol_block(text, name):
    """`(symbol "name"` 최상위 블록 문자열. 없으면 None."""
    m = re.search(r'\(symbol\s+"%s"' % re.escape(name), text)
    if not m:
        return None
    depth, i = 0, m.start()
    while i < len(text):
        c = text[i]
        if c == '"':  # 문자열 안의 괄호는 세지 않는다 (\" 이스케이프 건너뜀)
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[m.start():i + 1]
        i += 1
    return None


PIN_RE = re.compile(r'\(pin\s[\s\S]*?\(name\s+"([^"]*)"[\s\S]*?\(number\s+"([^"]*)"')


def symbol_pins(text, name, hops=0):
    block = symbol_block(text, name)
    if block is None:
        return None
    ext = re.search(r'\(extends\s+"([^"]+)"', block)
    if ext and hops < 5:  # 파생 심볼은 핀을 부모에서 가져온다
        return symbol_pins(text, ext.group(1), hops + 1)
    return sorted({(num, pname) for pname, num in PIN_RE.findall(block)}, key=lambda p: natkey(p[0]))


def natkey(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def find_symbol(ref, libs):
    lib, name = split_ref(ref)
    for nick, uri in libs:
        if lib and nick != lib:
            continue
        if not os.path.isfile(uri):
            continue
        with open(uri, encoding="utf-8", errors="replace") as f:
            text = f.read()
        if '(symbol "%s"' % name not in text:
            continue
        pins = symbol_pins(text, name)
        if pins is not None:
            fp = re.search(r'\(property\s+"Footprint"\s+"([^"]*)"', symbol_block(text, name))
            return {"ref": "%s:%s" % (nick, name), "file": uri, "found": True, "pins": pins,
                    "footprint_field": fp.group(1) if fp else ""}
    return {"ref": ref, "file": None, "found": False, "pins": [], "footprint_field": ""}


def find_footprint(ref, libs, env):
    lib, name = split_ref(ref)
    for nick, uri in libs:
        if lib and nick != lib:
            continue
        path = os.path.join(uri, name + ".kicad_mod")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        pads = sorted({p for p in re.findall(r'\(pad\s+"([^"]*)"', text) if p}, key=natkey)
        models = [{"raw": m, "file": expand(m, env), "exists": os.path.isfile(expand(m, env))}
                  for m in re.findall(r'\(model\s+"([^"]+)"', text)]
        return {"ref": "%s:%s" % (nick, name), "file": path, "found": True, "pads": pads, "models": models}
    return {"ref": ref, "file": None, "found": False, "pads": [], "models": []}


def compare(sym, fp):
    """심볼 핀 번호 vs 풋프린트 패드 번호. 경고 문자열 목록 (판정은 경고만, 차단하지 않는다)."""
    if not (sym["found"] and fp["found"]):
        return []
    pins = {n for n, _ in sym["pins"]}
    pads = set(fp["pads"])
    warns = []
    if pins - pads:
        warns.append("심볼에만 있는 핀 번호: " + ", ".join(sorted(pins - pads, key=natkey)))
    if pads - pins:
        warns.append("풋프린트에만 있는 패드 번호: " + ", ".join(sorted(pads - pins, key=natkey)))
    return warns


def locate(symbol, footprint, project=None, model=None):
    cfg = kicad_config_dir()
    env = build_env(cfg, project)
    res = {"kicad_config": cfg, "warnings": []}
    res["symbol"] = find_symbol(symbol, lib_tables("sym-lib-table", project, env, cfg)) if symbol else None
    if not footprint and res["symbol"]:  # 풋프린트를 안 주면 심볼의 Footprint 속성을 따른다
        footprint = res["symbol"]["footprint_field"] or None
    res["footprint"] = find_footprint(footprint, lib_tables("fp-lib-table", project, env, cfg), env) if footprint else None
    if model:  # metadata 에 적힌 모델 경로를 따로 확인 (풋프린트가 다른 모델을 가리킬 수 있다)
        res["model"] = {"raw": model, "file": expand(model, env), "exists": os.path.isfile(expand(model, env))}
    elif res["footprint"] and res["footprint"]["models"]:
        res["model"] = res["footprint"]["models"][0]
    else:
        res["model"] = None
    if res["symbol"] and res["footprint"]:
        res["warnings"] = compare(res["symbol"], res["footprint"])
    if cfg is None:
        res["warnings"].append("KiCad 사용자 설정 디렉토리를 못 찾았다 — 라이브러리 표 없이 판정 불가")
    return res


def status_line(res, missing="위치 끊김"):
    # locate(찾기)에서 못 찾으면 "없음", verify(기록된 위치 재확인)에서 못 찾으면 "위치 끊김"
    def st(item, label):
        if item is None:
            return label + " 없음"
        ok = item.get("found", item.get("exists"))
        return "%s %s" % (label, ("있음 " + (item.get("ref") or item.get("raw"))) if ok else missing)
    return " | ".join([st(res["symbol"], "심볼"), st(res["footprint"], "풋프린트"), st(res["model"], "3D")])


def verify(meta_path, project=None):
    with open(meta_path, encoding="utf-8") as f:
        kc = json.load(f).get("kicad") or {}
    return locate(kc.get("symbol"), kc.get("footprint"), project, kc.get("model"))


def selftest():
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "my.pretty"))
    with open(os.path.join(tmp, "my.kicad_sym"), "w") as f:
        f.write('(kicad_symbol_lib (symbol "BASE" (symbol "BASE_1_1"'
                ' (pin power_in line (at 0 0 0) (length 2) (name "VIN" (effects)) (number "1" (effects)))'
                ' (pin output line (at 0 0 0) (length 2) (name "OUT" (effects)) (number "2" (effects)))'
                ' (pin passive line (at 0 0 0) (length 2) (name "EN (x)" (effects)) (number "3" (effects))))'
                ' (property "Footprint" "my:PKG"))'
                ' (symbol "CHILD" (extends "BASE")))')
    with open(os.path.join(tmp, "my.pretty", "PKG.kicad_mod"), "w") as f:
        f.write('(footprint "PKG" (pad "1" smd) (pad "2" smd) (pad "4" smd) (pad "" np_thru_hole)'
                ' (model "${KIPRJMOD}/m.step"))')
    open(os.path.join(tmp, "m.step"), "w").close()
    with open(os.path.join(tmp, "sym-lib-table"), "w") as f:
        f.write('(sym_lib_table (lib (name "my") (type "KiCad") (uri "${KIPRJMOD}/my.kicad_sym") (options "") (descr "")))')
    with open(os.path.join(tmp, "fp-lib-table"), "w") as f:
        f.write('(fp_lib_table (lib (name "my") (type "KiCad") (uri "${KIPRJMOD}/my.pretty") (options "") (descr "")))')
    r = locate("CHILD", "my:PKG", project=tmp)
    assert r["symbol"]["found"] and r["symbol"]["ref"] == "my:CHILD", r["symbol"]
    assert [n for n, _ in r["symbol"]["pins"]] == ["1", "2", "3"], r["symbol"]["pins"]
    assert ("3", "EN (x)") in r["symbol"]["pins"]
    assert r["footprint"]["pads"] == ["1", "2", "4"], r["footprint"]["pads"]
    assert r["model"]["exists"]
    assert any("3" in w for w in r["warnings"]) and any("4" in w for w in r["warnings"]), r["warnings"]
    assert locate("my:BASE", None, project=tmp)["footprint"]["ref"] == "my:PKG"  # Footprint 속성 따라가기
    r = locate("my:NOPE", "my:NOPE", project=tmp, model="${KIPRJMOD}/gone.step")
    assert not r["symbol"]["found"] and not r["footprint"]["found"] and not r["model"]["exists"]
    assert status_line(r).count("위치 끊김") == 3, status_line(r)
    assert status_line(r, "없음").count("없음") == 3
    print("selftest OK")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]

    def opt(name):
        if name in args:
            i = args.index(name)
            return args[i + 1] if i + 1 < len(args) else None
        return None

    if args and args[0] == "locate":
        res = locate(opt("--symbol"), opt("--footprint"), opt("--project"), opt("--model"))
    elif len(args) >= 2 and args[0] == "verify":
        res = verify(args[1], opt("--project"))
    else:
        print(__doc__)
        return 2
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0
    print(status_line(res, "없음" if args[0] == "locate" else "위치 끊김"))
    for key in ("symbol", "footprint", "model"):
        item = res.get(key)
        if item and item.get("file"):
            print("  %-9s %s" % (key, item["file"]))
    if res["symbol"] and res["symbol"]["found"]:
        print("  pins      " + ", ".join("%s=%s" % p for p in res["symbol"]["pins"]))
    for w in res["warnings"]:
        print("  경고: " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
