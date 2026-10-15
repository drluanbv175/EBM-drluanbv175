"""Bước «TV» (toan_van_theo_chu_de._chay) đọc đầu ra công cụ con bằng UTF-8, không bằng bảng mã của máy. 14/10/2026.

VÌ SAO. `_chay` gọi `subprocess.run(..., text=True)` KHÔNG kèm `encoding` ⇒ Python giải mã bằng bảng mã locale. Ba công
cụ con in UTF-8 (tiếng Việt, ✓/✗). Trên Windows chưa bật UTF-8 mode (cp1252/cp1258) đầu ra bị mất (luồng đọc nền ném
UnicodeDecodeError, `r.stdout` thành None); trên máy locale ASCII, lỗi ném thẳng ra khỏi `_chay` (không nằm trong
except TimeoutExpired/OSError) ⇒ sập bước TV. CI Windows của gốc ép PYTHONUTF8 nên không thấy họ lỗi này.
Tiến trình con chạy với locale C + tắt ép UTF-8 (PEP 538/540) giả lập đúng máy không-UTF-8; mọi tham số dòng lệnh
giữ ASCII (chữ có dấu viết bằng escape) để chỉ đo đúng phần giải mã đầu ra.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

_BO_THU = r'''
import importlib.util, sys
spec = importlib.util.spec_from_file_location("_tv_utf8", sys.argv[1])
tv = importlib.util.module_from_spec(spec); spec.loader.exec_module(tv)
ma, ra = tv._chay([sys.executable, "-c",
                   "import sys; sys.stdout.buffer.write('\\u0110\\xe3 \\u0111\\u1ecdc to\\xe0n v\\u0103n \\u2713'.encode('utf-8'))"])
sys.stdout.write(ascii((ma, ra)))
'''


def test_chay_giai_ma_utf8_khi_locale_khong_phai_utf8():
    if os.name == "nt":
        env = {**os.environ, "PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"}
    else:
        env = {**os.environ, "LC_ALL": "C", "LANG": "C", "PYTHONCOERCECLOCALE": "0", "PYTHONUTF8": "0"}
        env.pop("PYTHONIOENCODING", None)
    r = subprocess.run([sys.executable, "-c", _BO_THU, str(REPO / "tools" / "toan_van_theo_chu_de.py")],
                       capture_output=True, env=env, timeout=120)
    ra = r.stdout.decode("ascii", errors="replace")
    loi = r.stderr.decode("utf-8", errors="replace")[-600:]
    assert r.returncode == 0, f"_chay sập khi locale không phải UTF-8:\n{loi}"
    assert "\\u0110\\xe3 \\u0111\\u1ecdc to\\xe0n v\\u0103n \\u2713" in ra, f"đầu ra công cụ con bị mất/giải mã sai: {ra}"
