# -*- coding: utf-8 -*-
"""Làn Chrome đóng gói (17/10/2026) — `tools/lan_chrome.py` + `tools/lan_chrome/{bo_luu.js,cau_hinh.json}` + vá
`tools/giam_sat_to_chuc.py`.

Đo thật 17/10/2026:
  • Làn toàn văn: hàm JS dựng tệp + cách lấy thân bài/PDF theo NXB chỉ nằm trong script TẠM của một phiên ⇒ phiên/máy khác
    dò lại từ đầu; 14/10 một PDF nhầm bài (liên kết /pdfft của tài liệu tham khảo) lọt vì không kiểm PII.
  • Làn nguồn: nạp cả trang WHO sinh 71 ứng viên giả từ bảng guideline DỰ KIẾN; dòng «Sep 2026» bị nối vào tiêu đề phía trên
    thành tiêu đề rác; SRC-015/SRC-022 nạp thành công mà vẫn `degraded`; vòng quét urllib hằng tuần hạ lại `degraded`.
Ngoại tuyến hoàn toàn: phiên/sổ/state/ứng viên đều là bản giả hoặc trỏ vào tmp_path.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


L = _nap("tools/lan_chrome.py", "_lan_chrome_20261017")
G = _nap("tools/giam_sat_to_chuc.py", "_gstc_lan_chrome_20261017")
PH = _nap("tools/phien_uy_quyen_chrome.py", "_puq_lan_chrome_20261017")
CH = L.doc_cau_hinh()


# ───────────────────────── cấu hình ─────────────────────────

def test_cau_hinh_that_dung_khuon_va_chi_ghi_dieu_da_kiem():
    assert L.kiem_cau_hinh(CH) == []
    for ten, c in CH["nxb"].items():
        assert c.get("kiem_lan_cuoi"), f"{ten}: cấu hình chưa kiểm thật không được vào bảng"
    for host, dich in CH["chuyen_huong"].items():
        assert dich in CH["nxb"], host
    assert {"SRC-015", "SRC-022"} <= set(CH["nguon"])


def test_kiem_cau_hinh_bat_tung_loi():
    xau = {"chuyen_huong": {"a.org": "khong-co"},
           "dau_khong_quyen_url": ["("],
           "nxb": {"x": {"mien": ["x.org"], "chon": "article", "pdf": "/doi/{issn}"},
                   "y": {"mien": ["y.org"], "chon": "article", "kiem_lan_cuoi": "nay", "khoa": "[" }},
           "nguon": {"SRC-1": {"url": "https://a"}, "SRC-2": {"dieu_kien": "tat_vpn"}}}
    noi = " | ".join(L.kiem_cau_hinh(xau))
    for chuoi in ("chuyen_huong.a.org", "dau_khong_quyen_url", "nxb.x: thiếu kiem_lan_cuoi", "biến lạ {issn}",
                  "nxb.y.khoa", "nguon.SRC-1"):
        assert chuoi in noi, chuoi
    assert "SRC-2" not in noi, "trạm khai dieu_kien là hợp lệ"


def test_tim_nxb_khop_dung_ten_va_mien_con():
    assert L.tim_nxb("www.sciencedirect.com", CH)[0] == "sciencedirect"
    assert L.tim_nxb("agsjournals.onlinelibrary.wiley.com", CH)[0] == "wiley"
    assert L.tim_nxb("evil-onlinelibrary.wiley.com.attacker.net", CH) == (None, None)
    assert L.tim_nxb("evilonlinelibrary.wiley.com", CH) == (None, None), "«*.x» chỉ khớp miền con THẬT (có dấu chấm)"
    assert L.tim_nxb("linkinghub.elsevier.com", CH) == (None, None), "miền chuyển hướng không phải trang bài"


def test_dien_cau_hinh_thay_bien_va_khong_doan():
    sd = L.dien_cau_hinh(CH["nxb"]["sciencedirect"], "https://www.sciencedirect.com/science/article/pii/S0140673624012345", "", ["x"])
    assert sd["pdf2"] == "/pii/S0140673624012345/pdfft" and sd["dauKhongQuyenUrl"] == ["x"]
    nejm = L.dien_cau_hinh(CH["nxb"]["nejm"], "https://www.nejm.org/doi/full/10.1056/NEJMoa1", "10.1056/NEJMoa1", [])
    assert nejm["pdf"] == "/doi/pdf/10.1056/NEJMoa1"
    with pytest.raises(ValueError, match="--doi"):
        L.dien_cau_hinh(CH["nxb"]["nejm"], "https://www.nejm.org/x", "", [])
    with pytest.raises(ValueError, match="pii"):
        L.dien_cau_hinh(CH["nxb"]["sciencedirect"], "https://www.sciencedirect.com/science/article/abs/x", "", [])
    assert "kiem_lan_cuoi" not in sd and "ghi_chu" not in sd, "chỉ truyền khoá bộ lưu dùng"


def test_chuoi_kiem_pdf_chong_pdf_nham_bai():
    assert L.chuoi_kiem_pdf(CH["nxb"]["sciencedirect"], "https://www.sciencedirect.com/science/article/pii/S01406736", "") == "S01406736"
    assert L.chuoi_kiem_pdf(CH["nxb"]["oup"], "https://academic.oup.com/eurheartj/x", "10.1093/eurheartj/ehaf170") == "ehaf170"
    assert L.chuoi_kiem_pdf(CH["nxb"]["nejm"], "https://www.nejm.org/x", "10.1056/a") == ""


def test_bo_luu_dung_dau_phien_ma_nhan_doc_duoc():
    js = L.BO_LUU.read_text(encoding="utf-8")
    assert "'<!-- ebm-phien:' + ma + ' pmid:' + pmid + ' url:' + url + ' -->" in js
    vi_du = "<!-- ebm-phien:20261017-164951 pmid:28898390 url:https://x -->"
    m = PH._DAU_PHIEN.search(vi_du)
    assert m and m.group("ma") == "20261017-164951" and m.group("pmid") == "28898390"


# ───────────────────────── phán quyết JS (node) ─────────────────────────

NODE = shutil.which("node")


def _danh_gia(t: dict) -> dict:
    ma = ("const m=require(process.argv[1]);process.stdout.write(JSON.stringify(m.danhGia(JSON.parse(process.argv[2]))))")
    r = subprocess.run([NODE, "-e", ma, str(L.BO_LUU), json.dumps(t)], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.mark.skipif(NODE is None, reason="máy không có node")
@pytest.mark.parametrize("t, ok, ly", [
    ({"soVung": 1, "doDai": 20000, "o": {}}, True, ""),
    ({"soVung": 0, "doDai": 20000, "o": {"chon": "article"}}, False, "không thấy vùng"),
    ({"soVung": 1, "doDai": 5000, "o": {}}, False, "thân bài ngắn"),
    ({"soVung": 1, "doDai": 20000, "deMuc": ["Abstract", " Access options "], "o": {"khoaDeMuc": ["Access options"]}},
     False, "đề mục tường phí"),
    ({"soVung": 1, "doDai": 20000, "href": "https://academic.oup.com/x?redirectedFrom=fulltext",
      "khongQuyenUrl": ["redirectedFrom=fulltext"], "o": {}}, False, "không quyền — URL"),
    ({"soVung": 1, "doDai": 20000, "vung": "… Purchase this article …", "o": {"khoa": "Purchase this article"}},
     False, "khoá trong thân bài"),
    ({"soVung": 1, "doDai": 20000, "trang": "Bài\nGet Access", "o": {"khoaTrang": "Get Access$"}}, False, "khoá trên trang"),
    ({"soVung": 1, "doDai": 20000, "trang": "Get Access\nphần còn lại", "o": {"khoaTrang": "Get Access$"}}, True, ""),
])
def test_danh_gia_than_bai(t, ok, ly):
    kq = _danh_gia(t)
    assert kq["ok"] is ok and ly in kq["ly"], kq


# ───────────────────────── toàn văn: toan-van · pdf · nhan ─────────────────────────

class _PhienGia:
    def __init__(self, kiem_tra: list[tuple[int, str]] | None = None):
        self.kiem_tra = list(kiem_tra or [(0, "được — phiên 20261017-1, Elsevier, www.sciencedirect.com")])
        self.goi_main: list[list[str]] = []

    def kiem(self, pmid, url, doi=""):
        return self.kiem_tra.pop(0) if len(self.kiem_tra) > 1 else self.kiem_tra[0]

    def phien_mo(self):
        return {"ma": "20261017-1"}

    def main(self, argv):
        self.goi_main.append(argv)
        return 0


def test_toan_van_in_ma_js_day_du_va_buoc_pdf_co_kiem_pii(capsys):
    url = "https://www.sciencedirect.com/science/article/pii/S0140673624012345"
    assert L.lenh_toan_van("42", url, "10.1016/x", None, 0, phien=_PhienGia(), cau_hinh=CH) == L.MA_OK
    ra = capsys.readouterr().out
    assert "window.__ebmTai = tai" not in ra and "g.__ebmTai = tai;" in ra, "in nguyên bộ lưu"
    assert 'await window.__ebmTai("20261017-1", "42", "' + url + '"' in ra
    assert '"pdf2": "/pii/S0140673624012345/pdfft"' in ra and '"dauKhongQuyenUrl"' in ra
    assert "lan_chrome.py pdf --pmid 42 --kiem S0140673624012345" in ra
    assert "lan_chrome.py nhan --pmid 42" in ra


@pytest.mark.parametrize("url, kiem, mong", [
    ("https://www.sciencedirect.com/science/article/pii/S1", [(3, "đã đủ 20 bài ở www.sciencedirect.com")], "đã đủ 20 bài"),
    ("https://www.unknown-journal.org/a", None, "chưa có cấu hình ĐÃ KIỂM"),
    ("https://linkinghub.elsevier.com/retrieve/pii/S1", None, "miền CHUYỂN HƯỚNG"),
])
def test_toan_van_tu_choi_khong_in_ma(capsys, url, kiem, mong):
    assert L.lenh_toan_van("42", url, "", None, 0, phien=_PhienGia(kiem), cau_hinh=CH) == L.MA_TU_CHOI
    ra = capsys.readouterr().out
    assert mong in ra and "__ebmTai" not in ra


def test_toan_van_cau_hinh_thu_cong_cho_mien_moi(capsys):
    ma = L.lenh_toan_van("42", "https://www.unknown-journal.org/a", "", '{"chon": "main", "min": 9000}', 0,
                         phien=_PhienGia(), cau_hinh=CH)
    assert ma == L.MA_OK and '"chon": "main"' in capsys.readouterr().out


def test_kiem_co_cho_doi_nhip_roi_moi_duoc(monkeypatch):
    monkeypatch.setattr(L.time, "sleep", lambda s: None)
    monkeypatch.setattr(L, "CHO_MOI_LAN", 0)
    ph = _PhienGia([(3, "chưa đủ nhịp ở x — đợi thêm 5 giây"), (3, "chưa đủ nhịp ở x — đợi thêm 1 giây"), (0, "được")])
    assert L._kiem_co_cho(ph, "1", "u", "", 100) == (0, "được")
    ph2 = _PhienGia([(3, "chưa đủ nhịp ở x"), (0, "được")])
    assert L._kiem_co_cho(ph2, "1", "u", "", 0)[0] == 3, "cho=0 ⇒ không đợi"


def test_pdf_in_ma_nut_co_chuoi_kiem(capsys):
    assert L.lenh_pdf("7", "ehaf170") == L.MA_OK
    assert "await window.__ebmPdfNut(\"7\", '', \"ehaf170\")" in capsys.readouterr().out


def test_nhan_html_truoc_pdf_bo_tep_dang_tai(tmp_path):
    # «PMID-5_phien (1).pdf» đứng TRƯỚC «…phien.html» theo bảng chữ cái — thứ tự HTML-trước phải do mã quyết, không do tên.
    for ten in ("PMID-5_phien.pdf", "PMID-5_phien (1).pdf", "PMID-5_phien.html", "PMID-5_phien.html.crdownload",
                "PMID-55_phien.html"):
        (tmp_path / ten).write_text("x")
    assert [p.name for p in L.tep_tai_ve("5", tmp_path)] == ["PMID-5_phien.html", "PMID-5_phien (1).pdf", "PMID-5_phien.pdf"]
    ph = _PhienGia()
    assert L.lenh_nhan("5", "https://u", "10.1/x", tmp_path, phien=ph) == 0
    assert [a[3] for a in ph.goi_main] == [str(tmp_path / n) for n in ("PMID-5_phien.html", "PMID-5_phien (1).pdf",
                                                                       "PMID-5_phien.pdf")]
    assert ph.goi_main[0][-2:] == ["--doi", "10.1/x"]
    assert L.lenh_nhan("6", "https://u", "", tmp_path, phien=ph) == L.MA_KHONG_DO


# ───────────────────────── hàng chờ ─────────────────────────

PHIEU_A = """| # | Trích dẫn | Toàn văn | Giải pháp |
| 1 | PMID 111 | ✓ máy có toàn văn | — |
| 2 | PMID 222 | ✗ chưa có | Làn Chrome có uỷ quyền: mở https://link.springer.com/x trong Chrome hồ sơ «Dr» |
| 3 | PMID 333 | ✗ chưa có | Làn Chrome có uỷ quyền: mở https://www.nejm.org/y trong Chrome hồ sơ «Dr» |
| 4 | PMID 444 | ✗ chưa có | bác sĩ tự đọc |
"""
PHIEU_B = "| 9 | PMID 222 | ✗ chưa có | mở https://khac.org/z trong Chrome |\n| 10 | PMID 555 | ✗ chưa có | mở https://a.org/q trong Chrome |\n"


def test_dung_hang_cho_tru_kho_khong_quyen_va_xep_uu_tien():
    ds = L.dung_hang_cho([PHIEU_A, PHIEU_B], co_trong_kho={"333"}, khong_quyen={"555"}, uu_tien={"444": 0, "222": 1},
                         doi_cua={"222": "10.1007/x"})
    assert [x["pmid"] for x in ds] == ["444", "222"], "đã có/không quyền bị bỏ; áp dụng trước cân nhắc"
    assert ds[1]["url"] == "https://link.springer.com/x" and ds[1]["mien"] == "link.springer.com", "phiếu đầu thắng"
    assert ds[1]["doi"] == "10.1007/x" and ds[0]["url"] == "" and ds[0]["mien"] == ""


# ───────────────────────── làn nguồn ─────────────────────────

TRANG_WHO = """WHO guidelines
Guideline proposed title Publication date (anticipated/released)
WHO guidelines on the clinical management of sepsis (jointly developed with WHE) 2026 Q4
Latest WHO guidelines approved by the Guidelines Review Committee
All →
7 October 2026
WHO guidelines on the integrated management of obesity in adolescents
Download Read More
10 September 2026
WHO guidelines for malaria
Download Read More
WHO publications
Bulletin of the World Health Organization
"""
TRANG_AHA = """Guidelines
Sep 2026
2026 Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery: A Report of the Joint Committee
Journal Article | PDF/EPUB | Hub
Aug 2026
2026 Guideline for Adult Stroke Rehabilitation and Recovery: A Guideline From the American Heart Association
Science Advisories
American Heart Association's Strategic Approach to Blood Pressure Control: A Science Advisory
"""


def test_cat_vung_who_chi_lay_guideline_da_phat_hanh():
    vung = L.cat_vung(TRANG_WHO, CH["nguon"]["SRC-022"])
    assert vung.splitlines() == ["WHO guidelines on the integrated management of obesity in adolescents",
                                 "WHO guidelines for malaria"], "bảng guideline DỰ KIẾN và dòng ngày/nút không được nạp"


def test_cat_vung_aha_bo_dong_ngay_khong_noi_vao_tieu_de():
    vung = L.cat_vung(TRANG_AHA, CH["nguon"]["SRC-015"])
    assert vung.splitlines() == [
        "2026 Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery: A Report of the Joint Committee",
        "2026 Guideline for Adult Stroke Rehabilitation and Recovery: A Guideline From the American Heart Association"]
    assert all("Aug 2026" not in t for t in G.rut_tieu_de_tu_van_ban(vung)), "dòng tháng-năm nối vào tiêu đề = tiêu đề rác"


def test_cat_vung_thieu_moc_thi_khong_doan():
    assert L.cat_vung(TRANG_WHO.replace("WHO publications", "Khác"), CH["nguon"]["SRC-022"]) is None
    assert L.cat_vung("không có gì", CH["nguon"]["SRC-015"]) is None


def test_trang_thai_nguon():
    c = CH["nguon"]["SRC-015"]
    nay = date(2026, 10, 17)
    assert L.trang_thai_nguon(CH["nguon"]["SRC-021"], None, nay)[0] == "⚪"
    assert L.trang_thai_nguon(c, {}, nay)[0] == "🛎"
    assert L.trang_thai_nguon(c, {"last_success_at": "2026-09-09"}, nay)[0] == "🛎"
    assert L.trang_thai_nguon(c, {"last_success_at": "2026-10-10"}, nay)[0] == "🟢"


class _GiamSatGia:
    def __init__(self, so: Path):
        self.SO_NGUON = so
        self.nap: list[str] = []

    def _nap_van_ban(self, sid, tep):
        self.nap.append(Path(tep).read_text(encoding="utf-8"))
        return 0


def test_nguon_bao_qua_han_ma_1_con_han_ma_0(tmp_path, capsys):
    so = tmp_path / "sources.json"
    nay = date(2026, 10, 17)
    so.write_text(json.dumps({"sources": [{"id": "SRC-015", "last_success_at": "2026-09-09"},
                                          {"id": "SRC-022", "last_success_at": "2026-10-17"}]}))
    assert L.lenh_nguon(None, giam_sat=_GiamSatGia(so), cau_hinh=CH, hom_nay=nay) == L.MA_QUA_HAN
    ra = capsys.readouterr().out
    assert "🛎 SRC-015" in ra and "lan_chrome.py nguon --cat SRC-015" in ra and "🟢 SRC-022" in ra and "⚪ SRC-021" in ra
    so.write_text(json.dumps({"sources": [{"id": "SRC-015", "last_success_at": "2026-10-16"},
                                          {"id": "SRC-022", "last_success_at": "2026-10-17"}]}))
    assert L.lenh_nguon(None, giam_sat=_GiamSatGia(so), cau_hinh=CH, hom_nay=nay) == L.MA_OK


def test_nguon_cat_chi_nap_dung_vung(tmp_path):
    tep = tmp_path / "who.txt"
    tep.write_text(TRANG_WHO, encoding="utf-8")
    gs = _GiamSatGia(tmp_path / "x.json")
    assert L.lenh_nguon(["SRC-022", str(tep)], giam_sat=gs, cau_hinh=CH) == 0
    assert gs.nap == ["WHO guidelines on the integrated management of obesity in adolescents\nWHO guidelines for malaria\n"]
    tep.write_text("trang chặn bot", encoding="utf-8")
    assert L.lenh_nguon(["SRC-022", str(tep)], giam_sat=gs, cau_hinh=CH) == L.MA_KHONG_DO and len(gs.nap) == 1
    assert L.lenh_nguon(["SRC-021", str(tep)], giam_sat=gs, cau_hinh=CH) == L.MA_TU_CHOI, "trạm chưa có vùng cắt"


# ───────────────────────── giam_sat_to_chuc: nạp trình duyệt + vòng quét ─────────────────────────

VAN_BAN_CO = ("2026 Guideline for Adult Stroke Rehabilitation and Recovery: A Guideline From the American Heart Association\n"
              "2026 AHA/ACC/ADA/ASN Guideline for the Prevention, Detection, Evaluation, and Management of CKM Syndrome\n")
VAN_BAN_KHONG = ("Checking your browser before accessing the site. This process is automatic. Your browser will redirect to "
                 "your requested content shortly. Please allow up to five seconds while we verify that you are a real visitor.")


def _tram(sid: str, status: str, lan: str | None) -> dict:
    return {"id": sid, "name": "thử", "org": "ACC/AHA", "tier": 1, "domain": ["tim mạch"], "access": "html-watch",
            "endpoint_or_url": f"https://vi.du/{sid}", "status": status, "last_success_at": lan, "known_gap": None}


def _dung(monkeypatch, tmp_path: Path, tram: list[dict], lan_chrome: dict | None) -> tuple[Path, list[str]]:
    so = tmp_path / "sources.json"
    so.write_text(json.dumps({"updated": "2000-01-01", "sources": tram}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setattr(G, "SO_NGUON", so)
    monkeypatch.setattr(G, "STATE", tmp_path / "state" / "giam-sat-to-chuc.json")
    monkeypatch.setattr(G, "RA", tmp_path / "surveillance")
    cfg = tmp_path / "lan_chrome.json"
    if lan_chrome is not None:
        cfg.write_text(json.dumps(lan_chrome), encoding="utf-8")
    else:
        cfg.unlink(missing_ok=True)   # «vắng cấu hình» thật — không để sót tệp của lần dựng trước trong cùng test
    monkeypatch.setattr(G, "LAN_CHROME", cfg)
    goi: list[str] = []

    def _gia(url):
        goi.append(url)
        return "<html><h2>2026 GOLD Report — Global Strategy for COPD management</h2></html>"
    monkeypatch.setattr(G, "_fetch", _gia)
    monkeypatch.setattr(sys, "argv", ["giam_sat_to_chuc.py"])
    return so, goi


def _doc(so: Path, sid: str) -> dict:
    return next(s for s in json.loads(so.read_text(encoding="utf-8"))["sources"] if s["id"] == sid)


# SRC-021 có ĐỦ vùng cắt nhưng khai điều kiện (cần tắt VPN) ⇒ làn trình duyệt CHƯA chạy được ⇒ vòng urllib vẫn chịu trách nhiệm.
LAN = {"nguon": {"SRC-015": {"url": "u", "dong_dau": "a", "dong_cuoi": "b", "chu_ky_ngay": 30},
                 "SRC-021": {"url": "u", "dong_dau": "a", "dong_cuoi": "b", "chu_ky_ngay": 30, "dieu_kien": "tat_vpn"}}}


def test_nap_van_ban_degraded_thanh_active(monkeypatch, tmp_path, capsys):
    so, _ = _dung(monkeypatch, tmp_path, [_tram("SRC-015", "degraded", "2026-09-09")], LAN)
    tep = tmp_path / "vb.txt"
    tep.write_text(VAN_BAN_CO, encoding="utf-8")
    G._nap_van_ban("SRC-015", str(tep))
    s = _doc(so, "SRC-015")
    assert s["status"] == "active" and s["last_success_at"] == date.today().isoformat()
    assert "↺ SRC-015" in capsys.readouterr().out


def test_nap_van_ban_khong_tieu_de_khong_ghi_gi(monkeypatch, tmp_path):
    so, _ = _dung(monkeypatch, tmp_path, [_tram("SRC-015", "degraded", "2026-09-09")], LAN)
    truoc = so.read_text(encoding="utf-8")
    tep = tmp_path / "vb.txt"
    tep.write_text(VAN_BAN_KHONG, encoding="utf-8")
    assert G._nap_van_ban("SRC-015", str(tep)) == 2
    assert so.read_text(encoding="utf-8") == truoc and not G.STATE.exists(), "0 tiêu đề KHÔNG phải thành công"


def test_vong_quet_khong_tai_tram_trinh_duyet_con_han(monkeypatch, tmp_path, capsys):
    hom_qua = (date.today() - timedelta(days=1)).isoformat()
    so, goi = _dung(monkeypatch, tmp_path, [_tram("SRC-015", "active", hom_qua)], LAN)
    G.main()
    assert goi == [] and _doc(so, "SRC-015")["status"] == "active"
    assert "◌ SRC-015: kênh trình duyệt" in capsys.readouterr().out


def test_vong_quet_tram_trinh_duyet_qua_han_thi_bao_khong_im(monkeypatch, tmp_path, capsys):
    cu = (date.today() - timedelta(days=45)).isoformat()
    so, goi = _dung(monkeypatch, tmp_path, [_tram("SRC-015", "active", cu)], LAN)
    assert G.main() == 1
    assert goi == [] and _doc(so, "SRC-015")["status"] == "degraded"
    assert "kênh TRÌNH DUYỆT quá hạn (45 ngày > chu kỳ 30)" in capsys.readouterr().out


def test_vong_quet_tram_dieu_kien_va_khong_cau_hinh_van_tai_urllib(monkeypatch, tmp_path):
    _, goi = _dung(monkeypatch, tmp_path, [_tram("SRC-021", "active", "2026-10-01"), _tram("SRC-010", "active", None)], LAN)
    G.main()
    assert goi == ["https://vi.du/SRC-021", "https://vi.du/SRC-010"]
    _, goi2 = _dung(monkeypatch, tmp_path, [_tram("SRC-015", "active", "2026-10-01")], None)
    G.main()
    assert goi2 == ["https://vi.du/SRC-015"], "vắng cấu hình làn Chrome ⇒ hành vi cũ"
