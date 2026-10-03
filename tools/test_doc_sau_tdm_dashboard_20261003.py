#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy 03/10/2026 — `tools/doc_sau_toan_van.py`: nhận PDF kênh TDM (`PMID-<n>_WTDM.pdf`), chế độ --dashboard/--chi-apply
đếm theo đơn vị PMID, và KHÔNG ghi đè bản đọc của làn trình duyệt có bác sĩ.

Ngoại tuyến: kho toàn văn + dashboard dựng trong tmp_path. Phần bóc PDF thuần được kiểm bằng trang giả (chạy cả trên lane CI
không cài pypdf); một test dùng PDF thật tự dựng (byte PDF tối giản) chỉ chạy khi máy có pypdf — skip CÓ KHAI BÁO."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


DS = _nap("_t_dstdm", "doc_sau_toan_van.py")

# ── nguyên liệu giả ─────────────────────────────────────────────────────────────────────────────────────────────────────
CAU_PP = ("Patients were randomized in a one to one ratio using a centralized computer system with allocation concealment "
          "maintained by an independent statistician who had no contact with the recruiting clinicians at any site.")
CAU_MU = ("The trial was double-blind, and the primary analysis followed the intention-to-treat principle including every "
          "participant who underwent randomization regardless of adherence to the assigned regimen during follow-up.")
CAU_KQ = ("During a median follow-up of four years the primary composite outcome occurred less often in the intervention "
          "group than in the control group with a hazard ratio of 0.77 (95% CI 0.62-0.96) after adjustment for centre.")
CAU_KQ2 = ("Among participants older than seventy years the effect on all-cause mortality was similar in direction with a "
           "relative risk of 0.85 (95% CI 0.70-1.03) and no evidence of interaction across the prespecified subgroups.")
CAU_HC = ("This study has several limitations because the open recruitment strategy in tertiary centres may limit the "
          "generalisability of these findings to community practice and to patients with milder disease at baseline.")
CAU_TT = ("The trial was funded by the National Research Agency grant 2019-77 and the funder had no role in the design, "
          "conduct, analysis or reporting of the study; correspondence to trial.office@example.org for data requests.")
CAU_TLTK = ("Smith J, Jones K. Prior cohort of statin users showed OR 2.31 (95% CI 1.10-4.20) for hepatotoxicity. "
            "Lancet. 2019;380:1509-15.")
DEM = ("Background prose that repeats a neutral statement about the clinical context of the trial for padding only. ")


def _trang_gia() -> list[str]:
    """Bốn trang văn bản như pypdf trả: dòng ngắn, tiêu đề mục đứng riêng một dòng, có mục tài liệu tham khảo."""
    def _dong(vb: str, rong: int = 70) -> str:
        tu, dong, ra = vb.split(), "", []
        for t in tu:
            if len(dong) + len(t) + 1 > rong:
                ra.append(dong)
                dong = t
            else:
                dong = (dong + " " + t).strip()
        return "\n".join(ra + [dong])
    return [
        "Comparing two strategies in a randomized trial\nAbstract\n" + _dong(DEM * 6),
        "2 | METHODS\n" + _dong(CAU_PP + " The trial was registered as NCT01234567. " + CAU_MU + " " + DEM * 4),
        "3 | RESULTS\n" + _dong(CAU_KQ + " " + CAU_KQ2 + " " + DEM * 4)
        + "\n4 | DISCUSSION\n" + _dong(CAU_HC + " " + DEM * 2),
        "FUNDING INFORMATION\n" + _dong(CAU_TT) + "\nCONFLICT OF INTEREST\nNone.\nREFERENCES\n" + _dong(CAU_TLTK),
    ]


def _xml(tieu_de: str = "Bài thử JATS") -> str:
    return ("<pmc-articleset><article><front><journal-meta><journal-title-group><journal-title>Tạp chí thử</journal-title>"
            "</journal-title-group></journal-meta><article-meta><article-id pub-id-type=\"doi\">10.1000/thu.1</article-id>"
            f"<title-group><article-title>{tieu_de}</article-title></title-group><pub-date><year>2025</year></pub-date>"
            "</article-meta></front><body><sec><title>Methods</title><p>Randomised trial NCT07654321 in adults.</p></sec>"
            "<sec><title>Results</title><p>The hazard ratio was 0.80 (95% CI 0.70-0.91) for the primary outcome.</p>"
            "</sec></body></article></pmc-articleset>")


@pytest.fixture()
def dash(tmp_path):
    d = tmp_path / "EBM-Dashboards"
    (d / "toan_van_oa").mkdir(parents=True)
    return d


@pytest.fixture()
def pdf_gia(monkeypatch):
    """Thay bộ đọc PDF bằng trang giả — phần bóc thuần chạy được cả khi máy không có pypdf."""
    monkeypatch.setattr(DS, "_doc_pdf", lambda pdf: (_trang_gia(), "Comparing two strategies in a randomized trial"))


def _tep_pdf(kho: Path, pm: str) -> Path:
    t = kho / f"PMID-{pm}_WTDM.pdf"
    t.write_bytes(b"%PDF-1.4 gia")
    return t


def _trich(md: str) -> list[str]:
    return re.findall(r"«([^»]*)»", md)


def _so_tu(t: str) -> int:
    return len(t.replace("…", " ").split())


# ── PDF kênh TDM ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_tdm_sinh_ban_doc_ghi_nguon_co_ban_quyen(dash, pdf_gia):
    kho = dash / "toan_van_oa"
    _tep_pdf(kho, "20482606")
    loai, ghi_chu = DS.xu_ly_pmid("20482606", kho, lam_lai=True)
    assert loai == "vua_sinh_tdm", ghi_chu
    md = (kho / "doc_sau" / "PMID-20482606.md").read_text(encoding="utf-8")
    assert "kênh TDM của NXB (Wiley) — có bản quyền, KHÔNG phải OA" in md
    assert "PMID-20482606_WTDM.pdf" in md and "Cần bác sĩ kiểm chứng" in md
    assert "NCT01234567" in md                                   # mã đăng ký là dữ kiện
    assert "Phương pháp tr. 2" in md and "Kết quả tr. 3" in md and "Tài liệu tham khảo tr. 4" in md
    hs = md.split("## Hiệu số", 1)[1].split("\n## ", 1)[0]
    assert "tr. 3" in hs and "0.77 (95% CI 0.62-0.96)" in hs and "0.85 (95% CI 0.70-1.03)" in hs
    assert "2.31" not in md and "Lancet" not in md               # mục tài liệu tham khảo không phải hiệu số của bài
    pp = md.split("## Dấu hiệu phương pháp", 1)[1].split("\n## ", 1)[0]
    for nhan in ("Ngẫu nhiên hoá: tr. 2", "Che giấu phân bổ: tr. 2", "Làm mù: tr. 2", "ITT / per-protocol: tr. 2"):
        assert nhan in pp
    assert "Không bắt gặp:" in pp and "GRADE" in pp.split("Không bắt gặp:", 1)[1]
    assert "## Hạn chế tác giả tự khai" in md and "limitations" in md
    tt = md.split("## Tài trợ & xung đột lợi ích", 1)[1]
    assert "[CONFLICT OF INTEREST] — «None.»" in tt and "funded by the National Research Agency" in tt


def test_tdm_tran_15_tu_moi_lan_va_khong_chep_doan_van(dash, pdf_gia):
    """Bài có bản quyền: mọi trích ≤ 15 từ, và KHÔNG có chuỗi ≥ 16 từ liền nào của nguồn lọt vào bản đọc."""
    kho = dash / "toan_van_oa"
    _tep_pdf(kho, "20482606")
    DS.xu_ly_pmid("20482606", kho, lam_lai=True)
    md = (kho / "doc_sau" / "PMID-20482606.md").read_text(encoding="utf-8")
    trich = _trich(md)
    assert trich and all(_so_tu(t) <= 15 for t in trich), [t for t in trich if _so_tu(t) > 15]
    assert len(trich) <= sum(DS.TRAN_TRICH_PDF.values()) + len(DS.DAU_HIEU_PP)
    tu = " ".join(_trang_gia()).split()
    md_gon = " ".join(md.split())
    lot = [" ".join(tu[i:i + 16]) for i in range(len(tu) - 15) if " ".join(tu[i:i + 16]) in md_gon]
    assert not lot, lot[:2]
    for cau in (CAU_PP, CAU_KQ, CAU_HC, CAU_TT):
        assert cau not in md


def test_tran_trich_dong_bo_lam_trinh_duyet():
    """Hai làn đọc bài có bản quyền dùng CÙNG kỷ luật — đổi một bên mà quên bên kia thì đỏ."""
    dtv = _nap("_t_dstdm_dtv", "doc_toan_van_co_nguoi.py")
    assert DS.TRAN_TU_TRICH == dtv.TRAN_TU_TRICH == 15
    assert DS.TOI_THIEU_KY_TU_PDF == dtv.TOI_THIEU_KY_TU


def test_trich_ngan_cua_so_quanh_con_so_va_che_email():
    cau = " ".join(f"w{i}" for i in range(40)) + " HR 0.70 (95% CI 0.60-0.80) " + " ".join(f"z{i}" for i in range(30))
    t = DS._trich_ngan(cau, cau.index("HR"))
    assert _so_tu(t) <= 15 and "HR 0.70" in t and t.startswith("…") and t.endswith("…")
    assert DS._trich_ngan("Liên hệ tác giả qua ban.thu@example.org để xin dữ liệu.") == \
        "Liên hệ tác giả qua [email] để xin dữ liệu."
    assert "»" not in DS._trich_ngan("Trích «có ngoặc» trong bài.")


def test_muc_ngan_khong_nuot_than_bai():
    """Tiêu đề «Funding information» ở cột bên không được biến cả thân bài phía sau thành mục tài trợ."""
    than = ("Recommendation text continues here with an odds ratio of 1.90 (95% CI 1.20-3.00) for the outcome. " * 60)
    khoi = DS._khoi_pdf(["Funding information\nSociety of Something.\n" + than, "More body text " * 50])
    assert {k[0] for k in khoi if k[0] == "tai_tro"} == {"tai_tro"}
    assert sum(len(k[2]) for k in khoi if k[0] == "tai_tro") < DS.TRAN_KY_TU_MUC_NGAN["tai_tro"] + 200
    assert any(k[0] == "dau_bai" for k in khoi[1:])
    # quá trần thì trả về ĐÚNG mục đứng trước tiêu đề ngắn (ở đây: Kết quả), không phải luôn «dau_bai»
    khoi = DS._khoi_pdf(["RESULTS\nShort result line.\nFunding information\nSociety of Something.\n" + than])
    assert [k[0] for k in khoi] == ["ket_qua", "tai_tro", "ket_qua"] and "odds ratio" in khoi[-1][2]


def test_pdf_it_chu_la_loi_khong_sinh_ban_doc(dash, monkeypatch):
    kho = dash / "toan_van_oa"
    _tep_pdf(kho, "20482606")
    monkeypatch.setattr(DS, "_doc_pdf", lambda pdf: (["Trang bìa ngắn.", ""], ""))
    loai, ghi_chu = DS.xu_ly_pmid("20482606", kho, lam_lai=True)
    assert loai == "loi" and "< 3000" in ghi_chu
    assert not (kho / "doc_sau" / "PMID-20482606.md").exists()


def test_thieu_thu_vien_pdf_bao_ro_khong_gay(dash, monkeypatch, capsys):
    """Không có pypdf: báo «không đọc được PDF — thiếu thư viện», mã 0, không sinh bản đọc, không xếp «chỉ tóm tắt»."""
    kho = dash / "toan_van_oa"
    _tep_pdf(kho, "20482606")
    monkeypatch.setitem(sys.modules, "pypdf", None)   # import pypdf ⇒ ImportError
    with pytest.raises(DS.LoiDocPdf) as e:
        DS._doc_pdf(kho / "PMID-20482606_WTDM.pdf")
    assert e.value.ly_do == "thieu_thu_vien"
    assert DS.main(["--dashboard", "--dash", str(dash), "--pmid", "20482606"]) in (0, 2)
    assert DS.main(["--pmid", "20482606", "--dash", str(dash)]) == 0
    ra = capsys.readouterr().out
    assert "không đọc được PDF — thiếu thư viện" in ra and "Chỉ tóm tắt" not in ra
    assert not (kho / "doc_sau" / "PMID-20482606.md").exists()
    assert DS.xu_ly_pmid("20482606", kho, lam_lai=True)[0] == "tdm_thieu_thu_vien", "thiếu thư viện ≠ lỗi tệp"


def test_che_do_pmid_luon_sinh_lai_ban_doc_may(dash):
    """Gói tuần (--queue/--pmid) giữ hành vi cũ: bản đọc MÁY đã có vẫn được sinh lại từ tệp nguồn."""
    kho = dash / "toan_van_oa"
    (kho / "PMID-11111111_PMC1.xml").write_text(_xml(), encoding="utf-8")
    (kho / "doc_sau").mkdir()
    md = kho / "doc_sau" / "PMID-11111111.md"
    md.write_text("# bản đọc máy cũ\n", encoding="utf-8")
    assert DS.main(["--pmid", "11111111", "--dash", str(dash)]) == 0
    assert "Bài thử JATS" in md.read_text(encoding="utf-8")


def test_pdf_that_qua_pypdf(dash):
    """PDF thật (byte tối giản tự dựng) đi trọn đường pypdf → bản đọc TDM."""
    pytest.importorskip("pypdf", reason="pypdf chưa cài trên máy/lane này — phần bóc thuần đã kiểm bằng trang giả")
    kho = dash / "toan_van_oa"
    (kho / "PMID-20482606_WTDM.pdf").write_bytes(_pdf_toi_gian([t.splitlines() for t in _trang_gia()]))
    loai, ghi_chu = DS.xu_ly_pmid("20482606", kho, lam_lai=True)
    assert loai == "vua_sinh_tdm", ghi_chu
    md = (kho / "doc_sau" / "PMID-20482606.md").read_text(encoding="utf-8")
    assert "NCT01234567" in md and "0.77 (95% CI 0.62-0.96)" in md and "4 trang" in md


def test_pdf_hong_la_loi_khong_gay(dash):
    pytest.importorskip("pypdf", reason="pypdf chưa cài trên máy/lane này")
    kho = dash / "toan_van_oa"
    (kho / "PMID-20482606_WTDM.pdf").write_bytes(b"<html>Access denied</html>")
    loai, ghi_chu = DS.xu_ly_pmid("20482606", kho, lam_lai=True)
    assert loai == "loi" and "PDF hỏng" in ghi_chu


# ── làn trình duyệt có bác sĩ: không bao giờ ghi đè ──────────────────────────────────────────────────────────────────
def test_khong_ghi_de_ban_doc_trinh_duyet(dash, pdf_gia, capsys):
    kho = dash / "toan_van_oa"
    pm = "42751933"
    (kho / "trinh_duyet").mkdir()
    (kho / "trinh_duyet" / f"PMID-{pm}.json").write_text(json.dumps({"kiem": {"do_day_du": "full"}}), encoding="utf-8")
    (kho / "doc_sau").mkdir()
    md = kho / "doc_sau" / f"PMID-{pm}.md"
    goc = "# Đọc sâu toàn văn — PMID 42751933\n\nTRÍCH XUẤT CÓ CẤU TRÚC của làn trình duyệt — bác sĩ + phiên Claude.\n"
    md.write_text(goc, encoding="utf-8", newline="\n")
    (kho / f"PMID-{pm}_PMC1.xml").write_text(_xml(), encoding="utf-8")   # XML về kho SAU lượt đọc trình duyệt
    _tep_pdf(kho, pm)
    assert DS.main(["--pmid", pm, "--dash", str(dash)]) == 0                       # gói tuần: luôn sinh lại bản máy
    assert DS.main(["--dashboard", "--lam-lai", "--pmid", pm, "--dash", str(dash)]) in (0, 2)
    assert md.read_text(encoding="utf-8") == goc
    ra = capsys.readouterr().out
    assert f"◑ {pm}" in ra and "độ đầy đủ full" in ra and "1 bài đọc qua trình duyệt" in ra


def test_ho_so_trinh_duyet_thieu_ban_doc_la_loi_khong_sinh_thay(dash):
    kho = dash / "toan_van_oa"
    pm = "42751933"
    (kho / "trinh_duyet").mkdir()
    (kho / "trinh_duyet" / f"PMID-{pm}.json").write_text("{}", encoding="utf-8")
    (kho / f"PMID-{pm}_PMC1.xml").write_text(_xml(), encoding="utf-8")
    loai, ghi_chu = DS.xu_ly_pmid(pm, kho, lam_lai=True)
    assert loai == "loi" and "THIẾU bản đọc" in ghi_chu
    assert not (kho / "doc_sau" / f"PMID-{pm}.md").exists()


# ── dashboard ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def _html_dashboard(items: list[tuple[str, str]], ref_pmid: str = "88888888") -> str:
    """Khối DATA kiểu Evidence Workbench: (pmid, decision) mỗi mục; mục đầu có references chứa PMID KHÁC."""
    dong = []
    for k, (pm, dec) in enumerate(items, 1):
        ref = f", references:[{{pmid:'{ref_pmid}', title:'Nghiên cứu khác'}}]" if k == 1 else ""
        dong.append(f"    {{id:'IT-{k:02d}', title:'Mục {k}', gradeSource:'\"Strong\" — nguồn', pmid:'{pm}', "
                    f"decision:'{dec}', gradeLevel:'mod'{ref}}},")
    return ("<html><body><script>\nconst DATA = {\n  meta: {title:'Thử'},\n  summary: {conclusion:'x', doNow:[], "
            "dontDo:[], redFlags:[]},\n  items: [\n" + "\n".join(dong) + "\n  ]\n};\n// HẾT KHỐI DATA\n</script></body></html>")


@pytest.fixture()
def kho_dash(dash, pdf_gia):
    kho = dash / "toan_van_oa"
    (dash / "WebDashboard_A_20261003.html").write_text(_html_dashboard([
        ("11111111", "apply"), ("22222222", "apply"), ("33333333", "consider"), ("11111111", "apply"),
        ("44444444", "apply"), ("55555555", "apply"), ("66666666", "apply"), ("77777777", "apply")]), encoding="utf-8")
    (dash / "WebDashboard_B_20261003.html").write_text(_html_dashboard([
        ("22222222", "apply"), ("99999901", "notyet")]), encoding="utf-8")
    # bản sao lưu: cả kiểu glob khớp («.bak.html») lẫn kiểu đuôi — đều phải bị bỏ
    (dash / "WebDashboard_A_20261003.bak.html").write_text(_html_dashboard([("99999902", "apply")]), encoding="utf-8")
    (dash / "WebDashboard_A_20261003.html.bak-20261003").write_text(_html_dashboard([("99999903", "apply")]),
                                                                    encoding="utf-8")
    (kho / "PMID-11111111_PMC111.xml").write_text(_xml(), encoding="utf-8")
    _tep_pdf(kho, "22222222")
    (kho / "PMID-33333333_PMC333.xml").write_text(_xml(), encoding="utf-8")
    (kho / "PMID-55555555_UPW.html").write_text("<html>OA</html>", encoding="utf-8")
    (kho / "trinh_duyet").mkdir()
    (kho / "trinh_duyet" / "PMID-66666666.json").write_text(json.dumps({"kiem": {"do_day_du": "partial"}}),
                                                            encoding="utf-8")
    (kho / "doc_sau").mkdir()
    (kho / "doc_sau" / "PMID-66666666.md").write_text("# bản đọc trình duyệt\n", encoding="utf-8")
    (kho / "trinh_duyet" / "bac-si-da-doc.jsonl").write_text(json.dumps({"pmid": "77777777"}) + "\n", encoding="utf-8")
    return dash


def _so(ra: str, nhan: str) -> int:
    m = re.search(re.escape(nhan) + r"\s*(\d+)", ra)
    assert m, f"thiếu «{nhan}» trong:\n{ra}"
    return int(m.group(1))


def test_dashboard_chi_apply_dem_theo_don_vi_pmid(kho_dash, capsys):
    dash = kho_dash
    kho = dash / "toan_van_oa"
    assert DS.main(["--dashboard", "--chi-apply", "--dash", str(dash)]) == 0
    ra = capsys.readouterr().out
    # apply duy nhất: 111 (XML) · 222 (PDF TDM) · 444 (không tệp) · 555 (UPW) · 666 (trình duyệt) · 777 (bác sĩ đã đọc)
    assert "Dashboard: 2 tệp · 6 PMID duy nhất — chỉ mục decision='apply'" in ra
    assert "(6 PMID duy nhất)" in ra
    assert _so(ra, "✓ đã có bản đọc:") == 1 and "1 bài đọc qua trình duyệt" in ra
    assert _so(ra, "✚ vừa sinh:") == 2 and "1 bài JATS · 1 bài PDF kênh TDM" in ra
    assert _so(ra, "chưa bóc:") == 1
    assert _so(ra, "○ bỏ qua vì chưa có tệp toàn văn:") == 2 and "trong đó 1 bác sĩ đã đọc trực tiếp" in ra
    assert _so(ra, "⚠ lỗi:") == 0 and "Cộng: 1 + 2 + 1 + 2 + 0 = 6" in ra
    assert (kho / "doc_sau" / "PMID-11111111.md").exists() and (kho / "doc_sau" / "PMID-22222222.md").exists()
    assert not (kho / "doc_sau" / "PMID-33333333.md").exists()          # mục «consider» không thuộc --chi-apply
    assert "--pmid 44444444" in ra and "77777777" not in ra.split("→ bài không có OA", 1)[1]
    for pm in ("99999902", "99999903", "88888888"):                      # .bak và PMID trong references: không tính
        assert pm not in ra


def test_dashboard_lan_hai_giu_ban_da_co_tru_khi_lam_lai(kho_dash, capsys):
    dash = kho_dash
    kho = dash / "toan_van_oa"
    DS.main(["--dashboard", "--chi-apply", "--dash", str(dash)])
    md = kho / "doc_sau" / "PMID-11111111.md"
    md.write_text("# bản đọc máy cũ\n", encoding="utf-8")
    capsys.readouterr()
    DS.main(["--dashboard", "--chi-apply", "--dash", str(dash)])
    ra = capsys.readouterr().out
    assert _so(ra, "✚ vừa sinh:") == 0 and _so(ra, "✓ đã có bản đọc:") == 3 and "2 bản đọc máy" in ra
    assert md.read_text(encoding="utf-8") == "# bản đọc máy cũ\n"
    DS.main(["--dashboard", "--chi-apply", "--lam-lai", "--dash", str(dash)])
    ra = capsys.readouterr().out
    assert _so(ra, "✚ vừa sinh:") == 2 and "Bài thử JATS" in md.read_text(encoding="utf-8")
    assert (kho / "doc_sau" / "PMID-66666666.md").read_text(encoding="utf-8") == "# bản đọc trình duyệt\n"


def test_dashboard_moi_decision_va_tep_chi_dinh(kho_dash, capsys):
    dash = kho_dash
    assert DS.main(["--dashboard", "--dash", str(dash)]) == 0
    ra = capsys.readouterr().out
    assert "Dashboard: 2 tệp · 8 PMID duy nhất" in ra and "chỉ mục decision" not in ra
    assert (dash / "toan_van_oa" / "doc_sau" / "PMID-33333333.md").exists()
    for pm in ("99999902", "99999903", "88888888"):
        assert pm not in ra
    assert DS.main(["--dashboard", str(dash / "WebDashboard_B_20261003.html"), "--dash", str(dash)]) == 0
    assert "Dashboard: 1 tệp · 2 PMID duy nhất" in capsys.readouterr().out


def test_khong_thay_kho_hay_dashboard_la_khong_do_duoc(tmp_path, capsys):
    rong = tmp_path / "EBM-Dashboards-vang"
    assert DS.main(["--dashboard", "--dash", str(rong)]) == 2
    assert DS.main(["--pmid", "42377292", "--dash", str(rong)]) == 2
    ra = capsys.readouterr().out
    assert "KHÔNG ĐO ĐƯỢC" in ra and "Chỉ tóm tắt" not in ra


def test_pmid_sai_dang_bi_bo_khong_thanh_mau_glob(dash, capsys):
    (dash / "toan_van_oa" / "PMID-11111111_PMC1.xml").write_text(_xml(), encoding="utf-8")
    assert DS.main(["--pmid", "*", "--dash", str(dash)]) == 1
    assert "bỏ qua «*»" in capsys.readouterr().out
    assert not (dash / "toan_van_oa" / "doc_sau").exists()


def test_skill_goi_tuan_day_cach_doc_ban_doc_tdm():
    """Thêm loại bản đọc mới thì DẠY agent cùng lúc (CLAUDE.md §6.4) — bước 4b gói tuần phải nói về bản đọc TDM."""
    sk = (TOOLS.parent / "sync" / "scheduled-tasks" / "goi-duyet-tuan-ebm" / "SKILL.md").read_text(encoding="utf-8")
    buoc = sk.split("4b.", 1)[1].split("\n5.", 1)[0]
    assert "_WTDM.pdf" in buoc and "KHÔNG phải OA" in buoc and "15 từ" in buoc


# ── PDF tối giản (không cần reportlab) ──────────────────────────────────────────────────────────────────────────────
def _pdf_toi_gian(trang_dong: list[list[str]]) -> bytes:
    """PDF 1.4 hợp lệ: Helvetica, mỗi dòng một lệnh Tj; bảng xref tính đúng offset — pypdf đọc được."""
    n = len(trang_dong)
    obj = [b"<< /Type /Catalog /Pages 2 0 R >>",
           ("<< /Type /Pages /Kids [" + " ".join(f"{4 + 2 * i} 0 R" for i in range(n)) + f"] /Count {n} >>").encode(),
           b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for i, dong in enumerate(trang_dong):
        lenh = ["BT /F1 8 Tf 30 810 Td 10 TL"]
        for d in dong:
            lenh.append("(" + d.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") Tj T*")
        lenh.append("ET")
        luong = "\n".join(lenh).encode("latin-1")
        obj.append((f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> "
                    f"/Contents {5 + 2 * i} 0 R >>").encode())
        obj.append(b"<< /Length " + str(len(luong)).encode() + b" >>\nstream\n" + luong + b"\nendstream")
    ra = bytearray(b"%PDF-1.4\n")
    vi_tri = []
    for k, o in enumerate(obj, 1):
        vi_tri.append(len(ra))
        ra += f"{k} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(ra)
    ra += f"xref\n0 {len(obj) + 1}\n0000000000 65535 f \n".encode()
    ra += b"".join(f"{v:010d} 00000 n \n".encode() for v in vi_tri)
    ra += f"trailer\n<< /Size {len(obj) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(ra)
