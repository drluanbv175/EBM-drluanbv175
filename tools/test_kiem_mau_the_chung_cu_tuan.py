#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho tools/kiem_mau_the_chung_cu_tuan.py (12/09/2026)."""
from __future__ import annotations

import importlib.util as _ilu
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_spec = _ilu.spec_from_file_location(
    "kiem_mau_the", REPO / "tools" / "kiem_mau_the_chung_cu_tuan.py"
)
mod = _ilu.module_from_spec(_spec)
sys.modules["kiem_mau_the"] = mod
_spec.loader.exec_module(mod)

THE_DAY_DU = """**[W99-01] Chủ đề mẫu — Cochrane — Cân nhắc (ưu tiên đọc #1)**
Điều gì thay đổi: câu kết luận thực hành tự đứng được.
Nguồn: SR/MA · *Tạp chí* 2026 · PMID 12345678 · doi:10.1000/xyz
Hiệu số như nguồn báo cáo: RR 0,80 (95% CI 0,70-0,90); độ chắc chắn CAO.
Ai bị ảnh hưởng: người lớn ngoại trú có bệnh X.
Rủi ro nếu áp dụng sai: đọc ngược chiều | Nếu bỏ qua: tiếp tục thực hành cũ.
⚠️ Giới hạn tự khai của nguồn.
Thẩm định toàn văn: đã đọc bản OA (PMC123), không phát hiện thêm.
"""

THE_THIEU_PMID = """**[W99-02] Chủ đề khác — RCT — Chưa đủ**
Điều gì thay đổi: mô tả ngắn.
Nguồn: RCT · *Tạp chí* 2026 (không có định danh phân giải được)
Hiệu số như nguồn báo cáo: không nêu.
Ai bị ảnh hưởng: nhóm X.
Rủi ro nếu áp dụng sai: A | Nếu bỏ qua: B.
Thẩm định toàn văn: chưa đọc được — chưa có bản OA.
"""

THE_APPLY_NGAY_NHUNG_PARTIAL = """**[W99-03] Chủ đề ba — Cochrane — Áp dụng ngay**
Điều gì thay đổi: mô tả.
Nguồn: SR/MA · *Tạp chí* 2026 · PMID 87654321
Hiệu số như nguồn báo cáo: RR 0,5.
Ai bị ảnh hưởng: nhóm Y.
Rủi ro nếu áp dụng sai: A | Nếu bỏ qua: B.
Thẩm định toàn văn: chưa đọc được — Cochrane không truy cập mở.
"""

THE_NHAN_SAI = """**[W99-04] Chủ đề bốn — RCT — Có thể thử**
Điều gì thay đổi: mô tả.
Nguồn: RCT · PMID 11111111
Hiệu số như nguồn báo cáo: x.
Ai bị ảnh hưởng: y.
Rủi ro nếu áp dụng sai: A | Nếu bỏ qua: B.
Thẩm định toàn văn: đã đọc.
"""

THE_THIEU_DIEU_GI_THAY_DOI = """**[W99-05] Chủ đề năm — RCT — Cân nhắc**
Nguồn: RCT · PMID 22222222
Hiệu số như nguồn báo cáo: x.
Ai bị ảnh hưởng: y.
Rủi ro nếu áp dụng sai: A | Nếu bỏ qua: B.
Thẩm định toàn văn: đã đọc.
"""


def _viet(tmp_path, noi_dung):
    f = tmp_path / "gia.md"
    f.write_text(noi_dung, encoding="utf-8")
    return f


def test_the_day_du_sach_hoan_toan(tmp_path):
    f = _viet(tmp_path, THE_DAY_DU)
    ma_thoat, ket_qua = mod.kiem_file(f)
    assert ma_thoat == 0, [(k.ma, k.do, k.vang) for k in ket_qua]
    assert len(ket_qua) == 1


def test_thieu_pmid_la_loi_cung(tmp_path):
    f = _viet(tmp_path, THE_THIEU_PMID)
    ma_thoat, ket_qua = mod.kiem_file(f)
    assert ma_thoat == 2
    assert any("PMID hoặc doi" in d for d in ket_qua[0].do)


def test_apply_ngay_voi_partial_la_loi_cung(tmp_path):
    f = _viet(tmp_path, THE_APPLY_NGAY_NHUNG_PARTIAL)
    ma_thoat, ket_qua = mod.kiem_file(f)
    assert ma_thoat == 2
    assert any("Áp dụng ngay" in d and "partial" in d.lower() or "PARTIAL" in d for d in ket_qua[0].do)


def test_nhan_de_xuat_khong_hop_le(tmp_path):
    f = _viet(tmp_path, THE_NHAN_SAI)
    ma_thoat, ket_qua = mod.kiem_file(f)
    assert ma_thoat == 2
    assert any("không hợp lệ" in d for d in ket_qua[0].do)


def test_thieu_dieu_gi_thay_doi_la_loi_cung(tmp_path):
    f = _viet(tmp_path, THE_THIEU_DIEU_GI_THAY_DOI)
    ma_thoat, ket_qua = mod.kiem_file(f)
    assert ma_thoat == 2
    assert any("Điều gì thay đổi" in d for d in ket_qua[0].do)


def test_thieu_ai_bi_anh_huong_chi_la_canh_bao(tmp_path):
    the = THE_DAY_DU.replace("Ai bị ảnh hưởng: người lớn ngoại trú có bệnh X.\n", "")
    f = _viet(tmp_path, the)
    ma_thoat, ket_qua = mod.kiem_file(f)
    assert ma_thoat == 1, "thiếu 'Ai bị ảnh hưởng' phải là cảnh báo, không chặn"
    assert any("Ai bị ảnh hưởng" in v for v in ket_qua[0].vang)


def test_file_khong_co_the_hop_le(tmp_path):
    f = _viet(tmp_path, "Văn bản tự do, không có thẻ nào khớp định dạng.\n")
    ma_thoat, ket_qua = mod.kiem_file(f)
    assert ma_thoat == 2
    assert ket_qua == []


def test_nghiem_ngat_nang_canh_bao_thanh_chan(tmp_path, capsys):
    the = THE_DAY_DU.replace("Ai bị ảnh hưởng: người lớn ngoại trú có bệnh X.\n", "")
    f = _viet(tmp_path, the)
    import subprocess
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "kiem_mau_the_chung_cu_tuan.py"), str(f), "--nghiem-ngat"],
        capture_output=True, text=True,
    )
    assert r.returncode == 2, r.stdout


def test_nhieu_the_trong_mot_file_khong_lan_sang_nhau(tmp_path):
    f = _viet(tmp_path, THE_DAY_DU + "\n" + THE_THIEU_PMID)
    ma_thoat, ket_qua = mod.kiem_file(f)
    assert len(ket_qua) == 2
    assert ket_qua[0].ma == "W99-01" and not ket_qua[0].do
    assert ket_qua[1].ma == "W99-02" and ket_qua[1].do
