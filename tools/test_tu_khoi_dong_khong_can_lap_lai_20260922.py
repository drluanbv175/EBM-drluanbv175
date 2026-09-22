#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #8, LOW).

`quarterly_superseded.sh` từng gộp CHUA_DO/MAU/KHONG_CO_CONG_CU (tất định, retry ngay
không giúp gì) CHUNG một nhãn "CÓ BƯỚC LỖI" với lỗi mạng/lỗi thật — khiến
`tu_khoi_dong.qua_han()` (đọc "LỖI" ⇒ phóng lại BẤT KỂ số ngày) hâm nóng ~326 lời gọi
NCBI MỖI LẦN MỞ PHIÊN một cách vô ích. Nay có nhãn riêng "KHÔNG CẦN LẶP LẠI" — file này
kiểm CẢ HAI phía: `kiem_do_tuoi_chung_cu.lan_chay_cuoi()` đọc đúng nhãn mới, VÀ
`tu_khoi_dong.qua_han()` xử lý nhãn đó như PASS (chịu ngưỡng han_ngay), không như LỖI
(retry ngay bất kể ngày).
"""
from __future__ import annotations

import datetime as _dt
import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

spec_do_tuoi = importlib.util.spec_from_file_location("_kdt_test", TOOLS / "kiem_do_tuoi_chung_cu.py")
kdt = importlib.util.module_from_spec(spec_do_tuoi)
sys.modules["_kdt_test"] = kdt
spec_do_tuoi.loader.exec_module(kdt)

spec_tkd = importlib.util.spec_from_file_location("_tkd_test", TOOLS / "tu_khoi_dong.py")
tkd = importlib.util.module_from_spec(spec_tkd)
sys.modules["_tkd_test"] = tkd
spec_tkd.loader.exec_module(tkd)


def _ghi_log(p: Path, *, ngay_lui: int, tong_the: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f"===== 2026-01-01 00:00:00 : BẮT ĐẦU quét =====\n"
        f"===== 2026-01-01 00:00:01 : KẾT THÚC — bước (1)=0, tổng thể={tong_the} =====\n",
        encoding="utf-8",
    )
    if ngay_lui:
        moc = (_dt.datetime.now() - _dt.timedelta(days=ngay_lui)).timestamp()
        import os
        os.utime(p, (moc, moc))


class TestLanChayCuoiNhanBaTang:
    def test_khong_can_lap_lai_duoc_doc_dung(self, tmp_path):
        log = tmp_path / "quarterly_superseded.log"
        _ghi_log(log, ngay_lui=0, tong_the="KHÔNG CẦN LẶP LẠI")
        _ngay, tt = kdt.lan_chay_cuoi(log)
        assert tt == "KHONG_CAN_LAP_LAI"

    def test_loi_that_van_la_loi(self, tmp_path):
        log = tmp_path / "quarterly_superseded.log"
        _ghi_log(log, ngay_lui=0, tong_the="CÓ BƯỚC LỖI")
        _ngay, tt = kdt.lan_chay_cuoi(log)
        assert tt == "LỖI"

    def test_pass_van_la_pass(self, tmp_path):
        log = tmp_path / "quarterly_superseded.log"
        _ghi_log(log, ngay_lui=0, tong_the="PASS")
        _ngay, tt = kdt.lan_chay_cuoi(log)
        assert tt == "PASS"


class TestQuaHanKhongHamNongNcbiVoIch:
    def test_khong_can_lap_lai_trong_han_khong_bi_phong_lai(self, tmp_path, monkeypatch):
        """Lượt cuối CHUA_DO/MAU/KHONG_CO_CONG_CU, mới 5 ngày (< han_ngay=92) — KHÔNG
        được coi là cần chạy lại NGAY, khác hành vi cũ (LỖI ⇒ phóng lại bất kể ngày)."""
        log = tmp_path / "quarterly_superseded.log"
        _ghi_log(log, ngay_lui=5, tong_the="KHÔNG CẦN LẶP LẠI")
        owner_gia = {"quy": {"script": tmp_path / "x.sh", "log": log, "han_ngay": 92, "ten": "quét quý"}}
        monkeypatch.setattr(tkd, "OWNER", owner_gia)
        ra = tkd.qua_han()
        assert ra == [], "trong hạn ⇒ không cần phóng lại, tránh hâm nóng NCBI vô ích"

    def test_khong_can_lap_lai_qua_han_van_duoc_thu_lai(self, tmp_path, monkeypatch):
        """Quá 92 ngày thì VẪN thử lại — tất định không có nghĩa là vĩnh viễn không
        cần đo lại, chỉ là không cần đo lại NGAY LẬP TỨC mỗi phiên."""
        log = tmp_path / "quarterly_superseded.log"
        _ghi_log(log, ngay_lui=100, tong_the="KHÔNG CẦN LẶP LẠI")
        owner_gia = {"quy": {"script": tmp_path / "x.sh", "log": log, "han_ngay": 92, "ten": "quét quý"}}
        monkeypatch.setattr(tkd, "OWNER", owner_gia)
        ra = tkd.qua_han()
        assert len(ra) == 1 and ra[0][0] == "quy"

    def test_loi_that_van_phong_lai_ngay_bat_ke_ngay(self, tmp_path, monkeypatch):
        """Hồi quy: LỖI thật (mạng hỏng…) vẫn phải phóng lại NGAY, kể cả mới 1 ngày —
        hành vi này KHÔNG được đổi bởi bản vá thêm nhãn KHONG_CAN_LAP_LAI."""
        log = tmp_path / "quarterly_superseded.log"
        _ghi_log(log, ngay_lui=1, tong_the="CÓ BƯỚC LỖI")
        owner_gia = {"quy": {"script": tmp_path / "x.sh", "log": log, "han_ngay": 92, "ten": "quét quý"}}
        monkeypatch.setattr(tkd, "OWNER", owner_gia)
        ra = tkd.qua_han()
        assert len(ra) == 1 and ra[0][0] == "quy"

    def test_pass_trong_han_khong_bi_phong_lai(self, tmp_path, monkeypatch):
        log = tmp_path / "quarterly_superseded.log"
        _ghi_log(log, ngay_lui=5, tong_the="PASS")
        owner_gia = {"quy": {"script": tmp_path / "x.sh", "log": log, "han_ngay": 92, "ten": "quét quý"}}
        monkeypatch.setattr(tkd, "OWNER", owner_gia)
        ra = tkd.qua_han()
        assert ra == []


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
