# -*- coding: utf-8 -*-
"""Bước TV ③ (20/10/2026): phiếu làn trình duyệt trả mã 1 = «còn bài chờ bác sĩ» — KHÔNG phải lỗi hạ tầng.

Lượt quét 7 chủ đề cũ ngày 20/10/2026: mọi chủ đề có bài thiếu toàn văn đều nhận «⚠ 1 công cụ con lỗi hạ tầng/quá giờ — số
liệu có thể thiếu» chỉ vì `doc_toan_van_co_nguoi.py` trả 1 (đúng hợp đồng: «0 hết việc · 1 còn bài chờ · 2 KHÔNG ĐO ĐƯỢC»).
Đỏ giả làm bác sĩ tưởng mạng hỏng và chạy lại vô ích. Ngoại tuyến: công cụ con là hàm giả.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


tv = _nap("tools/toan_van_theo_chu_de.py", "_tv_b3_1020")
op = _nap("ops/orchestrator.py", "_op_b3_1020")


def _chay(ma_phieu: int):
    def chay(lenh):
        if "doc_toan_van_co_nguoi.py" in lenh[1]:
            return ma_phieu, "Phiếu: 1 bài cần làn trình duyệt có bác sĩ"
        return 0, "ok"
    return chay


def _tv(tmp_path, ma_phieu):
    kho = tmp_path / "EBM-Dashboards" / "toan_van_oa"
    kho.mkdir(parents=True)
    a2 = tmp_path / "RID.A2-x.json"
    a2.write_text(json.dumps({"topics": [{"candidates": [{"pmid": "123456"}]}]}), encoding="utf-8")
    bc = tmp_path / "RID.TV-x.md"
    assert tv.main(["--a2-json", str(a2), "--bao-cao", str(bc)], chay=_chay(ma_phieu), kho=kho) == 0
    return bc


def test_ma_1_con_bai_cho_khong_thanh_canh_bao(tmp_path, capsys):
    bc = _tv(tmp_path, 1)
    assert not [d for d in capsys.readouterr().out.splitlines() if d.startswith("⚠ ")]
    assert not [d for d in bc.read_text(encoding="utf-8").splitlines() if d.startswith("⚠ ")]
    viec = op.viec_toan_van({"tv_bao_cao": [str(bc)]})
    assert viec and "1 bài còn thiếu toàn văn" in viec[0] and "lỗi hạ tầng" not in viec[0]


@pytest.mark.parametrize("ma", [2, -9, 3])
def test_ma_khac_van_la_canh_bao(tmp_path, capsys, ma):
    bc = _tv(tmp_path, ma)
    assert any(d.startswith("⚠ ③ Phiếu làn trình duyệt") for d in bc.read_text(encoding="utf-8").splitlines())
    viec = op.viec_toan_van({"tv_bao_cao": [str(bc)]})
    assert "lỗi hạ tầng" in viec[0]


def test_hang_so_khop_hop_dong_cong_cu_con():
    doc = (REPO / "tools" / "doc_toan_van_co_nguoi.py").read_text(encoding="utf-8")
    assert "Mã thoát: phiếu 0 hết việc · 1 còn bài" in doc and tv.MA_PHIEU_CON_BAI_CHO == 1
