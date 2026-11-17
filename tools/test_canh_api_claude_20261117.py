#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt cho cảnh báo SỨC KHOẺ API CLAUDE (17/11/2026, bác sĩ: «khi API hết hạn báo lại tôi»).

Khoá Anthropic không hết hạn theo ngày — nó chết vì hết TÍN DỤNG, bị THU HỒI (401) hay vượt HẠN MỨC (429), và chỉ lộ đúng lúc gọi.
Thăm dò định kỳ là tốn tiền vô ích, nên ta GHI LẠI kết quả những lượt gọi dây chuyền vốn đã thực hiện rồi để hòm việc đọc.
Mọi chốt ở đây ngoại tuyến tuyệt đối: không chạm kho khoá thật, không gọi mạng."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


CTR_PATH = HERE.parent / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "check_topic_relevance.py"
pytestmark = pytest.mark.skipif(not CTR_PATH.exists(), reason="⚪ không có check_topic_relevance.py ở cây này")


# ─────────────────── ghi nhật ký ───────────────────

@pytest.mark.parametrize("trang_thai", ["ok", "skipped", "error"])
def test_moi_nhanh_deu_duoc_ghi(tmp_path, trang_thai):
    """★ Vỏ bọc phải ghi CẢ BA nhánh — nhánh nào lọt thì hòm việc mù đúng lúc cần biết nhất."""
    ctr = _nap(f"_ctr_ghi_{trang_thai}", CTR_PATH)
    tep = tmp_path / "nk.json"
    ctr.NHAT_KY_API = str(tep)
    ctr._cham_chu_de = lambda _p: {"status": trang_thai, "message": "thông điệp thử", "total_items": 7}
    kq = ctr.check_dashboard_topic_relevance("khong-quan-trong.html")
    assert kq["status"] == trang_thai                      # hành vi trả về KHÔNG đổi
    d = json.loads(tep.read_text(encoding="utf-8"))
    assert d["trang_thai"] == trang_thai and d["so_muc"] == 7 and d["luc"]


def test_nhat_ky_khong_bao_gio_chua_khoa(tmp_path):
    """★ Nhật ký nằm ngoài repo nhưng vẫn không được mang giá trị khoá — chỉ trạng thái và lý do."""
    ctr = _nap("_ctr_bimat", CTR_PATH)
    tep = tmp_path / "nk.json"
    ctr.ghi_nhat_ky_api({"status": "error", "message": "AuthenticationError: 401 Invalid bearer token"}, str(tep))
    noi_dung = tep.read_text(encoding="utf-8")
    assert "sk-ant" not in noi_dung
    assert set(json.loads(noi_dung)) == {"luc", "trang_thai", "ly_do", "so_muc"}


def test_ghi_that_bai_khong_lam_hong_luot_xuat_goi(tmp_path):
    """★ Nhật ký hỏng KHÔNG được làm vỡ dây chuyền xuất gói của bác sĩ."""
    ctr = _nap("_ctr_hong", CTR_PATH)
    ctr.ghi_nhat_ky_api({"status": "ok"}, str(tmp_path / "khong" / "co" / "thu-muc" / "nk.json"))  # không được ném


# ─────────────────── giác quan ───────────────────

@pytest.fixture
def tdx():
    return _nap("_tdx_api", HERE / "tu_de_xuat_viec.py")


def _ghi(tmp_path, **kw) -> Path:
    tep = tmp_path / "nk.json"
    tep.write_text(json.dumps({"luc": "2026-11-17T08:30:00", "trang_thai": "ok", "ly_do": "", "so_muc": 3, **kw}),
                   encoding="utf-8")
    return tep


def test_luot_loi_bao_uu_tien_1_cho_bac_si(tmp_path, tdx):
    """★ Khoá chết ⇒ luật kiểm lạc chủ đề ngừng chạy ⇒ phải nổi lên ngay, thuộc thẩm quyền bác sĩ."""
    tep = _ghi(tmp_path, trang_thai="error", ly_do="AuthenticationError: Error code: 401 - Invalid bearer token")
    viec = tdx.giac_quan_api_claude(tep)
    assert len(viec) == 1
    uu, ai, dong, _lenh = viec[0]
    assert uu == 1 and ai == "👤"
    assert "401" in dong and "console.anthropic.com" in dong


def test_thieu_khoa_bao_uu_tien_2(tmp_path, tdx):
    tep = _ghi(tmp_path, trang_thai="skipped", ly_do="Thiếu ANTHROPIC_API_KEY — đặt trong biến môi trường…")
    viec = tdx.giac_quan_api_claude(tep)
    assert len(viec) == 1 and viec[0][0] == 2 and viec[0][1] == "👤"


def test_luot_ok_thi_im(tmp_path, tdx):
    assert tdx.giac_quan_api_claude(_ghi(tmp_path)) == []


def test_skipped_vi_khong_co_item_khong_phai_loi_khoa(tmp_path, tdx):
    """«Không có item nào để chấm» cũng là skipped nhưng KHÔNG phải chuyện khoá — không được báo oan."""
    tep = _ghi(tmp_path, trang_thai="skipped", ly_do="Không có item nào để chấm.")
    assert tdx.giac_quan_api_claude(tep) == []


def test_chua_co_luot_nao_la_chua_do_duoc_chu_khong_phai_api_tot(tmp_path, tdx):
    """★ Vắng nhật ký ⇒ ⚪ «chưa đo được», TUYỆT ĐỐI không đọc thành «API vẫn tốt»."""
    truoc = len(tdx._GIAC_QUAN_CHET)
    viec = tdx.giac_quan_api_claude(tmp_path / "khong-ton-tai.json")
    assert viec == []
    # KHÔNG rào assertion sau `hasattr`: bản trước làm thế, tên sổ sai nên chốt không kiểm gì
    # và đột biến «bỏ _ghi_chet» LỌT. Phải khẳng định thẳng là đã ghi một dòng ⚪.
    assert len(tdx._GIAC_QUAN_CHET) == truoc + 1
    assert "sức khoẻ API Claude" in tdx._GIAC_QUAN_CHET[-1]


def test_nhat_ky_hong_khong_doc_thanh_tot(tmp_path, tdx):
    tep = tmp_path / "nk.json"
    tep.write_text("{ hỏng", encoding="utf-8")
    truoc = len(tdx._GIAC_QUAN_CHET)
    assert tdx.giac_quan_api_claude(tep) == []
    assert len(tdx._GIAC_QUAN_CHET) == truoc + 1      # hỏng cũng phải thành ⚪, không im


def test_luot_loi_cua_cong_cu_nghien_cuu_bao_dung_cong_cu(tmp_path, tdx):
    """17/11: công cụ repo y khoa ghi «nguon» ⇒ thông báo + lệnh trỏ đúng công cụ, không đổ cho kiểm lạc chủ đề."""
    tep = _ghi(tmp_path, trang_thai="error", ly_do="Gọi API thất bại: RateLimitError: 429", nguon="hoi_dong_cong_batch")
    uu, ai, dong, lenh = tdx.giac_quan_api_claude(tep)[0]
    assert uu == 1 and "hội đồng cổng qua Batch API" in dong and "hoi_dong_cong_batch.py" in lenh
    tep = _ghi(tmp_path, trang_thai="error", ly_do="401")
    assert "kiểm lạc chủ đề" in tdx.giac_quan_api_claude(tep)[0][2]
