#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐO: nguồn nào kiểm được RÚT BÀI mà KHÔNG cần NCBI API key?

VÌ SAO CÓ (14/08/2026)
======================
`app/sources/pubmed.py::check_retraction_status()` là đường DUY NHẤT mà hệ này
kiểm rút bài, và nó gọi thẳng NCBI E-utilities. Khi NCBI chặn IP (trang "WWW
Error Blocked Diagnostic") thì toàn bộ kho — 1146 định danh — đứng ở trạng thái
**CHƯA kiểm rút bài**, fail-closed đúng thiết kế nhưng không nhúc nhích được.

Cách sửa chuẩn là thêm `NCBI_API_KEY`. Khi KHÔNG lấy được khoá, vấn đề thật sự
không phải "thiếu khoá" mà là **ĐƠN NGUỒN**: một nhà cung cấp chặn là mất hẳn
năng lực. Có ít nhất 3 nguồn khác công bố trạng thái rút bài và **không đòi
khoá API** nào:

  1. OpenAlex      — trường `is_retracted` ngay trên bản ghi, tra theo `pmid:`
  2. Europe PMC    — soi lại metadata MEDLINE (pubType / commentCorrection)
  3. Retraction Watch qua Crossref — CSV công khai CC0, TẢI MỘT LẦN, tra NGOẠI TUYẾN

Nhưng ba dòng trên là **giả thuyết cho tới khi đo**. Công cụ này ĐO, trên đúng
mạng của bác sĩ, bằng hai PMID đã biết đáp án, rồi báo nguồn nào thật sự dùng
được và trả về đúng thứ gì.

NÓ CHỈ ĐO VÀ BÁO. Không sửa cấu hình, không đụng `check_citation_retraction.py`,
không ghi vào sổ xác minh, không mở cổng A12. Việc chọn nguồn nào được quyền
nói "bài này chưa bị rút" trong một CỔNG AN TOÀN là quyết định của bác sĩ.

Dùng:
    python3 tools/do_nguon_rut_bai.py              # đo cả 3 nguồn
    python3 tools/do_nguon_rut_bai.py --bo-qua-rw  # bỏ Retraction Watch (cần email)
    python3 tools/do_nguon_rut_bai.py --email a@b.c

Mã thoát: 0 = có nguồn thay thế dùng được · 1 = tới được nhưng trả lời sai/thiếu
          · 2 = không nguồn nào tới được.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Windows: stdout mặc định cp1252 → print() tiếng Việt ném UnicodeEncodeError và
# giết tiến trình SAU KHI việc đã xong. Cùng lớp lỗi đã vá cho tools/vietnamize/.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

GOC = Path(__file__).resolve().parents[1]
TIMEOUT = 30

# Hai PMID ĐÃ BIẾT ĐÁP ÁN — đo bằng thứ mình biết trước, không đo bằng thứ mình
# đang muốn tin. Cả hai đều đã dùng ở nơi khác trong repo nên không phải mẫu mới.
#   9500320  — Wakefield 1998 (Lancet), bị rút 2010. Fixture rút bài chuẩn của repo.
#   26760044 — Bornstein 2016, hướng dẫn Endocrine Society. Chưa bị rút.
FIXTURES = [
    ("9500320", True, "Wakefield 1998 — ĐÃ BỊ RÚT"),
    ("26760044", False, "Bornstein 2016 — chưa bị rút"),
]


def _ssl_context() -> ssl.SSLContext:
    """Bối cảnh SSL có chứng chỉ CA dùng được.

    Python 3.14 cài tay trên máy Mac này KHÔNG có bộ chứng chỉ CA hệ thống, nên
    mọi lời gọi urllib gãy bằng SSLCertVerificationError (đã ghi trong bộ nhớ dự
    án 04/08/2026; httpx/requests không dính vì mang certifi theo). Ở đây ưu tiên
    certifi nếu có, và nếu không có thì để lỗi NỔI LÊN kèm cách sửa — tuyệt đối
    KHÔNG tắt xác minh chứng chỉ để "cho chạy được".
    """
    try:
        import certifi  # type: ignore
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


CTX = _ssl_context()


def _get(url: str, *, doc_dong_dau: int = 0) -> tuple[int, str]:
    """GET một URL. `doc_dong_dau` > 0 thì chỉ đọc bấy nhiêu byte (cho file lớn)."""
    req = urllib.request.Request(
        url, headers={"User-Agent": "EBM-Copilot/do_nguon_rut_bai (kiem tra rut bai)"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as resp:
        raw = resp.read(doc_dong_dau) if doc_dong_dau else resp.read()
        return resp.status, raw.decode("utf-8", errors="replace")


def _loi_ngan(exc: Exception) -> str:
    if isinstance(exc, ssl.SSLCertVerificationError):
        return ("THIẾU CHỨNG CHỈ CA — chạy lại bằng venv EBM: "
                "~/.ebm-venv/bin/python tools/do_nguon_rut_bai.py")
    if isinstance(exc, urllib.error.HTTPError):
        return f"HTTP {exc.code}"
    if isinstance(exc, urllib.error.URLError):
        return f"không kết nối được ({exc.reason})"
    return f"{type(exc).__name__}: {exc}"


# ─────────────────────────── Nguồn 1 — OpenAlex ────────────────────────────
def do_openalex(pmid: str) -> tuple[str, str]:
    """→ (trang_thai, chi_tiet). trang_thai ∈ retracted | not_retracted | unknown."""
    url = f"https://api.openalex.org/works/pmid:{pmid}"
    try:
        _, body = _get(url)
        d = json.loads(body)
    except Exception as exc:
        return "unknown", _loi_ngan(exc)
    if "is_retracted" not in d:
        return "unknown", "bản ghi KHÔNG có trường is_retracted"
    co = bool(d["is_retracted"])
    return ("retracted" if co else "not_retracted"), f"is_retracted={co}"


# ────────────────────────── Nguồn 2 — Europe PMC ───────────────────────────
def do_europepmc(pmid: str) -> tuple[str, str]:
    q = urllib.parse.quote(f"EXT_ID:{pmid} AND SRC:MED")
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
           f"?query={q}&resultType=core&format=json")
    try:
        _, body = _get(url)
        ket_qua = json.loads(body).get("resultList", {}).get("result", [])
    except Exception as exc:
        return "unknown", _loi_ngan(exc)
    if not ket_qua:
        return "unknown", "Europe PMC không có bản ghi cho PMID này"

    r = ket_qua[0]
    pubtypes = [str(t).lower() for t in (r.get("pubTypeList") or {}).get("pubType", [])]
    lien_ket = [
        str(c.get("type", "")).lower()
        for c in (r.get("commentCorrectionList") or {}).get("commentCorrection", [])
    ]
    dau_hieu = [t for t in pubtypes if "retract" in t] + \
               [t for t in lien_ket if "retract" in t]
    if dau_hieu:
        return "retracted", "dấu hiệu: " + ", ".join(sorted(set(dau_hieu)))
    return "not_retracted", f"pubType={pubtypes or '(trống)'}, liên kết={lien_ket or '(trống)'}"


# ────────────── Nguồn 3 — Retraction Watch (Crossref, CC0, ngoại tuyến) ──────────────
def do_retraction_watch(email: str) -> tuple[bool, str]:
    """Chỉ đọc DÒNG TIÊU ĐỀ để biết endpoint sống và có cột PMID không.

    KHÔNG tải cả file (~50 MB). Nếu có cột PMID thì đây là phương án MẠNH NHẤT khi
    không có khoá: tải một lần, tra hoàn toàn ngoại tuyến, không hạn mức nào.
    """
    url = "https://api.labs.crossref.org/data/retractionwatch?" + urllib.parse.quote(email)
    try:
        _, dau = _get(url, doc_dong_dau=8192)
    except Exception as exc:
        return False, _loi_ngan(exc)
    tieu_de = (dau.splitlines() or [""])[0]
    if not tieu_de or "," not in tieu_de:
        return False, "phản hồi không phải CSV"
    cot_pmid = re.findall(r"[A-Za-z]*PubMed[A-Za-z]*ID", tieu_de)
    if not cot_pmid:
        return True, "CSV sống nhưng KHÔNG thấy cột PubMedID → phải ánh xạ PMID→DOI"
    return True, "CSV sống, có cột " + ", ".join(sorted(set(cot_pmid)))


def _email_mac_dinh() -> str:
    """Lấy email đã cấu hình sẵn, không bịa và không hỏi lại."""
    for ten in ("OPENALEX_EMAIL", "NCBI_EMAIL", "UNPAYWALL_EMAIL"):
        if os.getenv(ten):
            return os.environ[ten]
    kho = Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"
    if kho.exists():
        for dong in kho.read_text(encoding="utf-8", errors="replace").splitlines():
            for ten in ("OPENALEX_EMAIL", "NCBI_EMAIL", "UNPAYWALL_EMAIL"):
                if dong.startswith(ten + "="):
                    gt = dong.split("=", 1)[1].strip()
                    if gt:
                        return gt
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Đo nguồn kiểm rút bài KHÔNG cần NCBI API key")
    ap.add_argument("--email", default="", help="email cho Retraction Watch (Crossref bắt buộc)")
    ap.add_argument("--bo-qua-rw", action="store_true", help="bỏ qua Retraction Watch")
    args = ap.parse_args()

    print("ĐO NGUỒN KIỂM RÚT BÀI — KHÔNG DÙNG NCBI API KEY")
    print("=" * 66)
    print("Đo bằng 2 PMID đã biết đáp án. Nguồn nào trả SAI trên fixture thì")
    print("KHÔNG được tin trên dữ liệu thật, dù nó có chạy trơn tru.\n")

    diem = {"OpenAlex": 0, "Europe PMC": 0}
    for pmid, phai_bi_rut, nhan in FIXTURES:
        print(f"── PMID {pmid} — {nhan}")
        for ten, ham in (("OpenAlex", do_openalex), ("Europe PMC", do_europepmc)):
            trang_thai, chi_tiet = ham(pmid)
            if trang_thai == "unknown":
                dau = "❓ KHÔNG BIẾT"
            else:
                dung = (trang_thai == "retracted") == phai_bi_rut
                dau = "✅ ĐÚNG" if dung else "❌ SAI"
                if dung:
                    diem[ten] += 1
            print(f"   {ten:<12} {dau:<14} {trang_thai:<14} {chi_tiet}")
        print()

    rw_song = None
    if not args.bo_qua_rw:
        email = args.email or _email_mac_dinh()
        print("── Retraction Watch (Crossref, CC0 — tra NGOẠI TUYẾN sau khi tải)")
        if not email:
            print("   ⚠  bỏ qua: Crossref bắt buộc email. Dùng --email <địa chỉ>.\n")
        else:
            print(f"   (gửi email {email} cho Crossref — đúng hợp đồng API của họ)")
            rw_song, chi_tiet = do_retraction_watch(email)
            print(f"   {'✅ tới được' if rw_song else '❌ không tới được'}  {chi_tiet}\n")

    print("=" * 66)
    dat = [t for t, d in diem.items() if d == len(FIXTURES)]
    if dat:
        print("🟢 DÙNG ĐƯỢC (đúng cả 2 fixture): " + ", ".join(dat))
    if rw_song:
        print("🟢 Retraction Watch tải được → phương án NGOẠI TUYẾN, không hạn mức.")
    if not dat and not rw_song:
        print("🔴 KHÔNG nguồn thay thế nào dùng được từ mạng này.")
        print("   Mọi PMID phải GIỮ trạng thái CHƯA kiểm rút bài (fail-closed).")
        return 2
    if not dat:
        print("🟡 Chỉ có phương án ngoại tuyến; nguồn tra trực tiếp chưa đạt.")
        return 1

    print()
    print("BƯỚC SAU (cần bác sĩ quyết, tool này KHÔNG tự làm):")
    print("  Nguồn đạt ở trên mới chỉ CHỨNG MINH LÀ TRA ĐƯỢC. Cho nó quyền nói")
    print("  'bài này chưa bị rút' bên trong cổng A12 là đổi mô hình tin cậy của")
    print("  một cổng an toàn — phải giữ nguyên 3 trạng thái rời nghĩa (đã rút /")
    print("  chưa rút / KHÔNG BIẾT) và tuyệt đối không để 'không tìm thấy' thành 'sạch'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
