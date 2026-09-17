"""Hồi quy cho `dong_bo_skill.py` — chỗ sao lưu khi đẩy skill (13/09/2026).

VÌ SAO CÓ: `--ap-dung` từng gọi `shutil.copytree(dst, dst.parent / f"{k}.bak-
{stamp}", ...)` — sao lưu NGAY TRONG thư mục `runtime` mà Claude Desktop quét
làm ứng viên skill (mỗi thư mục con có SKILL.md được coi là MỘT skill). Mỗi
lần đẩy skill tạo thêm một "skill" rác tên `<ten>.bak-<stamp>` (hiển thị thành
`<ten>-bak-<stamp>` trong danh sách skill gọi được — dấu chấm đổi thành gạch
ngang) — đo thật 13/09/2026: 3 mục rác lọt vào danh sách skill của phiên model.
Bug này ĐÃ được vá cho đường symlink (`dong_bo_skill_claude_codex.py::
backup_path()`) nhưng bị bỏ sót ở đường Cowork runtime này — cùng họ lỗi «vá
một nơi, quên nơi kia».

Ba luật khi thêm ca thử: kiểm HÀNH VI bằng cách gọi vào mã đang sống (không
đếm chuỗi); mỗi ca gắn rủi ro thật đã đo; ngoại tuyến, không đụng runtime thật.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dong_bo_skill as m  # noqa: E402


def _tao_skill_nguon(nguon_goc: Path, ten: str, noi_dung: str = "v1") -> Path:
    d = nguon_goc / ten
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {ten}\n---\n{noi_dung}\n", encoding="utf-8")
    return d


def _tao_skill_runtime(runtime: Path, ten: str, noi_dung: str = "v0-cu") -> Path:
    d = runtime / ten
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {ten}\n---\n{noi_dung}\n", encoding="utf-8")
    return d


class TestDuongDanSaoLuu:
    def test_tra_ve_duong_dan_ben_ngoai_runtime(self, tmp_path):
        runtime = tmp_path / "abc12345" / "def67890" / "skills"
        runtime.mkdir(parents=True)
        p = m.duong_dan_sao_luu(runtime, "mot-skill", "20260913-000000")
        assert runtime not in p.parents or p.parent != runtime
        assert p.parent == runtime.parent / "skills-backup"
        assert p.name == "mot-skill.bak-20260913-000000"

    def test_khong_khop_glob_ma_tim_runtime_dung(self, tmp_path):
        """`tim_runtime()` dò `GOC_RUNTIME.glob('*/*/skills')` — thư mục sao lưu
        PHẢI không bao giờ khớp mẫu đó, nếu không nó sẽ tự nhận là một
        runtime khác vào lượt quét sau."""
        goc = tmp_path / "GOC_RUNTIME"
        runtime = goc / "u1" / "u2" / "skills"
        runtime.mkdir(parents=True)
        bak_dir = m.duong_dan_sao_luu(runtime, "x", "s").parent
        bak_dir.mkdir(parents=True, exist_ok=True)
        ung_vien = list(goc.glob("*/*/skills"))
        assert bak_dir not in ung_vien


class TestApDungKhongTaoRacTrongRuntime:
    def test_ap_dung_khong_de_lai_bak_trong_runtime(self, tmp_path, monkeypatch):
        nguon_goc = tmp_path / "sync_skills"
        runtime = tmp_path / "runtime_uuid1" / "runtime_uuid2" / "skills"
        nguon_goc.mkdir(parents=True)
        runtime.mkdir(parents=True)

        _tao_skill_nguon(nguon_goc, "antifacts", "noi dung MOI")
        _tao_skill_runtime(runtime, "antifacts", "noi dung CU")

        monkeypatch.setattr(m, "NGUON", nguon_goc)
        monkeypatch.setattr(m, "tim_runtime", lambda: runtime)

        # --nguon-la-chuan: đúng cờ dong_bo_skill_claude_codex.py::sync_cowork()
        # truyền khi gọi công cụ này thật — nội dung cũ/mới hoàn toàn khác nhau
        # nên đây là ca PHÂN KỲ, chỉ đẩy được khi nguồn được chọn làm chuẩn.
        with mock.patch.object(
            sys, "argv",
            ["dong_bo_skill.py", "--ap-dung", "--nguon-la-chuan", "--im-khi-on"],
        ):
            rc = m.main()
        assert rc == 0

        # Không có mục *.bak-* nào lọt vào CHÍNH thư mục runtime (nơi Claude quét).
        rac_trong_runtime = list(runtime.rglob("*.bak-*"))
        assert rac_trong_runtime == [], f"vẫn còn rác trong runtime: {rac_trong_runtime}"

        # Bản sao lưu PHẢI tồn tại — ở nơi khác, không mất an toàn.
        bak_dir = runtime.parent / "skills-backup"
        assert bak_dir.is_dir(), "thư mục sao lưu ngoài không được tạo"
        bak_con = list(bak_dir.glob("antifacts.bak-*"))
        assert len(bak_con) == 1, "phải có đúng 1 bản sao lưu cho skill vừa ghi đè"
        noi_dung_bak = (bak_con[0] / "SKILL.md").read_text(encoding="utf-8")
        assert "noi dung CU" in noi_dung_bak, "bản sao lưu phải giữ NỘI DUNG CŨ của runtime"

        # Nội dung MỚI đã thật sự được đẩy vào runtime.
        noi_dung_moi = (runtime / "antifacts" / "SKILL.md").read_text(encoding="utf-8")
        assert "noi dung MOI" in noi_dung_moi

    def test_ap_dung_nhieu_lan_khong_chong_lan_ten_bak(self, tmp_path, monkeypatch):
        """Đẩy 2 lần liên tiếp (skill đổi nội dung giữa hai lần) không được làm
        lần sau XOÁ MẤT bản sao lưu của lần trước — mỗi lần một stamp riêng."""
        nguon_goc = tmp_path / "sync_skills"
        runtime = tmp_path / "u1" / "u2" / "skills"
        nguon_goc.mkdir(parents=True)
        runtime.mkdir(parents=True)
        _tao_skill_nguon(nguon_goc, "x", "v1")
        _tao_skill_runtime(runtime, "x", "v0")
        monkeypatch.setattr(m, "NGUON", nguon_goc)
        monkeypatch.setattr(m, "tim_runtime", lambda: runtime)

        with mock.patch.object(
            sys, "argv",
            ["dong_bo_skill.py", "--ap-dung", "--nguon-la-chuan", "--im-khi-on"],
        ):
            assert m.main() == 0

        # Đổi nguồn sang v2 rồi đẩy lần hai — ép stamp khác bằng cách giả lập
        # thời gian (đủ hiếm khi hai lần chạy thật trong CÙNG một giây, nhưng
        # test không nên phụ thuộc thời gian thực) bằng cách gọi thẳng logic
        # ghi hai lần với hai stamp khác nhau qua duong_dan_sao_luu trực tiếp.
        b1 = m.duong_dan_sao_luu(runtime, "x", "20260913-000000")
        b2 = m.duong_dan_sao_luu(runtime, "x", "20260913-000001")
        assert b1 != b2
        assert b1.parent == b2.parent == runtime.parent / "skills-backup"


class TestDonBakVanChayDungChoTanDu:
    def test_don_bak_van_don_duoc_tan_du_kieu_cu(self, tmp_path):
        """Sau bản vá, --ap-dung không tạo .bak-* mới trong runtime, nhưng
        don_bak() vẫn phải dọn được tàn dư TỪ TRƯỚC bản vá (đã có sẵn trên máy
        thật lúc phát hiện lỗi) — không được để mất khả năng dọn cũ.
        Từ 16/09/2026: dọn = DỜI ra `<runtime>-backup/`, nội dung còn nguyên."""
        runtime = tmp_path / "u1" / "u2" / "skills"
        runtime.mkdir(parents=True)
        tan_du = runtime / "mot-skill.bak-20260913-174830"
        tan_du.mkdir(parents=True)
        (tan_du / "SKILL.md").write_text("cu", encoding="utf-8")
        n = m.don_bak(runtime)
        assert n == 1
        assert not tan_du.exists()
        da_doi = runtime.parent / "skills-backup" / "mot-skill.bak-20260913-174830" / "SKILL.md"
        assert da_doi.read_text(encoding="utf-8") == "cu", "don_bak phải DỜI, không được xoá"


# =============================================================================
# 16/09/2026 — 23 thư mục `<tên>.bak-20260916-170912` nằm TRONG nơi chạy Cowork.
# Thủ phạm: phiên resume ở một git worktree dựng TRƯỚC bản vá 13/09 → hook chạy
# `tu_sua_chua.py` → `dong_bo_skill.py` CŨ CỦA WORKTREE → sao lưu tại chỗ. Mã của
# cây khác không sửa được từ đây, nên bản mới (1) tự DỜI tàn dư ra ngoài, (2) lọc
# nguồn theo đường dẫn TƯƠNG ĐỐI (worktree nằm dưới `.claude/`), (3) nhánh đẩy
# trọn skill cũng qua bộ lọc, (4) nguồn quy về repo CHÍNH.
# =============================================================================


def _tao_moi_truong(tmp_path, monkeypatch):
    nguon_goc = tmp_path / "sync_skills"
    runtime = tmp_path / "u1" / "u2" / "skills"
    nguon_goc.mkdir(parents=True)
    runtime.mkdir(parents=True)
    monkeypatch.setattr(m, "NGUON", nguon_goc)
    monkeypatch.setattr(m, "tim_runtime", lambda: runtime)
    return nguon_goc, runtime


class TestSaoLuuSaiChoTrongNoiChay:
    def test_ap_dung_doi_thu_muc_va_file_bak_ra_ngoai_giu_noi_dung(self, tmp_path, monkeypatch):
        nguon_goc, runtime = _tao_moi_truong(tmp_path, monkeypatch)
        _tao_skill_nguon(nguon_goc, "x", "v1")
        _tao_skill_runtime(runtime, "x", "v1")          # đã khớp — chỉ còn rác
        rac_thu_muc = runtime / "x.bak-20260916-170912"
        rac_thu_muc.mkdir()
        (rac_thu_muc / "SKILL.md").write_text("ban cu", encoding="utf-8")
        (runtime / "x" / "tools").mkdir()
        rac_file = runtime / "x" / "tools" / "a.py.bak-20260916-170912"
        rac_file.write_text("file cu", encoding="utf-8")

        assert m.main(["--ap-dung", "--im-khi-on"]) == 0

        assert list(runtime.rglob("*.bak-*")) == []
        kho = runtime.parent / "skills-backup"
        assert (kho / "x.bak-20260916-170912" / "SKILL.md").read_text(encoding="utf-8") == "ban cu"
        assert (kho / "x" / "tools" / "a.py.bak-20260916-170912").read_text(encoding="utf-8") == "file cu"

    def test_che_do_kiem_bao_lech_ma_khong_dong_vao(self, tmp_path, monkeypatch):
        """Hook `--im-khi-on` KHÔNG ghi gì nhưng phải trả mã 1 khi còn rác, để
        `tu_sua_chua` biết mà gọi `--ap-dung` — im lặng ở đây là rác nằm mãi."""
        nguon_goc, runtime = _tao_moi_truong(tmp_path, monkeypatch)
        _tao_skill_nguon(nguon_goc, "x", "v1")
        _tao_skill_runtime(runtime, "x", "v1")
        rac = runtime / "x.bak-20260916-170912"
        rac.mkdir()
        assert m.main(["--im-khi-on"]) == 1
        assert rac.is_dir(), "chế độ kiểm không được dời/xoá gì"

    def test_trung_ten_o_kho_khong_ghi_de(self, tmp_path):
        runtime = tmp_path / "u1" / "u2" / "skills"
        runtime.mkdir(parents=True)
        kho = runtime.parent / "skills-backup"
        (kho / "x.bak-20260916-170912").mkdir(parents=True)
        (kho / "x.bak-20260916-170912" / "SKILL.md").write_text("da co tu truoc", encoding="utf-8")
        rac = runtime / "x.bak-20260916-170912"
        rac.mkdir()
        (rac / "SKILL.md").write_text("moi doi ra", encoding="utf-8")

        da_doi = m.doi_sao_luu_ra_ngoai(runtime)

        assert len(da_doi) == 1
        assert (kho / "x.bak-20260916-170912" / "SKILL.md").read_text(encoding="utf-8") == "da co tu truoc"
        assert (da_doi[0][1] / "SKILL.md").read_text(encoding="utf-8") == "moi doi ra"
        assert da_doi[0][1].name == "x.bak-20260916-170912.trung-1"

    def test_day_tron_skill_khong_cuon_file_bak_va_pycache_trong_nguon(self, tmp_path, monkeypatch):
        """Nhánh đẩy TRỌN (skill thiếu hẳn ở nơi chạy) từng chép `src.rglob("*")`
        không qua `_bi_bo_qua` — đúng lỗi gốc BH22 đi đường vòng."""
        nguon_goc, runtime = _tao_moi_truong(tmp_path, monkeypatch)
        d = _tao_skill_nguon(nguon_goc, "moi", "v1")
        (d / "tools" / "__pycache__").mkdir(parents=True)
        (d / "tools" / "a.py").write_text("pass", encoding="utf-8")
        (d / "tools" / "a.py.bak-20260916-170912").write_text("cu", encoding="utf-8")
        (d / "tools" / "__pycache__" / "a.cpython-314.pyc").write_bytes(b"\x00")

        assert m.main(["--ap-dung", "--im-khi-on"]) == 0

        assert (runtime / "moi" / "tools" / "a.py").is_file()
        assert list(runtime.rglob("*.bak-*")) == []
        assert not (runtime / "moi" / "tools" / "__pycache__").exists()


class TestBoLocTheoDuongDanTuongDoi:
    def test_duong_dan_worktree_duoi_claude_khong_bi_loc_sach(self):
        """Mọi worktree nằm dưới `.claude/worktrees/` — lọc `.claude` trên đường dẫn
        TUYỆT ĐỐI làm 505/505 file nguồn bị bỏ, mọi skill «KHOP» trên phép so rỗng."""
        goc = Path("/x/.claude/worktrees/w/sync/skills/k")
        assert m._bi_bo_qua(goc / "SKILL.md", goc) is False
        assert m._bi_bo_qua(goc / "tools" / "a.py", goc) is False
        assert m._bi_bo_qua(goc / ".claude" / "settings.local.json", goc) is True
        assert m._bi_bo_qua(goc / "tools" / "a.py.bak-20260916-170912", goc) is True


def _git(args, cwd):
    import os
    import subprocess
    subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
    )


class TestNguonVaCongCuQuyVeRepoChinh:
    def test_goc_repo_chinh_tu_worktree_tra_ve_repo_chinh(self, tmp_path):
        chinh = tmp_path / "repo-chinh"
        (chinh / "tools").mkdir(parents=True)
        (chinh / "tools" / "dong_bo_skill.py").write_text("# gia\n", encoding="utf-8")
        _git(["init", "-q"], chinh)
        _git(["add", "-A"], chinh)
        _git(["commit", "-q", "-m", "khoi tao"], chinh)
        wt = chinh / ".claude" / "worktrees" / "phu"
        wt.parent.mkdir(parents=True)
        _git(["worktree", "add", "-q", "-b", "nhanh-phu", str(wt)], chinh)

        assert m.goc_repo_chinh(wt / "tools").resolve() == chinh.resolve()
        assert m.goc_repo_chinh(chinh / "tools").resolve() == chinh.resolve()

    def test_cong_cu_dong_bo_cowork_lui_ve_chinh_file_khi_repo_chinh_thieu(self, tmp_path, monkeypatch):
        monkeypatch.setattr(m, "GOC_CHINH", tmp_path / "khong-co-tools")
        assert m.cong_cu_dong_bo_cowork() == Path(m.__file__).resolve()
        co = tmp_path / "co-tools"
        (co / "tools").mkdir(parents=True)
        (co / "tools" / "dong_bo_skill.py").write_text("# gia\n", encoding="utf-8")
        monkeypatch.setattr(m, "GOC_CHINH", co)
        assert m.cong_cu_dong_bo_cowork() == co / "tools" / "dong_bo_skill.py"
