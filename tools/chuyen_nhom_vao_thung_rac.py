#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chuyen_nhom_vao_thung_rac.py — NÚT cho bác sĩ: chuyển một nhóm «_Cho thung rac…» của EndNote vào THÙNG RÁC (19/10/2026).

Bác sĩ 19/10/2026: «Hãy làm tất cả 6 việc giúp tôi» (việc 5). Claude gom bản ghi bác sĩ đã quyết bỏ vào nhóm tạm
«_Cho thung rac …» nhưng KHÔNG tự chuyển vào thùng rác (thao tác của bác sĩ). Nút này rút việc đó còn ba thao tác:

  1. Liệt kê các nhóm tên bắt đầu «_Cho thung rac» kèm số bản ghi và vài tiêu đề; bác sĩ chọn nhóm, gõ «y» xác nhận.
  2. Công cụ đưa EndNote lên trước và CHỈ HIỆN đúng các bản ghi của nhóm (`show records in` + `highlight records in`).
  3. Bác sĩ bấm vào danh sách → ⌘A → References → «Move References to Trash» (thao tác chuẩn của EndNote — vào THÙNG RÁC,
     khôi phục được bằng «Restore to Library»). Nhấn Enter ⇒ công cụ đọc `sdb.eni` (mode=ro) và báo từng bản ghi đã vào thùng
     rác hay chưa.

KHÔNG BAO GIỜ gọi `delete record` (đo 19/10/2026: lệnh AppleScript này xoá HẲN, không vào thùng rác). Công cụ không bấm menu
thay bác sĩ: mục «Move References to Trash» chỉ bật khi danh sách có tiêu điểm bàn phím, GUI scripting không bảo đảm đúng chỗ.

Chạy: bấm đúp `Chuyen Nhom Vao Thung Rac.command` ở gốc repo, hoặc `python3 tools/chuyen_nhom_vao_thung_rac.py`
(`--liet-ke` chỉ liệt kê; `--kiem "<tên nhóm>"` chỉ kiểm). Mã thoát 0 xong · 1 còn bản ghi chưa vào thùng rác · 2 không làm được.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, GOC / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def nhom_cho(ten_cac_nhom: list[str], tien_to: str) -> list[str]:
    """Tên nhóm chờ thùng rác (giữ thứ tự, bỏ trùng)."""
    return [t for t in dict.fromkeys(ten_cac_nhom) if t.startswith(tien_to)]


def tom_tat(sk, thu_vien: Path, rec: list[int], so_mau: int = 5) -> tuple[dict, list[str]]:
    """(trạng thái thùng rác, vài tiêu đề mẫu) của các bản ghi — đọc cơ sở dữ liệu, không qua giao diện."""
    tt = sk.kiem_thung_rac(thu_vien, rec)
    kn = sk._ket_noi(thu_vien)
    try:
        mau = [((kn.execute("SELECT title FROM refs WHERE id = ?", (r,)).fetchone() or [""])[0] or "")[:90]
               for r in rec[:so_mau]]
    finally:
        kn.close()
    return tt, mau


def bao_cao(tt: dict) -> tuple[int, str]:
    """(mã thoát, dòng báo) sau khi bác sĩ bấm — chỉ «đã vào thùng rác» mới là xong."""
    vao, con, mat = (len(tt.get(k) or []) for k in ("da_vao_thung_rac", "con_o_thu_vien", "khong_con_hang"))
    dong = f"✓ đã vào thùng rác: {vao}"
    if con:
        dong += f" · ⚠ CÒN ở thư viện: {con} (recNum {', '.join(map(str, tt['con_o_thu_vien'][:10]))})"
    if mat:
        dong += f" · ⚪ không còn trong cơ sở dữ liệu: {mat} (thùng rác đã được dọn hẳn?)"
    return (0 if not con else 1), dong


def hien_cho_bac_si(en, ids: list[str]) -> None:
    """Đưa EndNote lên trước, CHỈ hiện và tô sáng các bản ghi này. Không xoá, không bấm menu."""
    en._chay('activate\nset ids to items 2 thru -1 of argv\nshow records in ids in window (item 1 of argv)\n'
             'highlight records in ids in window (item 1 of argv)', en.ten, *ids)


def main(argv: list[str] | None = None, nhap=input) -> int:
    ap = argparse.ArgumentParser(description="Chuyển nhóm «_Cho thung rac…» của EndNote vào thùng rác (bác sĩ bấm)")
    ap.add_argument("--liet-ke", action="store_true", help="chỉ liệt kê nhóm chờ")
    ap.add_argument("--kiem", metavar="TEN_NHOM", help="chỉ kiểm nhóm này đã vào thùng rác chưa")
    a = ap.parse_args(argv)
    sk = _nap("_sk_cntr", "endnote_suc_khoe.py")
    nec = _nap("_nec_cntr", "nap_endnote_chu_de.py")
    ch = nec.doc_cau_hinh()
    if not ch:
        print("⚪ chưa khai thư viện EndNote (~/.ebm-endnote.json)")
        return 2
    thu_vien = Path(ch["thu_vien"])
    try:
        en = nec.EndNoteMac(ch["ung_dung"], thu_vien)
    except nec.KhongChayDuoc as e:
        print(f"⚪ {e}")
        return 2
    if not en.dang_mo_dung_thu_vien():
        print(f"Mở thư viện {thu_vien.name} trong EndNote…")
        en.mo_thu_vien()
    ds = nhom_cho(en.ten_cac_nhom(), sk.TIEN_TO_NHOM_THUNG_RAC)
    if a.kiem:
        ds = [n for n in ds if n == a.kiem]
    if not ds:
        print("🟢 Không có nhóm «_Cho thung rac…» nào chờ.")
        return 0
    thong_tin = []
    for i, ten in enumerate(ds, 1):
        ids = en.thanh_vien_nhom(ten)
        rec = [r for r in (sk.so_rec(x) for x in ids) if r is not None]
        tt, mau = tom_tat(sk, thu_vien, rec)
        thong_tin.append((ten, ids, rec))
        print(f"\n[{i}] «{ten}» — {len(rec)} bản ghi · đã vào thùng rác {len(tt['da_vao_thung_rac'])} · "
              f"còn ở thư viện {len(tt['con_o_thu_vien'])}")
        for t in mau:
            print(f"      · {t}")
    if a.liet_ke:
        return 0
    if a.kiem:
        ma, dong = bao_cao(sk.kiem_thung_rac(thu_vien, thong_tin[0][2]))
        print(dong)
        return ma
    chon = nhap(f"\nChọn nhóm [1-{len(ds)}] (Enter = thoát): ").strip()
    if not chon.isdigit() or not 1 <= int(chon) <= len(ds):
        print("Thoát — không làm gì.")
        return 0
    ten, ids, rec = thong_tin[int(chon) - 1]
    if nhap(f"Gõ y để CHUẨN BỊ chuyển {len(rec)} bản ghi của «{ten}» vào thùng rác: ").strip().lower() != "y":
        print("Thoát — không làm gì.")
        return 0
    hien_cho_bac_si(en, ids)
    print(f"\nEndNote đang CHỈ hiện {len(rec)} bản ghi của «{ten}». Trong EndNote:\n"
          "  1. bấm vào một bản ghi trong danh sách\n  2. ⌘A (chọn hết)\n"
          "  3. References → Move References to Trash (xác nhận nếu EndNote hỏi)\n")
    nhap("Làm xong thì nhấn Enter để công cụ kiểm…")
    time.sleep(2)
    ma, dong = bao_cao(sk.kiem_thung_rac(thu_vien, rec))
    print(dong)
    if ma == 0:
        print(f"Nhóm «{ten}» giờ trống — muốn xoá nhóm: chọn nhóm → Groups → Delete Group (tuỳ chọn).")
    return ma


if __name__ == "__main__":
    sys.exit(main())
