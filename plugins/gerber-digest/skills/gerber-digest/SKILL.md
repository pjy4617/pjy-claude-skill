---
name: gerber-digest
description: "거버 파일 세트(팹 출력 폴더 — RS-274X/X2 .gbr/.pho, Excellon 드릴 .drl, PADS/Altium/KiCad/Eagle 출력)를 한 번만 파싱·요약하여 마크다운 다이제스트로 저장하고, 이후 작업에서 보드 정보가 필요할 때마다 원본 거버를 다시 파싱하지 않고 다이제스트(보드 외곽·레이어 인벤토리·애퍼처/드릴 통계·이슈)를 1차 참조하는 워크플로. 디테일이 필요할 때만 원본 거버의 특정 레이어/좌표만 핀포인트로 재파싱. 사용자가 '이 거버 등록해줘', '거버 다이제스트 만들어줘', '이 팹 출력 폴더 분석해서 저장해줘', '보드 거버 인덱싱', '/gerber-digest <폴더>', '거버 다이제스트', '거버 분석 저장', '등록된 거버 목록', '거버 다이제스트 제거', 'gerber digest' 등을 요청하거나, 거버/드릴 파일이 든 폴더를 가리키며 등록·요약·인덱싱·갱신·삭제·목록을 명시할 때 자동 적용. 거버는 전부 텍스트라 Read/Grep/Bash로 파싱하며 MCP·gerbv 불필요. 깊은 분석은 gerber-pcb-analyst 에이전트에 위임. 첫 사용 전에는 gerber-digest-setup으로 환경을 1회 초기화한다."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# 거버 다이제스트 (Gerber Digest)

거버 파일 세트(팹으로 보내는 출력 폴더)를 **한 번만** 파싱·요약하여 마크다운 다이제스트로 만들고, 이후 작업에서는 다이제스트를 1차 참조원으로 삼는 워크플로. 디테일이 필요할 때만 원본 거버의 **특정 레이어/좌표**만 핀포인트로 다시 읽는다. `manual-digest`의 거버 버전이다.

## 왜 이 스킬이 중요한가

거버 폴더는 큰 실크 `.pho`까지 합치면 수십 KB~수 MB이고, 매번 보드 정보를 물으면 ① 토큰을 매번 소비하고 ② 애퍼처/드릴/외곽을 매번 다시 파싱하며 ③ 단위·좌표 포맷 함정을 매번 다시 디코드하는 낭비가 발생한다. 한 번 다이제스트를 만들면 동일 정보가 수 KB로 압축되어, 이후 "이 보드 외곽 몇 mm야?", "홀 몇 개야?", "최소 트레이스 폭은?" 같은 질문이 즉시 처리된다.

## 입력 — 폴더(거버 세트)

`<path>`는 **거버/드릴 파일이 든 폴더**다. 단일 거버 파일도 받지만, 거버는 레이어 세트로 의미가 완성되므로 폴더 단위가 기본이다. 폴더 안에 `.pho`/`.gbr`/`.ger`(RS-274X), `.drl`/`.txt`(Excellon), `.rep`/`.lst`(PADS 리포트), `.gbrjob`(KiCad job) 등이 섞여 있다.

## 사용 시기

다음 중 하나라도 해당하면 본 스킬을 적용한다:
- 사용자가 거버/드릴 폴더 경로를 지목하며 "등록", "다이제스트", "요약", "인덱싱", "분석 저장"을 요청
- `/gerber-digest <폴더>`, `/gerber-digest --update <id>`, `--list`, `--remove <id>`
- "이 보드 거버 자주 볼 것 같아", "팹 출력인데 매번 파싱하기 싫어", "보드 정보 빨리 찾게 거버 다이제스트 만들어줘" 같은 의도 표현
- 같은 거버 세트를 두 번째 이상 참조 — 다이제스트화 제안

다음은 **본 스킬을 쓰지 않는다**:
- 1회성 단발 거버 질문 (그땐 `gerber-pcb-analyst` 에이전트만 호출하거나 직접 답)
- KiCad **소스**(.kicad_pcb/.kicad_sch) 분석 — 그건 `kicad-analyze` 스킬(이건 팹 출력 거버 전용)

## 사전 조건

`/gerber-digest-setup`으로 환경 초기화가 끝나 있으면 가장 매끄럽다(디렉토리 + INDEX.md + CLAUDE.md 마커 + `gerber-pcb-analyst` 에이전트 설치). 미초기화여도:
- `.claude/gerbers/` 부재 → 자동 생성 후 진행
- 에이전트 미설치 → 직접 파싱(폴백) 경로로 진행 (`references/gerber-extract.md`). MCP·gerbv 불필요.

## 산출물 위치

```
<scope_root>/.claude/gerbers/
├── INDEX.md                       ← 마스터 카탈로그 (보드 1줄 요약)
├── <board-id>/
│   ├── digest.md                  ← 개요 + 인벤토리 + 물리/전기/이슈 요약
│   ├── index.md                   ← 파일/레이어 → 역할 + 핀포인트
│   └── metadata.json              ← id/source/cad_tool/units/layers/holes/sha256...
└── ...
```

- `--scope project` (기본): `<project>/.claude/gerbers/`
- `--scope global`: `~/.claude/gerbers/`

산출물 형식 상세는 `references/gerber-digest-format.md`, 추출 절차는 `references/gerber-extract.md`.

## 서브커맨드

| 호출 | 동작 |
|------|------|
| `/gerber-digest <폴더> [--scope project\|global] [--via agent\|direct]` | 신규 인제스트 |
| `/gerber-digest --update <id>` | 폴더 해시로 변경 감지 → `file_hashes` 비교로 불일치 파일만 재파싱 |
| `/gerber-digest --list [--scope project\|global\|all]` | 등록 보드 나열 |
| `/gerber-digest --remove <id>` | 다이제스트 + INDEX.md 항목 + CLAUDE.md 마커 카운트 갱신 |

`--via`: 깊은 분석을 `gerber-pcb-analyst` 에이전트에 위임(`agent`, 기본·권장) vs 스킬이 직접 파싱(`direct`, 폴백). 에이전트 미설치면 자동으로 `direct`.

## 인제스트 워크플로 (8단계)

### 1. 입력 검증
- 경로 정규화 + 존재/읽기 권한 확인.
- **폴더인지 확인** — 폴더 안에 거버/드릴 파일이 있는지 점검. 광고된 모든 CAD 출력을 통과시켜야 하므로 **확장자 화이트리스트**(`*.pho`/`*.gbr`/`*.ger`/`*.gtl`/`*.gbl`/`*.cmp`/`*.sol`/`*.drl`/`*.drd`/`*.gbrjob`) **또는** 파일 내용의 RS-274X 시그니처(`%FS`/`%MO`)·Excellon 시그니처(`M48` 헤더, `T<숫자>C` 드릴 정의)로 식별한다(확장자가 비표준이어도 헤더로 인식). `.txt`는 일반 텍스트(README/BOM 등)와 구분 불가하므로 화이트리스트에서 제외하고 **시그니처 검사로만** Altium Excellon `.txt`를 인정한다. 어느 것도 없으면 "거버 파일을 못 찾음" 안내 후 종료. 입력이 **단일 거버 파일**이면 부모 디렉토리를 세트 폴더로 승격해 인제스트하고 레이어 부족을 경고한다(에지케이스 표와 동일 경로).

### 2. ID 결정
- job명(`.pho` 헤더의 `%IN "..."`) 또는 폴더명 → 소문자 kebab-case (예: `DAISY_CON_J4-O_MDR_20160419_GBR` → `daisy-con-j4-o-mdr-20160419-gbr`).
- 같은 ID 존재 시: sha256 비교 → 일치하면 "이미 등록됨, --update 안내" 후 종료, 불일치면 사용자 확인 후 덮어쓰기.

### 3. 인벤토리 (.rep 우선)
`references/gerber-extract.md` 1단계. 작은 리포트(`.rep`/`.lst`/`.gbrjob`)를 먼저 Read해 애퍼처·드릴 인벤토리를 싸게 확보하고, 큰 `.pho`는 헤더만 Read해 역할·단위·좌표 포맷을 식별. 파일명 규칙으로 레이어 매핑(비표준이면 헤더 근거로).

### 4. 디코드 (CAD 툴 / 단위 / 좌표)
`references/gerber-extract.md` 2단계. `%MO`(단위), `%FS`(좌표 포맷) 디코드, 드릴 포맷은 헤더 없으면 패드 플래시 앵커링으로 확정. 단위 혼재(본문 inch vs .rep mm) 주의.

### 5. 깊은 파싱
- **`--via agent`(기본)**: `gerber-pcb-analyst` 에이전트를 Agent 도구로 호출(`subagent_type: "gerber-pcb-analyst"`). 프롬프트에 폴더 절대경로 + "다이제스트용: 출력 형식 1~6 전 섹션을 표·수치 위주로" 지시. 에이전트의 보고서(최종 메시지)가 다이제스트 본문 원천.
- **`--via direct`(폴백)**: `references/gerber-extract.md` 3~4단계를 스킬이 직접 수행(애퍼처 .pho↔.rep 대조 / 드릴 3중 교차검증, 외곽 bbox).

### 6. sha256 산출
`references/gerber-extract.md` 5단계의 정본 명령으로 **폴더 단일 해시**(빠른 변경 게이트, 재인제스트 판별) + **파일별 해시 매니페스트**(`file_hashes` — `--update`가 변경 파일만 식별하는 근거)를 산출. 화이트리스트가 아닌 전체 일반 파일을 해시하며, 공백 파일명·로케일에 안전한 `-print0`/`LC_ALL=C sort -z`/`while read -d ''` 형태(정본 `gd_manifest` 함수)를 그대로 쓴다. ※ ① 식별은 거버/드릴/리포트만 인정하지만 ⑥ 해시는 폴더 전체 파일 대상이라, BOM/README 등 비거버 `.txt` 변경도 `--update`를 트리거한다 — 거버 변경을 절대 놓치지 않기 위한 보수적 설계(필요 시 해당 보드를 재확인하면 됨).

### 7. 산출물 작성
`references/gerber-digest-format.md` 스키마대로 `digest.md` + `index.md` + `metadata.json` 작성. 모든 치수 inch·mm 병기, 확정/추정 구분, 근거(파일·라인·D-code) 명시. `indexed_at`은 `date -u +%Y-%m-%dT%H:%M:%SZ`로 stamp.

### 8. 마스터 카탈로그 갱신
- `<scope>/.claude/gerbers/INDEX.md`에 1줄 항목 추가 (보드명·외곽·레이어·홀 수·scope).
- 같은 scope `CLAUDE.md` 마커 블록의 `(현재 N개)` 카운트만 갱신(보드별 목록은 INDEX.md가 보유 — 마커는 정적 안내).

## 결정성

- 동일 sha256 재인제스트 → "이미 등록됨" 안내, 재파싱 안 함.
- `--update`는 변경 파일만 재파싱(metadata `file_hashes`의 파일별 sha256 비교로 불일치 파일 식별), 비변경분 보존.
- 산출물 형식(스키마, JSON 키, 헤딩 구조)은 결정적. LLM 요약/이슈 판정은 비결정적이나 형식은 고정.

## 활용 (Claude의 동작 규칙)

사용자가 보드/거버 정보가 필요한 질문을 할 때:

1. 두 INDEX.md 확인 (project가 global을 override):
   - `<project>/.claude/gerbers/INDEX.md`
   - `~/.claude/gerbers/INDEX.md`
2. 관련 보드가 있으면 `digest.md`를 먼저 읽는다.
3. digest로 답할 수 있으면 출처(파일·D-code·scope) 명시.
4. 디테일이 부족하면 `index.md`에서 파일/라인 포인터 → 원본 거버의 해당 부분만 `Read`/`Grep`. SI/PI·차동쌍·플레인 분할 등 깊은 분석은 `gerber-pcb-analyst` 에이전트 재호출.
5. 인덱싱되지 않은 거버 폴더면 `/gerber-digest <폴더>` 등록 제안.

## 에지케이스

| 상황 | 동작 |
|------|------|
| 같은 ID 재등록 (동일 sha256) | "이미 등록됨, --update로 갱신" 안내 후 종료 |
| 같은 ID 재등록 (다른 sha256) | 사용자 확인 후 덮어쓰기 |
| 폴더에 거버 없음 | "거버/드릴 파일 미발견" 안내, 경로 재확인 요청 |
| 단일 거버 파일 입력 | 부모 폴더를 세트로 보고 인제스트(레이어 부족 경고) |
| 에이전트 미설치 | 자동 `--via direct` 폴백, 한계(깊은 분석 제한) 명시 |
| 드릴 포맷 헤더 없음 | 패드 플래시 앵커링으로 확정 (`references/gerber-extract.md`) |
| 레거시 외곽 파일 부재 | 정상으로 처리(Info), 폴리라인/bbox에서 외곽 추출 |
| `.claude/gerbers/` 쓰기 권한 부재 | 명시적 에러 + scope 변경 제안 |
| ID 충돌 (project + global) | project가 override; `--scope global` 명시 시 경고 |

## 흔한 함정

| 함정 | 해결 |
|------|------|
| 큰 실크 .pho 전체 Read | 헤더 + 필요한 좌표만 핀포인트(.rep 우선 전략) |
| `.rep`(mm)와 본문(inch) 단위 혼동 | 결과는 inch·mm 둘 다 병기, 혼재 사실 메모 |
| 외곽을 좌표 bbox로 확정 못 했는데 확정처럼 기술 | `board_size_confirmed: false` + "추정" 명시 |
| 다이제스트만으로 모호하게 답변 | 출처(파일·D-code) 명시 + 모호하면 원본 핀포인트 |
| 깊은 분석을 스킬이 떠안음 | SI/PI·플레인·제조성 종합은 `gerber-pcb-analyst`에 위임 |

## 마무리 보고

인제스트 완료 시 사용자에게:
1. 산출물 경로 (digest.md / index.md / metadata.json)
2. 압축비 (원본 폴더 크기 vs 다이제스트)
3. 핵심 발견 요약 (외곽·레이어·홀·주요 이슈)
4. 등록된 scope, 다음 단계 (이후 보드 질문 시 자동 참조됨)

$ARGUMENTS
