#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GOM TOÀN VĂN OA CHO DASHBOARD LÂM SÀNG — kho DÙNG CHUNG theo PMID (nâng cấp A, 15/08/2026).

Vì sao: bộ máy toàn văn (gom → hỏi → đối chiếu số) đã chạy cho đề tài nghiên cứu
(C1a); phía lâm sàng `kiem_so_lieu` vẫn chỉ đọc TÓM TẮT nên tồn cả lớp ⚪ «không
thấy» dù con số nằm ngay trong thân bài. Tool này phủ kho toàn văn sang lâm sàng.

Khác bản nghiên cứu (`medical-ebm-automation/tools/gom_toan_van_oa.py` — kho THEO
ĐỀ TÀI): kho ở đây DÙNG CHUNG toàn thư mục `EBM-Dashboards/toan_van_oa/`, khoá theo
PMID, tải một lần dùng cho mọi dashboard. TÁI DÙNG nguyên hàm của bản nghiên cứu
(qua importlib — không chép đôi logic, kế thừa luôn bộ lọc `pubmed_pmc` của BH53).

P5 giữ nguyên: chỉ PMC Open Access + bản thảo tác giả PMC phát cho khai thác văn bản
(TDM) — không cào nguồn trả phí. Bài không-OA được ghi rõ, KHÔNG đoán. Chạy lại an
toàn: PMID đã có XML thì bỏ qua (idempotent).

Dùng:  python3 tools/gom_toan_van_dashboard.py            # mọi dashboard
       python3 tools/gom_toan_van_dashboard.py --file EBM-Dashboards/WebDashboard_X.html
Mã thoát: 0 = chạy trọn · 2 = KHÔNG ĐO ĐƯỢC (hạ tầng PMC chết toàn phần · kho `toan_van_oa/` vắng — không tự tạo ·
thiếu engine medical-ebm-automation).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]


def _goc_du_lieu(ten: str) -> Path:
    """Gốc dữ liệu ngoài git qua `ban_sao_tran.duong_goc` (lồng rồi anh em — TT-07, 15/10/2026: cùng cách định vị với mọi công
    cụ của kho toàn văn). Không thấy ⇒ vị trí lồng; `main` rào `KHO.is_dir()` và KHÔNG tự tạo kho (TT-05/W9)."""
    try:
        sp = importlib.util.spec_from_file_location("_bst_gtvd_goc", Path(__file__).resolve().parent / "ban_sao_tran.py")
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        return m.duong_goc(ten, REPO) or (REPO / ten)
    except Exception:  # noqa: BLE001 — thiếu bộ định vị ⇒ vị trí lồng như trước
        return REPO / ten


DASH = _goc_du_lieu("EBM-Dashboards")
KHO = DASH / "toan_van_oa"


def _ghi_nguyen_tu(dich: Path, du_lieu: bytes) -> None:
    """Ghi qua tệp tạm rồi `os.replace` (TT-01, 15/10/2026): đứt giữa chừng (hết đĩa, tiến trình bị giết) không để lại tệp CỤT
    mang tên hợp lệ — tệp cụt từng được tính là «có toàn văn». Lỗi ⇒ gỡ tệp tạm rồi ném lại (người gọi xử lý như lỗi một bài)."""
    tam = dich.with_name(dich.name + f".tam-{os.getpid()}")
    try:
        tam.write_bytes(du_lieu)
        os.replace(tam, dich)
    except OSError:
        try:
            tam.unlink(missing_ok=True)
        except OSError:
            pass
        raise


_NGUON = None


def _nap_nguon_su_that():
    """`doc_toan_van_co_nguoi` — NGUỒN SỰ THẬT độ phủ (`bao_phu_cuc_bo`), nạp RIÊNG với `_nap_dtv` (bảng điều khoản, test thay được).
    Lỗi ⇒ None: người gọi báo «KHÔNG ĐO ĐƯỢC», không lùi về đếm tên tệp."""
    global _NGUON
    if _NGUON is None:
        try:
            sp = importlib.util.spec_from_file_location("_dtv_gom_nguon", REPO / "tools" / "doc_toan_van_co_nguoi.py")
            mod = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(mod)
            _NGUON = mod
        except Exception:  # noqa: BLE001
            _NGUON = False
    return _NGUON or None


def _email_lich_su() -> str:
    """Email định danh lịch sự cho API (Unpaywall/NCBI đòi) — đọc theo đúng chuỗi
    ưu tiên của app/config.py: biến môi trường → kho secrets ngoài OneDrive."""
    import os
    e = os.environ.get("NCBI_EMAIL") or os.environ.get("UNPAYWALL_EMAIL")
    if e:
        return e
    sec = Path.home() / ".ebm-secrets" / "medical-ebm-automation.env"
    if sec.exists():
        for d in sec.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*NCBI_EMAIL\s*=\s*(\S+)", d)
            if m:
                return m.group(1).strip("'\"")
    return ""


def _chu_tho(vb: str) -> str:
    """Chữ thô của một đoạn HTML (bỏ script/style/thẻ, giải mã thực thể, gộp khoảng trắng)."""
    import html as _h
    vb = re.sub(r"<script.*?</script>|<style.*?</style>", " ", vb, flags=re.S | re.I)
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", vb)))


def _van_ban_tho(du_lieu: bytes) -> str:
    """Chữ thô CẢ TRANG — MÙ cấu trúc đề mục. Cổng toàn văn phải nhận NGUYÊN VĂN HTML (`la_toan_van_html`), không nhận chuỗi này."""
    return _chu_tho(du_lieu.decode("utf-8", errors="replace"))


_DTV = None
# Giá trị `license` của Unpaywall được coi là GIẤY PHÉP MỞ (mọi biến thể CC BY*, CC0, phạm vi công cộng).
GIAY_PHEP_MO_DUNG = ("cc0", "pd", "public-domain")
GIAY_PHEP_MO_TIEN_TO = ("cc-by",)
# PMID bị cổng điều khoản chặn ở lượt gần nhất: (pmid, doi, lý do) — để báo cáo, không phải để thử lại mù.
BO_QUA_UNPAYWALL: list[tuple[str, str, str]] = []


def _nap_dtv():
    """Nạp `tools/doc_toan_van_co_nguoi.py` (bảng điều khoản NXB + uỷ quyền bác sĩ). Lỗi ⇒ None: cổng ĐÓNG với mọi bản
    không mang giấy phép mở (fail-closed), không lặng lẽ cho qua."""
    global _DTV
    if _DTV is None:
        try:
            sp = importlib.util.spec_from_file_location("_dtv_gom_tv", REPO / "tools" / "doc_toan_van_co_nguoi.py")
            mod = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(mod)
            _DTV = mod
        except Exception:  # noqa: BLE001
            _DTV = False
    return _DTV or None


def la_giay_phep_mo(license: str | None) -> bool:
    lic = (license or "").strip().lower()
    return lic in GIAY_PHEP_MO_DUNG or lic.startswith(GIAY_PHEP_MO_TIEN_TO)


def quyet_dinh_unpaywall(doi: str, url: str, license: str | None, *, dtv=None, hom_nay=None) -> tuple[bool, str]:
    """CỔNG ĐIỀU KHOẢN của tầng 2 (04/10/2026) — trả (được LƯU tự động?, lý do). Trước bản vá, tầng này lưu MỌI bản «is_oa»
    (kể cả bản đọc-miễn-phí không giấy phép của NXB đã kết luận «cấm» dùng với AI), trái doctrine §2septies.

    CHỈ bản mang GIẤY PHÉP MỞ (CC BY*, CC0, phạm vi công cộng) được lưu tự động — chính giấy phép cho phép dùng.
    Bản không có giấy phép mở thì KHÔNG lưu, kể cả NXB «cấm» mà bác sĩ đã uỷ quyền: uỷ quyền 03/10 là uỷ quyền ĐỌC («KHÔNG lưu
    toàn văn»); lưu bản sao chỉ trong phiên uỷ quyền có lời bác sĩ, trần mỗi miền và nhịp nghỉ (`phien_uy_quyen_chrome.py`) —
    tải tự động hàng loạt là đúng thứ điều khoản NXB cấm. Lý do trả về phân loại để định tuyến:
    «cam_co_uq» → làn trình duyệt có phiên; «cam_khong_uq» → bác sĩ đọc trực tiếp; «chua_kiem» → đọc trang điều khoản trước.

    Giấy phép mở khai ở CẤP NXB (18/10/2026, `GIAY_PHEP_MO_CAP_NXB`): Unpaywall không ghi giấy phép nhưng bản OA nằm trên MIỀN
    CỦA CHÍNH NXB mà trang điều khoản (đã đọc, có nguồn + ngày) khai mọi nội dung trên miền đó mang giấy phép mở ⇒ được lưu. Xét
    SAU nhánh «cấm» — NXB «cấm» không bao giờ được hưởng nhánh này."""
    lic = (license or "").strip().lower()
    if la_giay_phep_mo(lic):
        return True, f"giấy phép mở ({lic})"
    dtv = dtv if dtv is not None else _nap_dtv()
    if dtv is None:
        return False, "khong_nap_bang: không nạp được bảng điều khoản NXB — chỉ lưu bản có giấy phép mở"
    ten, dk = dtv.nxb_cua(doi=doi or "", url=url or "")
    if ten and (dk or {}).get("ket_luan") == "cam":
        if dtv.uy_quyen_bac_si(ten, hom_nay):
            return False, (f"cam_co_uq: NXB «cấm» {ten}, bản đọc-miễn-phí không giấy phép mở — uỷ quyền ĐỌC không gồm lưu tự "
                           "động; đọc qua làn trình duyệt (phiên uỷ quyền lưu bản sao)")
        return False, f"cam_khong_uq: NXB «cấm» {ten}, chưa có uỷ quyền của bác sĩ — bác sĩ đọc trực tiếp"
    ten_cc, cc = dtv.giay_phep_mo_cap_nxb(url or "") if hasattr(dtv, "giay_phep_mo_cap_nxb") else (None, None)
    gp = tuple((cc or {}).get("giay_phep") or ())
    if ten_cc and gp and all(la_giay_phep_mo(g) for g in gp):
        return True, (f"giấy phép mở cấp NXB {ten_cc} ({', '.join(gp)}; điều khoản đọc {cc.get('doc_luc')}) — Unpaywall không "
                      "ghi giấy phép, bản nằm trên miền của chính NXB")
    if ten:
        return False, f"khac: NXB {ten} — kết luận điều khoản «{(dk or {}).get('ket_luan')}» tầng này chưa nhận"
    return False, ("chua_kiem: NXB chưa có trong DIEU_KHOAN_NXB/GIAY_PHEP_MO_CAP_NXB và bản OA không mang giấy phép mở — đọc "
                   "trang điều khoản trước")


# Dấu hiệu TRANG GIỚI THIỆU của cổng kho lưu trữ (Pure/Research Explorer, kho đại học): chỉ tóm tắt + metadata + nút tải.
# Đo 04/10/2026: 15/27 tệp `_UPW.html` trong kho là loại này (gồm 4 mục apply: CHA₂DS₂-VASc 19762550, HAS-BLED 20299623,
# EMPOWER 24733354, SUMMIT 27203508) — vượt ngưỡng 500 từ nên lọt vào kho với nhãn «toàn văn».
DAU_TRANG_GIOI_THIEU = ("Fingerprint", "Access to Document", "Link to publication", "Research output", "Accéder au contenu principal")
DE_MUC_TOAN_VAN = ("Methods", "Results", "Discussion", "Introduction", "METHODS", "RESULTS", "DISCUSSION", "INTRODUCTION")
SO_TU_TOAN_VAN_KHONG_DE_MUC = 6000  # guideline/khuyến cáo dài thường không có đề mục IMRaD (vd Tiêu chuẩn ADA: 18–26 nghìn từ)
SO_TU_TOAN_VAN_IMRAD = 2500
# Ngưỡng trên THÂN BÀI (đã bỏ References/hậu bài) — hiệu chỉnh 15/10/2026 trên 303 tệp HTML của kho: trang tường phí/giới thiệu
# có 575–1 463 từ thân bài và ≤ 5 mục nội dung; toàn văn thật KHÔNG IMRaD (tổng quan, báo cáo lâm sàng, cập nhật thực hành) có
# 4 054–5 764 từ thân bài và 10–22 mục — trước đây chúng chỉ qua ngưỡng 6000 nhờ danh mục tham khảo thổi số từ.
SO_TU_MOT_MUC = 40  # một «mục thân bài có nội dung»: đề mục ngoài tóm tắt/hậu bài, theo sau ≥ 40 từ chữ riêng
SO_MUC_TONG_QUAN = 8  # bài không IMRaD: ≥ 2500 từ thân bài + ≥ 8 mục nội dung
SO_TU_IMRAD_NGAN, SO_MUC_IMRAD_NGAN = 1500, 5  # bài ngắn: ≥ 3 nhóm IMRaD bằng THẺ đề mục + ≥ 1500 từ thân bài + ≥ 5 mục

# ĐỌC CẤU TRÚC ĐỀ MỤC (15/10/2026 — sự cố `audit/nhat-ky/2026-10-15-cong-toan-van-tuong-phi-dai.md`). Trước đó cổng nhận chữ thô
# cả trang và trả «toàn văn» cho MỌI trang ≥ 6000 từ, trước cả khi xét dấu nào: trang Nature Reviews Cardiology KHÔNG có quyền
# (PMID 27811932) chỉ có Key Points · Abstract · «Access options» — thân bài ~540 từ — nhưng danh mục tham khảo kéo tổng lên
# 8 743 từ ⇒ lọt vào kho `_CHR.html` qua phiên Chrome (TT-04 dùng chung cổng này) và có thể bị BH161 tính «đã đọc toàn văn».
# Chiều ngược (âm tính giả): CMAJ (PMID 16129869, 5 189 từ) đặt đề mục Methods · Results · Interpretation — «Interpretation» thay
# «Discussion», mở bài không đề mục — nên chỉ đếm được 2 đề mục IMRaD ⇒ toàn văn thật rơi vào sổ nợ BH161.
# Nay: (1) số từ chỉ tính THÂN BÀI — bỏ khối hậu bài (References · Author information · Rights and permissions · About this
# article…) cùng mọi tiểu mục của nó; (2) đề mục TƯỜNG PHÍ (thẻ h1–h6 — KHÔNG xét chuỗi toàn trang: trang Nature có quyền vẫn có
# «Subscribe to this journal» ở thanh bên) xét TRƯỚC mọi ngưỡng số từ: có đề mục đó mà thân bài KHÔNG tự chứng minh cấu trúc toàn
# văn ⇒ không phải toàn văn. Không dùng đề mục tường phí làm án tuyệt đối: đo 15/10, trang SAGE CÓ quyền (toàn văn đủ IMRaD —
# 40277321, 42084558, 42751933) vẫn có h4 «Access options» trong menu «View options»; (3) đề mục IMRaD đếm theo NHÓM, nhận đồng
# nghĩa (Background ≈ Introduction; Interpretation/Comment/Conclusions ≈ Discussion) nhưng CHỈ khi là thẻ đề mục nằm NGOÀI khối
# tóm tắt — tóm tắt có cấu trúc (Background/Methods/Results/Interpretation ~300 từ) không tự đủ ba nhóm; (4) bài không IMRaD được
# nhận bằng số MỤC nội dung (ngưỡng ở trên), không bằng số từ cả trang.
_LA_HTML = re.compile(r"<\s*(?:html|body|article|section|main|div|p|h[1-6])\b", re.I)
_THE_DE_MUC = re.compile(r"<(h[1-6])\b[^>]*>(.*?)</\1\s*>", re.S | re.I)
_DANH_SO = r"(?:(?:\d+(?:\.\d+)*|[IVXivx]+)[.):]?\s+)?"  # «3.», «IV.», «2.1» đứng đầu đề mục
_DUOI = r"(?:\s*\(\d+\))?\s*[:.]?"  # «References (52)», «Methods:»


def _mau_de_muc(*cum: str) -> re.Pattern:
    return re.compile(_DANH_SO + "(?:" + "|".join(cum) + ")" + _DUOI, re.I)


DE_MUC_TUONG_PHI = _mau_de_muc(
    r"access options", r"buy (?:this )?article(?: pdf)?", r"rent or buy(?: this article)?", r"purchase (?:this )?(?:pdf|article)",
    r"purchase access", r"get access(?: to (?:this|the full) article)?", r"access through your institution")
DE_MUC_HAU_BAI = _mau_de_muc(
    r"references?(?: and notes)?", r"notes and references", r"reference list", r"bibliography", r"literature cited", r"works cited",
    r"cited literature", r"tài liệu tham khảo", r"author information", r"authors? and affiliations", r"acknowledge?ments?",
    r"footnotes", r"ethics declarations", r"additional information", r"rights and permissions", r"about this article",
    r"cite this article", r"share this article", r"this article is cited by", r"cited by", r"citing articles",
    r"similar content being viewed by others", r"related articles", r"recommended articles")
DE_MUC_TOM_TAT = _mau_de_muc(r"abstract", r"structured abstract", r"summary", r"key points", r"highlights", r"graphical abstract")
NHOM_IMRAD = (
    ("mo_bai", _mau_de_muc(r"introduction", r"background")),
    ("phuong_phap", _mau_de_muc(r"methods?", r"(?:materials?|patients?|subjects|participants) and methods?", r"methodology",
                                r"study design(?: and (?:setting|participants|methods?))?")),
    ("ket_qua", _mau_de_muc(r"results?", r"results and discussion", r"findings")),
    ("ban_luan", _mau_de_muc(r"discussion", r"results and discussion", r"interpretation", r"comments?", r"conclusions?",
                             r"general discussion")),
)
# Từ khoá cũ (chuỗi trong chữ thân bài) ánh xạ vào nhóm — giữ mọi kết luận «toàn văn» cũ không phụ thuộc đề mục thẻ.
_NHOM_TU_KHOA_CU = {"Introduction": "mo_bai", "Methods": "phuong_phap", "Results": "ket_qua", "Discussion": "ban_luan"}


def phan_tich_trang_html(html: str) -> dict:
    """Tách THÂN BÀI của một trang HTML theo thẻ đề mục h1–h6. Trả {than_bai (chữ thô), tuong_phi [đề mục], hau_bai [đề mục đã bỏ],
    nhom_imrad {nhóm}, so_de_muc}. Khối hậu bài kéo tới đề mục kế tiếp CÙNG CẤP hoặc cao hơn; đề mục rỗng không phải ranh giới."""
    html = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", html, flags=re.S | re.I)
    than, tuong_phi, hau_bai, nhom = [], [], [], set()
    vi_tri, cap_bo, cap_tom_tat, so_de_muc, so_muc, muc_cho = 0, None, None, 0, 0, False
    for m in _THE_DE_MUC.finditer(html):
        doan = html[vi_tri:m.start()]
        if muc_cho and len(_chu_tho(doan).split()) >= SO_TU_MOT_MUC:
            so_muc += 1
        muc_cho = False
        if cap_bo is None:
            than.append(doan)
        vi_tri = m.end()
        chu = _chu_tho(m.group(2)).strip()
        if not chu:
            continue
        so_de_muc += 1
        cap = int(m.group(1)[1])
        if DE_MUC_TUONG_PHI.fullmatch(chu):
            tuong_phi.append(chu)
        if cap_bo is not None and cap > cap_bo:
            continue  # tiểu mục của khối hậu bài (Authors and Affiliations, Cite this article…)
        cap_bo = None
        if cap_tom_tat is not None and cap <= cap_tom_tat:
            cap_tom_tat = None
        if DE_MUC_HAU_BAI.fullmatch(chu):
            cap_bo = cap
            hau_bai.append(chu)
            continue
        than.append(f" {chu} ")
        if cap_tom_tat is not None:
            continue  # tiểu mục TRONG tóm tắt có cấu trúc — không tính đề mục thân bài
        if DE_MUC_TOM_TAT.fullmatch(chu):
            cap_tom_tat = cap
            continue
        if not DE_MUC_TUONG_PHI.fullmatch(chu):
            muc_cho = True
        nhom.update(ten for ten, mau in NHOM_IMRAD if mau.fullmatch(chu))
    if muc_cho and len(_chu_tho(html[vi_tri:]).split()) >= SO_TU_MOT_MUC:
        so_muc += 1
    if cap_bo is None:
        than.append(html[vi_tri:])
    return {"than_bai": _chu_tho(" ".join(than)), "tuong_phi": tuong_phi, "hau_bai": hau_bai, "nhom_imrad": nhom,
            "so_de_muc": so_de_muc, "so_muc_noi_dung": so_muc}


def la_toan_van_html(vb: str) -> tuple[bool, str]:
    """(có phải TOÀN VĂN?, lý do). `vb` nên là NGUYÊN VĂN HTML của trang — cổng đọc cấu trúc đề mục, mọi ngưỡng tính trên THÂN
    BÀI (đã bỏ References/hậu bài). Thứ tự: đề mục tường phí mà thân bài không tự chứng minh cấu trúc toàn văn (≥ 3 nhóm IMRaD
    bằng thẻ + ≥ 2500 từ, hoặc một trong hai luật cấu trúc cuối) ⇒ KHÔNG · ≥ 6000 từ (guideline
    dài) ⇒ CÓ · dấu trang giới thiệu kho ⇒ KHÔNG · ≥ 2500 từ + ≥ 3 nhóm IMRaD ⇒ CÓ · bài ngắn ≥ 1500 từ + ≥ 3 nhóm IMRaD bằng thẻ +
    ≥ 5 mục ⇒ CÓ · bài không IMRaD ≥ 2500 từ + ≥ 8 mục ⇒ CÓ. Chữ thô không thẻ (tương thích ngược) thì MÙ cấu trúc: luật cũ."""
    if not _LA_HTML.search(vb):
        so_tu = len(vb.split())
        de_muc = sum(1 for k in DE_MUC_TOAN_VAN if k in vb)
        dau = [k for k in DAU_TRANG_GIOI_THIEU if k in vb]
        if so_tu >= SO_TU_TOAN_VAN_KHONG_DE_MUC:
            return True, f"{so_tu} từ (chữ thô — không đọc được cấu trúc đề mục)"
        if dau:
            return False, f"trang giới thiệu kho lưu trữ ({', '.join(dau[:2])}; {so_tu} từ)"
        if so_tu >= SO_TU_TOAN_VAN_IMRAD and de_muc >= 3:
            return True, f"{so_tu} từ, {de_muc} đề mục"
        return False, f"không đủ dấu hiệu toàn văn ({so_tu} từ, {de_muc} đề mục IMRaD)"
    pt = phan_tich_trang_html(vb)
    than = pt["than_bai"]
    so_tu, muc, nhom_the = len(than.split()), pt["so_muc_noi_dung"], pt["nhom_imrad"]
    bo = f"; bỏ {len(pt['hau_bai'])} khối hậu bài" if pt["hau_bai"] else ""
    imrad_the = len(nhom_the) >= 3 and so_tu >= SO_TU_TOAN_VAN_IMRAD
    imrad_ngan = len(nhom_the) >= 3 and so_tu >= SO_TU_IMRAD_NGAN and muc >= SO_MUC_IMRAD_NGAN
    tong_quan = so_tu >= SO_TU_TOAN_VAN_IMRAD and muc >= SO_MUC_TONG_QUAN
    if pt["tuong_phi"] and not (imrad_the or imrad_ngan or tong_quan):
        return False, f"tường phí — đề mục «{pt['tuong_phi'][0]}», thân bài không có cấu trúc toàn văn ({so_tu} từ, {muc} mục{bo})"
    if so_tu >= SO_TU_TOAN_VAN_KHONG_DE_MUC:
        return True, f"{so_tu} từ thân bài{bo}"
    dau = [k for k in DAU_TRANG_GIOI_THIEU if k in _chu_tho(vb)]
    if dau:
        return False, f"trang giới thiệu kho lưu trữ ({', '.join(dau[:2])}; {so_tu} từ thân bài)"
    nhom = nhom_the | {n for k, n in _NHOM_TU_KHOA_CU.items() if k in than or k.upper() in than}
    if so_tu >= SO_TU_TOAN_VAN_IMRAD and len(nhom) >= 3:
        return True, f"{so_tu} từ thân bài, {len(nhom)} nhóm đề mục IMRaD{bo}"
    if imrad_ngan:
        return True, f"bài ngắn có cấu trúc IMRaD ({so_tu} từ thân bài, {len(nhom_the)} nhóm, {muc} mục{bo})"
    if tong_quan:
        return True, f"bài không IMRaD có cấu trúc ({so_tu} từ thân bài, {muc} mục nội dung{bo})"
    return False, f"không đủ dấu hiệu toàn văn ({so_tu} từ thân bài, {len(nhom)} nhóm đề mục IMRaD, {muc} mục{bo})"


def dem_toan_van(kho: Path) -> dict[str, set[str]]:
    """PMID có toàn văn trong kho theo LOẠI tệp ở gốc kho (XML JATS · PDF/HTML Unpaywall · _CHR phiên Chrome · TDM…) cộng
    `trinh_duyet/` (đọc qua làn trình duyệt có bác sĩ — hồ sơ trích xuất, KHÔNG lưu bản). Trước 04/10 sổ phủ chỉ đếm `*.xml`
    nên báo thấp hơn thật (203/676 trong khi 337/676 PMID đã có toàn văn hoặc đã được đọc toàn văn). Từ 15/10 (W8) chỉ là THÔNG
    TIN PHỤ theo tên tệp — số tổng độ phủ đi qua `doc_toan_van_co_nguoi.pmid_da_phu` (nguồn sự thật `bao_phu_cuc_bo`)."""
    loai: dict[str, set[str]] = {}
    for q in kho.glob("PMID-*"):
        m = re.match(r"PMID-(\d+)(?:_([A-Za-z]+))?", q.name)
        if not m or not q.is_file():
            continue
        nhan = "XML" if q.suffix.lower() == ".xml" else (m.group(2) or "khác").upper()
        loai.setdefault(nhan, set()).add(m.group(1))
    td = kho / "trinh_duyet"
    if td.is_dir():
        for q in td.glob("PMID-*"):
            m = re.match(r"PMID-(\d+)", q.name)
            if m:
                loai.setdefault("TRINH_DUYET", set()).add(m.group(1))
    return loai


def la_trang_chan_ncbi(du_lieu: bytes) -> bool:
    """NCBI chặn IP thì trả HTML «NCBI - WWW Error Blocked Diagnostic» với mã 200 — không phải JSON."""
    dau = du_lieu[:3000].lower()
    return b"blocked diagnostic" in dau or b"blocked for possible abuse" in dau


EPMC_REST = "https://www.ebi.ac.uk/europepmc/webservices/rest"


def la_jats_toan_van(du_lieu: bytes | None) -> bool:
    """JATS có thân bài — KHÔNG phải trang HTML (trang chặn NCBI cũng chứa «<body»: chỉ xét «<body» là lưu nhầm trang chặn)."""
    if not du_lieu:
        return False
    dau = du_lieu[:3000].lower()
    if b"<html" in dau or b"<!doctype html" in dau or la_trang_chan_ncbi(du_lieu):
        return False
    return b"<article" in dau and b"<body" in du_lieu


def _lay(url: str, timeout: int = 60) -> bytes:
    import urllib.request as _rq
    return _rq.urlopen(url, timeout=timeout).read()


def lien_ket_pmc_epmc(pmids: list[str], lay=None) -> dict[str, tuple[str, bool]]:
    """PMID → (PMCID chỉ phần số, có thuộc tập truy cập mở không) qua Europe PMC — đường dự phòng khi NCBI elink hỏng.

    Đo 11/10/2026: NCBI chặn IP ⇒ elink trả trang HTML ⇒ JSONDecodeError ⇒ bước gom DỪNG, bỏ cả tầng Unpaywall: lượt toàn văn
    63 chủ đề báo 49 bài «có bản truy cập mở mà chưa gom». Lỗi mạng của Europe PMC ném ra (người gọi báo hạ tầng)."""
    import json as _json
    import urllib.parse as _up
    lay = lay or _lay
    ra: dict[str, tuple[str, bool]] = {}
    for i in range(0, len(pmids), 80):
        lo = pmids[i:i + 80]
        q = _up.quote("(" + " OR ".join(f"EXT_ID:{p}" for p in lo) + ") AND SRC:MED")
        js = _json.loads(lay(f"{EPMC_REST}/search?resultType=lite&format=json&pageSize=1000&query={q}"))
        for r in (js.get("resultList") or {}).get("result") or []:
            pm, pmc = str(r.get("pmid") or ""), str(r.get("pmcid") or "")
            if pm in lo and pmc.upper().startswith("PMC"):
                ra[pm] = (pmc[3:], r.get("isOpenAccess") == "Y")
    return ra


def tai_jats(gom, pmcid: str, la_oa: bool | None, trang: dict, lay=None) -> tuple[bytes | None, str]:
    """Toàn văn JATS của một PMCID: NCBI efetch trước, NCBI chặn/lỗi/trả HTML ⇒ Europe PMC.

    Trả (JATS, "ok") · (None, "khong_oa") khi NCBI TRẢ LỜI là bài không thuộc tập OA (ghi sổ 30 ngày như cũ) ·
    (None, "khong_oa_epmc") khi Europe PMC nói không OA — KHÔNG ghi sổ (NCBI có thể có bản thảo tác giả khi hết chặn) ·
    (None, "rut_bai_pmc") khi PMC Cloud ghi bài đã rút · (None, "loi") khi chưa tải được (lượt sau thử lại).
    Trang chặn NCBI chứa «<body» ⇒ không bao giờ được lưu làm toàn văn.

    Europe PMC «không OA» trong lúc NCBI chặn/lỗi ⇒ thử PMC Cloud S3 (13/10/2026): bản thảo tác giả NIH bị Europe PMC ghi
    `isOpenAccess="N"` nhưng PMC phát cho khai thác văn bản — đúng thứ efetch NCBI vẫn trả khi không bị chặn. NCBI không chặn
    thì giữ nguyên hành vi cũ (không gọi gì)."""
    if la_oa is False:
        return tai_jats_pmc_s3(pmcid, lay) if trang.get("ncbi_chan") else (None, "khong_oa_epmc")
    if not trang.get("ncbi_chan"):
        try:
            xml = gom.tai_toan_van(pmcid)
        except Exception:  # noqa: BLE001 — lỗi mạng NCBI ⇒ thử Europe PMC
            xml = b""
        if xml is None:
            return None, "khong_oa"
        if la_jats_toan_van(xml):
            return xml, "ok"
        if xml and la_trang_chan_ncbi(xml):
            trang["ncbi_chan"] = True
            print("  ⚠ NCBI đang chặn IP này (trang «Blocked Diagnostic») — tải toàn văn qua Europe PMC cho phần còn lại")
    try:
        b = tai_jats_epmc(pmcid, lay)
    except Exception:  # noqa: BLE001
        return None, "loi"
    return (b, "ok") if b else (None, "loi")


def tai_jats_epmc(pmcid: str, lay=None) -> bytes | None:
    """JATS toàn văn của bài truy cập mở từ Europe PMC; trả về không phải JATS ⇒ None. Lỗi mạng/HTTP ném ra (chưa tải được)."""
    b = (lay or _lay)(f"{EPMC_REST}/PMC{pmcid}/fullTextXML")
    return b if la_jats_toan_van(b) else None


# PMC Cloud Service (bucket S3 công khai của NIH, không cùng hạ tầng với NCBI nên không dính lệnh chặn IP). Đo 13/10/2026 ca
# PMID 22591294 (Ray, NEJM 2012, PMC3374857, NIHMS381524): Europe PMC ghi «N», bucket có `PMC3374857.1/` với
# `license_code: "TDM"`, `is_manuscript: true`; md5 của bản XML lưu tay trùng md5 trong siêu dữ liệu.
PMC_S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
# README.txt của bucket: `license_code` là mã Creative Commons, hoặc «TDM» cho bản thảo tác giả có toàn văn dùng được cho
# khai thác văn bản. Mã khác/rỗng ⇒ không lưu.
GIAY_PHEP_PMC_TDM = "TDM"


def giay_phep_pmc_s3_cho_phep(license_code: str | None) -> bool:
    """«TDM» hoặc giấy phép mở (cùng tập với cổng Unpaywall: CC BY*, CC0, phạm vi công cộng). PMC ghi «CC BY-NC» có khoảng
    trắng nên chuẩn hoá về dạng gạch nối trước khi so."""
    lic = (license_code or "").strip()
    if lic.upper() == GIAY_PHEP_PMC_TDM:
        return True
    return la_giay_phep_mo(re.sub(r"[\s_]+", "-", lic.lower()))


def _co_khong(v) -> bool | None:
    """Cờ trong JSON của PMC: true/false (tài liệu PMC có chỗ viết «yes»/«no») — còn lại ⇒ None, tức KHÔNG BIẾT."""
    if isinstance(v, bool):
        return v
    s = v.strip().lower() if isinstance(v, str) else ""
    return True if s in ("yes", "true") else False if s in ("no", "false") else None


def phien_ban_pmc_s3(pmcid: str, lay=None) -> list[int]:
    """Các phiên bản `PMC<id>.<n>/` có trong bucket, tra bằng DANH MỤC (ListObjectsV2; tiền tố «PMC<id>.» có dấu chấm để không
    lẫn PMC<id>0…). Không thử «.1» mò: tài liệu PMC Cloud nói có bài có bản 2 mà không có bản 1. Trả về không phải danh mục S3
    hoặc danh mục bị cắt ⇒ NÉM lỗi; [] chỉ khi danh mục khẳng định bài không có trong bucket."""
    vb = (lay or _lay)(f"{PMC_S3}/?list-type=2&prefix=PMC{pmcid}.&delimiter=/").decode("utf-8", errors="replace")
    if "<ListBucketResult" not in vb:
        raise ValueError("trả về không phải danh mục S3")
    if re.search(r"<IsTruncated>\s*true", vb, flags=re.I):
        raise ValueError("danh mục S3 bị cắt — chưa chắc đã thấy mọi phiên bản")
    return sorted({int(n) for n in re.findall(rf"<Prefix>PMC{pmcid}\.(\d+)/</Prefix>", vb)})


def chon_ban_pmc_s3(pmcid: str, ds: list[tuple[int, dict]]) -> tuple[tuple[int, dict] | None, str]:
    """Chọn phiên bản được LƯU từ siêu dữ liệu MỌI phiên bản (không gọi mạng). Trả ((n, meta), "ok") ·
    (None, "loi") khi siêu dữ liệu lệch khoá (pmcid/version) hoặc cờ `is_retracted` không rõ — KHÔNG BIẾT không phải «chưa rút» ·
    (None, "rut_bai_pmc") khi BẤT KỲ phiên bản nào ghi đã rút — tín hiệu dương, không lưu bản nào ·
    (None, "khong_oa_epmc") khi không phiên bản nào mang giấy phép cho phép.

    Nhiều bản được phép ⇒ bản công bố chính thức trước bản thảo tác giả, rồi số phiên bản lớn hơn (tài liệu PMC: số lớn hơn
    KHÔNG có nghĩa là mới hơn, nên không chọn chỉ theo số)."""
    for n, md in ds:
        if not isinstance(md, dict) or md.get("pmcid") != f"PMC{pmcid}" or str(md.get("version")) != str(n):
            return None, "loi"
    rut = [_co_khong(md.get("is_retracted")) for _, md in ds]
    if any(rut):
        return None, "rut_bai_pmc"
    if None in rut:
        return None, "loi"
    duoc = [(n, md) for n, md in ds if giay_phep_pmc_s3_cho_phep(md.get("license_code"))]
    if not duoc:
        return None, "khong_oa_epmc"
    return max(duoc, key=lambda c: (_co_khong(c[1].get("is_manuscript")) is False, c[0])), "ok"


def tai_jats_pmc_s3(pmcid: str, lay=None) -> tuple[bytes | None, str]:
    """JATS từ PMC Cloud S3 cho bài Europe PMC ghi «không OA» trong lúc NCBI chặn/lỗi. Chỉ lưu khi `license_code` cho phép,
    `is_retracted` là false, md5 tệp khớp tham số `md5` trong `xml_url`, và tệp là JATS có thân bài.

    Trả (JATS, "ok") · (None, "khong_oa_epmc") khi giấy phép không cho phép hoặc bài không có trong bucket (như cũ, không ghi
    sổ) · (None, "rut_bai_pmc") · (None, "loi") khi lỗi mạng, siêu dữ liệu lạ, md5 lệch hoặc tệp không phải JATS (lượt sau
    thử lại)."""
    lay = lay or _lay
    if not re.fullmatch(r"\d{1,10}", pmcid or ""):
        return None, "loi"
    try:
        ds = [(n, json.loads(lay(f"{PMC_S3}/PMC{pmcid}.{n}/PMC{pmcid}.{n}.json"))) for n in phien_ban_pmc_s3(pmcid, lay)]
    except Exception:  # noqa: BLE001 — lỗi mạng/JSON hỏng ⇒ chưa tải được
        return None, "loi"
    if not ds:
        return None, "khong_oa_epmc"
    chon, ket_luan = chon_ban_pmc_s3(pmcid, ds)
    if chon is None:
        if ket_luan == "rut_bai_pmc":
            print(f"  ⛔ PMC Cloud ghi PMC{pmcid} ĐÃ RÚT — không lưu bản nào")
        return None, ket_luan
    n, md = chon
    m = re.fullmatch(rf"s3://pmc-oa-opendata/(PMC{pmcid}\.{n}/PMC{pmcid}\.{n}\.xml)\?md5=([0-9a-fA-F]{{32}})",
                     str(md.get("xml_url") or ""))
    if not m:
        return None, "loi"
    try:
        b = lay(f"{PMC_S3}/{m.group(1)}")
    except Exception:  # noqa: BLE001
        return None, "loi"
    if hashlib.md5(b, usedforsecurity=False).hexdigest() != m.group(2).lower():
        print(f"  ⚠ PMC Cloud PMC{pmcid}.{n}: md5 tệp XML lệch siêu dữ liệu — không lưu, lượt sau thử lại")
        return None, "loi"
    if not la_jats_toan_van(b):
        return None, "loi"
    loai = {True: "bản thảo tác giả", False: "bản công bố"}.get(_co_khong(md.get("is_manuscript")), "loại bản không rõ")
    print(f"  ✓ PMC Cloud S3: PMC{pmcid}.{n} ({loai}, giấy phép {md.get('license_code')})")
    return b, "ok"


def doi_cua_pmid(pm: str, email: str, trang_thai: dict) -> str:
    """DOI của một PMID ("" = bài KHÔNG có DOI). NCBI esummary trước, rồi Europe PMC (EXT_ID:<pmid> AND SRC:MED).

    Đo 11/10/2026: NCBI trả trang chặn cho MỌI esummary ⇒ cả 13 bài của chủ đề COPD báo «JSONDecodeError — chưa lấy
    được» như thể Unpaywall hỏng, tầng 2 không chạy được bài nào. Thấy trang chặn MỘT lần thì cả lượt không gọi NCBI nữa
    (`trang_thai["ncbi_chan"]` — gọi tiếp vào IP đang bị chặn chỉ kéo dài lệnh chặn). Lỗi mạng/JSON hỏng lẻ tẻ chỉ chuyển
    bài đó sang Europe PMC. Cả hai nguồn không trả lời được ⇒ NÉM lỗi, không trả "" (rỗng là khẳng định «không có DOI»)."""
    import json as _json
    import urllib.parse as _up
    import urllib.request as _rq
    if not trang_thai.get("ncbi_chan"):
        u = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
             f"?db=pubmed&id={pm}&retmode=json&email={email}")
        try:
            du_lieu = _rq.urlopen(u, timeout=20).read()
            if la_trang_chan_ncbi(du_lieu):
                trang_thai["ncbi_chan"] = True
                print("  ⚠ NCBI đang chặn IP này (trang «Blocked Diagnostic») — lấy DOI qua Europe PMC cho phần còn lại")
            else:
                ids = _json.loads(du_lieu)["result"][pm].get("articleids", [])
                return next((x["value"] for x in ids if x.get("idtype") == "doi"), "")
        except (OSError, ValueError, KeyError, TypeError):  # URLError/timeout là OSError; JSON hỏng là ValueError
            pass
    q = _up.quote(f"EXT_ID:{pm} AND SRC:MED")
    js = _json.loads(_rq.urlopen("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                                 f"?resultType=lite&format=json&pageSize=1&query={q}", timeout=25).read())
    kq = (js.get("resultList") or {}).get("result") or []
    if not kq:
        raise LookupError(f"Europe PMC không có bản ghi PMID {pm}")
    return kq[0].get("doi") or ""


def tang_unpaywall(pmids: list[str], gom=None) -> tuple[int, list[str]]:
    """TẦNG 2 OA — Unpaywall (bác sĩ duyệt gói ② 19/08): bài không có bản PMC vẫn
    thường có bản OA HỢP PHÁP ở repository (bản tác giả tự lưu, Gold OA ngoài PMC).
    Chỉ tải link best_oa_location do Unpaywall xác nhận — KHÔNG cào nguồn trả phí.
    Lưu PMID-<n>_UPW.pdf|.html (doc_sau không parse được PDF — phiên Claude đọc
    trực tiếp bằng skill pdf khi thẩm định). Trả (số tải được, danh sách còn thiếu)."""
    import json as _json
    import urllib.request as _rq
    email = _email_lich_su()
    if not email:
        print("  ⚠ Unpaywall cần email định danh (NCBI_EMAIL trong ~/.ebm-secrets) — bỏ tầng 2.")
        return 0, pmids
    moi_tai, con_thieu = 0, []
    BO_QUA_UNPAYWALL.clear()
    trang_thai: dict = {}
    for pm in pmids:
        try:  # DOI qua NCBI esummary, NCBI chặn/lỗi ⇒ Europe PMC
            doi = doi_cua_pmid(pm, email, trang_thai)
            if not doi:
                con_thieu.append(pm)
                continue
            uj = _json.loads(_rq.urlopen(
                f"https://api.unpaywall.org/v2/{doi}?email={email}", timeout=25).read())
            loc = uj.get("best_oa_location") or {}
            url = loc.get("url_for_pdf") or loc.get("url")
            if not (uj.get("is_oa") and url):
                con_thieu.append(pm)
                continue
            # CỔNG ĐIỀU KHOẢN — xét TRƯỚC khi mở nội dung (04/10/2026)
            duoc, ly_do = quyet_dinh_unpaywall(doi, url, loc.get("license"))
            if not duoc:
                BO_QUA_UNPAYWALL.append((pm, doi, ly_do))
                print(f"  ⛔ Unpaywall {pm}: KHÔNG lưu — {ly_do}")
                con_thieu.append(pm)
                continue
            req = _rq.Request(url, headers={"User-Agent": "Mozilla/5.0 (EBM-OA-fetch)"})
            phan_hoi = _rq.urlopen(req, timeout=40)
            du_lieu = phan_hoi.read()
            url_cuoi = phan_hoi.geturl() or url
            # Link trỏ về PMC → lấy JATS CHUẨN qua đúng đường PMC (doc_sau/RAG
            # parse được), không giữ bản HTML trang web
            m_pmc = (re.search(r"pmc\.ncbi\.nlm\.nih\.gov/articles/PMC(\d+)", url_cuoi)
                     or re.search(r"/articles/PMC(\d+)/", du_lieu[:4000].decode(
                         "utf-8", errors="replace")))
            if m_pmc and gom is not None:
                xml = gom.tai_toan_van(m_pmc.group(1))
                if xml:
                    _ghi_nguyen_tu(KHO / f"PMID-{pm}_PMC{m_pmc.group(1)}.xml", xml)
                    moi_tai += 1
                    print(f"  ✓ Unpaywall→PMC JATS: {pm} (PMC{m_pmc.group(1)})")
                    time.sleep(0.4)
                    continue
            if du_lieu[:5] == b"%PDF-":
                _ghi_nguyen_tu(KHO / f"PMID-{pm}_UPW.pdf", du_lieu)
                moi_tai += 1
                print(f"  ✓ Unpaywall: {pm} → PDF ({len(du_lieu)//1024} KB)")
                time.sleep(0.4)
                continue
            # CỔNG NỘI DUNG THẬT (bẫy đo được 19/08: trang chặn-cookie 15 từ suýt
            # vào kho làm «toàn văn» — tuần sau máy đọc rác mà tưởng đã thẩm định)
            vb = _van_ban_tho(du_lieu)
            la_tv, vi_sao = la_toan_van_html(du_lieu.decode("utf-8", errors="replace"))  # NGUYÊN VĂN HTML: cổng đọc đề mục
            if not la_tv or "Cookies must be enabled" in vb:
                print(f"  ⚠ Unpaywall {pm}: trang trả về KHÔNG phải toàn văn ({vi_sao}) — từ chối, không lưu")
                con_thieu.append(pm)
                continue
            _ghi_nguyen_tu(KHO / f"PMID-{pm}_UPW.html", du_lieu)
            moi_tai += 1
            print(f"  ✓ Unpaywall: {pm} → HTML ({len(vb.split())} từ chữ thật)")
            time.sleep(0.4)
        except Exception as exc:  # noqa: BLE001 — lỗi MỘT bài không giết cả lượt
            print(f"  ⚠ Unpaywall {pm}: {type(exc).__name__} — chưa lấy được, lần sau thử lại")
            con_thieu.append(pm)
    return moi_tai, con_thieu


def pmid_co_pdf(kho: Path) -> set[str]:
    """PMID có ít nhất một tệp PDF trong kho (`PMID-<n>_<NGUỒN>.pdf`)."""
    ra: set[str] = set()
    if kho.is_dir():
        for q in kho.glob("PMID-*_*.pdf"):
            m = re.fullmatch(r"PMID-(\d{1,9})_[A-Za-z]+\.pdf", q.name, flags=re.I)
            if m:
                ra.add(m.group(1))
    return ra


def gan_vao_endnote(pmids: list[str], kho: Path, nap=None) -> None:
    """PDF mới của lượt gom ⇒ gắn ngay vào bản ghi cùng PMID trong EndNote (11/10/2026; `nap_endnote_chu_de.py --gan-kho`).

    Chỉ khi thư viện ĐANG mở (không tự bật EndNote); chưa cấu hình/không phải Mac ⇒ một dòng ⚪; mọi lỗi chỉ thành một dòng ⚪
    — lượt gom đã ghi kho không bao giờ hỏng vì bước phụ này."""
    if not pmids:
        return
    try:
        if nap is None:
            sp = importlib.util.spec_from_file_location("_nap_endnote_gom", Path(__file__).resolve().parent
                                                        / "nap_endnote_chu_de.py")
            nap = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(nap)
        nap.main(["--gan-kho", "--pmid", *pmids, "--kho-toan-van", str(kho), "--ap-dung",
                  "--chi-khi-dang-mo", "--im-khi-chua-cau-hinh"])
    except Exception as e:  # noqa: BLE001
        print(f"  ⚪ EndNote: chưa gắn được — {type(e).__name__}")


def _nap_gom():
    import importlib.util as _ilu_mea
    _sp_mea = _ilu_mea.spec_from_file_location("_bst_gtvd", Path(__file__).resolve().parent / "ban_sao_tran.py")
    _bst_mea = _ilu_mea.module_from_spec(_sp_mea)
    _sp_mea.loader.exec_module(_bst_mea)
    duong = (_bst_mea.duong_goc("medical-ebm-automation", REPO) or (REPO / "medical-ebm-automation")) / "tools" / "gom_toan_van_oa.py"
    sp = importlib.util.spec_from_file_location("gom_tv_nc", duong)
    m = importlib.util.module_from_spec(sp)
    sys.modules["gom_tv_nc"] = m
    sp.loader.exec_module(m)
    return m


def pmids_tu_dashboard(f: Path) -> set[str]:
    t = f.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"pmid['\"]?\s*[:=]\s*['\"](\d{6,9})['\"]", t, re.I))


def main() -> int:
    ap = argparse.ArgumentParser(description="Gom toàn văn PMC-OA dùng chung cho dashboard")
    ap.add_argument("--file", nargs="*", help="dashboard cụ thể (mặc định: tất cả)")
    ap.add_argument("--queue", nargs="*",
                    help="file queue/tuan-*.md — gom PMID trong thẻ gói tuần "
                         "(mở rộng 18/08: dây chuyền tuần từng thẩm định 100%% từ tóm tắt)")
    ap.add_argument("--pmid", nargs="*", help="PMID chỉ định thêm")
    ap.add_argument("--unpaywall", action="store_true",
                    help="tầng 2 OA: bài không-PMC thử Unpaywall (bản OA hợp pháp ngoài PMC)")
    ap.add_argument("--gioi-han", type=int, default=0,
                    help="chỉ xử lý N PMID chưa có mỗi lần chạy (0 = không giới hạn)")
    a = ap.parse_args()
    chi_dinh = bool(a.queue or a.pmid)
    files = ([Path(p) for m in a.file for p in glob.glob(m)] if a.file
             else [] if chi_dinh else sorted(DASH.glob("WebDashboard_*.html")))
    files = [f for f in files if f.exists()]
    if not files and not chi_dinh:
        print("✗ Không thấy dashboard nào.")
        return 2
    pmids: set[str] = set()
    for f in files:
        pmids |= pmids_tu_dashboard(f)
    for m in (a.queue or []):
        for q in glob.glob(m):
            qt = Path(q).read_text(encoding="utf-8", errors="replace")
            pmids |= set(re.findall(r"PMID[ :]?(\d{6,9})", qt))
    pmids |= {pm for pm in (a.pmid or []) if re.fullmatch(r"\d{6,9}", pm)}
    # KHÔNG tự tạo kho (TT-05/W9, 15/10/2026): trước đó `KHO.mkdir(parents=True)` dựng `EBM-Dashboards/toan_van_oa` ngay trong cây
    # git của bản sao trần/worktree ⇒ cờ «bản sao trần» đảo, các chốt ⚪ thành FAIL, và lượt sau ghi vào kho ma không ai đọc.
    if not KHO.is_dir():
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy kho {KHO} (EBM-Dashboards/ vắng ở cây này) — KHÔNG tự tạo kho, KHÔNG gom. "
              "Máy thật lần đầu: tạo thư mục kho bằng tay rồi chạy lại.")
        return 2
    da_co = {re.search(r"PMID-(\d+)_", p.name).group(1) for p in KHO.glob("PMID-*.xml")}
    # Sổ «không lấy được» CÓ HẠN DÙNG 30 ngày (vá 15/08 chiều — bản đầu là danh
    # sách trần, tức SỔ ĐEN VĨNH VIỄN: một bài vào PMC-OA muộn (embargo hết,
    # tác giả nộp bản OA…) sẽ không bao giờ được thử lại. Tập OA là tập LỚN DẦN
    # theo thời gian — sổ nhớ phải già đi cùng nó. Dòng: «PMID yyyy-mm-dd»;
    # dòng cũ chỉ có PMID (không ngày) = hết hạn ngay, thử lại lượt này.
    ghi_chu = KHO / "khong-oa.txt"
    khong_pmc_cu: dict[str, str] = {}
    if ghi_chu.exists():
        for dong in ghi_chu.read_text(encoding="utf-8").split("\n"):
            phan = dong.split()
            if phan:
                khong_pmc_cu[phan[0]] = phan[1] if len(phan) > 1 else ""
    han = (date.today() - __import__("datetime").timedelta(days=30)).isoformat()
    con_han = {pm for pm, ngay in khong_pmc_cu.items() if ngay and ngay > han}
    can = sorted(pmids - da_co - con_han)
    if a.gioi_han:
        can = can[: a.gioi_han]
    print(f"Kho chung: {len(da_co)} toàn văn sẵn có · {len(pmids)} PMID trong "
          f"{len(files)} dashboard · cần tra lần này: {len(can)}")
    if not can and not a.unpaywall:
        print("✓ Không có gì mới để gom.")
        return 0
    # (họ lỗi return-sớm 12/08: khi --unpaywall bật, KHÔNG thoát ở đây — tầng 2
    # nằm sau và xét tập thiếu độc lập với sổ back-off của tầng PMC)
    try:
        gom = _nap_gom()
    except Exception as exc:  # noqa: BLE001 — vắng engine ⇒ một dòng ⚪, không traceback (W9, 15/10/2026)
        print(f"⚪ KHÔNG ĐO ĐƯỢC — thiếu engine medical-ebm-automation/tools/gom_toan_van_oa.py ({type(exc).__name__}) — "
              "bỏ gom, KHÔNG kết luận độ phủ.")
        return 2
    # NCBI hỏng/chặn ⇒ Europe PMC (11/10/2026). Trước đây elink hỏng là `return 2` NGAY — bỏ luôn tầng Unpaywall.
    ha_tang_loi, qua_epmc = False, False
    anh_xa: dict[str, tuple[str, bool | None]] = {}
    if can:
        try:
            anh_xa = {pm: (pmc, None) for pm, pmc in gom.lien_ket_pmc(can).items()}
        except Exception as exc:  # noqa: BLE001
            print(f"  ⚠ NCBI elink không trả lời ({type(exc).__name__}) — đổi PMID→PMCID qua Europe PMC")
            qua_epmc = True
            try:
                anh_xa = lien_ket_pmc_epmc(can)
            except Exception as exc2:  # noqa: BLE001
                print(f"🔴 HẠ TẦNG: cả NCBI elink lẫn Europe PMC không trả lời ({type(exc2).__name__}) — tầng PMC chưa "
                      "gom, KHÔNG kết luận độ phủ (tầng Unpaywall vẫn chạy).")
                ha_tang_loi = True
    moi, khong_oa, khong_pmc, rut_bai_pmc = 0, [], [], []
    loi_mang = 0
    trang = {"ncbi_chan": qua_epmc}
    for pm in ([] if ha_tang_loi else can):
        pmcid, la_oa = anh_xa.get(pm, (None, None))
        if not pmcid:
            if not qua_epmc:   # Europe PMC thiếu bản ghi ≠ «không có bản PMC» — không ghi sổ 30 ngày
                khong_pmc.append(pm)
            continue
        # Lỗi MỘT bài không được giết CẢ lượt (đo thật 15/08: IncompleteRead ở file
        # 17/600 làm mất trọn lượt chạy dài). Bài lỗi mạng KHÔNG vào danh sách
        # «không-OA» — đó là CHƯA TẢI ĐƯỢC, lần chạy sau thử lại (idempotent).
        xml, ket_luan = tai_jats(gom, pmcid, la_oa, trang)
        if ket_luan == "ok":
            _ghi_nguyen_tu(KHO / f"PMID-{pm}_PMC{pmcid}.xml", xml)
            moi += 1
            time.sleep(0.34)
        elif ket_luan == "khong_oa":
            khong_oa.append(pm)
        elif ket_luan == "loi":
            loi_mang += 1
        elif ket_luan == "rut_bai_pmc":
            rut_bai_pmc.append(pm)
    if loi_mang:
        print(f"  ⚠ {loi_mang} bài lỗi mạng lượt này — CHƯA tải được (không phải "
              "không-OA); chạy lại tool sẽ thử tiếp.")
    if rut_bai_pmc:
        print(f"  ⛔ PMC Cloud ghi ĐÃ RÚT {len(rut_bai_pmc)} bài ({', '.join(rut_bai_pmc)}) — không lưu; tra lại bằng "
              "chuỗi rút bài 3 tầng trước khi dùng.")
    # ghi sổ «không lấy được» KÈM NGÀY — mục vừa tra nhận ngày hôm nay; mục còn
    # hạn giữ nguyên ngày cũ; mục hết hạn mà lượt này không tra tới thì rơi khỏi sổ
    if a.unpaywall:
        # Tầng 2 xét TRỰC TIẾP tập còn thiếu trong kho — KHÔNG để sổ 30-ngày của
        # tầng PMC chặn (sổ đó ghi «không có bản PMC»; Unpaywall là nguồn KHÁC
        # chưa từng thử — back-off của nguồn này không được gác cửa nguồn kia).
        # Bỏ qua CHỈ PMID mà kho đã có TỆP toàn văn thật theo nguồn sự thật `bao_phu_cuc_bo` (W3, 15/10/2026): trước đó mọi tệp
        # `PMID-<n>_*.*` — kể cả `_MCP.md`, tệp tạm, trang giới thiệu kho `_UPW.html` — loại PMID khỏi tầng Unpaywall VĨNH VIỄN.
        nguon = _nap_nguon_su_that()
        if nguon is not None:
            da_bat_ky = {pm for pm, t in nguon.bao_phu_cuc_bo(sorted(pmids), KHO).items()
                         if t in nguon.TRANG_THAI_CO_TEP_TOAN_VAN}
        else:  # không nạp được nguồn sự thật ⇒ giữ quy tắc thận trọng cũ (không thử lại PMID đã có bất kỳ tệp nào)
            da_bat_ky = {re.search(r"PMID-(\d+)_", q.name).group(1) for q in KHO.glob("PMID-*_*.*")}
        thu = sorted(pmids - da_bat_ky)
        if thu:
            print(f"  Tầng 2 Unpaywall: thử {len(thu)} bài không có bản PMC…")
            pdf_truoc = pmid_co_pdf(KHO)
            upw_moi, _ = tang_unpaywall(thu, gom=gom)
            moi += upw_moi
            pdf_moi = sorted(pmid_co_pdf(KHO) - pdf_truoc)
            if pdf_moi and not os.environ.get("PYTEST_CURRENT_TEST"):  # dưới pytest không chạm EndNote thật
                gan_vao_endnote(pdf_moi, KHO)
    hom_nay = date.today().isoformat()
    so_moi = {pm: ngay for pm, ngay in khong_pmc_cu.items() if pm in con_han}
    for pm in list(khong_pmc) + list(khong_oa):
        so_moi[pm] = hom_nay
    ghi_chu.write_text("\n".join(f"{pm} {ngay}" for pm, ngay in sorted(so_moi.items()))
                       + "\n", encoding="utf-8")
    loai = dem_toan_van(KHO)
    # Số TỔNG đi qua nguồn sự thật `bao_phu_cuc_bo` (W8, 15/10/2026) — trước đó là hợp mọi tên tệp `PMID-*` (trang giới thiệu kho
    # lưu trữ, `_MCP.md`, tệp tạm đều thành «có toàn văn»; «bác sĩ đã đọc» lại không được đếm) ⇒ sổ báo phủ cao hơn thật.
    # Đếm theo loại tệp giữ làm THÔNG TIN PHỤ. Không nạp được nguồn sự thật ⇒ «KHÔNG ĐO ĐƯỢC», không lùi về đếm tên tệp.
    nguon = _nap_nguon_su_that()
    da_co_sau = nguon.pmid_da_phu(KHO, pmids) if nguon is not None else None
    tong_co = len(da_co_sau) if da_co_sau is not None else "KHÔNG ĐO ĐƯỢC"
    phu_quet = len(pmids & da_co_sau) if da_co_sau is not None else "?"
    chi_tiet = " · ".join(f"{k} {len(v)}" for k, v in sorted(loai.items()))
    bo_qua = "".join(f"  - {pm} (doi:{d}) — {ly}\n" for pm, d, ly in BO_QUA_UNPAYWALL)
    (KHO / "DO-PHU-OA.md").write_text(
        f"# ĐỘ PHỦ TOÀN VĂN — kho dùng chung dashboard — {date.today().isoformat()}\n\n"
        f"- Kho có toàn văn (hoặc đã đọc toàn văn qua làn trình duyệt / bác sĩ đã đọc trực tiếp) cho **{tong_co}** PMID; "
        f"tập vừa quét phủ **{phu_quet}/{len(pmids)}** — theo nguồn sự thật `doc_toan_van_co_nguoi.bao_phu_cuc_bo`\n"
        f"- Theo loại TÊN tệp (thông tin phụ, KHÔNG phải độ phủ — một PMID có thể nhiều loại): {chi_tiet or '—'}\n"
        f"- Lượt này: +{moi} tải mới · {len(khong_oa)} có PMC nhưng không-OA · "
        f"{len(khong_pmc)} không có bản PMC\n"
        + (f"- PMC Cloud ghi ĐÃ RÚT — không lưu, tra chuỗi rút bài: {', '.join(rut_bai_pmc)}\n" if rut_bai_pmc else "")
        + (f"- Tầng 2 Unpaywall — KHÔNG lưu vì điều khoản NXB ({len(BO_QUA_UNPAYWALL)}):\n{bo_qua}" if BO_QUA_UNPAYWALL else "")
        + "\n> Phần không-OA cần quyền truy cập của bác sĩ — độ phủ thấp là SỰ THẬT về OA,\n"
        "> không phải lỗi. Cần bác sĩ kiểm chứng.\n", encoding="utf-8")
    print(f"  +{moi} toàn văn mới · không-OA {len(khong_oa)} · không-PMC {len(khong_pmc)} "
          f"→ kho {tong_co}/{len(pmids)} PMID")
    return 2 if ha_tang_loi else 0   # tầng PMC chưa gom được ⇒ người gọi KHÔNG được kết luận độ phủ


if __name__ == "__main__":
    raise SystemExit(main())
