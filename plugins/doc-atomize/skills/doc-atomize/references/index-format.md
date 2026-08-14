# 산출물 포맷 (index / part / metadata)

## 0. 명명 규칙 — 왜 `<doc-id>.index.md`인가

```
.claude/atomized/
├── INDEX.md                       ← 마스터 카탈로그 (유일한 대문자)
└── hw-prd/
    ├── hw-prd.index.md            ← 문서별 인덱스 (doc-id 접두 필수)
    ├── hw-prd.metadata.json
    └── parts/001-….md
```

문서별 인덱스를 그냥 `index.md`로 두면 세 가지가 동시에 깨진다:

1. 문서 10개 = 구분 불가능한 `index.md` 10개 (탭·Grep 출력·Read 헤더가 전부 동일)
2. `INDEX.md` / `index.md`는 대소문자 한 글자 차 — Windows·macOS 기본 파일시스템에서 사람도 도구도 혼동한다
3. repo·타 플러그인의 `index.md`와 섞여 `Glob **/*.index.md` 같은 일괄 조회가 불가능해진다

doc-id 접두는 이 셋을 한 번에 해소하고, **부작용으로 전 문서 일괄 검색이 가능해진다**:

```bash
Glob  "**/*.index.md"                       # 등록된 모든 문서 인덱스
Grep  "SetServoOn" --glob "*.index.md"      # 전 문서 역색인 한 번에
```

## 1. `<doc-id>.index.md` — 5섹션 고정

````markdown
---
doc: hw-prd
title: "M.2 Artix-7 EtherCAT 마스터 카드 — 하드웨어 설계 PRD"
source: /abs/path/temp/HW_PRD.md
source_dir: /abs/path/temp
mode: derived            # derived | in-place
parts_count: 13
source_lines: 884
generated: "2026-08-14"
tool: "doc-atomize 1.0.0"
---

# <제목> — 원자 인덱스

> 원본 …을 조각 13개로 무손실 분할한 검색 인덱스.

## 조회 프로토콜        ← ① 읽는 순서 3줄 (항상 동일)
## 라우팅 힌트          ← ② 질문 유형 → 조각 (큐레이션 대상)
## 목차                 ← ③ 조각 목록 + 요약 + 라인범위 + ↳ 포함 헤딩
## 키워드 역색인        ← ④ 자동 추출 키워드 → 조각 번호
## 주의                 ← ⑤ 상대경로 자산·갱신 방법
````

목차 한 줄의 형식:

```markdown
- **005** 5. 전원 설계 → [`005-5-전원-설계`](parts/005-5-전원-설계.md) `L292-390` — 3.3V 입력에서 5개 레일 파생, VCCINT는 3A급 Buck 필수
  ↳ 5.1 전원 아키텍처 · 5.2 전류 버짓 · 5.3 DC-DC 컨버터 선정 · …(2개 더, 본문 참조)
```

`↳` 줄(`contains`)이 있어야 **병합으로 흡수된 절이 목차에서 실종되지 않는다.** 표시 예산은 조각 수에 따라 자동 조정된다(≤25개: 8항목, ≤60개: 5항목, 초과: 장 수준만) — 인덱스는 통째로 읽히는 파일이라 조각이 많을수록 압축해야 한다. **장(章) 수준 헤딩은 예산과 무관하게 항상 표시된다.**

## 2. 조각 프론트매터 — 필드 사전

```yaml
---
id: hw-prd/005-5-전원-설계      # <doc-id>/<파일명(확장자 제외)>
doc: hw-prd                      # 소속 문서
part: 005                        # 순번 (정렬 = 원문 순서)
title: 5. 전원 설계              # 병합 시 "A + B" 결합
path: 5. 전원 설계               # 빵부스러기 — 조각만 읽어도 맥락 복원
source_lines: "292-390"          # 원본 1-based inclusive — 핀포인트 Read용
keywords: [TPS62913, VCCINT, …]  # 자동 추출(또는 큐레이션)
prev: 004-4-클럭-아키텍처         # 앞 조각
next: 006-6-DP83848-PHY-주변회로  # 뒤 조각
---
<원본 본문 그대로>
```

**본문은 절대 편집하지 않는다.** 프론트매터 다음 첫 줄부터 원문이며, 원본이 `---`로 시작해도(선두 프론트매터) 파서가 첫 블록만 벗겨내므로 안전하다. 조각을 손으로 고치면 `verify`가 즉시 실패한다 — 고칠 것은 원본이고, 그 다음 `update`다.

## 3. `<doc-id>.metadata.json` — 정본

요약·키워드·라우팅의 **단일 정본**. 인덱스는 여기서 생성되는 뷰다.

```jsonc
{
  "id": "hw-prd",
  "title": "…",
  "source": "/abs/path/HW_PRD.md",
  "source_dir": "/abs/path",
  "mode": "derived",
  "generated": "2026-08-14",
  "base_level": 2,
  "limits": {"min_lines": 40, "max_lines": 250, "hard_max": 400},
  "slug_style": "auto",
  "source_total_lines": 884,
  "source_sha256_raw": "…",          // 원본 바이트 — 변경 감지용
  "source_sha256_normalized": "…",   // 정규화본 — 무손실 검증 기준
  "line_ending": "lf",
  "routing_hints": [
    {"question": "전원 레일 구성·전류 버짓", "parts": ["005-5-전원-설계"]}
  ],
  "parts": [
    {
      "n": "005",
      "name": "005-5-전원-설계",
      "file": "parts/005-5-전원-설계.md",
      "title": "5. 전원 설계",
      "level": 2,
      "path": ["5. 전원 설계"],
      "kind": "section",              // section | preamble | overflow
      "lines": [292, 390],
      "nlines": 99,
      "body_sha256": "…",             // 조각 단위 변경 감지
      "contains": [["5.1 전원 아키텍처", 3], …],
      "keywords": ["TPS62913", …],
      "summary": "…",
      "summary_source": "auto",       // auto | curated  ← curated여야 update가 보존
      "prev": "004-…", "next": "006-…"
    }
  ]
}
```

### 큐레이션 계약

| 필드 | 누가 쓰나 | 갱신 시 |
|---|---|---|
| `summary` + `summary_source: "curated"` | 사람/Claude | 승계. 본문이 바뀌었으면 `summary_stale: true`가 붙고 인덱스에 ⚠️ 표시 |
| `keywords` + `keywords_source: "curated"` | 사람/Claude | 승계 |
| `routing_hints` | 사람/Claude | 승계 |
| 그 외 전부 | 스크립트 | 매번 재계산 |

`summary_source`를 `curated`로 바꾸지 않으면 다음 `update`에서 자동 요약으로 덮인다. 큐레이션 후에는 반드시 `reindex`한다.

## 4. `INDEX.md` — 마스터 카탈로그

```markdown
# Atomized Documents

> doc-atomize가 관리하는 원자 분할 문서 카탈로그. 문서 내용이 필요한 질문을 받으면
> **먼저 이 파일을 확인**하고, 해당 문서의 `<doc-id>.index.md`를 진입점으로 사용한다.

## 등록된 문서

| id | 제목 | 원본 | 줄수 | 조각 | scope |
|----|------|------|------|------|-------|
| hw-prd | M.2 Artix-7 EtherCAT 마스터 카드 PRD | temp/HW_PRD.md | 884 | 13 | project |

## 참조 규칙
1. 등록 문서 관련 질문 → 본 INDEX.md 확인
2. `<doc-id>/<doc-id>.index.md` 진입 → 라우팅 힌트·키워드 역색인으로 조각 특정
3. `parts/*.md`만 Read — 원본 전체 Read 금지
4. 답변에 출처(조각 id·`source_lines`) 명시
5. 미등록 대형 .md면 `/doc-atomize <path>` 등록 제안
```
