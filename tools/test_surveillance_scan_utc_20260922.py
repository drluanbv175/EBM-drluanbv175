"""Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #11, LOW).

Con trỏ (`cursor[topic]`) và mốc `mindate` tính lại từ con trỏ trước đây dùng `date.today()`
(GIỜ MÁY) trong khi biên `since`/`today` thật sự gửi cho NCBI/Europe PMC luôn tính bằng
`datetime.now(timezone.utc)` — lệch 1 ngày ở Việt Nam (UTC+7) trong khoảng 00:00-07:00 giờ địa
phương. Nay cả hai đều dùng UTC nhất quán.
"""
from __future__ import annotations

import datetime as _real_dt
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_utc_test", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_utc_test"] = S
_sp.loader.exec_module(S)


class _DatetimeCoDinh(_real_dt.datetime):
    """Luôn trả một mốc UTC CỐ ĐỊNH cho .now(tz) bất kể tz — để phép kiểm không phụ thuộc đồng
    hồ máy thật (chống test không ổn định — flaky theo giờ chạy)."""

    _MOC = _real_dt.datetime(2026, 9, 22, 3, 0, 0)  # 03:00 UTC — 10:00 giờ Việt Nam cùng ngày

    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return cls._MOC.replace(tzinfo=tz)
        return cls._MOC  # nhánh "naive" không được dùng nữa ở các chỗ đã vá — nếu code cũ còn sót
        # sẽ vẫn ra cùng giá trị NGÀY ở đây (không giúp phát hiện hồi quy bằng cách này, xem test dưới)


def test_cursor_pass_dung_datetime_now_utc(monkeypatch):
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    # 22/09/2026: chặn nốt hai làn mới — có thể gọi mạng thật/tốn hạn mức tháng nếu máy
    # chạy test đã bật ENABLE_CORE/ENABLE_CONSENSUS/ENABLE_SERPAPI_SCHOLAR thật.
    monkeypatch.setattr(S, "search_core_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda *a, **k: ([], ""))
    monkeypatch.setattr(S, "datetime", _DatetimeCoDinh)
    cursor = {}
    rep = S.run_scan([{"topic": "A", "query": "q"}], days=30, max_results=5, cursor=cursor,
                     search_fn=lambda *a, **k: [], summarize_fn=lambda ids: [])
    assert rep["topics"][0]["status"] == "PASS"
    assert cursor["A"] == "2026-09-22", "cursor phải khớp ĐÚNG datetime.now(timezone.utc).date()"


def test_mindate_tinh_lai_tu_cursor_dung_utc(monkeypatch):
    """Cursor cũ đã có (lùi xa) — mindate tính lại từ max(cu-3, today_utc-days) phải neo theo
    today_utc, không phải giờ máy thật (test độc lập với đồng hồ hệ thống)."""
    monkeypatch.setattr(S, "search_preprint_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_trials_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "search_scopus_lane", lambda *a, **k: [])
    # 22/09/2026: chặn nốt hai làn mới — có thể gọi mạng thật/tốn hạn mức tháng nếu máy
    # chạy test đã bật ENABLE_CORE/ENABLE_CONSENSUS/ENABLE_SERPAPI_SCHOLAR thật.
    monkeypatch.setattr(S, "search_core_lane", lambda *a, **k: [])
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda *a, **k: ([], ""))
    monkeypatch.setattr(S, "datetime", _DatetimeCoDinh)
    thay: list[str] = []

    def search_gia(query, days, retmax, **kw):
        thay.append(kw.get("mindate", ""))
        return []

    cursor = {"A": "2025-01-01"}  # rất cũ ⇒ nhánh today_utc-days (30 ngày) sẽ thắng trong max()
    S.run_scan([{"topic": "A", "query": "q"}], days=30, max_results=5, cursor=cursor,
              search_fn=search_gia, summarize_fn=lambda ids: [])
    # today_utc = 2026-09-22, days=30 ⇒ mindate mong đợi = 2026-08-23 (UTC), khớp "%Y/%m/%d"
    ky_vong = (_real_dt.date(2026, 9, 22) - _real_dt.timedelta(days=30)).strftime("%Y/%m/%d")
    assert thay and thay[0] == ky_vong
