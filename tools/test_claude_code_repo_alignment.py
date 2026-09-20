from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_agents_to_codex as sync  # noqa: E402
import verify_claude_code_repo_alignment as V  # noqa: E402


def _git(args: list[str], cwd: Path) -> None:
    proc = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=30
    )
    assert proc.returncode == 0, f"git {args} failed: {proc.stderr}"


def _init_fake_repo(tmp_path: Path) -> Path:
    """Dựng một repo git tối giản, tự đứng độc lập, với một agent .md thật
    (glob `sync.source_agent_paths()` chấp nhận: không phải README, không bắt
    đầu bằng `_`), đã commit rồi mới có thể mô phỏng `git rm --cached`."""
    agents_dir = tmp_path / ".claude" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "vi-du-agent.md").write_text(
        "---\nname: vi-du-agent\ndescription: agent giả lập cho test\n---\nNội dung.\n",
        encoding="utf-8",
    )
    _git(["init", "-q"], tmp_path)
    _git(["config", "user.email", "test@example.com"], tmp_path)
    _git(["config", "user.name", "Test"], tmp_path)
    _git(["add", "."], tmp_path)
    _git(["commit", "-q", "-m", "init"], tmp_path)
    return agents_dir


def test_claude_code_repo_alignment_overall_passes():
    report = V.run_verification()

    assert report["overall_status"] == "PASS"
    assert {check["name"] for check in report["checks"]} == {
        "root_docs",
        "medical_repo_docs",
        "tracked_contract_files",
        "agent_sync_health",
        "agent_files_git_tracked",
        "upgrade_verify_wiring",
    }


def test_root_docs_share_required_claude_codex_markers():
    check = V.check_root_docs()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == {}


def test_medical_repo_docs_keep_claude_code_completion_contract():
    check = V.check_medical_docs()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == {}


def test_clinical_runtime_contract_files_are_tracked():
    check = V.check_tracked_contract_files()

    assert check["status"] == "PASS"
    assert check["missing_files"] == []


def test_agent_sync_health_is_green():
    check = V.check_agent_sync_health()

    assert check["status"] == "PASS"
    assert check["source_agents"] >= 40
    assert check["errors"] == []


def test_upgrade_verify_runs_alignment_gate():
    check = V.check_upgrade_verify_wires_alignment()

    assert check["status"] == "PASS"
    assert check["missing_markers"] == []


def test_agent_files_are_git_tracked_on_the_real_repo():
    check = V.check_agent_files_git_tracked()

    assert check["status"] == "PASS"
    assert check["untracked_files"] == []


class TestGitRmCachedAgentFileIsCaught:
    """Phát hiện của Workflow đối kháng đa-agent (2026-09-03, #6): một file
    .claude/agents/*.md có mặt trên đĩa nhưng bị `git rm --cached` khỏi index
    — checkout mới/clone mới sẽ mất trắng file đó — không cổng nào trước đây
    bắt được vì check_agent_sync_health() chỉ so sánh đĩa-với-đĩa, còn
    check_tracked_contract_files() chỉ canh một danh sách file hạ tầng cố
    định, không canh từng agent .md riêng lẻ."""

    def test_passes_when_agent_file_is_committed_and_present(self, tmp_path, monkeypatch):
        agents_dir = _init_fake_repo(tmp_path)
        monkeypatch.setattr(V, "ROOT", tmp_path)
        monkeypatch.setattr(sync, "SOURCE_DIR", agents_dir)

        check = V.check_agent_files_git_tracked()

        assert check["status"] == "PASS"
        assert check["untracked_files"] == []

    def test_fails_when_agent_file_is_git_rm_cached_but_still_on_disk(self, tmp_path, monkeypatch):
        agents_dir = _init_fake_repo(tmp_path)
        monkeypatch.setattr(V, "ROOT", tmp_path)
        monkeypatch.setattr(sync, "SOURCE_DIR", agents_dir)

        # git rm --cached: bỏ khỏi index, GIỮ NGUYÊN trên đĩa — đúng kịch bản
        # của phát hiện #6 (file "biến mất" khỏi git mà vẫn thấy được khi mở
        # thư mục, nên rất dễ không ai nhận ra cho tới lần checkout tiếp theo).
        _git(["rm", "--cached", "-q", ".claude/agents/vi-du-agent.md"], tmp_path)
        assert (agents_dir / "vi-du-agent.md").exists(), "file phải vẫn còn trên đĩa"

        check = V.check_agent_files_git_tracked()

        assert check["status"] == "FAIL"
        assert check["untracked_files"] == [".claude/agents/vi-du-agent.md"]
