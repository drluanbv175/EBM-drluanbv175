#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_library.py — Thư viện cập nhật chứng cứ (chỉ mục mọi Web Dashboard EBM đã làm).

Biến các bản cập nhật rời rạc thành MỘT tài sản tra cứu tích lũy: mỗi lần làm xong
một dashboard, thêm vào thư viện; sinh trang `evidence-library.html` có tìm/lọc,
mỗi dòng mở thẳng dashboard tương ứng.

Cách dùng (đặt cùng thư mục với các file dashboard):
    python3 build_library.py add <dashboard.html>     # thêm/cập nhật 1 mục + dựng lại HTML
    python3 build_library.py build                     # dựng lại HTML từ library.json
    python3 build_library.py add *.html                # thêm nhiều file

Dữ liệu lưu trong `library.json`; trang xuất `evidence-library.html` (cùng thư mục).
"""
import sys, os, re, json, glob

VALID_DECISION = {"apply", "consider", "notyet"}


def parse_dashboard(path):
    html = open(path, encoding="utf-8").read()
    i = html.find("const DATA")
    block = html[i:html.find("HẾT KHỐI DATA", i)] if i != -1 else html
    def meta(name):
        m = re.search(name + r"\s*:\s*['\"]([^'\"]*)['\"]", block)
        return m.group(1) if m else ""
    question = meta("question")
    updated = meta("updated")
    eyebrow = meta("eyebrow")
    # items
    ipos = block.find("items:")
    seg = block[ipos:] if ipos != -1 else block
    starts = [m.start() for m in re.finditer(r"\{\s*id\s*:\s*['\"]", seg)]
    dec = {"apply": 0, "consider": 0, "notyet": 0}
    pmids = set()
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(seg)
        ch = seg[s:e]
        d = re.search(r"decision\s*:\s*['\"](\w+)['\"]", ch)
        if d and d.group(1) in dec:
            dec[d.group(1)] += 1
        for pm in re.findall(r"pmid\s*:\s*['\"](\d+)['\"]", ch):
            pmids.add(pm)
    skin = "Dark Analyst" if ("ANALYST" in html or "dark-analyst" in html) else "Evidence Workbench"
    return {
        "file": os.path.basename(path),
        "question": question or "(không rõ tiêu đề)",
        "updated": updated or "",
        "eyebrow": eyebrow or "",
        "total": len(starts),
        "apply": dec["apply"], "consider": dec["consider"], "notyet": dec["notyet"],
        "pmids": sorted(pmids), "skin": skin,
    }


def load_lib(libpath):
    if os.path.exists(libpath):
        return json.load(open(libpath, encoding="utf-8"))
    return []


def upsert(lib, entry):
    lib = [e for e in lib if e.get("file") != entry["file"]]
    lib.append(entry)
    lib.sort(key=lambda e: (e.get("updated", ""), e.get("file", "")), reverse=True)
    return lib


HTML = """<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Thư viện cập nhật chứng cứ EBM</title><style>
:root{--bg:#0b1120;--bg2:#0f172a;--sur:#111a2e;--ink:#e7edf6;--ink2:#aebbd0;--muted:#7689a6;--faint:#56688a;--line:#1e2c46;--line2:#2a3b5c;--cyan:#22d3ee;--apply:#34d399;--consider:#fbbf24;--notyet:#fb923c;--mono:ui-monospace,Menlo,Consolas,monospace}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,system-ui,Arial,sans-serif;background:var(--bg);color:var(--ink);font-size:13px}
.top{display:flex;align-items:center;gap:12px;padding:12px 18px;background:var(--bg2);border-bottom:1px solid var(--line)}
.logo{width:26px;height:26px;border-radius:7px;background:linear-gradient(135deg,var(--cyan),#a78bfa);color:#06121f;display:grid;place-items:center;font-weight:800}
.top h1{font-size:15px}.top .sub{color:var(--muted);font-size:11px}
.bar{display:flex;gap:10px;padding:10px 18px;background:var(--bg2);border-bottom:1px solid var(--line);flex-wrap:wrap;align-items:center}
.bar input{flex:1;min-width:220px;background:var(--sur);border:1px solid var(--line2);border-radius:9px;padding:8px 11px;color:var(--ink);font-family:var(--mono);outline:none}
.chip{font-size:11px;color:var(--ink2);background:var(--sur);border:1px solid var(--line2);border-radius:20px;padding:4px 12px;cursor:pointer}
.chip.on{background:rgba(34,211,238,.14);border-color:var(--cyan);color:var(--cyan);font-weight:700}
.kpi{font-family:var(--mono);color:var(--muted);font-size:11px;margin-left:auto}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:12.5px}
thead th{position:sticky;top:0;background:var(--bg2);text-align:left;padding:9px 16px;font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);border-bottom:1px solid var(--line2)}
tbody tr{border-bottom:1px solid var(--line)}tbody tr:hover{background:var(--sur)}
tbody td{padding:11px 16px;vertical-align:top}
.q{font-weight:600;line-height:1.35;max-width:560px}.q .eb{display:block;color:var(--faint);font-size:10px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:2px}
.d{font-family:var(--mono);color:var(--ink2)}
.dec{display:inline-flex;gap:5px;font-family:var(--mono);font-size:11px}
.dec b{padding:1px 7px;border-radius:6px;font-weight:800}
.a{background:rgba(52,211,153,.15);color:var(--apply)}.c{background:rgba(251,191,36,.15);color:var(--consider)}.n{background:rgba(251,146,60,.15);color:var(--notyet)}
.skin{font-size:9.5px;color:var(--muted);border:1px solid var(--line2);border-radius:5px;padding:1px 6px}
.open{display:inline-flex;align-items:center;gap:6px;background:var(--cyan);color:#06121f;font-weight:800;border-radius:7px;padding:5px 11px;font-size:11px}
.foot{padding:9px 18px;color:var(--faint);font-size:11px;border-top:1px solid var(--line)}
.empty{padding:40px;text-align:center;color:var(--muted)}
</style></head><body>
<div class="top"><span class="logo">⊕</span><div><h1>Thư viện cập nhật chứng cứ EBM</h1><div class="sub">Chỉ mục mọi Web Dashboard đã làm · click để mở</div></div></div>
<div class="bar"><input id="q" placeholder="Tìm: chủ đề, thuốc, PMID…" oninput="render()"/>
<span class="chip on" data-f="all" onclick="setf(this)">Tất cả</span>
<span class="chip" data-f="apply" onclick="setf(this)">Có “áp dụng ngay”</span>
<span class="kpi" id="kpi"></span></div>
<table><thead><tr><th>Chủ đề cập nhật</th><th>Ngày</th><th>Quyết định</th><th>Nguồn</th><th></th></tr></thead><tbody id="rows"></tbody></table>
<div class="foot">⚠ Mỗi dashboard kèm disclaimer “Cần bác sĩ kiểm chứng”, nguồn PMID/DOI, không lưu PII. Sinh tự động từ <span class="d">library.json</span>.</div>
<script>
const LIB=/*LIBRARY*/[]/*END*/;
let filt="all";
function setf(el){document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));el.classList.add('on');filt=el.dataset.f;render();}
function render(){
  const q=document.getElementById('q').value.trim().toLowerCase();
  let arr=LIB.slice();
  if(filt==='apply')arr=arr.filter(e=>e.apply>0);
  if(q)arr=arr.filter(e=>JSON.stringify(e).toLowerCase().includes(q));
  document.getElementById('kpi').textContent=arr.length+' / '+LIB.length+' bản cập nhật';
  document.getElementById('rows').innerHTML=arr.map(e=>`<tr>
    <td><div class="q"><span class="eb">${e.eyebrow||''}</span>${e.question}</div></td>
    <td class="d">${e.updated||'—'}</td>
    <td><span class="dec"><b class="a">${e.apply}</b><b class="c">${e.consider}</b><b class="n">${e.notyet}</b></span></td>
    <td class="d">${e.total} item · ${(e.pmids||[]).length} PMID <span class="skin">${e.skin||''}</span></td>
    <td><a class="open" href="${e.file}" target="_blank">Mở →</a></td>
  </tr>`).join('')||`<tr><td colspan="5" class="empty">Chưa có bản cập nhật nào khớp.</td></tr>`;
}
render();
</script></body></html>"""


def build_html(lib, outpath):
    data = json.dumps(lib, ensure_ascii=False, indent=1)
    html = HTML.replace("/*LIBRARY*/[]/*END*/", data)
    open(outpath, "w", encoding="utf-8").write(html)


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    cmd = sys.argv[1]
    base = os.getcwd()
    libpath = os.path.join(base, "library.json")
    outpath = os.path.join(base, "evidence-library.html")
    lib = load_lib(libpath)

    if cmd == "add":
        files = []
        for a in sys.argv[2:]:
            files += glob.glob(a)
        files = [f for f in files if f.endswith(".html") and "evidence-library" not in f]
        if not files:
            print("Không có file .html hợp lệ để thêm."); return 1
        for f in files:
            entry = parse_dashboard(f)
            lib = upsert(lib, entry)
            print("  + %s  (%s · %d item · áp dụng %d)" % (entry["file"], entry["updated"], entry["total"], entry["apply"]))
        json.dump(lib, open(libpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        build_html(lib, outpath)
    elif cmd == "build":
        build_html(lib, outpath)
    else:
        print("Lệnh không rõ. Dùng: add <file.html> | build"); return 1

    print("Thư viện: %d bản → %s" % (len(lib), outpath))
    return 0


if __name__ == "__main__":
    sys.exit(main())
