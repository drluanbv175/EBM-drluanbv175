# -*- coding: utf-8 -*-
"""Toàn văn MỌI trích dẫn + phiếu xác thực cho bác sĩ (11/10/2026) — `toan_van_theo_chu_de.py --moi-trich-dan`.

Bác sĩ: «đảm bảo tất cả phải được kiểm tra, đọc và tải toàn văn giúp tôi, nếu tài liệu không tải và đọc toàn văn được thì sẽ
đưa ra giải pháp để tôi xác thực». Ngoại tuyến: công cụ con và đường đọc là hàm giả; kho là thư mục tạm.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


tv = _nap("tools/toan_van_theo_chu_de.py", "_tv_mtd")


@pytest.fixture
def kho(tmp_path):
    k = tmp_path / "toan_van_oa"
    (k / "doc_sau").mkdir(parents=True)
    (k / "PMID-111_PMC9.xml").write_text("<article/>", encoding="utf-8", newline="\n")
    (k / "doc_sau" / "PMID-111.md").write_text("đọc sâu", encoding="utf-8", newline="\n")
    (k / "PMID-222_WTDM.pdf").write_bytes(b"%PDF-1.4")
    return k


def _chay_main(tmp_path, kho, monkeypatch, *, moi=True, extra=()):
    db = tmp_path / "WebDashboard_X_20261011.html"
    db.write_text("x", encoding="utf-8", newline="\n")
    monkeypatch.setattr(tv, "trich_dan_moi_dashboard", lambda ds: (["111", "222", "333", "444"], ["10.1234/chi-doi"]))
    monkeypatch.setattr(tv, "pmid_apply_thieu", lambda ds, k, g=None: [])
    lenh: list[list[str]] = []
    hoi: list[list[str]] = []

    def chay(cmd):
        lenh.append(cmd)
        return 0, ""

    def lap(ds):
        hoi.append(list(ds))
        return [{"pmid": "333", "cach": "trinh_duyet", "url": "https://www.nejm.org/doi/x", "mien": "www.nejm.org",
                 "dieu_khoan": "bac_si_uy_quyen"},
                {"pmid": "444", "cach": "bac_si_doc_truc_tiep", "url": "https://www.sciencedirect.com/x", "nxb": "Elsevier"}]
    bc = tmp_path / "bao-cao.md"
    argv = ["--dashboard", str(db), "--bao-cao", str(bc), *(["--moi-trich-dan"] if moi else []), *extra]
    assert tv.main(argv, chay=chay, kho=kho, lap_phieu=lap) == 0
    return bc.read_text(encoding="utf-8"), lenh, hoi


def test_moi_trich_dan_deu_co_mot_dong_trang_thai_hoac_giai_phap(tmp_path, kho, monkeypatch):
    noi, lenh, hoi = _chay_main(tmp_path, kho, monkeypatch)
    assert "5 trích dẫn: 2 đã đọc toàn văn (1 có bản đọc sâu) · 2 cần bác sĩ · 1 chỉ có DOI" in noi
    assert "| PMID 111 | ✓ máy có toàn văn — PMC truy cập mở (XML) · đã đọc sâu | — |" in noi
    assert "| PMID 222 | ✓ máy có toàn văn — kênh TDM của NXB (Wiley) |" in noi and "chưa có bản đọc sâu tự động" in noi
    dong_333 = next(d for d in noi.splitlines() if d.startswith("| 3 | PMID 333"))
    assert "Làn Chrome có uỷ quyền" in dong_333 and "https://www.nejm.org/doi/x" in dong_333
    assert "--bac-si-da-doc 444" in noi, "NXB cấm chưa uỷ quyền ⇒ bác sĩ đọc rồi ghi kết luận"
    assert "| 5 | DOI 10.1234/chi-doi |" in noi and "https://doi.org/10.1234/chi-doi" in noi
    assert hoi == [["333", "444"]], "chỉ dò đường đọc cho bài CHƯA đọc toàn văn"


def test_moi_trich_dan_khong_tran_va_gom_du_moi_pmid(tmp_path, kho, monkeypatch):
    _, lenh, _ = _chay_main(tmp_path, kho, monkeypatch)
    gom = next(c for c in lenh if "gom_toan_van_dashboard.py" in c[1])
    assert gom[gom.index("--pmid") + 1: gom.index("--unpaywall")] == ["111", "222", "333", "444"]
    assert not any("doc_toan_van_co_nguoi.py" in c[1] for c in lenh), "phiếu có cấu trúc thay cho bản in thô"


def test_tran_van_ap_dung_khi_khai_ro(tmp_path, kho, monkeypatch):
    noi, lenh, _ = _chay_main(tmp_path, kho, monkeypatch, extra=["--tran", "2"])
    gom = next(c for c in lenh if "gom_toan_van_dashboard.py" in c[1])
    assert gom[gom.index("--pmid") + 1: gom.index("--unpaywall")] == ["111", "222"]
    assert "DỜI sang lượt sau: 333, 444" in noi


def test_khong_co_co_thi_giu_hanh_vi_cu(tmp_path, kho, monkeypatch):
    noi, _, hoi = _chay_main(tmp_path, kho, monkeypatch, moi=False)
    assert "PHIẾU XÁC THỰC" not in noi and hoi == []


@pytest.mark.parametrize("p, can", [
    ({"pmid": "9", "cach": "khong_truy_cap"}, ["Find Full Text", "tác giả", "thư viện", "«Cân nhắc»"]),
    ({"pmid": "9", "cach": "oa_chua_gom", "pmcid": "PMC1"}, ["PMC1", "chạy lại"]),
    ({"pmid": "9", "cach": "chua_ro", "ly_do": "Europe PMC lỗi URLError"}, ["https://pubmed.ncbi.nlm.nih.gov/9/", "URLError"]),
    ({"pmid": "9", "cach": "trinh_duyet", "url": "u", "mien": "m", "dieu_khoan": "chua_kiem"}, ["điều khoản NXB về AI chưa kiểm"]),
    ({"pmid": "9", "cach": "chua_co"}, ["có mạng"]),
])
def test_moi_duong_doc_deu_co_giai_phap(p, can):
    gp = tv.giai_phap(p)
    for c in can:
        assert c in gp, (p["cach"], c, gp)


def test_bo_nam_chay_toan_van_truoc_endnote():
    src = (REPO / "tools" / "xuat_goi_cap_nhat.py").read_text(encoding="utf-8")
    i_tv = src.index('print("⑦ Toàn văn mọi trích dẫn…")')
    i_en = src.index('print("⑧ EndNote…")')
    assert i_tv < i_en, "toàn văn phải chạy TRƯỚC EndNote để PDF vừa gom được gắn ngay lúc nhập"
    assert '"--moi-trich-dan"' in src[i_tv:i_en]
