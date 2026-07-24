---
name: wmx3-app-config-xml-analy
description: "WMX3 Config Export(파라미터 export XML)를 읽어 분석한다. WMX3Agent/WOS가 내보낸 엔진 파라미터 스냅샷(GlobalParameters + 128축 AxisParameters)을 파싱해 ① 실제 설정된 축(공장 디폴트에서 벗어난 축) 식별 ② 축별 핵심 파라미터(기어비·토크 제한·소프트리밋·원점·절대엔코더 등) 요약 ③ 안전/일관성 검토(오버트래블·소프트리밋·팔로잉 에러·E-Stop)를 심각도 4등급으로 리포트한다. 'WMX Config Export 분석', 'wmx 파라미터 파일 분석', 'wmx_parameters.xml 분석', 'WMX3 파라미터 export 읽어', '엔진 파라미터 검토', '축 설정 분석' 등의 요청에 자동 적용. (ENI/ec_network.def는 wmx3-app-eni, 코드 리뷰는 wmx3-app-review 담당)"
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep, Agent
---

# WMX3 Config Export 분석

> 이 스킬은 WMX3 엔진의 **파라미터 export XML**(WMX3Agent/WOS의 "파라미터 Export" 산출물,
> 예: `wmx_parameters.xml`)을 읽어 분석합니다. 이 파일은 코드가 아니라 **엔진 런타임 파라미터의
> 스냅샷**이며, 실기의 축 구성·안전 설정을 그대로 담고 있습니다.
> 파일 포맷·필드 사전은 `references/config-export-format.md`, 검토 항목은
> `references/config-analysis-checklist.md`를 참조합니다.

**다른 스킬과의 구분**
- **ENI / ec_network.def**(EtherCAT 네트워크 구성) → `wmx3-app-eni`
- **애플리케이션 소스 코드 리뷰**(API 오용·시퀀스·에러 처리) → `wmx3-app-review`
- 이 스킬은 **엔진 파라미터 export 파일** 자체의 분석·검토 담당입니다. 코드 소스가 함께 있으면
  이 분석 결과를 근거로 `wmx3-app-review`를 이어서 수행합니다.

---

## 왜 파서를 먼저 쓰는가

export 파일은 통상 **128축 × 9개 파라미터 그룹 ≈ 19,000줄(약 1MB)** 로 큽니다. 그런데 대부분의
축은 **손대지 않은 공장 디폴트**이고 실제 장비에 쓰이는 축은 소수입니다. 파일을 통째로 Read하면
컨텍스트만 소모하고 핵심을 놓칩니다.

**핵심 전략**: 각 필드의 전체 축 값 중 **최빈값을 디폴트(baseline)로 보고, 벗어난 축만** 골라냅니다.
동봉 파서 `assets/parse_wmx_config.py`가 이 판별·요약·자동 플래그를 한 번에 수행합니다.

---

## 절차 (4단계)

### 1. 파일 확인 — export 파일인지 검증

```bash
head -3 "<파일경로>"   # <?xml ...?> / <Parameters ver="..."> 확인
```

루트가 `<Parameters>`가 아니면 export 파일이 아닙니다(파서가 명시적으로 거부). ENI/def/소스면
해당 스킬로 안내합니다.

### 2. 파서 실행 — 설정 축 식별 + 요약 + 자동 플래그 (+ CSV 산출)

```bash
S="${CLAUDE_SKILL_DIR}/assets/parse_wmx_config.py"
python3 "$S" "<파일경로>"                                  # ① 텍스트 리포트(사람용)
python3 "$S" "<파일경로>" --format csv --out "<출력>.csv"  # ② 축별 CSV(스프레드시트/비교용)
python3 "$S" "<파일경로>" --format json                    # ③ JSON(기계 판독용)
```

`${CLAUDE_SKILL_DIR}`는 이 스킬 디렉토리입니다(호출 시 실제 절대 경로로 치환).

**텍스트 리포트(①) 출력**:
- **개요**: 파라미터 버전, 총 축 수, 설정(비디폴트) 축 수
- **GlobalParameters 요약**: 플라이트 레코더·E-Stop 주요 필드
- **설정 축 상세**: 축별 핵심 파라미터 + 디폴트에서 변경된 필드 목록
- **자동 검토 플래그**: 명백한 위험 후보(CRITICAL/MAJOR/MINOR/INFO)

**CSV(②) — 분석 산출물**: 한 축 = 한 행, 128축 전부 포함. 컬럼:
`axis, is_active, changed_count, flags, changed_fields, 그리고 핵심 파라미터`
(AxisCommandMode·기어비·토크 제한·소프트리밋·원점·팔로잉 에러 등).
- `is_active=1` 로 필터하면 **설정된 축만** 남습니다(디폴트 축 제외).
- `flags` 는 `SEV:CODE` 를 `|` 로, `changed_fields` 는 `필드=값` 을 `;` 로 이어붙입니다.
- 스프레드시트에서 **정렬·필터**하거나, 두 export 를 CSV 로 뽑아 **장비 간·버전 간 diff**
  (예: `diff <(...A.csv) <(...B.csv)`)에 바로 씁니다.

> Windows에서 `python3`가 MS Store alias로 실패(exit 49)하면 `python` 또는 `py -3`로 재시도합니다.

### 3. 체크리스트 검토 — 판정 확정

파서 플래그는 **후보**입니다. `references/config-analysis-checklist.md`의 A~G 카테고리로 판정을
확정합니다. 원문 확인이 필요하면 축 블록만 핀포인트로 Read/awk 합니다(포맷 가이드 §4).

- 설계 산출물(기어비·토크 제한·소프트리밋 계획)이 있으면 **대조**해 A2/A3/B2 등의 불일치를 확정합니다.
- 장비 사양(모터 정격·스트로크)이 있으면 A4/A5/B3의 과도 여부를 확정합니다.
- 근거 없이 "위험"으로 단정하지 말고, 사양·설계와 대조 가능한 항목만 등급을 올립니다.

### 4. 리포트 + CSV 산출

`references/config-analysis-checklist.md`의 "리포트 형식"에 따라 심각도별로 정리하고,
각 항목에 **축 번호·필드 근거**와 **체크리스트 항목 번호**를 명시합니다.
분석으로 끝내지 말고 **2단계의 CSV(②)를 파일로 남겨** 함께 제시합니다 — 사용자가
스프레드시트에서 직접 확인하거나 다른 장비/버전과 대조할 수 있게 합니다.

---

## 대용량·다중 파일 위임 (선택)

파서가 요약을 작게 만들어 주므로 보통 인라인으로 분석합니다. 다만 다음 경우
`wmx3app-usage-reviewer` 에이전트(읽기 전용) 또는 general-purpose 에이전트에 위임합니다.
- 여러 export 파일을 서로 비교(버전 간 diff, 라인별 장비 간 대조)
- export 파일 + 애플리케이션 소스를 함께 놓고 코드-파라미터 정합성(G 카테고리)까지 검토

위임 시 전달할 정보:
- export 파일 경로(들)와 파서 실행 결과(요약/JSON)
- references 정본 절대 경로: `${CLAUDE_SKILL_DIR}/references/` 아래 문서들(실제 절대 경로로 치환)
- 대조할 설계 산출물·장비 사양·소스 경로(있으면)

---

## 매뉴얼 다이제스트 연동

파라미터 필드의 의미·단위·허용값이 모호하면 manual-digest로 등록된 `wmx37-user-manual-kr`
(및 `wmx3-user-manual-kr`) 다이제스트를 1차 참조합니다
(`~/.claude/manuals/wmx37-user-manual-kr/digest.md`, project 스코프는 `.claude/manuals/`).
축 파라미터·원점복귀·리미트·팔로잉 에러·E-Stop 관련 토픽을 키워드 인덱스로 핀포인트합니다.
갠트리/동기 파라미터는 로봇/다축 동기 토픽을, 다이제스트가 없으면 이 스킬의 `references/`
문서만으로 진행하고 `/manual-digest`로 WMX3.7 매뉴얼 등록을 제안합니다.
답변/산출물에는 출처(§/토픽 또는 체크리스트 항목 번호)를 명시합니다.

---

## references / assets

| 파일 | 내용 |
|------|------|
| `references/config-export-format.md` | export XML 구조·9개 파라미터 그룹 필드 사전·설정 축 판별 원리·원문 핀포인트 방법 |
| `references/config-analysis-checklist.md` | A~G 7카테고리 안전/일관성 검토 항목·심각도 기준·리포트 형식 |
| `assets/parse_wmx_config.py` | export XML 파서 — 설정 축 식별(디폴트 대비 diff)·핵심 파라미터 요약·자동 검토 플래그. 출력 `--format text`(기본)/`csv`(한 축=한 행, 스프레드시트/비교용)/`json`, `--out`으로 파일 저장 |
