#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho kiem_do_tuoi_chung_cu.py (14/09/2026, workflow kiểm tra toàn diện).

Bối cảnh: `in_bang_tuoi()` — bảng median/phân bố tuổi từng chủ đề — trước bản
vá CHỈ được gọi bên trong nhánh `if not canh_bao:` (main(), nhánh 🟢). Nghĩa
là bảng này bị NUỐT MẤT mỗi khi có BẤT KỲ cảnh báo nào khác đang treo (vd
"giám sát an toàn thuốc chưa từng chạy" — gần như luôn đúng ở nhịp làm việc
thật), dù chính bảng đó mới trả lời câu "chủ đề nào lâu chưa xem lại NHẤT".

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`): (1) kiểm HÀNH VI,
không đếm chuỗi; (2) mỗi ca gắn với rủi ro THẬT; (3) nhanh, ngoại tuyến.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_do_tuoi_chung_cu as K  # noqa: E402


def test_in_bang_tuoi_in_dung_trung_vi_va_qua_han(capsys):
    K.in_bang_tuoi([("ChuDeA", 50), ("ChuDeB", 40), ("ChuDeC", 10)])
    out = capsys.readouterr().out
    assert "3 chủ đề" in out
    assert "trung vị 40 ngày" in out
    assert "2 chủ đề quá" in out


def test_in_bang_tuoi_rong_khong_in_gi(capsys):
    K.in_bang_tuoi([])
    assert capsys.readouterr().out == ""


def _ep_co_canh_bao(monkeypatch, tmp_path, lau):
    """Ép main() rơi vào nhánh 🟡 (canh_bao khác rỗng) một cách tối giản:
    không có dashboard nào ⇒ mục (1) im lặng; log tuần/tháng không tồn tại
    ⇒ mục (2) LUÔN cảnh báo 'chưa từng chạy' (đúng nhánh phổ biến nhất trong
    thực tế — máy nào cũng có log này). `lau` được ép trực tiếp qua
    `lau_chua_xem_lai` để không phụ thuộc dữ liệu dashboard thật."""
    dash_rong = tmp_path / "EBM-Dashboards-rong"
    dash_rong.mkdir()
    monkeypatch.setattr(K, "DASH", dash_rong)
    monkeypatch.setattr(K, "LOG_TUAN", tmp_path / "khong-ton-tai-tuan.log")
    monkeypatch.setattr(K, "LOG_THANG", tmp_path / "khong-ton-tai-thang.log")
    monkeypatch.setattr(K, "lau_chua_xem_lai", lambda: lau)
    monkeypatch.setattr(sys, "argv", ["kiem_do_tuoi_chung_cu.py"])


def test_bang_tuoi_van_hien_khi_co_canh_bao_khac(monkeypatch, tmp_path, capsys):
    """Ca thật: máy KHÔNG có log giám sát tuần (luôn đúng ngoài container có
    OneDrive) ⇒ canh_bao khác rỗng ⇒ trước bản vá, bảng median/phân bố tuổi
    KHÔNG BAO GIỜ hiện ra dù có 3 chủ đề rất lâu chưa xem lại."""
    _ep_co_canh_bao(monkeypatch, tmp_path,
                     [("ChuDeLau1", 50), ("ChuDeLau2", 40), ("ChuDeLau3", 10)])
    rc = K.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "🟡 GIÁM SÁT CHỨNG CỨ QUÁ HẠN" in out
    assert "trung vị 40 ngày" in out
    assert "2 chủ đề quá" in out


def test_bang_tuoi_van_hien_khi_canh_bao_va_lau_rong():
    """Đối chứng: canh_bao khác rỗng nhưng KHÔNG có chủ đề nào (lau=[]) thì
    không in gì thêm — không được crash, không in bảng rỗng vô nghĩa."""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        K.in_bang_tuoi([])
    assert buf.getvalue() == ""


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
