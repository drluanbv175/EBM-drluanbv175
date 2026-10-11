# -*- coding: utf-8 -*-
"""PDF về kho SAU trích dẫn ⇒ tự gắn vào EndNote (11/10/2026).

Hai công cụ sinh PDF — phiên Chrome uỷ quyền (`phien_uy_quyen_chrome.py --nhan`) và tầng Unpaywall
(`gom_toan_van_dashboard.py`) — gọi `nap_endnote_chu_de.py --gan-kho` cho đúng PMID vừa có PDF, chỉ khi thư viện ĐANG
mở (không tự bật EndNote), và không bao giờ làm hỏng lượt chính. Không chạm EndNote thật: `nap` là mô-đun giả.
"""
from __future__ import annotations

import importlib.util
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str):
    sp = importlib.util.spec_from_file_location(f"_{ten}_gan_test", REPO / "tools" / f"{ten}.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


P = _nap("phien_uy_quyen_chrome")
G = _nap("gom_toan_van_dashboard")


def _nap_gia(loi: Exception | None = None):
    goi: list[list[str]] = []

    def main(argv):
        goi.append(list(argv))
        if loi:
            raise loi
        return 0
    return types.SimpleNamespace(main=main), goi


@pytest.mark.parametrize("mod", [P, G], ids=["phien", "gom"])
def test_goi_dung_che_do_gan_kho_chi_khi_dang_mo(mod, tmp_path):
    nap, goi = _nap_gia()
    mod.gan_vao_endnote(["555", "556"], tmp_path, nap=nap)
    assert len(goi) == 1
    a = goi[0]
    assert a[:4] == ["--gan-kho", "--pmid", "555", "556"]
    assert a[a.index("--kho-toan-van") + 1] == str(tmp_path)
    for co in ("--ap-dung", "--chi-khi-dang-mo", "--im-khi-chua-cau-hinh"):
        assert co in a, f"thiếu {co} — công cụ khác gọi không được tự bật EndNote hay báo lỗi khi máy chưa cấu hình"


@pytest.mark.parametrize("mod", [P, G], ids=["phien", "gom"])
def test_loi_buoc_phu_khong_lam_hong_luot_chinh(mod, tmp_path, capsys):
    nap, _ = _nap_gia(RuntimeError("AppleScript sập"))
    mod.gan_vao_endnote(["555"], tmp_path, nap=nap)
    assert "⚪ EndNote: chưa gắn được — RuntimeError" in capsys.readouterr().out


@pytest.mark.parametrize("mod", [P, G], ids=["phien", "gom"])
def test_khong_co_pmid_thi_khong_goi(mod, tmp_path):
    nap, goi = _nap_gia()
    mod.gan_vao_endnote([], tmp_path, nap=nap)
    assert goi == []


def test_gom_pmid_co_pdf(tmp_path):
    for ten in ("PMID-1_UPW.pdf", "PMID-2_WTDM.pdf", "PMID-3_UPW.html", "PMID-4_PMC9.xml", "PMID-12_.pdf", "ghi-chu.pdf"):
        (tmp_path / ten).write_bytes(b"%PDF-1.4")
    assert G.pmid_co_pdf(tmp_path) == {"1", "2"}, "chỉ PDF đúng dạng PMID-<n>_<NGUỒN>.pdf"
    assert G.pmid_co_pdf(tmp_path / "khong-co") == set()


# ── nối trong main của phiên Chrome ────────────────────────────────────────────────────────────────

def _main_nhan(monkeypatch, tmp_path, *, co_pdf: bool, duoi_pytest: bool):
    kho = tmp_path / "kho"
    kho.mkdir()
    if co_pdf:
        (kho / "PMID-555_CHR.pdf").write_bytes(b"%PDF-1.4")
    tep = tmp_path / "tai.html"
    tep.write_text("x", encoding="utf-8", newline="\n")
    goi: list[list[str]] = []
    monkeypatch.setattr(P, "KHO", kho)
    monkeypatch.setattr(P, "nhan", lambda *a, **k: (0, "đã lưu PMID-555_CHR.pdf — phiên X"))
    monkeypatch.setattr(P, "gan_vao_endnote", lambda pmids, k, nap=None: goi.append(list(pmids)))
    if not duoi_pytest:
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    assert P.main(["--nhan", "555", "--tep", str(tep), "--url", "https://x.example/a"]) == 0
    return goi


def test_nhan_pdf_thanh_cong_thi_gan_vao_endnote(monkeypatch, tmp_path):
    assert _main_nhan(monkeypatch, tmp_path, co_pdf=True, duoi_pytest=False) == [["555"]]


def test_nhan_chi_html_thi_khong_goi_endnote(monkeypatch, tmp_path):
    assert _main_nhan(monkeypatch, tmp_path, co_pdf=False, duoi_pytest=False) == []


def test_duoi_pytest_khong_bao_gio_goi_endnote(monkeypatch, tmp_path):
    assert _main_nhan(monkeypatch, tmp_path, co_pdf=True, duoi_pytest=True) == []
