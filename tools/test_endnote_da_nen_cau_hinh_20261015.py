# -*- coding: utf-8 -*-
"""EndNote & đa nền (15/10/2026) — nap_endnote_chu_de.py + sua_abstract_bi_cat_endnote.py.

  • DN-02  ngoài macOS: xét nền tảng TRƯỚC cấu hình — chỉ thẳng sang --xuat-xml, không dạy «chạy --ghi-cau-hinh».
  • DN-03  so thư viện đang mở bằng ĐỊNH DANH tệp (samefile), không bằng chuỗi realpath (APFS không phân biệt hoa/thường).
  • gap_endnote_running  phép kiểm «đã mở chưa» KHÔNG được gửi `tell application` khi EndNote đang tắt (gửi là bật nó lên);
           hết giờ ⇒ False, không treo.
  • TT-09  ~/.ebm-endnote.json HỎNG ≠ VẮNG; --ghi-cau-hinh không ghi đè tệp hỏng nếu chưa xác nhận (giữ .hong-<ngày>).
  • G3-D8  --tom-tat-vi chạy khô không mở bằng «✓», có dòng «Chạy khô — … thêm --ap-dung».
  • W10    --chua-xac-minh: khối ĐỌC NHANH ghi «CHƯA xác minh nguồn sống», chân không nói «đã qua cổng».

Ngoại tuyến; KHÔNG chạm ~/.ebm-endnote.json thật (HOME và CAU_HINH trỏ vào tmp_path, có chốt so trước/sau).
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import types
import unicodedata
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_THAT = Path(os.environ.get("EBM_ENDNOTE_CAU_HINH") or (Path.home() / ".ebm-endnote.json"))


def _dau_van(p: Path):
    try:
        st = p.stat()
        return (st.st_size, st.st_mtime_ns)
    except OSError:
        return None


_DAU_VAN_THAT = _dau_van(_THAT)


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


N = _nap("tools/nap_endnote_chu_de.py", "_nap_endnote_dn_20261015")
S = _nap("tools/sua_abstract_bi_cat_endnote.py", "_sua_abs_dn_20261015")


@pytest.fixture(autouse=True)
def _cach_ly(tmp_path, monkeypatch):
    """Mọi test: HOME tạm + CAU_HINH tạm (cả bản N riêng lẫn bản N bên trong S)."""
    nha = tmp_path / "nha"
    nha.mkdir()
    monkeypatch.setenv("HOME", str(nha))
    monkeypatch.setenv("USERPROFILE", str(nha))
    ch = nha / ".ebm-endnote.json"
    monkeypatch.setattr(N, "CAU_HINH", ch)
    monkeypatch.setattr(S.N, "CAU_HINH", ch)
    yield ch
    assert _dau_van(_THAT) == _DAU_VAN_THAT, "test đã chạm tệp cấu hình EndNote THẬT"


def _dash(tmp_path: Path) -> Path:
    d = tmp_path / "WebDashboard_X_20261015.html"
    d.write_text("x", encoding="utf-8", newline="\n")
    # Bố cục thật của EBM-Dashboards: kho toàn văn CẠNH dashboard. Từ 17/10/2026 thiếu kho thì --ap-dung ghi khối bị từ chối
    # (test_endnote_chan_ghi_khong_kho_20261017.py) — fixture phải đúng bố cục thật, không nới assertion.
    (tmp_path / "toan_van_oa").mkdir(exist_ok=True)
    return d


def _thu_vien(tmp_path: Path, ten: str = "Thu vien EBM.enl") -> Path:
    tv = tmp_path / ten
    tv.write_bytes(b"enl")
    return tv


# ── DN-02: nền tảng trước cấu hình ────────────────────────────────────────────────────────────────

def test_ngoai_mac_chua_cau_hinh_chi_thang_xuat_xml_khong_day_ghi_cau_hinh(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(N, "_la_mac", lambda: False)
    dash = _dash(tmp_path)
    assert N.main(["--file", str(dash), "--ap-dung"]) == N.MA_KHONG_CHAY
    out = capsys.readouterr().out
    assert "chỉ chạy trên macOS" in out and "--xuat-xml" in out and "--file <dashboard>" in out
    assert "--ghi-cau-hinh" not in out and "chưa cấu hình" not in out, out
    assert N.main(["--file", str(dash), "--ap-dung", "--im-khi-chua-cau-hinh"]) == N.MA_OK
    out = capsys.readouterr().out
    assert out.startswith("⚪ EndNote: bỏ qua — tự nhập vào EndNote chỉ chạy trên macOS") and "--xuat-xml" in out


def test_ghi_cau_hinh_ngoai_mac_canh_bao_tren_mac_thi_khong(tmp_path, monkeypatch, capsys, _cach_ly):
    tv = _thu_vien(tmp_path)
    monkeypatch.setattr(N, "_la_mac", lambda: False)
    assert N.main(["--ghi-cau-hinh", str(tv)]) == N.MA_OK
    out = capsys.readouterr().out
    assert "không phải macOS" in out and "--xuat-xml" in out
    assert N.doc_cau_hinh(_cach_ly)["thu_vien"] == str(tv.resolve())
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    assert N.main(["--ghi-cau-hinh", str(tv)]) == N.MA_OK
    assert "không phải macOS" not in capsys.readouterr().out


def test_sua_abstract_ngoai_mac_xet_nen_tang_truoc_cau_hinh(monkeypatch, capsys):
    monkeypatch.setattr(S.N, "_la_mac", lambda: False)
    assert S.main(["--pmid", "12345678"]) == S.MA_KHONG_DO
    out = capsys.readouterr().out
    assert "chỉ chạy trên macOS" in out and "--xuat-xml" in out and "bản ghi MỚI" in out
    assert "chưa cấu hình" not in out and "--ghi-cau-hinh" not in out, out


# ── TT-09: cấu hình hỏng ≠ vắng ───────────────────────────────────────────────────────────────────

HONG = '{"thu_vien": "/thu-muc/Lib.enl", "nhom_theo_chu_de": {"SGLT2_CKD": "EBM · SGLT2'  # bị cắt cụt


@pytest.mark.parametrize("noi_dung,co_loi", [
    (None, False),
    ('{"thu_vien": "/a/Lib.enl", "ung_dung": "EndNote 2025"}', False),
    (HONG, True),
    ("[1, 2]", True),
    ('{"nhom_theo_chu_de": {"A": "EBM · A"}}', True),
    ("", True),
])
def test_ly_do_cau_hinh_hong_phan_biet_vang_hong_dung(tmp_path, noi_dung, co_loi):
    p = tmp_path / "ch.json"
    if noi_dung is not None:
        p.write_text(noi_dung, encoding="utf-8", newline="\n")
    assert bool(N.ly_do_cau_hinh_hong(p)) is co_loi


def test_main_cau_hinh_hong_bao_hong_khong_bao_chua_cau_hinh(tmp_path, monkeypatch, capsys, _cach_ly):
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    _cach_ly.write_text(HONG, encoding="utf-8", newline="\n")
    dash = _dash(tmp_path)
    assert N.main(["--file", str(dash), "--ap-dung", "--im-khi-chua-cau-hinh"]) == N.MA_OK
    out = capsys.readouterr().out
    assert f"⚪ EndNote: bỏ qua — tệp cấu hình hỏng — xem {_cach_ly}" in out and "chưa cấu hình" not in out, out
    assert N.main(["--file", str(dash), "--ap-dung"]) == N.MA_KHONG_CHAY
    out = capsys.readouterr().out
    assert out.startswith("✗ tệp cấu hình hỏng") and "--xac-nhan-cau-hinh-hong" in out
    assert _cach_ly.read_text(encoding="utf-8") == HONG, "chỉ đọc — không được đụng tệp hỏng"


def test_ghi_cau_hinh_tu_choi_ghi_de_tep_hong_khi_chua_xac_nhan(tmp_path, capsys, _cach_ly):
    _cach_ly.write_text(HONG, encoding="utf-8", newline="\n")
    tv = _thu_vien(tmp_path)
    with pytest.raises(N.CauHinhHong):
        N.ghi_cau_hinh(str(tv), "EndNote 2025", tep=_cach_ly)
    assert N.main(["--ghi-cau-hinh", str(tv)]) == N.MA_KHONG_CHAY
    assert "HỎNG" in capsys.readouterr().out
    assert _cach_ly.read_text(encoding="utf-8") == HONG, "tệp hỏng phải còn nguyên — bảng nhóm cứu tay được"
    assert list(_cach_ly.parent.glob("*.hong-*")) == []


def test_ghi_cau_hinh_xac_nhan_giu_ban_hong_roi_moi_ghi(tmp_path, capsys, _cach_ly):
    _cach_ly.write_text(HONG, encoding="utf-8", newline="\n")
    tv = _thu_vien(tmp_path)
    assert N.main(["--ghi-cau-hinh", str(tv), "--xac-nhan-cau-hinh-hong"]) == N.MA_OK
    out = capsys.readouterr().out
    ban = list(_cach_ly.parent.glob(".ebm-endnote.json.hong-*"))
    assert len(ban) == 1 and ban[0].read_text(encoding="utf-8") == HONG, ban
    assert str(ban[0]) in out
    assert N.doc_cau_hinh(_cach_ly) == {"thu_vien": str(tv.resolve()), "ung_dung": "EndNote 2025"}


def test_ghi_nhom_khong_ghi_de_tep_hong(_cach_ly):
    _cach_ly.write_text(HONG, encoding="utf-8", newline="\n")
    N.ghi_nhom("EBM_X", "EBM · X", _cach_ly)
    assert _cach_ly.read_text(encoding="utf-8") == HONG


def test_sua_abstract_cau_hinh_hong_bao_hong(monkeypatch, capsys, _cach_ly):
    monkeypatch.setattr(S.N, "_la_mac", lambda: True)
    _cach_ly.write_text(HONG, encoding="utf-8", newline="\n")
    assert S.main(["--pmid", "12345678"]) == S.MA_KHONG_DO
    out = capsys.readouterr().out
    assert "tệp cấu hình hỏng — xem" in out and "chưa cấu hình" not in out, out


# ── DN-03: so thư viện bằng định danh tệp ─────────────────────────────────────────────────────────

def test_cung_tep_lech_hoa_thuong_va_dang_chuan_unicode(tmp_path):
    tv = _thu_vien(tmp_path, "Thư viện EBM.enl")
    lech_hoa = str(tv.parent / "thư VIỆN ebm.ENL")
    nfd = unicodedata.normalize("NFD", str(tv))
    assert nfd != str(tv)
    assert N._cung_tep(lech_hoa, tv), "APFS không phân biệt hoa/thường — cùng một thư viện"
    assert N._cung_tep(nfd, tv), "NFD (AppleScript) và NFC (cấu hình) là cùng một tên"


def test_cung_tep_dung_dinh_danh_khong_dung_chuoi(tmp_path):
    tv = _thu_vien(tmp_path, "Lib.enl")
    lien_ket = tmp_path / "LienKetCung.enl"
    try:
        os.link(tv, lien_ket)
    except (OSError, NotImplementedError):
        pytest.skip("hệ tệp không cho liên kết cứng")
    assert N._cung_tep(lien_ket, tv), "khác tên, cùng inode ⇒ cùng tệp (chuỗi realpath nói khác)"
    khac = tmp_path / "lib.enl"
    khac.write_bytes(b"khac")
    if os.path.samefile(khac, tv):
        pytest.skip("hệ tệp không phân biệt hoa/thường — không dựng được hai tệp khác nhau chỉ lệch hoa/thường")
    assert not N._cung_tep(khac, tv), "hai tệp CÓ THẬT khác inode — không được gộp vì giống chữ"


def _en_gia(tv: Path, tra_loi):
    """EndNoteMac thật (bỏ hàm dựng — hàm dựng chặn pytest/máy không phải Mac), `_chay` giả ghi lại mọi lời gọi."""
    en = object.__new__(N.EndNoteMac)
    en.ung_dung, en.thu_vien, en.ten, en._csdl = "EndNote 2025", tv, tv.name, None
    en.goi = []

    def _chay(than, *doi_so, cho=600, trong_tell=True):
        en.goi.append({"than": than, "cho": cho, "trong_tell": trong_tell})
        return tra_loi(than, trong_tell)
    en._chay = _chay
    return en


def test_dang_mo_dung_thu_vien_nhan_duong_dan_lech_hoa_thuong(tmp_path):
    tv = _thu_vien(tmp_path, "Thư viện EBM.enl")
    lech = str(tv.parent / "THƯ VIỆN ebm.enl")
    en = _en_gia(tv, lambda than, tell: "true" if not tell else f"/khac/Other.enl\n{lech}\n")
    assert en.dang_mo_dung_thu_vien() is True
    en2 = _en_gia(tv, lambda than, tell: "true" if not tell else "/khac/Other.enl\n")
    assert en2.dang_mo_dung_thu_vien() is False


# ── gap_endnote_running: không bao giờ tự bật EndNote khi chỉ hỏi «đã mở chưa» ──────────────────────

def test_endnote_dang_tat_thi_khong_gui_tell_nao(tmp_path):
    tv = _thu_vien(tmp_path)

    def tra_loi(than, tell):
        if tell:
            raise AssertionError("gửi `tell application` khi EndNote đang tắt — chính phép kiểm sẽ bật EndNote lên")
        return "false"
    en = _en_gia(tv, tra_loi)
    assert en.dang_mo_dung_thu_vien() is False
    assert len(en.goi) == 1 and en.goi[0]["trong_tell"] is False
    assert "is running" in en.goi[0]["than"] and en.goi[0]["cho"] == N.CHO_KIEM_GIAY <= 30


@pytest.mark.parametrize("cho_het_o", ["dang_chay", "documents"])
def test_het_gio_tra_false_khong_treo_khong_nem(tmp_path, cho_het_o):
    tv = _thu_vien(tmp_path)

    def tra_loi(than, tell):
        if (cho_het_o == "dang_chay") != tell:
            raise subprocess.TimeoutExpired("osascript", N.CHO_KIEM_GIAY)
        return "true"
    en = _en_gia(tv, tra_loi)
    assert en.dang_mo_dung_thu_vien() is False
    assert all(g["cho"] == N.CHO_KIEM_GIAY for g in en.goi), en.goi


def test_chay_ngoai_tell_khong_boc_tell_application(tmp_path, monkeypatch):
    """Kiểm kịch bản THẬT gửi cho osascript (subprocess giả) — không chỉ kiểm cờ trong_tell."""
    nhan = []

    def run_gia(lenh, **kw):
        nhan.append((lenh, kw))
        return types.SimpleNamespace(returncode=0, stdout="false\n", stderr="")
    monkeypatch.setattr(N, "subprocess", types.SimpleNamespace(run=run_gia, TimeoutExpired=subprocess.TimeoutExpired))
    en = object.__new__(N.EndNoteMac)
    en.ung_dung, en.thu_vien = "EndNote 2025", _thu_vien(tmp_path)
    assert en.dang_chay() is False
    kich_ban = nhan[0][1]["input"]
    assert "tell application" not in kich_ban and 'application "EndNote 2025" is running' in kich_ban
    assert nhan[0][1]["timeout"] == N.CHO_KIEM_GIAY and nhan[0][1]["encoding"] == "utf-8"
    en._chay("return 1")
    assert 'tell application "EndNote 2025"' in nhan[1][1]["input"], "lệnh thường vẫn bọc tell"


class _MacTat(N.EndNoteMac):
    """EndNoteMac THẬT (dang_mo_dung_thu_vien thật) trên một máy mà EndNote đang tắt."""
    goi: list = []

    def __init__(self, ung_dung, thu_vien):
        self.ung_dung, self.thu_vien, self.ten, self._csdl = ung_dung, thu_vien, thu_vien.name, None

    def _chay(self, than, *doi_so, cho=600, trong_tell=True):
        _MacTat.goi.append(trong_tell)
        if trong_tell:
            raise AssertionError("gửi `tell application` khi EndNote đang tắt")
        return "false"

    def mo_thu_vien(self, cho_giay=40):
        raise AssertionError("--chi-khi-dang-mo mà vẫn tự mở EndNote")


def test_chi_khi_dang_mo_qua_main_khong_bat_endnote(tmp_path, monkeypatch, capsys):
    tv = _thu_vien(tmp_path)
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    monkeypatch.setattr(N, "doc_cau_hinh", lambda tep=None: {"thu_vien": str(tv), "ung_dung": "EndNote 2025"})
    monkeypatch.setattr(N, "EndNoteMac", _MacTat)
    _MacTat.goi = []
    ma = N.main(["--gan-kho", "--pmid", "555", "--kho-toan-van", str(tmp_path), "--ap-dung", "--chi-khi-dang-mo"])
    assert ma == N.MA_OK and "⚪ EndNote chưa mở" in capsys.readouterr().out
    assert _MacTat.goi == [False], "chỉ một phép kiểm `is running`, không một sự kiện `tell` nào"


# ── G3-D8 + W10: dòng tổng kết tóm tắt và cờ --chua-xac-minh ──────────────────────────────────────

def _bc(**kw):
    bc = {"trich_dan": 1, "co_ban_ghi": 1, "khong_co_ban_ghi": [], "khong_doi": 0, "se_ghi": 1, "da_ghi": 0,
          "loi": [], "sao_luu": None, "tom_tat_may": 0, "tom_tat_lech_so": [], "tham_khao_chua_tom_tat": []}
    bc.update(kw)
    return bc


def _tt_gia(bc):
    return types.SimpleNamespace(CHAN="chân cũ", CHAN_MAY="chân máy cũ", TEP_TOM_TAT_ABS="tom-tat-abstract-vi.json",
                                 nap_tom_tat_abstract=lambda d: {}, ghi_tom_tat=lambda *a, **k: bc)


def test_tom_tat_chay_kho_khong_mo_bang_dau_tich(tmp_path, capsys):
    dash = _dash(tmp_path)
    N.chay_tom_tat(object(), [dash], None, False, tt=_tt_gia(_bc()))
    out = capsys.readouterr().out
    assert out.startswith("ℹ Chạy khô · Tóm tắt tiếng Việt") and "✓" not in out and "sẽ ghi 1" in out, out
    N.chay_tom_tat(object(), [dash], None, True, tt=_tt_gia(_bc(da_ghi=1)))
    assert capsys.readouterr().out.startswith("✓ Tóm tắt tiếng Việt")


class _EnMo:
    def __init__(self, ung_dung, thu_vien):
        self.thu_vien = thu_vien

    def dang_mo_dung_thu_vien(self):
        return True


def test_main_tom_tat_vi_chay_kho_noi_ro_va_chuyen_co_chua_xac_minh(tmp_path, monkeypatch, capsys):
    tv = _thu_vien(tmp_path)
    dash = _dash(tmp_path)
    monkeypatch.setattr(N, "_la_mac", lambda: True)
    monkeypatch.setattr(N, "doc_cau_hinh", lambda tep=None: {"thu_vien": str(tv), "ung_dung": "EndNote 2025"})
    monkeypatch.setattr(N, "EndNoteMac", _EnMo)
    monkeypatch.setattr(N, "_nap_tom_tat", lambda: _tt_gia(_bc()))
    assert N.main(["--file", str(dash), "--tom-tat-vi"]) == N.MA_OK
    out = capsys.readouterr().out
    assert "Chạy khô — chưa ghi tóm tắt nào. Thêm --ap-dung để ghi." in out and "✓" not in out, out
    nhan = []
    monkeypatch.setattr(N, "chay_tom_tat", lambda *a, **k: nhan.append(k) or _bc())
    N.main(["--file", str(dash), "--tom-tat-vi", "--ap-dung", "--chua-xac-minh"])
    monkeypatch.setattr(N, "nap_nhieu", lambda *a, **k: [])
    N.main(["--file", str(dash), "--ap-dung", "--chua-xac-minh"])
    N.main(["--file", str(dash), "--ap-dung"])
    assert [k.get("chua_xac_minh") for k in nhan] == [True, True, False], nhan


def _tt_that_tra_khoi():
    """Mô-đun tóm tắt THẬT; `ghi_tom_tat` dựng khối bằng `khoi_tieng_viet` thật (đọc hằng CHAN/CHAN_MAY lúc chạy)."""
    tt = N._nap_tom_tat()
    muc = {"id": "ITEM-01", "title": "Điểm nhấn", "source": "X · 2024", "design": "RCT", "dateVersion": "2024",
           "pmid": "31111111", "doi": "10.1016/aaa", "gradeLevel": "mod", "decision": "apply",
           "action": "Làm X", "references": ["Phụ lục: Smith J. PMID 32222222"]}
    f = Path("/khong-ton-tai/WebDashboard_X_20261015.html")
    ds = tt.ngu_canh([f], lambda p: {"meta": {"question": "Câu hỏi"}, "items": [muc]})

    def ghi_tom_tat(*a, **k):
        return _bc(khoi=[tt.khoi_tieng_viet(ds["pmid:31111111"], None),
                         tt.khoi_tieng_viet(ds["pmid:32222222"], None)])
    tt.ghi_tom_tat = ghi_tom_tat
    return tt


def test_chua_xac_minh_khoi_doc_nhanh_ghi_ro_va_khong_noi_da_qua_cong(tmp_path, capsys):
    dash = _dash(tmp_path)
    tt = _tt_that_tra_khoi()
    chan_goc, chan_may_goc = tt.CHAN, tt.CHAN_MAY
    bc = N.chay_tom_tat(object(), [dash], None, True, tt=tt, chua_xac_minh=True)
    for khoi in bc["khoi"]:
        assert khoi.startswith(tt.MO_DAU), "dòng đầu giữ dấu mở — lượt chạy lại phải nhận ra để THAY khối"
        assert N.DONG_CHUA_XAC_MINH in khoi and "đã qua cổng" not in khoi, khoi
    assert "CHƯA PASS" in capsys.readouterr().out
    assert (tt.CHAN, tt.CHAN_MAY) == (chan_goc, chan_may_goc), "hằng của mô-đun tóm tắt phải được trả lại"
    bc2 = N.chay_tom_tat(object(), [dash], None, True, tt=tt)
    assert all(N.DONG_CHUA_XAC_MINH not in k for k in bc2["khoi"])
    assert bc2["khoi"][0].endswith(chan_goc)
