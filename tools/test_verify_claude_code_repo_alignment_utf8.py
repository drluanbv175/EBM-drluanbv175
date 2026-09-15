"""Khoá bản vá 16/09/2026: verify_claude_code_repo_alignment.main() từng crash
UnicodeEncodeError trên console Windows (cp1252 mặc định) ngay ở dòng in
disclaimer tiếng Việt cuối cùng — dù mọi check đã PASS. Không kiểm bằng cách
gọi lại toàn bộ main() (kéo theo git thật, chậm và phụ thuộc trạng thái repo);
kiểm ĐÚNG cơ chế đã gây lỗi: stream stdout bị ép về một codec không chứa ký tự
tiếng Việt, rồi xác nhận _configure_utf8_stdio() làm cho việc in lại an toàn.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_claude_code_repo_alignment as V  # noqa: E402


class _Cp1252LikeStream(io.TextIOBase):
    """Mô phỏng stdout Windows mặc định: encode() ném lỗi với ký tự ngoài cp1252,
    và (giống sys.stdout thật) có .reconfigure() để đổi encoding tại chỗ."""

    def __init__(self) -> None:
        self._encoding = "cp1252"
        self.written = []

    def write(self, s: str) -> int:  # type: ignore[override]
        s.encode(self._encoding)  # ném UnicodeEncodeError giống console Windows thật
        self.written.append(s)
        return len(s)

    def reconfigure(self, encoding: str | None = None, errors: str | None = None) -> None:
        if encoding:
            self._encoding = encoding


def test_disclaimer_with_vietnamese_diacritics_crashes_without_utf8_fix():
    """Tái hiện lỗi GỐC trước khi vá: in câu có 'ầ' (U+1EA7) vào stream cp1252
    ném UnicodeEncodeError — xác nhận phép thử này THẬT SỰ nhắm đúng cơ chế lỗi,
    không phải giả định suông."""
    stream = _Cp1252LikeStream()
    try:
        stream.write("Cần bác sĩ kiểm chứng.")
    except UnicodeEncodeError:
        return
    raise AssertionError("Kỳ vọng UnicodeEncodeError trên cp1252 giả lập — phép thử không còn nhắm đúng lỗi gốc")


def test_configure_utf8_stdio_makes_vietnamese_print_safe(monkeypatch):
    stream = _Cp1252LikeStream()
    monkeypatch.setattr(sys, "stdout", stream)
    monkeypatch.setattr(sys, "stderr", stream)

    V._configure_utf8_stdio()
    stream.write("Cần bác sĩ kiểm chứng.")  # không còn ném lỗi sau khi reconfigure

    assert stream.written == ["Cần bác sĩ kiểm chứng."]
