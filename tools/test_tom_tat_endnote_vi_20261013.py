# -*- coding: utf-8 -*-
"""Tóm tắt thực hành tiếng Việt trong trường Abstract của EndNote (13/10/2026) — `tom_tat_endnote_vi.py`.

Bác sĩ: «trong phần edit của trích dẫn với mục Abstract hãy ghi nội dung tiếng Việt tóm tắt trích dẫn đó cho thực hành
lâm sàng». Ngoại tuyến hoàn toàn: dashboard là dict giả, EndNote là đối tượng giả, sao lưu là hàm giả.
"""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_vi")
N = _nap("tools/nap_endnote_chu_de.py", "_nap_tt_vi")

MUC = {"id": "ITEM-01", "title": "Colchicine dự phòng thứ phát — chưa đủ dùng thường quy", "source": "CONVINCE · Lancet 2024",
       "design": "RCT", "org": "", "dateVersion": "2024", "pmid": "31111111", "doi": "10.1016/aaa",
       "population": "Đột quỵ không do tim", "pico": {"P": ["Đột quỵ", "match"], "I": ["Colchicine", "match"],
                                                       "C": "Chuẩn", "O": ["Tái phát", "match"]},
       "effectText": "Kết quả chính không đạt ý nghĩa", "effect": {"measure": "HR", "hr": 0.84, "ci": "0.68–1.05"},
       "gradeLevel": "mod", "gradeBy": "", "gradeSource": "RCT dừng sớm", "decision": "notyet",
       "action": "CHƯA thêm colchicine thường quy", "monitoring": "—", "vn": "Không khởi trị ngoài nghiên cứu",
       "flag": "Âm tính ở phân tích chính", "safety": "",
       "references": ["Kelly P. Lancet 2024. PMID 31111111. doi:10.1016/aaa", "Phụ lục: Smith J. Stroke 2020. PMID 32222222",
                      "Bản chỉ có DOI: doi:10.1093/bbb"]}


def _doc(bang: dict):
    return lambda p: bang.get(Path(p).name)


def _dash(ten: str, items: list[dict], cau_hoi: str = "Đột quỵ") -> tuple[Path, dict]:
    return Path(f"/khong-ton-tai/{ten}"), {"meta": {"question": cau_hoi}, "items": items}


def test_khoi_doc_nhanh_dong_dau_diem_nhan_va_truong_nguyen_ven(tmp_path):
    f, d = _dash("WebDashboard_X_20260614.html", [MUC])
    ds = tt.ngu_canh([f], _doc({f.name: d}))
    k = tt.khoi_tieng_viet(ds["pmid:31111111"], tmp_path)
    dong = k.splitlines()
    assert dong[0] == f"{tt.MO_DAU} Chưa đủ thay đổi · Chứng cứ: Trung bình · RCT 2024"
    assert dong[1] == "★ Colchicine dự phòng thứ phát — chưa đủ dùng thường quy"
    for chu in ("▸ Kết quả: Kết quả chính không đạt ý nghĩa; HR 0.84 (KTC 95% 0.68–1.05)",
                "▸ Thực hành: CHƯA thêm colchicine thường quy", "▸ Lưu ý: Âm tính ở phân tích chính",
                "▸ Tại Việt Nam: Không khởi trị ngoài nghiên cứu", "Chủ đề: Đột quỵ · 14/06/2026",
                "PMID 31111111 · Toàn văn: CHƯA có", "Cần bác sĩ kiểm chứng"):
        assert chu in k, chu
    for bo in ("Theo dõi", "Quần thể", "RCT dừng sớm"):
        assert bo not in k, f"bản đọc nhanh không in {bo}"
    assert dong[2:6] == ["   P · Đối tượng: Đột quỵ", "   I · Can thiệp/phơi nhiễm: Colchicine",
                         "   C · So sánh: Chuẩn", "   O · Kết cục: Tái phát"], "PICO ngay dưới dòng ★"
    assert len(k) < 1000


def test_pico_nhan_lech_cau_hoi_va_p_lay_quan_the_khi_thieu(tmp_path):
    f, d = _dash("WebDashboard_X_20260614.html",
                 [dict(MUC, pico={"I": ["Colchicine", "mis"], "C": ["Chuẩn", "partial"], "O": ["Tái phát", "match"]})])
    k = tt.khoi_tieng_viet(tt.ngu_canh([f], _doc({f.name: d}))["pmid:31111111"], tmp_path)
    assert "   P · Đối tượng: Đột quỵ không do tim" in k, "thiếu P ⇒ dùng trường quần thể"
    assert "   I · Can thiệp/phơi nhiễm: Colchicine ⚠ lệch câu hỏi của chủ đề" in k
    assert "   C · So sánh: Chuẩn (khớp một phần)" in k and "Tái phát (" not in k


ANH = dict(MUC, id="I2", pmid="34444444", doi=None, references=[], title="Colchicine liều thấp sau nhồi máu não",
           decision="apply", gradeLevel="high", effect={"measure": "HR", "hr": 0.7, "ci": "0.5–0.9"},
           pico={"I": ["Colchicine liều thấp", "match"], "C": ["Giả dược", "match"], "O": ["Đột quỵ tái phát", "match"]})


def test_dat_canh_cung_cau_hoi_kem_khuyen_nghi_va_so_do(tmp_path):
    kdcc = ["Không dùng công cụ / nhóm so sánh", "match"]  # đúng ca ghép nhầm thật 13/10 (thang điểm ↔ vắc-xin RSV)
    goc = dict(MUC, pico={"I": ["Colchicine 0,5 mg tối đa", "match"], "C": kdcc,
                          "O": ["Đột quỵ tái phát", "match"]})
    chi_c = dict(ANH, id="I3", pmid="35555555", title="Vắc-xin cúm", pico={"I": ["Vắc-xin cúm", "match"], "C": kdcc,
                                                                           "O": ["Nhập viện", "match"]})
    don_vi = dict(ANH, id="I4", pmid="36666666", title="Semaglutide", pico={"I": ["Semaglutide 1 mg dưới da", "match"],
                                                                            "C": ["Chuẩn", "match"], "O": ["Đột quỵ tái phát", "match"]})
    khac_o = dict(ANH, id="I5", pmid="37777777", title="Colchicine và gout", pico={"I": ["Colchicine", "match"],
                                                                                  "O": ["Cơn gout cấp", "match"]})
    f, d = _dash("WebDashboard_X_20260614.html", [goc, ANH, chi_c, don_vi, khac_o])
    k = tt.khoi_tieng_viet(tt.ngu_canh([f], _doc({f.name: d}))["pmid:31111111"], tmp_path)
    assert "▸ Đặt cạnh trong chủ đề (máy ghép theo PICO — chỉ đặt cạnh, không phán chiều):" in k
    assert ("   – Colchicine liều thấp sau nhồi máu não [PMID 34444444 · Áp dụng ngay · chứng cứ: Cao · "
            "HR 0.7 (KTC 95% 0.5–0.9)]") in k
    assert "Vắc-xin cúm" not in k, "chỉ trùng nhóm so sánh (C) không phải cùng câu hỏi"
    assert "Semaglutide" not in k, "chỉ trùng đơn vị liều/đường dùng («mg», «tối đa»/«dưới da») không phải cùng câu hỏi"
    assert "Colchicine và gout [" in k and "— kết cục khác: Cơn gout cấp" in k, "cùng can thiệp, khác kết cục ⇒ nói rõ"


def test_dat_canh_bo_o_giu_cho_va_gom_tu_chu_de_khac(tmp_path):
    gc = {"I": ["(không nêu rõ trong abstract)", "na"], "O": ["(không nêu rõ trong abstract)", "na"]}
    f, d = _dash("WebDashboard_X_20260614.html", [dict(MUC, pico=gc), dict(ANH, pico=gc)])
    k = tt.khoi_tieng_viet(tt.ngu_canh([f], _doc({f.name: d}))["pmid:31111111"], tmp_path)
    assert "Đặt cạnh" not in k, "hai ô giữ chỗ giống nhau không phải «cùng câu hỏi»"
    a, da = _dash("WebDashboard_A_20260901.html", [dict(MUC, pico=ANH["pico"])], "Chủ đề A")
    b, db = _dash("WebDashboard_B_20260601.html", [dict(MUC, pico=ANH["pico"]), ANH], "Chủ đề B")
    k2 = tt.khoi_tieng_viet(tt.ngu_canh([a, b], _doc({a.name: da, b.name: db}))["pmid:31111111"], tmp_path)
    assert "PMID 34444444" in k2, "bài cùng câu hỏi chỉ có ở dashboard khác vẫn được đặt cạnh"


def test_rut_gon_bang_chon_truong_khong_cat_giua_cau(tmp_path):
    dai = "Hiệu quả " + "rất " * 120 + "rõ"
    hd = "Dùng thuốc X " + "thận trọng " * 70 + "NẾU KHÔNG CHỐNG CHỈ ĐỊNH"
    f, d = _dash("WebDashboard_X_20260614.html", [dict(MUC, effectText=dai, action=hd, vn="V" * 400)])
    k = tt.khoi_tieng_viet(tt.ngu_canh([f], _doc({f.name: d}))["pmid:31111111"], tmp_path)
    assert "Hiệu quả" not in k and "▸ Kết quả: HR 0.84 (KTC 95% 0.68–1.05)" in k, "kết quả dài bỏ CẢ trường, giữ số đo"
    assert f"▸ Thực hành: {tt._gon(hd)}" in k, "«Thực hành» luôn in nguyên vẹn — giữ mệnh đề điều kiện cuối câu"
    assert "Tại Việt Nam" not in k, "trường áp dụng VN quá trần bị bỏ cả trường, không cắt"


@pytest.mark.parametrize("gl, qd, can", [("na", "apply", ["Chứng cứ: nguồn không phân hạng (≠ chứng cứ yếu)",
                                                            "Áp dụng ngay"]),
                                         ("high", "consider", ["Chứng cứ: Cao", "Cân nhắc chọn lọc"]),
                                         ("la", "xyz", ["chưa rõ («la»)", "chưa rõ («xyz»)"])])
def test_nhan_grade_va_quyet_dinh_khong_doan(tmp_path, gl, qd, can):
    f, d = _dash("WebDashboard_X_20260614.html", [dict(MUC, gradeLevel=gl, decision=qd)])
    k = tt.khoi_tieng_viet(tt.ngu_canh([f], _doc({f.name: d}))["pmid:31111111"], tmp_path)
    for c in can:
        assert c in k, c
    if qd == "xyz":
        assert "Cân nhắc chọn lọc" not in k, "giá trị lạ không được hiển thị như một khuyến nghị có thật"


def test_tai_lieu_tham_khao_khong_bi_gan_ket_qua_cua_nguon_chinh(tmp_path):
    f, d = _dash("WebDashboard_X_20260614.html", [MUC])
    ds = tt.ngu_canh([f], _doc({f.name: d}))
    k = tt.khoi_tieng_viet(ds["pmid:32222222"], tmp_path)
    assert k.startswith(f"{tt.MO_DAU} Tài liệu tham khảo bổ trợ") and "nguồn chính PMID 31111111" in k
    for chu in ("HR 0.84", "CHƯA thêm colchicine", "Không khởi trị", "Chứng cứ:", "Thực hành:", "P · Đối tượng",
                "Đặt cạnh"):
        assert chu not in k, f"kết quả/khuyến nghị của nguồn chính bị gán cho bài tham khảo: {chu}"
    assert "doi:10.1093/bbb" in ds, "trích dẫn chỉ có DOI vẫn có ngữ cảnh"
    assert len([n for n in ds["pmid:31111111"]["ngu_canh"] if n["vai"] == "tham_khao"]) == 0, \
        "tham khảo trỏ lại chính nguồn của mục không thành ngữ cảnh thứ hai"


def test_phien_ban_moi_thang_ban_cu_chi_bo_sung_trich_dan_da_bi_bo(tmp_path):
    cu, d_cu = _dash("WebDashboard_X_20260101.html", [dict(MUC, action="Lời CŨ"), dict(MUC, id="I2", pmid="33333333",
                                                                                       doi=None, references=[])])
    moi, d_moi = _dash("WebDashboard_X_20260614.html", [dict(MUC, action="Lời MỚI")])
    ds = tt.ngu_canh([cu, moi], _doc({cu.name: d_cu, moi.name: d_moi}))
    k111 = tt.khoi_tieng_viet(ds["pmid:31111111"], tmp_path)
    assert "Lời MỚI" in k111 and "Lời CŨ" not in k111, "cùng chủ đề: chỉ chép bản mới nhất"
    k333 = tt.khoi_tieng_viet(ds["pmid:33333333"], tmp_path)
    assert "bản dashboard CŨ" in k333, "bài chỉ còn ở bản cũ vẫn có tóm tắt, ghi rõ là bản cũ"


def test_nhieu_chu_de_khuyen_nghi_lech_thi_canh_bao(tmp_path):
    a, da = _dash("WebDashboard_A_20260901.html", [dict(MUC, decision="apply", action="Làm A")], "Suy tim: tổng hợp")
    b, db = _dash("WebDashboard_B_20260601.html", [dict(MUC, decision="notyet", action="Làm B")], "Tiên lượng suy tim")
    k = tt.khoi_tieng_viet(tt.ngu_canh([a, b], _doc({a.name: da, b.name: db}))["pmid:31111111"], tmp_path)
    assert "Làm A" in k and "Làm B" not in k, "ngữ cảnh chính = dashboard MỚI NHẤT, chủ đề khác chỉ nêu tên"
    assert "⚠ Khuyến nghị KHÁC nhau giữa các chủ đề — Suy tim: Áp dụng ngay; Tiên lượng suy tim: Chưa đủ thay đổi" in k
    b2, db2 = _dash("WebDashboard_B_20260601.html", [dict(MUC, decision="apply")], "Tiên lượng suy tim")
    k2 = tt.khoi_tieng_viet(tt.ngu_canh([a, b2], _doc({a.name: da, b2.name: db2}))["pmid:31111111"], tmp_path)
    assert "⚠" not in k2 and "▸ Cũng dùng trong: Tiên lượng suy tim" in k2


def test_chay_lai_nhan_ra_khoi_dang_cu_va_thay_khong_long(tmp_path):
    goc = "Background: original English abstract."
    cu = f"【TÓM TẮT THỰC HÀNH · tiếng Việt】\nPMID 1\n• Mục: dài dòng\n\n{tt.PHAN_CACH}\n{goc}".replace("\n", "\r")
    moi = tt.ghep_abstract(cu, tt.MO_DAU + " X")
    assert moi.startswith(tt.MO_DAU) and "TÓM TẮT THỰC HÀNH" not in moi and moi.endswith(goc)
    assert moi.count(tt.PHAN_CACH) == 1


def test_emoji_ngoai_bmp_doi_thanh_chu_vi_endnote_khong_luu_duoc(tmp_path):
    """Đo 13/10: EndNote đổi «🔴» thành «?» ⇒ đọc lại lệch. Khối ghi vào chỉ được chứa ký tự mặt phẳng cơ bản."""
    f, d = _dash("WebDashboard_X_20260614.html", [dict(MUC, action="🔴 ĐỌC THẬN TRỌNG 🧪 thử")])
    k = tt.khoi_tieng_viet(tt.ngu_canh([f], _doc({f.name: d}))["pmid:31111111"], tmp_path)
    assert "▸ Thực hành: ●đỏ ĐỌC THẬN TRỌNG ◆ thử" in k
    assert all(ord(c) <= 0xFFFF for c in k)


def test_ghep_abstract_giu_goc_va_chay_lai_khong_doi():
    goc = "Background: original English abstract.\nResults: HR 0.84."
    lan1 = tt.ghep_abstract(goc, "KHỐI 1".replace("KHỐI 1", tt.MO_DAU + "\nA"))
    assert lan1.endswith(goc) and tt.PHAN_CACH in lan1
    lan1_endnote = lan1.replace("\n", "\r")  # EndNote lưu \r
    assert tt.chuan_dong(tt.ghep_abstract(lan1_endnote, tt.MO_DAU + "\nA")) == tt.chuan_dong(lan1), "chạy lại = không đổi"
    lan2 = tt.ghep_abstract(lan1_endnote, tt.MO_DAU + "\nB")
    assert lan2.count(tt.MO_DAU) == 1 and lan2.endswith(goc) and "\nA\n" not in lan2, "chỉ thay khối tiếng Việt"
    assert "PubMed không có abstract" in tt.ghep_abstract("", tt.MO_DAU + "\nA")


class _EndNoteGia:
    def __init__(self, abstract: dict[str, str], khop: dict[str, list[str]], doc_hong: set[str] = frozenset()):
        self.abstract = dict(abstract)
        self.khop = khop
        self.doc_hong = doc_hong
        self.da_ghi: list[str] = []
        self.thu_vien = Path("/khong-ton-tai/tv.enl")

    def tim_khop(self, gia_tri, truong):
        return {v: self.khop[v] for v in gia_tri if v in self.khop}

    def doc_truong(self, ids, truong):
        assert truong == "Abstract"
        return {m: self.abstract.get(m, "") for m in ids if m not in self.doc_hong}

    def ghi_truong(self, cap, truong):
        for m, gt in cap:
            self.abstract[m] = gt.replace("\n", "\r")
            self.da_ghi.append(m)
        return {m: "" for m, _ in cap}


def _chay(en, tmp_path, ap_dung, sao_luu=lambda: "/sao-luu/x"):
    f, d = _dash("WebDashboard_X_20260614.html", [MUC])
    return tt.ghi_tom_tat(en, [f], kho=tmp_path, ap_dung=ap_dung, doc_data=_doc({f.name: d}), sao_luu=sao_luu)


def test_chay_kho_khong_ghi_ap_dung_thi_sao_luu_truoc_roi_ghi(tmp_path):
    en = _EndNoteGia({"r1": "Original."}, {"31111111": ["r1"], "32222222": ["r2"]})
    bc = _chay(en, tmp_path, False)
    assert en.da_ghi == [] and bc["se_ghi"] == 2 and bc["sao_luu"] is None
    thu_tu: list[str] = []
    en.ghi_truong_goc = en.ghi_truong
    en.ghi_truong = lambda cap, t: (thu_tu.append("ghi"), en.ghi_truong_goc(cap, t))[1]
    bc = _chay(en, tmp_path, True, sao_luu=lambda: (thu_tu.append("sao_luu"), "/sao-luu/x")[1])
    assert thu_tu[0] == "sao_luu" and bc["da_ghi"] == 2 and en.abstract["r1"].endswith("Original.")
    assert bc["khong_co_ban_ghi"] == ["DOI 10.1093/bbb"]
    bc2 = _chay(en, tmp_path, True, sao_luu=lambda: pytest.fail("không có gì để ghi thì không sao lưu"))
    assert bc2["se_ghi"] == 0 and bc2["khong_doi"] == 2, "chạy lại khi dashboard không đổi ⇒ không ghi gì"


def test_sao_luu_hong_thi_khong_ghi_gi(tmp_path):
    en = _EndNoteGia({}, {"31111111": ["r1"]})

    def hong():
        raise OSError("đĩa đầy")
    with pytest.raises(OSError):
        _chay(en, tmp_path, True, sao_luu=hong)
    assert en.da_ghi == []


def test_khong_doc_duoc_abstract_thi_khong_ghi_de(tmp_path):
    en = _EndNoteGia({"r1": "Original."}, {"31111111": ["r1"]}, doc_hong={"r1"})
    bc = _chay(en, tmp_path, True)
    assert en.da_ghi == [] and any("không đọc được Abstract" in x for x in bc["loi"])


def test_trang_thai_toan_van_theo_kho(tmp_path):
    (tmp_path / "doc_sau").mkdir()
    (tmp_path / "PMID-5_CHR.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "doc_sau" / "PMID-5.md").write_text("x", encoding="utf-8")
    (tmp_path / "PMID-6_CHR.html").write_text("x", encoding="utf-8")
    assert tt.trang_thai_toan_van("5", tmp_path) == "có PDF (bản quyền — dùng cá nhân) · có bản đọc sâu"
    assert tt.trang_thai_toan_van("6", tmp_path) == "có HTML (bản quyền — dùng cá nhân)"
    assert tt.trang_thai_toan_van("7", tmp_path).startswith("CHƯA có")


def test_sao_luu_thu_vien_ban_sao_doc_duoc(tmp_path):
    tv = tmp_path / "Lib.enl"
    tv.write_bytes(b"enl")
    sdb = tmp_path / "Lib.Data" / "sdb"
    sdb.mkdir(parents=True)
    c = sqlite3.connect(sdb / "sdb.eni")
    c.execute("create table refs(id integer, abstract text)")
    c.executemany("insert into refs values (?, ?)", [(i, "x" * 500) for i in range(40)])
    c.commit()
    c.close()
    d = tt.sao_luu_thu_vien(tv, tmp_path / "sl")
    assert (d / "Lib.enl").read_bytes() == b"enl"
    assert sqlite3.connect(d / "sdb.eni").execute("select count(*) from refs").fetchone()[0] == 40
    with pytest.raises(OSError):
        tt.sao_luu_thu_vien(tmp_path / "KhongCo.enl", tmp_path / "sl")


def _endnote_mac_gia(tra_ve):
    en = object.__new__(N.EndNoteMac)
    en.goi = []

    def _chay(than, *doi_so, cho=600):
        en.goi.append((than, doi_so))
        return tra_ve(than, doi_so)
    en._chay = _chay
    return en


def test_doc_truong_tach_ban_ghi_co_xuong_dong():
    a, b = '<RecordID database="1" recNum="9" />', '<RecordID database="1" recNum="10" />'
    en = _endnote_mac_gia(lambda than, ds: f"{a}\x1fDòng 1\rDòng 2\x1e{b}\x1f\x1e")
    assert en.doc_truong([a, b], "Abstract") == {a: "Dòng 1\rDòng 2", b: ""}


def test_ghi_truong_doc_lai_khong_khop_thi_bao_loi():
    a, b = "r1", "r2"
    en = _endnote_mac_gia(lambda than, ds: "Nội dung A\rhai\x1eKHÁC\x1e")
    kq = en.ghi_truong([(a, "Nội dung A\nhai"), (b, "B")], "Abstract")
    assert kq == {a: "", b: "đọc lại không khớp nội dung vừa ghi"}

    def no(than, ds):
        raise RuntimeError("AppleScript lỗi: -1708")
    kq2 = _endnote_mac_gia(no).ghi_truong([(a, "x")], "Abstract")
    assert kq2[a].startswith("AppleScript lỗi giữa lô")


def test_cli_tom_tat_can_file_va_khong_di_cung_gan_kho():
    assert N.main(["--tom-tat-vi"]) == 3
    assert N.main(["--tom-tat-vi", "--gan-kho"]) == 3
