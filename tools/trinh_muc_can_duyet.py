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

# ---------------------------------------------------------------------------
# VÁ 13/08/2026 — BẢN ĐẦU CỦA CHÍNH TOOL NÀY XẾP SAI, VÀ SAI THEO HƯỚNG NGUY HIỂM
# ---------------------------------------------------------------------------
# Bản đầu xét YEU_THAT trước, mà YEU_THAT khớp "consensus|đồng thuận". Trong dữ
# liệu thật, trường `design` gắn nhãn 'Consensus' cho CẢ những thứ này:
#     • cảnh báo HỘP ĐEN của FDA/EMA về JAK inhibitor (PMID 35081280)
#     • chống chỉ định + ngưỡng ngưng thuốc trên NHÃN THUỐC FDA của leflunomide
#     • bộ tiêu chí AGS Beers 2023 và STOPP/START v3
#     • tiêu chuẩn chẩn đoán GOLD, tiêu chuẩn phân loại ACR/EULAR 2010
# ⇒ cả 8 mục quy phạm đó rơi vào nhóm "nên HẠ decision". Hạ một cảnh báo hộp đen
# hay một chống chỉ định trên nhãn thuốc là LÀM GIẢM AN TOÀN — đúng thứ cổng sinh
# ra để ngăn. Đây là bằng chứng cụ thể vì sao lớp ngữ nghĩa KHÔNG được tự quyết.
#
# Sửa: xét TÍNH QUY PHẠM CỦA NGUỒN trước tính "thể loại văn bản", vì `gradeSource`
# mô tả NGUỒN THẬT còn `design` chỉ là nhãn tự do người soạn gõ vào.
NGUON_QUY_PHAM = re.compile(
    r"nhãn thuốc|drug label|prescribing information|boxed warning|hộp đen|"
    r"chống chỉ định|contraindication|regulatory|quản lý dược|cơ quan quản lý|"
    r"beers|stopp|start|tiêu chí|tiêu chuẩn chẩn đoán|tiêu chuẩn phân loại|"
    r"phân loại chính thức|official classification|khuyến cáo (eular|acr|esc|aha|ada)",
    re.I)
# Thể loại văn bản quy phạm (yếu hơn dấu hiệu nguồn ở trên, xét sau).
LOAI_QUY_PHAM = re.compile(
    r"guideline|khuyến cáo|nice|kdigo|gold|gina|idsa|eular|aasld|easl|apasl|"
    r"ada|uspstf|who|fda|ema|mhra|ihs|ean|acc/aha|esc", re.I)
# Dấu hiệu chứng cứ YẾU THẬT — KHÔNG còn gồm "consensus/đồng thuận" (xem trên).
YEU_THAT = re.compile(
    r"narrative review|tổng quan tường thuật|bài tổng quan|letter|thư gửi|"
    r"editorial|xã luận|case report|báo cáo ca|expert opinion|"
    r"đánh giá vận hành|không phải phân hạng chính thức|grade thấp|grade rất thấp",
    re.I)
DONG_THUAN = re.compile(r"consensus|đồng thuận|expert consensus", re.I)


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
    """Xếp sơ bộ MỘT mục. Thứ tự xét là phần quan trọng nhất của hàm này.

    NGUỒN quy phạm xét TRƯỚC thể loại văn bản, vì `gradeSource` mô tả nguồn thật
    còn `design` chỉ là nhãn tự do — và trong dữ liệu thật `design='Consensus'`
    đang mang cả nhãn thuốc FDA lẫn cảnh báo hộp đen (xem chú thích ở đầu file).
    """
    nguon = m["grade_src"] or ""
    van = f"{m['design']} {nguon}"

    # (1) Dấu hiệu NGUỒN quy phạm thắng mọi thứ khác.
    if NGUON_QUY_PHAM.search(nguon):
        return "QUY PHẠM?"
    # (2) Dấu hiệu yếu thật, đã bỏ 'consensus' khỏi nhóm này.
    if YEU_THAT.search(van):
        return "YẾU THẬT"
    # (3) Thể loại quy phạm (guideline/cơ quan) — yếu hơn (1) nhưng vẫn là quy phạm.
    if LOAI_QUY_PHAM.search(van):
        return "QUY PHẠM?"
    # (4) Đồng thuận chuyên gia THẬT — nhóm RIÊNG, cố ý không gộp vào "yếu thật".
    #     Một định nghĩa bệnh hay lộ trình quyết định của ACC không phải chứng cứ
    #     yếu; nó chỉ không dùng thang GRADE. Bác sĩ quyết từng mục.
    if DONG_THUAN.search(van):
        return "ĐỒNG THUẬN"
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
        f"| ĐỒNG THUẬN | {nhom.get('ĐỒNG THUẬN', 0)} | bác sĩ cân từng mục — KHÔNG hạ hàng loạt |",
        f"| YẾU THẬT | {nhom.get('YẾU THẬT', 0)} | **HẠ** `decision` → consider/notyet |",
        f"| CHƯA RÕ | {nhom.get('CHƯA RÕ', 0)} | bác sĩ đọc nguồn rồi xếp nhóm |",
        "",
        "> **TUYỆT ĐỐI không nâng `gradeLevel`** — nâng mức cho nguồn không phân hạng",
        "> là lỗi tự gán mức (R4 của `tham-dinh-dau-ra`).",
        ">",
        "> **Vì sao có nhóm ĐỒNG THUẬN riêng:** bản đầu của công cụ này gộp đồng thuận",
        "> vào 'yếu thật', khiến **cảnh báo hộp đen FDA về JAK inhibitor** và **chống chỉ",
        "> định leflunomide trên nhãn FDA** bị xếp vào nhóm 'nên hạ'. Hạ chúng là làm",
        "> GIẢM an toàn. Máy đề xuất, bác sĩ phán quyết.",
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
