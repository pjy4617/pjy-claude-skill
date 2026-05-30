---
name: kicad-setup
description: "KiCad 회로도 에이전트와 CLAUDE.md를 타겟 프로젝트에 설치합니다. 'KiCad 설정', 'kicad 설치', 'KiCad 에이전트 설치', '회로도 셋업' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# KiCad 회로도 도구 — 프로젝트 설정

이 스킬은 KiCad 에이전트(리뷰어, BOM 생성기, 설계자, PCB 분석가)와 CLAUDE.md 템플릿을 타겟 프로젝트에 설치한다.
선택적으로 PCB 정밀 분석용 **Seeed kicad-mcp-server**도 등록할 수 있다(`--with-mcp`).

## 옵션

| 옵션 | 동작 |
|------|------|
| (기본) | 에이전트 4종 + CLAUDE.md 설치 |
| `--with-mcp` | 위 + Seeed kicad-mcp-server 등록 절차 안내(단계 6) |

## 설치 절차

### 1. 타겟 프로젝트 경로 확인

사용자에게 KiCad 프로젝트가 있는 디렉토리 경로를 질문한다:

```
질문: "KiCad 프로젝트 경로를 알려주세요. (예: /home/user/project/hw/kicad)"
```

경로에 `.kicad_sch` 또는 `.kicad_pro` 파일이 존재하는지 확인한다.

### 2. 에이전트 설치

에이전트 파일을 타겟 프로젝트의 `.claude/agents/`로 복사한다:

```bash
# 타겟 프로젝트의 .claude/agents/ 디렉토리 생성
mkdir -p "$TARGET_PROJECT/.claude/agents"

# 에이전트 복사
cp agents/kicad-schematic-reviewer.md "$TARGET_PROJECT/.claude/agents/"
cp agents/kicad-bom-generator.md "$TARGET_PROJECT/.claude/agents/"
cp agents/kicad-schematic-designer.md "$TARGET_PROJECT/.claude/agents/"
cp agents/kicad-pcb-analyzer.md "$TARGET_PROJECT/.claude/agents/"
```

### 3. CLAUDE.md 설치

`claude-md/CLAUDE.md` 템플릿을 타겟 프로젝트에 복사하되, 기존 CLAUDE.md가 있으면 내용을 추가한다:

```bash
if [ -f "$TARGET_PROJECT/CLAUDE.md" ]; then
    echo "" >> "$TARGET_PROJECT/CLAUDE.md"
    cat claude-md/CLAUDE.md >> "$TARGET_PROJECT/CLAUDE.md"
    echo "기존 CLAUDE.md에 KiCad 설정을 추가했습니다."
else
    cp claude-md/CLAUDE.md "$TARGET_PROJECT/CLAUDE.md"
    echo "CLAUDE.md를 새로 생성했습니다."
fi
```

### 4. 설치 확인

```bash
echo "=== 설치 결과 ==="
echo "에이전트:"
ls -la "$TARGET_PROJECT/.claude/agents/"kicad-*.md 2>/dev/null || echo "  (설치 실패)"
echo "  (기대: reviewer, bom-generator, schematic-designer, pcb-analyzer = 4개)"
echo ""
echo "CLAUDE.md:"
grep -l "kicad" "$TARGET_PROJECT/CLAUDE.md" 2>/dev/null && echo "  OK" || echo "  (미포함)"
```

### 5. 안내

설치 완료 후 사용자에게 안내:

```
설치가 완료되었습니다!

사용 방법:
  1. 타겟 프로젝트 디렉토리에서 Claude Code를 실행하세요
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
  - CLAUDE.md (KiCad 설정 추가)

PCB 신호/전원 무결성(SI/PI)까지 정밀 분석하려면:
  /kicad-setup --with-mcp  (Seeed kicad-mcp-server 등록 안내)
```

### 6. (선택) Seeed kicad-mcp-server 등록 — `--with-mcp`

`kicad-analyze` 스킬의 SI/PI·정밀 트랙 분석은 Seeed MCP(pcbnew 기반)가 있어야 정확하다.
`--with-mcp` 옵션일 때만 아래를 진행하고, 기본 설치에서는 안내만 한다.

> **전제 확인 먼저**: 로컬에 KiCad 9.0+ 설치 + `kicad-cli`가 PATH에 있어야 한다. 없으면 등록을 건너뛰고
> "kicad-analyze는 kicad-cli/직접 파싱 폴백으로 동작하나 SI/PI는 제한됨"을 안내한다.

```bash
# 0) 전제 확인
kicad-cli version 2>/dev/null || { echo "KiCad 미설치 — MCP 등록 생략(폴백 모드로 사용 가능)"; }

# 1) 이미 등록됐는지 확인 (idempotent)
if claude mcp list 2>/dev/null | grep -qi "kicad"; then
    echo "Seeed MCP(kicad) 이미 등록됨 — 보존"
else
    echo "Seeed MCP 미등록 → 아래 절차 안내"
    echo "  git clone https://github.com/Seeed-Studio/kicad-mcp-server"
    echo "  cd kicad-mcp-server"
    echo "  <KiCad 번들 python> -m pip install fastmcp -e ."
    echo "  claude mcp add kicad -s user -- <KiCad 번들 python> -m kicad_mcp_server"
    echo "  → 등록 후 Claude Code 재시작 시 mcp__kicad__* 활성화"
fi
```

> KiCad 번들 Python 경로 예시는 `skills/kicad-analyze/references/mcp-tools.md`의 "설치/등록" 섹션 참조(OS별 경로 포함).
> **실제 `git clone`/`pip install`은 사용자 동의 후** 진행한다 — 시스템에 패키지를 설치하는 작업이므로 명령만 제시하고 사용자가 실행하도록 안내하는 것을 권장.

$ARGUMENTS
