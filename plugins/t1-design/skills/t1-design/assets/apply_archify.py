#!/usr/bin/env python3
"""archify 결과 HTML 에 T1 테마를 입힌다. 원본은 두고 새 파일로 쓴다.

넣는 것: Google Fonts 링크 + archify-t1.css(<style id="t1-archify-theme">) 를 </head> 앞에,
T1 로고(base64) 를 제목 옆 pulse-dot 뒤에. 이미 들어 있으면 다시 넣지 않는다.

사용: python3 apply_archify.py <archify.html> [-o 출력.html]   (기본 출력: <이름>.t1.html)
      python3 apply_archify.py --selftest
"""
import argparse, base64, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARK = '<style id="t1-archify-theme">'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700'
         '&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap">\n')
DOT = '<div class="pulse-dot"></div>'


def apply(html: str, css: str, logo_b64: str) -> str:
    if MARK in html:
        return html
    if html.count('</head>') != 1:
        sys.exit('archify HTML 이 아니다: </head> 가 정확히 1개여야 한다')
    html = html.replace('</head>', f'{FONTS}{MARK}\n{css}</style>\n</head>', 1)
    # 로고 자리가 없으면(헤더 구조가 바뀐 archify 버전) 색만 입히고 로고는 건너뛴다
    return html.replace(DOT, f'{DOT}\n<img class="t1-logo" alt="T1" src="data:image/jpeg;base64,{logo_b64}">', 1)


def selftest():
    src = '<html><head><style>a{}</style></head><body><div class="pulse-dot"></div><h1>x</h1></body></html>'
    once = apply(src, 'X{}\n', 'AA==')
    assert once.count(MARK) == 1 and 'Outfit' in once and 'class="t1-logo"' in once
    assert once.index(MARK) < once.index('</head>') < once.index('t1-logo"')
    assert apply(once, 'X{}\n', 'AA==') == once  # 두 번 돌려도 같다
    print('selftest OK')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('html', nargs='?')
    p.add_argument('-o', '--out')
    p.add_argument('--selftest', action='store_true')
    a = p.parse_args()
    if a.selftest:
        return selftest()
    if not a.html:
        p.error('archify HTML 경로가 필요하다')
    src = Path(a.html)
    out = Path(a.out) if a.out else src.with_suffix('.t1.html')
    css = (HERE / 'archify-t1.css').read_text(encoding='utf-8')
    logo = base64.b64encode((HERE / 't1_logo.jpg').read_bytes()).decode()
    out.write_text(apply(src.read_text(encoding='utf-8'), css, logo), encoding='utf-8')
    print(f'작성: {out}')


if __name__ == '__main__':
    main()
