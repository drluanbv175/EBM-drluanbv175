#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #1 (đợt dò nâng cấp 26/09/2026): luật «apply chỉ dựa Consensus ⇒ chặn».

Tái hiện gốc: `strict_source_checks()` so `design == "Consensus"` — CHÍNH XÁC, phân biệt hoa/thường.
Các biến thể 'consensus', 'CONSENSUS', 'Consensus statement', 'Đồng thuận chuyên gia',
'Đồng thuận đa hội (expert consensus)' (chuỗi cuối lấy từ dữ liệu thật của 60 dashboard) mang
gradeLevel mod/high + gradeBy + decision='apply' đi qua cổng strict với 0 lỗi — bộ năm được gắn
`--verified`, trái luật bất biến CLAUDE.md §6.3 «Consensus không bao giờ đủ».

Kiểm cả hai bản trong git (nguồn chuẩn + bản dark-analyst) và tính đồng nhất byte của chúng.
Ngoại tuyến 100%, không đọc dashboard thật.
"""
from __future__ import annotations

import datetime as dt
import filecmp
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VD_NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
VD_DARK = ROOT / "sync" / "skills" / "dark-analyst" / "tools" / "verify_dashboard.py"


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


BAN = {"nguon": _nap("vd_consensus_nguon_20260926", VD_NGUON),
       "dark": _nap("vd_consensus_dark_20260926", VD_DARK)}

_HOM_NAY = dt.date(2026, 9, 26)
_STANDARDS = ("standards:{frame:'PICO', sourceHierarchy:'guideline > SR', reporting:'PRISMA', "
              "appraisal:'GRADE', currency:'2026-09-20', safety:'có', vietnamFit:'có', "
              "searchSources:['PubMed','Cochrane'], gates:['verify']},")


def _item(design: str, grade: str = "mod", dec: str = "apply") -> str:
    return ("{id:'ITEM-01', source:'Nguồn thử', org:'Hội X', dateVersion:'2025', design:%r, "
            "gradeLevel:'%s', gradeBy:'Hội X 2025', gradeSource:'Hội X 2025 — mức B', "
            "decision:'%s', pmid:'34101376', references:['Tác giả. Tiêu đề. PMID 34101376.']}"
            % (design, grade, dec))


def _loi_consensus(vd, design: str, grade: str = "mod", dec: str = "apply") -> list[str]:
    db = "const DATA={meta:{updated:'2026-09-20'}, %s items:[%s]}" % (_STANDARDS, _item(design, grade, dec))
    blk = vd.extract_data_block("<script>%s</script>" % db) or db
    items = vd.split_items(blk)
    assert len(items) == 1, "fixture phải tách đúng 1 item"
    errors, _w, _o = vd.strict_source_checks(blk, items, today=_HOM_NAY)
    return [e for e in errors if "chỉ dựa Consensus" in e]


BIEN_THE = [
    ("Consensus", "mod"),
    ("consensus", "mod"),
    ("CONSENSUS", "high"),
    ("Consensus statement", "high"),
    ("Đồng thuận chuyên gia", "mod"),
    ("Đồng thuận đa hội (expert consensus)", "high"),
    ("  đồng thuận liên hội  ", "mod"),
]


@pytest.mark.parametrize("ban", sorted(BAN))
@pytest.mark.parametrize("design,grade", BIEN_THE)
def test_moi_bien_the_ho_dong_thuan_voi_apply_bi_chan_dung_mot_loi(ban, design, grade):
    loi = _loi_consensus(BAN[ban], design, grade)
    assert len(loi) == 1, (ban, design, loi)
    assert "ITEM-01" in loi[0]


@pytest.mark.parametrize("ban", sorted(BAN))
def test_chuoi_nfd_to_hop_cung_bi_bat(ban):
    import unicodedata
    nfd = unicodedata.normalize("NFD", "Đồng thuận chuyên gia")
    assert nfd != "Đồng thuận chuyên gia"
    assert len(_loi_consensus(BAN[ban], nfd)) == 1


@pytest.mark.parametrize("ban", sorted(BAN))
@pytest.mark.parametrize("design", ["Guideline", "Guideline (dựa đồng thuận)", "RCT (đồng thuận chuyên gia về kết cục)",
                                    "Meta", "Nhãn thuốc"])
def test_ca_am_ho_khac_khong_bi_gan_loi_consensus(ban, design):
    """Tiền tố, KHÔNG chuỗi con: guideline/RCT nhắc chữ «đồng thuận» ở phần mô tả không bị bắt nhầm."""
    assert _loi_consensus(BAN[ban], design) == []


@pytest.mark.parametrize("ban", sorted(BAN))
def test_consensus_khong_apply_khong_bi_loi_nay(ban):
    assert _loi_consensus(BAN[ban], "Đồng thuận chuyên gia", dec="consider") == []


@pytest.mark.parametrize("ban", sorted(BAN))
def test_la_consensus_thuan(ban):
    vd = BAN[ban]
    assert vd.la_consensus("consensus") and vd.la_consensus("Đồng Thuận") and vd.la_consensus(" CONSENSUS x")
    assert not vd.la_consensus("") and not vd.la_consensus(None) and not vd.la_consensus("Guideline (đồng thuận)")


def test_hai_ban_trong_git_giong_het_tung_byte():
    assert filecmp.cmp(VD_NGUON, VD_DARK, shallow=False), \
        "sửa nguồn chuẩn thì phải chép byte sang sync/skills/dark-analyst/tools/verify_dashboard.py"


def test_doctrine_skill_day_luat_ho_dong_thuan():
    """Thêm luật ở CỔNG thì phải DẠY AGENT cùng lúc (CLAUDE.md §6.4)."""
    skill = (ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "SKILL.md").read_text(encoding="utf-8")
    dong = [d for d in skill.splitlines() if "họ đồng thuận" in d.lower()]
    assert dong, "SKILL.md chưa dạy agent rằng MỌI biến thể họ đồng thuận + apply đều bị chặn"
