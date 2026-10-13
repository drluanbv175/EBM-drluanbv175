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


def test_khoi_nguon_chinh_chep_dung_truong_va_nhan_dashboard(tmp_path):
    f, d = _dash("WebDashboard_X_20260614.html", [MUC])
    ds = tt.ngu_canh([f], _doc({f.name: d}))
    k = tt.khoi_tieng_viet(ds["pmid:31111111"], tmp_path)
    assert k.startswith(tt.MO_DAU) and "PMID 31111111 · DOI 10.1016/aaa" in k
    for chu in ("Colchicine dự phòng thứ phát", "Đột quỵ không do tim", "P: Đột quỵ | I: Colchicine | C: Chuẩn | O: Tái phát",
                "Kết quả chính không đạt ý nghĩa; HR 0.84 (KTC 95% 0.68–1.05)", "Mức chứng cứ: Trung bình",
                "Khuyến nghị cho thực hành: Chưa đủ thay đổi — CHƯA thêm colchicine thường quy",
                "Áp dụng tại Việt Nam: Không khởi trị ngoài nghiên cứu", "Lưu ý: Âm tính", "Cần bác sĩ kiểm chứng", "14/06/2026"):
        assert chu in k, chu
    assert "Theo dõi" not in k, "ô giữ chỗ «—» không được in thành một dòng"
    assert "CHƯA có toàn văn" in k


@pytest.mark.parametrize("gl, qd, can", [("na", "apply", ["Nguồn không phân hạng", "KHÔNG có nghĩa là chứng cứ yếu",
                                                            "Áp dụng ngay"]),
                                         ("high", "consider", ["Mức chứng cứ: Cao", "Cân nhắc chọn lọc"]),
                                         ("la", "xyz", ["chưa rõ (giá trị «la»)", "chưa rõ (giá trị «xyz»)"])])
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
    assert "TÀI LIỆU THAM KHẢO bổ trợ cho mục «Colchicine" in k and "nguồn chính của mục: PMID 31111111" in k
    for chu in ("HR 0.84", "CHƯA thêm colchicine", "Không khởi trị", "Mức chứng cứ", "Khuyến nghị cho thực hành"):
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


def test_emoji_ngoai_bmp_doi_thanh_chu_vi_endnote_khong_luu_duoc(tmp_path):
    """Đo 13/10: EndNote đổi «🔴» thành «?» ⇒ đọc lại lệch. Khối ghi vào chỉ được chứa ký tự mặt phẳng cơ bản."""
    f, d = _dash("WebDashboard_X_20260614.html", [dict(MUC, action="🔴 ĐỌC THẬN TRỌNG 🧪 thử")])
    k = tt.khoi_tieng_viet(tt.ngu_canh([f], _doc({f.name: d}))["pmid:31111111"], tmp_path)
    assert "●đỏ ĐỌC THẬN TRỌNG ◆ thử" in k
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
    s5, s6 = tt.trang_thai_toan_van("5", tmp_path), tt.trang_thai_toan_van("6", tmp_path)
    assert "có PDF toàn văn" in s5 and "có bản quyền" in s5 and "doc_sau/PMID-5.md" in s5
    assert "có HTML toàn văn" in s6 and "đọc sâu" not in s6
    assert "CHƯA có toàn văn" in tt.trang_thai_toan_van("7", tmp_path)


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
