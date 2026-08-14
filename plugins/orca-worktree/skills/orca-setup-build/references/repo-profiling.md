# 레포 프로파일링 — 무엇을 탐지하고 무엇을 넣는가

setup 훅의 단계는 레포에서 **증거를 찾아** 정한다. 마커 파일이 없으면 그 단계는 넣지 않는다.

## 탐지 명령

```bash
# 추적되는 마커 (모노레포 하위까지)
git ls-files | grep -E '(^|/)(pnpm-lock\.yaml|package-lock\.json|yarn\.lock|bun\.lockb|Cargo\.lock|go\.sum|uv\.lock|poetry\.lock|Pipfile\.lock|requirements[^/]*\.txt|CMakePresets\.json|CMakeLists\.txt|[^/]*\.sln|[^/]*\.csproj|gradlew|Makefile|Gemfile\.lock|composer\.lock)$'

# 도구 가용성
for t in pnpm npm yarn bun cargo go uv poetry python3 cmake ninja dotnet gradle; do
  printf '%-8s %s\n' "$t" "$(command -v $t || echo '-')"
done
```

## 생태계별 권장 단계

비용 등급: **S**(~5초) · **M**(5~30초) · **L**(30초+, 예산 위험) · **X**(넣지 않는다)

| 마커 | 단계 | 비용 | 주의 |
|---|---|---|---|
| `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` | S~M | pnpm 10+는 미승인 빌드 스크립트가 있으면 정상 설치 후에도 `ERR_PNPM_IGNORED_BUILDS`로 1을 반환한다 → 종료코드가 아니라 출력으로 판정 |
| `package-lock.json` | `npm ci` | M | `npm install`이 아니라 `ci` — lockfile을 고치지 않는다 |
| `yarn.lock` | `yarn install --frozen-lockfile` | M | Yarn 2+는 `--immutable` |
| `bun.lockb` | `bun install` | S | |
| `Cargo.lock` | `cargo fetch` | M | `cargo build`는 **X** |
| `go.sum` | `go mod download` | M | 모듈 캐시는 전역이라 워크트리 간 공유된다 |
| `uv.lock` | `uv sync` | S~M | |
| `poetry.lock` | `poetry install --no-root` | L | 프로젝트에 따라 초과 위험 |
| `requirements*.txt` | `python3 -m venv .venv && .venv/bin/pip install -r ...` | L | 무거우면 메인의 `.venv`를 **링크**하는 편이 낫다 |
| `CMakePresets.json` | `cmake --preset <p> -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` | M | **configure만**. `--build`는 X. `compile_commands.json`이 있어야 clangd·serena의 C++ 심볼 탐색이 된다 |
| `CMakeLists.txt`(preset 없음) | `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` | M | FetchContent가 있으면 워크트리마다 `_deps` 수십~수백 MB를 먹는다 — 디스크 경고를 리포트에 남긴다 |
| `*.sln` / `*.csproj` | `dotnet restore` | M~L | |
| `gradlew` | (넣지 않음) | X | 데몬 기동만으로 예산을 먹는다. 캐시 링크만 검토 |
| `Makefile` | (넣지 않음) | X | 무엇을 하는지 알 수 없다 — 사용자에게 물어본다 |
| `Gemfile.lock` | `bundle install --path vendor/bundle` | L | |
| `composer.lock` | `composer install` | M | |
| `.git/lfs` 또는 `.gitattributes`에 lfs | (넣지 않음) | X | 대용량 수신은 예산 밖 |

**공통 가드**: 모든 단계는 마커 존재 확인 + `command -v <도구>` 확인을 통과했을 때만 실행하고, 실패해도 경고로 처리한다.

```bash
if [ -f "<하위경로>/pnpm-lock.yaml" ] && command -v pnpm >/dev/null 2>&1; then
  ...
else
  warn "pnpm 미설치 — 의존성 미설치"
fi
```

## 비추적 자산 스캔

```bash
git status --ignored --short | head -40            # 무시되는 항목
git ls-files --others --exclude-standard | head    # 미추적(무시도 아님)
du -sm <후보> 2>/dev/null                          # 크기
```

| 유형 | 예 | 처리 |
|---|---|---|
| 에이전트/에디터 로컬 설정 | `.claude/settings.local.json`, `.serena/`, `.vscode/settings.json`(미추적) | 메인에서 **복사** (없을 때만) |
| 시크릿·환경파일 | `.env`, `.env.local`, `*.pem` | 메인에서 **복사**. 내용을 orca.yaml에 절대 쓰지 않는다 |
| 파이썬 가상환경 | `.venv` | 크면 **링크**, 작고 빠르면 재생성 |
| 대용량 참조 자산 | 레거시 소스, 데이터셋, 문서 툴체인 | **링크** + `info/exclude` |
| 의존성 디렉토리 | `node_modules` | lockfile 있으면 **재설치**(링크 금지 — 워크트리별 상태가 달라진다) |
| 빌드 산출물 | `build/`, `target/`, `obj/` | 아무것도 하지 않는다 |

100MB 이상은 복사하지 않는다. 워크트리 5개면 그대로 5배가 된다.

## 프로젝트 성격별 기본형

**문서 중심(빌드 없음)**: 로컬 설정 승계 + 작업 전제 점검(참조 저장소 도달 가능 여부, 다이제스트 존재)만. 실패해도 항상 `exit 0`.

**프론트엔드 단일**: 의존성 설치 + `.env` 승계. 대개 10초 안쪽.

**모노레포(FE + 네이티브)**: 하위 패키지별 설치 + configure. 하위 경로를 정확히 잡는 것이 핵심이며, 대개 가장 예산을 많이 쓴다.

**임베디드/네이티브**: configure만. 툴체인은 호스트 전역에 있으므로 존재 확인만 하고 설치하지 않는다.

**플러그인/설정 저장소**(이 마켓플레이스 같은): 검증 도구 가용성 확인 + 로컬 설정 승계. 빌드 단계 자체가 없다.
