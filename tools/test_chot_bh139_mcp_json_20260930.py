"""BH139: `.mcp.json` khởi chạy pubmed-search không phụ thuộc thư mục chạy (30/09/2026).

CI chạy tệp này trên cả Ubuntu lẫn Windows ⇒ đây là phép đo ĐA NỀN của chính đoạn mã `-c` khai trong `.mcp.json`
(lớp `uv run --no-project python` không được kiểm ở đây — giới hạn ghi ở audit/NHAT-KY-SU-CO.md). Các ca đột biến giữ
lại dưới dạng test để chốt không lặng lẽ mất khả năng phân biệt.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "chot_hoi_quy_bai_hoc.py"
_sp = importlib.util.spec_from_file_location("chot_bh139", _TEP)
C = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(C)

_ARGS = json.loads((_TEP.parents[1] / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["pubmed-search"]["args"]
_MA = _ARGS[-1]


def _chay_voi(monkeypatch, tmp_path, args):
    """Chạy BH139 trên một bản `.mcp.json` đặt ở thư mục tạm (không đụng tệp thật của repo)."""
    khai = {"mcpServers": {"pubmed-search": {"command": "uv", "args": args}}}
    (tmp_path / ".mcp.json").write_text(json.dumps(khai), encoding="utf-8")
    monkeypatch.setattr(C, "REPO", tmp_path)
    return C.bh139_mcp_json_khoi_chay_khong_phu_thuoc_thu_muc_chay()


def test_ma_song_xanh():
    assert C.bh139_mcp_json_khoi_chay_khong_phu_thuoc_thu_muc_chay() == (True, "")


def test_doi_chung_ban_khai_nguyen_ven_qua_thu_muc_tam_van_xanh(monkeypatch, tmp_path):
    """Đối chứng cho các ca đột biến: chép NGUYÊN bản khai sang thư mục tạm thì chốt vẫn xanh."""
    assert _chay_voi(monkeypatch, tmp_path, list(_ARGS)) == (True, "")


_DOT_BIEN = [
    ("duong-dan-tuong-doi", ["run", "--no-project", "tools/mcp/chay_pubmed_search_mcp.py"], "đường dẫn tương đối"),
    ("khong-do-thu-muc-cha", [*_ARGS[:-1], _MA.replace("(c,*c.parents)", "(c,)")],
     "thư mục lồng 4 tầng: không khởi chạy được"),
    ("bo-dieu-kien-canh-mcp-json", [*_ARGS[:-1], _MA.replace(" and (d/'.mcp.json').is_file()", "")], "chạy bản lạc"),
    ("khong-thay-ma-thoat-0", [*_ARGS[:-1], _MA.replace("sys.exit(", "print(")], "thoát 0"),
    ("khong-thay-ma-in-stdout", [*_ARGS[:-1], _MA.replace("sys.exit('[pubmed-search]", "sys.exit(print('x') or '[pubmed-search]")],
     "in ra stdout"),
    ("python3-tran", ["run", "--no-project", "python3", "-c", _MA], "`python3`/`python` trần"),
    ("ky-tu-ngoai-ascii", [*_ARGS[:-1], _MA.replace("khong thay", "không thấy")], "ngoài ASCII"),
    ("run-name-khac-main", [*_ARGS[:-1], _MA.replace("run_name='__main__'", "run_name='khac'")], "không khởi chạy được"),
]


@pytest.mark.parametrize("args, cum_cho", [(a, c) for _t, a, c in _DOT_BIEN], ids=[t for t, _a, _c in _DOT_BIEN])
def test_dot_bien_bi_bat_dung_cho(monkeypatch, tmp_path, args, cum_cho):
    assert args != list(_ARGS), "phép đột biến không đổi gì — chuỗi cần thay đã biến mất khỏi .mcp.json, sửa phép thử"
    ok, chi_tiet = _chay_voi(monkeypatch, tmp_path, args)
    assert ok is False and cum_cho in chi_tiet, chi_tiet
