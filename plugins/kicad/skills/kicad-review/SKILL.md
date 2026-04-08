---
name: kicad-review
description: "KiCad 회로도(.kicad_sch)를 분석하여 설계 리뷰, 데이터시트 비교 검증, BOM(파트리스트) 마크다운 생성을 수행합니다. 'KiCad 회로도 리뷰', '회로도 검토', '회로 리뷰', 'schematic review', '회로도 분석', '파트리스트 만들어', 'BOM 생성', '부품 목록', '회로도에서 문제 찾아', '데이터시트 비교', '회로 검증', 'KiCad BOM', '회로도 체크' 등의 요청에 자동 적용. STM32, FPGA(Xilinx/Intel), EtherCAT 슬레이브, IO 보드, 전원부, PHY/트랜시버 등 모든 하드웨어 도메인을 지원하는 범용 회로도 리뷰 도구."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# KiCad 범용 회로도 리뷰 + BOM 생성

> 이 스킬은 KiCad 회로도 파일을 파싱하여 설계 오류를 검출하고,
> 사용된 소자의 데이터시트를 웹에서 검색해 권장 회로와 비교 검증한 뒤,
> 마크다운 형식의 BOM(파트리스트)을 생성합니다.

## 워크플로우 개요

```
[1] KiCad 파일 탐색 및 구조 파악
 ↓
[2] 회로도 파싱 — 부품, 핀, 네트, 값 추출
 ↓
[3] PDF 시각적 검토 — 와이어 연결, 부품 겹침, 레이아웃 이상 감지
 ↓
[4] 제조사 공식 라이브러리 비교 — 핀 번호/이름/풋프린트 정합성 검증
 ↓
[5] 설계 리뷰 — 범용 체크리스트 적용
 ↓
[6] 데이터시트 비교 — 웹 검색으로 주요 IC의 권장 회로 대조
 ↓
[7] BOM 마크다운 생성
 ↓
[8] 종합 리뷰 보고서 출력
```

---

## 단계 1: KiCad 프로젝트 탐색

```bash
# 프로젝트 파일 탐색
find "$TARGET_DIR" -name "*.kicad_pro" -o -name "*.kicad_sch" | sort

# kicad-cli 버전 확인
kicad-cli --version 2>/dev/null || echo "kicad-cli 없음 — 직접 파싱 모드"
```

**계층 구조 파악**: 루트 `.kicad_sch`에서 `(sheet ... (property "Sheetfile" "xxx.kicad_sch"))` 를 찾아 서브시트 계층을 파악한다.

---

## 단계 2: 회로도 파싱

KiCad 9.x의 `.kicad_sch`는 S-expression 형식이다. 파싱 방법은 `references/kicad-parser.md`를 참조한다.

### 추출 대상

| 항목 | S-expression 경로 | 예시 |
|------|-------------------|------|
| 부품 | `(symbol (lib_id "...") (property "Reference" "U1") (property "Value" "XC7A200T"))` | U1, C1, R1 |
| 핀 연결 | `(wire ...)` + `(label ...)` + `(global_label ...)` | NET_SPI_CLK |
| 값 | `(property "Value" "100nF")` | 저항값, 캡 값 |
| 풋프린트 | `(property "Footprint" "Package_QFP:LQFP-100...")` | 패키지 정보 |
| 데이터시트 | `(property "Datasheet" "https://...")` | 제조사 링크 |

### 파싱 스크립트

```bash
# kicad-cli로 넷리스트 추출 (가용 시)
kicad-cli sch export netlist \
  --output /tmp/netlist.xml \
  --format kicadxml \
  "$ROOT_SCH"

# 넷리스트에서 부품 목록 추출
python3 << 'PYEOF'
import xml.etree.ElementTree as ET

tree = ET.parse('/tmp/netlist.xml')
root = tree.getroot()

components = []
for comp in root.findall('.//comp'):
    ref = comp.get('ref', '')
    value = comp.findtext('value', '')
    footprint = comp.findtext('footprint', '')
    datasheet = comp.findtext('datasheet', '')
    fields = {}
    for f in comp.findall('.//field'):
        fields[f.get('name', '')] = f.text or ''
    components.append({
        'ref': ref, 'value': value,
        'footprint': footprint, 'datasheet': datasheet,
        'fields': fields
    })
    print(f"{ref:>8} | {value:<25} | {footprint}")

print(f"\n총 {len(components)}개 부품")
PYEOF
```

kicad-cli가 없으면 `.kicad_sch` 파일을 직접 파싱한다 — `references/kicad-parser.md`의 "직접 파싱" 섹션 참조.

---

## 단계 3: PDF 시각적 검토

텍스트 파싱만으로는 감지하기 어려운 시각적 오류를 잡아내기 위해, 회로도를 PDF로 내보내서 멀티모달 분석을 수행한다.

### PDF 내보내기

```bash
# kicad-cli로 PDF 내보내기 (모든 시트가 한 파일에 페이지별로 포함)
kicad-cli sch export pdf \
  --output /tmp/schematic_review.pdf \
  "$ROOT_SCH"
```

kicad-cli가 없으면 이 단계를 건너뛴다 (보고서에 "시각적 검토 미수행" 명시).

### PDF 분석

내보낸 PDF를 `Read` 도구로 시트(페이지)별로 읽으며 다음을 검토한다:

| ID | 검토 항목 | 문제 사례 |
|----|----------|----------|
| V1 | **와이어 연결 누락** — 교차하는 와이어에 junction(접합점) 마커가 없으면 실제로는 미연결 | 시각적으로 연결된 것 같지만 전기적 미연결 |
| V2 | **부품/텍스트 겹침** — 심볼, 레이블, 값 텍스트가 서로 겹쳐 가독성 저하 | Reference와 Value가 부품 위에 겹침 |
| V3 | **네트 레이블 위치** — 와이어 끝에 정확히 붙지 않은 레이블 (시각적 연결이지만 실제 미연결) | 레이블이 와이어에서 미세하게 떨어져 있음 |
| V4 | **전원 심볼 배치** — VCC/GND 심볼이 와이어에 올바르게 연결되었는지 | 전원 심볼이 떠 있거나 잘못된 네트에 연결 |
| V5 | **신호 흐름 가독성** — 입력이 왼쪽, 출력이 오른쪽 관례 준수 | 신호 방향이 혼란스러운 배치 |
| V6 | **시트 간 연결 일관성** — 계층 핀/글로벌 레이블의 시각적 정합 | 서브시트 핀 이름과 상위 시트 연결 불일치 |
| V7 | **미배선 영역** — 끊어진 와이어, 미완성 연결 | 와이어가 허공에서 끝남 |

### 시트별 분석 방법

```python
# PDF를 시트별로 읽어 분석
# 예: 6개 서브시트를 가진 프로젝트
for page in range(1, total_pages + 1):
    # Read 도구로 해당 페이지 읽기 (pages 파라미터 사용)
    # 시각적 이상 항목을 V1~V7 기준으로 검토
    pass
```

### 판정 기준

- **ERROR**: V1(junction 누락으로 실제 미연결), V3(레이블 미연결), V7(미배선)
- **WARN**: V2(겹침), V4(전원 배치), V5(가독성), V6(일관성)

---

## 단계 4: 제조사 공식 라이브러리 비교

회로도에서 사용된 IC 심볼이 제조사 공식 KiCad 라이브러리와 일치하는지 검증한다.
커스텀 심볼의 핀 번호/이름 오류는 가장 흔한 하드웨어 버그 중 하나이며, 공식 라이브러리와 비교하면 원천 차단할 수 있다.

### 라이브러리 검색 소스

| 우선순위 | 소스 | 검색 방법 | 비고 |
|---------|------|----------|------|
| 1 | KiCad 공식 라이브러리 | `kicad-cli sym export` 또는 로컬 라이브러리 경로 | 기본 내장 심볼 |
| 2 | SnapEDA | `snapeda.com/parts/{파트넘버}/kicad` 웹 검색 | 가장 넓은 커버리지 |
| 3 | Ultra Librarian | `ultralibrarian.com/search?q={파트넘버}` 웹 검색 | TI 부품 특히 강함 |
| 4 | Component Search Engine | `componentsearchengine.com` 웹 검색 | Samacsys 기반 |
| 5 | 제조사 공식 | ST, TI, Microchip 등 공식 사이트 | MCU/PHY 특화 |

### 검증 절차

1. **IC 목록 추출**: 회로도에서 IC(U 레퍼런스) 부품의 파트넘버를 수집한다
2. **공식 라이브러리 검색**: 각 파트넘버로 위 소스를 순서대로 검색한다

```
검색어 예시:
  "TPS62130 kicad symbol site:snapeda.com"
  "DP83848 kicad library site:ultralibrarian.com"
  "XC7A200T kicad symbol"
```

3. **핀 정의 비교**: 공식 라이브러리의 핀 정보와 회로도 심볼을 대조한다

| 비교 항목 | ERROR 조건 | WARN 조건 |
|-----------|-----------|-----------|
| 핀 번호 | 공식 라이브러리와 불일치 | - |
| 핀 이름 | - | 공식 라이브러리와 불일치 (기능은 동일) |
| 핀 타입 (입력/출력/전원) | 전원 핀이 I/O로 잘못 정의 | 입출력 방향 차이 |
| 풋프린트 | 패키지 불일치 | 패드 크기/간격 차이 |
| 핀 총 개수 | 핀 수 불일치 | - |

4. **결과 리포트 작성**:

```markdown
### 라이브러리 비교 결과

| IC | 파트넘버 | 공식 소스 | 핀 번호 | 핀 이름 | 풋프린트 | 판정 |
|----|---------|----------|---------|---------|---------|------|
| U1 | TPS62130 | SnapEDA | ✓ 일치 | ✓ 일치 | ✓ 일치 | OK |
| U2 | DP83848 | Ultra Librarian | ✗ Pin 24 불일치 | ⚠ RXD0→RX_D0 | ✓ 일치 | ERROR |

[불일치 상세]
  🔴 U2 (DP83848) Pin 24:
     회로도 심볼: Pin 24 = COL (출력)
     공식 라이브러리: Pin 24 = LED_CFG (입력)
     → 핀 기능이 완전히 다름. 회로도 심볼 교체 필요.

[공식 라이브러리 다운로드 링크]
  - TPS62130: https://snapeda.com/parts/TPS62130/...
  - DP83848: https://ultralibrarian.com/...
```

### 자동 대체가 아닌 비교 검증인 이유

공식 라이브러리로 자동 대체하면 심볼의 핀 배치(좌/우/상/하 위치)가 달라져 기존 와이어 연결이 끊어질 수 있다.
따라서 차이점을 리포트하고 다운로드 링크를 제공하여 사용자가 직접 교체 여부를 판단하게 한다.

---

## 단계 5: 텍스트 기반 설계 리뷰

`references/review-checklist.md`에 정의된 체크리스트를 적용한다. 아래는 핵심 요약이고, 상세 기준과 판정 로직은 참조 문서에 있다.

### 리뷰 카테고리

| # | 카테고리 | 주요 검증 내용 | 항목 수 |
|---|----------|---------------|---------|
| V | PDF 시각적 검토 | junction 누락, 부품 겹침, 미배선, 레이블 이탈 | 7 |
| L | 라이브러리 비교 | 제조사 공식 심볼 대비 핀 번호/이름/풋프린트 정합 | 5 |
| A | 전원 설계 | 모든 IC의 VCC/GND 연결, 디커플링 캡, 전원 시퀀싱 | 8 |
| B | 핀 연결 완전성 | 미연결(NC) 핀, 플로팅 입력, 풀업/풀다운 | 6 |
| C | 신호 무결성 | 직렬 종단 저항, 차동 페어 매칭, 임피던스 | 6 |
| D | 데이터시트 정합성 | 핀 기능, 정격 전압/전류, 권장 회로 일치 | 8 |
| E | ERC 수준 검증 | 전원 플래그, 양방향 핀 충돌, 네트 이름 일관성 | 5 |
| F | 도메인별 검증 | FPGA/MCU/PHY/EtherCAT 고유 항목 (해당 시에만) | 가변 |

### 판정 기준

- **ERROR**: 하드웨어 손상 또는 동작 불가. 반드시 수정 필요.
- **WARN**: 동작은 하지만 잠재적 문제 또는 모범사례 미준수.
- **OK**: 이상 없음.
- **N/A**: 해당 회로에 적용 불가.

---

## 단계 6: 데이터시트 비교 검증

각 주요 IC(passive 제외)에 대해 데이터시트를 웹 검색하고 권장 회로와 비교한다.
상세 검색 전략은 `references/datasheet-lookup.md`를 참조한다.

### 검증 절차

1. **IC 식별**: 회로도에서 IC 부품(U 레퍼런스) 목록 추출
2. **데이터시트 검색**: 파트넘버로 웹 검색 → 제조사 공식 데이터시트 우선
3. **권장 회로 대조**:
   - Application Circuit / Typical Application 섹션
   - 절대 최대 정격(Absolute Maximum Ratings) vs 실제 인가 전압
   - 필수 외부 부품(바이패스 캡, 부트스트랩 저항 등) 누락 여부
   - 핀별 기능 설명 vs 회로도 연결 일치
4. **결과 기록**: 각 IC별로 검증 항목과 결과를 정리

### 데이터시트 검색 예시

```
검색어: "DP83848 datasheet pdf site:ti.com"
검색어: "W25Q128JVS datasheet site:winbond.com"
검색어: "XC7A200T datasheet site:xilinx.com OR site:amd.com"
```

IC의 `(property "Datasheet" ...)` 필드에 URL이 있으면 해당 URL을 우선 사용한다.

---

## 단계 7: BOM 마크다운 생성

### BOM 형식

```markdown
# BOM (Bill of Materials)

**프로젝트**: {프로젝트명}
**날짜**: {날짜}
**회로도 리비전**: {rev}
**총 부품 수**: {고유 종류}종 / {총 수량}개

## 요약

| 카테고리 | 종류 수 | 총 수량 |
|----------|--------|---------|
| IC       | 5      | 7       |
| 커패시터 | 8      | 45      |
| 저항     | 6      | 23      |
| 커넥터   | 3      | 3       |
| 기타     | 2      | 4       |

## 상세 파트리스트

| # | Reference | Value | Footprint | Qty | Description | Datasheet |
|---|-----------|-------|-----------|-----|-------------|-----------|
| 1 | U1 | XC7A200T-2FBG484I | BGA-484 | 1 | Artix-7 FPGA | [Link](...) |
| 2 | U2, U3 | DP83848CVV | LQFP-48 | 2 | 10/100 Ethernet PHY | [Link](...) |
| 3 | U_FLASH | W25Q128JVS | WSON-8 | 1 | 128Mbit SPI Flash | [Link](...) |
| 4 | C1~C20 | 100nF | 0402 | 20 | 디커플링 캡 | - |
| 5 | C21~C24 | 10μF | 0805 | 4 | 벌크 캡 | - |
| ... | | | | | | |

## DNP (Do Not Place)

| Reference | Value | 사유 |
|-----------|-------|------|
| R99 | 0Ω | 옵션 미실장 |
```

### BOM 생성 규칙

- 같은 Value + Footprint 조합은 한 행으로 그룹핑
- Reference 목록은 자연 정렬 (C1, C2, ..., C10, C11)
- DNP 마킹된 부품은 별도 테이블로 분리
- 전원 심볼(#PWR), 테스트 포인트(TP) 등 가상 부품은 BOM에서 제외
- 데이터시트 URL이 있으면 링크 포함

---

## 단계 8: 종합 리뷰 보고서

### 보고서 템플릿

```
═══════════════════════════════════════════
  KiCad 회로도 리뷰 보고서
═══════════════════════════════════════════

프로젝트: {프로젝트명}
회로도: {파일 목록}
리비전: {rev}
검증일: {날짜}

━━━ 리뷰 요약 ━━━

  A. 전원 설계:       OK {n} / WARN {n} / ERROR {n}
  B. 핀 연결 완전성:   OK {n} / WARN {n} / ERROR {n}
  C. 신호 무결성:      OK {n} / WARN {n} / ERROR {n}
  D. 데이터시트 정합:  OK {n} / WARN {n} / ERROR {n}
  E. ERC 수준:        OK {n} / WARN {n} / ERROR {n}
  F. 도메인별 검증:    OK {n} / WARN {n} / ERROR {n}

  종합: OK {n} / WARN {n} / ERROR {n}

━━━ ERROR 항목 ━━━

  🔴 {ID} — {설명}
     위치: {서브시트} / {부품 레퍼런스}
     원인: {근거 — 데이터시트 섹션/페이지 참조}
     조치: {구체적 수정 방법}

━━━ WARN 항목 ━━━

  ⚠️ {ID} — {설명}
     위치: {서브시트}
     사유: {근거}
     권장: {개선 방법}

━━━ 데이터시트 비교 결과 ━━━

  [{IC 파트넘버}]
    데이터시트: {URL 또는 출처}
    권장 회로 대조:
      [✓] 바이패스 캡 배치 — OK
      [✗] REXT 저항 누락 — ERROR
      [✓] 전원 핀 연결 — OK
    정격 검증:
      VCC 범위: {min}~{max}V, 설계 전압: {actual}V — OK/ERROR

━━━ BOM 요약 ━━━

  총 {n}종 / {n}개 부품
  (상세 BOM은 별도 파일 참조)
```

---

## 도메인별 추가 검증 (카테고리 F)

해당 도메인의 IC가 감지되면 자동으로 추가 검증 항목을 적용한다.

### FPGA (Xilinx/AMD)

- VCCINT, VCCAUX, VCCBRAM, VCCO, MGTAVCC, MGTAVTT 전원 레일 완전성
- 컨피규레이션 핀(M[2:0], CCLK, DONE, PROGRAM_B, INIT_B) 연결 확인
- JTAG 체인(TCK, TMS, TDI, TDO) 연결
- 디커플링 캡 수량 (Xilinx Power Estimator 권장치 대비)
- SPI Flash 연결 (CCLK → SCK, D00~D03 → IO0~IO3)
- GT 트랜시버 AC 커플링 캡 (100nF, 차동 페어)

### MCU (STM32, etc.)

- 기존 `kicad-stm32-review` 스킬의 42항목 체크리스트 참조
- 다른 MCU 제조사는 해당 데이터시트의 하드웨어 설계 가이드 기준 적용

### Ethernet PHY (DP83848, KSZ8081, etc.)

- RMII/MII 모드 스트랩 핀 설정
- MDI 쌍(TX±, RX±) 매칭 및 종단
- REXT (1% 정밀 저항) 값과 연결
- 클럭 소스(25MHz/50MHz) 및 모드 설정 핀
- LED 출력 핀 연결
- **아날로그 프런트엔드** (ETH1~ETH10): 트랜스포머, ESD TVS, Bob Smith 종단, RJ45 — 상세 기준은 `references/ethernet-frontend.md` 참조

### EtherCAT 슬레이브 (LAN9252, ET1100, XMC4800)

- SPI/PDI 인터페이스 연결
- EEPROM(93C66) 연결
- PHY 인터페이스(RMII/MII) 및 스트랩 핀
- SYNC/LATCH 핀 연결
- IRQ 출력 핀

### 전원 IC (Buck/LDO)

- 입출력 캡 사양 (ESR, 용량) — 데이터시트 권장치 대조
- 피드백 저항 분배비 → 출력 전압 계산 검증
- Enable 핀 처리 (풀업 또는 시퀀싱 연결)
- Power Good 출력 연결
- 인덕터 값과 포화 전류

---

## 에이전트 위임

실제 검증 작업은 에이전트에게 위임한다:

- **kicad-schematic-reviewer**: 회로도 파싱 + 체크리스트 적용 + 데이터시트 비교 + 리뷰 보고서 작성
- **kicad-bom-generator**: 넷리스트에서 BOM 추출 + 마크다운 포맷팅

에이전트는 `kicad-setup` 스킬로 타겟 프로젝트의 `.claude/agents/`에 설치한다.

---

## 사용 예시

```
사용자: "이 KiCad 회로도 리뷰해줘"
사용자: "hw/kicad 폴더의 회로도 검토하고 BOM 만들어줘"
사용자: "이 보드에 사용된 IC들 데이터시트 확인해서 문제 없는지 봐줘"
사용자: "파트리스트 마크다운으로 뽑아줘"
```

$ARGUMENTS
