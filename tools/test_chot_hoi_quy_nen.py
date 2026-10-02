#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy HV-01 (02/10/2026): hook chốt hồi quy phải ĐỌC kết quả nền, không chạy trọn bộ chốt trong 30 giây.

Lỗi gốc đo được: hook `timeout: 30` mà bộ chốt cần 46–55 giây ⇒ hết hạn ở 18/19 phiên từ 24/09; lệnh kết thúc
bằng `; true` và chế độ `--im-khi-on` im lặng nên «bị cắt giữa chừng» đọc GIỐNG HỆT «mọi chốt xanh».
Kiểm HÀNH VI: không có đường nào im lặng ngoài «xanh THẬT và còn mới». Offline, không chạy bộ chốt thật."""
from __future__ import annotations

import importlib.util as _ilu
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = _ilu.spec_from_file_location("chot_nen", REPO / "tools" / "chot_hoi_quy_nen.py")
nen = _ilu.module_from_spec(_spec)
sys.modules["chot_nen"] = nen
_spec.loader.exec_module(nen)

BAY_GIO = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)


def _kq(trang_thai="XANH", gio_truoc=1.0, head="aaa", bao_cao=""):
    return {"schema": 1, "trang_thai": trang_thai, "bao_cao": bao_cao, "head": head,
            "ket_thuc": (BAY_GIO - timedelta(hours=gio_truoc)).isoformat()}


# ---- danh_gia: hàm thuần ------------------------------------------------------------------------------------------
def test_chua_co_ket_qua_la_chua_do_khong_phai_xanh():
    loai, msg, moi = nen.danh_gia(None, BAY_GIO, "aaa")
    assert loai == "CHUA_DO" and moi is True and msg


def test_xanh_con_moi_thi_im_va_khong_lam_moi():
    assert nen.danh_gia(_kq("XANH", 1.0), BAY_GIO, "aaa") == ("XANH_IM", "", False)


def test_xanh_cu_hon_72h_la_chua_do_khong_phai_xanh():
    loai, msg, moi = nen.danh_gia(_kq("XANH", 80.0), BAY_GIO, "aaa")
    assert loai == "CHUA_DO" and moi is True and "80" in msg


def test_xanh_vua_qua_6h_im_nhung_xin_lam_moi():
    loai, _msg, moi = nen.danh_gia(_kq("XANH", 7.0), BAY_GIO, "aaa")
    assert loai == "XANH_IM" and moi is True


def test_doi_head_xin_lam_moi_du_ket_qua_con_moi():
    assert nen.danh_gia(_kq("XANH", 0.5, head="aaa"), BAY_GIO, "bbb")[2] is True


def test_head_rong_khong_coi_la_da_doi():
    assert nen.danh_gia(_kq("XANH", 0.5, head="aaa"), BAY_GIO, "")[2] is False
    assert nen.danh_gia(_kq("XANH", 0.5, head=""), BAY_GIO, "bbb")[2] is False


def test_do_in_nguyen_bao_cao_kem_gio_do():
    loai, msg, _ = nen.danh_gia(_kq("DO", 2.0, bao_cao="🔴 CHỐT HỒI QUY: 1 BÀI HỌC TÁI PHÁT\n  ✗ BH99 x"), BAY_GIO, "aaa")
    assert loai == "DO" and "BH99" in msg and "2 giờ trước" in msg


def test_loi_la_chua_do_va_noi_ro_loi():
    loai, msg, moi = nen.danh_gia(_kq("LOI", 1.0, bao_cao="quá hạn 900 giây"), BAY_GIO, "aaa")
    assert loai == "CHUA_DO" and "quá hạn 900" in msg and moi is True


def test_dau_thoi_gian_tuong_lai_khong_duoc_tin():
    assert nen.danh_gia(_kq("XANH", -3.0), BAY_GIO, "aaa")[0] == "CHUA_DO"


def test_dau_thoi_gian_hong_la_chua_do():
    kq = _kq("XANH")
    kq["ket_thuc"] = "không-phải-ngày"
    assert nen.danh_gia(kq, BAY_GIO, "aaa")[0] == "CHUA_DO"


# ---- doc_ket_qua / đĩa --------------------------------------------------------------------------------------------
@pytest.fixture()
def state(tmp_path, monkeypatch):
    monkeypatch.setattr(nen, "THU_MUC_STATE", tmp_path / "state")
    monkeypatch.setattr(nen, "TEP_KET_QUA", tmp_path / "state" / "kq.json")
    monkeypatch.setattr(nen, "TEP_KHOA", tmp_path / "state" / "khoa")
    monkeypatch.setattr(nen, "head_hien_tai", lambda: "aaa")
    return tmp_path / "state"


@pytest.mark.parametrize("noi_dung", ["", "{hỏng", "[]", '{"trang_thai": "XANH"}',
                                      '{"trang_thai": "OK", "ket_thuc": "2026-10-02T00:00:00+00:00"}',
                                      '{"trang_thai": "XANH", "ket_thuc": 5}'])
def test_ket_qua_hong_thi_none(state, noi_dung):
    state.mkdir(parents=True)
    nen.TEP_KET_QUA.write_text(noi_dung, encoding="utf-8")
    assert nen.doc_ket_qua() is None


def test_thieu_tep_thi_none(state):
    assert nen.doc_ket_qua() is None


def _doc_va_bao(monkeypatch, state, kq, im=True, bay_gio=BAY_GIO):
    """Chạy chế độ hook với kết quả cho trước; trả (mã, stdout, số lần phóng nền)."""
    if kq is not None:
        state.mkdir(parents=True, exist_ok=True)
        nen.TEP_KET_QUA.write_text(json.dumps(kq), encoding="utf-8")
    monkeypatch.setattr(nen, "_bay_gio", lambda: bay_gio)
    so_phong = []
    monkeypatch.setattr(nen.subprocess, "Popen", lambda *a, **k: so_phong.append((a, k)))
    return so_phong


def test_hook_xanh_moi_im_lang_ma_0_khong_phong(monkeypatch, state, capsys):
    phong = _doc_va_bao(monkeypatch, state, _kq("XANH", 1.0))
    assert nen.doc_va_bao(True) == nen.MA_XANH
    assert capsys.readouterr().out == "" and phong == []


def test_hook_chua_co_ket_qua_in_vang_ma_2_va_phong_nen(monkeypatch, state, capsys):
    phong = _doc_va_bao(monkeypatch, state, None)
    assert nen.doc_va_bao(True) == nen.MA_CHUA_DO
    out = capsys.readouterr().out
    assert "CHƯA ĐO ĐƯỢC" in out and "KHÔNG đọc là «xanh»" in out and "chạy nền" in out
    assert len(phong) == 1
    args, kw = phong[0]
    assert args[0][0] == sys.executable and args[0][-1] == "--chay"
    assert kw["stdout"] is subprocess.DEVNULL and kw["stdin"] is subprocess.DEVNULL
    if os.name != "nt":
        assert kw.get("start_new_session") is True  # tách khỏi hook để hook không chờ


def test_hook_do_in_bao_cao_ma_1(monkeypatch, state, capsys):
    _doc_va_bao(monkeypatch, state, _kq("DO", 2.0, bao_cao="  ✗ BH77 một lỗi tái phát"))
    assert nen.doc_va_bao(True) == nen.MA_DO
    out = capsys.readouterr().out
    assert "BH77" in out and "🔴" in out


def test_hook_cu_hon_72h_khong_im_lang(monkeypatch, state, capsys):
    _doc_va_bao(monkeypatch, state, _kq("XANH", 100.0))
    assert nen.doc_va_bao(True) == nen.MA_CHUA_DO
    assert "CHƯA ĐO ĐƯỢC" in capsys.readouterr().out


def test_khong_im_khi_on_van_noi_khi_xanh(monkeypatch, state, capsys):
    _doc_va_bao(monkeypatch, state, _kq("XANH", 1.0))
    assert nen.doc_va_bao(False) == nen.MA_XANH
    assert "xanh" in capsys.readouterr().out


# ---- khoá & phóng nền ---------------------------------------------------------------------------------------------
def test_khoa_con_han_thi_khong_phong_them(monkeypatch, state):
    phong = _doc_va_bao(monkeypatch, state, None)
    state.mkdir(parents=True, exist_ok=True)
    nen.TEP_KHOA.write_text("123", encoding="utf-8")
    os.utime(nen.TEP_KHOA, (time.time(), time.time()))
    monkeypatch.setattr(nen, "_bay_gio", lambda: datetime.now(timezone.utc))
    assert nen.phong_nen() is False and phong == []


def test_khoa_mo_coi_qua_20_phut_thi_phong(monkeypatch, state):
    phong = _doc_va_bao(monkeypatch, state, None)
    state.mkdir(parents=True, exist_ok=True)
    nen.TEP_KHOA.write_text("123", encoding="utf-8")
    cu = time.time() - 3600
    os.utime(nen.TEP_KHOA, (cu, cu))
    monkeypatch.setattr(nen, "_bay_gio", lambda: datetime.now(timezone.utc))
    assert nen.phong_nen() is True and len(phong) == 1


# ---- chạy trọn bộ chốt (chặn) -------------------------------------------------------------------------------------
class _KetQuaGia:
    def __init__(self, ma, out="", err=""):
        self.returncode, self.stdout, self.stderr = ma, out, err


def _chay(monkeypatch, state, gia):
    monkeypatch.setattr(nen.subprocess, "run", gia)
    monkeypatch.setattr(nen, "_bay_gio", lambda: datetime.now(timezone.utc))
    return nen.chay_tron_bo_chot()


def _doc_tep():
    return json.loads(nen.TEP_KET_QUA.read_text(encoding="utf-8"))


def test_chay_xanh_ghi_ket_qua_va_go_khoa(monkeypatch, state):
    assert _chay(monkeypatch, state, lambda *a, **k: _KetQuaGia(0, "")) == 0
    d = _doc_tep()
    assert d["trang_thai"] == "XANH" and d["ma_thoat"] == 0 and d["schema"] == 1
    assert not nen.TEP_KHOA.exists(), "khoá phải được gỡ sau lượt chạy"


def test_chay_do_giu_bao_cao(monkeypatch, state):
    bao = "🔴 CHỐT HỒI QUY: 1 BÀI HỌC TÁI PHÁT\n  ✗ BH12 [x] y"
    _chay(monkeypatch, state, lambda *a, **k: _KetQuaGia(1, bao))
    d = _doc_tep()
    assert d["trang_thai"] == "DO" and "BH12" in d["bao_cao"]


def test_chay_ma_la_la_loi_khong_phai_xanh(monkeypatch, state):
    _chay(monkeypatch, state, lambda *a, **k: _KetQuaGia(2, "", "Traceback ... SyntaxError"))
    d = _doc_tep()
    assert d["trang_thai"] == "LOI" and "SyntaxError" in d["bao_cao"]


def test_chay_qua_han_la_loi(monkeypatch, state):
    def het_han(*a, **k):
        raise subprocess.TimeoutExpired(cmd="x", timeout=1)
    _chay(monkeypatch, state, het_han)
    d = _doc_tep()
    assert d["trang_thai"] == "LOI" and "quá hạn" in d["bao_cao"]


def test_chay_khong_khoi_dong_duoc_la_loi(monkeypatch, state):
    def hong(*a, **k):
        raise OSError("không có python")
    _chay(monkeypatch, state, hong)
    assert _doc_tep()["trang_thai"] == "LOI"
    assert not nen.TEP_KHOA.exists()


def test_chay_khi_co_luot_khac_thi_bo_qua_khong_ghi_de(monkeypatch, state):
    state.mkdir(parents=True)
    nen.TEP_KHOA.write_text("999", encoding="utf-8")
    goi = []
    ma = _chay(monkeypatch, state, lambda *a, **k: goi.append(1) or _KetQuaGia(0))
    assert ma == 3 and goi == [] and not nen.TEP_KET_QUA.exists()


def test_kq_do_roi_doc_lai_thanh_do_khong_tro_thanh_xanh(monkeypatch, state):
    """Vòng đầu–cuối: chạy nền ra ĐỎ ⇒ hook phiên sau PHẢI báo đỏ (không im lặng)."""
    _chay(monkeypatch, state, lambda *a, **k: _KetQuaGia(1, "  ✗ BH5 tái phát"))
    loai, msg, _ = nen.danh_gia(nen.doc_ket_qua(), datetime.now(timezone.utc), "aaa")
    assert loai == "DO" and "BH5" in msg


# ---- bản khai hook trong git --------------------------------------------------------------------------------------
def test_hook_sessionstart_goi_ban_doc_nen_khong_goi_bo_chot_tron():
    """Chặn quay lại lỗi gốc: lệnh hook KHÔNG được chạy trực tiếp `chot_hoi_quy_bai_hoc.py` (46–55 s > timeout)."""
    cfg = json.loads((REPO / "sync" / "hooks-sessionstart.json").read_text(encoding="utf-8"))
    lenh = [h for m in cfg["SessionStart"] for h in m["hooks"] if "chot_hoi_quy" in h["command"]]
    assert len(lenh) == 1, "phải có đúng MỘT hook chốt hồi quy"
    h = lenh[0]
    assert "tools/chot_hoi_quy_nen.py --doc --im-khi-on" in h["command"]
    assert "chot_hoi_quy_bai_hoc.py" not in h["command"], "hook chạy trọn bộ chốt ⇒ bị cắt ở timeout, lưới an toàn mù"
    assert h["timeout"] <= 30
