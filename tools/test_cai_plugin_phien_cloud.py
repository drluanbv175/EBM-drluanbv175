#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho sinh_manifest() trong cai_plugin_phien_cloud.py — ngoại tuyến.

Bối cảnh (05/09/2026): meta-pipe và pubmed-search hoàn toàn KHÔNG xuất hiện trong danh
sách skill thật của Claude Code (xác nhận trực tiếp trên phiên Cloud: 0/14 và 0/10, dù
cache có đủ file) trong khi 7 plugin khác đều bình thường. Nguyên nhân xác minh qua tài
liệu Claude Code chính thức: `sinh_manifest()` ghi CẢ HAI `.claude-plugin/plugin.json`
VÀ `.claude-plugin/marketplace.json` cùng khai `skills`, mà marketplace.json còn đặt
`strict: false` — theo tài liệu, `strict: false` nghĩa "mục marketplace là ĐỊNH NGHĨA
DUY NHẤT", và một `plugin.json` cùng thư mục CŨNG khai component là xung đột khiến
**CẢ PLUGIN KHÔNG NẠP ĐƯỢC**, im lặng. `aipoch-medical-research` — plugin DUY NHẤT
trong kho KHÔNG có plugin.json — là bằng chứng đối chứng: nó hoạt động đúng.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`):
  (1) chỉ kiểm HÀNH VI bằng cách gọi vào mã đang sống, không đếm chuỗi trong file;
  (2) mỗi ca gắn với một rủi ro THẬT đã nêu trong docstring của công cụ;
  (3) nhanh và ngoại tuyến.

Chạy:  python3 tools/test_cai_plugin_phien_cloud.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "_cai_plugin_cloud_test", Path(__file__).resolve().parent / "cai_plugin_phien_cloud.py"
)
CPC = importlib.util.module_from_spec(_spec)
sys.modules["_cai_plugin_cloud_test"] = CPC
_spec.loader.exec_module(CPC)


class TestSinhManifestKhongXungDot(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.kho = Path(self._tmp.name) / "kho-mau"
        for ten in ("skill-mot", "skill-hai"):
            d = self.kho / ten
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(f"---\nname: {ten}\n---\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_khong_sinh_plugin_json(self) -> None:
        """CHỈ marketplace.json được sinh — không có plugin.json nào cả, khuôn theo
        đúng aipoch-medical-research (plugin duy nhất đang hoạt động đúng)."""
        n = CPC.sinh_manifest(self.kho, "mau-marketplace", "mau-plugin", "mô tả mẫu", None)
        self.assertEqual(n, 2)
        self.assertFalse((self.kho / ".claude-plugin" / "plugin.json").exists(),
                         "plugin.json không được tồn tại — nó xung đột với strict:false")
        self.assertTrue((self.kho / ".claude-plugin" / "marketplace.json").is_file())

    def test_xoa_plugin_json_cu_neu_con_sot_tu_ban_truoc(self) -> None:
        """Ca thật: 2 plugin đã cài từ TRƯỚC bản vá này còn để lại plugin.json cũ.
        Gọi lại sinh_manifest() phải DỌN nốt file cũ, không chỉ bỏ qua không ghi thêm."""
        (self.kho / ".claude-plugin").mkdir(parents=True)
        (self.kho / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "mau-plugin", "skills": ["./skill-mot"]}), encoding="utf-8"
        )
        CPC.sinh_manifest(self.kho, "mau-marketplace", "mau-plugin", "mô tả mẫu", None)
        self.assertFalse((self.kho / ".claude-plugin" / "plugin.json").exists())

    def test_marketplace_json_van_giu_strict_false_va_du_skill(self) -> None:
        CPC.sinh_manifest(self.kho, "mau-marketplace", "mau-plugin", "mô tả mẫu", None)
        data = json.loads((self.kho / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        entry = data["plugins"][0]
        self.assertEqual(entry["strict"], False)
        self.assertEqual(set(entry["skills"]), {"./skill-mot", "./skill-hai"})

    def test_giu_skill_van_loc_dung_nhu_truoc(self) -> None:
        n = CPC.sinh_manifest(self.kho, "mau-marketplace", "mau-plugin", "mô tả mẫu",
                              giu_skill={"skill-mot"})
        self.assertEqual(n, 1)
        data = json.loads((self.kho / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(data["plugins"][0]["skills"], ["./skill-mot"])


if __name__ == "__main__":
    unittest.main()
