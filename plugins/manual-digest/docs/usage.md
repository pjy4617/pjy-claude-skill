# manual-digest 사용 가이드

대용량 매뉴얼을 한 번 추출·요약하여 마크다운 다이제스트로 저장하고, 이후 작업에서는 다이제스트만 참조하는 워크플로.

## 빠른 시작

### 1. 환경 셋업 (1회만)

```
/manual-digest-setup
```

수행 항목:
- PDF 추출용 MCP(`@sylphx/pdf-reader-mcp`) 등록
- `.claude/manuals/` 디렉토리 생성
- `INDEX.md` 헤더 작성
- `CLAUDE.md`에 마커 블록 주입

**MCP 신규 등록한 경우 Claude Code 재시작 필요**.

### 2. 첫 매뉴얼 등록

```
/manual-digest C:\docs\STM32F4-RM0090.pdf
```

- 자동: 추출 → 요약 → `digest.md` / `index.md` / `metadata.json` 작성
- 결과: `<project>/.claude/manuals/stm32f4-rm0090/`

### 3. 활용

이후 매뉴얼 관련 질문 시 Claude가 **자동으로 다이제스트를 1차 참조**한다 (CLAUDE.md 마커 가이드 동작).

```
사용자: SPI1 클럭 분주비 어떻게 설정해?
  → Claude: INDEX.md → digest.md(stm32f4-rm0090) → §RCC.PLL 확인
  → 디테일 부족 시 → index.md에서 페이지 포인터 → 원본 PDF p.220만 핀포인트 추출
  → 답변 + 출처 명시 (§6.2.3, p.220)
```

## 명령어

### 인제스트 (메인 스킬)

```
/manual-digest <path> [--scope project|global] [--depth shallow|standard|deep]
```

| 옵션 | 의미 |
|------|------|
| `--scope project` (기본) | `<project>/.claude/manuals/`에 저장 |
| `--scope global` | `~/.claude/manuals/`에 저장 (모든 프로젝트 공유) |
| `--depth shallow` | 압축비 우선 (~5KB 정도) |
| `--depth standard` (기본) | 균형 (~20KB) |
| `--depth deep` | 정확도 우선 (~50KB) |

### 갱신

```
/manual-digest --update <id>
```

원본 sha256이 바뀐 경우 변경된 섹션만 재요약 (비변경 섹션 보존).

### 목록

```
/manual-digest --list                    # project + global 통합 (project override)
/manual-digest --list --scope global     # global만
```

### 삭제

```
/manual-digest --remove <id>
```

해당 매뉴얼 디렉토리 + INDEX.md 항목 + CLAUDE.md 카탈로그 갱신.

## 스코프 결정 가이드

| 상황 | 권장 스코프 |
|------|------------|
| 특정 보드 데이터시트 | `project` |
| 프로젝트별 SDK 매뉴얼 | `project` |
| ARM Cortex-M TRM, C99 표준 같은 표준 매뉴얼 | `global` |
| 여러 프로젝트에서 공유하는 라이브러리 매뉴얼 | `global` |

## 지원 포맷

| 포맷 | V1 검증 | 추출 도구 |
|------|--------|-----------|
| PDF | ✓ 검증 (TwinCAT 168p, 0.29% 압축) | `@sylphx/pdf-reader-mcp` MCP |
| HTML | 미검증 | Claude Read |
| TXT/MD | 부분 검증 | Claude Read |
| EPUB | 미검증 | PowerShell `Expand-Archive` |
| DOCX | 미검증 | PowerShell `Expand-Archive` |
| CHM | 미검증 (Windows 전용) | `hh.exe -decompile` |

## 산출물 구조

```
<scope>/.claude/manuals/
├── INDEX.md                              ← 마스터 카탈로그
└── <manual-id>/
    ├── digest.md                         ← 개요 + 섹션 요약 + 키워드
    ├── index.md                          ← 섹션 → 페이지 매핑
    └── metadata.json                     ← 메타데이터 + 샘플링 전략
```

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| `pdf-reader MCP 미등록` | `/manual-digest-setup --mcp-only` |
| `MCP 등록했는데 read_pdf 도구 없음` | Claude Code 세션 재시작 |
| `CLAUDE.md 마커 손상` | `/manual-digest-setup --repair` |
| `같은 ID 중복 인제스트` | sha256 같으면 자동 스킵, 다르면 확인 후 덮어쓰기 |
| `대형 PDF (1000p+) 시간 초과` | 자동으로 페이지 청크 분할 — 진행률 표시 확인 |
| `스캔 PDF (텍스트 레이어 없음)` | "OCR 필요, V2 이후" — 현재 미지원 |

## 참고

- PRD: `.temp/PRD-manual-digest.md`
- 검증 결과: PRD 부록 B (TwinCAT 3 I/O Manual 실측)
