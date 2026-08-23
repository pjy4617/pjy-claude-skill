# metadata.json 스키마

manual-digest가 매뉴얼 1건마다 `<scope>/.claude/manuals/<id>/metadata.json`에 기록하는 공통 스키마.
digest.md 프론트매터와 같은 값을 기록한다 (두 곳의 값이 달라지면 안 된다 — 정본은 metadata.json).
코드베이스(`format: codebase`) 전용 필드는 `codebase-extract.md`의 "metadata.json" 절 참조.

## 필수 필드 (문서 포맷 공통)

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | kebab-case 매뉴얼 ID. 디렉토리명과 동일 |
| `title` | string | 매뉴얼 제목 |
| `source` | string | 원본 절대 경로 |
| `format` | string | `pdf` / `html` / `epub` / `docx` / `chm` / `md` / `txt` / `codebase` |
| `scope` | string | `project` 또는 `global` |
| `pages` | int | 원본 페이지 수 (페이지 개념이 없는 포맷은 최상위 섹션 수) |
| `sha256` | string | 원본 파일 sha256 — 재인제스트 스킵 판정 기준 |
| `indexed_at` | string | 인제스트 완료 ISO 8601 타임스탬프 |
| `extractor` | string | `mcp-pdf-reader` / `claude-read` / `expand-archive` / `hh-decompile` |

## 선택 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `publisher` | string | 발행처/제조사 |
| `version` | string | 매뉴얼 버전 |
| `publication_date` | string | 발행일 (ISO 날짜) |
| `language` | string | BCP47 언어 태그 (예: `ko-KR`) |
| `extractor_package` | string | 추출에 사용한 패키지/도구와 버전 |
| `subsection_count` | int | 요약된 하위 섹션 수 |
| `sampling_strategy` | string | 전수/샘플링 전략 서술 (대형 문서에서 일부만 정독한 경우) |
| `atomized` | object\|null | 다이제스트 무손실 분할 상태 (아래 참조). 분할하지 않았으면 생략하거나 `null` |

## `atomized` 필드

`digest.md`(또는 `index.md`)가 커서 `doc-atomize`의 `split_md.py`로 분할한 경우에만 기록한다.
절차는 `digest-atomize.md` 참조.

```json
"atomized": {
  "digest": {
    "dir": "digest.atomized",
    "doc_id": "wmx37-user-manual-kr-digest",
    "index": "digest.atomized/wmx37-user-manual-kr-digest.index.md",
    "parts": 14,
    "source_lines": 1340,
    "split_at": "2026-08-22T10:12:00+09:00",
    "verified": true
  },
  "index": null
}
```

| 하위 키 | 타입 | 설명 |
|---------|------|------|
| `digest` | object\|null | `digest.md` 분할 상태. 미분할이면 `null` |
| `index` | object\|null | `index.md` 분할 상태. 미분할이면 `null` |
| `.dir` | string | 매뉴얼 디렉토리 기준 상대 경로 (`digest.atomized` / `index.atomized`) |
| `.doc_id` | string | split_md.py에 넘긴 `--doc-id`. 인덱스 파일명 접두와 동일 |
| `.index` | string | 조회 진입점 파일의 상대 경로 |
| `.parts` | int | 조각 수 |
| `.source_lines` | int | 분할 시점의 원본(digest.md) 줄 수 |
| `.split_at` | string | 분할/최근 갱신 ISO 8601 타임스탬프 |
| `.verified` | bool | 마지막 `split_md.py verify` 결과. `false`면 조회에 쓰지 않는다 |

`verified: false`인 분할본은 **조회 경로에서 제외**하고 `digest.md`를 직접 읽는다.

## 코드베이스와의 차이

`format: codebase`는 문서 전용 필드(`sha256`/`pages`/`publication_date`)를 생략하거나 `null`로 두고,
대신 `loc` / `src_files` / `test_files` / `stack` / `version`(git ref) / `sampling_strategy` /
`<purpose>_targets` / `<purpose>_caveats`를 사용한다. 전체 예시는 `codebase-extract.md` 참조.
