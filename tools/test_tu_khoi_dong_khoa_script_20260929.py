"""Hook tự khởi động KHÔNG phóng chồng lượt giám sát do nơi khác phóng — vá 29/09/2026.

29/09: tác vụ lịch nổ bù weekly_safety.sh lúc 18:31 (máy vừa bật); 18:33 `tu_khoi_dong` thấy log «BẮT ĐẦU chưa KẾT THÚC»,
khoá PID riêng của nó rỗng (không phải nó phóng) ⇒ tưởng lượt đó đã chết ⇒ phóng thêm lượt thứ hai. Nay nó đọc khoá một
lượt của CHÍNH script (`medical-ebm-automation/scripts/_khoa_mot_luot.sh`, `$EBM_KHOA_DIR/<tên script>.khoa/{pid,luc}`).
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_khoi_dong.py"


@pytest.fixture()
def M(tmp_path, monkeypatch):
    sp = importlib.util.spec_from_file_location("tkd_khoa_script_20260929", _TEP)
    mod = importlib.util.module_from_spec(sp)
    sys.modules["tkd_khoa_script_20260929"] = mod
    sp.loader.exec_module(mod)
    monkeypatch.setenv("EBM_KHOA_DIR", str(tmp_path / "khoa"))
    return mod


def _khoa(tmp_path: Path, pid: int, luc: float) -> None:
    d = tmp_path / "khoa" / "weekly_safety.khoa"
    d.mkdir(parents=True)
    (d / "pid").write_text(f"{pid}\n", encoding="utf-8", newline="\n")
    (d / "luc").write_text(f"{int(luc)}\n", encoding="utf-8", newline="\n")


def _pid_da_chet() -> int:
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


def test_khoa_cua_tien_trinh_con_song_va_moi(M, tmp_path):
    _khoa(tmp_path, os.getpid(), time.time())
    assert M._khoa_script_dang_giu("tuan") == os.getpid()


def test_khoa_qua_han_tien_trinh_chet_hoac_khong_co_thi_khong_giu(M, tmp_path):
    assert M._khoa_script_dang_giu("tuan") is None
    _khoa(tmp_path, os.getpid(), time.time() - M.KHOA_SCRIPT_HAN_GIAY - 60)
    assert M._khoa_script_dang_giu("tuan") is None, "PID có thể bị cấp lại sau khi khởi động lại — khoá quá hạn không tính"
    (tmp_path / "khoa" / "weekly_safety.khoa" / "pid").write_text(f"{_pid_da_chet()}\n", encoding="utf-8")
    (tmp_path / "khoa" / "weekly_safety.khoa" / "luc").write_text(f"{int(time.time())}\n", encoding="utf-8")
    assert M._khoa_script_dang_giu("tuan") is None


@pytest.fixture()
def chay_main(M, tmp_path, monkeypatch, capsys):
    """Lượt «tuần» quá hạn, không có lượt nào do chính hook phóng; ghi lại việc phóng thay vì phóng thật."""
    da_phong: list[str] = []
    monkeypatch.setattr(M, "CONG_TAC_TAT", tmp_path / "khong-co")
    monkeypatch.setattr(M, "_canh_lich_nen", lambda: None)
    monkeypatch.setattr(M, "dang_chay", lambda: None)
    monkeypatch.setattr(M, "qua_han", lambda: [("tuan", 0)])
    monkeypatch.setattr(M, "phong", lambda ma: da_phong.append(ma) or (True, "giả"))
    monkeypatch.setattr(sys, "argv", ["tu_khoi_dong.py", "--phong"])

    def _chay() -> tuple[int, list[str], str]:
        ma = M.main()
        return ma, da_phong, capsys.readouterr().out
    return _chay


def test_lượt_do_noi_khac_phong_dang_chay_thi_khong_phong_chong(chay_main, tmp_path):
    _khoa(tmp_path, os.getpid(), time.time())
    ma, da_phong, out = chay_main()
    assert da_phong == [], "script đang giữ khoá một lượt mà hook vẫn phóng thêm — hai lượt chạy chồng (29/09)"
    assert ma == 0 and "Đang chạy" in out


def test_khong_ai_giu_khoa_thi_van_phong_binh_thuong(chay_main):
    ma, da_phong, _out = chay_main()
    assert da_phong == ["tuan"] and ma == 0
