#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện của Workflow đối kháng đa-agent vòng 2 (2026-09-04) trong
`dong_bo_tat_ca.py` — MEDIUM.

`nhan_dien_may.py` (dựng 02/09/2026) tự khai là "MỘT nguồn duy nhất cho câu hỏi
«máy này là máy nào?»", ra đời để chấm dứt tình trạng `dong_bo_plugin_claude_
codex.py` và `kiem_plugin_day_du.py` mỗi file tự chép một bản `ten_may()` giống
hệt nhau — hai bản chép đó ĐÃ được sửa để uỷ quyền cho nguồn chuẩn. Nhưng
`dong_bo_tat_ca.py::main()` là bản chép THỨ BA chưa ai bắt được: nó tự tính
`may = {"Darwin": "Mac", "Windows": "Windows"}.get(platform.system(),
platform.system())` — bản chép CŨ, KHÔNG nhận diện phiên Claude Code trên web
(CLAUDE_CODE_REMOTE=true). Đo sống trên chính phiên cloud đang chạy: bản chép cũ
trả "Linux" trong khi `nhan_dien_may.ten_may()` (nguồn chuẩn) trả "Cloud".

Nguyên tắc viết test: gọi THẲNG hàm ten_may() vừa thêm và chạy main() thật qua
subprocess với biến môi trường mô phỏng cả hai kịch bản — không grep chuỗi
trong mã nguồn.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def _nap_module(ten: str, duong_dan: Path):
    """Nạp module từ đường dẫn file, ĐĂNG KÝ vào sys.modules TRƯỚC exec_module.

    dong_bo_tat_ca.py dùng @dataclass (lớp KetQua) — dataclass tra
    sys.modules.get(cls.__module__).__dict__ lúc dựng lớp, nên nạp module mà
    không đăng ký trước sẽ vỡ với AttributeError (đúng bài học BH43 đã ghi
    trong CLAUDE.md, gặp lại ở đây khi viết test mới).
    """
    spec = importlib.util.spec_from_file_location(ten, duong_dan)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTenMayUyQuyenChoNguonChuan(unittest.TestCase):
    def test_ten_may_khop_voi_nhan_dien_may(self):
        """★★ Ca chính: dong_bo_tat_ca.ten_may() phải trả CÙNG giá trị với
        nguồn chuẩn nhan_dien_may.ten_may() trên chính máy đang chạy test."""
        dbtc = _nap_module("dong_bo_tat_ca", HERE / "dong_bo_tat_ca.py")
        ndm = _nap_module("nhan_dien_may", HERE / "nhan_dien_may.py")
        self.assertEqual(dbtc.ten_may(), ndm.ten_may())

    def test_khong_con_import_platform_truc_tiep_de_tu_tinh(self):
        """Đối chứng cấu trúc: module không còn tự map Darwin/Windows bằng
        platform.system() — xác nhận bằng cách kiểm module KHÔNG còn thuộc
        tính `platform` (import đã bị gỡ, không chỉ thêm hàm mới bên cạnh
        logic cũ)."""
        dbtc = _nap_module("dong_bo_tat_ca", HERE / "dong_bo_tat_ca.py")
        self.assertFalse(hasattr(dbtc, "platform"))


class TestMainJsonBaoCaoMayDung(unittest.TestCase):
    def _chay_json(self, env_them: dict) -> dict:
        env = dict(os.environ)
        env.update(env_them)
        r = subprocess.run(
            [sys.executable, str(HERE / "dong_bo_tat_ca.py"), "--liet-ke-lan", "--json"],
            cwd=str(REPO), env=env, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_liet_ke_lan_khong_dung_toi_ten_may(self):
        """--liet-ke-lan không in `may` (chỉ danh sách làn) — kiểm main() vẫn
        chạy được trọn vẹn sau khi sửa, không phải chỉ kiểm ten_may() cô lập."""
        d = self._chay_json({})
        self.assertIn("lan", d)
        self.assertGreater(len(d["lan"]), 0)

    def test_may_trong_json_that_la_cloud_khi_gia_lap_phien_cloud(self):
        """★★ Ca chính cấp CLI: chạy dong_bo_tat_ca.py --bo-qua-an-toan --json
        thật qua subprocess với CLAUDE_CODE_REMOTE=true — trường `may` trong
        JSON đầu ra phải là 'Cloud', không phải tên hệ điều hành thô."""
        env = dict(os.environ)
        env["CLAUDE_CODE_REMOTE"] = "true"
        r = subprocess.run(
            [sys.executable, str(HERE / "dong_bo_tat_ca.py"), "--bo-qua-an-toan", "--json"],
            cwd=str(REPO), env=env, capture_output=True, text=True, timeout=60,
        )
        # Mã thoát có thể 0/1/2 tuỳ trạng thái đồng bộ thật của máy — không kiểm
        # mã thoát ở đây, chỉ kiểm trường "may" trong JSON đã in được.
        self.assertTrue(r.stdout.strip(), r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d.get("may"), "Cloud", r.stdout)


if __name__ == "__main__":
    unittest.main()
