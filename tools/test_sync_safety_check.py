from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_safety_check as S  # noqa: E402


def test_generated_conflict_artifacts_do_not_hard_block(monkeypatch, tmp_path):
    root = tmp_path / "Claude AI"
    generated = root / "medical-ebm-automation" / "chronic-care-clinic-os" / "tsconfig.check-TESTHOST.tsbuildinfo"
    generated.parent.mkdir(parents=True)
    generated.write_text("{}", encoding="utf-8")
    log_copy = root / "medical-ebm-automation" / "data" / "archive" / "app-TESTHOST.log"
    log_copy.parent.mkdir(parents=True)
    log_copy.write_text("generated log", encoding="utf-8")

    monkeypatch.setattr(S, "ROOT", root)
    monkeypatch.setattr(S.socket, "gethostname", lambda: "TESTHOST")

    level, details = S.check_conflict_copies()

    assert level == "GREEN"
    assert len(details) == 2
    assert all("artefact sinh/ignored" in item for item in details)


def test_claude_session_state_conflict_copies_do_not_hard_block(monkeypatch, tmp_path):
    """`.claude/sessions/` + `.claude/state/` là bookkeeping nội bộ ngoài git (app tự
    sinh lại mỗi phiên) — conflict-copy ở đây là nhiễu bình thường khi nhiều phiên/máy
    cùng chạy, không phải mất việc. check_recent_writes() đã coi hai đường dẫn này là
    NOISE từ trước; test này khoá cho check_conflict_copies() khớp đúng tiền lệ đó
    (trước bản vá, hai đường dẫn này rơi vào hard_hits ⇒ RED giả)."""
    root = tmp_path / "Claude AI"
    sess = root / ".claude" / "sessions" / "active-TESTHOST-2.json"
    sess.parent.mkdir(parents=True)
    sess.write_text("{}", encoding="utf-8")
    state = root / ".claude" / "state" / "instructions-loaded-TESTHOST.jsonl"
    state.parent.mkdir(parents=True)
    state.write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(S, "ROOT", root)
    monkeypatch.setattr(S.socket, "gethostname", lambda: "TESTHOST")

    level, details = S.check_conflict_copies()

    assert level == "GREEN"
    assert len(details) == 2
    assert all("artefact sinh/ignored" in item for item in details)


def test_source_conflict_copy_still_hard_blocks(monkeypatch, tmp_path):
    root = tmp_path / "Claude AI"
    source = root / ".claude" / "agents" / "dieu-phoi-lam-sang-TESTHOST.md"
    source.parent.mkdir(parents=True)
    source.write_text("source conflict", encoding="utf-8")

    monkeypatch.setattr(S, "ROOT", root)
    monkeypatch.setattr(S.socket, "gethostname", lambda: "TESTHOST")

    level, details = S.check_conflict_copies()

    assert level == "RED"
    assert [item.replace("\\", "/") for item in details] == [
        ".claude/agents/dieu-phoi-lam-sang-TESTHOST.md"
    ]


def test_recent_write_check_ignores_isolated_copilot_worktrees(monkeypatch, tmp_path):
    root = tmp_path / "Claude AI"
    worktree_file = root / "copilot-worktrees" / "Claude AI" / "branch" / "AGENTS.md"
    worktree_file.parent.mkdir(parents=True)
    worktree_file.write_text("isolated worktree", encoding="utf-8")

    monkeypatch.setattr(S, "ROOT", root)

    level, details = S.check_recent_writes()

    assert level == "GREEN"
    assert details == []
