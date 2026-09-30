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


# ── thư mục cách ly `_quarantine-conflict-copy/` (30/09/2026) ────────────────
# Tên máy ĐÚNG ca đo: LocalHostName của Mac là «Dr-Luan-BV175-2». `_TEN_BAN_SAO` là tên mà luật hậu tố máy NHẬN trên máy ấy
# («tên-<máy>.ext») — dùng để thử luật MIỄN theo thư mục. Tên tệp của chính ca đo (`_TEN_CO_NGAY`: tệp cách ly từ 16/09, đổi
# tên kèm ngày) từng bị đọc thành bản lặp vì ngày «-20260916» khớp «-N»; từ tối 30/09 nó không còn là tên bản sao ở bất cứ
# đâu — xem khối «số bản lặp ≠ ngày» bên dưới.
_TEN_BAN_SAO = "so-tong-thuat-Dr-Luan-BV175-2.json"
_TEN_CO_NGAY = "so-tong-thuat-Dr-Luan-BV175-2-20260916.json"
_MAY_MAC = "Dr-Luan-BV175-2.local"


def _dat_tep(root: Path, *rel: str) -> None:
    for r in rel:
        p = root / r
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")


def _quet_muc_1(monkeypatch, root: Path, may: str = _MAY_MAC) -> tuple[str, list[str]]:
    monkeypatch.setattr(S, "ROOT", root)
    monkeypatch.setattr(S.socket, "gethostname", lambda: may)
    level, details = S.check_conflict_copies()
    return level, [d.replace("\\", "/") for d in details]


def test_tep_trong_thu_muc_cach_ly_khong_chan(monkeypatch, tmp_path):
    """Cách ly là cách xử lý ĐÃ DUYỆT cho bản sao xung đột (CLAUDE.md §2.1) — tệp nằm ở đó không được làm mục 1 🔴
    (đo 30/09: 4 tệp cách ly từ 16/09 chặn cả chốt đầu phiên), nhưng vẫn phải THẤY ở mức thông tin. Thư mục cách ly nằm
    sâu mấy tầng cũng vậy, và nhánh « 2»/«-dr-luan có bản gốc» đi qua cùng một cửa."""
    root = tmp_path / "Claude AI"
    _dat_tep(root,
             f"EBM-Dashboards/tong_thuat/_quarantine-conflict-copy/{_TEN_BAN_SAO}",
             "reports/_quarantine-conflict-copy/cu/BAO-CAO-C010000PK16BSL-3.md",
             "state/_quarantine-conflict-copy/so.json",
             "state/_quarantine-conflict-copy/so 2.json")

    level, details = _quet_muc_1(monkeypatch, root)

    assert level == "GREEN", details
    assert len(details) == 3, details
    assert all("đã cách ly" in d and "không chặn" in d for d in details), details


def test_cung_ten_tep_ngoai_thu_muc_cach_ly_van_chan(monkeypatch, tmp_path):
    """Luật miễn KHÔNG được làm yếu việc bắt bản sao thật: đúng tên tệp ấy, đặt ngay cạnh thư mục cách ly ⇒ vẫn 🔴;
    có tệp cách ly nằm bên cạnh cũng không hạ được mức chung."""
    root = tmp_path / "Claude AI"
    _dat_tep(root,
             f"EBM-Dashboards/tong_thuat/_quarantine-conflict-copy/{_TEN_BAN_SAO}",
             f"EBM-Dashboards/tong_thuat/{_TEN_BAN_SAO}")

    level, details = _quet_muc_1(monkeypatch, root)

    assert level == "RED", details
    assert details[0] == f"EBM-Dashboards/tong_thuat/{_TEN_BAN_SAO}", details   # bản ngoài cách ly: chặn, không gắn nhãn miễn
    assert len(details) == 2 and "đã cách ly" in details[1], details


def test_ban_lap_va_ban_may_kia_ngoai_cach_ly_van_chan(monkeypatch, tmp_path):
    """BH133 giữ nguyên: bản lặp «-<máy>-N» và bản do máy KIA đẻ, nằm NGOÀI thư mục cách ly ⇒ 🔴."""
    root = tmp_path / "Claude AI"
    _dat_tep(root,
             ".claude/agents/dieu-phoi-lam-sang-TESTHOST-2.md",
             "medical-ebm-automation/CLAUDE-C010000PK16BSL.md",
             "cloud-mirror/_quarantine-conflict-copy/trang-thai-C010000PK16BSL.json")

    level, details = _quet_muc_1(monkeypatch, root, may="TESTHOST")

    assert level == "RED", details
    assert sorted(d for d in details if "đã cách ly" not in d) == [
        ".claude/agents/dieu-phoi-lam-sang-TESTHOST-2.md",
        "medical-ebm-automation/CLAUDE-C010000PK16BSL.md",
    ]


def test_mien_cach_ly_chi_theo_dung_ten_thu_muc(monkeypatch, tmp_path):
    """Miễn quá tay là mở lại lỗ BH133. Không được miễn khi: chuỗi «_quarantine-conflict-copy» chỉ nằm trong TÊN TỆP;
    thư mục chỉ có tên GẦN giống; hay chính ROOT nằm dưới một thư mục tên cách ly (khi đó cả cây sẽ được miễn)."""
    root = tmp_path / "_quarantine-conflict-copy" / "Claude AI"
    ngoai = ["docs/_quarantine-conflict-copy-ghi-chu-TESTHOST.md",
             "docs/_quarantine-conflict-copy-cu/a-TESTHOST.md",
             "docs/quarantine/b-TESTHOST-2.md",
             "docs/c-C010000PK16BSL.md"]
    _dat_tep(root, *ngoai)

    level, details = _quet_muc_1(monkeypatch, root, may="TESTHOST")

    assert level == "RED", details
    assert sorted(details) == sorted(ngoai), details


def test_tep_cach_ly_trong_claude_state_van_khong_chan(monkeypatch, tmp_path):
    """`.claude/state/_quarantine-conflict-copy/` vừa là artefact sinh vừa là cách ly — nhãn nào cũng được, miễn không 🔴."""
    root = tmp_path / "Claude AI"
    _dat_tep(root, ".claude/state/_quarantine-conflict-copy/session-Dr-Luan-BV175-2.json")

    level, details = _quet_muc_1(monkeypatch, root)

    assert level == "GREEN" and len(details) == 1, details


# ── số bản lặp ≠ ngày (30/09/2026, tối) ──────────────────────────────────────
def test_ngay_sau_ten_may_khong_bi_doc_thanh_so_ban_lap(monkeypatch, tmp_path):
    """GỐC của 🔴 giả tối 30/09: tệp cách ly đổi tên kiểu «tên-Dr-Luan-BV175-2-20260916.json» gặp tên máy «Dr-Luan-BV175-2»
    ⇒ luật «-<máy>-N» (N dài bao nhiêu cũng nhận) đọc ngày 8 chữ số thành số bản lặp. OneDrive không đặt tên như thế: ngày/giờ
    sau tên máy là do người hay agent gắn khi đổi tên. Ở ĐÂU cũng không chấm — trong hay ngoài thư mục cách ly, máy này hay
    máy kia, 4 chữ số (năm) cũng vậy."""
    root = tmp_path / "Claude AI"
    _dat_tep(root,
             f"EBM-Dashboards/tong_thuat/_quarantine-conflict-copy/{_TEN_CO_NGAY}",     # đúng tên + đúng chỗ của ca đo
             f"EBM-Dashboards/tong_thuat/{_TEN_CO_NGAY}",                               # cùng tên, NGOÀI cách ly
             "cloud-mirror/trang-thai-chung-cu-Dr-Luan-BV175-2-20260914-185600.json",   # ngày + giờ
             "reports/BAO-CAO-C010000PK16BSL-20260916.md",                              # máy kia + ngày
             "docs/ke-hoach-C010000PK16BSL-2026.md",                                    # máy kia + năm
             "state/so-Dr-Luan-BV175-2-20260916")                                       # không đuôi

    level, details = _quet_muc_1(monkeypatch, root)

    assert (level, details) == ("GREEN", []), details


def test_so_ban_lap_that_mot_den_ba_chu_so_van_bi_bat(monkeypatch, tmp_path):
    """Siết «-N» không được làm mù bản lặp THẬT. Đo 30/09 trên cây thật: số lặp lớn nhất «-14» (`app-Dr Luân BV175-14.log`)
    ⇒ 2 chữ số là có thật, chừa tới 3 chữ số. Từ 4 chữ số trở lên (năm, ngày, giờ) không còn là số bản lặp."""
    root = tmp_path / "Claude AI"
    bat = ["docs/a-TESTHOST-2.md",
           "docs/b-C010000PK16BSL-14.md",
           "docs/c-C010000PK16BSL-999.md",
           "docs/d-TESTHOST-107"]                           # không đuôi, 3 chữ số
    _dat_tep(root, *bat, "docs/e-C010000PK16BSL-1000.md")

    level, details = _quet_muc_1(monkeypatch, root, may="TESTHOST")

    assert level == "RED", details
    assert sorted(details) == sorted(bat), details


def test_ban_doi_ten_kem_ngay_nam_canh_ban_goc_van_bi_bat(monkeypatch, tmp_path):
    """Siết «-N» không đụng nhánh «-dr-luan có bản gốc»: bản đổi tên kèm ngày mà còn nằm NGAY CẠNH bản gốc, ngoài thư mục
    cách ly, vẫn là bản sao chưa dọn ⇒ 🔴 — hành vi có từ trước BH133, không phụ thuộc tên máy đang chạy."""
    root = tmp_path / "Claude AI"
    _dat_tep(root,
             "EBM-Dashboards/tong_thuat/so-tong-thuat.json",
             f"EBM-Dashboards/tong_thuat/{_TEN_CO_NGAY}")

    level, details = _quet_muc_1(monkeypatch, root, may="TESTHOST")

    assert level == "RED", details
    assert len(details) == 1 and details[0].startswith(f"EBM-Dashboards/tong_thuat/{_TEN_CO_NGAY}"), details


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


def test_nhanh_that_ten_co_ten_may_va_ngay_khong_phai_ref_ma(monkeypatch, tmp_path):
    """Nhánh THẬT tên kiểu «moc-plugin-c010000pk16bsl-20260930» (tên máy + ngày) không phải bản sao xung đột của một nhánh
    «moc-plugin» nào cả. Luật «-N» không giới hạn đọc ngày thành số lặp ⇒ «ref ma giữ commit mà nhánh thật KHÔNG có» ⇒ 🔴
    giả, kèm lời khuyên dời một nhánh đang dùng."""
    repo, _c1, c2 = _repo_hai_commit(tmp_path)
    _git(repo, "branch", "moc-plugin-c010000pk16bsl-20260930", c2)
    _chi_repo(monkeypatch, repo)

    level, details = S.check_git_conflict_copies()

    assert (level, details) == ("GREEN", []), details


def test_ref_ma_so_lap_ba_chu_so_van_la_do(monkeypatch, tmp_path):
    """Số lặp 3 chữ số vẫn là bản sao: phải DÒ được và GỠ được hậu tố để so với `main` thật. Gỡ trượt thì ref ma bị so với
    chính nó ⇒ 🟡 «dời được» trong khi commit chỉ còn ref ma giữ."""
    repo, c1, c2 = _repo_hai_commit(tmp_path)
    _git(repo, "update-ref", "refs/heads/main", c1)
    (repo / ".git" / "refs" / "heads" / "main-C010000PK16BSL-100").write_text(c2 + "\n", encoding="utf-8")
    _chi_repo(monkeypatch, repo)

    level, details = S.check_git_conflict_copies()

    assert level == "RED"
    assert any("main-C010000PK16BSL-100" in d and "`refs/heads/main`" in d and "rescue/" in d for d in details), details


def test_main_that_su_chay_muc_ban_sao_trong_git(monkeypatch, capsys):
    """Có hàm mà `main()` không gọi thì với chốt đầu phiên nó không tồn tại (họ BH41)."""
    for ten in ("check_conflict_copies", "check_git_health", "check_core_materialized", "check_recent_writes"):
        monkeypatch.setattr(S, ten, lambda: ("GREEN", []))
    monkeypatch.setattr(S, "check_git_conflict_copies", lambda: ("RED", ["ref ma"]))

    assert S.main() == 2
    assert "TRONG .git" in capsys.readouterr().out
