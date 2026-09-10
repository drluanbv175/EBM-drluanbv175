#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho kiem_hop_dong_item.py — trọng tâm cờ require_human_approval (10/09/2026).

Bối cảnh: I4 ("máy không được tự đặt APPROVED/APPLIED") vốn thi hành CỨNG,
không đọc `clinical_runtime/CLINICAL_RUNTIME_FLAGS.json.require_human_approval`
— nghĩa là cờ đó chỉ là lời hứa suông (họ lỗi "cờ nói dối" BH94/BH98/BH61).
Bản vá nối cờ vào I4 thật sự, MẶC ĐỊNH fail-closed khi thiếu/hỏng file cờ.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`): (1) kiểm HÀNH VI,
không đếm chuỗi; (2) mỗi ca gắn với rủi ro THẬT; (3) nhanh và ngoại tuyến.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_hop_dong_item as K  # noqa: E402

APPROVED_KHONG_NGUOI_DUYET = {
    "id": "EBM-TEST-0001",
    "topic": "t",
    "status": "APPROVED",
    "decision": "consider",
    "source": {"type": "SR-MA", "title": "x", "year": 2026, "pmid": "123", "resolved": True},
    "certainty": {"reported_by_source": True, "level": "mod"},
}


def test_self_test_van_dat_sau_khi_noi_co():
    """Cờ mặc định true trong repo → hành vi self-test KHÔNG đổi (0 regression)."""
    assert K._self_test() == 0


def test_mac_dinh_khong_truyen_co_van_bat_duoc_may_tu_duyet():
    """Gọi kiem() không truyền kwarg (đúng cách chot_hoi_quy_bai_hoc.py /
    thu_dau_cuoi_chung_cu.py / migrate_ledger.py đang gọi) vẫn phải bắt được
    APPROVED thiếu người duyệt — tương thích ngược tuyệt đối."""
    loi = K.kiem(APPROVED_KHONG_NGUOI_DUYET)
    assert any("I4" in l for l in loi)


def test_truyen_false_tuong_minh_thi_that_su_tat_duoc_i4():
    """Chứng minh cờ có TEO THẬT, không chỉ trang trí: require_human_approval=False
    (truyền tường minh, mô phỏng bác sĩ tự tắt) phải để APPROVED không người
    duyệt đi qua — nếu test này không bao giờ đỏ được bằng đột biến bỏ dòng
    `and doi_hoi_duyet`, thì cờ vẫn là trang trí."""
    loi = K.kiem(APPROVED_KHONG_NGUOI_DUYET, require_human_approval=False)
    assert not any("I4" in l for l in loi)


def test_truyen_true_tuong_minh_van_bat():
    loi = K.kiem(APPROVED_KHONG_NGUOI_DUYET, require_human_approval=True)
    assert any("I4" in l for l in loi)


def test_doc_co_that_tu_file_flags_that_cua_repo():
    """Không truyền kwarg (None) → đọc thẳng clinical_runtime/CLINICAL_RUNTIME_FLAGS.json
    thật của repo. File đó hiện khai true, nên phải bắt được — đây là bài kiểm
    tích hợp: nếu ai đó lỡ đổi cờ thành false trong repo mà không cố ý, test
    này đỏ sẽ là tín hiệu đầu tiên."""
    assert K._require_human_approval_flag() is True
    loi = K.kiem(APPROVED_KHONG_NGUOI_DUYET)
    assert any("I4" in l for l in loi)


def test_thieu_file_co_thi_fail_closed(tmp_path, monkeypatch):
    """Thiếu/hỏng file cờ → mặc định True (fail-closed) — một validator an
    toàn không được vì thiếu cấu hình mà nới lỏng luật."""
    duong_gia = tmp_path / "khong-ton-tai.json"
    monkeypatch.setattr(K, "_FLAGS_PATH", duong_gia)
    assert K._require_human_approval_flag() is True

    duong_hong = tmp_path / "hong.json"
    duong_hong.write_text("{khong phai json hop le", encoding="utf-8")
    monkeypatch.setattr(K, "_FLAGS_PATH", duong_hong)
    assert K._require_human_approval_flag() is True


def test_flags_gia_co_false_thi_mac_dinh_tat_that(tmp_path, monkeypatch):
    """Đối chứng: file cờ THẬT khai false thì đường mặc định (không truyền
    kwarg) cũng phải tắt I4 — chứng minh đường đọc-mặc-định và đường
    truyền-tường-minh dùng chung một sự thật, không lệch nhau."""
    duong_gia = tmp_path / "flags.json"
    duong_gia.write_text(
        json.dumps({"require_human_approval": False}), encoding="utf-8"
    )
    monkeypatch.setattr(K, "_FLAGS_PATH", duong_gia)
    loi = K.kiem(APPROVED_KHONG_NGUOI_DUYET)
    assert not any("I4" in l for l in loi)


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
