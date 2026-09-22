"""Cảm biến người chết lịch nền (T2-01/T2-04, 20/09/2026): tính THEO TỪNG KỲ, lượt chạy tay không che kỳ lỡ."""
from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("kln_t", GOC / "tools" / "kiem_lich_nen.py")
kln = importlib.util.module_from_spec(sp)
sys.modules["kln_t"] = kln
sp.loader.exec_module(kln)

D = dt.datetime
KHAI = {"cua_so_ngay": 21, "tac_vu": [
    {"id": "thu-thap", "cron": "0 18 * * 1", "tu_ngay": "2026-08-17", "grace_gio": 30,
     "dau_vet": {"loai": "log-ket-thuc", "path": "data/weekly.log"}},
    {"id": "goi-duyet", "cron": "30 18 * * 1", "tu_ngay": "2026-08-17", "grace_gio": 30,
     "dau_vet": {"loai": "file-tuan-iso", "path": "queue/tuan-{iso_nam}-W{iso_tuan:02d}.md"}},
]}


def _dung(tmp: Path, ket_thuc: list[str], queue: list[str]):
    (tmp / "data").mkdir(exist_ok=True)
    (tmp / "queue").mkdir(exist_ok=True)
    (tmp / "data" / "weekly.log").write_text(
        "\n".join(f"===== {e} : KẾT THÚC — tổng thể=PASS =====" for e in ket_thuc) + "\n", encoding="utf-8")
    for w in queue:
        (tmp / "queue" / f"tuan-{w}.md").write_text("x", encoding="utf-8")


def test_cron_tuan_thang_quy():
    tu, den = dt.date(2026, 9, 1), dt.date(2026, 9, 30)
    assert [k.day for k in kln.cac_ky("0 18 * * 1", tu, den)] == [7, 14, 21, 28]
    assert [(k.day, k.hour, k.minute) for k in kln.cac_ky("30 18 1 * *", tu, den)] == [(1, 18, 30)]
    q = kln.cac_ky("0 19 1 1,4,7,10 *", dt.date(2026, 1, 1), dt.date(2026, 12, 31))
    assert [(k.month, k.day) for k in q] == [(1, 1), (4, 1), (7, 1), (10, 1)]


def test_moi_ky_deu_co_dau_vet_thi_xanh(tmp_path):
    _dung(tmp_path, ["2026-08-31 19:05:00", "2026-09-07 19:10:00", "2026-09-14 19:12:00"],
          ["2026-W36", "2026-W37", "2026-W38"])
    kq = kln.kiem(D(2026, 9, 16, 10), KHAI, tmp_path)
    assert kq["phat_hien"] == [] and kq["ok"] == 2


def test_ky_lo_khong_dau_vet_la_do(tmp_path):
    _dung(tmp_path, ["2026-09-07 19:10:00"], ["2026-W37"])  # kỳ 14/09 không có gì
    kq = kln.kiem(D(2026, 9, 16, 10), KHAI, tmp_path)
    ds = {p["id"]: p for p in kq["phat_hien"]}
    assert ds["thu-thap"]["uu"] == 0 and ds["goi-duyet"]["uu"] == 0 and ds["goi-duyet"]["ky"].startswith("2026-09-14")


def test_luot_chay_tay_chen_sau_khong_xoa_dau_vet_ky_lo(tmp_path):
    """Đúng ca 16/09: lượt chạy tay Thứ Tư (ngoài hạn) làm «PASS cuối» mới hơn kỳ lỡ — cảm biến cũ im, cảm biến này không."""
    _dung(tmp_path, ["2026-08-31 19:05:00", "2026-09-07 19:10:00", "2026-09-16 08:19:05"],
          ["2026-W36", "2026-W37", "2026-W38"])
    kq = kln.kiem(D(2026, 9, 20, 19), KHAI, tmp_path)
    p = [x for x in kq["phat_hien"] if x["id"] == "thu-thap" and x["ky"].startswith("2026-09-14")][0]
    assert p["muc"] == "tre" and p["uu"] == 1 and "TRỄ" in p["thong_diep"], "lượt chạy tay đã che kỳ lịch không nổ"


def test_ky_cu_lo_nhung_ky_sau_da_chay_thi_chi_vang(tmp_path):
    _dung(tmp_path, ["2026-08-31 19:05:00", "2026-09-07 19:10:00", "2026-09-21 19:05:00"],
          ["2026-W36", "2026-W37", "2026-W39"])
    kq = kln.kiem(D(2026, 9, 23, 10), KHAI, tmp_path)  # kỳ 21/09 đã quá hạn grace (30h)
    assert kq["phat_hien"] and all(p["uu"] == 2 for p in kq["phat_hien"])


def test_ky_qua_cu_ngoai_cua_so_tu_het(tmp_path):
    _dung(tmp_path, [], [])
    kq = kln.kiem(D(2026, 12, 1), {**KHAI, "cua_so_ngay": 7}, tmp_path)
    assert all(p["ky"] >= "2026-11-23" for p in kq["phat_hien"]), "kỳ lỡ ngoài cửa sổ vẫn bị báo mãi"


def test_chua_den_han_grace_thi_khong_bao(tmp_path):
    _dung(tmp_path, [], [])
    kq = kln.kiem(D(2026, 9, 14, 18, 30), {**KHAI, "cua_so_ngay": 1}, tmp_path)  # kỳ 14/09 18:00 mới 30 phút
    assert kq["phat_hien"] == []


def test_thieu_nguyen_lieu_la_khong_do_duoc_khong_phai_do(tmp_path):
    kq = kln.kiem(D(2026, 9, 20, 19), KHAI, tmp_path)  # tmp rỗng: không log, không queue/
    assert kq["phat_hien"] == [] and len(kq["khong_do_duoc"]) == 2


def test_tac_vu_khong_khai_dau_vet_khong_bi_do(tmp_path):
    so = {"cua_so_ngay": 21, "tac_vu": [{"id": "q", "cron": "0 18 * * 1", "tu_ngay": "2026-08-17",
                                         "dau_vet": {"loai": "khong-co"}}]}
    kq = kln.kiem(D(2026, 9, 20, 19), so, tmp_path)
    assert kq["phat_hien"] == [] and any("chưa khai dấu vết" in x for x in kq["khong_do_duoc"])


def test_ky_truoc_tu_ngay_khong_bi_tinh(tmp_path):
    _dung(tmp_path, [], [])
    so = {"cua_so_ngay": 90, "tac_vu": [dict(KHAI["tac_vu"][0], tu_ngay="2026-09-15")]}
    kq = kln.kiem(D(2026, 9, 20, 19), so, tmp_path)
    assert kq["phat_hien"] == [], "kỳ 14/09 nằm trước tu_ngay mà vẫn bị đo"


def _nap_tkd():
    import importlib.util as _u
    import sys as _s
    from pathlib import Path as _P
    sp = _u.spec_from_file_location("tkd_p201", _P(__file__).resolve().parents[1] / "tools" / "tu_khoi_dong.py")
    m = _u.module_from_spec(sp)
    _s.modules["tkd_p201"] = m
    sp.loader.exec_module(m)
    return m


def test_tu_khoi_dong_in_canh_bao_lich_nen(monkeypatch, capsys):
    """P2-01: lúc mở phiên, kỳ lịch lỡ phải được NÓI RA (trước đây chỉ có ở tu_de_xuat_viec)."""
    import subprocess as sp
    m = _nap_tkd()
    monkeypatch.setattr(m.subprocess, "run", lambda *a, **k: sp.CompletedProcess(a, 1, stdout="🔴 LỊCH NỀN LỠ\n", stderr=""))
    m._canh_lich_nen()
    assert "LỊCH NỀN LỠ" in capsys.readouterr().out


def test_tu_khoi_dong_khong_im_lang_khi_cam_bien_hong(monkeypatch, capsys):
    """Cảm biến chết ≠ «lịch ổn»: phải nói «không biết», không được im lặng."""
    import subprocess as sp
    m = _nap_tkd()
    monkeypatch.setattr(m.subprocess, "run", lambda *a, **k: sp.CompletedProcess(a, 2, stdout="", stderr="boom"))
    m._canh_lich_nen()
    assert "không biết" in capsys.readouterr().out


def test_tu_khoi_dong_cam_bien_im_khi_on(monkeypatch, capsys):
    import subprocess as sp
    m = _nap_tkd()
    monkeypatch.setattr(m.subprocess, "run", lambda *a, **k: sp.CompletedProcess(a, 0, stdout="", stderr=""))
    m._canh_lich_nen()
    assert capsys.readouterr().out == ""
