# setup 훅 작성 규약

## 필수 관용구

### 1. `set +e` — 타협 불가

```bash
set +e   # Orca가 러너 첫머리에 주입한 set -e 를 해제
```

없으면 첫 실패에서 나머지 단계가 통째로 누락된다. 그런데 **누락됐다는 사실이 눈에 띄지 않는다** — 앞부분 출력만 보고 성공했다고 오해하기 쉽다.

### 2. cwd 고정

```bash
WT="${ORCA_WORKTREE_PATH:-$PWD}"
cd "$WT" || exit 0
```

### 3. 멱등

```bash
[ -e "$dst" ] || cp "$src" "$dst"                       # 있으면 안 건드린다
[ -e "$dst" ] || [ -L "$dst" ] || ln -s "$src" "$dst"
grep -qxF "$pat" "$excl" 2>/dev/null || echo "$pat" >> "$excl"   # 중복 추가 금지
```

드라이런이 같은 워크트리에서 훅을 두 번 돌린다. 두 번째가 실패하면 멱등하지 않은 것이다.

### 4. 항상 `exit 0`

setup 실패로 워크트리 생성을 막을 이유는 거의 없다. 경고를 세어 마지막에 요약하고 `exit 0`으로 끝낸다.

```bash
if [ "$WARN_COUNT" -gt 0 ]; then
  echo "setup 완료 — 경고 ${WARN_COUNT}건 (작업은 가능하다)"
fi
exit 0
```

### 5. 경로는 변수로

`$ORCA_ROOT_PATH` / `$ORCA_WORKTREE_PATH`만 쓴다. `/home/<user>/...`, `/Users/<user>/...`, `C:\Users\...`는 팀원 호스트에서 깨진다.

### 6. 도구 존재 확인

```bash
command -v pnpm >/dev/null 2>&1 || { warn "pnpm 없음"; }
```

### 7. 링크 해제는 `-L` 확인 후에만 (archive)

```bash
for p in old .venv; do
  [ -L "$p" ] && rm -f "$p"      # 실제 디렉토리면 절대 건드리지 않는다
done
```

이 가드를 빼면 메인 체크아웃의 원본을 지울 수 있다. 링크 대상이 수백 MB짜리 참조 자산이라면 복구가 어렵다.

### 8. 사람이 읽는 출력

```bash
ok()   { printf '  ✓ %s\n' "$*"; }
skip() { printf '  · %s\n' "$*"; }
warn() { printf '  ! %s\n' "$*"; WARN_COUNT=$((WARN_COUNT+1)); }
```

Orca는 setup 터미널에 이 출력을 그대로 보여준다. 무엇이 됐고 무엇이 안 됐는지 한눈에 보여야 한다.

### 9. 종료코드가 거짓말하는 도구는 출력으로 판정

```bash
out="$( (cd pkg && pnpm install --frozen-lockfile) 2>&1 )"; rc=$?
if [ "$rc" -eq 0 ]; then
  ok "pnpm install"
elif printf '%s' "$out" | grep -q 'ERR_PNPM_IGNORED_BUILDS'; then
  ok "pnpm install (미승인 빌드 스크립트 — 메인 체크아웃과 동일, 무해)"
else
  printf '%s\n' "$out" | tail -15
  warn "pnpm install 실패 — 수동 실행 필요"
fi
```

## 안티패턴

| 안티패턴 | 왜 문제인가 | 대신 |
|---|---|---|
| `set -e` 유지 | 첫 실패에서 전부 누락 | `set +e` + 단계별 판정 |
| `cmake --build`, `npm run build`, `pytest` | 120초 초과 | configure/설치까지만 |
| `git clean`, `git reset --hard`, `git checkout .` | 작업분 파괴 | 넣지 않는다 |
| `sudo`, `apt-get install` | 호스트 상태 변경, 대개 비대화형에서 실패 | 존재 확인 후 경고 |
| `.env` 내용을 YAML에 인라인 | `orca.yaml`은 커밋된다 | 메인에서 복사 |
| `cp -r` 대용량 디렉토리 | 워크트리 수만큼 배수로 증가 | `ln -s` + `info/exclude` |
| `node_modules` 링크 | 워크트리 간 의존성 상태가 얽힌다 | lockfile로 재설치 |
| `rm -rf "$ORCA_ROOT_PATH/..."` | 메인 체크아웃 훼손 | 워크트리 안으로 범위 제한 |
| 실패 시 `exit 1` | 워크트리 생성 자체를 막는다 | 경고 + `exit 0` |
| YAML 블록에 200줄 셸 | 디버깅 불가, 들여쓰기 사고 | `tools/orca-setup.sh` 분리 |
| 분리 스크립트를 커밋하지 않음 | 새 워크트리에 파일이 없어 매번 실패 | `git add` |

## 인라인 vs 분리

| | 인라인 (`orca.yaml`) | 분리 (`tools/orca-setup.sh`) |
|---|---|---|
| 적합 | 단계 3개 이하, 각 5줄 이하 | 그 이상 |
| 장점 | 파일 하나, 한눈에 보임 | 직접 실행 가능, 셸 문법 검사·리뷰 용이 |
| 단점 | 들여쓰기 사고 = 훅 전체 무시 | 파일 2개, **커밋 누락 시 매번 실패** |

분리형의 `orca.yaml`:
```yaml
scripts:
  setup: |
    set -u
    bash tools/orca-setup.sh
```
(분리 스크립트 안에서 `set -uo pipefail`을 다시 잡으므로 여기서는 `set +e`가 아니라 `set -u`로 충분하다. 단, `bash` 호출이 실패해도 훅이 죽지 않기를 원하면 `|| true`를 붙인다.)

## Windows

Orca는 Windows 호스트에서 `%ComSpec%`(cmd.exe)로 훅을 실행한다. bash 스크립트는 그대로는 동작하지 않는다. 세 가지 중 하나를 택한다:

1. **명시적 제약** — 헤더 주석에 "리눅스/macOS 전용"이라 적고, Windows 팀원이 생기면 분기를 추가한다 (대부분의 팀에 충분)
2. **분기** — `%ComSpec%`에서 동작하는 cmd 버전을 병행 작성
3. **최소 공통** — Windows에서도 도는 명령만 사용 (실무상 비현실적)

어느 쪽을 택했는지 리포트에 반드시 남긴다.
