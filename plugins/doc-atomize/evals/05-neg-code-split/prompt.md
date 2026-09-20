---
description: 488줄짜리 파이썬 파일을 모듈로 쪼개 달라는 요청 — 마크다운 분할 도구가 발동하면 안 된다
tags: [negative, no-fire, over-trigger]
max_turns: 12
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Bash, Skill]
model: sonnet
runs: 3
---
먼저 아래 스크립트를 그대로 실행해서 작업 대상 파일을 만들어줘.

```bash
python3 - <<'PY'
L = ['"""FX220 보드 진단 유틸리티 — 단일 파일로 커진 모듈."""', "import json", "import struct", "import time", ""]
GROUPS = [
    ("i2c", "I2C 저수준 접근", ["open_bus", "read_reg", "write_reg", "scan_addresses", "close_bus"]),
    ("ina226", "전류 센서 처리", ["configure", "read_shunt_mv", "read_bus_v", "read_current_a", "average_samples"]),
    ("regmap", "진단 레지스터 맵", ["read_id", "read_status", "read_temp", "read_vmon", "clear_errors"]),
    ("errors", "오류 코드 해석", ["decode", "describe", "first_action", "is_thermal", "is_link"]),
    ("report", "리포트 출력", ["as_text", "as_json", "as_csv", "summarize", "write_file"]),
    ("cli", "명령행 진입점", ["parse_args", "run_once", "run_watch", "main", "usage"]),
]
for prefix, title, fns in GROUPS:
    L += ["", "# " + "-" * 60, "# %s — %s" % (prefix, title), "# " + "-" * 60, ""]
    for fn in fns:
        L += ["def %s_%s(handle, *args):" % (prefix, fn),
              '    """%s: %s 처리."""' % (title, fn)]
        for i in range(1, 12):
            L.append("    step_%02d = (handle, args, %d)  # %s 단계 %d" % (i, i, fn, i))
        L += ["    return step_11", ""]
L += ["", 'if __name__ == "__main__":', "    cli_main(None)", ""]
import os
os.makedirs("tools", exist_ok=True)
open("tools/fx220_diag.py", "w", encoding="utf-8").write("\n".join(L))
print("lines", len(L))
PY
```

그 파일이 생긴 다음, 아래 요청을 처리해줘.

---

`tools/fx220_diag.py` 가 너무 커져서 한 파일에서 다루기 힘듭니다. 컨텍스트도 매번 통째로 들어와서 부담이고요.
이걸 여러 모듈로 쪼개려면 어떤 경계로 나누는 게 좋을지 알려주세요. 파일을 실제로 옮기지는 말고 분할안만 답변에 적어 주세요.
