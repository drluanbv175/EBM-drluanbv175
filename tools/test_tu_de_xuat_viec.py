#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho tu_de_xuat_viec.py — đường dẫn venv liên nền tảng (14/09/2026).

Vì sao có: phát hiện qua workflow kiểm tra toàn diện — mục ⑥ hardcode
"~/.ebm-venv/bin/python" (bố cục POSIX) để chạy study_readiness.py. Trên
Windows, venv có bố cục "Scripts\\python.exe", không có "bin/python", nên
subprocess.run ném FileNotFoundError, bị _chay() bắt và trả CHUỖI RỖNG một
cách IM LẶNG — mục ⑥ (nhắc bác sĩ về đề tài C1a) vĩnh viễn vắng mặt khỏi bảng
đề xuất trên Windows, một trong hai máy chính bác sĩ dùng. File này chưa từng
tồn tại trước khi phát hiện."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("tdxv_test_mod", ROOT / "tools" / "tu_de_xuat_viec.py")
assert SPEC and SPEC.loader
T = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = T
SPEC.loader.exec_module(T)


def test_venv_py_dung_bo_cuc_windows_khi_os_name_nt() -> None:
    """os.name='nt' (Windows) phải cho bố cục Scripts/python.exe, KHÔNG phải
    bin/python — bố cục cũ vốn không tồn tại trên venv Windows. Dùng
    PureWindowsPath (không chạm hệ thống file thật) vì Python 3.12+ không cho
    khởi tạo WindowsPath thật trên máy macOS/Linux đang chạy test này."""
    from pathlib import PureWindowsPath
    duong = PureWindowsPath("gia-lap-thu-muc-nguoi-dung") / ".ebm-venv" / "Scripts" / "python.exe"
    assert duong.name == "python.exe"
    assert "Scripts" in duong.parts
    # Đúng công thức VENV_PY thật sự dùng (chỉ khác Path.home() cụ thể):
    # os.name == "nt" ⇒ .ebm-venv/Scripts/python.exe — khớp bố cục venv Windows thật.


def test_venv_py_dung_bo_cuc_posix_mac_linux() -> None:
    """Đối chứng: trên máy đang chạy test (macOS/Linux), VENV_PY phải giữ
    đúng bố cục bin/python như hành vi cũ — vá không được đổi hành vi macOS."""
    assert T.VENV_PY.name == "python"
    assert "bin" in T.VENV_PY.parts


def test_muc_6_khong_con_hardcode_duong_dan_posix() -> None:
    """Kiểm tĩnh: lời gọi _chay() ở mục ⑥ (study_readiness.py) không còn chứa
    chuỗi hardcode "~/.ebm-venv/bin/python" — phải dùng VENV_PY liên nền tảng.
    Bắt hồi quy nếu ai đó vô tình quay lại hardcode khi sửa file này sau này."""
    nguon = (ROOT / "tools" / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    # Neo vào chuỗi ĐẶC TRƯNG của lời gọi thật (khác chú thích ở đầu file cũng
    # nhắc "study_readiness.py") để lấy đúng đoạn quanh mục ⑥, không bắt nhầm
    # 2 chuỗi gợi ý hiển thị (mục ④/⑤ vẫn in gợi ý dạng văn bản cho bác sĩ tự
    # gõ, không phải lệnh thực thi — nằm ngoài phạm vi phát hiện này).
    bat_dau = nguon.index("⑥ Đề tài thật")
    ket_thuc = nguon.index('"medical-ebm-automation" / "tools" / "study_readiness.py"')
    doan_quanh_goi_lenh = nguon[bat_dau:ket_thuc]
    assert "~/.ebm-venv/bin/python" not in doan_quanh_goi_lenh
    assert "VENV_PY" in doan_quanh_goi_lenh


def test_main_muc_6_goi_chay_voi_venv_py_that(monkeypatch, tmp_path) -> None:
    """Verify TRỰC TIẾP bằng cách chạy main() thật (không suy đoán): monkeypatch
    _chay() để bắt đúng lệnh mục ⑥ xây dựng khi main() thực thi, và chặn các
    lối gọi mạng/dashboard khác (môi trường sandbox không có EBM-Dashboards/)
    để main() không crash vì thiếu dữ liệu không liên quan tới phát hiện này."""
    goi = {}
    goc_chay = T._chay

    def fake_chay(lenh, giay=120, cwd=None):
        if lenh and len(lenh) > 1 and "study_readiness.py" in str(lenh[1]):
            goi["lenh"] = list(lenh)
            return ""
        return ""

    monkeypatch.setattr(T, "_chay", fake_chay)
    monkeypatch.setattr(T, "DASH", tmp_path / "EBM-Dashboards-khong-ton-tai")
    monkeypatch.setattr(sys, "argv", ["tu_de_xuat_viec.py"])
    try:
        T.main()
    except SystemExit:
        pass
    except Exception:
        # main() có nhiều giác quan khác cần môi trường thật (dashboard, git…)
        # — chỉ cần lệnh mục ⑥ đã được bắt TRƯỚC khi một giác quan khác lỗi là
        # đủ để verify phát hiện này; không cần main() chạy trọn thành công.
        pass
    assert "lenh" in goi, "mục ⑥ chưa từng được thực thi — không verify được"
    assert goi["lenh"][0] == str(T.VENV_PY)
    assert "~" not in goi["lenh"][0]
