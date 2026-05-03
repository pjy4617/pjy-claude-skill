# 단계 2: 위험 차단 — Permissions

> Permissions는 도구 호출 자체를 **차단**한다. CLAUDE.md가 "부탁"이라면, 이건 "어길 수 없는 벽"이다.
> 클로드가 아무리 시도해도 deny에 걸린 명령은 실행되지 않는다.

## 이 단계가 잡는 빈틈

- `rm -rf`, `git push --force` 같은 파괴적 명령을 클로드가 자동 실행
- 매번 "이거 실행해도 돼요?" 권한 프롬프트가 떠서 흐름 끊김 (자주 쓰는 안전 명령)
- 외부 네트워크나 민감 디렉토리에 접근 차단 필요

## 진단 체크리스트

`.claude/settings.json` 및 `.claude/settings.local.json`을 Read하고:

| 항목 | 양호 ✅ | 약함 ⚠️ | 없음 ❌ |
|------|--------|--------|---------|
| settings.json 존재 | 있음 | local만 있음 | 둘 다 없음 |
| `permissions.allow` | 자주 쓰는 안전 도구 명시 | 너무 광범위 (`Bash(*)`) | 비어있음 |
| `permissions.deny` | 위험 명령 차단 | 없음 — 모두 ask | 없음 |
| `permissions.ask` | 회색 영역 명시 | 빠짐 | 없음 |
| 와일드카드 사용 | 적절 (`Bash(npm:*)`) | 과다 (`Bash(*)`) | - |

글로벌(`~/.claude/settings.json`)도 같이 본다. 글로벌에서 deny된 건 프로젝트 settings로 풀 수 없다는 점을 인지.

## 강제력의 진실 — settings.json의 작동 원리

```
사용자 prompt
   ↓
클로드가 도구 호출 시도
   ↓
[1] permissions.deny에 걸리면 → 차단 (사용자에게 알림 없이도)
[2] permissions.allow에 매치되면 → 자동 허용 (프롬프트 없음)
[3] permissions.ask에 매치되면 → 사용자에게 묻기
[4] 어디에도 없으면 → 기본 동작 (모드에 따라 ask 또는 자동)
```

deny가 가장 강하다. 클로드가 우회를 시도하더라도(예: `bash -c "rm ..."`로 둘러서 호출) 패턴 매칭 차단이라 막힌다 — 단, 패턴이 정확해야 한다.

## 위험 패턴 차단 추천 (deny)

```json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(rm -fr:*)",
      "Bash(git push --force:*)",
      "Bash(git push -f:*)",
      "Bash(git reset --hard:*)",
      "Bash(git clean -fd:*)",
      "Bash(:(*)~/.ssh*)",
      "Bash(curl:*| sh)",
      "Bash(wget:*| sh)",
      "Bash(chmod 777:*)",
      "Bash(sudo:*)"
    ]
  }
}
```

각 패턴의 의미:
- `rm -rf` / `rm -fr` — 재귀 삭제 차단 (단일 파일 `rm`은 허용)
- `git push --force` — 히스토리 덮어쓰기 차단
- `git reset --hard` — 작업물 손실 차단
- `~/.ssh` 접근 — 키 노출 위험
- `curl | sh` — 검증 없이 외부 스크립트 실행
- `chmod 777` — 보안 약화
- `sudo` — 권한 상승 (개발 환경에선 보통 불필요)

## 안전 자동 허용 추천 (allow)

매번 묻기 귀찮은 명령은 allow에 둔다. 단, "되돌릴 수 있는 것"만:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(ls:*)",
      "Bash(pwd)",
      "Bash(cat:*)",
      "Bash(git status)",
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(npm test:*)",
      "Bash(npm run lint:*)",
      "Bash(pytest:*)",
      "Bash(python:*)"
    ]
  }
}
```

원칙:
- 읽기 전용은 광범위하게 allow OK
- 쓰기는 좁게 — `Edit` 자체보다 특정 디렉토리만 OK 같은 건 어려우니, 쓰기는 그냥 ask로 두는 것도 안전
- 외부 네트워크는 최소화 — `WebFetch`는 ask 권장

## 회색 영역은 ask로

확실히 좋다/나쁘다 판단 어려운 건 ask로 명시:

```json
{
  "permissions": {
    "ask": [
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(npm publish:*)",
      "Write(.env*)",
      "Write(secrets/*)"
    ]
  }
}
```

## 위치 — settings.json vs settings.local.json

| 파일 | 공유 | 용도 |
|------|------|------|
| `.claude/settings.json` | git에 커밋, 팀 전체 | 팀 표준 정책 |
| `.claude/settings.local.json` | gitignore, 본인만 | 개인 추가 허용 |
| `~/.claude/settings.json` | 본인 + 모든 프로젝트 | 글로벌 기본값 |

규칙: **deny는 팀 settings에**, allow의 개인 추가는 local에. 팀 권한 정책은 공유돼야 일관된다.

## 진행 절차 (이 단계 진입 시)

1. settings.json (project & local & global) 모두 Read
2. 진단 체크리스트로 약점 식별
3. 추천 작성. 보통 다음 두 트랙:
   - **deny 트랙**: 위험 명령 차단 추가
   - **allow 트랙**: 자주 쓰는 안전 명령 자동화
4. 추천 형식:
   ```markdown
   ## 추천: settings.json 보강

   ### deny 추가 (프로젝트 settings.json)
   사유: 현재 deny 정책 없음 → rm -rf 같은 명령이 ask 한 번 누르면 실행됨
   
   ```diff
    "permissions": {
      "allow": [...],
   +  "deny": [
   +    "Bash(rm -rf:*)",
   +    "Bash(git push --force:*)"
   +  ]
    }
   ```
   ```
5. 사용자 확정 후 Edit
6. 적용 후 짧은 검증: 실제 deny된 명령을 클로드에게 시켜보라고 안내(테스트 권장)

## 자주 발생하는 함정

- **광범위 allow** — `Bash(*)` 같은 건 deny를 무력화한다. 좁게 시작해서 필요할 때 추가
- **deny 패턴 부정확** — `Bash(rm -rf)`는 매치 안 됨. 인자 와일드카드 `Bash(rm -rf:*)` 필요
- **글로벌 deny를 프로젝트 allow로 풀려는 시도** — 안 됨. deny 우선
- **테스트 없이 배포** — deny 추가 후 클로드가 정상 작업도 못 하게 되는 경우. 테스트 한 사이클 권장
- **CLAUDE.md에 "rm -rf 쓰지마"라고만 적기** — 그건 단계 1. 차단 효과는 단계 2여야 한다
