# 거버 다이제스트 산출물 형식

거버 파일 세트(팹 출력 폴더) 하나를 **하나의 보드 다이제스트**로 만든다. 문서/코드와 달리 단위가 **레이어·애퍼처·드릴·좌표**다. 핀포인트는 `mcp__pdf-reader__read_pdf`가 아니라 `Read`/`Grep`(거버는 전부 텍스트). 추출기는 `direct`(수동 파싱, SKILL의 `--via direct`와 동일) 또는 `gerber-pcb-analyst`(에이전트 위임).

산출물은 보드별 디렉토리에 3개 파일:

```
<scope>/.claude/gerbers/
├── INDEX.md                       ← 마스터 카탈로그 (보드 1줄 요약)
├── <board-id>/
│   ├── digest.md                  ← 보드 개요 + 인벤토리 + 물리/전기/이슈 요약
│   ├── index.md                   ← 파일/레이어 → 역할 + 핀포인트 라인
│   └── metadata.json              ← id/source/cad_tool/units/layers/holes/sha256...
└── ...
```

---

## digest.md

```markdown
---
id: <kebab-case-board-id>
title: <보드명 (job명 또는 폴더명)>
source: <거버 폴더 절대경로>
format: gerber
scope: <project|global>
cad_tool: <PADS 9.5 / Altium / KiCad 8 / Eagle / unknown>
units: <inch|mm>
coord_format: <동박 FS, 예: %FSLAX35Y35 → 3.5자리·%MO 단위(IN→inch, MM→mm), LZ 생략, absolute>
layers: <int>            # 동박 레이어 수 (추정 시 "~N" 표기)
board_size: <W×H mm (W×H inch)>   # 외곽 bbox, 확정/추정 명시
holes: <총 홀 수>
sha256: <파일별 sha256 매니페스트를 다시 해시한 폴더 단일 해시 (gd_manifest | sha256sum, 재인제스트 판별용)>
indexed_at: <ISO 타임스탬프 — 스크립트로 stamp>
extractor: <direct|gerber-pcb-analyst>
---

# <보드명> — 거버 다이제스트

## 개요
보드 정체성(job명/CAD 툴/리비전), 레이어 구성, 외곽 크기, 홀 통계 핵심을 2-3문단.
거버만으로 확정 가능한 것과 추정인 것을 구분해서 서술.

## 파일 인벤토리
| 파일 | 역할 | 면 | 근거(헤더/확장자) |
|------|------|----|------------------|
| art001.pho | Copper | Top | `.pho` RS-274X, art001=top copper |
| art002.pho | Copper | Bottom | art002=bottom copper |
| sm001021.pho | Soldermask | Top | sm001=top mask |
| sm002028.pho | Soldermask | Bottom | sm002=bottom mask |
| sst001026.pho | Silkscreen | Top | sst=silk top |
| ssb002029.pho | Silkscreen | Bottom | ssb=silk bottom |
| dd001024.pho | Drill drawing | — | dd=drill drawing |
| drl001.drl | Excellon drill | NPTH/PTH | drl=Excellon NC |
| *.rep / *.lst | 동반 리포트 | — | 애퍼처/드릴 인벤토리 |

## 보드 물리 정보
- **외곽**: <W×H mm (inch)> — 확정/추정, 산출 근거(어느 레이어 폴리라인/좌표 bbox)
- **레이어 스택업**: <2층/4층…> (동박 레이어 수 근거)
- **드릴/홀 통계**: 툴별 직경·도금·홀 수 표 + 합계
  | Tool | 직경 mm (inch) | 도금 | 홀 수 |
  |------|----------------|------|------|
  | T1 | 0.75 (0.02953") | PTH | 15 |
  | T2 | 2.5 (0.09843") | PTH | 2 |
- **마운팅 홀**: 큰 직경(예: 2.5mm↑) 홀 위치/개수

## 애퍼처 / 패드 요약
.rep 애퍼처 리포트를 압축 표기 — 형상·크기·수량 + 본문 .pho와 교차검증 결과.
| D-code | 형상 | 크기 mm (inch) | 수량 | 용도 추정 |
| ------ | ---- | -------------- | ---- | -------- |
| D17 | SQR | 1.8 (0.071") | 10 | THT 패드(1번핀?) |
| D23 | RND | 0.3 (0.012") | 38 | SMD 패드/비아 |
최소 트레이스 폭·최소 패드 등 DFM 임계값을 명시.

## 부품 / 전기 / 전원 분석 (거버로 가능한 범위)
- 실크 레퍼런스 디자네이터, 패드 유형(SMD/THT) 분포, 대략 부품 밀도
- 전원/접지 플레인 식별 가능 여부, 트레이스 폭 분포(전류 용량 힌트)
- 거버만으로 알 수 없는 항목(유전율/동박두께/임피던스)은 명시적으로 "불가"

## 좌표 / 포맷 디코드 (재파싱 시 필수)
- `%MO`=<IN/MM>, `%FS`=<디코드 결과>, 좌표 스케일(÷10^n = %MO 단위 — IN이면 inch, MM이면 mm)
- 드릴 포맷(헤더 부재 시 앵커링으로 확정한 결과: 2.4/3.5, TZ/LZ)
- 단위 혼재(본문 inch vs .rep mm 등) 주의 메모

## 이슈 및 권장사항
심각도로 분류:
- **Critical**: 제조 불가/누락(현대 CAD 기준)
- **Warning**: DFM 위험(최소 간격/슬리버/애뉴얼 링)
- **Info**: 레거시 출력의 정상적 부재 등

## 한계 및 추가 확인 필요
거버만으로 확정 못 한 항목, 렌더 검증 미수행 사실, 원본 핀포인트 권장.

## 사용 가이드 (핀포인트)
세부 필요 시 직접 Read할 파일·좌표:
- 외곽 폴리라인: `art001.pho`의 가는 원형 D-code(예: D24)로 그린 D01 draw 시퀀스 — 레거시 PADS는 G36/G37 region이 아님(단, 동박 plane을 G36으로 채운 보드면 G36/G37도 확인)
- 애퍼처 정의: `art001.pho` `%ADD` 라인 / `art001.rep`
- 드릴 좌표: `drl001.lst`(풀정밀) / `drl001.drl`
- 깊은 분석(SI/PI·차동쌍·플레인 분할): `gerber-pcb-analyst` 에이전트 재호출
```

---

## index.md (파일/레이어 → 역할 + 핀포인트)

```markdown
# <보드명> 거버 — 파일 → 역할 인덱스
> 다이제스트로 부족할 때 아래 파일을 직접 Read. 경로는 `source` 폴더 기준.

## 레이어
| 파일 | 역할 | 면 | 핵심 라인/영역 |
|------|------|----|----------------|
| art001.pho | Copper Top | Top | 애퍼처 `%ADD` 블록 line N~, 외곽=가는 D-code(D24 등) D01 draw |
| art002.pho | Copper Bottom | Bottom | … |
| sm001021.pho | Soldermask Top | Top | — |
| sm002028.pho | Soldermask Bottom | Bottom | — |
| sst001026.pho | Silkscreen Top | Top | 레퍼런스 텍스트 플래시 |

## 드릴
| 파일 | 역할 | 포맷 | 비고 |
|------|------|------|------|
| drl001.drl | Excellon NC | 2.4 inch TZ생략(앵커링 확정) | 본문 |
| drl001.lst | Drill Listing | 풀정밀 | 좌표 검증 기준 |
| drl001.rep | Drill Sizes | <리포트 단위> | 툴별 직경/수량 |

## 리포트
| 파일 | 내용 |
|------|------|
| art001.rep | Photo-Plotter Apertures(Width=<리포트 단위>) |
```

`:line` 포인터는 비자명한 핵심만(애퍼처 블록 시작, 외곽 D01 draw 시작). 라인은 재플롯 시 바뀔 수 있으니 식별자(파일·D-code) 우선.

---

## metadata.json

```json
{
  "id": "<board-id>",
  "title": "<보드명>",
  "source": "<폴더 절대경로>",
  "format": "gerber",
  "scope": "project",
  "cad_tool": "PADS 9.5 (Build 522968)",
  "job_name": "<%IN 잡명>",
  "units": "inch",
  "coord_format": "%FSLAX35Y35",
  "drill_format": "2.4 inch, TZ 생략 (앵커링 확정 — 동박 FS와 다를 수 있음)",
  "layers": 2,
  "board_size_mm": [80.0, 60.0],
  "board_size_inch": [3.15, 2.36],
  "board_size_confirmed": false,
  "holes_total": 17,
  "drill_tools": [
    {"tool": "T1", "dia_mm": 0.75, "dia_inch": 0.02953, "plated": true, "qty": 15},
    {"tool": "T2", "dia_mm": 2.5, "dia_inch": 0.09843, "plated": true, "qty": 2}
  ],
  "aperture_count": 9,
  "min_trace_mm": 0.15,
  "min_line_mm": 0.1,
  "file_inventory": {
    "art001.pho": "copper-top",
    "art002.pho": "copper-bottom",
    "sm001021.pho": "soldermask-top",
    "sm002028.pho": "soldermask-bottom",
    "sst001026.pho": "silkscreen-top",
    "ssb002029.pho": "silkscreen-bottom",
    "dd001024.pho": "drill-drawing",
    "drl001.drl": "excellon-drill"
  },
  "sha256": "<folder-hash>",
  "file_hashes": {
    "art001.pho": "<sha256>",
    "drl001.drl": "<sha256>",
    "...": "<각 일반 파일별 sha256 — --update가 변경 파일만 식별하는 근거>"
  },
  "indexed_at": "<ISO>",
  "extractor": "gerber-pcb-analyst",
  "issues": {"critical": 0, "warning": 1, "info": 2}
}
```

- `board_size_confirmed`: 외곽이 좌표 bbox로 확정됐으면 true, 추정이면 false.
- `sha256` / `file_hashes`: 폴더 단일 해시(빠른 변경 게이트) + 파일별 해시 맵(`--update`가 불일치 파일만 식별·재파싱하는 근거). **산출 명령은 `gerber-extract.md` 5단계 정본을 그대로 사용**한다(문서 간 명령 분기 금지 — 다르면 같은 폴더가 다른 해시를 내 판별이 깨진다). 명령은 공백 파일명·로케일에 안전한 `-print0`/`LC_ALL=C sort -z`/`while read -d ''` 형태(정본 `gd_manifest` 함수).
- `min_trace_mm` / `min_line_mm`: 신호 트레이스 최소폭과 윤곽/실크 최소 라인폭을 구분(예시값은 보드별 상이 — 실측으로 채움).
- 모든 치수는 mm·inch **둘 다** 기록. 추정값은 키 이름이나 `*_confirmed` 플래그로 표시.

---

## 압축비 목표

거버 폴더는 보통 수십 KB~수 MB(큰 실크 .pho 포함). 다이제스트는 보통 **3~8 KB**로 압축(텍스트 거버는 정보밀도가 높아 문서 0.3%보다 높은 게 정상). 핵심은 "다음에 이 보드를 다룰 때 원본 전체를 다시 파싱하지 않게 하는 것".
