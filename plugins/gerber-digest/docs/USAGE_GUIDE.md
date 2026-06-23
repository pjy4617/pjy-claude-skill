# Gerber Digest 사용 가이드

거버 파일 세트(팹 출력 폴더)를 한 번만 파싱·요약해 **마크다운 다이제스트**로 저장하고, 이후 보드 질문은 원본을 다시 파싱하지 않고 다이제스트만 1차 참조하는 메타 도구. `manual-digest`의 거버 버전이다.

## 구성

| 구성요소 | 종류 | 역할 |
|---------|------|------|
| `gerber-digest` | 스킬 | 인제스트/갱신/목록/삭제 (8단계 워크플로) |
| `gerber-digest-setup` | 스킬 | 환경 1회 초기화 (디렉토리 + INDEX.md + CLAUDE.md 마커 + 에이전트 설치) |
| `gerber-pcb-analyst` | 에이전트 | 깊은 거버 분석 + 보드별 노하우 메모리 누적 |

거버/드릴/리포트는 전부 텍스트이므로 `Read`/`Grep`/`Bash`로 파싱한다. **MCP·gerbv 불필요.**

## 빠른 시작

```
# 1) 환경 1회 초기화 (에이전트 설치 + 디렉토리 + CLAUDE.md 마커)
/gerber-digest-setup
#   → 에이전트 신규 설치 시 Claude Code 재시작

# 2) 거버 폴더 등록
/gerber-digest ./hw/fab/DAISY_CON_J4-O_MDR_20160419_GBR

# 3) 이후엔 그냥 물어보면 다이제스트가 자동 참조됨
"이 보드 외곽 몇 mm야?"   "홀 몇 개?"   "최소 트레이스 폭은?"

# 4) 관리
/gerber-digest --list
/gerber-digest --update <board-id>     # 거버 변경분만 재파싱
/gerber-digest --remove <board-id>
```

## 산출물

```
<project>/.claude/gerbers/
├── INDEX.md                       ← 보드 카탈로그 (1줄 요약)
└── <board-id>/
    ├── digest.md                  ← 개요·인벤토리·물리/전기/이슈 (1차 참조)
    ├── index.md                   ← 파일/레이어 → 역할 + 핀포인트
    └── metadata.json              ← cad_tool/units/layers/holes/sha256...
```

- `--scope project`(기본): `<project>/.claude/gerbers/`
- `--scope global`: `~/.claude/gerbers/` (모든 프로젝트 공유)

## 동작 흐름

```
/gerber-digest <폴더>
  → .rep/.lst 인벤토리 → CAD툴/단위/좌표 디코드
  → 깊은 파싱: gerber-pcb-analyst 에이전트 위임(기본) 또는 직접 파싱(폴백)
  → sha256 산출 → digest.md/index.md/metadata.json 작성 → INDEX.md/CLAUDE.md 갱신

보드 질문
  → INDEX.md 확인 → digest.md 1차 참조 → 부족하면 index.md 핀포인트로 원본 거버 재파싱
  → SI/PI·차동쌍·플레인 분할은 gerber-pcb-analyst 재호출
```

## 지원 입력

| CAD 툴 | 거버 | 드릴 | 리포트 | 식별 |
|--------|------|------|--------|------|
| PADS Layout 9.x | `.pho` (RS-274X) | `.drl` (Excellon) | `.rep`/`.lst` | `.pho` 헤더 `G04 PADS x.x`, `%IN` job명 |
| KiCad | `.gbr` (X2) | `.drl` | `.gbrjob` | `G04 #@! TF.GenerationSoftware,KiCad` |
| Altium/Protel | `.gtl/.gbl/...` | `.txt`/`.drl` | — | 헤더 식별 |
| Eagle | `.cmp/.sol/...` | `.drd` | — | 헤더 식별 |

레거시(PADS 등) 출력의 정상적 부재(전용 외곽 파일·`.gbrjob`·paste 거버 없음)는 Critical이 아니라 Info로 처리하고, 외곽은 동박/실크 폴리라인·좌표 bbox에서 추출한다.

## 파싱 함정 (요약)

- **단위 혼재**: PADS `.rep` 단위는 리포트 설정값(흔히 mm지만 mil/inch 가능 — 헤더 토큰 또는 본문 `%MO`와 ×25.4 교차검증으로 확정), 본문 거버는 inch — 결과는 inch·mm **둘 다** 병기.
- **`%FS` 디코드**: `%FSLAX35Y35` = 3.5 inch, leading-zero 생략 → 좌표 ÷ 10⁵.
- **드릴 포맷 헤더 부재**: 동박 패드 플래시(D03)에 **앵커링**해 2.4/3.5·TZ/LZ를 역산 확정.
- **bbox 오염**: housekeeping move(`X0Y0D02*`)·드릴 도면 텍스트 좌표 제외.

상세: `references/gerber-extract.md`, 산출물 형식: `references/gerber-digest-format.md`.

## 트리거 예시

| 의도 | 발화 / 명령 |
|------|------------|
| 환경 셋업(1회) | "gerber-digest 셋업" / `/gerber-digest-setup` |
| 거버 등록 | "이 거버 폴더 등록해줘" / `/gerber-digest <폴더>` |
| Global 등록 | `/gerber-digest <폴더> --scope global` |
| 변경 시 갱신 | `/gerber-digest --update <id>` (sha256 비교, 변경분만) |
| 등록 목록 | "등록된 거버 목록" / `/gerber-digest --list` |
| 제거 | `/gerber-digest --remove <id>` |
| 깊은 분석 | "이 보드 SI 검토해줘" → `gerber-pcb-analyst` 에이전트 |

## manual-digest / kicad-analyze 와의 구분

- **gerber-digest**: 팹 출력 **거버/드릴**(.pho/.gbr/.drl) — 제조 데이터.
- **kicad-analyze**: KiCad **소스**(.kicad_pcb/.kicad_sch) — 설계 데이터, ERC/DRC.
- **manual-digest**: PDF/HTML/코드베이스 등 일반 매뉴얼/문서.
