#!/usr/bin/env python3
"""Hồi quy cho skill nhạc trưởng ChatGPT/Codex."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
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


def load_catalog_module():
    path = ROUTER / "scripts/build_catalog.py"
    module_name = "_router_catalog_test"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
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

    def test_catalog_falls_back_to_enabled_config_and_real_cache(self):
        module = load_catalog_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_path = root / "config.toml"
            cache_root = root / "cache"
            config_lines: list[str] = []
            for plugin_id in module.PLUGIN_IDS:
                name, marketplace = plugin_id.split("@", 1)
                config_lines.extend([f'[plugins."{plugin_id}"]', "enabled = true", ""])
                version = "local" if name in {
                    "openmed-skills", "medsci-project", "aipoch-medical-research",
                    "meta-pipe", "pubmed-search",
                } else "1.0.0"
                (cache_root / marketplace / name / version).mkdir(parents=True)
            config_path.write_text("\n".join(config_lines), encoding="utf-8")

            records = module.read_configured_plugins_from_cache(config_path, cache_root)

        self.assertEqual({record.plugin_id for record in records}, set(module.PLUGIN_IDS))
        self.assertEqual(len(records), 9)

    def test_catalog_falls_back_to_claude_code_cache_when_codex_absent(self):
        """05/09/2026: máy chạy phiên Claude Code có thể KHÔNG có Codex ở bất kỳ dạng
        nào (đã xác nhận trên Cloud: không ~/.codex/config.toml, không ~/.codex/plugins/
        cache, không lệnh `codex`) — trước bản vá này, cả hai tầng dự phòng phía trên
        đều RuntimeError nên build_catalog.py không bao giờ tự làm mới được ở đó, và
        catalog bị lệch thật (đo được: academic-research-skills 17→4,
        pubmed-search 31→10 — hai lần cắt tỉa thật chưa từng tới catalog)."""
        module = load_catalog_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installed_path = root / "installed_plugins.json"
            cache_root = root / "claude-cache"
            payload = {"version": 1, "plugins": {}}
            for plugin_id in module.PLUGIN_IDS:
                name, marketplace = plugin_id.split("@", 1)
                version = "9.9.9"
                install_path = cache_root / marketplace / name / version
                install_path.mkdir(parents=True)
                (install_path / "SKILL.md").write_text(
                    f"---\nname: {name}-mau\ndescription: mau\n---\n", encoding="utf-8"
                )
                payload["plugins"][plugin_id] = [
                    {"scope": "user", "installPath": str(install_path), "version": version}
                ]
            installed_path.write_text(json.dumps(payload), encoding="utf-8")

            records = module.read_claude_code_cache_plugins(installed_path)

            # PHẢI kiểm is_dir() TRONG khi thư mục tạm còn sống — kiểm sau khi
            # TemporaryDirectory đã dọn sẽ luôn False bất kể hàm đúng hay sai.
            self.assertTrue(all(record.source_path.is_dir() for record in records))

        self.assertEqual({record.plugin_id for record in records}, set(module.PLUGIN_IDS))
        self.assertEqual(len(records), 9)


if __name__ == "__main__":
    unittest.main()
