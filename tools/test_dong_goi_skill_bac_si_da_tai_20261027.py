# -*- coding: utf-8 -*-
"""Test sổ «bác sĩ đã tải ZIP» của `dong_goi_skill_tai_khoan.py` (27/10/2026).

Sự cố: máy không đọc được tài khoản claude.ai, gương cục bộ dừng ở 02/10 ⇒ 44 skill «không đo được» mãi và hòm việc nhắc mãi,
bác sĩ «đã tải ZIP skill nhiều lần sao vẫn báo chưa tải». Khoá các hành vi:
  • `--bac-si-da-tai "<lời>"` ghi mã băm ZIP của lượt hiện tại kèm lời và lúc ghi; thiếu lời / chưa có lượt ⇒ không ghi;
  • skill «không đo được» có ZIP cùng nội dung trong sổ ⇒ «bac_si_da_tai», vẫn đóng gói, hòm việc im;
  • đóng gói lại khi nội dung không đổi vẫn giữ trạng thái; repo đổi nội dung ⇒ lại «cập nhật» và hòm việc nhắc.
Ngoại tuyến (thư mục tạm).
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


DG = _nap("_dg_da_tai_test", "dong_goi_skill_tai_khoan.py")
TDX = _nap("_tdx_da_tai_test", "tu_de_xuat_viec.py")


def _skill(goc: Path, ten: str, than: str) -> None:
    d = goc / ten
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {ten}\ndescription: Mô tả hợp lệ.\n---\n" + "Hướng dẫn dùng chung cho mọi bản. " * 30
                                + than, encoding="utf-8")


def _dung(tmp_path: Path):
    """Gương cũ 1 ngày (x bản cũ) · hub (x mới + y chưa lên) · ra (đã đóng gói sau gương ⇒ cả hai «không đo được»)."""
    cloud, hub, ra = tmp_path / "cloud", tmp_path / "hub", tmp_path / "ra"
    _skill(cloud, "x", "Bản cũ.\n")
    _skill(hub, "x", "Bản mới.\n")
    _skill(hub, "y", "Skill mới.\n")
    cloud.mkdir(parents=True, exist_ok=True)
    luc = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)
    (cloud / "manifest.json").write_text(json.dumps({"skills": [], "lastUpdated": int(luc.timestamp() * 1000)}),
                                         encoding="utf-8")
    DG.dong_goi(DG.danh_gia(hub, cloud), hub, ra, cloud, "test")
    return cloud, hub, ra


def _tt(hub, cloud, ra):
    return {m["ten"]: m for m in DG.danh_gia(hub, cloud, ra=ra)}


def test_xac_nhan_da_tai_thi_het_khong_do_duoc_va_hom_viec_im(tmp_path, monkeypatch):
    cloud, hub, ra = _dung(tmp_path)
    assert {k: m["trang_thai"] for k, m in _tt(hub, cloud, ra).items()} == {"x": "khong_do_duoc", "y": "khong_do_duoc"}
    zips = DG.ghi_bac_si_da_tai(ra, "đã tải ZIP skill nhiều lần")
    assert set(zips) == {"x.zip", "y.zip"}
    so = json.loads((ra / DG.SO_DA_TAI).read_text(encoding="utf-8"))
    assert so["lan"][0]["loi"] == "đã tải ZIP skill nhiều lần" and DG._gio(so["lan"][0]["luc"]).tzinfo is not None
    tt = _tt(hub, cloud, ra)
    assert {k: m["trang_thai"] for k, m in tt.items()} == {"x": "bac_si_da_tai", "y": "bac_si_da_tai"}
    assert all(m["dong_goi"] for m in tt.values()), "vẫn đóng gói để sổ lượt giữ dấu"
    monkeypatch.setattr(TDX, "_GIAC_QUAN_CHET", [])
    assert TDX.giac_quan_skill_tai_khoan(bundle=cloud, hub=hub, ra=ra) == []
    assert TDX._GIAC_QUAN_CHET == [], "đã xác nhận tải ⇒ không còn «không đo được»"
    # Đóng gói lại (nội dung không đổi) vẫn giữ trạng thái; danh sách tải có nhóm «đã xác nhận».
    DG.dong_goi(DG.danh_gia(hub, cloud, ra=ra), hub, ra, cloud, "lượt 2")
    assert {m["trang_thai"] for m in _tt(hub, cloud, ra).values()} == {"bac_si_da_tai"}
    ds = (ra / DG.DANH_SACH).read_text(encoding="utf-8")
    assert "## ✓ Bác sĩ đã xác nhận tải lên (2)" in ds and "## ⚪ Không đo được" not in ds


def test_repo_doi_sau_xac_nhan_thi_lai_cap_nhat(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    DG.ghi_bac_si_da_tai(ra, "đã tải")
    _skill(hub, "x", "Bản mới hơn nữa.\n")
    tt = _tt(hub, cloud, ra)
    assert tt["x"]["trang_thai"] == "cap_nhat" and tt["y"]["trang_thai"] == "bac_si_da_tai"
    assert TDX.giac_quan_skill_tai_khoan(bundle=cloud, hub=hub, ra=ra)[0][0] == 2


def test_khong_ghi_khi_thieu_loi_hoac_chua_dong_goi(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    with pytest.raises(ValueError):
        DG.ghi_bac_si_da_tai(ra, "   ")
    assert not (ra / DG.SO_DA_TAI).exists()
    trong = tmp_path / "trong"
    trong.mkdir()
    with pytest.raises(ValueError):
        DG.ghi_bac_si_da_tai(trong, "đã tải")
    (ra / DG.SO_DA_TAI).write_text("{hỏng", encoding="utf-8")
    with pytest.raises(ValueError):
        DG.ghi_bac_si_da_tai(ra, "đã tải")
    assert (ra / DG.SO_DA_TAI).read_text(encoding="utf-8") == "{hỏng", "sổ hỏng không bị ghi đè"
    assert DG.doc_so_da_tai(ra) == {}


def test_lenh_bac_si_da_tai(tmp_path, capsys):
    cloud, hub, ra = _dung(tmp_path)
    assert DG.main(["--ra", str(ra), "--bac-si-da-tai", "đã tải hết"]) == 0
    assert "Ghi nhận bác sĩ đã tải 2 ZIP" in capsys.readouterr().out
    assert DG.main(["--hub", str(hub), "--cloud", str(cloud), "--ra", str(ra), "--chay-kho"]) == 0
    assert "bác sĩ đã tải 2" in capsys.readouterr().out
    assert DG.main(["--ra", str(tmp_path / "khong_co"), "--bac-si-da-tai", "đã tải"]) == 3
