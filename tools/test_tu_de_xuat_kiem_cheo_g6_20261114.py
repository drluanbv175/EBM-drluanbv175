"""Giác quan «kiểm chéo G6 bằng SPSS + R» của `tu_de_xuat_viec.py` — 14/11/2026 (gói tự động hoá A–D, mục B).

Đề tài thật có kết quả Python G6 mà chưa kiểm chéo / kết quả kiểm chéo CŨ ⇒ 🛎 (một lệnh máy chạy được); LỆCH / lỗi ⇒ 👤.
Trạng thái đọc bằng CHÍNH hàm `trang_thai` của công cụ repo y khoa — test dùng một công cụ GIẢ cùng giao diện trong thư
mục tạm (CI repo gốc không có repo y khoa). Ngoại tuyến — không đọc exports/ thật.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_kiem_cheo", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

CONG_CU_GIA = '''
CHUA_CHAY, CU, KHOP, LECH_NHO, LECH, LOI, TU_CHOI, KHONG_DO_DUOC = (
    "CHUA_CHAY", "CU", "KHOP", "LECH_NHO", "LECH", "LOI", "TU_CHOI", "KHONG_DO_DUOC")
import json
from pathlib import Path


def trang_thai(d):
    tt = json.loads((Path(d) / "tt_gia.json").read_text(encoding="utf-8"))
    return {"trang_thai": tt, "nhan": "nhãn " + tt, "ly_do": "lý do giả"}
'''


@pytest.fixture(autouse=True)
def _reset():
    M._GIAC_QUAN_CHET.clear()
    M._SO_GIAC_QUAN["chay"] = 0
    yield
    M._GIAC_QUAN_CHET.clear()


def _goc(tmp_path: Path) -> tuple[Path, Path, Path]:
    exp = tmp_path / "mea" / "exports"
    exp.mkdir(parents=True)
    tools = tmp_path / "mea" / "tools"
    tools.mkdir()
    (tools / "kiem_cheo_g6.py").write_text(CONG_CU_GIA, encoding="utf-8", newline="\n")
    gc = tools / "gate_contract.py"
    gc.write_text('REAL_STUDY_DENYLIST = frozenset({"de-tai-that-z"})\n', encoding="utf-8", newline="\n")
    return exp, tools / "kiem_cheo_g6.py", gc


def _de_tai(exp: Path, ten: str, tt: str | None, *, g6: bool = True, kind: str | None = None) -> None:
    d = exp / ten
    d.mkdir()
    (d / "study_meta.json").write_text(json.dumps({"study_kind": kind} if kind else {}), encoding="utf-8", newline="\n")
    if g6:
        (d / "G6_analysis_summary.json").write_text("{}", encoding="utf-8", newline="\n")
    if tt:
        (d / "tt_gia.json").write_text(json.dumps(tt), encoding="utf-8", newline="\n")


def test_chua_chay_cu_la_chuong_lech_loi_la_nguoi(tmp_path):
    exp, cc, gc = _goc(tmp_path)
    for ten, tt in (("a", "CHUA_CHAY"), ("b", "CU"), ("c", "LECH"), ("d", "LOI"), ("e", "KHOP"), ("f", "LECH_NHO"),
                    ("g", "KHONG_DO_DUOC")):
        _de_tai(exp, ten, tt)
    _de_tai(exp, "h", None, g6=False)  # chưa có kết quả Python G6 ⇒ không xét
    viec = M.giac_quan_kiem_cheo_g6(exp, cc, gc)
    theo = {v[2].split(":")[0]: v for v in viec}
    assert set(theo) == {"a", "b", "c", "d"}  # khớp, lệch nhỏ, không đo được (máy thiếu SPSS/R) ⇒ không thành việc
    assert theo["a"][1] == theo["b"][1] == "🛎" and theo["c"][1] == theo["d"][1] == "👤"
    assert theo["c"][0] < theo["a"][0]  # LỆCH ưu tiên trước «chưa chạy»
    assert all("kiem_cheo_g6.py chay --study" in v[3] for v in viec)
    assert not M._GIAC_QUAN_CHET


def test_bo_qua_de_tai_gia_tru_khi_nam_trong_danh_sach_that(tmp_path):
    exp, cc, gc = _goc(tmp_path)
    _de_tai(exp, "de-tai-gia", "CHUA_CHAY", kind="synthetic_test")
    _de_tai(exp, "de-tai-that-z", "CHUA_CHAY", kind="synthetic_test")  # cờ đặt nhầm trên đề tài thật ⇒ vẫn đo
    viec = M.giac_quan_kiem_cheo_g6(exp, cc, gc)
    assert [v[2].split(":")[0] for v in viec] == ["de-tai-that-z"]


def test_thieu_cong_cu_hoac_exports_la_giac_quan_chet(tmp_path):
    exp, cc, gc = _goc(tmp_path)
    _de_tai(exp, "a", "CHUA_CHAY")
    assert M.giac_quan_kiem_cheo_g6(exp, tmp_path / "khong_co.py", gc) == []
    assert M._GIAC_QUAN_CHET, "thiếu công cụ phải hiện là giác quan chết, không phải «đã kiểm chéo»"
    M._GIAC_QUAN_CHET.clear()
    assert M.giac_quan_kiem_cheo_g6(tmp_path / "khong_co_exports", cc, gc) == [] and M._GIAC_QUAN_CHET
    M._GIAC_QUAN_CHET.clear()
    cc.write_text("raise RuntimeError('hỏng')\n", encoding="utf-8", newline="\n")
    assert M.giac_quan_kiem_cheo_g6(exp, cc, gc) == [] and M._GIAC_QUAN_CHET
