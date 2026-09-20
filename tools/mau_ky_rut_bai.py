#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MẪU CHỜ KÝ cho sổ miễn trừ «thông báo rút bài là bản đính chính bị rút» (BH109, 20/09/2026).

Vì sao có: cổng `verify_dashboard.py` chặn nguồn có thông báo rút bài là MỘT BẢN ĐÍNH CHÍNH bị rút
với thông điệp «CẦN BÁC SĨ XEM» cho tới khi bác sĩ ký mục vào `EBM-Dashboards/rut-bai-da-xem-xet.json`.
Trước công cụ này, bác sĩ phải tự đọc terminal, tự chép khoá + tập thông báo, tự dựng cấu trúc JSON —
ba chỗ dễ sai, và chép sai tập thông báo làm miễn trừ không có hiệu lực (fail-closed, im lặng).

Công cụ này CHỈ chuẩn bị, KHÔNG BAO GIỜ ký:
  • đọc sổ xác minh nguồn, lấy mọi bản ghi mang cờ `sua_loi_bi_rut` mà CHƯA có mục ký hợp lệ;
  • ghi `EBM-Dashboards/rut-bai-da-xem-xet.cho-ky.json` (KHÁC file cổng đọc) — máy điền `khoa` và
    `thong_bao_ids`; để TRỐNG `da_xem_boi` · `ngay` · `ly_do` (phần thuộc thẩm quyền bác sĩ);
  • không bao giờ ghi hay sửa `rut-bai-da-xem-xet.json` — cổng chỉ đọc file đó, nên mẫu dù có chép
    nguyên xi cũng KHÔNG hợp lệ cho tới khi bác sĩ tự điền ba trường trống (đã có test khoá).

Dùng:
  python3 tools/mau_ky_rut_bai.py            # ghi mẫu + in hướng dẫn
  python3 tools/mau_ky_rut_bai.py --dem      # chỉ in số mục đang chờ ký (cho tu_de_xuat_viec)
Mã thoát: 0 = không có gì chờ ký · 1 = có mục chờ bác sĩ.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
DASH = GOC / "EBM-Dashboards"
SO_KY = "rut-bai-da-xem-xet.json"
MAU = "rut-bai-da-xem-xet.cho-ky.json"


def _nap(duong_dan: Path, ten: str):
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


def _cong_kiem_tra():
    """Cổng thật (bản nguồn trong git) — dùng ĐÚNG hàm mà cổng dùng để quyết «đã ký hợp lệ chưa»."""
    return _nap(GOC / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py",
                "vd_mau_ky")


def muc_cho_ky(dash: Path = DASH, doc_so=None, cong=None) -> list[dict]:
    """Các bản ghi sổ mang cờ đính-chính-bị-rút mà chưa có mục ký hợp lệ ở thư mục `dash`.

    `doc_so`/`cong` tiêm được để kiểm thử offline. Bản ghi nào không có `thong_bao_ids` bị BỎ QUA
    (không có dấu vân tay thì không thể ký — cổng cũng từ chối), nhưng được đếm ở `khong_ky_duoc`.
    """
    if doc_so is None:
        doc_so = _nap(GOC / "tools" / "so_xac_minh_nguon.py", "sx_mau_ky").doc_so
    cong = cong or _cong_kiem_tra()
    muc = ((doc_so() or {}).get("muc") or {})
    ra: list[dict] = []
    for khoa, bg in sorted(muc.items()):
        if not (bg.get("da_rut") and bg.get("sua_loi_bi_rut")):
            continue
        ids = sorted({str(x).strip().lower() for x in (bg.get("thong_bao_ids") or []) if str(x).strip()})
        if not ids:
            continue
        ban_ghi = {"khoa": khoa, "loai": bg.get("loai", ""), "gia_tri": bg.get("gia_tri", ""),
                   "tinh_trang": "retracted", "sua_loi_bi_rut": True, "thong_bao_ids": ids}
        # `duong_dan` chỉ dùng để xác định THƯ MỤC chứa sổ ký; tệp không cần tồn tại.
        if cong._da_xem_xet_thong_bao_dinh_chinh(str(dash / "a.html"), ban_ghi):
            continue
        ra.append({
            "khoa": khoa,
            "thong_bao_ids": ids,
            "da_xem_boi": "",
            "ngay": "",
            "ly_do": "",
            "_ngu_canh": {
                "tieu_de_bai": (bg.get("tieu_de") or "")[:160],
                "dashboard": sorted(x for x in (bg.get("cac_dashboard") or []) if not x.startswith("(")),
                "mo_bai": (f"https://pubmed.ncbi.nlm.nih.gov/{bg.get('gia_tri')}/"
                           if bg.get("loai") == "pmid" else f"https://doi.org/{bg.get('gia_tri')}"),
                "mo_thong_bao": [(f"https://pubmed.ncbi.nlm.nih.gov/{i}/" if i.isdigit()
                                  else f"https://doi.org/{i}") for i in ids],
                "nguon_xac_minh": bg.get("nguon_xac_minh") or "",
                "kiem_luc": (bg.get("kiem_rut_luc") or "")[:10],
            },
        })
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh MẪU CHỜ KÝ cho sổ miễn trừ rút bài (không bao giờ ký)")
    ap.add_argument("--dem", action="store_true", help="chỉ in số mục chờ ký")
    a = ap.parse_args()
    cho = muc_cho_ky()
    if a.dem:
        print(len(cho))
        return 1 if cho else 0
    if not cho:
        print("🟢 Không có nguồn nào đang chờ bác sĩ ký miễn trừ «đính chính bị rút».")
        return 0
    mau = {
        "_huong_dan": [
            "TỆP NÀY CHỈ LÀ MẪU — cổng KHÔNG đọc nó. Máy đã điền `khoa` và `thong_bao_ids` (dấu vân tay).",
            "Bước 1: mở `mo_bai` và từng `mo_thong_bao` trong `_ngu_canh`; đọc thông báo VÀ mọi Author "
            "Correction còn hiệu lực của bài — quyết định khuyến cáo có đổi không.",
            "Bước 2: nếu (và chỉ nếu) bác sĩ chấp nhận, điền `da_xem_boi` (tên), `ngay` (YYYY-MM-DD), "
            "`ly_do` (≥ 20 ký tự, nêu đã đọc gì và kết luận gì).",
            f"Bước 3: chép mục đã điền vào `EBM-Dashboards/{SO_KY}` dạng {{\"muc\": [ ... ]}} (bỏ `_ngu_canh`).",
            "Thêm/đổi một thông báo rút sau này ⇒ dấu vân tay lệch ⇒ cổng chặn lại. Không muốn miễn: "
            "giữ nguyên chặn, hoặc hạ `decision` của mục trong dashboard (thẩm quyền bác sĩ).",
        ],
        "muc": cho,
    }
    duong = DASH / MAU
    duong.write_text(json.dumps(mau, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"🟠 {len(cho)} nguồn CHỜ BÁC SĨ KÝ — mẫu ghi ở {duong.relative_to(GOC)}")
    for e in cho:
        nc = e["_ngu_canh"]
        print(f"  • {e['khoa']} — {nc['tieu_de_bai'][:70]}")
        print(f"      thông báo: {', '.join(e['thong_bao_ids'])}  ← dashboard: {', '.join(nc['dashboard'])}")
    print(f"Mẫu KHÔNG có hiệu lực: cổng chỉ đọc EBM-Dashboards/{SO_KY}. Máy không ký thay bác sĩ.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
