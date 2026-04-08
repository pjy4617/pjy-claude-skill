# KiCad 9.x 회로도 S-expression 생성 가이드

> `.kicad_sch` 파일을 직접 생성할 때 참조하는 S-expression 포맷 가이드.
> KiCad 9.0 (version 20250114) 기준.

## 목차

1. [파일 헤더](#파일-헤더)
2. [라이브러리 심볼 정의](#라이브러리-심볼-정의)
3. [부품 배치](#부품-배치)
4. [와이어와 연결](#와이어와-연결)
5. [레이블과 전원 심볼](#레이블과-전원-심볼)
6. [계층 구조](#계층-구조)
7. [좌표 시스템](#좌표-시스템)

---

## 파일 헤더

```lisp
(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "고유-UUID-문자열")
  (paper "A3")         ;; A4, A3, A2 등
  (title_block
    (title "프로젝트 제목")
    (date "2026-04-07")
    (rev "0.1")
    (company "회사명")
    (comment 1 "설명 1")
    (comment 2 "설명 2")
  )
  (lib_symbols ...)
  ;; 본문: symbol, wire, label, sheet 등
  (sheet_instances
    (path "/"
      (page "1")
    )
  )
)
```

---

## 라이브러리 심볼 정의

`(lib_symbols ...)` 블록에 사용할 모든 부품의 핀 정의를 포함한다.

### 전원 심볼

```lisp
(symbol "power:+3V3"
  (power)
  (pin_numbers (hide yes))
  (pin_names (offset 0) (hide yes))
  (exclude_from_sim no)
  (in_bom yes)
  (on_board yes)
  (property "Reference" "#PWR" (at 0 -3.81 0)
    (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Value" "+3V3" (at 0 3.556 0)
    (effects (font (size 1.27 1.27))))
  (property "Footprint" "" (at 0 0 0)
    (effects (font (size 1.27 1.27)) (hide yes)))
  (property "Datasheet" "" (at 0 0 0)
    (effects (font (size 1.27 1.27)) (hide yes)))
  (symbol "+3V3_0_1"
    (polyline (pts (xy -0.762 1.27) (xy 0 2.54))
      (stroke (width 0) (type default)) (fill (type none)))
    (polyline (pts (xy 0 0) (xy 0 2.54))
      (stroke (width 0) (type default)) (fill (type none)))
    (polyline (pts (xy 0 2.54) (xy 0.762 1.27))
      (stroke (width 0) (type default)) (fill (type none)))
  )
  (symbol "+3V3_1_1"
    (pin power_in line (at 0 0 90) (length 0)
      (name "+3V3" (effects (font (size 1.27 1.27))))
      (number "1" (effects (font (size 1.27 1.27)))))
  )
)
```

GND 심볼도 동일 패턴 (`(at 0 0 270)` 방향).

### 수동 소자 (캐패시터, 저항)

```lisp
(symbol "Device:C"
  (pin_names (offset 1.016))
  (exclude_from_sim no)
  (in_bom yes)
  (on_board yes)
  (property "Reference" "C" (at 0 7.62 0) ...)
  (property "Value" "C" (at 0 -7.62 0) ...)
  (symbol "C_0_1"
    (rectangle (start -5.08 5.08) (end 5.08 -5.08)
      (stroke (width 0.254) (type default))
      (fill (type background)))
  )
  (symbol "C_1_1"
    (pin passive line (at -7.62 0 0) (length 2.54)
      (name "1" ...) (number "1" ...))
    (pin passive line (at 7.62 0 180) (length 2.54)
      (name "2" ...) (number "2" ...))
  )
)
```

### IC 심볼

IC는 데이터시트 핀 배치를 기반으로 정의한다:

```lisp
(symbol "Memory_Flash:W25Q128JVS"
  (exclude_from_sim no)
  (in_bom yes)
  (on_board yes)
  (property "Reference" "U" (at -6.35 11.43 0) ...)
  (property "Value" "W25Q128JVS" (at 7.62 11.43 0) ...)
  (property "Footprint" "Package_SON:WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4mm" ...)
  (property "Datasheet" "https://..." ...)
  (symbol "W25Q128JVS_0_1"
    (rectangle (start -7.62 10.16) (end 10.16 -10.16) ...)
  )
  (symbol "W25Q128JVS_1_1"
    (pin input line (at -10.16 7.62 0) (length 2.54)
      (name "~{CS}" ...) (number "1" ...))
    (pin input line (at -10.16 5.08 0) (length 2.54)
      (name "CLK" ...) (number "6" ...))
    ;; ... 나머지 핀
    (pin power_in line (at 0 12.7 270) (length 2.54)
      (name "VCC" ...) (number "8" ...))
    (pin power_in line (at 0 -12.7 90) (length 2.54)
      (name "GND" ...) (number "4" ...))
  )
)
```

### 핀 타입

| 타입 | 용도 |
|------|------|
| `input` | 디지털/아날로그 입력 |
| `output` | 디지털/아날로그 출력 |
| `bidirectional` | 양방향 (I2C SDA, 데이터 버스) |
| `passive` | 수동 소자 (R, C, L) |
| `power_in` | 전원 입력 (VCC, GND) |
| `power_out` | 전원 출력 (레귤레이터 출력) |
| `tri_state` | 트라이스테이트 출력 |
| `unconnected` | 미연결 핀 (NC) |
| `free` | 자유 핀 |

---

## 부품 배치

`lib_symbols`에 정의된 심볼을 회로도에 배치한다:

```lisp
(symbol
  (lib_id "Memory_Flash:W25Q128JVS")
  (at 127.0 88.9 0)          ;; x, y, 회전각(0/90/180/270)
  (unit 1)
  (exclude_from_sim no)
  (in_bom yes)
  (on_board yes)
  (dnp no)                    ;; Do Not Place 여부
  (uuid "고유-UUID")
  (property "Reference" "U_FLASH"
    (at 127.0 68.58 0)
    (effects (font (size 1.524 1.524)))
  )
  (property "Value" "W25Q128JVS"
    (at 127.0 71.12 0)
    (effects (font (size 1.524 1.524)))
  )
  (property "Footprint" "Package_SON:WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4mm"
    (at 127.0 88.9 0)
    (effects (font (size 1.27 1.27)) (hide yes))
  )
  (property "Datasheet" "https://..."
    (at 127.0 88.9 0)
    (effects (font (size 1.27 1.27)) (hide yes))
  )
  ;; 각 핀의 UUID
  (pin "1" (uuid "핀1-UUID"))
  (pin "2" (uuid "핀2-UUID"))
  ;; ...
)
```

---

## 와이어와 연결

### 와이어

두 점을 전선으로 연결한다:

```lisp
(wire
  (pts (xy 101.6 40.64) (xy 101.6 30.48))
  (stroke (width 0) (type default))
  (uuid "와이어-UUID")
)
```

### 교차점 (Junction)

와이어가 T자로 만나는 곳에 접합점 마커를 배치한다:

```lisp
(junction
  (at 101.6 40.64)
  (diameter 0)
  (color 0 0 0 0)
  (uuid "접합점-UUID")
)
```

### No Connect

미연결 핀에 NC 마커를 배치한다:

```lisp
(no_connect
  (at 139.7 88.9)
  (uuid "NC-UUID")
)
```

---

## 레이블과 전원 심볼

### 로컬 레이블

같은 시트 내에서 네트 이름을 부여한다:

```lisp
(label "SPI_CLK"
  (at 111.76 55.88 0)
  (effects
    (font (size 1.27 1.27))
    (justify left bottom)
  )
  (uuid "레이블-UUID")
)
```

### 글로벌 레이블

시트 간 공유되는 네트:

```lisp
(global_label "SPI_CLK"
  (shape input)              ;; input, output, bidirectional, passive
  (at 63.5 55.88 180)
  (effects
    (font (size 1.27 1.27))
    (justify right)
  )
  (uuid "글로벌레이블-UUID")
  (property "Intersheetref" "${INTERSHEET_REFS}"
    (at 0 0 0)
    (effects (font (size 1.27 1.27)) (hide yes))
  )
)
```

### 전원 심볼 배치

전원 심볼도 `(symbol (lib_id "power:+3V3") ...)` 형태로 배치한다:

```lisp
(symbol
  (lib_id "power:+3V3")
  (at 101.6 30.48 0)
  (unit 1)
  (exclude_from_sim no)
  (in_bom yes)
  (on_board yes)
  (dnp no)
  (uuid "전원-UUID")
  (property "Reference" "#PWR01"
    (at 101.6 26.67 0)
    (effects (font (size 1.27 1.27)) (hide yes))
  )
  (property "Value" "+3V3"
    (at 101.6 26.67 0)
    (effects (font (size 1.27 1.27)))
  )
  (pin "1" (uuid "핀-UUID"))
)
```

---

## 계층 구조

### 서브시트 참조 (루트 시트)

```lisp
(sheet
  (at 38.1 38.1)
  (size 40.64 30.48)
  (exclude_from_sim no)
  (in_bom yes)
  (on_board yes)
  (dnp no)
  (fields_autoplaced yes)
  (stroke (width 0.1524) (type solid))
  (fill (color 0 0 0 0.0000))
  (uuid "시트-UUID")
  (property "Sheetname" "전원부"
    (at 38.1 37.39 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
  )
  (property "Sheetfile" "power.kicad_sch"
    (at 38.1 69.16 0)
    (effects (font (size 1.27 1.27)) (justify left top))
  )
  ;; 시트 핀 (계층 연결)
  (pin "+3V3" input
    (at 38.1 45.72 180)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid "시트핀-UUID")
  )
  (pin "GND" input
    (at 38.1 50.8 180)
    (effects (font (size 1.27 1.27)) (justify left))
    (uuid "시트핀-UUID")
  )
  (instances
    (project ""
      (path "/루트-UUID"
        (page "2")
      )
    )
  )
)
```

### 서브시트 내부

서브시트에서는 `(hierarchical_label ...)` 로 상위 시트와 연결한다:

```lisp
(hierarchical_label "+3V3"
  (shape input)
  (at 25.4 38.1 180)
  (effects (font (size 1.27 1.27)) (justify right))
  (uuid "계층레이블-UUID")
)
```

---

## 좌표 시스템

- 단위: mm
- 원점: 좌측 상단
- X: 오른쪽 증가
- Y: 아래쪽 증가
- 그리드: 2.54mm (100mil) 기본
- 부품 간 간격: 최소 10.16mm (400mil) 권장
- 전원 심볼: 부품 위에 VCC, 아래에 GND 배치

### 배치 권장사항

- 신호 흐름: 왼쪽(입력) → 오른쪽(출력)
- 전원: 위(VCC) → 아래(GND)
- IC는 가로 중심에, 디커플링 캡은 VCC 핀 바로 옆에
- 서브시트는 기능 블록별로 분리하여 가독성 확보

---

## .kicad_pro 프로젝트 파일

KiCad에서 계층 구조 회로도를 열려면 `.kicad_pro` 프로젝트 파일이 필요하다.
JSON 형식이며, 최소한 아래 구조를 갖추면 된다.

### 기본 템플릿

```json
{
  "meta": {
    "filename": "프로젝트명.kicad_pro",
    "version": 2
  },
  "schematic": {
    "drawing": {
      "default_line_thickness": 6.0,
      "default_text_size": 50.0,
      "intersheets_ref_prefix": "",
      "intersheets_ref_short": false,
      "intersheets_ref_show": true,
      "intersheets_ref_suffix": ""
    },
    "meta": {
      "version": 1
    }
  },
  "text_variables": {
    "COMMENT1": "설명",
    "COMPANY": "회사명",
    "REVISION": "0.1"
  }
}
```

### 넷클래스 추가 (차동 페어 등)

```json
{
  "net_settings": {
    "classes": [
      {
        "name": "Default",
        "clearance": 0.2,
        "track_width": 0.2,
        "via_diameter": 0.6,
        "via_drill": 0.3
      },
      {
        "name": "Power",
        "clearance": 0.25,
        "track_width": 0.4
      },
      {
        "name": "Diff_100R",
        "clearance": 0.15,
        "track_width": 0.1,
        "diff_pair_width": 0.1,
        "diff_pair_gap": 0.15
      }
    ]
  }
}
```

### 생성 규칙

- 파일명은 루트 `.kicad_sch`와 동일한 이름 (확장자만 `.kicad_pro`)
- `meta.version`은 `2` (KiCad 9.x)
- 넷클래스는 설계에 맞게 추가 (전원, 차동 페어 등)
- `text_variables`에 프로젝트 정보를 넣으면 타이틀 블록에서 `${COMPANY}` 등으로 참조 가능

---

## 생성 시 주의사항

- 모든 요소에 고유 UUID를 부여해야 한다 (`uuid.uuid4()` 사용)
- 핀 연결은 와이어의 좌표가 핀의 절대 좌표와 정확히 일치해야 한다
- `lib_symbols`에 정의되지 않은 `lib_id`를 참조하면 KiCad에서 열리지 않는다
- 전원 심볼(`power:`)은 `(power)` 플래그가 필수
- 수동 소자의 Reference 접두사: C(캡), R(저항), L(인덕터), D(다이오드)
- `(in_bom no)` 설정 시 BOM에서 제외됨
- 파일 인코딩은 UTF-8
