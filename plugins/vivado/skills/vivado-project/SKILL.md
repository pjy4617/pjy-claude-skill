---
name: vivado-project
description: Vivado 프로젝트 생성, 보드 변경, 소스 파일 관리 시 사용. "프로젝트 만들어", "보드 바꿔", "새 모듈 추가" 등의 요청에 자동 적용.
---

# Vivado 프로젝트 관리

## 하이브리드 모드 기본 원칙
- CLI batch 모드로 빌드 (Non-Project 모드, .xpr 파일 없음)
- 시각적 확인이 필요할 때만 GUI로 체크포인트(.dcp) 열기
- GUI에서 디자인을 수정하지 않음. 수정은 항상 RTL/XDC에서.

## 보드 설정
`boards.json` 파일에서 타겟 보드 정보를 참조합니다.

boards.json에 포함된 정보:
- `part` — FPGA 파트 넘버 (TCL의 `set PART`에 사용)
- `clock_freq_mhz`, `clock_pin` — 기본 클럭 설정
- `bank_vcco` — **뱅크별 전압 및 IOSTANDARD** (pin-reviewer, kicad-xdc-gen이 참조)
- `master_xdc_url` — Digilent 공식 마스터 XDC 링크

보드 변경 시:
1. `boards.json`에서 파트 넘버 확인
2. TCL 스크립트의 `set PART` 변수 수정
3. 해당 보드의 XDC 파일이 `constraints/`에 있는지 확인
4. `bank_vcco`가 새 보드에 맞게 정의되어 있는지 확인
5. `"핀 배치 확인해줘"` → pin-reviewer가 보드 변경 후 핀 검증

## XDC 제약 파일 생성 방법

두 가지 방법이 있습니다:

**방법 1: KiCad 회로도에서 자동 생성 (KiCad 있을 때)**
- `"KiCad에서 XDC 만들어줘"` → kicad-xdc-gen 에이전트가 생성
- 회로도의 핀 연결 정보에서 PACKAGE_PIN, IOSTANDARD 자동 결정
- boards.json의 `bank_vcco`를 참조하여 전압 매핑

**방법 2: 수동 작성 (KiCad 없을 때)**
- rtl-designer 에이전트에게 `"XDC도 만들어줘"` 요청
- 또는 Digilent 마스터 XDC를 복사하여 필요한 핀만 활성화

## 새 모듈 추가 절차
1. `rtl/모듈명.v` 생성
2. `tb/tb_모듈명.v` 테스트벤치 생성
3. (run_synth.tcl이 glob 패턴 사용 시 자동 포함)

## 파일 구조 검증
프로젝트 작업 전 항상 확인:
```bash
# 소스 파일 목록
find rtl/ -name "*.v" | sort

# 테스트벤치 확인
find tb/ -name "tb_*.v" | sort

# 제약 파일 확인
ls constraints/*.xdc

# KiCad 파일 확인 (있으면)
find . -name "*.kicad_sch" -o -name "*.kicad_pro" 2>/dev/null
```
