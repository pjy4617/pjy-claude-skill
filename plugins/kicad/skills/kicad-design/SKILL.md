---
name: kicad-design
description: "HW PRD, 설계사양서, 블록다이어그램을 입력받아 KiCad 회로도(.kicad_sch)를 생성합니다. 'KiCad 회로도 만들어', '회로도 설계', '회로 생성', 'schematic design', 'PRD 기반 회로도', '설계사양서로 회로 만들어', '블록다이어그램 회로도 변환', '보드 설계', 'KiCad 스키매틱 생성', 'kicad design' 등의 요청에 자동 적용. STM32, FPGA(Xilinx/Intel), EtherCAT 슬레이브, IO 보드, 전원부, PHY/트랜시버 등 모든 하드웨어 도메인을 지원."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# KiCad 회로도 설계 — PRD/설계사양서 기반 생성

> 이 스킬은 HW PRD(Product Requirements Document), 설계사양서, 블록다이어그램 등을
> 입력받아 KiCad 9.x 형식의 회로도(.kicad_sch)를 생성합니다.
> 생성된 회로도는 `kicad-review` 스킬로 바로 검증할 수 있습니다.

## 워크플로우 개요

```
[1] 입력 분석 — PRD/설계사양서에서 요구사항 추출
 ↓
[2] 아키텍처 설계 — 블록다이어그램, IC 선정, 전원 트리
 ↓
[3] 데이터시트 수집 — 선정된 IC의 데이터시트 웹 검색
 ↓
[4] 회로도 생성 — KiCad S-expression 형식 .kicad_sch 파일 작성
 ↓
[5] 자동 리뷰 — kicad-review 스킬로 생성된 회로도 검증
```

---

## 단계 1: 입력 분석

사용자가 제공하는 입력 유형별 처리:

| 입력 유형 | 추출 내용 |
|-----------|----------|
| HW PRD 문서 | 기능 요구사항, 인터페이스 목록, 성능 사양, 전원 요구 |
| 설계사양서 | 구체적 IC 지정, 핀 할당, 전원 레일, 통신 프로토콜 |
| 블록다이어그램 | 모듈 구성, 인터페이스 연결, 신호 흐름 |
| 기존 회로도 수정 요청 | 변경 범위, 추가/삭제 부품 |
| 구두 설명 | 기능 의도, 대상 도메인 |

### 요구사항 정리 템플릿

분석 결과를 아래 형식으로 정리한 뒤 사용자 확인을 받는다:

```markdown
## 회로 설계 요구사항 정리

### 핵심 기능
- {기능 1}
- {기능 2}

### 주요 IC 후보
| 기능 | IC 후보 | 패키지 | 비고 |
|------|---------|--------|------|
| MCU | STM32F407VGT6 | LQFP-100 | 사용자 지정 |
| PHY | DP83848CVV | LQFP-48 | 선정 필요 |

### 인터페이스
- SPI x1 (Flash)
- I2C x1 (센서)
- UART x1 (디버그)
- Ethernet RMII x2

### 전원 요구
- 입력: +5V (USB) 또는 +3.3V
- 레일: 3.3V, 1.8V, 1.0V
- 최대 전류: {추정치}

### 커넥터
- {커넥터 목록}

### 제약사항
- PCB 크기, 레이어 수, 환경 조건 등
```

**반드시 사용자 확인을 받은 후** 다음 단계로 진행한다.

---

## 단계 2: 아키텍처 설계

### IC 선정

사용자가 IC를 지정하지 않은 경우, 요구사항에 맞는 IC를 제안한다:

- **MCU**: 요구 페리페럴, 핀 수, Flash/RAM, 패키지 기준
- **FPGA**: 로직 셀 수, IO 수, GT 트랜시버, 메모리 블록 기준
- **전원 IC**: 입출력 전압, 전류 용량, 효율, 패키지 기준
- **PHY/트랜시버**: 인터페이스 표준, 속도, 모드 기준

### 전원 트리

입력 전원에서 각 레일까지의 변환 경로를 설계한다:

```
+5V (USB)
 ├─ [Buck: TPS62130] → +1.0V VCCINT (3A)
 ├─ [Buck: TPS62160] → +1.8V VCCAUX (1A)
 ├─ [LDO: TPS7A4101] → +1.0V MGTAVCC (0.35A)
 └─ [LDO: TPS7A4101] → +1.2V MGTAVTT (0.08A)
```

### 계층 구조 설계

복잡한 회로는 서브시트로 분리한다:

```
root.kicad_sch (루트 — 서브시트 연결)
 ├── power.kicad_sch (전원부)
 ├── mcu.kicad_sch 또는 fpga.kicad_sch (메인 IC)
 ├── interface.kicad_sch (통신 인터페이스)
 ├── connector.kicad_sch (커넥터)
 └── peripheral.kicad_sch (주변 회로)
```

---

## 단계 3: 데이터시트 수집

선정된 IC별로 데이터시트를 웹 검색하여 다음을 확보한다:

- **핀 배치** (Pin Configuration / Pin Assignment) — 회로도 심볼 생성에 필수
- **권장 회로** (Typical Application) — 외부 부품 값과 연결 구조
- **전기적 특성** (Electrical Characteristics) — 전원 레일 전압/전류
- **패키지 정보** — 풋프린트 선택

검색 전략은 `../kicad-review/references/datasheet-lookup.md`를 참조한다.

---

## 단계 4: 회로도 생성

KiCad 9.x의 `.kicad_sch` S-expression 형식으로 회로도를 생성한다.
상세 생성 규칙은 `references/kicad-schematic-format.md`를 참조한다.

### 생성 원칙

1. **데이터시트 권장 회로 준수**: IC의 Application Circuit을 기반으로 설계한다
2. **디커플링 캡 필수**: 모든 IC의 VCC 핀에 100nF 세라믹 캡 배치
3. **풀업/풀다운 적용**: I2C에 4.7kΩ 풀업, BOOT/RESET에 풀다운/풀업
4. **네트 이름 규칙**: 대문자 + 언더스코어 (예: `SPI1_CLK`, `UART_TX`, `+3V3`)
5. **Reference 규칙**: IC는 U1~, 캡은 C1~, 저항은 R1~, 커넥터는 J1~
6. **계층 구조**: 기능 블록별 서브시트 분리
7. **전원 심볼**: `power:+3V3`, `power:GND` 등 KiCad 표준 전원 심볼 사용

### 파일 생성 순서

1. **라이브러리 심볼 정의** (`lib_symbols`) — 사용할 모든 부품의 핀 정의
2. **부품 배치** (`symbol`) — 좌표, Reference, Value, Footprint
3. **와이어 연결** (`wire`) — 핀 간 전선
4. **네트 레이블** (`label`, `global_label`) — 네트 이름
5. **전원 심볼** — VCC, GND 심볼 배치
6. **서브시트 참조** (`sheet`) — 계층 구조인 경우

### 라이브러리 사용 우선순위

반드시 아래 우선순위에 따라 심볼과 풋프린트를 선택한다. 상위 소스에서 찾으면 하위는 사용하지 않는다.

**우선순위 1: KiCad 기본 라이브러리 (필수 우선)**

저항, 캐패시터, 인덕터 등 수동 소자와 범용 부품은 반드시 KiCad 기본 라이브러리를 사용한다:

| 카테고리 | 심볼 라이브러리 | 풋프린트 라이브러리 | 예시 |
|----------|---------------|-------------------|------|
| 전원 심볼 | `power` | - | `+3V3`, `GND`, `+5V` |
| 저항 | `Device:R` | `Resistor_SMD:R_0402_*` | 10kΩ, 4.7kΩ |
| 캐패시터 | `Device:C` | `Capacitor_SMD:C_0402_*` | 100nF, 10μF |
| 인덕터 | `Device:L` | `Inductor_SMD:L_*` | 1.0μH, 2.2μH |
| LED | `Device:LED` | `LED_SMD:LED_0402_*` | - |
| 다이오드 | `Device:D` | `Diode_SMD:D_*` | - |
| 페라이트 비드 | `Device:FerriteBead` | `Inductor_SMD:L_0402_*` | 600Ω@100MHz |
| 퓨즈 | `Device:Polyfuse` | `Fuse:Fuse_1206_*` | 3A PTC |
| 크리스탈 | `Device:Crystal` | `Crystal:Crystal_SMD_*` | 8MHz, 25MHz |
| 커넥터 | `Connector_Generic` | `Connector_*` | `Conn_01x04` |
| MCU | `MCU_ST_STM32` | `Package_QFP:LQFP-*` | `STM32F407VGTx` |
| Flash | `Memory_Flash` | `Package_SO:SOIC-8_*` | `W25Q128JVS` |

**우선순위 2: 제조사 공식 라이브러리**

KiCad 기본 라이브러리에 없는 IC는 제조사가 제공하는 KiCad 라이브러리를 검색하여 사용한다:

| 소스 | 검색 방법 |
|------|----------|
| SnapEDA | `"{파트넘버} kicad site:snapeda.com"` |
| Ultra Librarian | `"{파트넘버} kicad site:ultralibrarian.com"` |
| Component Search Engine | `"{파트넘버} kicad site:componentsearchengine.com"` |
| 제조사 공식 | TI, ST, Microchip 등 공식 사이트 |

**우선순위 3: 커스텀 심볼 (최후 수단)**

위 두 소스에서 찾을 수 없는 경우에만 데이터시트의 핀 배치를 기반으로 커스텀 심볼을 `lib_symbols`에 정의한다. 커스텀 심볼 생성 시 반드시 데이터시트의 핀 번호, 이름, 타입을 정확히 반영한다.

### 연결 전략: 네트 레이블 우선

S-expression으로 회로도를 생성할 때 **직접 와이어 연결보다 네트 레이블(`label`, `global_label`)을 우선 사용**한다.

직접 와이어는 양 끝점 좌표가 핀의 절대 좌표와 mm 단위로 정확히 일치해야 전기적 연결이 성립한다. 이 정밀도를 보장하기 어려우므로, 다음 전략을 따른다:

| 연결 방식 | 사용 시점 | 좌표 정밀도 요구 |
|-----------|----------|----------------|
| `global_label` | 서브시트 간 연결, 전원 레일 | 낮음 (레이블만 배치) |
| `label` | 같은 시트 내 IC 간 연결 | 낮음 (레이블만 배치) |
| `wire` | 부품과 인접 레이블/전원 심볼 연결 (짧은 거리) | 높음 |

**권장 패턴**:
- IC의 각 핀에 짧은 와이어(1~2 그리드) + 네트 레이블을 붙인다
- IC 간 연결은 같은 이름의 레이블로 암묵적 연결한다
- 전원은 `power:+3V3`, `power:GND` 심볼을 핀 근처에 배치한다

이 방식은 좌표 정밀도 부담을 줄이면서 KiCad에서 정상적으로 네트를 인식한다.

### 생성 후 KiCad GUI 보정

생성된 `.kicad_sch` 파일은 KiCad GUI에서 열어 다음을 보정한다:

1. **ERC 실행** → 미연결 핀/와이어 확인
2. **와이어 끝점 스냅** → 핀에 정확히 연결되도록 드래그
3. **레이아웃 정리** → 부품 간격, 텍스트 겹침 조정

이 보정 작업은 보통 5~15분이면 완료된다. 생성된 회로도의 가치는 **부품 선정, 회로 구조, 네트 정의, 디커플링/바이패스 설계**에 있으며, 와이어 좌표는 GUI에서 마무리하는 것이 가장 효율적이다.

### S-expression 기본 구조

```lisp
(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "{UUID}")
  (paper "A3")
  (title_block
    (title "{프로젝트명}")
    (date "{날짜}")
    (rev "{리비전}")
    (company "{회사명}")
    (comment 1 "{설명}")
  )
  (lib_symbols
    ;; 사용할 모든 심볼의 핀 정의
  )
  ;; 부품 인스턴스, 와이어, 레이블 등
)
```

### UUID 생성

모든 요소에 고유 UUID가 필요하다:

```python
import uuid
new_uuid = str(uuid.uuid4())
```

### .kicad_pro 프로젝트 파일 생성

회로도와 함께 `.kicad_pro` 프로젝트 파일을 반드시 생성한다.
파일명은 루트 `.kicad_sch`와 동일하게 맞춘다 (예: `project.kicad_sch` → `project.kicad_pro`).

포맷과 템플릿은 `references/kicad-schematic-format.md`의 ".kicad_pro 프로젝트 파일" 섹션을 참조한다.

---

## 단계 5: 리뷰 및 보정

회로도 생성 완료 후 `kicad-review` 스킬을 트리거하여 생성된 회로도를 검증한다.

검증 항목:
- 전원 설계 완전성
- 핀 연결 누락
- 데이터시트 권장 회로 준수 여부
- BOM 정합성

### 리뷰 결과 처리

리뷰 보고서에서 ERROR가 발견되면 사용자에게 수정 사항을 제시한다:

1. **ERROR 목록 제시**: 각 ERROR의 위치, 원인, 구체적 수정 방법을 보고
2. **사용자 확인 후 수정**: 사용자가 수정을 승인하면 해당 `.kicad_sch` 파일을 편집
3. **재검증**: 수정 후 다시 리뷰를 실행하여 ERROR=0 확인

자동으로 회로도를 수정하지 않는다. 회로 변경은 사용자 판단이 필요하기 때문이다(예: FB 저항값 변경은 출력 전압에 직접 영향).

### KiCad GUI 보정 안내

리뷰 완료 후 사용자에게 안내한다:
- "KiCad에서 열어 ERC를 실행하고, 미연결 와이어를 보정하세요 (5~15분)"
- `/kicad-review`로 추가 리뷰도 가능합니다

---

## 에이전트 위임

실제 회로도 생성 작업은 **kicad-schematic-designer** 에이전트에게 위임한다.
에이전트는 `kicad-setup` 스킬로 타겟 프로젝트의 `.claude/agents/`에 설치한다.

---

## 사용 예시

```
사용자: "이 PRD 기반으로 KiCad 회로도 만들어줘"
사용자: "STM32F407 + Ethernet PHY 2포트 보드 설계해줘"
사용자: "이 블록다이어그램을 KiCad 회로도로 변환해줘"
사용자: "M.2 폼팩터의 FPGA 카드 회로도 생성해줘"
사용자: "EtherCAT 슬레이브 IO 보드 회로 설계"
```

$ARGUMENTS
