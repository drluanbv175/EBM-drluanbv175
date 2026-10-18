# -*- coding: utf-8 -*-
"""Hồi quy tools/liet_ke_the_trung_hub.py — cụm thẻ trùng + luật đề xuất thẻ giữ (18/10/2026).

Sổ cái giả trong thư mục tạm; dùng key_of của cầu nạp nguồn chuẩn (sync/ebm-master-tools/).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "liet_ke_the_trung_hub.py"


def _nap():
    spec = importlib.util.spec_from_file_location("liet_ke_trung_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LK = _nap()
CN = LK.nap_cau_nap()


def _the(id_, topic, doi="10.5/g", decision="apply", history=None, **them):
    c = {"id": id_, "topic": topic, "decision": decision, "date_added": "2026-07-13",
         "source": {"doi": doi, "pmid": "", "title": "Dashboard thử"},
         "recommendation": "Khuyến cáo", "practice": {"action": "Làm X", "monitoring": "", "safety": ""},
         "history": history or [{"date": "2026-07-13", "change": "nạp từ dashboard WebDashboard_EBM_VanDeCuThe_Thu_20260101.html"}]}
    c.update(them)
    return c


def test_tim_cum_cung_khoa_va_cung_tieu_de_chuan_hoa():
    cards = [
        _the("EVID-2026-0010", "Dự phòng  TIÊN PHÁT đột quỵ"),
        _the("EVID-2026-0020", "dự phòng tiên phát đột quỵ"),          # khác hoa/thường + khoảng trắng
        _the("EVID-2026-0030", "Mục tiêu huyết áp"),                     # cùng DOI, khác tiêu đề
        _the("EVID-2026-0040", "Dự phòng TIÊN PHÁT đột quỵ", doi="10.5/khac"),  # cùng tiêu đề, khác DOI
    ]
    cum = LK.tim_cum(cards, CN.key_of)
    assert [[c["id"] for c in v] for v in cum] == [["EVID-2026-0010", "EVID-2026-0020"]]


def test_de_xuat_giu_the_goc_khi_khong_co_tieu_chi_khac():
    cum = [_the("EVID-2026-0400", "A"), _the("EVID-2026-0005", "A"), _the("EVID-2026-0300", "A")]
    dx = LK.de_xuat(cum, {}, CN)
    assert dx["giu"] == "EVID-2026-0005" and not dx["can_bac_si"]
    assert sorted(dx["loai"]) == ["EVID-2026-0300", "EVID-2026-0400"]


def test_de_xuat_uu_tien_the_duoc_tham_chieu_roi_cap_nhat_bac_si():
    cum = [_the("EVID-2026-0005", "A"),
           _the("EVID-2026-0300", "A", history=[{"date": "2026-10-18", "change": "cập nhật tại chỗ theo phiên bản nối tiếp X.html (ITEM-01)"}]),
           _the("EVID-2026-0400", "A")]
    assert LK.de_xuat(cum, {}, CN)["giu"] == "EVID-2026-0300"
    dx = LK.de_xuat(cum, {"EVID-2026-0400": ["quality/eval/tra-diem-kham/bo-vang.json"]}, CN)
    assert dx["giu"] == "EVID-2026-0400" and dx["ly_do"].startswith("đang được tham chiếu")


def test_khong_de_xuat_khi_lech_decision_hoac_nhieu_the_duoc_tham_chieu():
    lech = [_the("EVID-2026-0005", "A", decision="apply"), _the("EVID-2026-0300", "A", decision="notyet")]
    dx = LK.de_xuat(lech, {}, CN)
    assert dx["giu"] is None and dx["can_bac_si"] and "decision" in dx["ly_do"]
    cum = [_the("EVID-2026-0005", "A"), _the("EVID-2026-0300", "A")]
    dx = LK.de_xuat(cum, {"EVID-2026-0005": ["a"], "EVID-2026-0300": ["b"]}, CN)
    assert dx["giu"] is None and dx["can_bac_si"]


def test_co_canh_bao_khi_the_giu_thieu_truong_the_loai_co():
    goc = _the("EVID-2026-0005", "A")
    ban_sao = _the("EVID-2026-0300", "A", practice={"action": "Làm X", "monitoring": "Theo dõi Y", "safety": ""})
    dx = LK.de_xuat([goc, ban_sao], {}, CN)
    assert dx["giu"] == "EVID-2026-0005"
    assert dx["thieu_so_voi_the_loai"] == ["practice.monitoring"]


def test_quet_tham_chieu_chi_nguon_song(tmp_path):
    (tmp_path / "implementation").mkdir()
    (tmp_path / "implementation" / "EVID-2026-0300.md").write_text("ghi chú", encoding="utf-8")
    (tmp_path / "clinical_runtime").mkdir()
    (tmp_path / "clinical_runtime" / "strict_source_report.json").write_text('["EVID-2026-0005"]', encoding="utf-8")
    ref = LK.quet_tham_chieu(tmp_path, {"EVID-2026-0005", "EVID-2026-0300"})
    assert ref == {"EVID-2026-0300": ["implementation/EVID-2026-0300.md"]}


def _chay(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-B", str(TOOL), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)


def test_cli_ghi_bao_cao_va_ma_thoat(tmp_path):
    hub = tmp_path / "EBM_MASTER"
    hub.mkdir()
    (hub / "EBM_MASTER.json").write_text(json.dumps({"evidence_cards": [
        _the("EVID-2026-0005", "A"), _the("EVID-2026-0300", "A"), _the("EVID-2026-0301", "B")]},
        ensure_ascii=False), encoding="utf-8")
    ra = tmp_path / "ra"
    r = _chay("--hub", hub, "--ra", ra, "--ngay", "2026-10-18")
    assert r.returncode == 1, r.stdout + r.stderr
    bc = json.loads((ra / "THE-TRUNG-HUB_2026-10-18.json").read_text(encoding="utf-8"))
    assert bc["so_cum"] == 1 and bc["so_the_thua"] == 1 and bc["cum"][0]["giu"] == "EVID-2026-0005"
    md = (ra / "THE-TRUNG-HUB_2026-10-18.md").read_text(encoding="utf-8")
    assert 'manage_ledger.py drop EVID-2026-0300' in md and "CHỈ ĐỌC" in md
    # Sổ cái KHÔNG bị ghi.
    assert len(json.loads((hub / "EBM_MASTER.json").read_text(encoding="utf-8"))["evidence_cards"]) == 3


def test_cli_khong_co_so_cai_la_khong_do_duoc(tmp_path):
    r = _chay("--hub", tmp_path / "khong-co", "--ra", tmp_path / "ra")
    assert r.returncode == 2 and "KHÔNG ĐO ĐƯỢC" in r.stdout


def test_cli_khong_co_cum_ma_0(tmp_path):
    hub = tmp_path / "EBM_MASTER"
    hub.mkdir()
    (hub / "EBM_MASTER.json").write_text(json.dumps({"evidence_cards": [_the("EVID-2026-0005", "A")]}), encoding="utf-8")
    assert _chay("--hub", hub, "--ra", tmp_path / "ra").returncode == 0
