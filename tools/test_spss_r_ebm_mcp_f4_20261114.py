"""MCP «spss-r-ebm» — F4 (14/11/2026): làm sạch sau tiếp nhận · «còn thiếu gì để khoá G5» · biến phái sinh · chạy trọn SAP G6,
và phân tích G6 nhận Poisson vững / hiệp biến phân loại / lọc quần thể (F2/F3).

Như test gốc: dựng repo y khoa GIẢ trong thư mục tạm, công cụ giả cùng tên ghi lại argv và sinh đúng tệp máy chủ đọc. Không PII.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "mcp" / "spss_r_ebm_mcp.py"
_sp = importlib.util.spec_from_file_location("spss_r_ebm_mcp_f4_test", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

GHI = """import json, sys
from pathlib import Path
goc = Path(__file__).resolve().parents[1]
with open(goc / "goi.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps([Path(__file__).name, *sys.argv[1:]]) + "\\n")
a = sys.argv[1:]
def lay(co):
    return a[a.index(co) + 1] if co in a else None
"""
GIA = {
    "nhap_lieu_excel.py": GHI + """
ra = Path(lay("--ra")); ra.mkdir(parents=True, exist_ok=True)
(ra / (Path(lay("--excel")).stem + "_bao_cao_nhap.json")).write_text(json.dumps({"trang_thai": "SACH", "phat_hien": []}),
                                                                      encoding="utf-8")
if "--tiep-nhan" in a:
    if (goc / "TIEP_NHAN_LOI").exists():
        sys.exit(3)
    d = goc / "exports" / lay("--study")
    (d / "02_raw_readonly").mkdir(exist_ok=True)
    (d / "02_raw_readonly" / "data.ab12.csv").write_text("ma,x\\nP1,1\\n", encoding="utf-8")
    (d / "study_meta.json").write_text(json.dumps({"real_data_intake": {
        "raw_readonly_path": "02_raw_readonly/data.ab12.csv"}}), encoding="utf-8")
""",
    "clean_research_dataset.py": GHI + """
d = goc / "exports" / lay("--study")
mo = int((goc / "SO_QUERY").read_text()) if (goc / "SO_QUERY").exists() else 0
(d / "DATA_CLEANING_report.json").write_text(json.dumps({"status": "CLEAN_WITH_OPEN_QUERIES" if mo else "CLEAN_READY",
    "open_query_count": mo, "ready_for_lock": not mo, "row_count": 1, "query_log": "04_query_logs/q.csv"}),
    encoding="utf-8")
print("DATA_CLEANING: xong")
""",
    "g5_quality_gate.py": """import json
from pathlib import Path
GOC = Path(__file__).resolve().parents[1]
def evaluate_study(study, out_dir, *, repo_root=None, write=True):
    with open(GOC / "goi.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(["g5_quality_gate.evaluate_study", study, str(out_dir), "write=" + str(write)]) + "\\n")
    if (GOC / "G5_HONG").exists():
        raise RuntimeError("hong")
    if write:
        (Path(out_dir) / "G5_quality_report.json").write_text("{}", encoding="utf-8")
    return {"status": "BLOCKED", "automatic_criteria": [
        {"id": "G5-01", "label": "từ điển", "status": "PASS", "evidence": "", "action": ""},
        {"id": "G5-04", "label": "query đóng", "status": "BLOCKED", "evidence": "", "action": "đóng 3 query"}],
        "actions": ["đóng 3 query"], "technical_lock_valid": False, "human_approval_valid": False,
        "vai_da_ky": [], "dong_ky_du": False, "real_data_present": True}
""",
    "bien_phai_sinh.py": GHI + """
if a[0] == "kiem":  # JSON NHIỀU DÒNG (> 80) như công cụ thật — máy chủ phải đọc trọn, không cắt 80 dòng cuối
    print(json.dumps({"study": lay("--study"), "dem": {"DA_DUYET": 2, "CHUA_DUYET": 1},
                      "bien": [{"ten": f"b{i}", "dong": i} for i in range(60)]}, indent=1))
else:
    print("xong")
""",
    "chay_sap_g6.py": GHI + """
if a[0] in ("kiem", "ket-qua"):
    print(json.dumps({"lenh": a[0], "duyet": "DA_DUYET", "phan_tich": [{"id": "MT2_chinh"}]}))
else:
    print("chay xong")
""",
    "run_stats_analysis.py": GHI + '# "--hiep-bien-phan-loai" "--loc" "poisson_pr"\nprint("phan tich xong")\n',
    "kiem_cheo_g6.py": GHI + "print(json.dumps({'trang_thai': 'KHOP'}))\n",
    "doi_chieu_bien_de_cuong.py": GHI + """
if (goc / "DC_HONG").exists():
    print("khong phai json"); sys.exit(2)
ph = [{"muc": "LECH", "luat": "V2", "pham_vi": "nhap_lieu", "bien": "GioiTinh", "chi_tiet": "ma khac"},
      {"muc": "LECH", "luat": "V5", "pham_vi": "phan_tich", "bien": "NhomTuoi", "chi_tiet": "ngoai de cuong"},
      {"muc": "CAN_XEM", "luat": "V4", "pham_vi": "nhap_lieu", "bien": "x", "chi_tiet": "chi o tu dien"}]
print(json.dumps({"trang_thai": "LECH", "phat_hien": ph, "nguon_nguoi_duyet": ["DE_CUONG.md"], "dat_canh": []}, indent=1))
sys.exit(1)
""",
    "cau_noi_spss.py": """from pathlib import Path
GOC = Path(__file__).resolve().parents[1]
def tim_du_lieu_khoa(study):
    if not (GOC / "exports" / study / "KHOA").exists():
        raise RuntimeError("chua khoa")
    return GOC / "exports" / study / "khoa.csv", {"lock_date": "2026-11-14"}
""",
}


@pytest.fixture()
def yk(tmp_path, monkeypatch) -> Path:
    g = tmp_path / "y_khoa"
    (g / "tools").mkdir(parents=True)
    for ten, ma in GIA.items():
        (g / "tools" / ten).write_text(ma, encoding="utf-8")
    d = g / "exports" / "DE-TAI"
    d.mkdir(parents=True)
    (d / "study_meta.json").write_text("{}", encoding="utf-8")
    (d / "G5_REDCap_dictionary_DE-TAI.csv").write_text("x\n", encoding="utf-8")
    monkeypatch.setenv("EBM_MEDICAL_ROOT", str(g))
    monkeypatch.setenv("EBM_VENV_PYTHON", sys.executable)
    return g


def _goi(g: Path) -> list[list[str]]:
    p = g / "goi.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def _cc(ten: str, **arg):
    r = M.xu_ly({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": ten, "arguments": arg}})["result"]
    txt = r["content"][0]["text"]
    try:
        return r["isError"], json.loads(txt)
    except ValueError:
        return r["isError"], txt


def _tiep_nhan_gia(g: Path) -> None:
    d = g / "exports" / "DE-TAI"
    (d / "02_raw_readonly").mkdir(exist_ok=True)
    (d / "02_raw_readonly" / "data.ab12.csv").write_text("ma,x\nP1,1\n", encoding="utf-8")
    (d / "study_meta.json").write_text(json.dumps({"real_data_intake": {"raw_readonly_path": "02_raw_readonly/data.ab12.csv"}}),
                                       encoding="utf-8")  # fmt: skip


def test_danh_sach_co_bon_cong_cu_moi_va_van_khong_co_khoa_ky_xoa():
    ten = [t["name"] for t in M.xu_ly({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]]
    assert {"lam_sach", "g5_con_thieu", "bien_phai_sinh", "chay_sap_g6"} <= set(ten)
    assert not [t for t in ten if any(x in t for x in ("khoa", "ky_", "xoa", "lock", "approve", "delete", "duyet"))]
    sc = {t["name"]: t["inputSchema"] for t in M.xu_ly({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})["result"]["tools"]}
    assert "poisson_pr" in sc["phan_tich_g6"]["properties"]["outcome_type"]["enum"]
    assert {"hiep_bien_phan_loai", "loc"} <= set(sc["phan_tich_g6"]["properties"])
    for t in ("lam_sach", "bien_phai_sinh", "chay_sap_g6"):  # công cụ có tác dụng phải có ap_dung
        assert "ap_dung" in sc[t]["properties"], t
    assert "ap_dung" not in sc["g5_con_thieu"]["properties"]


def test_phan_tich_g6_truyen_poisson_bien_phan_loai_va_loc(yk):
    (yk / "exports" / "DE-TAI" / "KHOA").write_text("", encoding="utf-8")
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", outcome="y", group="g", covariates=["tuoi", "kg"],
                  hiep_bien_phan_loai=["kg"], outcome_type="poisson_pr", loc="hop_le == 1 and mode == 1")  # fmt: skip
    ds = kq["se_chay"]
    assert ds[ds.index("--hiep-bien-phan-loai") + 1] == "kg" and ds[ds.index("--outcome-type") + 1] == "poisson_pr"
    assert ds[ds.index("--loc") + 1] == "hop_le == 1 and mode == 1" and ds[ds.index("--covariates") + 1] == "tuoi,kg"
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", outcome="y", loc="-x == 1")
    assert loi and "không được rỗng hay bắt đầu bằng" in kq


def test_phan_tich_g6_bao_ro_khi_repo_y_khoa_chua_co_ban_f2_f3(yk):
    (yk / "exports" / "DE-TAI" / "KHOA").write_text("", encoding="utf-8")
    (yk / "tools" / "run_stats_analysis.py").write_text(GHI + "# \"--locked-x\"\nprint('cu')\n", encoding="utf-8")
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", outcome="y", loc="hop_le == 1")
    assert loi and "F3 (lọc quần thể)" in kq and "kéo bản mới" in kq  # «--locked-x» không được tính là có «--loc»
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", outcome="y", outcome_type="poisson_pr")
    assert loi and "F2 (Poisson vững)" in kq
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", outcome="y", group="g")  # đặc tả cũ vẫn chạy với bản cũ
    assert not loi and kq["chay_kho"] and _goi(yk) == []


def test_lam_sach_chay_kho_mac_dinh_lay_ban_tiep_nhan_va_tu_dien_g5(yk):
    loi, kq = _cc("lam_sach", study="DE-TAI")
    assert loi and "chưa có bản sao sau cổng tiếp nhận" in kq
    _tiep_nhan_gia(yk)
    loi, kq = _cc("lam_sach", study="DE-TAI", cot_ma_nc="ma")
    d = yk / "exports" / "DE-TAI"
    assert not loi and kq["chay_kho"] and kq["data"] == str((d / "02_raw_readonly" / "data.ab12.csv").resolve())
    ds = kq["se_chay"]
    assert ds[ds.index("--dictionary") + 1] == str(d / "G5_REDCap_dictionary_DE-TAI.csv") and "--id-column" in ds
    assert _goi(yk) == []  # chạy khô: không gọi bộ làm sạch


def test_lam_sach_chi_nhan_tep_trong_thu_muc_de_tai(yk, tmp_path):
    ngoai = tmp_path / "tho.csv"
    ngoai.write_text("ten\nNguyen\n", encoding="utf-8")
    for xau in (str(ngoai), "../../tho.csv", "02_raw_readonly/../../../tho.csv"):
        loi, kq = _cc("lam_sach", study="DE-TAI", data=xau)
        assert loi and "chỉ nhận tệp trong exports/DE-TAI/" in kq, xau
    _tiep_nhan_gia(yk)
    loi, kq = _cc("lam_sach", study="DE-TAI", giai_quyet_query=str(ngoai))
    assert loi and "giai_quyet_query" in kq
    assert _goi(yk) == []


def test_lam_sach_ap_dung_tra_query_mo_va_buoc_tiep_khong_khoa(yk):
    _tiep_nhan_gia(yk)
    (yk / "SO_QUERY").write_text("3", encoding="utf-8")
    loi, kq = _cc("lam_sach", study="DE-TAI", ap_dung=True)
    assert not loi and kq["open_query_count"] == 3 and kq["ready_for_lock"] is False and "giai_quyet_query" in kq["buoc_tiep"]
    assert _goi(yk)[-1][0] == "clean_research_dataset.py"
    (yk / "SO_QUERY").write_text("0", encoding="utf-8")
    loi, kq = _cc("lam_sach", study="DE-TAI", ap_dung=True)
    assert kq["ready_for_lock"] is True and "máy chủ không khoá" in kq["buoc_tiep"]
    assert not [g for g in _goi(yk) if "lock" in g[0]]


def test_tiep_nhan_xong_tu_lam_sach_tat_duoc_va_khong_chay_khi_tiep_nhan_loi(yk, tmp_path):
    xl = tmp_path / "ngoai" / "lan1.xlsx"
    xl.parent.mkdir()
    xl.write_bytes(b"gia")
    loi, kq = _cc("nhap_lieu_tiep_nhan", study="DE-TAI", tep=str(xl))
    assert kq["chay_kho"] and kq["se_lam_sach_sau"] is True and not [g for g in _goi(yk) if g[0] == "clean_research_dataset.py"]
    loi, kq = _cc("nhap_lieu_tiep_nhan", study="DE-TAI", tep=str(xl), ap_dung=True)
    assert kq["ma_thoat"] == 0 and kq["lam_sach"]["status"] == "CLEAN_READY"
    assert [g[0] for g in _goi(yk)][-2:] == ["nhap_lieu_excel.py", "clean_research_dataset.py"]
    n = len(_goi(yk))
    _cc("nhap_lieu_tiep_nhan", study="DE-TAI", tep=str(xl), ap_dung=True, lam_sach=False)
    assert [g[0] for g in _goi(yk)[n:]] == ["nhap_lieu_excel.py"]
    (yk / "TIEP_NHAN_LOI").write_text("", encoding="utf-8")
    n = len(_goi(yk))
    loi, kq = _cc("nhap_lieu_tiep_nhan", study="DE-TAI", tep=str(xl), ap_dung=True)
    assert kq["ma_thoat"] == 3 and "lam_sach" not in kq and [g[0] for g in _goi(yk)[n:]] == ["nhap_lieu_excel.py"]


def test_g5_con_thieu_cham_bang_ham_cong_khong_ghi(yk):
    loi, kq = _cc("g5_con_thieu", study="DE-TAI")
    assert not loi and kq["trang_thai"] == "BLOCKED" and kq["so_tieu_chi"] == 2
    assert [x["id"] for x in kq["chua_dat"]] == ["G5-04"] and kq["viec_can_lam"] == ["đóng 3 query"]
    assert _goi(yk)[-1] == ["g5_quality_gate.evaluate_study", "DE-TAI", str(Path("exports") / "DE-TAI"), "write=False"]
    assert not (yk / "exports" / "DE-TAI" / "G5_quality_report.json").exists()
    (yk / "G5_HONG").write_text("", encoding="utf-8")
    loi, kq = _cc("g5_con_thieu", study="DE-TAI")
    assert not loi and kq["trang_thai"] is None and kq["khong_do_duoc"] and "≠ đạt" in kq["ghi_chu"]


def test_bien_phai_sinh_kiem_chi_doc_tinh_doi_chieu_chay_kho(yk, tmp_path):
    loi, kq = _cc("bien_phai_sinh", study="DE-TAI")
    assert kq["ket_qua"]["dem"] == {"DA_DUYET": 2, "CHUA_DUYET": 1} and _goi(yk)[-1][:2] == ["bien_phai_sinh.py", "kiem"]
    assert len(kq["ket_qua"]["bien"]) == 60 and "dau_ra" not in kq  # đọc trọn JSON; không trả thêm bản thô
    csv = tmp_path / "ngoai" / "khoa.csv"
    csv.parent.mkdir()
    csv.write_text("a\n1\n", encoding="utf-8")
    n = len(_goi(yk))
    loi, kq = _cc("bien_phai_sinh", study="DE-TAI", lenh="tinh", data=str(csv), chi=["hop_le", "hl_nhi"])
    assert kq["chay_kho"] and kq["se_chay"][kq["se_chay"].index("--chi") + 1] == "hop_le,hl_nhi" and len(_goi(yk)) == n
    loi, kq = _cc("bien_phai_sinh", study="DE-TAI", lenh="tinh", data=str(csv), ra=str(yk / "exports" / "ra"))
    assert loi and "NGOÀI repo" in kq
    loi, kq = _cc("bien_phai_sinh", study="DE-TAI", lenh="tinh", data=str(csv), chi=["-x"])
    assert loi and "không hợp lệ" in kq
    _cc("bien_phai_sinh", study="DE-TAI", lenh="doi_chieu", data=str(csv), khong_r=True, ap_dung=True)
    assert _goi(yk)[-1] == ["bien_phai_sinh.py", "doi-chieu", "--study", "DE-TAI", "--data", str(csv.resolve()), "--khong-r"]


def test_chay_sap_chi_tren_du_lieu_khoa_kiem_cheo_mac_dinh(yk):
    loi, kq = _cc("chay_sap_g6", study="DE-TAI")
    assert kq["ket_qua"]["lenh"] == "kiem" and _goi(yk)[-1][:2] == ["chay_sap_g6.py", "kiem"]
    loi, kq = _cc("chay_sap_g6", study="DE-TAI", lenh="chay", ap_dung=True)
    assert kq["tu_choi"] is True and not [g for g in _goi(yk) if g[:2] == ["chay_sap_g6.py", "chay"]]
    (yk / "exports" / "DE-TAI" / "KHOA").write_text("", encoding="utf-8")
    loi, kq = _cc("chay_sap_g6", study="DE-TAI", lenh="chay", chi=["MT2_chinh"])
    assert kq["chay_kho"] and kq["se_chay"][-1] == "--kiem-cheo" and kq["dac_ta"]["duyet"] == "DA_DUYET"
    assert not [g for g in _goi(yk) if g[:2] == ["chay_sap_g6.py", "chay"]]
    loi, kq = _cc("chay_sap_g6", study="DE-TAI", lenh="chay", chi=["MT2_chinh"], ap_dung=True)
    assert [g for g in _goi(yk) if g[:2] == ["chay_sap_g6.py", "chay"]][-1] == [
        "chay_sap_g6.py", "chay", "--study", "DE-TAI", "--chi", "MT2_chinh", "--kiem-cheo"]
    assert kq["ket_qua"]["lenh"] == "ket-qua"
    _cc("chay_sap_g6", study="DE-TAI", lenh="chay", kiem_cheo=False, ap_dung=True)
    assert "--kiem-cheo" not in _goi(yk)[-2] and not [x for g in _goi(yk) for x in g if str(x).startswith("--i-confirm")]


def test_doi_chieu_bien_chi_doc_tach_lech_nhap_lieu_va_phan_tich(yk):
    sc = {t["name"]: t["inputSchema"] for t in M.xu_ly({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})["result"]["tools"]}
    assert "doi_chieu_bien" in sc and "ap_dung" not in sc["doi_chieu_bien"]["properties"]
    loi, kq = _cc("doi_chieu_bien", study="DE-TAI")
    assert not loi and kq["trang_thai"] == "LECH" and kq["ma_thoat"] == 1  # có lệch là KẾT QUẢ, không phải lỗi công cụ
    assert [x["bien"] for x in kq["lech_nhap_lieu"]] == ["GioiTinh"] and [x["bien"] for x in kq["lech_phan_tich"]] == ["NhomTuoi"]
    assert [x["bien"] for x in kq["can_xem"]] == ["x"] and "KHÔNG tự thêm biến" in kq["ghi_chu"]
    assert _goi(yk)[-1] == ["doi_chieu_bien_de_cuong.py", "--study", "DE-TAI", "--json"]
    (yk / "DC_HONG").write_text("", encoding="utf-8")
    loi, kq = _cc("doi_chieu_bien", study="DE-TAI")
    assert not loi and kq["trang_thai"] is None and "không đo được ≠ đồng bộ" in kq["ghi_chu"]
