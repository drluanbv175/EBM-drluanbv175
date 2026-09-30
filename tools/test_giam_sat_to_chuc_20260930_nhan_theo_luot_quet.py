#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nhãn của trạm web hội phải đi theo LƯỢT QUÉT GẦN NHẤT — test ngoại tuyến cho vòng quét chính (30/09/2026, BH138).

Vì sao có: lượt trạm 29/09 không lấy được trang GOLD ⇒ `giam_sat_to_chuc.py` hạ SRC-010 xuống `degraded`. Ngày 30/09
trạm đọc 19 tiêu đề (`--kiem-tra`) nhưng nhãn vẫn `degraded`: vòng quét chỉ có chiều HẠ (fetch hỏng ⇒ degraded), không
có nhánh nào trả nhãn về `active` khi quét lại được, và `sources_health.py` chỉ hồi phục nguồn `api` có điểm thăm. Một
lần trượt mạng vì thế làm trạm mang nhãn «đang mù» mãi — sổ nguồn nói sai, và tuyên bố độ phủ rút trạm khỏi danh sách
đang giám sát dù lượt nào nó cũng thu hoạch.

Cùng vòng quét còn một chiều xanh giả: lấy được trang mà đọc ra 0 tiêu đề (trang thử thách chống bot trả 200, hội đổi
bố cục) vẫn được ghi `last_success_at` hôm nay và ghi đè state bằng danh sách rỗng — lượt kế mọi tiêu đề cũ hiện lại
thành «mới». Không gọi mạng: `_fetch` bị thay bằng trang giả, sổ/state/ứng viên trỏ vào tmp_path.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gstc_nhan_test_mod", ROOT / "tools" / "giam_sat_to_chuc.py")
assert SPEC and SPEC.loader
G = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = G
SPEC.loader.exec_module(G)

TRANG_CO_TIEU_DE = ("<html><body><h2>Global Strategy for Prevention, Diagnosis and Management of COPD: 2026 Report</h2>"
                    "<h2>GOLD Pocket Guide 2026 update for clinicians</h2></body></html>")
TRANG_KHONG_TIEU_DE = "<html><body><p>Checking your browser before accessing the site.</p></body></html>"
NGAY_CU = "2026-09-23"


def _tram(sid: str = "SRC-010", status: str = "degraded", url: str = "https://vi.du/gold") -> dict:
    return {"id": sid, "name": "GOLD — web hội (thử)", "org": "GOLD", "tier": 1, "domain": ["hô hấp"],
            "access": "html-watch", "endpoint_or_url": url, "scan_frequency": "quarterly",
            "detection_method": "content-hash", "owner": "agent-A2", "status": status,
            "last_success_at": NGAY_CU, "known_gap": None}


def _dung(monkeypatch, tmp_path: Path, nguon: list[dict], trang: dict[str, str | None]) -> tuple[Path, list[str]]:
    """Dựng sổ tạm + thay `_fetch`. Trả (đường dẫn sổ, danh sách URL đã bị gọi)."""
    so = tmp_path / "sources.json"
    so.write_text(json.dumps({"updated": "2000-01-01", "sources": nguon}, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")
    monkeypatch.setattr(G, "SO_NGUON", so)
    monkeypatch.setattr(G, "STATE", tmp_path / "state" / "giam-sat-to-chuc.json")
    monkeypatch.setattr(G, "RA", tmp_path / "surveillance")
    da_goi: list[str] = []

    def _gia(url: str) -> str | None:
        da_goi.append(url)
        return trang[url]

    monkeypatch.setattr(G, "_fetch", _gia)
    monkeypatch.setattr(sys, "argv", ["giam_sat_to_chuc.py"])
    return so, da_goi


def _doc(so: Path, sid: str = "SRC-010") -> dict:
    return next(s for s in json.loads(so.read_text(encoding="utf-8"))["sources"] if s["id"] == sid)


def test_tram_degraded_quet_lai_duoc_thi_nhan_ve_active(monkeypatch, tmp_path: Path, capsys) -> None:
    """Đúng ca 29→30/09: trạm đang `degraded`, lượt này đọc được tiêu đề ⇒ nhãn phải về `active` và nói ra."""
    so, _ = _dung(monkeypatch, tmp_path, [_tram(status="degraded")], {"https://vi.du/gold": TRANG_CO_TIEU_DE})
    G.main()
    s = _doc(so)
    assert s["status"] == "active"
    assert s["last_success_at"] == G.date.today().isoformat()
    ra = capsys.readouterr().out
    assert "↺ SRC-010 GOLD — quét lại được (2 tiêu đề) ⇒ nhãn về active" in ra


def test_tram_broken_quet_lai_duoc_cung_ve_active(monkeypatch, tmp_path: Path) -> None:
    """`broken` do `sources_health.py` đặt (quá 2 chu kỳ không thành công) cũng phải hồi phục khi quét được."""
    so, _ = _dung(monkeypatch, tmp_path, [_tram(status="broken")], {"https://vi.du/gold": TRANG_CO_TIEU_DE})
    G.main()
    assert _doc(so)["status"] == "active"


def test_tram_dang_active_quet_duoc_thi_khong_bao_hoi_phuc(monkeypatch, tmp_path: Path, capsys) -> None:
    so, _ = _dung(monkeypatch, tmp_path, [_tram(status="active")], {"https://vi.du/gold": TRANG_CO_TIEU_DE})
    G.main()
    assert _doc(so)["status"] == "active"
    assert "↺" not in capsys.readouterr().out


def test_fetch_hong_van_ha_degraded_va_giu_nguyen_lan_thanh_cong_cu(monkeypatch, tmp_path: Path, capsys) -> None:
    """Chiều HẠ giữ nguyên: fetch hỏng ⇒ degraded, `last_success_at` KHÔNG được tiến, mã thoát 1."""
    so, _ = _dung(monkeypatch, tmp_path, [_tram(status="active")], {"https://vi.du/gold": None})
    assert G.main() == 1
    s = _doc(so)
    assert s["status"] == "degraded" and s["last_success_at"] == NGAY_CU
    assert "fetch hỏng" in capsys.readouterr().out


def test_lay_duoc_trang_nhung_0_tieu_de_khong_tinh_la_thanh_cong(monkeypatch, tmp_path: Path, capsys) -> None:
    """Trang trả 200 mà không đọc ra tiêu đề nào = trạm đang mù: degraded, không ghi `last_success_at`, và KHÔNG
    ghi đè state cũ bằng danh sách rỗng."""
    so, _ = _dung(monkeypatch, tmp_path, [_tram(status="active")], {"https://vi.du/gold": TRANG_KHONG_TIEU_DE})
    state_cu = {"SRC-010": {"hash": "bam-cu", "titles": ["GOLD Report 2025 đã biết"], "luc": NGAY_CU}}
    G.STATE.parent.mkdir(parents=True)
    G.STATE.write_text(json.dumps(state_cu, ensure_ascii=False), encoding="utf-8")
    assert G.main() == 1
    s = _doc(so)
    assert s["status"] == "degraded"
    assert s["last_success_at"] == NGAY_CU
    assert json.loads(G.STATE.read_text(encoding="utf-8")) == state_cu
    ra = capsys.readouterr().out
    assert "SRC-010 GOLD — lấy được trang nhưng 0 tiêu đề" in ra and "state cũ giữ nguyên" in ra


def test_tram_degraded_gap_trang_0_tieu_de_khong_duoc_hoi_phuc(monkeypatch, tmp_path: Path, capsys) -> None:
    """Hai bản vá phải khớp nhau: trạm đang `degraded`/`broken` mà lượt này chỉ lấy được trang KHÔNG tiêu đề thì
    KHÔNG được về `active` và `last_success_at` không tiến — «lấy được trang» chưa phải «quét lại được» (đột biến
    «chỉ chặn 0 tiêu đề khi trạm đang active» từng sống sót trước khi có ca này)."""
    for nhan in ("degraded", "broken"):
        thu_muc = tmp_path / nhan
        thu_muc.mkdir()
        so, _ = _dung(monkeypatch, thu_muc, [_tram(status=nhan)], {"https://vi.du/gold": TRANG_KHONG_TIEU_DE})
        assert G.main() == 1
        s = _doc(so)
        assert s["status"] == "degraded", nhan
        assert s["last_success_at"] == NGAY_CU, nhan
        assert not G.STATE.exists() or "SRC-010" not in json.loads(G.STATE.read_text(encoding="utf-8")), nhan
        assert "↺" not in capsys.readouterr().out, nhan


def test_luot_0_tieu_de_khong_lam_luot_sau_bao_lai_tieu_de_cu_la_moi(monkeypatch, tmp_path: Path, capsys) -> None:
    """Ba lượt liên tiếp: đọc được → trang chặn (0 tiêu đề) → đọc được lại. Lượt ba không được sinh ứng viên nào
    (các tiêu đề đã biết từ lượt một) và nhãn phải về active — bản cũ xoá state ở lượt hai nên lượt ba báo lại cả hai."""
    trang = {"https://vi.du/gold": TRANG_CO_TIEU_DE}
    so, _ = _dung(monkeypatch, tmp_path, [_tram(status="active")], trang)
    assert G.main() == 1                                   # lượt 1: 2 tiêu đề mới ⇒ ghi ứng viên
    tep = list(G.RA.glob("to-chuc-*.md"))
    assert len(tep) == 1
    so_dong_luot_1 = tep[0].read_text(encoding="utf-8").count("- **GOLD**")
    assert so_dong_luot_1 == 2

    trang["https://vi.du/gold"] = TRANG_KHONG_TIEU_DE     # lượt 2: trang chặn
    assert G.main() == 1
    assert _doc(so)["status"] == "degraded"

    trang["https://vi.du/gold"] = TRANG_CO_TIEU_DE        # lượt 3: đọc được lại
    capsys.readouterr()
    assert G.main() == 0, "lượt 3 không có tiêu đề mới và không trạm hỏng ⇒ mã 0"
    assert _doc(so)["status"] == "active"
    assert tep[0].read_text(encoding="utf-8").count("- **GOLD**") == so_dong_luot_1
    assert "↺ SRC-010" in capsys.readouterr().out


def test_tram_not_covered_khong_bao_gio_bi_vong_quet_dung(monkeypatch, tmp_path: Path) -> None:
    """`not-covered` có endpoint KHÔNG được quét, càng không được tự bật ở vòng quét chính (chỉ `--bat-neu-ok` và
    `--nap-van-ban` mới bật, có ghi bằng chứng kích hoạt)."""
    so, da_goi = _dung(monkeypatch, tmp_path,
                       [_tram("SRC-099", status="not-covered", url="https://vi.du/cho"), _tram(status="degraded")],
                       {"https://vi.du/cho": TRANG_CO_TIEU_DE, "https://vi.du/gold": TRANG_CO_TIEU_DE})
    G.main()
    assert da_goi == ["https://vi.du/gold"]
    assert _doc(so, "SRC-099")["status"] == "not-covered"
    assert _doc(so, "SRC-099")["last_success_at"] == NGAY_CU


def test_nhan_hoi_phuc_duoc_ghi_xuong_so_dung_dinh_dang_git(monkeypatch, tmp_path: Path) -> None:
    """Nhãn mới phải nằm TRÊN ĐĨA (không chỉ trong bộ nhớ) và sổ vẫn đúng định dạng git: thụt lề 2 + LF (BH116)."""
    so, _ = _dung(monkeypatch, tmp_path, [_tram(status="degraded")], {"https://vi.du/gold": TRANG_CO_TIEU_DE})
    G.main()
    raw = so.read_bytes()
    du = json.loads(raw)
    assert du["sources"][0]["status"] == "active"
    assert b"\r" not in raw and raw.decode("utf-8") == json.dumps(du, ensure_ascii=False, indent=2) + "\n"
