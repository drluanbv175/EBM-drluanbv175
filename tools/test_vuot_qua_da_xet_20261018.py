"""Sổ «bác sĩ đã xét» nguồn tổng hợp mới hơn — 18/10/2026.

Lỗi đo thật: `dat_canh_chung_cu_moi.py` đếm mọi mục `apply` có bài tổng hợp «mới hơn» do PubMed gợi ý — kể cả bài lạc chủ
đề — và không có chỗ ghi «đã so» ⇒ con số 112 (18/10) không bao giờ giảm. Thêm: `EBM-Dashboards/vuot-qua-da-xet.json`
(chỉ `ghi_vuot_qua_da_xet.py` ghi, theo nguyên văn lời bác sĩ). Kèm vá phụ: trước đây «không mục nào có ứng viên» bị báo
«Không hỏi được PubMed» (mã 2) ngay cả khi PubMed đã trả lời đủ. Ngoại tuyến: mạng, verify_dashboard và CLI rút bài đều
được thay bằng hàm giả; chỉ ghi trong tmp_path.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import dat_canh_chung_cu_moi as DC  # noqa: E402
import ghi_vuot_qua_da_xet as G  # noqa: E402

MOI = {"111": [{"pmid": "900", "nam": 2025, "title": "Lạc đề", "journal": "J", "pubtype": ["Practice Guideline"]}],
       "222": [{"pmid": "901", "nam": 2026, "title": "Cùng câu hỏi", "journal": "J", "pubtype": ["Meta-Analysis"]}],
       "333": None}


def test_da_xet_het_chi_khi_ket_luan_dong_va_phu_moi_nguon_moi():
    so = {"111": {"pmid_moi_da_xet": ["900"], "ket_luan": "lac_chu_de"},
          "222": {"pmid_moi_da_xet": ["901"], "ket_luan": "can_cap_nhat"}}
    assert DC.da_xet_het("111", MOI["111"], so) is True
    assert DC.da_xet_het("111", MOI["111"] + [{"pmid": "902"}], so) is False, "nguồn MỚI chưa xét ⇒ mục mở lại"
    assert DC.da_xet_het("222", MOI["222"], so) is False, "can_cap_nhat không đóng mục"
    assert DC.da_xet_het("111", [], so) is False
    assert DC.da_xet_het("999", MOI["111"], so) is False


def test_so_vang_hoac_hong_thi_khong_loc_gi(tmp_path):
    assert DC.doc_da_xet(tmp_path / "vang.json") == {}
    (tmp_path / "hong.json").write_text("{", encoding="utf-8", newline="\n")
    assert DC.doc_da_xet(tmp_path / "hong.json") == {}
    (tmp_path / "sai.json").write_text('{"muc": [1]}', encoding="utf-8", newline="\n")
    assert DC.doc_da_xet(tmp_path / "sai.json") == {}


@pytest.fixture()
def gia(tmp_path, monkeypatch):
    dash = tmp_path / "EBM-Dashboards"
    (dash / "derivatives").mkdir(parents=True)
    items = [{"decision": "apply", "pmid": p, "title": f"Mục {p}", "id": f"ITEM-{p}", "dateVersion": "2020"}
             for p in ("111", "222", "333")]
    (dash / "WebDashboard_EBM_VanDeCuThe_Gia_20261018.html").write_text(json.dumps(items), encoding="utf-8")
    vd = types.SimpleNamespace(extract_data_block=lambda s: s, split_items=lambda b: json.loads(b),
                               field=lambda c, k: c.get(k))
    moi = dict(MOI)
    kcv = types.SimpleNamespace(tong_quan_moi_hon=lambda pm, nam, tu: moi[pm])
    monkeypatch.setattr(DC, "DASH", dash)
    monkeypatch.setattr(DC, "DA_XET", dash / "vuot-qua-da-xet.json")
    monkeypatch.setattr(DC, "_nap", lambda ten, duong: vd if ten == "_vd_dc" else kcv)
    monkeypatch.setattr(DC._bst_dccm_top, "duong_cong_cu_pipeline", lambda *a, **k: tmp_path / "vd.py")
    monkeypatch.setattr(DC, "_title_goc", lambda pms: {})
    monkeypatch.setattr(DC, "_tra_rut_bai", lambda pms: {})
    monkeypatch.setattr(DC.time, "sleep", lambda s: None)

    def khong_mang(*a, **k):
        raise OSError("ngoại tuyến")

    monkeypatch.setattr(DC.urllib.request, "urlopen", khong_mang)
    monkeypatch.setattr(sys, "argv", ["dat_canh_chung_cu_moi.py"])
    return dash, moi


def test_dau_cuoi_bo_muc_da_xet_va_bao_muc_khong_hoi_duoc(gia):
    dash, _ = gia
    (dash / "vuot-qua-da-xet.json").write_text(json.dumps(
        {"muc": {"111": {"pmid_moi_da_xet": ["900"], "ket_luan": "lac_chu_de"}}}), encoding="utf-8")
    assert DC.main() == 0
    bc = next((dash / "derivatives").glob("DAT-CANH-CHUNG-CU-MOI_*.md")).read_text(encoding="utf-8")
    assert "· 1 mục có tổng quan/guideline" in bc, "chỉ còn mục 222 (111 đã xét, 333 không hỏi được)"
    assert "1 mục khác có nguồn mới hơn nhưng bác sĩ ĐÃ XÉT HẾT" in bc
    assert "1 PMID KHÔNG hỏi được PubMed" in bc
    assert "Mục 222" in bc and "Mục 111" not in bc


def test_chua_co_so_thi_dem_nhu_cu(gia):
    dash, _ = gia
    assert DC.main() == 0
    bc = next((dash / "derivatives").glob("DAT-CANH-CHUNG-CU-MOI_*.md")).read_text(encoding="utf-8")
    assert "· 2 mục có tổng quan/guideline" in bc and "ĐÃ XÉT HẾT" not in bc


def test_khong_hoi_duoc_muc_nao_moi_tra_ma_2(gia):
    _, moi = gia
    for k in moi:
        moi[k] = None
    assert DC.main() == 2


def test_hoi_duoc_het_nhung_khong_co_bai_moi_khong_bi_bao_hong_mang(gia):
    _, moi = gia
    for k in moi:
        moi[k] = []
    assert DC.main() == 0, "PubMed đã trả lời đủ — «0 mục» không phải «không hỏi được»"


def _sang_loc(tmp_path):
    p = tmp_path / "sang-loc.json"
    p.write_text(json.dumps({"muc": [{"pmid": "111", "nhom": "L", "pmid_moi": ["900"]},
                                     {"pmid": "444", "nhom": "S", "pmid_moi": ["903"]},
                                     {"pmid": "222", "nhom": "A", "pmid_moi": ["901"]}]}), encoding="utf-8")
    return p


def test_ghi_chay_kho_khong_ghi_va_ghi_that_co_sao_luu(tmp_path):
    so = tmp_path / "vuot-qua-da-xet.json"
    sl = _sang_loc(tmp_path)
    assert G.main(["--sang-loc", str(sl), "--nhom", "L,S", "--loi", "đồng ý", "--so", str(so)]) == 0
    assert not so.exists(), "chạy khô không được ghi"
    assert G.main(["--sang-loc", str(sl), "--nhom", "L,S", "--loi", "đồng ý", "--so", str(so), "--ghi"]) == 0
    d = json.loads(so.read_text(encoding="utf-8"))
    assert set(d["muc"]) == {"111", "444"}, "nhóm A không bao giờ bị đóng hàng loạt"
    assert d["muc"]["111"]["ket_luan"] == "lac_chu_de" and d["muc"]["444"]["ket_luan"] == "chinh_nguon"
    assert d["muc"]["111"]["loi_bac_si"] == "đồng ý"
    assert G.main(["--pmid", "222", "--ket-luan", "da_so_giu", "--pmid-moi", "901", "--loi", "đã đọc, giữ",
                   "--so", str(so), "--ghi"]) == 0
    assert list(tmp_path.glob("vuot-qua-da-xet.json.bak-*")), "ghi đè sổ có sẵn phải sao lưu trước"
    assert DC.da_xet_het("222", MOI["222"], DC.doc_da_xet(so)) is True


def test_ghi_tu_choi_khi_thieu_loi_hoac_nhom_a_b(tmp_path):
    so = tmp_path / "vuot-qua-da-xet.json"
    sl = _sang_loc(tmp_path)
    assert G.main(["--sang-loc", str(sl), "--nhom", "L", "--so", str(so), "--ghi"]) == 2
    assert G.main(["--sang-loc", str(sl), "--nhom", "A", "--loi", "x", "--so", str(so), "--ghi"]) == 2
    assert not so.exists()


def test_so_hong_khong_bi_ghi_de(tmp_path):
    so = tmp_path / "vuot-qua-da-xet.json"
    so.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        G.main(["--pmid", "1", "--ket-luan", "lac_chu_de", "--pmid-moi", "2", "--loi", "x", "--so", str(so), "--ghi"])
    assert so.read_text(encoding="utf-8") == "[]"
