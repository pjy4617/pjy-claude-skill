# KiCad 프로젝트 매니저 · 환경 · 파일/라이브러리 — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/kicad/kicad.html

> **범위**: 소개·시스템요구사항, 설치/업그레이드·최초설정(First time setup), 프로젝트 매니저(생성/임포트/백업/아카이브/Git 연동), KiCad 파일·폴더 구조, 경로 변수·환경변수·라이브러리 설정, Jobsets, 프로젝트 템플릿, Plugin & Content Manager, 환경설정(Preferences), 프로젝트 매니저 단축키(Actions reference)

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/kicad/kicad.html#<anchor>

## 목차

- [Introduction](#introduction) — KiCad 개요(회로도+PCB 통합 워크플로, 최대 32 copper layers)
- [System Requirements](#system_requirements) — 시스템 요구사항(권장 1920x1080+, 전용 GPU)
- [Installing and Upgrading KiCad](#installing_and_upgrading_kicad) — 설치/업그레이드 개요
- [First time setup](#settings) — 최초 실행 시 설정 초기화(Welcome 창)
- [Configuration setup](#configuration_setup) — 설정 가져오기, 버전별 설정 폴더 위치
- [Libraries setup](#libraries_setup) — 라이브러리 초기화 옵션
- [Updates & Privacy setup](#updates_privacy_setup) — 업데이트 알림·크래시 리포트 동의
- [Migrating design files](#migrating_design_files_from_previous_versions) — 이전 버전 파일 마이그레이션
- [Using the KiCad project manager](#using_the_kicad_project_manager) — 프로젝트 매니저 창 구성, 트리뷰, 툴바
- [Standalone mode](#standalone_mode) — 독립 실행 모드(권장 안 함)
- [Creating a new project](#creating_a_new_project) — 새 프로젝트 생성(템플릿 선택, Ctrl+N)
- [Importing a project from another EDA tool](#importing_a_project_from_another_eda_tool) — 타 EDA 임포트 포맷 표
- [Project backups and autosave](#backups-and-autosave) — 백업/오토세이브 개요
- [Incremental backups](#incremental_backups) — 증분 백업(Local History, .history)
- [Zip archives](#zip_archives) — Zip 아카이브 백업
- [Saving and loading project archives](#project-archive) — 프로젝트 아카이브/언아카이브
- [Git integration](#git-integration) — Git 버전 관리 연동
- [Adding version control to an existing project](#adding_version_control_to_an_existing_project) — 기존 프로젝트에 Git 추가
- [Cloning an existing repository](#cloning_an_existing_repository) — 원격 저장소 클론
- [Tracking project changes with Git](#tracking_project_changes_with_git) — 커밋/푸시/풀/브랜치 전환
- [KiCad files and folders](#kicad_files_and_folders) — 파일 확장자/폴더 개요
- [Project files](#project_files) — 프로젝트 파일(.kicad_pro)
- [Schematic editor files and folders](#schematic_editor_files_and_folders) — 회로도 파일/라이브러리
- [Board editor files and folders](#board_editor_files_and_folders) — 보드 파일/라이브러리
- [Common files](#common_files) — 공통 파일(.kicad_prl, .kicad_wks 등)
- [Fabrication and documentation files](#fabrication_and_documentation_files) — 제조/문서 출력 파일
- [Storing and sending KiCad files](#storing_and_sending_kicad_files) — 파일 저장·전송 가이드
- [Paths and libraries configuration](#path-variables) — 경로 변수 개념
- [KiCad path variables](#kicad-environment-variables) — 내장 경로 변수 표
- [Advanced environment variables](#advanced_environment_variables) — 고급 환경변수
- [Libraries configuration](#libraries-configuration) — 심볼/풋프린트 라이브러리 테이블 관리
- [Jobsets](#jobsets) — 잡셋(일괄 출력 생성)
- [Defining jobs](#defining_jobs) — 잡 정의
- [Defining jobset destinations](#jobset-destinations) — 잡셋 대상(Archive/Folder)
- [Jobset destination details](#jobset_destination_details) — 임시 폴더/JOBSET_OUTPUT_WORK_PATH
- [Available job types](#job-types) — 사용 가능한 잡 타입 표
- [Project templates](#project-templates) — 프로젝트 템플릿
- [Using templates](#using_templates) — 템플릿 사용
- [Template locations](#template-locations) — 템플릿 위치(System/User)
- [Template contents](#template-contents) — 템플릿 구성/복사 규칙
- [Template metadata](#template-metadata) — meta/info.html
- [Template file renaming](#template_file_renaming) — 파일 이름 변경 규칙
- [Creating new templates](#creating_new_templates) — 새 템플릿 만들기
- [Plugin and Content Manager](#plugin-content-manager) — PCM 개요
- [Browsing packages](#browsing_packages) — 패키지 탐색
- [Installing packages](#installing_packages) — 패키지 설치/업데이트/제거
- [Managing repositories](#managing_repositories) — 저장소 관리
- [Creating packages and repositories](#pcm-creating-packages) — 패키지/저장소 생성
- [KiCad preferences](#kicad-manager-configuration) — 환경설정 개요(Ctrl+,)
- [Common preferences](#common_preferences) — 공통 환경설정
- [Mouse and touchpad preferences](#mouse_and_touchpad_preferences) — 마우스/터치패드
- [SpaceMouse preferences](#spacemouse_preferences) — SpaceMouse
- [Hotkey preferences](#hotkey_preferences) — 단축키 설정
- [Importing hotkeys](#importing_hotkeys) — 단축키 가져오기(.hotkeys)
- [Version control preferences](#version_control_preferences) — Git 환경설정
- [Data collection preferences](#data_collection_preferences) — 데이터 수집
- [Packages and updates preferences](#packages_and_updates_preferences) — 패키지/업데이트
- [Plugins preferences](#plugins_preferences) — 플러그인(IPC API, Python)
- [Maintenance preferences](#maintenance_preferences) — 유지보수(캐시·초기화)
- [Actions reference](#actions_reference) — 액션/단축키 레퍼런스
- [KiCad Project Manager actions](#kicad_project_manager) — 프로젝트 매니저 단축키 표

---

## Introduction · #introduction

- KiCad은 전자 회로도와 PCB를 만드는 오픈소스 소프트웨어 스위트. 회로도와 대응 PCB를 함께 설계하는 통합 워크플로와 특수 용도의 standalone 워크플로 모두 지원.
- 부속 유틸리티: PCB calculator(회로 구조의 전기적 특성 계산), Gerber viewer(제조 파일 검사), 통합 SPICE simulator(회로 동작 검사).
- 모든 주요 OS에서 동작. 최대 **32 copper layers** PCB 지원. 모든 복잡도의 설계에 적합.
- 최신 문서: https://docs.kicad.org

### System Requirements · #system_requirements

- KiCad은 다양한 하드웨어·OS에서 동작하나 저사양에서는 일부 작업이 느릴 수 있음.
- 권장 사양: 전용 그래픽 카드 + **1920x1080 이상** 해상도 디스플레이.
- 최신 시스템 요구사항: https://kicad.org/help/system-requirements/

## Installing and Upgrading KiCad · #installing_and_upgrading_kicad

- KiCad 설치 및 업그레이드를 다루는 상위 섹션. 세부 내용은 하위(First time setup, Migrating design files)에서 다룸.

### First time setup · #settings

- 새 메이저 버전을 처음 실행하면 **Welcome** 창이 떠서 설정 초기화 방법을 묻는다.
- 각 메이저 릴리스는 자체 설정을 가지므로, 같은 컴퓨터에서 여러 KiCad 버전을 설정 충돌 없이 함께 실행 가능.

### Configuration setup · #configuration_setup

- 새 버전을 기본 설정으로 시작할 수 있음. 이전 버전이 감지되면 그 설정을 가져오는 옵션 제공. 이전 설정 파일 위치는 자동 감지되나 다른 위치로 직접 지정 가능.
- ⚠️ **NOTE**: Hotkey 설정은 이전 버전에서 가져오지 않음. 수동으로 가져오려면 Preferences의 **Hotkeys** 페이지에서 **Import Hotkeys…** 버튼으로 구버전 설정 디렉토리의 `.hotkeys` 파일을 찾아 적용. 단 이 작업은 현재 버전의 hotkey 설정을 **덮어쓴다**.
- 설정 파일은 사용자 디렉토리 내 폴더에 저장되며, 버전별 하위 폴더 사용. KiCad 10 폴더 위치:

| OS | 경로 |
| --- | --- |
| Windows | `%APPDATA%\kicad\10.0` |
| Linux | `~/.config/kicad/10.0` |
| macOS | `/Users/<username>/Library/Preferences/kicad/10.0` |

### Libraries setup · #libraries_setup

- 심볼/풋프린트/디자인 블록 라이브러리를 어떻게 초기화할지 선택하는 단계.
- 옵션:
  1. **Start with the built-in KiCad libraries** — 최초 설정 시 권장. KiCad 동봉 라이브러리 전체를 라이브러리 테이블에 포함.
  2. **Import tables from the previous version** — 구버전에서 동작하던 라이브러리 설정이 이미 있을 때. 이 경우 **Migrate built-in libraries to the latest version**도 함께 선택 권장(구버전 내장 라이브러리 참조를 최신 참조로 교체).
  3. 라이브러리 없이 시작 후 직접 설정 — 회로도/PCB 에디터 문서 참조.
- 시스템·설치 방식에 따라 일부 옵션이 안 보일 수 있고, KiCad이 설치된 라이브러리를 못 찾을 수도 있음 → 라이브러리 설치 확인하거나 설정 후 수동 구성.
- ⚠️ **NOTE**: 일부 시스템에서는 KiCad 라이브러리가 별도 패키지로 설치됨.
- 기본 library table 파일 위치(OS·설치 위치에 따라 다름):

| OS | 경로 |
| --- | --- |
| Windows | `C:\Program Files\KiCad\10.0\share\kicad\template\` |
| Linux | `/usr/share/kicad/template/` |
| macOS | `/Applications/KiCad/KiCad.app/Contents/SharedSupport/template/` |

### Updates & Privacy setup · #updates_privacy_setup

- KiCad 애플리케이션 업데이트 및 PCM으로 설치한 서드파티 패키지(plugins, themes, libraries 등) 업데이트 알림 수신 여부 선택.
- Windows에서는 익명 crash reporting 활성화 옵션도 제공(핵심 이슈 진단·수정에 도움).

### Migrating design files from previous versions · #migrating_design_files_from_previous_versions

- 최신 KiCad은 이전 버전 파일을 열 수 있으나 **저장은 최신 포맷으로만** 가능. 따라서 파일 마이그레이션은 보통 파일을 여는 것 외에 특별한 단계가 없음.
- 일부 경우 버전 간 파일 확장자가 바뀜. 이런 파일을 열면 새 확장자의 새 포맷으로 저장되며, **구 파일은 자동 삭제되지 않음**.
- 레거시 회로도 관련 고려사항은 schematic editor 문서 참조.
- ⚠️ 한 버전에서 만들거나 수정한 파일은 일반적으로 **구버전 KiCad으로 열 수 없음**. 따라서 새 릴리스 테스트 시 구버전이 더 이상 필요 없다고 확신할 때까지 프로젝트 백업본을 보관하는 것이 중요.

## Using the KiCad project manager · #using_the_kicad_project_manager

- 프로젝트 매니저는 KiCad 실행 시 열리는 창. KiCad 프로젝트를 생성·열고 다른 도구를 실행하는 허브.
- 실행 가능한 도구: Schematic Editor, Symbol Editor, PCB Editor, Footprint Editor, Gerber Viewer, Image Converter, Calculator Tools, Drawing Sheet Editor, Plugin and Content Manager.
- 창 구성: 왼쪽 = 프로젝트 파일 트리뷰, 오른쪽 = 각 에디터/도구 바로가기 런처.
- 트리뷰: 프로젝트 폴더 내 파일 목록 표시(회로도/보드 설계 파일 및 기타 파일·폴더). 다중 시트면 root sheet만 표시.
  - ⚠️ **NOTE**: KiCad이 열 줄 아는 파일만 트리뷰에 표시됨.
  - 파일 더블클릭 → 연관 에디터로 열림. 우클릭 → 파일 조작 명령 컨텍스트 메뉴.
  - 프로젝트가 Git 저장소의 일부면 각 파일의 버전 관리 상태 아이콘 표시 + 프로젝트명 옆에 활성 branch 표시. 평소엔 root sheet만 보이나, Git 저장소일 때는 모든 시트가 표시되어 시트별 변경을 개별 관찰 가능.
- KiCad 프로젝트는 최소 project file + schematic + board design 포함. 회로도는 여러 시트(각각 별도 파일) 가능하지만 프로젝트당 보드는 **하나만**. project file, schematic root sheet file, board file은 **모두 같은 이름**이어야 함.
- 좌측 툴바 단축 동작:

| 아이콘 | 동작 |
| --- | --- |
| new project | 새 프로젝트 생성 |
| open project | 기존 프로젝트 열기 |
| zip | 전체 프로젝트(회로도, 라이브러리, PCB 등)를 zip 아카이브로 생성 |
| unzip | 프로젝트 zip 아카이브를 디렉토리로 추출. 대상 디렉토리의 파일은 덮어써짐 |
| refresh | 트리뷰 새로고침(파일시스템 변경 감지) |
| directory browser | 프로젝트 작업 디렉토리를 파일 탐색기로 열기 |

### Standalone mode · #standalone_mode

- 프로젝트 매니저가 아닌 OS 앱 런처에서 직접 에디터 도구를 실행하는 *standalone* 모드.
- ⚠️ 보통 **권장하지 않음**. 단 타 EDA 도구에서 프로젝트를 임포트하는 등 필요한 특정 상황에서만 사용.
- standalone 모드에서 사용 불가한 프로젝트 기능:
  - 회로도 에디터 ↔ 보드 에디터 간 cross probing
  - 회로도 ↔ 보드 간 design synchronization

### Creating a new project · #creating_a_new_project

- 대부분의 설계는 프로젝트 생성으로 시작. 새 프로젝트 생성 시 항상 project template을 선택(기본 빈 템플릿이라도).
- 절차:
  1. **File** 메뉴의 **New Project…** 명령, 또는 상단 툴바 **New Project** 버튼, 또는 단축키 `Ctrl`+`N`(기본).
  2. 다이얼로그 오른쪽 = 설치된 템플릿 목록(**Default** 템플릿은 항상 사용 가능, 빈 프로젝트 생성용). 템플릿 클릭 시 설명 패널 표시. 왼쪽 = 최근 사용 템플릿.
  3. 템플릿 선택 후 **OK** 클릭.
  4. 프로젝트 이름 입력. 기본적으로 같은 이름의 디렉토리가 생성됨. 예: `MyProject` 입력 → `MyProject` 디렉토리 + 그 안에 `MyProject/MyProject.kicad_pro`.
  5. 이미 디렉토리가 있으면 **Create a new directory for the project** 체크박스 해제.
- ⚠️ **NOTE**: 새 템플릿 만들기는 Project Templates 섹션(#project-templates) 참조.
- 💡 **TIP**: 직접 템플릿을 만들면 선호하는 drawing sheets, design rules, PCB outlines, logos 등이 미리 설정된 새 프로젝트를 쉽게 생성 가능.
- ⚠️ **NOTE**: 각 KiCad 프로젝트는 자체 디렉토리에 저장하는 것을 강력 권장.
- 프로젝트 디렉토리에 생성되는 파일:

| 파일 | 설명 |
| --- | --- |
| `example.kicad_pro` | KiCad project file |
| `example.kicad_sch` | Main schematic file |
| `example.kicad_pcb` | Printed circuit board file |

- 템플릿 내용에 따라 다른 파일도 생성될 수 있음.

### Importing a project from another EDA tool · #importing_a_project_from_another_eda_tool

- KiCad은 일부 타 소프트웨어 파일을 임포트 가능. 일부 포맷은 완전한 프로젝트로, 일부는 standalone 회로도/보드로만 임포트되어 수동으로 KiCad 프로젝트에 연결해야 함.
- 임포트 방법: **File** 메뉴 → **Import Non-KiCad Project** 서브메뉴에서 해당 옵션 선택. 포맷에 따라 project/schematic/board 파일 선택을 요구. 임포트할 schematic·board 파일은 같은 base 이름이어야 함(예: project.sch, project.brd). 이후 결과 KiCad 프로젝트를 저장할 디렉토리 선택.
- **완전한 프로젝트로 임포트 가능한 포맷**:

| Source EDA Tool | File Extension(s) |
| --- | --- |
| Altium Designer | `.PrjPcb` |
| CADSTAR archive format | `.csa`, `.cpa` |
| Eagle 6.x or newer (XML format) | `.sch`, `.brd` |
| EasyEDA (JLCEDA) Standard Backup | `.zip` |
| EasyEDA (JLCEDA) Pro Project | `.epro`, `.zip` |
| PADS ASCII Project | `.asc`, `.txt` |
| gEDA / Lepton EDA Project | `.prj`, `.sch`, `.pcb` |

- **Schematic Editor로 임포트 가능한 회로도 포맷**:

| Source EDA Tool | File Extension(s) |
| --- | --- |
| Altium Designer | `.SchDoc` |
| Eagle (Autodesk) | `.sch` (XML) |
| LTspice | `.asc` |
| PADS Logic | `.asc`, `.txt` |
| CADSTAR Schematic Archive | `.csa` |
| gEDA / Lepton EDA | `.sch` |
| EasyEDA (JLCEDA) Standard | `.json` |
| EasyEDA (JLCEDA) Professional | `.epro`, `.zip` |

- **PCB Editor로 임포트 가능한 PCB 포맷**:

| Source EDA Tool | File Extension(s) |
| --- | --- |
| Altium Designer | `.PcbDoc` |
| Altium Circuit Maker | `.CMPcbDoc` |
| Altium Circuit Studio | `.CSPcbDoc` |
| Cadence Allegro | `.brd` |
| CADSTAR PCB Archive | `.cpa` |
| Eagle (Autodesk) | `.brd` (XML) |
| EasyEDA / JLCEDA Standard | `.json`, `.zip` |
| EasyEDA / JLCEDA Professional | `.epro`, `.zip` |
| Fabmaster | `.txt`, `.fab` |
| gEDA / Lepton EDA | `.pcb` |
| P-CAD 200x | `.pcb` (ASCII) |
| PADS (ASCII) | `.asc` |
| Solidworks PCB | `.SWPcbDoc` |

- 회로도/PCB 임포트 상세는 각각 Schematic Editor·PCB Editor 문서 참조.

### Project backups and autosave · #backups-and-autosave

- KiCad은 프로젝트 백업을 자동 생성 가능. 활성화 시 두 상황에서 전체 프로젝트 백업:
  - 어떤 에디터에서든 수동 저장할 때.
  - 미저장 변경이 있고 몇 초간 비활성 상태일 때(*autosave*).
- 설정 위치: Project Backup preferences(#project_backup).
- 백업 방식 2가지: **incremental backups** 또는 **Zip archives**.

#### Incremental backups · #incremental_backups

- 증분 스냅샷으로 백업 저장.
- 스냅샷 보기: **View** → **Panels** → **Local History** 패널. 각 스냅샷 이벤트와 시각 표시. 이벤트에 마우스를 올리면 변경된 파일을 툴팁으로 표시.
- 복원: Local History 패널에서 스냅샷 우클릭 → **Restore Commit**.
- 내부적으로 숨김 폴더 `.history`의 Git 저장소 사용(KiCad이 자동 관리).
- 💡 **TIP**: 버전 관리 시스템으로 변경을 추적한다면 `.history` 폴더를 제외(exclude)하는 것이 좋음.

#### Zip archives · #zip_archives

- 프로젝트 디렉토리와 내용을 Zip 아카이브로 저장. 각 백업은 별도 Zip 파일.
- 복원: Unarchive 도구 사용, 또는 아카이브를 수동 추출 후 프로젝트 로드.

### Saving and loading project archives · #project-archive

- 프로젝트 파일을 zip 아카이브로 묶기: Archive 도구(**File** → **Archive Project…**).
- 언아카이브: **File** → **Unarchive Project…**. 현재 로드된 프로젝트 디렉토리로 언아카이브하면 프로젝트가 자동 재로드되어 변경 반영.
- Archive 도구가 프로젝트 폴더에서 아카이브에 저장하는 파일:

| 패턴 | 분류 |
| --- | --- |
| `*.kicad_prl`, `*.kicad_pro`, `*.kicad_sch`, `*.kicad_sym`, `*.kicad_pcb`, `*.kicad_mod`, `*.kicad_dru`, `*.kicad_wks`, `*.kicad_jobset`, `*.wbk`, `*.json`, `fp-lib-table`, `sym-lib-table`, `design-block-lib-table` | KiCad design files |
| `*.pro`, `*.sch`, `*.lib`, `*.dcm`, `*.cmp`, `*.brd`, `*.mod` | Legacy KiCad design files |
| `*.stp`, `*.step` | 3D models |
| `*.g?`, `*.g??`, `*.gm??`, `*.gbrjob` | Gerber files |
| `*.pos`, `*.drl`, `*.nc`, `*.xnc`, `*.d356`, `*.rpt` | Manufacturing files |
| `*.net` | Netlists |
| `*.py` | Python scripts |
| `*.pdf`, `*.txt` | Documentation files |
| `*.cir`, `*.sub`, `*.model` | SPICE models |
| `*.ibs`, `*.pkg` | IBIS models |

### Git integration · #git-integration

- 프로젝트 매니저는 Git 버전 관리 도구와 통합. 기존 로컬 Git 저장소와 작동, 원격에서 프로젝트 clone, 기존 프로젝트에 새 저장소 생성 가능. 변경 commit, 원격 push/pull, branch 전환 지원.
- 이미 Git으로 관리되는 프로젝트를 열면 추가 설정 없이 버전 관리 기능 사용 가능. 활성 branch가 프로젝트명 옆에 표시되고, 각 파일 상태가 트리에 그래픽으로 표시:
  - git good check 아이콘 = 변경 없음
  - git modified 아이콘 = 미커밋 변경 있음
  - git add 아이콘 = 추적되지 않음(untracked)
  - Git 저장소가 아니면 아이콘 표시 안 됨.
- ⚠️ **NOTE**: Git 통합 기능은 Preferences의 **Version Control** 페이지에서 비활성화 가능. 거기서 remote 업데이트 주기·기본 commit author 정보도 설정.

#### Adding version control to an existing project · #adding_version_control_to_an_existing_project

- 아직 버전 관리되지 않는 프로젝트: 트리에서 파일 우클릭 → **Version Control** → **Add Project to Version Control…** 으로 새 Git 저장소 초기화. 이 방식은 remote 구성이 **필수**.
- 구성 정보:
  - **Location**: remote의 URL 또는 파일 경로. HTTPS/SSH/local(file) 지원. URL 형식으로 연결 타입과 인증 옵션 자동 결정.
  - **SSH private key**: 인증용 SSH private keyfile (SSH 전용).
  - **User name**: 인증용 사용자명. SSH 연결에서는 보통 `git`.
  - **Password**: 인증용 비밀번호 (HTTPS 전용).
  - **SSH key password**: SSH 키 passphrase(설정한 경우, SSH 전용).
- **Test Connection** 버튼으로 연결·인증 확인 가능.

#### Cloning an existing repository · #cloning_an_existing_repository

- 기존 저장소 clone 후 열기: **File** → **Clone Project from Repository…**. SSH/HTTPS 원격 또는 로컬 저장소 clone 가능. 구성 설정은 기존 프로젝트에 remote 구성할 때와 동일.

#### Tracking project changes with Git · #tracking_project_changes_with_git

- 변경 commit:
  - 전체 프로젝트: 우클릭 → **Version Control** → **Commit Project…**
  - 특정 파일: 파일 우클릭 → **Version Control** → **Commit File…**
  - 둘 다 Commit Changes 다이얼로그를 열며, Commit Project는 저장소의 모든 변경 파일을, Commit File은 우클릭한 파일만 표시. 다이얼로그에서 포함할 파일 선택, commit message·author 입력 후 commit.
- Push: 트리 우클릭 → **Version Control** → **Push**. Pull: 우클릭 → **Version Control** → **Pull**.
- Branch 전환: **Version Control** → **Switch to Branch** 메뉴에서 선택.
- Git 추적 비활성화: 우클릭 → **Version Control** → **Disable Git Integration**. 현재 프로젝트 편집 시 KiCad의 Git 통합만 끄며, 디스크의 실제 Git history·저장소는 영향 없음(다른 Git 도구로 계속 관리 가능). 다른 프로젝트의 Git 통합도 끄지 않음. 모든 프로젝트에 대해 끄려면 Preferences의 **Version Control** 페이지 사용.

## KiCad files and folders · #kicad_files_and_folders

- KiCad이 회로도·보드 편집에 쓰는 파일 확장자(및 폴더) 목록.
- 중요 설계 정보를 담는 파일: project file(`.kicad_pro`), schematic file(s)(`.kicad_sch`), board file(`.kicad_pcb`) 등 — 프로젝트 배포 시 항상 포함. project-local 설정(`.kicad_prl`)이나 `fp-info-cache`처럼 배포 불필요 파일은 아래 표에 명시.

### Project files · #project_files

| 확장자 | 설명 |
| --- | --- |
| `.kicad_pro` | Project file. 회로도와 PCB 간 공유 설정 포함 |
| `.pro` | Legacy(KiCad 5.x 이전) project file. 읽기 가능하며 프로젝트 매니저가 `.kicad_pro`로 변환 |

### Schematic editor files and folders · #schematic_editor_files_and_folders

| 확장자 | 설명 |
| --- | --- |
| `.kicad_sch` | Schematic 파일. 모든 심볼·연결 정보 포함 |
| `.kicad_sym` | Schematic symbol library 파일(*packed* 라이브러리, 모든 심볼이 단일 파일). *unpacked* 라이브러리(폴더 안에 개별 `.kicad_sym` 파일, 각각이 별도 심볼)의 개별 심볼일 수도 있음. unpacked 폴더는 확장자 강제 없음, `.kicad_symdir`이 관례 |
| `.kicad_symdir` | Schematic symbol library 폴더. 폴더 자체가 라이브러리이며 개별 `.kicad_sym` 심볼 파일 포함. `.kicad_sym` *packed*의 *unpacked* 대안. `.kicad_symdir`은 관례일 뿐 필수 아님(임의 폴더명 가능) |
| `.wbk` | Simulator workbook 파일. SPICE 시뮬레이션 설정 정보 포함 |
| `.sch` | Legacy(5.x 이전) schematic 파일. 읽기 가능, 저장 시 `.kicad_sch`로 변환 |
| `.lib` | Legacy(5.x 이전) schematic library 파일. 읽기만 가능, 쓰기 불가 |
| `.dcm` | Legacy(5.x 이전) schematic library 문서. 읽기만 가능 |
| `*-cache.lib` | Legacy(5.x 이전) schematic component library cache. 레거시 `.sch` 로딩에 필요 |
| `sym-lib-table` | Symbol library table: 회로도 에디터에서 사용 가능한 심볼 라이브러리 목록 |
| `design-block-lib-table` | Design block library table: 회로도 에디터에서 사용 가능한 디자인 블록 라이브러리 목록 |

### Board editor files and folders · #board_editor_files_and_folders

| 확장자 | 설명 |
| --- | --- |
| `.kicad_pcb` | Board 파일. page layout 외 모든 정보 포함 |
| `.pretty` | Footprint library 폴더. 폴더 자체가 라이브러리 |
| `.kicad_mod` | Footprint 파일. 각 파일당 풋프린트 1개 |
| `.kicad_dru` | Design rules 파일. 특정 `.kicad_pcb`용 커스텀 design rules |
| `.brd` | Legacy(4.x 이전) board 파일. 읽기만 가능, 쓰기 불가 |
| `.mod` | Legacy(4.x 이전) footprint library 파일. footprint/board 에디터가 읽기 가능, 쓰기 불가 |
| `fp-lib-table` | Footprint library table: 보드 에디터에서 사용 가능한 풋프린트 라이브러리 목록 |
| `fp-info-cache` | 풋프린트 라이브러리 로딩 가속 cache. 배포·버전 관리 불필요 |

### Common files · #common_files

| 확장자 | 설명 |
| --- | --- |
| `.kicad_prl` | 현재 프로젝트의 local 설정(layer 가시성, selection filter 등 마지막 사용 설정 기억). 배포·버전 관리 불필요 |
| `.kicad_wks` | Page layout(drawing border + title block) 설명 파일 |
| `.kicad_jobset` | Jobset 정의 파일(output jobsets) |
| `.kicad_blocks` | Design block library 폴더. 폴더 자체가 라이브러리. 디자인 블록은 회로도·레이아웃 조각 모두 포함 가능 |
| `.kicad_block` | 재사용 가능 디자인 정의용 design block 폴더. 폴더가 디자인 블록이며 회로도 정의 `.kicad_sch`, 레이아웃 정의 `.kicad_pcb`, 메타데이터 정의 `.json` 포함 |
| `.net` | 회로도에서 만든 netlist, 보드 에디터가 읽음. 권장 워크플로(회로도→보드 전달)는 netlist 파일을 요구하지 않음 |
| `.cmp` | 회로도 컴포넌트와 풋프린트 연관. 보드 에디터가 생성, 회로도 에디터가 임포트. 보드에서 풋프린트를 바꾼(예: **Exchange Footprints**) 변경을 회로도로 역임포트하는 용도. 권장 워크플로(보드→회로도)는 `.cmp` 파일을 요구하지 않음 |

### Fabrication and documentation files · #fabrication_and_documentation_files

| 확장자 | 용도 |
| --- | --- |
| `.gbr` | Gerber 파일 (fabrication) |
| `.drl` | Drill 파일(Excellon 포맷) (fabrication) |
| `.pos` | Position 파일(ASCII), 자동 삽입기용 |
| `.rpt` | Report 파일(ASCII) (documentation) |
| `.ps` | Plot 파일(Postscript) (documentation) |
| `.pdf` | Plot 파일(PDF) (documentation) |
| `.svg` | Plot 파일(SVG) (documentation) |
| `.dxf` | Plot 파일(DXF) (documentation) |

### Storing and sending KiCad files · #storing_and_sending_kicad_files

- 회로도·보드 파일은 설계에 쓰인 모든 심볼·풋프린트를 포함하므로 단독으로 백업/전송해도 문제없음. 단 중요한 설계 정보가 project file(`.kicad_pro`)에 있으므로 완전한 설계를 보낼 때는 반드시 포함.
- `.kicad_prl`, `fp-info-cache` 같은 파일은 전송 불필요. Git 등 버전 관리 사용 시 ignore 목록에 추가 권장.

## Paths and libraries configuration · #path-variables

- **path variable**(경로 변수)로 경로를 정의 가능. 일부 경로 변수는 KiCad 내부에 정의되어 있어 라이브러리·3D 모델 등의 경로 정의에 사용.
- 절대 경로를 모르거나 바뀔 수 있을 때(다른 컴퓨터로 이전 등), 또는 하나의 기준 경로를 여러 항목이 공유할 때 유용. 적용 대상 예: schematic symbol libraries, footprint libraries, 풋프린트 정의의 3D model 파일.
- 예: `connect.pretty` 풋프린트 라이브러리 경로를 `KICAD10_FOOTPRINT_DIR` 변수로 정의 시 → `${KICAD10_FOOTPRINT_DIR}/connect.pretty`.
- 설정 위치: **Preferences** → **Configure Paths…** — 내장 경로 변수 정의 및 개인 경로 변수 추가.
- ⚠️ **NOTE**: 구버전의 versioned 경로 변수는, 해당 구버전 변수가 명시 정의되지 않은 한, 현재 버전의 대응 변수 값으로 자동 해석됨. 예: `KICAD9_FOOTPRINT_DIR`이 정의돼 있지 않으면 `${KICAD9_FOOTPRINT_DIR}`는 `${KICAD10_FOOTPRINT_DIR}` 값으로 자동 해석.

### KiCad path variables · #kicad-environment-variables

| 변수 | 설명 |
| --- | --- |
| `KICAD10_3DMODEL_DIR` | KiCad 표준 3D 풋프린트 모델 라이브러리 파일의 기준 경로 |
| `KICAD10_3RD_PARTY` | PCM으로 설치한 plugins/libraries/color themes 위치 |
| `KICAD10_FOOTPRINT_DIR` | KiCad 표준 footprint library 파일의 기준 경로 |
| `KICAD10_SYMBOL_DIR` | KiCad 표준 symbol library 파일의 기준 경로 |
| `KICAD10_TEMPLATE_DIR` | KiCad 표준 project template library 파일 위치 |
| `KICAD_USER_TEMPLATE_DIR` | 개인 project templates 위치 |
| `SPICE_LIB_DIR` | 개인 시뮬레이션 모델 라이브러리 위치. 기본 미정의 |
| `KIPRJMOD` | 현재 프로젝트 디렉토리 절대 경로. 자동 설정되며 재정의 불가 |

- Configure Paths 다이얼로그에서 설정한 경로는 KiCad 내부용이며 외부 환경변수로는 보이지 않음(KiCad 사용자 설정 파일에 저장).
- 경로는 KiCad 외부에서 system environment variable로도 설정 가능하며, 이는 사용자 설정을 **override**함.
- ⚠️ **NOTE**: KiCad 외부에서 설정된 system environment variable은 Configure Paths 다이얼로그로 override 불가. 외부 설정 변수는 다이얼로그에서 read-only로 표시됨.
- `KIPRJMOD`는 **항상** KiCad 내부 정의이며 **현재 프로젝트 절대 경로**로 확장됨. 예: `${KIPRJMOD}/connect.pretty`는 현재 프로젝트 폴더 안의 `connect.pretty` 폴더. Configure Paths에서 변경하거나 외부 환경변수로 override 불가.

### Advanced environment variables · #advanced_environment_variables

- 일부 고급 환경변수로 KiCad이 특정 파일을 찾는 위치를 커스터마이즈 가능. 기본값은 플랫폼 기준이며 system environment variable로 override 가능. 이 변수들은 Configure Paths 다이얼로그에 표시되지 않고 경로 치환(path substitution)에 사용 불가.
- ⚠️ 이 변수들을 바꿔도 KiCad이 파일을 기존 위치에서 새 위치로 이동하지 않음 → 변경 시 원하는 설정·파일을 수동 복사해야 함.

| 변수 | 설명 |
| --- | --- |
| `KICAD_CONFIG_HOME` | KiCad 설정 파일 기준 경로. minor 버전별 하위 디렉토리 생성 |
| `KICAD_DOCUMENTS_HOME` | 사용자 수정 가능 문서(projects, templates, Python scripts, libraries 등) 기준 경로. minor 버전별 하위 디렉토리 생성. 제안 위치일 뿐 강제 아님 |
| `KICAD_STOCK_DATA_HOME` | KiCad stock data(기본 라이브러리 포함) 기준 경로. installer/패키지 매니저가 관리, 사용자 쓰기용 아님 |

- ⚠️ **WARNING**: 경로 구성을 수정하면 경로 처리 문제를 피하기 위해 KiCad을 종료 후 재시작할 것.

### Libraries configuration · #libraries-configuration

- **Preferences** → **Manage Symbol Libraries…** : 심볼 라이브러리 목록(symbol library table) 관리.
- **Preferences** → **Manage Footprint Libraries…** : 풋프린트 라이브러리 목록(footprint library table) 관리.
- 각 라이브러리 타입(symbol/footprint)마다 라이브러리 테이블이 2개: **global**(사용자 설정 디렉토리, 모든 프로젝트에서 사용 가능)과 **project-specific**(선택적, 프로젝트 디렉토리에 위치, 해당 프로젝트 전용).

## Jobsets · #jobsets

- 여러 출력을 한 번의 클릭으로 모두 생성하도록 구성하는 기능. 출력 잡과 저장 대상의 목록을 *jobset*이라 함. 예: Gerber, assembly data, BOM, 회로도·PCB PDF plot 생성 + ERC/DRC 실행, 결과를 압축 아카이브에 저장.
- *job*: 단일 타입 출력 정의(BOM, Gerber 등). 회로도/보드 에디터에서 수동 생성하듯 구성. 설정은 jobset에 저장되어 다음에 jobset 로드 시 기억됨. 같은 타입 잡을 여러 번 넣으면 각각 독립 설정(예: 컬러 PDF + 흑백 PDF).
- *destination*: 실행할 잡 목록과 출력 저장 방식 정의. 선택 잡 출력을 지정 위치에 저장하거나 압축 아카이브에 추가. destination마다 다른 잡 부분집합 선택 가능. 개별 실행 또는 전체 동시 실행.
- 프로젝트는 여러 jobset 보유 가능. 각 jobset은 `.kicad_jobset` 파일에 저장(프로젝트 전용/프로젝트 간 복사/중앙 위치 공유 가능).
- 사용 절차:
  1. 프로젝트 매니저에서 새 jobset 파일 생성: **File** → **New Jobset File…**(이름·위치 선택). 또는 **File** → **Open Jobset File…**로 기존 파일 열기.
  2. 프로젝트 디렉토리에 저장된 jobset 파일은 프로젝트 일부로 간주되어 트리에 표시되며 더블클릭으로 열림.
  3. 열면 프로젝트 매니저에 새 탭으로 표시(가운데 = 잡 목록, 오른쪽 = destination 목록). 새 jobset은 잡이 없지만 폴더 저장용 destination이 자동 생성됨.
  4. 변경 후 **Save Jobset** 버튼으로 저장.

### Defining jobs · #defining_jobs

- 새 잡 추가: Jobs 목록 아래 **+** 버튼 → Add New Job 다이얼로그에서 잡 타입 선택. 하단 **Filter** 텍스트박스로 목록 필터링 가능.
- 잡 선택 후 **OK** → 해당 출력 타입의 설정 다이얼로그 표시(에디터에서 수동 생성 시와 동일 옵션).
- ⚠️ **NOTE**: 잡 설정의 출력 파일명·경로는 jobset destination 폴더/아카이브 root 기준 상대 경로. `${PROJECTNAME}`, `${CURRENT_DATE}`, 프로젝트 text variables 같은 텍스트 변수 사용 가능.
- 설정 다이얼로그 수락 시 잡이 목록에 추가됨(설명 변경 가능). 이후 변경: 잡 우클릭 → **Edit Job Description** 또는 **Edit Job Settings…**(더블클릭도 설정 편집). 제거: 잡 선택 후 trash 버튼. 순서 변경: up/down 버튼.

### Defining jobset destinations · #jobset-destinations

- destination이 없으면 출력 생성 불가. jobset 생성 시 1개가 자동 생성되며 필요한 만큼 추가 가능.
- 추가: Destinations 목록 아래 **+** 버튼 → Add New Destination 다이얼로그에서 타입 선택:
  - **Archive**: 잡 출력을 압축 zip 아카이브로 저장.
  - **Folder**: 잡 출력을 폴더에 비압축 저장.
- 타입 선택 후 Destination options 다이얼로그: 이 destination이 실행할 잡 선택(기본 전체 활성화), 저장 폴더/아카이브 이름, 설명 설정. output path는 절대 또는 프로젝트 기준 상대 경로, path variables·텍스트 변수(`${PROJECTNAME}`, `${CURRENT_DATE}`, 프로젝트 text variables) 사용 가능. 잡 설정의 파일명은 destination 디렉토리/아카이브 root 기준 상대.
- **OK** 클릭 시 destination 추가. 수정: config 버튼. 제거: trash 버튼.
- 출력 생성: 원하는 destination의 **Generate** 버튼(개별), 또는 **Generate All Destinations**(전체).
- 실행 성공 시 파란 체크, 실패 시 빨간 느낌표 표시. 인디케이터 클릭 → Jobset Run Log 다이얼로그(각 잡 상태 표시). 특정 잡 클릭 시 로그 출력 표시.
- 성공 후 destination의 **Open Output** 버튼으로 출력 위치 파일 브라우저 열기(미실행/미완료 시 비활성).

#### Jobset destination details · #jobset_destination_details

- 잡 실행 시 출력 파일은 먼저 임시 폴더에 생성됨. destination의 모든 잡 완료 후 임시 폴더에서 지정 폴더/아카이브로 이동. 모든 잡이 끝나기 전엔 이동되지 않음 → 같은 destination 내 다른 잡이 생성한 파일을 참조해야 하면 그 파일은 임시 폴더에 있음(최종 destination 아님).
- KiCad은 잡 실행 중 `${JOBSET_OUTPUT_WORK_PATH}` 환경변수를 현재 destination의 임시 경로로 설정. 잡이 임시 폴더 실제 위치를 알아야 할 때 사용(예: Execute Command 잡이 다른 잡 출력을 rename하는 스크립트를 돌릴 때, 이동 전 출력의 임시 위치 필요).

### Available job types · #job-types

| Job | 설명 |
| --- | --- |
| PCB: Export 3D Model | 보드 3D 모델 export. 포맷: STEP, GLB(binary glTF), XAO, BREP(OCCT), PLY, STL, STPZ, U3D, PDF |
| PCB: Export Board Statistics | Board Statistics 리포트(JSON 또는 text) 생성 |
| PCB: Export Drill Data | 보드에서 drill 파일 export |
| PCB: Export DXF | 보드 설계를 DXF로 export |
| PCB: Export Gencad | 보드 설계를 GenCAD 포맷으로 export |
| PCB: Export Gerbers | 보드 설계를 Gerber로 export(선택 레이어당 1파일) |
| PCB: Export IPC-2581 | 보드 설계를 IPC-2581 포맷으로 export |
| PCB: Export ODB++ | 보드 설계를 ODB++ 포맷으로 export |
| PCB: Export PDF | 보드 설계를 PDF로 export(레이어당 1파일, plot 설정에 따라 다중 레이어 단일 PDF 가능) |
| PCB: Export Position Data | position(component placement) 파일 export |
| PCB: Export PostScript | 보드 설계를 PostScript로 export |
| PCB: Export SVG | 보드 설계를 SVG로 export |
| PCB: Perform DRC | 보드 Design Rule Check 실행 + 리포트. DRC 위반 발견 시 선택적으로 job 실패 보고 가능 |
| PCB: Render | 보드 3D 모델 raytraced 렌더링(PNG/JPG) 생성 |
| Schematic: Export DXF | 회로도를 DXF로 export |
| Schematic: Export Netlist | 회로도에서 netlist export(여러 포맷) |
| Schematic: Export PDF | 회로도를 PDF로 export |
| Schematic: Export Postscript | 회로도를 PostScript로 export |
| Schematic: Export SVG | 회로도를 SVG로 export |
| Schematic: Generate Bill of Materials | 회로도에서 BOM export |
| Schematic: Perform ERC | 회로도 Electrical Rule Check 실행 + 리포트. ERC 위반 발견 시 선택적으로 job 실패 보고 가능 |
| Special: Copy Files | 지정 파일을 지정 위치로 복사. 복사 실패 시 선택적으로 job 실패. 출력 위치 파일 덮어쓰기 여부 제어 가능 |
| Special: Execute Command | 임의 명령 실행. 출력을 파일에 로깅 가능. non-zero exit code를 무시하거나 job 실패로 처리 가능. 플랫폼 셸에서 실행(Linux/macOS `/bin/sh -c`, Windows `cmd.exe \c`)되어 globbing·pipe 등 셸 기능 사용 가능. **Note**: 잡 출력은 임시 폴더에 생성 후 모든 잡 완료 시 destination으로 이동되므로, Execute Command 실행 시점에 다른 잡 출력은 아직 임시 위치에 있음. 임시 위치 참조 필요 시 `${JOBSET_OUTPUT_WORK_PATH}` 사용 |

## Project templates · #project-templates

- 프로젝트 템플릿으로 미리 정의된 설정의 새 프로젝트를 손쉽게 셋업. 포함 가능: sheet sizes, drawing sheets, board outlines, connector positions, schematic elements, design rules, logos 등. seed 파일로 완전한 회로도/PCB도 포함 가능.

### Using templates · #using_templates

- 새 프로젝트 생성(**File** → **New Project…**) 시 Project Template Selector 다이얼로그가 열림. 기본적으로 설치된 모든 템플릿 표시. 목록 위 드롭다운으로 system/user 템플릿으로 한정 가능:
  - *System templates*: KiCad과 함께 설치(일부 일반 form factor 설계용).
  - *User templates*: 사용자가 만든 템플릿. 기본 빈 KiCad 템플릿도 user template으로 간주.
- 템플릿 클릭 시 오른쪽 패널에 정보 표시. **OK** 클릭 → 선택 템플릿 기반 새 프로젝트 생성. 이름·생성 위치 지정. 템플릿 파일이 새 위치로 복사되며 새 프로젝트 이름으로 rename.

### Template locations · #template-locations

- Project Template Selector는 두 위치의 템플릿 표시:
  - **System Templates**: `KICAD10_TEMPLATE_DIR` 경로 변수가 정의한 경로. KiCad 기본 라이브러리와 함께 설치되며 사용자 수정 비권장.
  - **User templates**: `KICAD_USER_TEMPLATE_DIR` 경로 변수가 정의한 경로. 직접 만든 템플릿은 여기 저장.
- user template 폴더 위치 변경: paths 설정에서 `KICAD_USER_TEMPLATE_DIR` 편집.

### Template contents · #template-contents

- KiCad 템플릿 = 템플릿 프로젝트 파일들 + `meta` 하위 디렉토리(필수 메타데이터)를 담은 디렉토리. 디렉토리 이름이 템플릿 이름을 결정. 즉 KiCad 템플릿 폴더 = `meta` 하위 디렉토리가 추가된 KiCad 프로젝트 폴더.
- 템플릿으로 프로젝트 생성 시 모든 파일이 복사되며 새 프로젝트 이름에 맞게 rename. 단 3가지 예외:
  - `.`로 시작하는 dotfiles는 복사 안 됨. 단 `.gitignore`·`.gitattributes`는 존재 시 복사(특수 케이스).
  - `.gitignore`가 있으면 거기서 ignore된 파일은 복사 안 됨.
  - `meta` 디렉토리는 복사 안 됨.
- ⚠️ **NOTE**: 위 예외 외에는 KiCad 설계 파일이 아니어도 모두 복사됨 → 문서 템플릿, license 파일, logos, `.gitignore` 등 비-KiCad 파일이 미리 셋업된 프로젝트 생성에 템플릿 활용 가능.

#### Template metadata · #template-metadata

- 템플릿 `meta` 디렉토리는 `info.html` HTML 파일을 **반드시** 포함. KiCad 템플릿 브라우저에 표시되며 템플릿 기본 정보 기술. 기본 HTML 기능(이미지 포함) 지원. `info.html`이 참조하는 이미지도 `meta`에 저장.
- `<title>` 태그가 템플릿 선택 시 표시 이름 결정(너무 길면 잘림). 이 표시 이름은 템플릿 디렉토리 이름과 같지 않아도 됨.
- 샘플 `info.html`:

```
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html;
charset=windows-1252">
<TITLE>Raspberry Pi - Expansion Board</TITLE>
</HEAD>
<BODY LANG="fr-FR" DIR="LTR">
<P>This project template is the basis of an expansion board for the
<A HREF="http://www.raspberrypi.org/" TARGET="blank">Raspberry Pi $25
ARM board.</A> <BR><BR>This base project includes a PCB edge defined
as the same size as the Raspberry-Pi PCB with the connectors placed
correctly to align the two boards. All IO present on the Raspberry-Pi
board is connected to the project through the 0.1&quot; expansion
headers. <BR><BR>The board outline looks like the following:
</P>
<P><IMG SRC="brd.png" NAME="brd" ALIGN=BOTTOM WIDTH=680 HEIGHT=378
BORDER=0><BR><BR><BR><BR>
</P>
<P>(c)2012 Brian Sidebotham<BR>(c)2012 KiCad Developers</P>
</BODY>
</HTML>
```

- `meta`는 선택적으로 `icon.png`(템플릿 선택 다이얼로그 아이콘)도 포함 가능. 아이콘은 **64 x 64 pixel PNG** 권장.

#### Template file renaming · #template_file_renaming

- 템플릿의 모든 파일·디렉토리는 새 프로젝트 경로로 복사됨(단 `meta`·dotfiles 제외). 템플릿 디렉토리 이름을 포함하는 파일/디렉토리는 새 프로젝트 파일 이름으로 rename. 템플릿 이름을 포함하지 않으면 원래 이름 유지.
- 예: 템플릿 `example`로 프로젝트 `newproject` 생성(rename된 것은 굵게):

| 템플릿 `example` 디렉토리 파일 | 프로젝트 `newproject` 디렉토리 생성 파일 |
| --- | --- |
| `example.kicad_pro` `example.kicad_sch` `example.kicad_pcb` `example-first.kicad_sch` `second-example.kicad_sch` `third.kicad_sch` `third.kicad_pcb` | `newproject.kicad_pro` `newproject.kicad_sch` `newproject.kicad_pcb` `newproject-first.kicad_sch` `second-newproject.kicad_sch` `third.kicad_sch` `third.kicad_pcb` |

- 템플릿에 필수 프로젝트 파일이 빠지면 KiCad이 기본 프로젝트 생성 동작으로 채움:

| 템플릿 `example` 디렉토리 파일 | `newproject` 디렉토리 생성 파일 |
| --- | --- |
| `example.kicad_sch` `first-example.kicad_sch` `first-example.kicad_pcb` `second-example.kicad_sch` `second-example.kicad_pcb` | `newproject.kicad_sch` `first-newproject.kicad_sch` `first-newproject.kicad_pcb` `second-newproject.kicad_sch` `second-newproject.kicad_pcb` `newproject.kicad_pro`(기본) `newproject.kicad_pcb`(기본) |

- rename 규칙 예외: 템플릿에 프로젝트 파일(`.kicad_pro`)이 하나 있고 그 이름이 템플릿 이름과 다르면, KiCad은 그 프로젝트 파일 이름 기준으로 rename:

| 템플릿 `example` 디렉토리 파일 | `newproject` 디렉토리 생성 파일 |
| --- | --- |
| `example.kicad_sch` `example.kicad_pcb` `first-example.kicad_pro` `first-example.kicad_sch` `first-example.kicad_pcb` `second-example.kicad_sch` `second-example.kicad_pcb` | `example.kicad_sch` `example.kicad_pcb` `newproject.kicad_pro` `newproject.kicad_sch` `newproject.kicad_pcb` `second-example.kicad_sch` `second-example.kicad_pcb` |

- ⚠️ **WARNING**: 여러 프로젝트 파일을 가진 템플릿 생성은 비권장.

### Creating new templates · #creating_new_templates

- KiCad 템플릿은 메타데이터 폴더가 추가된 KiCad 프로젝트일 뿐이므로, 프로젝트에서 시작하는 것이 가장 쉬움. user template 폴더에 프로젝트를 저장하고 `meta` 폴더를 추가하면 템플릿으로 사용 가능.
- 💡 **TIP**: user template 폴더 위치 확인 → Configure Paths 다이얼로그(**Preferences** → **Configure Paths…**)의 `KICAD_USER_TEMPLATE_DIR` 값 확인.
- 처음부터 만들기: user template 폴더에 새 프로젝트 생성 후 원하는 템플릿이 될 때까지 편집(생성 시 이름이 템플릿 이름).
- 기존 프로젝트를 템플릿화: 프로젝트 매니저에서 **File** → **Save As…**로 user template 폴더에 복사 저장(저장 이름이 템플릿 이름). 이후 편집.
- 어느 경우든 템플릿은 메타데이터 디렉토리 필수 → 템플릿 폴더 안에 `meta` 폴더 + `info.html`(템플릿 설명) 추가. 위 샘플 `info.html`을 시작점으로 사용 가능.
- 일반적으로 템플릿마다 포함하고 싶지 않은 파일·폴더 제거 권장: `*-backups` 폴더, `.history` 스냅샷 폴더, 불필요한 버전 관리 파일(`.git` 등) 등.

## Plugin and Content Manager · #plugin-content-manager

- PCM은 다른 사용자·조직이 제출한 패키지를 탐색·설치·관리하는 도구. 패키지 종류: 전문 기능 plugins, 특정 제조사 PCB 주문 도구, 심볼·풋프린트 라이브러리, 새 에디터 color schemes. 메인 프로젝트 매니저 창에서 실행.
- PCM은 인터넷 repository에서 패키지 다운로드. 각 repository는 개인/조직이 관리하는 패키지 모음. 기본적으로 KiCad 조직이 관리하는 단일 repository 사용. 사용자·조직이 자체 repository(public/private) 생성 가능, 타 사용자가 추가 가능.
- ⚠️ **NOTE**: 패키지는 컴퓨터에서 실행되는 코드를 설치할 수 있음. KiCad 개발자가 만든 것이 아니며 KiCad 조직은 품질·안전을 보증하지 않음 → 신뢰하는 패키지만 설치할 것.
- ⚠️ **NOTE**: 패키지 피드백은 KiCad 팀이 아닌 패키지 개발자에게 제출. 연락처는 패키지 설명에 표시됨.
- 직접 만든 패키지 공유: KiCad official repository에 제출(승인 시 다른 사용자에게 노출). 자체 repository 생성 또는 타인 repository에 제출도 가능(단 해당 repository를 설정한 사용자만 봄).

### Browsing packages · #browsing_packages

- repository의 모든 패키지는 PCM의 **Repository** 탭에 표시. 탭 상단 드롭다운으로 탐색할 repository 선택. 기본적으로 KiCad official repository만 활성화.
- 패키지는 4개 카테고리(각각 **Repository** 탭 내 자체 탭):
  - **Plugins**: PCB Editor에서 실행 가능한 추가 도구(보드 수정, 특정 출력 생성 등). Footprint wizards도 plugins로 배포 가능.
  - **Fabrication plugins**: 특정 제조사 PCB 주문용 plugins 하위 카테고리. 편리하나 보통 필수 아님(일반 fabrication 출력으로 주문 가능). 제조사에 최적 주문 방법 확인.
  - **Libraries**: 심볼/풋프린트/3D 모델. 기본적으로 패키지 설치 시 적절한 라이브러리 테이블에 자동 추가, 제거 시 자동 삭제. 라이브러리 이름 prefix 설정 가능(기본 `PCM_`). 설정 위치: Preferences의 **Packages and Updates** 섹션.
  - **Color themes**: Schematic/Symbol/Board/Footprint 에디터용 color themes. 설치된 테마는 각 에디터 Preferences의 **Colors** 섹션에서 선택.
- 왼쪽 목록 = 각 카테고리 패키지. 상단 filter box로 필터링. **Refresh** 버튼으로 온라인 repository에서 목록 재로드.
- 패키지 선택 시 오른쪽에 정보(설명, license, 개발자 연락처, 버그/피드백 보고처) 표시. 사용 가능 버전 표(크기, 상태, 현재 KiCad 버전 호환 여부)도 표시.
- 패키지 상태(개발자 지정):
  - **Stable**: 일반 사용에 적합.
  - **Testing**: 테스트 단계, 주의 필요, 이슈 보고 권장.
  - **Development**: 개발 단계, 완전 동작 기대 금물.
  - **Deprecated**: 더 이상 유지보수 안 됨.
- 기본적으로 버전 표는 현재 KiCad 버전 호환 버전만 표시. **Show all versions** 체크 시 비호환 버전도 표시. 여러 버전 있으면 설치할 버전 선택 가능.

### Installing packages · #installing_packages

- 설치: 패키지 설명 페이지의 **Install** 버튼 클릭(여러 버전 있으면 버전 표에서 선택 후). 패키지 목록의 **Install** 버튼으로 최신 버전 설치도 가능. 즉시 설치되지 않고 **Pending** 탭에 대기열로 추가됨 → **Apply Pending Changes** 버튼 클릭 시 모든 pending 패키지 일괄 설치.
- pending 단일 제거: **Pending** 탭에서 선택 후 trash 버튼. 전체 취소: **Discard Pending Changes**.
- 설치 후 **Installed** 탭에 표시(업데이트/제거 가능).
- 새 버전 있는 패키지가 있으면 프로젝트 매니저의 PCM 아이콘에 가능 업데이트 수 인디케이터 표시.
- 업데이트: 버전 표에서 새 버전 선택 후 **Update**. installed 목록의 **Uninstall** 옆 드롭다운 메뉴 **Update**로 최신 버전 업데이트도 가능. 전체 업데이트: installed 목록 상단 **Update All**. 단 드롭다운에서 **Pin Package** 선택된 패키지는 업데이트 안 됨.
- 제거: installed 목록 또는 패키지 설명 페이지의 **Uninstall** 버튼.
- 설치와 마찬가지로 update/uninstall도 즉시 실행되지 않고 **Pending** 탭에 대기 → 개별 적용 또는 **Apply Pending Changes**.
- 설치 없이 다운로드만: 패키지 설명 하단 **Download** 버튼(위치 선택) → 설치 전 파일 검사 가능. 다운로드된 패키지 설치: **Install from file…** 버튼으로 선택. **Open Package Directory** 버튼으로 KiCad 패키지 설치 폴더 열기.

### Managing repositories · #managing_repositories

- 기본적으로 KiCad official repository만 사용. 서드파티 repository 추가/제거: **Repository** 탭 상단 **Manage…** 버튼.
- 추가: **+** 버튼 → repository 전체 URL 지정. 제거: 선택 후 trash 버튼. 순서 변경: up/down 버튼.
- 기본 KiCad official repository를 제거했다면 **+** 옆 드롭다운 메뉴의 **Add Default Repository**로 쉽게 재추가.

### Creating packages and repositories · #pcm-creating-packages

- PCM 패키지 생성: https://dev-docs.kicad.org/en/addons/index.html 지침 따름(모든 repository용 패키지 생성법 + KiCad repository 포함 규칙·제출 방법). 서드파티 repository는 같은 패키지 포맷이나 규칙·절차가 다를 수 있음.
- 자체 repository 생성: https://go.kicad.org/pcm/schemas/v1 스키마를 따르는 repository JSON 파일 publish.

## KiCad preferences · #kicad-manager-configuration

- KiCad 환경설정은 **Preferences** 메뉴 또는 hotkey(기본 `Ctrl`+`,`)로 접근.
- ⚠️ **NOTE**: macOS에서는 **KiCad** → **Settings…** 로 접근.
- Preferences 다이얼로그는 KiCad 도구 간 공유. 일부는 전체 도구 공통, 일부는 특정 도구(회로도/보드 에디터) 전용.

### Common preferences · #common_preferences

- 전체 도구 공통 환경설정. 하위 항목:

**Rendering engine** · #rendering_engine
- **Accelerated graphics antialising**: GPU 렌더링 시 aliasing(들쭉날쭉한 선) 방지 방법. 하드웨어별로 다르게 보일 수 있으니 실험 권장.
- **Fallback graphics antialiasing**: fallback 그래픽 모드에서도 antialiasing 적용. 일부 하드웨어에서 성능 저하 가능.

**Helper applications** · #helper_applications
- **Text editor**: 프로젝트 트리뷰에서 텍스트 파일 열 때 사용할 에디터.
- **PDF viewer**: PDF 파일 열 때 사용할 프로그램.

**User interface** · #user_interface
- **Show icons in menus**: 드롭다운 메뉴에 아이콘 표시. ⚠️ **NOTE**: 일부 OS에서는 메뉴 아이콘이 표시되지 않음.
- **Show scrollbars in editors**: 각 도구 편집 캔버스 옆 스크롤바 표시 여부.
- **Focus follows mouse between schematic and PCB editors**: 활성화 시 마우스 커서 아래 창이 자동 포커스됨.
- **Show popup indicator when toggling settings with hotkeys**: 설정을 순환하는 hotkey 사용 시 변경을 알리는 popup 인디케이터 표시.
- **Use alternating row colors in tables**: 테이블(라이브러리 테이블, Symbol Fields table 등)에 행마다 교대 색상 사용.
- **Disable custom cursors**: 활성화 시 KiCad이 context별 커스텀 커서 대신 시스템 커서 사용.
- **Icon theme**: 밝은/어두운 창 배경용 아이콘 테마 선택. 기본 Automatic은 OS 창 테마 밝기에 따라 선택. ⚠️ **NOTE**: light 테마는 밝은 배경에 잘 보이는 어두운 아이콘, dark 테마는 어두운 배경용 밝은 아이콘.
- **Icon scale**: 메뉴·버튼 아이콘 크기. *Automatic*은 OS 설정 기반 자동 선택.
- **High-contrast mode dimming factor**: high-contrast 표시 모드에서 비포커스 항목을 얼마나 흐리게 할지.

**Scaling** · #scaling
- **Display PPI**: 디스플레이 픽셀 밀도로 설정 시 100% 줌에서 객체가 실제 크기로 표시. **Detect** 버튼으로 디스플레이 보고 밀도 사용, 또는 ruler가 올바른 크기로 표시될 때까지 수동 조정.

**Editing** · #editing
- **Warp mouse to origin of moved object**: 객체 이동 명령 시작 시 마우스 커서를 객체 원점으로 재배치(warp).
- **First hotkey selects tool**: 비활성화 시 *Add Wire* 같은 명령 hotkey를 누르면 현재 커서 위치에서 즉시 명령 시작. 활성화 시 첫 hotkey는 도구만 선택하고 즉시 시작하지 않음.

**Session** · #session
- **Remember open files for next project launch**: 활성화 시 프로젝트 재오픈 시 이전에 열려 있던 파일 자동 재오픈.

**Project backup** · #project_backup
- **Automatically backup projects**: 활성화 시 현재 프로젝트의 백업·autosave 자동 생성. autosave는 미저장 변경이 있고 몇 초 비활성 시, 백업은 수동 저장 시마다.
- **Format**: 백업 포맷.
  - **Incremental**: 증분 백업 시스템(파일 변경 스냅샷 저장). Local History 패널(**View** → **Panels** → **Local History**)에 표시. 스냅샷 우클릭 → **Restore Commit**으로 복원. 내부적으로 숨김 `.history` 폴더의 Git 저장소 사용.
  - **Zip archive**: 프로젝트 디렉토리·내용을 Zip 아카이브로 저장. Unarchive 도구 또는 수동 추출로 복원.
- **Location**: 백업 저장 위치 — 프로젝트 디렉토리 또는 KiCad 사용자 데이터(설정) 디렉토리.
- **Maximum total backup size**: 새 백업 생성 시 이 한도 미만 유지를 위해 가장 오래된 백업부터 삭제.

### Mouse and touchpad preferences · #mouse_and_touchpad_preferences

- **Center and warp cursor on zoom**: hotkey/마우스 휠 줌 시 커서 위치 중심으로 뷰 중앙 정렬.
- **Use zoom acceleration**: 휠/터치패드를 빠르게 스크롤할수록 줌 변화도 빨라짐.
- **Zoom speed**: 휠/터치패드 스크롤 양에 대한 줌 변화량. *Automatic*은 OS별 기본값.
- **Automatically pan while moving object**: 활성화 시 객체 이동 중 캔버스 가장자리 근처로 이동하면 뷰 pan.
- **Auto pan speed**: 객체 이동 중 캔버스 pan 속도.
- **Mouse buttons**: 중간/오른쪽 버튼 드래그 동작(zoom/pan/없음) 설정. 왼쪽 버튼 드래그 동작은 객체 선택 여부에 따라 설정 가능. **Pan on mouse movement with key**에 키 설정 시 그 키를 누른 채 마우스 이동으로 pan. ⚠️ **NOTE**: 왼쪽 버튼은 항상 객체 선택·조작용.
- **Mouse wheel and touchpad scrolling**: 특정 modifier 키를 누른 채 휠/터치패드 수직 이동 동작 설정.
- **Pan left/right with horizontal movement**: 활성화 시 터치패드/수평 스크롤 휠로 뷰 pan 가능.

### SpaceMouse preferences · #spacemouse_preferences

- SpaceMouse 주변기기 통합 설정.
- **Rotation speed** / **Pan speed**: SpaceMouse 입력에 대한 회전·pan 속도.
- **Reverse rotation direction**: 회전 방향 반전.
- **Reverse vertical pan direction**: 수직 pan 방향 반전.
- **Reverse horizontal pan direction**: 수평 pan 방향 반전.
- **Reverse zoom direction**: 줌 방향 반전.

### Hotkey preferences · #hotkey_preferences

- 단축키 커스터마이즈 다이얼로그. *Common* 섹션 hotkey는 모든 KiCad 프로그램 공유. 같은 hotkey를 서로 다른 프로그램(회로도/보드 에디터)의 다른 동작에 할당 가능하나, **같은 프로그램 내**에서는 한 hotkey를 둘 이상 동작에 할당 불가.
- 많은 명령이 있어 기본 hotkey가 없는 것도 많음. 목록의 명령을 더블클릭해 hotkey 추가. 이미 다른 명령에 할당된 hotkey 선택 시, 그 hotkey를 선택 명령에 사용하면 충돌 명령에서 할당 제거됨.
- 변경된 할당은 명령 이름 끝에 `*` 문자로 표시. 특정 명령 변경 취소: 우클릭 → **Undo Changes**. 전체 취소: 목록 아래 버튼.

#### Importing hotkeys · #importing_hotkeys

- Hotkey 설정은 KiCad 설정 디렉토리의 `.hotkeys` 파일에 저장(설정 디렉토리 위치는 Settings 섹션 #settings 참조). 한 컴퓨터의 hotkey 설정을 다른 컴퓨터로 옮기려면 해당 `.hotkeys` 파일을 import.

### Version control preferences · #version_control_preferences

- KiCad의 Git 버전 관리 통합 설정.
- **Enable Git tracking**: 활성화 시 프로젝트 매니저의 Git 도구 사용 가능.
- **Update interval**: 원격 업데이트 확인 주기. 가능 업데이트는 트리 상태 아이콘으로 표시. **0**이면 원격 업데이트를 확인하지 않음.
- **Git commit data**: 새 commit의 author 정보 제어. **Use default values** 활성화 시 시스템 Git 설정에서 author·email 사용. 비활성화 시 author name·email 직접 지정.

### Data collection preferences · #data_collection_preferences

- KiCad이 사용·crash 데이터를 수집하는 방식 제어. **기본 비활성화**.
- ⚠️ **NOTE**: Crash reporting은 Windows·macOS만 지원.
- **I agree to provide anonymous reports** 활성화 시 crash 등 특정 상황에서 익명 리포트를 KiCad 개발팀에 전송(crash·버그 수정에 도움). 리포트에는 회로도/PCB 같은 설계 파일이 포함되지 않음.
- 리포트는 이 페이지에 표시되는 랜덤 고유 식별자에 연결(같은 컴퓨터의 리포트 연결용). IP 주소 등 PII는 저장·연결되지 않음. **Reset Unique Id** 버튼으로 언제든 식별자 재설정 가능.

### Packages and updates preferences · #packages_and_updates_preferences

- **Check for KiCad updates on startup**: 시작 시 KiCad 애플리케이션 업데이트 확인. 가능 시 설치 안내.
- **Check for package updates on startup**: 시작 시 PCM 설치 패키지 업데이트 확인. 가능 업데이트는 프로젝트 매니저 우하단 알림 표시.
- **Automatically add installed libraries to global library table**: PCM 설치 라이브러리를 라이브러리 테이블에 자동 추가(닉네임은 이 페이지 설정 prefix 사용). 비활성화 시 수동 추가 필요.
- **Automatically remove uninstalled libraries**: PCM 제거 라이브러리를 라이브러리 테이블에서 자동 제거. 비활성화 시 수동 제거 필요.

### Plugins preferences · #plugins_preferences

- **Enable KiCad API**: 활성화 시 KiCad IPC API와 상호작용하는 plugins 사용 가능. 비활성화 시 해당 plugins 미작동.
- **Path to Python interpreter**: KiCad이 Python 기반 IPC plugins 실행에 사용할 Python interpreter 위치. 자동 감지 또는 경로 수동 지정.

### Maintenance preferences · #maintenance_preferences

- **3D cache file duration**: 3D viewer 가속용 3D 모델 cache 보관 기간(이후 오래된 파일 삭제).
- **Clear "Open Recent" History**: **File** → **Open Recent** 메뉴 항목 삭제.
- **Reset "Don't Show Again" Dialogs**: **Don't Show Again**으로 숨긴 다이얼로그를 다시 표시.
- **Reset All Dialogs to Defaults**: 모든 KiCad 다이얼로그의 변경 설정 초기화.
- **Reset All Program Settings to Defaults**: 모든 KiCad preferences를 기본값으로 초기화.

## Actions reference · #actions_reference

- KiCad Project Manager에서 hotkey에 할당 가능한 모든 **action**(명령) 목록.

### KiCad Project Manager · #kicad_project_manager

- 아래 action들은 프로젝트 매니저에서 사용 가능. Preferences의 **Hotkeys** 섹션에서 임의의 hotkey 할당 가능.

| Action | Default Hotkey | Description |
| --- | --- | --- |
| Browse Project Files | | Open project directory in file explorer |
| Archive Project… | | Archive all project files |
| Close Project | | |
| Image Converter | `Ctrl`+`B` | Convert bitmap images to schematic or PCB components |
| Drawing Sheet Editor | `Ctrl`+`Y` | Edit drawing sheet borders and title block |
| Footprint Editor | `Ctrl`+`F` | Create, delete and edit PCB footprints |
| PCB Editor | `Ctrl`+`P` | Edit PCB in PCB editor |
| Schematic Editor | `Ctrl`+`E` | Edit schematic in schematic editor |
| Symbol Editor | `Ctrl`+`L` | Create, delete and edit schematic symbols |
| Clone Project from Repository… | | |
| New Jobset File… | | |
| New Project… | `Ctrl`+`N` | Create a new project based on an existing project |
| Open Demo Project… | | |
| Open Jobset File… | | |
| Open Project… | `Ctrl`+`O` | |
| Open Text Editor | | Launch preferred text editor |
| Plugin and Content Manager | `Ctrl`+`M` | Run Plugin and Content Manager |
| Restore Project from Local History… | | Restore project files from local history |
| Calculator Tools | | Run component calculations, track width calculations, etc. |
| Local History | | Show or hide local history panel |
| Unarchive Project… | | Unarchive project files from zip archive |
| Gerber Viewer | `Ctrl`+`G` | Preview Gerber output files |
