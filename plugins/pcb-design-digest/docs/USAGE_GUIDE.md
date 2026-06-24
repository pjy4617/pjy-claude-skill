# PCB Design Digest 사용 가이드

PCB 설계 입력(팹 출력 거버 폴더 / PADS 레이아웃 / KiCad 소스)을 한 번만 파싱·요약해 **마크다운 다이제스트**로 저장하고, 이후 보드 질문은 원본을 다시 파싱하지 않고 다이제스트만 1차 참조하는 메타 도구. `manual-digest`의 PCB 버전이다 — 한 번 만든 압축 다이제스트가 세션을 넘어 누적된다.

## 구성

| 구성요소 | 종류 | 역할 |
|---------|------|------|
| `pcb-design-digest` | 스킬 | 인제스트/갱신/목록/삭제 (8단계 워크플로, 거버/PADS/KiCad) |
| `pcb-design-digest-setup` | 스킬 | 환경 1회 초기화 (디렉토리 + INDEX.md + CLAUDE.md 마커 + 에이전트 설치) |
| `pcb-design-analyst` | 에이전트 | 깊은 PCB 분석 + 보드별 노하우 메모리 누적 |

거버/드릴/리포트·KiCad S-expression·PADS ASCII는 전부 텍스트이므로 `Read`/`Grep`/`Bash`로 파싱한다. **PADS 바이너리 `.pcb`만** `strings | grep`으로 부분 추출한다. **MCP·gerbv 불필요.**

## 빠른 시작

```
# 1) 환경 1회 초기화 (에이전트 설치 + 디렉토리 + CLAUDE.md 마커)
/pcb-design-digest-setup
#   → 에이전트 신규 설치 시 Claude Code 재시작

# 2) PCB 설계 입력 등록 (세 가지 입력군 모두 동일 명령)
/pcb-design-digest ./hw/fab/DAISY_CON_J4-O_MDR_20160419_GBR   # 거버 폴더
/pcb-design-digest ./hw/pads/DAISY_CON_J4-O_MDR.pcb           # PADS 바이너리 (부분 추출)
/pcb-design-digest ./hw/pads/DAISY_CON_J4-O_MDR.asc           # PADS ASCII export (완전 파싱 권장)
/pcb-design-digest ./hw/kicad/sensor_board.kicad_pcb          # KiCad PCB 소스

# 3) 이후엔 그냥 물어보면 다이제스트가 자동 참조됨
"이 보드 외곽 몇 mm야?"   "홀 몇 개?"   "최소 트레이스 폭은?"   "전원 넷 뭐뭐 있어?"

# 4) 관리
/pcb-design-digest --list
/pcb-design-digest --update <board-id>     # 원본 변경분만 재파싱 (sha256 비교)
/pcb-design-digest --remove <board-id>
```

## 산출물

```
<project>/.claude/pcb-designs/
├── INDEX.md                       ← 보드 카탈로그 (1줄 요약, format 포함)
└── <board-id>/
    ├── digest.md                  ← 개요·인벤토리·물리/전기/넷·이슈 (1차 참조)
    ├── index.md                   ← 파일/레이어/넷 → 역할 + 핀포인트
    └── metadata.json              ← format/extraction/cad_tool/units/layers/nets/holes/sha256...
```

- `--scope project`(기본): `<project>/.claude/pcb-designs/`
- `--scope global`: `~/.claude/pcb-designs/` (모든 프로젝트 공유)

산출물 형식 정본: `references/pcb-design-digest-format.md` (digest.md/index.md/metadata.json 스키마, `format` 필드, 입력군별 채움 가이드).

## 동작 흐름

```
/pcb-design-digest <입력>
  → 입력군 식별(폴더=gerber / .pcb·.asc=pads / .kicad_*=kicad)
  → 거버: .rep/.lst 인벤토리 → CAD툴/단위/좌표 디코드
    PADS .asc: *PART*/*NET*/*SIGNAL* 섹션 파싱 (extraction=full)
    PADS .pcb: strings 토큰 추출 (extraction=partial)
    KiCad: (layers)/(net)/(footprint)/(setup) S-expr 파싱 (좌표 mm 고정)
  → 깊은 파싱: pcb-design-analyst 에이전트 위임(기본) 또는 직접 파싱(폴백)
  → sha256 산출 → digest.md/index.md/metadata.json 작성 → INDEX.md/CLAUDE.md 갱신

보드 질문
  → INDEX.md 확인 → digest.md 1차 참조 → 부족하면 index.md 핀포인트로 원본 재파싱
  → SI/PI·차동쌍·플레인 분할은 pcb-design-analyst 재호출
```

## 지원 입력

| format | 입력 | 식별 방법 | 파싱 | extraction |
|--------|------|-----------|------|------------|
| `gerber` | 팹 출력 **폴더** (`.pho/.gbr/.ger/.gtl/.gbl/.drl/.gbrjob/.rep/.lst` …) | 폴더 입력 + 거버/드릴 확장자·헤더(`G04 PADS`, `%IN`, `TF.GenerationSoftware,KiCad`) | 전부 텍스트 → `Read`/`Grep`; `.rep`/`.lst` 인벤토리, `%MO`/`%FS` 디코드 | **full** |
| `pads` (.pcb) | PADS Layout/PowerPCB **바이너리** 네이티브 `.pcb` | `.pcb` 확장자 + `strings`에 `PADS`/팹 스펙 토큰 | `strings -n 4 board.pcb \| grep <토큰>` — 넷명·데칼·팹스펙만 회수, **좌표/기하 불가** | **partial** |
| `pads` (.asc) | PADS **ASCII export** `.asc` | `.asc` 확장자 + `*PADS-…*`/`*PART*`/`*NET*`/`*SIGNAL*` 섹션 헤더 | 전 텍스트 파싱; 단위 토큰(`*MILS*`/`*METRIC*`/`*INCHES*`)·부품·넷 완전 추출 | **full** |
| `kicad` | KiCad 소스 `.kicad_pcb` / `.kicad_sch` / `.kicad_pro` | 확장자 + `(kicad_pcb …)` / `(kicad_sch …)` S-expr 루트 | 전 텍스트 파싱; `(layers)`/`(net)`/`(footprint)`/`(setup)`, **좌표 항상 mm** | **full** |

> **PADS 바이너리 `.pcb`는 부분 추출(strings)만 가능** — 좌표·외곽·트랙 기하를 회수할 수 없다. 정밀 분석이 필요하면 **PADS에서 `.asc` ASCII export 또는 Gerber 출력**을 받아 그 쪽을 등록하는 것을 권장한다(`digest.md` 첫 문단과 `한계` 섹션에 이 사실을 명시).

레거시(PADS 등) 거버 출력의 정상적 부재(전용 외곽 파일·`.gbrjob`·paste 거버 없음)는 Critical이 아니라 Info로 처리하고, 외곽은 동박/실크 폴리라인·좌표 bbox에서 추출한다.

## 파싱 함정 (요약)

**거버**
- **단위 혼재**: PADS `.rep` 단위는 리포트 설정값(흔히 mm지만 mil/inch 가능 — 헤더 토큰 또는 본문 `%MO`와 ×25.4 교차검증으로 확정), 본문 거버는 inch — 결과는 inch·mm **둘 다** 병기.
- **`%FS` 디코드**: `%FSLAX35Y35` = 3.5 inch, leading-zero 생략 → 좌표 ÷ 10⁵.
- **드릴 포맷 헤더 부재**: 동박 패드 플래시(D03)에 **앵커링**해 2.4/3.5·TZ/LZ를 역산 확정.
- **bbox 오염**: housekeeping move(`X0Y0D02*`)·드릴 도면 텍스트 좌표 제외.

**PADS**
- **`.pcb`는 바이너리** — strings로 넷명·데칼·팹스펙만 회수, 좌표/외곽/트랙은 **불가**(`extraction=partial`). 정밀 분석은 `.asc`/Gerber 권장.
- **`.asc` 단위 토큰** 우선 확인(`*MILS*`/`*METRIC*`/`*INCHES*`) — 본문 좌표 해석의 기준.

**KiCad**
- **좌표는 항상 mm 고정** — 단위 추론 불필요(`coord_format: "mm (KiCad 고정)"`). 외곽은 `Edge.Cuts` `(gr_line)` bbox, 넷/부품은 `(net)`/`(footprint)` 카운트.

상세: 거버 `references/gerber-extract.md`, PADS `references/pads-extract.md`, KiCad `references/kicad-extract.md`. 산출물 형식: `references/pcb-design-digest-format.md`.

## 트리거 예시

| 의도 | 발화 / 명령 |
|------|------------|
| 환경 셋업(1회) | "pcb-design-digest 셋업" / `/pcb-design-digest-setup` |
| 거버 등록 | "이 거버 폴더 등록해줘" / `/pcb-design-digest <폴더>` |
| PADS 등록 | "이 PADS 보드 등록해줘" / `/pcb-design-digest <board.pcb 또는 .asc>` |
| KiCad 등록 | "이 KiCad 보드 다이제스트 만들어줘" / `/pcb-design-digest <board.kicad_pcb>` |
| Global 등록 | `/pcb-design-digest <입력> --scope global` |
| 변경 시 갱신 | `/pcb-design-digest --update <id>` (sha256 비교, 변경분만) |
| 등록 목록 | "등록된 PCB 목록" / `/pcb-design-digest --list` |
| 제거 | `/pcb-design-digest --remove <id>` |
| 깊은 분석 | "이 보드 SI 검토해줘" → `pcb-design-analyst` 에이전트 |

## manual-digest / kicad-analyze 와의 구분

- **pcb-design-digest**: 거버(.pho/.gbr/.drl) · PADS(.pcb/.asc) · KiCad(.kicad_pcb/.kicad_sch/.kicad_pro) 중 **무엇이든** 한 번 파싱해 **영속 다이제스트**를 구축 — 이후 원본 재파싱 없이 1차 참조. 제조 데이터·설계 데이터 모두 입력 가능.
- **kicad-analyze**: KiCad 소스에 대한 **라이브 분석** — ERC/DRC 실행, 넷 추적, SI/PI를 그때그때 수행(다이제스트 저장 아님).
- **manual-digest**: PDF/HTML/EPUB/DOCX/CHM/코드베이스 등 일반 매뉴얼·문서·소스코드의 다이제스트.

세 도구는 보완 관계다. 동일 KiCad 보드라도 "두고두고 참조할 압축 요약"이 필요하면 pcb-design-digest, "지금 ERC/DRC를 돌려 위반을 찾는" 것이면 kicad-analyze를 쓴다.
