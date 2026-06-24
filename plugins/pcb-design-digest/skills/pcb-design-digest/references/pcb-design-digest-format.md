# PCB 설계 다이제스트 산출물 형식

PCB 입력 하나(거버 세트 / PADS `.pcb`·`.asc` / KiCad 소스)를 **하나의 보드 다이제스트**로 만든다. 단위는 **레이어·넷·부품·애퍼처·드릴·좌표**다. 핀포인트는 `Read`/`Grep`(거버·KiCad·PADS ASCII는 텍스트) 또는 `strings | grep`(PADS 바이너리). 추출기는 `direct`(수동 파싱) 또는 `pcb-design-analyst`(에이전트 위임).

산출물은 보드별 디렉토리에 3개 파일:

```
<scope>/.claude/pcb-designs/
├── INDEX.md                       ← 마스터 카탈로그 (보드 1줄 요약)
├── <board-id>/
│   ├── digest.md                  ← 보드 개요 + 인벤토리 + 물리/전기/이슈 요약
│   ├── index.md                   ← 파일/레이어/넷 → 역할 + 핀포인트 라인
│   └── metadata.json              ← id/source/format/cad_tool/units/layers/nets/holes/sha256...
└── ...
```

`format` 필드는 **`gerber` | `pads` | `kicad`** 중 하나. 입력군에 따라 채울 수 있는 섹션이 다르다(아래 「입력군별 채움 가이드」).

---

## digest.md

```markdown
---
id: <kebab-case-board-id>
title: <보드명 (job명/보드명/프로젝트명)>
source: <원본 절대경로 (폴더 또는 파일)>
format: <gerber|pads|kicad>
extraction: <full|partial>      # PADS 바이너리 .pcb 등 부분 추출이면 partial
scope: <project|global>
cad_tool: <PADS Layout 9.x / KiCad 8 / Altium / Eagle / unknown>
units: <inch|mm|mils>           # 원본 본문 단위 (KiCad는 항상 mm)
coord_format: <거버 FS 등, 예: %FSLAX35Y35 → 3.5자리·%MO 단위. KiCad=mm 고정. PADS .pcb=불명(바이너리)>
layers: <int>                   # 동박 레이어 수 (추정 시 "~N")
board_size: <W×H mm (W×H inch)> # 외곽, 확정/추정 명시 (.pcb 바이너리는 보통 추정 불가)
nets: <int 또는 ~N 또는 unknown>  # 넷 수 (PADS .asc/.pcb·KiCad에서 추출, 거버는 보통 unknown)
components: <int 또는 ~N 또는 unknown>  # 부품 수 (PADS/KiCad. 거버는 실크 기반 추정)
holes: <총 홀 수 또는 unknown>
sha256: <폴더 단일 해시 또는 단일 파일 해시>
indexed_at: <ISO 타임스탬프 — 스크립트로 stamp>
extractor: <direct|pcb-design-analyst>
---

# <보드명> — PCB 다이제스트 (<format>)

## 개요
보드 정체성(job명/보드명/CAD 툴/리비전), 레이어 구성, 외곽 크기, 넷/부품/홀 통계 핵심을 2-3문단.
확정 가능한 것과 추정/불가인 것을 구분. **PADS 바이너리면 "부분 추출(strings 기반)"임과 `.asc` export 권장을 첫 문단에 명시.**

## 파일 인벤토리
| 파일 | 역할 | 면/종류 | 근거(헤더/확장자/시그니처) |
|------|------|---------|---------------------------|
| (거버) art001.pho | Copper | Top | `.pho` RS-274X, art001=top copper |
| (PADS) board.pcb | PADS 바이너리 레이아웃 | — | `strings`에 `PADS`/팹 스펙 |
| (KiCad) board.kicad_pcb | KiCad PCB 소스 | — | `(kicad_pcb …)` S-expr |

## 보드 물리 정보
- **외곽**: <W×H mm (inch)> — 확정/추정, 산출 근거(레이어 폴리라인/좌표 bbox/Edge.Cuts/PADS 스펙)
- **레이어 스택업**: <2층/4층…> + 팹 스펙(있으면: 두께/동박/표면처리 — 예 PADS `2.4T / FR-4 / 1oz /2Layer / HASL`)
- **드릴/홀 통계**(있으면): 툴/직경·도금·홀 수 표 + 합계
  | Tool/크기 | 직경 mm (inch) | 도금 | 홀 수 |
  |-----------|----------------|------|------|
- **마운팅 홀**: 큰 직경 홀 위치/개수(추출 가능 시)

## 넷 / 부품 (PADS·KiCad에서 추출, 거버는 제한)
- **넷**: 총 개수 + 주요 전원/접지 넷(예: `+24V_`, `+24VG_`, `GND`, `NC_NET`) 목록/근거
- **부품**: 총 개수 + 레퍼런스 디자네이터/데칼(footprint) 분포(예: `2MM_9PIN`, `SIP_3P_2MM`, `MH_3528_PD`)
- 거버만 있으면: 실크 레퍼런스·패드 유형(SMD/THT) 기반 **추정**임을 명시

## 애퍼처 / 패드 / 트랙 요약 (거버 중심)
.rep 애퍼처 리포트를 압축 표기 — 형상·크기·수량 + 본문 교차검증. 최소 트레이스 폭·최소 패드 등 DFM 임계값.
| D-code/항목 | 형상 | 크기 mm (inch) | 수량 | 용도 추정 |
| ----------- | ---- | -------------- | ---- | -------- |

## 전기 / 전원 분석 (가능한 범위)
- 전원/접지 플레인·넷 식별 가능 여부, 트레이스 폭 분포(전류 용량 힌트)
- 원본으로 알 수 없는 항목(유전율/동박두께/임피던스)은 "불가" 명시

## 좌표 / 포맷 디코드 (재파싱 시 필수)
- **거버**: `%MO`, `%FS` 디코드, 드릴 포맷(앵커링 결과), 단위 혼재 메모
- **PADS `.asc`**: 단위 토큰(`*MILS*`/`*METRIC*`/`*INCHES*`), 섹션 구조
- **PADS `.pcb`**: 바이너리 — 좌표 디코드 불가, strings 토큰 출처만
- **KiCad**: 좌표 mm 고정, `(layers …)`/`(net …)` 위치

## 이슈 및 권장사항
심각도로 분류:
- **Critical**: 제조 불가/누락(현대 CAD 기준)
- **Warning**: DFM 위험(최소 간격/슬리버/애뉴얼 링)
- **Info**: 레거시 출력의 정상적 부재, PADS 바이너리 부분 추출 한계 등

## 한계 및 추가 확인 필요
원본으로 확정 못 한 항목, 렌더 검증 미수행 사실, 원본 핀포인트 권장.
**PADS 바이너리**: "기하/좌표는 strings로 불가 — 정밀 분석은 `.asc` export 또는 PADS Gerber 출력 필요" 명시.

## 사용 가이드 (핀포인트)
세부 필요 시 직접 읽을 파일·좌표/넷/스탠자(입력군별):
- 거버 외곽 폴리라인: `art001.pho`의 가는 D-code D01 draw 시퀀스 / 애퍼처 `%ADD` / 드릴 `drl001.lst`
- PADS `.asc`: `*PART*`/`*NET*`/`*SIGNAL*` 섹션 / `.pcb`: `strings -n 4 board.pcb | grep <토큰>`
- KiCad: `(gr_line …)`(Edge.Cuts) / `(net …)` / `(footprint …)` / `(setup …)`
- 깊은 분석(SI/PI·차동쌍·플레인 분할): `pcb-design-analyst` 에이전트 재호출
```

---

## index.md (파일/레이어/넷 → 역할 + 핀포인트)

```markdown
# <보드명> — 파일/레이어/넷 인덱스 (<format>)
> 다이제스트로 부족할 때 아래를 직접 Read/Grep. 경로는 `source` 기준.

## 레이어 / 파일
| 파일 | 역할 | 면/종류 | 핵심 라인/영역 |
|------|------|---------|----------------|
| art001.pho | Copper Top | Top | 애퍼처 `%ADD` 블록 line N~, 외곽 D01 draw |
| board.kicad_pcb | KiCad PCB | — | `(layers` line N, `(footprint` 블록들 |
| board.pcb | PADS 바이너리 | — | `strings -n 4 | grep` (라인 무의미 — 토큰 검색) |

## 넷 (PADS/KiCad)
| 넷 | 종류 | 근거 |
|----|------|------|
| +24V_ | 전원 | PADS strings / `.asc` *NET* |
| GND | 접지 | … |

## 드릴 / 리포트 (거버)
| 파일 | 역할 | 포맷 | 비고 |
|------|------|------|------|
| drl001.drl | Excellon NC | 2.4 inch TZ생략(앵커링 확정) | 본문 |
| drl001.lst | Drill Listing | 풀정밀 | 좌표 검증 기준 |
```

`:line` 포인터는 비자명한 핵심만. 라인은 재플롯/재저장 시 바뀔 수 있으니 식별자(파일·D-code·넷명·스탠자) 우선. **PADS 바이너리는 라인 번호가 무의미** — `strings | grep <토큰>` 검색을 안내한다.

---

## metadata.json

```json
{
  "id": "<board-id>",
  "title": "<보드명>",
  "source": "<절대경로>",
  "format": "pads",
  "extraction": "partial",
  "scope": "project",
  "cad_tool": "PADS Layout (PowerPCB)",
  "job_name": "<보드명/job명>",
  "units": "unknown",
  "coord_format": "binary (strings 추출 — 좌표 디코드 불가)",
  "drill_format": null,
  "layers": 2,
  "board_size_mm": null,
  "board_size_inch": null,
  "board_size_confirmed": false,
  "fab_spec": "2.4T / FR-4 / 1oz / 2Layer / HASL",
  "nets_total": 3,
  "nets": ["+24V_", "+24VG_", "NC_NET"],
  "components_total": null,
  "decals": ["2MM_9PIN", "SIP_3P_2MM", "MH_3528_PD", "10120-3000"],
  "holes_total": null,
  "drill_tools": [],
  "aperture_count": null,
  "min_trace_mm": null,
  "file_inventory": {
    "DAISY_CON_J4-O_MDR_20160419.pcb": "pads-binary-layout"
  },
  "sha256": "<file-or-folder-hash>",
  "file_hashes": {
    "DAISY_CON_J4-O_MDR_20160419.pcb": "<sha256>"
  },
  "indexed_at": "<ISO>",
  "extractor": "pcb-design-analyst",
  "issues": {"critical": 0, "warning": 0, "info": 2}
}
```

거버 입력의 `metadata.json` 예시(애퍼처/드릴 풍부, nets/components는 unknown):

```json
{
  "format": "gerber",
  "extraction": "full",
  "units": "inch",
  "coord_format": "%FSLAX35Y35",
  "drill_format": "2.4 inch, TZ 생략 (앵커링 확정)",
  "layers": 2,
  "board_size_mm": [80.0, 60.0],
  "board_size_inch": [3.15, 2.36],
  "board_size_confirmed": false,
  "holes_total": 17,
  "drill_tools": [
    {"tool": "T1", "dia_mm": 0.75, "dia_inch": 0.02953, "plated": true, "qty": 15}
  ],
  "aperture_count": 9,
  "min_trace_mm": 0.15,
  "nets_total": null,
  "components_total": null
}
```

KiCad 입력은 `units: "mm"`, `coord_format: "mm (KiCad 고정)"`, `nets_total`/`components_total`을 `(net …)`/`(footprint …)` 카운트로 채운다.

- `extraction`: `full`(거버/KiCad/PADS ASCII 완전 파싱) vs `partial`(PADS 바이너리 strings).
- `board_size_confirmed`: 외곽을 좌표 bbox/Edge.Cuts로 확정했으면 true, 추정·불가면 false.
- `sha256` / `file_hashes`: 폴더 입력은 `gerber-extract.md` 5단계 정본 `gd_manifest`(폴더 단일 해시 + 파일별 맵), 단일 파일 입력은 `sha256sum <file>`. **문서 간 명령 분기 금지**.
- 추출 불가 수치는 `null`(또는 `"unknown"`)로 명시 — 0으로 채우지 마라.
- 모든 치수는 mm·inch **둘 다** 기록(KiCad는 mm 기준 + inch 병기). 추정값은 `*_confirmed` 플래그로 표시.

---

## INDEX.md 1줄 항목 형식

```markdown
| <board-id> | <보드명> | <format> | <외곽 또는 추정/불가> | <레이어> | nets:<N> holes:<N> | <project|global> |
```

## 압축비 목표

원본은 거버 폴더 수십 KB~수 MB / PADS `.pcb` 수백 KB / KiCad `.kicad_pcb` 수백 KB~수 MB. 다이제스트는 보통 **3~10 KB**로 압축(정보밀도가 높아 문서 0.3%보다 높은 게 정상). 핵심은 "다음에 이 보드를 다룰 때 원본 전체를 다시 파싱하지 않게 하는 것".
