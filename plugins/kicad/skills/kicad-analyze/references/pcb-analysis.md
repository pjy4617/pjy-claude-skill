# PCB 물리 분석 + SI/PI 도메인 가이드

`.kicad_pcb` 분석과 신호/전원 무결성 검토의 판정 기준. Seeed MCP가 없을 때의 **직접 파싱** 방법도 포함.

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
> 그러나 임피던스(스택업 유전율 필요), reference plane 연속성, IR drop은 **계산 불가** → Seeed MCP 필요.

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

> 정밀 임피던스/길이매칭은 `analyze_pcb_signal_integrity`(Seeed MCP) 결과를 1차로 신뢰. 아래는 검토 항목과 목표값.

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
4. 트랙 폭 → 스택업 대비 목표 임피던스 충족 여부(MCP 결과 우선).

---

## 전원 무결성(PI) 도메인 가이드

| 항목 | 확인 | 판정 |
|------|------|------|
| 전원/GND 평면 | `(zone)`로 plane 존재 | 평면 없으면 고전류·고속 보드에서 WARN |
| 평면 분할 | split plane이 고속 넷 reference를 끊는가 | ERROR — return path 단절 |
| 디커플링 근접 | IC 전원핀 ↔ 디커플링 캡 거리 | > 몇 mm면 WARN |
| 비아 stitching | 평면 간 연결 비아 충분 | 부족 시 WARN |
| IR drop | 전원 경로 저항 × 전류 | MCP `analyze_pcb_power_integrity` 결과 기준 |

---

## 도메인별 추가 (회로 분석과 공유)

`kicad-review`의 도메인 체크리스트(FPGA/MCU/PHY/EtherCAT/전원 IC)와 동일한 도메인 감지를 사용하되, 이 스킬은 **PCB 물리 구현** 관점을 추가한다:

- **FPGA**: 다수 전원 레일 평면 분할, 디커플링 캡 수량·배치, GT 트랜시버 차동 라우팅
- **Ethernet PHY**: MDI 차동 페어 임피던스·길이, 트랜스포머 1차/2차 분리, 아날로그/디지털 GND 분리
- **DDR**: 바이트레인 길이매칭, fly-by 토폴로지, VTT 종단
- **전원 IC**: 스위칭 노드 면적 최소화, 입력 캡 루프, 피드백 트레이스 노이즈 회피
