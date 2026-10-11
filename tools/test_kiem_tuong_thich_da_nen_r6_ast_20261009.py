"""Luật R6 (write_text thiếu newline trong vùng chuỗi-ký) đọc bằng CÚ PHÁP — vá 09/10/2026 (BH55 đỏ từ 07/10).

Regex theo dòng cũ khớp `encoding="utf-8")` của lời gọi `read_text(...)` LỒNG trong đối số, nên báo 🔴 cho
`p.write_text(p.read_text(encoding="utf-8") + "…",` ⏎ `encoding="utf-8", newline="\\n")` — đo 09/10: 24/24 cảnh báo trên
752 tệp vùng ký là báo nhầm; ngược lại nó bỏ sót mọi lời gọi trải nhiều dòng. Ngoại tuyến, tệp tạm.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "kiem_tuong_thich_da_nen.py"
_sp = importlib.util.spec_from_file_location("ktdn_r6_ast_20261009", _TEP)
ktd = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(ktd)


def _r6(tmp_path: Path, noi_dung: str, monkeypatch) -> list[str]:
    """Đặt tệp vào vùng ký `<tmp>/medical-ebm-automation/tests/` rồi chạy `quet_file`, trả các dòng R6."""
    thu_muc = tmp_path / "medical-ebm-automation" / "tests"
    thu_muc.mkdir(parents=True, exist_ok=True)
    p = thu_muc / "mau.py"
    p.write_text(noi_dung, encoding="utf-8", newline="\n")
    monkeypatch.setattr(ktd, "REPO", tmp_path)
    do, _vang = ktd.quet_file(p)
    return [x for x in do if " R6 " in x]


def test_read_text_long_trong_doi_so_khong_con_bao_nham(tmp_path, monkeypatch):
    """Đúng mẫu ở tests/test_g10_hoan_thien_20261005.py:331 — newline ở dòng kế."""
    noi_dung = (
        "def f(ban_thao):\n"
        '    ban_thao.write_text(ban_thao.read_text(encoding="utf-8") + "\\nCau them\\n",\n'
        '                        encoding="utf-8", newline="\\n")\n'
    )
    assert _r6(tmp_path, noi_dung, monkeypatch) == []


def test_mau_replace_long_nhieu_dong_khong_bao_nham(tmp_path, monkeypatch):
    """Đúng mẫu ở tests/test_g5_hoan_thien_20261004.py:116."""
    noi_dung = (
        "def f(dmp):\n"
        '    dmp.write_text(dmp.read_text(encoding="utf-8").replace(\n'
        '        "a", "b").replace(\n'
        '        "c", "d"), encoding="utf-8", newline="\\n")\n'
    )
    assert _r6(tmp_path, noi_dung, monkeypatch) == []


def test_loi_goi_nhieu_dong_thieu_newline_nay_bi_bat(tmp_path, monkeypatch):
    """Regex cũ BỎ SÓT ca này (encoding và dấu đóng ngoặc khác dòng) — vi phạm thật phải đỏ."""
    noi_dung = (
        "def f(p, s):\n"
        "    p.write_text(\n"
        "        s,\n"
        '        encoding="utf-8",\n'
        "    )\n"
    )
    r6 = _r6(tmp_path, noi_dung, monkeypatch)
    assert len(r6) == 1 and ":2 R6" in r6[0], r6


def test_mot_dong_thieu_newline_van_bi_bat_va_co_newline_thi_khong(tmp_path, monkeypatch):
    noi_dung = (
        "def f(p, s):\n"
        '    p.write_text(s, encoding="utf-8")\n'
        '    p.write_text(s, encoding="utf-8", newline="\\n")\n'
    )
    r6 = _r6(tmp_path, noi_dung, monkeypatch)
    assert len(r6) == 1 and ":2 R6" in r6[0], r6


def test_doi_so_vi_tri(tmp_path, monkeypatch):
    """`write_text(s, "utf-8")` là có encoding (thiếu newline ⇒ đỏ); 4 đối số vị trí là có newline."""
    noi_dung = (
        "def f(p, s):\n"
        '    p.write_text(s, "utf-8")\n'
        '    p.write_text(s, "utf-8", None, "\\n")\n'
    )
    r6 = _r6(tmp_path, noi_dung, monkeypatch)
    assert len(r6) == 1 and ":2 R6" in r6[0], r6


def test_kwargs_va_args_sao_khong_phan(tmp_path, monkeypatch):
    """`**kw` / `*a` có thể mang newline — không bịa vi phạm."""
    noi_dung = (
        "def f(p, s, kw, a):\n"
        '    p.write_text(s, encoding="utf-8", **kw)\n'
        "    p.write_text(*a)\n"
    )
    assert _r6(tmp_path, noi_dung, monkeypatch) == []


def test_mien_tru_o_dong_bat_ky_cua_loi_goi(tmp_path, monkeypatch):
    noi_dung = (
        "def f(p, s):\n"
        "    p.write_text(\n"
        "        s,\n"
        '        encoding="utf-8",  # da-nen: bo-qua (tệp chỉ đọc trên Mac, không ký)\n'
        "    )\n"
    )
    assert _r6(tmp_path, noi_dung, monkeypatch) == []


def test_dong_bao_la_dong_chua_write_text(tmp_path, monkeypatch):
    noi_dung = (
        "def f(p, s):\n"
        "    (\n"
        "        p\n"
        '        .write_text(s, encoding="utf-8")\n'
        "    )\n"
    )
    r6 = _r6(tmp_path, noi_dung, monkeypatch)
    assert len(r6) == 1 and ":4 R6" in r6[0], r6


def test_tep_loi_cu_phap_lui_ve_doc_theo_dong_khong_doc_thanh_sach(tmp_path, monkeypatch):
    """KHÔNG ĐO ĐƯỢC bằng cú pháp ⇒ dùng lại luật theo dòng cũ, không bao giờ trả «sạch» chỉ vì parse hỏng."""
    noi_dung = (
        "def f(p, s):\n"
        '    p.write_text(s, encoding="utf-8")\n'
        "    if True\n"
    )
    r6 = _r6(tmp_path, noi_dung, monkeypatch)
    assert len(r6) == 1 and "lỗi cú pháp" in r6[0], r6
    assert ktd.dong_r6_vi_pham(noi_dung) is None


def test_docstring_chua_vi_du_khong_bi_bao(tmp_path, monkeypatch):
    noi_dung = (
        "def f():\n"
        '    """Vi du: p.write_text("x", encoding="utf-8") — chi la van ban."""\n'
        "    return 1\n"
    )
    assert _r6(tmp_path, noi_dung, monkeypatch) == []
