# KiCad 회로도 파싱 가이드

> KiCad 9.x의 `.kicad_sch` 파일은 S-expression(Lisp 유사) 형식이다.
> 이 문서는 회로도에서 부품, 핀, 네트, 값을 추출하는 방법을 설명한다.

## 목차

1. [파일 구조 개요](#파일-구조-개요)
2. [kicad-cli를 이용한 넷리스트 추출](#kicad-cli-넷리스트-추출)
3. [.kicad_sch 직접 파싱](#직접-파싱)
4. [계층 구조 처리](#계층-구조-처리)
5. [풋프린트 라이브러리 테이블(fp-lib-table) 파싱](#fp-lib-table-파싱)
6. [`.kicad_sym` 심볼 핀 직접 파싱](#kicad_sym-심볼-핀-직접-파싱)
7. [구조 린트 오탐 필터](#구조-린트-오탐-필터)
8. [파싱 스크립트 모음](#파싱-스크립트)

---

## 파일 구조 개요

### S-expression 최상위 구조

```lisp
(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "...")
  (paper "A3")
  (title_block ...)
  (lib_symbols ...)      ;; 라이브러리 심볼 정의 (핀 번호, 타입 포함)
  (symbol ...)           ;; 배치된 부품 인스턴스
  (wire ...)             ;; 전선
  (label ...)            ;; 로컬 네트 레이블
  (global_label ...)     ;; 글로벌 네트 레이블
  (hierarchical_label...);; 계층 레이블
  (no_connect ...)       ;; NC 마커
  (junction ...)         ;; 교차점
  (sheet ...)            ;; 서브시트 참조
  (sheet_instances ...)
)
```

### 핵심 노드 설명

| 노드 | 용도 | 주요 필드 |
|------|------|----------|
| `lib_symbols` | 사용된 심볼의 핀 정의 | `(pin <type> <shape> (at ...) (name "...") (number "..."))` |
| `symbol` | 배치된 부품 | `(lib_id "...")`, `(property "Reference" "U1")`, `(property "Value" "...")` |
| `wire` | 전선 (두 점을 연결) | `(pts (xy x1 y1) (xy x2 y2))` |
| `label` | 로컬 네트 이름 | `"NET_NAME"`, `(at x y angle)` |
| `global_label` | 글로벌 네트 | 시트 간 공유되는 네트 |
| `sheet` | 서브시트 | `(property "Sheetfile" "xxx.kicad_sch")` |

---

## kicad-cli 넷리스트 추출

kicad-cli가 설치되어 있으면 넷리스트 XML을 추출하는 것이 가장 정확하다.

```bash
# 넷리스트 XML 추출 (계층 구조 자동 해석)
kicad-cli sch export netlist \
  --output /tmp/netlist.xml \
  --format kicadxml \
  "프로젝트.kicad_sch"

# BOM CSV 추출
kicad-cli sch export bom \
  --output /tmp/bom.csv \
  "프로젝트.kicad_sch"

# Python BOM 추출 (kicad-cli 내장 스크립트)
kicad-cli sch export python-bom \
  --output /tmp/bom.xml \
  "프로젝트.kicad_sch"
```

### 넷리스트 XML 구조

```xml
<export version="E">
  <components>
    <comp ref="U1">
      <value>XC7A200T</value>
      <footprint>Package_BGA:BGA-484_...</footprint>
      <datasheet>https://...</datasheet>
      <fields>
        <field name="Manufacturer">AMD/Xilinx</field>
      </fields>
    </comp>
  </components>
  <nets>
    <net code="1" name="+3V3">
      <node ref="U1" pin="A1" pinfunction="VCCO_0" pintype="passive"/>
      <node ref="C1" pin="1" pintype="passive"/>
    </net>
  </nets>
</export>
```

### 넷리스트 파싱 (Python)

```python
import xml.etree.ElementTree as ET

tree = ET.parse('/tmp/netlist.xml')
root = tree.getroot()

# 부품 목록
for comp in root.findall('.//comp'):
    ref = comp.get('ref')
    value = comp.findtext('value', '')
    footprint = comp.findtext('footprint', '')
    datasheet = comp.findtext('datasheet', '')
    print(f"{ref}: {value} ({footprint})")

# 네트-핀 매핑
for net in root.findall('.//net'):
    net_name = net.get('name')
    nodes = [(n.get('ref'), n.get('pin'), n.get('pinfunction', ''))
             for n in net.findall('node')]
    if len(nodes) > 1:  # 연결된 네트만
        print(f"Net '{net_name}': {nodes}")
```

---

## 직접 파싱

kicad-cli가 없을 때 `.kicad_sch`를 직접 파싱하는 방법.

### 방법 1: 정규식 기반 추출 (간단, 정확도 제한)

```bash
# 부품 레퍼런스와 값 추출
grep -oP '\(property "Reference" "\K[^"]+' *.kicad_sch | sort -u
grep -oP '\(property "Value" "\K[^"]+' *.kicad_sch | sort -u

# 풋프린트 추출
grep -oP '\(property "Footprint" "\K[^"]+' *.kicad_sch | sort -u

# 데이터시트 URL 추출
grep -oP '\(property "Datasheet" "\K[^"]+' *.kicad_sch | sort -u

# lib_id로 사용된 심볼 목록
grep -oP '\(lib_id "\K[^"]+' *.kicad_sch | sort -u

# 글로벌 레이블 (네트 이름) 추출
grep -oP '\(global_label "\K[^"]+' *.kicad_sch | sort -u

# 로컬 레이블
grep -oP '\(label "\K[^"]+' *.kicad_sch | sort -u
```

### 방법 2: Python S-expression 파서 (정확)

```python
import re
from pathlib import Path

def parse_sexpr(text):
    """간이 S-expression 파서. 중첩 리스트 반환."""
    tokens = re.findall(r'\(|\)|"[^"]*"|[^\s()]+', text)
    def parse():
        result = []
        while tokens:
            token = tokens.pop(0)
            if token == '(':
                result.append(parse())
            elif token == ')':
                return result
            else:
                result.append(token.strip('"') if token.startswith('"') else token)
        return result
    return parse()

def extract_components(sch_path):
    """kicad_sch에서 부품 정보 추출"""
    text = Path(sch_path).read_text(encoding='utf-8')
    components = []

    # symbol 블록 추출 (lib_id가 있는 것만 = 배치된 부품)
    # 간이 방식: 정규식으로 symbol 블록 단위 추출
    pattern = r'\(symbol\s*\(lib_id\s+"([^"]+)"\)(.+?)\n\s*\)'
    for match in re.finditer(pattern, text, re.DOTALL):
        lib_id = match.group(1)
        body = match.group(2)

        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', body)
        val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', body)
        fp_m = re.search(r'\(property\s+"Footprint"\s+"([^"]+)"', body)
        ds_m = re.search(r'\(property\s+"Datasheet"\s+"([^"]+)"', body)

        components.append({
            'lib_id': lib_id,
            'reference': ref_m.group(1) if ref_m else '',
            'value': val_m.group(1) if val_m else '',
            'footprint': fp_m.group(1) if fp_m else '',
            'datasheet': ds_m.group(1) if ds_m else '',
        })

    return components
```

---

## 계층 구조 처리

KiCad의 계층 회로도는 루트 `.kicad_sch`에서 `(sheet ...)` 노드로 서브시트를 참조한다.

### 서브시트 탐색

```bash
# 루트 스키매틱에서 서브시트 파일명 추출
grep -oP '\(property "Sheetfile" "\K[^"]+' root.kicad_sch
```

출력 예:
```
power.kicad_sch
m2_connector.kicad_sch
ffc_breakout.kicad_sch
fpga.kicad_sch
phy.kicad_sch
flash.kicad_sch
```

### 전체 계층 순회 (Python)

```python
from pathlib import Path
import re

def find_all_sheets(root_sch, base_dir=None):
    """계층적으로 모든 서브시트를 탐색"""
    if base_dir is None:
        base_dir = Path(root_sch).parent
    
    sheets = [Path(root_sch)]
    text = Path(root_sch).read_text(encoding='utf-8')
    
    for match in re.finditer(r'\(property "Sheetfile" "([^"]+)"', text):
        sub_path = base_dir / match.group(1)
        if sub_path.exists():
            sheets.extend(find_all_sheets(str(sub_path), base_dir))
    
    return sheets
```

### 시트 간 연결

- **글로벌 레이블** (`global_label`): 모든 시트에서 같은 이름이면 같은 네트
- **계층 핀** (`hierarchical_label` + `sheet` 내부 `pin`): 시트 간 명시적 연결
- **전원 심볼** (`power:+3V3`, `power:GND`): 암묵적 글로벌 네트

---

## fp-lib-table 파싱

풋프린트 해석 검사(SKILL.md 단계 4)에 쓰는 파싱이다. 회로도의 `Footprint` 속성은 `Lib:Name` 문자열일 뿐이고,
그 `Lib`(nickname)이 실제 라이브러리로 풀리는지는 `fp-lib-table`을 읽어야만 알 수 있다.
비유하면 회로도의 Footprint 필드는 "책 제목"이고, fp-lib-table은 "그 책이 어느 서가에 있는지 적힌 목록"이다.
목록에 없는 제목은 Update PCB 시점에 그대로 실패한다.

### 테이블 위치와 우선순위

| 범위 | 경로 | 비고 |
|------|------|------|
| 전역 | `~/.config/kicad/<버전>/fp-lib-table` (예: `~/.config/kicad/10.0/fp-lib-table`) | 모든 프로젝트가 로드 |
| 프로젝트 | `<프로젝트 디렉토리>/fp-lib-table` | 같은 nickname이면 프로젝트 항목이 이긴다 |

**KiCad 10의 간접 테이블에 주의한다.** KiCad 10의 전역 `fp-lib-table`은 대개 아래 한 줄뿐이다.

```lisp
(lib (name "KiCad") (type "Table") (uri "${KICAD10_TEMPLATE_DIR}/fp-lib-table") (options "") (descr "KiCad Default Libraries"))
```

`(type "Table")` 행은 라이브러리가 아니라 **다른 테이블을 가리키는 간접 참조**다.
이 환경(KiCad 10.0.6) 실측으로 이 한 줄이 `/usr/share/kicad/template/fp-lib-table`의 **155개 라이브러리**를 대신한다.
따라서 전역 테이블을 `grep`으로 훑어 "라이브러리가 하나뿐"이라고 판정하면 안 된다 — 사람 눈으로는 보이지 않는다.
간접 행을 따라 들어가 펼친 뒤에 nickname 실존을 판정한다.
MCP `list_library_table`은 이 펼치기와 URI 해석·실존 보고를 서버가 대신 해 준다(SKILL.md 단계 4 참조).

### URI 변수 치환

URI에는 다음 형태의 변수가 들어간다. 치환 우선순위는 `${KIPRJMOD}`(프로젝트 디렉토리) →
`~/.config/kicad/<버전>/kicad_common.json`의 `environment.vars` → 프로세스 환경변수 → KiCad 내장 기본값이다.

| 변수 | 기본값(리눅스 배포판 설치 기준) |
|------|-------------------------------|
| `${KIPRJMOD}` | `.kicad_pro`가 있는 디렉토리 |
| `${KICAD10_FOOTPRINT_DIR}` | `/usr/share/kicad/footprints` |
| `${KICAD10_SYMBOL_DIR}` | `/usr/share/kicad/symbols` |
| `${KICAD10_TEMPLATE_DIR}` | `/usr/share/kicad/template` |

### 파싱 + 해석 스크립트

```python
import os, re, glob, json

# KiCad 10 기본 경로 (배포판에 따라 다르면 실제 경로로 교체)
DEFAULTS = {
    'KICAD10_FOOTPRINT_DIR': '/usr/share/kicad/footprints',
    'KICAD10_SYMBOL_DIR':    '/usr/share/kicad/symbols',
    'KICAD10_TEMPLATE_DIR':  '/usr/share/kicad/template',
    'KICAD10_3DMODEL_DIR':   '/usr/share/kicad/3dmodels',
}

def _user_vars():
    """내장 기본값 + kicad_common.json의 environment.vars + 프로세스 환경변수"""
    v = dict(DEFAULTS)
    for cfg in sorted(glob.glob(os.path.expanduser('~/.config/kicad/*/kicad_common.json'))):
        try:
            v.update(json.load(open(cfg)).get('environment', {}).get('vars', {}))
        except Exception:
            pass
    v.update({k: val for k, val in os.environ.items() if k.startswith('KICAD')})
    return v

def _expand(uri, prj_dir, vars_):
    def sub(m):
        name = m.group(1)
        return prj_dir if name == 'KIPRJMOD' else vars_.get(name, m.group(0))
    return re.sub(r'\$\{([A-Za-z0-9_]+)\}', sub, uri)

def parse_fp_lib_table(path, prj_dir, vars_=None, _seen=None):
    """fp-lib-table을 읽어 {nickname: {'uri', 'type', 'exists'}} 반환.
    (type "Table") 행은 가리키는 테이블을 재귀로 펼친다(순환 방지 포함)."""
    vars_ = vars_ or _user_vars()
    _seen = _seen if _seen is not None else set()
    real = os.path.realpath(path)
    if real in _seen or not os.path.exists(real):
        return {}
    _seen.add(real)

    libs = {}
    text = open(real, encoding='utf-8', errors='replace').read()
    for m in re.finditer(
            r'\(lib\s+\(name\s+"?([^")\s]+)"?\)\s*\(type\s+"?([^")\s]+)"?\)\s*\(uri\s+"([^"]*)"\)', text):
        nick, typ, uri = m.group(1), m.group(2), m.group(3)
        resolved = _expand(uri, prj_dir, vars_)
        if typ.lower() == 'table':      # 간접 행 — 한 줄이 수백 개를 대신한다
            libs.update(parse_fp_lib_table(resolved, prj_dir, vars_, _seen))
        else:
            libs[nick] = {'uri': resolved, 'type': typ, 'exists': os.path.exists(resolved)}
    return libs

def resolve_footprints(fp_fields, prj_dir, kicad_ver='10.0'):
    """fp_fields: [(reference, 'Lib:Name'), ...] → [(ref, field, 판정, 사유), ...]"""
    libs = parse_fp_lib_table(
        os.path.expanduser(f'~/.config/kicad/{kicad_ver}/fp-lib-table'), prj_dir)   # 전역
    libs.update(parse_fp_lib_table(os.path.join(prj_dir, 'fp-lib-table'), prj_dir))  # 프로젝트가 우선

    out = []
    for ref, field in fp_fields:
        if not field.strip():
            out.append((ref, field, 'ERROR', 'Footprint 필드가 비어 있다')); continue
        if ':' not in field:
            out.append((ref, field, 'ERROR', 'Lib:Name 형식이 아니다')); continue
        nick, name = field.split(':', 1)
        lib = libs.get(nick)
        if lib is None:
            out.append((ref, field, 'ERROR', f'nickname "{nick}" 이 fp-lib-table 에 없다'))
        elif not lib['exists']:
            out.append((ref, field, 'ERROR', f'라이브러리 경로 없음: {lib["uri"]}'))
        elif not os.path.exists(os.path.join(lib['uri'], name + '.kicad_mod')):
            out.append((ref, field, 'ERROR', f'{name}.kicad_mod 이 {lib["uri"]} 에 없다'))
        else:
            out.append((ref, field, 'OK', ''))
    return out
```

### 넷리스트 XML에서 Footprint 필드 수집

`resolve_footprints`의 입력은 넷리스트 XML의 `<footprint>` 요소에서 모은다.

```python
import xml.etree.ElementTree as ET

def collect_footprint_fields(netlist_xml):
    """[(reference, 'Lib:Name'), ...] — 값이 없으면 빈 문자열로 남겨 ERROR 판정 대상에 넣는다"""
    tree = ET.parse(netlist_xml)
    return [(c.get('ref', ''), (c.findtext('footprint') or '').strip())
            for c in tree.findall('.//comp')]
```

넷리스트를 못 뽑는 환경(kicad-cli 부재)에서는 `.kicad_sch`를 직접 훑어 같은 목록을 만든다.

```bash
grep -ho '(property "Footprint" "[^"]*"' *.kicad_sch | sed 's/.*"Footprint" "//; s/"$//' | sort -u
```

이 방법은 부품 레퍼런스와 짝지어지지 않으므로 "어느 nickname이 안 풀리는가"까지만 판정하고,
"어느 부품인가"는 해당 nickname으로 다시 `grep`해서 찾는다.

---

## 파싱 스크립트

### 전체 BOM 추출 (모든 시트)

```python
import re
from pathlib import Path
from collections import defaultdict

def extract_full_bom(project_dir):
    """프로젝트 디렉토리의 모든 .kicad_sch에서 BOM 추출"""
    bom = []
    sch_files = list(Path(project_dir).glob('*.kicad_sch'))
    
    for sch in sch_files:
        text = sch.read_text(encoding='utf-8')
        
        # (symbol (lib_id "...") ... 블록 추출
        # lib_id가 "power:"로 시작하면 전원 심볼이므로 제외
        for block in re.finditer(
            r'\(symbol\s*\(lib_id\s+"([^"]+)"\)(.*?)\n\s*\)\s*$',
            text, re.DOTALL | re.MULTILINE
        ):
            lib_id = block.group(1)
            if lib_id.startswith('power:'):
                continue
            
            body = block.group(2)
            ref = _extract_prop(body, 'Reference')
            if ref and ref.startswith('#'):  # #PWR, #FLG 등 가상 부품 제외
                continue
            
            dnp_m = re.search(r'\(dnp\s+(yes|no)\)', body)
            is_dnp = dnp_m and dnp_m.group(1) == 'yes'
            
            bom.append({
                'reference': ref or '',
                'value': _extract_prop(body, 'Value') or '',
                'footprint': _extract_prop(body, 'Footprint') or '',
                'datasheet': _extract_prop(body, 'Datasheet') or '',
                'lib_id': lib_id,
                'sheet': sch.name,
                'dnp': is_dnp,
            })
    
    return sorted(bom, key=lambda x: _natural_sort_key(x['reference']))

def _extract_prop(text, name):
    m = re.search(rf'\(property\s+"{name}"\s+"([^"]*)"', text)
    return m.group(1) if m else None

def _natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower()
            for c in re.split(r'(\d+)', s)]
```

### 네트 연결 맵 추출

```python
def extract_net_connections(netlist_xml):
    """넷리스트 XML에서 네트별 연결된 부품-핀 맵 추출"""
    import xml.etree.ElementTree as ET
    tree = ET.parse(netlist_xml)
    
    net_map = {}
    for net in tree.findall('.//net'):
        name = net.get('name', '')
        nodes = []
        for node in net.findall('node'):
            nodes.append({
                'ref': node.get('ref'),
                'pin': node.get('pin'),
                'pinfunction': node.get('pinfunction', ''),
                'pintype': node.get('pintype', ''),
            })
        net_map[name] = nodes
    
    return net_map
```

---

## `.kicad_sym` 심볼 핀 직접 파싱

MCP `list_symbol_pins` / `batch_list_symbol_pins`가 `Symbol '...' not found`를 내는 경우의 폴백이다.
**등록이 잘못된 게 아니다** — 라이브러리 파일이 심볼을 `(symbol "LIB:NAME" …)`로 저장하면
MCP가 라이브러리 `LIB` 안에서 `NAME`을 찾다가 실패한다. KiCad 정본은 `(symbol "NAME" …)`이지만,
벤더 배포·SnapEDA 다운로드 심볼은 라이브러리 이름을 심볼 이름에 붙여 저장하는 경우가 흔하다.
`kicad-cli sym export`는 SVG만 내므로 핀 데이터를 주지 못한다 — 파일을 직접 읽는 것이 유일한 폴백이다.

### 파싱이 다뤄야 하는 세 가지

| 사항 | 내용 |
|---|---|
| 심볼 키 두 형식 | `NAME` 과 `LIB:NAME` 을 **둘 다** 시도한다 (콜론 뒤만 비교하면 양쪽을 한 번에 처리한다) |
| 하위 유닛 이름 | 실제 핀은 `<이름>_<유닛>_<표현>` 하위 심볼 안에 있다. `_1_1`은 기본 표현, `_1_2`는 De Morgan 대체 표현 — **대체 표현을 세면 핀 수가 2배가 된다** |
| 상속 | KiCad 정본 심볼은 `(extends "부모심볼")`로 핀을 물려받는다. 상속을 따라가지 않으면 핀 0개가 나온다 |

들여쓰기에 의존하면 안 된다 — 같은 파일 안에서도 최상위 심볼이 탭 1개, 하위 심볼이 탭 3개인 사례가 있다.
아래 스크립트는 이름 규칙(`_숫자_숫자` 접미어)으로 최상위/하위를 가른다.

### 스크립트

```python
#!/usr/bin/env python3
"""sym-lib-table 을 풀어 .kicad_sym 에서 심볼 핀을 직접 뽑는다 (MCP list_symbol_pins 폴백)."""
import sys, os, re, glob

KICAD_SYM_DIRS = ['/usr/share/kicad/symbols']

def resolve(nickname, project_dir):
    tables = [os.path.join(project_dir, 'sym-lib-table')]
    tables += sorted(glob.glob(os.path.expanduser('~/.config/kicad/*/sym-lib-table')), reverse=True)
    for tbl in tables:
        if not os.path.exists(tbl):
            continue
        text = open(tbl, encoding='utf-8').read()
        for m in re.finditer(r'\(lib\s+\(name\s+"?([^")\s]+)"?\).*?\(uri\s+"([^"]+)"\)', text, re.S):
            if m.group(1) != nickname:
                continue
            uri = os.path.expandvars(m.group(2).replace('${KIPRJMOD}', project_dir))
            uri = re.sub(r'\$\{KICAD\d+_SYMBOL_DIR\}', KICAD_SYM_DIRS[0], uri)
            if os.path.exists(uri):
                return uri
    for d in KICAD_SYM_DIRS:                       # KiCad 10 (type "Table") 간접 행 폴백
        p = os.path.join(d, nickname + '.kicad_sym')
        if os.path.exists(p):
            return p
    return None

def pins(lib_path, lib_id, _depth=0):
    """[(unit, number, name, type, x, y)]. 심볼 키가 'NAME' 이든 'LIB:NAME' 이든 찾는다."""
    src = open(lib_path, encoding='utf-8').read()
    base = lib_id.split(':')[-1]
    top = [m for m in re.finditer(r'\(symbol "([^"]+)"', src)
           if not re.search(r'_\d+_\d+$', m.group(1))]      # 하위 유닛(_유닛_표현) 제외
    start = end = None
    for i, m in enumerate(top):
        if m.group(1).split(':')[-1] == base:
            start = m.end()
            end = top[i + 1].start() if i + 1 < len(top) else len(src)
            break
    if start is None:
        return None
    body = src[start:end]
    ext = re.search(r'\(extends "([^"]+)"\)', body)      # KiCad 정본 심볼의 상속
    if ext and _depth < 4:
        return pins(lib_path, ext.group(1), _depth + 1)
    out = []
    for sm in re.finditer(r'\(symbol "[^"]*_(\d+)_(\d+)"', body):
        unit, style = int(sm.group(1)), int(sm.group(2))
        if style > 1:                              # De Morgan 대체 표현은 건너뛴다
            continue
        nx = re.search(r'\(symbol "[^"]*_\d+_\d+"', body[sm.end():])
        blk = body[sm.end(): sm.end() + (nx.start() if nx else len(body))]
        for pm in re.finditer(r'\(pin (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+)', blk):
            tail = blk[pm.end(): pm.end() + 800]
            nm = re.search(r'\(name "([^"]*)"', tail)
            nu = re.search(r'\(number "([^"]*)"', tail)
            out.append((unit, nu.group(1) if nu else '', nm.group(1) if nm else '',
                        pm.group(1), float(pm.group(3)), float(pm.group(4))))
    return out

if __name__ == '__main__':
    project_dir = sys.argv[1]
    for lib_id in sys.argv[2:]:
        nick = lib_id.split(':', 1)[0]
        path = resolve(nick, project_dir)
        if not path:
            print(f'{lib_id}: sym-lib-table 미해석'); continue
        p = pins(path, lib_id)
        if p is None:
            print(f'{lib_id}: 심볼 없음 ({path})'); continue
        empty = sum(1 for x in p if not x[1].strip())
        units = len({x[0] for x in p})
        print(f'{lib_id}: {len(p)}핀 / {units}유닛 (빈 핀번호 {empty}) <- {os.path.basename(path)}')
```

### 사용

```bash
# 인자: 프로젝트 디렉토리, 그다음 lib_id 들 ("Lib:Name")
python3 sym_pins.py "$PROJECT_DIR" "SMD_HOLE:SMDPAD" "ET1200_QFN-48:ET1200" "MCU_ST_STM32F4:STM32F407IGHx"
# SMD_HOLE:SMDPAD: 1핀 / 1유닛 (빈 핀번호 1) <- SMD_HOLE.kicad_sym
# ET1200_QFN-48:ET1200: 49핀 / 1유닛 (빈 핀번호 0) <- ET1200_QFN-48.kicad_sym
# MCU_ST_STM32F4:STM32F407IGHx: 201핀 / 1유닛 (빈 핀번호 0) <- MCU_ST_STM32F4.kicad_sym
```

`resolve()`는 프로젝트 `sym-lib-table` → 사용자 `~/.config/kicad/*/sym-lib-table` 순으로 훑고,
그래도 못 찾으면 `/usr/share/kicad/symbols/<nickname>.kicad_sym`을 마지막으로 시도한다
(KiCad 10 전역 테이블의 `(type "Table")` 간접 행 대응). 배포판 경로가 다르면 `KICAD_SYM_DIRS`를 고친다.

**빈 핀 번호(`(number "")`)를 세어 두면 구조 린트 오탐 필터 F1에 그대로 쓴다** — 아래 절 참조.

---

## 구조 린트 오탐 필터

MCP `find_orphaned_wires` · `find_overlapping_elements` · `find_wires_crossing_symbols`의
오탐을 걷어내는 재판정 스크립트다. 세 도구의 오탐 원인은 전부 **심볼 기하 정보를 도구가
잘못 쓰는 것**이라, `.kicad_sch`의 `lib_symbols` 정의를 직접 읽어 다시 판정하면 걸러진다.

| 필터 | 무엇을 거르나 |
|---|---|
| F1 | 떠 있다고 지목된 끝점이 **핀 번호가 빈 심볼**(테스트포인트·SMD 패드)의 핀 좌표와 일치 → 정상 연결 |
| F2 | **양쪽 레퍼런스가 같은 쌍**(`U6 ↔ U6`) → 멀티유닛 심볼의 자기 자신 |
| F3 | 심볼 전체가 아니라 **배치된 그 유닛의** 바운딩 박스로 다시 교차 판정 |
| F4 | 와이어 **끝점이 그 심볼의 핀 좌표와 일치** → 정상 접속. 동일 `(와이어, 심볼)` 중복 제거 |

좌표 변환 주의: `.kicad_sch`의 심볼 인스턴스는 `(at x y 각도)` + 선택적 `(mirror x|y)`를 갖고,
라이브러리 좌표계는 **y축이 위로 증가**한다. 배치 좌표로 옮길 때 y 부호를 뒤집어야 한다
(아래 `xf()`의 `oy - y`).

### 스크립트

```python
#!/usr/bin/env python3
"""MCP 구조 린트 3종의 오탐을 걷어내는 재판정 스크립트 (KiCad 9/10 .kicad_sch)."""
import sys, math, re

def toks(s):
    out=[];i=0;n=len(s)
    while i<n:
        c=s[i]
        if c in '()': out.append(c);i+=1
        elif c=='"':
            j=i+1;buf=[]
            while j<n:
                if s[j]=='\\': buf.append(s[j+1]);j+=2;continue
                if s[j]=='"': break
                buf.append(s[j]);j+=1
            out.append(('S',''.join(buf)));i=j+1
        elif c.isspace(): i+=1
        else:
            j=i
            while j<n and not s[j].isspace() and s[j] not in '()"': j+=1
            out.append(('A',s[i:j]));i=j
    return out

def parse(t,i=0):
    node=[];i+=1
    while i<len(t):
        if t[i]=='(':
            sub,i=parse(t,i); node.append(sub)
        elif t[i]==')': return node,i+1
        else: node.append(t[i][1]);i+=1
    return node,i

def load(p): return parse(toks(open(p,encoding='utf-8').read()),0)[0]
def kids(n,name): return [c for c in n if isinstance(c,list) and c and c[0]==name]
def f(x): return float(x)

def unit_of(subname):
    m=re.match(r'^.*_(\d+)_(\d+)$', subname)
    return int(m.group(1)) if m else 0

def sym_geom(sym):
    """lib_symbol -> {unit: (bbox, [pin(x,y)])}, unit 0 은 공통(모든 유닛)."""
    g={}
    for sub in kids(sym,'symbol'):
        u=unit_of(sub[1]); xs=[];ys=[];pins=[]
        for r in kids(sub,'rectangle'):
            s=kids(r,'start')[0]; e=kids(r,'end')[0]
            xs+= [f(s[1]),f(e[1])]; ys+=[f(s[2]),f(e[2])]
        for pl in kids(sub,'polyline')+kids(sub,'bezier'):
            for pts in kids(pl,'pts'):
                for xy in kids(pts,'xy'): xs.append(f(xy[1])); ys.append(f(xy[2]))
        for c in kids(sub,'circle'):
            ct=kids(c,'center')[0]; r=f(kids(c,'radius')[0][1])
            xs+=[f(ct[1])-r,f(ct[1])+r]; ys+=[f(ct[2])-r,f(ct[2])+r]
        for a in kids(sub,'arc'):
            for k in ('start','mid','end'):
                p=kids(a,k)
                if p: xs.append(f(p[0][1])); ys.append(f(p[0][2]))
        for p in kids(sub,'pin'):
            at=kids(p,'at')[0]
            num=kids(p,'number')
            pins.append((f(at[1]),f(at[2]), num[0][1] if num else ''))
        bb=(min(xs),min(ys),max(xs),max(ys)) if xs else None
        e=g.setdefault(u,[None,[]])
        if bb:
            e[0]=bb if e[0] is None else (min(e[0][0],bb[0]),min(e[0][1],bb[1]),max(e[0][2],bb[2]),max(e[0][3],bb[3]))
        e[1]+=pins
    return g

def xf(px,py,ox,oy,ang,mirror):
    a=math.radians(ang)
    x=px*math.cos(a)-py*math.sin(a); y=px*math.sin(a)+py*math.cos(a)
    if mirror=='y': x=-x
    elif mirror=='x': y=-y
    return (ox+x, oy-y)

def place(bb,ox,oy,ang,mirror):
    pts=[xf(bb[0],bb[1],ox,oy,ang,mirror),xf(bb[2],bb[1],ox,oy,ang,mirror),
         xf(bb[0],bb[3],ox,oy,ang,mirror),xf(bb[2],bb[3],ox,oy,ang,mirror)]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return (min(xs),min(ys),max(xs),max(ys))

def instances(path):
    root=load(path)
    libs={}
    for ls in kids(root,'lib_symbols'):
        for s in kids(ls,'symbol'): libs[s[1]]=sym_geom(s)
    out=[]
    for sym in kids(root,'symbol'):
        lid=kids(sym,'lib_id')
        if not lid: continue
        key=lid[0][1]
        if key not in libs:
            cand=[k for k in libs if k.split(':')[-1]==key.split(':')[-1]]
            if not cand: continue
            key=cand[0]
        at=kids(sym,'at')[0]; ox,oy=f(at[1]),f(at[2]); ang=f(at[3]) if len(at)>3 else 0.0
        mir=kids(sym,'mirror'); mirror=mir[0][1] if mir else None
        un=kids(sym,'unit'); u=int(un[0][1]) if un else 1
        ref=None
        for pr in kids(sym,'property'):
            if pr[1]=='Reference': ref=pr[2]
        g=libs[key]
        parts=[g.get(u),g.get(0)]
        bb=None; pins=[]; pinnums=[]
        for p in parts:
            if not p: continue
            if p[0]:
                b=place(p[0],ox,oy,ang,mirror)
                bb=b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
            pins+= [xf(px,py,ox,oy,ang,mirror) for px,py,_ in p[1]]
            pinnums+= [num for _,_,num in p[1]]
        if bb is None: continue
        nunits=len([k for k in g if k>0])
        out.append(dict(ref=ref,unit=u,bb=bb,pins=pins,pinnums=pinnums,nunits=nunits))
    wires=[]
    for w in kids(root,'wire'):
        for pts in kids(w,'pts'):
            xy=kids(pts,'xy')
            if len(xy)==2: wires.append(((f(xy[0][1]),f(xy[0][2])),(f(xy[1][1]),f(xy[1][2]))))
    return out,wires

def bb_inter(a,b,tol=0.0):
    return not (a[2]<b[0]-tol or b[2]<a[0]-tol or a[3]<b[1]-tol or b[3]<a[1]-tol)

def seg_bb(p,q,bb):
    # 선분이 bbox 내부를 지나가는가 (양 끝점이 밖이고 교차)
    x1,y1=p; x2,y2=q
    if max(x1,x2)<bb[0] or min(x1,x2)>bb[2] or max(y1,y2)<bb[1] or min(y1,y2)>bb[3]: return False
    return True

def near(a,b,tol=0.01): return abs(a[0]-b[0])<tol and abs(a[1]-b[1])<tol

def f1_empty_pin_points(inst):
    """F1: 핀 번호가 빈 심볼(테스트포인트·SMD 패드)의 핀 좌표 집합."""
    pts=set()
    for s in inst:
        for (px,py),num in zip(s['pins'], s['pinnums']):
            if not (num or '').strip(): pts.add((round(px,3),round(py,3)))
    return pts

def f1_filter(inst, dangling):
    """find_orphaned_wires 가 준 끝점 목록을 F1 으로 거른다. (남은 것, 제외 수)"""
    pts=f1_empty_pin_points(inst)
    keep=[p for p in dangling if (round(p[0],3),round(p[1],3)) not in pts]
    return keep, len(dangling)-len(keep)

for path in sys.argv[1:]:
    inst,wires=instances(path)
    name=path.split('/')[-1]
    # --- overlap 재판정 ---
    ov=[]
    for i in range(len(inst)):
        for j in range(i+1,len(inst)):
            a,b=inst[i],inst[j]
            if a['ref']==b['ref']: continue           # F2: 같은 레퍼런스(멀티유닛 자기 자신)
            if bb_inter(a['bb'],b['bb']): ov.append((a['ref'],b['ref']))
    # --- crossing 재판정 ---
    cr=set()
    for p,q in wires:
        for s in inst:
            if not seg_bb(p,q,s['bb']): continue
            if any(near(p,pin) or near(q,pin) for pin in s['pins']): continue  # 핀 정상 접속
            cr.add((p,q,s['ref'],s['unit']))
    multi=sum(1 for s in inst if s['nunits']>1)
    empty=len(f1_empty_pin_points(inst))
    print(f"{name:22s} 심볼 {len(inst):3d} (멀티유닛 유닛 {multi:2d}, 빈핀번호 좌표 {empty:2d})"
          f"  실제겹침 {len(ov):3d}  실제관통 {len(cr):3d}")
    if ov: print("     겹침:", ", ".join(f"{a}~{b}" for a,b in ov[:12]))
    if cr: print("     관통:", ", ".join(sorted({f'{r}(u{u})' for _,_,r,u in cr})[:12]))
```

### 사용과 실측

```bash
python3 lint_filter.py "$PROJECT_DIR"/*.kicad_sch
# CONN.kicad_sch         심볼  82 (멀티유닛 유닛  0)  실제겹침  16  실제관통   0
# FPGA1.kicad_sch        심볼 131 (멀티유닛 유닛  4)  실제겹침   4  실제관통   0
# MCU.kicad_sch          심볼 102 (멀티유닛 유닛  0)  실제겹침   5  실제관통   0
```

371부품·8시트 실무 보드 실측:

| 도구 | 도구 원본 | 재판정 후 |
|------|---------:|----------:|
| `find_orphaned_wires` | 29 | 0 (29건 전부 빈 핀번호 심볼 좌표와 소수점까지 일치) |
| `find_overlapping_elements` | 64 | 27 |
| `find_wires_crossing_symbols` | 334 | 2 |

**재판정 결과도 확정이 아니다.** 남은 건은 `[후보]`로 두고 `get_schematic_view_region`으로
좌표를 확대해 눈으로 확인한 것만 등급을 매긴다. 바운딩 박스는 축 정렬 사각형이라
회전한 심볼·삼각형 몸체(다이오드 등)에서는 실제로 닿지 않아도 교차로 나올 수 있다.

---

## 주의사항

- `.kicad_sch` 직접 파싱은 kicad-cli 넷리스트 대비 정확도가 낮을 수 있다 (특히 계층 구조의 네트 연결)
- 직접 파싱 시 보고서에 "kicad-cli 미사용, 직접 파싱 모드 — 네트 연결 정확도 제한" 경고를 포함한다
- KiCad 버전에 따라 S-expression 키워드가 다를 수 있다 (version 필드 확인)
- `(exclude_from_sim yes)` 또는 `(in_bom no)` 부품은 본 파트리스트에서 제외하되, **"BOM 제외로 표시된 부품"
  별도 표로 반드시 남긴다** — 마운팅 홀·스페이서처럼 실물이 존재하는 기구 부품이 섞여 있다.
  넷리스트 XML에서는 `<property name="exclude_from_bom"/>`로 나온다. `kicad-cli sch export bom`의
  `--include-excluded-from-bom`은 KiCad 10.0.0에서 폐기돼 효과가 없다
