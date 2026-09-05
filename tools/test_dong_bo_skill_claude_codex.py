#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `ensure_link()` trong dong_bo_skill_claude_codex.py — ngoại tuyến.

Bối cảnh (2026-09-05): `verify_plugin_orchestration.py` phát hiện junction
`~/.claude/skills/plugin-router-chatgpt` và `~/.codex/skills/plugin-router-chatgpt`
trỏ vào một worktree tạm (`trusting-gates-5c3907`) thay vì nguồn canonical
`sync/skills/`. Chạy `--ap-dung` KHÔNG sửa được — nhánh XUNG_DOT (liên kết đã tồn
tại nhưng trỏ sai) chỉ BÁO CÁO, chưa từng gọi `LK.go()`/`LK.tao()` để relink dù
`apply=True`. Đây là lỗ hổng trong chính công cụ tự sửa chữa: một junction từng
đúng rồi lệch do nguồn bị dời/xoá (đúng kiểu worktree bị dọn) sẽ VĨNH VIỄN không
tự phục hồi được, bất kể chạy `--ap-dung` bao nhiêu lần.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`):
  (1) chỉ kiểm HÀNH VI bằng cách gọi vào mã đang sống, không đếm chuỗi trong file;
  (2) mỗi ca gắn với một rủi ro THẬT đã nêu trong docstring của công cụ;
  (3) nhanh và ngoại tuyến.

Chạy:  python3 tools/test_dong_bo_skill_claude_codex.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dong_bo_skill_claude_codex as DB  # noqa: E402
import lien_ket_da_nen as LK  # noqa: E402


class TestEnsureLinkSuaJunctionTroSai(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.nguon_dung = root / "sync-skills" / "mot-skill"
        self.nguon_sai = root / "worktree-cu" / "mot-skill"
        self.destination = root / "runtime"
        for nguon in (self.nguon_dung, self.nguon_sai):
            nguon.mkdir(parents=True)
            (nguon / "SKILL.md").write_text("---\nname: mot-skill\n---\n", encoding="utf-8")
        self.destination.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_khong_apply_chi_bao_cao_khong_sua(self) -> None:
        LK.tao(self.nguon_sai, self.destination / self.nguon_dung.name)

        ket_qua = DB.ensure_link(self.nguon_dung, self.destination, apply=False)

        self.assertEqual(ket_qua.status, "XUNG_DOT")
        self.assertTrue(LK.tro_dung(self.destination / self.nguon_dung.name, self.nguon_sai))

    def test_apply_sua_lai_junction_tro_sai_ve_dung_nguon(self) -> None:
        # Mô phỏng đúng ca thật: junction từng nối đúng vào một worktree, rồi
        # worktree đó bị dọn/đổi tên nên junction còn lại trỏ sai.
        LK.tao(self.nguon_sai, self.destination / self.nguon_dung.name)
        target = self.destination / self.nguon_dung.name
        self.assertTrue(LK.tro_dung(target, self.nguon_sai), "fixture phải bắt đầu ở trạng thái trỏ sai")

        ket_qua = DB.ensure_link(self.nguon_dung, self.destination, apply=True)

        self.assertEqual(ket_qua.status, "DA_NOI")
        self.assertTrue(LK.la_lien_ket(target))
        self.assertTrue(
            LK.tro_dung(target, self.nguon_dung),
            "sau --ap-dung junction phải trỏ về nguồn canonical, không còn trỏ worktree cũ",
        )

    def test_apply_khong_dong_gi_khi_da_khop(self) -> None:
        LK.tao(self.nguon_dung, self.destination / self.nguon_dung.name)

        ket_qua = DB.ensure_link(self.nguon_dung, self.destination, apply=True)

        self.assertEqual(ket_qua.status, "KHOP")


if __name__ == "__main__":
    unittest.main()
