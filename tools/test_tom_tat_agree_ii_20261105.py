"""AGREE II — thống nhất nhãn mức miền khi DỰNG Word/PDF (05/11/2026, bác sĩ chọn «Thống nhất khi in»).

AGREE II cho điểm % theo miền, không có mức chữ; kho viết ~60 kiểu nhãn («tốt», «khá», «đạt một phần tiêu chí (định tính…)»,
«Mô tả rõ»…). Bước dựng in thấp / trung bình / cao hoặc khoảng; nhãn mô tả giữ sau «—»; dữ liệu `tom_tat.json` không đổi.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import tom_tat_chung_cu_word as T  # noqa: E402
from test_tom_tat_chung_cu_word_20261019 import NGU_CANH, _hop_le  # noqa: E402

CAN_DOCX = pytest.mark.skipif(importlib.util.find_spec("docx") is None, reason="thiếu python-docx (CI bản sao trần không cài)")


@pytest.mark.parametrize("vao, ra", [
    ("tốt", "cao"), ("khá", "trung bình – cao"), ("khá (trung bình – cao)", "trung bình – cao"),
    ("trung bình–cao", "trung bình – cao"), ("trung bình – khá", "trung bình – cao"), ("cao – trung bình", "trung bình – cao"),
    ("trung bình–thấp", "thấp – trung bình"), ("thấp đến trung bình (theo văn bản chương này)",
                                               "thấp – trung bình (theo văn bản chương này)"),
    ("tốt — có điểm không nhất quán", "cao — có điểm không nhất quán"),
    ("chất lượng thấp (nhận định định tính của một người chấm)", "thấp (nhận định định tính của một người chấm)"),
    ("đạt một phần tiêu chí (định tính)", "trung bình — đạt một phần tiêu chí (định tính)"),
    ("Mô tả rõ (định tính)", "cao — mô tả rõ (định tính)"),
    ("Mô tả rất hạn chế (định tính)", "thấp — mô tả rất hạn chế (định tính)"),
    ("Khá rõ, có vài chỗ chưa nhất quán", "trung bình – cao — khá rõ, có vài chỗ chưa nhất quán"),
    ("đạt phần lớn tiêu chí, có vài chỗ chưa rõ", "trung bình – cao — đạt phần lớn tiêu chí, có vài chỗ chưa rõ"),
])
def test_nhan_agree_in_thong_nhat(vao, ra):
    assert T.muc_chuan("AGREE II", vao) == ra


@pytest.mark.parametrize("giu", [
    "trung bình", "cao", "thấp", "thấp – trung bình", "trung bình — mô tả một phần trong bài chính",
    "cao theo phần bài mô tả (một số chi tiết chỉ có ở phụ lục)", "thấp (theo văn bản chương này)", "không rõ",
])
def test_nhan_chuan_giu_nguyen(giu):
    assert T.muc_chuan("AGREE II", giu) == giu


def test_cong_cu_khac_khong_bi_anh_huong():
    assert T.muc_chuan("JBI Text and Opinion", "tốt") == "tốt"
    assert T.muc_chuan("RoB 2", "có một số lo ngại") == "một số lo ngại"


def test_agree_khong_vao_cong_thang():
    assert T._muc_sai_thang("AGREE II", [{"ten": "Miền 3", "danh_gia": "khá", "ly_do": "x"}]) == []


@CAN_DOCX
def test_bang_word_in_nhan_agree_chuan():
    tt = _hop_le()
    tt["nguy_co_sai_lech"] = {"cong_cu": "AGREE II", "tong_the": "trung bình",
                              "mien": [{"ten": "Miền 4 — Trình bày", "danh_gia": "tốt", "ly_do": "x", "trang": 2}]}
    o = [c.text for t in T.dung_word(tt, NGU_CANH).tables for r in t.rows for c in r.cells]
    assert "cao" in o and "tốt" not in o
