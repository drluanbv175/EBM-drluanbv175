# -*- coding: utf-8 -*-
"""Bảo đảm đọc NGUỒN CHÍNH THỨC cho mục «Áp dụng ngay» không PMID (20/11/2026, bác sĩ «Làm 2,3,6» — mục 2). OFFLINE.

Chốt: (1) khoá nguồn ổn định và GIỮ query (openFDA/DailyMed định danh nhãn bằng query); (2) chỉ hồ sơ đủ chuẩn mới là bằng
chứng; (3) cổng chỉ CẢNH BÁO, không chặn, không đụng mục có PMID; (4) công cụ không ghi khi chạy khô, không tải miền chặn truy
cập tự động, từ chối trang chặn/lỗi/ngắn, chỉ lưu bản sao chữ ở miền giấy phép mở; (5) «bác sĩ đã đọc» đòi kết luận của bác sĩ.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent
_VD = _TOOLS.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _nap(ten, duong):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


V = _nap("_dnct_t_vd", _VD)
D = _nap("_dnct_t_tool", _TOOLS / "doc_nguon_chinh_thuc.py")

CHU_DAI = "Nội dung khuyến cáo an toàn thuốc đầy đủ. " * 80        # > 1500 ký tự


# ───── khoá nguồn ─────

@pytest.mark.parametrize("doi, url, khoa", [
    ("10.1016/J.KINT.2022.06.008", None, "doi:10.1016/j.kint.2022.06.008"),
    ("https://doi.org/10.1016/j.kint.2022.06.008", None, "doi:10.1016/j.kint.2022.06.008"),
    ("doi: 10.1161/STR.0000000000000513", None, "doi:10.1161/str.0000000000000513"),
    (None, "https://WWW.NICE.org.uk/guidance/ng56/", "url:https://www.nice.org.uk/guidance/ng56"),
    (None, "https://www.nice.org.uk/guidance/ng56#chuong-1", "url:https://www.nice.org.uk/guidance/ng56"),
    (None, "https://a.gov/x?utm_source=mail&b=2&a=1", "url:https://a.gov/x?a=1&b=2"),
    ("", "ftp://x/y", None),
    ("khong-phai-doi", "", None),
])
def test_khoa_nguon_chuan_hoa(doi, url, khoa):
    assert V.khoa_nguon_chinh_thuc(doi, url) == khoa


def test_query_dinh_danh_nhan_thuoc_khong_bi_gop():
    a = V.khoa_nguon_chinh_thuc(None, "https://api.fda.gov/drug/label.json?search=openfda.generic_name:metformin")
    b = V.khoa_nguon_chinh_thuc(None, "https://api.fda.gov/drug/label.json?search=openfda.generic_name:warfarin")
    assert a != b and a.startswith("url:https://api.fda.gov/drug/label.json?search=")


# ───── bằng chứng ─────

def _ho_so(kho: Path, khoa: str, **sua):
    hs = {"khoa": khoa, "cach": "may_tai", "so_ky_tu": 2000, "sha256": "a" * 64}
    hs.update(sua)
    thu = kho / V.THU_MUC_NGUON_CHINH_THUC
    thu.mkdir(parents=True, exist_ok=True)
    (thu / (hashlib.sha256(khoa.encode()).hexdigest()[:20] + json.dumps(sua, sort_keys=True)[:8].replace("/", "") + ".json")
     ).write_text(json.dumps(hs), encoding="utf-8")


def test_chi_ho_so_du_chuan_moi_la_bang_chung(tmp_path):
    kho = tmp_path / "toan_van_oa"
    _ho_so(kho, "url:https://a.gov/ok")
    _ho_so(kho, "url:https://a.gov/ngan", so_ky_tu=100)
    _ho_so(kho, "url:https://a.gov/cach-la", cach="doan")
    _ho_so(kho, "url:https://a.gov/sha-hong", sha256="xyz")
    _ho_so(kho, "khong-dung-khuon")
    (kho / V.THU_MUC_NGUON_CHINH_THUC / "hong.json").write_text("{hỏng", encoding="utf-8")
    (kho / "trinh_duyet").mkdir(parents=True)
    (kho / "trinh_duyet" / "bac-si-da-doc.jsonl").write_text(
        '{"pmid": "123"}\n{"nguon": "doi:10.1/abc", "ghi_chu": "đã đọc"}\ndòng hỏng\n{"nguon": "rác"}\n', encoding="utf-8")
    assert V.bang_chung_nguon_chinh_thuc(kho) == {"url:https://a.gov/ok", "doi:10.1/abc"}


# ───── cổng ─────

def _muc(iid, **f):
    return "{id:'%s', decision:'%s', pmid:'%s', doi:'%s', url:'%s'}" % (
        iid, f.get("decision", "apply"), f.get("pmid", ""), f.get("doi", ""), f.get("url", ""))


def _cong(items, kho):
    e, w, o = [], [], []
    V.kiem_doc_nguon_chinh_thuc_apply(items, kho, e, w, o)
    return e, w, o


def test_cong_chi_canh_bao_khong_chan_va_bo_qua_muc_co_pmid(tmp_path):
    kho = tmp_path / "toan_van_oa"
    kho.mkdir()
    _ho_so(kho, "url:https://a.gov/da-doc")
    items = [_muc("I1", url="https://a.gov/da-doc"), _muc("I2", url="https://a.gov/chua"),
             _muc("I3", pmid="12345678", url="https://a.gov/chua"), _muc("I4", decision="consider", url="https://a.gov/x"),
             _muc("I5")]
    e, w, o = _cong(items, kho)
    assert e == []
    assert any("[I2]" in x and "CHƯA có bằng chứng" in x for x in w)
    assert any("[I5]" in x and "không truy nguyên" in x for x in w)
    assert not any("[I3]" in x or "[I4]" in x or "[I1]" in x for x in w)
    assert any("1/3" in x for x in o)


def test_cong_khong_kho_la_chua_do(tmp_path):
    e, w, o = _cong([_muc("I1", url="https://a.gov/x")], tmp_path / "vang")
    assert e == [] and w == [] and any("⚪" in x for x in o)


def test_cong_duoc_goi_trong_main_sau_kiem_toan_van():
    ma = _VD.read_text(encoding="utf-8")
    i = ma.index("        kiem_toan_van_apply(items, Path(a.file)")
    assert ma.index("        kiem_doc_nguon_chinh_thuc_apply(items, Path(a.file)") > i


def test_hai_ban_git_cua_cong_trung_byte():
    ban2 = _TOOLS.parent / "sync" / "skills" / "dark-analyst" / "tools" / "verify_dashboard.py"
    assert ban2.read_bytes() == _VD.read_bytes()


# ───── công cụ ─────

HTML_OK = "<html><head><title>Drug Safety Update</title></head><body><nav>menu</nav><p>%s</p><script>x()</script></body></html>"


def _nhom(*khoa_url):
    return {k: {"khoa": k, "url": u, "doi": "", "muc": ["X I1"], "da_doc": False} for k, u in khoa_url}


def _lan_gia(url, doi):
    h = D.mien_cua(url)
    if doi.startswith("10.1016") or h == "evil.example":
        return {"lan": "bac_si", "ly_do": "NXB cấm", "can_dieu_khoan": False}
    if h in ("www.gov.uk", "open.example"):
        return {"lan": "may", "ly_do": "mở", "can_dieu_khoan": False}
    return {"lan": "trinh_duyet", "ly_do": "chặn/chưa kiểm", "can_dieu_khoan": h != "www.fda.gov"}


def test_tai_chay_kho_khong_ghi_va_ghi_that_dung_quy_tac(tmp_path):
    kho = tmp_path / "toan_van_oa"
    goi = []

    def fake(url):
        goi.append(url)
        if "ngan" in url:
            return url, "text/html", b"<title>OK</title><p>ngan</p>"
        if "chan" in url:
            return url, "text/html", ("<title>Just a moment...</title><p>%s</p>" % CHU_DAI).encode()
        if "chuyen" in url:
            return "https://evil.example/bai", "text/html", (HTML_OK % CHU_DAI).encode()
        return url, "text/html; charset=utf-8", (HTML_OK % CHU_DAI).encode()
    nhom = _nhom(("url:https://www.gov.uk/dsu/a", "https://www.gov.uk/dsu/a"),
                 ("url:https://open.example/b", "https://open.example/b"),
                 ("url:https://www.fda.gov/c", "https://www.fda.gov/c"),
                 ("url:https://www.gov.uk/ngan", "https://www.gov.uk/ngan"),
                 ("url:https://www.gov.uk/chan", "https://www.gov.uk/chan"),
                 ("url:https://www.gov.uk/chuyen", "https://www.gov.uk/chuyen"),
                 ("doi:10.1016/j.x.2024.1", ""))
    kq = D.tai(nhom, kho, ghi=False, tai_fn=fake, ngu=lambda s: None, lan_fn=_lan_gia)
    assert not kho.exists() and len(kq["doc_duoc"]) == 2
    assert "url:https://www.fda.gov/c" in kq["trinh_duyet"] and "https://www.fda.gov/c" not in goi     # làn trình duyệt: không tải
    assert {k for k, _ in kq["bac_si"]} == {"doi:10.1016/j.x.2024.1", "url:https://www.gov.uk/chuyen"}  # NXB cấm/chuyển hướng
    assert not any("doi.org" in u for u in goi)                                                        # NXB cấm: không tải
    assert {k for k, _ in kq["tu_choi"]} == {"url:https://www.gov.uk/ngan", "url:https://www.gov.uk/chan",
                                            "url:https://www.gov.uk/chuyen"}
    D.tai(nhom, kho, ghi=True, tai_fn=fake, ngu=lambda s: None, lan_fn=_lan_gia)
    thu = kho / V.THU_MUC_NGUON_CHINH_THUC
    hs = {json.loads(p.read_text(encoding="utf-8"))["khoa"]: p for p in thu.glob("*.json")}
    assert set(hs) == {"url:https://www.gov.uk/dsu/a", "url:https://open.example/b"}       # chuyển hướng ra ngoài: KHÔNG ghi
    assert hs["url:https://www.gov.uk/dsu/a"].with_suffix(".txt").exists()          # giấy phép mở ⇒ lưu bản sao chữ
    assert not hs["url:https://open.example/b"].with_suffix(".txt").exists()        # miền khác ⇒ chỉ độ dài + băm
    assert V.bang_chung_nguon_chinh_thuc(kho) == set(hs)                             # cổng nhận đúng hồ sơ vừa ghi
    chu = json.loads(hs["url:https://open.example/b"].read_text(encoding="utf-8"))
    assert "menu" not in hs["url:https://www.gov.uk/dsu/a"].with_suffix(".txt").read_text(encoding="utf-8")
    assert chu["cach"] == "may_tai" and chu["so_ky_tu"] >= V.SO_KY_TU_TOI_THIEU_NGUON


def _KHONG_UQ(ten):
    return None


def _CO_UQ(ten):
    return {"nxb": ten, "ngay": "2026-10-04"}


@pytest.mark.parametrize("url, doi, uq, lan, can", [
    ("https://doi.org/10.1016/j.kint.2022.06.008", "10.1016/j.kint.2022.06.008", _KHONG_UQ, "bac_si", False),
    ("https://doi.org/10.1016/j.kint.2022.06.008", "10.1016/j.kint.2022.06.008", _CO_UQ, "trinh_duyet", False),
    ("https://goldcopd.org/2026-gold-report/", "", _KHONG_UQ, "bac_si", False),
    ("https://www.gov.uk/drug-safety-update/x", "", _KHONG_UQ, "may", False),
    ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1", "", _KHONG_UQ, "may", False),
    ("https://api.fda.gov/drug/label.json?search=a", "", _KHONG_UQ, "may", False),      # openFDA: không phải miền chặn
    ("https://www.fda.gov/drugs/x", "", _KHONG_UQ, "trinh_duyet", False),               # miền chặn: không cần khai điều khoản
    ("https://www.ema.europa.eu/en/x", "", _KHONG_UQ, "trinh_duyet", False),
    ("https://psychiatriapolska.pl/x", "", _KHONG_UQ, "may", False),                    # giấy phép mở cấp NXB
    ("https://www.nice.org.uk/guidance/ng56", "", _KHONG_UQ, "trinh_duyet", True),      # chưa kiểm ⇒ đọc điều khoản trước
])
def test_lan_doc_theo_dieu_khoan_nxb(url, doi, uq, lan, can):
    r = D.lan_doc(url, doi, V=V, uy_quyen_fn=uq)
    assert (r["lan"], r["can_dieu_khoan"]) == (lan, can), r


def test_nap_trinh_duyet_theo_dieu_khoan(tmp_path):
    def lf(lan, can):
        return lambda u, d: {"lan": lan, "ly_do": "x", "can_dieu_khoan": can}
    goc = dict(tieu_de="Trang thật", so_ky_tu=3000, sha256="c" * 64, ghi=True)
    assert D.nap_trinh_duyet(tmp_path, "https://a.org/x", lan_fn=lf("bac_si", False), **goc)[0] == 1
    assert D.nap_trinh_duyet(tmp_path, "https://a.org/x", lan_fn=lf("trinh_duyet", True), **goc)[0] == 1
    assert D.nap_trinh_duyet(tmp_path, "https://a.org/x", lan_fn=lf("trinh_duyet", True), dieu_khoan="ngắn", **goc)[0] == 1
    assert not (tmp_path / V.THU_MUC_NGUON_CHINH_THUC).exists()
    assert D.nap_trinh_duyet(tmp_path, "https://doi.org/10.1234/abc", doi="10.1234/ABC", lan_fn=lf("trinh_duyet", True),
                             dieu_khoan="Trang điều khoản cho phép đọc bằng công cụ AI", **goc)[0] == 0
    hs = json.loads(next((tmp_path / V.THU_MUC_NGUON_CHINH_THUC).glob("*.json")).read_text(encoding="utf-8"))
    assert hs["khoa"] == "doi:10.1234/abc" and hs["dieu_khoan"].startswith("Trang điều khoản")    # khoá theo DOI của mục
    assert V.bang_chung_nguon_chinh_thuc(tmp_path) == {"doi:10.1234/abc"}


def test_tai_bo_qua_nguon_da_doc_va_loi_mang_sang_trinh_duyet(tmp_path):
    def loi(url):
        raise OSError("timeout")
    nhom = _nhom(("url:https://a.org/x", "https://a.org/x"))
    nhom["url:https://a.org/y"] = {"khoa": "url:https://a.org/y", "url": "https://a.org/y", "doi": "", "muc": [], "da_doc": True}
    kq = D.tai(nhom, tmp_path, ghi=True, tai_fn=loi, ngu=lambda s: None, lan_fn=lambda u, d: {"lan": "may"})
    assert kq["trinh_duyet"] == ["url:https://a.org/x"] and kq["doc_duoc"] == []


def test_boc_noi_dung_json_openfda_va_loai_la():
    du = json.dumps({"results": [{"warnings": ["Lactic acidosis " * 200], "id": "x"}]}).encode()
    td, chu = D.boc_noi_dung("application/json", du, "https://api.fda.gov/drug/label.json?search=a")
    assert "Lactic acidosis" in chu and td == "label.json"
    assert D.boc_noi_dung("application/json", b'{"error": {"code": "NOT_FOUND"}}', "u")[0] == "error"
    with pytest.raises(ValueError):
        D.boc_noi_dung("image/png", b"x", "https://a/b.png")


@pytest.mark.parametrize("tieu_de, so, sha, ma", [
    ("FDA Drug Safety Communication", 3000, "b" * 64, 0),
    ("Just a moment...", 3000, "b" * 64, 1),
    ("", 3000, "b" * 64, 1),
    ("Trang thật", 200, "b" * 64, 1),
    ("Trang thật", 3000, "khong-hex", 1),
])
def test_nap_trinh_duyet_kiem_dau_vao(tmp_path, tieu_de, so, sha, ma):
    assert D.nap_trinh_duyet(tmp_path, "https://www.fda.gov/x", tieu_de, so, sha, ghi=True)[0] == ma
    assert (len(list((tmp_path / V.THU_MUC_NGUON_CHINH_THUC).glob("*.json"))) if ma == 0 else 0) == (1 if ma == 0 else 0)


def test_bac_si_da_doc_doi_ket_luan_va_cong_nhan(tmp_path):
    assert D.bac_si_da_doc(tmp_path, "10.1016/j.kint.2022.06.008", None, ghi=True)[0] == 1
    assert D.bac_si_da_doc(tmp_path, "10.1016/j.kint.2022.06.008", "ok", ghi=True)[0] == 1
    assert D.bac_si_da_doc(tmp_path, "10.1016/j.kint.2022.06.008", "Đã đọc KDIGO, khớp mục.", ghi=False)[0] == 0
    assert not (tmp_path / "trinh_duyet").exists()
    assert D.bac_si_da_doc(tmp_path, "https://www.nice.org.uk/guidance/ng56/", "Đã đọc NG56, khớp mục.", ghi=True)[0] == 0
    assert V.bang_chung_nguon_chinh_thuc(tmp_path) == {"url:https://www.nice.org.uk/guidance/ng56"}


def test_so_toan_van_bao_cao_nguon_chinh_thuc():
    S = _nap("_dnct_t_stv", _TOOLS / "so_toan_van.py")
    dong = S.bao_cao([], {"ngoai_so": [], "qua_han": [], "trong_han": [], "han": None}, None,
                     __import__("datetime").date(2026, 11, 20), {"so_muc": 5, "so_nguon": 3, "da_doc": 1, "khong_khoa": 0})
    van = "\n".join(dong)
    assert "1/3 nguồn có bằng chứng" in van and "doc_nguon_chinh_thuc.py tai" in van
    assert "chưa đo được" in "\n".join(S.bao_cao([], {"ngoai_so": [], "qua_han": [], "trong_han": [], "han": None}, None,
                                                 __import__("datetime").date(2026, 11, 20), None))
