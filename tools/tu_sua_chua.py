#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TỰ SỬA CHỮA — vá mọi lỗi MÁY MÓC của hệ cập nhật chứng cứ, không cần bác sĩ.

RANH GIỚI (đọc trước khi thêm bất cứ gì vào file này)
======================================================
Công cụ này CHỈ tự sửa những thứ có MỘT đáp án đúng xác định được bằng máy:
skill lệch bản, sản phẩm phái sinh thiếu, mốc chuẩn kho công cụ lệch, cấu hình
gọi nhầm interpreter, danh mục tra cứu cũ.

Nó TUYỆT ĐỐI KHÔNG tự sửa NỘI DUNG Y KHOA. Cụ thể, ba việc sau đây bị CẤM tự
động, vĩnh viễn:

  1. Đổi `decision` của một mục chứng cứ (apply / consider / notyet).
  2. Đổi `gradeLevel` hoặc bất kỳ phân hạng nào của nguồn.
  3. Quyết định bản nào đúng khi hai dashboard nói ngược nhau.

VÌ SAO CẤM — đây không phải sự thận trọng thừa:
73 mục đang khai "Áp dụng ngay" trên chứng cứ yếu thuộc HAI nhóm ngược nhau.
Nhóm QUY PHẠM (guideline chính thức, nhãn thuốc FDA) mang `gradeLevel:'na'` vì
nguồn KHÔNG dùng thang GRADE — hạ `decision` của một CHỐNG CHỈ ĐỊNH hay liều
theo CrCl xuống "cân nhắc" là LÀM GIẢM AN TOÀN. Nhóm YẾU THẬT thì ngược lại,
phải hạ. Máy không phân biệt được hai nhóm này một cách đáng tin, và đoán sai
theo hướng nào cũng gây hại cho người bệnh.

Nâng `gradeLevel` còn tệ hơn: đó là lỗi TỰ GÁN MỨC (R4 của `tham-dinh-dau-ra`).

Nên với nội dung y khoa, công cụ này chỉ CHUẨN BỊ (phân loại, gom bằng chứng,
dựng đề xuất) rồi DỪNG ở bác sĩ — đúng Cổng A/B mà chính bác sĩ đặt ra.

Dùng:
    python3 tools/tu_sua_chua.py            # xem trước, không ghi gì
    python3 tools/tu_sua_chua.py --ap-dung  # tự sửa phần máy móc
    python3 tools/tu_sua_chua.py --im-khi-on  # chỉ nói khi có việc (hook)

Mã thoát: 0 = không còn việc máy · 1 = còn việc máy chưa sửa · 2 = có việc CẦN BÁC SĨ.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable


def chay(lenh: list[str], nhan: str) -> tuple[int, str]:
    try:
        r = subprocess.run(lenh, cwd=REPO, capture_output=True, text=True, timeout=900)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return 99, f"{nhan}: không chạy được ({e})"


# ---------------------------------------------------------------------------
# Các việc MÁY MÓC — mỗi việc: (nhãn, lệnh kiểm, lệnh sửa hoặc None)
# ---------------------------------------------------------------------------
VIEC_MAY = [
    ("Skill đang chạy lệch nguồn",
     [PY, "tools/dong_bo_skill.py", "--im-khi-on"],
     [PY, "tools/dong_bo_skill.py", "--ap-dung"]),
    ("Kho plugin/skill thiếu so với mốc",
     [PY, "tools/kiem_plugin_day_du.py", "--im-khi-on"],
     None),                      # cài lại plugin cần mạng + quyết định của bác sĩ
    ("Nguồn chứng cứ có thật không",
     [PY, "tools/kiem_nguon_that.py", "--nhanh", "--im-khi-on"],
     None),                      # cấu hình secrets — không tự điền
]


def id_muc_apply(dau_ra: str) -> set[str]:
    """Các ITEM-id bị cổng chặn vì `decision='apply'` — ĐẾM MỤC, KHÔNG ĐẾM DÒNG.

    Một mục có thể sinh HAI dòng lỗi (vừa "gradeLevel='na'" vừa "chỉ dựa Consensus").
    Đo thật 13/08: 64 dòng nhưng chỉ 49 mục ⇒ bản cũ dùng `out.count(...)` đã phóng
    đại khối lượng việc của bác sĩ 31%. Con số thổi phồng trong bản báo việc cũng là
    nói sai, và nó khiến người ta hoãn một việc thật ra nhỏ hơn tưởng.
    """
    import re as _re
    return {m.group(1) for dong in dau_ra.splitlines()
            if "decision='apply'" in dong and (m := _re.search(r"\[(ITEM-\d+)\]", dong))}


def phai_sinh_lech() -> tuple[list[str], list[str]]:
    """(thiếu bản Word, bản Word cũ hơn dashboard).

    GHÉP TÊN THEO CẢ HAI DẠNG — đây là chỗ đã đo sai HAI LẦN trong ngày 13/08.
    Sản phẩm phái sinh sinh ra theo hai quy ước tên khác nhau tuỳ thời điểm:
        WebDashboard_EBM_<chủ-đề>_<ngày>_TaiLieuChiTiet.docx   (giữ nguyên tiền tố)
        <chủ-đề>_<ngày>_TaiLieuChiTiet.docx                    (đã bỏ tiền tố)
    Chỉ khớp một dạng thì 14 bản CÓ ĐỦ file bị báo là "thiếu Word" — một báo động
    giả đủ sức đẩy người ta đi dựng lại 14 tài liệu vốn đã tồn tại. Gom logic vào
    một chỗ để lần sau không ai đo lại bằng tay rồi sai y hệt.
    """
    D = REPO / "EBM-Dashboards"
    DER = D / "derivatives"
    if not DER.is_dir():
        return [], []
    import re
    docx = list(DER.glob("*.docx"))
    thieu, cu = [], []
    for f in sorted(D.glob("WebDashboard_*.html")):
        goc = re.sub(r"\.html$", "", f.name)
        ngan = re.sub(r"^WebDashboard_EBM_(VanDeCuThe_)?", "", goc)
        co = [p for p in docx if p.name.startswith(goc) or p.name.startswith(ngan)]
        if not co:
            thieu.append(ngan)
        elif max(p.stat().st_mtime for p in co) < f.stat().st_mtime - 60:
            cu.append(ngan)
    return thieu, cu


def viec_can_bac_si() -> list[str]:
    """Đếm các việc CHỈ bác sĩ quyết được. Chỉ ĐO và BÁO, không bao giờ sửa."""
    ra: list[str] = []

    # (a) Mục 'apply' trên chứng cứ yếu — cần phân loại quy phạm vs yếu thật
    vd = REPO / "EBM-Dashboards/tools/verify_dashboard.py"
    if vd.exists():
        # VÁ 13/08/2026 — ĐẾM MỤC, KHÔNG ĐẾM DÒNG LỖI. Bản cũ dùng
        # out.count("decision='apply'"), mà MỘT mục có thể sinh HAI dòng (vừa
        # "gradeLevel='na'" vừa "chỉ dựa Consensus"). Đo thật: 64 dòng nhưng chỉ 49
        # mục — phóng đại khối lượng việc của bác sĩ 31%. Một con số thổi phồng trong
        # bản báo việc cũng là nói sai, và nó khiến người ta hoãn một việc thật ra
        # nhỏ hơn tưởng.
        muc: set[tuple[str, str]] = set()
        d = 0
        for f in sorted((REPO / "EBM-Dashboards").glob("WebDashboard_*.html")):
            rc, out = chay([PY, str(vd), str(f), "--strict-sources"], f.name)
            ids = id_muc_apply(out)
            muc |= {(f.name, i) for i in ids}
            d += 1 if ids else 0
        n = len(muc)
        if n:
            ra.append(f"{n} mục khai 'Áp dụng ngay' trên chứng cứ yếu/không phân hạng, "
                      f"trên {d} dashboard — phải phân loại NGUỒN QUY PHẠM (khai "
                      f"normativeBasis, GIỮ decision) vs CHỨNG CỨ YẾU THẬT (hạ decision). "
                      f"Máy không phân biệt đáng tin được.")

    # (a-bis) Sản phẩm phái sinh thiếu/tụt hậu. KHÔNG tự xuất lại ở đây: một lượt
    # xuất đi mạng và mất vài phút, không hợp với chốt lúc mở phiên; và với bản còn
    # mục 'apply' chờ duyệt thì cổng sẽ chặn xuất — đúng như thiết kế.
    thieu, cu = phai_sinh_lech()
    if thieu:
        ra.append(f"{len(thieu)} dashboard CHƯA có bản Word — chạy "
                  f"`tools/xuat_goi_cap_nhat.py <file>.html --online`.")
    if cu:
        ra.append(f"{len(cu)} dashboard có bản Word/PDF CŨ HƠN dashboard "
                  f"({', '.join(x[:30] for x in cu[:3])}) — bác sĩ đang đọc bản lỗi thời; "
                  f"xuất lại được ngay khi các mục 'apply' của bản đó được duyệt xong.")

    # (b) Hai bản nói ngược nhau
    dk = REPO / "tools/dang_ky_chu_de.py"
    if dk.exists():
        _, out = chay([PY, str(dk)], "dang_ky_chu_de")
        import re
        m = re.search(r"(\d+)\s+MỤC HAI BẢN NÓI NGƯỢC NHAU", out)
        if m and int(m.group(1)):
            ra.append(f"{m.group(1)} mục hai bản cùng chủ đề nói ngược nhau — "
                      f"bác sĩ quyết bản nào đúng. Nâng decision là làm khuyến cáo "
                      f"MẠNH hơn, không được tự động.")
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Tự sửa lỗi máy móc của hệ chứng cứ")
    ap.add_argument("--ap-dung", action="store_true", help="thật sự sửa")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có việc")
    ap.add_argument("--bo-qua-lam-sang", action="store_true",
                    help="không chạy phần đo việc cần bác sĩ (nhanh hơn, cho hook)")
    a = ap.parse_args()

    con_lai, da_sua = [], []
    for nhan, lenh_kiem, lenh_sua in VIEC_MAY:
        rc, _ = chay(lenh_kiem, nhan)
        if rc == 0:
            continue
        if a.ap_dung and lenh_sua:
            rc2, _ = chay(lenh_sua, nhan)
            rc3, _ = chay(lenh_kiem, nhan)
            (da_sua if rc3 == 0 else con_lai).append(nhan)
        else:
            con_lai.append(nhan + ("" if lenh_sua else "  (cần bác sĩ, không tự sửa được)"))

    bac_si = [] if a.bo_qua_lam_sang else viec_can_bac_si()

    if a.im_khi_on and not con_lai and not da_sua and not bac_si:
        return 0

    print("TỰ SỬA CHỮA — hệ cập nhật chứng cứ")
    if da_sua:
        print("\n✓ ĐÃ TỰ SỬA:")
        for x in da_sua:
            print(f"   • {x}")
    if con_lai:
        print("\n▸ CÒN VIỆC MÁY:")
        for x in con_lai:
            print(f"   • {x}")
        if not a.ap_dung:
            print("   (thêm --ap-dung để tự sửa)")
    if bac_si:
        print("\n🔴 CẦN BÁC SĨ — máy KHÔNG được tự quyết:")
        for x in bac_si:
            print(f"   • {x}")
        print("\n   Đây không phải hạn chế kỹ thuật mà là ranh giới an toàn: hạ nhầm một")
        print("   chống chỉ định, hay tự nâng phân hạng cho nguồn không dùng GRADE, đều")
        print("   gây hại trực tiếp cho người bệnh.")

    if not con_lai and not bac_si:
        print("\n🟢 Không còn việc nào.")
    return 2 if bac_si else (1 if con_lai else 0)


if __name__ == "__main__":
    raise SystemExit(main())
