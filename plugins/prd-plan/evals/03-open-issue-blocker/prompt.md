---
description: 미결 이슈가 MUST 요구 전체의 전제를 막고 있는 research-PoC PRD로 계획을 요청한다
tags: [plan, research-poc, open-issue]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Write, Glob, Grep, Skill]
runs: 3
---

아래 연구 과제 요구사항으로 실행 계획을 만들어 주세요. 착수는 확정됐습니다.
결과는 `docs/plan/PLAN-eval.md` 에 저장해 주세요.

```markdown
---
id: PRD-defect-poc
title: 표면 결함 검출 모델 PoC
profile: research-PoC
status: approved
version: 1.0
owner: 비전팀
---

## 7. 요구사항

### REQ-001 — 베이스라인 재현
- **강도**: MUST
- **설명**: 공개 논문의 베이스라인 모델을 사내 데이터셋에서 재현해야 한다.
- **수용 기준**:
  - AC-001-1: 논문 보고 수치 대비 mAP 편차가 3%p 이내다.

### REQ-002 — 제안 기법 구현·비교
- **강도**: MUST
- **설명**: 제안 기법을 구현해 베이스라인과 동일 조건에서 비교해야 한다.
- **수용 기준**:
  - AC-002-1: 동일 학습·평가 분할에서 베이스라인 대비 mAP가 개선된다.

### REQ-003 — 채택 판정 기준
- **강도**: MUST
- **설명**: PoC 채택/중단을 판정할 기준을 사전에 고정해야 한다.
- **수용 기준**:
  - AC-003-1: 채택 기준과 중단 기준이 수치로 명시되고, 측정 방법이 함께 적혀 있다.

## 11. 미결 이슈

| ID | 내용 | 영향 |
|----|------|------|
| OPEN-001 | 평가 데이터셋 외부 반출·학습 이용 라이선스 확인 미완 | 불가 판정 시 REQ-001·REQ-002의 학습·평가 전제가 통째로 바뀜 |
| OPEN-002 | 사내 GPU 자원 배정량 미정 | 실험 반복 횟수와 병행 실험 수가 결정되지 않음 |
```
