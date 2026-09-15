---
description: "CI 파이프라인 소요 시간을 묻는 개발자 질문 — '얼마나 걸려'·'언제 끝나' 같은 일정 계열 문구가 들어 있지만 프로젝트 계획 수립이 아니므로 prd-plan 계열 스킬이 발동하면 안 된다"
tags: [negative, no-fire, over-trigger]
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

CI에서 테스트 전체를 한 번 다 돌리면 보통 얼마나 걸려야 정상인가요?
지금은 PR 올려놓고 언제 끝나나 계속 쳐다보게 돼서 리뷰가 밀립니다.

아래가 어제 빌드 로그 요약인데, 어느 단계가 시간을 잡아먹는지 짚어 주시고
줄일 방법이 있으면 알려 주세요. 답변에 바로 적어 주시면 됩니다.

```
[00:00]  checkout                       12s
[00:12]  npm ci                       3m 41s
[03:53]  tsc --noEmit                 1m 08s
[05:01]  jest unit (worker 4)         2m 20s
[07:21]  playwright e2e (worker 1)   11m 47s
[19:08]  docker build + push          4m 02s
[23:10]  done                   total 23m 10s
```

캐시는 아직 안 걸어 뒀고, e2e는 러너 한 대에서 순차로 돕니다.
