# -*- coding: utf-8 -*-
"""Hồi quy `manage_ledger.py drop-nhieu` — loại nhiều thẻ, MỘT lần ghi, MỘT bản sao lưu (18/10/2026).

Chạy NGUỒN CHUẨN sync/ebm-master-tools/manage_ledger.py trên sổ cái TẠM (EBM_MASTER_HUB_DIR) —
không đụng EBM_MASTER thật; chạy được cả trên CI.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ML = REPO / "sync" / "ebm-master-tools" / "manage_ledger.py"
LIET_KE = REPO / "tools" / "liet_ke_the_trung_hub.py"


def _the(id_, topic, doi="10.5/g", decision="apply"):
    return {"id": id_, "topic": topic, "decision": decision, "date_added": "2026-07-13",
            "source": {"doi": doi, "pmid": "", "title": "Dashboard thử"}, "recommendation": "Khuyến cáo",
            "verification_status": "đã xác minh",
            "history": [{"date": "2026-07-13", "change": "nạp từ dashboard WebDashboard_EBM_VanDeCuThe_Thu_20260101.html"}]}


def _hub(tmp: Path, cards) -> Path:
    hub = tmp / "EBM_MASTER"
    hub.mkdir()
    (hub / "EBM_MASTER.json").write_text(json.dumps(
        {"meta": {"counts": {"evidence_cards": len(cards)}, "last_updated": "2026-10-18"},
         "evidence_cards": cards}, ensure_ascii=False), encoding="utf-8")
    return hub


def _so_cai_mau(tmp: Path) -> Path:
    return _hub(tmp, [
        _the("EVID-2026-0005", "Dự phòng tiên phát"), _the("EVID-2026-0300", "Dự phòng tiên phát"),
        _the("EVID-2026-0400", "dự phòng  TIÊN PHÁT"),
        _the("EVID-2026-0010", "Khung thứ phát", doi="10.5/h"), _the("EVID-2026-0310", "Khung thứ phát", doi="10.5/h"),
        _the("EVID-2026-0020", "Thẻ riêng", doi="10.5/k"),
    ])


def _chay(hub: Path, *args) -> subprocess.CompletedProcess:
    env = dict(os.environ, EBM_MASTER_HUB_DIR=str(hub), EBM_MASTER_LEDGER_LOCK_HELD="1", PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-B", str(ML), "drop-nhieu", *map(str, args)], cwd=str(hub),
                          capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)


def _ids(hub: Path) -> list[str]:
    return [c["id"] for c in json.loads((hub / "EBM_MASTER.json").read_text(encoding="utf-8"))["evidence_cards"]]


def _sao_luu(hub: Path) -> list[Path]:
    return sorted((hub / "BACKUPS").glob("EBM_MASTER_*")) if (hub / "BACKUPS").is_dir() else []


def _bao_cao(tmp: Path, cum) -> Path:
    p = tmp / "THE-TRUNG-HUB_2026-10-18.json"
    p.write_text(json.dumps({"cum": cum}, ensure_ascii=False), encoding="utf-8")
    return p


CUM_DUOC = {"giu": "EVID-2026-0005", "loai": ["EVID-2026-0300", "EVID-2026-0400"], "can_bac_si": False, "ly_do": "x"}
CUM_HAI = {"giu": "EVID-2026-0010", "loai": ["EVID-2026-0310"], "can_bac_si": False, "ly_do": "x"}
CUM_BAC_SI = {"giu": None, "loai": [], "can_bac_si": True, "ly_do": "các thẻ khác decision"}


def test_mac_dinh_chay_kho_khong_ghi(tmp_path):
    hub = _so_cai_mau(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    r = _chay(hub, "EVID-2026-0300", "EVID-2026-0400")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "CHẠY KHÔ" in r.stdout and "EVID-2026-0300" in r.stdout
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc and _sao_luu(hub) == []


def test_ap_dung_can_loi_duyet_cua_bac_si(tmp_path):
    hub = _so_cai_mau(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    r = _chay(hub, "EVID-2026-0300", "--ap-dung")
    assert r.returncode == 2 and "--ly-do" in r.stdout
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc


def test_ap_dung_mot_lan_ghi_mot_ban_sao_luu(tmp_path):
    hub = _so_cai_mau(tmp_path)
    r = _chay(hub, "EVID-2026-0300", "evid-2026-0400", "EVID-2026-0310", "--ap-dung", "--ly-do", "bác sĩ duyệt 18/10")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _ids(hub) == ["EVID-2026-0005", "EVID-2026-0010", "EVID-2026-0020"]
    sao_luu = _sao_luu(hub)
    assert len(sao_luu) == 1, sao_luu                          # MỘT bản cho cả lô ba thẻ
    assert len(json.loads(sao_luu[0].read_text(encoding="utf-8"))["evidence_cards"]) == 6
    meta = json.loads((hub / "EBM_MASTER.json").read_text(encoding="utf-8"))["meta"]
    assert meta["counts"]["evidence_cards"] == 3
    assert "bác sĩ duyệt 18/10" in r.stdout


def test_mot_id_khong_ton_tai_thi_khong_loai_gi(tmp_path):
    hub = _so_cai_mau(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    r = _chay(hub, "EVID-2026-0300", "EVID-2026-9999", "--ap-dung", "--ly-do", "duyệt")
    assert r.returncode == 2 and "EVID-2026-9999" in r.stdout
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc


def test_tu_bao_cao_chi_loai_cum_da_chon(tmp_path):
    hub = _so_cai_mau(tmp_path)
    bc = _bao_cao(tmp_path, [CUM_DUOC, CUM_HAI])
    r = _chay(hub, "--tu-bao-cao", bc, "--cum", "1", "--ap-dung", "--ly-do", "duyệt cụm 1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _ids(hub) == ["EVID-2026-0005", "EVID-2026-0010", "EVID-2026-0310", "EVID-2026-0020"]


def test_tu_bao_cao_cum_bac_si_chon_bi_tu_choi_ca_lo(tmp_path):
    hub = _so_cai_mau(tmp_path)
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    bc = _bao_cao(tmp_path, [CUM_DUOC, CUM_BAC_SI])
    r = _chay(hub, "--tu-bao-cao", bc, "--cum", "all", "--ap-dung", "--ly-do", "duyệt")
    assert r.returncode == 2 and "KHÔNG đề xuất thẻ giữ" in r.stdout
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc


def test_tu_bao_cao_so_cai_da_doi_thi_tu_choi(tmp_path):
    """Báo cáo là ảnh chụp: sau đó một thẻ trong cụm đổi tiêu đề (vd nạp nối tiếp) ⇒ không còn trùng."""
    hub = _so_cai_mau(tmp_path)
    bc = _bao_cao(tmp_path, [CUM_DUOC])
    data = json.loads((hub / "EBM_MASTER.json").read_text(encoding="utf-8"))
    data["evidence_cards"][2]["topic"] = "Dự phòng tiên phát — bản 2026 đã sửa"
    (hub / "EBM_MASTER.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    truoc = (hub / "EBM_MASTER.json").read_bytes()
    r = _chay(hub, "--tu-bao-cao", bc, "--cum", "1", "--ap-dung", "--ly-do", "duyệt")
    assert r.returncode == 2 and "KHÔNG còn trùng khoá + tiêu đề" in r.stdout
    assert (hub / "EBM_MASTER.json").read_bytes() == truoc


def test_tu_bao_cao_lech_decision_luc_ghi_thi_tu_choi(tmp_path):
    hub = _so_cai_mau(tmp_path)
    bc = _bao_cao(tmp_path, [CUM_DUOC])
    data = json.loads((hub / "EBM_MASTER.json").read_text(encoding="utf-8"))
    data["evidence_cards"][1]["decision"] = "notyet"
    (hub / "EBM_MASTER.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    r = _chay(hub, "--tu-bao-cao", bc, "--cum", "1", "--ap-dung", "--ly-do", "duyệt")
    assert r.returncode == 2 and "khác decision" in r.stdout
    assert "EVID-2026-0300" in _ids(hub)


def test_tham_so_bat_buoc(tmp_path):
    hub = _so_cai_mau(tmp_path)
    bc = _bao_cao(tmp_path, [CUM_DUOC])
    assert _chay(hub, "--tu-bao-cao", bc).returncode == 2                         # thiếu --cum
    assert _chay(hub, "EVID-2026-0300", "--tu-bao-cao", bc, "--cum", "1").returncode == 2
    assert _chay(hub, "--tu-bao-cao", bc, "--cum", "7").returncode == 2           # ngoài báo cáo
    assert _chay(hub).returncode == 2


def test_dau_cuoi_liet_ke_roi_loai_theo_bao_cao(tmp_path):
    """liet_ke_the_trung_hub.py lập báo cáo → drop-nhieu --cum all → không còn cụm trùng."""
    hub = _so_cai_mau(tmp_path)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    ra = tmp_path / "ra"
    r1 = subprocess.run([sys.executable, "-B", str(LIET_KE), "--hub", str(hub), "--ra", str(ra), "--ngay", "2026-10-18"],
                        capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)
    assert r1.returncode == 1, r1.stdout + r1.stderr
    r2 = _chay(hub, "--tu-bao-cao", ra / "THE-TRUNG-HUB_2026-10-18.json", "--cum", "all",
               "--ap-dung", "--ly-do", "bác sĩ duyệt cả hai cụm")
    assert r2.returncode == 0, r2.stdout + r2.stderr
    assert _ids(hub) == ["EVID-2026-0005", "EVID-2026-0010", "EVID-2026-0020"]
    assert len(_sao_luu(hub)) == 1
    r3 = subprocess.run([sys.executable, "-B", str(LIET_KE), "--hub", str(hub), "--ra", str(ra), "--ngay", "2026-10-19"],
                        capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)
    assert r3.returncode == 0, r3.stdout + r3.stderr
