"""Cảm biến «điểm-khám NGOÀI giám sát» trừ lượt ĐÃ RÀ — 18/10/2026.

Lỗi đo thật: `state/nhat-ky-tac-dong.jsonl` chỉ nối thêm, cảm biến ⑦ của `tu_de_xuat_viec.py` đếm MỌI dòng miss từ xưa
tới nay ⇒ 3 miss (20/08–13/10) giữ việc 🤖 «rà ứng viên mở watchlist» mãi mãi dù máy đã rà xong; Đài hoàn thiện báo
E-NGOAI = 3 không bao giờ giảm. Sửa: sổ rà `state/ngoai-giam-sat-da-ra.json` (khoá = `luc` của dòng miss). Lượt đã rà
không còn là việc 🤖; việc còn chờ bác sĩ hiện thành dòng 👤 và Đài VẪN đếm nó (không đọc thành «đạt»).
Ngoại tuyến, chỉ ghi trong tmp_path.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import do_dai_hoan_thien as D  # noqa: E402


def _nap(ten: str, tep: str):
    spec = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


TDX = _nap("tdxv_ngoai_gs_20261018", "tu_de_xuat_viec.py")
DONG = [{"luc": "2026-08-20T17:29:32", "khop": [], "miss": True, "ms": 55},
        {"luc": "2026-10-11T09:38:54", "khop": [], "miss": True, "loai": "khong_co", "ms": 992},
        {"luc": "2026-10-13T19:26:23", "khop": [], "miss": True, "loai": "khong_co", "ms": 250},
        {"luc": "2026-10-14T08:00:00", "khop": [], "miss": True, "loai": "khop_yeu", "ms": 9},
        {"luc": "2026-10-15T08:00:00", "khop": ["EVID-1"], "miss": False, "ms": 9}]


def test_chua_co_so_ra_thi_dem_nhu_cu_va_bo_khop_yeu():
    assert TDX.dem_ngoai_giam_sat(DONG, {}) == (3, [])


def test_luot_da_ra_khong_con_la_viec_may_va_viec_cho_nguoi_hien_rieng():
    da_ra = {"2026-08-20T17:29:32": {"ket_qua": "hub có thẻ, bộ khớp không trúng", "cho_nguoi": ""},
             "2026-10-11T09:38:54": {"ket_qua": "dashboard chưa nạp hub", "cho_nguoi": "duyệt nạp dashboard CGA"},
             "2026-10-13T19:26:23": {"ket_qua": "dashboard chưa nạp hub", "cho_nguoi": "duyệt nạp dashboard COPD"}}
    miss, cho = TDX.dem_ngoai_giam_sat(DONG, da_ra)
    assert miss == 0
    assert cho == ["duyệt nạp dashboard CGA", "duyệt nạp dashboard COPD"]


def test_so_ra_vang_hoac_hong_thi_khong_bao_gio_im_lang(tmp_path):
    assert TDX.doc_ngoai_giam_sat_da_ra(tmp_path / "vang.json") == {}
    (tmp_path / "hong.json").write_text("{không phải json", encoding="utf-8", newline="\n")
    assert TDX.doc_ngoai_giam_sat_da_ra(tmp_path / "hong.json") == {}
    (tmp_path / "mang.json").write_text("[1, 2]", encoding="utf-8", newline="\n")
    assert TDX.doc_ngoai_giam_sat_da_ra(tmp_path / "mang.json") == {}
    assert TDX.dem_ngoai_giam_sat(DONG, TDX.doc_ngoai_giam_sat_da_ra(tmp_path / "hong.json"))[0] == 3


def test_dai_dem_ca_luot_chua_ra_lan_luot_da_ra_cho_bac_si(monkeypatch, tmp_path):
    monkeypatch.setattr(D, "_chay", lambda *a, **k: None)
    viec = [{"viec": "2 câu điểm-khám ngoài giám sát ĐÃ RÀ, chờ việc của bác sĩ — duyệt nạp dashboard CGA; COPD"}]
    hang = {h["ma"]: h for h in D.thuoc_do(tmp_path, tmp_path, [], viec, [])}
    assert hang["E-NGOAI"]["so"] == 2 and hang["E-NGOAI"]["trang_thai"] == "chua"
    viec.append({"viec": "4 lượt điểm-khám NGOÀI giám sát — rà ứng viên mở watchlist"})
    hang = {h["ma"]: h for h in D.thuoc_do(tmp_path, tmp_path, [], viec, [])}
    assert hang["E-NGOAI"]["so"] == 6


def test_cau_chu_cam_bien_khop_mau_cua_dai():
    nguon = (TOOLS / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    assert "câu điểm-khám ngoài giám sát ĐÃ RÀ" in nguon
    json.dumps(DONG)  # dữ liệu mẫu không chứa định danh người bệnh — chỉ mốc giờ/mã thẻ
