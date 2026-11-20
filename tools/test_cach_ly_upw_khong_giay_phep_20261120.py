# -*- coding: utf-8 -*-
"""Cách ly tệp Unpaywall CŨ không giấy phép mở (20/11/2026 — bác sĩ chọn «Dời ra kho cách ly (Khuyến nghị)»). Ngoại tuyến.

Chốt: (1) chỉ tệp tạo TRƯỚC mốc BH160 (tệp sau mốc đã qua cổng giấy phép lúc lưu); (2) tệp mang dấu Creative Commons hoặc
`--giu` ⇒ giữ; (3) chốt bảo phủ: dời làm mục apply mất bằng chứng toàn văn DUY NHẤT ⇒ giữ, trừ `--ca-muc-apply`; tệp khác cùng
PMID (CHR/PMC), hồ sơ làn trình duyệt, «bác sĩ đã đọc», hoặc tệp HTML không phải toàn văn ⇒ không chặn; (4) chạy khô không
đụng gì; `--ap-dung` CHUYỂN (không xoá) kèm manifest sha256, không ghi đè đích; (5) sau khi dời, cổng toàn văn vẫn xanh cho
mọi PMID không bị chốt. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap(duong: Path, ten: str):
    sp = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


C = _nap(REPO / "tools" / "cach_ly_upw_khong_giay_phep.py", "_clu_t")
V = _nap(REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py", "_clu_t_vd")

CU = dt.datetime(2026, 10, 3, 10, 0, tzinfo=dt.timezone.utc)
MOI = dt.datetime(2026, 11, 5, 10, 0, tzinfo=dt.timezone.utc)
TOAN_VAN_HTML = ("<html><body><h2>Introduction</h2><p>" + "từ " * 900 + "</p><h2>Methods</h2><p>" + "từ " * 900
                 + "</p><h2>Results</h2><p>" + "từ " * 900 + "</p><h2>Discussion</h2><p>" + "từ " * 900 + "</p></body></html>")
CC_HTML = TOAN_VAN_HTML.replace("</body>", '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY</a></body>')


def _muc(iid, dec, pmid):
    return "{id:'%s', decision:'%s', pmid:'%s'}" % (iid, dec, pmid)


def _kho(tmp_path, monkeypatch, tao: dict[str, dt.datetime]):
    dash = tmp_path / "EBM-Dashboards"
    kho = dash / "toan_van_oa"
    (kho / "trinh_duyet").mkdir(parents=True)
    tep = {
        "PMID-1000001_UPW.html": TOAN_VAN_HTML,   # apply, bằng chứng duy nhất ⇒ chốt giữ
        "PMID-1000002_UPW.html": TOAN_VAN_HTML,   # apply, có CHR ⇒ dời được
        "PMID-1000002_CHR.html": TOAN_VAN_HTML,
        "PMID-1000003_UPW.html": CC_HTML,         # có giấy phép ⇒ giữ
        "PMID-1000004_UPW.html": TOAN_VAN_HTML,   # consider ⇒ dời
        "PMID-1000005_UPW.html": TOAN_VAN_HTML,   # tạo SAU mốc ⇒ ngoài phạm vi
        "PMID-1000006_UPW.html": "<html><body>Fingerprint Access to Document</body></html>",  # trang giới thiệu, apply ⇒ dời
        "PMID-1000007_UPW.html": TOAN_VAN_HTML,   # apply, bác sĩ đã đọc ⇒ dời được
    }
    for ten, nd in tep.items():
        (kho / ten).write_text(nd, encoding="utf-8")
    (kho / "trinh_duyet" / "bac-si-da-doc.jsonl").write_text(json.dumps({"pmid": "1000007"}) + "\n", encoding="utf-8")
    (dash / "WebDashboard_EBM_VanDeCuThe_A_20261120.html").write_text(
        "<script>const DATA = {items:[" + ",".join([
            _muc("ITEM-01", "apply", "1000001"), _muc("ITEM-02", "apply", "1000002"), _muc("ITEM-03", "apply", "1000003"),
            _muc("ITEM-04", "consider", "1000004"), _muc("ITEM-05", "apply", "1000005"), _muc("ITEM-06", "apply", "1000006"),
            _muc("ITEM-07", "apply", "1000007")]) + "]};\n/* HẾT KHỐI DATA */</script>", encoding="utf-8")
    monkeypatch.setattr(C, "thoi_diem_tao", lambda p: tao.get(p.name, CU))
    return dash, kho


def test_phan_loai_pham_vi_giay_phep_va_chot_bao_phu(tmp_path, monkeypatch):
    dash, kho = _kho(tmp_path, monkeypatch, {"PMID-1000005_UPW.html": MOI})
    ds = {x["pmid"]: x for x in C.quet(kho, dash, truoc=C.MOC_BH160, V=V)}
    assert "1000005" not in ds, "tệp lưu sau bản vá BH160 đã qua cổng giấy phép — ngoài phạm vi"
    assert ds["1000003"]["giay_phep_mo"] and not ds["1000004"]["giay_phep_mo"]
    assert ds["1000001"]["mat_bao_phu_apply"], "bằng chứng duy nhất của mục apply"
    assert not ds["1000002"]["mat_bao_phu_apply"], "còn bản CHR"
    assert not ds["1000006"]["mat_bao_phu_apply"], "trang giới thiệu không phải toàn văn — dời không đổi bảo phủ"
    assert not ds["1000007"]["mat_bao_phu_apply"], "bác sĩ đã đọc"
    assert "1000005" in {x["pmid"] for x in C.quet(kho, dash, truoc=None, V=V)}, "--tat-ca bỏ mốc"
    assert C.quet(kho, dash, truoc=C.MOC_BH160, V=V, giu={"1000004"})[3]["giay_phep_mo"] is True


def test_chay_kho_khong_dung_gi_ap_dung_chuyen_kem_manifest(tmp_path, monkeypatch):
    dash, kho = _kho(tmp_path, monkeypatch, {"PMID-1000005_UPW.html": MOI})
    ds = C.quet(kho, dash, truoc=C.MOC_BH160, V=V)
    dich = dash / C.THU_MUC_CACH_LY / "upw-khong-giay-phep-mo-20261120"
    truoc = sorted(p.name for p in kho.iterdir())
    ma, dong = C.ap_dung(kho, dich, ds, ca_muc_apply=False, ghi=False)
    assert ma == 1 and not dich.exists() and sorted(p.name for p in kho.iterdir()) == truoc
    assert any("GIỮ PMID-1000001_UPW.html" in x for x in dong)
    sha = hashlib.sha256((kho / "PMID-1000004_UPW.html").read_bytes()).hexdigest()
    ma, dong = C.ap_dung(kho, dich, ds, ca_muc_apply=False, ghi=True)
    assert ma == 1
    da_doi = {"PMID-1000002_UPW.html", "PMID-1000004_UPW.html", "PMID-1000006_UPW.html", "PMID-1000007_UPW.html"}
    assert {p.name for p in dich.iterdir()} == da_doi | {"MANIFEST.json"}
    assert all(not (kho / t).exists() for t in da_doi)
    for t in ("PMID-1000001_UPW.html", "PMID-1000003_UPW.html", "PMID-1000005_UPW.html", "PMID-1000002_CHR.html"):
        assert (kho / t).exists(), t
    mf = json.loads((dich / "MANIFEST.json").read_text(encoding="utf-8"))
    assert {x["tep"]: x["sha256"] for x in mf["tep"]}["PMID-1000004_UPW.html"] == sha
    for pm in ("1000001", "1000002", "1000003", "1000005", "1000007"):
        assert V.co_toan_van_trong_kho(pm, kho), "cổng toàn văn vẫn xanh cho " + pm


def test_khong_ghi_de_dich_va_ca_muc_apply(tmp_path, monkeypatch):
    dash, kho = _kho(tmp_path, monkeypatch, {})
    ds = C.quet(kho, dash, truoc=C.MOC_BH160, V=V)
    dich = dash / C.THU_MUC_CACH_LY / "x"
    dich.mkdir(parents=True)
    (dich / "PMID-1000004_UPW.html").write_text("bản cũ", encoding="utf-8")
    ma, _ = C.ap_dung(kho, dich, ds, ca_muc_apply=False, ghi=True)
    assert ma == 3 and (kho / "PMID-1000004_UPW.html").exists() and (dich / "PMID-1000004_UPW.html").read_text() == "bản cũ"
    dich2 = dash / C.THU_MUC_CACH_LY / "y"
    ma, _ = C.ap_dung(kho, dich2, ds, ca_muc_apply=True, ghi=True)
    assert ma == 0 and (dich2 / "PMID-1000001_UPW.html").exists() and not V.co_toan_van_trong_kho("1000001", kho)


def test_dau_giay_phep_trong_pdf_va_loi_doc(tmp_path):
    assert C.DAU_CC.search("This article is licensed under a Creative Commons Attribution 4.0 International License")
    assert C.DAU_CC.search("© The Author(s) 2026. Open Access. CC BY-NC-ND")
    assert not C.DAU_CC.search("All rights reserved. For personal use only.")
    hong = tmp_path / "PMID-1_UPW.pdf"
    hong.write_bytes(b"%PDF-1.4 khong phai pdf that")
    assert C.co_giay_phep_mo(hong) is False, "PDF hỏng ⇒ không thấy giấy phép (không giữ vì đoán)"


def test_moc_mac_dinh_la_ban_va_bh160():
    assert C.MOC_BH160.isoformat() == "2026-10-04T13:47:32+07:00"
    assert C.THU_MUC_CACH_LY == "_cach_ly_toan_van" and os.sep not in C.THU_MUC_CACH_LY


# ── Bản in BANIN đi theo tệp nguồn (20/11/2026, tối) ─────────────────────────────────────────────────────────────────────
def _ban_in(kho, monkeypatch, nguon_theo_tep: dict[str, str]):
    """Tạo tệp BANIN giả; dải đầu trang (chữ trang 1) trả theo bảng — không cần PDF thật."""
    for ten in nguon_theo_tep:
        (kho / ten).write_bytes(b"%PDF-1.4 ban in gia")
    monkeypatch.setattr(C, "chu_trang_dau", lambda p: nguon_theo_tep.get(p.name, ""))


def test_ban_in_tu_upw_cach_ly_chuyen_theo_ban_in_tu_chr_giu_nguyen(tmp_path, monkeypatch):
    dash, kho = _kho(tmp_path, monkeypatch, {"PMID-1000005_UPW.html": MOI})
    _ban_in(kho, monkeypatch, {
        "PMID-1000004_BANIN.pdf": "BẢN IN TỪ KHO TOÀN VĂN EBM · PMID 1000004 · nguồn: PMID-1000004_UPW.html (Unpaywall)",
        "PMID-1000002_BANIN.pdf": "BẢN IN TỪ KHO TOÀN VĂN EBM · PMID 1000002 · nguồn: PMID-1000002_CHR.html (phiên Chrome)",
        "PMID-1000001_BANIN.pdf": "BẢN IN TỪ KHO TOÀN VĂN EBM · PMID 1000001 · nguồn: PMID-1000001_UPW.html (Unpaywall)",
        "PMID-1000003_BANIN.pdf": "",   # không đọc được dải đầu trang ⇒ không dời vì đoán
    })
    ds = C.quet(kho, dash, truoc=C.MOC_BH160, V=V)
    sap = {x["tep"] for x in ds if not x["giay_phep_mo"] and not x["mat_bao_phu_apply"]}
    bi = {x["pmid"]: x for x in C.quet_ban_in(kho, dash, sap)}
    assert set(bi) == {"1000004"}, "chỉ bản in ghi đúng nguồn UPW sắp cách ly; 1000001 bị chốt bảo phủ giữ ⇒ bản in cũng ở lại"
    dich = dash / C.THU_MUC_CACH_LY / "upw-khong-giay-phep-mo-20261120"
    ma, dong = C.ap_dung_ban_in(kho, dich, list(bi.values()), ghi=False)
    assert ma == 0 and not dich.exists() and (kho / "PMID-1000004_BANIN.pdf").exists(), "chạy khô không đụng gì"
    C.ap_dung(kho, dich, ds, ca_muc_apply=False, ghi=True)
    bi2 = C.quet_ban_in(kho, dash)          # sau khi dời: đọc từ MANIFEST
    assert [x["pmid"] for x in bi2] == ["1000004"]
    ma, dong = C.ap_dung_ban_in(kho, dich, bi2, ghi=True)
    assert ma == 0 and (dich / "PMID-1000004_BANIN.pdf").exists() and not (kho / "PMID-1000004_BANIN.pdf").exists()
    for t in ("PMID-1000002_BANIN.pdf", "PMID-1000001_BANIN.pdf", "PMID-1000003_BANIN.pdf"):
        assert (kho / t).exists(), t
    mf = json.loads((dich / "MANIFEST.json").read_text(encoding="utf-8"))
    ban_in = [x for x in mf["tep"] if x.get("loai") == "ban_in"]
    assert len(ban_in) == 1 and ban_in[0]["nguon_ban_in"] == "PMID-1000004_UPW.html" and len(ban_in[0]["sha256"]) == 64
    assert any("không còn toàn văn" in x and "1000004" in x for x in dong), "1000004 không còn tệp nào ⇒ báo lấy lại"
    assert C.quet_ban_in(kho, dash) == [], "chạy lại không còn gì"


def test_ban_in_goi_y_in_lai_khi_con_chr_va_khong_ghi_de(tmp_path, monkeypatch):
    dash, kho = _kho(tmp_path, monkeypatch, {})
    _ban_in(kho, monkeypatch, {"PMID-1000002_BANIN.pdf": "nguồn: PMID-1000002_UPW.html (Unpaywall)"})
    ds = C.quet(kho, dash, truoc=C.MOC_BH160, V=V)
    dich = dash / C.THU_MUC_CACH_LY / "z"
    C.ap_dung(kho, dich, ds, ca_muc_apply=False, ghi=True)
    bi = C.quet_ban_in(kho, dash)
    assert [x["con_nguon_khac"] for x in bi] == [["PMID-1000002_CHR.html"]]
    ma, dong = C.ap_dung_ban_in(kho, dich, bi, ghi=False)
    assert any("in_pdf_toan_van_kho.py --pmid 1000002 --ap-dung" in x for x in dong)
    (dich / "PMID-1000002_BANIN.pdf").write_bytes(b"ban cu")
    ma, _ = C.ap_dung_ban_in(kho, dich, bi, ghi=True)
    assert ma == 3 and (kho / "PMID-1000002_BANIN.pdf").exists(), "đích đã có ⇒ không ghi đè, không dời"


def test_ban_in_khong_doi_khi_tep_nguon_da_duoc_dua_lai_kho(tmp_path, monkeypatch):
    dash, kho = _kho(tmp_path, monkeypatch, {})
    _ban_in(kho, monkeypatch, {"PMID-1000004_BANIN.pdf": "nguồn: PMID-1000004_UPW.html (Unpaywall)"})
    ds = C.quet(kho, dash, truoc=C.MOC_BH160, V=V)
    dich = dash / C.THU_MUC_CACH_LY / "w"
    C.ap_dung(kho, dich, ds, ca_muc_apply=False, ghi=True)
    (kho / "PMID-1000004_UPW.html").write_bytes((dich / "PMID-1000004_UPW.html").read_bytes())  # bác sĩ đưa tệp lại kho
    assert C.quet_ban_in(kho, dash) == [], "tệp nguồn đã về kho ⇒ manifest cũ không còn là căn cứ dời bản in"
