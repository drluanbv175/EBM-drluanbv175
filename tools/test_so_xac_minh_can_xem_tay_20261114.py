"""Sổ xác minh nguồn: bản ghi TRẦN (vắng ngày xác minh) KHÔNG phải «xem tay» — vá 14/11/2026.

Đo 14/11/2026 (`--bao-cao`, chỉ đọc): 80 mục «[MA] CAN_XEM_TAY — không đọc được ngày xác minh». Cả 80 là bản ghi VẮNG hẳn
`xac_minh_luc`: 52 thẻ `(hub-only)` do `--quet-ledger` tạo (chỉ kiểm rút bài) + 28 PMID `NC:<đề tài>` do cầu NC⇄LS tạo.
Không có bản ghi nào mang ngày sai khuôn. Thử xác minh mẫu cả hai nhóm đều THÀNH CÔNG ngay ⇒ máy tự sửa được bằng
`--phu-mo-coi`; `--vong 3` không chạm tới (chỉ tái kiểm định danh gom từ dashboard). Nhãn «xem tay» là lời khuyên lệch.

Bất biến phải giữ: không ngày (vắng hay hỏng) thì KHÔNG BAO GIỜ còn hiệu lực; không nới hạn 180/30 ngày; ngày hỏng thật
vẫn là «xem tay». Ngoại tuyến: sổ tạm, hàm mạng giả.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import importlib.util
import io
import json
import sys
from pathlib import Path
from unittest import mock

import pytest

_THU_MUC = Path(__file__).resolve().parent
_TEP = _THU_MUC / "so_xac_minh_nguon.py"


@pytest.fixture()
def M(tmp_path, monkeypatch):
    sp = importlib.util.spec_from_file_location("so_xac_minh_can_xem_tay_20261114", _TEP)
    mod = importlib.util.module_from_spec(sp)
    sys.modules["so_xac_minh_can_xem_tay_20261114"] = mod
    sp.loader.exec_module(mod)
    monkeypatch.setattr(mod, "SO", tmp_path / ".so-xac-minh-nguon.json")
    monkeypatch.setattr(mod, "DASH", tmp_path)
    monkeypatch.setattr(mod, "_nap_verify_dashboard", lambda: None)
    # Chặn mạng: không tra được rút bài ⇒ giữ nguyên (bất biến «chỉ ghi THÀNH CÔNG»).
    monkeypatch.setattr(mod, "kiem_rut_bai", lambda ds: {})
    monkeypatch.setattr(mod, "kiem_rut_doi", lambda ds: {})
    return mod


def _bay_gio() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def _ghi_so(M, muc: dict) -> None:
    M.SO.write_text(json.dumps({"phien_ban": 1, "muc": muc}, ensure_ascii=False), encoding="utf-8")


def _bao_cao(M) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = M.bao_cao()
    return rc, buf.getvalue()


def _so_mau() -> dict:
    """Bốn kiểu bản ghi đúng như sổ thật: hub trần (đã kiểm rút «ok»), NC trần, ngày sai khuôn, URL trần."""
    bg = _bay_gio()
    return {
        "doi:10.1/hub": {"loai": "doi", "gia_tri": "10.1/hub", "cac_dashboard": ["(hub-only)"],
                         "kiem_rut_luc": bg, "ghi_chu_rut": "ok", "nguon_xac_minh": "crossref"},
        "pmid:111": {"loai": "pmid", "gia_tri": "111", "cac_dashboard": ["NC:de-tai-thu"]},
        "pmid:222": {"loai": "pmid", "gia_tri": "222", "cac_dashboard": ["WebDashboard_X.html"],
                     "xac_minh_luc": "14/11/2026", "kiem_rut_luc": bg, "ghi_chu_rut": "ok"},
        "url:https://vi-du.test/a": {"loai": "url", "gia_tri": "https://vi-du.test/a", "cac_dashboard": []},
    }


# ── con_hieu_luc: tách lý do, cả hai vẫn HẾT hiệu lực ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("gia_tri", [None, "", "   "])
def test_vang_ngay_la_chua_xac_minh_ton_tai_va_het_hieu_luc(M, gia_tri):
    bg = {"loai": "pmid", "gia_tri": "1", "kiem_rut_luc": _bay_gio(), "ghi_chu_rut": "ok"}
    if gia_tri is not None:
        bg["xac_minh_luc"] = gia_tri
    assert M.con_hieu_luc(bg) == (False, M.LY_DO_CHUA_XAC_MINH_TON_TAI)


@pytest.mark.parametrize("gia_tri", ["14/11/2026", "2026-13-40T00:00:00", 20261114, ["2026-11-14"]])
def test_ngay_hong_van_la_xem_tay_va_khong_sap(M, gia_tri):
    """Ngày CÓ mà không đọc được ⇒ lý do cũ «không đọc được ngày xác minh»; giá trị không phải chuỗi không làm sập."""
    bg = {"loai": "pmid", "gia_tri": "1", "xac_minh_luc": gia_tri, "kiem_rut_luc": _bay_gio(), "ghi_chu_rut": "ok"}
    assert M.con_hieu_luc(bg) == (False, M.LY_DO_NGAY_HONG)


def test_khong_noi_han(M):
    """Hạn 180/30 ngày giữ nguyên — vá không được đụng tới luật hạn."""
    assert (M.HAN_TON_TAI_NGAY, M.HAN_RUT_BAI_NGAY) == (180, 30)
    cu = (dt.date.today() - dt.timedelta(days=181)).isoformat()
    bg = {"loai": "url", "gia_tri": "u", "xac_minh_luc": cu}
    ok, ly_do = M.con_hieu_luc(bg)
    assert not ok and "xác minh đã 181 ngày" in ly_do


# ── bao_cao: nhóm TRẦN ra mã riêng với cách sửa máy làm được ────────────────────────────────────────────────────

def test_bao_cao_tach_ban_ghi_tran_khoi_xem_tay(M):
    _ghi_so(M, _so_mau())
    rc, out = _bao_cao(M)
    assert rc == 1, "còn mục hết hiệu lực ⇒ mã 1 (không được thành 0)"
    assert "Còn hiệu lực : 0/4" in out, "bản ghi trần/ngày hỏng không bao giờ được tính còn hạn"
    # Nhóm trần: đúng 2 (hub DOI + NC PMID), có nguồn gốc, có lệnh sửa, có mã riêng.
    assert "[MA] CAN_PHU_MO_COI" in out
    assert "2 mục: bản ghi TRẦN" in out
    assert "1 thẻ hub (--quet-ledger)" in out and "1 đề tài NC (cầu NC⇄LS)" in out
    assert "--phu-mo-coi --vong 3" in out
    # Phần xem tay chỉ còn ngày hỏng + URL trần, và MỌI lý do đều được liệt kê (không chỉ lý do đầu).
    assert "[MA] CAN_XEM_TAY" in out
    assert "2 mục: lý do khác — cần xem tay" in out
    assert f"1 mục: {M.LY_DO_NGAY_HONG}" in out
    assert f"1 mục: {M.LY_DO_CHUA_XAC_MINH_TON_TAI}" in out  # URL trần: --phu-mo-coi không phủ URL ⇒ xem tay


def test_bao_cao_khong_con_ma_xem_tay_khi_chi_co_ban_ghi_tran(M):
    """Đúng hình dạng sổ thật 14/11: chỉ có bản ghi trần PMID/DOI ⇒ 0 «xem tay»."""
    muc = {k: v for k, v in _so_mau().items() if k in ("doi:10.1/hub", "pmid:111")}
    _ghi_so(M, muc)
    rc, out = _bao_cao(M)
    assert rc == 1
    assert "[MA] CAN_PHU_MO_COI" in out
    assert "CAN_XEM_TAY" not in out


# ── --phu-mo-coi thật sự gỡ được nhóm này (máy sửa được), giữ phán quyết rút bài ───────────────────────────────

def test_phu_mo_coi_go_duoc_ban_ghi_tran(M, monkeypatch):
    bay_gio = _bay_gio()
    muc = {k: v for k, v in _so_mau().items() if k in ("doi:10.1/hub", "pmid:111")}
    _ghi_so(M, muc)

    def _xm(khoa, vd):
        loai, _, gt = khoa.partition(":")
        return {"loai": loai, "gia_tri": gt, "xac_minh_luc": bay_gio, "tieu_de": "t",
                "nguon_xac_minh": "pubmed" if loai == "pmid" else "crossref"}

    monkeypatch.setattr(M, "xac_minh_mot", _xm)
    # PMID NC chưa từng kiểm rút bài: lượt phủ gọi kiem_rut_lai_dich_danh ⇒ cho trả «ok» thật để bản ghi hội tụ.
    monkeypatch.setattr(M, "kiem_rut_bai", lambda ds: {p: {"status": "ok"} for p in ds})
    with contextlib.redirect_stdout(io.StringIO()):
        M._chay_lenh(argparse.Namespace(phu_mo_coi=True, vong=1, kiem_rut_lai=None, quet_ledger=False,
                                        bao_cao=False, quet=None, cuu_so_hong=False))
    so = M.doc_so()["muc"]
    assert so["doi:10.1/hub"]["kiem_rut_luc"] == muc["doi:10.1/hub"]["kiem_rut_luc"], "mất phán quyết rút bài cũ"
    assert so["doi:10.1/hub"]["cac_dashboard"] == ["(hub-only)"]
    assert so["pmid:111"]["cac_dashboard"] == ["NC:de-tai-thu"]
    assert M.con_hieu_luc(so["doi:10.1/hub"]) == (True, "")
    assert M.con_hieu_luc(so["pmid:111"]) == (True, "")
    rc, out = _bao_cao(M)
    assert rc == 0 and "CAN_PHU_MO_COI" not in out


def test_phu_mo_coi_mang_hong_giu_chua_kiem(M, monkeypatch):
    """Không tra được ⇒ KHÔNG ghi gì, bản ghi vẫn trần và vẫn hết hiệu lực (không bịa ngày)."""
    muc = {k: v for k, v in _so_mau().items() if k == "pmid:111"}
    _ghi_so(M, muc)
    monkeypatch.setattr(M, "xac_minh_mot", lambda khoa, vd: None)
    with contextlib.redirect_stdout(io.StringIO()):
        M._chay_lenh(argparse.Namespace(phu_mo_coi=True, vong=2, kiem_rut_lai=None, quet_ledger=False,
                                        bao_cao=False, quet=None, cuu_so_hong=False))
    bg = M.doc_so()["muc"]["pmid:111"]
    assert "xac_minh_luc" not in bg
    assert M.con_hieu_luc(bg) == (False, M.LY_DO_CHUA_XAC_MINH_TON_TAI)


# ── chu_trinh_chung_cu đọc mã mới, không rơi về câu chung ───────────────────────────────────────────────────────

class _P:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def test_chu_trinh_doc_ma_phu_mo_coi(capsys):
    sys.path.insert(0, str(_THU_MUC))
    import chu_trinh_chung_cu as ctcc  # noqa: PLC0415

    out_so = "  • 80 mục: bản ghi TRẦN …\n       [MA] CAN_PHU_MO_COI\n"

    def _goi(cmd, **kw):
        cmd = [str(c) for c in cmd]
        if len(cmd) > 1 and "so_xac_minh_nguon.py" in cmd[1] and "--phu-mo-coi" not in cmd and "--quet-ledger" not in cmd:
            return _P(1, out_so)
        return _P(0, "")

    with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
            mock.patch.object(ctcc.subprocess, "run", side_effect=_goi), \
            mock.patch.object(ctcc, "_co_dashboard_that", return_value=True):
        ctcc.main()
    out = capsys.readouterr().out
    assert "bản ghi TRẦN chưa xác minh tồn tại" in out and "--phu-mo-coi --vong 3" in out
    assert "Còn nguồn chưa xác minh hoặc hết hạn — xem phần ③④" not in out
    assert "lý do khác — xem phần ③④" not in out


# ── --quet-ledger nói ra khi vừa tạo bản ghi trần ───────────────────────────────────────────────────────────────

def _chay_quet_ledger(M, monkeypatch, tmp_path, the_hub: list[dict], ket_qua_doi: dict, so_truoc: dict) -> str:
    """Chạy `quet_ledger_hub(1)` trên hub giả + chuỗi rút bài giả (không mạng); trả đầu ra."""
    hub_dir = tmp_path / "EBM_MASTER"
    hub_dir.mkdir()
    (hub_dir / "EBM_MASTER.json").write_text(json.dumps({"evidence_cards": the_hub}), encoding="utf-8")
    _ghi_so(M, so_truoc)

    class _BST:
        @staticmethod
        def duong_goc(ten, repo):
            return hub_dir if ten == "EBM_MASTER" else None

    class _Chain:
        def check(self, lo):
            return {}

    class _CR:
        def check(self, lo):
            return {d: ket_qua_doi.get(d, {"status": "ok"}) for d in lo}

    import types
    goi_that = importlib.util.module_from_spec

    def _module_from_spec(spec):
        if spec.name == "_bst_sxmn_qlh":
            return _BST()
        return goi_that(spec)

    fake_rc = types.ModuleType("app.sources.retraction_chain")
    fake_rc.RetractionChain = _Chain
    fake_cr = types.ModuleType("app.sources.crossref_retraction")
    fake_cr.CrossrefRetraction = _CR
    monkeypatch.setitem(sys.modules, "app", types.ModuleType("app"))
    monkeypatch.setitem(sys.modules, "app.sources", types.ModuleType("app.sources"))
    monkeypatch.setitem(sys.modules, "app.sources.retraction_chain", fake_rc)
    monkeypatch.setitem(sys.modules, "app.sources.crossref_retraction", fake_cr)
    monkeypatch.setattr(importlib.util, "module_from_spec", _module_from_spec)
    monkeypatch.setattr(sys, "path", list(sys.path))  # quet_ledger_hub chèn đường dẫn engine — không rò ra test khác
    goi_spec = importlib.util.spec_from_file_location

    def _spec(name, *a, **kw):
        sp = goi_spec(name, *a, **kw)
        if name == "_bst_sxmn_qlh":
            sp.loader = type("L", (), {"exec_module": staticmethod(lambda m: None)})()
        return sp

    monkeypatch.setattr(importlib.util, "spec_from_file_location", _spec)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        M.quet_ledger_hub(1)
    return buf.getvalue()


def test_quet_ledger_nhac_phu_mo_coi_khi_tao_ban_ghi_tran(M, monkeypatch, tmp_path):
    out = _chay_quet_ledger(M, monkeypatch, tmp_path, [{"source": {"doi": "10.9/moi"}}], {}, {})
    bg = M.doc_so()["muc"]["doi:10.9/moi"]
    assert "xac_minh_luc" not in bg and bg["ghi_chu_rut"] == "ok"
    assert M.con_hieu_luc(bg) == (False, M.LY_DO_CHUA_XAC_MINH_TON_TAI), "bản ghi trần không được tính còn hạn"
    assert "1 bản ghi hub MỚI chưa xác minh tồn tại" in out and "--phu-mo-coi" in out


# ── Rà #349 (vá 14/11/2026): ba góp ý mức thấp ──────────────────────────────────────────────────────────────────────

def test_quet_ledger_khong_dem_ban_ghi_tran_da_co_tu_truoc(M, monkeypatch, tmp_path):
    """Bộ lọc `k not in khoa_truoc`: bản ghi trần CŨ (đã nằm sẵn trong sổ) không được đếm là «MỚI» của lượt này."""
    so_truoc = {"pmid:777": {"loai": "pmid", "gia_tri": "777", "cac_dashboard": ["NC:de-tai-thu"]}}
    out = _chay_quet_ledger(M, monkeypatch, tmp_path, [{"source": {"doi": "10.9/moi"}}], {}, so_truoc)
    assert "1 bản ghi hub MỚI chưa xác minh tồn tại" in out, out
    assert "2 bản ghi hub MỚI" not in out


def test_quet_ledger_khong_dem_ban_ghi_moi_da_rut(M, monkeypatch, tmp_path):
    """Bản ghi hub mới là DƯƠNG TÍNH (`da_rut`): `--phu-mo-coi` bỏ qua nó ⇒ nhắc «chạy --phu-mo-coi» là lời khuyên vô ích."""
    the = [{"source": {"doi": "10.9/sach"}}, {"source": {"doi": "10.9/rut"}}]
    out = _chay_quet_ledger(M, monkeypatch, tmp_path, the, {"10.9/rut": {"status": "retracted"}}, {})
    muc = M.doc_so()["muc"]
    assert muc["doi:10.9/rut"]["da_rut"] is True and "xac_minh_luc" not in muc["doi:10.9/rut"]
    assert "1 bản ghi hub MỚI chưa xác minh tồn tại" in out, out


def test_quet_ledger_chi_co_ban_ghi_moi_da_rut_thi_im(M, monkeypatch, tmp_path):
    out = _chay_quet_ledger(M, monkeypatch, tmp_path, [{"source": {"doi": "10.9/rut"}}],
                            {"10.9/rut": {"status": "retracted"}}, {})
    assert "bản ghi hub MỚI" not in out


def test_bao_cao_khong_noi_vong_3_khong_cham_toi_ban_ghi_tran_co_dashboard(M):
    """Bản ghi trần CÓ liên kết dashboard: `--vong` gom từ dashboard nên CÓ phủ nó — không được in «KHÔNG chạm tới»."""
    _ghi_so(M, {"pmid:333": {"loai": "pmid", "gia_tri": "333", "cac_dashboard": ["WebDashboard_X.html"]}})
    rc, out = _bao_cao(M)
    assert rc == 1 and "[MA] CAN_PHU_MO_COI" in out
    assert "KHÔNG chạm tới" not in out
    assert "`--vong 3` cũng phủ được" in out


def test_bao_cao_tach_dem_vong_3_khi_tron_hai_nguon_goc(M):
    muc = {k: v for k, v in _so_mau().items() if k in ("doi:10.1/hub", "pmid:111")}
    muc["pmid:333"] = {"loai": "pmid", "gia_tri": "333", "cac_dashboard": ["WebDashboard_X.html"]}
    _ghi_so(M, muc)
    _rc, out = _bao_cao(M)
    assert "2 mục không liên kết dashboard nào: `--vong 3` KHÔNG chạm tới" in out
    assert "1 mục có liên kết dashboard: `--vong 3` cũng phủ được" in out


def test_bao_cao_chi_ban_ghi_tran_ngoai_dashboard_van_noi_khong_cham_toi(M):
    muc = {k: v for k, v in _so_mau().items() if k in ("doi:10.1/hub", "pmid:111")}
    _ghi_so(M, muc)
    _rc, out = _bao_cao(M)
    assert "`--vong 3` KHÔNG chạm tới nhóm này" in out
    assert "cũng phủ được" not in out
