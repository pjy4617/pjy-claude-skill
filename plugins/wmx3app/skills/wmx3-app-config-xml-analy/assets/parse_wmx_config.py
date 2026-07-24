#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WMX3 Config Export(파라미터 export XML) 파서 / 요약 도구.

WMX3 엔진의 파라미터 설정 전체를 내보낸 XML(예: WMX3Agent/WOS의 파라미터 Export)을
읽어, 128개 축 중 실제로 설정된(공장 디폴트에서 벗어난) 축만 골라 핵심 파라미터를
요약하고, 명백한 설정 위험을 자동 플래그한다.

핵심 아이디어: 대부분의 축은 손대지 않은 공장 디폴트이므로, 각 필드의 128축 값 중
'최빈값(mode)'을 baseline(디폴트)으로 보고, baseline과 다른 필드가 하나라도 있는 축을
'설정 축(active axis)'으로 판정한다. 이 방식은 특정 필드명에 하드코딩 의존하지 않아
파라미터 스키마가 조금 달라져도 견고하게 동작한다.

사용법:
    python3 parse_wmx_config.py <config_export.xml>                   # 텍스트 리포트
    python3 parse_wmx_config.py <config_export.xml> --format json     # 기계 판독용 JSON
    python3 parse_wmx_config.py <config_export.xml> --format csv      # 축별 CSV(표준출력)
    python3 parse_wmx_config.py <config_export.xml> --format csv --out axes.csv   # CSV 파일 저장

CSV 는 한 축 = 한 행이며 is_active/changed_count/flags 컬럼으로 스프레드시트에서
필터·정렬하거나 장비 간·버전 간 파라미터를 비교하기에 좋다.
"""
import argparse
import csv
import json
import sys
from collections import Counter

try:
    import xml.etree.ElementTree as ET
except ImportError:  # pragma: no cover - 표준 라이브러리라 사실상 발생 안 함
    print("ERROR: xml.etree.ElementTree 를 사용할 수 없습니다.", file=sys.stderr)
    sys.exit(2)

# 축 요약 표에 항상 노출할 핵심 필드 (그룹/필드) — 존재하지 않으면 자동 생략
CORE_FIELDS = [
    ("AxisParam", "AxisCommandMode"),
    ("AxisParam", "AxisGearRatioNumerator"),
    ("AxisParam", "AxisGearRatioDenominator"),
    ("AxisParam", "AxisUnit"),
    ("AxisParam", "SingleTurnMode"),
    ("AxisParam", "SingleTurnEncoderCount"),
    ("AxisParam", "MaxTrqLimit"),
    ("AxisParam", "PositiveTrqLimit"),
    ("AxisParam", "NegativeTrqLimit"),
    ("AxisParam", "AxisPolarity"),
    ("AxisParam", "MaxMotorSpeed"),
    ("AxisParam", "AbsoluteEncoderMode"),
    ("AxisParam", "AbsoluteEncoderHomeOffset"),
    ("MotionParam", "ProhibitOvertravel"),
    ("MotionParam", "QuickStopDec"),
    ("LimitParam", "SoftLimitType"),
    ("LimitParam", "SoftLimitPositivePos"),
    ("LimitParam", "SoftLimitNegativePos"),
    ("HomeParam", "HomeType"),
    ("HomeParam", "HomeDir"),
    ("AlarmParam", "FollowingErrorStopped"),
    ("AlarmParam", "FollowingErrorMoving"),
]

# GlobalParameters 요약에 노출할 필드
GLOBAL_FIELDS = [
    ("FlightRecorderParam", "EnableFlightRecorder"),
    ("FlightRecorderParam", "TriggerFlightRecorderOnAmpAlarm"),
    ("EmergencyStopParam", "EnableEStopSignal"),
    ("EmergencyStopParam", "EnableEStopStatusSignal"),
    ("EmergencyStopParam", "EStopLevel1Type"),
    ("GlobalParam", "InterpolationDataSize"),
]


def _to_float(text):
    """문자열을 float 로 변환. 실패 시 None."""
    if text is None:
        return None
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def load_axes(root):
    """AxisParameters 요소 목록을 (축번호, element) 로 반환. 축 번호 오름차순."""
    axes = []
    for ax in root.findall("AxisParameters"):
        num = ax.attrib.get("Axis")
        try:
            key = int(num)
        except (ValueError, TypeError):
            key = 1 << 30  # 번호 없는 축은 뒤로
        axes.append((key, num, ax))
    axes.sort(key=lambda t: t[0])
    return [(num, el) for _, num, el in axes]


def axis_fields(ax_el):
    """축 element 를 {'Group/Field': text} 평탄화 딕셔너리로."""
    out = {}
    for group in ax_el:
        for field in group:
            out[f"{group.tag}/{field.tag}"] = field.text
    return out


def compute_baseline(all_axis_maps):
    """각 필드의 최빈값을 디폴트(baseline)로 계산."""
    counters = {}
    for m in all_axis_maps:
        for k, v in m.items():
            counters.setdefault(k, Counter())[v] += 1
    return {k: c.most_common(1)[0][0] for k, c in counters.items()}


def diff_from_baseline(ax_map, baseline):
    """축 맵에서 baseline 과 다른 필드만 {key: (value, baseline_value)}."""
    changed = {}
    for k, v in ax_map.items():
        base = baseline.get(k)
        if v != base:
            changed[k] = (v, base)
    return changed


def sanity_flags(axis_num, ax_map):
    """설정 축 대상 명백한 위험만 플래그. (severity, code, message) 리스트.

    자동 플래그는 '후보'이며 최종 판정은 사람/체크리스트가 한다 —
    오탐을 줄이기 위해 명백한 것만 검사한다.
    """
    flags = []

    def val(key):
        return ax_map.get(key)

    def fval(key):
        return _to_float(ax_map.get(key))

    # CRITICAL: 기어비 분모 0 → 사용자 단위 환산에서 0 나눗셈 위험
    den = fval("AxisParam/AxisGearRatioDenominator")
    if den is not None and den == 0:
        flags.append(("CRITICAL", "GEAR_DEN_ZERO",
                      "AxisGearRatioDenominator=0 — 기어비 분모 0(사용자 단위 환산 0 나눗셈 위험)"))

    # CRITICAL: 단회전 엔코더 카운트 0
    stc = fval("AxisParam/SingleTurnEncoderCount")
    if stc is not None and stc == 0:
        flags.append(("CRITICAL", "SINGLE_TURN_ZERO",
                      "SingleTurnEncoderCount=0 — 단회전 엔코더 분해능 0"))

    # MAJOR: 오버트래블 금지 해제 (설정 축인데 리미트 보호 off)
    pot = val("MotionParam/ProhibitOvertravel")
    if pot is not None and pot == "0":
        flags.append(("MAJOR", "OVERTRAVEL_OFF",
                      "ProhibitOvertravel=0 — 오버트래블(리미트 초과) 금지가 해제됨"))

    # MINOR: 팔로잉 에러 감시 완전 비활성 (정지/이동 임계 모두 0)
    fes = fval("AlarmParam/FollowingErrorStopped")
    fem = fval("AlarmParam/FollowingErrorMoving")
    if fes is not None and fem is not None and fes == 0 and fem == 0:
        flags.append(("MINOR", "FOLLOWING_ERR_OFF",
                      "FollowingError 임계(정지/이동) 모두 0 — 위치 팔로잉 에러 감시 없음"))

    # INFO: 소프트리밋 비활성 (타입 0 + 양/음 위치 모두 0)
    slt = val("LimitParam/SoftLimitType")
    slp = fval("LimitParam/SoftLimitPositivePos")
    sln = fval("LimitParam/SoftLimitNegativePos")
    if slt == "0" and (slp in (0, None)) and (sln in (0, None)):
        flags.append(("INFO", "SOFTLIMIT_OFF",
                      "SoftLimit 비활성(Type=0, 양/음 위치 0) — 소프트웨어 위치 제한 없음"))

    # INFO: 절대 엔코더 사용 (원점복귀 불필요 가능성)
    abs_enc = val("AxisParam/AbsoluteEncoderMode")
    if abs_enc is not None and abs_enc != "0":
        flags.append(("INFO", "ABSOLUTE_ENCODER",
                      f"AbsoluteEncoderMode={abs_enc} — 절대 엔코더(원점복귀 절차 재검토)"))

    return [(sev, code, msg, axis_num) for sev, code, msg in flags]


def build_report(xml_path):
    """XML 을 파싱해 리포트용 구조체(dict)를 만든다."""
    try:
        tree = ET.parse(xml_path)
    except FileNotFoundError:
        raise SystemExit(f"ERROR: 파일을 찾을 수 없습니다: {xml_path}")
    except ET.ParseError as e:
        raise SystemExit(f"ERROR: XML 파싱 실패: {e}")

    root = tree.getroot()
    if root.tag != "Parameters":
        raise SystemExit(
            f"ERROR: 루트 태그가 <Parameters> 가 아닙니다 (실제: <{root.tag}>). "
            "WMX3 Config Export(파라미터 export XML)가 맞는지 확인하세요.")

    ver = root.attrib.get("ver", "?")

    # GlobalParameters
    global_el = root.find("GlobalParameters")
    global_map = axis_fields(global_el) if global_el is not None else {}
    global_summary = {}
    for grp, fld in GLOBAL_FIELDS:
        key = f"{grp}/{fld}"
        if key in global_map:
            global_summary[key] = global_map[key]

    # AxisParameters
    axes = load_axes(root)
    axis_maps = [axis_fields(el) for _, el in axes]
    baseline = compute_baseline(axis_maps) if axis_maps else {}

    active = []       # 디폴트에서 벗어난 축(상세)
    axes_table = []   # 전체 축 요약(CSV/JSON 테이블용 — 한 축 = 한 행)
    all_flags = []
    for (num, _el), amap in zip(axes, axis_maps):
        changed = diff_from_baseline(amap, baseline)
        core = {}
        for grp, fld in CORE_FIELDS:
            key = f"{grp}/{fld}"
            if key in amap:
                core[key] = amap[key]
        is_active = bool(changed)
        axis_flags = []
        if is_active:
            axis_flags = sanity_flags(num, amap)
            all_flags.extend(axis_flags)
            active.append({
                "axis": num,
                "core": core,
                "changed": {k: {"value": v, "baseline": b}
                            for k, (v, b) in sorted(changed.items())},
            })
        axes_table.append({
            "axis": num,
            "is_active": is_active,
            "changed_count": len(changed),
            "changed_fields": {k: {"value": v, "baseline": b}
                               for k, (v, b) in sorted(changed.items())},
            "core": core,
            # (severity, code, message) — sanity_flags 는 축 번호를 4번째로 붙여 반환
            "flags": [(s, c, m) for s, c, m, _ in axis_flags],
        })

    return {
        "version": ver,
        "axis_count": len(axes),
        "active_axis_count": len(active),
        "active_axes": active,
        "axes_table": axes_table,
        "global": global_summary,
        "flags": all_flags,
        "baseline_note": "baseline = 각 필드의 128축 최빈값(공장 디폴트 추정)",
    }


SEV_ORDER = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2, "INFO": 3}
SEV_ICON = {"CRITICAL": "🔴", "MAJOR": "🟠", "MINOR": "🟡", "INFO": "🔵"}


def print_text(rep, fh=sys.stdout):
    def p(*a):
        print(*a, file=fh)

    p("== WMX3 Config Export 분석 ==\n")
    p(f"파라미터 버전: {rep['version']}")
    p(f"총 축: {rep['axis_count']}개  |  설정(비디폴트) 축: {rep['active_axis_count']}개")
    p(f"({rep['baseline_note']})\n")

    # GlobalParameters
    p("[GlobalParameters]")
    if rep["global"]:
        for k, v in rep["global"].items():
            p(f"  {k} = {v}")
    else:
        p("  (요약 대상 필드 없음)")
    p()

    # 설정 축
    p("[설정된 축 상세]")
    if not rep["active_axes"]:
        p("  설정된(디폴트에서 벗어난) 축이 없습니다 — 전 축 공장 디폴트로 보입니다.\n")
    for a in rep["active_axes"]:
        p(f"\n  ● Axis {a['axis']}")
        # 핵심 파라미터
        core = a["core"]
        if core:
            p("    핵심 파라미터:")
            for k, v in core.items():
                p(f"      {k} = {v}")
        # 디폴트에서 벗어난 필드
        p("    디폴트에서 변경된 필드:")
        for k, d in a["changed"].items():
            p(f"      {k}: {d['value']}  (디폴트 {d['baseline']})")

    # 자동 검토 플래그
    p("\n[자동 검토 플래그] (후보 — 최종 판정은 체크리스트/사람)")
    flags = sorted(rep["flags"], key=lambda f: (SEV_ORDER.get(f[0], 9), str(f[3])))
    if not flags:
        p("  명백한 위험 플래그 없음.")
    else:
        for sev, code, msg, axis_num in flags:
            p(f"  {SEV_ICON.get(sev,'')} [{sev}] Axis {axis_num}: {msg}")

    # 요약 카운트
    cnt = Counter(f[0] for f in rep["flags"])
    p("\n== 플래그 요약 ==")
    for sev in ("CRITICAL", "MAJOR", "MINOR", "INFO"):
        p(f"  {sev}: {cnt.get(sev, 0)}건")


# CSV 컬럼: 고정 메타 + 핵심 파라미터(필드명만). 한 축 = 한 행.
CSV_META_COLS = ["axis", "is_active", "changed_count", "flags", "changed_fields"]
CSV_CORE_COLS = [fld for _grp, fld in CORE_FIELDS]


def write_csv(rep, fh):
    """전체 축 요약을 CSV 로 출력. 스프레드시트 필터/정렬·장비 간 비교용.

    - is_active: 디폴트에서 벗어난 축이면 1 (스프레드시트에서 =1 필터 → 설정 축만)
    - changed_count: 디폴트와 다른 필드 개수
    - flags: 'SEV:CODE' 를 '|' 로 이어붙임 (예: 'MINOR:FOLLOWING_ERR_OFF')
    - changed_fields: '필드=값' 을 ';' 로 이어붙임 (디폴트와 다른 필드만)
    """
    writer = csv.writer(fh)
    writer.writerow(CSV_META_COLS + CSV_CORE_COLS)
    for a in rep["axes_table"]:
        flags = "|".join(f"{s}:{c}" for s, c, _m in a["flags"])
        changed = ";".join(f"{k}={d['value']}" for k, d in a["changed_fields"].items())
        row = [
            a["axis"],
            1 if a["is_active"] else 0,
            a["changed_count"],
            flags,
            changed,
        ]
        for grp, fld in CORE_FIELDS:
            row.append(a["core"].get(f"{grp}/{fld}", ""))
        writer.writerow(row)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="WMX3 Config Export(파라미터 export XML) 파서/요약 도구")
    ap.add_argument("xml_path", help="WMX3 파라미터 export XML 경로")
    ap.add_argument("--format", choices=["text", "json", "csv"], default="text",
                    help="출력 형식 (기본 text). csv 는 한 축=한 행")
    ap.add_argument("--json", action="store_true",
                    help="(구버전 호환) --format json 과 동일")
    ap.add_argument("--out", metavar="PATH",
                    help="출력 파일 경로 (생략 시 표준출력)")
    args = ap.parse_args(argv)

    fmt = "json" if args.json else args.format
    rep = build_report(args.xml_path)

    # CSV 는 open 시 newline='' 로 열어야 줄바꿈이 중복되지 않는다
    if args.out:
        fh = open(args.out, "w", encoding="utf-8", newline="" if fmt == "csv" else None)
    else:
        fh = sys.stdout
    try:
        if fmt == "json":
            fh.write(json.dumps(rep, ensure_ascii=False, indent=2) + "\n")
        elif fmt == "csv":
            write_csv(rep, fh)
        else:
            print_text(rep, fh)
    finally:
        if args.out:
            fh.close()

    if args.out:
        print(f"[저장] {fmt} → {args.out}  "
              f"(총 {rep['axis_count']}축 / 설정 {rep['active_axis_count']}축, "
              f"플래그 {len(rep['flags'])}건)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
