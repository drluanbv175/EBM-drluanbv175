"""Làn dự phòng tính phí: engine KHÔNG NẠP ĐƯỢC (ImportError) là «chắc chắn không gọi», không tiêu suất tuần (26/10/2026).

Đo 26/10/2026: `python3 ops/orchestrator.py --cu-nhat 3 --online` chạy bộ quét bằng python3 HỆ THỐNG (thiếu thư viện của
engine) ⇒ `from app.sources.base import RawRecord` ném ModuleNotFoundError TRƯỚC mọi lời gọi nguồn tính phí, nhưng nơi gọi
xếp nó là «lần gọi LỖI» ⇒ «Viêm phổi cộng đồng (CAP)» mất 1 suất tuần với 0 lời gọi. Offline: engine giả trong tmp_path.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

NGUON = Path(__file__).resolve().parents[1] / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_loi_nap_2610", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_loi_nap_2610"] = S  # @dataclass tra sys.modules lúc dựng lớp — đăng ký TRƯỚC exec
_sp.loader.exec_module(S)


@pytest.fixture()
def engine_gia(tmp_path, monkeypatch):
    """Engine giả: app/sources/base.py + app/services/fallback_ladder.py; mỗi test tự viết nội dung."""
    goc = tmp_path / "medical-ebm-automation"
    for thu_muc in ("app", "app/sources", "app/services"):
        (goc / thu_muc).mkdir(parents=True, exist_ok=True)
        (goc / thu_muc / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(S, "_tim_medical_ebm_automation", lambda: goc)
    monkeypatch.setattr(sys, "path", list(sys.path))  # hàm tự nối đường dẫn engine — trả lại sau test
    for ten in [k for k in sys.modules if k == "app" or k.startswith("app.")]:
        monkeypatch.delitem(sys.modules, ten)  # engine thật đã nạp ở test khác không được che engine giả
    return goc


def test_base_thieu_thu_vien_thi_chac_chan_khong_goi(engine_gia):
    (engine_gia / "app/sources/base.py").write_text("import thu_vien_khong_co_2610\n", encoding="utf-8")
    (engine_gia / "app/services/fallback_ladder.py").write_text("", encoding="utf-8")
    kq = S.bo_sung_du_phong_lane("community acquired pneumonia", [], 5)
    assert kq.so_goi == 0 and tuple(kq) == ([], ""), "lỗi nạp engine ≠ lần gọi lỗi"
    assert "ModuleNotFoundError" in kq.ly_do_khong_goi and "thu_vien_khong_co_2610" in kq.ly_do_khong_goi


def test_bac_thang_thieu_thu_vien_thi_chac_chan_khong_goi(engine_gia):
    (engine_gia / "app/sources/base.py").write_text("class RawRecord:\n    pass\n", encoding="utf-8")
    (engine_gia / "app/services/fallback_ladder.py").write_text("import thu_vien_khong_co_2610b\n", encoding="utf-8")
    kq = S.bo_sung_du_phong_lane("community acquired pneumonia", [], 5)
    assert kq.so_goi == 0 and tuple(kq) == ([], "") and "thu_vien_khong_co_2610b" in kq.ly_do_khong_goi


def test_ham_tiem_san_van_chay_khi_base_khong_nap_duoc(engine_gia):
    # Caller tiêm `bo_sung_fn` (test/caller khác) ⇒ dùng bản ghi tối thiểu, không phụ thuộc engine (giữ hành vi 22/09).
    (engine_gia / "app/sources/base.py").write_text("import thu_vien_khong_co_2610c\n", encoding="utf-8")
    kq = S.bo_sung_du_phong_lane("x", [], 5, bo_sung_fn=lambda *a, **k: ([], {"active": True, "tang": {"c": {"da_goi": 1}}}))
    assert kq.so_goi == 1


def test_ket_qua_cu_khong_co_ly_do_van_tao_duoc():
    kq = S.KetQuaDuPhong([], "", 0)
    assert kq.ly_do_khong_goi == "" and tuple(kq) == ([], "")


def test_luot_quet_khong_tieu_suat_va_ghi_ro_ly_do(tmp_path, monkeypatch):
    """Toàn lượt: làn trả «không gọi vì engine không nạp được» ⇒ không ghi mốc/dấu lỗi, ghi chú nêu lý do + cách chạy đúng."""
    import json
    wl = tmp_path / "watchlist.json"
    wl.write_text(json.dumps({"topics": [{"topic": "Alpha", "query": "q alpha", "active": True,
                                          "truy_van_du_phong": "alpha treatment"}]}), encoding="utf-8")
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", wl)
    for ten in ("search_preprint_lane", "search_trials_lane", "search_scopus_lane", "search_core_lane"):
        monkeypatch.setattr(S, ten, lambda *a, **k: [])
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda ds: list(ds))
    monkeypatch.setattr(S, "_pmid_da_co_trong_kho", lambda: set())
    monkeypatch.setattr(S, "search", lambda query, days, retmax, **kw: ["123"])
    monkeypatch.setattr(S, "summarize", lambda ids: [S.Candidate(p, "2026 Sep 20", "Bài thường", f"u{p}") for p in ids])
    ly_do = "engine không nạp được (ModuleNotFoundError: No module named 'pydantic')"
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda *a, **k: S.KetQuaDuPhong([], "", 0, ly_do_khong_goi=ly_do))
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()
    S._VUOT_TRAN.clear()
    bao_cao = tmp_path / "bc.json"
    assert S.main(["--watchlist", str(wl), "--days", "30", "--json-report", str(bao_cao), "--topic", "Alpha",
                   "--khong-cursor"]) == 0
    bc = json.loads(bao_cao.read_text(encoding="utf-8"))
    assert bc["du_phong_da_leo_thang"] == [] and bc["du_phong_loi"] == []
    assert bc["du_phong_khong_leo_thang"] == {"nguon_khong_goi": 1}
    so = tmp_path / ".du-phong-trang-thai.json"
    if so.exists():
        d = json.loads(so.read_text(encoding="utf-8"))
        assert d.get("lan_cuoi_leo_thang", {}) == {} and d.get("leo_thang_loi", {}) == {}
    loi = bc["topics"][0]["error"]
    assert "không tính suất tuần" in loi and "ModuleNotFoundError" in loi and "~/.ebm-venv/bin/python" in loi
