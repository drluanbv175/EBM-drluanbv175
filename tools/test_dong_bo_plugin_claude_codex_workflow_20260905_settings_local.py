#!/usr/bin/env python3
"""Hồi quy phát hiện HIGH của Workflow đối kháng đa-agent 2026-09-05 (vòng 5, task #82)
trong `tools/dong_bo_plugin_claude_codex.py::quet_claude()` — đọc THẲNG `settings.json`,
bỏ qua `settings.local.json`.

CƠ CHẾ LỖI: bản gốc gọi `doc_json(SETTINGS)` với `SETTINGS = HOME / ".claude/settings.json"`
— một hàm nội bộ chỉ `json.loads` MỘT file, không đi qua `doc_settings()` (bộ gộp
`settings.json` + `settings.local.json` dựng ngày 02/09/2026, BH86, chính vì lớp lỗi
này). Bốn công cụ chị em cùng đọc `enabledPlugins`
(`extract_catalog.py`/`don_bong_tieng_anh.py`/`kiem_plugin_day_du.py`/
`kiem_co_tat_plugin_trung.py`) đều đã chuyển sang `doc_settings()` cùng ngày 02/09 —
file này (dựng 21/08, TRƯỚC BH86) bị bỏ sót vì công cụ chưa tồn tại ở thời điểm đó.

HẬU QUẢ: doctrine tự khai «8 cờ `false`» (8 plugin medsci trùng, tắt có chủ ý) sống ở
`~/.claude/settings.local.json` — file KHÔNG qua git, hay bị app ghi đè mất
`settings.json` định kỳ (BH69/BH81/BH86). Khi đó `quet_claude()` gốc thấy
`settings.json` trống ⇒ `khai = {}` ⇒ `tat = set()` ⇒ báo cáo TẤT CẢ plugin đang BẬT,
kể cả 8 plugin doctrine đã tắt hẳn — một báo động XANH GIẢ đúng loại mà BH86 sinh ra
để chấm dứt, tái diễn ở đúng công cụ đối chiếu CHÉO MÁY (mục đích của file này).

Nguyên tắc viết test: import module thật bằng `importlib`, monkeypatch HAI hằng module
(`REG`, `SETTINGS`) trỏ vào fixture tạm, gọi THẲNG `quet_claude()` thật — không grep
chuỗi trong mã nguồn, không mock `doc_settings`.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

_MOD_PATH = Path(__file__).resolve().parent / "dong_bo_plugin_claude_codex.py"


def _nap_module():
    """Nạp file như một module MỚI mỗi lần — tránh trạng thái module cũ rò rỉ giữa
    các test (mỗi test tự monkeypatch REG/SETTINGS trên bản nạp riêng của nó)."""
    spec = importlib.util.spec_from_file_location(
        "_test_dong_bo_plugin_claude_codex", _MOD_PATH)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


class TestQuetClaudeDocCaSettingsLocal(unittest.TestCase):
    """★★★ Ca chính — plugin bị tắt CHỈ trong settings.local.json phải được báo cáo
    ĐÚNG là đang TẮT, không được báo nhầm là đang BẬT."""

    def _fixture(self, thu: Path, *, settings_json: dict, settings_local_json: dict):
        (thu / "installed_plugins.json").write_text(json.dumps({
            "plugins": {
                "medsci-review": [{"installPath": str(thu / "medsci-review"), "version": "1.0"}],
                "medsci-project": [{"installPath": str(thu / "medsci-project"), "version": "1.0"}],
            }
        }), encoding="utf-8")
        (thu / "medsci-review").mkdir()
        (thu / "medsci-project").mkdir()
        (thu / "settings.json").write_text(json.dumps(settings_json), encoding="utf-8")
        (thu / "settings.local.json").write_text(json.dumps(settings_local_json),
                                                  encoding="utf-8")

    def test_plugin_tat_chi_o_settings_local_duoc_bao_dung_la_tat(self):
        with tempfile.TemporaryDirectory() as d:
            thu = Path(d)
            self._fixture(thu, settings_json={},
                           settings_local_json={"enabledPlugins": {"medsci-review": False}})
            m = _nap_module()
            m.REG = thu / "installed_plugins.json"
            m.SETTINGS = thu / "settings.json"
            ra = m.quet_claude()
            self.assertFalse(ra["medsci-review"]["bat"],
                              "plugin tắt CHỈ trong settings.local.json bị báo nhầm là BẬT")
            self.assertTrue(ra["medsci-review"]["khai_tat_ro"])
            self.assertTrue(ra["medsci-project"]["bat"],
                             "plugin KHÔNG bị tắt ở đâu cả vẫn phải báo đang BẬT")

    def test_settings_json_trong_hoan_toan_khong_lam_mat_co_tat(self):
        """Đúng kịch bản BH86 mô tả: settings.json bị app xoá sạch (trống), toàn bộ
        cấu hình chỉ còn trong settings.local.json."""
        with tempfile.TemporaryDirectory() as d:
            thu = Path(d)
            self._fixture(thu, settings_json={},
                           settings_local_json={"enabledPlugins": {
                               "medsci-review": False, "medsci-project": False}})
            m = _nap_module()
            m.REG = thu / "installed_plugins.json"
            m.SETTINGS = thu / "settings.json"
            ra = m.quet_claude()
            self.assertFalse(ra["medsci-review"]["bat"])
            self.assertFalse(ra["medsci-project"]["bat"])


class TestQuetClaudeVanDungKhiChiCoSettingsJson(unittest.TestCase):
    """Đối chứng — cờ tắt khai trong settings.json (không có settings.local.json) vẫn
    phải hoạt động như trước (không thoái lui hành vi cũ khi KHÔNG có file .local)."""

    def test_plugin_tat_o_settings_json_van_dung(self):
        with tempfile.TemporaryDirectory() as d:
            thu = Path(d)
            (thu / "installed_plugins.json").write_text(json.dumps({
                "plugins": {"medsci-review": [{"installPath": str(thu / "medsci-review"),
                                                "version": "1.0"}]}
            }), encoding="utf-8")
            (thu / "medsci-review").mkdir()
            (thu / "settings.json").write_text(
                json.dumps({"enabledPlugins": {"medsci-review": False}}), encoding="utf-8")
            m = _nap_module()
            m.REG = thu / "installed_plugins.json"
            m.SETTINGS = thu / "settings.json"
            ra = m.quet_claude()
            self.assertFalse(ra["medsci-review"]["bat"])


if __name__ == "__main__":
    unittest.main()
