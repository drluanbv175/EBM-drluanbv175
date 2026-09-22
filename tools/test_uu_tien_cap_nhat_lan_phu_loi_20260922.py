"""Vá 22/09/2026 (phản biện vòng 2, review:thu-nhan #10, LOW).

Một chủ đề `status=PASS` (nguồn PubMed chính sạch) nhưng có làn phụ (preprint/clinicaltrials/
scopus) hỏng vẫn có thể có 0 ứng viên — trước đây bị gộp chung vào nhóm "KHÔNG có chứng cứ mới,
chưa cần đụng" giống hệt một chủ đề THẬT SỰ sạch cả 4 làn. Nay tách riêng thành nhóm cảnh báo.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "tools" / "uu_tien_cap_nhat.py"
_sp = importlib.util.spec_from_file_location("uu_tien_lan_phu_test", NGUON)
M = importlib.util.module_from_spec(_sp)
sys.modules["uu_tien_lan_phu_test"] = M
_sp.loader.exec_module(M)


class _FakeTuoi:
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


def test_pass_lan_phu_hong_tach_khoi_nhom_sach_that(monkeypatch, capsys):
    du = {
        "status": "PASS",
        "candidate_count": 0,
        "days": 75,
        "topics": [
            {"topic": "Watchlist A", "status": "PASS", "candidates": [], "lan_phu_loi": ["scopus", "preprint"]},
            {"topic": "Watchlist B", "status": "PASS", "candidates": []},  # sạch THẬT — không có lan_phu_loi
        ],
    }
    bando = {"A": "Watchlist A", "B": "Watchlist B"}
    out = _chay(monkeypatch, capsys, du, bando)

    assert "làn TÍN HIỆU SỚM NHẤT" in out
    canh_bao = out.split("làn TÍN HIỆU SỚM NHẤT")[1]
    assert "A" in canh_bao and "scopus" in canh_bao and "preprint" in canh_bao

    sach_that = out.split("KHÔNG có chứng cứ mới")[1].split("⚪")[0]
    assert "B" in sach_that
    assert "A" not in sach_that.split("·"), "chủ đề có làn phụ hỏng không được lẫn vào nhóm sạch thật"


def test_khong_co_lan_phu_loi_khong_in_dong_canh_bao_moi(monkeypatch, capsys):
    du = {
        "status": "PASS",
        "candidate_count": 0,
        "days": 75,
        "topics": [{"topic": "Watchlist A", "status": "PASS", "candidates": []}],
    }
    bando = {"A": "Watchlist A"}
    out = _chay(monkeypatch, capsys, du, bando)
    assert "làn TÍN HIỆU SỚM NHẤT" not in out


def test_chu_de_fail_van_o_nhom_chua_do_khong_lan_sang_nhom_lan_phu(monkeypatch, capsys):
    """Đối chứng: chủ đề FAIL/DEGRADED (đã có nhóm riêng từ #6) không được rơi vào nhóm
    "lan_phu_loi" mới — dù bản thân FAIL cũng có thể mang lan_phu_loi rỗng hoặc không."""
    du = {
        "status": "PARTIAL",
        "candidate_count": 0,
        "days": 75,
        "topics": [{"topic": "Watchlist A", "status": "FAIL", "candidates": [], "lan_phu_loi": []}],
    }
    bando = {"A": "Watchlist A"}
    out = _chay(monkeypatch, capsys, du, bando)
    assert "CHƯA ĐO ĐƯỢC" in out
    assert "làn TÍN HIỆU SỚM NHẤT" not in out
