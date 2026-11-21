# -*- coding: utf-8 -*-
"""Sổ miễn trừ (`tools/so_mien_tru.py`, 21/11/2026) — đo provenanceUnknown theo lát cắt + marker miễn trừ trong mã.

Kiểm HÀNH VI trên kho dashboard GIẢ trong thư mục tạm (ngoại tuyến, không đọc EBM-Dashboards thật):
  • phân lớp đọc bằng parser của CHÍNH cổng verify_dashboard (bản vendor qua git);
  • nhóm lát cắt bằng ĐÚNG dang_ky_chu_de.tach_ten (tên nhóm không thuộc lát cắt) và loại bản tin gộp bằng ĐÚNG
    kiem_do_tuoi_chung_cu.la_khong_can;
  • (b) tách «chỉ có cờ» khỏi «kế thừa có ghi lượt mới», mốc PRISMA-S tính từ 15/08/2026;
  • ảnh chụp chỉ ghi khi số đổi (BH153), sổ hỏng không bị ghi đè;
  • «không đo được» ⇒ do_duoc False / mã 2, không bao giờ xanh giả.
Marker trong test dựng bằng nối chuỗi để CHÍNH tệp này không thành một marker thật bị đếm.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "so_mien_tru.py"
_sp = importlib.util.spec_from_file_location("so_mien_tru_test", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

BH10 = "bh10" + "-mien:"
BIMAT = "bimat" + "-mien:"
HOM_NAY = dt.date(2026, 11, 21)


def _html(standards: str | None, co_data: bool = True) -> str:
    if not co_data:
        return "<html><body>không có khối dữ liệu</body></html>"
    st = f"  standards:{standards},\n" if standards is not None else ""
    return ("<html><script>\nconst DATA = {\n  meta:{updated:\"2026-11-01\"},\n" + st
            + "  items:[ {id:'ITEM-01', pmid:'12345678', decision:'consider', gradeLevel:'mod'} ]\n};\n"
            + "// HẾT KHỐI DATA\n</script></html>")


ST_DU = '{ frame:"PICO", searchSources:["PubMed 2026-11-01","NICE"], currency:"2026-11-01" }'
ST_CHI_CO = '{ provenanceUnknown: true, provenanceUnknownLyDo: "bản sinh trước khi khối DATA.standards thành bắt buộc" }'
ST_CO_GHI = ('{ provenanceUnknown: true, provenanceUnknownLyDo: "mục kế thừa", '
             'searchSources:["PubMed E-utilities 4 tầng (2026-11-05)"], currency:"2026-11-05 — lượt quét" }')
ST_CO_GHI_CHI_CURRENCY = '{ provenanceUnknown: true, provenanceUnknownLyDo: "kế thừa", currency:"2026-11-05" }'


def _vd():
    """Cổng bản GIT — cùng bản `so_mien_tru.nap_cong()` dùng (bản chạy EBM-Dashboards/tools chỉ chép sau khi gộp)."""
    return M.nap_cong()


def _kho(tmp_path: Path, tep: dict[str, str], khong_can: dict | None = None, muc: dict | None = None,
         watchlist: list[str] | None = None) -> Path:
    dash = tmp_path / "EBM-Dashboards"
    dash.mkdir()
    for ten, noi_dung in tep.items():
        (dash / ten).write_text(noi_dung, encoding="utf-8")
    (dash / "giam-sat-chu-de.json").write_text(json.dumps({"muc": muc or {}, "khong_can": khong_can or {}},
                                                          ensure_ascii=False), encoding="utf-8")
    (dash / "watchlist.json").write_text(json.dumps({"topics": [{"topic": w, "active": True}
                                                               for w in (watchlist or [])]}, ensure_ascii=False),
                                         encoding="utf-8")
    return dash


def _ten(nhom: str, lat: str, ngay: str) -> str:
    return f"WebDashboard_EBM_{nhom}_{lat}_{ngay}.html"


# ───────────── phân lớp bằng parser của cổng ─────────────

@pytest.mark.parametrize("standards, co_data, ky_vong", [
    (ST_DU, True, M.DU),
    (ST_CHI_CO, True, M.CHI_CO),
    (ST_CO_GHI, True, M.CO_GHI),
    (ST_CO_GHI_CHI_CURRENCY, True, M.CHI_CO),   # chỉ ngày, không nguồn ⇒ chưa ghi lượt tìm (định nghĩa của cổng)
    (None, True, M.THIEU),
    (None, False, M.KHONG_DOC),
    ('{ provenanceUnknown: false, searchSources:["a","b"] }', True, M.DU),
])
def test_phan_loai_doc_bang_parser_cua_cong(standards, co_data, ky_vong):
    assert M.phan_loai(_vd(), _html(standards, co_data)) == ky_vong


def test_chien_luoc_chi_viet_trong_ly_do_van_la_chi_co():
    """Chiến lược tìm viết VĂN XUÔI trong provenanceUnknownLyDo (kiểu DaLieu_HS 07/11) không phải trường hợp đồng."""
    st = ('{ provenanceUnknown: true, provenanceUnknownLyDo: "Lượt nối tiếp 07/11: PubMed «x»[ti] (searchStrategy/'
          'currency) — 73 bản ghi" }')
    assert M.phan_loai(_vd(), _html(st)) == M.CHI_CO


# ───────────── (a)(b) trên kho giả ─────────────

def _kho_mau(tmp_path: Path) -> Path:
    return _kho(tmp_path, {
        # lát cắt BenhA_TongHop: bản cũ chỉ cờ (07/2026) → bản mới khai đủ ⇒ KHÔNG vào (a)
        _ten("VanDeCuThe", "BenhA_TongHop", "20260701"): _html(ST_CHI_CO),
        _ten("VanDeCuThe", "BenhA_TongHop", "20261101"): _html(ST_DU),
        # BenhB: bản hiện hành CHỈ CÓ CỜ, dựng sau mốc ⇒ (a) + 🟠
        _ten("VanDeCuThe", "BenhB_DieuTri", "20261026"): _html(ST_CHI_CO),
        # BenhC: kế thừa có ghi lượt mới ⇒ (a) nhưng không 🟠
        _ten("VanDeCuThe", "BenhC_ChanDoan", "20261105"): _html(ST_CO_GHI),
        # bản tin gộp W30 mang cờ ⇒ không vào (a)
        _ten("Uptodate", "W30", "20260725"): _html(ST_CHI_CO),
        # đúng ngày 14/08 (trước mốc) chỉ cờ ⇒ không vào (b)
        _ten("VanDeCuThe", "BenhD", "20260814"): _html(ST_CHI_CO),
        # tên không tách được
        "WebDashboard_Khac.html": _html(ST_DU),
    }, khong_can={"W30": "bản tin tuần gộp"})


def _do(tmp_path: Path, dash: Path, **kw):
    kw.setdefault("cac_repo", {"goc": None})
    kw.setdefault("tep_state", tmp_path / "state" / "so-mien-tru.json")
    kw.setdefault("hom_nay", HOM_NAY)
    return M.do(dash=dash, **kw)


def test_a_b_tren_kho_gia(tmp_path):
    kq = _do(tmp_path, _kho_mau(tmp_path))
    assert kq["do_duoc"] is True
    assert [b["lat_cat"] for b in kq["a"]] == ["BenhD", "BenhB_DieuTri", "BenhC_ChanDoan"]
    assert kq["lat_cat_tong"] == 5 and kq["lat_cat_lam_moi_duoc"] == 4 and kq["tai_lap_duoc"] == 1
    assert [b["lat_cat"] for b in kq["b_chi_co_hien_hanh"]] == ["BenhB_DieuTri"]
    assert [b["lat_cat"] for b in kq["b_co_ghi_hien_hanh"]] == ["BenhC_ChanDoan"]
    assert kq["b_tong"] == 2 and kq["b_chi_co_tong"] == 1 and kq["b_co_ghi_tong"] == 1
    assert kq["tong_dashboard"] == 6 and kq["tong_mien"] == 5
    assert kq["khong_tach"] == ["WebDashboard_Khac.html"]
    assert kq["theo_thang"]["2026-11"] == {"tong": 2, "mien": 1}


def test_nhom_lat_cat_bang_dang_ky_chu_de_ten_nhom_khong_thuoc_lat_cat(tmp_path):
    """Đúng logic dang_ky_chu_de.tach_ten: CongCuKeDon_X cũ bị VanDeCuThe_X mới thay (đo 21/11: ThuocTamThanKinh)."""
    dash = _kho(tmp_path, {
        _ten("CongCuKeDon", "ThuocTamThanKinh", "20260620"): _html(ST_CHI_CO),
        _ten("VanDeCuThe", "ThuocTamThanKinh", "20261021"): _html(ST_DU),
    })
    kq = _do(tmp_path, dash)
    assert kq["lat_cat_tong"] == 1 and kq["a"] == []


def test_ban_tin_gop_loai_theo_goc_cua_lat_cat(tmp_path):
    """la_khong_can khớp cả lát cắt lẫn phần đầu trước «_» (vd khong_can khai «NgoaiTru»)."""
    dash = _kho(tmp_path, {_ten("CapNhatTuan", "NgoaiTru_TongHop", "20260609"): _html(ST_CHI_CO)},
                khong_can={"NgoaiTru": "bản tin gộp"})
    kq = _do(tmp_path, dash)
    assert kq["a"] == [] and kq["lat_cat_lam_moi_duoc"] == 0 and kq["lat_cat_tong"] == 1


def test_khong_doc_duoc_giam_sat_chu_de_la_chua_do(tmp_path):
    dash = _kho(tmp_path, {_ten("VanDeCuThe", "BenhB", "20261026"): _html(ST_CHI_CO)})
    (dash / "giam-sat-chu-de.json").write_text("{hỏng", encoding="utf-8")
    kq = _do(tmp_path, dash)
    assert kq["do_duoc"] is True
    assert any("giam-sat-chu-de.json" in c for c in kq["chua_do"])


# ───────────── không đo được ⇒ ⚪ ─────────────

def test_vang_ebm_dashboards_khong_do_duoc_va_khong_ghi_anh_chup(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "goc_du_lieu", lambda ten: None)
    tep = tmp_path / "state" / "so-mien-tru.json"
    kq = M.do(cac_repo={"goc": None}, tep_state=tep, hom_nay=HOM_NAY)
    assert kq["do_duoc"] is False and "EBM-Dashboards" in kq["ly_do"]
    assert not tep.exists()


def test_kho_rong_khong_phai_0_mien_tru(tmp_path):
    kq = _do(tmp_path, _kho(tmp_path, {}))
    assert kq["do_duoc"] is False and "không phải «0 miễn trừ»" in kq["ly_do"]


def test_main_ma_thoat(tmp_path, monkeypatch, capsys):
    tep = tmp_path / "st.json"
    assert M.main(["--dash", str(_kho_mau(tmp_path)), "--tep-state", str(tep), "--khong-ghi"]) == 1
    assert not tep.exists()
    sach = tmp_path / "sach"
    sach.mkdir()
    assert M.main(["--dash", str(_kho(sach, {_ten("VanDeCuThe", "BenhA", "20261101"): _html(ST_DU)})),
                   "--tep-state", str(tep), "--khong-ghi"]) == 0
    monkeypatch.setattr(M, "goc_du_lieu", lambda ten: None)
    assert M.main(["--tep-state", str(tep), "--khong-ghi"]) == 2
    assert "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out


# ───────────── (c) marker trong mã ─────────────

def _repo_git(tmp_path: Path, tep: dict[str, str], chua_track: dict[str, str] | None = None) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    for ten, nd in tep.items():
        (r / ten).write_text(nd, encoding="utf-8")
    subprocess.run(["git", "-C", str(r), "add", "-A"], check=True)
    for ten, nd in (chua_track or {}).items():
        (r / ten).write_text(nd, encoding="utf-8")
    return r


def test_dem_marker_chi_dem_marker_that_tren_tep_track(tmp_path):
    r = _repo_git(tmp_path, {
        "a.py": f"x = ghi(decision)  # {BH10} fixture tạm, không phải dashboard\n"
                f"# {BH10} lý do khác\n"
                f"# nhắc tên marker `{BH10}` trong tài liệu\n"     # không đứng ngay sau «#»
                f"#{BH10}\n",                                       # không có lý do
        "b.py": f"k = 'gia'  # {BIMAT} khoá giả cho test\n",
    }, chua_track={"c.py": f"# {BH10} chưa track\n"})
    m = M.dem_marker(r)
    assert m["dem"] == {"bh10-mien": 2, "bimat-mien": 1}
    assert m["vi_tri"]["bimat-mien"] == ["b.py:1"]


def test_dem_marker_khong_phai_repo_la_none(tmp_path):
    assert M.dem_marker(tmp_path) is None


# ───────────── (d) ảnh chụp BH153 + ⓘ marker tăng ─────────────

def test_anh_chup_chi_ghi_khi_so_doi_va_moi_ngay_mot_dong(tmp_path):
    dash = _kho_mau(tmp_path)
    tep = tmp_path / "state" / "so-mien-tru.json"
    kq1 = _do(tmp_path, dash, tep_state=tep)
    assert kq1["anh_chup"] == "ghi"
    mtime = tep.stat().st_mtime_ns
    assert _do(tmp_path, dash, tep_state=tep)["anh_chup"] == "khong_doi"
    assert tep.stat().st_mtime_ns == mtime
    # ngày khác, số không đổi ⇒ vẫn không ghi
    assert _do(tmp_path, dash, tep_state=tep, hom_nay=HOM_NAY + dt.timedelta(days=1))["anh_chup"] == "khong_doi"
    # cùng ngày, số đổi ⇒ thay dòng của ngày đó (không thêm dòng)
    (dash / _ten("VanDeCuThe", "BenhB_DieuTri", "20261120")).write_text(_html(ST_DU), encoding="utf-8")
    assert _do(tmp_path, dash, tep_state=tep)["anh_chup"] == "ghi"
    ls = json.loads(tep.read_text(encoding="utf-8"))["lich_su"]
    assert [x["ngay"] for x in ls] == ["2026-11-21"] and ls[0]["a_lat_cat"] == ["BenhD", "BenhC_ChanDoan"]
    # ngày khác, số đổi ⇒ thêm dòng
    (dash / _ten("VanDeCuThe", "BenhC_ChanDoan", "20261121")).write_text(_html(ST_DU), encoding="utf-8")
    assert _do(tmp_path, dash, tep_state=tep, hom_nay=HOM_NAY + dt.timedelta(days=2))["anh_chup"] == "ghi"
    assert [x["ngay"] for x in json.loads(tep.read_text(encoding="utf-8"))["lich_su"]] == ["2026-11-21",
                                                                                          "2026-11-23"]


def test_anh_chup_hong_khong_bi_ghi_de(tmp_path):
    tep = tmp_path / "state" / "so-mien-tru.json"
    tep.parent.mkdir()
    tep.write_text("{không phải json", encoding="utf-8")
    kq = _do(tmp_path, _kho_mau(tmp_path), tep_state=tep)
    assert kq["anh_chup"] == "hong"
    assert tep.read_text(encoding="utf-8") == "{không phải json"
    assert any("hỏng" in c for c in kq["chua_do"])


def _lich_su(ngay: str, bh10: int) -> list[dict]:
    return [{"ngay": ngay, "marker": {"goc": {"bh10-mien": bh10, "bimat-mien": 1}}}]


def test_marker_tang_so_anh_chup_du_7_ngay():
    hien_tai = {"goc": {"dem": {"bh10-mien": 6, "bimat-mien": 1}}, "y_khoa": None}
    assert M.marker_tang(_lich_su("2026-11-14", 5), hien_tai, HOM_NAY) == ("2026-11-14", {"goc:bh10-mien": (5, 6)})
    assert M.marker_tang(_lich_su("2026-11-15", 5), hien_tai, HOM_NAY) is None      # mới 6 ngày
    assert M.marker_tang(_lich_su("2026-11-01", 6), hien_tai, HOM_NAY) is None      # không tăng
    assert M.marker_tang([], hien_tai, HOM_NAY) is None


# ───────────── giác quan cho tu_de_xuat_viec ─────────────

def test_giac_quan_cam_va_vang_kem_lenh_orchestrator(tmp_path):
    dash = _kho(tmp_path, {
        _ten("VanDeCuThe", "BenhB_DieuTri", "20261026"): _html(ST_CHI_CO),
        _ten("VanDeCuThe", "BenhC_ChanDoan", "20261105"): _html(ST_CO_GHI),
    }, muc={"BenhC": "Bệnh C"}, watchlist=["Bệnh C"])
    viec, tt, chet, chua = M.giac_quan(dash=dash, cac_repo={"goc": None}, tep_state=tmp_path / "s.json",
                                       hom_nay=HOM_NAY)
    assert chet == [] and tt == []
    cam = [v for v in viec if v[0] == 1]
    vang = [v for v in viec if v[0] == 3]
    # chưa có sổ nợ ⇒ cổng ĐANG CHẶN bản hiện hành chỉ có cờ
    assert len(cam) == 1 and "ĐANG CHẶN" in cam[0][2] and "BenhB_DieuTri" in cam[0][2]
    assert "BenhC_ChanDoan" not in cam[0][2], "bản kế thừa đã ghi lượt mới không bị chặn"
    assert "chưa ánh xạ watchlist" in cam[0][2]
    # BenhC (kế thừa, có ánh xạ watchlist) ⇒ dòng 🟡 kèm lệnh orchestrator chạy được A2
    assert len(vang) == 1 and vang[0][3] == 'python3 ops/orchestrator.py --topic "BenhC_ChanDoan" --online'
    assert "BenhB_DieuTri" not in vang[0][2], "chủ đề đã có dòng chặn/nợ không lặp ở dòng 🟡"
    assert all(v[1] == "👤" for v in viec)


def test_giac_quan_khong_lat_cat_nao_anh_xa_thi_ghi_chu(tmp_path):
    dash = _kho(tmp_path, {_ten("VanDeCuThe", "BenhB_DieuTri", "20261026"): _html(ST_CHI_CO)})
    viec, *_ = M.giac_quan(dash=dash, cac_repo={"goc": None}, tep_state=tmp_path / "s.json", hom_nay=HOM_NAY)
    assert len(viec) == 1
    assert '--topic "BenhB_DieuTri"' in viec[0][3] and "chưa ánh xạ watchlist" in viec[0][2]


def test_giac_quan_sach_khong_viec(tmp_path):
    dash = _kho(tmp_path, {_ten("VanDeCuThe", "BenhA", "20261101"): _html(ST_DU)})
    assert M.giac_quan(dash=dash, cac_repo={"goc": None}, tep_state=tmp_path / "s.json",
                       hom_nay=HOM_NAY) == ([], [], [], [])


def test_giac_quan_khong_do_duoc_la_chet(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "goc_du_lieu", lambda ten: None)
    viec, tt, chet, _ = M.giac_quan(cac_repo={"goc": None}, tep_state=tmp_path / "s.json", hom_nay=HOM_NAY)
    assert viec == [] and len(chet) == 1 and "EBM-Dashboards" in chet[0]


def test_giac_quan_marker_tang_la_dong_thong_tin(tmp_path):
    r = _repo_git(tmp_path, {"a.py": f"# {BH10} một\n# {BH10} hai\n"})
    tep = tmp_path / "s.json"
    tep.write_text(json.dumps({"lich_su": _lich_su("2026-11-01", 1)}), encoding="utf-8")
    dash = _kho(tmp_path, {_ten("VanDeCuThe", "BenhA", "20261101"): _html(ST_DU)})
    viec, tt, chet, _ = M.giac_quan(dash=dash, cac_repo={"goc": r}, tep_state=tep, hom_nay=HOM_NAY)
    assert viec == [] and chet == []
    assert len(tt) == 1 and "goc:bh10-mien 1→2" in tt[0] and "2026-11-01" in tt[0]


# ───────────── nối dây: tu_de_xuat_viec + Đài hoàn thiện ─────────────

def _nap_tdxv():
    sp = importlib.util.spec_from_file_location("tdxv_so_mien_tru", M.TOOLS / "tu_de_xuat_viec.py")
    T = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(T)
    return T


def test_tu_de_xuat_viec_noi_giac_quan_va_ghi_chet(tmp_path):
    T = _nap_tdxv()
    dash = _kho(tmp_path, {_ten("VanDeCuThe", "BenhB_DieuTri", "20261026"): _html(ST_CHI_CO)})
    viec = T.giac_quan_so_mien_tru(dash=dash, cac_repo={"goc": None}, tep_state=tmp_path / "s.json", hom_nay=HOM_NAY)
    assert [v[0] for v in viec] == [1] and T._GIAC_QUAN_CHET == [] and T._SO_GIAC_QUAN["chay"] == 1
    # không đo được ⇒ giác quan CHẾT (⚪), không phải «không còn việc»
    T2 = _nap_tdxv()
    tep_hong = tmp_path / "hong.json"
    tep_hong.write_text("{", encoding="utf-8")
    assert T2.giac_quan_so_mien_tru(dash=tmp_path / "khong-co", cac_repo={"goc": None}, tep_state=tep_hong,
                                    hom_nay=HOM_NAY) == []
    assert len(T2._GIAC_QUAN_CHET) == 1 and "sổ miễn trừ" in T2._GIAC_QUAN_CHET[0]
    assert any("hỏng" in c for c in T2._CHUA_DO)


def test_main_tu_de_xuat_viec_goi_giac_quan_so_mien_tru():
    """Công cụ không ai gọi thì không tồn tại: main() phải GỌI giác quan (khớp dòng thi hành, không khớp bình luận)."""
    nguon = (M.TOOLS / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    dong = [d for d in nguon.splitlines() if not d.lstrip().startswith("#") and "giac_quan_so_mien_tru(dash" in d]
    # dash=DASH: test trỏ DASH vào thư mục tạm thì giác quan không đọc/ghi dữ liệu thật (đo 21/11: test gradeBy
    # gọi main() đã ghi state/so-mien-tru.json thật khi giác quan tự dò dashboard).
    assert dong and dong[0].lstrip().startswith("de_xuat += giac_quan_so_mien_tru(dash=DASH)")


def test_dash_vang_khong_ghi_anh_chup(tmp_path):
    """DASH (của main) trỏ thư mục không tồn tại ⇒ giác quan ⚪ và KHÔNG ghi tệp ảnh chụp."""
    T = _nap_tdxv()
    tep = tmp_path / "state" / "so-mien-tru.json"
    assert T.giac_quan_so_mien_tru(dash=tmp_path / "khong-co", cac_repo={"goc": None}, tep_state=tep) == []
    assert len(T._GIAC_QUAN_CHET) == 1 and not tep.exists()


def _nap_dai():
    sp = importlib.util.spec_from_file_location("dai_so_mien_tru", M.TOOLS / "do_dai_hoan_thien.py")
    D = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(D)
    return D


def test_dai_hoan_thien_thuoc_do_tai_lap(tmp_path, monkeypatch):
    D = _nap_dai()
    ra = {"do_duoc": True, "tai_lap_duoc": 93, "lat_cat_lam_moi_duoc": 102,
          "b_chi_co_hien_hanh": [{"lat_cat": "X"}] * 5}
    monkeypatch.setattr(D, "_chay", lambda cmd, *a, **k: json.dumps(ra) if "tools/so_mien_tru.py" in cmd else None)
    h = {x["ma"]: x for x in D.thuoc_do(tmp_path, tmp_path, [], [], [])}["E-TAILAP"]
    assert h["hien_tai"] == "93/102 · 5 bản mới CHỈ CÓ CỜ" and h["so"] == 93 and h["trang_thai"] == "chua"
    ra.update(tai_lap_duoc=102, b_chi_co_hien_hanh=[])
    assert {x["ma"]: x for x in D.thuoc_do(tmp_path, tmp_path, [], [], [])}["E-TAILAP"]["trang_thai"] == "dat"
    ra["do_duoc"] = False
    assert {x["ma"]: x for x in D.thuoc_do(tmp_path, tmp_path, [], [], [])}["E-TAILAP"]["trang_thai"] == "khong_do"


# ───────────── sổ nợ cổng provenance gói mới ─────────────

CAN_CU = "«chặn có sổ nợ» — bác sĩ trả lời câu hỏi thử (21/11/2026)"


class _A:
    def __init__(self, dash, **kw):
        self.dash, self.tep_state = dash, dash.parent / "s.json"
        self.tao, self.gia_han, self.han, self.can_cu, self.ghi = (kw.get("tao", False), kw.get("gia_han"),
                                                                   kw.get("han"), kw.get("can_cu"), kw.get("ghi", False))


def test_hang_so_trung_voi_cong():
    vd = _vd()
    assert M.TEN_SO_NO == vd.TEN_SO_NO_PROVENANCE
    assert M.MOC_PRISMA_S == vd.MOC_PROVENANCE_GOI_MOI.strftime("%Y%m%d")
    assert (M.DU, M.CO_GHI, M.CHI_CO, M.THIEU) == (vd.PROV_DU, vd.PROV_CO_GHI, vd.PROV_CHI_CO, vd.PROV_THIEU)


def test_lap_so_no_mot_lan_nguyen_van_va_chay_kho(tmp_path, capsys):
    dash = _kho_mau(tmp_path)
    tep = dash / M.TEN_SO_NO
    assert M.lenh_so_no(_A(dash, tao=True, han="2026-12-21", can_cu="ngắn"), HOM_NAY) == 3
    assert M.lenh_so_no(_A(dash, tao=True, han="2027-03-01", can_cu=CAN_CU), HOM_NAY) == 3      # > 90 ngày
    assert M.lenh_so_no(_A(dash, tao=True, han="2026-12-21", can_cu=CAN_CU), HOM_NAY) == 0 and not tep.exists()
    assert M.lenh_so_no(_A(dash, tao=True, han="2026-12-21", can_cu=CAN_CU, ghi=True), HOM_NAY) == 0
    so = json.loads(tep.read_text(encoding="utf-8"))
    # chỉ tệp CHỈ CÓ CỜ dựng từ mốc (BenhB 26/10); BenhD 14/08 (trước mốc) và BenhC kế thừa có ghi KHÔNG vào nợ
    assert [m["dashboard"] for m in so["muc"]] == ["WebDashboard_EBM_VanDeCuThe_BenhB_DieuTri_20261026"]
    assert so["han"] == "2026-12-21" and so["can_cu"] == CAN_CU
    assert M.lenh_so_no(_A(dash, tao=True, han="2026-12-21", can_cu=CAN_CU, ghi=True), HOM_NAY) == 3   # bánh cóc
    assert M.lenh_so_no(_A(dash, gia_han="2027-01-10", can_cu=CAN_CU, ghi=True), HOM_NAY) == 0
    so2 = json.loads(tep.read_text(encoding="utf-8"))
    assert so2["han"] == "2027-01-10" and so2["muc"] == so["muc"] and so2["lich_su"][0]["han_cu"] == "2026-12-21"
    assert M.lenh_so_no(_A(dash), HOM_NAY) == 0
    assert "nợ trong hạn 1 tệp" in capsys.readouterr().out


def test_bao_no_ma_1_khi_cong_dang_chan(tmp_path, capsys):
    assert M.lenh_so_no(_A(_kho_mau(tmp_path)), HOM_NAY) == 1
    assert "cổng ĐANG CHẶN 1 tệp" in capsys.readouterr().out


def test_gia_han_tu_choi_so_hong(tmp_path):
    dash = _kho_mau(tmp_path)
    (dash / M.TEN_SO_NO).write_text("{hỏng", encoding="utf-8")
    assert M.lenh_so_no(_A(dash, gia_han="2026-12-30", can_cu=CAN_CU, ghi=True), HOM_NAY) == 3
    assert (dash / M.TEN_SO_NO).read_text(encoding="utf-8") == "{hỏng"
    kq = _do(tmp_path, dash)
    assert kq["so_no"]["hong"] and any("KHÔNG đọc được" in c for c in kq["chua_do"])
    assert len(kq["so_no"]["ngoai_so"]) == 1, "sổ hỏng ⇒ coi như vắng: cổng chặn"


def _kho_no(tmp_path: Path, han: str) -> Path:
    dash = _kho(tmp_path, {_ten("VanDeCuThe", "BenhB_DieuTri", "20261026"): _html(ST_CHI_CO)})
    (dash / M.TEN_SO_NO).write_text(json.dumps({"han": han, "can_cu": CAN_CU, "muc": [
        {"dashboard": "WebDashboard_EBM_VanDeCuThe_BenhB_DieuTri_20261026"}]}), encoding="utf-8")
    return dash


@pytest.mark.parametrize("han, uu, chu", [("2026-12-21", 2, "NỢ provenance"), ("2026-11-25", 1, "còn 4 ngày"),
                                          ("2026-11-20", 1, "ĐANG CHẶN")])
def test_giac_quan_no_trong_han_sap_han_qua_han(tmp_path, han, uu, chu):
    viec, *_ = M.giac_quan(dash=_kho_no(tmp_path, han), cac_repo={"goc": None}, tep_state=tmp_path / "s.json",
                           hom_nay=HOM_NAY)
    assert len(viec) == 1 and viec[0][0] == uu and chu in viec[0][2]


def test_anh_chup_ghi_so_cong_chan_va_no(tmp_path):
    tep = tmp_path / "state" / "so-mien-tru.json"
    _do(tmp_path, _kho_no(tmp_path, "2026-12-21"), tep_state=tep)
    dong = json.loads(tep.read_text(encoding="utf-8"))["lich_su"][-1]
    assert dong["cong_chan"] == 0 and dong["no_trong_han"] == 1

