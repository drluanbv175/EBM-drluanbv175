"""Máy chủ MCP «spss-r-ebm» (tools/mcp/spss_r_ebm_mcp.py) — 14/11/2026: nhập liệu + phân tích SPSS/R tự động như endnote-ebm.

CI của repo gốc không có repo y khoa ⇒ test dựng một repo y khoa GIẢ (thư mục tạm) với các công cụ giả cùng tên, ghi lại
từng lời gọi (argv) và sinh đúng tệp báo cáo mà máy chủ đọc. Chạy tiến trình con thật (Python đang chạy test). Không PII.
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "mcp" / "spss_r_ebm_mcp.py"
_sp = importlib.util.spec_from_file_location("spss_r_ebm_mcp_test", _TEP)
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
if a[0] == "nhap":
    ra = Path(lay("--ra")); ra.mkdir(parents=True, exist_ok=True)
    ten = Path(lay("--excel")).stem
    (ra / (ten + "_bao_cao_nhap.json")).write_text(json.dumps({"trang_thai": "SACH", "so_loi": 0, "so_truy_van": 0,
        "so_canh_bao": 0, "so_ma_nghien_cuu": 2, "phat_hien": []}), encoding="utf-8")
    print("noi dung ra man hinh cua cong cu")
elif a[0] == "so-sanh":
    ra = Path(lay("--ra")); ra.mkdir(parents=True, exist_ok=True)
    (ra / "NHAP_KEP_tom_tat.json").write_text(json.dumps({"so_o_lech": 2, "trang_thai": "CO_LECH"}), encoding="utf-8")
    (ra / "NHAP_KEP_chi_tiet.csv").write_text("ma_nc,cot,o_lan1,o_lan2,gia_tri_lan1,gia_tri_lan2,kieu\\n"
        "P01,tuoi,phieu!C4,phieu!C4,45,54,so_nguyen\\nP02,ghi_chu,phieu!K5,phieu!K5,Ong A,Ong B,chu\\n", encoding="utf-8")
    sys.exit(1)
""",
    "mo_trong_phan_mem.py": GHI + "print('✓ Sẵn sàng')\n",
    "kiem_cheo_g6.py": GHI + "print(json.dumps({'trang_thai': 'KHOP'}) if a[0] == 'trang-thai' else 'chay xong')\n",
    "run_stats_analysis.py": GHI + "print('phan tich xong')\n",
    "cau_noi_spss.py": """from pathlib import Path
GOC = Path(__file__).resolve().parents[1]
def tim_spss():
    return "/gia/spss/python3"
def tim_du_lieu_khoa(study):
    p = GOC / "exports" / study / "KHOA"
    if not p.exists():
        raise RuntimeError("chua khoa")
    return GOC / "exports" / study / "khoa.csv", {"lock_date": "2026-11-14", "sap_version": "v1"}
""",
    "cau_noi_r.py": "def tim_r():\n    raise RuntimeError('khong co R')\n",
}


@pytest.fixture()
def y_khoa(tmp_path, monkeypatch) -> Path:
    yk = tmp_path / "y_khoa"
    (yk / "tools").mkdir(parents=True)
    for ten, ma in GIA.items():
        (yk / "tools" / ten).write_text(ma, encoding="utf-8")
    d = yk / "exports" / "DE-TAI"
    d.mkdir(parents=True)
    (d / "study_meta.json").write_text("{}", encoding="utf-8")
    (d / "G5_REDCap_dictionary_DE-TAI.csv").write_text("x\n", encoding="utf-8")
    monkeypatch.setenv("EBM_MEDICAL_ROOT", str(yk))
    monkeypatch.setenv("EBM_VENV_PYTHON", sys.executable)
    return yk


def _goi(yk: Path) -> list[list[str]]:
    p = yk / "goi.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def _cc(ten: str, **arg) -> tuple[bool, dict | str]:
    r = M.xu_ly({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": ten, "arguments": arg}})["result"]
    txt = r["content"][0]["text"]
    try:
        return r["isError"], json.loads(txt)
    except ValueError:
        return r["isError"], txt


def _tep(tmp_path: Path, ten: str) -> str:
    p = tmp_path / "ngoai" / ten
    p.parent.mkdir(exist_ok=True)
    p.write_bytes(b"gia")
    return str(p)


def test_giao_thuc_va_khong_co_cong_cu_khoa_ky_xoa():
    kq = M.xu_ly({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
    assert kq["result"]["serverInfo"]["name"] == "spss-r-ebm" and "KHÔNG" in kq["result"]["instructions"]
    ten = [t["name"] for t in M.xu_ly({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]]
    assert {"nhap_lieu_kiem", "nhap_lieu_so_sanh", "spss_r_xuat", "phan_tich_g6", "phan_tich_ket_qua"} <= set(ten)
    assert not [t for t in ten if any(x in t for x in ("khoa", "ky_", "xoa", "lock", "approve", "delete"))]
    loi, txt = _cc("khoa_du_lieu", study="X")
    assert loi and "không có công cụ" in txt
    assert M.xu_ly({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_trang_thai_doc_phan_mem_va_de_tai(y_khoa):
    loi, kq = _cc("spss_r_trang_thai")
    assert not loi and kq["spss"] == "/gia/spss/python3" and kq["rscript"] is None and "khong co R" in kq["r_ly_do"]
    assert [d["study"] for d in kq["de_tai"]] == ["DE-TAI"] and kq["de_tai"][0]["tu_dien_g5"] is True


def test_cong_cu_co_tac_dung_chay_kho_mac_dinh(y_khoa, tmp_path):
    xl = _tep(tmp_path, "lan1.xlsx")
    for ten, arg in (("nhap_lieu_mau", {"study": "DE-TAI"}), ("spss_r_xuat", {"study": "DE-TAI", "phan_mem": "spss", "tep": xl})):
        loi, kq = _cc(ten, **arg)
        assert not loi and kq["chay_kho"] is True
    assert _goi(y_khoa) == []  # chạy khô: KHÔNG gọi công cụ nào
    loi, kq = _cc("nhap_lieu_tiep_nhan", study="DE-TAI", tep=xl)
    assert kq["chay_kho"] and kq["se_tiep_nhan"] is True
    assert all("--tiep-nhan" not in g for g in _goi(y_khoa))  # chạy khô chỉ KIỂM
    _cc("nhap_lieu_tiep_nhan", study="DE-TAI", tep=xl, ap_dung=True)
    assert "--tiep-nhan" in _goi(y_khoa)[-1]
    _cc("spss_r_xuat", study="DE-TAI", phan_mem="r", tep=xl, mo=False, ap_dung=True)
    assert _goi(y_khoa)[-1] == ["mo_trong_phan_mem.py", "r", "--study", "DE-TAI", "--excel", xl, "--khong-mo"]


def test_kiem_va_so_sanh_che_gia_tri_chu(y_khoa, tmp_path):
    xl = _tep(tmp_path, "lan1.xlsx")
    loi, kq = _cc("nhap_lieu_kiem", study="DE-TAI", tep=xl)
    assert not loi and kq["trang_thai"] == "SACH" and kq["ma_thoat"] == 0
    assert kq["dau_ra"] == "noi dung ra man hinh cua cong cu"  # đầu ra công cụ được BẮT, không lẫn vào kênh giao thức
    loi, kq = _cc("nhap_lieu_so_sanh", study="DE-TAI", tep1=xl, tep2=_tep(tmp_path, "lan2.xlsx"))
    assert kq["tom_tat"]["so_o_lech"] == 2
    assert [(x["cot"], x["gia_tri_lan1"]) for x in kq["o_lech"]] == [("tuoi", "45"), ("ghi_chu", "«chữ»")]


def test_kiem_tham_so_dau_vao(y_khoa, tmp_path):
    for xau in ("../x", "..", ".an", "a/b", ""):
        assert "mã đề tài không hợp lệ" in _cc("nhap_lieu_kiem", study=xau, tep=_tep(tmp_path, "a.xlsx"))[1], xau
    assert "không có thư mục đề tài" in _cc("nhap_lieu_kiem", study="KHONG-CO", tep=_tep(tmp_path, "a.xlsx"))[1]
    assert "chỉ nhận" in _cc("nhap_lieu_kiem", study="DE-TAI", tep=_tep(tmp_path, "a.csv"))[1]
    assert "không thấy tệp" in _cc("nhap_lieu_kiem", study="DE-TAI", tep=str(tmp_path / "vang.xlsx"))[1]
    assert _goi(y_khoa) == []


def test_phan_tich_chi_tren_du_lieu_khoa_khong_ghi_de_cong(y_khoa):
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", outcome="y", ap_dung=True)
    assert kq["tu_choi"] is True and "ĐÃ KHOÁ" in kq["ly_do"] and _goi(y_khoa) == []
    (y_khoa / "exports" / "DE-TAI" / "KHOA").write_text("", encoding="utf-8")
    loi, kq = _cc("phan_tich_g6", study="DE-TAI")
    assert loi and "KHÔNG tự chọn biến" in kq
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", outcome="y", group="g", covariates=["a", "b"], don_vi_phoi_nhiem=15)
    assert kq["chay_kho"] and "--kiem-cheo" in kq["se_chay"] and not [x for x in kq["se_chay"] if "i-confirm" in x]
    assert kq["se_chay"][kq["se_chay"].index("--covariates") + 1] == "a,b"
    _cc("phan_tich_g6", study="DE-TAI", outcome="y", group="g", ap_dung=True)
    goi = _goi(y_khoa)[-1]
    assert goi[0] == "run_stats_analysis.py" and goi[goi.index("--data") + 1].endswith("khoa.csv")
    assert not [x for x in goi if x.startswith("--i-confirm")]


def test_phan_tich_dung_lai_dung_dac_ta_luot_truoc(y_khoa):
    d = y_khoa / "exports" / "DE-TAI"
    (d / "KHOA").write_text("", encoding="utf-8")
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", dung_dac_ta_truoc=True)
    assert loi and "chưa có lượt G6 trước" in kq
    (d / "G6_analysis_summary.json").write_text(json.dumps({"dac_ta_phan_tich": {"outcome": "hl", "group": "cho",
        "covariates": ["tuoi"], "don_vi_phoi_nhiem": 15}, "n_total": 30}), encoding="utf-8")  # fmt: skip
    loi, kq = _cc("phan_tich_g6", study="DE-TAI", dung_dac_ta_truoc=True)
    assert kq["dac_ta"]["outcome"] == "hl" and "--don-vi-phoi-nhiem" in kq["se_chay"]
    loi, kq = _cc("phan_tich_ket_qua", study="DE-TAI")
    assert kq["ket_qua"]["n_total"] == 30 and kq["kiem_cheo_g6"] == {"trang_thai": "KHOP"}


def test_kiem_cheo_mac_dinh_chi_doc(y_khoa):
    _cc("kiem_cheo_g6", study="DE-TAI")
    assert _goi(y_khoa)[-1][:2] == ["kiem_cheo_g6.py", "trang-thai"]
    _cc("kiem_cheo_g6", study="DE-TAI", ap_dung=True)
    assert _goi(y_khoa)[-1][:2] == ["kiem_cheo_g6.py", "chay"]


def test_kenh_giao_thuc_chi_co_json(y_khoa, tmp_path):
    vao = io.StringIO(
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "nhap_lieu_kiem",
                    "arguments": {"study": "DE-TAI", "tep": _tep(tmp_path, "lan1.xlsx")}}}) + "\n" + "{hỏng\n"
    )  # fmt: skip
    ra = io.StringIO()
    M.chay(vao, ra)
    dong = ra.getvalue().splitlines()
    assert len(dong) == 2 and all(json.loads(x)["jsonrpc"] == "2.0" for x in dong)


def test_cai_claude_desktop_chay_kho_sao_luu_giu_khoa_khac(tmp_path):
    tep = tmp_path / "claude_desktop_config.json"
    tep.write_text(json.dumps({"mcpServers": {"endnote-ebm": {"command": "x"}}, "khac": 1}), encoding="utf-8")
    kq = M.cai_claude_desktop(False, tep)
    assert not kq.get("da_ghi") and "spss-r-ebm" not in json.loads(tep.read_text(encoding="utf-8"))["mcpServers"]
    kq = M.cai_claude_desktop(True, tep)
    moi = json.loads(tep.read_text(encoding="utf-8"))
    assert kq["da_ghi"] and Path(kq["sao_luu"]).exists() and moi["khac"] == 1
    assert set(moi["mcpServers"]) == {"endnote-ebm", "spss-r-ebm"}
    assert M.cai_claude_desktop(True, tep)["khong_doi"] is True


def test_chan_chen_co_qua_ten_bien(y_khoa, monkeypatch):
    (y_khoa / "exports" / "DE-TAI" / "KHOA").write_text("", encoding="utf-8")
    for arg in ({"outcome": "--i-confirm-sap-locked"}, {"outcome": "y", "covariates": ["a", "--data"]},
                {"outcome": "y", "vars": "-x"}, {"outcome": "y\n--i-confirm-irb-approved"}):  # fmt: skip
        loi, kq = _cc("phan_tich_g6", study="DE-TAI", ap_dung=True, **arg)
        assert loi and "không hợp lệ" in kq, arg
    assert _goi(y_khoa) == []
    # lớp chặn cuối vẫn đứng khi lớp kiểm giá trị bị gỡ
    monkeypatch.setattr(M, "_gia_tri", str)
    with pytest.raises(RuntimeError, match="cấm"):
        M._doi_so_phan_tich("DE-TAI", "k.csv", {"outcome": "--i-confirm-sap-locked"}, {})
