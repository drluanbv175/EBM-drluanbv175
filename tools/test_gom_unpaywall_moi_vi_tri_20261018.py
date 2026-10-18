# -*- coding: utf-8 -*-
"""Tầng 2 Unpaywall xét MỌI vị trí OA, không chỉ `best_oa_location` (18/10/2026 — bác sĩ: «127 bản ghi có PMID nhưng chưa có tệp,
và 19 bản ghi không có PMID hãy giải quyết toàn văn tất cả cho tôi»).

Ca thật: PMID 42240859 (Eur J Heart Fail, OUP — NXB «cấm») — best là bản không giấy phép ⇒ trước đây cả bài bị «cam_co_uq», trong
khi kho Glasgow có bản CC BY-SA hợp lệ. Khoá:
  • vị trí có giấy phép mở ở SAU best vẫn được tải; bản không giấy phép của NXB «cấm» KHÔNG bao giờ được mở (cổng giữ nguyên);
  • vị trí đầu lỗi mạng / không phải toàn văn ⇒ thử vị trí kế, lưu được thì dừng;
  • không vị trí nào qua cổng ⇒ ghi lý do của vị trí bị chặn đầu tiên vào BO_QUA_UNPAYWALL như cũ;
  • thiếu `oa_locations` (dữ liệu cũ) ⇒ vẫn chạy với riêng best.
Ngoại tuyến hoàn toàn (urlopen giả).
"""
from __future__ import annotations

import importlib.util
import io
import json
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("_gom_upw_moi_vi_tri", REPO / "tools" / "gom_toan_van_dashboard.py")
g = importlib.util.module_from_spec(sp)
sp.loader.exec_module(g)

BANG = {"Oxford University Press": {"ket_luan": "cam", "doi": ("10.1093/",), "mien": ("academic.oup.com",)}}
IMRAD = " ".join(["<h2>Introduction</h2>" + "chữ " * 900, "<h2>Methods</h2>" + "chữ " * 900, "<h2>Results</h2>" + "chữ " * 900,
                  "<h2>Discussion</h2>" + "chữ " * 900])
PDF = b"%PDF-1.7\n" + b"0" * 4000


def _dtv():
    def nxb_cua(doi="", url="", tieu_de=""):
        for ten, d in BANG.items():
            if any((doi or "").lower().startswith(t) for t in d["doi"]):
                return ten, d
        return None, None
    return types.SimpleNamespace(DIEU_KHOAN_NXB=BANG, nxb_cua=nxb_cua, uy_quyen_bac_si=lambda ten, hom_nay=None: {"ngay": "2026-10-04"},
                                 giay_phep_mo_cap_nxb=lambda url="": (None, None))


class _PhanHoi(io.BytesIO):
    def __init__(self, du_lieu: bytes, url: str):
        super().__init__(du_lieu)
        self._url = url

    def geturl(self):
        return self._url


def _mang(monkeypatch, tmp_path, doi: str, uj: dict, noi_dung: dict, da_goi: list):
    def urlopen(req, timeout=None, context=None):
        url = req if isinstance(req, str) else req.full_url
        da_goi.append(url)
        if "esummary.fcgi" in url:
            pm = url.split("id=")[1].split("&")[0]
            return _PhanHoi(json.dumps({"result": {pm: {"articleids": [{"idtype": "doi", "value": doi}]}}}).encode(), url)
        if "api.unpaywall.org" in url:
            return _PhanHoi(json.dumps(uj).encode(), url)
        gt = noi_dung.get(url)
        if isinstance(gt, Exception):
            raise gt
        return _PhanHoi(gt if gt is not None else b"", url)
    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    monkeypatch.setattr(g, "_email_lich_su", lambda: "test@example.org")
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    monkeypatch.setattr(g, "KHO", tmp_path)
    monkeypatch.setattr(g, "_nap_dtv", _dtv)


BEST_CAM = {"url": "https://academic.oup.com/ejhf/x.pdf", "license": None}
GLA_CC = {"url": "https://eprints.gla.ac.uk/389438/1/389438.pdf", "license": "cc-by-sa"}
HAL_CC = {"url": "https://hal.univ-lorraine.fr/hal-05772142", "license": "cc-by-nc-nd"}


def test_vi_tri_cc_sau_best_duoc_tai_ban_cam_khong_bao_gio_mo(monkeypatch, tmp_path):
    da_goi: list[str] = []
    uj = {"is_oa": True, "best_oa_location": BEST_CAM, "oa_locations": [BEST_CAM, GLA_CC]}
    _mang(monkeypatch, tmp_path, "10.1093/ejhf/xuag142", uj, {GLA_CC["url"]: PDF}, da_goi)
    moi, thieu = g.tang_unpaywall(["42240859"])
    assert moi == 1 and thieu == [] and (tmp_path / "PMID-42240859_UPW.pdf").exists()
    assert not any("academic.oup.com" in u for u in da_goi), "đã MỞ bản không giấy phép của NXB «cấm»"
    assert not g.BO_QUA_UNPAYWALL


def test_vi_tri_dau_hong_thi_thu_vi_tri_ke(monkeypatch, tmp_path):
    da_goi: list[str] = []
    uj = {"is_oa": True, "best_oa_location": BEST_CAM, "oa_locations": [BEST_CAM, HAL_CC, GLA_CC]}
    _mang(monkeypatch, tmp_path, "10.1093/ejhf/xuag142", uj,
          {HAL_CC["url"]: OSError("mạng hỏng"), GLA_CC["url"]: PDF}, da_goi)
    moi, _ = g.tang_unpaywall(["42240859"])
    assert moi == 1 and (tmp_path / "PMID-42240859_UPW.pdf").exists()
    assert da_goi.index(HAL_CC["url"]) < da_goi.index(GLA_CC["url"]), "phải thử theo thứ tự Unpaywall trả"


def test_trang_gioi_thieu_khong_phai_toan_van_thi_thu_vi_tri_ke(monkeypatch, tmp_path):
    da_goi: list[str] = []
    uj = {"is_oa": True, "best_oa_location": HAL_CC, "oa_locations": [HAL_CC, GLA_CC]}
    _mang(monkeypatch, tmp_path, "10.1093/ejhf/xuag142", uj,
          {HAL_CC["url"]: b"<html><body><h1>Fingerprint</h1>Research output</body></html>", GLA_CC["url"]: PDF}, da_goi)
    moi, _ = g.tang_unpaywall(["42240859"])
    assert moi == 1 and not (tmp_path / "PMID-42240859_UPW.html").exists() and (tmp_path / "PMID-42240859_UPW.pdf").exists()


def test_dung_o_vi_tri_dau_tien_luu_duoc(monkeypatch, tmp_path):
    da_goi: list[str] = []
    uj = {"is_oa": True, "best_oa_location": GLA_CC, "oa_locations": [GLA_CC, HAL_CC]}
    _mang(monkeypatch, tmp_path, "10.1093/ejhf/xuag142", uj,
          {GLA_CC["url"]: PDF, HAL_CC["url"]: ("<html><body>" + IMRAD + "</body></html>").encode()}, da_goi)
    moi, _ = g.tang_unpaywall(["42240859"])
    assert moi == 1 and HAL_CC["url"] not in da_goi


def test_khong_vi_tri_nao_qua_cong_thi_ghi_ly_do_nhu_cu(monkeypatch, tmp_path):
    da_goi: list[str] = []
    repo = {"url": "https://repo.example/ban-tac-gia.pdf", "license": None}
    uj = {"is_oa": True, "best_oa_location": BEST_CAM, "oa_locations": [BEST_CAM, repo]}
    _mang(monkeypatch, tmp_path, "10.1093/eurheartj/ehs337", uj, {}, da_goi)
    moi, thieu = g.tang_unpaywall(["23095984"])
    assert moi == 0 and thieu == ["23095984"] and not list(tmp_path.iterdir())
    assert g.BO_QUA_UNPAYWALL and g.BO_QUA_UNPAYWALL[0][2].startswith("cam_co_uq")
    assert not any(x in u for u in da_goi for x in ("academic.oup.com", "repo.example"))


def test_thieu_oa_locations_van_chay_voi_best(monkeypatch, tmp_path):
    da_goi: list[str] = []
    uj = {"is_oa": True, "best_oa_location": GLA_CC}
    _mang(monkeypatch, tmp_path, "10.1093/ejhf/xuag142", uj, {GLA_CC["url"]: PDF}, da_goi)
    assert g.tang_unpaywall(["42240859"])[0] == 1


def test_vi_tri_oa_duoc_luu_thuan():
    uj = {"is_oa": True, "best_oa_location": BEST_CAM, "oa_locations": [BEST_CAM, GLA_CC, GLA_CC, {"url": None}]}
    ds, ly = g.vi_tri_oa_duoc_luu(uj, "10.1093/ejhf/xuag142", dtv=_dtv())
    assert ds == [GLA_CC["url"]] and ly.startswith("cam_co_uq")
    assert g.vi_tri_oa_duoc_luu({"is_oa": False, "best_oa_location": GLA_CC}, "10.1093/x", dtv=_dtv()) == ([], "")
