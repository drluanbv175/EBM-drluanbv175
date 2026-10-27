# -*- coding: utf-8 -*-
"""Antifacts hiện tiến độ đề tài nghiên cứu (27/10/2026) — `tools/build_antifacts.py` đọc sổ `exports/*/tien_do/TIEN_DO_*.json`.

Bác sĩ giao: «Bảng tiến độ đưa lên Antifacts». Antifacts chỉ ĐỌC sổ rồi trình bày; việc chưa xong bấm vào thì chép câu lệnh
«Tiếp tục mục …» để dán vào Claude. Ngoại tuyến hoàn toàn: sổ giả trong thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap():
    sp = importlib.util.spec_from_file_location("_build_antifacts_test_tien_do", REPO / "tools" / "build_antifacts.py")
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


BA = _nap()


def _so(**ghi_de) -> dict:
    so = {
        "schema": "de_tai/so_tien_do/v1",
        "study": "de-tai-gia",
        "ten_de_tai": "Đề tài giả",
        "tap_chi_dich": "Tạp chí giả",
        "cap_nhat": "2026-10-27",
        "ai": {"may": "Máy", "bs": "Bác sĩ"},
        "giai_doan": [{"id": "GĐ1", "ten": "Một", "tu": "01/11/2026", "den": "05/11/2026"},
                      {"id": "GĐ2", "ten": "Hai", "tu": "06/11/2026", "den": "10/11/2026"}],
        "viec": [
            {"id": "1.1", "gd": "GĐ1", "ten": "Đã xong", "ai": "may", "han": "01/11/2026", "trang_thai": "xong",
             "phu_thuoc": [], "do_song": ""},
            {"id": "1.2", "gd": "GĐ1", "ten": "Chờ bác sĩ", "ai": "bs", "han": "02/11/2026", "trang_thai": "cho_bs",
             "phu_thuoc": [], "do_song": ""},
            {"id": "1.3", "gd": "GĐ1", "ten": "Làm được", "ai": "may", "han": "03/11/2026", "trang_thai": "chua",
             "phu_thuoc": ["1.1"], "do_song": ""},
            {"id": "2.1", "gd": "GĐ2", "ten": "Bị chặn", "ai": "bs", "han": "07/11/2026", "trang_thai": "chua",
             "phu_thuoc": ["1.2"], "do_song": "approval_ledger G2"},
            {"id": "2.2", "gd": "GĐ2", "ten": "Đã ký", "ai": "bs", "han": "08/11/2026", "trang_thai": "xong",
             "phu_thuoc": [], "do_song": "approval_ledger G4"},
        ],
    }
    so.update(ghi_de)
    return so


def _ghi(goc: Path, ma: str, noi_dung) -> Path:
    thu_muc = goc / ma / "tien_do"
    thu_muc.mkdir(parents=True)
    tep = thu_muc / f"TIEN_DO_{ma}.json"
    tep.write_text(noi_dung if isinstance(noi_dung, str) else json.dumps(noi_dung, ensure_ascii=False), encoding="utf-8")
    return tep


def test_doc_so_va_tach_trang_thai_lam_duoc_voi_bi_chan(tmp_path):
    _ghi(tmp_path, "de-tai-gia", _so())
    [p] = BA.load_projects(tmp_path)
    tt = {v[0]: v[5] for v in p["viec"]}
    assert tt == {"1.1": "xong", "1.2": "cho_bs", "1.3": "san", "2.1": "khoa", "2.2": "xong"}
    assert (p["tong"], p["xong"]) == (5, 2)
    # Cổng cứng chỉ đếm việc đo bằng sổ cái phê duyệt.
    assert (p["cong_ky"], p["cong_tong"]) == (1, 2)
    assert p["gd_hien"] == 0
    assert [(g["xong"], g["tong"]) for g in p["giai_doan"]] == [(1, 3), (1, 2)]
    # Nhãn người làm lấy từ bảng «ai» của sổ.
    assert p["viec"][1][3] == "Bác sĩ"


def test_so_hong_hoac_sai_khuon_bi_bo_khong_lam_sap_trang(tmp_path, capsys):
    _ghi(tmp_path, "a-hong-json", "{không phải json")
    _ghi(tmp_path, "b-sai-schema", _so(schema="khac/v9"))
    sai_tt = _so()
    sai_tt["viec"][0]["trang_thai"] = "gan_xong"
    _ghi(tmp_path, "c-sai-trang-thai", sai_tt)
    sai_pt = _so()
    sai_pt["viec"][2]["phu_thuoc"] = ["9.9"]
    _ghi(tmp_path, "d-phu-thuoc-ma", sai_pt)
    _ghi(tmp_path, "e-tot", _so(study="e-tot"))
    ps = BA.load_projects(tmp_path)
    assert [p["ma"] for p in ps] == ["e-tot"]
    ra = capsys.readouterr().out
    assert ra.count("Bỏ qua sổ tiến độ") == 4


def test_khong_co_thu_muc_exports_tra_rong(tmp_path):
    assert BA.load_projects(tmp_path / "khong-co") == []


def test_trang_sinh_ra_co_muc_de_tai_va_chep_lenh(tmp_path, monkeypatch):
    _ghi(tmp_path / "exports", "de-tai-gia", _so())
    monkeypatch.setattr(BA, "EXPORTS_DIR", tmp_path / "exports")
    monkeypatch.setattr(BA, "DASH_DIR", tmp_path / "khong-co-dashboard")
    monkeypatch.setattr(BA, "LIBRARY_JSON", tmp_path / "khong-co-dashboard" / "library.json")
    monkeypatch.setattr(BA, "SCALES_JSON", tmp_path / "khong-co-thang-diem.json")
    monkeypatch.setattr(BA, "OUT_HTML", tmp_path / "Antifacts.html")
    BA.main()
    html = (tmp_path / "Antifacts.html").read_text(encoding="utf-8")
    assert "đề tài đang làm" in html
    assert '"projects": [{"ma": "de-tai-gia"' in html
    assert "function renderProjects" in html and "renderProjects()+" in html
    assert "Tiếp tục mục " in html
