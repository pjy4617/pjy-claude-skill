# WMX3 애플리케이션 테스트 전략

> **근거**: WMX3.7 다이제스트(`wmx37-user-manual-kr`) / 3.6u3 다이제스트(`wmx3-user-manual-kr`) §4 아키텍처·§5 모션 프로그래밍, 시뮬레이터 장 `kr/guide/simu/`.
> API 함수의 정확한 시그니처는 다이제스트 키워드 인덱스로 API 레퍼런스(Doxygen `api/html/`)를 핀포인트해 확인한다 — 아래 골격의 API 호출은 확인된 함수명만 사용하되 시그니처 세부는 주석으로 표시한다.

## 1. 테스트 피라미드

| 단계 | 대상 | 목적 | 비고 |
|------|------|------|------|
| ① 로직 단위 | WMX3 비의존 앱 로직 (궤적 계산, 시퀀스 상태기계, 파라미터 변환 등) | 빠른 회귀, WMX3 없이 실행 | WMX3 호출부를 인터페이스로 분리해 두면 이 단계가 커진다 |
| ② 시뮬레이터 통합 | WMX3 API 호출 경로 전체 (초기화~모션~이벤트~종료) | 실 HW 없이 시퀀스·모션 로직 리허설 | SimuPlatform — `references/simulator-platform.md` |
| ③ 실기 인수 | 실 서보·센서·안전 계통 | 시뮬레이터가 못 보는 영역(편차·네트워크·기계·안전) | `SKILL.md` 실기 전환 전 체크리스트 선행 필수 |

원칙: ①에서 최대한 걸러내고, ②는 "WMX3와의 계약"(호출 순서·상태·오류 처리)을, ③은 "물리 세계와의 계약"만 검증하도록 역할을 나눈다.

## 2. 픽스처 패턴 (초기화/종료)

WMX3 필수 시퀀스(다이제스트 §4 통신/서보온): `CreateDevice(path, DeviceType)` → `StartCommunication()` → Engine State = `Communicating` 확인 → (통신 직후 전 축 서보 오프이므로) `SetServoOn()` → 테스트 본문 → 역순 정리(`StopCommunication()` → `CloseDevice()`). 상태 확인은 모두 `GetStatus()`.

### C++ (gtest)

```cpp
// 시뮬레이터 통합 테스트 픽스처 골격.
// 정확한 시그니처·인수는 API 레퍼런스(api/html/, wmx3Api 네임스페이스)에서 확인할 것.
class WmxSimuTest : public ::testing::Test {
protected:
    void SetUp() override {
        // 1) CreateDevice(<경로>, DeviceType) — 디바이스 생성. 반환 코드 확인
        // 2) StartCommunication() — 이후 GetStatus()로 Engine State == Communicating을
        //    타임아웃 있는 루프로 확인 (무한 대기 금지)
        // 3) SetServoOn() — 대상 축 서보 온 (통신 직후 전 축은 서보 오프 상태)
        //    각 단계 실패 시 GTEST_SKIP() 또는 FAIL()로 명확히 중단
    }
    void TearDown() override {
        // 역순 정리: 모션 정지 확인 → 서보 오프 → StopCommunication() → CloseDevice()
        //   모션 정지 = Stop(또는 ExecQuickStop) 후 GetStatus 폴링(상한 필수)으로 정지 확인
        //   (Stop/ExecQuickStop — WMX3.7 매뉴얼 CoreMotion 확인됨)
        // 테스트가 실패해도 반드시 실행되도록 TearDown에 배치 (자원 누수 방지)
    }
};
```

### C# (xUnit / NUnit)

```csharp
// xUnit: 클래스 픽스처(IDisposable) / NUnit: [SetUp]·[TearDown]
// ★ .NET(WMX3ApiCLR)은 CloseDevice() 후 Dispose() 호출 필수 —
//    미호출 시 정의되지 않은 동작 (다이제스트 §4 디바이스 모델)
public class WmxSimuFixture : IDisposable
{
    public WmxSimuFixture()
    {
        // CreateDevice → StartCommunication → 상태 확인 → SetServoOn (반환 코드 확인)
    }
    public void Dispose()
    {
        // 모션 정지 확인 → 서보 오프 → StopCommunication() → CloseDevice() → 디바이스 객체 Dispose()
    }
}
```

픽스처 공통 규칙:

- 모든 WMX3 호출의 **반환 코드를 확인**하고, 준비 실패는 테스트 실패와 구분해 보고
- 모든 대기(통신 개시·모션 완료·이벤트)는 **타임아웃 필수**
- 테스트 간 상태 오염 방지: 각 테스트 후 축 정지·서보 상태 원복, 또는 픽스처를 테스트 단위로 재생성

## 3. 모션 판정 기준

| 판정 | 방법 | 유의 |
|------|------|------|
| 위치 도달 | `GetStatus()`의 지령 위치(Pos Cmd)·피드백 위치(Actual Pos)를 목표와 비교 | 시뮬레이터 기본 구성은 피드백 = 지령 복사(편차 0)이므로 epsilon은 부동소수점·단위 변환 오차 수준으로 충분. 실기용 허용 오차(서보 편차 반영)는 별도 상수로 분리 |
| 상태 천이 | Engine State(`Communicating` 등)·서보 온 상태·모션 중/완료 상태를 `GetStatus()`로 확인 | 폴링 시 반드시 타임아웃, 주기적 Sleep으로 바쁜 대기 회피 |
| 오류 코드 | 반환 코드를 **심볼 상수와 비교** | 정수 하드코딩 금지 — v3.7에서 API버퍼 오류코드 값 시프트(예: `AlreadyRecordingForSpecifiedChannel` 73734→73735, 릴리즈 노트) |
| 시간 조건 | 모션 소요 시간 상한/하한 | 시뮬레이터 타이머 기반이므로 미세 타이밍 검증은 참고치로만 (실기와 다름) |

## 4. 시나리오 설계

| 시나리오 | 구성 | 검증 포인트 |
|----------|------|-------------|
| 초기화/종료 | 픽스처 자체 + 실패 경로(잘못된 경로로 CreateDevice 등) | 반환 코드 처리, 정리 경로 |
| 원점복귀 | `simu_network.def`에서 `UserDef=1` + `HSFb`(홈 스위치)·`LSPFb`/`LSNFb`(리미트) IO 매핑 → 테스트 중 SimuApi `SetIn*`으로 스위치 신호 주입 → `StartHome` | 원점 완료 상태 천이, Home Offset 반영 위치, 리미트 도달 시 처리 |
| 모션 프로파일 | 앱이 사용하는 프로파일별 단축 이동 (26종 전수 아님 — 사용분만) | 목표 도달, 완료 상태 |
| 보간 궤적 | 선형·원호·헬리컬 등 사용 보간의 대표 궤적 | 종점·경유점 위치, 다축 동기 |
| 이벤트/ApiBuffer | 입력 조건→출력 동작, 버퍼 기록·실행·Wait/FlowIf 분기 | 실행 순서, 조건 분기 결과 |
| 에러 주입 | `AlmFb`/`AlmCode` 매핑 + `SetIn*` 주입으로 알람 발생, 리미트 트립 주입 | 앱의 오류 처리 경로: 정지·서보 오프·복구·운영자 보고 |

## 5. 에러 주입 (SimuApi SetIn*)

SimuApi의 `SetIn***`(Bit/Byte/Bytes/Bits) 함수는 원래 읽기 전용인 IO Input 주소에 쓰기를 가능하게 한다(출처: `kr/guide/simu/precautions.html`). `simu_network.def`의 축 피드백 IO 매핑(`HSFb`/`LSPFb`/`LSNFb`/`AlmFb`/`AlmCode` 등)과 조합하면:

1. 축 피드백 소스를 IO 입력 주소에 매핑 (`references/simulator-platform.md` §3)
2. 테스트 코드에서 `SetIn*`으로 해당 주소에 값 주입 → 홈/리미트 스위치 ON, 알람 발생을 모의
3. 앱의 반응(정지·오류 처리·복구)을 `GetStatus()`·오류 코드로 판정

주의:

- 멀티 마스터(Simu + EtherCAT) 구성에서는 동일 IO Input 주소에 대한 플랫폼 간 데이터 간섭 가능 — 주소 영역 분리 (출처: `kr/guide/simu/precautions.html`)
- 주입 코드는 테스트 전용으로 격리하고, 실기 전환 전에 프로덕션 경로에 남아 있지 않은지 Grep으로 확인 (`SKILL.md` 체크리스트 7)

## 6. CI에서 시뮬레이터 활용

- 시뮬레이터 플랫폼은 **NIC·실 HW가 불필요**하므로(출처: `kr/guide/simu/supported_nic.html`) 물리 장비 없는 러너에서 통합 테스트(피라미드 ②)를 자동화할 수 있다.
- 단, WMX3 엔진 실행 환경(엔진 설치·리얼타임 OS 구성·라이선스)은 여전히 필요하다 — 일반 클라우드 러너가 아닌 **엔진 환경을 갖춘 셀프호스티드 러너**를 상정한다 (환경 요건은 다이제스트 §2 지원 사양·§3 설치/환경설정 참조).
- 권장 파이프라인: PR마다 로직 단위(①) → 엔진 러너에서 시뮬레이터 통합(②) → 릴리즈 게이트로 실기 인수(③, 수동 + 체크리스트).
- 시뮬레이터 구성 파일(`Module.ini` 플랫폼 섹션, `simu_network.def`)은 테스트 리포지토리에 버전 관리하고, 테스트 리포트에 CommCycle·축 수 등 환경을 함께 기록한다.
