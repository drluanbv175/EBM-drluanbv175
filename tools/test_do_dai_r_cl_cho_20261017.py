"""Dòng «R-CL-CHO» của Đài hoàn thiện (17/10/2026) — nhiệm vụ chưa tới lượt đánh giá chéo tách khỏi R-CL.

Bác sĩ chọn «tách dòng chưa tới lượt»: G6-T3/G7-T2 của C1a chưa có đầu ra nên không chấm chéo được trước 2027. Test chốt:
① có nhiệm vụ chưa tới lượt ⇒ trạng thái «cho» (Chờ cổng trước), liệt kê mã — không phải «đạt»;
② không còn ⇒ «đạt»; ③ công cụ y khoa cũ thiếu khoá ⇒ «không đo được», không bao giờ coi là 0;
④ `do_cong` rút mã từ danh sách đối tượng, vắng khoá ⇒ None.
Ngoại tuyến: mọi lệnh đo con được thay bằng hàm giả.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import do_dai_hoan_thien as D  # noqa: E402


def _cong(gate, toi_luot):
    return {"cong": gate, "dieu_phoi": f"dieu-phoi-{gate.lower()}", "trang_thai_song": "BLOCKED",
            "ket_luan": "CHO_CONG_TRUOC", "tieu_chi_dat": 0, "tieu_chi": 1, "agent_con_viec": 0, "cho_nguoi": 0,
            "cho_cong_truoc": 1, "nhiem_vu_ap_dung": 1, "danh_gia_cheo_hieu_luc": 0, "chat_luong_chua_bao_dam": 0,
            "chat_luong_chua_toi_luot": toi_luot}


@pytest.fixture
def mu(monkeypatch, tmp_path):
    monkeypatch.setattr(D, "_chay", lambda *a, **k: None)
    return tmp_path


def _dong(mu, cong):
    return {h["ma"]: h for h in D.thuoc_do(mu, mu, cong, [], [])}["R-CL-CHO"]


def test_con_nhiem_vu_chua_toi_luot_la_cho_khong_phai_dat(mu):
    h = _dong(mu, [_cong("G6", ["G6-T3"]), _cong("G7", ["G7-T2"]), _cong("G10", [])])
    assert (h["hien_tai"], h["so"], h["trang_thai"], h["nhan"]) == ("G6-T3, G7-T2", 2, "cho", "Chờ cổng trước")


def test_khong_con_thi_dat(mu):
    h = _dong(mu, [_cong("G6", []), _cong("G10", [])])
    assert (h["hien_tai"], h["trang_thai"]) == ("0", "dat")


def test_cong_cu_cu_thieu_khoa_la_khong_do_duoc(mu):
    h = _dong(mu, [_cong("G6", None), _cong("G10", [])])
    assert h["trang_thai"] == "khong_do" and h["so"] is None


def test_do_cong_rut_ma_va_vang_khoa_la_none(monkeypatch, tmp_path):
    bang = {"cong": [
        {"gate": "G6", "ket_luan": "CHO_CONG_TRUOC", "nhiem_vu": [],
         "chat_luong_chua_toi_luot": [{"ma": "G6-T3", "agent": "dien-giai-ket-qua", "ly_do": "chưa có đầu ra: x"}]},
        {"gate": "G1", "ket_luan": "DAT_TIEU_CHI", "nhiem_vu": []}]}
    monkeypatch.setattr(D, "_chay", lambda *a, **k: json.dumps(bang))
    hang = {h["cong"]: h for h in D.do_cong(tmp_path, "S")}
    assert hang["G6"]["chat_luong_chua_toi_luot"] == ["G6-T3"]
    assert hang["G1"]["chat_luong_chua_toi_luot"] is None
