# PCB 물리 분석 + SI/PI 도메인 가이드

`.kicad_pcb` 분석과 신호/전원 무결성 검토의 판정 기준. MCP가 없을 때의 **직접 파싱** 방법도 포함.

---

## .kicad_pcb 직접 파싱 (폴백)

`.kicad_pcb`도 S-expression 텍스트다. 주요 토큰:

| 토큰 | 의미 | 추출 예 |
|------|------|---------|
| `(footprint "lib:fp" (layer "F.Cu") ... (property "Reference" "U1"))` | 부품 배치 | Ref, 레이어(앞/뒤), 좌표 |
| `(segment (start x y) (end x y) (width w) (layer "F.Cu") (net N))` | 트랙 세그먼트 | 길이=√(Δx²+Δy²), 폭, 레이어, 넷 |
| `(via (at x y) (size s) (drill d) (layers ...) (net N))` | 비아 | 좌표, 넷, 레이어 전환 |
| `(net N "넷이름")` | 넷 ID↔이름 매핑 | 트랙/비아 넷 해석 |
| `(zone ... (net N) (layer ...))` | 평면(copper pour) | 전원/GND 평면 존재 |
| `(gr_line ...)` on `Edge.Cuts` | 보드 외곽 | 치수 계산 |

### 파이썬 추출 스니펫

```python
import re, math

txt = open(PCB).read()

# 넷 ID → 이름
nets = dict(re.findall(r'\(net (\d+) "([^"]*)"\)', txt))

# 트랙 세그먼트: (넷, 길이mm, 폭mm, 레이어)
seg_re = re.compile(
    r'\(segment\s+\(start ([\d.-]+) ([\d.-]+)\)\s+\(end ([\d.-]+) ([\d.-]+)\)'
    r'\s+\(width ([\d.]+)\).*?\(layer "([^"]+)"\).*?\(net (\d+)\)', re.S)
tracks = []
for sx, sy, ex, ey, w, layer, net in seg_re.findall(txt):
    length = math.hypot(float(ex)-float(sx), float(ey)-float(sy))
    tracks.append({'net': nets.get(net, net), 'len': length,
                   'width': float(w), 'layer': layer})

# 넷별 총 트랙 길이 / 최소 폭
from collections import defaultdict
by_net = defaultdict(lambda: {'len': 0.0, 'min_w': 1e9})
for t in tracks:
    by_net[t['net']]['len'] += t['len']
    by_net[t['net']]['min_w'] = min(by_net[t['net']]['min_w'], t['width'])

# 비아 수 / 풋프린트 수
via_cnt = len(re.findall(r'\(via\b', txt))
fp_cnt  = len(re.findall(r'\(footprint\b', txt))
```

> 직접 파싱은 트랙 **길이/폭/넷/레이어**, 비아·풋프린트 카운트까지는 신뢰할 만하다.
> 존 채움(fill) 결과와 실제 클리어런스는 pcbnew 없이 재현되지 않으므로 **MCP(`query_zones`/`check_clearance`)가 필요**하다.
>
> 임피던스와 IR drop 절대값은 **스택업이 파일에 있으면 근사 계산한다**(아래 "스택업 파싱과 임피던스 근사" 절).
> 스택업이 비어 있으면 "미수행 — Board Setup > Physical Stackup 미설정"으로 표시한다.

---

## 스택업 파싱과 임피던스 근사

KiCad는 Board Setup > Physical Stackup을 채우면 그 값을 `.kicad_pcb`에 저장한다.
**서버에 스택업 읽기 도구는 없으므로 이 블록은 직접 파싱한다** — MCP 등록 여부와 무관하게 폴백 모드에서도 같은 계산이 된다.

```
(setup
  (stackup
    (layer "F.Cu" (type "copper") (thickness 0.035))
    (layer "dielectric 1" (type "prepreg") (thickness 0.0994) (material "2116 RC58%")
      (epsilon_r 4.45) (loss_tangent 0.02))
    (layer "In1.Cu" (type "copper") (thickness 0.0152))
    ...))
```

S-expression은 중첩되므로 **정규식만으로 블록을 자르면 안 된다**(비탐욕 매칭이 첫 `)`에서 끊긴다).
괄호 depth를 세어 블록을 잘라낸 뒤, 그 안에서만 필드를 정규식으로 뽑는다.

```python
import re

def block(src, key, start=0):
    """(key ...) 블록을 괄호 depth 로 잘라낸다 — 중첩은 정규식으로 못 센다."""
    m = re.compile(r'\(' + key + r'[\s(]').search(src, start)
    if not m:
        return ''
    i, d = m.start(), 0
    for j in range(i, len(src)):
        if src[j] == '(':
            d += 1
        elif src[j] == ')':
            d -= 1
            if d == 0:
                return src[i:j + 1]
    return ''

txt = open(pcb_path, encoding='utf-8').read()
stackup = block(txt, 'stackup')

# 층 순서대로 (이름, type, thickness, epsilon_r) 추출 — 없는 필드는 None
layers = []
for lm in re.finditer(r'\(layer\s+"([^"]+)"', stackup):
    body = block(stackup, 'layer', lm.start())
    def f(key):
        km = re.search(r'\(%s\s+([^\s)"]+)\)' % key, body)
        return float(km.group(1)) if km else None
    tm = re.search(r'\(type\s+"([^"]+)"\)', body)
    layers.append({
        'name': lm.group(1),
        'type': tm.group(1) if tm else None,   # "copper" / "core" / "prepreg" / 마스크·실크
        'thickness': f('thickness'),           # mm
        'epsilon_r': f('epsilon_r'),
    })

# 스택업이 없거나 dielectric 에 epsilon_r 이 없으면 임피던스 판정은 "미수행"
has_stackup = any(l['epsilon_r'] is not None for l in layers)
```

실측(KiCad 10 데모 보드): 4층 `CM5_MINIMA_3.kicad_pcb`는 층 17개에 `dielectric 1` = prepreg/0.0994 mm/Er 4.45,
2층 `ecc83-pp.kicad_pcb`는 층 9개에 `dielectric 1` = core/1.51 mm/Er 4.5가 나온다.
`layers`는 **파일에 적힌 물리 순서**이므로, 신호 층의 인덱스 앞뒤를 훑어 인접 dielectric과 기준 평면을 찾는다.

판정에 쓰는 값: 신호 층 바로 위/아래 dielectric 층의 `epsilon_r`(Er)과 `thickness`(H),
신호 층 자신의 copper `thickness`(T), 그리고 `query_traces`에서 받은 트랙 폭(W). 단위는 전부 mm.

**외층 마이크로스트립(IPC-2141 근사)** — 신호 층이 F.Cu/B.Cu 이고 한쪽만 기준 평면일 때:

```
Z0 = (87 / sqrt(Er + 1.41)) * ln(5.98 * H / (0.8 * W + T))      [Ω]
```

**내층 스트립라인(IPC-2141 근사)** — 신호 층이 두 기준 평면 사이에 있을 때(H는 평면 간 총 두께):

```
Z0 = (60 / sqrt(Er)) * ln(4 * H / (0.67 * pi * (0.8 * W + T)))   [Ω]
```

두 식 모두 근사다. 계산값은 목표값(아래 SI 표의 50/90/100 Ω) 대비 **±10% 이내면 OK,
±10~20%면 WARN, 그 밖이면 ERROR**로 판정하고, 보고서에는 반드시 "IPC-2141 근사식, 스택업 값 기준"임을 밝힌다.
차동 임피던스는 이 단일선 값에 페어 간격 의존 보정이 필요하므로, 정밀값이 필요하면
KiCad의 Board Setup > Physical Stackup > Impedance(또는 Tuning profiles) 계산 결과를 쓰도록 안내한다.

**IR drop 근사**: copper 층의 `thickness`(T, mm)가 있으면 트랙 저항을 구할 수 있다.

```
R = rho * L / (W * T)      rho(구리) = 1.68e-5 Ω·mm,  L·W·T 는 mm
V_drop = R * I
```

L은 `query_traces` 세그먼트 좌표 합, W는 그 넷의 최소 트랙 폭을 쓴다(최악값 기준).
스택업이 없어 T를 모르면 1oz = 0.035 mm 를 **가정값으로 명시**하거나 "미수행"으로 둔다.

---

## 보드 통계 판정

| 항목 | 확인 | WARN/ERROR 신호 |
|------|------|------------------|
| 미라우팅 넷 | ratsnest 잔존(넷에 트랙 0) | ERROR — 미완성 라우팅 |
| 양면 분포 | F.Cu vs B.Cu 풋프린트 비율 | (정보) |
| 비아 수 | 고속 넷 비아 과다 | WARN — 임피던스 불연속 |
| 보드 외곽 | Edge.Cuts 폐곡선 여부 | ERROR — 외곽 미완성 |

---

## 전원 넷 트랙 폭 (IR drop 추정)

외층(1oz/35µm) 기준 대략적 전류 용량(IPC-2221, ΔT=10°C):

| 트랙 폭 | 외층 허용 전류(근사) |
|---------|----------------------|
| 0.25 mm (10 mil) | ~0.9 A |
| 0.5 mm (20 mil) | ~1.5 A |
| 1.0 mm (40 mil) | ~2.6 A |
| 2.0 mm (80 mil) | ~4.5 A |

- 전원/GND 넷의 **최소 트랙 폭**이 예상 전류 대비 부족하면 WARN, 2배 이상 부족하면 ERROR.
- 평면(zone)으로 공급되는 전원은 폭 대신 평면 연속성/비아 stitching으로 판정.

---

## 신호 무결성(SI) 도메인 가이드

> **SI 전용 분석 도구는 없다.** MCP `query_traces`(넷별 세그먼트 좌표·폭·레이어)로 기하를 받아
> 길이·폭을 직접 계산하고(레이어 전환(비아) 수는 MCP로 오지 않으므로 `(via ...)` 직접 파싱), 아래 목표값과 대조해 판정한다.
> 절대 임피던스는 `(setup (stackup ...))`의 `epsilon_r`·`thickness`로 근사 계산한다("스택업 파싱과 임피던스 근사" 절).
> 스택업이 비어 있을 때만 폭/레이어 구성이 목표 범위에 드는지로 대체 판정한다.

| 인터페이스 | 임피던스 목표 | 길이 매칭 | 비고 |
|-----------|--------------|-----------|------|
| USB 2.0 (D+/D−) | 90 Ω diff | 페어 내 스큐 < 1.25 mm | 분기 금지 |
| Ethernet (MDI 쌍) | 100 Ω diff | 페어 내 < 0.5 mm, 쌍 간 매칭 권장 | 트랜스포머까지 |
| LVDS | 100 Ω diff | 페어 내 < 0.5 mm | |
| DDR3 (DQ/DQS) | 40 Ω SE / 80 Ω diff | 바이트 그룹 길이 편차 관리 | T-분기 회피 |
| RGMII | 50 Ω SE | 클럭/데이터 스큐 관리 | |
| 일반 단일선 | 50 Ω SE | — | |

검토 절차:
1. 고속 넷 식별(넷 이름 패턴: `USB_D`, `ETH_`, `*_DQ*`, `LVDS_`, `*_P`/`*_N`).
2. 페어(`_P`/`_N`, `+`/`−`) 매칭 → 페어 내 길이 편차 계산.
3. 레이어 전환(비아) 수 → reference plane 불연속 위험.
4. 트랙 폭 + 스택업(`epsilon_r`·`thickness`) → 마이크로스트립/스트립라인 근사식으로 Z0 계산 후 목표값 대비 판정.
   스택업이 없으면 폭·레이어 구성만으로 대체 판정하고 "미수행 — Board Setup > Physical Stackup 미설정"을 함께 적는다.

---

## 전원 무결성(PI) 도메인 가이드

> **PI 전용 분석 도구도 없다.** MCP `query_zones`(레이어별 카퍼 존 = 평면 커버리지),
> `query_traces`(전원 넷 폭), `get_net_pads` + `get_component_list`(디커플링 캡 ↔ 전원 핀 거리)로
> 입력을 모아 아래 기준으로 판정한다.

| 항목 | 확인 | 판정 |
|------|------|------|
| 전원/GND 평면 | `(zone)`로 plane 존재 | 평면 없으면 고전류·고속 보드에서 WARN |
| 평면 분할 | split plane이 고속 넷 reference를 끊는가 | ERROR — return path 단절 |
| 디커플링 근접 | IC 전원핀 ↔ 디커플링 캡 거리 | > 몇 mm면 WARN |
| 비아 stitching | 평면 간 연결 비아 충분 | 부족 시 WARN |
| IR drop | 전원 경로 저항 × 전류 | 스택업의 copper `thickness`가 있으면 `R = rho*L/(W*T)`로 근사 계산. 없으면 1oz(0.035 mm) 가정값을 명시하거나 트랙 폭·평면 커버리지로 대체 판정 |

---

## 도메인별 추가 (회로 분석과 공유)

`kicad-review`의 도메인 체크리스트(FPGA/MCU/PHY/EtherCAT/전원 IC)와 동일한 도메인 감지를 사용하되, 이 스킬은 **PCB 물리 구현** 관점을 추가한다:

- **FPGA**: 다수 전원 레일 평면 분할, 디커플링 캡 수량·배치, GT 트랜시버 차동 라우팅
- **Ethernet PHY**: MDI 차동 페어 임피던스·길이, 트랜스포머 1차/2차 분리, 아날로그/디지털 GND 분리
- **DDR**: 바이트레인 길이매칭, fly-by 토폴로지, VTT 종단
- **전원 IC**: 스위칭 노드 면적 최소화, 입력 캡 루프, 피드백 트레이스 노이즈 회피
