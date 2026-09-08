#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `ensure_link()` trong dong_bo_skill_claude_codex.py — ngoại tuyến.

Bối cảnh (2026-09-05): `verify_plugin_orchestration.py` phát hiện junction
`~/.claude/skills/plugin-router-chatgpt` và `~/.codex/skills/plugin-router-chatgpt`
trỏ vào một worktree tạm (`trusting-gates-5c3907`) thay vì nguồn canonical
`sync/skills/`. Chạy `--ap-dung` KHÔNG sửa được — nhánh XUNG_DOT (liên kết đã tồn
tại nhưng trỏ sai) chỉ BÁO CÁO, chưa từng gọi `LK.go()`/`LK.tao()` để relink dù
`apply=True`. Đây là lỗ hổng trong chính công cụ tự sửa chữa: một junction từng
đúng rồi lệch do nguồn bị dời/xoá (đúng kiểu worktree bị dọn) sẽ VĨNH VIỄN không
tự phục hồi được, bất kể chạy `--ap-dung` bao nhiêu lần.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`):
  (1) chỉ kiểm HÀNH VI bằng cách gọi vào mã đang sống, không đếm chuỗi trong file;
  (2) mỗi ca gắn với một rủi ro THẬT đã nêu trong docstring của công cụ;
  (3) nhanh và ngoại tuyến.

Chạy:  python3 tools/test_dong_bo_skill_claude_codex.py   (2 lớp unittest ở trên)
       pytest tools/test_dong_bo_skill_claude_codex.py    (đủ cả — gồm 6 ca kiểu
       pytest phía dưới, hợp nhất từ nhánh song song 08/09/2026 cùng kiểm
       ensure_link() nhưng theo góc khác: idempotent, không để lại .bak khi tự
       phục hồi, symlink treo (dangling) chứ không chỉ trỏ-sai-nhưng-còn-tồn-tại).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dong_bo_skill_claude_codex as DB  # noqa: E402
import lien_ket_da_nen as LK  # noqa: E402


class TestEnsureLinkSuaJunctionTroSai(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.nguon_dung = root / "sync-skills" / "mot-skill"
        self.nguon_sai = root / "worktree-cu" / "mot-skill"
        self.destination = root / "runtime"
        for nguon in (self.nguon_dung, self.nguon_sai):
            nguon.mkdir(parents=True)
            (nguon / "SKILL.md").write_text("---\nname: mot-skill\n---\n", encoding="utf-8")
        self.destination.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_khong_apply_chi_bao_cao_khong_sua(self) -> None:
        LK.tao(self.nguon_sai, self.destination / self.nguon_dung.name)

        ket_qua = DB.ensure_link(self.nguon_dung, self.destination, apply=False)

        self.assertEqual(ket_qua.status, "XUNG_DOT")
        self.assertTrue(LK.tro_dung(self.destination / self.nguon_dung.name, self.nguon_sai))

    def test_apply_sua_lai_junction_tro_sai_ve_dung_nguon(self) -> None:
        # Mô phỏng đúng ca thật: junction từng nối đúng vào một worktree, rồi
        # worktree đó bị dọn/đổi tên nên junction còn lại trỏ sai.
        LK.tao(self.nguon_sai, self.destination / self.nguon_dung.name)
        target = self.destination / self.nguon_dung.name
        self.assertTrue(LK.tro_dung(target, self.nguon_sai), "fixture phải bắt đầu ở trạng thái trỏ sai")

        ket_qua = DB.ensure_link(self.nguon_dung, self.destination, apply=True)

        self.assertEqual(ket_qua.status, "DA_NOI")
        self.assertTrue(LK.la_lien_ket(target))
        self.assertTrue(
            LK.tro_dung(target, self.nguon_dung),
            "sau --ap-dung junction phải trỏ về nguồn canonical, không còn trỏ worktree cũ",
        )

    def test_apply_khong_dong_gi_khi_da_khop(self) -> None:
        LK.tao(self.nguon_dung, self.destination / self.nguon_dung.name)

        ket_qua = DB.ensure_link(self.nguon_dung, self.destination, apply=True)

        self.assertEqual(ket_qua.status, "KHOP")


class TestCoTheDungCacheClaudeCode(unittest.TestCase):
    """Bối cảnh (05/09/2026): trước bản vá này, `rebuild_router()` bỏ qua
    build_catalog.py bất cứ khi nào máy không có Codex — kể cả trên máy hoàn toàn
    có thể tự dựng catalog qua cache Claude Code (sau khi build_catalog.py học đọc
    tầng đó cùng ngày). Hậu quả thật: catalog cam kết 828 skill trong khi phiên
    Cloud đo được 842, và hai lần cắt tỉa thật (academic-research-skills 17→4,
    pubmed-search 31→10) chưa từng tới catalog dù đã xảy ra từ lâu. Ca thử ở đây
    kiểm ĐÚNG hàm quyết định có gọi build_catalog.py hay không, không đếm chuỗi."""

    def test_true_khi_co_installed_plugins_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "installed_plugins.json"
            p.write_text('{"version": 1, "plugins": {}}', encoding="utf-8")
            import unittest.mock as mock
            with mock.patch.object(Path, "home", return_value=Path(tmp)):
                p2 = Path(tmp) / ".claude" / "plugins"
                p2.mkdir(parents=True)
                (p2 / "installed_plugins.json").write_text("{}", encoding="utf-8")
                self.assertTrue(DB.co_the_dung_cache_claude_code())

    def test_false_khi_khong_co_gi(self) -> None:
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(Path, "home", return_value=Path(tmp)):
                self.assertFalse(DB.co_the_dung_cache_claude_code())

    def test_rebuild_router_khong_bo_qua_khi_co_cache_claude_code_du_thieu_codex(self) -> None:
        """Đây là hành vi TRỌNG TÂM của bản vá: máy không Codex nhưng CÓ cache Claude
        Code phải vẫn được GỌI build_catalog.py (để nó tự chọn tầng đọc), không còn bị
        chặn ngay từ vòng ngoài như trước 05/09/2026.

        Cố ý KHÔNG chỉ kiểm mã thoát == 0 — nhánh "bỏ qua, giữ nguyên" CŨNG trả 0, nên
        một đột biến gỡ điều kiện `co_the_dung_cache_claude_code()` vẫn để test đó xanh
        (đã tự bắt được lỗi này khi viết: mutation-test đầu tiên KHÔNG đỏ). Thay vào đó
        script giả GHI MỘT FILE ĐÁNH DẤU — chỉ nhánh THỰC SỰ GỌI subprocess mới tạo ra nó,
        nên đây là bằng chứng trực tiếp "đã gọi", không suy luận qua mã thoát."""
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "sync" / "skills"
            router_dir = source_root / DB.ROUTER_NAME / "scripts"
            router_dir.mkdir(parents=True)
            marker = root / "da-goi.marker"
            (router_dir / "build_catalog.py").write_text(
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('x')\n",
                encoding="utf-8",
            )
            with (
                mock.patch.object(DB, "co_codex_tren_may", return_value=False),
                mock.patch.object(DB, "co_the_dung_cache_claude_code", return_value=True),
            ):
                rc = DB.rebuild_router(source_root, quiet=True)
            self.assertEqual(rc, 0)
            self.assertTrue(marker.is_file(),
                             "build_catalog.py giả PHẢI được gọi (file đánh dấu phải xuất hiện)")


if __name__ == "__main__":
    unittest.main()


# =============================================================================
# Ca thử kiểu pytest — hợp nhất 08/09/2026 từ nhánh song song. Cùng kiểm
# ensure_link(), nhưng ở các góc unittest ở trên CHƯA phủ: symlink thường (không
# phải junction) trỏ sai nhưng đích vẫn tồn tại, symlink TREO (dangling, đích đã
# bị xoá hẳn), idempotent ở lượt chạy thứ hai, và bất biến "tự phục hồi symlink
# KHÔNG được để lại .bak" (khác nhánh "đích là thư mục thật" — nhánh đó CÓ sao
# lưu, đây thì không). Chạy bằng `pytest`, không chạy qua `unittest.main()` ở trên.
# =============================================================================


def _make_source(tmp_path, name="scientific-writing"):
    source = tmp_path / "sync-skills" / name
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    return source


def test_ensure_link_dry_run_reports_conflict_without_touching_symlink(tmp_path):
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    stray = tmp_path / "nowhere"
    stray.mkdir()
    (destination / source.name).symlink_to(stray, target_is_directory=True)

    result = DB.ensure_link(source, destination, apply=False)

    assert result.status == "XUNG_DOT"
    # samefile(), khong so chuoi resolve(): tren Windows hai lan resolve() doc
    # lap tren CUNG mot thu muc co the ra hai chuoi khac nhau (xem tro_dung()).
    assert os.path.samefile(LK.dich_cua(destination / source.name), stray)


def test_ensure_link_self_heals_symlink_pointing_to_wrong_real_dir(tmp_path):
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    stray = tmp_path / "somewhere-else"
    stray.mkdir()
    (destination / source.name).symlink_to(stray, target_is_directory=True)

    result = DB.ensure_link(source, destination, apply=True)

    assert result.status == "DA_NOI"
    assert LK.tro_dung(destination / source.name, source)
    # stray target itself must be untouched -- LK.go() only unlinks the link
    assert stray.is_dir()


def test_ensure_link_self_heals_dangling_symlink(tmp_path):
    """Bug goc: lien ket cu tro toi mot duong dan KHONG con ton tai (repo doi
    cho, OneDrive ghi de). Truoc ban va, nhanh nay tra XUNG_DOT vinh vien du
    da truyen apply=True, vi khong co else-if nao goi LK.go()+LK.tao()."""
    source = _make_source(tmp_path)
    destination = tmp_path / ".codex" / "skills"
    destination.mkdir(parents=True)
    (destination / source.name).symlink_to(tmp_path / "da-bi-xoa" / source.name)

    result = DB.ensure_link(source, destination, apply=True)

    assert result.status == "DA_NOI"
    assert LK.tro_dung(destination / source.name, source)


def test_ensure_link_dangling_symlink_apply_false_leaves_it_dangling(tmp_path):
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    target = destination / source.name
    target.symlink_to(tmp_path / "da-bi-xoa" / source.name)

    result = DB.ensure_link(source, destination, apply=False)

    assert result.status == "XUNG_DOT"
    assert not target.exists()  # van con treo (broken), khong tu sua
    assert LK.la_lien_ket(target)  # nhung van la mot lien ket, chua bi xoa


def test_ensure_link_self_heal_is_idempotent_on_second_run(tmp_path):
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    (destination / source.name).symlink_to(tmp_path / "da-bi-xoa" / source.name)

    first = DB.ensure_link(source, destination, apply=True)
    second = DB.ensure_link(source, destination, apply=True)

    assert first.status == "DA_NOI"
    assert second.status == "KHOP"
    assert LK.tro_dung(destination / source.name, source)


def test_ensure_link_self_heal_does_not_create_a_backup(tmp_path):
    """Khac voi nhanh 'target la thu muc that' (co sao luu), tu phuc hoi mot
    lien ket sai KHONG duoc de lai .bak nao -- LK.go() chi go diem noi."""
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    (destination / source.name).symlink_to(tmp_path / "da-bi-xoa" / source.name)

    DB.ensure_link(source, destination, apply=True)

    assert not (destination.parent / f"{destination.name}-backup").exists()


# =============================================================================
# _resolve_repo_root() — thêm 08/09/2026, họ lỗi RỘNG hơn cả hai lớp ca trên.
#
# Ca thử ở trên chứng minh ensure_link() TỰ PHỤC HỒI một liên kết trỏ sai —
# nhưng "phục hồi" nghĩa là quay về ĐÚNG `source` được TRUYỀN VÀO. Chúng không
# hề chạm tới câu hỏi nguồn gốc: `source` mặc định (`DEFAULT_SOURCE`, dùng khi
# gọi `--ap-dung` mà không truyền `--source`) được tính THẾ NÀO?
#
# Trước bản vá này: `REPO = Path(__file__).resolve().parents[1]`. Một PHIÊN
# đang chạy TRONG một git worktree phụ (`.claude/worktrees/<tên>` — Claude Code
# tự dựng để cô lập agent/subagent) thực thi file .py CỦA CHÍNH worktree đó, nên
# `__file__` trỏ vào worktree, KHÔNG phải repo chính — REPO/DEFAULT_SOURCE theo
# đó cũng lệch vào `sync/skills` của worktree (một bản sao độc lập, thường CŨ
# hơn nhánh chính). Gọi `ensure_link(nguồn_sai, ~/.claude/skills, apply=True)`
# thì chính cơ chế "tự phục hồi" ở trên sẽ NHIỆT TÌNH ép symlink DÙNG CHUNG cho
# CẢ MÁY về phía worktree đó — tệ hơn hẳn XUNG_DOT không tự sửa, vì giờ nó CHỦ
# ĐỘNG lan lỗi sang mọi phiên khác đang dùng chung `~/.claude/skills`.
#
# Ca thật đo được 08/09/2026: 2 skill (`cap-nhat-chung-cu-y-khoa`, `dark-analyst`)
# hoàn toàn vắng mặt khỏi danh sách skill chào ra ở một phiên KHÁC trên CÙNG máy,
# vì runtime bị một phiên worktree ghi đè sang bản snapshot cũ của chính nó —
# đúng nguyên nhân bác sĩ báo "mỗi lần thực hiện một kiểu, không đọc trực tiếp
# được trên khung chat".
# =============================================================================


def _run_git(args, cwd):
    subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
    )


def _make_git_repo_with_worktree(tmp_path):
    """Dựng một repo git thật + một worktree phụ thật, độc lập với repo của
    chính dự án này (để test không đụng vào `.git` sống)."""
    main_repo = tmp_path / "repo-chinh"
    main_repo.mkdir()
    _run_git(["init", "-q", "-b", "main"], main_repo)
    (main_repo / "sync").mkdir()
    (main_repo / "sync" / "skills").mkdir()
    (main_repo / "README.md").write_text("gốc\n", encoding="utf-8")
    _run_git(["add", "-A"], main_repo)
    _run_git(["commit", "-q", "-m", "khoi tao"], main_repo)

    worktree_dir = main_repo / ".claude" / "worktrees" / "worktree-phu"
    worktree_dir.parent.mkdir(parents=True)
    _run_git(["worktree", "add", "-q", "-b", "nhanh-phu", str(worktree_dir)], main_repo)

    (worktree_dir / "tools").mkdir(parents=True, exist_ok=True)
    return main_repo, worktree_dir


def test_resolve_repo_root_from_inside_worktree_returns_main_repo(tmp_path):
    """Bug thật: gọi TỪ BÊN TRONG worktree phụ phải trả về gốc repo CHÍNH,
    không phải gốc worktree — kể cả khi worktree đó có sẵn thư mục
    `sync/skills` riêng (bản sao cũ, dễ gây nhầm là "nguồn hợp lệ")."""
    main_repo, worktree_dir = _make_git_repo_with_worktree(tmp_path)
    (worktree_dir / "sync").mkdir()
    (worktree_dir / "sync" / "skills").mkdir()  # bản sao RIÊNG của worktree

    resolved = DB._resolve_repo_root(start_dir=worktree_dir / "tools")

    assert resolved == main_repo, (
        f"Phải quy về repo CHÍNH ({main_repo}), không phải worktree phụ "
        f"({worktree_dir}) — nếu không, DEFAULT_SOURCE sẽ trỏ nhầm sang bản "
        f"sao cũ và lan ra ~/.claude/skills dùng chung cho mọi phiên."
    )


def test_resolve_repo_root_from_main_repo_returns_itself(tmp_path):
    """Đối chứng: gọi từ CHÍNH repo (không phải worktree) không được đổi hành
    vi — vẫn phải trả về đúng gốc repo đó."""
    main_repo, _worktree_dir = _make_git_repo_with_worktree(tmp_path)
    tools_dir = main_repo / "tools"
    tools_dir.mkdir()

    resolved = DB._resolve_repo_root(start_dir=tools_dir)

    assert resolved == main_repo


def test_resolve_repo_root_falls_back_when_not_a_git_repo(tmp_path):
    """Không phải git repo (hoặc git không gọi được) thì lùi về cách cũ
    (đi lên một cấp từ thư mục chứa file) thay vì ném lỗi làm chết lệnh."""
    lone_dir = tmp_path / "khong-phai-git" / "tools"
    lone_dir.mkdir(parents=True)

    resolved = DB._resolve_repo_root(start_dir=lone_dir)

    assert resolved == lone_dir.parent
