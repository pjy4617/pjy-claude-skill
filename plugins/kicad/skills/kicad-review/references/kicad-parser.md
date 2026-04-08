# KiCad 회로도 파싱 가이드

> KiCad 9.x의 `.kicad_sch` 파일은 S-expression(Lisp 유사) 형식이다.
> 이 문서는 회로도에서 부품, 핀, 네트, 값을 추출하는 방법을 설명한다.

## 목차

1. [파일 구조 개요](#파일-구조-개요)
2. [kicad-cli를 이용한 넷리스트 추출](#kicad-cli-넷리스트-추출)
3. [.kicad_sch 직접 파싱](#직접-파싱)
4. [계층 구조 처리](#계층-구조-처리)
5. [파싱 스크립트 모음](#파싱-스크립트)

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

## 주의사항

- `.kicad_sch` 직접 파싱은 kicad-cli 넷리스트 대비 정확도가 낮을 수 있다 (특히 계층 구조의 네트 연결)
- 직접 파싱 시 보고서에 "kicad-cli 미사용, 직접 파싱 모드 — 네트 연결 정확도 제한" 경고를 포함한다
- KiCad 버전에 따라 S-expression 키워드가 다를 수 있다 (version 필드 확인)
- `(exclude_from_sim yes)` 또는 `(in_bom no)` 부품은 BOM에서 제외한다
