#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy 02/10/2026: làn Scopus / Web of Science qua tài khoản của bác sĩ (bác sĩ yêu cầu).

Kiểm: câu tìm đúng cú pháp hai trang và không tự đoán khi thiếu `truy_van_du_phong`; đọc đủ 4 định dạng export; bỏ trùng trong tệp và
với kho/hàng ngoài-quét; xếp mạnh trước; CHỈ bản ghi «xac_minh_duoc» thành ứng viên (không khớp/mơ hồ/lỗi mạng bị bỏ và ĐẾM; bài rút
bị nêu đỏ, không vào hàng); trần xác minh có ghi chú; chạy thử không ghi gì; `--ghi` nối JSONL đúng khoá + báo cáo phiên; engine vắng ⇒
mã 2 không ghi; mọi lượt xác minh lỗi ⇒ mã 2. Ngoại tuyến — bộ xác minh giả."""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("tcsw_t", REPO / "tools" / "tra_cuu_co_tai_khoan.py")
T = importlib.util.module_from_spec(_spec)
sys.modules["tcsw_t"] = T
_spec.loader.exec_module(T)

SCOPUS_CSV = (
    '﻿"Authors","Author full names","Title","Year","Source title","DOI","PubMed ID","Document Type"\n'
    '"Smolen J.","Smolen, Josef","EULAR recommendations for the management of rheumatoid arthritis: 2026 update","2026",'
    '"Annals of the Rheumatic Diseases","10.1136/ard-2026-001","41000001","Review"\n'
    '"Nguyen A.","Nguyen, An","Comparative efficacy of JAK inhibitors in rheumatoid arthritis: a systematic review and meta-analysis","2025",'
    '"Rheumatology","https://doi.org/10.1093/RHEUM/KEAF100","","Review"\n'
    '"Tran B.","Tran, Binh","Lung ultrasound in rheumatoid arthritis interstitial lung disease","2026","Clin Rheumatol",'
    '"10.1007/s10067-026-1","","Article"\n'
    '"Smolen J.","Smolen, Josef","EULAR recommendations for the management of rheumatoid arthritis: 2026 update","2026",'
    '"Annals of the Rheumatic Diseases","10.1136/ard-2026-001","41000001","Review"\n'
    '"Le C.","Le, Cuong","A randomized trial of tapering biologics in rheumatoid arthritis remission","2026","Lancet Rheumatol",'
    '"10.1016/s2665-9913(26)00001-1","","Article"\n'
)
WOS_TAB = ("PT\tAU\tTI\tSO\tDT\tPY\tDI\tPM\n"
           "J\tSmolen, J\tEULAR recommendations for the management of rheumatoid arthritis: 2026 update\tANN RHEUM DIS\tReview\t2026\t10.1136/ard-2026-001\t41000001\n"
           "J\tPham, D\tCardiovascular risk in seropositive rheumatoid arthritis cohort\tRMD OPEN\tArticle\t2025\t10.1136/rmdopen-2025-9\t\n")
WOS_PLAIN = ("FN Clarivate Analytics Web of Science\nVR 1.0\n"
             "PT J\nAU Smolen, J\nTI EULAR recommendations for the management of rheumatoid arthritis:\n   2026 update\n"
             "SO ANN RHEUM DIS\nDT Review\nPY 2026\nDI 10.1136/ard-2026-001\nPM 41000001\nER\n\n"
             "PT J\nAU Vo, E\nTI Methotrexate adherence in rheumatoid arthritis outpatients\nSO J RHEUMATOL\nDT Article\nPY 2026\n"
             "DI 10.3899/jrheum.2026-5\nER\n\nEF\n")
RIS = ("TY  - JOUR\nAU  - Smolen, J.\nTI  - EULAR recommendations for the management of rheumatoid arthritis: 2026 update\n"
       "T2  - Annals of the Rheumatic Diseases\nPY  - 2026\nDO  - 10.1136/ard-2026-001\nER  - \n"
       "TY  - JOUR\nTI  - Ngắn\nPY  - 2026\nER  - \n")


def _tep(tmp_path, ten, noi_dung, ma="utf-8"):
    p = tmp_path / ten
    p.write_bytes(noi_dung.encode(ma))
    return p


# ── câu tìm ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_cau_tim_dung_cu_phap_hai_trang():
    c = T.cau_tim({"topic": "RA", "truy_van_du_phong": "rheumatoid arthritis  disease-modifying treatment"}, 2026)
    assert c["scopus"].startswith("TITLE-ABS-KEY(rheumatoid arthritis disease-modifying treatment) AND PUBYEAR > 2024 AND (DOCTYPE(re) OR TITLE(")
    assert c["wos"].startswith("TS=(rheumatoid arthritis disease-modifying treatment) AND PY=(2025-2026) AND (DT=(Review) OR TI=(")
    for k in ("scopus", "wos"):
        assert c[k].count("(") == c[k].count(")") and c[k].count('"') % 2 == 0


@pytest.mark.parametrize("muc", [{"topic": "x"}, {"topic": "x", "truy_van_du_phong": ""},
                                 {"topic": "x", "truy_van_du_phong": '"rheumatoid arthritis"[MeSH]'}])
def test_thieu_hoac_cu_phap_pubmed_thi_khong_doan(muc):
    assert T.cau_tim(muc, 2026) is None


def test_phieu_noi_ro_bac_si_tu_dang_nhap_va_khong_cao_trang():
    vb = T.phieu([{"topic": "RA", "truy_van_du_phong": "rheumatoid arthritis treatment"}, {"topic": "Không truy vấn"}], 2026)
    assert "tự đăng nhập" in vb and "KHÔNG gõ mật khẩu" in vb and "KHÔNG tự cào" in vb and "Export" in vb
    assert "TITLE-ABS-KEY(rheumatoid arthritis treatment)" in vb and "⚪ chưa có `truy_van_du_phong`" in vb


def test_chon_chu_de_theo_ten_khong_dau_va_theo_mu(tmp_path):
    ds = [{"topic": "Viêm khớp dạng thấp (RA)"}, {"topic": "Hen phế quản"}, {"topic": "Gout"}]
    sl = tmp_path / "sl.json"
    sl.write_text(json.dumps({"mu": ["Hen phế quản"]}), encoding="utf-8")
    assert [t["topic"] for t in T.chon_chu_de(ds, ["viem khop"], False, sl)] == ["Viêm khớp dạng thấp (RA)"]
    assert [t["topic"] for t in T.chon_chu_de(ds, [], True, sl)] == ["Hen phế quản"]


# ── đọc tệp ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_doc_scopus_csv(tmp_path):
    dang, ds = T.doc_tep(_tep(tmp_path, "scopus.csv", SCOPUS_CSV))
    assert dang == "scopus_csv" and len(ds) == 5
    assert ds[1]["doi"] == "10.1093/rheum/keaf100", "DOI dạng URL/hoa phải chuẩn hoá"
    assert ds[0]["pmid"] == "41000001" and ds[0]["year"] == 2026 and ds[0]["tac_gia"] == "Smolen J."


def test_doc_wos_tab_utf16(tmp_path):
    dang, ds = T.doc_tep(_tep(tmp_path, "savedrecs.txt", "﻿" + WOS_TAB, "utf-16-le"))
    assert dang == "wos_tab" and [d["doi"] for d in ds] == ["10.1136/ard-2026-001", "10.1136/rmdopen-2025-9"]


def test_doc_wos_plain_noi_dong_tiep(tmp_path):
    dang, ds = T.doc_tep(_tep(tmp_path, "savedrecs.txt", WOS_PLAIN))
    assert dang == "wos_plain" and len(ds) == 2
    assert ds[0]["title"] == "EULAR recommendations for the management of rheumatoid arthritis: 2026 update"


def test_doc_ris_bo_ban_ghi_tieu_de_ngan(tmp_path):
    dang, ds = T.doc_tep(_tep(tmp_path, "x.ris", RIS))
    assert dang == "ris" and len(ds) == 1 and ds[0]["journal"] == "Annals of the Rheumatic Diseases"


def test_tep_la_khong_nhan_dang(tmp_path):
    assert T.doc_tep(_tep(tmp_path, "x.txt", "chỉ là một ghi chú\nkhông phải export")) == ("", [])


# ── bỏ trùng · xếp hạng ────────────────────────────────────────────────────────────────────────────────────────────────
def test_bo_trung_va_xep_manh_truoc(tmp_path):
    _d, ds = T.doc_tep(_tep(tmp_path, "scopus.csv", SCOPUS_CSV))
    ra, dem = T.chuan_bi(ds, pm_kho=set(), doi_kho={"10.1007/s10067-026-1"})
    assert dem == {"trung_trong_tep": 1, "da_co_trong_kho_hoac_hang": 1}
    assert [T.diem(b) for b in ra] == [5, 4, 3]
    assert ra[0]["title"].startswith("EULAR recommendations")


def test_da_co_doc_so_xac_minh_va_hang(tmp_path):
    so = tmp_path / "so.json"
    so.write_text(json.dumps({"muc": {"pmid:111": {"cac_dashboard": ["a"]}, "pmid:222": {"cac_dashboard": []},
                                      "doi:10.1/AB": {"cac_dashboard": ["b"]}}}), encoding="utf-8")
    hang = tmp_path / "hang.jsonl"
    hang.write_text('{"pmid": "333", "doi": "10.9/X"}\nhỏng\n', encoding="utf-8")
    pm, doi = T.da_co(so, hang)
    assert pm == {"111", "333"} and doi == {"10.1/ab", "10.9/x"}


# ── nhập + xác minh ────────────────────────────────────────────────────────────────────────────────────────────────────
def _xm(ket: dict):
    """Bộ xác minh giả: tra theo DOI ⇒ kết quả định sẵn; mặc định không khớp."""
    def f(b):
        k = ket.get(b["doi"], "khong_khop")
        r = {"ket_qua": k, "ly_do": f"giả: {k}"}
        if k == "xac_minh_duoc":
            r.update(pmid=b["pmid"] or "999", doi=b["doi"], title=b["title"], journal=b["journal"], study_type="Review", co=[])
        return r
    return f


def test_chi_xac_minh_duoc_moi_thanh_ung_vien_rut_bai_neu_do(tmp_path):
    p = _tep(tmp_path, "scopus.csv", SCOPUS_CSV)
    bc = T.nhap(p, "scopus", "Viêm khớp dạng thấp (RA)", toi_da=7, pm_kho=set(), doi_kho=set(),
                xac_minh=_xm({"10.1136/ard-2026-001": "xac_minh_duoc", "10.1093/rheum/keaf100": "bi_rut_bai",
                              "10.1016/s2665-9913(26)00001-1": "loi_xac_minh"}))
    assert [c["doi"] for c in bc["chon"]] == ["10.1136/ard-2026-001"]
    assert [r["doi"] for r in bc["rut_bai"]] == ["10.1093/rheum/keaf100"]
    assert sorted(h["ket_qua"] for h in bc["bo"]) == ["khong_khop", "loi_xac_minh"]
    assert bc["dem"]["xac_minh_loi"] == 1 and bc["dem"]["da_xac_minh"] == 4


def test_tran_xac_minh_duoc_ghi_ro_khong_cat_im_lang(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "HE_SO_XAC_MINH", 1)
    goi = []
    p = _tep(tmp_path, "scopus.csv", SCOPUS_CSV)
    bc = T.nhap(p, "scopus", "RA", toi_da=2, pm_kho=set(), doi_kho=set(),
                xac_minh=lambda b: goi.append(b["doi"]) or {"ket_qua": "khong_khop"})
    assert len(goi) == 2 and bc["khong_xac_minh_vuot_tran"] == 2


def test_toi_da_ung_vien(tmp_path):
    p = _tep(tmp_path, "scopus.csv", SCOPUS_CSV)
    bc = T.nhap(p, "scopus", "RA", toi_da=1, pm_kho=set(), doi_kho=set(),
                xac_minh=lambda b: {"ket_qua": "xac_minh_duoc", "pmid": "", "doi": b["doi"], "title": b["title"],
                                    "journal": "", "study_type": "", "co": []})
    assert len(bc["chon"]) == 1 and bc["chon"][0]["doi"] == "10.1136/ard-2026-001"


def test_ghi_noi_jsonl_dung_khoa_va_bao_cao_phien(tmp_path):
    p = _tep(tmp_path, "scopus.csv", SCOPUS_CSV)
    bc = T.nhap(p, "scopus", "Viêm khớp dạng thấp (RA)", toi_da=7, pm_kho=set(), doi_kho=set(),
                xac_minh=_xm({"10.1136/ard-2026-001": "xac_minh_duoc"}))
    hang = tmp_path / "surveillance" / "ung-vien-ngoai-quet.jsonl"
    hang.parent.mkdir()
    hang.write_text('{"pmid": "1", "trang_thai": "THEO DÕI"}\n', encoding="utf-8")
    bc_tep = T.ghi_ket_qua(bc, date(2026, 10, 2), hang=hang, thu_muc_bao_cao=tmp_path / "phien-web")
    dong = hang.read_text(encoding="utf-8").splitlines()
    assert len(dong) == 2 and json.loads(dong[0])["pmid"] == "1", "dòng cũ giữ nguyên"
    moi = json.loads(dong[1])
    for k in ("pmid", "doi", "title", "journal", "pubtype", "chu_de", "nguon_phat_hien", "lien_quan", "trang_thai", "ghi_luc"):
        assert k in moi
    assert moi["trang_thai"] == "CANDIDATE" and "Scopus web" in moi["nguon_phat_hien"] and "bác sĩ đăng nhập" in moi["nguon_phat_hien"]
    assert moi["xac_minh"]["ket_qua"] == "xac_minh_duoc" and "chuỗi 3 tầng" in moi["rut_bai"]
    assert json.loads(bc_tep.read_text(encoding="utf-8"))["dem"]["da_xac_minh"] == 4


def test_khong_co_ung_vien_thi_khong_dong_vao_hang(tmp_path):
    p = _tep(tmp_path, "scopus.csv", SCOPUS_CSV)
    bc = T.nhap(p, "scopus", "RA", toi_da=7, pm_kho=set(), doi_kho=set(), xac_minh=_xm({}))
    hang = tmp_path / "hang.jsonl"
    T.ghi_ket_qua(bc, date(2026, 10, 2), hang=hang, thu_muc_bao_cao=tmp_path / "pw")
    assert not hang.exists() and list((tmp_path / "pw").glob("*.json")), "báo cáo phiên vẫn phải có (không lọc im lặng)"


# ── main ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def moi_truong(tmp_path, monkeypatch):
    wl = tmp_path / "watchlist.json"
    wl.write_text(json.dumps({"topics": [{"topic": "Viêm khớp dạng thấp (RA)", "truy_van_du_phong": "rheumatoid arthritis"},
                                         {"topic": "Hen phế quản"}]}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(T, "WATCHLIST", wl)
    monkeypatch.setattr(T, "HANG_NGOAI_QUET", tmp_path / "hang.jsonl")
    monkeypatch.setattr(T, "BAO_CAO_PHIEN", tmp_path / "pw")
    monkeypatch.setattr(T, "SO_XAC_MINH", tmp_path / "khong-co.json")
    return tmp_path


def test_main_chay_thu_khong_ghi(moi_truong, monkeypatch, capsys):
    monkeypatch.setattr(T, "tao_xac_minh_engine", lambda: _xm({"10.1136/ard-2026-001": "xac_minh_duoc"}))
    p = _tep(moi_truong, "scopus.csv", SCOPUS_CSV)
    assert T.main(["--nhap", str(p), "--chu-de", "viem khop"]) == 0
    assert "CHẠY THỬ" in capsys.readouterr().out and not (moi_truong / "hang.jsonl").exists()


def test_main_ghi(moi_truong, monkeypatch):
    monkeypatch.setattr(T, "tao_xac_minh_engine", lambda: _xm({"10.1136/ard-2026-001": "xac_minh_duoc"}))
    p = _tep(moi_truong, "scopus.csv", SCOPUS_CSV)
    assert T.main(["--nhap", str(p), "--chu-de", "viem khop", "--ghi"]) == 0
    assert len((moi_truong / "hang.jsonl").read_text(encoding="utf-8").splitlines()) == 1


def test_main_engine_vang_thi_ma_2_khong_ghi(moi_truong, monkeypatch, capsys):
    def hong():
        raise FileNotFoundError("không có engine")
    monkeypatch.setattr(T, "tao_xac_minh_engine", hong)
    p = _tep(moi_truong, "scopus.csv", SCOPUS_CSV)
    assert T.main(["--nhap", str(p), "--chu-de", "viem khop", "--ghi"]) == 2
    assert "KHÔNG XÁC MINH ĐƯỢC" in capsys.readouterr().out and not (moi_truong / "hang.jsonl").exists()


def test_main_moi_luot_xac_minh_loi_thi_ma_2_khong_ghi(moi_truong, monkeypatch, capsys):
    monkeypatch.setattr(T, "tao_xac_minh_engine", lambda: (lambda b: {"ket_qua": "loi_xac_minh", "ly_do": "mạng"}))
    p = _tep(moi_truong, "scopus.csv", SCOPUS_CSV)
    assert T.main(["--nhap", str(p), "--chu-de", "viem khop", "--ghi"]) == 2
    assert "KHÔNG phải «không có bài»" in capsys.readouterr().out and not (moi_truong / "hang.jsonl").exists()


@pytest.mark.parametrize("args,ma", [(["--chu-de", "khong-ton-tai"], 3), (["--chu-de", "e"], 3), ([], 3)])
def test_main_chu_de_phai_khop_dung_mot(moi_truong, monkeypatch, args, ma):
    monkeypatch.setattr(T, "tao_xac_minh_engine", lambda: _xm({}))
    p = _tep(moi_truong, "scopus.csv", SCOPUS_CSV)
    assert T.main(["--nhap", str(p), *args]) == ma


def test_main_ris_bat_buoc_neu_nguon(moi_truong, monkeypatch, capsys):
    monkeypatch.setattr(T, "tao_xac_minh_engine", lambda: _xm({}))
    p = _tep(moi_truong, "x.ris", RIS)
    assert T.main(["--nhap", str(p), "--chu-de", "viem khop"]) == 3 and "--nguon" in capsys.readouterr().out
    assert T.main(["--nhap", str(p), "--chu-de", "viem khop", "--nguon", "wos"]) == 1


# ── DynaMed (thêm cùng ngày — bác sĩ đăng nhập DynaMed trên khung trình duyệt) ───────────────────────────────────────────
DM_HAI_DONG = """Recent Alerts
Drug/Device Alert
Updated 2 Oct 2026

Obinutuzumab (Gazyva) receives expanded FDA approval in childhood-onset idiopathic nephrotic syndrome (FDA Product Information 2026 Sep).

View in Management of Nephrotic Syndrome in Children

Evidence
Updated 2 Oct 2026

The addition of radium-223 to first-line enzalutamide may improve overall survival in metastatic castration-resistant prostate cancer (Ann Oncol 2026 May).

View in Management of Castration-Resistant Prostate Cancer
"""
DM_MOT_DONG = """Guideline SummaryUpdated 1 Oct 2026

World Society of Emergency Surgery (WSES) recommendations for nonoperative management of uncomplicated appendicitis (JAMA Surg 2026 Mar 1)

View in Management of Appendicitis in Adolescents and Adults

EvidenceUpdated 30 Sep 2026

Inhaled corticosteroid tapering may reduce exacerbations in adults with severe eosinophilic asthma (Lancet Respir Med 2026 Aug).

View in Asthma in Adults
"""
WL_DM = [{"topic": "Hội chứng thận hư & Bệnh thận nhi", "truy_van_du_phong": "nephrotic syndrome treatment in children"},
         {"topic": "Hen phế quản", "truy_van_du_phong": "asthma management with inhaled therapy"},
         {"topic": "ĐTĐ + GLP-1", "truy_van_du_phong": "GLP-1 receptor agonist obesity diabetes"},
         {"topic": "IBS", "truy_van_du_phong": "irritable bowel syndrome"}]


def test_dynamed_tach_ca_hai_bo_cuc_va_khong_giu_cau_tom_tat():
    a = T.doc_canh_bao_dynamed(DM_HAI_DONG)
    b = T.doc_canh_bao_dynamed(DM_MOT_DONG)
    assert [(x["loai"], x["ngay"], x["trich_dan"]) for x in a] == [
        ("Drug/Device Alert", "2026-10-02", "FDA Product Information 2026 Sep"), ("Evidence", "2026-10-02", "Ann Oncol 2026 May")]
    assert [(x["loai"], x["ngay"], x["chu_de_dynamed"]) for x in b] == [
        ("Guideline Summary", "2026-10-01", "Management of Appendicitis in Adolescents and Adults"),
        ("Evidence", "2026-09-30", "Asthma in Adults")]
    for x in a + b:
        assert set(x) == {"loai", "ngay", "trich_dan", "chu_de_dynamed", "tu_khoa", "so_thu_tu"}, "không được giữ câu tóm tắt của DynaMed"
        assert len(x["tu_khoa"]) <= 4


def test_dynamed_van_ban_khong_phai_trang_canh_bao_thi_rong():
    assert T.doc_canh_bao_dynamed("Một trang bất kỳ\nkhông có cảnh báo") == []


@pytest.mark.parametrize("td,mong", [("Ann Oncol 2026 May", {"tap_chi": "Ann Oncol", "nam": 2026}),
                                     ("Am J Obstet Gynecol 2026 Jul 14 early online", {"tap_chi": "Am J Obstet Gynecol", "nam": 2026}),
                                     ("FDA Product Information 2026 Sep", None), ("NCCN 2026 Sep", None), ("không có năm", None)])
def test_tach_trich_dan(td, mong):
    assert T.tach_trich_dan(td) == mong


@pytest.mark.parametrize("ten,mong", [
    ("Management of Nephrotic Syndrome in Children", "Hội chứng thận hư & Bệnh thận nhi"),   # trùng 2 từ đặc hiệu
    ("Asthma in Adults", "Hen phế quản"),                                                      # tên có đúng 1 từ đặc hiệu
    ("Management of Hormone Receptor (HR) Positive, HER2 Negative Metastatic Breast Cancer", None),  # chỉ trùng «receptor» ⇒ không gắn
    ("Endometriosis", None),
    ("Obesity Hypoventilation Syndrome", None),   # 2 từ đặc hiệu, chỉ trùng «obesity» với chủ đề GLP-1 ⇒ KHÔNG gắn
    ("", None),
])
def test_gan_chu_de_khong_doan(ten, mong):
    assert T.gan_chu_de(ten, WL_DM) == mong


def test_gan_chu_de_hoa_diem_cao_nhat_thi_khong_gan():
    wl = [{"topic": "A", "truy_van_du_phong": "gout flare"}, {"topic": "B", "truy_van_du_phong": "gout urate"}]
    assert T.gan_chu_de("Gout", wl) is None


def _tim(bang):
    def f(term):
        for k, v in bang.items():
            if k in term:
                if isinstance(v, Exception):
                    raise v
                return v
        return []
    return f


BAI = {"pmid": "42000001", "title": "Final overall survival results of enzalutamide plus radium-223", "journal": "Annals of oncology",
       "year": 2026, "doi": "10.1016/j.annonc.2026.02.009"}


def test_phan_giai_chi_nhan_dung_mot_bai():
    cb = {"trich_dan": "Ann Oncol 2026 May", "tu_khoa": ["castration-resistant", "enzalutamide", "radium-223"]}
    assert T.phan_giai_pubmed(cb, _tim({'"Ann Oncol"[ta] AND 2026[dp]': [BAI]})) == ("mot", BAI)
    assert T.phan_giai_pubmed(cb, _tim({'"Ann Oncol"[ta]': [BAI, {**BAI, "pmid": "2"}]}))[0] == "mo_ho"
    assert T.phan_giai_pubmed(cb, _tim({}))[0] == "khong_thay"
    assert T.phan_giai_pubmed(cb, _tim({'"Ann Oncol"': RuntimeError("NCBI chặn")}))[0] == "loi"
    assert T.phan_giai_pubmed({"trich_dan": "NCCN 2026 Sep", "tu_khoa": ["x"]}, _tim({}))[0] == "ngoai_pubmed"


def test_phan_giai_noi_dan_so_tu_khoa():
    goi = []

    def tim(term):
        goi.append(term.count("[tiab]"))
        return [BAI] if term.count("[tiab]") == 2 else []
    cb = {"trich_dan": "Ann Oncol 2026 May", "tu_khoa": ["a1", "b2", "c3", "d4"]}
    assert T.phan_giai_pubmed(cb, tim)[0] == "mot" and goi == [4, 3, 2]


def test_tu_canh_bao_chi_tra_chu_de_watchlist_tru_khi_tat_ca():
    cb = T.doc_canh_bao_dynamed(DM_HAI_DONG + DM_MOT_DONG)
    tim = _tim({'"Lancet Respir Med"': [{**BAI, "pmid": "43000009", "title": "Inhaled corticosteroid tapering in severe asthma",
                                         "doi": "10.1016/s2213-2600(26)00001-1"}],
                '"Ann Oncol"': [BAI], '"JAMA Surg"': [{**BAI, "pmid": "41999999", "doi": "10.1001/jamasurg.2025.6218",
                                                        "title": "Diagnosis and Treatment of Acute Appendicitis"}]})
    bg, bc = T.tu_canh_bao_dynamed(cb, WL_DM, tim)
    assert [b["chu_de"] for b in bg] == ["Hen phế quản"] and bg[0]["pmid"] == "43000009"
    assert len(bc["ngoai_pubmed"]) == 1 and bc["ngoai_pubmed"][0].startswith("cảnh báo DynaMed #1 (2026-10-02)")
    assert len(bc["ngoai_watchlist"]) == 2
    # 03/10/2026 — điều khoản EBSCO: đầu ra (Claude đọc được) không mang CHỮ NÀO của DynaMed: tên chủ đề, trích dẫn, loại cảnh báo.
    chu_dm = {x["chu_de_dynamed"] for x in cb} | {x["trich_dan"] for x in cb} | {x["loai"] for x in cb}
    dau_ra = [b["ngu_canh"] for b in bg] + bc["ngoai_pubmed"] + bc["ngoai_watchlist"] + bc["khong_phan_giai"]
    lot = [(c, d) for c in chu_dm for d in dau_ra if c and c in d]
    assert not lot, f"đầu ra còn chữ của DynaMed: {lot[:3]}"
    bg2, _ = T.tu_canh_bao_dynamed(cb, WL_DM, tim, tat_ca=True)
    assert len(bg2) == 3


def test_xu_ly_giu_pmid_khi_ban_ghi_dang_ky_khong_co_pmid():
    bg = [{**T._ban_ghi(BAI["title"], 2026, BAI["journal"], BAI["doi"], BAI["pmid"], "Evidence"), "chu_de": "X", "ngu_canh": "nc"}]
    bc = T.xu_ly(bg, "dynamed", "t.txt", "dynamed_canh_bao", "(theo từng cảnh báo)", toi_da=7, pm_kho=set(), doi_kho=set(),
                 xac_minh=lambda b: {"ket_qua": "xac_minh_duoc", "pmid": "", "doi": b["doi"], "title": b["title"],
                                     "journal": "J", "study_type": "", "co": []})
    c = bc["chon"][0]
    assert c["pmid"] == BAI["pmid"] and c["chu_de"] == "X" and c["ngu_canh"] == "nc"
    d = T.dong_hang(bc, date(2026, 10, 2))[0]
    assert d["chu_de"] == "X" and "DynaMed Recent Alerts" in d["nguon_phat_hien"] and "nc" in d["nguon_phat_hien"]


def test_main_dynamed_chay_thu_va_ghi(moi_truong, monkeypatch, capsys):
    monkeypatch.setattr(T, "WATCHLIST", moi_truong / "wl_dm.json")
    (moi_truong / "wl_dm.json").write_text(json.dumps({"topics": WL_DM}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(T, "tao_tim_pubmed", lambda: _tim({'"Lancet Respir Med"': [{**BAI, "pmid": "43000009",
                                                            "title": "Inhaled corticosteroid tapering in severe asthma",
                                                            "doi": "10.1016/s2213-2600(26)00001-1"}]}))
    monkeypatch.setattr(T, "tao_xac_minh_engine", lambda: (lambda b: {"ket_qua": "xac_minh_duoc", "pmid": b["pmid"],
                                                                       "doi": b["doi"], "title": b["title"], "journal": "",
                                                                       "study_type": "", "co": []}))
    tep = _tep(moi_truong, "dm.txt", DM_HAI_DONG + DM_MOT_DONG)
    assert T.main(["--dynamed-canh-bao", str(tep)]) == 0
    out = capsys.readouterr().out
    assert "CHẠY THỬ" in out and "NGUỒN NGOÀI PUBMED" in out and not (moi_truong / "hang.jsonl").exists()
    assert T.main(["--dynamed-canh-bao", str(tep), "--ghi"]) == 0
    dong = [json.loads(x) for x in (moi_truong / "hang.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [d["chu_de"] for d in dong] == ["Hen phế quản"] and dong[0]["pmid"] == "43000009"


def test_main_dynamed_van_ban_la_thi_ma_3(moi_truong, capsys):
    tep = _tep(moi_truong, "x.txt", "không phải trang DynaMed")
    assert T.main(["--dynamed-canh-bao", str(tep)]) == 3


def test_huong_dan_dynamed_cam_cao_hang_loat_va_khong_luu_cau():
    # 03/10/2026 — điều khoản EBSCO (AI phải được phép; TDM bị cấm): Claude không mở/đọc trang hay tệp chép của DynaMed.
    assert "Claude KHÔNG mở, KHÔNG đọc trang DynaMed" in T.HUONG_DAN_DYNAMED and "KHÔNG đọc tệp bác sĩ chép" in T.HUONG_DAN_DYNAMED
    assert "không in, không lưu chữ nào của DynaMed" in T.HUONG_DAN_DYNAMED
    assert "Claude KHÔNG mở/đọc trang Scopus" in T.HUONG_DAN_SCOPUS


def test_scopus_khong_mang_tieu_de_export_ra_dau_ra():
    """Scopus là nội dung Elsevier (điều khoản: không dùng với công cụ AI) — dòng bỏ/rút không mang tiêu đề export; ứng viên được
    chọn lấy tiêu đề của cơ quan đăng ký."""
    bg = [T._ban_ghi(f"Tieu de export Scopus so {i} du dai", 2026, "J", f"10.1/{i}", "", "Review") for i in range(3)]
    kq = {"10.1/0": "xac_minh_duoc", "10.1/1": "bi_rut_bai", "10.1/2": "khong_khop"}
    bc = T.xu_ly(bg, "scopus", "t.csv", "scopus_csv", "X", toi_da=7, pm_kho=set(), doi_kho=set(),
                 xac_minh=lambda b: {"ket_qua": kq[b["doi"]], "pmid": "", "doi": b["doi"], "title": "Tieu de Crossref",
                                     "journal": "", "study_type": "", "co": []})
    assert bc["chon"][0]["title"] == "Tieu de Crossref"
    assert all("Tieu de export" not in json.dumps(x, ensure_ascii=False) for x in bc["rut_bai"] + bc["bo"])
