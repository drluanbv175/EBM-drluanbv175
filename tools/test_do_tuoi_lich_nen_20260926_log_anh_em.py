"""Độ tươi chứng cứ đọc log giám sát ở repo y khoa ANH EM; không xanh giả khi không đo được — 26/09/2026 (#35).

  • kiem_do_tuoi_chung_cu: bố cục anh em có log PASS ⇒ KHÔNG còn «CHƯA TỪNG chạy» (bản cũ viết cứng
    đường lồng ⇒ đỏ giả); không gói chứng cứ + không repo y khoa ⇒ tiêu đề ⚪, KHÔNG 🟢, mã 0.
  • kiem_lich_nen: ok == 0 ⇒ tiêu đề KHÔNG có 🟢 (mã 0 giữ nguyên cho tu_khoi_dong); và CỐ Ý không dò
    log anh em (bộ lập lịch chỉ sống trên Mac — đọc log anh em trên Cloud là đo nhầm máy ⇒ đỏ giả).

Ngoại tuyến: chép công cụ vào cây tạm để `REPO = Path(__file__).parents[1]` trỏ vào đó.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent


def _cay_tam(tmp_path: Path, anh_em_log: str | None, co_yk: bool = True) -> Path:
    """Dựng tmp/goc/tools/<công cụ> + (tuỳ chọn) tmp/medical-ebm-automation ANH EM có log tuần."""
    goc = tmp_path / "goc"
    (goc / "tools").mkdir(parents=True)
    for ten in ("kiem_do_tuoi_chung_cu.py", "ban_sao_tran.py", "nhan_dien_may.py"):
        shutil.copy2(_TOOLS / ten, goc / "tools" / ten)
    if co_yk:
        arch = tmp_path / "medical-ebm-automation" / "data" / "archive"
        arch.mkdir(parents=True)
        if anh_em_log is not None:
            (arch / "launchd_weekly.log").write_text(anh_em_log, encoding="utf-8")
    return goc


def _nap_ban_chep(goc: Path, bi_danh: str):
    sp = importlib.util.spec_from_file_location(bi_danh, goc / "tools" / "kiem_do_tuoi_chung_cu.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _log_pass(ngay: dt.date) -> str:
    return (f"===== {ngay:%Y-%m-%d} 18:00:01 : BẮT ĐẦU giám sát tuần\n"
            f"===== {ngay:%Y-%m-%d} 18:20:44 : KẾT THÚC tổng thể=PASS\n")


@pytest.fixture(autouse=True)
def _khong_cloud(monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)


def test_log_anh_em_duoc_doc_khong_con_chua_tung_chay(tmp_path, monkeypatch, capsys):
    goc = _cay_tam(tmp_path, _log_pass(dt.date.today() - dt.timedelta(days=2)))
    K = _nap_ban_chep(goc, "kdtcc_anh_em_pass")
    assert K.LOG_TUAN == tmp_path / "medical-ebm-automation" / "data" / "archive" / "launchd_weekly.log"
    monkeypatch.setattr(sys, "argv", ["kiem_do_tuoi_chung_cu.py"])
    rc = K.main()
    out = capsys.readouterr().out
    assert "CHƯA TỪNG" not in out, out
    assert rc == 0
    # Có số đo (log PASS) ⇒ 🟢 hợp lệ; gói chứng cứ vắng vẫn được NÓI ra bằng dòng ⚪.
    assert "🟢 HỆ GIÁM SÁT còn hoạt động" in out
    assert "⚪ Gói chứng cứ/tuổi chủ đề: KHÔNG đo được" in out


def test_anh_em_khong_co_log_van_bao_chua_tung_chay_voi_lenh_dung_duong(tmp_path, monkeypatch, capsys):
    """Đối chứng: repo y khoa anh em CÓ mặt nhưng log thật sự vắng ⇒ cảnh báo thật vẫn còn, và lệnh
    chạy bù trỏ đúng script của repo anh em (không phải đường tương đối viết cứng)."""
    goc = _cay_tam(tmp_path, None)
    K = _nap_ban_chep(goc, "kdtcc_anh_em_vang")
    monkeypatch.setattr(sys, "argv", ["kiem_do_tuoi_chung_cu.py"])
    rc = K.main()
    out = capsys.readouterr().out
    assert rc == 1 and "CHƯA TỪNG chạy" in out
    assert str(tmp_path / "medical-ebm-automation" / "scripts" / "weekly_safety.sh") in out


@pytest.mark.parametrize("im", [False, True])
def test_khong_do_duoc_gi_la_tieu_de_trang_khong_xanh(tmp_path, monkeypatch, capsys, im):
    """Bố cục một-repo (không EBM-Dashboards, không repo y khoa): không đo được mục nào ⇒ ⚪, mã 0."""
    goc = _cay_tam(tmp_path, None, co_yk=False)
    K = _nap_ban_chep(goc, f"kdtcc_mot_repo_{int(im)}")
    monkeypatch.setattr(sys, "argv", ["kiem_do_tuoi_chung_cu.py"] + (["--im-khi-on"] if im else []))
    rc = K.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "🟢" not in out
    if im:
        assert out == ""        # hook giữ im lặng như cũ khi không có gì quá hạn
    else:
        assert "⚪ HỆ GIÁM SÁT: KHÔNG đo được" in out
        assert "EBM-Dashboards/ vắng" in out


# ---------- kiem_lich_nen ----------

def _nap_kln():
    sp = importlib.util.spec_from_file_location("kln_20260926", _TOOLS / "kiem_lich_nen.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


@pytest.mark.parametrize("khong_do_duoc", [["thu-thap-tuan: không đọc được log"], []])
def test_lich_nen_ok_0_khong_co_xanh(monkeypatch, capsys, khong_do_duoc):
    L = _nap_kln()
    monkeypatch.setattr(L, "kiem", lambda: {"phat_hien": [], "khong_do_duoc": khong_do_duoc, "ok": 0})
    rc = L.main([])
    out = capsys.readouterr().out
    assert rc == 0                               # tu_khoi_dong coi mã ngoài {0,1} là cảm biến lỗi
    assert "🟢" not in out
    assert out.startswith("⚪ Lịch nền: KHÔNG đo được")


def test_lich_nen_co_tac_vu_do_duoc_van_xanh(monkeypatch, capsys):
    L = _nap_kln()
    monkeypatch.setattr(L, "kiem", lambda: {"phat_hien": [], "khong_do_duoc": ["x"], "ok": 2})
    assert L.main([]) == 0
    assert capsys.readouterr().out.startswith("🟢 Mọi kỳ lịch nền đến hạn đều có dấu vết đúng hẹn (2 tác vụ")


def test_lich_nen_ok_0_im_khi_on_van_im(monkeypatch, capsys):
    L = _nap_kln()
    monkeypatch.setattr(L, "kiem", lambda: {"phat_hien": [], "khong_do_duoc": ["x"], "ok": 0})
    assert L.main(["--im-khi-on"]) == 0
    assert capsys.readouterr().out == ""


def test_lich_nen_khong_do_log_anh_em(tmp_path):
    """Log ở repo y khoa ANH EM chỉ chứa lượt chạy tay (Cloud) — cảm biến KHÔNG được đọc nó (đo nhầm máy)."""
    L = _nap_kln()
    goc = tmp_path / "goc"
    goc.mkdir()
    arch = tmp_path / "medical-ebm-automation" / "data" / "archive"
    arch.mkdir(parents=True)
    (arch / "launchd_weekly.log").write_text(
        "===== 2026-09-24 10:11:12 : KẾT THÚC tổng thể=PASS\n", encoding="utf-8")
    so_khai = {"cua_so_ngay": 21, "tac_vu": [{
        "id": "thu-thap-tuan-an-toan-thuoc", "cron": "0 18 * * 1", "tu_ngay": "2026-09-01",
        "grace_gio": 30,
        "dau_vet": {"loai": "log-ket-thuc", "path": "medical-ebm-automation/data/archive/launchd_weekly.log"}}]}
    kq = L.kiem(hom_nay=dt.datetime(2026, 9, 26, 12, 0), so_khai=so_khai, goc=goc)
    assert kq["phat_hien"] == [], "đọc log anh em ⇒ «kỳ không nổ đúng hẹn» cho nhầm máy (đỏ giả)"
    assert kq["ok"] == 0 and len(kq["khong_do_duoc"]) == 1
