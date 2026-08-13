#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐĂNG KÝ CHỦ ĐỀ — bản nào là bản HIỆN HÀNH, và hai bản có nói ngược nhau không?

VÌ SAO CÓ (12/08/2026)
======================
Kho có 60 dashboard nhưng **8 chủ đề có nhiều hơn một bản** — suy tim tới 5 bản,
riêng loại "TongHop" đã 3 bản (04/08 · 05/08 · 11/08). Không có gì đánh dấu bản
nào còn hiệu lực, nên tại phòng khám bác sĩ có thể mở nhầm bản cũ.

Đo thật cho thấy hai mức rủi ro KHÁC NHAU, không được nói gộp:

  • **Thiếu** — bản mới bao trọn bản cũ rồi thêm nguồn. Ví dụ suy tim: bản 11/08
    chứa đủ 100% PMID của 04/08 và 05/08, thêm 12 nguồn mới, và KHÔNG mục nào đổi
    quyết định. Mở bản cũ thì thiếu thông tin, không phải nhận thông tin sai.
  • **NGƯỢC NHAU** — cùng một PMID mà hai bản kết luận khác nhau. Đo được **10 mục**
    như vậy, gồm những chỗ đáng lo: COPD PMID 27783918 đi từ `consider` sang
    `notyet` (oxy dài hạn), RA PMID 35081280 từ `apply` sang `consider` (cảnh báo
    JAK inhibitor). Đây mới là rủi ro thật: bác sĩ mở bản cũ sẽ đọc một kết luận
    mà bản mới đã bác.

Một phần mâu thuẫn do CHÍNH việc sửa dashboard ngày 12/08 gây ra: thêm
`normativeBasis` cho nguồn quy phạm ở bản 18/07 mà không áp cùng cách cho bản
11/08 cùng chủ đề ⇒ ICHD-3 (tiêu chuẩn phân loại chính thức của IHS) nay là
`apply` ở bản này và `consider` ở bản kia. Sửa một bản KHÔNG tự lan sang bản khác
cùng chủ đề — đó là khoảng trống công cụ này sinh ra để bịt.

GIỚI HẠN CÓ CHỦ Ý
  • Chỉ ĐO và BÁO. KHÔNG tự sửa dashboard, và tuyệt đối KHÔNG tự NÂNG `decision`
    (nâng làm một khuyến cáo mạnh lên — nguy hiểm hơn hạ, và là quyết định lâm
    sàng của bác sĩ).
  • "Bản hiện hành" suy từ ngày trong TÊN FILE. Đây là quy ước đặt tên của kho,
    không phải phán đoán về chất lượng nội dung.

Dùng:
    python tools/dang_ky_chu_de.py              # bảng chủ đề + mâu thuẫn
    python tools/dang_ky_chu_de.py --mau-thuan  # chỉ liệt kê mâu thuẫn

Mã thoát: 0 = không mâu thuẫn · 1 = có mâu thuẫn cần bác sĩ quyết.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import re
import sys
from pathlib import Path

# Windows: stdout mặc định là cp1252 → mọi print() tiếng Việt hoặc ký hiệu (✓ ⚠ →)
# ném UnicodeEncodeError và GIẾT tiến trình, thường SAU KHI công việc đã xong. Đo thật
# ngày 12/08/2026 trên dây chuyền cập nhật chứng cứ: bản Word 82 KB đã ghi ra đĩa nhưng
# tool thoát mã 1 ở đúng dòng print cuối ⇒ caller đọc mã thoát, tưởng hỏng, bỏ luôn 2
# bước sau. Cùng lớp lỗi đã vá cho tools/vietnamize/.
import sys as _sys_utf8
for _s in (_sys_utf8.stdout, _sys_utf8.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"

# Hậu tố mô tả "lát cắt" của cùng một chủ đề (bệnh kèm, đối tượng, tiên lượng…).
# Bỏ chúng đi để gom về chủ đề gốc.
HAU_TO = re.compile(
    r"_(TongHop|HopNhat|DieuTri|ChanDoan.*|TienLuong.*|DoiTuong.*|BenhKem.*|"
    r"ThuocBenhKem.*|TamThanKinh|NoiTiet|TimMach.*|Than|DaBenh.*)$")


def nap_vd():
    spec = importlib.util.spec_from_file_location(
        "vd_chu_de", DASH / "tools" / "verify_dashboard.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tach_ten(ten: str) -> tuple[str, str, str] | None:
    """Trả (lát_cắt, chủ_đề_gốc, ngày).

    PHÂN BIỆT HAI THỨ RẤT KHÁC NHAU — bản đầu của công cụ này gộp chúng làm một
    và suýt gây hại:

      • LÁT CẮT = tên đầy đủ bỏ ngày, vd "COPD_DoiTuongDacBiet_DaBenh".
        Hai file cùng lát cắt, khác ngày ⇒ đúng là PHIÊN BẢN NỐI TIẾP, bản mới
        thay bản cũ.
      • CHỦ ĐỀ GỐC = "COPD". Các lát cắt khác nhau của cùng chủ đề
        (COPD tổng quát · COPD ở đối tượng đặc biệt · COPD kèm tim mạch) là
        BỔ SUNG cho nhau, KHÔNG thay thế nhau.

    Gộp nhầm sẽ dán nhãn "đã có bản mới hơn" lên bản COPD tổng quát chỉ vì có một
    bản về đối tượng đặc biệt ra sau — khiến bác sĩ bỏ qua đúng bản mình cần. Đó
    là làm GIẢM an toàn, tức chính thứ công cụ này sinh ra để ngăn.
    """
    # VÁ 14/08/2026 — phần TÊN CHỦ ĐỀ nay là TUỲ CHỌN.
    # Bản cũ bắt buộc `<nhóm>_<chủ-đề>_<ngày>`, nên một file như
    # `WebDashboard_EBM_Uptodate_20260607.html` (không có phần chủ đề) KHÔNG khớp
    # và bị LOẠI IM LẶNG khỏi đăng ký chủ đề — vô hình luôn với phần dò mâu thuẫn.
    # Đo thật: 61/62 dashboard tách được, đúng 1 bản rơi ra mà không một dòng báo.
    # Không có gì báo lỗi, nên nó trông hệt như "đã kiểm hết".
    m = re.match(r"WebDashboard_EBM_(VanDeCuThe|Uptodate|CapNhatTuan|AnToanThuoc|"
                 r"CongCuKeDon)_(?:(.+?)_)?(\d{8})\.html$", ten)
    if not m:
        return None
    # Không có phần chủ đề → lấy chính tên NHÓM làm lát cắt (vd "Uptodate"),
    # để bản đó vẫn nằm trong đăng ký và vẫn được so mâu thuẫn.
    lat_cat = m.group(2) or m.group(1)
    goc = HAU_TO.sub("", lat_cat).split("_")[0]
    return lat_cat, goc, m.group(2)


def doc_muc(vd, p: Path) -> dict[str, list[tuple]]:
    """{pmid: [(decision, gradeLevel, normativeBasis, title), …]} — GIỮ MỌI item.

    VÁ 13/08/2026 — bản cũ trả `{pmid: tuple}` nên khi một dashboard có NHIỀU item
    cùng trích một PMID thì chỉ item CUỐI theo thứ tự file được giữ, các item trước
    bị bỏ IM LẶNG. Đó là chuyện bình thường, không phải bất thường: một guideline
    (vd KDIGO 2024) mang hàng chục khuyến cáo, mỗi khuyến cáo có `decision` riêng —
    đo được 21 ca như vậy trong kho.
    Hệ quả của bản cũ: phần so mâu thuẫn đem so một item TÙY Ý của bản này với một
    item TÙY Ý của bản kia, nên có thể tuyên bố "hai bản nói ngược nhau" trong khi
    chúng chỉ đang nói về HAI KHUYẾN CÁO KHÁC NHAU của cùng một tài liệu.
    Đo trên toàn kho: 3/224 PMID chung bị ảnh hưởng (1%), trong đó **2 nằm đúng
    trong danh sách mâu thuẫn đã trình bác sĩ** (BenhThanMan PMID 38490803,
    ViemGanB PMID 41186418). Nay giữ đủ để phân biệt được hai tình huống.
    """
    try:
        db = vd.extract_data_block(p.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return {}
    if not db:
        return {}
    out: dict[str, list[tuple]] = {}
    for c in vd.split_items(db):
        pm = vd.field(c, "pmid")
        if pm:
            out.setdefault(pm, []).append(
                (vd.field(c, "decision"), vd.field(c, "gradeLevel"),
                 vd.field(c, "normativeBasis"), (vd.field(c, "title") or "")[:58]))
    return out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Đăng ký chủ đề + phát hiện mâu thuẫn giữa các bản")
    ap.add_argument("--mau-thuan", action="store_true", help="chỉ in phần mâu thuẫn")
    a = ap.parse_args()

    vd = nap_vd()
    theo_lat_cat: dict[str, list[tuple[str, Path]]] = collections.defaultdict(list)
    theo_goc: dict[str, list[tuple[str, str, Path]]] = collections.defaultdict(list)
    for p in sorted(DASH.glob("WebDashboard_*.html")):
        r = tach_ten(p.name)
        if not r:
            continue
        lat_cat, goc, ngay = r
        theo_lat_cat[lat_cat].append((ngay, p))
        theo_goc[goc].append((ngay, lat_cat, p))

    # (1) PHIÊN BẢN NỐI TIẾP — cùng lát cắt, khác ngày. Đây mới là "bản cũ bị thay".
    nhieu_phien_ban = {k: sorted(v) for k, v in theo_lat_cat.items() if len(v) > 1}
    chi_thieu: list[tuple] = []
    for lc, v in nhieu_phien_ban.items():
        muc_moi = doc_muc(vd, v[-1][1])
        for ngay_cu, p_cu in v[:-1]:
            muc_cu = doc_muc(vd, p_cu)
            if muc_cu and not (set(muc_cu) - set(muc_moi)):
                chi_thieu.append((lc, ngay_cu, v[-1][0], len(set(muc_moi) - set(muc_cu))))

    # (2) MÂU THUẪN — so MỌI cặp bản trong cùng chủ đề gốc, kể cả khác lát cắt:
    # hai bản nói ngược nhau về cùng một PMID là vấn đề dù chúng bổ sung cho nhau.
    mau_thuan: list[tuple] = []
    khong_so_duoc: list[tuple] = []
    for goc, v in sorted(theo_goc.items()):
        if len(v) < 2:
            continue
        v = sorted(v)
        cache = {ngay: doc_muc(vd, p) for ngay, _lc, p in v}
        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                (n1, lc1, _), (n2, lc2, _) = v[i], v[j]
                m1, m2 = cache[n1], cache[n2]
                khac = []
                for pm in sorted(set(m1) & set(m2)):
                    a1, a2 = m1[pm], m2[pm]
                    # Chỉ so được TỰ ĐỘNG khi mỗi bên có ĐÚNG MỘT item cho PMID đó.
                    # Nhiều item = nhiều khuyến cáo khác nhau của cùng một tài liệu;
                    # ghép tuỳ tiện hai trong số đó rồi gọi là "nói ngược nhau" là
                    # BÁO ĐỘNG GIẢ — thứ đã được ghi là tệ hơn không kiểm.
                    if len(a1) > 1 or len(a2) > 1:
                        khong_so_duoc.append(
                            (goc, f"{lc1} ({n1})", f"{lc2} ({n2})", pm, len(a1), len(a2)))
                        continue
                    if a1[0][0] != a2[0][0]:
                        khac.append((pm, a1[0], a2[0]))
                if khac:
                    mau_thuan.append((goc, f"{lc1} ({n1})", f"{lc2} ({n2})", khac))

    if not a.mau_thuan:
        print("=" * 70)
        print("  ĐĂNG KÝ CHỦ ĐỀ")
        print("=" * 70)
        tong_file = sum(len(v) for v in theo_lat_cat.values())
        print(f"  {tong_file} dashboard · {len(theo_goc)} chủ đề gốc · "
              f"{len(theo_lat_cat)} lát cắt\n")

        print("  ── PHIÊN BẢN NỐI TIẾP (cùng lát cắt — bản mới THAY bản cũ) ──")
        if not nhieu_phien_ban:
            print("     (không có)\n")
        for lc, v in sorted(nhieu_phien_ban.items()):
            print(f"  ▸ {lc}")
            for i, (ngay, p) in enumerate(v):
                nhan = "◀ HIỆN HÀNH" if i == len(v) - 1 else "  đã bị thay"
                print(f"      {ngay}  {nhan}")
            print()

        print("  ── LÁT CẮT KHÁC NHAU CỦA CÙNG CHỦ ĐỀ (BỔ SUNG, không thay nhau) ──")
        for goc, v in sorted(theo_goc.items()):
            lc_set = {lc for _n, lc, _p in v}
            if len(lc_set) < 2:
                continue
            print(f"  ▸ {goc}: {len(lc_set)} lát cắt — cần đọc CẢ NHÓM, đừng bỏ bản cũ")
            for ngay, lc, _p in sorted(v):
                print(f"      {ngay}  {lc}")
            print()

    if chi_thieu and not a.mau_thuan:
        print("  ── Bản cũ CHỈ THIẾU, không nói sai (bản mới bao trọn) ──")
        for lc, cu, moi, them in chi_thieu:
            print(f"     {lc}: bản {cu} nằm gọn trong bản {moi} (+{them} nguồn mới)")
        print()

    print("=" * 70)
    if not mau_thuan:
        print("  🟢 KHÔNG có mục nào hai bản nói ngược nhau.")
        print("=" * 70)
        print("  Lưu ý: chỉ so các mục CÙNG PMID. Khác biệt về mục không có PMID")
        print("  (guideline chỉ có URL) không đo được ở đây.\n  Cần bác sĩ kiểm chứng.")
        return 0

    if khong_so_duoc:
        print(f"\n  ⚠ {len(khong_so_duoc)} PMID KHÔNG so tự động được — một tài liệu mang")
        print("     NHIỀU khuyến cáo, mỗi khuyến cáo có quyết định riêng. Ghép tuỳ tiện")
        print("     hai trong số đó rồi gọi là 'nói ngược nhau' là BÁO ĐỘNG GIẢ.")
        for goc, a, b, pm, n1, n2 in khong_so_duoc:
            print(f"     • {goc}: PMID {pm} — {a} có {n1} mục · {b} có {n2} mục → bác sĩ đọc tay")
    tong = sum(len(k[3]) for k in mau_thuan)
    print(f"  🔴 {tong} MỤC HAI BẢN NÓI NGƯỢC NHAU — cùng PMID, khác quyết định")
    print("=" * 70)
    print("  Đây là rủi ro thật: mở bản cũ sẽ đọc một kết luận mà bản mới đã bác.\n")
    for cd, cu, moi, khac in mau_thuan:
        print(f"  ▸ {cd}:  {cu}   ⟷   {moi}")
        for pm, c, m in khac:
            note = ""
            if m[2] and not c[2]:
                note = "  [bản mới có normativeBasis, bản cũ chưa]"
            elif c[2] and not m[2]:
                note = "  [bản CŨ có normativeBasis, bản mới CHƯA — nhiều khả năng bản mới " \
                       "chưa được áp cách sửa quy phạm]"
            print(f"      PMID {pm}: {c[0]!r} → {m[0]!r}{note}")
            print(f"        {m[3]}")
        print()
    print("  Công cụ này KHÔNG tự sửa và KHÔNG tự nâng decision — nâng làm một")
    print("  khuyến cáo MẠNH hơn, đó là quyết định lâm sàng của bác sĩ.")
    print("  Cần bác sĩ kiểm chứng.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
