#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI ĐÃ CHẤM MỨC NÀY? — soi từng `gradeLevel` xem có truy được về tổ chức chấm không.

VÌ SAO CÓ (14/08/2026)
======================
`gradeLevel` là thứ bác sĩ HÀNH ĐỘNG THEO. Đo toàn kho: **530 item có gradeLevel khác
'na', trong đó 249 (47%) không truy được về bất kỳ tổ chức nào đã chấm**:

  • **128 mục** lấy MÔ TẢ THIẾT KẾ làm lý do cho mức — "RCT đa trung tâm, mù đôi
    (chất lượng cao)" ⇒ `high`. Đó là tự chấm của người soạn, không phải phân hạng
    của nguồn. Cùng lỗi đã khiến `COPD_TimThanChuyenHoa ITEM-26` bị hạ ngày 13/08.
  • **103 mục** không nói ai chấm.
  • **18 mục** tự khai thẳng *"nguồn không nêu GRADE"* / *"không phân hạng GRADE"*
    mà VẪN mang mức `mod`/`low`.

Ca cụ thể cho thấy hậu quả: cùng DAPA-CKD, bản `BenhThanMan_CKD` 07/06 ghi `high`
(lý do: "RCT đa trung tâm, mù đôi") còn bản 13/08 ghi `na` — hai bản nói khác nhau về
CÙNG một thử nghiệm, và không bản nào trích được mức của một tổ chức có chấm.

CÁCH ĐO — VÀ CÁI BẪY ĐÃ VẤP
============================
Bản đo ĐẦU TIÊN của chính công cụ này dò tên tổ chức trong `gradeSource`, và đếm nhầm
18 mục có tên tổ chức trong câu **PHỦ ĐỊNH** ("CHƯA được AASLD đưa vào khuyến cáo",
"nguồn KHÔNG nêu GRADE") thành "đã có tổ chức chấm" — tức tạo dấu ✓ sai, đúng lỗi BH28.
Nên:
  • **Cổng** (`verify_dashboard.py --strict-sources`) chỉ kiểm trường KHAI BÁO `gradeBy`.
  • **Công cụ này** dùng từ khoá CHỈ để xếp thứ tự việc cho người đọc, và luôn in kèm
    nguyên văn `gradeSource` để bác sĩ tự phán. Nó KHÔNG tự điền `gradeBy`.

Dùng:
    python tools/kiem_phan_hang.py              # nhóm apply trước (nguy hiểm nhất)
    python tools/kiem_phan_hang.py --tat-ca     # cả mục không phải apply
    python tools/kiem_phan_hang.py --file F     # một dashboard

Mã thoát: 0 = mọi mục có gradeLevel đều đã khai `gradeBy` · 1 = còn mục chưa khai.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"

import importlib.util as _ilu_kph  # noqa: E402
_sp_kph = _ilu_kph.spec_from_file_location("_bst_kph", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst_kph = _ilu_kph.module_from_spec(_sp_kph)
_sp_kph.loader.exec_module(_bst_kph)

# CHỈ để xếp thứ tự việc cho người đọc — KHÔNG phải căn cứ của cổng.
TU_CHAM = ("đa trung tâm", "mù đôi", "mù người đánh giá", "chất lượng cao", "nhãn mở",
           "đánh giá vận hành", "nghiên cứu quan sát", "cỡ mẫu", "hồi cứu", "tiến cứu",
           "thiết kế thích nghi", "đoàn hệ", "cohort")
NOI_KHONG_CHAM = ("không nêu grade", "không phân hạng", "chưa phân hạng", "chưa được",
                  "chưa có", "không được", "chưa đưa vào", "nguồn không")


def _nap_vd():
    # VÁ 08/09/2026: lùi về bản git-vendor khi EBM-Dashboards vắng (mọi checkout
    # git-only) thay vì ném FileNotFoundError thô — xem
    # tools/ban_sao_tran.py::duong_cong_cu_pipeline.
    duong = _bst_kph.duong_cong_cu_pipeline("verify_dashboard.py", REPO)
    if duong is None:
        return None
    spec = importlib.util.spec_from_file_location("vd_phan_hang", duong)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _phan_nhom(grade_source: str) -> str:
    gs = (grade_source or "").lower()
    if not gs.strip():
        return "KHÔNG có gradeSource"
    if any(k in gs for k in NOI_KHONG_CHAM):
        return "TỰ KHAI nguồn KHÔNG chấm"
    if any(k in gs for k in TU_CHAM):
        return "Tự chấm theo THIẾT KẾ"
    return "Không rõ ai chấm"


def main() -> int:
    ap = argparse.ArgumentParser(description="Soi gradeLevel có truy được tổ chức chấm không")
    ap.add_argument("--tat-ca", action="store_true", help="kể cả mục không phải 'apply'")
    ap.add_argument("--file", help="chỉ một dashboard")
    ap.add_argument("--im-khi-on", action="store_true", help="không in gì khi đã đủ (hook)")
    a = ap.parse_args()

    vd = _nap_vd()
    if vd is None:
        if not a.im_khi_on:
            print("⚪ Không tìm thấy verify_dashboard.py ở EBM-Dashboards/tools/ lẫn bản "
                  "git-vendor — không dò được trên máy này.")
        return 0
    files = [Path(a.file)] if a.file else sorted(DASH.glob("WebDashboard_*.html"))
    thieu: list[tuple] = []
    tong_co_muc = 0
    for f in files:
        try:
            blk = vd.extract_data_block(f.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if not blk:
            continue
        for c in vd.split_items(blk):
            g = (vd.field(c, "gradeLevel") or "").strip()
            if not g or g == "na":
                continue
            tong_co_muc += 1
            if vd.field(c, "gradeBy"):
                continue
            dec = vd.field(c, "decision") or ""
            thieu.append((dec == "apply", f.name, vd.field(c, "id"), g, dec,
                          vd.field(c, "gradeSource") or ""))

    if a.im_khi_on and not thieu:
        return 0

    n_apply = sum(1 for t in thieu if t[0])
    print("=" * 70)
    print("  PHÂN HẠNG — AI ĐÃ CHẤM MỨC NÀY?")
    print("=" * 70)
    print(f"  {tong_co_muc} item có gradeLevel khác 'na' · {len(thieu)} CHƯA khai `gradeBy` "
          f"({n_apply} trong số đó là decision='apply')\n")
    if not thieu:
        print("  🟢 Mọi mức chứng cứ đều truy được về một tổ chức đã chấm.")
        return 0

    nhom = collections.Counter(_phan_nhom(t[5]) for t in thieu)
    for k, v in nhom.most_common():
        print(f"     {v:4d}  {k}")

    print("\n  🔴 NHÓM decision='apply' — bác sĩ làm theo NGAY, xử lý trước:")
    theo_file = collections.defaultdict(list)
    for la_apply, fn, iid, g, dec, gs in thieu:
        if la_apply or a.tat_ca:
            theo_file[fn].append((iid, g, dec, gs, la_apply))
    for fn in sorted(theo_file, key=lambda x: -sum(1 for r in theo_file[x] if r[4])):
        rows = theo_file[fn]
        if not a.tat_ca:
            rows = [r for r in rows if r[4]]
        if not rows:
            continue
        print(f"\n  ▸ {fn.replace('WebDashboard_EBM_', '')}")
        for iid, g, dec, gs, la in rows:
            print(f"      {iid:8} grade={g:5} dec={dec:9} [{_phan_nhom(gs)}]")
            # Dấu gạch chéo ngược trong phần biểu thức của f-string cũng là PEP 701
            # (3.12+). Nhấc ra biến để giữ đúng sàn 3.11 mà CLAUDE.md khai.
            gs_gon = re.sub(r"\s+", " ", gs)[:120]
            print(f"        gradeSource: {gs_gon}")

    print("\n" + "=" * 70)
    print("  CÁCH SỬA — hai đường, chọn theo SỰ THẬT của nguồn:")
    print("   (a) Nguồn CÓ chấm → khai `gradeBy: \"<tổ chức> <năm>\"` và trích nguyên văn")
    print("       mức đó vào `gradeSource` (vd 'KDIGO 2024, khuyến cáo 1A').")
    print("   (b) Nguồn KHÔNG chấm → đặt `gradeLevel: 'na'`. Mô tả thiết kế nghiên cứu")
    print("       KHÔNG phải phân hạng. Nếu mục đang 'apply' thì sau đó phải khai")
    print("       `normativeBasis` (nguồn quy phạm) hoặc hạ `decision` — quyết định của bác sĩ.")
    print("\n  Công cụ chỉ ĐO và XẾP VIỆC. Nhóm hiển thị ở trên là gợi ý ưu tiên dựa trên từ")
    print("  ngữ, KHÔNG phải phán quyết — luôn đọc nguyên văn `gradeSource` trước khi sửa.")
    print("  Cần bác sĩ kiểm chứng.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
