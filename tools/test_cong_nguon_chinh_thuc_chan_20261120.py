# -*- coding: utf-8 -*-
"""Cổng «ĐỌC NGUỒN CHÍNH THỨC» chuyển từ CẢNH BÁO sang CHẶN, có SỔ NỢ (20/11/2026). Ngoại tuyến hoàn toàn.

Bác sĩ («Hoàn thiện tất cả vấn đề trên», chọn «Chặn, có sổ nợ (Khuyến nghị)»): mục apply không PMID mà nguồn chính thức (DOI/URL)
chưa có bằng chứng đã đọc ⇒ CHẶN; 9 mục đã tồn (trang chủ GOLD ở 2 bản COPD cũ, NICE NG56 ở 5 bản «Người cao tuổi đa bệnh») vào sổ
nợ có hạn — cùng khuôn bánh cóc với BH161 (`no-toan-van-apply.json`).

Chốt: (1) ngoài sổ ⇒ lỗi; trong sổ còn hạn ⇒ cảnh báo; quá hạn ⇒ lỗi; (2) khoá sổ gồm KHOÁ NGUỒN — đổi URL là nguồn mới, không
còn được nợ; khác tên dashboard cũng không; (3) sổ hỏng ⇒ coi như vắng (fail-closed); (4) mục không DOI/URL ⇒ lỗi; (5) main
truyền tên dashboard vào cổng; (6) `so-no` lập MỘT lần, đòi nguyên văn lời bác sĩ, hạn ≤ 90 ngày, chỉ gồm mục đang chưa đọc,
gia hạn giữ nguyên danh sách; (7) phân loại của công cụ TRÙNG phân loại của cổng; (8) báo cáo và hòm việc nói «CHẶN».
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_VD = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"


def _nap(duong: Path, ten: str):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


V = _nap(_VD, "_cnct_vd")
D = _nap(REPO / "tools" / "doc_nguon_chinh_thuc.py", "_cnct_dn")
S = _nap(REPO / "tools" / "so_toan_van.py", "_cnct_stv")
T = _nap(REPO / "tools" / "tu_de_xuat_viec.py", "_cnct_tdx")

HOM_NAY = date(2026, 11, 20)
DA_DOC = "https://a.gov/da-doc"
CHUA = "https://a.gov/chua-doc"
K_CHUA = "url:https://a.gov/chua-doc"


def _ho_so(kho: Path, khoa: str):
    thu = kho / V.THU_MUC_NGUON_CHINH_THUC
    thu.mkdir(parents=True, exist_ok=True)
    hs = {"khoa": khoa, "cach": "may_tai", "so_ky_tu": 2000, "sha256": "b" * 64}
    (thu / (hashlib.sha256(khoa.encode()).hexdigest()[:20] + ".json")).write_text(json.dumps(hs), encoding="utf-8")


def _muc(iid, **f):
    return "{id:'%s', decision:'%s', pmid:'%s', doi:'%s', url:'%s'}" % (
        iid, f.get("decision", "apply"), f.get("pmid", ""), f.get("doi", ""), f.get("url", ""))


def _dash(tmp_path) -> tuple[Path, Path]:
    dash = tmp_path / "EBM-Dashboards"
    kho = dash / "toan_van_oa"
    (kho / "trinh_duyet").mkdir(parents=True)
    _ho_so(kho, "url:" + DA_DOC)
    (dash / "WebDashboard_EBM_VanDeCuThe_A_20261120.html").write_text(
        "<script>const DATA = {items:[" + ",".join([
            _muc("ITEM-01", url=DA_DOC), _muc("ITEM-02", url=CHUA), _muc("ITEM-03", pmid="12345678", url=CHUA),
            _muc("ITEM-04", decision="consider", url=CHUA)]) + "]};\n/* HẾT KHỐI DATA */</script>", encoding="utf-8")
    return dash, kho


def _so(dash: Path, han: str, muc: list[dict]):
    (dash / V.TEN_SO_NO_NGUON).write_text(json.dumps({"han": han, "muc": muc}), encoding="utf-8")


def _cong(items, kho, *, ten="WebDashboard_EBM_VanDeCuThe_A_20261120", hom_nay=HOM_NAY):
    e, w, o = [], [], []
    V.kiem_doc_nguon_chinh_thuc_apply(items, kho, e, w, o, ten_dashboard=ten, hom_nay=hom_nay)
    return e, w, o


TEN = "WebDashboard_EBM_VanDeCuThe_A_20261120"
NO_ITEM02 = [{"dashboard": TEN, "item": "ITEM-02", "khoa": K_CHUA}]


# ── (1)(4) cổng chặn ────────────────────────────────────────────────────────────────────────────
def test_ngoai_so_no_bi_chan_khong_doi_url_cung_bi_chan_muc_pmid_va_consider_khong_dung(tmp_path):
    _, kho = _dash(tmp_path)
    items = [_muc("ITEM-01", url=DA_DOC), _muc("ITEM-02", url=CHUA), _muc("ITEM-03", pmid="12345678", url=CHUA),
             _muc("ITEM-04", decision="consider", url=CHUA), _muc("ITEM-05")]
    e, w, o = _cong(items, kho)
    assert any("[ITEM-02]" in x and "KHÔNG có trong sổ nợ" in x and "chặn" in x for x in e)
    assert any("[ITEM-05]" in x and "không truy nguyên" in x for x in e), "không DOI/URL ⇒ chặn"
    assert not any(t in x for x in e + w for t in ("[ITEM-01]", "[ITEM-03]", "[ITEM-04]"))
    assert w == [] and any("1/3" in x for x in o)


def test_trong_han_canh_bao_qua_han_chan(tmp_path):
    dash, kho = _dash(tmp_path)
    _so(dash, "2026-12-20", NO_ITEM02)
    e, w, _ = _cong([_muc("ITEM-02", url=CHUA)], kho)
    assert e == [] and any("NỢ NGUỒN CHÍNH THỨC" in x and "còn 30 ngày" in x for x in w)
    e, w, _ = _cong([_muc("ITEM-02", url=CHUA)], kho, hom_nay=date(2026, 12, 21))
    assert any("NỢ QUÁ HẠN 2026-12-20" in x for x in e) and w == []


# ── (2) khoá sổ ─────────────────────────────────────────────────────────────────────────────────
def test_doi_url_hoac_khac_dashboard_khong_con_duoc_no(tmp_path):
    dash, kho = _dash(tmp_path)
    _so(dash, "2026-12-20", NO_ITEM02)
    e, _, _ = _cong([_muc("ITEM-02", url="https://a.gov/nguon-khac")], kho)
    assert any("KHÔNG có trong sổ nợ" in x for x in e), "đổi URL là nguồn MỚI"
    e, _, _ = _cong([_muc("ITEM-02", url=CHUA)], kho, ten="WebDashboard_EBM_VanDeCuThe_B_20261121")
    assert any("KHÔNG có trong sổ nợ" in x for x in e), "bản dashboard mới không thừa hưởng nợ"


# ── (3) sổ hỏng ─────────────────────────────────────────────────────────────────────────────────
def test_so_hong_coi_nhu_vang(tmp_path):
    dash, kho = _dash(tmp_path)
    for noi_dung in ("{hỏng", json.dumps({"han": "khong-phai-ngay", "muc": NO_ITEM02}), json.dumps({"han": "2026-12-20"}),
                     json.dumps({"han": "2026-12-20", "muc": 5})):
        (dash / V.TEN_SO_NO_NGUON).write_text(noi_dung, encoding="utf-8")
        e, w, _ = _cong([_muc("ITEM-02", url=CHUA)], kho)
        assert e and any("KHÔNG đọc được" in x for x in w), noi_dung
        assert D.phan_loai_no(D.quet_muc(sorted(dash.glob("WebDashboard_*.html")), V), V.bang_chung_nguon_chinh_thuc(kho),
                              D.doc_so_no(dash), HOM_NAY)["ngoai_so"], "công cụ cũng fail-closed: " + noi_dung


# ── (5) main truyền tên dashboard ───────────────────────────────────────────────────────────────
def test_main_truyen_ten_dashboard_vao_cong():
    ma = _VD.read_text(encoding="utf-8")
    i = ma.index("        kiem_doc_nguon_chinh_thuc_apply(items, Path(a.file)")
    dong_goi = ma[i:ma.index(")\n", i)]
    assert "ten_dashboard=Path(a.file).stem" in dong_goi
    assert D.TEN_SO_NO == V.TEN_SO_NO_NGUON
    assert (REPO / "sync/skills/dark-analyst/tools/verify_dashboard.py").read_bytes() == _VD.read_bytes()


# ── (6) lập/gia hạn sổ ──────────────────────────────────────────────────────────────────────────
def _a(**kw):
    d = {"tao": False, "gia_han": None, "han": None, "can_cu": None, "json": False, "ghi": False}
    d.update(kw)
    return argparse.Namespace(**d)


LOI = "«Hoàn thiện tất cả vấn đề trên» — chọn «Chặn, có sổ nợ (Khuyến nghị)»"


def test_lap_so_mot_lan_loi_bac_si_han_toi_da_chi_muc_chua_doc(tmp_path):
    dash, kho = _dash(tmp_path)
    ds = sorted(dash.glob("WebDashboard_*.html"))
    tep = dash / D.TEN_SO_NO
    assert D._lenh_so_no(_a(tao=True, han="2026-12-20", can_cu="ngắn", ghi=True), kho, ds, V, HOM_NAY) == 3
    assert D._lenh_so_no(_a(tao=True, han="2027-03-01", can_cu=LOI, ghi=True), kho, ds, V, HOM_NAY) == 3
    assert D._lenh_so_no(_a(tao=True, han="2026-11-20", can_cu=LOI, ghi=True), kho, ds, V, HOM_NAY) == 3
    assert D._lenh_so_no(_a(tao=True, han="2026-12-20", can_cu=LOI), kho, ds, V, HOM_NAY) == 0 and not tep.exists(), "chạy khô"
    assert D._lenh_so_no(_a(tao=True, han="2026-12-20", can_cu=LOI, ghi=True), kho, ds, V, HOM_NAY) == 0
    so = json.loads(tep.read_text(encoding="utf-8"))
    assert so["muc"] == NO_ITEM02 and so["can_cu"] == LOI and so["han"] == "2026-12-20"
    assert D._lenh_so_no(_a(tao=True, han="2026-12-20", can_cu=LOI, ghi=True), kho, ds, V, HOM_NAY) == 3, "chỉ lập MỘT lần"
    assert D._lenh_so_no(_a(), kho, ds, V, HOM_NAY) == 0, "chỉ còn nợ trong hạn ⇒ mã 0"
    assert D._lenh_so_no(_a(), kho, ds, V, date(2026, 12, 21)) == 1, "quá hạn ⇒ mã 1"
    assert D._lenh_so_no(_a(gia_han="2027-01-10", can_cu=LOI, ghi=True), kho, ds, V, HOM_NAY) == 0
    so2 = json.loads(tep.read_text(encoding="utf-8"))
    assert so2["muc"] == so["muc"] and so2["han"] == "2027-01-10" and so2["lich_su"][-1]["han_cu"] == "2026-12-20"
    e, w, _ = _cong([_muc("ITEM-02", url=CHUA)], kho, hom_nay=date(2026, 12, 21))
    assert e == [] and w, "cổng đọc đúng sổ do công cụ ghi (đã gia hạn)"


def test_gia_han_khi_chua_co_so_bi_tu_choi(tmp_path):
    dash, kho = _dash(tmp_path)
    assert D._lenh_so_no(_a(gia_han="2026-12-20", can_cu=LOI, ghi=True), kho,
                         sorted(dash.glob("WebDashboard_*.html")), V, HOM_NAY) == 3


# ── (7) công cụ và cổng cùng một phân loại ───────────────────────────────────────────────────────
def test_phan_loai_cong_cu_trung_cong(tmp_path):
    dash, kho = _dash(tmp_path)
    _so(dash, "2026-12-20", NO_ITEM02)
    ds = sorted(dash.glob("WebDashboard_*.html"))
    for hom_nay, khoa in ((HOM_NAY, "trong_han"), (date(2026, 12, 21), "qua_han")):
        no = D.phan_loai_no(D.quet_muc(ds, V), V.bang_chung_nguon_chinh_thuc(kho), D.doc_so_no(dash), hom_nay)
        assert [m["item"] for m in no[khoa]] == ["ITEM-02"]
        e, w, _ = _cong([_muc("ITEM-02", url=CHUA)], kho, hom_nay=hom_nay)
        assert bool(e) == (khoa == "qua_han") and bool(w) == (khoa == "trong_han")


# ── (8) báo cáo và hòm việc ─────────────────────────────────────────────────────────────────────
def test_so_toan_van_va_hom_viec_noi_chan(tmp_path):
    dash, kho = _dash(tmp_path)
    ng = S.quet_nguon_chinh_thuc(dash, kho, HOM_NAY)
    assert ng["chan"] == 1 and ng["no_trong_han"] == 0
    van = "\n".join(S.bao_cao([], {"ngoai_so": [], "qua_han": [], "trong_han": [], "han": None}, None, HOM_NAY, ng))
    assert "🔴 1 mục bị cổng CHẶN" in van and "chỉ CẢNH BÁO" not in van
    viec = [v for v in T.giac_quan_no_toan_van(dash, HOM_NAY) if "KHÔNG PMID" in v[1]]
    assert len(viec) == 1 and viec[0][0] == 1 and "ĐANG CHẶN" in viec[0][1]
    _so(dash, "2026-12-20", NO_ITEM02)
    viec = [v for v in T.giac_quan_no_toan_van(dash, HOM_NAY) if "KHÔNG PMID" in v[1]]
    assert len(viec) == 1 and viec[0][0] == 2 and "còn 30 ngày" in viec[0][1]
    viec = [v for v in T.giac_quan_no_toan_van(dash, date(2026, 12, 15)) if "KHÔNG PMID" in v[1]]
    assert viec[0][0] == 1, "≤ 7 ngày tới hạn ⇒ ưu tiên 1"
