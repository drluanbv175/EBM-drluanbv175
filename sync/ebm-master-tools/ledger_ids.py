# -*- coding: utf-8 -*-
"""ledger_ids.py — Tiện ích SINH & KIỂM id thẻ chứng cứ cho sổ cái EBM_MASTER.

ID có dạng 'EVID-<năm>-<seq 4 chữ số>'. Trước đây các writer (ingest_dashboard.py,
bridge_master_ledger.py) lấy gốc seq = len(cards) → KHÔNG đơn điệu toàn cục: khi sổ cái có
thẻ bị xóa/thêm xen kẽ hoặc trải nhiều năm, len(cards) ≠ số thứ tự lớn nhất đang dùng → sinh
TRÙNG id (lỗi đã gặp: EVID-2026-0159/0160/0164 mỗi cái xuất hiện 2 lần, làm selftest_loop.py FAIL).

max_seq() quét MỌI id hiện có và lấy số đuôi lớn nhất → seq kế tiếp luôn duy nhất toàn sổ cái,
bất kể năm hay khoảng trống. assert_unique() là cổng bất biến "khóa chống trùng".
"""
import re

_ID_RE = re.compile(r"EVID-\d{4}-(\d+)\s*$")


def max_seq(cards):
    """Số thứ tự (đuôi) lớn nhất trong mọi id 'EVID-YYYY-NNNN'; 0 nếu chưa có thẻ nào."""
    m = 0
    for c in cards or []:
        mt = _ID_RE.search(str(c.get("id", "")))
        if mt:
            m = max(m, int(mt.group(1)))
    return m


def max_ledger_seq(data):
    """Số đuôi ID lớn nhất trên TOÀN sổ cái, kể cả thẻ đang cách ly.

    ``quarantined_cards`` vẫn mang định danh đã cấp; bỏ chúng khỏi phép tính sẽ tái sử
    dụng ID và gây xung đột khi thẻ được khôi phục về hàng bác sĩ duyệt.
    """
    if not isinstance(data, dict):
        return 0
    return max_seq((data.get("evidence_cards") or []) + (data.get("quarantined_cards") or []))


def make_id(year, seq):
    """Dựng id 'EVID-<năm>-<seq>' (seq 4 chữ số)."""
    return "EVID-%s-%04d" % (str(year or "0000")[:4], seq)


def assert_unique(cards):
    """Chặn trùng id — bất biến KHÓA CHỐNG TRÙNG của sổ cái. Báo rõ id nào trùng."""
    ids = [c.get("id") for c in cards or []]
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise AssertionError("Trùng id sổ cái — vi phạm khóa chống trùng: %s" % dup)
