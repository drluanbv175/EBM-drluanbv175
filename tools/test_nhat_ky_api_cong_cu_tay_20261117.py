#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hai công cụ chạy tay (quét lạc chủ đề toàn kho · CAFÉ-S) ghi sức khoẻ lượt gọi API cho hòm việc — 17/11/2026.

Khoá: thành công ⇒ ok (làm mới mốc 14 ngày của giác quan) · thiếu khoá ⇒ skipped · lỗi kênh API ⇒ error, và công cụ
dừng GỌN (không văng traceback) · lỗi phía máy ⇒ không ghi · dưới pytest không bao giờ ghi tệp THẬT. Khách API giả —
không gọi mạng, không tốn tiền.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _nap(ten: str, duong: Path):
    spec = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


NK = _nap("_nk_kiem_20261117", HERE / "nhat_ky_api_claude.py")


@pytest.fixture
def nhat_ky(tmp_path, monkeypatch):
    tep = tmp_path / "suc-khoe.json"
    monkeypatch.setenv("EBM_NHAT_KY_API", str(tep))
    return tep


def _doc(tep: Path) -> dict:
    return json.loads(tep.read_text(encoding="utf-8"))


# ─────────────────── mô-đun ghi ───────────────────

def test_ghi_dung_khuon_va_nguon(nhat_ky):
    NK.ghi("ok", "", 5, "quet_lac_chu_de_kho")
    d = _doc(nhat_ky)
    # 17/11 (mục 2): thêm «theo_nguon» (lượt gần nhất theo từng công cụ) — vẫn KHỚP CHẶT, không trường lạ.
    assert set(d) == {"luc", "trang_thai", "ly_do", "so_muc", "nguon", "theo_nguon"}
    assert set(d["theo_nguon"]) == {"quet_lac_chu_de_kho"}
    assert set(d["theo_nguon"]["quet_lac_chu_de_kho"]) == {"luc", "trang_thai", "ly_do", "so_muc"}
    assert (d["trang_thai"], d["so_muc"], d["nguon"]) == ("ok", 5, "quet_lac_chu_de_kho")


def test_duoi_pytest_khong_ghi_tep_that(monkeypatch):
    """★ Một lượt CI/kiểm trên máy bác sĩ không được ghi đè nhật ký THẬT (BH181)."""
    monkeypatch.delenv("EBM_NHAT_KY_API", raising=False)
    assert NK._duoi_pytest_cham_that(NK._NK_THAT) is True


def test_loi_ghi_khong_lam_vo_luot_chay(tmp_path):
    NK.ghi("ok", tep=str(tmp_path / "khong" / "co" / "thu-muc" / "nk.json"))   # không được ném


# ─────────────────── quét lạc chủ đề toàn kho ───────────────────

QT = _nap("_quet_kho_nk_kiem", HERE / "test_quet_lac_chu_de_kho_20261117.py")


class TestQuetToanKho(QT._CoSo):
    def setUp(self):
        super().setUp()
        self.mp = pytest.MonkeyPatch()
        self.tep = self.goc / "suc-khoe.json"
        self.mp.setenv("EBM_NHAT_KY_API", str(self.tep))

    def tearDown(self):
        self.mp.undo()
        super().tearDown()

    def test_thanh_cong_ghi_ok_so_muc_that(self):
        cli = QT._ClientBatch({"d001": QT._thanh_cong(QT.JSON_A), "d002": QT._thanh_cong(QT.JSON_B)})
        self.assertEqual(self._chay("--ap-dung", client=cli), 0)
        d = _doc(self.tep)
        self.assertEqual((d["trang_thai"], d["nguon"], d["so_muc"]), ("ok", "quet_lac_chu_de_kho", 4))

    def test_gui_batch_loi_dung_gon_va_ghi_error(self):
        """★ Trước đây 401/429 lúc gửi batch văng traceback và hòm việc không biết."""
        cli = QT._ClientBatch({})

        def _hong(requests):
            raise RuntimeError("Error code: 401 - authentication_error")

        cli.messages.batches.create = _hong
        self.assertEqual(self._chay("--ap-dung", client=cli), 2)
        d = _doc(self.tep)
        self.assertEqual(d["trang_thai"], "error")
        self.assertIn("401", d["ly_do"])
        self.assertIn("gửi batch", d["ly_do"])

    def test_moi_yeu_cau_deu_loi_la_error(self):
        loi = types.SimpleNamespace(type="errored", error=types.SimpleNamespace(type="overloaded"))
        cli = QT._ClientBatch({"d001": loi, "d002": loi})
        self._chay("--ap-dung", client=cli)
        d = _doc(self.tep)
        self.assertEqual(d["trang_thai"], "error")
        self.assertIn("overloaded", d["ly_do"])

    def test_mot_phan_hong_van_la_ok_vi_khoa_song(self):
        cli = QT._ClientBatch({"d001": QT._thanh_cong("{cụt", stop="max_tokens"), "d002": QT._thanh_cong(QT.JSON_B)})
        self._chay("--ap-dung", client=cli)
        self.assertEqual(_doc(self.tep)["trang_thai"], "ok")

    def test_thieu_khoa_ghi_skipped(self):
        self.assertEqual(self._chay("--ap-dung"), 2)     # dưới pytest rào của cổng chặn kho khoá thật
        d = _doc(self.tep)
        self.assertEqual(d["trang_thai"], "skipped")
        self.assertIn("ANTHROPIC_API_KEY", d["ly_do"])

    def test_chay_kho_khong_ghi_gi(self):
        self.assertEqual(self._chay(), 0)
        self.assertFalse(self.tep.exists())


# ─────────────────── CAFÉ-S ───────────────────

CS = _nap("_cafes_nk_kiem_20261117", HERE / "eval" / "cafes_suite.py")


def _agent(so_luot: int, nhat_ky=()):
    return types.SimpleNamespace(so_luot=so_luot, nhat_ky=list(nhat_ky))


def test_cafes_co_luot_tra_ve_la_ok(nhat_ky):
    CS.ghi_suc_khoe_luot(agent=_agent(32))
    d = _doc(nhat_ky)
    assert (d["trang_thai"], d["so_muc"], d["nguon"]) == ("ok", 32, "cafes_suite")


def test_cafes_moi_luot_loi_api_la_error(nhat_ky):
    CS.ghi_suc_khoe_luot(agent=_agent(0, [{"khong_do": "lỗi API RateLimitError: 429"}]))
    d = _doc(nhat_ky)
    assert d["trang_thai"] == "error" and "429" in d["ly_do"]


def test_cafes_thieu_khoa_la_skipped(nhat_ky):
    CS.ghi_suc_khoe_luot(loi=CS.CauHinhSai("Thiếu ANTHROPIC_API_KEY (biến môi trường lẫn kho bí mật)"))
    assert _doc(nhat_ky)["trang_thai"] == "skipped"


def test_cafes_loi_xac_thuc_sdk_la_error(nhat_ky, monkeypatch):
    monkeypatch.setattr(CS, "_cac_loi_cau_hinh", lambda: (PermissionError,))
    try:
        try:
            raise PermissionError("403 permission_error")
        except PermissionError as goc:
            raise CS.CauHinhSai("PermissionDeniedError: 403 — dừng cả lượt.") from goc
    except CS.CauHinhSai as e:
        CS.ghi_suc_khoe_luot(loi=e)
    assert _doc(nhat_ky)["trang_thai"] == "error"


def test_cafes_loi_phia_may_khong_ghi(nhat_ky):
    CS.ghi_suc_khoe_luot(loi=CS.CauHinhSai("Không thấy tệp agent x.md — chạy tiếp là đo model TRẦN"))
    assert not nhat_ky.exists()


def test_cafes_main_api_noi_day_ghi_suc_khoe(nhat_ky, monkeypatch):
    """Đầu–cuối nhánh --api: lỗi cấu hình phải đi qua bộ ghi (không chỉ hàm ghi đúng mà main có GỌI)."""
    def _khong_khoa(*a, **k):
        raise CS.CauHinhSai("Thiếu ANTHROPIC_API_KEY (biến môi trường lẫn kho bí mật) — không chạy được --api.")

    monkeypatch.setattr(CS, "ClaudeAPIAgent", _khong_khoa)
    monkeypatch.setattr(sys, "argv", ["cafes_suite.py", "--api", "--luu-dau-ra", str(nhat_ky.parent / "ra")])
    assert CS.main() == 2
    assert _doc(nhat_ky)["trang_thai"] == "skipped"


# ─────────────────── giác quan ───────────────────

@pytest.mark.parametrize("nguon, nhan, lenh", [("quet_lac_chu_de_kho", "quét lạc chủ đề toàn kho", "quet_lac_chu_de_kho.py"),
                                               ("cafes_suite", "CAFÉ-S", "cafes_suite.py")])
def test_giac_quan_bao_dung_cong_cu(tmp_path, nguon, nhan, lenh):
    tdx = _nap(f"_tdx_nk_{nguon}", HERE / "tu_de_xuat_viec.py")
    tep = tmp_path / "nk.json"
    NK.ghi("error", "Error code: 401", 0, nguon, tep=str(tep))
    uu, _ai, dong, lenh_goi = tdx.giac_quan_api_claude(tep)[0]
    assert uu == 1 and nhan in dong and lenh in lenh_goi


def test_cafes_main_api_thanh_cong_ghi_ok(nhat_ky, monkeypatch):
    """Đầu–cuối nhánh --api THÀNH CÔNG: lượt chạy thật (khách giả) phải làm mới nhật ký «ok» — đột biến «main không
    ghi ok» trước đây lọt vì chỉ nhánh lỗi có chốt."""
    tao = types.SimpleNamespace(create=lambda **kw: types.SimpleNamespace(
        stop_reason="end_turn", stop_details=None, content=[types.SimpleNamespace(type="text", text="Không có cờ đỏ.")],
        usage=types.SimpleNamespace(input_tokens=10, output_tokens=5, cache_creation_input_tokens=0,
                                    cache_read_input_tokens=0)))
    khach = types.SimpleNamespace(beta=types.SimpleNamespace(messages=tao), messages=tao)
    that = CS.ClaudeAPIAgent
    monkeypatch.setattr(CS, "ClaudeAPIAgent", lambda d, effort="high": that(d, effort=effort, client=khach))
    monkeypatch.setattr(sys, "argv", ["cafes_suite.py", "--api", "--luu-dau-ra", str(nhat_ky.parent / "ra")])
    assert CS.main() == 0
    d = _doc(nhat_ky)
    assert (d["trang_thai"], d["nguon"]) == ("ok", "cafes_suite") and d["so_muc"] == len(CS.TEST_CASES)
