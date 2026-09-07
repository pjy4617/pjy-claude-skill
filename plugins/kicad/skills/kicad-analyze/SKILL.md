---
name: kicad-analyze
description: "KiCad 회로(넷리스트)와 PCB(.kicad_pcb)를 정밀 분석합니다. 넷 연결 추적, ERC/DRC 검증, 핀 충돌 탐지, 풋프린트/보드 통계, 넷별 트랙 추적, 라우팅 품질, 신호 무결성(SI)/전원 무결성(PI) 분석을 수행합니다. 'PCB 분석', 'PCB 검토', 'PCB 리뷰', 'DRC 돌려줘', 'DRC 검사', 'ERC 검사', '넷 추적', '넷리스트 분석', '트랙 분석', '라우팅 검토', '신호 무결성', 'signal integrity', '전원 무결성', 'power integrity', '핀 충돌 확인', '보드 통계', '풋프린트 목록', '배치 검토', '배치 확인', '에어와이어 길이', '회로도 보드 동기화 확인', 'Update PCB 누락', 'KiCad 회로/PCB 분석', 'kicad pcb analyze' 등의 요청에 자동 적용. ※ 회로도 *설계* 적정성 리뷰·데이터시트 비교·BOM 생성은 kicad-review를, 거버/드릴/위치 파일 등 *제조 출력 생성*은 kicad-fabricate를 쓰고, *넷리스트 연결성·ERC/DRC·PCB 물리 레이아웃·배치·SI/PI* 분석은 이 스킬을 쓴다. KiCAD-MCP-Server(등록 시) → kicad-cli → 직접 파싱 순으로 폴백한다. STM32, FPGA, EtherCAT, 고속 신호 보드 등 모든 도메인 지원."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# KiCad 회로/PCB 정밀 분석

> 이 스킬은 KiCad **회로(넷리스트)**와 **PCB(.kicad_pcb)**를 프로그래매틱하게 분석한다.
> `kicad-review`(회로도 *설계* 리뷰 + BOM)와 상호 보완적이다 — 이 스킬은 **넷 연결성·전기 규칙·PCB 물리 레이아웃·신호/전원 무결성**에 초점을 둔다.

## kicad-review 와의 역할 분담

| | kicad-review | **kicad-analyze (이 스킬)** |
|---|---|---|
| 입력 | `.kicad_sch` | `.kicad_sch` + **`.kicad_pcb`** |
| 초점 | 설계 적정성(전원/데이터시트/도메인 체크리스트), BOM | 넷 연결성·ERC/DRC·**PCB 물리 레이아웃**·SI/PI |
| 방식 | 텍스트 파싱 + 데이터시트 웹 비교 | **KiCAD-MCP-Server / kicad-cli** 기반 정밀 분석 |
| PCB | ✗ 미지원 | ✓ 풋프린트/트랙/비아/DRC/SI/PI |

회로도 *설계 검토*나 BOM이 필요하면 `kicad-review`를, 넷 연결 추적·PCB 분석·SI/PI가 필요하면 이 스킬을 쓴다.
**거버·드릴·위치 파일 같은 제조 산출물을 뽑는 것은 `kicad-fabricate`** 다 — 이 스킬은 판정만 하고 팹에 넘길 파일을 만들지 않는다.

---

## 분석 엔진 폴백 체인

이 스킬은 세 가지 엔진을 **가용한 것 우선**으로 사용한다. 도구별 매핑은 `references/mcp-tools.md` 참조.

```
[1순위] KiCAD-MCP-Server (mcp__kicad__*)
        → ERC/DRC, 넷 추적, 회로도 린트, 풋프린트/보드 통계,
          트랙·존·패드 기하(SI/PI 판정의 입력)까지 정밀
        → 등록: kicad-setup 스킬 또는 references/mcp-tools.md "설치" 참조
[2순위] kicad-cli  (PATH에 있을 때)
        → sch erc / pcb drc / sch export netlist / pcb export gerbers
        → 트랙·존 기하 미지원 (heuristic 분석으로 대체)
        ※ ERC/DRC는 MCP 경로도 내부에서 kicad-cli를 부른다 — kicad-cli가 없으면 MCP를 등록해도 ERC/DRC는 실패
[3순위] 직접 파싱  (.kicad_sch / .kicad_pcb S-expression 텍스트)
        → 넷/풋프린트/트랙 추출 가능, 존 채움·정밀 트랙 통계는 제한
```

> **중요 1**: 정밀 트랙 길이/비아 통계·존 채움 결과는 사실상 **MCP(pcbnew 기반)** 가 있어야 정확하다. 폴백 모드에서는 해당 항목을 "제한적/heuristic" 또는 "미수행"으로 보고서에 명시한다.
>
> **중요 2**: 이 서버에는 **SI/PI 전용 분석 도구가 없다.** `analyze_pcb_signal_integrity` 같은 이름으로 호출하지 않는다. MCP에서 트랙·존·패드 **기하 데이터**를 받아 이 스킬이 직접 계산·판정한다. 절대 임피던스와 IR drop은 `.kicad_pcb`의 `(setup (stackup ...))`에 `epsilon_r`·`thickness`가 있으면 그 값으로 근사 계산하고, 스택업 블록이 없으면 "미수행 — Board Setup > Physical Stackup 미설정"으로 명시한다. 상세는 `references/mcp-tools.md`의 "SI/PI 분석" 절 참조.

---

## 워크플로우 개요

```
[1] 환경·엔진 감지 — MCP 등록 / kicad-cli / 파일 탐색
 ↓
[2] 대상 식별 — .kicad_sch(회로) + .kicad_pcb(PCB) 매핑
 ↓
[3] 회로(넷리스트) 분석 — 넷/부품, 넷 연결 추적, ERC, 핀 충돌
 ↓
[3.5] 회로도-보드 동기화 확인 — IPC-D-356 ↔ 넷리스트 diff (Update PCB 누락 탐지)
 ↓
[4] PCB 분석 — 배치 검토, 보드 통계, 넷별 트랙, 라우팅 품질, DRC
 ↓
[5] 신호/전원 무결성(SI/PI) — 트랙 기하 기반 길이매칭·폭·레이어, 전원 평면
 ↓
[6] 종합 분석 보고서
```

---

## 단계 1: 환경·엔진 감지

```bash
# KiCAD-MCP-Server 등록 여부 (등록 시 mcp__kicad__* 도구 사용 가능)
claude mcp list 2>/dev/null | grep -i "kicad" && echo "→ KiCAD-MCP-Server 엔진 사용" \
  || echo "→ MCP 미등록 (kicad-cli/직접 파싱으로 폴백)"

# kicad-cli 가용성 + 버전
kicad-cli version 2>/dev/null || kicad-cli --version 2>/dev/null \
  || echo "→ kicad-cli 없음 (직접 파싱 모드)"

# 대상 파일의 포맷 세대 (kicad-cli 메이저가 이 세대 이상이어야 한다)
grep -m1 -o '(version [0-9]*)' "$PCB"

# 대상 파일 탐색
find "$TARGET_DIR" -name "*.kicad_pro" -o -name "*.kicad_sch" -o -name "*.kicad_pcb" | sort
```

선택된 엔진을 보고서 헤더에 명시한다 (예: `엔진: KiCAD-MCP-Server (pcbnew)` / `엔진: kicad-cli` / `엔진: 직접 파싱`).

MCP를 쓰기로 했다면:

- **연결 확인은 `mcp__kicad__get_backend_state`**로 한다. 파이썬 브리지까지 실제로 타므로 `backend`가 돌아오면 pcbnew까지 준비된 것이다
  (`list_tool_categories`는 Node 서버만 확인한다). `diskChangedExternally`가 true면 `reload_board`로 갱신한 뒤 분석한다.
- **`get_backend_state`를 세션의 첫 MCP 호출로 둔다.** wxApp 초기화 55~65초는 **macOS 한정 비용**이고,
  서버가 기동하는 동안 내부 `_warmup` 커맨드로 그것을 미리 지불한다 — 첫 *도구 호출* 때 내는 비용이 아니다
  (서버 소스 `python/kicad_interface.py`의 pcbnew import 주석, `_warmup` 핸들러).
  실측(Linux, 서버 기동 후 첫 호출)은 **3.3초**다. 다만 서버를 막 띄운 직후라면 최대 1분까지 기다리고,
  타임아웃으로 오판해 폴백으로 내려가지 않는다.
- **kicad-cli 유무는 MCP를 써도 필수 확인**이다 — `run_erc`/`run_drc`가 내부에서 kicad-cli를 부른다.
- **kicad-cli 버전은 파일 포맷 세대 이상**이어야 한다. `kicad-cli version`의 메이저가 대상 파일의 `(version ...)` 세대보다 낮으면
  `sch erc`/`pcb drc`가 파싱 실패로 죽는다 — `20260101` 파일에는 kicad-cli 10이 필요하다.
  여러 버전이 깔려 있으면 환경변수 `KICAD_CLI`(별칭 `KICAD_CLI_PATH`)로 서버에 경로를 고정한다.
- **브리지가 죽으면 자동으로 되살아나지 않는다.** 도구가 연속으로 `Python process for KiCAD scripting is not running`을
  돌려주면 파이썬 브리지가 종료된 것이다(서버는 프로세스 핸들만 비우고 재기동하지 않는다).
  `/mcp`에서 kicad 서버를 재연결(또는 세션 재시작)한 뒤 `get_backend_state`로 확인하고, 보드는 `open_board`로 다시 연다.
  **세션 중 `refill_zones`는 호출하지 않는다** — SWIG 세그폴트로 브리지가 죽는다(대안은 4.3 참조).
- **도구 이름의 정본은 서버 저장소 `docs/TOOL_INVENTORY.md`**다. `search_tools`로 안 잡히는 도구(`query_traces`, `get_nets_list`, `run_erc` 등 23개 —
  `references/mcp-tools.md` "탐색 미검출 도구")를 "이름이 틀렸다"로 오판해 폴백으로 내려가지 않는다.

**보드 분석 전에는 보드를 연다**: `mcp__kicad__open_project`(`.kicad_pro`, 같은 이름의 `.kicad_pcb` 함께 로드) 또는
`mcp__kicad__open_board`(`.kicad_pcb`). 보드 도구(board/component/routing/DRC)는 전부 로드가 필요하다(`No board is loaded`).
**회로도 도구는 열지 않는다** — 전부 `schematicPath` 파라미터로 파일을 직접 받으며, 계층 설계는 루트 `.kicad_sch` 경로를 넘긴다.

---

## 단계 2: 대상 식별

- `.kicad_pro`(프로젝트) 기준으로 같은 베이스명의 `.kicad_sch`/`.kicad_pcb` 쌍을 묶는다.
- `.kicad_pcb`가 없으면 → PCB 단계(4·5)는 "PCB 파일 없음 — 회로 분석만 수행"으로 표시하고 회로(3)만 진행.
- 계층 회로도면 루트 `.kicad_sch`의 `(sheet ...)`로 서브시트를 파악한다.

**베이스명이 갈리는 프로젝트를 먼저 걸러낸다.** `.kicad_pcb`와 `.kicad_pro`/`.kicad_sch`의 베이스명이 다른 프로젝트가
실무에 흔하다(실측 사례: pcb `EtherCAT2 Trigger Module_Rev_0.4.kicad_pcb` vs pro·sch `EtherCAT2 Trigger Module(Rev_0.4)`).
`kicad-cli pcb drc --schematic-parity` 는 **PCB 와 같은 디렉토리·같은 베이스명의 `.kicad_sch`** 만 짝으로 찾으므로,
이 상태를 모르고 넘어가면 패리티가 **0건으로 조용히 통과**한다(같은 보드에서 짝을 맞추면 431건).

```bash
# 베이스명 비교 — 확장자를 뗀 이름이 서로 다르면 그대로 진행하지 않는다
ls "$TARGET_DIR"/*.kicad_pcb "$TARGET_DIR"/*.kicad_pro "$TARGET_DIR"/*.kicad_sch 2>/dev/null
```

| 상태 | 처리 |
|------|------|
| 베이스명 일치 | 그대로 진행 |
| 베이스명 불일치 | **사용자에게 어느 `.kicad_sch`가 이 보드의 짝인지 확인**한다. 확인된 루트 회로도 경로를 단계 3·3.5에서 `$ROOT_SCH`로 **명시 지정**하고, 보고서 헤더에 "pcb/sch 베이스명 불일치 — 루트 회로도를 수동 지정" 을 적는다 |
| `.kicad_pcb`가 여러 개 | 어느 보드를 분석할지 사용자에게 확인. 임의로 고르지 않는다 |

**패리티 검사만은 베이스명을 맞춰야 돈다** — kicad-cli 에 회로도 경로를 넘기는 옵션이 없다.
원본을 건드리지 않고 **스크래치 디렉토리에 프로젝트 파일 전체를 심링크로 미러**한 뒤,
보드 베이스명과 같은 이름의 `.kicad_sch` 심링크를 하나 더 만들어 그 디렉토리에서 DRC 를 돌린다.
(계층 시트는 상대 파일명으로 참조되므로 같은 디렉토리에 함께 심링크되면 그대로 해석된다.)

```bash
MIRROR=$(mktemp -d)
ln -s "$TARGET_DIR"/* "$MIRROR"/
ln -s "$ROOT_SCH" "$MIRROR/$(basename "$PCB" .kicad_pcb).kicad_sch"
kicad-cli pcb drc -o /tmp/drc.json --format json --severity-all --schematic-parity "$MIRROR/$(basename "$PCB")"
```

원본 디렉토리에 사본을 만들어 짝을 맞추지 않는다 — 프로젝트 베이스명과 같은 이름의 보드/회로도 사본이 남으면
이후 패리티 검사의 짝을 오염시킨다.

---

## 단계 3: 회로(넷리스트) 분석

넷리스트 = "어떤 핀이 어떤 넷에 묶였는가"의 ground truth. 회로도 좌표·시각보다 정확하다.

### 3.1 넷리스트 생성

| 엔진 | 방법 |
|------|------|
| MCP | `mcp__kicad__generate_netlist` → `list_schematic_nets` / `list_schematic_components` |
| kicad-cli | `kicad-cli sch export netlist --format kicadxml --output /tmp/netlist.xml "$ROOT_SCH"` |
| 직접 파싱 | `.kicad_sch`의 `(label)`/`(global_label)`/`(wire)`로 넷 추론 (정확도 제한 경고) |

### 3.2 넷 연결 추적

특정 넷(예: `SPI_CLK`, `+3V3`)에 연결된 **모든 핀**을 나열한다.

- MCP: `mcp__kicad__get_net_connections`(넷 → 연결 전체), `mcp__kicad__list_schematic_nets`, PCB 쪽은 `mcp__kicad__get_net_pads`
- 활용: 클럭/리셋/전원 넷의 팬아웃 확인, 미연결(1핀) 넷 탐지, 의도치 않은 다중 드라이버 탐지

### 3.3 ERC (Electrical Rules Check)

| 엔진 | 방법 |
|------|------|
| MCP | `mcp__kicad__run_erc` |
| kicad-cli | `kicad-cli sch erc --output /tmp/erc.json --format json --severity-all "$ROOT_SCH"` |
| 직접 파싱 | 미지원 → "ERC 미수행(엔진 없음)" 표시 |

주요 위반: 전원 핀에 PWR_FLAG 누락, output↔output 충돌, 미연결 입력, 양방향 핀 충돌.

### 3.4 핀 충돌 탐지

핀 충돌 전용 도구는 없다. 그러나 **ERC가 돌아갔으면 ERC 결과를 그대로 쓴다** —
`pin_to_pin`(핀 타입 충돌)·`pin_not_driven`(드라이버 없음) 항목이 KiCad 핀-타입 매트릭스로 낸 정본 판정이다.
같은 판정을 이 스킬이 다시 하지 않는다. 자체 규칙은 passive를 거쳐 오는 드라이버·버스·계층 경계를 보지 못해
ERC보다 부정확하다.

**아래 자체 규칙 표는 kicad-cli가 없어 ERC를 못 돌린 폴백에서만 쓴다.**

- MCP: `mcp__kicad__get_net_connections`(넷에 물린 핀) + `mcp__kicad__list_symbol_pins`(심볼별 핀 **타입**)
  → 넷별로 핀 타입 조합을 만들어 규칙 적용. `batch_list_symbol_pins`로 여러 심볼을 한 번에 받으면 왕복이 준다.
  **`schematicPath`를 항상 함께 넘긴다** — 그래야 프로젝트 로컬 `sym-lib-table`의 벤더 심볼 핀 타입을 찾는다.
- 폴백: 넷리스트 XML의 핀 타입 집계 후 같은 규칙 적용(아래 표).

| 넷에 물린 조합 | 판정 |
|---------------|------|
| output + output | ERROR (다중 드라이버) |
| power_out + power_out | ERROR |
| output + power_in | WARN (의도 확인) |
| 입력만 존재 (드라이버 0) | ERROR (플로팅 넷) |

---

## 단계 3.5: 회로도-보드 동기화 확인

`.kicad_pcb`가 있을 때만 수행한다. **"회로도는 고쳤는데 Update PCB(F8)를 안 돌린 보드"** 를 걸러내는 단계다.
이것을 놓치면 이후 단계 4·5 가 **낡은 보드**를 분석해 놓고 "정상" 이라고 보고하게 된다.

### 3.5.1 IPC-D-356 ↔ 넷리스트 diff

IPC-D-356 은 **보드에 실제로 존재하는 패드와 그 넷**을 적은 파일이다. 보드 쪽 정본으로 쓴다.

| 엔진 | 방법 |
|------|------|
| MCP | `mcp__kicad__export_ipcd356` — `outputPath` **필수**, `boardPath` 선택(생략하면 로드된 보드). 산출물은 스크래치 디렉토리에 둔다 |
| kicad-cli | `kicad-cli pcb export ipcd356 -o /tmp/board.ipc "$PCB"` |
| 직접 파싱 | 미지원 → "동기화 확인 미수행(엔진 없음)" 표시 |

회로도 쪽은 단계 3.1 에서 만든 넷리스트를 그대로 쓴다(`kicad-cli sch export netlist --format kicadxml`).

레코드 포맷(kicad-cli 10.0.6 실측, 고정폭):

| 컬럼 | 내용 | 예 |
|------|------|-----|
| 1–3 | 레코드 코드 — `317`(관통홀·비아) / `327`(**SMD 패드**) / `999`(종료) / `P `(헤더 파라미터) | `327` |
| 4–17 | 넷 이름 (**14자**. 넘으면 **앞이 잘리고 뒤 14자만 남는다**. 항상 대문자) | `T-(U1-VCC_PLL)` |
| 18–20 | 공백 패딩(항상 비어 있다) | ` ` |
| 21–26 | 레퍼런스 (6자) | `C1` |
| 27–30 | `-` + 핀 번호 (테스트포인트 등은 빈칸) | `-1` |
| 31– | 패드 기하(직경·좌표·회전) | `A01X+069940Y-024764...` |

**`^317`만 읽으면 SMT 보드를 통째로 놓친다.** SMD 패드는 `327`이다 — 실측 보드(356 풋프린트, 2층)의
IPC-D-356 1411행 중 `327`이 **1394행**, `317`은 **16행**뿐이었다. `^317`만 파싱하면 보드 패드를 14개만 보고
"회로도에만 1387건"이라는 무의미한 판정이 나와, **정상 보드도 미동기화로 오판**된다.

```bash
# 레코드 코드 분포를 먼저 확인한다 — 327 이 대부분이면 SMT 보드다
cut -c1-3 /tmp/board.ipc | sort | uniq -c | sort -rn
```

diff 절차: **`^317`과 `^327` 두 행 종류 모두**에서 `(레퍼런스, 핀) → 넷` 맵을 만들고,
넷리스트 XML 의 같은 맵과 비교한다. 핀 번호가 빈 레코드(테스트포인트·기구 홀)는 키를 만들 수 없으므로 집계에서 뺀다.

| 차이 | 판정 | 해석 |
|------|------|------|
| 회로도에 있는 `(ref, 핀)` 이 보드에 없음 | **ERROR** | Update PCB 미실행 — 부품/핀이 보드에 올라가지 않았다 |
| 회로도와 보드의 넷 이름이 다름 | **ERROR** | 회로도 변경이 보드에 반영되지 않았다 |
| 보드에만 있는 `(ref, 핀)` | WARN | 보드에서 직접 추가한 부품(펜스 비아, 기구 홀 등)인지 확인 |
| IPC 넷 이름이 `N/C` | 정보 | 미연결 패드. 회로도에서도 미연결이면 정상 |

**넷 이름은 뒤 14자만 남고 대문자로 변환된다.** 앞에서 잘리는 것이지 뒤에서 잘리는 것이 아니다 —
`Net-(U1-VCC_PLL)`(16자)는 `T-(U1-VCC_PLL)`로, `Net-(D15-PadA)`는 `NET-(D15-PADA)`로 나온다.
따라서 양쪽을 **`name.upper()[-14:]`** 로 정규화해 비교한다.
문서가 예전에 적었던 "앞 17자·대소문자 구분" 규칙으로 같은 보드를 비교하면 불일치가 **477건**,
정정 규칙으로는 **83건**이다 — 394건이 순수 오탐이었다.
`(ref, 핀)` 존재 여부는 넷 이름과 무관하므로 1차 키로 그대로 쓴다.

### 3.5.2 패리티 교차 확인 (kicad-cli)

`kicad-cli pcb drc --schematic-parity` 는 KiCad 자신의 판정을 `schematic_parity` 배열로 돌려준다
(`footprint_symbol_mismatch` 등). **보드와 같은 디렉토리·같은 베이스명의 `.kicad_sch`** 를 짝으로 찾으므로,
짝이 없으면 배열이 비어서 돌아온다 — **"0건" 을 통과로 읽기 전에 검사가 실제로 수행됐는지 확인한다.**
단계 4.4 에서 어차피 DRC 를 돌리므로 그때 `--schematic-parity` 를 함께 켜고 결과를 이 단계로 가져온다.

**`--schematic-parity` 는 옵트인 플래그다 — 빼면 `schematic_parity`가 빈 배열로 오는데 그것은 "이상 없음"이 아니라 "미검사"다.**
그래서 이 스킬의 DRC 명령 예시에는 항상 이 플래그가 들어 있다. 실측 보드에서 플래그 없이 돌리면 0건,
켜면 431건(net_conflict 185 / footprint_symbol_mismatch 94 / missing_footprint 70 / duplicate_footprints 34 /
footprint_symbol_field_mismatch 26 / extra_footprint 22)이 나왔다.

0건이 나왔을 때의 판정 순서:
1. stderr 에 "패리티 테스트를 위한 회로도 네트리스트를 가져오지 못함" 류 경고가 있는가 → 짝을 못 찾은 것이다.
2. 명령줄에 `--schematic-parity` 가 실제로 있었는가 → 없으면 미검사다.
3. pcb 와 sch 의 베이스명이 같은가 → 다르면 **단계 2의 심링크 미러 절차**로 짝을 맞춘 뒤 다시 돌린다.

셋 다 통과했을 때만 "패리티 이상 없음" 으로 적는다.

ERROR 가 있으면 보고서 맨 위에 **"보드가 회로도와 동기화되지 않음 — 이후 PCB 분석 결과는 낡은 보드 기준"** 을 적고,
사용자에게 KiCad 에서 Tools → Update PCB from Schematic(F8) 실행 후 저장을 안내한다.

---

## 단계 4: PCB 분석

`.kicad_pcb`가 있을 때만. 없으면 건너뛰고 보고서에 명시.

### 4.1 배치 검토

배선 전 **배치 품질을 숫자로** 본다. 여기서 잡으면 배선 후 재작업이 없다.

**부품 목록**

- MCP: `mcp__kicad__get_component_list` — 부품 배치, 앞/뒷면 분포 확인. 특정 부품은 `find_component`
  **주의: `boundingBox` 필터는 실측(서버 2.7.0)에서 무시되고 전체가 돌아온다.** 356 풋프린트 보드에서
  bbox 를 넘겼는데 356개 전부가 왔고 응답 101,265자로 **토큰 한도를 넘겨 호출 자체가 실패**했다.
  수백 부품 보드는 `layer` 필터로 앞/뒷면을 나눠 부르거나, `.kicad_pcb` 의 `(footprint ... (at x y))` 를
  직접 파싱해 좌표를 얻는다 — 좌표 계산이 목적이면 직접 파싱이 더 싸고 확실하다.
- 폴백: `.kicad_pcb`의 `(footprint ... (layer "F.Cu"|"B.Cu"))` 추출
- 검토: BOM 부품 수 ↔ PCB 풋프린트 수 일치, 미배치(unplaced) 부품, 양면 분포

**에어와이어 길이 — 이 배치로 배선하면 얼마나 길어지는가**

- `mcp__kicad__get_ratsnest`(`nets` 넷 이름 배열, `maxPadsPerNet` 기본 128) 로 넷별 에어와이어 길이 합을 받는다.
- **넷을 나눠 호출한다.** 이 도구는 서버 기본 예산 **30초**로 돌고 600초 목록에 없다. 보드 전체를 한 번에 부르면 큰 보드에서 타임아웃난다 —
  고속 넷, 전원 넷, 나머지처럼 그룹을 지어 `nets` 로 여러 번 나눠 부른다.
- `maxPadsPerNet` 초과 넷은 조용히 `skipped` 로 빠진다(GND·전원이 흔히 해당). `skipped` 는 **"미수행"** 으로 보고하거나 상한을 올려 재호출한다.
- 판정: 길이 합이 큰 상위 넷이 곧 재배치 후보다. 절대 기준은 없으므로 **상대 순위와 값**을 함께 적는다.

**거리 기반 점검 (부품 좌표로 계산)**

`get_component_list`(부품 좌표) + `mcp__kicad__get_net_pads`(넷에 물린 패드 좌표)로 아래를 계산한다.

| 항목 | 보는 것 | 판정 방향 |
|------|--------|----------|
| 디커플링 캡 ↔ 전원 핀 | 같은 전원 넷에 물린 캡과 IC 전원 핀의 거리 | 가까울수록 좋다. 먼 캡을 거리 순으로 나열한다 |
| 크리스탈 ↔ MCU | 크리스탈/부하 캡과 MCU OSC 핀의 거리 | 멀면 클럭 루프가 길어진다 — 재배치 후보로 적는다 |
| 차동쌍 두 넷 | 각 넷의 에어와이어 길이 차 | 배치 단계에서 이미 차이가 크면 배선으로 메우기 어렵다 |

이 항목들은 **절대 임계값을 이 스킬이 정하지 않는다.** 측정값과 순위를 제시하고, 임계는 데이터시트·설계 규칙을 따르게 한다.

**간섭·클리어런스**

- `mcp__kicad__check_courtyard_overlaps` — 코트야드 겹침 + 보드 외곽 이탈.
  `positions`(가상 배치 맵 `{ref: [x, y, 회전]}`)를 넘기면 **옮기기 전에** 그 배치가 겹치는지 미리 볼 수 있다.
  **결과는 두 필터를 적용한 뒤에만 보고한다.**
  1. **면이 다르면 겹침이 아니다.** 앞면 부품(`F.Cu`/`F.CrtYd`)과 뒷면 부품(`B.Cu`/`B.CrtYd`)의 쌍은 양면 실장이지
     간섭이 아니다. 이 도구는 2D 좌표만 비교해 앞뒤를 구분하지 않는다 — 실측 보드는 앞면 222 / 뒷면 134 로
     양면 실장이었고, "실제 검토 대상" 으로 남은 쌍이 전부 이 유형이었다.
  2. **중복 레퍼런스 부품은 제외한다.** 같은 `ref` 가 여러 개면 멀리 떨어진 인스턴스들을 하나의 바운딩 박스로
     병합해 허위 겹침·허위 외곽 이탈을 만든다(실측: `D14` 하나가 두 좌표에서 각각 보고, 실제 외곽 이탈 0개).
     중복 여부는 패리티의 `duplicate_footprints` 로 확인하고, 중복을 먼저 정리한 뒤 다시 돌린다.
  두 필터를 적용해 남은 것이 없으면 **KiCad DRC 의 `courtyards_overlap` 항목을 정본으로 삼는다**
  (실측 보드에서 KiCad DRC 의 코트야드 위반은 0건인데 이 도구는 305쌍을 보고했다).
  수백 부품 보드는 `refs` 로 나눠 부른다 — 356 부품에서 한 응답이 약 30 KB 였다.
- `mcp__kicad__check_placement_clearance`(`refs`·`margin`·`padClearance`) — 충돌을 몸체/코트야드/키프아웃/실크/패드로 분류.

**배치 제안 (읽기 전용으로만)**

- `mcp__kicad__suggest_placement` 는 기본이 **dry run** 이라 제안(`{ref: [x, y, 회전]}`)과 점수만 돌려준다.
- **`apply` 는 넘기지 않는다.** 이 스킬은 분석 스킬이며 보드를 바꾸지 않는다. 제안은 보고서에 "재배치 후보" 로 싣고,
  적용 여부는 사용자가 KiCad GUI 에서 판단한다.

### 4.2 보드 통계

통계 전용 도구는 없다. **아래를 조합해 만든다.**

- MCP: `mcp__kicad__get_board_info`(보드 메타) + `get_layer_list`(레이어 수) + `get_board_extents`(외곽 치수)
  + `get_nets_list`(넷 수·넷클래스 — 통계는 없다) + `query_traces`(트랙 카운트)
- **비아 수는 MCP로 못 받는다**(`query_traces`가 비아를 제외하고, 비아 읽기 도구가 없다) → `.kicad_pcb`의 `(via ...)` 직접 파싱으로 보충
- 폴백: `(segment)`/`(via)`/`(net)` 카운트로 근사 (트랙 길이는 좌표로 직접 계산)
- 눈으로 확인이 필요하면 `mcp__kicad__get_board_2d_view`(`responseMode: "file"`, 큰 보드의 메시지 한도 회피)로 보드를 이미지로 받아 첨부한다.

### 4.3 넷별 트랙 추적

- MCP: `mcp__kicad__query_traces`(넷/레이어/영역 필터 → 세그먼트 좌표·폭·레이어),
  `mcp__kicad__query_zones`(카퍼 존 — `isFilled`가 false면 `filledArea`가 없다),
  `mcp__kicad__get_ratsnest`(미라우팅 에어와이어 + 넷별 길이 추정 — `maxPadsPerNet` 기본 128 초과 넷은 조용히 `skipped`.
  GND/전원 넷이 흔히 해당하므로 `skipped`는 "미수행"으로 보고하거나 상한을 올려 재호출)
- 검토: 전원/GND 넷 트랙 폭 충분성, 고속 넷의 레이어 전환(비아 — 직접 파싱) 수, 미라우팅(ratsnest 잔존) 넷

**존이 채워져 있지 않을 때(`isFilled=false`)**: 사용자 동의를 받은 뒤
`kicad-cli pcb drc --refill-zones --save-board "$PCB"`로 채워 저장하고, `mcp__kicad__reload_board` 후 `query_zones`를 다시 부른다.
MCP `refill_zones`는 브리지를 죽일 수 있어 쓰지 않는다.
주의: `--save-board`는 원본 파일을 덮어쓰므로 **KiCad GUI에서 그 보드가 닫힌 상태에서만** 실행한다.
동의를 받지 못하면 "미수행 — 존 미채움"으로 표기한다.

### 4.4 DRC (Design Rules Check)

| 엔진 | 방법 |
|------|------|
| MCP (작은 보드) | `mcp__kicad__get_drc_violations`(`severity: error\|warning\|all`) **하나만** 호출 — 내부에서 DRC를 돌린다. `run_drc`를 먼저 부르면 DRC가 두 번 돈다 |
| MCP (큰 보드) | `mcp__kicad__run_drc` 후 결과 JSON을 심각도별로 직접 거른다 — 아래 타임아웃 참조 |
| kicad-cli | `kicad-cli pcb drc --output /tmp/drc.json --format json --severity-all --schematic-parity "$PCB"` — `--schematic-parity` 결과는 단계 3.5 로 가져간다 |
| 직접 파싱 | 미지원 → "DRC 미수행(엔진 없음)" 표시 |

**타임아웃 주의**: 서버의 기본 명령 예산은 30초이고 `run_drc`만 600초 목록에 있다.
`get_drc_violations`는 내부에서 `run_drc`를 부르지만 자신은 목록에 없어 **30초 예산**으로 돈다.
**예산 구분 자체는 유효하되, 보드 규모로 미리 단정하지 않는다** — 356 풋프린트·476 넷 2층 보드에서
`get_drc_violations`가 **4.7초**에 514건 전체를 반환했다(같은 보드 `kicad-cli pcb drc` 는 1.28초).
따라서 **일단 `get_drc_violations`로 돌려 보고, 실제로 타임아웃이 나면 그때 `run_drc`(600초)로 바꿔
결과 JSON을 심각도별로 직접 거른다.** 30초 예산은 그대로 전제하되 판단은 실측 후에 한다.

**DRC 전에 저장 여부를 사용자에게 묻는다** — "KiCad GUI에서 저장(Ctrl+S)했는가".
DRC는 kicad-cli가 디스크 파일을 읽으므로, GUI에서 저장하지 않았으면 낡은 보드를 검사한다.
`is_dirty`는 MCP 쪽 메모리 상태만 보며 **GUI의 미저장 편집은 감지하지 못한다** — 저장 확인 수단으로 쓰지 않는다.

주요 위반: clearance 미달, 미라우팅 넷, 실루엣/마스크 겹침, 드릴/홀 규칙, copper-edge clearance.

**미라우팅(미연결) 개수는 DRC 결과에서 그대로 인용하지 않는다.**

- MCP `get_drc_violations` 응답에는 `unconnected` 유형이 아예 없다 — MCP 경로만 쓰면 미배선이 **0건으로 보고**된다.
  `kicad-cli pcb drc --format json` 은 `violations` 와 **별도의 `unconnected_items` 배열**로 준다.
- 그 `unconnected_items` 는 **500에서 잘린다.** 실측 보드에서 499건이 왔는데 실제 미연결 에어와이어는 **902개**였고,
  499건이 언급한 넷은 GND·+3.3V·+1V 등 **10개뿐**이었다(나머지 224개 넷은 목록에 없었다).
  `kicad-cli pcb drc --help` 에 이 상한을 올리는 플래그는 **없다**(`--all-track-errors` 로도 499 그대로).
- **판정 규칙: `unconnected_items` 가 499~500이면 "절단됨" 으로 읽는다.** 그 숫자를 미연결 총수로 적지 않고
  "DRC 보고 상한 도달(≥500)" 로 표기한 뒤, 실제 수는 아래 둘 중 하나로 구해 함께 적는다.
  - `mcp__kicad__get_ratsnest` — 단, `maxPadsPerNet`(기본 128) 초과 넷은 `skipped` 로 빠지므로 GND·전원은 별도 처리
  - `.kicad_pcb` 직접 파싱 — 넷별 패드 수를 세어 `Σ(패드 수 − 1)` (트랙 0인 보드에서는 이것이 곧 에어와이어 수다)

```bash
# 넷별 (패드 수 − 1) 합 — 미배선 보드의 실제 에어와이어 수
python3 - "$PCB" <<'EOS'
import re, sys, collections
pads = collections.Counter()
for L in open(sys.argv[1], encoding='utf-8', errors='replace'):
    if re.match(r'\t\(net (\d+) "', L):
        continue          # 보드 상단의 넷 선언 줄 — 패드가 아니다
    for n in re.findall(r'\(net (\d+) "', L):
        pads[int(n)] += 1
print("에어와이어:", sum(c - 1 for n, c in pads.items() if n != 0))
EOS
```

기준값이 궁금하면 `mcp__kicad__get_design_rules`로 현재 설계 규칙을,
특정 두 요소의 실제 간격은 `mcp__kicad__check_clearance`로 확인한다.

### 4.5 회로도 구조·연결 린트 (MCP 전용)

DRC/ERC가 잡지 못하는 "보이지 않는 미접속"을 걸러낸다. MCP가 있을 때만 수행하고, 없으면 생략을 명시한다.
전부 `schematicPath`로 파일을 직접 받는다(프로젝트 열기 불필요). `schematic_load_failed` + `flatSymbols`가 돌아오면
벤더 flat 심볼 문제이므로 해당 시트는 kicad-cli 폴백으로 처리한다.
루트 시트가 flat 심볼을 **임베드만 해도** 루트를 대상으로 한 skip 기반 도구가 전부 실패한다 —
응답의 `flatSymbols`에 심볼 이름이 오므로 그것을 리포트에 적고, 사용자에게 `repair_flat_symbols` 실행(쓰기 도구)을 제안한다.

**린트 5종은 넘긴 시트 파일 하나만 검사한다.** 계층 설계는 `mcp__kicad__get_sheet_properties`로 서브시트 목록을 받아
**시트마다 반복 호출**하고 결과를 시트명으로 태깅한다. 루트만 넘기면 서브시트의 뜬 라벨·오프그리드는 잡히지 않는다.
계층 전체를 한 번에 보는 것은 `run_erc`·`generate_netlist`뿐이다(둘 다 kicad-cli 경유).

**`get_sheet_properties`는 직접 자식 1단계만 준다** — 루트에 호출하면 바로 아래 시트만 돌아온다.
중첩 서브시트가 있으면 **반환된 시트마다 다시 호출해 재귀**해야 계층 전체를 덮는다.
그리고 반대 방향도 본다 — 디렉토리의 `.kicad_sch` 파일 목록과 대조해 **계층 어디에서도 참조되지 않는 고아 시트**를
리포트한다(실측 보드: 디렉토리에 `.kicad_sch` 9개, 계층은 8개 — `ET1200.kicad_sch` 가 고아였다).

**린트가 잡고 ERC 가 침묵하면 곧바로 결함으로 올리지 않는다.** ERC 가 정본이므로
"판정 불일치 — 육안 확인 필요" 로 표기한다(실측: 한 시트에서 `find_orphaned_wires` 26건 대 ERC 의 dangling 0건).

- `mcp__kicad__validate_schematic` — `.kicad_sch` 구조 무결성 (결함 라인/컬럼)
- `mcp__kicad__lint_offgrid` — 그리드에서 벗어난 연결 좌표. **미접속의 가장 흔한 원인**. `fix`는 넘기지 않는다(기본 false — true면 파일을 고친다)
- `mcp__kicad__list_floating_labels` / `find_orphaned_wires` — 뜬 라벨·고아 와이어
- `mcp__kicad__find_wires_crossing_symbols` — 심볼을 관통하는 와이어(오접속 후보)

---

## 단계 5: 신호 무결성(SI) / 전원 무결성(PI)

> **SI/PI 전용 분석 도구는 이 서버에 없다.** MCP에서 트랙·존·패드의 **기하 데이터**를 받아
> 이 스킬이 직접 계산·판정한다. MCP가 있으면 기하가 정확해 판정이 정밀하고, 폴백 모드에서는
> 좌표 기반 heuristic으로 가능한 범위만 보고한다.
>
> **절대 임피던스와 IR drop은 스택업이 파일에 있으면 근사 계산한다.** KiCad는 Board Setup > Physical Stackup을
> 채우면 그 값을 `.kicad_pcb`의 `(setup (stackup (layer "dielectric 1" (type "core") (thickness ...) (material "FR4")
> (epsilon_r ...) (loss_tangent ...)) ...))`에 저장한다. `epsilon_r`·`thickness`가 있으면 그 값으로
> **외층 마이크로스트립 / 내층 스트립라인 임피던스를 IPC-2141 근사식으로 계산해 판정**하고,
> IR drop도 동박 두께(스택업의 copper `thickness`)로 트랙 저항을 근사해 판정한다.
>
> 스택업 블록이 없거나 dielectric 층에 `epsilon_r`이 없으면 **"미수행 — Board Setup > Physical Stackup 미설정"**으로
> 표기하고, 폭·길이·레이어 구성이 목표값 범위에 드는지로 대체 판정한다.
>
> 서버에 스택업 읽기 도구는 없으므로 **이 블록은 `.kicad_pcb`에서 직접 파싱한다(MCP 등록 여부와 무관)**.
> 파싱 스니펫과 근사식은 `references/pcb-analysis.md` 참조.

### 5.1 신호 무결성 (SI)

- 입력 수집: `mcp__kicad__query_traces`(넷별 세그먼트 좌표·폭·레이어) → 길이는 세그먼트 좌표 합으로 계산.
  레이어 전환(비아) 수는 `.kicad_pcb`의 `(via ... (net N))` 직접 파싱(MCP로는 비아가 오지 않는다).
  미라우팅 넷 길이 추정은 `mcp__kicad__get_ratsnest`.
- 검토 항목:
  - **임피던스**: 고속 넷(USB/Ethernet/LVDS/DDR)의 트랙 폭·레이어와 `(setup (stackup ...))`의 `epsilon_r`·`thickness`로
    특성 임피던스를 근사 계산해 목표값(50Ω SE / 90·100Ω diff) 대비 판정
  - **길이 매칭**: 차동 페어 내 스큐, 버스(DDR 등) 그룹 길이 편차
  - **레이어 전환**: 고속 넷의 비아 수(reference plane 불연속)
  - **스터브/분기**: T-분기, 미사용 스터브
- 도메인 가이드는 `references/pcb-analysis.md` 참조.

### 5.2 전원 무결성 (PI)

- 입력 수집: `mcp__kicad__query_zones`(레이어별 카퍼 존 = 평면 커버리지),
  `mcp__kicad__query_traces`(전원 넷 폭), `mcp__kicad__get_net_pads` + `get_component_list`(디커플링 캡 ↔ 전원 핀 거리)
- 검토 항목:
  - 전원/GND **평면(plane)** 존재 및 분할 적정성
  - 전원 넷 트랙/평면 폭 대비 전류(IR drop 추정)
  - 디커플링 캡 배치 근접성(핀 ↔ 캡 거리)
  - 비아 stitching(평면 연결) 충분성

---

## 단계 6: 종합 분석 보고서

```
═══════════════════════════════════════════
  KiCad 회로/PCB 분석 보고서
═══════════════════════════════════════════

프로젝트: {프로젝트명}
대상: {.kicad_sch} / {.kicad_pcb}
분석된 보드: {get_backend_state 의 boardPath — MCP 사용 시 필수}
엔진: {KiCAD-MCP-Server (pcbnew) | kicad-cli | 직접 파싱}
분석일: {날짜}

━━━ 요약 ━━━
  회로(넷리스트):  넷 {n} / 부품 {n} / ERC  OK {n} · WARN {n} · ERROR {n}
  동기화:          회로도에만 {n} / 보드에만 {n} / 넷 불일치 {n} · 패리티 {n}건  → {동기화됨 | 불일치 | 미수행}
  PCB:            풋프린트 {n} / 트랙 {n} / 비아 {n} / DRC  OK {n} · WARN {n} · ERROR {n}
  배치:            에어와이어 상위 넷 {넷명}({길이}mm) / 코트야드 겹침 {n} / 클리어런스 위반 {n}
  SI/PI:          {수행/heuristic/미수행} — 이슈 {n}

━━━ ERROR 항목 ━━━
  [ERROR] [{ERC|DRC|PIN|SI|PI}] {설명}
     위치: {넷/부품/좌표}
     근거: {규칙/측정값}
     조치: {구체적 수정}

━━━ WARN 항목 ━━━
  [WARN] [{카테고리}] {설명} — {권장}

━━━ 미수행/제한 항목 ━━━
  [미수행] {항목}: {사유 — 예: "트랙 기하 분석 — MCP 미등록" / "절대 임피던스 — Board Setup > Physical Stackup 미설정"}
     → 활성화: kicad-setup 스킬로 KiCAD-MCP-Server 등록 후 재실행
```

**보드 상태 정리**: 파이썬 브리지는 보드를 **한 번에 하나만** 들고 있다.
두 프로젝트를 번갈아 분석하면 두 번째 `open_board`가 첫 번째를 조용히 대체한다.
그래서 보고서 헤더에 `get_backend_state`의 `boardPath`를 찍어 **어떤 보드를 실제로 분석했는지** 남기고,
분석이 끝나면 `mcp__kicad__close_project`로 정리한 뒤 다음 보드를 연다.

### 보고서 원칙

- **근거 명시**: 모든 ERROR/WARN에 규칙명 또는 측정값(트랙 폭 µm, 길이 mm, clearance mil)을 붙인다.
- **추측 금지**: 엔진이 측정하지 못한 항목은 "미수행"으로 솔직히 표시한다 — "아마 괜찮음" 금지.
- **구체적 조치**: "넷 +3V3 트랙폭 0.25mm → 0.5mm 이상(예상 전류 1.2A 기준)" 처럼 수치로.
- **활성화 안내**: 폴백으로 막힌 분석은 KiCAD-MCP-Server 등록 경로(kicad-setup)를 안내한다.
- **동기화 실패는 맨 위에**: 단계 3.5 가 ERROR 면 PCB 분석 결과 전체가 낡은 보드 기준이므로, 개별 항목보다 먼저 적는다.
- **엔진 한계와 데이터 한계를 구분**: "MCP 미등록"(등록하면 해결)과 "Board Setup > Physical Stackup 미설정"(등록해도 해결되지 않고, 사용자가 KiCad에서 스택업을 채워야 해결)을 같은 줄로 뭉뚱그리지 않는다.

---

## 에이전트 위임

실제 분석은 전용 에이전트에 위임한다:

- **kicad-pcb-analyzer**: 엔진 감지 → 넷리스트/ERC/DRC/트랙/SI·PI 분석 → 보고서 작성

이 에이전트는 `tools:`를 명시하지 않아 등록된 모든 도구를 상속하므로, KiCAD-MCP-Server(`mcp__<서버명>__*`)가 있으면 1순위로 쓰고 없으면 kicad-cli/직접 파싱으로 폴백한다. 에이전트는 `kicad-setup` 스킬로 타겟 프로젝트의 `.claude/agents/`에 설치한다.

---

## 참조 파일

- `references/mcp-tools.md` — KiCAD-MCP-Server 도구 카탈로그(도구 탐색 3종 포함) + 엔진별 매핑 + 설치/등록
- `references/pcb-analysis.md` — PCB 물리 분석·SI/PI 도메인 가이드 + 직접 파싱 방법

## 사용 예시

```
사용자: "이 보드 PCB 분석해줘"
사용자: "DRC 돌리고 미라우팅 넷 찾아줘"
사용자: "+3V3 넷에 뭐가 연결됐는지 추적해줘"
사용자: "Ethernet 차동 페어 임피던스랑 길이 매칭 확인해줘"
사용자: "핀 충돌 있는지 ERC 검사해줘"
사용자: "배선 전에 배치 괜찮은지 봐줘"
사용자: "회로도랑 보드 동기화됐는지 확인해줘"
```

$ARGUMENTS
