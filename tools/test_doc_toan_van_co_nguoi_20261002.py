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
    hs = {"pmid": "42751933", "doi": "10.1080/07853890.2026.2600001", "tieu_de_bai": TIEU_DE,
          "url_doc": "https://www.tandfonline.com/doi/full/10.1080/07853890.2026.2600001",
          "tieu_de_trang": TIEU_DE + " - Taylor & Francis Online", "doc_luc": HOM_NAY.isoformat(),
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
        {"availabilityCode": "F", "url": "https://www.tandfonline.com/doi/full/10.1/b"}]}})
    assert mp["cach"] == "trinh_duyet" and mp["mien_phi"] and "Cloudflare" in mp["mien_do_duoc"]
    # (jacc.org là Elsevier, nejm.org/ahajournals.org vào bảng cấm 03/10/2026 ⇒ ca này dùng NXB NGOÀI bảng: T&F, Karger.)
    qua_doi = D.duong_doc("3", "chua_co", epmc=lambda **k: {"doi": "10.1/c"}, doi_dich=lambda d: "https://karger.com/doi/" + d)
    assert qua_doi["cach"] == "trinh_duyet" and qua_doi["mien"] == "karger.com" and not qua_doi["mien_phi"]

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
    ("", "https://www.dynamed.com/topics/x", "EBSCO (DynaMed)"), ("10.1136/heartjnl-2025-326305", "https://heart.bmj.com/x", "BMJ Publishing Group"),
    ("10.1080/07853890.2026.2600001", "https://www.tandfonline.com/doi/full/x", None),
])
def test_nxb_cua(doi, url, ten):
    assert D.nxb_cua(doi, url)[0] == ten


def test_phieu_xep_bai_elsevier_cho_bac_si_doc_truc_tiep_ke_ca_mien_phi():
    r = D.duong_doc("42377292", "chua_co", epmc=lambda **k: {"doi": "10.1016/j.jacc.2026.05.033", "fullTextUrlList": {"fullTextUrl": [
        {"availabilityCode": "F", "url": "https://www.jacc.org/doi/10.1016/j.jacc.2026.05.033"}]}})
    assert r["cach"] == "bac_si_doc_truc_tiep" and r["nxb"] == "Elsevier" and "TDM" in r["ly_do"]
    k = D.duong_doc("41672763", "chua_co", epmc=lambda **k: {"doi": "10.1080/07853890.2026.2600001"},
                    doi_dich=lambda d: "https://www.tandfonline.com/doi/full/" + d)
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


def test_doctrine_day_agent_cung_bang_dieu_khoan():
    """03/10/2026 — doctrine `_CONNECTOR-CHUNG-CU.md` §2septies phải nêu ĐỦ mọi NXB «cấm» của bảng (CLAUDE.md §6.4)."""
    van_ban = (TOOLS.parent / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md").read_text(encoding="utf-8")
    assert D.lech_doctrine(van_ban) == []


def test_lech_doctrine_bat_bang_moi_va_doctrine_cu(monkeypatch):
    van_ban = (TOOLS.parent / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md").read_text(encoding="utf-8")
    # NXB CHƯA có trong bảng (Karger, 10.1159/ — chưa kiểm 03/10/2026; trước đó ví dụ này là Springer Nature, nay đã vào bảng).
    monkeypatch.setitem(D.DIEU_KHOAN_NXB, "Karger", {"ket_luan": "cam", "doi": ("10.1159/",), "mien": ()})
    assert any("Karger" in x for x in D.lech_doctrine(van_ban))
    assert D.lech_doctrine(van_ban.replace("## 2septies. ", "## 2x. ")) == ["doctrine mất §2septies (điều khoản NXB trước toàn văn)"]


def test_bang_dieu_khoan_ghi_dung_ngoai_le_va_loai_nguon():
    """03/10/2026 — kiểm độc lập đọc lại văn bản gốc: câu trích Elsevier từng bỏ mất mệnh đề ngoại lệ («except … relevant
    license»), scopus.com không nằm trong miền Elsevier dù doctrine cấm mở trang Scopus, và nguồn của EBSCO là TÓM TẮT của thư
    viện UBC chứ không phải điều khoản của chính EBSCO."""
    e = D.DIEU_KHOAN_NXB["Elsevier"]
    assert "except" in e["trich"] and e.get("ngoai_le"), "câu trích Elsevier bỏ mất mệnh đề ngoại lệ"
    # 03/10/2026 (tối): Scopus tách thành khoá riêng «Scopus (Elsevier)» (điều khoản riêng 16/09/2026 + uỷ quyền làn Chrome riêng của
    # bác sĩ) — vẫn là «cấm»; điều cần giữ là trang Scopus KHÔNG bao giờ rơi vào «chưa kiểm».
    ten, dk = D.nxb_cua("", "https://www.scopus.com/results/results.uri")
    assert ten == "Scopus (Elsevier)" and dk["ket_luan"] == "cam"
    assert "UBC" in D.DIEU_KHOAN_NXB["EBSCO (DynaMed)"].get("loai_nguon", ""), "nguồn EBSCO là tóm tắt của thư viện — ghi rõ"


# ── 03/10/2026: «bác sĩ đã đọc trực tiếp» — NXB cấm AI/TDM, bác sĩ tự đọc rồi ghi KẾT LUẬN (không phải nội dung bài) ───────────
PM_BS = "42377292"
GHI_CHU_BS = "Đã đọc toàn văn: kết luận khớp tóm tắt, giữ đề xuất hiện tại"


def test_bac_si_da_doc_ghi_duoc_va_thanh_da_phu(kho):
    ma, bao = D.danh_dau_bac_si_da_doc(PM_BS, "  " + GHI_CHU_BS + "  ", ghi=True, kho=kho, hom_nay=HOM_NAY)
    assert ma == 0, bao
    dong = (kho / "trinh_duyet" / "bac-si-da-doc.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(x) for x in dong] == [{"pmid": PM_BS, "ngay": "2026-10-02", "ghi_chu": GHI_CHU_BS,
                                               "nguon": "bac_si_doc_truc_tiep"}], "ghi_chu phải strip; ngày ISO; nguồn cố định"
    assert D.bao_phu_cuc_bo([PM_BS, "10000009"], kho, HOM_NAY) == {PM_BS: "bac_si_da_doc_truc_tiep", "10000009": "chua_co"}
    assert "bac_si_da_doc_truc_tiep" in D.TRANG_THAI_DA_PHU and "bac_si_da_doc_truc_tiep" not in D.TRANG_THAI_MAY_CO_TOAN_VAN


def test_bac_si_da_doc_xet_truoc_khong_truy_cap_va_khong_het_han(kho):
    (kho / "trinh_duyet").mkdir()
    (kho / "trinh_duyet" / "khong-truy-cap.jsonl").write_text(
        json.dumps({"pmid": PM_BS, "ngay": "2026-10-01", "ly_do": "đòi mua bài"}) + "\n", encoding="utf-8", newline="\n")
    assert D.bao_phu_cuc_bo([PM_BS], kho, HOM_NAY) == {PM_BS: "khong_truy_cap"}
    assert D.danh_dau_bac_si_da_doc(PM_BS, GHI_CHU_BS, ghi=True, kho=kho, hom_nay=HOM_NAY)[0] == 0
    assert D.bao_phu_cuc_bo([PM_BS], kho, HOM_NAY) == {PM_BS: "bac_si_da_doc_truc_tiep"}, "phải xét TRƯỚC khong_truy_cap"
    assert D.bao_phu_cuc_bo([PM_BS], kho, HOM_NAY + timedelta(days=400)) == {PM_BS: "bac_si_da_doc_truc_tiep"}, "KHÔNG hết hạn"
    # Bản ghi THẬT SỰ cũ 400 ngày, đọc với «hôm nay» mặc định — bắt cả kiểu hết hạn dùng date.today() lẫn dùng hom_nay truyền vào.
    pm_cu = "10000400"
    assert D.danh_dau_bac_si_da_doc(pm_cu, GHI_CHU_BS, ghi=True, kho=kho, hom_nay=date.today() - timedelta(days=400))[0] == 0
    assert D.bao_phu_cuc_bo([pm_cu], kho) == {pm_cu: "bac_si_da_doc_truc_tiep"}, "bản ghi 400 ngày tuổi vẫn phải còn hiệu lực"


@pytest.mark.parametrize("ghi_chu, mau", [
    (None, "bắt buộc"), ("", "bắt buộc"), ("   ok  ", "bắt buộc"), ("x" * 301, "KHÔNG chép nội dung bài"),
    ("Đã đọc, liên hệ bn@example.com để bàn thêm", "KHÔNG PII"),
    ("Đã đọc, gọi 0912345678 nếu cần", "KHÔNG PII"),  # bimat-mien: số điện thoại GIẢ — fixture kiểm luật chặn PII của ghi chú
])
def test_bac_si_da_doc_tu_choi_khong_ghi(kho, ghi_chu, mau):
    ma, bao = D.danh_dau_bac_si_da_doc(PM_BS, ghi_chu, ghi=True, kho=kho, hom_nay=HOM_NAY)
    assert ma == 3 and any(mau in x for x in bao), bao
    assert not (kho / "trinh_duyet").exists() and D.bao_phu_cuc_bo([PM_BS], kho, HOM_NAY) == {PM_BS: "chua_co"}


def test_bac_si_da_doc_bien_do_dai_va_pmid_sai(kho):
    assert D.kiem_ghi_chu_bac_si("x" * 5) == [] and D.kiem_ghi_chu_bac_si("x" * 300) == []
    assert D.kiem_ghi_chu_bac_si("x" * 4) and D.kiem_ghi_chu_bac_si("x" * 301)
    ma, bao = D.danh_dau_bac_si_da_doc("123", GHI_CHU_BS, ghi=True, kho=kho, hom_nay=HOM_NAY)
    assert ma == 3 and any("sai dạng" in x for x in bao) and not (kho / "trinh_duyet").exists()


def test_bac_si_da_doc_chay_thu_khong_ghi_va_kho_vang_khong_tu_tao(tmp_path, kho):
    ma, bao = D.danh_dau_bac_si_da_doc(PM_BS, GHI_CHU_BS, ghi=False, kho=kho, hom_nay=HOM_NAY)
    assert ma == 0 and any("chạy thử" in x for x in bao) and not (kho / "trinh_duyet").exists()
    vang = tmp_path / "khong-co-kho"
    ma2, bao2 = D.danh_dau_bac_si_da_doc(PM_BS, GHI_CHU_BS, ghi=True, kho=vang, hom_nay=HOM_NAY)
    assert ma2 == 2 and any("KHÔNG ĐO ĐƯỢC" in x for x in bao2) and not vang.exists()


def test_bac_si_da_doc_qua_cli(kho, monkeypatch, capsys):
    monkeypatch.setattr(D, "KHO", kho)
    assert D.main(["--bac-si-da-doc", PM_BS]) == 3, "thiếu --ghi-chu phải bị từ chối"
    assert D.main(["--bac-si-da-doc", PM_BS, "--ghi-chu", GHI_CHU_BS]) == 0 and not (kho / "trinh_duyet").exists()
    assert D.main(["--bac-si-da-doc", PM_BS, "--ghi-chu", GHI_CHU_BS, "--ghi"]) == 0
    assert (kho / "trinh_duyet" / "bac-si-da-doc.jsonl").exists()
    capsys.readouterr()


def test_phieu_tach_may_co_toan_van_va_bac_si_doc(kho, capsys):
    D.in_phieu([{"pmid": "10000001", "cach": "oa_xml"}, {"pmid": PM_BS, "cach": "bac_si_da_doc_truc_tiep"},
                {"pmid": "10000003", "cach": "chua_co"}])
    ra = capsys.readouterr().out
    assert "1/3 bài máy có toàn văn + 1 bài bác sĩ đọc trực tiếp (máy KHÔNG có toàn văn" in ra
    assert "BÁC SĨ ĐÃ ĐỌC TRỰC TIẾP" in ra and PM_BS in ra
    assert D.danh_dau_bac_si_da_doc(PM_BS, GHI_CHU_BS, ghi=True, kho=kho, hom_nay=HOM_NAY)[0] == 0
    phieu = D.lap_phieu([PM_BS], ngoai_tuyen=False, epmc=lambda **k: pytest.fail("bài đã phủ không được tra mạng"),
                        kho=kho, hom_nay=HOM_NAY)
    assert phieu == [{"pmid": PM_BS, "cach": "bac_si_da_doc_truc_tiep"}], "không được rơi vào nhóm CHỜ «bac_si_doc_truc_tiep»"


def test_giac_quan_the_tuan_khong_dem_the_bac_si_da_doc(tmp_path):
    tdx = _nap("_t_dtv_tdxv_bs", "tu_de_xuat_viec.py")
    q = tmp_path / "queue"
    q.mkdir()
    (q / "tuan-2026-W40.md").write_text(f"## ⓶ BẢY THẺ\nPMID {PM_BS} · PMID 42751933\n## ⓷ GIỮ\n", encoding="utf-8", newline="\n")
    dash = tmp_path / "EBM-Dashboards"
    kho_t = dash / "toan_van_oa"
    kho_t.mkdir(parents=True)
    (kho_t / "PMID-42751933_PMC1.xml").write_text("<x/>", encoding="utf-8", newline="\n")
    homnay = date.fromtimestamp(time.time())
    ra = tdx.giac_quan_toan_van_the_tuan(q, dash, homnay)
    assert len(ra) == 1 and "1/2 thẻ" in ra[0][1] and "--bac-si-da-doc" in ra[0][1]
    assert D.danh_dau_bac_si_da_doc(PM_BS, GHI_CHU_BS, ghi=True, kho=kho_t, hom_nay=homnay)[0] == 0
    assert tdx.giac_quan_toan_van_the_tuan(q, dash, homnay) == [], "thẻ bác sĩ đã đọc trực tiếp vẫn bị đếm «chỉ tóm tắt»"


def test_huong_dan_co_buoc_bac_si_da_doc():
    h = D.HUONG_DAN
    assert "--bac-si-da-doc <PMID> --ghi-chu" in h and "--ghi" in h and "KHÔNG dán nội dung bài Elsevier/ADA vào chat" in h
    assert "5–300 ký tự" in h and "{GHI_CHU" not in h


# ── 03/10/2026: BÁC SĨ UỶ QUYỀN MÁY ĐỌC — quyết định của bác sĩ (chủ hệ thống) cho Claude đọc bài NXB «cấm» bác sĩ có quyền truy cập ──
# Điều khoản NXB KHÔNG đổi; công cụ chỉ ghi và tôn trọng QUYẾT ĐỊNH của bác sĩ (tệp ngoài git), fail-closed khi tệp vắng/hỏng/hết hạn.
NGAY_UQ = "2026-10-02"
CAN_CU_UQ = "Vậy hãy chỉnh sửa lại để máy đọc toàn văn và tóm tắt cho tôi"
ADA = "ADA (American Diabetes Association)"
DOI_E, URL_E = "10.1016/j.jacc.2026.05.033", "https://www.jacc.org/doi/10.1016/j.jacc.2026.05.033"


@pytest.fixture(autouse=True)
def _co_lap_tep_uy_quyen(monkeypatch, tmp_path):
    """Mọi test của tệp này KHÔNG được đọc tệp quyết định THẬT ở EBM-Dashboards/ (bác sĩ ghi nó sau khi PR gộp): đường mặc định
    tính lúc gọi từ D.DASH ⇒ trỏ D.DASH vào một thư mục tạm chưa có tệp."""
    monkeypatch.setattr(D, "DASH", tmp_path / "EBM-Dashboards-gia")


def _muc_uq(**sua) -> dict:
    m = {"nxb": "Elsevier", "ngay": NGAY_UQ, "can_cu": CAN_CU_UQ, "pham_vi": "đọc qua Chrome của bác sĩ, chỉ hồ sơ tóm lược"}
    m.update(sua)
    return m


def _tep_uq(tmp_path, *muc, noi_dung: str | None = None) -> Path:
    t = tmp_path / "uq" / "dieu-khoan-bac-si-uy-quyen.json"
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_text(noi_dung if noi_dung is not None else json.dumps({"_about": "thử", "muc": list(muc)}, ensure_ascii=False),
                 encoding="utf-8", newline="\n")
    return t


def _hs_e(**dk) -> dict:
    kd = {"ket_luan": "bac_si_uy_quyen", "ngay_uy_quyen": NGAY_UQ}
    kd.update(dk)
    return _hs(doi=DOI_E, url_doc=URL_E, tieu_de_trang=TIEU_DE + " | JACC", dieu_khoan=kd)


@pytest.mark.parametrize("muc, noi_dung, mo_ta", [
    (None, None, "tệp vắng"),
    (None, "{hỏng", "tệp hỏng JSON"),
    (None, json.dumps({"muc": {"nxb": "Elsevier"}}), "muc không phải danh sách"),
    ([_muc_uq(het_han="2026-10-01")], None, "hết hạn hôm qua"),
    ([_muc_uq(nxb=ADA)], None, "uỷ quyền khác NXB"),
    ([_muc_uq(ngay="2026-10-09")], None, "ngày ở tương lai"),
    ([_muc_uq(can_cu="ok")], None, "căn cứ quá ngắn"),
    ([_muc_uq(het_han="mai")], None, "het_han sai dạng"),
    ([_muc_uq(ngay="03/10/2026")], None, "ngày sai dạng"),
])
def test_uy_quyen_vang_hong_het_han_khac_nxb_thi_tu_choi(tmp_path, muc, noi_dung, mo_ta):
    tep = (tmp_path / "khong-co.json") if muc is None and noi_dung is None else _tep_uq(tmp_path, *(muc or []), noi_dung=noi_dung)
    assert D.uy_quyen_bac_si("Elsevier", HOM_NAY, tep) is None, mo_ta
    loi, _cb, tt = D.kiem_ho_so(_hs_e(), HOM_NAY, XN.kiem_tieu_de, tep)
    assert any("Elsevier cấm" in x for x in loi) and "uy_quyen" not in tt, (mo_ta, loi)
    assert any("KHÔNG có uỷ quyền còn hiệu lực" in x for x in loi), "hồ sơ tự khai bac_si_uy_quyen mà không có uỷ quyền phải được nói rõ"


def test_khong_uy_quyen_giu_nguyen_thong_diep_cu(tmp_path):
    """Không uỷ quyền ⇒ thông điệp cũ NGUYÊN VĂN (đường hợp lệ, «bác sĩ đọc trực tiếp»)."""
    hs = _hs(doi=DOI_E, url_doc=URL_E)
    loi, _cb, _tt = D.kiem_ho_so(hs, HOM_NAY, XN.kiem_tieu_de, tmp_path / "khong-co.json")
    dk = D.DIEU_KHOAN_NXB["Elsevier"]
    assert (f"điều khoản Elsevier cấm dùng nội dung với công cụ AI/TDM (đọc {dk['doc_luc']}: {dk['nguon']}) — KHÔNG nạp; "
            f"bác sĩ đọc trực tiếp, đường hợp lệ: {dk['duong_hop_le']}") in loi


def test_uy_quyen_dung_va_ho_so_khai_dung_ngay_thi_nhan(tmp_path):
    tep = _tep_uq(tmp_path, _muc_uq())
    uq = D.uy_quyen_bac_si("Elsevier", HOM_NAY, tep)
    assert uq and uq["ngay"] == NGAY_UQ and uq["can_cu"] == CAN_CU_UQ
    loi, _cb, tt = D.kiem_ho_so(_hs_e(), HOM_NAY, XN.kiem_tieu_de, tep)
    assert loi == [] and tt["uy_quyen"]["nxb"] == "Elsevier" and tt["uy_quyen"]["ngay"] == NGAY_UQ, loi
    # Mọi kiểm khác GIỮ NGUYÊN với hồ sơ uỷ quyền: tiêu đề chặn, trích > 15 từ, chuỗi > 800, số ngoài CI, PII.
    for sua, mau in (({"tieu_de_trang": "Just a moment..."}, "CHẶN BOT"), ({"han_che": "x" * 900}, "nguyên văn"),
                     ({"ket_qua": [{**_hs()["ket_qua"][0], "gia_tri": 3.1}]}, "ngoài CI"),
                     ({"ghi_chu": "liên hệ bn@example.com"}, "định danh"),
                     ({"ket_qua": [{**_hs()["ket_qua"][0], "trich_ngan": " ".join(["từ"] * 16)}]}, "15 từ")):
        loi2, _c, _t = D.kiem_ho_so({**_hs_e(), **sua}, HOM_NAY, XN.kiem_tieu_de, tep)
        assert any(mau in x for x in loi2), (sua, loi2)


def test_uy_quyen_het_han_dung_ngay_van_hieu_luc_va_muc_moi_nhat_thang(tmp_path):
    tep = _tep_uq(tmp_path, _muc_uq(het_han=HOM_NAY.isoformat()))
    assert D.uy_quyen_bac_si("Elsevier", HOM_NAY, tep) is not None, "ngày het_han vẫn còn hiệu lực"
    assert D.uy_quyen_bac_si("Elsevier", HOM_NAY + timedelta(days=1), tep) is None, "qua het_han ⇒ hết uỷ quyền"
    tep2 = _tep_uq(tmp_path, _muc_uq(ngay="2026-09-30"), _muc_uq(ngay="2026-10-01"), _muc_uq(nxb=ADA, ngay=NGAY_UQ))
    assert D.uy_quyen_bac_si("Elsevier", HOM_NAY, tep2)["ngay"] == "2026-10-01"


@pytest.mark.parametrize("dk, mo_ta", [
    ({"ket_luan": "cho_phep"}, "ket_luan cho_phep"), ({"ket_luan": "giay_phep_cc"}, "ket_luan giay_phep_cc"),
    ({"ket_luan": None}, "thiếu ket_luan"), ({"ngay_uy_quyen": "2026-10-01"}, "ngày lệch tệp quyết định"),
    ({"ngay_uy_quyen": None}, "thiếu ngay_uy_quyen"),
])
def test_uy_quyen_dung_nhung_ho_so_khai_sai_thi_tu_choi(tmp_path, dk, mo_ta):
    tep = _tep_uq(tmp_path, _muc_uq())
    loi, _cb, tt = D.kiem_ho_so(_hs_e(**dk), HOM_NAY, XN.kiem_tieu_de, tep)
    assert any("Elsevier cấm" in x and "ĐÃ uỷ quyền máy đọc ngày 2026-10-02" in x for x in loi) and "uy_quyen" not in tt, (mo_ta, loi)


def test_nxb_chua_kiem_khai_bac_si_uy_quyen_van_tu_choi(tmp_path):
    """bac_si_uy_quyen CHỈ nhận ở nhánh NXB «cam» có uỷ quyền — NXB chưa kiểm vẫn chỉ cho_phep | giay_phep_cc."""
    tep = _tep_uq(tmp_path, _muc_uq())
    hs = _hs(dieu_khoan={"url": "https://nxb.invalid/terms", "doc_luc": "2026-10-02", "ket_luan": "bac_si_uy_quyen",
                         "ngay_uy_quyen": NGAY_UQ})
    loi, _cb, tt = D.kiem_ho_so(hs, HOM_NAY, XN.kiem_tieu_de, tep)
    assert any("CHƯA KIỂM" in x for x in loi) and "uy_quyen" not in tt, loi
    assert "bac_si_uy_quyen" not in D._KET_LUAN_DIEU_KHOAN_NHAN


def test_uy_quyen_duong_dan_mac_dinh_tinh_luc_goi(tmp_path, monkeypatch):
    dash = tmp_path / "dash-luc-goi"
    dash.mkdir()
    (dash / "dieu-khoan-bac-si-uy-quyen.json").write_text(json.dumps({"muc": [_muc_uq()]}, ensure_ascii=False), encoding="utf-8",
                                                          newline="\n")
    assert D.uy_quyen_bac_si("Elsevier", HOM_NAY) is None, "DASH tạm (autouse) chưa có tệp"
    monkeypatch.setattr(D, "DASH", dash)
    assert D.tep_uy_quyen_mac_dinh() == dash / "dieu-khoan-bac-si-uy-quyen.json"
    assert D.uy_quyen_bac_si("Elsevier", HOM_NAY)["ngay"] == NGAY_UQ
    assert D.kiem_ho_so(_hs_e(), HOM_NAY, XN.kiem_tieu_de)[0] == []


def test_phieu_doi_nhan_khi_co_uy_quyen(tmp_path, kho, capsys):
    epmc = lambda **k: {"doi": DOI_E, "title": "Bài JACC thử", "fullTextUrlList": {"fullTextUrl": [  # noqa: E731
        {"availabilityCode": "F", "url": URL_E}]}}
    khong = D.duong_doc("42377292", "chua_co", epmc=epmc, hom_nay=HOM_NAY, tep_uy_quyen=tmp_path / "khong-co.json")
    assert khong["cach"] == "bac_si_doc_truc_tiep", "không uỷ quyền ⇒ như cũ"
    ada = D.duong_doc("42377292", "chua_co", epmc=epmc, hom_nay=HOM_NAY, tep_uy_quyen=_tep_uq(tmp_path, _muc_uq(nxb=ADA)))
    assert ada["cach"] == "bac_si_doc_truc_tiep", "uỷ quyền ADA không mở bài Elsevier"
    tep = _tep_uq(tmp_path, _muc_uq())
    r = D.duong_doc("42377292", "chua_co", epmc=epmc, hom_nay=HOM_NAY, tep_uy_quyen=tep)
    assert r["cach"] == "trinh_duyet" and r["dieu_khoan"] == "bac_si_uy_quyen" and r["nxb"] == "Elsevier"
    assert r["ngay_uy_quyen"] == NGAY_UQ and r["nhan_dieu_khoan"] == "BÁC SĨ UỶ QUYỀN MÁY ĐỌC (2026-10-02)"
    phieu = D.lap_phieu(["42377292"], ngoai_tuyen=False, kho=kho, hom_nay=HOM_NAY, epmc=epmc, tep_uy_quyen=tep)
    assert phieu[0]["cach"] == "trinh_duyet" and phieu[0]["dieu_khoan"] == "bac_si_uy_quyen"
    D.in_phieu(phieu)
    ra = capsys.readouterr().out
    assert "CẦN TRÌNH DUYỆT CÓ BÁC SĨ" in ra and "BÁC SĨ UỶ QUYỀN MÁY ĐỌC (2026-10-02)" in ra and "KHÔNG đổi" in ra
    assert "BÁC SĨ ĐỌC TRỰC TIẾP —" not in ra and "CHƯA KIỂM" not in ra


def test_ban_doc_ho_so_uy_quyen_co_dong_quyet_dinh(tmp_path, kho):
    tep = _tep_uq(tmp_path, _muc_uq())
    ma, bao = D.nap(_hs_e(), ghi=True, xac_minh=_xm(), kho=kho, hom_nay=HOM_NAY, kiem_tieu_de=XN.kiem_tieu_de, tep_uy_quyen=tep)
    assert ma == 0 and any("QUYẾT ĐỊNH của bác sĩ" in x for x in bao), bao
    md = (kho / "doc_sau" / "PMID-42751933.md").read_text(encoding="utf-8")
    dong = ("Đọc theo QUYẾT ĐỊNH của bác sĩ ngày 2026-10-02 (điều khoản Elsevier chỉ cho dùng với AI khi có giấy phép/thuê bao/"
            "sự cho phép — trách nhiệm điều khoản thuộc bác sĩ).")
    than = [x for x in md.splitlines()[1:] if x.strip()]
    assert than[0] == "> " + dong, "dòng quyết định phải là dòng ĐẦU của thân bản đọc"
    hs = json.loads((kho / "trinh_duyet" / "PMID-42751933.json").read_text(encoding="utf-8"))
    assert hs["kiem"]["uy_quyen"]["ngay"] == NGAY_UQ and hs["kiem"]["uy_quyen"]["can_cu"] == CAN_CU_UQ
    # Hồ sơ KHÔNG uỷ quyền (NXB đã kiểm giấy phép CC) ⇒ không có dòng quyết định.
    kho2 = tmp_path / "kho2"
    kho2.mkdir()
    assert D.nap(_hs(), ghi=True, xac_minh=_xm(), kho=kho2, hom_nay=HOM_NAY, kiem_tieu_de=XN.kiem_tieu_de)[0] == 0
    assert "QUYẾT ĐỊNH của bác sĩ" not in (kho2 / "doc_sau" / "PMID-42751933.md").read_text(encoding="utf-8")


def test_cli_ghi_uy_quyen_chay_thu_khong_ghi(tmp_path, monkeypatch, capsys):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    monkeypatch.setattr(D, "DASH", dash)
    assert D.main(["--ghi-uy-quyen", "Elsevier", "--can-cu", CAN_CU_UQ]) == 0
    ra = capsys.readouterr().out
    assert "quyết định của bác sĩ — trách nhiệm điều khoản thuộc bác sĩ" in ra and "KHÔNG phải «NXB cho phép»" in ra
    assert "chạy thử" in ra and not (dash / "dieu-khoan-bac-si-uy-quyen.json").exists()


@pytest.mark.parametrize("nxb", ["Karger", "elsevier", "ADA", "NXB thử cho phép"])
def test_cli_ghi_uy_quyen_tu_choi_nxb_khong_phai_khoa_cam(tmp_path, monkeypatch, capsys, nxb):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    monkeypatch.setattr(D, "DASH", dash)
    monkeypatch.setitem(D.DIEU_KHOAN_NXB, "NXB thử cho phép", {"ket_luan": "cho_phep", "doi": ("10.9999/",), "mien": ()})
    assert D.main(["--ghi-uy-quyen", nxb, "--can-cu", CAN_CU_UQ, "--ghi"]) == 3
    assert "không phải khoá «cấm»" in capsys.readouterr().out and not (dash / "dieu-khoan-bac-si-uy-quyen.json").exists()


@pytest.mark.parametrize("can_cu", [None, "", "ok bác sĩ", "   cho đọc   "])
def test_cli_ghi_uy_quyen_tu_choi_can_cu_ngan(tmp_path, monkeypatch, capsys, can_cu):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    monkeypatch.setattr(D, "DASH", dash)
    argv = ["--ghi-uy-quyen", "Elsevier", "--ghi"] + ([] if can_cu is None else ["--can-cu", can_cu])
    assert D.main(argv) == 3
    assert "--can-cu bắt buộc" in capsys.readouterr().out and not (dash / "dieu-khoan-bac-si-uy-quyen.json").exists()


def test_ghi_uy_quyen_ghi_that_noi_tiep_khong_de_tep_hong_khong_tao_thu_muc(tmp_path):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    tep = dash / "dieu-khoan-bac-si-uy-quyen.json"
    ma, bao = D.ghi_uy_quyen("Elsevier", CAN_CU_UQ, ghi=True, tep=tep, hom_nay=HOM_NAY)
    assert ma == 0, bao
    d = json.loads(tep.read_text(encoding="utf-8"))
    assert "KHÔNG phải «NXB cho phép»" in d["_about"] and len(d["muc"]) == 1
    m = d["muc"][0]
    assert (m["nxb"], m["ngay"], m["can_cu"]) == ("Elsevier", NGAY_UQ, CAN_CU_UQ) and "Chrome của bác sĩ" in m["pham_vi"]
    assert m["dieu_khoan_nxb_khong_doi"]["nguon"] == D.DIEU_KHOAN_NXB["Elsevier"]["nguon"]
    assert D.uy_quyen_bac_si("Elsevier", HOM_NAY, tep)["ngay"] == NGAY_UQ
    assert D.ghi_uy_quyen(ADA, CAN_CU_UQ, ghi=True, tep=tep, hom_nay=HOM_NAY, het_han="2027-10-02")[0] == 0
    d2 = json.loads(tep.read_text(encoding="utf-8"))
    assert [x["nxb"] for x in d2["muc"]] == ["Elsevier", ADA] and d2["muc"][1]["het_han"] == "2027-10-02"
    assert D.ghi_uy_quyen("Elsevier", CAN_CU_UQ, ghi=True, tep=tep, hom_nay=HOM_NAY, het_han="2026-10-01")[0] == 3
    tep.write_text("{hỏng", encoding="utf-8", newline="\n")
    ma3, bao3 = D.ghi_uy_quyen("Elsevier", CAN_CU_UQ, ghi=True, tep=tep, hom_nay=HOM_NAY)
    assert ma3 == 3 and tep.read_text(encoding="utf-8") == "{hỏng" and any("KHÔNG ghi đè" in x for x in bao3)
    vang = tmp_path / "khong-co" / "dieu-khoan-bac-si-uy-quyen.json"
    assert D.ghi_uy_quyen("Elsevier", CAN_CU_UQ, ghi=True, tep=vang, hom_nay=HOM_NAY)[0] == 2 and not vang.parent.exists()


def test_huong_dan_va_doctrine_co_uy_quyen_bac_si():
    assert "--ghi-uy-quyen" in D.HUONG_DAN and "BÁC SĨ UỶ QUYỀN MÁY ĐỌC" in D.HUONG_DAN and "KHÔNG phải «NXB cho phép»" in D.HUONG_DAN
    van_ban = (TOOLS.parent / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md").read_text(encoding="utf-8")
    i = van_ban.find("## 2septies. ")
    muc = van_ban[i:van_ban.find("\n## ", i + 5)]
    assert "**Bác sĩ uỷ quyền máy đọc (03/10/2026):**" in muc and "`EBM-Dashboards/dieu-khoan-bac-si-uy-quyen.json`" in muc
    assert "KHÔNG phải «NXB cho phép»" in muc and D.lech_doctrine(van_ban) == []


def test_bai_da_co_ban_tdm_cua_nxb_thi_khong_nap_lan_trinh_duyet(kho):
    """03/10/2026: đã có PDF qua kênh TDM của NXB (`PMID-<n>_WTDM.pdf`) ⇒ không mở bài bằng trình duyệt nữa."""
    (kho / "PMID-42751933_WTDM.pdf").write_bytes(b"%PDF-1.4")
    ma, bao = D.nap(_hs(), ghi=True, xac_minh=_xm(), kho=kho, hom_nay=HOM_NAY, kiem_tieu_de=XN.kiem_tieu_de)
    assert ma == 3 and any("kênh TDM" in x for x in bao), bao
    assert not (kho / "trinh_duyet").exists()
