# 거버 추출 워크플로 (저비용 다이제스트 빌드)

거버 폴더를 **싸게** 다이제스트화하는 절차. 핵심 원칙: **작은 리포트 먼저(.rep/.lst), 큰 .pho는 핀포인트만**. 거버는 전부 텍스트라 MCP·gerbv 불필요 — `Read`/`Grep`/`Bash`로 파싱한다.

> 깊은 분석(SI/PI, 차동쌍, 플레인 분할, 제조성 종합 판정)은 `gerber-pcb-analyst` 에이전트에 위임한다. 이 가이드는 다이제스트 골격을 만드는 추출 절차에 집중한다.

## 추출 경로 두 가지

1. **에이전트 위임(권장, 기본)** — `gerber-pcb-analyst` 에이전트를 Agent 도구로 호출(`subagent_type: "gerber-pcb-analyst"`)하여 "출력 형식 1~6" 전 구조의 보고서를 받는다. 그 보고서를 `gerber-digest-format.md` 스키마로 재배치해 `digest.md`로 저장. 에이전트는 분석 노하우를 자체 메모리에 누적하므로 반복 보드에서 점점 빨라진다.
2. **직접 파싱(폴백)** — 에이전트가 설치돼 있지 않거나(`/gerber-digest-setup` 미실행) 보드가 단순하면, 아래 단계를 스킬이 직접 수행한다.

어느 경로든 산출물 형식과 교차검증 기준은 동일하다.

## 1. 인벤토리 (.rep/.lst 우선)

```bash
ls -la <folder>
# 작은 리포트부터 Read: *.rep (애퍼처/드릴 사이즈), *.lst (드릴 좌표), *.gbrjob (있으면)
```

- 각 `.pho`/`.gbr`/`.drl`의 **헤더만**(앞 20~30줄) Read하여 CAD 툴·단위·좌표 포맷·역할을 식별.
- 파일명 규칙으로 레이어 역할 매핑. 비표준이면 헤더 근거로 매핑(추측 금지).

## 2. CAD 툴 / 단위 / 좌표 포맷 디코드

`.pho` 헤더에서:
- 툴: `G04 PADS x.x Build ...`, `G04 PC Version=...`, job명 `%IN "..."`
- 단위: `%MOIN`(inch) / `%MOMM`(mm)
- 좌표: `%FSLAX35Y35` → Leading-zero 생략, Absolute, **3.5**(정수3·소수5) → 좌표 ÷ 10⁵ = **%MO 단위**(`%MOIN`→inch, `%MOMM`→mm)

**드릴 포맷 헤더가 없을 수 있다**(예: `T1C.02953F197S55`). 이때 드릴 좌표를 이미 디코드한 동박 패드 플래시(D03) 위치에 **앵커링**해 역산한다(같은 홀이 같은 패드 중심과 맞는 포맷이 정답). 토큰 자릿수 불균일(`X039764`(6) vs `X04252`(5))은 LZ·TZ 어느 쪽에서도 나타나므로 zero-suppression을 단정하지 말고 반드시 위 앵커링으로 확정한다.

## 3. 애퍼처 / 드릴 집계 + 교차검증 (애퍼처 2-way: .pho↔.rep / 드릴 3-way: .drl↔.lst↔.rep)

- 애퍼처: `art*.rep`(Width/Shape/Qty) ↔ 본문 `.pho`의 `%ADD` 정의 → 형상·개수 일치 확인.
- 드릴: `.drl`(Excellon) ↔ `.lst`(풀정밀 좌표) ↔ `.rep`(Drill Sizes) → 툴별 직경·홀 수 3중 일치 확인.
- **`.rep` 단위는 리포트 설정값**(흔히 mm지만 mil/inch도 가능) — `.rep` 헤더의 단위 토큰(Units/Metric/English/mils)을 먼저 확인하고, 없으면 `.rep` 값을 본문 거버 `%MO` 단위로 환산해 패드 플래시(D03)·`%ADD`·드릴 좌표와 ×25.4/÷25.4 교차검증해 확정한다. **결과는 inch·mm 둘 다 병기**.

## 4. 외곽 bbox 계산

- 전용 외곽/Edge.Cuts/.gbrjob가 있으면 그걸로. **레거시 PADS는 전용 외곽이 없는 게 정상** → 동박/실크의 윤곽 폴리라인(가는 원형 D-code) 또는 좌표 bbox로 추정.
- **bbox 오염 제거**: 파일 끝 `X0Y0D02*` housekeeping move, 드릴 도면 우측의 드릴차트 텍스트 영역(보드 밖 큰 좌표) 제외.
- `%ADD…R,0.07087X0.07087`의 `X`는 파라미터(필드) 구분자 — 두 치수(폭/높이)를 분리하는 것이지 좌표 X도 곱셈도 아님. 좌표 추출 시 `%`/`G04`/`%AD`/`%AM` 등 비좌표 라인만 제외. **D01/D02/D03은 모달** — D-code 생략 좌표 라인은 직전 연산을 잇는 정점이니 bbox에 포함(제외는 `X0Y0D02` 류 housekeeping뿐).
- 외곽이 좌표로 확정되면 `board_size_confirmed: true`, 추정이면 false + 근거 명시.

## 5. sha256 (재인제스트 판별)

```bash
# (1) 파일별 해시 매니페스트 — --update가 "어느 파일이 바뀌었나"를 식별하는 근거.
#     출력을 metadata.json의 file_hashes 맵(파일명→sha256)으로 저장. 화이트리스트 없이 전체 파일(.숨김 제외).
#     공백 파일명·로케일에 안전(-print0 / LC_ALL=C sort -z), basename 사용(폴더 위치 무관).
gd_manifest() {
  find "$1" -maxdepth 1 -type f ! -name '.*' -print0 | LC_ALL=C sort -z | while IFS= read -r -d '' f; do
    printf '%s  %s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$(basename "$f")"
  done
}
gd_manifest <folder>

# (2) 폴더 단일 해시 — "변경됐나?" 빠른 게이트. 매니페스트(파일명+해시)를 다시 해시한다 →
#     파일 경계·이름·내용이 모두 묶여, 단순 cat 연결의 경계 충돌·리네임 미반영 문제가 없다.
gd_manifest <folder> | sha256sum | cut -d' ' -f1
```

- 폴더 해시가 **같으면** "이미 등록됨"·변경 없음 → 재파싱 안 함.
- **다르면** `file_hashes` 맵을 파일별로 비교해 **불일치 파일만 재파싱**하고, 비변경 파일의 digest 섹션은 보존한다(`--update`).

## 6. 다이제스트 작성

`gerber-digest-format.md` 스키마대로 `digest.md` + `index.md` + `metadata.json` 작성. 모든 수치는 inch·mm 병기, 확정/추정 구분, 근거(파일·라인·D-code) 명시.

## 흔한 함정

| 함정 | 해결 |
|------|------|
| 큰 실크 .pho 전체 Read | 헤더 + 필요한 플래시/좌표만 핀포인트(Read offset/limit, Grep) |
| `.rep` 단위를 mm로 단정 | `.rep` 단위는 리포트 설정값(mm/mil/inch) — 헤더 토큰 확인 또는 본문 %MO와 ×25.4 교차검증으로 확정 |
| 드릴 포맷 헤더 없음 → 단위 추측 | 동박 패드 플래시에 앵커링 역산으로 확정 |
| `%FS` 자릿수/LZ 혼동 | 값이 10×/0.1× 틀어짐 — 디코드 결과를 패드 좌표로 검증 |
| 레거시 외곽 누락을 Critical로 | 구형 PADS는 정상 — Info로, 외곽은 폴리라인/bbox에서 추출 |
| bbox에 드릴차트 텍스트 좌표 포함 | 보드 밖 큰 좌표·housekeeping move 제외 |
| 단일 파일 값 맹신 | .pho↔.rep, .drl↔.lst↔.rep 교차검증으로 "확정" 판정 |
