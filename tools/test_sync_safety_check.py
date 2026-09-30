from __future__ import annotations

import inspect
import subprocess
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
    # Tên phải khớp một nhánh nhận diện conflict-copy thật của check_conflict_copies() (hậu tố
    # "-<tên-máy>"). ĐÍNH CHÍNH 30/09/2026: ghi chú cũ ở đây nói OneDrive đánh số bản lặp bằng
    # dấu cách nên "active-TESTHOST-2.json" không khớp — SAI với bản sao XUNG ĐỘT: đo thật
    # `so-tong-thuat-Dr Luân BV175-2.json`, `.git/index-C010000PK16BSL-5` (gạch nối). Nhánh cũ
    # vì thế trượt mọi bản lặp; nay "-<máy>-N" cũng khớp (xem test_ban_sao_lap_lai_...).
    # « 2» (dấu cách) là kiểu NHÂN ĐÔI khác, có nhánh riêng.
    sess = root / ".claude" / "sessions" / "active-TESTHOST.json"
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


def test_ban_sao_lap_lai_va_ban_sao_cua_may_kia_deu_bi_bat(monkeypatch, tmp_path):
    """Hai điểm mù đo 30/09/2026 ở mục 1: (a) bản lặp «tên-<máy này>-2.ext» không khớp nhánh «-<máy>» cũ;
    (b) chạy trên máy A thì bản sao do máy B đẻ (`CLAUDE-C010000PK16BSL.md` khi đang ở Mac) lọt hết."""
    root = tmp_path / "Claude AI"
    a = root / ".claude" / "agents" / "dieu-phoi-lam-sang-TESTHOST-2.md"
    b = root / "medical-ebm-automation" / "CLAUDE-C010000PK16BSL.md"
    for p in (a, b):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
    monkeypatch.setattr(S, "ROOT", root)
    monkeypatch.setattr(S.socket, "gethostname", lambda: "TESTHOST")   # đang ở máy KHÁC C010000PK16BSL

    level, details = S.check_conflict_copies()

    assert level == "RED"
    assert sorted(d.replace("\\", "/") for d in details) == [
        ".claude/agents/dieu-phoi-lam-sang-TESTHOST-2.md",
        "medical-ebm-automation/CLAUDE-C010000PK16BSL.md",
    ]


# ── mục 5: bản sao xung đột NẰM TRONG .git (30/09/2026) ──────────────────────
def _git(repo: Path, *lenh: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                        "-c", "commit.gpgsign=false", *lenh], check=True, capture_output=True, text=True)
    return p.stdout.strip()


def _repo_hai_commit(tmp_path: Path) -> tuple[Path, str, str]:
    """Repo tạm có 2 commit trên `main`; trả (repo, commit 1, commit 2)."""
    repo = tmp_path / "Claude AI"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    for i in (1, 2):
        (repo / "a.txt").write_text(str(i), encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", f"c{i}")
    return repo, _git(repo, "rev-parse", "HEAD~1"), _git(repo, "rev-parse", "HEAD")


def _chi_repo(monkeypatch, repo: Path) -> None:
    monkeypatch.setattr(S, "ROOT", repo)
    monkeypatch.setattr(S, "GIT_REPOS", [(".", repo)])
    monkeypatch.setattr(S.socket, "gethostname", lambda: "TESTHOST")


def test_rac_trong_git_duoc_liet_ke_nhung_khong_chan(monkeypatch, tmp_path):
    """30/09/2026: 36 bản sao xung đột nằm TRONG .git (index, FETCH_HEAD, reflog…) mà mục 1 prune `.git` nên báo 🟢
    sạch. Rác git không đọc ⇒ không chặn — nhưng phải THẤY, kể cả bản lặp «-N» và tên máy kia; kho đối tượng thì không soi."""
    repo, _c1, _c2 = _repo_hai_commit(tmp_path)
    g = repo / ".git"
    (g / "index-TESTHOST-2").write_bytes((g / "index").read_bytes())
    (g / "FETCH_HEAD-Dr Luân BV175").write_text("x\n", encoding="utf-8")
    (g / "logs" / "HEAD-C010000PK16BSL").write_text("x\n", encoding="utf-8")
    (g / "objects" / "ab").mkdir(exist_ok=True)
    (g / "objects" / "ab" / "cd-TESTHOST").write_text("x", encoding="utf-8")
    _chi_repo(monkeypatch, repo)

    level, details = S.check_git_conflict_copies()

    assert level == "GREEN"
    assert len(details) == 1 and "3 tệp rác" in details[0], details


def test_ref_ma_da_nam_trong_nhanh_that_la_vang(monkeypatch, tmp_path):
    repo, c1, _c2 = _repo_hai_commit(tmp_path)
    (repo / ".git" / "refs" / "heads" / "main-TESTHOST").write_text(c1 + "\n", encoding="utf-8")
    _chi_repo(monkeypatch, repo)

    level, details = S.check_git_conflict_copies()

    assert level == "YELLOW"
    assert any("refs/heads/main-TESTHOST" in d and "dời được" in d for d in details), details


def test_ref_ma_giu_commit_ma_nhanh_that_khong_co_la_do(monkeypatch, tmp_path):
    """Bản sao «main-<máy>-2» trỏ commit mà `main` đang dùng KHÔNG chứa ⇒ dời ref ma là mất commit — phải 🔴."""
    repo, c1, c2 = _repo_hai_commit(tmp_path)
    _git(repo, "update-ref", "refs/heads/main", c1)          # ref thật lùi về c1: c2 chỉ còn ref ma giữ
    (repo / ".git" / "refs" / "heads" / "main-C010000PK16BSL-2").write_text(c2 + "\n", encoding="utf-8")
    _chi_repo(monkeypatch, repo)

    level, details = S.check_git_conflict_copies()

    assert level == "RED"
    assert any("main-C010000PK16BSL-2" in d and "rescue/" in d for d in details), details


def test_ref_ma_nhanh_may_chu_la_vang(monkeypatch, tmp_path):
    """Đúng ca đo 30/09: `refs/remotes/origin/master-C010000PK16BSL` — ref máy chủ lấy lại được bằng fetch."""
    repo, _c1, c2 = _repo_hai_commit(tmp_path)
    ref = repo / ".git" / "refs" / "remotes" / "origin" / "master-C010000PK16BSL"
    ref.parent.mkdir(parents=True)
    ref.write_text(c2 + "\n", encoding="utf-8")
    _chi_repo(monkeypatch, repo)

    level, details = S.check_git_conflict_copies()

    assert level == "YELLOW"
    assert any("fetch --prune" in d for d in details), details


def test_ban_sao_packed_refs_giu_nhanh_da_mat_la_do(monkeypatch, tmp_path):
    repo, c1, c2 = _repo_hai_commit(tmp_path)
    _git(repo, "update-ref", "refs/heads/main", c1)
    (repo / ".git" / "packed-refs-C010000PK16BSL").write_text(
        "# pack-refs with: peeled fully-peeled sorted\n" + f"{c2} refs/heads/main\n", encoding="utf-8")
    _chi_repo(monkeypatch, repo)

    level, details = S.check_git_conflict_copies()

    assert level == "RED"
    assert any("packed-refs-C010000PK16BSL" in d and "refs/heads/main" in d for d in details), details


def test_ban_sao_config_la_vang(monkeypatch, tmp_path):
    repo, _c1, _c2 = _repo_hai_commit(tmp_path)
    g = repo / ".git"
    (g / "config-C010000PK16BSL").write_text((g / "config").read_text(encoding="utf-8"), encoding="utf-8")
    _chi_repo(monkeypatch, repo)

    level, details = S.check_git_conflict_copies()

    assert level == "YELLOW"
    assert any("config-C010000PK16BSL" in d and "git config -f" in d for d in details), details


def test_main_that_su_chay_muc_ban_sao_trong_git(monkeypatch, capsys):
    """Có hàm mà `main()` không gọi thì với chốt đầu phiên nó không tồn tại (họ BH41)."""
    for ten in ("check_conflict_copies", "check_git_health", "check_core_materialized", "check_recent_writes"):
        monkeypatch.setattr(S, ten, lambda: ("GREEN", []))
    monkeypatch.setattr(S, "check_git_conflict_copies", lambda: ("RED", ["ref ma"]))

    assert S.main() == 2
    assert "TRONG .git" in capsys.readouterr().out
