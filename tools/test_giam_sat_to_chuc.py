#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test NGOẠI TUYẾN cho chế độ dò/bật trạm của giam_sat_to_chuc (29/08/2026).

Vì sao có: trạm hội «dựng xong nằm chờ» từ 15/08 vì không ai xác minh sống được
URL; hai chế độ --kiem-tra/--bat-neu-ok là đường kích hoạt một-lệnh trên máy
thật. Test này khoá hợp đồng của chúng bằng fixture — không gọi mạng."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gstc_test_mod", ROOT / "tools" / "giam_sat_to_chuc.py")
assert SPEC and SPEC.loader
G = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = G
SPEC.loader.exec_module(G)

HTML_CO_TIEU_DE = "<html><h2>GOLD Report 2026 — Global Strategy</h2><a href=/x>Pocket Guide 2026</a></html>"
HTML_KHONG_TIEU_DE = "<html><p>chỉ văn xuôi giới thiệu hội, không mục lục</p></html>"


def _nguon(sid: str, status: str = "not-covered", url: str | None = "https://vi.du/x") -> dict:
    return {"id": sid, "org": "X", "domain": ["d"], "access": "html-watch",
            "endpoint_or_url": url, "status": status}


def test_kiem_tra_phan_biet_ba_ket_cuc(monkeypatch) -> None:
    """fetch hỏng ✗ · fetch OK nhưng 0 tiêu đề ✗ (kèm lý do) · có tiêu đề ✓."""
    noi_dung = {"https://vi.du/hong": None,
                "https://vi.du/rong": HTML_KHONG_TIEU_DE,
                "https://vi.du/tot": HTML_CO_TIEU_DE}
    monkeypatch.setattr(G, "_fetch", lambda url: noi_dung[url])
    kq = G.kiem_tra_tram([_nguon("A", url="https://vi.du/hong"),
                          _nguon("B", url="https://vi.du/rong"),
                          _nguon("C", url="https://vi.du/tot")])
    assert kq["A"]["ok"] is False and "fetch hỏng" in kq["A"]["ly_do"]
    assert kq["B"]["ok"] is False and "0 tiêu đề" in kq["B"]["ly_do"]
    assert kq["C"]["ok"] is True and kq["C"]["so_tieu_de"] >= 1


def test_kiem_tra_bo_qua_nguon_khong_phai_tram(monkeypatch) -> None:
    """Nguồn access=api/manual hoặc thiếu endpoint KHÔNG được dò — tránh gọi mạng thừa."""
    monkeypatch.setattr(G, "_fetch", lambda url: HTML_CO_TIEU_DE)
    kq = G.kiem_tra_tram([
        {"id": "API", "access": "api", "endpoint_or_url": "https://vi.du", "status": "active"},
        _nguon("THIEU-URL", url=None),
        _nguon("TRAM"),
    ])
    assert set(kq) == {"TRAM"}


def test_bat_neu_ok_chi_bat_tram_dat_va_dang_not_covered() -> None:
    """Chỉ trạm dò ĐẠT + đang not-covered mới bật; trạm active sẵn và trạm dò
    trượt giữ nguyên — bật trạm trượt là ghi «active» suông, đúng thứ sổ cấm."""
    du = {"sources": [_nguon("DAT"), _nguon("TRUOT"),
                       _nguon("DA-BAT", status="active")]}
    kq = {"DAT": {"ok": True, "so_tieu_de": 3, "ly_do": None},
          "TRUOT": {"ok": False, "so_tieu_de": 0, "ly_do": "fetch hỏng"},
          "DA-BAT": {"ok": True, "so_tieu_de": 2, "ly_do": None}}
    bat = G.bat_neu_ok(du, kq)
    assert bat == ["DAT"]
    trang_thai = {s["id"]: s["status"] for s in du["sources"]}
    assert trang_thai == {"DAT": "active", "TRUOT": "not-covered", "DA-BAT": "active"}
    dat = next(s for s in du["sources"] if s["id"] == "DAT")
    assert dat["kich_hoat"]["so_tieu_de_luc_do"] == 3
    assert "DA-BAT" not in [s["id"] for s in du["sources"] if "kich_hoat" in s]


def test_bat_neu_ok_khong_ghi_dia() -> None:
    """bat_neu_ok là hàm THUẦN sửa dict — caller sao lưu rồi mới ghi; hàm tự ghi
    đĩa sẽ vòng qua bước sao lưu."""
    import inspect
    nguon = inspect.getsource(G.bat_neu_ok)
    assert "write_text" not in nguon and "open(" not in nguon


# ---------------------------------------------------------------------------
# --nap-van-ban (09/09/2026) — SRC-015 ACC/AHA bị Cloudflare bot-challenge
# chặn urllib nhưng Browser thật tải được; luồng này nạp nội dung ĐÃ TẢI SẴN
# (văn bản thuần, không HTML) và chạy CÙNG logic so-sánh/ghi-state với luồng
# quét chính, chỉ khác nguồn nội dung.
# ---------------------------------------------------------------------------

VAN_BAN_CO_TIEU_DE = (
    "Trang chủ Guidelines and Statements\n"
    "\n"
    "2026 Guideline for the Prevention of Stroke in Patients With Stroke\n"
    "\n"
    "Fifth Universal Definition of Myocardial Infarction (2026)\n"
    "\n"
    "giới thiệu hội, không phải tiêu đề — quá ngắn hoặc không có năm/từ khoá\n"
)


def test_rut_tieu_de_tu_van_ban_loc_dung_va_khop_loc_html() -> None:
    """Bộ lọc văn bản thuần phải nhận đúng 3 dòng hợp lệ (kể cả dòng tiêu đề
    trang «Guidelines and Statements» — CHỨA đúng 2 từ khoá luật cho phép,
    khớp thực tế đã đo trên trang ACC/AHA thật 09/09/2026), loại dòng tiếng
    Việt không có năm/từ khoá — VÀ cho kết quả giống hệt khi đưa CÙNG 3 dòng
    đó qua rut_tieu_de(html) (chứng minh hai đường dùng chung một tiêu chí)."""
    ba_dong = {
        "Trang chủ Guidelines and Statements",
        "2026 Guideline for the Prevention of Stroke in Patients With Stroke",
        "Fifth Universal Definition of Myocardial Infarction (2026)",
    }
    tu_van_ban = G.rut_tieu_de_tu_van_ban(VAN_BAN_CO_TIEU_DE)
    assert tu_van_ban == ba_dong
    tu_html = G.rut_tieu_de("".join(f"<h2>{d}</h2>" for d in ba_dong))
    assert tu_van_ban == tu_html


# Trang thật ACC/AHA 09/09/2026 (rút gọn) — lần chạy đầu KHÔNG lọc rác cho
# 20/20 dòng "qua", 17 là rác. Fixture này tái hiện ĐÚNG ca đó để khoá bản vá.
VAN_BAN_TRANG_THAT_LAN_ACC_AHA = """Title: Guidelines and Statements - Professional Heart Daily | American Heart Association
URL: https://professional.heart.org
Source element: <main>
---
Home Guidelines and Statements
Guidelines & Statements
About Guidelines & Statements

Heart Disease and Stroke Statistics — 2026 Update
2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack
A Guideline From the American Heart Association/American Stroke Association
Guidelines Pocketcards
FEATURED NEWS
Sep 08, 2026 | Circulation
ESC 2026 Science News
Aug 31, 2026
Fifth Universal Definition of Myocardial Infarction (2026)
Aug 28, 2026 | Circulation
Search Guidelines and Statements

Tab Context:
- Executed on tabId: seed
- Available tabs:
  • tabId seed: "Guidelines and Statements" (https://professional.heart.org)
"""


def test_rut_tieu_de_tu_van_ban_loc_rac_trang_that_09_09() -> None:
    """Ca thật đo được khi vá: dòng khung get_page_text (Title:/URL:/---/Tab
    Context:/tabId…) và dòng <4 từ (ngày-tháng đơn độc, breadcrumb, nhãn nút)
    phải bị loại — chỉ còn tiêu đề guideline/statement thật."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_LAN_ACC_AHA)
    assert ket == {
        "Heart Disease and Stroke Statistics — 2026 Update",
        "2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack",
        "A Guideline From the American Heart Association/American Stroke Association",
        "Fifth Universal Definition of Myocardial Infarction (2026)",
    }
    # Rác đã bị loại — khẳng định TƯỜNG MINH, không chỉ suy từ độ dài tập kết quả.
    rac = {"Home Guidelines and Statements", "Guidelines & Statements",
           "About Guidelines & Statements", "Guidelines Pocketcards",
           "Sep 08, 2026 | Circulation", "ESC 2026 Science News",
           "Aug 31, 2026", "Aug 28, 2026 | Circulation",
           "Search Guidelines and Statements"}
    assert not (ket & rac)


def _don_dep(monkeypatch, tmp_path: Path) -> Path:
    """Trỏ 3 đường dẫn module-level (SO_NGUON/STATE/RA) vào tmp_path — không
    đụng file dự án thật khi chạy test."""
    so_nguon = tmp_path / "sources.json"
    monkeypatch.setattr(G, "SO_NGUON", so_nguon)
    monkeypatch.setattr(G, "STATE", tmp_path / "state" / "giam-sat-to-chuc.json")
    monkeypatch.setattr(G, "RA", tmp_path / "surveillance")
    return so_nguon


def test_nap_van_ban_qua_ngan_khong_ghi_gi(monkeypatch, tmp_path: Path) -> None:
    """Nội dung <200 ký tự (trang chưa tải xong/bị chặn) phải KHÔNG ghi gì —
    tránh hiểu nhầm 'chặn' thành 'không có tin mới' (họ lỗi BH08/BH27)."""
    so_nguon = _don_dep(monkeypatch, tmp_path)
    du = {"sources": [_nguon("SRC-X", status="not-covered")]}
    so_nguon.write_text(json.dumps(du), encoding="utf-8")
    ngan = tmp_path / "ngan.txt"
    ngan.write_text("quá ngắn", encoding="utf-8")
    ma = G._nap_van_ban("SRC-X", str(ngan))
    assert ma == 2
    assert json.loads(so_nguon.read_text())["sources"][0]["status"] == "not-covered"
    assert not G.STATE.exists()


def test_nap_van_ban_id_khong_ton_tai(monkeypatch, tmp_path: Path) -> None:
    so_nguon = _don_dep(monkeypatch, tmp_path)
    so_nguon.write_text(json.dumps({"sources": []}), encoding="utf-8")
    f = tmp_path / "noi_dung.txt"
    f.write_text(VAN_BAN_CO_TIEU_DE * 20, encoding="utf-8")
    assert G._nap_van_ban("KHONG-CO", str(f)) == 2


def test_nap_van_ban_bat_not_covered_va_ghi_ung_vien(monkeypatch, tmp_path: Path) -> None:
    """Đường chính: trạm not-covered, nội dung đủ dài có tiêu đề mới ⇒ tự BẬT
    active + ghi state + ghi file ứng viên đánh dấu 'nạp qua Browser thật'."""
    so_nguon = _don_dep(monkeypatch, tmp_path)
    du = {"sources": [_nguon("SRC-015", status="not-covered")]}
    du["sources"][0]["org"] = "ACC/AHA"
    so_nguon.write_text(json.dumps(du), encoding="utf-8")
    f = tmp_path / "noi_dung.txt"
    f.write_text(VAN_BAN_CO_TIEU_DE * 5, encoding="utf-8")

    ma = G._nap_van_ban("SRC-015", str(f))
    assert ma == 1

    du2 = json.loads(so_nguon.read_text())
    s2 = du2["sources"][0]
    assert s2["status"] == "active"
    assert s2["kich_hoat"]["so_tieu_de_luc_do"] == 3
    assert "Browser" in s2["kich_hoat"]["bang"]
    assert s2["last_success_at"] == G.date.today().isoformat()

    state = json.loads(G.STATE.read_text())
    assert len(state["SRC-015"]["titles"]) == 3

    file_ung_vien = list(G.RA.glob("to-chuc-*.md"))
    assert len(file_ung_vien) == 1
    noi_dung_file = file_ung_vien[0].read_text()
    assert "ACC/AHA" in noi_dung_file and "nạp qua Browser thật" in noi_dung_file


def test_nap_van_ban_nhieu_tram_cung_ngay_khong_de_ghi_de(monkeypatch, tmp_path: Path) -> None:
    """Vá 13/09/2026: gọi --nap-van-ban cho HAI trạm khác nhau trong CÙNG một
    ngày (ca thật xảy ra khi nạp lần lượt GOLD/GINA/KDIGO/ADA/ESC cùng buổi)
    trước đây làm file to-chuc-<ngày>.md bị GHI ĐÈ — chỉ trạm chạy SAU CÙNG
    còn xuất hiện, dù state/giam-sat-to-chuc.json vẫn lưu đúng cho cả hai.
    Nay file phải GIỮ ứng viên của CẢ HAI trạm."""
    so_nguon = _don_dep(monkeypatch, tmp_path)
    du = {"sources": [_nguon("SRC-A", status="not-covered"),
                      _nguon("SRC-B", status="not-covered")]}
    du["sources"][0]["org"] = "GOLD"
    du["sources"][1]["org"] = "ESC"
    so_nguon.write_text(json.dumps(du), encoding="utf-8")
    fa = tmp_path / "a.txt"
    fa.write_text(VAN_BAN_CO_TIEU_DE * 5, encoding="utf-8")
    fb = tmp_path / "b.txt"
    fb.write_text(VAN_BAN_TRANG_THAT_LAN_ACC_AHA * 5, encoding="utf-8")

    G._nap_van_ban("SRC-A", str(fa))
    G._nap_van_ban("SRC-B", str(fb))

    file_ung_vien = list(G.RA.glob("to-chuc-*.md"))
    assert len(file_ung_vien) == 1
    noi_dung_file = file_ung_vien[0].read_text()
    assert "GOLD" in noi_dung_file, "ứng viên của trạm CHẠY TRƯỚC bị mất — đúng lỗi đã vá"
    assert "ESC" in noi_dung_file


def test_nap_van_ban_da_active_khong_ghi_de_kich_hoat(monkeypatch, tmp_path: Path) -> None:
    """Trạm ĐÃ active thì lần nạp sau chỉ cập nhật state, KHÔNG được tự thêm
    khối kich_hoat mới (đó là bằng chứng của LẦN BẬT ĐẦU TIÊN, không phải mỗi
    lần quét) — cùng luật bat_neu_ok đã khoá cho DA-BAT ở test phía trên."""
    so_nguon = _don_dep(monkeypatch, tmp_path)
    du = {"sources": [_nguon("SRC-015", status="active")]}
    du["sources"][0]["org"] = "ACC/AHA"
    so_nguon.write_text(json.dumps(du), encoding="utf-8")
    f = tmp_path / "noi_dung.txt"
    f.write_text(VAN_BAN_CO_TIEU_DE * 5, encoding="utf-8")

    G._nap_van_ban("SRC-015", str(f))
    s2 = json.loads(so_nguon.read_text())["sources"][0]
    assert s2["status"] == "active"
    assert "kich_hoat" not in s2
