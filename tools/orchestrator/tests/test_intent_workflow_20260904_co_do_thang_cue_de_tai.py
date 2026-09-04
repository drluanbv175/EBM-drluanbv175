#!/usr/bin/env python3
"""Hồi quy phát hiện CRITICAL của Workflow đối kháng đa-agent vòng 3 (2026-09-04) trong
tools/orchestrator/intent.py::route() — CỜ ĐỎ không thắng được cue ĐỀ TÀI dù comment ở
VIEC_LE_MANH (dòng ~129-131) đã tự khai bất biến "việc lẻ mạnh KHÔNG bao giờ thắng cue
CA LÂM SÀNG — over-route sang nơi CÓ sàng lọc cờ đỏ là chiều an toàn".

Ca thật: một mô tả cấp cứu THẬT ("bệnh nhân ngừng tim, chạy protocol hồi sức...") chứa
từ "protocol" — một RESEARCH_TOPIC_CUES hợp lệ, thường gặp trong mô tả lâm sàng ("protocol
hoá trị", "protocol hồi sức"), KHÔNG chỉ trong ngữ cảnh nghiên cứu. route() kiểm cue đề tài
TRƯỚC (có chủ đích, để không misroute một đề tài mô tả quần thể thành ca lâm sàng đơn lẻ —
xem test_intent_research_topic_natural_phrasing.py), và nhánh "giải cứu" duy nhất trước bản
vá này (`manh`) chỉ cứu VIEC_LE_MANH (agent nghiên cứu thuần: co-mau-nghien-cuu,
kiem-chung-trich-dan…) — "sang-loc-co-do" (agent sàng lọc CỜ ĐỎ) bị loại KHỎI tập đó một
cách CÓ CHỦ Ý (nó không phải "sản phẩm nghiên cứu lẻ"), nên một request vừa khớp cue đề tài
("protocol") vừa khớp cờ đỏ ("cấp cứu"/"chuyển viện"...) bị route thẳng vào research_topic —
RESEARCH_FLOW (G0→G10) không có bước nào tương đương BƯỚC 0 sàng lọc cờ đỏ của CLINICAL_FLOW,
nên một ca cấp cứu thật KHÔNG BAO GIỜ được sàng lọc.

Nguyên tắc viết test: gọi THẲNG route(), đối chiếu `kind`/`target`, không grep chuỗi trong
mã nguồn. Chạy: python tools/orchestrator/tests/test_intent_workflow_20260904_co_do_thang_cue_de_tai.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # tools/

from orchestrator.intent import CLINICAL_ORCHESTRATOR, RESEARCH_ORCHESTRATOR, route  # noqa: E402


class TestCoDoThangCueDeTai(unittest.TestCase):
    """★★ Ca chính đúng nguyên văn kịch bản trong finding."""

    def test_ngung_tim_voi_tu_protocol_van_di_qua_sang_loc_co_do(self):
        r = route("Bệnh nhân ngừng tim, chạy protocol hồi sức thế nào, cần chuyển cấp cứu ngay?")
        self.assertEqual(r.kind, "clinical_case", r)
        self.assertEqual(r.target, CLINICAL_ORCHESTRATOR, r)
        self.assertTrue(any("sang-loc-co-do" in m for m in r.matches), r.matches)

    def test_giam_bach_cau_hat_sot_dang_protocol_hoa_tri(self):
        r = route(
            "Bệnh nhân đang trong protocol hóa trị, sốt cao 39.5 độ, ớn lạnh, "
            "nghi giảm bạch cầu hạt sốt, cần chuyển cấp cứu không?"
        )
        self.assertEqual(r.kind, "clinical_case", r)
        self.assertEqual(r.target, CLINICAL_ORCHESTRATOR, r)

    def test_dang_ky_co_do_bang_tu_khoa_khac_cung_thang(self):
        r = route("Đề cương protocol này có nguy hiểm gì cho bệnh nhân không, có cần chuyển viện?")
        self.assertEqual(r.kind, "clinical_case", r)
        self.assertEqual(r.target, CLINICAL_ORCHESTRATOR, r)


class TestDoiChungKhongPhaVoHanhViCu(unittest.TestCase):
    """Đối chứng BẮT BUỘC: cue đề tài KHÔNG kèm cờ đỏ vẫn phải route đúng research_topic
    như trước bản vá — bản vá chỉ thêm MỘT lối thoát hẹp (cờ đỏ), không đổi luật chung."""

    def test_de_tai_thuan_tuy_khong_co_do_van_ra_research_topic(self):
        r = route("Tôi muốn viết đề cương protocol cho nghiên cứu hồi cứu về metformin")
        self.assertEqual(r.kind, "research_topic", r)
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR, r)

    def test_khao_sat_tu_nhien_khong_co_do_van_dung_nhu_cu(self):
        r = route("Nghiên cứu hồi cứu hiệu quả metformin trên bệnh nhân PCOS ngoại trú")
        self.assertEqual(r.kind, "research_topic", r)
        self.assertEqual(r.target, RESEARCH_ORCHESTRATOR, r)

    def test_viec_le_manh_van_thang_cue_de_tai_khi_khong_co_co_do(self):
        """Đối chứng: nhánh VIEC_LE_MANH cũ (agent nghiên cứu thuần thắng cue đề tài khi
        KHÔNG có cờ đỏ) không bị đổi hành vi bởi bản vá."""
        r = route("Tính cỡ mẫu cho nghiên cứu cắt ngang này")
        self.assertEqual(r.kind, "single_task", r)
        self.assertEqual(r.target, "co-mau-nghien-cuu", r)


class TestCoDoThuanKhongCoCueDeTaiVanDungNhuCu(unittest.TestCase):
    """Đối chứng: một ca cấp cứu KHÔNG kèm cue đề tài (đường đi thông thường, chưa từng
    hỏng) vẫn phải route đúng như trước — bản vá không đụng nhánh clinical_case gốc."""

    def test_ca_cap_cuu_khong_co_tu_protocol(self):
        r = route("Bệnh nhân đau ngực dữ dội, cần chuyển cấp cứu ngay không?")
        self.assertEqual(r.kind, "clinical_case", r)
        self.assertEqual(r.target, CLINICAL_ORCHESTRATOR, r)


if __name__ == "__main__":
    unittest.main()
