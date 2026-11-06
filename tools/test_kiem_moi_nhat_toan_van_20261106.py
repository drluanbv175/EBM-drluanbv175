"""Kiểm `tools/kiem_moi_nhat_toan_van.py` (06/11/2026) — ngoại tuyến, dashboard giả tự dựng, hàm toàn văn tiêm vào.

Mỗi phép thử một luật: M1 guideline ≥ 5 năm thiếu dấu «đã kiểm phiên bản» · dấu cũ > 365 ngày · M2 nguồn mạnh/mới/apply
chưa có toàn văn · mục không PMID ⇒ ⚪ (không bao giờ «đã có») · consider cũ/yếu không vào M2 · mã thoát.
"""
from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "kiem_moi_nhat_toan_van.py"
_sp = importlib.util.spec_from_file_location("kiem_moi_nhat_toan_van", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

HOM_NAY = date(2026, 11, 6)


def _it(**kw):
    goc = {"id": "ITEM-01", "design": "Guideline", "dateVersion": "2026", "pmid": "111", "decision": "consider",
           "gradeSource": ""}
    goc.update(kw)
    return goc


def _kq(items, co=lambda p, k: False, kho=Path(".")):
    return M.kiem({"meta": {"updated": "2026-11-06"}, "items": items}, kho, hom_nay=HOM_NAY, co_toan_van=co)


def test_m1_guideline_cu_khong_dau_bi_bat():
    kq = _kq([_it(design="Guideline — ICFSR", dateVersion="2019", decision="notyet")])
    assert [d["id"] for d in kq["m1"]] == ["ITEM-01"]
    assert kq["m1"][0]["tuoi"] == 7


def test_m1_guideline_cu_co_dau_moi_thi_xanh():
    kq = _kq([_it(dateVersion="2019", decision="notyet",
                  gradeSource="Mạnh/Trung bình — đã kiểm phiên bản 06/11/2026: chưa có bản thay thế")])
    assert kq["m1"] == [] and kq["m1_cu"] == []


def test_m1_dau_cu_qua_han_nhac_kiem_lai():
    kq = _kq([_it(dateVersion="2018", decision="notyet", gradeSource="đã kiểm phiên bản 01/10/2025: chưa có bản thay thế")])
    assert kq["m1"] == [] and [d["id"] for d in kq["m1_cu"]] == ["ITEM-01"]


def test_m1_bien_dung_5_nam_bi_bat_4_nam_thi_khong():
    kq = _kq([_it(id="ITEM-01", dateVersion="2021", decision="notyet"),
              _it(id="ITEM-02", dateVersion="2022", decision="notyet")])
    assert [d["id"] for d in kq["m1"]] == ["ITEM-01"]


def test_m2_bien_consider_dung_3_nam_van_vao():
    kq = _kq([_it(decision="consider", design="Meta", dateVersion="2023")])
    assert len(kq["m2"]) == 1


def test_m1_khong_ap_cho_rct_va_guideline_con_moi():
    kq = _kq([_it(id="ITEM-01", design="RCT", dateVersion="2010", decision="notyet"),
              _it(id="ITEM-02", design="Guideline", dateVersion="2022", decision="notyet")])
    assert kq["m1"] == []


def test_m1_nhan_dong_thuan_va_nhan_thuoc():
    kq = _kq([_it(id="ITEM-01", design="Consensus — Delphi", dateVersion="2015", decision="notyet"),
              _it(id="ITEM-02", design="Nhãn thuốc FDA", dateVersion="2012", decision="notyet")])
    assert {d["id"] for d in kq["m1"]} == {"ITEM-01", "ITEM-02"}


def test_m2_apply_va_consider_manh_moi_chua_co_toan_van():
    kq = _kq([_it(id="ITEM-01", decision="apply", design="Cohort", dateVersion="2015"),
              _it(id="ITEM-02", decision="consider", design="Meta — tổng quan hệ thống", dateVersion="2024"),
              _it(id="ITEM-03", decision="consider", design="RCT", dateVersion="2025")])
    assert [d["id"] for d in kq["m2"]] == ["ITEM-01", "ITEM-02", "ITEM-03"]
    assert kq["tong"]["ung_vien_m2"] == 3


def test_m2_bo_qua_consider_cu_hoac_yeu_va_notyet():
    kq = _kq([_it(id="ITEM-01", decision="consider", design="Meta", dateVersion="2020"),
              _it(id="ITEM-02", decision="consider", design="Cohort", dateVersion="2026"),
              _it(id="ITEM-03", decision="notyet", design="RCT", dateVersion="2026")])
    assert kq["m2"] == [] and kq["tong"]["ung_vien_m2"] == 0


def test_m2_da_co_toan_van_thi_khong_bao():
    kq = _kq([_it(decision="apply", pmid="222")], co=lambda p, k: p == "222")
    assert kq["m2"] == [] and kq["tong"]["ung_vien_m2"] == 1


def test_m2_khong_pmid_la_khong_do_duoc_khong_phai_da_co():
    kq = _kq([_it(decision="apply", pmid="")], co=lambda p, k: True)
    assert kq["m2"] == [] and [d["id"] for d in kq["khong_do"]] == ["ITEM-01"]


def test_m2_thieu_ham_cong_la_khong_do_duoc():
    kq = M.kiem({"items": [_it(decision="apply")]}, Path("."), hom_nay=HOM_NAY, co_toan_van=None)
    assert kq["m2"] == [] and len(kq["khong_do"]) == 1


def test_dau_da_kiem_ngay_sai_la_none():
    assert M.dau_da_kiem({"gradeSource": "đã kiểm phiên bản 31/02/2026: chưa có"}) is None
    assert M.dau_da_kiem({"gradeSource": "đã kiểm bản thay thế 5/3/2026 — ESC 2025"}) == date(2026, 3, 5)


DASH = """<html><script>
const DATA = {
  meta:{question:'Thử', updated:'2026-11-06'},
  summary:{conclusion:'x', doNow:[], dontDo:[], redFlags:[]},
  items:[
    {id:'ITEM-01', title:'A', pmid:'101', design:'Guideline', dateVersion:'2017', decision:'consider', gradeSource:'Mạnh'},
    {id:'ITEM-02', title:'B', pmid:'102', design:'RCT', dateVersion:'2025', decision:'consider', gradeSource:''}
  ]
};
// HẾT KHỐI DATA
</script></html>"""


def test_main_doc_dashboard_that_ma_thoat_1_khi_co_canh_bao(tmp_path, capsys):
    p = tmp_path / "WebDashboard_Thu_20261106.html"
    p.write_text(DASH, encoding="utf-8", newline="\n")
    (tmp_path / "toan_van_oa").mkdir()
    ma = M.main([str(p), "--json"])
    out = json.loads(capsys.readouterr().out)
    assert ma == 1
    assert [d["id"] for d in out["m1"]] == ["ITEM-01"]
    assert [d["id"] for d in out["m2"]] == ["ITEM-02"]


def test_main_khong_doc_duoc_data_ma_2(tmp_path, capsys):
    p = tmp_path / "khong_phai_dashboard.html"
    p.write_text("<html>không có DATA</html>", encoding="utf-8", newline="\n")
    assert M.main([str(p)]) == 2
