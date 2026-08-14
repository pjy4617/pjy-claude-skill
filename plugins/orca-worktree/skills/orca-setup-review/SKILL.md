---
name: orca-setup-review
description: "기존 orca.yaml 워크트리 훅을 읽기 전용으로 진단한다. 구조(인식 키 4종·들여쓰기·블록 스칼라), 실행 안전(주입된 set -e 미해제·파괴적 명령·-L 없는 링크 해제·시크릿 하드코딩), 예산(120초 초과 위험), 이식성(호스트 절대경로·Windows), 멱등성, 그리고 레포 특성 대비 커버리지 갭을 CRITICAL/MAJOR/MINOR/INFO 4등급으로 파일:라인 근거와 함께 리포트한다. 코드를 수정하지 않는다. 사용자가 'orca.yaml 검토', 'Orca 훅 리뷰', 'setup 스크립트 점검', '워크트리 훅 진단', 'orca 훅이 안 돈다', 'setup 훅 왜 중간에 멈추지', '/orca-setup-review' 등을 요청할 때 자동 적용. 훅을 새로 쓰거나 고치는 작업은 orca-setup-build, Orca 쪽 레포 등록·설정 점검은 orca-project-config 담당."
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
---

# orca-setup-review — Orca 워크트리 훅 진단

`orca.yaml`의 워크트리 훅을 **읽기 전용으로** 검토한다. 고치지 않는다 — 수정은 `/orca-setup-build`가 한다.

## 사용 시기

- "훅이 안 돈다" / "앞부분만 실행되고 끝난다" / "팀원 호스트에서만 실패한다"
- 남이 쓴 `orca.yaml`을 물려받았을 때
- 훅을 커밋하기 전 마지막 확인 (작성과 검토는 분리된 패스여야 한다)
- 정기 점검 — 레포는 변하는데 훅은 그대로다

## 워크플로 (5단계)

### 1. 대상 수집

```bash
R="$(git rev-parse --show-toplevel)"
ls "$R/orca.yaml" "$R/orca.yml" 2>/dev/null
grep -nE '(bash|sh|source|\.)\s+\S*orca[-_]setup\S*\.sh' "$R/orca.yaml"   # 분리 스크립트 위임
```

훅이 외부 스크립트를 호출하면 **그 스크립트도 검토 대상**이다. `orca.yaml`만 보고 통과시키면 실제 로직을 전혀 안 본 셈이 된다.

### 2. 정적 검사

```bash
C="${CLAUDE_SKILL_DIR}/../orca-setup-build/assets/check_orca_yaml.py"
python3 "$C" check "$R/orca.yaml"
```

구조(미인식 키·탭 들여쓰기·빈 블록·중복 키), 안티패턴(파괴적 명령·시크릿·무거운 단계·호스트 절대경로), `bash -n` 문법을 한 번에 본다. 분리 스크립트는 따로 확인한다:

```bash
bash -n "$R/tools/orca-setup.sh"
```

### 3. 사람이 읽어야 하는 항목

스크립트가 잡지 못하는 것들이다. `references/review-checklist.md`의 6개 카테고리를 훑는다:

| 카테고리 | 핵심 질문 |
|---|---|
| A. 구조·인식 | 인식되는 키만 쓰는가? 파싱이 깨질 지점은? |
| B. 실행 안전 | `set +e`가 있는가? 워크트리 밖을 건드리는가? archive가 원본을 지울 수 있는가? |
| C. 예산 | 120초 안에 끝나는가? 콜드 캐시·느린 호스트에서도? |
| D. 이식성 | 다른 호스트/OS에서 도는가? 없는 도구를 가정하는가? |
| E. 멱등·복원력 | 두 번 돌려도 안전한가? 실패해도 워크트리 생성을 막지 않는가? |
| F. 커버리지 | 레포에 실제로 필요한 준비가 다 들어 있는가? |

### 4. 커버리지 갭 (F)

레포 특성과 훅을 대조한다. `orca-project-config`의 점검 스크립트가 이 대조를 자동화한다:

```bash
P="${CLAUDE_SKILL_DIR}/../orca-project-config/assets/check_orca_project.sh"
bash "$P" --repo "$R"
```

`GAP_*` 코드가 나오면 그 갭이 **의도된 것인지** 판단한다 — 아무도 쓰지 않는 하위 패키지라면 갭이 아니다. 판단 근거를 리포트에 쓴다.

### 5. 리포트

등급별로 묶고, 각 항목에 **파일:라인 근거**와 **구체적 수정안**을 붙인다.

```
[CRITICAL] orca.yaml:34  archive 훅이 -L 검사 없이 rm 한다
  근거   : `rm -rf "$WT/refdata"` — 링크가 아니라 실제 디렉토리면 메인의 원본이 사라진다
  수정안 : if [ -L "$p" ]; then rm -f "$p"; fi
  영향   : 워크트리 아카이브 시 메인 체크아웃 데이터 손실
```

등급 기준:

| 등급 | 기준 |
|---|---|
| **CRITICAL** | 데이터 손실·시크릿 유출·훅 전체 무효화(파싱 실패·미인식 키·문법 오류)·매번 실패 |
| **MAJOR** | 훅이 조용히 절반만 실행됨(`set -e`), 타임아웃 위험, 다른 호스트에서 깨짐, 필수 준비 누락 |
| **MINOR** | 멱등성 흠, 잡음(`git status` 오염), 불필요한 비용 |
| **INFO** | 이식성 제약 명시, 개선 여지, 관측된 사실 |

**CRITICAL/MAJOR가 있으면 "통과"라고 쓰지 않는다.** 근거 없이 등급을 매기지도 않는다 — 라인을 인용할 수 없으면 그 지적은 빼거나 INFO로 낮춘다.

## 자주 나오는 진단

| 증상 | 진단 | 등급 |
|---|---|---|
| 훅이 아예 안 돈다 | 미인식 최상위 키 / YAML 파싱 실패 / 신뢰 확인 대기 | CRITICAL |
| 앞부분만 실행되고 끝난다 | 주입된 `set -e` 미해제 | MAJOR |
| 새 워크트리마다 실패 | 분리 스크립트가 git 미추적 | CRITICAL |
| 워크트리 생성이 오래 걸린다/중단된다 | 빌드·테스트가 훅에 있음 | MAJOR |
| `git status`에 `??` 잡음 | 링크가 `.gitignore`에 안 잡힘 → `info/exclude` 미등록 | MINOR |
| 팀원 호스트에서만 실패 | 호스트 절대경로 / `command -v` 가드 없음 | MAJOR |
| 아카이브 후 메인에서 파일이 사라짐 | `-L` 없는 링크 해제 | CRITICAL |
| `orca.yaml`에 토큰이 보임 | 커밋되는 파일에 시크릿 | CRITICAL |

## 참조

| 파일 | 내용 |
|---|---|
| `references/review-checklist.md` | 6카테고리 30항목 체크리스트 + 등급 판정 기준 |
| `../orca-setup-build/assets/check_orca_yaml.py` | 정적 검사기 |
| `../orca-setup-build/references/orca-yaml-schema.md` | 스키마·실행 규약 정본 |
| `../orca-project-config/assets/check_orca_project.sh` | 레포 특성 대비 커버리지 갭 |
