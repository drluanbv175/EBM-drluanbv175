"""Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #9, LOW).

`ghi_alert()` trước đây luôn append vô điều kiện — chạy `main()` nhiều lần trong cùng ngày
(orchestrator A2 chạy TỪNG chủ đề riêng, mỗi lần watchlist chỉ 1/1 chủ đề, hoặc bác sĩ chạy tay
lặp lại) làm `alerts/<ngày>.md` tích nhiều dòng "🟠 QUÉT SUY GIẢM: 1/1 chủ đề..." GIỐNG HỆT nhau,
không phân biệt được chủ đề nào — đúng kiểu nhiễu dạy người đọc bỏ qua (BH32). Sửa: (1) nêu TÊN
chủ đề suy giảm thay vì chỉ số lượng, (2) `ghi_alert()` không ghi lại dòng đã có nguyên văn.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_ghi_alert_test", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_ghi_alert_test"] = S
_sp.loader.exec_module(S)

# Giữ tham chiếu HÀM GỐC trước khi test monkeypatch S.search — nếu không, gọi S.search() bên
# trong hàm giả tự trỏ ngược vào chính hàm giả (đệ quy sai), vì monkeypatch đã đổi thuộc tính
# module rồi mới chạy tới lời gọi đó.
_SEARCH_GOC = S.search


# ── 1. Đơn vị ghi_alert() — dedup theo NGUYÊN VĂN dòng, không theo lượt gọi ────────────────────
def test_ghi_alert_khong_ghi_lai_dong_da_co(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", tmp_path / "sub" / "watchlist.json")
    d1 = ["- 🟠 QUÉT SUY GIẢM: 1/1 chủ đề — A."]
    f1 = S.ghi_alert(d1, "2026-09-22")
    f2 = S.ghi_alert(d1, "2026-09-22")  # gọi lại ĐÚNG dòng cũ, mô phỏng lượt chạy thứ hai trong ngày
    assert f1 == f2
    noi_dung = f1.read_text(encoding="utf-8")
    assert noi_dung.count("QUÉT SUY GIẢM") == 1, "dòng giống hệt không được ghi lại lần thứ hai"


def test_ghi_alert_dong_khac_van_duoc_them(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", tmp_path / "sub" / "watchlist.json")
    S.ghi_alert(["- 🟠 QUÉT SUY GIẢM: 1/2 chủ đề — A."], "2026-09-22")
    f = S.ghi_alert(["- 🟠 QUÉT SUY GIẢM: 1/2 chủ đề — B."], "2026-09-22")
    noi_dung = f.read_text(encoding="utf-8")
    assert "— A." in noi_dung and "— B." in noi_dung, "hai chủ đề khác nhau đều phải được giữ"
    assert noi_dung.count("QUÉT SUY GIẢM") == 2


def test_ghi_alert_danh_sach_rong_khong_tao_file(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", tmp_path / "sub" / "watchlist.json")
    assert S.ghi_alert([], "2026-09-22") is None
    assert not (tmp_path / "alerts").exists()


def test_ghi_alert_toan_bo_trung_thi_tra_file_khong_ghi_them(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", tmp_path / "sub" / "watchlist.json")
    d = ["- 🔴 CỔNG QUÉT FAIL: chủ đề «X» — lỗi."]
    S.ghi_alert(d, "2026-09-22")
    truoc = (tmp_path / "alerts" / "2026-09-22.md").stat().st_mtime_ns
    f2 = S.ghi_alert(d, "2026-09-22")
    assert f2 is not None  # file đã tồn tại, vẫn trả về path — chỉ không GHI THÊM
    sau = (tmp_path / "alerts" / "2026-09-22.md").stat().st_mtime_ns
    noi_dung = f2.read_text(encoding="utf-8")
    assert noi_dung.count("CỔNG QUÉT FAIL") == 1


# ── 2. main() — dòng suy giảm nêu TÊN chủ đề, hai lượt cùng chủ đề không nhân đôi ───────────────
@pytest.fixture()
def _kho_tam(monkeypatch, tmp_path):
    import json

    wl = tmp_path / "sub" / "watchlist.json"
    wl.parent.mkdir(parents=True)
    wl.write_text(json.dumps({"topics": [{"topic": "SuyTim", "query": "hf guideline[pt]", "active": True}]}),
                   encoding="utf-8")
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", wl)
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    yield tmp_path, wl


def _alert_path(tmp_path) -> Path:
    import datetime as _dt
    return tmp_path / "alerts" / f"{_dt.date.today().isoformat()}.md"


def _search_suy_giam(query, days, retmax, **kw):
    """NCBI hỏng nhưng Europe PMC OK ⇒ chủ đề PASS_DEGRADED (không phải FAIL)."""
    def ncbi_hong(_u):
        raise RuntimeError("NCBI timeout")

    def epmc(_u):
        return {"hitCount": 1, "resultList": {"result": [{"pmid": "999"}]}}

    return _SEARCH_GOC(query, days, retmax, fetch_json=ncbi_hong, fallback_fetch_json=epmc, **kw)


def test_hai_luot_cung_chu_de_suy_giam_khong_nhan_doi_dong(_kho_tam, monkeypatch):
    tmp_path, wl = _kho_tam
    monkeypatch.setattr(S, "search", _search_suy_giam)
    S.main(["--watchlist", str(wl), "--days", "30", "--max", "5"])
    S.main(["--watchlist", str(wl), "--days", "30", "--max", "5"])  # lượt thứ hai, cùng ngày

    af = _alert_path(tmp_path)
    assert af.exists()
    noi_dung = af.read_text(encoding="utf-8")
    assert "SuyTim" in noi_dung, "dòng cảnh báo phải nêu TÊN chủ đề, không chỉ số lượng"
    assert noi_dung.count("QUÉT SUY GIẢM") == 1, "hai lượt cùng chủ đề suy giảm không được nhân đôi dòng"


def test_hai_chu_de_khac_nhau_suy_giam_giu_ca_hai_dong(_kho_tam, monkeypatch, tmp_path):
    import json

    wl2 = tmp_path / "sub2" / "watchlist2.json"
    wl2.parent.mkdir(parents=True)
    wl2.write_text(json.dumps({"topics": [{"topic": "COPD", "query": "copd guideline[pt]", "active": True}]}),
                   encoding="utf-8")

    monkeypatch.setattr(S, "search", _search_suy_giam)
    tmp_path0, wl = _kho_tam
    S.main(["--watchlist", str(wl), "--days", "30", "--max", "5"])       # chủ đề "SuyTim"
    S.main(["--watchlist", str(wl2), "--days", "30", "--max", "5"])      # chủ đề "COPD", cùng ngày

    af = _alert_path(tmp_path0)
    noi_dung = af.read_text(encoding="utf-8")
    assert "SuyTim" in noi_dung and "COPD" in noi_dung
    assert noi_dung.count("QUÉT SUY GIẢM") == 2, "hai chủ đề KHÁC nhau suy giảm phải giữ CẢ HAI dòng"
