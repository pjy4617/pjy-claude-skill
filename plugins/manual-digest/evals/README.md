# manual-digest eval 스위트

`manual-digest` 스킬의 **문서(PDF) 인제스트 흐름** 하나를 검증한다. 케이스 9개 = 발동 7 + 발동금지 2. `08`·`09` 는 부품 모드(`--component`) 케이스다 — `08` 은 `--check` 판정 근거, `09` 는 `--step`/`--lcsc` 를 버리지 않고 생성 단계로 이어 가는지 본다.

## 실행

```bash
cd plugins/manual-digest
claude plugin eval . --ablation with-without --judge-model opus --allow-tools Bash
```

로컬에만 두려면 `--no-publish`를 붙인다. 머리 숫자는 합격률이 아니라 **Δ**(플러그인 켠 점수 − 끈 점수)다.

## 실행 전 준비

`socat` 이 설치돼 있어야 한다. `Bash` 권한을 주면 러너가 실행을 OS 샌드박스에 가두는데,
그 백엔드가 `bubblewrap` + `socat` 을 요구한다. 없으면 14회 실행이 전부 3초 만에 거부된다.

```bash
sudo apt install socat     # bubblewrap 은 대개 이미 있다
```

## 필수 플래그 — `--allow-tools Bash`

**이 플래그가 없으면 발동 케이스 5개가 양쪽 arm 모두 0점이 되고, "플러그인이 아무것도 안 했다"로 읽힌다.**
스킬 프론트매터의 `allowed-tools` 는 실행 안에서 권한으로 쳐주지 않는다 — 운영자가 직접 줘야 한다.

`Write` 와 `Edit` 는 일부러 주지 않는다. eval 샌드박스는 `.claude/` 경로에 대해 이 두 도구를 거부하고
(경로 패턴 `Write(.claude/**)` 를 줘도 거부된다), Bash 경유 쓰기만 통과한다. manual-digest 는 산출물을
전부 `.claude/manuals/` 아래에 쓰므로, `Write` 를 허용하면 에이전트가 그 도구를 먼저 골랐다가 막혀서
인제스트를 포기한다. 실측: `Write` 허용 시 5개 중 2개만 성공, `Bash` 만 허용 시 5개 전부 성공.

## 픽스처를 두지 않는 이유

케이스는 매번 빈 샌드박스에서 시작하고, `evals/` 안의 파일도 케이스 디렉토리 안의 파일도 그리로
복사되지 않는다(`prompt.md` 에 scaffold 훅이 없고, `case.yaml` 의 `scaffold_script` 가 만든 파일도
실행 cwd 에 나타나지 않는다). 그래서 각 프롬프트가 앞부분에서 **파이썬으로 39페이지 샘플 PDF를
직접 만든 뒤** 그것을 인제스트한다. 샌드박스 안에 PyMuPDF 와 pdftotext 가 모두 있어 성립한다.

샘플 PDF의 수치는 실존 부품과 일부러 다르게 잡았다 — 부품명 `ACME-MX184RB`, 184 MHz, Flash 192 KB,
SRAM 48 KB. 모델이 파일을 읽지 않고 기억으로 답하면 반드시 틀리게 만들기 위해서다. 초기에 실제
STM32G431 데이터시트를 쓰다가, 모델이 PDF 없이도 정답(170 MHz)을 맞히는 바람에 그레이더가 파일
접근 실패를 통과시킨 적이 있다.

## 채점 기준

발동 케이스(`01`~`05`)는 "인제스트가 끝났다고 했는데 산출물이 반만 생긴" 회귀를 겨눈다.

| 그레이더 | 타입 | 가중 | 본다 |
|---|---|---|---|
| `a-digest-created` | regex/files | 1 | `.claude/manuals/<id>/digest.md` 생성 |
| `b-index-created` | regex/files | 1 | `index.md` 생성 |
| `c-metadata-created` | regex/files | 1 | `metadata.json` 생성 |
| `d-catalog-entry` | regex/file | 1 | `INDEX.md` 카탈로그에 항목 추가 |
| `e-extractor-honest` | regex/file | 1 | `extractor` 값이 실제 도구명 (추출 실패를 감추지 않았는가) |
| `f-facts-freq` | regex/file | 1 | 본문에 `184 MHz` |
| `g-facts-mem` | regex/file | 0.5 | 본문에 `192 K` |
| `h-no-contamination` | regex/file (없어야 함) | 0.5 | `170 MHz`·`128 Kbytes` 오염 차단 |
| `i-page-pointers` | regex/file | 1 | `p.NN` 페이지 포인터 3곳 이상 |
| `j-substance` | llm | 1 | 섹션 요약이 장마다 고유한 내용인가 (껍데기 판별) |
| `k-report-paths` | regex/last_message | 0.5 | 마무리 보고에 산출물 경로 명시 |
| `z-skill-fired` | tool_used | 비채점 | 트리거 표시용 (ablation 리포트에만) |

발동금지 케이스(`06`,`07`)는 `.claude/manuals/` 아래에 아무것도 안 생기고(`a-no-registration`),
스킬이 안 뜨고(`z-skill-not-used`, 양쪽 arm 채점), **동시에 질문에는 제대로 답해야** 통과한다.
답변 그레이더가 없으면 "아무것도 안 하기"로 만점을 받을 수 있다.

## llm 그레이더 주의

`j-substance` 루브릭은 **다이제스트 파일 하나만 보고 판정할 수 있는 것만** 묻는다. 초안에서
"원본에 없는 수치가 적혀 있으면 거짓"을 넣었다가, 판정 모델이 원본 PDF를 볼 수 없어 같은 내용에
FAIL/FAIL/FAIL → PASS/FAIL/FAIL → PASS/PASS/PASS 로 흔들렸다. 확인 불가한 요구를 넣지 말 것.

판정 모델은 에이전트 모델과 달라야 한다(자기 편향). 케이스가 `model: sonnet` 이므로 `--judge-model opus`.

## 실측 기준선 (2026-09-15, Sonnet 에이전트 / Opus 판정)

- 발동 5개: with 1.00 / without 0.00 → Δ +1.00 each
- 발동금지 2개: with 1.00 / without 1.00 → Δ 0.00
- 평균 Δ +0.71, 1회 실행(runs 1) $5.51 / 1,457초
- 전체 실행(runs 3) 추정 $16.5 / 약 70분
- 최장 케이스 380초·28턴 (상한 900초·40턴)
