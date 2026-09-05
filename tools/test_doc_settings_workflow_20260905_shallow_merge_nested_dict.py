#!/usr/bin/env python3
"""Hồi quy phát hiện HIGH của Workflow đối kháng đa-agent 2026-09-05 (vòng 5, task #81)
trong `tools/doc_settings.py::doc_settings()` — gộp NÔNG (`gop.update(d)`) làm mất khoá
con khi một khoá cấp một (vd `enabledPlugins`, `hooks`) có mặt ở CẢ HAI file.

CƠ CHẾ LỖI: `gop.update(d)` (dict.update chuẩn) THAY THẾ TOÀN BỘ giá trị của một khoá
cấp một khi khoá đó có mặt trong `d` — không merge đệ quy. Với `enabledPlugins` (khoá con
là TÊN PLUGIN → bool), nếu `settings.json` khai một plugin và `settings.local.json` khai
một plugin KHÁC, plugin của `settings.json` biến mất khỏi kết quả gộp — dù cả hai file
đều đọc được và hợp lệ, không có lỗi cú pháp nào để báo.

HẬU QUẢ THẬT: 4 công cụ tiêu thụ `enabledPlugins` qua `doc_settings()`
(`extract_catalog.py`, `don_bong_tieng_anh.py`, `kiem_plugin_day_du.py`,
`kiem_co_tat_plugin_trung.py`) sẽ đọc SAI trạng thái bật/tắt của bất kỳ plugin nào chỉ
được khai ở MỘT trong hai file — đúng họ lỗi "đo đúng, nhưng đo nhầm chỗ" mà BH69/BH74/
BH81/BH86 đã lặp lại nhiều lần trong hệ này, lần này ở NGAY CHÍNH công cụ (`doc_settings`)
được dựng lên để chấm dứt họ lỗi đó.

Bằng chứng cho thấy đây là bug chưa từng bị bắt: `chot_hoi_quy_bai_hoc.py::bh16_...()` đã
phải TỰ VIẾT logic CỘNG DỒN riêng (nối mảng `hooks.SessionStart` của cả hai file bằng
`lenhs += [...]`) thay vì gọi `doc_settings()` — vì hàm này chưa từng gộp đúng cho khoá
lồng. Test BH86 hiện có (trong `chot_hoi_quy_bai_hoc.py`) chỉ kiểm khoá SCALAR trùng cả
hai file (`skillListingBudgetFraction`) và khoá chỉ có ở MỘT file — KHÔNG kiểm khoá kiểu
dict có mặt ở CẢ HAI file với các khoá CON khác nhau, nên khoảng trống này lọt qua.

BẢN VÁ: gộp lồng MỘT CẤP cho giá trị kiểu dict trong `doc_settings()` — khoá con nào chỉ
có ở một file thì GIỮ NGUYÊN, khoá con trùng cả hai file thì `.local` thắng (giữ đúng
nguyên tắc "`.local` đè", chỉ đổi CẤP mà nguyên tắc đó áp dụng — từ cấp khoá xuống cấp
khoá con). Giá trị không phải dict (số/chuỗi/list) hành vi KHÔNG đổi.

Nguyên tắc viết test: gọi THẲNG `doc_settings()` thật với fixture tạm (tham số `goc` được
chính module thiết kế để tiêm đường dẫn — xem docstring `duong_dan_doc()`), không grep
chuỗi trong mã nguồn.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/

from doc_settings import doc_settings  # noqa: E402


class TestGopLongMotCapChoDictTrungCaHaiFile(unittest.TestCase):
    """★★★ Ca chính — enabledPlugins có mặt ở CẢ HAI file với khoá con KHÁC NHAU: kết
    quả gộp phải giữ CẢ HAI, không được để file sau xoá mất khoá con của file trước."""

    def _fixture(self, chinh_json: dict, cuc_bo_json: dict):
        thu = tempfile.TemporaryDirectory()
        self.addCleanup(thu.cleanup)
        chinh = Path(thu.name) / "settings.json"
        cuc_bo = Path(thu.name) / "settings.local.json"
        chinh.write_text(json.dumps(chinh_json), encoding="utf-8")
        cuc_bo.write_text(json.dumps(cuc_bo_json), encoding="utf-8")
        return chinh

    def test_enabledplugins_khoa_con_khac_nhau_giu_ca_hai(self):
        chinh = self._fixture(
            {"enabledPlugins": {"plugin-moi-app-vua-them@m": True}},
            {"enabledPlugins": {"plugin-a@m": False, "plugin-b@m": False}},
        )
        cfg = doc_settings(nghiem=False, goc=chinh)
        ep = cfg.get("enabledPlugins", {})
        self.assertIs(ep.get("plugin-moi-app-vua-them@m"), True,
                      "khoá con CHỈ có ở settings.json bị mất khi settings.local.json "
                      "cũng khai enabledPlugins")
        self.assertIs(ep.get("plugin-a@m"), False)
        self.assertIs(ep.get("plugin-b@m"), False)

    def test_khoa_con_trung_ca_hai_file_thi_local_thang(self):
        """Khi CÙNG một khoá con xuất hiện ở cả hai file (giá trị khác nhau), `.local`
        vẫn phải thắng — giữ đúng nguyên tắc "`.local` đè", chỉ đổi cấp áp dụng."""
        chinh = self._fixture(
            {"enabledPlugins": {"plugin-x@m": True}},
            {"enabledPlugins": {"plugin-x@m": False}},
        )
        cfg = doc_settings(nghiem=False, goc=chinh)
        self.assertIs(cfg["enabledPlugins"]["plugin-x@m"], False)

    def test_hooks_sessionstart_kieu_du_lieu_khac_khong_bi_dung_nham(self):
        """`hooks` cũng là dict lồng (giống enabledPlugins) — cùng luật phải áp dụng,
        không riêng gì enabledPlugins."""
        chinh = self._fixture(
            {"hooks": {"PreToolUse": [{"hooks": [{"command": "echo pretooluse"}]}]}},
            {"hooks": {"SessionStart": [{"hooks": [{"command": "echo sessionstart"}]}]}},
        )
        cfg = doc_settings(nghiem=False, goc=chinh)
        self.assertIn("PreToolUse", cfg["hooks"],
                      "khoá con hooks.PreToolUse chỉ có ở settings.json bị mất")
        self.assertIn("SessionStart", cfg["hooks"])


class TestGiaTriVoHuongVanDeNhuCu(unittest.TestCase):
    """Đối chứng bắt buộc — giá trị SCALAR (số/chuỗi) trùng cả hai file vẫn phải để file
    sau (`.local`) thắng TOÀN BỘ như hành vi gốc — bản vá KHÔNG được đổi ngữ nghĩa "đè"
    cho giá trị vô hướng, chỉ đổi cho giá trị dict."""

    def test_scalar_trung_ca_hai_file_local_van_thang_toan_bo(self):
        thu = tempfile.TemporaryDirectory()
        self.addCleanup(thu.cleanup)
        chinh = Path(thu.name) / "settings.json"
        cuc_bo = Path(thu.name) / "settings.local.json"
        chinh.write_text(json.dumps({"skillListingBudgetFraction": 0.01}), encoding="utf-8")
        cuc_bo.write_text(json.dumps({"skillListingBudgetFraction": 0.08}), encoding="utf-8")
        cfg = doc_settings(nghiem=False, goc=chinh)
        self.assertEqual(cfg["skillListingBudgetFraction"], 0.08)

    def test_list_trung_ca_hai_file_local_thang_toan_bo_khong_noi_mang(self):
        """List KHÔNG phải dict — hành vi phải là THAY THẾ toàn bộ (không nối mảng),
        đúng ngữ nghĩa "đè" hiện có cho kiểu không-phải-dict."""
        thu = tempfile.TemporaryDirectory()
        self.addCleanup(thu.cleanup)
        chinh = Path(thu.name) / "settings.json"
        cuc_bo = Path(thu.name) / "settings.local.json"
        chinh.write_text(json.dumps({"mot_mang": [1, 2, 3]}), encoding="utf-8")
        cuc_bo.write_text(json.dumps({"mot_mang": [4, 5]}), encoding="utf-8")
        cfg = doc_settings(nghiem=False, goc=chinh)
        self.assertEqual(cfg["mot_mang"], [4, 5])


if __name__ == "__main__":
    unittest.main()
