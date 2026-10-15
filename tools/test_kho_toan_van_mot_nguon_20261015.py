# -*- coding: utf-8 -*-
"""Kho toàn văn — MỘT nguồn sự thật cho «đã có toàn văn» (15/10/2026, nhóm G3 của đợt rà làn Chrome + EndNote).

Các phát hiện đã qua phản biện, khoá bằng HÀNH VI (ngoại tuyến, thư mục tạm):
  • TT-01 — `phien_uy_quyen_chrome --nhan` ghi kho hỏng để sót `PMID-<n>_CHR.pdf.tam-<pid>`; bộ đếm (`bao_phu_cuc_bo`, cổng
    `co_toan_van_trong_kho`, khối EndNote) glob `_CHR.*` nên tính bài là «đã đọc». Nay: lượt hỏng dọn tệp tạm + tệp đã chuyển;
    mọi bộ đếm chỉ nhận tên khớp NGUYÊN mẫu hợp lệ (không mất loại hợp lệ nào); gom ghi qua tệp tạm + os.replace.
  • TT-04 — `_CHR.html` chỉ cần ≥ 5 000 byte: trang chỉ có tóm tắt + «Purchase PDF» lọt vào kho rồi qua cổng BH161. Nay phiên và
    bộ đếm dùng CÙNG cổng nội dung với `_UPW.html`; thân bài không phải toàn văn mà có PDF nhúng ⇒ chỉ giữ PDF.
  • TT-03 / W8 — khối EndNote và sổ phủ DO-PHU-OA.md có định nghĩa «có toàn văn» riêng ⇒ đi qua `bao_phu_cuc_bo`.
  • W3 — tầng Unpaywall của gom loại VĨNH VIỄN mọi PMID có tệp `PMID-<n>_*.*` (kể cả `_MCP.md`, trang giới thiệu kho).
  • TT-07 — công cụ kho định vị `EBM-Dashboards` qua `ban_sao_tran.duong_goc` (lồng rồi anh em), như bộ nạp EndNote.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


dtv = _nap("tools/doc_toan_van_co_nguoi.py", "_dtv_kho1015")
vd = _nap("sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py", "_vd_kho1015")
g = _nap("tools/gom_toan_van_dashboard.py", "_gom_kho1015")
P = _nap("tools/phien_uy_quyen_chrome.py", "_puq_kho1015")
tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_kho1015")
stv = _nap("tools/so_toan_van.py", "_stv_kho1015")

T0 = datetime(2026, 10, 15, 9, 0, 0, tzinfo=timezone(timedelta(hours=7)))
LOI = "uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay"
URL = "https://www.sciencedirect.com/science/article/pii/S0741521421008934"
TOAN_VAN = ("<article><h2>Introduction</h2><p>" + "background " * 700 + "</p><h2>Methods</h2><p>" + "randomised " * 700
            + "</p><h2>Results</h2><p>" + "outcome " * 700 + "</p><h2>Discussion</h2><p>" + "meaning " * 700 + "</p></article>")
# Đo thật trong phản biện (repro_chr_html.py): 6 986 byte / 812 từ — chỉ tóm tắt + «Access through your institution · Purchase PDF».
CHI_TOM_TAT = ("<article><h1>Title</h1><h2>Abstract</h2><p>" + "Background word. " * 400
               + "</p><p>Access through your institution · Purchase PDF</p></article>")
TRANG_GIOI_THIEU = ("<html><body>Abstract Introduction Methods Results Discussion " + "w " * 2700
                    + " Fingerprint Access to Document Link to publication</body></html>")
PDF = b"%PDF-1.7\n" + b"1" * 40_000


def _dtv_gia():
    bang = {"Elsevier": {"ket_luan": "cam", "doi": ("10.1016/",), "mien": ("sciencedirect.com",)}}

    def nxb_cua(doi="", url="", tieu_de=""):
        h = P._mien(url)
        return ("Elsevier", bang["Elsevier"]) if h.endswith("sciencedirect.com") else (None, None)
    return types.SimpleNamespace(DIEU_KHOAN_NXB=bang, nxb_cua=nxb_cua, uy_quyen_bac_si=lambda ten, hom_nay=None: {"nxb": ten})


def _phien(tmp_path):
    so, kho = tmp_path / "state" / "phien.json", tmp_path / "kho"
    kho.mkdir()
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=_dtv_gia())[0] == 0
    return so, kho, P.doc_phien(so)["ma"]


def _tai(tmp_path, ma, pmid, than, pdf: bytes | None = None):
    import base64
    t = tmp_path / f"tai-{pmid}.html"
    nhung = f'<script type="application/pdf;base64" id="ebm-pdf">{base64.b64encode(pdf).decode()}</script>' if pdf else ""
    t.write_text(f"<!-- ebm-phien:{ma} pmid:{pmid} url:{URL} -->\n{than}{nhung}", encoding="utf-8")
    return t


# ── TT-01: lượt ghi hỏng không để lại tệp được tính là toàn văn ─────────────────────────────────────────────────────────
def test_nhan_loi_os_replace_don_tep_tam_va_tep_da_chuyen_thu_lai_duoc(tmp_path, monkeypatch):
    so, kho, ma = _phien(tmp_path)
    t = _tai(tmp_path, ma, "44444444", TOAN_VAN, PDF)          # HTML chuyển xong, PDF hỏng ⇒ phải gỡ cả HTML
    that = os.replace

    def replace_gia(a, b):
        if str(b).endswith(".pdf"):
            raise PermissionError("OneDrive đang khoá tệp")
        return that(a, b)
    monkeypatch.setattr(P.os, "replace", replace_gia)
    ma_ra, tb = P.nhan("44444444", t, URL, bay_gio=T0, so=so, kho=kho, dtv=_dtv_gia())
    assert ma_ra == 2 and "OneDrive" in tb
    assert sorted(x.name for x in kho.iterdir()) == [], "tệp tạm/tệp dở của lượt hỏng phải được gỡ"
    assert dtv.bao_phu_cuc_bo(["44444444"], kho)["44444444"] == "chua_co"
    assert P.doc_phien(so)["lich_su"] == [] and t.exists(), "sổ không ghi gì, tệp tải về giữ nguyên"
    monkeypatch.setattr(P.os, "replace", that)
    ma2, tb2 = P.nhan("44444444", t, URL, bay_gio=T0 + timedelta(seconds=5), so=so, kho=kho, dtv=_dtv_gia())
    assert ma2 == 0, f"lượt thử lại bị chặn: {tb2}"


def test_nhan_ghi_so_loi_thi_go_tep_vua_vao_kho(tmp_path, monkeypatch):
    so, kho, ma = _phien(tmp_path)
    t = _tai(tmp_path, ma, "44444445", TOAN_VAN)

    def ghi_hong(d, tep=None):
        raise OSError("đĩa đầy")
    monkeypatch.setattr(P, "_ghi", ghi_hong)
    ma_ra, tb = P.nhan("44444445", t, URL, bay_gio=T0, so=so, kho=kho, dtv=_dtv_gia())
    assert ma_ra == 2 and not list(kho.iterdir()), "sổ và kho phải khớp — tệp trong kho mà sổ không có làm trần/nhịp đếm thiếu"


@pytest.mark.parametrize("ten", ["PMID-22222222_CHR.pdf.tam-2363", "PMID-22222222_PMC1.xml.tam-7", "PMID-22222222_UPW.pdf.cu",
                                 "PMID-22222222_WTDM.pdf.tam-9", "PMID-22222222_MCP.md", "PMID-22222222_CHR.htm",
                                 "PMID-22222222_WTDM.html"])
def test_bo_dem_chi_nhan_ten_khop_nguyen(tmp_path, ten):
    (tmp_path / ten).write_bytes(b"%PDF-1.7 " + TOAN_VAN.encode())
    assert dtv.bao_phu_cuc_bo(["22222222"], tmp_path)["22222222"] == "chua_co"
    assert not vd.co_toan_van_trong_kho("22222222", tmp_path), "cổng BH161 tính tệp không hợp lệ là «đã đọc»"
    assert tt.trang_thai_toan_van("22222222", tmp_path).startswith("CHƯA có")


@pytest.mark.parametrize("ten, noi_dung, trang_thai", [
    ("PMID-33333333_PMC9.xml", b"<article><body/></article>", "oa_xml"),
    ("PMID-33333333_UPW.pdf", b"%PDF-1.4", "oa_khac"),
    ("PMID-33333333_UPW.html", TOAN_VAN.encode(), "oa_khac"),
    ("PMID-33333333_WTDM.pdf", b"%PDF-1.4", "tdm_nxb"),
    ("PMID-33333333_CHR.pdf", b"%PDF-1.4", "phien_chrome"),
    ("PMID-33333333_CHR.html", TOAN_VAN.encode(), "phien_chrome"),
])
def test_moi_loai_hop_le_van_duoc_tinh(tmp_path, ten, noi_dung, trang_thai):
    (tmp_path / ten).write_bytes(noi_dung)
    assert dtv.bao_phu_cuc_bo(["33333333"], tmp_path)["33333333"] == trang_thai
    assert vd.co_toan_van_trong_kho("33333333", tmp_path)
    assert tt.trang_thai_toan_van("33333333", tmp_path).startswith("có ")


def test_pmid_tien_to_khong_bat_nham(tmp_path):
    (tmp_path / "PMID-1234_PMC1.xml").write_text("<x/>", encoding="utf-8")
    assert dtv.bao_phu_cuc_bo(["123"], tmp_path)["123"] == "chua_co" and not vd.co_toan_van_trong_kho("123", tmp_path)


def test_mau_ten_hop_le_trung_giua_nguon_su_that_va_cong():
    assert dtv.TEN_TEP_TOAN_VAN.pattern == vd._TEN_TEP_TOAN_VAN.pattern
    assert (REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py").read_bytes() == \
        (REPO / "sync/skills/dark-analyst/tools/verify_dashboard.py").read_bytes()


def test_gom_ghi_nguyen_tu_loi_khong_de_tep_tam(tmp_path, monkeypatch):
    def replace_hong(a, b):
        raise OSError("hết đĩa")
    monkeypatch.setattr(g.os, "replace", replace_hong)
    with pytest.raises(OSError):
        g._ghi_nguyen_tu(tmp_path / "PMID-1_UPW.pdf", b"%PDF-1.4")
    assert not list(tmp_path.iterdir())
    monkeypatch.undo()
    g._ghi_nguyen_tu(tmp_path / "PMID-1_UPW.pdf", b"%PDF-1.4")
    assert [x.name for x in tmp_path.iterdir()] == ["PMID-1_UPW.pdf"]


def test_nap_ho_so_khong_bi_chan_boi_trang_gioi_thieu_hay_tep_tam(tmp_path):
    """Làn trình duyệt (`--nap`) chỉ bị chặn «đã có toàn văn OA» khi kho có toàn văn THẬT (cùng nguồn sự thật)."""
    (tmp_path / "PMID-11111111_UPW.html").write_text(TRANG_GIOI_THIEU, encoding="utf-8")
    (tmp_path / "PMID-11111111_UPW.pdf.tam-3").write_bytes(b"%PDF-1.4")
    _, bao = dtv.nap({"pmid": "11111111"}, ghi=False, xac_minh=None, kho=tmp_path)
    assert not any("đã có toàn văn OA" in x for x in bao), bao
    (tmp_path / "PMID-11111111_UPW.pdf").write_bytes(b"%PDF-1.4")
    _, bao2 = dtv.nap({"pmid": "11111111"}, ghi=False, xac_minh=None, kho=tmp_path)
    assert any("đã có toàn văn OA" in x for x in bao2)


# ── TT-04: `_CHR.html` qua cùng cổng nội dung với `_UPW.html` ──────────────────────────────────────────────────────────
def test_phien_tu_choi_than_bai_chi_co_tom_tat(tmp_path):
    t = _tai(tmp_path, "M1", "66666666", CHI_TOM_TAT)
    assert len(t.read_bytes()) > P.CO_HTML[0], "fixture phải vượt ngưỡng byte cũ (tái hiện đúng đường vòng)"
    loai, ly = P.kiem_tep(t, "66666666", "M1")
    assert loai is None and "KHÔNG phải toàn văn" in ly
    assert P.kiem_tep(_tai(tmp_path, "M1", "66666666", TOAN_VAN), "66666666", "M1") == ("html", "")


def test_than_bai_tom_tat_co_pdf_nhung_chi_giu_pdf(tmp_path):
    so, kho, ma = _phien(tmp_path)
    t = _tai(tmp_path, ma, "66666667", CHI_TOM_TAT, PDF)
    assert P.kiem_tep(t, "66666667", ma)[0] == "pdf_nhung"
    ma_ra, tb = P.nhan("66666667", t, URL, bay_gio=T0, so=so, kho=kho, dtv=_dtv_gia())
    assert ma_ra == 0, tb
    assert sorted(x.name for x in kho.iterdir()) == ["PMID-66666667_CHR.pdf"], "HTML chỉ tóm tắt không được vào kho"
    assert [x["loai"] for x in P.doc_phien(so)["lich_su"]] == ["pdf"]


def test_bo_dem_chr_html_chi_tom_tat_khong_tinh_nhu_upw(tmp_path):
    (tmp_path / "PMID-66666666_CHR.html").write_text(CHI_TOM_TAT, encoding="utf-8")
    (tmp_path / "PMID-77777777_UPW.html").write_text(CHI_TOM_TAT, encoding="utf-8")
    for pm in ("66666666", "77777777"):
        assert dtv.bao_phu_cuc_bo([pm], tmp_path)[pm] == "chua_co", pm
        assert not vd.co_toan_van_trong_kho(pm, tmp_path), pm
        assert tt.trang_thai_toan_van(pm, tmp_path).startswith("CHƯA có"), pm


# ── TT-03: khối EndNote đi qua nguồn sự thật ───────────────────────────────────────────────────────────────────────────
def test_endnote_trang_gioi_thieu_va_bac_si_da_doc(tmp_path):
    (tmp_path / "trinh_duyet").mkdir()
    (tmp_path / "PMID-11111111_UPW.html").write_text(TRANG_GIOI_THIEU, encoding="utf-8")
    (tmp_path / "trinh_duyet" / "bac-si-da-doc.jsonl").write_text(json.dumps({"pmid": "33333333", "ngay": "2026-10-15"}) + "\n",
                                                                  encoding="utf-8")
    (tmp_path / "trinh_duyet" / "PMID-44444444.json").write_text("{}", encoding="utf-8")
    assert tt.trang_thai_toan_van("11111111", tmp_path).startswith("CHƯA có"), "trang giới thiệu kho không phải «có HTML»"
    assert tt.trang_thai_toan_van("33333333", tmp_path) == "bác sĩ đã đọc trực tiếp (kết luận ghi sổ)"
    assert tt.trang_thai_toan_van("44444444", tmp_path) == "đã đọc qua làn trình duyệt (hồ sơ trích xuất)"


# ── W8 + W3: sổ phủ và tầng Unpaywall của gom ──────────────────────────────────────────────────────────────────────────
def _kho_tron(kho: Path) -> None:
    (kho / "trinh_duyet").mkdir(parents=True)
    (kho / "PMID-11111111_UPW.html").write_text(TRANG_GIOI_THIEU, encoding="utf-8")      # trang giới thiệu — không phủ
    (kho / "PMID-22222222_MCP.md").write_text("# bản MCP", encoding="utf-8")            # _MCP — không phủ
    (kho / "PMID-33333333_CHR.pdf.tam-9").write_bytes(b"%PDF-1.4")                       # tệp tạm — không phủ
    (kho / "PMID-44444444_PMC1.xml").write_text("<article><body/></article>", encoding="utf-8")   # phủ
    (kho / "PMID-66666666_UPW.pdf").write_bytes(b"%PDF-1.4")                             # phủ
    (kho / "trinh_duyet" / "bac-si-da-doc.jsonl").write_text(json.dumps({"pmid": "55555555", "ngay": "2026-10-15"}) + "\n",
                                                             encoding="utf-8")         # phủ (bác sĩ đã đọc)


def test_pmid_da_phu_mot_nguon_su_that(tmp_path):
    _kho_tron(tmp_path)
    assert dtv.pmid_da_phu(tmp_path) == {"44444444", "55555555", "66666666"}


def _main_gom(monkeypatch, kho, argv, tang=None):
    monkeypatch.setattr(g, "KHO", kho)
    monkeypatch.setattr(g, "_nap_gom", lambda: types.SimpleNamespace(lien_ket_pmc=lambda can: {}))
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    if tang is not None:
        monkeypatch.setattr(g, "tang_unpaywall", tang)
    monkeypatch.setattr(sys, "argv", ["gom_toan_van_dashboard.py", *argv])
    return g.main()


def test_do_phu_tong_di_qua_bao_phu_cuc_bo(tmp_path, monkeypatch):
    _kho_tron(tmp_path)
    pm = ["11111111", "22222222", "33333333", "44444444", "55555555", "77777777"]
    assert _main_gom(monkeypatch, tmp_path, ["--pmid", *pm]) == 0
    so = (tmp_path / "DO-PHU-OA.md").read_text(encoding="utf-8")
    assert "cho **3** PMID" in so, so
    assert "phủ **2/6**" in so, "tập quét: chỉ 44444444 (XML) + 55555555 (bác sĩ đã đọc) là đã phủ"
    assert "thông tin phụ" in so


def test_unpaywall_thu_lai_pmid_chi_co_tep_khong_phai_toan_van(tmp_path, monkeypatch):
    _kho_tron(tmp_path)
    da_thu: list[list[str]] = []
    pm = ["11111111", "22222222", "33333333", "44444444", "66666666"]
    _main_gom(monkeypatch, tmp_path, ["--pmid", *pm, "--unpaywall"],
              tang=lambda thu, gom=None: (da_thu.append(list(thu)), (0, list(thu)))[1])
    assert da_thu == [["11111111", "22222222", "33333333"]], \
        "trang giới thiệu, _MCP.md, tệp tạm không được loại PMID khỏi Unpaywall; XML/UPW.pdf thật thì bỏ qua"


# ── TT-07: định vị gốc dữ liệu qua ban_sao_tran.duong_goc (lồng rồi anh em) ────────────────────────────────────────────
@pytest.mark.parametrize("mod", [dtv, g, P, stv], ids=["doc_toan_van_co_nguoi", "gom", "phien_uy_quyen_chrome", "so_toan_van"])
def test_goc_du_lieu_theo_duong_goc_anh_em_va_long(tmp_path, monkeypatch, mod):
    repo = tmp_path / "wt"
    repo.mkdir()
    (tmp_path / "EBM-Dashboards").mkdir()
    monkeypatch.setattr(mod, "REPO", repo)
    assert mod._goc_du_lieu("EBM-Dashboards") == tmp_path / "EBM-Dashboards", "bố cục anh em phải thấy kho thật"
    (repo / "EBM-Dashboards").mkdir()
    assert mod._goc_du_lieu("EBM-Dashboards") == repo / "EBM-Dashboards", "vị trí lồng được ưu tiên như duong_goc"
