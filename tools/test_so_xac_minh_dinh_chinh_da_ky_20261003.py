"""Báo cáo sổ xác minh tách «bản đính chính bị rút» ĐÃ KÝ / CHƯA KÝ khỏi «rút thật» (03/10/2026).

Đo cùng ngày: hai nguồn CCS/CHFS 2025 (bác sĩ ký 24/09, cổng verify_dashboard PASS) vẫn in dưới «🔴 ĐÃ BỊ RÚT — không dùng
kết luận» ⇒ báo động giả xui bỏ một guideline hợp lệ. Dòng ĐẾM «ĐÃ BỊ RÚT : N» phải giữ nghĩa cũ (tu_de_xuat_viec dựa vào nó).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("sxmn_dc_t", TOOLS / "so_xac_minh_nguon.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def _bg(**kw) -> dict:
    g = {"da_rut": True, "cac_dashboard": ["WebDashboard_X.html"], "ghi_chu_rut": "retracted", "loai": "pmid"}
    g.update(kw)
    return g


def _dung_so(tmp_path: Path, monkeypatch, ky: list[dict]) -> None:
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    so = {"muc": {
        "pmid:111": _bg(gia_tri="111"),                                                   # rút thật
        "pmid:222": _bg(gia_tri="222", sua_loi_bi_rut=True, thong_bao_ids=["999"]),         # đính chính, ĐÃ ký
        "pmid:333": _bg(gia_tri="333", sua_loi_bi_rut=True, thong_bao_ids=["888"]),         # đính chính, CHƯA ký
    }}
    (dash / ".so-xac-minh-nguon.json").write_text(json.dumps(so), encoding="utf-8")
    (dash / "rut-bai-da-xem-xet.json").write_text(json.dumps({"muc": ky}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(S, "DASH", dash)
    monkeypatch.setattr(S, "SO", dash / ".so-xac-minh-nguon.json")


KY_222 = {"khoa": "pmid:222", "thong_bao_ids": ["999"], "da_xem_boi": "Bác sĩ thử", "ngay": "2026-09-24",
          "ly_do": "Đã đọc thông báo rút bản đính chính và Author Correction; không đổi khuyến cáo đang dùng."}


def test_tach_ba_nhom_va_giu_dong_dem(tmp_path, monkeypatch, capsys) -> None:
    _dung_so(tmp_path, monkeypatch, [KY_222])
    S.bao_cao()
    ra = capsys.readouterr().out
    assert "ĐÃ BỊ RÚT    : 3" in ra, "dòng đếm phải giữ nghĩa cũ (gồm cả ca đính chính)"
    i_that = ra.index("🔴 NGUỒN ĐÃ BỊ RÚT")
    i_cho = ra.index("🔴 CẦN BÁC SĨ XEM")
    i_ky = ra.index("✅ BẢN ĐÍNH CHÍNH bị rút — bác sĩ ĐÃ KÝ")
    assert "pmid:111" in ra[i_that:i_cho] and "pmid:222" not in ra[i_that:i_cho]
    assert "pmid:333" in ra[i_cho:i_ky]
    assert "pmid:222" in ra[i_ky:]


def test_vay_tay_lech_thi_khong_tinh_la_da_ky(tmp_path, monkeypatch, capsys) -> None:
    _dung_so(tmp_path, monkeypatch, [dict(KY_222, thong_bao_ids=["000"])])
    S.bao_cao()
    ra = capsys.readouterr().out
    assert "✅ BẢN ĐÍNH CHÍNH" not in ra
    assert "pmid:222" in ra[ra.index("🔴 CẦN BÁC SĨ XEM"):]


def test_khong_nap_duoc_cong_thi_coi_nhu_chua_ky(tmp_path, monkeypatch, capsys) -> None:
    _dung_so(tmp_path, monkeypatch, [KY_222])
    monkeypatch.setattr(S, "REPO", tmp_path / "khong-co-repo")
    S.bao_cao()
    ra = capsys.readouterr().out
    assert "✅ BẢN ĐÍNH CHÍNH" not in ra and "pmid:222" in ra[ra.index("🔴 CẦN BÁC SĨ XEM"):]
