"""Kiểm `tools/kiem_quan_the_chieu.py` (K1 quần thể + K4 chiều, 25/09/2026) — ngoại tuyến.

Văn bản nguồn là tóm tắt TỰ DỰNG cho phép thử (không phải trích nguyên văn bài báo nào).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "kiem_quan_the_chieu.py"
_sp = importlib.util.spec_from_file_location("kiem_quan_the_chieu", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

DASH_HTML = """<html><script>
const DATA = {
  meta:{question:'Thử K1/K4', updated:'2026-09-25'},
  summary:{conclusion:'x', doNow:[], dontDo:[], redFlags:[]},
  items:[
    {id:'ITEM-01', title:'A', pmid:'101', decision:'apply', population:'HFrEF, EF ≤40%, eGFR ≥ 20', action:'a'},
    {id:'ITEM-02', title:'B', pmid:'102', decision:'apply', population:'Suy tim HFpEF người lớn', action:'b'},
    {id:'ITEM-03', title:'C', pmid:'103', decision:'consider', population:'HFpEF', action:'c'},
    {id:'ITEM-04', title:'D', pmid:'104', decision:'apply', population:'Người ≥65 tuổi', action:'d'}
  ]
};
// HẾT KHỐI DATA
</script></html>"""

NGUON = {
    "101": {"title": "Drug X in heart failure with reduced ejection fraction",
            "abstract": "Adults with HFrEF and an ejection fraction of 40% or less and an eGFR of 25 to 75 "
                        "were randomized. Drug X reduced the primary outcome."},
    "102": {"title": "Drug Y in heart failure with reduced ejection fraction",
            "abstract": "Adults with reduced ejection fraction were enrolled. Drug Y did not significantly "
                        "reduce hospitalization."},
}


def _dash(tmp_path: Path) -> Path:
    p = tmp_path / "WebDashboard_K1K4_20260925.html"
    p.write_text(DASH_HTML, encoding="utf-8", newline="\n")
    return p


def _nguon(tmp_path: Path) -> str:
    p = tmp_path / "nguon.json"
    p.write_text(json.dumps(NGUON), encoding="utf-8", newline="\n")
    return str(p)


def test_trich_nguong_ca_hai_thu_tu():
    assert M.trich_nguong("HFrEF, EF ≤40%, eGFR ≥ 20") == [("ef", "40"), ("egfr", "20")]
    assert M.trich_nguong("Người ≥65 tuổi") == [("tuoi", "65")]
    assert M.trich_nguong("không có ngưỡng") == []


def test_nguong_khop_va_lech():
    ng = M.chuan_hoa(NGUON["101"]["abstract"])
    assert M.kiem_nguong("ef", "40", ng)[0] == "khop"
    muc, doan = M.kiem_nguong("egfr", "20", ng)
    assert muc == "can_doc" and "25" in doan          # nguồn là 25, mục ghi 20
    assert M.kiem_nguong("hba1c", "7", ng)[0] == "chua_kiem"   # nguồn không nhắc chỉ số


def test_cap_quan_the_loai_tru():
    ng = M.chuan_hoa("adults with reduced ejection fraction")
    kq = {x["ve_muc"]: x["muc"] for x in M.kiem_cap(M.chuan_hoa("suy tim hfpef người lớn"), ng)}
    assert kq == {"HFpEF": "can_doc", "người lớn": "khop"}
    # «non-dialysis» KHÔNG được đọc thành «dialysis»
    kq2 = M.kiem_cap(M.chuan_hoa("bệnh thận mạn không lọc máu"), M.chuan_hoa("patients with non-dialysis ckd"))
    assert kq2 == [{"ve_muc": "không lọc máu", "ve_nguon": "không lọc máu", "muc": "khop"}]
    kq3 = M.kiem_cap(M.chuan_hoa("bệnh nhân lọc máu"), M.chuan_hoa("patients not on dialysis"))
    assert kq3[0]["muc"] == "can_doc"


def test_k4_bat_tin_hieu_nguoc_chieu():
    assert M.kiem_chieu(M.chuan_hoa(NGUON["102"]["abstract"]))
    assert M.kiem_chieu(M.chuan_hoa("SGLT2 inhibitors are not recommended in type 1 diabetes."))
    assert M.kiem_chieu(M.chuan_hoa(NGUON["101"]["abstract"])) == []


def test_dau_cuoi_ma_thoat_va_chi_muc_apply(tmp_path, capsys):
    rc = M.main([str(_dash(tmp_path)), "--nguon-json", _nguon(tmp_path), "--json"])
    kq = json.loads(capsys.readouterr().out)
    ids = [d["id"] for d in kq["muc"]]
    assert ids == ["ITEM-01", "ITEM-02", "ITEM-04"]     # consider bị bỏ
    assert rc == 1                                       # có 🟠
    it4 = kq["muc"][2]
    assert it4["co_nguon"] is False                      # không có nguồn ⇒ ⚪, không bao giờ ✓
    assert it4["k4"] is None and it4["k1_nguong"] == [] and it4["k1_cap"] == []   # không phán gì
    assert kq["dem"]["chua_kiem"] >= 1


def test_khong_nguon_nao_la_ma_2(tmp_path, capsys):
    rc = M.main([str(_dash(tmp_path))])
    assert rc == 2
    assert "chưa kiểm" in capsys.readouterr().out
