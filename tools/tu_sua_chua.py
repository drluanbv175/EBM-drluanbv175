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


def viec_can_bac_si() -> list[str]:
    """Đếm các việc CHỈ bác sĩ quyết được. Chỉ ĐO và BÁO, không bao giờ sửa."""
    ra: list[str] = []

    # (a) Mục 'apply' trên chứng cứ yếu — cần phân loại quy phạm vs yếu thật
    vd = REPO / "EBM-Dashboards/tools/verify_dashboard.py"
    if vd.exists():
        n = d = 0
        for f in sorted((REPO / "EBM-Dashboards").glob("WebDashboard_*.html")):
            rc, out = chay([PY, str(vd), str(f), "--strict-sources"], f.name)
            c = out.count("decision='apply'")
            n += c
            d += 1 if c else 0
        if n:
            ra.append(f"{n} mục khai 'Áp dụng ngay' trên chứng cứ yếu/không phân hạng, "
                      f"trên {d} dashboard — phải phân loại NGUỒN QUY PHẠM (khai "
                      f"normativeBasis, GIỮ decision) vs CHỨNG CỨ YẾU THẬT (hạ decision). "
                      f"Máy không phân biệt đáng tin được.")

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
