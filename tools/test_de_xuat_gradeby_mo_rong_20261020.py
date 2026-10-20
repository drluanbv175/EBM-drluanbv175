# -*- coding: utf-8 -*-
"""Mở rộng đề xuất gradeBy (20/10/2026, bác sĩ: «Giải quyết 3 vấn đề chưa đạt»). Mỗi ca dưới là MỘT ca thật gặp khi soát
toàn văn gradeSource của 330 mục — máy chỉ đề xuất khi CHỮ của item chứng minh ai chấm; còn lại để tay người."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_sp = importlib.util.spec_from_file_location("_gb_mr", Path(__file__).resolve().parent / "de_xuat_gradeby.py")
G = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(G)


@pytest.mark.parametrize("gs,org,mong", [
    # lời người soạn tự nhận
    ("RCT (đánh giá vận hành: độ chắc chắn trung bình; cỡ mẫu nhỏ)", "NEJM", ("G9", "Người soạn — đánh giá vận hành")),
    # Cochrane tự chấm
    ("Cochrane tự chấm: chứng cứ CHẤT LƯỢNG CAO cho việc giảm tỷ lệ được truyền máu", "Cochrane Database",
     ("G8", "Cochrane (GRADE)")),
    # tổ chức có tên + thuật ngữ phân hạng, trùng org của item
    ("AAN 2022 — Level B (nên cung cấp)", "American Academy of Neurology", ("G10", "AAN (phân hạng nguyên bản)")),
    ("Phân hạng chứng cứ GOLD (A–D) theo nguồn", "Global Initiative for Chronic Obstructive Lung Disease",
     ("G10", "GOLD (phân hạng nguyên bản)")),
    # thuật ngữ phân hạng, không nêu tổ chức — mức thuộc nguồn của CHÍNH item (guideline AHA/ASA)
    ("Khuyến cáo loại I (statin cường độ cao); mục tiêu LDL <70 mg/dL", "AHA/ASA", ("G10", "AHA/ASA (phân hạng nguyên bản)")),
    ("Khuyến cáo loại I (dựa EMPEROR-Preserved, DELIVER)", "European Society of Cardiology",
     ("G10", "ESC (phân hạng nguyên bản)")),
    # tên tổ chức lấy từ CHỮ của gradeSource: org «SVS / ESVS» + «SVS grade 1» ⇒ SVS, KHÔNG phải ESVS
    ("SVS grade 1, chất lượng trung bình (tái thông <14 ngày)", "SVS / ESVS", ("G10", "SVS (phân hạng nguyên bản)")),
    # chỉ mô tả thiết kế, không tổ chức nào
    ("RCT đa trung tâm, nguy cơ sai lệch thấp", "Lancet",
     ("G11", "Người soạn — đánh giá theo thiết kế (nguồn không tự phân hạng)")),
])
def test_de_xuat_dung(gs, org, mong):
    assert G.phan_nhom(gs, org) == mong


@pytest.mark.parametrize("gs,org", [
    # «LOE A» của AHA không được rơi vào nhóm EULAR (mẫu LoE không phân biệt hoa/thường)
    ("RCT lớn; AHA/ASA 2026 mục 4.9 — COR 2a, LOE A", "Lancet"),
    # bài tổng quan trên tạp chí nói lại mức của ATS — không chắc ai chấm
    ("ATS 2025 guideline update — review 2026; chứng cứ quan sát + RCT nhỏ (chất lượng rất thấp)", "Am J Emerg Med"),
    # hai tổ chức ⇒ không đoán
    ("ATS 2025 — chứng cứ chất lượng RẤT THẤP (IDSA rút bảo lãnh vì thiếu dữ liệu an toàn)", "ATS"),
    # có bàn tay bác sĩ ⇒ để bác sĩ tự xác nhận
    ("RCT (đánh giá vận hành: độ chắc chắn cao) | Đồng bộ (bác sĩ chuẩn y 14/08/2026)", "NEJM"),
    # thẩm định trộn với mức của tổ chức ⇒ không rõ mức lấy từ đâu
    ("GRADE Cao (thẩm định) — nguồn gốc AAN xếp Mức A", "American Academy of Neurology"),
    # Cochrane không nêu mức ⇒ không chắc người soạn có chép GRADE của Cochrane
    ("Tổng quan hệ thống Cochrane", "Cochrane Collaboration"),
    # thuật ngữ phân hạng, org là tạp chí ⇒ không đoán
    ("Khuyến cáo loại I (Class 1)", "Lancet"),
])
def test_khong_du_chu_thi_de_tay_nguoi(gs, org):
    assert G.phan_nhom(gs, org) is None


def test_g1_g3_goc_van_chay():
    assert G.phan_nhom("COR I, LOE A — ACC/AHA 2022", "ACC/AHA") == ("G1", "ACC/AHA (COR/LOE)")
    assert G.phan_nhom("KDIGO: khuyến cáo mạnh theo GRADE", "KDIGO") == ("G3", "KDIGO (GRADE)")


def test_g3_khong_ten_to_chuc_khong_bi_mat_khoi_bao_cao():
    """Trước 20/10: mục khớp G3 mà không có tên tổ chức bị `break` loại khỏi CẢ hai danh sách (74 mục biến mất khỏi báo
    cáo). Nay phan_nhom trả kết quả xác định (None ⇒ «không tự suy») — quet() luôn xếp mục vào một trong hai danh sách."""
    kq = G.phan_nhom("Bằng chứng theo GRADE (thẩm định)", "Journal X")
    assert kq is None
    src = (Path(__file__).resolve().parent / "de_xuat_gradeby.py").read_text(encoding="utf-8")
    than = src[src.index("def quet()"):src.index("def ap_dung(")]
    assert "khong_suy.append(muc)" in than and "break" not in than
