# -*- coding: utf-8 -*-
"""Kiểm phần PDF của `tom_tat_chung_cu_word.py` (21/10/2026): bác sĩ «không thể đọc trực tiếp» bản Word tóm tắt trong
EndNote ⇒ dựng thêm PDF giữ màu và gắn PDF THAY liên kết Word, KHÔNG được làm mất PDF toàn văn của bản ghi."""
from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

_sp = importlib.util.spec_from_file_location("_ttcc_pdf_test", Path(__file__).resolve().parent / "tom_tat_chung_cu_word.py")
T = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T)

TOAN_VAN = "internal-pdf://1/PMID-123.pdf"


class _EnGia:
    """EndNote giả: trường «File Attachments» là chuỗi ngăn bằng \\r; `mat` = EndNote làm rơi mọi tệp trừ tệp cuối."""

    def __init__(self, cu: str, mat: bool = False):
        self.gia_tri = cu
        self.mat = mat
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


def _word_pdf(thu_muc: Path, khoa: str = "PMID-123", co_pdf: bool = True) -> tuple[Path, Path]:
    thu_muc.mkdir(parents=True, exist_ok=True)
    docx = thu_muc / f"{khoa}_TomTatChungCu.docx"
    docx.write_bytes(b"w")
    pdf = thu_muc / f"{khoa}_TomTatChungCu.pdf"
    if co_pdf:
        pdf.write_bytes(b"%PDF")
        os.utime(pdf, (docx.stat().st_mtime + 5, docx.stat().st_mtime + 5))
    return docx, pdf


def test_gan_pdf_thay_lien_ket_word_giu_toan_van(tmp_path):
    docx, pdf = _word_pdf(tmp_path)
    en = _EnGia(TOAN_VAN + "\r" + docx.resolve().as_uri())
    assert T.gan_vao_endnote(tmp_path, {"rec": 5}, pdf, ap_dung=True, endnote=en, thay=(docx.name,)) == 0
    tep = en.gia_tri.split("\r")
    assert tep[0] == TOAN_VAN                       # PDF toàn văn còn nguyên, đứng đầu
    assert tep[-1].endswith(pdf.name)               # PDF tóm tắt được gắn
    assert not any(x.endswith(docx.name) for x in tep)  # liên kết Word đã bỏ khỏi trường
    assert docx.is_file()                           # tệp Word trên đĩa KHÔNG bị xoá


def test_gan_pdf_chay_kho_khong_ghi(tmp_path):
    docx, pdf = _word_pdf(tmp_path)
    en = _EnGia(TOAN_VAN + "\r" + docx.resolve().as_uri())
    assert T.gan_vao_endnote(tmp_path, {"rec": 5}, pdf, ap_dung=False, endnote=en, thay=(docx.name,)) == 0
    assert en.ghi == []


def test_endnote_lam_mat_toan_van_thi_ghi_tra_ca_word(tmp_path):
    docx, pdf = _word_pdf(tmp_path)
    cu = TOAN_VAN + "\r" + docx.resolve().as_uri()
    en = _EnGia(cu, mat=True)
    assert T.gan_vao_endnote(tmp_path, {"rec": 5}, pdf, ap_dung=True, endnote=en, thay=(docx.name,)) == 1
    assert en.ghi[-1] == cu  # trả lại NGUYÊN trạng cũ (toàn văn + Word), không để bản ghi mất tệp


def test_da_gan_pdf_va_het_word_thi_khong_ghi(tmp_path):
    docx, pdf = _word_pdf(tmp_path)
    en = _EnGia(TOAN_VAN + "\r" + pdf.resolve().as_uri())
    assert T.gan_vao_endnote(tmp_path, {"rec": 5}, pdf, ap_dung=True, endnote=en, thay=(docx.name,)) == 0
    assert en.ghi == []


def test_ten_tep_giai_ma_khoang_trang():
    assert T._ten_tep("file:///a/b%20c/PMID-1_TomTatChungCu.pdf") == "PMID-1_TomTatChungCu.pdf"
    assert T._ten_tep("internal-pdf://9/PMID-1.pdf") == "PMID-1.pdf"


def test_dung_pdf_loi_thi_tra_none(tmp_path):
    docx, _ = _word_pdf(tmp_path, co_pdf=False)

    def chay_hong(lenh, **kw):
        return subprocess.CompletedProcess(lenh, 1, stdout="thiếu Chrome", stderr="")
    assert T.dung_pdf(docx, chay=chay_hong) is None


def test_dung_pdf_ra_cu_hon_word_thi_tra_none(tmp_path):
    docx, pdf = _word_pdf(tmp_path, co_pdf=False)
    pdf.write_bytes(b"%PDF")
    os.utime(pdf, (docx.stat().st_mtime - 60, docx.stat().st_mtime - 60))  # PDF cũ của bản Word trước

    def chay_ok(lenh, **kw):
        return subprocess.CompletedProcess(lenh, 0, stdout="", stderr="")
    assert T.dung_pdf(docx, chay=chay_ok) is None


def test_pdf_hoa_chay_kho_khong_dung_khong_ghi(tmp_path):
    thu_vien = tmp_path / "Lib.enl"
    docx, pdf = _word_pdf(tmp_path / T.TEN_THU_MUC_RA, co_pdf=False)
    goi: list[Path] = []
    en = _EnGia(TOAN_VAN + "\r" + docx.resolve().as_uri())
    ma = T.pdf_hoa(thu_vien, ap_dung=False, endnote=en, dung_pdf_fn=lambda d: goi.append(d),
                   tim=lambda tv, k: {"rec": 5, "khoa": k})
    assert ma == 0 and goi == [] and en.ghi == [] and not pdf.exists()


def test_pdf_hoa_ap_dung_dung_pdf_va_gan_thay_word(tmp_path):
    thu_vien = tmp_path / "Lib.enl"
    docx, pdf = _word_pdf(tmp_path / T.TEN_THU_MUC_RA, co_pdf=False)
    en = _EnGia(TOAN_VAN + "\r" + docx.resolve().as_uri())

    def dung_gia(d):
        p = T.tep_pdf(d)
        p.write_bytes(b"%PDF")
        os.utime(p, (d.stat().st_mtime + 5, d.stat().st_mtime + 5))
        return p
    ma = T.pdf_hoa(thu_vien, ap_dung=True, endnote=en, dung_pdf_fn=dung_gia, tim=lambda tv, k: {"rec": 5, "khoa": k})
    assert ma == 0 and pdf.is_file()
    assert en.gia_tri.split("\r")[0] == TOAN_VAN and en.gia_tri.endswith(pdf.name)
    assert docx.name not in en.gia_tri


def test_pdf_hoa_khong_dung_duoc_pdf_thi_khong_gan(tmp_path):
    thu_vien = tmp_path / "Lib.enl"
    docx, _ = _word_pdf(tmp_path / T.TEN_THU_MUC_RA, co_pdf=False)
    en = _EnGia(TOAN_VAN + "\r" + docx.resolve().as_uri())
    ma = T.pdf_hoa(thu_vien, ap_dung=True, endnote=en, dung_pdf_fn=lambda d: None, tim=lambda tv, k: {"rec": 5, "khoa": k})
    assert ma == 1 and en.ghi == []  # không có PDF ⇒ giữ liên kết Word, không gắn gì


def test_dung_gan_pdf_khi_co_pdf(monkeypatch):
    """`dung … --gan-endnote` gắn PDF (thay Word) — đường gắn Word chỉ còn là dự phòng khi không dựng được PDF."""
    nguon = (Path(__file__).resolve().parent / "tom_tat_chung_cu_word.py").read_text(encoding="utf-8")
    than = nguon[nguon.index("def dung(thu_vien"):nguon.index("def _tach_tep")]
    dong = [x.strip() for x in than.splitlines() if "gan_vao_endnote(" in x]
    assert dong[0].startswith("return gan_vao_endnote(thu_vien, bg, pdf,") and "thay=(ra.name,)" in dong[0]
