# -*- coding: utf-8 -*-
"""Test gương cục bộ lạc hậu của bộ skill tài khoản (23/10/2026, BH168).

Sự cố: gương `~/.claude/skills/synced/<uuid>` dừng ở lần đồng bộ 02/10/2026; bác sĩ đã tải đủ 44 ZIP đóng gói 21/10 (danh sách
skill sống của tài khoản xác nhận) mà `dong_goi_skill_tai_khoan.py` và hòm việc vẫn báo «21 skill CŨ · 23 mới» — đỏ giả.

Khoá các hành vi:
  • gương cũ hơn ZIP CÙNG nội dung ⇒ «khong_do_duoc» (không bao giờ «da_moi»), vẫn đóng gói để sổ lượt giữ dấu;
  • repo đổi sau lần đóng gói ⇒ «cap_nhat» (kể cả skill gương chưa có — đã đóng gói thì không còn là «mới, tuỳ chọn»);
  • gương đồng bộ SAU lần đóng gói / gương không có manifest / không truyền sổ ⇒ giữ nguyên phán của gương;
  • sổ lượt giữ lúc đóng gói LẦN ĐẦU khi nội dung không đổi, đặt lại khi nội dung đổi; sổ cũ thiếu khoá thì lấy `luc`;
  • ZIP ghi ra đĩa trùng từng byte với ZIP dựng trong bộ nhớ để so;
  • hòm việc: skill không đo được ⇒ ⚪ giác quan không đo được, không vào dòng 🟡.
Ngoại tuyến (thư mục tạm).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


DG = _nap("_dg_guong_test", "dong_goi_skill_tai_khoan.py")
TDX = _nap("_tdx_guong_test", "tu_de_xuat_viec.py")

NGAY = dt.timedelta(days=1)


def _skill(goc: Path, ten: str, than: str) -> None:
    d = goc / ten
    d.mkdir(parents=True, exist_ok=True)
    # Thân chung dài để hai bản chỉ «lệch bản», không bị `phan_loai` xếp «khác hẳn» (hai skill khác nhau cùng tên).
    (d / "SKILL.md").write_text(f"---\nname: {ten}\ndescription: Mô tả hợp lệ.\n---\n" + "Hướng dẫn dùng chung cho mọi bản. " * 30
                                + than, encoding="utf-8")


def _manifest(cloud: Path, luc: dt.datetime | None, gia_tri=None) -> None:
    cloud.mkdir(parents=True, exist_ok=True)
    du_lieu = {"skills": []}
    if luc is not None:
        du_lieu["lastUpdated"] = int(luc.timestamp() * 1000)
    if gia_tri is not None:
        du_lieu["lastUpdated"] = gia_tri
    (cloud / "manifest.json").write_text(json.dumps(du_lieu), encoding="utf-8")


def _dung(tmp_path: Path, guong_cach_day: dt.timedelta | None = NGAY):
    """cloud (gương có x bản cũ) · hub (x bản mới + y chưa lên gương) · ra (đã đóng gói x, y lúc này)."""
    cloud, hub, ra = tmp_path / "cloud", tmp_path / "hub", tmp_path / "ra"
    _skill(cloud, "x", "Bản cũ.\n")
    _skill(hub, "x", "Bản mới.\n")
    _skill(hub, "y", "Skill mới.\n")
    _manifest(cloud, None if guong_cach_day is None else dt.datetime.now(dt.timezone.utc) - guong_cach_day)
    DG.dong_goi(DG.danh_gia(hub, cloud), hub, ra, cloud, "test")
    return cloud, hub, ra


def _trang_thai(hub, cloud, ra):
    return {m["ten"]: m for m in DG.danh_gia(hub, cloud, ra=ra)}


def test_guong_cu_hon_zip_cung_noi_dung_la_khong_do_duoc(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    tt = _trang_thai(hub, cloud, ra)
    assert tt["x"]["trang_thai"] == "khong_do_duoc"
    assert tt["x"]["trang_thai_guong"] == "cap_nhat"
    assert tt["y"]["trang_thai"] == "khong_do_duoc"
    assert tt["y"]["trang_thai_guong"] == "moi"
    assert all(m["dong_goi"] for m in tt.values()), "skill không đo được vẫn phải đóng gói để sổ lượt giữ dấu"
    assert DG.tom_tat(list(tt.values())).get("da_moi") is None, "không đo được KHÔNG bao giờ là «đã mới»"


def test_khong_truyen_so_luot_thi_giu_phan_cua_guong(tmp_path):
    cloud, hub, _ra = _dung(tmp_path)
    tt = {m["ten"]: m["trang_thai"] for m in DG.danh_gia(hub, cloud)}
    assert tt == {"x": "cap_nhat", "y": "moi"}


def test_repo_doi_sau_dong_goi_la_cap_nhat_ke_ca_skill_guong_chua_co(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    _skill(hub, "x", "Bản mới hơn nữa.\n")
    _skill(hub, "y", "Skill mới, sửa sau khi đóng gói.\n")
    tt = _trang_thai(hub, cloud, ra)
    assert tt["x"]["trang_thai"] == "cap_nhat"
    assert tt["y"]["trang_thai"] == "cap_nhat", "đã đóng gói sau gương mà repo đổi ⇒ cần tải bản mới, không phải «mới, tuỳ chọn»"
    assert "repo đổi sau đó" in tt["y"]["canh"][0]
    assert TDX.giac_quan_skill_tai_khoan(bundle=cloud, hub=hub, ra=ra)[0][0] == 2


def test_guong_dong_bo_sau_dong_goi_thi_giu_phan_cua_guong(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    _manifest(cloud, dt.datetime.now(dt.timezone.utc) + NGAY)
    tt = _trang_thai(hub, cloud, ra)
    assert (tt["x"]["trang_thai"], tt["y"]["trang_thai"]) == ("cap_nhat", "moi")


def test_guong_khong_co_manifest_thi_giu_phan_cua_guong(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    (cloud / "manifest.json").unlink()
    assert DG.moc_guong(cloud) is None
    tt = _trang_thai(hub, cloud, ra)
    assert (tt["x"]["trang_thai"], tt["y"]["trang_thai"]) == ("cap_nhat", "moi")


def test_moc_guong_doc_mili_giay_va_lui_ve_gio_sua_tep(tmp_path):
    luc = dt.datetime(2026, 10, 2, 14, 23, 11, tzinfo=dt.timezone.utc)
    _manifest(tmp_path, luc)
    assert DG.moc_guong(tmp_path) == luc
    _manifest(tmp_path, None, gia_tri=True)
    assert abs(DG.moc_guong(tmp_path).timestamp() - (tmp_path / "manifest.json").stat().st_mtime) < 1


def test_so_luot_giu_luc_dong_goi_lan_dau_va_dat_lai_khi_noi_dung_doi(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    so = json.loads((ra / ".dong-goi.json").read_text(encoding="utf-8"))
    dau = dict(so["dong_goi_dau"])
    so["dong_goi_dau"] = {k: "2026-10-21T20:02:00+07:00" for k in dau}
    (ra / ".dong-goi.json").write_text(json.dumps(so), encoding="utf-8")
    _skill(hub, "y", "Skill mới, sửa sau khi đóng gói.\n")
    DG.dong_goi(DG.danh_gia(hub, cloud, ra=ra), hub, ra, cloud, "lượt 2")
    so2 = json.loads((ra / ".dong-goi.json").read_text(encoding="utf-8"))
    assert so2["dong_goi_dau"]["x.zip"] == "2026-10-21T20:02:00+07:00", "nội dung không đổi ⇒ giữ lúc đóng gói lần đầu"
    assert so2["dong_goi_dau"]["y.zip"] != "2026-10-21T20:02:00+07:00", "nội dung đổi ⇒ lúc đóng gói đặt lại"
    assert DG._gio(so2["luc_iso"]).tzinfo is not None


def test_so_cu_thieu_dong_goi_dau_thi_lay_luc(tmp_path):
    ra = tmp_path / "ra"
    ra.mkdir()
    (ra / ".dong-goi.json").write_text(json.dumps({"luc": "2026-10-21 20:02", "zip": {"x.zip": "ab"}}), encoding="utf-8")
    sha, gio = DG.doc_so_luot(ra)["x.zip"]
    assert sha == "ab" and gio == dt.datetime(2026, 10, 21, 20, 2).astimezone()
    (ra / ".dong-goi.json").write_text("{hỏng", encoding="utf-8")
    assert DG.doc_so_luot(ra) == {}


def test_zip_tren_dia_trung_zip_dung_trong_bo_nho(tmp_path):
    tep = {"SKILL.md": b"---\nname: z\ndescription: d\n---\n", "tools/a.py": b"print(1)\n"}
    sha = DG.ghi_zip(tmp_path / "z.zip", "z", tep, {"tools/a.py": 0o755})
    bo_nho = DG._zip_byte("z", tep, {"tools/a.py": 0o755})
    assert sha == hashlib.sha256(bo_nho).hexdigest()
    assert bo_nho[-22:-18] == b"PK\x05\x06", "ZIP phải kết thúc đúng ở bản ghi cuối (không byte thừa) như bản ghi_zip cũ"


def test_danh_sach_tach_nhom_khong_do_duoc(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    DG.dong_goi(DG.danh_gia(hub, cloud, ra=ra), hub, ra, cloud, "lượt 2")
    ds = (ra / DG.DANH_SACH).read_text(encoding="utf-8")
    phan_moi = ds.split("## ② ", 1)[1].split("## ", 1)[0]
    assert "## ⚪ Không đo được" in ds
    assert "`x.zip`" not in phan_moi and "`y.zip`" not in phan_moi


def test_hom_viec_khong_do_duoc_la_giac_quan_chet_khong_phai_viec(tmp_path, monkeypatch):
    cloud, hub, ra = _dung(tmp_path)
    monkeypatch.setattr(TDX, "_GIAC_QUAN_CHET", [])
    assert TDX.giac_quan_skill_tai_khoan(bundle=cloud, hub=hub, ra=ra) == []
    assert len(TDX._GIAC_QUAN_CHET) == 1 and "2 skill: gương cục bộ" in TDX._GIAC_QUAN_CHET[0]


def test_lenh_that_doc_so_luot_o_thu_muc_ra(tmp_path, capsys):
    cloud, hub, ra = _dung(tmp_path)
    ma = DG.main(["--hub", str(hub), "--cloud", str(cloud), "--ra", str(ra), "--chay-kho", "--json"])
    ket = json.loads(capsys.readouterr().out)
    assert ma == 0
    assert {m["ten"]: m["trang_thai"] for m in ket["skill"]} == {"x": "khong_do_duoc", "y": "khong_do_duoc"}
