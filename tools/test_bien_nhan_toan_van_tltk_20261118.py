"""Hồi quy 18/11/2026 — `nap_endnote_de_tai.py --ghi-bien-nhan-toan-van`: biên nhận toàn văn TỪNG TLTK cho cổng
G10-AUTO-12 của repo y khoa (bác sĩ: «tất cả trích dẫn cho nghiên cứu … phải luôn là toàn văn, nếu không phải toàn văn
và không thể lấy được toàn văn thì loại bỏ»).

Đo thật 18/11 (chạy khô, bản sao thư mục đề tài): BTM 42/42 có toàn văn ⇒ ĐẠT; C1a 25/58 ⇒ CÒN VIỆC, 3 TLTK đã có làn
trình duyệt «không quyền» trong sổ.

Khoá TLTK/khuôn biên nhận do mô-đun `toan_van_trich_dan` của repo y khoa quyết; CI repo gốc không có repo y khoa nên phần
lớn phép thử dùng mô-đun GIẢ cùng giao diện, phép thử với mô-đun THẬT chỉ chạy khi có cây OneDrive (skip có khai báo).
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, ROOT / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


T = _nap("tools/nap_endnote_de_tai.py", "_nap_endnote_de_tai_bien_nhan_test")
S = "NC-TV"
DE_CUONG = ("# Đề cương\n\n# 7. TÀI LIỆU THAM KHẢO\n\n"
            "1. Bài có PDF trong EndNote. PMID: 11111111.\n"
            "2. Bài có bản ghi nhưng chưa có PDF. PMID: 22222222.\n"
            "3. Bài chưa có bản ghi EndNote. PMID: 33333333.\n"
            "4. Bài có PDF ở thư mục đề tài. doi:10.1000/xyz4.\n")


def _tvt_gia():
    """Mô-đun giả cùng giao diện `toan_van_trich_dan` (tltk_de_tai · doc_bien_nhan · _tim_muc · ghi_bien_nhan)."""
    def tltk_de_tai(out, study):
        p = Path(out) / f"DE_CUONG_NOP_HOI_DONG_{study}.md"
        ra = []
        for d in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(\d+)\.\s+(.+)$", d)
            if m:
                k = {f"pmid:{x}" for x in re.findall(r"PMID:\s*(\d+)", d)} | {
                    f"doi:{x.rstrip('.').lower()}" for x in re.findall(r"doi:(10\.\S+)", d)}
                ra.append({"tai_lieu": p.name, "so": int(m.group(1)), "van": m.group(2), "khoa": sorted(k)})
        return ra, [p.name]

    def doc_bien_nhan(out, study):
        p = Path(out) / f"TOAN_VAN_TLTK_{study}.json"
        return (json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None), None

    def _tim_muc(khoa, bn):
        return next((x for x in bn.get("muc") or [] if set(khoa) & set(x.get("khoa") or [])), None)

    def ghi_bien_nhan(out, study, bn):
        p = Path(out) / f"TOAN_VAN_TLTK_{study}.json"
        p.write_text(json.dumps(bn, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        return p

    return SimpleNamespace(SCHEMA="de_tai/toan_van_tltk/v1", tltk_de_tai=tltk_de_tai, doc_bien_nhan=doc_bien_nhan,
                           _tim_muc=_tim_muc, ghi_bien_nhan=ghi_bien_nhan,
                           danh_gia=lambda out, s: {"trang_thai": "GIA", "dem": {}})


class _En:
    """EndNote giả tối thiểu: Accession Number/DOI → mã bản ghi; «File Attachments» theo mã."""

    def __init__(self, ban_ghi):
        self.bg = ban_ghi  # [(pmid, doi, tep)]

    def tim_khop(self, gia_tri, truong):
        i = 0 if truong == "Accession Number" else 1
        return {v: [f"R{j}" for j, b in enumerate(self.bg) if b[i] and b[i].lower() == v.lower()] for v in gia_tri}

    def doc_truong(self, ids, truong):
        assert truong == "File Attachments"
        return {f"R{j}": b[2] for j, b in enumerate(self.bg) if f"R{j}" in ids}


def _de_tai(tmp_path: Path) -> Path:
    d = tmp_path / "exports" / S
    d.mkdir(parents=True)
    (d / f"DE_CUONG_NOP_HOI_DONG_{S}.md").write_text(DE_CUONG, encoding="utf-8", newline="\n")
    tv = d / T.THU_MUC_TOAN_VAN
    tv.mkdir()
    (tv / "DOI-10.1000_xyz4.pdf").write_bytes(b"%PDF-1.4 toan van")
    return d


EN = _En([("11111111", "", "internal-pdf://1/bai1.pdf"), ("22222222", "", "internal-pdf://2/bai2_TomTatChungCu.pdf")])


def _muc(bn, so):
    return next(m for m in bn["muc"] if m["so"] == so)


def test_do_tung_tltk_endnote_va_thu_muc_de_tai(tmp_path):
    d = _de_tai(tmp_path)
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={}, tvt=_tvt_gia())
    assert bn["schema"] == "de_tai/toan_van_tltk/v1" and len(bn["muc"]) == 4
    assert (_muc(bn, 1)["toan_van"], _muc(bn, 1)["nguon"]) == (True, "endnote")
    assert _muc(bn, 2)["toan_van"] is False      # chỉ có PDF tóm tắt chứng cứ — không phải toàn văn
    assert _muc(bn, 3)["toan_van"] is False      # EndNote đo được mà chưa có bản ghi ⇒ thiếu (không phải «chưa đo»)
    assert (_muc(bn, 4)["toan_van"], _muc(bn, 4)["nguon"], _muc(bn, 4)["tep"]) == (
        True, "toan_van_tltk", "DOI-10.1000_xyz4.pdf")


def test_lan_da_thu_gom_truy_cap_mo_so_khong_truy_cap_va_giu_lan_cu(tmp_path):
    d = _de_tai(tmp_path)
    tvt = _tvt_gia()
    cu = {"muc": [{"khoa": ["pmid:33333333"], "lan_da_thu": [{"lan": "trinh_duyet", "ngay": "2026-11-01",
                                                               "ket_qua": "lượt cũ"}]}]}
    tvt.ghi_bien_nhan(d, S, cu)
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": {"chay": True}}, tvt=tvt,
                              hom_nay=date(2026, 11, 18),
                              khong_truy_cap={"22222222": {"ngay": "2026-11-10", "ly_do": "Wiley chỉ tóm tắt"}})
    lan2 = {(x["lan"], x["ngay"]) for x in _muc(bn, 2)["lan_da_thu"]}
    assert lan2 == {("truy_cap_mo", "2026-11-18"), ("trinh_duyet", "2026-11-10")}
    lan3 = {(x["lan"], x["ngay"]) for x in _muc(bn, 3)["lan_da_thu"]}
    assert lan3 == {("trinh_duyet", "2026-11-01"), ("truy_cap_mo", "2026-11-18")}  # lượt cũ được giữ
    assert _muc(bn, 1)["lan_da_thu"] == []   # có toàn văn ⇒ không ghi làn
    # chạy lại cùng ngày không nhân đôi làn
    tvt.ghi_bien_nhan(d, S, bn)
    bn2 = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": {"chay": True}}, tvt=tvt,
                               hom_nay=date(2026, 11, 18))
    assert len(_muc(bn2, 3)["lan_da_thu"]) == 2


def test_khong_gom_thi_khong_tu_ghi_lan_truy_cap_mo(tmp_path):
    d = _de_tai(tmp_path)
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={}, tvt=_tvt_gia())
    assert all(x["lan"] != "truy_cap_mo" for m in bn["muc"] for x in m["lan_da_thu"])


def test_endnote_chua_mo_thi_khong_ghi_bien_nhan(tmp_path, monkeypatch, capsys):
    d = _de_tai(tmp_path)
    monkeypatch.setattr(T, "nap_tvt", lambda _t: _tvt_gia())
    T._chay_bien_nhan(S, d, endnote=None, kho=None, bc={})
    assert not (d / f"TOAN_VAN_TLTK_{S}.json").exists()
    assert "KHÔNG ghi" in capsys.readouterr().out


def test_chua_co_mo_dun_y_khoa_thi_khong_ghi(tmp_path, capsys):
    d = _de_tai(tmp_path)
    assert T.nap_tvt(d) is None
    T._chay_bien_nhan(S, d, endnote=EN, kho=None, bc={})
    assert not (d / f"TOAN_VAN_TLTK_{S}.json").exists()
    assert "chưa có tools/toan_van_trich_dan.py" in capsys.readouterr().out


def test_endnote_mo_thi_ghi_bien_nhan(tmp_path, monkeypatch, capsys):
    d = _de_tai(tmp_path)
    monkeypatch.setattr(T, "nap_tvt", lambda _t: _tvt_gia())
    T._chay_bien_nhan(S, d, endnote=EN, kho=None, bc={})
    bn = json.loads((d / f"TOAN_VAN_TLTK_{S}.json").read_text(encoding="utf-8"))
    assert [m["toan_van"] for m in bn["muc"]] == [True, False, False, True]
    assert "Biên nhận toàn văn: 4 TLTK" in capsys.readouterr().out


MOD_THAT = ROOT / "medical-ebm-automation" / "tools" / "toan_van_trich_dan.py"


@pytest.mark.skipif(not MOD_THAT.is_file(), reason="cần repo y khoa có tools/toan_van_trich_dan.py (cây OneDrive)")
def test_voi_mo_dun_that_ket_luan_khong_lay_duoc_sau_hai_lan(tmp_path, monkeypatch):
    d = _de_tai(tmp_path)
    tvt = _nap("medical-ebm-automation/tools/toan_van_trich_dan.py", "_tvt_that_test")
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": {"chay": True}}, tvt=tvt,
                              khong_truy_cap={"22222222": {"ngay": "2026-11-10", "ly_do": "không quyền"}})
    tvt.ghi_bien_nhan(d, S, bn)
    kq = tvt.danh_gia(d, S)
    kl = {x["so"]: x["ket_luan"] for x in kq["tltk"]}
    assert kl == {1: "co", 2: "khong_lay_duoc", 3: "chua_thu_het", 4: "co"}
    assert kq["trang_thai"] == "VI_PHAM"
