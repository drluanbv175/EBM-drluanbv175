"""Luật R7 của chốt đa nền: subprocess CHẾ ĐỘ VĂN BẢN thiếu encoding= (15/10/2026 — DN-01).

Lỗi thật: tools/test_xuat_goi_cap_nhat_workflow_20260904.py gọi `subprocess.run([sys.executable, verify_dashboard…],
capture_output=True, text=True)` không có encoding ⇒ tiến trình cha giải mã stdout UTF-8 của công cụ bằng bảng mã
LOCALE — đỏ dưới `LC_ALL=C PYTHONUTF8=0` (UnicodeDecodeError), sẽ đỏ trên Windows chưa bật chế độ UTF-8 (cp1252 không
có byte 0x8d). CI ép `PYTHONUTF8=1` nên không bao giờ thấy ⇒ chỉ chốt tĩnh bắt được. Ngoại tuyến, tệp tạm.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "kiem_tuong_thich_da_nen.py"
_sp = importlib.util.spec_from_file_location("ktdn_r7_20261015", _TEP)
ktd = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(ktd)


def _r7(tmp_path: Path, noi_dung: str, monkeypatch, thu_muc: str = "tools") -> tuple[list[str], list[str]]:
    """Đặt tệp vào `<tmp>/<thu_muc>/mau.py`, chạy `quet_file`, trả (🔴 R7, 🟡 R7)."""
    d = tmp_path / thu_muc
    d.mkdir(parents=True, exist_ok=True)
    p = d / "mau.py"
    p.write_text(noi_dung, encoding="utf-8", newline="\n")
    monkeypatch.setattr(ktd, "REPO", tmp_path)
    do, vang = ktd.quet_file(p)
    return [x for x in do if " R7 " in x], [x for x in vang if " R7 " in x]


def test_python_con_thieu_encoding_la_do_dung_dong(tmp_path, monkeypatch):
    """Đúng mẫu lỗi thật DN-01 (lời gọi trải nhiều dòng — dòng báo là dòng mở lời gọi)."""
    noi_dung = (
        "import subprocess\n"
        "import sys\n"
        "def f(tool, dash):\n"
        "    r = subprocess.run(\n"
        '        [sys.executable, str(tool), str(dash), "--online"],\n'
        "        capture_output=True, text=True, timeout=30,\n"
        "    )\n"
        "    return r.stdout\n"
    )
    do, vang = _r7(tmp_path, noi_dung, monkeypatch)
    assert len(do) == 1 and "mau.py:4 R7" in do[0] and "sys.executable" in do[0], do
    assert vang == []


def test_co_encoding_thi_sach(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess, sys\n"
        "def f(t):\n"
        '    subprocess.run([sys.executable, t], capture_output=True, text=True, encoding="utf-8", errors="replace")\n'
        '    subprocess.run(["git", "status"], capture_output=True, text=True, encoding="utf-8")\n'
    )
    assert _r7(tmp_path, noi_dung, monkeypatch) == ([], [])


def test_lenh_khac_la_vang_khong_phai_do(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess\n"
        "def f(cay):\n"
        '    return subprocess.run(["git", "-C", cay, "ls-files"], capture_output=True, text=True).stdout\n'
    )
    do, vang = _r7(tmp_path, noi_dung, monkeypatch)
    assert do == [] and len(vang) == 1 and "mau.py:3 R7" in vang[0], (do, vang)


def test_che_do_byte_va_text_false_khong_bao(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess, sys\n"
        "def f(t):\n"
        "    subprocess.run([sys.executable, t], capture_output=True)\n"
        "    subprocess.run([sys.executable, t], capture_output=True, text=False)\n"
    )
    assert _r7(tmp_path, noi_dung, monkeypatch) == ([], [])


def test_universal_newlines_va_bi_danh_import_deu_bi_bat(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess as _sp\n"
        "import sys as _sys\n"
        "from subprocess import run as chay, Popen\n"
        "def f(t):\n"
        "    _sp.check_output([_sys.executable, t], universal_newlines=True)\n"
        '    chay(["bash", t], text=True)\n'
        "    Popen((_sys.executable, t), stdout=_sp.PIPE, text=True)\n"
    )
    do, vang = _r7(tmp_path, noi_dung, monkeypatch)
    assert sorted(x.split(" R7")[0] for x in do) == ["tools/mau.py:5", "tools/mau.py:7"], do
    assert len(vang) == 1 and "mau.py:6 R7" in vang[0], vang


def test_kwargs_va_text_bien_khong_phan(tmp_path, monkeypatch):
    """`**kw` có thể mang encoding; `text=<biến>` không chứng minh được là True — không bịa vi phạm."""
    noi_dung = (
        "import subprocess, sys\n"
        "def f(t, kw, van_ban):\n"
        "    subprocess.run([sys.executable, t], text=True, **kw)\n"
        "    subprocess.run([sys.executable, t], text=van_ban)\n"
    )
    assert _r7(tmp_path, noi_dung, monkeypatch) == ([], [])


def test_encoding_none_viet_ro_van_la_vi_pham(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess, sys\n"
        "def f(t):\n"
        "    subprocess.run([sys.executable, t], text=True, encoding=None)\n"
    )
    do, _ = _r7(tmp_path, noi_dung, monkeypatch)
    assert len(do) == 1, do


def test_ham_trung_ten_khong_phai_subprocess_khong_bao(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess\n"
        "def run(lenh, text=False):\n"
        "    return lenh\n"
        "def f(t, may):\n"
        "    run([t], text=True)\n"
        "    may.run([t], text=True)\n"
    )
    assert _r7(tmp_path, noi_dung, monkeypatch) == ([], [])


def test_mien_tru_o_dong_bat_ky_cua_loi_goi(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess, sys\n"
        "def f(t):\n"
        "    subprocess.run(\n"
        "        [sys.executable, t],\n"
        "        text=True,  # da-nen: bo-qua (tiến trình con chỉ in ASCII, đã đo)\n"
        "    )\n"
    )
    assert _r7(tmp_path, noi_dung, monkeypatch) == ([], [])


def test_vi_du_trong_docstring_khong_bi_bao(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess\n"
        "def f():\n"
        '    """Vi du: subprocess.run([sys.executable, "x"], text=True) — chi la van ban."""\n'
        "    return 1\n"
    )
    assert _r7(tmp_path, noi_dung, monkeypatch) == ([], [])


def test_cay_ngoai_git_chi_vang(tmp_path, monkeypatch):
    """EBM-Dashboards/tools nằm ngoài git (CI không thấy) ⇒ 🟡 dù gọi Python con."""
    monkeypatch.setattr(ktd, "CAY_NGOAI_GIT", (tmp_path / "EBM-Dashboards" / "tools",))
    noi_dung = (
        "import subprocess, sys\n"
        "def f(t):\n"
        "    subprocess.run([sys.executable, t], capture_output=True, text=True)\n"
    )
    do, vang = _r7(tmp_path, noi_dung, monkeypatch, thu_muc="EBM-Dashboards/tools")
    assert do == [] and len(vang) == 1 and "cây ngoài git" in vang[0], (do, vang)


def test_tep_loi_cu_phap_lui_ve_doc_theo_dong_khong_doc_thanh_sach(tmp_path, monkeypatch):
    noi_dung = (
        "import subprocess, sys\n"
        "def f(t):\n"
        "    subprocess.run([sys.executable, t], text=True)\n"
        "    if True\n"
    )
    do, vang = _r7(tmp_path, noi_dung, monkeypatch)
    assert do == [] and len(vang) == 1 and "lỗi cú pháp" in vang[0], (do, vang)
    assert ktd.dong_r7_vi_pham(noi_dung) is None


def test_tep_that_cua_loi_dn01_nay_sach_r7():
    """Hồi quy trên MÃ SỐNG: lời gọi của test bộ năm (gốc DN-01) và các test cùng họ đã có encoding."""
    goc = Path(__file__).resolve().parent
    for ten in ("test_xuat_goi_cap_nhat_workflow_20260904.py", "test_kiem_mau_the_chung_cu_tuan.py",
                "test_dong_bo_tat_ca_ten_may_workflow_20260904.py"):
        p = goc / ten
        assert ktd.dong_r7_vi_pham(p.read_text(encoding="utf-8")) == [], ten
