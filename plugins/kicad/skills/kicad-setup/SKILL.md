---
name: kicad-setup
description: "KiCad 회로도 에이전트와 CLAUDE.md를 타겟 프로젝트에 설치합니다. 'KiCad 설정', 'kicad 설치', 'KiCad 에이전트 설치', '회로도 셋업' 등의 요청에 자동 적용."
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# KiCad 회로도 도구 — 프로젝트 설정

이 스킬은 KiCad 회로도 에이전트(리뷰어, BOM 생성기, 설계자)와 CLAUDE.md 템플릿을 타겟 프로젝트에 설치한다.

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

설치된 파일:
  - .claude/agents/kicad-schematic-reviewer.md (회로도 리뷰 에이전트)
  - .claude/agents/kicad-bom-generator.md (BOM 생성 에이전트)
  - .claude/agents/kicad-schematic-designer.md (회로도 설계 에이전트)
  - CLAUDE.md (KiCad 설정 추가)
```

$ARGUMENTS
