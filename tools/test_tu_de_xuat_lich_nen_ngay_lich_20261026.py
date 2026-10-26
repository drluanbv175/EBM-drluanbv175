"""Giác quan lịch nền KHÔNG báo «kỳ thứ Hai không nổ» khi chính ngày thứ Hai chưa hết — 26/10/2026.

Ca thật: 17:18 thứ Hai 26/10/2026, hòm việc báo «Kỳ lịch thứ Hai vừa qua KHÔNG nổ» trong khi tác vụ
`thu-thap-tuan-an-toan-thuoc` (cron 18:00 thứ Hai) chưa tới giờ và lượt 19/10 đã PASS. Ngoại tuyến, chỉ dùng tệp tạm.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_ngay_lich", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

THU_HAI = dt.date(2026, 10, 26)


def _log(tmp_path: Path, ngay: str) -> Path:
    p = tmp_path / "tuan.log"
    p.write_text(f"===== {ngay} 18:10:00 : KẾT THÚC — tổng thể=PASS =====\n", encoding="utf-8", newline="\n")
    return p


def test_fixture_dung_thu():
    assert THU_HAI.weekday() == 0


def test_thu_hai_truoc_gio_chay_khong_bao_lo_ky(tmp_path):
    log = _log(tmp_path, "2026-10-19")
    assert M.giac_quan_lich_nen(log, bay_gio=dt.datetime(2026, 10, 26, 17, 18)) == []


def test_thu_hai_toi_luot_dang_chay_cung_khong_bao(tmp_path):
    # Lượt 12/10 chạy 1 giờ 48 phút ⇒ 19:30 vẫn có thể chưa ghi dòng KẾT THÚC.
    log = _log(tmp_path, "2026-10-19")
    assert M.giac_quan_lich_nen(log, bay_gio=dt.datetime(2026, 10, 26, 19, 30)) == []


def test_thu_ba_ma_thu_hai_khong_no_thi_bao(tmp_path):
    log = _log(tmp_path, "2026-10-19")
    kq = M.giac_quan_lich_nen(log, bay_gio=dt.datetime(2026, 10, 27, 8, 0))
    assert kq and kq[0][0] == 1  # PASS 8 ngày tuổi ⇒ «kỳ lịch đã lỡ, chạy bù»


def test_thu_hai_luot_hom_nay_da_pass_thi_im(tmp_path):
    log = _log(tmp_path, "2026-10-26")
    assert M.giac_quan_lich_nen(log, bay_gio=dt.datetime(2026, 10, 26, 18, 30)) == []


def test_chi_truyen_hom_nay_giu_hanh_vi_cu_cuoi_ngay(tmp_path):
    # Chốt BH và test thuần chỉ truyền ngày = đánh giá lúc hết ngày ⇒ kỳ hôm nay đã đến hạn.
    log = _log(tmp_path, "2026-10-19")
    kq = M.giac_quan_lich_nen(log, THU_HAI)
    assert kq and kq[0][0] == 2


def test_thu_bay_lo_ky_van_bao(tmp_path):
    # Không làm mù ca BH57: thứ Bảy 31/10, lượt thứ Hai 26/10 không nổ, PASS cuối 24/10 (7 ngày) ⇒ mức 2.
    log = _log(tmp_path, "2026-10-24")
    kq = M.giac_quan_lich_nen(log, bay_gio=dt.datetime(2026, 10, 31, 9, 0))
    assert kq and kq[0][0] == 2
