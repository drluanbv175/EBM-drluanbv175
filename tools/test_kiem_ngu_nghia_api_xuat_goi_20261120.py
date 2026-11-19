# -*- coding: utf-8 -*-
"""Bộ kiểm ngữ nghĩa Claude API ở bước xuất gói (20/11/2026, bác sĩ «Làm 2,3,6» — mục 3). OFFLINE, không gọi API thật.

Chốt: (1) chính sách tắt/vắng/hỏng ⇒ không gọi, không in kết quả cũ; (2) GIỮ MÙ — mục thật của bộ vàng chưa có nhãn bác sĩ
không được gọi/in; (3) chỉ mục apply có PMID; (4) bộ đệm dùng lại, trần lượt gọi mỗi dashboard; (5) lỗi trần/khoá ⇒ dừng gửi;
(6) mọi đầu ra mang nhãn CHƯA HIỆU CHUẨN; (7) bộ năm gọi bước này ở mức cảnh báo và có cờ --khong-api.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

_TOOLS = Path(__file__).resolve().parent


def _nap(ten, tep):
    sp = importlib.util.spec_from_file_location(ten, _TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


A = _nap("_knx_api", "kiem_ngu_nghia_api.py")
B = A._bvk()


class _LoiApi(RuntimeError):
    pass


class _LoiCucBo(_LoiApi):
    pass


class _KetQuaHong(_LoiApi):
    pass


def _cau_noi(tra_loi, nem=None):
    ds, nk = [], []

    def goi(noi_dung, **kw):
        ds.append((noi_dung, kw))
        x = nem(len(ds)) if nem else None
        if x:
            raise x
        return SimpleNamespace(van_ban=tra_loi, model="claude-sonnet-5-5", token_vao=10, token_ra=5, token_cache_doc=0)
    return SimpleNamespace(goi=goi, doc_json=json.loads, LoiApi=_LoiApi, LoiCucBo=_LoiCucBo, KetQuaHong=_KetQuaHong,
                           ghi_nhat_ky_api=lambda *a, **k: nk.append((a, k)), _goi=ds, _nk=nk)


NGHI = '{"dung_quan_the": false, "dung_chieu": true, "du_dieu_kien": false, "ly_do": {"quan_the": "nguồn là người cao tuổi", "dieu_kien": "bỏ ngưỡng eGFR"}}'
ON = '{"dung_quan_the": true, "dung_chieu": true, "du_dieu_kien": null, "ly_do": {}}'

ITEMS = [
    {"id": "ITEM-01", "decision": "apply", "pmid": "111", "title": "Dùng thuốc A", "population": "Người lớn", "action": "Dùng A"},
    {"id": "ITEM-02", "decision": "apply", "pmid": "222", "title": "Dùng thuốc B", "population": "Người lớn", "action": "Dùng B"},
    {"id": "ITEM-03", "decision": "consider", "pmid": "333", "title": "Cân nhắc C", "population": "x", "action": "y"},
    {"id": "ITEM-04", "decision": "apply", "pmid": "", "title": "Nhãn FDA D", "population": "x", "action": "y"},
    {"id": "ITEM-05", "decision": "apply", "pmid": "555", "title": "Mục bộ vàng chờ nhãn", "population": "x", "action": "y"},
    {"id": "ITEM-06", "decision": "apply", "pmid": "666", "title": "Mục bộ vàng ĐÃ có nhãn", "population": "x", "action": "y"},
]
BV = {"muc": [
    {"dashboard": "khac.html", "id": "ITEM-99", "pmid": "555", "title": "mục bộ vàng  chờ nhãn", "nguon_muc": "that",
     "nhan_bac_si": {"dung_quan_the": None, "dung_chieu": None, "du_dieu_kien": None}},
    {"dashboard": "WebDashboard_X.html", "id": "ITEM-06", "pmid": "666", "title": "Mục bộ vàng ĐÃ có nhãn", "nguon_muc": "that",
     "nhan_bac_si": {"dung_quan_the": True, "dung_chieu": True, "du_dieu_kien": None}},
    {"dashboard": "WebDashboard_Y.html", "id": "ITEM-02", "pmid": "999", "title": "khác hẳn", "nguon_muc": "that",
     "nhan_bac_si": {}},
]}


def _kqtc(items=ITEMS, tai=None):
    tai_ds = []

    def _tai(pm):
        tai_ds.append(pm)
        return (tai or {}).get(pm, f"Tóm tắt nguồn PMID {pm}. Conclusions: dùng được.")
    return SimpleNamespace(doc_data=lambda d: {"items": items}, _tai_online=_tai, than_nguon=lambda raw: raw, _tai_ds=tai_ds)


def _chay(tmp_path, cn, capsys, **kw):
    dash = tmp_path / "WebDashboard_X.html"
    dash.write_text("<html></html>", encoding="utf-8")
    k = dict(cau_noi=cn, goi_api=True, online=True, bv=BV, tep_dem=tmp_path / "dem.json", tep_tt=tmp_path / "tt.json",
             tep_dem_bv=tmp_path / "dem_bv.json", kqtc=_kqtc(), bvk=B)
    k.update(kw)
    ma = A.kiem_dashboard_api(dash, **k)
    return ma, capsys.readouterr().out


def test_chi_cham_apply_co_pmid_va_giu_mu_bo_vang(tmp_path, capsys):
    cn = _cau_noi(ON)
    ma, out = _chay(tmp_path, cn, capsys)
    gui = "\n".join(x[0] for x in cn._goi)
    assert ma == 0 and len(cn._goi) == 3                                     # ITEM-01, 02, 06
    assert "Mục bộ vàng chờ nhãn" not in gui and "Cân nhắc C" not in gui and "Nhãn FDA D" not in gui
    assert "ITEM-05" not in out and "ẩn giữ mù bộ vàng 1" in out           # khớp theo PMID (tiêu đề khác vẫn ẩn)
    assert A.NHAN_CHUA_HIEU_CHUAN in out                                   # nhãn đầy đủ ở đầu báo cáo
    cuoi = out.strip().splitlines()[-1]
    assert cuoi.startswith("Tổng:") and "CHƯA HIỆU CHUẨN" in cuoi           # bộ năm chỉ in dòng Tổng — nhãn phải ở đó
    assert all(x[1]["nguon"] == A.NGUON_XUAT for x in cn._goi)


def test_giu_mu_theo_dashboard_va_id(tmp_path, capsys):
    bv = {"muc": [{"dashboard": "WebDashboard_X.html", "id": "ITEM-01", "pmid": "0", "title": "khác", "nguon_muc": "that"}]}
    cn = _cau_noi(ON)
    _, out = _chay(tmp_path, cn, capsys, bv=bv)
    assert "Dùng thuốc A" not in "\n".join(x[0] for x in cn._goi) and "ẩn giữ mù bộ vàng 1" in out


def test_in_muc_bi_nghi_kem_ly_do_va_ma_1(tmp_path, capsys):
    ma, out = _chay(tmp_path, _cau_noi(NGHI), capsys)
    assert ma == 1
    assert "🟠 [ITEM-01] PMID 111 — API nghi lệch quần thể, điều kiện" in out and "bỏ ngưỡng eGFR" in out
    assert "NGHI 3 (quần thể 3 · chiều 0 · điều kiện 3)" in out


def test_bo_dem_dung_lai_va_tom_tat_tai_mot_lan(tmp_path, capsys):
    cn = _cau_noi(ON)
    _chay(tmp_path, cn, capsys)
    kq2 = _kqtc()
    cn2 = _cau_noi(ON)
    ma, out = _chay(tmp_path, cn2, capsys, kqtc=kq2)
    assert ma == 0 and cn2._goi == [] and kq2._tai_ds == []                 # lượt 2: không gọi API, không tải lại tóm tắt
    assert "có kết quả 3" in out


def test_tran_luot_goi_moi_dashboard(tmp_path, capsys):
    cn = _cau_noi(ON)
    _, out = _chay(tmp_path, cn, capsys, toi_da=1)
    assert len(cn._goi) == 1 and "vượt trần 1 lượt/dashboard — 2 mục chưa chấm" in out


def test_loi_tran_chi_phi_dung_gui_va_ket_qua_hong_di_tiep(tmp_path, capsys):
    cn = _cau_noi(ON, nem=lambda n: _KetQuaHong("cắt cụt") if n == 1 else (_LoiCucBo("HetNganSach") if n == 2 else None))
    ma, out = _chay(tmp_path, cn, capsys)
    assert ma == 1 and len(cn._goi) == 2 and "⛔ dừng gọi API: _LoiCucBo" in out and "✗ ITEM-01: cắt cụt" in out
    assert cn._nk and cn._nk[0][0][0] == "loi"


def test_chay_kho_va_khong_cau_noi_khong_goi(tmp_path, capsys):
    cn = _cau_noi(ON)
    ma, out = _chay(tmp_path, cn, capsys, goi_api=False)
    assert cn._goi == [] and "(chạy khô) 3 mục" in out and ma == 0
    ma, out = _chay(tmp_path, None, capsys)
    assert "không có cầu nối" in out


def test_khong_online_khong_tai_tom_tat(tmp_path, capsys):
    kq = _kqtc()
    ma, out = _chay(tmp_path, _cau_noi(ON), capsys, online=False, kqtc=kq)
    assert kq._tai_ds == [] and "thiếu tóm tắt 3" in out


def test_chinh_sach_tat_vang_hong_thi_khong_chay(tmp_path, capsys):
    dash = tmp_path / "WebDashboard_X.html"
    dash.write_text("x", encoding="utf-8")
    for nd in (None, "{hỏng", '{"tu_chay": {"ngu_nghia_xuat_goi": false}}', '{"tu_chay": {"ngu_nghia_xuat_goi": "true"}}'):
        cs = tmp_path / "cs.json"
        if nd is None:
            cs.unlink(missing_ok=True)
        else:
            cs.write_text(nd, encoding="utf-8")
        cn = _cau_noi(ON)
        assert A.chay_buoc_xuat(dash, online=True, goi_api=True, tep_cs=cs, cau_noi=cn) == 2
        assert cn._goi == [] and "TẮT" in capsys.readouterr().out
    cs.write_text('{"tu_chay": {"ngu_nghia_xuat_goi": true}}', encoding="utf-8")
    assert A.bat_trong_chinh_sach(cs) is True


def test_chinh_sach_that_cua_repo_da_bat_va_api_khi_can_van_doc_duoc():
    assert A.bat_trong_chinh_sach() is True
    K = _nap("_knx_akc", "api_khi_can.py")
    cs = K.doc_chinh_sach()
    assert cs is not None and all(cs["tu_chay"][v] for v in K.VIEC)          # khoá mới không làm hỏng chính sách cũ


def test_bo_nam_goi_buoc_canh_bao_va_co_co_khong_api():
    ma = (_TOOLS / "xuat_goi_cap_nhat.py").read_text(encoding="utf-8")
    i = ma.index("# ── ④-quinquies")
    j = ma.index("# ── ④-quater", i)
    doan = ma[i:j]
    assert '"--dashboard", str(dash), "--online", "--goi-api"' in doan and "elif a.khong_api:" in doan
    assert "rc_final" not in doan.replace("không đổi\n    # rc_final", "")             # cảnh báo: không đụng mã thoát
    assert '"--khong-api"' in ma
