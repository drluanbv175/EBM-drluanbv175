#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá 22/09/2026 (phản biện vòng 2, review:cong-rut-bai #7, LOW).

Một manifest SACH (âm tính — "không có cờ") duy nhất, không có báo cáo nào mới hơn để so sánh,
trước đây được coi là `hop_le=True` VÔ THỜI HẠN. Đo được ca thật 9+ tháng tuổi vẫn được trả về
như thể vừa mới dò xong. Nay có hạn HAN_AM_TINH_NGAY (92 ngày, khớp nhịp quý của
quarterly_superseded.sh) — dương tính (CO_BAI_MOI) không bị ảnh hưởng, chỉ ÂM TÍNH cần freshness.
"""
from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
spec = importlib.util.spec_from_file_location("kcv_han_am_tinh_test", TOOLS / "kiem_chung_cu_vuot_qua.py")
kcv = importlib.util.module_from_spec(spec)
sys.modules["kcv_han_am_tinh_test"] = kcv
spec.loader.exec_module(kcv)


def _man(**ghi_de) -> dict:
    m = {"phien_ban": 2, "ket_luan": "SACH", "ma_thoat": 0,
         "pham_vi": {"decision": ["apply"], "file": None, "gioi_han": None, "tu_nam": None, "toan_kho": True},
         "so_pmid_tong": 3, "so_pmid_do": 3, "so_pmid_hong": 0, "pmid_da_do": ["1", "2", "3"], "pmid_co_bai_moi": []}
    m.update(ghi_de)
    return m


def _ngay_cach_hom_nay(so_ngay: int) -> str:
    return (_dt.date.today() - _dt.timedelta(days=so_ngay)).strftime("%Y%m%d")


def test_manifest_sach_qua_han_khong_con_hop_le():
    ngay = _ngay_cach_hom_nay(kcv.HAN_AM_TINH_NGAY + 10)  # quá hạn 10 ngày
    with tempfile.TemporaryDirectory() as td:
        g = Path(td)
        (g / f"CHUNG-CU-VUOT-QUA_{ngay}.json").write_text(json.dumps(_man()), encoding="utf-8")
        r = kcv.doc_bao_cao_vuot_qua(g)
    assert r["hop_le"] is False, "manifest SACH quá hạn không còn là căn cứ 'không có cờ'"
    assert "quá hạn" in r["ly_do"]


def test_manifest_sach_trong_han_van_hop_le():
    ngay = _ngay_cach_hom_nay(kcv.HAN_AM_TINH_NGAY - 5)  # còn trong hạn
    with tempfile.TemporaryDirectory() as td:
        g = Path(td)
        (g / f"CHUNG-CU-VUOT-QUA_{ngay}.json").write_text(json.dumps(_man()), encoding="utf-8")
        r = kcv.doc_bao_cao_vuot_qua(g)
    assert r["hop_le"] is True


def test_duong_tinh_cua_manifest_qua_han_van_duoc_giu(monkeypatch):
    """Bất đối xứng: manifest QUÁ HẠN nhưng ket_luan=CO_BAI_MOI với PMID dương tính THẬT vẫn phải
    giữ được dương tính đó — chỉ mất tư cách 'hợp lệ để nói sạch', không mất dương tính đã biết."""
    ngay = _ngay_cach_hom_nay(kcv.HAN_AM_TINH_NGAY + 30)
    man = _man(ket_luan="CO_BAI_MOI", pmid_co_bai_moi=["2"])
    with tempfile.TemporaryDirectory() as td:
        g = Path(td)
        (g / f"CHUNG-CU-VUOT-QUA_{ngay}.json").write_text(json.dumps(man), encoding="utf-8")
        r = kcv.doc_bao_cao_vuot_qua(g)
    assert r["hop_le"] is False, "quá hạn ⇒ không còn 'hợp lệ để nói sạch'"
    assert r["pmids"] == {"2"}, "dương tính THẬT không có hạn — vẫn phải được giữ"


def test_ban_moi_trong_han_khong_bi_anh_huong_boi_ban_cu_qua_han():
    """Có HAI manifest: bản mới (trong hạn, SACH) và bản cũ hơn (quá hạn) — bản mới quyết định,
    quá hạn của bản cũ không ảnh hưởng gì (bản mới không cần rơi xuống bản cũ)."""
    ngay_moi = _ngay_cach_hom_nay(5)
    ngay_cu = _ngay_cach_hom_nay(kcv.HAN_AM_TINH_NGAY + 100)
    with tempfile.TemporaryDirectory() as td:
        g = Path(td)
        (g / f"CHUNG-CU-VUOT-QUA_{ngay_moi}.json").write_text(json.dumps(_man()), encoding="utf-8")
        (g / f"CHUNG-CU-VUOT-QUA_{ngay_cu}.json").write_text(json.dumps(_man()), encoding="utf-8")
        r = kcv.doc_bao_cao_vuot_qua(g)
    assert r["hop_le"] is True
    assert r["ngay"] == ngay_moi
