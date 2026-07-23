#!/usr/bin/env python3
"""Hồi quy HIGH (vòng lặp kiểm tra-hoàn thiện vòng 10, 2026-07-22, workflow
wf_8e7ca8c0-968): RESEARCH_TOPIC_CUES trước đây chỉ có 8 cụm hẹp ("đề tài",
"đề cương", "protocol"...) — một đề tài nghiên cứu diễn đạt TỰ NHIÊN (không
dùng đúng 1 trong 8 cụm) mà có nhắc quần thể bệnh nhân bị định tuyến SAI
thành ca lâm sàng đơn lẻ (clinical_case/dieu-phoi-lam-sang), bỏ qua toàn bộ
cổng cứng G2/G4/G8/G9 của luồng nghiên cứu (research_topic/dieu-phoi-nghien-cuu).

Chạy: python tools/orchestrator/tests/test_intent_research_topic_natural_phrasing.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # tools/

from orchestrator.intent import RESEARCH_ORCHESTRATOR, CLINICAL_ORCHESTRATOR, route  # noqa: E402


class TestNaturalResearchPhrasingRoutesToResearchTopic(unittest.TestCase):
    def test_retrospective_study_natural_phrasing(self):
        r = route("Nghiên cứu hồi cứu hiệu quả metformin trên bệnh nhân PCOS ngoại trú")
        self.assertEqual(r.kind, "research_topic")
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR)

    def test_i_want_to_research_phrasing(self):
        r = route("Tôi muốn nghiên cứu tác dụng phụ statin ở bệnh nhân cao tuổi")
        self.assertEqual(r.kind, "research_topic")
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR)

    def test_cross_sectional_survey_phrasing(self):
        r = route("Khảo sát cắt ngang mức độ tuân thủ điều trị ở bệnh nhân đái tháo đường")
        self.assertEqual(r.kind, "research_topic")
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR)

    def test_comparative_study_phrasing_with_gender_cues(self):
        # "nam," / "nữ," khớp CLINICAL_CASE_CUES nhưng cụm nghiên cứu phải thắng vì được
        # kiểm TRƯỚC trong route().
        r = route("Nghiên cứu so sánh tỷ lệ mắc bệnh giữa nam, nữ trong nhóm tuổi 40-60")
        self.assertEqual(r.kind, "research_topic")
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR)

    def test_original_narrow_cue_still_works(self):
        # Không hồi quy ngược: cụm cũ ("Đề tài...") vẫn phải đúng.
        r = route("Đề tài hiệu quả metformin ở bệnh nhân PCOS ngoại trú")
        self.assertEqual(r.kind, "research_topic")


class TestClinicalEvidenceLookupStaysClinical(unittest.TestCase):
    """Không được lạm phát ngược: một câu hỏi lâm sàng việc lẻ chỉ TÌNH CỜ chứa từ
    "nghiên cứu" (không phải khởi động đề tài mới) không được đẩy sang research_topic."""

    def test_bare_research_word_in_clinical_question_not_misrouted(self):
        r = route("Nghiên cứu nào ủng hộ dùng SGLT2i cho bệnh nhân này?")
        self.assertNotEqual(r.kind, "research_topic")

    def test_plain_clinical_case_still_routes_clinical(self):
        r = route("Tôi có bệnh nhân nam 68 tuổi, đau ngực khi gắng sức")
        self.assertEqual(r.kind, "clinical_case")
        self.assertEqual(r.target, CLINICAL_ORCHESTRATOR)


if __name__ == "__main__":
    unittest.main()
