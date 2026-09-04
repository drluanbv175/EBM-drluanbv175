#!/usr/bin/env python3
"""Hồi quy phát hiện #39 của Workflow đối kháng đa-agent vòng 2 (2026-09-04).

`PluginOwnershipRegistry.capability_for()` chỉ khớp một capability qua HAI
đường: `intent_kinds` (intent nhiều từ, kind != "single_task") hoặc
`entry_agents` (intent single_task). Registry sống có 2 capability —
`software_delivery` và `bioinformatics_specialist` — khai cả `owner` lẫn
`workers` đầy đủ nhưng KHÔNG khai `intent_kinds`/`entry_agents` nào: chúng
vĩnh viễn không thể được `capability_for()`/`resolve_for_intent()` tự động
tìm thấy, kể cả khi bác sĩ gõ đúng ý định nhắm tới worker của chúng — con
đường DUY NHẤT chạm tới là escape hatch nội bộ `--resolve-capability
<id>`. `validate()` trước bản vá không có luật nào bắt việc này, nên một
capability MỚI phạm cùng lỗi (quên khai cả hai trường vì sơ suất, khác
với hai capability hiện tại vốn CỐ Ý chỉ gọi tay) sẽ lọt qua mọi cổng
kiểm mà không một cảnh báo nào.

Vá: thêm `CapabilitySpec.manual_only` (mặc định False, đọc từ JSON) + một
luật `validate()` mới báo lỗi cho capability rỗng cả hai trường khớp intent
mà KHÔNG khai `manual_only: true`. Registry sống đã đánh dấu 2 capability
hiện tại là `manual_only: true` kèm lý do — chúng tiếp tục hoạt động y hệt
qua `--resolve-capability`, chỉ khác là ý định "chỉ gọi tay" nay tường minh
thay vì trông giống một lỗi quên khai.

Nguyên tắc viết test: kiểm HÀNH VI của validate()/capability_for() bằng
registry dựng tay, không grep chuỗi trong JSON/mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator.plugin_ownership import (  # noqa: E402
    CapabilitySpec,
    PluginOwnershipRegistry,
)

_PROVIDERS = {
    "local-agent": {"kind": "local", "priority": 100, "may_own": True},
    "local-runtime": {"kind": "local", "priority": 95, "may_own": True},
    "some-plugin": {"kind": "plugin", "priority": 10, "may_own": False},
}

_GLOBAL_RULES_OK = {
    "single_owner_per_capability": True,
    "plugins_are_workers_only": True,
    "plugin_may_release_human_gate": False,
}


def _registry(capabilities: dict[str, CapabilitySpec]) -> PluginOwnershipRegistry:
    return PluginOwnershipRegistry(
        providers=dict(_PROVIDERS),
        capabilities=capabilities,
        global_rules=dict(_GLOBAL_RULES_OK),
        canonical_research_hard_gates=(),
        policy_id="TEST-POLICY",
    )


def _cap(capability_id: str, *, manual_only: bool = False,
         intent_kinds: tuple[str, ...] = (),
         entry_agents: tuple[str, ...] = ()) -> CapabilitySpec:
    return CapabilitySpec(
        capability_id=capability_id,
        risk="medium",
        owner_provider="local-runtime",
        owner_unit="some-owner",
        intent_kinds=intent_kinds,
        entry_agents=entry_agents,
        manual_only=manual_only,
    )


class TestManualOnlyParsing(unittest.TestCase):
    def test_from_dict_defaults_to_false(self):
        spec = CapabilitySpec.from_dict("x", {"owner": {"provider": "p", "unit": "u"}})
        self.assertFalse(spec.manual_only)

    def test_from_dict_reads_true(self):
        spec = CapabilitySpec.from_dict(
            "x", {"owner": {"provider": "p", "unit": "u"}, "manual_only": True}
        )
        self.assertTrue(spec.manual_only)


class TestValidateCatchesUnreachableCapability(unittest.TestCase):
    def test_khong_intent_khong_entry_khong_manual_only_bi_bao_loi(self):
        """★★ Ca chính: capability rỗng cả hai trường khớp intent, KHÔNG khai
        manual_only — validate() phải báo lỗi (trước bản vá: im lặng)."""
        reg = _registry({"orphan_capability": _cap("orphan_capability")})
        errors = reg.validate()
        matches = [e for e in errors if "orphan_capability" in e and "rong ca intent_kinds" in e]
        self.assertEqual(len(matches), 1, errors)

    def test_manual_only_true_khong_bi_bao_loi(self):
        """Đối chứng: cùng cấu hình rỗng nhưng khai manual_only:true — KHÔNG
        báo lỗi (đây là ý định thật của software_delivery/bioinformatics_specialist)."""
        reg = _registry({"deliberately_manual": _cap("deliberately_manual", manual_only=True)})
        errors = reg.validate()
        matches = [e for e in errors if "rong ca intent_kinds" in e]
        self.assertEqual(matches, [])

    def test_co_intent_kinds_khong_bi_bao_loi(self):
        reg = _registry({"c": _cap("c", intent_kinds=("some_topic",))})
        errors = reg.validate()
        self.assertEqual([e for e in errors if "rong ca intent_kinds" in e], [])

    def test_co_entry_agents_khong_bi_bao_loi(self):
        reg = _registry({"c": _cap("c", entry_agents=("some-agent",))})
        errors = reg.validate()
        self.assertEqual([e for e in errors if "rong ca intent_kinds" in e], [])

    def test_khong_lan_sang_capability_khac(self):
        """Một capability hợp lệ (có intent_kinds) đứng cạnh một capability lỗi
        không được lây lỗi hoặc bị bỏ sót lỗi của capability kia."""
        reg = _registry({
            "hop_le": _cap("hop_le", intent_kinds=("topic_a",)),
            "loi": _cap("loi"),
        })
        errors = reg.validate()
        flagged = [e for e in errors if "rong ca intent_kinds" in e]
        self.assertEqual(len(flagged), 1)
        self.assertIn("loi", flagged[0])


class TestCapabilityForCannotReachManualOnly(unittest.TestCase):
    """Xác nhận ĐÚNG cái lỗ hổng mà manual_only mô tả: dù bác sĩ gõ đúng
    entry_agent/intent của một capability manual_only, capability_for()
    KHÔNG BAO GIỜ trả về nó — validate() chỉ CẢNH BÁO cấu hình bất khả thi,
    không tự thêm đường định tuyến (đúng luật owner rõ ràng, không suy đoán)."""

    def test_manual_only_khong_the_khop_qua_capability_for(self):
        reg = _registry({"manual": _cap("manual", manual_only=True)})
        # Không có intent_kinds/entry_agents nào để "gõ đúng" tới — thử vài
        # giá trị hợp lý đại diện cho ý định thật của bác sĩ, tất cả đều None.
        self.assertIsNone(reg.capability_for("software_delivery", "manual"))
        self.assertIsNone(reg.capability_for("single_task", "manual"))


class TestLiveRegistryStillPasses(unittest.TestCase):
    """Registry SỐNG (plugin_ownership_registry.json) phải sạch luật mới —
    2 capability manual_only hiện có phải đã được đánh dấu đúng."""

    def test_live_registry_validate_khong_co_loi_rong_intent(self):
        reg = PluginOwnershipRegistry.load()
        errors = reg.validate()
        matches = [e for e in errors if "rong ca intent_kinds" in e]
        self.assertEqual(matches, [], errors)

    def test_software_delivery_va_bioinformatics_da_danh_dau_manual_only(self):
        reg = PluginOwnershipRegistry.load()
        self.assertTrue(reg.capabilities["software_delivery"].manual_only)
        self.assertTrue(reg.capabilities["bioinformatics_specialist"].manual_only)


if __name__ == "__main__":
    unittest.main()
