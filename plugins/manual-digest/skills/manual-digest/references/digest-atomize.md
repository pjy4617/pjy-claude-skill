# 다이제스트 원자 분할 (digest atomization)

다이제스트가 커지면 그 자체가 컨텍스트 부담이 된다. 이때 `doc-atomize`의 `split_md.py`로
`digest.md`를 **무손실 분할**해, 이후 조회를 `인덱스 1개 + 조각 1~3개`로 줄인다.

## 왜 필요한가

manual-digest의 원래 이득은 "원본 대신 다이제스트만 읽는다"이다. 그런데 1000페이지급 매뉴얼이나
대형 모노레포를 인제스트하면 다이제스트 자체가 수천 줄이 되어, 매뉴얼 질문 한 번마다 수만 토큰이
들어간다. 압축을 한 번 더 하는 대신(정보가 더 깎인다), **다이제스트를 쪼개서 필요한 절만 읽는다.**

- 요약을 한 번 더 하기: 정보 손실이 누적된다. 하지 않는다.
- 분할하기: 총량은 그대로지만 **읽는 양**이 줄고, 조각을 합치면 원본 다이제스트와 sha256이 일치한다.

## 언제 분할하는가

| `digest.md` 크기 | 판정 |
|---|---|
| 300줄 미만 | **분할 금지**. 인덱스 유지비가 이득보다 크다 |
| 300~699줄 | 분할하지 않는다. 사용자가 명시적으로 `--atomize`를 요청하면 진행 |
| **700줄 이상 또는 50 KB 이상** | **분할 권고** — 인제스트 마무리에서 사용자에게 제안 |
| 1200줄 이상 또는 90 KB 이상 | 강하게 권고. 이 크기는 매 질문마다 20k 토큰 이상을 태운다 |

`index.md`(섹션→페이지 매핑, 코드베이스는 심볼→파일)도 같은 임계를 적용한다. 1000p 매뉴얼의
`index.md`는 종종 digest보다 크다.

측정:

```bash
D="<scope_root>/.claude/manuals/<id>"
wc -l "$D/digest.md" "$D/index.md"
wc -c "$D/digest.md" "$D/index.md"
```

## 산출물 배치

분할본은 **그 매뉴얼 디렉토리 안**에 둔다. 매뉴얼 1건 = 디렉토리 1개라는 규칙을 깨지 않기 위해서다.

```
<scope_root>/.claude/manuals/<id>/
├── digest.md                       ← 정본(분할 원본). 지우지 않는다
├── index.md
├── metadata.json
├── digest.atomized/                ← 분할본 (파생물)
│   ├── <id>-digest.index.md        ← 조회 진입점
│   ├── <id>-digest.metadata.json
│   └── parts/001-….md …
└── index.atomized/                 ← index.md도 분할했을 때만
    └── …
```

**`.claude/atomized/`에 등록하지 않는다.** 이유:

1. 매뉴얼 카탈로그(`.claude/manuals/INDEX.md`)와 분할 카탈로그(`.claude/atomized/INDEX.md`)에
   같은 것이 두 번 등록되면 조회 경로가 갈린다
2. doc-atomize의 PostToolUse 훅은 `.claude/atomized/` 아래만 스캔하므로, 여기 두면 훅이 반응하지
   않는다 — **의도한 것이다.** 다이제스트 갱신은 `/manual-digest --update`가 책임진다
3. `digest.md`는 사람이 손으로 고치는 문서가 아니라 인제스트 산출물이다. 자동 훅의 대상이 아니다

**`digest.md`는 지우지 않는다.** doc-atomize의 `--in-place` 모드는 쓰지 않는다. 원본이 남아 있어야
`verify`(재조립 대조)와 `--update`(변경분 재분할)가 성립한다. 디스크는 2배가 되지만 컨텍스트 비용은
0이고, 파생물이므로 드리프트 위험도 없다.

## split_md.py 찾기

doc-atomize 플러그인이 함께 설치되어 있어야 한다. 탐색 순서는 doc-atomize 훅과 동일하다:

```bash
find_split_md() {
    # 1) 환경변수 고정 경로
    if [ -n "$DOC_ATOMIZE_SPLIT_MD" ] && [ -f "$DOC_ATOMIZE_SPLIT_MD" ]; then
        echo "$DOC_ATOMIZE_SPLIT_MD"; return 0
    fi
    # 2) 플러그인 캐시 (설치 경로가 버전별로 달라지므로 glob 대신 find)
    local p
    p="$(find "$HOME/.claude/plugins" \
            -path "*doc-atomize*/skills/doc-atomize/assets/split_md.py" \
            -print -quit 2>/dev/null)"
    [ -n "$p" ] && { echo "$p"; return 0; }
    # 3) 개발 레포 체크아웃
    [ -f "./plugins/doc-atomize/skills/doc-atomize/assets/split_md.py" ] && {
        echo "./plugins/doc-atomize/skills/doc-atomize/assets/split_md.py"; return 0
    }
    return 1
}
```

`**` 글롭은 셸 설정(`globstar`)에 의존하므로 쓰지 않는다.

찾지 못하면 **인제스트를 실패시키지 않는다.** 분할만 건너뛰고 다음을 안내한다:

```
digest.md가 1,340줄입니다. 분할하면 조회 비용이 크게 줄지만
doc-atomize 플러그인의 split_md.py를 찾지 못했습니다.
  /plugin 에서 doc-atomize 설치 후 → /manual-digest --atomize <id>
```

Windows에서 `python3`가 MS Store alias로 exit 49면 `py -3` 또는 `python`으로 대체한다.

## 분할 절차

### 1. 분할 실행

```bash
S="$(find_split_md)"
D="<scope_root>/.claude/manuals/<id>"

python3 "$S" split "$D/digest.md" \
    --out "$D/digest.atomized" \
    --doc-id "<id>-digest" \
    --title "<매뉴얼 제목> — 다이제스트"
```

- `--doc-id`를 반드시 준다. 주지 않으면 파일명에서 `digest`가 뽑혀, 매뉴얼이 여러 개일 때 인덱스
  파일명이 전부 `digest.index.md`로 겹친다
- `--mode in-place`는 쓰지 않는다 (위 "산출물 배치" 참조)
- 조각이 80개를 넘는다는 경고가 나오면 `--max-lines 350` 정도로 올려 재분할한다
- 다이제스트는 `## 섹션별 요약` 아래 `### §n` 가 실질 본문이므로 `--base-level 3`이 잘 맞는 경우가
  많다. 기본값(자동)으로 조각이 지나치게 크게 잡히면 이 옵션을 쓴다

### 2. 무손실 검증 (게이트)

```bash
python3 "$S" verify "$D/digest.atomized"
```

`PASS`가 아니면 **분할본을 지우고 원래 상태로 되돌린다.** 무손실이 깨진 분할은 쓸모가 없다:

```bash
rm -rf "$D/digest.atomized"
```

실패 사실과 원인을 사용자에게 보고한다. `digest.md`는 그대로이므로 조회는 종전대로 동작한다.

### 3. 의미 큐레이션 (게이트)

**여기를 건너뛰면 분할이 헛돈다.** 조회 비용을 정하는 것은 조각 크기가 아니라 **조회당 여는 조각 수**이고,
그 수는 조각 요약과 라우팅 힌트가 얼마나 정확히 조각을 지목하느냐로 정해진다. 조각 3개를 여는 대신
1개로 끝내는 것이, 조각을 잘게 쪼개는 것보다 크다.

**다이제스트는 특히 위험하다.** 사람이 쓴 문서가 아니라 요약 산출물이라 문장이 균질하고 절 제목이
비슷비슷하다 — 자동 요약이 제목 재진술이나 하위 헤딩 나열로 떨어질 확률이 PRD·설계서보다 높다.

`digest.atomized/<id>-digest.metadata.json`이 요약·라우팅의 정본이다. 인덱스 마크다운을 직접 고치지
말고 metadata를 고친 뒤 `reindex`한다 (그래야 `--update` 때 큐레이션이 살아남는다).

1. 자동 생성된 조각 요약 중 부실한 것을 다시 쓰고 `summary_source`를 `"curated"`로 바꾼다
2. `routing_hints`를 채운다. **매뉴얼 사용자가 실제로 물어볼 질문**으로 쓴다:
   ```json
   "routing_hints": [
     {"question": "서보 온 시퀀스와 타임아웃", "parts": ["004-4-축-제어"]},
     {"question": "에러 코드 목록·복구 절차", "parts": ["009-9-에러-처리"]}
   ]
   ```
3. 재생성:
   ```bash
   python3 "$S" reindex "$D/digest.atomized"
   ```
4. **게이트** — 통과할 때까지 1~3을 반복한다:
   ```bash
   python3 "$S" audit "$D/digest.atomized" --strict
   ```
   `BLOCK`이 하나라도 있으면 exit 1이며, **4단계(metadata 기록)로 가지 않는다.**

무손실 검증 실패와 이 게이트 실패는 대응이 다르다:

| 실패 | 의미 | 대응 |
|---|---|---|
| `verify` FAIL | 분할이 성립하지 않았다 | `digest.atomized/` 삭제, 원상 복구, 원인 보고 |
| `audit` BLOCK | 분할은 맞지만 라우팅이 동작하지 않는다 | **지우지 않는다.** 큐레이션을 더 해서 통과시킨다 |

지적 코드(S1~S8 / R1~R8)의 전체 표는 doc-atomize의 `references/index-format.md`에 있다.

#### 조각 요약 작성 규칙

**한 줄, 90자 이내, 그 조각에만 있는 정보.** 공식: `[대상] + [값·판정] + [주의]`.
부품번호·API명·에러코드·수치 같은 **식별 토큰을 최소 1개** 넣는다 — 그것이 조각을 구별하는 손잡이다.

다이제스트 조각에서는 **원본 위치(`§`·페이지)를 요약에 함께 넣는다.** 식별 토큰 노릇을 하면서
동시에 원본 핀포인트가 되어, 조각을 열기 전에 이미 "어느 페이지를 봐야 하는가"가 정해진다.

| 나쁜 요약 | 왜 나쁜가 | 이렇게 쓴다 |
|---|---|---|
| `이 절은 축 제어를 설명한다` | 제목의 재진술. 제목은 이미 목차에 있다 | `§4.2 SetServoOn 후 최대 3초 대기, 타임아웃 시 -7 반환 (p.82)` |
| `에러 처리에 대해 기술한다` | 서술 동사만 있고 식별 토큰이 없다 | `§9 에러코드 -1~-99 분류표와 복구 절차 (p.210-218)` |
| `4.1 개요 / 4.2 서보 온 / 4.3 정지` | 자동 폴백 그대로. 목차 `↳` 줄과 완전 중복 | 그 절들이 합쳐 정하는 것을 한 줄로 |
| `표: 항목 · 값 · 비고` | 표 헤더 덤프. 무슨 표인지 모른다 | `축 파라미터 기본값·범위 표 (p.140)` |

#### 라우팅 힌트 작성 규칙

- **질문 형태로 쓴다.** 다이제스트의 절 제목을 복사하지 않는다 — 그건 이미 목차에 있어 새 진입 경로가 아니다
- **하나가 조각 1개를 가리키게 쓴다.** 3개를 넘게 가리키면 좁히지 못한 것이고, 그대로 조회당 조각 수가 된다.
  목표는 **힌트당 평균 1.5개 이하** (`audit`이 이 수치를 출력한다)
- **개수**: 조각 15개 이하면 5개 이상, 그보다 크면 `조각수 ÷ 4`개(최대 12개)
- **평균 크기 이상인 조각은 최소 하나의 힌트에 걸리게 한다.** 어떤 힌트에도 없는 큰 조각은 Grep으로만 도달 가능해진다
- **매뉴얼 용어가 아니라 질문자 어휘로 쓴다.** 매뉴얼이 "서보 온 시퀀스"라 해도 실제 질문은
  "모터가 안 돈다"로 온다. API명·에러코드·증상 표현을 같이 넣는다 — 이것이 매뉴얼 다이제스트에서
  가장 값이 큰 큐레이션이다

### 4. metadata.json에 기록

매뉴얼 쪽 `metadata.json`에 `atomized` 필드를 추가한다 (스키마는 `metadata-schema.md`).

```json
"atomized": {
  "digest": {
    "dir": "digest.atomized",
    "index": "digest.atomized/wmx37-user-manual-kr-digest.index.md",
    "doc_id": "wmx37-user-manual-kr-digest",
    "parts": 14,
    "source_lines": 1340,
    "split_at": "2026-08-22T10:12:00+09:00",
    "verified": true
  },
  "index": null
}
```

`index.md`를 분할했으면 `"index"`에 같은 형태로 채운다. 분할하지 않은 쪽은 `null`.

### 5. 카탈로그 표기

`<scope_root>/.claude/manuals/INDEX.md`의 해당 행에 분할 여부를 표시한다. Claude가 INDEX만 보고도
"digest.md를 통째로 읽으면 안 된다"를 알아야 하기 때문이다.

```markdown
| id | 제목 | 포맷 | 분할 | 요약 |
|----|------|------|------|------|
| wmx37-user-manual-kr | WMX3 v3.7 사용자 매뉴얼 | pdf | digest(14조각) | EtherCAT 모션 제어 API 레퍼런스 |
| stm32f4-rm0090 | STM32F4 Reference Manual | pdf | — | 페리페럴 레지스터 정의 |
```

## 분할 후 조회 규칙

분할본이 있는 매뉴얼은 **`digest.md`를 통째로 읽지 않는다.**

1. `.claude/manuals/INDEX.md`에서 대상 매뉴얼 확인 — "분할" 칸이 비어 있지 않으면 아래로
2. `digest.atomized/<id>-digest.index.md` 읽기 (라우팅 힌트 → 목차 → 키워드 역색인)
3. 후보 조각 1~3개만 `parts/`에서 Read
4. 그래도 부족하면 종전대로 `index.md`의 페이지/파일 포인터로 **원본** 핀포인트 추출
5. 답변에 출처 명시 — 조각을 인용해도 근거는 원본 기준(`§4.2, p.82`)으로 쓴다.
   조각은 다이제스트의 일부일 뿐 원본의 페이지가 아니다

전 매뉴얼 분할본을 한 번에 훑어야 할 때:

```bash
grep -rn "<키워드>" <scope_root>/.claude/manuals/*/*.atomized/*.index.md
```

## 갱신 (`--update`와의 관계)

`/manual-digest --update <id>`로 다이제스트를 다시 쓰면 분할본이 **낡는다.** 갱신 절차 마지막에
반드시 이어서 실행한다:

```bash
python3 "$S" update "$D/digest.atomized"   # 변경 조각만 재생성 + 큐레이션 승계 + 무손실 재검증
```

- 원본(`digest.md`) sha256이 같으면 아무 일도 하지 않는다
- 본문이 바뀐 조각의 승계 요약에는 `summary_stale`이 붙고 인덱스에 `⚠️`로 나타난다 →
  그 요약을 다듬고 `reindex`한다. **이건 자동화되지 않는다**
- `metadata.json`의 `atomized.digest.parts` / `split_at`을 갱신한다

`--update`가 분할본 갱신을 건너뛰면 **다이제스트와 조각이 어긋난 채 조회된다** — 가장 위험한 실패
모드다. update 리포트에 분할본 갱신 결과를 반드시 포함한다.

## 해제 (`--deatomize`)

분할이 오히려 번거로울 때(조각이 잘못 잡혔거나 다이제스트가 축소된 경우) 되돌린다:

```bash
rm -rf "$D/digest.atomized" "$D/index.atomized"
```

그다음 `metadata.json`의 `atomized`를 `null`로, INDEX.md의 "분할" 칸을 `—`로 되돌린다.
`digest.md`는 손대지 않았으므로 조회는 즉시 종전 방식으로 돌아간다.

## 제거 (`--remove`)와의 관계

`/manual-digest --remove <id>`는 매뉴얼 디렉토리를 통째로 지우므로 분할본도 함께 사라진다.
별도 처리가 필요 없다. `.claude/atomized/`에 등록하지 않았기 때문에 남는 고아 항목도 없다.

## 흔한 함정

| 함정 | 해결 |
|------|------|
| `--doc-id` 없이 split → 인덱스 파일명 충돌 | 항상 `--doc-id "<id>-digest"` 지정 |
| `--mode in-place`로 digest.md 삭제 | 쓰지 않는다. verify·update가 원본을 필요로 한다 |
| verify FAIL인데 분할본을 남김 | 즉시 `rm -rf`. 무손실 아닌 조각은 인용 근거가 못 된다 |
| `--update` 후 분할본 미갱신 | update 절차에 `split_md.py update`를 붙박이로 포함 |
| 분할본을 `.claude/atomized/`에 등록 | 카탈로그가 갈리고 훅과 `--update`가 충돌한다 |
| 300줄짜리 다이제스트를 분할 | 인덱스 유지비가 더 크다. 임계 미만이면 하지 않는다 |
| 조각을 인용하며 출처를 조각 번호로 표기 | 출처는 원본 기준(§/p.)으로 쓴다 |
