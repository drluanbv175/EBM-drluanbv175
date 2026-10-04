#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỌC SÂU TOÀN VĂN — bóc chi tiết có cấu trúc cho thẩm định lâm sàng (18/08/2026; mở rộng 03/10/2026).

VÌ SAO CÓ
=========
Đo 18/08: kho toàn văn phủ 170/579 PMID của dashboard CŨ, nhưng 0/12 PMID của gói
tuần W34 — dây chuyền TUẦN (nơi chứng cứ MỚI đến tay bác sĩ) thẩm định 100% từ
TÓM TẮT, kể cả khi bài là OA nằm sẵn trên PMC. Tóm tắt không có: cách chọn ngẫu
nhiên, làm mù, ITT, tỷ lệ biến cố từng nhánh, phân nhóm, hạn chế tự khai, tài trợ.
Thiếu các mục đó thì mọi thẻ chỉ đáng «Cân nhắc» — và đúng là appraisalCompleteness
partial đã chặn trần như vậy (ghi nhớ 18/08: «tường phí chặn mức apply»).

Tool này đọc kho `EBM-Dashboards/toan_van_oa/` (đã gom bằng `gom_toan_van_dashboard.py`)
và xuất MỖI PMID một bản đọc-sâu markdown:

  · Nhận diện (tạp chí · năm · DOI · PMCID) + mã ĐĂNG KÝ (NCT/ChiCTR/PROSPERO…)
  · PHƯƠNG PHÁP nguyên văn (thiết kế, quần thể, mù, kết cục)
  · KẾT QUẢ nguyên văn + danh sách CÂU MANG HIỆU SỐ (RR/HR/OR/CI/%… để đối chiếu)
  · HẠN CHẾ tác giả tự khai · TÀI TRỢ & XUNG ĐỘT LỢI ÍCH

TRUNG THỰC PHẠM VI — bốn luật cứng:
  1. CHỈ TRÍCH NGUYÊN VĂN theo mục, kèm nguồn mục — không tóm tắt thay, không
     diễn giải thay, không chấm điểm. Việc THẨM ĐỊNH là của người đọc (bác sĩ,
     hoặc phiên Claude gói tuần đọc bản này rồi tự chịu trách nhiệm câu chữ).
  2. PMID chưa có toàn văn trong kho → nói rõ «chỉ tóm tắt», KHÔNG đoán.
  3. Mục dài bị CẮT có ghi chú rõ tại chỗ cắt — không cắt im lặng.
  4. Bài CÓ BẢN QUYỀN (PDF kênh TDM của NXB) → chỉ DỮ KIỆN + vị trí trang + trích ≤ 15 từ/lần.

MỞ RỘNG 03/10/2026 — «có tệp toàn văn» khác xa «đã đọc»
========================================================
Đo 03/10/2026 trên 72 dashboard: 18/163 PMID của mục `decision='apply'` và 21/674 PMID toàn kho có bản đọc
sâu; kho nằm sẵn tệp cho 68 PMID apply chưa ai đọc (39 XML PMC · 11 `_UPW.*` · 18 `_WTDM.pdf`). Hai nguyên nhân
ở chính tool này:
  (a) chỉ nhận *.xml, `PMID-<n>_UPW.*` và `trinh_duyet/` — KHÔNG nhận `PMID-<n>_WTDM.pdf` (PDF tải qua kênh TDM
      của Wiley bằng token của bác sĩ; quy ước tên + trạng thái «tdm_nxb» ở `tools/doc_toan_van_co_nguoi.py`)
      ⇒ 18 PMID apply có PDF hợp lệ vẫn bị gói tuần (bước 4b) báo «CHỈ TÓM TẮT»;
  (b) chỉ chạy theo --queue/--pmid ⇒ 200/203 PMID dashboard có XML chưa từng qua bộ bóc.
Vá:
  · PDF kênh TDM đọc bằng pypdf (có sẵn trong ~/.ebm-venv, khoá ở requirements của repo y khoa; KHÔNG tự cài —
    thiếu thì báo «không đọc được PDF — thiếu thư viện», không gãy). Bài có bản quyền, KHÔNG phải OA ⇒ bản đọc
    chỉ ghi dữ kiện (bản đồ mục, mã đăng ký, dấu hiệu phương pháp) + VỊ TRÍ TRANG + trích ≤ 15 từ/lần (cùng trần
    TRAN_TU_TRICH của làn trình duyệt) — KHÔNG chép đoạn văn như bản OA JATS. Văn bản < 3000 ký tự (ảnh quét,
    trang bìa) ⇒ lỗi, không sinh bản đọc giả.
  · --dashboard [tệp …] (mặc định mọi WebDashboard_*.html, bỏ bản .bak) + --chi-apply: PMID lấy bằng CHÍNH bộ
    tách mục của cổng (`verify_dashboard.extract_data_block/split_items/field`); số đếm theo ĐƠN VỊ PMID. Bản đọc
    máy đã có thì giữ (--lam-lai để sinh lại); --queue/--pmid giữ hành vi cũ (luôn sinh lại bản đọc máy).
  · Bản đọc của LÀN TRÌNH DUYỆT CÓ BÁC SĨ (có `trinh_duyet/PMID-<n>.json`) KHÔNG BAO GIỜ bị ghi đè — trước bản vá,
    XML về kho sau lượt đọc trình duyệt thì bộ bóc JATS ghi đè im lặng `doc_sau/PMID-<n>.md`.
  · --dash <thư mục EBM-Dashboards>: chạy từ worktree (cây git không chứa dữ liệu ngoài git); kho vắng ⇒ KHÔNG
    ĐO ĐƯỢC (mã 2), không kết luận «chỉ tóm tắt».

Dùng:  python3 tools/doc_sau_toan_van.py --queue queue/tuan-2026-W34.md
       python3 tools/doc_sau_toan_van.py --pmid 42587114 42605418
       python3 tools/doc_sau_toan_van.py --dashboard --chi-apply            # PMID mục apply của mọi dashboard
       python3 tools/doc_sau_toan_van.py --dashboard EBM-Dashboards/WebDashboard_X.html [--lam-lai]
       python3 tools/doc_sau_toan_van.py --dashboard --dash <cây OneDrive>/EBM-Dashboards   # chạy từ worktree
Ra:    EBM-Dashboards/toan_van_oa/doc_sau/PMID-<n>.md   (khoá theo PMID, dùng lại
       được giữa các tuần — không theo tuần)
Mã thoát: 0 = chạy trọn · 1 = không có PMID đầu vào · 2 = KHÔNG ĐO ĐƯỢC (không thấy kho/dashboard).
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import glob
import html
import importlib.util
import json
import logging
import os
import re
import sys
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"
KHO = DASH / "toan_van_oa"
# Bộ tách mục DÙNG CHUNG với cổng liêm chính — bản vendor qua git (luôn có trên mọi checkout, kể cả worktree/CI).
VERIFY_DASHBOARD = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"

# Nhận mục theo TIÊU ĐỀ sec — JATS không bắt buộc @sec-type nên khớp cả hai
NHAN_MUC = {
    "phuong_phap": re.compile(r"method|material|design|participant|patients and|"
                              r"study population|phương pháp", re.I),
    "ket_qua": re.compile(r"^result|kết quả", re.I),
    "ban_luan": re.compile(r"discussion|bàn luận", re.I),
}
MA_DANG_KY = re.compile(r"\b(NCT\d{8}|ISRCTN\d{8}|ChiCTR\d{9,}|CRD\d{11}|"
                        r"UMIN\d{9}|IRCT[\w\d]+|ACTRN\d{14})\b")
CAU_HIEU_SO = re.compile(r"(\d+[·.,]\d+\s*%?|\b\d+\s*%)\D{0,40}"
                         r"(CI|RR|HR|OR|MD|SMD|IRR|aOR|aHR|RD)|"
                         r"\b(RR|HR|OR|MD|SMD|IRR|aOR|aHR)\b\s*[=:]?\s*\d|"
                         r"\bp\s*[<=≤]\s*0[·.,]\d+", re.I)

# ── PDF kênh TDM của NXB (03/10/2026) ──────────────────────────────────────────────────────────────────────────────
# Kỷ luật trích cho bài CÓ BẢN QUYỀN: ≤ 15 từ/lần — CÙNG trần với làn trình duyệt (doc_toan_van_co_nguoi.TRAN_TU_TRICH);
# ngưỡng văn bản tối thiểu = doc_toan_van_co_nguoi.TOI_THIEU_KY_TU. Test khoá từng cặp hằng bằng nhau.
TRAN_TU_TRICH = 15
TOI_THIEU_KY_TU_PDF = 3000
TRAN_TRICH_PDF = {"hieu_so": 10, "khuyen_cao": 4, "han_che": 2, "tai_tro": 3}
NHAN_NGUON_TDM = "kênh TDM của NXB (Wiley) — có bản quyền, KHÔNG phải OA"
CAU_NGUON_TDM = "tải bằng token của bác sĩ, chỉ dùng theo giấy phép TDM"
# PDF lưu trong PHIÊN UỶ QUYỀN Chrome của bác sĩ (04/10/2026, tools/phien_uy_quyen_chrome.py) — cùng bộ bóc PDF, KHÁC nhãn nguồn:
# không phải token TDM, không phải OA; điều khoản NXB không đổi.
NHAN_NGUON_CHR = "phiên uỷ quyền Chrome của bác sĩ — có bản quyền, KHÔNG phải OA"
CAU_NGUON_CHR = "tải bằng tài khoản của bác sĩ trong phiên bác sĩ đã uỷ quyền; điều khoản NXB không đổi — chỉ dùng cá nhân"

_SO_MUC = r"(?:\d{1,2}(?:\.\d{1,2})*\.?|[IVX]{1,4}\.)?\s*\|?\s*"
_MUC_PDF = {
    "phuong_phap": r"(?:(?:materials?|patients?|participants?|subjects?)\s+and\s+)?methods?|methodology|study\s+design",
    "ket_qua": r"results?|findings",
    "ban_luan": r"discussion",
    "han_che": r"(?:strengths?\s+and\s+)?limitations?(?:\s+of\s+(?:the|this)\s+(?:study|review|guideline))?",
    "tai_tro": (r"funding(?:\s+(?:information|sources?|statement))?|sources?\s+of\s+funding|financial\s+support|"
                r"conflicts?\s+of\s+interests?(?:\s+statements?)?|competing\s+interests?|"
                r"declarations?\s+of\s+(?:competing\s+)?interests?|disclosures?"),
    "tai_lieu": r"references?|bibliography|literature\s+cited",
    "tom_tat": r"abstract|summary",
    "khac": (r"introduction|background|conclusions?|acknowledge?ments?|data\s+availability(?:\s+statement)?|"
             r"author\s+contributions?|supporting\s+information|appendix"),
}
# Mục NGẮN không kéo dài vô hạn: quá trần ký tự mà chưa gặp tiêu đề mới ⇒ trả về mục trước nó. Đo 03/10/2026: dòng
# «Funding information» ở cột bên trang 2 của guideline EAACI (PMID 34343358) làm cả 13 trang thân bài thành «tài trợ».
TRAN_KY_TU_MUC_NGAN = {"tai_tro": 2500, "han_che": 4000}
_TIEU_DE_PDF = {k: re.compile(r"^\s*" + _SO_MUC + "(?:" + v + r")\s*:?\s*$", re.I) for k, v in _MUC_PDF.items()}
_TEN_MUC_PDF = {"phuong_phap": "Phương pháp", "ket_qua": "Kết quả", "ban_luan": "Bàn luận", "han_che": "Hạn chế",
                "tai_tro": "Tài trợ/COI", "tai_lieu": "Tài liệu tham khảo"}
# Câu NHIỄU: giống mục tài liệu tham khảo (trích dẫn «2019;380:1509», doi, URL — kể cả «https:/ /» do bản in tách)
# hoặc dòng ORCID (tên + mã tác giả) — không lấy làm trích.
_NHIEU = re.compile(r"(?:19|20)\d{2}\s*;\s*\d+\s*(?:\(\d+\))?\s*:\s*\d+|\bdoi\s*:|https?:/\s*/|\bORCID\b", re.I)
# Hiệu số trong PDF: chữ viết tắt PHẢI viết hoa + có số ngay sau (regex JATS cũ không phân biệt hoa-thường nên «OR»/«CI»
# khớp cả «or»/«cirrhosis» — đo trên PDF thật 03/10/2026); cụm từ đầy đủ thì không phân biệt. «¼» = dấu «=» bản in
# Wiley trích sai mã chữ (đo: «P ¼ 0.37»).
CAU_HIEU_SO_PDF = re.compile(
    r"\b(?:CI|RR|HR|OR|MD|SMD|WMD|IRR|aOR|aHR|RD|ARR|NNT|NNH)\b[^.;]{0,25}?\d"
    r"|(?i:\b(?:hazard|odds|risk|rate)\s+ratios?|\brelative\s+risks?|\b(?:standardi[sz]ed\s+)?mean\s+differences?"
    r"|\bconfidence\s+intervals?)[^.;]{0,40}?\d"
    r"|(?i:\bp\s*[<=≤¼]\s*0?[·.,]\d+)")
_KHUYEN_CAO = re.compile(r"\b(?:strong|conditional|weak)\s+recommendation|\bgood\s+practice\s+(?:point|statement)|"
                         r"\blevel\s+of\s+evidence\b|\bclass\s+(?:I{1,3}|IIa|IIb)\b|\bgrade\s+[A-D]\b", re.I)
_HAN_CHE = re.compile(r"\blimitations?\b|\bweakness(?:es)?\b|interpreted\s+with\s+caution", re.I)
_TAI_TRO = re.compile(r"\bfund(?:ed|ing)\b|\bgrants?\b|\bsponsor|conflicts?\s+of\s+interest|competing\s+interest|"
                      r"\bdisclos|\bhonorari", re.I)
DAU_HIEU_PP = (
    ("Ngẫu nhiên hoá", re.compile(r"\brandomi[sz]", re.I)),
    ("Che giấu phân bổ", re.compile(r"allocation\s+conceal", re.I)),
    ("Làm mù", re.compile(r"\b(?:double|single|triple)[-\s]blind|\bblind(?:ed|ing)\b|\bmask(?:ed|ing)\b", re.I)),
    ("ITT / per-protocol", re.compile(r"intention[-\s]to[-\s]treat|\bITT\b|\bper[-\s]protocol\b", re.I)),
    ("Mất theo dõi", re.compile(r"lost\s+to\s+follow[-\s]?up|loss\s+to\s+follow[-\s]?up|\bdrop[-\s]?outs?\b", re.I)),
    ("Nguy cơ sai lệch", re.compile(r"risk\s+of\s+bias|\bRoB\s?2\b|ROBINS|Newcastle[-\s]Ottawa|QUADAS", re.I)),
    ("Dị biệt (heterogeneity)", re.compile(r"heterogeneity|\bI\s?[²2]\s?(?:=|<|>|statistic)", re.I)),
    ("GRADE", re.compile(r"\bGRADE\b")),
    ("Cỡ mẫu / lực mẫu", re.compile(r"sample\s+size|statistical\s+power|power\s+calculation", re.I)),
)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


class LoiDocPdf(Exception):
    """PDF không đọc được. `ly_do` ∈ {thieu_thu_vien, pdf_hong, pdf_it_chu} — để đếm và chọn cách báo."""

    def __init__(self, ly_do: str, thong_diep: str) -> None:
        super().__init__(thong_diep)
        self.ly_do = ly_do


def _chu(el: ET.Element) -> str:
    return re.sub(r"\s+", " ", " ".join(el.itertext())).strip()


def _cat(vb: str, gioi_han_tu: int, nhan: str) -> str:
    tu = vb.split()
    if len(tu) <= gioi_han_tu:
        return vb
    return (" ".join(tu[:gioi_han_tu])
            + f" […cắt tại {gioi_han_tu} từ / {len(tu)} từ — toàn văn trong XML {nhan}]")


def _goc_bai(root: ET.Element) -> ET.Element:
    # File có thể là <pmc-articleset><article>… hoặc <article> trần
    return root.find(".//article") if root.find(".//article") is not None else root


def _mot_bai(xml_path: Path) -> dict:
    art = _goc_bai(ET.fromstring(xml_path.read_bytes()))
    meta = {"tieu_de": "", "tap_chi": "", "nam": "", "doi": "", "dang_ky": [],
            "phuong_phap": [], "ket_qua": [], "han_che": [], "tai_tro": []}
    tt = art.find(".//article-title")
    if tt is not None:
        meta["tieu_de"] = _chu(tt)
    jt = art.find(".//journal-title")
    if jt is not None:
        meta["tap_chi"] = _chu(jt)
    for y in art.findall(".//pub-date/year"):
        meta["nam"] = meta["nam"] or (y.text or "")
    for aid in art.findall(".//article-id"):
        if aid.get("pub-id-type") == "doi":
            meta["doi"] = (aid.text or "").strip()
    toan_bo = _chu(art)
    meta["dang_ky"] = sorted(set(MA_DANG_KY.findall(toan_bo)))
    body = art.find(".//body")
    if body is not None:
        # Duyệt cây CÓ NHẬN CHỦ: sec khớp Phương pháp/Kết quả nhận trọn cây con
        # (kể cả tiểu mục — con số gộp thường nằm ở đó); không khớp thì đi tiếp
        # xuống con. Tránh vừa bỏ sót tiểu mục vừa lấy trùng hai tầng.
        def _walk(sec: ET.Element) -> None:
            td = sec.find("title")
            ten = _chu(td) if td is not None else ""
            loai = ("phuong_phap" if NHAN_MUC["phuong_phap"].search(ten)
                    else "ket_qua" if NHAN_MUC["ket_qua"].search(ten) else None)
            if loai:
                doan = [_chu(p) for p in sec.iter("p")]
                meta[loai] += [f"**{ten}.** " + d for d in doan if d]
                return
            if NHAN_MUC["ban_luan"].search(ten):
                meta["han_che"] += [d for d in (_chu(p) for p in sec.iter("p"))
                                    if re.search(r"limitation|hạn chế", d, re.I)]
                return
            for con in sec.findall("sec"):
                _walk(con)
        for sec in body.findall("sec"):
            _walk(sec)
    # Tài trợ + COI: funding-group, fn conflict, sec ở <back>
    for fs in art.findall(".//funding-statement"):
        meta["tai_tro"].append(_chu(fs))
    for fn in art.findall(".//fn"):
        if re.search(r"coi|conflict|competing", fn.get("fn-type", ""), re.I):
            meta["tai_tro"].append(_chu(fn))
    back = art.find(".//back")
    if back is not None:
        for sec in back.iter("sec"):
            td = sec.find("title")
            if td is not None and re.search(r"funding|conflict|competing|disclos",
                                            _chu(td), re.I):
                meta["tai_tro"].append(f"**{_chu(td)}.** " + " ".join(
                    _chu(p) for p in sec.findall("p")))
    return meta


def _cau_hieu_so(ket_qua: list[str], toi_da: int = 14) -> list[str]:
    ra = []
    for doan in ket_qua:
        for cau in re.split(r"(?<=[.!?])\s+", doan):
            # >420 ký tự gần như chắc là BẢNG bị ép phẳng thành «câu» — bỏ
            if 25 < len(cau) < 420 and CAU_HIEU_SO.search(cau):
                ra.append(cau.strip())
    # khử trùng lặp giữ thứ tự
    seen: set[str] = set()
    ra = [c for c in ra if not (c in seen or seen.add(c))]
    return ra[:toi_da]


def _tuong_doi(tep: Path) -> str:
    """Đường dẫn tương đối repo khi được — kho ở cây khác (--dash, test) thì in đường dẫn đầy đủ, không ném lỗi."""
    try:
        return str(tep.relative_to(REPO))
    except ValueError:
        return str(tep)


def _ghi_nguyen_tu(tep: Path, noi_dung: str) -> None:
    """Ghi qua tệp tạm + os.replace — OneDrive/tiến trình khác không bao giờ thấy bản đọc ghi dở."""
    tep.parent.mkdir(parents=True, exist_ok=True)
    tam = tep.with_name(tep.name + f".tam-{os.getpid()}")
    tam.write_text(noi_dung, encoding="utf-8", newline="\n")
    os.replace(tam, tep)


def viet_ban_doc(pm: str, xml_path: Path, ra_dir: Path | None = None) -> Path:
    m = _mot_bai(xml_path)
    pmc = re.search(r"_PMC(\d+)", xml_path.name)
    cau_so = _cau_hieu_so(m["ket_qua"])
    phan = [
        f"# Đọc sâu toàn văn — PMID {pm}",
        f"\n> Trích MÁY nguyên văn theo mục từ JATS XML (PMC{pmc.group(1) if pmc else '?'},"
        f" bản OA hợp pháp) — không tóm tắt thay, không diễn giải thay."
        f" Sinh {date.today().isoformat()}. **Cần bác sĩ kiểm chứng.**\n",
        f"**{m['tieu_de']}**  \n*{m['tap_chi']}* · {m['nam']}"
        + (f" · doi:{m['doi']}" if m["doi"] else ""),
    ]
    if m["dang_ky"]:
        phan.append("\n**Mã đăng ký tìm thấy trong bài:** " + " · ".join(m["dang_ky"]))
    if m["phuong_phap"]:
        phan.append("\n## Phương pháp (nguyên văn)\n")
        phan.append(_cat("\n\n".join(m["phuong_phap"]), 900, "phương pháp"))
    else:
        phan.append("\n## Phương pháp\n*(XML không có mục phương pháp tách riêng — "
                    "đọc trực tiếp file XML)*")
    if m["ket_qua"]:
        phan.append("\n## Kết quả (nguyên văn)\n")
        phan.append(_cat("\n\n".join(m["ket_qua"]), 1100, "kết quả"))
    if cau_so:
        phan.append("\n## Câu mang hiệu số — để đối chiếu con số trích trên thẻ\n")
        phan += [f"- {c}" for c in cau_so]
    if m["han_che"]:
        phan.append("\n## Hạn chế tác giả tự khai (nguyên văn)\n")
        phan.append(_cat("\n\n".join(m["han_che"]), 350, "bàn luận"))
    if m["tai_tro"]:
        phan.append("\n## Tài trợ & xung đột lợi ích (nguyên văn)\n")
        phan.append(_cat("\n\n".join(dict.fromkeys(m["tai_tro"])), 180, "tài trợ"))
    phan.append("\n---\n*Bản trích phục vụ thẩm định — quyết định lâm sàng qua Cổng A"
                " của bác sĩ. Không PII.*\n")
    ra = (ra_dir or KHO / "doc_sau") / f"PMID-{pm}.md"
    _ghi_nguyen_tu(ra, "\n".join(phan))
    return ra


# ── PDF kênh TDM: đọc → cắt mục → dữ kiện + trích ngắn ────────────────────────────────────────────────────────────
def _doc_pdf(pdf: Path) -> tuple[list[str], str]:
    """(văn bản từng trang, tiêu đề trong metadata). Thiếu thư viện / PDF hỏng ⇒ LoiDocPdf — một tệp hỏng không
    giết cả lượt."""
    try:
        from pypdf import PdfReader  # noqa: PLC0415 — thư viện tuỳ chọn: thiếu thì báo rõ, không gãy
    except ImportError as e:
        raise LoiDocPdf("thieu_thu_vien", "không đọc được PDF — thiếu thư viện pypdf (máy KHÔNG tự cài; "
                                          "~/.ebm-venv có sẵn theo requirements của repo y khoa) — phiên thẩm định "
                                          "đọc trực tiếp tệp") from e
    logging.getLogger("pypdf").setLevel(logging.ERROR)  # cảnh báo cấu trúc PDF không phải việc của bản đọc
    try:
        rd = PdfReader(str(pdf))
        if rd.is_encrypted:
            rd.decrypt("")  # chỉ mở được PDF khoá bằng mật khẩu RỖNG (quyền in/chép); mật khẩu thật ⇒ lỗi dưới
        trang = [(p.extract_text() or "") for p in rd.pages]
    except Exception as e:  # noqa: BLE001 — pypdf ném nhiều loại lỗi với tệp hỏng/không phải PDF
        raise LoiDocPdf("pdf_hong", f"PDF hỏng/không đọc được ({type(e).__name__})") from e
    try:  # metadata hỏng không được biến một PDF đọc được chữ thành «hỏng»
        tieu_de = str((rd.metadata or {}).get("/Title") or "")
    except Exception:  # noqa: BLE001
        tieu_de = ""
    return trang, tieu_de


def _nhan_tieu_de(dong: str) -> str | None:
    s = dong.strip()
    if not s or len(s) > 70:
        return None
    for loai, rx in _TIEU_DE_PDF.items():
        if rx.match(s):
            return loai
    return None


def _noi_dong(dong: list[str]) -> str:
    vb = "\n".join(dong)
    vb = re.sub(r"([a-z])[-‐­]\n([a-z])", r"\1\2", vb)  # gạch nối cuối dòng của bản in
    return re.sub(r"\s+", " ", vb).strip()


def _khoi_pdf(trang: list[str]) -> list[tuple[str, int, str, str]]:
    """Cắt văn bản PDF thành đoạn (mục, số trang, văn bản đã nối dòng, dòng tiêu đề mục). Mục đổi khi gặp một DÒNG tiêu
    đề chuẩn; trước tiêu đề đầu tiên là «dau_bai» (tiêu đề bài, tác giả, tóm tắt). Không nhận ra tiêu đề nào ⇒ cả bài là
    «dau_bai». Mục ngắn (TRAN_KY_TU_MUC_NGAN) quá trần ký tự ⇒ trả về mục trước nó."""
    ra: list[tuple[str, int, str, str]] = []
    muc, tieu_de, muc_truoc, da_tich = "dau_bai", "", "dau_bai", 0
    for so, vb in enumerate(trang, 1):
        dong_doan: list[str] = []
        for dong in vb.splitlines():
            loai = _nhan_tieu_de(dong)
            if loai:
                if dong_doan:
                    ra.append((muc, so, _noi_dong(dong_doan), tieu_de))
                if loai in TRAN_KY_TU_MUC_NGAN and muc not in TRAN_KY_TU_MUC_NGAN:
                    muc_truoc = muc
                dong_doan, muc, tieu_de, da_tich = [], loai, " ".join(dong.split()), 0
                continue
            # Xét TRƯỚC khi nhận dòng: một dòng dài (pypdf có khi trả cả đoạn trên một dòng) không được lọt vào mục ngắn.
            tran = TRAN_KY_TU_MUC_NGAN.get(muc)
            if tran is not None and da_tich + len(dong) > tran:
                if dong_doan:
                    ra.append((muc, so, _noi_dong(dong_doan), tieu_de))
                dong_doan, muc, tieu_de, da_tich = [], muc_truoc, "", 0
            dong_doan.append(dong)
            da_tich += len(dong)
        if dong_doan:
            ra.append((muc, so, _noi_dong(dong_doan), tieu_de))
    return ra


def _lam_sach_trich(s: str) -> str:
    return _EMAIL.sub("[email]", s).replace("«", '"').replace("»", '"')


def _trich_ngan(cau: str, vi_tri: int = 0, toi_da: int = TRAN_TU_TRICH) -> str:
    """Cửa sổ ≤ `toi_da` từ quanh ký tự `vi_tri` của câu — bài có bản quyền: không chép cả câu dài. «…» đánh dấu
    chỗ cắt."""
    tu = list(re.finditer(r"\S+", cau))
    if len(tu) <= toi_da:
        return _lam_sach_trich(" ".join(m.group() for m in tu))
    i = next((k for k, m in enumerate(tu) if m.end() > vi_tri), len(tu) - 1)
    dau = max(0, min(i - 5, len(tu) - toi_da))
    cuoi = dau + toi_da
    s = " ".join(m.group() for m in tu[dau:cuoi])
    return _lam_sach_trich(("…" if dau else "") + s + ("…" if cuoi < len(tu) else ""))


def _cau_pdf(khoi, muc_uu_tien: tuple[str, ...], bo_muc: tuple[str, ...] = ("tai_lieu",),
             chi_muc: tuple[str, ...] | None = None):
    """Duyệt (mục, trang, câu, tiêu đề mục): mục ưu tiên trước theo thứ tự, rồi các mục còn lại theo thứ tự trong bài;
    bỏ mục trong `bo_muc`; `chi_muc` (nếu có) ⇒ chỉ các mục đó."""
    thu_tu = {m: k for k, m in enumerate(muc_uu_tien)}
    chon = [k for k in khoi if k[0] not in bo_muc and (chi_muc is None or k[0] in chi_muc)]
    for muc, so, vb, td in sorted(chon, key=lambda k: thu_tu.get(k[0], len(muc_uu_tien))):
        for cau in re.split(r"(?<=[.!?])\s+", vb):
            if cau.strip():
                yield muc, so, cau.strip(), td


def _trich_theo(khoi, rx, toi_da: int, muc_uu_tien: tuple[str, ...], *, muc_tron: str | None = None,
                bo_muc: tuple[str, ...] = ("tai_lieu",), chi_muc: tuple[str, ...] | None = None):
    """≤ `toi_da` trích ngắn (trang, trích, tiêu đề mục). Lượt 1: câu khớp `rx`. Lượt 2 (còn chỗ): câu đầu của mục
    `muc_tron` (Hạn chế/Tài trợ — câu không mang từ khoá vẫn là nội dung của mục; nhận cả câu ngắn như «None.»)."""
    ra: list[tuple[int, str, str]] = []
    da: set[str] = set()

    def _them(so: int, cau: str, vi_tri: int, td: str) -> None:
        t = _trich_ngan(cau, vi_tri)
        if t not in da:
            da.add(t)
            ra.append((so, t, td))

    for _muc, so, cau, td in _cau_pdf(khoi, muc_uu_tien, bo_muc, chi_muc):
        if len(ra) >= toi_da:
            return ra
        m = rx.search(cau) if 25 < len(cau) < 420 and not _NHIEU.search(cau) else None
        if m:
            _them(so, cau, m.start(), td)
    for _muc, so, cau, td in (_cau_pdf(khoi, (muc_tron,), bo_muc, (muc_tron,)) if muc_tron else ()):
        if len(ra) >= toi_da:
            break
        if 4 <= len(cau) < 420 and not _NHIEU.search(cau):
            _them(so, cau, 0, td)
    return ra


def _dong_trich(ds: list[tuple[int, str, str]], kem_tieu_de: bool = False) -> list[str]:
    return [f"- tr. {so}" + (f" [{td}]" if kem_tieu_de and td else "") + f" — «{t}»" for so, t, td in ds]


def ban_doc_tdm_md(pm: str, trang: list[str], tieu_de: str, ten_tep: str, nhan_nguon: str = NHAN_NGUON_TDM,
                   cau_nguon: str = CAU_NGUON_TDM) -> str:
    """Bản đọc của PDF kênh TDM (thuần — không đọc đĩa, không ghi). Chỉ dữ kiện + trang + trích ≤ TRAN_TU_TRICH từ."""
    khoi = _khoi_pdf(trang)
    so_tu = sum(len(t.split()) for t in trang)
    td = html.unescape(tieu_de or "").strip()
    if not td or td.startswith("/") or re.search(r"\.(?:dvi|docx?|tex)\b|microsoft word", td, re.I):
        td = "(tiêu đề: xem trang 1 của PDF)"
    m_doi = re.search(r"10\.\d{4,9}/[^\s\"<>]+", "\n".join(trang[:2]))
    doi = m_doi.group().rstrip(".,;)]") if m_doi else ""
    ban_do = []
    for loai, ten in _TEN_MUC_PDF.items():
        trg = sorted({k[1] for k in khoi if k[0] == loai})
        ban_do.append(f"{ten} tr. {trg[0]}" if trg else f"{ten} —")
    noi_dung = " ".join(k[2] for k in khoi if k[0] != "tai_lieu")
    dang_ky = sorted(set(MA_DANG_KY.findall(noi_dung)))
    d = [f"# Đọc sâu toàn văn — PMID {pm}",
         f"\n> Trích MÁY từ PDF qua **{nhan_nguon}** (tệp `{ten_tep}`, ngoài git; {cau_nguon}). Bản đọc chỉ ghi DỮ KIỆN + VỊ TRÍ TRANG + trích ≤ {TRAN_TU_TRICH} từ/lần — "
         f"KHÔNG chép đoạn văn (khác bản OA JATS); đủ ngữ cảnh thì đọc chính tệp PDF ở trang ghi kèm. "
         f"{len(trang)} trang · {so_tu} từ trích được. Sinh {date.today().isoformat()}. **Cần bác sĩ kiểm chứng.**\n",
         f"**{td}**" + (f"  \ndoi:{doi}" if doi else ""),
         "\n**Bản đồ mục (trang đầu tiên máy nhận ra tiêu đề):** " + " · ".join(ban_do)]
    if all(x.endswith("—") for x in ban_do):
        d.append("*(máy không nhận ra tiêu đề mục nào — đọc thẳng PDF; trích dưới đây lấy trên toàn văn bản)*")
    if dang_ky:
        d.append("\n**Mã đăng ký tìm thấy trong bài:** " + " · ".join(dang_ky))
    # Hiệu số của CHÍNH bài: mục Kết quả + Tóm tắt (+ phần đầu bài); bài không nhận ra mục Kết quả (guideline,
    # Cochrane…) thì lấy trên toàn văn trừ tài liệu tham khảo và tài trợ.
    co_ket_qua = any(k[0] == "ket_qua" for k in khoi)
    hs = _trich_theo(khoi, CAU_HIEU_SO_PDF, TRAN_TRICH_PDF["hieu_so"], ("ket_qua", "tom_tat", "dau_bai"),
                     bo_muc=("tai_lieu", "tai_tro"), chi_muc=("ket_qua", "tom_tat", "dau_bai") if co_ket_qua else None)
    if hs:
        d.append(f"\n## Hiệu số — trích ≤ {TRAN_TU_TRICH} từ quanh con số (câu đủ ở trang ghi kèm)\n")
        d += _dong_trich(hs)
    kc = _trich_theo(khoi, _KHUYEN_CAO, TRAN_TRICH_PDF["khuyen_cao"], ("tom_tat", "dau_bai", "ket_qua"))
    if kc:
        d.append(f"\n## Mức/lớp khuyến cáo bắt gặp — trích ≤ {TRAN_TU_TRICH} từ (mức NGUYÊN BẢN đọc ở PDF)\n")
        d += _dong_trich(kc)
    d.append("\n## Dấu hiệu phương pháp — máy dò cụm từ (vắng ≠ bài không báo cáo)\n")
    vang = []
    for ten, rx in DAU_HIEU_PP:
        thay = [(so, cau, m) for _, so, cau, _ in _cau_pdf(khoi, ("phuong_phap", "ket_qua"))
                for m in [rx.search(cau)] if m]
        if not thay:
            vang.append(ten)
            continue
        so, cau, m = thay[0]
        d.append(f"- {ten}: tr. {so} (×{len(thay)} câu) — «{_trich_ngan(cau, m.start())}»")
    if vang:
        d.append("- Không bắt gặp: " + " · ".join(vang))
    hc = _trich_theo(khoi, _HAN_CHE, TRAN_TRICH_PDF["han_che"], ("han_che", "ban_luan"), muc_tron="han_che")
    if hc:
        d.append(f"\n## Hạn chế tác giả tự khai — trích ≤ {TRAN_TU_TRICH} từ\n")
        d += _dong_trich(hc, kem_tieu_de=True)
    tt = _trich_theo(khoi, _TAI_TRO, TRAN_TRICH_PDF["tai_tro"], ("tai_tro", "dau_bai", "tom_tat"), muc_tron="tai_tro")
    if tt:
        d.append(f"\n## Tài trợ & xung đột lợi ích — trích ≤ {TRAN_TU_TRICH} từ\n")
        d += _dong_trich(tt, kem_tieu_de=True)
    d.append("\n---\n*Bản trích phục vụ thẩm định — quyết định lâm sàng qua Cổng A của bác sĩ. Toàn văn KHÔNG tự "
             "nâng đề xuất. Không PII.*\n")
    return "\n".join(d)


def viet_ban_doc_tdm(pm: str, pdf: Path, ra_dir: Path | None = None, nhan_nguon: str = NHAN_NGUON_TDM,
                     cau_nguon: str = CAU_NGUON_TDM) -> Path:
    """PDF kênh TDM → doc_sau/PMID-<n>.md. Văn bản quá ít (ảnh quét/trang bìa) ⇒ LoiDocPdf, KHÔNG sinh bản đọc giả."""
    trang, tieu_de = _doc_pdf(pdf)
    n = len(re.sub(r"\s+", " ", " ".join(trang)).strip())
    if n < TOI_THIEU_KY_TU_PDF:
        raise LoiDocPdf("pdf_it_chu", f"PDF chỉ có {n} ký tự chữ (< {TOI_THIEU_KY_TU_PDF}) — ảnh quét/trang bìa? "
                                      "đọc trực tiếp tệp, không sinh bản đọc")
    ra = (ra_dir or KHO / "doc_sau") / f"PMID-{pm}.md"
    _ghi_nguyen_tu(ra, ban_doc_tdm_md(pm, trang, tieu_de, pdf.name, nhan_nguon, cau_nguon))
    return ra


# ── một PMID ───────────────────────────────────────────────────────────────────────────────────────────────────────
# «tdm_thieu_thu_vien»: có PDF kênh TDM nhưng máy thiếu pypdf ⇒ phiên thẩm định đọc thẳng tệp (đếm chung nhóm ◐, luôn in
# cảnh báo) — KHÔNG phải «chỉ tóm tắt».
NHOM = ("trinh_duyet", "da_co", "vua_sinh_xml", "vua_sinh_tdm", "doc_truc_tiep", "tdm_thieu_thu_vien", "chua_co_tep",
        "loi")


def _do_day_du(hs_td: Path) -> str:
    try:
        return json.loads(hs_td.read_text(encoding="utf-8")).get("kiem", {}).get("do_day_du", "?")
    except (OSError, ValueError, AttributeError):
        return "?"


def _bac_si_da_doc(kho: Path) -> set[str]:
    """PMID trong sổ «bác sĩ đã đọc trực tiếp» (NXB cấm AI — máy không có toàn văn); dòng hỏng bỏ qua."""
    tep = kho / "trinh_duyet" / "bac-si-da-doc.jsonl"
    ra: set[str] = set()
    if tep.exists():
        for dong in tep.read_text(encoding="utf-8").splitlines():
            try:
                ra.add(str(json.loads(dong)["pmid"]))
            except (ValueError, KeyError, TypeError):
                continue
    return ra


def xu_ly_pmid(pm: str, kho: Path, *, lam_lai: bool) -> tuple[str, str]:
    """Một PMID → (nhóm ∈ NHOM, ghi chú). `lam_lai`: sinh lại bản đọc MÁY (JATS/TDM) đã có.

    Bản đọc của làn trình duyệt có bác sĩ (có `trinh_duyet/PMID-<n>.json`) xét TRƯỚC mọi tệp và KHÔNG BAO GIỜ bị
    ghi đè."""
    ra_dir = kho / "doc_sau"
    md = ra_dir / f"PMID-{pm}.md"
    hs_td = kho / "trinh_duyet" / f"PMID-{pm}.json"
    if hs_td.exists():
        if not md.exists():
            return "loi", (f"hồ sơ trình duyệt có nhưng THIẾU bản đọc doc_sau/{md.name} — nạp lại bằng "
                           "doc_toan_van_co_nguoi.py --nap <hồ sơ> --ghi (máy không tự sinh thay)")
        return "trinh_duyet", (f"toàn văn đọc qua trình duyệt có bác sĩ — trích xuất có cấu trúc, độ đầy đủ "
                               f"{_do_day_du(hs_td)} (doc_sau/{md.name})")
    if md.exists() and not lam_lai:
        return "da_co", f"đã có bản đọc doc_sau/{md.name}"
    xml = sorted(kho.glob(f"PMID-{pm}_*.xml"))
    pdf = sorted(kho.glob(f"PMID-{pm}_WTDM.pdf"))
    pdf_chr = [] if pdf else sorted(kho.glob(f"PMID-{pm}_CHR.pdf"))
    loi_xml = ""
    if xml:
        try:
            return "vua_sinh_xml", f"→ {_tuong_doi(viet_ban_doc(pm, xml[0], ra_dir))} (JATS, bản OA)"
        except ET.ParseError:
            loi_xml = (f"XML hỏng ({xml[0].name}) — gom bỏ qua PMID đã có XML nên tệp hỏng chặn cả làn OA lẫn làn "
                       "trình duyệt; kiểm tệp")
    if pdf or pdf_chr:
        tep, nhan, cau = (pdf[0], NHAN_NGUON_TDM, CAU_NGUON_TDM) if pdf else (pdf_chr[0], NHAN_NGUON_CHR, CAU_NGUON_CHR)
        try:
            return "vua_sinh_tdm", f"→ {_tuong_doi(viet_ban_doc_tdm(pm, tep, ra_dir, nhan, cau))} (PDF {nhan})"
        except LoiDocPdf as e:
            if e.ly_do == "thieu_thu_vien":
                return "tdm_thieu_thu_vien", f"PDF {'kênh TDM' if pdf else 'phiên Chrome'} ({tep.name}) — {e}"
            return "loi", f"{tep.name}: {e}"
    if loi_xml:
        return "loi", loi_xml
    if md.exists():
        return "da_co", f"đã có bản đọc doc_sau/{md.name} (kho không còn tệp nguồn để sinh lại)"
    khac = sorted(kho.glob(f"PMID-{pm}_UPW.*")) or sorted(kho.glob(f"PMID-{pm}_CHR.html"))
    if khac:
        # kho có bản HTML/PDF tầng-2 (Unpaywall) → toàn văn CÓ, chỉ là không qua bộ bóc — phiên thẩm định đọc trực tiếp
        return "doc_truc_tiep", (f"toàn văn dạng {khac[0].suffix[1:].upper()} ({khac[0].name}) — đọc trực tiếp, "
                                 "không qua bóc JATS")
    return "chua_co_tep", "chỉ tóm tắt"


# ── dashboard ──────────────────────────────────────────────────────────────────────────────────────────────────────
def _nap_verify_dashboard():
    sp = importlib.util.spec_from_file_location("_vd_doc_sau", VERIFY_DASHBOARD)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def tep_dashboard(dash: Path, chi_dinh: list[str] | None) -> tuple[list[Path], list[str]]:
    """(tệp dashboard cần đọc, tệp chỉ định không thấy). Mặc định mọi WebDashboard_*.html; luôn bỏ bản sao lưu
    «.bak»."""
    if chi_dinh:
        tep, vang = [], []
        for mau in chi_dinh:
            khop = [Path(p) for p in glob.glob(mau)]
            tep += khop
            if not khop:
                vang.append(mau)
    else:
        tep, vang = list(dash.glob("WebDashboard_*.html")), []
    return sorted({t for t in tep if t.is_file() and ".bak" not in t.name.lower()}), vang


def pmid_tu_dashboard(tep: Path, vd, chi_apply: bool) -> list[str] | None:
    """PMID CHÍNH của từng mục (trường `pmid` qua verify_dashboard.field — PMID trong references KHÔNG tính);
    `chi_apply` ⇒ chỉ mục decision='apply'. None = dashboard không có khối DATA."""
    blk = vd.extract_data_block(tep.read_text(encoding="utf-8", errors="replace"))
    if not blk:
        return None
    ra = []
    for ch in vd.split_items(blk):
        pm = (vd.field(ch, "pmid") or "").strip()
        if not re.fullmatch(r"\d{6,9}", pm):
            continue
        if chi_apply and (vd.field(ch, "decision") or "").strip() != "apply":
            continue
        ra.append(pm)
    return ra


def _ds(pmids: list[str], toi_da: int = 40) -> str:
    return " ".join(pmids[:toi_da]) + (f" … (+{len(pmids) - toi_da})" if len(pmids) > toi_da else "")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đọc sâu toàn văn cho thẩm định lâm sàng (OA JATS · PDF kênh TDM)")
    ap.add_argument("--queue", nargs="*", help="file queue/tuan-*.md — lấy PMID trong thẻ")
    ap.add_argument("--pmid", nargs="*", help="PMID chỉ định")
    ap.add_argument("--dashboard", nargs="*", default=None, metavar="TỆP",
                    help="lấy PMID từ dashboard (không kèm tệp = mọi WebDashboard_*.html của --dash, bỏ .bak)")
    ap.add_argument("--chi-apply", action="store_true", help="chỉ PMID của mục decision='apply' (bật luôn --dashboard)")
    ap.add_argument("--lam-lai", action="store_true",
                    help="--dashboard: sinh lại bản đọc MÁY đã có (bản đọc trình duyệt có bác sĩ KHÔNG BAO GIỜ "
                         "bị đụng)")
    ap.add_argument("--dash", type=Path, default=None,
                    help="thư mục EBM-Dashboards (mặc định: cạnh repo) — dùng khi chạy từ worktree")
    a = ap.parse_args(argv)
    dash = a.dash if a.dash else DASH
    kho = (a.dash / "toan_van_oa") if a.dash else KHO
    che_do_dash = a.dashboard is not None or a.chi_apply
    pmids: set[str] = set()
    for p in (a.pmid or []):
        if re.fullmatch(r"\d{6,9}", p):
            pmids.add(p)
        else:
            print(f"  ⚠ bỏ qua «{p}» — PMID phải là 6–9 chữ số")
    for m in (a.queue or []):
        for q in glob.glob(m):
            pmids |= set(re.findall(r"PMID[ :]?(\d{6,9})",
                                    Path(q).read_text(encoding="utf-8", errors="replace")))
    if che_do_dash:
        tep, vang = tep_dashboard(dash, a.dashboard)
        for v in vang:
            print(f"  ⚠ không thấy dashboard «{v}»")
        if not tep:
            print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy dashboard nào ở {dash} (chạy từ worktree? thêm --dash "
                  "<EBM-Dashboards>)")
            return 2
        vd = _nap_verify_dashboard()
        pm_dash: set[str] = set()
        for t in tep:
            ds_pm = pmid_tu_dashboard(t, vd, a.chi_apply)
            if ds_pm is None:
                print(f"  ⚠ {t.name}: không có khối DATA — bỏ qua")
                continue
            pm_dash |= set(ds_pm)
        print(f"Dashboard: {len(tep)} tệp · {len(pm_dash)} PMID duy nhất"
              + (" — chỉ mục decision='apply'" if a.chi_apply else ""))
        pmids |= pm_dash
    if not pmids:
        print("✗ Không có PMID đầu vào (--queue, --pmid hoặc --dashboard).")
        return 1
    if not kho.is_dir():
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy kho toàn văn {kho} (chạy từ worktree? thêm --dash <EBM-Dashboards>) — "
              "KHÔNG kết luận «chỉ tóm tắt»")
        return 2
    # gói tuần/--pmid giữ hành vi cũ: luôn sinh lại bản đọc máy; --dashboard giữ bản đã có trừ khi --lam-lai
    lam_lai = a.lam_lai or not che_do_dash
    bsd = _bac_si_da_doc(kho)
    nhom: dict[str, list[str]] = {k: [] for k in NHOM}
    pdf_chr: list[str] = []      # PDF phiên Chrome nằm trong nhóm vua_sinh_tdm (cùng bộ bóc) — đếm RIÊNG để nhãn tổng kết đúng nguồn
    ky_hieu = {"trinh_duyet": "◑", "da_co": "=", "vua_sinh_xml": "✓", "vua_sinh_tdm": "✓", "doc_truc_tiep": "◐",
               "tdm_thieu_thu_vien": "◐", "chua_co_tep": "○", "loi": "⚠"}
    luon_in = ("vua_sinh_xml", "vua_sinh_tdm", "tdm_thieu_thu_vien", "loi")
    for pm in sorted(pmids):
        loai, ghi_chu = xu_ly_pmid(pm, kho, lam_lai=lam_lai)
        nhom[loai].append(pm)
        if loai == "vua_sinh_tdm" and NHAN_NGUON_CHR in ghi_chu:
            pdf_chr.append(pm)
        if loai == "chua_co_tep":
            continue  # liệt kê gộp ở cuối
        if che_do_dash and loai not in luon_in:
            continue  # chế độ dashboard: chỉ in dòng có thay đổi/lỗi — còn lại trong số đếm
        noi = "" if ghi_chu.startswith("→") else ":"
        print(f"  {ky_hieu[loai]} {pm}{noi} {ghi_chu}")
    n = len(pmids)
    da_co = len(nhom["trinh_duyet"]) + len(nhom["da_co"])
    vua = len(nhom["vua_sinh_xml"]) + len(nhom["vua_sinh_tdm"])
    truc_tiep = len(nhom["doc_truc_tiep"]) + len(nhom["tdm_thieu_thu_vien"])
    co_bsd = [p for p in nhom["chua_co_tep"] if p in bsd]
    print(f"\nĐọc sâu — đơn vị PMID ({n} PMID duy nhất):")
    print(f"  ✓ đã có bản đọc: {da_co} — {len(nhom['trinh_duyet'])} bài đọc qua trình duyệt có bác sĩ (giữ nguyên) · "
          f"{len(nhom['da_co'])} bản đọc máy")
    n_tdm = len(nhom["vua_sinh_tdm"]) - len(pdf_chr)
    print(f"  ✚ vừa sinh: {vua} — {len(nhom['vua_sinh_xml'])} bài JATS · {n_tdm} bài PDF kênh TDM của NXB · {len(pdf_chr)} bài "
          "PDF phiên uỷ quyền Chrome (hai loại PDF đều có bản quyền, không phải OA)")
    print(f"  ◐ có toàn văn nhưng đọc trực tiếp (HTML/PDF tầng 2 hoặc thiếu thư viện PDF), chưa bóc: {truc_tiep}")
    if nhom["tdm_thieu_thu_vien"]:
        print(f"    ⚠ {len(nhom['tdm_thieu_thu_vien'])} PDF kênh TDM: không đọc được PDF — thiếu thư viện pypdf "
              "(máy không tự cài; chạy bằng ~/.ebm-venv/bin/python)")
    print(f"  ○ bỏ qua vì chưa có tệp toàn văn: {len(nhom['chua_co_tep'])} bài CHỈ TÓM TẮT (ghi rõ trên thẻ, "
          "không đoán)"
          + (f" — trong đó {len(co_bsd)} bác sĩ đã đọc trực tiếp" if co_bsd else ""))
    print(f"  ⚠ lỗi: {len(nhom['loi'])}")
    print(f"  Cộng: {da_co} + {vua} + {truc_tiep} + {len(nhom['chua_co_tep'])} + "
          f"{len(nhom['loi'])} = {n}")
    if nhom["chua_co_tep"]:
        print("  Chỉ tóm tắt: " + _ds(nhom["chua_co_tep"]))
    thieu = [p for p in nhom["chua_co_tep"] if p not in bsd]
    if thieu:
        lo = thieu[:40]
        print("  → bài không có OA: Claude mở trình duyệt, bác sĩ vượt chặn/đăng nhập — "
              "python3 tools/doc_toan_van_co_nguoi.py --pmid " + " ".join(lo)
              + (f"   (lô đầu 40/{len(thieu)} — chạy tiếp theo lô)" if len(thieu) > 40 else ""))
    print("Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
