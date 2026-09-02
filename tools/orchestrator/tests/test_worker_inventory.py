#!/usr/bin/env python3
"""Hồi quy cho WorkerInventory — tách «plugin chưa cài trên máy này» khỏi «binding treo».

Vì sao có (01/09/2026, BH85): cổng verify_plugin_orchestration đỏ ở MỌI máy không phải
Mac (Windows · cloud) vì ~/.codex/plugins/cache thiếu meta-pipe/pubmed-search — thứ mà
sổ khai sync/plugin-manifest.json ghi rõ chỉ cần ở Mac. Thiếu nguyên liệu bị báo như
binding hỏng (BH08).
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator import worker_inventory as wi  # noqa: E402
from orchestrator.plugin_ownership import WorkerSpec  # noqa: E402


def _spec(provider: str, unit: str) -> WorkerSpec:
    return WorkerSpec(provider=provider, unit=unit, mode="worker")


class TestWorkerInventory(unittest.TestCase):
    def test_ba_trang_thai_tach_bach(self):
        with tempfile.TemporaryDirectory() as td:
            co = Path(td) / "co-plugin"
            (co / "skill-a").mkdir(parents=True)
            (co / "skill-a/SKILL.md").write_text("---\nname: skill-a\n---\n", encoding="utf-8")
            inv = wi.WorkerInventory(provider_roots={
                "p-co": (co,),
                "p-chua-cai": (Path(td) / "khong-ton-tai",),
            })
            self.assertTrue(inv.locate(_spec("p-co", "skill-a")).available)
            thieu = inv.locate(_spec("p-co", "skill-b"))
            self.assertFalse(thieu.available)
            self.assertEqual(thieu.reason, wi.LY_DO_THIEU_SKILL)
            chua = inv.locate(_spec("p-chua-cai", "bat-ky"))
            self.assertFalse(chua.available)
            self.assertEqual(chua.reason, wi.LY_DO_CHUA_CAI)
            la = inv.locate(_spec("p-khong-khai", "x"))
            self.assertEqual(la.reason, wi.LY_DO_KHONG_QUY_TAC)

    def test_cong_phan_loai_chua_cai_la_trang_khong_phai_fail(self):
        import importlib.util
        path = Path(__file__).resolve().parents[2] / "verify_plugin_orchestration.py"
        spec = importlib.util.spec_from_file_location("_vpo_test", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        dat = wi.WorkerAvailability("a", True, "x", "SKILL.md khả dụng")
        chua = wi.WorkerAvailability("b", False, reason=wi.LY_DO_CHUA_CAI)
        thieu = wi.WorkerAvailability("c", False, reason=wi.LY_DO_THIEU_SKILL)
        la = wi.WorkerAvailability("d", False, reason=wi.LY_DO_KHONG_QUY_TAC)
        self.assertEqual(mod.phan_loai_binding(dat), "dat")
        self.assertEqual(mod.phan_loai_binding(chua), "chua_cai")
        self.assertEqual(mod.phan_loai_binding(thieu), "loi")
        self.assertEqual(mod.phan_loai_binding(la), "loi")


if __name__ == "__main__":
    unittest.main()
