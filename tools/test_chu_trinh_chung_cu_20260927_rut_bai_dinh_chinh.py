"""Chu trình chứng cứ KHÔNG kéo 🔴 «rút bỏ hẳn» cho ca đính-chính-bị-rút mà bác sĩ đã ký — vá 27/09/2026.

Đo 27/09: `chu_trinh_chung_cu.py --nhanh` báo «🔴 CÓ NGUỒN RÚT BỎ HẲN đang được trích» vì sổ xác minh trả mã 2 cho 2 nguồn
mang cờ rút bài — cả hai là ca thông báo rút là BẢN ĐÍNH CHÍNH bị rút (BH109), bác sĩ đã ký xem xét ngày 24/09; cổng cho qua
và `tu_de_xuat_viec` đã trừ đúng ca này. Ngoại tuyến: subprocess giả.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import chu_trinh_chung_cu as ctcc  # noqa: E402

BAO_CAO_RUT = ("  ĐÃ BỊ RÚT    : {n}  ·  RÚT & ĐĂNG LẠI BẢN SỬA: 0\n"
               "  🔴 NGUỒN ĐÃ BỊ RÚT — không dùng kết luận của các bài này:\n"
               "     • pmid:41110921 [retracted]  ← WebDashboard_X.html\n")


class _P:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def _chay(n_rut: int | None, cho_ky: str, tat_ca: str, capsys) -> str:
    """`n_rut=None` ⇒ báo cáo sổ KHÔNG in dòng «ĐÃ BỊ RÚT : N» (không đọc được số bài rút)."""
    def _goi(cmd, **kw):
        cmd = [str(c) for c in cmd]
        if len(cmd) > 1 and "so_xac_minh_nguon.py" in cmd[1]:
            return _P(2, BAO_CAO_RUT.format(n=n_rut) if n_rut is not None else "  🔴 NGUỒN ĐÃ BỊ RÚT — …\n")
        if len(cmd) > 2 and "mau_ky_rut_bai.py" in cmd[1]:
            return _P(0, {"--dem": cho_ky, "--dem-tat-ca": tat_ca}.get(cmd[2], ""))
        return _P(0, "")
    with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
            mock.patch.object(ctcc.subprocess, "run", side_effect=_goi):
        ctcc.main()
    return capsys.readouterr().out


def test_ca_dinh_chinh_da_ky_khong_ra_do_va_noi_ro(capsys):
    out = _chay(2, "0", "2", capsys)
    assert "CÓ NGUỒN RÚT BỎ HẲN" not in out
    assert "🟢 Mọi chốt đạt" in out and "không có bài bị rút bỏ hẳn" in out
    assert "ℹ 2 nguồn mang cờ rút bài là BẢN ĐÍNH CHÍNH" in out, "không được im lặng — phải nói rõ ca đã ký"


def test_ca_dinh_chinh_chua_ky_la_viec_cua_bac_si(capsys):
    out = _chay(2, "1", "2", capsys)
    assert "CÓ NGUỒN RÚT BỎ HẲN" not in out
    assert "👤 1 nguồn bị cờ rút bài mà thông báo là BẢN ĐÍNH CHÍNH" in out and "🟢 Mọi chốt đạt" not in out


def test_con_bai_rut_that_ngoai_ca_dinh_chinh_van_do(capsys):
    assert "🔴 CÓ NGUỒN RÚT BỎ HẲN" in _chay(3, "0", "2", capsys)


def test_khong_doc_duoc_bo_dem_thi_giu_do(capsys):
    assert "🔴 CÓ NGUỒN RÚT BỎ HẲN" in _chay(2, "", "", capsys), "đọc không được ⇒ fail-closed, giữ 🔴"


def test_khong_doc_duoc_so_bai_rut_thi_giu_do(capsys):
    assert "🔴 CÓ NGUỒN RÚT BỎ HẲN" in _chay(None, "0", "2", capsys), \
        "không biết có bao nhiêu bài rút ⇒ không được coi là «toàn ca đính chính» — fail-closed"
