# -*- coding: utf-8 -*-
"""Kiểm cổng của `tom_tat_chung_cu_word.py` (19/10/2026): bản Word tóm tắt chứng cứ mà bác sĩ DỰA VÀO để thực hành không
được để lọt số không có trong bài, trích dẫn bịa, công cụ nguy cơ sai lệch sai thiết kế, hay làm mất PDF khi gắn vào EndNote."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

_sp = importlib.util.spec_from_file_location("_ttcc_test", Path(__file__).resolve().parent / "tom_tat_chung_cu_word.py")
T = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T)

TRANG = [
    "Trial of drug X versus placebo in heart failure. DOI: 10.1000/xyz123",
    "Patients were randomly assigned with concealed allocation. The study was double-blind.",
    "The primary outcome occurred in 914 patients (21.8%) and 1117 patients (26.5%) "
    "(hazard ratio, 0·80; 95% CI, 0.73 to 0.87; P<0.001). No patient had airway compromise or required mechanical air -\n"
    "way protection.",
    "Cough occurred in 474 (11.3) and 601 (14.3) patients, P<0.001. Enrolled 10,513 patients.",
]
NGU_CANH = {"ban_ghi": {"rec": 1, "pmid": "123", "doi": "10.1000/xyz123", "tieu_de": "Trial of drug X", "khoa": "PMID-123",
                        "nam": "2014", "tac_gia": "A", "tap_chi": "J"},
            "pdf": {"tep": "PMID-123.pdf", "sha256": "ab" * 32, "so_trang": 4},
            "rut_bai": {"trang_thai": "khong_thay_rut", "luc": "2026-10-19T00:00:00", "nguon": "pubmed"},
            "ngu_canh_dashboard": []}


def _dien(x):
    """Điền ô «…» của khuôn bằng chữ thật (cổng coi «…» là RỖNG — đúng ý: khuôn chưa điền không được ra Word)."""
    if isinstance(x, dict):
        return {k: _dien(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_dien(v) for v in x]
    return "nội dung thật" if x in ("…", "...") else x


def _hop_le() -> dict:
    tt = _dien(copy.deepcopy(T.MAU))
    tt.update({"khoa": "PMID-123", "pmid": "123", "doi": "10.1000/xyz123"})
    tt["ket_qua"] = [{"ket_cuc": "Kết cục chính", "chinh": True, "nhom_can_thiep": "914 (21.8%)",
                      "nhom_so_sanh": "1117 (26.5%)", "hieu_ung": "HR 0.80", "ktc95": "0.73–0.87", "p": "<0.001",
                      "tuyet_doi": "4.7 điểm %", "nnt": "", "may_tinh": ["tuyet_doi"], "trang": 3}]
    tt["tac_hai"] = [{"ket_cuc": "Ho", "chinh": False, "nhom_can_thiep": "474 (11.3%)", "nhom_so_sanh": "601 (14.3%)",
                      "hieu_ung": "", "ktc95": "", "p": "<0.001", "tuyet_doi": "", "nnt": "", "may_tinh": [], "trang": 4}]
    tt["trich_nguyen_van"] = [{"cau": "No patient had airway compromise or required mechanical airway protection.",
                               "trang": 3}]
    tt["ket_luan_thuc_hanh"] = ["Kết luận một.", "Kết luận hai."]
    return tt


def test_hop_le_dat():
    assert T.kiem_tom_tat(_hop_le(), TRANG, NGU_CANH) == []


def test_khuon_chua_dien_bi_chan():
    tt = copy.deepcopy(T.MAU)
    tt.update({"khoa": "PMID-123", "pmid": "123"})
    assert any("goi_y_ap_dung" in x or "rỗng" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_so_khong_co_tren_trang_bi_chan():
    tt = _hop_le()
    tt["ket_qua"][0]["hieu_ung"] = "HR 0.78"
    loi = T.kiem_tom_tat(tt, TRANG, NGU_CANH)
    assert any("0.78" in x for x in loi)


def test_so_dung_nhung_sai_trang_bi_chan():
    tt = _hop_le()
    tt["tac_hai"][0]["trang"] = 1  # số 474 nằm ở trang 4, không ở trang 1±1
    assert any("474" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_so_may_tinh_phai_khai_moi_duoc_bo_qua():
    tt = _hop_le()
    tt["ket_qua"][0]["may_tinh"] = []  # 4.7 không có trong bài ⇒ phải bị bắt
    assert any("4.7" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_trich_qua_15_tu_bi_chan():
    tt = _hop_le()
    tt["trich_nguyen_van"][0]["cau"] = " ".join(["word"] * 16)
    assert any("tối đa" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_trich_khong_co_trong_bai_bi_chan():
    tt = _hop_le()
    tt["trich_nguyen_van"][0]["cau"] = "The drug cured every patient completely"
    assert any("không tìm thấy" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_rob2_cho_thuan_tap_bi_chan():
    tt = _hop_le()
    tt["loai_thiet_ke"] = "cohort"
    loi = T.kiem_tom_tat(tt, TRANG, NGU_CANH)
    assert any("RoB 2 chỉ dùng cho RCT" in x for x in loi)


def test_robins_cho_rct_bi_chan():
    tt = _hop_le()
    tt["nguy_co_sai_lech"]["cong_cu"] = "ROBINS-I"
    assert any("không đúng thiết kế rct" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_muc_grade_la_bi_chan():
    tt = _hop_le()
    tt["grade_de_xuat"][0]["muc"] = "rất cao"
    assert any("grade_de_xuat" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_pmid_lech_ban_ghi_bi_chan():
    tt = _hop_le()
    tt["pmid"] = "999"
    assert any("pmid" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_guideline_phai_co_khuyen_cao():
    tt = _hop_le()
    tt["loai_thiet_ke"] = "guideline"
    tt["nguy_co_sai_lech"]["cong_cu"] = "AGREE II"
    tt["khuyen_cao"] = []
    assert any("khuyen_cao" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_chuan_so_hai_cach_viet():
    assert T.cac_so("0·70") == ["0.70"]
    assert "10513" in T.cac_so("10,513 patients")
    assert T._so_khop("0.8", {"0.80"}) and not T._so_khop("8", {"80"})
    assert not T._so_khop("8", {"8.0"})  # số nguyên phải trùng nguyên văn, không so theo giá trị


def _chu_word(doc) -> tuple[str, str]:
    """(thân văn bản, mục Lưu ý cuối) — tách tại đoạn tiêu đề «Lưu ý»."""
    doan = ["".join(t.text or "" for t in p.iter() if t.tag.endswith("}t"))
            for p in doc.element.body.iter() if p.tag.endswith("}p")]
    i = doan.index("Lưu ý")
    return "\n".join(doan[:i]), "\n".join(doan[i:])


def test_word_11_muc_co_mau_va_luu_y_o_cuoi():
    tt = _hop_le()
    tt["ket_luan_thuc_hanh"][0] = "[!Không dùng!] cho người [+có lợi+] **đậm**."
    tt["can_xac_nhan"] = ["BHYT tại đơn vị."]
    doc = T.dung_word(tt, NGU_CANH)
    muc = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
    assert len(muc) == 11 and not any(k in " ".join(muc) for k in ("Đối chiếu", "Trích nguyên văn", "Câu hỏi còn mở"))
    xml = doc.element.xml
    assert 'w:val="C00000"' in xml and 'w:val="1E7B34"' in xml  # đỏ cảnh báo · xanh lá lợi ích
    assert 'w:fill="E2F0D9"' in xml  # nền xanh lá: điểm nhấn / kết cục chính
    assert "4.7 điểm % †" in xml
    than, cuoi = _chu_word(doc)
    assert not T.CUM_CAM_THAN_BAI.search(than) and "đề xuất" not in than.lower()
    assert "CẦN BÁC SĨ KIỂM CHỨNG" in cuoi and "do máy đánh giá" in cuoi and "BHYT tại đơn vị." in cuoi


def test_cum_cam_trong_than_bi_chan():
    for truong, gt in (("kha_nang_ap_dung", {"tuong_dong": "a", "khac_biet": "b", "trien_khai_viet_nam": "BHYT [CẦN XÁC NHẬN]"}),
                       ("han_che", ["Mức này là đề xuất của máy"]),
                       ("diem_manh", ["Kết luận cần bác sĩ kiểm chứng"])):
        tt = _hop_le()
        tt[truong] = gt
        assert any("thân văn bản chứa" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH)), truong


def test_cum_cho_phep_o_can_xac_nhan():
    tt = _hop_le()
    tt["can_xac_nhan"] = ["Cần xác nhận BHYT; cần bác sĩ kiểm chứng."]
    assert T.kiem_tom_tat(tt, TRANG, NGU_CANH) == []


def test_so_tu_cong_o_truong_chu_bi_chan():
    tt = _hop_le()
    tt["diem_manh"] = ["Cỡ mẫu lớn, 2031 biến cố chính"]  # 914 + 1117 — máy tự cộng, bài không ghi
    assert any("2031" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_so_ngoai_bai_duoc_mien_khi_ghi_nguon():
    tt = _hop_le()
    tt["goi_y_ap_dung"]["khong_nen"] = ["Ngừng ACEi ≥ 36 giờ [ngoài bài: nhãn thuốc]"]
    assert T.kiem_tom_tat(tt, TRANG, NGU_CANH) == []
    tt["goi_y_ap_dung"]["khong_nen"] = ["Ngừng ACEi ≥ 36 giờ"]
    assert any("36" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_diem_nhan_thieu_bi_chan():
    tt = _hop_le()
    tt["diem_nhan"]["grade"] = ""
    assert any("diem_nhan.grade" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))


def test_dau_cach_thuong_khong_gop_so_bang_pdf():
    assert T.cac_so("122±15 121±15") == ["122", "15", "121", "15"]
    assert "696100" not in T.cac_so("LCZ696 100 mg")
    assert T.cac_so("08/12/2009") == ["8", "12", "2009"]


def test_huong_dan_day_moi_truong_so_va_luat_cong():
    hd = T.huong_dan_doc()
    for k in T.TRUONG_SO + T.KHOA_DIEM_NHAN + ("may_tinh", "can_xac_nhan", "danh_gia", "[ngoài bài", "RoB 2", "AMSTAR-2",
                                              "ROBINS-I", "QUADAS", "AGREE II"):
        assert k in hd, k


def test_khop_dinh_danh():
    assert T.khop_dinh_danh(TRANG, "10.1000/xyz123", "")[0]
    assert not T.khop_dinh_danh(TRANG, "10.9999/khac", "Completely unrelated cardiology paper title words")[0]


class _EnGia:
    def __init__(self, cu: str, mat_tep_cu: bool = False):
        self.gia_tri = cu
        self.mat = mat_tep_cu
        self.ghi: list[str] = []

    def so_csdl(self):
        return "1"

    def doc_truong(self, ids, truong):
        return {ids[0]: self.gia_tri}

    def _truoc_khi_ghi(self, ly_do):
        pass

    def _chay(self, than, ma, gt):
        self.ghi.append(gt)
        self.gia_tri = gt.split("\r")[-1] if self.mat else gt
        return self.gia_tri


def test_gan_endnote_chay_kho_khong_ghi(tmp_path):
    en = _EnGia("internal-pdf://1/a.pdf")
    tep = tmp_path / "PMID-123_TomTatChungCu.docx"
    tep.write_bytes(b"x")
    assert T.gan_vao_endnote(tmp_path, {"rec": 5}, tep, ap_dung=False, endnote=en) == 0
    assert en.ghi == []


def test_gan_endnote_giu_pdf_cu(tmp_path):
    en = _EnGia("internal-pdf://1/a.pdf")
    tep = tmp_path / "PMID-123_TomTatChungCu.docx"
    tep.write_bytes(b"x")
    assert T.gan_vao_endnote(tmp_path, {"rec": 5}, tep, ap_dung=True, endnote=en) == 0
    assert en.gia_tri.startswith("internal-pdf://1/a.pdf\r") and tep.name in en.gia_tri


def test_gan_endnote_mat_tep_cu_thi_ghi_tra(tmp_path):
    en = _EnGia("internal-pdf://1/a.pdf", mat_tep_cu=True)
    tep = tmp_path / "PMID-123_TomTatChungCu.docx"
    tep.write_bytes(b"x")
    assert T.gan_vao_endnote(tmp_path, {"rec": 5}, tep, ap_dung=True, endnote=en) == 1
    assert en.ghi[-1] == "internal-pdf://1/a.pdf"


def test_gan_endnote_khong_doc_duoc_tep_cu_thi_khong_ghi(tmp_path):
    en = _EnGia("")
    tep = tmp_path / "x.docx"
    tep.write_bytes(b"x")
    assert T.gan_vao_endnote(tmp_path, {"rec": 5}, tep, ap_dung=True, endnote=en) == 2
    assert en.ghi == []


def test_khong_co_lenh_xoa_ban_ghi():
    nguon = (Path(__file__).resolve().parent / "tom_tat_chung_cu_word.py").read_text(encoding="utf-8")
    assert "delete record" not in nguon


@pytest.mark.parametrize("trang_thai,ma", [("da_rut", 3)])
def test_bai_da_rut_bi_chan_khi_dung(tmp_path, monkeypatch, trang_thai, ma):
    goi = tmp_path / "cache" / "PMID-123"
    goi.mkdir(parents=True)
    (goi / "van_ban.txt").write_text(T.ghep_van_ban(TRANG), encoding="utf-8")
    import json
    nc = dict(NGU_CANH, dinh_danh={"khop": True, "ly_do": "DOI"})
    (goi / "ngu_canh.json").write_text(json.dumps(nc, ensure_ascii=False), encoding="utf-8")
    (goi / "tom_tat.json").write_text(json.dumps(_hop_le(), ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(T, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(T, "tim_ban_ghi", lambda tv, ma_: {"rec": 1, "pmid": "123", "doi": "10.1000/xyz123",
                                                            "khoa": "PMID-123"})
    rb = lambda p, d: {"trang_thai": trang_thai, "luc": "x", "nguon": "test"}  # noqa: E731
    assert T.dung(tmp_path / "lib.enl", "123", rut_bai=rb) == ma
    assert not (tmp_path / T.TEN_THU_MUC_RA).exists()
