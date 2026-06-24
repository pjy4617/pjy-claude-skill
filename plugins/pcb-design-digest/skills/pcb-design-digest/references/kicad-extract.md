# KiCad 소스 추출 워크플로 (저비용 다이제스트 빌드)

KiCad 설계 소스를 **싸게** 다이제스트화하는 절차. 핵심 원칙: **Grep 카운트로 인벤토리 먼저, 큰 파일 전체 Read 금지**. KiCad 소스는 전부 S-expression 텍스트(`.kicad_pro`만 JSON)라 MCP·kicad-cli 불필요 — `Read`/`Grep`/`Bash`로 파싱한다. **좌표는 항상 mm**(단위 디코드 불필요).

> 깊은 분석(SI/PI, 차동쌍, 플레인 분할, 라우팅 품질 종합 판정)은 `pcb-design-analyst` 에이전트에 위임한다. 이 가이드는 다이제스트 골격을 만드는 추출 절차에 집중한다.
>
> **스킬 경계**: `kicad-analyze` 스킬은 **실시간** ERC/DRC·넷 추적·핀 충돌을 수행한다(라이브 검증). 반면 **이 가이드는 영속 다이제스트만 추출**한다 — 다음에 같은 보드를 다룰 때 원본을 다시 파싱하지 않게 하는 게 목적이라 상호 보완적이다.

## 추출 경로 두 가지

1. **에이전트 위임(권장, 기본)** — `pcb-design-analyst` 에이전트를 Agent 도구로 호출(`subagent_type: "pcb-design-analyst"`)하여 전 구조 보고서를 받는다. 그 보고서를 `pcb-design-digest-format.md` 스키마로 재배치해 `digest.md`로 저장. 에이전트는 분석 노하우를 자체 메모리에 누적하므로 반복 보드에서 점점 빨라진다.
2. **직접 파싱(폴백)** — 에이전트가 설치돼 있지 않거나(`/pcb-design-digest-setup` 미실행) 보드가 단순하면, 아래 단계를 스킬이 직접 수행한다.

어느 경로든 산출물 형식은 `pcb-design-digest-format.md` 스키마로 동일(`format: kicad`, `extraction: full`, `units: mm`).

## 0. 파일 역할 식별

| 파일 | 포맷 | 역할 |
|------|------|------|
| `*.kicad_pro` | JSON | 프로젝트 메타 — 보드명·DRC 룰·넷클래스·페이지 설정. 작아서 전체 Read 가능 |
| `*.kicad_pcb` | S-expr | 보드(레이어 스택·풋프린트·트랙·비아·존·외곽). 보통 가장 큼 → **Grep만** |
| `*.kicad_sch` | S-expr | 회로도(심볼·라벨·시트). 멀티시트면 여러 파일 |
| `*.kicad_dru` | text | 커스텀 DRC 룰(있으면 — 클리어런스·폭 규칙 보강 근거) |
| `*.net` | S-expr | 익스포트 넷리스트(있으면 — 넷↔핀 매핑 교차검증용) |

루트 `.kicad_pro`의 베이스명 = 보드 id 후보. 멀티시트는 루트 `.kicad_sch`가 하위 시트를 `(sheet ...)`로 참조한다.

## 1. 저비용 인벤토리 (Grep 카운트)

큰 파일은 절대 전체 Read하지 말고 **카운트만** 뽑는다(`grep -c` 또는 `grep -o ... | wc -l`):

```bash
# 부품 수 (PCB 풋프린트) — 보드에 실제 배치된 부품
grep -c '(footprint ' board.kicad_pcb

# 넷 목록/수 — (net <N> "<name>") 한 줄당 한 넷
grep -oE '\(net [0-9]+ "[^"]*"\)' board.kicad_pcb | sort -u

# 트랙(세그먼트) / 비아 수
grep -c '(segment ' board.kicad_pcb
grep -c '(via '     board.kicad_pcb

# 존(플레인) — net_name 별 채움 영역
grep -oE '\(zone .*\(net_name "[^"]*"' board.kicad_pcb

# 외곽: Edge.Cuts 위의 라인/아크
grep -E '"Edge.Cuts"' board.kicad_pcb | grep -cE '\(gr_line|\(gr_arc'

# 레이어 스택 — (layers ...) 스탠자에서 동박층(.Cu) 카운트
grep -oE '"[A-Za-z0-9.]+\.Cu"' board.kicad_pcb | sort -u | wc -l

# 보드 두께
grep -oE '\(thickness [0-9.]+\)' board.kicad_pcb        # (general ...) 안

# 회로도 심볼 수 (라이브러리 심볼 인스턴스)
grep -c '(symbol (lib_id' sheet.kicad_sch
```

- `(footprint ...)`=PCB 부품 수, `(net N "name")`=넷 리스트/수, `Edge.Cuts`의 `(gr_line ...)`/`(gr_arc ...)`=외곽, `(segment ...)`/`(via ...)`=트랙/비아.
- `(layers (...))` 스탠자에서 `*.Cu` 종류를 세면 **동박 레이어 수**(예: `F.Cu`/`B.Cu`=2층, `In1.Cu`~`In2.Cu` 추가=4층).
- `(setup ...)` 스탠자=디자인 룰(최소 트랙폭·클리어런스·비아 드릴), `(general (thickness ...))`=보드 두께.

## 2. 외곽 bbox 계산 (Edge.Cuts, mm 고정)

좌표는 mm이므로 **단위 환산 없이** Edge.Cuts의 `(gr_line ... (start x y)(end x y))`에서 min/max를 모은다:

```bash
# Edge.Cuts gr_line의 start/end xy만 뽑아 bbox
grep -A4 '(gr_line' board.kicad_pcb | grep -B2 '"Edge.Cuts"' -A0 >/dev/null
# 실전: layer 토큰이 같은 스탠자 안에 있으므로 한 줄 정규화 후 awk
grep -oE '\(gr_line \(start [-0-9.]+ [-0-9.]+\) \(end [-0-9.]+ [-0-9.]+\)[^)]*"Edge.Cuts"' board.kicad_pcb \
 | grep -oE '[-0-9.]+ [-0-9.]+' \
 | awk '{if(NR==1||$1<minx)minx=$1; if(NR==1||$1>maxx)maxx=$1;
         if(NR==1||$2<miny)miny=$2; if(NR==1||$2>maxy)maxy=$2}
        END{printf "W=%.3f H=%.3f mm  (%.4f x %.4f inch)\n",
            maxx-minx, maxy-miny, (maxx-minx)/25.4, (maxy-miny)/25.4}'
```

- `(gr_arc ...)`가 외곽 라운드에 쓰이면 끝점만으로 bbox가 약간 작게 나올 수 있다 → 라운드 코너 보드는 `board_size_confirmed` 신중히(아크 반경 고려). 직선 외곽이면 확정(`board_size_confirmed: true`).
- 회전된 보드/오프셋 원점이라도 mm 절대좌표 차이라 W×H는 유효. 결과는 **mm·inch 병기**.

## 3. 넷 / 전원·접지 / 플레인

- **넷 목록**: `(net N "name")` 이름에서 전원/접지 식별 — `GND`, `GNDA`, `+3V3`, `+5V`, `+1V8`, `VCC`, `VDD` 등. 1번 넷(`(net 0 "")`)은 미연결 더미이니 카운트에서 제외 판단.
- **플레인/존**: `(zone ... (net_name "GND"))` = 그 넷의 카피 채움 영역(접지/전원 플레인). 존의 `(layer ...)`로 어느 동박층 플레인인지 기록.
- 넷 수는 `(net ...)` 유니크 카운트, 전원/접지는 이름 패턴으로 분류해 digest의 「넷 / 부품」 섹션에 근거(넷명)와 함께 기록.

## 4. 회로도 (.kicad_sch)

- **부품**: `(symbol (lib_id "Device:R") ...)` 인스턴스 = 회로도 심볼. lib_id 분포로 부품 유형 파악.
- **넷 라벨**: `(label "...")`(로컬), `(global_label "...")`(전역, 시트 간 연결), `(hierarchical_label "...")`(시트 핀). 전원 심볼(`(symbol (lib_id "power:GND"))` 등)은 라벨로 넷을 만든다.
- **멀티시트**: 루트 `.kicad_sch`의 `(sheet (property "Sheetfile" "sub.kicad_sch"))`로 하위 시트 추적 → 모든 시트의 심볼/라벨을 합산해야 전체 부품·넷이 나온다.
- 회로도 심볼 수와 PCB 풋프린트 수는 **다를 수 있다**(전원 심볼·테스트포인트는 풋프린트가 없거나 1:N) — 둘을 별도로 기록한다.

## 5. sha256 (재인제스트 판별)

KiCad 입력은 보통 **여러 파일**(`.kicad_pro`+`.kicad_pcb`+`.kicad_sch`...). 폴더 입력으로 보고 `gerber-extract.md` 5단계 정본 `gd_manifest`(파일별 맵 + 폴더 단일 해시)를 쓴다. 단일 파일만 가리키면 `sha256sum <file>`. **문서 간 명령 분기 금지**. 변경 시 `file_hashes` 비교로 바뀐 파일만 재파싱.

## 6. 다이제스트 작성

`pcb-design-digest-format.md` 스키마대로 `digest.md` + `index.md` + `metadata.json` 작성. `format: kicad`, `extraction: full`, `units: mm`, `coord_format: "mm (KiCad 고정)"`. 모든 치수 mm·inch 병기, 외곽 확정/추정 구분, 근거(파일·스탠자·넷명) 명시.

## 흔한 함정

| 함정 | 해결 |
|------|------|
| 회로도 심볼 수 = PCB 부품 수로 단정 | 전원 심볼·테스트포인트는 풋프린트 없음/불일치 — `(symbol (lib_id`(sch)와 `(footprint `(pcb)를 별도 카운트 |
| 전원 심볼(`power:GND` 등)을 부품으로 셈 | 전원 심볼은 넷 라벨일 뿐 별도 부품/넷 아님 — lib_id `power:`는 부품 카운트에서 제외 |
| 멀티시트에서 루트만 파싱 | `(sheet ... "Sheetfile")` 따라 하위 `.kicad_sch` 전부 합산 |
| 큰 `.kicad_pcb` 전체 Read | 1단계 Grep 카운트 + 필요한 스탠자만 핀포인트(Read offset/limit) |
| `(net 0 "")` 더미를 넷으로 셈 | 0번 미연결 넷 제외 후 카운트 |
| Edge.Cuts 아크 외곽을 직선 bbox로 확정 | `(gr_arc ...)` 있으면 반경 고려, `board_size_confirmed` 신중 |
| 좌표 단위 환산 시도 | KiCad는 항상 mm — 환산 불필요, inch는 ÷25.4 병기만 |
| `.kicad_pro`(JSON)를 S-expr로 파싱 | 프로젝트 파일만 JSON — `python3 -c "import json"` 또는 jq로 |

---

깊은 분석(SI/PI·차동쌍·플레인 분할·라우팅 품질)은 `pcb-design-analyst` 에이전트에 재호출로 위임한다. 산출물 형식·필드 정의는 `pcb-design-digest-format.md`를 정본으로 따른다.
