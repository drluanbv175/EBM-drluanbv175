#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỌC SÂU TOÀN VĂN OA — bóc chi tiết có cấu trúc cho thẩm định lâm sàng (18/08/2026).

VÌ SAO CÓ
=========
Đo 18/08: kho toàn văn phủ 170/579 PMID của dashboard CŨ, nhưng 0/12 PMID của gói
tuần W34 — dây chuyền TUẦN (nơi chứng cứ MỚI đến tay bác sĩ) thẩm định 100% từ
TÓM TẮT, kể cả khi bài là OA nằm sẵn trên PMC. Tóm tắt không có: cách chọn ngẫu
nhiên, làm mù, ITT, tỷ lệ biến cố từng nhánh, phân nhóm, hạn chế tự khai, tài trợ.
Thiếu các mục đó thì mọi thẻ chỉ đáng «Cân nhắc» — và đúng là appraisalCompleteness
partial đã chặn trần như vậy (ghi nhớ 18/08: «tường phí chặn mức apply»).

Tool này đọc XML JATS trong kho `EBM-Dashboards/toan_van_oa/` (đã gom bằng
`gom_toan_van_dashboard.py --queue ...`) và xuất MỖI PMID một bản đọc-sâu markdown:

  · Nhận diện (tạp chí · năm · DOI · PMCID) + mã ĐĂNG KÝ (NCT/ChiCTR/PROSPERO…)
  · PHƯƠNG PHÁP nguyên văn (thiết kế, quần thể, mù, kết cục)
  · KẾT QUẢ nguyên văn + danh sách CÂU MANG HIỆU SỐ (RR/HR/OR/CI/%… để đối chiếu)
  · HẠN CHẾ tác giả tự khai · TÀI TRỢ & XUNG ĐỘT LỢI ÍCH

TRUNG THỰC PHẠM VI — ba luật cứng:
  1. CHỈ TRÍCH NGUYÊN VĂN theo mục, kèm nguồn mục — không tóm tắt thay, không
     diễn giải thay, không chấm điểm. Việc THẨM ĐỊNH là của người đọc (bác sĩ,
     hoặc phiên Claude gói tuần đọc bản này rồi tự chịu trách nhiệm câu chữ).
  2. PMID chưa có toàn văn trong kho → nói rõ «chỉ tóm tắt», KHÔNG đoán.
  3. Mục dài bị CẮT có ghi chú rõ tại chỗ cắt — không cắt im lặng.

Dùng:  python3 tools/doc_sau_toan_van.py --queue queue/tuan-2026-W34.md
       python3 tools/doc_sau_toan_van.py --pmid 42587114 42605418
Ra:    EBM-Dashboards/toan_van_oa/doc_sau/PMID-<n>.md   (khoá theo PMID, dùng lại
       được giữa các tuần — không theo tuần)
Mã thoát: 0 = chạy trọn · 1 = không có PMID đầu vào. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import glob
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
KHO = REPO / "EBM-Dashboards" / "toan_van_oa"
RA = KHO / "doc_sau"

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


def viet_ban_doc(pm: str, xml_path: Path) -> Path:
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
    RA.mkdir(parents=True, exist_ok=True)
    ra = RA / f"PMID-{pm}.md"
    ra.write_text("\n".join(phan), encoding="utf-8", newline="\n")
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Đọc sâu toàn văn OA cho thẩm định lâm sàng")
    ap.add_argument("--queue", nargs="*", help="file queue/tuan-*.md — lấy PMID trong thẻ")
    ap.add_argument("--pmid", nargs="*", help="PMID chỉ định")
    a = ap.parse_args()
    pmids: set[str] = set(a.pmid or [])
    for m in (a.queue or []):
        for q in glob.glob(m):
            pmids |= set(re.findall(r"PMID[ :]?(\d{6,9})",
                                    Path(q).read_text(encoding="utf-8", errors="replace")))
    if not pmids:
        print("✗ Không có PMID đầu vào (--queue hoặc --pmid).")
        return 1
    co, thieu, dang_khac = [], [], []
    for pm in sorted(pmids):
        khop = list(KHO.glob(f"PMID-{pm}_*.xml"))
        if not khop:
            # kho có bản HTML/PDF tầng-2 (Unpaywall) → toàn văn CÓ, chỉ là không
            # qua bộ bóc JATS — phiên thẩm định đọc trực tiếp file đó
            khac = sorted(KHO.glob(f"PMID-{pm}_UPW.*"))
            if khac:
                dang_khac.append(pm)
                print(f"  ◐ {pm}: toàn văn dạng {khac[0].suffix[1:].upper()} "
                      f"({khac[0].name}) — đọc trực tiếp, không qua bóc JATS")
            else:
                thieu.append(pm)
            continue
        try:
            ra = viet_ban_doc(pm, khop[0])
            co.append(pm)
            print(f"  ✓ {pm} → {ra.relative_to(REPO)}")
        except ET.ParseError:
            thieu.append(pm)
            print(f"  ⚠ {pm}: XML hỏng — bỏ qua, coi như chưa có toàn văn")
    print(f"\nĐọc sâu: {len(co)} bài JATS · {len(dang_khac)} bài toàn văn HTML/PDF "
          f"(đọc trực tiếp) · {len(thieu)} bài CHỈ TÓM TẮT (ghi rõ trên thẻ, không đoán)")
    if thieu:
        print("  Chỉ tóm tắt: " + " ".join(thieu))
    print("Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
