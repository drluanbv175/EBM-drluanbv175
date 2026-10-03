#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy tín hiệu «chủ đề 0 ứng viên nhiều lượt tuần liền» (03–04/10/2026).

Đếm thô 03/10: W39 + W40 có 10/47 chủ đề watchlist 0 ứng viên mà bộ quét vẫn PASS; đề xuất viết lại truy vấn soạn 02/10
nằm chờ; chốt sản lượng (EV-02) không nằm trong dây chuyền tuần ⇒ không ai thấy. Các test này khoá: (1) chỉ chủ đề
PASS mới là «đo được» — PASS_DEGRADED/FAIL/tệp hỏng KHÔNG BAO GIỜ thành «0 ứng viên»; (2) lượt không đo được nằm giữa
không bắc cầu; (3) đề xuất chờ duyệt là việc 👤; (4) nguyên liệu hỏng ⇒ ⚪, không phải «không có chủ đề mù».
Ngoại tuyến hoàn toàn (dữ liệu giả trong tmp_path)."""
from __future__ import annotations

import ast
import hashlib
import importlib.util as _ilu
import inspect
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"


def _nap(ten: str, tep: str):
    spec = _ilu.spec_from_file_location(ten, TOOLS / tep)
    m = _ilu.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


K0 = _nap("k0uv_t20261004", "kiem_chuoi_0_ung_vien.py")
SL = _nap("sl_t20261004", "kiem_san_luong_giam_sat.py")
TDX = _nap("tdxv_t20261004", "tu_de_xuat_viec.py")

BAY_GIO = datetime(2026, 10, 4, 9, 0, tzinfo=timezone.utc)


# ── dữ liệu giả ─────────────────────────────────────────────────────────────────────────────────────────────────────
def _queries(dem: str = "q") -> list[dict]:
    return [
        {"tang": "guideline", "query": f"({dem}) AND G", "datetype": "pdat", "loc_thiet_ke": True},
        {"tang": "sr_ma", "query": f"({dem}) AND S", "datetype": "pdat", "loc_thiet_ke": True},
        {"tang": "rct", "query": f"({dem}) AND R", "datetype": "pdat", "loc_thiet_ke": True},
        {"tang": "moi_vao_pubmed", "query": f"({dem})", "datetype": "edat", "loc_thiet_ke": False},
    ]


def _chu_de_wl(ten: str, *, co_tang: bool = True, active: bool = True) -> dict:
    t = {"topic": ten, "query": "cũ", "active": active}
    if co_tang:
        t["queries"] = _queries(ten)
    return t


def _ghi_luot(thu_muc: Path, tuan: int, chu_de: dict, *, status: str = "PASS", han_che: dict | None = None,
              nam: int = 2026) -> Path:
    """chu_de = {tên: (status chủ đề, số ứng viên)} — số ứng viên None ⇒ `candidates` không phải danh sách."""
    thu_muc.mkdir(parents=True, exist_ok=True)
    p = thu_muc / f"tuan-{nam}-W{tuan:02d}-quet.json"
    d = {"kind": "surveillance", "status": status, "topics": [
        {"topic": ten, "status": st, "candidates": ([{"pmid": str(i)} for i in range(n)] if n is not None else "x")}
        for ten, (st, n) in chu_de.items()]}
    if han_che:
        d["quan_sat_han_che"] = [{"topic": t, "kenh_khac": k} for t, k in han_che.items()]
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return p


def _ghi_wl(dash: Path, chu_de: list[dict]) -> str:
    dash.mkdir(parents=True, exist_ok=True)
    txt = json.dumps({"topics": chu_de}, ensure_ascii=False, indent=1)
    (dash / "watchlist.json").write_text(txt, encoding="utf-8")
    return txt


def _ghi_de_xuat(dash: Path, chu_de: list[dict], about: str = "Đề xuất soạn 02/10/2026") -> None:
    (dash / "watchlist.de-xuat.json").write_text(
        json.dumps({"_about": about, "topics": chu_de}, ensure_ascii=False), encoding="utf-8")


def _ghi_san_luong(tep: Path, wl_text: str, theo: dict, *, tuoi_ngay: float = 1, khong_do: list | None = None,
                   sha: str | None = None) -> None:
    d = {"nguong": SL.NGUONG_MU, "so_ngay": SL.SO_NGAY,
         "chu_de": [{"topic": t, "loai": loai, "tong": tong} for t, (loai, tong) in theo.items()],
         "mu": [t for t, (loai, _) in theo.items() if loai == "MU"], "khong_do": khong_do or [],
         "bo_qua_khong_tang": [], "do_luc": (BAY_GIO - timedelta(days=tuoi_ngay)).isoformat(),
         "watchlist_sha256": sha or SL.bam_watchlist(wl_text)}
    tep.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


def _bo_quet_gia(tmp_path: Path, bang: dict | None = None) -> Path:
    p = tmp_path / "surveillance_scan_gia.py"
    p.write_text(f"KENH_THAT_NGOAI_PUBMED: dict[str, str] = {bang or {}!r}\n", encoding="utf-8")
    return p


def _pt(dash: Path, tmp_path: Path, san_luong: Path | None = None, bang: dict | None = None, **kw) -> dict:
    return K0.phan_tich(dash, san_luong or (tmp_path / "khong-co-san-luong.json"), _bo_quet_gia(tmp_path, bang),
                        bay_gio=BAY_GIO, **kw)


# ── đọc lượt ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_doc_cac_luot_xep_theo_nam_tuan_trong_ten_va_lay_moi_nhat(tmp_path):
    q = tmp_path / "surveillance"
    for nam, tuan in ((2025, 52), (2026, 1), (2026, 9), (2026, 10)):
        _ghi_luot(q, tuan, {"A": ("PASS", 0)}, nam=nam)
    (q / "tuan-2026-W5-quet.json").write_text(json.dumps({"status": "PASS", "topics": []}), encoding="utf-8")
    (q / "tuan-2026-W11-quet.json.bak").write_text("{}", encoding="utf-8")
    (q / "tuan-2026-W11.md").write_text("x", encoding="utf-8")
    nhan = [lt["nhan"] for lt in K0.doc_cac_luot(q, 8)]
    assert nhan == ["W52", "W01", "W05", "W09", "W10"], "xếp theo (năm, tuần) trong TÊN, bỏ tệp không đúng khuôn"
    assert [lt["nhan"] for lt in K0.doc_cac_luot(q, 3)] == ["W05", "W09", "W10"]


def test_tep_hong_ca_luot_khong_do_duoc(tmp_path):
    q = tmp_path / "surveillance"
    q.mkdir()
    (q / "tuan-2026-W39-quet.json").write_text("{hỏng", encoding="utf-8")
    (q / "tuan-2026-W40-quet.json").write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
    ds = K0.doc_cac_luot(q)
    assert [lt["doc_duoc"] for lt in ds] == [False, False]
    assert K0.do_trong_luot(ds[0], "A") == ("khong_do", "tệp quét không đọc được")


@pytest.mark.parametrize("luot_status, chu_de, ky_vong", [
    ("PASS", {"A": ("PASS", 0)}, "0"),
    ("PASS", {"A": ("PASS", 2)}, "co"),
    ("PARTIAL", {"A": ("PASS", 0)}, "0"),            # trạng thái lượt là số của TẬP HỢP, không của từng chủ đề
    ("PASS", {"A": ("PASS_DEGRADED", 0)}, "khong_do"),
    ("PASS", {"A": ("FAIL", 0)}, "khong_do"),
    ("FAIL", {"A": ("PASS", 0)}, "khong_do"),
    ("PASS", {"A": ("PASS", None)}, "khong_do"),     # candidates không phải danh sách
    ("PASS", {"B": ("PASS", 0)}, "vang"),
])
def test_do_trong_luot(tmp_path, luot_status, chu_de, ky_vong):
    _ghi_luot(tmp_path, 40, chu_de, status=luot_status)
    luot = K0.doc_cac_luot(tmp_path)[0]
    assert K0.do_trong_luot(luot, "A")[0] == ky_vong


# ── chuỗi liền ──────────────────────────────────────────────────────────────────────────────────────────────────────
def _chuoi(tmp_path, cac: list[tuple[str, int | None] | None], tuan_dau: int = 35) -> dict:
    """cac: (status chủ đề, số ứng viên) cũ → mới; None ⇒ chủ đề vắng ở lượt đó."""
    for i, x in enumerate(cac):
        _ghi_luot(tmp_path, tuan_dau + i, {} if x is None else {"A": x})
    return K0.chuoi_cua(K0.doc_cac_luot(tmp_path), "A")


def test_chuoi_dem_nguoc_tu_luot_moi_nhat_va_dung_o_luot_co_ung_vien(tmp_path):
    ch = _chuoi(tmp_path, [("PASS", 0), ("PASS", 3), ("PASS", 0), ("PASS", 0)])
    assert (ch["lien"], ch["cac_luot_0"], ch["ngat_boi"]) == (2, ["W37", "W38"], "")


def test_chuoi_khong_bac_cau_qua_luot_khong_do_duoc(tmp_path):
    ch = _chuoi(tmp_path, [("PASS", 0), ("PASS_DEGRADED", 0), ("PASS", 0)])
    assert ch["lien"] == 1 and ch["ngat_boi"] == "W36 (PASS_DEGRADED)", "bắc cầu qua lượt suy giảm = báo đỏ giả"


def test_luot_moi_nhat_khong_do_duoc_khong_xoa_tin_hieu_da_co(tmp_path):
    ch = _chuoi(tmp_path, [("PASS", 0), ("PASS", 0), ("FAIL", 0)])
    assert ch["lien"] == 2 and ch["dau_khong_do"] == ["W37 (FAIL)"]


def test_chu_de_vang_o_luot_cu_thi_chuoi_dung(tmp_path):
    ch = _chuoi(tmp_path, [None, ("PASS", 0)])
    assert (ch["lien"], ch["ngat_boi"]) == (1, "")


def test_tuan_thieu_tep_quet_van_la_hai_luot_lien(tmp_path):
    """Bộ quét dùng con trỏ tăng dần (K8): lượt sau phủ cửa sổ của tuần không chạy ⇒ W37 và W39 là hai lượt LIỀN."""
    _ghi_luot(tmp_path, 37, {"A": ("PASS", 0)})
    _ghi_luot(tmp_path, 39, {"A": ("PASS", 0)})
    ch = K0.chuoi_cua(K0.doc_cac_luot(tmp_path), "A")
    assert (ch["lien"], ch["cac_luot_0"]) == (2, ["W37", "W39"])
    assert "CON TRỎ TĂNG DẦN" in K0.__doc__


# ── phân tích + phân nhóm ───────────────────────────────────────────────────────────────────────────────────────────
def _kich_ban_nhom(tmp_path):
    dash = tmp_path / "EBM-Dashboards"
    wl = [_chu_de_wl("A_duyet"), _chu_de_wl("B_hanche"), _chu_de_wl("C_khongtang", co_tang=False),
          _chu_de_wl("D_cando"), _chu_de_wl("E_mu"), _chu_de_wl("F_on"), _chu_de_wl("G_tat", active=False),
          _chu_de_wl("I_co_ung_vien")]
    wl_text = _ghi_wl(dash, wl)
    q = dash / "surveillance"
    tat_ca = {t["topic"]: ("PASS", 0) for t in wl} | {"H_roi_watchlist": ("PASS", 0), "I_co_ung_vien": ("PASS", 4)}
    _ghi_luot(q, 39, tat_ca)
    _ghi_luot(q, 40, tat_ca | {"I_co_ung_vien": ("PASS", 0)}, han_che={"B_hanche": "kênh khác X"})
    _ghi_de_xuat(dash, [{"topic": "A_duyet", "queries": _queries("A_duyet_moi")}])
    sl = tmp_path / "san-luong.json"
    _ghi_san_luong(sl, wl_text, {"E_mu": ("MU", 2), "F_on": ("ON", 40)})
    return dash, sl


def test_phan_tich_phan_nhom_dung_duong_xu_ly(tmp_path):
    dash, sl = _kich_ban_nhom(tmp_path)
    pt = _pt(dash, tmp_path, sl)
    assert pt["do_duoc"] and pt["canh_bao"] == []
    nhom = {m["topic"]: m["nhom"] for m in pt["chu_de"]}
    assert nhom == {"A_duyet": "duyet_de_xuat", "B_hanche": "han_che_da_biet", "C_khongtang": "khong_tang",
                    "D_cando": "can_do", "E_mu": "mu_chua_de_xuat", "F_on": "san_luong_du"}
    assert "G_tat" not in nhom and "H_roi_watchlist" not in nhom, "chủ đề tắt/rời watchlist không còn giám sát"
    assert "I_co_ung_vien" not in nhom, "0 chỉ ở MỘT lượt (lượt trước có ứng viên) chưa phải chuỗi"


def test_kenh_khac_lay_tu_bang_bo_quet_chuan_khi_luot_khong_ghi(tmp_path):
    dash, sl = _kich_ban_nhom(tmp_path)
    pt = _pt(dash, tmp_path, sl, bang={"D_cando": "trạm web hội"})
    assert {m["topic"]: m["nhom"] for m in pt["chu_de"]}["D_cando"] == "han_che_da_biet"


def test_de_xuat_da_ap_khong_con_la_viec(tmp_path):
    dash, sl = _kich_ban_nhom(tmp_path)
    _ghi_de_xuat(dash, [{"topic": "A_duyet", "queries": _queries("A_duyet")}])   # trùng hiện hành ⇒ đã áp
    pt = _pt(dash, tmp_path, sl)
    assert pt["de_xuat"]["trang_thai"] == {"A_duyet": "da_ap"}
    viec, _ = K0.viec_tu_phan_tich(pt)
    assert not [v for v in viec if v[1] == "👤"]


def test_de_xuat_loi_van_la_viec_cua_bac_si(tmp_path):
    dash, sl = _kich_ban_nhom(tmp_path)
    _ghi_de_xuat(dash, [{"topic": "A_duyet", "queries": _queries("A_duyet_moi")[:3]}])   # bỏ tầng moi_vao_pubmed
    pt = _pt(dash, tmp_path, sl)
    assert pt["de_xuat"]["trang_thai"] == {"A_duyet": "loi"} and pt["de_xuat"]["so_loi"] == 1
    assert {m["topic"]: m["nhom"] for m in pt["chu_de"]}["A_duyet"] == "duyet_de_xuat"
    viec, _ = K0.viec_tu_phan_tich(pt)
    assert any(v[1] == "👤" and "đề xuất có 1 lỗi" in v[2] for v in viec)


def test_de_xuat_hong_la_canh_bao_khong_phai_khong_co_de_xuat(tmp_path):
    dash, sl = _kich_ban_nhom(tmp_path)
    (dash / "watchlist.de-xuat.json").write_text("{hỏng", encoding="utf-8")
    pt = _pt(dash, tmp_path, sl)
    assert pt["do_duoc"] and pt["canh_bao"] and "watchlist.de-xuat.json" in pt["canh_bao"][0]


@pytest.mark.parametrize("hong, ly_do", [
    ("khong_thu_muc", "không có thư mục quét"),
    ("mot_luot", "chỉ 1 lượt quét tuần đọc được"),
    ("watchlist", "không đọc được watchlist.json"),
])
def test_khong_do_duoc_la_ma_2_khong_phai_on(tmp_path, capsys, hong, ly_do):
    dash = tmp_path / "EBM-Dashboards"
    _ghi_wl(dash, [_chu_de_wl("A")])
    if hong != "khong_thu_muc":
        _ghi_luot(dash / "surveillance", 40, {"A": ("PASS", 0)})
    if hong in ("watchlist",):
        _ghi_luot(dash / "surveillance", 39, {"A": ("PASS", 0)})
        (dash / "watchlist.json").write_text("{hỏng", encoding="utf-8")
    pt = _pt(dash, tmp_path)
    assert not pt["do_duoc"] and ly_do in pt["ly_do"]
    assert K0.in_bao_cao(pt) == 2 and "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out


# ── số đo sản lượng ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("kieu, tuoi_ky_vong", [("moi", True), ("cu", False), ("khac_wl", False), ("do_khong_tron", False)])
def test_san_luong_chi_tin_khi_cung_watchlist_con_han_va_do_tron(tmp_path, kieu, tuoi_ky_vong):
    wl_text = '{"topics": []}'
    tep = tmp_path / "sl.json"
    _ghi_san_luong(tep, wl_text, {"A": ("MU", 1)}, tuoi_ngay=10 if kieu == "cu" else 8,
                   sha="0" * 64 if kieu == "khac_wl" else None,
                   khong_do=["A"] if kieu == "do_khong_tron" else None)
    assert K0.doc_san_luong(tep, wl_text, BAY_GIO)["tuoi"] is tuoi_ky_vong


def test_bam_watchlist_la_mot_dinh_nghia_duy_nhat():
    assert SL.bam_watchlist("abc") == hashlib.sha256(b"abc").hexdigest()
    cay = ast.parse((TOOLS / "kiem_san_luong_giam_sat.py").read_text(encoding="utf-8"))
    goi = [n for n in ast.walk(cay) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
           and n.func.attr == "sha256"]
    ham = next(n for n in cay.body if isinstance(n, ast.FunctionDef) and n.name == "bam_watchlist")
    assert len(goi) == 1 and any(g is n for g in goi for n in ast.walk(ham)), "băm watchlist ở hai nơi = chỗ trôi"


def test_mot_duong_dan_ket_qua_san_luong_cho_ca_ba_noi():
    rel = SL.KET_QUA_GAN_NHAT.relative_to(SL.REPO).as_posix()
    assert rel == "state/san-luong-giam-sat-gan-nhat.json"
    assert f'"--json", "{rel}"' in (TOOLS / "chu_trinh_chung_cu.py").read_text(encoding="utf-8")
    skill = (REPO / "sync" / "scheduled-tasks" / "goi-duyet-tuan-ebm" / "SKILL.md").read_text(encoding="utf-8")
    assert f"--json {rel}" in skill and "kiem_chuoi_0_ung_vien.py" in skill and rel in K0.LENH_DO


# ── việc + mã thoát ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_viec_bac_si_dung_dau_mo_ta_va_uu_tien_cao_khi_chu_de_cho_duyet_dang_lien(tmp_path):
    dash, sl = _kich_ban_nhom(tmp_path)
    viec, tt = K0.viec_tu_phan_tich(_pt(dash, tmp_path, sl))
    bs = [v for v in viec if v[1] == "👤"]
    assert len(bs) == 1 and bs[0][0] == 1
    assert K0.NHAC in bs[0][2][:150] and K0.LENH_DUYET in bs[0][2][:150], "hòm việc cắt mô tả ở 150 ký tự"
    may = [v for v in viec if v[1] == "🛎"]   # cần đo · mù chưa đề xuất · không tầng — mỗi nhóm MỘT việc
    assert len(may) == 3
    assert [v for v in may if "D_cando" in v[2]][0][3] == K0.LENH_DO
    assert [v for v in may if "E_mu" in v[2]][0][0] == 1
    assert [v for v in may if "C_khongtang" in v[2]][0][0] == 2
    assert any("B_hanche" in x for x in tt) and any("F_on" in x for x in tt)


def test_viec_bac_si_uu_tien_thap_khi_chu_de_cho_duyet_con_co_ung_vien(tmp_path):
    dash = tmp_path / "EBM-Dashboards"
    _ghi_wl(dash, [_chu_de_wl("A"), _chu_de_wl("Z")])
    for tuan in (39, 40):
        _ghi_luot(dash / "surveillance", tuan, {"A": ("PASS", 5), "Z": ("PASS", 1)})
    _ghi_de_xuat(dash, [{"topic": "A", "queries": _queries("A_moi")}])
    viec, _ = K0.viec_tu_phan_tich(_pt(dash, tmp_path))
    assert [(v[0], v[1]) for v in viec] == [(2, "👤")] and "1 chủ đề còn có ứng viên gần đây" in viec[0][2]


def test_viec_bac_si_uu_tien_cao_khi_chu_de_cho_duyet_0_ma_luot_truoc_khong_do(tmp_path):
    dash = tmp_path / "EBM-Dashboards"
    _ghi_wl(dash, [_chu_de_wl("A")])
    _ghi_luot(dash / "surveillance", 39, {"A": ("PASS_DEGRADED", 0)})
    _ghi_luot(dash / "surveillance", 40, {"A": ("PASS", 0)})
    _ghi_de_xuat(dash, [{"topic": "A", "queries": _queries("A_moi")}])
    pt = _pt(dash, tmp_path)
    assert [m["muc"] for m in pt["chu_de"]] == ["chua_tinh_lien"]
    viec, _ = K0.viec_tu_phan_tich(pt)
    assert [(v[0], v[1]) for v in viec] == [(1, "👤")] and "lượt liền trước KHÔNG đo được" in viec[0][2]


def test_ma_thoat_0_khi_chi_con_khoang_trong_da_biet(tmp_path, capsys):
    dash = tmp_path / "EBM-Dashboards"
    _ghi_wl(dash, [_chu_de_wl("NICE")])
    for tuan in (39, 40):
        _ghi_luot(dash / "surveillance", tuan, {"NICE": ("PASS", 0)}, han_che={"NICE": "SRC-017"})
    pt = _pt(dash, tmp_path)
    assert K0.in_bao_cao(pt) == 0
    out = capsys.readouterr().out
    assert "ⓘ NICE" in out and K0.NHAC in out


def test_ma_thoat_1_khi_co_viec(tmp_path, capsys):
    dash, sl = _kich_ban_nhom(tmp_path)
    assert K0.in_bao_cao(_pt(dash, tmp_path, sl)) == 1
    assert "🟠 👤" in capsys.readouterr().out


def test_main_cong_cu_loi_la_ma_2(tmp_path, monkeypatch, capsys):
    def _no(*_a, **_k):
        raise RuntimeError("giả")
    monkeypatch.setattr(K0, "phan_tich", _no)
    assert K0.main(["--dash", str(tmp_path)]) == 2 and "công cụ lỗi RuntimeError" in capsys.readouterr().out


def test_bang_kenh_ngoai_pubmed_doc_bang_ast_tu_bo_quet_chuan(tmp_path):
    bang = K0.bang_kenh_ngoai_pubmed(SL.SCANNER)
    assert {"NICE — hướng dẫn mới", "USPSTF — khuyến cáo dự phòng"} <= set(bang)
    (tmp_path / "a.py").write_text("KENH_THAT_NGOAI_PUBMED = {'X': 'k'}\n", encoding="utf-8")
    assert K0.bang_kenh_ngoai_pubmed(tmp_path / "a.py") == {"X": "k"}
    (tmp_path / "b.py").write_text("KENH_THAT_NGOAI_PUBMED = {\n", encoding="utf-8")
    assert K0.bang_kenh_ngoai_pubmed(tmp_path / "b.py") == {}


# ── giác quan trong «hệ còn gì để làm?» ──────────────────────────────────────────────────────────────────────────────
def test_giac_quan_tu_de_xuat_viec(tmp_path):
    dash, sl = _kich_ban_nhom(tmp_path)
    viec, tt = TDX.giac_quan_chu_de_0_lien(dash, sl)
    assert any(v[1] == "👤" and K0.LENH_DUYET in v[2] for v in viec) and tt


def test_giac_quan_chet_khi_khong_do_duoc_hay_cong_cu_loi(tmp_path, monkeypatch):
    truoc = len(TDX._GIAC_QUAN_CHET)
    assert TDX.giac_quan_chu_de_0_lien(tmp_path / "khong-co", None) == ([], [])
    dash = tmp_path / "EBM-Dashboards"
    _ghi_luot(dash / "surveillance", 40, {"A": ("PASS", 0)})
    assert TDX.giac_quan_chu_de_0_lien(dash, None) == ([], [])           # 1 lượt ⇒ không đo được
    gia = tmp_path / "tools-gia"
    gia.mkdir()
    (gia / "kiem_chuoi_0_ung_vien.py").write_text("raise RuntimeError('hỏng')\n", encoding="utf-8")
    monkeypatch.setattr(TDX, "__file__", str(gia / "tu_de_xuat_viec.py"))
    assert TDX.giac_quan_chu_de_0_lien(dash, None) == ([], [])
    chet = TDX._GIAC_QUAN_CHET[truoc:]
    assert len(chet) == 3 and "lỗi RuntimeError" in str(chet[-1])


def test_giac_quan_de_xuat_hong_ghi_chet_nhung_van_tra_viec(tmp_path):
    dash, sl = _kich_ban_nhom(tmp_path)
    (dash / "watchlist.de-xuat.json").write_text("{hỏng", encoding="utf-8")
    truoc = len(TDX._GIAC_QUAN_CHET)
    viec, _ = TDX.giac_quan_chu_de_0_lien(dash, sl)
    assert len(TDX._GIAC_QUAN_CHET) == truoc + 1 and viec


def test_main_cua_tu_de_xuat_viec_goi_giac_quan():
    dong = [d.strip() for d in inspect.getsource(TDX.main).splitlines()]
    assert any(d.startswith("_viec_0, _tt_0 = giac_quan_chu_de_0_lien(") for d in dong if not d.startswith("#"))
    assert "de_xuat += _viec_0" in dong and "_THONG_TIN.extend(_tt_0)" in dong
