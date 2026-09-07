---
name: kicad-setup
description: "KiCad 회로도 에이전트와 CLAUDE.md를 타겟 프로젝트에 설치합니다. 'KiCad 설정', 'kicad 설치', 'KiCad 에이전트 설치', '회로도 셋업' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# KiCad 회로도 도구 — 프로젝트 설정

이 스킬은 KiCad 에이전트(리뷰어, BOM 생성기, 설계자, PCB 분석가)와 CLAUDE.md 템플릿을 타겟 프로젝트에 설치한다.
선택적으로 PCB 정밀 분석용 **KiCAD-MCP-Server**도 등록할 수 있다(`--with-mcp`).

## 옵션

| 옵션 | 동작 |
|------|------|
| (기본) | 에이전트 4종 + CLAUDE.md 설치 |
| `--with-mcp` | 위 + KiCAD-MCP-Server 등록 절차 안내(단계 6) |

## 설치 절차

### 1. 타겟 프로젝트 루트 + 플러그인 디렉토리 확인

**(1-a) 프로젝트 루트 질문** — 설치 위치는 KiCad 파일이 있는 하위 폴더가 아니라 **Claude Code를 실행할 프로젝트 루트**다.
Claude Code는 작업 디렉토리의 `.claude/agents/`만 읽으므로, 루트가 아닌 곳에 설치하면 파일은 생겨도 에이전트가 로드되지 않는다.

```
질문: "Claude Code를 실행할 프로젝트 루트(git 루트) 경로를 알려주세요.
       (예: /home/user/project — 엔터만 누르면 현재 디렉토리)"
```

- 입력이 있으면 그 경로를, 없으면 현재 작업 디렉토리를 `TARGET_PROJECT`로 설정한다.
- git 루트인지 확인해 다르면 사용자에게 알린다: `git -C "$TARGET_PROJECT" rev-parse --show-toplevel`

**(1-b) KiCad 파일 위치는 루트 아래에서 자동 탐색** — 사용자에게 따로 묻지 않는다.

```bash
find "$TARGET_PROJECT" -maxdepth 4 \( -name "*.kicad_pro" -o -name "*.kicad_sch" \) \
     -not -path "*/node_modules/*" 2>/dev/null | head -20
```

찾지 못해도 설치는 계속한다(아직 회로도를 만들기 전일 수 있다). 찾은 경로는 단계 5 안내에 그대로 보여 준다.

**(1-c) 플러그인 디렉토리 해석** — 에이전트·CLAUDE.md 템플릿의 원본 위치다. 상대경로(`agents/…`)는 사용자 cwd 기준이라 실패하므로 쓰지 않는다.

`${CLAUDE_SKILL_DIR}`는 셸 환경변수가 **아니다**. 스킬 본문을 로드할 때 실제 절대경로로 바뀌는 **텍스트 플레이스홀더**이며,
치환은 `${CLAUDE_SKILL_DIR}`(중괄호 포함) 형태만 인식한다. `$CLAUDE_SKILL_DIR`처럼 중괄호 없이 쓰면 치환되지 않고
셸에도 그런 변수가 없으므로 빈 문자열이 되어, `PLUGIN_DIR`이 조용히 cwd의 부모로 잘못 잡힌다. 반드시 중괄호 형태로 쓴다.

```bash
# ${CLAUDE_SKILL_DIR} = <플러그인 루트>/skills/kicad-setup — 두 단계 위가 플러그인 루트다
PLUGIN_DIR="$(cd "${CLAUDE_SKILL_DIR}/../.." 2>/dev/null && pwd)"
if [ -n "$PLUGIN_DIR" ] && [ -d "$PLUGIN_DIR/agents" ] && [ -f "$PLUGIN_DIR/claude-md/CLAUDE.md" ]; then
    echo "PLUGIN_DIR=$PLUGIN_DIR"
else
    PLUGIN_DIR=""
    echo "PLUGIN_DIR 해석 실패 — 아래 폴백 탐색으로 넘어간다"
fi
```

가드를 `agents/` 존재 하나로 두면 cwd 부모에 우연히 같은 이름의 디렉토리가 있을 때 통과해 **남의 파일을 복사**한다.
그래서 `claude-md/CLAUDE.md`까지 함께 확인한다.

**폴백 탐색** — 위 가드가 실패하면 설치된 플러그인에서 직접 찾는다. 런타임이 실제로 로드하는 경로는
`~/.claude/plugins/cache/<마켓플레이스>/kicad/<버전>/agents/` 로, `kicad`와 `agents` 사이에 **버전 디렉토리가 하나 끼어 있다**.

```bash
if [ -z "$PLUGIN_DIR" ]; then
    # 1순위: 설치 캐시. 여러 버전이 잡히면 sort -V 로 정렬해 마지막(최신 버전)을 쓴다
    CAND="$(ls -d ~/.claude/plugins/cache/*/kicad/*/agents 2>/dev/null | sort -V | tail -1)"
    # 2순위: 마켓플레이스 클론 등 다른 레이아웃까지 넓힌다
    [ -n "$CAND" ] || CAND="$(find ~/.claude/plugins -type d -path "*/kicad/*" -name agents 2>/dev/null | sort -V | tail -1)"
    [ -n "$CAND" ] && PLUGIN_DIR="$(cd "$CAND/.." && pwd)"
    if [ -n "$PLUGIN_DIR" ] && [ -f "$PLUGIN_DIR/claude-md/CLAUDE.md" ]; then
        echo "PLUGIN_DIR=$PLUGIN_DIR (폴백)"
    else
        echo "플러그인 디렉토리를 찾지 못했습니다 — 설치를 중단하고 사용자에게 알립니다."
        exit 1
    fi
fi
```

- 찾은 `agents/` 디렉토리의 **상위 한 단계**가 `PLUGIN_DIR`이다 — 캐시·클론 두 레이아웃 모두에서 같다.
- 캐시를 1순위로 두는 이유: 마켓플레이스 클론(`~/.claude/plugins/marketplaces/<마켓>/plugins/kicad`)은 리포의 특정 커밋이고,
  캐시는 사용자가 **실제로 설치한 버전**이다. 설치 버전이 뒤처져 있으면 둘의 내용이 다르다.
- `Glob` 도구로 같은 탐색을 해도 되지만(`~/.claude/plugins/cache/**/kicad/*/agents/*.md`),
  하네스가 `Glob`을 끈 환경에서는 `Glob is not available` 오류가 나므로 위 `ls`/`find` 를 기본으로 한다.

### 2. 에이전트 설치 (MCP 접두어 치환 포함)

에이전트 4종의 `tools:` 프론트매터에는 KiCAD-MCP-Server 도구가 `mcp__kicad__<도구명>` **전체 이름으로 나열**되어 있다.
이 방식이 동작함은 실측 확인됐다 — 프론트매터에 나열한 도구가 그대로 서브에이전트에 할당되고, 나열하지 않은
쓰기 계열(`save_board`·`refill_zones`·`sync_schematic_to_board` 등)은 보이지 않는다. 즉 나열이 화이트리스트로 작동해
읽기 전용 에이전트의 권한 경계가 선다. 서버 단위 와일드카드 표기는 그 경계를 무너뜨리므로 쓰지 않는다.
접두어의 `kicad` 부분은 **MCP 서버 등록명**이라 사용자 환경에 따라 다르다 — 복사할 때 실제 등록명으로 치환한다.

**(2-a) 등록명 읽기** — `claude mcp list`의 각 줄은 `<등록명>: <명령> - <상태>` 형식이다.
등록명에 콜론(`plugin:foo:bar`)이나 공백이 들어갈 수 있으므로 `: `(콜론+공백)으로 잘라 첫 필드를 쓰고,
Claude Code가 도구 이름을 만들 때와 같은 방식으로 영숫자·`_`·`-` 이외 문자는 `_`로 바꾼다.
`grep -oP`의 lookbehind/lookahead는 BSD grep 등에 없으므로 쓰지 않는다.

`claude mcp list`는 **실행한 디렉토리의 프로젝트 스코프**를 읽는다. local 스코프로 등록된 서버는 그 프로젝트에서만 보이므로,
반드시 `TARGET_PROJECT`에서 실행한다 — 여기서 필요한 것은 "타겟 프로젝트에서 보이는 등록명"이기 때문이다.

```bash
REG="$( (cd "$TARGET_PROJECT" && claude mcp list 2>/dev/null) \
       | grep -i 'kicad' \
       | head -1 \
       | awk -F': ' '{print $1}' \
       | sed 's/[^A-Za-z0-9_-]/_/g')"
echo "MCP 등록명: ${REG:-(미등록)}"
```

- 서버 이름이 아니라 실행 명령 경로에 `kicad`가 들어간 경우(`mypcb: node /opt/KiCAD-MCP-Server/dist/index.js`)에도
  같은 줄의 첫 필드인 `mypcb`가 잡히므로 결과는 맞다.
- `REG`가 비면 **미등록**이다. 그대로 복사한다 — Claude Code는 존재하지 않는 MCP 도구 이름을 `tools:`에서 무시하므로
  에이전트는 `kicad-cli`/직접 파싱 폴백으로 정상 동작한다.
- 단, "미등록"이 **다른 프로젝트에 local 스코프로 등록돼 있어서 여기서 안 보이는 것**일 수 있다. 사용자가 이미 등록했다고 하면
  `claude mcp list -s user` 또는 `~/.claude.json`의 `projects.<경로>.mcpServers`를 확인하도록 안내한다.
  여러 프로젝트에서 쓰려면 `-s user` 스코프로 등록하는 편이 낫다(단계 6의 등록 명령이 그렇게 되어 있다).

**(2-b) 복사** — `REG`가 `kicad`가 아니면 `sed`로 접두어를 치환하며 복사한다.

```bash
mkdir -p "$TARGET_PROJECT/.claude/agents"

for A in kicad-schematic-reviewer kicad-bom-generator kicad-schematic-designer kicad-pcb-analyzer; do
    SRC="$PLUGIN_DIR/agents/$A.md"
    DST="$TARGET_PROJECT/.claude/agents/$A.md"
    if [ -n "$REG" ] && [ "$REG" != "kicad" ]; then
        sed "s/mcp__kicad__/mcp__${REG}__/g" "$SRC" > "$DST"
        echo "복사(접두어 → mcp__${REG}__): $A.md"
    else
        cp "$SRC" "$DST"
        echo "복사(접두어 그대로): $A.md"
    fi
done
```

이미 같은 이름의 파일이 있으면 덮어쓰기 전에 사용자에게 확인한다.

**나중에 MCP를 등록하거나 등록명을 바꾸면** `/kicad-setup`을 다시 실행한다 — 복사 시점의 등록명이 파일에 박히기 때문이다.

### 3. CLAUDE.md 설치

`PLUGIN_DIR/claude-md/CLAUDE.md` 템플릿을 **마커 블록**으로 감싸 병합한다.
마커가 있으면 블록 내부만 교체하고, 없으면 파일 끝에 추가한다 — 여러 번 실행해도 중복되지 않는다(idempotent).

```bash
CLAUDE_MD="$TARGET_PROJECT/CLAUDE.md"
BEGIN="<!-- kicad-plugin:begin -->"
END="<!-- kicad-plugin:end -->"

BLOCK="$(printf '%s\n' "$BEGIN"; cat "$PLUGIN_DIR/claude-md/CLAUDE.md"; printf '%s\n' "$END")"

if [ ! -f "$CLAUDE_MD" ]; then
    printf '%s\n' "$BLOCK" > "$CLAUDE_MD"
    echo "CLAUDE.md를 새로 생성했습니다(마커 블록 포함)."
elif grep -qF "$BEGIN" "$CLAUDE_MD"; then
    cp "$CLAUDE_MD" "$CLAUDE_MD.bak.$(date +%Y%m%d-%H%M%S)"
    # 마커 블록 내부만 교체 — 블록 밖 사용자 내용은 보존
    awk -v b="$BEGIN" -v e="$END" -v f=/dev/stdin '
        $0 == b { print; while ((getline line < f) > 0) print line; skip=1; next }
        $0 == e { skip=0; print; next }
        !skip   { print }
    ' "$CLAUDE_MD" < "$PLUGIN_DIR/claude-md/CLAUDE.md" > "$CLAUDE_MD.tmp" \
      && mv "$CLAUDE_MD.tmp" "$CLAUDE_MD"
    echo "기존 CLAUDE.md의 kicad-plugin 마커 블록을 최신 내용으로 교체했습니다."
else
    cp "$CLAUDE_MD" "$CLAUDE_MD.bak.$(date +%Y%m%d-%H%M%S)"
    printf '\n%s\n' "$BLOCK" >> "$CLAUDE_MD"
    echo "기존 CLAUDE.md 끝에 kicad-plugin 마커 블록을 추가했습니다."
fi
```

주의: 마커 블록 밖의 사용자 내용은 절대 수정하지 않는다. 교체 전 백업(`.bak.<날짜>`)을 남긴다.

### 4. 설치 확인

```bash
echo "=== 설치 결과 ==="
echo "프로젝트 루트: $TARGET_PROJECT"
echo "에이전트:"
ls -la "$TARGET_PROJECT/.claude/agents/"kicad-*.md 2>/dev/null || echo "  (설치 실패)"
echo "  (기대: reviewer, bom-generator, schematic-designer, pcb-analyzer = 4개)"
echo ""
echo "MCP 도구 접두어 (에이전트 4개 중 등록명 ${REG:-(미등록)}과 일치하는 파일 수):"
grep -lF "mcp__${REG:-kicad}__" "$TARGET_PROJECT/.claude/agents/"kicad-*.md 2>/dev/null | wc -l
echo "  (기대: MCP 등록 시 4 / 미등록이면 mcp__kicad__ 그대로 4)"
echo ""
echo "CLAUDE.md:"
grep -qF "<!-- kicad-plugin:begin -->" "$TARGET_PROJECT/CLAUDE.md" 2>/dev/null \
  && echo "  OK (마커 블록 존재)" || echo "  (미포함)"
```

**중요 1**: 에이전트는 Claude Code의 **작업 디렉토리** 기준으로 로드된다.
설치한 루트에서 실행해야 한다 — `cd $TARGET_PROJECT && claude`.
다른 디렉토리에서 실행하면 위 `ls`가 통과해도 에이전트는 보이지 않는다.

**중요 2**: `.claude/agents/`는 **세션 시작 시점에 한 번 읽힌다.** 그래서 `/kicad-setup`을 돌린 **바로 그 세션에서는
방금 설치한 에이전트를 호출할 수 없다**(`Agent type 'kicad-pcb-analyzer' not found`). Claude Code를 다시 띄워야 보인다.
설치 직후 확인은 위 `ls` 결과로 하고, 실제 호출은 재시작 후에 한다.

### 5. 안내

설치 완료 후 사용자에게 안내:

```
설치가 완료되었습니다!

사용 방법:
  1. 설치한 프로젝트 루트에서 Claude Code를 실행하세요 — cd $TARGET_PROJECT && claude
     (다른 디렉토리에서 실행하면 에이전트가 로드되지 않습니다)
     이미 Claude Code가 떠 있었다면 재시작하세요 — 에이전트 목록은 세션 시작 때 한 번만 읽습니다
  2. 다음과 같이 요청하세요:
     - "회로도 리뷰해줘" → kicad-review 스킬
     - "BOM 만들어줘" → kicad-review 스킬 (BOM 단계)
     - "이 PRD 기반으로 회로도 만들어줘" → kicad-design 스킬
     - "PCB 분석해줘 / DRC 돌려줘 / 넷 추적해줘" → kicad-analyze 스킬

설치된 파일:
  - .claude/agents/kicad-schematic-reviewer.md (회로도 리뷰 에이전트)
  - .claude/agents/kicad-bom-generator.md (BOM 생성 에이전트)
  - .claude/agents/kicad-schematic-designer.md (회로도 설계 에이전트)
  - .claude/agents/kicad-pcb-analyzer.md (회로/PCB 분석 에이전트)
  - CLAUDE.md (kicad-plugin 마커 블록 추가)

PCB 트랙·존 기하 기반 정밀 분석(SI/PI 판정 포함)까지 하려면:
  /kicad-setup --with-mcp  (KiCAD-MCP-Server 등록 안내)
```

**스모크 테스트(선택)** — 로컬에 KiCad 데모 프로젝트가 있으면 ERC를 한 번 돌려 환경이 맞는지 보여 준다.
데모가 없으면 이 단계는 생략한다(설치 결과에는 영향이 없다).

데모 폴더 안의 `.kicad_sch`를 알파벳순으로 집으면 **하위 시트**가 잡혀, 상위 시트가 없다는 계층 라벨 오류가 수백 건 쏟아진다
(실측: `cm5_minima`에서 하위 시트 `CM5.kicad_sch` 는 176건, 루트 시트 `CM5_MINIMA_3.kicad_sch` 는 1건).
`.kicad_pro`와 이름이 같은 파일이 **루트 시트**이므로 그쪽을 먼저 고른다.

```bash
DEMO="$(ls -d /usr/share/kicad/demos/*/ 2>/dev/null | head -1)"
DEMO_PRO="$(ls "$DEMO"*.kicad_pro 2>/dev/null | head -1)"
DEMO_SCH="${DEMO_PRO%.kicad_pro}.kicad_sch"          # 루트 시트 = .kicad_pro 와 같은 이름
[ -n "$DEMO_PRO" ] && [ -f "$DEMO_SCH" ] || DEMO_SCH="$(ls "$DEMO"*.kicad_sch 2>/dev/null | head -1)"
if [ -n "$DEMO_SCH" ] && command -v kicad-cli >/dev/null 2>&1; then
    echo "스모크 테스트: kicad-cli sch erc $DEMO_SCH"
    kicad-cli sch erc --severity-all -o /dev/stdout "$DEMO_SCH" 2>&1 | head -20
    echo "→ 위 리포트가 나오면 kicad-cli 환경이 정상입니다(위반 건수 자체는 데모 내용이라 무관)."
else
    echo "스모크 테스트 생략 — /usr/share/kicad/demos 아래 데모 프로젝트 또는 kicad-cli 없음"
fi
```

### 6. (선택) KiCAD-MCP-Server 등록 — `--with-mcp`

`kicad-analyze` 스킬의 트랙·존 기하 분석(SI/PI 판정의 입력)은 MCP(pcbnew 기반)가 있어야 정확하다.
`--with-mcp` 옵션일 때만 아래를 진행하고, 기본 설치에서는 안내만 한다.

> **전제 확인 먼저**: 로컬에 KiCad 9.0+ 설치(`kicad-cli` + `pcbnew` 파이썬 모듈 포함) + **Node.js 18+**가 필요하다.
> **`kicad-cli`가 없으면 MCP 등록 안내를 진행하지 않는다.** MCP의 `run_erc`/`run_drc`가 내부에서 kicad-cli를 부르므로,
> 없는 상태로 등록하면 "등록 성공"만 보이고 ERC/DRC는 전부 실패한다. 이 경우 "KiCad 설치(kicad-cli 포함)가 먼저"로 안내를 끝낸다.

```bash
# 0) 전제 확인 — kicad-cli 부재는 중단 조건이다
if ! kicad-cli version >/dev/null 2>&1; then
    echo "kicad-cli 없음 — MCP 등록 안내를 중단합니다."
    echo "  KiCad 설치(kicad-cli 포함)가 먼저입니다. 설치 후 /kicad-setup --with-mcp 를 다시 실행하세요."
    echo "  그 전까지 kicad-analyze 는 직접 파싱 폴백으로만 동작하며 트랙·존 기하 분석은 제한됩니다."
    exit 0
fi
python3 -c "import pcbnew; print('pcbnew', pcbnew.GetBuildVersion())" 2>/dev/null \
  || echo "pcbnew 모듈 없음 — 아래 venv(--system-site-packages) 절차 또는 KICAD_PYTHON 지정 필요(references/mcp-tools.md 참조)"
node --version 2>/dev/null || echo "Node.js 없음 — 18+ 필요"

# 1) 이미 등록됐는지 확인 (idempotent)
#    claude mcp list 는 실행 디렉토리의 프로젝트 스코프를 읽는다 — TARGET_PROJECT 에서 실행해야
#    "이 프로젝트에서 실제로 보이는가"를 판정한다. cwd 를 고정하지 않으면 이미 등록된 서버를
#    미등록으로 오판해 중복 등록을 안내하게 된다.
if (cd "$TARGET_PROJECT" && claude mcp list 2>/dev/null) | grep -qi "kicad"; then
    echo "MCP(kicad) 이미 등록됨 — 보존"
else
    echo "KiCAD-MCP-Server 미등록 → 아래 절차 안내"
    echo "  git clone https://github.com/mixelpixx/KiCAD-MCP-Server.git"
    echo "  cd KiCAD-MCP-Server"
    echo "  npm install && npm run build      # 클라이언트가 실행하는 것은 dist/ — 빌드 필수"
    echo "  python3 -m venv --system-site-packages venv && ./venv/bin/pip install -r requirements.txt"
    echo "  claude mcp add kicad -s user -e KICAD_AUTO_LAUNCH=false -e KICAD_BACKEND=swig -- \\"
    echo "    node \$(pwd)/dist/index.js"
    echo "  → 등록 후 /mcp 에서 kicad 를 reconnect 하면 즉시 활성화(세션 재시작보다 빠르다)"
    echo "  → 확인 1: claude mcp list | grep kicad  (Connected 표시)"
    echo "  → 확인 2: mcp__kicad__get_backend_state 호출 — backend 가 돌아오면 파이썬 브리지·pcbnew 까지 정상"
    echo "  → 첫 get_backend_state 는 pcbnew(wxApp) 초기화로 최대 1분 걸린다 — 침묵은 정상이며 기다린다"
    echo "  → 등록을 마쳤으면 /kicad-setup 을 한 번 더 실행한다 — 설치된 에이전트의 mcp__kicad__ 접두어를"
    echo "    실제 등록명으로 다시 치환해야 MCP 도구가 에이전트에 보인다(단계 2)"
    echo "  ※ 다른 프로젝트에 local 스코프로 이미 등록돼 있으면 여기서는 미등록으로 보인다."
    echo "    중복 등록 전에 claude mcp list -s user 또는 ~/.claude.json 의 projects.<경로>.mcpServers 를 확인한다."
fi
```

> **`pip3 install -r requirements.txt`를 쓰지 않는 이유**: Ubuntu 24.04·Debian 12 이상의 시스템 pip는
> PEP 668(`externally-managed-environment`)로 설치를 거부한다. 그렇다고 평범한 venv를 만들면 이번에는
> 시스템에 설치된 `pcbnew`가 보이지 않는다. `--system-site-packages`가 두 문제를 동시에 푼다.
> 서버는 저장소의 `venv/`(그다음 `.venv/`)를 파이썬 1순위로 잡으므로 이 방식이면 `KICAD_PYTHON`을 따로 지정할 필요가 없다.

> **`npm run build`를 빠뜨리면 등록해도 뜨지 않는다** — 클라이언트가 실행하는 것은 `src/`가 아니라 컴파일 결과인 `dist/`다.
> **kicad-cli도 필수다** — MCP의 `run_erc`/`run_drc`가 내부에서 kicad-cli를 부르므로, 없으면 MCP를 등록해도 ERC/DRC는 실패한다.
> 그래서 위 0단계는 kicad-cli가 없으면 안내 자체를 중단한다.
> Windows/macOS처럼 `pcbnew`가 시스템 파이썬에 없어 `--system-site-packages` venv로도 잡히지 않는 환경은
> `KICAD_PYTHON`으로 KiCad 번들 파이썬을 지정해야 한다.
> Windows의 `setup-windows.ps1`은 전제 점검·빌드·경로 감지까지만 하고 **Claude Code 등록은 해 주지 않는다** — 스크립트가 출력한
> `KICAD_PYTHON`/`PYTHONPATH` 값을 위 `claude mcp add -e ...`에 옮겨 적는다. macOS는 `setup-macos.sh --verify`가 등록 힌트를 출력한다.
> OS별 경로와 환경변수는 `skills/kicad-analyze/references/mcp-tools.md`의 "설치 / 등록" 섹션 참조.
> **실제 `git clone`/`npm install`/venv 생성 및 `pip install`은 사용자 동의 후** 진행한다 — 시스템에 패키지를 설치하는 작업이므로 명령만 제시하고 사용자가 실행하도록 안내하는 것을 권장.

$ARGUMENTS
