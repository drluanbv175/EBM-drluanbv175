"""Đài hoàn thiện — thước đo CI nhánh chính + PR chờ bác sĩ đo ĐÚNG lượt (17/10/2026).

Sự cố: sau khi gộp PR Dependabot, job «Dependabot Updates» (event «dynamic») của GitHub hỏng ⇒ thước đo CI nhánh chính
repo y khoa (đo `--limit 1` mọi workflow) báo «failure» dù CI thật đang chạy; lượt «cancelled» do bị lượt mới thay chỗ
cũng không phải kết luận. PR đã bật tự gộp không còn «chờ bác sĩ». Ngoại tuyến: `_gh` giả.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import do_dai_hoan_thien as D  # noqa: E402

DYN = {"event": "dynamic", "status": "completed", "conclusion": "failure", "createdAt": "2026-10-17T08:52:00Z"}
HUY = {"event": "push", "status": "completed", "conclusion": "cancelled", "createdAt": "2026-10-17T08:51:00Z"}
CHAY = {"event": "push", "status": "in_progress", "conclusion": "", "createdAt": "2026-10-17T08:50:00Z"}
XANH = {"event": "push", "status": "completed", "conclusion": "success", "createdAt": "2026-10-17T05:34:00Z"}
DO = {"event": "push", "status": "completed", "conclusion": "failure", "createdAt": "2026-10-17T05:00:00Z"}


def test_bo_job_dynamic_va_luot_huy():
    moi, xong = D.chon_luot_ci([DYN, HUY, CHAY, XANH])
    assert moi is CHAY and xong is XANH
    assert D.chon_luot_ci([DYN, HUY]) == (None, None)
    assert D.chon_luot_ci([DO, XANH]) == (DO, DO), "failure THẬT của CI vẫn là failure"


def _hang(monkeypatch, tmp_path, luot, prs):
    monkeypatch.setattr(D, "_chay", lambda *a, **k: None)

    def gia(args, goc):
        return luot if args[:2] == ["run", "list"] else (prs if args[:2] == ["pr", "list"] else None)
    monkeypatch.setattr(D, "_gh", gia)
    return {h["ma"]: h for h in D.thuoc_do(tmp_path, tmp_path, [], [], [])}


def test_ci_dang_chay_la_khong_do_kem_luot_xong(monkeypatch, tmp_path):
    h = _hang(monkeypatch, tmp_path, [DYN, HUY, CHAY, XANH], [])
    assert h["N-CI-YK"]["trang_thai"] == "khong_do" and "lượt xong gần nhất: success" in h["N-CI-YK"]["hien_tai"]
    h = _hang(monkeypatch, tmp_path, [DYN, XANH], [])
    assert h["N-CI-YK"]["trang_thai"] == "dat", "job Dependabot hỏng không làm đỏ CI nhánh chính"


def test_pr_tu_gop_khong_tinh_la_cho_bac_si(monkeypatch, tmp_path):
    prs = [{"number": 1, "autoMergeRequest": {"mergeMethod": "SQUASH"}}, {"number": 2, "autoMergeRequest": None}]
    h = _hang(monkeypatch, tmp_path, [XANH], prs)
    # hai repo cùng trả danh sách giả ⇒ 2 PR chờ, 2 PR tự gộp
    assert h["N-PR"]["so"] == 2 and h["N-PR"]["hien_tai"] == "2 (+2 tự gộp khi CI xanh)"
    h = _hang(monkeypatch, tmp_path, [XANH], [prs[0]])
    assert h["N-PR"]["trang_thai"] == "dat" and h["N-PR"]["hien_tai"].startswith("0 (+2")
