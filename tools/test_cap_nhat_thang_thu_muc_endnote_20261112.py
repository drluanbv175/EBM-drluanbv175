#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt `tools/cap_nhat_thang_thu_muc_endnote.py` — cập nhật chứng cứ THÁNG theo thư mục EndNote (bác sĩ giao 12/11/2026, nguyên
văn: «Xây dựng tự động cập nhật chứng cứ hàng tháng với các thư mục trong Endnote»; bổ sung: «Với việc cập nhật những chứng cứ áp
dụng cho thực hành lâm sàng đảm bảo toàn văn và tóm tắt như đã xây dựng cho hệ thống cập nhật chứng cứ»).

Khoá (toàn bộ trên FIXTURE giả — không đọc EndNote/tệp thật của bác sĩ, không gọi mạng, không ghi EndNote):
  • phân nhóm (a) cần bản nối tiếp · (b) cần watchlist · (c) chưa gắn dashboard (4 phụ loại) · (d) ổn;
  • ứng viên chỉ tính khi MỚI (lần đầu bộ quét trình sau ngày dashboard), chưa có trong dashboard, đúng loại xuất bản thật;
  • ⚪ khi không đo được (thư viện, báo cáo quét, kho toàn văn, DATA) — không bao giờ thành 🟢 hay thành «thiếu»;
  • mục apply/consider: toàn văn kho · PDF EndNote · khối tiếng Việt · ⑨; bài bác sĩ đã loại không bị mời nạp lại;
  • chạy khô không ghi tệp và không gọi lệnh nào (kể cả có --quet/--hoan-thien);
  • --quet gọi đúng lệnh orchestrator, có trần, mỗi mục watchlist một lần, dừng khi hạ tầng hỏng;
  • --hoan-thien gọi đúng chuỗi gom → in PDF → gắn kho → tóm tắt, rào ghi EndNote kiểm TRƯỚC TỪNG bước (khoá/cờ/giao dịch treo);
  • giác quan hòm việc ⚪ khi chưa có phiếu tháng; kiem_lich_nen hiểu dấu vết «file-thang».
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, TOOLS / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


cn = _nap("_cntm_test", "cap_nhat_thang_thu_muc_endnote.py")

HOM_NAY = dt.date(2026, 11, 12)
WL_A, WL_B, WL_D, WL_D2 = "Chủ đề A", "Chủ đề cũ", "Chủ đề D", "Chủ đề D2"


def _c(pmid, pt, **kw):
    return dict({"pmid": pmid, "title": f"bài {pmid}", "publication_date": "2026 Nov", "pubtype": pt, "rut_bai": "ok",
                 "da_co_trong_kho": False, "chua_binh_duyet": False}, **kw)


def _fixture(tmp_path: Path) -> dict:
    """Thư viện giả 11 thư mục + 7 dashboard + báo cáo quét giả."""
    def d(khoa, ngay):
        return {"tep": tmp_path / f"WebDashboard_{khoa}_{ngay}.html", "ngay": ngay, "cac_ban": []}
    dashboards = {
        "EBM_VanDeCuThe_Cu": d("EBM_VanDeCuThe_Cu", "20260701"),            # > 90 ngày ⇒ (a) ưu tiên
        "EBM_VanDeCuThe_GuiMoi": d("EBM_VanDeCuThe_GuiMoi", "20261101"),    # guideline MỚI ⇒ (a)
        "EBM_VanDeCuThe_NhieuSR": d("EBM_VanDeCuThe_NhieuSR", "20261101"),  # 5 SR/RCT mới ⇒ (a) theo dõi
        "EBM_VanDeCuThe_DaXet": d("EBM_VanDeCuThe_DaXet", "20261101"),      # guideline đã trình TRƯỚC dashboard ⇒ (d)
        "EBM_VanDeCuThe_ChuaWL": d("EBM_VanDeCuThe_ChuaWL", "20261105"),    # không watchlist ⇒ (b)
        "EBM_VanDeCuThe_ChuaQuet": d("EBM_VanDeCuThe_ChuaQuet", "20261110"),  # chưa có lượt quét sau dashboard ⇒ (d) ⚪
        "EBM_Uptodate_W26_BanTin": d("EBM_Uptodate_W26_BanTin", "20260628"),  # bản tin ⇒ (d), không nối tiếp dù cũ
    }
    phan_giai = {
        "Cu": {"loai": "watchlist", "a2_arg": WL_A}, "GuiMoi": {"loai": "watchlist", "a2_arg": WL_A},
        "NhieuSR": {"loai": "watchlist", "a2_arg": WL_D}, "DaXet": {"loai": "watchlist", "a2_arg": WL_D2},
        "ChuaWL": {"loai": "khong_ro", "goc": ["ChuaWL"]}, "ChuaQuet": {"loai": "watchlist", "a2_arg": WL_D},
        "W26_BanTin": {"loai": "khong_can", "ly_do": "bản tin gộp"},
    }
    bang = {k: f"Thư mục {k.split('_')[-1]}" for k in dashboards}
    bang["DE-TAI_x"] = "NC · đề tài x"
    nhom_ten = list(dict.fromkeys(bang.values())) + ["EBM · Câu hỏi cũ của bản trước", "EBM · Bản tin mồ côi",
                                                    "Core Evidence", "Thư mục bác sĩ tự đặt", "_Cho thung rac", "PubMed (NLM)"]
    ban_ghi = {r: {"pmid": str(1000 + r), "doi": None, "pdf": True, "khoi_vi": True} for r in range(1, 60)}
    nhom = []
    r = 1
    for i, ten in enumerate(nhom_ten):
        n = 1 if ten == "Core Evidence" else 5
        loai = "online" if ten.startswith("PubMed") else "custom"
        nhom.append({"group_id": i + 1, "ten": ten, "loai": loai, "rec": list(range(r, r + n))})
        r += n
    # mục apply/consider của dashboard «GuiMoi» (rec 6..10 thuộc thư mục GuiMoi)
    muc_gui = [
        {"id": "ITEM-01", "pmid": "1006", "doi": None, "decision": "apply", "sao": True},   # đủ hết, ⑨ đã có
        {"id": "ITEM-02", "pmid": "1007", "doi": None, "decision": "apply", "sao": True},   # thiếu toàn văn kho ⇒ 🔴
        {"id": "ITEM-03", "pmid": "1008", "doi": None, "decision": "consider", "sao": False},  # thiếu PDF EndNote
        {"id": "ITEM-04", "pmid": "1009", "doi": None, "decision": "apply", "sao": True},   # thiếu khối tiếng Việt, ⑨ chờ
        {"id": "ITEM-05", "pmid": "7777", "doi": None, "decision": "consider", "sao": False},  # chưa có bản ghi
        {"id": "ITEM-06", "pmid": "8888", "doi": None, "decision": "consider", "sao": False},  # bác sĩ đã loại
        {"id": "ITEM-07", "pmid": None, "doi": None, "decision": "apply", "sao": True},     # không định danh ⇒ ⚪
    ]
    ban_ghi[8]["pdf"] = False
    ban_ghi[9]["khoi_vi"] = False
    ban_ghi[53]["khoi_vi"] = False  # bài trong «Thư mục bác sĩ tự đặt» (rec 52–56, ngoài dashboard) chưa có khối tiếng Việt

    def do_dash(tep):
        if "ChuaQuet" in tep.name:
            return {"doc_duoc": False}
        muc = muc_gui if "GuiMoi" in tep.name else []
        return {"doc_duoc": True, "pmids": {"5555"} if "NhieuSR" in tep.name else set(), "dois": set(), "m1": 0, "m2": 0,
                "m2_khong_do": 0, "m1_ds": [], "muc": muc}
    luc_moi = dt.datetime(2026, 11, 9, 19, 0)
    luc_cu = dt.datetime(2026, 10, 26, 19, 0)
    bao_cao = [
        {"tep": "tuan-2026-W46-quet.json", "luc": luc_moi, "topics": {
            WL_A: [_c("2001", ["Practice Guideline"]), _c("2002", ["Journal Article"])],
            WL_D: [_c(str(3000 + i), ["Systematic Review"]) for i in range(4)] + [_c("3100", ["Randomized Controlled Trial"]),
                                                                               _c("5555", ["Meta-Analysis"]),  # đã có trong dash
                                                                               _c("3200", ["Meta-Analysis"], chua_binh_duyet=True)],
            WL_D2: [_c("4001", ["Practice Guideline"])]}},
        {"tep": "tuan-2026-W44-quet.json", "luc": luc_cu, "topics": {WL_D2: [_c("4001", ["Practice Guideline"])]}},
    ]
    lan_dau = {"2001": luc_moi, "2002": luc_moi, "4001": luc_cu, "3100": luc_moi, "5555": luc_moi, "3200": luc_moi,
               **{str(3000 + i): luc_moi for i in range(4)}}
    word9 = {"hang_cho": [{"rec": 9}], "da_co": {"PMID-1006"}}
    return {"nhom": nhom, "ban_ghi": ban_ghi, "bang_nhom": bang, "dashboards": dashboards,
            "phan_giai": lambda q: phan_giai.get(q, {"loai": "khong_ro"}), "do_dash": do_dash, "bao_cao": bao_cao,
            "toan_van": {"1006": True, "1007": False, "1008": True, "1009": True, "7777": True, "8888": True},
            "so_no": set(), "word9": word9, "cau_hoi_cu": {cn._khoa_ten("EBM · Câu hỏi cũ của bản trước"): "EBM_VanDeCuThe_X"},
            "watchlist": [WL_A, WL_D, WL_D2], "hom_nay": HOM_NAY, "lan_dau": lan_dau, "bo_qua": {"8888"}}


def _theo_ten(pt: dict) -> dict:
    return {tm["ten"]: tm for tm in pt["thu_muc"]}


# ───────────────────────── phân nhóm ─────────────────────────

def test_phan_nhom_a_b_c_d(tmp_path):
    pt = cn.phan_tich(**_fixture(tmp_path))
    t = _theo_ten(pt)
    assert "PubMed (NLM)" not in t and "_Cho thung rac" not in t  # nhóm trực tuyến và nhóm làm việc không phải thư mục chủ đề
    assert t["Thư mục Cu"]["nhom"] == "a" and t["Thư mục Cu"]["uu_tien"] and "tuoi" in t["Thư mục Cu"]["ly_do_loai"]
    assert t["Thư mục GuiMoi"]["nhom"] == "a" and t["Thư mục GuiMoi"]["ly_do_loai"] == ["guideline"]
    sr = t["Thư mục NhieuSR"]
    assert sr["nhom"] == "a" and sr["ly_do_loai"] == ["sr_rct"] and not sr["uu_tien"]  # theo dõi, không ưu tiên
    uv = sr["lat_cat"][0]["ung_vien"]
    assert {x["pmid"] for x in uv["sr_ma"] + uv["rct"]} == {"3000", "3001", "3002", "3003", "3100"}  # bỏ bài đã có + preprint
    assert t["Thư mục DaXet"]["nhom"] == "d"  # guideline đã trình TRƯỚC ngày dashboard — người soạn đã có dịp xét
    assert t["Thư mục ChuaWL"]["nhom"] == "b" and t["Thư mục ChuaWL"]["can_watchlist"]
    assert t["Thư mục BanTin"]["nhom"] == "d"  # bản tin gộp (khong_can) cũ 137 ngày vẫn không cần nối tiếp
    c = {k: t[k]["phu_loai"] for k in ("NC · đề tài x", "EBM · Câu hỏi cũ của bản trước", "EBM · Bản tin mồ côi",
                                        "Core Evidence", "Thư mục bác sĩ tự đặt")}
    assert c == {"NC · đề tài x": "nc_tt", "EBM · Câu hỏi cũ của bản trước": "ebm_cu", "EBM · Bản tin mồ côi": "ebm_cu",
                 "Core Evidence": "khung", "Thư mục bác sĩ tự đặt": "noi_dung_that"}
    assert t["EBM · Câu hỏi cũ của bản trước"]["dashboard_cu"] == "EBM_VanDeCuThe_X"
    assert all(t[k]["nhom"] == "c" for k in c)


def test_ung_vien_chi_tinh_loai_xuat_ban_that():
    assert cn.phan_loai_ung_vien(_c("1", ["Practice Guideline"])) == "guideline"
    assert cn.phan_loai_ung_vien(_c("1", ["Consensus Statement"])) == "guideline"
    # «authority_source» là hội gắn với TẠP CHÍ — một tổng quan trên Diabetologia mang «ADA/EASD» KHÔNG thành guideline
    assert cn.phan_loai_ung_vien(_c("1", ["Systematic Review"], authority_source="ADA/EASD")) == "sr_ma"
    assert cn.phan_loai_ung_vien(_c("1", ["Journal Article"], tang="guideline")) is None
    assert cn.phan_loai_ung_vien(_c("1", ["Practice Guideline"], rut_bai="retracted")) is None
    assert cn.phan_loai_ung_vien(_c("1", ["Practice Guideline"], da_co_trong_kho=True)) is None


# ───────────────────────── ⚪ khi không đo được ─────────────────────────

def test_khong_do_duoc_la_trang_khong_bao_gio_xanh(tmp_path):
    fx = _fixture(tmp_path)
    fx.update(nhom=None, ban_ghi=None, bao_cao=None, toan_van=None, watchlist=None)
    pt = cn.phan_tich(**fx)
    kd = " | ".join(pt["khong_do"])
    assert "thư viện EndNote không đọc được" in kd and "báo cáo quét" in kd and "kho toàn văn" in kd and "watchlist" in kd
    t = _theo_ten(pt)
    assert t["Thư mục GuiMoi"]["so_bai"] is None and t["Thư mục GuiMoi"]["thieu_pdf"] is None
    # không có thư mục nào nhóm (d) mà danh sách «không đo được» rỗng (không có 🟢 giả)
    assert not [tm for tm in pt["thu_muc"] if tm["nhom"] == "d" and not tm["khong_do"]]
    vm = cn.viec_muc(pt)
    assert vm["apply_thieu_tv"] == [] and vm["thieu_pdf"] == [] and vm["chua_ban_ghi"] == []  # ⚪ ≠ «thiếu»


def test_chua_quet_sau_dashboard_la_trang(tmp_path):
    t = _theo_ten(cn.phan_tich(**_fixture(tmp_path)))
    cq = t["Thư mục ChuaQuet"]
    assert cq["nhom"] == "d" and any("chưa có lượt quét" in x for x in cq["khong_do"])
    assert any("DATA" in x for x in cq["khong_do"])  # DATA không đọc được ⇒ ⚪


# ───────────────────────── mục apply/consider: toàn văn · PDF · khối tiếng Việt · ⑨ ─────────────────────────

def test_do_thieu_toan_van_pdf_tom_tat_word9(tmp_path):
    pt = cn.phan_tich(**_fixture(tmp_path))
    muc = {m["id"]: m for m in _theo_ten(pt)["Thư mục GuiMoi"]["lat_cat"][0]["muc"]}
    assert muc["ITEM-01"]["word9"] == "co" and muc["ITEM-01"]["pdf_endnote"] and muc["ITEM-01"]["khoi_vi"]
    assert muc["ITEM-04"]["word9"] == "cho" and muc["ITEM-04"]["khoi_vi"] is False
    assert muc["ITEM-05"]["ban_ghi"] is False
    assert muc["ITEM-06"]["ban_ghi"] == "bo_qua"  # bác sĩ đã loại ⇒ không mời nạp lại (sự cố 18/10/2026)
    assert muc["ITEM-07"]["ban_ghi"] is None and muc["ITEM-07"]["toan_van"] is None and muc["ITEM-07"]["word9"] is None
    vm = cn.viec_muc(pt)
    assert [x["pmid"] for x in vm["apply_thieu_tv"]] == ["1007"]
    assert [x["pmid"] for x in vm["thieu_pdf"]] == ["1008"]
    assert [x["pmid"] for x in vm["chua_ban_ghi"]] == ["7777"]
    assert [x["pmid"] for x in vm["thieu_khoi"]] == ["1009"]
    assert [x["pmid"] for x in vm["word9_cho"]] == ["1009"]
    md = cn.dung_phieu(pt, vm, thang="2026-11", sinh_luc="t", che_do="thử", quet=None, hoan_thien=None, de_xuat_kq=None)
    i11 = md.index("### 1.1")
    assert "🔴" in md[i11:md.index("### 1.2")] and "PMID 1007" in md[i11:md.index("### 1.2")]
    assert md.index("## 1. Việc bác sĩ cần quyết") < md.index("## 3.")  # việc bác sĩ đứng đầu phiếu


# ───────────────────────── chạy khô: không ghi, không gọi ─────────────────────────

def _vao_main(monkeypatch, tmp_path, pt):
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir(exist_ok=True)
    monkeypatch.setattr(cn, "thu_thap_va_phan_tich", lambda h, b: (pt, None, {"dash_dir": dash}))
    goi: list = []

    def khong_duoc_goi(*a, **k):
        goi.append(a)
        raise AssertionError("chạy khô không được gọi lệnh nào")
    monkeypatch.setattr(cn.subprocess, "run", khong_duoc_goi)
    monkeypatch.setattr(cn.time, "sleep", lambda s: None)
    return dash, goi


def test_chay_kho_khong_ghi_khong_goi(monkeypatch, tmp_path, capsys):
    pt = cn.phan_tich(**_fixture(tmp_path))
    dash, goi = _vao_main(monkeypatch, tmp_path, pt)
    truoc = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    rc = cn.main(["--quet", "--toi-da", "3", "--hoan-thien", "--ghi-endnote", "--hom-nay", "2026-11-12"])
    assert rc == 1 and goi == []
    assert sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*")) == truoc  # không tạo tệp/thư mục nào
    out = capsys.readouterr().out
    assert "(khô) --quet sẽ chạy" in out and "(khô) --hoan-thien sẽ chạy" in out and "chạy khô" in out


def test_ap_dung_ghi_phieu_va_de_xuat_giu_khoa_khac(monkeypatch, tmp_path):
    pt = cn.phan_tich(**_fixture(tmp_path))
    dash, _goi = _vao_main(monkeypatch, tmp_path, pt)
    (dash / "watchlist.de-xuat.json").write_text(json.dumps({"_about": "đợt 6", "topics": [{"topic": "x"}]}), encoding="utf-8")
    assert cn.main(["--ghi", "--hom-nay", "2026-11-12"]) == 1
    md, js = cn.tep_phieu(dash, "2026-11")
    assert md.is_file() and js.is_file()
    d = json.loads(js.read_text(encoding="utf-8"))
    assert {tm["nhom"] for tm in d["thu_muc"]} == {"a", "b", "c", "d"}
    dx = json.loads((dash / "watchlist.de-xuat.json").read_text(encoding="utf-8"))
    assert dx["_about"] == "đợt 6" and dx["topics"] == [{"topic": "x"}]  # đề xuất đợt khác giữ nguyên
    assert [m["chu_de_goc"] for m in dx[cn.KHOA_DE_XUAT]["chu_de"]] == ["ChuaWL"]
    assert list(dash.glob("watchlist.de-xuat.json.bak-*"))  # sao lưu trước khi ghi
    assert not (dash / "watchlist.json").exists()  # KHÔNG đụng watchlist thật


def test_de_xuat_tep_hong_khong_ghi(tmp_path):
    tep = tmp_path / "watchlist.de-xuat.json"
    tep.write_text("{hỏng", encoding="utf-8")
    assert cn.ghi_de_xuat(tep, {"chu_de": []}).startswith("⚪")
    assert tep.read_text(encoding="utf-8") == "{hỏng"


def test_hat_giong_chi_tu_ten_tieng_anh():
    assert cn._hat_giong_tieng_anh("ILD / Pulmonary Fibrosis") == "ild pulmonary fibrosis"
    assert cn._hat_giong_tieng_anh("Peripheral Artery Disease (Động mạch ngoại biên)") == "peripheral artery disease"
    assert cn._hat_giong_tieng_anh("Tăng áp lực động mạch phổi") is None  # máy KHÔNG dịch (BH10)


# ───────────────────────── --quet ─────────────────────────

class _Kq:
    def __init__(self, rc, out=""):
        self.returncode, self.stdout, self.stderr = rc, out, ""


def test_quet_dung_lenh_co_tran_moi_watchlist_mot_lan(tmp_path):
    pt = cn.phan_tich(**_fixture(tmp_path))
    ke = cn.ke_hoach_quet(pt, 8)
    assert [x["watchlist"] for x in ke] == [WL_A, WL_D]  # Cu + GuiMoi cùng WL_A ⇒ một lần; (d)/(b) không quét
    assert ke[0]["lenh"][1:] == [str(cn.GOC / "ops" / "orchestrator.py"), "--topic", ke[0]["lat"], "--online"]
    assert ke[0]["lenh"][0] == sys.executable
    assert len(cn.ke_hoach_quet(pt, 1)) == 1
    assert len(cn.ke_hoach_quet(pt, 99)) <= cn.TRAN_QUET


def test_quet_tuan_tu_nghi_va_dung_khi_ha_tang(tmp_path):
    ke = [{"lat": f"L{i}", "watchlist": f"W{i}", "lenh": ["py", "ops/orchestrator.py", "--topic", f"L{i}", "--online"]}
          for i in range(3)]
    goi, ngu = [], []

    def chay(lenh, **kw):
        goi.append(lenh)
        assert kw["timeout"] == cn.TIMEOUT_QUET_GIAY
        return _Kq(2 if lenh[3] == "L1" else 0, f"KẾ HOẠCH run 20261205T1800-{lenh[3]} — 5 bước")
    kq = cn.chay_quet(ke, chay=chay, ngu=ngu.append)
    assert [x[3] for x in goi] == ["L0", "L1"]  # mã 2 (hạ tầng) ⇒ không dội tiếp vào nguồn
    assert kq[0]["run_id"] == "20261205T1800-L0" and kq[2]["rc"] is None and "dừng" in kq[2]["bo_qua"]
    assert ngu == [cn.NGHI_GIUA_QUET_GIAY]


def test_quet_qua_main_ap_dung_goi_mock(monkeypatch, tmp_path):
    pt = cn.phan_tich(**_fixture(tmp_path))
    dash, _ = _vao_main(monkeypatch, tmp_path, pt)
    goi = []
    monkeypatch.setattr(cn.subprocess, "run", lambda lenh, **kw: (goi.append(lenh), _Kq(0, "KẾ HOẠCH run R1 — x"))[1])
    monkeypatch.setattr(cn, "thu_thap_va_phan_tich", lambda h, b: (pt, None, {"dash_dir": dash}))
    cn.main(["--quet", "--toi-da", "1", "--ghi", "--hom-nay", "2026-11-12"])
    assert len(goi) == 1 and goi[0][2:] == ["--topic", goi[0][3], "--online"] and goi[0][1].endswith("orchestrator.py")


# ───────────────────────── --hoan-thien ─────────────────────────

def test_hoan_thien_dung_thu_tu_va_lenh(tmp_path):
    pt = cn.phan_tich(**_fixture(tmp_path))
    ke = cn.ke_hoach_hoan_thien(pt, cn.viec_muc(pt))
    assert [b["buoc"] for b in ke] == ["gom", "in_pdf", "gan_kho", "tom_tat_vi", "tom_tat_thu_vien"]
    lenh = {b["buoc"]: b["lenh"][1:] for b in ke}
    assert lenh["gom"][0].endswith("gom_toan_van_dashboard.py") and lenh["gom"][1:] == ["--pmid", "1007", "--unpaywall"]
    assert lenh["in_pdf"][0].endswith("in_pdf_toan_van_kho.py") and lenh["in_pdf"][-1] == "--ap-dung"
    assert lenh["gan_kho"][:2] == [lenh["gan_kho"][0], "--gan-kho"] and "--chi-khi-dang-mo" in lenh["gan_kho"]
    assert set(lenh["gan_kho"][lenh["gan_kho"].index("--pmid") + 1:lenh["gan_kho"].index("--ap-dung")]) == {"1007", "1008"}
    assert "--tom-tat-vi" in lenh["tom_tat_vi"] and lenh["tom_tat_vi"][lenh["tom_tat_vi"].index("--file") + 1].endswith(
        "WebDashboard_EBM_VanDeCuThe_GuiMoi_20261101.html")
    assert [b["ghi_endnote"] for b in ke] == [False, False, True, True, True]


def test_hoan_thien_rao_kiem_truoc_tung_buoc_ghi():
    buoc = [{"buoc": b, "ghi_endnote": g, "lenh": ["py", b]} for b, g in
            (("gom", False), ("in_pdf", False), ("gan_kho", True), ("tom_tat_vi", True))]
    goi, lan_kiem = [], []

    def chay(lenh, **kw):
        goi.append(lenh[1])
        return _Kq(0)

    def kiem():  # lần 1 cho ghi, lần 2 phiên khác vừa lấy khoá
        lan_kiem.append(1)
        return (len(lan_kiem) == 1, "khoá ghi EndNote đang do tiến trình khác giữ")
    kq = cn.chay_hoan_thien(buoc, ghi_endnote=True, chay=chay, kiem_ghi=kiem)
    assert goi == ["gom", "in_pdf", "gan_kho"] and len(lan_kiem) == 2
    assert kq[3]["rc"] is None and "khoá" in kq[3]["bo_qua"]
    goi.clear()
    kq = cn.chay_hoan_thien(buoc, ghi_endnote=True, chay=chay, kiem_ghi=lambda: (False, "cờ tạm dừng"))
    assert goi == ["gom", "in_pdf"] and all(x.get("bo_qua") == "cờ tạm dừng" for x in kq[2:])


def test_luot_lich_khong_ghi_endnote_du_rao_xanh(monkeypatch, tmp_path):
    """Không có --ghi-endnote (lượt lịch) ⇒ ③④ KHÔNG chạy kể cả khi rào xanh; rào không bị hỏi; phiếu ghi việc 🛎."""
    buoc = [{"buoc": b, "ghi_endnote": g, "lenh": ["py", b]} for b, g in
            (("gom", False), ("in_pdf", False), ("gan_kho", True), ("tom_tat_vi", True))]
    goi, hoi = [], []
    kq = cn.chay_hoan_thien(buoc, chay=lambda lenh, **kw: (goi.append(lenh[1]), _Kq(0))[1],
                            kiem_ghi=lambda: (hoi.append(1), (True, "🟢"))[1])
    assert goi == ["gom", "in_pdf"] and hoi == [] and all("chờ phiên Claude" in x["bo_qua"] for x in kq[2:])
    pt = cn.phan_tich(**_fixture(tmp_path))
    dash, _ = _vao_main(monkeypatch, tmp_path, pt)
    lenh_goi = []
    monkeypatch.setattr(cn.subprocess, "run", lambda lenh, **kw: (lenh_goi.append(lenh), _Kq(0))[1])
    cn.main(["--hoan-thien", "--ghi", "--hom-nay", "2026-11-12"])
    assert lenh_goi and not any("nap_endnote_chu_de.py" in str(x) for lenh in lenh_goi for x in lenh)
    md = cn.tep_phieu(dash, "2026-11")[0].read_text(encoding="utf-8")
    assert "--hoan-thien --ghi-endnote --ghi" in md


def test_ghi_endnote_chi_di_cung_hoan_thien(monkeypatch, tmp_path):
    pt = cn.phan_tich(**_fixture(tmp_path))
    _vao_main(monkeypatch, tmp_path, pt)
    assert cn.main(["--ghi-endnote", "--ghi"]) == 3


def test_rao_ghi_endnote_co_khoa_giao_dich_nen_tang(tmp_path, monkeypatch):
    monkeypatch.delenv("EBM_CO_TAM_DUNG_ENDNOTE", raising=False)
    co = tmp_path / "TAM-DUNG-ENDNOTE"
    xanh = lambda: {"do_duoc": True, "canh_bao": [], "giao_dich_mo": {"treo": False}}  # noqa: E731
    kw = dict(nen_tang="darwin", co_tam_dung=co, khoa=lambda: None, tinh_trang=xanh)
    assert cn.kiem_ghi_endnote(**kw) == (True, "🟢")
    co.write_text("", encoding="utf-8")
    assert cn.kiem_ghi_endnote(**kw)[0] is False and "cờ tạm dừng" in cn.kiem_ghi_endnote(**kw)[1]
    co.unlink()
    assert cn.kiem_ghi_endnote(**dict(kw, khoa=lambda: {"pid": 42, "ly_do": "bộ năm"}))[0] is False
    treo = lambda: {"do_duoc": True, "canh_bao": [], "giao_dich_mo": {"treo": True, "mo_ta": "treo 22 giờ"}}  # noqa: E731
    ok, ly = cn.kiem_ghi_endnote(**dict(kw, tinh_trang=treo))
    assert not ok and "TREO" in ly
    assert cn.kiem_ghi_endnote(**dict(kw, tinh_trang=lambda: {"do_duoc": True, "canh_bao": ["bản sao xung đột"]}))[0] is False
    assert cn.kiem_ghi_endnote(**dict(kw, tinh_trang=lambda: {"do_duoc": False, "ly_do": "x"}))[0] is False
    assert cn.kiem_ghi_endnote(**dict(kw, nen_tang="win32"))[0] is False


# ───────────────────────── giác quan hòm việc + lịch nền ─────────────────────────

def test_giac_quan_trang_khi_chua_co_phieu_va_dem_con_lai(tmp_path):
    dash = tmp_path / "EBM-Dashboards"
    (dash / "derivatives").mkdir(parents=True)
    viec, chet = cn.giac_quan(dash, HOM_NAY)
    assert viec == [] and chet and "chưa có phiếu tháng 2026-11" in chet
    (dash / "WebDashboard_EBM_VanDeCuThe_A_20261120.html").write_text("x", encoding="utf-8")  # bản nối tiếp đã làm
    phieu = {"thu_muc": [
        {"nhom": "a", "lat_cat": [{"khoa": "EBM_VanDeCuThe_A", "ngay": "2026-11-01"}]},
        {"nhom": "a", "lat_cat": [{"khoa": "EBM_VanDeCuThe_B", "ngay": "2026-11-01"}]},
        {"nhom": "b", "lat_cat": []}]}
    cn.tep_phieu(dash, "2026-11")[1].write_text(json.dumps(phieu), encoding="utf-8")
    viec, chet = cn.giac_quan(dash, HOM_NAY)
    assert chet is None and "2 thư mục cần bản nối tiếp (còn 1 chưa làm)" in viec[0][2] and viec[0][:2] == (2, "👤")
    assert "1 thư mục" in viec[1][2] and len(viec) == 2
    phieu["viec_muc"] = {"thieu_pdf": [{"pmid": "1"}], "thieu_khoi": []}
    cn.tep_phieu(dash, "2026-11")[1].write_text(json.dumps(phieu), encoding="utf-8")
    viec, _ = cn.giac_quan(dash, HOM_NAY)
    assert viec[-1][1] == "🛎" and "--ghi-endnote" in viec[-1][3]


def test_kiem_lich_nen_hieu_file_thang(tmp_path):
    kln = _nap("_kln_cntm_test", "kiem_lich_nen.py")
    so = {"cua_so_ngay": 40, "tac_vu": [{"id": "t", "cron": "0 18 5 * *", "tu_ngay": "2026-12-01", "grace_gio": 30,
                                          "dau_vet": {"loai": "file-thang",
                                                      "path": "EBM-Dashboards/derivatives/CAP-NHAT-THANG-THU-MUC_{thang}.md"}}]}
    (tmp_path / "EBM-Dashboards" / "derivatives").mkdir(parents=True)
    kq = kln.kiem(dt.datetime(2026, 12, 8, 9, 0), so, tmp_path)
    assert kq["ok"] == 0 and kq["phat_hien"][0]["muc"] == "lo"
    (tmp_path / "EBM-Dashboards" / "derivatives" / "CAP-NHAT-THANG-THU-MUC_2026-12.md").write_text("x", encoding="utf-8")
    kq = kln.kiem(dt.datetime(2026, 12, 8, 9, 0), so, tmp_path)
    assert kq["ok"] == 1 and kq["phat_hien"] == []


def test_khai_lich_va_quyen_nhat_quan():
    """13/11/2026 bác sĩ: «có 2 tác vụ cập nhật tháng … gộp lại chỉ 1 tác vụ» ⇒ phiếu thư mục EndNote là bước SAU bộ
    thu thập trong tác vụ tháng DUY NHẤT `cap-nhat-thang-ebm`; tác vụ ngày 5 riêng đã bỏ."""
    goc = TOOLS.parent
    ky = json.loads((goc / "sync" / "lich-nen-ky-vong.json").read_text(encoding="utf-8"))
    assert not [t for t in ky["tac_vu"] if t["id"] == "cap-nhat-thang-thu-muc-endnote"]
    assert not (goc / "sync" / "scheduled-tasks" / "cap-nhat-thang-thu-muc-endnote").exists()
    thang = [t for t in ky["tac_vu"] if t["cron"].split()[2] != "*" and t["cron"].split()[3] == "*"
             and "cap-nhat" in t["id"]]
    assert [t["id"] for t in thang] == ["cap-nhat-thang-ebm"]  # đúng MỘT tác vụ cập nhật tháng
    skill = (goc / "sync" / "scheduled-tasks" / "cap-nhat-thang-ebm" / "SKILL.md").read_text(encoding="utf-8")
    # 13/11/2026 (lần 2) bác sĩ: «Gói thu thập an toàn thuốc và duyệt chứng cứ hãy gộp vào một tác vụ tháng» ⇒ thứ tự bắt buộc:
    # an toàn thuốc → cập nhật tháng → gói duyệt (quy trình goi-duyet-tuan-ebm) → phiếu thư mục EndNote.
    vi_tri = [skill.index(s) for s in ("`bash medical-ebm-automation/scripts/weekly_safety.sh`",
                                        "`bash medical-ebm-automation/scripts/monthly_update.sh`",
                                        "`sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md`",
                                        "`python3 tools/cap_nhat_thang_thu_muc_endnote.py --quet --toi-da 3 --hoan-thien --ghi`")]
    assert vi_tri == sorted(vi_tri)
    for tid in ("thu-thap-tuan-an-toan-thuoc", "goi-duyet-tuan-ebm"):  # không còn là tác vụ lịch riêng
        assert not [t for t in ky["tac_vu"] if t["id"] == tid], tid
    assert not (goc / "sync" / "scheduled-tasks" / "thu-thap-tuan-an-toan-thuoc").exists()
    assert (goc / "sync" / "scheduled-tasks" / "goi-duyet-tuan-ebm" / "SKILL.md").exists()  # tệp QUY TRÌNH vẫn giữ
    assert "run_in_background" in skill
    assert "KHÔNG tự mở agent" in skill
    q = json.loads((goc / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))
    assert "cap-nhat-thang-thu-muc-endnote" not in q["tac_vu"]
    tv = q["tac_vu"]["cap-nhat-thang-ebm"]
    assert "bash medical-ebm-automation/scripts/monthly_update.sh" in tv["lenh"]
    assert "bash medical-ebm-automation/scripts/weekly_safety.sh" in tv["lenh"]
    assert not any("--ghi-endnote" in c for c in tv["lenh"])  # lượt lịch không bao giờ được khai quyền ghi EndNote
    assert any("--ghi-endnote" in c for c in tv["khong_chay"])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
