#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỔ ĐĂNG KÝ BÀI TỔNG THUẬT — đưa bài vào vòng sống của hệ (20/08/2026).

VÌ SAO CÓ
=========
Bài tổng thuật hiện là ẢNH TĨNH: không nằm trong hòm thư, không ai canh độ tươi,
không nối với bộ dò chứng-cứ-vượt-qua. Nó sẽ cũ đi IM LẶNG — đúng họ lỗi đã vá ở
dashboard (một sản phẩm không có ai canh thì với bác sĩ nó thành sai lúc nào không hay).

Tool quét `EBM-Dashboards/tong_thuat/*.md` → sổ máy-đọc `so-tong-thuat.json`:
tiêu đề · ngày · chủ đề khớp danh bạ · PMID/DOI trong bài · số nguồn.
Chỉ ĐỌC và GHI SỔ — không sửa bài, không phán nội dung.

SỔ NẰM TRONG CÂY ONEDRIVE DÙNG CHUNG Mac↔Windows (28/09/2026, BH126): nội dung sổ phải
là HÀM THUẦN của các tệp bài — hai máy quét cùng cây phải ra đúng cùng một chuỗi byte,
và không đổi thì KHÔNG ghi. Bản cũ ghi đường dẫn `\\` trên Windows, lưu `tuoi_ngay`
(đổi mỗi ngày) và `cap_nhat` (đổi mỗi giây) ⇒ mỗi lượt chạy trên bất kỳ máy nào cũng
viết lại cả tệp ⇒ bản sao xung đột OneDrive (20/09, 23/09, 28/09). Tuổi bài nay tính
LÚC ĐỌC từ `ngay` (`tuoi_ngay()` ở dưới; hòm thư tự tính tương tự).

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
from datetime import date
from pathlib import Path, PurePath

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


def duong_tuong_doi(f: PurePath, goc: PurePath) -> str:
    """Đường dẫn tương đối `goc`, LUÔN dấu `/` và chuẩn NFC — giống nhau trên Mac lẫn Windows.

    `str(f.relative_to(REPO))` ra `EBM-Dashboards\\tong_thuat\\…` trên Windows, `/` trên Mac ⇒
    hai máy ghi hai sổ khác nhau cho CÙNG một bài (BH126); dấu `\\` còn làm hỏng liên kết của
    hòm thư khi mở trên Mac. NFC vì tên tệp có dấu tiếng Việt có thể về dạng NFD trên macOS."""
    return unicodedata.normalize("NFC", f.relative_to(goc).as_posix())


def tuoi_ngay(b: dict, hom_nay: date | None = None) -> int | None:
    """Tuổi (ngày) của một bài, tính LÚC ĐỌC từ trường `ngay` — sổ KHÔNG lưu con số này
    (đổi mỗi ngày ⇒ sổ bị viết lại mỗi ngày trên mọi máy, BH126). `None` khi `ngay` hỏng."""
    try:
        return ((hom_nay or date.today()) - date.fromisoformat(b["ngay"])).days
    except (KeyError, TypeError, ValueError):
        return None


def quet() -> list[dict]:
    # Thứ tự theo TÊN tệp (so từng ký tự, như nhau trên mọi máy): `sorted()` trên Path và
    # glob của Windows không phân biệt hoa/thường, còn trên Mac thì có ⇒ hai máy có thể xếp
    # khác nhau / nhận khác nhau rồi thay nhau viết lại sổ.
    tep = [f for f in THU_MUC.glob("TT_*.md") if f.name.startswith("TT_") and f.name.endswith(".md")]
    ban_ghi = []
    for f in sorted(tep, key=lambda p: p.name):
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
        ban_ghi.append({
            "file_md": duong_tuong_doi(f, REPO),
            "file_html": duong_tuong_doi(f.with_suffix(".html"), REPO)
                         if f.with_suffix(".html").exists() else "",
            "tieu_de": tieu_de, "ngay": ngay,
            "chu_de": _chu_de(tieu_de, vb), "so_nguon": so_muc,
            "pmids": pmids, "dois": dois,
        })
    return ban_ghi


def ghi_so(bg: list[dict]) -> bool:
    """Ghi sổ CHỈ KHI nội dung đổi; trả True nếu đã ghi.

    Không dấu thời gian, không tuổi: sổ không đổi thì tệp không bị chạm, OneDrive không có gì
    để đồng bộ; hai máy cùng thấy một thay đổi thật thì cùng ghi ra MỘT chuỗi byte (BH126)."""
    moi = json.dumps({"bai": bg}, ensure_ascii=False, indent=2) + "\n"
    try:
        if SO.read_text(encoding="utf-8") == moi:
            return False
    except OSError:
        pass  # chưa có sổ / đọc không được ⇒ ghi mới
    SO.write_text(moi, encoding="utf-8", newline="\n")
    return True


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
    ghi_so(bg)
    if a.json:
        # Đầu ra màn hình (không phải sổ) giữ trường `tuoi_ngay` như trước cho người gọi cũ.
        print(json.dumps([dict(b, tuoi_ngay=tuoi_ngay(b)) for b in bg], ensure_ascii=False, indent=2))
        return 0
    if not bg:
        print("(chưa có bài tổng thuật nào)")
        return 0
    def qua_han(b: dict) -> bool:
        t = tuoi_ngay(b)
        return t is None or t > a.qua_han  # ngày hỏng ⇒ không biết tuổi ⇒ cần rà (BH08)

    print(f"SỔ ĐĂNG KÝ BÀI TỔNG THUẬT — {len(bg)} bài\n")
    for b in bg:
        cd = ", ".join(b["chu_de"]) or "chưa khớp chủ đề danh bạ"
        cu = "  ⚠ QUÁ HẠN RÀ LẠI" if qua_han(b) else ""
        t = tuoi_ngay(b)
        print(f"• {b['tieu_de'][:78]}")
        print(f"  {b['ngay']} ({'?' if t is None else t} ngày) · {b['so_nguon']} nguồn · "
              f"{len(b['pmids'])} PMID · chủ đề: {cd}{cu}")
    qh = [b for b in bg if qua_han(b)]
    print(f"\n{len(qh)}/{len(bg)} bài quá {a.qua_han} ngày — cần rà lại nguồn mới hơn.")
    print("Sổ chỉ ĐO tuổi và ghi định danh; KHÔNG tự sửa bài. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
