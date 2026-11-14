"""tools/day_do_song_cloud.py — Mac tự commit + đẩy ĐÚNG dữ liệu đo sống lên GitHub (14/11/2026).

VÌ SAO: bác sĩ chọn «Một chiều + tự động» — kho chứng cứ ở lại OneDrive (repo công khai, toàn văn có bản quyền), Cloud chỉ
đọc gương tóm tắt qua git. Đo 14/11: 7 tệp đo sống nằm chờ trên Mac 9 ngày vì không gì commit/đẩy. Chốt giữ: chỉ danh sách
trắng được commit (tệp khác để nguyên), rào Cloud/vắng kho/sai nhánh/🔴, không đẩy commit lạ, đẩy lỗi thì lượt sau đẩy tiếp,
và tu_sua_chua có gọi công cụ (không ai gọi thì như không có — BH41).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    spec = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


DDS = _nap("dds_20261114", "day_do_song_cloud.py")
ENV = {"HOME": "/tmp"}   # không có CLAUDE_CODE_REMOTE


def _g(cwd: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout.strip()


def _dung(tmp_path: Path) -> tuple[Path, Path]:
    """Remote trần + bản sao trên nhánh master có sẵn các tệp đo sống đã track + EBM-Dashboards/."""
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "master", str(remote)], check=True)
    may = tmp_path / "may"
    subprocess.run(["git", "clone", "-q", str(remote), str(may)], check=True, capture_output=True)
    _g(may, "config", "user.email", "t@example.invalid")
    _g(may, "config", "user.name", "Kiem thu")
    _g(may, "checkout", "-q", "-b", "master")
    for rel in ("cloud-mirror/trang-thai-chung-cu.json", "data/sources.json", "README.md", "alerts/2026-11-01.md"):
        p = may / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("v1\n", encoding="utf-8")
    _g(may, "add", "-A")
    _g(may, "commit", "-q", "-m", "goc")
    _g(may, "push", "-q", "origin", "master")
    (may / "EBM-Dashboards").mkdir()
    return remote, may


def _chay(may: Path, **kw) -> int:
    kw.setdefault("moi_truong", ENV)
    kw.setdefault("sinh_guong", lambda r, e: 0)
    kw.setdefault("an_toan", lambda r: 0)
    return DDS.chay(may, **kw)


def _doi_do_song(may: Path) -> None:
    (may / "cloud-mirror/trang-thai-chung-cu.json").write_text("v2\n", encoding="utf-8")
    (may / "alerts/2026-11-13.md").write_text("canh bao\n", encoding="utf-8")
    (may / "README.md").write_text("viec do cua phien khac\n", encoding="utf-8")   # NGOÀI danh sách trắng
    (may / "alerts/con").mkdir()
    (may / "alerts/con/khong.md").write_text("x\n", encoding="utf-8")            # lồng sâu — ngoài danh sách


def test_danh_sach_trang():
    assert DDS.thuoc_danh_sach_trang("alerts/2026-11-13.md")
    assert DDS.thuoc_danh_sach_trang("data/sources.json")
    for rel in ("alerts/con/khong.md", "alerts/2026-11-13.txt", "README.md", "EBM-Dashboards/WebDashboard_x.html",
                "toan_van_oa/PMID-1_CHR.html", "cloud-mirror/khac.json"):
        assert not DDS.thuoc_danh_sach_trang(rel), rel


def test_ap_dung_chi_commit_danh_sach_trang_roi_day(tmp_path):
    remote, may = _dung(tmp_path)
    _doi_do_song(may)
    assert _chay(may, ap_dung=True) == 0
    tep = _g(remote, "show", "--name-only", "--format=", "master").split()
    assert sorted(tep) == ["alerts/2026-11-13.md", "cloud-mirror/trang-thai-chung-cu.json"], tep
    con = _g(may, "status", "--porcelain")
    assert "README.md" in con and "alerts/con/" in con, "tệp ngoài danh sách trắng phải ĐỂ NGUYÊN, chưa commit"


def test_chay_thu_khong_ghi_gi(tmp_path):
    remote, may = _dung(tmp_path)
    _doi_do_song(may)
    truoc = _g(remote, "rev-parse", "master")
    assert _chay(may, ap_dung=False) == 1
    assert _g(remote, "rev-parse", "master") == truoc
    assert _g(may, "rev-parse", "HEAD") == truoc


def test_rao_cloud_vang_kho_sai_nhanh_va_an_toan_do(tmp_path):
    remote, may = _dung(tmp_path)
    _doi_do_song(may)
    truoc = _g(may, "rev-parse", "HEAD")
    assert _chay(may, ap_dung=True, moi_truong={"CLAUDE_CODE_REMOTE": "true"}) == 0
    assert _chay(may, ap_dung=True, dash=tmp_path / "khong_co") == 0
    assert _chay(may, ap_dung=True, an_toan=lambda r: 2) == 2
    _g(may, "checkout", "-q", "-b", "nhanh-khac")
    assert _chay(may, ap_dung=True) == 2
    assert _g(may, "rev-parse", "HEAD") == truoc, "mọi rào phải dừng TRƯỚC khi commit"


def test_khong_day_commit_la(tmp_path):
    remote, may = _dung(tmp_path)
    (may / "README.md").write_text("sua ma\n", encoding="utf-8")
    _g(may, "commit", "-qam", "commit cua bac si")
    truoc = _g(remote, "rev-parse", "master")
    (may / "data/sources.json").write_text("v2\n", encoding="utf-8")
    assert _chay(may, ap_dung=True) == 2
    assert _g(remote, "rev-parse", "master") == truoc


def test_day_loi_thi_giu_commit_luot_sau_day_tiep(tmp_path):
    remote, may = _dung(tmp_path)
    (may / "data/sources.json").write_text("v2\n", encoding="utf-8")
    url = _g(may, "remote", "get-url", "origin")
    # fetch vẫn chạy được nhưng push bị từ chối: remote chỉ-đọc qua pushurl hỏng
    _g(may, "remote", "set-url", "--push", "origin", str(tmp_path / "khong-ton-tai.git"))
    assert _chay(may, ap_dung=True) == 1
    assert _g(may, "status", "--porcelain") == "", "commit phải được giữ cục bộ"
    _g(may, "remote", "set-url", "--push", "origin", url)
    assert _chay(may, ap_dung=False) == 1, "commit đo sống chưa đẩy phải được báo"
    assert _chay(may, ap_dung=True) == 0
    assert _g(remote, "rev-parse", "master") == _g(may, "rev-parse", "HEAD")


def test_tu_sua_chua_goi_cong_cu():
    ts = (REPO / "tools" / "tu_sua_chua.py").read_text(encoding="utf-8")
    dong = [d for d in ts.splitlines() if "day_do_song_cloud.py" in d and not d.lstrip().startswith("#")]
    assert any('"--ap-dung"' in d for d in dong) and any('"--im-khi-on"' in d for d in dong), dong
