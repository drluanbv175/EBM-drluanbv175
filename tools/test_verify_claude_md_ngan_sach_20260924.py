"""Khoá chốt ngân sách ký tự của CLAUDE.md gốc (24/09/2026, đề xuất #12 của audit/12).

CLAUDE.md được nạp vào MỌI phiên. Trước khi rút gọn, nó phình tới 278.003 ký tự vì mỗi
sự cố được nối thêm vào như nhật ký. Lịch sử nay nằm ở audit/NHAT-KY-SU-CO.md; chốt
`check_claude_md_budget()` chặn tệp phình trở lại. Các test dưới đây kiểm HÀNH VI (tệp
thật, tệp tạm vượt/dưới ngân sách, dây nối vào `run_verification`), không đếm chuỗi.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_claude_code_repo_alignment as V  # noqa: E402


def test_claude_md_that_nam_trong_ngan_sach():
    """CLAUDE.md đang track phải nằm trong ngân sách — mục đích của cả chốt."""
    ket_qua = V.check_claude_md_budget()
    assert ket_qua["status"] == "PASS", ket_qua
    assert ket_qua["so_ky_tu"] <= V.NGAN_SACH_CLAUDE_MD


def test_tep_vuot_ngan_sach_bi_chan_va_chi_duong_ghi_nhat_ky(tmp_path):
    tep = tmp_path / "CLAUDE.md"
    tep.write_text("ư" * 101, encoding="utf-8")  # 101 ký tự, 202 byte
    ket_qua = V.check_claude_md_budget(tep, ngan_sach=100)
    assert ket_qua["status"] == "FAIL"
    assert ket_qua["so_ky_tu"] == 101, "phải đếm KÝ TỰ, không đếm byte"
    assert "audit/NHAT-KY-SU-CO.md" in ket_qua["errors"][0]


def test_tep_dung_bang_ngan_sach_van_qua(tmp_path):
    """Ranh giới: đúng bằng ngân sách vẫn PASS (dấu <=, không phải <)."""
    tep = tmp_path / "CLAUDE.md"
    tep.write_text("ư" * 100, encoding="utf-8")  # 200 byte — đếm byte sẽ FAIL sai
    ket_qua = V.check_claude_md_budget(tep, ngan_sach=100)
    assert ket_qua["status"] == "PASS", ket_qua


def test_thieu_tep_la_fail_khong_phai_pass(tmp_path):
    ket_qua = V.check_claude_md_budget(tmp_path / "khong-co.md", ngan_sach=100)
    assert ket_qua["status"] == "FAIL"


def test_chot_ngan_sach_duoc_noi_vao_run_verification():
    """Chốt không ai gọi thì không tồn tại: nó phải nằm trong danh sách kiểm của
    run_verification() — thứ mà pre-commit chạy."""
    ten = [c["name"] for c in V.run_verification()["checks"]]
    assert "claude_md_budget" in ten
