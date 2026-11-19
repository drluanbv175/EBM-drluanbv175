# -*- coding: utf-8 -*-
"""Bộ vàng mở rộng 19/11/2026 (bác sĩ: «Bộ vàng này hiện chưa có. Hãy giải quyết», chọn «Kết hợp hai cách»).

Bất biến được chốt (OFFLINE, không gọi API thật):
(1) đột biến chỉ thành nhãn khi bác sĩ DUYỆT bằng nguyên văn lời; trục bị đột biến luôn false, trục khác chỉ kế thừa đúng nhãn
    gốc; lời duyệt mơ hồ ⇒ không ghi gì;
(2) mục thật mới rút theo tầng, không trùng, nhãn để trống; phiếu phần B chỉ in mục chưa nhãn và vẫn MÙ với máy;
(3) số đo đột biến tách khỏi số đo mục thật; bộ kiểm API chỉ thấy ba trường của mục + tóm tắt — không nhãn, không mã;
(4) bộ kiểm API chạy khô mặc định, dừng khi chạm trần/khoá/mạng, không ghi bộ đệm thật dưới pytest.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, _TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


B = _nap("_bvm_bvk", "bo_vang_kiem_ngu_nghia.py")
A = _nap("_bvm_api", "kiem_ngu_nghia_api.py")


def _muc(i, q=True, c=True, d=True, pmid="111", **kw):
    m = {"dashboard": f"WebDashboard_EBM_X{i}_20260101.html", "id": f"ITEM-{i}", "title": f"Dùng thuốc A {i}",
         "population": "Người lớn suy tim HFrEF", "action": "Dùng thuốc A khi eGFR ≥30", "pmid": pmid, "doi": None,
         "gradeLevel": "high",
         "nhan_bac_si": {"dung_quan_the": q, "dung_chieu": c, "du_dieu_kien": d, "ghi_chu": None,
                         **({"loi_bac_si": "x"} if any(v is not None for v in (q, c, d)) else {})}}
    m.update(kw)
    return m


def _dx(*ds):
    return {"dot_bien": list(ds)}


def _db(ma="D01", tu=1, kieu="quan_the", sua=None, nhan=(False, True, None), mo_ta="đổi quần thể"):
    return {"ma": ma, "tu_muc": tu, "kieu": kieu, "mo_ta": mo_ta,
            "sua": sua if sua is not None else {"population": "Trẻ em suy tim"},
            "nhan_du_kien": dict(zip(B.NHAN, nhan))}


# ───── (a) đề xuất đột biến ─────

def test_de_xuat_da_commit_hop_le_va_du_ba_kieu():
    bv = B.doc_bo_vang()
    dx = json.loads(B.TEP_DOT_BIEN_DE_XUAT.read_text(encoding="utf-8"))
    assert B.kiem_de_xuat(bv, dx) == []
    ds = dx["dot_bien"]
    assert [x["ma"] for x in ds] == [f"D{i:02d}" for i in range(1, len(ds) + 1)]
    for kieu in B.KIEU_DOT_BIEN:
        assert sum(1 for x in ds if x["kieu"] == kieu) >= 15, kieu
    assert len({x["tu_muc"] for x in ds}) >= 15
    # mỗi biến thể chỉ sửa trường thuộc kiểu của nó và mang false ở đúng trục
    for x in ds:
        assert set(x["sua"]) <= B.TRUONG_DUOC_SUA[x["kieu"]]
        assert x["nhan_du_kien"][B.KIEU_DOT_BIEN[x["kieu"]]] is False


@pytest.mark.parametrize("hong, mau", [
    (dict(nhan=(None, True, None)), "phải mang nhãn dự kiến false"),
    (dict(kieu="quan_the", sua={"action": "Không dùng thuốc A"}), "chỉ được sửa"),
    (dict(sua={"population": "Người lớn suy tim HFrEF"}), "không đổi nội dung"),
    (dict(kieu="chieu", sua={"action": "Không dùng thuốc A"}, nhan=(True, False, False)), "khác nhãn mục gốc"),
    (dict(tu=9), "ngoài bộ vàng"),
    (dict(kieu="xyz"), "không thuộc"),
    (dict(mo_ta=" "), "thiếu mô tả"),
])
def test_kiem_de_xuat_bat_loi_cau_truc(hong, mau):
    bv = {"muc": [_muc(1, d=None)]}
    loi = B.kiem_de_xuat(bv, _dx(_db(**hong)))
    assert any(mau in x for x in loi), loi


def test_muc_goc_chua_nhan_hoac_la_dot_bien_khong_dung_lam_goc():
    bv = {"muc": [_muc(1, q=None, c=None, d=None), _muc(2, nguon_muc="dot_bien")]}
    loi = B.kiem_de_xuat(bv, _dx(_db(tu=1), _db(ma="D02", tu=2)))
    assert sum("mục thật đã có nhãn" in x for x in loi) == 2


def test_ma_trung_bi_bat():
    bv = {"muc": [_muc(1)]}
    assert any("mã trùng" in x for x in B.kiem_de_xuat(bv, _dx(_db(), _db())))


def test_dung_dot_bien_giu_nguon_va_gan_ma():
    bv = {"muc": [_muc(1)]}
    m = B.dung_dot_bien(bv, _dx(_db()))[0]
    assert m["population"] == "Trẻ em suy tim" and m["action"] == "Dùng thuốc A khi eGFR ≥30"
    assert m["pmid"] == "111" and m["id"] == "ITEM-1·D01" and m["nguon_muc"] == "dot_bien"
    assert m["nhan_bac_si"] is None and m["nhan_du_kien"]["dung_quan_the"] is False


# ───── lời duyệt ─────

MA = [f"D{i:02d}" for i in range(1, 13)]


@pytest.mark.parametrize("loi, duyet", [
    ("duyệt đột biến: tất cả", set(MA)),
    ("Duyệt đột biến: tất cả trừ D05, D12", set(MA) - {"D05", "D12"}),
    ("đồng ý toàn bộ, bỏ D03-D04", set(MA) - {"D03", "D04"}),
    ("duyệt D01-D03 và D07", {"D01", "D02", "D03", "D07"}),
])
def test_doc_loi_duyet_mau_hop_le(loi, duyet):
    d, _loai, loi_doc = B.doc_loi_duyet(loi, MA)
    assert loi_doc == [] and d == duyet


@pytest.mark.parametrize("loi, mau", [
    ("tất cả trừ D05", "thiếu lời duyệt"),
    ("duyệt tất cả, riêng D07 sửa nhãn", "vừa «tất cả»"),
    ("duyệt tất cả trừ", "không nêu mã"),
    ("duyệt D01, D99", "không có trong đề xuất"),
    ("duyệt D05-D02", "khoảng mã ngược"),
    ("duyệt đột biến", "không duyệt mã nào"),
])
def test_doc_loi_duyet_mo_ho_thi_khong_doan(loi, mau):
    _d, _l, loi_doc = B.doc_loi_duyet(loi, MA)
    assert any(mau in x for x in loi_doc), loi_doc


@pytest.fixture
def ba_tep(tmp_path):
    bv = {"_mo_ta": "x", "so_muc": 2, "muc": [_muc(1, d=None), _muc(2)]}
    dx = _dx(_db("D01", 1), _db("D02", 2, "dieu_kien", {"action": "Dùng thuốc A"}, (True, True, False), "rụng eGFR"),
             _db("D03", 2, "chieu", {"title": "Không dùng thuốc A 2", "action": "Không dùng thuốc A"}, (True, False, None)))
    t = {"bv": tmp_path / "bv.json", "dx": tmp_path / "dx.json", "ra": tmp_path / "ra.json"}
    t["bv"].write_text(json.dumps(bv, ensure_ascii=False), encoding="utf-8")
    t["dx"].write_text(json.dumps(dx, ensure_ascii=False), encoding="utf-8")
    return t


def _duyet(t, loi, **kw):
    return B.duyet_dot_bien(loi, tep_bv=t["bv"], tep_de_xuat=t["dx"], tep_ra=t["ra"], **kw)


def test_duyet_chay_kho_khong_ghi(ba_tep):
    assert _duyet(ba_tep, "duyệt đột biến: tất cả", ap_dung=False) == 0
    assert not ba_tep["ra"].exists()


def test_duyet_ghi_nhan_kem_nguyen_van_va_nguon_goc(ba_tep):
    loi = "duyệt đột biến: tất cả trừ D03"
    assert _duyet(ba_tep, loi, ap_dung=True) == 0
    ra = json.loads(ba_tep["ra"].read_text(encoding="utf-8"))
    ma = {m["dot_bien"]["ma"]: m for m in ra["muc"]}
    assert set(ma) == {"D01", "D02"} and ra["bi_loai"] == ["D03"]
    nh = ma["D02"]["nhan_bac_si"]
    assert nh["du_dieu_kien"] is False and nh["dung_quan_the"] is True and nh["loi_bac_si"] == loi
    assert nh["de_xuat_boi"] == B.DE_XUAT_BOI_DOT_BIEN
    assert len(B.doc_dot_bien_da_duyet(ba_tep["ra"])) == 2


def test_duyet_lai_khong_ghi_de_tru_khi_ghi_de(ba_tep, capsys):
    _duyet(ba_tep, "duyệt D01", ap_dung=True)
    truoc = ba_tep["ra"].read_text(encoding="utf-8")
    assert _duyet(ba_tep, "duyệt D01", ap_dung=True) == 0
    assert "bỏ qua D01" in capsys.readouterr().out
    assert json.loads(ba_tep["ra"].read_text(encoding="utf-8"))["muc"] == json.loads(truoc)["muc"]


def test_loi_duyet_khong_doc_duoc_thi_khong_ghi_gi(ba_tep):
    assert _duyet(ba_tep, "tất cả", ap_dung=True) == 1
    assert not ba_tep["ra"].exists()


def test_de_xuat_hong_thi_tu_choi_duyet(ba_tep):
    dx = json.loads(ba_tep["dx"].read_text(encoding="utf-8"))
    dx["dot_bien"][0]["nhan_du_kien"]["dung_quan_the"] = True
    ba_tep["dx"].write_text(json.dumps(dx, ensure_ascii=False), encoding="utf-8")
    assert _duyet(ba_tep, "duyệt đột biến: tất cả", ap_dung=True) == 2
    assert not ba_tep["ra"].exists()


def test_cho_duyet_bo_ma_da_duyet_va_da_loai(ba_tep):
    _duyet(ba_tep, "duyệt D01 trừ D03", ap_dung=True)
    bv = json.loads(ba_tep["bv"].read_text(encoding="utf-8"))
    assert [x["ma"] for x in B.de_xuat_cho_duyet(bv, ba_tep["dx"], ba_tep["ra"])] == ["D02"]


# ───── (b) mục thật phân tầng ─────

def _uv(i, tang, dash=None, pmid=None, action=None, decision="apply"):
    return {"dashboard": dash or f"D{i}.html", "tang": tang,
            "it": {"id": f"I{i}", "title": f"t{i}", "population": "p", "action": action or f"a{i}",
                   "pmid": pmid if pmid is not None else str(1000 + i), "decision": decision}}


def _chon(bv, uv, n):
    tang = {u["it"]["id"]: u["tang"] for u in uv}
    return B.chon_muc_that(bv, uv, n, tang_cua=lambda it: tang[it["id"]])


def test_chon_muc_that_theo_han_ngach_va_don_tang():
    uv = [_uv(i, "phu_dinh") for i in range(3)] + [_uv(10 + i, "dieu_kien") for i in range(30)] + \
         [_uv(50 + i, "dac_biet") for i in range(30)] + [_uv(90 + i, "khac") for i in range(30)]
    ra = _chon({"muc": []}, uv, 40)
    dem = {t: sum(1 for m in ra if m["tang"] == t) for t in B.TANG}
    assert len(ra) == 40 and dem["phu_dinh"] == 3 and dem["dieu_kien"] == 12 + 7   # 7 chỗ thiếu dồn sang tầng sau
    assert all(m["nguon_muc"] == "that" and m["nhan_bac_si"]["dung_quan_the"] is None for m in ra)


def test_chon_muc_that_loai_trung_bo_vang_trung_nhau_khong_pmid_va_khong_apply():
    bv = {"muc": [{"pmid": "1001", "action": "a1"}]}
    uv = [_uv(1, "khac"), _uv(2, "khac", pmid="1003", action="a3"), _uv(3, "khac"), _uv(4, "khac", pmid=""),
          _uv(5, "khac", decision="consider"), _uv(6, "khac")]
    ids = [m["id"] for m in _chon(bv, uv, 40)]
    assert sorted(ids) == ["I2", "I6"] or sorted(ids) == ["I3", "I6"]
    assert "I1" not in ids and "I4" not in ids and "I5" not in ids


def test_chon_muc_that_toi_da_hai_muc_moi_dashboard_va_tat_dinh():
    uv = [_uv(i, "khac", dash="cung.html") for i in range(10)]
    ra = _chon({"muc": []}, uv, 40)
    assert len(ra) == 2
    assert [m["id"] for m in ra] == [m["id"] for m in _chon({"muc": []}, uv, 40)]


def test_them_muc_that_chay_kho_khong_ghi_va_ap_dung_noi_so_muc(tmp_path):
    t = tmp_path / "bv.json"
    t.write_text(json.dumps({"so_muc": 1, "muc": [_muc(1)]}, ensure_ascii=False), encoding="utf-8")
    uv = [_uv(i, "khac") for i in range(5)]
    goc = t.read_text(encoding="utf-8")
    assert B.them_muc_that(3, ap_dung=False, tep=t, ung_vien=uv) == 0 and t.read_text(encoding="utf-8") == goc
    assert B.them_muc_that(3, ap_dung=True, tep=t, ung_vien=uv) == 0
    bv = json.loads(t.read_text(encoding="utf-8"))
    assert bv["so_muc"] == 4 and all(m.get("them_ngay") for m in bv["muc"][1:])


def test_bo_vang_da_commit_co_muc_that_moi_nhan_trong():
    bv = B.doc_bo_vang()
    moi = [m for m in bv["muc"] if m.get("nguon_muc") == "that"]
    assert len(moi) >= 40 and bv["so_muc"] == len(bv["muc"])
    for m in moi:   # máy chỉ RÚT mục — nhãn phải đến từ bác sĩ (`ghi --loi`), kèm nguyên văn
        nh = m["nhan_bac_si"]
        if any(nh.get(k) is not None for k in B.NHAN):
            assert nh.get("loi_bac_si") and not nh.get("de_xuat_boi"), m["id"]
    khoa = [(str(m.get("pmid")), B.chuan(str(m.get("action") or ""))) for m in moi]
    assert len(khoa) == len(set(khoa))


# ───── phiếu ─────

MAY = ("co_dieu_kien", "can_doc", "🟠", "k1_", "K1", "K4", "K3b", "gradeLevel", "tang", "nguon_muc")


def test_phieu_phan_b_chi_in_muc_chua_nhan_va_mu_voi_may():
    bv = {"muc": [_muc(1), _muc(2, q=None, c=None, d=None, tang="phu_dinh", nguon_muc="that")]}
    md = B.dung_phieu_md(bv, {"111": "BACKGROUND: x."})
    assert "## Mục 2 —" in md and "## Mục 1 —" not in md
    for la in MAY:
        assert la not in md, la


def test_phieu_phan_a_ban_goc_canh_ban_sua_va_nhan_du_kien():
    bv = {"muc": [_muc(1, d=None)]}
    md = B.dung_phieu_md(bv, {}, [_db()])
    assert "PHẦN A" in md and "PHẦN B" in md and "## D01" in md
    assert "Quần thể GỐC: Người lớn suy tim HFrEF" in md and "Quần thể ĐỘT BIẾN: Trẻ em suy tim" in md
    assert "S · Đ · —" in md and "mọi mục trong bộ vàng đã có nhãn".lower() in md.lower()
    for la in ("can_doc", "🟠", "K1", "K4"):
        assert la not in md


# ───── đo ─────

def _kiem(k1=False, k4=False, k4b=False, k3b=False):
    def kiem_muc(_it, _tx):
        return {"k1_nguong": [{"muc": "can_doc" if k1 else "khop"}], "k1_cap": [],
                "k4": {"muc": "can_doc" if k4 else "khop"}, "k4b": {"muc": "can_doc" if k4b else "khop"},
                "k3b": [{"muc": "can_doc" if k3b else "khop"}]}
    return kiem_muc


def test_do_tach_dot_bien_khoi_muc_that():
    bv = {"muc": [_muc(1), _muc(2)]}
    db = [dict(_muc(3), nguon_muc="dot_bien", nhan_bac_si={"dung_quan_the": False, "dung_chieu": True,
                                                          "du_dieu_kien": None, "loi_bac_si": "x"})]
    kq = B.do(bv, {"111": "abc"}, kiem_muc=_kiem(k1=True), dot_bien=db)
    assert kq["K1"]["n"] == 2 and kq["K1"]["fp"] == 2 and kq["K1"]["tp"] == 0     # mục thật: không lẫn đột biến
    assert kq["theo_nguon"]["dot_bien"]["K1"]["tp"] == 1 and kq["theo_nguon"]["dot_bien"]["n_muc"] == 1
    assert "theo_nguon" not in B.do(bv, {"111": "abc"}, kiem_muc=_kiem())          # không có đột biến ⇒ như cũ


def test_do_so_sanh_api_tren_cung_muc():
    bv = {"muc": [_muc(1, q=False), _muc(2, d=False), _muc(3)]}
    tra = {"ITEM-1": {"dung_quan_the": False, "dung_chieu": True, "du_dieu_kien": True},
           "ITEM-2": {"dung_quan_the": True, "dung_chieu": None, "du_dieu_kien": False}}
    kq = B.do(bv, {"111": "abc"}, kiem_muc=_kiem(), api=lambda m, _tx: tra.get(m["id"]))
    ss = kq["so_sanh_api"]
    assert ss["quan_the"]["api"]["tp"] == 1 and ss["quan_the"]["luat"]["fn"] == 1
    assert ss["dieu_kien"]["api"]["tp"] == 1 and ss["chieu"]["api_null"] == 1
    assert ss["quan_the"]["api_thieu"] == 1 and ss["quan_the"]["api"]["n"] == 2   # ITEM-3 chưa chạy ⇒ ngoài bảng API


def test_in_do_noi_ro_dot_bien_va_api(capsys):
    bv = {"muc": [_muc(1)]}
    db = [dict(_muc(3), nguon_muc="dot_bien", nhan_bac_si={"dung_quan_the": False, "dung_chieu": True,
                                                          "du_dieu_kien": None, "loi_bac_si": "x"})]
    B.in_do(B.do(bv, {"111": "abc"}, kiem_muc=_kiem(), dot_bien=db, api=lambda m, _t: None))
    out = capsys.readouterr().out
    assert "Đột biến có kiểm soát" in out and "Luật cứng ↔ bộ kiểm API" in out and "chưa chạy API" in out


# ───── bộ kiểm API ─────

TOM = ("1. N Engl J Med. 2026;1:1.\n\nTitle.\n\nSmith A(1), Tran B(2).\n\nAuthor information:\n(1)Dept X.\n\n"
       "BACKGROUND: adults with HFrEF. CONCLUSIONS: drug A recommended.\n\nPMID: 111")


def test_noi_dung_gui_api_khong_lo_nhan_ma_dashboard_hay_nguon_muc():
    bv = {"muc": [_muc(1)]}
    m = B.dung_dot_bien(bv, _dx(_db()))[0]
    nd = A.dung_noi_dung(m, A.than_tom_tat(TOM))
    for la in ("D01", "ITEM-1", "WebDashboard", "dot_bien", "nhan", "dung_quan_the", "đột biến", "quan_the"):
        assert la not in nd, la
    assert "Trẻ em suy tim" in nd and "drug A recommended" in nd


def test_khoa_muc_doi_khi_muc_tom_tat_hoac_model_doi():
    m = _muc(1)
    k = A.khoa_muc(m, "tt", "claude-sonnet-5-5")
    assert k == A.khoa_muc(dict(m, id="khac", dashboard="khac"), "tt", "claude-sonnet-5-5")   # id/dashboard không vào khoá
    assert k != A.khoa_muc(dict(m, action="Không dùng thuốc A"), "tt", "claude-sonnet-5-5")
    assert k != A.khoa_muc(m, "tt2", "claude-sonnet-5-5") and k != A.khoa_muc(m, "tt", "claude-opus-5-5")


def _doc_json(s):
    return json.loads(s)


@pytest.mark.parametrize("van_ban", [
    '{"dung_quan_the": true, "dung_chieu": "yes", "du_dieu_kien": null}',
    '{"dung_quan_the": true, "dung_chieu": true}',
    '[1, 2]',
])
def test_doc_tra_loi_khuon_sai_thi_bao_khong_doan(van_ban):
    with pytest.raises(ValueError):
        A.doc_tra_loi(van_ban, _doc_json)


class _LoiApi(RuntimeError):
    pass


class _LoiCucBo(_LoiApi):
    pass


class _KetQuaHong(_LoiApi):
    pass


def _cau_noi_gia(tra_loi, nem=None):
    goi_ds = []

    def goi(noi_dung, **kw):
        goi_ds.append((noi_dung, kw))
        x = nem(len(goi_ds)) if nem else None
        if x:
            raise x
        return SimpleNamespace(van_ban=tra_loi, model="claude-sonnet-5-5", token_vao=10, token_ra=5, token_cache_doc=0)
    nk = []
    return SimpleNamespace(goi=goi, doc_json=_doc_json, LoiApi=_LoiApi, LoiCucBo=_LoiCucBo, KetQuaHong=_KetQuaHong,
                           in_chi_phi=lambda a, b, m: f"{a}/{b}/{m}",
                           ghi_nhat_ky_api=lambda *a, **k: nk.append((a, k)), _goi=goi_ds, _nk=nk)


OK = '{"dung_quan_the": false, "dung_chieu": true, "du_dieu_kien": null, "ly_do": {"quan_the": "khác"}}'


def test_chay_kho_khong_goi_api(tmp_path, capsys):
    cn = _cau_noi_gia(OK)
    assert A.chay([_muc(1)], {"111": TOM}, goi_api=False, cau_noi=cn, tep=tmp_path / "dem.json") == 0
    assert cn._goi == [] and not (tmp_path / "dem.json").exists()
    assert "cần gọi 1" in capsys.readouterr().out


def test_goi_ghi_bo_dem_moi_muc_va_lan_sau_khong_goi_lai(tmp_path):
    cn, tep = _cau_noi_gia(OK), tmp_path / "dem.json"
    ds = [_muc(1), _muc(2)]
    assert A.chay(ds, {"111": TOM}, goi_api=True, cau_noi=cn, tep=tep) == 0
    assert len(cn._goi) == 2
    kw = cn._goi[0][1]
    assert kw["he_thong"] == A.HE_THONG and kw["cache_he_thong"] is True and kw["nguon"] == A.NGUON
    assert "max_tokens" not in kw                              # để cầu nối dùng mặc định 16000 (BH180)
    assert A.chay(ds, {"111": TOM}, goi_api=True, cau_noi=cn, tep=tep) == 0 and len(cn._goi) == 2
    tra = A.tra_bo_dem(tep)(_muc(1), TOM)
    assert tra["dung_quan_the"] is False and tra["du_dieu_kien"] is None
    assert cn._nk[0][0][0] == "ok"


def test_mot_muc_hong_di_tiep_cham_tran_thi_dung(tmp_path):
    cn = _cau_noi_gia(OK, nem=lambda n: _KetQuaHong("cắt cụt") if n == 1 else (_LoiCucBo("HetNganSach") if n == 3 else None))
    tep = tmp_path / "dem.json"
    assert A.chay([_muc(i) for i in range(1, 6)], {"111": TOM}, goi_api=True, cau_noi=cn, tep=tep) == 1
    assert len(cn._goi) == 3                                    # mục 1 hỏng, mục 2 xong, mục 3 chạm trần ⇒ dừng
    assert len(json.loads(tep.read_text(encoding="utf-8"))) == 1
    assert cn._nk[0][0][0] == "loi"


def test_loi_api_mang_khoa_thi_dung_ngay(tmp_path):
    cn = _cau_noi_gia(OK, nem=lambda n: _LoiApi("401"))
    assert A.chay([_muc(1), _muc(2)], {"111": TOM}, goi_api=True, cau_noi=cn, tep=tmp_path / "d.json") == 1
    assert len(cn._goi) == 1


def test_thieu_cau_noi_khi_goi_api_tra_2_khong_gui(tmp_path):
    assert A.chay([_muc(1)], {"111": TOM}, goi_api=True, cau_noi=None, tep=tmp_path / "d.json") == 2


def test_muc_khong_co_tom_tat_khong_goi(tmp_path):
    cn = _cau_noi_gia(OK)
    A.chay([_muc(1, pmid="999")], {"111": TOM}, goi_api=True, cau_noi=cn, tep=tmp_path / "d.json")
    assert cn._goi == []


def test_duoi_pytest_khong_ghi_bo_dem_that(monkeypatch):
    monkeypatch.delenv("EBM_KIEM_API_THAT", raising=False)
    with pytest.raises(RuntimeError):
        A.ghi_bo_dem(A.tep_bo_dem(), {})


def test_tap_muc_gom_muc_that_va_moi_de_xuat():
    ds = A.tap_muc()
    dx = json.loads(B.TEP_DOT_BIEN_DE_XUAT.read_text(encoding="utf-8"))
    assert sum(1 for m in ds if m.get("nguon_muc") == "dot_bien") == len(dx["dot_bien"])
    assert all((m.get("nguon_muc") or "that") == "that" for m in A.tap_muc("that"))


_CAU_NOI_THAT = Path(os.environ.get("EBM_CAU_NOI_THU") or A.CAU_NOI)


@pytest.mark.skipif(not _CAU_NOI_THAT.is_file(), reason="không có cầu nối y khoa (phiên một-repo / CI gốc)")
def test_khop_cau_noi_that_voi_khach_gia(tmp_path, monkeypatch):
    """Dùng ĐÚNG api_claude_nc.goi (khách giả) — bắt lệch chữ ký/lớp lỗi mà cầu nối giả ở trên không bắt được."""
    cn = A._nap("_bvm_cau_noi_that", _CAU_NOI_THAT)
    monkeypatch.setattr(cn, "SO_CHI_PHI", str(tmp_path / "cp.json"))
    monkeypatch.setattr(cn, "NHAT_KY_API", str(tmp_path / "nk.json"))
    goi_kw = []

    class _Msgs:
        def create(self, **kw):
            goi_kw.append(kw)
            return SimpleNamespace(content=[SimpleNamespace(text=OK)], model=kw["model"], stop_reason="end_turn",
                                   usage=SimpleNamespace(input_tokens=100, output_tokens=40,
                                                         cache_creation_input_tokens=0, cache_read_input_tokens=0))
    khach = SimpleNamespace(messages=_Msgs(), beta=SimpleNamespace(messages=_Msgs()))
    tep = tmp_path / "dem.json"
    assert A.chay([_muc(1)], {"111": TOM}, goi_api=True, cau_noi=cn, client=khach, tep=tep) == 0
    assert goi_kw and goi_kw[0]["max_tokens"] >= 16000 and goi_kw[0]["system"][0]["cache_control"]
    assert json.loads(tep.read_text(encoding="utf-8"))
    # cắt cụt ⇒ KetQuaHong của cầu nối thật ⇒ mục lỗi, không ghi bộ đệm
    goi_kw.clear()
    _Msgs.create = lambda self, **kw: SimpleNamespace(content=[SimpleNamespace(text='{"dung_')], model=kw["model"],
                                                       stop_reason="max_tokens", usage=None)
    assert A.chay([_muc(2, action="khác")], {"111": TOM}, goi_api=True, cau_noi=cn, client=khach, tep=tep) == 1
    assert len(json.loads(tep.read_text(encoding="utf-8"))) == 1


def test_main_cli_api_chay_kho(monkeypatch, capsys):
    monkeypatch.setattr(A, "nap_cau_noi", lambda duong=None: None)
    assert A.main([]) == 0
    assert "(chạy khô)" in capsys.readouterr().out


def test_khong_sua_do_cu_khi_khong_truyen_tham_so_moi():
    """`do(bv, nguon, kiem_muc)` cũ (3 tham số) giữ đúng khoá trả về như trước 19/11."""
    kq = B.do({"muc": [_muc(1)]}, {"111": "abc"}, kiem_muc=_kiem())
    assert {"K1", "K4", "K3b", "K4b", "chua", "so_nhan"} <= set(kq) and "so_sanh_api" not in kq
    assert copy.deepcopy(kq) == kq


# ───── hòm việc ─────

def test_giac_quan_bao_viec_bac_si_va_het_viec_thi_im(ba_tep):
    viec, chet = B.giac_quan(ba_tep["bv"], ba_tep["dx"], ba_tep["ra"])
    assert chet == [] and len(viec) == 1 and viec[0][1] == "👤" and "3 đột biến chờ duyệt" in viec[0][2]
    _duyet(ba_tep, "duyệt đột biến: tất cả", ap_dung=True)
    assert B.giac_quan(ba_tep["bv"], ba_tep["dx"], ba_tep["ra"]) == ([], [])


def test_giac_quan_bo_vang_hong_la_chet_khong_phai_het_viec(tmp_path):
    (tmp_path / "bv.json").write_text("{hỏng", encoding="utf-8")
    viec, chet = B.giac_quan(tmp_path / "bv.json", tmp_path / "dx.json", tmp_path / "ra.json")
    assert viec == [] and chet


def test_giac_quan_de_xuat_hong_bao_chet(ba_tep):
    dx = json.loads(ba_tep["dx"].read_text(encoding="utf-8"))
    dx["dot_bien"][0]["kieu"] = "xyz"
    ba_tep["dx"].write_text(json.dumps(dx, ensure_ascii=False), encoding="utf-8")
    _viec, chet = B.giac_quan(ba_tep["bv"], ba_tep["dx"], ba_tep["ra"])
    assert any("hỏng" in c for c in chet)


def test_hom_viec_goi_giac_quan_bo_vang():
    tdxv = _nap("_bvm_tdxv", "tu_de_xuat_viec.py")
    viec = tdxv.giac_quan_bo_vang_ngu_nghia()
    assert viec and viec[0][1] == "👤" and "bo_vang_kiem_ngu_nghia.py phieu" in viec[0][3]
