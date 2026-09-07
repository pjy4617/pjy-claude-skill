# KiCad 사용법 다이제스트 — 마스터 인덱스 (INDEX)

> KiCad 10.0 공식 매뉴얼 한국어 사용 다이제스트의 토픽 → 파일·anchor 라우팅 맵.
> `kicad-usage` 스킬은 사용자의 How-to 질문을 받으면 **이 파일을 먼저 보고** 해당 다이제스트 파일·섹션을 연다.
> 깊은 키워드 검색은 `grep -ri "키워드" references/`. 원문 점프 = `<파일의 원문 URL>#<anchor>`.

## A. 자주 묻는 How-to → 파일 · anchor

| 하고 싶은 것 | 파일 | anchor |
|---|---|---|
| KiCad 설치 / 최초 설정 | `kicad-project.md` | `#settings` |
| 프로젝트 생성·관리·백업·Git | `kicad-project.md` | `#using_the_kicad_project_manager` |
| 라이브러리(심볼/풋프린트) 경로 설정 | `kicad-project.md` | `#libraries-configuration` |
| 경로/환경변수(KIPRJMOD 등) | `kicad-project.md` | `#kicad-environment-variables` |
| 프로젝트 템플릿 | `kicad-project.md` | `#project-templates` |
| Jobsets(출력 자동화 묶음) | `kicad-project.md` | `#jobsets` |
| Plugin & Content Manager(PCM) | `kicad-project.md` | `#plugin-content-manager` |
| 회로도→PCB 반영(Update PCB / forward annotation) | `pcbnew-3-inspect-output.md` | `#forward-annotation` |
| 보드 스택업·임피던스·물리 파라미터 | `pcbnew-1-setup-ui.md` | `#board-setup-stackup` |
| 디자인 룰 제약(clearance/track width 등) | `pcbnew-1-setup-ui.md` | `#board-setup-constraints` |
| 넷 클래스 설정 | `pcbnew-1-setup-ui.md` | `#board-setup-net-classes` |
| 레이어 표시/Appearance 패널 | `pcbnew-1-setup-ui.md` | `#appearance-panel` |
| 트랙/비아 배선(interactive router) | `pcbnew-2-editing-routing.md` | `#routing-tracks` |
| 차동쌍(differential pair) 배선 | `pcbnew-2-editing-routing.md` | `#routing-differential-pairs` |
| 길이 튜닝(length tuning) | `pcbnew-2-editing-routing.md` | `#length-tuning` |
| Zone(구리 채움 / GND·전원 평면) | `pcbnew-2-editing-routing.md` | `#working-with-zones` |
| Teardrops | `pcbnew-2-editing-routing.md` | `#editing-teardrops` |
| 풋프린트 배치/이동/교체 | `pcbnew-2-editing-routing.md` | `#working-with-footprints` |
| 보드 외곽(Edge Cuts) 그리기 | `pcbnew-2-editing-routing.md` | `#board-outlines` |
| DRC(Design Rule Check) 실행 | `pcbnew-3-inspect-output.md` | `#design-rule-checking` |
| 3D 뷰어 | `pcbnew-3-inspect-output.md` | `#threed-viewer` |
| Net inspector(넷 길이/통계) | `pcbnew-3-inspect-output.md` | `#net-inspector` |
| 거버 내보내기(Plot) | `pcbnew-3-inspect-output.md` | `#plotting` |
| 드릴 파일 생성 | `pcbnew-3-inspect-output.md` | `#drill-files` |
| STEP/3D 모델 내보내기 | `pcbnew-3-inspect-output.md` | `#_3d-export` |
| BOM / Position(배치) 파일 | `pcbnew-3-inspect-output.md` | `#bill_of_materials` |
| 타 EDA 보드 임포트 | `pcbnew-3-inspect-output.md` | `#importing-boards` |
| Design variants(설계 변형) | `pcbnew-3-inspect-output.md` | `#pcb-design-variants` |
| 풋프린트 라이브러리 관리 | `pcbnew-4-footprints.md` | `#managing-footprint-libraries` |
| 풋프린트 새로 만들기/편집 | `pcbnew-4-footprints.md` | `#creating_a_new_footprint` |
| 패드 속성 편집 | `pcbnew-4-footprints.md` | `#fp-pads` |
| 멀티채널 레이아웃(채널 복제) | `pcbnew-4-footprints.md` | `#multichannel` |
| 디자인 블록(design blocks) | `pcbnew-4-footprints.md` | `#pcb-design-blocks` |
| 커스텀 디자인 룰(.kicad_dru) 문법·예제 | `pcbnew-5-advanced-rules.md` | `#custom-design-rules` |
| 그래픽 디자인 룰 편집기 | `pcbnew-5-advanced-rules.md` | `#graphical-design-rule-editor` |
| Text variables(${VAR}) | `pcbnew-5-advanced-rules.md` | `#text-variables` |
| Python 스크립팅(pcbnew API) | `pcbnew-5-advanced-rules.md` | `#scripting` |
| PCB 에디터 단축키 전체 | `pcbnew-6-hotkeys.md` | `#pcb_editor` |
| GerbView로 거버/드릴 보기 | `gerbview.md` | `#interface` |
| GerbView D-code 보기/Show source | `gerbview.md` | `#tools_menu` |
| kicad-cli로 PCB DRC 자동화 | `kicad-cli.md` | `kicad-cli pcb drc` |
| kicad-cli로 거버/드릴 내보내기 | `kicad-cli.md` | `kicad-cli pcb export gerbers` |
| kicad-cli로 넷리스트/ERC 추출 | `kicad-cli.md` | `kicad-cli sch export netlist / sch erc` |

## B. 파일별 전체 섹션 목록 (anchor)

각 `#anchor`는 원문 점프 키다(`<원문 URL>#anchor`). 파일을 Read 후 `· #anchor`로 해당 섹션을 찾는다.

### `kicad-project.md` — KiCad 프로젝트 매니저 · 환경 · 파일/라이브러리
원문: https://docs.kicad.org/10.0/en/kicad/kicad.html  ·  섹션 61개

- `#introduction` — Introduction
- `#system_requirements` — System Requirements
- `#installing_and_upgrading_kicad` — Installing and Upgrading KiCad
- `#settings` — First time setup
- `#configuration_setup` — Configuration setup
- `#libraries_setup` — Libraries setup
- `#updates_privacy_setup` — Updates & Privacy setup
- `#migrating_design_files_from_previous_versions` — Migrating design files from previous versions
- `#using_the_kicad_project_manager` — Using the KiCad project manager
- `#standalone_mode` — Standalone mode
- `#creating_a_new_project` — Creating a new project
- `#importing_a_project_from_another_eda_tool` — Importing a project from another EDA tool
- `#backups-and-autosave` — Project backups and autosave
- `#incremental_backups` — Incremental backups
- `#zip_archives` — Zip archives
- `#project-archive` — Saving and loading project archives
- `#git-integration` — Git integration
- `#adding_version_control_to_an_existing_project` — Adding version control to an existing project
- `#cloning_an_existing_repository` — Cloning an existing repository
- `#tracking_project_changes_with_git` — Tracking project changes with Git
- `#kicad_files_and_folders` — KiCad files and folders
- `#project_files` — Project files
- `#schematic_editor_files_and_folders` — Schematic editor files and folders
- `#board_editor_files_and_folders` — Board editor files and folders
- `#common_files` — Common files
- `#fabrication_and_documentation_files` — Fabrication and documentation files
- `#storing_and_sending_kicad_files` — Storing and sending KiCad files
- `#path-variables` — Paths and libraries configuration
- `#kicad-environment-variables` — KiCad path variables
- `#advanced_environment_variables` — Advanced environment variables
- `#libraries-configuration` — Libraries configuration
- `#jobsets` — Jobsets
- `#defining_jobs` — Defining jobs
- `#jobset-destinations` — Defining jobset destinations
- `#jobset_destination_details` — Jobset destination details
- `#job-types` — Available job types
- `#project-templates` — Project templates
- `#using_templates` — Using templates
- `#template-locations` — Template locations
- `#template-contents` — Template contents
- `#template-metadata` — Template metadata
- `#template_file_renaming` — Template file renaming
- `#creating_new_templates` — Creating new templates
- `#plugin-content-manager` — Plugin and Content Manager
- `#browsing_packages` — Browsing packages
- `#installing_packages` — Installing packages
- `#managing_repositories` — Managing repositories
- `#pcm-creating-packages` — Creating packages and repositories
- `#kicad-manager-configuration` — KiCad preferences
- `#common_preferences` — Common preferences
- `#mouse_and_touchpad_preferences` — Mouse and touchpad preferences
- `#spacemouse_preferences` — SpaceMouse preferences
- `#hotkey_preferences` — Hotkey preferences
- `#importing_hotkeys` — Importing hotkeys
- `#version_control_preferences` — Version control preferences
- `#data_collection_preferences` — Data collection preferences
- `#packages_and_updates_preferences` — Packages and updates preferences
- `#plugins_preferences` — Plugins preferences (외부 도구(MCP 등)의 IPC 연동은 여기서 Enable KiCad API 로 켠다)
- `#maintenance_preferences` — Maintenance preferences
- `#actions_reference` — Actions reference
- `#kicad_project_manager` — KiCad Project Manager

### `pcbnew-1-setup-ui.md` — PCB 에디터 ① 화면/표시·선택·보드 셋업
원문: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html  ·  섹션 57개

- `#introduction_to_the_kicad_pcb_editor` — Introduction to the KiCad PCB Editor
- `#the_pcb_editor_user_interface` — The PCB Editor user interface
- `#navigating_the_editing_canvas` — Navigating the editing canvas
- `#hotkeys` — Hotkeys
- `#display-and-selection` — Display and selection controls (그룹)
- `#board_layers` — Board layers
- `#display_order_for_board_layers` — Display order for board layers
- `#appearance-panel` — The appearance panel
- `#layer_controls` — Layer controls
- `#object_controls` — Object controls
- `#layer_presets` — Layer presets
- `#viewports` — Viewports
- `#net_and_net_class_controls` — Net and net class controls
- `#selection` — Selection and the selection filter
- `#net-highlighting` — Net highlighting
- `#cross_probing_from_the_schematic` — Cross-probing from the schematic
- `#left-toolbar-display-controls` — Left toolbar display controls
- `#creating_a_pcb` — Creating a PCB
- `#basic_pcb_concepts` — Basic PCB concepts
- `#capabilities` — Capabilities
- `#starting_from_a_schematic` — Starting from a schematic
- `#starting-from-scratch` — Starting from scratch
- `#board_setup` — Board setup
- `#board-setup-stackup` — Configuring board stackup and physical parameters
- `#board_editor_layers` — Board editor layers
- `#physical_stackup` — Physical stackup
- `#board_finish` — Board finish
- `#solder_maskpaste` — Solder mask/paste
- `#zone_hatch_offsets` — Zone hatch offsets
- `#configuring_text_and_graphics` — Configuring text and graphics
- `#board-setup-defaults` — Defaults
- `#formatting` — Formatting
- `#board-setup-text-variables` — Text variables
- `#configuring_design_rules` — Configuring design rules
- `#board-setup-constraints` — Constraints
- `#board-setup-pre-defined-sizes` — Pre-defined sizes
- `#board-setup-teardrops` — Teardrops
- `#length_tuning_patterns` — Length-tuning patterns
- `#tuning_profiles` — Tuning profiles
- `#when_to_enable_time_domain_tuning` — When to enable time-domain tuning
- `#understanding_track_propagation_parameters` — Understanding track propagation parameters
- `#understanding_via_propagation_parameters` — Understanding via propagation parameters
- `#how_tuning_profiles_net_classes_and_the_length_tuner_work_together` — How tuning profiles, net classes, and the length tuner work together
- `#board-setup-net-classes` — Net classes
- `#component-classes` — Component classes
- `#component-class-concepts` — Understanding component classes
- `#where_component_classes_are_defined` — Where component classes are defined
- `#how_multiple_classes_combine` — How multiple classes combine
- `#schematic_defined_and_pcb_defined_classes` — Schematic-defined and PCB-defined classes
- `#component-class-assignment-rules` — Assignment rule details
- `#assignment_rule_examples` — Assignment rule examples
- `#how_classes_update` — How classes update
- `#component-classes-in-drc` — Using component classes in custom DRC rules
- `#custom_rules` — Custom rules
- `#board-setup-violation-severity` — Violation severity
- `#pcb-embedding-files` — Embedding files
- `#importing_settings` — Importing settings

### `pcbnew-2-editing-routing.md` — PCB 에디터 ② 편집·배치·배선
원문: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html  ·  섹션 108개

- `#editing_a_board` — Editing a board (개요)
- `#placement-and-drawing-operations` — Placement and drawing operations
- `#grids-and-snapping` — Grids and snapping
- `#snapping_to_graphical_shapes` — Snapping to graphical shapes
- `#grid_settings` — Grid settings
- `#editing-object-properties` — Editing object properties
- `#board-outlines` — Board outlines (Edge Cuts)
- `#working-with-footprints` — Working with footprints
- `#adding_footprints_to_the_board` — 풋프린트 추가
- `#placing_and_moving_footprints` — 풋프린트 배치/이동
- `#board-editing-footprints` — 보드 내 풋프린트 편집
- `#editing_footprint_fields` — 풋프린트 필드 편집
- `#updating-and-exchanging-footprints` — 풋프린트 갱신/교환
- `#comparing-footprints` — 보드↔라이브러리 풋프린트 비교
- `#working_with_pads` — Working with pads
- `#working-with-zones` — Working with zones
- `#drawing_zones` — Drawing zones
- `#zone-properties` — Zone properties
- `#clearances_pad_connections` — Clearances & pad connections
- `#display_overrides` — Display overrides
- `#zone-hatching` — Hatched fill
- `#zone-manager` — Zone manager
- `#zone_list` — Zone list
- `#zone_preview` — Zone preview
- `#zone_settings` — Zone settings
- `#routing-tracks` — Routing tracks and vias
- `#interactive-router-settings` — Interactive router settings
- `#track-posture` — Track posture
- `#track_corner_mode` — Track corner mode
- `#track_width` — Track width
- `#placing-vias` — Placing vias
- `#layer_pairs` — Layer Pairs
- `#placing-free-vias` — Placing free vias
- `#modifying-tracks` — Modifying tracks
- `#track-and-via-properties` — Editing track and via properties
- `#track_and_via_nets` — Track and via nets
- `#track_size_position_and_layers` — Track size, position, and layers
- `#via_size_position_and_layers` — Via size, position, and layers
- `#via-treatment-properties` — Via protection (IPC-4761)
- `#via_backdrilling_and_post_machining_counterbores_and_countersinks` — Via backdrilling and post-machining
- `#via-back-drilling` — Back-drilling
- `#via-post-machining` — Post-machining (counterbore/countersink)
- `#via_teardrops` — Via teardrops
- `#bulk-editing-tracks-and-vias` — Bulk editing tracks and vias
- `#removing-unused-pads` — Removing unused pads
- `#cleaning-up-tracks-and-vias` — Cleaning up tracks and vias
- `#routing_convenience_functions` — Routing Convenience Functions
- `#automatically_completing_tracks` — Automatically completing tracks
- `#routing-differential-pairs` — Routing differential pairs
- `#length-tuning` — Length tuning
- `#editing-tuning-patterns` — Editing tuning patterns
- `#setting-target-length-and-skew` — Setting target length and skew
- `#length_tuning_pitfalls_and_tips` — Length tuning pitfalls and tips
- `#time-domain-tuning` — Time-domain tuning (propagation delay)
- `#when_to_use_each_mode` — When to use each mode
- `#how_time_domain_tuning_works` — How time-domain tuning works
- `#board_stackup_and_delay_calculations` — Board stackup and delay calculations
- `#propagation_delay_calculation_details` — Propagation delay calculation details
- `#per_layer_delay_tracking` — Per-layer delay tracking
- `#setting_target_delay` — Setting target delay
- `#practical_example_ddr4_memory_bus` — Practical example: DDR4 memory bus
- `#drc_integration` — DRC integration
- `#editing-teardrops` — Teardrops
- `#adding_teardrops_in_bulk` — Adding teardrops in bulk
- `#adding_teardrops_to_individual_objects` — Adding teardrops to individual objects
- `#other_details_about_teardrops` — Other details about teardrops
- `#backdrills_and_hole_post_machining_counterborescountersinks` — Backdrills and hole post-machining
- `#backdrills` — Backdrills
- `#post-machining` — Post-machining holes
- `#pcb-graphical-objects` — Graphics and text
- `#graphical-shapes` — Graphical shapes
- `#arc-editing-modes` — Arc editing modes
- `#editing_shape_properties` — Editing shape properties
- `#shape-modification-tools` — Shape modification tools
- `#create-from-selection` — Converting objects to and from graphic shapes
- `#importing_vector_graphics` — Importing vector graphics
- `#text-objects` — Text objects
- `#tables` — Tables
- `#table-properties` — Editing a whole table
- `#table-cell-properties` — Editing individual table cells
- `#table-layout` — Editing table layout
- `#dimensions` — Dimensions
- `#dimension_format_options` — Dimension format options
- `#dimension_text_options` — Dimension text options
- `#dimension_line_options` — Dimension line options
- `#leader_options` — Leader options
- `#barcodes` — Barcodes
- `#points` — Points
- `#pcbnew-edit-text-and-graphics-properties` — Bulk editing text and graphics
- `#scope_and_filters` — Scope and Filters
- `#action` — Action
- `#cleaning_up_graphics` — Cleaning up graphics
- `#sheet-title-block` — Sheet title block
- `#pcb-rule-areas` — Rule areas (keepouts)
- `#locking` — Locking
- `#groups` — Groups
- `#aligning_objects` — Aligning objects
- `#distributing_objects` — Distributing objects
- `#creating-arrays` — Arrays
- `#grid_arrays` — Grid arrays
- `#circular_arrays` — Circular arrays
- `#common_array_options` — Common array options
- `#pcb-reference-images` — Using reference images
- `#pin-and-gate-swapping` — Pin and gate swapping
- `#pin_swaps` — Pin swaps
- `#gate_unit_swaps` — Gate (unit) swaps
- `#swapping_more_than_two_items` — Swapping more than two items
- `#syncing_pin_and_gate_swaps_to_the_schematic` — Syncing pin and gate swaps to the schematic

### `pcbnew-3-inspect-output.md` — PCB 에디터 ③ 검사·임포트·출력 생성
원문: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html  ·  섹션 91개

- `#forward-and-back-annotation` — Forward and back annotation
- `#forward-annotation` — Update PCB From Schematic (forward annotation)
- `#options` — Forward annotation 옵션
- `#re-linking` — Re-linking symbols and footprints
- `#re_linking_by_unique_identifier_default` — Re-linking by unique identifier (default)
- `#re_linking_by_reference_designator` — Re-linking by reference designator
- `#back-annotation` — Update Schematic from PCB (back annotation)
- `#options_2` — Back annotation 옵션
- `#back_annotation_with_cmp_files` — Back annotation with CMP files
- `#geographical-re-annotation` — Geographical re-annotation
- `#design-rule-checking` — Design rules checking (DRC)
- `#clearance-and-constraint-resolution` — Clearance and constraint resolution
- `#drc_configuration` — DRC configuration
- `#list-of-drc-checks` — List of DRC checks
- `#electrical_drc_checks` — Electrical DRC checks
- `#dfm-drc` — Design for manufacturing DRC checks
- `#schematic_parity_drc_checks` — Schematic parity DRC checks
- `#signal_integrity_drc_checks` — Signal integrity DRC checks
- `#readability_drc_checks` — Readability DRC checks
- `#miscellaneous_drc_checks` — Miscellaneous DRC checks
- `#text-var-drc` — User-definable DRC violations
- `#drc_report_file` — DRC report file
- `#board-statistics` — Board Statistics
- `#measurement-tool` — Measurement tool
- `#find_tool` — Find tool
- `#search_panel` — Search panel
- `#threed-viewer` — 3D Viewer
- `#navigating_the_3d_view` — Navigating the 3D view
- `#appearance_manager` — Appearance Manager
- `#generating_images_with_the_3d_viewer` — Generating images with the 3D Viewer
- `#3d_viewer_controls` — 3D viewer controls
- `#net-inspector` — Net inspector
- `#grouping_nets` — Grouping nets
- `#editing_nets` — Editing nets
- `#differences_between_net_inspector_and_length_tuner` — Differences between Net Inspector and Length Tuner
- `#supported_import_formats` — Supported import formats
- `#how_to_import_a_board` — How to import a board
- `#layer_mapping` — Layer mapping
- `#post_import_cleanup` — Post-import cleanup
- `#format_specific_notes` — Format-specific notes
- `#import-altium-designer` — Altium Designer
- `#import-altium-circuit-maker` — Altium Circuit Maker
- `#import-altium-circuit-studio` — Altium Circuit Studio
- `#import-cadence-allegro` — Cadence Allegro
- `#import-cadstar` — CADSTAR PCB Archive
- `#import-eagle` — Eagle (Autodesk)
- `#import-easyeda` — EasyEDA / JLCEDA Standard
- `#import-easyeda-pro` — EasyEDA / JLCEDA Professional
- `#import-fabmaster` — Fabmaster
- `#import-geda` — gEDA / Lepton EDA
- `#import-pcad` — P-CAD
- `#import-pads` — PADS
- `#import-solidworks` — Solidworks PCB
- `#specctra-session-import` — Importing Specctra session files
- `#plotting` — Plotting (Gerber / PostScript / SVG / DXF / PDF)
- `#plotting_options` — Plotting options
- `#gerber_options` — Gerber options
- `#postscript_options` — PostScript options
- `#svg_options` — SVG options
- `#dxf_options` — DXF options
- `#pdf_options` — PDF options
- `#drill-files` — Drill files
- `#ipc-2581-export` — IPC-2581
- `#odb-export` — ODB++
- `#component_placement_position_files` — Component placement (position) files
- `#footprint_reports` — Footprint reports
- `#ipc_d_356_netlists` — IPC-D-356 netlists
- `#bill_of_materials` — Bill of Materials
- `#printing` — Printing
- `#specctra_dsn` — Specctra DSN
- `#gencad` — GenCAD
- `#vrml-exporter` — VRML
- `#idf-exporter` — IDF
- `#_3d-export` — 3D models (STEP / GLB / BREP / XAO / PLY / STL / STPZ / U3D / PDF)
- `#board_options` — Board options
- `#conductor_options` — Conductor options
- `#coordinates` — Coordinates
- `#other_options` — Other options
- `#footprint_association_cmp_files` — Footprint association (CMP) files
- `#hyperlynx` — Hyperlynx
- `#selecting-a-variant-in-the-pcb-editor` — Selecting a variant in the PCB editor
- `#viewing-variant-effects` — Viewing variant effects
- `#component-visibility-and-dnp` — Component visibility and DNP
- `#three-d-viewer` — 3D viewer
- `#footprint-properties` — Footprint properties
- `#pcb-generating-variant-aware-outputs` — Generating variant-aware outputs
- `#gerber-and-fabrication-output` — Gerber and fabrication output
- `#position-files` — Position files
- `#three-d-model-export` — 3D model export (STEP/VRML)
- `#odb-and-ipc2581` — ODB++ and IPC-2581
- `#command-line-variant-support` — Command-line variant support

### `pcbnew-4-footprints.md` — PCB 에디터 ④ 풋프린트·라이브러리·멀티채널·디자인블록
원문: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html  ·  섹션 77개

- `#footprints_and_footprint_libraries` — Footprints and footprint libraries
- `#managing-footprint-libraries` — Managing footprint libraries
- `#initial_configuration` — Initial configuration
- `#managing_table_entries` — Managing table entries
- `#nested-library-tables` — Nested library tables
- `#fp-path-variable-substitution` — Path variable substitution
- `#using_the_github_plugin` — Using the GitHub plugin
- `#migrating-footprint-libraries` — Migrating footprint libraries to KiCad format
- `#browsing_footprint_libraries` — Browsing footprint libraries
- `#footprint_editor_overview` — Footprint editor overview
- `#top_toolbar` — Top toolbar
- `#left_toolbar_display_controls` — Left toolbar display controls
- `#right_toolbar_tools` — Right toolbar tools
- `#browsing_modifying_and_saving_footprints` — Browsing, modifying, and saving footprints
- `#creating_a_new_footprint_library` — Creating a new footprint library
- `#creating_a_new_footprint` — Creating a new footprint
- `#footprint-editor-properties` — Editing footprint properties
- `#fp-pads` — Footprint pads
- `#footprint-pad-properties` — Editing pad properties
- `#pad-connections` — Pad connections
- `#pad-clearance-overrides` — Pad clearance overrides
- `#pad-post-machining-and-backdrilling` — Pad post-machining and backdrilling
- `#custom-pad-shapes` — Custom pad shapes
- `#default-pad-properties` — Default pad properties
- `#renumbering-pads` — Renumbering pads
- `#pad-table` — Pad table
- `#pad-arrays` — Pad arrays
- `#fp-graphical-objects` — Footprint graphics and text
- `#bulk_editing_footprint_text_and_graphics` — Bulk editing footprint text and graphics
- `#cleaning_up_footprint_graphics` — Cleaning up footprint graphics
- `#fp-fields` — Footprint fields
- `#fp-layers` — Footprint layers
- `#private_footprint_layers` — Private footprint layers
- `#fp-clearance-overrides` — Clearance overrides
- `#clearance_override_hierarchy` — Clearance override hierarchy
- `#fp-pad-connections` — Pad connections, net ties, and jumper pads
- `#net-ties` — Net ties
- `#fp-jumper-pads` — Jumper pads
- `#fp-3d-models` — 3D models
- `#fp-embedding-files` — Embedding files
- `#fp-rule-areas` — Rule areas
- `#fp-reference-images` — Reference images
- `#footprint-wizards` — Footprint wizards
- `#checking-footprints` — Checking footprints
- `#multichannel-schematic` — Multichannel design procedure: schematic
- `#multichannel-board` — Multichannel design procedure: board
- `#multichannel-generate-rule-areas` — Generating placement rule areas
- `#multichannel-repeat-layout` — Repeating the layout
- `#multichannel-repeat-layout-dialog` — Target rule area table
- `#repeat_layout_options` — Repeat layout options
- `#multichannel-topology-matching` — Topology matching
- `#how_components_are_matched` — How components are matched
- `#tie_breaking_for_identical_components` — Tie-breaking for identical components
- `#mismatch_error_details` — Mismatch error details
- `#multichannel-routing-duplication` — Routing duplication details
- `#what_is_copied` — What is copied
- `#net_reassignment` — Net reassignment
- `#existing_target_routing` — Existing target routing
- `#layer_considerations` — Layer considerations
- `#when_routing_duplication_fails` — When routing duplication fails
- `#multichannel-other-items` — Other item duplication
- `#multichannel-step-by-step` — Step-by-step multichannel workflow
- `#multichannel-troubleshooting` — Troubleshooting multichannel layouts
- `#channels_fail_topology_matching` — Channels fail topology matching
- `#routing_does_not_appear_in_target_channels` — Routing does not appear in target channels
- `#footprint_placement_is_not_copied` — Footprint placement is not copied
- `#other_items_do_not_appear_in_target_channels` — Other items do not appear in target channels
- `#target_rule_area_shape_is_wrong` — Target rule area shape is wrong
- `#tips_for_clean_multichannel_designs` — Tips for clean multichannel designs
- `#creating-and-managing-design-blocks` — Creating and managing design blocks
- `#creating_a_new_design_block_library` — Creating a new design block library
- `#creating_a_new_design_block` — Creating a new design block
- `#updating-an-existing-design-block` — Updating an existing design block
- `#using-pcb-design-blocks` — Using design blocks in a board
- `#directly_placing_design_blocks_in_a_board` — Directly placing design blocks in a board
- `#applying_layouts_to_design_blocks_from_a_schematic` — Applying layouts to design blocks from a schematic
- `#grouped-design-blocks` — Grouped design blocks

### `pcbnew-5-advanced-rules.md` — PCB 에디터 ⑤ 고급(커스텀 DRC룰·텍스트변수·스크립팅)
원문: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html  ·  섹션 88개

- `#advanced_topics` — Advanced topics (개요)
- `#configuration-and-customization` — Configuration and Customization
- `#display_options` — Display options
- `#editing_options` — Editing options
- `#colors` — Colors
- `#action_plugins` — Action plugins
- `#origin_axes` — Origin & axes
- `#text-variables` — Text variables
- `#text-expressions` — Text expressions
- `#mathematical_and_logical_expressions` — Mathematical and logical expressions
- `#boolean_expressions` — Boolean expressions
- `#string_manipulation` — String manipulation
- `#date_and_time_formatting` — Date and time formatting
- `#version_control_expressions` — Version control expressions
- `#graphical-design-rule-editor` — Graphical design rule editor
- `#rule_tree` — Rule tree
- `#rule_editor_panel` — Rule editor panel
- `#constraint_values` — Constraint values
- `#conditions` — Conditions
- `#layer` — Layer
- `#drc-rule-editor-constraint-reference` — Constraint reference
- `#electrical` — Electrical
- `#manufacturability` — Manufacturability
- `#highspeed_design` — Highspeed design
- `#footprints` — Footprints
- `#custom` — Custom
- `#examples` — Examples
- `#minimum_clearance_for_a_high_voltage_net_class` — Minimum clearance for a high-voltage net class
- `#preferred_track_width_for_power_nets` — Preferred track width for power nets
- `#restricting_a_footprint_to_the_top_side_only` — Restricting a footprint to the top side only
- `#custom-design-rules` — Custom design rules
- `#the_custom_rules_editor` — The Custom Rules editor
- `#custom_rule_syntax` — Custom rule syntax
- `#layer_clause` — Layer Clause
- `#severity_clause` — Severity Clause
- `#condition_clauses` — Condition Clauses
- `#constraint_clauses` — Constraint Clauses
- `#object_property_and_function_reference` — Object property and function reference
- `#common_properties` — Common Properties
- `#connected_object_properties` — Connected Object Properties
- `#footprint_properties` — Footprint Properties
- `#pad_properties` — Pad Properties
- `#track_and_arc_properties` — Track and Arc Properties
- `#via_properties` — Via Properties
- `#tuning_pattern_properties` — Tuning Pattern Properties
- `#zone_and_rule_area_properties` — Zone and Rule Area Properties
- `#graphic_shape_properties` — Graphic Shape Properties
- `#text_properties` — Text Properties
- `#expression_functions` — Expression functions
- `#from-to-signal-path-matching` — From-To signal path matching
- `#how_from_to_paths_work` — How From-To paths work
- `#pad_name_format` — Pad name format
- `#using_fromto_in_custom_drc_rules` — Using fromTo() in custom DRC rules
- `#from_to_path_examples` — From-To path examples
- `#length_constrain_a_specific_signal_path` — Length-constrain a specific signal path
- `#match_lengths_across_a_ddr_data_bus` — Match lengths across a DDR data bus
- `#usb_signal_path_constraints` — USB signal path constraints
- `#pcie_lane_length_matching` — PCIe lane length matching
- `#series_termination_resistor_paths` — Series termination resistor paths
- `#clearance_between_high_speed_paths_and_other_nets` — Clearance between high-speed paths and other nets
- `#custom_design_rule_examples` — Custom design rule examples
- `#basic_examples` — Basic examples
- `#various_clearances` — Various clearances
- `#high_current_design_rules` — High-current design rules
- `#hole_sizes` — Hole sizes
- `#solder_mask_and_solder_paste` — Solder mask and solder paste
- `#dangling_vias` — Dangling vias
- `#scripting` — Scripting
- `#using_the_scripting_console` — Using the scripting console
- `#python_script_locations` — Python script locations
- `#pcbnew_api_overview` — pcbnew API overview
- `#examples_2` — Examples
- `#action_plugins_2` — Action plugins
- `#creating-footprint-wizards` — Footprint wizards
- `#idf-component-outlines` — IDF component outlines
- `#specifying_component_models_for_use_by_the_exporter` — Specifying component models for use by the exporter
- `#creating_a_component_outline_file` — Creating a component outline file
- `#guidelines_for_creating_outlines` — Guidelines for creating outlines
- `#package_naming` — Package naming
- `#comments` — Comments
- `#geometry_and_part_number_entries` — Geometry and Part Number entries
- `#pin_orientation_and_positioning` — Pin orientation and positioning
- `#tips_on_dimensions` — Tips on dimensions
- `#idf_component_outline_tools` — IDF Component Outline Tools
- `#idfcyl` — idfcyl
- `#idfrect` — idfrect
- `#dxf2idf` — dxf2idf
- `#idf2vrml` — idf2vrml

### `pcbnew-6-hotkeys.md` — PCB 에디터 ⑥ 단축키(Actions reference)
원문: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html  ·  섹션 4개

- `#pcbnew-actions-reference` — Actions reference
- `#pcb_editor` — PCB Editor
- `#3d_viewer` — 3D Viewer
- `#common` — Common

### `gerbview.md` — GerbView 거버/드릴 뷰어
원문: https://docs.kicad.org/10.0/en/gerbview/gerbview.html  ·  섹션 10개

- `#introduction_to_gerbview` — Introduction to GerbView
- `#interface` — Interface
- `#main_window` — Main window
- `#top_toolbar` — Top toolbar
- `#left_toolbar` — Left toolbar
- `#layers_manager` — Layers Manager
- `#commands_in_menu_bar` — Commands in menu bar
- `#file_menu` — File menu
- `#tools_menu` — Tools menu
- `#printing` — Printing

### `kicad-cli.md` — kicad-cli 명령행 레퍼런스
원문: https://docs.kicad.org/10.0/en/cli/cli.html  ·  섹션 48개

- `#introduction_to_the_kicad_command_line_interface` — Introduction to the KiCad Command-Line Interface
- `#fp` — Footprint commands
- `#footprint_export` — Footprint export
- `#footprint_upgrade` — Footprint upgrade
- `#jobset` — Jobset commands
- `#pcb` — PCB commands
- `#pcb_drc` — PCB DRC
- `#pcb_export_3d_pdf` — PCB export: 3D PDF
- `#pcb_export_brep_occt` — PCB export: BREP (OCCT)
- `#pcb_export_drill_file` — PCB export: drill file
- `#pcb_export_dxf` — PCB export: DXF
- `#pcb_export_gencad` — PCB export: GenCAD
- `#pcb_export_gerber` — PCB export: Gerber
- `#pcb_export_glb` — PCB export: GLB
- `#pcb_export_hpgl` — PCB export: HPGL
- `#pcb_export_ipc_2581` — PCB export: IPC-2581
- `#pcb_export_ipc_d_356` — PCB export: IPC-D-356
- `#pcb_export_odb` — PCB export: ODB++
- `#pcb_export_pdf` — PCB export: PDF
- `#pcb_export_ply` — PCB export: PLY
- `#pcb_export_position_file` — PCB export: position file
- `#pcb_export_postscript` — PCB export: PostScript
- `#pcb_export_statistics` — PCB export: statistics
- `#pcb_export_step` — PCB export: STEP
- `#pcb_export_stl` — PCB export: STL
- `#pcb_export_stepz` — PCB export: STEPZ
- `#pcb_export_u3d` — PCB export: U3D
- `#pcb_export_svg` — PCB export: SVG
- `#pcb_export_vrml` — PCB export: VRML
- `#pcb_export_xao` — PCB export: XAO
- `#pcb_import` — PCB import
- `#pcb_render` — PCB render
- `#pcb_upgrade` — PCB upgrade
- `#schematic` — Schematic commands
- `#schematic_erc` — Schematic ERC
- `#schematic_export_bill_of_materials` — Schematic export: bill of materials
- `#schematic_export_dxf` — Schematic export: DXF
- `#schematic_export_hpgl` — Schematic export: HPGL
- `#schematic_export_netlist` — Schematic export: netlist
- `#schematic_export_pdf` — Schematic export: PDF
- `#schematic_export_postscript` — Schematic export: PostScript
- `#schematic_export_bill_of_materials_legacy_bom_scripts` — Schematic export: bill of materials (legacy BOM scripts)
- `#schematic_export_svg` — Schematic export: SVG
- `#schematic_upgrade` — Schematic upgrade
- `#symbol` — Symbol commands
- `#symbol_export` — Symbol export
- `#symbol_upgrade` — Symbol upgrade
- `#version` — Version commands

> 총 인덱싱된 섹션: 544개 (9개 다이제스트 파일).
