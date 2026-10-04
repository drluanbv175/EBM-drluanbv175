# -*- coding: utf-8 -*-
"""Test BẢO ĐẢM ĐỌC TOÀN VĂN (04/10/2026 — bác sĩ: «Hãy xây dựng đảm bảo việc đọc toàn văn cho tôi»). Ngoại tuyến hoàn toàn.

Đo thật 04/10: cổng chỉ chặn mục apply thẩm định từ tóm tắt khi mục TỰ KHAI 'partial' ⇒ 27 mục apply (20 PMID) không có toàn văn
vẫn qua cổng; chuỗi theo chủ đề không có bước toàn văn. Vá bốn lớp: nguồn sự thật `bao_phu_cuc_bo` (loại trang giới thiệu) ·
cổng BÁNH CÓC + sổ nợ (`verify_dashboard.kiem_toan_van_apply`) · sổ `tools/so_toan_van.py` · giác quan hòm việc · bước «TV».
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


vd = _nap("sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py", "_vd_tvbd")
tv = _nap("tools/toan_van_theo_chu_de.py", "_tv_tvbd")
op = _nap("ops/orchestrator.py", "_op_tvbd")
stv = _nap("tools/so_toan_van.py", "_stv_tvbd")
dtv = _nap("tools/doc_toan_van_co_nguoi.py", "_dtv_tvbd")
tdx = _nap("tools/tu_de_xuat_viec.py", "_tdx_tvbd")

HOM_NAY = date(2026, 10, 4)
TRANG_GIOI_THIEU = ("<html><body>Abstract Introduction Methods Results Discussion " + "w " * 2700
                    + " Fingerprint Access to Document Link to publication</body></html>")


def _muc(iid, dec, pmid, ac=None):
    them = f", appraisalCompleteness:'{ac}'" if ac else ""
    return "{id:'%s', decision:'%s', pmid:'%s'%s}" % (iid, dec, pmid, them)


def _kho(tmp_path):
    kho = tmp_path / "toan_van_oa"
    (kho / "trinh_duyet").mkdir(parents=True)
    return kho


def _so_no(tmp_path, han, muc):
    (tmp_path / "no-toan-van-apply.json").write_text(json.dumps({"han": han, "muc": muc}), encoding="utf-8")


def _cong(items, kho, *, ten="DB", hom_nay=HOM_NAY):
    errors, warns, oks = [], [], []
    vd.kiem_toan_van_apply(items, kho, errors, warns, oks, ten_dashboard=ten, hom_nay=hom_nay)
    return errors, warns, oks


# ── lớp 1: nguồn sự thật ────────────────────────────────────────────────────────────────────────
def test_da_doc_gom_toan_van_may_ho_so_trinh_duyet_va_bac_si_da_doc(tmp_path):
    kho = _kho(tmp_path)
    (kho / "PMID-111111_PMC9.xml").write_text("x")
    (kho / "PMID-222222_CHR.pdf").write_text("x")
    (kho / "trinh_duyet" / "PMID-444444.json").write_text("{}")
    (kho / "trinh_duyet" / "bac-si-da-doc.jsonl").write_text(json.dumps({"pmid": "555555", "ngay": "2026-10-04"}) + "\n")
    (kho / "PMID-333333_UPW.html").write_text(TRANG_GIOI_THIEU)
    for pm in ("111111", "222222", "444444", "555555"):
        assert vd.co_toan_van_trong_kho(pm, kho), pm
    assert not vd.co_toan_van_trong_kho("333333", kho), "trang giới thiệu kho lưu trữ KHÔNG phải toàn văn"
    tt = dtv.bao_phu_cuc_bo(["111111", "333333", "444444", "555555", "666666"], kho, HOM_NAY)
    assert tt["333333"] == "chua_co", "nguồn sự thật cũng phải loại trang giới thiệu (trước 04/10 tính «oa_khac»)"
    assert [tt[p] in dtv.TRANG_THAI_DA_PHU for p in ("111111", "444444", "555555", "666666")] == [True, True, True, False]


# ── lớp 2: cổng bánh cóc ────────────────────────────────────────────────────────────────────────
def test_apply_chua_doc_ngoai_so_no_bi_chan(tmp_path):
    kho = _kho(tmp_path)
    (kho / "PMID-111111_PMC9.xml").write_text("x")
    e, w, o = _cong([_muc("ITEM-01", "apply", "111111"), _muc("ITEM-02", "apply", "222222"), _muc("ITEM-03", "consider", "3")], kho)
    assert len(e) == 1 and "ITEM-02" in e[0] and "222222" in e[0] and "KHÔNG có trong sổ nợ" in e[0]
    assert any("1/2" in x for x in o)


def test_no_trong_han_chi_canh_bao_qua_han_thi_chan(tmp_path):
    kho = _kho(tmp_path)
    _so_no(tmp_path, "2026-11-03", [{"dashboard": "DB", "item": "ITEM-02", "pmid": "222222"}])
    e, w, _ = _cong([_muc("ITEM-02", "apply", "222222")], kho)
    assert not e and len(w) == 1 and "NỢ TOÀN VĂN" in w[0] and "2026-11-03" in w[0]
    e2, _, _ = _cong([_muc("ITEM-02", "apply", "222222")], kho, hom_nay=date(2026, 11, 4))
    assert len(e2) == 1 and "QUÁ HẠN" in e2[0]


def test_banh_coc_muc_moi_khong_duoc_ke_vao_no_cu(tmp_path):
    kho = _kho(tmp_path)
    _so_no(tmp_path, "2026-11-03", [{"dashboard": "DB", "item": "ITEM-02", "pmid": "222222"}])
    e, _, _ = _cong([_muc("ITEM-09", "apply", "999999")], kho)
    assert len(e) == 1, "mục apply MỚI chưa đọc toàn văn phải bị chặn ngay dù đã có sổ nợ"
    e2, _, _ = _cong([_muc("ITEM-02", "apply", "222222")], kho, ten="DB_KHAC")
    assert len(e2) == 1, "khoá sổ nợ gồm cả tên dashboard"


def test_so_no_hong_thi_chan_va_bao(tmp_path):
    kho = _kho(tmp_path)
    (tmp_path / "no-toan-van-apply.json").write_text("{hỏng", encoding="utf-8")
    e, w, _ = _cong([_muc("ITEM-02", "apply", "222222")], kho)
    assert len(e) == 1 and any("KHÔNG đọc được" in x for x in w)


def test_tu_khai_full_khong_thay_bang_chung(tmp_path):
    e, _, _ = _cong([_muc("ITEM-01", "apply", "123456", ac="full")], _kho(tmp_path))
    assert len(e) == 1, "tự khai «full» mà kho không có bằng chứng đọc ⇒ vẫn chặn"


def test_bac_si_da_doc_tra_no(tmp_path):
    kho = _kho(tmp_path)
    (kho / "trinh_duyet" / "bac-si-da-doc.jsonl").write_text(json.dumps({"pmid": "222222", "ngay": "2026-10-05"}) + "\n")
    e, w, _ = _cong([_muc("ITEM-02", "apply", "222222")], kho)
    assert not e and not w


def test_khong_thay_kho_thi_khong_do(tmp_path):
    e, w, o = _cong([_muc("ITEM-01", "apply", "111111")], tmp_path / "khong_co")
    assert not e and not w and any("CHƯA đo" in x for x in o)


def test_main_cong_that_su_goi_bao_dam(tmp_path):
    """DÒNG THI HÀNH: main() trên dashboard tối giản, kho rỗng bên cạnh, không sổ nợ ⇒ lỗi bảo đảm + mã thoát ≠ 0."""
    _kho(tmp_path)
    db = tmp_path / "WebDashboard_EBM_VanDeCuThe_X_20261004.html"
    db.write_text("<script>const DATA = {meta:{}, summary:{}, items:[" + _muc("ITEM-01", "apply", "123456")
                  + "]};\n/* HẾT KHỐI DATA */</script>", encoding="utf-8")
    r = subprocess.run([sys.executable, str(REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py"),
                        str(db), "--strict-sources"], capture_output=True, text=True)
    assert "PMID 123456 CHƯA được đọc toàn văn" in r.stdout + r.stderr and r.returncode != 0


def test_hai_ban_cong_trung_byte():
    assert (REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py").read_bytes() == \
        (REPO / "sync/skills/dark-analyst/tools/verify_dashboard.py").read_bytes()


# ── lớp 3: sổ bảo đảm ───────────────────────────────────────────────────────────────────────────
def _dash_mau(tmp_path):
    dash = tmp_path / "EBM-Dashboards"
    kho = dash / "toan_van_oa"
    (kho / "trinh_duyet").mkdir(parents=True)
    (kho / "PMID-111111_PMC9.xml").write_text("x")
    (dash / "WebDashboard_EBM_VanDeCuThe_A_20261004.html").write_text(
        "<script>const DATA = {items:[" + _muc("ITEM-01", "apply", "111111") + "," + _muc("ITEM-02", "apply", "222222")
        + "," + _muc("ITEM-03", "consider", "333333") + "]};\n/* HẾT KHỐI DATA */</script>", encoding="utf-8")
    return dash


def test_so_lap_no_mot_lan_can_loi_bac_si_va_han_toi_da(tmp_path, capsys):
    dash = _dash_mau(tmp_path)
    loi = "bác sĩ: hãy xây dựng bảo đảm đọc toàn văn cho tôi"
    assert stv.main(["--tao-no", "--han", "2026-11-03", "--can-cu", "ngắn", "--ghi"], dash=dash, hom_nay=HOM_NAY) == 3
    assert stv.main(["--tao-no", "--han", "2027-06-01", "--can-cu", loi, "--ghi"], dash=dash, hom_nay=HOM_NAY) == 3
    assert stv.main(["--tao-no", "--han", "2026-11-03", "--can-cu", loi, "--ghi"], dash=dash, hom_nay=HOM_NAY) == 0
    so = json.loads((dash / "no-toan-van-apply.json").read_text(encoding="utf-8"))
    assert [m["pmid"] for m in so["muc"]] == ["222222"] and so["can_cu"] == loi
    assert stv.main(["--tao-no", "--han", "2026-11-03", "--can-cu", loi, "--ghi"], dash=dash, hom_nay=HOM_NAY) == 3, \
        "sổ nợ chỉ được lập MỘT lần (bánh cóc)"
    assert stv.main(["--gia-han", "2026-12-03", "--can-cu", loi, "--ghi"], dash=dash, hom_nay=HOM_NAY) == 0
    so2 = json.loads((dash / "no-toan-van-apply.json").read_text(encoding="utf-8"))
    assert so2["han"] == "2026-12-03" and [m["pmid"] for m in so2["muc"]] == ["222222"] and so2["lich_su"]


def test_so_ma_thoat_theo_trang_thai(tmp_path):
    dash = _dash_mau(tmp_path)
    assert stv.main([], dash=dash, hom_nay=HOM_NAY) == 1, "mục apply chưa đọc ngoài sổ nợ ⇒ mã 1 (cổng đang chặn)"
    stv.main(["--tao-no", "--han", "2026-11-03", "--can-cu", "bác sĩ: hãy xây dựng bảo đảm toàn văn", "--ghi"], dash=dash,
             hom_nay=HOM_NAY)
    assert stv.main([], dash=dash, hom_nay=HOM_NAY) == 0, "chỉ còn nợ trong hạn ⇒ mã 0"
    assert stv.main([], dash=dash, hom_nay=date(2026, 11, 4)) == 1, "nợ quá hạn ⇒ mã 1"
    assert stv.main([], dash=tmp_path / "khong_co", hom_nay=HOM_NAY) == 2


# ── lớp 4: giác quan hòm việc ───────────────────────────────────────────────────────────────────
def test_giac_quan_no_toan_van(tmp_path):
    dash = _dash_mau(tmp_path)
    viec = tdx.giac_quan_no_toan_van(dash, HOM_NAY)
    assert viec and viec[0][0] == 1 and "ĐANG CHẶN" in viec[0][1]
    stv.main(["--tao-no", "--han", "2026-11-03", "--can-cu", "bác sĩ: hãy xây dựng bảo đảm toàn văn", "--ghi"], dash=dash,
             hom_nay=HOM_NAY)
    viec2 = tdx.giac_quan_no_toan_van(dash, HOM_NAY)
    assert len(viec2) == 1 and viec2[0][0] == 2 and "còn 30" in viec2[0][1]
    assert tdx.giac_quan_no_toan_van(dash, date(2026, 10, 30))[0][0] == 1, "≤ 7 ngày tới hạn ⇒ ưu tiên 1"


# ── bước TV của chuỗi theo chủ đề ───────────────────────────────────────────────────────────────
def _a2(tmp_path, ung_vien):
    p = tmp_path / "RID.A2-x.json"
    p.write_text(json.dumps({"topics": [{"topic": "x", "candidates": ung_vien}]}), encoding="utf-8")
    return p


def test_pmid_tu_a2_bo_bai_rut_va_trung(tmp_path):
    p = _a2(tmp_path, [{"pmid": "123456", "rut_bai": "ok"}, {"pmid": "234567", "rut_bai": "retracted"},
                       {"pmid": "123456", "rut_bai": "ok"}, {"pmid": "", "rut_bai": "ok"}, {"pmid": "345678"}])
    assert tv.pmid_tu_a2(p) == ["123456", "345678"]


def test_main_tv_goi_dung_ba_cong_cu_va_ghi_bao_cao(tmp_path):
    kho = _kho(tmp_path)
    p = _a2(tmp_path, [{"pmid": "123456", "rut_bai": "ok"}, {"pmid": "234567", "rut_bai": "ok"}])
    goi = []

    def chay(lenh):
        goi.append(lenh)
        if "gom_toan_van_dashboard.py" in lenh[1]:
            (kho / "PMID-123456_PMC1.xml").write_text("x")
        return 0, "ok"
    bc = tmp_path / "RID.TV-x.md"
    assert tv.main(["--a2-json", str(p), "--bao-cao", str(bc)], chay=chay, kho=kho) == 0
    assert [Path(l[1]).name for l in goi] == ["gom_toan_van_dashboard.py", "doc_sau_toan_van.py", "doc_toan_van_co_nguoi.py"]
    assert "--unpaywall" in goi[0] and goi[2][goi[2].index("--pmid") + 1:] == ["234567"]
    assert "+1 bài có toàn văn mới" in bc.read_text(encoding="utf-8")


def test_main_tv_json_hong_tra_2_va_khong_pmid_tra_0(tmp_path):
    hong = tmp_path / "hong.json"
    hong.write_text("{khong phai json", encoding="utf-8")
    assert tv.main(["--a2-json", str(hong), "--bao-cao", str(tmp_path / "a.md")], chay=lambda l: (0, ""), kho=tmp_path) == 2
    rong = _a2(tmp_path, [])
    assert tv.main(["--a2-json", str(rong), "--bao-cao", str(tmp_path / "b.md")], chay=lambda l: (0, ""), kho=tmp_path) == 0


def _ke(monkeypatch, tt, dbs):
    monkeypatch.setattr(op, "_phan_giai", lambda _t: tt)
    monkeypatch.setattr(op, "_dashboards_cua_chu_de", lambda _t: dbs)
    return op.ke_hoach("x", False, False, run_id="RID")


def test_buoc_tv_sau_a2_truoc_a4_va_khong_chan_chuoi(monkeypatch):
    tt = {"loai": "watchlist", "a2_arg": "Bệnh thận mạn (CKD)", "lat_cat": [], "ly_do": ""}
    db = Path("WebDashboard_EBM_VanDeCuThe_BenhThanMan_CKD_20260701.html")
    cac = _ke(monkeypatch, tt, [db])
    ten = [b["buoc"] for b in cac]
    i_a2, i_tv = ten.index("A2-quet"), ten.index("TV-toan-van")
    assert i_a2 < i_tv < min(i for i, t in enumerate(ten) if t.startswith(("A4", "B2")))
    a2, tvl = cac[i_a2]["lenh"], cac[i_tv]["lenh"]
    assert tvl[tvl.index("--a2-json") + 1] == a2[a2.index("--json-report") + 1] and str(db) in tvl
    assert op.phan_loai("TV-toan-van", 2)[0] not in op.DUNG_HET
    khong_can = {"loai": "khong_can", "a2_arg": None, "lat_cat": [], "ly_do": "bản tin gộp"}
    assert not [b for b in _ke(monkeypatch, khong_can, [db]) if b["buoc"].startswith("TV")]
