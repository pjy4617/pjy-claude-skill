# WMX3.7 C# (.NET) 구현 가이드

WMX3 C++ 라이브러리에서 호출할 수 있는 거의 모든 함수는 .NET 라이브러리(WMX3ApiCLR)에서도 호출할 수
있으며, 대부분 이름과 인터페이스가 동일하다. 이 문서는 C# 프로젝트 설정과 **C++↔.NET 차이**,
그리고 .NET 고유의 함정(Dispose/GC)을 정리한다.
(근거: WMX3.7 매뉴얼 미러 `kr/guide/general/tutorial/tutorial2/`,
`kr/guide/general/supplemental/cpp_vs_net/`)

> API Reference는 C++ 인터페이스 기준으로 기술된다 — .NET에서 사용할 때는 아래 §3의 변환 규칙을 적용.

## 1. 프로젝트 설정 (Visual Studio)

- C# **콘솔 응용 프로그램** 템플릿으로 시작 (튜토리얼 2-1 기준).
- 64비트 WMX3(RTX64 사용 시)이면 플랫폼을 **Any CPU → x64**로 변경.
- References → Add Reference → Browse에서 `C:\Program Files\SoftServo\WMX3\Lib`의 CLR DLL 참조 추가:

```text
AdvancedMotionApi_CLRLib.dll
ApiBufferApi_CLRLib.dll
CompensationApi_CLRLib.dll
CoreMotionApi_CLRLib.dll
CyclicBufferApi_CLRLib.dll
EventApi_CLRLib.dll
IOApi_CLRLib.dll
LogApi_CLRLib.dll
UserMemoryApi_CLRLib.dll
WMX3Api_CLRLib.dll
```

- **WMX3Api_CLRLib.dll을 제외한 나머지는 선택 사항** — 해당 모듈 함수를 쓰지 않으면 생략 가능.
- **IMDll.dll이 실행 파일과 동일 디렉토리에 없으면 실행 직후 예외 발생.** 포스트 빌드 이벤트로 복사:

```text
copy /y "C:\Program Files\SoftServo\WMX3\lib\IMDll.dll" "$(TargetDir)"
```

- 소스 파일 상단에 네임스페이스 선언:

```csharp
using WMX3ApiCLR;
```

## 2. Dispose 규칙 (.NET 최대 함정)

- `WMX3Api`와 각 모듈의 메인 클래스(`CoreMotion` 등)는 **IDisposable을 상속**한다.
- 인스턴스마다 객체를 해방할 수 있을 때 `Dispose()`를 호출해야 하며, 이는 통상
  **`CloseDevice` 호출 직후**다(닫힌 디바이스로 이후 `CreateDevice`를 다시 호출하지 않는 한).
- **적절한 시점에 `Dispose`를 호출하지 않으면 .NET 가비지 컬렉터가 비관리 리소스를 조기에 해제하여
  정의되지 않은 동작이 발생할 수 있다.** (보충정보 IDisposable 원문 강조)
- 순서 (튜토리얼 2-6/보충정보 확인):

```csharp
WMX3Api wmxlib = new WMX3Api();
CoreMotion wmxlib_cm = new CoreMotion(wmxlib);
wmxlib.CreateDevice("C:\\Program Files\\SoftServo\\WMX3", DeviceType.DeviceTypeNormal);

// ... wmxlib / wmxlib_cm 함수 호출 ...

wmxlib.CloseDevice();     // 1) 디바이스 닫기
wmxlib_cm.Dispose();      // 2) 모듈 객체 Dispose
wmxlib.Dispose();         // 3) WMX3Api Dispose
```

- 예외 경로에서도 위 순서가 보장되도록 `try { ... } finally { CloseDevice → Dispose }` 구성을 권장.
  C#의 `using` 문은 블록 종료 시 `Dispose`만 호출하므로, **`CloseDevice`를 `Dispose` 전에 명시적으로
  호출하는 코드가 반드시 있어야** 한다(없으면 엔진 프로세스가 잔존).

## 3. C++↔.NET 차이 10항목 (supplemental/cpp_vs_net 확인)

| # | 항목 | C++ | .NET |
|---|------|-----|------|
| 1 | IDisposable | 없음 | `WMX3Api`/모듈 클래스는 IDisposable — `Dispose` 필수 (§2) |
| 2 | 네임스페이스 | `wmx3Api`, `wmx3Api::simuApi` | `WMX3ApiCLR`, `WMX3ApiCLR.SimuApiCLR` — 첫 글자 대문자 + `CLR` 접미 규칙 |
| 3 | 멤버 변수 | 소문자 시작 (`profile.velocity`) | **첫 글자 대문자** (`Profile.Velocity`) |
| 4 | 문자열 인수 | `char*`/`wchar_t*` 오버로드 2개 | `String` 1개 (예: `SetDeviceName(String name)`) |
| 5 | 디폴트 매개변수 | 인수 기본값 (`CreateDevice(path, type, waitTime = 0, core = -1, affinityMask = 0)`) | 기본값 대신 **오버로드 함수** 제공 — 생략 시 C++과 같은 기본값 |
| 6 | 공용체(union) | `trig.input.ioBit.byteAddress` | 멤버별 클래스 + 프로퍼티: `trig.Input_IOBit.ByteAddress` (최초 액세스 시 인스턴스화) |
| 7 | 배열 크기 인수 | 배열 + 크기 인수 별도 | 배열 객체에 크기 포함 — 크기 인수 생략 (예: `UploadSDO`) |
| 8 | 상수 | `constants::maxAxes` (전역) | `Constants.MaxAxes`, 모듈 상수는 `[모듈명]Constants` 클래스 (예: `ApiBufferConstants`) |
| 9 | String 반환 | 인수로 반환: `ErrorToString(int, char*, uint)` | 반환값으로 반환: `static String ErrorToString(int errCode)` (`ApiLogToString`/`TimestampToString`도 동일) |
| 10 | FILE 클래스 | `FILE` 사용 | `WMX3ApiCLR.WMX3File` 클래스로 캡슐화 |

## 4. 초기화/종료 시퀀스 골격 (튜토리얼 2-7 기반)

```csharp
using System;
using WMX3ApiCLR;

namespace WMX3App
{
	class Program
	{
		static void Main(string[] args)
		{
			WMX3Api wmxlib = new WMX3Api();
			CoreMotion wmxlib_cm = new CoreMotion(wmxlib);   // 모듈 클래스 생성자에 WMX3Api 전달
			int err;
			int counter;
			CoreMotionStatus st = new CoreMotionStatus();
			Motion.PosCommand pos = new Motion.PosCommand();

			// 1) 디바이스 생성
			err = wmxlib.CreateDevice("C:\\Program Files\\SoftServo\\WMX3", DeviceType.DeviceTypeNormal);
			if (err != ErrorCode.None) {
				Console.WriteLine("Failed to create device. Error={0} ({1})", err, WMX3Api.ErrorToString(err));
				goto exit;
			}

			// 2) 통신 개시 (최대 5초 대기)
			err = wmxlib.StartCommunication(5000);
			if (err != ErrorCode.None) {
				Console.WriteLine("Failed to start communication. Error={0} ({1})", err, WMX3Api.ErrorToString(err));
				goto exit;
			}

			// 3) 서보 온 — .NET은 중첩 클래스가 아닌 대문자 프로퍼티 접근 (AxisControl)
			err = wmxlib_cm.AxisControl.SetServoOn(0, 1);   // 축 0 서보 온
			if (err != ErrorCode.None) {
				Console.WriteLine("Failed to set servo on. Error={0} ({1})", err, CoreMotion.ErrorToString(err));
				goto exit;
			}

			// 4) 서보 온 완료 폴링 (몇 사이클 지연 가능) — .NET은 ref 인수 + bool 멤버
			counter = 1000;   // 무한 루프 방지 카운터
			do {
				err = wmxlib_cm.GetStatus(ref st);
				if (err != ErrorCode.None) {
					Console.WriteLine("Failed to get status. Error={0} ({1})", err, CoreMotion.ErrorToString(err));
					goto exit;
				}
				System.Threading.Thread.Sleep(10);
				counter--;
			} while (counter > 0 && st.AxesStatus[0].ServoOn == false);

			// 5) 모션 지령 — 멤버 첫 글자 대문자 (Axis/Profile/Target)
			pos.Axis = 0;
			pos.Profile.Type = ProfileType.Trapezoidal;
			pos.Profile.Velocity = 10000;
			pos.Profile.Acc = 10000;
			pos.Profile.Dec = 10000;
			pos.Target = 10000;
			err = wmxlib_cm.Motion.StartMov(pos);   // .NET은 포인터 대신 객체 전달
			if (err != ErrorCode.None) {
				Console.WriteLine("Failed to execute motion. Error={0} ({1})", err, CoreMotion.ErrorToString(err));
				goto exit;
			}

			// 모션 완료까지 블로킹 대기 — C++ 골격의 motion->Wait(0)과 동일 (cpp-implementation.md §3).
			// Wait는 CoreMotion의 완료 대기 API(근거: 미러 kr/python-api/method_coremotion.html),
			// .NET 표기는 §3-3 규칙에 따라 Motion. 프로퍼티 경유
			err = wmxlib_cm.Motion.Wait(0);
			if (err != ErrorCode.None) {
				Console.WriteLine("Failed to wait motion. Error={0} ({1})", err, CoreMotion.ErrorToString(err));
				goto exit;
			}

		exit:
			// 6) 종료 역순: 모션 정지 확인 → 서보 오프 → 통신 정지 → 디바이스 닫기 → Dispose (오류 경로에서도 반드시 통과)
			//    [플러그인 확장] 튜토리얼 2-7 원문은 통신 정지→닫기만 수행하는 단순화 —
			//    서보 온 이후 오류로 진입한 경우에도 모션 정지·서보 오프가 StopCommunication에
			//    선행하도록 보강한다 (SKILL.md 필수 골격, error-handling.md §5·§8)
			wmxlib_cm.Motion.Stop(0);                 // 모션 정지 (C++ §5 표의 motion->Stop — §3-3 표기 규칙)
			//    정지 완료는 GetStatus 폴링(카운터 상한)으로 확인한 뒤 서보 오프한다 (4)의 폴링과 동일 패턴)
			wmxlib_cm.AxisControl.SetServoOn(0, 0);   // 서보 오프 — 통신 정지는 서보 오프 후

			// 7) 통신 정지 → 디바이스 닫기 → Dispose (모듈 → WMX3Api 순)
			err = wmxlib.StopCommunication();
			if (err != ErrorCode.None) {
				Console.WriteLine("Failed to stop communication. Error={0} ({1})", err, WMX3Api.ErrorToString(err));
			}
			err = wmxlib.CloseDevice();
			if (err != ErrorCode.None) {
				Console.WriteLine("Failed to close device. Error={0} ({1})", err, WMX3Api.ErrorToString(err));
			}
			wmxlib_cm.Dispose();
			wmxlib.Dispose();
		}
	}
}
```

C++ 골격과의 차이 요약:
- `axisControl->` → `AxisControl.`, `motion->` → `Motion.` (멤버 첫 글자 대문자, §3-3)
- `GetStatus(&st)` → `GetStatus(ref st)`, `servoOn == 0` → `ServoOn == false`
- `ErrorToString(err, buf, size)` → `WMX3Api.ErrorToString(err)` / `CoreMotion.ErrorToString(err)`
  (static, String 반환, §3-9)
- 종료 시 `Dispose` 2회(모듈 → WMX3Api) 추가
- 모션 완료 대기는 C++과 동일한 `Wait(0)` 블로킹 — `motion->Wait(0)` ↔ `Motion.Wait(0)`(§3-3 표기).
  고정 `Thread.Sleep` 대기로 완료를 가정하지 않는다(§4 골격 참조)

## 5. GC 함정 체크리스트

- [ ] 모든 `WMX3Api`/모듈 객체에 대해 `CloseDevice` → `Dispose` 경로가 예외 시에도 실행되는가
  (`try/finally` 권장)
- [ ] `Dispose` 이후 해당 객체(및 그 `WMX3Api`를 받은 모듈 객체)를 다시 사용하지 않는가
- [ ] 장수명 객체(폼/서비스 필드)로 보관해 GC 조기 수집을 유발하는 임시 지역 변수 남발이 없는가
- [ ] 스레드마다 자신의 `WMX3Api` + `CreateDevice`를 사용하는가 (C++과 동일 규칙 — 튜토리얼 2-2)

## 6. 이벤트/콜백 패턴

- 이벤트 입력/출력 구성은 `EventControl` 모듈이 담당한다(다이제스트 §5 기타 기능 — 이벤트).
  `EventControl.SetEvent`는 메모리를 동적으로 할당하므로 **초기화 단계에서 등록**한다
  (`funcnotes_mem` — cpp-implementation.md §9 참조).
- 트리거/이벤트 조건 클래스는 C++ 공용체 대신 .NET에서는 프로퍼티 인터페이스를 쓴다(§3-6):

```csharp
TriggerEvent trig = new TriggerEvent();
// Input_IOBit는 공용체 멤버 대용 클래스에 액세스하는 프로퍼티
trig.Input_IOBit.ByteAddress = 10;
trig.Input_IOBit.BitAddress = 2;
trig.InputFunction = TriggerEventInputFunction.IOBit;
```

- .NET 델리게이트/콜백 형태의 통지 API 존재 여부와 시그니처는 원문 튜토리얼에서 확인되지 않음 —
  사용 전 **API Reference(EventControl 클래스)에서 시그니처 확인**. 확인 전에는 `GetStatus`/`Wait`
  기반 폴링·대기 패턴(§4)을 기본으로 한다.

---
출처: WMX3.7 매뉴얼 미러 `kr/guide/general/tutorial/tutorial2/1~7`,
`kr/guide/general/supplemental/cpp_vs_net/*`(IDisposable·네임스페이스·멤버 변수·문자열·디폴트
매개변수·공용체·배열 크기·상수·String 반환·FILE). 다이제스트: `wmx37-user-manual-kr`, `wmx3-user-manual-kr`.
