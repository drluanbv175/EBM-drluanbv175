#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28/09/2026 (đề xuất E1): `chu_trinh_chung_cu --ghi-log` để tác vụ lịch kiem-rut-bai-kho-thang có dấu vết
máy-đọc-được — dòng KẾT THÚC phải đọc được bằng CHÍNH hàm của cảm biến lịch nền (kiem_lich_nen._ket_thuc), và
mã thoát của chu trình không bị việc ghi log làm đổi. Ngoại tuyến.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import chu_trinh_chung_cu as ctcc  # noqa: E402
import kiem_lich_nen as kln  # noqa: E402


def test_dong_ket_thuc_doc_duoc_bang_cam_bien_lich_nen(tmp_path):
    tep = tmp_path / "state" / "kiem-rut-bai-kho.log"
    luc = dt.datetime(2026, 10, 4, 18, 30, 5)
    ctcc.ghi_dau_vet(tep, 1, luc)
    ctcc.ghi_dau_vet(tep, 0, luc + dt.timedelta(days=30))
    assert kln._ket_thuc(tep) == [luc, luc + dt.timedelta(days=30)]


def test_main_ghi_log_giu_nguyen_ma_thoat(tmp_path):
    tep = tmp_path / "log.txt"
    for rc in (0, 1, 2):
        with mock.patch.object(ctcc, "_chu_trinh", return_value=rc):
            assert ctcc.main(["--nhanh", "--ghi-log", str(tep)]) == rc
    assert [ln.rsplit("(mã ", 1)[1] for ln in tep.read_text(encoding="utf-8").splitlines()] == ["0)", "1)", "2)"]


def test_khong_ghi_log_khi_khong_khai(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with mock.patch.object(ctcc, "_chu_trinh", return_value=0):
        assert ctcc.main(["--nhanh"]) == 0
    assert list(tmp_path.iterdir()) == []


def test_so_khai_lich_nen_co_tac_vu_va_dau_vet_khop():
    so = json.loads((ROOT / "sync" / "lich-nen-ky-vong.json").read_text(encoding="utf-8"))
    tv = {t["id"]: t for t in so["tac_vu"]}["kiem-rut-bai-kho-thang"]
    assert tv["dau_vet"] == {"loai": "log-ket-thuc", "path": "state/kiem-rut-bai-kho.log"}
    skill = (ROOT / "sync" / "scheduled-tasks" / "kiem-rut-bai-kho-thang" / "SKILL.md").read_text(encoding="utf-8")
    assert "--ghi-log state/kiem-rut-bai-kho.log" in skill
    # Chạy được trên CẢ Mac lẫn Windows: SKILL không được chỉ có đường dẫn cứng của một máy.
    assert "OneDrive-Personal" in skill and "C:\\Users" in skill
