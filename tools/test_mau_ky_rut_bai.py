"""Kiểm hồi quy `tools/mau_ky_rut_bai.py` (BH109): mẫu chờ ký KHÔNG BAO GIỜ có hiệu lực thay bác sĩ."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    spec = importlib.util.spec_from_file_location(ten, GOC / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


mau = _nap("tools/mau_ky_rut_bai.py", "mau_ky_rut_bai_t")
vd = _nap("sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py", "vd_mau_ky_t")

BG = {"loai": "pmid", "gia_tri": "1", "da_rut": True, "sua_loi_bi_rut": True, "thong_bao_ids": ["41422828"],
      "tieu_de": "Guideline X", "cac_dashboard": ["WebDashboard_a.html"], "nguon_xac_minh": "pubmed",
      "kiem_rut_luc": "2026-09-20T10:00:00"}


def _so(**muc):
    return lambda: {"muc": muc}


def _chay_cong(thu_muc: Path, ban_ghi: dict):
    e, w, o = [], [], []
    vd.kiem_nguon_da_rut(str(thu_muc / "a.html"), e, w, o, tra_cuu=lambda _t: [ban_ghi])
    return e, w


def _ban_ghi_cong(khoa: str, bg: dict) -> dict:
    return {"khoa": khoa, "loai": bg["loai"], "gia_tri": bg["gia_tri"], "tinh_trang": "retracted",
            "tieu_de": "t", "kiem_luc": "2026-09-20", "nguon": "pubmed", "thong_bao": "",
            "rut_va_thay": False, "sua_loi_bi_rut": True, "thong_bao_ids": bg["thong_bao_ids"]}


def test_liet_ke_ban_ghi_chua_ky_va_dien_dung_van_tay(tmp_path):
    cho = mau.muc_cho_ky(tmp_path, doc_so=_so(**{"pmid:1": BG}), cong=vd)
    assert [e["khoa"] for e in cho] == ["pmid:1"]
    assert cho[0]["thong_bao_ids"] == ["41422828"]
    assert cho[0]["da_xem_boi"] == cho[0]["ngay"] == cho[0]["ly_do"] == ""


def test_bo_qua_ban_ghi_khong_co_co_hoac_khong_co_van_tay(tmp_path):
    so = _so(**{"pmid:1": dict(BG, sua_loi_bi_rut=False), "pmid:2": dict(BG, thong_bao_ids=[]),
                "pmid:3": dict(BG, da_rut=False)})
    assert mau.muc_cho_ky(tmp_path, doc_so=so, cong=vd) == []


def test_mau_chep_nguyen_xi_KHONG_co_hieu_luc_cho_toi_khi_bac_si_dien(tmp_path):
    cho = mau.muc_cho_ky(tmp_path, doc_so=_so(**{"pmid:1": BG}), cong=vd)
    (tmp_path / "rut-bai-da-xem-xet.json").write_text(json.dumps({"muc": cho}), encoding="utf-8")
    e, _w = _chay_cong(tmp_path, _ban_ghi_cong("pmid:1", BG))
    assert e, "mẫu trống mà cổng đã miễn — máy ký thay bác sĩ"
    ky = dict(cho[0], da_xem_boi="BS thử", ngay="2026-09-21", ly_do="Đã đọc thông báo và hai Author Correction; không đổi.")
    ky.pop("_ngu_canh")
    (tmp_path / "rut-bai-da-xem-xet.json").write_text(json.dumps({"muc": [ky]}), encoding="utf-8")
    e, w = _chay_cong(tmp_path, _ban_ghi_cong("pmid:1", BG))
    assert not e and w
    # đã ký hợp lệ ⇒ không còn nằm trong danh sách chờ ký
    assert mau.muc_cho_ky(tmp_path, doc_so=_so(**{"pmid:1": BG}), cong=vd) == []


def test_main_khong_bao_gio_ghi_so_ky_that(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mau, "DASH", tmp_path)
    monkeypatch.setattr(mau, "GOC", tmp_path)
    monkeypatch.setattr(mau, "muc_cho_ky", lambda *a, **k: [
        {"khoa": "pmid:1", "thong_bao_ids": ["7"], "da_xem_boi": "", "ngay": "", "ly_do": "",
         "_ngu_canh": {"tieu_de_bai": "t", "dashboard": ["a.html"]}}])
    monkeypatch.setattr(sys, "argv", ["mau_ky_rut_bai.py"])
    assert mau.main() == 1
    assert (tmp_path / mau.MAU).exists()
    assert not (tmp_path / mau.SO_KY).exists(), "công cụ ghi vào sổ mà cổng đọc — vượt thẩm quyền bác sĩ"
