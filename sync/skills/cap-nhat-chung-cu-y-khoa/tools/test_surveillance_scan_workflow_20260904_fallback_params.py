#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Hồi quy phát hiện HIGH của audit đối kháng 2026-09-04: `search()` trong
surveillance_scan.py rơi vào Europe PMC khi PubMed E-utilities lỗi
(`except RuntimeError: return search_europe_pmc(query, days, retmax)`), nhưng BỎ
MẤT ba tham số caller vừa truyền vào `search()`: `mindate`, `maxdate`, `loc_thiet_ke`.

Hai hậu quả thật, cả hai đã có bằng chứng bằng lời trong chính comment của file:
  (1) CON TRỎ TĂNG DẦN (K8) — `run_scan()` tính `mindate` là cửa sổ NGÀY HẸP mà
      cursor đang quét tới (lùi 3 ngày để chống hở khe). Bỏ `mindate`/`maxdate` ở
      fallback khiến Europe PMC quay về cửa sổ RỘNG "days lùi từ hôm nay" — ứng
      viên ĐÃ duyệt ở lượt quét trước tái xuất vào hàng chờ mỗi khi PubMed lỗi.
  (2) Tầng "moi_vao_pubmed" cố ý `loc_thiet_ke=False` (KHÔNG lọc publication type)
      — chính comment ở `search()` gọi đây là "đúng cái bẫy đang vá" (BH38: lọc
      publication type vứt mất bài MỚI chưa kịp gán loại). Bỏ `loc_thiet_ke` ở
      fallback khiến Europe PMC ÂM THẦM lọc lại, tái diễn đúng lỗi BH38 — chỉ
      khác nguyên nhân kích hoạt (PubMed lỗi, thay vì quên tham số).

Nguyên tắc viết test: gọi THẬT `search()`/`search_europe_pmc()`, đọc query đã dựng
qua `fetch_json` bị mock — không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import surveillance_scan as ss  # noqa: E402


def _query_of(url: str) -> str:
    return urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["query"][0]


class TestSearchFallbackForwardsParams:
    """★★ Ca chính: search() rơi vào RuntimeError phải chuyển ĐÚNG mindate/
    maxdate/loc_thiet_ke cho search_europe_pmc(), không dùng bộ mặc định."""

    def test_mindate_maxdate_loc_thiet_ke_duoc_chuyen_tiep(self):
        goi = {}

        def fake_ep(query, days, retmax, **kwargs):
            goi.update(kwargs)
            goi["query"] = query
            goi["days"] = days
            goi["retmax"] = retmax
            return ["1"]

        original = ss.search_europe_pmc
        ss.search_europe_pmc = fake_ep
        try:
            ids = ss.search(
                "type 2 diabetes", 90, 20,
                fetch_json=lambda _u: (_ for _ in ()).throw(RuntimeError("NCBI lỗi")),
                loc_thiet_ke=False, mindate="2026/08/01", maxdate="2026/08/31",
            )
        finally:
            ss.search_europe_pmc = original

        assert ids == ["1"]
        assert goi["query"] == "type 2 diabetes"
        assert goi["days"] == 90
        assert goi["retmax"] == 20
        assert goi["loc_thiet_ke"] is False
        assert goi["mindate"] == "2026/08/01"
        assert goi["maxdate"] == "2026/08/31"

    def test_mac_dinh_loc_thiet_ke_true_khong_co_mindate_van_chuyen_tiep_dung(self):
        """Đối chứng: tầng mặc định (loc_thiet_ke=True, không cursor) cũng phải
        chuyển tiếp ĐÚNG giá trị (True/rỗng), không phải chỉ tầng đặc biệt."""
        goi = {}

        def fake_ep(query, days, retmax, **kwargs):
            goi.update(kwargs)
            return []

        original = ss.search_europe_pmc
        ss.search_europe_pmc = fake_ep
        try:
            ss.search(
                "hypertension", 30, 10,
                fetch_json=lambda _u: (_ for _ in ()).throw(RuntimeError("boom")),
            )
        finally:
            ss.search_europe_pmc = original

        assert goi["loc_thiet_ke"] is True
        assert goi["mindate"] == ""
        assert goi["maxdate"] == ""


class TestSearchEuropePmcQueryConstruction:
    """Kiểm search_europe_pmc() TỰ DỰNG đúng query theo tham số mới — độc lập với
    search(), để bắt được lỗi ngay cả khi ai đó gọi thẳng hàm này (không qua fallback)."""

    def test_mindate_maxdate_dung_cua_so_hep_khong_phai_days(self):
        captured = {}

        def fake_json(url):
            captured["url"] = url
            return {"resultList": {"result": []}}

        # days=90 SẼ cho cửa sổ rất khác nếu bị lờ đi — mindate/maxdate phải THẮNG.
        ss.search_europe_pmc("diabetes", 90, 20, fetch_json=fake_json,
                             mindate="2026/08/01", maxdate="2026/08/31")
        q = _query_of(captured["url"])
        assert "FIRST_PDATE:[2026-08-01 TO 2026-08-31]" in q
        assert "2026-06" not in q  # cửa sổ 90-ngày-lùi (sai) không được xuất hiện

    def test_khong_co_mindate_thi_lui_ve_cua_so_days_nhu_cu(self):
        """Regression: hành vi CŨ (không mindate → days-lùi-từ-hôm-nay) phải còn nguyên."""
        captured = {}

        def fake_json(url):
            captured["url"] = url
            return {"resultList": {"result": []}}

        ss.search_europe_pmc("diabetes", 30, 20, fetch_json=fake_json)
        q = _query_of(captured["url"])
        assert "FIRST_PDATE:[" in q
        assert "PUB_TYPE:" in q  # loc_thiet_ke mặc định True — vẫn lọc như cũ

    def test_maxdate_sentinel_3000_doi_thanh_hom_nay(self):
        """search() dùng "3000" làm sentinel 'không trần trên' (khuôn PubMed) —
        Europe PMC không hiểu sentinel này, phải đổi thành ngày hôm nay."""
        captured = {}

        def fake_json(url):
            captured["url"] = url
            return {"resultList": {"result": []}}

        ss.search_europe_pmc("diabetes", 30, 20, fetch_json=fake_json,
                             mindate="2026/08/01", maxdate="3000")
        q = _query_of(captured["url"])
        assert "TO 3000" not in q
        assert "3000-" not in q

    def test_loc_thiet_ke_false_khong_loc_publication_type(self):
        """★★ Đúng kịch bản tầng "moi_vao_pubmed" — KHÔNG được lọc PUB_TYPE, nếu
        không tái diễn BH38 (bài mới chưa kịp gán loại bị vứt)."""
        captured = {}

        def fake_json(url):
            captured["url"] = url
            return {"resultList": {"result": []}}

        ss.search_europe_pmc("diabetes", 30, 20, fetch_json=fake_json, loc_thiet_ke=False)
        q = _query_of(captured["url"])
        assert "PUB_TYPE:" not in q
        assert "SRC:MED" in q  # phần ràng buộc nguồn khác vẫn phải còn nguyên

    def test_loc_thiet_ke_true_van_loc_nhu_cu(self):
        """Đối chứng bắt buộc: loc_thiet_ke=True (mặc định) vẫn phải lọc như trước
        bản vá — không được vô tình tắt bộ lọc cho MỌI lượt gọi."""
        captured = {}

        def fake_json(url):
            captured["url"] = url
            return {"resultList": {"result": []}}

        ss.search_europe_pmc("diabetes", 30, 20, fetch_json=fake_json, loc_thiet_ke=True)
        q = _query_of(captured["url"])
        assert 'PUB_TYPE:"guideline"' in q
        assert 'PUB_TYPE:"randomized controlled trial"' in q


class TestRunScanCallingConventionStillWorks:
    """search_fn trong run_scan() gọi search_fn(query, days, max_results, datetype=...,
    loc_thiet_ke=..., mindate=...) rồi bắt TypeError để lùi về chữ ký cũ khi cần
    (bộ tìm giả trong test không nhận tham số phụ). Xác nhận search() thật vẫn
    tương thích với CẢ HAI cách gọi sau bản vá."""

    def test_goi_voi_du_tham_so_phu_khong_loi(self):
        ids = ss.search(
            "x", 30, 5,
            fetch_json=lambda _u: {"esearchresult": {"idlist": ["1", "2"]}},
            datetype="edat", loc_thiet_ke=False, mindate="",
        )
        assert ids == ["1", "2"]

    def test_goi_voi_chu_ky_cu_ba_tham_so_khong_loi(self):
        ids = ss.search("x", 30, 5,
                        fetch_json=lambda _u: {"esearchresult": {"idlist": ["3"]}})
        assert ids == ["3"]


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
