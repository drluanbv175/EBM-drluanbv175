#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #3, MEDIUM).

`in_quick_view()` trước đây bỏ qua HOÀN TOÀN các thẻ KHÔNG có PMID (điều kiện `if pm and ...`)
— không in cờ 🟠, cũng không in ⚪ CHƯA DÒ, nên thẻ trông Y HỆT một thẻ đã được đối chiếu và
sạch. Đo 21/09: 73/1100 thẻ đã duyệt không có `source.pmid` (20 decision='apply'). Cơ chế quét
quý chỉ khoá theo PMID nên nhóm này KHÔNG BAO GIỜ được đối chiếu — vi phạm «không biết ≠ sạch».
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tdk_khong_pmid_test", TOOLS / "tra_diem_kham.py")
tdk = importlib.util.module_from_spec(spec)
sys.modules["tdk_khong_pmid_test"] = tdk
spec.loader.exec_module(tdk)


def _the_khong_pmid(rec: str = "khuyến cáo X") -> dict:
    return {"id": "T-KHONG-PMID", "topic": "chủ đề không PMID", "recommendation": rec,
            "decision": "apply", "provenance": "from_doctor_master", "verification_status": "đã xác minh",
            "date_added": "2026-01-01", "source": {"doi": "10.1000/x"}, "gradeLevel": "na"}


def _the_co_pmid(pmid: str, rec: str = "khuyến cáo Y") -> dict:
    return {"id": "T-CO-PMID", "topic": "chủ đề có pmid", "recommendation": rec,
            "decision": "apply", "provenance": "from_doctor_master", "verification_status": "đã xác minh",
            "date_added": "2026-01-01", "source": {"pmid": pmid}, "gradeLevel": "na"}


def _bat_stdout(fn, *a, **kw) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*a, **kw)
    return buf.getvalue()


def test_the_khong_pmid_in_ro_khong_bi_im_lang():
    vq_info = {"hop_le": True, "pmids": set(), "da_do": {"1", "2"}, "nguon": "x", "ngay": "20260921",
               "cu": False, "ly_do": ""}
    out = _bat_stdout(tdk.in_quick_view, "câu hỏi", [_the_khong_pmid()], set(), 0.0, "khop", vq_info, False)
    assert "KHÔNG CÓ PMID" in out, "thẻ không PMID phải được nói rõ, không được im lặng như đã dò sạch"
    assert "CHƯA DÒ" not in out.split("KHÔNG CÓ PMID")[0], "không được lẫn với nhãn CHƯA DÒ của thẻ CÓ pmid"


def test_the_co_pmid_da_do_khong_bi_gan_nham_khong_co_pmid():
    vq_info = {"hop_le": True, "pmids": set(), "da_do": {"1111"}, "nguon": "x", "ngay": "20260921",
               "cu": False, "ly_do": ""}
    out = _bat_stdout(tdk.in_quick_view, "câu hỏi", [_the_co_pmid("1111")], set(), 0.0, "khop", vq_info, False)
    assert "KHÔNG CÓ PMID" not in out
    assert "CHƯA DÒ" not in out
    assert "CÓ BẢN TỔNG HỢP MỚI HƠN" not in out


def test_the_co_pmid_chua_dua_vao_da_do_van_bao_chua_do_nhu_cu():
    """Đối chứng — không phá hành vi ⚪ CHƯA DÒ đã có cho thẻ CÓ pmid nhưng ngoài tập đã dò."""
    vq_info = {"hop_le": True, "pmids": set(), "da_do": {"2222"}, "nguon": "x", "ngay": "20260921",
               "cu": False, "ly_do": ""}
    out = _bat_stdout(tdk.in_quick_view, "câu hỏi", [_the_co_pmid("1111")], set(), 0.0, "khop", vq_info, False)
    assert "CHƯA DÒ «bản tổng hợp mới hơn»" in out
    assert "KHÔNG CÓ PMID" not in out


def test_the_co_pmid_co_co_van_bao_do_binh_thuong():
    """Đối chứng — cờ 🟠 dương tính của thẻ CÓ pmid không bị bản vá này chạm vào."""
    vq_info = {"hop_le": True, "pmids": {"3333"}, "da_do": {"3333"}, "nguon": "x", "ngay": "20260921",
               "cu": False, "ly_do": ""}
    out = _bat_stdout(tdk.in_quick_view, "câu hỏi", [_the_co_pmid("3333")], {"3333"}, 0.0, "khop", vq_info, False)
    assert "CÓ BẢN TỔNG HỢP MỚI HƠN" in out
    assert "KHÔNG CÓ PMID" not in out
    assert "CHƯA DÒ «bản tổng hợp mới hơn»" not in out


def test_khong_co_vq_info_van_bao_khong_co_pmid():
    """`vq_info=None` (không truyền báo cáo quét quý) — thẻ không PMID VẪN phải được nói rõ,
    vì đây là giới hạn CẤU TRÚC, không phụ thuộc lượt quét nào."""
    out = _bat_stdout(tdk.in_quick_view, "câu hỏi", [_the_khong_pmid()], set(), 0.0, "khop", None, False)
    assert "KHÔNG CÓ PMID" in out
