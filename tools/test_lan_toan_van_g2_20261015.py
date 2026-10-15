# -*- coding: utf-8 -*-
"""Làn toàn văn × dây chuyền/orchestrator/định tuyến — các phát hiện đã qua phản biện ngày 15/10/2026 (nhóm G2).

  W1    bước TV (phụ trợ) QUÁ GIỜ bị đọc thành «timeout» ⇒ dừng cả lượt; ngân sách giờ các tầng không khớp; ⑦ không có trần giờ.
  W2    phiếu ⑦ hứa «Claude lưu bản sao» cho cả NXB chưa kiểm điều khoản (phiên lưu chỉ nhận NXB có uỷ quyền còn hiệu lực).
  W4    báo cáo TV không vào phiếu cuối lượt ⇒ lượt có thể kết luận «🟢 xong, sạch» dù còn bài cần làn trình duyệt.
  W6    lỗi mạng khi dò đường đọc bị đếm vào «cần bác sĩ»; mã 2 (hạ tầng) của công cụ con bị nuốt.
  W10   ⑧ EndNote không biết cổng liêm chính đã PASS chưa ⇒ khối đọc nhanh ghi «đã qua cổng» khi Word nói «CHƯA xác minh».
  TT-06 đầu vào đã khai mà vắng / kho vắng ⇒ «Không có PMID nào» mã 0 (xanh giả); bộ năm ghi `toan_van` cho cả lượt rỗng.
  TT-07 kho toàn văn định vị cố định REPO/EBM-Dashboards ⇒ worktree/bố cục anh em nhìn kho MA; ⑦ ⑧ không nhận kho cạnh dashboard.
  intent cửa vào không biết EndNote · phiên uỷ quyền lưu bản sao · sổ nợ toàn văn.

Ngoại tuyến hoàn toàn: công cụ con và mạng là hàm giả; kho/dashboard là thư mục tạm. Không chạm EndNote, không chạm data/ thật.
"""
from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str, goc: Path = REPO):
    sp = importlib.util.spec_from_file_location(ten, goc / rel)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


op = _nap("ops/orchestrator.py", "_op_g2_1015")
tv = _nap("tools/toan_van_theo_chu_de.py", "_tv_g2_1015")
xg = _nap("tools/xuat_goi_cap_nhat.py", "_xg_g2_1015")
dtv = _nap("tools/doc_toan_van_co_nguoi.py", "_dtv_g2_1015")
sys.path.insert(0, str(REPO / "tools"))
from orchestrator import intent as it  # noqa: E402


# ═══ W1 — TV quá giờ không dừng chuỗi; ngân sách giờ khớp tầng dưới ═══════════════════════════════════════════════════
def test_tv_qua_gio_la_noi_dung_va_chuoi_chay_tiep():
    assert op.phan_loai("TV-toan-van", -9)[0] not in op.DUNG_HET
    assert op.phan_loai("TV-toan-van@suy-tim", -9)[0] == "noi_dung"
    assert op.phan_loai("B2-cong-liem-chinh[X]", -9)[0] == "timeout", "bước KHÔNG phụ trợ quá giờ vẫn dừng như cũ"
    plan = [{"buoc": "TV-toan-van", "lenh": ["py", "tv"]}, {"buoc": "A4-so-xac-minh[X]", "lat": "X", "lenh": ["py", "a4"]},
            {"buoc": "B2-cong-liem-chinh[X]", "lat": "X", "lenh": ["py", "b2"]}, {"buoc": "B5-hang-cho-bac-si", "lenh": ["py", "b5"]}]
    da_chay: list[str] = []
    res = op.thuc_thi(plan, chay=lambda ln, _t: (da_chay.append(ln[1]) or (-9 if ln[1] == "tv" else 0)), in_=lambda *_: None)
    assert da_chay == ["tv", "a4", "b2", "b5"], "TV quá giờ làm A4/B2/B5 không chạy"
    assert res["dung"] is None and res["tong_rc"] == 1


def test_ngan_sach_gio_khop_tang_duoi():
    assert op.TIMEOUT_BUOC["TV"] >= 3 * tv.TIMEOUT_CONG_CU + 300, "TV nối 3 công cụ con, mỗi cái trần TIMEOUT_CONG_CU"
    assert xg.TIMEOUT_TOAN_VAN >= 2 * tv.TIMEOUT_CONG_CU + tv.TRAN_GIAY_DUONG_DOC + 60, "⑦ = gom + đọc sâu + dò đường đọc"
    assert op.TIMEOUT_BUOC["B4"] >= xg.TIMEOUT_TOAN_VAN + 3600, "B4 = ngân sách cũ của ①–⑥ + trần ⑦"


def test_run_qua_gio_tra_9_khong_nem():
    rc, out = xg.run([sys.executable, "-c", "import time; time.sleep(30)"], timeout=1)
    assert rc == -9 and "QUÁ 1 giây" in out


def test_lap_phieu_co_han_dung_o_tran_gio_va_ghi_chua_do_duoc(tmp_path):
    goi: list[list[str]] = []
    gio = [0.0]

    class _Dtv:
        @staticmethod
        def lap_phieu(ds, *, ngoai_tuyen, kho):
            assert ngoai_tuyen is False and kho == tmp_path
            goi.append(list(ds))
            gio[0] += 400
            return [{"pmid": ds[0], "cach": "trinh_duyet", "url": "u", "mien": "m", "dieu_khoan": "chua_kiem"}]
    lap = tv.lap_phieu_co_han(tmp_path, tran_giay=900, dong_ho=lambda: gio[0], dtv=_Dtv)
    ra = lap(["1", "2", "3", "4"])
    assert goi == [["1"], ["2"], ["3"]], "dò từng PMID, dừng khi hết trần"
    assert ra[3] == {"pmid": "4", "cach": "chua_ro", "het_gio": True, "ly_do": "hết trần 900 giây dò đường đọc lượt này"}
    assert tv.chua_do_duoc(ra[3]) and not tv.chua_do_duoc(ra[0])


# ═══ W2 — chỉ hứa «Claude lưu bản sao» khi NXB có uỷ quyền còn hiệu lực ══════════════════════════════════════════════
def _td(dk):
    return {"pmid": "9", "cach": "trinh_duyet", "url": "https://x.org/a", "mien": "x.org", "dieu_khoan": dk}


def test_giai_phap_luu_ban_sao_chi_khi_co_uy_quyen():
    co = tv.giai_phap(_td(dtv.KET_LUAN_UY_QUYEN))
    assert "Claude lưu bản sao" in co and "phien_uy_quyen_chrome.py --mo" in co and "Làn Chrome có uỷ quyền" in co
    chua = tv.giai_phap(_td("chua_kiem"))
    assert "Claude lưu bản sao" not in chua
    for can in ("đọc trang điều khoản trước", "chưa thuộc phạm vi lưu", "--nap", "điều khoản NXB về AI chưa kiểm"):
        assert can in chua, can
    da = tv.giai_phap(_td("da_kiem"))
    assert "Claude lưu bản sao" not in da and "--nap" in da and "Làn Chrome có uỷ quyền" not in da


# ═══ W6 — lỗi mạng ⇒ «chưa đo được», đếm riêng; mã 2 công cụ con nổi lên ═════════════════════════════════════════════
def test_giai_phap_loi_mang_la_chua_do_duoc_con_khong_co_url_van_la_viec_bac_si():
    gp = tv.giai_phap({"pmid": "9", "cach": "chua_ro", "ly_do": "Europe PMC lỗi URLError"})
    assert gp.startswith("Chưa đo được (Europe PMC lỗi URLError)") and "chạy lại" in gp and "KHÔNG phải «không có toàn văn»" in gp
    gp2 = tv.giai_phap({"pmid": "9", "cach": "chua_ro", "ly_do": "không có DOI/URL toàn văn trong Europe PMC"})
    assert not gp2.startswith("Chưa đo được") and "Find Full Text" in gp2


def test_phieu_dem_rieng_chua_do_duoc_khong_cong_vao_can_bac_si(tmp_path):
    kho = tmp_path / "toan_van_oa"
    kho.mkdir()

    def lap(ds):
        return [{"pmid": "111111", "cach": "chua_ro", "ly_do": "Europe PMC lỗi URLError"},
                {"pmid": "222222", "cach": "chua_ro", "ly_do": "doi.org lỗi TimeoutError"},
                {"pmid": "333333", "cach": "khong_truy_cap"}]
    dong, dem = tv.phieu_xac_thuc(["111111", "222222", "333333"], [], kho, lap, lambda pm: False)
    assert dem["khong_do_duoc"] == 2 and dem["can_bac_si"] == 1
    assert "1 cần bác sĩ · 0 chỉ có DOI · 2 chưa đo được (lỗi mạng — chạy lại khi mạng ổn)" in dong[0]
    assert sum("| ⚪ chưa đo được" in d for d in dong) == 2


def _kho(tmp_path):
    k = tmp_path / "EBM-Dashboards" / "toan_van_oa"
    k.mkdir(parents=True)
    return k


def _a2(tmp_path, pm=("123456",)):
    p = tmp_path / "RID.A2-x.json"
    p.write_text(json.dumps({"topics": [{"candidates": [{"pmid": x} for x in pm]}]}), encoding="utf-8")
    return p


def test_ma_2_cong_cu_con_thanh_dong_canh_bao_tren_stdout_va_bao_cao(tmp_path, capsys):
    kho = _kho(tmp_path)

    def chay(lenh):
        if "gom_toan_van_dashboard.py" in lenh[1]:
            return 2, "elink chết toàn phần — HẠ TẦNG"
        return 0, "ok"
    bc = tmp_path / "tv.md"
    assert tv.main(["--a2-json", str(_a2(tmp_path)), "--bao-cao", str(bc)], chay=chay, kho=kho) == 0, "phụ trợ: vẫn mã 0"
    out = capsys.readouterr().out
    dong = [d for d in out.splitlines() if d.startswith("⚠ ① Gom")]
    assert dong and "mã 2" in dong[0] and "HẠ TẦNG" in dong[0], out
    assert any(d.startswith("⚠ ① Gom") for d in bc.read_text(encoding="utf-8").splitlines())


# ═══ TT-06 — đầu vào vắng / kho vắng ⇒ ⚪ mã 2 ════════════════════════════════════════════════════════════════════════
def test_dashboard_khai_ma_vang_la_khong_do_duoc(tmp_path, capsys):
    vang = tmp_path / "WebDashboard_KHONG_CO.html"
    bc = tmp_path / "tv.md"
    assert tv.main(["--dashboard", str(vang), "--moi-trich-dan", "--bao-cao", str(bc)], chay=lambda ln: (0, ""),
                   kho=_kho(tmp_path)) == 2
    out = capsys.readouterr().out
    assert "⚪ KHÔNG ĐO ĐƯỢC" in out and "WebDashboard_KHONG_CO.html" in out
    noi = bc.read_text(encoding="utf-8")
    assert "⚪ KHÔNG ĐO ĐƯỢC" in noi and "Không có PMID nào" not in noi.replace("«không có PMID nào»", "")


def test_a2_json_khai_ma_vang_la_khong_do_duoc(tmp_path, capsys):
    assert tv.main(["--a2-json", str(tmp_path / "vang.json"), "--bao-cao", str(tmp_path / "a.md")], chay=lambda ln: (0, ""),
                   kho=_kho(tmp_path)) == 2
    assert "vang.json" in capsys.readouterr().out


def test_kho_vang_la_khong_do_duoc_khong_phai_can_bac_si(tmp_path, capsys):
    goi: list = []
    assert tv.main(["--a2-json", str(_a2(tmp_path)), "--bao-cao", str(tmp_path / "a.md")],
                   chay=lambda ln: (goi.append(ln) or (0, "")), kho=tmp_path / "khong_co" / "toan_van_oa") == 2
    assert "kho toàn văn" in capsys.readouterr().out and goi == [], "kho vắng thì không gọi công cụ con nào"


# ═══ TT-07 — định vị kho theo bố cục lồng rồi anh em; truyền kho xuống công cụ con hỗ trợ ═══════════════════════════════
def test_kho_mac_dinh_tim_ca_bo_cuc_anh_em(tmp_path):
    wt = tmp_path / "wt"
    (wt / "tools").mkdir(parents=True)
    for ten in ("toan_van_theo_chu_de.py", "ban_sao_tran.py"):
        shutil.copy(REPO / "tools" / ten, wt / "tools" / ten)
    (tmp_path / "EBM-Dashboards").mkdir()
    m = _nap("tools/toan_van_theo_chu_de.py", "_tv_g2_anh_em", goc=wt)
    assert m.DASH == tmp_path / "EBM-Dashboards" and m.KHO == tmp_path / "EBM-Dashboards" / "toan_van_oa"


def test_doc_sau_nhan_dash_cua_dung_kho_gom_va_phieu_khong_nhan_co_la(tmp_path):
    kho = _kho(tmp_path)
    goi: list[list[str]] = []
    tv.main(["--a2-json", str(_a2(tmp_path)), "--bao-cao", str(tmp_path / "a.md")],
            chay=lambda ln: (goi.append(ln) or (0, "")), kho=kho)
    ten = {Path(ln[1]).name: ln for ln in goi}
    ds = ten["doc_sau_toan_van.py"]
    assert ds[ds.index("--dash") + 1] == str(kho.parent) and ds.index("--dash") < ds.index("--pmid")
    assert "--dash" not in ten["gom_toan_van_dashboard.py"] and "--dash" not in ten["doc_toan_van_co_nguoi.py"]


def test_hop_dong_co_cua_cong_cu_con():
    """Chỉ truyền cờ mà công cụ con THẬT nhận (cờ lạ làm argparse chết mã 2): doc_sau `--dash`, EndNote `--kho-toan-van`,
    toan_van_theo_chu_de `--kho`."""
    for ten, co in (("doc_sau_toan_van.py", "--dash"), ("nap_endnote_chu_de.py", "--kho-toan-van"),
                    ("toan_van_theo_chu_de.py", "--kho")):
        r = subprocess.run([sys.executable, str(REPO / "tools" / ten), "--help"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120, cwd=str(REPO))
        assert r.returncode == 0 and co in r.stdout, (ten, co, r.stdout[-400:], r.stderr[-400:])


# ═══ ⑦ ⑧ của bộ năm (gọi trực tiếp, run() giả) ════════════════════════════════════════════════════════════════════════
def _buoc_tv(monkeypatch, tmp_path, rc, out):
    goi: list[tuple[list[str], int | None]] = []
    monkeypatch.setattr(xg, "run", lambda cmd, cwd=None, timeout=None: (goi.append(([str(c) for c in cmd], timeout)) or (rc, out)))
    dash = tmp_path / "WebDashboard_X_20261015.html"
    result: dict = {"ban_doc": str(tmp_path / "derivatives" / "X_ban-doc.html")}
    buf = io.StringIO()
    with redirect_stdout(buf):
        ma = xg.buoc_toan_van(sys.executable, dash, result)
    return ma, result, goi, buf.getvalue(), dash


def test_buoc_7_truyen_kho_canh_dashboard_va_tran_gio(monkeypatch, tmp_path):
    _ma, result, goi, _out, dash = _buoc_tv(monkeypatch, tmp_path, 0, "PHIẾU XÁC THỰC — 2 trích dẫn: …\n→ x")
    (cmd, het), = goi
    assert cmd[cmd.index("--kho") + 1] == str(dash.parent / "toan_van_oa") and "--moi-trich-dan" in cmd
    assert het == xg.TIMEOUT_TOAN_VAN
    assert result["toan_van"].endswith("X_toan-van.md")


def test_buoc_7_ma_0_khong_phieu_khong_ghi_toan_van(monkeypatch, tmp_path):
    _ma, result, _g, out, _d = _buoc_tv(monkeypatch, tmp_path, 0, "# TOÀN VĂN …\nKhông có PMID nào cần lấy toàn văn lượt này.\n→ x")
    assert "toan_van" not in result and result["toan_van_ly_do"] and "⚪" in out


def test_buoc_7_khong_do_duoc_va_canh_bao_duoc_in_lai(monkeypatch, tmp_path):
    _ma, result, _g, out, _d = _buoc_tv(monkeypatch, tmp_path, 2, "⚪ KHÔNG ĐO ĐƯỢC — không thấy kho toàn văn /k\n→ x")
    assert "toan_van" not in result and "   ⚪ KHÔNG ĐO ĐƯỢC — không thấy kho toàn văn /k" in out
    _ma, result, _g, out, _d = _buoc_tv(monkeypatch, tmp_path, 0, "PHIẾU XÁC THỰC — 1 …\n⚠ ① Gom bản hợp lệ: mã 2 — HẠ TẦNG\n→ x")
    assert "   ⚠ ① Gom bản hợp lệ: mã 2 — HẠ TẦNG" in out and result["toan_van_canh_bao"] == ["⚠ ① Gom bản hợp lệ: mã 2 — HẠ TẦNG"]


def test_buoc_7_qua_gio_di_tiep(monkeypatch, tmp_path):
    ma, result, _g, out, _d = _buoc_tv(monkeypatch, tmp_path, -9, "QUÁ 3000 giây — dừng công cụ con")
    assert ma == -9 and "toan_van" not in result and "QUÁ" in out and "không chặn" in out


def test_lenh_endnote_chua_xac_minh_khi_cong_khong_pass(tmp_path):
    dash = tmp_path / "WebDashboard_X_20261015.html"
    chua = xg.lenh_endnote("py", dash, verified=False)
    da = xg.lenh_endnote("py", dash, verified=True)
    assert "--chua-xac-minh" in chua and "--chua-xac-minh" not in da
    assert chua[chua.index("--kho-toan-van") + 1] == str(dash.parent / "toan_van_oa")


# ═══ bộ năm đầu–cuối: main() với run() giả, ⑦ ⑧ được phép chạy (không chạm công cụ thật) ══════════════════════════════
def _main_bo_nam(monkeypatch, tmp_path, *, online: bool, rc_cong: int):
    cong_cu = tmp_path / "cc"
    cong_cu.mkdir()
    for ten in ("verify_dashboard.py", "build_dashboard_docx.py", "build_ban_doc_chung_cu.py"):
        (cong_cu / ten).write_text("# giả\n", encoding="utf-8")
    monkeypatch.setattr(xg, "VERIFY", cong_cu / "verify_dashboard.py")
    monkeypatch.setattr(xg, "DOCX", cong_cu / "build_dashboard_docx.py")
    monkeypatch.setattr(xg, "BAN_DOC", cong_cu / "build_ban_doc_chung_cu.py")
    monkeypatch.setattr(xg, "xuat_ban_word_html", lambda docx, dash: (Path(str(docx)).with_suffix(".html"), ""))
    monkeypatch.setattr(xg, "ghi_sidecar_hash_data", lambda dash, word: None)
    monkeypatch.setattr(xg, "_dang_kiem_thu", lambda: False)
    goi: list[list[str]] = []

    def run(cmd, cwd=None, timeout=None):
        c = [str(x) for x in cmd]
        goi.append(c)
        ten = Path(c[1]).name
        if ten == "verify_dashboard.py":
            return (0, "KẾT QUẢ: ✓ PASS") if "--strict-sources" in c else (rc_cong, "KẾT QUẢ")
        return {"build_ban_doc_chung_cu.py": (0, f"✓ Đã ghi {tmp_path / 'derivatives' / 'X_ban-doc.html'}"),
                "build_dashboard_docx.py": (0, f"✓ Đã ghi {tmp_path / 'derivatives' / 'X.docx'} — ok"),
                "docx_sang_pdf_giu_mau.py": (0, "✓ pdf"),
                "toan_van_theo_chu_de.py": (0, "PHIẾU XÁC THỰC — 1 trích dẫn\n→ bc")}.get(ten, (0, "Tổng: 0"))
    monkeypatch.setattr(xg, "run", run)
    dash = tmp_path / "WebDashboard_X_20261015.html"
    dash.write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["xuat_goi_cap_nhat.py", str(dash)] + (["--online"] if online else []))
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        xg.main()
    return [Path(c[1]).name for c in goi], {Path(c[1]).name: c for c in goi}


@pytest.mark.parametrize("online, rc_cong, chua_xm", [(True, 0, False), (True, 2, True), (False, 0, True)])
def test_main_buoc_8_mang_trang_thai_cong(monkeypatch, tmp_path, online, rc_cong, chua_xm):
    thu_tu, lenh = _main_bo_nam(monkeypatch, tmp_path, online=online, rc_cong=rc_cong)
    assert "nap_endnote_chu_de.py" in lenh, thu_tu
    assert ("--chua-xac-minh" in lenh["nap_endnote_chu_de.py"]) is chua_xm, (online, rc_cong, lenh["nap_endnote_chu_de.py"])
    if online:
        assert thu_tu.index("toan_van_theo_chu_de.py") < thu_tu.index("nap_endnote_chu_de.py"), "⑦ phải chạy TRƯỚC ⑧"
    else:
        assert "toan_van_theo_chu_de.py" not in lenh, "⑦ cần mạng — không --online thì không chạy"


# ═══ W4 — báo cáo TV vào phiếu cuối lượt ══════════════════════════════════════════════════════════════════════════════
def _bc(tmp_path, noi):
    p = tmp_path / "RID.TV-x.md"
    p.write_text(noi, encoding="utf-8")
    return str(p)


def test_viec_toan_van_theo_noi_dung_bao_cao(tmp_path):
    thieu = _bc(tmp_path, "# TOÀN VĂN\n\n## ① Gom — mã 0\n```\n⚠ bỏ qua «x» — dòng của công cụ con\n## Kết quả: còn thiếu 99\n```\n\n"
                          "## Kết quả: +1 bài có toàn văn mới · còn thiếu 3\n")
    v = op.viec_toan_van({"tv_bao_cao": [thieu]})
    assert len(v) == 1 and "đọc phiếu toàn văn" in v[0] and "RID.TV-x.md" in v[0] and "3 bài còn thiếu" in v[0], v
    assert "⚠" not in v[0], "dòng ⚠ trong rào ``` là của công cụ con — không đếm"
    loi = _bc(tmp_path, "## ① Gom — mã 2\n```\nx\n```\n\n⚠ ① Gom: mã 2 — HẠ TẦNG\n\n## Kết quả: +0 bài có toàn văn mới · còn thiếu 0\n")
    v = op.viec_toan_van({"tv_bao_cao": [loi]})
    assert len(v) == 1 and "1 công cụ con lỗi hạ tầng" in v[0]
    assert op.viec_toan_van({"tv_bao_cao": [_bc(tmp_path, "Không có PMID nào cần lấy toàn văn lượt này.\n")]}) == []
    v = op.viec_toan_van({"tv_bao_cao": [_bc(tmp_path, "⚪ KHÔNG ĐO ĐƯỢC — không thấy kho toàn văn /k\n")]})
    assert len(v) == 1 and "KHÔNG ĐO ĐƯỢC" in v[0] and "/k" in v[0]
    v = op.viec_toan_van({"tv_bao_cao": [str(tmp_path / "vang.md")]})
    assert len(v) == 1 and "chưa ra phiếu toàn văn" in v[0] and "KHÔNG phải «đã đủ toàn văn»" in v[0]


def test_thuc_thi_ghi_duong_dan_bao_cao_tv_ca_khi_resume():
    b = {"buoc": "TV-toan-van", "lenh": ["py", "tv.py", "--bao-cao", "logs/R.TV-x.md"]}
    assert op.thuc_thi([b], chay=lambda *_: 0, in_=lambda *_: None)["tv_bao_cao"] == ["logs/R.TV-x.md"]
    assert op.thuc_thi([b], chay=lambda *_: 0, in_=lambda *_: None, da_xong={"TV-toan-van"})["tv_bao_cao"] == ["logs/R.TV-x.md"]


def test_main_phieu_cuoi_luot_co_dong_toan_van(tmp_path, monkeypatch, capsys):
    m = _nap("ops/orchestrator.py", "_op_g2_main")
    (tmp_path / "logs").mkdir()
    dash = tmp_path / "dash"
    dash.mkdir()
    db = dash / "WebDashboard_EBM_VanDeCuThe_SuyTim_TongHop_20260609.html"
    db.write_text("<html></html>", encoding="utf-8")
    monkeypatch.setattr(m, "LOGS", tmp_path / "logs")
    monkeypatch.setattr(m, "DASH", dash)
    monkeypatch.setattr(m, "_cho_ky_rut_bai", lambda: frozenset())
    tt = {"q": "Suy tim", "loai": "watchlist", "wl_topics": ["Suy tim"], "a2_arg": "Suy tim", "goc": [],
          "lat_cat": [{"duong_dan": str(db)}], "ly_do": "", "gan_dung": [], "cach": "ten-watchlist"}
    monkeypatch.setattr(m, "_phan_giai", lambda t: tt)
    monkeypatch.setattr(m, "_dashboards_cua_chu_de", lambda t: [db])

    def chay(lenh, _timeout):
        if "--json-report" in lenh:
            Path(lenh[lenh.index("--json-report") + 1]).write_text(json.dumps({"status": "PASS", "topics": []}), encoding="utf-8")
        if "--bao-cao" in lenh:
            Path(lenh[lenh.index("--bao-cao") + 1]).write_text("## Kết quả: +0 bài có toàn văn mới · còn thiếu 2\n",
                                                                 encoding="utf-8")
        return 0
    monkeypatch.setattr(m, "_chay_that", chay)
    monkeypatch.setattr(sys, "argv", ["orchestrator.py", "--topic", "Suy tim", "--online"])
    assert m.main() == 0
    out = capsys.readouterr().out
    (phieu,) = (tmp_path / "logs").glob("*.phieu.md")
    noi = phieu.read_text(encoding="utf-8")
    assert "đọc phiếu toàn văn" in noi and "2 bài còn thiếu" in noi, noi
    assert "🟢 xong, sạch" not in out


# ═══ cửa vào định tuyến ═══════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("cau, dich", [
    ("nạp chủ đề này vào EndNote", "tools/nap_endnote_chu_de.py"),
    ("gắn PDF toàn văn vào EndNote", "tools/nap_endnote_chu_de.py"),
    ("tóm tắt tiếng Việt vào EndNote", "tools/nap_endnote_chu_de.py"),
    ("nap chu de nay vao endnote", "tools/nap_endnote_chu_de.py"),
    ("mở phiên uỷ quyền chrome", "tools/phien_uy_quyen_chrome.py"),
    ("tôi uỷ quyền Claude mở Chrome lưu bản sao toàn văn hôm nay", "tools/phien_uy_quyen_chrome.py"),
    ("tôi ủy quyền Claude mở Chrome lưu bản sao toàn văn hôm nay", "tools/phien_uy_quyen_chrome.py"),
    ("sổ nợ toàn văn còn bao nhiêu", "tools/so_toan_van.py"),
    ("so no toan van con bao nhieu", "tools/so_toan_van.py"),
    ("đọc toàn văn các thẻ tuần W40", "tools/doc_toan_van_co_nguoi.py"),
])
def test_dinh_tuyen_lan_toan_van(cau, dich):
    r = it.route(cau)
    assert (r.kind, r.target) == ("cong_cu", dich), (cau, r)


def test_dinh_tuyen_lan_toan_van_van_thua_ca_lam_sang_va_co_do():
    assert it.route("tôi có bệnh nhân nam 60 tuổi, nạp EndNote giúp").kind == "clinical_case"
    assert it.route("bệnh nhân ngừng tim, mở phiên uỷ quyền chrome").kind == "clinical_case"
    assert it.route("uỷ quyền máy đọc Wiley").target != "tools/phien_uy_quyen_chrome.py", \
        "uỷ quyền ĐỌC theo NXB không phải mở phiên LƯU bản sao"
