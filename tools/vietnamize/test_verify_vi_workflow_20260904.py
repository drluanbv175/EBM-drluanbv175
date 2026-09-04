#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện của Workflow đối kháng đa-agent vòng 2 (2026-09-04) trong
`verify_vi.py` — chốt kiểm chéo BỊ LỆCH so với hành vi THẬT của apply_vi.py.

apply_vi.py đã BỎ điều kiện `qua_ten` khỏi luật "giữ-bản-việt-tự-viết" từ
24/08/2026 (áp cho MỌI cách khớp — id lẫn tên — không chỉ khớp qua tên; xem
comment "Bỏ điều kiện qua_ten" trong apply_vi.py). Nhưng `verify_vi.py` — bộ
kiểm ĐỘC LẬP, cố ý không import logic từ apply_vi.py — vẫn giữ điều kiện
`qua_ten and ...` trong bản sao của luật này. Hệ quả: một file khớp bản dịch
qua ID TRỰC TIẾP (không qua tên), có mô tả tiếng Việt tự viết (không mang
`description-src`) mà apply_vi.py ĐÚNG khi bỏ qua, bị verify_vi.py báo NHẦM
thành lỗi "description KHÁC bản dịch đã khai".

Đồng thời, bản vá 2026-09-04 của apply_vi.py (cùng phiên) thêm nhận diện
tiếng Việt KHÔNG DẤU vào luật đó — nếu không đồng bộ luôn vào verify_vi.py,
một mô tả không dấu mà apply_vi.py ĐÚNG khi giữ nguyên sẽ tạo báo động giả Ở
ĐÂY (trước đây "vô hại" chỉ vì apply_vi.py cũ ghi đè nên hai công cụ luôn
khớp nhau một cách tình cờ — SAI theo kiểu khác).

Nguyên tắc viết test: gọi THẲNG verify_vi.main() qua fixture catalog/từ điển
dựng tay (monkeypatch HERE), không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_vi as VV  # noqa: E402


def _chay(td: Path, catalog: list, vi_map: dict) -> tuple[int, str]:
    (td / "catalog_raw.json").write_text(json.dumps(catalog), encoding="utf-8")
    (td / "vi_descriptions.json").write_text(json.dumps(vi_map), encoding="utf-8")
    buf = io.StringIO()
    old_here = VV.HERE
    VV.HERE = td
    try:
        with contextlib.redirect_stdout(buf):
            rc = VV.main()
    finally:
        VV.HERE = old_here
    return rc, buf.getvalue()


class TestQuaTenSyncVoiApplyVi(unittest.TestCase):
    def test_khop_qua_id_truc_tiep_mo_ta_viet_co_dau_khong_bi_bao_loi(self):
        """★★ Ca chính: khớp qua ID (không phải name:), mô tả hiện tại đã là
        tiếng Việt CÓ DẤU do người viết tay (không có description-src) — phải
        được xếp vào 'giữ', KHÔNG được báo lỗi."""
        with tempfile.TemporaryDirectory() as td:
            td_p = Path(td)
            skill = td_p / "SKILL.md"
            skill.write_text(
                "---\nname: vi-du\ndescription: Mô tả tiếng Việt tự viết, khác từ điển\n---\n"
                "Noi dung.\n",
                encoding="utf-8",
            )
            catalog = [{"id": "skill:user-skills:vi-du", "name": "vi-du", "path": str(skill)}]
            vi_map = {"skill:user-skills:vi-du": {"vi": "Bản dịch từ điển hoàn toàn khác"}}
            rc, out = _chay(td_p, catalog, vi_map)
            self.assertEqual(rc, 0, out)
            self.assertIn("giữ mô tả tiếng Việt tự viết", out)
            self.assertNotIn("KHÁC bản dịch đã khai", out)

    def test_khop_qua_id_mo_ta_khong_dau_khong_bi_bao_loi(self):
        """★★ Ca chính thứ hai: cùng kịch bản nhưng mô tả KHÔNG DẤU — đồng bộ
        với bản vá 2026-09-04 của apply_vi.py trong cùng phiên."""
        with tempfile.TemporaryDirectory() as td:
            td_p = Path(td)
            skill = td_p / "SKILL.md"
            skill.write_text(
                "---\nname: vi-du\n"
                "description: Dat lich tai kham cho benh nhan sau moi ca kham ngoai tru\n"
                "---\nNoi dung.\n",
                encoding="utf-8",
            )
            catalog = [{"id": "skill:user-skills:vi-du", "name": "vi-du", "path": str(skill)}]
            vi_map = {"skill:user-skills:vi-du": {"vi": "Đặt lịch hẹn tái khám (bản dịch từ điển)"}}
            rc, out = _chay(td_p, catalog, vi_map)
            self.assertEqual(rc, 0, out)
            self.assertIn("giữ mô tả tiếng Việt tự viết", out)
            self.assertNotIn("KHÁC bản dịch đã khai", out)

    def test_mo_ta_tieng_anh_that_khac_tu_dien_van_bi_bao_loi(self):
        """Đối chứng QUAN TRỌNG: một mô tả tiếng ANH thật (không phải tiếng
        Việt tự viết) khác bản dịch từ điển — vẫn PHẢI báo lỗi. Bản vá không
        được nới lỏng luật tới mức che mất lỗi thật (ví dụ mô tả gốc vừa đổi
        do plugin cập nhật mà chưa dịch lại)."""
        with tempfile.TemporaryDirectory() as td:
            td_p = Path(td)
            skill = td_p / "SKILL.md"
            skill.write_text(
                "---\nname: vi-du\ndescription: Search PubMed and summarize findings\n---\n"
                "Noi dung.\n",
                encoding="utf-8",
            )
            catalog = [{"id": "skill:user-skills:vi-du", "name": "vi-du", "path": str(skill)}]
            vi_map = {"skill:user-skills:vi-du": {"vi": "Tra cứu PubMed và tóm tắt"}}
            rc, out = _chay(td_p, catalog, vi_map)
            self.assertEqual(rc, 1, out)
            self.assertIn("KHÁC bản dịch đã khai", out)

    def test_mo_ta_dung_bang_ban_dich_khong_bao_loi(self):
        """Đối chứng: mô tả trên đĩa ĐÚNG bằng bản dịch từ điển — sạch, không
        báo lỗi, không rơi vào nhánh 'giữ'."""
        with tempfile.TemporaryDirectory() as td:
            td_p = Path(td)
            skill = td_p / "SKILL.md"
            skill.write_text(
                "---\nname: vi-du\ndescription: Bản dịch đúng\n---\nNoi dung.\n",
                encoding="utf-8",
            )
            catalog = [{"id": "skill:user-skills:vi-du", "name": "vi-du", "path": str(skill)}]
            vi_map = {"skill:user-skills:vi-du": {"vi": "Bản dịch đúng"}}
            rc, out = _chay(td_p, catalog, vi_map)
            self.assertEqual(rc, 0, out)
            self.assertNotIn("KHÁC bản dịch đã khai", out)
            self.assertNotIn("giữ mô tả tiếng Việt tự viết", out)


if __name__ == "__main__":
    unittest.main()
