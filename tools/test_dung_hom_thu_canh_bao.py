"""Hòm thư bác sĩ phải đọc đúng khuôn `alerts/*.md` hiện hành — T2-03, 20/09/2026."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("dht_t", GOC / "tools" / "dung_hom_thu.py")
dht = importlib.util.module_from_spec(sp)
sys.modules["dht_t"] = dht
sp.loader.exec_module(dht)

MAU_17_09 = """# CẢNH BÁO KHẨN — 2026-09-17

(chỉ sự kiện khẩn: rút bài · cổng FAIL · guideline bị vượt. Cần bác sĩ kiểm chứng.)

- 🔴 CỔNG QUÉT FAIL: chủ đề «Bệnh thận mạn (CKD)» — `RuntimeError: Europe PMC fallback thất bại`
- 🔴 CỔNG QUÉT FAIL: chủ đề «Suy tim — tiên lượng & điều trị» — `RuntimeError: Europe PMC fallback thất bại`
- 🟠 TÁI PHÁT TUẦN THỨ HAI: tên chủ đề
"""


def test_khuon_hien_hanh_du_bullet_va_ngay_dung():
    d = dht.doc_canh_bao(MAU_17_09)
    assert len(d) == 3
    assert all(n == "2026-09-17" for n, _t in d), "ngày bị backtrack thành '2026-09'"
    assert d[0][1].startswith("CỔNG QUÉT FAIL: chủ đề «Bệnh thận mạn (CKD)»")
    assert d[2][1].startswith("TÁI PHÁT TUẦN THỨ HAI")


def test_khuon_cu_mot_dong_van_doc_duoc():
    assert dht.doc_canh_bao("# CẢNH BÁO KHẨN — 2026-08-17 - 🔴 Tiêu đề — chi tiết dài\n") == \
        [("2026-08-17", "Tiêu đề — chi tiết dài")]


def test_dong_khong_thuoc_khuon_khong_bi_bo_vao():
    assert dht.doc_canh_bao("chỉ là văn xuôi\n- một bullet mồ côi không có tiêu đề ngày\n") == []


def test_hai_ngay_trong_mot_tep():
    d = dht.doc_canh_bao("# CẢNH BÁO KHẨN — 2026-09-01\n- 🔴 a\n# CẢNH BÁO KHẨN — 2026-09-02\n- 🔴 b\n")
    assert d == [("2026-09-01", "a"), ("2026-09-02", "b")]


def test_bullet_nhieu_dong_thut_le_duoc_noi_du():
    """P2-02: cảnh báo 07/09 dài 12 dòng thụt lề — bản cũ chỉ lấy dòng đầu, mất con số đo và «việc của bác sĩ»."""
    mau = ("# CẢNH BÁO KHẨN — 2026-09-07\n\n"
           "- 🔴 **TÁI PHÁT: bộ quét báo PASS trong khi 4/4 làn trả 0 GIẢ.**\n"
           "  Đo trong lượt quét W37: **136/136** ứng viên vào bằng fallback.\n"
           "  👤 **VIỆC THUỘC THẨM QUYỀN BÁC SĨ:** cho phép mở một phiên sửa.\n"
           "- 🟠 mục thứ hai một dòng\n")
    d = dht.doc_canh_bao(mau)
    assert len(d) == 2
    assert "136/136" in d[0][1] and "VIỆC THUỘC THẨM QUYỀN BÁC SĨ" in d[0][1]
    assert "136/136" not in d[1][1] and d[1][1].startswith("mục thứ hai")


def test_alerts_that_khong_mat_noi_dung():
    """Trên tệp thật: mọi bullet nhiều dòng của alerts/2026-09-07.md phải giữ dòng cuối (câu «tuần thứ ba»)."""
    f = GOC / "alerts" / "2026-09-07.md"
    if not f.exists():
        return
    d = dht.doc_canh_bao(f.read_text(encoding="utf-8"))
    assert d and "tuần thứ ba" in d[0][1]
