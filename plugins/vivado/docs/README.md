# Vivado + Claude Code 개발 환경 설정

## 개념 정리 (한눈에 보기)

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code                          │
│                                                         │
│  ┌─────────────┐   "나 이 작업 어떻게 하지?"            │
│  │   스킬       │   → SKILL.md 참조해서 작업 수행        │
│  │  (HOW-TO)   │   예: "합성은 이 TCL로, 이 순서로"      │
│  └─────────────┘                                        │
│                                                         │
│  ┌─────────────┐   "이건 전문가한테 맡기자"              │
│  │  에이전트    │   → 별도 컨텍스트에서 독립 작업         │
│  │  (WHO)      │   예: "타이밍 분석은 timing-analyst가"  │
│  └─────────────┘                                        │
│                                                         │
│  ┌─────────────┐   "자주 쓰는 명령 단축키"               │
│  │  커맨드      │   → 현재 스킬로 통합됨                 │
│  │ (SHORTCUT)  │   예: /synth, /sim, /impl              │
│  └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

## 핵심 차이

| 구분 | 스킬 (Skill) | 에이전트 (Agent) |
|------|-------------|-----------------|
| 파일 위치 | `.claude/skills/이름/SKILL.md` | `.claude/agents/이름.md` |
| 역할 | **방법**을 정의 (작업 절차서) | **전문가**를 정의 (독립 작업자) |
| 컨텍스트 | 메인 대화에 포함됨 | **별도 컨텍스트 윈도우** |
| 호출 방식 | 자동 감지 또는 `/스킬명` | 자동 위임 또는 "~에게 맡겨줘" |
| 언제 쓰나 | 반복 작업의 표준 절차가 필요할 때 | 복잡한 분석을 메인 대화 오염 없이 할 때 |
| 지원 파일 | 같은 디렉터리에 템플릿, 스크립트 가능 | 시스템 프롬프트만 정의 |

## 디렉터리 구조

```
your-vivado-project/
├── .claude/
│   ├── skills/                    # ← 스킬 (작업 방법)
│   │   ├── vivado-sim/
│   │   │   ├── SKILL.md           # 시뮬레이션 절차
│   │   │   └── tb_template.v      # 테스트벤치 템플릿
│   │   ├── vivado-synth/
│   │   │   ├── SKILL.md           # 합성 절차
│   │   │   └── run_synth.tcl      # 합성 TCL 템플릿
│   │   ├── vivado-impl/
│   │   │   ├── SKILL.md           # Implementation 절차
│   │   │   └── run_impl.tcl       # Impl TCL 템플릿
│   │   ├── vivado-bitstream/
│   │   │   ├── SKILL.md           # Bitstream 생성 절차
│   │   │   └── run_bit.tcl        # Bitstream TCL 템플릿
│   │   └── vivado-project/
│   │       ├── SKILL.md           # 프로젝트 생성/관리 절차
│   │       └── boards.json        # 보드별 파트넘버/설정
│   │
│   ├── agents/                    # ← 에이전트 (전문가)
│   │   ├── rtl-designer.md        # Verilog RTL 설계 전문가
│   │   └── timing-analyst.md      # 타이밍 분석 전문가
│   │
│   └── CLAUDE.md                  # 프로젝트 전역 컨텍스트
│
├── rtl/                           # Verilog 소스
├── tb/                            # 테스트벤치
├── constraints/                   # XDC 파일 (보드별)
│   ├── arty_a7.xdc
│   ├── nexys4.xdc
│   └── zedboard.xdc
├── scripts/                       # TCL 스크립트
└── build/                         # 빌드 출력 (gitignore)
```

## 사용 시나리오

### 시나리오 1: "UART 모듈 만들어줘" 
→ Claude가 `rtl-designer` 에이전트에 위임
→ 에이전트가 Verilog 코드 작성, 별도 컨텍스트에서 작업
→ 완성된 코드만 메인 대화로 반환

### 시나리오 2: "합성 돌려줘"
→ Claude가 `vivado-synth` 스킬 자동 참조
→ 스킬에 정의된 TCL 명령과 절차대로 실행
→ 에러 발생 시 스킬의 트러블슈팅 가이드 참조

### 시나리오 3: "/vivado-sim uart_tb"
→ 슬래시 커맨드로 시뮬레이션 스킬 직접 호출
→ uart_tb 테스트벤치로 시뮬레이션 실행

### 시나리오 4: "타이밍 위반 분석해줘"
→ Claude가 `timing-analyst` 에이전트에 위임
→ 에이전트가 리포트 파일 읽고 분석 (별도 컨텍스트)
→ 분석 결과와 XDC 수정 제안만 반환
