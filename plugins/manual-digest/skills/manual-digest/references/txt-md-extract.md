# TXT/MD 추출 가이드

가장 단순. Claude 내장 Read 도구로 직접 읽음.

## 단계

### 1. 직접 읽기
```
Read({ file_path: "<abs>.md" })
Read({ file_path: "<abs>.txt" })
```

대형 파일이면 offset/limit 사용:
```
Read({ file_path: "<abs>.md", offset: 100, limit: 200 })
```

### 2. 구조 파싱

#### Markdown
- `#`/`##`/`###` → 섹션 트리
- 코드 블록(```\`\`\`...\`\`\````)은 다이제스트에선 요약만 (본문은 위치 포인터로)
- 표/리스트는 키 정보면 보존, 길면 요약

#### Plain Text
- 빈 줄 다음 들여쓰기·대문자 시작 줄을 헤딩 후보로
- 챕터 표기(`Chapter 1`, `1.`, `1.1`) 패턴 매칭
- 헤딩 식별이 모호하면 사용자에게 확인

### 3. 위치 포인터

라인 번호 + 헤딩 텍스트:

```markdown
| § | 제목 | 라인 |
|---|------|------|
| §3 | Configuration | L120 |
| §3.1 | Options | L145 |
```

원본 핀포인트 추출:
```
Read({ file_path: "<abs>", offset: 145, limit: 30 })
```

### 4. 메타데이터

#### Markdown
- 파일 첫줄이 `---`이면 YAML frontmatter 파싱 (`title`, `author`, `date`, `version` 등)
- 첫 `#` 헤딩 → title 후보

#### TXT
- 파일명 → title 자동 생성
- 사용자에게 메타데이터 직접 입력 옵션 제공

## 압축비

TXT/MD는 이미 텍스트라 다이제스트가 원본보다 크게 줄지 않을 수 있다 (예: 50KB MD → 20KB digest = 40%). 큰 매뉴얼만 다이제스트화 권장 (≥ 200KB 또는 ≥ 5000줄).

작은 MD는 그냥 직접 읽는 게 나음.

## V1 검증 상태

🟡 부분 검증 — Read 동작 자체는 확실. 헤딩 추출 + 청킹 정확도는 다양한 MD 변형(GFM, MyST, Pandoc 확장)에서 추가 확인 필요.
