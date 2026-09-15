---
description: PRD라는 말 없이 "작업 분해/WBS" 표현으로 하드웨어-펌웨어 요구사항의 계획을 요청한다
tags: [plan, hardware-firmware, phrasing]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Write, Glob, Grep, Skill]
runs: 3
---

이번 IO 보드 요구사항이 아래처럼 확정됐습니다. 작업 분해해서 WBS 좀 뽑아 주세요.
확정된 요구라 바로 진행하면 되고, 결과는 `docs/plan/PLAN-eval.md` 에 저장해 주세요.

```markdown
---
id: PRD-io-board
title: EtherCAT 디지털 IO 보드
profile: hardware-firmware
status: approved
version: 1.0
owner: 하드웨어팀
---

## 7. 요구사항

### REQ-001 — 광역 입력 전원부
- **강도**: MUST
- **설명**: 9~36V 입력에서 내부 5V/3A, 3.3V/2A를 안정적으로 공급해야 한다.
- **수용 기준**:
  - AC-001-1: 입력 9V와 36V 양 끝단에서 5V 레일 리플이 50mVpp 이하다.

### REQ-002 — EtherCAT 슬레이브 인터페이스
- **강도**: MUST
- **설명**: 1ms 주기 EtherCAT 통신으로 입출력 상태를 교환해야 한다.
- **수용 기준**:
  - AC-002-1: 1ms 주기로 1시간 연속 통신 시 워킹 카운터 오류가 0이다.

### REQ-003 — 절연 디지털 입력 16채널
- **강도**: MUST
- **설명**: 24V 신호 16채널을 광절연으로 받아야 한다.
- **수용 기준**:
  - AC-003-1: 채널 간 크로스토크로 인한 오검출이 24시간 시험에서 0건이다.

### REQ-004 — 상태 표시 LED
- **강도**: MAY
- **설명**: 전원·링크·에러 상태를 LED로 표시한다.
- **수용 기준**:
  - AC-004-1: 에러 발생 시 에러 LED가 점등된다.

## 11. 미결 이슈

| ID | 내용 | 영향 |
|----|------|------|
| OPEN-001 | EtherCAT 슬레이브 컨트롤러 칩 수급 미확정 | REQ-002 회로 설계와 펌웨어 드라이버 선택이 달라짐 |
```
