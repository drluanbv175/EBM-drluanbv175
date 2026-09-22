"""Cửa vào mù dấu + năng lực mới chưa có cửa vào (T3-01/T3-05, khảo sát điều phối 20/09/2026)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from orchestrator.intent import route  # noqa: E402

CA_KHONG_DAU = [
    "benh nhan nam 60 tuoi dau nguc 2 gio",
    "be trai 8 tuoi kho tho ve dem",
    "phu nu mang thai 32 tuan dau dau du doi",
    "cu ong 78 tuoi ngat 1 lan",
    "toi co bn nu 55 tuoi sot cao",
]


@pytest.mark.parametrize("cau", CA_KHONG_DAU)
def test_ca_lam_sang_go_khong_dau_khong_con_roi_unknown(cau):
    r = route(cau)
    assert r.kind == "clinical_case" and r.target == "dieu-phoi-lam-sang", (cau, r)


def test_de_tai_va_viec_le_khong_dau():
    assert route("de tai hieu qua metformin o benh nhan PCOS").kind == "research_topic"
    r = route("tinh co mau cho nghien cuu cat ngang")
    assert (r.kind, r.target) == ("single_task", "co-mau-nghien-cuu"), "việc lẻ mạnh phải thắng cue đề tài cả khi không dấu"


def test_bat_doi_xung_an_toan_van_giu_khi_khong_dau():
    """Cờ đỏ / ca cụ thể LUÔN thắng cue đề tài và việc lẻ — over-route sang nơi có sàng lọc cờ đỏ (BH88)."""
    assert route("benh nhan ngung tim, chay protocol hoi suc the nao, can chuyen cap cuu ngay").kind == "clinical_case"
    assert route("benh nhan nam 62 tuoi dau nguc, tinh co mau giup toi").kind == "clinical_case"


def test_cau_co_dau_van_dung_bang_cu_khong_khop_nham_nam_voi_nam():
    """«năm,» (năm) không được khớp cue «nam,» (nam giới) — lý do bảng có dấu vẫn được giữ cho câu có dấu."""
    assert route("Trong năm, tôi muốn xem tài liệu").kind != "clinical_case"


@pytest.mark.parametrize("cau,kind,dich", [
    ("Tra biệt dược Coversyl là hoạt chất gì", "single_task", "ke-don-an-toan"),
    ("Thông báo rút bài của guideline này là gì", "single_task", "kiem-chung-trich-dan"),
    ("Chủ đề nào cũ nhất cần làm mới chứng cứ", "cong_cu", "ops/orchestrator.py"),
    ("Độ tươi thang điểm còn hiệu lực không", "cong_cu", "medical-ebm-automation/tools/kiem_do_tuoi_thang_diem.py"),
    ("Lịch nền tuần này có chạy không", "cong_cu", "tools/kiem_lich_nen.py"),
])
def test_nang_luc_moi_co_cua_vao(cau, kind, dich):
    r = route(cau)
    assert (r.kind, r.target) == (kind, dich), (cau, r)


def test_cau_ngoai_pham_vi_van_unknown():
    assert route("xin chao").kind == "unknown"
    assert route("hello there").kind == "unknown"


# ── phản biện đối kháng 20/09/2026 (L1–L5, L11) ─────────────────────────────────────────────────────
def test_L1_cau_ca_nhac_ten_thuoc_khong_mat_buoc_0():
    """Nhắc «biệt dược»/«hoạt chất» trong câu mô tả ca KHÔNG được chuyển unknown (có BƯỚC 0) thành single_task."""
    for cau in ["Bà 70 tuổi uống biệt dược Coversyl, nay khó thở, phù mặt",
                "Cô ấy nổi mề đay, sưng môi sau khi dùng thuốc chứa hoạt chất amoxicillin"]:
        assert route(cau).kind != "single_task", cau


@pytest.mark.parametrize("cau", [
    "Tre 4 tuoi tieu phan co mau, quay khoc",          # «có máu» ≠ «cỡ mẫu»
    "Dau mang phoi khi tho sau, kho tho",              # «đau màng phổi» ⊄ «đau mạn»
    "Toi ho co mau 2 ngay, chong mat",
])
def test_L2_va_cham_gap_dau_khong_bien_trieu_chung_thanh_viec_le(cau):
    r = route(cau)
    assert r.kind != "single_task" or r.target not in ("co-mau-nghien-cuu", "dau-man-tinh"), (cau, r)


@pytest.mark.parametrize("cau", [
    "De tai nghien cuu co doi chung ve metformin",
    "De tai nghien cuu co do huyet ap 24 gio",
    "De tai nghien cuu co dot cap COPD",
])
def test_L3_co_do_khong_khop_co_doi_chung_co_do_huyet_ap(cau):
    assert route(cau).kind == "research_topic", cau


@pytest.mark.parametrize("cau", [
    "benh nhan nam 60 tuoi sot 39°C, ret run",
    "benh nhan nam 60 tuoi dau nguc… 2 gio",
    "benh nhan nam 60 tuoi – dau nguc",
    "benh nhan nam 60 tuoi dau nguc 😥",
])
def test_L4_ky_tu_phi_ascii_vo_hai_khong_day_cau_khong_dau_ve_bang_co_dau(cau):
    assert route(cau).kind == "clinical_case", cau


def test_L5_de_tai_ve_retraction_van_mo_g0_g10():
    assert route("Đề tài: phân tích retraction trong y văn Việt Nam").kind == "research_topic"
    assert route("Đề cương nghiên cứu corrigendum trong tạp chí y học").kind == "research_topic"


def test_L11_cau_nfd_dau_to_hop_duoc_chuan_hoa():
    import unicodedata
    nfd = unicodedata.normalize("NFD", "Bệnh nhân nam 60 tuổi đau ngực 2 giờ")
    assert route(nfd).kind == "clinical_case"


def test_cho_chinh_dang_van_dung_sau_khi_gap_dau():
    """Không hồi quy: cỡ mẫu / cờ đỏ gõ KHÔNG dấu đúng cụm vẫn vào đúng cửa."""
    assert route("tinh co mau cho nghien cuu cat ngang").target == "co-mau-nghien-cuu"
    assert route("benh nhan ngung tim, can chuyen vien cap cuu ngay").kind == "clinical_case"
