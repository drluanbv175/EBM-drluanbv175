"""Kiểm hồi quy `ops/orchestrator.py` + `tools/chu_de_resolver.py` (T1-01…T1-14, 20/09/2026). Thuần offline."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    spec = importlib.util.spec_from_file_location(ten, GOC / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


rs = _nap("tools/chu_de_resolver.py", "rs_t")
op = _nap("ops/orchestrator.py", "op_t")

WL = ["Biến chứng thần kinh do ĐTĐ", "Bệnh thận mạn (CKD)", "Suy tim — tiên lượng & điều trị", "Suy tim nội trú GDMT"]


def _d(p):  # một dashboard giả
    return Path(f"WebDashboard_EBM_VanDeCuThe_{p}.html")


DL = {
    "watchlist": WL,
    "muc": {"BienChungThanKinh": WL[0], "BenhThanMan": WL[1], "Than": WL[1], "SuyTim": WL[2], "TienLuongSuyTim": WL[2]},
    "khong_can": {"Uptodate": "bản tin tuần GỘP"},
    "theo_goc": {
        "BienChungThanKinh": [("20260607", "BienChungThanKinh_DTD", _d("BienChungThanKinh_DTD_20260607"))],
        "BenhThanMan": [("20260607", "BenhThanMan_CKD", _d("BenhThanMan_CKD_20260607")),
                        ("20260701", "BenhThanMan_CKD", _d("BenhThanMan_CKD_20260701"))],
        "Than": [("20260610", "Than", _d("Than_20260610"))],
        "SuyTim": [("20260804", "SuyTim_TongHop", _d("SuyTim_TongHop_20260804")),
                   ("20260811", "SuyTim_TongHop", _d("SuyTim_TongHop_20260811"))],
        "TienLuongSuyTim": [("20260914", "TienLuongSuyTim", _d("TienLuongSuyTim_20260914"))],
        "Uptodate": [("20260607", "Uptodate", Path("WebDashboard_EBM_Uptodate_20260607.html"))],
        "ChuaKhai": [("20260101", "ChuaKhai_X", _d("ChuaKhai_X_20260101"))],
    },
}


# ── resolver ────────────────────────────────────────────────────────────────────────────────────
def test_ten_lat_cat_phan_giai_ve_ten_watchlist_dung():
    r = rs.resolve("BienChungThanKinh_DTD", DL)
    assert r["loai"] == "watchlist" and r["a2_arg"] == WL[0] and r["cach"] == "lat-cat"
    assert [x["ten"] for x in r["lat_cat"]] == ["BienChungThanKinh_DTD"]


def test_gap_dau_d_khi_go_khong_dau():
    assert rs.resolve("bien chung than kinh do DTD", DL)["a2_arg"] == WL[0]


def test_lat_cat_lay_ban_moi_nhat_va_tat_ca_goc_cung_watchlist():
    r = rs.resolve("Bệnh thận mạn (CKD)", DL)
    assert sorted(r["goc"]) == ["BenhThanMan", "Than"]
    ban = {x["ten"]: x["ngay"] for x in r["lat_cat"]}
    assert ban["BenhThanMan_CKD"] == "20260701", "phải lấy bản MỚI NHẤT của lát cắt"
    assert "Than" in ban


def test_chu_de_goc_gom_ca_goc_cung_mot_muc_watchlist():
    r = rs.resolve("Suy tim", DL)  # chuan('Suy tim') == chuan('SuyTim')
    assert r["cach"] == "chu-de-goc" and sorted(r["goc"]) == ["SuyTim", "TienLuongSuyTim"]


def test_ban_tin_gop_khong_can_khong_co_a2():
    r = rs.resolve("Uptodate", DL)
    assert r["loai"] == "khong_can" and r["a2_arg"] is None and r["ly_do"]


def test_goc_chua_khai_anh_xa_khong_bi_doan_ho():
    r = rs.resolve("ChuaKhai_X", DL)
    assert r["loai"] == "khong_ro" and r["a2_arg"] is None and "CHƯA khai" in r["ly_do"]


def test_chuoi_con_duy_nhat_va_chuoi_con_mo_ho():
    assert rs.resolve("thần kinh do", DL)["cach"] == "chuoi-con-duy-nhat"
    r = rs.resolve("suy tim noi tru", DL)
    assert r["a2_arg"] == WL[3]
    mo = rs.resolve("suy tim", {**DL, "theo_goc": {}, "muc": {}})  # không có gốc ⇒ rơi vào chuỗi con
    assert mo["cach"] == "chuoi-con-nhieu" and mo["loai"] == "khong_ro" and mo["a2_arg"] is None, \
        "chuỗi con NHIỀU mục không được truyền chuỗi thô cho A2 (bộ khớp của A2 khác — P1-01)"
    assert len(mo["gan_dung"]) == 2


def test_khong_khop_thi_khong_doan_va_co_goi_y():
    r = rs.resolve("hoan toan la", DL)
    assert r["loai"] == "khong_ro" and r["a2_arg"] is None and not r["lat_cat"]
    assert rs.resolve("", DL)["loai"] == "khong_ro"


# ── phân loại mã thoát ──────────────────────────────────────────────────────────────────────────
def test_a2_rc2_tham_so_khac_ha_tang_va_khong_noi_toi_mang():
    muc, msg = op.phan_loai("A2-quet", 2, a2_json_khong_pass=False)
    assert muc == "tham_so" and "không phải lỗi mạng" in msg
    muc, msg = op.phan_loai("A2-quet", 2, a2_json_khong_pass=True)
    assert muc == "ha_tang" and "HẠ TẦNG" in msg


def test_a2_rc3_khoa_ban_dung_lai():
    assert op.phan_loai("A2-quet", 3)[0] == "khoa_ban" and "khoa_ban" in op.DUNG_HET


def test_a4_rc2_la_nguon_bi_rut_khong_phai_mang():
    muc, msg = op.phan_loai("A4-so-xac-minh[X]", 2)
    assert muc == "rut" and "mạng ổn" not in msg.replace("KHÔNG chạy lại vì mạng", "")


def test_b2_va_b4_va_timeout():
    assert op.phan_loai("B2-cong-liem-chinh[X]", 1)[0] == "chan"
    assert op.phan_loai("B2-cong-liem-chinh[X]", 2)[0] == "ha_tang"
    assert op.phan_loai("B4-bo-nam[X]", 3)[0] == "chan"
    assert op.phan_loai("B5-hang-cho-bac-si", 1)[0] == "noi_dung"
    assert op.phan_loai("B2-x", -9)[0] == "timeout" and "timeout" in op.DUNG_HET
    assert op.phan_loai("B2-x", 0)[0] == "ok"


# ── thực thi ────────────────────────────────────────────────────────────────────────────────────
def _plan(xuat=True):
    return [
        {"buoc": "A4-so-xac-minh[X]", "lat": "X", "lenh": ["py", "a4x"]},
        {"buoc": "B2-cong-liem-chinh[X]", "lat": "X", "lenh": ["py", "b2x"]},
        {"buoc": "B4-bo-nam[X]", "lat": "X", "lenh": ["py", "b4x"]},
        {"buoc": "A4-so-xac-minh[Y]", "lat": "Y", "lenh": ["py", "a4y"]},
        {"buoc": "B2-cong-liem-chinh[Y]", "lat": "Y", "lenh": ["py", "b2y"]},
        {"buoc": "B4-bo-nam[Y]", "lat": "Y", "lenh": ["py", "b4y"]},
        {"buoc": "B5-hang-cho-bac-si", "lenh": ["py", "b5"]},
    ]


def test_b2_fail_mot_lat_cat_khong_dung_ca_luot_va_khong_xuat_lat_do():
    da_chay: list[str] = []

    def chay(lenh, _t):
        da_chay.append(lenh[1])
        return 1 if lenh[1] == "b2x" else 0
    res = op.thuc_thi(_plan(), chay=chay, in_=lambda *_: None)
    assert "b4x" not in da_chay, "gói bị cổng chặn đi tiếp sang B4 xuất bộ năm"
    assert {"b4y", "b5", "a4y", "b2y"} <= set(da_chay), "lát cắt độc lập phải chạy tiếp"
    assert res["tong_rc"] == 1 and res["dung"] is None and res["lat_hong"] == {"X"}


def test_tham_so_va_ha_tang_dung_het():
    plan = [{"buoc": "A2-quet", "lenh": ["py", "a2"]}, {"buoc": "B5-hang-cho-bac-si", "lenh": ["py", "b5"]}]
    da_chay: list[str] = []
    res = op.thuc_thi(plan, chay=lambda l, _t: (da_chay.append(l[1]) or 2), in_=lambda *_: None)
    assert res["tong_rc"] == 64 and res["dung"] == "tham_so" and da_chay == ["a2"]


def test_nguon_rut_ghi_vao_phieu_va_di_tiep():
    res = op.thuc_thi(_plan(), chay=lambda l, _t: 2 if l[1] == "a4x" else 0, in_=lambda *_: None)
    assert res["rut"] == ["X"] and res["tong_rc"] == 1 and res["dung"] is None


def test_timeout_dung_buoc():
    res = op.thuc_thi(_plan(), chay=lambda *_: -9, in_=lambda *_: None)
    assert res["dung"] == "timeout" and res["tong_rc"] == 2


def test_b2_rc2_ha_tang_van_dung_nhu_cu():
    res = op.thuc_thi(_plan(), chay=lambda l, _t: 2 if l[1] == "b2x" else 0, in_=lambda *_: None)
    assert res["dung"] == "ha_tang"


# ── kế hoạch ────────────────────────────────────────────────────────────────────────────────────
def _ke(monkeypatch, tt, dbs, **kw):
    monkeypatch.setattr(op, "_phan_giai", lambda _t: tt)
    monkeypatch.setattr(op, "_dashboards_cua_chu_de", lambda _t: dbs)
    return op.ke_hoach("x", kw.pop("online", False), kw.pop("xuat", False), **kw)


def test_a2_luon_nhan_ten_watchlist_day_du_va_luu_ung_vien(monkeypatch):
    tt = {"loai": "watchlist", "a2_arg": WL[0], "lat_cat": [], "ly_do": ""}
    cac = _ke(monkeypatch, tt, [], run_id="RID")
    a2 = [b for b in cac if b["buoc"].startswith("A2")][0]["lenh"]
    assert a2[a2.index("--topic") + 1] == WL[0]
    assert "--json-report" in a2 and "--report" in a2 and "RID" in a2[a2.index("--json-report") + 1]


def test_khong_can_bo_a2_va_khong_dung_phien_dung_dashboard(monkeypatch):
    tt = {"loai": "khong_can", "a2_arg": None, "lat_cat": [], "ly_do": "bản tin gộp"}
    cac = _ke(monkeypatch, tt, [_d("X_20260101")])
    assert not [b for b in cac if b["buoc"].startswith("A2") and "lenh" in b]
    assert [b for b in cac if b["buoc"].startswith("A2-bo-qua")]


def test_a3_chi_khi_uu_tien_va_b2_luon_strict_ca_offline(monkeypatch):
    tt = {"loai": "watchlist", "a2_arg": WL[0], "lat_cat": [], "ly_do": ""}
    cac = _ke(monkeypatch, tt, [_d("X_20260101")], online=False)
    assert not [b for b in cac if b["buoc"].startswith("A3")], "A3 quét toàn kho ~70 phút không được chạy mặc định"
    b2 = [b for b in cac if b["buoc"].startswith("B2")][0]["lenh"]
    assert "--strict-sources" in b2 and "--online" not in b2, "offline vẫn phải có strict-sources (T1-07)"
    assert [b for b in _ke(monkeypatch, tt, [], uu_tien=True) if b["buoc"].startswith("A3")]


def test_b4_chi_khi_xuat(monkeypatch):
    tt = {"loai": "watchlist", "a2_arg": WL[0], "lat_cat": [], "ly_do": ""}
    assert not [b for b in _ke(monkeypatch, tt, [_d("X_20260101")]) if b["buoc"].startswith("B4")]
    assert [b for b in _ke(monkeypatch, tt, [_d("X_20260101")], xuat=True) if b["buoc"].startswith("B4")]


# ── chế độ lô ───────────────────────────────────────────────────────────────────────────────────
def test_cu_nhat_gom_theo_watchlist_bo_khong_can_va_xep_cu_truoc():
    tuoi = [("Uptodate", 105), ("BienChungThanKinh_DTD", 100), ("BenhThanMan_CKD", 90), ("Than", 95),
            ("SuyTim_TongHop", 40), ("ChuaKhai_X", 200)]
    chon, bo = op.chon_cu_nhat(2, DL, tuoi)
    assert [c["q"] for c in chon] == [WL[0], WL[1]]
    assert chon[1]["tuoi_max"] == 95 and sorted(chon[1]["lat"]) == ["BenhThanMan_CKD", "Than"]
    assert any("Uptodate" in x for x in bo) and any("ChuaKhai_X" in x for x in bo)


def test_cu_nhat_co_tran():
    tuoi = [(f"L{i}", 10 + i) for i in range(20)]
    du = {"watchlist": [f"W{i}" for i in range(20)], "muc": {f"L{i}": f"W{i}" for i in range(20)},
          "khong_can": {}, "theo_goc": {f"L{i}": [("20260101", f"L{i}", Path("x.html"))] for i in range(20)}}
    chon, _ = op.chon_cu_nhat(999, du, tuoi)
    assert len(chon) == op.TRAN_LO


# ── main: mã thoát tham số, resume giữ cờ ──────────────────────────────────────────────────────
def test_main_ten_khong_phan_giai_tra_64_khong_phai_2(monkeypatch, capsys):
    monkeypatch.setattr(op, "_phan_giai", lambda _t: {"q": "zzz", "loai": "khong_ro", "wl_topics": [],
                        "a2_arg": None, "goc": [], "lat_cat": [], "ly_do": "không khớp", "gan_dung": ["A"], "cach": ""})
    monkeypatch.setattr(sys, "argv", ["orchestrator.py", "--topic", "zzz", "--dry-run"])
    assert op.main() == 64
    out = capsys.readouterr().out
    assert "KHÔNG phải lỗi mạng" in out and "Có phải: A" in out


def test_resume_khong_ha_co_online(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(op, "LOGS", tmp_path)
    (tmp_path / "RID.jsonl").write_text(
        json.dumps({"tham_so": {"topic": "x", "cu_nhat": None, "uu_tien": False, "online": True, "xuat": False,
                                "cac_chu_de": None}}) + "\n", encoding="utf-8")
    tt = {"loai": "watchlist", "a2_arg": WL[0], "lat_cat": [], "ly_do": "", "cach": "x"}
    monkeypatch.setattr(op, "_phan_giai", lambda _t: tt)
    monkeypatch.setattr(op, "_dashboards_cua_chu_de", lambda _t: [_d("X_20260101")])
    monkeypatch.setattr(sys, "argv", ["orchestrator.py", "--resume", "RID", "--dry-run"])  # KHÔNG truyền --online
    assert op.main() == 0
    b2 = [ln for ln in capsys.readouterr().out.splitlines() if "B2-cong-liem-chinh" in ln][0]
    assert "--online" in b2, "resume làm rơi --online ⇒ B2 offline nhưng vẫn ghi rc=0 như «đã xong»"


def test_slug_gap_dau_d():
    assert op._slug("Bệnh đái tháo đường") == "benh-dai-thao-duong"


def test_phieu_cho_biet_can_phien_khi_qua_han_hoac_co_ung_vien():
    cac = [Path("WebDashboard_EBM_VanDeCuThe_X_20200101.html")]
    v = op.phieu_can_phien("x", {"loai": "watchlist", "a2_arg": WL[0]}, cac, {"ung_vien": 3, "rut": [], "lat_hong": set()})
    assert v and v[0].startswith("/cap-nhat-chung-cu " + WL[0]) and "3 ứng viên" in v[0]
    assert not op.phieu_can_phien("x", {"loai": "khong_can", "a2_arg": None}, cac, {"ung_vien": 9})
    moi = [Path(f"WebDashboard_EBM_VanDeCuThe_X_{__import__('datetime').date.today():%Y%m%d}.html")]
    assert not op.phieu_can_phien("x", {"loai": "watchlist", "a2_arg": WL[0]}, moi, {"ung_vien": 0, "rut": [], "lat_hong": set()})


def test_ten_trung_ca_goc_va_lat_cat_lay_ca_nhom_goc_khong_chi_mot_lat_cat():
    """P-01 (phản biện 20/09): `COPD` là tên gốc VÀ tên một lát cắt — phải trả cả nhóm, không chỉ lát cắt cùng tên."""
    du = {"watchlist": ["COPD — điều trị"], "muc": {"COPD": "COPD — điều trị"}, "khong_can": {},
          "theo_goc": {"COPD": [("20260601", "COPD", Path("a_20260601.html")),
                                ("20260602", "COPD_DoiTuongDacBiet", Path("b_20260602.html")),
                                ("20260603", "COPD_TimMach", Path("c_20260603.html")),
                                ("20260604", "COPD_ThuocHit", Path("d_20260604.html"))]}}
    r = rs.resolve("COPD", du)
    assert r["cach"] == "chu-de-goc" and len(r["lat_cat"]) == 4, "chỉ lấy một lát cắt — A4/B2 bỏ sót 3 lát cắt"
    # tên chỉ là lát cắt (khác tên gốc) vẫn thu hẹp về đúng lát cắt đó
    assert [x["ten"] for x in rs.resolve("COPD_TimMach", du)["lat_cat"]] == ["COPD_TimMach"]


def test_phieu_goi_bac_si_ky_khi_goi_bi_chan_chi_vi_cho_chu_ky_khong_bao_dung_lai():
    """P-07: gói chặn vì chờ ký miễn trừ ⇒ dòng 👤 ký/hạ, KHÔNG gợi ý /cap-nhat-chung-cu cho nguyên nhân đó."""
    db = Path("WebDashboard_EBM_VanDeCuThe_TienLuongSuyTim_20200101.html")
    res = {"ung_vien": 0, "rut": [], "lat_hong": {"TienLuongSuyTim"}}
    v = op.phieu_can_phien("x", {"loai": "watchlist", "a2_arg": WL[2]}, [db], res, frozenset({db.name}))
    assert any(x.startswith("👤 KÝ hoặc HẠ") and "mau_ky_rut_bai" in x for x in v)
    assert not any("cổng liêm chính chặn: TienLuongSuyTim" in x for x in v), "vẫn đổ lỗi chặn cho việc dựng lại"
    # không chờ ký (chặn vì lý do khác) ⇒ vẫn gợi ý phiên cập nhật như cũ
    v2 = op.phieu_can_phien("x", {"loai": "watchlist", "a2_arg": WL[2]}, [db], res, frozenset())
    assert any("cổng liêm chính chặn" in x for x in v2)


def test_chuoi_ngan_khong_duoc_coi_la_khop_duy_nhat():
    """P1-16/P1-02: «a», «da», «Đ» khớp gần cả kho — không phân giải."""
    for q in ("a", "da", "Đ", "nan", "1"):
        r = rs.resolve(q, {**DL, "theo_goc": {}, "muc": {}})
        assert r["a2_arg"] is None and r["loai"] == "khong_ro", q


def test_loi_nap_kho_duoc_bao_khong_nuot_im_lang(tmp_path):
    d = rs.nap_du_lieu(tmp_path)  # thư mục rỗng: không watchlist/ánh xạ/kho
    assert d["loi"], "lỗi nạp bị nuốt — orchestrator sẽ in «CHƯA có dashboard» sai rồi xanh"
    assert rs.resolve("Suy tim", d)["loi_nap"]


def test_main_loi_nap_dung_ha_tang_khong_in_tham_so_sai(monkeypatch, capsys):
    """P1-05: resolver hỏng/kho hỏng ⇒ rc=2 «HẠ TẦNG», không rc=64 «THAM SỐ SAI» và không «xanh»."""
    import importlib.util, sys
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("orch_p105", Path(__file__).resolve().parents[1] / "ops" / "orchestrator.py")
    m = importlib.util.module_from_spec(spec); sys.modules["orch_p105"] = m; spec.loader.exec_module(m)
    monkeypatch.setattr(m, "_phan_giai", lambda t: {"q": t, "loai": "khong_ro", "wl_topics": [], "a2_arg": None,
                                                   "goc": [], "lat_cat": [], "ly_do": "", "gan_dung": [],
                                                   "cach": "", "loi_nap": "quet_kho: OSError"})
    monkeypatch.setattr(sys, "argv", ["orchestrator.py", "--topic", "Suy tim", "--dry-run"])
    rc = m.main()
    out = capsys.readouterr().out
    assert rc == 2 and "HẠ TẦNG" in out and "THAM SỐ SAI" not in out


# ═══ Test main() thật (P1-09): khoá, log, phiếu, mã thoát, resume — bộ chạy được thay bằng giả ═══════════════════
import json as _json


def _nap_op(ten="orch_main"):
    import importlib.util, sys
    from pathlib import Path
    sp = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parents[1] / "ops" / "orchestrator.py")
    m = importlib.util.module_from_spec(sp); sys.modules[ten] = m; sp.loader.exec_module(m)
    return m


def _khung(tmp_path, monkeypatch, m, *, a2_json=None, rc_theo_buoc=None, lat=None):
    """Dựng môi trường giả: logs/ + DASH tạm, resolver trả chủ đề watchlist có 1 lát cắt, bộ chạy giả ghi lại lệnh."""
    (tmp_path / "logs").mkdir()
    dash = tmp_path / "dash"; dash.mkdir()
    db = dash / "WebDashboard_EBM_VanDeCuThe_SuyTim_TongHop_20260609.html"
    db.write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(m, "LOGS", tmp_path / "logs")
    monkeypatch.setattr(m, "DASH", dash)
    monkeypatch.setattr(m, "_cho_ky_rut_bai", lambda: frozenset())
    tt = {"q": "Suy tim", "loai": "watchlist", "wl_topics": ["Suy tim"], "a2_arg": "Suy tim", "goc": [],
          "lat_cat": [{"duong_dan": str(db)}] if lat is None else lat, "ly_do": "", "gan_dung": [], "cach": "ten-watchlist"}
    monkeypatch.setattr(m, "_phan_giai", lambda t: tt)
    monkeypatch.setattr(m, "_dashboards_cua_chu_de", lambda t: [db])
    da_chay: list = []

    def chay(lenh, timeout):
        da_chay.append(list(lenh))
        ten = " ".join(str(x) for x in lenh)
        if "--json-report" in lenh and a2_json is not None:
            from pathlib import Path
            Path(lenh[lenh.index("--json-report") + 1]).write_text(_json.dumps(a2_json), encoding="utf-8")
        for khoa, rc in (rc_theo_buoc or {}).items():
            if khoa in ten:
                return rc
        return 0
    monkeypatch.setattr(m, "_chay_that", chay)
    return da_chay, db


def _chay_main(m, monkeypatch, *argv):
    import sys
    monkeypatch.setattr(sys, "argv", ["orchestrator.py", *argv])
    return m.main()


def test_main_ghi_log_tham_so_va_phieu_khi_xanh(tmp_path, monkeypatch, capsys):
    m = _nap_op("orch_main1")
    _khung(tmp_path, monkeypatch, m, a2_json={"status": "PASS", "topics": []})
    rc = _chay_main(m, monkeypatch, "--topic", "Suy tim", "--online")
    assert rc == 0
    logs = list((tmp_path / "logs").glob("*.jsonl"))
    assert len(logs) == 1
    dong = [_json.loads(x) for x in logs[0].read_text(encoding="utf-8").splitlines()]
    assert dong[0]["tham_so"]["online"] is True, "dòng tham_so phải ghi cờ để resume không hạ cờ"
    assert list((tmp_path / "logs").glob("*.phieu.md")), "thiếu phiếu"


def test_main_a2_rc2_va_json_khong_pass_thanh_ha_tang_rc2(tmp_path, monkeypatch, capsys):
    m = _nap_op("orch_main2")
    _khung(tmp_path, monkeypatch, m, a2_json={"status": "FAIL", "topics": []}, rc_theo_buoc={"surveillance_scan": 2})
    assert _chay_main(m, monkeypatch, "--topic", "Suy tim") == 2


def test_main_a2_rc2_khong_co_json_la_tham_so_rc64(tmp_path, monkeypatch, capsys):
    m = _nap_op("orch_main3")
    _khung(tmp_path, monkeypatch, m, a2_json=None, rc_theo_buoc={"surveillance_scan": 2})
    assert _chay_main(m, monkeypatch, "--topic", "Suy tim") == 64


def test_main_khoa_ban_tra_2(tmp_path, monkeypatch, capsys):
    m = _nap_op("orch_main4")
    _khung(tmp_path, monkeypatch, m)
    khoa = m._nap_khoa()

    class Ban:
        def __init__(self, *a, **k): pass
        def __enter__(self): raise khoa.KhoaBanRon("đang bận")
        def __exit__(self, *a): return False
    monkeypatch.setattr(khoa, "Khoa", Ban)
    monkeypatch.setattr(m, "_nap_khoa", lambda: khoa)
    assert _chay_main(m, monkeypatch, "--topic", "Suy tim") == 2


def test_main_resume_a2_khong_lam_roi_ung_vien_va_khong_ghi_de_phieu(tmp_path, monkeypatch, capsys):
    """P1-03: lượt 1 dừng ở B2 (hạ tầng) sau khi A2 tìm được ứng viên; resume phải THẤY ứng viên, giữ phiếu cũ."""
    m = _nap_op("orch_main5")
    a2 = {"status": "PASS", "topics": [{"candidates": [1, 2, 3]}]}
    da_chay, _db = _khung(tmp_path, monkeypatch, m, a2_json=a2, rc_theo_buoc={"verify_dashboard": 2})
    assert _chay_main(m, monkeypatch, "--topic", "Suy tim") == 2
    rid = next((tmp_path / "logs").glob("*.jsonl")).stem
    # lượt 2: B2 nay chạy được
    _khung(tmp_path / "x", monkeypatch, m, a2_json=a2) if False else None
    monkeypatch.setattr(m, "_chay_that", lambda lenh, timeout: 0)
    rc = _chay_main(m, monkeypatch, "--resume", rid)
    out = capsys.readouterr().out
    phieu = (tmp_path / "logs" / f"{rid}.phieu.md").read_text(encoding="utf-8")
    assert "Lượt resume" in phieu, "phiếu lượt 1 bị ghi đè"
    assert "3 ứng viên" in phieu.split("Lượt resume", 1)[1], \
        "resume làm rơi ứng viên A2 ⇒ phần phiếu của lượt resume nói «không có việc» (âm tính giả)"
    assert rc == 0 and "🟢 xong, sạch" not in out


def test_main_resume_nang_online_chay_lai_b2(tmp_path, monkeypatch, capsys):
    """P1-07: chạy offline xong rồi --resume --online ⇒ B2 phải chạy lại với --online, không bị coi «đã xong»."""
    m = _nap_op("orch_main6")
    da_chay, _db = _khung(tmp_path, monkeypatch, m, a2_json={"status": "PASS", "topics": []})
    assert _chay_main(m, monkeypatch, "--topic", "Suy tim") == 0
    rid = next((tmp_path / "logs").glob("*.jsonl")).stem
    da_chay.clear()
    assert _chay_main(m, monkeypatch, "--resume", rid, "--online") == 0
    b2 = [l for l in da_chay if any("verify_dashboard" in str(x) for x in l)]
    assert b2 and "--online" in b2[0], "resume --online bỏ qua B2 offline cũ ⇒ không lệnh online nào chạy"


def test_main_dashboard_doi_sau_khi_xong_thi_resume_chay_lai(tmp_path, monkeypatch, capsys):
    m = _nap_op("orch_main7")
    da_chay, db = _khung(tmp_path, monkeypatch, m, a2_json={"status": "PASS", "topics": []})
    assert _chay_main(m, monkeypatch, "--topic", "Suy tim") == 0
    rid = next((tmp_path / "logs").glob("*.jsonl")).stem
    import os, time
    db.write_text("<html>doi</html>", encoding="utf-8")
    os.utime(db, ns=(time.time_ns() + 10**9, time.time_ns() + 10**9))
    da_chay.clear()
    assert _chay_main(m, monkeypatch, "--resume", rid) == 0
    assert any("verify_dashboard" in str(x) for l in da_chay for x in l), "dashboard đã đổi mà B2 vẫn bị coi «xong»"


def test_main_chu_de_chua_co_dashboard_khong_ket_luan_sach(tmp_path, monkeypatch, capsys):
    """P1-04: B1 «chưa có dashboard» phải vào phiếu và kết luận cuối, không «🟢 xong, sạch»."""
    m = _nap_op("orch_main8")
    _khung(tmp_path, monkeypatch, m, a2_json={"status": "PASS", "topics": []})
    monkeypatch.setattr(m, "_dashboards_cua_chu_de", lambda t: [])
    monkeypatch.setattr(m, "_phan_giai", lambda t: {"q": t, "loai": "watchlist", "wl_topics": [t], "a2_arg": t,
                                                    "goc": [], "lat_cat": [], "ly_do": "", "gan_dung": [], "cach": "x"})
    rc = _chay_main(m, monkeypatch, "--topic", "Hen phế quản")
    out = capsys.readouterr().out
    phieu = next((tmp_path / "logs").glob("*.phieu.md")).read_text(encoding="utf-8")
    assert "CHƯA có dashboard" in phieu and "🟢 xong, sạch" not in out


def test_main_offline_duoc_noi_ra(tmp_path, monkeypatch, capsys):
    """P1-18: không --online ⇒ kết luận nói rõ B2 offline."""
    m = _nap_op("orch_main9")
    _khung(tmp_path, monkeypatch, m, a2_json={"status": "PASS", "topics": []})
    assert _chay_main(m, monkeypatch, "--topic", "Suy tim") == 0
    assert "OFFLINE" in capsys.readouterr().out


def test_main_co_xung_dot_bi_tu_choi(tmp_path, monkeypatch, capsys):
    """P1-12: --cu-nhat 0 / -2, --cu-nhat + --topic, --resume + --topic ⇒ rc 64."""
    m = _nap_op("orch_main10")
    _khung(tmp_path, monkeypatch, m)
    for argv in (("--cu-nhat", "0"), ("--cu-nhat", "-2"), ("--cu-nhat", "2", "--topic", "COPD"),
                 ("--resume", "abc", "--topic", "COPD")):
        assert _chay_main(m, monkeypatch, *argv, "--dry-run") == 64, argv


def test_thieu_tep_khong_bi_doc_thanh_nguon_bi_rut(tmp_path):
    """P1-06: script/dashboard không tồn tại ⇒ THIEU_TEP ⇒ «tham_so», không phải «rut»."""
    m = _nap_op("orch_main11")
    rc = m._chay_that([m.PY, str(tmp_path / "khong-ton-tai.py")], 5)
    assert rc == m.THIEU_TEP
    muc, msg = m.phan_loai("A4-so-xac-minh[X]", rc)
    assert muc == "tham_so" and "rút" not in msg.split("—")[0]


def test_phieu_lat_cat_cu_nhat_khong_ghi_nham_moi_nhat(tmp_path):
    """P1-10: hai lát cắt 6 và 100 ngày ⇒ lời phải nói «cũ nhất 100», không «mới nhất 100»."""
    import datetime as dt
    m = _nap_op("orch_main12")
    mo = lambda d: tmp_path / f"WebDashboard_EBM_VanDeCuThe_A_{(dt.date.today() - dt.timedelta(days=d)):%Y%m%d}.html"
    viec = m.phieu_can_phien("x", {"loai": "watchlist", "a2_arg": "W"}, [mo(6), mo(100)],
                             {"ung_vien": 0, "rut": [], "lat_hong": set()}, frozenset())
    assert viec and "cũ nhất 100" in viec[0] and "mới nhất" not in viec[0]


def test_gop_khong_ro_co_lat_cat_van_noi_a2_bi_bo():
    """P1-15: gốc chưa khai ánh xạ nhưng có lát cắt ⇒ phải có dòng A2-bo-qua (trước đây im lặng)."""
    m = _nap_op("orch_main13")
    tt = {"q": "ChuaKhai", "loai": "khong_ro", "wl_topics": [], "a2_arg": None, "goc": [], "gan_dung": [],
          "lat_cat": [{"duong_dan": "/tmp/WebDashboard_EBM_VanDeCuThe_ChuaKhai_20260101.html"}], "ly_do": "CHƯA khai", "cach": ""}
    m._phan_giai = lambda t: tt
    ke = m.ke_hoach("ChuaKhai", False, False)
    assert any(b["buoc"].startswith("A2-bo-qua") for b in ke)
