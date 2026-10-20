# -*- coding: utf-8 -*-
"""K4 nhận «khuyến cáo chống» của guideline + nhận biết chiều của chính mục (20/10/2026).

Đo trên 85 câu ngược chiều thật của kho toàn văn: K4 cũ bắt 0/8 câu «(strong|conditional) recommendation against» /
«recommend against» và 0/3 câu USPSTF D — đúng kiểu tín hiệu «nguồn khuyến cáo KHÔNG làm» quan trọng nhất. Câu thử dưới
đây là câu tự viết theo đúng khuôn của GRADE/USPSTF (không chép nguyên văn bài). OFFLINE.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent


def _nap(tep: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, _TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


K = _nap("kiem_quan_the_chieu.py", "_k4_chong_1020")
B = _nap("bo_vang_kiem_ngu_nghia.py", "_bvk_k4_1020")


@pytest.mark.parametrize("cau", [
    "We suggest against routine use of the drug (conditional recommendation, low certainty).",
    "The panel made a strong recommendation against long-term therapy.",
    "The USPSTF recommends against screening for the condition in adults.",
    "Grade D recommendation.",
    "The harms of screening for the condition outweigh the benefits.",
    "Experts advise against initiating therapy in this group.",
    # «against» nằm cạnh chữ an toàn/biến cố vẫn phải báo (không bị lọc như kết cục phụ)
    "We recommend against the drug because of serious adverse events.",
])
def test_khuyen_cao_chong_duoc_bat(cau):
    assert K.kiem_chieu(K.chuan_hoa(cau)), cau


@pytest.mark.parametrize("cau", [
    "We recommend screening for the condition in adults aged 50 to 75 years (B recommendation).",
    "The benefits outweigh the harms.",
    "No serious adverse events were reported.",
])
def test_cau_cung_chieu_khong_bao(cau):
    assert not K.kiem_chieu(K.chuan_hoa(cau)), cau


NGUON_CHONG = "The USPSTF recommends against screening for the condition in the general adult population. (D recommendation)."


def test_muc_phu_dinh_cung_chieu_nguon_la_khop():
    it = {"id": "X", "title": "KHÔNG tầm soát bệnh X ở người không triệu chứng", "population": "Người lớn",
          "action": "Không siêu âm thường quy để sàng lọc."}
    k4 = K.kiem_muc(it, NGUON_CHONG)["k4"]
    assert k4["muc"] == "khop" and k4["muc_phu_dinh"] and k4["cau_bo_qua"]


def test_muc_khang_dinh_nguoc_nguon_chong_la_can_doc():
    it = {"id": "Y", "title": "Tầm soát bệnh X", "population": "Người lớn", "action": "Siêu âm sàng lọc định kỳ."}
    k4 = K.kiem_muc(it, NGUON_CHONG)["k4"]
    assert k4["muc"] == "can_doc" and k4["cau_nguon"]


@pytest.mark.parametrize("truong,gia_tri", [("title", "Tránh benzodiazepine ở người cao tuổi"),
                                             ("action", "Ngừng thuốc nếu men gan tăng."),
                                             ("action", "— Không dùng thường quy.")])
def test_nhan_dien_muc_phu_dinh(truong, gia_tri):
    assert K.muc_phu_dinh({truong: gia_tri})


@pytest.mark.parametrize("gia_tri", ["Khởi trị statin cường độ cao", "Bỏ qua bước này là sai",
                                     "Không chỉ người lớn mà cả trẻ em", "Bỏ thuốc lá — can thiệp giảm tử vong"])
def test_muc_khang_dinh_khong_bi_coi_la_phu_dinh(gia_tri):
    # «bỏ qua…», «không chỉ…» là câu khẳng định — không được làm K4 im lặng
    assert not K.muc_phu_dinh({"title": gia_tri, "action": gia_tri})


def test_bo_vang_truyen_action_cho_kiem_muc():
    """Đường đo bộ vàng phải đưa `action` vào kiem_muc — mục có tiêu đề khẳng định nhưng hành động phủ định."""
    m = {"id": "Z", "title": "Tầm soát bệnh X — USPSTF", "population": "Người lớn", "action": "Không tầm soát thường quy.",
         "pmid": "1", "doi": None,
         "nhan_bac_si": {"dung_quan_the": True, "dung_chieu": True, "du_dieu_kien": True, "ghi_chu": None}}
    kq = B.do({"muc": [m]}, {"1": NGUON_CHONG})
    assert kq["K4"]["fp"] == 0 and kq["K4"]["tn"] == 1
