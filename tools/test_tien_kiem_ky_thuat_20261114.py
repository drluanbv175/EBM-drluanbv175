"""Tiền kiểm cho tác vụ kỹ thuật tháng + phép dò lệnh ghép/git/gh (14/11/2026).

Đo 14/11/2026: SKILL `kiem-tra-hoan-thien-he-thong-thang` có `gh run list …`, `git worktree list`,
`cd medical-ebm-automation && … pytest …`, `git branch -a --sort=-committerdate | head -20`, `git push` — không lệnh nào
được khai ở `sync/quyen-lich-nen.json`, mà `python3 tools/quyen_lich_nen.py` vẫn «🟢 đủ» vì phép dò chỉ nhận lệnh bắt đầu
bằng `python3`/`~/.ebm-venv/bin/python`/`bash`. Lượt lịch gõ tới đó là bị cắt ngang (không ai bấm «cho phép»), cảm biến
`kiem_lich_nen` chỉ thấy «BẮT ĐẦU thiếu KẾT THÚC» SAU sự việc. SKILL còn dặn tự sửa + commit/push — đúng các bước cố ý không
khai quyền.

Khoá: (1) phép dò bắt `git`/`gh`/`cd` và LỆNH GHÉP (Claude Code xét quyền từng lệnh con ⇒ quy tắc khai không phủ được), chỉ
miễn ở `khong_chay`; (2) tác vụ đang chạy theo sổ kỳ vọng mà thiếu khoá khai ⇒ mọi lệnh «chưa khai»; (3) SKILL kỹ thuật có
bước 0 tiền kiểm CHÍNH nó, DỪNG khi thiếu quyền; mọi lệnh là lệnh đơn chạy từ gốc; không khai lệnh SỬA.

Đính chính sau thẩm định 14/11/2026: (a) bước 0 dừng thì KHÔNG ghi KẾT THÚC — `kiem_lich_nen` chỉ đọc mốc giờ KẾT THÚC, không
đọc mã, nên «KẾT THÚC (mã 2)» làm kỳ không chạy thành «đúng hẹn» (xanh giả; đo bằng chính cảm biến, test hành vi dưới);
(b) lệnh ghép được một quy tắc có «*» phủ vẫn phải bị báo (đột biến bỏ luật lệnh ghép từng sống sót); (c) «…» xét sau khi
thay chỗ điền «<…>»; (d) nháy dính giữa từ (`--format="%H|%s"`) không bị báo oan là ống.
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
    ('git log --format="%H|%s"', False),                       # nháy dính giữa từ vẫn là nháy (shlex posix=False báo oan)
    ('git log --grep "|"', False),                             # nháy đứng riêng chỉ chứa toán tử (shlex posix=True báo oan)
    ("git log --grep 'a;b'", False),
    (r"git log --grep a\|b", False),                           # toán tử bị thoát bằng \ là chữ
    ('git log --x="a" | head', True),                          # nháy dính giữa từ, ống ở NGOÀI nháy vẫn là ống
    ('git log --format="$(id)"', True),                        # $( trong nháy kép vẫn là lệnh con
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


def test_lenh_co_cho_dien_ba_cham_khong_bi_coi_la_mau_mo_ta():
    # «<…>» là cú pháp chỗ điền chính thức của SKILL — xét «…» trên chuỗi thô thì lệnh thật lọt hẳn khỏi phép dò (xanh giả).
    vb = "`git -C medical-ebm-automation log <…>`\n`gh run view <…> --log`\n`git … <nhánh>`\n"
    assert Q.lenh_trong_skill(vb) == ["git -C medical-ebm-automation log <…>", "gh run view <…> --log"]


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


def test_lenh_ghep_duoc_quy_tac_sao_phu_van_bi_bao(tmp_path):
    # Quy tắc khai dạng «*» (đúng kiểu khai thật: `master..*`, `--thang * --ghi`) khớp fnmatch cả phần `| head -3` — chỉ luật
    # lệnh ghép chặn được; trước thẩm định 14/11 đột biến «thieu = not duoc_phu(c, phu)» sống sót qua mọi test.
    goc = _goc(tmp_path, "`git log --oneline -10 master..<nhánh> | head -3`\n`python3 tools/a.py --thang <T> --ghi; ls`\n",
               {"lenh": ["git log --oneline -10 master..*", "python3 tools/a.py --thang * --ghi*"], "khong_chay": [], "ghi": []})
    assert Q.duoc_phu("git log --oneline -10 master..<nhánh> | head -3", ["git log --oneline -10 master..*"]), \
        "tiền đề của ca thử: quy tắc «*» phủ được cả chuỗi ghép theo fnmatch"
    assert Q.kiem(goc, nen_tang="__khong_doi_chieu__")["thieu_khai"] == [
        ("t", "git log --oneline -10 master..<nhánh> | head -3"), ("t", "python3 tools/a.py --thang <T> --ghi; ls")]


def test_lenh_co_cho_dien_ba_cham_chua_khai_thi_bao(tmp_path):
    goc = _goc(tmp_path, "`git -C medical-ebm-automation log <…>`\n", {"lenh": [], "khong_chay": [], "ghi": []})
    assert Q.kiem(goc, nen_tang="__khong_doi_chieu__")["thieu_khai"] == [("t", "git -C medical-ebm-automation log <…>")]


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
    for cum in ("mã 1", "mã 2", "DỪNG LƯỢT NGAY", "KHÔNG ghi dòng KẾT THÚC", "--ap-dung", "Windows"):
        assert cum in khoi, cum
    assert "LƯỢT LỊCH KHÔNG TỰ SỬA" in khoi
    assert not _dau_vet_trong(_khoi_buoc_0(sk)), "bước 0 dừng mà ghi KẾT THÚC ⇒ cảm biến tính kỳ là đúng hẹn (xanh giả)"
    # Đồng bộ runtime giữ bản cũ tới khi quyền của ĐÚNG tác vụ này 🟢 (đọc tập --tac-vu từ SKILL nguồn)
    sp = importlib.util.spec_from_file_location("_tkkt_dbtvl", REPO / "tools" / "dong_bo_tac_vu_lich.py")
    D = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(D)
    assert D._TIEN_KIEM_RE.search(sk).group(1) == TV


# ── lượt dừng ở bước 0 phải GÃY ỒN trên cảm biến người chết (hành vi, không đếm chuỗi) ─────────────────────────────────


def _nap(ten: str):
    sp = importlib.util.spec_from_file_location(f"_tkkt_{ten}", REPO / "tools" / f"{ten}.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _khoi_buoc_0(sk: str) -> str:
    i, j = sk.index("\nBƯỚC 0 — TIỀN KIỂM QUYỀN"), sk.index("\nQUY TẮC CHẠY LỆNH")
    assert i < j
    return sk[i:j]


def _dau_vet_trong(van_ban: str) -> list[int | None]:
    """Các lệnh ghi dấu vết của tác vụ trong một khối SKILL, theo thứ tự: None = BẮT ĐẦU, số = KẾT THÚC mã đó."""
    mau = re.compile(rf"`python3 tools/ghi_dau_vet_lich\.py {re.escape(TV)} (--bat-dau|--ma (?:(\d)|\S+))`")
    return [None if m.group(1) == "--bat-dau" else int(m.group(2) or 2) for m in mau.finditer(van_ban)]


def _tin_hieu_cam_bien(tmp_path: Path, dong: list[int | None]) -> dict:
    """Dựng repo tạm có ĐÚNG mục sổ kỳ vọng thật của tác vụ, ghi các dòng dấu vết bằng chính `ghi_dau_vet_lich.ghi` trong giờ
    của kỳ ĐẦU từ mốc `dau_vet.tu_ngay` (tính từ cron thật — hiện 03/12/2026 18:00), rồi đọc cảm biến `kiem_lich_nen.kiem` một
    ngày sau hạn grace (máy có bản chạy của tác vụ)."""
    import datetime as dt
    G, K = _nap("ghi_dau_vet_lich"), _nap("kiem_lich_nen")
    so = json.loads((REPO / "sync" / "lich-nen-ky-vong.json").read_text(encoding="utf-8"))
    so_tam = {**so, "tac_vu": [t for t in so["tac_vu"] if t["id"] == TV]}
    assert so_tam["tac_vu"] and so_tam["tac_vu"][0]["dau_vet"]["ghi_boi"] == "tools/ghi_dau_vet_lich.py"
    tv = so_tam["tac_vu"][0]
    moc = dt.date.fromisoformat(tv["dau_vet"]["tu_ngay"])
    ky = K.cac_ky(tv["cron"], moc, moc + dt.timedelta(days=60))[0]
    _ghi(tmp_path / "sync" / "lich-nen-ky-vong.json", json.dumps(so_tam, ensure_ascii=False))
    (tmp_path / "ban_chay" / TV).mkdir(parents=True)
    for k, ma in enumerate(dong):
        G.ghi(TV, ma, tmp_path, ky + dt.timedelta(seconds=5, minutes=k))
    xet = ky + dt.timedelta(hours=int(tv.get("grace_gio", 30)) + 24)
    return K.kiem(xet, so_tam, tmp_path, tmp_path / "ban_chay")


def test_luot_dung_o_buoc_0_lam_cam_bien_bao_do(tmp_path):
    sk = SKILL.read_text(encoding="utf-8")
    assert _dau_vet_trong(sk)[:1] == [None], "lệnh dấu vết đầu tiên của SKILL phải là BẮT ĐẦU"
    # Đường dừng ở bước 0 = lệnh ĐẦU lượt (BẮT ĐẦU) + mọi lệnh dấu vết SKILL dặn trong khối bước 0 (thêm lại `--ma 2` ở đó
    # ⇒ test đỏ vì cảm biến xanh).
    kq = _tin_hieu_cam_bien(tmp_path, [None] + _dau_vet_trong(_khoi_buoc_0(sk)))
    assert kq["ok"] == 0 and [p["uu"] for p in kq["phat_hien"]] == [0], kq
    assert "quyen_lich_nen" in kq["phat_hien"][0]["thong_diep"], "cảm biến phải chỉ đúng gốc (quyền lượt lịch)"


def test_luot_chay_tron_thi_cam_bien_xanh(tmp_path):
    # Đối chứng: cùng dựng như trên, lượt đi hết (BẮT ĐẦU + KẾT THÚC cuối SKILL) ⇒ kỳ đúng hẹn. Không có ca này thì test bên trên
    # có thể đỏ vì dựng sai chứ không vì đường dừng.
    sk = SKILL.read_text(encoding="utf-8")
    cuoi = _dau_vet_trong(sk[sk.index("\nDẤU VẾT LƯỢT"):sk.index("\nBƯỚC 0 — TIỀN KIỂM QUYỀN")])
    assert cuoi[0] is None and len(cuoi) == 2 and cuoi[1] in (0, 1, 2), cuoi
    assert _tin_hieu_cam_bien(tmp_path, cuoi) == {"phat_hien": [], "khong_do_duoc": [], "ok": 1}


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
