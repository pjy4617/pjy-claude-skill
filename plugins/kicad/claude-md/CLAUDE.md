## KiCad 회로도 도구 설정

이 프로젝트에는 KiCad 회로도 풀스택 도구가 설치되어 있습니다.

### 사용 가능한 스킬

- `/kicad-review` — 회로도 분석, 데이터시트 비교 검증, BOM 생성을 통합 수행
- `/kicad-design` — PRD/설계사양서 기반 KiCad 회로도 생성
- `/kicad-setup` — 에이전트를 다른 프로젝트에 설치

### 에이전트

- `kicad-schematic-reviewer` — 회로도 리뷰 전문가 (8단계 체크리스트 + 데이터시트 비교)
- `kicad-bom-generator` — BOM 마크다운 생성 전문가
- `kicad-schematic-designer` — PRD 기반 회로도 설계 전문가

### 워크플로우

```
[설계] PRD/설계사양서
  → kicad-design 스킬 트리거
  → kicad-schematic-designer 에이전트가 회로도 생성
  → .kicad_sch 파일 출력

[리뷰] 회로도 리뷰 요청
  → kicad-review 스킬 트리거
  → kicad-schematic-reviewer 에이전트가 8단계 리뷰 수행
  → kicad-bom-generator 에이전트가 BOM 마크다운 생성
  → 종합 보고서 출력
```

### KiCad CLI

- `kicad-cli`가 설치되어 있으면 넷리스트/BOM 추출, PDF 내보내기 정확도가 높아집니다
- 없으면 `.kicad_sch` 직접 파싱 모드로 동작합니다 (정확도 제한 경고 포함)
