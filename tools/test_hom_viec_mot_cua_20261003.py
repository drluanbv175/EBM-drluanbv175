#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy 03/10/2026 — hòm việc một cửa (HV-02), giác quan PR chờ gộp (HV-04), ghi quyết định thẻ tuần (EV-10). Ngoại tuyến."""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


GD = _nap("_t_hv_gd", "ghi_duyet_the_tuan.py")
HV = _nap("_t_hv_hv", "hom_viec_mot_cua.py")
TD = _nap("_t_hv_td", "tu_de_xuat_viec.py")
THE7 = [f"W40-0{i}" for i in range(1, 8)]


# ── EV-10: ghi quyết định thẻ tuần ─────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("cau, mong", [
    ("duyệt W40: 1 ✓ 3 ✗ 5 hoãn", [("W40-01", "ap_dung"), ("W40-03", "khong"), ("W40-05", "hoan")]),
    ("W40-02 ✗ thiếu đối chứng", [("W40-02", "khong")]),
    ("duyet W40: 4 dong y, 6 khong, 7 de sau", [("W40-04", "ap_dung"), ("W40-06", "khong"), ("W40-07", "hoan")]),
    ("W40: 1 ✓ cho bệnh nhân béo phì", [("W40-01", "ap_dung")]),
])
def test_phan_tich_dung_loi_bac_si(cau, mong):
    qd, loi = GD.phan_tich(cau, THE7)
    assert loi == [] and [(q["the"], q["quyet_dinh"]) for q in qd] == mong


def test_ghi_chu_giu_nguyen_van():
    qd, _ = GD.phan_tich("W40-02 ✗ thiếu đối chứng", THE7)
    assert qd[0]["ghi_chu"] == "thiếu đối chứng"


@pytest.mark.parametrize("cau, mau", [
    ("duyệt: 1 ✓", "không thấy tuần"),
    ("W40: 1 ✓ 1 ✗", "hai lần"),
    ("W40: 9 ✓", "không có trong gói"),
    ("W40: tuyệt vời", "không thấy cặp"),
])
def test_tu_choi_khong_doan(cau, mau):
    _qd, loi = GD.phan_tich(cau, THE7)
    assert any(mau in x for x in loi), loi


def _goi(queue: Path, tuan: int = 40, so_the: int = 7, ngay_tuoi: int = 4) -> Path:
    queue.mkdir(parents=True, exist_ok=True)
    g = queue / f"tuan-2026-W{tuan}.md"
    g.write_text("## ⓶ THẺ\n" + "".join(f"**[W{tuan}-{i:02d}] tiêu đề**\nNguồn: PMID 4{i:07d}\n" for i in range(1, so_the + 1)),
                 encoding="utf-8", newline="\n")
    t = time.time() - ngay_tuoi * 86400
    os.utime(g, (t, t))
    return g


def test_ghi_va_doc_so_dong_moi_nhat_thang(tmp_path):
    so = tmp_path / "state" / "duyet-the-tuan.jsonl"
    qd, _ = GD.phan_tich("W40: 1 ✓ 2 hoãn", THE7)
    GD.ghi(qd, "câu 1", so)
    qd2, _ = GD.phan_tich("W40: 2 ✗", THE7)
    GD.ghi(qd2, "câu 2", so)
    d = GD.doc_so(so)
    assert d["W40-01"]["quyet_dinh"] == "ap_dung" and d["W40-02"]["quyet_dinh"] == "khong" and d["W40-02"]["nguoi_quyet"] == "bac_si"
    g = _goi(tmp_path / "queue")
    the, chua = GD.chua_quyet(g, so)
    assert the == THE7 and chua == THE7[2:]


def test_main_chay_thu_khong_ghi(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(GD, "QUEUE", tmp_path / "queue")
    monkeypatch.setattr(GD, "SO", tmp_path / "state" / "so.jsonl")
    _goi(tmp_path / "queue")
    assert GD.main(["duyệt W40: 1 ✓"]) == 0 and not (tmp_path / "state" / "so.jsonl").exists()
    assert GD.main(["duyệt W40: 9 ✓", "--ghi"]) == 3 and not (tmp_path / "state" / "so.jsonl").exists()
    assert GD.main(["duyệt W40: 1 ✓", "--ghi"]) == 0 and (tmp_path / "state" / "so.jsonl").exists()
    assert GD.main(["duyệt W41: 1 ✓"]) == 2, "không có gói tuần ⇒ không đo được, không ghi"


def test_giac_quan_the_tuan(tmp_path, monkeypatch):
    q = tmp_path / "queue"
    _goi(q, ngay_tuoi=4)
    so = tmp_path / "so.jsonl"
    ra = TD.giac_quan_the_tuan_chua_quyet(q, so=so)
    assert len(ra) == 1 and "7/7 thẻ gói tuan-2026-W40" in ra[0][1] and "ghi_duyet_the_tuan.py" in ra[0][2]
    GD.ghi(GD.phan_tich("W40: 1 ✓ 2 ✓ 3 ✓ 4 ✓ 5 ✓ 6 ✓ 7 ✗", THE7)[0], "đủ", so)
    assert TD.giac_quan_the_tuan_chua_quyet(q, so=so) == [], "đủ 7 quyết định ⇒ hết việc"
    _goi(q, ngay_tuoi=1)
    assert TD.giac_quan_the_tuan_chua_quyet(q, so=tmp_path / "trong.jsonl") == [], "gói < 3 ngày — chưa nhắc"
    truoc = len(TD._GIAC_QUAN_CHET)
    assert TD.giac_quan_the_tuan_chua_quyet(tmp_path / "khong-co") == [] and len(TD._GIAC_QUAN_CHET) == truoc + 1


# ── HV-04: PR chờ gộp ──────────────────────────────────────────────────────────────────────────────────────────────────
def _pr(so, tuoi_gio, ci, base="master", draft=False):
    tao = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=tuoi_gio)).isoformat().replace("+00:00", "Z")
    roll = {"xanh": [{"conclusion": "SUCCESS"}], "do": [{"conclusion": "FAILURE"}], "chay": [{"status": "IN_PROGRESS"}]}[ci]
    return {"number": so, "createdAt": tao, "baseRefName": base, "isDraft": draft, "statusCheckRollup": roll}


@pytest.fixture()
def khong_cloud(monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.setattr(TD, "_owner_repo_tu_remote", lambda d: "chu/repo")


def test_pr_cho_gop_dem_ci_xep_chong_va_bo_nhap(khong_cloud):
    prs = [_pr(89, 30, "xanh"), _pr(93, 10, "chay", base="claude/cong-mien-chan"), _pr(97, 5, "xanh", draft=True)]
    ra = TD.giac_quan_pr_cho_gop([("gốc", Path("."))], chay=lambda lenh: json.dumps(prs))
    assert len(ra) == 1
    uu, dong, lenh = ra[0]
    assert "2 PR chờ bác sĩ gộp" in dong and "#89" in dong and "#97" not in dong, "PR nháp không tính"
    assert "XẾP CHỒNG" in dong and "#93→claude/cong-mien-chan" in dong and uu == 2 and "SỐ PR" in lenh


def test_pr_do_hoac_cu_la_uu_tien_cao(khong_cloud):
    assert TD.giac_quan_pr_cho_gop([("gốc", Path("."))], chay=lambda lenh: json.dumps([_pr(1, 5, "do")]))[0][0] == 1
    assert TD.giac_quan_pr_cho_gop([("gốc", Path("."))], chay=lambda lenh: json.dumps([_pr(1, 60, "xanh")]))[0][0] == 1


def test_gh_khong_tra_loi_la_giac_quan_chet_khong_phai_0_pr(khong_cloud):
    truoc = len(TD._GIAC_QUAN_CHET)
    assert TD.giac_quan_pr_cho_gop([("gốc", Path("."))], chay=lambda lenh: "") == []
    assert len(TD._GIAC_QUAN_CHET) == truoc + 1
    assert TD.giac_quan_pr_cho_gop([("gốc", Path("."))], chay=lambda lenh: "[]") == [], "0 PR thật ⇒ không có việc"


def test_cloud_khong_doan(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    truoc = len(TD._GIAC_QUAN_CHET)
    assert TD.giac_quan_pr_cho_gop([("gốc", Path("."))], chay=lambda lenh: pytest.fail("không được gọi gh trên Cloud")) == []
    assert len(TD._GIAC_QUAN_CHET) == truoc + 1


# ── HV-02: hòm việc một cửa ────────────────────────────────────────────────────────────────────────────────────────────
def _bang(n_bs=3, n_chuong=1, n_may=2, chet=(), sinh="2026-10-03T07:00:00"):
    viec = ([{"uu": 2, "ai": "👤", "viec": f"việc bác sĩ {i}", "lenh": "x"} for i in range(n_bs)]
            + [{"uu": 1, "ai": "👤", "viec": "việc bác sĩ GẤP", "lenh": "x"}]
            + [{"uu": 2, "ai": "🛎", "viec": f"chờ người chạy {i}", "lenh": "x"} for i in range(n_chuong)]
            + [{"uu": 2, "ai": "🤖", "viec": f"máy {i}", "lenh": "x"} for i in range(n_may)])
    return {"sinh_luc": sinh, "chet": list(chet), "viec": viec}


def test_dong_hom_uu_tien_va_tran_12():
    ra = HV.dong_hom(_bang(n_bs=20), dt.datetime(2026, 10, 3, 8))
    assert len(ra) <= 12 and "việc bác sĩ GẤP" in ra[1], "🟠 phải đứng đầu"
    assert "+" in ra[-1] and "tu_de_xuat_viec.py" in ra[-1]
    assert not any("máy 0" in x for x in ra), "🤖 chỉ được đếm, không chiếm dòng"
    it = HV.dong_hom(_bang(n_bs=1, n_chuong=1, n_may=3), dt.datetime(2026, 10, 3, 8))
    assert not any("máy " in x for x in it[1:]) and "3 máy tự lo" in it[0], "🤖 chỉ đếm ở dòng đầu, kể cả khi còn chỗ"


def test_dong_hom_bang_cu_va_vang():
    ra = HV.dong_hom(_bang(), dt.datetime(2026, 10, 4, 12))
    assert "bảng cũ 29 giờ" in ra[0]
    assert "chưa có bảng" in HV.dong_hom(None)[0]
    xanh = HV.dong_hom({"sinh_luc": "2026-10-03T07:00:00", "chet": [], "viec": []}, dt.datetime(2026, 10, 3, 8))
    assert "🟢" in xanh[-1]
    chet = HV.dong_hom({"sinh_luc": "2026-10-03T07:00:00", "chet": ["x"], "viec": []}, dt.datetime(2026, 10, 3, 8))
    assert "🟢" not in chet[-1] and "⚪ 1 giác quan" in chet[-1], "giác quan chết ⇒ không được nói «không có việc»"


def test_khoa_tuoi_thi_khong_phong_va_khong_chay_chong(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(HV, "KHOA", tmp_path / "hom-viec.khoa")
    (tmp_path / "hom-viec.khoa").write_text("", encoding="utf-8")
    assert HV.phong_nen() is False
    assert HV.lam_moi(tmp_path / "hv.json") == 0 and "không chạy chồng" in capsys.readouterr().out
    assert not (tmp_path / "hv.json").exists()


def test_main_doc_khong_goi_mang_va_ma_0(tmp_path, monkeypatch, capsys):
    tep = tmp_path / "hv.json"
    tep.write_text(json.dumps(_bang(sinh=dt.datetime.now().isoformat(timespec="seconds"))), encoding="utf-8")
    monkeypatch.setattr(HV, "TEP", tep)
    monkeypatch.setattr(HV, "phong_nen", lambda: pytest.fail("bảng còn tươi thì không phóng làm mới"))
    assert HV.main(["--doc", "--lam-moi-nen"]) == 0 and "HÒM VIỆC" in capsys.readouterr().out


def test_ghi_json_cua_tu_de_xuat_viec(tmp_path):
    tep = tmp_path / "state" / "hv.json"
    TD.ghi_json([(1, "👤", "a", "b"), (2, "🤖", "c", "d")], ["x (y)"], tep, 20)
    d = json.loads(tep.read_text(encoding="utf-8"))
    assert d["giac_quan"] == 20 and d["chet"] == ["x (y)"] and d["viec"][0] == {"uu": 1, "ai": "👤", "viec": "a", "lenh": "b"}
    assert HV.doc(tep) is not None


def test_hook_nguon_co_hom_viec_va_nhanh():
    d = json.loads((TOOLS.parent / "sync" / "hooks-sessionstart.json").read_text(encoding="utf-8"))
    h = [x for g in d["SessionStart"] for x in g["hooks"] if "hom_viec_mot_cua.py" in x.get("command", "")]
    assert len(h) == 1 and "--doc --lam-moi-nen" in h[0]["command"] and h[0]["timeout"] <= 10


def test_dinh_tuyen_hom_viec_va_duyet_the():
    sys.path.insert(0, str(TOOLS / "orchestrator"))
    it = _nap("_t_hv_it", "orchestrator/intent.py")
    assert it.route("hòm việc của tôi còn gì").target == "tools/hom_viec_mot_cua.py"
    assert it.route("ghi duyệt W40: 1 ✓ 3 ✗").target == "tools/ghi_duyet_the_tuan.py"
    assert it.route("đọc toàn văn các thẻ tuần W40").target != "tools/ghi_duyet_the_tuan.py", \
        "đọc bài của thẻ tuần KHÔNG phải ghi quyết định thẻ"


def test_giac_quan_agent_lech(tmp_path):
    g, m = tmp_path / "goc", tmp_path / "mea"
    g.mkdir()
    m.mkdir()
    for d in (g, m):
        (d / "ke-don-an-toan.md").write_text("A\n", encoding="utf-8", newline="\n")
        (d / "_TRANG-THAI.json").write_text("{}", encoding="utf-8")   # không phải agent .md ⇒ không so
    assert TD.giac_quan_agent_lech(g, m) == []
    (m / "ke-don-an-toan.md").write_text("B\n", encoding="utf-8", newline="\n")
    (g / "moi.md").write_text("x", encoding="utf-8")
    ra = TD.giac_quan_agent_lech(g, m)
    assert len(ra) == 1 and "1 lệch nội dung (ke-don-an-toan.md)" in ra[0][1] and "1 chỉ có ở một bên (moi.md)" in ra[0][1]
    truoc = len(TD._GIAC_QUAN_CHET)
    assert TD.giac_quan_agent_lech(g, tmp_path / "vang") == [] and len(TD._GIAC_QUAN_CHET) == truoc + 1
