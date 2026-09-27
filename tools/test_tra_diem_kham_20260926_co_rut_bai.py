#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy #5 (26/09/2026): điểm khám phải HIỆN cờ rút bài — không ẩn thẻ, không đổi decision.

Trước bản vá: thẻ đã duyệt decision='apply' đứng trên PMID 9500320 (Wakefield, đã rút) in «▶ [APPLY] …» y hệt một thẻ
sạch — `tra_diem_kham.py` không tra Retraction Watch ngoại tuyến, không đọc sổ xác minh. Nay phân loại qua hàm DÙNG CHUNG
`provenance_ledger.trang_thai_rut_the` (một luật gộp bất đối xứng cho cả sổ truy nguyên lẫn điểm khám) và in:
⛔ ĐÃ RÚT · ⛔ RÚT & ĐĂNG LẠI · 🟠 EoC · ⚪ chưa kiểm rút bài; thiếu mọi căn cứ ⇒ một dòng ⚪ đầu phiên.

Ngoại tuyến hoàn toàn: nền Retraction Watch là đối tượng GIẢ được tiêm vào; không đọc CSV thật, không ghi state/ thật.
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, bi_danh: str):
    spec = importlib.util.spec_from_file_location(bi_danh, TOOLS / ten)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[bi_danh] = mod
    spec.loader.exec_module(mod)
    return mod


tdk = _nap("tra_diem_kham.py", "tdk_rut_bai_0926")
pl = _nap("provenance_ledger.py", "pl_rut_bai_0926")


def _iso(so_ngay_truoc: int) -> str:
    return (datetime.now() - timedelta(days=so_ngay_truoc)).isoformat(timespec="seconds")


def the(pmid: str | None = "9500320", doi: str | None = None, decision: str = "apply") -> dict:
    src = {"agency": "Lancet"}
    if pmid:
        src["pmid"] = pmid
    if doi:
        src["doi"] = doi
    return {"id": "T-MMR", "topic": "Vắc xin MMR và rối loạn phổ tự kỷ ở trẻ em", "recommendation": "Khuyến cáo fixture",
            "decision": decision, "provenance": "from_doctor_master", "verification_status": "đã xác minh",
            "date_added": "2026-01-01", "source": src, "gradeLevel": "moderate"}


class RWGia:
    """Nền Retraction Watch giả: chỉ trả bản ghi DƯƠNG TÍNH đã khai; không thấy ⇒ None (KHÔNG BAO GIỜ 'ok')."""

    def __init__(self, theo_pmid: dict | None = None, theo_doi: dict | None = None):
        self.theo_pmid = theo_pmid or {}
        self.theo_doi = theo_doi
        self.goi: list[str] = []

    def tra(self, pmid):
        self.goi.append(f"pmid:{pmid}")
        return dict(self.theo_pmid[pmid], source="retraction_watch") if pmid in self.theo_pmid else None

    def __getattr__(self, ten):
        if ten == "tra_doi" and self.theo_doi is not None:
            return lambda doi: (dict(self.theo_doi[doi], source="retraction_watch") if doi in self.theo_doi else None)
        raise AttributeError(ten)


RW_WAKEFIELD = RWGia({"9500320": {"status": "retracted", "reason": "+Falsification/Fabrication of Data;",
                                  "notice_pmid": "20137807"}})


def _in(ket: list[dict], **kw) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        tdk.in_quick_view("vắc xin MMR tự kỷ trẻ em", ket, set(), 0.0, "khop", None, False, **kw)
    return buf.getvalue()


def _tra_tu(rw, so=None):
    return lambda c: pl.trang_thai_rut_the(c, rw, so or {})


# ── (1) hàm phân loại DÙNG CHUNG ────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "rw,so,card,mong",
    [
        (RW_WAKEFIELD, {}, the(), "duong"),
        (RWGia({"1": {"status": "expression_of_concern", "reason": "+Concerns;"}}), {}, the("1"), "eoc"),
        (RWGia({"2": {"status": "retracted", "reason": "+Retract and Replace;"}}), {}, the("2"), "rut_va_thay"),
        (None, {"pmid:3": {"ghi_chu_rut": "retracted", "da_rut": True, "rut_va_thay": True}}, the("3"), "rut_va_thay"),
        (None, {"pmid:4": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(5)}}, the("4"), "ok_con_han"),
        (None, {"pmid:5": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(45)}}, the("5"), "ok_qua_han"),
        (None, {"pmid:6": {"ghi_chu_rut": "ok"}}, the("6"), "ok_qua_han"),
        (None, {"pmid:7": {"ghi_chu_rut": "unresolved", "nghi_ma": True}}, the("7"), "khong_biet"),
        # Cờ DÍNH: lượt sau ghi 'ok' đè ghi_chu_rut nhưng dương tính cũ vẫn phải thắng (luật bất đối xứng).
        (None, {"pmid:8": {"ghi_chu_rut": "ok", "da_rut": True, "kiem_rut_luc": _iso(1)}}, the("8"), "duong"),
        (None, {"pmid:9": {"ghi_chu_rut": "ok", "quan_ngai": True, "kiem_rut_luc": _iso(1)}}, the("9"), "eoc"),
        (None, {"pmid:10": {"ghi_chu_rut": "ok", "nghi_ma": True, "kiem_rut_luc": _iso(1)}}, the("10"), "khong_biet"),
        # Thẻ chỉ có DOI: sổ tra theo khoá doi (nguyên dạng rồi chữ thường).
        (None, {"doi:10.1/abc": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(2)}}, the(None, "10.1/ABC"), "ok_con_han"),
        (None, {"doi:10.1/rut": {"ghi_chu_rut": "retracted", "da_rut": True}}, the(None, "10.1/rut"), "duong"),
        (RWGia(theo_doi={"10.9/x": {"status": "retracted", "reason": "+Error;"}}), {}, the(None, "10.9/x"), "duong"),
        # Không có dữ liệu ở đâu cả ⇒ KHÔNG BIẾT — RW im lặng KHÔNG BAO GIỜ là 'ok'.
        (RWGia(), {}, the("11"), "khong_biet"),
        (RWGia(), {}, the(None, "10.1/khong"), "khong_biet"),
        (None, {}, {"id": "X", "decision": "apply"}, "khong_biet"),
    ],
)
def test_phan_loai_dung_chung(rw, so, card, mong):
    assert pl.trang_thai_rut_the(card, rw, so)["muc"] == mong


def test_rw_im_lang_va_so_ok_con_han_thi_moi_la_ok():
    """'ok' CHỈ đến từ sổ (nguồn sống đã trả bản ghi) — RW không có bản ghi không cộng thêm gì."""
    kq = pl.trang_thai_rut_the(the("12"), RWGia(), {"pmid:12": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(3)}})
    assert kq["muc"] == "ok_con_han"
    assert kq["nguon"] == ["sổ xác minh"]


def test_duong_tinh_rw_thang_so_ok():
    kq = pl.trang_thai_rut_the(the(), RW_WAKEFIELD, {"pmid:9500320": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(1)}})
    assert kq["muc"] == "duong"
    assert kq["thong_bao"] == "PMID 20137807"


# ── (2) hiển thị ở điểm khám ───────────────────────────────────────────────────────────────────────────────
def test_the_nguon_da_rut_in_dai_do_o_dong_dau_the():
    out = _in([the()], tra_rut=_tra_tu(RW_WAKEFIELD))
    dong = out.splitlines()
    i_rut = next(i for i, d in enumerate(dong) if "⛔ NGUỒN ĐÃ BỊ RÚT" in d)
    i_the = next(i for i, d in enumerate(dong) if d.strip().startswith("▶ [APPLY]"))
    assert i_rut == i_the - 1, out            # dòng ĐẦU TIÊN của thẻ, ngay trước ▶
    assert "PMID 20137807" in dong[i_rut]
    assert "chưa kiểm rút bài" not in out     # đã có kết luận dương tính, không lẫn nhãn ⚪


def test_khong_an_the_khong_doi_decision():
    card = the()
    goc = copy.deepcopy(card)
    out = _in([card], tra_rut=_tra_tu(RW_WAKEFIELD))
    assert "▶ [APPLY] Vắc xin MMR" in out      # thẻ vẫn hiện, nhãn quyết định giữ nguyên
    assert card == goc                         # không đụng decision/gradeLevel/nội dung thẻ


def test_rut_va_thay_va_eoc_co_nhan_rieng():
    rw = RWGia({"2": {"status": "retracted", "reason": "+Retract and Replace;"},
                "1": {"status": "expression_of_concern", "reason": "+Concerns;"}})
    assert "⛔ RÚT & ĐĂNG LẠI" in _in([the("2")], tra_rut=_tra_tu(rw))
    out_eoc = _in([the("1")], tra_rut=_tra_tu(rw))
    assert "🟠 CÓ THÔNG BÁO QUAN NGẠI" in out_eoc
    assert "NGUỒN ĐÃ BỊ RÚT" not in out_eoc


def test_khong_co_du_lieu_thi_in_chua_kiem_khong_im_lang():
    out = _in([the("11")], tra_rut=_tra_tu(RWGia()))
    assert "⚪ chưa kiểm rút bài" in out
    assert "⛔" not in out


def test_so_ok_con_han_thi_khong_in_co_rut():
    out = _in([the("4")], tra_rut=_tra_tu(None, {"pmid:4": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(5)}}))
    assert "⛔" not in out and "🟠 CÓ THÔNG BÁO" not in out and "chưa kiểm rút bài" not in out


def test_so_ok_qua_han_bao_can_kiem_lai():
    out = _in([the("5")], tra_rut=_tra_tu(None, {"pmid:5": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(45)}}))
    assert "quá 30 ngày" in out


def test_mac_dinh_none_la_fail_closed():
    """Không truyền hàm tra (chữ ký cũ) ⇒ ⚪ đầu phiên + ⚪ từng thẻ, KHÔNG im lặng như thẻ sạch."""
    out = _in([the()])
    assert "⚪ KHÔNG KIỂM ĐƯỢC RÚT BÀI" in out
    assert "⚪ chưa kiểm rút bài" in out


def test_ghi_chu_loi_nap_duoc_in_ra():
    out = _in([the()], rut_ghi_chu=["chưa tải nền Retraction Watch (tools/tai_retraction_watch.py)"])
    assert "chưa tải nền Retraction Watch" in out


def test_ham_tra_loi_hoac_ket_qua_la_thanh_chua_biet():
    def hong(_c):
        raise RuntimeError("nổ")
    assert "⚪ chưa kiểm rút bài" in _in([the()], tra_rut=hong)
    assert "⚪ chưa kiểm rút bài" in _in([the()], tra_rut=lambda c: {"muc": "sach"})
    assert "⚪ chưa kiểm rút bài" in _in([the()], tra_rut=lambda c: None)


def test_khong_the_nao_thi_khong_in_dong_rut_bai():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        tdk.in_quick_view("câu không có thẻ", [], set(), 0.0, "khong_co", None, False)
    assert "RÚT BÀI" not in buf.getvalue()


# ── (3) nạp căn cứ + main() ───────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def goc_tam(tmp_path, monkeypatch):
    goc = tmp_path / "EBM-drluanbv175"
    (goc / "EBM_MASTER").mkdir(parents=True)
    monkeypatch.setattr(tdk, "GOC", goc)
    monkeypatch.setattr(tdk, "STATE", goc / "state")
    monkeypatch.setattr(tdk, "LEDGER", goc / "EBM_MASTER" / "EBM_MASTER.json")
    return goc


def _ghi_so(goc: Path, muc) -> None:
    p = goc / tdk.SO_XAC_MINH_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"muc": muc}) if not isinstance(muc, str) else muc, encoding="utf-8")


def test_dung_tra_rut_thieu_moi_can_cu_tra_none(goc_tam):
    tra, gc = tdk.dung_tra_rut_bai()
    assert tra is None
    assert any("repo y khoa" in g for g in gc) and any("sổ xác minh" in g for g in gc)


def test_dung_tra_rut_chi_co_so_van_tra_duoc(goc_tam):
    _ghi_so(goc_tam, {"pmid:4": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(2)}})
    tra, _gc = tdk.dung_tra_rut_bai()
    assert tra is not None and tra(the("4"))["muc"] == "ok_con_han"
    assert tra(the("999"))["muc"] == "khong_biet"


def test_so_hong_khong_bi_doc_thanh_so_rong(goc_tam):
    _ghi_so(goc_tam, "{hỏng")
    tra, gc = tdk.dung_tra_rut_bai()
    assert tra is None
    assert any("không đọc được" in g for g in gc)


def test_dung_tra_rut_voi_nen_rw_tiem_vao(goc_tam, monkeypatch):
    monkeypatch.setattr(tdk, "_nap_nen_rw", lambda: (RW_WAKEFIELD, ""))
    tra, _gc = tdk.dung_tra_rut_bai()
    assert tra(the())["muc"] == "duong"


def test_main_dau_cuoi_hien_co_rut(goc_tam, monkeypatch):
    tdk.LEDGER.write_text(json.dumps({"evidence_cards": [the()]}), encoding="utf-8")
    monkeypatch.setattr(tdk, "_nap_nen_rw", lambda: (RW_WAKEFIELD, ""))
    monkeypatch.setattr(sys, "argv", ["tra_diem_kham.py", "vắc xin MMR tự kỷ trẻ em"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert tdk.main() == 0
    out = buf.getvalue()
    assert "▶ [APPLY]" in out, out
    assert "⛔ NGUỒN ĐÃ BỊ RÚT" in out, out
    assert "9500320" in RW_WAKEFIELD.goi[-1]


def test_main_khong_the_khop_thi_khong_nap_can_cu_rut(goc_tam, monkeypatch):
    tdk.LEDGER.write_text(json.dumps({"evidence_cards": [the()]}), encoding="utf-8")

    def cam(*_a, **_k):  # pragma: no cover — chạy tới đây là lỗi
        raise AssertionError("không được nạp căn cứ rút bài khi không có thẻ khớp")

    monkeypatch.setattr(tdk, "dung_tra_rut_bai", cam)
    monkeypatch.setattr(sys, "argv", ["tra_diem_kham.py", "gãy xương đòn trẻ sơ sinh"])
    with contextlib.redirect_stdout(io.StringIO()):
        assert tdk.main() == 0


# ── (4) sổ truy nguyên toàn kho dùng CÙNG hàm — hành vi báo cáo giữ nguyên (+ cờ dính chặt hơn) ─────────────
def test_provenance_ledger_dung_ham_chung_phan_loai_dung(tmp_path, monkeypatch):
    goc = tmp_path / "goc"
    (goc / "EBM_MASTER").mkdir(parents=True)
    (goc / "EBM-Dashboards").mkdir()
    the_ = [
        dict(the("9500320"), id="C1"),                         # RW: đã rút, apply
        dict(the("2", decision="consider"), id="C2"),          # RW: EoC
        dict(the("3"), id="C3"),                               # sổ: rút & đăng lại
        dict(the("4"), id="C4"),                               # sổ: ok còn hạn
        dict(the("5"), id="C5"),                               # sổ: ok quá hạn
        dict(the("6"), id="C6"),                               # không có gì
        dict(the("8"), id="C8"),                               # cờ dính da_rut + ghi 'ok'
    ]
    so = {"pmid:3": {"ghi_chu_rut": "retracted", "da_rut": True, "rut_va_thay": True, "thong_bao_rut_doi": "10.9/tb",
                     "kiem_rut_luc": _iso(1), "xac_minh_luc": _iso(1)},
          "pmid:4": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(2), "xac_minh_luc": _iso(2)},
          "pmid:5": {"ghi_chu_rut": "ok", "kiem_rut_luc": _iso(60), "xac_minh_luc": _iso(60)},
          "pmid:8": {"ghi_chu_rut": "ok", "da_rut": True, "kiem_rut_luc": _iso(1), "xac_minh_luc": _iso(1)}}
    (goc / "EBM_MASTER" / "EBM_MASTER.json").write_text(json.dumps({"evidence_cards": the_}), encoding="utf-8")
    (goc / "EBM-Dashboards" / ".so-xac-minh-nguon.json").write_text(json.dumps({"muc": so}), encoding="utf-8")
    monkeypatch.setattr(pl, "GOC", goc)
    monkeypatch.setattr(pl, "LEDGER", goc / "EBM_MASTER" / "EBM_MASTER.json")
    monkeypatch.setattr(pl, "SO", goc / "EBM-Dashboards" / ".so-xac-minh-nguon.json")
    rw = RWGia({"9500320": {"status": "retracted", "reason": "+Falsification;"},
                "2": {"status": "expression_of_concern", "reason": "+Concerns;"}})
    monkeypatch.setattr(pl, "_nap_rw", lambda: rw)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = pl.main()
    assert rc == 1
    bc = next((goc / "reports").glob("provenance-*.md")).read_text(encoding="utf-8")
    assert ("- Phân loại: {'dương tính': 4, 'ok (rút bài còn hạn 30d)': 1, "
            "'ok NHƯNG QUÁ HẠN 30d — cần kiểm lại': 1, 'KHÔNG BIẾT (chưa nguồn sống nào kết luận)': 1}") in bc, bc
    assert "C3 · decision=**apply** · PMID 3 / DOI None — RÚT & ĐĂNG LẠI (đối chiếu bản đã thay): retracted · thông báo: doi:10.9/tb" in bc
    assert "C2 · decision=**consider** · PMID 2 / DOI None — ĐÃ RÚT/EoC (không dùng): +Concerns;" in bc
    assert "C8 · decision=**apply** · PMID 8 / DOI None — ĐÃ RÚT/EoC (không dùng): retracted (cờ da_rut của sổ xác minh)" in bc
    canh_bao = next((goc / "alerts").glob("*.md")).read_text(encoding="utf-8")
    assert canh_bao.count("🔴 LEDGER") == 3           # C1, C3, C8 (apply); C2 là consider
