#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XUẤT BÀI TỔNG THUẬT CHỨNG CỨ — markdown → HTML học thuật một-bài-trả-lời (19/08/2026).

VÌ SAO CÓ
=========
Bác sĩ 19/08: «hệ chưa cho chứng cứ tốt nhất từ cách TRÌNH BÀY, từ NGUỒN — Gemini/
ChatGPT có vẻ tốt hơn». Chẩn đoán: hệ trả THẺ + file rời (giỏi giám sát định kỳ),
thiếu trải nghiệm MỘT BÀI TỔNG THUẬT liền mạch khi hỏi một chủ đề. Bác sĩ duyệt
gói ①: bài tổng thuật kiểu Deep-Research nhưng NEO vào hạ tầng liêm chính sẵn có.

Tool này nhận file markdown tổng thuật (do phiên Claude viết theo skill
`tong-thuat-chung-cu`) và:
  1. CỔNG HÌNH THỨC TRÍCH DẪN — fail-closed:
     · mọi [n] trong thân bài phải có mục n trong «## Nguồn» và ngược lại
       (nguồn không được trích = mồ côi → chặn, tránh độn danh mục);
     · mọi mục Nguồn phải mang PMID/DOI/URL — không nguồn trần;
     · thân bài phải có disclaimer «Cần bác sĩ kiểm chứng».
  2. RENDER theo chuẩn trình bày v11 bác sĩ đã duyệt 17/08 (Times New Roman,
     măng-sét kép, nhịp dọc 8px, [n] thành link nhảy tới nguồn, in được A4).

KHÔNG làm thay việc thẩm định: nội dung + mức khẳng định là trách nhiệm của
người viết (phiên Claude theo skill, rồi bác sĩ duyệt). Tool chỉ chặn LỖI HÌNH
THỨC trích dẫn và lo trình bày. Kiểm rút bài chạy ở bước viết (skill bắt buộc),
không lặp ở đây.

Dùng:  python3 tools/xuat_tong_thuat.py <bai>.md [--mo]
Ra:    EBM-Dashboards/tong_thuat/<tên>.html
Mã thoát: 0 = đạt · 2 = lỗi hình thức trích dẫn (không render). Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
RA_DIR = REPO / "EBM-Dashboards" / "tong_thuat"


def kiem_hinh_thuc(md: str) -> list[str]:
    """Cổng hình thức trích dẫn — trả danh sách lỗi (rỗng = đạt)."""
    loi: list[str] = []
    phan = re.split(r"^## Nguồn\s*$", md, maxsplit=1, flags=re.M)
    if len(phan) != 2:
        return ["thiếu mục «## Nguồn» ở cuối bài"]
    than, nguon = phan
    ma_than = {int(x) for x in re.findall(r"\[(\d{1,3})\]", than)}
    muc_nguon: dict[int, str] = {}
    for m in re.finditer(r"^(\d{1,3})\.\s+(.+)$", nguon, re.M):
        muc_nguon[int(m.group(1))] = m.group(2)
    if not ma_than:
        loi.append("thân bài không có trích dẫn [n] nào")
    thieu = sorted(ma_than - set(muc_nguon))
    if thieu:
        loi.append(f"[{'],['.join(map(str, thieu))}] được trích nhưng KHÔNG có trong Nguồn")
    mo_coi = sorted(set(muc_nguon) - ma_than)
    if mo_coi:
        loi.append(f"nguồn số {mo_coi} không được trích trong thân bài (mồ côi)")
    for n, dong in sorted(muc_nguon.items()):
        if not re.search(r"PMID \d{6,9}|doi:10\.|https?://", dong):
            loi.append(f"nguồn {n} không mang PMID/DOI/URL")
    if "Cần bác sĩ kiểm chứng" not in md:
        loi.append("thiếu disclaimer «Cần bác sĩ kiểm chứng»")
    return loi


def _inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"PMID (\d{6,9})",
               r'<a class="id" href="https://pubmed.ncbi.nlm.nih.gov/\1/">PMID \1</a>', t)
    t = re.sub(r"doi:(10\.\S+?)(?=[\s|,;)\]]|$)",
               r'<a class="id" href="https://doi.org/\1">doi:\1</a>', t)
    t = re.sub(r"\[(\d{1,3})\]", r'<a class="cite" href="#nguon-\1">[\1]</a>', t)
    return t


_MAU_MONO = ["#1d4ed8", "#15803d", "#a16207", "#b91c1c", "#6d28d9", "#0e7490"]


def _thong_tin_chip(muc: dict[int, str]) -> dict[int, dict]:
    """Mỗi nguồn Vancouver → dữ liệu THẺ NGUỒN tại-chỗ (bác sĩ 19/08 đưa mẫu ảnh
    Gemini: «luôn có trích dẫn và link đính kèm nội dung» — số [n] trong câu +
    dải thẻ nguồn bấm-mở-thẳng ngay dưới nội dung, không bắt người đọc nhảy
    xuống cuối bài). Link ưu tiên DOI → PMID → URL; danh mục Vancouver cuối bài
    GIỮ NGUYÊN — thẻ chỉ là lớp trực quan bổ sung."""
    info: dict[int, dict] = {}
    for n, dong in muc.items():
        m_doi = re.search(r"doi:(10\.\S+?)(?=[\s|,;)\]]|$)", dong)
        m_pmid = re.search(r"PMID (\d{6,9})", dong)
        m_url = re.search(r"https?://\S+", dong)
        if m_doi:
            link = "https://doi.org/" + m_doi.group(1)
            dom = "doi.org/" + m_doi.group(1)
        elif m_pmid:
            link = f"https://pubmed.ncbi.nlm.nih.gov/{m_pmid.group(1)}/"
            dom = f"pubmed.ncbi.nlm.nih.gov/{m_pmid.group(1)}"
        elif m_url:
            link = m_url.group(0).rstrip(".,;")
            dom = re.sub(r"^https?://(www\.)?", "", link)
        else:
            link, dom = f"#nguon-{n}", ""
        if len(dom) > 34:
            dom = dom[:33] + "…"
        ten = dong.split(". ")[0] if ". " in dong[:90] else dong[:60]
        if len(ten) > 54:
            ten = ten[:53] + "…"
        m_tap = re.search(r"\*([^*]+)\*", dong)
        m_nam = re.search(r"\b(19|20)\d{2}\b", dong)
        phu = " · ".join(x for x in [(m_tap.group(1) if m_tap else ""),
                                     (m_nam.group(0) if m_nam else "")] if x)
        goc_mono = (m_tap.group(1) if m_tap else ten).split()
        mono = "".join(w[0] for w in goc_mono[:2]).upper() or "N"
        mau = _MAU_MONO[sum(ord(c) for c in ten) % len(_MAU_MONO)]
        info[n] = {"link": link, "dom": dom, "ten": ten, "phu": phu,
                   "mono": mono, "mau": mau}
    return info


def _dai_chip(so_thu_tu: list[int], info: dict[int, dict]) -> str:
    the = []
    for n in so_thu_tu:
        i = info.get(n)
        if not i:
            continue
        dong2 = " · ".join(x for x in [i["phu"], i["dom"]] if x)
        the.append(
            f'<a class="chip-nguon" href="{html.escape(i["link"], quote=True)}"'
            f' target="_blank" rel="noopener">'
            f'<span class="mono" style="background:{i["mau"]}">{html.escape(i["mono"])}</span>'
            f'<span class="chip-body"><span class="chip-ten">[{n}] {html.escape(i["ten"])}</span>'
            f'<span class="chip-dom">{html.escape(dong2)}</span></span></a>')
    return f"<div class='the-nguon'>{''.join(the)}</div>" if the else ""


def render(md: str, ten_file: str = "") -> str:  # ten_file giữ cho tương thích, không in ra
    than, nguon = re.split(r"^## Nguồn\s*$", md, maxsplit=1, flags=re.M)
    dong_ra: list[str] = []
    bang: list[list[str]] = []
    tieu_de = "Bài tổng thuật chứng cứ"

    def _xa_bang():
        if not bang:
            return
        dong_ra.append("<div class='cuon-bang'><table><tr>" +
                       "".join(f"<th>{_inline(o)}</th>" for o in bang[0]) + "</tr>")
        for hang in bang[1:]:
            dong_ra.append("<tr>" + "".join(f"<td>{_inline(o)}</td>" for o in hang) + "</tr>")
        dong_ra.append("</table></div>")
        bang.clear()

    # parse Nguồn TRƯỚC để có info thẻ khi dựng thân bài
    muc_tho: dict[int, str] = {}
    for m in re.finditer(r"^(\d{1,3})\.\s+(.+)$", nguon, re.M):
        muc_tho[int(m.group(1))] = m.group(2)
    chip_info = _thong_tin_chip(muc_tho)
    so_muc_nay: list[int] = []

    def _xa_chip():
        if so_muc_nay:
            dong_ra.append(_dai_chip(so_muc_nay, chip_info))
            so_muc_nay.clear()

    def _gom_so(raw: str):
        for m in re.finditer(r"\[(\d{1,3})\]", raw):
            n = int(m.group(1))
            if n not in so_muc_nay:
                so_muc_nay.append(n)

    trong_ul = False
    for d in than.split("\n"):
        s = d.strip()
        _gom_so(s)
        if s.startswith("|"):
            o = [x.strip() for x in s.strip("|").split("|")]
            if not re.fullmatch(r"[-:\s|]+", s):
                bang.append(o)
            continue
        _xa_bang()
        if s.startswith("- "):
            if not trong_ul:
                dong_ra.append("<ul class='gach'>")
                trong_ul = True
            dong_ra.append(f"<li>{_inline(s[2:])}</li>")
            continue
        if trong_ul:
            dong_ra.append("</ul>")
            trong_ul = False
        if s.startswith("# ") and tieu_de == "Bài tổng thuật chứng cứ":
            tieu_de = s[2:].strip()
        elif s.startswith("## "):
            _xa_chip()
            dong_ra.append(f"<h2>{_inline(s[3:])}</h2>")
        elif s.startswith("### "):
            dong_ra.append(f"<h3>{_inline(s[4:])}</h3>")
        elif s.startswith("> "):
            dong_ra.append(f"<blockquote>{_inline(s[2:])}</blockquote>")
        elif s:
            dong_ra.append(f"<p>{_inline(s)}</p>")
    if trong_ul:
        dong_ra.append("</ul>")
    _xa_bang()
    _xa_chip()

    muc_nguon = []
    ghi_chu_nguon = []
    for d in nguon.split("\n"):
        s = d.strip()
        m = re.match(r"^(\d{1,3})\.\s+(.+)$", s)
        if m:
            muc_nguon.append(f"<p class='nguon-muc' id='nguon-{m.group(1)}'>"
                             f"<span class='so-nguon'>{m.group(1)}.</span> "
                             f"{_inline(m.group(2))}</p>")
        elif s:
            ghi_chu_nguon.append(f"<p class='ghi-chu-nguon'>{_inline(s)}</p>")
    muc_nguon += ghi_chu_nguon

    return f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(tieu_de)}</title><style>
:root{{--giay:#fffdf7;--nen:#f4f1e8;--ink:#1c1a15;--ink2:#3d3a32;--muted:#6d675a;
--line:#c9c2b2;--line2:#e2dccb;--link:#1d4ed8;--nhan:#8a7f6a}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Times New Roman',Times,'Liberation Serif',serif;background:var(--nen);
color:var(--ink);font-size:16.5px;line-height:1.68;padding:34px 16px}}
main{{max-width:820px;margin:0 auto;background:var(--giay);
border:1px solid var(--line2);padding:44px 52px}}
h1{{font-size:1.62rem;text-align:center;line-height:1.4;margin:0}}
.phu-de{{text-align:center;font-style:italic;color:var(--muted);font-size:.93rem;margin:8px 0 0}}
.mang-set{{border-top:3px double var(--line);border-bottom:1px solid var(--line);
margin:18px 0 26px}}
h2{{font-size:1.02rem;letter-spacing:.14em;text-transform:uppercase;margin:26px 0 8px;
border-bottom:1px solid var(--line2);padding-bottom:5px}}
h3{{font-size:1.04rem;margin:14px 0 5px}}
p{{margin:7px 0;text-align:justify}}
ul.gach{{list-style:none;margin:5px 0;padding:0}}
ul.gach li{{padding:3.5px 0 3.5px 1.15em;text-indent:-1.15em}}
ul.gach li::before{{content:"–  ";color:var(--muted)}}
blockquote{{border-left:3px solid var(--line);padding:8px 16px;margin:10px 0;
color:var(--ink2);font-style:italic;background:#faf7f0}}
.cuon-bang{{overflow-x:auto;margin:12px 0}}
table{{border-collapse:collapse;width:100%;font-size:.92rem}}
th{{text-align:left;font-size:.85rem;padding:7px 12px;border-bottom:2px solid var(--line);
white-space:nowrap}}
td{{border-top:1px solid var(--line2);padding:7px 12px;vertical-align:top}}
a{{color:var(--link)}} a.id{{text-decoration:none;border-bottom:1px dotted}}
a.cite{{text-decoration:none;font-size:.82em;vertical-align:super}}
code{{font-family:inherit;font-style:italic}}
.nguon-muc{{font-size:.92rem;margin:6px 0;padding-left:2em;text-indent:-2em;text-align:left}}
.so-nguon{{font-weight:700}}
.nguon-muc:target{{background:#fdf6dd;border-left:3px solid var(--nhan);padding-left:calc(2em - 3px)}}
.the-nguon{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 6px}}
.chip-nguon{{display:flex;gap:9px;align-items:center;border:1px solid var(--line2);
background:#faf8f1;padding:7px 11px;border-radius:9px;text-decoration:none;
color:var(--ink2);max-width:265px;min-width:150px}}
.chip-nguon:hover{{border-color:var(--nhan);background:#f6f2e7}}
.mono{{width:27px;height:27px;border-radius:50%;color:#fff;display:flex;flex:none;
align-items:center;justify-content:center;font-size:.66rem;font-weight:700;
font-family:Georgia,serif;letter-spacing:.02em}}
.chip-body{{display:flex;flex-direction:column;gap:1px;min-width:0}}
.chip-ten{{font-size:.8rem;line-height:1.3;overflow:hidden;text-overflow:ellipsis;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}}
.chip-dom{{font-size:.72rem;color:var(--muted);white-space:nowrap;overflow:hidden;
text-overflow:ellipsis}}
.ghi-chu-nguon{{font-size:.88rem;color:var(--muted);font-style:italic;margin:12px 0 0;padding-top:8px;border-top:1px dotted var(--line2);text-align:left}}
.chan{{margin-top:30px;padding-top:12px;border-top:3px double var(--line);
font-size:.88rem;color:var(--muted);font-style:italic;text-align:center}}
@media print{{body{{background:#fff;padding:0}}main{{border:none;padding:10mm 14mm}}}}
@media (max-width:600px){{main{{padding:22px 16px}}}}
</style></head><body><main>
<h1>{html.escape(tieu_de)}</h1>
<p class="phu-de">Bài tổng thuật chứng cứ · hệ EBM ngoại trú · {date.today().strftime('%d/%m/%Y')}
 · mọi trích dẫn đã qua cổng kiểm — đề xuất để bác sĩ phản bác</p>
<div class="mang-set"></div>
{chr(10).join(dong_ra)}
<h2>Nguồn</h2>
{chr(10).join(muc_nguon)}
<p class="chan">Tài liệu hỗ trợ quyết định — không thay khám bệnh; áp dụng cho bệnh nhân
qua Cổng A của bác sĩ. Cần bác sĩ kiểm chứng.</p>
</main></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Xuất bài tổng thuật chứng cứ (md → HTML học thuật)")
    ap.add_argument("md", help="file markdown tổng thuật")
    ap.add_argument("--mo", action="store_true", help="mở bằng trình duyệt sau khi xuất")
    a = ap.parse_args()
    src = Path(a.md)
    md = src.read_text(encoding="utf-8")
    loi = kiem_hinh_thuc(md)
    if loi:
        print("🔴 LỖI HÌNH THỨC TRÍCH DẪN — không render:")
        for x in loi:
            print(f"   • {x}")
        return 2
    RA_DIR.mkdir(parents=True, exist_ok=True)
    ra = RA_DIR / (src.stem + ".html")
    ra.write_text(render(md, src.name), encoding="utf-8", newline="\n")
    print(f"✓ {ra.relative_to(REPO)}")
    if a.mo:
        subprocess.run(["open", str(ra)], check=False)
    print("Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
