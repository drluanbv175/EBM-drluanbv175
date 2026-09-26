"""Cảm biến CI của `tu_de_xuat_viec.py` CHỈ đọc run của NHÁNH MẶC ĐỊNH — 26/09/2026 (mục #9).

Ca thật cùng ngày: run #838 (nhánh `claude/*`, success) che run #837 (nhánh mặc định repo y khoa,
FAILURE) vì cảm biến đọc «run hoàn tất mới nhất» trên MỌI nhánh. Test khoá:
  • URL API mang `branch=` (urlencode, giữ đúng tên nhánh có «/»);
  • run trả về mang `head_branch` khác ⇒ «» và đúng 1 giác quan chết (không bao giờ «success»);
  • dò nhánh mặc định hỏng hết ⇒ «», KHÔNG gửi truy vấn không lọc nhánh;
  • symbolic-ref hỏng (đúng ca Cloud) ⇒ lùi API `default_branch` rồi bảng khai báo CLAUDE.md;
  • đường `gh`: DÒNG thi hành có `--branch`, và headBranch trả về được SO với nhánh.

Ngoại tuyến: `urlopen` giả, `_chay` giả, repo git dựng trong thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_ci_nhanh", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

NHANH_YK = "feat/r1-1-2-design-gap-remediation"


def _g(cay: Path, *a: str) -> None:
    subprocess.run(["git", *a], cwd=cay, check=True, capture_output=True, text=True)


def _repo(tmp_path: Path, url: str, head_symbolic: str | None = None) -> Path:
    cay = tmp_path / "cay"
    cay.mkdir()
    _g(cay, "init", "-q", "-b", "master")
    _g(cay, "remote", "add", "origin", url)
    if head_symbolic:
        _g(cay, "config", "user.email", "t@t.t")
        _g(cay, "config", "user.name", "t")
        _g(cay, "config", "commit.gpgsign", "false")
        (cay / "a.txt").write_text("1", encoding="utf-8")
        _g(cay, "add", "-A")
        _g(cay, "commit", "-qm", "c1")
        _g(cay, "update-ref", f"refs/remotes/origin/{head_symbolic}", "HEAD")
        _g(cay, "symbolic-ref", "refs/remotes/origin/HEAD", f"refs/remotes/origin/{head_symbolic}")
    return cay


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _mo_gia(tuyen: dict, bat: list[str]):
    """urlopen giả: khớp theo đoạn cuối URL (trước «?»); giá trị Exception ⇒ ném."""
    def mo(req, timeout=0):
        url = req.full_url
        bat.append(url)
        for khoa, payload in tuyen.items():
            if url.split("?")[0].endswith(khoa):
                if isinstance(payload, Exception):
                    raise payload
                return _Resp(json.dumps(payload).encode())
        raise OSError(f"không có tuyến giả cho {url}")
    return mo


@pytest.fixture(autouse=True)
def _sach():
    M._GIAC_QUAN_CHET.clear()
    M._SO_GIAC_QUAN["chay"] = 0


# ---------- doc_ci_qua_api: lọc nhánh + phòng thủ head_branch ----------

def test_url_api_co_branch_urlencode(tmp_path):
    bat: list[str] = []
    kq = M.doc_ci_qua_api(_repo(tmp_path, "https://github.com/chu/kho"), "ci.yml", NHANH_YK,
                          urlopen=_mo_gia({"/runs": {"workflow_runs": [
                              {"conclusion": "failure", "head_branch": NHANH_YK}]}}, bat))
    assert kq == "failure"
    assert bat == ["https://api.github.com/repos/chu/kho/actions/workflows/ci.yml/runs"
                   "?status=completed&per_page=1&branch=feat%2Fr1-1-2-design-gap-remediation"]
    assert M._GIAC_QUAN_CHET == []


@pytest.mark.parametrize("dau", ["claude/focused-fermat-4nnttd", None])
def test_run_nhanh_khac_khong_bao_gio_success(tmp_path, dau):
    """API trả run của nhánh khác (hoặc thiếu head_branch) ⇒ «» và đúng 1 giác quan chết."""
    kq = M.doc_ci_qua_api(_repo(tmp_path, "https://github.com/chu/kho"), "ci.yml", NHANH_YK,
                          urlopen=_mo_gia({"/runs": {"workflow_runs": [
                              {"conclusion": "success", "head_branch": dau}]}}, []))
    assert kq == ""
    assert len(M._GIAC_QUAN_CHET) == 1


def test_nhanh_rong_khong_gui_truy_van_khong_loc(tmp_path):
    bat: list[str] = []
    kq = M.doc_ci_qua_api(_repo(tmp_path, "https://github.com/chu/kho"), "ci.yml", "",
                          urlopen=_mo_gia({"/runs": {"workflow_runs": [
                              {"conclusion": "success", "head_branch": "master"}]}}, bat))
    assert kq == "" and bat == []
    assert len(M._GIAC_QUAN_CHET) == 1


# ---------- _nhanh_mac_dinh: thứ tự dò ----------

def test_symbolic_ref_la_nac_dau_khong_goi_mang(tmp_path):
    bat: list[str] = []
    cay = _repo(tmp_path, "https://github.com/chu/kho", head_symbolic="nhanh-chinh")
    assert M._nhanh_mac_dinh(cay, urlopen=_mo_gia({}, bat), co_gh=False) == "nhanh-chinh"
    assert bat == []


def test_symbolic_ref_hong_lui_api_default_branch(tmp_path):
    bat: list[str] = []
    cay = _repo(tmp_path, "https://github.com/chu/kho")
    nhanh = M._nhanh_mac_dinh(cay, urlopen=_mo_gia({"/repos/chu/kho": {"default_branch": "trunk"}}, bat),
                              co_gh=False)
    assert nhanh == "trunk"
    assert bat == ["https://api.github.com/repos/chu/kho"]


def test_symbolic_ref_va_api_hong_repo_khai_bao_lui_bang_claude_md(tmp_path):
    """Nấc cuối: bảng khai báo (kiem_cay_lam_viec.NHANH_CHINH) — KHÔNG phải «main»."""
    cay = _repo(tmp_path, "https://github.com/chu/medical-ebm-automation.git")
    nhanh = M._nhanh_mac_dinh(cay, urlopen=_mo_gia({"/repos/chu/medical-ebm-automation": OSError("x")}, []),
                              co_gh=False)
    assert nhanh == NHANH_YK


def test_do_hong_het_khong_ra_success_khong_truy_van_khong_loc(tmp_path):
    bat: list[str] = []
    cay = _repo(tmp_path, "https://github.com/chu/repo-la")
    mo = _mo_gia({"/repos/chu/repo-la": OSError("mang"),
                  "/runs": {"workflow_runs": [{"conclusion": "success", "head_branch": "master"}]}}, bat)
    kq, nhanh = M.doc_ci_mot_repo("gốc", cay, "ci.yml", co_gh=False, urlopen=mo)
    assert (kq, nhanh) == ("", "")
    assert not any("/runs" in u for u in bat), "dò nhánh hỏng mà vẫn hỏi run KHÔNG lọc nhánh"
    assert len(M._GIAC_QUAN_CHET) == 1
    assert M._SO_GIAC_QUAN["chay"] == 1          # giác quan được đếm ⇒ bảng «x/y» không lệch


def test_do_hong_het_duong_gh_khong_goi_gh_run_list(tmp_path, monkeypatch):
    """Đường gh: dò nhánh hỏng ⇒ KHÔNG chạy `gh run list` (với `--branch ""` gh trả run mọi nhánh)."""
    goi: list[list[str]] = []
    monkeypatch.setattr(M, "_nhanh_mac_dinh", lambda *a, **k: "")
    monkeypatch.setattr(M, "_chay", lambda lenh, giay=120, cwd=None: goi.append(lenh) or "success master")
    assert M.doc_ci_mot_repo("gốc", tmp_path, "ci.yml", co_gh=True) == ("", "")
    assert goi == []
    assert len(M._GIAC_QUAN_CHET) == 1


def test_doc_ci_mot_repo_api_dung_nhanh_mac_dinh(tmp_path):
    bat: list[str] = []
    cay = _repo(tmp_path, "https://github.com/chu/medical-ebm-automation")
    mo = _mo_gia({"/repos/chu/medical-ebm-automation": {"default_branch": NHANH_YK},
                  "/runs": {"workflow_runs": [{"conclusion": "failure", "head_branch": NHANH_YK}]}}, bat)
    assert M.doc_ci_mot_repo("y khoa", cay, "offline-ci.yml", co_gh=False, urlopen=mo) == ("failure", NHANH_YK)
    assert "branch=feat%2Fr1-1-2-design-gap-remediation" in bat[-1]


# ---------- đường gh ----------

def test_dong_gh_thi_hanh_co_branch():
    """Khớp DÒNG thi hành (không khớp cả tệp — bình luận cùng chuỗi làm xanh giả)."""
    nguon = _TEP.read_text(encoding="utf-8")
    dong = [x for x in nguon.splitlines() if '"gh", "run", "list"' in x and "_chay(" in x]
    assert len(dong) == 1
    assert '"--branch", nhanh' in dong[0] and '"--status", "completed"' in dong[0]


@pytest.mark.parametrize("ra, mong", [
    (f"failure {NHANH_YK}\n", "failure"),
    (f"success {NHANH_YK}\n", "success"),
    ("success claude/focused-fermat-4nnttd\n", ""),   # nhánh khác ⇒ không đo được
    (" \n", ""),                                      # không có run hoàn tất trên nhánh
])
def test_duong_gh_so_head_branch(tmp_path, monkeypatch, ra, mong):
    cay = _repo(tmp_path, "https://github.com/chu/medical-ebm-automation", head_symbolic=NHANH_YK)
    lenh_bat: list[list[str]] = []

    def chay_gia(lenh, giay=120, cwd=None):
        M._SO_GIAC_QUAN["chay"] += 1
        lenh_bat.append(lenh)
        return ra
    monkeypatch.setattr(M, "_chay", chay_gia)
    kq, nhanh = M.doc_ci_mot_repo("y khoa", cay, "offline-ci.yml", co_gh=True, urlopen=_mo_gia({}, []))
    assert (kq, nhanh) == (mong, NHANH_YK)
    assert lenh_bat and lenh_bat[0][lenh_bat[0].index("--branch") + 1] == NHANH_YK
    assert len(M._GIAC_QUAN_CHET) == (0 if mong else 1)
