# WMX3 애플리케이션 에러 처리 가이드

WMX3 함수는 예외를 던지지 않고 **오류 코드를 반환**한다. 반환값이 `ErrorCode::None`(C#은
`ErrorCode.None`)이면 성공이다. 이 문서는 반환 코드 처리 원칙과 v3.7 특유의 주의점을 정리한다.
(근거: WMX3.7 매뉴얼 미러 tutorial1-4/tutorial2-4, funcnotes, release-notes;
다이제스트 `wmx37-user-manual-kr`, `wmx3-user-manual-kr`)

## 1. 원칙: 모든 반환 코드를 확인한다

- 튜토리얼 원문: "실제 응용 프로그램에서는 각 함수의 반환 값을 확인하고 감지된 오류를 적절하게
  처리해야 합니다." (tutorial1-4)
- 오류 발생 시 기본 동작: **처리 중단 → 통신 정지(StopCommunication) → 디바이스 닫기(CloseDevice)**.
  어떤 오류 경로에서도 이 정리 시퀀스를 건너뛰지 않는다(튜토리얼의 `goto exit` 패턴,
  C++ RAII 래퍼 또는 C# `try/finally`로 구조화 가능).
- 반환값을 버리는 호출(`(void)` 캐스팅, 결과 미사용)은 리뷰에서 MAJOR 이상으로 취급한다.

## 2. ErrorToString 활용

- 각 모듈이 `ErrorToString`을 정의한다 — **해당 모듈의 오류는 해당 모듈 클래스의 것으로 변환**
  (예: CoreMotion 함수의 오류는 `CoreMotion`의 `ErrorToString`).
- 시그니처(보충정보 String형의 반환값 원문 확인):
  - C++: `static long ErrorToString(int errCode, char* pString, unsigned int size)` (+ `wchar_t*` 오버로드)
  - .NET: `static String ErrorToString(int errCode)` — 반환값으로 문자열 반환
- `ErrorToString`은 엔진과 통신하지 않아 **인터럽트 처리 중에도 지연 없이 실행**된다(funcnotes_blk)
  — 오류 경로/로그 경로에서 안심하고 호출 가능.
- API 로그 원시 데이터 변환에는 `ApiLogToString`, 타임스탬프에는 `TimestampToString`(Log 모듈)을
  사용한다(시그니처는 보충정보 확인, 상세 사용법은 API Reference에서 시그니처 확인).

## 3. 오류 코드의 모듈별 분류

오류 코드는 모듈별로 분류되어 있다(3.6u3 다이제스트 §5: 기본/API버퍼/보정/코어모션/Advanced모션/
사이클릭버퍼/이벤트/IO. 3.7 위치: `kr/guide/motion/error_codes/`). 진단 시:

1. 오류를 반환한 함수가 속한 모듈의 오류 코드 표를 먼저 확인
2. `ErrorToString` 문자열과 대조
3. 필요 시 API 로그로 호출 이력 추적 (§7)

## 4. 재시도 vs 중단 판단

원문에서 확인된 대표 오류의 성격으로 판단 기준을 세운다:

| 오류 (원문 확인) | 의미 | 대응 |
|------|------|------|
| `StartingPreviousCommand` | 모션 시작 후 첫 인터럽트 종료 전에 오버라이드 호출 (funcnotes_blk) | **재시도 가능** — Command Ready 상태 확인 후 재호출, 또는 "API는 모션 시작까지 대기" 파라미터 TRUE 유지 |
| `WaitTimeout` | Wait 타임아웃 초과 (wait_timeout) | 상황별 — 조건 미충족 원인(축 정지/알람) 확인 후 재시도 또는 중단 |
| `CommNotStarted` | 통신 개시 전 API 호출 (release-notes) | **중단** — 초기화 시퀀스 결함, 코드 수정 |
| `DeviceIsNull` | CreateDevice 미수행 디바이스로 호출 (funcnotes_special) | **중단** — 초기화 시퀀스 결함 |
| `InterruptMismatch` | 보간/동기 축이 서로 다른 인터럽트 (funcnotes_ipt) | **중단** — 축 구성/설계 수정 |
| `AlreadyRecordingForSpecifiedChannel` | 기록 중 API 버퍼 채널에 Execute/Halt/Clear/Rewind 호출 (v3.7 명확화) | **중단** — 기록 종료(EndRecordBufferChannel) 후 호출하도록 로직 수정 |
| `ApiBufferNotOpened` | CreateApiBuffer로 열지 않은 채널 조작 (release-notes) | **중단** — 초기화 순서 수정 |
| `RequestModeChangeTimeout` / `PrevSettingsBeingApplied` | ApiBuffer 모드 변경 타임아웃/직전 지령 처리 중 (release-notes) | **제한적 재시도** — 짧은 대기 후 재호출, 반복되면 중단 |

일반 규칙:
- **일시적 상태 경합**(타이밍성) → 짧은 대기 후 제한 횟수 재시도 (무한 재시도 금지)
- **시퀀스/구성 결함** → 재시도 무의미, 중단하고 코드/설계 수정
- 위 표에 없는 오류는 매뉴얼 오류 코드 섹션과 API Reference에서 성격을 확인한 뒤 분류한다.

## 5. 운전 중 통신 이상 처리 (EtherCAT 케이블 단선·슬레이브 탈락 등)

초기화 성공 후에도 케이블 단선·슬레이브 탈락 등으로 운전 중 통신이 끊길 수 있다.
시뮬레이터 플랫폼에는 네트워크 계층이 없어 이 경로는 테스트로 걸러지지 않으므로
(wmx3-app-test 스킬 `references/simulator-platform.md` §6 검증 불가 항목), 구현 단계에서 아래를 반영한다.

- **감시**: 운전 중 주기적으로 `GetStatus`의 Engine State를 확인하고, `Communicating`에서
  이탈하면 통신 이상으로 판정한다. 감시 주기·판정 기준은 앱 요구에 맞게 설계서에 명기한다.
  (매뉴얼에서 확인된 감시 메커니즘은 GetStatus 폴링)
- **판정 시 대응**: 모션 정지/서보 오프 시도 → 원인 확인 → `StopCommunication` → `CloseDevice`
  정리(§1의 정리 시퀀스와 동일 원칙). 재접속(재초기화) 여부는 **원인 제거 확인 후** 판단하고,
  무한 자동 재접속은 금지한다(§4 일반 규칙과 정합).
- **관련 오류 코드**: 매뉴얼 EtherCAT 플랫폼 오류 코드 섹션에서 확인 —
  3.6u3 CHM `_w_m_x3__p_l_a_t_f_o_r_m__f_u_n_c__e_c__e_r_r_c_o_d_e*.html`,
  3.7 미러 `kr/guide/ec/error_codes.html`.
- Watchdog(§7)은 반대 방향(**앱 장애 시 엔진 측** 안전 동작)의 보완재로, 이 절의
  통신 이상 감시(앱이 통신 이상을 감지)를 대체하지 않는다.

## 6. v3.7 오류코드 값 시프트 — 하드코딩 금지 (CRITICAL)

v3.7에서 `RewindBlockIndexOutOfRange` 오류 코드가 **0x12006 위치에 삽입**되어 후속 API 버퍼
오류 코드의 정수 값이 **+1씩 이동**했다. 예: `AlreadyRecordingForSpecifiedChannel`
**73734 → 73735**. (release-notes 원문: "로그 파서 또는 진단 도구에 오류 코드 값을 하드코딩한
사용자는 이에 맞게 업데이트해야 합니다.")

규칙:
- 비교는 항상 **심볼 상수**로: `if (err == ErrorCode::None)`, 오류 코드 enum 멤버 사용.
  `if (err == 73734)` 같은 정수 리터럴 비교 금지.
- 로그 파서/진단 도구/알람 매핑 테이블에 정수 오류코드를 저장했다면 v3.7 기준으로 재생성.
- 탐지 grep (기존 코드 점검용):

```bash
# 오류코드로 의심되는 정수 리터럴 비교/매핑 탐지 (API 버퍼 계열 7373x, 0x1200x)
grep -rn "7373[0-9]\|0x1200[0-9]" --include="*.cpp" --include="*.cs" --include="*.h" .
# err 변수와 정수 리터럴 직접 비교 탐지
grep -rn "err\s*==\s*[0-9]\{3,\}\|ErrorCode)\s*[0-9]\{3,\}" --include="*.cpp" --include="*.cs" .
```

## 7. 로그 연계 진단

- **API 로그**(Log 모듈 `SetApiLog`): 어떤 API가 언제 호출되었는지 추적 — 오류 재현 경로 특정에 사용.
  `SetApiLog`는 메모리를 동적으로 할당/해제하므로 초기화 단계에서 설정(funcnotes_mem).
- **데이터 로그/메모리 로그**(`SetLog`/`StartLog`, `SetMemoryLog`/`StartMemoryLog`): 오류 발생 전후의
  축 지령/피드백 파형 확보. 로그 대상 축이 서로 다른 인터럽트면 `InterruptMismatch` 반환(funcnotes_ipt).
- **v3.7 신설 `ApiBuffer::GetCumulativeBlockCount`**: API 버퍼 처리와 동기화된 블록 카운트 —
  오류 로그에서 **어느 API 호출이 실패했는지 식별**하는 용도(릴리즈노트). `GetStatus`와 달리
  블록 추가 직후에도 최신값이 보장된다.
- Watchdog(`SetWatchdog`/`ResetWatchdogTimer` — funcnotes_special에서 함수명 확인)으로 앱 정지 시
  엔진 측 안전 동작을 구성할 수 있다 — 구성 상세는 매뉴얼 Watchdog 토픽과 API Reference에서
  시그니처 확인.

## 8. 에러 처리 체크리스트 (구현 완료 전 확인)

- [ ] 모든 WMX3 호출의 반환값을 확인하는가 (버리는 호출 없음)
- [ ] 오류 메시지에 오류 코드 정수 + `ErrorToString` 문자열을 함께 남기는가
- [ ] 오류 경로에서 서보 오프 → StopCommunication → CloseDevice(→ Dispose) 정리가 보장되는가
- [ ] 오류코드 정수 리터럴 비교/매핑이 없는가 (§6 grep 통과)
- [ ] 재시도 로직에 최대 횟수/타임아웃이 있는가 (무한 재시도 없음)
- [ ] Wait 계열에 타임아웃을 지정했는가 (`WaitTimeout` 처리 포함)

---
출처: WMX3.7 매뉴얼 미러 `kr/guide/general/tutorial/tutorial1/4`·`tutorial2/4`,
`kr/guide/general/funcnotes/`, `kr/guide/motion/basic_motion/wait/wait_timeout`,
`kr/release-notes/index.html`(오류코드 시프트·ApiBuffer 사양). 다이제스트: `wmx37-user-manual-kr` §변경 요약,
`wmx3-user-manual-kr` §5 오류 코드.
