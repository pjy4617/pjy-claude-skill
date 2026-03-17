---
name: vivado-build-all
description: Vivado 전체 빌드 플로우(합성 → Implementation → Bitstream)를 순차 실행합니다. "전체 빌드", "build all", "처음부터 빌드", "빌드 전체", "synth부터 bitstream까지" 등의 요청에 자동 적용.
---

# Vivado 전체 빌드 플로우 (Synthesis → Implementation → Bitstream)

> 합성 → Implementation → Bitstream을 순차 실행합니다.
> 각 단계 실패 시 즉시 중단하고 원인 분석을 안내합니다.

## 선행 조건 (권장)

빌드 전 아래 리뷰를 실행하면 빌드 실패를 사전에 방지할 수 있습니다:
- RTL 리뷰: `"RTL 리뷰해줘"` → rtl-reviewer 에이전트
- 핀 리뷰: `"핀 배치 확인해줘"` → pin-reviewer 에이전트
- FAIL 항목이 있으면 먼저 수정을 권장합니다. 사용자가 무시하면 빌드를 진행합니다.

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BOARD` | `arty_a7` | 보드 이름 → XDC 파일 경로 결정 |
| `TOP` | `top` | 톱 모듈 이름 |
| `PART_NUM` | `xc7a35ticsg324-1L` | FPGA 파트넘버 |

## 실행 절차

### 0단계: 환경 확인
```bash
# Vivado 설치 확인
which vivado || echo "ERROR: Vivado not found in PATH"

# 소스 파일 존재 확인
ls rtl/*.v rtl/*.sv 2>/dev/null || echo "WARNING: No RTL files found"

# 제약 파일 확인
BOARD=${BOARD:-arty_a7}
ls constraints/${BOARD}.xdc || echo "ERROR: XDC not found for board ${BOARD}"

# 빌드 디렉토리 생성
mkdir -p build/{checkpoints,reports,output,logs}
```

### 1단계: 합성 (Synthesis)
```bash
cd build
BOARD=${BOARD:-arty_a7} TOP=${TOP:-top} \
  vivado -mode batch -source ../scripts/run_synth.tcl \
  -log logs/synth.log -journal logs/synth.jou
```

**실패 시 중단.** 원인 분석:
- 로그 확인: `grep -E "ERROR|CRITICAL" build/logs/synth.log`
- RTL 리뷰 요청: `"RTL 리뷰해줘"` → 래치 추론, 멀티 드라이버 등 확인
- 일반적 원인: 모듈 미발견(read_verilog 누락), 구문 오류, 포트 불일치

**성공 시 결과 확인:**
```bash
grep "WNS\|WHS" build/reports/timing_synth.rpt
grep -A 20 "Slice Logic" build/reports/utilization_synth.rpt
```

### 2단계: Implementation (Place & Route)
```bash
cd build
vivado -mode batch -source ../scripts/run_impl.tcl \
  -log logs/impl.log -journal logs/impl.jou
```

**실패 시 중단.** 원인 분석:
- 로그 확인: `grep -E "ERROR|CRITICAL" build/logs/impl.log`
- 타이밍 분석 요청: `"타이밍 분석해줘"` → timing-analyst 에이전트
- 일반적 원인: 타이밍 위반(WNS < 0), 리소스 부족, 배선 불가

**성공 시 결과 확인:**
```bash
grep "WNS\|WHS" build/reports/timing_route.rpt
grep -c "VIOLATION" build/reports/drc_route.rpt
grep "Total On-Chip Power" build/reports/power_route.rpt
```

### 3단계: Bitstream 생성
```bash
cd build
vivado -mode batch -source ../scripts/run_bit.tcl \
  -log logs/bitstream.log -journal logs/bitstream.jou
```

**실패 시 중단.** 원인 분석:
- 로그 확인: `grep -E "ERROR|CRITICAL" build/logs/bitstream.log`
- DRC 확인: `cat build/reports/drc_final.rpt`
- 일반적 원인: DRC 위반, 타이밍 미충족 상태에서 bitstream 시도

**성공 시 결과 확인:**
```bash
ls -la build/output/top.bit
```

## 전체 빌드 결과 요약

모든 단계가 성공하면 아래 형식으로 요약합니다:

```
═══════════════════════════════════════
  Vivado 전체 빌드 완료
  보드: {BOARD} ({PART})
  톱 모듈: {TOP}
═══════════════════════════════════════

[합성]
  WNS: +1.234 ns (Setup OK)
  WHS: +0.056 ns (Hold OK)
  LUT: 1234/20800 (5.9%)
  FF:  567/41600 (1.4%)

[Implementation]
  WNS: +0.876 ns (Setup OK)
  WHS: +0.023 ns (Hold OK)
  DRC: 0 violations
  Power: 0.123 W

[Bitstream]
  파일: build/output/top.bit
  크기: 2,083,740 bytes

다음 단계:
  FPGA 프로그래밍: "FPGA에 다운로드해줘"
  GUI 확인:       "라우팅 결과 보여줘"
  ILA 디버깅:     "Hardware Manager 열어줘"
```

## 타이밍 위반 시 자동 연계

빌드 중 WNS < 0 (타이밍 위반)이 발생하면:
1. 위반 심각도에 따라 안내:
   - **-0.5 ~ 0 ns**: "phys_opt_design 반복으로 해결 가능할 수 있습니다"
   - **-2 ~ -0.5 ns**: "RTL 파이프라인 추가가 필요합니다. timing-analyst에게 분석 요청하세요"
   - **< -2 ns**: "클럭 주파수를 낮추거나 아키텍처 재설계가 필요합니다"
2. `"타이밍 분석해줘"` → timing-analyst 에이전트에게 상세 분석 위임

## 주의사항
- 전체 빌드는 디자인 크기에 따라 **수 분~수십 분** 소요될 수 있습니다
- 각 단계의 로그는 `build/logs/`에 저장되므로 나중에 확인 가능합니다
- 빌드 중 `build/checkpoints/`에 중간 체크포인트가 저장되므로, 특정 단계부터 재실행 가능합니다
