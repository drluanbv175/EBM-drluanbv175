"""Kiểm `tools/do_nhay_kiem_ngu_nghia.py` (đo độ nhạy K1–K4 bằng đột biến tổng hợp, 14/11/2026) — ngoại tuyến.

Văn bản nguồn là tóm tắt TỰ DỰNG theo khuôn efetch dạng text (không trích nguyên văn bài báo nào). Dashboard là
fixture tự dựng; không cần EBM-Dashboards/ (chạy được trên bản sao git trần/CI).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

_TEP = Path(__file__).resolve().parent / "do_nhay_kiem_ngu_nghia.py"
_sp = importlib.util.spec_from_file_location("do_nhay_kiem_ngu_nghia", _TEP)
M = importlib.util.module_from_spec(_sp)
sys.modules["do_nhay_kiem_ngu_nghia"] = M
_sp.loader.exec_module(M)

DASH_HTML = """<html><script>
const DATA = {
  meta:{question:'Thử đo độ nhạy', updated:'2026-11-14'},
  summary:{conclusion:'x', doNow:[], dontDo:[], redFlags:[]},
  items:[
    {id:'ITEM-01', title:'Thuốc X ở CKD', pmid:'101', decision:'apply',
     population:'Người lớn ĐTĐ típ 2, eGFR ≥ 25 (n=4,304)',
     action:'Dùng thuốc X nếu không có chống chỉ định, khi eGFR ≥ 25 ml/phút.'},
    {id:'ITEM-02', title:'Thuốc Y trong suy tim', pmid:'102', decision:'apply',
     population:'Suy tim HFrEF, EF ≤ 40%', action:'Khởi trị thuốc Y ở bệnh nhân đã tối ưu điều trị nền.'},
    {id:'ITEM-03', title:'C', pmid:'103', decision:'consider', population:'HFpEF', action:'c'},
    {id:'ITEM-04', title:'Bỏ thuốc lá', doi:'10.0000/fake.104', decision:'apply', population:'Người hút thuốc',
     action:'Tư vấn bỏ thuốc lá ngoài thai kỳ, dùng varenicline khi đã đặt ngày bỏ.'}
  ]
};
// HẾT KHỐI DATA
</script></html>"""

NGUON = {
    "101": ("1. Fake J Med. 2026;1:1-2. doi: 10.0000/fake.101.\n\n"
            "Drug X in adults with type 2 diabetes and chronic kidney disease.\n\n"
            "Author A(1), Author B(1).\n\n"
            "Author information:\n(1)Department of Medicine, Example University Hospital.\n\n"
            "BACKGROUND: Drug X lowers plasma glucose.\n"
            "METHODS: We randomized 4,304 adults with type 2 diabetes and an eGFR of 25 to 75.\n"
            "RESULTS: Over 2 years the composite outcome occurred less often with drug X.\n"
            "CONCLUSIONS: Drug X reduced the risk of kidney failure in adults with type 2 diabetes.\n\n"
            "DOI: 10.0000/fake.101\nPMID: 101"),
    "102": ("1. Fake J Med. 2026;1:3-4. doi: 10.0000/fake.102.\n\n"
            "Drug Y in heart failure with reduced ejection fraction.\n\n"
            "Author C(1).\n\n"
            "Author information:\n(1)Heart Institute, Example City.\n\n"
            "BACKGROUND: Many adults remain symptomatic; drug Z is not recommended in this setting.\n"
            "METHODS: Adults with reduced ejection fraction and an ejection fraction of 40% or less were enrolled.\n"
            "CONCLUSIONS: Drug Y improved outcomes in adults with reduced ejection fraction.\n\n"
            "PMID: 102"),
}


def _nguon_fn(pmids):
    co = {p: NGUON[p] for p in pmids if p in NGUON}
    return co, {"can": len(pmids), "co_san": len(co), "tai_moi": 0, "tai_hong": 0}


def _dash(thu_muc: Path, ten: str = "WebDashboard_EBM_ThuDoNhay_20261114.html", html: str = DASH_HTML) -> Path:
    thu_muc.mkdir(parents=True, exist_ok=True)
    p = thu_muc / ten
    p.write_text(html, encoding="utf-8", newline="\n")
    return p


def _rec(item_id: str, tmp_path: Path) -> dict:
    p = _dash(tmp_path)
    data = M._k3().doc_data(p)
    muc = M.lay_muc_apply({p: data})
    return next(r for r in muc if r["muc"].get("id") == item_id)


def _lam_pass(dash: Path) -> None:
    """Dựng đúng điều kiện «đã qua cổng» của dây chuyền: sidecar băm DATA + bản Word HTML có câu PASS."""
    tt = M._tt()
    d = dash.parent / "derivatives"
    d.mkdir(exist_ok=True)
    ma = tt.ma_phai_sinh(dash)
    (d / f"{ma}_TaiLieuChiTiet.data-sha256").write_text(tt.bam_data(dash) + "\n", encoding="utf-8", newline="\n")
    (d / f"{ma}_TaiLieuChiTiet.html").write_text(f"<p>verify_dashboard.py --online {tt.CAU_PASS}</p>",
                                                  encoding="utf-8", newline="\n")


# ───────────────────────── tiện ích ─────────────────────────

def test_wilson_gia_tri_chuan_va_mau_so_0():
    lo, hi = M.wilson(0, 10)
    assert lo == 0.0 and abs(hi - 0.2775) < 1e-3
    lo, hi = M.wilson(10, 10)
    assert abs(lo - 0.7225) < 1e-3 and abs(hi - 1.0) < 1e-9
    lo, hi = M.wilson(5, 10)
    assert abs(lo - 0.2366) < 1e-3 and abs(hi - 0.7634) < 1e-3
    assert M.wilson(0, 0) is None                     # mẫu số 0 ⇒ CHƯA ĐO, không bao giờ 0%


def test_rng_tat_dinh_theo_khoa():
    assert M.rng_cho(7, "a", 1).random() == M.rng_cho(7, "a", 1).random()
    assert M.rng_cho(7, "a", 1).random() != M.rng_cho(7, "a", 2).random()
    assert M.rng_cho(7, "a", 1).random() != M.rng_cho(8, "a", 1).random()


def test_doan_than_bo_tac_gia_va_dinh_danh():
    than = M.van_ban_than(NGUON["101"])
    assert "Drug X in adults" in than and "CONCLUSIONS" in than
    assert "Example University" not in than and "Author A" not in than and "PMID" not in than


def test_boc_luy_dang_qua_chuan_hoa():
    raw = "<p>khi eGFR &lt;30 thì giảm liều; HbA1c &gt; 7</p>"
    x = M.chuan_hoa(raw)
    assert M.chuan_hoa(M._boc(x)) == x                # văn bản đã chuẩn hoá đi qua doi_chieu không bị cắt nhầm


# ───────────────────────── bộ sinh: nhãn theo cấu trúc ─────────────────────────

def test_sinh_k1_doi_nhan_quan_the(tmp_path):
    rec = _rec("ITEM-01", tmp_path)
    db = M.sinh_k1(rec, NGUON["101"], 1)
    assert db["phep"] == "K1" and db["truong"] == "k1_cap" and db["trong_pham_vi"]
    b = db["dich"]["ve_muc"]
    assert b in ("ĐTĐ típ 1", "trẻ em")              # nguồn chỉ nêu người lớn + típ 2 ⇒ vế đổi sang phải là vế kia
    viet = db["bien_the"].split(":", 1)[1]
    assert viet in db["muc_dot_bien"]["population"]
    assert db["muc_dot_bien"]["population"] != rec["muc"]["population"]
    assert M.sinh_k1(rec, NGUON["101"], 1) == db      # tất định


def test_sinh_k2_nguong_va_co_mau(tmp_path):
    rec = _rec("ITEM-01", tmp_path)
    db = M.sinh_k2_nguong(rec, NGUON["101"], 3)
    assert db["truong"] == "k1_nguong" and db["dich"]["chi_so"] == "egfr"
    so_moi = db["dich"]["so"]
    assert so_moi != "25" and so_moi in db["muc_dot_bien"]["population"]
    assert not M._co_so(so_moi, M.chuan_hoa(NGUON["101"]))      # giá trị mới KHÔNG có trong nguồn ⇒ chắc chắn sai
    db2 = M.sinh_k2_co_mau(rec, NGUON["101"], 3)
    assert db2["truong"] == "k2_co_mau" and db2["bien_the"] == "thay_n"
    assert db2["dich"]["so"] != "4304" and not M._co_co_mau(db2["dich"]["so"], M.chuan_hoa(NGUON["101"]))
    # ngưỡng trong HÀNH ĐỘNG: ngoài phạm vi thiết kế của K1/K2
    db3 = M.sinh_k2_nguong(rec, NGUON["101"], 3, truong_hanh_dong=True)
    assert db3["lop"] == "K2_nguong_hanh_dong" and db3["trong_pham_vi"] is False
    assert db3["muc_dot_bien"]["population"] == rec["muc"]["population"]


def test_k2_chi_chon_gia_tri_nguon_khong_neu(tmp_path):
    rec = _rec("ITEM-01", tmp_path)
    nguon = NGUON["101"].replace("CONCLUSIONS:", "Subgroups by eGFR 15, 20, 30 and 45 were similar.\nCONCLUSIONS:")
    for hat in range(6):
        assert M.sinh_k2_nguong(rec, nguon, hat)["dich"]["so"] == "60"   # mọi giá trị khác đã có trong nguồn


def test_sinh_k3_hai_bien_the_cung_mot_cum(tmp_path):
    rec = _rec("ITEM-04", tmp_path)
    ban_xuat, trong_muc = M.sinh_k3(rec, 5, None)
    assert ban_xuat["lop"] == "K3_rung_ban_xuat" and ban_xuat["trong_pham_vi"]
    assert ban_xuat["bien_the"].startswith("ban_xuat_tong_hop|")
    assert ban_xuat["muc_dot_bien"] == rec["muc"]                # bản xuất mất cụm, mục giữ nguyên
    cum = ban_xuat["dich"]["cum"]
    assert cum in ban_xuat["ban_xuat_goc"] and cum not in ban_xuat["ban_xuat_dot_bien"]
    # 14/11/2026c: rụng NGAY TRONG MỤC thuộc phạm vi phép mới K3b (so mục với NGUỒN)
    assert trong_muc["lop"] == "K3_rung_trong_muc" and trong_muc["trong_pham_vi"] is True
    assert trong_muc["phep"] == "K3b" and trong_muc["truong"] == "k3b"
    assert cum not in M.chuan_hoa(trong_muc["muc_dot_bien"]["action"])
    assert trong_muc["ban_xuat_goc"] == trong_muc["ban_xuat_dot_bien"] == M.chuan_hoa(trong_muc["muc_dot_bien"]["action"])


def test_tim_dieu_kien_gom_dau_ngoai_k3_va_nguong():
    ds = M.tim_dieu_kien("Dùng statin ở người ≥ 75 tuổi, giảm liều khi eGFR < 30; loại trừ ung thư")
    nhom = [x["nhom"] for x in ds]
    assert "dau_khac:ở người" in nhom and "dau_k3:khi" in nhom
    assert not any(n.startswith("dau_khac:trừ") for n in nhom)  # «loại trừ» không phải điều kiện
    ds2 = M.tim_dieu_kien("Dapagliflozin cho CKD eGFR ≥ 25")
    assert [x["nhom"] for x in ds2] == ["nguong_so:egfr"] and ds2[0]["cum"] == "eGFR ≥ 25"


def test_sinh_k4_dao_cau_ket_luan(tmp_path):
    rec = _rec("ITEM-01", tmp_path)
    db = M.sinh_k4_nguon(rec, NGUON["101"], 9)
    assert db["bien_the"] == "qua_khu:did_not" and db["trong_pham_vi"]
    assert "Drug X did not reduce the risk of kidney failure" in db["nguon_dot_bien"]
    assert db["nguon_dot_bien"].replace("did not reduce", "reduced") == NGUON["101"]   # chỉ đổi đúng một chỗ
    # «reduced ejection fraction» là tính từ quần thể, KHÔNG được đảo
    db2 = M.sinh_k4_nguon(_rec("ITEM-02", tmp_path), NGUON["102"], 9)
    assert "reduced ejection fraction" in db2["nguon_dot_bien"] and "did not improve outcomes" in db2["nguon_dot_bien"]
    db3 = M.sinh_k4_muc(rec, NGUON["101"], 9)
    assert db3["trong_pham_vi"] is True and db3["phep"] == "K4b" and db3["truong"] == "k4b"   # phạm vi K4b từ 14/11c
    assert db3["muc_dot_bien"]["action"].split()[0] in ("KHÔNG", "Tránh", "Không")


# ───────────────────────── chấm: quy kết đúng chỗ ─────────────────────────

def _db(truong, dich, phep="K1"):
    return {"phep": phep, "truong": truong, "dich": dich, "muc_dot_bien": {}, "nguon_dot_bien": ""}


def _bo(r):
    return {"kiem_muc": lambda it, src: r}


def test_cham_k124_phan_loai_ket_qua():
    db = _db("k1_cap", {"ve_muc": "HFpEF"})
    goc = {"k1_cap": [], "k1_nguong": [], "k2_co_mau": [], "k4": {"muc": "khop"}}
    def mk(muc):
        return {"k1_cap": [{"ve_muc": "HFpEF", "ve_nguon": "HFrEF", "muc": muc}], "k4": {"muc": "khop"}}
    assert M.cham_k124(db, goc, _bo(mk("can_doc"))) == "bat"
    assert M.cham_k124(db, goc, _bo(mk("khop"))) == "lot_xanh"
    assert M.cham_k124(db, goc, _bo(mk("chua_kiem"))) == "lot_trang"         # ⚪ KHÔNG BAO GIỜ là bắt
    assert M.cham_k124(db, goc, _bo({"k1_cap": [], "k4": {"muc": "khop"}})) == "lot_im"
    lech = {"k1_cap": [{"ve_muc": "người lớn", "ve_nguon": "trẻ em", "muc": "can_doc"}], "k4": {"muc": "khop"}}
    assert M.cham_k124(db, goc, _bo(lech)) == "bat_lech"                     # 🟠 MỚI nhưng ở phần tử khác
    assert M.cham_k124(db, lech, _bo(lech)) == "lot_im"                      # 🟠 có sẵn từ đối chứng ⇒ không quy được
    # nhiều dòng cho CÙNG phần tử đích (vd population + pico.P): chỉ cần một dòng 🟠 là bắt — 🟠 thắng ✓
    hai = {"k1_cap": [{"ve_muc": "HFpEF", "ve_nguon": "HFpEF", "muc": "khop"},
                      {"ve_muc": "HFpEF", "ve_nguon": "HFrEF", "muc": "can_doc"}], "k4": {"muc": "khop"}}
    assert M.cham_k124(db, goc, _bo(hai)) == "bat"
    db2 = _db("k1_nguong", {"chi_so": "hba1c", "so": "7.5"}, "K2")
    r = {"k1_nguong": [{"chi_so": "hba1c", "so": "7.5", "muc": "can_doc"}]}
    assert M.cham_k124(db2, goc, _bo(r)) == "bat"
    db4 = _db("k4", {}, "K4")
    assert M.cham_k124(db4, goc, _bo({"k4": {"muc": "can_doc"}})) == "bat"
    assert M.cham_k124(db4, goc, _bo({"k4": {"muc": "khop"}})) == "lot_xanh"


def test_cham_k3_chi_bat_khi_cum_lat_tu_con_sang_can_doc():
    bo = M.bo_kiem_that()
    it = {"id": "X", "decision": "apply", "action": "Dùng thuốc X khi eGFR ≥ 30 ml/phút."}
    a0 = M.chuan_hoa(it["action"])
    db = {"muc_dot_bien": it, "ban_xuat_goc": a0, "ban_xuat_dot_bien": M.chuan_hoa("Dùng thuốc X.")}
    assert M.cham_k3(db, bo) == "bat"
    db_kg = {**db, "ban_xuat_goc": M.chuan_hoa("Dùng thuốc X.")}
    assert M.cham_k3(db_kg, bo) == "lot_xanh"         # đối chứng đã 🟠 ⇒ không quy cho đột biến
    db_im = {"muc_dot_bien": {"id": "Y", "decision": "apply", "action": "Dùng thuốc X."},
             "ban_xuat_goc": "dùng thuốc x.", "ban_xuat_dot_bien": "dùng thuốc x."}
    assert M.cham_k3(db_im, bo) == "lot_im"


# ───────────────────────── chọn dashboard ─────────────────────────

def test_chon_dashboard_ban_pass_moi_nhat(tmp_path):
    for ten in ("WebDashboard_EBM_A_20261001.html", "WebDashboard_EBM_A_20261101.html",
                "WebDashboard_EBM_B_20261005.html", "WebDashboard_EBM_B_20261105.html"):
        _dash(tmp_path, ten)
    (tmp_path / "WebDashboard_EBM_B_20261105.html.bak-x").write_text("x", encoding="utf-8", newline="\n")
    khong_pass = {"WebDashboard_EBM_A_20261101.html"}
    ds = M.chon_dashboard(tmp_path, lambda p: p.name not in khong_pass)
    assert [p.name for p in ds] == ["WebDashboard_EBM_A_20261001.html", "WebDashboard_EBM_B_20261105.html"]


def test_luat_pass_that_qua_sidecar_va_cau_pass(tmp_path):
    p = _dash(tmp_path, "WebDashboard_EBM_VanDeCuThe_ThuPass_20261114.html")
    assert M.da_pass_that(p) is False
    _lam_pass(p)
    assert M.da_pass_that(p) is True
    word = tmp_path / "derivatives" / "ThuPass_20261114_TaiLieuChiTiet.html"
    word.write_text("<p>CHƯA xác minh nguồn sống</p>", encoding="utf-8", newline="\n")
    assert M.da_pass_that(p) is False                  # thiếu câu PASS của cổng ⇒ không tính là đã qua cổng


def test_khu_trung_muc_giua_hai_chu_de(tmp_path):
    a = _dash(tmp_path, "WebDashboard_EBM_A_20261114.html")
    b = _dash(tmp_path, "WebDashboard_EBM_B_20261114.html")
    d = M._k3().doc_data(a)
    muc = M.lay_muc_apply({a: d, b: M._k3().doc_data(b)})
    assert sorted(r["muc"]["id"] for r in muc) == ["ITEM-01", "ITEM-02", "ITEM-04"]


# ───────────────────────── đầu–cuối với bộ kiểm THẬT ─────────────────────────

def test_dau_cuoi_noi_dung_ham_kiem_that_va_tat_dinh(tmp_path):
    _dash(tmp_path)
    kq = M.do_tat_ca(tmp_path, hat=11, nguon_fn=_nguon_fn, da_pass=lambda p: True)
    assert kq["so_dashboard_pass"] == 1 and kq["so_muc_apply"] == 3 and kq["so_muc_co_nguon"] == 2
    theo = {(d["id"], d["lop"]): d for d in kq["dot_bien"]}
    # dây nối tới hàm kiểm thật: đảo «reduced» ⇒ «did not reduce» là dạng K4 có trong từ điển ⇒ phải bắt
    assert theo[("ITEM-01", "K4_nguon_nguoc")]["ket_qua"] == "bat"
    assert theo[("ITEM-01", "K2_co_mau")]["ket_qua"] == "bat"
    assert ("ITEM-04", "K3_rung_ban_xuat") in theo        # mục không có PMID vẫn đo được K3
    assert not any(d["id"] == "ITEM-03" for d in kq["dot_bien"])   # consider không vào
    assert kq["doi_chung"]["muc"]["K4"]["n"] == 2 and kq["doi_chung"]["muc"]["K4"]["bao"] == 1
    # đối chứng K4 của ITEM-02 đã 🟠 ⇒ 🟠 sau đột biến không quy được ⇒ KHÔNG sinh đột biến K4 cho mục đó
    assert not any(d["id"] == "ITEM-02" and d["phep"] == "K4" for d in kq["dot_bien"])
    bj = M.ban_json(kq, hat=11, ngay="20261114")
    s = M.json_gon(bj)
    assert json.loads(s)["tong_hop"] == json.loads(json.dumps(bj["tong_hop"]))
    assert "Example University" not in s and "kidney failure in adults" not in s   # không chép văn bản nguồn
    kq2 = M.do_tat_ca(tmp_path, hat=11, nguon_fn=_nguon_fn, da_pass=lambda p: True)
    assert M.json_gon(M.ban_json(kq2, hat=11, ngay="20261114")) == s               # tất định


def test_k3_dung_ban_word_that_khi_hanh_dong_co_trong_ban_xuat(tmp_path):
    p = _dash(tmp_path, "WebDashboard_EBM_VanDeCuThe_ThuWord_20261114.html")
    d = tmp_path / "derivatives"
    d.mkdir()
    (d / "ThuWord_20261114_TaiLieuChiTiet.html").write_text(
        "<h2>ITEM-04</h2><p>Tư vấn bỏ thuốc lá <b>ngoài thai kỳ</b>, dùng varenicline khi đã đặt ngày bỏ.</p>",
        encoding="utf-8", newline="\n")
    kq = M.do_tat_ca(tmp_path, hat=5, nguon_fn=_nguon_fn, da_pass=lambda x: x == p)
    db = next(x for x in kq["dot_bien"] if x["id"] == "ITEM-04" and x["lop"] == "K3_rung_ban_xuat")
    assert db["bien_the"].startswith("ban_xuat_that|") and db["ket_qua"] == "bat"


def test_main_chay_kho_khong_ghi_roi_ghi(tmp_path, capsys):
    p = _dash(tmp_path / "dash", "WebDashboard_EBM_VanDeCuThe_ThuMain_20261114.html")
    _lam_pass(p)
    dem = tmp_path / "nguon.json"
    dem.write_text(json.dumps(NGUON), encoding="utf-8", newline="\n")
    truoc = hashlib.sha256(dem.read_bytes()).hexdigest()
    ra = tmp_path / "bao-cao"
    rc = M.main(["--thu-muc", str(tmp_path / "dash"), "--bo-dem", str(dem), "--bao-cao", str(ra), "--ngay", "20261114"])
    assert rc in (0, 1) and not ra.exists()            # chạy khô: không ghi gì
    assert "chạy khô" in capsys.readouterr().out
    rc = M.main(["--thu-muc", str(tmp_path / "dash"), "--bo-dem", str(dem), "--bao-cao", str(ra), "--ngay", "20261114",
                 "--ghi"])
    tj, tm = ra / "do-nhay-dot-bien-20261114.json", ra / "do-nhay-dot-bien-20261114.md"
    assert tj.is_file() and tm.is_file()
    md = tm.read_bytes().decode("utf-8")
    assert "\r\n" not in md and "TỔNG HỢP" in md and "KHÔNG thay bộ vàng" in md and "Cần bác sĩ kiểm chứng" in md
    bj = json.loads(tj.read_text(encoding="utf-8"))
    assert bj["hat_giong"] == M.HAT_GIONG_MAC_DINH
    assert all(r["ket_qua"] not in ("bat", "bat_lech") for r in bj["dot_bien_lot"])   # chỉ liệt kê phần bỏ lọt
    assert hashlib.sha256(dem.read_bytes()).hexdigest() == truoc    # không --online ⇒ không đụng bộ đệm


def test_khong_do_duoc_la_ma_2(tmp_path, capsys):
    assert M.main(["--thu-muc", str(tmp_path / "khong-co")]) == 2
    (tmp_path / "rong").mkdir()
    assert M.main(["--thu-muc", str(tmp_path / "rong"), "--bo-dem", str(tmp_path / "x.json")]) == 2
    assert "không đo được" in capsys.readouterr().out


def test_ma_thoat_theo_so_phep_do_duoc():
    def th(*n):
        assert len(n) == len(M.PHEP)
        return {"theo_phep_trong_pham_vi": {p: {"n": k} for p, k in zip(M.PHEP, n)}}
    assert M.PHEP == ("K1", "K2", "K3", "K3b", "K4", "K4b")
    assert M.ma_thoat(th(3, 2, 5, 4, 1, 6)) == 0
    assert M.ma_thoat(th(3, 0, 5, 4, 1, 6)) == 1       # một phép CHƯA ĐO ⇒ không phải 0
    assert M.ma_thoat(th(3, 2, 5, 0, 1, 6)) == 1       # K3b chưa đo cũng vậy
    assert M.ma_thoat(th(0, 0, 0, 0, 0, 0)) == 2


# ───────────────────────── chẩn đoán lý do lọt (thẩm định 14/11: quy kết K3 theo cụm K3 THỰC trích) ─────────────────────────

def _rec_tay(action: str) -> dict:
    return {"muc": {"id": "ITEM-T", "decision": "apply", "action": action}, "dashboard": "WebDashboard_EBM_T.html",
            "chi_so": 0, "duong_dan": Path("WebDashboard_EBM_T.html")}


def _k3_ban_xuat(action: str, word_html: str, cum_bo_sinh: str) -> dict:
    """Đột biến K3 ở bản xuất THẬT, chọn hạt giống để bộ sinh rụng đúng `cum_bo_sinh`, rồi chấm bằng bộ kiểm THẬT."""
    rec, word = _rec_tay(action), M.gon_dau(M.chuan_hoa(word_html))
    for hat in range(200):
        dbs = M.sinh_k3(rec, hat, word)
        if dbs and dbs[0]["dich"]["cum"] == M.chuan_hoa(cum_bo_sinh):
            db = {**dbs[0], "dashboard": rec["dashboard"], "id": "ITEM-T", "pmid": None, "_khoa": ("T", 0)}
            assert db["bien_the"].startswith("ban_xuat_that|")
            M.cham_tat_ca([db], {}, M.bo_kiem_that())
            return db
    raise AssertionError(f"bộ sinh không chọn được cụm {cum_bo_sinh!r}")


def test_ly_do_k3_khong_trich_cum_du_cum_bo_sinh_con_cho_khac():
    # K3 không coi «ở người …» là điều kiện ⇒ lot_im; cụm của BỘ SINH còn ở mục khác trong Word nhưng điều đó không cứu được
    db = _k3_ban_xuat("Dùng statin ở người ≥ 75 tuổi.",
                      "<p>Dùng statin ở người ≥ 75 tuổi.</p><p>Mục khác: theo dõi ở người ≥ 75 tuổi.</p>",
                      "ở người ≥ 75 tuổi")
    assert db["ket_qua"] == "lot_im"
    assert db["k3_chan_doan"] == {"so_cum_k3": 0, "cum_k3_bi_cat": 0, "cum_k3_bi_cat_con_cho_khac": 0,
                                  "pham_vi": "tai_lieu"}
    assert db["ly_do_lot"] == "k3_khong_trich_cum"


def test_ly_do_k3_trich_cum_khac_khi_cum_k3_van_nguyen():
    # bộ sinh cắt «ở người …» (ngoài từ điển K3); cụm K3 «khi eGFR …» còn nguyên trong hành động đã cắt
    db = _k3_ban_xuat("Dùng thuốc X khi eGFR ≥ 30 ml/phút, ở người ≥ 75 tuổi.",
                      "<p>Dùng thuốc X khi eGFR ≥ 30 ml/phút, ở người ≥ 75 tuổi.</p><p>Theo dõi ở người ≥ 75 tuổi.</p>",
                      "ở người ≥ 75 tuổi")
    assert db["ket_qua"] == "lot_xanh"
    assert db["k3_chan_doan"]["so_cum_k3"] == 1 and db["k3_chan_doan"]["cum_k3_bi_cat"] == 0
    assert db["ly_do_lot"] == "k3_trich_cum_khac"


def test_ly_do_k3_khop_cap_tai_lieu_chi_khi_cum_k3_bi_cat_con_o_muc_khac():
    db = _k3_ban_xuat("Dùng thuốc X khi eGFR ≥ 30 ml/phút.",
                      "<p>Dùng thuốc X khi eGFR ≥ 30 ml/phút.</p><p>Giảm liều thuốc Z khi eGFR ≥ 30 ml/phút.</p>",
                      "khi eGFR ≥ 30 ml/phút")
    assert db["ket_qua"] == "lot_xanh"
    assert db["k3_chan_doan"] == {"so_cum_k3": 1, "cum_k3_bi_cat": 1, "cum_k3_bi_cat_con_cho_khac": 1,
                                  "pham_vi": "tai_lieu"}
    assert db["ly_do_lot"] == "cum_con_o_cho_khac_trong_ban_xuat"
    # cùng mục, Word KHÔNG có cụm ở chỗ khác ⇒ K3 bắt (không có lý do lọt)
    db2 = _k3_ban_xuat("Dùng thuốc X khi eGFR ≥ 30 ml/phút.", "<p>Dùng thuốc X khi eGFR ≥ 30 ml/phút.</p>",
                       "khi eGFR ≥ 30 ml/phút")
    assert db2["ket_qua"] == "bat" and db2["ly_do_lot"] is None
    assert db2["k3_chan_doan"] == {"so_cum_k3": 1, "cum_k3_bi_cat": 1, "cum_k3_bi_cat_con_cho_khac": 0,
                                   "pham_vi": "tai_lieu"}


def test_ly_do_k3_khong_chan_doan_duoc_la_khac():
    db = {"lop": "K3_rung_ban_xuat", "trong_pham_vi": True, "ket_qua": "lot_xanh"}
    assert M.ly_do_lot(db, None, None) == "khac"                       # không có chẩn đoán ⇒ không đoán lý do
    def cd(bi_cat, con):
        return {**db, "k3_chan_doan": {"so_cum_k3": 2, "cum_k3_bi_cat": bi_cat, "cum_k3_bi_cat_con_cho_khac": con}}
    assert M.ly_do_lot(cd(0, 0), None, None) == "k3_trich_cum_khac"
    assert M.ly_do_lot(cd(1, 1), None, None) == "cum_con_o_cho_khac_trong_ban_xuat"
    assert M.ly_do_lot(cd(1, 0), None, None) == "khac"                 # cụm K3 bị cắt mà không còn chỗ khác vẫn lọt: lạ
    assert M.ly_do_lot({**cd(1, 1), "ket_qua": "lot_im"}, None, None) == "k3_khong_trich_cum"   # lot_im xét TRƯỚC
    assert M.chan_doan_k3({"muc_dot_bien": {}, "ban_xuat_dot_bien": ""}, M.bo_kiem_that()) is None


def _k3_gia(ket_qua: str, ly_do: str | None, nhom: str = "dau_k3:khi") -> dict:
    # cờ cũ «cum_con_cho_khac» (theo cụm của bộ sinh) cố ý = True: tổng hợp KHÔNG được dựa vào nó
    return {"lop": "K3_rung_ban_xuat", "phep": "K3", "trong_pham_vi": True, "bien_the": f"ban_xuat_that|{nhom}",
            "ket_qua": ket_qua, "ly_do_lot": ly_do, "cum_con_cho_khac": True}


def test_tong_hop_k3_quy_ket_va_do_nhay_neu_so_theo_tung_muc():
    ds = ([_k3_gia("bat", None)] * 5 + [_k3_gia("lot_im", "k3_khong_trich_cum", "dau_khac:ở người")] * 3
          + [_k3_gia("lot_xanh", "k3_trich_cum_khac", "nguong_so:egfr")] * 2
          + [_k3_gia("lot_xanh", "cum_con_o_cho_khac_trong_ban_xuat")]
          + [_k3_gia("lot_xanh", "khac")])
    kp = M.tong_hop(ds)["k3_phu"]
    assert (kp["n"], kp["bat"], kp["lot"]) == (12, 5, 7)
    assert kp["lot_k3_khong_trich_cum"] == 3 and kp["lot_k3_trich_cum_khac"] == 2
    assert kp["lot_do_khop_cap_tai_lieu"] == 1 and kp["lot_khac"] == 1      # số đếm các lý do cố ý khác nhau
    assert abs(kp["do_nhay_neu_so_theo_tung_muc"] - 6 / 12) < 1e-12        # (bắt + khớp cấp tài liệu) / n, n KHÔNG bị bớt
    assert kp["ktc95_neu_so_theo_tung_muc"] == M.wilson(6, 12)
    dk = kp["theo_nhom_dau"]["dau_k3"]
    assert (dk["n"], dk["bat"]) == (7, 5) and dk["ktc95"] == M.wilson(5, 7)


def test_k1_trong_tu_dien_hoi_bo_kiem_that():
    assert M.k1_trong_tu_dien("trẻ em", "nhi khoa") is True
    # 14/11/2026c: từ điển bộ kiểm đã mở rộng — các cách viết từng lọt im nay được nhận
    assert M.k1_trong_tu_dien("trẻ em", "bệnh nhi") is True
    assert M.k1_trong_tu_dien("trẻ em", "trẻ vị thành niên") is True
    assert M.k1_trong_tu_dien("người lớn", "người trưởng thành") is True
    assert M.k1_trong_tu_dien("HFpEF", "suy tim phân suất tống máu còn bảo tồn") is True
    assert M.k1_trong_tu_dien("HFrEF", "suy tim PSTM giảm") is True
    assert M.k1_trong_tu_dien("ĐTĐ típ 1", "ĐTĐ tuýp 1") is True
    assert M.k1_trong_tu_dien("ĐTĐ típ 1", "ĐTĐ1") is True
    assert M.k1_trong_tu_dien("ngoài thai kỳ", "phụ nữ không mang thai") is True
    assert M.k1_trong_tu_dien("trẻ em", "trẻ nhỏ") is False               # vẫn có cách viết ngoài từ điển — hàm phải nói thật


def test_tong_hop_k1_tach_trong_ngoai_tu_dien(tmp_path):
    rec = _rec("ITEM-01", tmp_path)
    db = M.sinh_k1(rec, NGUON["101"], 1)
    viet = db["bien_the"].split(":", 1)[1]
    assert db["tu_dien_bo_kiem"] is M.k1_trong_tu_dien(db["dich"]["ve_muc"], viet)
    def k1(tu_dien, kq):
        return {"lop": "K1_quan_the", "phep": "K1", "trong_pham_vi": True, "bien_the": "x", "ket_qua": kq,
                "tu_dien_bo_kiem": tu_dien}
    th = M.tong_hop([k1(True, "bat")] * 3 + [k1(True, "lot_xanh")] + [k1(False, "lot_im")] * 4)
    assert (th["k1_phu"]["trong_tu_dien"]["n"], th["k1_phu"]["trong_tu_dien"]["bat"]) == (4, 3)
    assert (th["k1_phu"]["ngoai_tu_dien"]["n"], th["k1_phu"]["ngoai_tu_dien"]["bat"]) == (4, 0)
    assert th["theo_phep_trong_pham_vi"]["K1"]["n"] == 8


def test_chan_doan_nguon_dem_doan_chuan_hoa_xoa():
    ngan = "LNM risk < 3 % in group A and > 5 % in group B."
    dai = "Rate < 2 " + "x" * 250 + " > end. Drug Z is not recommended."
    the = "Drug <i>X</i> reduced events."
    nguon = {"1": ngan, "2": dai, "3": "No comparison signs at all.", "4": the}
    # mẫu CŨ (trước bản vá 14/11/2026): mọi «<…>» là thẻ ⇒ 3 nguồn bị cắt, có đoạn > 200 ký tự
    assert [len(M.vung_bi_cat(nguon[k], mau_cu=True)) for k in "1234"] == [1, 1, 0, 2]
    cd = M.chan_doan_nguon(nguon)
    # mẫu bộ kiểm ĐANG dùng cho nguồn: chỉ thẻ định dạng nội dòng ⇒ chỉ nguồn «4» bị bỏ (đúng 2 thẻ <i>, </i>)
    assert cd["so_nguon"] == 4 and cd["nguon_bi_cat"] == 1 and cd["nguon_bi_cat_tren_200_ky_tu"] == 0
    assert cd["ky_tu_bi_cat"] == len("<i>") + len("</i>") and cd["nguon_bi_cat_neu_mau_cu"] == 3
    assert cd["ky_tu_tong"] == sum(len(v) for v in nguon.values())
    # gắn với hành vi THẬT của bộ kiểm: chữ giữa «<» so sánh và «>» không còn bị xoá
    kq = M._kq()
    assert "group a" in kq.chuan_hoa_nguon(ngan) and "not recommended" in kq.chuan_hoa_nguon(dai)
    assert kq.chuan_hoa_nguon(the) == "drug x reduced events."


def test_ban_md_tom_tat_ghi_rieng_phan_trong_tu_dien(tmp_path):
    p = _dash(tmp_path)
    kq = M.do_tat_ca(tmp_path, hat=11, nguon_fn=_nguon_fn, da_pass=lambda x: x == p)
    th = kq["tong_hop"]
    th["k1_phu"]["trong_tu_dien"] = {**th["k1_phu"]["trong_tu_dien"], "n": 4, "bat": 3, "do_nhay": 0.75,
                                     "ktc95": M.wilson(3, 4)}
    th["k3_phu"]["theo_nhom_dau"]["dau_k3"] = {"n": 10, "bat": 7, "do_nhay": 0.7, "ktc95": M.wilson(7, 10)}
    md = M.ban_md(M.ban_json(kq, hat=11, ngay="20261114"))
    tom_tat = md.split("## Tóm tắt", 1)[1].split("## Dữ liệu", 1)[0]
    assert "K1 " in tom_tat and "riêng phần trong từ điển bộ kiểm 75% [KTC" in tom_tat and "; 3/4]" in tom_tat
    assert "riêng phần trong từ điển bộ kiểm 70% [KTC" in tom_tat and "; 7/10]" in tom_tat
    bang1 = md.split("## 1.", 1)[1].split("## 2.", 1)[0]
    assert "Riêng phần trong từ điển" in bang1 and "70% (" in bang1
    # câu so sánh hai lỗ hổng K3 phải theo SỐ ĐO, không viết cứng
    for khong, khac, cap, chu in ((3, 1, 2, "lớn hơn"), (1, 0, 3, "nhỏ hơn"), (1, 1, 2, "bằng")):
        th["k3_phu"].update(lot_k3_khong_trich_cum=khong, lot_k3_trich_cum_khac=khac, lot_do_khop_cap_tai_lieu=cap,
                            lot=khong + khac + cap, lot_khac=0)
        md = M.ban_md(M.ban_json(kq, hat=11, ngay="20261114"))
        assert f"({khong + khac}/{khong + khac + cap} lần lọt) {chu} lỗ hổng so khớp cấp tài liệu" in md
