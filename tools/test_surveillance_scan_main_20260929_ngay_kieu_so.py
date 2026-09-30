"""Vá 29/09/2026 — lượt quét tuần W40 SẬP ở bước đo độ trễ (K4).

Một ứng viên có `publication_date` kiểu int (chỉ có NĂM) ⇒ `int[:11]` ném TypeError. Lỗi nổ
SAU khi con trỏ đã tiến và TRƯỚC khi ghi báo cáo JSON ⇒ 12 phút quét mất trắng, con trỏ nhảy
tới hôm nay mà không ai thấy ứng viên nào (đúng kiểu «suy giảm im lặng» mà con trỏ phải tránh).

Sửa 29/09: ép về chuỗi ở nơi đo độ trễ — ngày không đọc được là «không đo được», không sập. Hoàn thiện 30/09: ép
chuỗi ngay tại `Candidate.__post_init__` (gốc rễ) và dời việc ghi con trỏ xuống sau khi báo cáo tới nơi — xem
`test_surveillance_scan_main_20260930_con_tro_sau_bao_cao.py`.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_main_ngay_so_test", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_main_ngay_so_test"] = S
_sp.loader.exec_module(S)


@pytest.fixture()
def _kho_tam(monkeypatch, tmp_path):
    """Watchlist + con trỏ + khoá đều nằm ở thư mục tạm; mọi làn mạng bị chặn."""
    wl = tmp_path / "watchlist.json"
    wl.write_text(json.dumps({"topics": [{"topic": "A", "query": "qa", "active": True}]}),
                  encoding="utf-8")
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", wl)
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_core_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda *a, **k: ([], ""))
    # 30/09/2026: chặn nốt chuỗi kiểm rút bài + đối chiếu kho — ở cây có engine, PMID 111/222 từng gọi mạng thật.
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda ds: list(ds))
    monkeypatch.setattr(S, "_pmid_da_co_trong_kho", lambda: set())
    monkeypatch.setattr(S, "search", lambda query, days, retmax, **kw: ["111", "222"])
    yield tmp_path, wl


def test_ngay_cong_bo_kieu_so_khong_lam_sap_luot_quet(_kho_tam, monkeypatch):
    tmp_path, wl = _kho_tam

    def summarize(ids):
        # "111": ngày kiểu int (thủ phạm thật W40) · "222": ngày chuẩn đo được
        return [S.Candidate("111", 2026, "Bài năm-số", ""),
                S.Candidate("222", "2026 Sep 20", "Bài ngày-chuẩn", "")]

    monkeypatch.setattr(S, "summarize", summarize)
    out = tmp_path / "bao-cao.json"
    rc = S.main(["--watchlist", str(wl), "--days", "30", "--max", "5",
                 "--json-report", str(out)])
    assert rc == 0
    assert out.exists(), "báo cáo JSON PHẢI được ghi — trước bản vá lượt quét sập trước bước này"
    bc = json.loads(out.read_text(encoding="utf-8"))
    # ứng viên ngày chuẩn vẫn được đo; ứng viên ngày-số chỉ bị bỏ khỏi phép đo, không mất khỏi báo cáo
    assert bc["do_tre"]["n_do_duoc"] == 1
    assert {c["pmid"] for t in bc["topics"] for c in t["candidates"]} >= {"111", "222"}
