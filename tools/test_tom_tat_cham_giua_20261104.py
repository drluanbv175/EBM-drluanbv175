"""Chấm giữa « · » phân cách trong chữ bản tóm tắt KHÔNG phải dấu thập phân — 04/11/2026.

Bản vá 28/10 (#274) ghép «11 ·1», «2·⏎12» của văn bản PDF thành số thập phân. Hàm dùng chung cho cả hai phía nên chữ của bản
tóm tắt «≥60 · 45–<60» (PMID 39490700) thành 60.45 và dãy số đếm «34 · 3 · 9 · 3 · 1» (PMID 41033330) thành 34.3, 9.3 ⇒ cổng
chặn số ĐÚNG. Phía bản tóm tắt: chấm giữa có khoảng trắng hai bên là phân cách; phía bài giữ nguyên cách ghép cũ.
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import tom_tat_chung_cu_word as T  # noqa: E402
from test_tom_tat_chung_cu_word_20261019 import NGU_CANH, TRANG, _hop_le  # noqa: E402


def test_phan_cach_danh_sach_khong_thanh_thap_phan():
    assert T.cac_so_tom_tat("nhóm eGFR ≥60 · 45–<60 · <45") == ["60", "45", "60", "45"]
    assert T.cac_so_tom_tat("34 · 3 · 9 · 3 · 1") == ["34", "3", "9", "3", "1"]
    assert T.cac_so_tom_tat("66\t·\t11") == ["66", "11"]


def test_thap_phan_cham_giua_van_ghep_o_ban_tom_tat():
    assert T.cac_so_tom_tat("HR 0·85 (0·73–0·99)") == ["0.85", "0.73", "0.99"]
    assert T.cac_so_tom_tat("HR 1 ·01") == ["1.01"]
    assert T.cac_so_tom_tat("1⋅5") == ["1.5"]


def test_phia_bai_giu_nguyen_cach_ghep_cu():
    # văn bản PDF: «11 ·1», «2·⏎12» vẫn là số thập phân bị tách (bản vá #274 không đổi)
    assert T.cac_so("HR 1 ·01 (0·85–1·21)") == ["1.01", "0.85", "1.21"]
    assert T.cac_so("1·62–2·\n12") == ["1.62", "2.12"]
    assert T.cac_so("11 · 1") == ["11.1"]


def test_cong_khong_chan_so_dem_phan_cach_bang_cham_giua():
    tt = _hop_le()
    trang = list(TRANG)
    trang[0] = trang[0] + " Loop diuretic 1,329 (85.1) eGFR 60 45 group"
    tt["can_thiep_so_sanh"]["dong_tri_lieu"] = "Lợi tiểu quai ở nhóm eGFR ≥60 · 45–<60: 85.1%"
    assert not any("60.45" in x for x in T.kiem_tom_tat(tt, trang, NGU_CANH))


def test_cong_van_chan_so_thap_phan_khong_co_trong_bai():
    tt = _hop_le()
    tt["can_thiep_so_sanh"]["dong_tri_lieu"] = "HR 0·47 cho nhóm điều trị"
    assert any("0.47" in x for x in T.kiem_tom_tat(tt, TRANG, NGU_CANH))
