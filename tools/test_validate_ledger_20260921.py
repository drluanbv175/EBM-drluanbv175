#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_ledger V8 (21/09/2026, việc #2c): gradeLevel do MÁY gán phải được BÁO, không được sửa (BH10)."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ledger as vl  # noqa: E402

BASE = {"id": "E1", "decision": "consider", "gradeLevel": "high", "provenance": "from_engine",
        "certainty": "tier A · engine score CL=90 (máy chấm, không phải GRADE chính thức)",
        "verification_status": "đã xác minh", "source": {"pmid": "123"}}


class V8(unittest.TestCase):
    def test_the_engine_mang_high_bi_bao(self):
        kq = vl.cham([copy.deepcopy(BASE)])
        self.assertTrue(any(k.startswith("V8") for k in kq["bao_cao"]))
        self.assertFalse(kq["chan"], "chỉ BÁO CÁO, không chặn (dữ liệu hợp lệ về cấu trúc)")

    def test_khong_sua_du_lieu(self):
        the = [copy.deepcopy(BASE)]
        vl.cham(the)
        self.assertEqual(the[0]["gradeLevel"], "high", "BH10: công cụ tuyệt đối không ghi gradeLevel")

    def test_the_bac_si_duyet_high_khong_bi_bao(self):
        c = copy.deepcopy(BASE)
        c.update(provenance="from_doctor_master", certainty="RCT đa trung tâm")
        self.assertFalse([k for k in vl.cham([c])["bao_cao"] if k.startswith("V8")])

    def test_the_engine_da_ve_na_khong_bi_bao(self):
        c = copy.deepcopy(BASE)
        c["gradeLevel"] = "na"
        self.assertFalse([k for k in vl.cham([c])["bao_cao"] if k.startswith("V8")])

    def test_nhan_may_cham_bi_bao_du_provenance_khac(self):
        c = copy.deepcopy(BASE)
        c["provenance"] = "from_dashboard_master"
        self.assertTrue([k for k in vl.cham([c])["bao_cao"] if k.startswith("V8")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
