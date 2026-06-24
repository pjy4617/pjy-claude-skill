# PADS 추출 워크플로 (저비용 다이제스트 빌드)

PADS 입력을 **싸게** 다이제스트화하는 절차. PADS 입력은 **두 가지 변종**이며 추출 난이도와 신뢰도가 완전히 다르다 — 어느 쪽인지부터 판정한다.

- **(A) `.asc` (PADS ASCII / PowerPCB ASCII export)** — 전부 텍스트. `Read`/`Grep`/`Bash`로 완전 파싱(`extraction=full`). **고신뢰 경로 — 가능하면 항상 이것을 권장.**
- **(B) `.pcb` (PADS Layout / PowerPCB 네이티브 바이너리)** — 바이너리. `strings`로 **이름·스펙·넷 라벨만** 부분 추출(`extraction=partial`). 좌표/외곽/트랙 기하는 **복구 불가**.

> 깊은 분석(SI/PI, 차동쌍, 플레인 분할, 제조성 종합 판정)은 `pcb-design-analyst` 에이전트에 위임한다. 이 가이드는 다이제스트 골격을 만드는 추출 절차에 집중한다.

## 0. 변종 판정 (먼저)

```bash
file <input>            # ".asc" 라도 내용으로 확인. "ASCII text" → A경로, "data"/binary → B경로
head -1 <input>         # .asc면 !PADS-POWERPCB-... 헤더가 보임. 안 보이면 바이너리로 취급
```

확장자만 믿지 말 것 — `.pcb`라도 export된 ASCII일 수 있고, 그 반대도 있다. **`file`이 `data`/binary면 무조건 B경로(partial)**.

---

## A. PADS ASCII (.asc) — 고신뢰 전체 파싱 (`extraction=full`)

### A-1. 헤더 / 단위 디코드 (필수, 먼저)

첫 줄이 버전·단위를 준다:

```
!PADS-POWERPCB-V9.5-MILS! HKBD ...
                  └버전   └단위 토큰
```

- 단위 토큰: **`*MILS*` / `*METRIC*`(=mm) / `*INCHES*` / `*BASIC*`**. 헤더 또는 `*MISC*` 블록 안 `UNITS` 라인에 위치.
- **모든 좌표·치수는 이 단위** — 추측 금지. 단위 확정 후 산출물은 mm·inch 둘 다 병기(MILS↔mm는 ×0.0254/÷0.0254).

### A-2. 섹션 마커 인벤토리

`.asc`는 `*SECTION*` 마커로 구획된다. 출현 마커를 한 번에 잡는다:

```bash
grep -n '^\*' <input>.asc     # 모든 섹션 헤더 + 라인 번호 → index.md 핀포인트로 사용
```

| 마커 | 내용 |
|------|------|
| `*PART*` | 부품 배치 인스턴스(레퍼런스·데칼·좌표·회전) |
| `*NET*` | 넷 정의(넷명 + 소속 핀 리스트) |
| `*SIGNAL*` | 시그널/라우팅(트랙 정점) |
| `*POUR* / *COPPER*` | 카퍼 푸어(플레인/영역) |
| `*VIA* / *PARTDECAL*` | 비아 정의 / 데칼(footprint) 정의 |
| `*LINES*` | 보드 외곽·실크·도큐 라인(외곽 폴리라인이 여기 있을 수 있음) |
| `*TEXT*` | 실크/도큐 텍스트 |
| `*MISC*` | 보드 전역 설정(단위·레이어·룰·보드 외곽) |
| `*END*` | 파일 종료 |

### A-3. 카운트 집계 (Grep)

각 인스턴스는 섹션 내 비들여쓰기(레코드 시작) 라인이다. 섹션 범위를 잘라 카운트한다:

```bash
# 섹션 한 구간만 추출하는 헬퍼: 다음 '*SECTION*' 전까지
sec() { awk -v s="$1" '$0~"^\\*"s"\\*"{f=1;next} /^\*/{f=0} f' "$2"; }

sec PART  <input>.asc | grep -cE '^[^ \t]'   # 부품 수 (레코드 시작 라인)
sec NET   <input>.asc | grep -cE '^\*\*'     # 넷 수 (PADS는 넷 레코드가 **NETNAME 형식인 경우 多)
sec SIGNAL <input>.asc | grep -cE '^[^ \t]'  # 시그널/라우팅 레코드 수
```

> NET 레코드 시작 토큰은 버전마다 다르다(`*NET*` 하위에 `**` 또는 `*SIGNAL*` 라벨). 실제 첫 5~10줄을 Read해 레코드 경계 패턴을 확정한 뒤 `grep -c`를 맞춘다 — 패턴을 단정하지 말 것.

### A-4. 보드 외곽 / 드릴·패드 스택

- **외곽**: `*MISC*`의 보드 라인 또는 `*LINES*`의 보드 윤곽 폴리라인(닫힌 루프)에서 좌표 bbox 계산 → A-1 단위로 환산. 좌표로 닫힌 외곽이면 `board_size_confirmed: true`.
- **드릴/패드 스택**: `*PARTDECAL*`(데칼별 패드 스택)과 비아 정의에서 드릴 직경·패드 형상·도금 여부를 읽는다. 데칼별로 핀 패드 스택이 정의되므로 홀 직경은 거기서 확정.
- 모든 수치는 단위 환산 후 mm·inch 병기.

### A-5. 산출 → `extraction=full`

`pcb-design-digest-format.md` 스키마대로 `digest.md`/`index.md`/`metadata.json` 작성. `nets_total`/`components_total`을 실수로 채울 수 있는 **고신뢰 입력**이다.

---

## B. PADS 바이너리 (.pcb) — strings 부분 추출 (`extraction=partial`)

네이티브 `.pcb`는 바이너리라 좌표/외곽/트랙을 디코드할 수 없다. `strings`로 **임베드된 텍스트 토큰만** 회수한다.

### B-1. 추출 레시피

```bash
file board.pcb            # → "data" (바이너리) 확인
strings -n 4 board.pcb | grep -iE 'pads|powerpcb|version'                 # CAD 툴·버전
strings -n 4 board.pcb | grep -iE 'FR-?4|HASL|ENIG|oz|layer|/.*T'        # 팹 스펙(두께/동박/표면처리)
strings -n 4 board.pcb | grep -iE '\+?[0-9]*V[_A-Z0-9]*|GND|VCC|NET'     # 넷 라벨 후보
strings -n 4 board.pcb | grep -iE 'VIA|DECAL|[0-9]+PIN|SIP|MH_|[0-9]+K$|1N[0-9]' # 데칼/부품/비아
strings -n 4 board.pcb | grep -iE 'DOC_|APERTURE|POLAR_GRID|LAYER_'      # CAM/도큐 설정 토큰(넷 아님)
```

### B-2. 실증 예시 (`DAISY_CON_J4-O_MDR_20160419.pcb`, 252 KB)

`file` → `data`(바이너리). `strings`로 회수한 것:

- **보드명**: `DAISY_CON_J4_MDR-O_20160419.pcb`
- **팹 스펙**: `2.4T / FR-4 / 1oz /2Layer / HASL` → 두께 2.4mm, FR-4, 1oz 동박, **2층**, HASL 표면처리
- **넷명**: `+24V_`, `+24VG_`, `NC_NET`
- **데칼/부품**: `10120-3000`, `37212-62M3-003SC`(3M MDR 커넥터), `2MM_9PIN`, `SIP_3P_2MM`, `MH_3528_PD/PDA/PDB/PT`, `1N4148`(다이오드), `390K`(저항), `STANDARDVIA`/`JMPVIA_AAAAA`(비아)
- **CAM/도큐 설정 토큰**: `APERTURE_1..31+`, `DOC_LAYER_NAMES/NUMBERS/TYPES`, `DOC_PADS`, `POLAR_GRID` — **넷·부품이 아님(CAM 설정)**

회수 불가: 외곽 치수, 트랙 폭/경로, 패드 좌표. `7620000`/`3048000`/`1905000`/`381000`/`27000000` 같은 큰 정수는 **PADS 내부 기하 단위**일 뿐 — strings만으로 보드 피처/좌표로 매핑할 수 없으니 **좌표로 해석 금지**.

### B-3. 산출 → 반드시 `partial`로 표기 + export 권장

- `metadata.json`: `extraction: "partial"`, `board_size_confirmed: false`, `board_size_mm/inch: null`, `coord_format: "binary (strings 추출 — 좌표 디코드 불가)"`, `units: "unknown"`(또는 팹 스펙에서 두께만 확정).
- `digest.md` 첫 문단과 「한계」 섹션에: **"부분 추출(strings 기반) — 기하/좌표 불가. 정밀 분석은 PADS에서 `File > Export > ASCII`(.asc) 또는 Gerber 출력 후 재인제스트 필요."** 명시.
- 넷·데칼 목록은 "strings 토큰 출처"임을 근거로 표기(완전 목록 보장 아님).

---

## sha256 (재인제스트 판별)

PADS 입력은 보통 **단일 파일** → `sha256sum <file>`로 해시. (거버 폴더처럼 다중 파일이면 `gerber-extract.md` 5단계 정본 `gd_manifest` 사용 — 문서 간 명령 분기 금지.) 해시가 같으면 재파싱 안 함.

## 흔한 함정

| 함정 | 해결 |
|------|------|
| 바이너리 `.pcb`를 완전 파싱한 것처럼 표기 | `extraction=partial` + `board_size_confirmed=false` 고정, `.asc`/Gerber export 권장 명시 |
| CAM 설정 토큰을 넷으로 오인 | `ADD_MULTIPLE_FOR_POWERNET`/`DOC_COLOR_BY_NET`/`DOC_*`/`APERTURE_*`/`POLAR_GRID`는 CAM 설정 — 넷 아님 |
| 큰 정수 토큰을 좌표로 해석 | PADS 내부 기하 단위 — strings만으로 보드 좌표 매핑 불가, 외곽/트랙 단정 금지 |
| 단위 추측(mil vs mm) | `.asc`는 헤더/`*MISC*`의 `*MILS*`/`*METRIC*`/`*INCHES*` 토큰 확인; `.pcb`는 `units: unknown` |
| 확장자만으로 변종 판정 | `file`/`head -1`로 ASCII vs binary 실제 확인 후 경로 선택 |
| `.asc` NET 레코드 경계 패턴 단정 | 버전마다 다름 — 섹션 첫 줄 Read로 레코드 시작 토큰 확정 후 `grep -c` |
| 팹 스펙 문자열의 `2Layer`를 놓침 | 동박 레이어 수는 팹 스펙에서 확정(예 `2Layer`→layers:2) |

깊은 분석(SI/PI·차동쌍·플레인 분할·제조성 종합)은 `pcb-design-analyst` 에이전트에 위임하고, 산출물 형식은 `pcb-design-digest-format.md`를 따른다.
