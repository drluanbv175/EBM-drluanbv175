#!/usr/bin/env python3
"""Hồi quy phát hiện HIGH của Workflow đối kháng đa-agent 2026-09-04 (task #56):
`plugin_ownership.py::resolve_for_intent()` chặn NHẦM mọi request kind `cong_cu`
ngay trong `Orchestrator.handle()`, TRƯỚC KHI `_plan()` chạy tới nhánh đã viết
đúng (`if kind == "cong_cu": return [GUARDRAIL_STEP]`).

Cơ chế lỗi: `resolve_for_intent()` chỉ có MỘT nhánh cứu (`kind == "single_task"
and entry_agent`) cho request không khớp capability nào trong registry. `cong_cu`
(chủ là LỆNH/SKILL/công cụ — xem `VIEC_CONG_CU` trong intent.py, thêm ở BH88)
không khớp nhánh đó, nên rơi thẳng xuống `BLOCKED_UNKNOWN_CAPABILITY`. Trong
`handle()`, `if plugin_decision.status.startswith("BLOCKED"): ... return
self._finish(...)` đóng session NGAY sau bước định tuyến plugin — session
chưa từng chạy tới `_plan()`/`_run_step()`. Nghĩa là CẢ BA mục trong
`VIEC_CONG_CU` (bảng 8 giác quan, tra ICD-10, đào tạo slide) bị chặn nhầm
100%, dù hệ biết rõ chủ của từng việc — đúng câu CLAUDE.md đã ghi về BH88:
"unknown là câu trả lời SAI SỰ THẬT về việc mà hệ biết rõ chủ", chỉ khác lần
này lỗi nằm ở TẦNG SAU (plugin ownership), không phải tầng định tuyến intent.

Nguyên tắc viết test: gọi THẲNG `resolve_for_intent()` và
`Orchestrator.handle()` với các câu THẬT trong `VIEC_CONG_CU`, không grep
chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator.intent import VIEC_CONG_CU, route  # noqa: E402
from orchestrator.orchestrator import Orchestrator  # noqa: E402
from orchestrator.plugin_ownership import PluginOwnershipRegistry  # noqa: E402


class TestResolveForIntentCongCuUnit(unittest.TestCase):
    """Đơn vị — thẳng vào `resolve_for_intent()`, không qua Orchestrator."""

    def setUp(self):
        self.plugins = PluginOwnershipRegistry.load()

    def test_cong_cu_khong_bi_block(self):
        decision = self.plugins.resolve_for_intent("cong_cu", "tools/tu_de_xuat_viec.py")
        self.assertFalse(decision.status.startswith("BLOCKED"), decision.status)

    def test_cong_cu_tra_dung_owner_unit_la_ten_cong_cu(self):
        decision = self.plugins.resolve_for_intent("cong_cu", "/tra-ma-icd10")
        self.assertEqual(decision.owner_unit, "/tra-ma-icd10")

    def test_cong_cu_khong_co_worker_treo(self):
        """`_run_step` tra registry AGENT — owner của cong_cu KHÔNG được đi vào
        đường đó (workers rỗng nghĩa là không có worker plugin nào phải xác
        minh tồn tại qua worker_inventory)."""
        decision = self.plugins.resolve_for_intent("cong_cu", "dao-tao-slide-tai-lieu-y-khoa")
        self.assertEqual(decision.workers, ())

    def test_cong_cu_khong_co_entry_agent_van_khong_crash(self):
        """entry_agent rỗng (lý thuyết, không xảy ra trong route() thật) không
        được làm resolve_for_intent() ném lỗi — rơi về BLOCKED an toàn."""
        decision = self.plugins.resolve_for_intent("cong_cu", "")
        self.assertTrue(decision.status.startswith("BLOCKED"))

    def test_khong_lam_hong_nhanh_single_task_da_dung_tu_truoc(self):
        """★★ Đối chứng bắt buộc — nhánh single_task (đã đúng từ trước) không
        được ảnh hưởng bởi việc thêm nhánh cong_cu."""
        decision = self.plugins.resolve_for_intent("single_task", "sang-loc-co-do")
        self.assertEqual(decision.status, "READY_LOCAL_SPECIALIST_ONLY")
        self.assertEqual(decision.owner_provider, "local-agent")

    def test_khong_lam_hong_nhanh_capability_that_da_dung_tu_truoc(self):
        decision = self.plugins.resolve_for_intent("research_topic", "dieu-phoi-nghien-cuu")
        self.assertEqual(decision.status, "READY_WITH_OWNER")

    def test_kind_la_thu_khong_ton_tai_van_block_dung(self):
        """Đối chứng — một kind lạ hoàn toàn (không phải cong_cu/single_task)
        vẫn phải BLOCKED như cũ, không bị nới lỏng oan."""
        decision = self.plugins.resolve_for_intent("khong-ton-tai", "gi-do")
        self.assertTrue(decision.status.startswith("BLOCKED"))


class TestOrchestratorHandleCongCuEndToEnd(unittest.TestCase):
    """★★ Tích hợp — chạy qua ĐÚNG con đường bác sĩ gõ câu thật, dùng cả 3 mục
    trong VIEC_CONG_CU (BH88) làm ca thật, không phải chuỗi tự bịa."""

    def test_route_nhan_dung_kind_cong_cu_cho_ca_3_muc(self):
        """Tiền điều kiện — xác nhận route() vẫn phân loại đúng `cong_cu`
        trước khi kiểm tầng plugin ownership phía sau nó."""
        for kws, target, _note in VIEC_CONG_CU:
            with self.subTest(target=target):
                result = route(kws[0])
                self.assertEqual(result.kind, "cong_cu")
                self.assertEqual(result.target, target)

    def test_ca_3_muc_cong_cu_khong_con_bi_chan(self):
        for kws, target, note in VIEC_CONG_CU:
            with self.subTest(target=target, note=note):
                session = Orchestrator().handle(kws[0])
                self.assertEqual(session.kind, "cong_cu")
                self.assertFalse(
                    session.status.startswith("blocked"),
                    f"'{kws[0]}' (chủ: {target}) vẫn bị chặn: {session.status}",
                )

    def test_bang_8_giac_quan_chay_toi_guardrail_that_su(self):
        """★★ Ca chính đã tái hiện được lỗi — trước bản vá, dấu vết (trace)
        rỗng vì session đóng ngay sau bước định tuyến plugin."""
        session = Orchestrator().handle("còn gì để hoàn thiện hệ thống?")
        self.assertEqual(session.kind, "cong_cu")
        self.assertEqual(session.entry_agent, "tools/tu_de_xuat_viec.py")
        self.assertGreaterEqual(len(session.trace), 1)
        self.assertEqual(session.trace[-1]["agent"], "tham-dinh-dau-ra")
        self.assertIn("released", session.status)

    def test_khong_dung_agent_gia_cho_ten_cong_cu(self):
        """`_plan()` cố ý KHÔNG dựng bước agent cho cong_cu (comment tại chỗ:
        "ex.execute tra registry AGENT, tên lệnh sẽ thành tham chiếu treo").
        Xác nhận trace KHÔNG chứa một agent trùng tên với tool path/lệnh."""
        session = Orchestrator().handle("tra mã ICD-10 cho viêm phổi")
        agents_in_trace = [row.get("agent") for row in session.trace]
        self.assertNotIn("/tra-ma-icd10", agents_in_trace)

    def test_single_task_van_hoat_dong_dung_sau_khi_them_nhanh_cong_cu(self):
        """★★ Đối chứng bắt buộc — một câu ca lâm sàng thật (kind khác hẳn
        cong_cu) vẫn phải chạy đúng như trước, không bị lỗi lan sang."""
        session = Orchestrator().handle(
            "Bệnh nhân đau ngực dữ dội, khó thở, vã mồ hôi — cần xử trí gì ngay?"
        )
        self.assertNotEqual(session.kind, "cong_cu")
        self.assertFalse(session.status.startswith("blocked · chưa xác định quyền sở hữu plugin"))


if __name__ == "__main__":
    unittest.main()
