"""Tiền kiểm cho tác vụ kỹ thuật tháng + phép dò lệnh ghép/git/gh (14/11/2026).

Đo 14/11/2026: SKILL `kiem-tra-hoan-thien-he-thong-thang` có `gh run list …`, `git worktree list`,
`cd medical-ebm-automation && … pytest …`, `git branch -a --sort=-committerdate | head -20`, `git push` — không lệnh nào
được khai ở `sync/quyen-lich-nen.json`, mà `python3 tools/quyen_lich_nen.py` vẫn «🟢 đủ» vì phép dò chỉ nhận lệnh bắt đầu
bằng `python3`/`~/.ebm-venv/bin/python`/`bash`. Lượt lịch gõ tới đó là bị cắt ngang (không ai bấm «cho phép»), cảm biến
`kiem_lich_nen` chỉ thấy «BẮT ĐẦU thiếu KẾT THÚC» SAU sự việc. SKILL còn dặn tự sửa + commit/push — đúng các bước cố ý không
khai quyền.

Khoá: (1) phép dò bắt `git`/`gh`/`cd` và LỆNH GHÉP (Claude Code xét quyền từng lệnh con ⇒ quy tắc khai không phủ được), chỉ
miễn ở `khong_chay`; (2) tác vụ đang chạy theo sổ kỳ vọng mà thiếu khoá khai ⇒ mọi lệnh «chưa khai»; (3) SKILL kỹ thuật có
bước 0 tiền kiểm CHÍNH nó, DỪNG + KẾT THÚC mã 2 khi thiếu quyền; mọi lệnh là lệnh đơn chạy từ gốc; không khai lệnh SỬA.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import quyen_lich_nen as Q  # noqa: E402

TV = "kiem-tra-hoan-thien-he-thong-thang"
SKILL = REPO / "sync" / "scheduled-tasks" / TV / "SKILL.md"


def _ghi(p: Path, nd: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(nd, encoding="utf-8", newline="\n")


def _khai() -> dict:
    return json.loads((REPO / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))


# ── ly_do_ghep: lệnh đơn vs lệnh ghép ─────────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("lenh, ghep", [
    ("cd medical-ebm-automation && git status", True),
    ("cd medical-ebm-automation", True),                       # đổi thư mục: lệnh sau chạy sai chỗ
    ("git branch -a --sort=-committerdate | head -20", True),
    ("git status; ls", True),
    ("python3 tools/a.py > state/x.json", True),
    ("python3 tools/a.py 2>&1", True),
    ("python3 tools/a.py &", True),
    ("echo $(ls)", True),
    ('python3 tools/a.py "nháy không đóng', True),             # không tách được ⇒ không coi là lệnh đơn
    ("python3 tools/ghi_dau_vet_lich.py tv --ma <0|1|2>", False),  # «<…>» là chỗ điền, không phải ống/chuyển hướng
    ("~/.ebm-venv/bin/python medical-ebm-automation/tools/x.py --study <mã> --no-write", False),
    ('git log --grep "a|b"', False),                           # toán tử trong nháy không tính
    ("git -C medical-ebm-automation fetch origin --quiet", False),
    ("gh run list --repo a/b --limit 3 --json databaseId,status,conclusion,headSha", False),
    ("git for-each-ref --count=20 --sort=-committerdate --no-merged=master refs/heads refs/remotes", False),
])
def test_ly_do_ghep(lenh, ghep):
    assert bool(Q.ly_do_ghep(lenh)) is ghep, (lenh, Q.ly_do_ghep(lenh))


def test_lenh_trong_skill_bat_git_gh_cd_va_bo_mau_mo_ta_chi_voi_dau_moi():
    vb = ("`git worktree list` · `gh run list --repo a/b` · `cd x && y` · Không thêm `cd … &&` · `git …`\n"
          "`python3 tools/a.py …` · `git` · `cd`\n")
    assert Q.lenh_trong_skill(vb) == ["git worktree list", "gh run list --repo a/b", "cd x && y", "python3 tools/a.py …"], \
        "mẫu mô tả «…» chỉ miễn cho đầu lệnh mới; lệnh python3 giữ phép dò cũ; từ trơn `git`/`cd` không phải lệnh"


# ── kiem(): trên repo tạm ────────────────────────────────────────────────────────────────────────────────────────────


def _goc(tmp_path: Path, skill: str, khai_tv: dict, ky_vong: list[str] | None = None, them: dict | None = None) -> Path:
    _ghi(tmp_path / "sync" / "scheduled-tasks" / "t" / "SKILL.md", skill)
    for ten, nd in (them or {}).items():
        _ghi(tmp_path / "sync" / "scheduled-tasks" / ten / "SKILL.md", nd)
    _ghi(tmp_path / "sync" / "quyen-lich-nen.json", json.dumps({"nen_tang": "darwin", "tac_vu": {"t": khai_tv}}))
    if ky_vong is not None:
        _ghi(tmp_path / "sync" / "lich-nen-ky-vong.json", json.dumps({"tac_vu": [{"id": t} for t in ky_vong]}))
    return tmp_path


def test_git_gh_chua_khai_thi_bao(tmp_path):
    goc = _goc(tmp_path, "`git worktree list`\n`gh run list --repo a/b`\n`git status --short`\n",
               {"lenh": ["git status --short"], "khong_chay": [], "ghi": []})
    kq = Q.kiem(goc, nen_tang="__khong_doi_chieu__")
    assert kq["thieu_khai"] == [("t", "git worktree list"), ("t", "gh run list --repo a/b")]


def test_lenh_ghep_bao_ca_khi_trung_chu_muc_lenh_chi_mien_o_khong_chay(tmp_path):
    goc = _goc(tmp_path, "`cd x && python3 tools/a.py`\nCho người chạy tay: `cd y && pytest -q`\n",
               {"lenh": ["cd x && python3 tools/a.py"], "khong_chay": ["cd y && pytest -q"], "ghi": []})
    kq = Q.kiem(goc, nen_tang="__khong_doi_chieu__")
    # Mục `lenh` có toán tử là quy tắc vô hiệu: báo một lần (cùng chuỗi với dòng SKILL), không «phủ» được SKILL.
    assert kq["thieu_khai"] == [("t", "cd x && python3 tools/a.py")]


def test_muc_lenh_ghep_trong_khai_bi_bao_du_skill_khong_nhac(tmp_path):
    goc = _goc(tmp_path, "`python3 tools/a.py`\n",
               {"lenh": ["python3 tools/a.py", "git status | head"], "khong_chay": [], "ghi": []})
    assert Q.kiem(goc, nen_tang="__khong_doi_chieu__")["thieu_khai"] == [("t", "git status | head")]


def test_cho_dien_va_nhay_va_mau_mo_ta_khong_bao_oan(tmp_path):
    goc = _goc(tmp_path, "`python3 tools/g.py t --ma <0|1|2>`\n`git log --grep \"a|b\"`\nKhông thêm `cd … &&`.\n",
               {"lenh": ["python3 tools/g.py t --ma *", "git log --grep \"a|b\""], "khong_chay": [], "ghi": []})
    assert Q.kiem(goc, nen_tang="__khong_doi_chieu__")["thieu_khai"] == []


def test_tac_vu_dang_chay_thieu_khoa_khai_thi_moi_lenh_la_chua_khai(tmp_path):
    goc = _goc(tmp_path, "`python3 tools/a.py`\n", {"lenh": ["python3 tools/a.py"], "khong_chay": [], "ghi": []},
               ky_vong=["t", "moi"], them={"moi": "`python3 tools/m.py`\n`git status --short`\n", "cu": "`python3 tools/c.py`\n"})
    kq = Q.kiem(goc, nen_tang="__khong_doi_chieu__")
    assert kq["thieu_khai"] == [("moi", "python3 tools/m.py"), ("moi", "git status --short")], \
        "tác vụ lịch đang chạy mà thiếu khoá phải ồn; thư mục SKILL không còn lịch (`cu`) không xét"
    # --tac-vu (tiền kiểm một lượt) không bị tác vụ khác làm dừng oan
    assert Q.kiem(goc, nen_tang="__khong_doi_chieu__", tac_vu=["t"])["thieu_khai"] == []


def test_so_ky_vong_vang_hoac_hong_khong_lam_vo_phep_kiem(tmp_path):
    goc = _goc(tmp_path, "`python3 tools/a.py`\n", {"lenh": ["python3 tools/a.py"], "khong_chay": [], "ghi": []})
    assert Q.kiem(goc, nen_tang="__khong_doi_chieu__")["thieu_khai"] == []
    _ghi(goc / "sync" / "lich-nen-ky-vong.json", "{hỏng")
    assert Q.kiem(goc, nen_tang="__khong_doi_chieu__")["thieu_khai"] == []


def test_main_in_ro_lenh_ghep(monkeypatch, capsys):
    monkeypatch.setattr(Q, "kiem", lambda: {"khong_do": [], "thieu_khai": [("t", "cd x && y"), ("t", "gh run list")],
                                            "thieu_may": []})
    assert Q.main([]) == 1
    ra = capsys.readouterr().out
    assert "LỆNH GHÉP" in ra and "cd x && y" in ra and "git -C" in ra
    assert "SKILL.md có lệnh chưa khai ở sync/quyen-lich-nen.json — gh run list" in ra


# ── trên repo thật ───────────────────────────────────────────────────────────────────────────────────────────────────


def test_skill_ky_thuat_moi_lenh_la_lenh_don_va_da_khai():
    tv = _khai()["tac_vu"][TV]
    lenh = Q.lenh_trong_skill(SKILL.read_text(encoding="utf-8"))
    chay = [c for c in lenh if not Q.duoc_phu(c, tv["khong_chay"])]
    assert chay and all(Q.ly_do_ghep(c) is None for c in chay), [c for c in chay if Q.ly_do_ghep(c)]
    assert all(Q.duoc_phu(c, tv["lenh"]) for c in chay), [c for c in chay if not Q.duoc_phu(c, tv["lenh"])]
    # các lệnh từng lọt phép dò cũ nay có mặt dưới dạng lệnh đơn
    for can in ("gh run list --repo drluanbv175/EBM-drluanbv175", "gh run list --repo drluanbv175/medical-ebm-automation",
                "git worktree list", "git -C medical-ebm-automation fetch origin --quiet",
                "~/.ebm-venv/bin/python medical-ebm-automation/tools/list_studies.py"):
        assert any(c.startswith(can) for c in chay), can


def test_moi_muc_lenh_da_khai_deu_la_lenh_don():
    for ten, tv in _khai()["tac_vu"].items():
        for c in tv["lenh"]:
            assert Q.ly_do_ghep(c) is None, f"{ten}: quy tắc khai có toán tử shell — vô hiệu với Claude Code: {c}"


def test_khai_tac_vu_ky_thuat_khong_co_lenh_sua():
    sua = re.compile(r"^(?:git (?:-C \S+ )?(?:commit|push|merge|rebase|reset|checkout|add|switch|pull)\b|gh pr\b)")
    tv = _khai()["tac_vu"][TV]
    assert not [c for c in tv["lenh"] if sua.search(c)]
    assert not [g for g in tv["ghi"] if g != "state/**"], "lượt kỹ thuật chỉ ghi state/ — không Edit mã/tài liệu"


def test_skill_ky_thuat_tien_kiem_chinh_no_sau_bat_dau_truoc_mang_1_va_dung():
    sk = SKILL.read_text(encoding="utf-8")
    i_bd = sk.index(f"`python3 tools/ghi_dau_vet_lich.py {TV} --bat-dau`")
    i_q = sk.index(f"`python3 tools/quyen_lich_nen.py --tac-vu {TV}`")
    i_viec = sk.index("\nVIỆC CẦN KIỂM MỖI LẦN CHẠY")
    assert i_bd < i_q < i_viec
    khoi = sk[i_q:i_viec]
    for cum in ("mã 1", "mã 2", "DỪNG LƯỢT NGAY", f"`python3 tools/ghi_dau_vet_lich.py {TV} --ma 2`", "--ap-dung", "Windows"):
        assert cum in khoi, cum
    assert "LƯỢT LỊCH KHÔNG TỰ SỬA" in khoi
    # Đồng bộ runtime giữ bản cũ tới khi quyền của ĐÚNG tác vụ này 🟢 (đọc tập --tac-vu từ SKILL nguồn)
    sp = importlib.util.spec_from_file_location("_tkkt_dbtvl", REPO / "tools" / "dong_bo_tac_vu_lich.py")
    D = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(D)
    assert D._TIEN_KIEM_RE.search(sk).group(1) == TV


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
