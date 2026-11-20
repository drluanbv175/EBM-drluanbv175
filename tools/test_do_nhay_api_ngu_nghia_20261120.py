# -*- coding: utf-8 -*-
"""Đo độ bắt lỗi bộ kiểm Claude API trên đột biến tổng hợp (20/11/2026, bác sĩ: «Kiểm ngữ nghĩa chưa đo được độ bắt lỗi …
giải quyết triệt để»). OFFLINE — không gọi API, không đọc dashboard thật.

Chốt: (1) mẫu phân tầng tất định, bỏ đột biến API không nhìn thấy; (2) DEV/TEST theo MỤC; (3) «bắt» chỉ khi bản GỐC không
bị nghi ở trục đích; (4) so cặp với luật cứng + McNemar chính xác; (5) gọi API: trần/khoá dừng, kết quả hỏng đi tiếp, bộ
đệm theo phiên bản prompt; (6) dưới pytest không ghi bộ đệm thật; (7) prompt theo phiên bản không đổi khoá cũ.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_TOOLS = Path(__file__).resolve().parent


def _nap(ten, tep):
    sp = importlib.util.spec_from_file_location(ten, _TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


D = _nap("_dna_t", "do_nhay_api_ngu_nghia.py")
A = _nap("_dna_t_api", "kiem_ngu_nghia_api.py")
KQTC = SimpleNamespace(than_nguon=lambda raw: raw)
MDL, PB = "claude-sonnet-5-5", "2026-11-19a"


def _goc(i, nguon="Nguồn gốc. Conclusions: dùng được."):
    return {"muc": {"id": f"ITEM-{i}", "title": f"Dùng thuốc {i}", "population": "Người lớn", "action": f"Dùng {i}"},
            "nguon": nguon, "ket_qua_luat": {}}


def _db(i, lop, **sua):
    muc = dict(_goc(i)["muc"])
    muc.update(sua.pop("muc", {}))
    return {"lop": lop, "dashboard": "WebDashboard_X.html", "_khoa": ("WebDashboard_X.html", i), "bien_the": sua.pop("bt", "x"),
            "muc_dot_bien": muc, "nguon_dot_bien": sua.pop("nguon", _goc(i)["nguon"]), "ket_qua": sua.pop("luat", "lot_xanh")}


def _R(cap):
    """{(mục, nguồn): kết quả} → bộ đệm theo khoá thật của kiem_ngu_nghia_api."""
    return {A.khoa_muc(it, A.than_tom_tat(raw, KQTC), MDL, PB): {"ket_qua": kq} for (it, raw), kq in cap}


T = {"dung_quan_the": True, "dung_chieu": True, "du_dieu_kien": True}


def _kq(**sua):
    return dict(T, **sua)


def test_mcnemar_chinh_xac_va_wilson():
    assert D.mcnemar_chinh_xac(0, 0) is None
    assert D.mcnemar_chinh_xac(10, 0) == pytest.approx(2 / 2 ** 10)
    assert D.mcnemar_chinh_xac(3, 3) == 1.0
    lo, hi = D.wilson(186, 187)
    assert 0.96 < lo < 0.98 and hi == pytest.approx(1.0, abs=0.005)
    assert D.wilson(0, 0) is None


def test_tap_dev_test_theo_muc_tat_dinh():
    a = [D.tap_cua(20261114, "X.html", i) for i in range(200)]
    assert a == [D.tap_cua(20261114, "X.html", i) for i in range(200)]
    assert 70 < a.count("dev") < 130                                         # gần một nửa
    assert D.tap_cua(1, "X.html", 5) in ("dev", "test")


def test_chon_mau_phan_tang_tat_dinh_va_bo_dot_bien_api_khong_thay():
    goc = {("WebDashboard_X.html", i): _goc(i) for i in range(30)}
    ds = [_db(i, "K1_quan_the", muc={"population": "Trẻ em"}, bt=f"b{i}") for i in range(30)]
    ds += [_db(i, "K4_muc_dao", muc={"action": f"KHÔNG dùng {i}"}) for i in range(5)]
    ds.append(_db(99, "K1_quan_the"))                                        # không có gốc ⇒ bỏ
    ds.append({**_db(1, "K3_rung_trong_muc"), "muc_dot_bien": dict(goc[("WebDashboard_X.html", 1)]["muc"],
                                                                    pico={"P": "đổi"})})  # đổi trường API không đọc
    mau, tk = D.chon_mau(ds, goc, 10, 20261114)
    assert tk["K1_quan_the"] == {"co_san": 31, "api_khong_thay": 0, "chon": 10}
    assert tk["K4_muc_dao"]["chon"] == 5 and tk["K3_rung_trong_muc"] == {"co_san": 1, "api_khong_thay": 1, "chon": 0}
    assert [d["bien_the"] for d in mau] == [d["bien_the"] for d in D.chon_mau(list(reversed(ds)), goc, 10, 20261114)[0]]


def test_cham_chi_tinh_bat_khi_goc_khong_bi_nghi():
    g = _goc(1)
    d = _db(1, "K1_quan_the", muc={"population": "Trẻ em"})
    goc_ok, goc_nghi = (g["muc"], g["nguon"]), (g["muc"], g["nguon"])
    dot = (d["muc_dot_bien"], d["nguon_dot_bien"])

    def c(o, r):
        cap = ([(goc_ok, o)] if o is not None else []) + ([(dot, r)] if r is not None else [])
        return D.cham(d, g, _R(cap), A, KQTC, MDL, PB)
    assert c(T, _kq(dung_quan_the=False)) == "bat"
    assert c(_kq(dung_quan_the=False), _kq(dung_quan_the=False)) == "goc_da_nghi"
    assert c(T, _kq(dung_chieu=False)) == "bat_lech"
    assert c(_kq(dung_chieu=False), _kq(dung_chieu=False)) == "lot_xanh"     # lệch trục đã có ở gốc ⇒ không quy cho đột biến
    assert c(T, _kq(dung_quan_the=None)) == "lot_trang"
    assert c(T, T) == "lot_xanh"
    assert c(None, T) == "chua_cham" and c(T, None) == "chua_cham"
    assert goc_nghi                                                          # (dùng biến cho rõ ý)


def test_o_so_cap_voi_luat_cung_va_loai_mau_so():
    o = D._o(["bat", "bat", "lot_xanh", "goc_da_nghi", "chua_cham", "bat"],
             ["lot_xanh", "bat", "bat", "bat", "bat", "lot_im"])
    assert o["n_tinh"] == 4 and o["bat"] == 3 and o["do_nhay"] == pytest.approx(0.75)
    assert o["luat_cung"]["n"] == 4 and o["luat_cung"]["bat"] == 2               # gốc đã nghi / chưa chấm bị loại cả hai bên
    assert o["cap"] == {"ca_hai": 1, "chi_api": 2, "chi_luat_cung": 1, "ca_hai_lot": 0,
                        "p_mcnemar": D.mcnemar_chinh_xac(2, 1)}


class _LoiApi(RuntimeError):
    pass


class _LoiCucBo(_LoiApi):
    pass


class _KetQuaHong(_LoiApi):
    pass


def _cn(tra, nem=None):
    ds, nk = [], []

    def goi(nd, **kw):
        ds.append(kw)
        x = nem(len(ds)) if nem else None
        if x:
            raise x
        return SimpleNamespace(van_ban=tra, model=MDL, token_vao=10, token_ra=5, token_cache_doc=0)
    return SimpleNamespace(goi=goi, doc_json=json.loads, LoiApi=_LoiApi, LoiCucBo=_LoiCucBo, KetQuaHong=_KetQuaHong,
                           ghi_nhat_ky_api=lambda *a, **k: nk.append(a), _ds=ds, _nk=nk)


def test_goi_thieu_dung_khi_tran_va_di_tiep_khi_hong(tmp_path):
    goc = {("WebDashboard_X.html", i): _goc(i) for i in range(4)}
    mau = [_db(i, "K1_quan_the", muc={"population": "Trẻ em"}) for i in range(4)]
    yc = D.lap_yeu_cau(mau, goc, A, KQTC, MDL, PB)
    assert len(yc) == 8                                                      # 4 đột biến + 4 gốc
    tra = json.dumps(dict(T, ly_do={}))
    dem = {}
    kq = D.goi_thieu(yc, dem, A=A, cau_noi=_cn(tra, nem=lambda n: _KetQuaHong("cắt") if n == 2 else
                     (_LoiCucBo("HetNganSach") if n == 4 else None)), client=None, mdl=MDL, phien_ban=PB,
                     tep=tmp_path / "dem.json")
    assert kq["da_goi"] == 2 and len(kq["loi"]) == 1 and "HetNganSach" in kq["dung"]
    assert len(json.loads((tmp_path / "dem.json").read_text(encoding="utf-8"))) == 2
    cn = _cn(tra)
    kq = D.goi_thieu(yc, dem, A=A, cau_noi=cn, client=None, mdl=MDL, phien_ban=PB, tep=tmp_path / "dem.json", toi_da=3)
    assert kq["can_goi"] == 3 and all(k["nguon"] == D.NGUON and k["he_thong"] == A.he_thong(PB) for k in cn._ds)


def test_tong_hop_va_doi_chung_tren_bo_dem_gia():
    goc = {("WebDashboard_X.html", i): _goc(i) for i in range(6)}
    mau = [_db(i, "K1_quan_the", muc={"population": "Trẻ em"}, luat="bat" if i < 3 else "lot_xanh") for i in range(6)]
    cap = []
    for i, d in enumerate(mau):
        g = goc[d["_khoa"]]
        cap.append(((g["muc"], g["nguon"]), T if i else _kq(du_dieu_kien=False)))
        cap.append(((d["muc_dot_bien"], d["nguon_dot_bien"]), _kq(dung_quan_the=False) if i % 2 == 0 else T))
    DN = SimpleNamespace(chu_ky_bao=lambda r, p: bool(r.get("bao")), PHEP_NGUON=("K1",))
    th = D.tong_hop(mau, goc, _R(cap), A, KQTC, MDL, PB, 20261114, {}, DN)
    o = th["theo_tap"]["tat_ca"]["lop"]["K1_quan_the"]
    assert (o["n_tinh"], o["bat"]) == (6, 3) and o["luat_cung"]["bat"] == 3
    dc = th["theo_tap"]["tat_ca"]["doi_chung"]
    assert dc["n"] == 6 and dc["api_bat_ky"] == 1 and dc["api_theo_truc"]["du_dieu_kien"] == 1
    assert set(th["theo_tap"]) == {"dev", "test", "tat_ca"}
    md = D.ban_md({"ngay": "20261120", "phien_ban": PB, "hat_giong": 20261114, "model": MDL, "so_mau": 40, "so_dashboard": 1,
                   "so_muc": 6, "bam_ma": {"a.py": "x"}, "ket_qua": th,
                   "phu_mau": {k: {"co_san": 0, "api_khong_thay": 0, "chon": 0} for k in D.LOP_API}})
    assert "KHÔNG thay bộ vàng" in md and "TEST (tập giữ lại" in md and "Nguồn gốc" not in md   # không chép văn bản nguồn


def test_khoa_bo_dem_theo_phien_ban_prompt_va_tuong_thich():
    it = {"title": "a", "population": "b", "action": "c"}
    assert A.khoa_muc(it, "tt", MDL) == A.khoa_muc(it, "tt", MDL, A.PHIEN_BAN_PROMPT)      # khoá cũ không đổi
    assert all(A.khoa_muc(it, "tt", MDL, v) != A.khoa_muc(it, "tt", MDL, A.PHIEN_BAN_PROMPT)
               for v in A.PROMPT_THEO_PHIEN_BAN if v != A.PHIEN_BAN_PROMPT)
    assert A.he_thong() == A.PROMPT_THEO_PHIEN_BAN[A.PHIEN_BAN_PROMPT]
    assert "2026-11-19a" in A.PROMPT_THEO_PHIEN_BAN                                       # giữ prompt cũ để so cặp


def test_duoi_pytest_khong_ghi_bo_dem_that():
    with pytest.raises(RuntimeError):
        D.ghi_bo_dem(D.tep_bo_dem(), {})


def test_ket_hop_va_phan_duoc():
    o = D._o(["bat", "lot_xanh", "lot_trang", "lot_xanh"], ["lot_xanh", "bat", "lot_xanh", "lot_xanh"],
             [True, True, False, True])
    assert o["ket_hop"]["bat"] == 2 and o["ket_hop"]["n"] == 4                # API bắt 1 + chỉ luật cứng bắt 1
    assert o["phan_duoc"] == {"n": 3, "bat": 1, "do_nhay": pytest.approx(1 / 3), "ktc95": D.wilson(1, 3)}


def test_chi_tap_bao_cao_chi_tap_do():
    goc = {("WebDashboard_X.html", i): _goc(i) for i in range(6)}
    mau = [_db(i, "K1_quan_the", muc={"population": "Trẻ em"}) for i in range(6)]
    DN = SimpleNamespace(chu_ky_bao=lambda r, p: False, PHEP_NGUON=("K1",))
    th = D.tong_hop(mau, goc, {}, A, KQTC, MDL, PB, 20261114, {}, DN, chi_tap="test")
    assert set(th["theo_tap"]) == {"test"} and th["chi_tap"] == "test"
