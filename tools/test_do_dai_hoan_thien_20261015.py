"""Test `do_dai_hoan_thien.py` (15/10/2026) — trang Đài hoàn thiện không bao giờ báo xanh giả.

Ngoại tuyến: mọi lệnh đo con được thay bằng hàm giả; không gọi gh, không chạy công cụ thật.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import do_dai_hoan_thien as D  # noqa: E402

GOC = Path(__file__).resolve().parents[1]


def _cong(gate, song, ket_luan, clcb=0):
    return {"cong": gate, "dieu_phoi": f"dieu-phoi-{gate.lower()}", "trang_thai_song": song, "ket_luan": ket_luan,
            "tieu_chi_dat": 1, "tieu_chi": 1, "agent_con_viec": 0, "cho_nguoi": 0, "cho_cong_truoc": 0,
            "nhiem_vu_ap_dung": 1, "danh_gia_cheo_hieu_luc": 0, "chat_luong_chua_bao_dam": clcb}


@pytest.fixture
def mu(monkeypatch, tmp_path):
    """Mọi lệnh đo con «không chạy được» và state/ trống — giả lập máy thiếu công cụ/mạng."""
    monkeypatch.setattr(D, "_chay", lambda *a, **k: None)
    return tmp_path


def test_khong_do_duoc_khong_bao_gio_la_dat(mu):
    hang = D.thuoc_do(mu, mu / "medical-ebm-automation", [], [], [])
    assert hang, "phải có dòng cho từng thước đo dù không đo được"
    assert all(h["trang_thai"] == "khong_do" for h in hang), [h for h in hang if h["trang_thai"] != "khong_do"]


def test_bang_viec_rong_khong_suy_ra_so_khong(mu):
    hang = {h["ma"]: h for h in D.thuoc_do(mu, mu, [], [], [])}
    for ma in ("E-MOI", "E-THE", "E-NGOAI"):
        assert hang[ma]["trang_thai"] == "khong_do"


def test_dem_cong_cung_co_chu_ky_va_cong_con_viec(mu):
    cong = [_cong("G2", "PASS_G2_APPROVED", "DAT_TIEU_CHI"), _cong("G4", "READY_FOR_SIGNATURE", "AGENT_XONG_CHO_NGUOI"),
            _cong("G5", "LOCKED", "DAT_TIEU_CHI"), _cong("G8", "BLOCKED", "CHO_CONG_TRUOC", clcb=2),
            _cong("G9", "BLOCKED", "CHO_CONG_TRUOC"), _cong("G10", "DRAFT_ASSEMBLED_NEEDS_COMPLETION", "AGENT_CON_VIEC")]
    hang = {h["ma"]: h for h in D.thuoc_do(mu, mu, cong, [], [])}
    assert hang["R-KY"]["hien_tai"] == "2/6" and hang["R-KY"]["trang_thai"] == "chua"
    assert hang["R-AGENT"]["hien_tai"] == "G10" and hang["R-AGENT"]["trang_thai"] == "chua"
    assert hang["R-CL"]["so"] == 2


def test_so_lay_tu_bang_viec(mu):
    viec = [{"viec": "117 mục 'apply' có nguồn tổng hợp MỚI HƠN — bản đặt-cạnh sẵn"},
            {"viec": "6/6 thẻ gói tuan-2026-W42 chưa ghi quyết định của bác sĩ (3 ngày)"}]
    hang = {h["ma"]: h for h in D.thuoc_do(mu, mu, [], viec, [])}
    assert hang["E-MOI"]["so"] == 117 and hang["E-MOI"]["trang_thai"] == "chua"
    assert hang["E-THE"]["so"] == 6
    assert hang["E-NGOAI"]["so"] == 0 and hang["E-NGOAI"]["trang_thai"] == "dat"


def test_mau_cau_khop_dung_cau_chu_cua_cam_bien():
    """Mẫu tìm số phải khớp câu chữ THẬT của tu_de_xuat_viec.py — cảm biến đổi câu chữ thì test này đỏ trước,
    thay vì trang lặng lẽ báo «0 — đạt»."""
    nguon = (GOC / "tools" / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    for doan in ("mục 'apply' có nguồn tổng hợp MỚI HƠN", "chưa ghi quyết định", "lượt điểm-khám NGOÀI giám sát"):
        assert doan in nguon, doan


def test_chu_de_qua_nguong_va_ban_tin_gop(mu):
    tuoi = [{"chu_de": "A", "ngay": 130, "ban_tin_gop": False}, {"chu_de": "B", "ngay": 40, "ban_tin_gop": False},
            {"chu_de": "Tin", "ngay": 300, "ban_tin_gop": True}]
    hang = {h["ma"]: h for h in D.thuoc_do(mu, mu, [], [], tuoi)}
    assert hang["E-QUA"]["so"] == 1, "bản tin gộp không tính vào chủ đề quá hạn"
    assert hang["E-TUOI"]["so"] == 130


def test_main_ghi_du_bo_tep(monkeypatch, tmp_path):
    monkeypatch.setattr(D, "_chay", lambda *a, **k: None)
    monkeypatch.setattr(D, "do_tuoi", lambda goc: [])
    assert D.main(["--goc", str(tmp_path), "--ra", str(tmp_path / "ra")]) == 0
    for ten in ("thuoc_do", "cong_c1a", "viec", "chu_de_cu", "lo_trinh", "chi_phi_token"):
        d = json.loads((tmp_path / "ra" / f"{ten}.json").read_text(encoding="utf-8"))
        assert set(d) == {"do_luc", "rows"} and isinstance(d["rows"], list)


def _han_muc_vao(tmp_path, pct5, pcttuan):
    (tmp_path / "han_muc_vao.json").write_text(json.dumps({"do_luc": "2026-10-15T21:00:00+07:00", "windows": [
        {"label": "5-hour limit", "percentUsed": pct5, "resetsAt": "2026-10-15T14:50:00Z"},
        {"label": "Weekly · all models", "percentUsed": pcttuan, "resetsAt": "2026-10-17T20:00:00Z"}]}),
        encoding="utf-8", newline="\n")


def test_han_muc_theo_nguong(tmp_path):
    _han_muc_vao(tmp_path, 74, 64)
    h = {r["loai"]: r for r in D.do_han_muc(tmp_path)}
    assert h["5 giờ"]["trang_thai"] == "binh_thuong" and h["tuần"]["trang_thai"] == "binh_thuong"
    _han_muc_vao(tmp_path, 90, 93)
    h = {r["loai"]: r for r in D.do_han_muc(tmp_path)}
    assert h["5 giờ"]["trang_thai"] == "hoan_viec_nang" and h["tuần"]["trang_thai"] == "dung"


def test_han_muc_vang_la_khong_do(tmp_path):
    h = D.do_han_muc(tmp_path)
    assert len(h) == 1 and h[0]["trang_thai"] == "khong_do"


def test_ghi_tien_do_chi_noi_them_va_moi_nhat_truoc(tmp_path):
    _han_muc_vao(tmp_path, 74, 64)
    hm = D.do_han_muc(tmp_path)
    D.ghi_tien_do(tmp_path, "Nghiên cứu|Kéo cây y khoa|Hết lệch BH107", hm, "2026-10-15T21:00:00+07:00")
    D.ghi_tien_do(tmp_path, "Chứng cứ lâm sàng|Dựng lại RAG|Chỉ mục mới", hm, "2026-10-15T21:05:00+07:00")
    td = D.doc_tien_do(tmp_path)
    assert [r["viec"] for r in td] == ["Dựng lại RAG", "Kéo cây y khoa"]
    assert td[0]["han_muc_5h"] == 74 and td[0]["ma"] == "T002"
    with pytest.raises(ValueError):
        D.ghi_tien_do(tmp_path, "thiếu|phần", hm, "x")
    assert len((tmp_path / "tien_do.jsonl").read_text(encoding="utf-8").splitlines()) == 2


def test_main_bao_tep_doi(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(D, "_chay", lambda *a, **k: None)
    monkeypatch.setattr(D, "do_tuoi", lambda goc: [])
    ra = tmp_path / "ra"
    D.main(["--goc", str(tmp_path), "--ra", str(ra)])
    capsys.readouterr()
    D.main(["--goc", str(tmp_path), "--ra", str(ra), "--ghi-tien-do", "Nền hệ thống|Thử|Xong"])
    out = capsys.readouterr().out
    assert "tien_do.json" in out and "thuoc_do.json" not in out.split("Tệp đổi")[1]
