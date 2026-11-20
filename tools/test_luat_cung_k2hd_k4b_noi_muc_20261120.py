"""Luật cứng mới cho hai lớp đột biến luật cứng từng bắt 0–7% (do_nhay_api 20/11/2026) — ngoại tuyến, không gọi API.

  · K2 ngưỡng trong HÀNH ĐỘNG (`k2_nguong_hd`): ngưỡng EF/eGFR/tuổi/HbA1c/BMI/LDL nằm trong `action` được đối chiếu với nguồn
    bằng CÙNG phép của K1a (trước đây K1/K2 không đọc action ⇒ lớp «K2-hđ» lọt 100%).
  · K4b NỘI MỤC (`k4b_noi_muc`): hành động mở đầu «KHÔNG/Tránh…» trong khi tiêu đề + gradeSource + effectText của CHÍNH mục không
    có dấu phủ định/chống/hại nào ⇒ 🟠, kể cả khi nguồn có câu chống rộng.
Văn bản nguồn là tóm tắt TỰ DỰNG theo khuôn efetch dạng text (không trích nguyên văn bài báo nào). Mọi phép vẫn ở mức CẢNH BÁO.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_THU_MUC = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, _THU_MUC / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


Q = _nap("kiem_quan_the_chieu_k2hd", "kiem_quan_the_chieu.py")
DN = _nap("do_nhay_kiem_ngu_nghia_k2hd", "do_nhay_kiem_ngu_nghia.py")


def _efetch(tieu_de: str, than: str) -> str:
    return (f"1. Fake J Med. 2026 Jan;1(1):10-20. doi: 10.0000/fake.\n\n{tieu_de}\n\nAuthor A(1), Author B(1).\n\n"
            f"Author information:\n(1)Department of Medicine, Example University Hospital.\n\n{than}\n\n"
            "Copyright © 2026 Example.\n\nDOI: 10.0000/fake\nPMID: 900002")


SRC_EGFR = _efetch("Drug Z in chronic kidney disease.",
                   "METHODS: Adults with an eGFR of 25 to 75 ml/min/1.73 m2 were randomized.\n"
                   "CONCLUSIONS: Drug Z reduced the risk of kidney failure.")
SRC_CHONG = _efetch("Drug W in heart failure.",
                    "METHODS: Adults were randomized.\nCONCLUSIONS: Drug W reduced hospitalization; it should be avoided "
                    "in patients with hyperkalemia.")


def _muc(action: str, *, title: str = "Thuốc Z ở bệnh thận mạn", population: str = "Bệnh thận mạn",
         gradeSource: str | None = "KDIGO 2024: COR 1, khuyến cáo mạnh", effectText: str | None = "Giảm 30% suy thận",
         normativeBasis: str | None = None) -> dict:
    it = {"id": "ITEM-T", "decision": "apply", "title": title, "population": population, "action": action, "pmid": "1"}
    for k, v in (("gradeSource", gradeSource), ("effectText", effectText), ("normativeBasis", normativeBasis)):
        if v is not None:
            it[k] = v
    return it


# ───────────────────────── K2 ngưỡng trong HÀNH ĐỘNG ─────────────────────────

def test_k2hd_nguong_hanh_dong_lech_nguon_la_can_doc_khop_la_khop():
    r = Q.kiem_muc(_muc("Khởi trị thuốc Z khi eGFR ≥ 45 ml/phút."), SRC_EGFR)
    assert [(x["chi_so"], x["so"], x["muc"]) for x in r["k2_nguong_hd"]] == [("egfr", "45", "can_doc")]
    assert "egfr" in r["k2_nguong_hd"][0]["doan_nguon"]
    r2 = Q.kiem_muc(_muc("Khởi trị thuốc Z khi eGFR ≥ 25 ml/phút."), SRC_EGFR)
    assert [(x["so"], x["muc"]) for x in r2["k2_nguong_hd"]] == [("25", "khop")]
    # nguồn không nhắc chỉ số ⇒ ⚪, không bao giờ 🟠
    r3 = Q.kiem_muc(_muc("Dùng statin khi LDL-C ≥ 70 mg/dL."), SRC_EGFR)
    assert [(x["chi_so"], x["muc"]) for x in r3["k2_nguong_hd"]] == [("ldl", "chua_kiem")]


def test_k2hd_khong_bao_trung_nguong_da_co_o_quan_the():
    it = _muc("Khởi trị thuốc Z khi eGFR ≥ 45.", population="Bệnh thận mạn eGFR ≥ 45")
    r = Q.kiem_muc(it, SRC_EGFR)
    assert [(x["so"], x["muc"]) for x in r["k1_nguong"]] == [("45", "can_doc")]   # K1 đã phán ngưỡng của quần thể
    assert r["k2_nguong_hd"] == []                                                # hành động lặp lại ⇒ không báo trùng


def test_k2hd_dem_vao_phep_k2_va_ma_thoat_dashboard():
    r = Q.kiem_muc(_muc("Khởi trị thuốc Z khi eGFR ≥ 45."), SRC_EGFR)
    assert r["k2_nguong_hd"][0] in Q.phan_quyet_theo_phep(r)["K2"]
    data = {"items": [{**_muc("Khởi trị thuốc Z khi eGFR ≥ 45."), "pmid": "1"}]}
    kq = Q.kiem_dashboard(data, {"1": SRC_EGFR}, False)
    assert kq["dem_theo_phep"]["K2"]["can_doc"] == 1
    assert sum(v["can_doc"] for v in kq["dem_theo_phep"].values()) == kq["dem"]["can_doc"]


def test_k2hd_khong_nguon_khong_phan():
    assert Q.kiem_muc(_muc("Khởi trị thuốc Z khi eGFR ≥ 45."), None)["k2_nguong_hd"] == []


# ───────────────────────── K4b NỘI MỤC ─────────────────────────

def test_k4b_noi_muc_hanh_dong_phu_dinh_trong_muc_khang_dinh():
    it = _muc("KHÔNG khởi trị thuốc Z ở bệnh thận mạn.")
    assert Q.k4b_noi_muc(it) == {"tieu_de": "thuốc z ở bệnh thận mạn"}
    r = Q.kiem_k4b(it, Q.chuan_hoa_nguon(Q.than_nguon(SRC_EGFR)))
    assert r["muc"] == "can_doc" and r["muc_nguon"] == "can_doc" and r["noi_muc"]["tieu_de"]


def test_k4b_noi_muc_bao_ca_khi_nguon_co_cau_chong_rong():
    """Nguồn có câu chống rộng («should be avoided in patients with hyperkalemia») ⇒ phép đối chiếu nguồn coi là cùng chiều
    (✓); nhưng tiêu đề + phân hạng của CHÍNH mục nói «nên làm» ⇒ 🟠 nội mục, giữ phán quyết nguồn ở muc_nguon."""
    it = _muc("Tránh thuốc W ở suy tim.", title="Thuốc W giảm nhập viện suy tim",
              gradeSource="ESC 2026: Class I, A", effectText="HR 0,75 (0,65–0,86)")
    ng = Q.chuan_hoa_nguon(Q.than_nguon(SRC_CHONG))
    r = Q.kiem_k4b(it, ng)
    assert r["muc"] == "can_doc" and r["muc_nguon"] == "khop" and r["cau_nguon"]
    # cùng mục nhưng không có trường đối chiếu ⇒ hành vi cũ nguyên vẹn
    r0 = Q.kiem_k4b(_muc("Tránh thuốc W ở suy tim.", gradeSource=None, effectText=None), ng)
    assert r0 == {"muc": "khop", "cau_nguon": r["cau_nguon"]}


def test_k4b_noi_muc_khong_bao_khi_muc_tu_mang_chieu_chong():
    act = "KHÔNG tầm soát thường quy."
    for kw in ({"title": "KHÔNG tầm soát hẹp động mạch cảnh"},                       # tiêu đề phủ định
               {"title": "USPSTF — khuyến cáo MẠNH CHỐNG glucosamine"},                # «khuyến cáo … chống»
               {"title": "Vắc xin X — giấy phép bị rút sau rà soát an toàn"},          # thu hồi
               {"title": "Tầm soát PSA", "gradeSource": "USPSTF 2018: mức D"},         # phân hạng chống
               {"title": "Thuốc X", "gradeSource": "COR 3: Harm"},
               {"title": "Thuốc X", "effectText": "tăng nguy cơ chảy máu HR 1,6"},
               {"title": "Thuốc X", "normativeBasis": "contraindication"},
               {"title": "Thuốc X", "gradeSource": None, "effectText": None},         # thiếu trường đối chiếu
               {"title": ""}):                                                          # tiêu đề trống
        assert Q.k4b_noi_muc(_muc(act, **kw)) is None, kw
    # hành động KHÔNG phủ định / phủ định kép ⇒ không phải khuyến cáo «KHÔNG làm»
    assert Q.k4b_noi_muc(_muc("Khởi trị thuốc Z.")) is None
    assert Q.k4b_noi_muc(_muc("KHÔNG từ chối thuốc Z chỉ vì eGFR thấp.")) is None


def test_k4b_noi_muc_khong_mo_ta_quan_the_khong_chan():
    """«không triệu chứng», «không dung nạp» trong tiêu đề là mô tả QUẦN THỂ, không phải khuyến cáo chống."""
    for tieu_de in ("Statin cho người KHÔNG triệu chứng nguy cơ cao", "Thuốc thay thế khi không dung nạp ƯCMC"):
        assert Q.k4b_noi_muc(_muc("KHÔNG kê statin.", title=tieu_de)) is not None, tieu_de
    assert Q.k4b_noi_muc(_muc("KHÔNG kê statin.", title="Statin: không dùng ở phụ nữ có thai")) is None


def test_k4b_noi_muc_in_bao_cao(capsys):
    data = {"items": [_muc("KHÔNG khởi trị thuốc Z ở bệnh thận mạn.")]}
    Q.in_bao_cao("t", Q.kiem_dashboard(data, {"1": SRC_EGFR}, False))
    ra = capsys.readouterr().out
    assert "K4b hành động nói KHÔNG làm nhưng tiêu đề" in ra and "«thuốc z ở bệnh thận mạn»" in ra
    assert "K4b mục nói KHÔNG làm, nguồn có câu ủng hộ" in ra                       # phán quyết nguồn vẫn in


# ───────────────────────── bộ đo độ nhạy: chấm đúng trường mới ─────────────────────────

def test_do_nhay_cham_k2hd_tai_truong_moi():
    bo = DN.bo_kiem_that()
    goc_it = _muc("Khởi trị thuốc Z khi eGFR ≥ 25.")
    db = {"lop": "K2_nguong_hanh_dong", "phep": "K2", "truong": "k2_nguong_hd", "trong_pham_vi": True,
          "dich": {"chi_so": "egfr", "so": "45"}, "muc_dot_bien": _muc("Khởi trị thuốc Z khi eGFR ≥ 45."),
          "nguon_dot_bien": SRC_EGFR}
    goc = bo["kiem_muc"](goc_it, SRC_EGFR)
    assert DN.cham_k124(db, goc, bo) == "bat"
    assert "nguong_hd:egfr:45" in DN.chu_ky_bao(bo["kiem_muc"](db["muc_dot_bien"], SRC_EGFR), "K2")
    assert DN.cham_k124({**db, "muc_dot_bien": goc_it, "dich": {"chi_so": "egfr", "so": "25"}}, goc, bo) == "lot_xanh"
    assert "k2_nguong_hd" in DN.TRUONG_CUA_PHEP["K2"]


def test_do_nhay_cham_k4b_noi_muc_khi_nguon_co_cau_chong():
    bo = DN.bo_kiem_that()
    goc_it = _muc("Dùng thuốc W ở suy tim.", title="Thuốc W giảm nhập viện suy tim", gradeSource="Class I, A")
    db = {"phep": "K4b", "truong": "k4b", "dich": {}, "nguon_dot_bien": SRC_CHONG,
          "muc_dot_bien": {**goc_it, "action": "KHÔNG dùng thuốc W ở suy tim."}}
    assert DN.cham_k124(db, bo["kiem_muc"](goc_it, SRC_CHONG), bo) == "bat" and db["phan_duoc"] is True
