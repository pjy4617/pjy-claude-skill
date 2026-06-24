---
name: pcb-design-digest
description: "PCB 설계/제조 데이터(거버 팹 출력 폴더 — RS-274X/X2 .gbr/.pho·Excellon 드릴 .drl / PADS 레이아웃 — .pcb 바이너리·.asc ASCII / KiCad 소스 — .kicad_pcb·.kicad_sch·.kicad_pro)를 한 번만 파싱·요약하여 마크다운 다이제스트로 저장하고, 이후 작업에서 보드 정보가 필요할 때마다 원본을 다시 파싱하지 않고 다이제스트(보드 외곽·레이어·넷·부품·애퍼처/드릴 통계·이슈)를 1차 참조하는 워크플로. 디테일이 필요할 때만 원본의 특정 레이어/넷/좌표만 핀포인트로 재파싱. 사용자가 '이 거버/PADS/KiCad 등록해줘', 'PCB 다이제스트 만들어줘', '이 .pcb 파일 분석해서 저장해줘', '이 .kicad_pcb 다이제스트', '보드 인덱싱', '/pcb-design-digest <경로>', 'PCB 다이제스트', '거버 다이제스트', '등록된 보드 목록', '보드 다이제스트 제거', 'pcb design digest', 'gerber digest' 등을 요청하거나, 거버/드릴 폴더·PADS .pcb/.asc·KiCad 소스를 가리키며 등록·요약·인덱싱·갱신·삭제·목록을 명시할 때 자동 적용. 거버·KiCad·PADS ASCII는 텍스트라 Read/Grep/Bash로, PADS 바이너리 .pcb는 strings 부분 추출(MCP·gerbv 불필요). 깊은 분석은 pcb-design-analyst 에이전트에 위임. 첫 사용 전에는 pcb-design-digest-setup으로 환경을 1회 초기화한다."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# PCB 설계 다이제스트 (PCB Design Digest)

PCB 설계/제조 데이터를 **한 번만** 파싱·요약하여 마크다운 다이제스트로 만들고, 이후 작업에서는 다이제스트를 1차 참조원으로 삼는 워크플로. 디테일이 필요할 때만 원본의 **특정 레이어/넷/좌표**만 핀포인트로 다시 읽는다. `manual-digest`의 PCB 버전이며, 거버 전용 다이제스트에서 **거버 + PADS + KiCad** 세 입력군으로 확장한 후속이다.

## 왜 이 스킬이 중요한가

PCB 데이터는 거버 세트(수십 KB~수 MB), PADS `.pcb`(수백 KB 바이너리), KiCad `.kicad_pcb`(수백 KB~수 MB S-expression)로 크고, 매번 보드 정보를 물으면 ① 토큰을 매번 소비하고 ② 외곽/레이어/넷/애퍼처/드릴을 매번 다시 파싱하며 ③ 단위·좌표·포맷 함정을 매번 다시 디코드하는 낭비가 발생한다. 한 번 다이제스트를 만들면 동일 정보가 수 KB로 압축되어, 이후 "이 보드 외곽 몇 mm야?", "홀 몇 개야?", "레이어 몇 층?", "넷 몇 개?", "최소 트레이스 폭은?" 같은 질문이 즉시 처리된다.

## 입력 — 세 입력군

`<path>`는 아래 셋 중 하나다. 스킬이 경로·확장자·내용 시그니처로 **입력군을 자동 판별**한다(§워크플로 1단계).

| 입력군 | `format` | 받는 것 | 파싱 방식 | 추출 가이드 |
|--------|----------|---------|-----------|-------------|
| **거버/드릴 팹 출력** | `gerber` | 폴더(`.pho`/`.gbr`/`.ger`/`.gtl`/`.gbl`/`.drl`/`.gbrjob`/`.rep`/`.lst` …) | 전부 텍스트 → Read/Grep | `references/gerber-extract.md` |
| **PADS 레이아웃** | `pads` | `.pcb`(바이너리 네이티브) 또는 `.asc`(ASCII export) | `.asc`=전체 텍스트 파싱 / `.pcb`=`strings` **부분 추출** | `references/pads-extract.md` |
| **KiCad 소스** | `kicad` | `.kicad_pcb`(PCB) / `.kicad_sch`(회로도) / `.kicad_pro`(프로젝트) | S-expression 텍스트 → Read/Grep | `references/kicad-extract.md` |

> **PADS 바이너리 `.pcb`는 부분 추출이다.** 네이티브 `.pcb`는 사유 바이너리라 좌표·트랙 등 기하 정보를 완전 복원할 수 없다 — `strings`로 보드명·팹 스펙(예: `2.4T / FR-4 / 1oz /2Layer / HASL`)·넷 이름·데칼(footprint) 이름·레이어 설정만 신뢰성 있게 뽑는다. **완전 충실도가 필요하면 PADS에서 ASCII(`.asc`)로 export**하라고 안내하고, 추출 가능 범위와 한계를 다이제스트에 명시한다. KiCad·PADS ASCII·거버는 전부 텍스트라 완전 파싱된다.

## 사용 시기

다음 중 하나라도 해당하면 본 스킬을 적용한다:
- 사용자가 거버 폴더 / PADS(`.pcb`/`.asc`) / KiCad(`.kicad_pcb`/`.kicad_sch`/`.kicad_pro`) 경로를 지목하며 "등록", "다이제스트", "요약", "인덱싱", "분석 저장"을 요청
- `/pcb-design-digest <경로>`, `/pcb-design-digest --update <id>`, `--list`, `--remove <id>`
- "이 보드 자주 볼 것 같아", "매번 파싱하기 싫어", "보드 정보 빨리 찾게 다이제스트 만들어줘" 같은 의도 표현
- 같은 보드 데이터를 두 번째 이상 참조 — 다이제스트화 제안

다음은 **본 스킬을 쓰지 않는다**:
- 1회성 단발 질문 (그땐 `pcb-design-analyst` 에이전트만 호출하거나 직접 답)
- KiCad에 대한 **라이브 ERC/DRC·넷 추적·SI/PI 분석** — 그건 `kicad-analyze` 스킬(이건 *영속 압축 다이제스트* 생성에 집중). 단, KiCad 소스를 **다이제스트로 등록**하고 싶으면 본 스킬이 맞다(둘은 상보적).

## 사전 조건

`/pcb-design-digest-setup`으로 환경 초기화가 끝나 있으면 가장 매끄럽다(디렉토리 + INDEX.md + CLAUDE.md 마커 + `pcb-design-analyst` 에이전트 설치). 미초기화여도:
- `.claude/pcb-designs/` 부재 → 자동 생성 후 진행
- 에이전트 미설치 → 직접 파싱(폴백) 경로로 진행. MCP·gerbv 불필요.

## 산출물 위치

```
<scope_root>/.claude/pcb-designs/
├── INDEX.md                       ← 마스터 카탈로그 (보드 1줄 요약)
├── <board-id>/
│   ├── digest.md                  ← 개요 + 인벤토리 + 물리/전기/이슈 요약
│   ├── index.md                   ← 파일/레이어/넷 → 역할 + 핀포인트
│   └── metadata.json              ← id/source/format/cad_tool/units/layers/nets/holes/sha256...
└── ...
```

- `--scope project` (기본): `<project>/.claude/pcb-designs/`
- `--scope global`: `~/.claude/pcb-designs/`

산출물 형식 상세는 `references/pcb-design-digest-format.md`, 입력군별 추출 절차는 `references/gerber-extract.md`(거버) · `references/pads-extract.md`(PADS) · `references/kicad-extract.md`(KiCad).

## 서브커맨드

| 호출 | 동작 |
|------|------|
| `/pcb-design-digest <경로> [--scope project\|global] [--via agent\|direct]` | 신규 인제스트 |
| `/pcb-design-digest --update <id>` | 해시로 변경 감지 → `file_hashes` 비교로 불일치 파일만 재파싱 |
| `/pcb-design-digest --list [--scope project\|global\|all]` | 등록 보드 나열 |
| `/pcb-design-digest --remove <id>` | 다이제스트 + INDEX.md 항목 + CLAUDE.md 마커 카운트 갱신 |

`--via`: 깊은 분석을 `pcb-design-analyst` 에이전트에 위임(`agent`, 기본·권장) vs 스킬이 직접 파싱(`direct`, 폴백). 에이전트 미설치면 자동으로 `direct`.

## 인제스트 워크플로 (8단계)

### 1. 입력 검증 + 입력군 판별
- 경로 정규화 + 존재/읽기 권한 확인.
- **입력군 자동 판별** (확장자 우선, 모호하면 내용 시그니처):
  - **KiCad**: 파일이 `.kicad_pcb`/`.kicad_sch`/`.kicad_pro`이거나, 폴더에 이들이 있음. 내용 시그니처 `(kicad_pcb` / `(kicad_sch` / `(kicad_symbol_lib`. → `format: kicad`
  - **PADS**: 파일이 `.asc`(첫 줄 `!PADS-POWERPCB-...` 또는 `*PADS-…*`)이거나 `.pcb`. `.pcb`는 **바이너리 PADS**(`file`이 `data`, `strings`로 `PADS`/`POWERPCB`/팹 스펙 노출) → `format: pads`. (주의: KiCad legacy도 `.pcb`를 쓰지 않으며, 거버 폴더의 `.pcb`는 없음 — `.pcb`는 PADS로 본다. 단 내용 시그니처로 재확인.)
  - **거버/드릴**: 폴더 안에 `.pho`/`.gbr`/`.ger`/`.gtl`/`.gbl`/`.cmp`/`.sol`/`.drl`/`.drd`/`.gbrjob` **또는** RS-274X 시그니처(`%FS`/`%MO`)·Excellon 시그니처(`M48` 헤더, `T<숫자>C` 드릴 정의)를 가진 파일이 있음. `.txt`는 시그니처 검사로만 Altium Excellon으로 인정(일반 텍스트 화이트리스트 제외). → `format: gerber`
  - 어느 것도 아니면 "PCB 입력을 못 찾음" 안내 후 종료.
- **단일 거버 파일** 입력이면 부모 디렉토리를 세트 폴더로 승격해 인제스트하고 레이어 부족을 경고한다. **PADS/KiCad는 단일 파일 입력이 정상**(거버만 폴더 단위).

### 2. ID 결정
- 거버: job명(`.pho` 헤더 `%IN "..."`) 또는 폴더명. PADS: `.pcb`/`.asc` 내부 보드명 또는 파일명. KiCad: 프로젝트/파일명. → 소문자 kebab-case (예: `DAISY_CON_J4-O_MDR_20160419.pcb` → `daisy-con-j4-o-mdr-20160419`).
- 같은 ID 존재 시: sha256 비교 → 일치하면 "이미 등록됨, --update 안내" 후 종료, 불일치면 사용자 확인 후 덮어쓰기.

### 3. 인벤토리 (작은 것 먼저)
입력군별 추출 가이드의 1단계를 따른다.
- **거버**: 작은 리포트(`.rep`/`.lst`/`.gbrjob`)를 먼저 Read해 애퍼처·드릴 인벤토리를 싸게 확보, 큰 `.pho`는 헤더만 Read. (`references/gerber-extract.md`)
- **PADS `.asc`**: 섹션 헤더(`*PART*`/`*NET*`/`*SIGNAL*`/`*MISC*` 등)를 Grep해 구조 파악. **`.pcb` 바이너리**: `strings -n 4`로 보드명·팹 스펙·넷·데칼·레이어 토큰만 수집. (`references/pads-extract.md`)
- **KiCad**: `(layers …)`, `(net …)`, `(footprint …)`, `(gr_line …)`(Edge.Cuts), `(setup …)` 스탠자를 Grep으로 카운트·추출. (`references/kicad-extract.md`)

### 4. 디코드 (CAD 툴 / 단위 / 좌표)
- **거버**: `%MO`(단위), `%FS`(좌표 포맷), 드릴 포맷은 헤더 없으면 패드 플래시 앵커링. 단위 혼재(본문 inch vs .rep mm) 주의. (`references/gerber-extract.md` 2단계)
- **PADS**: `.asc` 헤더의 단위(`*PADS-POWERPCB-V…-BASIC*` 다음 `*MILS*`/`*METRIC*`/`*INCHES*`). `.pcb` 바이너리는 단위 토큰을 strings에서 확인하되 좌표 스케일 단정 금지. (`references/pads-extract.md`)
- **KiCad**: 좌표 단위는 **항상 mm**(고정). 레이어 정의는 `(layers …)`. (`references/kicad-extract.md`)

### 5. 깊은 파싱
- **`--via agent`(기본)**: `pcb-design-analyst` 에이전트를 Agent 도구로 호출(`subagent_type: "pcb-design-analyst"`). 프롬프트에 **입력군(format)** + 절대경로 + "다이제스트용: 출력 형식 1~6 전 섹션을 표·수치 위주로" 지시. 에이전트의 보고서(최종 메시지)가 다이제스트 본문 원천.
- **`--via direct`(폴백)**: 해당 입력군의 추출 가이드 3~4단계를 스킬이 직접 수행(거버=애퍼처 대조·드릴 교차검증·외곽 bbox / PADS=섹션 파싱 또는 strings 분류 / KiCad=스탠자 집계).

### 6. sha256 산출
- **폴더 입력(거버)**: `references/gerber-extract.md` 5단계의 정본 `gd_manifest`로 **폴더 단일 해시**(빠른 변경 게이트) + **파일별 해시 매니페스트**(`file_hashes` — `--update` 근거)를 산출. 공백 파일명·로케일에 안전한 `-print0`/`LC_ALL=C sort -z`/`while read -d ''` 형태.
- **단일 파일 입력(PADS/KiCad)**: 해당 파일 1개의 `sha256sum`을 `sha256` 및 `file_hashes`에 기록(`.kicad_pro`+`.kicad_pcb`처럼 동반 파일이 함께 오면 각각 해시). KiCad 프로젝트 폴더 통째로 받으면 `gd_manifest` 사용.

### 7. 산출물 작성
`references/pcb-design-digest-format.md` 스키마대로 `digest.md` + `index.md` + `metadata.json` 작성. **모든 치수 inch·mm 병기**(KiCad는 mm 기준), 확정/추정 구분, 근거(파일·라인·D-code·넷명) 명시. **부분 추출(PADS 바이너리)은 한계를 명시**. `indexed_at`은 `date -u +%Y-%m-%dT%H:%M:%SZ`로 stamp.

### 8. 마스터 카탈로그 갱신
- `<scope>/.claude/pcb-designs/INDEX.md`에 1줄 항목 추가 (보드명·format·외곽·레이어·넷/홀 수·scope).
- 같은 scope `CLAUDE.md` 마커 블록의 `(현재 N개)` 카운트만 갱신.

## 결정성

- 동일 sha256 재인제스트 → "이미 등록됨" 안내, 재파싱 안 함.
- `--update`는 변경 파일만 재파싱(metadata `file_hashes` 비교), 비변경분 보존.
- 산출물 형식(스키마, JSON 키, 헤딩 구조)은 결정적. LLM 요약/이슈 판정은 비결정적이나 형식은 고정.

## 활용 (Claude의 동작 규칙)

사용자가 보드/PCB 정보가 필요한 질문을 할 때:

1. 두 INDEX.md 확인 (project가 global을 override):
   - `<project>/.claude/pcb-designs/INDEX.md`
   - `~/.claude/pcb-designs/INDEX.md`
2. 관련 보드가 있으면 `digest.md`를 먼저 읽는다.
3. digest로 답할 수 있으면 출처(파일·D-code/넷·scope) 명시.
4. 디테일이 부족하면 `index.md`에서 파일/라인 포인터 → 원본의 해당 부분만 `Read`/`Grep`(PADS 바이너리는 `strings | grep`). SI/PI·차동쌍·플레인 분할 등 깊은 분석은 `pcb-design-analyst` 에이전트 재호출.
5. 인덱싱되지 않은 보드면 `/pcb-design-digest <경로>` 등록 제안.

## 에지케이스

| 상황 | 동작 |
|------|------|
| 같은 ID 재등록 (동일 sha256) | "이미 등록됨, --update로 갱신" 안내 후 종료 |
| 같은 ID 재등록 (다른 sha256) | 사용자 확인 후 덮어쓰기 |
| 폴더/파일에 PCB 데이터 없음 | "거버/PADS/KiCad 입력 미발견" 안내, 경로 재확인 요청 |
| 단일 거버 파일 입력 | 부모 폴더를 세트로 보고 인제스트(레이어 부족 경고) |
| PADS 바이너리 `.pcb` | strings 부분 추출 — 추출 범위·한계 명시 + `.asc` export 권장 |
| `.asc`/KiCad 단일 파일 | 정상(완전 텍스트 파싱) |
| 에이전트 미설치 | 자동 `--via direct` 폴백, 한계(깊은 분석 제한) 명시 |
| 드릴 포맷 헤더 없음(거버) | 패드 플래시 앵커링으로 확정 (`references/gerber-extract.md`) |
| `.claude/pcb-designs/` 쓰기 권한 부재 | 명시적 에러 + scope 변경 제안 |
| ID 충돌 (project + global) | project가 override; `--scope global` 명시 시 경고 |

## 흔한 함정

| 함정 | 해결 |
|------|------|
| PADS 바이너리 `.pcb`를 완전 파싱한 것처럼 기술 | strings 추출은 부분 — `extraction: partial` + 한계 명시, 좌표/외곽 단정 금지 |
| 큰 실크 .pho / 큰 .kicad_pcb 전체 Read | 헤더 + 필요한 좌표/스탠자만 핀포인트(Grep/Read offset) |
| `.rep`(mm)와 본문(inch) 단위 혼동 | 결과는 inch·mm 둘 다 병기, 혼재 사실 메모 |
| KiCad 좌표를 inch로 가정 | KiCad 좌표는 항상 mm — inch는 환산값만 병기 |
| 외곽을 좌표 bbox로 확정 못 했는데 확정처럼 기술 | `board_size_confirmed: false` + "추정" 명시 |
| 깊은 분석을 스킬이 떠안음 | SI/PI·플레인·제조성 종합은 `pcb-design-analyst`에 위임 |

## 마무리 보고

인제스트 완료 시 사용자에게:
1. 산출물 경로 (digest.md / index.md / metadata.json)
2. 입력군(format)과 압축비 (원본 크기 vs 다이제스트)
3. 핵심 발견 요약 (외곽·레이어·넷·홀·주요 이슈) + (PADS 바이너리면) 추출 한계
4. 등록된 scope, 다음 단계 (이후 보드 질문 시 자동 참조됨)

$ARGUMENTS
