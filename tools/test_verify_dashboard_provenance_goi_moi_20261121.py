#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cổng verify_dashboard.py: gói MỚI khai provenanceUnknown mà không ghi lượt tìm của chính bản ⇒ CHẶN có sổ nợ (21/11/2026).

Bác sĩ 21/11/2026 «chặn có sổ nợ». Gói dựng từ 15/08/2026 (mốc luật PRISMA-S gói mới) mang cờ thì phải có searchSources ≥ 1
và currency có ngày — cờ vẫn được giữ cho mục kế thừa. Thiếu ⇒ lỗi; tệp trong sổ nợ `no-provenance-goi-moi.json` còn hạn ⇒
cảnh báo; quá hạn ⇒ lỗi; sổ hỏng ⇒ coi như vắng. Gói CŨ (trước mốc) giữ nguyên miễn trừ chỉ-cảnh-báo. Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py"
BAN_SAO = [REPO / "sync/skills/dark-analyst/tools/verify_dashboard.py"]
HOM_NAY = date(2026, 11, 21)


def _nap():
    sp = importlib.util.spec_from_file_location("_vd_prov_moi", NGUON)
    m = importlib.util.module_from_spec(sp)
    sys.modules["_vd_prov_moi"] = m
    sp.loader.exec_module(m)
    return m


vd = _nap()

ST_CHI_CO = '{ provenanceUnknown: true, provenanceUnknownLyDo: "bản sinh trước khi khối DATA.standards thành bắt buộc" }'
ST_CO_GHI = ('{ provenanceUnknown: true, provenanceUnknownLyDo: "4 mục kế thừa", '
             'searchSources:["PubMed E-utilities 4 tầng (2026-11-05)"], currency:"2026-11-05 — lượt quét A2" }')
ST_NGUON_KHONG_NGAY = ('{ provenanceUnknown: true, provenanceUnknownLyDo: "x", searchSources:["PubMed"], '
                       'currency:"lượt quét tuần trước" }')
ST_DU = '{ frame:"PICO", searchSources:["PubMed 2026-11-01","NICE"], currency:"2026-11-01" }'


def _data(standards: str | None, updated: str = "2026-11-01") -> str:
    st = f"  standards:{standards},\n" if standards is not None else ""
    return ("const DATA = {\n  meta:{updated:\"" + updated + "\"},\n" + st
            + "  items:[ {id:'ITEM-01', pmid:'12345678', decision:'consider', gradeLevel:'mod'} ]\n};\n")


def _kiem(tmp_path: Path, standards: str | None, ten: str = "WebDashboard_EBM_VanDeCuThe_BenhX_20261122.html",
          so_no: dict | str | None = None, updated: str = "2026-11-01", hom_nay: date = HOM_NAY):
    if so_no is not None:
        (tmp_path / vd.TEN_SO_NO_PROVENANCE).write_text(
            so_no if isinstance(so_no, str) else json.dumps(so_no, ensure_ascii=False), encoding="utf-8")
    e, w, o = [], [], []
    vd.kiem_provenance_goi_moi(_data(standards, updated), e, w, o, ten_tep=str(tmp_path / ten), hom_nay=hom_nay)
    return e, w, o


def _so(ten: str, han: str = "2026-12-21") -> dict:
    return {"han": han, "can_cu": "«chặn có sổ nợ» — thử", "muc": [{"dashboard": Path(ten).stem}]}


@pytest.mark.parametrize("standards, ky_vong", [
    (ST_DU, vd.PROV_DU), (ST_CHI_CO, vd.PROV_CHI_CO), (ST_CO_GHI, vd.PROV_CO_GHI),
    (ST_NGUON_KHONG_NGAY, vd.PROV_CHI_CO), (None, vd.PROV_THIEU),
    ('{ provenanceUnknown: true, provenanceUnknownLyDo: "x", currency:"2026-11-05" }', vd.PROV_CHI_CO),
])
def test_phan_loai_provenance(standards, ky_vong):
    assert vd.phan_loai_provenance(_data(standards)) == ky_vong


def test_goi_moi_chi_co_ngoai_so_bi_chan(tmp_path):
    e, w, _ = _kiem(tmp_path, ST_CHI_CO)
    assert len(e) == 1 and "PROVENANCE GÓI MỚI" in e[0] and "KHÔNG có trong sổ nợ" in e[0]
    assert "searchSources" in e[0] and "currency" in e[0]


def test_goi_moi_trong_so_con_han_chi_canh_bao(tmp_path):
    ten = "WebDashboard_EBM_VanDeCuThe_BenhX_20261025.html"
    e, w, _ = _kiem(tmp_path, ST_CHI_CO, ten=ten, so_no=_so(ten))
    assert e == [] and len(w) == 1 and "NỢ PROVENANCE GÓI MỚI" in w[0] and "còn 30 ngày" in w[0]


def test_no_qua_han_bi_chan(tmp_path):
    ten = "WebDashboard_EBM_VanDeCuThe_BenhX_20261025.html"
    e, w, _ = _kiem(tmp_path, ST_CHI_CO, ten=ten, so_no=_so(ten), hom_nay=date(2026, 12, 22))
    assert len(e) == 1 and "NỢ QUÁ HẠN 2026-12-21" in e[0]


def test_so_no_cua_tep_khac_khong_che(tmp_path):
    e, _, _ = _kiem(tmp_path, ST_CHI_CO, so_no=_so("WebDashboard_EBM_VanDeCuThe_BenhY_20261025.html"))
    assert len(e) == 1


def test_so_hong_coi_nhu_vang(tmp_path):
    ten = "WebDashboard_EBM_VanDeCuThe_BenhX_20261025.html"
    e, w, _ = _kiem(tmp_path, ST_CHI_CO, ten=ten, so_no="{hỏng")
    assert len(e) == 1 and any("KHÔNG đọc được" in x for x in w)


def test_goi_cu_truoc_moc_giu_mien_tru(tmp_path):
    for ngay in ("20260628", "20260814"):
        e, w, o = _kiem(tmp_path, ST_CHI_CO, ten=f"WebDashboard_EBM_VanDeCuThe_BenhX_{ngay}.html")
        assert e == [] and w == [] and o == [], ngay


def test_moc_dung_15_08_2026(tmp_path):
    e, _, _ = _kiem(tmp_path, ST_CHI_CO, ten="WebDashboard_EBM_VanDeCuThe_BenhX_20260815.html")
    assert len(e) == 1
    assert vd.MOC_PROVENANCE_GOI_MOI == date(2026, 8, 15)


def test_ke_thua_co_ghi_luot_moi_dat(tmp_path):
    e, w, o = _kiem(tmp_path, ST_CO_GHI)
    assert e == [] and w == [] and any("ĐÃ ghi" in x for x in o)


def test_nguon_co_ma_currency_khong_ngay_van_chan(tmp_path):
    assert len(_kiem(tmp_path, ST_NGUON_KHONG_NGAY)[0]) == 1


def test_khong_co_co_khong_dung(tmp_path):
    assert _kiem(tmp_path, ST_DU) == ([], [], [])
    assert _kiem(tmp_path, None) == ([], [], [])


def test_ten_khong_ngay_dung_meta_updated_va_fail_closed(tmp_path):
    assert len(_kiem(tmp_path, ST_CHI_CO, ten="goi_khong_ngay.html", updated="2026-11-01")[0]) == 1
    assert _kiem(tmp_path, ST_CHI_CO, ten="goi_khong_ngay.html", updated="2026-07-01") == ([], [], [])
    e, _, _ = _kiem(tmp_path, ST_CHI_CO, ten="goi_khong_ngay.html", updated="chưa rõ")
    assert len(e) == 1 and "không xác định" in e[0]


def _html(standards: str) -> str:
    return ("<html><body><p>Cần bác sĩ kiểm chứng</p><script>\n" + _data(standards)
            + "// HẾT KHỐI DATA\n</script></body></html>")


def test_main_strict_sources_goi_luat(tmp_path):
    tep = tmp_path / "WebDashboard_EBM_VanDeCuThe_BenhX_20261122.html"
    tep.write_text(_html(ST_CHI_CO), encoding="utf-8")
    r = subprocess.run([sys.executable, "-B", str(NGUON), str(tep), "--strict-sources"], capture_output=True, text=True,
                       encoding="utf-8")
    assert "PROVENANCE GÓI MỚI" in r.stdout and r.returncode != 0
    r2 = subprocess.run([sys.executable, "-B", str(NGUON), str(tep)], capture_output=True, text=True, encoding="utf-8")
    assert "PROVENANCE GÓI MỚI" not in r2.stdout, "luật chỉ chạy dưới --strict-sources như cổng nguồn chính thức"


def test_hai_ban_git_trung_byte():
    for p in BAN_SAO:
        assert p.read_bytes() == NGUON.read_bytes(), p
