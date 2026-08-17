#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HÒM THƯ BÁC SĨ — một cửa cố định cho mọi sản phẩm hệ sinh ra (17/08/2026).

VÌ SAO CÓ
=========
Kỳ lịch đầu tiên chạy trọn (17/08) nhưng bác sĩ nói thẳng: «gói đã chạy xong
tôi KHÔNG THỂ TIẾP CẬN thông tin cập nhật để đánh giá và áp dụng». Sản phẩm
nằm rải queue/ · derivatives/ · alerts/, tác vụ lịch chạy ở phiên riêng —
không có đường tiếp cận tự nhiên. Đây là lỗ LAST-MILE: hệ tốt đến đâu cũng
vô nghĩa nếu người dùng không mở được sản phẩm.

Tool dựng `HOM-THU-BAC-SI.html` ở GỐC thư mục (OneDrive sync cả 2 máy, bấm đúp
là mở, không cần Claude đang chạy):
  ① GÓI TUẦN MỚI NHẤT — nhúng TRỌN nội dung (không bắt mở file md)
  ② CẢNH BÁO (alerts/ 14 ngày)
  ③ BẢN ĐỌC mới cập nhật 7 ngày (link mở thẳng)
  ④ VIỆC CHỜ BÁC SĨ (bảng tự-đề-xuất, chỉ nhóm 👤)
  ⑤ ỨNG VIÊN NGOÀI-QUÉT còn CANDIDATE

Chạy: python3 tools/dung_hom_thu.py   (nối sẵn ở ĐUÔI gói tuần — tự tươi mỗi thứ Hai)
Chỉ ĐỌC và RENDER — không sửa dữ liệu nào. Cần bác sĩ kiểm chứng.
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


def _md_sang_html(md: str) -> str:
    """Render markdown → HTML đủ dùng cho gói tuần (thuần python, không phụ thuộc)."""
    ra = []
    for dong in md.splitlines():
        d = html.escape(dong, quote=False)
        d = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", d)
        d = re.sub(r"`([^`]+)`", r"<code>\1</code>", d)
        if d.startswith("### "):
            ra.append(f"<h4>{d[4:]}</h4>")
        elif d.startswith("## "):
            ra.append(f"<h3>{d[3:]}</h3>")
        elif d.startswith("# "):
            ra.append(f"<h2>{d[2:]}</h2>")
        elif d.startswith("- ") or d.startswith("· "):
            ra.append(f"<div class='li'>• {d[2:]}</div>")
        elif d.strip() == "---":
            ra.append("<hr>")
        elif not d.strip():
            ra.append("<div class='sp'></div>")
        else:
            ra.append(f"<p>{d}</p>")
    return "\n".join(ra)


def main() -> int:
    hom_nay = dt.date.today()
    khoi: list[str] = []

    # ① gói tuần mới nhất — NHÚNG TRỌN
    goi = sorted((REPO / "queue").glob("tuan-*.md"))
    if goi:
        g = goi[-1]
        tuoi = (hom_nay - dt.date.fromtimestamp(g.stat().st_mtime)).days
        khoi.append(f"<section><div class='tag moi'>GÓI DUYỆT TUẦN · {g.stem} · "
                    f"{'HÔM NAY' if tuoi == 0 else f'{tuoi} ngày trước'}</div>"
                    + _md_sang_html(g.read_text(encoding="utf-8", errors="replace"))
                    + "</section>")

    # ② cảnh báo 14 ngày
    canh_bao = []
    for f in sorted((REPO / "alerts").glob("*.md"), reverse=True):
        if (hom_nay - dt.date.fromtimestamp(f.stat().st_mtime)).days <= 14:
            canh_bao.append(f"<h4>{f.stem}</h4>" + _md_sang_html(
                f.read_text(encoding="utf-8", errors="replace")[:3000]))
    if canh_bao:
        khoi.append("<section><div class='tag do'>CẢNH BÁO 14 NGÀY</div>"
                    + "\n".join(canh_bao) + "</section>")

    # ③ bản đọc mới 7 ngày
    ban_doc = []
    der = REPO / "EBM-Dashboards" / "derivatives"
    for f in sorted(der.glob("*_ban-doc.html"), key=lambda x: -x.stat().st_mtime):
        if (hom_nay - dt.date.fromtimestamp(f.stat().st_mtime)).days <= 7:
            ten = f.name.replace("_ban-doc.html", "")
            ban_doc.append(f"<div class='li'>📖 <a href='EBM-Dashboards/derivatives/{f.name}'>"
                           f"{html.escape(ten)}</a> <span class='mo'>"
                           f"({dt.date.fromtimestamp(f.stat().st_mtime):%d/%m})</span></div>")
    if ban_doc:
        khoi.append(f"<section><div class='tag xanh'>BẢN ĐỌC CẬP NHẬT 7 NGÀY ({len(ban_doc)})</div>"
                    "<p class='mo'>Bấm mở thẳng — cờ đỏ và việc-cần-làm đứng trước, chứng cứ sau.</p>"
                    + "\n".join(ban_doc) + "</section>")

    # ④ việc chờ bác sĩ (bảng tự-đề-xuất, lọc 👤)
    try:
        r = subprocess.run([sys.executable, "tools/tu_de_xuat_viec.py", "--gon"],
                           capture_output=True, text=True, timeout=300, cwd=REPO)
        # giữ cặp dòng (việc 👤 + dòng lệnh ngay sau)
        loc, giu = [], False
        for ln in (r.stdout or "").splitlines():
            if "👤" in ln:
                loc.append(ln.strip())
                giu = True
            elif giu and "→" in ln:
                loc.append("   " + ln.strip())
                giu = False
            else:
                giu = False
        if loc:
            khoi.append("<section><div class='tag vang'>VIỆC CHỜ BÁC SĨ</div><pre>"
                        + html.escape("\n".join(loc)) + "</pre></section>")
    except (OSError, subprocess.SubprocessError):
        pass

    # ⑤ ứng viên ngoài-quét còn CANDIDATE
    uv = REPO / "EBM-Dashboards" / "surveillance" / "ung-vien-ngoai-quet.jsonl"
    if uv.exists():
        con = [json.loads(x) for x in uv.read_text(encoding="utf-8").splitlines()
               if x.strip() and "CANDIDATE" in x]
        if con:
            dong = [f"<div class='li'>🔎 PMID {c['pmid']} — {html.escape(c['title'][:110])} "
                    f"<span class='mo'>({html.escape(c.get('nguon_phat_hien', ''))})</span></div>"
                    for c in con]
            khoi.append("<section><div class='tag'>ỨNG VIÊN NGOÀI-QUÉT CÒN CHỜ</div>"
                        + "\n".join(dong) + "</section>")

    RA.write_text(f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hòm thư Bác sĩ — EBM</title>
<style>
  body{{font-family:-apple-system,'Segoe UI',Roboto,sans-serif;max-width:880px;margin:0 auto;
       padding:24px 20px 60px;background:#f4f6fa;color:#0f172a;line-height:1.55}}
  h1{{font-size:1.35rem;margin:0 0 4px}} h2{{font-size:1.1rem}} h3{{font-size:1rem}}
  h4{{font-size:.95rem;margin:14px 0 4px}}
  section{{background:#fff;border:1px solid #e2e8f0;border-radius:12px;
          padding:18px 20px;margin:16px 0;box-shadow:0 1px 3px rgba(15,23,42,.06)}}
  .tag{{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.06em;
       padding:3px 10px;border-radius:99px;background:#e2e8f0;color:#334155;margin-bottom:10px}}
  .tag.moi{{background:#dbeafe;color:#1d4ed8}} .tag.do{{background:#fee2e2;color:#b91c1c}}
  .tag.xanh{{background:#dcfce7;color:#15803d}} .tag.vang{{background:#fef9c3;color:#a16207}}
  .li{{margin:3px 0}} .mo{{color:#64748b;font-size:.85rem}} .sp{{height:8px}}
  pre{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;
      overflow-x:auto;font-size:.82rem;line-height:1.5}}
  code{{background:#f1f5f9;padding:1px 5px;border-radius:4px;font-size:.85em}}
  a{{color:#1d4ed8}} hr{{border:none;border-top:1px solid #e2e8f0;margin:14px 0}}
  .chan{{color:#64748b;font-size:.8rem;margin-top:24px}}
</style></head><body>
<h1>📬 Hòm thư Bác sĩ</h1>
<p class="mo">Dựng {hom_nay:%d/%m/%Y %H:%M} — một cửa cho mọi sản phẩm hệ sinh ra.
Tự làm tươi ở đuôi mỗi gói tuần; làm tươi tay: <code>python3 tools/dung_hom_thu.py</code>.</p>
{"".join(khoi)}
<p class="chan">Mọi thẻ dừng ở CANDIDATE — quyết định áp dụng là của bác sĩ (Cổng A/B).
Cần bác sĩ kiểm chứng trước khi áp dụng cho người bệnh cụ thể.</p>
</body></html>""", encoding="utf-8", newline="\n")
    print(f"✓ {RA.name} — {len(khoi)} khối")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
