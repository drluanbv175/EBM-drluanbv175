"""Cảm biến CI đường `gh` chịu được mạng chập chờn — 30/09/2026 (BH134).

Ca thật 28–30/09 trên máy Windows: DNS nội bộ trượt lần phân giải ĐẦU sau khi bộ đệm nguội ⇒ `gh run list` in
«error connecting to api.github.com». `_chay` gộp stderr vào stdout nên công cụ tách chữ «connecting» thành TÊN NHÁNH,
báo ⚪ «run trả về nhánh «connecting»» — không thử lại, không lùi sang API công khai, kể cả sau khi bác sĩ đã đăng nhập
lại gh (đo 8 lần liên tiếp: lần 1 lỗi sau 12 s, lần 2 được, các lần sau < 1 s). Test khoá:
  • lỗi kết nối rồi được ⇒ đo được, nghỉ đúng 1 lần, 0 giác quan chết, vẫn đếm MỘT giác quan;
  • lỗi kết nối cả hai lần ⇒ «», đúng 1 giác quan chết ghi NGUYÊN NHÂN thật, không gọi API (cùng máy chủ vừa trượt);
  • mạng đã hỏng ở repo trước ⇒ repo sau chỉ thử MỘT lần (bên gọi cho cả công cụ 90 s);
  • gh hỏng KHÔNG phải vì mạng (token) ⇒ không thử lại gh, lùi sang API công khai và đo được;
  • gh treo hết hạn ⇒ không thử lại, không gọi API; gh không khởi động được ⇒ lùi sang API;
  • câu trả lời THẬT của gh (nhánh khác / chưa có run) không bị coi là lỗi: không thử lại, không gọi API.
Ngoại tuyến: `_chay`, `urlopen`, `ngu` đều giả; repo git dựng trong thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_ci_gh_thu_lai", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

NHANH = "feat/r1-1-2-design-gap-remediation"
LOI_MANG = "error connecting to api.github.com\ncheck your internet connection or https://githubstatus.com\n"
LOI_TOKEN = "HTTP 401: Bad credentials (https://api.github.com/graphql)\nTry authenticating with:  gh auth login\n"
RUN_API = {"/runs": {"workflow_runs": [{"conclusion": "failure", "head_branch": NHANH}]}}


def _g(cay: Path, *a: str) -> None:
    subprocess.run(["git", *a], cwd=cay, check=True, capture_output=True, text=True)


@pytest.fixture()
def cay(tmp_path: Path) -> Path:
    """Repo tạm mà `_nhanh_mac_dinh` trả NHANH ngay ở nấc symbolic-ref (không gọi mạng)."""
    goc = tmp_path / "cay"
    goc.mkdir()
    _g(goc, "init", "-q", "-b", "master")
    _g(goc, "remote", "add", "origin", "https://github.com/chu/medical-ebm-automation")
    for khoa, gia_tri in (("user.email", "t@t.t"), ("user.name", "t"), ("commit.gpgsign", "false")):
        _g(goc, "config", khoa, gia_tri)
    (goc / "a.txt").write_text("1", encoding="utf-8")
    _g(goc, "add", "-A")
    _g(goc, "commit", "-qm", "c1")
    _g(goc, "update-ref", f"refs/remotes/origin/{NHANH}", "HEAD")
    _g(goc, "symbolic-ref", "refs/remotes/origin/HEAD", f"refs/remotes/origin/{NHANH}")
    return goc


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


def _chay_kich_ban(monkeypatch, ra: list[str], ghi_chet: str = "") -> list[list[str]]:
    """`_chay` giả trả lần lượt `ra` (hết thì lặp phần tử cuối); `ghi_chet` ≠ «» ⇒ giả lập `_chay` thật tự ghi
    giác quan chết (quá giờ / không khởi động được) rồi trả chuỗi rỗng."""
    goi: list[list[str]] = []

    def chay_gia(lenh, giay=120, cwd=None):
        M._SO_GIAC_QUAN["chay"] += 1
        goi.append(lenh)
        if ghi_chet:
            M._ghi_chet(lenh, ghi_chet)
            return ""
        return ra[min(len(goi), len(ra)) - 1]
    monkeypatch.setattr(M, "_chay", chay_gia)
    return goi


@pytest.fixture(autouse=True)
def _sach():
    M._GIAC_QUAN_CHET.clear()
    M._SO_GIAC_QUAN["chay"] = 0
    M._MANG_GH["hong"] = False


def _do(cay: Path, tuyen: dict, bat: list[str], ngu: list[float]) -> tuple[str, str]:
    return M.doc_ci_mot_repo("y khoa", cay, "offline-ci.yml", co_gh=True, urlopen=_mo_gia(tuyen, bat),
                             ngu=ngu.append)


# ---------- phân biệt câu trả lời của gh với thông báo lỗi ----------

@pytest.mark.parametrize("out, mong", [
    (f"success {NHANH}\n", (True, "success", NHANH)),
    ("timed_out master\n", (True, "timed_out", "master")),
    (" \n", (True, "", "")),                       # chưa có run hoàn tất: vẫn là câu trả lời
    (LOI_MANG, (False, "", "")),
    ("error connecting\n", (False, "", "")),       # đúng 2 chữ, nhưng «error» không phải conclusion
    (LOI_TOKEN, (False, "", "")),
    ("success\n", (False, "", "")),                # thiếu nhánh ⇒ không tin
])
def test_doc_tra_loi_gh(out, mong):
    assert M._doc_tra_loi_gh(out) == mong


# ---------- lỗi kết nối: thử lại ----------

def test_loi_ket_noi_roi_duoc_thi_do_duoc(cay, monkeypatch):
    goi = _chay_kich_ban(monkeypatch, [LOI_MANG, f"failure {NHANH}\n"])
    bat: list[str] = []
    ngu: list[float] = []
    assert _do(cay, RUN_API, bat, ngu) == ("failure", NHANH)
    assert len(goi) == 2 and ngu == [M._NGHI_THU_LAI_GH]
    assert M._GIAC_QUAN_CHET == []
    assert M._SO_GIAC_QUAN["chay"] == 1            # MỘT giác quan dù thử hai lần ⇒ bảng «x/y» không lệch
    assert bat == [] and M._MANG_GH["hong"] is False


def test_loi_ket_noi_ca_hai_lan_ghi_dung_nguyen_nhan(cay, monkeypatch):
    goi = _chay_kich_ban(monkeypatch, [LOI_MANG])
    bat: list[str] = []
    assert _do(cay, RUN_API, bat, []) == ("", NHANH)
    assert len(goi) == 2
    assert len(M._GIAC_QUAN_CHET) == 1
    ly_do = M._GIAC_QUAN_CHET[0]
    assert "error connecting to api.github.com" in ly_do and "y khoa" in ly_do and "2 lần" in ly_do
    assert "«connecting»" not in ly_do, "chữ trong thông báo lỗi lại bị đọc thành tên nhánh"
    assert M._SO_GIAC_QUAN["chay"] == 1
    assert bat == []                               # cùng máy chủ vừa trượt ⇒ không tốn thêm một lượt API
    assert M._MANG_GH["hong"] is True


def test_mang_da_hong_repo_sau_chi_thu_mot_lan(cay, monkeypatch):
    M._MANG_GH["hong"] = True
    goi = _chay_kich_ban(monkeypatch, [LOI_MANG])
    ngu: list[float] = []
    assert _do(cay, RUN_API, [], ngu) == ("", NHANH)
    assert len(goi) == 1 and ngu == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "1 lần" in M._GIAC_QUAN_CHET[0]


def test_mang_da_hong_nhung_lan_nay_duoc_thi_van_do(cay, monkeypatch):
    M._MANG_GH["hong"] = True
    goi = _chay_kich_ban(monkeypatch, [f"success {NHANH}\n"])
    assert _do(cay, RUN_API, [], []) == ("success", NHANH)
    assert len(goi) == 1 and M._GIAC_QUAN_CHET == []


# ---------- gh hỏng không phải vì mạng: lùi sang API công khai ----------

def test_gh_hong_token_lui_sang_api_khong_thu_lai_gh(cay, monkeypatch):
    goi = _chay_kich_ban(monkeypatch, [LOI_TOKEN])
    bat: list[str] = []
    ngu: list[float] = []
    assert _do(cay, RUN_API, bat, ngu) == ("failure", NHANH)
    assert len(goi) == 1 and ngu == []
    assert len(bat) == 1 and "branch=feat%2Fr1-1-2-design-gap-remediation" in bat[0]
    assert M._GIAC_QUAN_CHET == [] and M._SO_GIAC_QUAN["chay"] == 1
    assert M._MANG_GH["hong"] is False


def test_gh_va_api_deu_hong_mot_giac_quan_chet_du_nguyen_nhan(cay, monkeypatch):
    _chay_kich_ban(monkeypatch, [LOI_TOKEN])
    assert _do(cay, {"/runs": OSError("mang")}, [], []) == ("", NHANH)
    assert len(M._GIAC_QUAN_CHET) == 1
    assert "HTTP 401" in M._GIAC_QUAN_CHET[0] and "OSError" in M._GIAC_QUAN_CHET[0]
    assert M._SO_GIAC_QUAN["chay"] == 1


def test_gh_khong_khoi_dong_duoc_lui_sang_api(cay, monkeypatch):
    goi = _chay_kich_ban(monkeypatch, [], ghi_chet="không chạy được")
    bat: list[str] = []
    assert _do(cay, RUN_API, bat, []) == ("failure", NHANH)
    assert len(goi) == 1 and len(bat) == 1
    assert M._GIAC_QUAN_CHET == [] and M._SO_GIAC_QUAN["chay"] == 1


def test_gh_treo_het_han_khong_thu_lai_khong_goi_api(cay, monkeypatch):
    """gh treo đủ 30 s rồi mới bị cắt: thử lại hay gọi thêm API (20 s) sẽ vượt hạn 90 s của bên gọi."""
    goi = _chay_kich_ban(monkeypatch, [], ghi_chet="quá 30s")
    bat: list[str] = []
    ngu: list[float] = []
    assert _do(cay, RUN_API, bat, ngu) == ("", NHANH)
    assert len(goi) == 1 and ngu == [] and bat == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "quá 30s" in M._GIAC_QUAN_CHET[0]
    assert M._SO_GIAC_QUAN["chay"] == 1 and M._MANG_GH["hong"] is True


# ---------- câu trả lời thật của gh không bị coi là lỗi ----------

@pytest.mark.parametrize("out, dau_hieu", [
    ("success claude/nhanh-khac\n", "≠"),
    (" \n", "chưa có run"),
])
def test_cau_tra_loi_that_khong_thu_lai_khong_goi_api(cay, monkeypatch, out, dau_hieu):
    goi = _chay_kich_ban(monkeypatch, [out])
    bat: list[str] = []
    ngu: list[float] = []
    assert _do(cay, RUN_API, bat, ngu) == ("", NHANH)
    assert len(goi) == 1 and ngu == [] and bat == []
    assert len(M._GIAC_QUAN_CHET) == 1 and dau_hieu in M._GIAC_QUAN_CHET[0]
    assert M._SO_GIAC_QUAN["chay"] == 1
