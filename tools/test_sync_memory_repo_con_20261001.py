"""sync_memory.py — mỗi dự án một bộ nhớ, mỗi bộ nhớ một mirror riêng (01/10/2026, BH143). Ngoại tuyến.

Phiên Claude Code mở trong repo con medical-ebm-automation/ (và worktree của nó) ghi bộ nhớ ở
~/.claude/projects/<mã của …/Claude AI/medical-ebm-automation>/memory. Bản cũ của sync_memory.py chỉ đồng bộ bộ
nhớ của repo GỐC ⇒ bộ nhớ repo y khoa không bao giờ lên OneDrive, sang Windows là mất. Các ca dưới KHÔNG chạm
~/.claude thật: thư mục dự án, ~/.claude/projects và mirror đều dựng trong tmp_path; ca dòng lệnh trỏ
HOME/USERPROFILE sang tmp.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent
_REPO = _TOOLS.parent


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod                       # đăng ký TRƯỚC khi exec (dataclass cần)
    spec.loader.exec_module(mod)
    return mod


SM = _load(_TOOLS / "sync_memory.py", "sync_memory_bh143")
ROOT_NAME = "gốc (Claude AI)"
CHILD_NAME = "medical-ebm-automation"


def _layout(tmp_path: Path):
    """tmp/Claude AI/medical-ebm-automation/ + tmp/home/.claude/projects + hai MemoryProject dựng như sổ thật."""
    root = tmp_path / "Claude AI"
    child = root / "medical-ebm-automation"
    child.mkdir(parents=True)
    projects_dir = tmp_path / "home" / ".claude" / "projects"
    projects_dir.mkdir(parents=True)
    mirror = root / "memory-sync"
    projects = (SM.MemoryProject(ROOT_NAME, root, mirror),
                SM.MemoryProject(CHILD_NAME, child, mirror / "medical-ebm-automation"))
    return root, child, projects_dir, projects


def _memory(projects_dir: Path, project_dir: Path) -> Path:
    """Tạo sẵn thư mục memory mang ĐÚNG tên Claude Code tính được cho project_dir."""
    d = projects_dir / SM.claude_project_slug(project_dir) / "memory"
    d.mkdir(parents=True)
    return d


def _write(path: Path, text: str, mtime: float | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _snapshot(*dirs: Path) -> dict:
    """Ảnh chụp mọi tệp/thư mục (nội dung + mtime) — để chứng minh một lượt chạy KHÔNG ghi gì."""
    out = {}
    for d in dirs:
        if d.exists():
            for f in sorted(d.rglob("*")):
                out[str(f)] = (f.read_bytes(), f.stat().st_mtime) if f.is_file() else "dir"
    return out


def _symlink_dir(target: Path, link: Path) -> None:
    try:
        os.symlink(target, link, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"máy không cho tạo symlink ({exc}) — phép so đường dẫn THẬT có ca không cần symlink riêng")


# ── Tên thư mục dự án: khớp TỪNG KÝ TỰ với Claude Code ─────────────────────────────────────────────────────
# Giá trị đối chứng tính bằng CHÍNH đoạn JS trích nguyên văn từ Claude Code 2.1.284 (node v24.18, 01/10/2026) —
# không tính lại bằng Python, để test không tự chứng minh vòng tròn. Đường dẫn trung tính `/home/…`: chốt BH06 cấm
# chuỗi đường dẫn của một máy trong tools/; việc tên tính được khớp đúng thư mục THẬT trên Mac của bác sĩ đã đo
# bằng dry-run trên dữ liệu thật lúc vá (ghi ở audit/nhat-ky/2026-10-01-sync-memory-repo-con-mirror-rieng.md).
_LONG_VI = "/home/bs/OneDrive-Personal/Claude AI/" + "th\u01b0 m\u1ee5c d\u00e0i " * 20 + "\U0001F600"
_ORACLE = [
    ("/home/bs/OneDrive-Personal/Claude AI", "-home-bs-OneDrive-Personal-Claude-AI", 2061749319),
    ("/home/bs/OneDrive-Personal/Claude AI/medical-ebm-automation",
     "-home-bs-OneDrive-Personal-Claude-AI-medical-ebm-automation", 1214933272),
    ("C:\\Users\\Admin\\OneDrive\\Claude AI\\medical-ebm-automation",
     "C--Users-Admin-OneDrive-Claude-AI-medical-ebm-automation", -279772044),
    ("/home/x/OneDrive-Personal(2)/Claude AI", "-home-x-OneDrive-Personal-2--Claude-AI", -1536973207),
    ("/a/.claude/b(2)", "-a--claude-b-2-", -459517827),
    ("/home/Dr Lu\u00e2n/Claude AI", "-home-Dr-Lu-n-Claude-AI", -638239519),
    ("/tmp/\U0001F600/x", "-tmp----x", -136163853),
    ("/home/bs/" + "a" * 250, "-home-bs-" + "a" * 191 + "-uaecgz", -1831450787),
    ("/home/bs/" + "b" * 250, "-home-bs-" + "b" * 191 + "-ifqy9p", 1114842877),
    (_LONG_VI,
     "-home-bs-OneDrive-Personal-Claude-AI-th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-"
     "th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-th--m-c-d-i-th--m-c-it0g9x",
     -1137121125),
    ("C:\\Users\\Admin\\OneDrive\\Claude AI\\" + "z" * 220,
     "C--Users-Admin-OneDrive-Claude-AI-" + "z" * 166 + "-rzlu8s", -1692392284),
]


@pytest.mark.parametrize("path, slug, java_hash", _ORACLE)
def test_slug_and_hash_match_claude_code(path, slug, java_hash):
    """Mọi ký tự ngoài [a-zA-Z0-9] ⇒ '-' (cả '.', '(', ')', chữ có dấu; emoji = HAI mã UTF-16 ⇒ hai '-'), đường
    dẫn Windows, và đường dẫn dài hơn 200 ký tự ⇒ cắt 200 + '-' + băm hệ 36 (trị tuyệt đối — có cả băm âm lẫn dương)."""
    assert SM.claude_project_slug(path) == slug
    assert SM._java_string_hash(SM._utf16_units(path)) == java_hash


def test_slug_normalizes_nfd_like_claude_code():
    """Claude Code chuẩn hoá đường dẫn dự án về NFC trước khi mã hoá: «â» dạng tổ hợp (NFD, hay gặp từ macOS)
    vẫn phải ra MỘT dấu '-' như dạng dựng sẵn."""
    nfd = unicodedata.normalize("NFD", "/home/Dr Lu\u00e2n/Claude AI")
    assert len(nfd) == len("/home/Dr Lu\u00e2n/Claude AI") + 1
    assert SM.claude_project_slug(nfd) == "-home-Dr-Lu-n-Claude-AI"


def test_slug_accepts_path_objects(tmp_path):
    assert SM.claude_project_slug(tmp_path / "Claude AI") == SM.claude_project_slug(str(tmp_path / "Claude AI"))


# ── Dò thư mục bộ nhớ cục bộ ────────────────────────────────────────────────────────────────────────────────
def test_find_uses_exact_slug_when_memory_exists(tmp_path):
    root, child, projects_dir, projects = _layout(tmp_path)
    mem = _memory(projects_dir, child)
    found = SM.find_local_memory(projects[1], projects_dir, root)
    assert found.path == mem
    assert "đúng tên Claude Code" in found.how


def test_find_prefers_existing_slug_dir_over_stale_candidate(tmp_path):
    """Claude Code đã chạy ở đây (thư mục dự án mang tên tính được có sẵn) nhưng chưa ghi bộ nhớ ⇒ dùng tên đó
    (memory/ tạo khi kéo về), KHÔNG lấy một thư mục cũ khác chỉ khớp đuôi tên (vd OneDrive từng gắn ở «(2)»)."""
    root, child, projects_dir, projects = _layout(tmp_path)
    (projects_dir / SM.claude_project_slug(child)).mkdir()
    (projects_dir / "-Users-x-OneDrive-Personal-2--Claude-AI-medical-ebm-automation" / "memory").mkdir(parents=True)
    found = SM.find_local_memory(projects[1], projects_dir, root)
    assert found.path == projects_dir / SM.claude_project_slug(child) / "memory"
    assert "chưa có memory/" in found.how


def test_find_falls_back_to_single_suffix_candidate(tmp_path):
    root, child, projects_dir, projects = _layout(tmp_path)
    other = projects_dir / "-Users-x-OneDrive-Personal-2--Claude-AI-medical-ebm-automation" / "memory"
    other.mkdir(parents=True)
    found = SM.find_local_memory(projects[1], projects_dir, root)
    assert found.path == other
    assert "đuôi tên" in found.how


def test_find_suffix_match_ignores_case(tmp_path):
    """Windows/macOS không phân biệt hoa thường tên thư mục: «c--users-…-claude-ai-medical-ebm-automation» vẫn khớp."""
    root, child, projects_dir, projects = _layout(tmp_path)
    other = projects_dir / "c--users-admin-onedrive-claude-ai-medical-ebm-automation" / "memory"
    other.mkdir(parents=True)
    assert SM.find_local_memory(projects[1], projects_dir, root).path == other


def test_find_never_picks_temporary_worktree_dirs(tmp_path):
    """(1) worktree của repo GỐC mở phiên ở thư mục con (có thật trên Mac 01/10); (2) worktree của chính repo y
    khoa; (3) bản sao cây trong ~/.ebm-worktrees — khớp ĐÚNG đuôi tên, chỉ chữ «worktrees» chặn được. Không còn
    ứng viên hợp lệ ⇒ dùng tên tính được (máy mới), không đoán."""
    root, child, projects_dir, projects = _layout(tmp_path)
    for name in ("-Users-x-OneDrive-Personal-Claude-AI--claude-worktrees-relaxed-chaplygin-d19240-medical-ebm-automation",
                 "-Users-x-OneDrive-Personal-Claude-AI-medical-ebm-automation--claude-worktrees-eager-tu-406b0f",
                 "-Users-x--ebm-worktrees-sao-luu-Claude-AI-medical-ebm-automation"):
        (projects_dir / name / "memory").mkdir(parents=True)
    found = SM.find_local_memory(projects[1], projects_dir, root)
    assert found.path == projects_dir / SM.claude_project_slug(child) / "memory"
    assert "máy mới" in found.how


def test_find_ignores_other_clone_with_same_repo_name(tmp_path):
    """Đuôi tên gồm cả tên thư mục gốc: một bản clone khác của repo y khoa ở nơi khác không phải bộ nhớ này."""
    root, child, projects_dir, projects = _layout(tmp_path)
    (projects_dir / "-Users-x-code-medical-ebm-automation" / "memory").mkdir(parents=True)
    found = SM.find_local_memory(projects[1], projects_dir, root)
    assert found.path == projects_dir / SM.claude_project_slug(child) / "memory"


def test_root_never_picks_child_repo_memory(tmp_path):
    """Hồi quy lối dò cũ («chỉ một ứng viên» rồi «tên chứa claude»): máy chưa có thư mục gốc mang tên tính được,
    chỉ có bộ nhớ của repo y khoa — tên nó cũng chứa «Claude-AI». Dò cho GỐC tuyệt đối không được chọn nó."""
    root, child, projects_dir, projects = _layout(tmp_path)
    child_mem = _memory(projects_dir, child)
    found = SM.find_local_memory(projects[0], projects_dir, root)
    assert found.path != child_mem
    assert found.path == projects_dir / SM.claude_project_slug(root) / "memory"


def test_find_refuses_to_guess_between_two_candidates(tmp_path):
    root, child, projects_dir, projects = _layout(tmp_path)
    a = projects_dir / "-Users-x-OneDrive-Personal-Claude-AI-medical-ebm-automation" / "memory"
    b = projects_dir / "-Users-x-OneDrive-Personal-2--Claude-AI-medical-ebm-automation" / "memory"
    a.mkdir(parents=True)
    b.mkdir(parents=True)
    found = SM.find_local_memory(projects[1], projects_dir, root)
    assert found.path is None
    assert set(found.candidates) == {a, b}


# ── Chốt chống trộn ─────────────────────────────────────────────────────────────────────────────────────────
def test_crossings_clean_for_real_layout(tmp_path):
    """Bố cục thật: mirror gốc CHỨA mirror repo y khoa (thiết kế — mirror chỉ đọc tầng đầu), hai cục bộ riêng."""
    m = tmp_path / "Claude AI" / "memory-sync"
    blocked, messages = SM.find_crossings([("goc", tmp_path / "p" / "a" / "memory", m),
                                           ("yk", tmp_path / "p" / "b" / "memory", m / "medical-ebm-automation")])
    assert blocked == set() and messages == []


def test_crossings_same_local_dir_blocks_both(tmp_path):
    loc = tmp_path / "p" / "a" / "memory"
    blocked, messages = SM.find_crossings([("goc", loc, tmp_path / "m1"), ("yk", loc, tmp_path / "m2")])
    assert blocked == {"goc", "yk"} and messages


def test_crossings_nested_local_dirs_block(tmp_path):
    loc = tmp_path / "p" / "a" / "memory"
    blocked, _ = SM.find_crossings([("goc", loc, tmp_path / "m1"), ("yk", loc / "con", tmp_path / "m2")])
    assert blocked == {"goc", "yk"}


def test_crossings_local_is_other_projects_mirror(tmp_path):
    m = tmp_path / "Claude AI" / "memory-sync"
    blocked, _ = SM.find_crossings([("goc", tmp_path / "p" / "a" / "memory", m),
                                    ("yk", m, m / "medical-ebm-automation")])
    assert blocked == {"goc", "yk"}


def test_crossings_local_containing_other_projects_mirror(tmp_path):
    """Bộ nhớ GỐC liên kết thẳng vào memory-sync/ ⇒ mirror repo y khoa nằm TRONG thư mục bộ nhớ gốc của Claude
    Code — phiên ở repo gốc sẽ thấy cả bộ nhớ repo y khoa. Phải chặn."""
    m = tmp_path / "Claude AI" / "memory-sync"
    blocked, _ = SM.find_crossings([("goc", m, m),
                                    ("yk", tmp_path / "p" / "b" / "memory", m / "medical-ebm-automation")])
    assert blocked == {"goc", "yk"}


def test_crossings_same_mirror_blocks(tmp_path):
    m = tmp_path / "m"
    blocked, _ = SM.find_crossings([("goc", tmp_path / "a", m), ("yk", tmp_path / "b", m)])
    assert blocked == {"goc", "yk"}


def test_crossings_follow_symlinks(tmp_path):
    """Hai thư mục cục bộ KHÁC tên nhưng một cái là liên kết tới cái kia (symlink/junction) ⇒ vẫn là MỘT."""
    real = tmp_path / "p" / "a" / "memory"
    real.mkdir(parents=True)
    link = tmp_path / "p" / "b-memory"
    _symlink_dir(real, link)
    blocked, _ = SM.find_crossings([("goc", real, tmp_path / "m1"), ("yk", link, tmp_path / "m2")])
    assert blocked == {"goc", "yk"}


# ── Đồng bộ một cặp ─────────────────────────────────────────────────────────────────────────────────────────
def test_sync_pair_two_way_newer_wins_never_deletes(tmp_path):
    local, mirror = tmp_path / "local", tmp_path / "mirror"
    t = 1_700_000_000
    _write(local / "only-local.md", "L")
    _write(mirror / "only-mirror.md", "M")
    _write(local / "local-newer.md", "L2", t + 100)
    _write(mirror / "local-newer.md", "M1", t)
    _write(local / "mirror-newer.md", "L1", t)
    _write(mirror / "mirror-newer.md", "M2", t + 100)
    _write(local / "within-1s.md", "L", t + 0.5)
    _write(mirror / "within-1s.md", "M", t)
    _write(local / "exactly-1s.md", "L", t + 1)
    _write(mirror / "exactly-1s.md", "M", t)
    before_local, before_mirror = {p.name for p in local.iterdir()}, {p.name for p in mirror.iterdir()}
    assert SM.sync_pair(local, mirror, dry=False) == (2, 2, 2, 0)
    assert _read(mirror / "only-local.md") == "L"
    assert _read(local / "only-mirror.md") == "M"
    assert _read(mirror / "local-newer.md") == "L2"
    assert _read(local / "mirror-newer.md") == "M2"
    for name in ("within-1s.md", "exactly-1s.md"):          # lệch ≤ 1 giây: không bên nào thắng, giữ cả hai
        assert (_read(local / name), _read(mirror / name)) == ("L", "M")
    assert before_local <= {p.name for p in local.iterdir()}       # KHÔNG BAO GIỜ XOÁ
    assert before_mirror <= {p.name for p in mirror.iterdir()}


def test_sync_pair_only_top_level_memory_files(tmp_path):
    local, mirror = tmp_path / "local", tmp_path / "mirror"
    _write(local / ".an.md", "x")
    _write(local / "ghi-chu.txt", "x")
    _write(local / "con" / "sau.md", "x")
    _write(local / "a.json", "{}")
    SM.sync_pair(local, mirror, dry=False)
    assert sorted(p.name for p in mirror.iterdir()) == ["a.json"]


def test_sync_pair_dry_run_writes_nothing_and_lists_every_action(tmp_path, capsys):
    local, mirror = tmp_path / "local", tmp_path / "mirror"
    _write(local / "a.md", "A")
    _write(mirror / "b.md", "B")
    before = _snapshot(tmp_path)
    assert SM.sync_pair(local, mirror, dry=True) == (1, 1, 0, 0)
    assert _snapshot(tmp_path) == before
    out = capsys.readouterr().out
    assert "→ sẽ đẩy lên mirror : a.md  (chỉ có ở cục bộ)" in out
    assert "← sẽ kéo về cục bộ  : b.md  (chỉ có ở mirror)" in out


def test_sync_pair_copy_error_is_counted_and_others_continue(tmp_path, monkeypatch, capsys):
    local, mirror = tmp_path / "local", tmp_path / "mirror"
    _write(local / "a.md", "A")
    _write(local / "b.md", "B")
    real_copy2 = shutil.copy2

    def flaky(src, dst, *args, **kwargs):
        if Path(src).name == "a.md":
            raise PermissionError("OneDrive đang khoá tệp")
        return real_copy2(src, dst, *args, **kwargs)

    monkeypatch.setattr(SM.shutil, "copy2", flaky)
    assert SM.sync_pair(local, mirror, dry=False) == (1, 0, 0, 1)
    assert (mirror / "b.md").exists() and not (mirror / "a.md").exists()
    assert "✗ a.md" in capsys.readouterr().out


# ── Đồng bộ mọi dự án ───────────────────────────────────────────────────────────────────────────────────────
def test_two_projects_two_mirrors_never_mixed(tmp_path):
    """Lõi của bản vá: hai MEMORY.md khác nhau đi về HAI mirror khác nhau; tệp của dự án này không bao giờ xuất
    hiện ở mirror hay ở bộ nhớ cục bộ của dự án kia — kể cả sau lượt chạy thứ hai."""
    root, child, projects_dir, projects = _layout(tmp_path)
    root_mem, child_mem = _memory(projects_dir, root), _memory(projects_dir, child)
    _write(root_mem / "MEMORY.md", "chỉ mục GỐC")
    _write(root_mem / "goc-1.md", "g")
    _write(child_mem / "MEMORY.md", "chỉ mục Y KHOA")
    _write(child_mem / "yk-1.md", "y")
    mirror = root / "memory-sync"
    for _ in range(2):
        assert SM.sync_all(projects, projects_dir, root) == 0
        assert _read(mirror / "MEMORY.md") == "chỉ mục GỐC"
        assert _read(mirror / "medical-ebm-automation" / "MEMORY.md") == "chỉ mục Y KHOA"
        assert sorted(p.name for p in mirror.iterdir() if p.is_file()) == ["MEMORY.md", "goc-1.md"]
        assert sorted(p.name for p in (mirror / "medical-ebm-automation").iterdir()) == ["MEMORY.md", "yk-1.md"]
        assert sorted(p.name for p in root_mem.iterdir()) == ["MEMORY.md", "goc-1.md"]
        assert sorted(p.name for p in child_mem.iterdir()) == ["MEMORY.md", "yk-1.md"]


def test_other_machine_pulls_child_memory_into_exact_slug_dir(tmp_path):
    """Máy B (vd Windows) chưa từng có bộ nhớ repo y khoa: mirror do máy A đẩy lên được kéo về ĐÚNG thư mục mang
    tên Claude Code tính được cho repo y khoa của máy B — không lẫn sang bộ nhớ gốc."""
    root, child, projects_dir, projects = _layout(tmp_path)
    mirror = root / "memory-sync"
    _write(mirror / "MEMORY.md", "chỉ mục GỐC")
    _write(mirror / "medical-ebm-automation" / "MEMORY.md", "chỉ mục Y KHOA")
    _write(mirror / "medical-ebm-automation" / "pytest-tren-mac.md", "y")
    assert SM.sync_all(projects, projects_dir, root) == 0
    child_mem = projects_dir / SM.claude_project_slug(child) / "memory"
    root_mem = projects_dir / SM.claude_project_slug(root) / "memory"
    assert _read(child_mem / "MEMORY.md") == "chỉ mục Y KHOA"
    assert (child_mem / "pytest-tren-mac.md").is_file()
    assert sorted(p.name for p in root_mem.iterdir()) == ["MEMORY.md"]
    assert _read(root_mem / "MEMORY.md") == "chỉ mục GỐC"


def test_missing_project_dir_is_skipped_without_creating_anything(tmp_path, capsys):
    root, child, projects_dir, projects = _layout(tmp_path)
    shutil.rmtree(child)
    _write(root / "memory-sync" / "medical-ebm-automation" / "MEMORY.md", "yk")      # mirror có từ máy kia
    before = _snapshot(projects_dir)
    assert SM.sync_all(projects, projects_dir, root) == 0
    assert _snapshot(projects_dir) == before
    assert "máy này không có thư mục dự án" in capsys.readouterr().out


def test_both_sides_empty_creates_nothing(tmp_path, capsys):
    root, child, projects_dir, projects = _layout(tmp_path)
    before = _snapshot(tmp_path)
    assert SM.sync_all(projects, projects_dir, root) == 0
    assert _snapshot(tmp_path) == before
    assert capsys.readouterr().out.count("Cả hai phía chưa có bộ nhớ") == 2


def test_crossing_is_refused_with_exit_2_and_no_writes(tmp_path, capsys):
    """Hai dự án trỏ cùng một thư mục cục bộ ⇒ TỪ CHỐI cả hai, mã 2, không ghi một byte nào."""
    root, child, projects_dir, _ = _layout(tmp_path)
    _write(_memory(projects_dir, child) / "MEMORY.md", "yk")
    mirror = root / "memory-sync"
    projects = (SM.MemoryProject("a", child, mirror / "a"), SM.MemoryProject("b", child, mirror / "b"))
    before = _snapshot(tmp_path)
    assert SM.sync_all(projects, projects_dir, root) == 2
    assert _snapshot(tmp_path) == before
    assert "TỪ CHỐI" in capsys.readouterr().out


def test_ambiguous_project_exit_1_other_project_still_synced(tmp_path, capsys):
    root, child, projects_dir, projects = _layout(tmp_path)
    for name in ("-Users-x-OneDrive-Personal-Claude-AI-medical-ebm-automation",
                 "-Users-x-OneDrive-Personal-2--Claude-AI-medical-ebm-automation"):
        _write(projects_dir / name / "memory" / "MEMORY.md", name)
    _write(_memory(projects_dir, root) / "MEMORY.md", "goc")
    assert SM.sync_all(projects, projects_dir, root) == 1
    assert _read(root / "memory-sync" / "MEMORY.md") == "goc"
    assert not (root / "memory-sync" / "medical-ebm-automation").exists()
    out = capsys.readouterr().out
    assert "không đoán" in out and "Mở một phiên Claude Code" in out


def test_copy_error_gives_exit_1(tmp_path, monkeypatch):
    root, child, projects_dir, projects = _layout(tmp_path)
    _write(_memory(projects_dir, child) / "MEMORY.md", "yk")

    def boom(*args, **kwargs):
        raise PermissionError("bị khoá")

    monkeypatch.setattr(SM.shutil, "copy2", boom)
    assert SM.sync_all(projects, projects_dir, root) == 1


def test_real_windows_layout_root_memory_linked_to_sync_memory(tmp_path):
    """Máy Windows thật: bộ nhớ GỐC là junction tới `sync/memory` (sync/link-memory.ps1). Không được báo chồng thư
    mục giả, và đồng bộ đi xuyên liên kết bình thường."""
    root, child, projects_dir, projects = _layout(tmp_path)
    hub = root / "sync" / "memory"
    _write(hub / "MEMORY.md", "chỉ mục GỐC")
    slug_dir = projects_dir / SM.claude_project_slug(root)
    slug_dir.mkdir()
    _symlink_dir(hub, slug_dir / "memory")
    _write(_memory(projects_dir, child) / "MEMORY.md", "chỉ mục Y KHOA")
    assert SM.sync_all(projects, projects_dir, root) == 0
    assert _read(root / "memory-sync" / "MEMORY.md") == "chỉ mục GỐC"
    assert _read(root / "memory-sync" / "medical-ebm-automation" / "MEMORY.md") == "chỉ mục Y KHOA"


def test_local_linked_to_own_mirror_is_a_noop(tmp_path, capsys):
    root, child, projects_dir, projects = _layout(tmp_path)
    child_mirror = root / "memory-sync" / "medical-ebm-automation"
    _write(child_mirror / "MEMORY.md", "yk")
    slug_dir = projects_dir / SM.claude_project_slug(child)
    slug_dir.mkdir()
    _symlink_dir(child_mirror, slug_dir / "memory")
    assert SM.sync_all(projects, projects_dir, root) == 0
    assert "MỘT thư mục" in capsys.readouterr().out


# ── Hợp đồng trên mã thật + chạy dòng lệnh ──────────────────────────────────────────────────────────────────
def test_registry_child_repo_has_own_mirror_inside_root_repo():
    by_dir = {p.directory: p for p in SM.MEMORY_PROJECTS}
    root_p = by_dir[SM.PROJECT_ROOT]
    child_p = by_dir[SM.PROJECT_ROOT / "medical-ebm-automation"]
    assert root_p.mirror == SM.MIRROR == SM.PROJECT_ROOT / "memory-sync"      # máy chưa cập nhật vẫn kéo từ đây
    assert child_p.mirror == SM.MIRROR / "medical-ebm-automation"
    assert len({p.mirror for p in SM.MEMORY_PROJECTS}) == len(SM.MEMORY_PROJECTS)
    assert not child_p.mirror.is_relative_to(child_p.directory)               # repo y khoa công khai
    ignore = [ln.strip() for ln in (_REPO / ".gitignore").read_text(encoding="utf-8").splitlines()]
    assert "memory-sync/" in ignore


def _run_cli(script: Path, home: Path, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-B", str(script), *args], env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120, check=False)


def test_cli_dry_run_then_apply_with_redirected_home(tmp_path):
    """Chạy ĐÚNG như bác sĩ chạy (tiến trình con, gốc tự suy từ vị trí tệp, sổ dự án thật), HOME/USERPROFILE trỏ
    sang tmp: --dry-run in từng cặp và không tạo mirror; chạy thật thì hai bộ nhớ về hai mirror riêng."""
    root = tmp_path / "Claude AI"
    (root / "tools").mkdir(parents=True)
    script = root / "tools" / "sync_memory.py"
    shutil.copy2(_TOOLS / "sync_memory.py", script)
    child = root / "medical-ebm-automation"
    child.mkdir()
    home = tmp_path / "home"
    projects_dir = home / ".claude" / "projects"
    root_mem, child_mem = _memory(projects_dir, root.resolve()), _memory(projects_dir, child.resolve())
    _write(root_mem / "MEMORY.md", "chỉ mục GỐC")
    _write(child_mem / "MEMORY.md", "chỉ mục Y KHOA")
    r = _run_cli(script, home, "--dry-run")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (root / "memory-sync").exists()
    for path in (root_mem, child_mem, root.resolve() / "memory-sync" / "medical-ebm-automation"):
        assert str(path) in r.stdout
    assert r.stdout.count("→ sẽ đẩy lên mirror : MEMORY.md") == 2
    r = _run_cli(script, home)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _read(root / "memory-sync" / "MEMORY.md") == "chỉ mục GỐC"
    assert _read(root / "memory-sync" / "medical-ebm-automation" / "MEMORY.md") == "chỉ mục Y KHOA"
