---
name: vivado-sim
description: Verilog 시뮬레이션 실행 시 사용. "시뮬레이션 돌려", "테스트벤치 실행", "파형 확인", "파형 열어줘", "waveform", "xsim", "시뮬" 등의 요청에 자동 적용.
---

# Vivado 시뮬레이션 (xsim) — 하이브리드 모드

> 기본: CLI에서 자동 실행 → 파형 디버깅 필요 시 GUI로 전환
> 요구: Vivado 2020.1+ (xvlog, xelab, xsim CLI)

## CLI 실행 (기본)

### 1. 컴파일 (xvlog)
```bash
cd build

# Verilog 파일 컴파일
xvlog ../rtl/모듈명.v ../tb/tb_모듈명.v

# SystemVerilog 파일이 있으면 --sv 옵션 추가
xvlog --sv ../rtl/모듈명.sv ../tb/tb_모듈명.sv
```
- `.v` 파일은 `xvlog`로, `.sv` 파일은 `xvlog --sv`로 컴파일
- 여러 파일은 공백으로 구분하거나 `-f filelist.txt` 사용
- 혼합 프로젝트에서는 `.v`와 `.sv`를 별도 xvlog 호출로 처리

### 2. 엘라보레이션 (xelab)
```bash
xelab -debug typical tb_모듈명 -s sim_snapshot
```
- `-debug typical`: 파형 덤프 가능하게 (GUI 전환 시 필수)
- `-s`: 스냅샷 이름 지정
- 타이밍 시뮬레이션 시: `-L unisims_ver -L secureip`

### 3. 시뮬레이션 실행 (xsim)
```bash
xsim sim_snapshot -runall -wdb output.wdb
```
- `-runall`: $finish까지 실행
- `-wdb`: 파형 파일 저장 (GUI에서 열 수 있음)
- TCL 명령으로 실행: `xsim sim_snapshot -tclbatch sim_cmds.tcl`

### 4. 결과 확인
```bash
# 로그에서 PASS/FAIL 확인
grep -E "(PASS|FAIL|ERROR)" xsim.log
```

## GUI 전환: 파형 디버깅

사용자가 "파형 보여줘", "waveform 열어줘", "파형 디버깅" 등을 요청하면 GUI로 전환한다.

### 방법 1: WDB 파형 파일 열기 (CLI 시뮬레이션 후)
```bash
# 백그라운드로 Vivado GUI 실행 (터미널 블로킹 방지)
vivado -mode gui -source open_waveform.tcl &
```
```tcl
# open_waveform.tcl
open_wave_database build/output.wdb
```

### 방법 2: GUI 모드에서 시뮬레이션 직접 실행
```bash
# xsim을 GUI 모드로 실행 (인터랙티브 디버깅)
xsim sim_snapshot -gui &
```
이 모드에서는:
- 파형 추가/삭제를 마우스로 조작
- 브레이크포인트 설정
- 신호값 실시간 모니터링
- 시간 커서로 특정 구간 줌인

### 방법 3: VCD → GTKWave (경량 대안)
```bash
# GTKWave가 설치되어 있으면 (Vivado보다 가벼움)
gtkwave build/dump.vcd &
```

## 테스트벤치 작성 규칙
- 파일명: `tb_모듈명.v`
- 클럭 생성: `always #5 clk = ~clk;` (100MHz 기준)
- 종료: 반드시 `$finish;` 포함
- 검증: `$display`로 PASS/FAIL 출력
- 파형 덤프 (두 가지 포맷 모두 생성 권장):
```verilog
initial begin
    // VCD: GTKWave 등 외부 도구용
    $dumpfile("dump.vcd");
    $dumpvars(0, tb_모듈명);
    // WDB는 xsim이 -wdb 옵션으로 자동 생성
end
```

## 테스트벤치 템플릿
`tb_template.v` 파일을 참조하여 새 테스트벤치를 생성합니다.

## 시뮬레이션 FAIL 시 원인 추적

시뮬레이션이 FAIL이면 다음 순서로 원인을 추적합니다:
1. tb-reviewer에게 → "TB 자체에 버그가 있나?" 확인
2. rtl-reviewer에게 → "RTL에 합성 가능성 문제가 있나?" 확인
3. 둘 다 PASS면 → DUT 로직 버그 → rtl-designer에게 수정 요청

## 트러블슈팅
| 에러 | 원인 | 해결 |
|------|------|------|
| `ERROR: [XSIM 43-3409]` | 모듈 미발견 | `read_verilog` 경로 확인 |
| `ERROR: [VRFC 10-2458]` | 구문 오류 | 해당 라인 Verilog 문법 확인 |
| 시뮬레이션 hang | `$finish` 누락 | 테스트벤치에 `$finish` 추가 |
| 파형 없음 | `$dumpvars` 누락 | initial 블록에 추가 |
| GUI 안 열림 | DISPLAY 미설정 | `export DISPLAY=:0` 또는 X11 forwarding 확인 |
| WDB 파일 없음 | `-wdb` 옵션 누락 | xsim 실행 시 `-wdb output.wdb` 추가 |
