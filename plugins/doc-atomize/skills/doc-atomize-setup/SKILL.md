---
name: doc-atomize-setup
description: "doc-atomize 플러그인 사용 전 환경을 1회 초기화하는 셋업 스킬. ① python3 가용성 확인(MCP·외부 패키지 불필요) ② .claude/atomized/ 디렉토리(project 또는 global) 생성 ③ INDEX.md 카탈로그 헤더 작성 ④ CLAUDE.md에 원자 분할 문서 사용 규칙 마커 블록 주입 ⑤ 쓰기 권한·구조 검증 ⑥ 상태 리포트. 에이전트가 없어 설치 단계도 없다. idempotent — 여러 번 실행해도 안전하며 누락분만 보충하고 기존 콘텐츠는 보존. 사용자가 'doc-atomize 셋업', '문서 원자화 설정', '/doc-atomize-setup', 'doc-atomize 환경 초기화' 등을 요청하거나, doc-atomize 첫 사용 직전에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# doc-atomize 환경 셋업

`doc-atomize`를 처음 쓰기 전에 환경을 1회 초기화한다. **idempotent**: 여러 번 실행해도 안전하며, 이미 있는 항목은 건드리지 않고 누락된 것만 보충한다.

> **MCP·에이전트 불필요**: 분할기는 Python 표준 라이브러리만 쓰고, 의미 큐레이션은 메인 컨텍스트가 처리한다. `manual-digest`의 PDF MCP 등록이나 `pcb-design-digest`의 에이전트 설치에 해당하는 단계가 없다.

## 핵심 원칙

- **사용자 콘텐츠 보존** — 기존 CLAUDE.md / INDEX.md를 덮어쓰지 않는다. 마커 블록(`<!-- doc-atomize:start --> … <!-- doc-atomize:end -->`) 사이만 갱신.
- **사용자 동의 우선** — 변경 예정 항목을 먼저 출력하고 확인받는다. `--dry-run`으로 미리 검토 가능.
- **백업** — CLAUDE.md 수정 전 `CLAUDE.md.bak.<timestamp>` 백업.
- **부분 실패 안전** — 한 단계가 실패해도 다른 단계 결과는 유지된다.

## 옵션

| 옵션 | 동작 |
|------|------|
| `--scope project\|global\|both` | 초기화 스코프 (기본: `project`) |
| `--repair` | 마커가 온전(start+end)하면 블록 재작성, 전체 누락이면 재주입. end 마커만 유실된 비대칭 손상은 자동복구하지 않고 수동 확인 안내 |
| `--dry-run` | 실제 변경 없이 무엇을 할지만 출력 |

## 절차

### 1. 타겟 경로 확인

사용자에게 문서를 다룰 **프로젝트 디렉토리 절대경로**를 질문해 `TARGET_PROJECT`에 넣는다.
⚠️ **`$(pwd)`로 폴백하지 마라** — 셋업 bash는 플러그인 루트에서 도는 경우가 많아, 산출물이 사용자 프로젝트가 아니라 플러그인 폴더에 잘못 설치된다.

```bash
echo "[1/5] 타겟 경로 확인"
case "${SCOPE:-project}" in project|global|both) ;; *) echo "  ERROR: 알 수 없는 scope '$SCOPE' (project|global|both)"; exit 1 ;; esac
if [ "$DRY_RUN" != "true" ] && [ -z "$TARGET_PROJECT" ] && [ "${SCOPE:-project}" != "global" ]; then
    echo "  ERROR: 프로젝트 절대경로를 TARGET_PROJECT에 지정하세요 (예: TARGET_PROJECT=/path/to/project)."; exit 1
fi
[ "$DRY_RUN" = "true" ] && [ -z "$TARGET_PROJECT" ] && TARGET_PROJECT="<프로젝트경로>"
echo "  Project scope: ${TARGET_PROJECT}/.claude/atomized/"
echo "  Global scope : $HOME/.claude/atomized/"
echo "  스코프: ${SCOPE:-project}"
```

### 2. python3 가용성 확인

```bash
echo "[2/5] python3 확인"
if python3 -c "import sys; print(sys.version.split()[0])" 2>/dev/null; then
    echo "  OK — 표준 라이브러리만 사용하므로 추가 설치 없음"
elif python -c "import sys; print(sys.version.split()[0])" 2>/dev/null; then
    echo "  ⚠️ python3 없음 / python 사용 가능 — 분할 시 'python' 또는 'py -3'으로 호출"
else
    echo "  ⚠️ Python 미검출. Windows에서는 python3가 MS Store alias로 exit 49가 날 수 있음 → 'py -3' 확인"
fi
```

Python 3.8 이상이면 충분하다.

### 3. atomized 디렉토리 초기화

`--scope`에 따라 한 곳 또는 양쪽. INDEX.md 헤더는 없을 때만 작성한다:

```bash
init_atomized_dir() {
    local DIR="$1"; local LABEL="$2"
    case "$DIR" in ""|/.claude/*) echo "  ⚠️ $LABEL: 잘못된 대상 경로 '$DIR' (TARGET_PROJECT 미설정?) — 중단"; return 1 ;; esac
    [ -d "$DIR" ] && echo "  $LABEL: 디렉토리 이미 존재" || { [ "$DRY_RUN" = "true" ] && echo "  (dry-run) mkdir -p $DIR" || { mkdir -p "$DIR"; echo "  $LABEL: 디렉토리 생성"; }; }
    if [ "$DRY_RUN" != "true" ]; then
        if touch "$DIR/.write-test" 2>/dev/null; then rm -f "$DIR/.write-test"; else echo "  ⚠️  $LABEL: 쓰기 권한 없음 — 권한 확인 또는 --scope 변경 필요"; return 1; fi
    fi
    if [ "$DRY_RUN" != "true" ] && [ ! -f "$DIR/INDEX.md" ]; then
        cat > "$DIR/INDEX.md" <<'EOF'
# Atomized Documents

> doc-atomize 플러그인이 관리하는 원자 분할 문서 카탈로그. Claude는 등록 문서 관련 질문을 받으면
> **먼저 이 파일을 확인**하고, 해당 문서의 `<doc-id>.index.md`를 진입점으로 사용한다.

## 등록된 문서

| id | 제목 | 원본 | 줄수 | 조각 | scope |
|----|------|------|------|------|-------|
| _(아직 등록된 문서가 없습니다. `/doc-atomize <file.md>`로 첫 문서를 등록하세요.)_ | | | | | |

## 참조 규칙

1. 등록 문서 관련 질문 시 → 본 INDEX.md를 먼저 확인
2. `<doc-id>/<doc-id>.index.md` 진입 → 라우팅 힌트·키워드 역색인·목차로 후보 조각 특정
3. `parts/*.md`만 Read — **원본 전체 Read 금지**. 미스 시 `Grep parts/` → 적중 파일만 Read
4. 답변에 출처(조각 id·원본 라인범위) 명시
5. 미등록 대형 .md(300줄 이상)를 반복 참조하면 `/doc-atomize <path>` 등록 제안

조각 본문은 원본 그대로다(요약 아님) — 원문 인용에 그대로 쓸 수 있다.
EOF
        echo "    INDEX.md 헤더 작성"
    elif [ "$DRY_RUN" = "true" ] && [ ! -f "$DIR/INDEX.md" ]; then
        echo "    (dry-run) INDEX.md 헤더 작성 예정"
    else
        echo "    INDEX.md 이미 존재 — 보존"
    fi
}

echo "[3/5] atomized 디렉토리 초기화"
case "${SCOPE:-project}" in
    project) init_atomized_dir "$TARGET_PROJECT/.claude/atomized" "Project" ;;
    global)  init_atomized_dir "$HOME/.claude/atomized" "Global" ;;
    both)    init_atomized_dir "$TARGET_PROJECT/.claude/atomized" "Project"; init_atomized_dir "$HOME/.claude/atomized" "Global" ;;
esac
```

### 4. CLAUDE.md 마커 블록 주입

project scope면 `$TARGET_PROJECT/CLAUDE.md`, global scope면 `$HOME/.claude/CLAUDE.md`가 대상이다.

절차:
1. 대상 CLAUDE.md 존재 확인 (없으면 생성)
2. `<!-- doc-atomize:start -->` 존재 여부 확인
   - 있음 + `--repair` 아님 → 보존하고 건너뜀
   - 있음 + `--repair` → start~end 사이만 재작성
   - 없음 → 파일 끝에 블록 추가
   - start만 있고 end가 없음(비대칭 손상) → **자동 수정하지 않고** 수동 확인 안내
3. 수정 전 `CLAUDE.md.bak.$(date +%Y%m%d-%H%M%S)` 백업

주입 내용은 `../doc-atomize/references/retrieval-guide.md`의 "CLAUDE.md 마커 블록" 절 원문을 그대로 쓴다. 마커 밖 콘텐츠는 절대 건드리지 않는다.

### 5. 검증 + 리포트

```bash
echo "[5/5] 검증"
for D in "$TARGET_PROJECT/.claude/atomized" "$HOME/.claude/atomized"; do
    [ -d "$D" ] && echo "  ✓ $D ($([ -f "$D/INDEX.md" ] && echo "INDEX.md 있음" || echo "INDEX.md 없음"))"
done
grep -l "doc-atomize:start" "$TARGET_PROJECT/CLAUDE.md" 2>/dev/null && echo "  ✓ CLAUDE.md 마커 주입됨"
```

리포트에 다음을 포함한다:
- 생성/보존된 디렉토리와 INDEX.md
- CLAUDE.md 마커 상태(주입/보존/복구/수동확인필요)와 백업 파일 경로
- Python 상태
- **다음 단계 안내**: `/doc-atomize <큰 .md 경로>`로 첫 문서를 분할

## 셋업 이후

```
/doc-atomize docs/BIG_SPEC.md            ← 분할 + 인덱스 생성
/doc-atomize --list                      ← 등록 문서 목록
/doc-atomize --update big-spec           ← 원본 변경분 반영
/doc-atomize --verify big-spec           ← 무손실 재검증
```

> **세션 재시작 불필요**: MCP·에이전트를 등록하지 않으므로 셋업 직후 바로 사용할 수 있다.
