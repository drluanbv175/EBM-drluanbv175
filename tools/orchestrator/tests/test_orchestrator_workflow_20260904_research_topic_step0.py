#!/usr/bin/env python3
"""Hồi quy phát hiện HIGH của Workflow đối kháng đa-agent 2026-09-04 (task #57):
`Orchestrator.handle()` không ép chạy BƯỚC 0 cờ đỏ (`sang-loc-co-do`) cho nhánh
`research_topic`, dù RESEARCH_FLOW (G0→G10) không có bước nào tương đương.

Cơ chế lỗi: `intent.py::route()` có luật (vòng 3, đã vá) khiến "sang-loc-co-do"
thắng cue đề tài — NHƯNG luật đó chỉ cứu khi câu khớp ĐÚNG cụm hẹp trong
SINGLE_TASK_RULES ("có nguy hiểm"/"chuyển viện"/"cấp cứu"/"cờ đỏ"/"đừng bỏ
sót"). Một đề tài nghiên cứu diễn đạt tự nhiên vẫn có thể lồng mô tả LÂM SÀNG
NGUY HIỂM mà không dùng đúng cụm đó — ca thật đã đo: "Nghiên cứu cắt ngang tỷ
lệ đau đầu dữ dội kèm sốt cao ở phụ nữ mang thai tại phòng khám" (gợi ý tiền
sản giật/viêm màng não) khớp RESEARCH_TOPIC_CUES ("nghiên cứu cắt ngang")
nhưng KHÔNG khớp bất kỳ cụm nào của "sang-loc-co-do" → `route()` trả
`research_topic`, và `flows.py::RESEARCH_FLOW` không có bước nào tương đương
BƯỚC 0 của CLINICAL_FLOW → session chạy trọn 25 bước G0→G10 mà KHÔNG MỘT LẦN
nào `sang-loc-co-do` được gọi.

Cùng nguyên tắc bất biến BH88 đã áp cho nhánh 'unknown' (Workflow đối kháng
vòng 2, 2026-09-03): "over-route sang nơi CÓ sàng lọc cờ đỏ là chiều an
toàn, under-route bỏ qua cờ đỏ thì không". Bản vá này áp CÙNG nguyên tắc cho
`research_topic`: chạy BƯỚC 0 như một lớp phòng thủ bổ sung, KHÔNG đổi
kind/routing/cổng.

Nguyên tắc viết test: gọi THẲNG `Orchestrator.handle()` với câu THẬT đã tái
hiện được lỗi, không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator.intent import route  # noqa: E402
from orchestrator.orchestrator import Orchestrator  # noqa: E402

# Ca chính đã tái hiện được lỗi sống: nghiên cứu cắt ngang lồng mô tả lâm sàng
# nguy hiểm (đau đầu dữ dội + sốt cao ở phụ nữ mang thai — gợi ý tiền sản
# giật/viêm màng não), không khớp bất kỳ cụm "sang-loc-co-do" nào.
CA_CHINH = "Nghiên cứu cắt ngang tỷ lệ đau đầu dữ dội kèm sốt cao ở phụ nữ mang thai tại phòng khám"


class TestTienDieuKienCaChinhVanLaResearchTopic(unittest.TestCase):
    """Xác nhận route() vẫn phân loại đúng research_topic cho ca chính (nếu
    intent.py đổi cách phân loại sau này, test này phải fail trước tiên để
    không ai hiểu nhầm bản vá này còn cần thiết hay không)."""

    def test_ca_chinh_van_la_research_topic_khong_khop_sang_loc_co_do(self):
        result = route(CA_CHINH)
        self.assertEqual(result.kind, "research_topic")
        self.assertNotIn("sang-loc-co-do", [m for m in result.matches])


class TestResearchTopicChayBuoc0(unittest.TestCase):
    """★★ Ca chính — BƯỚC 0 phải chạy TRƯỚC G0, không đổi kind/routing/cổng."""

    def test_sang_loc_co_do_duoc_goi_dau_tien(self):
        session = Orchestrator().handle(CA_CHINH)
        self.assertGreaterEqual(len(session.trace), 1)
        first = session.trace[0]
        self.assertEqual(first["step"], "0")
        self.assertEqual(first["agent"], "sang-loc-co-do")

    def test_kind_va_dich_khong_doi(self):
        session = Orchestrator().handle(CA_CHINH)
        self.assertEqual(session.kind, "research_topic")
        self.assertEqual(session.entry_agent, "dieu-phoi-nghien-cuu")

    def test_van_dung_o_dung_cong_g2_nhu_truoc(self):
        """Thêm BƯỚC 0 không được làm lệch cổng cứng G2 (đạo đức) — vẫn phải
        dừng đúng chỗ RESEARCH_FLOW quy định."""
        session = Orchestrator().handle(CA_CHINH)
        self.assertIn("G2", session.status)

    def test_g0_van_chay_sau_buoc_0_khong_bi_mat(self):
        """BƯỚC 0 là bổ sung, KHÔNG được thay thế G0-G10 — toàn bộ chuỗi cổng
        vẫn phải nguyên vẹn phía sau."""
        session = Orchestrator().handle(CA_CHINH)
        steps_after_0 = [row["step"] for row in session.trace[1:]]
        self.assertIn("G0", steps_after_0)
        self.assertIn("G2", steps_after_0)

    def test_mot_de_tai_khong_lien_quan_lam_sang_van_qua_buoc_0_an_toan(self):
        """★★ Đối chứng bắt buộc — BƯỚC 0 chạy vô hại cho một đề tài KHÔNG mô
        tả tình huống nguy hiểm (sang-loc-co-do tự quyết định không có gì
        đáng ngại; agent vẫn CHẠY nhưng không đổi kết cục an toàn)."""
        session = Orchestrator().handle(
            "Nghiên cứu hồi cứu tỷ lệ tuân thủ điều trị statin ở bệnh nhân ngoại trú"
        )
        self.assertEqual(session.kind, "research_topic")
        self.assertEqual(session.trace[0]["agent"], "sang-loc-co-do")
        # vẫn tiếp tục chạy hết chuỗi G0-G10, không bị chặn oan bởi bước bổ sung
        self.assertIn("G2", [row["step"] for row in session.trace])


class TestDoiChungCacKindKhacKhongBiAnhHuong(unittest.TestCase):
    """★★ Bốn kind còn lại (clinical_case/single_task/cong_cu/unknown) phải
    giữ nguyên hành vi — bản vá CHỈ chạm nhánh research_topic."""

    def test_clinical_case_van_chi_chay_buoc_0_mot_lan_nhu_cu(self):
        session = Orchestrator().handle(
            "Bệnh nhân nữ 60 tuổi đau ngực dữ dội, khó thở — xử trí gì ngay?"
        )
        self.assertEqual(session.kind, "clinical_case")
        step0_count = sum(1 for row in session.trace if row["step"] == "0")
        self.assertEqual(step0_count, 1, "BƯỚC 0 không được chạy 2 lần cho clinical_case")

    def test_single_task_khong_co_buoc_0(self):
        session = Orchestrator().handle("Tính cỡ mẫu cho nghiên cứu cắt ngang tỷ lệ tăng huyết áp")
        self.assertEqual(session.kind, "single_task")
        self.assertNotIn("sang-loc-co-do", [row.get("agent") for row in session.trace])

    def test_cong_cu_khong_co_buoc_0(self):
        session = Orchestrator().handle("còn gì để hoàn thiện hệ thống?")
        self.assertEqual(session.kind, "cong_cu")
        self.assertNotIn("sang-loc-co-do", [row.get("agent") for row in session.trace])

    def test_unknown_van_chi_chay_buoc_0_mot_lan_nhu_cu(self):
        session = Orchestrator().handle("xin chào")
        self.assertEqual(session.kind, "unknown")
        step0_count = sum(1 for row in session.trace if row["step"] == "0")
        self.assertEqual(step0_count, 1, "BƯỚC 0 không được chạy 2 lần cho unknown")


if __name__ == "__main__":
    unittest.main()
