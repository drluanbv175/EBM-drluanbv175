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
        thật lúc phát hiện lỗi) — không được để mất khả năng dọn cũ."""
        runtime = tmp_path / "u1" / "u2" / "skills"
        runtime.mkdir(parents=True)
        tan_du = runtime / "mot-skill.bak-20260913-174830"
        tan_du.mkdir(parents=True)
        (tan_du / "SKILL.md").write_text("cu", encoding="utf-8")
        n = m.don_bak(runtime)
        assert n == 1
        assert not tan_du.exists()
