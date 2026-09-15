---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Skill]
model: sonnet
runs: 3
---
먼저 아래 스크립트를 그대로 실행해서 작업용 샘플 매뉴얼 PDF를 만들어줘.

```bash
python3 - <<'PY'
import fitz, os
SEC = [("1 Introduction",2),("2 Description",4),("3 Functional overview",7),
       ("4 Pinouts and pin description",6),("5 Memory mapping",3),
       ("6 Electrical characteristics",9),("7 Package information",5),
       ("8 Ordering information",2)]
F = ["Maximum CPU frequency: 184 MHz (231 DMIPS)",
     "Flash memory: 192 Kbytes with ECC support",
     "SRAM: 48 Kbytes total (36 Kbytes + 12 Kbytes CCM)",
     "VDD/VDDA operating range: 1.62 V to 3.6 V",
     "Packages: LQFP64, LQFP48, UFQFPN48"]
doc = fitz.open(); toc = []
p = doc.new_page(); p.insert_text((60,90), "ACME-MX184RB", fontsize=22)
p.insert_text((60,120), "Arm Cortex-M4 32-bit MCU+FPU - Datasheet", fontsize=13)
p.insert_text((60,150), "DS-AX184 Rev 6", fontsize=10)
for i,f in enumerate(F): p.insert_text((60,200+i*20), "- "+f, fontsize=10)
n = 2
for title, plen in SEC:
    toc.append([1, title, n])
    for k in range(plen):
        pg = doc.new_page()
        pg.insert_text((60,70), title if k==0 else title+" (cont.)", fontsize=15)
        pg.insert_text((60,110), "Section body page %d." % (k+1), fontsize=10)
        pg.insert_text((60,135), F[(n+k) % len(F)], fontsize=10)
        pg.insert_text((60,160), "Refer to Table %d-%d for detailed limits." % (len(toc), k+1), fontsize=10)
        pg.insert_text((300,800), "%d/%d" % (n+k, 1+sum(s[1] for s in SEC)), fontsize=8)
    n += plen
doc.set_toc(toc); os.makedirs("manuals", exist_ok=True)
doc.save("manuals/acme-mx184rb-datasheet.pdf")
print("pages", doc.page_count, "toc", len(toc))
PY
```

그 PDF가 생긴 다음, 아래 요청을 처리해줘.

---

Index the datasheet at `manuals/acme-mx184rb-datasheet.pdf` — I'll be referencing it constantly.
