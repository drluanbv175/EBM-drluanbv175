#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy 02/10/2026 — làn đọc toàn văn bài KHÔNG OA qua trình duyệt có bác sĩ (`tools/doc_toan_van_co_nguoi.py`).

Ngoại tuyến: mạng (Europe PMC, doi.org) và bộ xác minh định danh đều GIẢ, kho toàn văn dựng trong tmp_path."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
HOM_NAY = date(2026, 10, 2)


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


D = _nap("_t_dtv", "doc_toan_van_co_nguoi.py")
XN = _nap("_t_dtv_xn", "xac_nhan_trinh_duyet.py")
TIEU_DE = "Cognitive behavioral therapy for insomnia-assisted discontinuation of hypnotics: a systematic review and meta-analysis"


def _hs(**sua) -> dict:
    hs = {"pmid": "42751933", "doi": "10.1177/03000605261487272", "tieu_de_bai": TIEU_DE,
          "url_doc": "https://journals.sagepub.com/doi/10.1177/03000605261487272",
          "tieu_de_trang": TIEU_DE + " - SAGE Journals", "doc_luc": HOM_NAY.isoformat(),
          "nguon_truy_cap": "trinh_duyet_co_nguoi", "gap_chan": True, "nguoi_vuot_chan": "bac_si",
          "so_ky_tu_toan_van": 41000, "sha256_toan_van": "ab" * 32, "loai_tai_lieu": "sr_ma",
          "phuong_phap": {"thiet_ke": "Tổng quan hệ thống + phân tích gộp 12 RCT", "quan_the": "Người lớn dùng thuốc ngủ kéo dài",
                          "ket_cuc_chinh": "Ngừng thuốc ngủ hoàn toàn", "nguy_co_sai_lech": "RoB 2: 8 thấp, 4 vài lo ngại",
                          "di_bien": "I² 41%"},
          "ket_qua": [{"ket_cuc": "Ngừng thuốc ngủ", "chi_so": "RR", "gia_tri": 1.85, "ci_duoi": 1.32, "ci_tren": 2.59, "p": "<0.001",
                       "vi_tri": "Hình 2", "trich_ngan": "CBT-I nearly doubled discontinuation"}],
          "han_che": "Đa số thử nghiệm nhỏ, không làm mù người tham gia", "tai_tro_coi": "Không tài trợ; không xung đột khai báo",
          "dieu_khoan": {"url": "https://nxb-thu.invalid/terms", "doc_luc": "2026-10-02", "ket_luan": "giay_phep_cc",
                         "trich": "CC BY-NC 4.0"}}
    hs.update(sua)
    return hs


def _xm(ket_qua="xac_minh_duoc", title=TIEU_DE):
    return lambda b: {"ket_qua": ket_qua, "ly_do": "", "pmid": b["pmid"], "doi": b["doi"], "title": title}


# ── phiếu ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pmid_chi_lay_khoi_the(tmp_path):
    q = tmp_path / "tuan-2026-W40.md"
    q.write_text("# Gói\nPMID 11111111 ở bảng đầu\n## ⓶ BẢY THẺ — CANDIDATE\nNguồn: PMID 42377292 · PMID 42751933\n"
                 "## ⓷ GIỮ LẠI\n- PMID 42788405\n", encoding="utf-8", newline="\n")
    assert D.pmid_cua_queue(q) == ["42377292", "42751933"]


def test_bao_phu_cuc_bo_doc_dung_kho(tmp_path):
    kho = tmp_path / "toan_van_oa"
    (kho / "trinh_duyet").mkdir(parents=True)
    (kho / "PMID-10000001_PMC1.xml").write_text("<x/>", encoding="utf-8", newline="\n")
    (kho / "PMID-10000002_UPW.pdf").write_bytes(b"%PDF")
    (kho / "trinh_duyet" / "PMID-10000003.json").write_text("{}", encoding="utf-8", newline="\n")
    (kho / "trinh_duyet" / "khong-truy-cap.jsonl").write_text(
        json.dumps({"pmid": "10000004", "ngay": "2026-09-30", "ly_do": "đòi mua bài"}) + "\n"
        + json.dumps({"pmid": "10000005", "ngay": "2026-01-01", "ly_do": "cũ"}) + "\n", encoding="utf-8", newline="\n")
    bp = D.bao_phu_cuc_bo(["10000001", "10000002", "10000003", "10000004", "10000005"], kho, HOM_NAY)
    assert bp == {"10000001": "oa_xml", "10000002": "oa_khac", "10000003": "da_doc_trinh_duyet",
                  "10000004": "khong_truy_cap", "10000005": "chua_co"}, "quá 90 ngày thì nhắc lại"


def test_duong_doc_phan_nhanh_va_loi_mang_khong_thanh_khong_co():
    oa = D.duong_doc("1", "chua_co", epmc=lambda **k: {"pmcid": "PMC9", "isOpenAccess": "Y", "doi": "10.1/a"})
    assert oa["cach"] == "oa_chua_gom"
    mp = D.duong_doc("2", "chua_co", epmc=lambda **k: {"doi": "10.1/b", "fullTextUrlList": {"fullTextUrl": [
        {"availabilityCode": "F", "url": "https://www.nejm.org/doi/full/10.1/b"}]}})
    assert mp["cach"] == "trinh_duyet" and mp["mien_phi"] and "Cloudflare" in mp["mien_do_duoc"]
    # (jacc.org là Elsevier ⇒ nay thuộc «bác sĩ đọc trực tiếp» — ca này dùng một NXB ngoài bảng cấm.)
    qua_doi = D.duong_doc("3", "chua_co", epmc=lambda **k: {"doi": "10.1/c"}, doi_dich=lambda d: "https://www.ahajournals.org/doi/" + d)
    assert qua_doi["cach"] == "trinh_duyet" and qua_doi["mien"] == "www.ahajournals.org" and not qua_doi["mien_phi"]

    def hong(**k):
        raise OSError("mạng")
    assert D.duong_doc("4", "chua_co", epmc=hong)["cach"] == "chua_ro"
    assert D.duong_doc("5", "chua_co", epmc=lambda **k: {"doi": "10.1/e"},
                       doi_dich=lambda d: (_ for _ in ()).throw(TimeoutError()))["cach"] == "chua_ro"
    assert D.duong_doc("6", "oa_xml")["cach"] == "oa_xml"


def test_phan_loai_mien_ghi_ro_do_hay_suy():
    assert "đo 02/10/2026" in D.phan_loai_mien("https://diabetesjournals.org/care/article/49/S1/x")
    assert "suy từ" in D.phan_loai_mien("https://thorax.bmj.com/content/1")
    assert D.phan_loai_mien("https://mien-chua-do.invalid/x").startswith("chưa đo")


# ── kiểm hồ sơ ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_ho_so_hop_le_du_muc_la_full():
    loi, cb, kiem = D.kiem_ho_so(_hs(), HOM_NAY, XN.kiem_tieu_de)
    assert loi == [] and kiem["do_day_du"] == "full", (loi, cb)


@pytest.mark.parametrize("sua, mau", [
    ({"tieu_de_trang": "Just a moment..."}, "CHẶN BOT"),
    ({"tieu_de_trang": "Chờ một chút..."}, "CHẶN BOT"),                       # trình duyệt app chạy giao diện tiếng Việt
    ({"tieu_de_trang": "Thực hiện xác minh bảo mật"}, "CHẶN BOT"),
    ({"tieu_de_trang": "Sign in to your account | ScienceDirect"}, "ĐĂNG NHẬP"),
    ({"gap_chan": True, "nguoi_vuot_chan": "claude"}, "KHÔNG tự vượt"),
    ({"so_ky_tu_toan_van": 1800}, "tóm tắt"),
    ({"sha256_toan_van": "abc"}, "64 ký tự hex"),
    ({"han_che": "x" * 900}, "nguyên văn"),
    ({"toan_van": "..."}, "khoá chứa toàn văn"),
    ({"url_doc": "https://www.dynamed.com/topics/dmp~AN~T1"}, "TỔNG HỢP"),
    ({"doc_luc": "2026-10-09"}, "tương lai"),
    ({"doc_luc": "2026-09-01"}, "cũ hơn"),
    ({"ghi_chu": "liên hệ bn@example.com"}, "định danh"),
    ({"pmid": "", "doi": ""}, "thiếu cả pmid"),
])
def test_ho_so_bi_tu_choi(sua, mau):
    loi, _cb, _k = D.kiem_ho_so(_hs(**sua), HOM_NAY, XN.kiem_tieu_de)
    assert any(mau in x for x in loi), loi


@pytest.mark.parametrize("ket_qua, mau", [
    ({"ket_cuc": "A", "chi_so": "RR", "gia_tri": 3.1, "ci_duoi": 1.3, "ci_tren": 2.6, "vi_tri": "Bảng 2"}, "ngoài CI"),
    ({"ket_cuc": "A", "chi_so": "HR", "gia_tri": -0.5, "vi_tri": "Bảng 2"}, "> 0"),
    ({"ket_cuc": "A", "chi_so": "OR", "gia_tri": 1.2, "vi_tri": ""}, "vi_tri"),
    ({"ket_cuc": "A", "chi_so": "OR", "gia_tri": "1.2", "vi_tri": "Bảng 1"}, "gia_tri (số)"),
    ({"ket_cuc": "A", "chi_so": "OR", "gia_tri": 1.2, "ci_duoi": 1.0, "vi_tri": "Bảng 1"}, "thiếu một đầu"),
    ({"ket_cuc": "A", "chi_so": "MD", "gia_tri": 1.2, "p": 1.7, "vi_tri": "Bảng 1"}, "ngoài [0;1]"),
    ({"ket_cuc": "A", "chi_so": "MD", "gia_tri": 1.2, "vi_tri": "Bảng 1",
      "trich_ngan": "một hai ba bốn năm sáu bảy tám chín mười mười một mười hai mười ba"}, "15 từ"),
])
def test_con_so_sai_bi_chan(ket_qua, mau):
    loi, _cb, _k = D.kiem_ho_so(_hs(ket_qua=[ket_qua]), HOM_NAY, XN.kiem_tieu_de)
    assert any(mau in x for x in loi), loi


def test_thieu_muc_la_partial_khong_chan():
    loi, cb, kiem = D.kiem_ho_so(_hs(han_che="", phuong_phap={"thiet_ke": "SR"}), HOM_NAY, XN.kiem_tieu_de)
    assert loi == [] and kiem["do_day_du"] == "partial" and "han_che" in kiem["thieu_muc"] and cb


def test_guideline_can_khuyen_cao_co_muc_nguyen_ban():
    g = _hs(loai_tai_lieu="guideline", ket_qua=[], phuong_phap={"thiet_ke": "Guideline ESC, hệ Class/LOE"},
            khuyen_cao=[{"tom_tat": "Dùng SGLT2i cho suy tim EF giảm", "muc": "", "vi_tri": "Bảng 5"}])
    loi, _cb, _k = D.kiem_ho_so(g, HOM_NAY, XN.kiem_tieu_de)
    assert any("NGUYÊN BẢN" in x for x in loi)
    g["khuyen_cao"][0]["muc"] = "Class I, LOE A"
    loi, _cb, kiem = D.kiem_ho_so(g, HOM_NAY, XN.kiem_tieu_de)
    assert loi == [] and kiem["do_day_du"] == "full"


# ── nạp ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def kho(tmp_path):
    k = tmp_path / "toan_van_oa"
    k.mkdir()
    return k


def test_chay_thu_khong_ghi(kho):
    ma, _ = D.nap(_hs(), ghi=False, xac_minh=_xm(), kho=kho, hom_nay=HOM_NAY, kiem_tieu_de=XN.kiem_tieu_de)
    assert ma == 0 and not (kho / "trinh_duyet").exists()


def test_ghi_tao_json_va_ban_doc_cho_goi_tuan(kho):
    ma, bao = D.nap(_hs(), ghi=True, xac_minh=_xm(), kho=kho, hom_nay=HOM_NAY, kiem_tieu_de=XN.kiem_tieu_de)
    assert ma == 0, bao
    hs = json.loads((kho / "trinh_duyet" / "PMID-42751933.json").read_text(encoding="utf-8"))
    assert hs["trang_thai"] == "CANDIDATE" and hs["kiem"]["do_day_du"] == "full" and hs["kiem"]["xac_minh"]["ket_qua"] == "xac_minh_duoc"
    md = (kho / "doc_sau" / "PMID-42751933.md").read_text(encoding="utf-8")
    assert "TRÌNH DUYỆT CÓ BÁC SĨ" in md and "KHÔNG nguyên văn" in md and "RR 1.85 (95% CI 1.32–2.59)" in md and "[Hình 2]" in md
    assert "Cần bác sĩ kiểm chứng" in md
    ma2, bao2 = D.nap(_hs(), ghi=True, xac_minh=_xm(), kho=kho, hom_nay=HOM_NAY, kiem_tieu_de=XN.kiem_tieu_de)
    assert ma2 == 0 and any("bản cũ giữ" in x for x in bao2) and list((kho / "trinh_duyet").glob("PMID-42751933.*.json.cu"))


@pytest.mark.parametrize("xm, ma", [(_xm("bi_rut_bai"), 3), (_xm("khong_khop"), 3), (_xm(title="A different article entirely about gout"), 3),
                                    (None, 2)])
def test_khong_xac_minh_duoc_thi_khong_ghi(kho, xm, ma):
    m, bao = D.nap(_hs(), ghi=True, xac_minh=xm, kho=kho, hom_nay=HOM_NAY, kiem_tieu_de=XN.kiem_tieu_de)
    assert m == ma, bao
    assert not list(kho.rglob("*.json")) and not list(kho.rglob("*.md"))


def test_bai_da_co_oa_thi_tu_choi(kho):
    (kho / "PMID-42751933_PMC1.xml").write_text("<x/>", encoding="utf-8", newline="\n")
    ma, bao = D.nap(_hs(), ghi=True, xac_minh=_xm(), kho=kho, hom_nay=HOM_NAY, kiem_tieu_de=XN.kiem_tieu_de)
    assert ma == 3 and any("OA" in x for x in bao)


@pytest.mark.parametrize("td", ["Chờ một chút...", "Thực hiện xác minh bảo mật", "Xác minh bạn là con người", "Please wait",
                                "Lỗi 1020"])
def test_cong_xac_nhan_trinh_duyet_tu_choi_tieu_de_chan_tieng_viet(td):
    """Trình duyệt của app chạy giao diện tiếng Việt (đo 02/10/2026) — sổ bằng chứng URL cũng không được nhận các tiêu đề này."""
    assert XN.kiem_tieu_de(td) is not None


def test_huong_dan_cam_claude_vuot_chan():
    assert "KHÔNG bấm" in D.HUONG_DAN and "KHÔNG giải CAPTCHA" in D.HUONG_DAN and "KHÔNG gõ tài khoản" in D.HUONG_DAN
    assert "crypto.subtle.digest" in D.HUONG_DAN


# ── nối dây chuyền ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_doc_sau_dem_ban_doc_trinh_duyet(kho, monkeypatch, capsys):
    ds = _nap("_t_dtv_ds", "doc_sau_toan_van.py")
    (kho / "trinh_duyet").mkdir()
    (kho / "trinh_duyet" / "PMID-42751933.json").write_text(json.dumps({"kiem": {"do_day_du": "partial"}}), encoding="utf-8",
                                                            newline="\n")
    monkeypatch.setattr(ds, "KHO", kho)
    monkeypatch.setattr(sys, "argv", ["x", "--pmid", "42751933", "42377292"])
    assert ds.main() == 0
    ra = capsys.readouterr().out
    assert "◑ 42751933" in ra and "độ đầy đủ partial" in ra and "1 bài đọc qua trình duyệt" in ra and "Chỉ tóm tắt: 42377292" in ra
    assert "doc_toan_van_co_nguoi.py --pmid 42377292" in ra


def test_giac_quan_the_tuan(tmp_path):
    tdx = _nap("_t_dtv_tdxv", "tu_de_xuat_viec.py")
    q = tmp_path / "queue"
    q.mkdir()
    (q / "tuan-2026-W40.md").write_text("## ⓶ BẢY THẺ\nPMID 42377292 · PMID 42751933\n## ⓷ GIỮ\n", encoding="utf-8", newline="\n")
    dash = tmp_path / "EBM-Dashboards"
    (dash / "toan_van_oa").mkdir(parents=True)
    homnay = date.fromtimestamp(time.time())
    ra = tdx.giac_quan_toan_van_the_tuan(q, dash, homnay)
    assert len(ra) == 1 and "2/2 thẻ gói tuan-2026-W40" in ra[0][1] and "doc_toan_van_co_nguoi.py --queue" in ra[0][2]
    for pm in ("42377292", "42751933"):
        (dash / "toan_van_oa" / f"PMID-{pm}_PMC1.xml").write_text("<x/>", encoding="utf-8", newline="\n")
    assert tdx.giac_quan_toan_van_the_tuan(q, dash, homnay) == []
    cu = time.time() - 20 * 86400
    (dash / "toan_van_oa" / "PMID-42377292_PMC1.xml").unlink()
    os.utime(q / "tuan-2026-W40.md", (cu, cu))
    assert tdx.giac_quan_toan_van_the_tuan(q, dash, homnay) == [], "gói > 14 ngày không nhắc"
    truoc = len(tdx._GIAC_QUAN_CHET)
    assert tdx.giac_quan_toan_van_the_tuan(tmp_path / "khong-co", dash, homnay) == [] and len(tdx._GIAC_QUAN_CHET) == truoc + 1


def test_dinh_tuyen_doc_toan_van():
    sys.path.insert(0, str(TOOLS / "orchestrator"))
    it = _nap("_t_dtv_it", "orchestrator/intent.py")
    for cau in ("đọc toàn văn các thẻ tuần W40", "doc toan van bai bi chan bot", "lấy full text bài NEJM"):
        r = it.route(cau)
        assert (r.kind, r.target) == ("cong_cu", "tools/doc_toan_van_co_nguoi.py"), (cau, r)
    assert it.route("trang FDA chặn bot cần xác nhận").target == "tools/xac_nhan_trinh_duyet.py"
    assert it.route("tôi có bệnh nhân nam 60 tuổi, cần đọc toàn văn guideline ESC suy tim").kind == "clinical_case"


def test_han_doc_luc_dung_hang_so():
    assert D.HAN_DOC_LUC_NGAY == 14 and (HOM_NAY - timedelta(days=14)).isoformat() == "2026-09-18"
    loi, _cb, _k = D.kiem_ho_so(_hs(doc_luc="2026-09-18"), HOM_NAY, XN.kiem_tieu_de)
    assert loi == []


# ── 03/10/2026: điều khoản nhà xuất bản về AI/TDM ──────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("doi, url, ten", [
    ("10.1016/j.jacc.2026.05.033", "", "Elsevier"), ("", "https://www.sciencedirect.com/science/article/pii/S1", "Elsevier"),
    ("", "https://www.thelancet.com/journals/lancet/article/x", "Elsevier"), ("10.2337/dc26-sint", "", "ADA (American Diabetes Association)"),
    ("", "https://www.dynamed.com/topics/x", "EBSCO (DynaMed)"), ("10.1136/heartjnl-2025-326305", "https://heart.bmj.com/x", None),
])
def test_nxb_cua(doi, url, ten):
    assert D.nxb_cua(doi, url)[0] == ten


def test_phieu_xep_bai_elsevier_cho_bac_si_doc_truc_tiep_ke_ca_mien_phi():
    r = D.duong_doc("42377292", "chua_co", epmc=lambda **k: {"doi": "10.1016/j.jacc.2026.05.033", "fullTextUrlList": {"fullTextUrl": [
        {"availabilityCode": "F", "url": "https://www.jacc.org/doi/10.1016/j.jacc.2026.05.033"}]}})
    assert r["cach"] == "bac_si_doc_truc_tiep" and r["nxb"] == "Elsevier" and "TDM" in r["ly_do"]
    k = D.duong_doc("41672763", "chua_co", epmc=lambda **k: {"doi": "10.1136/heartjnl-2025-326305"},
                    doi_dich=lambda d: "https://heart.bmj.com/lookup/doi/" + d)
    assert k["cach"] == "trinh_duyet" and k["dieu_khoan"] == "chua_kiem"


@pytest.mark.parametrize("sua, mau", [
    ({"doi": "10.1016/j.jhep.2026.08.028", "url_doc": "https://www.journal-of-hepatology.eu/article/x"}, "Elsevier cấm"),
    ({"doi": "10.2337/dc26-s001", "url_doc": "https://diabetesjournals.org/care/article/49/x"}, "ADA"),
    ({"dieu_khoan": None}, "CHƯA KIỂM"),
    ({"dieu_khoan": {"url": "https://x.invalid/t", "doc_luc": "2026-10-02", "ket_luan": "cam"}}, "CHƯA KIỂM"),
    ({"dieu_khoan": {"url": "", "doc_luc": "2026-10-02", "ket_luan": "cho_phep"}}, "CHƯA KIỂM"),
])
def test_nap_tu_choi_theo_dieu_khoan_nxb(sua, mau):
    loi, _cb, _k = D.kiem_ho_so(_hs(**sua), HOM_NAY, XN.kiem_tieu_de)
    assert any(mau in x for x in loi), loi


def test_nap_nhan_khi_da_kiem_dieu_khoan_cho_phep():
    hs = _hs(dieu_khoan={"url": "https://nxb.invalid/terms", "doc_luc": "2026-10-03", "ket_luan": "cho_phep", "trich": "AI use permitted"})
    assert D.kiem_ho_so(hs, HOM_NAY, XN.kiem_tieu_de)[0] == []


def test_huong_dan_co_buoc_dieu_khoan():
    assert "2a. ĐIỀU KHOẢN NHÀ XUẤT BẢN" in D.HUONG_DAN and "2b. NXB CHƯA KIỂM" in D.HUONG_DAN
