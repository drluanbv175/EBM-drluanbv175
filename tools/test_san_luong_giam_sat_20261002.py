#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy EV-02 (02/10/2026): chốt phủ giám sát chỉ đo KHAI BÁO nên xanh dù truy vấn «mù».

Đo thật 02/10: 10/42 chủ đề cho ≤3 bản ghi trong CẢ BỐN tầng/90 ngày (RA = 2) vì cụm truy vấn dài bị PubMed ngầm AND mọi từ.
Hai công cụ: `kiem_san_luong_giam_sat.py` (ĐO sản lượng thật qua esearch — ở đây dùng fetch GIẢ, ngoại tuyến) và
`ap_dung_de_xuat_watchlist.py` (chép đề xuất đã duyệt, có sao lưu, chỉ đổi `queries`). Không gọi mạng."""
from __future__ import annotations

import copy
import importlib.util as _ilu
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _nap(ten: str, tep: str):
    spec = _ilu.spec_from_file_location(ten, REPO / "tools" / tep)
    m = _ilu.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


sl = _nap("san_luong_gs", "kiem_san_luong_giam_sat.py")
ad = _nap("ap_dung_dx", "ap_dung_de_xuat_watchlist.py")

DESIGN = "(DESIGN_GIA)"


def _muc(ten, *, dem_query="q", datetypes=None):
    return {"topic": ten, "query": "cũ", "active": True, "truy_van_du_phong": "dp", "queries": [
        {"tang": "guideline", "query": f"({dem_query}) AND G", "datetype": "pdat", "loc_thiet_ke": True},
        {"tang": "sr_ma", "query": f"({dem_query}) AND S", "datetype": "pdat", "loc_thiet_ke": True},
        {"tang": "rct", "query": f"({dem_query}) AND R", "datetype": "pdat", "loc_thiet_ke": True},
        {"tang": "moi_vao_pubmed", "query": f"({dem_query})", "datetype": "edat", "loc_thiet_ke": False},
    ]}


# ================= kiem_san_luong_giam_sat =================
def test_thuat_ngu_dung_phep_ghep_cua_bo_quet():
    assert sl.thuat_ngu_that("a b", True, DESIGN) == "(a b) AND (DESIGN_GIA)"
    assert sl.thuat_ngu_that("a b", False, DESIGN) == "(a b)"


def test_design_la_hang_cua_bo_quet_chuan_khong_chep_tay():
    """DESIGN lấy từ bộ quét chuẩn — nếu bộ quét đổi, chốt này tự theo, không trôi."""
    bq = sl.nap_bo_quet()
    assert "randomized controlled trial[ptyp]" in bq.DESIGN and bq.EUTILS.startswith("https://eutils.ncbi")


def _fetch_theo(bang):
    def f(term, datetype, days):
        for khoa, v in bang.items():
            if khoa in term:
                if isinstance(v, Exception):
                    raise v
                return v
        return 0
    return f


def test_chu_de_tong_thap_la_mu():
    wl = {"topics": [_muc("MÙ", dem_query="mu"), _muc("ỔN", dem_query="on")]}
    b = sl.kiem(wl, _fetch_theo({"(mu)": 0, "(on)": 50}), DESIGN)
    assert b["mu"] == ["MÙ"] and [k["loai"] for k in b["chu_de"]] == ["MU", "ON"]
    assert sl.ma_thoat(b) == 1


def test_dung_ngay_nguong_la_mu_tren_nguong_la_on():
    wl = {"topics": [_muc("X", dem_query="x")]}
    ba_tang_tren = {"AND G": 1, "AND S": 1, "AND R": 1}
    mu = sl.kiem(wl, _fetch_theo({**ba_tang_tren, "(x)": 0}), DESIGN)["chu_de"][0]   # 1+1+1+0 = 3 = ngưỡng ⇒ MÙ
    on = sl.kiem(wl, _fetch_theo({**ba_tang_tren, "(x)": 1}), DESIGN)["chu_de"][0]   # 1+1+1+1 = 4 > ngưỡng ⇒ ỔN
    assert (mu["tong"], mu["loai"]) == (3, "MU") and (on["tong"], on["loai"]) == (4, "ON")


def test_tang_loi_khong_duoc_doc_thanh_0_hay_on():
    """NCBI chặn/mạng đứt ở một tầng ⇒ KHONG_DO (⚪): không mù, cũng không ổn."""
    wl = {"topics": [_muc("LỖI", dem_query="loi")]}
    b = sl.kiem(wl, _fetch_theo({"AND S": RuntimeError("NCBI chặn"), "(loi)": 0}), DESIGN)
    k = b["chu_de"][0]
    assert k["loai"] == "KHONG_DO" and k["do_duoc"] is False
    assert any(t["dem"] is None and "NCBI chặn" in t["loi"] for t in k["tang"])
    assert b["mu"] == [] and b["khong_do"] == ["LỖI"]


def test_khong_do_duoc_gi_ca_thi_ma_2_khong_phai_0():
    wl = {"topics": [_muc("A"), _muc("B")]}
    b = sl.kiem(wl, _fetch_theo({"(q)": RuntimeError("x")}), DESIGN)
    assert sl.ma_thoat(b) == 2
    assert sl.ma_thoat(sl.kiem({"topics": []}, _fetch_theo({}), DESIGN)) == 2  # không có chủ đề nào cũng KHÔNG phải «ổn»


def test_tat_ca_on_thi_ma_0():
    b = sl.kiem({"topics": [_muc("A", dem_query="a")]}, _fetch_theo({"(a)": 100}), DESIGN)
    assert sl.ma_thoat(b) == 0 and b["mu"] == []


def test_bo_qua_chu_de_tat_nhom_co_quan_va_loc_ten():
    wl = {"topics": [_muc("Hen"), dict(_muc("Tắt"), active=False),
                     {"topic": "NICE — hướng dẫn mới", "query": "x", "active": True},
                     _muc("Gout")]}
    b = sl.kiem(wl, _fetch_theo({"(q)": 9}), DESIGN)
    assert [k["topic"] for k in b["chu_de"]] == ["Hen", "Gout"] and b["bo_qua_khong_tang"] == ["NICE — hướng dẫn mới"]
    b2 = sl.kiem(wl, _fetch_theo({"(q)": 9}), DESIGN, loc_ten="gou")
    assert [k["topic"] for k in b2["chu_de"]] == ["Gout"]


def test_in_bao_cao_noi_ro_mu_va_khong_do(capsys):
    wl = {"topics": [_muc("MÙ", dem_query="mu"), _muc("LỖI", dem_query="loi")]}
    b = sl.kiem(wl, _fetch_theo({"(mu)": 0, "(loi)": RuntimeError("x")}), DESIGN)
    sl.in_bao_cao(b)
    out = capsys.readouterr().out
    assert "🔴 1 chủ đề CÓ THỂ MÙ" in out and "⚪ 1 chủ đề có tầng KHÔNG đo được" in out and "Cần bác sĩ kiểm chứng" in out


def test_main_thieu_watchlist_la_khong_do_duoc_ma_2(tmp_path, capsys):
    assert sl.main(["--watchlist", str(tmp_path / "khong-co.json")]) == 2
    assert "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out


# ================= ap_dung_de_xuat_watchlist =================
def _wl():
    return {"_about": "a", "_updated": "2026-08-25", "topics": [_muc("Hen", dem_query="asthma old"), _muc("Gout", dem_query="gout old"),
                                                                 _muc("Khác", dem_query="khac")]}


def _dx(*cap):
    topics = []
    for ten, q in cap:
        m = _muc(ten, dem_query=q)
        m["_ly_do"] = "đề xuất"   # khoá phụ trong đề xuất KHÔNG được lọt vào watchlist
        topics.append(m)
    return {"_about": "dx", "topics": topics}


def test_chi_thay_queries_cua_chu_de_de_xuat_con_lai_giu_nguyen():
    wl, dx = _wl(), _dx(("Hen", "asthma NEW"))
    doi, loi, kd = ad.lap_ke_hoach(wl, dx)
    assert loi == [] and [d[0] for d in doi] == ["Hen"] and kd == []
    moi = ad.ap_dung_vao(wl, doi, "2026-10-02")
    assert moi["topics"][0]["queries"] == dx["topics"][0]["queries"]
    assert moi["topics"][1] == wl["topics"][1] and moi["topics"][2] == wl["topics"][2]
    for khoa in ("topic", "query", "active", "truy_van_du_phong"):
        assert moi["topics"][0][khoa] == wl["topics"][0][khoa]
    assert "_ly_do" not in moi["topics"][0] and moi["_updated"] == "2026-10-02"
    assert wl["topics"][0]["queries"][0]["query"].startswith("(asthma old)"), "bản gốc không được bị sửa tại chỗ"


def test_chu_de_la_va_trung_ten_bi_tu_choi():
    wl = _wl()
    assert any("không có trong watchlist" in x for x in ad.lap_ke_hoach(wl, _dx(("Lạ", "q")))[1])
    wl["topics"].append(_muc("Hen"))
    assert any("trùng tên 2 lần" in x for x in ad.lap_ke_hoach(wl, _dx(("Hen", "q")))[1])
    assert any("hai lần" in x for x in ad.lap_ke_hoach(_wl(), _dx(("Hen", "q"), ("Hen", "r")))[1])


@pytest.mark.parametrize("sua,mong", [
    (lambda m: m["queries"].pop(), "bộ tầng"),                                      # bỏ tầng moi_vao_pubmed
    (lambda m: m["queries"][0].__setitem__("datetype", "xxx"), "datetype"),
    (lambda m: m["queries"][0].__setitem__("loc_thiet_ke", "true"), "loc_thiet_ke"),
    (lambda m: m["queries"][0].__setitem__("query", "(a AND b"), "ngoặc không cân"),
    (lambda m: m["queries"][0].__setitem__("query", "a) AND (b"), "ngoặc đóng thừa"),
    (lambda m: m["queries"][1].__setitem__("query", 'a AND "b'), "dấu nháy"),
    (lambda m: m["queries"][1].__setitem__("query", "a[ti AND b"), "ngoặc vuông"),
    (lambda m: m["queries"][2].__setitem__("query", "  "), "rỗng"),
    (lambda m: m["queries"][3].__setitem__("datetype", "pdat"), "bất biến"),        # moi_vao_pubmed phải edat
    (lambda m: m["queries"][3].__setitem__("loc_thiet_ke", True), "bất biến"),      # và KHÔNG lọc loại thiết kế
    (lambda m: m["queries"].append(copy.deepcopy(m["queries"][0])), "trùng tên tầng"),
    (lambda m: m.pop("queries"), "thiếu `queries`"),
])
def test_de_xuat_hong_bi_tu_choi_va_khong_ghi(sua, mong):
    dx = _dx(("Hen", "asthma NEW"))
    sua(dx["topics"][0])
    doi, loi, _ = ad.lap_ke_hoach(_wl(), dx)
    assert doi == [] and any(mong in x for x in loi), loi


def test_de_xuat_giong_het_la_khong_doi():
    wl = _wl()
    doi, loi, kd = ad.lap_ke_hoach(wl, {"topics": [copy.deepcopy(wl["topics"][1])]})
    assert (doi, loi, kd) == ([], [], ["Gout"])


def test_loc_chu_de_chi_xet_chu_de_khop():
    doi, loi, _ = ad.lap_ke_hoach(_wl(), _dx(("Hen", "A"), ("Lạ", "B")), loc_ten="hen")
    assert loi == [] and [d[0] for d in doi] == ["Hen"]


def _tep(tmp_path, wl, dx):
    w, d = tmp_path / "watchlist.json", tmp_path / "de-xuat.json"
    w.write_text(json.dumps(wl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    d.write_text(json.dumps(dx, ensure_ascii=False), encoding="utf-8")
    return w, d


def test_chay_kho_mac_dinh_khong_ghi_gi(tmp_path, capsys):
    w, d = _tep(tmp_path, _wl(), _dx(("Hen", "asthma NEW")))
    truoc = w.read_bytes()
    assert ad.main(["--watchlist", str(w), "--de-xuat", str(d)]) == 0
    assert w.read_bytes() == truoc and list(tmp_path.glob("*.bak-*")) == []
    assert "CHẠY KHÔ" in capsys.readouterr().out


def test_ap_dung_co_sao_luu_khop_byte_va_chi_doi_chu_de_duyet(tmp_path):
    wl = _wl()
    w, d = _tep(tmp_path, wl, _dx(("Hen", "asthma NEW")))
    goc = w.read_bytes()
    assert ad.main(["--watchlist", str(w), "--de-xuat", str(d), "--ap-dung"]) == 0
    bak = list(tmp_path.glob("watchlist.json.bak-*"))
    assert len(bak) == 1 and bak[0].read_bytes() == goc, "bản sao lưu phải KHỚP BYTE với bản gốc"
    moi = json.loads(w.read_text(encoding="utf-8"))
    assert moi["topics"][0]["queries"][0]["query"].startswith("(asthma NEW)")
    assert moi["topics"][1] == wl["topics"][1] and moi["topics"][2] == wl["topics"][2]
    assert list(tmp_path.glob("*.tmp*")) == [], "không để lại tệp tạm"


def test_ap_dung_lan_hai_khong_doi_gi_va_khong_sao_luu_them(tmp_path, capsys):
    w, d = _tep(tmp_path, _wl(), _dx(("Hen", "asthma NEW")))
    assert ad.main(["--watchlist", str(w), "--de-xuat", str(d), "--ap-dung"]) == 0
    capsys.readouterr()
    assert ad.main(["--watchlist", str(w), "--de-xuat", str(d), "--ap-dung"]) == 0
    assert "Không có gì để đổi" in capsys.readouterr().out
    assert len(list(tmp_path.glob("watchlist.json.bak-*"))) == 1


def test_de_xuat_hong_thi_ma_1_va_khong_ghi_ca_khi_co_chu_de_hop_le(tmp_path, capsys):
    dx = _dx(("Hen", "asthma NEW"), ("Gout", "gout NEW"))
    dx["topics"][1]["queries"][0]["query"] = "(hỏng"      # MỘT chủ đề hỏng ⇒ KHÔNG ghi chủ đề nào
    w, d = _tep(tmp_path, _wl(), dx)
    truoc = w.read_bytes()
    assert ad.main(["--watchlist", str(w), "--de-xuat", str(d), "--ap-dung"]) == 1
    assert w.read_bytes() == truoc and list(tmp_path.glob("*.bak-*")) == []
    assert "KHÔNG ghi gì" in capsys.readouterr().out


def test_thieu_tep_la_ma_2(tmp_path):
    assert ad.main(["--watchlist", str(tmp_path / "x.json"), "--de-xuat", str(tmp_path / "y.json")]) == 2


def test_de_xuat_that_trong_kho_neu_co_thi_hop_le_voi_watchlist_that():
    """Nếu máy có cả watchlist thật và tệp đề xuất của máy ⇒ đề xuất PHẢI qua kiểm hợp lệ (⚪ bỏ qua khi vắng)."""
    wl_p, dx_p = REPO / "EBM-Dashboards" / "watchlist.json", REPO / "EBM-Dashboards" / "watchlist.de-xuat.json"
    if not (wl_p.exists() and dx_p.exists()):
        pytest.skip("máy không có EBM-Dashboards/watchlist(.de-xuat).json — ⚪ không kiểm được, KHÔNG phải đạt")
    _doi, loi, _kd = ad.lap_ke_hoach(json.loads(wl_p.read_text(encoding="utf-8")), json.loads(dx_p.read_text(encoding="utf-8")))
    assert loi == [], loi

# ================= dùng lại kết quả đo (không gọi mạng khi không cần) =================
from datetime import datetime, timedelta, timezone  # noqa: E402

BG = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)


def _bc(sha="s1", gio_truoc=24.0, nguong=3, ngay=90, khong_do=None, chu_de=None):
    return {"nguong": nguong, "so_ngay": ngay, "chu_de": [{"topic": "A"}] if chu_de is None else chu_de,
            "khong_do": khong_do or [], "mu": [], "bo_qua_khong_tang": [], "watchlist_sha256": sha,
            "do_luc": (BG - timedelta(hours=gio_truoc)).isoformat()}


def _ghi(tmp_path, d):
    p = tmp_path / "gan-nhat.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


def test_dung_lai_khi_cung_watchlist_con_moi(tmp_path):
    assert sl.dung_lai_duoc(_ghi(tmp_path, _bc()), "s1", 3, 90, 7, BG) is not None


@pytest.mark.parametrize("sua,sha,nguong,ngay", [
    (dict(sha="s_khac"), "s1", 3, 90),                 # đã đổi watchlist ⇒ đo lại
    (dict(gio_truoc=24 * 8), "s1", 3, 90),             # quá 7 ngày
    (dict(gio_truoc=-2), "s1", 3, 90),                 # dấu thời gian tương lai
    (dict(khong_do=["X"]), "s1", 3, 90),               # lần trước đo dở (tầng lỗi) ⇒ không dùng lại
    (dict(chu_de=[]), "s1", 3, 90),                    # kết quả rỗng ⇒ không tin
    (dict(), "s1", 5, 90),                             # đổi ngưỡng
    (dict(), "s1", 3, 30),                             # đổi cửa sổ
])
def test_khong_dung_lai_khi(tmp_path, sua, sha, nguong, ngay):
    assert sl.dung_lai_duoc(_ghi(tmp_path, _bc(**sua)), sha, nguong, ngay, 7, BG) is None


def test_tep_thieu_khoa_thi_khong_dung_lai(tmp_path):
    d = _bc()
    d.pop("bo_qua_khong_tang")
    assert sl.dung_lai_duoc(_ghi(tmp_path, d), "s1", 3, 90, 7, BG) is None


@pytest.mark.parametrize("noi_dung", ["", "{hỏng", "[]", '{"do_luc": "không-phải-ngày"}', "{}"])
def test_tep_cu_hong_thi_khong_dung_lai(tmp_path, noi_dung):
    p = tmp_path / "x.json"
    p.write_text(noi_dung, encoding="utf-8")
    assert sl.dung_lai_duoc(p, "s1", 3, 90, 7, BG) is None
    assert sl.dung_lai_duoc(tmp_path / "khong-co.json", "s1", 3, 90, 7, BG) is None


def test_main_dung_lai_khong_goi_mang_va_giu_ma_thoat(tmp_path, monkeypatch, capsys):
    import hashlib
    wl_text = json.dumps({"topics": [_muc("Hen", dem_query="a")]})
    w = tmp_path / "wl.json"
    w.write_text(wl_text, encoding="utf-8")
    cu = _bc(sha=hashlib.sha256(wl_text.encode("utf-8")).hexdigest(), gio_truoc=1.0)
    cu["do_luc"] = datetime.now(timezone.utc).isoformat()
    cu["mu"] = ["Hen"]
    cu["chu_de"] = [{"topic": "Hen", "tang": [], "tong": 0, "loai": "MU", "do_duoc": True}]
    j = _ghi(tmp_path, cu)
    def cam_mang(*_a, **_k):
        raise AssertionError("không được gọi mạng khi dùng lại kết quả")
    monkeypatch.setattr(sl, "tao_fetch_ncbi", lambda *_: cam_mang)
    ma = sl.main(["--watchlist", str(w), "--json", str(j), "--dung-lai-neu-moi-hon-ngay", "7"])
    assert ma == 1 and "Dùng lại lượt đo" in capsys.readouterr().out
