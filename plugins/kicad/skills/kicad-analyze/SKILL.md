---
name: kicad-analyze
description: "KiCad 회로(넷리스트)와 PCB(.kicad_pcb)를 정밀 분석합니다. 넷 연결 추적, ERC/DRC 검증, 핀 충돌 탐지, 풋프린트/보드 통계, 넷별 트랙 추적, 라우팅 품질, 신호 무결성(SI)/전원 무결성(PI) 분석을 수행합니다. 'PCB 분석', 'PCB 검토', 'PCB 리뷰', 'DRC 돌려줘', 'DRC 검사', 'ERC 검사', '넷 추적', '넷리스트 분석', '트랙 분석', '라우팅 검토', '신호 무결성', 'signal integrity', '전원 무결성', 'power integrity', '핀 충돌 확인', '보드 통계', '풋프린트 목록', 'KiCad 회로/PCB 분석', 'kicad pcb analyze' 등의 요청에 자동 적용. ※ 회로도 *설계* 적정성 리뷰·데이터시트 비교·BOM 생성은 kicad-review를 쓰고, *넷리스트 연결성·ERC/DRC·PCB 물리 레이아웃·SI/PI* 분석은 이 스킬을 쓴다. Seeed kicad-mcp-server(등록 시) → kicad-cli → 직접 파싱 순으로 폴백한다. STM32, FPGA, EtherCAT, 고속 신호 보드 등 모든 도메인 지원."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# KiCad 회로/PCB 정밀 분석

> 이 스킬은 KiCad **회로(넷리스트)**와 **PCB(.kicad_pcb)**를 프로그래매틱하게 분석한다.
> `kicad-review`(회로도 *설계* 리뷰 + BOM)와 상호 보완적이다 — 이 스킬은 **넷 연결성·전기 규칙·PCB 물리 레이아웃·신호/전원 무결성**에 초점을 둔다.

## kicad-review 와의 역할 분담

| | kicad-review | **kicad-analyze (이 스킬)** |
|---|---|---|
| 입력 | `.kicad_sch` | `.kicad_sch` + **`.kicad_pcb`** |
| 초점 | 설계 적정성(전원/데이터시트/도메인 체크리스트), BOM | 넷 연결성·ERC/DRC·**PCB 물리 레이아웃**·SI/PI |
| 방식 | 텍스트 파싱 + 데이터시트 웹 비교 | **Seeed MCP / kicad-cli** 기반 정밀 분석 |
| PCB | ✗ 미지원 | ✓ 풋프린트/트랙/비아/DRC/SI/PI |

회로도 *설계 검토*나 BOM이 필요하면 `kicad-review`를, 넷 연결 추적·PCB 분석·SI/PI가 필요하면 이 스킬을 쓴다.

---

## 분석 엔진 폴백 체인

이 스킬은 세 가지 엔진을 **가용한 것 우선**으로 사용한다. 도구별 매핑은 `references/mcp-tools.md` 참조.

```
[1순위] Seeed kicad-mcp-server (mcp__kicad__*)
        → ERC/DRC, 넷 추적, 풋프린트/보드 통계, SI/PI 분석까지 정밀
        → 등록: kicad-setup 스킬 또는 references/mcp-tools.md "설치" 참조
[2순위] kicad-cli  (PATH에 있을 때)
        → sch erc / pcb drc / sch export netlist / pcb export gerbers
        → SI/PI는 미지원 (heuristic 분석으로 대체)
[3순위] 직접 파싱  (.kicad_sch / .kicad_pcb S-expression 텍스트)
        → 넷/풋프린트/트랙 추출 가능, SI/PI·정밀 트랙 통계는 제한
```

> **중요**: 신호 무결성(SI)·전원 무결성(PI)·정밀 트랙 길이/비아 통계는 사실상 **Seeed MCP(pcbnew 기반)** 가 있어야 정확하다. 폴백 모드에서는 해당 항목을 "제한적/heuristic" 또는 "미수행"으로 보고서에 명시한다.

---

## 워크플로우 개요

```
[1] 환경·엔진 감지 — MCP 등록 / kicad-cli / 파일 탐색
 ↓
[2] 대상 식별 — .kicad_sch(회로) + .kicad_pcb(PCB) 매핑
 ↓
[3] 회로(넷리스트) 분석 — 넷/부품, 넷 연결 추적, ERC, 핀 충돌
 ↓
[4] PCB 분석 — 풋프린트, 보드 통계, 넷별 트랙, 라우팅 품질, DRC
 ↓
[5] 신호/전원 무결성(SI/PI) — 임피던스, 길이매칭, 전원 평면/IR drop
 ↓
[6] 종합 분석 보고서
```

---

## 단계 1: 환경·엔진 감지

```bash
# Seeed MCP 등록 여부 (등록 시 mcp__kicad__* 도구 사용 가능)
claude mcp list 2>/dev/null | grep -i "kicad" && echo "→ Seeed MCP 엔진 사용" \
  || echo "→ Seeed MCP 미등록 (kicad-cli/직접 파싱으로 폴백)"

# kicad-cli 가용성
kicad-cli version 2>/dev/null || kicad-cli --version 2>/dev/null \
  || echo "→ kicad-cli 없음 (직접 파싱 모드)"

# 대상 파일 탐색
find "$TARGET_DIR" -name "*.kicad_pro" -o -name "*.kicad_sch" -o -name "*.kicad_pcb" | sort
```

선택된 엔진을 보고서 헤더에 명시한다 (예: `엔진: Seeed MCP (pcbnew)` / `엔진: kicad-cli` / `엔진: 직접 파싱`).

---

## 단계 2: 대상 식별

- `.kicad_pro`(프로젝트) 기준으로 같은 베이스명의 `.kicad_sch`/`.kicad_pcb` 쌍을 묶는다.
- `.kicad_pcb`가 없으면 → PCB 단계(4·5)는 "PCB 파일 없음 — 회로 분석만 수행"으로 표시하고 회로(3)만 진행.
- 계층 회로도면 루트 `.kicad_sch`의 `(sheet ...)`로 서브시트를 파악한다.

---

## 단계 3: 회로(넷리스트) 분석

넷리스트 = "어떤 핀이 어떤 넷에 묶였는가"의 ground truth. 회로도 좌표·시각보다 정확하다.

### 3.1 넷리스트 생성

| 엔진 | 방법 |
|------|------|
| Seeed MCP | `mcp__kicad__generate_netlist` → `get_netlist_nets` / `get_netlist_components` |
| kicad-cli | `kicad-cli sch export netlist --format kicadxml --output /tmp/netlist.xml "$ROOT_SCH"` |
| 직접 파싱 | `.kicad_sch`의 `(label)`/`(global_label)`/`(wire)`로 넷 추론 (정확도 제한 경고) |

### 3.2 넷 연결 추적

특정 넷(예: `SPI_CLK`, `+3V3`)에 연결된 **모든 핀**을 나열한다.

- Seeed MCP: `mcp__kicad__trace_netlist_connection`(넷 → 핀 목록), `mcp__kicad__list_schematic_nets`
- 활용: 클럭/리셋/전원 넷의 팬아웃 확인, 미연결(1핀) 넷 탐지, 의도치 않은 다중 드라이버 탐지

### 3.3 ERC (Electrical Rules Check)

| 엔진 | 방법 |
|------|------|
| Seeed MCP | `mcp__kicad__run_erc` |
| kicad-cli | `kicad-cli sch erc --output /tmp/erc.json --format json --severity-all "$ROOT_SCH"` |
| 직접 파싱 | 미지원 → "ERC 미수행(엔진 없음)" 표시 |

주요 위반: 전원 핀에 PWR_FLAG 누락, output↔output 충돌, 미연결 입력, 양방향 핀 충돌.

### 3.4 핀 충돌 탐지

- Seeed MCP: `mcp__kicad__detect_pin_conflicts` — 같은 넷에 물린 핀 타입 조합이 전기적으로 위험한지 (output-output, power-output 등).
- 폴백: 넷별 핀 타입 집계 후 규칙 적용(아래 표).

| 넷에 물린 조합 | 판정 |
|---------------|------|
| output + output | ERROR (다중 드라이버) |
| power_out + power_out | ERROR |
| output + power_in | WARN (의도 확인) |
| 입력만 존재 (드라이버 0) | ERROR (플로팅 넷) |

---

## 단계 4: PCB 분석

`.kicad_pcb`가 있을 때만. 없으면 건너뛰고 보고서에 명시.

### 4.1 풋프린트 목록

- Seeed MCP: `mcp__kicad__list_pcb_footprints`(레이어 필터 가능) — 부품 배치, 앞/뒷면 분포 확인
- 폴백: `.kicad_pcb`의 `(footprint ... (layer "F.Cu"|"B.Cu"))` 추출
- 검토: BOM 부품 수 ↔ PCB 풋프린트 수 일치, 미배치(unplaced) 부품, 양면 분포

### 4.2 보드 통계

- Seeed MCP: `mcp__kicad__get_pcb_statistics` — 레이어 수, 트랙/비아 수, 넷 수, 보드 외곽 치수
- 폴백: `(segment)`/`(via)`/`(net)` 카운트로 근사 (트랙 길이는 좌표로 직접 계산)

### 4.3 넷별 트랙 추적

- Seeed MCP: `mcp__kicad__find_tracks_by_net`(넷 → 트랙 세그먼트/레이어/폭), `mcp__kicad__analyze_pcb_nets`
- 검토: 전원/GND 넷 트랙 폭 충분성, 고속 넷의 레이어 전환(비아) 수, 미라우팅(ratsnest 잔존) 넷

### 4.4 DRC (Design Rules Check)

| 엔진 | 방법 |
|------|------|
| Seeed MCP | `mcp__kicad__run_drc` |
| kicad-cli | `kicad-cli pcb drc --output /tmp/drc.json --format json --severity-all "$PCB"` |
| 직접 파싱 | 미지원 → "DRC 미수행(엔진 없음)" 표시 |

주요 위반: clearance 미달, 미라우팅 넷, 실루엣/마스크 겹침, 드릴/홀 규칙, copper-edge clearance.

---

## 단계 5: 신호 무결성(SI) / 전원 무결성(PI)

> **이 단계는 Seeed MCP(pcbnew) 가용 시에만 정밀하다.** 폴백 모드에서는 좌표 기반 heuristic으로 가능한 범위만 보고하고, 불가 항목은 "미수행"으로 명시한다.

### 5.1 신호 무결성 (SI)

- Seeed MCP: `mcp__kicad__analyze_pcb_signal_integrity`
- 검토 항목:
  - **임피던스**: 고속 넷(USB/Ethernet/LVDS/DDR)의 트랙 폭·레이어 스택업 대비 목표 임피던스(50Ω SE / 90·100Ω diff)
  - **길이 매칭**: 차동 페어 내 스큐, 버스(DDR 등) 그룹 길이 편차
  - **레이어 전환**: 고속 넷의 비아 수(reference plane 불연속)
  - **스터브/분기**: T-분기, 미사용 스터브
- 도메인 가이드는 `references/pcb-analysis.md` 참조.

### 5.2 전원 무결성 (PI)

- Seeed MCP: `mcp__kicad__analyze_pcb_power_integrity`
- 검토 항목:
  - 전원/GND **평면(plane)** 존재 및 분할 적정성
  - 전원 넷 트랙/평면 폭 대비 전류(IR drop 추정)
  - 디커플링 캡 배치 근접성(핀 ↔ 캡 거리)
  - 비아 stitching(평면 연결) 충분성

---

## 단계 6: 종합 분석 보고서

```
═══════════════════════════════════════════
  KiCad 회로/PCB 분석 보고서
═══════════════════════════════════════════

프로젝트: {프로젝트명}
대상: {.kicad_sch} / {.kicad_pcb}
엔진: {Seeed MCP (pcbnew) | kicad-cli | 직접 파싱}
분석일: {날짜}

━━━ 요약 ━━━
  회로(넷리스트):  넷 {n} / 부품 {n} / ERC  OK {n} · WARN {n} · ERROR {n}
  PCB:            풋프린트 {n} / 트랙 {n} / 비아 {n} / DRC  OK {n} · WARN {n} · ERROR {n}
  SI/PI:          {수행/heuristic/미수행} — 이슈 {n}

━━━ ERROR 항목 ━━━
  🔴 [{ERC|DRC|PIN|SI|PI}] {설명}
     위치: {넷/부품/좌표}
     근거: {규칙/측정값}
     조치: {구체적 수정}

━━━ WARN 항목 ━━━
  ⚠️ [{카테고리}] {설명} — {권장}

━━━ 미수행/제한 항목 ━━━
  ⊘ {항목}: {사유 — 예: "SI 분석 — Seeed MCP 미등록"}
     → 활성화: kicad-setup 스킬로 Seeed MCP 등록 후 재실행
```

### 보고서 원칙

- **근거 명시**: 모든 ERROR/WARN에 규칙명 또는 측정값(트랙 폭 µm, 길이 mm, clearance mil)을 붙인다.
- **추측 금지**: 엔진이 측정하지 못한 항목은 "미수행"으로 솔직히 표시한다 — "아마 괜찮음" 금지.
- **구체적 조치**: "넷 +3V3 트랙폭 0.25mm → 0.5mm 이상(예상 전류 1.2A 기준)" 처럼 수치로.
- **활성화 안내**: 폴백으로 막힌 분석은 Seeed MCP 등록 경로(kicad-setup)를 안내한다.

---

## 에이전트 위임

실제 분석은 전용 에이전트에 위임한다:

- **kicad-pcb-analyzer**: 엔진 감지 → 넷리스트/ERC/DRC/트랙/SI·PI 분석 → 보고서 작성

이 에이전트는 `tools:`를 명시하지 않아 등록된 모든 도구를 상속하므로, Seeed MCP(`mcp__<서버명>__*`)가 있으면 1순위로 쓰고 없으면 kicad-cli/직접 파싱으로 폴백한다. 에이전트는 `kicad-setup` 스킬로 타겟 프로젝트의 `.claude/agents/`에 설치한다.

---

## 참조 파일

- `references/mcp-tools.md` — Seeed MCP 도구 카탈로그 + 엔진별 매핑 + 설치/등록
- `references/pcb-analysis.md` — PCB 물리 분석·SI/PI 도메인 가이드 + 직접 파싱 방법

## 사용 예시

```
사용자: "이 보드 PCB 분석해줘"
사용자: "DRC 돌리고 미라우팅 넷 찾아줘"
사용자: "+3V3 넷에 뭐가 연결됐는지 추적해줘"
사용자: "Ethernet 차동 페어 임피던스랑 길이 매칭 확인해줘"
사용자: "핀 충돌 있는지 ERC 검사해줘"
```

$ARGUMENTS
