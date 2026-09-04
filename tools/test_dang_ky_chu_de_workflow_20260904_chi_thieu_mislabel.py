#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện MEDIUM của Workflow đối kháng đa-agent 2026-09-04
(vòng 2, task #70): `tools/dang_ky_chu_de.py` — nhánh "chỉ thiếu, không nói
sai" (`chi_thieu`) dán nhãn SAI cho một cặp bản ĐANG mâu thuẫn thật.

CƠ CHẾ LỖI (xác nhận bằng thực nghiệm TRƯỚC khi vá): dòng gốc
    if muc_cu and not (set(muc_cu) - set(muc_moi)):
        chi_thieu.append(...)
chỉ so TẬP HỢP KHÓA PMID (bản mới có phủ hết PMID của bản cũ không) —
KHÔNG đọc giá trị `decision`. Một cặp cùng lát cắt có thể vừa là siêu tập
PMID VỪA đổi `decision` cho một PMID chung (ca thật đã ghi trong docstring
đầu file: ICHD-3 `apply` ở bản này, `consider` ở bản kia sau đợt sửa
12/08). `chi_thieu` cũ dán nhãn cặp đó "CHỈ THIẾU, không nói sai" — ĐÚNG
LÚC `tim_mau_thuan()` (so mọi cặp trong cùng `theo_goc`, bao gồm CẢ cặp
cùng lát cắt khác ngày) dán nhãn 🔴 "nói ngược nhau" cho CHÍNH cặp đó.
Hai nhãn trái ngược nhau cho cùng một cặp bản — đúng lúc bác sĩ cần phân
biệt rạch ròi nhất "thiếu thông tin" (an toàn hơn) khỏi "nhận thông tin
sai" (nguy hiểm hơn), theo đúng phân biệt đã nêu ở docstring dòng 11-20
của chính file này.

BẢN VÁ: thêm `_co_xung_dot_quyet_dinh()` — so GIÁ TRỊ `decision` cho mọi
PMID chung (so được đơn trị ở cả hai bên); một cặp có xung đột decision bị
LOẠI khỏi `chi_thieu`, dù vẫn là siêu tập PMID. Không đổi `tim_mau_thuan()`
— cặp đó vẫn được báo 🔴 như trước.

Nguyên tắc viết test: monkeypatch `dkcd.nap_vd` và `dkcd.DASH`/`dkcd.DA_DUYET`
(không tạo file thật ở đường dẫn tuyệt đối EBM-Dashboards/ mà module tự suy
từ `Path(__file__).resolve().parents[1]`), gọi THẲNG `main()` qua
`sys.argv`, đọc stdout thật — không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dang_ky_chu_de as dkcd  # noqa: E402


class _FakeVD:
    """Nội dung file dashboard trong các test này LÀ json list các item — mô
    phỏng tối giản, `extract_data_block` passthrough, `split_items` parse JSON."""

    @staticmethod
    def extract_data_block(text: str) -> str:
        return text

    @staticmethod
    def split_items(blk: str):
        return json.loads(blk)

    @staticmethod
    def field(item: dict, key: str):
        return item.get(key)


def _muc(pmid: str, decision: str, title: str) -> dict:
    return {"pmid": pmid, "decision": decision, "gradeLevel": "high",
            "normativeBasis": None, "title": title}


def _dung_dash(tmp_path: Path, ten_va_items: dict) -> Path:
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    for ten, items in ten_va_items.items():
        (dash / ten).write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    return dash


class TestCapXungDotKhongDuocDanNhanChiThieu:
    """★★ Ca chính — cặp cùng lát cắt, bản mới phủ hết PMID bản cũ NHƯNG đổi
    `decision` cho PMID chung → KHÔNG được xuất hiện trong "CHỈ THIẾU", PHẢI
    xuất hiện trong danh sách 🔴 mâu thuẫn thật."""

    def test_khong_vao_chi_thieu_co_vao_mau_thuan(self, monkeypatch, tmp_path, capsys):
        dash = _dung_dash(tmp_path, {
            "WebDashboard_EBM_VanDeCuThe_TestXungDot_TongHop_20260101.html": [
                _muc("12345", "apply", "Ban cu ve mot van de")],
            "WebDashboard_EBM_VanDeCuThe_TestXungDot_TongHop_20260201.html": [
                _muc("12345", "consider", "Ban moi ve cung van de"),
                _muc("67890", "apply", "Nguon moi bo sung")],
        })
        monkeypatch.setattr(dkcd, "nap_vd", lambda: _FakeVD())
        monkeypatch.setattr(dkcd, "DASH", dash)
        monkeypatch.setattr(dkcd, "DA_DUYET", dash / "mau-thuan-da-duyet.json")
        monkeypatch.setattr(sys, "argv", ["dang_ky_chu_de.py"])
        ma_thoat = dkcd.main()
        in_ra = capsys.readouterr().out
        # Định dạng in ra thật của chi_thieu (xem main(), dòng in f-string) —
        # câu này TUYỆT ĐỐI không được xuất hiện khi có xung đột decision.
        assert "TestXungDot_TongHop: bản 20260101 nằm gọn trong bản 20260201" not in in_ra
        # Nhưng PHẢI được báo là mâu thuẫn thật (🔴).
        assert "🔴" in in_ra
        assert "12345" in in_ra
        assert ma_thoat == 1

    def test_ham_phat_hien_xung_dot_true_khi_co_khac_bat_ky(self):
        """★★ Đối chứng trực tiếp hàm nguồn `_co_xung_dot_quyet_dinh()`."""
        muc_cu = {"12345": [("apply", "high", None, "t1")]}
        muc_moi = {"12345": [("consider", "high", None, "t2")], "67890": [("apply", "high", None, "t3")]}
        assert dkcd._co_xung_dot_quyet_dinh(muc_cu, muc_moi) is True


class TestChiThieuThatVanDuocBaoDungNhuCu:
    """Đối chứng bắt buộc — cặp KHÔNG đổi decision (chỉ thiếu thật, đúng ý
    nghĩa gốc của nhãn) vẫn phải xuất hiện trong "CHỈ THIẾU", và KHÔNG được
    xuất hiện trong danh sách mâu thuẫn."""

    def test_chi_thieu_that_van_bao_dung(self, monkeypatch, tmp_path, capsys):
        dash = _dung_dash(tmp_path, {
            "WebDashboard_EBM_VanDeCuThe_TestOK_TongHop_20260101.html": [
                _muc("11111", "apply", "Nguon cu")],
            "WebDashboard_EBM_VanDeCuThe_TestOK_TongHop_20260201.html": [
                _muc("11111", "apply", "Nguon cu, giu nguyen quyet dinh"),
                _muc("22222", "consider", "Nguon moi them vao")],
        })
        monkeypatch.setattr(dkcd, "nap_vd", lambda: _FakeVD())
        monkeypatch.setattr(dkcd, "DASH", dash)
        monkeypatch.setattr(dkcd, "DA_DUYET", dash / "mau-thuan-da-duyet.json")
        monkeypatch.setattr(sys, "argv", ["dang_ky_chu_de.py"])
        ma_thoat = dkcd.main()
        in_ra = capsys.readouterr().out
        assert "TestOK_TongHop: bản 20260101 nằm gọn trong bản 20260201" in in_ra
        assert "🔴" not in in_ra
        assert ma_thoat == 0

    def test_ham_phat_hien_xung_dot_false_khi_decision_giong_nhau(self):
        muc_cu = {"11111": [("apply", "high", None, "t1")]}
        muc_moi = {"11111": [("apply", "high", None, "t1")], "22222": [("consider", "high", None, "t2")]}
        assert dkcd._co_xung_dot_quyet_dinh(muc_cu, muc_moi) is False

    def test_ham_bo_qua_pmid_nhieu_muc_khong_so_duoc(self):
        """PMID mang NHIỀU item ở một bên (không so đơn trị được) không được
        tính là xung đột — nhánh đó thuộc về `khong_so_duoc` của tim_mau_thuan()."""
        muc_cu = {"12345": [("apply", "high", None, "t1"), ("consider", "high", None, "t2")]}
        muc_moi = {"12345": [("apply", "high", None, "t1")]}
        assert dkcd._co_xung_dot_quyet_dinh(muc_cu, muc_moi) is False
