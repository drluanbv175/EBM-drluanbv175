"""Kiểm `tools/kiem_cheo_ngu_nghia.py` (K3, 25/09/2026) — ngoại tuyến, dashboard giả tự dựng."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "kiem_cheo_ngu_nghia.py"
_sp = importlib.util.spec_from_file_location("kiem_cheo_ngu_nghia", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

DASH_HTML = """<html><script>
const DATA = {
  meta:{question:'SGLT2i ở HFrEF', updated:'2026-09-25'},
  summary:{
    conclusion:'Thêm SGLT2i cho HFrEF nếu không có chống chỉ định.',
    doNow:['Khởi trị SGLT2i khi đã tối ưu nền tảng','Theo dõi eGFR'],
    dontDo:['Không dùng khi eGFR dưới 20'],
    redFlags:['DKA']
  },
  items:[
    {id:'ITEM-01', title:'A', pmid:'1', decision:'apply', action:'Dùng ngoài thai kỳ, trừ khi có đái tháo đường típ 1.'},
    {id:'ITEM-02', title:'B', pmid:'2', decision:'consider', action:'Chỉ khi bệnh nhân đồng ý tham gia.'},
    {id:'ITEM-03', title:'C', pmid:'3', decision:'apply', action:'Khởi trị sớm.'}
  ]
};
// HẾT KHỐI DATA
</script></html>"""


def _dash(tmp_path: Path) -> Path:
    p = tmp_path / "WebDashboard_Test_20260925.html"
    p.write_text(DASH_HTML, encoding="utf-8", newline="\n")
    return p


def test_trich_cum_dieu_kien_uu_tien_cum_dai_va_bo_khi_tro_troi():
    assert M.trich_cum_dieu_kien("Dùng thuốc trừ khi có suy gan nặng.") == ["trừ khi có suy gan nặng"]
    assert M.trich_cum_dieu_kien("Theo dõi khi cần") == []           # «khi» + 1 từ ⇒ bỏ
    assert M.trich_cum_dieu_kien("Dùng ngoài thai kỳ.") == ["ngoài thai kỳ"]
    assert M.trich_cum_dieu_kien("Không có điều kiện gì ở đây") == []


def test_chi_lay_muc_apply_va_summary(tmp_path):
    nguon = M.lay_nguon_dieu_kien(M.doc_data(_dash(tmp_path)))
    vi_tri = [n["vi_tri"] for n in nguon]
    assert "summary.conclusion" in vi_tri and "summary.doNow[0]" in vi_tri
    assert "summary.dontDo[0]" in vi_tri and "ITEM-01.action" in vi_tri
    assert "ITEM-02.action" not in vi_tri          # consider ⇒ không lấy
    assert "ITEM-03.action" not in vi_tri          # apply nhưng không có điều kiện


def test_rung_dieu_kien_bi_bat_con_nguyen_thi_xanh(tmp_path):
    dash = _dash(tmp_path)
    du = tmp_path / "ban_doc_du.html"
    du.write_text("<p>Thêm SGLT2i cho HFrEF <b>nếu không có chống chỉ định</b>.</p>"
                  "<li>Khởi trị SGLT2i khi đã tối ưu nền tảng</li><li>Không dùng khi eGFR dưới 20</li>"
                  "<p>Dùng ngoài thai kỳ, trừ khi có đái tháo đường típ 1.</p>", encoding="utf-8", newline="\n")
    rung = tmp_path / "ban_doc_rung.html"
    rung.write_text("<p>Thêm SGLT2i cho HFrEF.</p><li>Khởi trị SGLT2i</li>", encoding="utf-8", newline="\n")
    assert M.main([str(dash), "--ban-doc", str(du)]) == 0
    assert M.main([str(dash), "--ban-doc", str(rung)]) == 1


def test_khong_co_san_pham_la_khong_do_duoc(tmp_path):
    assert M.main([str(_dash(tmp_path))]) == 2      # không bao giờ thành 0
    assert M.main([str(tmp_path / "khong-co.html"), "--ban-doc", str(tmp_path / "x")]) == 2


def test_ung_vien_bo_vang_khong_ghi_de_nhan_bac_si(tmp_path):
    dash = _dash(tmp_path)
    dich = tmp_path / "bo-vang.json"
    assert M.main([str(dash), "--ung-vien-bo-vang", "--dich", str(dich)]) == 0
    d = json.loads(dich.read_text(encoding="utf-8"))
    assert [m["id"] for m in d["muc"]] == ["ITEM-01", "ITEM-03"]    # chỉ apply có PMID
    assert all(v is None for m in d["muc"] for v in m["nhan_bac_si"].values())   # máy không gắn nhãn
    d["muc"][0]["nhan_bac_si"]["dung_chieu"] = True
    dich.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8", newline="\n")
    assert M.main([str(dash), "--ung-vien-bo-vang", "--dich", str(dich), "--ghi-de"]) == 2
    assert json.loads(dich.read_text(encoding="utf-8"))["muc"][0]["nhan_bac_si"]["dung_chieu"] is True
