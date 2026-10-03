#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #13 (đợt dò nâng cấp 26/09/2026): PMID dạng «PMID 12345678» trong references[].

Tái hiện gốc: regex tầng 2/3 của `kiem_nguon_da_rut` bắt buộc có ':'/'=' sau «pmid», nên dạng
«… PMID 9500320.» — đúng định dạng references của template EW — bị bỏ sót. Bài Wakefield (đã rút)
nằm trong references làm cổng PASS mã 0 và không hiện cả trong đếm phạm vi. `gom_nguon` của sổ cũng
chỉ lấy trường pmid/doi/url của item nên `--quet` không bao giờ kiểm các định danh đó.

Ngoại tuyến 100%: sổ + nền Retraction Watch là stub; không đọc dashboard thật.
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VD_NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


STUB_SO = '''
def nguon_da_rut(ten): return []
def dinh_danh_da_rut(ids): return []
def pham_vi_kiem_rut_bai(ids):
    co = [i for i in ids if i in _CO]
    return {"co": co, "chua": [i for i in ids if i not in _CO]}
def rut_bai_retraction_watch_ngoai_tuyen(pmids):
    return [{"khoa": "pmid:"+p, "loai": "pmid", "gia_tri": p, "tinh_trang": "retracted", "tieu_de": "",
             "kiem_luc": "2026-09-26", "nguon": "Retraction Watch (nền ngoại tuyến; lý do: x)", "rut_va_thay": False,
             "thong_bao": "", "sua_loi_bi_rut": False, "thong_bao_ids": []} for p in pmids if p in _RUT]
'''


def _dung_cay(tmp: Path, refs: list[str], co: set, rut: set, ghi_chu: str = ""):
    (tmp / "tools").mkdir()
    shutil.copy(VD_NGUON, tmp / "tools" / "verify_dashboard.py")
    (tmp / "tools" / "so_xac_minh_nguon.py").write_text(
        f"_CO = {sorted(co)!r}\n_RUT = {sorted(rut)!r}\n" + STUB_SO, encoding="utf-8")
    refs_js = ", ".join(repr(r) for r in refs)
    note = (", note:%r" % ghi_chu) if ghi_chu else ""
    page = tmp / "WebDashboard_EBM_VanDeCuThe_X_20260926.html"
    page.write_text("<script>const DATA={items:[{id:'ITEM-01', pmid:'34101376'%s, references:[%s]}]}</script>"
                    % (note, refs_js), encoding="utf-8")
    vd = _nap("vd_refs_" + tmp.name, tmp / "tools" / "verify_dashboard.py")
    return vd, page


def _chay(vd, page):
    errors, warns, oks = [], [], []
    vd.kiem_nguon_da_rut(str(page), errors, warns, oks)
    return errors, warns, oks


def test_pmid_da_rut_trong_references_dang_khoang_trang_bi_chan(tmp_path):
    vd, page = _dung_cay(tmp_path, ["Tác giả. Tiêu đề. Lancet 2021. PMID 34101376.",
                                    "Supporting RCT. Lancet 1998;351:637-641. PMID 9500320."],
                         co={"34101376"}, rut={"9500320"})
    errors, _w, oks = _chay(vd, page)
    assert any("ĐÃ BỊ RÚT" in e and "9500320" in e for e in errors), errors
    assert not any("Rút bài:" in o for o in oks)


def test_bien_the_co_hai_cham_cung_bi_chan(tmp_path):
    vd, page = _dung_cay(tmp_path, ["Supporting RCT. PMID: 9500320"], co={"34101376"}, rut={"9500320"})
    errors, _w, _o = _chay(vd, page)
    assert any("ĐÃ BỊ RÚT" in e and "9500320" in e for e in errors), errors


def test_pham_vi_dem_ca_pmid_trong_references(tmp_path):
    vd, page = _dung_cay(tmp_path, ["Supporting RCT. PMID 9500320."], co={"34101376"}, rut=set())
    errors, warns, _o = _chay(vd, page)
    assert not errors
    pv = [w for w in warns if "Phạm vi kiểm rút bài" in w]
    assert pv and "1/2" in pv[0] and "9500320" in pv[0], warns


def test_ghi_chu_ngoai_references_khong_bi_quet(tmp_path):
    """KHÔNG quét cả tệp: ghi chú giải thích vì sao LOẠI một bài đã rút không được biến thành trích dẫn."""
    vd, page = _dung_cay(tmp_path, ["Tác giả. PMID 34101376."], co={"34101376"}, rut={"9500320"},
                         ghi_chu="Đã loại PMID 9500320 vì bài bị rút năm 2010")
    errors, _w, _o = _chay(vd, page)
    assert not any("9500320" in e for e in errors), errors


def test_ham_thuan_pmid_trong_references():
    vd = _nap("vd_refs_thuan_20260926", VD_NGUON)
    html = ("<script>const DATA={items:[{id:'ITEM-01', note:'PMID 11111111', references:['A. PMID 22222222.', "
            "\"B. pmid: 33333333\", 'C. PMIDX 44444444']}, {id:'ITEM-02', references:['D. PMID 55555555']}]}</script>")
    assert vd.pmid_trong_references(html) == {"22222222", "33333333", "55555555"}


def test_gom_nguon_thu_ca_dinh_danh_trong_references(tmp_path):
    so = _nap("so_refs_20260926", ROOT / "tools" / "so_xac_minh_nguon.py")
    vd = _nap("vd_refs_gom_20260926", VD_NGUON)
    f = tmp_path / "WebDashboard_EBM_VanDeCuThe_Y_20260926.html"
    f.write_text("<script>const DATA={items:[{id:'ITEM-01', pmid:'34101376', note:'PMID 11111111', "
                 "references:['Supporting RCT. PMID 9500320.', 'Khác. doi:10.1016/S0140-6736(97)11096-0.']}]}"
                 "</script>", encoding="utf-8")
    nguon = so.gom_nguon([f], vd)
    assert "pmid:34101376" in nguon
    assert "pmid:9500320" in nguon, sorted(nguon)
    # Từ 03/10/2026 khoá DOI của sổ ở DẠNG CHUẨN chữ thường (so_xac_minh_nguon.chuan_hoa_khoa — DOI không phân biệt
    # hoa/thường); kỳ vọng cũ giữ nguyên chữ hoa chính là hành vi đã sinh bản ghi trùng.
    assert "doi:10.1016/s0140-6736(97)11096-0" in nguon, sorted(nguon)
    assert "pmid:11111111" not in nguon, "ghi chú ngoài references không phải nguồn gói trích"
