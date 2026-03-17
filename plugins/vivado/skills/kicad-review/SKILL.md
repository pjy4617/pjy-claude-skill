---
name: kicad-review
allowed-tools: Bash, Read, Write, Edit
description: KiCad 프로젝트 회로도를 종합 검토합니다. ERC/DRC 실행, 스키매틱 파싱, 넷리스트 분석, BOM 검증을 수행합니다. "KiCad 회로도 리뷰", "ERC 실행", "회로 검토" 등의 요청에 자동 적용.
---

# KiCad 회로 설계 종합 검토

현재 프로젝트 디렉토리의 KiCad 파일을 종합적으로 검토해주세요.

## 수행 단계

### 1. 환경 파악
- `kicad-cli --version` 으로 CLI 사용 가능 여부 확인
- `.kicad_sch`, `.kicad_pcb`, `.kicad_pro` 파일 탐색
- 프로젝트 구조 파악 (멀티시트 여부 포함)

### 2. ERC 실행 (kicad-cli 가용 시)
```bash
kicad-cli sch erc --output erc_report.json --format json --severity-all --exit-code-violations <ROOT_SCH>
```
결과를 분석하여 각 위반 항목의 원인과 해결 방법을 설명

### 3. 스키매틱 직접 분석
`.kicad_sch` 파일을 읽어 S-expression 구조를 파싱하고:
- 심볼, 와이어, 라벨, 전원 심볼, 계층 시트 추출
- 부품 분류 (저항, 캐패시터, IC, 커넥터 등)
- 전원 네트 구성 확인
- 디커플링 캡 존재 여부 확인

### 4. 넷리스트 기반 검증 (kicad-cli 가용 시)
```bash
kicad-cli sch export netlist --output netlist.xml --format kicadxml <ROOT_SCH>
```
넷리스트에서 연결성을 검증하고 단일 핀 넷, 전원 핀 미연결 등 확인

### 5. BOM 추출 및 검토 (kicad-cli 가용 시)
```bash
kicad-cli sch export bom --output bom.csv --fields 'Reference,Value,Footprint,${DNP}' --group-by 'Value,Footprint' --sort-asc <ROOT_SCH>
```

### 6. PCB DRC (kicad_pcb 파일 존재 시)
```bash
kicad-cli pcb drc --output drc_report.json --format json --severity-all --schematic-parity --exit-code-violations <PCB_FILE>
```

### 7. 종합 보고서 작성
다음 체크리스트 기반으로 검토:
- **전원부**: 전원 레일, 디커플링 캡, LDO/DCDC 주변 회로, PWR_FLAG
- **MCU**: 클럭, 리셋, 부트 핀, 미사용 핀, 디버그 인터페이스
- **통신**: I2C 풀업, SPI CS, UART 크로스, RS485 종단, CAN 종단
- **보호회로**: ESD, TVS, 역전압, 과전류
- **일반**: 네트 라벨 일관성, 풋프린트 할당, 테스트 포인트

각 항목을 **PASS / WARN / FAIL / N/A** 로 평가하고, 
심각도별(Critical > Warning > Info) 문제점을 정리해주세요.

$ARGUMENTS
