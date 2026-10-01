"""Khoá quy ước nhật ký sự cố «mỗi sự cố một tệp» (01/10/2026, bác sĩ chọn phương án b).

Từ 24/09 mọi PR nối mục vào CUỐI `audit/NHAT-KY-SU-CO.md`, nên hai PR song song gần như
chắc xung đột ở đó (3/3 lần gộp có xung đột từ 24/09). Tệp cũ nay ĐÓNG BĂNG bằng băm;
mục mới vào `audit/nhat-ky/YYYY-MM-DD-<slug>.md`. Các test kiểm HÀNH VI: tệp thật, tệp
tạm vượt luật, dây nối vào `run_verification` (thứ pre-commit chạy), và một repo git tạm
chứng minh chính lý do đổi quy ước — hai tệp khác tên gộp sạch, cùng nối cuối thì xung đột.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import muc_luc_nhat_ky as NK  # noqa: E402
import verify_claude_code_repo_alignment as V  # noqa: E402

MUC_HOP_LE = "# 01/10/2026 — Một sự cố thử\nNguyên nhân · cách vá · kiểm hồi quy.\n"


def _tep_cu_tam(tmp_path: Path, noi_dung: bytes = b"# Nhat ky cu\nmuc A\n") -> tuple[Path, str]:
    tep = tmp_path / "NHAT-KY-SU-CO.md"
    tep.write_bytes(noi_dung)
    return tep, hashlib.sha256(noi_dung.replace(b"\r\n", b"\n")).hexdigest()


def _thu_muc(tmp_path: Path, tep: dict[str, str]) -> Path:
    thu_muc = tmp_path / "nhat-ky"
    thu_muc.mkdir()
    for ten, noi_dung in tep.items():
        (thu_muc / ten).write_text(noi_dung, encoding="utf-8")
    return thu_muc


# ---------- Tệp thật trong repo ----------

def test_repo_that_dat_quy_uoc():
    """Tệp cũ đúng băm đã đóng băng, thư mục mới đúng quy ước — mục đích của cả chốt."""
    ket_qua = V.check_nhat_ky_su_co()
    assert ket_qua["status"] == "PASS", ket_qua


def test_chot_duoc_noi_vao_run_verification():
    """Chốt không ai gọi thì không tồn tại: phải nằm trong run_verification() — pre-commit chạy nó."""
    ten = [c["name"] for c in V.run_verification()["checks"]]
    assert "nhat_ky_su_co" in ten


def test_tep_cu_van_mang_dong_dong_bang_o_dau_tep():
    """Người/agent mở tệp cũ phải thấy NGAY nó đã đóng băng và nơi ghi mục mới."""
    dau = V.NHAT_KY_CU.read_text(encoding="utf-8").splitlines()[:3]
    assert any("ĐÓNG BĂNG" in d and "audit/nhat-ky/" in d for d in dau), dau


# ---------- Đóng băng tệp cũ ----------

def test_noi_them_vao_tep_cu_bi_chan_va_chi_duong(tmp_path):
    tep, sha = _tep_cu_tam(tmp_path)
    tep.write_bytes(tep.read_bytes() + b"\n### 02/10/2026 - muc moi noi cuoi\n")
    ket_qua = V.check_nhat_ky_su_co(tep, _thu_muc(tmp_path, {}), sha)
    assert ket_qua["status"] == "FAIL"
    assert "audit/nhat-ky/" in ket_qua["errors"][0]
    assert "git checkout origin/master -- audit/NHAT-KY-SU-CO.md" in ket_qua["errors"][0]


def test_sua_giua_tep_cu_cung_bi_chan(tmp_path):
    tep, sha = _tep_cu_tam(tmp_path, b"# Nhat ky cu\nmuc A\nmuc B\n")
    tep.write_bytes(b"# Nhat ky cu\nmuc A (DINH CHINH)\nmuc B\n")
    assert V.check_nhat_ky_su_co(tep, _thu_muc(tmp_path, {}), sha)["status"] == "FAIL"


def test_crlf_cua_windows_khong_do_gia(tmp_path):
    """Cùng nội dung nhưng xuống dòng CRLF (Windows) vẫn PASS — băm tính sau chuẩn hoá LF."""
    _, sha = _tep_cu_tam(tmp_path, b"# Nhat ky cu\nmuc A\n")
    tep_crlf = tmp_path / "crlf.md"
    tep_crlf.write_bytes(b"# Nhat ky cu\r\nmuc A\r\n")
    assert V.check_nhat_ky_su_co(tep_crlf, _thu_muc(tmp_path, {}), sha)["status"] == "PASS"


def test_thieu_tep_cu_la_fail(tmp_path):
    ket_qua = V.check_nhat_ky_su_co(tmp_path / "khong-co.md", _thu_muc(tmp_path, {}), "0" * 64)
    assert ket_qua["status"] == "FAIL"


# ---------- Quy ước thư mục mới ----------

def test_muc_dung_quy_uoc_va_readme_va_tep_an_deu_qua(tmp_path):
    thu_muc = _thu_muc(tmp_path, {
        "2026-10-01-mot-su-co-thu.md": MUC_HOP_LE,
        "README.md": "# Quy ước\n",
        ".DS_Store": "rac cua Finder",
    })
    assert NK.loi_thu_muc_nhat_ky(thu_muc) == []
    tep, sha = _tep_cu_tam(tmp_path)
    assert V.check_nhat_ky_su_co(tep, thu_muc, sha)["status"] == "PASS"


@pytest.mark.parametrize("ten", [
    "su-co-khong-ngay.md",              # thiếu ngày
    "2026-02-30-ngay-khong-co-that.md",  # ngày không có thật
    "2026-10-01-Chu-Hoa.md",            # slug chữ hoa
    "2026-10-01-xung-đột.md",           # slug có dấu
    "2026-10-01-hai--gach.md",          # hai gạch liền
    "2026-10-01-sai-duoi.txt",          # sai đuôi
    "2026-10-01-ban-sao 2.md",          # bản sao xung đột OneDrive
    "01-10-2026-dao-ngay.md",           # ngày đảo kiểu Việt
])
def test_ten_tep_sai_bi_chan(tmp_path, ten):
    thu_muc = _thu_muc(tmp_path, {ten: MUC_HOP_LE})
    loi = NK.loi_thu_muc_nhat_ky(thu_muc)
    # Phải bị bắt ở luật TÊN — không được lọt qua tên rồi mới đỏ vì lý do khác.
    assert len(loi) == 1 and loi[0].startswith(f"{ten}: tên phải là"), loi
    tep, sha = _tep_cu_tam(tmp_path)
    assert V.check_nhat_ky_su_co(tep, thu_muc, sha)["status"] == "FAIL"


@pytest.mark.parametrize("noi_dung", [
    "",                                            # tệp rỗng
    "### 01/10/2026 — kiểu tiêu đề tệp cũ\n",      # quên đổi ### thành #
    "# 02/10/2026 — ngày lệch tên tệp\n",          # ngày không khớp tên tệp
    "# 01/10/2026 — \n",                           # thiếu tiêu đề
    "# Một sự cố không ghi ngày\n",
])
def test_dong_dau_sai_bi_chan(tmp_path, noi_dung):
    loi = NK.loi_thu_muc_nhat_ky(_thu_muc(tmp_path, {"2026-10-01-thu.md": noi_dung}))
    assert len(loi) == 1 and "dòng đầu" in loi[0], loi


def test_dong_trong_dau_tep_khong_tinh(tmp_path):
    loi = NK.loi_thu_muc_nhat_ky(_thu_muc(tmp_path, {"2026-10-01-thu.md": "\n\n" + MUC_HOP_LE}))
    assert loi == []


def test_thu_muc_con_bi_chan(tmp_path):
    thu_muc = _thu_muc(tmp_path, {})
    (thu_muc / "2026-10").mkdir()
    loi = NK.loi_thu_muc_nhat_ky(thu_muc)
    assert len(loi) == 1 and "thư mục con" in loi[0]


# ---------- Công cụ mục lục ----------

def test_muc_luc_moi_nhat_truoc_va_bo_readme(tmp_path):
    thu_muc = _thu_muc(tmp_path, {
        "2026-10-01-cu-hon.md": MUC_HOP_LE,
        "2026-10-03-moi-hon.md": "# 03/10/2026 — Mới hơn\n",
        "README.md": "# Quy ước\n",
    })
    assert [t for t, _ in NK.muc_luc(thu_muc)] == ["2026-10-03-moi-hon.md", "2026-10-01-cu-hon.md"]
    assert NK.muc_luc(thu_muc)[0][1] == "03/10/2026 — Mới hơn"


def test_cong_cu_chay_tren_repo_that(capsys):
    assert NK.main([]) == 0
    assert "audit/nhat-ky/2026-10-01-xung-dot-gop-nhat-ky-chung.md" in capsys.readouterr().out


# ---------- Lý do đổi quy ước, kiểm bằng git thật ----------

def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    # Bỏ mọi GIT_* (hook pre-commit đặt sẵn GIT_DIR/GIT_INDEX_FILE trỏ vào repo thật) và
    # cấu hình người dùng (HOME tạm) để repo thử không mượn hook/cấu hình của máy.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(HOME=str(cwd.parent), GIT_CONFIG_NOSYSTEM="1")
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=", "-c", "init.defaultBranch=master", *args],
        cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8")


def _hai_nhanh(tmp_path: Path, viet_nhanh) -> subprocess.CompletedProcess:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "audit").mkdir()
    (repo / "audit" / "NHAT-KY-SU-CO.md").write_text("# Cũ\n\n### A\nmục A\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "goc")
    for nhanh in ("mot", "hai"):
        _git(repo, "switch", "-q", "-c", nhanh, "master")
        viet_nhanh(repo, nhanh)
        _git(repo, "add", "-A")
        assert _git(repo, "commit", "-qm", nhanh).returncode == 0
    _git(repo, "switch", "-q", "mot")
    return _git(repo, "merge", "--no-edit", "hai")


def test_hai_nhanh_moi_nhanh_mot_tep_gop_sach(tmp_path):
    def viet(repo: Path, nhanh: str) -> None:
        tep = repo / "audit" / "nhat-ky" / f"2026-10-01-{nhanh}.md"
        tep.parent.mkdir(exist_ok=True)  # git gỡ thư mục rỗng khi đổi nhánh
        tep.write_text(f"# 01/10/2026 — Sự cố {nhanh}\n", encoding="utf-8")
    kq = _hai_nhanh(tmp_path, viet)
    assert kq.returncode == 0, kq.stdout + kq.stderr


def test_doi_chung_hai_nhanh_cung_noi_cuoi_tep_cu_thi_xung_dot(tmp_path):
    """Đối chứng: tái hiện đúng kiểu xung đột 30/09 — chứng minh repo thử đo được xung đột."""
    def viet(repo: Path, nhanh: str) -> None:
        tep = repo / "audit" / "NHAT-KY-SU-CO.md"
        tep.write_text(tep.read_text(encoding="utf-8") + f"\n### Sự cố {nhanh}\n", encoding="utf-8")
    kq = _hai_nhanh(tmp_path, viet)
    assert kq.returncode != 0 and "CONFLICT" in kq.stdout, kq.stdout + kq.stderr
