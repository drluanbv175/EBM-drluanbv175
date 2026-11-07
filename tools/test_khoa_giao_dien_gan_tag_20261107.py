# -*- coding: utf-8 -*-
"""Khoá PHIÊN GIAO DIỆN khi gắn tag EndNote (07/11/2026).

Sự cố đo thật 07/11: khoá ghi `khoa_ghi_endnote` giữ theo tiến trình, phiên kéo-thả gắn tag gồm nhiều lượt công cụ ⇒ giữa hai
lượt (rảnh ≥ 20 giây) phiên khác nhập bản ghi bằng AppleScript ⇒ EndNote đổi vùng chọn ⇒ bản ghi 9046 bị gắn nhầm «CAD»; một
lần show/highlight của phiên khác cũng đổi danh sách. Kiểm: (1) nhận diện khoá phiên giao diện của tiến trình KHÁC; (2)
`--giu-khoa` giữ khoá suốt phiên, nhả khi dừng, không chiếm khi tiến trình khác đang giữ; (3) `--nha-khoa` chỉ dừng đúng tiến
trình giữ khoá phiên giao diện, không đụng khoá khác; (4) `EndNoteMac.hien_ban_ghi` của phiên khác bị từ chối khi khoá đó còn
hiệu lực, còn `--hien` của chính phiên gắn tag được phép; (5) `--cho-vao-nhom` báo ⚪ thay vì traceback."""
from __future__ import annotations

import importlib.util
import json
import os
import signal
import time
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


G = _nap("_gte_khoa_test", "gan_tag_endnote.py")
N = _nap("_nap_khoa_gd_test", "nap_endnote_chu_de.py")
K = N.nap_khoa_ghi()
CHA = os.getppid()  # tiến trình khác CÒN SỐNG (không bao giờ gửi tín hiệu thật cho nó — mọi `gui` đều giả)


def _khoa(tep: Path, pid: int, ly_do: str, tuoi: float = 0) -> None:
    tep.write_text(json.dumps({"pid": pid, "luc_epoch": time.time() - tuoi, "ly_do": ly_do}, ensure_ascii=False), encoding="utf-8")


# ───────────────────────── (1) nhận diện ─────────────────────────

def test_khoa_giao_dien_khac(tmp_path):
    tep = tmp_path / "khoa.json"
    assert K.khoa_giao_dien_khac(tep) is None
    _khoa(tep, CHA, K.LY_DO_GIAO_DIEN + " — tối đa 30 phút")
    assert K.khoa_giao_dien_khac(tep)["pid"] == CHA
    _khoa(tep, CHA, "nạp chủ đề X")                                   # khoá ghi thường ⇒ không phải phiên giao diện
    assert K.khoa_giao_dien_khac(tep) is None
    _khoa(tep, os.getpid(), K.LY_DO_GIAO_DIEN)                         # khoá của CHÍNH tiến trình ⇒ không chặn mình
    assert K.khoa_giao_dien_khac(tep) is None
    _khoa(tep, CHA, K.LY_DO_GIAO_DIEN, tuoi=K.HAN_KHOA + 5)            # quá hạn ⇒ coi như bỏ
    assert K.khoa_giao_dien_khac(tep) is None


# ───────────────────────── (2) giữ khoá ─────────────────────────

def test_giu_khoa_suot_phien_roi_nha(tmp_path):
    tep = tmp_path / "khoa.json"
    dung, thay = {"co": False}, []

    def ngu(_giay):
        d = json.loads(tep.read_text(encoding="utf-8"))
        thay.append((d["pid"], d["ly_do"]))
        if len(thay) >= 3:
            dung["co"] = True

    ra = []
    assert G.giu_khoa_giao_dien(30, kg=K, tep=tep, ngu=ngu, dung=dung, dang_dung=lambda: False, in_ra=ra.append) == G.MA_OK
    assert len(thay) == 3 and all(p == os.getpid() and ly.startswith(K.LY_DO_GIAO_DIEN) for p, ly in thay)
    assert not tep.exists(), "phải nhả khoá khi phiên dừng"
    assert ra[0].startswith("✓ đang giữ") and ra[-1].startswith("✓ đã nhả")


def test_giu_khoa_het_han_tu_nha(tmp_path):
    tep = tmp_path / "khoa.json"
    gio = [0.0]

    def ngu(giay):
        gio[0] += giay

    assert G.giu_khoa_giao_dien(1, kg=K, tep=tep, ngu=ngu, dong_ho=lambda: gio[0], dung={"co": False},
                                dang_dung=lambda: False, in_ra=lambda *_: None) == G.MA_OK
    assert gio[0] >= 60 and not tep.exists()


def test_ngu_tung_giay_de_nha_khoa_kip_thoi_va_van_lam_moi(tmp_path, monkeypatch):
    """Đo thật 07/11: ngủ một lèo 30 s ⇒ SIGTERM chỉ có hiệu lực khi hết giấc (PEP 475). Mỗi giấc ≤ 1 s; khoá vẫn được làm mới."""
    tep = tmp_path / "khoa.json"
    gio, giac, lam_moi = [0.0], [], []
    goc = K.cho_phep_ghi_loi

    def dem(*a, **kw):
        lam_moi.append(gio[0])
        return goc(*a, **kw)

    monkeypatch.setattr(K, "cho_phep_ghi_loi", dem)

    def ngu(giay):
        giac.append(giay)
        gio[0] += giay

    assert G.giu_khoa_giao_dien(2, kg=K, tep=tep, ngu=ngu, dong_ho=lambda: gio[0], dung={"co": False},
                                dang_dung=lambda: False, in_ra=lambda *_: None) == G.MA_OK
    assert giac and max(giac) <= 1.0, "mỗi giấc phải ≤ 1 giây (số tuyệt đối — không so với hằng số của chính mã)"
    assert len(lam_moi) >= 1 + int(120 // G.NHIP_LAM_MOI) - 1, "khoá phải được làm mới định kỳ (HAN_KHOA 15 phút)"


def test_khong_chiem_khoa_cua_tien_trinh_khac(tmp_path):
    tep = tmp_path / "khoa.json"
    _khoa(tep, CHA, "nạp chủ đề X")
    gio = [0.0]

    def ngu(giay):
        gio[0] += giay

    ra = []
    assert G.giu_khoa_giao_dien(30, kg=K, tep=tep, ngu=ngu, dong_ho=lambda: gio[0], dung={"co": False},
                                dang_dung=lambda: False, in_ra=ra.append) == G.MA_KHONG_DO
    assert json.loads(tep.read_text(encoding="utf-8"))["pid"] == CHA and ra[0].startswith("⚪")


# ───────────────────────── (3) nhả khoá ─────────────────────────

def test_nha_khoa_chi_dung_tien_trinh_giao_dien(tmp_path):
    tep = tmp_path / "khoa.json"
    gui = []

    def gui_gia(pid, sig):
        gui.append((pid, sig))
        tep.unlink()

    assert G.nha_khoa_giao_dien(kg=K, tep=tep, gui=gui_gia, in_ra=lambda *_: None) == G.MA_OK and gui == []
    _khoa(tep, CHA, "nạp chủ đề X")
    assert G.nha_khoa_giao_dien(kg=K, tep=tep, gui=gui_gia, in_ra=lambda *_: None) == G.MA_THAM_SO and gui == []
    _khoa(tep, CHA, K.LY_DO_GIAO_DIEN + " — tối đa 30 phút")
    assert G.nha_khoa_giao_dien(kg=K, tep=tep, gui=gui_gia, ngu=lambda _s: None, in_ra=lambda *_: None) == G.MA_OK
    assert gui == [(CHA, signal.SIGTERM)]


# ───────────────────────── (4) show/highlight của phiên khác ─────────────────────────

def _en_gia():
    chay = []
    return types.SimpleNamespace(so_csdl=lambda: "csdl", ten="EndNote 2025",
                                 _chay=lambda *a: chay.append(a)), chay


def test_hien_ban_ghi_bi_chan_khi_phien_khac_dang_gan_tag(tmp_path, monkeypatch):
    tep = tmp_path / "khoa.json"
    monkeypatch.setattr(K, "TEP_KHOA", tep)
    en, chay = _en_gia()
    N.EndNoteMac.hien_ban_ghi(en, [1, 2])                              # không có khoá ⇒ hiện được
    assert len(chay) == 1
    _khoa(tep, CHA, K.LY_DO_GIAO_DIEN + " — tối đa 30 phút")
    with pytest.raises(K.DangCoTienTrinhKhacGhi):
        N.EndNoteMac.hien_ban_ghi(en, [3])
    assert len(chay) == 1, "không được gửi AppleScript show/highlight chen"
    N.EndNoteMac.hien_ban_ghi(en, [3], trong_phien_gan_tag=True)       # --hien của CHÍNH phiên gắn tag
    assert len(chay) == 2
    _khoa(tep, CHA, "nạp chủ đề X")                                   # khoá ghi thường không chặn show/highlight
    N.EndNoteMac.hien_ban_ghi(en, [4])
    assert len(chay) == 3


def test_hien_cua_gan_tag_truyen_co_phien(monkeypatch, tmp_path):
    goi = {}

    class _En:
        def __init__(self, *_a):
            pass

        def dang_mo_dung_thu_vien(self):
            return True

        def hien_ban_ghi(self, rec, **kw):
            goi.update(rec=rec, **kw)

    kh = {"thieu": {G.TAG_AP_DUNG: [5, 6]}, "thu_vien": str(tmp_path / "x.enl")}
    assert G.hien_thieu(G.TAG_AP_DUNG, kh, endnote_cls=_En) == G.MA_CON_VIEC
    assert goi == {"rec": [5, 6], "trong_phien_gan_tag": True}


# ───────────────────────── (5) nối dây ─────────────────────────

def test_cho_vao_nhom_bao_khong_traceback():
    """Khớp DÒNG THI HÀNH: lời gọi hien_ban_ghi của --cho-vao-nhom nằm trong try, chỉ nuốt đúng DangCoTienTrinhKhacGhi."""
    dong = (REPO / "tools" / "nap_endnote_chu_de.py").read_text(encoding="utf-8").splitlines()
    i = next(k for k, d in enumerate(dong) if d.strip() == 'en.hien_ban_ghi(chon[0]["rec"])')
    assert dong[i - 1].strip() == "try:"
    assert 'if type(e).__name__ != "DangCoTienTrinhKhacGhi":' in dong[i + 2] and dong[i + 3].strip() == "raise"


def test_huong_dan_va_tham_so():
    assert "--giu-khoa 30" in G.HUONG_DAN and "--nha-khoa" in G.HUONG_DAN
    assert G.main(["--giu-khoa", "5", "--nha-khoa"]) == G.MA_THAM_SO
