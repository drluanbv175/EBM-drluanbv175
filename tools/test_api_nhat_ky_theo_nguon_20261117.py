#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt cho HAI lỗ hổng kết nối API Claude (17/11/2026, bác sĩ duyệt «làm cả 2 mục»).

MỤC 1 — cổng kiểm lạc chủ đề TẮT CÂM khi chạy bằng `python3` mặc định. Dây chuyền xuất gói được gọi bằng
`python3 tools/xuat_goi_cap_nhat.py …` (skill, tác vụ lịch goi-duyet-tuan-ebm, CLAUDE.md); `python3` của máy bác sĩ
KHÔNG có SDK `anthropic`, chỉ ~/.ebm-venv có. Đo thật trên VKDT_TamThanKinh: «skipped — Chưa cài SDK», hòm việc im.
Vá: thiếu SDK ⇒ chấm bằng Python của venv (tiến trình con); giác quan báo 🤖 khi lượt nào bị bỏ qua vì thiếu SDK.

MỤC 2 — nhật ký sức khoẻ chỉ giữ MỘT lượt: 8 công cụ ghi chung một ô, công cụ A lỗi rồi công cụ B chạy ổn ngay sau thì
lỗi của A biến mất. Vá: khoá «theo_nguon» giữ lượt gần nhất của TỪNG công cụ; giác quan xét từng công cụ.

Mọi chốt NGOẠI TUYẾN tuyệt đối: không đọc kho khoá thật, không ghi nhật ký thật, không gọi API (chỉ một chốt chạy tiến
trình con THẬT bằng chính trình Python đang chạy, trên dashboard KHÔNG có mục ⇒ dừng trước bước đọc khoá)."""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
CTR_PATH = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "check_topic_relevance.py"
NK_PATH = HERE / "nhat_ky_api_claude.py"
TDX_PATH = HERE / "tu_de_xuat_viec.py"
# Cầu nối repo y khoa — chỉ có trên máy thật (CI repo gốc không có) ⇒ chốt đối chiếu khuôn tự bỏ qua ở đó.
CAU_NOI_Y_KHOA = HERE.parent / "medical-ebm-automation" / "tools" / "api_claude_nc.py"


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


@pytest.fixture
def ctr(tmp_path):
    m = _nap(f"_ctr_tn_{tmp_path.name}", CTR_PATH)
    m.NHAT_KY_API = str(tmp_path / "nk.json")
    return m


@pytest.fixture
def nk():
    return _nap("_nk_tn", NK_PATH)


@pytest.fixture
def tdx():
    return _nap("_tdx_tn", TDX_PATH)


def _doc(tep: Path) -> dict:
    return json.loads(tep.read_text(encoding="utf-8"))


def _nhat_ky(tmp_path: Path, **theo_nguon: dict) -> Path:
    """Nhật ký khuôn mới: mỗi khoá là một công cụ → lượt gần nhất của nó."""
    tep = tmp_path / "nk.json"
    moi_nhat = max(theo_nguon.items(), key=lambda x: x[1]["luc"])
    tep.write_text(json.dumps({**moi_nhat[1], "nguon": moi_nhat[0], "theo_nguon": theo_nguon}, ensure_ascii=False),
                   encoding="utf-8", newline="\n")
    return tep


def _luot(luc: str, trang_thai: str = "ok", ly_do: str = "", so_muc: int = 3) -> dict:
    return {"luc": luc, "trang_thai": trang_thai, "ly_do": ly_do, "so_muc": so_muc}


_BAY_GIO = dt.datetime(2026, 11, 18, 9, 0, 0)


# ════════════════════════ MỤC 2 — ghi theo từng công cụ ════════════════════════

def test_loi_cua_cong_cu_a_khong_bi_luot_ok_cua_b_xoa(tmp_path, ctr, nk, tdx):
    """★ ĐÚNG KỊCH BẢN LỖ HỔNG: quét toàn kho lỗi 401, ngay sau đó cổng kiểm chủ đề chạy ổn — bản cũ xoá mất lỗi."""
    tep = tmp_path / "nk.json"
    nk.ghi("error", "AuthenticationError: 401 invalid x-api-key", 0, "quet_lac_chu_de_kho", tep=str(tep))
    ctr.ghi_nhat_ky_api({"status": "ok", "total_items": 12}, str(tep))
    d = _doc(tep)
    assert (d["trang_thai"], d["nguon"]) == ("ok", "check_topic_relevance")          # cấp cao = lượt gần nhất
    assert d["theo_nguon"]["quet_lac_chu_de_kho"]["trang_thai"] == "error"           # lỗi của A CÒN NGUYÊN
    viec = tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO)
    assert len(viec) == 1 and "quét lạc chủ đề toàn kho" in viec[0][2] and "401" in viec[0][2]


def test_nhat_ky_kieu_cu_duoc_giu_lam_muc_cua_nguon_cu(tmp_path, nk):
    """Máy đang có nhật ký MỘT lượt (khuôn cũ) — lượt đó không được mất khi công cụ khác ghi đè."""
    tep = tmp_path / "nk.json"
    tep.write_text(json.dumps({**_luot("2026-11-17T10:00:00", "error", "429"), "nguon": "hoi_dong_cong_batch"}),
                   encoding="utf-8", newline="\n")
    nk.ghi("ok", "", 32, "cafes_suite", tep=str(tep))
    d = _doc(tep)
    assert set(d["theo_nguon"]) == {"hoi_dong_cong_batch", "cafes_suite"}
    assert d["theo_nguon"]["hoi_dong_cong_batch"] == _luot("2026-11-17T10:00:00", "error", "429")


def test_cong_kiem_chu_de_bo_ten_cu_rong_cua_chinh_no(tmp_path, ctr):
    """Bản cũ của cổng không ghi «nguon» (= «»). Ghi bằng tên mới thì lượt tên cũ phải đi — không nằm lại mãi."""
    tep = tmp_path / "nk.json"
    tep.write_text(json.dumps(_luot("2026-11-17T10:00:00", "error", "401")), encoding="utf-8", newline="\n")
    ctr.ghi_nhat_ky_api({"status": "ok", "total_items": 5}, str(tep))
    assert set(_doc(tep)["theo_nguon"]) == {"check_topic_relevance"}


def test_nhat_ky_hong_thi_ghi_lai_tu_dau_khong_nem(tmp_path, ctr, nk):
    tep = tmp_path / "nk.json"
    tep.write_text("{ hỏng", encoding="utf-8", newline="\n")
    nk.ghi("ok", "", 1, "cafes_suite", tep=str(tep))
    assert set(_doc(tep)["theo_nguon"]) == {"cafes_suite"}
    tep.write_text("[1, 2]", encoding="utf-8", newline="\n")                       # JSON hợp lệ nhưng không phải object
    ctr.ghi_nhat_ky_api({"status": "ok"}, str(tep))
    assert set(_doc(tep)["theo_nguon"]) == {"check_topic_relevance"}


def test_ghi_nguyen_tu_khong_de_lai_tep_tam(tmp_path, ctr, nk):
    tep = tmp_path / "nk.json"
    nk.ghi("ok", "", 1, "cafes_suite", tep=str(tep))
    ctr.ghi_nhat_ky_api({"status": "error", "message": "x"}, str(tep))
    assert sorted(p.name for p in tmp_path.iterdir()) == ["nk.json"]


def test_hai_noi_ghi_cua_repo_goc_tron_cung_mot_khuon(tmp_path, ctr, nk):
    """Khuôn trộn có ở BA nơi ghi — hai nơi trong repo này phải cho CÙNG kết quả trên cùng đầu vào."""
    cu = {**_luot("2026-11-17T09:00:00", "error", "401"), "nguon": "phan_bien_may_de_cuong"}
    moi = {**_luot("2026-11-17T10:00:00"), "nguon": "cafes_suite"}
    tep = tmp_path / "nk.json"
    tep.write_text(json.dumps(cu), encoding="utf-8", newline="\n")
    assert ctr._gop_theo_nguon(str(tep), moi) == nk.gop_theo_nguon(str(tep), moi)


@pytest.mark.skipif(not CAU_NOI_Y_KHOA.exists(), reason="⚪ không có repo y khoa cạnh repo gốc (CI/Cloud một repo)")
def test_cau_noi_y_khoa_tron_cung_khuon(tmp_path, nk):
    """Nơi ghi thứ ba (cầu nối repo y khoa) — chỉ đối chiếu được khi hai repo nằm cạnh nhau (máy thật)."""
    api = _nap("_api_nc_tn", CAU_NOI_Y_KHOA)
    if not hasattr(api, "gop_theo_nguon"):
        pytest.skip("⚪ cầu nối y khoa ở cây này chưa có khuôn theo nguồn (PR y khoa chưa gộp)")
    cu = {**_luot("2026-11-17T09:00:00", "error", "401"), "nguon": "quet_lac_chu_de_kho"}
    moi = {**_luot("2026-11-17T10:00:00"), "nguon": "kiem_noi_dung_trich_dan"}
    tep = tmp_path / "nk.json"
    tep.write_text(json.dumps(cu), encoding="utf-8", newline="\n")
    assert api.gop_theo_nguon(str(tep), moi) == nk.gop_theo_nguon(str(tep), moi)


# ════════════════════════ MỤC 2 — giác quan xét từng công cụ ════════════════════════

def test_loi_chua_ai_goi_duoc_sau_do_la_uu_tien_1(tmp_path, tdx):
    tep = _nhat_ky(tmp_path, check_topic_relevance=_luot("2026-11-17T09:00:00"),
                   quet_lac_chu_de_kho=_luot("2026-11-17T11:00:00", "error", "401 authentication_error"))
    viec = tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO)
    assert len(viec) == 1
    uu, ai, dong, lenh = viec[0]
    assert (uu, ai) == (1, "👤") and "console.anthropic.com" in dong and "quet_lac_chu_de_kho.py" in lenh


def test_loi_ma_cong_cu_khac_goi_duoc_sau_do_la_uu_tien_2(tmp_path, tdx):
    """Khoá còn sống (công cụ khác gọi được SAU lỗi) ⇒ không hô «khoá chết», nhưng VẪN nêu lỗi của công cụ."""
    tep = _nhat_ky(tmp_path, quet_lac_chu_de_kho=_luot("2026-11-17T09:00:00", "error", "529 overloaded"),
                   check_topic_relevance=_luot("2026-11-17T11:00:00"))
    viec = tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO)
    assert len(viec) == 1
    uu, ai, dong, _lenh = viec[0]
    assert (uu, ai) == (2, "👤") and "khoá còn sống" in dong and "529" in dong
    assert "console.anthropic.com" not in dong


def test_hai_cong_cu_cung_loi_gop_mot_dong(tmp_path, tdx):
    tep = _nhat_ky(tmp_path, cafes_suite=_luot("2026-11-17T10:00:00", "error", "401"),
                   hoi_dong_cong_batch=_luot("2026-11-17T11:00:00", "error", "401"))
    viec = tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO)
    assert len(viec) == 1 and viec[0][0] == 1
    assert "2 công cụ" in viec[0][2] and "CAFÉ-S" in viec[0][2] and "hội đồng cổng" in viec[0][2]
    assert "hoi_dong_cong_batch.py" in viec[0][3]                       # lệnh của lượt lỗi MỚI NHẤT


def test_thieu_khoa_ma_sau_do_da_goi_duoc_thi_im(tmp_path, tdx):
    """Khoá đã được nạp (công cụ khác gọi được sau) ⇒ không báo «TẮT vì chưa có khoá» sai sự thật."""
    tep = _nhat_ky(tmp_path, check_topic_relevance=_luot("2026-11-17T09:00:00", "skipped", "Thiếu ANTHROPIC_API_KEY"),
                   kiem_noi_dung_trich_dan=_luot("2026-11-17T10:00:00"))
    assert tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO) == []


def test_thieu_khoa_chua_ai_goi_duoc_van_bao(tmp_path, tdx):
    tep = _nhat_ky(tmp_path, kiem_noi_dung_trich_dan=_luot("2026-11-17T09:00:00"),
                   check_topic_relevance=_luot("2026-11-17T10:00:00", "skipped", "Thiếu ANTHROPIC_API_KEY — đặt…"))
    viec = tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO)
    assert len(viec) == 1 and viec[0][:2] == (2, "👤") and "chưa có khoá" in viec[0][2]


def test_tuoi_tinh_theo_luot_moi_nhat_cua_moi_cong_cu(tmp_path, tdx):
    """Một công cụ lâu không chạy KHÔNG làm cả giác quan ⚪ khi công cụ khác vừa gọi được."""
    tep = _nhat_ky(tmp_path, cafes_suite=_luot("2026-09-01T09:00:00"), check_topic_relevance=_luot("2026-11-17T09:00:00"))
    truoc = len(tdx._GIAC_QUAN_CHET)
    assert tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO) == []
    assert len(tdx._GIAC_QUAN_CHET) == truoc
    tep = _nhat_ky(tmp_path, cafes_suite=_luot("2026-09-01T09:00:00"), check_topic_relevance=_luot("2026-10-01T09:00:00"))
    assert tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO) == []
    assert len(tdx._GIAC_QUAN_CHET) == truoc + 1 and "48 ngày" in tdx._GIAC_QUAN_CHET[-1]


def test_ten_cu_rong_bi_bo_khi_cong_da_ghi_ten_moi(tmp_path, tdx):
    tep = _nhat_ky(tmp_path, **{"": _luot("2026-11-10T09:00:00", "error", "401"),
                                "check_topic_relevance": _luot("2026-11-17T09:00:00")})
    assert tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO) == []


def test_nguon_la_neu_dung_ten_khong_do_cho_cong_kiem_chu_de(tmp_path, tdx):
    tep = _nhat_ky(tmp_path, cong_cu_moi=_luot("2026-11-17T09:00:00", "error", "401"))
    dong = tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO)[0][2]
    assert "«cong_cu_moi»" in dong and "kiểm lạc chủ đề" not in dong.split("—")[0]


def test_theo_nguon_rong_la_chua_do_duoc(tmp_path, tdx):
    tep = tmp_path / "nk.json"
    tep.write_text(json.dumps({"luc": "2026-11-17T09:00:00", "trang_thai": "ok", "theo_nguon": {"x": "không phải dict"}}),
                   encoding="utf-8", newline="\n")
    truoc = len(tdx._GIAC_QUAN_CHET)
    assert tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO) == []
    assert len(tdx._GIAC_QUAN_CHET) == truoc + 1


# ════════════════════════ MỤC 1 — thiếu SDK ════════════════════════

@pytest.mark.parametrize("trang_thai, ly_do, nguon", [
    ("skipped", "Chưa cài SDK `anthropic` trong trình Python /usr/local/bin/python3 — cài bằng …", "check_topic_relevance"),
    ("error", "Chưa cài SDK: `~/.ebm-venv/bin/pip install anthropic`.", "kiem_noi_dung_trich_dan"),
])
def test_thieu_sdk_bao_may_lam_khong_do_cho_khoa(tmp_path, tdx, trang_thai, ly_do, nguon):
    """★ Lượt «bỏ qua — Chưa cài SDK» trước đây IM LẶNG (giác quan chỉ báo skipped khi lý do nhắc tên khoá). Cầu nối
    y khoa ghi thiếu SDK là «error» ⇒ trước đây bị đọc thành khoá/tín dụng hỏng — sai hướng sửa."""
    tep = _nhat_ky(tmp_path, **{nguon: _luot("2026-11-17T09:00:00", trang_thai, ly_do)})
    viec = tdx.giac_quan_api_claude(tep, bay_gio=_BAY_GIO)
    assert len(viec) == 1
    uu, ai, dong, lenh = viec[0]
    assert (uu, ai) == (2, "🤖") and "thiếu SDK" in dong and "pip install anthropic" in lenh
    assert "console.anthropic.com" not in dong


def test_thong_diep_thieu_sdk_neu_dung_trinh_python(ctr, monkeypatch):
    """Thông điệp phải nói RÕ trình Python nào thiếu SDK — «pip install anthropic» trơn từng cài nhầm chỗ."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "khoa-gia-chi-de-qua-buoc-kiem-khoa")
    monkeypatch.setitem(sys.modules, "anthropic", None)          # giả lập trình Python thiếu SDK (như CI)
    with pytest.raises(ctr.TopicCheckError) as exc:
        ctr.call_claude("x")
    assert "cài SDK" in str(exc.value) and sys.executable in str(exc.value)


def _vao_nhanh_venv(ctr, monkeypatch, py: str = "/gia/.ebm-venv/bin/python"):
    """Đặt điều kiện «trình hiện tại thiếu SDK, venv có Python, không phải pytest» — MỌI đường gọi thật bị chặn."""
    monkeypatch.setattr(ctr, "_co_sdk", lambda: False)
    monkeypatch.setattr(ctr, "_duoi_pytest", lambda: False)
    monkeypatch.setattr(ctr, "_dang_trong_venv", lambda: False)
    monkeypatch.setattr(ctr, "_python_venv", lambda: py)
    monkeypatch.delenv(ctr.CO_QUA_VENV, raising=False)

    def _khong_duoc_cham_tai_cho(_p):
        raise AssertionError("đã chuyển tiếp sang venv thì KHÔNG chấm tại chỗ")
    monkeypatch.setattr(ctr, "_cham_chu_de", _khong_duoc_cham_tai_cho)


def test_thieu_sdk_cham_bang_python_cua_venv(tmp_path, ctr, monkeypatch):
    """★ MỤC 1: trình hiện tại thiếu SDK ⇒ chấm bằng Python của ~/.ebm-venv, trả đúng kết quả và GHI nhật ký."""
    _vao_nhanh_venv(ctr, monkeypatch)
    goi = {}

    def _chay_gia(args, **kw):
        goi["args"], goi["env"] = args, kw["env"]
        kq = {"status": "ok", "topic": "Chủ đề", "total_items": 3, "off_topic": [], "uncertain": ["ITEM-2"],
              "verdicts": {}}
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(kq, ensure_ascii=False), stderr="")
    monkeypatch.setattr(ctr.subprocess, "run", _chay_gia)
    html = tmp_path / "db.html"
    kq = ctr.check_dashboard_topic_relevance(str(html))
    assert kq["status"] == "ok" and kq["uncertain"] == ["ITEM-2"] and kq["qua_venv"] == "/gia/.ebm-venv/bin/python"
    assert goi["args"] == ["/gia/.ebm-venv/bin/python", os.path.abspath(ctr.__file__), os.path.abspath(str(html)), "--json"]
    assert goi["env"][ctr.CO_QUA_VENV] == "1" and goi["env"]["PYTHONIOENCODING"] == "utf-8"
    d = _doc(Path(ctr.NHAT_KY_API))
    assert (d["trang_thai"], d["so_muc"], d["nguon"]) == ("ok", 3, "check_topic_relevance")


def test_co_sdk_thi_cham_tai_cho_khong_chuyen_tiep(tmp_path, ctr, monkeypatch):
    monkeypatch.setattr(ctr, "_co_sdk", lambda: True)

    def _cam(_p):
        raise AssertionError("có SDK thì không được chuyển tiếp")
    monkeypatch.setattr(ctr, "_cham_qua_venv", _cam)
    monkeypatch.setattr(ctr, "_cham_chu_de", lambda _p: {"status": "skipped", "message": "Không có item nào để chấm."})
    assert ctr.check_dashboard_topic_relevance("x.html")["status"] == "skipped"


def test_duoi_pytest_khong_bao_gio_chuyen_tiep(ctr, monkeypatch):
    """★ RÀO TIỀN: venv máy bác sĩ có SDK + kho khoá thật ⇒ chuyển tiếp dưới pytest = gọi API THẬT. Không vá rào."""
    monkeypatch.delenv("EBM_KIEM_API_THAT", raising=False)
    monkeypatch.delenv(ctr.CO_QUA_VENV, raising=False)
    monkeypatch.setattr(ctr, "_dang_trong_venv", lambda: False)
    monkeypatch.setattr(ctr, "_python_venv", lambda: sys.executable)

    def _cam(*_a, **_k):
        raise AssertionError("dưới pytest KHÔNG được chạy tiến trình con chấm thật")
    monkeypatch.setattr(ctr.subprocess, "run", _cam)
    assert ctr._cham_qua_venv("x.html") is None


def test_tien_trinh_con_khong_chuyen_tiep_lan_nua(ctr, monkeypatch):
    _vao_nhanh_venv(ctr, monkeypatch)
    monkeypatch.setenv(ctr.CO_QUA_VENV, "1")
    assert ctr._cham_qua_venv("x.html") is None


def test_dang_o_venv_hoac_khong_co_venv_thi_khong_chuyen_tiep(tmp_path, ctr, monkeypatch):
    _vao_nhanh_venv(ctr, monkeypatch)
    monkeypatch.setattr(ctr, "_dang_trong_venv", lambda: True)
    assert ctr._cham_qua_venv("x.html") is None
    monkeypatch.setattr(ctr, "_dang_trong_venv", lambda: False)
    monkeypatch.setattr(ctr, "_python_venv", lambda: None)
    assert ctr._cham_qua_venv("x.html") is None


def test_nhan_dien_venv_theo_thu_muc_khong_theo_tep_thuc_thi(tmp_path, ctr, monkeypatch):
    """Python của venv thường là symlink tới `python3` hệ thống — phải so sys.prefix, không so realpath tệp chạy."""
    monkeypatch.setattr(ctr, "THU_MUC_VENV", sys.prefix)
    assert ctr._dang_trong_venv() is True
    monkeypatch.setattr(ctr, "THU_MUC_VENV", str(tmp_path / "venv-khac"))
    assert ctr._dang_trong_venv() is False


def test_tim_python_venv_ca_mac_lan_windows(tmp_path, ctr, monkeypatch):
    monkeypatch.setattr(ctr, "THU_MUC_VENV", str(tmp_path))
    assert ctr._python_venv() is None
    (tmp_path / "Scripts").mkdir()
    (tmp_path / "Scripts" / "python.exe").write_bytes(b"")
    assert ctr._python_venv() == str(tmp_path / "Scripts" / "python.exe")
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "python").write_bytes(b"")
    assert ctr._python_venv() == str(tmp_path / "bin" / "python")


@pytest.mark.parametrize("hong", ["rac", "qua_gio", "loi_os"])
def test_tien_trinh_con_hong_thanh_error_khong_im_lang(tmp_path, ctr, monkeypatch, hong):
    """Đường vòng hỏng ⇒ «error» (hòm việc báo), KHÔNG BAO GIỜ im lặng thành «skipped»."""
    _vao_nhanh_venv(ctr, monkeypatch)

    def _chay_gia(args, **kw):
        if hong == "qua_gio":
            raise subprocess.TimeoutExpired(args, kw.get("timeout"))
        if hong == "loi_os":
            raise OSError("không chạy được")
        return subprocess.CompletedProcess(args, 1, stdout="Traceback … ModuleNotFoundError", stderr="")
    monkeypatch.setattr(ctr.subprocess, "run", _chay_gia)
    kq = ctr.check_dashboard_topic_relevance(str(tmp_path / "db.html"))
    assert kq["status"] == "error" and "/gia/.ebm-venv/bin/python" in kq["message"]
    assert _doc(Path(ctr.NHAT_KY_API))["trang_thai"] == "error"


def test_tien_trinh_con_that_tra_json_doc_duoc(tmp_path, ctr, monkeypatch):
    """Đi trọn đường THẬT (subprocess + `--json` + UTF-8) bằng chính trình Python đang chạy, trên dashboard KHÔNG có mục ⇒
    tiến trình con dừng ở «Không có item» TRƯỚC bước đọc khoá: không đọc kho khoá, không gọi API, không tốn tiền.
    Tiến trình con kế thừa PYTEST_CURRENT_TEST ⇒ rào BH181 chặn nó ghi nhật ký thật."""
    _vao_nhanh_venv(ctr, monkeypatch, py=sys.executable)
    html = tmp_path / "db.html"
    html.write_text("""<html><script>const DATA = {
  meta: { question: 'Chủ đề thử — tiếng Việt có dấu' },
  items: [],
  summary: { conclusion: 'x', doNow: [], dontDo: [], redFlags: [] }
};</script></html>""", encoding="utf-8", newline="\n")
    kq = ctr._cham_qua_venv(str(html))
    assert kq is not None and kq["status"] == "skipped" and "Không có item" in kq["message"]
    assert kq["qua_venv"] == sys.executable
