# -*- coding: utf-8 -*-
"""Chặn GHI EndNote khi không thấy kho toàn văn (17/10/2026) — `nap_endnote_chu_de.py`.

Đo thật 17/10/2026: chạy công cụ từ một worktree (không có EBM-Dashboards/ gốc) với `--file` trỏ tới dashboard THẬT
⇒ `kho = None` ⇒ khối ĐỌC NHANH của MỌI bản ghi dựng dòng «Toàn văn: chưa xét (không thấy kho)» ⇒ chạy khô báo
«sẽ ghi 877 · không đổi 0»; thêm `--ap-dung` là ghi đè «có PDF · có bản đọc sâu» của cả thư viện bằng thông tin kém hơn.
Cùng lệnh kèm `--kho-toan-van <EBM-Dashboards>/toan_van_oa` ⇒ «sẽ ghi 0 · không đổi 877».

Vá: (1) suy kho CẠNH dashboard của `--file` (cùng cách bước ⑧ — TT-07); (2) vẫn không có kho ⇒ `--ap-dung` ghi khối bị TỪ CHỐI
trước khi đụng EndNote. Ngoại tuyến; HOME/CAU_HINH trỏ vào tmp_path; thư mục gốc EBM-Dashboards bị thay bằng None.
"""
from __future__ import annotations

import importlib.util
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


N = _nap("tools/nap_endnote_chu_de.py", "_nap_endnote_chan_kho_20261017")


@pytest.fixture(autouse=True)
def _cach_ly(tmp_path, monkeypatch):
    nha = tmp_path / "nha"
    nha.mkdir()
    monkeypatch.setenv("HOME", str(nha))
    monkeypatch.setenv("USERPROFILE", str(nha))
    monkeypatch.setattr(N, "CAU_HINH", nha / ".ebm-endnote.json")
    monkeypatch.setattr(N, "_tim_dash_goc", lambda: None)   # như worktree/bản sao trần — kết quả không phụ thuộc cây đang đứng


def _dash(thu_muc: Path, co_kho: bool) -> Path:
    thu_muc.mkdir(parents=True, exist_ok=True)
    d = thu_muc / "WebDashboard_X_20261017.html"
    d.write_text("x", encoding="utf-8", newline="\n")
    if co_kho:
        (thu_muc / "toan_van_oa").mkdir(exist_ok=True)
    return d


class _EnGhiLai:
    """EndNote giả đã cấu hình — ghi lại mọi lần bị gọi (để chứng minh bị từ chối TRƯỚC khi đụng EndNote)."""
    goi: list[str] = []

    def __init__(self, ung_dung, thu_vien):
        self.thu_vien = thu_vien

    def dang_mo_dung_thu_vien(self):
        _EnGhiLai.goi.append("dang_mo")
        return True

    def mo_thu_vien(self):
        _EnGhiLai.goi.append("mo")


@pytest.fixture()
def en(tmp_path, monkeypatch):
    tv = tmp_path / "Thu vien EBM.enl"
    tv.write_bytes(b"enl")
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    monkeypatch.setattr(N, "doc_cau_hinh", lambda tep=None: {"thu_vien": str(tv), "ung_dung": "EndNote 2025"})
    monkeypatch.setattr(N, "EndNoteMac", _EnGhiLai)
    _EnGhiLai.goi = []
    nhan: dict = {"tom_tat": [], "nap": []}

    def chay_tom_tat(endnote, files, kho, ap_dung, **k):
        nhan["tom_tat"].append({"kho": kho, "ap_dung": ap_dung})
        return {"loi": []}

    def nap_nhieu(files, **k):
        nhan["nap"].append(k)
        return []
    monkeypatch.setattr(N, "chay_tom_tat", chay_tom_tat)
    monkeypatch.setattr(N, "nap_nhieu", nap_nhieu)
    return nhan


# ── Suy kho ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_xac_dinh_kho_thu_tu_va_khong_chon_bua(tmp_path):
    a = _dash(tmp_path / "a", co_kho=True)
    b = _dash(tmp_path / "b", co_kho=True)
    c = _dash(tmp_path / "c", co_kho=False)
    goc = tmp_path / "goc"
    (goc / "toan_van_oa").mkdir(parents=True)
    assert N.xac_dinh_kho(str(tmp_path / "khong-co"), goc, [a]) == tmp_path / "khong-co", \
        "--kho-toan-van giữ NGUYÊN kể cả khi sai — không lặng lẽ đổi sang kho khác"
    assert N.xac_dinh_kho(None, None, [a]) == (tmp_path / "a" / "toan_van_oa").resolve(), "kho CẠNH dashboard (TT-07)"
    assert N.xac_dinh_kho(None, goc, [a]) == (tmp_path / "a" / "toan_van_oa").resolve(), \
        "kho cạnh dashboard đứng trước kho gốc — đúng kho cổng BH161 đọc"
    assert N.xac_dinh_kho(None, goc, [c]) == goc / "toan_van_oa", "dashboard không có kho cạnh ⇒ lùi về kho gốc"
    assert N.xac_dinh_kho(None, None, [a, b]) is None, "dashboard ở hai thư mục có hai kho ⇒ mơ hồ, không chọn bừa"
    assert N.xac_dinh_kho(None, None, [c]) is None


# ── Từ chối GHI khi không có kho ────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("co", [["--tom-tat-vi", "--ap-dung"], ["--ap-dung"]])
def test_ap_dung_khong_kho_bi_tu_choi_truoc_khi_dung_endnote(tmp_path, en, capsys, co):
    dash = _dash(tmp_path / "d", co_kho=False)
    assert N.main(["--file", str(dash), *co]) == N.MA_KHONG_CHAY
    ra = capsys.readouterr().out
    assert "KHÔNG ĐO ĐƯỢC — không thấy kho toàn văn" in ra and "KHÔNG ghi gì vào EndNote" in ra and "--kho-toan-van" in ra
    assert en["tom_tat"] == [] and en["nap"] == [], "không một bản ghi nào bị đụng"
    assert _EnGhiLai.goi == [], "từ chối TRƯỚC bước có thể bật EndNote lên màn hình"


def test_kho_chi_ro_ma_sai_duong_cung_bi_tu_choi(tmp_path, en, capsys):
    dash = _dash(tmp_path / "d", co_kho=True)
    ma = N.main(["--file", str(dash), "--tom-tat-vi", "--ap-dung", "--kho-toan-van", str(tmp_path / "go-nham")])
    assert ma == N.MA_KHONG_CHAY and en["tom_tat"] == [], "kho chỉ rõ sai đường không được thay bằng kho cạnh dashboard"
    assert "go-nham" in capsys.readouterr().out


def test_chay_kho_khong_kho_van_chay_va_noi_ro(tmp_path, en, capsys):
    dash = _dash(tmp_path / "d", co_kho=False)
    assert N.main(["--file", str(dash), "--tom-tat-vi"]) == N.MA_OK
    ra = capsys.readouterr().out
    assert "⚠ không thấy kho toàn văn" in ra and "--ap-dung ghi khối ĐỌC NHANH sẽ bị từ chối" in ra
    assert en["tom_tat"] == [{"kho": None, "ap_dung": False}], "chạy khô vẫn lập kế hoạch"


def test_ap_dung_khong_tom_tat_chi_nhap_ban_ghi_van_chay(tmp_path, en, capsys):
    dash = _dash(tmp_path / "d", co_kho=False)
    assert N.main(["--file", str(dash), "--ap-dung", "--khong-tom-tat"]) == N.MA_OK
    ra = capsys.readouterr().out
    assert len(en["nap"]) == 1 and en["tom_tat"] == [], "chỉ nhập bản ghi — không ghi khối nên không có gì bị đè"
    assert "không đính PDF" in ra and "KHÔNG ĐO ĐƯỢC" not in ra


def test_kho_canh_dashboard_duoc_suy_va_ghi_binh_thuong(tmp_path, en, capsys):
    dash = _dash(tmp_path / "d", co_kho=True)
    assert N.main(["--file", str(dash), "--tom-tat-vi", "--ap-dung"]) == N.MA_OK
    assert en["tom_tat"] == [{"kho": (tmp_path / "d" / "toan_van_oa").resolve(), "ap_dung": True}]
    assert "không thấy kho" not in capsys.readouterr().out


# ── Luật cũ vẫn thắng khi máy không ghi được EndNote ─────────────────────────────────────────────────────────────────────
def test_may_chua_cau_hinh_van_im_lang_ma_0_du_thieu_kho(tmp_path, capsys):
    dash = _dash(tmp_path / "d", co_kho=False)
    assert N.main(["--file", str(dash), "--ap-dung", "--im-khi-chua-cau-hinh"]) == N.MA_OK
    ra = capsys.readouterr().out
    assert "⚪ EndNote: bỏ qua" in ra and "KHÔNG ĐO ĐƯỢC — không thấy kho" not in ra, \
        "chưa cấu hình EndNote là điều kiện gốc hơn — bộ năm vẫn ⚪/mã 0 như cũ"


def test_gan_kho_khong_bi_chot_moi_chan(tmp_path, en, monkeypatch, capsys):
    monkeypatch.setattr(N, "gan_kho", lambda *a, **k: {"kho_toan_van": False})
    assert N.main(["--gan-kho", "--ap-dung"]) == N.MA_OK
    ra = capsys.readouterr().out
    assert "Không thấy kho toàn văn — CHƯA XÉT PDF" in ra and "KHÔNG ĐO ĐƯỢC" not in ra, "--gan-kho giữ báo riêng của nó"


def test_chan_ghi_khi_thieu_kho_truc_tiep(tmp_path):
    ns = lambda **k: types.SimpleNamespace(**{"gan_kho": False, "xuat_xml": None, "ap_dung": True,  # noqa: E731
                                              "tom_tat_vi": False, "khong_tom_tat": False, **k})
    assert N.chan_ghi_khi_thieu_kho(ns(), None) == N.MA_KHONG_CHAY
    assert N.chan_ghi_khi_thieu_kho(ns(), tmp_path) is None, "có kho thật ⇒ đi tiếp"
    assert N.chan_ghi_khi_thieu_kho(ns(xuat_xml="x.xml"), None) is None
    assert N.chan_ghi_khi_thieu_kho(ns(khong_tom_tat=True), None) is None
    assert N.chan_ghi_khi_thieu_kho(ns(khong_tom_tat=True, tom_tat_vi=True), None) == N.MA_KHONG_CHAY
