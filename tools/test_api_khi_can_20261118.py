#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt cho cơ chế TỰ CHẠY API CLAUDE KHI CẦN (18/11/2026, bác sĩ duyệt) — `tools/api_khi_can.py`.

Bác sĩ chọn tự chạy «Khi hệ thống nghiên cứu y khoa và cập nhật chứng cứ cần, Quét lạc chủ đề phần đổi, Kiểm đề cương khi
đổi, CAFÉ-S khi agent an toàn đổi»; trần chi tiêu đặt ở Claude Console.

NGOẠI TUYẾN TUYỆT ĐỐI: mọi lượt «gọi API» là hàm giả tiêm vào; sổ, khoá, báo cáo đều ở tmp_path; không đọc kho khoá thật,
không phóng tiến trình nền thật. Các chốt ★ khoá RÀO TIỀN: dưới pytest không bao giờ gọi thật / phóng nền thật."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CTR_PATH = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "check_topic_relevance.py"


def _nap(ten: str, duong: Path):
    if str(duong.parent) not in sys.path:
        sys.path.insert(0, str(duong.parent))
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


@pytest.fixture
def akc(tmp_path, monkeypatch):
    m = _nap(f"_akc_{tmp_path.name}", HERE / "api_khi_can.py")
    monkeypatch.setattr(m, "SO", tmp_path / "so.json")
    cs = tmp_path / "chinh-sach.json"
    cs.write_text(json.dumps({"tu_chay": {"chu_de": True, "de_cuong": True, "cafes": True}}), encoding="utf-8",
                  newline="\n")
    monkeypatch.setattr(m, "CHINH_SACH", cs)
    return m


@pytest.fixture
def ctr(tmp_path):
    m = _nap(f"_ctr_akc_{tmp_path.name}", CTR_PATH)
    m.NHAT_KY_API = str(tmp_path / "nk.json")
    m.NHAT_KY_CHU_DE = str(tmp_path / "so-chu-de.json")
    return m


@pytest.fixture
def quet():
    return _nap("_quet_akc", HERE / "quet_lac_chu_de_kho.py")


def _db(goc: Path, ten: str, cau: str = "Tăng huyết áp ngoại trú", muc=(("ITEM-01", "Bài A", "Áp dụng"),)) -> Path:
    thu_muc = goc / "EBM-Dashboards"
    thu_muc.mkdir(parents=True, exist_ok=True)
    items = ",\n".join(f"    {{ id: '{i}', title: '{t}', action: '{a}' }}" for i, t, a in muc)
    f = thu_muc / ten
    f.write_text(f"<html><script>const DATA = {{\n  meta: {{ question: '{cau}' }},\n  items: [\n{items}\n  ],\n"
                 "  summary: { conclusion: 'x', doNow: [], dontDo: [], redFlags: [] }\n};</script></html>",
                 encoding="utf-8", newline="\n")
    return f


# ════════════════ sổ «đã kiểm chủ đề» của cổng ════════════════

def test_van_tay_cong_trung_prompt_cua_quet_toan_kho(tmp_path, ctr, quet):
    """★ Cổng, quét toàn kho và bộ phát hiện phải băm CÙNG một thứ — lệch thì cơ chế trả tiền chấm lại mãi mãi."""
    f = _db(tmp_path, "WebDashboard_A_20261101.html")
    yc = quet.dung_yeu_cau(ctr, f)
    assert ctr.van_tay_chu_de(str(f)) == hashlib.sha256(yc["prompt"].encode("utf-8")).hexdigest()


def test_cong_ghi_so_khi_cham_ok_va_chi_khi_ok(tmp_path, ctr):
    f = _db(tmp_path, "WebDashboard_A_20261101.html")
    for st in ("error", "skipped"):
        ctr._cham_chu_de = lambda _p, st=st: {"status": st, "message": "x"}
        ctr.check_dashboard_topic_relevance(str(f))
        assert ctr.doc_so_chu_de() == {}
    ctr._cham_chu_de = lambda _p: {"status": "ok", "total_items": 1, "off_topic": [{"id": "ITEM-01"}], "uncertain": []}
    ctr.check_dashboard_topic_relevance(str(f))
    so = ctr.doc_so_chu_de()
    assert so[f.name]["van_tay"] == ctr.van_tay_chu_de(str(f)) and so[f.name]["so_lac"] == 1


def test_so_chu_de_duoi_pytest_khong_ghi_tep_that(tmp_path, ctr, monkeypatch):
    monkeypatch.delenv("EBM_KIEM_API_THAT", raising=False)
    that = tmp_path / "that.json"
    monkeypatch.setattr(ctr, "_NKCD_THAT", str(that))
    ctr.ghi_so_chu_de("x.html", "abc", {"status": "ok"}, tep=str(that))
    assert not that.exists()


def test_quet_toan_kho_ghi_so_cho_dashboard_ok(tmp_path, ctr, quet):
    f1, f2 = _db(tmp_path, "WebDashboard_A_20261101.html"), _db(tmp_path, "WebDashboard_B_20261101.html")
    yc = [quet.dung_yeu_cau(ctr, f1), quet.dung_yeu_cau(ctr, f2)]
    cham = [{"status": "ok", "so_muc": 1, "off_topic": [], "uncertain": []}, {"status": "error"}]
    assert quet.ghi_so_da_kiem(ctr, yc, cham) == 1
    so = ctr.doc_so_chu_de()
    assert set(so) == {f1.name} and so[f1.name]["van_tay"] == ctr.van_tay_chu_de(str(f1))
    assert so[f1.name]["nguon"] == "quet_lac_chu_de_kho"


def test_cong_cu_khong_co_ghi_so_thi_quet_bo_qua_em(quet):
    class CongCu:
        pass
    assert quet.ghi_so_da_kiem(CongCu(), [{"tep": "x", "prompt": "p"}], [{"status": "ok"}]) == 0


# ════════════════ phát hiện «quét lạc chủ đề phần đổi» ════════════════

def test_chi_ban_moi_nhat_va_chi_noi_dung_doi(tmp_path, akc, ctr, quet):
    _db(tmp_path, "WebDashboard_A_20261101.html")
    moi = _db(tmp_path, "WebDashboard_A_20261110.html", muc=(("ITEM-01", "Bài A", "Áp dụng"), ("ITEM-02", "Bài B", "Cân nhắc")))
    khong_doi = _db(tmp_path, "WebDashboard_B_20261101.html", cau="Đái tháo đường")
    so = {khong_doi.name: {"van_tay": ctr.van_tay_chu_de(str(khong_doi))},
          moi.name: {"van_tay": "van-tay-cu-truoc-khi-sua"}}
    can = akc.can_chu_de(tmp_path, so_chu_de=so, Q=quet, C=ctr)
    assert [x["tep"].name for x in can] == [moi.name] and can[0]["so_muc"] == 2 and can[0]["uoc_usd"] > 0


def test_quet_toan_kho_phu_tep_khong_sua_sau_do(tmp_path, akc, ctr, quet):
    cu = _db(tmp_path, "WebDashboard_A_20261101.html")
    sua_sau = _db(tmp_path, "WebDashboard_B_20261101.html", cau="Đái tháo đường")
    dv = tmp_path / "EBM-Dashboards" / "derivatives"
    dv.mkdir()
    js = dv / "QUET-LAC-CHU-DE_20261117.json"
    js.write_text(json.dumps({"ket_qua": [{"tep": cu.name, "status": "ok"}, {"tep": sua_sau.name, "status": "ok"}]}),
                  encoding="utf-8", newline="\n")
    moc = js.stat().st_mtime
    os.utime(cu, (moc - 100, moc - 100))
    os.utime(sua_sau, (moc + 100, moc + 100))          # sửa SAU lượt quét toàn kho ⇒ phải kiểm lại
    can = akc.can_chu_de(tmp_path, so_chu_de={}, Q=quet, C=ctr)
    assert [x["tep"].name for x in can] == [sua_sau.name]


def test_so_cong_thang_quet_toan_kho_khi_ca_hai_co(tmp_path, akc, ctr, quet):
    """Sổ của cổng là căn cứ chính: tệp có trong sổ mà vân tay lệch ⇒ CẦN kiểm, dù quét toàn kho từng chấm «ok»."""
    f = _db(tmp_path, "WebDashboard_A_20261101.html")
    dv = tmp_path / "EBM-Dashboards" / "derivatives"
    dv.mkdir()
    (dv / "QUET-LAC-CHU-DE_20261117.json").write_text(json.dumps({"ket_qua": [{"tep": f.name, "status": "ok"}]}),
                                                     encoding="utf-8", newline="\n")
    os.utime(f, (1, 1))
    assert len(akc.can_chu_de(tmp_path, so_chu_de={f.name: {"van_tay": "khac"}}, Q=quet, C=ctr)) == 1


# ════════════════ chạy «quét lạc chủ đề phần đổi» ════════════════

def _cs(akc, **kw):
    cs = akc.doc_chinh_sach()
    cs.update(kw)
    return cs


def test_cham_bang_cong_va_ghi_bao_cao_khi_co_muc_nghi_lac(tmp_path, akc):
    can = [{"tep": tmp_path / f"WebDashboard_{c}_20261101.html", "so_muc": 3, "uoc_usd": 0.01} for c in "ABC"]
    def goi(p):
        if "_A_" in p:
            return {"status": "ok", "topic": "THA", "off_topic": [{"id": "ITEM-02", "title": "Thai kỳ", "reason": "sản"}],
                    "uncertain": ["ITEM-03"]}
        return {"status": "ok", "topic": "x", "off_topic": [], "uncertain": []}
    r = akc.chay_chu_de(can, _cs(akc, chu_de_toi_da_moi_luot=2), tmp_path, goi)
    assert (r["ket_qua"], r["da_cham"], r["con_lai"], r["so_lac"], r["so_khong_chac"]) == ("ok", 2, 1, 1, 1)
    md = Path(r["bao_cao"])
    assert md.name.startswith("KIEM-CHU-DE-KHI-CAN_") and "ITEM-02" in md.read_text(encoding="utf-8")
    assert "không mục nào bị gỡ" in md.read_text(encoding="utf-8")


def test_sach_thi_khong_ghi_bao_cao(tmp_path, akc):
    can = [{"tep": tmp_path / "WebDashboard_A_20261101.html", "so_muc": 3, "uoc_usd": 0.01}]
    r = akc.chay_chu_de(can, _cs(akc), tmp_path, lambda p: {"status": "ok", "off_topic": [], "uncertain": []})
    assert r["bao_cao"] == "" and not (tmp_path / "EBM-Dashboards").exists()


@pytest.mark.parametrize("tra, ly_do", [
    ({"status": "error", "message": "401"}, "3 lỗi liền"),
    ({"status": "skipped", "message": "Thiếu ANTHROPIC_API_KEY — đặt…"}, "ANTHROPIC_API_KEY"),
])
def test_dung_som_khi_khoa_hong_hoac_loi_lien(tmp_path, akc, tra, ly_do):
    """Khoá chết thì không gọi tiếp 60 lượt vô ích."""
    goi_dem = []
    can = [{"tep": tmp_path / f"WebDashboard_{i}_20261101.html", "so_muc": 1, "uoc_usd": 0.01} for i in range(10)]
    r = akc.chay_chu_de(can, _cs(akc), tmp_path, lambda p: goi_dem.append(p) or tra)
    assert r["ket_qua"] == "loi" and ly_do in r["dung"] and len(goi_dem) <= 3


def test_duoi_pytest_khong_bao_gio_goi_cong_that(tmp_path, akc):
    """★ RÀO TIỀN: không tiêm hàm gọi ⇒ dưới pytest phải BỎ QUA, không nạp cổng thật (cổng thật + venv = gọi API thật)."""
    r = akc.chay_chu_de([{"tep": tmp_path / "x.html", "so_muc": 1, "uoc_usd": 0}], _cs(akc), tmp_path)
    assert r["ket_qua"] == "bo_qua"


# ════════════════ kiểm đề cương khi đổi ════════════════

def _mea(tmp_path: Path, tt) -> Path:
    goc = tmp_path / "mea"
    (goc / "tools").mkdir(parents=True)
    (goc / "tools" / "duyet_kiem_may_api.py").write_text(
        f"def tinh_trang_tat_ca(goc):\n    return {tt!r}\n", encoding="utf-8", newline="\n")
    return goc


def test_chi_bao_cao_khang_dinh_cu_moi_tu_chay(tmp_path, akc):
    tt = [{"study": "btm", "bao_cao": [{"loai": "A12", "ten": "A12", "cu": True, "ly_do": "băm khác"},
                                       {"loai": "PHAN_BIEN", "ten": "PB", "cu": None, "ly_do": "chưa có mã băm"}]},
          {"study": "c1a", "bao_cao": [{"loai": "A12", "ten": "A12", "cu": False, "ly_do": "khớp"}]}]
    can, ly = akc.can_de_cuong(_mea(tmp_path, tt))
    assert ly == "" and [(x["study"], x["loai"]) for x in can] == [("btm", "A12")]


def test_thieu_cong_cu_y_khoa_la_khong_do_duoc(tmp_path, akc):
    can, ly = akc.can_de_cuong(tmp_path / "khong-co")
    assert can == [] and "#306" in ly


def test_cong_cu_y_khoa_loi_la_khong_do_duoc_khong_phai_khong_co_viec(tmp_path, akc):
    goc = tmp_path / "mea"
    (goc / "tools").mkdir(parents=True)
    (goc / "tools" / "duyet_kiem_may_api.py").write_text("def tinh_trang_tat_ca(goc):\n    raise RuntimeError('hỏng')\n",
                                                         encoding="utf-8", newline="\n")
    can, ly = akc.can_de_cuong(goc)
    assert can == [] and "RuntimeError" in ly


def test_chay_de_cuong_goi_that_va_doc_ma_thoat_dung(tmp_path, akc):
    lenh_da_chay = []
    def chay(lenh, cwd, timeout):
        lenh_da_chay.append(lenh)
        return (1, "có 3 phát hiện cần xem") if "kiem_noi_dung_trich_dan.py" in lenh[1] else (0, "sạch")
    can = [{"study": "btm", "loai": "A12"}, {"study": "btm", "loai": "PHAN_BIEN"}]
    r = akc.chay_de_cuong(can, tmp_path, chay)
    assert r["ket_qua"] == "ok" and r["so_loi"] == 0 and r["chi_tiet"][0]["co_phat_hien"] is True
    assert all(lenh[-1] == "--goi-api" and lenh[-3:-1] == ["--study", "btm"] for lenh in lenh_da_chay)


def test_cham_tran_chi_phi_thi_dung_cac_viec_con_lai(tmp_path, akc):
    dem = []
    r = akc.chay_de_cuong([{"study": "a", "loai": "A12"}, {"study": "b", "loai": "A12"}], tmp_path,
                          lambda l, c, t: dem.append(l) or (2, "⛔ Vượt trần chi phí tháng — HetNganSach"))
    assert r["ket_qua"] == "loi" and "trần" in r["dung"] and len(dem) == 1


def test_duoi_pytest_khong_chay_cong_cu_de_cuong_that(tmp_path, akc):
    """★ RÀO TIỀN."""
    assert akc.chay_de_cuong([{"study": "a", "loai": "A12"}], tmp_path)["ket_qua"] == "bo_qua"


# ════════════════ CAFÉ-S khi agent an toàn đổi ════════════════

def _cafes(goc: Path, luc: str, sua_agent: bool = False, cong: str = "PASS") -> None:
    ag = goc / ".claude" / "agents"
    ag.mkdir(parents=True, exist_ok=True)
    for t in ("sang-loc-co-do", "ke-don-an-toan"):
        if not (ag / f"{t}.md").exists():
            (ag / f"{t}.md").write_text(f"bản {t}", encoding="utf-8", newline="\n")
    vt = {t: hashlib.sha256((ag / f"{t}.md").read_bytes()).hexdigest() for t in ("sang-loc-co-do", "ke-don-an-toan")}
    out = goc / "tools" / "eval" / "agent_outputs" / f"cafes_api_{luc[:10]}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "_ket_qua.json").write_text(json.dumps({"luc": luc, "van_tay_agent": vt, "bao_cao": {"CRITICAL_GATE": cong}}),
                                       encoding="utf-8", newline="\n")
    if sua_agent:
        (ag / "sang-loc-co-do.md").write_text("bản đã sửa", encoding="utf-8", newline="\n")


def test_cafes_chi_khi_agent_doi_va_du_khoang_cach(tmp_path, akc):
    cs = akc.doc_chinh_sach()
    assert akc.can_cafes(cs, tmp_path)[0] is None and "lượt đầu do bác sĩ" in akc.can_cafes(cs, tmp_path)[1]
    _cafes(tmp_path, "2026-11-17T14:00:00")
    assert akc.can_cafes(cs, tmp_path, dt.datetime(2026, 12, 30)) == (None, "")            # agent không đổi
    (tmp_path / ".claude" / "agents" / "sang-loc-co-do.md").write_text("đã sửa", encoding="utf-8", newline="\n")
    v, ly = akc.can_cafes(cs, tmp_path, dt.datetime(2026, 12, 1))
    assert v is None and "sớm nhất 17/12/2026" in ly                                       # chưa đủ 30 ngày
    v, _ = akc.can_cafes(cs, tmp_path, dt.datetime(2026, 12, 17, 15))
    assert v == {"agent_doi": ["sang-loc-co-do"], "luc_do_truoc": "2026-11-17T14:00:00"}


def test_chay_cafes_doc_cong_critical_cua_luot_moi(tmp_path, akc):
    _cafes(tmp_path, "2026-11-17T14:00:00", sua_agent=True)
    viec = {"agent_doi": ["sang-loc-co-do"], "luc_do_truoc": "2026-11-17T14:00:00"}
    r = akc.chay_cafes(viec, tmp_path, lambda l, c, t: (_cafes(tmp_path, "2026-12-18T09:00:00", cong="FAIL") or (0, "xong")))
    assert r["ket_qua"] == "ok" and r["critical_gate"] == "FAIL"
    r = akc.chay_cafes(viec | {"luc_do_truoc": "2026-12-18T09:00:00"}, tmp_path, lambda l, c, t: (2, "lỗi"))
    assert r["ket_qua"] == "loi"                                                          # không có lượt mới ⇒ lỗi


def test_duoi_pytest_khong_chay_cafes_that(tmp_path, akc):
    """★ RÀO TIỀN (~3 USD mỗi lượt)."""
    assert akc.chay_cafes({"agent_doi": [], "luc_do_truoc": "x"}, tmp_path)["ket_qua"] == "bo_qua"


# ════════════════ chính sách ════════════════

def test_chinh_sach_cua_repo_dung_lua_chon_cua_bac_si(akc):
    """★ Hợp đồng với lời duyệt 18/11: cả ba việc TỰ CHẠY; hội đồng cổng không nằm trong chính sách."""
    cs = akc.doc_chinh_sach(REPO / "sync" / "api-khi-can.json")
    assert cs is not None and cs["tu_chay"] == {"chu_de": True, "de_cuong": True, "cafes": True}
    assert "hoi_dong" not in json.loads((REPO / "sync" / "api-khi-can.json").read_text(encoding="utf-8"))["tu_chay"]


@pytest.mark.parametrize("noi_dung", [
    "{ hỏng", "[1]", '{"khong_co_tu_chay": 1}', '{"tu_chay": {"chu_de": "co"}}',
    '{"tu_chay": {}, "chu_de_toi_da_moi_luot": 0}', '{"tu_chay": {}, "nen_cach_gio_toi_thieu": true}',
])
def test_chinh_sach_hong_la_tat_han(tmp_path, akc, noi_dung):
    p = tmp_path / "cs.json"
    p.write_text(noi_dung, encoding="utf-8", newline="\n")
    assert akc.doc_chinh_sach(p) is None
    assert akc.doc_chinh_sach(tmp_path / "vang.json") is None


# ════════════════ điều phối · khoá · hook ════════════════

def test_chay_tron_luot_ghi_so_va_tat_theo_chinh_sach(tmp_path, akc, monkeypatch):
    monkeypatch.setattr(akc, "xet", lambda cs, chi, goc, goc_mea, bay_gio: {
        "chu_de": {"can": [{"tep": tmp_path / "WebDashboard_A_20261101.html", "so_muc": 1, "uoc_usd": 0}], "ghi_chu": "",
                   "do_duoc": True},
        "de_cuong": {"can": [], "ghi_chu": "repo y khoa chưa có duyet_kiem_may_api.py", "do_duoc": False},
        "cafes": {"can": [], "ghi_chu": "", "do_duoc": True}})
    akc.CHINH_SACH.write_text(json.dumps({"tu_chay": {"chu_de": True, "de_cuong": True, "cafes": False}}),
                              encoding="utf-8", newline="\n")
    ma = akc.chay(goc=tmp_path, goi_cong=lambda p: {"status": "ok", "off_topic": [], "uncertain": []},
                  bay_gio=dt.datetime(2026, 11, 18, 9))
    so = akc.doc_so()
    v = so["luot"][-1]["viec"]
    assert ma == 0 and so["lan_xet_cuoi"] == "2026-11-18T09:00:00"
    assert v["chu_de"]["da_cham"] == 1 and v["de_cuong"]["ket_qua"] == "khong_do_duoc" and v["cafes"]["ket_qua"] == "tat"
    assert not Path(str(akc.SO) + ".lock").exists()                                       # khoá đã trả


def test_chinh_sach_vang_thi_khong_chay_viec_nao(tmp_path, akc, monkeypatch):
    akc.CHINH_SACH.unlink()
    monkeypatch.setattr(akc, "xet", lambda *a, **k: pytest.fail("chính sách vắng mà vẫn xét/chạy"))
    assert akc.chay(goc=tmp_path) == 2


def test_luot_khac_dang_giu_khoa_thi_bo_qua_khoa_treo_thi_lay_lai(tmp_path, akc, monkeypatch):
    k = Path(str(akc.SO) + ".lock")
    k.write_text("123", encoding="utf-8")
    monkeypatch.setattr(akc, "xet", lambda *a, **kw: pytest.fail("đang có lượt khác mà vẫn chạy"))
    assert akc.chay(goc=tmp_path) == 0
    cu = (dt.datetime.now() - dt.timedelta(hours=akc.HAN_KHOA_GIO + 1)).timestamp()
    os.utime(k, (cu, cu))
    assert akc.lay_khoa() is True
    akc.tra_khoa()


def test_hook_duoi_pytest_khong_bao_gio_phong_nen(akc, monkeypatch):
    """★ RÀO TIỀN: hook gọi trong bộ kiểm không được phóng lượt nền thật."""
    monkeypatch.setattr(akc.subprocess, "Popen", lambda *a, **k: pytest.fail("đã phóng nền dưới pytest"))
    assert akc.phong_nen(im_khi_on=True) == 0


def test_hook_chi_phong_khi_du_gio_khong_cloud_khong_khoa(tmp_path, akc, monkeypatch):
    phong = []
    monkeypatch.setattr(akc, "_duoi_pytest", lambda: False)
    monkeypatch.setattr(akc.subprocess, "Popen", lambda lenh, **k: phong.append(lenh))
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    akc.ghi_so({"lan_xet_cuoi": "2026-11-18T08:00:00", "luot": []})
    akc.phong_nen(True, bay_gio=dt.datetime(2026, 11, 18, 12))          # mới 4 giờ < 6 giờ
    assert phong == []
    akc.phong_nen(True, bay_gio=dt.datetime(2026, 11, 18, 15))          # đủ 7 giờ
    assert len(phong) == 1 and phong[0][-1] == "--chay"
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    akc.phong_nen(True, bay_gio=dt.datetime(2026, 11, 19, 15))
    assert len(phong) == 1                                               # phiên Cloud: không phóng


def test_hook_da_khai_trong_nguon_git_va_hom_viec_van_cuoi(akc):
    d = json.loads((REPO / "sync" / "hooks-sessionstart.json").read_text(encoding="utf-8"))
    lenh = [h["command"] for g in d["SessionStart"] for h in g["hooks"]]
    vt = [i for i, c in enumerate(lenh) if "tools/api_khi_can.py --nen --im-khi-on" in c]
    assert len(vt) == 1 and "hom_viec_mot_cua" in lenh[-1]


def test_tac_vu_thang_goi_va_da_khai_quyen(akc):
    skill = (REPO / "sync" / "scheduled-tasks" / "cap-nhat-thang-ebm" / "SKILL.md").read_text(encoding="utf-8")
    quyen = json.loads((REPO / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))
    assert "`python3 tools/api_khi_can.py --chay`" in skill
    assert "python3 tools/api_khi_can.py --chay" in quyen["tac_vu"]["cap-nhat-thang-ebm"]["lenh"]


# ════════════════ giác quan hòm việc ════════════════

@pytest.fixture
def tdx(akc, monkeypatch):
    m = _nap("_tdx_akc", HERE / "tu_de_xuat_viec.py")
    monkeypatch.setattr(m, "_nap_api_khi_can", lambda: akc)
    m._GIAC_QUAN_CHET.clear()
    return m


def test_giac_quan_chinh_sach_hong_la_chet(tdx, akc):
    akc.CHINH_SACH.write_text("{ hỏng", encoding="utf-8")
    assert tdx.giac_quan_api_khi_can() == [] and "TẮT" in tdx._GIAC_QUAN_CHET[-1]


def test_giac_quan_chua_xet_lan_nao_la_chet(tdx):
    assert tdx.giac_quan_api_khi_can() == [] and "hook" in tdx._GIAC_QUAN_CHET[-1]


def test_giac_quan_luot_loi_bao_bac_si(tmp_path, tdx, akc):
    akc.ghi_so({"lan_xet_cuoi": "2026-11-18T09:00:00", "luot": [
        {"luc": "2026-11-18T09:00:00", "viec": {"chu_de": {"ket_qua": "loi", "dung": "dừng sau 3 lỗi liền", "so_loi": 3}}}]})
    (uu, ai, dong, lenh), = tdx.giac_quan_api_khi_can(tmp_path, bay_gio=dt.datetime(2026, 11, 18, 10))
    assert (uu, ai) == (2, "👤") and "3 lỗi liền" in dong and lenh.endswith("--chi chu_de")


def test_giac_quan_bao_cao_co_muc_nghi_lac_trong_14_ngay(tmp_path, tdx, akc):
    akc.ghi_so({"lan_xet_cuoi": "2026-11-18T09:00:00", "luot": []})
    akc.ghi_bao_cao_chu_de([{"tep": "WebDashboard_A_20261101.html", "chu_de": "THA", "so_muc": 3, "status": "ok",
                             "off_topic": [{"id": "ITEM-02", "title": "Thai kỳ", "reason": "sản"}], "uncertain": [],
                             "ly_do": ""}], tmp_path, luc=dt.datetime(2026, 11, 18, 9))
    (uu, ai, dong, lenh), = tdx.giac_quan_api_khi_can(tmp_path, bay_gio=dt.datetime(2026, 11, 20))
    assert (uu, ai) == (2, "👤") and "1 mục NGHI LẠC" in dong and "KIEM-CHU-DE-KHI-CAN_20261118-0900.md" in lenh
    assert tdx.giac_quan_api_khi_can(tmp_path, bay_gio=dt.datetime(2026, 12, 10)) == []    # quá 14 ngày


def test_giac_quan_lau_khong_xet_la_chet(tmp_path, tdx, akc):
    akc.ghi_so({"lan_xet_cuoi": "2026-11-01T09:00:00", "luot": []})
    truoc = len(tdx._GIAC_QUAN_CHET)
    assert tdx.giac_quan_api_khi_can(tmp_path, bay_gio=dt.datetime(2026, 11, 18)) == []
    assert len(tdx._GIAC_QUAN_CHET) == truoc + 1 and "16 ngày" in tdx._GIAC_QUAN_CHET[-1]
