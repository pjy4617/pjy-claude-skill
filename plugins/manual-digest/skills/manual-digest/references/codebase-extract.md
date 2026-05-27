# 코드베이스 추출 가이드

소스코드 디렉토리(레포 또는 하위 패키지)를 **하나의 매뉴얼**로 다이제스트한다. 문서 포맷과 달리 "페이지"가 없고, 단위는 **디렉토리·파일·심볼**이다. 핀포인트는 `mcp__pdf-reader__read_pdf`가 아니라 `Read`/`Grep`/`Glob`이다.

추출기(extractor)는 `claude-read` — Claude가 코드를 직접 읽어 요약한다. MCP 의존성이 없으므로 PDF MCP 미등록 상태에서도 동작한다.

## 언제 코드베이스 포맷인가

`source`가 **디렉토리**이면 자동으로 `format: codebase`. 트리거 예시:
- "이 레포 코드베이스 다이제스트 만들어줘"
- "`Frontend/` 소스 인덱싱해줘"
- `/manual-digest ./src` 처럼 디렉토리 경로 지목
- "런타임 구현할 때 재사용할 자산 빨리 찾게 코드 맵 만들어줘"

문서 파일(PDF/HTML/...) 단건이면 기존 포맷 가이드를 따른다.

## 추출 목적 먼저 확정 (★ 가장 중요)

코드베이스 다이제스트는 범용 요약이 아니라 **목적 지향 인덱스**다. 인제스트 시작 시 사용자에게 목적을 1줄로 확인한다:
- "재사용/공유 자산 탐색" (예: 다른 프로젝트·모노레포에서 무엇을 가져다 쓸지)
- "온보딩/아키텍처 파악"
- "리팩토링/마이그레이션 대상 식별"
- "디버깅용 데이터 흐름 맵"

목적에 따라 `sampling_strategy`, 디렉토리 맵의 **주석 컬럼**(예: "재사용 ★/△/전용"), 그리고 **본문 섹션 구성**이 달라진다. 목적 없는 전수 요약은 토큰만 쓰고 쓸모가 낮다.

목적을 frontmatter/metadata에 `purpose` 필드로 명시한다. 목적별 권장 산출물:

| 목적 | 디렉토리 맵 주석 | 추가 섹션 / metadata |
|------|-----------------|---------------------|
| 재사용/공유 탐색 | "재사용 가치 ★/△/전용" | **재사용 자산 빠른 표**(무엇을/어디서/어떻게+주의) + `reuse_targets` + `reuse_caveats` |
| 온보딩/아키텍처 | "역할 / 진입점" | 데이터 흐름·계층 다이어그램 |
| 리팩토링 식별 | "부채 / 강결합 / 중복" | `refactor_targets` + 우선순위 |
| 디버깅 흐름 | "흐름상 위치" | 이벤트→상태→렌더 경로 |

## 스택/규모 자동 수집

```bash
# 규모
find <src> -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.c' -o -name '*.py' ... \) | wc -l   # 파일 수
# 또는 cloc/scc가 있으면 사용
# 라인 수 (간이)
find <src> -name '*.ts*' -not -path '*/node_modules/*' | xargs wc -l | tail -1

# 스택 + 정체성 (언어/런타임별 manifest) — ★ 추측 금지, manifest로 확정
cat package.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('name=',d.get('name'),'version=',d.get('version'),'private=',d.get('private')); print(d.get('dependencies'))"
# pyproject.toml / Cargo.toml / go.mod / CMakeLists.txt / *.csproj 등도 동일하게

# 버전 핀 (git)
git -C <src> rev-parse --short HEAD
git -C <src> branch --show-current
git -C <src> status --porcelain | head -1   # 비어있지 않으면 dirty
```

metadata에 기록: `loc`, `src_files`, `test_files`, `stack`(주요 의존성 버전 맵), `version`(git ref + 브랜치, dirty면 표기).

★ **패키지명·버전 등 정체성은 manifest에서 읽어 확정한다 — "패키지명 추정 ~"처럼 검증 안 된 추측을 본문에 쓰지 않는다.**

## 구조 파싱 (TOC 대응)

문서의 목차 = 코드베이스의 **디렉토리 트리 + 심볼 인덱스**.

1. 최상위 디렉토리 트리 파악 (`Glob`, `ls`, `find -maxdepth 2`)
2. 진입점·manifest 먼저 읽기: `package.json` scripts, 빌드 설정, 라우터/`main`/`index`, 프로젝트 `CLAUDE.md`/`README`
3. 디렉토리별 역할 매핑 — 각 디렉토리에서 대표 파일 1~2개만 열어 역할 추론
4. 핵심 심볼 추출: 타입/스키마 정의 파일, 공개 인터페이스, store/상태, 진입 함수

## 샘플링 전략

전수 읽기 금지. **목적 기준 가중 샘플링**:

| 우선순위 | 대상 | 깊이 |
|---------|------|------|
| 1 (전수 Read) | 목적과 직결되는 핵심 파일 (타입 단일소스, 공유 후보, 데이터 모델) | 전체 본문 |
| 2 (맵핑만) | 목적과 무관한 UI/보일러플레이트 | 파일명·역할 1줄 |
| 3 (규칙만) | 빌드/lint/테스트 설정 | 게이트·규칙 추출 |
| 4 (포인터) | 나머지 | `index.md`에 경로만 |

> ★★ **우선순위 1 파일은 디렉토리 맵 추론으로 때우지 말 것.** 파일명·디렉토리 위치만 보고 "★ 재사용"을 달면 거의 틀린다. 목적 직결 자산은 **반드시 Read해서 실제 수치·메커니즘·시그니처를 본문에 박는다**:
> - 인터페이스/함수는 **시그니처**(인자·반환), 상수는 **실제 값**, 정책은 **임계치**.
> - 예(실측 교훈): "Undo/Redo patch deque" ❌ → "past/future **20단계** deque, `record`가 future 무효화, `applyPatches`로 적용" ✅ / "색·치수 상수" ❌ → "`CANVAS_GRID_SIZE=10`, `TOUCHSWITCH_CORNER_RADIUS=6`" ✅ / "기본값 팩토리" ❌ → "`DEFAULT_SIZES`(Rect 100×60 …) + `createDefaultWidget(type,pos)`" ✅
> - 재사용 목적에선 바로 이 **수치·시그니처가 가져다 쓸 때 필요한 정보**다. 추상적 역할 서술은 재사용에 거의 도움 안 됨.

`frontend-authoring-codebase` 실측: 124 src(ts/tsx) 파일 중 목적 직결 ~14개만 전수 Read, 나머지는 디렉토리 맵 1줄 — 18,079 LOC를 ~16 KB digest로 (압축비 ~5–6%, 문서 0.3%보다 높지만 코드는 정보 밀도가 높아 정상).

## digest.md 본문 구성 (문서와 다른 섹션)

```markdown
# <제목> — 코드베이스 다이제스트

> 목적: <한 줄 목적>. (이 인덱스가 무엇을 빠르게 찾기 위한 것인지)

## 개요
패키지 정체성(manifest의 name/version)·핵심 책임·데이터 모델 단일소스 (2-3문단)

## 재사용 자산 빠른 표 (목적=재사용일 때 강력 권장)
| 가져올 것 | 위치 | 재사용 방법 / 주의 |
| <자산> | `src/...` | <어떻게 import·호출하나 + ★주의(강결합/제약)> |

## 디렉토리 맵 (<src>, N 파일)
| 경로 | 역할 | <목적 컬럼: 재사용 ★/△/전용> |

## 데이터 모델 — 단일 소스
스키마/타입 정의를 압축 표기 (파일 경로 명시)

## 핵심 서브시스템
목적과 직결된 시스템(상태/통신/렌더/IO 등)을 인터페이스 시그니처 + 함정 포함

## 아키텍처 규칙
프로젝트 CLAUDE.md/관례에서 추출한 불변식 (지키지 않으면 깨지는 것들)

## 함정 / 재발 이슈
재발 2회 이상이거나 비자명한 제약

## 빌드 / 게이트
scripts, 통과 기준(typecheck/lint/test/e2e), 커버리지 임계

## 테스트 자산
재사용 가능한 테스트 패턴·셀렉터·헬퍼 위치

## 사용 가이드 (핀포인트)
세부 필요 시 직접 Read할 파일:line 목록
```

프론트매터(문서 포맷과 공통 + 코드 전용):
```yaml
format: codebase
source: <디렉토리 절대경로>
loc: <int>
files: <src 수> (src), <test 수> tests
version: git <short-sha> (<branch>[, dirty])
language: <ko-KR / 주 언어>
extractor: claude-read
purpose: <확정한 추출 목적 1줄>
stack: <한 줄 요약>
```

## index.md (심볼/파일 → 위치)

문서의 "섹션 → 페이지" 대신 **"심볼 → 파일"**. 카테고리별 표:

```markdown
# <레포> 코드베이스 — 파일 → 위치 인덱스
> 다이제스트로 부족할 때 아래 경로를 직접 Read. 모든 경로는 `<src>/` 기준.

## 타입 / 스키마
| 심볼 | 파일 |
| ProjectSchema, WidgetSchema | `src/types/project.ts` |
...
```

행 단위로 `★`(목적 직결) 표시를 달면 검색 효율이 오른다. `:line` 포인터는 자주 바뀌므로 **비자명한 핵심 라인만** 명시(예: `migrateTouchSwitch line 99`).

## metadata.json (코드베이스 전용 필드)

부록 A 공통 필드에 더해:
```json
{
  "format": "codebase",
  "source": "<디렉토리 절대경로>",
  "extractor": "claude-read",
  "purpose": "<확정한 추출 목적>",
  "loc": 18079,
  "src_files": 124,
  "test_files": 66,
  "stack": { "react": "^19", "...": "..." },
  "version": "git 85d12c8 (feat/runtime-viewer, dirty)",
  "sampling_strategy": "<목적>-focused: <전수 읽은 파일 목록> 전수 + 나머지 맵핑만",
  "<purpose>_targets": [ "src/...", "..." ],
  "<purpose>_caveats": [ "강결합/제약/함정을 한 줄씩", "..." ]
}
```

- `sha256`/`pages`/`publication_date` 같은 문서 전용 필드는 생략하거나 `null`.
- `version`은 doc 버전 대신 **git ref + 브랜치**. 워킹트리가 dirty면 `(dirty)` 표기.
- 목적별 배열은 자유 키(`reuse_targets`/`reuse_caveats`, `refactor_targets`, `schema_gaps` 등)로 — 갱신/검색 시 바로 쓰인다. `*_caveats`(강결합·제약·함정)는 재사용·리팩토링 목적에서 특히 유용.

## --update (코드베이스 갱신)

문서는 sha256 단일 해시지만 코드베이스는 디렉토리다:
- 비교 기준: 저장된 `version`(git ref)과 현재 `git rev-parse HEAD`
- 같으면 "변경 없음" 안내 후 종료
- 다르면 `git diff --stat <old>..<HEAD>`로 변경 디렉토리 식별 → **변경된 디렉토리 섹션만** 재요약, 나머지 보존
- git 레포가 아니면 디렉토리 mtime/파일 목록 diff로 폴백

## 핀포인트 (활용 시)

코드베이스 다이제스트로 부족하면:
- `index.md`에서 심볼 → 파일 경로 확인 → `Read` 해당 파일
- 심볼 위치를 모르면 `Grep`(정의/사용처) → `Glob`(파일 패턴)
- PDF MCP 불필요 — 표준 코드 도구만 사용

## 흔한 함정

| 함정 | 해결 |
|------|------|
| 모든 파일을 읽으려 함 | 목적 직결 핵심만 전수, 나머지 디렉토리 맵 1줄 |
| 목적 없이 범용 요약 | 인제스트 시작에 목적 1줄 확정 — sampling_strategy/주석 컬럼/섹션 구성이 거기서 나옴 |
| **목적 직결 파일을 안 읽고 ★ 표시** | 우선순위 1 파일은 반드시 Read — 추론으로 "재사용 ★" 달면 거의 틀림 |
| **추상적 역할만 서술** | 실제 수치·시그니처·임계치를 박는다 (deque 20단계, `GRID=10`, `fn(type,pos)`) — 재사용 시 그게 필요한 정보 |
| **검증 안 된 추측** ("패키지명 추정") | manifest(package.json 등)에서 name/version 확정 |
| `:line` 포인터 남발 | 라인은 자주 바뀜 — 비자명한 핵심만, 나머지는 심볼명으로 |
| node_modules/.git/빌드산출물 포함 | `find`에서 제외, `.gitignore` 존중 |
| 버전을 doc 버전으로 기록 | git ref + 브랜치(+dirty)로 — --update 비교 기준 |
