---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Skill, Agent]
model: sonnet
runs: 2
---
먼저 아래 스크립트를 그대로 실행해서 작업용 가짜 부품 도면 PDF 와 가짜 STEP 파일을 만들어줘.

```bash
python3 - <<'PY'
import fitz, os
os.makedirs("parts", exist_ok=True)
doc = fitz.open(); p = doc.new_page()
p.insert_text((60,80), "ACME TB-5.08-XXP pluggable terminal block", fontsize=16)
p.insert_text((60,110), "Customer drawing T0  2026-01-05", fontsize=10)
for i,l in enumerate(["Pitch 5.08 mm, N = 02..12", "Hole dia 1.30 mm, pin 1.0 x 0.5 mm, L 3.5 mm",
                       "Row spacing 7.62 mm", "Rated 300 V / 10 A, wire 0.2-1.5 mm2",
                       "Length = 5.08 x N + 2.54", "Depth 14.1 mm, height 13.4 mm"]):
    p.insert_text((60,150+i*18), l, fontsize=10)
doc.save("parts/TB-5.08-XXP-T0.pdf")
open("parts/TB-5.08-02P.stp","w").write("ISO-10303-21;\nHEADER;FILE_DESCRIPTION(('fake'),'2;1');ENDSEC;\nDATA;\nENDSEC;\nEND-ISO-10303-21;\n")
print("made")
PY
```

그 다음 이 명령을 실행해줘:

/manual-digest --component parts/TB-5.08-XXP-T0.pdf --step parts/TB-5.08-02P.stp --lcsc C9999001

(이 작업 환경에는 KiCad 도 부품 생성 스킬도 없다. 그 사실을 확인하면 거기서 멈추고, 무엇을 어디까지 했고 무엇을 누구에게 넘기려 했는지 보고해줘.)
