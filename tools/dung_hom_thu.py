#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HÒM THƯ BÁC SĨ — một cửa cố định cho mọi sản phẩm hệ sinh ra (17/08/2026).

v2 (17/08 tối): bác sĩ chê bản đầu «không chấp nhận được» về học thuật/thẩm mỹ
— renderer thô bẹt cấu trúc 6-trường/thẻ thành văn xuôi. Nay: PARSE thẻ thành
cấu trúc rồi render CARD học thuật theo ngôn ngữ thiết kế Evidence Workbench
(semantic màu Áp dụng/Cân nhắc/Chưa đủ; hiệu số tách khối tabular; PMID/DOI
thành link chuẩn; rủi ro tách hai vế; footnote thẩm định riêng).

Khối: ① gói tuần (card từng thẻ) ② cảnh báo 14d ③ bản đọc 7d ④ việc chờ 👤
⑤ ứng viên ngoài-quét. Chỉ ĐỌC và RENDER. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
RA = REPO / "HOM-THU-BAC-SI.html"

MAU_DE_XUAT = {"Áp dụng ngay": ("apply", "#15803d", "#dcfce7"),
               "Cân nhắc": ("consider", "#a16207", "#fef9c3"),
               "Chưa đủ": ("notyet", "#c2410c", "#ffedd5")}


def _inline(t: str) -> str:
    """Inline markdown → HTML: bold, italic, code, PMID/DOI thành link."""
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"PMID (\d{6,9})",
               r'<a class="id" href="https://pubmed.ncbi.nlm.nih.gov/\1/">PMID \1</a>', t)
    t = re.sub(r"doi:(10\.\S+?)(?=[\s|,)]|$)",
               r'<a class="id" href="https://doi.org/\1">doi:\1</a>', t)
    return t


def _hang(nhan: str, noi_dung: str, lop: str = "") -> str:
    return (f'<div class="hang {lop}"><div class="nhan">{nhan}</div>'
            f'<div class="nd">{noi_dung}</div></div>')


def render_the(khoi: str) -> str:
    """Một thẻ 6-trường → card học thuật."""
    dong = [d for d in khoi.strip().splitlines() if d.strip()]
    m = re.match(r"\*\*\[([\w-]+)\]\s*(.+?)\s*—\s*(Áp dụng ngay|Cân nhắc|Chưa đủ)\s*(\([^)]*\))?\s*\*?\*?$",
                 dong[0].strip())
    if not m:
        return f"<p>{_inline(dong[0])}</p>" + "".join(f"<p>{_inline(d)}</p>" for d in dong[1:])
    ma, tieu_de, de_xuat, ly_do = m.group(1), m.group(2), m.group(3), (m.group(4) or "")
    lop, mau_chu, mau_nen = MAU_DE_XUAT[de_xuat]
    truong: dict[str, str] = {}
    phu: list[str] = []
    for d in dong[1:]:
        mm = re.match(r"(Điều gì thay đổi|Nguồn|Hiệu số như nguồn báo cáo|Ai bị ảnh hưởng|Rủi ro nếu áp dụng sai)\s*:\s*(.*)", d.strip())
        if mm:
            truong[mm.group(1)] = mm.group(2)
        else:
            phu.append(d.strip())
    than = []
    if "Điều gì thay đổi" in truong:
        than.append(_hang("Điều gì<br>thay đổi", _inline(truong["Điều gì thay đổi"])))
    if "Nguồn" in truong:
        than.append(_hang("Nguồn", f'<span class="nguon">{_inline(truong["Nguồn"])}</span>'))
    if "Hiệu số như nguồn báo cáo" in truong:
        than.append(_hang("Hiệu số<br><span class='chu-thich'>như nguồn báo cáo</span>",
                          f'<div class="hieu-so">{_inline(truong["Hiệu số như nguồn báo cáo"])}</div>'))
    if "Ai bị ảnh hưởng" in truong:
        than.append(_hang("Ai bị<br>ảnh hưởng", _inline(truong["Ai bị ảnh hưởng"])))
    if "Rủi ro nếu áp dụng sai" in truong:
        ve = re.split(r"\s*\|\s*[Nn]ếu bỏ qua\s*:\s*", truong["Rủi ro nếu áp dụng sai"], maxsplit=1)
        rr = f'<div class="rui-ro"><b>Nếu áp dụng sai:</b> {_inline(ve[0])}</div>'
        if len(ve) > 1:
            rr += f'<div class="rui-ro bo-qua"><b>Nếu bỏ qua:</b> {_inline(ve[1])}</div>'
        than.append(_hang("Rủi ro", rr, "hang-rui-ro"))
    chan = "".join(f'<div class="ghi-chu-tham-dinh">{_inline(p)}</div>' for p in phu)
    return f"""<article class="the {lop}">
  <header><span class="ma">{ma}</span>
    <h3>{_inline(tieu_de)}</h3>
    <span class="badge" style="color:{mau_chu};background:{mau_nen}">{de_xuat}{html.escape(" " + ly_do) if ly_do else ""}</span>
  </header>
  {"".join(than)}{chan}
</article>"""


def render_goi_tuan(md: str) -> str:
    """Gói tuần → phần mở + dãy card + phần kết."""
    # cắt theo ranh thẻ **[Wxx-yy]
    manh = re.split(r"(?=^\*\*\[[\w-]+\])", md, flags=re.M)
    mo_dau, the_html, ket = [], [], []
    for i, kh in enumerate(manh):
        if re.match(r"^\*\*\[[\w-]+\]", kh.strip()):
            # phần sau thẻ cuối có thể chứa cả đoạn kết — tách tại dòng '---' hoặc '**Đã quét'
            cat = re.split(r"^(?=---$|\*\*Đã quét)", kh, flags=re.M, maxsplit=1)
            the_html.append(render_the(cat[0]))
            if len(cat) > 1:
                ket.append(cat[1])
        elif not the_html:
            mo_dau.append(kh)
        else:
            ket.append(kh)

    def md_don_gian(t: str) -> str:
        ra = []
        for d in t.splitlines():
            s = _inline(d)
            if d.startswith("### "):
                ra.append(f"<h4>{s[4:]}</h4>")
            elif d.startswith("## "):
                ra.append(f"<h3>{s[3:]}</h3>")
            elif d.startswith("# "):
                ra.append(f"<h2>{s[2:]}</h2>")
            elif d.strip() == "---":
                ra.append("<hr>")
            elif d.startswith("|"):
                o = [x.strip() for x in d.strip("|").split("|")]
                if set("".join(o)) <= set("-: "):
                    continue
                ra.append("<tr>" + "".join(f"<td>{_inline(x)}</td>" for x in o) + "</tr>")
            elif d.startswith("- ") or d.startswith("• "):
                ra.append(f"<div class='li'>• {s[2:]}</div>")
            elif d.strip():
                ra.append(f"<p>{s}</p>")
        t2 = "\n".join(ra)
        t2 = re.sub(r"((?:<tr>.*?</tr>\n?)+)", r"<table>\1</table>", t2, flags=re.S)
        return t2

    return (f'<div class="mo-dau">{md_don_gian("".join(mo_dau))}</div>'
            + "".join(the_html)
            + f'<div class="ket-goi">{md_don_gian("".join(ket))}</div>')


def main() -> int:
    hom_nay = dt.datetime.now()
    khoi: list[str] = []

    goi = sorted((REPO / "queue").glob("tuan-*.md"))
    if goi:
        g = goi[-1]
        tuoi = (hom_nay.date() - dt.date.fromtimestamp(g.stat().st_mtime)).days
        khoi.append(f"<section class='goi'><div class='tag moi'>GÓI DUYỆT TUẦN · {g.stem.upper()} · "
                    f"{'HÔM NAY' if tuoi == 0 else f'{tuoi} NGÀY TRƯỚC'}</div>"
                    + render_goi_tuan(g.read_text(encoding="utf-8", errors="replace"))
                    + "</section>")

    canh_bao = []
    for f in sorted((REPO / "alerts").glob("*.md"), reverse=True):
        if (hom_nay.date() - dt.date.fromtimestamp(f.stat().st_mtime)).days <= 14:
            canh_bao.append(f"<h4>{f.stem}</h4><p>" + _inline(
                f.read_text(encoding="utf-8", errors="replace")[:2500]) + "</p>")
    if canh_bao:
        khoi.append("<section><div class='tag do'>CẢNH BÁO 14 NGÀY</div>"
                    + "\n".join(canh_bao) + "</section>")

    ban_doc = []
    der = REPO / "EBM-Dashboards" / "derivatives"
    for f in sorted(der.glob("*_ban-doc.html"), key=lambda x: -x.stat().st_mtime):
        if (hom_nay.date() - dt.date.fromtimestamp(f.stat().st_mtime)).days <= 7:
            ten = f.name.replace("_ban-doc.html", "").replace("_", " ")
            ban_doc.append(f"<a class='o-doc' href='EBM-Dashboards/derivatives/{f.name}'>"
                           f"<span>📖</span><span>{html.escape(ten)}</span>"
                           f"<span class='mo'>{dt.date.fromtimestamp(f.stat().st_mtime):%d/%m}</span></a>")
    if ban_doc:
        khoi.append(f"<section><div class='tag xanh'>BẢN ĐỌC CẬP NHẬT 7 NGÀY ({len(ban_doc)})</div>"
                    "<p class='mo'>Bấm mở thẳng — cờ đỏ và việc-cần-làm đứng trước, chứng cứ xếp sau trên một trục.</p>"
                    f"<div class='luoi-doc'>{''.join(ban_doc)}</div></section>")

    try:
        r = subprocess.run([sys.executable, "tools/tu_de_xuat_viec.py", "--gon"],
                           capture_output=True, text=True, timeout=300, cwd=REPO)
        loc, giu = [], False
        for ln in (r.stdout or "").splitlines():
            if "👤" in ln:
                loc.append(f"<div class='li'>{_inline(ln.strip())}</div>")
                giu = True
            elif giu and "→" in ln:
                loc.append(f"<div class='li lenh'>{_inline(ln.strip())}</div>")
                giu = False
            else:
                giu = False
        if loc:
            khoi.append("<section><div class='tag vang'>VIỆC CHỜ BÁC SĨ</div>"
                        + "\n".join(loc) + "</section>")
    except (OSError, subprocess.SubprocessError):
        pass

    uv = REPO / "EBM-Dashboards" / "surveillance" / "ung-vien-ngoai-quet.jsonl"
    if uv.exists():
        con = [json.loads(x) for x in uv.read_text(encoding="utf-8").splitlines()
               if x.strip() and "CANDIDATE" in x]
        if con:
            dong = [f"<div class='li'>🔎 {_inline('PMID ' + c['pmid'])} — {html.escape(c['title'][:110])} "
                    f"<span class='mo'>({html.escape(c.get('nguon_phat_hien', ''))})</span></div>"
                    for c in con]
            khoi.append("<section><div class='tag'>ỨNG VIÊN NGOÀI-QUÉT CÒN CHỜ</div>"
                        + "\n".join(dong) + "</section>")

    RA.write_text(f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hòm thư Bác sĩ — EBM</title>
<style>
  :root{{--ink:#0f172a;--ink2:#334155;--muted:#64748b;--line:#e2e8f0;--bg:#eef1f6;
        --primary:#0e7490;--apply:#15803d;--consider:#a16207;--notyet:#c2410c;--danger:#b91c1c}}
  *{{box-sizing:border-box}}
  body{{font-family:-apple-system,'Segoe UI',Roboto,'Helvetica Neue',sans-serif;
       max-width:920px;margin:0 auto;padding:28px 22px 70px;background:var(--bg);
       color:var(--ink);line-height:1.6;font-size:15.5px}}
  h1{{font-size:1.45rem;margin:0 0 2px;letter-spacing:-.01em}}
  h2{{font-size:1.12rem}} h3{{font-size:1.02rem;margin:.2em 0}} h4{{font-size:.95rem;margin:14px 0 4px}}
  section{{background:#fff;border:1px solid var(--line);border-radius:14px;
          padding:22px 24px;margin:18px 0;box-shadow:0 1px 4px rgba(15,23,42,.05)}}
  .tag{{display:inline-block;font-size:.7rem;font-weight:800;letter-spacing:.08em;
       padding:4px 12px;border-radius:99px;background:#e2e8f0;color:var(--ink2);margin-bottom:12px}}
  .tag.moi{{background:#dbeafe;color:#1d4ed8}} .tag.do{{background:#fee2e2;color:var(--danger)}}
  .tag.xanh{{background:#dcfce7;color:var(--apply)}} .tag.vang{{background:#fef9c3;color:var(--consider)}}
  /* ── card thẻ chứng cứ ── */
  .the{{border:1px solid var(--line);border-left:5px solid var(--muted);border-radius:12px;
       padding:16px 18px 12px;margin:16px 0;background:#fff}}
  .the.apply{{border-left-color:var(--apply)}} .the.consider{{border-left-color:var(--consider)}}
  .the.notyet{{border-left-color:var(--notyet)}}
  .the header{{display:flex;align-items:flex-start;gap:10px;flex-wrap:wrap;margin-bottom:10px}}
  .the .ma{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.72rem;
           font-weight:700;color:var(--muted);background:#f1f5f9;border-radius:6px;
           padding:3px 8px;margin-top:3px;white-space:nowrap}}
  .the h3{{flex:1 1 320px;font-size:1rem;line-height:1.45;margin:0;font-weight:650}}
  .badge{{font-size:.74rem;font-weight:800;padding:4px 12px;border-radius:99px;
         white-space:nowrap;margin-top:2px}}
  .hang{{display:grid;grid-template-columns:118px 1fr;gap:12px;padding:7px 0;
        border-top:1px solid #f1f5f9;font-size:.92rem}}
  .nhan{{font-size:.7rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;
        color:var(--muted);padding-top:3px;line-height:1.35}}
  .nhan .chu-thich{{font-weight:500;text-transform:none;letter-spacing:0}}
  .nd{{color:var(--ink2)}}
  .nguon{{font-size:.88rem}}
  .hieu-so{{background:#f8fafc;border:1px solid var(--line);border-radius:9px;
           padding:10px 13px;font-variant-numeric:tabular-nums;line-height:1.65}}
  .hieu-so b{{color:var(--ink);font-size:1.02em}}
  .rui-ro{{padding:2px 0}} .rui-ro.bo-qua{{color:var(--muted)}}
  .ghi-chu-tham-dinh{{margin-top:10px;padding:9px 13px;background:#fffbeb;
        border:1px solid #fde68a;border-radius:9px;font-size:.86rem;color:#78350f}}
  a.id{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88em;
       color:var(--primary);text-decoration:none;border-bottom:1px dotted}}
  a{{color:#1d4ed8}} code{{background:#f1f5f9;padding:1px 6px;border-radius:5px;font-size:.86em}}
  hr{{border:none;border-top:1px solid var(--line);margin:16px 0}}
  table{{border-collapse:collapse;margin:10px 0;font-size:.88rem;width:100%}}
  td{{border:1px solid var(--line);padding:6px 10px;vertical-align:top}}
  .li{{margin:4px 0}} .li.lenh{{color:var(--muted);font-size:.85rem;margin-left:20px}}
  .mo{{color:var(--muted);font-size:.85rem}}
  .mo-dau p,.ket-goi p{{font-size:.92rem;color:var(--ink2)}}
  .luoi-doc{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:8px}}
  .o-doc{{display:flex;gap:8px;align-items:baseline;border:1px solid var(--line);
         border-radius:10px;padding:9px 12px;text-decoration:none;color:var(--ink2);
         font-size:.88rem;background:#fbfdff}}
  .o-doc:hover{{border-color:var(--primary)}}
  .o-doc .mo{{margin-left:auto;white-space:nowrap}}
  .chan{{color:var(--muted);font-size:.8rem;margin-top:26px}}
  @media (max-width:560px){{.hang{{grid-template-columns:1fr}}.nhan{{padding-top:0}}}}
</style></head><body>
<h1>📬 Hòm thư Bác sĩ</h1>
<p class="mo">Dựng {hom_nay:%d/%m/%Y %H:%M} — một cửa cho mọi sản phẩm hệ sinh ra.
Tự làm tươi ở đuôi mỗi gói tuần; làm tươi tay: <code>python3 tools/dung_hom_thu.py</code>.</p>
{"".join(khoi)}
<p class="chan">Mọi thẻ dừng ở CANDIDATE — đề xuất để bác sĩ phản bác, quyết định áp dụng
thuộc Cổng A/B của bác sĩ. Cần bác sĩ kiểm chứng trước khi áp dụng cho người bệnh cụ thể.</p>
</body></html>""", encoding="utf-8", newline="\n")
    print(f"✓ {RA.name} — {len(khoi)} khối")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
