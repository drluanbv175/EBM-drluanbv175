#!/usr/bin/env python3
"""Hồi quy phát hiện HIGH của Workflow đối kháng đa-agent vòng 4 (2026-09-05) trong
tools/orchestrator/intent.py::route() — bản vá vòng 3
(test_intent_workflow_20260904_co_do_thang_cue_de_tai.py) chỉ giải cứu khi câu chứa một
TỪ KHOÁ cờ đỏ tường minh khớp SINGLE_TASK_RULES["sang-loc-co-do"] ("cấp cứu"/"chuyển
viện"/"cờ đỏ"/"có nguy hiểm"/"đừng bỏ sót"). Một ca cấp cứu THẬT có thể không dùng đúng
từ nào trong số đó mà vẫn mang dấu hiệu RÕ RÀNG là đang mô tả MỘT bệnh nhân cụ thể theo
đúng khuôn trình bày ca lâm sàng ("nữ 60 tuổi,"/"bé trai...").

Ca thật: "nữ 60 tuổi, tiền sử ung thư vú, đang trong protocol hoá trị, nay sốt cao 39 độ,
rét run" — mô tả giảm bạch cầu hạt sốt (neutropenic fever), một cấp cứu ung thư học thật
sự. Câu này khớp RESEARCH_TOPIC_CUES qua từ "protocol" (rất phổ biến trong mô tả lâm sàng:
"protocol hoá trị") nhưng KHÔNG khớp bất kỳ từ khoá cờ đỏ tường minh nào của
"sang-loc-co-do" → trước bản vá này, route() trả research_topic, và RESEARCH_FLOW không có
bước nào tương đương BƯỚC 0 sàng lọc cờ đỏ của CLINICAL_FLOW.

Bản vá: mở rộng điều kiện "cờ đỏ luôn thắng cue đề tài" để CŨNG kiểm
`_INDIVIDUAL_PATIENT_OVERRIDE_PATTERNS` — tập CON của CLINICAL_CASE_PATTERNS, CHỈ hai mẫu
tuổi+giới cụ thể ("nữ 60 tuổi") và giới tính trẻ em ("bé trai") — KHÔNG bao gồm mẫu thai kỳ
("phụ nữ mang thai").

★ VÌ SAO LOẠI MẪU THAI KỲ — xác nhận bằng thực nghiệm, không phải suy đoán: bản vá ĐẦU TIÊN
dùng CẢ BA mẫu của CLINICAL_CASE_PATTERNS làm hỏng chính CA_CHINH của
test_orchestrator_workflow_20260904_research_topic_step0.py — "Nghiên cứu cắt ngang tỷ lệ đau
đầu dữ dội kèm sốt cao ở phụ nữ mang thai tại phòng khám" là một ĐỀ TÀI THẬT mô tả QUẦN THỂ
nghiên cứu (không phải một ca cụ thể), nhưng bị misroute ngược thành clinical_case vì khớp mẫu
"phụ nữ mang thai" — tái phát đúng lỗi vòng 10 mà RESEARCH_TOPIC_CUES sinh ra để chặn. "phụ nữ
mang thai" MỘT MÌNH không phải tín hiệu an toàn để phân biệt "một bệnh nhân cụ thể" khỏi "mô tả
quần thể", khác "nữ 60 tuổi,"/"bé trai..." (số tuổi/giới GẮN VÀO một chủ ngữ số ít, đúng khuôn
trình bày ca lâm sàng — không có tiền lệ dùng để mô tả quần thể trong toàn bộ test suite hiện
có, xác nhận bằng lớp đối chứng bên dưới).

⚠️ GIỚI HẠN CÒN LẠI, GHI NHẬN CÓ CHỦ Ý (không được coi là "đã đóng hoàn toàn"): một cấp cứu sản
khoa thật (tiền sản giật, sản giật…) mô tả bằng "protocol" mà KHÔNG kèm tuổi/giới cụ thể theo
đúng khuôn ca lâm sàng vẫn có thể lọt qua override này — xem lớp
`TestGioiHanConLaiThaiKyKhongKemTuoiGioiVanLotQua` bên dưới, ghi lại đúng hành vi HIỆN TẠI
(chưa đóng), không phải hành vi mong muốn.

Nguyên tắc viết test: gọi THẲNG route(), đối chiếu `kind`/`target`, không grep chuỗi trong
mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # tools/

from orchestrator.intent import CLINICAL_ORCHESTRATOR, RESEARCH_ORCHESTRATOR, route  # noqa: E402


class TestPatternHitsThangCueDeTaiKhongCoTuKhoaCoDoTuongMinh(unittest.TestCase):
    """★★ Ca chính đúng nguyên văn kịch bản trong finding."""

    def test_giam_bach_cau_hat_sot_khong_co_tu_khoa_co_do(self):
        r = route("nữ 60 tuổi, tiền sử ung thư vú, đang trong protocol hoá trị, "
                  "nay sốt cao 39 độ, rét run")
        self.assertEqual(r.kind, "clinical_case", r)
        self.assertEqual(r.target, CLINICAL_ORCHESTRATOR, r)

    def test_be_trai_kho_tho_dang_nghien_cuu_protocol_ho_tro_ho_hap(self):
        r = route("bé trai khó thở nhiều, đang trong protocol hỗ trợ hô hấp của khoa, "
                  "tím tái môi")
        self.assertEqual(r.kind, "clinical_case", r)
        self.assertEqual(r.target, CLINICAL_ORCHESTRATOR, r)


class TestDoiChungKhongPhaVoCaChinhVong3ThangCueDeTai(unittest.TestCase):
    """★★★ Đối chứng QUAN TRỌNG NHẤT — CA_CHINH của
    test_orchestrator_workflow_20260904_research_topic_step0.py (bản vá task #57, dùng mẫu
    thai kỳ để mô tả QUẦN THỂ nghiên cứu) TUYỆT ĐỐI không được bị phá vỡ. Đây chính là kịch
    bản đã bị hỏng ở bản vá đầu tiên (dùng cả 3 mẫu) trước khi phát hiện và thu hẹp lại."""

    def test_de_tai_cat_ngang_ve_phu_nu_mang_thai_van_la_research_topic(self):
        r = route("Nghiên cứu cắt ngang tỷ lệ đau đầu dữ dội kèm sốt cao ở phụ nữ mang thai "
                  "tại phòng khám")
        self.assertEqual(r.kind, "research_topic", r)
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR, r)


class TestDoiChungKhongMoRongQuaRongSangClinicalCaseCues(unittest.TestCase):
    """★★ Đối chứng BẮT BUỘC — bản vá CHỈ dùng 2 mẫu hẹp (tuổi+giới, trẻ em), KHÔNG dùng
    CLINICAL_CASE_CUES rộng hơn. Nếu lỡ mở rộng sang CLINICAL_CASE_CUES, hai test dưới đây
    (mô tả QUẦN THỂ nghiên cứu, dùng chữ "bệnh nhân" nhưng KHÔNG mô tả một ca cụ thể theo
    tuổi+giới) sẽ bị misroute ngược lại thành clinical_case — đúng lỗi vòng 10."""

    def test_de_tai_mo_ta_quan_the_benh_nhan_khong_co_pattern_tuoi_gioi(self):
        r = route("Nghiên cứu hồi cứu hiệu quả metformin trên bệnh nhân PCOS ngoại trú")
        self.assertEqual(r.kind, "research_topic", r)
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR, r)

    def test_de_tai_thuan_tuy_khong_co_pattern_tuoi_gioi(self):
        r = route("Tôi muốn viết đề cương protocol cho nghiên cứu hồi cứu về metformin")
        self.assertEqual(r.kind, "research_topic", r)
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR, r)


class TestDoiChungPatternHitsKhongCoCueDeTaiVanDungNhuCu(unittest.TestCase):
    """Đối chứng — một ca có CLINICAL_CASE_PATTERNS (tuổi+giới) nhưng KHÔNG có cue đề tài
    (đường đi thông thường, chưa từng hỏng) vẫn phải route đúng như trước — bản vá không đụng
    nhánh clinical_case gốc, chỉ mở rộng nhánh "cờ đỏ luôn thắng cue đề tài"."""

    def test_ca_binh_thuong_khong_co_tu_protocol_van_dung(self):
        r = route("nữ 60 tuổi, đau ngực dữ dội, vã mồ hôi")
        self.assertEqual(r.kind, "clinical_case", r)
        self.assertEqual(r.target, CLINICAL_ORCHESTRATOR, r)


class TestGioiHanConLaiThaiKyKhongKemTuoiGioiVanLotQua(unittest.TestCase):
    """⚠️ Ghi nhận GIỚI HẠN CÒN LẠI có chủ ý — KHÔNG phải test khẳng định "đúng", mà là bằng
    chứng bằng mã cho việc "chưa đóng hoàn toàn" đã nêu trong docstring đầu file. Nếu ai đó
    sau này lỡ đóng được khoảng trống này (vd thêm tín hiệu mới), assertEqual dưới đây sẽ tự
    nhắc phải cập nhật lại docstring — không được âm thầm để tài liệu lỗi thời."""

    def test_thai_ky_khong_kem_tuoi_gioi_van_roi_xuong_research_topic(self):
        r = route("phụ nữ mang thai, đang trong protocol theo dõi tiền sản giật, "
                  "đau đầu dữ dội, nhìn mờ")
        self.assertEqual(
            r.kind, "research_topic",
            f"{r}\n\nNếu test này FAIL vì kind đã đổi thành 'clinical_case', đó là một "
            "CẢI THIỆN thật — hãy cập nhật lại docstring đầu file (bỏ phần "
            "'GIỚI HẠN CÒN LẠI') thay vì coi đây là hồi quy.")


if __name__ == "__main__":
    unittest.main()
