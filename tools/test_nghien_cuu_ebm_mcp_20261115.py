"""Máy chủ MCP «nghien-cuu-ebm» (tools/mcp/nghien_cuu_ebm_mcp.py) — 15/11/2026: một cửa CHỈ ĐỌC vào hệ nghiên cứu G0–G10.

CI của repo gốc không có repo y khoa ⇒ test dựng một repo gốc GIẢ và một repo y khoa GIẢ (thư mục tạm) với công cụ giả
cùng tên, ghi lại từng lời gọi (argv) vào `goi.jsonl`. Chạy tiến trình con thật (Python đang chạy test). Không PII, không
đụng exports/ của đề tài thật. Đột biến «thêm công cụ ghi» được giữ lại dưới dạng test (kiem_bat_bien phải đỏ).
"""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "mcp" / "nghien_cuu_ebm_mcp.py"
_sp = importlib.util.spec_from_file_location("nghien_cuu_ebm_mcp_test", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

GHI = """import json, sys
from pathlib import Path
goc = Path(__file__).resolve().parents[1]
with open(goc / "goi.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps([Path(__file__).name, *sys.argv[1:]]) + "\\n")
a = sys.argv[1:]
"""
Y_KHOA = {
    "list_studies.py": GHI + """print(json.dumps([
    {"study": "DE-TAI", "topic": "Đề tài giả", "furthest_gate": "G4", "recognized": True, "system": False,
     "milestones": {"irb_approved": False}, "last_modified": "2026-11-15 03:00"},
    {"study": "chatgpt_project", "recognized": False, "system": True},
    {"study": "rong", "recognized": False, "system": False}], ensure_ascii=False, indent=2))
""",
    "study_readiness.py": GHI + """import os
print('TÌNH TRẠNG THẬT CỦA ĐỀ TÀI — ' + a[1])
print('PYTHONDONTWRITEBYTECODE=' + str(os.environ.get('PYTHONDONTWRITEBYTECODE')))
print('Cần bác sĩ kiểm chứng.')
""",
    "kiem_chi_tiet_he_nghien_cuu.py": GHI + """for g in range(11):
    print('G%d' % g)
    for i in range(10):
        print('  🟢 ① mục đạt %d' % i)
    print('  🟡 ③ còn ô chưa điền')
    print('      chi tiết thụt sâu')
print('TỔNG: 🟢 110 · 🟡 11')
sys.exit(1)
""",
    "hoi_dong_cong.py": GHI + "print(json.dumps({'lenh': a[0], 'gate': a[a.index('--gate') + 1]}))\n",
    "nhat_quan_xuyen_cong.py": GHI + "print(json.dumps({'tong': {'lech_mem': 1}, 'trang_thai_g10': 'REVIEW'}))\nsys.exit(1)\n",
    "cong_song.py": """import json
from pathlib import Path
KHONG_DO_DUOC = "KHONG_DO_DUOC"
def trang_thai_song(gate, study, out_dir, repo_root=None):
    goc = Path(__file__).resolve().parents[1]
    with open(goc / "goi.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(["cong_song", gate, study, str(out_dir)]) + "\\n")
    dat = gate == "G0"
    return {"gate": gate, "status": "PASS_G0_CONFIRMED" if dat else "READY_FOR_SIGNATURE", "muc": "PASS" if dat else "READY",
            "dat": dat, "bi_chan": False, "nguon": "song", "ly_do": "chấm sống (write=False)", "trang_thai_luu": None,
            "bao_cao": {"rat_dai": "x" * 5000}}
""",
    "gate_contract.py": "_GATE_REQUIRED_STAKEHOLDERS = {g: () for g in ('G2', 'G4', 'G5', 'G8', 'G9', 'G10')}\n",
}
GOC = {
    "tra_diem_kham.py": """import json, sys
from pathlib import Path
GOC = Path(__file__).resolve().parents[1]
STATE = GOC / "state"
def _vet(*x):
    with open(GOC / "goi.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(["tra_diem_kham", *x], default=str) + "\\n")
def tra_chi_tiet(q, cards):
    if "copd" in q.lower():
        return [{"id": "THE-1", "decision": "apply", "topic": "COPD đợt cấp: bộ ba", "gradeLevel": "high",
                 "source": {"pmid": "29668352", "doi": "10.1056/x"}, "_xung_dot": False}], "khop"
    return [], "khong_co"
def _ghi_nhat_ky_tac_dong(ket, giay, loai="khong_co"):
    STATE.mkdir(exist_ok=True)
    with open(STATE / "nhat-ky-tac-dong.jsonl", "a", encoding="utf-8") as f:
        f.write("x\\n")
def in_quick_view(cau_hoi, ket, vq, giay, loai="khong_co", vq_info=None, ghi=True, tra_rut=None, rut_ghi_chu=None):
    _vet("ghi", ghi, "state", STATE)
    if ghi:
        _ghi_nhat_ky_tac_dong(ket, giay, loai)
    print("❓ " + cau_hoi)
    if not ket:
        print("  ⛔ CHỦ ĐỀ NÀY CHƯA ĐƯỢC GIÁM SÁT")
        if not ghi:
            print("     (chế độ --demo: không ghi sổ ứng viên watchlist)")
            return
        STATE.mkdir(exist_ok=True)
        with open(STATE / "cau-hoi-chua-giam-sat.jsonl", "a", encoding="utf-8") as f:
            f.write(cau_hoi + "\\n")
        return
    for c in ket:
        print("  ▶ [" + c["decision"].upper() + "] " + c["topic"])
def main():
    _vet("argv", sys.argv[1:])
    q = " ".join(sys.argv[1:])
    ket, loai = tra_chi_tiet(q, [])
    in_quick_view(q, ket, set(), 0.0, loai, None)
    return 0
""",
    "kiem_do_tuoi_chung_cu.py": GHI + "print('🟢 HỆ GIÁM SÁT còn hoạt động — gói mới nhất 14/11/2026')\n",
    "doc_ket_qua_rut_bai_kho.py": GHI + "print(json.dumps({'ma': 1, 'muc': '🔴'}))\nsys.exit(1)\n",
    "dang_ky_chu_de.py": GHI + """print('=' * 70)
for i in range(300):
    print('     • chi tiết cặp đã duyệt %d' % i)
print('  🔴 2 MỤC HAI BẢN NÓI NGƯỢC NHAU — cùng PMID, khác quyết định')
print('  ▸ DTD:  A (20261102)   ⟷   A (20261114)')
print('      PMID 1: consider → apply')
sys.exit(1)
""",
    "kiem_quyet_dinh_da_duyet.py": GHI + "print('KẾT: ✓ 3 còn nguyên · 🔴 0 tái phạm')\n",
}


@pytest.fixture()
def may(tmp_path, monkeypatch) -> dict:
    goc, yk = tmp_path / "goc", tmp_path / "y_khoa"
    for thu_muc, tep in ((goc, GOC), (yk, Y_KHOA)):
        (thu_muc / "tools").mkdir(parents=True)
        for ten, ma in tep.items():
            (thu_muc / "tools" / ten).write_text(ma, encoding="utf-8")
    d = yk / "exports" / "DE-TAI"
    d.mkdir(parents=True)
    (d / "study_meta.json").write_text("{}", encoding="utf-8")
    (d / "G0_checkpoint.json").write_text("{}", encoding="utf-8")
    (d / "G4_A5_SAP_FINAL_DE-TAI.md").write_text("SAP giả\n", encoding="utf-8")
    (goc / "cloud-mirror").mkdir()
    (goc / "cloud-mirror" / "trang-thai-chung-cu.json").write_text(json.dumps(
        {"sinh_luc": "2026-11-14T08:20:46", "may": "Mac",
         "bo_dem": {"do_tuoi_chung_cu": {"stdout": "🟢 ảnh chụp độ tươi"}}}), encoding="utf-8")  # fmt: skip
    monkeypatch.setenv("EBM_GOC_ROOT", str(goc))
    monkeypatch.setenv("EBM_MEDICAL_ROOT", str(yk))
    monkeypatch.setenv("EBM_VENV_PYTHON", sys.executable)
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)  # máy chủ phải TỰ đặt cho tiến trình con
    return {"goc": goc, "yk": yk}


def _goi(thu_muc: Path) -> list[list]:
    p = thu_muc / "goi.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def _cc(ten: str, **arg) -> tuple[bool, dict | str]:
    r = M.xu_ly({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": ten, "arguments": arg}})["result"]
    txt = r["content"][0]["text"]
    try:
        return r["isError"], json.loads(txt)
    except ValueError:
        return r["isError"], txt


CONG_CU_MONG_DOI = {"danh_sach_de_tai", "trang_thai_cong", "san_sang", "kiem_chi_tiet", "hoi_dong", "nhat_quan",
                    "tra_diem_kham", "trang_thai_chung_cu"}


# ─────────────── CHỈ ĐỌC: không có công cụ ghi + đột biến ───────────────

def test_giao_thuc_va_khong_co_cong_cu_ghi():
    kq = M.xu_ly({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
    assert kq["result"]["serverInfo"]["name"] == "nghien-cuu-ebm" and "CHỈ ĐỌC" in kq["result"]["instructions"]
    ds = M.xu_ly({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
    ten = {t["name"] for t in ds}
    assert ten == CONG_CU_MONG_DOI
    assert not [t for t in ten if set(t.split("_")) & {"ky", "ghi", "sua", "xoa", "khoa", "chay", "ap", "duyet"}
                or any(w in t for w in ("approve", "sign", "lock", "write", "delete", "ledger"))]
    assert not [p for t in ds for p in t["inputSchema"]["properties"] if p in ("ap_dung", "ghi", "force", "tep", "ra")]
    assert all(len(t["description"]) <= 120 for t in ds)  # mô tả NGẮN — token thường trực
    for x in ("approve_gate", "ky_cong", "ghi_so_cai", "khoa_du_lieu"):
        loi, txt = _cc(x, study="DE-TAI")
        assert loi and "không có công cụ" in txt and "CHỈ ĐỌC" in txt
    assert M.xu_ly({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    M.kiem_bat_bien()  # bản sống đạt bất biến


def test_bat_bien_chay_luc_nap(tmp_path):
    """Thêm công cụ ghi vào CHÍNH mã nguồn ⇒ nạp mô-đun phải hỏng (máy chủ không khởi động) — không chỉ khi test gọi."""
    src = _TEP.read_text(encoding="utf-8")
    moc = "_BANG = {ten: ham for ten"
    assert src.count(moc) == 1
    tep = tmp_path / "mcp" / "nghien_cuu_ebm_mcp.py"
    tep.parent.mkdir()
    tep.write_text(src.replace(moc, 'CONG_CU.append(("ky_cong", "giả", _sc({}), lambda a: {}))\n' + moc), encoding="utf-8")
    sp = importlib.util.spec_from_file_location("nghien_cuu_dot_bien", tep)
    with pytest.raises(RuntimeError, match="ky_cong"):
        sp.loader.exec_module(importlib.util.module_from_spec(sp))


def _cong_cu_gia(ten: str, props: dict | None = None):
    return (ten, "giả", M._sc(props or {}), lambda a: {})


@pytest.mark.parametrize("cong_cu, cum", [
    ([*M.CONG_CU, _cong_cu_gia("ky_cong")], "ky_cong"),
    ([*M.CONG_CU, _cong_cu_gia("approve_gate_g4")], "approve_gate_g4"),
    ([*M.CONG_CU, _cong_cu_gia("ghi_so_cai")], "ghi_so_cai"),
    ([*M.CONG_CU, _cong_cu_gia("khoa_du_lieu_g5")], "khoa_du_lieu_g5"),
    ([*M.CONG_CU, _cong_cu_gia("chay_du_thao_cong")], "chay_du_thao_cong"),
    ([*M.CONG_CU[:-1], _cong_cu_gia("trang_thai_chung_cu", {"ap_dung": {"type": "boolean"}})], "ap_dung"),
])  # fmt: skip
def test_dot_bien_them_cong_cu_ghi_lam_bat_bien_do(cong_cu, cum):
    with pytest.raises(RuntimeError, match=cum):
        M.kiem_bat_bien(cong_cu=cong_cu)


@pytest.mark.parametrize("sua, cum", [
    (lambda L: L.update({("y_khoa", "approve_gate.py"): {"co": {"--study": True}}}), "approve_gate"),
    (lambda L: L.update({("y_khoa", "run_g4_auto.py"): {"co": {"--study": True}}}), "run_g4_auto"),
    (lambda L: L.update({("y_khoa", "mark_study_synthetic.py"): {"co": {}}}), "mark_study"),
    (lambda L: L[("y_khoa", "list_studies.py")]["co"].update({"--ghi": False}), "--ghi"),
    (lambda L: L[("y_khoa", "hoi_dong_cong.py")].update({"lenh_con": ("uoc-tinh", "ghi-quyet-dinh")}), "ghi-quyet-dinh"),
    (lambda L: L[("y_khoa", "kiem_chi_tiet_he_nghien_cuu.py")].update({"bat_buoc": ()}), "--no-write"),
])  # fmt: skip
def test_dot_bien_danh_sach_lenh_ghi_lam_bat_bien_do(sua, cum):
    lenh = json.loads(json.dumps({"|".join(k): v for k, v in M._LENH_CHI_DOC.items()}))  # bản sao sâu
    lenh = {tuple(k.split("|")): v for k, v in lenh.items()}
    sua(lenh)
    with pytest.raises(RuntimeError, match=cum):
        M.kiem_bat_bien(lenh=lenh)


@pytest.mark.parametrize("them", ["p.write_text('x')", "open('a', 'w')", "k['ghi'] = True\nx(ghi=True)", "write=True"])
def test_dot_bien_ma_noi_tuyen_co_thao_tac_ghi(them):
    ma = {k: (g, m + "\n" + them) if k == "tra_diem_kham" else (g, m) for k, (g, m) in M._MA_CHI_DOC.items()}
    with pytest.raises(RuntimeError, match="mã nội tuyến tra_diem_kham"):
        M.kiem_bat_bien(ma=ma)


def test_lop_chan_cuoi_cua_tien_trinh_con(may):
    for goc, tep, ds, cum in (
        ("y_khoa", "approve_gate.py", ["--study", "DE-TAI"], "không nằm trong danh sách"),
        ("y_khoa", "kiem_chi_tiet_he_nghien_cuu.py", ["--study", "DE-TAI"], "thiếu cờ bắt buộc --no-write"),
        ("y_khoa", "hoi_dong_cong.py", ["ghi", "--study", "DE-TAI", "--gate", "G4"], "lệnh con"),
        ("y_khoa", "hoi_dong_cong.py", ["trach-nhiem", "--study", "DE-TAI", "--gate", "G4"], "lệnh con"),
        ("y_khoa", "list_studies.py", ["--json", "--ghi"], "cờ '--ghi'"),
        ("y_khoa", "study_readiness.py", ["--study", "-x"], "thiếu giá trị hợp lệ"),
        ("y_khoa", "study_readiness.py", ["--study"], "thiếu giá trị hợp lệ"),
        ("goc", "xuat_trang_thai_cloud.py", [], "không nằm trong danh sách"),
    ):
        with pytest.raises(RuntimeError, match="cấm"):
            M.chay_cong_cu(goc, tep, ds)
        with pytest.raises(RuntimeError, match=cum):
            M.chay_cong_cu(goc, tep, ds)
    with pytest.raises(RuntimeError, match="cấm"):
        M.chay_ma("ghi_gi_do", [])
    with pytest.raises(RuntimeError, match="cấm"):
        M.chay_ma("trang_thai_cong", ["../x"])
    assert _goi(may["yk"]) == [] and _goi(may["goc"]) == []


# ─────────────── từng công cụ trên dữ liệu giả ───────────────

def test_danh_sach_de_tai_loc_thu_muc_he_thong(may):
    loi, kq = _cc("danh_sach_de_tai")
    assert not loi and kq["so_de_tai"] == 1 and kq["an_di"] == 2 and kq["de_tai"][0]["study"] == "DE-TAI"
    assert kq["de_tai"][0]["cong_xa_nhat_da_chay"] == "G4" and kq["luu_y"] == "Cần bác sĩ kiểm chứng."
    loi, kq = _cc("danh_sach_de_tai", tat_ca=True)
    assert kq["so_de_tai"] == 3
    assert _goi(may["yk"])[-1] == ["list_studies.py", "--json"]


def test_trang_thai_cong_cham_song_va_chua_chay(may):
    loi, kq = _cc("trang_thai_cong", study="DE-TAI")
    assert not loi, kq
    cong = {c["gate"]: c for c in kq["cong"]}
    assert list(cong) == [f"G{i}" for i in range(11)]
    assert cong["G0"]["muc"] == "PASS" and cong["G0"]["dat"] is True and cong["G0"]["cong_cung"] is False
    assert cong["G4"]["muc"] == "READY" and cong["G4"]["dat"] is False and cong["G4"]["cong_cung"] is True
    assert cong["G1"]["muc"] == "CHUA_CHAY" and "dat" not in cong["G1"]
    assert all("bao_cao" not in c for c in kq["cong"])  # báo cáo thô của bộ chấm không đổ vào ngữ cảnh
    da_cham = [g[1] for g in _goi(may["yk"]) if g[0] == "cong_song"]
    assert da_cham == ["G0", "G4"]  # chỉ chấm cổng có checkpoint/artifact


def test_san_sang_va_kiem_chi_tiet_luon_no_write(may):
    loi, kq = _cc("san_sang", study="DE-TAI")
    assert not loi and "TÌNH TRẠNG THẬT CỦA ĐỀ TÀI — DE-TAI" in kq["dau_ra"]
    assert _goi(may["yk"])[-1] == ["study_readiness.py", "--study", "DE-TAI"]
    assert "PYTHONDONTWRITEBYTECODE=1" in kq["dau_ra"]  # tiến trình con không ghi __pycache__ vào repo
    loi, kq = _cc("kiem_chi_tiet", study="DE-TAI")
    assert not loi and kq["ma_thoat"] == 1 and "người thật" in kq["y_nghia"]
    assert _goi(may["yk"])[-1] == ["kiem_chi_tiet_he_nghien_cuu.py", "--study", "DE-TAI", "--no-write", "--khong-canary"]
    assert "rut_gon" in kq and "🟢 ① mục đạt" not in kq["dau_ra"] and "chi tiết thụt sâu" not in kq["dau_ra"]
    assert kq["dau_ra"].count("🟡 ③") == 11 and "TỔNG:" in kq["dau_ra"]
    loi, kq = _cc("kiem_chi_tiet", study="DE-TAI", day_du=True)
    assert "rut_gon" not in kq and kq["dau_ra"].count("🟢 ① mục đạt") == 110


def test_hoi_dong_uoc_tinh_va_ho_so(may):
    loi, kq = _cc("hoi_dong", study="DE-TAI")
    assert not loi and kq["gate"] == "ALL" and kq["ket_qua"] == {"lenh": "uoc-tinh", "gate": "ALL"}
    assert _goi(may["yk"])[-1] == ["hoi_dong_cong.py", "uoc-tinh", "--study", "DE-TAI", "--gate", "ALL", "--json"]
    loi, kq = _cc("hoi_dong", study="DE-TAI", che_do="ho_so", gate="g4")
    assert kq["ket_qua"] == {"lenh": "ho-so", "gate": "G4"} and "KHÔNG triệu tập" in kq["ghi_chu"]
    n = len(_goi(may["yk"]))
    for arg in ({"che_do": "ho_so"}, {"che_do": "ho_so", "gate": "ALL"}, {"gate": "G11"}, {"che_do": "ghi"}):
        loi, txt = _cc("hoi_dong", study="DE-TAI", **arg)
        assert loi, arg
    assert len(_goi(may["yk"])) == n


def test_nhat_quan_doc_ma_thoat(may):
    loi, kq = _cc("nhat_quan", study="DE-TAI")
    assert not loi and kq["ma_thoat"] == 1 and kq["y_nghia"].startswith("REVIEW")
    assert kq["ket_qua"]["trang_thai_g10"] == "REVIEW"
    assert _goi(may["yk"])[-1] == ["nhat_quan_xuyen_cong.py", "--study", "DE-TAI", "--json"]


def test_tra_diem_kham_khong_ghi_nhat_ky(may):
    loi, kq = _cc("tra_diem_kham", cau_hoi="COPD  đợt cấp bộ ba")
    assert not loi and kq["chua_giam_sat"] is False and kq["the"][0]["id"] == "THE-1"
    assert kq["the"][0]["pmid"] == "29668352" and "[APPLY]" in kq["van_ban"]
    loi, kq = _cc("tra_diem_kham", cau_hoi="viêm tuyến mồ hôi mủ")
    assert kq["chua_giam_sat"] is True and kq["the"] == [] and "CHƯA ĐƯỢC GIÁM SÁT" in kq["van_ban"]
    assert "MCP chỉ đọc" in kq["van_ban"] and "--demo" not in kq["van_ban"] and "trí nhớ" in kq["luat"]
    assert not (may["goc"] / "state").exists()  # không nhật ký tác động, không sổ ứng viên watchlist
    vet = [g for g in _goi(may["goc"]) if g[0] == "tra_diem_kham"]
    assert [g[2] for g in vet if g[1] == "ghi"] == [False, False]  # lớp 1: ép ghi=False
    assert all(not str(g[4]).startswith(str(may["goc"])) for g in vet if g[1] == "ghi")  # lớp 2: STATE trỏ ra ngoài
    assert [g[2] for g in vet if g[1] == "argv"] == [["COPD đợt cấp bộ ba"], ["viêm tuyến mồ hôi mủ"]]
    for xau in ("", "--demo", "-x", "a" * 501):
        loi, txt = _cc("tra_diem_kham", cau_hoi=xau)
        assert loi and "cau_hoi" in txt, xau


def test_trang_thai_chung_cu_ngoai_tuyen(may):
    loi, kq = _cc("trang_thai_chung_cu")
    assert not loi, kq
    assert kq["do_tuoi"]["ma_thoat"] == 0 and "HỆ GIÁM SÁT" in kq["do_tuoi"]["dau_ra"]
    assert kq["rut_bai_kho"]["ma_thoat"] == 1 and kq["rut_bai_kho"]["ket_qua"]["muc"] == "🔴"
    mt = kq["mau_thuan_giua_ban"]
    assert mt["ma_thoat"] == 1 and "2 MỤC HAI BẢN NÓI NGƯỢC NHAU" in mt["dau_ra"] and "▸ DTD" in mt["dau_ra"]
    assert "rut_gon" in mt and "chi tiết cặp đã duyệt" not in mt["dau_ra"]
    assert kq["quyet_dinh_da_duyet"]["ma_thoat"] == 0
    assert kq["co_du_lieu_dashboard_that"] is False and "ẢNH CHỤP" in kq["anh_chup_cloud_mirror"]["canh_bao"]
    assert kq["anh_chup_cloud_mirror"]["do_tuoi"] == "🟢 ảnh chụp độ tươi"
    goi = [g for g in _goi(may["goc"])]
    assert goi == [["kiem_do_tuoi_chung_cu.py"], ["doc_ket_qua_rut_bai_kho.py", "--json"],
                   ["dang_ky_chu_de.py", "--mau-thuan"], ["kiem_quyet_dinh_da_duyet.py"]]
    (may["goc"] / "EBM-Dashboards").mkdir()
    (may["goc"] / "tools" / "kiem_quyet_dinh_da_duyet.py").unlink()  # một bộ đếm vắng ⇒ ⚪, các bộ khác vẫn đo
    loi, kq = _cc("trang_thai_chung_cu")
    assert not loi and "anh_chup_cloud_mirror" not in kq and kq["co_du_lieu_dashboard_that"] is True
    assert kq["quyet_dinh_da_duyet"]["ma_thoat"] is None and "không đo được" in kq["quyet_dinh_da_duyet"]["y_nghia"]


def test_kiem_tham_so_dau_vao(may):
    for xau in ("../x", "..", ".an", "a/b", "", "-x", "DE-TAI\n--ghi", "DE TAI"):
        loi, txt = _cc("san_sang", study=xau)
        assert loi and "mã đề tài không hợp lệ" in txt, xau
    loi, txt = _cc("trang_thai_cong", study="KHONG-CO")
    assert loi and "không có thư mục đề tài" in txt
    assert _goi(may["yk"]) == []


def test_thieu_repo_y_khoa_bao_ro(may, monkeypatch, tmp_path):
    monkeypatch.setenv("EBM_MEDICAL_ROOT", str(tmp_path / "vang"))
    loi, txt = _cc("danh_sach_de_tai")
    assert loi and "không thấy" in txt


def test_kenh_giao_thuc_chi_co_json(may):
    vao = io.StringIO(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "san_sang", "arguments": {"study": "DE-TAI"}}}) + "\n{hỏng\n")  # fmt: skip
    ra = io.StringIO()
    M.chay(vao, ra)
    dong = ra.getvalue().splitlines()
    assert len(dong) == 2 and all(json.loads(x)["jsonrpc"] == "2.0" for x in dong)


def test_mcp_json_khoi_chay_tu_thu_muc_long():
    """Chạy ĐÚNG đoạn mã `-c` khai cho nghien-cuu-ebm trong `.mcp.json` (bằng trình thông dịch đang chạy thay cho `uv run`)
    từ một thư mục lồng của repo — phải tìm thấy máy chủ cạnh `.mcp.json` và trả lời initialize qua stdio."""
    goc = _TEP.parents[2]
    khai = json.loads((goc / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    muc = khai["nghien-cuu-ebm"]
    assert muc["command"] == "uv" and muc["args"][:5] == ["run", "--no-project", "python", "-c", muc["args"][-1]]
    assert "tools/mcp/nghien_cuu_ebm_mcp.py" in muc["args"][-1] and {"endnote-ebm", "spss-r-ebm", "pubmed-search"} <= set(khai)
    tin = json.dumps({"jsonrpc": "2.0", "id": 7, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
    k = subprocess.run([sys.executable, "-c", muc["args"][-1]], cwd=goc / "tools" / "mcp", input=tin + "\n",
                       capture_output=True, text=True, encoding="utf-8", timeout=60, check=False)  # fmt: skip
    assert k.returncode == 0, k.stderr
    tl = json.loads(k.stdout.strip().splitlines()[-1])
    assert tl["id"] == 7 and tl["result"]["serverInfo"]["name"] == "nghien-cuu-ebm"


def test_cai_claude_desktop_chay_kho_sao_luu_giu_khoa_khac(tmp_path):
    tep = tmp_path / "claude_desktop_config.json"
    tep.write_text(json.dumps({"mcpServers": {"endnote-ebm": {"command": "x"}}, "khac": 1}), encoding="utf-8")
    kq = M.cai_claude_desktop(False, tep)
    assert not kq.get("da_ghi") and "nghien-cuu-ebm" not in json.loads(tep.read_text(encoding="utf-8"))["mcpServers"]
    kq = M.cai_claude_desktop(True, tep)
    moi = json.loads(tep.read_text(encoding="utf-8"))
    assert kq["da_ghi"] and Path(kq["sao_luu"]).exists() and moi["khac"] == 1
    assert set(moi["mcpServers"]) == {"endnote-ebm", "nghien-cuu-ebm"}
    assert M.cai_claude_desktop(True, tep)["khong_doi"] is True
