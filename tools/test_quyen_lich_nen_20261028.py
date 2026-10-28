"""Quyền cho lượt lịch nền (28/10/2026, BH173).

Sự cố: gói tuần W44 (kỳ 26/10/2026) không có — lượt lịch chạy ở chế độ quyền «default», `python3 tools/tu_de_xuat_viec.py`
đòi duyệt, không ai bấm ⇒ lượt bị cắt ngang sau 73 giây mà bộ lập lịch vẫn ghi «succeeded». 16/17 lệnh của gói tuần chưa được
phép. Bác sĩ chọn «khai đúng lệnh»: `sync/quyen-lich-nen.json` (đi qua git) → `tools/quyen_lich_nen.py --ap-dung` áp vào
`.claude/settings.local.json`; giác quan báo TRƯỚC khi lượt hỏng.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import quyen_lich_nen as Q  # noqa: E402

SKILL_MAU = """Bước 1: `python3 tools/a.py --json-report state/tuan.json`
Bước 2: `python3 tools/b.py --queue queue/tuan-<W>.md --unpaywall` rồi `python3 tools/a.py --json-report state/tuan.json`
Cho bác sĩ: `python3 tools/c.py --ap-dung`
Không phải lệnh: `EBM-Dashboards/x.json` · `--queue`
"""

KHAI_MAU = {
    "nen_tang": "darwin",
    "tac_vu": {
        "tv-mau": {
            "lenh": ["python3 tools/a.py --json-report state/tuan.json", "python3 tools/b.py --queue queue/tuan-* --unpaywall"],
            "khong_chay": ["python3 tools/c.py --ap-dung"],
            "ghi": ["queue/**"],
        }
    },
}


def _goc(tmp_path: Path, skill: str = SKILL_MAU, khai: dict | None = None, settings: dict | None = None) -> Path:
    (tmp_path / "sync" / "scheduled-tasks" / "tv-mau").mkdir(parents=True)
    (tmp_path / "sync" / "scheduled-tasks" / "tv-mau" / "SKILL.md").write_text(skill, encoding="utf-8")
    (tmp_path / "sync" / "quyen-lich-nen.json").write_text(json.dumps(khai or KHAI_MAU), encoding="utf-8")
    if settings is not None:
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.local.json").write_text(json.dumps(settings), encoding="utf-8")
    return tmp_path


def test_tach_lenh_trong_backtick_bo_trung():
    assert Q.lenh_trong_skill(SKILL_MAU) == [
        "python3 tools/a.py --json-report state/tuan.json",
        "python3 tools/b.py --queue queue/tuan-<W>.md --unpaywall",
        "python3 tools/c.py --ap-dung",
    ]


def test_tham_so_khop_dau_sao_nhung_khong_noi_rong():
    assert Q.duoc_phu("python3 tools/b.py --queue queue/tuan-<W>.md --unpaywall", ["python3 tools/b.py --queue queue/tuan-* --unpaywall"])
    assert not Q.duoc_phu("python3 tools/b.py --queue queue/tuan-<W>.md", ["python3 tools/b.py --queue queue/tuan-* --unpaywall"])
    assert not Q.duoc_phu("python3 tools/b.py --ap-dung", ["python3 tools/b.py"])


def test_quy_tac_may_dung_cu_phap_claude_code(tmp_path):
    q = Q.quy_tac_may(KHAI_MAU, tmp_path)
    assert "Bash(python3 tools/b.py --queue queue/tuan-* --unpaywall)" in q
    assert f"Edit(//{str(tmp_path).lstrip('/')}/queue/**)" in q
    assert not any("c.py" in x for x in q), "lệnh `khong_chay` (chỉ in cho bác sĩ) không được vào allow"


def test_lenh_moi_trong_skill_chua_khai_thi_bao(tmp_path):
    goc = _goc(tmp_path, SKILL_MAU + "Bước 3: `python3 tools/moi.py`\n", settings={"permissions": {"allow": []}})
    kq = Q.kiem(goc, nen_tang="darwin")
    assert kq["thieu_khai"] == [("tv-mau", "python3 tools/moi.py")]


def test_may_chua_ap_thi_bao_va_ap_dung_chi_them_dung_muc_khai(tmp_path):
    goc = _goc(tmp_path, settings={"permissions": {"allow": ["Bash(git status)"], "deny": ["Bash(rm *)"]}, "khac": 1})
    st = goc / ".claude" / "settings.local.json"
    assert len(Q.kiem(goc, nen_tang="darwin")["thieu_may"]) == 3
    assert Q.ap_dung(goc) == 3
    d = json.loads(st.read_text(encoding="utf-8"))
    assert d["permissions"]["allow"][0] == "Bash(git status)" and d["permissions"]["deny"] == ["Bash(rm *)"] and d["khac"] == 1
    assert len(list(st.parent.glob("settings.local.json.bak-quyen-lich-*"))) == 1
    assert Q.kiem(goc, nen_tang="darwin") == {"khong_do": [], "thieu_khai": [], "thieu_may": []}
    assert Q.ap_dung(goc) == 0, "chạy lại không được thêm trùng"
    assert len(list(st.parent.glob("settings.local.json.bak-quyen-lich-*"))) == 1, "không có gì để thêm thì không sao lưu"


@pytest.mark.parametrize("settings, nen_tang", [(None, "darwin"), ({"permissions": {"allow": []}}, "win32")])
def test_khong_do_duoc_khong_bao_gio_la_du(tmp_path, settings, nen_tang):
    goc = _goc(tmp_path, settings=settings)
    kq = Q.kiem(goc, nen_tang=nen_tang)
    assert kq["khong_do"] and kq["thieu_may"] == []


@pytest.mark.parametrize("kq, ma", [
    ({"khong_do": [], "thieu_khai": [], "thieu_may": []}, 0),
    ({"khong_do": [], "thieu_khai": [("tv", "python3 tools/moi.py")], "thieu_may": []}, 1),
    ({"khong_do": [], "thieu_khai": [], "thieu_may": ["Bash(python3 tools/a.py)"]}, 1),
    ({"khong_do": ["không đọc được settings.local.json"], "thieu_khai": [], "thieu_may": []}, 2),
])
def test_ma_thoat(monkeypatch, kq, ma):
    monkeypatch.setattr(Q, "kiem", lambda: kq)
    assert Q.main([]) == ma


# ── trên repo thật ───────────────────────────────────────────────────────────────────────────────────────────────────────


def test_moi_lenh_cua_tac_vu_lich_da_khai_tren_repo():
    """Thêm lệnh vào SKILL.md của tác vụ lịch mà quên khai ⇒ đỏ ở đây (lượt lịch sẽ bị cắt ngang)."""
    kq = Q.kiem(REPO, nen_tang="__khong_doi_chieu_may__")
    assert kq["thieu_khai"] == [], kq["thieu_khai"]


def test_khai_khong_chua_lenh_ghi_quyet_dinh_thay_bac_si():
    khai = json.loads((REPO / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))
    cam = ("ap_dung_de_xuat_watchlist", "ghi_vuot_qua_da_xet", "approve_gate", "nap_endnote", "manage_ledger",
           "ingest_dashboard", "ghi_duyet_the_tuan", "quyen_lich_nen")
    for ten, tv in khai["tac_vu"].items():
        for c in tv["lenh"]:
            assert not any(x in c for x in cam), f"{ten}: lệnh ghi quyết định/cấu hình không được khai cho lượt lịch: {c}"
            assert "--ap-dung" not in c, f"{ten}: {c}"


def test_bang_tu_de_xuat_co_noi_giac_quan_quyen_lich():
    dong = [d for d in (REPO / "tools" / "tu_de_xuat_viec.py").read_text(encoding="utf-8").splitlines()
            if "_qln.kiem()" in d and not d.lstrip().startswith("#")]
    assert dong, "giác quan quyền lượt lịch không được gọi trong tu_de_xuat_viec.py (BH41: công cụ không ai gọi thì không tồn tại)"


def test_liet_ke_phai_sinh_cu_tra_ten_tep(tmp_path):
    import tu_de_xuat_viec as T
    (tmp_path / "derivatives").mkdir()
    (tmp_path / "WebDashboard_EBM_VanDeCuThe_X_20261028.html").write_text("<html></html>", encoding="utf-8")
    ds = T.liet_ke_dashboard_phai_sinh_loi_thoi(tmp_path)
    assert [f.name for f in ds] == ["WebDashboard_EBM_VanDeCuThe_X_20261028.html"]
    assert T.dem_dashboard_phai_sinh_loi_thoi(tmp_path) == 1
