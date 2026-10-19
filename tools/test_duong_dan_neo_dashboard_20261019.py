# -*- coding: utf-8 -*-
"""Kiểm build_library.py và make_derivatives.py ghi CẠNH dashboard, không theo thư mục đang đứng (19/10/2026).

Ca thật: xuất gói THA ngoại trú, chạy hai công cụ từ GỐC repo — `build_library.py add EBM-Dashboards/<dashboard>.html`
nối dashboard vào một library.json cũ ở gốc (4 → 5 bản, liên kết tương đối không mở được dashboard), còn
`make_derivatives.py` tạo thư mục derivatives/ ở gốc, tách khỏi bộ năm trong EBM-Dashboards/derivatives/.
Chạy đúng như người gọi thật: tiến trình con, cwd là một thư mục KHÁC thư mục của dashboard. Ngoại tuyến, chỉ tmp_path.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MAU = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "templates" / "web-dashboard-evidence-workbench.html"
BAN = [REPO / "sync" / "skills" / ten / "tools" for ten in ("cap-nhat-chung-cu-y-khoa", "dark-analyst")]
TEN = "WebDashboard_EBM_VanDeCuThe_Thu_20261019.html"


def _chay(tool: Path, *doi_so: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(tool), *doi_so], cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120)


@pytest.fixture
def cay(tmp_path):
    """gốc/ (nơi đứng, có library.json cũ) + gốc/kho/ (thư mục dashboard, có thư viện chuẩn)."""
    goc = tmp_path / "goc"
    kho = goc / "kho"
    kho.mkdir(parents=True)
    shutil.copyfile(MAU, kho / TEN)
    (goc / "library.json").write_text(json.dumps([{"file": "Cu.html", "updated": "2026-06-28"}]), encoding="utf-8")
    (kho / "library.json").write_text(json.dumps([{"file": "Khac.html", "updated": "2026-10-01"}]), encoding="utf-8")
    return goc, kho


@pytest.mark.parametrize("thu_muc", BAN, ids=lambda p: p.parent.name)
def test_build_library_add_ghi_canh_dashboard_khong_theo_cwd(cay, thu_muc):
    goc, kho = cay
    kq = _chay(thu_muc / "build_library.py", "add", f"kho/{TEN}", cwd=goc)
    assert kq.returncode == 0, kq.stdout + kq.stderr
    chuan = json.loads((kho / "library.json").read_text(encoding="utf-8"))
    assert {e["file"] for e in chuan} == {"Khac.html", TEN}, "phải nối vào thư viện CẠNH dashboard"
    assert (kho / "evidence-library.html").is_file()
    assert json.loads((goc / "library.json").read_text(encoding="utf-8")) == [
        {"file": "Cu.html", "updated": "2026-06-28"}], "không được đụng library.json ở thư mục đang đứng"
    assert not (goc / "evidence-library.html").exists()


@pytest.mark.parametrize("thu_muc", BAN, ids=lambda p: p.parent.name)
def test_build_library_tu_choi_mo_ho_va_thu_vien_rong(cay, tmp_path, thu_muc):
    goc, kho = cay
    khac = tmp_path / "khac"
    khac.mkdir()
    shutil.copyfile(MAU, khac / "WebDashboard_EBM_VanDeCuThe_Khac_20261019.html")
    kq = _chay(thu_muc / "build_library.py", "add", f"kho/{TEN}", str(khac / "WebDashboard_EBM_VanDeCuThe_Khac_20261019.html"),
               cwd=goc)
    assert kq.returncode == 1 and "--thu-vien" in kq.stdout, "dashboard ở hai thư mục ⇒ không đoán thư viện"
    trong = tmp_path / "trong"
    trong.mkdir()
    kq = _chay(thu_muc / "build_library.py", "build", cwd=trong)
    assert kq.returncode == 1 and not (trong / "evidence-library.html").exists(), "không dựng thư viện rỗng ở chỗ lạ"
    kq = _chay(thu_muc / "build_library.py", "build", "--thu-vien", str(kho), cwd=trong)
    assert kq.returncode == 0 and (kho / "evidence-library.html").is_file()


@pytest.mark.parametrize("thu_muc", BAN, ids=lambda p: p.parent.name)
def test_make_derivatives_ghi_canh_dashboard_khong_theo_cwd(cay, thu_muc):
    goc, kho = cay
    kq = _chay(thu_muc / "make_derivatives.py", f"kho/{TEN}", cwd=goc)
    assert kq.returncode == 0, kq.stdout + kq.stderr
    assert not (goc / "derivatives").exists(), "không tạo derivatives/ ở thư mục đang đứng"
    sinh = sorted(p.name for p in (kho / "derivatives").iterdir())
    assert len(sinh) == 3 and all(n.endswith(".md") for n in sinh), sinh


@pytest.mark.parametrize("thu_muc", BAN, ids=lambda p: p.parent.name)
def test_make_derivatives_outdir_tuong_minh_van_duoc_ton_trong(cay, tmp_path, thu_muc):
    goc, kho = cay
    ra = tmp_path / "ra"
    kq = _chay(thu_muc / "make_derivatives.py", f"kho/{TEN}", "--outdir", str(ra), cwd=goc)
    assert kq.returncode == 0 and len(list(ra.iterdir())) == 3 and not (kho / "derivatives").exists()
