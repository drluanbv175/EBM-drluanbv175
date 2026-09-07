#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy: build_ban_doc_chung_cu.py::khoi_do_phu() phải tìm được
tools/tuyen_bo_do_phu.py bất kể chạy từ BẢN NÀO trong hai bản byte-identical
của chính file này (`tools/` gốc repo và
`sync/skills/cap-nhat-chung-cu-y-khoa/tools/`).

Phát hiện thật: bản đọc `SuyTim_HFnrEF_20260907_ban-doc.html` (sinh bằng bản
mirror) có nguyên chuỗi lỗi Python
"[CHƯA SINH ĐƯỢC TUYÊN BỐ ĐỘ PHỦ: [Errno 2] No such file or directory: '…/
sync/skills/cap-nhat-chung-cu-y-khoa/tools/tuyen_bo_do_phu.py' — chạy
python3 tools/tuyen_bo_do_phu.py]" ngay trong footer — nơi bác sĩ đọc trực
tiếp. Nguyên nhân: `Path(__file__).resolve().parents[1] / "tools" / ...`
đúng CHO BẢN GỐC (parents[1] = gốc repo) nhưng SAI cho bản mirror (parents[1]
= sync/skills/cap-nhat-chung-cu-y-khoa/, một cấp KHÔNG chứa tools/tuyen_bo_
do_phu.py — tệp đó chỉ tồn tại đúng MỘT bản, ở tools/ gốc repo).

Nguyên tắc viết test: gọi THẲNG _tim_goc_repo()/khoi_do_phu(), không grep
chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ban_doc_chung_cu as bd  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
MIRROR_TOOLS_DIR = (REPO_ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa"
                     / "tools")


class TestTimGocRepoDocLapDoSau(unittest.TestCase):
    """★★ Ca chính — _tim_goc_repo() phải trả về CÙNG một gốc dù xuất phát từ
    độ sâu khác nhau (giả lập hai vị trí của build_ban_doc_chung_cu.py)."""

    def test_tu_ban_goc_ra_dung_goc_repo(self):
        goc = bd._tim_goc_repo(REPO_ROOT / "tools" / "build_ban_doc_chung_cu.py")
        self.assertEqual(goc, REPO_ROOT)

    def test_tu_ban_mirror_van_ra_dung_goc_repo(self):
        goc = bd._tim_goc_repo(MIRROR_TOOLS_DIR / "build_ban_doc_chung_cu.py")
        self.assertEqual(goc, REPO_ROOT)

    def test_tuyen_bo_do_phu_thuc_su_ton_tai_o_duong_da_tinh(self):
        goc = bd._tim_goc_repo(MIRROR_TOOLS_DIR / "build_ban_doc_chung_cu.py")
        self.assertTrue((goc / "tools" / "tuyen_bo_do_phu.py").exists())


class TestKhoiDoPhuKhongLoiKhiChayTuBanMirror(unittest.TestCase):
    """Đối chứng trực tiếp harm: khoi_do_phu() gọi từ THƯ MỤC BẢN MIRROR
    không được trả về chuỗi lỗi Python."""

    def test_khong_con_chuoi_loi_khi_module_o_thu_muc_mirror(self):
        import importlib.util as ilu
        spec = ilu.spec_from_file_location(
            "bd_mirror", MIRROR_TOOLS_DIR / "build_ban_doc_chung_cu.py")
        m = ilu.module_from_spec(spec)
        sys.modules["bd_mirror"] = m
        spec.loader.exec_module(m)
        khoi = m.khoi_do_phu()
        self.assertNotIn("CHƯA SINH ĐƯỢC", khoi)
        self.assertNotIn("Errno 2", khoi)
        self.assertIn("ĐỘ PHỦ NGUỒN", khoi)


class TestDongBoHaiBanTrackGit(unittest.TestCase):
    """Đối chứng đồng bộ: tools/ và sync/skills/cap-nhat-chung-cu-y-khoa/tools/
    phải byte-identical sau bản vá."""

    def test_hai_ban_byte_identical(self):
        a = Path(__file__).resolve().parent / "build_ban_doc_chung_cu.py"
        b = MIRROR_TOOLS_DIR / "build_ban_doc_chung_cu.py"
        self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
