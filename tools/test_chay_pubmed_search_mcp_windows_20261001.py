"""Lớp bọc MCP pubmed-search trên Windows: `os.execvpe` không thay tiến trình (01/10/2026) — ngoại tuyến, đa nền.

`os.exec*` trên Windows tạo một tiến trình MỚI rồi cho tiến trình hiện tại thoát NGAY với mã 0 (đo: cha `poll()` = 0 sau vài
giây, con vẫn chạy) và không bọc dấu nháy đối số có dấu cách. Đo trên máy Windows thật: qua lớp bọc, khởi chạy MCP thành công
3/6 lượt (python lớp bọc) và 5/6 (`uv run`), còn `uvx` chạy thẳng 6/6. Bản vá `chay_may_chu(la_windows=True)` chạy máy chủ như tiến
trình CON (stdio kế thừa), chờ nó và trả đúng mã thoát; POSIX giữ nguyên `os.execvpe`. `la_windows` là tham số nên ca thử Windows
chạy được ở mọi nền (CI Ubuntu lẫn Windows).
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "mcp" / "chay_pubmed_search_mcp.py"
_sp = importlib.util.spec_from_file_location("chay_pubmed_search_mcp_test", _TEP)
M = importlib.util.module_from_spec(_sp)
sys.modules["chay_pubmed_search_mcp_test"] = M
_sp.loader.exec_module(M)


def _con(tmp_path: Path, than: str) -> Path:
    tep = tmp_path / "con.py"
    tep.write_text(textwrap.dedent(than), encoding="utf-8")
    return tep


def test_windows_cha_cho_con_roi_tra_dung_ma_thoat(tmp_path):
    dau = tmp_path / "con-xong.marker"
    con = _con(tmp_path, f"""
        import sys, time
        time.sleep(1.0)
        open({str(dau)!r}, "w").write("x")
        sys.exit(7)
    """)
    b = time.time()
    rc = M.chay_may_chu([sys.executable, str(con)], os.environ.copy(), la_windows=True)
    assert rc == 7, "phải trả ĐÚNG mã thoát của máy chủ (execvpe-trên-Windows trả 0 ngay)"
    assert dau.exists(), "lớp bọc trả về TRƯỚC khi máy chủ xong — đúng triệu chứng của os.exec* trên Windows"
    assert time.time() - b >= 0.9


def test_windows_stdio_ke_thua_stdin_stdout_stderr(tmp_path):
    """Chạy `chay_may_chu` trong một tiến trình riêng nối ống: dòng gửi vào stdin phải tới con, stdout/stderr của con phải tới cha."""
    con = _con(tmp_path, """
        import sys
        dong = sys.stdin.readline().strip()
        print("PHAN-HOI:" + dong, flush=True)
        print("LOI:" + dong, file=sys.stderr, flush=True)
    """)
    ma = (f"import sys; sys.path.insert(0, {str(_TEP.parent)!r}); import chay_pubmed_search_mcp as M; "
          f"sys.exit(M.chay_may_chu([sys.executable, {str(con)!r}], dict(__import__('os').environ), la_windows=True))")
    p = subprocess.run([sys.executable, "-B", "-c", ma], input=b"XIN-CHAO\n", capture_output=True, timeout=60)
    assert p.returncode == 0
    assert b"PHAN-HOI:XIN-CHAO" in p.stdout
    assert b"LOI:XIN-CHAO" in p.stderr


def test_windows_doi_so_co_dau_cach_khong_bi_tach(tmp_path):
    dau = tmp_path / "argv.txt"
    con = _con(tmp_path, f"""
        import sys
        open({str(dau)!r}, "w", encoding="utf-8").write(repr(sys.argv[1:]))
    """)
    M.chay_may_chu([sys.executable, str(con), "có dấu cách", "a b"], os.environ.copy(), la_windows=True)
    assert dau.read_text(encoding="utf-8") == repr(["có dấu cách", "a b"])


def test_windows_khong_dung_execvpe(monkeypatch, tmp_path):
    def _cam(*_a, **_k):
        raise AssertionError("Windows không được gọi os.execvpe — nó không thay tiến trình")
    monkeypatch.setattr(M.os, "execvpe", _cam)
    con = _con(tmp_path, "pass\n")
    assert M.chay_may_chu([sys.executable, str(con)], os.environ.copy(), la_windows=True) == 0


def test_posix_van_goi_execvpe_dung_doi_so(monkeypatch):
    cuoc = []
    monkeypatch.setattr(M.os, "execvpe", lambda *a: cuoc.append(a))
    monkeypatch.setattr(M.subprocess, "call", lambda *a, **k: pytest.fail("POSIX không được chạy tiến trình con"))
    env = {"PATH": "x"}
    assert M.chay_may_chu(["uvx", "pubmed-search-mcp"], env, la_windows=False) == 0
    assert cuoc == [("uvx", ["uvx", "pubmed-search-mcp"], env)]


def test_windows_phan_giai_duong_dan_theo_PATH_cua_env(monkeypatch):
    """CreateProcess tìm tệp thực thi theo PATH của tiến trình CHA — nên phải phân giải sẵn theo PATH của `env` truyền cho con."""
    thay = {}
    monkeypatch.setattr(M.shutil, "which", lambda ten, path=None: thay.update(ten=ten, path=path) or r"C:\x\uvx.EXE")
    goi = []
    monkeypatch.setattr(M.subprocess, "call", lambda lenh, env=None: goi.append((lenh, env)) or 0)
    env = {"PATH": r"C:\x"}
    assert M.chay_may_chu(["uvx", "pubmed-search-mcp"], env, la_windows=True) == 0
    assert thay == {"ten": "uvx", "path": r"C:\x"}
    assert goi == [([r"C:\x\uvx.EXE", "pubmed-search-mcp"], env)]


def test_windows_khong_chay_duoc_thi_tra_1_va_noi_ro(capsys):
    assert M.chay_may_chu(["khong-ton-tai-xyz-pubmed"], {"PATH": ""}, la_windows=True) == 1
    assert "không chạy được" in capsys.readouterr().err


def test_mac_dinh_la_windows_theo_os_name(monkeypatch):
    monkeypatch.setattr(M.os, "name", "nt")
    goi = []
    monkeypatch.setattr(M.shutil, "which", lambda ten, path=None: ten)
    monkeypatch.setattr(M.subprocess, "call", lambda lenh, env=None: goi.append(lenh) or 0)
    monkeypatch.setattr(M.os, "execvpe", lambda *a: pytest.fail("os.name == 'nt' phải đi đường tiến trình con"))
    assert M.chay_may_chu(["a", "b"], {"PATH": ""}) == 0 and goi == [["a", "b"]]
