#!/usr/bin/env python3
"""Hồi quy cho CodexCliClient.__init__ — chọn đường dẫn binary theo nền tảng
(15/09/2026, workflow kiểm tra toàn diện).

Bối cảnh: trước bản vá, `_APP_BINARY` (đường dẫn app bundle ChatGPT.app, CHỈ
có ý nghĩa trên macOS) là fallback vô điều kiện khi `shutil.which("codex")`
thất bại — không phân biệt nền tảng. `tools/kiem_tuong_thich_da_nen.py` (R5)
báo vàng mỗi lần quét vì cả file không có dấu hiệu nhận thức nền tảng nào.
Vá bằng cách chỉ dùng đường dẫn app bundle khi `sys.platform == "darwin"`.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from orchestrator.agent_adapter import CodexCliClient  # noqa: E402


def test_uu_tien_shutil_which_bat_ke_nen_tang(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/codex")
    c = CodexCliClient()
    assert c.binary == Path("/usr/local/bin/codex")


def test_macos_lui_ve_app_bundle_khi_khong_co_trong_path(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr(sys, "platform", "darwin")
    c = CodexCliClient()
    assert c.binary == CodexCliClient._APP_BINARY_MACOS


def test_khac_macos_khong_dung_duong_dan_app_bundle(monkeypatch):
    """Vá 15/09/2026: trên Windows/Linux, đường dẫn app bundle của macOS
    KHÔNG được dùng làm fallback — trước bản vá đây chính là hành vi sai
    (dù vô hại nhờ .exists() bên dưới, vẫn là sai ngữ nghĩa)."""
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr(sys, "platform", "win32")
    c = CodexCliClient()
    assert c.binary != CodexCliClient._APP_BINARY_MACOS
    assert not c.binary.exists()


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
