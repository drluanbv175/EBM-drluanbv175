#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỔ ĐĂNG KÝ BÀI TỔNG THUẬT — đưa bài vào vòng sống của hệ (20/08/2026).

VÌ SAO CÓ
=========
Bài tổng thuật hiện là ẢNH TĨNH: không nằm trong hòm thư, không ai canh độ tươi,
không nối với bộ dò chứng-cứ-vượt-qua. Nó sẽ cũ đi IM LẶNG — đúng họ lỗi đã vá ở
dashboard (một sản phẩm không có ai canh thì với bác sĩ nó thành sai lúc nào không hay).

Tool quét `EBM-Dashboards/tong_thuat/*.md` → sổ máy-đọc `so-tong-thuat.json`:
tiêu đề · ngày · chủ đề khớp danh bạ · PMID/DOI trong bài · số nguồn · tuổi.
Chỉ ĐỌC và GHI SỔ — không sửa bài, không phán nội dung.

Dùng:  python3 tools/dang_ky_tong_thuat.py            # cập nhật sổ + in bảng
       python3 tools/dang_ky_tong_thuat.py --qua-han 90
Mã thoát: 0 · 1 chưa có thư mục bài. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
THU_MUC = REPO / "EBM-Dashboards" / "tong_thuat"
SO = THU_MUC / "so-tong-thuat.json"
DANH_BA = REPO / "EBM-Dashboards" / "nguon_chuan" / "danh-ba-nguon-chuan.json"


def _khong_dau(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn").replace("đ", "d")


def _chu_de(tieu_de: str, than: str) -> list[str]:
    """Khớp chủ đề danh bạ để bộ dò chứng-cứ-vượt-qua và độ tươi quét được."""
    if not DANH_BA.exists():
        return []
    db = json.loads(DANH_BA.read_text(encoding="utf-8"))
    # Khớp theo RANH GIỚI TỪ, không phải chuỗi con: bỏ dấu xong «tha» (tăng huyết
    # áp) trúng trong «thay đổi», «cap» trúng «cấp» ⇒ mọi bài dính mọi chủ đề
    # (đo 20/08: 9/9 bài đều khớp tăng-huyết-áp + kháng-sinh). Cùng họ lỗi khớp
    # lỏng đã gặp nhiều lần trong hệ.
    goc = tieu_de + " " + than[:4000]
    vb = _khong_dau(goc)
    ra = []
    for ma, cd in db["chu_de"].items():
        for tk in cd["tu_khoa"]:
            k = _khong_dau(tk)
            la_viet_tat = len(k) <= 4 and " " not in k and k.isascii()
            if la_viet_tat:
                # VIẾT TẮT phải khớp CHỮ HOA trên văn bản GỐC: bỏ dấu xong «CAP»
                # trùng «cấp», «THA» trùng «tha thứ» ⇒ mọi bài dính mọi chủ đề
                # (đo 20/08: 9/9 bài khớp kháng-sinh chỉ vì chữ «đợt cấp»).
                hop = re.search(rf"(?<![A-Za-z0-9]){re.escape(tk.upper())}(?![A-Za-z0-9])", goc)
            else:
                hop = re.search(rf"(?<![a-z]){re.escape(k)}(?![a-z])", vb)
            if hop:
                ra.append(ma)
                break
    return ra


def quet() -> list[dict]:
    ban_ghi = []
    for f in sorted(THU_MUC.glob("TT_*.md")):
        vb = f.read_text(encoding="utf-8", errors="replace")
        m_td = re.search(r"^#\s+(.+)$", vb, re.M)
        tieu_de = m_td.group(1).strip() if m_td else f.stem
        m_ngay = re.search(r"_(\d{8})\.md$", f.name)
        ngay = (f"{m_ngay.group(1)[:4]}-{m_ngay.group(1)[4:6]}-{m_ngay.group(1)[6:]}"
                if m_ngay else date.fromtimestamp(f.stat().st_mtime).isoformat())
        phan = re.split(r"^## Nguồn\s*$", vb, maxsplit=1, flags=re.M)
        nguon_vb = phan[1] if len(phan) == 2 else ""
        pmids = sorted(set(re.findall(r"PMID (\d{6,9})", nguon_vb)))
        dois = sorted(set(re.findall(r"doi:(10\.\S+?)(?=[\s|,;)\]]|$)", nguon_vb)))
        so_muc = len(re.findall(r"^\d{1,3}\.\s+", nguon_vb, re.M))
        tuoi = (date.today() - date.fromisoformat(ngay)).days
        ban_ghi.append({
            "file_md": str(f.relative_to(REPO)),
            "file_html": str((f.with_suffix(".html")).relative_to(REPO))
                         if f.with_suffix(".html").exists() else "",
            "tieu_de": tieu_de, "ngay": ngay, "tuoi_ngay": tuoi,
            "chu_de": _chu_de(tieu_de, vb), "so_nguon": so_muc,
            "pmids": pmids, "dois": dois,
        })
    return ban_ghi


def main() -> int:
    ap = argparse.ArgumentParser(description="Sổ đăng ký bài tổng thuật")
    ap.add_argument("--qua-han", type=int, default=90,
                    help="ngưỡng ngày coi là cần rà lại (mặc định 90)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not THU_MUC.exists():
        print("✗ Chưa có thư mục bài tổng thuật.")
        return 1
    bg = quet()
    SO.write_text(json.dumps({"cap_nhat": datetime.now().isoformat(timespec="seconds"),
                              "bai": bg}, ensure_ascii=False, indent=2),
                  encoding="utf-8", newline="\n")
    if a.json:
        print(json.dumps(bg, ensure_ascii=False, indent=2))
        return 0
    if not bg:
        print("(chưa có bài tổng thuật nào)")
        return 0
    print(f"SỔ ĐĂNG KÝ BÀI TỔNG THUẬT — {len(bg)} bài\n")
    for b in bg:
        cd = ", ".join(b["chu_de"]) or "chưa khớp chủ đề danh bạ"
        cu = "  ⚠ QUÁ HẠN RÀ LẠI" if b["tuoi_ngay"] > a.qua_han else ""
        print(f"• {b['tieu_de'][:78]}")
        print(f"  {b['ngay']} ({b['tuoi_ngay']} ngày) · {b['so_nguon']} nguồn · "
              f"{len(b['pmids'])} PMID · chủ đề: {cd}{cu}")
    qh = [b for b in bg if b["tuoi_ngay"] > a.qua_han]
    print(f"\n{len(qh)}/{len(bg)} bài quá {a.qua_han} ngày — cần rà lại nguồn mới hơn.")
    print("Sổ chỉ ĐO tuổi và ghi định danh; KHÔNG tự sửa bài. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
