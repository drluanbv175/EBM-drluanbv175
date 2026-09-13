from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_plugin_orchestration as vpo  # noqa: E402

# Vì sao có (12/09/2026): pre-commit chặn một commit KHÔNG liên quan vì
# `router runtime tro sai nguon` — verify_plugin_orchestration.py so
# `target.resolve()` với đúng `ROOT` của LẦN CHẠY này, trong khi symlink
# runtime máy-toàn-cục (~/.claude/skills/plugin-router-chatgpt) hợp lệ trỏ
# vào worktree CHÍNH (nơi bác sĩ làm việc hằng ngày) — khác `ROOT` khi công cụ
# chạy từ một `git worktree add` PHỤ. Tương tự, gói ZIP phân phối
# (CHATGPT_SKILLS/dist/..., gitignored) là artifact CỤC BỘ không đi qua git
# nên không có ở worktree phụ dù worktree chính đã build hợp lệ.
# `cac_goc_worktree_git()` + `kiem_router_runtime_va_zip()` sửa đúng chỗ này:
# chấp nhận BẤT KỲ worktree nào của CÙNG repo, không chỉ ROOT.


def _can_git() -> bool:
    return shutil.which("git") is not None


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True,
        timeout=30, check=True,
    )


class TestCacGocWorktreeGit:
    def test_tra_ve_chinh_no_khi_khong_phai_git(self, tmp_path):
        assert vpo.cac_goc_worktree_git(tmp_path) == [tmp_path]

    @pytest.mark.skipif(not _can_git(), reason="cần git trong PATH")
    def test_liet_ke_ca_worktree_chinh_lan_worktree_phu(self, tmp_path):
        main = tmp_path / "chinh"
        main.mkdir()
        _git("init", "-q", cwd=main)
        _git("config", "user.email", "t@t.dev", cwd=main)
        _git("config", "user.name", "t", cwd=main)
        (main / "f.txt").write_text("x", encoding="utf-8")
        _git("add", "f.txt", cwd=main)
        _git("commit", "-q", "-m", "init", cwd=main)

        phu = tmp_path / "phu"
        _git("worktree", "add", "-q", "-b", "nhanh-phu", str(phu), cwd=main)

        for goc_goi in (main, phu):
            goc = {p.resolve() for p in vpo.cac_goc_worktree_git(goc_goi)}
            assert main.resolve() in goc, f"thiếu worktree chính khi gọi từ {goc_goi}"
            assert phu.resolve() in goc, f"thiếu worktree phụ khi gọi từ {goc_goi}"


def _tao_router_that(goc: Path) -> None:
    """Dựng `<goc>/sync/skills/plugin-router-chatgpt/` — chỉ cần TỒN TẠI làm
    đích symlink hợp lệ để `target.exists()` (theo symlink) trả True; nội
    dung không quan trọng cho các test router-runtime/ZIP ở đây."""
    d = goc / "sync/skills/plugin-router-chatgpt"
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text("# router", encoding="utf-8")


def _tao_runtime_symlink(runtime_dir: Path, dich: Path) -> Path:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    lien_ket = runtime_dir / "plugin-router-chatgpt"
    lien_ket.symlink_to(dich, target_is_directory=True)
    return lien_ket


ZIP_REL = "CHATGPT_SKILLS/dist/plugin-router-chatgpt.zip"


class TestKiemRouterRuntimeVaZip:
    def test_chap_nhan_symlink_tro_dung_root(self, tmp_path):
        root = tmp_path / "worktree-a"
        _tao_router_that(root)
        runtime = _tao_runtime_symlink(tmp_path / "home/.claude/skills",
                                        root / "sync/skills/plugin-router-chatgpt")
        (root / "CHATGPT_SKILLS/dist").mkdir(parents=True)
        zip_path = root / ZIP_REL
        zip_path.write_bytes(b"PK\x05\x06" + b"\x00" * 18)  # empty-zip EOCD giả

        errors, worktree_phu = vpo.kiem_router_runtime_va_zip(
            root, zip_path, ZIP_REL, [root], thu_muc_runtime=(runtime.parent,))
        assert errors == []
        assert worktree_phu == []

    def test_chap_nhan_symlink_tro_worktree_khac_cung_repo(self, tmp_path):
        """Đúng ca đã gây báo động giả 12/09/2026: ROOT là worktree A, nhưng
        symlink runtime trỏ vào sync/skills của worktree B — PHẢI được chấp
        nhận vì B nằm trong danh sách `goc_worktree` của cùng repo."""
        root_a = tmp_path / "worktree-a"
        root_b = tmp_path / "worktree-b"
        root_a.mkdir()
        _tao_router_that(root_b)
        runtime = _tao_runtime_symlink(tmp_path / "home/.claude/skills",
                                        root_b / "sync/skills/plugin-router-chatgpt")
        (root_b / "CHATGPT_SKILLS/dist").mkdir(parents=True)
        zip_b = root_b / ZIP_REL
        zip_b.write_bytes(b"PK\x05\x06" + b"\x00" * 18)

        zip_a = root_a / ZIP_REL  # KHÔNG tồn tại ở root_a — worktree A chưa build

        errors, worktree_phu = vpo.kiem_router_runtime_va_zip(
            root_a, zip_a, ZIP_REL, [root_a, root_b], thu_muc_runtime=(runtime.parent,))
        assert errors == [], f"lẽ ra không còn báo động giả, nhưng vẫn còn: {errors}"
        assert len(worktree_phu) == 1
        assert "worktree" in worktree_phu[0]

    def test_tu_choi_symlink_tro_ngoai_moi_worktree(self, tmp_path):
        """Đối chứng bắt buộc: KHÔNG được lách luôn — symlink trỏ ra một nơi
        HOÀN TOÀN không liên quan tới repo vẫn phải bị bắt."""
        root = tmp_path / "worktree-a"
        _tao_router_that(root)
        noi_khong_lien_quan = tmp_path / "noi-khac-hoan-toan"
        noi_khong_lien_quan.mkdir()
        runtime = _tao_runtime_symlink(tmp_path / "home/.claude/skills", noi_khong_lien_quan)
        zip_path = root / ZIP_REL

        errors, _worktree_phu = vpo.kiem_router_runtime_va_zip(
            root, zip_path, ZIP_REL, [root], thu_muc_runtime=(runtime.parent,))
        assert any("tro sai nguon" in e for e in errors), errors

    def test_bao_loi_khi_symlink_gay(self, tmp_path):
        root = tmp_path / "worktree-a"
        _tao_router_that(root)
        runtime_dir = tmp_path / "home/.claude/skills"
        runtime_dir.mkdir(parents=True)
        lien_ket_gay = runtime_dir / "plugin-router-chatgpt"
        lien_ket_gay.symlink_to(tmp_path / "khong-ton-tai")
        zip_path = root / ZIP_REL

        errors, _worktree_phu = vpo.kiem_router_runtime_va_zip(
            root, zip_path, ZIP_REL, [root], thu_muc_runtime=(runtime_dir,))
        # Dùng mốc thuần ASCII "ket gay" — tránh bẫy NFC/NFD của ký tự "liên"
        # (repo này lưu tiếng Việt ở dạng NFD, xem "khong ton tai/lien ket gay").
        assert any("ket gay" in e for e in errors), errors

    def test_that_bai_khi_khong_worktree_nao_co_zip(self, tmp_path):
        root_a = tmp_path / "worktree-a"
        root_b = tmp_path / "worktree-b"
        _tao_router_that(root_a)
        runtime = _tao_runtime_symlink(tmp_path / "home/.claude/skills",
                                        root_a / "sync/skills/plugin-router-chatgpt")
        zip_a = root_a / ZIP_REL  # không tồn tại ở đâu cả

        errors, worktree_phu = vpo.kiem_router_runtime_va_zip(
            root_a, zip_a, ZIP_REL, [root_a, root_b], thu_muc_runtime=(runtime.parent,))
        assert worktree_phu == []
        assert any("thieu goi router" in e for e in errors), errors
