---
name: kicad-review
description: "KiCad 회로도(.kicad_sch)를 실무 순서로 리뷰합니다 — ERC(기계 판정) → 풋프린트 해석 검사 → 구조 린트 → 시각 검토 → 라이브러리 핀 대조 → 설계/데이터시트 체크리스트 → BOM(파트리스트) 마크다운 생성. 'KiCad 회로도 리뷰', '회로도 검토', '회로 리뷰', 'schematic review', '회로도 분석', 'ERC 돌려줘', '회로도 ERC', '풋프린트 확인', '풋프린트 해석', '회로도 린트', '파트리스트 만들어', 'BOM 생성', '부품 목록', 'MPN BOM', 'JLCPCB 조달', '회로도에서 문제 찾아', '데이터시트 비교', '회로 검증', 'KiCad BOM', '회로도 체크' 등의 요청에 자동 적용. ※ ERC는 이 스킬(회로도 리뷰)의 첫 단계다. PCB(.kicad_pcb) 물리 레이아웃·DRC·트랙/넷 추적·신호/전원 무결성(SI/PI)은 kicad-analyze 스킬을 쓴다. STM32, FPGA(Xilinx/Intel), EtherCAT 슬레이브, IO 보드, 전원부, PHY/트랜시버 등 모든 하드웨어 도메인을 지원하는 범용 회로도 리뷰 도구."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# KiCad 범용 회로도 리뷰 + BOM 생성

> 이 스킬은 KiCad 회로도 파일을 파싱하여 설계 오류를 검출하고,
> 사용된 소자의 데이터시트를 웹에서 검색해 권장 회로와 비교 검증한 뒤,
> 마크다운 형식의 BOM(파트리스트)을 생성합니다.

## 워크플로우 개요

순서의 원칙은 하나다 — **기계가 판정할 수 있는 것을 먼저 걷어내고, 남은 것만 사람이 본다.**
실무 회로도 리뷰는 ERC를 첫 단계로 돌린다. 미연결 핀·다중 드라이버·PWR_FLAG 누락은 30초짜리 기계 판정이라
사람이 다시 볼 이유가 없고, 가장 비싼 단계(PDF 멀티모달 판독, IC별 웹 검색)를 맨 앞에 두면
기계가 이미 잡아낼 문제를 사람 시간으로 다시 찾게 된다.
비유하면 원고 교정에서 맞춤법 검사기를 먼저 돌리고 나서 문장을 읽는 것과 같다.

```
[준비]
 [1] 프로젝트 탐색 + 파일 무결성 확인
 [2] 회로도 파싱 — 부품, 핀, 네트, 값 추출
     ↓
[기계 판정 — 여기서 대부분이 걸린다]
 [3] ERC 실행 — 프로젝트 ignore 설정 확인 후 기본값 재실행까지
 [4] 풋프린트 해석 검사 (fp-lib-table 실존 + 실제 로드 시험)
 [5] 회로도 구조 린트 (MCP, 시트마다 반복 + 오탐 필터)
     ↓
[사람 판정 — 기계가 못 잡는 것만]
 [6] PDF 시각 검토 — 가독성 항목(V2/V5/V6)
 [7] 라이브러리 핀 대조 — 로컬 .kicad_sym(MCP 실패 시 직접 파싱) + 데이터시트
 [8] 설계 리뷰 체크리스트 — 전원/핀 연결/신호 무결성/도메인별
 [9] 데이터시트 비교 — 권장 회로·정격 대조
     ↓
[산출]
 [10] BOM 마크다운 생성 (실제 필드명 탐지 → 매핑, --sourcing 옵트인)
 [11] 종합 리뷰 보고서 출력
```

**폴백**: kicad-cli도 KiCAD-MCP-Server도 없으면 3~5단계를 수행할 수 없다.
그때는 기존 텍스트 추론 경로(넷리스트/직접 파싱 기반 E 카테고리 판정 + V1~V7 육안)로 내려가고,
보고서 머리에 "ERC·구조 린트 미수행 — 텍스트 추론 모드" 를 명시한다.

---

## 단계 1: 프로젝트 탐색 + 파일 무결성 확인

```bash
# 프로젝트 파일 탐색
find "$TARGET_DIR" -name "*.kicad_pro" -o -name "*.kicad_sch" | sort

# kicad-cli 버전 확인
kicad-cli --version 2>/dev/null || echo "kicad-cli 없음 — 직접 파싱 모드"
```

**계층 구조 파악**: 루트 `.kicad_sch`에서 `(sheet ... (property "Sheetfile" "xxx.kicad_sch"))` 를 찾아 서브시트 계층을 파악한다.

**엔진 선택**: KiCAD-MCP-Server가 등록돼 있으면 `get_backend_state`로 파이썬 브리지까지 살아 있는지 먼저 확인한다
(첫 호출은 pcbnew 초기화로 최대 1분 걸릴 수 있다 — 타임아웃으로 오판하지 않는다).
도구 카탈로그와 폴백 체인의 정본은 `../kicad-analyze/references/mcp-tools.md`이며, 여기서 복제하지 않는다.

**파일 무결성(S0)**: MCP가 있으면 시트마다 `validate_schematic`을 돌려 괄호/문자열 불균형·고아 property를
라인·컬럼 단위로 먼저 걷어낸다(kicad-cli가 없으면 `runKicadCli: false`).
여기서 실패하는 파일은 이후 단계가 전부 무의미하므로 즉시 보고하고 멈춘다.

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

## 단계 3: ERC 실행 (기계 판정)

**리뷰의 첫 기계 판정이다.** ERC(Electrical Rules Check, KiCad가 회로도의 전기 규칙 위반을 자동으로 찾는 검사)를
루트 시트에 한 번 돌리면 계층 전체를 본다. 미연결 핀·다중 드라이버·전원 드라이버 부재는 여기서 확정되며,
사람이 PDF를 보며 다시 찾을 이유가 없다.

### 3-1. 먼저 프로젝트가 무엇을 꺼 놨는지 읽는다

**ERC를 그냥 돌리면 프로젝트가 꺼 둔 규칙은 아예 보고되지 않는다.** `.kicad_pro`의
`erc.rule_severities`에서 `ignore`로 설정된 규칙은 `--severity-all`을 줘도 나오지 않는다.
`--severity-all`은 "보고할 규칙 중 모든 등급을 내보내라"는 뜻이지 "꺼진 규칙을 되살려라"가 아니다.
비유하면 화재경보기 전원을 뽑아 놓고 "경보가 안 울리니 안전하다"고 적는 것과 같다.

```bash
# 프로젝트가 무시하도록 설정한 규칙 목록
python3 -c "
import json,sys
d=json.load(open(sys.argv[1])); erc=d.get('erc',{})
rs=erc.get('rule_severities',{})
ig=[k for k,v in rs.items() if v=='ignore']
print('ignore 설정:', len(ig), '종 ->', ig)
print('erc_exclusions:', len(erc.get('erc_exclusions',[])), '건')
" "$PROJECT.kicad_pro"
```

### 3-2. 기본 설정으로 되살려 재실행한다

프로젝트 사본을 만들고 `.kicad_pro`에서 `erc.rule_severities` 블록을 **통째로 지운 뒤** 다시 돌린다.
그러면 KiCad 기본 등급이 적용된다. **꺼진 규칙을 전부 `error`로 올리지는 않는다** — 실측에서
`footprint_filter` 하나가 282건을 쏟아 내 리포트가 잡음에 묻혔다(아래 수치 참조).

```bash
cp -r "$PROJECT_DIR" /tmp/erc_default && cd /tmp/erc_default
python3 -c "
import json,sys
p=sys.argv[1]; d=json.load(open(p)); d['erc'].pop('rule_severities',None)
json.dump(d,open(p,'w'),indent=2)" "$PROJECT.kicad_pro"
kicad-cli sch erc --format json --severity-all --output /tmp/erc_default.json "$ROOT_SCH"
```

### 3-3. 두 결과를 함께 보고한다

리포트에 **"프로젝트가 무시하도록 설정한 규칙 N종"** 을 목록으로 적고, 기본 설정 재실행에서
새로 나온 위반을 **"프로젝트 설정으로 가려져 있던 위반"** 으로 별도 표에 싣는다.
`erc_exclusions`가 비어 있는데 `rule_severities`에 `ignore`만 쓰였다면
**"이력 없는 억제"** 로 지적한다 — 개별 위반을 검토하고 제외한 기록이 아니라 규칙 자체를 끈 것이다.

**중요 규칙이 꺼져 있으면 경고한다.** 아래 다섯은 꺼져 있다는 사실 자체를 WARN으로 낸다.

| 꺼지면 경고할 규칙 | 왜 |
|---|---|
| `power_pin_not_driven` | 전원 핀 미구동 — 보드가 안 켜지는 1순위 원인 |
| `pin_to_pin` | 출력 충돌 — 소자가 깨진다 |
| `endpoint_dangling` · `wire_dangling` | 미배선 |
| `lib_symbol_mismatch` · `lib_symbol_issues` | 라이브러리와 회로도 심볼 불일치 |
| `duplicate_reference` | 레퍼런스 중복 |

**실측(이 스킬 검증 보드: 371부품·8시트, KiCad 10.0.6).**

| 실행 | 위반 수 | 내역 |
|---|---:|---|
| 프로젝트 설정 그대로 | 25 | `footprint_link_issues` 24, `lib_symbol_mismatch` 1 |
| `rule_severities` 제거(KiCad 기본) | **41** | 위 25 + `power_pin_not_driven` 10(error), `pin_to_pin` 5, `multiple_net_names` 1 |
| `ignore` 7종을 전부 `error`로 승격 | 358 | `footprint_filter` 282가 잡음 — **이 방식은 쓰지 않는다** |

이 보드의 `.kicad_pro`는 7종(`footprint_filter`, `four_way_junction`, `multiple_net_names`,
`pin_to_pin`, `power_pin_not_driven`, `simulation_model_issue`, `single_global_label`)을 껐고
`erc_exclusions`는 0건이었다. 문서대로 한 번만 돌리면 **전원 핀 미구동 10건을 통째로 못 본다.**

### 3-4. 실행

```bash
# kicad-cli 경로 (실측 기준: KiCad 10.0.6)
kicad-cli sch erc \
  --format json \
  --severity-all \
  --output /tmp/erc.json \
  "$ROOT_SCH"
```

MCP가 있으면 `run_erc`를 대신 쓴다 — 구현이 위 kicad-cli 명령의 래퍼이므로 판정은 동일하다.
**단, MCP에는 `rule_severities`를 무시하고 돌리는 옵션이 없다** — 3-2의 사본 재실행은 kicad-cli로만 된다.
**`run_erc`는 600초 예외 목록에 없어 30초 예산으로 돈다.** 큰 계층에서 타임아웃이 나면
위 kicad-cli 명령을 Bash로 직접 부른다.

### 결과를 체크리스트에 연결하는 방법

| ERC 위반 | 체크리스트 항목 |
|----------|----------------|
| `pin_to_pin` (출력 충돌) | E1 |
| `power_pin_not_driven` | A7 / E2 |
| `same_local_global_label` | E4 |
| 미연결 끝점 · `four_way_junction` | E5 / V1 |
| 미연결 핀 | B1 / B2 |
| `footprint_link_issues` | P4 (단계 4의 로드 시험 1차 근거) |
| `lib_symbol_mismatch` · `lib_symbol_issues` | L1~L3 (단계 7) |

**주의: ERC 위반 항목에는 부품 참조가 없고 좌표(x/y)만 남는다.** 보고서에 "U2 pin 5"로 쓰려면
`list_schematic_components`(MCP) 또는 넷리스트의 핀 좌표와 대조하는 후처리가 필요하다.
대조가 불가능하면 좌표와 시트 이름만 적고 부품을 추정해 쓰지 않는다.

kicad-cli도 MCP도 없으면 이 단계를 수행할 수 없다 — E 카테고리를 넷리스트/직접 파싱 기반
텍스트 추론으로 판정하고, 보고서에 "ERC 미수행 — 텍스트 추론 모드" 를 명시한다.

---

## 단계 4: 풋프린트 해석 검사

회로도의 `Footprint` 속성은 `Lib:Name` 문자열일 뿐이다. 그 nickname이 실제 라이브러리로 풀리는지는
`fp-lib-table`을 읽어야만 알 수 있고, **여기서 실패하는 것이 Update PCB 실패의 1위 원인**이다.
비유하면 Footprint 필드는 "책 제목"이고 fp-lib-table은 "그 책이 어느 서가에 있는지 적힌 목록"이다.
목록에 없는 제목은 보드로 넘어가는 시점에 그대로 실패한다.

### 절차

1. **넷리스트 XML의 `<footprint>`를 전부 수집한다** — 빈 값도 버리지 않고 함께 모은다(P1 판정 대상).

```python
import xml.etree.ElementTree as ET
tree = ET.parse('/tmp/netlist.xml')
fp_fields = [(c.get('ref', ''), (c.findtext('footprint') or '').strip())
             for c in tree.findall('.//comp')]
```

2. **`Lib:Name`으로 분리한다.** 콜론이 없는 값은 그 자체로 ERROR다.

3. **nickname 실존을 확인한다.**
   - MCP: `list_library_table`(`tableType: "footprint"`, `scope: "project"` 또는 `"global"`,
     `projectPath`는 `.kicad_pro` 또는 그 디렉토리). 서버가 URI를 해석하고 파일 실존까지 보고하며,
     `(type "Table")` 간접 행은 "몇 개 라이브러리를 대신하는가"까지 풀어 준다.
     **단, 실존은 로드 가능을 뜻하지 않는다** — 이 도구는 디렉토리가 있는지만 보고 `.kicad_mod`를
     파싱하지 않으므로 `exists: true` / `missingCount: 0`을 합격으로 읽으면 안 된다. 5단계로 넘어간다.
   - MCP 없음: 전역 `~/.config/kicad/<버전>/fp-lib-table` + 프로젝트 `fp-lib-table`을 직접 파싱한다
     (같은 nickname이면 프로젝트 항목이 이긴다). 파싱 스크립트는 `references/kicad-parser.md`의
     "fp-lib-table 파싱" 절에 있다.

4. **`.pretty` 디렉토리에 `<Name>.kicad_mod`가 있는지 확인한다.**

5. **각 라이브러리를 실제로 로드해 본다(P4).** 파일이 제자리에 있는데 KiCad가 못 읽는 라이브러리는
   위 1~4로는 구조적으로 안 잡힌다. 라이브러리마다 풋프린트 하나를 골라 `kicad-cli`로 실제 내보내 보고,
   실패하면 ERROR다.

```bash
# 해석된 .pretty 전부에 대해 "진짜 열리는가"를 시험한다
TMP=$(mktemp -d)
for d in "$PROJECT_DIR"/libraries/*.pretty; do
  one=$(ls "$d"/*.kicad_mod 2>/dev/null | head -1); [ -z "$one" ] && continue
  fp=$(basename "$one" .kicad_mod)
  kicad-cli fp export svg --fp "$fp" --output "$TMP/$(basename "$d")" "$d" >/dev/null 2>&1 \
    || echo "P4 ERROR: $(basename "$d") — 라이브러리를 로드할 수 없습니다"
done
rm -rf "$TMP"
```

   `kicad-cli fp export svg`가 KiCad 10.0.6에 실존하는 유일한 풋프린트 로더 명령이다
   (`kicad-cli fp --help` → `export`(svg) / `upgrade`뿐). `--fp`로 풋프린트 하나만 지정하면
   라이브러리 전체를 그리지 않아 빠르다 — **실측 42개 라이브러리에 7.8초.**
   kicad-cli가 없으면 `.kicad_mod`를 python으로 파싱해 `(fp_arc ...)`의 start/mid/end 외심을 구하고
   **호 각도가 정확히 180도**인 아크가 있는 파일을 후보로 낸다(아래 실측 원인 참조).

**실측(이 스킬 검증 보드).** `list_library_table`은 41개 항목 전부 `exists: true` / `missingCount: 0`으로
합격을 냈지만, 로드 시험에서는 **42개 중 2개(`LED_1608_GREEN`, `M24C64C`)가 실패**했다.
같은 두 라이브러리를 ERC가 `footprint_link_issues` 24건으로 지적했으므로 **ERC가 옳고 1~4 판정이 틀렸다.**
원인은 두 파일에만 있는 **정확히 180도인 `fp_arc`** 다 — KiCad 10의 파서가 그 아크에서 깨져
라이브러리 **전체**를 못 읽는다. 파일은 멀쩡히 자리에 있으므로 "파일 있음" 검사로는 절대 안 보인다.

> 비유: 책 한 권에 찢어진 페이지가 하나 있으면 도서관이 그 책을 아예 안 꺼내 준다.
> 서가에 책이 꽂혀 있는 것(실존)과 빌릴 수 있는 것(로드 가능)은 다른 이야기다.

### KiCad 10 간접 테이블 주의

KiCad 10의 전역 `fp-lib-table`은 대개 아래 **한 줄뿐**이다.

```lisp
(lib (name "KiCad") (type "Table") (uri "${KICAD10_TEMPLATE_DIR}/fp-lib-table") (options "") (descr "KiCad Default Libraries"))
```

`(type "Table")`은 라이브러리가 아니라 **다른 테이블을 가리키는 간접 참조**다.
이 환경(KiCad 10.0.6) 실측으로 이 한 줄이 `/usr/share/kicad/template/fp-lib-table`의 **155개 라이브러리**를 대신한다.
따라서 전역 테이블을 `grep`으로 훑어 "라이브러리가 하나뿐"이라고 판정하면 안 된다 — **사람 눈으로는 보이지 않는다.**
간접 행을 따라 들어가 펼친 뒤에 판정한다.

### 판정

| 조건 | 판정 | 체크리스트 |
|------|------|-----------|
| `Footprint` 필드가 비어 있음 | ERROR | P1 |
| `Lib:Name` 형식이 아님 (콜론 없음) | ERROR | P2 |
| nickname이 fp-lib-table에 없음 | ERROR | P2 |
| 해석된 URI 경로가 존재하지 않음 | ERROR | P2 |
| `<Name>.kicad_mod` 파일 부재 | ERROR | P3 |
| 파일은 있는데 `kicad-cli fp export svg`가 로드에 실패 | ERROR | P4 |

**P1 판정에서 BOM 제외 부품은 걸러낸다.** 넷리스트 XML의 `<property name="exclude_from_bom"/>`
(회로도의 `(in_bom no)`)가 붙은 심볼은 기구 표기용 마운팅 홀·전원 표기라 풋프린트가 없는 것이 정상이고,
KiCad 자신의 ERC도 문제 삼지 않는다. 걸러낸 건수는 **"제외 N건(BOM 제외 표시 부품)"** 으로 함께 적는다.
실측: 빈 `Footprint` 9건 중 8건이 `exclude_from_bom`이었고 **진짜 결함은 1건(J1, 실장 커넥터)** 이다.

```python
excluded = {c.get('ref') for c in tree.findall('.//comp')
            if c.find('property[@name="exclude_from_bom"]') is not None}
p1 = [(ref, fp) for ref, fp in fp_fields if not fp and ref not in excluded]
```

D2/L4(풋프린트가 그 부품의 패키지와 맞는가)와는 다른 검사다 — 이 단계는 "그 풋프린트가 존재하는가"만 본다.

---

## 단계 5: 회로도 구조 린트 (MCP)

KiCAD-MCP-Server가 등록돼 있으면 구조 결함을 좌표·라인 번호와 함께 기계로 뽑는다.
**이 린트 도구들은 kicad-cli 없이도 동작하므로, 직접 파싱 모드에서 특히 값이 크다.**

| 도구 | 무엇을 잡나 | 체크리스트 |
|------|------------|-----------|
| `validate_schematic` | 괄호/문자열 불균형·고아 property (단계 1에서 이미 돌렸으면 생략) | S0 |
| `lint_offgrid` | 오프그리드 좌표 + 라인 번호. "보기엔 붙었는데 실제 미연결"의 주원인 | S3 / V1 |
| `list_floating_labels` | 핀에 닿지 않는 떠 있는 레이블 | S1 / V3 |
| `find_orphaned_wires` | 한쪽 이상이 떠 있는 와이어 끝점 | S2 / V7 |
| `find_wires_crossing_symbols` | 심볼을 관통하는 와이어 | S4 / V2 |
| `find_overlapping_elements` | 겹친 와이어·레이블, 같은 좌표의 중복 전원 심볼 | S4 / V2 / V4 |

### 호출 규칙

- **시트마다 반복한다.** 이 도구들은 파일 하나만 읽는다 — 루트와 모든 서브시트에 각각 호출한다.
  시트 목록은 단계 1의 계층 구조 또는 MCP `get_sheet_properties`로 얻는다.
- **`lint_offgrid`에 `fix`를 넘기지 않는다.** 이 스킬은 회로도를 수정하지 않는다.
  같은 이유로 `enrich_datasheets`·`snap_to_grid`도 호출하지 않는다.
- 출력 상한은 도구마다 다르다(실측: `find_wires_crossing_symbols` 30건, `find_overlapping_elements` 20건).
  **`Found N`의 N과 실제 출력 줄 수를 항상 비교**해 다르면 보고서에 "린트 결과 절단됨" 을 명시한다.
- 오프그리드 이탈이 0.5 mm를 넘으면 도구가 NEEDS HUMAN으로 표시한다 — 자동 판정하지 말고 그대로 보고한다.

### 오탐 필터 — 이 세 도구는 거른 뒤에 쓴다

`find_orphaned_wires` · `find_overlapping_elements` · `find_wires_crossing_symbols` 세 도구는
**날것 그대로면 대부분이 오탐이다.** 실측(371부품·8시트 실무 보드)에서 427건이 나왔고 그중
진짜 결함은 0건이었다. 원인이 재현 가능하게 특정되므로, 아래 네 필터를 **적용한 뒤에만** 보고한다.

| 필터 | 대상 도구 | 규칙 | 근거 |
|------|-----------|------|------|
| F1 | `find_orphaned_wires` | 떠 있다고 지목된 끝점이 **핀 번호가 빈 문자열인 심볼**(테스트포인트·SMD 패드·마운팅 패드)의 핀 좌표와 일치하면 제외 | 도구가 `(number "")` 핀을 핀으로 세지 않아 정상 연결을 dangling으로 본다 |
| F2 | `find_overlapping_elements` · `find_wires_crossing_symbols` | **양쪽 레퍼런스가 같은 쌍**(`U6 ↔ U6`)은 제외 | 멀티유닛 심볼의 서로 다른 유닛을 별개 심볼로 보고 자기 자신과 겹쳤다고 판정한다 |
| F3 | `find_overlapping_elements` · `find_wires_crossing_symbols` | 상대가 **멀티유닛 심볼 또는 몸체가 거대한 단일 심볼**이면, 배치된 **그 유닛의** 바운딩 박스로 다시 판정해 실제로 교차하는 건만 남긴다 | 도구가 심볼 전체(모든 유닛)의 바운딩 박스를 쓴다 — 245 mm 떨어진 두 유닛이 "겹침"이 된다 |
| F4 | `find_wires_crossing_symbols` | 와이어의 **끝점이 그 심볼의 핀 좌표와 일치하면** 정상 접속이므로 제외 + 동일한 `(와이어, 심볼)` 중복 보고 제거 | 핀에 정상 접속한 와이어도 바운딩 박스와 겹치면 "관통"이 된다. 같은 와이어가 2번씩 세어져 건수가 2배로 부풀려진다 |

F1·F3·F4는 `.kicad_sch`의 `lib_symbols` 정의를 읽어야 판정된다 —
스크립트는 `references/kicad-parser.md`의 **"구조 린트 오탐 필터"** 절에 있다.

**보고 방식.** 필터 후 남은 건만 본문 표에 싣고, 걸러낸 건수는
**"제외 N건(사유)"** 로 같은 표 아래에 한 줄로 남긴다. 예:

```
S2 떠 있는 와이어: 0건 (제외 29건 — 핀 번호가 빈 테스트포인트 심볼 F1)
S4 겹침: 27건 [후보] (제외 37건 — 멀티유닛 바운딩 박스 F2/F3)
S4 관통: 2건 [후보] (제외 332건 — 핀 정상 접속·중복 계수 F4)
```

**필터 후에도 ERROR/WARN으로 확정하지 않는다.** 남은 건은 `[후보]`로 표시하고,
`get_schematic_view_region`으로 좌표를 확대해 눈으로 확인한 것만 등급을 매긴다.

**실측 효과(같은 보드, 필터 적용 전 → 후).**

| 도구 | 필터 전 | 필터 후 | 적용 필터 |
|------|--------:|--------:|-----------|
| `find_orphaned_wires` | 29 | **0** | F1 (29/29가 빈 핀번호 심볼 좌표와 정확히 일치) |
| `find_overlapping_elements` | 64 | **27** | F2(2) + F3 |
| `find_wires_crossing_symbols` | 334 | **2** | F2 + F4 |
| 단계 4 P1(빈 Footprint) | 9 | **1** | `exclude_from_bom` 8건 제외 |
| **단계 3~5 기계 판정 합계** | **461** | **55** | 진짜 결함 26건은 전건 생존, 잡음 435 → 29 |

이 표의 ERC 값은 양쪽 모두 **프로젝트 설정 그대로**인 25건이다. 단계 3의 ignore 확인까지 적용하면
ERC가 41건이 되므로 실제 최종 산출은 55 + 16 = 71건이며, **늘어난 16건은 전부 진짜 위반**이다
(전원 핀 미구동 10, 출력 충돌 5, 넷 이름 중복 1). 필터는 잡음만 줄이고 신호는 오히려 늘린다.

MCP가 없으면 이 단계를 건너뛰고 단계 6의 육안 판정으로 대체한다
(보고서에 "구조 린트 미수행 — MCP 미등록" 명시).

---

## 단계 6: PDF 시각 검토

회로도를 PDF로 내보내 멀티모달 분석을 수행한다.

**단계 3~5(ERC·풋프린트·린트)를 이미 돌렸다면 이 단계의 범위는 줄어든다.**
V1·V3·V4·V7은 ERC와 린트가 좌표 근거로 확정하므로 육안 재확인을 하지 않는다.
PDF 육안이 담당하는 고유 영역은 세 항목이다.

| 남는 항목 | 왜 기계가 못 잡나 |
|-----------|------------------|
| V2 (필드 텍스트 겹침) | `find_overlapping_elements`는 심볼·와이어·레이블 중첩까지만 본다. Reference/Value 필드 텍스트 겹침은 범위 밖 |
| V5 (신호 흐름 가독성) | 관례 판정이라 규칙으로 표현되지 않는다 |
| V6 (시트 간 일관성) | 계층 핀 이름과 서브시트 레이블의 의미 대조는 사람 판정 |

ERC도 MCP도 없는 환경에서는 V1~V7 전부를 육안으로 보되, 보고서에 "기계 판정 미수행 — 육안 폴백" 을 명시한다.

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
| V1 | **T 접합 junction 누락** — 와이어 끝점이 다른 와이어 중간에 닿는 T 접합에 junction(접합점) 마커가 없으면 미연결. X 자 교차는 junction이 없어야 정상이며, junction이 있으면 의도치 않은 단락 후보로 WARN | T 접합에 접합점이 없어 시각적으로만 연결됨 / X 자 교차에 접합점이 찍혀 두 네트가 합쳐짐 |
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

- **ERROR**: V1의 T 접합 junction 누락(실제 미연결), V3(레이블 미연결), V7(미배선)
- **WARN**: V1의 X 자 교차 junction(의도치 않은 단락 후보), V2(겹침), V4(전원 배치), V5(가독성), V6(일관성)

린트가 찍어 준 좌표 주변만 확대해 오탐을 검증하려면 MCP `get_schematic_view_region`
(mm 좌표 `x1,y1,x2,y2`, `format`은 지정하지 않고 기본 png)을 쓴다.
서버에 PNG 변환기가 없으면 SVG 텍스트가 그대로 돌아와 토큰이 폭증하므로, 실패하면 즉시 PDF 경로로 돌아온다.
`get_schematic_view`(단수)는 **루트 페이지만 렌더**하므로 계층 설계의 시각 검토를 대체하지 못한다.

---

## 단계 7: 라이브러리 핀 대조

회로도 심볼의 핀 정의가 정본과 맞는지 검증한다.
커스텀 심볼의 핀 번호/이름 오류는 가장 흔한 하드웨어 버그 중 하나다.

### 핀 대조 소스 (순서대로)

| 우선순위 | 소스 | 방법 | 비고 |
|---------|------|------|------|
| 1 | 프로젝트 내 벤더 `.kicad_sym` | MCP `list_symbol_pins`(`symbol`="Lib:Name", `schematicPath`로 프로젝트 sym-lib-table 해석). 다건은 `batch_list_symbol_pins`(`symbols` 배열). **`not found`가 나오면 1'로 내려간다** | 사용자가 이미 받아 둔 심볼이 있으면 그것이 회로도의 정본 |
| 1' | 같은 `.kicad_sym`을 **직접 파싱** | `sym-lib-table`에서 URI를 풀어 파일을 열고 `(symbol "…")` 블록에서 `(pin …)`을 뽑는다. 스크립트는 `references/kicad-parser.md`의 "**.kicad_sym 심볼 핀 직접 파싱**" 절 | MCP가 못 찾는 형식을 그대로 읽는다 — 아래 실측 참조 |
| 2 | KiCad 공식 라이브러리 | 같은 도구, 또는 `/usr/share/kicad/symbols/<Lib>.kicad_sym`을 Grep으로 `(pin ` 블록 추출 | 기본 내장 심볼 |
| 3 | 데이터시트 Pin Description 표 | 단계 9의 데이터시트로 대조 | **라이브러리 정의 자체가 틀린 경우의 최종 정본** |
| 4 | SnapEDA / Ultra Librarian / Component Search Engine | 웹 검색 — **다운로드 링크 제공용** | 핀 대조에는 쓰지 않는다(아래) |

**웹 검색을 핀 대조에 쓰지 않는 이유.** SnapEDA와 Ultra Librarian은 핀 테이블을 웹 페이지에 노출하지 않는다.
로그인 후 zip 다운로드가 필요해 WebFetch로는 열리지 않으므로, IC마다 검색을 시도하면 시간만 쓰고 결과가 없다.
이 소스들은 "불일치를 찾았을 때 교체본을 어디서 받는가"를 사용자에게 알려 주는 용도다.

**`kicad-cli sym export`는 쓰지 않는다** — SVG만 지원해서(실측: `kicad-cli sym --help`) 핀 데이터를 뽑지 못한다.
**대신 `.kicad_sym`을 텍스트로 직접 파싱한다**(위 우선순위 1'). 이 폴백이 없으면 단계 7이 통째로 죽는다.

### MCP `list_symbol_pins`가 못 찾는 형식 — 반드시 폴백한다

라이브러리 파일이 심볼을 `(symbol "LIB:NAME" …)`로 저장하면 MCP는 **100% `not found`** 를 낸다.
KiCad 정본은 `(symbol "NAME" …)`이지만, 벤더가 배포하거나 SnapEDA 등에서 받은 심볼은
라이브러리 이름을 심볼 이름에 붙여 저장하는 경우가 흔하다. MCP는 라이브러리 `LIB` 안에서 `NAME`을
찾는데 실제 키가 `LIB:NAME`이라 못 찾는다. **등록이 잘못된 게 아니라 도구의 키 조회 한계다.**

> 비유: 서류철 이름이 이미 파일 앞에 적혀 있는데, 검색기가 "서류철 안에서 이름만" 찾도록 만들어져
> 매번 빈손으로 돌아온다. 파일을 직접 열면 바로 보인다.

**실측(이 스킬 검증 보드).** 프로젝트 벤더 라이브러리 33개의 최상위 심볼 36개가 **전부** `LIB:NAME`
형식이었다. MCP는 **36개 중 0개** 조회에 성공했고, 직접 파싱 폴백은 **36개 중 36개** 를 뽑았다
(`SMD_HOLE:SMDPAD` 1핀, `C3216:C3216` 2핀, `ET1200_QFN-48:ET1200` 49핀 등).
같은 스크립트가 KiCad 정본(`MCU_ST_STM32F4:STM32F407IGHx` 201핀)도 읽는다 —
정본은 `(extends "…")` 상속을 쓰므로 스크립트가 상속을 따라간다.

이 폴백이 실제로 값을 내는 예: `ET1200_QFN-48:ET1200`의 exposed pad가 라이브러리에서는 핀 번호 `GND`인데
회로도 심볼은 `49`다. U1의 풋프린트(`QFN-48-1EP_…`)에서 exposed pad는 패드 **49번** 이므로
**회로도가 맞고 라이브러리가 낡았다.** 라이브러리를 그대로 다시 가져다 쓰면 방열 패드가 넷에 안 붙는다.

### 대형 IC 호출 규칙

**핀 100개 이상 IC는 전체 핀을 받지 않는다.** `compact: true`는 2핀 수동소자에만 적용되므로
BGA 하나가 그대로 수천 토큰을 먹는다(실측: STM32F407IGHx 201핀 약 5000토큰).
데이터시트 대조가 필요한 핵심 핀(전원·컨피그·클럭·리셋)만 골라 단건 조회하거나,
`.kicad_sym`을 직접 파싱해 해당 핀만 필터링한다.

### 검증 절차

1. **IC 목록 추출**: 회로도에서 IC(U 레퍼런스) 부품의 `lib_id`와 파트넘버를 수집한다
2. **라이브러리 정의 조회**: `lib_id`(`Lib:Name`)로 위 소스 1~2를 조회한다

```
# MCP 예시
list_symbol_pins(symbol="Device:R", schematicPath="/abs/path/root.kicad_sch")
batch_list_symbol_pins(symbols=["Regulator_Switching:TPS62130", "Interface_Ethernet:DP83848"],
                       schematicPath="/abs/path/root.kicad_sch")

# MCP 없음 또는 not found — 로컬 .kicad_sym 직접 파싱 (references/kicad-parser.md)
python3 sym_pins.py "$PROJECT_DIR" "SMD_HOLE:SMDPAD" "C3216:C3216"
```

3. **핀 정의 비교**: 조회한 핀 정보와 회로도 심볼 인스턴스를 대조한다

| 비교 항목 | ERROR 조건 | WARN 조건 |
|-----------|-----------|-----------|
| 핀 번호 | 공식 라이브러리와 불일치 | - |
| 핀 이름 | - | 공식 라이브러리와 불일치 (기능은 동일) |
| 핀 타입 (입력/출력/전원) | 전원 핀이 I/O로 잘못 정의 | 입출력 방향 차이 |
| 풋프린트 | 패키지 불일치 | 패드 크기/간격 차이 |
| 핀 총 개수 | 핀 수 불일치 | - |

4. **결과 리포트 작성**:

```markdown
### 라이브러리 핀 대조 결과

| IC | 파트넘버 | 대조 정본 | 핀 번호 | 핀 이름 | 핀 수 | 판정 |
|----|---------|----------|---------|---------|-------|------|
| U1 | TPS62130 | list_symbol_pins (프로젝트 .kicad_sym) | 일치 | 일치 | 일치 | OK |
| U2 | DP83848 | 데이터시트 Pin Description 표 (§4, p.7) | Pin 24 불일치 | RXD0 vs RX_D0 | 일치 | ERROR |

[불일치 상세]
  U2 (DP83848) Pin 24 — ERROR:
     회로도 심볼: Pin 24 = COL (출력)
     데이터시트 Pin Description (§4, p.7): Pin 24 = LED_CFG (입력)
     → 핀 기능이 완전히 다름. 회로도 심볼 교체 필요.

[교체본 다운로드 링크 — 미검증, 사용자가 직접 확인]
  - DP83848: https://ultralibrarian.com/... (검색: "DP83848 kicad library site:ultralibrarian.com")
```

`list_symbol_pins`는 "회로도 심볼 인스턴스 vs 라이브러리 정의"를 보는 1차 게이트다.
**라이브러리 정의 자체가 틀린 경우**(커스텀 심볼이 오답 원천인 가장 흔한 케이스)는 이 도구로 잡히지 않으므로,
IC의 핵심 핀은 데이터시트 Pin Description 표로 반드시 한 번 더 본다.
L4(풋프린트 패키지 일치)는 이 도구로 볼 수 없다 — 단계 4(존재 여부)와 단계 9 D2(패키지 적합성)가 담당한다.

### 자동 대체가 아닌 비교 검증인 이유

라이브러리 심볼로 자동 대체하면 핀 배치(좌/우/상/하 위치)가 달라져 기존 와이어 연결이 끊어질 수 있다.
따라서 차이점을 리포트하고 다운로드 링크를 제공하여 사용자가 직접 교체 여부를 판단하게 한다.

---

## 단계 8: 설계 리뷰 체크리스트

`references/review-checklist.md`에 정의된 체크리스트를 적용한다. 아래는 핵심 요약이고, 상세 기준과 판정 로직은 참조 문서에 있다.

### 리뷰 카테고리

| # | 카테고리 | 주요 검증 내용 | 항목 수 | 어느 단계에서 |
|---|----------|---------------|---------|--------------|
| E | ERC 수준 검증 | 출력 충돌, 전원 드라이버, 레이블 혼용, junction | 5 | 단계 3 (기계) |
| P | 풋프린트 해석 | Footprint 필드 실존, nickname 해석, `.kicad_mod` 실존 | 3 | 단계 4 (기계) |
| S | 구조 린트 | 파일 무결성, 오프그리드, 떠 있는 레이블/와이어, 겹침 | 5 | 단계 5 (기계) |
| V | PDF 시각적 검토 | 텍스트 겹침, 신호 흐름, 시트 간 일관성 (V2/V5/V6) | 7 | 단계 6 (사람) |
| L | 라이브러리 핀 대조 | 라이브러리 정의·데이터시트 대비 핀 번호/이름/타입/수 | 5 | 단계 7 |
| A | 전원 설계 | 모든 IC의 VCC/GND 연결, 디커플링 캡, 전원 시퀀싱 | 8 | 단계 8 |
| B | 핀 연결 완전성 | 미연결(NC) 핀, 플로팅 입력, 풀업/풀다운 | 6 | 단계 8 |
| C | 신호 무결성 | 직렬 종단 저항, 차동 페어 매칭, 임피던스 | 6 | 단계 8 |
| F | 도메인별 검증 | FPGA/MCU/PHY/EtherCAT 고유 항목 (해당 시에만) | 가변 | 단계 8 |
| D | 데이터시트 정합성 | 핀 기능, 정격 전압/전류, 권장 회로 일치 | 8 | 단계 9 |

E·P·S는 앞선 기계 판정 단계에서 이미 채워져 있다 — 이 단계에서는 남은 A/B/C/F만 판정하고,
E/P/S 결과는 집계에 합친다.

### 판정 기준

- **ERROR**: 하드웨어 손상 또는 동작 불가. 반드시 수정 필요.
- **WARN**: 동작은 하지만 잠재적 문제 또는 모범사례 미준수.
- **OK**: 이상 없음.
- **N/A**: 해당 회로에 적용 불가.

---

## 단계 9: 데이터시트 비교 검증

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

## 단계 10: BOM 마크다운 생성

### 1차 소스: 회로도 BOM

회로도 BOM은 **`export_sch_bom`**(MCP) 또는 그것이 감싸는 `kicad-cli sch export bom`으로 뽑는다.
`export_bom`(접미어 없음)은 **열린 보드 기준**이라 회로도 리뷰 시점에는 보드가 없을 수 있으므로 쓰지 않는다.

#### 1단계: 회로도가 실제로 쓰는 필드명을 먼저 찾는다

**`--fields`에 필드명을 하드코딩하면 안 된다.** `Manufacturer` / `MPN` / `LCSC`는 KiCad 관례일 뿐이고,
실무 회로도는 SnapEDA·Ultra Librarian·사내 라이브러리마다 다른 이름을 쓴다. 없는 이름을 요청하면
kicad-cli는 오류 없이 **빈 열**을 내주므로, 조달 정보가 통째로 사라져도 아무 신호가 없다.

> 비유: 창고에 "제조사"라고 적힌 서랍이 없는데 "제조사 서랍을 비워 오라"고 시킨 셈이다.
> 빈손으로 돌아와도 심부름은 "성공"으로 보고된다.

```bash
# 넷리스트에서 값이 채워진 커스텀 필드명과 그 빈도를 뽑는다
python3 -c "
import xml.etree.ElementTree as ET, collections, sys
r = ET.parse(sys.argv[1]).getroot(); c = collections.Counter()
for comp in r.findall('.//comp'):
    for f in comp.findall('.//field'):
        if (f.text or '').strip(): c[f.get('name')] += 1
for name, n in sorted(c.items(), key=lambda x: -x[1]): print(f'{n:5d}  {name}')
" /tmp/netlist.xml
```

이 목록에서 **제조사·파트넘버·유통사 코드로 보이는 이름을 골라 `--fields`에 추가한다.**
표준 이름(`Manufacturer`, `MPN`, `LCSC`)은 다른 회로도와의 호환을 위해 그대로 두고 **뒤에 덧붙인다**.
매핑은 보고서에 **"필드 매핑: `MANUFACTURER` → Manufacturer, `Manufacturer_Part_Number` → MPN"** 처럼 남긴다.

| 실제로 만나는 이름 | 매핑할 표준 열 |
|---|---|
| `MANUFACTURER`, `Manufacturer_Name`, `MFR`, `Mfr` | Manufacturer |
| `Manufacturer_Part_Number`, `MFR_PN`, `PartNumber`, `SNAPEDA_PN`, `MPN` | MPN |
| `LCSC`, `LCSC Part #`, `JLCPCB` | LCSC |
| `Mouser Part Number`, `Arrow Part Number`, `Digikey` | (유통사 열 — 별도로 둔다) |

**실측(이 스킬 검증 보드).** 실제 필드는 `MANUFACTURER`(29) / `Manufacturer_Name`(16) /
`Manufacturer_Part_Number`(16) / `Manufacturer`(1) / `MPN`(1)이고 `LCSC`는 0건이었다.
하드코딩된 이름 그대로 돌리면 **363개 부품 중 제조사 정보가 회수된 것은 1건**,
탐지한 실제 필드명을 넣으면 **46건**이다.

#### 2단계: 탐지한 필드명으로 내보낸다

```bash
# 탐지 결과를 반영한 예 (이 보드의 경우)
kicad-cli sch export bom \
  --fields 'Reference,Value,Footprint,MANUFACTURER,Manufacturer_Name,Manufacturer_Part_Number,MPN,LCSC,Datasheet,${QUANTITY},${DNP}' \
  --labels 'Reference,Value,Footprint,Manufacturer,Manufacturer2,MPN_vendor,MPN,LCSC,Datasheet,Qty,DNP' \
  --group-by 'Value,Footprint' \
  --ref-range-delimiter '~' \
  --output /tmp/bom.csv \
  "$ROOT_SCH"
```

- MCP `export_sch_bom`은 같은 플래그를 `fields` / `labels` / `groupBy` / `refRangeDelimiter`로 받고,
  **결과로 파일 경로만 돌려준다** — 이어서 CSV를 Read해야 한다.
  실측에서 kicad-cli 출력과 **바이트 단위로 동일**했다.
- `--fields`와 `--labels`는 **개수가 같아야 한다.** 같은 열로 매핑되는 두 벤더 필드는 라벨을
  구분해 두고(예: `Manufacturer` / `Manufacturer2`) 후처리에서 하나로 합친다.
- `QUANTITY` / `DNP` / `EXCLUDE_FROM_BOM` 같은 생성 필드는 `${}` 유무 상관없이 인식된다
  (실측: `kicad-cli sch export bom --help`).
- `--exclude-dnp`(MCP `excludeDnp`)는 DNP를 **삭제**하므로 쓰지 않는다.
  DNP 열을 함께 뽑아 후처리로 별도 테이블에 분리한다.
- 카테고리 분류(IC/커패시터/…)와 한글 요약표는 후처리다.

#### 3단계: BOM 제외 부품을 회수한다

회로도에서 `(in_bom no)`로 표시된 심볼은 kicad-cli BOM에 **소리 없이 빠진다.**
`--include-excluded-from-bom` 플래그는 **KiCad 10.0.0에서 폐기돼 아무 효과가 없다**
(실측: `--help`에 "Deprecated. Has no effect."). 즉 kicad-cli/MCP로는 되살릴 수 없다.

**규칙**: 넷리스트 XML의 부품 수와 BOM 행 수량 합계를 대조하고, 차이가 있으면
넷리스트에서 제외 부품을 직접 뽑아 **"BOM 제외로 표시된 부품" 별도 표**로 싣는다.
본 파트리스트에는 섞지 않는다 — 발주 대상이 아니면서 실물로 존재하는 항목이기 때문이다.

```bash
python3 -c "
import xml.etree.ElementTree as ET, sys
r = ET.parse(sys.argv[1]).getroot(); comps = r.findall('.//comp')
ex = [(c.get('ref'), c.findtext('value',''))
      for c in comps if c.find('property[@name=\"exclude_from_bom\"]') is not None]
print(f'넷리스트 부품 {len(comps)} / BOM 제외 표시 {len(ex)}')
for ref, val in ex: print('  ', ref, val)
" /tmp/netlist.xml
```

**실측**: 넷리스트 371부품 vs BOM 수량 합계 363 → 차이 8건이 전부 `exclude_from_bom`
(1 mm 마운팅 홀 `+3V1`/`GND1~3`/`TCK1`/`TDI1`/`TDO1`/`TMS1`)이었고,
정답지 BOM에는 실장 항목으로 올라 있었다. 이 표가 없으면 8개 부품이 발주에서 통째로 빠진다.

**판정**: 제외 부품이 순수 도면 표기(전원 심볼·시트 표기)면 INFO, 실물이 존재하는 기구 부품
(마운팅 홀·스페이서·나사)이면 **WARN — "BOM 제외 표시지만 실물 부품일 수 있다"** 로 낸다.

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

> 주의: 이 BOM은 MPN 부재로 발주에 쓸 수 없다. (MPN 필드가 없을 때만 이 줄을 넣는다)

## 상세 파트리스트

| # | Reference | Value | Footprint | Qty | Manufacturer | MPN | LCSC | Description | Datasheet |
|---|-----------|-------|-----------|-----|--------------|-----|------|-------------|-----------|
| 1 | U1 | XC7A200T-2FBG484I | BGA-484 | 1 | AMD/Xilinx | XC7A200T-2FBG484I | | Artix-7 FPGA | [Link](...) |
| 2 | U2, U3 | DP83848CVV | LQFP-48 | 2 | TI | DP83848CVV/NOPB | | 10/100 Ethernet PHY | [Link](...) |
| 3 | U4 | W25Q128JVS | WSON-8 | 1 | Winbond | W25Q128JVSIQ | C97521 | 128Mbit SPI Flash | [Link](...) |
| 4 | C1~C20 | 100nF | 0402 | 20 | | | | 디커플링 캡 | - |
| 5 | C21~C24 | 10μF | 0805 | 4 | | | | 벌크 캡 | - |
| ... | | | | | | | | | |

## DNP (Do Not Place)

| Reference | Value | 사유 |
|-----------|-------|------|
| R99 | 0Ω | 옵션 미실장 |
```

### BOM 생성 규칙

- **`Manufacturer` / `MPN` / `LCSC` 열은 항상 둔다.** 회로도에 해당 필드가 없으면 빈 칸으로 남긴다 —
  열을 없애면 "이 BOM에 조달 정보가 빠져 있다"는 사실 자체가 보이지 않는다.
  **단, 비어 있다고 단정하기 전에 위 1단계의 필드 탐지를 반드시 먼저 돌린다** — 이름만 다를 뿐
  정보가 있는 경우가 실무에서는 더 흔하다.
- **그룹 키**: 회로도에 `MPN` 필드가 있으면 **MPN이 그룹 키**다. 없으면 `Value + Footprint`로 두되,
  BOM 머리에 **"MPN 부재 — 발주용 아님"** 을 명시한다.
  이유: `100nF 0402 16V X7R`과 `100nF 0402 50V X5R`은 `Value + Footprint`가 같아 한 행으로 합쳐지지만
  서로 다른 부품이다. 실무 BOM의 그룹 키는 MPN(또는 LCSC)이다.
- Reference 목록은 자연 정렬 (C1, C2, ..., C10, C11)
- DNP 마킹된 부품은 별도 테이블로 분리
- 가상 부품(전원 심볼·시트 표기)은 BOM에서 제외한다. **접두어(`#PWR`, `TP`)로 거르지 않는다** —
  실무 회로도의 전원/홀 심볼은 `+3V1`, `GND1`, `TCK1` 처럼 접두어 규칙을 따르지 않는 이름이 흔하다.
  판정 기준은 넷리스트의 `exclude_from_bom` 속성이고, 제외한 것은 3단계의 별도 표로 남긴다
- 데이터시트 URL이 있으면 링크 포함

### `--sourcing` 옵트인: 조달 열 추가

기본 동작이 아니다. 사용자가 `--sourcing`을 붙였을 때만, 그리고 MCP가 등록돼 있을 때만 수행한다.

| 열 | 도구 | 조건 |
|----|------|------|
| 단가(1개) · 재고 · Basic/Extended | `get_jlcpcb_part`(`lcsc_number`) | 행에 LCSC 필드가 있을 때 |
| (LCSC 매핑) | `search_jlcpcb_parts`(`query`=MPN, `package`, `limit`) | LCSC가 없고 MPN만 있을 때 — 1홉 추가 |
| 대체 후보 | `suggest_jlcpcb_alternatives`(`lcsc_number`, `limit`) | 재고 0 또는 Extended 행에만 |
| Datasheet 빈칸 채움 | `get_datasheet_url`(`lcsc`) | LCSC가 있고 Datasheet가 비었을 때 |

**전제와 비용을 먼저 사용자에게 알린다.**

- JLCPCB 스냅샷 DB를 먼저 내려받아야 한다(`download_jlcpcb_database`, 약 465 MB).
  API 자격증명이 설정돼 있으면 실시간 조회, 없으면 스냅샷이며 스냅샷은 수일~수주 지연될 수 있다.
  결과의 `source` 필드가 `live-api`인지 `local-db`인지 보고서에 적는다.
- **행당 1호출**이다. 50행이면 50호출 — 큰 BOM에서는 IC와 발주가 필요한 행으로 대상을 좁힌다.
- `search_jlcpcb_parts`로 MPN→LCSC를 매핑하면 **패키지가 다른 동일 MPN에 잘못 붙을 수 있다.**
  매핑으로 얻은 LCSC는 "미검증 매핑"으로 표기한다.
- `get_datasheet_url`은 **LCSC 번호 전용**이다. 네트워크 호출 없이
  `https://www.lcsc.com/datasheet/C<번호>.pdf` 문자열을 조립할 뿐이라 PDF 존재를 검증하지 않는다.
  제조사 원본 데이터시트가 우선이며, 이 URL은 필드 URL 다음 순위다.
- `suggest_jlcpcb_alternatives` 결과는 제안일 뿐 검증이 아니다 — "미검증 후보"로 표기한다.

**N/A 규칙**: DB가 없거나 자격증명이 없거나 조회에 실패하면 해당 열 전체를 `N/A`로 채우고
BOM 머리에 사유를 한 줄 적는다. 조달 열이 비어 있는 것과 조회에 실패한 것을 구분한다.

`enrich_datasheets`는 **회로도 파일을 수정하므로 이 스킬에서 호출하지 않는다.**

---

## 단계 11: 종합 리뷰 보고서

### 보고서 템플릿

```
═══════════════════════════════════════════
  KiCad 회로도 리뷰 보고서
═══════════════════════════════════════════

프로젝트: {프로젝트명}
회로도: {파일 목록}
리비전: {rev}
검증일: {날짜}

판정 엔진: {MCP / kicad-cli / 텍스트 추론 모드}
  ERC: {수행 / 미수행 — 사유}   구조 린트: {수행 / 미수행 — 사유}

━━━ 리뷰 요약 ━━━

  [기계 판정]
  E. ERC 수준:        OK {n} / WARN {n} / ERROR {n}
  P. 풋프린트 해석:    OK {n} / WARN {n} / ERROR {n}
  S. 구조 린트:        OK {n} / WARN {n} / ERROR {n}

  [사람 판정]
  V. 시각 검토:        OK {n} / WARN {n} / ERROR {n}
  L. 라이브러리 핀:    OK {n} / WARN {n} / ERROR {n}
  A. 전원 설계:       OK {n} / WARN {n} / ERROR {n}
  B. 핀 연결 완전성:   OK {n} / WARN {n} / ERROR {n}
  C. 신호 무결성:      OK {n} / WARN {n} / ERROR {n}
  D. 데이터시트 정합:  OK {n} / WARN {n} / ERROR {n}
  F. 도메인별 검증:    OK {n} / WARN {n} / ERROR {n}

  종합: OK {n} / WARN {n} / ERROR {n}

━━━ ERROR 항목 ━━━

  [ERROR] {ID} — {설명}
     위치: {서브시트} / {부품 레퍼런스}
     원인: {근거 — 데이터시트 섹션/페이지 참조}
     조치: {구체적 수정 방법}

━━━ WARN 항목 ━━━

  [WARN] {ID} — {설명}
     위치: {서브시트}
     사유: {근거}
     권장: {개선 방법}

━━━ 데이터시트 비교 결과 ━━━

  [{IC 파트넘버}]
    데이터시트: {URL 또는 출처}
    권장 회로 대조:
      바이패스 캡 배치 — OK
      REXT 저항 누락 — ERROR
      전원 핀 연결 — OK
    정격 검증:
      VCC 범위: {min}~{max}V, 설계 전압: {actual}V — OK/ERROR

━━━ 풋프린트 해석 결과 ━━━

  전수 {n}개 중 미해석 {n}개
    {Reference} — {Lib:Name} — {빈 필드 / nickname 미등록 / .kicad_mod 부재}
  (미해석이 남아 있으면 Update PCB 가 그 부품에서 실패한다)

━━━ BOM 요약 ━━━

  총 {n}종 / {n}개 부품
  그룹 키: {MPN / Value+Footprint (MPN 부재 — 발주용 아님)}
  조달 열: {--sourcing 수행 (source: live-api|local-db) / 미수행}
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

- stm32f4 플러그인이 설치돼 있으면 그 플러그인의 `kicad-stm32-review` 스킬(42항목 체크리스트)을 함께 참조한다 — 이 플러그인 단독으로는 존재하지 않는다
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

- **kicad-schematic-reviewer**: 단계 1~9 — ERC·풋프린트 해석·구조 린트·시각 검토·라이브러리 핀 대조 +
  체크리스트 적용 + 데이터시트 비교 + 리뷰 보고서 작성
- **kicad-bom-generator**: 단계 10 — 회로도 BOM 추출 + 조달 열(`--sourcing`) + 마크다운 포맷팅

두 에이전트 모두 **읽기 전용**이다. `Write`는 보고서·BOM 파일용이고 `.kicad_sch`에는 쓰지 않는다.
`lint_offgrid`의 `fix`, `enrich_datasheets`, `snap_to_grid`는 호출하지 않는다.

에이전트는 `kicad-setup` 스킬로 타겟 프로젝트의 `.claude/agents/`에 설치한다.

### 다른 스킬과의 경계

| 작업 | 담당 |
|------|------|
| 회로도 ERC · 풋프린트 해석 · 구조 린트 · 회로도 설계 리뷰 · 데이터시트 대조 · BOM | **이 스킬(kicad-review)** |
| PCB 물리 레이아웃 · DRC · 트랙/비아 기하 · 넷별 라우팅 추적 · SI/PI | `kicad-analyze` |
| 회로도 생성(PRD/설계사양서 → `.kicad_sch`) | `kicad-design` |
| KiCad 사용법 Q&A (GUI 조작·kicad-cli 명령) | `kicad-usage` |
| MCP 도구 카탈로그·폴백 체인 정본 | `kicad-analyze/references/mcp-tools.md` |

---

## 사용 예시

```
사용자: "이 KiCad 회로도 리뷰해줘"
사용자: "hw/kicad 폴더의 회로도 검토하고 BOM 만들어줘"
사용자: "이 보드에 사용된 IC들 데이터시트 확인해서 문제 없는지 봐줘"
사용자: "파트리스트 마크다운으로 뽑아줘"
```

$ARGUMENTS
