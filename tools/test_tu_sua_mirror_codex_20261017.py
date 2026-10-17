"""Bộ tự vá mỗi phiên sinh lại mirror Codex khi lệch nguồn agent — 17/10/2026.

Ca thật: gộp PR gốc #188 (sửa .claude/agents) ⇒ mirror .Codex/agents (không track) ở cây chính không đổi ⇒ BH91 đỏ và
pre-commit y khoa chặn commit tới khi có người chạy tay `sync_agents_to_codex.py`. Test chốt: mục có trong VIEC_MAY với
lệnh kiểm `--check` (mã ≠ 0 khi lệch) và lệnh sửa không cờ; main() gọi lệnh sửa rồi kiểm lại khi kiểm báo lệch.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tu_sua_chua as T  # noqa: E402


def _muc():
    return [v for v in T.VIEC_MAY if "sync_agents_to_codex.py" in " ".join(map(str, v[1]))]


def test_muc_mirror_codex_co_trong_viec_may():
    m = _muc()
    assert len(m) == 1, "đúng một mục đồng bộ mirror Codex"
    nhan, kiem, sua, cloud = m[0]
    assert kiem[-1] == "--check" and sua is not None and "--check" not in sua
    assert cloud is False, "phiên Cloud: hook đã tự sinh lại mirror"


def test_lech_thi_sua_roi_kiem_lai(monkeypatch):
    goi = []
    lan_kiem = {"n": 0}

    def gia(lenh, nhan):
        goi.append(" ".join(map(str, lenh)))
        if "sync_agents_to_codex.py" not in goi[-1]:
            return 0, ""
        if goi[-1].endswith("--check"):
            lan_kiem["n"] += 1
            return (1, "Agent sync check: FAIL") if lan_kiem["n"] == 1 else (0, "PASS")
        return 0, ""
    monkeypatch.setattr(T, "chay", gia)
    monkeypatch.setattr(T, "viec_can_bac_si", lambda: [])
    monkeypatch.setattr(T, "phai_sinh_lech", lambda: ([], []), raising=False)
    monkeypatch.setattr(sys, "argv", ["tu_sua_chua.py", "--ap-dung", "--bo-qua-lam-sang"])
    T.main()
    lenh = [g for g in goi if "sync_agents_to_codex.py" in g]
    assert len(lenh) == 3 and lenh[0].endswith("--check") and not lenh[1].endswith("--check") \
        and lenh[2].endswith("--check"), lenh
