#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy canh mạng + VPN (27/10/2026): Kaspersky VPN rớt lúc 15:28 ⇒ «No network route» tới khi bác sĩ khởi động lại 17:18.

Kiểm HÀNH VI: đọc đúng đầu ra scutil; mất mạng luôn ĐỎ (kể cả khi scutil báo VPN «Connected»); không đo được ⇒ KHONG_DO (không xanh);
phát lại đúng ca 27/10 ⇒ nhắc ở phút thứ 2, tự nối lại ≤ 2 lần cách ≥ 10 phút, ghi sự cố 1 giờ 50 phút, báo hồi phục; chớp tắt một mẫu
không là sự cố; VPN tắt mà có mạng CHỈ nhắc (không tự bật); tạm dừng ⇒ không nhắc/không nối lại nhưng vẫn ghi; đổi máy chủ được ghi;
hook phiên im khi ổn, báo khi có chuyện, đo lại nguồn khi đổi máy chủ; công cụ không xoá/giết gì. Ngoại tuyến, không chạm mạng/scutil thật."""
from __future__ import annotations

import ast
import importlib.util as _ilu
import json
import plistlib
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = _ilu.spec_from_file_location("canh_mang_vpn", REPO / "tools" / "canh_mang_vpn.py")
cm = _ilu.module_from_spec(_spec)
sys.modules["canh_mang_vpn"] = cm
_spec.loader.exec_module(cm)

NWI_CO_VPN = """Network information

IPv4 network interface information
   utun4 : flags      : 0x7 (IPv4,IPv6,DNS)
           address    : 172.21.56.207
           VPN server : 103.107.199.164
           reach      : 0x00000003 (Reachable,Transient Connection)
     en1 : flags      : 0x7 (IPv4,IPv6,DNS)
           address    : 192.168.1.11
           reach      : 0x00000002 (Reachable)

   REACH : flags 0x00000003 (Reachable,Transient Connection)

Network interfaces: utun4 en1
"""
NWI_KHONG_VPN = "Network information\n\n     en1 : flags : 0x7\n\nNetwork interfaces: en1\n"
T0 = 1_793_000_000.0  # mốc giả cố định


@pytest.fixture(autouse=True)
def _state_tam(monkeypatch, tmp_path):
    """MỌI test ghi vào thư mục tạm — không bao giờ chạm state/ thật của repo (bài học canh_dia 03/10)."""
    monkeypatch.setattr(cm, "THU_MUC", tmp_path)
    for ten in ("TEP_STATE", "TEP_SU_CO", "TEP_TAM_DUNG", "TEP_PHIEN", "TEP_DO_NGUON", "TEP_LOG_DO_NGUON", "BAN_CAI"):
        monkeypatch.setattr(cm, ten, tmp_path / Path(getattr(cm, ten)).name)
    monkeypatch.setattr(cm, "thong_bao_he_thong", lambda *a, **k: (_ for _ in ()).throw(AssertionError("thông báo thật trong test")))
    monkeypatch.setattr(cm, "noi_lai_vpn", lambda *a, **k: (_ for _ in ()).throw(AssertionError("scutil thật trong test")))
    monkeypatch.setattr(cm, "khoi_dong_do_nguon", lambda: (_ for _ in ()).throw(AssertionError("đo nguồn thật trong test")))
    return tmp_path


def _do(t, vpn="Connected", co_mang=True, vat_ly=("en1",), may_chu="aaaa1111"):
    return {"t": t, "do_duoc": True, "vpn": vpn, "co_mang": co_mang, "vat_ly": None if vat_ly is None else list(vat_ly),
            "may_chu": may_chu}


def _chay_chuoi(mau, st=None, tam_dung_den=0.0):
    st = st or {}
    tat_ca = []
    for d in mau:
        st, viec = cm.buoc(st, d, tam_dung_den)
        tat_ca.append((d["t"], viec))
    return st, tat_ca


# ---- đọc đầu ra scutil -------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("ra,mong", [("Connected\nExtended Status <dictionary> {\n", "Connected"), ("Disconnected\n", "Disconnected"),
                                     ("Reasserting\n", "Reasserting"), ("No service\n", None), ("", None)])
def test_doc_trang_thai_vpn(ra, mong):
    assert cm.doc_trang_thai_vpn(ra) == mong


def test_doc_nwi_co_vpn_bam_may_chu_va_bo_giao_dien_duong_ham():
    may_chu, vat_ly = cm.doc_nwi(NWI_CO_VPN)
    assert may_chu == cm.bam("103.107.199.164") and len(may_chu) == 8 and "103.107" not in may_chu
    assert vat_ly == ["en1"]


def test_doc_nwi_khong_vpn_va_khong_giao_dien():
    assert cm.doc_nwi(NWI_KHONG_VPN) == (None, ["en1"])
    assert cm.doc_nwi("Network interfaces:\n") == (None, [])
    assert cm.doc_nwi("") == (None, None)


def test_do_mang_dung_lenh_gia_va_ket_noi_gia():
    def chay(lenh):
        return "Connected\n" if "status" in lenh else NWI_CO_VPN
    d = cm.do_mang(chay=chay, ket_noi=lambda: False, nen_tang="darwin", bay_gio=T0)
    assert d["do_duoc"] and d["vpn"] == "Connected" and d["co_mang"] is False and d["vat_ly"] == ["en1"]


def test_do_mang_khong_phai_mac_hoac_khong_co_scutil_la_khong_do():
    assert cm.do_mang(nen_tang="win32")["do_duoc"] is False
    assert cm.do_mang(chay=lambda _lenh: "", ket_noi=lambda: True, nen_tang="darwin")["do_duoc"] is False


# ---- phân loại ---------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("vpn,co_mang,vat_ly,mong", [
    ("Connected", True, ("en1",), "ON"),
    ("Disconnected", True, ("en1",), "VPN_TAT"),
    (None, True, ("en1",), "VPN_TAT"),
    ("Reasserting", True, ("en1",), "VPN_DANG_NOI"),
    ("Disconnected", False, ("en1",), "MAT_MANG"),
    ("Connected", False, ("en1",), "MAT_MANG"),   # đường hầm chết mà scutil vẫn «Connected» ⇒ vẫn ĐỎ
    ("Disconnected", False, (), "MAT_MANG"),
])
def test_phan_loai(vpn, co_mang, vat_ly, mong):
    assert cm.phan_loai(_do(T0, vpn, co_mang, vat_ly))[0] == mong


def test_khong_do_duoc_khong_bao_gio_la_xanh():
    assert cm.phan_loai({"t": T0, "do_duoc": False, "ly_do": "x"})[0] == "KHONG_DO"
    assert cm.MA_THOAT["KHONG_DO"] == 3


def test_khong_co_wifi_ghi_ro_ly_do():
    assert "Wi-Fi" in cm.phan_loai(_do(T0, "Disconnected", False, ()))[1]


# ---- phát lại ca 27/10 -------------------------------------------------------------------------------------------------
def test_phat_lai_ca_27_10_nhac_som_noi_lai_ghi_su_co_va_bao_hoi_phuc():
    """15:27 ổn → 15:28–17:17 mất mạng, VPN Disconnected, vẫn có Wi-Fi (110 mẫu) → 17:18 có mạng lại."""
    mau = [_do(T0)] + [_do(T0 + 60 * i, "Disconnected", False) for i in range(1, 111)] + [_do(T0 + 60 * 111)]
    st, tat_ca = _chay_chuoi(mau)
    viec = [(t, v) for t, ds in tat_ca for v in ds]
    nhac = [t for t, v in viec if v[0] == "thong_bao" and "mất kết nối" in v[1]]
    noi = [(t, v[1]) for t, v in viec if v[0] == "noi_lai"]
    ghi = [v[1] for t, v in viec if v[0] == "ghi"]
    assert nhac[0] == T0 + 120, "phải nhắc ở mẫu xấu thứ 2 (≈ phút thứ 2), không đợi tới khi bác sĩ tự phát hiện"
    assert all(b - a >= cm.KHOANG_NHAC_MAT_MANG_GIAY for a, b in zip(nhac, nhac[1:])), "nhắc lặp phải cách ≥ 15 phút"
    assert len(nhac) == 8
    assert noi == [(T0 + 120, "bat"), (T0 + 120 + 600, "bat")], "tự bật VPN ≤ 2 lần, cách ≥ 10 phút"
    assert len(ghi) == 1 and ghi[0]["loai"] == "MAT_MANG" and ghi[0]["giay"] == 110 * 60
    assert ghi[0]["vpn_luc_dau"] == "Disconnected" and len(ghi[0]["noi_lai"]) == 2
    assert any(v[0] == "thong_bao" and "hồi phục" in v[1] for t, v in viec if t == T0 + 60 * 111)
    assert st["su_co"] is None and st["mau_cuoi"]["muc"] == "ON"


def test_chop_tat_mot_mau_khong_la_su_co():
    _st, tat_ca = _chay_chuoi([_do(T0), _do(T0 + 60, "Disconnected", False), _do(T0 + 120)])
    assert not [v for _t, ds in tat_ca for v in ds]


def test_vpn_connected_ma_mat_mang_cho_3_mau_roi_ngat_bat():
    mau = [_do(T0 + 60 * i, "Connected", False) for i in range(4)]
    _st, tat_ca = _chay_chuoi(mau)
    noi = [(t, v[1]) for t, ds in tat_ca for v in ds if v[0] == "noi_lai"]
    assert noi == [(T0 + 120, "ngat_bat")]


def test_khong_co_wifi_thi_khong_dung_toi_vpn_va_nhac_kiem_wifi():
    mau = [_do(T0 + 60 * i, "Disconnected", False, ()) for i in range(5)]
    _st, tat_ca = _chay_chuoi(mau)
    viec = [v for _t, ds in tat_ca for v in ds]
    assert not [v for v in viec if v[0] == "noi_lai"]
    assert any(v[0] == "thong_bao" and "Wi-Fi" in v[2] for v in viec)


def test_vpn_tat_ma_co_mang_chi_nhac_khong_tu_bat_va_doi_5_mau():
    mau = [_do(T0 + 60 * i, "Disconnected", True) for i in range(70)] + [_do(T0 + 60 * 70)]
    _st, tat_ca = _chay_chuoi(mau)
    viec = [(t, v) for t, ds in tat_ca for v in ds]
    assert not [v for _t, v in viec if v[0] == "noi_lai"], "VPN tắt có thể là bác sĩ cố ý — không tự bật"
    nhac = [t for t, v in viec if v[0] == "thong_bao" and v[1] == "VPN đang tắt"]
    assert nhac == [T0 + 240, T0 + 240 + 3600]
    assert any(v[0] == "thong_bao" and v[1] == "VPN đã bật lại" for _t, v in viec)
    assert [v[1]["loai"] for _t, v in viec if v[0] == "ghi"] == ["VPN_TAT"]


def test_tam_dung_khong_nhac_khong_noi_lai_nhung_van_ghi_su_co():
    mau = [_do(T0 + 60 * i, "Disconnected", False) for i in range(20)] + [_do(T0 + 60 * 20)]
    _st, tat_ca = _chay_chuoi(mau, tam_dung_den=T0 + 10 ** 6)
    viec = [v for _t, ds in tat_ca for v in ds]
    assert [v[0] for v in viec] == ["ghi"] and viec[0][1]["loai"] == "MAT_MANG"


def test_doi_may_chu_vpn_duoc_ghi():
    _st, tat_ca = _chay_chuoi([_do(T0, may_chu="aaaa1111"), _do(T0 + 60, may_chu="bbbb2222")])
    ghi = [v[1] for _t, ds in tat_ca for v in ds if v[0] == "ghi"]
    assert ghi == [{"loai": "DOI_MAY_CHU", "luc": T0 + 60, "truoc": "aaaa1111", "sau": "bbbb2222"}]


def test_khong_do_duoc_giu_nguyen_su_co_dang_mo():
    st, _ = _chay_chuoi([_do(T0 + 60 * i, "Disconnected", False) for i in range(3)])
    st2, viec = cm.buoc(st, {"t": T0 + 300, "do_duoc": False, "ly_do": "scutil hỏng"})
    assert not viec and st2["su_co"]["so_mau"] == 3 and st2["mau_cuoi"]["muc"] == "KHONG_DO"


# ---- chạy nền + tệp -----------------------------------------------------------------------------------------------------
def test_chay_nen_ghi_state_va_su_co_vao_thu_muc_tam(monkeypatch, tmp_path):
    goi = []
    monkeypatch.setattr(cm, "thong_bao_he_thong", lambda td, nd: goi.append(("tb", td)) or True)
    monkeypatch.setattr(cm, "noi_lai_vpn", lambda kieu: goi.append(("noi", kieu)) or "Connected")
    for i in range(3):
        cm.chay_nen(_do(T0 + 60 * i, "Disconnected", False))
    assert cm.chay_nen(_do(T0 + 180)) == 0
    assert ("noi", "bat") in goi and ("tb", "MẠNG — mất kết nối") in goi
    ban_ghi = cm.doc_su_co(0)
    assert len(ban_ghi) == 1 and ban_ghi[0]["noi_lai"][0]["ket_qua"] == "Connected"
    assert json.loads(cm.TEP_STATE.read_text(encoding="utf-8"))["mau_cuoi"]["muc"] == "ON"
    assert str(cm.TEP_STATE).startswith(str(tmp_path))


def test_chay_nen_ton_trong_tam_dung(monkeypatch):
    cm.ghi_json({"den": T0 + 10 ** 6}, cm.TEP_TAM_DUNG)
    for i in range(5):
        cm.chay_nen(_do(T0 + 60 * i, "Disconnected", False))   # thông báo/nối lại thật sẽ ném AssertionError


def test_doc_su_co_bo_dong_hong_va_loc_theo_moc(tmp_path):
    cm.TEP_SU_CO.write_text('{"loai":"MAT_MANG","ket_thuc":10}\nrác\n{"loai":"DOI_MAY_CHU","luc":5}\n', encoding="utf-8")
    assert [b["loai"] for b in cm.doc_su_co(6)] == ["MAT_MANG"]
    assert len(cm.doc_su_co(0)) == 2


def test_state_hong_thi_rong(tmp_path):
    cm.TEP_STATE.write_text("{hỏng", encoding="utf-8")
    assert cm.doc_json(cm.TEP_STATE) == {}


def test_noi_lai_vpn_ngat_roi_bat_dung_dich_vu():
    _spec2 = _ilu.spec_from_file_location("canh_mang_vpn_goc", REPO / "tools" / "canh_mang_vpn.py")
    goc = _ilu.module_from_spec(_spec2)
    _spec2.loader.exec_module(goc)
    lenh = []

    def chay(mot):
        lenh.append(mot)
        return "Connected\n" if mot[2] == "status" else ""
    assert goc.noi_lai_vpn("ngat_bat", chay=chay, ngu=lambda s: None) == "Connected"
    assert [x[2] for x in lenh] == ["stop", "start", "status"] and all(x[-1] == goc.TEN_VPN for x in lenh)


# ---- hook phiên ---------------------------------------------------------------------------------------------------------
def test_doc_phien_im_khi_on(monkeypatch, capsys):
    monkeypatch.setattr(cm, "da_cai_launchd", lambda: True)
    cm.ghi_json({"mau_cuoi": {"t": T0, "muc": "ON", "ly_do": "ok", "may_chu": None}}, cm.TEP_STATE)
    assert cm.doc_cho_phien(True, False, bay_gio=T0 + 30) == 0
    assert capsys.readouterr().out == ""


def test_doc_phien_bao_mat_mang_24_gio(monkeypatch, capsys):
    monkeypatch.setattr(cm, "da_cai_launchd", lambda: True)
    cm.ghi_json({"mau_cuoi": {"t": T0, "muc": "ON", "ly_do": "ok"}}, cm.TEP_STATE)
    cm.ghi_su_co({"loai": "MAT_MANG", "bat_dau": T0 - 7000, "ket_thuc": T0 - 400, "giay": 6600,
                  "noi_lai": [{"kieu": "bat", "ket_qua": "Disconnected"}]})
    assert cm.doc_cho_phien(True, False, bay_gio=T0 + 30) == 2
    out = capsys.readouterr().out
    assert "mất mạng 1 lần" in out and "1 giờ 50 phút" in out and "0/1" in out


def test_doc_phien_nen_chua_cai_thi_nhac_cai_va_do_nhanh(monkeypatch, capsys):
    monkeypatch.setattr(cm, "da_cai_launchd", lambda: False)
    assert cm.doc_cho_phien(True, False, bay_gio=T0, do=_do(T0)) == 1
    assert "--cai-launchd --ap-dung" in capsys.readouterr().out


def test_doc_phien_khong_do_duoc_la_trang(monkeypatch, capsys):
    assert cm.doc_cho_phien(True, False, bay_gio=T0, do={"t": T0, "do_duoc": False, "ly_do": "chỉ canh được trên macOS"}) == 3
    assert "⚪" in capsys.readouterr().out


def test_doi_may_chu_thi_do_lai_nguon_o_nen_mot_lan(monkeypatch, capsys):
    monkeypatch.setattr(cm, "da_cai_launchd", lambda: True)
    phong = []
    monkeypatch.setattr(cm, "khoi_dong_do_nguon", lambda: phong.append(1) or (True, ""))
    cm.ghi_json({"mau_cuoi": {"t": T0, "muc": "ON", "ly_do": "ok", "may_chu": "bbbb2222"}}, cm.TEP_STATE)
    cm.ghi_json({"may_chu_da_do": "aaaa1111", "do_luc": T0 - 7200}, cm.TEP_PHIEN)
    assert cm.doc_cho_phien(True, True, bay_gio=T0 + 10) == 1
    assert phong == [1] and "#aaaa1111 → #bbbb2222" in capsys.readouterr().out
    cm.doc_cho_phien(True, True, bay_gio=T0 + 20)
    assert phong == [1], "cùng máy chủ đã đo ⇒ không đo lại"


def test_dang_mat_mang_khong_phong_do_nguon(monkeypatch):
    monkeypatch.setattr(cm, "da_cai_launchd", lambda: True)
    cm.ghi_json({"mau_cuoi": {"t": T0, "muc": "MAT_MANG", "ly_do": "x", "may_chu": "bbbb2222"}}, cm.TEP_STATE)
    assert cm.doc_cho_phien(True, True, bay_gio=T0 + 10) == 2   # khoi_dong_do_nguon thật sẽ ném AssertionError


def test_bao_ket_qua_do_nguon_moi_mot_lan(monkeypatch, capsys):
    monkeypatch.setattr(cm, "da_cai_launchd", lambda: True)
    cm.ghi_json({"mau_cuoi": {"t": T0, "muc": "ON", "ly_do": "ok", "may_chu": "bbbb2222"}}, cm.TEP_STATE)
    cm.ghi_json({"may_chu_da_do": "bbbb2222", "do_luc": T0}, cm.TEP_PHIEN)
    cm.ghi_json({"mang": {"luc": "2026-10-27T12:15:52+00:00"}, "nguon": {
        "NCBI E-utilities (PubMed)": {"ket_qua": "ncbi-chan"}, "Crossref": {"ket_qua": "OK"},
        "BJGP — RSS": {"ket_qua": "cloudflare-chan"}}}, cm.TEP_DO_NGUON)
    cm.doc_cho_phien(True, True, bay_gio=T0 + 10)
    out = capsys.readouterr().out
    assert "1/3 tới được" in out and "BJGP — RSS (cloudflare-chan)" in out and "PubMed/NCBI bị chặn" in out
    cm.doc_cho_phien(True, True, bay_gio=T0 + 20)
    assert capsys.readouterr().out == "", "kết quả đo đã báo thì không lặp lại mỗi phiên"


def test_bao_cao_tong_hop(monkeypatch):
    cm.ghi_json({"mau_cuoi": {"t": T0, "muc": "ON", "ly_do": "có mạng, đi qua VPN"}}, cm.TEP_STATE)
    cm.ghi_su_co({"loai": "MAT_MANG", "bat_dau": T0 - 7000, "ket_thuc": T0 - 400, "giay": 6600, "vpn_luc_dau": "Disconnected",
                  "noi_lai": [{"kieu": "bat", "ket_qua": "Connected"}]})
    cm.ghi_su_co({"loai": "DOI_MAY_CHU", "luc": T0 - 100, "truoc": "a", "sau": "b"})
    s = cm.bao_cao(7, bay_gio=T0 + 30)
    assert "Mất mạng: 1 lần" in s and "thành công 1" in s and "Đổi máy chủ VPN: 1 lần" in s and "bat→Connected" in s


# ---- launchd + an toàn --------------------------------------------------------------------------------------------------
def test_plist_chay_moi_phut_che_do_nen():
    d = plistlib.loads(cm.tao_plist("/usr/bin/python3", Path("/x/tools/canh_mang_vpn.py")))
    assert d["StartInterval"] == 60 and d["ProgramArguments"][-1] == "--chay-nen" and d["Label"] == cm.NHAN_LAUNCHD


def test_cai_launchd_mac_dinh_chay_kho(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cm.sys, "platform", "darwin")
    monkeypatch.setattr(cm.Path, "home", classmethod(lambda c: tmp_path))
    monkeypatch.setattr(cm.os, "getuid", lambda: 501, raising=False)
    monkeypatch.setattr(cm.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError("chạy khô mà gọi launchctl")))
    assert cm.cai_launchd(False, False) == 0
    assert not (tmp_path / "Library").exists() and "CHẠY KHÔ" in capsys.readouterr().out


def test_cai_launchd_khong_phai_mac(monkeypatch):
    monkeypatch.setattr(cm.sys, "platform", "win32")
    assert cm.cai_launchd(True, False) == 3


def test_cong_cu_chi_do_bao_va_chi_dung_vpn():
    """Không xoá tệp/thư mục, không giết tiến trình, không đổi cấu hình mạng; scutil chỉ đọc/bật/tắt dịch vụ VPN."""
    nguon = (REPO / "tools" / "canh_mang_vpn.py").read_text(encoding="utf-8")
    cay = ast.parse(nguon)
    goi = {f"{n.func.value.id}.{n.func.attr}" for n in ast.walk(cay)
           if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)}
    assert not goi & {"shutil.rmtree", "os.remove", "os.kill", "os.killpg", "os.rmdir"}
    for cam in ("networksetup", "ifconfig", "killall", "pkill", "--set "):
        assert cam not in nguon, f"công cụ canh không được đổi cấu hình mạng/giết tiến trình: {cam}"


def test_ham_doc_tep_theo_luc_goi_khong_chot_luc_import():
    """Hàm đọc/ghi phải lấy TEP_* LÚC GỌI (mặc định None), không chốt đường dẫn thật làm giá trị mặc định."""
    cay = ast.parse((REPO / "tools" / "canh_mang_vpn.py").read_text(encoding="utf-8"))
    for n in ast.walk(cay):
        if isinstance(n, ast.FunctionDef):
            for mac_dinh in n.args.defaults + n.args.kw_defaults:
                assert not (isinstance(mac_dinh, ast.Name) and mac_dinh.id.startswith("TEP_")), n.name


def _ban_goc():
    sp = _ilu.spec_from_file_location("canh_mang_vpn_mac_dinh", REPO / "tools" / "canh_mang_vpn.py")
    m = _ilu.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def test_state_mac_dinh_nam_ngoai_repo_onedrive():
    """Agent nền ghi MỖI PHÚT: state trong cây OneDrive sẽ bắt OneDrive đồng bộ liên tục (máy từng kẹt vòng lặp log, BH149)."""
    m = _ban_goc()
    for ten in ("TEP_STATE", "TEP_SU_CO", "TEP_TAM_DUNG", "TEP_PHIEN", "TEP_DO_NGUON", "TEP_LOG_DO_NGUON", "BAN_CAI"):
        duong = Path(getattr(m, ten)).resolve()
        assert REPO.resolve() not in duong.parents, f"{ten} nằm trong repo: {duong}"
        assert "CloudStorage" not in duong.parts and "OneDrive" not in str(duong), f"{ten} nằm trong OneDrive: {duong}"


def test_cai_that_chep_ban_chay_ra_ngoai_va_plist_tro_ban_chep(monkeypatch, tmp_path):
    monkeypatch.setattr(cm.sys, "platform", "darwin")
    monkeypatch.setattr(cm.Path, "home", classmethod(lambda c: tmp_path))
    monkeypatch.setattr(cm.os, "getuid", lambda: 501, raising=False)
    lenh = []

    class _R:
        returncode, stderr = 0, ""
    monkeypatch.setattr(cm.subprocess, "run", lambda mot, **k: lenh.append(mot) or _R())
    assert cm.cai_launchd(True, False) == 0
    assert cm.BAN_CAI.read_bytes() == (REPO / "tools" / "canh_mang_vpn.py").read_bytes()
    plist = plistlib.loads((tmp_path / "Library" / "LaunchAgents" / f"{cm.NHAN_LAUNCHD}.plist").read_bytes())
    assert plist["ProgramArguments"][1] == str(cm.BAN_CAI)
    assert ["launchctl", "bootstrap", "gui/501", str(tmp_path / "Library" / "LaunchAgents" / f"{cm.NHAN_LAUNCHD}.plist")] in lenh


def test_hook_bao_ban_chay_nen_cu(monkeypatch, capsys):
    monkeypatch.setattr(cm, "da_cai_launchd", lambda: True)
    cm.BAN_CAI.write_text("# bản cũ\n", encoding="utf-8")
    cm.ghi_json({"mau_cuoi": {"t": T0, "muc": "ON", "ly_do": "ok"}}, cm.TEP_STATE)
    assert cm.doc_cho_phien(True, False, bay_gio=T0 + 5) == 1
    assert "bản CŨ" in capsys.readouterr().out
