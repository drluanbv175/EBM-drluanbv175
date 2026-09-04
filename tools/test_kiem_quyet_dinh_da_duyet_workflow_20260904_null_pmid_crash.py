#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện MEDIUM-HIGH của Workflow đối kháng đa-agent 2026-09-04
(vòng 2, task #69): `tools/kiem_quyet_dinh_da_duyet.py::kiem()` — bản ghi
trong sổ `quyet-dinh-da-duyet.json` khai TƯỜNG MINH `item: null, pmid: null`
làm cả chốt CRASH, giết chết luôn việc kiểm mọi bản ghi khác trong cùng sổ.

CƠ CHẾ LỖI (xác nhận bằng thực nghiệm TRƯỚC khi vá):
`qd.get('pmid', '?')` chỉ trả về `'?'` khi key `pmid` THIẾU HẲN — không áp
dụng khi `pmid` được khai tường minh là `null` (Python `None`) trong JSON
(giống hệt lớp lỗi đã vá trước đó ở `clinical_output_validator.py` trong
cùng marathon này). Dòng gốc:
    nhan = f"{ten} · {qd.get('item') or 'PMID ' + qd.get('pmid', '?')}"
Với `qd = {'item': None, 'pmid': None}`: `qd.get('item')` → `None` (falsy)
→ Python đánh giá vế phải `'PMID ' + qd.get('pmid', '?')` → `'PMID ' + None`
→ `TypeError: can only concatenate str (not "NoneType") to str`. Lỗi này
KHÔNG có try/except nào bọc quanh trước bản vá, văng thẳng ra ngoài
`kiem()`/`main()` — giết chết chốt cho MỌI bản ghi khác trong sổ, không
chỉ báo "⚪ không kiểm được" cho riêng bản ghi hỏng.

BẢN VÁ (hai lớp, cả hai đều cần cho ca thật):
1. Tính `nhan` an toàn với `None` — không còn phép cộng chuỗi trực tiếp
   với giá trị có thể là `None`.
2. Bọc TOÀN BỘ xử lý một bản ghi (không chỉ phần tính `nhan`) trong
   `try/except Exception` — một bản ghi hỏng theo BẤT KỲ kiểu nào khác
   (thiếu trường `ky_vong`, kiểu dữ liệu sai…) cũng chỉ được báo "⚪ không
   kiểm được" cho RIÊNG bản ghi đó, các bản ghi khác trong cùng sổ vẫn
   được xử lý bình thường — đúng chủ đích BAN ĐẦU của chốt này (tách "không
   biết" khỏi "có vấn đề", BH08) mà bug cũ đã vi phạm ngay trong chính cơ
   chế được thiết kế để giữ nguyên tắc đó.

Nguyên tắc viết test: monkeypatch `kqd._nap_vd` (không tạo file thật ở
đường dẫn tuyệt đối `EBM-Dashboards/tools/verify_dashboard.py` mà module
tự suy từ `Path(__file__).resolve().parents[1]` — tham số `dash_dir`
truyền vào `kiem()` KHÔNG kiểm soát việc `_nap_vd()` tìm module ở đâu),
gọi THẲNG hàm nguồn `kiem()`, không grep chuỗi trong mã nguồn.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_quyet_dinh_da_duyet as kqd  # noqa: E402


class _FakeVD:
    """Mô phỏng tối giản `EBM-Dashboards/tools/verify_dashboard.py` — nội
    dung file thật KHÔNG quan trọng vì các hàm này đều bị fake, chỉ cần
    file tồn tại (kiem() có kiểm `f.exists()` trước khi đọc)."""

    @staticmethod
    def extract_data_block(text: str) -> str:
        return "DATA"

    @staticmethod
    def split_items(blk: str):
        return [
            {"id": "ITEM-01", "decision": "apply"},
            {"id": "ITEM-02", "decision": "consider"},
        ]

    @staticmethod
    def field(item: dict, key: str):
        return item.get(key)


def _dung_so(tmp_path: Path, quyet_dinh: list[dict]) -> tuple[Path, Path]:
    """Dựng một sổ + thư mục dashboard tối giản dưới tmp_path; trả (so_path, dash_dir)."""
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    for ten_file in {qd.get("file") for qd in quyet_dinh if qd.get("file")}:
        (dash / ten_file).write_text("<html></html>", encoding="utf-8")
    so_path = tmp_path / "quyet-dinh-da-duyet.json"
    so_path.write_text(json.dumps({"quyet_dinh": quyet_dinh}, ensure_ascii=False), encoding="utf-8")
    return so_path, dash


class TestNullItemVaPmidKhongLamCrash:
    """★★ Ca chính — bản ghi khai TƯỜNG MINH item=None, pmid=None (đúng hình
    dạng lỗi thật) không được làm `kiem()` ném exception; phải báo "⚪ không
    kiểm được" với thông điệp nêu rõ lý do, không phải văng ra ngoài."""

    def test_khong_nem_exception(self, monkeypatch, tmp_path):
        monkeypatch.setattr(kqd, "_nap_vd", lambda: _FakeVD())
        so_path, dash = _dung_so(tmp_path, [
            {"file": "a.html", "item": None, "pmid": None,
             "ky_vong": {"decision": "apply"}, "duyet": "2026-09-04", "ly_do": "test null"},
        ])
        # Không được ném TypeError — nếu bug tái phát, dòng dưới sẽ tự nổ.
        khop, lech, mu = kqd.kiem(so_path, dash)
        assert khop == []
        assert lech == []
        assert len(mu) == 1
        assert "thiếu cả item lẫn pmid" in mu[0]

    def test_pmid_null_rieng_khong_nem_exception(self, monkeypatch, tmp_path):
        """Đối chứng — chỉ `pmid` null (item hoàn toàn thiếu key, không phải
        None) cũng phải an toàn, đúng đường mã cũ `qd.get('pmid', '?')`."""
        monkeypatch.setattr(kqd, "_nap_vd", lambda: _FakeVD())
        so_path, dash = _dung_so(tmp_path, [
            {"file": "a.html", "pmid": None,
             "ky_vong": {"decision": "apply"}, "duyet": "2026-09-04", "ly_do": "test pmid null"},
        ])
        khop, lech, mu = kqd.kiem(so_path, dash)
        assert lech == []
        assert len(mu) == 1


class TestBanGhiBinhThuongVanXuLyDungNhuCu:
    """Đối chứng bắt buộc — bản ghi có `item`/`pmid` hợp lệ vẫn phải khớp/lệch
    đúng như hành vi trước bản vá (bản vá không được đổi logic so sánh)."""

    def test_item_khop_ky_vong_vao_khop(self, monkeypatch, tmp_path):
        monkeypatch.setattr(kqd, "_nap_vd", lambda: _FakeVD())
        so_path, dash = _dung_so(tmp_path, [
            {"file": "b.html", "item": "ITEM-01", "pmid": None,
             "ky_vong": {"decision": "apply"}, "duyet": "2026-09-04", "ly_do": "khop"},
        ])
        khop, lech, mu = kqd.kiem(so_path, dash)
        assert khop == ["b.html · ITEM-01"]
        assert lech == mu == []

    def test_item_lech_ky_vong_vao_lech(self, monkeypatch, tmp_path):
        monkeypatch.setattr(kqd, "_nap_vd", lambda: _FakeVD())
        so_path, dash = _dung_so(tmp_path, [
            {"file": "d.html", "item": "ITEM-02", "pmid": None,
             "ky_vong": {"decision": "apply"}, "duyet": "2026-09-04", "ly_do": "lech"},
        ])
        khop, lech, mu = kqd.kiem(so_path, dash)
        assert khop == []
        assert len(lech) == 1
        assert "decision='consider' ≠ đã duyệt 'apply'" in lech[0]


class TestMotBanGhiHongKhongGietCacBanGhiKhac:
    """★★ Ca chính thứ hai — MỘT bản ghi hỏng (kể cả kiểu hỏng KHÁC null
    item/pmid, ví dụ thiếu hẳn trường `ky_vong`) không được ngăn các bản ghi
    còn lại trong CÙNG sổ được xử lý đúng. Đây là mục tiêu ban đầu của lớp
    try/except ngoài, tách biệt khỏi việc null-safe hoá riêng `nhan`."""

    def test_ban_ghi_thieu_ky_vong_bi_co_lap_cac_ban_khac_van_dung(self, monkeypatch, tmp_path):
        monkeypatch.setattr(kqd, "_nap_vd", lambda: _FakeVD())
        so_path, dash = _dung_so(tmp_path, [
            {"file": "a.html", "item": None, "pmid": None,
             "ky_vong": {"decision": "apply"}, "duyet": "2026-09-04", "ly_do": "null"},
            {"file": "b.html", "item": "ITEM-01", "pmid": None,
             "ky_vong": {"decision": "apply"}, "duyet": "2026-09-04", "ly_do": "khop"},
            # Bản ghi hỏng KIỂU KHÁC: có item hợp lệ nhưng THIẾU hẳn "ky_vong"
            # — trước bản vá, KeyError ở đây (nếu vượt qua được lỗi null ở
            # bản ghi "a.html" phía trên) cũng sẽ giết cả lượt.
            {"file": "c.html", "item": "ITEM-01", "pmid": None,
             "duyet": "2026-09-04", "ly_do": "thieu ky_vong"},
            {"file": "d.html", "item": "ITEM-02", "pmid": None,
             "ky_vong": {"decision": "apply"}, "duyet": "2026-09-04", "ly_do": "lech"},
        ])
        khop, lech, mu = kqd.kiem(so_path, dash)
        # b.html (record 2) và d.html (record 4) phải được xử lý bình thường
        # dù đứng xen giữa hai bản ghi hỏng (record 1 và 3).
        assert khop == ["b.html · ITEM-01"]
        assert len(lech) == 1 and "d.html · ITEM-02" in lech[0]
        # Cả hai bản ghi hỏng đều rơi vào "không kiểm được", không có exception nào thoát ra.
        assert len(mu) == 2
        assert any("thiếu cả item lẫn pmid" in m for m in mu)
        assert any("c.html" in m and "không đọc được" in m for m in mu)
