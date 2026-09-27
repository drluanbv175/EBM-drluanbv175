#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #17 (đợt dò nâng cấp 26/09/2026): 🟢 khi quét được 0 dashboard.

Tái hiện gốc: trên bản sao trần, `dang_ky_chu_de.py [--mau-thuan]` in «0 dashboard …» rồi «🟢 KHÔNG có mục nào
hai bản nói ngược nhau», thoát 0; `kiem_phan_hang.py` in «🟢 Mọi mức chứng cứ đều truy được…», thoát 0 — dù
CHƯA đọc một dashboard nào (nap_vd lùi về bản git-vendor từ 08/09 nên nhánh «⚪ Không kiểm được» thành mã chết).
Bước ⑤ của `chu_trinh_chung_cu` chỉ xử lý rc=1 nên tổng kết cũng im lặng.

Kiểm bằng lời gọi main() THẬT (DASH trỏ thư mục tạm) và bằng đầu ra THẬT của công cụ đưa vào chu_trinh.
Ngoại tuyến, không dữ liệu thật.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


DK = _nap("dk_khong_dash_20260926", ROOT / "tools" / "dang_ky_chu_de.py")
KPH = _nap("kph_khong_dash_20260926", ROOT / "tools" / "kiem_phan_hang.py")

DASHBOARD_MAU = ("<script>const DATA={items:[{id:'ITEM-01', pmid:'34101376', gradeLevel:'mod', gradeBy:'KDIGO 2024', "
                 "decision:'apply', source:'KDIGO', references:['KDIGO. PMID 34101376.']}]}</script>")


def _chay_main(mod, argv, capsys):
    with mock.patch.object(sys, "argv", argv):
        rc = mod.main()
    return rc, capsys.readouterr().out


@pytest.mark.parametrize("co_thu_muc", [False, True])
@pytest.mark.parametrize("che_do", [[], ["--mau-thuan"]])
def test_dang_ky_0_dashboard_la_trang_ma_2(tmp_path, monkeypatch, capsys, co_thu_muc, che_do):
    dash = tmp_path / "EBM-Dashboards"
    if co_thu_muc:
        dash.mkdir()           # máy thật mà OneDrive chưa tải về: thư mục có, 0 tệp
    monkeypatch.setattr(DK, "DASH", dash)
    rc, out = _chay_main(DK, ["dang_ky_chu_de.py", *che_do], capsys)
    assert rc == 2, out
    assert "⚪ Không kiểm được trên máy này" in out and "0 dashboard" in out
    assert "🟢" not in out, "chưa so dashboard nào mà in xanh"


def test_dang_ky_doi_chung_mot_dashboard_van_xanh(tmp_path, monkeypatch, capsys):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    (dash / "WebDashboard_EBM_VanDeCuThe_COPD_20260926.html").write_text(DASHBOARD_MAU, encoding="utf-8")
    monkeypatch.setattr(DK, "DASH", dash)
    rc, out = _chay_main(DK, ["dang_ky_chu_de.py", "--mau-thuan"], capsys)
    assert rc == 0 and "🟢 KHÔNG có mục nào hai bản nói ngược nhau" in out, out


def test_quet_kho_voi_dash_rieng_khong_bi_rao(tmp_path):
    """Rào chỉ ở main(): canary/bản đọc gọi quet_kho(dash) trong-tiến-trình vẫn nhận kết quả rỗng, không ném lỗi."""
    _vd, theo_lat_cat, theo_goc = DK.quet_kho(tmp_path)
    assert dict(theo_lat_cat) == {} and dict(theo_goc) == {}


def test_kiem_phan_hang_0_dashboard_la_trang_ma_2(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(KPH, "DASH", tmp_path / "EBM-Dashboards")
    rc, out = _chay_main(KPH, ["kiem_phan_hang.py"], capsys)
    assert rc == 2 and "⚪ Không kiểm được trên máy này" in out and "🟢" not in out, out
    rc, out = _chay_main(KPH, ["kiem_phan_hang.py", "--im-khi-on"], capsys)
    assert rc == 2 and out == "", "--im-khi-on được im lặng nhưng KHÔNG được trả 0"


def test_kiem_phan_hang_doi_chung_mot_dashboard_du_gradeby(tmp_path, monkeypatch, capsys):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    (dash / "WebDashboard_EBM_VanDeCuThe_COPD_20260926.html").write_text(DASHBOARD_MAU, encoding="utf-8")
    monkeypatch.setattr(KPH, "DASH", dash)
    rc, out = _chay_main(KPH, ["kiem_phan_hang.py"], capsys)
    assert rc == 0 and "🟢" in out and "1 item" in out, out


def test_kiem_phan_hang_thieu_verify_dashboard_tra_2(monkeypatch, capsys):
    monkeypatch.setattr(KPH, "_nap_vd", lambda: None)
    rc, out = _chay_main(KPH, ["kiem_phan_hang.py"], capsys)
    assert rc == 2 and "⚪" in out


def test_dash_do_ca_bo_cuc_anh_em(tmp_path):
    """DASH dùng duong_goc: có EBM-Dashboards cạnh repo (bố cục anh em) thì phải tìm thấy."""
    goc = tmp_path / "EBM-drluanbv175"
    (goc / "tools").mkdir(parents=True)
    for ten in ("dang_ky_chu_de.py", "kiem_phan_hang.py", "ban_sao_tran.py"):
        shutil.copy(ROOT / "tools" / ten, goc / "tools" / ten)
    (tmp_path / "EBM-Dashboards").mkdir()
    dk = _nap("dk_anh_em_20260926", goc / "tools" / "dang_ky_chu_de.py")
    kph = _nap("kph_anh_em_20260926", goc / "tools" / "kiem_phan_hang.py")
    assert dk.DASH == tmp_path / "EBM-Dashboards" and kph.DASH == tmp_path / "EBM-Dashboards"


# ── chu_trinh ⑤ với đầu ra THẬT của dang_ky_chu_de trên cây trần ─────────────────────────────────────────
def _dau_ra_that_ban_sao_tran(tmp: Path) -> tuple[int, str]:
    goc = tmp / "repo"
    (goc / "tools").mkdir(parents=True)
    for ten in ("dang_ky_chu_de.py", "ban_sao_tran.py"):
        shutil.copy(ROOT / "tools" / ten, goc / "tools" / ten)
    vendor = goc / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools"
    vendor.mkdir(parents=True)
    shutil.copy(ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py", vendor)
    p = subprocess.run([sys.executable, "-B", "tools/dang_ky_chu_de.py", "--mau-thuan"], cwd=str(goc),
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                       env={**os.environ, "PYTHONUTF8": "1"})
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def test_chu_trinh_buoc5_dau_ra_that_ra_trang(tmp_path, capsys):
    rc_dk, out_dk = _dau_ra_that_ban_sao_tran(tmp_path)
    assert rc_dk == 2 and "🟢" not in out_dk, out_dk
    sys.path.insert(0, str(ROOT / "tools"))
    import chu_trinh_chung_cu as ctcc

    class _P:
        def __init__(self, rc, out):
            self.returncode, self.stdout, self.stderr = rc, out, ""

    def _goi(cmd, **kw):
        if "dang_ky_chu_de.py" in str(cmd[1]):
            return _P(rc_dk, out_dk)
        return _P(0, "")
    with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
         mock.patch.object(ctcc.subprocess, "run", side_effect=_goi):
        rc = ctcc.main()
    out = capsys.readouterr().out
    assert "⚪ Chưa quét được mâu thuẫn hai bản" in out
    assert "🔴 Có mục hai bản CÙNG CHỦ ĐỀ nói ngược nhau" not in out
    assert "🟢 Mọi chốt đạt" not in out
    assert rc == 1
