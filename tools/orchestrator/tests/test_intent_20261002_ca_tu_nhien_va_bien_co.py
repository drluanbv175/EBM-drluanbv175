"""Hồi quy B2 (02/10/2026): câu bác sĩ mô tả ca TỰ NHIÊN rơi `unknown`; «ngừng tim + protocol hồi sức» rơi nhánh đề tài.

Đo trên 17 câu: 10 câu ca tự nhiên (xưng hô + tuổi, trẻ em + tuổi, thai phụ + tuần, «đang dùng» thuốc) ⇒ `unknown`; câu ngừng tim ⇒
`research_topic` (do «protocol») — mất BƯỚC 0 cờ đỏ. Over-route sang nhạc trưởng lâm sàng là chiều AN TOÀN; mô tả QUẦN THỂ nghiên cứu
(«người 65 tuổi trở lên», «trẻ 6 tháng đến 5 tuổi») phải giữ nguyên nhánh đề tài/việc lẻ."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from intent import route  # noqa: E402


@pytest.mark.parametrize("cau", [
    "ông 65 tuổi sốt ho 3 ngày khó thở", "bà 70 tuổi rung nhĩ mới phát hiện, có nên dùng kháng đông",
    "người 80 tuổi té ngã, uống 9 loại thuốc", "trẻ 3 tuổi sốt cao co giật", "sản phụ 30 tuần HA 160/100",
    "cô 25 tuổi khó thở đột ngột", "anh 45t tiểu đường HbA1c 9", "chị 38 tuổi TSH tăng",
    "suy tim, kali 6,2, đang dùng spironolactone", "kê đơn cho CKD giai đoạn 4 đang dùng metformin",
    "ong 65 tuoi sot ho 3 ngay kho tho", "tre 3 tuoi sot cao co giat", "san phu 30 tuan HA 160/100",
])
def test_ca_tu_nhien_vao_nhac_truong_lam_sang(cau):
    r = route(cau)
    assert r.kind == "clinical_case" and r.target == "dieu-phoi-lam-sang", (cau, r)


@pytest.mark.parametrize("cau", [
    "bệnh nhân ngừng tim, chạy protocol hồi sức thế nào",
    "benh nhan ngung tim chay protocol hoi suc",
    "đề tài: protocol xử trí sốc phản vệ tại phòng khám, có ca bất tỉnh",
    "nghiên cứu cắt ngang về co giật do sốt ở trẻ, protocol theo dõi",
])
def test_bien_co_cap_cuu_thang_cue_de_tai(cau):
    assert route(cau).kind == "clinical_case", cau


@pytest.mark.parametrize("cau,kind", [
    ("Nghiên cứu cắt ngang tỷ lệ tăng huyết áp ở người 65 tuổi trở lên", "research_topic"),
    ("Khảo sát mô tả tình trạng dinh dưỡng trẻ 6 tháng đến 5 tuổi", "research_topic"),
    ("đề tài: tỷ lệ tăng huyết áp ở người cao tuổi", "research_topic"),
    ("Nghiên cứu cắt ngang tỷ lệ đau đầu dữ dội kèm sốt cao ở phụ nữ mang thai tại phòng khám", "research_topic"),
    ("tính cỡ mẫu cho nghiên cứu cắt ngang", "single_task"),
    ("Tra biệt dược Coversyl là hoạt chất gì", "single_task"),
    ("người 65 tuổi trở lên nên tiêm vắc-xin gì", "single_task"),
])
def test_mo_ta_quan_the_va_viec_le_giu_nguyen(cau, kind):
    assert route(cau).kind == kind, (cau, route(cau))


def test_khong_khop_chuoi_con_trong_tu_khac():
    """«ông» trong «không», «em» trong «them» không được thành xưng hô."""
    assert route("không 5 tuổi nào").kind == "unknown"
    assert route("thêm 5 tuổi vào dữ liệu").kind == "unknown"
