#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LÀN NHẬP TAY CÓ KỶ LUẬT cho văn bản Việt Nam — LÔ C PHA 4 (15/08/2026).

BYT / Cục Quản lý Dược / danh mục BHYT không có API ổn định — không vì thế mà
bỏ trống: đây là làn nhập THỦ CÔNG nhưng CHUẨN HOÁ, và là loại bản ghi DUY NHẤT
trong hệ được xác minh bởi NGƯỜI thay vì API (`verified_by_human=true`).

LUẬT CỨNG (P6):
  • TỪ CHỐI bản ghi thiếu SỐ HIỆU hoặc thiếu tệp/đường dẫn gốc — cấm mọi hình
    thức suy đoán số quyết định. Máy không bao giờ điền hộ hai trường này.
  • Tệp gốc lưu `vn-guidelines/docs/` (bác sĩ tự tải từ nguồn chính thức) hoặc
    URL chính thức; cả hai vắng ⇒ chặn.
  • Ghi vào `vn-guidelines/registry.json` (mảng `muc`), giữ nguyên schema sổ.

Dùng (bác sĩ chạy, mỗi tham số một trường bắt buộc):
  python3 tools/add_vn_source.py \
    --loai "Hướng dẫn chẩn đoán điều trị" --so-hieu "….QĐ-BYT" \
    --ngay 2024-01-01 --co-quan "Bộ Y tế" --chu-de "Đái tháo đường type 2" \
    --pham-vi "toàn quốc" --nguon "vn-guidelines/docs/<tệp>.pdf HOẶC URL chính thức" \
    --nguoi-nhap "BS Luân"
  python3 tools/add_vn_source.py --nhac-quy    # liệt kê mục treo quá 2 quý
  python3 tools/add_vn_source.py --self-test   # chứng minh validator CHẶN thiếu số hiệu
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
SO = GOC / "vn-guidelines" / "registry.json"
DOCS = GOC / "vn-guidelines" / "docs"


def kiem(ban_ghi: dict) -> list[str]:
    """Trả danh sách lý do TỪ CHỐI — rỗng là hợp lệ."""
    loi = []
    so = str(ban_ghi.get("so_quyet_dinh") or "").strip()
    if not so or so.startswith("[CẦN"):
        loi.append("THIẾU SỐ HIỆU văn bản — cấm suy đoán, phải chép từ văn bản gốc")
    ng = str(ban_ghi.get("ngay_ban_hanh") or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ng):
        loi.append(f"ngày ban hành phải YYYY-MM-DD (đang: {ng!r})")
    nguon = str(ban_ghi.get("nguon_goc") or "").strip()
    if not nguon:
        loi.append("THIẾU tệp/đường dẫn gốc")
    elif not nguon.startswith(("http://", "https://")):
        if not (GOC / nguon).exists():
            loi.append(f"tệp gốc không tồn tại: {nguon} — tải văn bản về "
                       f"vn-guidelines/docs/ trước khi nhập")
    for k in ("loai_van_ban", "co_quan", "chu_de", "pham_vi", "nguoi_nhap"):
        if not str(ban_ghi.get(k) or "").strip():
            loi.append(f"thiếu trường bắt buộc `{k}`")
    return loi


def _ghi(ban_ghi: dict, so_path: Path) -> None:
    du = json.loads(so_path.read_text(encoding="utf-8"))
    du.setdefault("muc", []).append(ban_ghi)
    du["_updated"] = date.today().isoformat()
    so_path.write_text(json.dumps(du, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")


def nhac_quy() -> int:
    du = json.loads(SO.read_text(encoding="utf-8"))
    treo = [m for m in du.get("muc", [])
            if "[CẦN XÁC NHẬN" in json.dumps(m, ensure_ascii=False)]
    print(f"NHẮC QUÝ — {len(treo)} mục còn [CẦN XÁC NHẬN TẠI ĐƠN VỊ]:")
    for m in treo:
        print(f"  ◌ {m.get('chu_de')}: {m.get('ten_van_ban','?')[:70]}")
    if treo:
        print("→ mục treo quá 2 quý nên được bác sĩ đối chiếu bản tại đơn vị "
              "hoặc đánh dấu không-áp-dụng kèm lý do.")
    return 0


def _self_test() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="vn-src-")) / "registry.json"
    tmp.write_text('{"muc": []}', encoding="utf-8")
    thieu = {"loai_van_ban": "Hướng dẫn", "so_quyet_dinh": "",
             "ngay_ban_hanh": "2024-01-01", "co_quan": "Bộ Y tế",
             "chu_de": "x", "pham_vi": "toàn quốc",
             "nguon_goc": "https://example.gov.vn/x", "nguoi_nhap": "test"}
    l1 = kiem(thieu)
    print("  ca THIẾU SỐ HIỆU →", "CHẶN ✓" if any("SỐ HIỆU" in x for x in l1) else "🔴 LỌT")
    thieu2 = {**thieu, "so_quyet_dinh": "00/TEST", "nguon_goc": ""}
    l2 = kiem(thieu2)
    print("  ca THIẾU TỆP GỐC →", "CHẶN ✓" if any("gốc" in x for x in l2) else "🔴 LỌT")
    du_du = {**thieu, "so_quyet_dinh": "00/TEST-TỔNG-HỢP",
             "nguon_goc": "https://example.gov.vn/x",
             "_ghi_chu": "bản ghi TỔNG HỢP CHO SELF-TEST, ghi vào sổ TẠM — không phải văn bản thật"}
    l3 = kiem(du_du)
    if not l3:
        _ghi({**du_du, "verified_by_human": False}, tmp)
        n = len(json.loads(tmp.read_text(encoding="utf-8"))["muc"])
        print(f"  ca ĐỦ TRƯỜNG → nhận vào sổ TẠM ({n} mục) ✓ — sổ thật KHÔNG bị đụng")
    ok = bool(l1) and bool(l2) and not l3
    print("🟢 self-test ĐẠT" if ok else "🔴 self-test TRƯỢT")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Nhập văn bản VN có kỷ luật")
    ap.add_argument("--loai", dest="loai_van_ban")
    ap.add_argument("--so-hieu", dest="so_quyet_dinh")
    ap.add_argument("--ngay", dest="ngay_ban_hanh")
    ap.add_argument("--co-quan", dest="co_quan")
    ap.add_argument("--chu-de", dest="chu_de")
    ap.add_argument("--ten", dest="ten_van_ban", default=None)
    ap.add_argument("--pham-vi", dest="pham_vi")
    ap.add_argument("--nguon", dest="nguon_goc",
                    help="đường dẫn tệp trong vn-guidelines/docs/ hoặc URL chính thức")
    ap.add_argument("--nguoi-nhap", dest="nguoi_nhap")
    ap.add_argument("--nhac-quy", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return _self_test()
    if a.nhac_quy:
        return nhac_quy()

    ban_ghi = {k: getattr(a, k) for k in
               ("loai_van_ban", "so_quyet_dinh", "ngay_ban_hanh", "co_quan",
                "chu_de", "ten_van_ban", "pham_vi", "nguon_goc", "nguoi_nhap")}
    loi = kiem(ban_ghi)
    if loi:
        print("🔴 TỪ CHỐI bản ghi:")
        for x in loi:
            print("  ✗ " + x)
        return 1
    DOCS.mkdir(exist_ok=True)
    ban_ghi.update({"verified_by_human": True, "ngay_nhap": date.today().isoformat(),
                    "trang_thai": "dung-duoc"})
    _ghi(ban_ghi, SO)
    print(f"✓ Đã ghi {ban_ghi['so_quyet_dinh']} vào vn-guidelines/registry.json "
          f"(verified_by_human=true, người nhập: {ban_ghi['nguoi_nhap']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
