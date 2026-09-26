# -*- coding: utf-8 -*-
"""Hồi quy 26/09/2026 (synthesis #38) — dò venv EBM đa nền: `bin/python` rồi `Scripts/python.exe`.

Lỗi: tu_sua_chua · dat_canh_chung_cu_moi · cap_nhat_plugin_tay chỉ dò `~/.ebm-venv/bin/python`
(bố cục POSIX). Trên Windows venv nằm ở `Scripts/python.exe` nên cả ba LẶNG LẼ rơi về python hệ
thống: mục tự Việt hoá plugin không bao giờ chạy mà vẫn báo sạch, cột rút bài luôn «chưa kiểm».
BH73 cũng mù vì chỉ kiểm `ts._VENV.exists()` (bố cục POSIX).

Mọi ca dựng HOME giả bằng tmp_path — không đụng venv thật, không gọi mạng/tiến trình con thật.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent


def _nap(ten_tep: str, ten_mod: str):
    spec = importlib.util.spec_from_file_location(ten_mod, _TOOLS / ten_tep)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten_mod] = mod
    spec.loader.exec_module(mod)
    return mod


def _home_gia(tmp_path: Path, *, bin_: bool = False, scripts: bool = False) -> Path:
    home = tmp_path / "home"
    goc = home / ".ebm-venv"
    if bin_:
        (goc / "bin").mkdir(parents=True)
        (goc / "bin" / "python").write_text("", encoding="utf-8")
    if scripts:
        (goc / "Scripts").mkdir(parents=True)
        (goc / "Scripts" / "python.exe").write_text("", encoding="utf-8")
    home.mkdir(exist_ok=True)
    return home


@pytest.fixture
def home_chi_scripts(tmp_path, monkeypatch):
    """HOME giả kiểu Windows: CHỈ có .ebm-venv/Scripts/python.exe; Path.home() trỏ vào đó."""
    home = _home_gia(tmp_path, scripts=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    assert Path.home() == home
    return home


# ---------- hàm dùng chung ----------

def test_chi_scripts_tra_dung_duong_scripts(tmp_path):
    bst = _nap("ban_sao_tran.py", "_bst_venv_20260926_a")
    home = _home_gia(tmp_path, scripts=True)
    assert bst.venv_python(home) == home / ".ebm-venv" / "Scripts" / "python.exe"


def test_chi_bin_tra_duong_bin(tmp_path):
    bst = _nap("ban_sao_tran.py", "_bst_venv_20260926_b")
    home = _home_gia(tmp_path, bin_=True)
    assert bst.venv_python(home) == home / ".ebm-venv" / "bin" / "python"


def test_ca_hai_uu_tien_bin_hanh_vi_mac_linux_khong_doi(tmp_path):
    bst = _nap("ban_sao_tran.py", "_bst_venv_20260926_c")
    home = _home_gia(tmp_path, bin_=True, scripts=True)
    assert bst.venv_python(home) == home / ".ebm-venv" / "bin" / "python"


def test_khong_co_venv_tra_none(tmp_path):
    bst = _nap("ban_sao_tran.py", "_bst_venv_20260926_d")
    assert bst.venv_python(_home_gia(tmp_path)) is None


def test_mac_dinh_dung_path_home(home_chi_scripts):
    bst = _nap("ban_sao_tran.py", "_bst_venv_20260926_e")
    assert bst.venv_python() == home_chi_scripts / ".ebm-venv" / "Scripts" / "python.exe"


# ---------- ba nơi dùng ----------

def test_tu_sua_chua_py_yaml_dung_venv_scripts(home_chi_scripts):
    ts = _nap("tu_sua_chua.py", "_tss_venv_20260926")
    ky_vong = home_chi_scripts / ".ebm-venv" / "Scripts" / "python.exe"
    assert ts.PY_YAML == str(ky_vong)
    # Lệnh SỬA của mục Việt hoá phải chạy bằng đúng trình thông dịch đó.
    muc = [v for v in ts.VIEC_MAY if any("apply_vi" in str(x) for x in (v[1] or []) + (v[2] or []))]
    assert muc and muc[0][2][0] == str(ky_vong)


def test_tu_sua_chua_khong_venv_lui_ve_sys_executable(tmp_path, monkeypatch):
    home = _home_gia(tmp_path)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    ts = _nap("tu_sua_chua.py", "_tss_venv_20260926_none")
    assert ts._VENV is None
    assert ts.PY_YAML == sys.executable


def test_dat_canh_tra_rut_bai_chay_bang_venv_scripts(home_chi_scripts, tmp_path, monkeypatch):
    dc = _nap("dat_canh_chung_cu_moi.py", "_dccm_venv_20260926")
    # repo giả có CLI kiểm rút bài của engine (vị trí lồng) để hàm đi tới lời gọi tiến trình con.
    repo = tmp_path / "repo"
    cli = repo / "medical-ebm-automation" / "tools" / "check_citation_retraction.py"
    cli.parent.mkdir(parents=True)
    cli.write_text("", encoding="utf-8")
    monkeypatch.setattr(dc, "REPO", repo)
    goi: list[list[str]] = []

    class _Kq:
        stdout = "{}"

    def _run_gia(lenh, **_kw):
        goi.append(list(lenh))
        return _Kq()

    monkeypatch.setattr(dc.subprocess, "run", _run_gia)
    nhan = dc._tra_rut_bai(["12345678"])
    assert goi, "không gọi CLI kiểm rút bài"
    assert goi[0][0] == str(home_chi_scripts / ".ebm-venv" / "Scripts" / "python.exe")
    # Không có phán quyết ⇒ vẫn «chưa kiểm» (KHÔNG BIẾT không thành ok).
    assert nhan["12345678"].startswith("⚠️ chưa kiểm")


def test_cap_nhat_plugin_tay_ap_vi_bang_venv_scripts(tmp_path, monkeypatch):
    cn = _nap("cap_nhat_plugin_tay.py", "_cnpt_venv_20260926")
    home = _home_gia(tmp_path, scripts=True)
    monkeypatch.setattr(cn, "HOME", home)
    monkeypatch.setattr(cn, "KHO_GOC", tmp_path / "kho-khong-co")
    goi: list[list[str]] = []

    def _chay_gia(lenh, cwd=None):
        goi.append(list(lenh))
        return 1, "gia"  # git clone «thất bại» ⇒ vòng lặp bỏ qua, đi thẳng tới bước Việt hoá

    monkeypatch.setattr(cn, "chay", _chay_gia)
    monkeypatch.setattr(sys, "argv", ["cap_nhat_plugin_tay.py", "--chi", "meta-pipe"])
    cn.main()
    buoc_vi = [lenh for lenh in goi if any(str(x).endswith(("apply_vi.py", "verify_vi.py")) for x in lenh)]
    assert len(buoc_vi) == 2
    for lenh in buoc_vi:
        assert lenh[0] == str(home / ".ebm-venv" / "Scripts" / "python.exe")


# ---------- BH73 không còn mù trên bố cục Windows ----------

def test_bh73_dat_tren_home_windows(home_chi_scripts):
    chot = _nap("chot_hoi_quy_bai_hoc.py", "_chot_bh73_venv_20260926")
    ok, ct = chot.bh73_viet_hoa_phai_tu_phuc_hoi_sau_cap_nhat_plugin()
    assert ok is True, ct


def test_bh73_bat_tu_sua_chua_cu_chi_do_bin_tren_windows(home_chi_scripts, monkeypatch):
    """Mô phỏng ĐÚNG lỗi cũ trên máy Windows: tu_sua_chua chỉ dò `bin/python` (không có) nên PY_YAML
    rơi về sys.executable, `_VENV` trỏ đường bin không tồn tại. BH73 cũ cho qua (so chuỗi «.ebm-venv»
    / `_VENV.exists()` False); BH73 mới dò cả Scripts ⇒ phải ĐỎ."""
    chot = _nap("chot_hoi_quy_bai_hoc.py", "_chot_bh73_venv_20260926_b")
    nap_that = chot._nap

    def _nap_gia(duong, ten):
        mod = nap_that(duong, ten)
        if Path(duong).name == "tu_sua_chua.py":
            mod._VENV = home_chi_scripts / ".ebm-venv" / "bin" / "python"  # không tồn tại
            for i, v in enumerate(mod.VIEC_MAY):
                if any("apply_vi" in str(x) for x in (v[1] or []) + (v[2] or [])):
                    kiem = [sys.executable] + list(v[1][1:])
                    sua = [sys.executable] + list(v[2][1:])
                    mod.VIEC_MAY[i] = (v[0], kiem, sua) + tuple(v[3:])
        return mod

    monkeypatch.setattr(chot, "_nap", _nap_gia)
    ok, ct = chot.bh73_viet_hoa_phai_tu_phuc_hoi_sau_cap_nhat_plugin()
    assert ok is False
    assert "trình thông dịch có PyYAML" in ct
