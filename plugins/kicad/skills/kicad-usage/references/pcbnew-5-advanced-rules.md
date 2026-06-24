# PCB 에디터 ⑤ — 고급(커스텀 디자인룰·텍스트변수·스크립팅) — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html

> **범위**: Configuration/Customization(설정 파일·hotkey·색상테마), Text variables, Text expressions, Graphical design rule editor, Custom design rules(.kicad_dru 문법·constraint/condition 토큰·예제), Scripting(Python API), IDF component outlines

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#<anchor>

## 목차

- [Advanced topics (개요)](#advanced_topics) — 고급 기능 챕터 개요
- [Configuration and Customization](#configuration-and-customization) — Preferences 다이얼로그(Display/Editing/Colors/Action plugins/Origin & axes)
- [Text variables](#text-variables) — `${VAR}` 치환, 프로젝트/시스템 변수 테이블
- [Text expressions](#text-expressions) — `@{expr}` 평가, 수학/불리언/문자열/날짜/VCS 함수
- [Graphical design rule editor](#graphical-design-rule-editor) — 폼 기반 룰 편집기, 제약 레퍼런스, 예제
- [Custom design rules](#custom-design-rules) — `.kicad_dru` s-expression 문법, constraint/condition 토큰, 속성·함수, From-To, 예제 룰 모음
- [Scripting](#scripting) — `pcbnew` Python API, 콘솔, 액션 플러그인, Footprint wizard
- [IDF component outlines](#idf-component-outlines) — IDF 모델 부착, `.idf` 파일 작성, idfcyl/idfrect/dxf2idf/idf2vrml 툴

---

## Advanced topics (개요) · #advanced_topics

PCB 에디터 **고급** 기능 묶음 챕터: 설정/커스터마이즈, Text variables/expressions, 디자인 룰 편집(그래픽/커스텀 .kicad_dru), Python 스크립팅, IDF 컴포넌트 아웃라인.

## Configuration and Customization · #configuration-and-customization

- PCB 에디터의 환경설정은 Preferences 다이얼로그에서 구성하며, 사용자 설정 디렉토리에 저장되고 KiCad 마이너 버전별로 독립적이다(여러 버전 병행 실행 가능).
- 첫 세 섹션(Common, Mouse and Touchpad, Hotkeys)은 모든 KiCad 프로그램 공통 — 자세한 내용은 KiCad 매뉴얼의 "Common preferences" 참조.

### Display options · #display_options

캔버스 렌더링/그리드/스냅/표시 옵션을 제어한다.

| 옵션 | 설명 |
| --- | --- |
| **Rendering Engine** | Accelerated graphics / Fallback graphics 선택. |
| **Grid style** | 정렬 그리드 표시 방식. |
| **Grid thickness** | 그리드 선/점의 두께. |
| **Min grid spacing** | 두 그리드 선 사이 최소 거리(픽셀). 위반 시 그리드 설정과 무관하게 그려지지 않음. |
| **Snap to grid** | 드로잉/편집 시 그리드 스냅 시점. "Always"=그리드 숨김 시에도 스냅, "When grid shown"=그리드가 보일 때만. |
| **Cursor shape** | 편집 커서를 small crosshair / full-screen crosshair로. |
| **Always show crosshairs** | 편집 커서를 항상 표시할지, 도구 활성 시에만 표시할지. |
| **Net names** | copper 객체에 net name 라벨 표시 여부(편집 가이드용, 팹 출력에는 안 나옴). |
| **Show pad numbers** | footprint pad의 번호 라벨 표시. |
| **Show pad \<no net\> indicator** | net 없는 pad를 특수 마커로 표시. |
| **Track clearance** | track/via 주변 clearance 윤곽 표시. |
| **Show pad clearance** | pad 주변 clearance 윤곽 표시. |
| **Center view on cross-probed items** | Eeschema에서 컴포넌트/핀 클릭 시 PCB 뷰를 해당 footprint/pad로 센터링. |
| **Zoom to fit cross-probed items** | cross-probe된 footprint/pad가 보이도록 줌. |
| **Highlight cross-probed nets** | Eeschema에서 하이라이트한 net을 PCB 에디터에서도 하이라이트. |

💡 그리드 스냅은 `Ctrl`을 누른 채로 일시적으로 비활성화할 수 있다.

### Editing options · #editing_options

객체 이동/회전/스냅(magnetic points) 동작을 제어한다.

| 옵션 | 설명 |
| --- | --- |
| **Flip board items L/R** | top↔bottom 이동 시 뒤집는 축. 체크=좌우(수직축 기준), 해제=상하(수평축 기준). |
| **Step for rotate commands** | Rotate 명령 1회당 회전 각도. |
| **Allow free pads** | footprint pad를 footprint와 별도로 잠금 해제·편집·이동 허용. |
| **Magnetic points** | 객체 스냅(=magnetic points). 활성 시 그리드 스냅보다 우선. 활성 레이어 객체에만 작동. `Shift`로 일시 비활성화. |
| **Snap to pads** | 편집 커서가 pad 원점에 스냅. |
| **Snap to tracks** | track 세그먼트 끝점에 스냅. |
| **Snap to graphics** | 그래픽 도형 포인트에 스냅. |
| **Always show selected ratsnest** | 글로벌 ratsnest가 숨겨져도 선택한 footprint의 ratsnest는 항상 표시. |
| **Show ratsnest with curved lines** | ratsnest 선을 직선/곡선으로. |
| **Mouse drag track behavior** | track 드래그 동작: "Move"=독립 이동, "Drag (45 degree mode)"=push-and-shove 라우터로 디자인룰 준수 드래그(연결 유지), "Drag (free angle)"=가장 가까운 코너 이동(충돌은 하이라이트만, 비켜주지 않음). |
| **Limit actions to 45 degrees from start** | 그래픽 드로잉 도구로 그리는 새 선의 각도 제한(새 선에만 적용, 편집 시 임의 각도 가능). |
| **Show page limits** | 페이지 경계를 사각형으로 표시. |
| **Refill zones after Zone Properties dialog** | zone 속성 편집 후 자동 refill 여부. 복잡한 설계/느린 PC에서는 응답성 향상 위해 끌 수 있음. |

### Colors · #colors

- KiCad는 색상 테마 전환을 지원한다. KiCad 10.0 기본 내장 테마는 2개: "KiCad Default"(신규 설치 기본), "KiCad Classic"(KiCad 5.1 이전 기본). 두 내장 테마는 수정 불가 — 새 테마를 만들거나 타 사용자 테마를 설치해야 한다.
- 테마는 KiCad 설정 디렉토리의 `colors` 하위 폴더에 JSON 파일로 저장. **Open Theme Folder** 버튼으로 파일 관리자에서 열 수 있다. 새 테마 설치: 이 폴더에 파일을 넣고 KiCad 재시작(유효한 테마 파일이면 드롭다운에 표시).
- 새 테마 생성: 색상 테마 드롭다운에서 **New Theme…** 선택 → 이름 입력. 새 테마의 색상은 생성 직전 선택돼 있던 테마에서 복사된다.
- 색상 변경: 목록의 색상 스와치를 더블클릭 또는 가운데 클릭. **Reset to Default** 버튼은 해당 색상을 "KiCad Default" 테마 값으로 복원.
- 테마는 자동 저장되며 Preferences 다이얼로그를 닫으면 즉시 반영. 우측 창에 미리보기 표시.

### Action plugins · #action_plugins

- PCB 에디터는 보드를 조작하는 Python 액션 플러그인을 지원한다. 설치는 Plugin and Content Manager(PCM) 또는 사용자 plugins 디렉토리에 파일 배치(Scripting 섹션 참조).
- 감지된 각 플러그인은 이 설정 페이지에 한 행씩 표시되며 상단 툴바에 버튼을 표시할 수 있다. **Show button**을 해제해도 **Tools → External Plugins** 메뉴에서 접근 가능.
- 하단 화살표 버튼으로 툴바/메뉴 표시 순서 변경, 폴더 버튼으로 플러그인 폴더 탐색, 새로고침 버튼으로 폴더 재스캔.

### Origin & axes · #origin_axes

| 옵션 | 설명 |
| --- | --- |
| **Display origin** | 편집 캔버스 좌표 표시의 기준 원점. page origin은 페이지 모서리에 고정, drill/place file origin과 grid origin은 사용자가 이동 가능. |
| **X axis** | X 좌표 증가 방향(우/좌). |
| **Y axis** | Y 좌표 증가 방향(상/하). |

---

## Text variables · #text-variables

- 텍스트 변수는 이름으로 미리 정의한 값을 참조하는 기능. `${VARIABLENAME}` 구문이 쓰인 모든 곳에서 변수명이 지정 문자열로 치환된다.
- 사용 가능 컨텍스트: schematic/PCB 그래픽 텍스트, symbol/footprint 텍스트·필드, drawing sheet 필드, 커스텀 DRC 룰 등.
- 예: 변수 `VERSION`=`1.0` 정의 → 텍스트에 `${VERSION}` 입력 시 `1.0` 표시. `Version: ${VERSION}` → `Version: 1.0`. 값을 `2.0`으로 바꾸면 모든 객체가 자동 갱신.
- **프로젝트 텍스트 변수**: schematic 또는 board setup 다이얼로그에서 정의. 프로젝트 전체 공용이므로 Schematic Editor에서 정의한 변수를 Board Editor에서도 사용 가능(역방향도 동일).
- 아래는 내장 **시스템 텍스트 변수** 목록(일부 컨텍스트에서만 사용 가능). Schematic Editor에는 별도 동등 목록이 있음.

| Variable name | Description |
| --- | --- |
| `ADDR` | 현재 테이블 셀의 열(문자)·행(0-인덱스 숫자) 주소. 테이블 셀에서만 사용 가능. |
| `CELL(<row>, <col>)` | `<row>`,`<col>`(0-인덱스)로 인덱싱된 테이블 셀 내용. 테이블 셀에서만. |
| `COL` | 현재 테이블 셀의 열 번호(0-인덱스). 테이블 셀에서만. |
| `COMMENT1` - `COMMENT9` | drawing sheet의 `Comment<n>` 필드 내용. |
| `COMPANY` | drawing sheet의 `Company` 필드 내용. |
| `CURRENT_DATE` | 오늘 날짜(ISO 형식). |
| `CURRENT_TIME_HH_MM_SS` | 현재 시각(`HHhMMmSSs` 형식, 예 `14h30m45s`). 파일명에 안전. |
| `CURRENT_TIME_LOCALE` | 현재 시각(현재 로케일 형식). |
| `FILENAME` | 보드 파일명(확장자 포함). |
| `FILEPATH` | 보드 전체 파일 경로(확장자 포함). |
| `ISSUE_DATE` | drawing sheet의 `Issue Date` 필드. |
| `KICAD_VERSION` | 현재 KiCad 버전. drawing sheet 필드에서만 사용 가능. |
| `LAYER` | 객체의 레이어. footprint 필드/텍스트에서는 부모 footprint가 아니라 그 필드/텍스트의 레이어. drawing sheet 필드에서는 플롯되는 레이어로 해석(예 `F.Fab` 플롯 시 `F.Fab`). 레이어가 있는 객체에서만 사용 가능, DRC 룰처럼 적용 레이어가 없으면 사용 불가. |
| `PAPER` | 현재 시트 용지 크기. drawing sheet 필드에서만. |
| `PROJECTNAME` | 프로젝트명(확장자 없음). |
| `REVISION` | drawing sheet의 `Revision` 필드. |
| `ROW` | 현재 테이블 셀의 행 번호(0-인덱스). 테이블 셀에서만. |
| `TITLE` | drawing sheet의 `Title` 필드. |
| `VARIANT` | 현재 활성 디자인 variant 이름. 기본 variant이면 빈 문자열. |
| `VARIANT_DESC` | 현재 활성 디자인 variant 설명. 기본 variant이거나 설명 없으면 빈 문자열. |
| `VCSHASH` | 프로젝트의 현재 Git 커밋 전체 해시. Git 리포지토리가 아니면 "no hash". |
| `VCSSHORTHASH` | 현재 Git 커밋 짧은(8자) 해시. 아니면 "no hash". |
| `<variablename>` | 프로젝트 텍스트 변수 `<variablename>`의 내용. |
| `<fieldname>` | footprint 필드 `<fieldname>` 내용. 필드는 부모 객체 내에서만 접근 가능(footprint 내 다른 필드/텍스트에서 접근). 내장·사용자 정의 필드 모두 가능. 내장 필드는 전부 대문자(예 value는 `${VALUE}`). 내장 footprint 필드: `FOOTPRINT_LIBRARY`, `FOOTPRINT_NAME`, `LAYER`, `NET_CLASS(<pad_number>)`, `NET_NAME(<pad_number>)`, `PIN_NAME(<pad_number>)`, `REFERENCE`, `SHORT_NET_NAME(<pad_number>)`, `VALUE`. |
| `<refdes>:<fieldname>` | footprint `<refdes>`의 필드 `<fieldname>` 내용(예 `${U1:VALUE}`). 내장 필드 목록은 위와 동일. **Note:** `<refdes>`가 재annotate되면 텍스트 변수의 `<refdes>`도 새 reference designator로 자동 갱신되어 동일 footprint를 계속 참조. |
| `DRC_ERROR <errorname>` | `<errorname>` 이름의 DRC 에러 생성. 중괄호 안은 빈 문자열로 해석되고 중괄호 뒤 텍스트가 위반 설명문이 됨. 텍스트 변수가 텍스트 항목 맨 앞에 있어야 함. 예: `${DRC_ERROR TODO}Length match tracks` → "Length match tracks" 표시 + 이름 "TODO" 에러 생성. |
| `DRC_WARNING <warningname>` | `<warningname>` 이름의 DRC 경고 생성. `DRC_ERROR`와 동일하나 에러 대신 경고. |

---

## Text expressions · #text-expressions

- 텍스트 식 평가 시스템 — 문자열 조작, 수식 계산, 동적 문자열 생성. schematic/PCB 그래픽 텍스트, symbol/footprint 텍스트·필드, drawing sheet 필드 등에서 사용.
- `@{expression}` 구문 사용 시 중괄호 안이 평가되고 `@{}` 포함 전체가 결과로 치환됨. 평가 불가 시 원본 텍스트 유지.
- 예: `1 plus 1 is @{1 + 1}` → `1 plus 1 is 2`. `@{abs(-1)}` → `1`.
- 다중 평가·중첩 가능: `@{max(1, 2, 3)}, @{max(4, 5, 6)}` → `3, 6`. 텍스트 변수와 결합 가능: `var`=`-10`이면 `@{max(abs(${var}), 5)}` → `10`.
- 과학 표기: `@{2e3 + 1}` → `2001`.
- 단위 지원 — 결과는 항상 SI 단위로, 단위 기호는 출력 안 함: `@{1mm + 1in}` → `26.4`.
- 문자열은 작은/큰따옴표로 감쌈(`'string 1'`, `"string 2"`). 예: `@{upper("string")}` → `STRING`.
- 연결은 `concat` 또는 `+` 연산자: `@{concat("hello ", "world")}`·`@{"hello " + "world"}` → `hello world`. `@{"revision " + 1}` → `revision 1`.

### Mathematical and logical expressions · #mathematical_and_logical_expressions

산술 연산자(중위, 연산 우선순위 적용, 괄호로 그룹화). 예: `@{3 + 4 * 3}`=`15`, `@{(3 + 4) * 3}`=`21`.

| 연산자 | 설명 | 예 |
| --- | --- | --- |
| `+` | 덧셈(**Note:** 문자열 연결, 문자열+숫자 연결에도 사용 가능) | `@{1 + 1}` = `2` |
| `-` | 뺄셈 | `@{1 - 1}` = `0` |
| `*` | 곱셈 | `@{2 * 2}` = `4` |
| `/` | 나눗셈(제수 `0`이면 미평가) | `@{3 / 2}` = `1.5`, `@{1 / 0}` = `@{1 / 0}` |
| `%` | 모듈로(제수 `0`이면 미평가) | `@{3 % 2}` = `1`, `@{3 % -2}` = `1` |
| `^` | 거듭제곱(우결합) | `@{2 ^ 3}` = `8`, `@{2 ^ 3 ^ 2}` = `512` |

수학 함수:

| 함수 | 설명 | 예 |
| --- | --- | --- |
| `abs(x)` | 절댓값 | `@{abs(-1)}` = `1` |
| `sqrt(x)` | 제곱근(음수면 미평가) | `@{sqrt(4)}` = `2` |
| `pow(x, y)` | x의 y제곱 | `@{pow(2, 3)}` = `8` |
| `floor(x)` | x 이하 최대 정수 | `@{floor(3.7)}` = `3` |
| `ceil(x)` | x 이상 최소 정수 | `@{ceil(3.2)}` = `4` |
| `round(x, [precision])` | precision 자릿수로 반올림(생략 시 정수) | `@{round(3.7)}` = `4`, `@{round(3.14159, 2)}` = `3.14` |
| `min(…)` | 콤마 구분 값의 최소 | `@{min(5, 3, 8, 1)}` = `1` |
| `max(…)` | 최대 | `@{max(5, 3, 8, 1)}` = `8` |
| `sum(…)` | 합 | `@{sum(1, 2, 3, 4)}` = `10` |
| `avg(…)` | 평균 | `@{avg(2, 4, 6)}` = `4` |
| `random()` | `0`(포함)~`1`(미포함) 난수 | `0` ≤ `@{random()}` < `1` |
| `shunt(r1, r2)` | 병렬 저항 `(r1*r2)/(r1+r2)` | `@{shunt(10k, 10k)}` = `5000` |
| `db(ratio)` | 전력비→데시벨 `10*log10(ratio)` | `@{db(2)}` ≈ `3` |
| `dbv(ratio)` | 전압/전류비→데시벨 `20*log10(ratio)` | `@{dbv(2)}` ≈ `6` |
| `fromdb(db)` | 데시벨→전력비 `10^(db/10)` | `@{fromdb(3)}` ≈ `2` |
| `fromdbv(db)` | 데시벨→전압/전류비 `10^(db/20)` | `@{fromdbv(6)}` ≈ `2` |
| `enearest(value, [series])` | value에 가장 가까운 E-시리즈 표준값. series=`"E3"`~`"E192"`(생략 시 `"E24"`) | `@{enearest(5)}` = `5.1` |
| `eup(value, [series])` | value보다 큰 가장 가까운 E-시리즈 값 | `@{eup(5)}` = `5.1` |
| `edown(value, [series])` | value보다 작은 가장 가까운 E-시리즈 값 | `@{edown(5)}` = `4.7` |

### Boolean expressions · #boolean_expressions

불리언 연산은 참=`1`, 거짓=`0`으로 평가.

| 연산자 | 설명 | 예 |
| --- | --- | --- |
| `<` | 미만 | `@{1 < 2}` = `1` |
| `<=` | 이하 | `@{1 <= 2}` = `1` |
| `>` | 초과 | `@{1 > 2}` = `0` |
| `>=` | 이상 | `@{1 >= 2}` = `0` |
| `==` | 같음 | `@{1 == 2}` = `0` |
| `!=` | 다름 | `@{1 != 2}` = `1` |

| 함수 | 설명 | 예 |
| --- | --- | --- |
| `if(condition, true_value, false_value)` | condition이 참(0이 아님)이면 true_value, 아니면 false_value | `@{if(1 < 2, 5, 10)}` = `5` |

### String manipulation · #string_manipulation

💡 문자열은 작은/큰따옴표로 감싼 텍스트(`"this is a string"`, `'this is also a string'`).

| 함수 | 설명 | 예 |
| --- | --- | --- |
| `upper(str)` | 대문자 변환 | `@{upper("hello world")}` = `HELLO WORLD` |
| `lower(str)` | 소문자 변환 | `@{lower("HELLO WORLD")}` = `hello world` |
| `concat(…)` | 콤마 구분 문자열/숫자 연결(`+`로도 가능) | `@{concat("Hello", " ", "World")}` = `Hello World` |
| `beforefirst(str, c)` | str에서 문자 c 첫 등장 이전 부분 | `@{beforefirst("hello.world.txt", ".")}` = `hello` |
| `beforelast(str, c)` | c 마지막 등장 이전 | `@{beforelast("hello.world.txt", ".")}` = `hello.world` |
| `afterfirst(str, c)` | c 첫 등장 이후 | `@{afterfirst("hello.world.txt", ".")}` = `world.txt` |
| `afterlast(str, c)` | c 마지막 등장 이후 | `@{afterlast("hello.world.txt", ".")}` = `txt` |
| `format(num, [precision])` | num을 precision 소수자리로 반올림한 문자열(생략 시 2자리). `fixed()`와 동일 | `@{format(3.14159, 3)}` = `3.142`, `@{format(1234.5)}` = `1234.50` |
| `fixed(num, [precision])` | `format()`와 완전 동일 | `@{fixed(3.14159)}` = `3.14` |
| `currency(amount, [symbol])` | 통화 기호+소수 2자리(symbol 생략 시 `"$"`) | `@{currency(1234.56)}` = `$1234.56`, `@{currency(999.99, "€")}` = `€999.99` |

### Date and time formatting · #date_and_time_formatting

| 함수 | 설명 | 예 |
| --- | --- | --- |
| `today()` | Unix epoch(1970-01-01 00:00:00 UTC) 이후 일수로 표현한 현재 날짜. `dateformat()`로 포맷, ±정수로 상대 날짜 | — |
| `now()` | Unix epoch 이후 초로 표현한 현재 타임스탬프. ±정수로 상대 타임스탬프 | — |
| `dateformat(days, [format])` | days를 날짜 문자열로. format=`"ISO"`,`"US"`,`"EU"`,`"Chinese"`,`"Japanese"`,`"long"`,`"short"`(생략 시 `"ISO"`) | `@{dateformat(0)}` = `1970-01-01`, `@{dateformat(0, "short")}` = `Jan 1, 1970` |
| `weekdayname(days)` | days에 해당하는 요일 | `@{weekdayname(0)}` = `Thursday` |
| `timeformat(seconds, [format])` | seconds를 시각 문자열로. format=`"24h"`,`"12h"`,`"ISO"`(=24h),`"HH_MM_SS"`,`"filename"`(=HH_MM_SS),`"short"`(생략 시 `"ISO"`) | `@{timeformat(0)}` = `00:00:00`, `@{timeformat(0), "HH_MM_SS"}` = `00h00m00s` |

### Version control expressions · #version_control_expressions

VCS 정보 추출 함수. 프로젝트가 버전 관리 하에 없으면 각각 `<unknown>`으로 평가. Git만 지원.

| 함수 | 설명 |
| --- | --- |
| `vcsidentifier([length])` | 현재 HEAD 커밋 식별자(length자로 절단, 생략 시 40, 최소 4). |
| `vcsbranch()` | 현재 브랜치명. |
| `vcsauthor()` / `vcsauthoremail()` | HEAD 커밋 작성자 이름 / 이메일. |
| `vcscommitter()` / `vcscommitteremail()` | HEAD 커밋 committer 이름 / 이메일. |
| `vcscommitdate([format])` | HEAD 커밋 날짜. format=`"ISO"`/`"US"`/`"EU"`/`"Chinese"`/`"Japanese"`/`"long"`/`"short"`(생략 시 ISO). |
| `vcsnearestlabel([match], [anyTags])` | HEAD에 가장 가까운 매칭 태그명. match=glob 패턴(생략 시 `*`). anyTags=`0`/생략이면 annotated 태그만, `1`이면 모든 태그. |
| `vcslabeldistance([match], [anyTags])` | HEAD와 가장 가까운 매칭 태그 사이 커밋 수. |
| `vcsdirty([includeUntracked])` | 리포지토리 dirty면 `1`, 아니면 `0`. includeUntracked=`1`이면 untracked 파일도 반영. |
| `vcsdirtysuffix([suffix], [includeUntracked])` | dirty면 suffix(생략 시 `-dirty`), 아니면 빈 문자열. |
| `vcsfileidentifier(file, [length])` | file을 마지막 수정한 커밋 식별자(length 절단, 생략 시 40, 최소 4). |
| `vcsfileauthor(file)` / `vcsfileauthoremail(file)` | file 마지막 수정 커밋 작성자 이름 / 이메일. |
| `vcsfilecommitter(file)` / `vcsfilecommitteremail(file)` | file 마지막 수정 커밋 committer 이름 / 이메일. |
| `vcsfilecommitdate(file, [format])` | file 마지막 수정 커밋 날짜(format은 vcscommitdate와 동일). |

---

## Graphical design rule editor · #graphical-design-rule-editor

- 폼 컨트롤로 디자인 룰을 만들고 관리하는 편집기(raw 문법 대신). 룰은 텍스트 에디터와 동일한 `.kicad_dru` 파일에 저장되며 두 편집기를 같은 파일에 교차 사용 가능.
- 다루는 범위: clearances, track widths, via styles, footprint placement 룰, 여러 고속 설계 제약. 미지원 룰은 커스텀 디자인 룰 텍스트 에디터 사용.
- 열기: **Tools → Design Rule Editor**.
- 다이얼로그는 2-pane: 좌측은 카테고리별 제약 타입을 묶은 rule tree, 우측은 선택 항목의 rule editor.

### Rule tree · #rule_tree

- 모든 제약 타입을 5개 카테고리로 그룹화. 제약 타입 노드는 굵게, 사용자 생성 룰은 그 하위 자식으로 표시.
  - **Electrical**: 전기적으로 강제되는 간격·연결 요구
  - **Manufacturability**: 홀·via·텍스트·표면처리의 물리 제조 한계
  - **Highspeed design**: 차동쌍·skew·길이 매칭 제약
  - **Footprints**: 레이어·방향·via 근접의 배치 룰
  - **Custom**: 위 카테고리 미포함 제약을 위한 raw 문법 룰
- 새 룰: 제약 타입 노드 선택 후 하단 툴바 `+` 버튼, 또는 우클릭 **New Rule**.
- 복제: 툴바 copy 버튼 또는 우클릭 **Copy Rule**. 삭제: delete 버튼 또는 우클릭 **Delete Rule**.
- 룰은 기반 `.kicad_dru` 파일과 동일 순서로 평가(평가 순서는 Custom design rules 참조).

### Rule editor panel · #rule_editor_panel

- 트리에서 룰 선택 시 우측 패널에 설정 표시.
- **Rule name**: 룰의 고유 식별자. DRC 위반 보고에 표시되므로 `HV clearance`, `PWR track width` 같이 서술적으로.
- **Comment**: 선택적 메모(편집기에서 보이고 생성 룰 텍스트에 보존됨).

#### Constraint values · #constraint_values

- 선택한 제약 타입의 파라미터를 보여주는 시각 다이어그램에, 물리적 측정 위치에 입력 필드가 배치됨. 다이어그램은 제약 타입별로 다름(아래 Constraint reference 참조).

#### Conditions · #conditions

- **Conditions** 섹션은 룰이 적용될 보드 객체를 결정. 조건 미설정 시 해당 타입 모든 객체에 적용.
- 각 조건 행은 검사 대상 한 객체를 필터링. 단일 객체 제약은 각 행이 **Object A** 필터, clearance 같은 2-객체 제약은 각 행에 **Object A / Object B** 선택기.
- 조건 타입 드롭다운 5가지 모드: **Any**(모든 객체) / **Net**(특정 net) / **Netclass**(net class) / **Within Area**(명명된 rule area 내부) / **Custom Query**(커스텀 룰 문법 자유식).
- 여러 조건은 하단 `+` 버튼으로 결합. 행 간 불리언 연산자는 좌측 드롭다운으로 **AND** / **OR** / **AND NOT** / **OR NOT** 설정. 조건은 암묵적 그룹화 없이 좌→우 평가.
- 행 제거는 우측 끝 delete 버튼. **Syntax help**(조건 섹션 우상단)로 커스텀 룰 식 언어 빠른 참조.

#### Layer · #layer

- 패널 하단 **Layer** 선택기로 룰 적용 레이어 제한(제약 타입별로 선택지 다름):
  - **Any**: 모든 관련 레이어(기본)
  - 특정 레이어명: 그 레이어만
  - **Outer**: `F.Cu`·`B.Cu`만
  - **Inner**: 내부 copper 레이어만
- **Show Matches**: 현재 룰 조건을 만족하는 보드 객체를 하이라이트(저장 전 조건 검증용).
- 값 설정 후 **Save**로 저장, **Discard**로 변경 취소.

### Constraint reference · #drc-rule-editor-constraint-reference

#### Electrical · #electrical

| 제약 | 설명 |
| --- | --- |
| **Minimum clearance** | copper-copper 최소 간격. |
| **Copper to edge clearance** | copper 객체와 보드 외곽 사이 최소 거리. |
| **Courtyard clearance** | footprint courtyard 경계 간 최소 간격. |
| **Physical clearance** | 물리 객체 간 최소 거리(홀 가장자리까지 측정). |
| **Creepage distance** | 다른 전위 도체 간 최소 표면 creepage 거리. |
| **Minimum connection width** | track·zone fill 연결의 최소 폭. |
| **Copper to hole clearance** | copper 형상과 드릴 홀 가장자리 최소 거리. |
| **Minimum thermal relief spoke count** | pad-zone fill 연결의 thermal relief spoke 최소 개수. |

#### Manufacturability · #manufacturability

| 제약 | 설명 |
| --- | --- |
| **Minimum annular width** | through-hole pad·via 최소 annular ring 폭. |
| **Minimum drill size** | 최소 허용 드릴 직경. |
| **Hole to hole distance** | 두 홀 간 최소 가장자리-가장자리 간격. |
| **Via style** | via pad 직경·드릴 크기의 최소/최대. **Via type** 필터로 Any/Through/Micro/Blind/Buried 제한 가능. |
| **Minimum text height and thickness** | 모든 레이어 텍스트의 최소 문자 높이·획 두께. |
| **Silk to silk clearance** | silkscreen 객체 간 최소 간격. |
| **Silk to soldermask clearance** | silkscreen 객체와 soldermask 개구부 가장자리 최소 거리. |
| **Minimum soldermask silver** | 인접 pad 개구부 사이 최소 soldermask sliver 폭. |
| **Soldermask expansion** | pad 대비 soldermask 개구부 확장 최소/최대. |
| **Solderpaste expansion** | pad 대비 solderpaste 개구부 크기 최소/최대. |

#### Highspeed design · #highspeed_design

| 제약 | 설명 |
| --- | --- |
| **Routing width** | track 폭 최소/optimal(선호)/최대. 선호 폭은 새 track 배치 시 라우터 기본값. |
| **Maximum via count** | net당 허용 최대 via 수. |
| **Routing diff pair** | 차동쌍 두 신호 간 최대 skew 허용. |
| **Matched length diff pair** | 차동쌍 두 신호 길이 불일치 최대 + 쌍 도체 간 gap 최소/최대. |
| **Absolute length** | net의 최소/최대 총 라우팅 길이. |

#### Footprints · #footprints

| 제약 | 설명 |
| --- | --- |
| **Permitted layers** | top/bottom/양면 배치 허용 체크박스. 체크 안 된 레이어에 배치 시 DRC 에러. |
| **Allowed orientation** | 0°·90°·180°·270°·All 체크박스. 체크 안 된 회전으로 배치 시 DRC 에러. |
| **Vias under SMD** | SMD pad 바로 아래 via 허용 여부. |

#### Custom · #custom

- **Custom rule** 선택 시 전체 커스텀 디자인 룰 문법으로 룰 입력. 텍스트 에디터는 구문 강조·자동완성 지원. **Check syntax**로 저장 전 검증. 전체 문법은 Custom design rules 참조.

### Examples · #examples

#### Minimum clearance for a high-voltage net class · #minimum_clearance_for_a_high_voltage_net_class

`HV` net class 객체와 다른 모든 객체 사이에 1.5 mm 최소 clearance 강제.
1. **Tools → Design Rule Editor**.
2. rule tree에서 **Electrical → Clearance → Minimum clearance** 선택.
3. `+` 버튼 또는 우클릭 **New Rule**. `Minimum clearance 1`이 생성됨.
4. **Rule name**을 `HV clearance`로 변경.
5. **Conditions**에서 **Condition type**=**Netclass**, `HV` 선택. **Object** 선택기는 `A` 유지.
6. clearance 값 `1.5` 설정.
7. **Save**. → DRC 실행 시 `HV` net class 객체의 clearance가 1.5 mm 미만이면 flag.

#### Preferred track width for power nets · #preferred_track_width_for_power_nets

`PWR` net class 전 net에 선호 라우팅 폭 0.5 mm, 최소 0.25 mm 설정.
1. **Tools → Design Rule Editor**.
2. **Highspeed design → Diff Pair (width, gap, uncoupled length) → Routing width** 선택.
3. `+`로 새 룰 생성, `PWR track width`로 명명.
4. **Condition type**=**Netclass**, `PWR` 선택.
5. 제약 다이어그램에서 **Min**=`0.25`, **Opt**=`0.5`, **Max**=`1.0`.
6. **Save**. → 인터랙티브 라우터가 `PWR` net 라우팅 시 0.5 mm 기본, 0.25 mm 최소 강제.

#### Restricting a footprint to the top side only · #restricting_a_footprint_to_the_top_side_only

U-reference footprint이 보드 bottom에 배치되면 DRC 에러 생성.
1. **Tools → Design Rule Editor**.
2. **Footprints → Allowed Layers → Permitted layers** 선택.
3. `+`로 새 룰 생성, `ICs top only`로 명명.
4. **Condition type**=**Custom Query**로 설정 후 식 입력(원문에 식 본문 미수록).
5. **Allow top layer** 체크, **Allow bottom layer** 해제.
6. **Show Matches**로 올바른 footprint가 선택되는지 확인.
7. **Save**.

💡 **Permitted layers**·**Allowed orientation** 제약은 내부적으로 `assertion` 제약 타입을 사용. 위반은 DRC 보고에 `Assertion violation` 에러로 나타나며 룰 이름이 위반된 assertion을 식별.

---

## Custom design rules · #custom-design-rules

- 커스텀 디자인 룰은 Board Setup의 Constraints 페이지 일반 룰보다 구체적인 룰을 만든다. 주로 보드 일부(특정 net/net class, 특정 area, 특정 footprint)에 적용.
- 별도 파일 `.kicad_dru`에 저장. 커스텀 룰 추가 시 자동 생성. **백업/버전 관리 시 `kicad_pcb`·`kicad_pro`와 함께 `kicad_dru`도 저장할 것.**

⚠️ `kicad_dru` 파일은 KiCad가 자동 관리하므로 외부 텍스트 에디터로 편집하지 말 것. 항상 Board Setup의 Custom Rules 페이지로 편집.

### The Custom Rules editor · #the_custom_rules_editor

- Board Setup 다이얼로그에 위치. 텍스트 에디터 + 구문 검사기 + 빠른 참조·예제 룰을 담은 syntax help 다이얼로그 제공.
- 컨텍스트 기반 자동완성(키워드·속성 제안). 자동 표시되며 `Ctrl`+`Space`로 수동 호출 가능.
- 편집 후 **Check rule syntax** 버튼 사용 권장. 커스텀 룰에 오류가 있으면 DRC가 실행되지 않음.

### Custom rule syntax · #custom_rule_syntax

- s-expression 기반. 각 룰은 일반적으로 매칭 대상을 정의하는 **condition**과 적용할 **constraint**를 가짐.
- 괄호 `(` `)`로 절(clause) 정의 — 항상 짝을 맞춰야 함. 절 내부 키워드·값은 공백(스페이스·탭·개행)으로 구분. 공백 없는 문자열은 `"`·`'`로 인용하거나 비인용 가능, 공백 포함 문자열은 반드시 인용. 인용 문자열 안에 개행 불가. 중첩 인용은 외부 `"`/내부 `'`(또는 반대)로 1단계 가능.
- 문법 설명에서 `<angle brackets>`=필수, `[square brackets]`=선택/때때로 필요.
- 파일은 버전 헤더로 시작. KiCad 10.0의 버전은 `1`:
```
(version 1)
```
- 버전 헤더 뒤 임의 개수 룰. **룰은 역순 평가** — 파일 마지막 룰이 가장 먼저 검사됨. 한 객체 집합에 매칭 룰을 찾으면 이후 룰은 검사 안 함. 따라서 **더 구체적인 룰을 파일 뒤쪽에 둘 것**(일반 룰보다 먼저 평가되게).
  - 예: HV net과 다른 net의 최소 clearance 룰과, 특정 rule area 내부 모든 객체의 최소 clearance 룰이 있다면, 첫 번째(HV) 룰이 두 번째(area)보다 뒤에 있어야 HV net이 area 안에 들어가도 올바른 clearance가 적용됨.
- 각 룰은 name과 하나 이상의 `constraint` 절 필수. 선택적으로 `condition`, `layer`, `severity` 절.
```
(rule <name>
    [(severity <severity>)]
    [(layer <layer_name>)]
    [(condition <expression>)]
    (constraint <constraint_type> [constraint_arguments]))
```
- 주석은 `#`로 시작하는 줄(앞 공백 무시). `Ctrl`+`/`로 줄 주석 토글.
```
# Clearance for 400V nets to anything else
(rule HV
    (condition "A.hasNetclass('HV')")
    (constraint clearance (min 1.5mm)))
```
- 커스텀 룰은 텍스트 변수 참조 가능(문법 일부는 아니고 평가 전 전처리에서 텍스트 치환). 예: `(constraint clearance (min ${hv_clearance}))`. 단 `${LAYER}`·`${<fieldname>}`처럼 객체에 따라 값이 달라지는 변수는 룰 평가 전 해석 불가 → 미해석 상태로 남아 구문 오류 유발.

#### Layer Clause · #layer_clause

- `layer` 절은 룰이 작동할 레이어 결정. condition에서 레이어를 테스트할 수도 있으나 `layer` 절이 더 효율적.
- 값: 임의 보드 레이어명, 또는 단축 키워드 `outer`(`F.Cu`·`B.Cu`), `inner`(내부 copper 레이어). 생략 시 모든 레이어에 적용.
```
# Do not allow footprints on back layer (no condition clause means this rule always applies)
(rule "Top side footprints only"
    (layer B.Cu)
    (constraint disallow footprint))

# This rule does the same thing, but is less efficient
(rule "Top side footprints only"
    (condition "A.Layer == 'B.Cu'")
    (constraint disallow footprint))

# Larger clearance on outer layers (inner layer clearance set by board minimum clearance)
(rule "clearance_outer"
    (layer outer)
    (constraint clearance (min 0.25mm)))
```

#### Severity Clause · #severity_clause

- `severity` 절은 룰 위반 시 DRC 위반 심각도 설정. 값: `error`, `warning`, `ignore`, `exclusion`.
- `ignore` 룰은 인터랙티브 라우터가 무시하고 DRC 다이얼로그에 위반이 안 나타남. 단 매칭 평가는 수행되어 이전 룰을 여전히 오버라이드할 수 있음.

⚠️ severity를 `ignore`로 해도 룰이 비활성화되는 게 아니라 **효과만** 비활성화. 룰은 여전히 평가되어 이전 룰을 오버라이드 가능.

#### Condition Clauses · #condition_clauses

- `condition` 절은 룰 적용 객체를 결정. 조건 절이 있으면 매칭 객체에, 없으면 무조건 적용.
- condition은 텍스트 문자열 안의 식(보통 가독성 위해 인용). 검사되는 객체 쌍마다 평가되며 식이 불리언(true/false)으로 해석되어야 함. true면 룰 적용.
- 두 객체는 식에서 `A`, `B`로 참조. 순서 무관(DRC가 양방향 모두 검사). 두 객체를 함께 테스트하는 함수는 `AB` 사용.
- 속성·함수 구문: `<object>.<property>`, `<object>.<function>([arguments])`.

💡 텍스트 에디터에 `A.`/`B.`/`AB.` 입력 시 사용 가능한 속성 자동완성 목록이 열림.

불리언·관계 연산자:

| 연산자 | 의미 |
| --- | --- |
| `==` | 같음 |
| `!=` | 다름 |
| `>`, `>=` | 초과, 이상 |
| `<`, `<=` | 미만, 이하 |
| `&&` | And |
| `\|\|` | Or |
| `!` | Not(단항) |

- 예: `A.NetName == 'VDD'`, `A.NetName != B.NetName`. 모든 불리언 연산자는 같은 우선순위로 좌→우 평가(괄호는 명료화용, 필수 아님).
- 불리언 속성은 `true`/`false` 리터럴과 비교하지 말고 속성 자체로 평가(이 언어엔 불리언 리터럴 없음). 예: `A.Do_not_populate`(DNP면 참), `!A.Do_not_populate`(DNP 미설정이면 참).
- 물리 측정 속성에는 단위 접미사 사용 가능(미사용 시 내부 표현: 거리 nm, 각도 degree):

| 접미사 | 의미 |
| --- | --- |
| `mm` | 밀리미터 |
| `mil`, `th` | mil(1/1000 inch) |
| `in`, `"` | 인치 |
| `deg` | 도 |
| `rad` | 라디안 |

💡 커스텀 룰의 단위는 PCB 에디터 표시 단위와 독립적이다.

- 수치 조건에 간단 수식 가능: `(condition "A.Hole_Size_X == 1.0mm + 0.1mm")`.
- nullable 속성은 값(0 포함) 또는 null을 가질 수 있음. null 검사는 `null` 토큰과 비교: `(condition "A.Soldermask_Margin_Override != null")`.

#### Constraint Clauses · #constraint_clauses

- `constraint` 절은 매칭 객체에 적용할 동작을 정의. constraint type + 인자(들)로 구성. 한 룰에 여러 constraint 절 가능(예 같은 조건에 `clearance`와 `track_width`).
- 물리 측정 인자는 minimum/optimal/maximum("min/opt/max") 지정 가능. min/max는 DRC용(실제 값이 min 미만 또는 max 초과면 에러). opt는 일부 제약에서 기본값 힌트(예 새 차동쌍 배치 시 `diff_pair_gap`의 opt 사용). 나중에 opt와 달라도 min~max 범위 내면 에러 없음.
- 지정: `(min <value>)`, `(opt <value>)`, `(max <value>)`. 예: `(constraint track_width (min 0.5mm) (opt 0.5mm) (max 1.0mm))` 또는 `(constraint track_width (min 0.5mm))`.
- 수치 인자에 수식 가능: `(constraint clearance (min 0.5mm + 0.1mm))`.

| Constraint type | 인자 타입 | 설명 |
| --- | --- | --- |
| `annular_width` | min/max | via·pad annular ring 폭 검사. |
| `assertion` | boolean expression | 식이 참인지 검사. 거짓이면 DRC 에러. Object Properties의 어떤 속성이든 사용 가능. |
| `bridged_mask` | — | copper 항목 간 solder mask 브리지 검사. min/opt/max 없음. severity와 조합해 다양한 조건에서 mask 브리징 허용/금지. |
| `clearance` | min | 다른 net copper 객체 간 **전기적** clearance(net 무관은 `physical_clearance`). 겹침(충돌) 허용은 `min`을 음수(예 `-1`)로. |
| `connection_width` | min | pad-zone 연결 폭 검사. `min`보다 좁은 pad 연결마다 에러. |
| `courtyard_clearance` | min | footprint courtyard 간 clearance. courtyard 없는 footprint는 에러 없음. 겹침 허용은 `min` 음수. |
| `creepage` | min | 다른 net copper 객체 간 creepage. |
| `diff_pair_gap` | min/opt/max | 차동쌍 평행 track 간 gap. `opt`는 새 쌍 배치 시 라우터가 사용. min~max 벗어나면 에러. 비평행 구간(fanout 등)은 미검사. |
| `diff_pair_uncoupled` | max | 차동쌍 track이 짝 track과 uncoupled로 라우팅된 거리. `max` 초과 시 에러. 비평행이거나 `diff_pair_gap` 범위 밖이면 uncoupled로 간주. |
| `disallow` | `track via through_via micro_via blind_via buried_via pad zone text graphic hole footprint` | 금지할 객체 타입(들)을 공백 구분 지정. 예 `(constraint disallow track via pad)`. 매칭되면 DRC 에러. keepout rule area와 본질 동일하나 더 구체적 제한 가능. |
| `edge_clearance` | min | 객체와 보드 외곽 clearance("밀링 공차"). `Edge.Cuts` 그래픽 + **oval** pad 홀 포함. (드릴 공차는 `physical_hole_clearance`.) 겹침 허용은 `min` 음수. |
| `hole_clearance` | min | pad/via 드릴 홀과 다른 net copper 간 clearance. 홀 중심이 아니라 직경 기준. |
| `hole_size` | min/opt/max | pad/via 드릴 홀 직경. oval 홀은 minor 직경↔`min`, major 직경↔`max`. `opt`는 라우터의 기본 via 홀 크기. |
| `hole_to_hole` | min | 기계 드릴 홀 간 clearance(중심 아닌 직경 기준). 드릴 비트 보호용. laser-drilled(microvia)·milled(oval) 홀은 미검사. |
| `length` | min/opt/max | 매칭 net의 총 라우팅 길이. `min` 미만/`max` 초과 net마다 에러. `opt`는 length 튜닝 도구의 목표 길이. |
| `min_resolved_spokes` | `0 1 2 3 4` | pad에 대한 연결(spoke) 총 수. 지정 수보다 적은 pad마다 에러. |
| `physical_clearance` | min | net 무관 두 객체 간 clearance(동일 net·비copper 레이어 포함). copper/adhesive/paste/silkscreen/mask/courtyard/edge cut 레이어만 검사. 같은 레이어끼리만(단 `Edge.Cuts`는 모든 레이어에 있는 것처럼 취급). `clearance`보다 훨씬 느림 — 가능하면 `clearance` 사용. |
| `physical_hole_clearance` | min | pad/via 드릴 홀과 다른 객체 간 clearance(net 무관, "드릴 공차"). **round** 홀만(밀링 공차는 `edge_clearance`). |
| `silk_clearance` | min | silkscreen 레이어 객체와 다른 객체 간 clearance. 겹침 허용은 `min` 음수. |
| `skew` | min/opt/max/within_diff_pairs | 매칭 net의 총 skew(각 net 길이와 최장 net 길이 차). 최장-각 net 차가 `max` 초과면 에러. 목표 skew=`opt`(없으면 `min`, 둘 다 없으면 `0`). `within_diff_pairs` 지정 시 유효 차동쌍별로 skew 개별 검사, 미지정 시 매칭 net 전체에서(버스 skew 튜닝용). |
| `solder_mask_expansion` | opt | pad·shape·track의 solder mask expansion. |
| `solder_paste_abs_margin` | opt | pad의 절대 solder paste clearance(보통 음수=inset). 최종=절대+상대. |
| `solder_paste_rel_margin` | opt | pad의 상대 solder paste clearance(보통 음수). 최종=절대+상대. |
| `text_height` | min/max | 텍스트(텍스트 박스 포함) 높이. `min` 미만/`max` 초과 항목마다 에러. |
| `text_thickness` | min/max | 텍스트 획 두께. `min` 미만/`max` 초과 항목마다 에러. |
| `thermal_relief_gap` | min | thermal-relief 연결에서 pad-zone 간 gap 폭. |
| `thermal_spoke_width` | opt | thermal-relief 연결 spoke 폭. |
| `track_angle` | min/max | 연결된 두 track 세그먼트 간 각도. min 미만/max 초과 쌍마다 에러. |
| `track_segment_length` | min/max | track·arc 세그먼트 길이. min 미만/max 초과 세그먼트마다 에러. |
| `track_width` | min/opt/max | track·arc 세그먼트 폭. `min` 미만/`max` 초과 세그먼트마다 에러. `opt`는 라우터의 기본 track 폭. |
| `via_count` | min/max | 매칭 net별 via 수. `min` 미만/`max` 초과 net마다 에러. |
| `via_dangling` | — | 미연결 또는 한 레이어만 연결된 via 검사. min/opt/max 없음. severity와 조합해 dangling via 허용/금지. |
| `via_diameter` | min/opt/max | via pad 직경. `min` 미만/`max` 초과 via마다 에러. `opt`는 라우터의 기본 via 직경. |
| `zone_connection` | `solid thermal_reliefs none` | zone-pad 연결 방식 지정. |

### Object property and function reference · #object_property_and_function_reference

커스텀 룰 식에서 테스트 가능한 속성 목록.

#### Common Properties · #common_properties

모든 PCB 객체 공통.

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Layer` | string | 객체가 존재하는 레이어. 다중 레이어 객체는 첫 레이어 반환(예 대부분 through-hole pad/via는 `F.Cu`). |
| `Locked` | boolean | 잠금 여부. |
| `Parent` | string | 부모 객체의 고유 식별자. |
| `Position_X` | dimension | 객체 원점 X 위치(원점은 bounding box 중심과 다를 수 있음). |
| `Position_Y` | dimension | 원점 Y 위치(KiCad는 내부적으로 항상 Y가 위→아래로 증가). |
| `Type` | string | "Bitmap", "Dimension", "Footprint", "Graphic", "Group", "Leader", "Pad", "Target", "Text", "Text Box", "Track", "Via", "Zone" 중 하나. |

#### Connected Object Properties · #connected_object_properties

net 할당 가능한 copper 객체(pad·via·zone·track).

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Net` | integer | net code. net code는 불변 보장 안 됨 — 특정 net 참조 시 `NetName` 사용. 단 두 객체 net 비교는 `A.Net == B.Net`이 `A.NetName == B.NetName`보다 빠름. |
| `NetClass` | string | 모든 net class의 우선순위 콤마 구분 목록(`Default` 포함 가능). 문자열이 목록의 어느 하나 또는 전체 순서와 일치하면 같음. `hasNetclass(<netclass>)`로 멤버십, `hasExactNetclass(<list>)`로 정확 일치 검사. |
| `NetName` | string | copper 객체 net명. |
| `Curved_Edges` | boolean | teardrop 곡선 가장자리 활성 여부. |
| `Enable_Teardrops` | boolean | teardrop 활성 여부. |
| `Prefer_Zone_Connections` | boolean | "Prefer zone connections" 설정 여부. |
| `Allow_Teardrops_To_Span_Two_Tracks` | boolean | "Allow teardrops to span two tracks" 설정 여부. |
| `Best_Length_Ratio` | double | teardrop 길이/객체 크기 최적 비율. |
| `Best_Width_Ratio` | double | teardrop 폭/객체 크기 최적 비율. |
| `Max_Length` | dimension | teardrop 최대 길이. |
| `Max_Width` | dimension | teardrop 최대 폭. |
| `Max_Width_Ratio` | double | teardrop의 객체 크기/track 폭 최대 허용 비율. |

#### Footprint Properties · #footprint_properties

footprint(및 그 자식 pad·graphic — pad는 부모와 같은 `Reference`·`Value`·`Component_Class`로 취급).

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Clearance_Override` | dimension | footprint copper clearance override. |
| `Component_Class` | string | 알파벳순 콤마 구분 component class 목록. 일치 규칙은 NetClass와 유사. `hasComponentClass()` / `memberOfFootprint('${Class:x}')`로도 검사. |
| `Do_not_Populate` | boolean | "Do not populate" 속성. |
| `Exclude_From_Position_Files` | boolean | "Exclude from position files" 속성. |
| `Exclude_From_Bill_of_Materials` | boolean | "Exclude from bill of materials" 속성. |
| `Exempt_From_Courtyard_Requirement` | boolean | "Exempt from courtyard requirement" 속성. |
| `Keywords` | string | 라이브러리 footprint의 "Keywords". |
| `Library_Description` | string | 라이브러리 내 footprint 설명(`Description` 필드 내용 아님). |
| `Library_Link` | string | `library_name:footprint_name` 형식 라이브러리 링크. |
| `Not_in_Schematic` | boolean | "Not in schematic" 속성. |
| `Orientation` | double | footprint 회전(도). |
| `Reference` | string | reference designator. |
| `Solderpaste_Margin_Override` | dimension | solder paste margin override. |
| `Solderpaste_Margin_Ratio_Override` | dimension | solder paste margin ratio override. |
| `Thermal_Relief_Gap` | dimension | thermal relief gap. |
| `Thermal_Relief_Width` | dimension | thermal relief 연결 폭. |
| `Value` | string | "Value" 필드 내용. |
| `Zone_Connection_Style` | string | "Inherited", "None", "Thermal reliefs", "Solid" 중 하나. |

#### Pad Properties · #pad_properties

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Clearance_Override` | dimension | pad copper clearance override. |
| `Fabrication_Property` | string | "None", "BGA pad", "Fiducial, global to board", "Fiducial, local to footprint", "Test point pad", "Heatsink pad", "Castellated pad". |
| `Hole_Size_X` / `Hole_Size_Y` | dimension | 드릴 홀/슬롯 X/Y 크기. |
| `Orientation` | double | pad 회전(도). |
| `Pad_Number` | string | pad 번호(문자열 가능, 예 BGA "A1"). |
| `Pad_Shape` | string | "Circle", "Rectangle", "Oval", "Trapezoid", "Rounded rectangle", "Chamfered rectangle", "Custom". |
| `Pad_To_Die_Length` | dimension | net 길이 계산 시 추가되는 pad-to-die 길이. |
| `Pad_Type` | string | "Through-hole", "SMD", "Edge connector", "NPTH, mechanical". |
| `Pin_Name` | string | pad 이름(보통 schematic 핀명). |
| `Pin_Type` | string | "Input", "Output", "Bidirectional", "Tri-state", "Passive", "Free", "Unspecified", "Power input", "Power output", "Open collector", "Open emitter", "Unconnected". no-connection 플래그 핀은 "+no_connect" 접미사. 와일드카드 `passive*`로 둘 다 매칭. |
| `Corner_Radius_Ratio` | double | rounded rectangle pad의 radius/크기 비율. |
| `Size_X` / `Size_Y` | dimension | pad X/Y 크기. |
| `Soldermask_Margin_Override` | dimension | solder mask margin override. |
| `Solderpaste_Margin_Override` | dimension | solder paste margin override. |
| `Solderpaste_Margin_Ratio_Override` | dimension | solder paste margin ratio override. |
| `Thermal_Relief_Gap` | dimension | thermal relief gap. |
| `Thermal_Relief_Spoke_Angle` | dimension | thermal relief 연결 각도. |
| `Thermal_Relief_Spoke_Width` | dimension | thermal relief 연결 폭. |
| `Zone_Connection_Style` | string | "Inherited", "None", "Thermal reliefs", "Solid". |

#### Track and Arc Properties · #track_and_arc_properties

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Origin_X` / `Origin_Y` | dimension | 시작점 x/y 좌표. |
| `End_X` / `End_Y` | dimension | 끝점 x/y 좌표. |
| `Width` | dimension | track/arc 폭. |

#### Via Properties · #via_properties

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Diameter` | dimension | via pad 직경. |
| `Hole` | dimension | via 완성 홀 직경. |
| `Layer_Bottom` | string | via 스택업 마지막 레이어. |
| `Layer_Top` | string | via 스택업 첫 레이어. |
| `Via_Type` | string | "Blind", "Buried", "Micro", "Through". |

#### Tuning Pattern Properties · #tuning_pattern_properties

| Property | 타입 | 설명 |
| --- | --- | --- |
| `End_X` / `End_Y` | dimension | 끝점 x/y 좌표. |
| `Min_Amplitude` / `Max_Amplitude` | dimension | 튜닝 패턴 최소/최대 진폭. |
| `Tuning_Mode` | string | "Single track", "Differential pair", "Diff pair skew". |
| `Initial_Side` | string | "Left", "Right", "Default". |
| `Min_Spacing` | dimension | 최소 간격. |
| `Corner_Radius_%` | integer | 코너 반경 퍼센트. |
| `Target_Length` | dimension | 목표 길이. |
| `Target_Skew` | dimension | 목표 skew. |
| `Override_Custom_Rules` | boolean | 커스텀 DRC 룰 오버라이드 여부. |
| `Single-sided` | boolean | 단면 여부. |
| `Rounded` | boolean | rounded meander 사용 여부. |

#### Zone and Rule Area Properties · #zone_and_rule_area_properties

copper/비copper zone, rule area(구 keepout).

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Clearance_Override` | dimension | zone copper clearance override. |
| `Hatch_Gap` | dimension | 해치 선 간 거리. |
| `Hatch_Minimum_Hole_Ratio` | float | 최소 허용 해치 홀 크기(공칭 대비 비율). |
| `Hatch_Orientation` | integer | 해치 선 각도(도). |
| `Hatch_Width` | dimension | 해치 선 폭. |
| `Min_Width` | dimension | zone 채움 영역 최소 폭. |
| `Name` | string | 사용자 지정 이름(기본 빈값). |
| `Pad_Connections` | string | "Inherited", "None", "Thermal reliefs", "Solid", "Thermal Reliefs for PTH". |
| `Priority` | integer | zone 우선순위 레벨. |
| `Thermal_Relief_Gap` | dimension | thermal relief gap. |
| `Thermal_Relief_Width` | dimension | thermal relief 연결 폭. |

#### Graphic Shape Properties · #graphic_shape_properties

그래픽 선·호·원·사각·다각형.

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Angle` | dimension | 호의 각도. |
| `End_X` / `End_Y` | dimension | 끝점 x/y. |
| `Filled` | boolean | 채움 여부. |
| `Line_Width` | dimension | 획 두께. |
| `Line_Style` | string | "Solid", "Dashed", "Dotted", "Dash-Dot", "Dash-Dot-Dot". |
| `Shape` | string | "Segment", "Rectangle", "Arc", "Circle", "Polygon", "Bezier". |
| `Start_X` / `Start_Y` | dimension | 시작점 x/y. |

#### Text Properties · #text_properties

텍스트 객체(footprint 필드·자유 텍스트 라벨 등).

| Property | 타입 | 설명 |
| --- | --- | --- |
| `Bold` | boolean | 굵게 여부. |
| `Height` | dimension | 문자 높이. |
| `Horizontal_Justification` | string | "Left", "Center", "Right". |
| `Italic` | boolean | 이탤릭 여부. |
| `Knockout` | boolean | knockout 속성. |
| `Mirrored` | boolean | 미러 여부. |
| `Name` | string | footprint 필드 이름(필드 아닌 텍스트는 빈 문자열). |
| `Text` | string | 텍스트 내용. |
| `Thickness` | dimension | 폰트 획 두께. |
| `Width` | dimension | 문자 폭. |
| `Vertical_Justification` | string | "Top", "Center", "Bottom". |
| `Visible` | boolean | 표시 여부. |

#### Expression functions · #expression_functions

커스텀 룰 식에서 객체에 호출 가능한 함수.

| Function | 객체 | 설명 |
| --- | --- | --- |
| `enclosedByArea('x')` | A or B | 객체 전체가 명명된 rule area/zone 내부면 true. `intersectsArea()`보다 느림. |
| `existsOnLayer('layer_id')` | A or B | 주어진 레이어에 객체가 존재하면 true. |
| `fromTo('x', 'y')` | A or B | 객체가 두 pad 사이 copper 경로상에 있으면 true. `x`,`y`=`'RefDes-PadNumber'`(예 `'U1-A5'`) 또는 RefDes 단독(footprint 모든 pad). `*`,`?` 와일드카드 지원. (From-To 참조) |
| `getField('x')` | A or B | 객체의 필드 `x` 값(footprint만 필드 보유). |
| `hasComponentClass('x')` | A or B | 객체/부모 footprint의 component class 집합이 `x`를 포함하면 true. |
| `hasExactNetclass('x')` | A or B | 객체 net class 집합이 `x`와 정확히 일치하면 true. |
| `hasNetclass('x')` | A or B | 객체 net class 집합이 `x`를 포함하면 true. |
| `inDiffPair('x')` | A or B | 객체가 차동쌍의 일부이고 base name이 `x`와 일치하면 true. 예 `inDiffPair('/USB_')`는 `/USB_P`·`/USB_N`에 true. `*`,`?` 지원. 반대 극성 net이 없으면 항상 false. |
| `insideArea('x')` | A or B | 객체 일부가 명명 area/zone 내부면 true. **Deprecated** — `intersectsArea()` 사용. |
| `insideCourtyard('x')` `insideFrontCourtyard('x')` `insideBackCourtyard('x')` | A or B | 객체 일부가 footprint courtyard 내부면 true. `x`=refdes(와일드카드), 라이브러리 ID, 또는 `${Class:ClassName}`. **Deprecated** — `intersectsCourtyard()` 등 사용. |
| `intersectsArea('x')` | A or B | 객체 일부가 명명 area/zone 내부면 true(copper zone은 채워진 영역 기준). |
| `intersectsCourtyard('x')` `intersectsFrontCourtyard('x')` `intersectsBackCourtyard('x')` | A or B | 객체 일부가 footprint courtyard(전체/front/back) 내부면 true. `x`=refdes(와일드카드)/라이브러리 ID/`${Class:ClassName}`. |
| `isBlindVia()` | A or B | blind via면 true. |
| `isBuriedVia()` | A or B | buried via면 true. |
| `isBlindBuriedVia()` | A or B | blind 또는 buried via면 true. |
| `isCoupledDiffPair()` | AB | 두 객체가 같은 차동쌍의 반대 극성이면 true(예 A=`/USB+`, B=`/USB-`). |
| `isMicroVia()` | A or B | microvia면 true. |
| `isPlated()` | A or B | (pad/via) plated 홀이면 true. |
| `memberOf('x')` | A or B | 명명 그룹 `x` 멤버면 true. **Deprecated** — `memberOfGroup()` 사용. |
| `memberOfGroup('x')` | A or B | 그룹 `x` 멤버면 true. |
| `memberOfFootprint('x')` | A or B | footprint 멤버면 true. `x`=refdes(와일드카드)/라이브러리 ID/`${Class:ClassName}`. |
| `memberOfSheet('x')` | A or B | schematic 시트 `x` 멤버면 true(자식 시트 미포함, 와일드카드 지원). 자식 포함은 `memberOfSheetOrChildren()`. |
| `memberOfSheetOrChildren('x')` | A or B | 시트 `x` 또는 그 자식 시트 멤버면 true. |

### From-To signal path matching · #from-to-signal-path-matching

- 고속 PCB에서 net 전체 제약은 너무 거칠다. From-To 경로는 두 특정 pad 사이의 설계자 정의 신호 경로 — net에서 타이밍 핵심 구간만 골라 길이/skew 등 룰을 적용. Altium의 xSignals와 유사.

#### How From-To paths work · #how_from_to_paths_work

`fromTo()` 사용 시 KiCad가 From-To 경로를 평가하는 과정:
1. **Endpoint discovery**: 모든 footprint를 스캔해 `RefDes-PadNumber`(예 `U1-A5`, `R3-1`) 형식 endpoint 목록 구축. refdes 단독(`U1`)으로 모든 pad 매칭.
2. **Pad matching**: `from`/`to` 인자를 와일드카드(`*`,`?`)로 endpoint와 비교. 대소문자 무관.
3. **Path tracing**: 같은 net을 공유하는 매칭 endpoint 쌍마다 copper 연결을 추적해 경로(track·via·pad) 발견.
4. **Uniqueness check**: 두 pad 사이 경로가 유일한지 판정. 다중 경로(예 ground plane으로 연결)면 경로는 찾되 non-unique로 표시.

💡 `from` 패턴이 같은 net에서 `to` 패턴과 매칭되는 pad를 둘 이상 가지면 경로가 모호해 생성되지 않음. 패턴을 각 끝에서 정확히 하나의 pad로 좁힐 것.

#### Pad name format · #pad_name_format

| Format | 설명 |
| --- | --- |
| `RefDes-PadNumber` | 특정 footprint의 특정 pad(`'U1-A5'`=U1의 pad A5). |
| `RefDes` | footprint의 모든 pad(`'U1'`=U1 전체 pad). |
| Wildcards | `*`,`?` 지원. `'U1-A*'`=U1에서 번호가 A로 시작하는 pad, `'R?-1'`=단일 문자 R로 시작하는 refdes의 pad 1. |

#### Using fromTo() in custom DRC rules · #using_fromto_in_custom_drc_rules

- `condition` 절에서 사용. 두 문자열 인자(from/to). 테스트 객체(A 또는 B)가 두 pad 사이 copper 경로상에 있으면 true.
```
(rule <name>
    (condition "A.fromTo('<from_pad>', '<to_pad>')")
    (constraint <constraint_type> <arguments>))
```
- 자주 결합하는 constraint: `length`(경로별 길이), `skew`(경로군 길이 매칭, 예 DDR 버스), `track_width`(고속 경로 폭), `clearance`(경로별 clearance), `diff_pair_gap`(구간별 차동쌍 간격).

#### From-To path examples · #from_to_path_examples

##### Length-constrain a specific signal path · #length_constrain_a_specific_signal_path

```
# Constrain the DDR clock path from the controller to the DRAM
(rule "DDR_CLK length"
    (condition "A.fromTo('U1-C5', 'U2-D3')")
    (constraint length (min 20mm) (max 25mm)))
```

##### Match lengths across a DDR data bus · #match_lengths_across_a_ddr_data_bus

```
# Match data signal lengths from memory controller to DRAM
# Each data line has its own fromTo path; the skew constraint
# checks that all matching paths are within tolerance
(rule "DDR_DQ0 length"
    (condition "A.fromTo('U1-A1', 'U2-B1')")
    (constraint length (max 50mm)))

(rule "DDR_DQ1 length"
    (condition "A.fromTo('U1-A2', 'U2-B2')")
    (constraint length (max 50mm)))

(rule "DDR_DQ2 length"
    (condition "A.fromTo('U1-A3', 'U2-B3')")
    (constraint length (max 50mm)))

(rule "DDR_DQ3 length"
    (condition "A.fromTo('U1-A4', 'U2-B4')")
    (constraint length (max 50mm)))

# Constrain skew across all DQ paths
(rule "DDR_DQ skew"
    (condition "A.fromTo('U1-A*', 'U2-B*')")
    (constraint skew (max 0.2mm)))
```

##### USB signal path constraints · #usb_signal_path_constraints

```
# USB data path track width
(rule "USB track width"
    (condition "A.fromTo('J1-D*', 'U1-H*')")
    (constraint track_width (min 0.09mm) (opt 0.09mm) (max 0.09mm)))

# USB data path length constraint
(rule "USB path length"
    (condition "A.fromTo('J1-D*', 'U1-H*')")
    (constraint length (max 80mm)))
```

##### PCIe lane length matching · #pcie_lane_length_matching

```
# PCIe TX lane length matching from connector to controller
(rule "PCIe TX length"
    (condition "A.fromTo('J1-TX*', 'U1-TX*')")
    (constraint length (min 40mm) (max 60mm)))

# PCIe RX lane length matching from connector to controller
(rule "PCIe RX length"
    (condition "A.fromTo('J1-RX*', 'U1-RX*')")
    (constraint length (min 40mm) (max 60mm)))
```

##### Series termination resistor paths · #series_termination_resistor_paths

```
# Segment from driver to series resistor (keep short)
(rule "CLK driver to resistor"
    (condition "A.fromTo('U1-C5', 'R1-1')")
    (constraint length (max 10mm)))

# Segment from series resistor to receiver (length-controlled)
(rule "CLK resistor to receiver"
    (condition "A.fromTo('R1-2', 'U2-D3')")
    (constraint length (min 20mm) (max 30mm)))
```

💡 net이 직렬 부품(종단 저항 등)을 지나면 부품 pad에서 net이 바뀐다. 각 구간(driver→저항, 저항→receiver)을 별도 `fromTo()` 경로로 정의해 독립 제어.

##### Clearance between high-speed paths and other nets · #clearance_between_high_speed_paths_and_other_nets

```
# Extra clearance around high-speed clock path
(rule "CLK clearance"
    (condition "A.fromTo('U1-C5', 'U2-D3')")
    (constraint clearance (min 0.3mm)))
```

### Custom design rule examples · #custom_design_rule_examples

#### Basic examples · #basic_examples

```
(rule RF_width
    (layer outer)
    (condition "A.hasNetclass('RF')")
    (constraint track_width (min 0.35mm) (max 0.35mm)))

(rule "BGA neckdown"
    (constraint track_width (min 0.2mm) (opt 0.25mm))
    (constraint clearance (min 0.05mm) (opt 0.08mm))
    (condition "A.intersectsCourtyard('U3')"))

# Specify an optimal gap for a particular differential pair
(rule "Clock gap"
    (condition "A.inDiffPair('/CLK')")
    (constraint diff_pair_gap (opt 0.8mm)))

# Specify a larger clearance between differential pairs and anything else
(rule "Differential pair clearance"
    (condition "A.inDiffPair('*') && !AB.isCoupledDiffPair()")
    (constraint clearance (min 1.5mm)))

(rule "copper keepout"
    (constraint disallow track via zone)
    (condition "A.intersectsArea('zone3')"))

(rule "minimum creepage distance for high voltage nets"
    (condition "A.hasNetclass('HV')")
    (constraint creepage (min 5mm)))
```

#### Various clearances · #various_clearances

```
(rule "Clearance between Pads of Different Nets"
    (constraint clearance (min 3.0mm))
    (condition "A.Type == 'Pad' && B.Type == 'Pad' && A.Net != B.Net"))

(rule "Pad to Track Clearance"
    (constraint clearance (min 0.2mm))
    (condition "A.Type == 'Pad' && B.Type == 'Track'"))

# Enforce a clearance around pads (and other copper objects) in a specific footprint
(rule "Pad clearance in R1"
    (constraint clearance (min 1mm))
    (condition "A.memberOfFootprint('TP1')"))

# Enforce a mechanical clearance between components and board edge
(rule front_mechanical_board_edge_clearance
    (layer "F.Courtyard")
    (constraint physical_clearance (min 3mm))
    (condition "B.Layer == 'Edge.Cuts'"))

# Prevent copper pours under capacitors
(rule "No copper pours under capacitors"
    (constraint physical_clearance (min 0.1mm))
    (condition "A.Type == 'Zone' && B.Reference == 'C*'")
)

# This assumes that there is a cutout with 1mm thick lines
(rule "Clearance to cutout"
    (constraint edge_clearance (min 0.8mm))
    (condition "A.Layer=='Edge.Cuts' && A.Line_Width == 1.0mm"))

# prevent silk over tented vias
(rule silk_over_via
    (constraint silk_clearance (min 0.2mm))
    (condition "A.Type == '*Text' && B.Type == 'Via'"))

(rule "Allow connector silk to intersect board edge"
    (constraint silk_clearance)
    (severity ignore)
    (condition "A.memberOfFootprint('J*') && B.Layer=='Edge.Cuts'"))

(rule "Distance between Vias of Different Nets"
    (constraint hole_to_hole (min 0.254mm))
    (condition "A.Type == 'Via' && B.Type == 'Via' && A.Net != B.Net"))

(rule "Via Hole to Track Clearance"
    (constraint hole_clearance (min 0.254mm))
    (condition "A.Type == 'Via' && B.Type == 'Track'"))

(rule "Distance between test points"
    (constraint courtyard_clearance (min 1.5mm))
    (condition "A.Reference =='TP*' && B.Reference == 'TP*"))
```

#### High-current design rules · #high_current_design_rules

```
# Check current-carrying capacity
(rule high-current
    (constraint track_width (min 1.0mm))
    (constraint connection_width (min 0.8mm))
    (condition "A.hasNetclass('Power')"))

# Don't use thermal reliefs on heatsink pads
(rule heat_sink_pad
    (constraint zone_connection solid)
    (condition "A.Fabrication_Property == 'Heatsink pad'"))

# Require all four thermal relief spokes to connect to parent zone
(rule fully_spoked_pads
    (constraint min_resolved_spokes 4))

# Set thermal relief gap & spoke width for all zones
(rule defined_relief
    (constraint thermal_relief_gap (min 10mil))
    (constraint thermal_spoke_width (min 12mil)))

# Override thermal relief gap & spoke width for GND and PWR zones
(rule defined_relief_pwr
    (constraint thermal_relief_gap (min 10mil))
    (constraint thermal_spoke_width (min 12mil))
    (condition "A.Name == 'zone_GND' || A.Name == 'zone_PWR'"))

# Prevent solder wicking from SMD pads
(rule holes_in_pads
    (constraint physical_hole_clearance (min 0.2mm))
    (condition "B.Pad_Type == 'SMD'"))

# Disallow solder mask margin overrides
(rule "disallow solder mask margin overrides"
    (constraint assertion "A.Soldermask_Margin_Override == null")
    (condition "A.Type == 'Pad'"))
```

#### Hole sizes · #hole_sizes

```
(rule "Max Drill Hole Size Mechanical"
    (constraint hole_size (max 6.3mm))
    (condition "A.Pad_Type == 'NPTH, mechanical'"))

(rule "Max Drill Hole Size PTH"
    (constraint hole_size (max 6.35mm))
    (condition "A.Pad_Type == 'Through-hole'"))

# Separate drill bit and milling cutter size constraints
(rule "Plated through-hole size"
    (constraint hole_size (min 0.2mm) (max 6.35mm))
    (condition "A.isPlated() && A.Hole_Size_X == A.Hole_Size_Y"))

(rule "Plated slot size"
    (constraint hole_size (min 0.5mm))
    (condition "A.isPlated() && A.Hole_Size_X != A.Hole_Size_Y"))
```

#### Solder mask and solder paste · #solder_mask_and_solder_paste

```
# No solder mask expansion for vias
(rule "no mask expansion on vias"
    (constraint solder_mask_expansion (opt 0mm))
    (condition "A.type == via"))

# Remove solder paste from DNP footprints
(rule remove_solder_paste_from_DNP
    (constraint solder_paste_abs_margin (opt -50mm))
    (condition "A.Do_not_Populate"))

# Allow solder mask bridging under guard ring mask apertures
(rule guard_ring_bridging
    (constraint bridged_mask)
    (condition "A.intersectsArea('guard_ring')")
    (severity ignore))
```

#### Dangling vias · #dangling_vias

```
# allow dangling vias within a specific rule area named 'dangling vias allowed'
(rule ignore_left
    (constraint via_dangling)
    (condition "A.enclosedByArea('dangling vias allowed')")
    (severity ignore))
```

---

## Scripting · #scripting

- KiCad 작업을 Python으로 자동화. PCB 편집용 `pcbnew` API는 인터랙티브/독립 스크립트로 사용. Board Editor 스크립트는 "action plugin"(상단 툴바 아이콘)으로 구성 가능. Footprint Editor용 별도 Footprint Wizard API도 있음.
- 최신 API 레퍼런스는 Doxygen 문서: https://docs.kicad.org/doxygen-python-10.0/namespaces.html
- KiCad 6+는 스크립팅에 Python 3 필요(Python 2 미지원).

### Using the scripting console · #using_the_scripting_console

- 내장 Python 콘솔로 보드를 검사·조작. 상단 툴바의 Scripting console 버튼으로 실행. API는 자동 로드 안 됨 → `import pcbnew` 입력. `pcbnew.GetBoard()`로 현재 로드된 보드 참조를 반환받아 검사·수정.

### Python script locations · #python_script_locations

- 플러그인(PCB action plugin, footprint wizard)은 PCM으로 자동 설치하거나, 각자 자기 폴더에 넣어 `plugins` 폴더에 수동 복사. 기본 `plugins` 폴더 위치:

| Platform | Path |
| --- | --- |
| Linux | `~/.local/share/kicad/10.0/scripting/plugins` |
| macOS | `~/Documents/KiCad/10.0/scripting/plugins` |
| Windows | `%USERPROFILE%\Documents\KiCad\10.0\scripting\plugins` |

💡 플러그인 종류는 상속 클래스로 결정: `FootprintWizardBase.FootprintWizard` 상속=footprint wizard, `pcbnew.ActionPlugin` 상속=action plugin.

### pcbnew API overview · #pcbnew_api_overview

- 스크립팅 API는 Board Editor 내부 객체 구조를 반영하며 `pcbnew` 모듈로 제공.

⚠️ API는 KiCad 내부와 밀결합되어 시간에 따라 변하며 안정적이지 않음. 해당 버전의 Doxygen 문서 참조.

- 보통 `GetBoard()`로 시작 → 현재 열린 보드의 `BOARD` 객체 반환. `BOARD`는 footprint·zone·track·via·text 등 각 객체 타입 집합과 속성을 가짐.
- 객체 접근 메서드(반복 가능 리스트 반환):
  - `board.GetFootprints()`: 모든 footprint.
  - `board.GetDrawings()`: 기타 보드 객체.
  - `board.GetTracks()`: 모든 track·via.
  - `board.GetZones()`: 모든 zone.
  - `board.GetNetClasses()`: 디자인 룰의 모든 net class.
- 디스크 입출력:
  - `LoadBoard(filename)`: 파일에서 보드 로드(확장자로 포맷 판정), `BOARD` 반환.
  - `SaveBoard(filename, board)`: `BOARD`를 파일로 저장(확장자로 포맷).
  - `board.Save(filename)`: `SaveBoard()`와 동일한 `BOARD` 메서드.

#### Examples · #examples_2

Value 숨김 / Reference 표시:
```python
#!/usr/bin/env python3
import sys
from pcbnew import LoadBoard

filename = sys.argv[1]

pcb = LoadBoard(filename)
for fp in pcb.GetFootprints():
    print(f"* Footprint: {fp.GetReference()}")
    fp.Value().SetVisible(False)      # set Value as Hidden
    fp.Reference().SetVisible(True)   # set Reference as Visible

pcb.Save("mod_" + filename)
```

U304의 pad solder paste margin 조정:
```python
#!/usr/bin/env python3
import sys
from pcbnew import *

filename=sys.argv[1]
pcb = LoadBoard(filename)

# Find module U304
u304 = pcb.FindFootprintByReference('U304')
pads = u304.Pads()

#  Iterate over pads, printing solder paste margin
for p in pads:
    print(p.GetPadName(), ToMM(p.GetLocalSolderPasteMargin()))
    id = int(p.GetPadName())
    # Set margin to 0 for all but pad (pin) 15
    if id<15: p.SetLocalSolderPasteMargin(0)

pcb.Save("mod_"+filename)
```

.pretty 라이브러리 footprint·pad 열거:
```python
#!/usr/bin/env python3
from pcbnew import *

libpath = "/usr/share/kicad/footprints/Connector_PinSocket_2.54mm.pretty"
print(f">> enumerate footprints, pads of {libpath}")

# Load the suitable plugin to read/write the .pretty library
src_type = PCB_IO_MGR.GuessPluginTypeFromLibPath( libpath );
# We can force the plugin type by using IO_MGR.PluginFind( IO_MGR.KICAD )
plugin = PCB_IO_MGR.PluginFind( src_type )

# Print plugin type name: (Expecting "KiCad" for a .pretty library)
print(f"Selected plugin type: {PCB_IO_MGR.ShowType(src_type)}")

list_of_footprints = plugin.FootprintEnumerate(libpath)

for name in list_of_footprints:
    fp = plugin.FootprintLoad(libpath,name)
    print(name)
    print(f"  -> {fp.GetReference()} {fp.GetValue()} {fp.GetLibDescription()}")
    for pad in fp.Pads():
        print(
            f"    pad [{pad.GetPadName()}] at "
            f"pos ({ToMM(pad.GetPosition().x)}, {ToMM(pad.GetPosition().y)}) mm,",
            f"shape offset ({ToMM(pad.GetOffset().x)}, {ToMM(pad.GetOffset().y)}) mm"
        )
    print()
```

Track/Via, Text/Shape, Footprint, Zone, Netclass 열거(통계 출력):
```python
#!/usr/bin/env python
import sys
from pcbnew import *

filename=sys.argv[1]
pcb = LoadBoard(filename)

print("Listing Tracks and Vias:")
for item in pcb.GetTracks():
    if type(item) is PCB_VIA:
        pos = item.GetPosition()
        drill = item.GetDrillValue()
        width = item.GetWidth()
        print(f" * Via:   {ToMM(pos)} - {ToMM(drill)}/{ToMM(width)}")
    elif type(item) is PCB_TRACK:
        start = item.GetStart()
        end = item.GetEnd()
        width = item.GetWidth()
        print(f" * Track: {ToMM(start)} to {ToMM(end)}, width {ToMM(width)}")
    else:
        print(f"Unknown type    {type(item)}")

print("Listing Footprints")
for fp in pcb.GetFootprints():
    print(f"* Footprint: {fp.GetReference()} at {ToMM(fp.GetPosition())}")

print(f"Ratsnest count: {pcb.GetNetCount()}")
print(f"Track width count: {len(pcb.GetTrackWidthList())}")
print(f"Via size count: {len(pcb.GetViasDimensionsList())}")

print(f"Listing Zones: {pcb.GetAreaCount()}")
for idx in range(0, pcb.GetAreaCount()):
    zone = pcb.GetArea(idx)
    print(f"zone: {idx} priority: {zone.GetAssignedPriority()} netname: {zone.GetNetname()}")

print(f"Netclasses: {len(pcb.GetAllNetClasses())}")
```

### Action plugins · #action_plugins_2

- 스크립트를 PCB Editor GUI 버튼에 연결. 버튼 클릭 시 스크립트 실행. **Tools → External plugins** 메뉴에 표시되며 Preferences의 **Action Plugins** 페이지에서 활성화 시 툴바에도 표시.
- 아래 예제는 텍스트 항목의 `$date$`를 현재 날짜로 치환하는 action plugin:
```python
import pcbnew
import re
import datetime

class text_by_date(pcbnew.ActionPlugin):
    """
    test_by_date: A sample plugin as an example of ActionPlugin
    Add the date to any text field of the board containing '$date$'
    """

    def defaults(self):
        self.name = "Add date on PCB"
        self.category = "Modify PCB"
        self.description = "Automatically add date on an existing PCB"

    def Run(self):
        pcb = pcbnew.GetBoard()
        for item in pcb.GetDrawings():
            if item.GetClass() == "PCB_TEXT":
                txt = re.sub("\$date\$ [0-9]{4}-[0-9]{2}-[0-9]{2}",
                                 "$date$", item.GetText())
                if txt == "$date$":
                    item.SetText("$date$ %s" % datetime.date.today())

text_by_date().register()
```

### Footprint wizards · #creating-footprint-wizards

- Footprint Editor에서 접근하는 Python 스크립트. 파라미터 선택지를 제시하고 값에 따라 footprint 생성.
- 생성 3단계:
  1. `FootprintWizardBase.FootprintWizard` 상속 Python 클래스 인스턴스화.
  2. 6개 필수 함수 정의: `GetName()`, `GetDescription()`, `GetValue()`, `GenerateParameterList()`, `CheckParameters()`, `BuildThisFootprint()`.
  3. `{your_class_name}().register()` 호출로 등록.
- `GetName()`/`GetDescription()`/`GetValue()`는 UI용 문자열 반환만.
- `GenerateParameterList()`: 파라미터를 `page`+`name` 형식으로 그룹화. 예 `self.AddParam("demo", "radius", self.uMM, 5)` → demo 페이지에 radius 추가. 조회는 `self.footprint_radius = self.parameters["demo"]["radius"]`.
- `CheckParameters()`: 파라미터 데이터 검증. 위 `self.parameters[...]` 호출도 여기에.
- `BuildThisFootprint()`: footprint 생성 단계 호출.
- `register()` 호출은 파일 끝 또는 `__init__.py`에 둘 수 있음(둘 다 지원).

💡 KiCad는 오류(예 `NotImplementedError`)를 낸 플러그인을 재로드하지 않음 → KiCad를 완전히 종료·재시작해야 함. 단 오류 없는 변경은 해당 안 됨.

---

## IDF component outlines · #idf-component-outlines

- KiCad는 기계 CAD용 IDF 보드 표현을 export 가능. 아래는 footprint에 IDF 아웃라인 부착, 신규 작성, 동봉 IDF 유틸리티 설명.

### Specifying component models for use by the exporter · #specifying_component_models_for_use_by_the_exporter

- IDF 모델은 footprint의 3D model 속성으로 부착. IDF exporter는 3D viewer 등과 다른 파일 타입을 쓰므로 충돌 없음.
- 부착: footprint 속성 편집 → **3D Models** 탭 → folder 버튼 → **IDF (*.idf;*.IDF)** 필터 선택 → 아웃라인 파일 선택.
- offset/rotation 값 입력. offset은 IDF 보드 출력 단위(mm/mil), IDF 좌표계(우손 좌표계: +Z=뷰어 방향, +X=뷰어 우측, +Y=화면 상단)로. rotation은 도 단위, 양수=반시계(IDFv3 사양). 여러 아웃라인을 offset과 조합해 DIP-소켓 같은 단순 조립체 표현 가능.

💡 IDF exporter는 offset 값과 Z rotation 값만 사용하고 나머지는 무시.

### Creating a component outline file · #creating_a_component_outline_file

- 아웃라인 파일(`*.idf`)은 단일 `.ELECTRICAL` 또는 `.MECHANICAL` 섹션. 앞에 임의 개수 주석 줄 가능(라이브러리 파일로 복사됨, 메타데이터 추적용).
- 필드는 문자열/정수/부동소수점. 문자열은 공백 포함 시 인용 필수(인용부호 안에 인용부호 불가). 부동소수점은 십진/지수 표기 가능(십진 권장), 소수점은 dot(콤마 아님). 7-bit ASCII만(8-bit 사용 시 undefined).
- 구조: SECTION → RECORD(한 줄) → FIELD(공백 구분). 아웃라인 파일은 한 종류 섹션만(`.ELECTRICAL` 또는 `.MECHANICAL`).
- 섹션 헤딩=Record 1. Record 2(4 필드):
  1. **Geometry Name**: Part Number와 합쳐 고유 식별자(표준 패키지는 패키지명, 예 "SOT-23").
  2. **Part Number**: 패키지 설명에 활용(예 geometry가 "TO-92"면 pad 배치/방향 설명).
  3. **IDF Unit**: `MM` 또는 `THOU`(이 아웃라인에만 적용).
  4. **Height**: 부동소수점 공칭 높이(Field 3 단위).
- Record 3(여러 개, 4 필드 — 아웃라인 정의):
  1. **Loop Index**: `0`(반시계 순서) 또는 `1`(시계 순서).
  2. **X coordinate**: 부동소수점.
  3. **Y coordinate**: 부동소수점.
  4. **Included Angle**: 부동소수점. `0`=직선, `360`=이전 점이 원 중심·이 점이 원 위의 점(`-360`은 금지), 음수=시계 호, 양수=반시계 호.
- 닫힌 루프 1개만, cutout 불가. 마지막 점=첫 점(원이 아닌 경우).

Example IDF File 1:
```
# a simple cylinder - this could represent an electrolytic capacitor
.ELECTRICAL
    "cylinder" "5mm OD, 5mm height" MM 5
    0 0 0 0
    0 2.5 0 360
.END_ELECTRICAL
```

Example IDF File 2:
```
# an upside-down T
# a comment added for the sake of adding comments
.ELECTRICAL
    "Capital T" "5x8x10mm, upside down" MM 10
    0 -0.5 8 0
    0 -0.5 0.5 0
    0 -2.5 0.5 0
    0 -2.5 -0.5 180
    0 2.5 -0.5 0
    0 2.5 0.5 180
    0 0.5 0.5 0
    0 0.5 8 0
    0 -0.5 8 180
.END_ELECTRICAL
```

### Guidelines for creating outlines · #guidelines_for_creating_outlines

#### Package naming · #package_naming

- 파일명에 아웃라인 정보를 담을 것. 예 axial leaded cylindrical 패키지는 horizontal/vertical 구분 + 주요 치수(diameter, length, pitch). 고유 아웃라인은 제조사 part number + 장치 클래스 prefix.

#### Comments · #comments

- IDF 파일 주석으로 아웃라인 정보(예 치수 출처) 제공.

#### Geometry and Part Number entries · #geometry_and_part_number_entries

- Geometry + Part Number는 합쳐서 MCAD 시스템의 고유 ID 역할. 사용자에게 의미 있되 주 용도는 고유 ID. 큰 컬렉션 내에서 고유하면 충돌이 줄어듦.

#### Pin orientation and positioning · #pin_orientation_and_positioning

- 아웃라인은 대응 footprint의 방향·위치에 맞춰 작성(비0 rotation 불필요). IDF exporter가 (X,Y) offset을 무시하므로 IDF 아웃라인에 올바른 원점 사용이 필수.
- (참고: idfcyl/idfrect로 생성한 샘플 아웃라인 예 — 수직 radial/axial leaded cylinder, horizontal cylinder, square(plain/chamfer/axial lead) 등.)

#### Tips on dimensions · #tips_on_dimensions

- 압출 아웃라인은 부품의 위치·점유 공간을 기계 설계자에게 전달하는 용도. 대개 정확도는 중요치 않으나 가능한 좋은 기계 정보를 담는 게 좋음(예 케이스에 빠듯이 넣는 경우). 부실한 아웃라인은 모델 교체에 시간 낭비를 초래.

### IDF Component Outline Tools · #idf_component_outline_tools

- IDF 아웃라인 생성용 커맨드라인 툴:
  1. `idfcyl`: 수직/수평, axial/radial lead 실린더 아웃라인.
  2. `idfrect`: axial lead 또는 좌상단 chamfer가 있을 수 있는 사각형 아웃라인.
  3. `dxf2idf`: DXF 도면을 IDF 아웃라인으로 변환.

#### idfcyl · #idfcyl

- 실린더형 부품 아웃라인 생성. 인자 없이 실행 시 사용법·입력 요약 출력:
```
idfcyl: This program generates an outline for a cylindrical component.
    The cylinder may be horizontal or vertical.
    A horizontal cylinder may have wires at one or both ends.
    A vertical cylinder may have at most one wire which may be
    placed on the left or right side.

Input:
    Unit: mm, in (millimeters or inches)
    Orientation: V (vertical)
    Lead type: X, R (axial, radial)
    Diameter of body
    Length of body
    Board offset
    *   Wire diameter
    *   Pitch
    **  Wire side: L, R (left, right)
    *** Lead length
    File name (must end in *.idf)

    NOTES:
        *   only required for horizontal orientation or
            vertical orientation with axial leads
        **  only required for vertical orientation with axial leads
        *** only required for horizontal orientation with radial leads
```
- 임의 인자를 주면 notes 출력 억제. 스크립트 예(수직 5mm 실린더, axial wire 우측):
```
#!/bin/bash
idfcyl - 1 > /dev/null <<  _EOF
mm
v
x
5
8
3
0.8
3.5
r
cylvmm_1R_D5_L8_Z3_WD0.8_P3.5.idf
_EOF
```

#### idfrect · #idfrect

- 사각형 부품 아웃라인 생성. 인자 없이 실행 시 사용법 출력:
```
idfrect: This program generates an outline for a rectangular component.
    The component may have a single lead (axial) or a chamfer on the
    upper left corner.
Input:
    Unit: mm, in (millimeters or inches)
    Width:
    Length:
    Height:
    Chamfer: length of the 45 deg. chamfer
    *  Leaded: Y,N (lead is always to the right)
    ** Wire diameter
    ** Pitch
    File name (must end in *.idf)

    NOTES:
        *   only required if chamfer = 0
        **  only required for leaded components
```
- 스크립트 예(chamfer 사각형 + axial leaded):
```
#!/bin/bash
# 10x10, 1mm chamfer, 2mm height
idfrect - 1 > /dev/null <<  _EOF
mm
10
10
2
1
rectMM_10x10x2_C0.5.idf
_EOF
# 10x10x12,  0.8mm lead on 6mm pitch
idfrect - 1 > /dev/null <<  _EOF
mm
10
10
12
0
Y
0.8
6
rectLMM_10x10x12_D0.8_P6.0.idf
_EOF
```

#### dxf2idf · #dxf2idf

- DXF 아웃라인에서 IDF 부품 파일 생성. DXF는 LibreCAD로 준비 권장. 인자 없이 실행 시 사용법 출력:
```
dxf2idf: this program takes line, arc, and circle segments
    from a DXF file and creates an IDF component outline file.

Input:
    DXF filename: the input file, must end in '.dxf'
    Units: mm, in (millimeters or inches)
    Geometry Name: string, as per IDF version 3.0 specification
    Part Name: as per IDF version 3.0 specification of Part Number
    Height: extruded height of the outline
    Comments: all non-empty lines are comments to be added to
        the IDF file. An empty line signifies the end of
        the comment block.
    File name: output filename, must end in '.idf'
```
- 스크립트 예(`test.dxf`에서 5mm 높이 아웃라인):
```
#!/bin/bash
dxf2idf - 1 > /dev/null << _EOF
test.dxf
mm
DXF TEST GEOMETRY
DXF TEST PART
5
This is an IDF test file produced from the outline 'test.dxf'
This is a second IDF comment to demonstrate multiple comments

test_dxf2idf.idf
_EOF
```

#### idf2vrml · #idf2vrml

- IDF Board(`.emn`) + IDF Component(`.emp`) 1쌍을 읽어 VRML 파일 생성(MCAD 없이 보드 조립 시각화). 인자 없이 실행 시 사용법:
```
>./idf2vrml
Usage: idf2vrml -f input_file.emn -s scale_factor {-k} {-d} {-z} {-m}
flags:
   -k: produce KiCad-friendly VRML output; default is compact VRML
   -d: suppress substitution of default outlines
   -z: suppress rendering of zero-height outlines
   -m: print object mapping to stdout for debugging purposes
example to produce a model for use by KiCad: idf2vrml -f input.emn -s 0.3937008 -k
```

💡 `idf2vrml`은 `.emn` 파일에서 PCB 뒷면에 지정된 `OTHER_OUTLINE` 엔티티를 올바로 렌더링하지 못함. 단 KiCad export 파일에는 그런 엔티티 지정 메커니즘이 없어 문제 없음 — 뒷면 엔티티를 쓰는 제3자 emn 파일 렌더 시에만 해당.
