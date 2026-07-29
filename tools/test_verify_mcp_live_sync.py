from __future__ import annotations

import sys
from pathlib import Path
from subprocess import CompletedProcess

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_mcp_live_sync as V  # noqa: E402


def test_git_hooks_path_falls_back_to_local_config_when_git_refuses_repo(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    git_dir = repo / ".git"
    git_dir.mkdir(parents=True)
    (git_dir / "config").write_text(
        "[core]\n\trepositoryformatversion = 0\n\thooksPath = .githooks\n",
        encoding="utf-8",
    )

    def fake_run(*args, **kwargs):
        return CompletedProcess(args=args, returncode=128, stdout="", stderr="dubious ownership")

    monkeypatch.setattr(V.subprocess, "run", fake_run)

    assert V._git_hooks_path(repo) == ".githooks"


def test_windows_sync_verifier_checks_git_hooks(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(V.platform, "system", lambda: "Windows")
    monkeypatch.setattr(V.Path, "home", lambda: tmp_path)
    (tmp_path / ".ebm-venv").mkdir()
    monkeypatch.setattr(V, "_git_hooks_path", lambda repo: ".githooks")

    assert V.main() == 0

    out = capsys.readouterr().out
    assert "Git hooks đầy đủ" in out
    assert "launchd watcher N/A" in out


def test_windows_sync_verifier_fails_when_root_hook_is_missing(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(V.platform, "system", lambda: "Windows")
    monkeypatch.setattr(V.Path, "home", lambda: tmp_path)
    (tmp_path / ".ebm-venv").mkdir()

    def hooks(repo: Path) -> str | None:
        return None if repo == V.ROOT else ".githooks"

    monkeypatch.setattr(V, "_git_hooks_path", hooks)

    assert V.main() == 1

    err = capsys.readouterr().err
    assert "Repo gốc" in err
    assert "core.hooksPath=None" in err


def test_hook_contract_reports_missing_markers(tmp_path):
    hook = tmp_path / "pre-commit"
    hook.write_text("#!/bin/sh\nCOMPLETION_SYNC_FAIL_CLOSED=1\n", encoding="utf-8")

    missing = V._hook_contract_errors(
        hook,
        ("COMPLETION_SYNC_FAIL_CLOSED=1", "sync_agents_to_codex.py --check"),
    )

    assert missing == ["sync_agents_to_codex.py --check"]


def test_hook_contract_reports_missing_file(tmp_path):
    missing = V._hook_contract_errors(
        tmp_path / "missing-pre-commit",
        ("COMPLETION_SYNC_FAIL_CLOSED=1",),
    )

    assert len(missing) == 1
    assert missing[0].startswith("missing:")
