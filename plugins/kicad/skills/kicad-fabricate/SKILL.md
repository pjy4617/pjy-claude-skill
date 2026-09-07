---
name: kicad-fabricate
description: "DRC 통과를 게이트로 KiCad 보드(.kicad_pcb)에서 제조 데이터 일습을 뽑습니다 — 거버(RS-274X/X2), 드릴(Excellon PTH/NPTH + 맵), 위치 파일(pick and place), IPC-D-356 전기 테스트 넷리스트, 발주용 BOM. '제조 출력', '거버 뽑아줘', '거버 생성', '거버 내보내기', '드릴 파일', '위치 파일', 'pick and place', 'CPL 파일', 'IPC-D-356', '팹 출력', '제조 파일 만들어', 'JLCPCB 발주 파일', 'PCBWay 파일', 'fabrication', 'gerber export', 'drill export' 등의 요청에 자동 적용. ※ DRC/ERC 판정·넷 추적·SI/PI 같은 *분석*은 kicad-analyze, 회로도 *설계 적정성*과 리뷰용 BOM은 kicad-review, 회로도 *생성*은 kicad-design을 쓴다 — 이 스킬은 '이미 배선이 끝난 보드에서 팹에 넘길 파일을 만든다'만 담당한다."
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep, Agent
---

# KiCad 제조 출력 — 거버/드릴/위치/IPC-D-356/BOM

> 이 스킬은 **배선이 끝난 보드**에서 팹(PCB 제조사)과 조립사에 넘길 파일을 만든다.
> 한 줄로: DRC 에러 0을 게이트로 두고, 존 채움과 회로도-보드 동기화를 확인한 뒤,
> 거버 → 드릴 → 위치 파일 → BOM 순으로 뽑고 산출물을 검증한다.
> 비유하면 **원고 교정이 끝난 책을 인쇄소에 넘기기 전 최종 파일 묶음을 싸는 작업**이다.

## 다른 스킬과의 경계

| | kicad-design | kicad-review | kicad-analyze | **kicad-fabricate (이 스킬)** |
|---|---|---|---|---|
| 입력 | PRD/사양서 | `.kicad_sch` | `.kicad_sch` + `.kicad_pcb` | **`.kicad_pcb` + `.kicad_sch`** |
| 하는 일 | 회로도 생성 | 설계 적정성·데이터시트·리뷰 BOM | ERC/DRC·넷 추적·배치·SI/PI 분석 | **팹 산출물 생성·검증** |
| 출력 | `.kicad_sch` | 리뷰 보고서 + 마크다운 BOM | 분석 보고서 | **거버·드릴·위치·IPC·발주 BOM + 검증 리포트** |

DRC 를 **판정**하는 것은 kicad-analyze 다. 이 스킬은 그 판정을 **게이트로 쓴다** — 통과하지 못하면 아무것도 뽑지 않는다.

---

## 워크플로우 개요

```
[0] 전제 확인 — kicad-cli, GUI 저장 여부, 산출물 디렉토리
 ↓
[1] DRC 게이트 — error 0 이 아니면 중단
 ↓
[2] 존 채움 확인 — 구리 존만 대상(keepout 제외). 미채움이면 채워 저장(사용자 동의)
 ↓
[3] 회로도-보드 동기화 확인 — 패리티 + IPC-D-356 ↔ 넷리스트 diff
 ↓
[4] 거버 (팹 프로파일별 레이어 세트)
 ↓
[5] 드릴 (PTH/NPTH 분리 + 맵)
 ↓
[6] 위치 파일 (SMD only, DNP 제외, 드릴 원점)
 ↓
[7] BOM (발주용 — MPN/LCSC 열)
 ↓
[8] 산출물 목록 · 체크섬 · 팹 전달 패키지(zip) · 검증 리포트
```

각 단계에 MCP(KiCAD-MCP-Server) 대응 도구를 병기한다. **기본 경로는 kicad-cli 직접 호출**이다 —
MCP `export_gerbers`(복수형)는 서버 기본 예산 30초로 돌아(600초 목록에 `export_gerber` 단수형만 있다) **매우 큰 보드에서는** 타임아웃될 수 있다.
다만 2.3 MB · 356 풋프린트 · 1410 패드 규모에서는 두 경로가 동등했다(실측: MCP 즉시 완료, kicad-cli 0.26초, 산출물은 생성 시각 주석 한 줄 외 동일).
kicad-cli 를 기본으로 두는 이유는 "MCP 가 느려서" 가 아니라 **팹 프로파일 옵션을 전부 넘길 수 있고 실패 모드가 단순해서**다. MCP 로 뽑다가 실패하면 kicad-cli 로 폴백한다.

---

## 단계 0: 전제 확인

```bash
# 1) kicad-cli 필수 — 이 스킬의 모든 산출물이 kicad-cli 를 거친다
kicad-cli version || { echo "kicad-cli 없음 — 제조 출력 불가"; exit 1; }

# 2) kicad-cli 메이저가 보드 포맷 세대 이상인지
grep -m1 -o '(version [0-9]*)' "$PCB"

# 3) 대상 파일
ls "$PCB" "$SCH"

# 4) 보드와 짝이 되는 회로도가 있는가 — 패리티 검사(단계 3.1)의 전제
PAIR="$(dirname "$PCB")/$(basename "$PCB" .kicad_pcb).kicad_sch"
ls "$PAIR" 2>/dev/null || echo "짝 회로도 없음 — 패리티가 무음으로 미수행된다(단계 3.1 참조)"

# 5) 보드 파일명에 공백이 있는가 — 산출물 파일명이 이 이름을 그대로 따른다
case "$(basename "$PCB")" in *\ *) echo "보드 파일명에 공백 있음 — 단계 8 에서 파일명 정리 필요";; esac

# 6) 보조 원점(드릴/배치 원점)이 보드에 설정돼 있는가
grep -c 'aux_axis_origin' "$PCB"
```

체크 항목:

- **kicad-cli 필수.** MCP 를 쓰더라도 내부에서 kicad-cli 를 부른다. 없으면 이 스킬은 시작하지 않는다.
- **보드와 루트 회로도의 베이스명이 같은지 확인한다.** kicad-cli 는 `<보드 베이스명>.kicad_sch` 를 짝으로 찾는다.
  이름이 다르면 패리티는 **stderr 경고 한 줄만 남기고 JSON 에는 빈 배열**을 넣는다 — JSON 만 읽는 자동화는 이것을 통과로 오독한다.
  실측 예: `… Module_Rev_0.4.kicad_pcb`(언더스코어) ↔ `… Module(Rev_0.4).kicad_sch`(괄호) → 패리티 0건.
  베이스명을 맞춘 사본으로 재실행하니 **431건**이 나왔다. 조치 절차는 단계 3.1 에 있다.
- **보드 파일명의 공백을 확인한다.** 거버·드릴 파일명은 보드 파일명을 그대로 따르므로, 보드명에 공백이 있으면
  산출물 전부에 공백이 들어간다. 팹 CAM 업로드에서 거부되는 흔한 사유이며, 단계 8 에서 정리한다.
- **보조 원점(`aux_axis_origin`) 존재를 확인한다.** 0 이면 `--use-drill-file-origin` / `--drill-origin plot` 이
  모두 절대 원점(0,0)으로 폴백한다. 세 산출물의 원점은 여전히 서로 일치하지만 좌표가 보드 실제 위치로 나오므로,
  검증 리포트에 **"보조 원점 미설정 — 절대 원점 사용"** 을 명시한다(실측: 이 보드는 0건, 거버 X177.165 mm / 드릴 X180.6 mm 로 같은 절대 좌표계).
- **GUI 에서 저장했는지 사용자에게 묻는다.** 모든 export 는 **디스크에 마지막으로 저장된 `.kicad_pcb`** 를 읽는다.
  KiCad GUI 에서 배선하고 저장(Ctrl+S)하지 않았으면 낡은 보드가 팹에 넘어간다.
  MCP `is_dirty` 는 **서버 메모리 상태만** 보며 GUI 의 미저장 편집을 감지하지 못한다 — 저장 확인 수단으로 쓰지 않는다.
- **산출물 디렉토리는 사용자가 지정한다.** 임의로 프로젝트 루트에 쏟지 않는다.
  권장 형태: `fab/<프로젝트명>_rev<리비전>_<YYYYMMDD>/` 아래 `gerber/`, `drill/`, `assembly/`.
- **보드 리비전을 확인한다.** 산출물 디렉토리 이름과 검증 리포트에 리비전을 적어, 다음 발주 때 어느 파일이 어느 리비전인지 섞이지 않게 한다.

---

## 단계 1: DRC 게이트

**error 가 하나라도 있으면 여기서 중단한다.** 제조 출력은 "DRC 통과한 보드" 에서만 의미가 있다.

```bash
# 게이트용 — 사용자가 KiCad 에서 등록한 DRC 예외(exclusion)를 제외한다
kicad-cli pcb drc --format json --severity-error --severity-warning --schematic-parity \
  --output "$OUT/drc.json" "$PCB"

# 리포트용(선택) — 예외까지 포함한 전체 목록. 게이트 판정에는 쓰지 않는다
kicad-cli pcb drc --format json --severity-all --schematic-parity \
  --output "$OUT/drc-all.json" "$PCB"
```

**`--severity-all` 을 게이트에 쓰지 않는다.** `--severity-all` 은 `included_severities` 가
`['error','warning','exclusion']` 이 되어 **설계자가 검토 후 명시적으로 수용한 위반까지 포함**한다.
그런데 JSON violation 객체의 키는 `description`/`items`/`severity`/`type` 뿐이라 **제외 여부를 표시하는 필드가 없다** —
"수용된 위반" 과 "살아 있는 위반" 을 구분할 수 없고, 전자도 error 로 세어 완성 보드가 막힌다.
`--severity-error --severity-warning` 으로 돌리면 `included_severities` 가 `['error','warning']` 이 된다(kicad-cli 10.0.6 실측).
DRC 예외는 `.kicad_pro` 의 `board.design_settings.drc_exclusions` 배열에 남으므로, 예외 등록 자체가 감사 기록이 된다.

**이 명령의 exit code 는 위반 유무와 무관하게 0 이다**(실측: 위반 514건에도 rc=0).
반드시 JSON 을 파싱해 판정한다. 셸 게이트가 필요하면 `--exit-code-violations` 를 함께 준다.

JSON 최상위에 판정 배열이 **세 개** 있다. 셋 다 봐야 한다.

| 키 | 의미 | 게이트 |
|----|------|--------|
| `violations` | 일반 DRC 위반(clearance, 홀, 실크 등) | `severity == "error"` 가 1건이라도 있으면 중단 |
| `unconnected_items` | 미배선 넷(래츠네스트 잔존) | 1건이라도 있으면 중단 — 배선이 안 끝난 보드다 |
| `schematic_parity` | 회로도와 보드의 불일치 | **severity 가 아니라 `type` 으로 판정한다** — 아래 표 |

### 패리티 게이트는 severity 로 판정하지 않는다

KiCad 10.0.6 은 패리티 문제를 **전부 `warning` 으로 낸다**. 실측: 이 검사의 존재 이유인
"Update PCB(F8) 를 안 돌린 보드" 431건이 전수 warning 이었다(`net_conflict` 185, `footprint_symbol_mismatch` 94,
`missing_footprint` 70, `duplicate_footprints` 34, `footprint_symbol_field_mismatch` 26, `extra_footprint` 22).
severity 기준 게이트는 **사실상 절대 발동하지 않는다.** 그래서 `type` 으로 판정한다.

| `type` | 판정 | 해석 |
|--------|------|------|
| `missing_footprint` | **중단** | 회로도 부품이 보드에 없다 — F8 미실행 |
| `extra_footprint` | **중단** | 보드에만 있는 부품 — 회로도에서 지운 부품이 남아 있다 |
| `net_conflict` | **중단** | 패드 넷이 회로도 넷과 다르다 — 배선이 회로도와 어긋난다 |
| `duplicate_footprints` | **중단** | 같은 레퍼런스가 보드에 둘 이상 — 조립이 불가능하다 |
| `footprint_symbol_mismatch` | 리포트 | 값/풋프린트 문자열 불일치. 발주 전 확인 항목으로 남긴다 |
| `footprint_symbol_field_mismatch` | 리포트 | 필드 값 불일치. 위와 같음 |

**`schematic_parity` 가 빈 배열이면 "통과" 가 아니라 "미수행" 이다.** 단계 0 의 베이스명 확인과 단계 3.1 을 따른다.

MCP 대응: 작은 보드는 `mcp__kicad__get_drc_violations`(`severity: "error"`) **하나만** 부른다(내부에서 DRC 를 돌린다).
큰 보드(4층·수백 부품)는 30초 예산을 넘기므로 `mcp__kicad__run_drc`(600초 목록)를 쓰고 결과 JSON 을 직접 거른다.
어느 쪽이든 판정 자체는 kicad-analyze 단계 4.4 와 같은 규약을 따른다 — 이미 kicad-analyze 를 돌렸으면 그 보고서를 게이트 근거로 재사용하고 DRC 를 두 번 돌리지 않는다.

DRC 판정과 위반 해석을 깊게 해야 하면 **kicad-pcb-analyzer 에이전트에 위임**한다(이 스킬 전용 에이전트는 없다 — 나머지 단계는 메인 세션에서 실행한다).

중단 시 보고 형식:

```
[중단] DRC 게이트 미통과 — error {n}건 / 미배선 {n}건 / 패리티 중단 사유 {n}건
  1. clearance: 넷 +3V3 ↔ GND 0.12mm (규칙 0.20mm) @ (45.2, 31.7)
  ...
  → 수정 후 다시 /kicad-fabricate 를 실행하세요.
  → 이 위반들이 설계 검토를 거쳐 수용된 것이라면, KiCad 에서 DRC 예외(Exclusion)로 등록한 뒤
    다시 실행하세요. 게이트용 DRC 는 예외를 세지 않으므로 정상 통과합니다.
```

**게이트를 인자로 끄는 경로는 두지 않는다.** 예외 등록을 거치게 하면 판단 근거가 `.kicad_pro` 에 남아
나중에 "누가 무엇을 수용했는가" 를 되짚을 수 있다. 스킬 인자로 끄면 그 기록이 남지 않는다.

---

## 단계 2: 존 채움

채워지지 않은 존은 **거버에 구리가 빠진 채로** 나간다. 보드가 통째로 못 쓰게 되는 대표적 사고다.

**단, 세는 대상은 구리 존뿐이다.** `.kicad_pcb` 의 `(zone ...)` 블록에는 구리 존과 **keepout(룰 영역) 존**이 섞여 있고,
keepout 존은 정의상 `filled_polygon` 을 갖지 않는다. `(zone` 을 통째로 세면 **모든 keepout 보드에서 100% 오탐**이 난다.
실측: 이 보드는 `(zone` 245개 / `filled_polygon` 0개라 나이브 판정으로는 "미채움 245개" 지만,
245개가 전부 keepout(`copperpour not_allowed`)이고 **구리 존은 0개**다. 이 오탐을 따르면 사용자에게 불필요한
동의를 구하고, 동의 시 `--refill-zones --save-board` 로 **멀쩡한 원본 보드를 무의미하게 덮어쓴다.**

확인 (1차 수단은 MCP 다 — keepout 을 이미 제외해서 돌려준다):

- MCP: `mcp__kicad__query_zones` → `zoneCount` 는 **구리 존 수**다. 존별 `isFilled` 를 본다(false 면 `filledArea` 자체가 없다).
  실측: 이 보드에서 `{"zoneCount": 0, "zones": []}` — 파일 파싱보다 정확하다.
- MCP 를 못 쓸 때의 파일 파싱: **`(keepout ...)` 을 포함하지 않는 zone 블록만 구리 존으로 센다.**

```bash
# 구리 존 / 채워진 구리 존 수 — keepout 제외. KiCad 파일은 CRLF 일 수 있어 \r 를 먼저 지운다
awk '
  { sub(/\r$/, "") }
  /^[[:space:]]*\(zone$/ { inzone=1; depth=0; keep=0; filled=0 }
  inzone {
    depth += gsub(/\(/,"(") - gsub(/\)/,")")
    if ($0 ~ /\(keepout/)        keep=1
    if ($0 ~ /\(filled_polygon/) filled=1
    if (depth<=0) { total++; if (keep) ko++; else { cu++; if (filled) cuf++ }; inzone=0 }
  }
  END { printf "zone %d / keepout %d / copper %d / copper-filled %d\n", total+0, ko+0, cu+0, cuf+0 }
' "$PCB"
```

판정:

- **구리 존 0개면 "해당 없음" 으로 넘어간다.** 채울 것이 없으므로 refill 을 제안하지도 않는다.
- 구리 존 > 0 이고 `copper-filled` < `copper` 일 때만 미채움이다.
- `grep -c 'filled_polygon'` 로 채움 여부를 판정하지 않는다 — 존 하나가 `filled_polygon` 블록을 여럿 가질 수 있어
  존 수와 대응하지 않는다(실측: 구리 존 9개인 보드에서 `filled_polygon` 231줄).

미채움 존이 있으면 **사용자 동의를 받은 뒤** 채워 저장한다.

```bash
# 원본 .kicad_pcb 를 덮어쓴다 — KiCad GUI 에서 그 보드가 닫힌 상태에서만 실행
kicad-cli pcb drc --refill-zones --save-board --format json \
  --output "$OUT/drc-refilled.json" "$PCB"
```

- `--save-board` 는 `--refill-zones` 와 함께만 쓴다(도움말: "must be used with --refill-zones").
  단독으로 주면 **에러가 아니라 조용히 무시된다**(실측: rc=0, 보드 md5 불변). 즉 "저장했다" 는 착각을 남긴다.
- 저장 후에는 DRC 결과가 달라질 수 있으므로 **단계 1 을 다시 판정한다**.
- MCP 를 쓰고 있었다면 `mcp__kicad__reload_board` 로 갱신한다.
- **MCP `refill_zones` 는 호출하지 않는다** — SWIG 세그폴트로 파이썬 브리지가 죽고, 죽은 브리지는 자동으로 살아나지 않는다.
- 사용자가 보드 덮어쓰기에 동의하지 않으면: KiCad 10.0 의 `kicad-cli pcb export gerbers --check-zones` 로
  **플롯할 때만 존을 채워** 거버를 뽑을 수 있다(보드 파일은 그대로). 다만 이 경우 보드에 저장된 존 상태와 거버가 달라지므로
  검증 리포트에 "존은 플롯 시점에만 채움 — 보드 파일 미갱신" 을 명시한다.

---

## 단계 3: 회로도-보드 동기화 확인

"회로도는 고쳤는데 Update PCB(F8)를 안 돌린 보드" 를 걸러내는 단계다. 두 겹으로 본다.

### 3.1 패리티 (1차, 저렴)

단계 1 의 `--schematic-parity` 결과(`schematic_parity` 배열)를 그대로 쓰고, **판정은 단계 1 의 `type` 표**를 따른다.
`footprint_symbol_mismatch`(회로도 Footprint 필드 ≠ 보드 풋프린트), 넷 불일치, 보드에 없는 부품이 여기로 나온다.

**빈 배열은 통과가 아니라 미수행이다.** kicad-cli 는 **보드와 같은 디렉토리·같은 베이스명의 `.kicad_sch`** 를 짝으로 찾는다.
짝이 없으면 stderr 에 한국어 경고 한 줄("패리티 테스트를 위한 회로도 네트리스트를 가져오지 못함")만 흘리고
JSON 에는 `"schematic_parity": []` 를 넣는다 — **JSON 만 파싱하는 자동화는 이것을 0건 통과로 오독한다.**

짝이 없을 때의 조치 (원본은 건드리지 않는다):

```bash
PAIR="$(dirname "$PCB")/$(basename "$ROOT_SCH" .kicad_sch).kicad_pcb"
cp "$PCB" "$PAIR"                              # 루트 회로도와 같은 베이스명의 사본
kicad-cli pcb drc --format json --severity-error --severity-warning --schematic-parity \
  --output "$OUT/drc-paired.json" "$PAIR"
rm -f "$PAIR"                                  # 검사 후 사본 삭제 — 원본 불변
```

실측: 베이스명이 다른 상태로는 0건이었고, 사본으로 재실행하니 **431건**이 나왔다.
사본으로 검사했다면 검증 리포트에 "패리티: 베이스명 사본으로 검사" 를 한 줄 남긴다.
근본 해결은 보드와 루트 회로도의 베이스명을 맞추는 것이다 — 사용자에게 그 사실을 알린다.

### 3.2 IPC-D-356 ↔ 넷리스트 diff (2차, 독립 확인)

IPC-D-356 은 **보드에 실제로 존재하는 패드와 그 넷**을 적은 파일이다. 팹의 전기 테스트에도 그대로 넘어가므로,
어차피 만들어야 할 산출물을 동기화 확인에 재사용한다.

```bash
kicad-cli pcb export ipcd356 -o "$OUT/assembly/$NAME.ipc" "$PCB"
kicad-cli sch export netlist --format kicadxml -o "$OUT/netlist.xml" "$ROOT_SCH"
```

MCP 대응: `mcp__kicad__export_ipcd356`(`outputPath` 필수, `boardPath` 선택 — 생략하면 로드된 보드).
산출물 경로는 스크래치가 아니라 **팹에 넘길 디렉토리**로 잡는다(이 파일은 최종 산출물이기도 하다).

레코드 포맷(10.0.6 실측, 고정폭):

| 컬럼 | 내용 | 예 |
|------|------|-----|
| 1–3 | 레코드 코드 — `317` 스루홀 / `327` SMD | `327` |
| 4–17 | 넷 이름 (**14자**, 넘으면 **앞이 잘리고 뒤 14자**가 남음, **전부 대문자**) | `ET-(U25-ANODE)` |
| 18–20 | 공백 패딩 | (공백 3칸) |
| 21–26 | 레퍼런스 (6자) | `C1` |
| 27–30 | `-` + 핀 번호 | `-1` |
| 31– | 패드 기하(직경·좌표·회전) | `A01X+069940Y-024764...` |

**레코드 코드는 `317` 과 `327` 을 둘 다 센다.** IPC-D-356A 에서 `317` 은 스루홀 패드,
`327` 은 표면실장(SMD) 패드 테스트포인트다. SMD 가 대부분인 현대 보드에서 `317` 만 고르면 테스트포인트의 1% 만 본다.
실측(`cut -c1-3 board.ipc | sort | uniq -c`): `327` 1394행 / `317` 16행 / 합계 1410행.
`^317` 만 골랐을 때와 교정 후를 나란히 돌린 결과:

| diff 방법 | IPC 측 핀 수 | 회로도에만 | 보드에만 | 넷 불일치 |
|---|---|---|---|---|
| `^317` 만 | 14 | **1416** | 1 | 0 |
| `^317` + `^327` | 1347 | 167 | 85 | 94 |

`317` 만 세면 "회로도에만 1416핀" 이 되어 아래 판정표상 ERROR 다 — **동기화가 완벽한 보드에서도 무조건 중단한다.**

diff 방법:

1. IPC 파일에서 `^317` 과 `^327` 행을 골라 `(레퍼런스, 핀)` 집합과 `(레퍼런스, 핀) → 넷` 맵을 만든다.
   (셸이면 `grep '^3[12]7'` 로 두 코드를 한 번에 고른다.)
2. 넷리스트 XML 에서 같은 `(레퍼런스, 핀) → 넷` 맵을 만든다.
3. 비교 결과를 아래 등급으로 낸다.

| 차이 | 판정 | 해석 |
|------|------|------|
| 회로도에 있는 `(ref, 핀)` 이 보드에 없음 | **ERROR** | Update PCB 미실행 — 부품/핀이 보드에 올라가지 않았다 |
| 회로도와 보드의 넷 이름이 다름 | **ERROR** | 회로도 변경이 보드에 반영되지 않았다 |
| 보드에만 있는 `(ref, 핀)` | **WARN** | 보드에서 직접 추가한 부품(펜스 비아, 기구 홀 등)인지 확인 |
| IPC 넷 이름이 `N/C` | 정보 | 미연결 패드. 회로도에서도 미연결이면 정상 |

**넷 이름 비교는 "대문자 + 뒤 14자" 로 정규화해서 한다.** IPC 쪽은 넷 이름을 14자로 줄이는데,
**뒤를 자르는 것이 아니라 앞을 자르고 뒤 14자를 남긴다.** 실측: 회로도 `Net-(U25-ANODE)`(15자) → IPC `ET-(U25-ANODE)`(14자).
게다가 전부 대문자로 변환된다(실측: 1410행 중 소문자 포함 행 0). 따라서 비교 규칙은:

```python
norm = lambda s: s.upper()[-14:]     # 양쪽 모두에 적용
```

뒷자르기(`s[:14]`)로 구현하거나 대소문자를 구분하면 **전 행이 불일치로 나온다.**
넷 이름이 `N/C` 인 행은 미연결 패드이므로 넷 비교에서 제외한다.
정규화가 불안하면 `(ref, 핀)` 존재 여부를 1차 키로 삼고 넷 비교는 2차로 둔다.

ERROR 가 하나라도 있으면 **중단하고** 사용자에게 "KiCad 에서 Tools → Update PCB from Schematic(F8) 을 실행한 뒤 저장하세요" 를 안내한다.

---

## 단계 4: 거버

```bash
kicad-cli pcb export gerbers \
  --output "$OUT/gerber" \
  --layers "F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts" \
  --use-drill-file-origin \
  --subtract-soldermask \
  "$PCB"
```

MCP 대응: `mcp__kicad__export_gerbers`(`outputDir` 필수, `boardPath`·`layers`·`commonLayers`·`noX2`·`noNetlist`·
`useDrillFileOrigin`·`subtractSoldermask`·`precision`·`boardPlotParams`·DNP 옵션 4종).
**단, 30초 예산이라 큰 보드는 kicad-cli 직접이 기본이다.** MCP `export_gerber`(단수형)는 600초지만 옵션이 6개뿐이고
`boardPath` 를 받지 않아(로드된 보드만) 팹 프로파일을 못 맞춘다.

실측으로 확인된 함정 4가지 (kicad-cli 10.0.6):

1. **`--layers` 를 생략하면 사용 가능한 레이어를 전부 플롯한다.** Courtyard·Fab·Adhesive·Margin·User_* 까지 나와
   팹이 어느 파일이 구리인지 못 고른다. 레이어 세트는 **항상 명시**한다.
2. **`--common-layers`(`--cl`)는 별도 파일을 만들지 않는다.** 지정한 레이어를 *각 플롯 안에 겹쳐* 그린다.
   Edge.Cuts 를 독립 파일로 받으려면 `--layers` 쪽에 넣어야 한다.
3. **레이어 이름을 바꾼 보드는 출력 파일명도 바뀐다.** `F.Cu` 를 `Top` 으로 이름 바꾼 보드는 `*-Top.gtl` 로 나온다.
   `--layers` 에는 **표준 이름**(`F.Cu`, `B.Cu`, `In1.Cu` …)을 쓰는 것을 권장하되, kicad-cli 10.0.6 은 **개명된 이름도 받는다**
   (실측: `F.SilkS` 를 `F.Silkscreen` 으로 개명한 보드에 `--layers "F.Silkscreen"` 을 넘겨 정상 플롯).
   어느 쪽이든 파일명은 사용자 이름을 따르므로, 산출물 검증(단계 8)은 파일명 문자열이 아니라 **파일 수와 실제 목록**으로 한다.
4. **`.gbrjob` 이 항상 함께 나온다.** X2 잡 파일이며 스택업·재질 정보를 담는다. 팹이 요구하면 함께 보내고, 요구하지 않으면 빼도 된다.

레이어 세트와 X2 여부는 팹마다 다르다 — `references/fabrication-outputs.md` 의 팹 프로파일 표를 쓴다.
내층이 있으면 `In1.Cu,In2.Cu,…` 를 `--layers` 에 추가한다(보드의 실제 레이어 수는 `.kicad_pcb` 의 `(layers ...)` 로 확인).

---

## 단계 5: 드릴

```bash
kicad-cli pcb export drill \
  --output "$OUT/drill/" \
  --format excellon \
  --excellon-separate-th \
  --excellon-units mm \
  --excellon-zeros-format decimal \
  --drill-origin plot \
  --generate-map --map-format gerberx2 \
  "$PCB"
```

MCP 대응: `mcp__kicad__export_drill`(`outputDir` 필수, `format`·`drillOrigin`·`excellonZerosFormat`·`excellonOvalFormat`·
`excellonUnits`·`excellonSeparateTh`·`generateMap`·`mapFormat`·`gerberPrecision`).

- `--excellon-separate-th` 로 **PTH 와 NPTH 를 분리**한다. 산출물은 `<보드명>-PTH.drl`, `<보드명>-NPTH.drl`.
  분리하지 않으면 도금 홀과 비도금 홀이 한 파일에 섞여 팹이 도금 여부를 되묻는다.
- `--generate-map` 은 홀 크기별 기호를 그린 **드릴 맵**을 낸다(`*-PTH-drl_map.gbr` 등). 사람이 검산하는 용도다.
- **`--drill-origin` 은 단계 4·6 과 반드시 같은 원점을 쓴다.** `plot`(드릴/배치 원점)으로 통일하면
  거버(`--use-drill-file-origin`)·드릴·위치 파일의 좌표계가 하나로 맞는다. 섞이면 조립 좌표가 통째로 어긋난다.
  단계 0 에서 `aux_axis_origin` 이 0 이었으면 세 옵션 모두 **절대 원점(0,0)으로 폴백**한다 —
  서로는 일치하지만 좌표가 보드 실제 위치로 나오므로 리포트에 그 사실을 적는다.
- **NPTH 가 0홀이면 빈 파일(헤더 + `M30`)이 나온다.** 기구 홀이 정말 없는 보드인지 확인하고,
  맞으면 **전달 zip 에 넣지 않는다**(단계 8). 실측: 이 보드는 PTH 16홀 / NPTH 0홀이었고,
  회로도의 `Hole(1mm)` 심볼 8개가 풋프린트 미배정이라 보드에 오르지 않은 것이 원인이었다 — 이런 경우는 리포트에 결함으로 적는다.
- `--excellon-units` 기본값은 `mm`, 위치 파일 `--units` 기본값은 `in` 이다 — **두 기본값이 다르다.** 명시적으로 맞춘다.

---

## 단계 6: 위치 파일 (pick and place)

```bash
kicad-cli pcb export pos \
  --output "$OUT/assembly/$NAME-top-pos.csv" \
  --format csv --units mm --side both \
  --smd-only --exclude-dnp --use-drill-file-origin \
  "$PCB"
```

MCP 대응: `mcp__kicad__export_pos`(`outputPath` 필수, `side`·`format`·`units`·`bottomNegateX`·`useDrillFileOrigin`·
`smdOnly`·`excludeFpTh`·`excludeDnp`·`gerberBoardEdge`).

- 기본 출력 헤더(10.0.6 실측): `Ref,Val,Package,PosX,PosY,Rot,Side` — **7열**.
- 조립사 템플릿이 다르면 **열을 삭제·재배치**해야 한다. 헤더 행만 바꾸면 열 수가 안 맞는 파일이 나온다.
  예: JLCPCB CPL 은 `Designator,Mid X,Mid Y,Layer,Rotation` **5열**이고 순서도 다르다(KiCad 는 `Side` 가 맨 끝).
  대응 관계는 `Ref→Designator`, `PosX→Mid X`, `PosY→Mid Y`, `Side→Layer`, `Rot→Rotation` 이고 `Val`·`Package` 는 버린다.

  ```bash
  # KiCad pos CSV → JLCPCB CPL (열 재배치, 값은 변환하지 않는다)
  python3 -c '
import csv,sys
r=csv.DictReader(open(sys.argv[1],newline="",encoding="utf-8"))
w=csv.writer(open(sys.argv[2],"w",newline="",encoding="utf-8"))
w.writerow(["Designator","Mid X","Mid Y","Layer","Rotation"])
for x in r: w.writerow([x["Ref"],x["PosX"],x["PosY"],x["Side"],x["Rot"]])
' "$OUT/assembly/$NAME-top-pos.csv" "$OUT/assembly/$NAME-cpl-jlcpcb.csv"
  ```

  **좌표·회전 값 자체는 건드리지 않는다** — 열 이름과 순서만 맞춘다.
- `--smd-only` 는 SMD 만 남긴다. **THT 전용 보드에서 행이 0개로 나오는 것은 정상**이며, 이때 위치 파일은 보내지 않는다 —
  0행 파일을 그대로 넘기면 조립사가 "부품 없음" 으로 처리한다.
- `--exclude-dnp` 로 DNP(Do Not Populate) 부품을 뺀다. **제외된 수를 세어 리포트에 적는다**
  (BOM 의 DNP 수와 일치해야 한다).
- `--side both` 로 한 파일에 앞뒤를 담거나, 조립사가 면별 파일을 요구하면 `front`/`back` 으로 두 번 뽑는다.
- 회전 기준(0도 방향)은 KiCad 풋프린트 정의를 따르며 **조립사 기준과 다를 수 있다.**
  이 스킬은 회전값을 임의로 보정하지 않는다 — 리포트에 "회전 기준 미보정, 조립사 규격 확인 필요" 를 남긴다.

---

## 단계 7: BOM (발주용)

```bash
kicad-cli sch export bom \
  --output "$OUT/assembly/$NAME-bom.csv" \
  --fields "Reference,Value,Footprint,MPN,Manufacturer,LCSC,QUANTITY,DNP" \
  --labels "Reference,Value,Footprint,MPN,Manufacturer,LCSC,Qty,DNP" \
  --group-by "MPN,Value,Footprint" \
  --sort-field "Reference" \
  --exclude-dnp \
  "$ROOT_SCH"
```

MCP 대응: `mcp__kicad__export_sch_bom`(`schematicPath` **필수**, `outputPath` 필수, `preset`·`formatPreset`·
`fields`·`labels`·`groupBy`·`sortField`·`sortAsc`·`filter`·`excludeDnp` 등).

- **그룹 키는 `MPN` 이 먼저다.** `Value + Footprint` 만으로 묶으면 `100nF 0402 16V X7R` 과 `100nF 0402 50V X5R` 이
  한 행으로 합쳐져 발주가 틀린다.
- **회로도에 `MPN`/`LCSC` 필드가 없으면 그 열은 빈 칸으로 나온다.** 이때는 BOM 헤더와 검증 리포트에
  **"MPN 부재 — 발주용 아님"** 을 명시한다. 열 자체는 빈 칸으로라도 남겨 두어, 나중에 채울 자리를 보이게 한다.
- `--exclude-dnp` 로 뽑은 **조립용 BOM** 과, DNP 를 포함한 **전체 BOM** 을 따로 뽑아 두면 조립사와의 소통이 줄어든다.
- kicad-review 가 만드는 마크다운 BOM 은 **리뷰용**(사람이 읽는 파트리스트)이고, 여기서 만드는 CSV 는 **발주용**이다.
  같은 회로도에서 나오므로 부품 종류 수와 총 수량이 일치해야 한다.
- **수량이 어긋나면 원인을 이 순서로 짚는다.**
  1. **회로도 심볼 수와 BOM 총 수량을 먼저 대조한다** — 넷리스트 XML 의 `<comp>` 수가 기준이다.
  2. **`exclude_from_bom` 심볼**: 기구 홀·테스트 마커 같은 심볼은 이 속성 때문에 BOM 에서 빠진다.
     실측: 이 회로도의 `Hole(1mm)` 심볼 8개(`+3V1, GND1~3, TCK1, TDI1, TDO1, TMS1`)가 그래서 빠졌고,
     `--include-excluded-from-bom` 을 붙여도 **되살아나지 않았다**(10.0.6 실측: 68종/363개로 불변).
     이 경우 리포트에 "회로도 심볼 {n}개가 `exclude_from_bom` 으로 제외됨" 을 수치로 남긴다.
  3. `on_board no` 심볼(보드에 올리지 않는 심볼).
  4. 그룹 키 차이(`MPN` 포함 여부)나 DNP 처리 차이.

---

## 단계 8: 산출물 목록 · 체크섬 · 전달 패키지 · 검증 리포트

산출물 디렉토리를 실제로 훑어 리포트를 만든다. "명령이 성공했다" 가 아니라 **파일이 실제로 존재하고 내용이 비어 있지 않은지** 본다.

```bash
# 목록 — -printf 는 파일당 한 줄이므로 공백 파일명에 안전하다
find "$OUT" -type f -printf '%P\t%s\n' | sort

# 체크섬 — 반드시 -print0 | xargs -0 로 넘긴다
find "$OUT" -type f ! -name SHA256SUMS -print0 | sort -z \
  | xargs -0 sha256sum > "$OUT/SHA256SUMS"

# 검증: 기록된 줄 수 == 대상 파일 수
echo "$(wc -l < "$OUT/SHA256SUMS") / $(find "$OUT" -type f ! -name SHA256SUMS | wc -l)"
```

**`sha256sum $(find ...)` 를 쓰지 않는다.** 명령 치환 결과가 공백에서 쪼개져 **공백이 든 파일명이 통째로 빠진다.**
KiCad 산출물 파일명은 보드 파일명을 그대로 따르므로, 보드명에 공백이 있으면 거버·드릴이 전부 누락된다.
그런데 명령은 부분 성공하므로 `SHA256SUMS` 파일 자체는 만들어진다 — **조용히 잘못된 체크섬 목록이 남는다.**
실측(보드명에 공백 있음): 나이브 명령은 20개 중 **6개만** 기록(에러 42줄), `-print0 | xargs -0` 은 **20/20**.
그래서 위 마지막 줄의 **줄 수 대조를 반드시 수행하고 리포트에 `{기록}/{대상}` 으로 적는다.**

### 팹 전달 패키지

체크섬까지 만들었으면 **보낼 수 있는 형태로 묶는 것까지가 이 단계다.**

```bash
# 1) 파일명 공백 제거 — 팹 CAM 업로드에서 거부되는 흔한 사유
find "$OUT/gerber" "$OUT/drill" -type f -name '* *' -print0 \
  | while IFS= read -r -d '' f; do mv "$f" "$(dirname "$f")/$(basename "$f" | tr ' ' '_')"; done

# 2) 거버 + 드릴을 zip 1개로 (팹 표준 전달 형태). 체크섬은 이름 정리 후 다시 만든다
find "$OUT" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$OUT/SHA256SUMS"
(cd "$OUT" && zip -r "${NAME}_fab.zip" gerber drill >/dev/null)
```

- **zip 은 거버 + 드릴만 담는다.** BOM·CPL 은 팹/조립사가 별도로 받는다(`references/fabrication-outputs.md` 1.1 전달 형태).
- **드릴 맵(`*-drl_map.*`)은 팹이 요구할 때만 zip 에 넣는다.** 사람이 검산하는 용도라 CAM 이 여분 파일로 보고 되물을 수 있다.
- **0홀 NPTH 파일은 zip 에 넣지 않는다** — 짝이 되는 `*-NPTH-drl_map.*` 도 함께 뺀다.
  위치 파일 0행을 보내지 않는 것과 같은 원칙이다. 빈 파일은 팹이 "도금 안 하는 홀이 있는데 좌표가 없다" 로 되묻는 원인이 된다.
  리포트에 "NPTH 0홀 — 미포함" 을 적는다. 홀 수는 `grep -c '^X' *NPTH.drl` 로 센다.
- **파일명을 바꿨으면 체크섬을 다시 만든다.** 위 순서(이름 정리 → 체크섬 → zip)를 지킨다.
- **스택업 사양은 이 스킬이 만들지 않는다.** `.gbrjob` 에 보드 두께와 동박 두께는 들어가지만
  표면처리(HASL/ENIG)·솔더마스크 색·실크 색·유전율(임피던스 제어)은 없다. 발주 폼에 사람이 적어야 하므로
  리포트 "확인 필요" 에 남긴다.

리포트 형식:

```
═══════════════════════════════════════════
  KiCad 제조 출력 리포트
═══════════════════════════════════════════

프로젝트: {프로젝트명}   리비전: {rev}   보드: {.kicad_pcb}
kicad-cli: {버전}        생성일: {날짜}
산출물: {디렉토리}

━━━ 게이트 ━━━
  DRC:        error {n} / warning {n} / 미배선 {n}     → 통과 / 중단
              (severity 범위: error+warning — 예외(exclusion) 제외)
  패리티:     {n}건 ({검사됨 | 베이스명 사본으로 검사 | 짝 회로도 없음 — 미수행})
              중단 사유 type {n}건 (missing/extra_footprint, net_conflict, duplicate_footprints)
              리포트 type {n}건 (footprint_symbol_*_mismatch)
  IPC↔넷리스트: 회로도에만 {n} / 보드에만 {n} / 넷 불일치 {n}  → 통과 / 중단
              (레코드 317+327 기준, 넷 비교는 대문자·뒤 14자 정규화)
  존 채움:    구리 존 {n}개 (keepout {n}개 제외) — 전부 채움 / 미채움 {n}개 ({조치}) / 해당 없음
  원점:       보조 원점 {설정됨 | 미설정 — 절대 원점 사용}

━━━ 산출물 ━━━
  거버:       {n}개 파일 — {실제 파일 목록}
  드릴:       PTH {n}홀 / NPTH {n}홀 / 맵 {n}개
  위치 파일:  {n}행 (SMD only, DNP {n}개 제외)
  IPC-D-356:  {n}개 테스트 포인트 (317 {n} / 327 {n})
  BOM:        {n}종 / 총 {n}개 (DNP {n}개 제외, exclude_from_bom {n}개 제외) — MPN {있음 | 부재 — 발주용 아님}
  전달 패키지: {NAME}_fab.zip (거버 {n} + 드릴 {n}) / 파일명 공백 {정리함 | 없음}

━━━ 확인 필요 ━━━
  [확인] {항목}: {사유 — 예: "회전 기준 미보정 — 조립사 규격 확인 필요"}
  [확인] 스택업 사양: 표면처리·솔더마스크 색·유전율은 산출물에 없음 — 발주 폼에 기재 필요

━━━ 체크섬 ━━━
  SHA256SUMS {기록 n}/{대상 n} 파일   (일치하지 않으면 미완성 목록이다)
```

검증 항목의 상세 목록(레이어 수 대조, 드릴 홀 수 대조, 위치 파일 행 수 대조 등)은
`references/fabrication-outputs.md` 의 "산출물 검증 체크리스트" 를 따른다.

### 리포트 원칙

- **근거 명시**: 파일 수·홀 수·행 수 같은 **센 값**으로 적는다. "정상 생성됨" 만 쓰지 않는다.
- **추측 금지**: 확인하지 않은 항목은 "미수행" 으로 적는다. 팹 규격은 이 스킬이 판정할 수 없으므로 "확인 필요" 로 넘긴다.
- **원점 일치 명시**: 거버·드릴·위치 파일이 같은 원점을 썼다는 사실을 리포트에 한 줄로 남긴다.
- **체크섬**: 팹에 보낸 뒤 "받은 파일이 보낸 파일과 같은가" 를 되물을 수 있게 SHA256 을 남긴다.
  기록된 줄 수와 대상 파일 수를 **대조한 값**으로 적는다 — 부분 성공한 체크섬 목록은 없는 것보다 나쁘다.

---

## 참조 파일

- `references/fabrication-outputs.md` — 팹별 프로파일(레이어 세트·X2·드릴 포맷·위치 파일 요구) + 산출물 검증 체크리스트

## 사용 예시

```
사용자: "이 보드 거버 뽑아줘"
사용자: "JLCPCB 에 보낼 제조 파일 만들어줘"
사용자: "드릴 파일이랑 위치 파일 생성해줘"
사용자: "제조 출력 전에 DRC 랑 동기화 확인부터 해줘"
사용자: "IPC-D-356 전기 테스트 넷리스트 뽑아줘"
사용자: "발주용 BOM CSV 만들어줘"
```

$ARGUMENTS
