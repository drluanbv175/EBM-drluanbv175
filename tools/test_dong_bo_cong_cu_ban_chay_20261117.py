#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy BH179 (17/11/2026): vá ở nguồn chuẩn phải TỚI ĐƯỢC bản CHẠY của MỌI tool dây chuyền.

Ca thật: PR #402 vá `check_topic_relevance.py` ở `sync/skills/cap-nhat-chung-cu-y-khoa/tools/`
và đã gộp, nhưng dây chuyền máy thật nạp bản `EBM-Dashboards/tools/` còn cũ — chỉ đọc khoá từ
môi trường shell ⇒ «BỎ QUA — Thiếu ANTHROPIC_API_KEY», cổng kiểm lạc chủ đề trơ. BH11 PHÁT HIỆN
lệch nhưng chỉ `surveillance_scan.py` có đường TỰ VÁ (`tools/dong_bo_scanner_giam_sat.py`).

Bộ chốt này khoá ĐƯỜNG TỰ VÁ, không lặp phần phát hiện của BH11:
  • tự dò mọi tool của nguồn (không danh sách viết cứng);
  • luật (c) hỏi git theo ĐÚNG tệp nguồn tương ứng (ca #402 chỉ vá được nhờ luật này);
  • luật (b) vẫn giữ bản chạy có dòng riêng thật;
  • dark-analyst chỉ đồng bộ surveillance_scan (hợp đồng ESD02), tool khác để nguyên;
  • phạm vi bản chạy của công cụ vá TRÙNG phạm vi BH11 canh (đọc bằng AST, không khớp chuỗi);
  • tu_sua_chua gọi công cụ với --ap-dung mỗi phiên (công cụ không ai gọi thì không tồn tại — BH41).
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

THU_MUC_TOOLS = Path(__file__).resolve().parent
REPO = THU_MUC_TOOLS.parent
CONG_CU = THU_MUC_TOOLS / "dong_bo_scanner_giam_sat.py"
NGUON = "sync/skills/cap-nhat-chung-cu-y-khoa/tools"
CHAY_1 = "EBM-Dashboards/tools"
CHAY_2 = "EBM_MASTER/skill_assets"
DARK = "sync/skills/dark-analyst/tools"

# Dựng lại đúng hình dạng thay đổi của PR #402: một dòng có sẵn bị SỬA (không chỉ thêm dòng).
BAN_CU = 'import os\n\ndef lay_khoa():\n    key = os.getenv("ANTHROPIC_API_KEY", "")\n    return key\n'
BAN_MOI = ('import os\n\ndef lay_khoa():\n    key = os.getenv("ANTHROPIC_API_KEY", "") or _khoa_tu_kho()\n'
           '    return key\n\ndef _khoa_tu_kho():\n    return ""\n')


def _nap_cong_cu():
    spec = importlib.util.spec_from_file_location("_dbsgs_test_20261117", CONG_CU)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def _chay(goc: Path, *them: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CONG_CU), "--goc", str(goc), *them],
                          capture_output=True, text=True, encoding="utf-8", timeout=60, check=False)


def _ghi(goc: Path, rel: str, noi_dung: str) -> Path:
    p = goc / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(noi_dung, encoding="utf-8", newline="\n")
    return p


def _git(goc: Path, *tham_so: str) -> None:
    subprocess.run(["git", "-C", str(goc), "-c", "user.name=t", "-c", "user.email=t@t",
                    "-c", "commit.gpgsign=false", *tham_so], capture_output=True, check=True, timeout=30)


def _dung_ca_402(goc: Path) -> tuple[Path, Path]:
    """Kho git tạm: nguồn commit BAN_CU rồi BAN_MOI; hai bản chạy (ngoài git) kẹt BAN_CU."""
    _git(goc, "init", "-q")
    _ghi(goc, f"{NGUON}/check_topic_relevance.py", BAN_CU)
    _git(goc, "add", "-A")
    _git(goc, "commit", "-qm", "ban cu")
    _ghi(goc, f"{NGUON}/check_topic_relevance.py", BAN_MOI)
    _git(goc, "add", "-A")
    _git(goc, "commit", "-qm", "PR 402: sua dong lay khoa")
    return (_ghi(goc, f"{CHAY_1}/check_topic_relevance.py", BAN_CU),
            _ghi(goc, f"{CHAY_2}/check_topic_relevance.py", BAN_CU))


def test_tu_do_moi_tool_cua_nguon_khong_viet_cung(tmp_path):
    for ten in ("a_moi_them.py", "check_topic_relevance.py", "surveillance_scan.py"):
        _ghi(tmp_path, f"{NGUON}/{ten}", "x\n")
    _ghi(tmp_path, f"{NGUON}/khong_phai_py.txt", "x\n")
    cap = {(n.as_posix(), d.as_posix()) for n, d in _nap_cong_cu().cac_cap_dong_bo(tmp_path)}
    mong = set()
    for ten in ("a_moi_them.py", "check_topic_relevance.py", "surveillance_scan.py"):
        mong |= {(f"{NGUON}/{ten}", f"{CHAY_1}/{ten}"), (f"{NGUON}/{ten}", f"{CHAY_2}/{ten}")}
    mong.add((f"{NGUON}/surveillance_scan.py", f"{DARK}/surveillance_scan.py"))
    assert cap == mong


def test_ca_402_ban_chay_tut_hau_chay_kho_bao_lech_khong_ghi(tmp_path):
    c1, c2 = _dung_ca_402(tmp_path)
    kq = _chay(tmp_path)
    assert kq.returncode == 1, kq.stdout
    assert kq.stdout.count("🟡") == 2, kq.stdout
    assert c1.read_text(encoding="utf-8") == BAN_CU
    assert c2.read_text(encoding="utf-8") == BAN_CU


def test_ca_402_ap_dung_tu_va_ca_hai_ban_chay_nho_luat_c_theo_dung_tep(tmp_path):
    c1, c2 = _dung_ca_402(tmp_path)
    kq = _chay(tmp_path, "--ap-dung")
    assert kq.returncode == 0, kq.stdout
    assert c1.read_text(encoding="utf-8") == BAN_MOI
    assert c2.read_text(encoding="utf-8") == BAN_MOI
    assert "ĐÃ chép đè" in kq.stdout
    # Chạy lại: đã khớp ⇒ im lặng với --im-khi-on.
    kq2 = _chay(tmp_path, "--im-khi-on")
    assert kq2.returncode == 0 and kq2.stdout == ""


def test_ban_chay_co_dong_rieng_that_duoc_giu_lai(tmp_path):
    c1, _ = _dung_ca_402(tmp_path)
    ban_va = BAN_CU + "# ban va chi co o ban chay, chua hoi nguon\n"
    c1.write_text(ban_va, encoding="utf-8", newline="\n")
    kq = _chay(tmp_path, "--ap-dung")
    assert kq.returncode == 1, kq.stdout
    assert c1.read_text(encoding="utf-8") == ban_va
    assert "RIÊNG" in kq.stdout and "ban va chi co o ban chay" in kq.stdout


def test_nguon_bao_trum_chep_de_khong_can_git(tmp_path):
    _ghi(tmp_path, f"{NGUON}/build_library.py", "a\nb\n")
    dich = _ghi(tmp_path, f"{CHAY_1}/build_library.py", "a\n")
    kq = _chay(tmp_path, "--ap-dung")
    assert kq.returncode == 0, kq.stdout
    assert dich.read_text(encoding="utf-8") == "a\nb\n"


def test_dark_analyst_chi_dong_bo_surveillance_tool_khac_de_nguyen(tmp_path):
    _ghi(tmp_path, f"{NGUON}/surveillance_scan.py", "s\nt\n")
    _ghi(tmp_path, f"{NGUON}/verify_dashboard.py", "a\nb\n")
    dark_ss = _ghi(tmp_path, f"{DARK}/surveillance_scan.py", "s\n")
    dark_vd = _ghi(tmp_path, f"{DARK}/verify_dashboard.py", "a\n")
    kq = _chay(tmp_path, "--ap-dung")
    assert kq.returncode == 0, kq.stdout
    assert dark_ss.read_text(encoding="utf-8") == "s\nt\n"
    assert dark_vd.read_text(encoding="utf-8") == "a\n", "dark-analyst là skill khác — chỉ hợp đồng ESD02 được chạm"


def test_khong_co_ban_chay_khong_phai_loi(tmp_path):
    _ghi(tmp_path, f"{NGUON}/verify_dashboard.py", "a\n")
    kq = _chay(tmp_path)
    assert kq.returncode == 0, kq.stdout
    assert "⚪" in kq.stdout


def test_thieu_thu_muc_nguon_ma_2(tmp_path):
    assert _chay(tmp_path).returncode == 2


def test_thu_muc_nguon_khong_co_tool_ma_2(tmp_path):
    _ghi(tmp_path, f"{NGUON}/ghi_chu.md", "x\n")
    assert _chay(tmp_path).returncode == 2


def _chuoi_trong_list(nut: ast.AST) -> list[str]:
    return [p.value for p in getattr(nut, "elts", []) if isinstance(p, ast.Constant) and isinstance(p.value, str)]


def test_pham_vi_ban_chay_trung_dung_pham_vi_bh11_canh():
    """Bộ PHÁT HIỆN (BH11) và bộ TỰ VÁ phải canh cùng những nơi — thêm nơi ở một bên mà quên bên kia
    là tái sinh đúng khoảng hở 17/11. Đọc danh sách NOI của BH11 bằng AST (dòng thi hành, không khớp chú thích)."""
    cay = ast.parse((THU_MUC_TOOLS / "chot_hoi_quy_bai_hoc.py").read_text(encoding="utf-8"))
    ham = next(n for n in cay.body if isinstance(n, ast.FunctionDef) and n.name.startswith("bh11_"))
    gan_noi = next(n for n in ast.walk(ham) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "NOI" for t in n.targets))
    noi_bh11 = {s.rsplit("/", 1)[0] for s in _chuoi_trong_list(gan_noi.value)}
    noi_bh11.discard(NGUON)
    assert noi_bh11 == {p.as_posix() for p in _nap_cong_cu().THU_MUC_CHAY}


def test_tu_sua_chua_goi_cong_cu_voi_ap_dung_moi_phien():
    cay = ast.parse((THU_MUC_TOOLS / "tu_sua_chua.py").read_text(encoding="utf-8"))
    gan = next(n for n in cay.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "VIEC_MAY" for t in n.targets))
    lenh_sua = [_chuoi_trong_list(muc.elts[2]) for muc in gan.value.elts
                if isinstance(muc, ast.Tuple) and len(muc.elts) >= 3]
    assert any("tools/dong_bo_scanner_giam_sat.py" in lenh and "--ap-dung" in lenh for lenh in lenh_sua)


def test_tool_cua_su_co_nam_trong_pham_vi_tren_repo_that():
    cap = {(n.as_posix(), d.as_posix()) for n, d in _nap_cong_cu().cac_cap_dong_bo(REPO)}
    assert (f"{NGUON}/check_topic_relevance.py", f"{CHAY_1}/check_topic_relevance.py") in cap
    assert (f"{NGUON}/verify_dashboard.py", f"{CHAY_1}/verify_dashboard.py") in cap
