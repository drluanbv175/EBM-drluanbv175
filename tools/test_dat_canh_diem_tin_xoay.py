#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho tools/dat_canh_diem_tin_xoay.py (12/09/2026).

Kiểm HÀNH VI thật: parse đúng cấu trúc file DAT-CANH-CHUNG-CU-MOI, xoay
vòng có wrap-around, reset khi tên file đổi, và TUYỆT ĐỐI không in phần
"Kết luận nguyên văn (abstract)" (R28/BH28 — không phán chiều)."""
from __future__ import annotations

import importlib.util as _ilu
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_spec = _ilu.spec_from_file_location("dat_canh_xoay", REPO / "tools" / "dat_canh_diem_tin_xoay.py")
mod = _ilu.module_from_spec(_spec)
sys.modules["dat_canh_xoay"] = mod
_spec.loader.exec_module(mod)

MAU_2_MUC = """# tiêu đề báo cáo

## 1. Tiêu đề mục một
- **Đang dùng:** PMID 111 (năm ghi trên gói: 2020) — *bài cũ một*
  - nơi dùng: a.html · ITEM-01
- **Nguồn tổng hợp mới hơn:** bài mới một — *Tạp chí A*, 2026 · PMID 222 · [Review] · ✓ không phát hiện rút bài
  - **Kết luận nguyên văn (abstract):** ĐOẠN DÀI TUYỆT ĐỐI KHÔNG ĐƯỢC XUẤT HIỆN Ở DIGEST.

## 2. Tiêu đề mục hai
- **Đang dùng:** PMID 333 — *bài cũ hai*
- **Nguồn tổng hợp mới hơn:** bài mới hai — *Tạp chí B*, 2026 · PMID 444 · [Guideline]
  - **Kết luận nguyên văn (abstract):** ĐOẠN DÀI KHÁC CŨNG KHÔNG ĐƯỢC LỌT RA.
"""


def test_doc_muc_bat_du_2_muc(tmp_path):
    f = tmp_path / "DAT-CANH-CHUNG-CU-MOI_2026-01-01.md"
    f.write_text(MAU_2_MUC, encoding="utf-8")
    muc = mod.doc_muc(f)
    assert len(muc) == 2, f"kỳ vọng 2 mục, được {len(muc)}"
    assert muc[0]["so"] == 1 and muc[0]["pmid_cu"] == "111" and muc[0]["nam_cu"] == "2020"
    assert muc[1]["so"] == 2 and muc[1]["pmid_cu"] == "333" and muc[1]["nam_cu"] is None


def test_khong_lo_ket_luan_nguyen_van(tmp_path, capsys):
    f = tmp_path / "DAT-CANH-CHUNG-CU-MOI_2026-01-01.md"
    f.write_text(MAU_2_MUC, encoding="utf-8")
    muc = mod.doc_muc(f)
    mod.in_digest(muc, len(muc), f.name)
    out = capsys.readouterr().out
    assert "ĐOẠN DÀI" not in out, "digest lộ đoạn 'Kết luận nguyên văn (abstract)' — vi phạm BH28"


def test_xoay_vong_wrap_around():
    muc = [{"so": i, "tieu_de": f"t{i}", "pmid_cu": str(i), "nam_cu": None,
            "nguon_moi": "x"} for i in range(1, 6)]  # 5 mục
    cua_so_1 = mod.cua_so(muc, con_tro=3, so_muc=4)
    so_thu_tu = [m["so"] for m in cua_so_1]
    assert so_thu_tu == [4, 5, 1, 2], f"wrap-around sai: {so_thu_tu}"


def test_con_tro_reset_khi_doi_ten_file(tmp_path, monkeypatch):
    state = tmp_path / "state.json"
    monkeypatch.setattr(mod, "STATE", state)
    state.write_text(json.dumps({"file": "cu.md", "con_tro": 50}), encoding="utf-8")
    ct = mod.doc_con_tro("moi.md", tong=10)
    assert ct == 0, "tên file đổi mà con trỏ không reset về 0"


def test_con_tro_tien_dung_va_luu_lai(tmp_path, monkeypatch):
    state = tmp_path / "state.json"
    monkeypatch.setattr(mod, "STATE", state)
    mod.ghi_con_tro("a.md", 8)
    assert mod.doc_con_tro("a.md", tong=114) == 8


def test_it_hon_so_muc_tra_het():
    muc = [{"so": 1, "tieu_de": "t", "pmid_cu": "1", "nam_cu": None, "nguon_moi": "x"}]
    assert mod.cua_so(muc, con_tro=0, so_muc=4) == muc


def test_file_khong_ton_tai_khong_chet(tmp_path):
    assert mod.doc_muc(tmp_path / "khong_co_that.md") == []


def test_main_luon_thoat_0(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "DASH", tmp_path)
    monkeypatch.setattr(mod, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(sys, "argv", ["x"])
    assert mod.main() == 0  # không có thư mục derivatives/ -> vẫn thoát 0, không crash
