#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Khoá DOI trong sổ xác minh nguồn KHÔNG được phân biệt hoa/thường — 03/10/2026.

Vì sao có (đợt kiểm 03/10/2026): `lenh_quet` ghi khoá DOI đúng như dashboard viết (giữ chữ HOA, qua `gom_nguon`),
còn `dinh_danh_da_rut` / `pham_vi_kiem_rut_bai` chỉ tra `doi:` + chữ thường; `--kiem-rut-lai` và `--quet-ledger`
lại ghi khoá chữ thường. Hệ quả tái hiện được:
  • bản ghi ĐÃ RÚT mang khoá viết hoa KHÔNG được tầng 2 của cổng tìm thấy ⇒ dashboard MỚI trích đúng DOI đó PASS
    như sạch (chỉ còn một cảnh báo «chưa kiểm»);
  • dashboard đổi cách viết DOI (hoa → thường) ⇒ `--quet` đẻ bản ghi trùng chưa kiểm và GỠ liên kết dashboard khỏi
    bản ghi đã rút ⇒ tầng 1 lẫn báo cáo không còn thấy bài đã rút;
  • bản ghi còn hạn mang khoá viết hoa bị tầng 3 xếp oan vào «chưa kiểm».
Đo trên sổ THẬT 03/10/2026 (chỉ đọc): 210/837 khoá DOI có chữ hoa, 17 cặp trùng chỉ khác hoa/thường, 0 bản ghi dương
tính bị khuất (lỗi đang TIỀM ẨN), 194 bản ghi còn hạn bị tầng 3 gọi là «chưa kiểm».

Căn cứ đặc tả: tài liệu Crossref «Constructing your DOIs» — hậu tố DOI không phân biệt hoa/thường (`10.1006/abc` và
`10.1006/ABC` là một trong hệ thống).

DOI trong tệp này là DOI TỔNG HỢP dưới tiền tố thử nghiệm 10.5555 của Crossref — không trỏ bài thật nào. Ngoại tuyến
100%: sổ nằm trong tmp_path, mọi nguồn mạng (Crossref, chuỗi rút bài) là đối tượng giả trong sys.modules.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import shutil
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SX_NGUON = ROOT / "tools" / "so_xac_minh_nguon.py"
VD_NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
PL_NGUON = ROOT / "tools" / "provenance_ledger.py"
BST_NGUON = ROOT / "tools" / "ban_sao_tran.py"

DOI_HOA = "10.5555/S0000-0000(26)00001-X"      # dáng DOI kiểu Lancet: ngoặc tròn + chữ X hoa ở cuối
DOI_THUONG = DOI_HOA.lower()
DOI_NEJM = "10.5555/NEJMoa2600001"              # dáng DOI kiểu NEJM: chữ hoa xen giữa


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


S = _nap("sx_doi_hoa_thuong_20261003", SX_NGUON)


def _iso(ngay_truoc: int = 0) -> str:
    return (dt.datetime.now() - dt.timedelta(days=ngay_truoc)).isoformat(timespec="seconds")


def _rut(gia_tri: str, dash=()) -> dict:
    return {"loai": "doi", "gia_tri": gia_tri, "xac_minh_luc": _iso(3), "kiem_rut_luc": _iso(3),
            "ghi_chu_rut": "retracted", "da_rut": True, "rut_va_thay": False, "nguon_xac_minh": "crossref",
            "cac_dashboard": list(dash)}


def _ok(gia_tri: str, dash=(), xac_minh_truoc: int = 3, kiem_truoc: int = 3) -> dict:
    return {"loai": "doi", "gia_tri": gia_tri, "xac_minh_luc": _iso(xac_minh_truoc), "kiem_rut_luc": _iso(kiem_truoc),
            "ghi_chu_rut": "ok", "nguon_xac_minh": "crossref", "cac_dashboard": list(dash)}


@pytest.fixture
def so_tam(tmp_path, monkeypatch):
    """Sổ THẬT trên đĩa (doc_so/ghi_so đi đúng đường thật) — trả (ghi_muc, doc_muc)."""
    p = tmp_path / ".so-xac-minh-nguon.json"
    monkeypatch.setattr(S, "SO", p)

    def ghi_muc(muc: dict) -> None:
        p.write_text(json.dumps({"phien_ban": 1, "muc": muc}, ensure_ascii=False), encoding="utf-8")

    def doc_muc() -> dict:
        return json.loads(p.read_text(encoding="utf-8"))["muc"]

    return ghi_muc, doc_muc


def _gia_app_sources(monkeypatch, crossref_check=None, chain_check=None, hoi=None):
    """Thay `app.sources.*` bằng đối tượng GIẢ — không bao giờ chạm mạng, kể cả trên máy có engine thật."""
    hoi = hoi if hoi is not None else []
    pkg = types.ModuleType("app")
    pkg.__path__ = []
    src = types.ModuleType("app.sources")
    src.__path__ = []
    cr = types.ModuleType("app.sources.crossref_retraction")
    rc = types.ModuleType("app.sources.retraction_chain")

    class _CR:
        def __init__(self, mailto=""):
            pass

        def check(self, dois):
            hoi.extend(dois)
            return (crossref_check or (lambda ds: {}))(list(dois))

    class _RC:
        def check(self, pmids):
            return (chain_check or (lambda ps: {}))(list(pmids))

    cr.CrossrefRetraction = _CR
    rc.RetractionChain = _RC
    for ten, mod in (("app", pkg), ("app.sources", src), ("app.sources.crossref_retraction", cr),
                     ("app.sources.retraction_chain", rc)):
        monkeypatch.setitem(sys.modules, ten, mod)
    return hoi


def _trang(tmp: Path, ten: str, doi: str, refs=()) -> Path:
    """Dashboard tối thiểu đúng khuôn `const DATA … HẾT KHỐI DATA` mà parser của cổng đọc."""
    ref_js = ",".join("'%s'" % r for r in refs)
    p = tmp / ten
    p.write_text("<script>const DATA = {meta:{}, items:[{id:'ITEM-01', doi:'%s', references:[%s]}]};\n"
                 "// HẾT KHỐI DATA\n</script>" % (doi, ref_js), encoding="utf-8")
    return p


def _vd_ngoai_tuyen(monkeypatch, ten: str):
    """Bộ parser THẬT của cổng; mọi hàm gọi mạng bị thay — DOI «xác minh được», PMID/URL không được phép gọi."""
    vd = _nap(ten, VD_NGUON)

    def _cam(*_a, **_k):
        raise AssertionError("test ngoại tuyến không được gọi mạng")

    monkeypatch.setattr(vd, "verify_doi_online", lambda doi, retries=2: (True, "tiêu đề giả cho " + doi))
    monkeypatch.setattr(vd, "verify_pmid_online", _cam)
    monkeypatch.setattr(vd, "verify_url_online", _cam)
    return vd


# ── 1. Hàm chuẩn hoá DUY NHẤT ────────────────────────────────────────────────────────────────────────────────────────
def test_chuan_hoa_khoa_chi_ha_chu_phan_doi():
    assert S.chuan_hoa_khoa("doi:" + DOI_HOA) == "doi:" + DOI_THUONG
    assert S.chuan_hoa_khoa("DOI: " + DOI_NEJM + " ") == "doi:" + DOI_NEJM.lower(), "tiền tố/khoảng trắng cũng về chuẩn"
    assert S.chuan_hoa_khoa("pmid:30267080") == "pmid:30267080"
    url = "url:https://www.ema.europa.eu/en/Documents/Report_ABC.pdf"
    assert S.chuan_hoa_khoa(url) == url, "đường dẫn URL CÓ phân biệt hoa/thường — hạ chữ là trộn hai trang khác nhau"


# ── 2. ĐỌC: tầng 2 (dinh_danh_da_rut) và tầng 3 (pham_vi_kiem_rut_bai) ──────────────────────────────────────────────
@pytest.mark.parametrize("tra", [DOI_HOA, DOI_THUONG, "10.5555/s0000-0000(26)00001-X"])
def test_tang2_thay_ban_ghi_da_rut_khoa_viet_hoa_du_tra_kieu_nao(monkeypatch, tra):
    """LỖI GỐC: khoá lưu viết hoa ⇒ tra `doi:`+lower trượt ⇒ bài đã rút im lặng như sạch."""
    muc = {"doi:" + DOI_HOA: _rut(DOI_HOA, ["WebDashboard_Khac.html"])}
    monkeypatch.setattr(S, "doc_so", lambda: {"muc": muc})
    ra = S.dinh_danh_da_rut([tra])
    assert [r["khoa"] for r in ra] == ["doi:" + DOI_HOA], ra
    assert ra[0]["tinh_trang"] == "retracted"


def test_tang2_khoa_thuong_tra_bang_chu_hoa_van_thay(monkeypatch):
    """Đối chứng chiều đã chạy đúng từ trước — bản vá không được làm rơi nó."""
    muc = {"doi:" + DOI_THUONG: _rut(DOI_THUONG)}
    monkeypatch.setattr(S, "doc_so", lambda: {"muc": muc})
    assert [r["khoa"] for r in S.dinh_danh_da_rut([DOI_HOA])] == ["doi:" + DOI_THUONG]


def test_tang2_cap_trung_hoa_thuong_duong_tinh_thang_ban_ok(monkeypatch):
    """Sổ cũ có cặp trùng: bản viết thường «ok», bản viết hoa ĐÃ RÚT ⇒ phải phát dương tính (bất đối xứng)."""
    muc = {"doi:" + DOI_NEJM: _rut(DOI_NEJM, ["A.html"]), "doi:" + DOI_NEJM.lower(): _ok(DOI_NEJM.lower(), ["B.html"])}
    monkeypatch.setattr(S, "doc_so", lambda: {"muc": muc})
    ra = S.dinh_danh_da_rut([DOI_NEJM.lower()])
    assert [r["khoa"] for r in ra] == ["doi:" + DOI_NEJM], "một bản «ok» không được che bản ĐÃ RÚT cùng DOI"


def test_tang2_khong_lap_cung_mot_ban_ghi_khi_trang_viet_ca_hai_kieu(monkeypatch):
    muc = {"doi:" + DOI_HOA: _rut(DOI_HOA)}
    monkeypatch.setattr(S, "doc_so", lambda: {"muc": muc})
    assert len(S.dinh_danh_da_rut([DOI_HOA, DOI_THUONG])) == 1


def test_tang3_ban_ghi_con_han_khoa_viet_hoa_la_co_dau_vet(monkeypatch):
    """Tầng 3 từng xếp oan 194 bản ghi còn hạn (sổ thật 03/10) vào «chưa kiểm» chỉ vì khoá viết hoa."""
    muc = {"doi:" + DOI_HOA: _ok(DOI_HOA)}
    monkeypatch.setattr(S, "doc_so", lambda: {"muc": muc})
    pv = S.pham_vi_kiem_rut_bai([DOI_HOA, DOI_THUONG, "10.5555/vang-so"])
    assert sorted(pv["co"]) == sorted([DOI_HOA, DOI_THUONG])
    assert pv["chua"] == ["10.5555/vang-so"], "vắng sổ vẫn là CHƯA KIỂM — không bao giờ thành có dấu vết"


def test_tang3_cap_trung_mot_ban_con_han_la_du(monkeypatch):
    muc = {"doi:" + DOI_NEJM: _ok(DOI_NEJM, kiem_truoc=400), "doi:" + DOI_NEJM.lower(): _ok(DOI_NEJM.lower())}
    monkeypatch.setattr(S, "doc_so", lambda: {"muc": muc})
    assert S.pham_vi_kiem_rut_bai([DOI_NEJM])["co"] == [DOI_NEJM]


# ── 3. GHI: gom nguồn, đồng bộ liên kết, quét ────────────────────────────────────────────────────────────────────────
def test_gom_nguon_khoa_doi_chuan_hoa_va_gop_bien_the(tmp_path, monkeypatch):
    vd = _vd_ngoai_tuyen(monkeypatch, "vd_gom_" + tmp_path.name)
    a = _trang(tmp_path, "WebDashboard_A.html", DOI_HOA, refs=["Tác giả. Tạp chí 2026. doi:" + DOI_NEJM + "."])
    b = _trang(tmp_path, "WebDashboard_B.html", DOI_THUONG)
    nguon = S.gom_nguon([a, b], vd)
    assert nguon == {"doi:" + DOI_THUONG: {"WebDashboard_A.html", "WebDashboard_B.html"},
                     "doi:" + DOI_NEJM.lower(): {"WebDashboard_A.html"}}, nguon


def test_dong_bo_noi_ban_ghi_khoa_thuong_voi_dashboard_viet_hoa(tmp_path, monkeypatch):
    """Bản ghi chữ thường (do --kiem-rut-lai/--quet-ledger ghi) phải được nối với dashboard trích DOI viết hoa — nếu
    không, tầng 1 (`nguon_da_rut`) không bao giờ thấy nó cho dashboard đó."""
    vd = _vd_ngoai_tuyen(monkeypatch, "vd_db1_" + tmp_path.name)
    a = _trang(tmp_path, "WebDashboard_A.html", DOI_HOA)
    muc = {"doi:" + DOI_THUONG: _rut(DOI_THUONG, [])}
    S.dong_bo_lien_ket_dashboard(muc, S.gom_nguon([a], vd), {"WebDashboard_A.html"})
    assert muc["doi:" + DOI_THUONG]["cac_dashboard"] == ["WebDashboard_A.html"]


def test_dong_bo_khong_go_lien_ket_cua_ban_ghi_cu_khoa_viet_hoa(tmp_path, monkeypatch):
    """Sổ CŨ (khoá viết hoa) không bị bắt di cư: sau khi nguồn gom về khoá chuẩn, liên kết cũ phải còn nguyên."""
    vd = _vd_ngoai_tuyen(monkeypatch, "vd_db2_" + tmp_path.name)
    a = _trang(tmp_path, "WebDashboard_A.html", DOI_HOA)
    muc = {"doi:" + DOI_HOA: _rut(DOI_HOA, ["WebDashboard_A.html"])}
    S.dong_bo_lien_ket_dashboard(muc, S.gom_nguon([a], vd), {"WebDashboard_A.html"})
    assert muc["doi:" + DOI_HOA]["cac_dashboard"] == ["WebDashboard_A.html"]


def test_quet_khi_dashboard_doi_cach_viet_khong_lam_mat_bai_da_rut(tmp_path, monkeypatch, so_tam, capsys):
    """Dashboard đổi DOI từ HOA sang thường: bản cũ đẻ bản ghi trùng «chưa kiểm», gỡ liên kết khỏi bản ĐÃ RÚT và trả
    mã 1 — bài đã rút biến mất khỏi tầng 1 lẫn báo cáo. Đúng: khớp bản ghi cũ, giữ dương tính, mã 2."""
    ghi_muc, doc_muc = so_tam
    _gia_app_sources(monkeypatch)
    vd = _vd_ngoai_tuyen(monkeypatch, "vd_quet1_" + tmp_path.name)
    monkeypatch.setattr(S, "_nap_verify_dashboard", lambda: vd)
    ghi_muc({"doi:" + DOI_HOA: _rut(DOI_HOA, ["WebDashboard_A.html"])})
    a = _trang(tmp_path, "WebDashboard_A.html", DOI_THUONG)
    rc = S.lenh_quet([a], 1)
    muc = doc_muc()
    assert sorted(muc) == ["doi:" + DOI_HOA], "không được đẻ bản ghi trùng chỉ khác hoa/thường"
    assert muc["doi:" + DOI_HOA]["da_rut"] is True
    assert muc["doi:" + DOI_HOA]["cac_dashboard"] == ["WebDashboard_A.html"]
    assert rc == 2, capsys.readouterr().out
    assert [r["khoa"] for r in S.nguon_da_rut("WebDashboard_A.html")] == ["doi:" + DOI_HOA]


def test_quet_xac_minh_lai_ghi_vao_ban_ghi_cu_khong_de_ban_sao(tmp_path, monkeypatch, so_tam):
    ghi_muc, doc_muc = so_tam
    _gia_app_sources(monkeypatch)
    vd = _vd_ngoai_tuyen(monkeypatch, "vd_quet2_" + tmp_path.name)
    monkeypatch.setattr(S, "_nap_verify_dashboard", lambda: vd)
    ghi_muc({"doi:" + DOI_HOA: _ok(DOI_HOA, ["WebDashboard_A.html"], xac_minh_truoc=400)})   # tồn tại đã quá hạn
    a = _trang(tmp_path, "WebDashboard_A.html", DOI_THUONG)
    S.lenh_quet([a], 1)
    muc = doc_muc()
    assert sorted(muc) == ["doi:" + DOI_HOA]
    assert muc["doi:" + DOI_HOA]["xac_minh_luc"][:10] == dt.date.today().isoformat(), "phải xác minh lại ĐÚNG bản cũ"
    assert muc["doi:" + DOI_HOA]["ghi_chu_rut"] == "ok", "dấu vết kiểm rút bài cũ phải được giữ"


def test_kiem_rut_bai_theo_doi_hoi_ca_ban_ghi_cu_khoa_viet_hoa(monkeypatch):
    """Nguồn gom về khoá chuẩn mà phép «có trong nguồn» so nguyên văn thì bản ghi viết hoa không bao giờ được kiểm
    rút bài lại — hết hạn 30 ngày là kẹt «chưa kiểm» vĩnh viễn."""
    hoi = _gia_app_sources(monkeypatch, crossref_check=lambda ds: {d: {"status": "retracted"} for d in ds})
    monkeypatch.setattr(Path, "exists",
                        lambda self, _g=Path.exists: True if str(self).endswith("crossref_retraction.py") else _g(self))
    monkeypatch.setattr(S, "ghi_so", lambda so: None)
    muc = {"doi:" + DOI_HOA: _ok(DOI_HOA, ["A.html"], kiem_truoc=45)}
    S.kiem_rut_bai_theo_doi(muc, {"doi:" + DOI_THUONG: {"A.html"}}, {"muc": muc})
    assert hoi == [DOI_HOA]
    assert muc["doi:" + DOI_HOA]["da_rut"] is True


def test_kiem_rut_lai_dich_danh_ghi_vao_ban_ghi_cu(monkeypatch, so_tam):
    ghi_muc, doc_muc = so_tam
    _gia_app_sources(monkeypatch, crossref_check=lambda ds: {d: {"status": "retracted"} for d in ds})
    ghi_muc({"doi:" + DOI_HOA: _ok(DOI_HOA, ["A.html"])})
    S.kiem_rut_lai_dich_danh(["doi:" + DOI_THUONG])
    muc = doc_muc()
    assert sorted(muc) == ["doi:" + DOI_HOA], "--kiem-rut-lai không được đẻ bản ghi chữ thường bên cạnh bản cũ"
    assert muc["doi:" + DOI_HOA]["da_rut"] is True
    assert muc["doi:" + DOI_HOA]["cac_dashboard"] == ["A.html"]


def test_kiem_rut_lai_dich_danh_duong_tinh_ghi_vao_moi_bien_the(monkeypatch, so_tam):
    """Cặp trùng cũ: phán quyết RÚT phải phủ MỌI biến thể — bản nào còn «ok» là còn một chỗ nói sai về cùng một DOI."""
    ghi_muc, doc_muc = so_tam
    _gia_app_sources(monkeypatch, crossref_check=lambda ds: {d: {"status": "retracted"} for d in ds})
    ghi_muc({"doi:" + DOI_NEJM: _ok(DOI_NEJM, ["A.html"]), "doi:" + DOI_NEJM.lower(): _ok(DOI_NEJM.lower(), ["B.html"])})
    S.kiem_rut_lai_dich_danh([DOI_NEJM])
    muc = doc_muc()
    assert all(muc[k].get("da_rut") is True for k in muc), muc


def test_quet_ledger_hub_nhan_phan_quyet_cua_ban_ghi_cu_khoa_viet_hoa(tmp_path, monkeypatch):
    """Hub ghi DOI chữ thường; sổ có bản ghi viết hoa với phán quyết CÒN HẠN ⇒ không hỏi lại, không đẻ bản trùng."""
    goc = tmp_path / "goc"
    (goc / "tools").mkdir(parents=True)
    shutil.copy(SX_NGUON, goc / "tools" / "so_xac_minh_nguon.py")
    shutil.copy(BST_NGUON, goc / "tools" / "ban_sao_tran.py")
    (goc / "EBM_MASTER").mkdir()
    (goc / "EBM_MASTER" / "EBM_MASTER.json").write_text(json.dumps({"evidence_cards": [
        {"source": {"doi": DOI_THUONG}}, {"source": {"doi": "10.5555/MOI-HOAN-TOAN"}}]}), encoding="utf-8")
    (goc / "EBM-Dashboards").mkdir()
    so = goc / "EBM-Dashboards" / ".so-xac-minh-nguon.json"
    so.write_text(json.dumps({"phien_ban": 1, "muc": {"doi:" + DOI_HOA: _ok(DOI_HOA, ["A.html"], kiem_truoc=1)}}),
                  encoding="utf-8")
    hoi = _gia_app_sources(monkeypatch, crossref_check=lambda ds: {d: {"status": "ok"} for d in ds})
    sx = _nap("sx_hub_" + tmp_path.name, goc / "tools" / "so_xac_minh_nguon.py")
    sx.quet_ledger_hub(1)
    muc = json.loads(so.read_text(encoding="utf-8"))["muc"]
    assert [d.lower() for d in hoi] == ["10.5555/moi-hoan-toan"], "DOI đã có phán quyết còn hạn (khoá viết hoa) bị hỏi lại"
    assert sorted(muc) == sorted(["doi:10.5555/moi-hoan-toan", "doi:" + DOI_HOA]), sorted(muc)


# ── 4. Báo cáo theo phạm vi quét ─────────────────────────────────────────────────────────────────────────────────────
def test_bao_cao_pham_vi_khop_ban_ghi_cu_va_duong_tinh_thang(so_tam, capsys):
    ghi_muc, _doc = so_tam
    ghi_muc({"doi:" + DOI_HOA: _rut(DOI_HOA, ["A.html"]), "doi:" + DOI_THUONG: _ok(DOI_THUONG, ["A.html"])})
    assert S.bao_cao(nguon_pham_vi={"doi:" + DOI_THUONG}) == 2, capsys.readouterr().out
    assert "doi:" + DOI_HOA in capsys.readouterr().out


def test_bao_cao_pham_vi_ban_ghi_cu_con_han_khong_bao_thieu(so_tam, capsys):
    """Một bản còn hạn là đủ cho cả định danh — bản trùng đã cũ không được thành chuông «còn thiếu» không tắt được."""
    ghi_muc, _doc = so_tam
    ghi_muc({"doi:" + DOI_HOA: _ok(DOI_HOA, ["A.html"], xac_minh_truoc=400), "doi:" + DOI_THUONG: _ok(DOI_THUONG)})
    assert S.bao_cao(nguon_pham_vi={"doi:" + DOI_THUONG}) == 0, capsys.readouterr().out
    ghi_muc({"doi:" + DOI_HOA: _ok(DOI_HOA, ["A.html"])})
    assert S.bao_cao(nguon_pham_vi={"doi:" + DOI_THUONG}) == 0, capsys.readouterr().out


# ── 5. Cổng verify_dashboard THẬT + sổ THẬT trong cây giả ───────────────────────────────────────────────────────────
def _cay_cong(tmp: Path, muc: dict, doi_trich: str):
    (tmp / "tools").mkdir()
    shutil.copy(VD_NGUON, tmp / "tools" / "verify_dashboard.py")
    shutil.copy(SX_NGUON, tmp / "tools" / "so_xac_minh_nguon.py")
    dash = tmp / "EBM-Dashboards"
    dash.mkdir()
    (dash / ".so-xac-minh-nguon.json").write_text(json.dumps({"phien_ban": 1, "muc": muc}), encoding="utf-8")
    page = _trang(dash, "WebDashboard_EBM_VanDeCuThe_Moi_20261003.html", doi_trich)
    vd = _nap("vd_cong_doi_" + tmp.name, tmp / "tools" / "verify_dashboard.py")
    return vd, page


@pytest.mark.parametrize("khoa_luu,doi_trich", [
    (DOI_HOA, DOI_HOA),          # LỖI GỐC: khoá lưu viết hoa, trang mới trích y hệt
    (DOI_HOA, DOI_THUONG),       # trang mới viết thường
    (DOI_THUONG, DOI_HOA),       # đối chứng: chiều đã đúng từ trước
])
def test_cong_chan_dashboard_moi_trich_doi_da_rut_bat_ke_hoa_thuong(tmp_path, khoa_luu, doi_trich):
    vd, page = _cay_cong(tmp_path, {"doi:" + khoa_luu: _rut(khoa_luu, ["WebDashboard_Khac.html"])}, doi_trich)
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    assert any("ĐÃ BỊ RÚT" in e and khoa_luu in e for e in errors), (errors, warns)
    assert not any("Rút bài:" in o for o in oks)


def test_cong_khong_goi_chua_kiem_cho_ban_ghi_con_han_khoa_viet_hoa(tmp_path):
    vd, page = _cay_cong(tmp_path, {"doi:" + DOI_HOA: _ok(DOI_HOA, ["WebDashboard_Khac.html"])}, DOI_HOA)
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    assert not errors
    assert not [w for w in warns if "Phạm vi kiểm rút bài" in w], warns
    assert any("Rút bài: 1/1" in o for o in oks), oks


# ── 6. Điểm khám / sổ truy nguyên (provenance_ledger) đọc CÙNG luật ─────────────────────────────────────────────────
PL = _nap("pl_doi_hoa_thuong_20261003", PL_NGUON)


def test_provenance_thay_ban_ghi_da_rut_khoa_viet_hoa():
    muc = {"doi:" + DOI_HOA: _rut(DOI_HOA, ["A.html"])}
    assert PL.trang_thai_rut_the({"source": {"doi": DOI_THUONG}}, None, muc)["muc"] == "duong"


def test_provenance_cap_trung_khong_ra_ok_khi_mot_ban_da_rut():
    """Thẻ viết DOI đúng như bản «ok», bản kia (chữ thường) ĐÃ RÚT ⇒ không bao giờ được ra «ok còn hạn»."""
    muc = {"doi:" + DOI_NEJM: _ok(DOI_NEJM, ["A.html"]), "doi:" + DOI_NEJM.lower(): _rut(DOI_NEJM.lower())}
    assert PL.trang_thai_rut_the({"source": {"doi": DOI_NEJM}}, None, muc)["muc"] == "duong"


def test_provenance_doi_chung_ok_con_han_van_dung():
    muc = {"doi:" + DOI_HOA: _ok(DOI_HOA, ["A.html"])}
    assert PL.trang_thai_rut_the({"source": {"doi": DOI_THUONG}}, None, muc)["muc"] == "ok_con_han"


def test_hai_ham_chuan_hoa_khoa_khop_nhau():
    """provenance_ledger viết lại luật chuẩn hoá tại chỗ (không nạp mô-đun sổ) — hai bản phải luôn cho CÙNG kết quả."""
    for k in ("doi:" + DOI_HOA, "DOI: " + DOI_NEJM + " ", "doi:" + DOI_THUONG, "pmid:30267080",
              "url:https://example.org/A_B.pdf", "khong-co-hai-cham"):
        assert PL._khoa_doi_chuan(k) == S.chuan_hoa_khoa(k), k
