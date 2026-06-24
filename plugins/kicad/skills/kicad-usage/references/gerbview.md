# GerbView — 거버/드릴 뷰어 — KiCad 10.0 사용 다이제스트

> **원문**: https://docs.kicad.org/10.0/en/gerbview/gerbview.html

> **범위**: GerbView 소개(RS-274X·Excellon, 최대 32 레이어), 인터페이스(메인창·상단 툴바·좌측 툴바·Layers Manager), 메뉴 명령(File: Export to PCB Editor / Tools: List DCodes·Show Source·Measure·Clear Layer), 인쇄(Printing)

> 한국어 요약 다이제스트. 섹션 제목의 #anchor로 원문 핀포인트: https://docs.kicad.org/10.0/en/gerbview/gerbview.html#<anchor>

## 목차
- [Introduction to GerbView](#introduction_to_gerbview) — GerbView가 무엇인지(RS-274X·Excellon 뷰어, 최대 32 파일)
- [Interface](#interface) — UI 전체 구성 개요
- [Main window](#main_window) — 메인 창
- [Top toolbar](#top_toolbar) — 상단 툴바 버튼 일람
- [Left toolbar](#left_toolbar) — 좌측 툴바 버튼 일람
- [Layers Manager](#layers_manager) — 레이어 가시성·색상 관리
- [Commands in menu bar](#commands_in_menu_bar) — 메뉴 명령 개요
- [File menu](#file_menu) — Export to PCB Editor
- [Tools menu](#tools_menu) — List DCodes / Show Source / Measure / Clear Layer
- [Printing](#printing) — 인쇄

## Introduction to GerbView · #introduction_to_gerbview

- GerbView는 **Gerber 파일(RS-274X 포맷)** 과 **Excellon 드릴 파일** 뷰어다. 동시에 최대 **32개 파일**까지 표시할 수 있다.
- 포맷 상세 참고:
  - Gerber 파일 포맷: [the Gerber File Format Specification](http://www.ucamco.com/files/downloads/file/81/the_gerber_file_format_specification.pdf)
  - Excellon 드릴 포맷: [the Excellon format description](http://web.archive.org/web/20071030075236/http://www.excellon.com/manuals/program.htm)

## Interface · #interface

- GerbView 인터페이스는 메인 창, 상단 툴바, 좌측 툴바, Layers Manager로 구성된다(아래 각 섹션 참조).

### Main window · #main_window

- 로드한 거버/드릴 레이어가 그려지는 메인 작업 영역이다.

### Top toolbar · #top_toolbar

- 파일 로드/표시 제어, 페이지 설정, 인쇄, 줌, 활성 레이어 선택, Gerber X2 하이라이트 등 주요 명령에 접근하는 상단 툴바.

| 기능 | 설명 |
| --- | --- |
| Clear all layers | 모든 레이어 지우기 |
| Load Gerber files | Gerber 파일 로드 |
| Load Excellon drill files | Excellon 드릴 파일 로드 |
| Set page size | 페이지 크기 설정 |
| Print | 인쇄 |
| Redraw view | 화면 다시 그리기 |
| Zoom in or out | 확대/축소 |
| Zoom to fit page | 페이지에 맞게 줌 |
| Zoom to selection | 선택 영역으로 줌 |
| Select active layer | 활성 레이어 선택 |
| Display info about active layer | 활성 레이어 정보 표시 |
| Highlight items belonging to selected component (Gerber X2) | 선택한 컴포넌트에 속한 항목 하이라이트 (Gerber X2) |
| Highlight items belonging to selected net (Gerber X2) | 선택한 net에 속한 항목 하이라이트 (Gerber X2) |
| Highlight items with the selected attribute (Gerber X2) | 선택한 attribute를 가진 항목 하이라이트 (Gerber X2) |
| Highlight items of selected D Code on the active layer | 활성 레이어에서 선택한 D Code의 항목 하이라이트 |

### Left toolbar · #left_toolbar

- 선택/측정 도구, 그리드·좌표·단위 토글, 스케치(외곽선) 표시 모드, diff 모드, 레이어 매니저 표시 등 보기·편집 보조 명령을 모은 좌측 툴바.

| 기능 | 설명 |
| --- | --- |
| Select items | 항목 선택 |
| Measure between two points | 두 점 사이 거리 측정 |
| Toggle grid visibility | 그리드 표시 토글 |
| Toggle polar coordinates display | 극좌표 표시 토글 |
| Select inch, mils, or millimeter units | 단위 선택(inch / mils / millimeter) |
| Toggle full-screen cursor | 전체 화면 커서 토글 |
| Display flashed items in sketch (outline) mode | flashed 항목을 스케치(외곽선) 모드로 표시 |
| Display lines in sketch (outline) mode | 선(line)을 스케치(외곽선) 모드로 표시 |
| Display polygons in sketch (outline) mode | 폴리곤을 스케치(외곽선) 모드로 표시 |
| Show negative objects in ghost color | negative 객체를 ghost 색상으로 표시 |
| Show/hide D Codes | D Codes 표시/숨김 |
| Display layers in diff (compare) mode | 레이어를 diff(비교) 모드로 표시 |
| Toggle inactive layers between normal and dimmed display | 비활성 레이어를 normal/dimmed 표시 간 토글 |
| Show/hide layer manager | 레이어 매니저 표시/숨김 |
| Show Gerbers as mirror image | Gerber를 거울상(mirror)으로 표시 |

### Layers Manager · #layers_manager

- 로드된 모든 레이어의 **가시성과 색상**을 제어·표시하는 패널이다. 화살표가 활성 레이어를 가리키고, 각 레이어는 체크박스로 표시/숨김할 수 있다.
- 마우스 버튼 동작:

| 동작 | 결과 |
| --- | --- |
| Left click | 활성 레이어 선택 |
| Right click | 레이어 표시/숨김/정렬 옵션 표시 |
| Middle click 또는 (색상 스와치) Double click | 레이어 색상 선택 |

- **Layers 탭**: 로드된 모든 Gerber·드릴 레이어의 가시성과 색상을 제어.
- **Items 탭**: grid, D Codes, negative 객체의 색상과 표시를 제어.

## Commands in menu bar · #commands_in_menu_bar

- 메뉴 바의 명령은 File 메뉴와 Tools 메뉴로 나뉜다(아래 참조).

### File menu · #file_menu

- **Export to PCB Editor**: Gerber 파일을 KiCad PCB로 내보내는 **제한적** 기능. 최종 결과는 원본 Gerber가 사용한 RS-274X 기능에 따라 달라진다.
  - rasterized 항목(일반적으로 negative 객체)은 변환되지 않는다.
  - flashed 항목 → via로 변환.
  - line → track 세그먼트로 변환(비-copper 레이어는 graphic line으로 변환).

### Tools menu · #tools_menu

| 명령 | 설명 |
| --- | --- |
| **List DCodes** | 모든 레이어의 D Code 정보 표시 |
| **Show Source** | 활성 레이어의 Gerber 파일 내용을 텍스트 에디터로 표시 |
| **Measure Tool** | 두 점 사이 거리 측정 |
| **Clear Current Layer** | 활성 레이어 내용 삭제 |

## Printing · #printing

- 레이어를 인쇄하려면 Print 아이콘 또는 **File → Print** 메뉴를 사용한다.
- ⚠️ **CAUTION:** 항목이 인쇄 가능 영역(printable area) 안에 들어가도록 한다. Set page size(페이지 포맷) 기능으로 적절한 페이지 포맷을 선택하라. 많은 photoplotter는 대부분의 프린터가 사용하는 페이지 크기보다 훨씬 큰 plottable 영역을 지원하므로, 전체 레이어 세트를 이동(Moving the entire layer set)해야 할 수 있다.
