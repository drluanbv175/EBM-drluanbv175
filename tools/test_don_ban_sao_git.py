"""tools/don_ban_sao_git.py — dọn bản sao xung đột OneDrive trong `.git`: chạy thử không đổi gì; áp dụng thì CỨU ref chỉ
bản sao giữ rồi DỜI bản sao ra ngoài (sao lưu, so SHA-256), không xoá gì; bản sao config/HEAD khác bản đang dùng ⇒ bỏ qua;
quét dở ⇒ không làm gì. 06/10/2026."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import don_ban_sao_git as D  # noqa: E402
import sync_safety_check as S  # noqa: E402

NGAY = "20261006"


def _git(repo: Path, *lenh: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                        "-c", "commit.gpgsign=false", *lenh], check=True, capture_output=True, text=True)
    return p.stdout.strip()


def _repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "Claude AI"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    for i in (1, 2):
        (repo / "a.txt").write_text(str(i), encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", f"c{i}")
    return repo, _git(repo, "rev-parse", "HEAD~1"), _git(repo, "rev-parse", "HEAD")


def _gia_may(monkeypatch) -> None:
    monkeypatch.setattr(S.socket, "gethostname", lambda: "TESTHOST")


def _don(repo: Path, tmp_path: Path, ap_dung: bool):
    return D.don([(".", repo)], sao_luu=tmp_path / "sao-luu", ap_dung=ap_dung, ngay=NGAY)


def test_chay_thu_khong_doi_gi(monkeypatch, tmp_path):
    repo, _c1, _c2 = _repo(tmp_path)
    g = repo / ".git"
    (g / "FETCH_HEAD-C010000PK16BSL").write_text("x\n", encoding="utf-8")
    (g / "index-TESTHOST-2").write_bytes((g / "index").read_bytes())
    _gia_may(monkeypatch)

    ma, ket = _don(repo, tmp_path, ap_dung=False)

    assert ma == 0
    assert {m["rel"] for m in ket["repo"][0]["muc"]} == {"FETCH_HEAD-C010000PK16BSL", "index-TESTHOST-2"}
    assert (g / "FETCH_HEAD-C010000PK16BSL").exists() and (g / "index-TESTHOST-2").exists()
    assert not (tmp_path / "sao-luu").exists(), "chạy thử không được tạo gì"


def test_ap_dung_doi_rac_ra_ngoai_dung_byte_ban_goc_con_nguyen(monkeypatch, tmp_path):
    repo, _c1, _c2 = _repo(tmp_path)
    g = repo / ".git"
    (g / "FETCH_HEAD").write_text("that\n", encoding="utf-8")
    (g / "FETCH_HEAD-C010000PK16BSL").write_text("ban sao\n", encoding="utf-8")
    (g / "logs" / "HEAD-Dr Luân BV175").write_text("reflog\n", encoding="utf-8")
    _gia_may(monkeypatch)

    ma, ket = _don(repo, tmp_path, ap_dung=True)

    assert ma == 0, ket
    dich = tmp_path / "sao-luu" / "goc" / ".git"
    assert (dich / "FETCH_HEAD-C010000PK16BSL").read_text(encoding="utf-8") == "ban sao\n"
    assert (dich / "logs" / "HEAD-Dr Luân BV175").read_text(encoding="utf-8") == "reflog\n"
    assert not (g / "FETCH_HEAD-C010000PK16BSL").exists() and not (g / "logs" / "HEAD-Dr Luân BV175").exists()
    assert (g / "FETCH_HEAD").read_text(encoding="utf-8") == "that\n", "bản gốc không được đụng"
    manifest = json.loads((tmp_path / "sao-luu" / "manifest.json").read_text(encoding="utf-8"))
    assert {d["rel"] for d in manifest["repo"][0]["da_doi"]} == {"FETCH_HEAD-C010000PK16BSL", "logs/HEAD-Dr Luân BV175"}
    monkeypatch.setattr(S, "GIT_REPOS", [(".", repo)])
    assert S.check_git_conflict_copies() == ("GREEN", [])


def test_packed_refs_giu_commit_mat_thi_cuu_truoc_roi_moi_doi(monkeypatch, tmp_path):
    repo, c1, c2 = _repo(tmp_path)
    _git(repo, "update-ref", "refs/heads/main", c1)            # c2 chỉ còn bản sao packed-refs giữ
    (repo / ".git" / "packed-refs-C010000PK16BSL").write_text(f"{c2} refs/heads/main\n", encoding="utf-8")
    _gia_may(monkeypatch)

    ma0, ket0 = _don(repo, tmp_path, ap_dung=False)
    assert ma0 == 0 and ket0["repo"][0]["muc"][0]["can_cuu"] == [{"ref": "refs/heads/main", "sha": c2, "kieu": "commit"}]
    ma, ket = _don(repo, tmp_path, ap_dung=True)

    assert ma == 0, ket
    assert _git(repo, "rev-parse", f"refs/heads/rescue/{NGAY}/heads/main") == c2
    assert not (repo / ".git" / "packed-refs-C010000PK16BSL").exists()
    monkeypatch.setattr(S, "GIT_REPOS", [(".", repo)])
    assert S.check_git_conflict_copies() == ("GREEN", [])


def test_tree_codex_khong_ai_giu_cuu_vao_refs_rescue_khong_phai_nhanh(monkeypatch, tmp_path):
    repo, c1, _c2 = _repo(tmp_path)
    cay = _git(repo, "rev-parse", f"{c1}^{{tree}}")
    (repo / ".git" / "packed-refs-C010000PK16BSL").write_text(f"{cay} refs/codex/turn-diffs/x\n", encoding="utf-8")
    _gia_may(monkeypatch)

    ma, ket = _don(repo, tmp_path, ap_dung=True)

    assert ma == 0, ket
    assert _git(repo, "rev-parse", f"refs/rescue/{NGAY}/codex/turn-diffs/x") == cay
    assert "rescue" not in _git(repo, "branch", "--list"), "tree không được thành nhánh"


def test_ref_codex_tro_tree_dang_dung_va_nhanh_da_gop_khong_cuu(monkeypatch, tmp_path):
    """Đúng ca đo 06/10/2026 trên repo gốc: cả 4 ref của bản sao đều còn ref thật giữ ⇒ không cứu gì, chỉ dời."""
    repo, c1, c2 = _repo(tmp_path)
    cay = _git(repo, "rev-parse", "HEAD^{tree}")
    _git(repo, "update-ref", "refs/codex/turn-diffs/a", cay)
    _git(repo, "update-ref", "refs/heads/main", c1)           # c2 chỉ còn nhánh MÁY CHỦ (ma) giữ — máy chủ là nguồn sự thật
    (repo / ".git" / "packed-refs-C010000PK16BSL").write_text(
        f"{cay} refs/codex/turn-diffs/a\n{c1} refs/heads/claude/da-gop-roi-xoa\n{c2} refs/remotes/origin/xoa\n",
        encoding="utf-8")
    ma_roi = repo / ".git" / "refs" / "remotes" / "origin" / "xoa2-C010000PK16BSL"
    ma_roi.parent.mkdir(parents=True)
    ma_roi.write_text(c2 + "\n", encoding="utf-8")
    _gia_may(monkeypatch)

    ma, ket = _don(repo, tmp_path, ap_dung=True)

    assert ma == 0, ket
    assert ket["repo"][0]["da_cuu"] == [], "ref Codex còn ref thật giữ, nhánh đã gộp, nhánh máy chủ ⇒ không cứu"
    assert not (repo / ".git" / "packed-refs-C010000PK16BSL").exists() and not ma_roi.exists()


def test_ref_ma_roi_giu_commit_mat_cuu_roi_doi_khoi_for_each_ref(monkeypatch, tmp_path):
    repo, c1, c2 = _repo(tmp_path)
    _git(repo, "update-ref", "refs/heads/main", c1)
    (repo / ".git" / "refs" / "heads" / "main-C010000PK16BSL-2").write_text(c2 + "\n", encoding="utf-8")
    _gia_may(monkeypatch)

    ma, ket = _don(repo, tmp_path, ap_dung=True)

    assert ma == 0, ket
    assert _git(repo, "rev-parse", f"refs/heads/rescue/{NGAY}/heads/main") == c2
    assert "main-C010000PK16BSL-2" not in _git(repo, "for-each-ref", "--format=%(refname)")


def test_ten_cuu_trung_ref_khac_thi_them_so(monkeypatch, tmp_path):
    repo, c1, c2 = _repo(tmp_path)
    _git(repo, "update-ref", "refs/heads/main", c1)
    _git(repo, "branch", f"rescue/{NGAY}/heads/main", c1)     # tên cứu đã có, trỏ commit KHÁC
    (repo / ".git" / "packed-refs-C010000PK16BSL").write_text(f"{c2} refs/heads/main\n", encoding="utf-8")
    _gia_may(monkeypatch)

    ma, ket = _don(repo, tmp_path, ap_dung=True)

    assert ma == 0, ket
    assert _git(repo, "rev-parse", f"refs/heads/rescue/{NGAY}/heads/main") == c1, "không được đè ref có sẵn"
    assert _git(repo, "rev-parse", f"refs/heads/rescue/{NGAY}/heads/main-2") == c2


def test_ban_sao_config_khac_thi_bo_qua_giong_thi_doi(monkeypatch, tmp_path):
    repo, _c1, _c2 = _repo(tmp_path)
    g = repo / ".git"
    (g / "config-C010000PK16BSL").write_text((g / "config").read_text(encoding="utf-8")
                                             + "[core]\n\thooksPath = .githooks\n", encoding="utf-8")
    (g / "config-Dr Luân BV175").write_text((g / "config").read_text(encoding="utf-8"), encoding="utf-8")
    _gia_may(monkeypatch)

    ma, ket = _don(repo, tmp_path, ap_dung=True)

    assert ma == 1, "còn mục người phải xem ⇒ mã 1"
    assert (g / "config-C010000PK16BSL").exists(), "bản sao config có thiết lập bản đang dùng không có ⇒ KHÔNG dời"
    assert not (g / "config-Dr Luân BV175").exists()
    assert ket["repo"][0]["bo_qua"][0]["rel"] == "config-C010000PK16BSL"
    assert "hooksPath" in ket["repo"][0]["bo_qua"][0]["ly_do"].replace("hookspath", "hooksPath")


def test_quet_chua_het_thi_khong_lam_gi(monkeypatch, tmp_path):
    repo, _c1, _c2 = _repo(tmp_path)
    (repo / ".git" / "FETCH_HEAD-C010000PK16BSL").write_text("x\n", encoding="utf-8")
    _gia_may(monkeypatch)
    monkeypatch.setattr(S, "_quet_ban_sao_git", lambda *a, **k: ([("FETCH_HEAD-C010000PK16BSL", "c010000pk16bsl")], False))

    ma, ket = _don(repo, tmp_path, ap_dung=True)

    assert ma == 2 and "quét .git chưa hết" in ket["repo"][0]["loi"]
    assert (repo / ".git" / "FETCH_HEAD-C010000PK16BSL").exists()


def test_cli_mac_dinh_chay_thu(monkeypatch, tmp_path, capsys):
    repo, _c1, _c2 = _repo(tmp_path)
    (repo / ".git" / "FETCH_HEAD-C010000PK16BSL").write_text("x\n", encoding="utf-8")
    _gia_may(monkeypatch)
    monkeypatch.setattr(S, "GIT_REPOS", [(".", repo)])

    assert D.main(["--sao-luu", str(tmp_path / "sl")]) == 0
    assert "CHẠY THỬ" in capsys.readouterr().out and (repo / ".git" / "FETCH_HEAD-C010000PK16BSL").exists()
    assert D.main(["--ap-dung", "--sao-luu", str(tmp_path / "sl")]) == 0
    assert not (repo / ".git" / "FETCH_HEAD-C010000PK16BSL").exists()
    assert (tmp_path / "sl" / "goc" / ".git" / "FETCH_HEAD-C010000PK16BSL").exists()
