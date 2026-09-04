#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy 2 phát hiện của Workflow đối kháng đa-agent vòng 2 (2026-09-04) trong
`apply_vi.py` — cùng một hậu quả (đè/bỏ qua hàng rào bảo vệ mô tả tự viết của
bác sĩ), hai cơ chế khác nhau:

  #1 (MEDIUM) — `VN_CHARS` (dùng chung với extract_catalog.py) chỉ nhận diện
     ký tự CÓ DẤU. Một mô tả tiếng Việt KHÔNG DẤU do bác sĩ tự gõ tay (cách gõ
     nhanh phổ biến, và CHÍNH `bo_dau.py` trong thư mục này sinh ra unaccented
     Vietnamese có chủ đích khi font không vẽ được dấu) không được luật
     giữ-bản-tự-viết nhận ra, nên `apply_vi.py` ĐÈ bản không dấu bằng bản dịch
     từ điển — mất nội dung gốc không một cảnh báo. Tái hiện sống: chạy
     process() trên fixture có description="Dat lich tai kham cho benh nhan
     sau moi ca kham ngoai tru" (không dấu) → trước bản vá trả "applied" và
     ghi đè; sau bản vá trả "giữ-bản-việt-tự-viết", nội dung giữ nguyên.

  #2 (nghiêm trọng hơn dự kiến khi điều tra) — `trong_repo_git()` đi ngược từ
     ĐƯỜNG DẪN CHO TRƯỚC (không resolve symlink) để tìm `.git`. Nhưng
     `~/.claude/skills/<skill>/SKILL.md` — 43 skill của bác sĩ, đo thật
     2026-09-04 — là SYMLINK trỏ thẳng vào `sync/skills/<skill>/SKILL.md`
     (repo git đã track). Tổ tiên của đường dẫn SYMLINK không chứa `.git`
     (chỉ tổ tiên của ĐÍCH thật mới có), nên hàng rào "skip-git-repo" — dựng
     10/08/2026 CHÍNH XÁC để chặn kịch bản ghi tiếng Việt vào nguồn git-tracked
     — bị symlink vô hiệu hoá hoàn toàn cho toàn bộ 43 skill này.

Nguyên tắc viết test: kiểm HÀNH VI bằng fixture thật (file thật, symlink thật
qua tempfile), không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_vi as AV  # noqa: E402


# ════════════════════════════════════════════════════════════════════════════
# #1 — Nhận diện tiếng Việt KHÔNG DẤU trong luật giữ-bản-tự-viết
# ════════════════════════════════════════════════════════════════════════════

class TestKhongDauKhongBiDe(unittest.TestCase):
    def _fixture(self, td: str, mo_ta_khong_dau: str) -> Path:
        p = Path(td) / "SKILL.md"
        p.write_text(
            f"---\nname: vi-du\ndescription: {mo_ta_khong_dau}\n---\nNoi dung.\n",
            encoding="utf-8",
        )
        return p

    def test_mo_ta_khong_dau_tu_viet_khong_bi_de(self):
        """★★ Ca chính #1: mô tả không dấu do bác sĩ tự gõ, chưa từng qua
        apply_vi.py (không có description-src) — phải được GIỮ NGUYÊN."""
        with tempfile.TemporaryDirectory() as td:
            p = self._fixture(td, "Dat lich tai kham cho benh nhan sau moi ca kham ngoai tru")
            item = {"path": str(p)}
            vi_entry = {"vi": "Đặt lịch hẹn tái khám (bản dịch từ điển, KHÔNG được ghi đè)"}
            ket_qua = AV.process(item, vi_entry, restore=False, dry=False)
            self.assertEqual(ket_qua, "giữ-bản-việt-tự-viết")
            noi_dung = p.read_text(encoding="utf-8")
            self.assertIn("Dat lich tai kham", noi_dung)
            self.assertNotIn("bản dịch từ điển", noi_dung)

    def test_mo_ta_tieng_anh_that_van_dich_binh_thuong(self):
        """Đối chứng: mô tả tiếng Anh thật (không đủ 3 từ trùng danh sách) vẫn
        được dịch bình thường — bản vá không được chặn oan luồng chính."""
        with tempfile.TemporaryDirectory() as td:
            p = self._fixture(
                td, "Search PubMed for clinical trials and generate a summary report",
            )
            item = {"path": str(p)}
            vi_entry = {"vi": "Tra cứu PubMed và tạo báo cáo tóm tắt"}
            ket_qua = AV.process(item, vi_entry, restore=False, dry=False)
            self.assertEqual(ket_qua, "applied")
            self.assertIn("Tra cứu PubMed", p.read_text(encoding="utf-8"))

    def test_da_qua_apply_vi_truoc_do_khong_bi_giu_oan(self):
        """Đối chứng: mô tả không dấu do CHÍNH apply_vi.py ghi (có
        description-src, ví dụ sau khi chạy bo_dau.py) vẫn được xử lý STALE/
        already bình thường — luật giữ-bản-tự-viết không áp cho trường hợp
        này (chỉ áp khi description-src VẮNG MẶT)."""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "SKILL.md"
            # Mô phỏng: apply_vi.py đã ghi bản không dấu (bo_dau.py) trước đó.
            p.write_text(
                "---\nname: vi-du\n"
                'description: "Dat lich tai kham cho benh nhan"\n'
                'description-en: "Schedule follow-up for patient"\n'
                'description-src: "aaaaaaaaaaaaaaaa"\n'
                "---\nNoi dung.\n",
                encoding="utf-8",
            )
            item = {"path": str(p)}
            vi_entry = {"vi": "Dat lich tai kham cho benh nhan"}
            ket_qua = AV.process(item, vi_entry, restore=False, dry=False)
            self.assertNotEqual(ket_qua, "giữ-bản-việt-tự-viết")

    def test_ham_nhan_dien_tra_ve_false_cho_van_ban_tieng_anh(self):
        self.assertFalse(AV._co_dau_hieu_tieng_viet_khong_dau(
            "Search PubMed for clinical trials and generate a summary report"
        ))

    def test_ham_nhan_dien_tra_ve_true_cho_tieng_viet_khong_dau(self):
        self.assertTrue(AV._co_dau_hieu_tieng_viet_khong_dau(
            "Dat lich tai kham cho benh nhan sau moi ca kham ngoai tru"
        ))


# ════════════════════════════════════════════════════════════════════════════
# #2 — trong_repo_git() phải resolve symlink trước khi tìm .git
# ════════════════════════════════════════════════════════════════════════════

class TestTrongRepoGitTheoSymlink(unittest.TestCase):
    def test_symlink_vao_repo_git_duoc_nhan_dien_dung(self):
        """★★ Ca chính #2: dựng CHÍNH XÁC kịch bản thật — repo git giả +
        symlink trỏ vào file bên trong repo đó (khớp ~/.claude/skills/<skill>
        → sync/skills/<skill> trong thực tế). trong_repo_git() PHẢI nhận ra
        symlink này nằm trong repo, không phải None."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo_gia"
            (repo / ".git").mkdir(parents=True)
            (repo / "sync" / "skills" / "vi-du").mkdir(parents=True)
            file_that = repo / "sync" / "skills" / "vi-du" / "SKILL.md"
            file_that.write_text("---\nname: vi-du\n---\n", encoding="utf-8")

            thu_muc_symlink = Path(td) / "gia-lap-claude-skills"
            thu_muc_symlink.mkdir()
            duong_dan_symlink = thu_muc_symlink / "SKILL.md"
            duong_dan_symlink.symlink_to(file_that)

            ket_qua = AV.trong_repo_git(duong_dan_symlink)
            self.assertIsNotNone(ket_qua, "symlink trỏ vào repo git phải được nhận diện")
            self.assertEqual(ket_qua.resolve(), repo.resolve())

    def test_process_tu_choi_ghi_qua_symlink_vao_repo_git(self):
        """Đối chứng cấp cao hơn: process() phải trả skip-git-repo cho một
        catalog item có path là symlink vào repo git — không được ghi đè
        NGUỒN GIT-TRACKED qua đường vòng symlink."""
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo_gia"
            (repo / ".git").mkdir(parents=True)
            file_that = repo / "SKILL.md"
            file_that.write_text(
                "---\nname: vi-du\ndescription: Dat lich tai kham\n---\nNoi dung.\n",
                encoding="utf-8",
            )
            duong_dan_symlink = Path(td) / "SKILL.md.symlink"
            duong_dan_symlink.symlink_to(file_that)

            item = {"path": str(duong_dan_symlink)}
            vi_entry = {"vi": "Bản dịch KHÔNG được ghi vào nguồn git"}
            ket_qua = AV.process(item, vi_entry, restore=False, dry=False)
            self.assertEqual(ket_qua, "skip-git-repo")
            self.assertNotIn("Bản dịch KHÔNG được ghi", file_that.read_text(encoding="utf-8"))

    def test_file_thuong_khong_trong_git_van_tra_none(self):
        """Đối chứng: file KHÔNG nằm trong repo git nào (không symlink, không
        .git ở tổ tiên) vẫn trả None như trước — bản vá không chặn oan cache
        plugin bình thường."""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "SKILL.md"
            p.write_text("---\nname: x\n---\n", encoding="utf-8")
            self.assertIsNone(AV.trong_repo_git(p))


if __name__ == "__main__":
    unittest.main()
