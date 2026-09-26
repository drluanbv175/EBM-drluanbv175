#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #41 (26/09/2026): `verify_dashboard_xss_hardening.py` báo
«FAIL — 4 vấn đề» (mã 1) trên mọi bản sao git trần chỉ vì các tệp CHỈ sống trong
OneDrive (EBM-Dashboards/, EBM_MASTER/) vắng mặt — đỏ giả làm mất lòng tin vào chốt bảo
mật; kèm khe im lặng: gen_catalog_html.py vắng thì bị bỏ qua.

Hợp đồng sau vá:
  · ⚪ CHƯA ĐO chỉ khi ĐỒNG THỜI tệp thuộc gốc chỉ-OneDrive VÀ ban_sao_git_tran() đúng;
  · máy thật (còn gốc dữ liệu) thiếu tệp ⇒ FAIL; bản vendor sync/skills/ vắng ⇒ FAIL;
  · mã: FAIL ⇒ 1 (kể cả khi có ⚪) · chỉ ⚪ ⇒ 2 «MEASUREMENT_INCOMPLETE» · đủ và đạt ⇒ 0;
  · không in «KẾT QUẢ: PASS» khi còn ⚪.

Mỗi ca dựng một cây ROOT tạm (tmp_path) và chép ĐÚNG bản vendor thật có trong git — kiểm
hành vi, không grep mã nguồn; ban_sao_git_tran() chạy thật trên cây tạm (không giả lập).
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
VENDOR = [
    "sync/skills/cap-nhat-chung-cu-y-khoa/tools/build_library.py",
    "sync/skills/dark-analyst/tools/build_library.py",
]


def _nap():
    spec = importlib.util.spec_from_file_location(
        "verify_xss_t20260926", HERE / "verify_dashboard_xss_hardening.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["verify_xss_t20260926"] = mod
    spec.loader.exec_module(mod)
    return mod


X = _nap()


def _cay_tam(tmp_path: Path, vendor: bool = True) -> Path:
    goc = tmp_path / "goc"
    goc.mkdir()
    if vendor:
        for rel in VENDOR:
            dich = goc / rel
            dich.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, dich)
    return goc


def _chay(monkeypatch, capsys, goc: Path) -> tuple[int, str]:
    monkeypatch.setattr(X, "ROOT", goc)
    rc = X.main()
    return rc, capsys.readouterr().out


def _dong_ket_qua(out: str) -> str:
    return next(dong for dong in out.splitlines() if dong.startswith("KẾT QUẢ:"))


def test_ban_sao_tran_vendor_dat_ma_2_khong_in_pass(monkeypatch, capsys, tmp_path):
    goc = _cay_tam(tmp_path)
    assert X._bst.ban_sao_git_tran(goc) is True
    rc, out = _chay(monkeypatch, capsys, goc)
    assert rc == 2, out
    kq = _dong_ket_qua(out)
    assert "MEASUREMENT_INCOMPLETE" in kq
    assert "PASS" not in kq and "FAIL" not in kq
    # Cả năm tệp chỉ-OneDrive đều được liệt kê là ⚪, gồm cả gen_catalog_html.py.
    for rel in ("EBM-Dashboards/tools/build_library.py", "EBM_MASTER/skill_assets/build_library.py",
                "EBM-Dashboards/tools/assemble_dashboard.py", "EBM_MASTER/tools/gen_links_html.py",
                "EBM_MASTER/tools/gen_catalog_html.py"):
        assert f"⚪ {rel}: vắng trên bản sao git trần" in out, rel
    assert "✓ PASS  sync/skills/cap-nhat-chung-cu-y-khoa/tools/build_library.py" in out
    # Nhãn từng dòng cũng không được nói FAIL cho tệp chỉ vắng trên bản sao trần.
    assert "⚪ CHƯA ĐO  EBM-Dashboards/tools/build_library.py" in out
    assert "✗ FAIL" not in out, out


def test_may_that_thieu_tep_onedrive_van_fail(monkeypatch, capsys, tmp_path):
    goc = _cay_tam(tmp_path)
    (goc / "EBM-Dashboards" / "tools").mkdir(parents=True)   # máy thật, cây OneDrive hỏng dở
    assert X._bst.ban_sao_git_tran(goc) is False
    rc, out = _chay(monkeypatch, capsys, goc)
    assert rc == 1, out
    assert "EBM-Dashboards/tools/build_library.py: KHÔNG TỒN TẠI" in out
    assert "MEASUREMENT_INCOMPLETE" not in out


def test_ban_sao_tran_vendor_bi_go_esc_la_fail_du_co_cho_do(monkeypatch, capsys, tmp_path):
    goc = _cay_tam(tmp_path)
    f = goc / VENDOR[0]
    f.write_text(f.read_text(encoding="utf-8").replace("function esc(", "function khong_esc("),
                 encoding="utf-8")
    rc, out = _chay(monkeypatch, capsys, goc)
    assert rc == 1, out
    kq = _dong_ket_qua(out)
    assert kq.startswith("KẾT QUẢ: FAIL") and "⚪ CHƯA ĐO" in kq
    assert "thiếu hàm esc()/escUrl()" in out


def test_vendor_trong_git_vang_luon_fail_ke_ca_ban_sao_tran(monkeypatch, capsys, tmp_path):
    goc = _cay_tam(tmp_path)
    (goc / VENDOR[1]).unlink()
    rc, out = _chay(monkeypatch, capsys, goc)
    assert rc == 1, out
    assert f"{VENDOR[1]}: KHÔNG TỒN TẠI" in out


def test_may_that_thieu_rieng_gen_catalog_la_fail_khong_bo_qua(monkeypatch, tmp_path):
    goc = _cay_tam(tmp_path)
    gl = goc / "EBM_MASTER" / "tools" / "gen_links_html.py"
    gl.parent.mkdir(parents=True)
    gl.write_text('const ESC=s=>String(s).replace(/</g,"&lt;");\n', encoding="utf-8")
    monkeypatch.setattr(X, "ROOT", goc)
    p = X.check_ebm_master_generators()
    assert p == ["EBM_MASTER/tools/gen_catalog_html.py: KHÔNG TỒN TẠI"], p
    assert not isinstance(p[0], X.ChuaDo)


def test_du_tep_va_dat_moi_ra_ma_0(monkeypatch, capsys, tmp_path):
    """Đối chứng: đủ mọi bản và đều đạt ⇒ mã 0, «KẾT QUẢ: PASS»."""
    goc = _cay_tam(tmp_path)
    for rel in ("EBM-Dashboards/tools/build_library.py", "EBM_MASTER/skill_assets/build_library.py"):
        (goc / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / VENDOR[0], goc / rel)
    ad = goc / "EBM-Dashboards" / "tools" / "assemble_dashboard.py"
    ad.write_text(
        "import json\n"
        "def to_js(o):\n"
        "    s = json.dumps(o, ensure_ascii=False)\n"
        "    return s.replace('<', '\\\\u003c').replace('\\u2028', '\\\\u2028')"
        ".replace('\\u2029', '\\\\u2029')\n", encoding="utf-8")
    t = goc / "EBM_MASTER" / "tools"
    t.mkdir(parents=True, exist_ok=True)
    (t / "gen_links_html.py").write_text('const ESC=s=>String(s).replace(/</g,"&lt;");\n',
                                          encoding="utf-8")
    (t / "gen_catalog_html.py").write_text('E = {"<": "&lt;", \'"\': "&quot;"}\n', encoding="utf-8")
    rc, out = _chay(monkeypatch, capsys, goc)
    assert rc == 0, out
    assert _dong_ket_qua(out).startswith("KẾT QUẢ: PASS")
