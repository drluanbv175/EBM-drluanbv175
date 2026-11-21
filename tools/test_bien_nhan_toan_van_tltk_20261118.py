"""Hồi quy 18/11/2026 — `nap_endnote_de_tai.py --ghi-bien-nhan-toan-van`: biên nhận toàn văn TỪNG TLTK cho cổng
G10-AUTO-12 của repo y khoa (bác sĩ: «tất cả trích dẫn cho nghiên cứu … phải luôn là toàn văn, nếu không phải toàn văn
và không thể lấy được toàn văn thì loại bỏ»).

Đo thật 18/11 (chạy khô, bản sao thư mục đề tài): BTM 42/42 có toàn văn ⇒ ĐẠT; C1a 25/58 ⇒ CÒN VIỆC, 3 TLTK đã có làn
trình duyệt «không quyền» trong sổ.

Khoá TLTK/khuôn biên nhận do mô-đun `toan_van_trich_dan` của repo y khoa quyết; CI repo gốc không có repo y khoa nên phần
lớn phép thử dùng mô-đun GIẢ cùng giao diện, phép thử với mô-đun THẬT chỉ chạy khi có cây OneDrive (skip có khai báo).
"""
from __future__ import annotations

import ast
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
# Kết quả `gom_toan_van` HỢP LỆ của một lượt làn truy cập mở chạy trọn (21/11/2026 — fixture cũ `{"chay": True}` không phải
# khuôn thật): mọi TLTK thiếu PDF đã gửi đi gom và làn ra kết luận cho từng định danh.
GOM_TRON = {"do_duoc": {"pmid": ["11111111", "22222222", "33333333"], "doi": ["10.2000/abc5"]}, "khong_do_duoc": []}


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
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": GOM_TRON}, tvt=tvt,
                              hom_nay=date(2026, 11, 18),
                              khong_truy_cap={"22222222": {"ngay": "2026-11-10", "ly_do": "Wiley chỉ tóm tắt"}})
    lan2 = {(x["lan"], x["ngay"]) for x in _muc(bn, 2)["lan_da_thu"]}
    assert lan2 == {("truy_cap_mo", "2026-11-18"), ("trinh_duyet", "2026-11-10")}
    lan3 = {(x["lan"], x["ngay"]) for x in _muc(bn, 3)["lan_da_thu"]}
    assert lan3 == {("trinh_duyet", "2026-11-01"), ("truy_cap_mo", "2026-11-18")}  # lượt cũ được giữ
    assert _muc(bn, 1)["lan_da_thu"] == []   # có toàn văn ⇒ không ghi làn
    # chạy lại cùng ngày không nhân đôi làn
    tvt.ghi_bien_nhan(d, S, bn)
    bn2 = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": GOM_TRON}, tvt=tvt,
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
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": GOM_TRON}, tvt=tvt,
                              khong_truy_cap={"22222222": {"ngay": "2026-11-10", "ly_do": "không quyền"}})
    tvt.ghi_bien_nhan(d, S, bn)
    kq = tvt.danh_gia(d, S)
    kl = {x["so"]: x["ket_luan"] for x in kq["tltk"]}
    assert kl == {1: "co", 2: "khong_lay_duoc", 3: "chua_thu_het", 4: "co"}
    assert kq["trang_thai"] == "VI_PHAM"


# ── 18/11/2026 (làn toàn văn C1a): sổ «không truy cập» nhận DOI; biên nhận tra theo PMID · DOI · PMID suy từ DOI ──────────
DTV = _nap("tools/doc_toan_van_co_nguoi.py", "_dtv_bien_nhan_test")
DE_CUONG_DOI = DE_CUONG + "5. Bài chỉ có DOI. doi:10.2000/abc5.\n"


def test_so_khong_truy_cap_ghi_va_doc_theo_doi(tmp_path):
    kho = tmp_path / "kho"
    kho.mkdir()
    assert DTV.danh_dau_khong_truy_cap(None, "T&F đòi mua", kho=kho, hom_nay=date(2026, 11, 18), doi="10.1080/ABC") == 0
    assert DTV.danh_dau_khong_truy_cap("12345678", "SAGE", kho=kho, hom_nay=date(2026, 11, 18)) == 0
    ktc = DTV._khong_truy_cap(kho, date(2026, 11, 18))
    assert set(ktc) == {"doi:10.1080/abc", "12345678"}
    assert ktc["doi:10.1080/abc"]["ly_do"] == "T&F đòi mua"


def test_cli_khong_truy_cap_nhan_doi_tu_choi_chuoi_la(tmp_path, monkeypatch, capsys):
    kho = tmp_path / "kho"
    kho.mkdir()
    monkeypatch.setattr(DTV, "KHO", kho)
    assert DTV.main(["--khong-truy-cap", "10.1177/0049124192021002005", "--ly-do", "SAGE get access"]) == 0
    assert "DOI 10.1177/0049124192021002005" in capsys.readouterr().out
    assert DTV.main(["--khong-truy-cap", "abc", "--ly-do", "x"]) == 3
    assert DTV.main(["--khong-truy-cap", "10.1177/x"]) == 3  # thiếu --ly-do


def _de_tai_doi(tmp_path: Path) -> Path:
    d = _de_tai(tmp_path)
    (d / f"DE_CUONG_NOP_HOI_DONG_{S}.md").write_text(DE_CUONG_DOI, encoding="utf-8", newline="\n")
    return d


def test_bien_nhan_tra_so_theo_doi_cho_tltk_chi_co_doi(tmp_path):
    d = _de_tai_doi(tmp_path)
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": GOM_TRON}, tvt=_tvt_gia(),
                              hom_nay=date(2026, 11, 18),
                              khong_truy_cap={"doi:10.2000/abc5": {"ngay": "2026-11-18", "ly_do": "không quyền"}})
    lan = {x["lan"] for x in _muc(bn, 5)["lan_da_thu"]}
    assert lan == {"truy_cap_mo", "trinh_duyet"}


def test_bien_nhan_tra_so_theo_pmid_suy_tu_doi(tmp_path):
    d = _de_tai_doi(tmp_path)
    bc = {"pmid_tu_doi": {"them": ["TLTK 5: DOI 10.2000/abc5 → PMID 55555555"]}}
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc=bc, tvt=_tvt_gia(), hom_nay=date(2026, 11, 18),
                              khong_truy_cap={"55555555": {"ngay": "2026-11-10", "ly_do": "OUP redirectedFrom"}})
    assert [(x["lan"], x["ngay"]) for x in _muc(bn, 5)["lan_da_thu"]] == [("trinh_duyet", "2026-11-10")]


# ── 21/11/2026: làn truy cập mở KHÔNG ĐO ĐƯỢC thì biên nhận không ghi lượt «truy_cap_mo» ───────────────────────────────────
# Đo thật 21/11: `--gom-toan-van --ghi-bien-nhan-toan-van` chạy từ worktree của repo gốc — bộ gom in «⚪ KHÔNG ĐO ĐƯỢC — không
# thấy kho …» và trả mã 2 — mà biên nhận C1a vẫn ghi «không có bản truy cập mở hợp lệ» ngày hôm đó cho 17 TLTK, đẩy TLTK về
# phía luật «đã thử hết OA mà không có toàn văn ⇒ loại khỏi danh mục trích dẫn».

def _boom(*_a, **_k):
    raise AssertionError("không được chạy làn truy cập mở khi kho vắng/lệch")


def _khong_doi(*_a):
    raise AssertionError("ca này không có TLTK chỉ-DOI cần làn Unpaywall theo DOI")


class _Kq:
    def __init__(self, ma: int, ra: str = ""):
        self.returncode, self.stdout = ma, ra


def _chay_gia(ma_gom=0, ra_gom="  +0 toàn văn mới · không-OA 2", ma_in=0, ghi=None):
    """subprocess.run giả cho hai bước của làn theo PMID (bộ gom · bộ in PDF)."""
    def chay(lenh, **_k):
        if ghi is not None:
            ghi.append(lenh)
        return _Kq(ma_gom, ra_gom) if lenh[1].endswith("gom_toan_van_dashboard.py") else _Kq(ma_in, "✓ đã in 0/0 bài")
    return chay


DS_GOM = [{"so": 2, "pmid": "22222222", "doi": None}, {"so": 3, "pmid": "33333333", "doi": None}]
UPW_KHONG_EMAIL = {"luu": [], "khong_luu": [], "loi": "Unpaywall cần email định danh (giả)", "da_do_doi": [],
                   "khong_do_duoc": []}


def _kho(tmp_path: Path) -> Path:
    k = tmp_path / "toan_van_oa"
    k.mkdir()
    return k


def test_gom_kho_vang_khong_chay_lan_pmid_va_bao_khong_do_duoc(tmp_path):
    bc = T.gom_toan_van(DS_GOM, tmp_path / "tv", None, chay=_boom, gom_doi=_khong_doi, tim_kho_oa=lambda: None)
    assert bc["do_duoc"] == {"pmid": [], "doi": []}
    assert len(bc["khong_do_duoc"]) == 1 and "không thấy kho" in bc["khong_do_duoc"][0]


def test_gom_kho_lech_kho_dang_doc_khong_chay(tmp_path):
    khac = tmp_path / "khac"
    khac.mkdir()
    bc = T.gom_toan_van(DS_GOM, tmp_path / "tv", khac, chay=_boom, gom_doi=_khong_doi, tim_kho_oa=lambda: _kho(tmp_path))
    assert bc["do_duoc"]["pmid"] == [] and "lượt này đọc kho" in bc["khong_do_duoc"][0]


@pytest.mark.parametrize("ma_gom, ma_in", [(2, 0), (0, 1), (0, 2)])
def test_gom_hoac_in_pdf_ma_khac_0_la_khong_do_duoc(tmp_path, ma_gom, ma_in):
    kho = _kho(tmp_path)
    bc = T.gom_toan_van(DS_GOM, tmp_path / "tv", kho, chay=_chay_gia(ma_gom=ma_gom, ma_in=ma_in), gom_doi=_khong_doi,
                        tim_kho_oa=lambda: kho)
    assert bc["do_duoc"]["pmid"] == [] and len(bc["khong_do_duoc"]) == 1


@pytest.mark.parametrize("dau", T.DAU_HIEU_GOM_CHUA_TRON)
def test_gom_ma_0_nhung_in_dau_hieu_chua_tron_la_khong_do_duoc(tmp_path, dau):
    kho = _kho(tmp_path)
    bc = T.gom_toan_van(DS_GOM, tmp_path / "tv", kho, chay=_chay_gia(ra_gom=f"  ⚠ 1 {dau} x\n  +0 toàn văn mới"),
                        gom_doi=_khong_doi, tim_kho_oa=lambda: kho)
    assert bc["do_duoc"]["pmid"] == [] and dau in bc["khong_do_duoc"][0]


def test_gom_tron_thi_do_duoc_va_bo_in_pdf_ghi_dung_kho(tmp_path):
    kho, ghi = _kho(tmp_path), []
    bc = T.gom_toan_van(DS_GOM, tmp_path / "tv", kho, chay=_chay_gia(ghi=ghi), gom_doi=_khong_doi, tim_kho_oa=lambda: kho)
    assert bc["do_duoc"] == {"pmid": ["22222222", "33333333"], "doi": []} and bc["khong_do_duoc"] == []
    lenh_in = next(x for x in ghi if x[1].endswith("in_pdf_toan_van_kho.py"))
    assert lenh_in[lenh_in.index("--kho") + 1] == str(kho)


def _chuoi_thi_hanh(tep: Path) -> str:
    """Mọi chuỗi trong MÃ THI HÀNH của tệp: bỏ docstring/chuỗi đứng một mình; chú thích `#` vốn không có trong AST."""
    cay = ast.parse(tep.read_text(encoding="utf-8"))
    bo = {id(n.value) for n in ast.walk(cay) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    return "\n".join(n.value for n in ast.walk(cay)
                     if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in bo)


@pytest.mark.parametrize("dau", T.DAU_HIEU_GOM_CHUA_TRON)
def test_dau_hieu_con_trong_dong_thi_hanh_cua_bo_gom(dau):
    assert dau in _chuoi_thi_hanh(ROOT / "tools" / "gom_toan_van_dashboard.py"), (
        f"bộ gom không còn in «{dau}» — cập nhật DAU_HIEU_GOM_CHUA_TRON theo câu mới, không xoá chốt")


def test_bien_nhan_lan_oa_khong_do_duoc_thi_khong_ghi_truy_cap_mo(tmp_path):
    """Đúng ca đo thật: kho vắng ⇒ có báo cáo gom (khác rỗng) mà không định danh nào được ghi «đã thử truy cập mở»."""
    d = _de_tai_doi(tmp_path)
    ds = DS_GOM + [{"so": 5, "pmid": None, "doi": "10.2000/abc5"}]
    gom = T.gom_toan_van(ds, d / T.THU_MUC_TOAN_VAN, None, chay=_boom, gom_doi=lambda _d, _t: UPW_KHONG_EMAIL,
                         tim_kho_oa=lambda: None)
    assert gom and len(gom["khong_do_duoc"]) == 2      # trước bản vá: báo cáo khác rỗng là đủ để ghi lượt
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": gom}, tvt=_tvt_gia(),
                              hom_nay=date(2026, 11, 21))
    assert all(x["lan"] != "truy_cap_mo" for m in bn["muc"] for x in m["lan_da_thu"])
    assert [m["toan_van"] for m in bn["muc"]] == [True, False, False, True, False]   # phần đo toàn văn giữ nguyên


def test_bien_nhan_chi_ghi_cho_dinh_danh_lan_da_ket_luan(tmp_path):
    d = _de_tai_doi(tmp_path)
    gom = {"do_duoc": {"pmid": ["33333333"], "doi": []}, "khong_do_duoc": ["Unpaywall theo DOI — TLTK 5: URLError"]}
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc={"gom_toan_van": gom}, tvt=_tvt_gia(),
                              hom_nay=date(2026, 11, 21))
    assert _muc(bn, 2)["lan_da_thu"] == []     # chưa gửi đi gom ở lượt này (vd TLTK chỉ có trong bản thảo G7)
    assert [x["lan"] for x in _muc(bn, 3)["lan_da_thu"]] == ["truy_cap_mo"]
    assert _muc(bn, 5)["lan_da_thu"] == []     # DOI gặp lỗi mạng ⇒ chưa kết luận


def test_bien_nhan_doi_va_pmid_suy_tu_doi_ghi_dung_lan(tmp_path):
    d = _de_tai_doi(tmp_path)
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, tvt=_tvt_gia(), hom_nay=date(2026, 11, 21),
                              bc={"gom_toan_van": {"do_duoc": {"pmid": [], "doi": ["10.2000/abc5"]}}})
    assert [x["ket_qua"] for x in _muc(bn, 5)["lan_da_thu"]] == [
        "--gom-toan-van (Unpaywall theo DOI): không có bản truy cập mở hợp lệ"]
    bc = {"pmid_tu_doi": {"them": ["TLTK 5: DOI 10.2000/abc5 → PMID 55555555"]},
          "gom_toan_van": {"do_duoc": {"pmid": ["55555555"], "doi": []}}}
    bn = T.bien_nhan_toan_van(S, d, endnote=EN, kho=None, bc=bc, tvt=_tvt_gia(), hom_nay=date(2026, 11, 21))
    assert [x["ket_qua"] for x in _muc(bn, 5)["lan_da_thu"]] == [
        "--gom-toan-van (PMC + Unpaywall theo PMID): không có bản truy cập mở hợp lệ"]


def test_unpaywall_doi_loi_mang_khong_vao_da_do(tmp_path):
    gom = SimpleNamespace(_email_lich_su=lambda: "a@b.c", vi_tri_oa_duoc_luu=lambda uj, doi: (uj["urls"], uj.get("ly")),
                          _ghi_nguyen_tu=lambda dich, du_lieu: dich.write_bytes(du_lieu))
    tra = {"10.1/het": {"urls": []}, "10.1/vt-loi": {"urls": ["u-loi1", "u-loi2"]},
           "10.1/html": {"urls": ["u-loi1", "u-html"]}, "10.1/tra-loi": None}

    def tai(url):
        if url.startswith("https://api.unpaywall.org/v2/"):
            kq = tra[url.split("/v2/")[1].split("?")[0]]
            if kq is None:
                raise OSError("mất mạng")
            return json.dumps(kq).encode()
        if url == "u-html":
            return b"<html>"
        raise TimeoutError("hết giờ")
    ds = [{"so": i, "pmid": None, "doi": d} for i, d in enumerate(tra, 1)]
    bc = T.gom_doi_unpaywall(ds, tmp_path / "tv", gom_mod=gom, tai=tai)
    assert sorted(bc["da_do_doi"]) == ["10.1/het", "10.1/html"]
    assert [x.split(":")[0] for x in bc["khong_do_duoc"]] == ["TLTK 2", "TLTK 4"]
    assert not any("trang HTML" in x for x in bc["khong_luu"] if x.startswith("TLTK 2"))


def test_ma_thoat_lan_oa_khong_do_duoc_la_con_viec():
    sach = {"nap": {}, "khong_dinh_danh": {}, "thieu_toan_van": [], "lech": {}, "danh_muc": [], "khong_tach_duoc": [],
            "khong_lay_duoc_metadata": [], "kiem_trung": True}
    assert T.ma_thoat(sach) == T.MA_OK
    assert T.ma_thoat({**sach, "gom_toan_van": GOM_TRON}) == T.MA_OK
    assert T.ma_thoat({**sach, "gom_toan_van": {"do_duoc": {}, "khong_do_duoc": ["không thấy kho"]}}) == T.MA_MOT_PHAN
