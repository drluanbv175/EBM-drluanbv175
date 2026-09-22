"""Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #6, MEDIUM).

`uu_tien_cap_nhat.py` trước đây đọc trạng thái lượt quét CHỈ Ở MỨC TOÀN CỤC (dòng cảnh
báo khi `status != PASS`) — nhưng danh sách "0 chủ đề mới ⇒ chưa cần đụng" đọc SỐ ỨNG
VIÊN theo TỪNG chủ đề mà bỏ qua trạng thái riêng của chủ đề đó. Một chủ đề FAIL/
PASS_DEGRADED với 0 ứng viên bị in chung với chủ đề PASS 0 ứng viên — đúng cách đọc
"0 GIẢ" mà PASS_DEGRADED sinh ra để ngăn.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "tools" / "uu_tien_cap_nhat.py"
_sp = importlib.util.spec_from_file_location("uu_tien_v2_test", NGUON)
M = importlib.util.module_from_spec(_sp)
sys.modules["uu_tien_v2_test"] = M
_sp.loader.exec_module(M)


class _FakeTuoi:
    """Thay `kiem_do_tuoi_chung_cu` để test không phụ thuộc kho dashboard thật."""

    @staticmethod
    def lau_chua_xem_lai():
        return [("A_20260101", 40), ("B_20260101", 40), ("C_20260101", 40)]


def _chay(monkeypatch, capsys, du: dict, bando: dict) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp)
        bando_file = tmp_p / "giam-sat-chu-de.json"
        bando_file.write_text(json.dumps({"muc": bando}), encoding="utf-8")
        du_file = tmp_p / "quet.json"
        du_file.write_text(json.dumps(du), encoding="utf-8")

        monkeypatch.setattr(M, "BANDO", bando_file)
        monkeypatch.setattr(M, "_nap", lambda *a, **k: _FakeTuoi)
        monkeypatch.setattr(sys, "argv", ["uu_tien_cap_nhat.py", "--tu-json", str(du_file)])
        rc = M.main()
        assert rc == 0
    return capsys.readouterr().out


def test_chu_de_fail_0_ung_vien_khong_bi_goi_la_khong_co_gi_moi(monkeypatch, capsys):
    du = {
        "status": "PARTIAL",
        "candidate_count": 0,
        "days": 75,
        "topics": [
            {"topic": "Watchlist A", "status": "FAIL", "candidates": []},
            {"topic": "Watchlist B", "status": "PASS_DEGRADED", "candidates": []},
            {"topic": "Watchlist C", "status": "PASS", "candidates": []},
        ],
    }
    bando = {"A": "Watchlist A", "B": "Watchlist B", "C": "Watchlist C"}
    out = _chay(monkeypatch, capsys, du, bando)

    # C (PASS thật, 0 ứng viên) vẫn được nói là "không có gì mới"
    assert "KHÔNG có chứng cứ mới" in out
    assert "C" in out.split("KHÔNG có chứng cứ mới")[1].split("Số ứng viên")[0]

    # A (FAIL) và B (PASS_DEGRADED) phải nằm ở nhóm CẢNH BÁO riêng, không lẫn vào "không có gì mới"
    assert "CHƯA ĐO ĐƯỢC" in out
    canh_bao = out.split("CHƯA ĐO ĐƯỢC")[1]
    assert "A (FAIL)" in canh_bao
    assert "B (PASS_DEGRADED)" in canh_bao
    # A/B không được xuất hiện trong dòng "không có gì mới" (đọc TRƯỚC dòng cảnh báo)
    khong_co_gi_moi = out.split("KHÔNG có chứng cứ mới")[1].split("⚠")[0]
    assert "A" not in khong_co_gi_moi.split("·")
    assert "B" not in khong_co_gi_moi.split("·")


def test_tat_ca_pass_khong_in_dong_canh_bao_chua_do_duoc(monkeypatch, capsys):
    du = {
        "status": "PASS",
        "candidate_count": 0,
        "days": 75,
        "topics": [
            {"topic": "Watchlist A", "status": "PASS", "candidates": []},
        ],
    }
    bando = {"A": "Watchlist A"}
    out = _chay(monkeypatch, capsys, du, bando)
    assert "CHƯA ĐO ĐƯỢC" not in out
    assert "KHÔNG có chứng cứ mới" in out


def test_chu_de_co_ung_vien_van_hien_binh_thuong(monkeypatch, capsys):
    du = {
        "status": "PASS",
        "candidate_count": 2,
        "days": 75,
        "topics": [
            {"topic": "Watchlist A", "status": "PASS",
             "candidates": [{"pmid": "1"}, {"pmid": "2"}]},
        ],
    }
    bando = {"A": "Watchlist A"}
    out = _chay(monkeypatch, capsys, du, bando)
    assert "CHƯA ĐO ĐƯỢC" not in out
    assert "KHÔNG có chứng cứ mới" not in out
    assert "Watchlist A" in out
