# -*- coding: utf-8 -*-
"""Làn Chrome + kho toàn văn — sổ phiên, kho vắng, khuôn kho tóm tắt, hòm thư (15/10/2026, nhóm G3 của đợt rà làn Chrome + EndNote).

Khoá bằng HÀNH VI (ngoại tuyến, thư mục tạm):
  • TT-02 — `--mo` ghi đè sổ phiên (mất nhật ký SHA-256 + lời bác sĩ của phiên trước); sổ HỎNG bị coi như «không có phiên» rồi
    bị ghi đè. Nay phiên cũ được lưu trữ `state/phien-uy-quyen-chrome/<mã>.json`; sổ hỏng ⇒ `--mo`/`--dung`/`--trang-thai` mã 2.
  • TT-05 / W9 — công cụ GHI tự tạo `EBM-Dashboards/toan_van_oa` khi kho vắng (`--khong-truy-cap`, gom, phiên Chrome) ⇒ kho ma,
    chốt ⚪ bị lật; gom còn văng traceback khi vắng engine. Nay ⚪ mã 2, không tạo gì.
  • TT-06 — `so_toan_van` với 0 dashboard in 🟢 mã 0 ⇒ ⚪ mã 2.
  • TT-08 — kho `tom-tat-abstract-vi.json` khoá sai bị bỏ IM LẶNG ⇒ `--mau` in khuôn; khoá lạ vào `loi`; mục rỗng = «chưa tóm tắt».
  • TT-12 — hòm thư in «PMID » rỗng cho ứng viên chỉ có DOI; một dòng JSONL hỏng làm sập việc dựng hòm thư.
  • W2/W5 — `--huong-dan` trỏ tới phiên uỷ quyền (`--kiem`/`--nhan`) và bước 0 gom có `--unpaywall`.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


P = _nap("tools/phien_uy_quyen_chrome.py", "_puq_lc1015")
dtv = _nap("tools/doc_toan_van_co_nguoi.py", "_dtv_lc1015")
g = _nap("tools/gom_toan_van_dashboard.py", "_gom_lc1015")
stv = _nap("tools/so_toan_van.py", "_stv_lc1015")
tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_lc1015")
dht = _nap("tools/dung_hom_thu.py", "_dht_lc1015")

T0 = datetime(2026, 10, 14, 9, 0, 0, tzinfo=timezone(timedelta(hours=7)))
LOI = "uỷ quyền phiên: đọc và lưu toàn văn các bài trong phiếu hôm nay"
URL = "https://www.sciencedirect.com/science/article/pii/S0741521421008934"


def _dtv_gia():
    bang = {"Elsevier": {"ket_luan": "cam", "doi": ("10.1016/",), "mien": ("sciencedirect.com",)}}
    return types.SimpleNamespace(DIEU_KHOAN_NXB=bang,
                                 nxb_cua=lambda doi="", url="", tieu_de="": ("Elsevier", bang["Elsevier"])
                                 if P._mien(url).endswith("sciencedirect.com") else (None, None),
                                 uy_quyen_bac_si=lambda ten, hom_nay=None: {"nxb": ten})


# ── TT-02: sổ phiên không bị ghi đè ──────────────────────────────────────────────────────────────────────────────────
def test_mo_phien_moi_luu_tru_phien_cu_giu_nhat_ky(tmp_path):
    so = tmp_path / "state" / "phien.json"
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=_dtv_gia())[0] == 0
    cu = P.doc_phien(so)
    cu["lich_su"] = [{"luc": T0.isoformat(), "pmid": "55555555", "mien": "www.sciencedirect.com",
                      "tep": "PMID-55555555_CHR.pdf", "sha256": "cdefb4202c8f3017" + "0" * 48, "loai": "pdf"}]
    P._ghi(cu, so)
    hom_sau = T0 + timedelta(days=1)
    loi_moi = "uỷ quyền phiên hôm nay: đọc và lưu toàn văn trong phiếu W42"
    assert P.mo(loi_moi, bay_gio=hom_sau, tep=so, dtv=_dtv_gia())[0] == 0
    luu = P.thu_muc_luu_tru(so) / f"{cu['ma']}.json"
    assert luu.is_file(), "phiên cũ phải được lưu trữ trước khi sổ nhận phiên mới"
    d_luu = json.loads(luu.read_text(encoding="utf-8"))
    assert d_luu["can_cu"] == LOI and d_luu["lich_su"][0]["sha256"].startswith("cdefb4202c8f3017")
    moi = P.doc_phien(so)
    assert moi["ma"] != cu["ma"] and moi["can_cu"] == loi_moi and moi["lich_su"] == []


def test_so_phien_hong_khong_bi_ghi_de(tmp_path, monkeypatch, capsys):
    so = tmp_path / "state" / "phien.json"
    so.parent.mkdir(parents=True)
    hong = '{"ma": "20261014-090000", "mo_luc": "2026-10-14T09:00:00+07:00", "lich_su": [{"pmid": "5555'
    so.write_text(hong, encoding="utf-8")
    ma, tb = P.mo(LOI, bay_gio=T0, tep=so, dtv=_dtv_gia())
    assert ma == 2 and "KHÔNG ĐO ĐƯỢC" in tb
    assert P.dung(bay_gio=T0, tep=so)[0] == 2
    assert so.read_text(encoding="utf-8") == hong, "sổ hỏng (còn nhật ký phiên cũ) bị ghi đè"
    monkeypatch.setattr(P, "SO_PHIEN", so)
    assert P.main(["--trang-thai"]) == 2 and "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out
    assert P.phien_mo(T0, so) is None, "kiểm/nhận vẫn fail-closed: sổ hỏng ⇒ không có phiên"


# ── TT-05 / W9: không tự tạo kho ─────────────────────────────────────────────────────────────────────────────────────
def test_phien_mo_va_nhan_kho_vang_ma_2_khong_tao_kho(tmp_path, monkeypatch, capsys):
    kho = tmp_path / "EBM-Dashboards" / "toan_van_oa"
    so = tmp_path / "state" / "phien.json"
    monkeypatch.setattr(P, "KHO", kho)
    monkeypatch.setattr(P, "SO_PHIEN", so)
    assert P.main(["--mo", LOI]) == 2 and not so.exists() and not kho.parent.exists()
    assert "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out
    assert P.mo(LOI, bay_gio=T0, tep=so, dtv=_dtv_gia())[0] == 0
    ma = P.doc_phien(so)["ma"]
    tai = tmp_path / "tai.pdf"
    tai.write_bytes(b"%PDF-1.7\n" + b"0" * 30_000)
    kq, tb = P.nhan("34153348", tai, URL, bay_gio=T0, so=so, kho=kho, dtv=_dtv_gia())
    assert kq == 2 and "KHÔNG ĐO ĐƯỢC" in tb and ma
    assert not kho.parent.exists() and tai.exists(), "kho ma bị tạo hoặc tệp tải về bị xoá"


def test_khong_truy_cap_kho_vang_ma_2_khong_tao_kho(tmp_path, monkeypatch, capsys):
    kho = tmp_path / "EBM-Dashboards" / "toan_van_oa"
    monkeypatch.setattr(dtv, "KHO", kho)
    assert dtv.main(["--khong-truy-cap", "42377292", "--ly-do", "tạp chí đòi mua bài"]) == 2
    assert not kho.parent.exists() and "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out
    kho.mkdir(parents=True)
    assert dtv.main(["--khong-truy-cap", "42377292", "--ly-do", "tạp chí đòi mua bài"]) == 0
    assert (kho / "trinh_duyet" / "khong-truy-cap.jsonl").is_file()


def _argv(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["gom_toan_van_dashboard.py", *argv])


def test_gom_kho_vang_ma_2_khong_tao_kho(tmp_path, monkeypatch, capsys):
    kho = tmp_path / "EBM-Dashboards" / "toan_van_oa"
    monkeypatch.setattr(g, "KHO", kho)
    monkeypatch.setattr(g, "_nap_gom", lambda: (_ for _ in ()).throw(AssertionError("không được nạp engine khi kho vắng")))
    _argv(monkeypatch, "--pmid", "12345678")
    assert g.main() == 2 and not kho.parent.exists()
    assert "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out


def test_gom_vang_engine_mot_dong_khong_traceback(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(g, "KHO", tmp_path)

    def vang():
        raise FileNotFoundError("…/medical-ebm-automation/tools/gom_toan_van_oa.py")
    monkeypatch.setattr(g, "_nap_gom", vang)
    _argv(monkeypatch, "--pmid", "12345678")
    assert g.main() == 2
    out = capsys.readouterr().out
    assert "thiếu engine" in out and not (tmp_path / "DO-PHU-OA.md").exists()


# ── TT-06: 0 dashboard ⇒ ⚪ ──────────────────────────────────────────────────────────────────────────────────────────
def test_so_toan_van_khong_dashboard_la_khong_do_duoc(tmp_path, capsys):
    dash = tmp_path / "EBM-Dashboards"
    (dash / "toan_van_oa").mkdir(parents=True)
    assert stv.main([], dash=dash, hom_nay=date(2026, 10, 15)) == 2
    out = capsys.readouterr().out
    assert "KHÔNG ĐO ĐƯỢC" in out and "🟢" not in out


# ── TT-08: khuôn kho tóm tắt máy ─────────────────────────────────────────────────────────────────────────────────────
def test_mau_kho_tom_tat_dung_khoa_hop_le(capsys):
    assert tt.main(["--mau"]) == 0
    mau = json.loads(capsys.readouterr().out)
    assert tt.kiem_kho_tom_tat(mau["muc"]) == []
    for v in mau["muc"].values():
        assert set(v) == set(tt.KHOA_TRUONG_TOM_TAT) == {"thiet_ke", "P", "I", "C", "O", "ket_qua", "han_che", "ket_luan"}


def test_kiem_kho_bao_khoa_la_va_dinh_danh_sai():
    loi = tt.kiem_kho_tom_tat({"PMID 1": {"design": "RCT", "P": "a"}, "pmid:2": {"P": "b"}, "DOI 10.1000/ABC": {"P": "c"},
                               "PMID 3": {"thiết kế": "RCT", "kết quả": "x"}})
    noi = " | ".join(loi)
    assert "design" in noi and "«pmid:2» sai dạng" in noi and "chữ thường" in noi and "thiết kế" in noi
    assert len(loi) == 4


class _EndNoteGia:
    def __init__(self, abstract, khop):
        self.abstract, self.khop, self.thu_vien = dict(abstract), khop, Path("/khong-ton-tai/tv.enl")

    def tim_khop(self, gia_tri, truong):
        return {v: self.khop[v] for v in gia_tri if v in self.khop}

    def doc_truong(self, ids, truong):
        return {m: self.abstract.get(m, "") for m in ids}

    def ghi_truong(self, cap, truong):
        return {m: "" for m, _ in cap}


def test_ghi_tom_tat_khoa_sai_bao_loi_va_tinh_chua_tom_tat():
    muc = {"id": "ITEM-01", "title": "Mục", "pmid": "31111111", "decision": "consider", "gradeLevel": "mod",
           "references": ["Phụ lục: Smith J. Stroke 2020. PMID 32222222"]}
    f = Path("/khong-ton-tai/WebDashboard_X_20261015.html")
    doc = lambda p: {"meta": {"question": "Q"}, "items": [muc]} if Path(p).name == f.name else None  # noqa: E731
    en = _EndNoteGia({"r1": "A.", "r2": "B."}, {"31111111": ["r1"], "32222222": ["r2"]})
    bc = tt.ghi_tom_tat(en, [f], kho=None, ap_dung=False, doc_data=doc,
                        tom_tat_abs={"PMID 32222222": {"design": "RCT", "population": "người lớn"}})
    assert bc["tham_khao_chua_tom_tat"] == ["PMID 32222222"], "mục chỉ có khoá lạ = chưa tóm tắt, không lọt khỏi danh sách"
    assert any("design" in x for x in bc["loi"]) and bc["tom_tat_may"] == 0


# ── TT-12: hòm thư ứng viên ngoài quét ───────────────────────────────────────────────────────────────────────────────
def test_hom_thu_ung_vien_chi_doi_va_dong_hong(tmp_path):
    uv = tmp_path / "ung-vien-ngoai-quet.jsonl"
    uv.write_text("\n".join([
        json.dumps({"pmid": "", "doi": "10.1093/eurheartj/ehae999", "title": "Bài chỉ có DOI", "trang_thai": "CANDIDATE",
                    "nguon_phat_hien": "Scopus"}, ensure_ascii=False),
        '{"pmid": "41234567", "title": "dòng ghi dở", "trang_thai": "CANDID',
        json.dumps({"pmid": "40000001", "title": "Bài có PMID", "trang_thai": "CANDIDATE", "nguon_phat_hien": "WoS"},
                   ensure_ascii=False),
    ]) + "\n", encoding="utf-8")
    html = dht.khoi_ung_vien(uv)
    assert "doi:10.1093/eurheartj/ehae999" in html and "PMID  —" not in html, "ứng viên chỉ có DOI hiện «PMID » rỗng"
    assert "PMID 40000001" in html and "1 dòng hỏng" in html
    assert dht.khoi_ung_vien(tmp_path / "khong-co.jsonl") == ""


# ── W2/W5: hướng dẫn làn trình duyệt ─────────────────────────────────────────────────────────────────────────────────
def test_huong_dan_tro_toi_phien_uy_quyen_va_unpaywall():
    hd = dtv.HUONG_DAN
    buoc0 = next(d for d in hd.splitlines() if d.strip().startswith("0."))
    assert "gom_toan_van_dashboard.py" in buoc0 and "--unpaywall" in buoc0
    assert "phien_uy_quyen_chrome.py" in hd and "--kiem" in hd and "--nhan" in hd
