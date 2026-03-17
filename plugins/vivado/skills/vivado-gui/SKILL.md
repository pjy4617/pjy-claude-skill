---
name: vivado-gui
description: Vivado GUI를 열거나 GUI에서 시각적으로 확인해야 할 때 사용. "GUI 열어", "결과 보여줘", "스키매틱", "Device View", "파형 보여줘", "ILA", "Hardware Manager", "Block Design" 등의 요청에 자동 적용.
---

# Vivado GUI 연동 — 하이브리드 모드 가이드

> 원칙: CLI에서 빌드 → 체크포인트(.dcp)를 GUI에서 열어 시각적 확인
> .xpr 프로젝트 파일이 필요 없음

## 핵심 개념: DCP 체크포인트

모든 Vivado 빌드 단계는 `.dcp` (Design CheckPoint) 파일을 남긴다.
이 파일을 `vivado 파일명.dcp` 로 열면 GUI가 해당 시점의 디자인을 보여준다.

```
build/checkpoints/
├── post_synth.dcp    ← 합성 후 (스키매틱, 리소스)
├── post_place.dcp    ← 배치 후 (Device View, 배치 결과)
└── post_route.dcp    ← 라우팅 후 (배선, 타이밍 경로, 전체 결과)
```

## GUI 열기 명령 (단계별)

### 합성 결과 확인
```bash
vivado build/checkpoints/post_synth.dcp &
```
확인 가능 항목: Schematic View, Utilization Report, Hierarchy Browser

### 배치 결과 확인
```bash
vivado build/checkpoints/post_place.dcp &
```
확인 가능 항목: Device View (칩 위 배치), Clock Region, Placement Constraint

### 라우팅 결과 확인 (가장 자주 사용)
```bash
vivado build/checkpoints/post_route.dcp &
```
확인 가능 항목: 배선 경로, Critical Path, Power Report, DRC

### 시뮬레이션 파형 확인
```bash
# 방법 1: xsim GUI 모드
xsim sim_snapshot -gui &

# 방법 2: WDB 파일 열기
vivado -mode gui -source open_waveform.tcl &

# 방법 3: GTKWave (경량 대안)
gtkwave build/dump.vcd &
```

### Hardware Manager (FPGA 프로그래밍 / ILA)
```bash
vivado -mode gui -source open_hw_manager.tcl &
```

## GUI에서만 편한 작업 목록

| 작업 | CLI 가능? | GUI 권장 이유 |
|------|-----------|--------------|
| 파형 디버깅 | △ (로그만) | 시각적 파형 비교, 줌, 커서 |
| Device View | ✗ | 물리적 배치를 눈으로 확인 |
| Schematic | ✗ | 합성된 회로도 탐색 |
| ILA 캡처 | △ (TCL) | 트리거 설정, 실시간 파형 |
| Block Design (IP) | ✗ | AXI 연결, IP 설정 |
| Floorplanning | ✗ | Pblock 드래그앤드롭 |
| SPI Flash 프로그래밍 | △ (TCL) | Memory Device 설정이 GUI가 편함 |

## X11 / 디스플레이 설정

WSL에서 GUI를 사용하려면 X 서버가 필요합니다:

### WSL2 + Windows 11 (WSLg 내장)
```bash
# 보통 추가 설정 불필요. 안 되면:
export DISPLAY=:0
```

### WSL2 + Windows 10 (X 서버 필요)
```bash
# VcXsrv 또는 X410 설치 후:
export DISPLAY=$(grep nameserver /etc/resolv.conf | awk '{print $2}'):0.0
```

### SSH 원격 접속 시
```bash
# X11 forwarding 활성화
ssh -X user@remote-server
# 또는 -Y (trusted)
ssh -Y user@remote-server
```

## 도우미 TCL 스크립트

### open_waveform.tcl
```tcl
open_wave_database build/output.wdb
```

### open_hw_manager.tcl
```tcl
open_hw_manager
connect_hw_server
open_hw_target
```

## 주의사항
- GUI는 `&` (백그라운드)로 실행하여 터미널을 블로킹하지 않도록 한다
- GUI에서 디자인을 수정하지 않는다. 수정은 항상 RTL/XDC에서 하고 CLI로 다시 빌드한다
- GUI는 "보는 용도"로만 사용. "빌드"는 CLI 스킬이 담당한다
