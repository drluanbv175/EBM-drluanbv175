#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #3 (đợt dò nâng cấp 26/09/2026): sổ xác minh HỎNG không được đọc thành sổ RỖNG.

Tái hiện gốc: `doc_so()` bắt JSONDecodeError rồi trả `{"muc": {}}` ⇒ (1) cổng verify_dashboard mất mọi dương
tính rút bài (PASS mã 0 với DOI đã rút — chỉ còn một dòng stderr không thuộc kết luận); (2) lượt
`--quet/--vong` kế tiếp ghi sổ rỗng đè lên tệp hỏng, không sao lưu (EBM-Dashboards ngoài git) — mất vĩnh viễn.

Ngoại tuyến 100%: sổ ở thư mục tạm, mạng không được gọi (doc_so ném lỗi TRƯỚC mọi lời gọi mạng).
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
VD_NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


SO = _nap("so_hong_20260926", ROOT / "tools" / "so_xac_minh_nguon.py")

SO_HOP_LE = {"phien_ban": 1, "muc": {
    "doi:10.9999/retracted.demo": {"loai": "doi", "gia_tri": "10.9999/retracted.demo", "da_rut": True,
                                   "ghi_chu_rut": "retracted", "cac_dashboard": ["WebDashboard_EBM_VanDeCuThe_X_20260926.html"],
                                   "kiem_rut_luc": "2026-09-20T10:00:00"},
    "pmid:12345678": {"loai": "pmid", "gia_tri": "12345678", "da_rut": True, "ghi_chu_rut": "retracted",
                      "cac_dashboard": []},
    "pmid:34101376": {"loai": "pmid", "gia_tri": "34101376", "ghi_chu_rut": "ok", "xac_minh_luc": "2026-09-20"},
}}


def _van_hop_le() -> str:
    return json.dumps(SO_HOP_LE, ensure_ascii=False, indent=2, sort_keys=True)


@pytest.fixture()
def so_tam(tmp_path, monkeypatch):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    so = dash / ".so-xac-minh-nguon.json"
    monkeypatch.setattr(SO, "DASH", dash)
    monkeypatch.setattr(SO, "SO", so)
    return so


HONG = {
    "cat_cut": lambda: _van_hop_le()[:-7].encode("utf-8"),
    "rong_0_byte": lambda: b"",
    "chi_khoang_trang": lambda: b"  \n",
    "khong_utf8": lambda: b"\xff\xfe\x00{",
    "goc_la_list": lambda: b"[]",
    "muc_khong_phai_dict": lambda: b'{"phien_ban": 1, "muc": []}',
    "thieu_muc": lambda: b'{"phien_ban": 1}',
}


# ── 1. doc_so ──────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("kieu", sorted(HONG))
def test_so_hong_nem_loi_khong_tra_rong(so_tam, kieu):
    so_tam.write_bytes(HONG[kieu]())
    with pytest.raises(SO.SoHongLoi) as ei:
        SO.doc_so()
    assert "HỎNG" in str(ei.value) and "--cuu-so-hong" in str(ei.value)


def test_so_vang_van_la_so_rong(so_tam):
    assert not so_tam.exists()
    assert SO.doc_so() == {"phien_ban": 1, "muc": {}}


def test_so_hop_le_doc_binh_thuong(so_tam):
    so_tam.write_text(_van_hop_le(), encoding="utf-8")
    assert SO.dinh_danh_da_rut(["10.9999/retracted.demo"])[0]["gia_tri"] == "10.9999/retracted.demo"


def test_ham_cong_goi_so_hong_deu_nem_loi(so_tam):
    so_tam.write_bytes(HONG["cat_cut"]())
    for goi in (lambda: SO.nguon_da_rut("a.html"), lambda: SO.dinh_danh_da_rut(["1"]),
                lambda: SO.pham_vi_kiem_rut_bai(["1"])):
        with pytest.raises(SO.SoHongLoi):
            goi()


# ── 2. Không ghi đè sổ hỏng — mọi lệnh CLI ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("argv", [["--quet", "{page}", "--vong", "1"], ["--bao-cao"], ["--phu-mo-coi"],
                                  ["--kiem-rut-lai", "pmid:12345678"]])
def test_moi_lenh_tren_so_hong_tra_2_va_khong_doi_byte(so_tam, tmp_path, capsys, argv):
    tho = HONG["cat_cut"]()
    so_tam.write_bytes(tho)
    page = tmp_path / "EBM-Dashboards" / "WebDashboard_EBM_VanDeCuThe_X_20260926.html"
    page.write_text("<script>const DATA={items:[{id:'ITEM-01', doi:'10.9999/retracted.demo'}]}</script>",
                    encoding="utf-8")
    vd = _nap("vd_so_hong_cli_20260926", VD_NGUON)
    argv = [x.replace("{page}", str(page)) for x in argv]
    with mock.patch.object(SO, "_nap_verify_dashboard", lambda: vd), \
         mock.patch.object(SO, "xac_minh_mot", lambda khoa, vd: None), \
         mock.patch.object(SO, "kiem_rut_bai", lambda pmids: {}), \
         mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", *argv]):
        rc = SO.main()
    err = capsys.readouterr().err
    assert rc == 2, argv
    assert "SO_HONG" in err and "HỎNG" in err
    assert so_tam.read_bytes() == tho, "sổ hỏng bị ghi đè — dương tính rút bài mất vĩnh viễn"
    assert not list(so_tam.parent.glob("*.tmp"))


# ── 3. ghi_so nguyên tử ────────────────────────────────────────────────────────────────────────────────
def test_ghi_so_dung_os_replace(so_tam):
    goi = []
    that = os.replace

    def _ghi_lai(a, b):
        goi.append((Path(a).name, Path(b).name))
        return that(a, b)
    with mock.patch.object(os, "replace", _ghi_lai):
        SO.ghi_so(SO_HOP_LE)
    assert goi == [(so_tam.name + ".tmp", so_tam.name)]
    assert json.loads(so_tam.read_text(encoding="utf-8")) == SO_HOP_LE


def test_ghi_so_bi_ngat_giua_chung_khong_lam_hong_so_cu(so_tam):
    so_tam.write_text(_van_hop_le(), encoding="utf-8")
    truoc = so_tam.read_bytes()
    with mock.patch.object(os, "fsync", side_effect=KeyboardInterrupt), pytest.raises(KeyboardInterrupt):
        SO.ghi_so({"phien_ban": 1, "muc": {}})
    assert so_tam.read_bytes() == truoc
    assert not list(so_tam.parent.glob("*.tmp"))


# ── 4. Cổng verify_dashboard: sổ hỏng là LỖI CỨNG ─────────────────────────────────────────────────────
def _dung_cay(tmp: Path, noi_dung_so: bytes | None):
    (tmp / "tools").mkdir()
    shutil.copy(ROOT / "tools" / "so_xac_minh_nguon.py", tmp / "tools" / "so_xac_minh_nguon.py")
    shutil.copy(ROOT / "tools" / "ban_sao_tran.py", tmp / "tools" / "ban_sao_tran.py")
    dash = tmp / "EBM-Dashboards"
    (dash / "tools").mkdir(parents=True)
    shutil.copy(VD_NGUON, dash / "tools" / "verify_dashboard.py")
    if noi_dung_so is not None:
        (dash / ".so-xac-minh-nguon.json").write_bytes(noi_dung_so)
    page = dash / "WebDashboard_EBM_VanDeCuThe_X_20260926.html"
    page.write_text("<script>const DATA={items:[{id:'ITEM-01', doi:'10.9999/retracted.demo'}]}</script>",
                    encoding="utf-8")
    vd = _nap("vd_so_hong_" + tmp.name, dash / "tools" / "verify_dashboard.py")
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    return errors, warns, oks


def test_cong_so_hong_la_loi_cung(tmp_path):
    errors, _w, oks = _dung_cay(tmp_path, HONG["cat_cut"]())
    assert any("Sổ xác minh nguồn HỎNG" in e for e in errors), errors
    assert not any("Rút bài:" in o for o in oks)


def test_cong_so_hop_le_van_chan_doi_da_rut(tmp_path):
    errors, _w, _o = _dung_cay(tmp_path, _van_hop_le().encode("utf-8"))
    assert any("ĐÃ BỊ RÚT" in e and "10.9999/retracted.demo" in e for e in errors), errors


def test_cong_so_vang_chi_la_chua_kiem_khong_phai_loi(tmp_path):
    errors, warns, _o = _dung_cay(tmp_path, None)
    assert not any("HỎNG" in e for e in errors)
    assert any("Phạm vi kiểm rút bài" in w for w in warns), warns


# ── 5. --cuu-so-hong ───────────────────────────────────────────────────────────────────────────────────
def test_cuu_so_hong_giu_ban_hong_va_cuu_duong_tinh(so_tam, capsys):
    tho = HONG["cat_cut"]()
    so_tam.write_bytes(tho)
    with mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--cuu-so-hong"]):
        assert SO.main() == 0
    hong = list(so_tam.parent.glob(".so-xac-minh-nguon.hong-*.json"))
    assert len(hong) == 1 and hong[0].read_bytes() == tho, "bản hỏng phải được GIỮ NGUYÊN byte"
    moi = SO.doc_so()["muc"]
    assert moi["doi:10.9999/retracted.demo"]["da_rut"] is True
    assert moi["pmid:12345678"]["da_rut"] is True
    assert "pmid:34101376" not in moi, "chỉ cứu dương tính — dấu vết «ok» không được cứu thành «đã kiểm»"


def test_cuu_so_hong_tu_choi_khi_so_khong_hong(so_tam):
    so_tam.write_text(_van_hop_le(), encoding="utf-8")
    truoc = so_tam.read_bytes()
    with mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--cuu-so-hong"]):
        assert SO.main() == 1
    assert so_tam.read_bytes() == truoc
    assert not list(so_tam.parent.glob(".so-xac-minh-nguon.hong-*.json"))


# ── 6. chu_trinh: sổ hỏng không bị gọi là «có nguồn rút bỏ hẳn» ─────────────────────────────────────────
def test_chu_trinh_bao_so_hong_dung_ban_chat(capsys):
    sys.path.insert(0, str(ROOT / "tools"))
    import chu_trinh_chung_cu as ctcc

    class _P:
        def __init__(self, rc, out):
            self.returncode, self.stdout, self.stderr = rc, out, ""

    def _goi(cmd, **kw):
        if "so_xac_minh_nguon.py" in str(cmd[1]):
            return _P(2, "⛔ Sổ xác minh nguồn HỎNG …\n[MA] SO_HONG — không ghi gì vào sổ.")
        return _P(0, "")
    with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
         mock.patch.object(ctcc.subprocess, "run", side_effect=_goi):
        rc = ctcc.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "SỔ XÁC MINH NGUỒN HỎNG" in out
    assert "CÓ NGUỒN RÚT BỎ HẲN" not in out
    assert "🟢 Mọi chốt đạt" not in out
