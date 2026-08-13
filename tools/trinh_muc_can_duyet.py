#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHUẨN BỊ hồ sơ cho bác sĩ duyệt các mục 'Áp dụng ngay' trên chứng cứ yếu.

Công cụ này làm HẾT phần máy làm được, rồi DỪNG:
  • gom mọi mục bị cổng `--strict-sources` chặn
  • đọc `design`, `gradeSource`, `journal`, `pmid/doi` của từng mục
  • PHÂN NHÓM SƠ BỘ: quy phạm (guideline/nhãn thuốc) vs chứng cứ yếu thật
  • dựng bảng để bác sĩ đọc và quyết

Nó KHÔNG sửa file, KHÔNG đổi `decision`, KHÔNG đổi `gradeLevel`.

VÌ SAO KHÔNG TỰ QUYẾT — lý do an toàn, không phải kỹ thuật
===========================================================
73 mục bị chặn thuộc hai nhóm NGƯỢC NHAU về cách sửa:

  NHÓM QUY PHẠM — guideline chính thức (AGS Beers · NICE · ADA · AASLD · APASL ·
  IHS · EAN…) và nhãn thuốc FDA. Chúng mang `gradeLevel:'na'` KHÔNG PHẢI vì yếu,
  mà vì nguồn không dùng thang GRADE. Hạ `decision` của một CHỐNG CHỈ ĐỊNH
  (vd peginterferon ở xơ gan mất bù) hay một liều theo CrCl của nhãn FDA xuống
  "cân nhắc" là LÀM GIẢM AN TOÀN — đúng thứ cổng sinh ra để ngăn.

  NHÓM YẾU THẬT — tổng quan tường thuật, thư gửi toà soạn, cohort nhỏ, Cochrane
  tự chấm GRADE thấp. Ở đây hạ `decision` mới đúng.

Phân nhóm sơ bộ dưới đây dựa trên `design` + `gradeSource` — đủ để bác sĩ đọc
nhanh, KHÔNG đủ để tự động hoá. Một nhãn `design` là chuỗi tự do; đã đo được
đường lách: chỉ cần đặt chữ "Guideline" ở đầu là một văn bản đồng thuận trông
như nguồn quy phạm. Vì vậy máy đề xuất, bác sĩ phán quyết.

Dùng:
    python3 tools/trinh_muc_can_duyet.py                 # toàn kho
    python3 tools/trinh_muc_can_duyet.py --dashboard <tên>  # một bản
    python3 tools/trinh_muc_can_duyet.py --md <file.md>   # xuất bảng để đọc/in
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"

# Dấu hiệu nguồn QUY PHẠM. Cố ý KHÔNG dùng để tự quyết — chỉ để xếp thứ tự đọc.
QUY_PHAM = re.compile(
    r"guideline|khuyến cáo|nhãn thuốc|drug label|prescribing information|"
    r"beers|nice|kdigo|gold|gina|idsa|eular|acr|aasld|easl|apasl|adа|ada|"
    r"uspstf|who|fda|ema|mhra|ihs|ean|acc/aha|esc", re.I)
YEU_THAT = re.compile(
    r"narrative review|tổng quan tường thuật|letter|thư gửi|editorial|xã luận|"
    r"case report|báo cáo ca|consensus|đồng thuận|expert opinion", re.I)


def nap_vd():
    p = DASH / "tools" / "verify_dashboard.py"
    spec = importlib.util.spec_from_file_location("vd_trinh", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def thu_thap(vd, files: list[Path]) -> list[dict]:
    ra: list[dict] = []
    for f in files:
        html = f.read_text(encoding="utf-8", errors="replace")
        db = vd.extract_data_block(html)
        if not db:
            continue
        items = vd.split_items(db)
        errs, _w, _o = vd.strict_source_checks(db, items)
        bi_chan = {m.group(1) for e in errs
                   if (m := re.match(r"\[(ITEM-\d+)\]", e)) and "decision='apply'" in e}
        if not bi_chan:
            continue
        for ch in items:
            iid = vd.field(ch, "id")
            if iid not in bi_chan:
                continue
            ra.append({
                "dashboard": f.name,
                "id": iid,
                "tieu_de": (vd.field(ch, "title") or "")[:96],
                "design": vd.field(ch, "design") or "",
                "grade": vd.field(ch, "gradeLevel") or "",
                "grade_src": (vd.field(ch, "gradeSource") or "")[:70],
                "pmid": vd.field(ch, "pmid") or "",
                "doi": (vd.field(ch, "doi") or "")[:44],
            })
    return ra


def phan_nhom(m: dict) -> str:
    van = f"{m['design']} {m['grade_src']}"
    if YEU_THAT.search(van):
        return "YẾU THẬT"
    if QUY_PHAM.search(van):
        return "QUY PHẠM?"
    return "CHƯA RÕ"


def main() -> int:
    ap = argparse.ArgumentParser(description="Chuẩn bị hồ sơ mục cần bác sĩ duyệt")
    ap.add_argument("--dashboard", help="chỉ một dashboard (khớp tên gần đúng)")
    ap.add_argument("--md", help="ghi bảng ra file markdown")
    a = ap.parse_args()

    files = sorted(DASH.glob("WebDashboard_*.html"))
    if a.dashboard:
        files = [f for f in files if a.dashboard.lower() in f.name.lower()]
        if not files:
            print(f"✗ Không thấy dashboard khớp '{a.dashboard}'")
            return 1

    muc = thu_thap(nap_vd(), files)
    if not muc:
        print("🟢 Không có mục nào bị cổng nguồn chặn.")
        return 0

    from collections import Counter
    nhom = Counter(phan_nhom(m) for m in muc)
    dong = [
        "# Mục 'Áp dụng ngay' trên chứng cứ yếu — CẦN BÁC SĨ DUYỆT", "",
        f"Tổng **{len(muc)} mục** trên **{len({m['dashboard'] for m in muc})} dashboard**.", "",
        "| Nhóm sơ bộ | Số mục | Cách sửa ĐÚNG |",
        "|---|---:|---|",
        f"| QUY PHẠM? | {nhom.get('QUY PHẠM?', 0)} | khai `normativeBasis`, **GIỮ** `decision` |",
        f"| YẾU THẬT | {nhom.get('YẾU THẬT', 0)} | **HẠ** `decision` → consider/notyet |",
        f"| CHƯA RÕ | {nhom.get('CHƯA RÕ', 0)} | bác sĩ đọc nguồn rồi xếp nhóm |",
        "",
        "> **TUYỆT ĐỐI không nâng `gradeLevel`** — nâng mức cho nguồn không phân hạng",
        "> là lỗi tự gán mức (R4 của `tham-dinh-dau-ra`).",
        "",
    ]
    for dash in sorted({m["dashboard"] for m in muc}):
        ms = [m for m in muc if m["dashboard"] == dash]
        dong += [f"## {dash}  ({len(ms)} mục)", "",
                 "| Mục | Nhóm | Thiết kế | GRADE | Nguồn phân hạng | PMID/DOI | Tiêu đề |",
                 "|---|---|---|---|---|---|---|"]
        for m in ms:
            tv = m["pmid"] or m["doi"] or "—"
            dong.append(f"| {m['id']} | {phan_nhom(m)} | {m['design'][:26]} | "
                        f"{m['grade']} | {m['grade_src'][:34]} | {tv} | {m['tieu_de'][:56]} |")
        dong.append("")

    ket = "\n".join(dong)
    if a.md:
        Path(a.md).write_text(ket + "\nCần bác sĩ kiểm chứng.\n", encoding="utf-8")
        print(f"✓ Đã ghi {len(muc)} mục ra {a.md}")
    else:
        print(ket)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
