from __future__ import annotations

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_safety_check as S  # noqa: E402


def test_iter_files_cap_is_generous_enough_for_a_deep_tree(tmp_path):
    """Trước bản vá 16/09/2026, cap mặc định 60.000 khiến _iter_files() KHÔNG BAO GIỜ
    chạm tới ~65% cây làm việc thật (đo trực tiếp: 172.400 file, state/ ở vị trí
    150.679). Test này không dựng nổi 172k file thật (chậm), nên khoá HÀNH VI thay
    vì con số: 1) cap mặc định phải cao hơn hẳn quy mô một thư mục vài trăm file
    thật (không lặng lẽ cắt cụt); 2) cơ chế cap vẫn hoạt động đúng khi bị ép thấp
    (không bị bản vá xoá mất, chỉ đổi số mặc định)."""
    root = tmp_path / "Claude AI"
    root.mkdir()
    for i in range(500):
        (root / f"file-{i:04d}.txt").write_text("x", encoding="utf-8")

    old_root = S.ROOT
    try:
        S.ROOT = root
        seen_default = list(S._iter_files())
        seen_capped = list(S._iter_files(cap=50))
    finally:
        S.ROOT = old_root

    assert len(seen_default) == 500  # cap mặc định không cắt cụt 500 file
    assert len(seen_capped) == 50    # cơ chế cap vẫn chặn đúng khi bị ép thấp
    # 500 file << mọi cap hợp lý nên tự nó không bắt được hồi quy về cap cũ 60.000 —
    # khoá THẲNG giá trị mặc định (đo thật 16/09/2026: cây làm việc có 172.400 file).
    default_cap = inspect.signature(S._iter_files).parameters["cap"].default
    assert default_cap >= 500_000, f"cap mặc định {default_cap} lại đủ thấp để mù trên cây thật"


def test_iter_files_time_budget_stops_a_hanging_scan(monkeypatch, tmp_path):
    """Trần THẬT chống treo phải là THỜI GIAN (ổ mạng/OneDrive tải file cloud-only),
    không phải đếm số file — một cây nhỏ nhưng chậm (mô phỏng bằng đồng hồ giả) vẫn
    phải dừng đúng hạn thay vì treo tới khi liệt kê xong."""
    root = tmp_path / "Claude AI"
    (root / "sub").mkdir(parents=True)
    (root / "sub" / "a.txt").write_text("x", encoding="utf-8")
    (root / "sub" / "b.txt").write_text("x", encoding="utf-8")

    monkeypatch.setattr(S, "ROOT", root)
    clock = iter([0.0, 100.0])  # lần gọi thứ 2 (sau khi vào thư mục con) đã "quá hạn"
    monkeypatch.setattr(S.time, "monotonic", lambda: next(clock, 100.0))

    seen = list(S._iter_files(time_budget_s=25.0))

    assert seen == []  # dừng trước khi kịp yield file nào của thư mục con


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
