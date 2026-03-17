#!/usr/bin/env python3
"""
KiCad Netlist XML → Vivado XDC 변환 스크립트

Usage:
    python3 gen_xdc_from_netlist.py \
        --netlist build/netlist.xml \
        --board zedboard \
        --boards-json .claude/skills/vivado-project/boards.json \
        --patterns .claude/skills/kicad-xdc/net_patterns.json \
        --fpga-ref U1 \
        --output constraints/zedboard.xdc

이 스크립트는 kicad-xdc-gen 에이전트가 호출합니다.
"""

import xml.etree.ElementTree as ET
import json
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from fnmatch import fnmatch


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def find_fpga_component(root, fpga_ref=None):
    """넷리스트에서 FPGA 컴포넌트를 찾는다."""
    components = root.findall('.//comp')

    if fpga_ref:
        for comp in components:
            if comp.get('ref') == fpga_ref:
                return comp
        print(f"ERROR: Component {fpga_ref} not found in netlist", file=sys.stderr)
        sys.exit(1)

    # 자동 탐지: Xilinx 파트넘버 패턴
    xilinx_patterns = ['xc7z', 'xc7a', 'xc7k', 'xc7v', 'xc7s',
                       'xczu', 'xcku', 'xcvu', 'xc6s', 'xc6v']
    for comp in components:
        value = (comp.findtext('value') or '').lower()
        for pat in xilinx_patterns:
            if pat in value:
                print(f"INFO: Auto-detected FPGA: {comp.get('ref')} ({comp.findtext('value')})")
                return comp

    # 핀 수 기반 탐지 (100+ 핀)
    for comp in components:
        pins = comp.findall('.//pin')
        if len(pins) >= 100:
            print(f"INFO: Detected large component as FPGA candidate: {comp.get('ref')} ({len(pins)} pins)")
            return comp

    print("ERROR: No FPGA component found. Use --fpga-ref to specify.", file=sys.stderr)
    sys.exit(1)


def extract_pin_net_map(fpga_comp):
    """FPGA 컴포넌트에서 핀→네트 매핑을 추출한다."""
    pin_map = []
    # KiCad XML 넷리스트 구조에 따라 파싱
    # 방법 1: comp 내부의 pin 태그 (단순 구조)
    for pin in fpga_comp.findall('.//pin'):
        pin_num = pin.get('num', '')
        pin_name = pin.get('name', '')
        net_name = pin.get('net', '') or pin.findtext('net', '')
        if pin_num and net_name:
            pin_map.append({
                'pin_num': pin_num,
                'pin_name': pin_name,
                'net_name': net_name
            })
    return pin_map


def extract_pin_net_from_nets(root, fpga_ref):
    """넷 섹션에서 FPGA 핀→네트 매핑을 추출한다 (KiCad XML 넷리스트 방식)."""
    pin_map = []
    nets = root.findall('.//net')
    for net in nets:
        net_name = net.get('name', '')
        net_code = net.get('code', '')
        for node in net.findall('node'):
            if node.get('ref') == fpga_ref:
                pin_num = node.get('pin', '')
                pin_name = node.get('pinfunction', '') or node.get('pintype', '')
                if pin_num and net_name:
                    pin_map.append({
                        'pin_num': pin_num,
                        'pin_name': pin_name,
                        'net_name': net_name
                    })
    return pin_map


def extract_bank_from_pin_name(pin_name):
    """Xilinx 핀 이름에서 뱅크 번호 추출. 예: IO_L12P_T1_MRCC_33 → 33"""
    if not pin_name:
        return None
    match = re.search(r'_(\d+)$', pin_name)
    if match:
        return match.group(1)
    return None


def classify_net(net_name, patterns):
    """네트 이름을 패턴에 따라 분류한다."""
    net_upper = net_name.upper()
    for category, info in patterns.items():
        for pattern in info['patterns']:
            if fnmatch(net_upper, pattern.upper()):
                return category, info
    return 'general', {'xdc_action': 'none', 'group_label': 'General I/O'}


def net_to_port_name(net_name):
    """네트 이름을 Verilog 포트 이름으로 변환한다."""
    name = net_name.lower()
    name = re.sub(r'[-\s]+', '_', name)
    name = re.sub(r'[^a-z0-9_]', '', name)
    if name and name[0].isdigit():
        name = 'pin_' + name
    verilog_keywords = {'input', 'output', 'inout', 'wire', 'reg', 'module', 'always'}
    if name in verilog_keywords:
        name = name + '_io'
    return name


def get_iostandard(bank, board_info):
    """뱅크 번호에서 IOSTANDARD를 결정한다."""
    bank_vcco = board_info.get('bank_vcco', {})
    if bank and bank in bank_vcco:
        return bank_vcco[bank]['iostandard']
    return None


def generate_xdc(pin_map, board_info, patterns, board_name, fpga_ref, fpga_value, sch_file):
    """XDC 파일 내용을 생성한다."""
    lines = []
    clock_freq = board_info.get('clock_freq_mhz', 100)
    clock_period = 1000.0 / clock_freq

    # 헤더
    lines.append(f"## ============================================================")
    lines.append(f"## Auto-generated XDC from KiCad schematic")
    lines.append(f"## Board: {board_info.get('notes', board_name)} ({board_info['part']})")
    lines.append(f"## Source: {sch_file}")
    lines.append(f"## FPGA: {fpga_ref} ({fpga_value})")
    lines.append(f"## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"## ============================================================")
    lines.append(f"## WARNING: 자동 생성 파일. pin-reviewer로 검증 필요.")
    lines.append(f"## ============================================================")
    lines.append("")

    # 카테고리별 그룹화
    categorized = {}
    excluded = []
    todo_pins = []

    for pin in pin_map:
        category, cat_info = classify_net(pin['net_name'], patterns)
        action = cat_info.get('xdc_action', 'none')

        if action == 'exclude':
            excluded.append(pin)
            continue

        bank = extract_bank_from_pin_name(pin['pin_name'])
        iostandard = get_iostandard(bank, board_info)
        port_name = net_to_port_name(pin['net_name'])

        pin['bank'] = bank
        pin['iostandard'] = iostandard
        pin['port_name'] = port_name
        pin['category'] = category
        pin['cat_info'] = cat_info

        if iostandard is None:
            todo_pins.append(pin)

        group = cat_info.get('group_label', category.title())
        if group not in categorized:
            categorized[group] = []
        categorized[group].append(pin)

    # 클럭 먼저
    clock_key = None
    for group_name, pins in categorized.items():
        if any(p['category'] == 'clock' for p in pins):
            clock_key = group_name
            break

    def write_group(group_name, pins):
        lines.append(f"## ---- {group_name} ----")
        for pin in pins:
            ios = pin['iostandard'] or 'LVCMOS33  ## TODO: IOSTANDARD 확인 필요'
            bank_comment = f"  ## Bank {pin['bank']}" if pin['bank'] else "  ## Bank 불명"
            lines.append(
                f"set_property -dict {{ PACKAGE_PIN {pin['pin_num']:<5} "
                f"IOSTANDARD {ios:<10} }} "
                f"[get_ports {pin['port_name']}]{bank_comment}"
            )

            # 클럭이면 create_clock 추가
            if pin['category'] == 'clock':
                lines.append(
                    f"create_clock -period {clock_period:.3f} "
                    f"-name {pin['port_name']}_clk [get_ports {pin['port_name']}]"
                )

        # 리셋/버튼이면 그룹 false_path
        categories_in_group = set(p['category'] for p in pins)
        if categories_in_group & {'reset', 'button'}:
            port_names = [p['port_name'] for p in pins]
            for pn in port_names:
                lines.append(f"set_false_path -from [get_ports {pn}]")

        lines.append("")

    # 클럭 그룹 먼저 출력
    if clock_key and clock_key in categorized:
        write_group(clock_key, categorized[clock_key])

    # 나머지 그룹 출력 (클럭 제외)
    for group_name in sorted(categorized.keys()):
        if group_name == clock_key:
            continue
        write_group(group_name, categorized[group_name])

    # 제외된 핀 목록 (주석)
    if excluded:
        lines.append("## ---- Excluded (Power/GND/Config/NC) ----")
        for pin in excluded[:10]:
            lines.append(f"## {pin['pin_num']:<5} {pin['net_name']}")
        if len(excluded) > 10:
            lines.append(f"## ... and {len(excluded) - 10} more")
        lines.append("")

    # TODO 핀 (IOSTANDARD 불명)
    if todo_pins:
        lines.append("## ============================================================")
        lines.append(f"## TODO: {len(todo_pins)}개 핀의 IOSTANDARD 확인 필요")
        lines.append("## boards.json의 bank_vcco에 해당 뱅크 정보를 추가하거나,")
        lines.append("## 패키지 핀아웃 파일에서 뱅크를 확인해주세요.")
        lines.append("## ============================================================")

    # 통계
    total = len(pin_map) - len(excluded)
    lines.append("")
    lines.append(f"## ---- Summary ----")
    lines.append(f"## Total pins in XDC: {total}")
    lines.append(f"## Excluded (power/GND/config): {len(excluded)}")
    lines.append(f"## TODO (IOSTANDARD 불명): {len(todo_pins)}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='KiCad Netlist → Vivado XDC')
    parser.add_argument('--netlist', required=True, help='KiCad netlist XML file')
    parser.add_argument('--board', required=True, help='Board name (key in boards.json)')
    parser.add_argument('--boards-json', required=True, help='Path to boards.json')
    parser.add_argument('--patterns', required=True, help='Path to net_patterns.json')
    parser.add_argument('--fpga-ref', default=None, help='FPGA reference designator (e.g., U1)')
    parser.add_argument('--output', required=True, help='Output XDC file path')
    parser.add_argument('--sch-file', default='project.kicad_sch', help='Source schematic filename')
    args = parser.parse_args()

    # 입력 파일 로드
    boards = load_json(args.boards_json)
    patterns = load_json(args.patterns)

    if args.board not in boards['boards']:
        print(f"ERROR: Board '{args.board}' not found in boards.json", file=sys.stderr)
        print(f"Available: {', '.join(boards['boards'].keys())}", file=sys.stderr)
        sys.exit(1)

    board_info = boards['boards'][args.board]

    # 넷리스트 파싱
    tree = ET.parse(args.netlist)
    root = tree.getroot()

    # FPGA 컴포넌트 찾기
    fpga_ref = args.fpga_ref
    fpga_comp = find_fpga_component(root, fpga_ref)
    if fpga_comp is not None:
        fpga_ref = fpga_comp.get('ref')
        fpga_value = fpga_comp.findtext('value', 'unknown')
    else:
        fpga_value = 'unknown'

    # 핀-네트 매핑 추출
    # KiCad XML 넷리스트는 핀 정보를 <nets> 섹션에 저장 (우선 시도)
    pin_map = extract_pin_net_from_nets(root, fpga_ref)
    if not pin_map:
        # fallback: comp 내부 pin 태그 (일부 버전/포맷)
        pin_map = extract_pin_net_map(fpga_comp)

    if not pin_map:
        print(f"ERROR: No pin-net mappings found for {fpga_ref}", file=sys.stderr)
        sys.exit(1)

    print(f"INFO: Found {len(pin_map)} pin-net mappings for {fpga_ref}")

    # XDC 생성
    xdc_content = generate_xdc(
        pin_map, board_info, patterns,
        args.board, fpga_ref, fpga_value, args.sch_file
    )

    # 출력
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(xdc_content)

    print(f"OK: XDC generated → {args.output}")
    print(f"    Next: pin-reviewer로 검증해주세요.")


if __name__ == '__main__':
    main()
