# -*- coding: utf-8 -*-
"""Khoá ghi EndNote theo PHẠM VI một thao tác (24/10/2026).

Sự cố đo 24/10/2026: máy chủ MCP `endnote-ebm` (sống cả phiên Claude) giữ `~/.ebm-endnote-dang-ghi.json` sau MỘT lệnh ghi tới
khi quá HAN_KHOA (15 phút) ⇒ `xuat_goi_cap_nhat.py` bước ⑧, `tom_tat_endnote_vi.py`, `tom_tat_chung_cu_word.py dung
--gan-endnote` đều nhận `DangCoTienTrinhKhacGhi` (bộ năm VKDT_TongHop_20261024 bị bỏ bước ⑧). Thêm: `luc_epoch` không được làm
mới khi tiến trình đang giữ khoá ghi tiếp ⇒ khoá của tiến trình đang ghi dở bị tiến trình khác coi là treo.

Khoá: phạm vi nhả ngay khi xong (kể cả khi lỗi, lồng nhau chỉ khối ngoài cùng nhả, chạy khô không đụng tệp khoá, khoá theo
tiến trình của script ngắn giữ nguyên) · mỗi lệnh ghi làm mới `luc_epoch` (đo bằng TIẾN TRÌNH KHÁC thật) · mỗi lời gọi công cụ
MCP là một phạm vi, trên CÙNG bản mô-đun khoá mà `EndNoteMac` dùng. Ngoại tuyến, không chạm `~/.ebm-endnote-dang-ghi.json`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TEP_MO_DUN = REPO / "tools" / "khoa_ghi_endnote.py"


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


kg = _nap("_kg_t1024", "khoa_ghi_endnote.py")
mcp = _nap("_mcp_t1024", "mcp/endnote_ebm_mcp.py")

# Tiến trình KHÁC thật thử lấy khoá một lần (cho_toi_da=0). `song` giả: tiến trình pytest còn sống; không gọi `os.kill(pid, 0)`
# (trên Windows tín hiệu 0 là CTRL_C_EVENT).
_THU_LAY_KHOA = """
import importlib.util, sys
from pathlib import Path
sp = importlib.util.spec_from_file_location("_kg_con", sys.argv[1])
kg = importlib.util.module_from_spec(sp)
sp.loader.exec_module(kg)
try:
    kg.cho_phep_ghi_loi("EndNote 2025", "tien trinh khac", tep=Path(sys.argv[2]), dang_dung=lambda: False, cho_toi_da=0,
                        thong_bao=lambda s: None, song=lambda pid: True)
    print("LAY_DUOC")
except kg.DangCoTienTrinhKhacGhi:
    print("BI_CHAN")
"""


def _tien_trinh_khac_lay_khoa(tep: Path) -> str:
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_CURRENT_TEST"}
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, "-c", _THU_LAY_KHOA, str(TEP_MO_DUN), str(tep)], capture_output=True, text=True,
                       encoding="utf-8", timeout=120, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _dat_lai(m) -> None:
    m._DANG_GIU.update({"pid": None, "tep": None, "thong_bao": False, "pham_vi": 0, "tu_pham_vi": False})


@pytest.fixture(autouse=True)
def _sach():
    _dat_lai(kg)
    yield
    _dat_lai(kg)


def _ghi(tep: Path, ly_do: str = "ghi", tb: list | None = None, bay_gio=time.time) -> None:
    kg.cho_phep_ghi_loi("EndNote 2025", ly_do, tep=tep, dang_dung=lambda: False, ngu=lambda s: None,
                        thong_bao=(tb.append if tb is not None else lambda s: None), song=lambda pid: True, bay_gio=bay_gio)


# ── phạm vi ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pham_vi_nha_khoa_ngay_khi_xong_tien_trinh_khac_lay_duoc(tmp_path):
    tep = tmp_path / "khoa.json"
    with kg.pham_vi_ghi():
        _ghi(tep, "đăng vào nhóm")
        assert kg.doc_khoa(tep)["pid"] == os.getpid()
        assert _tien_trinh_khac_lay_khoa(tep) == "BI_CHAN", "đang trong thao tác thì tiến trình khác phải chờ"
    assert not tep.exists(), "ra khỏi phạm vi mà khoá vẫn giữ — máy chủ MCP sẽ chặn mọi tiến trình khác tới 15 phút"
    assert _tien_trinh_khac_lay_khoa(tep) == "LAY_DUOC"


def test_pham_vi_nha_khoa_ca_khi_thao_tac_loi(tmp_path):
    tep = tmp_path / "khoa.json"
    with pytest.raises(RuntimeError, match="AppleScript hỏng"):
        with kg.pham_vi_ghi():
            _ghi(tep)
            raise RuntimeError("AppleScript hỏng")
    assert not tep.exists()


def test_pham_vi_long_nhau_chi_khoi_ngoai_cung_nha(tmp_path):
    tep = tmp_path / "khoa.json"
    with kg.pham_vi_ghi():
        with kg.pham_vi_ghi():
            _ghi(tep)
        assert tep.exists(), "khối trong nhả khoá khi thao tác ngoài còn đang chạy"
        _ghi(tep, "lệnh ghi thứ hai")
    assert not tep.exists()


def test_pham_vi_chay_kho_khong_dung_tep_khoa(tmp_path):
    tep = tmp_path / "khoa.json"
    with kg.pham_vi_ghi():
        pass
    assert not tep.exists()
    tep.write_text(json.dumps({"pid": os.getpid() + 999999, "luc_epoch": time.time()}))
    with kg.pham_vi_ghi():
        pass
    assert json.loads(tep.read_text())["pid"] == os.getpid() + 999999, "phạm vi không ghi gì không được xoá khoá người khác"


def test_khoa_theo_tien_trinh_cua_script_ngan_giu_nguyen(tmp_path):
    """Script ngắn (không mở phạm vi) lấy khoá ở lần ghi đầu, giữ tới khi thoát — một phạm vi về sau không được nhả hộ."""
    tep = tmp_path / "khoa.json"
    _ghi(tep, "nhập trích dẫn")
    with kg.pham_vi_ghi():
        _ghi(tep, "đăng vào nhóm")
    assert kg.doc_khoa(tep)["pid"] == os.getpid()


def test_thong_bao_moi_lan_lay_khoa_khong_lap_moi_lenh_ghi(tmp_path):
    tep, tb = tmp_path / "khoa.json", []
    for lan in ("thao tác 1", "thao tác 2"):
        with kg.pham_vi_ghi():
            _ghi(tep, lan, tb)
            _ghi(tep, lan + " (lệnh ghi thứ hai)", tb)
    assert tb == ["thao tác 1", "thao tác 2"]


def test_giu_khoa_ghi_co_ly_do_lay_khoa_ngay_khi_vao_khoi(tmp_path, monkeypatch):
    tep, tb = tmp_path / "khoa.json", []
    monkeypatch.setattr(kg, "_bo_qua", lambda: False)
    monkeypatch.setattr(kg, "TEP_KHOA", tep)
    monkeypatch.setattr(kg, "bac_si_dang_dung", lambda *a, **k: False)
    monkeypatch.setattr(kg, "_thong_bao", tb.append)
    with kg.giu_khoa_ghi("EndNote 2025", "gắn toàn văn"):
        assert kg.doc_khoa()["ly_do"] == "gắn toàn văn"
    assert not tep.exists() and tb == ["gắn toàn văn"]


# ── làm mới luc_epoch ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_moi_lenh_ghi_lam_moi_luc_epoch_khoa_dang_ghi_do_khong_bi_coi_la_treo(tmp_path):
    tep = tmp_path / "khoa.json"
    cu = time.time() - kg.HAN_KHOA - 60  # lấy khoá 16 phút trước, ghi suốt từ đó
    _ghi(tep, "lệnh ghi đầu", bay_gio=lambda: cu)
    assert _tien_trinh_khac_lay_khoa(tep) == "LAY_DUOC", "tiền đề: khoá không làm mới quá HAN_KHOA thì bị coi là treo"
    _dat_lai(kg)
    _ghi(tep, "lệnh ghi đầu", bay_gio=lambda: cu)
    _ghi(tep, "lệnh ghi tiếp")
    d = kg.doc_khoa(tep)
    assert d["luc_epoch"] > cu + kg.HAN_KHOA and d["ly_do"] == "lệnh ghi tiếp"
    assert _tien_trinh_khac_lay_khoa(tep) == "BI_CHAN", "khoá của tiến trình đang ghi dở bị tiến trình khác coi là treo"


def test_ghi_khoa_nguyen_tu_khong_de_tep_tam(tmp_path):
    tep = tmp_path / "khoa.json"
    _ghi(tep)
    _ghi(tep)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["khoa.json"]


# ── máy chủ MCP ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_mcp_moi_loi_goi_cong_cu_ghi_nha_khoa_khi_tra_ve(tmp_path, monkeypatch):
    """Đầu–cuối trên đường ghi THẬT: `tools/call endnote_dua_vao_nhom` → `EndNoteMac.dang_vao_nhom` → `_truoc_khi_ghi` →
    `nap_khoa_ghi()`. Phạm vi mở sai bản mô-đun hoặc không mở ⇒ khoá còn lại sau lời gọi ⇒ đỏ."""
    tep = tmp_path / "khoa.json"
    nec = mcp.mod("nec")
    kgc = mcp._khoa_ghi()
    assert kgc is not None and kgc is nec.nap_khoa_ghi(), "máy chủ MCP phải dùng CHÍNH bản mô-đun khoá của EndNoteMac"
    _dat_lai(kgc)
    monkeypatch.setattr(kgc, "_bo_qua", lambda: False)
    monkeypatch.setattr(kgc, "TEP_KHOA", tep)
    monkeypatch.setattr(kgc, "bac_si_dang_dung", lambda *a, **k: False)
    monkeypatch.setattr(kgc, "_thong_bao", lambda s: None)

    trong_luc_ghi: list[str] = []
    en = object.__new__(nec.EndNoteMac)
    en.ten, en.ung_dung, en._csdl = "Lib.enl", "EndNote 2025", "1"

    def _chay(than, *ds, **kw):
        assert kgc.doc_khoa(tep)["pid"] == os.getpid(), "lệnh ghi chạy khi chưa giữ khoá"
        trong_luc_ghi.append(_tien_trinh_khac_lay_khoa(tep))
        if "HONG" in ds:
            raise RuntimeError("AppleScript hỏng")
        return ""

    en._chay = _chay
    monkeypatch.setattr(mcp, "_endnote", lambda: (en, tmp_path / "Lib.enl"))
    monkeypatch.setattr(mcp, "_nhom_dich", lambda tv, ten: [])
    monkeypatch.setattr(mcp, "_do_sau_khi_dang", lambda tv, ten, rec, truoc: {"da_goi_post": True})
    try:
        for i, ten in enumerate(("EBM · a", "HONG")):
            kq = mcp.xu_ly({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {
                "name": "endnote_dua_vao_nhom", "arguments": {"rec_nums": [7], "ten_nhom": ten, "ap_dung": True}}})
            assert kq["result"]["isError"] is (ten == "HONG")
            assert not tep.exists(), f"lời gọi #{i} trả về mà khoá vẫn giữ (pid máy chủ MCP chặn bộ năm bước ⑧)"
            assert _tien_trinh_khac_lay_khoa(tep) == "LAY_DUOC"
        assert trong_luc_ghi == ["BI_CHAN", "BI_CHAN"]
    finally:
        _dat_lai(kgc)


def test_mcp_cong_cu_chay_kho_khong_lay_khoa(tmp_path, monkeypatch):
    tep = tmp_path / "khoa.json"
    kgc = mcp._khoa_ghi()
    monkeypatch.setattr(kgc, "_bo_qua", lambda: False)
    monkeypatch.setattr(kgc, "TEP_KHOA", tep)

    class _En:
        ung_dung = "EndNote 2025"

        def so_csdl(self):
            return "1"

    monkeypatch.setattr(mcp, "_endnote", lambda: (_En(), tmp_path / "Lib.enl"))
    monkeypatch.setattr(mcp, "_nhom_dich", lambda tv, ten: [])
    kq = mcp.xu_ly({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "endnote_dua_vao_nhom", "arguments": {"rec_nums": [7], "ten_nhom": "EBM · a"}}})
    assert json.loads(kq["result"]["content"][0]["text"])["chay_kho"] is True
    assert not tep.exists()


def test_hai_ban_nap_endnote_chu_de_dung_chung_mot_ban_khoa():
    """Một tiến trình nạp `nap_endnote_chu_de.py` nhiều lần dưới tên khác nhau (máy chủ MCP, công cụ tóm tắt…) vẫn chỉ có MỘT
    trạng thái khoá — phạm vi mở qua bản này thấy lần lấy khoá qua bản kia."""
    a, b = _nap("_nec_a_t1024", "nap_endnote_chu_de.py"), _nap("_nec_b_t1024", "nap_endnote_chu_de.py")
    assert a.nap_khoa_ghi() is not None and a.nap_khoa_ghi() is b.nap_khoa_ghi() is mcp._khoa_ghi()
