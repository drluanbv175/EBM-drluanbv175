"""Thang mức từng miền nguy cơ sai lệch theo công cụ — 04/11/2026.

Kiểm chéo bù 20 bản đầu (luật 26/10) bắt 3 mức KHÔNG có trong thang của công cụ (QUADAS «trung bình», ROBINS-E «không đánh
giá được» ở cấp miền, kết quả công cụ Cochrane xếp làm «miền» AMSTAR-2 «cao/không rõ»); quét toàn kho: 15 mục/14 bản cùng
kiểu và 188 nhãn đồng nghĩa viết lẫn lộn (AMSTAR-2 «đạt» bên cạnh «có»…). Cổng chặn mức ngoài thang; bước dựng in nhãn chuẩn.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import tom_tat_chung_cu_word as T  # noqa: E402
from test_tom_tat_chung_cu_word_20261019 import NGU_CANH, TRANG, _hop_le  # noqa: E402

CAN_DOCX = pytest.mark.skipif(importlib.util.find_spec("docx") is None, reason="thiếu python-docx (CI bản sao trần không cài)")


@pytest.mark.parametrize("cong_cu, muc", [
    ("RoB 2", "thấp"), ("RoB 2", "một số lo ngại (thiếu thông tin)"), ("RoB 2", "thấp với MACE và ung thư; một số lo ngại với tác hại"),
    ("ROBINS-I", "nghiêm trọng"), ("ROBINS-I", "vừa"), ("ROBINS-I", "không rõ"), ("ROBINS-I", "dự kiến thấp"),
    ("ROBINS-E", "một số lo ngại (toàn đoàn hệ); cao nếu so sánh phân nhóm"), ("ROBINS-E", "Có lo ngại (some concerns)"),
    ("QUADAS-2", "lo ngại cao"), ("PROBAST", "không rõ"), ("AMSTAR-2", "Đạt một phần"), ("AMSTAR-2", "không đạt theo bản đã đọc"),
    ("AMSTAR-2", "không áp dụng"),
])
def test_muc_hop_le(cong_cu, muc):
    assert T._muc_sai_thang(cong_cu, [{"ten": "m", "danh_gia": muc, "ly_do": "x"}]) == []


@pytest.mark.parametrize("cong_cu, muc", [
    ("QUADAS-2", "trung bình"), ("PROBAST", "có lo ngại"), ("ROBINS-E", "không đánh giá được"),
    ("AMSTAR-2", "Cao/không rõ ở nhiều thử nghiệm"), ("AMSTAR-2", "đáng lo ngại"),
    ("RoB 2", "thấp (kết cục chính); cao hơn cho đái tháo đường mới"), ("ROBINS-I", "dự kiến thấp đến trung bình"),
    ("AMSTAR-2", "Có (vận động) · Không (tâm lý–xã hội)"),
])
def test_muc_ngoai_thang_bi_chan(cong_cu, muc):
    loi = T._muc_sai_thang(cong_cu, [{"ten": "m", "danh_gia": muc, "ly_do": "x"}])
    assert len(loi) == 1 and "không có trong thang" in loi[0]


def test_cong_cu_ngoai_bang_khong_kiem_thang():
    assert T._muc_sai_thang("AGREE II", [{"ten": "Miền 3", "danh_gia": "trung bình – cao", "ly_do": "x"}]) == []


@pytest.mark.parametrize("cong_cu, vao, ra", [
    ("AMSTAR-2", "Đạt một phần", "Có một phần"), ("AMSTAR-2", "đạt", "có"), ("AMSTAR-2", "không đạt", "không"),
    ("ROBINS-I", "vừa", "trung bình"), ("ROBINS-I", "không rõ", "không có thông tin"),
    ("RoB 2", "có một số lo ngại (x)", "một số lo ngại (x)"), ("RoB 2", "thấp", "thấp"), ("AGREE II", "đạt", "đạt"),
])
def test_nhan_dong_nghia_in_thong_nhat(cong_cu, vao, ra):
    assert T.muc_chuan(cong_cu, vao) == ra


def test_cong_kiem_tom_tat_chan_muc_ngoai_thang():
    tt = _hop_le()
    tt["nguy_co_sai_lech"]["mien"][0]["danh_gia"] = "không đánh giá được"
    assert any("không có trong thang" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


@CAN_DOCX
def test_bang_rob_in_nhan_chuan():
    tt = _hop_le()
    tt["nguy_co_sai_lech"] = {"cong_cu": "AMSTAR-2", "tong_the": "thấp",
                              "mien": [{"ten": "Mục 2 — đề cương", "danh_gia": "Đạt một phần", "ly_do": "x", "trang": 2}]}
    doc = T.dung_word(tt, NGU_CANH)
    o = [c.text for t in doc.tables for r in t.rows for c in r.cells]
    assert "Có một phần" in o and "Đạt một phần" not in o
