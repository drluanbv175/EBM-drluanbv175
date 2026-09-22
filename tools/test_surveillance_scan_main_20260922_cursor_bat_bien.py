"""Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #7, MEDIUM).

`main()` trước đây gọi `ghi_cursor(cursor)` VÔ ĐIỀU KIỆN mỗi khi không có `--khong-cursor`,
kể cả khi TOÀN BỘ chủ đề trong lượt quét FAIL (nội dung con trỏ không đổi). Hệ quả:
`.quet-cursor.json` vẫn bị ghi lại (mtime đổi), và `sources_health.lay_thanh_cong_that()`
đọc mtime đó thành "lượt quét THÀNH CÔNG hôm nay" — sai, vì không có gì thành công.

Sửa: chỉ ghi khi `cursor != con_tro_truoc` (nội dung THẬT SỰ đổi, tức có ≥1 chủ đề PASS).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_main_cursor_test", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_main_cursor_test"] = S
_sp.loader.exec_module(S)


@pytest.fixture()
def _kho_tam(monkeypatch, tmp_path):
    """Chuyển DEFAULT_WATCHLIST sang thư mục tạm — _cursor_path()/_khoa_path() đều suy từ
    DEFAULT_WATCHLIST.parent, nên test không bao giờ chạm .quet-cursor.json THẬT."""
    wl = tmp_path / "watchlist.json"
    wl.write_text(json.dumps({"topics": [{"topic": "A", "query": "qa", "active": True}]}),
                   encoding="utf-8")
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", wl)
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    yield tmp_path, wl


def _duong_con_tro(tmp_path: Path) -> Path:
    return tmp_path / ".quet-cursor.json"


def test_ca_kho_toan_bo_khong_ghi_cursor(_kho_tam, monkeypatch, capsys):
    tmp_path, wl = _kho_tam

    def search_hong(query, days, retmax, **kw):
        raise RuntimeError("NCBI + Europe PMC đều hỏng")

    monkeypatch.setattr(S, "search", search_hong)

    rc = S.main(["--watchlist", str(wl), "--days", "30", "--max", "5"])
    assert rc != 0  # FAIL/PARTIAL — không xanh giả
    assert not _duong_con_tro(tmp_path).exists(), (
        "mọi chủ đề FAIL, nội dung con trỏ không đổi ⇒ KHÔNG được tạo/ghi lại file con trỏ"
    )


def test_chu_de_pass_van_ghi_cursor_binh_thuong(_kho_tam, monkeypatch):
    tmp_path, wl = _kho_tam

    def search_ok(query, days, retmax, **kw):
        return ["111"]

    def summarize_ok(ids):
        return [S.Candidate(i, "2026-09-20", f"Bài {i}", "") for i in ids]

    monkeypatch.setattr(S, "search", search_ok)
    monkeypatch.setattr(S, "summarize", summarize_ok)

    rc = S.main(["--watchlist", str(wl), "--days", "30", "--max", "5"])
    assert rc == 0
    cp = _duong_con_tro(tmp_path)
    assert cp.exists()
    du = json.loads(cp.read_text(encoding="utf-8"))
    assert "A" in du


def test_lan_hong_sau_lan_pass_khong_ghi_de_lam_mat_gia_tri_da_co(_kho_tam, monkeypatch):
    """Đối chứng quan trọng nhất: một chủ đề ĐÃ có con trỏ từ trước (lượt PASS cũ), lượt
    sau FAIL toàn bộ — file con trỏ (và giá trị bên trong) phải giữ NGUYÊN, không bị ghi lại
    dù nội dung không đổi (tránh mtime nhảy vô ích và tránh hiểu lầm đã «có lượt chạy mới»)."""
    tmp_path, wl = _kho_tam
    cp = _duong_con_tro(tmp_path)
    cp.write_text(json.dumps({"A": "2026-09-01"}), encoding="utf-8")
    mtime_truoc = cp.stat().st_mtime
    time.sleep(0.05)

    def search_hong(query, days, retmax, **kw):
        raise RuntimeError("hỏng")

    monkeypatch.setattr(S, "search", search_hong)

    rc = S.main(["--watchlist", str(wl), "--days", "30", "--max", "5"])
    assert rc != 0
    assert json.loads(cp.read_text(encoding="utf-8")) == {"A": "2026-09-01"}
    assert cp.stat().st_mtime == mtime_truoc, "file KHÔNG được ghi lại khi nội dung không đổi"
