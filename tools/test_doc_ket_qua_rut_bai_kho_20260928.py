#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28/09/2026 (N4): gói tuần đọc KẾT QUẢ tái kiểm rút bài kho. Log dựng bằng CHÍNH hàm ghi của chu trình
(chu_trinh_chung_cu.ghi_dau_vet) để bên ghi và bên đọc không lệch khuôn. Ngoại tuyến."""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import chu_trinh_chung_cu as ctcc  # noqa: E402
import doc_ket_qua_rut_bai_kho as D  # noqa: E402

NAY = dt.datetime(2026, 10, 12, 20, 0, 0)


def _log(tmp_path: Path, *ma_theo_ngay: tuple[int, int]) -> Path:
    tep = tmp_path / "state" / "kiem-rut-bai-kho.log"
    for ngay_truoc, ma in ma_theo_ngay:
        ctcc.ghi_dau_vet(tep, ma, NAY - dt.timedelta(days=ngay_truoc))
    return tep


def test_chua_co_log_hoac_rong_la_chua_do_duoc(tmp_path):
    assert D.doc(tmp_path / "khong.log", NAY)["muc"] == "⚪"
    tep = tmp_path / "rong.log"
    tep.write_text("dòng khác\n", encoding="utf-8", newline="\n")
    kq = D.doc(tep, NAY)
    assert kq["muc"] == "⚪" and "KHÔNG coi là kho sạch" in kq["dong"]


def test_dong_cuoi_quyet_dinh(tmp_path):
    assert D.doc(_log(tmp_path / "a", (40, 0), (8, 1)), NAY)["muc"] == "🔴"
    kq = D.doc(_log(tmp_path / "b", (40, 1), (8, 0)), NAY)
    assert kq["muc"] == "🟢" and kq["ma"] == 0 and kq["tuoi_ngay"] == 8


def test_cu_qua_cua_so_ma_2_va_ma_la_la_chua_do_duoc(tmp_path):
    assert D.doc(_log(tmp_path / "a", (36, 0)), NAY)["muc"] == "⚪"
    assert D.doc(_log(tmp_path / "b", (36, 1)), NAY)["muc"] == "⚪"
    assert D.doc(_log(tmp_path / "c", (35, 0)), NAY)["muc"] == "🟢"
    assert D.doc(_log(tmp_path / "d", (1, 2)), NAY)["muc"] == "⚪"
    assert D.doc(_log(tmp_path / "e", (1, 130)), NAY)["muc"] == "⚪"


def test_main_ma_thoat(tmp_path, capsys):
    tep = _log(tmp_path, (1, 1))
    assert D.main(["--log", str(tep), "--tuoi-toi-da", "100000"]) == 1
    assert capsys.readouterr().out.startswith("🔴")
    assert D.main(["--log", str(tmp_path / "x.log")]) == 3


def test_skill_goi_tuan_goi_cong_cu_va_dat_do_len_dau():
    vb = (ROOT / "sync" / "scheduled-tasks" / "goi-duyet-tuan-ebm" / "SKILL.md").read_text(encoding="utf-8")
    assert "tools/doc_ket_qua_rut_bai_kho.py" in vb and "LÊN ĐẦU" in vb and "không viết «kho sạch»" in vb
