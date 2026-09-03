#!/usr/bin/env python3
"""Hồi quy phát hiện CRITICAL của Workflow đối kháng đa-agent vòng 2 (2026-09-03):

Trước khi vá, `Orchestrator.handle()` trả `status='needs_clarification'` NGAY LẬP TỨC
khi `route()` không nhận diện được câu (`kind == 'unknown'`) — 0 bước, 0 bản ghi trace.
Nghĩa là BƯỚC 0 cờ đỏ (`sang-loc-co-do`) KHÔNG BAO GIỜ chạy cho một câu mô tả ca có khả
năng nguy hiểm nhưng không khớp bất kỳ luật nào của `intent.route()` — đo được bằng chạy
sống với câu tự nhiên gợi ý tiền sản giật/suy hô hấp trẻ em.

Đúng bất biến BH88 đã tuyên bố ("over-route sang nơi CÓ sàng lọc cờ đỏ là chiều an toàn,
under-route bỏ qua cờ đỏ thì không") — `unknown` còn tệ hơn under-route vì nó là KHÔNG
định tuyến gì cả. Bản vá: LUÔN chạy BƯỚC 0 cờ đỏ trước khi trả `needs_clarification`.

Kèm 2 hồi quy phụ (cùng phát hiện, mức độ thấp hơn — cải thiện độ phủ NLU của
`intent.route()`, không phải bản thân bất biến an toàn):
  - CLINICAL_CASE_PATTERNS: nhận diện thêm mô tả tuổi/giới/thai kỳ tự nhiên.
  - `_khao_sat_co_thiet_ke()`: chống misroute một mô tả ĐỀ TÀI có từ chen giữa cụm thiết kế
    bị SINGLE_TASK_RULES nuốt mất (vd "trầm cảm" khớp việc lẻ trước khi kịp nhận ra đây là
    một đề tài khảo sát cắt ngang).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator.intent import route  # noqa: E402
from orchestrator.orchestrator import Orchestrator  # noqa: E402


class TestUnknownAlwaysRunsRedFlagScreening(unittest.TestCase):
    """Trục CRITICAL — bất biến an toàn ở orchestrator.py, KHÔNG phụ thuộc độ phủ NLU."""

    def test_unknown_request_still_runs_sang_loc_co_do(self):
        o = Orchestrator()
        # Một câu bất kỳ không khớp luật nào của route() — không cần liên quan lâm sàng,
        # bất biến phải giữ CHO MỌI 'unknown', không chỉ câu có vẻ nguy hiểm.
        s = o.handle("xyz không rõ nghĩa gì cả 12345", persist=False)
        self.assertEqual(s.kind, "unknown")
        self.assertEqual(s.status, "needs_clarification")
        self.assertTrue(
            any(t.get("agent") == "sang-loc-co-do" for t in s.trace),
            f"BƯỚC 0 cờ đỏ phải luôn chạy khi unknown — trace: {s.trace}",
        )

    def test_dangerous_unrecognized_sentence_still_screened(self):
        """Ca cụ thể đã đo được rơi 'unknown' TRƯỚC bản vá NLU — bất biến an toàn phải
        giữ đúng bất kể route() có nhận diện được câu hay không (test này cố tình không
        phụ thuộc kết quả NLU — xem test riêng ở lớp dưới cho phần đó)."""
        o = Orchestrator()
        s = o.handle(
            "Cụ bà không rõ tình trạng gì đó đau bụng dạng khó tả kỳ lạ chưa từng thấy",
            persist=False,
        )
        # Bất kể kind cuối cùng là gì (unknown hay clinical_case), nếu vẫn unknown thì
        # phải đã chạy sàng lọc cờ đỏ.
        if s.kind == "unknown":
            self.assertTrue(any(t.get("agent") == "sang-loc-co-do" for t in s.trace))

    def test_empty_request_also_screened_not_a_bare_zero_trace(self):
        o = Orchestrator()
        s = o.handle("", persist=False)
        self.assertEqual(s.kind, "unknown")
        self.assertEqual(len(s.trace), 1)
        self.assertEqual(s.trace[0].get("agent"), "sang-loc-co-do")

    def test_normal_clinical_case_path_unaffected(self):
        """Đối chứng: đường ĐÃ nhận diện được (clinical_case) không đổi hành vi —
        sang-loc-co-do đã LUÔN là bước đầu của CLINICAL_FLOW từ trước bản vá này."""
        o = Orchestrator()
        s = o.handle("Tôi có bệnh nhân nam 65 tuổi đau ngực, cần đánh giá.", persist=False)
        self.assertEqual(s.kind, "clinical_case")
        self.assertGreater(len(s.trace), 1)
        self.assertEqual(s.trace[0].get("agent"), "sang-loc-co-do")

    def test_normal_research_topic_path_unaffected(self):
        o = Orchestrator()
        s = o.handle(
            "Tôi muốn nghiên cứu hồi cứu hiệu quả metformin trên bệnh nhân PCOS.",
            persist=False,
        )
        self.assertEqual(s.kind, "research_topic")


class TestClinicalCasePatternsRecognizeNaturalPhrasing(unittest.TestCase):
    """Trục phụ — mở rộng độ phủ NLU cho CLINICAL_CASE_CUES bằng regex hẹp."""

    def test_pregnancy_headache_case_recognized(self):
        r = route("Phụ nữ mang thai 32 tuần bị đau đầu dữ dội kèm phù chân, huyết áp 160/100")
        self.assertEqual(r.kind, "clinical_case")

    def test_child_dyspnea_case_recognized(self):
        r = route("Bé trai 8 tuổi khó thở về đêm, nghi hen")
        self.assertEqual(r.kind, "clinical_case")

    def test_gender_age_without_separator_recognized(self):
        r = route("Nữ 60 tuổi tăng huyết áp mới phát hiện, cần tư vấn điều trị")
        self.assertEqual(r.kind, "clinical_case")

    def test_girl_child_descriptor_recognized(self):
        r = route("Cháu gái 5 tuổi sốt cao liên tục 3 ngày")
        self.assertEqual(r.kind, "clinical_case")

    def test_bare_age_alone_without_gender_or_child_marker_stays_unaffected(self):
        """Đối chứng cố ý hẹp: KHÔNG thêm mẫu \\d+\\s*tuổi trần (quá rộng — xem comment
        trong intent.py) — một câu chỉ có số tuổi, không có 'nam/nữ' hay 'bé/cháu' đứng
        cạnh, không được tự động thành clinical_case qua patterns mới."""
        r = route("Cần biết thêm dữ liệu ở nhóm 65 tuổi")
        # Không có cue/pattern nào khớp — phải KHÔNG rơi vào clinical_case
        self.assertNotEqual(r.kind, "clinical_case")


class TestKhaoSatWithDesignWordNotSwallowedBySingleTask(unittest.TestCase):
    """Trục phụ — chống misroute một mô tả ĐỀ TÀI có từ chen giữa cụm thiết kế."""

    def test_depression_survey_with_scattered_design_words_routes_to_research(self):
        r = route("Muốn khảo sát tỷ lệ trầm cảm sau sinh tại phòng khám, thiết kế cắt ngang mô tả")
        self.assertEqual(r.kind, "research_topic")
        self.assertEqual(r.target, "dieu-phoi-nghien-cuu")

    def test_khao_sat_without_design_word_does_not_trigger(self):
        """Đối chứng: 'khảo sát' MỘT MÌNH (không có từ thiết kế nào) không được kích
        hoạt — tránh biến 'khảo sát' trần thành cue quá rộng như đã tránh cho 'nghiên cứu'."""
        r = route("Có khảo sát nào về tần suất tái khám của bệnh nhân không?")
        self.assertNotEqual(r.kind, "research_topic")

    def test_existing_adjacent_phrase_cue_still_works(self):
        """Đối chứng: cụm liền kề gốc ('khảo sát cắt ngang') vẫn khớp như trước."""
        r = route("Tôi muốn làm một khảo sát cắt ngang về tuân thủ điều trị")
        self.assertEqual(r.kind, "research_topic")

    def test_strong_single_task_still_wins_over_bare_nghien_cuu_word(self):
        """Đối chứng: caveat gốc của tác giả vẫn còn nguyên — 'nghiên cứu' trần (không
        phải 'khảo sát') không được mở rộng thành match rời rạc; câu hỏi tra cứu chứng
        cứ tại điểm khám vẫn không bị hiểu nhầm thành mở đề tài."""
        r = route("Nghiên cứu nào ủng hộ dùng SGLT2i cho bệnh nhân này, có so sánh với GLP-1 không?")
        self.assertNotEqual(r.kind, "research_topic")


if __name__ == "__main__":
    unittest.main()
