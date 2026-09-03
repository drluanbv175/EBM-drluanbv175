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


class TestBioResearchDefaultRoots(unittest.TestCase):
    """★ Phát hiện #10 của Workflow đối kháng đa-agent 2026-09-03: đường dò cache
    mặc định của provider `bio-research` từng là "claude-cowork/bio-research" —
    không khớp khuôn marketplace/plugin thật nào (grep xác nhận: chuỗi
    "claude-cowork" chỉ xuất hiện ở đúng 2 dòng trong worker_inventory.py, không
    đâu khác trong repo hay trong known_marketplaces.json/installed_plugins.json
    thật). Xác minh qua WebFetch 03/09/2026: 3 unit registry của provider này
    (nextflow-development · single-cell-rna-qc · scvi-tools) khớp CHÍNH XÁC 3
    thư mục skill riêng biệt trong marketplace THẬT `anthropics/life-sciences`."""

    def test_bio_research_default_roots_point_to_life_sciences_not_claude_cowork(self):
        inv = wi.WorkerInventory()
        roots = inv.provider_roots["bio-research"]
        self.assertTrue(roots, "provider bio-research phải có ít nhất 1 root")
        for root in roots:
            self.assertNotIn("claude-cowork", root.parts,
                             f"đường dò cũ đã sai vẫn còn sót: {root}")
            self.assertEqual(root.name, "life-sciences", root)
        # Đúng 2 root — một cho mỗi kho cache (Claude + Codex), khớp khuôn duong().
        self.assertEqual(len(roots), 2, roots)

    def test_bio_research_skills_found_recursively_under_life_sciences(self):
        """Mô phỏng CẤU TRÚC ĐÃ VÁ (chưa quan sát được trên máy thật vì plugin
        này chưa cài ở đâu — xem sync/plugin-manifest.json): mỗi skill nằm
        trong một thư mục con tuỳ ý dưới marketplace life-sciences, có thể lồng
        thêm cấp phiên bản. rglob() phải tìm thấy CẢ BA bất kể độ sâu/tên thư
        mục con cụ thể — đây chính là lý do chỉ cần trỏ đúng CẤP MARKETPLACE,
        không cần biết/đoán tên thư mục từng skill."""
        with tempfile.TemporaryDirectory() as td:
            life_sciences = Path(td) / "life-sciences"
            for skill in ("nextflow-development", "single-cell-rna-qc", "scvi-tools"):
                d = life_sciences / skill / "1.0.0"
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"---\nname: {skill}\n---\n", encoding="utf-8")
            inv = wi.WorkerInventory(provider_roots={"bio-research": (life_sciences,)})
            for skill in ("nextflow-development", "single-cell-rna-qc", "scvi-tools"):
                found = inv.locate(_spec("bio-research", skill))
                self.assertTrue(found.available, f"{skill}: {found.reason}")


if __name__ == "__main__":
    unittest.main()
