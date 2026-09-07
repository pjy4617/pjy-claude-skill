---
name: kicad-design
description: "HW PRD, 설계사양서, 블록다이어그램을 입력받아 KiCad 회로도(.kicad_sch)를 생성합니다. 'KiCad 회로도 만들어', '회로도 설계', '회로 생성', 'schematic design', 'PRD 기반 회로도', '설계사양서로 회로 만들어', '블록다이어그램 회로도 변환', '보드 설계', 'KiCad 스키매틱 생성', 'kicad design' 등의 요청에 자동 적용. STM32, FPGA(Xilinx/Intel), EtherCAT 슬레이브, IO 보드, 전원부, PHY/트랜시버 등 모든 하드웨어 도메인을 지원."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# KiCad 회로도 설계 — PRD/설계사양서 기반 생성

> 이 스킬은 HW PRD(Product Requirements Document), 설계사양서, 블록다이어그램 등을
> 입력받아 KiCad 9.x 또는 10.x(대상 버전에 맞춤) 형식의 회로도(.kicad_sch)를 생성합니다.
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
[5] 자동 리뷰 — 메인 세션이 kicad-review 스킬로 생성된 회로도 검증
 ↓
[6] 보드 생성 (선택) — 회로도 → .kicad_pcb 로 풋프린트·넷을 올린다 (외곽·배치는 사용자)
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

**시작 전 KiCad 메이저 버전 확인**: `kicad-cli version`을 실행해 사용자의 KiCad 메이저 버전을 확인한다. KiCad 10은 9 파일을 열지만 9는 10 파일을 열지 못하므로, 어느 포맷으로 쓸지가 먼저 정해져야 한다.

- **9면**: 텍스트 생성 경로만 쓴다. 그리고 사용자에게 알린다 — KiCAD-MCP-Server의 편집 도구(`batch_add_and_connect` 등)로 파일을 한 번이라도 편집하면 파일이 KiCad 10 포맷(`version 20260101`)으로 다시 쓰이고, 그 순간부터 KiCad 9에서 그 회로도를 열 수 없게 된다.
- **10이면**: `references/kicad-schematic-format.md`의 `version`/`generator_version`을 `20260101` / `"10.0"`으로 맞춘다.

대상 버전의 `.kicad_sch` S-expression 형식으로 회로도를 생성한다.
상세 생성 규칙은 `references/kicad-schematic-format.md`를 참조한다.

### 생성 원칙

1. **데이터시트 권장 회로 준수**: IC의 Application Circuit을 기반으로 설계한다
2. **디커플링 캡 필수**: 모든 IC의 VCC 핀에 100nF 세라믹 캡 배치
3. **풀업/풀다운 적용**: I2C에 4.7kΩ 풀업, BOOT/RESET에 풀다운/풀업
4. **네트 이름 규칙**: 대문자 + 언더스코어 (예: `SPI1_CLK`, `UART_TX`, `+3V3`)
5. **Reference 규칙**: IC는 U1~, 캡은 C1~, 저항은 R1~, 커넥터는 J1~
6. **계층 구조**: 기능 블록별 서브시트 분리
7. **전원 심볼**: `power:+3V3`, `power:GND` 등 KiCad 표준 전원 심볼 사용
8. **PWR_FLAG**: 레일을 구동하는 `power_out` 핀이 없는 레일(커넥터로 들어오는 입력, 출력이 `passive`로 잡힌 벤더 심볼)에만 그 레일의 원천 시트에 `power:PWR_FLAG`를 정확히 1개 붙인다. 레귤레이터 등 `power_out` 핀이 이미 구동하는 레일에는 붙이지 않는다 — 붙이면 ERC가 `Power output and Power output are connected` 오류를 낸다

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
| MCU | `MCU_ST_STM32F4` (패밀리별 분리: F0/F1/F2/F3/F4/F7/G0/G4/H5/…) | `Package_QFP:LQFP-*` | `MCU_ST_STM32F4:STM32F407VGTx` |
| Flash | `Memory_Flash` | `Package_SO:SOIC-8_*` | `W25Q128JVS` |

**라이브러리 실존 확인**: `lib_id`를 쓰기 전에 `search_symbols`(KiCAD-MCP-Server) 또는 `ls /usr/share/kicad/symbols | grep <이름>`으로 라이브러리 파일이 실제로 있는지 확인한다. 위 표의 이름도 KiCad 버전에 따라 달라질 수 있다.

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
| `global_label` | 서브시트 간 신호 연결 (전원은 전원 심볼로) | 낮음 (레이블만 배치) |
| `label` | 같은 시트 내 IC 간 연결 | 낮음 (레이블만 배치) |
| `wire` | 부품과 인접 레이블/전원 심볼 연결 (짧은 거리) | 높음 |

**권장 패턴**:
- IC의 각 핀에 짧은 와이어(1~2 그리드) + 네트 레이블을 붙인다
- IC 간 연결은 같은 이름의 레이블로 암묵적 연결한다
- 전원은 `power:+3V3`, `power:GND` 심볼을 핀 근처에 배치한다. 전원 심볼 자체가 전역 넷이므로 전원에는 글로벌 레이블도 시트 핀도 만들지 않는다

이 방식은 좌표 정밀도 부담을 줄이면서 KiCad에서 정상적으로 네트를 인식한다.

### 생성 후 KiCad GUI 보정

생성된 `.kicad_sch` 파일은 KiCad GUI에서 열어 다음을 보정한다:

1. **ERC 실행** → 미연결 핀/와이어 확인
2. **와이어 끝점 스냅** → 핀에 정확히 연결되도록 드래그
3. **레이아웃 정리** → 부품 간격, 텍스트 겹침 조정

**보정 시간은 핀 수에 비례한다.** 와이어 끝점을 손으로 드래그해 스냅하는 작업은 핀 하나당 한 번이므로,
30핀 IC 하나면 끝점이 30개다. 이 경로는 **부품 20개(핀 100개) 이하 초안에서만 실용적**이며,
그 이상은 MCP 저작 경로(`batch_add_and_connect` + `lint_offgrid`)를 쓴다.

생성된 회로도의 가치는 **부품 선정, 회로 구조, 네트 정의, 디커플링/바이패스 설계**에 있으며,
그 규모 안에서는 와이어 좌표를 GUI에서 마무리하는 것이 가장 효율적이다.

> **MCP 저작 경로는 후속 범위다.** KiCAD-MCP-Server 의 `batch_add_and_connect`(핀 끝점에 레이블을 정확히 스냅)로
> 시트를 통째로 만들고 `lint_offgrid` 로 오프그리드를 걷어내는 절차는 이 스킬에 아직 들어 있지 않다.
> 지금은 "부품이 많으면 텍스트 생성 경로의 GUI 보정이 감당이 안 된다" 는 한계만 알고, 회로를 시트로 쪼개
> 시트당 부품 수를 20개 아래로 유지한다.

### S-expression 기본 구조

```lisp
(kicad_sch
  (version 20250114)          ;; KiCad 9: 20250114 / KiCad 10: 20260101
  (generator "eeschema")
  (generator_version "9.0")   ;; KiCad 10이면 "10.0"
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

넷클래스를 넣을 때는 클래스 정의(`net_settings.classes`)와 넷 배정(`net_settings.netclass_patterns`)을 한 쌍으로 쓴다. 정의만 하고 배정하지 않으면 DRC가 그 넷을 `Default` 폭으로 검사한다.

---

## 단계 5: 리뷰 및 보정

**호출 주체는 메인 세션이다.** 회로도 생성이 끝나 kicad-schematic-designer 에이전트가 결과를 돌려주면,
그때 **메인 세션이** `kicad-review` 스킬을 호출해 생성된 회로도를 검증한다.
서브에이전트는 스킬을 부르지 않는다 — 에이전트 안에서 "kicad-review 를 트리거" 하는 일은 일어나지 않으므로,
에이전트의 산출물을 받은 뒤 이 단계를 **메인 세션에서 직접 실행**한다.

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
- "KiCad에서 열어 ERC를 실행하고, 미연결 와이어를 보정하세요" — 소요 시간은 핀 수에 비례한다(단계 4 "생성 후 KiCad GUI 보정" 참조)
- `/kicad-review`로 추가 리뷰도 가능합니다

---

## 단계 6 (선택): 보드 생성

회로도의 풋프린트와 넷을 `.kicad_pcb` 에 올리는 것까지만 한다 — KiCad GUI 의 Tools → Update PCB from Schematic(F8)에
해당하며, **kicad-cli 에는 이 명령이 없다**. KiCAD-MCP-Server 가 유일한 무 GUI 경로다. 선택 단계이므로 **사용자가 요청했을 때만** 수행한다.

**이 단계가 하지 않는 것**: 보드 외곽(테두리)과 부품 배치. 외곽은 기구 치수·마운팅 홀·커넥터 위치 같은
회로도에 없는 정보로 정해지고, 배치는 열·노이즈·조립성을 보는 설계 판단이다. 둘 다 사용자가 KiCad GUI 에서 한다.
이 스킬은 배치 도구(`hierarchical_place` 등)를 호출하지 않는다 — 원점에 겹쳐 올라온 풋프린트를 사용자가 옮기는 것이 정상 상태다.

### 전제 (하나라도 못 채우면 건너뛴다)

전제는 아래 표의 순서로 확인한다. **첫 두 전제(풋프린트 해석과 ERC)는 서로를 대신하지 못한다 — 각각 따로 확인한다.**

| 전제 | 확인 방법 | 못 채웠을 때 |
|------|----------|-------------|
| 모든 `Footprint` 필드가 fp-lib-table 에서 풀리고 **실제로 로드됨** | 아래 (가) 정적 검사 + (나) 로드 검사를 **둘 다** 통과 (kicad-review 의 풋프린트 해석 검사와 같은 판정) | 미해석 nickname·로드 실패 라이브러리를 먼저 해결한다 |
| ERC 0 errors | `kicad-cli sch erc --format json --severity-all` → `severity == "error"` 0건 | 회로도를 먼저 고친다 |
| KiCAD-MCP-Server 등록 + pcbnew 가용 | `mcp__kicad__get_backend_state` 로 `backend` 응답 확인 | GUI 에서 F8 을 직접 실행하도록 안내 |
| **프로젝트 파일**이 KiCad 10 세대 | 보드/회로도 파일의 `(generator_version ...)` 을 읽는다 — 아래 (다) | **"9.x" 면 건너뛴다** — MCP 편집 도구가 파일을 10 포맷으로 다시 쓰면 9 에서 열 수 없게 된다 |
| KiCad GUI 에서 대상 프로젝트가 닫혀 있음 | 사용자에게 확인 | 닫은 뒤 진행 |

**ERC 전제는 풋프린트 전제를 못 잡는다.** 풋프린트 미해석은 KiCad ERC 에서 error 가 아니라
**warning** (`footprint_link_issues`) 으로 나오기 때문이다. "0 errors" 만 보면 미해석이 수십 건 있어도
ERC 전제는 그대로 통과한다 — 실측 사례에서 `error 0 / warning 25` 였고 그중 24건이 `footprint_link_issues` 였다.
표에서 풋프린트 전제를 먼저 둔 이유가 이것이다. 보드 생성을 실제로 망가뜨리는 쪽을 먼저 본다.

풋프린트 해석이 왜 게이트인가: `create_board_from_schematic` 은 회로도의 풋프린트를 **보드에 직접 추가**한다.
fp-lib-table 에서 풀리지 않는 풋프린트는 추가되지 않고 응답의 `skipped` 로 돌아온다.
이 게이트를 건너뛰면 "보드는 만들어졌는데 부품이 절반만 있는" 상태가 된다.

확인 명령:

```
(가) 정적 검사 — nickname 이 fp-lib-table 에 등록돼 있고 .kicad_mod 파일이 실제로 있는가.
     ERC 의 footprint_link_issues 목록도 함께 본다 (0건이어야 통과).

(나) 로드 검사 — 파일이 있어도 KiCad 가 못 읽는 라이브러리가 있다. 정적 검사로는 안 잡힌다.
     for d in <프로젝트>/libraries/*.pretty; do
       python3 -c "import pcbnew,os;pcbnew.FootprintEnumerate(os.path.abspath('$d'))" || echo "FAIL $d"
     done

(다) 프로젝트 세대 — 설치된 CLI 버전이 아니라 파일의 세대를 본다.
     grep -m1 -o '(generator_version "[^"]*")' <board>.kicad_pcb
     grep -m1 -o '(generator_version "[^"]*")' <root>.kicad_sch
     → "9.0" 이면 KiCad 9 프로젝트다. `kicad-cli version` 이 10.x 여도 건너뛴다.
       보드가 아직 없으면 회로도 쪽 값으로 판정한다.
       `.kicad_pro` 의 `meta.version`(예: 3)은 KiCad 세대가 아니라 파일 스키마 번호다 — 판정에 쓰지 않는다.
```

### 실행

```
[6-1] 보드가 없을 때
      mcp__kicad__create_board_from_schematic
        schematicPath: 루트 .kicad_sch 절대경로 (필수)
        boardPath:     생성할 .kicad_pcb 절대경로 (생략 시 회로도 옆)
        overwrite:     기존 파일이 있을 때만 true

[6-1b] 넷 커버리지 검증 (필수 — 생략하지 않는다)
      [6-1] 로 만들었을 때도 [6-2] 로 동기화했을 때도 똑같이 돌린다.
      회로도의 넷·핀 연결이 보드에 몇 개나 올라갔는지 세어 대조한다.
      kicad-cli sch export netlist --format kicadsexpr -o <tmp>/sch.net <root.kicad_sch>
      세는 방법과 판정 기준은 아래 "넷 커버리지 검증 (6-1b)" 절에 있다.
      손실이 있으면 손실 넷 수와 목록을 [6-3] 보고에 그대로 싣는다.

[6-2] 보드가 이미 있을 때
      mcp__kicad__sync_schematic_to_board
        schematicPath / boardPath 둘 다 절대경로 (필수)
      → 기존 배치·배선을 유지한 채 회로도 변경분만 반영한다

[6-3] 사용자에게 넘긴다
      "풋프린트 {n}/{m}개(skipped {k}개: ...),
       넷 {p}/{q}개 — 손실 {r}개({s}%), 넷이 배정된 패드 {u}/{v}개가 보드에 올라갔습니다.
       손실 넷: {목록}
       다음은 KiCad GUI 에서:
       1) 보드 외곽 — Edge.Cuts 에 기구 치수대로 테두리, 마운팅 홀, 커넥터 위치
       2) 배치 — 커넥터/기구 고정 부품부터, 그다음 IC 와 디커플링, 마지막에 수동 소자
       3) 배선
       배치가 끝나면 /kicad-analyze 로 배치 검토(에어와이어 길이·디커플링 거리·코트야드 겹침)를 받을 수 있습니다."
```

### 넷 커버리지 검증 (6-1b)

`create_board_from_schematic` 은 **라벨이 붙은 넷만** 보드에 올린다. 배선만으로 이어져 KiCad 가
`Net-(C1-Pad2)` 처럼 자동으로 이름을 지어 준 **로컬 넷은 통째로 빠진다.** 부품은 다 올라와 있어서
파일만 보면 정상으로 보이고, 러츠네스트(연결선)만 조용히 사라진다. 그래서 세어 봐야 한다.

세는 법 — 회로도 넷리스트와 보드 파일을 직접 대조한다.

```
kicad-cli sch export netlist --format kicadsexpr -o <tmp>/sch.net <root.kicad_sch>

python3 - "<tmp>/sch.net" "<board>.kicad_pcb" <<'EOF'
import re, sys
L = open(sys.argv[1], encoding='utf-8').read().splitlines()
i = next(k for k, l in enumerate(L) if l.strip() == '(nets')
names, nodes, cur = [], [], 0
for l in L[i+1:]:
    s = l.strip()
    if s == '(net':
        if names: nodes.append(cur)
        cur = 0; names.append(None)
    elif names and names[-1] is None and s.startswith('(name "'):
        names[-1] = re.match(r'\(name "(.*)"\)', s).group(1)
    elif s == '(node': cur += 1
nodes.append(cur)
real = [(n, c) for n, c in zip(names, nodes) if not n.startswith('unconnected-')]
T = open(sys.argv[2], encoding='utf-8').read()
head, _, body = T.partition('\n\t(footprint ')
tab = set(re.findall(r'\(net\s+\d+\s+"([^"]*)"\)', head)) - {''}
pad = [x for x in re.findall(r'\(net\s+(?:\d+\s+)?"([^"]*)"\)', body) if x]
bn = tab if tab else set(pad)
lost = sorted(set(n for n, _ in real) - bn)
print("회로도 실넷 %d / 실핀연결 %d" % (len(real), sum(c for _, c in real)))
print("보드   넷 %d / 패드배정 %d" % (len(bn), len(pad)))
print("손실 넷 %d (%.1f%%)" % (len(real) - len(bn), (len(real) - len(bn)) * 100.0 / len(real)))
print("손실 목록:", lost)
EOF
```

세는 대상 정의 — 위 스크립트가 하는 일을 말로 옮기면 이렇다.

| 값 | 무엇을 세는가 |
|----|--------------|
| 회로도 실넷 | 넷리스트의 넷 중 이름이 `unconnected-` 로 시작하지 않는 것. `unconnected-` 는 1핀짜리 미연결 표시라 보드 넷이 아니다 |
| 회로도 실핀연결 | 그 실넷들에 달린 `(node ...)` 의 수 |
| 보드 넷 | `.kicad_pcb` 의 넷 이름 종류 수. 상단 넷 테이블이 있으면 거기서, 없으면 패드에 쓰인 이름에서 센다 |
| 보드 패드배정 | 풋프린트 블록 안의 `(net ...)` 참조 수 |

판정 기준

| 손실률 (손실 넷 ÷ 회로도 실넷) | 판단 |
|------|------|
| 0% | 그대로 진행한다 |
| 5% 이하 | 손실 넷 목록을 보고하고, 사용자가 GUI 에서 그 넷만 보정하도록 안내한다 |
| **5% 초과** | **이 보드를 쓰지 않는다.** 생성한 보드를 버리고, KiCad GUI 에서 프로젝트를 연 뒤 Tools → Update PCB from Schematic(**F8**)으로 다시 올리도록 안내한다. F8 은 자동명 넷도 함께 올린다 |

이 절차를 실측 회로도(371 부품·계층 시트 8장)에 돌린 결과는 이렇다.

```
회로도 실넷 247 / 실핀연결 1212
보드   넷 161 / 패드배정 906
손실 넷 86 (34.8%)
손실 목록: /FPGA1/MODE0, /FPGA1/MODE1, /FPGA1/MODE2, Net-(C1-Pad2), Net-(C4-Pad2), ... (총 92개 이름)
```

손실 넷 86개는 손실률 34.8% 로 5% 기준을 크게 넘는다 — 이 보드는 넘기지 않고 F8 로 안내해야 하는 사례다.
핀 연결도 1212개 중 906개만 배정돼 306개가 빠졌다. 이름 대조로는 92개가 안 맞는데
(자동명 89개 + 계층 경로가 다르게 붙은 3개), 개수 차이 86개와 값이 다른 것은 보드 쪽에 계층 경로가
벗겨진 이름(`MODE0` 등)이 따로 잡히기 때문이다. **보고에는 개수 기준(86)과 목록을 함께 적는다.**

주의: 이 대조는 **방금 생성한 보드**에만 의미가 있다. 이미 배선까지 끝난 기존 보드는 회로도와 개정 차이가
있어 보드 넷이 회로도보다 많게 나올 수 있고, 그때 이 수치는 손실이 아니라 동기화 차이를 뜻한다
(그 확인은 `kicad-analyze` 의 회로도-보드 동기화 검사가 담당한다).

### 주의

- **보드 파일을 덮어쓴다.** `create_board_from_schematic` 은 `overwrite: true` 일 때 기존 `.kicad_pcb` 를 **통째로 대체**한다 —
  배치·배선이 들어 있는 보드에는 절대 쓰지 않는다. 기존 보드가 있으면 **`sync_schematic_to_board` 를 쓴다.**
  둘 다 디스크의 `.kicad_pcb` 를 읽고 다시 쓰므로 **GUI 에서 그 보드가 닫힌 상태**에서만 실행한다.
- **타임아웃이 도구마다 다르다.** 서버의 기본 명령 예산은 30초이고 600초 목록에 있는 것은 `sync_schematic_to_board` 뿐이다.
  `create_board_from_schematic` 은 **30초 예산**으로 돈다 — 부품이 많은 회로도에서 타임아웃이 나면
  빈 보드를 만든 뒤 `sync_schematic_to_board`(600초)로 나눠 넣는다.
- **`skipped` 를 반드시 리포트한다.** 응답의 `skipped` 목록(해석 실패 풋프린트)을 사용자에게 그대로 보여 주고,
  몇 개 중 몇 개가 올라갔는지 수로 적는다. "보드 생성 완료" 만 적지 않는다.
- **`skipped` 의 흔한 진짜 원인은 `.kicad_mod` 의 `(version ...)` 헤더 누락이다.** 헤더가 없으면 KiCad 가
  그 파일을 레거시 포맷 파서로 읽는데, 본문이 최신 문법(`fp_arc` 의 `(start)(mid)(end)`)이면 `(mid ...)` 에서
  파싱이 죽어 라이브러리 전체가 로드 실패한다. 응답의 `skipped` 사유 문구로는 이게 안 보이므로
  전제 확인의 (나) 로드 검사로 잡고, 해당 `.kicad_mod` 첫 줄 뒤에 `(version ...)`·`(generator ...)` 두 줄을 넣어 고친다.
- **넷 손실을 반드시 확인하고 보고한다.** 풋프린트 수만 맞아도 넷은 3분의 1이 빠져 있을 수 있다.
  [6-1b] 를 건너뛰지 말고, 위 "넷 커버리지 검증 (6-1b)" 절의 판정 기준대로 보고·중단 여부를 정한다.

### 이후 흐름

이 단계의 산출물은 **풋프린트와 넷만 올라간 보드**다. 외곽·배치·배선은 사용자가 KiCad GUI 에서 한다.

- 배치가 끝난 시점 → `kicad-analyze` 4.1 배치 검토(에어와이어 길이·디커플링/크리스탈 거리·코트야드 겹침)
- 배선이 끝난 시점 → `kicad-analyze` 전체(동기화 확인·DRC·SI/PI)
- 거버·드릴·위치 파일 등 제조 출력 → `kicad-fabricate`

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
