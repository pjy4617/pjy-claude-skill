---
name: vivado-bitstream
description: Vivado Bitstream 생성 및 FPGA 프로그래밍 시 사용. "비트스트림", "bitstream", "bit 파일", "FPGA 다운로드", "프로그래밍", "Hardware Manager" 등의 요청에 자동 적용.
---

# Vivado Bitstream 생성 & FPGA 프로그래밍 — 하이브리드 모드

> 기본: CLI batch로 비트스트림 생성 → 프로그래밍/ILA 디버깅 시 GUI 전환

## 전제 조건
- Implementation 체크포인트(`post_route.dcp`)가 존재해야 함
- 라우팅 후 타이밍 위반(WNS < 0)이 없어야 함
- DRC 위반이 없어야 함

## CLI: Bitstream 생성 (기본)

### 1. TCL 스크립트 실행
```bash
cd build
vivado -mode batch -source ../scripts/run_bit.tcl -log logs/bitstream.log
```

### 2. TCL 스크립트 구조 (`run_bit.tcl` 참조)
```tcl
# 1) 라우팅 체크포인트 로드
open_checkpoint checkpoints/post_route.dcp

# 2) Bitstream 생성
write_bitstream -force output/top.bit

# 3) (선택) Memory Configuration 파일 생성
# write_cfgmem -format mcs -interface SPIx4 \
#   -size 16 -loadbit "up 0x0 output/top.bit" \
#   -force -file output/top.mcs
```

### 3. 결과 확인
```bash
ls -la build/output/top.bit
# 파일 크기가 0이 아닌지 확인
```

## CLI: FPGA 프로그래밍 (batch)

### USB-JTAG 직접 프로그래밍
```bash
vivado -mode batch -source ../scripts/program_fpga.tcl
```

```tcl
# program_fpga.tcl
open_hw_manager
connect_hw_server
open_hw_target

set device [lindex [get_hw_devices] 0]
set_property PROGRAM.FILE {output/top.bit} $device
program_hw_devices $device

close_hw_target
close_hw_server
close_hw_manager
```

## GUI 전환: Hardware Manager / ILA 디버깅

사용자가 "Hardware Manager 열어", "ILA 보여줘", "FPGA 프로그래밍 GUI로", "디버그 프로브" 등을 요청하면 GUI로 전환한다.

### Hardware Manager GUI로 열기
```bash
# Hardware Manager만 GUI로 열기
vivado -mode gui -source open_hw_manager.tcl &
```
```tcl
# open_hw_manager.tcl
open_hw_manager
connect_hw_server
open_hw_target
# 이후 GUI에서 인터랙티브 조작
```
GUI에서 할 수 있는 일:
- **Program Device**: 비트스트림 선택하여 프로그래밍
- **ILA Dashboard**: 실시간 신호 캡처 및 트리거 설정
- **VIO Console**: Virtual I/O로 실시간 신호 제어
- **Memory Read/Write**: BRAM/DDR 내용 확인
- **JTAG Debug**: 저수준 디바이스 접근

### ILA (Integrated Logic Analyzer) 디버깅 워크플로우
```
1. RTL에 ILA IP 추가 (또는 합성 후 insert_debug_probes)
2. CLI로 합성/Impl/Bitstream 생성
3. CLI로 FPGA 프로그래밍
4. GUI Hardware Manager 열어서 ILA 파형 확인
```
```bash
# ILA 포함된 비트스트림 프로그래밍 후 GUI로 캡처 확인
vivado -mode gui &
# GUI에서: Open Hardware Manager → Connect → Program Device
# → ILA 자동 인식 → 트리거 설정 → Run Trigger
```

### SPI Flash 프로그래밍 (GUI 권장)
SPI Flash 프로그래밍은 Configuration Memory Device 설정이 필요하므로 GUI가 편리:
```bash
vivado -mode gui &
# GUI에서: Hardware Manager → Add Configuration Memory Device
# → MCS 파일 선택 → Program
```

CLI로도 가능:
```tcl
write_cfgmem -format mcs -interface SPIx4 \
  -size 16 -loadbit "up 0x0 output/top.bit" \
  -force -file output/top.mcs
```

## Bitstream 옵션
| 옵션 | 용도 |
|------|------|
| `-bin_file` | .bin 파일도 함께 생성 |
| `BITSTREAM.GENERAL.COMPRESS TRUE` | Bitstream 압축 |
| `BITSTREAM.CONFIG.SPI_BUSWIDTH 4` | SPI x4 모드 |
| `BITSTREAM.CONFIG.CONFIGRATE 33` | SPI 클럭 속도 (MHz) |

적용 방법 (write_bitstream 전):
```tcl
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
```

## 트러블슈팅
| 에러 | 원인 | 해결 |
|------|------|------|
| `DRC Error` | 비트스트림 전 DRC 실패 | `report_drc` 확인, 위반 수정 |
| `No hardware target` | FPGA 보드 미연결 | USB 연결 확인, 드라이버 설치 |
| `Program failed` | Bitstream-디바이스 불일치 | PART 설정과 보드 일치 확인 |
| `.bit 파일 0 bytes` | Bitstream 생성 실패 | 로그에서 에러 확인 |
| ILA 안 보임 | debug probe 미삽입 | 합성 시 `insert_debug_probes` 또는 RTL에 ILA IP 추가 |
