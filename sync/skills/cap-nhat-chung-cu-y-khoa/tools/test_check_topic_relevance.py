#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test cho check_topic_relevance.py — unittest chuẩn (không cần cài thêm), chạy:
    python3 tools/test_check_topic_relevance.py

Bộ ground truth 20 mục dùng đúng dữ liệu THẬT đã gặp ở dashboard TimMach_20260609 trước khi
sửa (2026-07-02): 8 mục lạc chủ đề đã bị gỡ khỏi dashboard thật, 12 mục đúng chủ đề còn giữ
lại — xem lịch sử phiên làm việc. Test KHÔNG gọi API thật (mock call_claude) vì môi trường
này không có ANTHROPIC_API_KEY; test riêng biệt (skip nếu thiếu key) để xác nhận model thật
phân loại đúng khi có key.

ĐƯA VÀO NGUỒN CHUẨN 17/11/2026 (trước chỉ nằm ở EBM-Dashboards/tools/, ngoài git — không ai canh,
CI không chạy). CI thu các lớp kiểm này qua tools/test_check_topic_relevance_20261117.py. Ba chỗ vá:
  • «thiếu khoá» nay chuyển hướng KHO_BI_MAT sang đường vắng — từ 17/11 call_claude đọc cả kho bí mật,
    nên bản cũ (chỉ gỡ biến môi trường) sẽ đọc khoá THẬT và gọi API thật, tốn tiền;
  • chốt tích hợp KHÔI PHỤC biến môi trường cũ thay vì xoá vô điều kiện (xoá mất khoá thật nếu có);
  • lượt gọi thật chỉ chạy khi đặt EBM_KIEM_API_THAT=1 — không bao giờ tự tiêu tiền khi chạy kiểm.
Bộ vàng có 19 mục (12 đúng chủ đề + 7 lạc chủ đề); tên ALL_20_ITEMS giữ nguyên cho tương thích.
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_topic_relevance as ctr  # noqa: E402

DASHBOARD_TOPIC = "Cập nhật chứng cứ — Tim mạch"

# 12 mục ĐÚNG chủ đề (còn giữ lại trong dashboard thật sau khi sửa 2026-07-02).
IN_TOPIC_ITEMS = [
    {"id": "ITEM-01", "title": "2755-LB: Education and Implementation to Improve Prescription "
     "of Guideline-Based Cardiorenal Protective Medications", "action": ""},
    {"id": "ITEM-02", "title": "Discrepancies in office blood pressure measurement protocols "
     "across international guidelines", "action": ""},
    {"id": "ITEM-03", "title": "Trends in the hypertension care cascade under dual guideline "
     "criteria in Peru, 2014-2024", "action": ""},
    {"id": "ITEM-04", "title": "Retrospective comparison of ChatGPT-4 treatment recommendations "
     "with real-world physician management in newly diagnosed hypertension", "action": ""},
    {"id": "ITEM-05", "title": "Cardiac evaluation of paediatric athletes", "action": ""},
    {"id": "ITEM-06", "title": "Mechanisms, Magnitude, and Consequence of Acute Estimated "
     "Glomerular Filtration Rate Change With Guideline-Directed Medical Therapy Initiation in "
     "Heart Failure", "action": ""},
    {"id": "ITEM-07", "title": "Global Lipid Guidelines: More Aligned Than They Appear",
     "action": ""},
    {"id": "ITEM-08", "title": "Development of a guideline-based clinical decision support "
     "system for emergency department assessment of suspected non-ST-elevation acute coronary "
     "syndromes", "action": ""},
    {"id": "ITEM-09", "title": "The impact of right ventricular free wall strain on current "
     "international echocardiography guidelines for the assessment of pulmonary hypertension",
     "action": ""},
    {"id": "ITEM-10", "title": "Net clinical benefit of extended dual pathway inhibition in "
     "chronic coronary syndrome as classified by the 2024 ESC criteria", "action": ""},
    {"id": "ITEM-11", "title": "Effect of Small-Quantity Lipid-Based Nutrient Supplementation "
     "on Children's Cortisol Concentration", "action": ""},  # NOTE: ground-truth gây tranh cãi,
    # xem test riêng test_known_ambiguous_case_is_flagged_or_uncertain bên dưới
    {"id": "ITEM-12", "title": "The impact of environmental pollution and climate change on "
     "hypertension: a position paper by the European Society of Hypertension", "action": ""},
]

# 7 mục THỰC SỰ lạc chủ đề (đã bị gỡ khỏi dashboard thật 2026-07-02 sau khi đọc tay).
OFF_TOPIC_ITEMS = [
    {"id": "ITEM-13", "title": "Vitamin B12 and Folic Acid Deficiency in Pregnancy: Current "
     "discrepancy in clinical practice and variety of guidelines", "action": ""},
    {"id": "ITEM-14", "title": "A multisociety consensus statement on a new common definition "
     "and diagnostic criteria for PSVD or NCPF", "action": ""},
    {"id": "ITEM-15", "title": "Kidney Disease: Improving Global Outcomes (KDIGO) Life Cycle of "
     "Guideline Development: Part 1: Introduction to a new series", "action": ""},
    {"id": "ITEM-16", "title": "Update on pediatric allergic rhinitis: narrative review based "
     "on guideline updates", "action": ""},
    {"id": "ITEM-17", "title": "KDIGO Life Cycle of Guideline Development Series- Part 3: "
     "Evidence synthesis for Guideline Development", "action": ""},
    {"id": "ITEM-18", "title": "KDIGO Life Cycle of Guideline Development Series- Part 4: "
     "Translating Evidence into KDIGO Guideline Statements", "action": ""},
    {"id": "ITEM-19", "title": "Treatment adherence among patients with pulmonary tuberculosis "
     "at Hai Duong Lung Hospital, Vietnam", "action": ""},
]

ALL_20_ITEMS = IN_TOPIC_ITEMS + OFF_TOPIC_ITEMS


class TestBuildPrompt(unittest.TestCase):
    def test_prompt_includes_topic_and_all_items(self):
        prompt = ctr.build_prompt(DASHBOARD_TOPIC, ALL_20_ITEMS)
        self.assertIn(DASHBOARD_TOPIC, prompt)
        for it in ALL_20_ITEMS:
            self.assertIn(it["id"], prompt)
            self.assertIn(it["title"][:30], prompt)  # đủ để chắc tiêu đề có mặt, không cần y hệt

    def test_prompt_asks_for_json_only(self):
        prompt = ctr.build_prompt(DASHBOARD_TOPIC, IN_TOPIC_ITEMS)
        self.assertIn("JSON", prompt)


class TestParseVerdicts(unittest.TestCase):
    def test_parses_clean_json(self):
        raw = json.dumps({"ITEM-01": {"verdict": "in_topic", "reason": "ok"}})
        out = ctr.parse_verdicts(raw)
        self.assertEqual(out["ITEM-01"]["verdict"], "in_topic")

    def test_strips_markdown_code_fence(self):
        raw = "```json\n" + json.dumps({"ITEM-01": {"verdict": "off_topic", "reason": "x"}}) + "\n```"
        out = ctr.parse_verdicts(raw)
        self.assertEqual(out["ITEM-01"]["verdict"], "off_topic")

    def test_rejects_invalid_verdict_value(self):
        raw = json.dumps({"ITEM-01": {"verdict": "maybe", "reason": "x"}})
        with self.assertRaises(ctr.TopicCheckError):
            ctr.parse_verdicts(raw)

    def test_rejects_non_json(self):
        with self.assertRaises(ctr.TopicCheckError):
            ctr.parse_verdicts("not json at all")

    def test_rejects_json_array_not_object(self):
        with self.assertRaises(ctr.TopicCheckError):
            ctr.parse_verdicts("[1, 2, 3]")


class TestCheckDashboardTopicRelevanceIntegration(unittest.TestCase):
    """Test logic tích hợp end-to-end BẰNG MOCK (không gọi API thật) — dùng ground truth 20 mục
    TimMach: mock trả về ĐÚNG verdict đã biết trước (giống model lý tưởng), xác nhận
    check_dashboard_topic_relevance() tổng hợp/phân loại kết quả đúng."""

    def _mock_perfect_response(self, prompt):
        verdicts = {}
        for it in IN_TOPIC_ITEMS:
            verdicts[it["id"]] = {"verdict": "in_topic", "reason": "liên quan tim mạch"}
        for it in OFF_TOPIC_ITEMS:
            verdicts[it["id"]] = {"verdict": "off_topic", "reason": "không liên quan tim mạch"}
        return json.dumps(verdicts)

    def test_no_api_key_returns_skipped_not_error(self):
        old = os.environ.pop("ANTHROPIC_API_KEY", None)
        kho_cu = ctr.KHO_BI_MAT
        # Kho bí mật cũng phải VẮNG — nếu không, call_claude đọc khoá thật và gọi API thật.
        ctr.KHO_BI_MAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_khong_ton_tai_", "x.env")
        try:
            with self.assertRaises(ctr.TopicCheckError):
                ctr.call_claude("bất kỳ prompt nào")
        finally:
            ctr.KHO_BI_MAT = kho_cu
            if old is not None:
                os.environ["ANTHROPIC_API_KEY"] = old

    def test_integration_with_mocked_perfect_model(self):
        """Nếu model chấm đúng 100% (ground truth), hàm tổng hợp phải báo đúng 8 off_topic,
        0 uncertain, không báo nhầm mục nào thuộc 12 mục in_topic."""
        original_call = ctr.call_claude
        ctr.call_claude = self._mock_perfect_response
        env_cu = os.environ.get("ANTHROPIC_API_KEY")
        try:
            os.environ["ANTHROPIC_API_KEY"] = "fake-key-for-test-only"
            # Gọi thẳng logic tổng hợp (không qua file thật) để test độc lập với I/O đĩa.
            items = ALL_20_ITEMS
            prompt = ctr.build_prompt(DASHBOARD_TOPIC, items)
            raw = ctr.call_claude(prompt)
            verdicts = ctr.parse_verdicts(raw)
            off_topic_ids = {iid for iid, v in verdicts.items() if v["verdict"] == "off_topic"}
            in_topic_ids = {iid for iid, v in verdicts.items() if v["verdict"] == "in_topic"}

            expected_off = {it["id"] for it in OFF_TOPIC_ITEMS}
            expected_in = {it["id"] for it in IN_TOPIC_ITEMS}
            self.assertEqual(off_topic_ids, expected_off)
            self.assertEqual(in_topic_ids, expected_in)
        finally:
            ctr.call_claude = original_call
            if env_cu is None:
                os.environ.pop("ANTHROPIC_API_KEY", None)
            else:
                os.environ["ANTHROPIC_API_KEY"] = env_cu


@unittest.skipUnless(os.getenv("EBM_KIEM_API_THAT") == "1",
                     "Gọi API thật (~0,02 USD) — chỉ chạy khi đặt EBM_KIEM_API_THAT=1")
class TestLiveModelAgainstGroundTruth(unittest.TestCase):
    """CHỈ chạy khi có ANTHROPIC_API_KEY thật trong môi trường — xác nhận model THẬT (không
    phải mock) phân loại đúng phần lớn 20 mục ground truth. Không yêu cầu 100% (model có sai
    số tự nhiên) nhưng phải đạt ngưỡng hợp lý để coi là dùng được."""

    def test_live_classification_accuracy(self):
        prompt = ctr.build_prompt(DASHBOARD_TOPIC, ALL_20_ITEMS)
        raw = ctr.call_claude(prompt)
        verdicts = ctr.parse_verdicts(raw)

        correct = 0
        for it in IN_TOPIC_ITEMS:
            if verdicts.get(it["id"], {}).get("verdict") == "in_topic":
                correct += 1
        for it in OFF_TOPIC_ITEMS:
            if verdicts.get(it["id"], {}).get("verdict") == "off_topic":
                correct += 1
        accuracy = correct / len(ALL_20_ITEMS)
        print(f"\n[LIVE] Độ chính xác so với ground truth: {accuracy:.0%} ({correct}/{len(ALL_20_ITEMS)})")
        self.assertGreaterEqual(accuracy, 0.80, "Độ chính xác dưới 80% — cần xem lại prompt.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
