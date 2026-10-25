# -*- coding: utf-8 -*-
"""ZIP skill tài khoản cũ hơn repo ⇒ máy tự đóng lại; hòm việc chỉ đích danh ZIP mới nhất (25/10/2026).

Sự cố: skill `cap-nhat-chung-cu-y-khoa`/`dark-analyst` đổi trong repo 24/10 sau lần đóng ZIP 23/10. Hòm việc báo «bác sĩ tải ZIP
lên»; bác sĩ tải lại đúng ZIP 23/10 còn trong CLAUDE_AI_SKILLS/ nhiều lần mà cảnh báo không hết — vì bước ĐÓNG GÓI (việc của máy)
chưa ai chạy lại.

Khoá các hành vi:
  • `can_dong_goi_lai`: repo đổi sau lần đóng gói / chưa từng đóng ⇒ có tên; đóng gói xong ⇒ rỗng; skill lỗi luật thì không;
  • `--im-khi-on`: mã 1 + một dòng khi cần đóng lại, mã 0 im lặng khi không, không ghi gì; thiếu gương tài khoản ⇒ 0;
  • `tools/tu_sua_chua.py` có mục tự đóng lại ZIP (kiểm `--im-khi-on`, sửa = chạy đóng gói), không bật trên Cloud;
  • hòm việc: dòng 🟡 nói MÁY đóng lại ZIP trước; dòng ⚪ nêu tên ZIP đóng gói mới nhất.
Ngoại tuyến (thư mục tạm).
"""
from __future__ import annotations

import datetime as dt
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


DG = _nap("_dg_dong_lai_test", "dong_goi_skill_tai_khoan.py")
TDX = _nap("_tdx_dong_lai_test", "tu_de_xuat_viec.py")
TSC = _nap("_tsc_dong_lai_test", "tu_sua_chua.py")


def _skill(goc: Path, ten: str, than: str) -> None:
    d = goc / ten
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {ten}\ndescription: Mô tả hợp lệ.\n---\n" + "Hướng dẫn dùng chung cho mọi bản. " * 30
                                + than, encoding="utf-8")


def _dung(tmp_path: Path):
    """Gương đồng bộ HÔM QUA có x bản cũ; repo có x bản mới + y chưa lên; đã đóng gói lúc này (sau gương)."""
    cloud, hub, ra = tmp_path / "cloud", tmp_path / "hub", tmp_path / "ra"
    _skill(cloud, "x", "Bản cũ.\n")
    _skill(hub, "x", "Bản mới.\n")
    _skill(hub, "y", "Skill mới.\n")
    cloud.mkdir(parents=True, exist_ok=True)
    hom_qua = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)
    (cloud / "manifest.json").write_text(json.dumps({"skills": [], "lastUpdated": int(hom_qua.timestamp() * 1000)}),
                                         encoding="utf-8")
    DG.dong_goi(DG.danh_gia(hub, cloud), hub, ra, cloud, "lượt 1")
    return cloud, hub, ra


def _kiem(hub, cloud, ra, capsys):
    ma = DG.main(["--hub", str(hub), "--cloud", str(cloud), "--ra", str(ra), "--im-khi-on"])
    return ma, capsys.readouterr().out


def test_vua_dong_goi_thi_khong_can_dong_lai(tmp_path, capsys):
    cloud, hub, ra = _dung(tmp_path)
    assert DG.can_dong_goi_lai(DG.danh_gia(hub, cloud, ra=ra), hub, DG.doc_so_luot(ra)) == []
    assert _kiem(hub, cloud, ra, capsys) == (0, "")


def test_repo_doi_sau_dong_goi_thi_can_dong_lai_va_khong_ghi_gi(tmp_path, capsys):
    cloud, hub, ra = _dung(tmp_path)
    so_truoc = (ra / DG.SO_LUOT).read_bytes()
    _skill(hub, "x", "Bản mới hơn nữa (repo đổi sau lần đóng gói).\n")
    assert DG.can_dong_goi_lai(DG.danh_gia(hub, cloud, ra=ra), hub, DG.doc_so_luot(ra)) == ["x"]
    ma, out = _kiem(hub, cloud, ra, capsys)
    assert ma == 1 and "x" in out and "đóng lại" in out
    assert (ra / DG.SO_LUOT).read_bytes() == so_truoc, "--im-khi-on chỉ kiểm, không ghi sổ/ZIP"
    # Máy đóng lại (đúng lệnh sửa của tu_sua_chua) ⇒ hết việc.
    assert DG.main(["--hub", str(hub), "--cloud", str(cloud), "--ra", str(ra)]) == 0
    capsys.readouterr()
    assert _kiem(hub, cloud, ra, capsys) == (0, "")


def test_skill_chua_tung_dong_goi_thi_can_dong(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    _skill(hub, "z", "Skill thêm sau lần đóng gói.\n")
    assert DG.can_dong_goi_lai(DG.danh_gia(hub, cloud, ra=ra), hub, DG.doc_so_luot(ra)) == ["z"]


def test_skill_vi_pham_luat_tai_len_khong_vao_danh_sach(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    (hub / "Sai_Ten").mkdir()
    (hub / "Sai_Ten" / "SKILL.md").write_text("---\nname: Sai_Ten\ndescription: d\n---\nthân\n", encoding="utf-8")
    assert "Sai_Ten" not in DG.can_dong_goi_lai(DG.danh_gia(hub, cloud, ra=ra), hub, DG.doc_so_luot(ra))


def test_thieu_guong_tai_khoan_thi_im_lang(tmp_path, capsys):
    hub, ra = tmp_path / "hub", tmp_path / "ra"
    _skill(hub, "x", "Bản mới.\n")
    assert _kiem(hub, tmp_path / "khong-co", ra, capsys) == (0, "")
    assert not ra.exists()


def test_tu_sua_chua_co_muc_tu_dong_lai_zip():
    muc = [v for v in TSC.VIEC_MAY if "dong_goi_skill_tai_khoan.py" in " ".join(map(str, v[1]))]
    assert len(muc) == 1
    _nhan, kiem, sua, cloud = muc[0]
    assert "--im-khi-on" in kiem and sua is not None and "--im-khi-on" not in sua and "--chay-kho" not in sua
    assert cloud is False


def test_hom_viec_dong_vang_noi_may_dong_lai_truoc(tmp_path):
    cloud, hub, ra = _dung(tmp_path)
    _skill(hub, "x", "Bản mới hơn nữa (repo đổi sau lần đóng gói).\n")
    (muc_do, cau, _lenh), = TDX.giac_quan_skill_tai_khoan(bundle=cloud, hub=hub, ra=ra)
    assert muc_do == 2 and "MÁY đóng lại ZIP" in cau and "ZIP cũ" in cau


def test_hom_viec_dong_trang_neu_ten_zip_moi_nhat(tmp_path, monkeypatch):
    cloud, hub, ra = _dung(tmp_path)
    so = json.loads((ra / DG.SO_LUOT).read_text(encoding="utf-8"))
    # Gương lùi về 3 ngày trước; y đóng gói 2 ngày trước (SAU gương, khác ngày với x) ⇒ vẫn «không đo được», không phải mới nhất.
    bay_gio = dt.datetime.now(dt.timezone.utc)
    (cloud / "manifest.json").write_text(
        json.dumps({"skills": [], "lastUpdated": int((bay_gio - dt.timedelta(days=3)).timestamp() * 1000)}), encoding="utf-8")
    so["dong_goi_dau"]["y.zip"] = (bay_gio - dt.timedelta(days=2)).astimezone().isoformat(timespec="seconds")
    (ra / DG.SO_LUOT).write_text(json.dumps(so), encoding="utf-8")
    monkeypatch.setattr(TDX, "_GIAC_QUAN_CHET", [])
    assert TDX.giac_quan_skill_tai_khoan(bundle=cloud, hub=hub, ra=ra) == []
    (dong,) = TDX._GIAC_QUAN_CHET
    assert "2 skill: gương cục bộ" in dong
    assert "ZIP mới nhất" in dong and ": x —" in dong, "chỉ nêu ZIP đóng gói mới nhất (x), không nêu y đóng hôm trước"
