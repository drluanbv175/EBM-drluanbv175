from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_agents_to_codex as S  # noqa: E402


def _init_isolated_source(tmp_path: Path, monkeypatch) -> Path:
    """Dựng một .claude/agents/ giả lập tối giản, tách khỏi repo thật — vô
    hiệu REQUIRED_AGENTS/REQUIRED_INFRA (đòi đúng tên agent/hạ tầng THẬT của
    repo, không liên quan tới điều đang kiểm) để check_target() chỉ còn phản
    ánh đúng phần logic đang test."""
    source_dir = tmp_path / "source" / ".claude" / "agents"
    source_dir.mkdir(parents=True)
    (source_dir / "vi-du-agent.md").write_text(
        "---\nname: vi-du-agent\ndescription: agent giả lập cho test\n---\nNội dung.\n",
        encoding="utf-8",
    )
    (source_dir / "_GHI-CHU-HA-TANG.md").write_text("# Ghi chú hạ tầng giả lập\n", encoding="utf-8")
    monkeypatch.setattr(S, "SOURCE_DIR", source_dir)
    monkeypatch.setattr(S, "REQUIRED_AGENTS", set())
    monkeypatch.setattr(S, "REQUIRED_INFRA", set())
    # write_target()/check_target() dùng .relative_to(ROOT) khi ghi thông
    # điệp lỗi — phải trỏ ROOT vào tmp_path để đường dẫn giả lập nằm trong đó.
    monkeypatch.setattr(S, "ROOT", tmp_path)
    return source_dir


def test_active_targets_dedups_on_case_insensitive_fs_even_when_neither_dir_exists(
    tmp_path, monkeypatch
):
    """Tai hien dung bug goc: worktree moi, .Codex/agents va .codex/agents
    deu CHUA TON TAI tren dia tai thoi diem goi active_targets() lan dau.
    Heuristic cu dua vao Path.exists() nen coi day la KHONG trung nhau va
    ghi doc lap ca hai -> lan ghi sau de len lan ghi truoc tren filesystem
    case-insensitive. Ban vá phai dedup dung NGAY LAN GOI DAU, khong can
    thu muc da ton tai."""
    target_a = tmp_path / ".Codex" / "agents"
    target_b = tmp_path / ".codex" / "agents"
    assert not target_a.exists()
    assert not target_b.exists()

    monkeypatch.setattr(S, "TARGETS", ((target_a, ".Codex/agents"), (target_b, ".codex/agents")))
    monkeypatch.setattr(S, "_case_insensitive_fs", lambda: True)

    active = S.active_targets()

    assert active == [(target_a, ".Codex/agents")]


def test_active_targets_keeps_both_independent_on_case_sensitive_fs(tmp_path, monkeypatch):
    """Tren filesystem phan biet hoa/thuong (vd Linux/CI), .Codex/agents va
    .codex/agents la hai thu muc THAT SU khac nhau va PHAI duoc ghi doc lap
    - ban vá khong duoc lam mat hanh vi nay."""
    target_a = tmp_path / ".Codex" / "agents"
    target_b = tmp_path / ".codex" / "agents"

    monkeypatch.setattr(S, "TARGETS", ((target_a, ".Codex/agents"), (target_b, ".codex/agents")))
    monkeypatch.setattr(S, "_case_insensitive_fs", lambda: False)

    active = S.active_targets()

    assert active == [(target_a, ".Codex/agents"), (target_b, ".codex/agents")]


def test_active_targets_dedups_after_dirs_already_exist_too(tmp_path, monkeypatch):
    """Khong pha vo truong hop cu: khi ca hai thu muc dich DA ton tai (vd
    checkout da chay sync truoc do), van phai dedup dung nhu truoc."""
    target_a = tmp_path / ".Codex" / "agents"
    target_b = tmp_path / ".codex" / "agents"
    target_a.mkdir(parents=True)
    # exist_ok=True: tren filesystem case-insensitive that (vd may test nay
    # dang chay tren APFS), target_b da ton tai vi trung target_a.
    target_b.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(S, "TARGETS", ((target_a, ".Codex/agents"), (target_b, ".codex/agents")))
    monkeypatch.setattr(S, "_case_insensitive_fs", lambda: True)

    active = S.active_targets()

    assert active == [(target_a, ".Codex/agents")]


def test_case_insensitive_fs_probe_matches_independent_check_and_caches(tmp_path, monkeypatch):
    """_case_insensitive_fs() phai phat hien dung tinh case-insensitive cua
    filesystem THAT (khong dua vao .Codex/.codex), va phai cache ket qua
    (khong tham do lai moi lan goi)."""
    (tmp_path / "tools").mkdir()
    monkeypatch.setattr(S, "ROOT", tmp_path)
    monkeypatch.setattr(S, "_CASE_INSENSITIVE_FS_CACHE", None)

    # Kiem tra doc lap: KHONG goi lai code duoi test, tu hoi filesystem that.
    expected = (tmp_path / "TOOLS").exists()

    result = S._case_insensitive_fs()
    assert result == expected

    # Da cache: doi ROOT sang noi khong co "tools" van phai tra ve gia tri cu.
    monkeypatch.setattr(S, "ROOT", tmp_path / "khong-ton-tai")
    assert S._case_insensitive_fs() == result


def test_real_checkout_active_targets_dedups_to_single_canonical_entry():
    """Kiem tra hoi quy tren checkout that (khong mock): active_targets()
    khong duoc tra ve ca .Codex/agents lan .codex/agents cung luc tren may
    nay (APFS case-insensitive) - dung day la trieu chung truc tiep cua bug
    goc (ca hai bi ghi doc lap, de len nhau)."""
    active = S.active_targets()
    labels = [label for _, label in active]
    assert labels == [".Codex/agents"]


class TestCheckTargetCatchesOrphanedInfraMirror:
    """Phát hiện của Workflow đối kháng đa-agent (2026-09-03, #7):
    check_target() kiểm hai chiều (missing + extra) cho agent .toml (dòng
    299-306) nhưng chỉ kiểm một chiều (missing, qua REQUIRED_INFRA và vòng
    expected.items()) cho hạ tầng .md — một file mirror hạ tầng MỒ CÔI (source
    đã đổi tên/xóa, bản .md cũ còn nằm lại trong .Codex/agents hoặc
    .codex/agents) không bao giờ bị bắt."""

    def test_passes_when_target_exactly_mirrors_source(self, tmp_path, monkeypatch):
        _init_isolated_source(tmp_path, monkeypatch)
        target_dir = tmp_path / "target"
        S.write_target(target_dir, "target-gia-lap")

        errors = S.check_target(target_dir, "target-gia-lap")

        assert errors == []

    def test_catches_orphaned_infra_md_left_behind_after_source_rename(self, tmp_path, monkeypatch):
        _init_isolated_source(tmp_path, monkeypatch)
        target_dir = tmp_path / "target"
        S.write_target(target_dir, "target-gia-lap")

        # Mô phỏng: file hạ tầng nguồn đã bị xóa/đổi tên (source_infra_paths()
        # không còn trả về nó), nhưng bản mirror .md CŨ vẫn còn nằm lại trong
        # thư mục đích — đúng kịch bản "git rm oan phần đã đổi tên" của #7.
        orphan = target_dir / "_HA-TANG-DA-XOA.md"
        orphan.write_text("# Bản mirror mồ côi\n", encoding="utf-8")

        errors = S.check_target(target_dir, "target-gia-lap")

        assert any("so ha tang mo coi" in e and "_HA-TANG-DA-XOA.md" in e for e in errors), errors

    def test_orphaned_toml_agent_mirror_is_unaffected_by_the_new_infra_check(
        self, tmp_path, monkeypatch
    ):
        """Đối chứng: nhánh .toml (agent thừa) đã có sẵn từ trước — chốt bổ
        sung cho hạ tầng KHÔNG được lấn/che nhánh đó."""
        _init_isolated_source(tmp_path, monkeypatch)
        target_dir = tmp_path / "target"
        S.write_target(target_dir, "target-gia-lap")
        (target_dir / "agent-mo-coi.toml").write_text(
            'name = "agent-mo-coi"\ndescription = "x"\n', encoding="utf-8"
        )

        errors = S.check_target(target_dir, "target-gia-lap")

        assert any("agent thua" in e and "agent-mo-coi" in e for e in errors), errors
