# WMX3.7 C++ 구현 가이드

WMX3 라이브러리의 주요 언어는 C++이다. 이 문서는 WMX3 API를 호출하는 **응용 프로그램**(비RT 사용자 앱)의
C++ 구현 패턴을 정리한다. (근거: WMX3.7 매뉴얼 미러 `kr/guide/general/tutorial/tutorial1/`,
`tutorial3/`, `kr/guide/general/funcnotes/`, `kr/guide/motion/basic_motion/wait/`)

> 엔진에 로드되는 rtdll 모듈 개발(C99 Core)은 이 문서의 범위가 아니다 — wmx3md 플러그인 참조.

## 1. 프로젝트 설정 (Visual Studio)

- Visual C++ **Win32 콘솔 응용 프로그램** 템플릿으로 시작 (튜토리얼 1-1 기준).
- 64비트 WMX3(RTX64 사용 시)이면 Configuration Manager에서 플랫폼을 **Win32 → x64**로 변경.
- 인클루드 경로: `C:\Program Files\SoftServo\WMX3\Include`
- 라이브러리 경로: `C:\Program Files\SoftServo\WMX3\Lib`
- 링크 라이브러리 (Additional Dependencies):

```text
AdvancedMotionApi.lib
ApiBufferApi.lib
CompensationApi.lib
CoreMotionApi.lib
CyclicBufferApi.lib
EventApi.lib
IMDll.lib
IOApi.lib
LogApi.lib
UserMemoryApi.lib
WMX3Api.lib
```

- **IMDll.lib와 WMX3Api.lib를 제외한 나머지는 선택 사항** — 해당 모듈 함수를 쓰지 않으면 생략 가능.
- Visual Studio 2015 이상: `legacy_stdio_definitions.lib`, `legacy_stdio_wide_specifiers.lib` 추가.
- **IMDll.dll이 응용 프로그램 디렉토리에 없으면 동작하지 않는다.** 포스트 빌드 이벤트로 자동 복사 권장:

```text
copy /y "C:\Program Files\SoftServo\WMX3\lib\IMDll.dll" "$(OutDir)"
```

- 사용할 모듈의 헤더를 포함:

```cpp
#include "AdvancedMotionApi.h"
#include "ApiBufferApi.h"
#include "CompensationApi.h"
#include "CoreMotionApi.h"
#include "CyclicBufferApi.h"
#include "EventApi.h"
#include "IOApi.h"
#include "LogApi.h"
#include "UserMemoryApi.h"
#include "WMX3Api.h"
```

## 2. 디바이스 모델

- 디바이스 = WMX3 엔진과의 통신 채널을 연 `WMX3Api` 클래스 객체.
- **WMX3 API 함수를 호출하는 각 스레드는 자신의 `WMX3Api` 객체를 만들고 `CreateDevice`를 호출**해야 한다.
- 모든 클래스/상수는 `wmx3Api` 네임스페이스에 있다.
- `CreateDevice` 1번째 인수 = `WMX3Engine.rtss`가 있는 디렉토리 절대 경로(기본
  `C:\Program Files\SoftServo\WMX3`), 2번째 인수 = `DeviceType::DeviceTypeNormal`.
- 디바이스를 만든 모든 `WMX3Api` 객체는 종료 전 **반드시 `CloseDevice`** — 닫지 않으면 앱 종료 후에도
  WMX3 엔진 프로세스가 계속 실행된다(StopEngine 수동 종료 필요, 비권장).
- C++ 시그니처(보충정보 확인): `CreateDevice(const char* path, DeviceType::T type, unsigned int waitTimeMilliseconds = 0, int core = -1, DWORD_PTR affinityMask = 0)`

## 3. 초기화/종료 시퀀스 골격 (튜토리얼 1-7 기반)

```cpp
#include "CoreMotionApi.h"
#include "WMX3Api.h"

int _tmain(int argc, _TCHAR* argv[])
{
	using namespace wmx3Api;
	WMX3Api wmxlib;
	CoreMotion wmxlib_cm(&wmxlib);   // 모듈 클래스 생성자에 WMX3Api 객체 전달
	int err;
	char errString[256];
	CoreMotionStatus st;
	int counter;
	Motion::PosCommand pos;

	// 1) 디바이스 생성
	err = wmxlib.CreateDevice(_T("C:\\Program Files\\SoftServo\\WMX3"), DeviceType::DeviceTypeNormal);
	if (err != ErrorCode::None) {
		wmxlib.ErrorToString(err, errString, sizeof(errString));
		printf("Failed to create device. Error=%d (%s)\n", err, errString);
		goto exit;
	}

	// 2) 통신 개시 (최대 5초 대기) — 성공 시 Engine State = Communicating
	err = wmxlib.StartCommunication(5000);
	if (err != ErrorCode::None) {
		wmxlib.ErrorToString(err, errString, sizeof(errString));
		printf("Failed to start communication. Error=%d (%s)\n", err, errString);
		goto exit;
	}

	// 3) 서보 온 — 통신 직후 전 축은 서보 오프 상태
	err = wmxlib_cm.axisControl->SetServoOn(0, 1);   // 축 0 서보 온
	if (err != ErrorCode::None) {
		wmxlib_cm.ErrorToString(err, errString, sizeof(errString));
		printf("Failed to set servo on. Error=%d (%s)\n", err, errString);
		goto exit;
	}

	// 4) 서보 온 완료를 GetStatus 폴링으로 확인 (몇 사이클 지연될 수 있음)
	counter = 1000;   // 무한 루프 방지 카운터
	do {
		err = wmxlib_cm.GetStatus(&st);
		if (err != ErrorCode::None) {
			wmxlib_cm.ErrorToString(err, errString, sizeof(errString));
			printf("Failed to get status. Error=%d (%s)\n", err, errString);
			goto exit;
		}
		Sleep(10);
		counter--;
	} while (counter > 0 && st.axesStatus[0].servoOn == 0);

	// 5) 모션 지령 (사다리꼴 프로파일, 상대 이동)
	pos.axis = 0;
	pos.profile.type = ProfileType::Trapezoidal;
	pos.profile.velocity = 10000;
	pos.profile.acc = 10000;
	pos.profile.dec = 10000;
	pos.target = 10000;
	err = wmxlib_cm.motion->StartMov(&pos);
	if (err != ErrorCode::None) {
		wmxlib_cm.ErrorToString(err, errString, sizeof(errString));
		printf("Failed to execute motion. Error=%d (%s)\n", err, errString);
		goto exit;
	}

	// 모션 완료까지 블로킹
	err = wmxlib_cm.motion->Wait(0);

exit:
	// 6) 종료는 역순: 모션 정지 확인 → 서보 오프 → 통신 정지 → 디바이스 닫기 (오류 경로에서도 반드시 통과)
	//    [플러그인 확장] 튜토리얼 1-7 원문은 통신 정지→디바이스 닫기만 수행하는 단순화 —
	//    서보 온 이후 오류로 진입한 경우에도 모션 정지·서보 오프가 StopCommunication에 선행하도록
	//    보강한다 (SKILL.md 필수 골격, error-handling.md §5·§8). CreateDevice 성공 전 실패로
	//    진입한 경우 모듈 함수는 오류만 반환하므로(아래 핵심 규칙) 정리 경로에서 그대로 호출해도 안전.
	wmxlib_cm.motion->Stop(0);   // 모션 정지 (Stop — §5 표, 미러 tutorial3. 필요 시 ExecQuickStop)
	//    정지 완료는 GetStatus 폴링(카운터 상한)으로 확인한 뒤 서보 오프한다 (4)의 서보 온 폴링과 동일 패턴)
	wmxlib_cm.axisControl->SetServoOn(0, 0);   // 서보 오프 — 통신 정지는 서보 오프 후에 실시 (튜토리얼 1-6)

	// 7) 통신 정지 → 디바이스 닫기
	err = wmxlib.StopCommunication();
	if (err != ErrorCode::None) {
		wmxlib.ErrorToString(err, errString, sizeof(errString));
		printf("Failed to stop communication. Error=%d (%s)\n", err, errString);
	}
	err = wmxlib.CloseDevice();
	if (err != ErrorCode::None) {
		wmxlib.ErrorToString(err, errString, sizeof(errString));
		printf("Failed to close device. Error=%d (%s)\n", err, errString);
	}
	return 0;
}
```

핵심 규칙:
- 모듈 클래스(`CoreMotion` 등) 객체는 생성자에 `WMX3Api*`를 받고, 그 `WMX3Api`가 `CreateDevice`에
  성공한 뒤에만 모듈 함수를 호출할 수 있다(그 전에 호출하면 오류 반환). `CloseDevice` 후에는
  전달된 모듈 객체의 함수도 실행 불가.
- 서보 온 후 실제 온까지 몇 사이클 지연 가능 → `GetStatus`의 `servoOn` 확인 후 모션 지령.

## 4. 에러 처리 래퍼 패턴

튜토리얼의 `err != ErrorCode::None` + `ErrorToString` + `goto exit` 패턴을 프로젝트 공통
헬퍼/매크로로 일관화한다. 상세 원칙(재시도 vs 중단, 오류코드 시프트)은 `error-handling.md` 참조.

```cpp
// WMX3 호출 결과를 검사하고 실패 시 정리 라벨로 점프하는 공통 매크로 예
#define WMX3_CHECK(call, modObj, label)                                   \
	do {                                                                  \
		err = (call);                                                     \
		if (err != wmx3Api::ErrorCode::None) {                            \
			(modObj).ErrorToString(err, errString, sizeof(errString));    \
			printf("[WMX3] %s failed. Error=%d (%s)\n", #call, err, errString); \
			goto label;                                                   \
		}                                                                 \
	} while (0)
```

- `ErrorToString`은 각 모듈 클래스마다 정의된다 — 해당 모듈의 오류는 해당 모듈 클래스의
  `ErrorToString`으로 변환한다(예: CoreMotion 오류는 `wmxlib_cm.ErrorToString`).
- C++ 시그니처(보충정보 확인): `static long ErrorToString(int errCode, char* pString, unsigned int size)` (wchar_t 오버로드 있음).

## 5. 기본 모션 패턴 (튜토리얼 3 기반)

| 목적 | API | 비고 |
|------|-----|------|
| 절대 위치 이동 | `motion->StartPos(&pos)` | `pos.target` = 절대 좌표 |
| 상대 이동 | `motion->StartMov(&pos)` | `pos.target` = 이동량 |
| 완료 대기 | `motion->Wait(axis)` | 블로킹 — 아래 §6 |
| 정지 | `motion->Stop(axis)`, `ExecQuickStop`, `ExecTimedStop` | StartPos의 프로파일/감속도로 정지 |
| 오버라이드 | 동일 유형 모션 지령 재발행 | 속도 유지된 채 새 목표/프로파일 적용 |
| 선형 보간 | `motion->StartLinearIntplPos(&lin)` | `Motion::LinearIntplCommand` (axisCount/axis[]/target[]) |
| 원호 보간 | `motion->StartCircularIntplPos(&cir)` | `Motion::LengthAndEndCircularIntplCommand` |
| 속도 지령 | `velocity->StartVel(&vel)` / `velocity->Stop(axis)` | 먼저 `axisControl->SetAxisCommandMode(axis, AxisCommandMode::Velocity)` |
| 토크 지령 | `torque->StartTrq(&trq)` / `torque->StopTrq(axis)` | `AxisCommandMode::Torque` 필요. v3.7 `TrqCommand`는 빌더 패턴 — `v37-migration.md` ② 참조 |
| 파라미터 R/W | `config->GetParam(&param)` / `config->SetParam(&param)` | 엔진 종료 시 파라미터 소실 — 파일 저장 필요 |
| 파라미터 파일 | `config->Import`/`Export`, `config->ImportAndSetAll`/`GetAndExportAll` | XML. **관리자 권한 필요**(파일 권한 없으면 오류 반환) |

- 프로파일 필수 입력(사다리꼴): `profile.type/velocity/acc/dec`. 시작/종료 속도는 옵션
  (Profile 생성자가 0으로 초기화). 프로파일 26종은 매뉴얼 `kr/guide/motion/profile/` 참조.
- 위 표의 구조체 멤버 구성은 튜토리얼 코드에서 확인된 것만 기재 — 그 외 명령 클래스의
  정확한 시그니처는 **API Reference에서 시그니처 확인** 후 사용할 것.

## 6. 블로킹/논블로킹 함수 구분 (funcnotes_blk 확인)

- 별도 명시가 없는 한 WMX3 함수는 **비블로킹**(수 마이크로초 이내 반환).
- 블로킹하는 것:
  - `CoreMotion`의 `Wait` 함수(오버로드 다수) — 조건 충족까지 호출 스레드 중단. **의도적 블로킹**.
  - "API는 모션 시작까지 대기(Wait Until Motion Start)" 파라미터가 TRUE(기본값)이면
    `StartPos`/`StartMov`/보간/`Stop`/`Override*`/`StartVel`/`StartTrq` 등 대부분의 모션 함수가
    다음 인터럽트 끝까지 블로킹. FALSE면 모션 시작 후 첫 인터럽트 종료 전에 오버라이드를 호출할 때
    `StartingPreviousCommand` 오류 가능 → Command Ready 상태 확인 필요.
  - `Compensation::SetPitchErrorCompensation`/`EnablePitchErrorCompensation`/
    `Set2DPitchErrorCompensation`/`Enable2DPitchErrorCompensation` — 다음 인터럽트 끝까지 블로킹.
  - `ApiBuffer`의 `Execute`/`Halt`/`Clear`/`Rewind` — 모드 변경 완료(통상 1ms) 또는
    타임아웃(50ms)까지 블로킹.
  - `RemoveEvent`/`ClearAllEvent` — 다음 인터럽트 끝까지 블로킹(통신 정지 중이면 즉시).
  - 예측 경로 보간 `AddPathIntplWithRotationCommand` — 점 수에 따라 수백 ms~수 초 블로킹 가능.
- 일부 Wait 함수에는 대기 타임아웃 매개변수가 있고 초과 시 `WaitTimeout` 오류 반환 —
  **무한 대기 방지를 위해 타임아웃 지정 권장**.

## 7. 멀티스레드 주의 (wait_multithread 확인)

- `Wait`는 **호출한 스레드를 정지**시킨다. 싱글 스레드 GUI 앱에서 호출하면 대기 종료까지 GUI가 멈춤.
- 모션 지령과 `Wait` 호출만을 담당하는 **별도 스레드**를 두는 구성을 권장.
- 각 스레드는 자신의 `WMX3Api` 객체 + `CreateDevice`로 디바이스를 취득한다(§2).
- `Wait`는 함수를 호출한 디바이스의 인터럽트에 동기되어, 조건 충족 사이클의 인터럽트 루틴 직후 반환.
- `Wait`는 동기(Synchronization)·E-CAM의 슬레이브 축에는 사용할 수 없다.

## 8. 인터럽트 영향 주의 (funcnotes_blk·funcnotes_ipt 확인)

- 엔진이 인터럽트(사이클릭 핸들러)를 처리하는 도중에 API를 호출하면 인터럽트 종료까지 실행이 지연된다.
- 지연 없이 실행되는 함수: `ErrorToString`(전 모듈), `GetLibVersion`, `WMX3Api::GetIMDllVersion`,
  `CoreMotion::GetStatus`, `Io`의 `...Ex` 접미어 고속 I/O 함수군(`SetOutBitEx`/`GetInBitEx` 등).
- 회피책: `CreateDevice`의 `affinityMask` 인수로 RTX에 2코어 이상 할당 —
  **2코어 이상 지원 RTX 라이선스 필요**.
- 보간·동기 계열 함수(`StartLinearIntplPos`, `SetSyncMasterSlave`, `StartPVT`, `StartEcam` 등)는
  지령하는 모든 축이 같은 인터럽트에 있지 않으면 `InterruptMismatch` 오류를 반환한다 —
  멀티 인터럽트 구성 시 축 배치에 주의.

## 9. 메모리 할당 함수 주의 (funcnotes_mem 확인)

- 장시간 안정 가동을 위해 **필요 메모리는 초기화 단계에서 전부 확보**하고 운전 중에는
  확보/해제하지 않는다.
- 동적으로 메모리를 **할당**하는 함수 — 초기화 단계에서만 호출:
  `WMX3Api::CreateDevice`, `ApiBuffer::CreateApiBuffer`, `Log::SetLog`/`SetLogOption`/
  `OpenMemoryLogBuffer`/`SetApiLog`, `EventControl::SetEvent`, `AdvMotion::CreateSplineBuffer`/
  `CreatePathIntplBuffer`/`CreatePathIntplWithRotationBuffer`/`CreatePathIntplLookaheadBuffer`,
  `Motion::CreatePVTBuffer`, `CyclicBuffer::OpenCyclicBuffer`
- 동적으로 메모리를 **해제**하는 함수 — 종료 단계에서만 호출:
  `WMX3Api::CloseDevice`, `ApiBuffer::FreeApiBuffer`, `Log::CloseMemoryLogBuffer`,
  `AdvMotion::FreeSplineBuffer`, `Motion::FreePVTBuffer`, `AdvMotion::FreePathIntplBuffer`/
  `FreePathIntplWithRotationBuffer`/`FreePathIntplLookaheadBuffer`, `CyclicBuffer::CloseCyclicBuffer`
- 이 함수들을 제외하면 WMX3 엔진은 작동 중 메모리를 동적으로 할당/해제하지 않는다.

## 10. 디버깅 팁

- WMX3 콘솔(`C:\Program Files\SoftServo\WMX3\WMX3Console.exe`)로 통신 상태를 확인하면서 디버깅.
- 파라미터를 코드에서 변경한 뒤 WMX3 Console Config 화면에서 확인하려면 Refresh 필요.

---
출처: WMX3.7 매뉴얼 미러 `kr/guide/general/tutorial/tutorial1/1~7`, `tutorial3/1~9`,
`kr/guide/general/funcnotes/funcnotes_blk·funcnotes_ipt·funcnotes_mem`,
`kr/guide/motion/basic_motion/wait/wait_overview·wait_multithread·wait_timeout`,
`kr/guide/general/supplemental/cpp_vs_net/` (시그니처). 다이제스트: `wmx37-user-manual-kr`, `wmx3-user-manual-kr`.
