#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy HV-08 (02/10/2026): «kỳ 14/09 lỡ» lặp 28 lần ở 15 phiên dù kỳ sau đã chạy lại — cảnh báo hết giá trị.

Kỳ CŨ đã lỡ mà kỳ sau đã chạy lại (uu=2): hook (`--im-khi-on`) im lặng; hòm việc không đưa thành 🛎 (chỉ một dòng ⓘ, không tính là việc);
chạy KHÔNG cờ vẫn in đủ. Kỳ GẦN NHẤT lỡ/trễ (uu ≤ 1) vẫn in đỏ/cam như cũ."""
from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, GOC / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


kln = _nap("kln_hv08", "kiem_lich_nen.py")
PD_CU = {"phat_hien": [{"id": "goi-duyet-tuan-ebm", "ky": "2026-09-14 18:30", "muc": "lo", "uu": 2,
                        "thong_diep": "«goi-duyet-tuan-ebm» kỳ 14/09/2026 18:30: thiếu queue/tuan-2026-W38.md"}],
         "khong_do_duoc": [], "ok": 3}
PD_MOI = {"phat_hien": [dict(PD_CU["phat_hien"][0], uu=0, ky="2026-09-28 18:30",
                             thong_diep="«goi-duyet-tuan-ebm» kỳ 28/09/2026 18:30: thiếu queue/tuan-2026-W40.md")],
          "khong_do_duoc": [], "ok": 3}


def test_hook_im_lang_voi_ky_cu_da_chay_lai(monkeypatch, capsys):
    monkeypatch.setattr(kln, "kiem", lambda *a, **k: PD_CU)
    assert kln.main(["--im-khi-on"]) == 0 and capsys.readouterr().out == ""


def test_chay_khong_co_van_in_ky_cu(monkeypatch, capsys):
    monkeypatch.setattr(kln, "kiem", lambda *a, **k: PD_CU)
    assert kln.main([]) == 0 and "kỳ 14/09/2026" in capsys.readouterr().out


def test_ky_gan_nhat_lo_van_bao_do_o_hook(monkeypatch, capsys):
    monkeypatch.setattr(kln, "kiem", lambda *a, **k: PD_MOI)
    assert kln.main(["--im-khi-on"]) == 1 and "🔴" in capsys.readouterr().out


def test_hom_viec_khong_dua_ky_cu_thanh_viec():
    tdx = _nap("tdx_hv08", "tu_de_xuat_viec.py")
    viec, tt = tdx.phan_loai_lich_nen(PD_CU["phat_hien"])
    assert viec == [] and len(tt) == 1 and "1 kỳ lịch nền CŨ" in tt[0]
    viec2, tt2 = tdx.phan_loai_lich_nen(PD_MOI["phat_hien"] + PD_CU["phat_hien"])
    assert [v[0] for v in viec2] == [0] and viec2[0][1] == "🛎" and "W40" in viec2[0][2] and len(tt2) == 1
    assert tdx.phan_loai_lich_nen([]) == ([], [])


def test_kiem_that_tren_du_lieu_gia_cho_uu_2_khi_ky_sau_da_chay(tmp_path):
    """Hành vi gốc của `kiem` không đổi: kỳ cũ lỡ + kỳ mới có dấu vết ⇒ uu=2 (đầu vào cho luật im lặng ở hook)."""
    (tmp_path / "queue").mkdir()
    (tmp_path / "queue" / "tuan-2026-W39.md").write_text("x", encoding="utf-8", newline="\n")
    (tmp_path / "queue" / "tuan-2026-W40.md").write_text("x", encoding="utf-8", newline="\n")
    so = {"cua_so_ngay": 21, "tac_vu": [{"id": "goi-duyet-tuan-ebm", "cron": "30 18 * * 1", "tu_ngay": "2026-08-17",
                                         "grace_gio": 30, "dau_vet": {"loai": "file-tuan-iso",
                                                                      "path": "queue/tuan-{iso_nam}-W{iso_tuan:02d}.md"}}]}
    kq = kln.kiem(dt.datetime(2026, 10, 2, 12), so, tmp_path)
    assert [p["uu"] for p in kq["phat_hien"]] == [2] and "W38" in kq["phat_hien"][0]["thong_diep"]


# ── F4: dấu vết «file-ngay» (tệp mang ngày chạy) cho tác vụ 9 trạm web hội ──────────────────────────────────────────────
SO_9_TRAM = {"cua_so_ngay": 21, "tac_vu": [{"id": "giam-sat-9-tram-web-hoi-tuan", "cron": "45 18 * * 1", "tu_ngay": "2026-09-14",
                                            "grace_gio": 30, "dau_vet": {"loai": "file-ngay",
                                                                         "path": "surveillance/to-chuc-{ngay}.md"}}]}


def _to_chuc(tmp_path, *ngay):
    d = tmp_path / "surveillance"
    d.mkdir(exist_ok=True)
    for x in ngay:
        (d / f"to-chuc-{x}.md").write_text("x", encoding="utf-8", newline="\n")
    (d / "to-chuc-khong-phai-ngay.md").write_text("x", encoding="utf-8", newline="\n")


def test_file_ngay_dung_han_tre_va_lo(tmp_path):
    _to_chuc(tmp_path, "2026-09-15", "2026-09-24", "2026-09-29")  # 14/09 đúng hạn · 21/09 trễ (24/09; hạn 30 giờ = tới hết 23/09) · 28/09 đúng
    kq = kln.kiem(dt.datetime(2026, 10, 2, 12), SO_9_TRAM, tmp_path)
    ds = {p["ky"][:10]: p for p in kq["phat_hien"]}
    assert set(ds) == {"2026-09-21"} and ds["2026-09-21"]["muc"] == "tre" and ds["2026-09-21"]["uu"] == 2
    assert "TRỄ ngày 24/09" in ds["2026-09-21"]["thong_diep"]


def test_file_ngay_ky_gan_nhat_lo_la_do(tmp_path):
    _to_chuc(tmp_path, "2026-09-15", "2026-09-22")
    kq = kln.kiem(dt.datetime(2026, 10, 2, 12), SO_9_TRAM, tmp_path)
    moi = [p for p in kq["phat_hien"] if p["ky"].startswith("2026-09-28")]
    assert moi and moi[0]["uu"] == 0 and moi[0]["muc"] == "lo"


def test_file_ngay_vang_thu_muc_la_khong_do_duoc(tmp_path):
    kq = kln.kiem(dt.datetime(2026, 10, 2, 12), SO_9_TRAM, tmp_path)
    assert kq["phat_hien"] == [] and any("vắng mặt" in x for x in kq["khong_do_duoc"])


def test_so_khai_that_co_tac_vu_9_tram_va_ban_nguon_git():
    import json
    so = json.loads((GOC / "sync" / "lich-nen-ky-vong.json").read_text(encoding="utf-8"))
    tv = [t for t in so["tac_vu"] if t["id"] == "giam-sat-9-tram-web-hoi-tuan"]
    assert len(tv) == 1 and tv[0]["cron"] == "45 18 * * 1" and tv[0]["dau_vet"]["loai"] == "file-ngay"
    skill = GOC / "sync" / "scheduled-tasks" / "giam-sat-9-tram-web-hoi-tuan" / "SKILL.md"
    assert skill.exists() and "NỀN TẢNG: macOS + Windows" in skill.read_text(encoding="utf-8")
