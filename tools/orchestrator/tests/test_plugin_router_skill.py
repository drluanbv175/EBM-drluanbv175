#!/usr/bin/env python3
"""Hồi quy cho skill nhạc trưởng ChatGPT/Codex."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROUTER = ROOT / "sync/skills/plugin-router-chatgpt"


def load_router_module():
    path = ROUTER / "scripts/route_skill.py"
    spec = importlib.util.spec_from_file_location("_router_skill_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestPluginRouterSkill(unittest.TestCase):
    def test_router_source_is_complete(self):
        for relative in (
            "SKILL.md",
            "agents/openai.yaml",
            "references/governance.md",
            "references/plugin-catalog.md",
            "references/plugin-catalog.json",
            "scripts/build_catalog.py",
            "scripts/route_skill.py",
        ):
            self.assertTrue((ROUTER / relative).is_file(), f"thiếu {relative}")

    def test_catalog_has_all_nine_plugin_families(self):
        data = json.loads((ROUTER / "references/plugin-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["plugins"]), 9)
        self.assertGreaterEqual(len(data["skills"]), 100)

    def test_mendelian_request_prefers_specialized_aipoch_skill(self):
        module = load_router_module()
        data = json.loads((ROUTER / "references/plugin-catalog.json").read_text(encoding="utf-8"))
        ranked = module.rank(
            "Thiết kế nghiên cứu Mendelian randomization về đái tháo đường",
            data,
            5,
        )
        self.assertTrue(ranked)
        self.assertEqual(ranked[0]["plugin"], "aipoch-medical-research")
        self.assertEqual(ranked[0]["skill"], "mendelian-randomization-protocol-designer")


if __name__ == "__main__":
    unittest.main()
