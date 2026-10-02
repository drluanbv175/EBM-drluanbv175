#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy canh đĩa + log OneDrive (02/10/2026): vòng lặp log OneDrive tái diễn lần thứ ba mà không có gì báo sớm.

Đo 02/10: log 20,7–24 GB, 24.796 tệp, ~54 tệp/phút, OneDrive 131% CPU. Kiểm HÀNH VI của hàm thuần `phan_loai` và các bảo đảm:
không đo được ⇒ KHÔNG_ĐO (không xanh); tốc độ chỉ tính khi có mẫu trước 2 phút–3 giờ; thông báo chống lặp; công cụ KHÔNG xoá gì.
Offline, không chạm OneDrive thật."""
from __future__ import annotations

import importlib.util as _ilu
import plistlib
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = _ilu.spec_from_file_location("canh_dia", REPO / "tools" / "canh_dia_onedrive.py")
cd = _ilu.module_from_spec(_spec)
sys.modules["canh_dia"] = cd
_spec.loader.exec_module(cd)

GIB, MIB = cd.GIB, cd.MIB


def _mau(t=1000.0, dia_gib=100.0, log_mb=1.0, tep=10, co_log=True, do_do=False):
    return {"t": t, "dia_trong": int(dia_gib * GIB), "dia_tong": 228 * GIB, "co_log": co_log,
            "log_tep": tep if co_log else None, "log_byte": int(log_mb * MIB) if co_log else None, "do_do": do_do}


# ---- ngưỡng tĩnh ----------------------------------------------------------------------------------------------------
def test_binh_thuong_la_xanh():
    assert cd.phan_loai(_mau(), None) == ("XANH", [])


@pytest.mark.parametrize("dia_gib,mong", [(9.9, "DO"), (10.0, "VANG"), (19.9, "VANG"), (20.0, "XANH"), (58.0, "XANH")])
def test_nguong_dia_trong(dia_gib, mong):
    assert cd.phan_loai(_mau(dia_gib=dia_gib), None)[0] == mong


@pytest.mark.parametrize("log_mb,mong", [(500, "XANH"), (1100, "VANG"), (8300, "DO"), (24000, "DO")])
def test_nguong_log_onedrive(log_mb, mong):
    assert cd.phan_loai(_mau(log_mb=log_mb, tep=24796), None)[0] == mong


def test_khong_do_duoc_dia_la_khong_do_khong_phai_xanh():
    m = _mau()
    m["dia_trong"] = None
    muc, ly = cd.phan_loai(m, None)
    assert muc == "KHONG_DO" and ly


def test_khong_thay_thu_muc_log_la_vang_khong_phai_xanh():
    muc, ly = cd.phan_loai(_mau(co_log=False), None)
    assert muc == "VANG" and any("KHÔNG biết" in x for x in ly)


def test_dem_do_dang_la_can_duoi_va_vang():
    muc, ly = cd.phan_loai(_mau(do_do=True), None)
    assert muc == "VANG" and any("CẬN DƯỚI" in x for x in ly)


# ---- tốc độ giữa hai mẫu ---------------------------------------------------------------------------------------------
def test_log_tang_nong_theo_tep_phut_la_do():
    truoc = _mau(t=1000.0, log_mb=10, tep=100)
    sau = _mau(t=1000.0 + 600, log_mb=12, tep=100 + 600 * 54 // 60)   # 54 tệp/phút (ca đo 02/10)
    muc, ly = cd.phan_loai(sau, truoc)
    assert muc == "DO" and any("TĂNG NÓNG" in x for x in ly)


def test_log_tang_nong_theo_mb_phut_la_do():
    truoc = _mau(t=1000.0, log_mb=10, tep=100)
    sau = _mau(t=1000.0 + 300, log_mb=10 + 5 * 200, tep=105)           # 200 MB/phút
    assert cd.phan_loai(sau, truoc)[0] == "DO"


def test_log_tang_cham_khong_bao_dong():
    truoc = _mau(t=1000.0, log_mb=10, tep=100)
    assert cd.phan_loai(_mau(t=1000.0 + 600, log_mb=11, tep=110), truoc)[0] == "XANH"


def test_dia_giam_nhanh_co_the_can_trong_2h_la_do():
    truoc = _mau(t=1000.0, dia_gib=50.0)
    sau = _mau(t=1000.0 + 600, dia_gib=50.0 - 800 * 10 / 1024)          # 800 MB/phút, còn ~42 GiB ⇒ cạn sau ~0,9 giờ
    muc, ly = cd.phan_loai(sau, truoc)
    assert muc == "DO" and any("cạn sau" in x for x in ly)


def test_dia_giam_vua_phai_chi_la_vang_vi_co_the_la_dong_bo():
    truoc = _mau(t=1000.0, dia_gib=58.0)
    sau = _mau(t=1000.0 + 600, dia_gib=58.0 - 200 * 10 / 1024)          # 200 MB/phút ⇒ ~4,7 giờ
    muc, ly = cd.phan_loai(sau, truoc)
    assert muc == "VANG" and any("đồng bộ" in x for x in ly)


@pytest.mark.parametrize("dt", [30, 119, 3 * 3600 + 10, -100])
def test_toc_do_chi_tinh_khi_mau_truoc_trong_cua_so_2_phut_3_gio(dt):
    truoc = _mau(t=1000.0, log_mb=1, tep=1, dia_gib=80.0)
    sau = _mau(t=1000.0 + dt, log_mb=9000, tep=900000, dia_gib=79.0)   # nhảy rất lớn nhưng khoảng cách mẫu không hợp lệ
    muc, ly = cd.phan_loai(sau, truoc)
    assert not any("TĂNG NÓNG" in x or "cạn sau" in x for x in ly), "không suy tốc độ từ hai mẫu quá gần/quá xa"
    assert muc == "DO"  # vẫn đỏ vì log tuyệt đối > 8 GiB — ngưỡng tĩnh không phụ thuộc mẫu trước


def test_mau_truoc_hong_hoac_thieu_khoa_khong_gay_sap():
    for truoc in ({}, {"t": None}, {"t": 900.0}, {"t": 900.0, "log_byte": None, "dia_trong": None}):
        assert cd.phan_loai(_mau(t=1500.0), truoc)[0] == "XANH"


# ---- thông báo chống lặp -----------------------------------------------------------------------------------------------
def test_chi_thong_bao_khi_do_va_cach_nhau_60_phut():
    assert cd.can_thong_bao("DO", {}, 10_000.0) is True
    assert cd.can_thong_bao("DO", {"thong_bao_luc": 10_000.0 - 300}, 10_000.0) is False
    assert cd.can_thong_bao("DO", {"thong_bao_luc": 10_000.0 - 3700}, 10_000.0) is True
    for muc in ("VANG", "XANH", "KHONG_DO"):
        assert cd.can_thong_bao(muc, {}, 10_000.0) is False


# ---- đếm thư mục & state -----------------------------------------------------------------------------------------------
def test_dem_thu_muc_dung_so_tep_va_byte(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.log").write_bytes(b"1" * 100)
    (tmp_path / "y.log").write_bytes(b"2" * 50)
    d = cd.dem_thu_muc([tmp_path])
    assert (d["tep"], d["byte"], d["do_do"]) == (2, 150, False)


def test_dem_thu_muc_het_han_bao_do_do_khong_im_lang_cat(tmp_path):
    for i in range(50):
        (tmp_path / f"{i}.log").write_text("x")
    assert cd.dem_thu_muc([tmp_path], han_giay=-1)["do_do"] is True


def test_dem_thu_muc_khong_ton_tai_la_0_khong_sap(tmp_path):
    assert cd.dem_thu_muc([tmp_path / "khong-co"]) == {"tep": 0, "byte": 0, "do_do": False}


def test_state_hong_thi_rong_khong_sap(tmp_path):
    p = tmp_path / "s.json"
    for noi_dung in ("", "{hỏng", "[]"):
        p.write_text(noi_dung, encoding="utf-8")
        assert cd.doc_state(p) == {}
    assert cd.doc_state(tmp_path / "khong-co.json") == {}


def test_ghi_state_nguyen_tu_va_doc_lai(tmp_path):
    p = tmp_path / "state" / "s.json"
    cd.ghi_state({"muc": "XANH", "mau": {"t": 1.0}}, p)
    assert cd.doc_state(p)["muc"] == "XANH" and list(p.parent.glob("*.tmp*")) == []


# ---- main đầu–cuối trên mẫu giả -----------------------------------------------------------------------------------------
def _chay_main(monkeypatch, tmp_path, mau, truoc_state=None, argv=()):
    monkeypatch.setattr(cd, "TEP_STATE", tmp_path / "s.json")
    monkeypatch.setattr(cd, "do_mau", lambda *a, **k: mau)
    monkeypatch.setattr(cd, "doc_state", lambda *a, **k: truoc_state or {})
    return cd.main(list(argv))


def test_main_xanh_im_lang_ma_0(monkeypatch, tmp_path, capsys):
    assert _chay_main(monkeypatch, tmp_path, _mau(t=time.time()), argv=["--im-khi-on"]) == 0
    assert capsys.readouterr().out == ""


def test_main_do_in_huong_dan_va_ma_2_khong_xoa_gi(monkeypatch, tmp_path, capsys):
    mau = _mau(t=time.time(), log_mb=24000, tep=24796)
    assert _chay_main(monkeypatch, tmp_path, mau, argv=["--im-khi-on"]) == 2
    out = capsys.readouterr().out
    assert "🔴" in out and "Sync Issues" in out and "KHÔNG bấm Reset" in out and "không xoá gì" in out


def test_main_khong_do_duoc_la_ma_3_va_in_trang(monkeypatch, tmp_path, capsys):
    m = _mau(t=time.time())
    m["dia_trong"] = None
    assert _chay_main(monkeypatch, tmp_path, m, argv=["--im-khi-on"]) == 3
    assert "⚪" in capsys.readouterr().out


def test_main_thong_bao_chi_goi_mot_lan_trong_60_phut(monkeypatch, tmp_path):
    goi = []
    monkeypatch.setattr(cd, "thong_bao_he_thong", lambda nd: goi.append(nd) or True)
    mau = _mau(t=time.time(), log_mb=24000, tep=24796)
    _chay_main(monkeypatch, tmp_path, mau, argv=["--thong-bao"])
    assert len(goi) == 1
    _chay_main(monkeypatch, tmp_path, mau, truoc_state={"thong_bao_luc": mau["t"] - 120}, argv=["--thong-bao"])
    assert len(goi) == 1, "lượt sau 2 phút không được thông báo lại"


# ---- launchd ----------------------------------------------------------------------------------------------------------
def test_plist_chay_moi_5_phut_chi_do_va_bao():
    d = plistlib.loads(cd.tao_plist("/usr/bin/python3", Path("/x/tools/canh_dia_onedrive.py")))
    assert d["Label"] == cd.NHAN_LAUNCHD and d["StartInterval"] == 300 and d["RunAtLoad"] is True
    assert d["ProgramArguments"] == ["/usr/bin/python3", "/x/tools/canh_dia_onedrive.py", "--im-khi-on", "--thong-bao"]
    assert not any(k in d for k in ("KeepAlive", "WatchPaths"))


def test_cai_launchd_mac_dinh_la_chay_kho_khong_ghi_gi(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cd.sys, "platform", "darwin")
    monkeypatch.setattr(cd.Path, "home", classmethod(lambda c: tmp_path))
    chay = []
    monkeypatch.setattr(cd.subprocess, "run", lambda *a, **k: chay.append(a) or None)
    assert cd.cai_launchd(False, False) == 0 and cd.cai_launchd(False, True) == 0
    assert chay == [] and not (tmp_path / "Library").exists(), "chạy khô không được ghi/gọi launchctl"
    assert "CHẠY KHÔ" in capsys.readouterr().out


def test_cai_launchd_khong_phai_mac_la_mo_ta_ro_khong_gia_vo(monkeypatch, capsys):
    monkeypatch.setattr(cd.sys, "platform", "win32")
    assert cd.cai_launchd(True, False) == 3 and "Task Scheduler" in capsys.readouterr().out


def test_cong_cu_khong_co_lenh_xoa_hay_dung_tien_trinh():
    """Chốt chặn tính CHỈ ĐO: mã nguồn không được gọi xoá tệp/giết tiến trình (trừ gỡ plist của chính nó)."""
    nguon = (REPO / "tools" / "canh_dia_onedrive.py").read_text(encoding="utf-8")
    import ast
    cay = ast.parse(nguon)
    goi = {f"{n.func.value.id}.{n.func.attr}" for n in ast.walk(cay)
           if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)}
    cam = {"shutil.rmtree", "os.remove", "os.kill", "os.killpg"}
    assert not (goi & cam), goi & cam
    assert ".unlink" in nguon and nguon.count(".unlink(") <= 1, "unlink chỉ dùng để gỡ plist của chính công cụ"
