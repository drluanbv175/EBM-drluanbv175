# -*- coding: utf-8 -*-
"""Test «hệ thống BẢO ĐẢM toàn văn» (04/10/2026) — ngoại tuyến hoàn toàn.

Đo thật 04/10: (1) cổng chỉ chặn mục apply thẩm định từ tóm tắt khi mục TỰ KHAI 'partial' ⇒ 27 mục apply (20 PMID) không có
toàn văn trong kho vẫn qua cổng; (2) chuỗi máy theo chủ đề (`ops/orchestrator.py`) không có bước toàn văn nào.
Vá: `verify_dashboard.kiem_toan_van_apply` (cảnh báo đo được từ kho) · `tools/toan_van_theo_chu_de.py` · bước «TV».
"""
from __future__ import annotations

import importlib.util
import json
import sys
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

TRANG_GIOI_THIEU = ("<html><body>Abstract Introduction Methods Results Discussion " + "w " * 2700
                    + " Fingerprint Access to Document Link to publication</body></html>")


def _muc(iid, dec, pmid, ac=None):
    them = f", appraisalCompleteness:'{ac}'" if ac else ""
    return "{id:'%s', decision:'%s', pmid:'%s'%s}" % (iid, dec, pmid, them)


# ── cổng: toàn văn đo được ──────────────────────────────────────────────────────────────────────
def test_co_toan_van_nhan_moi_loai_va_loai_trang_gioi_thieu(tmp_path):
    (tmp_path / "PMID-111_PMC9.xml").write_text("x")
    (tmp_path / "PMID-222_CHR.pdf").write_text("x")
    (tmp_path / "PMID-333_UPW.html").write_text(TRANG_GIOI_THIEU)
    (tmp_path / "trinh_duyet").mkdir()
    (tmp_path / "trinh_duyet" / "PMID-444.json").write_text("{}")
    (tmp_path / "doc_sau").mkdir()
    (tmp_path / "doc_sau" / "PMID-555.md").write_text("ghi chú — không phải toàn văn")
    assert vd.co_toan_van_trong_kho("111", tmp_path) and vd.co_toan_van_trong_kho("222", tmp_path)
    assert vd.co_toan_van_trong_kho("444", tmp_path), "đọc qua làn trình duyệt có bác sĩ là đã đọc toàn văn"
    assert not vd.co_toan_van_trong_kho("333", tmp_path), "trang giới thiệu kho lưu trữ KHÔNG phải toàn văn"
    assert not vd.co_toan_van_trong_kho("555", tmp_path), "hồ sơ đọc sâu không thay toàn văn"


def test_kiem_toan_van_apply_canh_bao_dung_muc(tmp_path):
    (tmp_path / "PMID-111_PMC9.xml").write_text("x")
    items = [_muc("ITEM-01", "apply", "111"), _muc("ITEM-02", "apply", "222"), _muc("ITEM-03", "consider", "333"),
             _muc("ITEM-04", "apply", "444", ac="full")]
    warns, oks = [], []
    vd.kiem_toan_van_apply(items, tmp_path, warns, oks)
    assert len(warns) == 1 and "ITEM-02" in warns[0] and "222" in warns[0]
    assert any("2/3" in o for o in oks)


def test_khong_thay_kho_thi_khong_do_khong_bao_do_gia(tmp_path):
    warns, oks = [], []
    vd.kiem_toan_van_apply([_muc("ITEM-01", "apply", "111")], tmp_path / "khong_co", warns, oks)
    assert not warns and any("CHƯA đo" in o for o in oks)


def test_main_cong_that_su_goi_kiem_toan_van(tmp_path):
    """Kiểm DÒNG THI HÀNH: chạy main() của cổng trên dashboard tối giản có kho rỗng bên cạnh ⇒ phải in cảnh báo toàn văn."""
    import subprocess
    (tmp_path / "toan_van_oa").mkdir()
    db = tmp_path / "WebDashboard_EBM_VanDeCuThe_X_20261004.html"
    db.write_text("<script>const DATA = {meta:{}, summary:{}, items:[" + _muc("ITEM-01", "apply", "123456")
                  + "]};\n/* HẾT KHỐI DATA */</script>", encoding="utf-8")
    r = subprocess.run([sys.executable, str(REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py"),
                        str(db), "--strict-sources"], capture_output=True, text=True)
    assert "kho toàn văn CHƯA có PMID 123456" in r.stdout + r.stderr


def test_hai_ban_cong_trung_byte():
    assert (REPO / "sync/skills/cap-nhat-chung-cu-y-khoa/tools/verify_dashboard.py").read_bytes() == \
        (REPO / "sync/skills/dark-analyst/tools/verify_dashboard.py").read_bytes()


# ── công cụ bước TV ─────────────────────────────────────────────────────────────────────────────
def _a2(tmp_path, ung_vien):
    p = tmp_path / "RID.A2-x.json"
    p.write_text(json.dumps({"topics": [{"topic": "x", "candidates": ung_vien}]}), encoding="utf-8")
    return p


def test_pmid_tu_a2_bo_bai_rut_va_trung(tmp_path):
    p = _a2(tmp_path, [{"pmid": "123456", "rut_bai": "ok"}, {"pmid": "234567", "rut_bai": "retracted"},
                       {"pmid": "123456", "rut_bai": "ok"}, {"pmid": "", "rut_bai": "ok"}, {"pmid": "345678"}])
    assert tv.pmid_tu_a2(p) == ["123456", "345678"]


def test_main_goi_dung_ba_cong_cu_va_ghi_bao_cao(tmp_path):
    kho = tmp_path / "kho"
    kho.mkdir()
    p = _a2(tmp_path, [{"pmid": "123456", "rut_bai": "ok"}, {"pmid": "234567", "rut_bai": "ok"}])
    goi = []

    def chay(lenh):
        goi.append(lenh)
        if "gom_toan_van_dashboard.py" in lenh[1]:
            (kho / "PMID-123456_PMC1.xml").write_text("x")  # giả lập: một bài có bản OA
        return 0, "ok"
    bc = tmp_path / "RID.TV-x.md"
    assert tv.main(["--a2-json", str(p), "--bao-cao", str(bc)], chay=chay, kho=kho) == 0
    ten = [Path(l[1]).name for l in goi]
    assert ten == ["gom_toan_van_dashboard.py", "doc_sau_toan_van.py", "doc_toan_van_co_nguoi.py"]
    assert "--unpaywall" in goi[0]
    assert goi[2][goi[2].index("--pmid") + 1:] == ["234567"], "phiếu làn trình duyệt chỉ cho bài CÒN THIẾU"
    noi = bc.read_text(encoding="utf-8")
    assert "+1 bài có toàn văn mới" in noi and "234567" in noi


def test_main_json_hong_tra_2_va_khong_pmid_tra_0(tmp_path):
    hong = tmp_path / "hong.json"
    hong.write_text("{khong phai json", encoding="utf-8")
    assert tv.main(["--a2-json", str(hong), "--bao-cao", str(tmp_path / "a.md")], chay=lambda l: (0, ""),
                   kho=tmp_path) == 2
    rong = _a2(tmp_path, [])
    assert tv.main(["--a2-json", str(rong), "--bao-cao", str(tmp_path / "b.md")], chay=lambda l: (0, ""), kho=tmp_path) == 0
    assert "Không có PMID" in (tmp_path / "b.md").read_text(encoding="utf-8")


# ── orchestrator: bước TV nằm giữa A2 và A4/B2, không chặn chuỗi ───────────────────────────────
def _ke(monkeypatch, tt, dbs):
    monkeypatch.setattr(op, "_phan_giai", lambda _t: tt)
    monkeypatch.setattr(op, "_dashboards_cua_chu_de", lambda _t: dbs)
    return op.ke_hoach("x", False, False, run_id="RID")


def test_buoc_tv_sau_a2_truoc_a4_va_doc_json_cua_a2(monkeypatch):
    tt = {"loai": "watchlist", "a2_arg": "Bệnh thận mạn (CKD)", "lat_cat": [], "ly_do": ""}
    db = Path("WebDashboard_EBM_VanDeCuThe_BenhThanMan_CKD_20260701.html")
    cac = _ke(monkeypatch, tt, [db])
    ten = [b["buoc"] for b in cac]
    i_a2, i_tv = ten.index("A2-quet"), ten.index("TV-toan-van")
    assert i_a2 < i_tv < min(i for i, t in enumerate(ten) if t.startswith(("A4", "B2")))
    a2 = cac[i_a2]["lenh"]
    tvl = cac[i_tv]["lenh"]
    assert tvl[tvl.index("--a2-json") + 1] == a2[a2.index("--json-report") + 1]
    assert str(db) in tvl


def test_buoc_tv_khong_co_khi_ban_tin_gop_va_khong_chan_chuoi(monkeypatch):
    tt = {"loai": "khong_can", "a2_arg": None, "lat_cat": [], "ly_do": "bản tin gộp"}
    assert not [b for b in _ke(monkeypatch, tt, [Path("WebDashboard_EBM_Uptodate_20260607.html")])
                if b["buoc"].startswith("TV")]
    muc, _ = op.phan_loai("TV-toan-van", 2)
    assert muc not in op.DUNG_HET, "lỗi bước toàn văn (phụ trợ) không được dừng cả chuỗi"
