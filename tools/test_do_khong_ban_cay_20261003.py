#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy 03/10/2026 (HV-13 · N11 · PM-14): PHÉP ĐO không được làm bẩn cây git khi không có gì MỚI.

Đo 02/10: `cloud-mirror/trang-thai-chung-cu.json` có 27 commit «chore» / 30 ngày mà diff chỉ là `sinh_luc` và các số tự trôi theo
lịch («94 ngày» → «95 ngày»); `sources_health.py` viết lại `data/sources.json` mỗi lượt chỉ để đổi `updated`/`last_probe_at`.
(Phần sổ nguồn có test riêng trong `test_sources_health_20260930_engine_vang.py`.) Ngoại tuyến."""
from __future__ import annotations

import ast
import copy
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, HERE / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


XC = _nap("_t_dkbc_xc", "xuat_trang_thai_cloud.py")

GUONG = {
    "sinh_luc": "2026-10-02T23:28:51",
    "may": "Mac",
    "co_du_lieu_dashboard_that": True,
    "bo_dem": {
        "do_tuoi_chung_cu": {"ma_thoat": 0, "stdout": "🟢 gói mới nhất 15/09/2026\n   64 chủ đề · trung vị 94 ngày · 60 chủ đề quá 35 ngày\n"
                                                      "   Lâu nhất: TimMach (117ng) · CapCuu (115ng)", "stderr": ""},
        "tu_de_xuat_viec": {"ma_thoat": 0, "stdout": "HỆ TỰ ĐỀ XUẤT VIỆC — 2026-10-02\n  Giác quan đo được: 17/17\n"
                                                     "  🟠 👤 C1a: 0/4 cổng cứng có chữ ký\n  🟡 🤖 Repo gốc: 1 file chưa commit\n"
                                                     "  🟡 🛎 kỳ 14/09/2026 18:00: lượt chạy TRỄ 16/09 08:08", "stderr": ""},
    },
    "so_da_duyet": {"quyet_dinh_da_duyet": {"quyet_dinh": [{"ma": "QD-01"}]}},
}


def _troi(g: dict, ngay: int) -> dict:
    """Bản sao «chỉ thời gian trôi»: tuổi + ngày, dấu sinh, số tệp chưa commit (chính tệp gương)."""
    import re
    m = copy.deepcopy(g)
    m["sinh_luc"] = (dt.datetime.fromisoformat(g["sinh_luc"]) + dt.timedelta(days=ngay)).isoformat(timespec="seconds")
    b = m["bo_dem"]
    b["do_tuoi_chung_cu"]["stdout"] = re.sub(r"(\d+)(ng\)| ngày)", lambda x: f"{int(x.group(1)) + ngay}{x.group(2)}",
                                             b["do_tuoi_chung_cu"]["stdout"])
    b["tu_de_xuat_viec"]["stdout"] = b["tu_de_xuat_viec"]["stdout"].replace("2026-10-02", "2026-10-04").replace(
        "1 file chưa commit", "2 file chưa commit")
    return m


def test_chi_thoi_gian_troi_thi_chu_ky_trung():
    assert XC.chu_ky_on_dinh(_troi(GUONG, 2)) == XC.chu_ky_on_dinh(GUONG)


def test_so_dem_that_doi_thi_chu_ky_khac():
    for cu, moi in (("0/4 cổng cứng", "1/4 cổng cứng"), ("17/17", "16/17"), ("64 chủ đề", "65 chủ đề"), ("🟠 👤 C1a", "🔴 👤 C1a")):
        g = copy.deepcopy(GUONG)
        for k in g["bo_dem"]:
            g["bo_dem"][k]["stdout"] = g["bo_dem"][k]["stdout"].replace(cu, moi)
        assert XC.chu_ky_on_dinh(g) != XC.chu_ky_on_dinh(GUONG), f"«{cu}» → «{moi}» là thay đổi THẬT, không được che"
    g = copy.deepcopy(GUONG)
    g["so_da_duyet"]["quyet_dinh_da_duyet"]["quyet_dinh"].append({"ma": "QD-02"})
    assert XC.chu_ky_on_dinh(g) != XC.chu_ky_on_dinh(GUONG)


def test_can_ghi(tmp_path):
    tep = tmp_path / "trang-thai-chung-cu.json"
    luc = dt.datetime.fromisoformat(GUONG["sinh_luc"])
    assert XC.can_ghi(GUONG, tep, luc)[0] is True, "gương vắng ⇒ ghi"
    tep.write_text("{hỏng", encoding="utf-8", newline="\n")
    assert XC.can_ghi(GUONG, tep, luc)[0] is True, "gương hỏng ⇒ ghi"
    tep.write_text(json.dumps(GUONG, ensure_ascii=False), encoding="utf-8", newline="\n")
    ghi, ly = XC.can_ghi(_troi(GUONG, 2), tep, luc + dt.timedelta(days=2))
    assert ghi is False and "không đổi" in ly
    assert XC.can_ghi(_troi(GUONG, 7), tep, luc + dt.timedelta(days=7))[0] is True, "≥ 7 ngày ⇒ làm mới định kỳ"
    g = copy.deepcopy(GUONG)
    g["bo_dem"]["tu_de_xuat_viec"]["ma_thoat"] = 1
    assert XC.can_ghi(g, tep, luc)[0] is True, "mã thoát đổi ⇒ ghi"


def _chay_main(monkeypatch, tmp_path, *argv) -> tuple[Path, str]:
    tep = tmp_path / "cloud-mirror" / "trang-thai-chung-cu.json"
    tep.parent.mkdir()
    tep.write_text(json.dumps(GUONG, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    monkeypatch.setattr(XC, "MIRROR_FILE", tep)
    monkeypatch.setattr(XC, "MIRROR_DIR", tep.parent)
    monkeypatch.setattr(XC, "DASH", tmp_path)        # có «EBM-Dashboards» ⇒ không vào nhánh máy-không-dữ-liệu
    monkeypatch.setattr(XC, "xay_trang_thai", lambda: _troi(GUONG, 1))
    monkeypatch.setattr(sys, "argv", ["xuat_trang_thai_cloud.py", *argv])
    assert XC.main() == 0
    return tep, tep.read_text(encoding="utf-8")


def test_main_khong_ghi_khi_chi_thoi_gian_troi(monkeypatch, tmp_path, capsys):
    _tep, nd = _chay_main(monkeypatch, tmp_path)
    assert json.loads(nd)["sinh_luc"] == GUONG["sinh_luc"] and "≡ Không ghi" in capsys.readouterr().out


def test_ep_ghi_van_ghi(monkeypatch, tmp_path):
    _tep, nd = _chay_main(monkeypatch, tmp_path, "--ep-ghi")
    assert json.loads(nd)["sinh_luc"] != GUONG["sinh_luc"]


def test_xuat_goi_cap_nhat_ep_ghi_guong_sau_khi_cap_nhat():
    """Bước ⑥ chạy NGAY sau khi một gói chứng cứ đổi — phải ép ghi, kể cả khi bộ đếm chỉ đổi số ngày."""
    cay = ast.parse((HERE / "xuat_goi_cap_nhat.py").read_text(encoding="utf-8"))
    goi = [n for n in ast.walk(cay) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "run" and n.args
           and isinstance(n.args[0], ast.List) and any(isinstance(e, ast.Call) and getattr(e.func, "id", "") == "str"
                                                       and getattr(e.args[0], "id", "") == "XUAT_CLOUD" for e in n.args[0].elts)]
    assert goi and any(isinstance(e, ast.Constant) and e.value == "--ep-ghi" for e in goi[0].args[0].elts)
