---
name: vivado-impl
description: Vivado Implementation(배치 및 라우팅) 실행 시 사용. "Implementation 돌려", "Place and Route", "배치", "라우팅", "impl", "배치 결과 보여줘", "Device View" 등의 요청에 자동 적용.
---

# Vivado Implementation (Place & Route) — 하이브리드 모드

> 기본: CLI batch로 P&R → 배치 확인/타이밍 디버깅 시 GUI 전환

## 전제 조건
- 합성 체크포인트(`post_synth.dcp`)가 존재해야 함
- 합성 단계에서 타이밍 위반이 없는 것이 이상적

## CLI 실행 (기본)

### 1. TCL 스크립트 실행
```bash
cd build
vivado -mode batch -source ../scripts/run_impl.tcl -log logs/impl.log -journal logs/impl.jou
```

### 2. TCL 스크립트 구조 (`run_impl.tcl` 참조)
```tcl
# 1) 합성 체크포인트 로드
open_checkpoint checkpoints/post_synth.dcp

# 2) Optimization (선택)
opt_design

# 3) Place
place_design
# 체크포인트 저장
write_checkpoint -force checkpoints/post_place.dcp
report_timing_summary -file reports/timing_place.rpt

# 4) Physical Optimization (선택, 타이밍 개선)
phys_opt_design

# 5) Route
route_design
write_checkpoint -force checkpoints/post_route.dcp

# 6) 최종 리포트
report_timing_summary -file reports/timing_route.rpt
report_utilization -file reports/utilization_route.rpt
report_power -file reports/power_route.rpt
report_drc -file reports/drc_route.rpt
```

### 3. 결과 확인 (반드시 수행)
```bash
# 최종 타이밍 확인 (Setup + Hold)
grep "WNS" build/reports/timing_route.rpt
grep "WHS" build/reports/timing_route.rpt

# DRC 위반 확인
grep -c "VIOLATION" build/reports/drc_route.rpt

# 전력 소비 확인
grep "Total On-Chip Power" build/reports/power_route.rpt
```

## GUI 전환: 배치/라우팅 시각화

사용자가 "배치 결과 보여줘", "Device View", "라우팅 확인", "타이밍 경로 보여줘" 등을 요청하면 체크포인트를 GUI로 연다.

### 배치 결과 확인 (Device View)
```bash
# 배치 후 체크포인트를 GUI에서 열기
vivado build/checkpoints/post_place.dcp &
```
GUI에서 확인 사항:
- **Device View**: FPGA 칩 위에 로직이 어디에 배치되었는지
- **Highlight Net**: 특정 신호의 물리적 경로
- **Clock Region**: 클럭 트리가 어떤 영역을 커버하는지

### 라우팅 결과 확인
```bash
# 라우팅 후 체크포인트를 GUI에서 열기
vivado build/checkpoints/post_route.dcp &
```
GUI에서 확인 사항:
- **Routing Resource Usage**: 배선 혼잡도
- **Critical Path**: 타이밍 위반 경로를 시각적으로 추적
- **Report Timing** 인터랙티브 분석

### 타이밍 위반 경로 시각적 디버깅
```tcl
# GUI에서 worst path를 하이라이트
open_checkpoint build/checkpoints/post_route.dcp
start_gui
# GUI 메뉴: Report → Timing → Report Timing Summary
# worst path 클릭 → Schematic에서 경로 하이라이트
```

## Implementation 전략 옵션
| 전략 | 용도 |
|------|------|
| `Vivado Implementation Defaults` | 기본 (대부분 충분) |
| `Performance_Explore` | 타이밍 최적화 우선 |
| `Area_Explore` | 면적 최소화 우선 |
| `Power_DefaultOpt` | 전력 최적화 |

Non-Project 모드 적용 방법 (run_impl.tcl에서):
```tcl
# 전략 직접 지정 (Non-Project 모드에서는 개별 옵션으로)
place_design -directive ExtraTimingOpt
route_design -directive Explore
```

## 트러블슈팅
| 에러/경고 | 원인 | 해결 |
|-----------|------|------|
| `WNS < 0` (라우팅 후) | 타이밍 미충족 | `phys_opt_design` 반복 또는 RTL 수정. GUI에서 critical path 확인 권장 |
| `Unroutable` | 배선 불가 | 배치 제약 완화, 디자인 단순화 |
| `DRC VIOLATION` | 설계 규칙 위반 | 리포트 상세 확인 후 XDC 수정 |
| Place 실패 | 리소스 부족 | `report_utilization`로 사용량 확인 |
