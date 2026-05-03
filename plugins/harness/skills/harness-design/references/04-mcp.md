# 단계 4: 테스트 도구 — MCP

> MCP(Model Context Protocol) 서버는 클로드에게 외부 도구를 제공한다.
> 코드만 보고는 알 수 없는 버그가 있다 — 브라우저에서 실제 클릭해봐야 보이는 UI 깨짐, DB에 쿼리 던져봐야 알 수 있는 데이터 이상. AI에게 그런 도구를 "만들어서 줘라".

## 이 단계가 잡는 빈틈

- 코드는 맞는데 브라우저에서 동작이 다른 경우 (UI/렌더링/타이밍 이슈)
- 라이브러리 사용법을 추측해서 잘못 쓰는 경우 (최신 문서 부재)
- DB 스키마/데이터 상태를 모른 채 마이그레이션 작성
- 외부 API 응답을 모른 채 파서 작성

## 진단 체크리스트

`.mcp.json` 또는 `.claude/.mcp.json`을 Read:

| 항목 | 양호 ✅ | 약함 ⚠️ | 없음 ❌ |
|------|--------|--------|---------|
| .mcp.json 존재 | 있음 | - | 없음 |
| 등록 서버 수 | 1~5개 (집중) | 10개+ (잡다) | 0개 |
| 작업과 무관한 서버 비활성 | 정리됨 | 안 쓰는 서버 다수 | - |
| 인증/시크릿 분리 | env 또는 별도 파일 | .mcp.json에 직접 | - |

## 핵심 MCP 서버 카탈로그

작업 유형별 추천:

### 웹 개발 / UI

- **playwright** — 브라우저 실행, 클릭/입력, 스크린샷, 콘솔 로그 캡처
  - 빈틈: "코드는 맞는데 화면이 이상해"
- **chrome-devtools** — 네트워크/성능/콘솔 분석

### 코드 라이브러리

- **context7** — 라이브러리 공식 문서 실시간 검색
  - 빈틈: 최신 API 추측 사용 → 잘못된 코드
- **deepwiki** — GitHub repo의 wiki/README 조회

### 데이터

- **postgres / sqlite / mysql** — DB 직접 쿼리
  - 빈틈: 스키마/데이터 추측

### 파일/시스템

- **filesystem** — 프로젝트 외부 디렉토리 접근 (보통 불필요, allow 정책으로 충분)
- **git** — git 작업 (보통 Bash로 충분)

### 협업

- **github** — 이슈/PR 조회 및 작성
- **linear / jira / notion** — 티켓 시스템 연동
- **slack** — 메시지 조회/발송

### LLM

- **memory** — 대화 간 메모리 (단, Claude Code 내장 메모리도 있으니 중복 주의)

## .mcp.json 기본 구조

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## 추천 패턴 — 작업 유형별

### 패턴 1: 웹 프론트엔드

`playwright` 단독으로 80% 커버. 추가로 `context7`(React/Vue 등 라이브러리 문서) 권장.

### 패턴 2: 백엔드 + DB

`postgres`(또는 적절한 DB) + `context7`. 마이그레이션 짤 때 실제 스키마 확인 가능.

### 패턴 3: 라이브러리/SDK 개발

`context7` + `deepwiki`. API 추측 대신 실문서 기반.

### 패턴 4: 운영/협업

`github` + `linear`(또는 jira/notion). 이슈 컨텍스트 자동 가져오기.

## 위치 — 어디에 두나

| 위치 | 공유 | 용도 |
|------|------|------|
| `<project>/.mcp.json` | git 커밋, 팀 공유 | 팀 표준 도구 |
| `~/.claude/.mcp.json` (또는 글로벌 settings) | 본인만 | 개인 도구 |
| `.mcp.json` + 토큰은 `.env` | 시크릿 분리 | 토큰 누출 방지 |

원칙: **MCP 서버 정의는 공유, 인증 토큰은 분리**. `.mcp.json`에는 `${ENV_VAR}` 참조만 두고, 실제 값은 `.env` 또는 OS 환경변수.

## 진행 절차 (이 단계 진입 시)

1. 현재 .mcp.json Read (있으면)
2. 사용자에게 작업 유형 묻기:
   - "주로 어떤 종류 작업이세요? 웹 / 백엔드 / 데이터 / 라이브러리 / 협업 ..."
3. 작업 유형에 맞는 1~3개 서버 추천 (잡다하게 많이 X, 핵심만)
4. 추천 형식:
   ```markdown
   ## 추천: MCP 서버 추가
   
   ### 추가 1: playwright
   사유: UI 작업 시 코드만으론 잡을 수 없는 버그를 잡기 위함.
        예: 버튼 클릭 후 모달이 안 뜨는 문제, CSS 깨짐 등.
   
   ```diff
    {
      "mcpServers": {
   +    "playwright": {
   +      "command": "npx",
   +      "args": ["-y", "@playwright/mcp"]
   +    }
      }
    }
   ```
   
   설치 명령 (사용자가 직접 실행 권장):
   `npx -y @playwright/mcp --help`
   ```
5. 사용자 확정 후 Edit
6. 적용 후: 클로드 재시작 필요. "Claude Code 재시작 후 `/mcp` 명령으로 서버 확인"  안내

## 자주 발생하는 함정

- **너무 많은 서버** — 모든 가능한 도구를 다 끌어오면 클로드가 어떤 걸 언제 쓸지 헷갈림. 실제로 쓸 것만
- **토큰을 .mcp.json에 직접** — 팀에 커밋하면 누출. 항상 env 분리
- **서버 추가 후 재시작 안 함** — Claude Code 재시작해야 새 서버 인식
- **MCP로 모든 걸 해결하려 함** — 단순 read는 Bash/Read로 충분. MCP는 외부 시스템과의 다리
- **Hook으로 가능한 일을 MCP로** — 예: lint는 Hook이 적합. MCP는 클로드가 호출 시점을 결정하는 도구
