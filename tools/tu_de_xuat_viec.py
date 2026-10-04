#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HỆ TỰ ĐỀ XUẤT VIỆC — đóng vòng meta: danh sách «nâng cấp tiếp theo» tự sinh (16/08/2026).

Vì sao: suốt các vòng «đề xuất để tôi chọn», danh sách việc luôn do NGƯỜI/agent
ngồi gom tay từ hàng chục bộ đếm. Các bộ đếm đã sống sẵn — mảnh thiếu là một chỗ
ĐỌC CHÚNG CÙNG LÚC và xếp hạng thành việc kèm LỆNH chạy ngay. Từ nay «hệ còn gì
để hoàn thiện?» có câu trả lời tự động, chạy được mỗi tối thứ Hai trong gói tuần
(cron "0 18 * * 1" — đổi từ sáng thứ Bảy ngày 17/08/2026).

Ba luật của bảng đề xuất — kế thừa toàn bộ bài học BH:
  1. Mỗi dòng phải có SỐ ĐO THẬT đứng sau (không đề xuất từ cảm giác).
  2. Việc thuộc thẩm quyền BÁC SĨ ghi rõ «👤» — máy không bao giờ tự làm nhóm đó.
  3. «Không còn gì» là kết quả hợp lệ và PHẢI in ra được — một bộ tự-đề-xuất
     không biết nói «đủ rồi» sẽ chế việc để tồn tại.

Dùng:  python3 tools/tu_de_xuat_viec.py [--gon]
Mã thoát: 0 luôn (bảng đề xuất là sản phẩm, không phải phán quyết).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
import importlib.util as _ilu_mea  # noqa: E402
_sp_mea = _ilu_mea.spec_from_file_location("_bst_tdxv", Path(__file__).resolve().parent / "ban_sao_tran.py")
_bst_mea = _ilu_mea.module_from_spec(_sp_mea)
_sp_mea.loader.exec_module(_bst_mea)
_GOC_MEA = _bst_mea.duong_goc("medical-ebm-automation", REPO) or (REPO / "medical-ebm-automation")
# Vá 14/09/2026 (workflow kiểm tra toàn diện): mục ⑥ trước đây hardcode
# "~/.ebm-venv/bin/python" (bố cục POSIX) để chạy study_readiness.py — trên
# Windows venv có bố cục "Scripts\python.exe", không có "bin/python", nên
# subprocess.run ném FileNotFoundError, bị _chay() bắt và trả CHUỖI RỖNG một
# cách IM LẶNG (không log, không cảnh báo). Hệ quả: mục ⑥ (nhắc bác sĩ về đề
# tài C1a — G0 chờ 5 cờ FINER, hoặc 0/4 cổng cứng có chữ ký) vĩnh viễn vắng
# mặt khỏi bảng đề xuất trên Windows — một trong hai máy chính bác sĩ dùng.
# Khuôn theo đúng VENV_PY đã dùng ở audit_ebm_system.py/upgrade_verify.py/
# chot_hoi_quy_bai_hoc.py — không phát minh cách mới.
VENV_PY = (
    Path.home() / ".ebm-venv" / "Scripts" / "python.exe"
    if os.name == "nt"
    else Path.home() / ".ebm-venv" / "bin" / "python"
)
DASH = _bst_mea.duong_goc("EBM-Dashboards", REPO) or (REPO / "EBM-Dashboards")


# Giác quan CHẾT (T4-08, 20/09/2026): `_chay` trả chuỗi RỖNG khi công cụ không chạy được và các regex phía trên
# không khớp chuỗi rỗng ⇒ không dòng nào được thêm ⇒ cuối bảng in «🟢 KHÔNG CÒN VIỆC NÀO» — sự im lặng của một cảm
# biến hỏng bị đọc thành «đủ rồi». Nay mỗi lệnh chạy hỏng (không khởi động được / quá giờ / traceback) được GHI
# NHẬN, và bảng không bao giờ in xanh khi còn giác quan không đo được.
_SO_GIAC_QUAN = {"chay": 0}
_GIAC_QUAN_CHET: list[str] = []
# Dòng THÔNG TIN (ⓘ) — sự kiện đã qua, không còn việc: in riêng, KHÔNG tính vào danh sách việc (để «🟢 không còn việc» vẫn in được).
_THONG_TIN: list[str] = []


def _dong_kiem_ke_gradeby(out: str) -> str | None:
    """Dòng ⓘ kiểm kê quý gradeBy từ đầu ra `kiem_phan_hang.py`; None khi 0 item hoặc không đọc được số.

    Bác sĩ chấp nhận là khoảng trống đã biết (03/10/2026, «5b») nên đây là THÔNG TIN, không phải việc 👤.
    Không đọc được số (công cụ hỏng) ⇒ None; giác quan chết đã được `_chay` ghi nhận riêng."""
    m = re.search(r"(\d+) CHƯA khai `gradeBy` \((\d+)", out or "")
    if not m or not int(m.group(1)):
        return None
    return (f"Kiểm kê quý gradeBy: {m.group(1)} item chưa khai ({m.group(2)} đang apply) — KHOẢNG TRỐNG ĐÃ BIẾT, "
            "bác sĩ chấp nhận 03/10/2026; 'na' là trung thực, số tự giảm khi cập nhật chủ đề "
            "(xem: python3 tools/de_xuat_gradeby.py)")


def _ghi_chet(lenh: list[str], ly_do: str) -> None:
    ten = " ".join(str(x) for x in lenh[1:3])[:70] or str(lenh[0])
    _GIAC_QUAN_CHET.append(f"{ten} ({ly_do})")


def _chay(lenh: list[str], giay: int = 120, cwd: Path | None = None) -> str:
    _SO_GIAC_QUAN["chay"] += 1
    try:
        # encoding tường minh: Windows mặc định cp1252 → thread đọc output chết
        # UnicodeDecodeError với tiếng Việt/UTF-8 (lớp lỗi đã ghi ở CLAUDE.md)
        r = subprocess.run(lenh, capture_output=True, text=True, timeout=giay,
                           cwd=cwd or REPO, encoding="utf-8", errors="replace")
        ra = (r.stdout or "") + (r.stderr or "")
        if "Traceback (most recent call last)" in ra:
            _ghi_chet(lenh, "công cụ văng traceback")
        return ra
    except subprocess.TimeoutExpired:
        _ghi_chet(lenh, f"quá {giay}s")
        return ""
    except (OSError, subprocess.SubprocessError):
        _ghi_chet(lenh, "không chạy được")
        return ""


def _owner_repo_tu_remote(duong_repo: Path) -> str:
    """«owner/repo» suy từ `git remote get-url origin` — chấp nhận https/ssh/URL proxy cục bộ
    (phiên Cloud trỏ `http://…@127.0.0.1:…/git/owner/repo`). Không suy được ⇒ chuỗi rỗng."""
    try:
        r = subprocess.run(["git", "-C", str(duong_repo), "remote", "get-url", "origin"],
                           capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return ""
    m = re.search(r"([\w.-]+)/([\w.-]+?)(?:\.git)?/?$", (r.stdout or "").strip())
    return f"{m.group(1)}/{m.group(2)}" if m else ""


# Tên nhánh hợp lệ để đưa vào truy vấn (không khoảng trắng/ký tự lạ) — chặn đầu ra lỗi của gh/API
# bị đọc nhầm thành tên nhánh.
_TEN_NHANH_HOP_LE = re.compile(r"[\w.][\w./-]*")


def _nhanh_khai_bao(duong_repo: Path) -> str:
    """Nấc lùi CUỐI: nhánh chính khai báo theo CLAUDE.md — MỘT nguồn duy nhất là
    `kiem_cay_lam_viec.NHANH_CHINH` (khoá theo tên repo suy từ remote, lùi về tên thư mục)."""
    try:
        sp = _ilu_mea.spec_from_file_location(
            "_kcl_tdxv", Path(__file__).resolve().parent / "kiem_cay_lam_viec.py")
        kcl = _ilu_mea.module_from_spec(sp)
        sp.loader.exec_module(kcl)
        bang = dict(kcl.NHANH_CHINH)
    except Exception:  # noqa: BLE001 — thiếu nguồn khai báo ⇒ không có nấc lùi, không đoán
        return ""
    ten = _owner_repo_tu_remote(duong_repo).split("/")[-1] or duong_repo.resolve().name
    return bang.get(ten, "")


def _nhanh_mac_dinh(duong_repo: Path, urlopen=None, co_gh: bool | None = None) -> str:
    """Nhánh MẶC ĐỊNH của repo để lọc cảm biến CI (26/09/2026).

    Vì sao: cả hai workflow chạy trên MỌI nhánh (`push: branches: ["**"]`), nên «run hoàn tất mới
    nhất» sau mỗi lần merge gần như luôn là run của nhánh `claude/*` được đẩy lên CÙNG commit — đo
    thật 26/09: run #838 (claude/*, success) che run #837 (nhánh mặc định repo y khoa, FAILURE).
    Thứ tự dò: (a) `git symbolic-ref refs/remotes/origin/HEAD` (hỏng thật trên clone Cloud ở CẢ HAI
    repo) → (b) `gh repo view` rồi API `GET /repos/{owner}/{repo}` → `default_branch` → (c) nhánh
    chính khai báo (`kiem_cay_lam_viec.NHANH_CHINH`). Hỏng hết ⇒ «» (bên gọi ghi giác quan chết ⇒ ⚪).
    TUYỆT ĐỐI không viết cứng «main» (repo y khoa CÓ origin/main nhưng đó là nhánh bỏ) và không bao
    giờ để bên gọi lùi về truy vấn KHÔNG lọc nhánh.

    Rào origin/HEAD CŨ (rà phản biện 26/09/2026): `origin/HEAD` là bản chụp CỤC BỘ lúc clone, git
    không tự cập nhật khi GitHub đổi nhánh mặc định — một clone cũ của repo y khoa có thể còn trỏ
    `origin/main` (nhánh bỏ, run cuối có thể xanh ⇒ xanh giả). Nên (a) chỉ được dùng NGAY khi repo
    không có khai báo hoặc KHỚP khai báo; lệch khai báo ⇒ hỏi nguồn có thẩm quyền (gh/API); nguồn
    đó cũng hỏng ⇒ «» (hai nguồn cục bộ mâu thuẫn, không đoán bên nào đúng).
    """
    import urllib.request
    khai_bao = _nhanh_khai_bao(duong_repo)
    lech_khai_bao = ""
    try:
        r = subprocess.run(["git", "-C", str(duong_repo), "symbolic-ref", "--quiet", "--short",
                            "refs/remotes/origin/HEAD"], capture_output=True, text=True, timeout=10,
                           encoding="utf-8", errors="replace")
        ra = (r.stdout or "").strip()
        if r.returncode == 0 and ra.startswith("origin/") and _TEN_NHANH_HOP_LE.fullmatch(ra[7:]):
            if not khai_bao or ra[7:] == khai_bao:
                return ra[7:]
            lech_khai_bao = ra[7:]
    except (OSError, subprocess.SubprocessError):
        pass
    if co_gh is None:
        co_gh = bool(shutil.which("gh"))
    if co_gh:
        try:
            r = subprocess.run(["gh", "repo", "view", "--json", "defaultBranchRef", "--jq",
                                ".defaultBranchRef.name"], capture_output=True, text=True, timeout=30,
                               cwd=duong_repo, encoding="utf-8", errors="replace")
            ra = (r.stdout or "").strip()
            if r.returncode == 0 and _TEN_NHANH_HOP_LE.fullmatch(ra):
                return ra
        except (OSError, subprocess.SubprocessError):
            pass
    repo = _owner_repo_tu_remote(duong_repo)
    if repo:
        try:
            mo = urlopen or urllib.request.urlopen
            with mo(urllib.request.Request(f"https://api.github.com/repos/{repo}",
                                           headers={"Accept": "application/vnd.github+json"}),
                    timeout=20) as r:
                du_lieu = json.loads(r.read().decode("utf-8"))
            ra = str(du_lieu.get("default_branch") or "").strip()
            if _TEN_NHANH_HOP_LE.fullmatch(ra):
                return ra
        except Exception:  # noqa: BLE001 — mạng/giới hạn nhịp/JSON lạ ⇒ thử nấc sau
            pass
    if lech_khai_bao:
        return ""   # origin/HEAD cục bộ ≠ khai báo, không nguồn thẩm quyền nào phân xử ⇒ không đo được
    return khai_bao


def doc_ci_qua_api(duong_repo: Path, wf: str, nhanh: str, urlopen=None) -> str:
    """Phán quyết run mới nhất của workflow `wf` TRÊN NHÁNH `nhanh` qua GitHub REST API công khai —
    đường LÙI khi máy không có `gh` (phiên Cloud: đo 26/09/2026, `gh` vắng nên cảm biến CI luôn ⚪
    «không đo được» dù API đọc được cả hai repo). Trả `conclusion` («success»/«failure»/…) của run
    ĐÃ HOÀN TẤT gần nhất (`status=completed`; sửa 26/09/2026: bản đầu lấy run mới nhất kể cả đang
    chạy ⇒ `conclusion=null` và bảng báo 🟡 «rỗng» mỗi lần vừa push/merge).
    Lọc `branch=` (26/09/2026): không lọc thì run xanh của nhánh `claude/*` che nhánh mặc định đỏ.
    Phòng thủ thêm: run trả về mang `head_branch` khác `nhanh` ⇒ không đo được. `nhanh` rỗng ⇒ không
    đo được, KHÔNG BAO GIỜ gửi truy vấn không lọc nhánh.
    Không đọc được (mạng, repo riêng tư, giới hạn nhịp) ⇒ ghi GIÁC QUAN CHẾT, trả «» — không bao giờ
    đoán «success» (BH08)."""
    import urllib.parse
    import urllib.request
    _SO_GIAC_QUAN["chay"] += 1
    if not nhanh:
        _ghi_chet(["api.github.com", wf], "không có nhánh mặc định để lọc — không đọc run không lọc nhánh")
        return ""
    repo = _owner_repo_tu_remote(duong_repo)
    if not repo:
        _ghi_chet(["api.github.com", wf], "không suy được owner/repo")
        return ""
    tham_so = urllib.parse.urlencode({"status": "completed", "per_page": 1, "branch": nhanh})
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{wf}/runs?{tham_so}"
    try:
        mo = urlopen or urllib.request.urlopen
        with mo(urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"}),
                timeout=20) as r:
            du_lieu = json.loads(r.read().decode("utf-8"))
        run = (du_lieu.get("workflow_runs") or [None])[0]
    except Exception as exc:  # noqa: BLE001 — mọi lỗi đều là «không đo được»
        _ghi_chet(["api.github.com", wf], f"không đọc được ({type(exc).__name__})")
        return ""
    if not run:
        _ghi_chet(["api.github.com", wf], f"chưa có run nào hoàn tất trên nhánh {nhanh}")
        return ""
    if run.get("head_branch") != nhanh:
        _ghi_chet(["api.github.com", wf], f"run trả về nhánh «{run.get('head_branch')}» ≠ «{nhanh}»")
        return ""
    return str(run.get("conclusion") or "")


# Phán quyết hợp lệ của một run ĐÃ HOÀN TẤT (`conclusion` của GitHub Actions) — để phân biệt CÂU TRẢ LỜI của gh với
# THÔNG BÁO LỖI của gh. `_chay` gộp stderr vào stdout, nên «error connecting to api.github.com» từng bị tách thành
# conclusion=«error», nhánh=«connecting» rồi in «run trả về nhánh «connecting»» (đo 28–30/09/2026 trên máy Windows).
_KET_LUAN_CI = frozenset({"success", "failure", "cancelled", "skipped", "timed_out", "action_required",
                          "neutral", "stale", "startup_failure"})
# Lỗi KẾT NỐI của gh — đáng thử lại: DNS nội bộ hay trượt lần phân giải ĐẦU sau khi bộ đệm nguội (đo 30/09: lần 1 lỗi sau
# 12 s, lần 2 được, các lần sau < 1 s). Lỗi khác (token hỏng, HTTP 4xx, gh không chạy) thử lại vô ích ⇒ lùi sang API.
_LOI_KET_NOI_GH = re.compile(r"error connecting|could not resolve|no such host|dial tcp|timed? ?out|"
                             r"connection (?:reset|refused)|TLS handshake|unexpected EOF", re.I)
_NGHI_THU_LAI_GH = 2.0           # giây nghỉ trước lần thử thứ hai
# Repo trước đã trượt kết nối ở MỌI lần thử ⇒ repo sau chỉ thử một lần: bên gọi (`xuat_trang_thai_cloud`) cho cả công cụ
# 90 s, mà mỗi lần gh trượt DNS mất ~12 s.
_MANG_GH = {"hong": False}


def _doc_tra_loi_gh(out: str) -> tuple[bool, str, str]:
    """(đây có phải CÂU TRẢ LỜI của `gh run list` không, conclusion, nhánh). Rỗng = chưa có run hoàn tất trên nhánh —
    vẫn là câu trả lời. Mọi dạng khác (nhiều dòng, nhiều chữ, conclusion lạ) là thông báo lỗi, KHÔNG đọc thành nhánh."""
    dong = [d for d in out.strip().splitlines() if d.strip()]
    if not dong:
        return True, "", ""
    phan = dong[0].split()
    if len(dong) == 1 and len(phan) == 2 and phan[0] in _KET_LUAN_CI and _TEN_NHANH_HOP_LE.fullmatch(phan[1]):
        return True, phan[0], phan[1]
    return False, "", ""


def doc_ci_mot_repo(ten_ci: str, cwd_ci: Path, wf: str, co_gh: bool | None = None,
                    urlopen=None, ngu=None) -> tuple[str, str]:
    """Phán quyết CI của NHÁNH MẶC ĐỊNH một repo → (conclusion hoặc «», tên nhánh hoặc «»).

    «» nghĩa là KHÔNG ĐO ĐƯỢC (đã ghi giác quan chết) — bảng hiện ⚪/🟡, không bao giờ xanh.

    Vá 30/09/2026 (BH134): có `gh` mà gọi trượt MỘT nhịp là ⚪ ngay — không thử lại, không lùi sang API công khai, còn
    chữ trong thông báo lỗi bị đọc thành tên nhánh. Nay: lỗi kết nối ⇒ thử lại một lần; gh hỏng vì lý do khác ⇒ lùi
    sang `doc_ci_qua_api`; mọi đường hỏng vẫn là «» kèm ĐÚNG nguyên nhân, và vẫn chỉ tính MỘT giác quan.
    """
    if co_gh is None:
        co_gh = bool(shutil.which("gh"))
    nhanh = _nhanh_mac_dinh(cwd_ci, urlopen=urlopen, co_gh=co_gh)
    if not nhanh:
        _SO_GIAC_QUAN["chay"] += 1
        _ghi_chet(["CI", ten_ci], "không xác định được nhánh mặc định (symbolic-ref, gh/API, khai báo "
                                  "đều hỏng) — KHÔNG đọc run không lọc nhánh")
        return "", ""
    if not co_gh:
        return doc_ci_qua_api(cwd_ci, wf, nhanh, urlopen=urlopen), nhanh
    so_chet, dem = len(_GIAC_QUAN_CHET), _SO_GIAC_QUAN["chay"]
    nhan = ["gh", f"run list · CI {ten_ci}"]
    loi_gh, loi_mang, lan = "", False, 0
    for lan in range(1 if _MANG_GH["hong"] else 2):
        if lan:
            (ngu or time.sleep)(_NGHI_THU_LAI_GH)
        chet_truoc = len(_GIAC_QUAN_CHET)
        out = _chay(["gh", "run", "list", "--workflow", wf, "--branch", nhanh, "--limit", "1", "--status", "completed",
                     "--json", "conclusion,headBranch", "--jq",
                     ".[0].conclusion + \" \" + .[0].headBranch"], giay=30, cwd=cwd_ci)
        khong_chay = len(_GIAC_QUAN_CHET) > chet_truoc       # `_chay` tự ghi: quá giờ / không khởi động được / traceback
        la_tra_loi, kq_ci, dau = (False, "", "") if khong_chay else _doc_tra_loi_gh(out)
        if la_tra_loi:
            _SO_GIAC_QUAN["chay"] = dem + 1                  # MỘT giác quan, dù thử mấy lần
            if dau != nhanh:
                _ghi_chet(nhan, f"run trả về nhánh «{dau}» ≠ «{nhanh}»" if dau
                          else f"chưa có run nào hoàn tất trên nhánh {nhanh}")
                return "", nhanh
            return kq_ci, nhanh
        if khong_chay:
            loi_gh = _GIAC_QUAN_CHET[-1]
            loi_mang = "quá " in loi_gh                      # treo hết 30 s ⇒ coi như mạng; «không chạy được» ⇒ gh hỏng
            break                                            # đằng nào cũng không thử lại gh
        loi_gh = (out.strip().splitlines() or ["?"])[0][:120]
        loi_mang = bool(_LOI_KET_NOI_GH.search(out))
        if not loi_mang:
            break                                            # token hỏng / HTTP 4xx: thử lại vô ích ⇒ lùi sang API
    del _GIAC_QUAN_CHET[so_chet:]
    _SO_GIAC_QUAN["chay"] = dem
    if loi_mang:
        # Cùng máy chủ api.github.com vừa trượt ⇒ không gọi API thêm (chỉ tốn thêm ~12 s); ghi ĐÚNG nguyên nhân.
        _MANG_GH["hong"] = True
        _SO_GIAC_QUAN["chay"] += 1
        _ghi_chet(nhan, f"gh không gọi được GitHub sau {lan + 1} lần ({loi_gh}) — mạng/DNS, KHÔNG phải CI đỏ")
        return "", nhanh
    kq = doc_ci_qua_api(cwd_ci, wf, nhanh, urlopen=urlopen)  # tự đếm 1 giác quan, tự ghi chết nếu cũng hỏng
    if not kq and len(_GIAC_QUAN_CHET) > so_chet:
        _GIAC_QUAN_CHET[-1] += f" — trước đó gh lỗi: {loi_gh}"
    return kq, nhanh


def la_phien_cloud() -> bool:
    """Phiên claude.ai/code (container Cloud) — nơi dữ liệu OneDrive/log máy thật vắng mặt."""
    return os.environ.get("CLAUDE_CODE_REMOTE", "").strip().lower() == "true"


def de_xuat_plugin(rc: int, cloud: bool) -> list[tuple[int, str, str, str]]:
    """Dòng đề xuất từ mã thoát của `kiem_plugin_day_du.py` (26/09/2026, mục ⑨).

    Máy thật: giữ nguyên hành vi cũ (rc=2 thiếu ⇒ 🟠, rc=1 lệch nhẹ ⇒ 🟡, cả hai gợi ý nghi thức
    sau-cập-nhật). Phiên CLOUD: plugin được cài BẢN MỚI NHẤT mỗi phiên (không ghim phiên bản) nên
    lệch phiên bản so với mốc là thường trực — KHÔNG sinh mục 🤖 nào; và KHÔNG BAO GIỜ gợi ý
    `sau_cap_nhat_plugin.py` (trên Cloud nó từng ghi đè DANH-MUC/INDEX gộp hai máy đang track bằng
    dữ liệu một máy). rc=2 (THIẾU plugin) trên Cloud vẫn cảnh báo, gợi ý cài lại plugin phiên Cloud.
    """
    if cloud:
        if rc == 2:
            return [(1, "🤖", "Kho plugin phiên Cloud THIẾU so với mốc chuẩn — xem chi tiết rồi cài lại "
                     "plugin thiếu (KHÔNG chạy nghi thức sau-cập-nhật trên Cloud: nó ghi đè danh mục "
                     "gộp hai máy đang track)",
                     "python3 tools/kiem_plugin_day_du.py && python3 tools/cai_plugin_phien_cloud.py --ap-dung")]
        return []
    if rc == 2:
        return [(1, "🤖", "Kho plugin THIẾU so với mốc chuẩn — xem chi tiết rồi "
                 "chạy nghi thức sau-cập-nhật (hoặc cài lại plugin thiếu)",
                 "python3 tools/kiem_plugin_day_du.py && python3 tools/sau_cap_nhat_plugin.py --ghi-moc")]
    if rc == 1:
        return [(2, "🤖", "Plugin đổi phiên bản/kho lệch nhẹ so với mốc — chạy "
                 "nghi thức sau-cập-nhật để danh mục+trang tra+mốc khớp thực tế",
                 "python3 tools/sau_cap_nhat_plugin.py --ghi-moc")]
    return []


# Nguồn mà «hỏng kéo dài» là việc gấp hơn (ưu tiên 1): ba nguồn khám phá lõi + nguồn an toàn thuốc của engine.
_NGUON_THIET_YEU = frozenset({"pubmed", "europepmc", "crossref", "openfda", "feed_fda_medwatch", "feed_fda_recalls",
                              "feed_mhra_dsu"})


def giac_quan_nguon_hong_keo_dai(db: Path) -> list[tuple[int, str, str]]:
    """Nguồn engine báo «hỏng kéo dài» ở lượt live gần nhất có số đo nguồn — [(ưu tiên, mô tả, lệnh)] (01/10/2026).

    Vì sao (BH145): RSS NEJM bị Cloudflare chặn 9/9 lần gọi từ lượt 07/09 tới 29/09, kho không nhận bài NEJM nào, mà lượt
    nào cũng PASS — trạng thái lượt cố ý không đổi vì một feed lẻ hỏng — nên chỉ lộ khi đo tay 30/09 (15 feed BMJ cũng hỏng
    từ 13/08 như vậy). Engine y khoa ghi `source_health["hong_keo_dai"]` (≥ 3 lượt live liền, trải ≥ 7 ngày) vào
    `pipeline_runs.stats`; cảm biến này đưa nó lên hòm việc. CHỈ ĐỌC (sqlite `mode=ro`), không đổi gì.
    - CSDL vắng/không đọc được ⇒ giác quan chết (⚪ — bảng không in «đủ rồi»), KHÔNG phải «không nguồn nào hỏng».
    - Lượt live mới nhất có số đo do engine CŨ ghi (chưa có khoá) ⇒ [] — chưa có số đo thì không báo động.
    - `hong_keo_dai` None (engine không đọc được lịch sử) ⇒ một dòng «không đo được».
    Ưu tiên: nguồn lõi/an toàn thuốc 1 · nguồn khác 2 · đã có ghi chú chấp nhận trong lượt (vd Scopus) 3.
    """
    import sqlite3

    _SO_GIAC_QUAN["chay"] += 1
    if not db.exists():
        _ghi_chet(["", "nguồn hỏng kéo dài"], "không thấy CSDL engine data/medical_ebm.db ở cây này")
        return []
    try:
        con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
        try:
            dong_csdl = con.execute("SELECT stats FROM pipeline_runs WHERE mode = 'live' AND finished_at IS NOT NULL "
                                    "ORDER BY started_at DESC, id DESC LIMIT 20").fetchall()
        finally:
            con.close()
    except sqlite3.Error as exc:
        _ghi_chet(["", "nguồn hỏng kéo dài"], f"không đọc được CSDL engine ({type(exc).__name__})")
        return []
    lenh = "cd medical-ebm-automation && python tools/do_mang_nguon.py  # đo đường mạng tới từng nguồn"
    for (stats,) in dong_csdl:
        try:
            sh = (json.loads(stats) if isinstance(stats, str) else (stats or {})).get("source_health") or {}
        except (ValueError, AttributeError):
            continue
        if not isinstance(sh, dict) or not isinstance(sh.get("sources"), dict):
            continue  # lượt nạp sẵn bản ghi (vd lượt lấy bù) — không có số đo nguồn
        if "hong_keo_dai" not in sh:
            return []
        hong = sh["hong_keo_dai"]
        if hong is None:
            return [(2, "Engine KHÔNG đo được nguồn hỏng kéo dài ở lượt live gần nhất "
                     f"({sh.get('hong_keo_dai_loi') or 'không rõ lỗi'}) — không phải «không có nguồn nào hỏng»",
                     "xem medical-ebm-automation/data/archive/launchd_weekly.log")]
        ra: list[tuple[int, str, str]] = []
        for ten, ct in sorted((hong or {}).items()):
            if not isinstance(ct, dict):
                continue
            kieu = ",".join(sorted(ct.get("kieu_duong_mang") or {})) or "chưa phân loại"
            ghi_chu = ct.get("da_co_ghi_chu")
            uu = 3 if ghi_chu else (1 if ten in _NGUON_THIET_YEU else 2)
            mo_ta = (f"Nguồn {ten} HỎNG KÉO DÀI: {ct.get('so_luot_lien')} lượt live liền từ {ct.get('hong_tu')} "
                     f"({ct.get('so_ngay')} ngày, kiểu: {kieu}) — lượt vẫn PASS nên không tự lộ; đo lại đường mạng, "
                     "chặn ở biên/mạng thì chuyển nguồn sang lane không phụ thuộc mạng (Crossref/Europe PMC)")
            if ghi_chu:
                mo_ta += f" · đã có ghi chú chấp nhận {ghi_chu}"
            ra.append((uu, mo_ta, lenh))
        return ra
    return []


def giac_quan_url_chan_bot(dash_dir: Path) -> list[tuple[int, str, str]]:
    """URL miền chặn bot (vd www.fda.gov) đang được dashboard trích mà THIẾU/SẮP HẾT HẠN bằng chứng trình duyệt (02/10/2026).

    Thiếu bằng chứng ⇒ cổng `--strict-sources` chặn gói và (trước 02/10) dừng cả lô orchestrator. Việc 👤: Claude mở trang, bác sĩ TỰ
    bấm xác nhận chống bot, Claude đọc tiêu đề rồi ghi sổ (`tools/xac_nhan_trinh_duyet.py`). Ngoại tuyến. Vắng EBM-Dashboards/
    hoặc công cụ hỏng ⇒ giác quan chết (⚪), KHÔNG phải «không có URL chờ»."""
    _SO_GIAC_QUAN["chay"] += 1
    if not dash_dir.is_dir():
        _ghi_chet(["", "URL chặn bot"], "không có EBM-Dashboards/ ở cây này")
        return []
    try:
        sp = _ilu_mea.spec_from_file_location("_xntd_tdxv", Path(__file__).resolve().parent / "xac_nhan_trinh_duyet.py")
        xn = _ilu_mea.module_from_spec(sp)
        sp.loader.exec_module(xn)
        cho = xn.can_xac_nhan(xn.quet(xn.nap_cong(), dash_dir))
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra
        _ghi_chet(["", "URL chặn bot"], f"lỗi {type(exc).__name__}")
        return []
    if not cho:
        return []
    thieu = sum(1 for m in cho if m["trang_thai"] == "THIEU")
    return [(1 if thieu else 3, f"{len(cho)} URL miền chặn bot chờ bác sĩ xác nhận trên trình duyệt "
             f"({thieu} thiếu bằng chứng — cổng đang chặn gói; {len(cho) - thieu} sắp hết hạn) — ~1 phút/URL",
             "python3 tools/xac_nhan_trinh_duyet.py --huong-dan  # Claude mở trang, bác sĩ tự bấm xác nhận chống bot")]


def giac_quan_no_toan_van(dash_dir: Path, hom_nay: dt.date | None = None) -> list[tuple[int, str, str]]:
    """BẢO ĐẢM ĐỌC TOÀN VĂN (04/10/2026, bác sĩ: «Hãy xây dựng đảm bảo việc đọc toàn văn cho tôi»).

    Mục «Áp dụng ngay» CHƯA đọc toàn văn: ngoài sổ nợ hoặc nợ QUÁ HẠN ⇒ cổng `verify_dashboard` ĐANG CHẶN (ưu tiên 1); nợ trong hạn
    ⇒ nhắc kèm số ngày còn lại (ưu tiên 1 khi ≤ 7 ngày). Nguồn: `tools/so_toan_van.py` (dùng `bao_phu_cuc_bo`). Ngoại tuyến. Vắng
    kho/công cụ hỏng ⇒ giác quan chết (⚪), KHÔNG phải «đủ toàn văn»."""
    _SO_GIAC_QUAN["chay"] += 1
    hom_nay = hom_nay or dt.date.today()
    kho = dash_dir / "toan_van_oa"
    if not kho.is_dir():
        _ghi_chet(["", "bảo đảm toàn văn"], "không có kho toàn văn ở cây này")
        return []
    try:
        sp = _ilu_mea.spec_from_file_location("_stv_tdxv", Path(__file__).resolve().parent / "so_toan_van.py")
        stv = _ilu_mea.module_from_spec(sp)
        sp.loader.exec_module(stv)
        no = stv.phan_loai_no(stv.quet_muc(dash_dir, kho, hom_nay), stv.doc_so_no(dash_dir), hom_nay)
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra
        _ghi_chet(["", "bảo đảm toàn văn"], f"lỗi {type(exc).__name__}")
        return []
    ra = []
    chan = len(no["ngoai_so"]) + len(no["qua_han"])
    if chan:
        ra.append((1, f"{chan} mục «Áp dụng ngay» CHƯA đọc toàn văn — cổng ĐANG CHẶN (ngoài sổ nợ hoặc nợ quá hạn): đọc toàn văn, "
                      "bác sĩ xác nhận đã đọc, hoặc hạ «Cân nhắc»", "python3 tools/so_toan_van.py"))
    if no["trong_han"]:
        con = (dt.date.fromisoformat(no["han"]) - hom_nay).days
        ra.append((1 if con <= 7 else 2, f"{len(no['trong_han'])} mục «Áp dụng ngay» còn NỢ toàn văn — hạn {no['han']} (còn {con} "
                                         "ngày; quá hạn cổng chặn) — làn trình duyệt hoặc bác sĩ xác nhận đã đọc",
                   "python3 tools/so_toan_van.py"))
    return ra


def giac_quan_skill_tai_khoan(bundle: Path | None = None, hub: Path | None = None) -> list[tuple[int, str, str]]:
    """Skill của bác sĩ trên TÀI KHOẢN claude.ai cũ hơn repo (04/10/2026, BH163).

    Cowork · claude.ai web · Routine nạp bộ skill của TÀI KHOẢN — chỉ đổi khi bác sĩ tự tải lên; đẩy vào ~/.claude/skills hay thư
    mục chạy của Claude Desktop KHÔNG lan lên. Đo 04/10: 21/25 skill trên tài khoản đã cũ (cap-nhat-chung-cu-y-khoa v1.15.0 so với
    repo v1.53.0) mà không giác quan nào nhắc. So CẢ thư mục skill (`tools/dong_goi_skill_tai_khoan.py`). Skill «mới» (chưa từng
    lên) là TUỲ CHỌN ⇒ chỉ nhắc kèm, không đẩy ưu tiên. Máy không có bộ skill tài khoản / công cụ hỏng ⇒ giác quan chết (⚪), KHÔNG
    phải «đã khớp»."""
    _SO_GIAC_QUAN["chay"] += 1
    try:
        sp = _ilu_mea.spec_from_file_location("_dgsk_tdxv", Path(__file__).resolve().parent / "dong_goi_skill_tai_khoan.py")
        dg = _ilu_mea.module_from_spec(sp)
        sp.loader.exec_module(dg)
        nhom = dg.tom_tat(dg.danh_gia(hub or dg.HUB, bundle or dg.dcbb.tim_bundle_cloud(None)))
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng/thiếu bộ tài khoản phải hiện ra, không im lặng như «đã khớp»
        _ghi_chet(["", "skill tài khoản claude.ai"], f"{type(exc).__name__}: {str(exc)[:90]}")
        return []
    cap, moi, khac = nhom.get("cap_nhat", []), nhom.get("moi", []), nhom.get("khac_han", [])
    lenh = "python3 tools/dong_goi_skill_tai_khoan.py  # rồi mở CLAUDE_AI_SKILLS/DANH-SACH-TAI-LEN.md, bác sĩ tự tải ZIP lên claude.ai"
    if cap or khac:
        dau = ", ".join(cap[:3]) + ("…" if len(cap) > 3 else "")
        return [(2, f"{len(cap)} skill của bác sĩ trên TÀI KHOẢN claude.ai đã CŨ hơn repo ({dau}) — Cowork/claude.ai/Routine "
                    "đang chạy bản cũ; bác sĩ tải ZIP lên"
                    + (f"; {len(khac)} skill trùng tên mà KHÁC HẲN — bác sĩ quyết" if khac else "")
                    + (f"; thêm {len(moi)} skill chưa từng lên (tuỳ chọn)" if moi else ""), lenh)]
    if moi:
        return [(3, f"{len(moi)} skill trong repo chưa từng lên tài khoản claude.ai (tuỳ chọn — đọc mô tả trong danh sách)", lenh)]
    return []


def giac_quan_toan_van_the_tuan(queue_dir: Path, dash_dir: Path, hom_nay: dt.date | None = None) -> list[tuple[int, str, str]]:
    """Thẻ của gói tuần MỚI NHẤT (≤ 14 ngày) chỉ có TÓM TẮT vì bài không có bản OA (02/10/2026, bác sĩ yêu cầu).

    Đo W40: 5/7 thẻ «chỉ tóm tắt» ⇒ trần «Cân nhắc». Hầu hết nhà xuất bản chặn truy cập tự động (đo 02/10) nên đường duy nhất là làn
    CÓ NGƯỜI: Claude mở trình duyệt, bác sĩ tự vượt chặn/đăng nhập, Claude trích xuất có cấu trúc (`tools/doc_toan_van_co_nguoi.py`).
    Ngoại tuyến — chỉ soi kho `EBM-Dashboards/toan_van_oa/`. Vắng kho/công cụ hỏng ⇒ giác quan chết (⚪), KHÔNG phải «đủ toàn văn»."""
    _SO_GIAC_QUAN["chay"] += 1
    hom_nay = hom_nay or dt.date.today()
    if not queue_dir.is_dir():
        _ghi_chet(["", "toàn văn thẻ tuần"], "không có queue/ ở cây này")
        return []
    goi = sorted(queue_dir.glob("tuan-*.md"))
    if not goi:
        return []
    moi = goi[-1]
    if (hom_nay - dt.date.fromtimestamp(moi.stat().st_mtime)).days > 14:
        return []
    kho = dash_dir / "toan_van_oa"
    if not kho.is_dir():
        _ghi_chet(["", "toàn văn thẻ tuần"], "không có EBM-Dashboards/toan_van_oa ở cây này")
        return []
    try:
        sp = _ilu_mea.spec_from_file_location("_dtv_tdxv", Path(__file__).resolve().parent / "doc_toan_van_co_nguoi.py")
        dtv = _ilu_mea.module_from_spec(sp)
        sp.loader.exec_module(dtv)
        pmids = dtv.pmid_cua_queue(moi)
        bp = dtv.bao_phu_cuc_bo(pmids, kho, hom_nay)
        # Bộ trạng thái ĐÃ PHỦ lấy từ chính công cụ (một nguồn sự thật). 03/10/2026: «bac_si_da_doc_truc_tiep» — bác sĩ đã tự đọc
        # bài NXB cấm AI và ghi kết luận ⇒ không còn là việc treo, dù máy vẫn không có toàn văn.
        da_phu = set(dtv.TRANG_THAI_DA_PHU)
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra
        _ghi_chet(["", "toàn văn thẻ tuần"], f"lỗi {type(exc).__name__}")
        return []
    chua = [pm for pm, t in bp.items() if t not in da_phu and t != "khong_truy_cap"]
    if not chua:
        return []
    return [(3, f"{len(chua)}/{len(pmids)} thẻ gói {moi.stem} chỉ có TÓM TẮT (không có bản OA) — bài của NXB cho phép: Claude mở "
             f"trình duyệt, bác sĩ tự vượt chặn/đăng nhập; bài Elsevier/ADA (điều khoản cấm AI): bác sĩ đọc trực tiếp rồi ghi "
             f"`--bac-si-da-doc <PMID> --ghi-chu \"<kết luận>\" --ghi`; tới lúc đó thẻ giữ trần «Cân nhắc»",
             f"python3 tools/doc_toan_van_co_nguoi.py --queue queue/{moi.name}  # rồi --huong-dan")]


def giac_quan_lich_nen_theo_noi_chay(log_tuan: Path) -> list[tuple[int, str]]:
    """Bọc `giac_quan_lich_nen` theo nơi chạy (26/09/2026).

    Phiên Cloud: log thu thập chỉ nằm trên máy chạy lịch (ngoài git) — vắng tệp ở đây là «KHÔNG ĐO
    ĐƯỢC» (ghi giác quan chết ⇒ ⚪, bảng không in «đủ rồi»), KHÔNG phải «chưa từng chạy» (🔴 giả mỗi
    phiên Cloud). Trên máy thật, hoặc khi tệp CÓ mặt, giữ nguyên phán quyết của hàm gốc.
    """
    if la_phien_cloud() and not log_tuan.exists():
        _ghi_chet(["", "log giám sát tuần"], "phiên Cloud — log chỉ có trên máy chạy lịch")
        return []
    return giac_quan_lich_nen(log_tuan)


def giac_quan_lich_nen(log_tuan: Path,
                       hom_nay: dt.date | None = None,
                       ngay_lich_tuan: int = 0) -> list[tuple[int, str]]:
    """Kỳ lịch tuần có NỔ thật không — đọc dòng «KẾT THÚC … tổng thể=PASS» trong log.

    Trả [(ưu tiên, mô tả)]. Ba mức theo tuổi lượt PASS cuối: ≤7 ngày mà kỳ lịch
    tuần vừa qua không nổ → 2 (nhắc, dữ liệu vẫn tươi nhờ watchdog mở-phiên);
    8–10 ngày → 1 (chạy bù); >10 hoặc không đọc được lượt PASS nào → 0.
    Hàm thuần nhận đường log + ngày để chốt BH đột biến được bằng file tạm.

    `ngay_lich_tuan` (thứ trong tuần, T2=0…CN=6) PHẢI khớp cron THẬT của tác vụ
    `thu-thap-tuan-an-toan-thuoc` — mặc định 0 (thứ Hai, cron "0 18 * * 1").
    ĐÍNH CHÍNH 12/09/2026 (BH-lịch-nền): hằng số cũ viết cứng 5 (thứ Bảy) từ
    16/08/2026 — MỘT NGÀY TRƯỚC khi lịch đổi sang thứ Hai (17/08/2026) — và
    chưa từng được cập nhật theo, khiến hàm báo "KHÔNG nổ" GIẢ mỗi thứ Bảy dù
    kỳ thứ Hai thật đã chạy PASS đúng hẹn. Đổi từ hằng số ẩn sang tham số có
    tên, để lần đổi lịch sau chỉ cần sửa MỘT chỗ thay vì một số không giải
    thích được ý nghĩa.
    """
    hom_nay = hom_nay or dt.date.today()
    try:
        dong = log_tuan.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return [(0, "Log giám sát tuần KHÔNG ĐỌC ĐƯỢC — chưa từng chạy trên máy này?")]
    ngay_pass = None
    for ln in reversed(dong):
        if "KẾT THÚC" in ln and "tổng thể=PASS" in ln:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", ln)
            if m:
                ngay_pass = dt.date.fromisoformat(m.group(1))
            break
    if ngay_pass is None:
        return [(0, "Log tuần không có lượt PASS nào — giám sát chưa từng chạy trọn")]
    tuoi = (hom_nay - ngay_pass).days
    # ngày lịch tuần gần nhất đã qua; đúng ngày đó thì chính hôm nay
    ky_gan_nhat = hom_nay - dt.timedelta(days=(hom_nay.weekday() - ngay_lich_tuan) % 7)
    lo_ky = ngay_pass < ky_gan_nhat <= hom_nay
    if tuoi > 10:
        return [(0, f"Giám sát tuần quá hạn {tuoi} ngày (PASS cuối {ngay_pass}) — chạy bù NGAY")]
    if tuoi > 7:
        return [(1, f"Giám sát tuần {tuoi} ngày tuổi (PASS cuối {ngay_pass}) — kỳ lịch đã lỡ, chạy bù")]
    if lo_ky:
        return [(2, f"Kỳ lịch thứ Hai vừa qua KHÔNG nổ (máy không thức?) — dữ liệu vẫn tươi "
                    f"(PASS {ngay_pass}, {tuoi} ngày), nhưng lịch nền đang không tự chạy")]
    return []


def phan_loai_lich_nen(phat_hien: list[dict]) -> tuple[list[tuple[int, str, str, str]], list[str]]:
    """(việc 🛎, dòng thông tin ⓘ) từ phát hiện của `kiem_lich_nen.kiem()` (02/10/2026, HV-08).

    Kỳ CŨ đã lỡ mà kỳ sau đã chạy lại (uu ≥ 2) KHÔNG phải việc: «Run now» lúc này vô ích (kỳ sau đã chạy, vòng quét dùng con trỏ
    tăng dần nên không hở cửa sổ). Đo: «kỳ 14/09» lặp 28 lần ở 15 phiên. Gộp thành MỘT dòng ⓘ, không tính vào danh sách việc."""
    viec = [(p["uu"], "🛎", p["thong_diep"], "python3 tools/kiem_lich_nen.py  # rồi list_scheduled_tasks (bị xoá/tắt?) + «Run now»")
            for p in phat_hien if p["uu"] < 2]
    cu = sum(1 for p in phat_hien if p["uu"] >= 2)
    tt = [f"{cu} kỳ lịch nền CŨ đã lỡ nhưng kỳ sau đã chạy lại — không còn việc phải làm "
          "(chi tiết: python3 tools/kiem_lich_nen.py)"] if cu else []
    return viec, tt


def dem_commit_chua_co_tren_remote(duong: Path) -> tuple[int | None, list[str]]:
    """(số commit CHỈ có ở nhánh cục bộ — không có trên remote nào, tên các nhánh đang giữ chúng); None = không đo được.

    Vá 27/09/2026: cảm biến cũ chỉ đếm `@{u}..HEAD` của nhánh ĐANG đứng — nhánh chưa có upstream thì git báo lỗi và bị
    đếm thành 0, còn các nhánh khác không bao giờ được nhìn. Đo cùng ngày: 8 nhánh cục bộ của repo gốc giữ 20 commit
    không có trên GitHub (06–17/09) trong khi cảm biến báo «0 commit chưa đẩy». Đúng 2 lượt gọi git: danh sách commit
    chưa có trên remote, rồi đỉnh các nhánh (nhánh giữ commit chưa đẩy ⇔ đỉnh của nó nằm trong danh sách đó).
    """
    ra = _chay(["git", "-C", str(duong), "rev-list", "--branches", "--not", "--remotes"], giay=30)
    dong = [x.strip() for x in ra.splitlines() if x.strip()]
    if any(not re.fullmatch(r"[0-9a-f]{40,64}", x) for x in dong):
        return None, []   # git lỗi / đầu ra lạ ⇒ KHÔNG ĐO ĐƯỢC — không được đọc thành 0 (BH08)
    if not dong:
        return 0, []
    chua_day = set(dong)
    dinh = _chay(["git", "-C", str(duong), "for-each-ref", "--format=%(objectname) %(refname:short)", "refs/heads"],
                 giay=20)
    nhanh = sorted(ten for ma, _, ten in (d.strip().partition(" ") for d in dinh.splitlines()) if ma in chua_day and ten)
    return len(chua_day), nhanh


def _trang_thai_ci_pr(rollup: list) -> str:
    """xanh · do · chay · khong — từ `statusCheckRollup` của gh (CheckRun dùng conclusion/status, StatusContext dùng state)."""
    if not rollup:
        return "khong"
    ket = [str(c.get("conclusion") or c.get("state") or c.get("status") or "").upper() for c in rollup if isinstance(c, dict)]
    if any(k in ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE") for k in ket):
        return "do"
    if all(k in ("SUCCESS", "SKIPPED", "NEUTRAL") for k in ket):
        return "xanh"
    return "chay"


def giac_quan_pr_cho_gop(cac_repo: list[tuple[str, Path]], chay=None, bay_gio: dt.datetime | None = None
                         ) -> list[tuple[int, str, str]]:
    """PR MỞ đang chờ bác sĩ gộp ở cả hai repo (HV-04, kiểm toàn diện 02/10/2026: 11 PR mở mà 0 cảm biến đếm).

    Gộp PR là thẩm quyền bác sĩ (CLAUDE.md §0.5) ⇒ việc 👤. Nêu CI xanh/đỏ/đang chạy, tuổi PR cũ nhất và PR XẾP CHỒNG (base không
    phải nhánh mặc định ⇒ phải gộp PR nền trước). Cần mạng + `gh`; không trả lời được ⇒ giác quan chết (⚪), KHÔNG phải «0 PR»."""
    chay = chay or (lambda lenh: _chay(lenh, giay=45))
    bay_gio = bay_gio or dt.datetime.now(dt.timezone.utc)
    if la_phien_cloud():
        _SO_GIAC_QUAN["chay"] += 1
        _ghi_chet(["", "PR chờ gộp"], "phiên Cloud — gh không có xác thực ở đây")
        return []
    nhom, do, chay_dang, xanh, cu_nhat, xep_chong = [], 0, 0, 0, 0.0, []
    for ten, duong in cac_repo:
        orr = _owner_repo_tu_remote(duong)
        if not orr:
            _SO_GIAC_QUAN["chay"] += 1
            _ghi_chet(["", f"PR chờ gộp ({ten})"], "không suy được owner/repo từ remote")
            return []
        out = chay(["gh", "pr", "list", "--repo", orr, "--state", "open", "--limit", "50", "--json",
                    "number,createdAt,baseRefName,isDraft,statusCheckRollup"])
        try:
            prs = json.loads(out)
            assert isinstance(prs, list)
        except (ValueError, AssertionError):
            _ghi_chet(["", f"PR chờ gộp ({ten})"], "gh không trả JSON (chưa đăng nhập / mất mạng?)")
            return []
        prs = [x for x in prs if not x.get("isDraft")]
        if not prs:
            continue
        mac_dinh = _nhanh_mac_dinh(duong) if ten == "y khoa" else "master"
        so = []
        for x in sorted(prs, key=lambda y: y.get("number", 0)):
            tt = _trang_thai_ci_pr(x.get("statusCheckRollup") or [])
            do += tt == "do"
            chay_dang += tt == "chay"
            xanh += tt == "xanh"
            so.append(f"#{x['number']}" + ("✗" if tt == "do" else ""))
            try:
                tuoi = (bay_gio - dt.datetime.fromisoformat(str(x["createdAt"]).replace("Z", "+00:00"))).total_seconds() / 3600
                cu_nhat = max(cu_nhat, tuoi)
            except (KeyError, ValueError):
                pass
            if mac_dinh and x.get("baseRefName") not in (mac_dinh, None, ""):
                xep_chong.append(f"#{x['number']}→{x['baseRefName'][:40]}")
        nhom.append(f"{ten}: {' '.join(so)}")
    tong = do + chay_dang + xanh
    if not tong:
        return []
    dong = (f"{tong} PR chờ bác sĩ gộp — " + " · ".join(nhom)
            + f" (CI xanh {xanh}/{tong}" + (f", ĐỎ {do}" if do else "") + (f", đang chạy {chay_dang}" if chay_dang else "")
            + f"; cũ nhất {cu_nhat:.0f} giờ)" + (f"; XẾP CHỒNG (gộp PR nền trước): {', '.join(xep_chong)}" if xep_chong else ""))
    return [(1 if (do or cu_nhat > 48) else 2, dong, "nêu SỐ PR muốn gộp trong chat (gh --auto không chờ CI ở repo này)")]


def giac_quan_the_tuan_chua_quyet(queue_dir: Path, hom_nay: dt.date | None = None, so: Path | None = None
                                 ) -> list[tuple[int, str, str]]:
    """Thẻ của gói tuần MỚI NHẤT (≥ 3 ngày tuổi, ≤ 21 ngày) chưa có quyết định của bác sĩ trong sổ (EV-10, 03/10/2026).
    Ngoại tuyến; vắng queue ⇒ giác quan chết (⚪)."""
    _SO_GIAC_QUAN["chay"] += 1
    hom_nay = hom_nay or dt.date.today()
    if not queue_dir.is_dir():
        _ghi_chet(["", "quyết định thẻ tuần"], "không có queue/ ở cây này")
        return []
    try:
        sp = _ilu_mea.spec_from_file_location("_gdtt_tdxv", Path(__file__).resolve().parent / "ghi_duyet_the_tuan.py")
        gd = _ilu_mea.module_from_spec(sp)
        sp.loader.exec_module(gd)
        goi = gd.goi_moi_nhat(queue_dir)
        if goi is None:
            return []
        tuoi = (hom_nay - dt.date.fromtimestamp(goi.stat().st_mtime)).days
        if not 3 <= tuoi <= 21:
            return []
        the, chua = gd.chua_quyet(goi, so)
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra
        _ghi_chet(["", "quyết định thẻ tuần"], f"lỗi {type(exc).__name__}")
        return []
    if not chua:
        return []
    return [(2, f"{len(chua)}/{len(the)} thẻ gói {goi.stem} chưa ghi quyết định của bác sĩ ({tuoi} ngày) — máy không biết thẻ nào "
             "hữu ích", 'python3 tools/ghi_duyet_the_tuan.py "duyệt W<tuần>: 1 ✓ 3 ✗ 5 hoãn" --ghi')]


def giac_quan_agent_lech(goc_agents: Path, mea_agents: Path) -> list[tuple[int, str, str]]:
    """Agent `.claude/agents/*.md` của repo GỐC phải trùng từng byte bản ở repo Y KHOA (PM-15, kiểm toàn diện 02/10/2026).

    Chỉ một tệp doctrine (`_CONNECTOR-CHUNG-CU.md`, BH107) từng được so; cặp PR #77↔#61 cho thấy gộp một bên là hai bản lệch mà không
    chốt nào đỏ — vd agent kê đơn sửa ở một repo, quên repo kia. Không chặn commit (hai PR cặp có thể lệch pha vài giờ) — chỉ nhắc 🤖.
    Vắng repo y khoa ⇒ giác quan chết (⚪)."""
    _SO_GIAC_QUAN["chay"] += 1
    if not (goc_agents.is_dir() and mea_agents.is_dir()):
        _ghi_chet(["", "agent gốc ↔ y khoa"], "thiếu một trong hai thư mục .claude/agents")
        return []
    goc = {p.name: p for p in goc_agents.glob("*.md")}
    mea = {p.name: p for p in mea_agents.glob("*.md")}
    lech = sorted(n for n in goc.keys() & mea.keys() if goc[n].read_bytes() != mea[n].read_bytes())
    chi_mot = sorted(goc.keys() ^ mea.keys())
    if not lech and not chi_mot:
        return []
    mo_ta = []
    if lech:
        mo_ta.append(f"{len(lech)} lệch nội dung ({', '.join(lech[:4])}{'…' if len(lech) > 4 else ''})")
    if chi_mot:
        mo_ta.append(f"{len(chi_mot)} chỉ có ở một bên ({', '.join(chi_mot[:4])}{'…' if len(chi_mot) > 4 else ''})")
    return [(2, "Agent gốc ↔ y khoa: " + "; ".join(mo_ta) + " — đồng bộ bằng PR CẶP (cùng nội dung ở cả hai repo)",
             "diff -rq .claude/agents medical-ebm-automation/.claude/agents")]


# Kết quả `--json` gần nhất của kiem_san_luong_giam_sat; None ⇒ đúng hằng KET_QUA_GAN_NHAT của chính công cụ đó.
SAN_LUONG_GIAM_SAT: Path | None = None


def giac_quan_chu_de_0_lien(dash_dir: Path, san_luong: Path | None = None
                            ) -> tuple[list[tuple[int, str, str, str]], list[str]]:
    """Chủ đề watchlist 0 ứng viên ≥ 2 lượt tuần LIỀN + đề xuất truy vấn chờ duyệt (03/10/2026) — (việc, dòng ⓘ).

    Đếm thô 03/10: W39 + W40 có 10/47 chủ đề 0 ứng viên mà bộ quét vẫn PASS và tiến con trỏ; đề xuất viết lại truy vấn
    soạn 02/10 nằm chờ; chốt sản lượng không nằm trong dây chuyền tuần ⇒ không ai thấy. Logic và luật «đo được» ở
    `tools/kiem_chuoi_0_ung_vien.py` (một nguồn cho CLI và bảng này): chủ đề PASS_DEGRADED/FAIL, tệp hỏng không bao
    giờ thành «0 ứng viên», lượt không đo được nằm giữa không bắc cầu. Ngoại tuyến. Vắng EBM-Dashboards/surveillance,
    < 2 lượt đọc được, watchlist/đề xuất hỏng, công cụ lỗi ⇒ giác quan chết (⚪), KHÔNG phải «không có chủ đề mù»."""
    _SO_GIAC_QUAN["chay"] += 1
    nhan = ["", "chủ đề 0 ứng viên liền"]
    if not (dash_dir / "surveillance").is_dir():
        _ghi_chet(nhan, "không có EBM-Dashboards/surveillance ở cây này")
        return [], []
    try:
        sp = _ilu_mea.spec_from_file_location("_k0uv_tdxv",
                                              Path(__file__).resolve().parent / "kiem_chuoi_0_ung_vien.py")
        k0 = _ilu_mea.module_from_spec(sp)
        sp.loader.exec_module(k0)
        pt = k0.phan_tich(dash_dir, san_luong)
        viec, tt = k0.viec_tu_phan_tich(pt)
    except Exception as exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra
        _ghi_chet(nhan, f"lỗi {type(exc).__name__}")
        return [], []
    if not pt.get("do_duoc"):
        _ghi_chet(nhan, str(pt.get("ly_do")))
        return [], []
    for cb in pt.get("canh_bao") or []:
        _ghi_chet(nhan, cb)
    return viec, tt


def ghi_json(de_xuat: list, chet: list[str], tep: Path, so_giac_quan: int) -> None:
    """Bảng đề xuất dạng máy đọc cho hòm việc một cửa (`tools/hom_viec_mot_cua.py`) — ghi nguyên tử, ngoài git (state/)."""
    tep.parent.mkdir(parents=True, exist_ok=True)
    tam = tep.with_name(tep.name + f".tam-{os.getpid()}")
    tam.write_text(json.dumps({"sinh_luc": dt.datetime.now().isoformat(timespec="seconds"), "giac_quan": so_giac_quan,
                               "chet": chet, "viec": [{"uu": u, "ai": a, "viec": v, "lenh": lenh} for u, a, v, lenh in de_xuat]},
                              ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, tep)


def dem_dashboard_phai_sinh_loi_thoi(dash_dir: Path) -> int:
    """Đếm dashboard có bản Word/bản-đọc THẬT SỰ lỗi thời so với nội dung.

    Ưu tiên so HASH khối `const DATA` (sidecar `<tên>.data-sha256` cạnh file
    `.docx`, ghi bởi `xuat_goi_cap_nhat.py` mỗi lần xuất — xem BH76). Không có
    sidecar (dashboard chưa từng qua cơ chế mới) thì lùi về heuristic MTIME cũ:
    docx thiếu hoặc cũ hơn html. Trả về số dashboard thật sự lỗi thời."""
    n_cu = 0
    vd = None
    try:
        tools_dir = str(dash_dir / "tools")
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import verify_dashboard as vd  # noqa: PLC0415
    except ImportError:
        vd = None
    for f_db in sorted(dash_dir.glob("WebDashboard_*.html")):
        if ".bak" in f_db.name:
            continue
        ma = f_db.stem.replace("WebDashboard_EBM_VanDeCuThe_", "").replace("WebDashboard_EBM_", "")
        cac_docx = [dash_dir / "derivatives" / f"{ma}_TaiLieuChiTiet.docx",
                    dash_dir / "derivatives" / f"{f_db.stem}_TaiLieuChiTiet.docx"]
        docx = next((d for d in cac_docx if d.exists()), None)
        if docx is None:
            n_cu += 1
            continue
        sidecar = docx.with_suffix(".data-sha256")
        if sidecar.exists() and vd is not None:
            try:
                html = f_db.read_text(encoding="utf-8", errors="replace")
                data_block = vd.extract_data_block(html)
                h_hien_tai = (hashlib.sha256(data_block.encode("utf-8")).hexdigest()
                              if data_block else None)
                h_luc_xuat = sidecar.read_text(encoding="utf-8").strip()
                if h_hien_tai is not None and h_hien_tai != h_luc_xuat:
                    n_cu += 1
                continue
            except OSError:
                pass  # đọc lỗi ⇒ lùi về heuristic mtime bên dưới
        if docx.stat().st_mtime < f_db.stat().st_mtime:
            n_cu += 1
    return n_cu


def main() -> int:
    ap = argparse.ArgumentParser(description="Bảng đề xuất việc tự sinh từ bộ đếm sống")
    ap.add_argument("--gon", action="store_true", help="chỉ in bảng, bỏ phần giải thích")
    ap.add_argument("--json", type=Path, default=None, help="ghi bảng dạng máy đọc (cho hom_viec_mot_cua.py)")
    a = ap.parse_args()
    de_xuat: list[tuple[int, str, str, str]] = []  # (ưu tiên, ai, việc+số đo, lệnh)

    # ① Sổ xác minh — độ phủ & rút bài. Sửa 16/08: đọc dòng «Chưa/hết hạn» TRỰC
    # TIẾP thay vì hiệu số tổng−hiệu-lực — hiệu số dính cả ca rút-và-thay (dương
    # tính THẬT phải giữ) và bản ghi lịch sử không còn ai trích ⇒ «còn 2 mục»
    # treo vĩnh viễn dù việc thật = 0 (họ BH32: chỉ số gộp nói sai về tập hợp).
    out = _chay([sys.executable, "tools/so_xac_minh_nguon.py", "--bao-cao"])
    m = re.search(r"Chưa/hết hạn\s*:\s*(\d+)", out)
    if m and int(m.group(1)):
        # Số đo là của TOÀN sổ; `--vong 3` chỉ quét định danh đang nằm trong dashboard — bản ghi mồ côi (cầu NC⇄LS/hub tạo
        # trần) chỉ `--quet-ledger` + `--phu-mo-coi` chạm tới. 27/09/2026: chạy đúng lệnh gợi ý cũ, 125 mục đứng yên nguyên vẹn.
        de_xuat.append((2, "🤖", f"Phủ sổ xác minh: {m.group(1)} mục chưa/hết hạn (đo trên TOÀN sổ)",
                        "~/.ebm-venv/bin/python tools/so_xac_minh_nguon.py --vong 3 && "
                        "~/.ebm-venv/bin/python tools/so_xac_minh_nguon.py --quet-ledger --vong 3 && "
                        "~/.ebm-venv/bin/python tools/so_xac_minh_nguon.py --phu-mo-coi --vong 3"))
    # Nguồn «ĐÃ BỊ RÚT» trong sổ gồm CẢ ca thông báo-là-bản-đính-chính (BH109). Tách hai nhóm để dòng «rút-bỏ-hẳn»
    # không cảnh báo sai về ca chỉ cần bác sĩ ký (T4-05: gọi nó «rút-bỏ-hẳn/không dùng» dạy người đọc bỏ qua cảnh báo).
    dem_dinh_chinh = _chay([sys.executable, "tools/mau_ky_rut_bai.py", "--dem"]).strip()
    n_dc = int(dem_dinh_chinh) if dem_dinh_chinh.isdigit() else 0            # CÒN chờ bác sĩ ký
    dem_tat_ca = _chay([sys.executable, "tools/mau_ky_rut_bai.py", "--dem-tat-ca"]).strip()
    n_dc_tong = int(dem_tat_ca) if dem_tat_ca.isdigit() else n_dc           # loại đính chính, đã ký lẫn chưa
    m_rut = re.search(r"ĐÃ BỊ RÚT\s*:\s*(\d+)", out)
    n_rut = int(m_rut.group(1)) if m_rut else 0
    if n_rut - max(n_dc, n_dc_tong) > 0:  # đã ký xong KHÔNG được biến thành «rút-bỏ-hẳn» (P2-03)
        de_xuat.append((0, "👤", "CÓ nguồn rút-bỏ-hẳn đang được trích — xử lý trước "
                        "khi dùng gói chứa nó", "python3 tools/so_xac_minh_nguon.py --bao-cao"))
    # ①-bis (BH109, 20/09/2026): nguồn bị cờ «rút bài» mà thông báo là BẢN ĐÍNH CHÍNH bị rút. Cổng vẫn
    # CHẶN; chỉ bác sĩ ký được. Máy đã dựng mẫu chờ ký — dòng này để việc đó tự hiện ra, khỏi phải
    # đọc terminal rồi tự chép khoá + tập thông báo (chép sai vân tay thì miễn trừ im lặng vô hiệu).
    if n_dc:
        de_xuat.append((0, "👤", f"{n_dc} nguồn bị cờ «rút bài» nhưng thông báo là BẢN ĐÍNH CHÍNH bị rút — "
                        "đọc thông báo + Author Correction rồi ký hoặc hạ mục (máy đã dựng mẫu chờ ký, "
                        "KHÔNG ký thay)", "python3 tools/mau_ky_rut_bai.py"))

    # ② gradeBy tồn kho — ĐÓNG 16/08 theo duyệt bác sĩ: mọi đường máy đã vét
    # (nhóm tổ chức · tra sống pubtype · toàn văn PMC-OA); 'na' là khai báo
    # TRUNG THỰC khi nguồn không phân hạng, cổng đang mức CẢNH BÁO. Chuyển
    # theo dõi thành KIỂM KÊ QUÝ (tháng đầu quý), số sẽ tự giảm khi các phiên
    # cập-nhật-chủ-đề thay nguồn cũ bằng guideline có chấm.
    # 03/10/2026 bác sĩ chọn «5b»: chấp nhận là KHOẢNG TRỐNG ĐÃ BIẾT ⇒ hạ xuống dòng ⓘ, không còn là việc
    # 👤 (cổng verify_dashboard vẫn cảnh báo từng item như cũ; chỉ hòm việc thôi nhắc).
    if dt.date.today().month in (1, 4, 7, 10):
        dong = _dong_kiem_ke_gradeby(_chay([sys.executable, "tools/kiem_phan_hang.py"]))
        if dong:
            _THONG_TIN.append(dong)

    # ③ Hai bản nói ngược
    out = _chay([sys.executable, "tools/dang_ky_chu_de.py"])
    m = re.search(r"(\d+) MỤC HAI BẢN NÓI NGƯỢC", out)
    if m and int(m.group(1)):
        de_xuat.append((0, "👤", f"{m.group(1)} cặp hai-bản-nói-ngược cùng PMID — "
                        "bác sĩ quyết bản đúng", "python3 tools/dang_ky_chu_de.py"))

    # ④ Độ tươi chứng cứ (trung vị + báo động 120 ngày — BH32: không dùng max)
    out = _chay([sys.executable, "tools/kiem_do_tuoi_chung_cu.py"])
    m = re.search(r"trung vị\s*(\d+)", out)
    if m and int(m.group(1)) > 60:
        de_xuat.append((2, "🤖", f"Trung vị tuổi gói {m.group(1)} ngày — chạy cập nhật "
                        "chủ đề lâu nhất (máy làm A2/A4/B2, rồi mở phiên /cap-nhat-chung-cu theo phiếu)",
                        "python3 ops/orchestrator.py --cu-nhat 3 --online"))

    # ⑤ Kho toàn văn + chỉ mục RAG
    kho = DASH / "toan_van_oa"
    xmls = list(kho.glob("PMID-*.xml"))
    vec = kho / ".rag" / "vec.npy"
    if xmls and vec.exists() and max(f.stat().st_mtime for f in xmls) > vec.stat().st_mtime:
        de_xuat.append((2, "🤖", "Chỉ mục RAG cũ hơn kho toàn văn — dựng lại",
                        "~/.ebm-venv/bin/python tools/rag_toan_van.py --dung-index"))

    # ⑥ Đề tài thật — việc người gần nhất (đọc readiness C1a)
    out = _chay([str(VENV_PY),
                 str(_GOC_MEA / "tools" / "study_readiness.py"),
                 "--study", "hai-long-benh-nhan-C1a-BVQY175"])
    if "CHƯA được bác sĩ chốt" in out:
        de_xuat.append((1, "👤", "C1a: G0 chờ 5 cờ FINER — một cú đúp",
                        "mở «Chot FINER C1a.command» (Mac) / .ps1 (Windows)"))
    if "0/4" in out:
        de_xuat.append((1, "👤", "C1a: 0/4 cổng cứng có chữ ký — bước tiếp là hồ sơ "
                        "G2 nộp IRB thật", "xem exports/.../HO-SO-KHOI-DONG-2026-08-15.md"))

    # ⑦b GIÁC QUAN CI (thêm 16/08 — bài học «CI đỏ 13 tháng không ai nhìn»):
    # đọc phán quyết run mới nhất CỦA TỪNG REPO; đỏ = việc ưu tiên 0. Fail-soft
    # khi thiếu gh/mạng. Sửa cùng ngày: bản đầu chạy gh với cwd repo GỐC cho
    # workflow của repo Y KHOA ⇒ HTTP 404 đội lốt «mạng chập chờn» — dòng nhắc
    # «thấy: HTTP» dai dẳng nhiều lượt bảng thật ra là hỏi NHẦM REPO.
    # Sửa 26/09/2026: CHỈ đọc run của NHÁNH MẶC ĐỊNH (xem `_nhanh_mac_dinh`) — run xanh của nhánh
    # `claude/*` từng che nhánh mặc định đỏ sau mỗi lần merge. Dòng đề xuất in tên nhánh.
    co_gh = bool(shutil.which("gh"))
    for ten_ci, cwd_ci, wf in (("y khoa", _GOC_MEA, "offline-ci.yml"),
                               ("gốc", REPO, "kiem-tinh-da-nen.yml")):
        if not (cwd_ci / ".github" / "workflows" / wf).exists():
            continue
        kq_ci, nhanh = doc_ci_mot_repo(ten_ci, cwd_ci, wf, co_gh=co_gh)
        nhan = f"[{nhanh}]" if nhanh else "[nhánh mặc định: KHÔNG xác định]"
        loc = f"--branch {nhanh}" if nhanh else "--branch <nhánh-mặc-định>"
        if kq_ci == "failure":
            de_xuat.append((0, "🤖", f"CI repo {ten_ci} {nhan} FAILURE — đọc log, sửa tới xanh, "
                            "đừng để đỏ qua đêm",
                            f"cd \"{cwd_ci.name}\" && gh run list --workflow {wf} {loc} --limit 3 "
                            "&& gh run view <id> --log-failed"))
        elif kq_ci != "success":
            # đang chạy / gh lỗi / mạng — KHÔNG BIẾT ≠ CÓ VẤN ĐỀ (BH08): mức nhắc
            de_xuat.append((2, "🤖", f"Chưa đọc được phán quyết CI repo {ten_ci} {nhan} "
                            f"(thấy: {kq_ci or 'rỗng'}) — kiểm tay khi tiện",
                            f"gh run list --workflow {wf} {loc} --limit 3"))

    # ⑦c GIÁC QUAN GIT (bài «40 file chưa commit mà tưởng cây sạch»): đếm file
    # bẩn + commit chưa đẩy ở cả hai repo. Chỉ ĐẾM và BÁO — không tự add của ai.
    for ten_repo, duong in (("gốc", REPO), ("y khoa", _GOC_MEA)):
        if not (duong / ".git").exists():
            continue  # máy/cây thiếu repo (CI checkout đơn-repo) — stderr của git
            # sẽ bị _chay gộp vào stdout và đếm nhầm thành "1 file chưa commit"
        st = _chay(["git", "-C", str(duong), "status", "--porcelain"], giay=20)
        n_ban = len([x for x in st.splitlines() if x.strip()])
        n_chua_day, nhanh_chua_day = dem_commit_chua_co_tren_remote(duong)
        if n_chua_day is None:
            de_xuat.append((2, "🤖", f"Repo {ten_repo}: KHÔNG đo được commit chưa có trên remote (git lỗi) — kiểm tay",
                            f"git -C \"{duong.name}\" log --branches --not --remotes --oneline"))
        if n_ban or n_chua_day:
            o_nhanh = ""
            if nhanh_chua_day:
                o_nhanh = (f" (ở {len(nhanh_chua_day)} nhánh cục bộ: {', '.join(nhanh_chua_day[:4])}"
                           f"{'…' if len(nhanh_chua_day) > 4 else ''})")
            de_xuat.append((2, "🤖", f"Repo {ten_repo}: {n_ban} file chưa commit · "
                            f"{n_chua_day or 0} commit chưa có trên remote nào{o_nhanh} — soi rồi commit/push "
                            "(file/nhánh của phiên khác thì ĐỂ NGUYÊN — chỉ đẩy bản sao `rescue/<nhánh>`)",
                            f"git -C \"{duong.name}\" log --branches --not --remotes --oneline"
                            if nhanh_chua_day else f"git -C \"{duong.name}\" status -sb"))

    # ⑦d GIÁC QUAN LỊCH-NỀN (16/08 — ngay kỳ đầu của kiến trúc lịch mới đã LỠ:
    # tác vụ Claude 06:30 T7 không nổ vì máy/app không chạy, nextRunAt nhảy thẳng
    # tuần sau, không lastRunAt — không bộ đếm nào nhìn thấy). Đo ĐẦU RA THẬT
    # trong log (bài học launchd: đăng ký ≠ nổ), không đọc đăng ký lịch.
    # ĐÍNH CHÍNH 12/09/2026: lịch đã đổi sang thứ Hai 18:00 (17/08/2026) và
    # chạy qua mcp scheduled-tasks (cloud, KHÔNG cần máy/phiên local đang mở —
    # khác hẳn launchd cũ) — 4/4 lần chạy gần nhất đều PASS đúng hẹn, không hề
    # lỡ kỳ nào kể từ khi đổi. giac_quan_lich_nen() đã cập nhật theo lịch mới.
    for uu, dong in giac_quan_lich_nen_theo_noi_chay(
            _GOC_MEA / "data" / "archive" / "launchd_weekly.log"):
        de_xuat.append((uu, "🛎" if uu < 2 else "👤", dong,
                        "bash medical-ebm-automation/scripts/weekly_safety.sh  # chạy bù"
                        if uu < 2 else "bấm «Run now» tác vụ thu-thap-tuan-an-toan-thuoc "
                        "(mcp__scheduled-tasks__run_scheduled_task) hoặc kiểm lịch sử qua "
                        "list_task_runs"))

    # ⑦f CẢM BIẾN NGƯỜI CHẾT (T2-01, 20/09/2026): mỗi KỲ lịch nền phải để lại dấu vết đầu ra ĐÚNG HẸN. ⑦d ở trên chỉ so
    # «PASS cuối» nên một lượt chạy tay chen giữa làm kỳ lỡ vô hình (đúng ca 14/09: 3/4 tác vụ bị xoá, không cảm biến nào
    # báo). Nhãn 🛎 = máy làm được (chạy bù) nhưng chưa ai chạy — luôn hiện ở hòm thư bác sĩ (T2-02).
    _SO_GIAC_QUAN["chay"] += 1
    try:
        _sp_kln = _ilu_mea.spec_from_file_location("_kln_tdxv", Path(__file__).resolve().parent / "kiem_lich_nen.py")
        _kln = _ilu_mea.module_from_spec(_sp_kln)
        _sp_kln.loader.exec_module(_kln)
        _viec, _tt = phan_loai_lich_nen(_kln.kiem()["phat_hien"])
        de_xuat += _viec
        _THONG_TIN.extend(_tt)
    except Exception as _exc:  # noqa: BLE001 — cảm biến hỏng phải hiện ra, không được im lặng
        _ghi_chet(["python3", "tools/kiem_lich_nen.py"], f"lỗi {type(_exc).__name__}")

    # ⑦h URL MIỀN CHẶN BOT (02/10/2026): bác sĩ tự vượt kiểm tra chống bot, máy ghi bằng chứng — xem docstring.
    for uu, dong, lenh in giac_quan_url_chan_bot(DASH):
        de_xuat.append((uu, "👤", dong, lenh))

    # ⑦i TOÀN VĂN THẺ TUẦN (02/10/2026): bài không OA ⇒ làn trình duyệt có bác sĩ — xem docstring.
    for uu, dong, lenh in giac_quan_toan_van_the_tuan(_bst_mea.duong_goc("queue", REPO) or (REPO / "queue"), DASH):
        de_xuat.append((uu, "👤", dong, lenh))

    # ⑦k BẢO ĐẢM ĐỌC TOÀN VĂN (04/10/2026): mục apply chưa đọc toàn văn — sổ nợ có hạn, quá hạn cổng chặn — xem docstring.
    for uu, dong, lenh in giac_quan_no_toan_van(DASH):
        de_xuat.append((uu, "👤", dong, lenh))

    # ⑦l SKILL TÀI KHOẢN CLAUDE.AI (04/10/2026, BH163): bộ skill Cowork/claude.ai/Routine nạp cũ hơn repo — xem docstring.
    for uu, dong, lenh in giac_quan_skill_tai_khoan():
        de_xuat.append((uu, "👤", dong, lenh))

    # ⑦j CHỦ ĐỀ 0 ỨNG VIÊN NHIỀU LƯỢT LIỀN (03/10/2026): «0 ứng viên ≠ không có chứng cứ mới» — xem docstring.
    _viec_0, _tt_0 = giac_quan_chu_de_0_lien(DASH, SAN_LUONG_GIAM_SAT)
    de_xuat += _viec_0
    _THONG_TIN.extend(_tt_0)

    # ⑦g NGUỒN HỎNG KÉO DÀI (01/10/2026, BH145): nguồn hỏng nhiều lượt live liền mà lượt vẫn PASS — xem docstring.
    for uu, dong, lenh in giac_quan_nguon_hong_keo_dai(_GOC_MEA / "data" / "medical_ebm.db"):
        de_xuat.append((uu, "🤖", dong, lenh))

    # ⑦e GIÁC QUAN QUYẾT ĐỊNH ĐÃ DUYỆT (16/08): dashboard sinh lại/sửa hàng loạt
    # có thể lật ngược im lặng quyết định bác sĩ 13–14/08 (đã xảy ra: 5 mục Đau
    # Đầu tái lệch do đợt 12/08). Tái phạm = 🔴 👤 — đổi decision là thẩm quyền.
    out = _chay([sys.executable, "tools/kiem_quyet_dinh_da_duyet.py"], giay=60)
    m = re.search(r"🔴 (\d+) tái phạm", out)
    if m and int(m.group(1)):
        de_xuat.append((0, "👤", f"{m.group(1)} quyết định ĐÃ DUYỆT bị lật ngược trong kho "
                        "— xem chi tiết rồi quyết áp lại hay duyệt lại",
                        "python3 tools/kiem_quyet_dinh_da_duyet.py"))

    # ⑧ Bản ĐẶT-CẠNH mới nhất (16/08): nhắc khi có mục 'apply' mang nguồn tổng
    # hợp mới hơn chưa được bác sĩ so — đọc con số từ chính header bản gần nhất.
    cac_ban = sorted((DASH / "derivatives").glob("DAT-CANH-CHUNG-CU-MOI_*.md"))
    if cac_ban:
        dau = cac_ban[-1].read_text(encoding="utf-8", errors="replace")[:600]
        m = re.search(r"(\d+) mục có tổng quan/guideline", dau)
        if m and int(m.group(1)):
            de_xuat.append((2, "👤", f"{m.group(1)} mục 'apply' có nguồn tổng hợp MỚI HƠN "
                            f"— bản đặt-cạnh sẵn ở {cac_ban[-1].name} (không phán chiều, "
                            "bác sĩ tự so)", f"mở EBM-Dashboards/derivatives/{cac_ban[-1].name}"))

    # ⑨ GIÁC QUAN PLUGIN (16/08 — kho không đứng yên: 2 plugin tự đổi bản giữa
    # một resume; danh mục/trang tra/mốc trôi theo mà không ai thấy). Đọc chốt
    # kiem_plugin_day_du: lệch mốc/đổi bản → nhắc chạy nghi thức MỘT lệnh.
    # Sửa 26/09/2026: phần sinh dòng tách thành `de_xuat_plugin()` — trên Cloud không còn mục 🤖
    # «ghi mốc» (lệnh đó ghi đè danh mục gộp hai máy đang track bằng dữ liệu chỉ-Cloud).
    r_pl = subprocess.run([sys.executable, "tools/kiem_plugin_day_du.py"],
                          capture_output=True, text=True, timeout=60, cwd=REPO,
                          encoding="utf-8", errors="replace")
    de_xuat.extend(de_xuat_plugin(r_pl.returncode, la_phien_cloud()))

    # ⑩ PHÁI SINH LỖI THỜI (16/08 — đo được 45/62 bản Word/bản-đọc CŨ HƠN chính
    # dashboard sau các đợt sửa nội dung: bác sĩ đọc bản lỗi thời mà không biết).
    # Sửa 16/08 đêm: tool xuất đặt tên phái sinh theo HAI mẫu — nhóm VanDeCuThe
    # cắt tiền tố, nhóm còn lại (Uptodate/AnToanThuoc…) GIỮ nguyên cả
    # WebDashboard_EBM_ — đếm bằng một mẫu tạo 13 «tồn ảo» bị xuất lại vô ích.
    #
    # VÁ 25/08/2026 (BH76) — MTIME KHÔNG PHÂN BIỆT ĐƯỢC «SỬA NỘI DUNG» VỚI «SỬA VỎ».
    # Đo thật: Sprint 9 task 9.2 reskin THUẦN CSS/HTML cho 66/67 dashboard (đã xác
    # nhận `DATA` byte-for-byte không đổi) bump mtime của CẢ 66 bản cùng lúc ⇒
    # heuristic mtime báo "66 dashboard lỗi thời" trong khi THẬT SỰ chỉ 5 bản có
    # nội dung đổi (đối chiếu DATA-hash với bản backup trước reskin xác nhận đúng
    # 5/66, đã xuất lại). Chạy `xuat_goi_cap_nhat.py --online` cho 61 bản còn lại
    # sẽ lãng phí ~60 lượt gọi PubMed thật cho một thay đổi KHÔNG đụng khoa học.
    # Nay ưu tiên so HASH nội dung khối DATA (sidecar `<tên>.data-sha256`, ghi bởi
    # `xuat_goi_cap_nhat.py` mỗi lần xuất) — chỉ báo lỗi thời khi hash THẬT SỰ khác.
    # Dashboard chưa từng có sidecar (chưa qua cơ chế mới) lùi về heuristic mtime cũ,
    # không đổi hành vi cho dashboard chưa từng chạm. Logic tách hàm riêng
    # `dem_dashboard_phai_sinh_loi_thoi()` để BH76 kiểm được bằng đột biến trên
    # đĩa tạm, không đụng kho dashboard thật.
    n_cu = dem_dashboard_phai_sinh_loi_thoi(DASH)
    if n_cu:
        de_xuat.append((2, "🤖", f"{n_cu} dashboard có bản Word/bản-đọc CŨ HƠN nội dung "
                        "— xuất lại để bác sĩ không đọc bản lỗi thời",
                        "chạy lại tools/xuat_goi_cap_nhat.py cho từng bản (gói tuần tự làm)"))

    # ⑦ Nhật ký tác động — miss dồn cụm
    log = REPO / "state" / "nhat-ky-tac-dong.jsonl"
    if log.exists():
        try:
            dong = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x]
            # «khớp yếu» (có thẻ gần chủ đề, dưới ngưỡng) ≠ khoảng trống giám sát — không dồn vào ngưỡng báo động.
            miss = sum(1 for r in dong if r.get("miss") and r.get("loai") != "khop_yeu")
            if miss >= 3:
                de_xuat.append((1, "🤖", f"{miss} lượt điểm-khám NGOÀI giám sát — rà "
                                "ứng viên mở watchlist",
                                "đọc state/cau-hoi-chua-giam-sat.jsonl trong gói tuần"))
        except (json.JSONDecodeError, OSError):
            pass

    # ⑪ BÀI TỔNG THUẬT — độ tươi + phủ hòm thư (thêm 20/08: bài là ẢNH TĨNH, không
    # ai canh thì nó cũ đi IM LẶNG — đúng họ lỗi đã vá ở dashboard).
    out = _chay([sys.executable, "tools/dang_ky_tong_thuat.py"])
    m = re.search(r"(\d+)/(\d+) bài quá (\d+) ngày", out)
    if m and int(m.group(1)):
        de_xuat.append((2, "👤", f"{m.group(1)}/{m.group(2)} bài tổng thuật quá "
                        f"{m.group(3)} ngày — rà nguồn mới hơn trước khi dùng lại",
                        "python3 tools/dang_ky_tong_thuat.py"))
    so_tt = REPO / "EBM-Dashboards" / "tong_thuat" / "so-tong-thuat.json"
    if so_tt.exists():
        try:
            bai = json.loads(so_tt.read_text(encoding="utf-8")).get("bai", [])
            mo_coi = [b for b in bai if not b.get("chu_de")]
            if mo_coi:
                de_xuat.append((2, "🤖", f"{len(mo_coi)} bài tổng thuật CHƯA khớp chủ đề "
                                "danh bạ — bộ dò chứng-cứ-vượt-qua không quét tới",
                                "python3 tools/tra_nguon_chuan.py --danh-sach"))
        except (json.JSONDecodeError, OSError):
            pass

    # ⑫ PR CHỜ GỘP (HV-04) + ⑬ QUYẾT ĐỊNH THẺ TUẦN (EV-10) — 03/10/2026, xem docstring.
    for uu, dong, lenh in giac_quan_pr_cho_gop([("gốc", REPO), ("y khoa", _GOC_MEA)] if _GOC_MEA.exists() else [("gốc", REPO)]):
        de_xuat.append((uu, "👤", dong, lenh))
    for uu, dong, lenh in giac_quan_the_tuan_chua_quyet(_bst_mea.duong_goc("queue", REPO) or (REPO / "queue")):
        de_xuat.append((uu, "👤", dong, lenh))
    for uu, dong, lenh in giac_quan_agent_lech(REPO / ".claude" / "agents", _GOC_MEA / ".claude" / "agents"):
        de_xuat.append((uu, "🤖", dong, lenh))
    if a.json:
        de_xuat.sort(key=lambda x: x[0])
        ghi_json(de_xuat, list(_GIAC_QUAN_CHET), a.json, _SO_GIAC_QUAN["chay"])

    hom_nay = dt.date.today().isoformat()
    print("=" * 66)
    print(f"  HỆ TỰ ĐỀ XUẤT VIỆC — {hom_nay} (sinh từ bộ đếm sống, không cảm giác)")
    print("=" * 66)
    n_chay, n_chet = _SO_GIAC_QUAN["chay"], len(_GIAC_QUAN_CHET)
    print(f"  Giác quan đo được: {n_chay - n_chet}/{n_chay}"
          + (f" — {n_chet} KHÔNG đo được (xem cuối bảng)" if n_chet else ""))
    if not de_xuat and not n_chet:
        print("  🟢 KHÔNG CÒN VIỆC NÀO các bộ đếm nhìn thấy — «đủ rồi» là kết quả")
        print("     hợp lệ; nghỉ cũng là một trạng thái đúng của hệ.")
    elif not de_xuat:
        print("  ⚪ KHÔNG THỂ nói «đủ rồi»: còn giác quan không đo được — im lặng của cảm biến hỏng")
        print("     KHÔNG phải bằng chứng không có việc (BH08/BH27).")
    if de_xuat:
        de_xuat.sort(key=lambda x: x[0])
        for uu, ai, viec, lenh in de_xuat:
            print(f"  {'🔴' if uu == 0 else '🟠' if uu == 1 else '🟡'} {ai} {viec}")
            print(f"       → {lenh}")
    for x in _GIAC_QUAN_CHET:
        print(f"  ⚪ giác quan KHÔNG đo được: {x}")
    for x in _THONG_TIN:
        print(f"  ⓘ {x}")
    if not a.gon:
        print("-" * 66)
        print("  👤 = thẩm quyền bác sĩ, máy không tự làm · 🤖 = máy chạy được ngay")
        print("  🛎 = máy làm được nhưng CHƯA CÓ AI chạy — cần một phiên chạy hộ (luôn hiện ở hòm thư)")
        print("  Mỗi dòng đều có SỐ ĐO đứng sau. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
