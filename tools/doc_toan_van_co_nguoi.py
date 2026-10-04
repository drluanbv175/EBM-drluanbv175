#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỌC TOÀN VĂN BÀI KHÔNG MỞ QUA TRÌNH DUYỆT CÓ BÁC SĨ — phiếu + quy trình + nạp hồ sơ trích xuất (02/10/2026, bác sĩ yêu cầu).

VÌ SAO CÓ. Dây chuyền toàn văn hiện có (`gom_toan_van_dashboard.py` → `doc_sau_toan_van.py`) chỉ lấy được bản OA hợp pháp: gói tuần
W40 có 5/7 thẻ «CHỈ TÓM TẮT» ⇒ tối đa «Cân nhắc» (appraisalCompleteness=partial). Đo 02/10/2026 bằng yêu cầu TRUNG THỰC (không giả
trình duyệt): diabetesjournals.org (ADA), academic.oup.com (ESC/EHJ), nejm.org, thelancet.com, jamanetwork.com, ahajournals.org,
onlinelibrary.wiley.com, bmj.com trả 403 «Just a moment…» (Cloudflare); sciencedirect.com 403; link.springer.com, kdigo.org 406;
www.fda.gov 401 — máy KHÔNG đọc được, kể cả bài miễn phí. Đường đúng là làn CÓ NGƯỜI: Claude mở trang trong khung trình duyệt của
app, BÁC SĨ tự vượt kiểm tra chống bot / tự đăng nhập (Claude KHÔNG bấm, KHÔNG giải CAPTCHA, KHÔNG gõ mật khẩu), Claude đọc toàn
văn rồi ghi một HỒ SƠ TRÍCH XUẤT CÓ CẤU TRÚC — không chép nguyên văn (bản quyền nhà xuất bản).

    python3 tools/doc_toan_van_co_nguoi.py --queue queue/tuan-2026-W40.md   # phiếu: thẻ nào chưa có toàn văn, mở ở đâu (có mạng)
    python3 tools/doc_toan_van_co_nguoi.py --pmid 42377292 --ngoai-tuyen     # chỉ soi kho cục bộ, không gọi mạng
    python3 tools/doc_toan_van_co_nguoi.py --huong-dan                       # quy trình từng bước cho phiên Claude + bác sĩ
    python3 tools/doc_toan_van_co_nguoi.py --mau                             # khuôn JSON hồ sơ trích xuất
    python3 tools/doc_toan_van_co_nguoi.py --nap ho-so.json [--ghi]          # kiểm (mặc định chạy thử) rồi ghi vào kho
    python3 tools/doc_toan_van_co_nguoi.py --khong-truy-cap 42377292 --ly-do "tạp chí đòi mua bài"   # bác sĩ không có quyền đọc
    python3 tools/doc_toan_van_co_nguoi.py --bac-si-da-doc 42377292 --ghi-chu "<kết luận của bác sĩ>" [--ghi]   # NXB cấm AI: bác sĩ đã tự đọc
    python3 tools/doc_toan_van_co_nguoi.py --ghi-uy-quyen Elsevier --can-cu "<nguyên văn lời bác sĩ>" [--ghi]   # bác sĩ uỷ quyền máy đọc

Ghi vào (ngoài git, cùng kho dây chuyền OA): `EBM-Dashboards/toan_van_oa/trinh_duyet/PMID-<n>.json` + bản đọc
`EBM-Dashboards/toan_van_oa/doc_sau/PMID-<n>.md` (gói tuần bước 4b đọc đúng thư mục này). Mã thoát: phiếu 0 hết việc · 1 còn bài
chờ · 2 KHÔNG ĐO ĐƯỢC; nạp 0 đạt (đã ghi / chạy thử) · 2 không xác minh được (engine vắng) · 3 từ chối. Mọi hồ sơ là CANDIDATE —
toàn văn KHÔNG tự nâng đề xuất; nâng/hạ là thẩm quyền bác sĩ. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import time
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote, urlparse

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
DASH = REPO / "EBM-Dashboards"
KHO = DASH / "toan_van_oa"
PHIEU_DIR = REPO / "state" / "doc-toan-van"
HAN_KHONG_TRUY_CAP_NGAY = 90      # bác sĩ báo «không có quyền đọc» ⇒ không nhắc lại trong 90 ngày
HAN_DOC_LUC_NGAY = 14             # hồ sơ phải nạp trong 14 ngày kể từ lúc đọc trang
TOI_THIEU_KY_TU = 3000            # văn bản trang ngắn hơn ⇒ gần như chắc chỉ là trang đích/tóm tắt, chưa phải toàn văn
TRAN_CHUOI = 800                  # trường văn bản dài hơn ⇒ nghi chép nguyên văn
TRAN_TOM_TAT_KC = 400
TRAN_TU_TRICH = 15                # trích nguyên văn ngắn: ≤ 15 từ/lần
TRAN_SO_TRICH = 6
# Ghi chú «bác sĩ đã đọc trực tiếp» (03/10/2026): KẾT LUẬN bằng lời bác sĩ, không phải nội dung bài ⇒ ngắn có chủ ý (không có hàm
# kiểm trích nguyên văn dùng chung — trần 300 ký tự là rào chép bài). KHÔNG hết hạn: kết luận đã ghi không cũ đi như «không có quyền».
GHI_CHU_BAC_SI_MIN, GHI_CHU_BAC_SI_MAX = 5, 300
# Trạng thái kho cục bộ được tính ĐÃ PHỦ (không còn «chỉ tóm tắt» cần làm). `bac_si_da_doc_truc_tiep`: máy KHÔNG có toàn văn —
# bác sĩ tự đọc (NXB cấm AI/TDM) và ghi kết luận. Khác `cach` «bac_si_doc_truc_tiep» của phiếu = bài CHỜ bác sĩ đọc.
# «tdm_nxb» (03/10/2026): PDF tải qua kênh TDM chính thức của NXB bằng token của bác sĩ (Wiley TDM — SRC-042), lưu NGOÀI git
# dạng `PMID-<n>_WTDM.pdf`; KHÔNG gọi là OA (bài có bản quyền, chỉ dùng theo giấy phép TDM).
# «phien_chrome» (04/10/2026): HTML thân bài/PDF của NXB lưu trong PHIÊN UỶ QUYỀN của bác sĩ (`tools/phien_uy_quyen_chrome.py`),
# dạng `PMID-<n>_CHR.html|pdf` ngoài git; KHÔNG gọi là OA (tài khoản cá nhân của bác sĩ, điều khoản NXB không đổi).
TRANG_THAI_MAY_CO_TOAN_VAN = ("oa_xml", "oa_khac", "tdm_nxb", "phien_chrome", "da_doc_trinh_duyet")
TRANG_THAI_DA_PHU = TRANG_THAI_MAY_CO_TOAN_VAN + ("bac_si_da_doc_truc_tiep",)

# Đo 02/10/2026, yêu cầu trung thực «EBM-Copilot/1.0» (scratchpad do_mien.py) — số đo, không phải luật của nhà xuất bản. Đo lại
# 03/10/2026 13:04–13:10 (35/37 miền, cùng UA trung thực; không gọi scopus.com/dynamed.com): 6 miền đổi, ghi kèm ngày bên dưới.
# VPN đổi IP thoát ⇒ mỗi dòng là ẢNH CHỤP lúc đo, không phải trạng thái cố định.
MIEN_DO_DUOC: dict[str, str] = {
    "diabetesjournals.org": "chặn bot 403 «Just a moment…» (Cloudflare) — ADA Standards of Care",
    "academic.oup.com": "chặn bot 403 «Just a moment…» (Cloudflare) — ESC/EHJ trên OUP",
    "www.nejm.org": "chặn bot 403 (Cloudflare)",
    "www.thelancet.com": "chặn bot 403 (Cloudflare)",
    "jamanetwork.com": "chặn bot 403 (Cloudflare)",
    "www.ahajournals.org": "chặn bot 403 (Cloudflare) — AHA/ACC trên AHA journals",
    "onlinelibrary.wiley.com": "chặn bot 403 (Cloudflare)",
    "www.bmj.com": "chặn bot 403 «Just a moment…» (Cloudflare) — đo 03/10/2026, trang chủ + trang bài (02/10 là «Attention Required»)",
    "www.sciencedirect.com": "chặn truy cập tự động 403 (Elsevier)",
    "link.springer.com": "từ chối truy cập tự động 406",
    "kdigo.org": "MỞ (200) — đo 03/10/2026: trang chủ, /guidelines/, trang guideline và PDF đều 200 (02/10 là 406)",
    "www.fda.gov": "chặn bot 401 «automated request»",
    "journals.sagepub.com": "chặn bot 403 (Cloudflare)",
    "www.jacc.org": "chặn bot 403 (Cloudflare) — JACC",
    "heart.bmj.com": "chặn bot 403 «Attention Required» (Cloudflare)",
    "www.tandfonline.com": "chặn bot 403 (Cloudflare)",
    "www.nature.com": "từ chối truy cập tự động 406",
    "karger.com": "chặn bot 403 (Cloudflare)",
    "www.thieme-connect.com": "trang chờ «Please wait» (thử thách JS)",
    "journals.lww.com": "chặn bot 403 (Cloudflare)",
    "www.acpjournals.org": "chặn bot 403 (Cloudflare) — Annals of Internal Medicine",
    "www.mdpi.com": "chặn truy cập tự động 403 «Access Denied»",
    "www.cochranelibrary.com": "chặn bot 403 «Just a moment…» (Cloudflare) — đo 03/10/2026, trang chủ + trang bài CDSR (02/10 là 419)",
    "www.journal-of-hepatology.eu": "chặn bot 403 (Cloudflare)",
    "publications.ersnet.org": "chặn bot 403 (Cloudflare)",
    "www.atsjournals.org": "CHUYỂN 301 → academic.oup.com/atsjournals (URL bài cũ cũng về trang chung) rồi 403 «Just a moment…» — đo 03/10/2026; DOI 10.1164/… nay phân giải sang academic.oup.com/ajrccm/…",
    "linkinghub.elsevier.com": "trang CHUYỂN HƯỚNG của Elsevier (200 «Redirecting») → trang tạp chí/ScienceDirect (đều chặn 403)",
    "www.webofscience.com": "200 → /wos/ nhưng chỉ là vỏ ứng dụng JS (~3 KB, không nội dung) + cần tài khoản bác sĩ — đo 03/10/2026 (02/10 là 403)",
    "www.scopus.com": "cần tài khoản bác sĩ",
    "www.dynamed.com": "cần tài khoản bác sĩ",
    "www.escardio.org": "MỞ (200) — trang đích ESC; toàn văn guideline nằm trên academic.oup.com",
    "www.nice.org.uk": "MỞ (200)",
    "ginasthma.org": "MỞ (200)",
    "www.frontiersin.org": "MỞ (200) — thường là OA, dây chuyền OA lấy được",
    "www.acc.org": "MỞ (200) — trang hội; toàn văn guideline nằm trên jacc.org/ahajournals.org",
    "pmc.ncbi.nlm.nih.gov": "MỞ (200) — dùng dây chuyền OA, không cần làn này",
    "europepmc.org": "web chặn bot 403 «Just a moment…» — đo 03/10/2026 (02/10 là 200); REST API www.ebi.ac.uk/europepmc/webservices/rest vẫn 200 ⇒ dây chuyền OA dùng API, không cần làn này",
}
# DynaMed/UpToDate là bản TỔNG HỢP có bản quyền: chỉ dùng để đi tới nghiên cứu gốc (tools/tra_cuu_co_tai_khoan.py), không làm «toàn văn».
MIEN_TONG_HOP = ("dynamed.com", "uptodate.com", "bestpractice.bmj.com")

# ĐIỀU KHOẢN NHÀ XUẤT BẢN về dùng NỘI DUNG với công cụ AI / khai thác văn bản (TDM) — 03/10/2026, góp ý của phiên khác + phiên này
# tự đọc lại. CHỈ ghi điều ĐÃ ĐỌC (nguồn + ngày). NXB không có trong bảng = CHƯA KIỂM ⇒ hồ sơ phải tự khai `dieu_khoan` đã đọc.
# «cam» ⇒ Claude KHÔNG đọc/xử lý bài; bác sĩ đọc trực tiếp, hoặc đi đường hợp lệ (giấy phép TDM) — TRỪ KHI bác sĩ đã ghi uỷ quyền
# máy đọc cho đúng NXB đó (`uy_quyen_bac_si`, quyết định của bác sĩ, xem dưới). Nhận diện theo TIỀN TỐ DOI (một
# NXB có hàng trăm miền tạp chí — vd JACC, J Hepatol, Clin Gastroenterol Hepatol đều là 10.1016) rồi tới miền.
DIEU_KHOAN_NXB: dict[str, dict] = {
    "Elsevier": {
        # Tiền tố DOI của các NHÁNH xuất bản Elsevier (Saunders 10.1053 — Gastroenterology, AJKD; Mosby 10.1067; Churchill
        # Livingstone 10.1054; Academic Press 10.1006…) — Crossref /prefixes xác nhận «Elsevier BV» 03/10/2026. Thiếu chúng ⇒ bài
        # Gastroenterology/AJKD rơi vào «chưa kiểm» dù cùng điều khoản Elsevier. 10.1378 (CHEST — Crossref /prefixes «Elsevier BV»,
        # đo 04/10/2026): journal.chestnet.org chạy trên nền tảng Elsevier, chân trang «Terms and Conditions» trỏ ĐÚNG trang điều
        # khoản website Elsevier ở `nguon` (đọc trên Chrome 04/10/2026) ⇒ cùng điều khoản, cùng uỷ quyền.
        "ket_luan": "cam", "doi": ("10.1016/", "10.1053/", "10.1067/", "10.1054/", "10.1006/", "10.1078/", "10.1383/", "10.1157/",
                                     "10.1378/"),
        "mien": ("sciencedirect.com", "elsevier.com", "thelancet.com", "cell.com", "jacc.org", "journal-of-hepatology.eu",
                 "cghjournal.org", "elsevierhealth.com", "gastrojournal.org", "ajkd.org", "chestnet.org"),
        "nguon": "https://www.elsevier.com/legal/elsevier-website-terms-and-conditions", "doc_luc": "2026-10-03",
        "trich": "may not use Content … with an artificial intelligence tool … except … relevant license",
        "ngoai_le": "giấy phép, thoả thuận thuê bao hay cho phép của Elsevier; điều khoản riêng của dịch vụ (Scopus: khoá riêng dưới) hoặc hợp đồng thuê bao của cơ sở thắng điều khoản chung",
        "duong_hop_le": "API khai thác văn bản (TDM) của Elsevier cho nhà nghiên cứu thuộc cơ sở HỌC THUẬT có thuê bao, mục đích PHI THƯƠNG MẠI; dùng cùng AI theo API Service Agreement §2.4 (môi trường đóng, không huấn luyện, không chia sẻ, không lưu cục bộ đáng kể) — "
                        "https://www.elsevier.com/about/policies-and-standards/text-and-data-mining"},
    "ADA (American Diabetes Association)": {
        "ket_luan": "cam", "doi": ("10.2337/",), "mien": ("diabetesjournals.org", "diabetes.org"),
        "nguon": "https://www.diabetesjournals.org/journals/pages/license", "doc_luc": "2026-10-03",
        "trich": "CHƯA XÁC MINH NGUYÊN VĂN — trang trả 403 cho máy này; bác sĩ mở bằng Chrome để chép câu ≤ 15 từ",
        "duong_hop_le": "xin phép bằng văn bản (kênh cụ thể chưa xác minh lại: nút «Get Permissions» trên bài hoặc permissions@diabetes.org)"},
    "EBSCO (DynaMed)": {
        "ket_luan": "cam", "doi": (), "mien": ("dynamed.com", "ebsco.com", "ebscohost.com"),
        "nguon": "https://licenses.library.ubc.ca/EBSCOPublishing_Dynamed", "doc_luc": "2026-10-03",
        "loai_nguon": "tóm tắt giấy phép của thư viện UBC (đại diện) — chưa đọc điều khoản của chính EBSCO hay hợp đồng của bác sĩ; «cam» theo luật «không rõ ⇒ dừng»",
        "trich": "AI tool: Ask (phải hỏi phép) · Text and Data Mining: No",
        "duong_hop_le": "Dyna AI của chính EBSCO hoặc giấy phép bằng văn bản của EBSCO; chỉ dùng để tìm nghiên cứu gốc — tools/tra_cuu_co_tai_khoan.py --dynamed-canh-bao (bác sĩ tự chép, thỉnh thoảng bằng tay, không đưa vào lịch nền)"},
    # Hai nền tảng TRA CỨU (không phải NXB bài báo) — khoá riêng để uỷ quyền làn Chrome của bác sĩ (tools/tra_cuu_co_tai_khoan.py)
    # không lẫn với uỷ quyền đọc toàn văn bài Elsevier. Không có tiền tố DOI: chỉ nhận diện theo miền.
    "Scopus (Elsevier)": {
        "ket_luan": "cam", "doi": (), "mien": ("scopus.com",),
        "nguon": "https://www.elsevier.com/legal/elsevier-website-terms-and-conditions/elsevier-scopus-terms-and-conditions",
        "doc_luc": "2026-10-03",
        "trich": "used in a closed hosted, enterprise-grade, environment solely for the individual use",
        "loai_nguon": "Elsevier Terms and Conditions of Sale for Scopus (sửa 16/09/2026): §1.1 cho dùng cùng công cụ AI CHỈ khi đủ (a) môi trường đóng cấp doanh nghiệp, chỉ cho cá nhân người dùng được cấp quyền (b) không huấn luyện AI bên ngoài (c) không chia sẻ cho bên thứ ba; §1.2 cấm robot/spider/crawler ⇒ «không rõ ⇒ dừng»",
        "duong_hop_le": "Export chính thức do bác sĩ xuất ⇒ tools/tra_cuu_co_tai_khoan.py --nhap; Scopus API qua Elsevier Developer Portal theo API Service Agreement §2.4 (cờ ENABLE_SCOPUS của engine — tạm tắt chờ bác sĩ quyết)"},
    "Clarivate (Web of Science)": {
        "ket_luan": "cam", "doi": (), "mien": ("webofscience.com", "webofknowledge.com", "clarivate.com"),
        "nguon": "https://clarivate.com/download/web-of-science-apis/", "doc_luc": "2026-10-03",
        "trich": "must not use and access the Web of Science API data … application of artificial intelligence",
        "loai_nguon": "Product/Service Terms — Web of Science APIs v3.8 (17/07/2024) §4(a); End User Terms (12/2018) §3(b)(iv) cấm «automatically download, text mine or index Content»; Terms of Use 3.1 (24/11/2023) trang HTML trả 403 cho máy — chưa đọc lại nguyên văn",
        "ngoai_le": "«Artificial Intelligence Addendum» hoặc thoả thuận bằng văn bản hai bên ký với Clarivate; hợp đồng giấy phép của tổ chức thắng End User Terms",
        "duong_hop_le": "Export chính thức do bác sĩ xuất ⇒ tools/tra_cuu_co_tai_khoan.py --nhap; dùng cùng AI qua API cần AI Addendum của Clarivate (Developer Portal / Sales Support)"},
    # ESC giữ quyền cấp phép AI cho GUIDELINE của mình bất kể nơi đăng (EHJ/OUP, EJHF/Wiley…): miền escardio.org + luật nhận diện
    # theo TIÊU ĐỀ «ESC … Guidelines» trong `nxb_cua` (tiền tố DOI của tạp chí đăng guideline còn chở cả bài KHÔNG phải guideline).
    "ESC (European Society of Cardiology)": {
        "ket_luan": "cam", "doi": (), "mien": ("escardio.org",),
        "nguon": "https://www.escardio.org/guidelines/clinical-practice-guidelines/esc-guidelines-licensing-for-ai-llms-and-cds-tools/",
        "doc_luc": "2026-10-03",
        "trich": "explicit permission is required for AI-related applications—even if the content is publicly accessible",
        "duong_hop_le": "giấy phép AI/LLM/CDS của ESC qua ESC Licensing Form (có phí, theo năm); tái bản/dịch: xin Oxford University Press bằng văn bản"},
    "Springer Nature": {
        "ket_luan": "cam", "doi": ("10.1007/", "10.1038/"), "mien": ("link.springer.com", "springer.com", "nature.com"),
        "nguon": "https://datasolutions.springernature.com/tdm-reservation-policy/", "doc_luc": "2026-10-03",
        "trich": "explicitly reserves all rights in the Content for any kind of text-and-data-mining",
        "ngoai_le": "bài mang giấy phép CC của CHÍNH bài: theo đúng giấy phép (đường PMC OA); BMC (10.1186/) toàn OA nên không nằm trong tiền tố cấm",
        "duong_hop_le": "TDM cho nhà nghiên cứu qua tổ chức, mục đích phi thương mại (TDM API có phí, cần khoá); hỏi datasolutions@springernature.com"},
    # Đợt đọc điều khoản 03/10/2026 (bác sĩ yêu cầu phủ các hiệp hội/tạp chí uy tín cho làn Chrome). Năm NXB cấm RÕ việc dùng
    # nội dung với công cụ AI; ba NXB còn lại chỉ cấm huấn luyện mô hình hoặc im lặng về AI ⇒ «không rõ ⇒ xử như cấm» (doctrine
    # §2septies mục 4). Guideline ESC đăng trên OUP vẫn mang khoá ESC — `nxb_cua` xét tiêu đề ESC TRƯỚC nền tảng đăng bài.
    "Oxford University Press": {
        "ket_luan": "cam", "doi": ("10.1093/", "10.1210/", "10.1164/"), "mien": ("academic.oup.com", "oup.com"),
        "nguon": "https://academic.oup.com/pages/legal-notice", "doc_luc": "2026-10-03",
        "trich": "use any portion of the Content in combination with any artificial intelligence (AI) tool",
        "loai_nguon": "Legal notice của Oxford Academic, mục «Text and Data Mining, TDM Reservation Policy, and Artificial "
                      "Intelligence Systems» (đọc bằng Chrome); 10.1210 = Endocrine Society (JCEM…), 10.1164 = ATS (AJRCCM…) — "
                      "atsjournals.org chuyển 301 sang academic.oup.com (đo 03/10/2026)",
        "ngoai_le": "Subscriber Agreement của cơ sở, giấy phép CC của bài Open Access, giấy phép chính phủ cho Government Works",
        "duong_hop_le": "TDM phi thương mại theo Subscription Agreement của cơ sở có quyền truy cập hợp pháp; dùng với AI/TDM thương mại "
                        "phải có thoả thuận — data.mining@oup.com"},
    "Massachusetts Medical Society (NEJM)": {
        "ket_luan": "cam", "doi": ("10.1056/",), "mien": ("nejm.org", "nejmgroup.org"),
        "nguon": "https://www.nejmgroup.org/legal/terms-of-use.htm", "doc_luc": "2026-10-03",
        "trich": "test, process, analyze, train, generate output from, or develop any form of artificial intelligence",
        "loai_nguon": "NEJM Group Terms of Use (sửa 01/2026), §4 Prohibited Conduct — đọc qua WebFetch (bản chuyển markdown), "
                      "chưa mở bằng trình duyệt; §2 giữ mọi quyền TDM/huấn luyện AI, chỉ cho dùng cá nhân phi thương mại",
        "duong_hop_le": "xin phép bằng văn bản của NEJM Group (permissions) — chưa có kênh TDM/AI công khai"},
    "American Medical Association (JAMA Network)": {
        "ket_luan": "cam", "doi": ("10.1001/",), "mien": ("jamanetwork.com", "ama-assn.org"),
        "nguon": "https://www.ama-assn.org/about/terms-use", "doc_luc": "2026-10-03",
        "trich": "CHƯA XÁC MINH NGUYÊN VĂN — ama-assn.org chặn cứng («Sorry, you have been blocked») cả Chrome của bác sĩ",
        "loai_nguon": "jamanetwork.com/pages/terms-of-use chuyển 301 sang trang AMA; trang AMA chặn cứng 03/10/2026; hướng dẫn "
                      "biên tập JAMA Network (chỉ qua kết quả tìm kiếm, chưa đọc nguyên văn) nêu cấm đưa bài vào mô hình AI khi "
                      "chưa có giấy phép ⇒ «không rõ ⇒ dừng»",
        "duong_hop_le": "xin phép/giấy phép của AMA (JAMA Network permissions) — kênh cụ thể chưa xác minh"},
    "American Academy of Pediatrics": {
        "ket_luan": "cam", "doi": ("10.1542/",), "mien": ("publications.aap.org", "aap.org", "aappublications.org"),
        "nguon": "https://www.aap.org/en/pages/terms-of-use/", "doc_luc": "2026-10-03",
        "trich": "in conjunction with any artificial intelligence tool without the express written permission of the AAP",
        "loai_nguon": "AAP Terms of Use (sửa 24/09/2026) — đọc qua WebFetch; điều khoản phủ «websites, apps, and digital "
                      "platforms provided by AAP», không nêu đích danh publications.aap.org",
        "duong_hop_le": "văn bản cho phép của AAP"},
    "SAGE Publishing": {
        "ket_luan": "cam", "doi": ("10.1177/",), "mien": ("journals.sagepub.com", "sagepub.com"),
        "nguon": "https://www.sagepub.com/tdm-ai-policy", "doc_luc": "2026-10-03",
        "trich": "for any AI uses including generative AI you will need … a license from Sage",
        "loai_nguon": "Sage Policy on TDM and AI (không ghi ngày) — đọc qua WebFetch; TDM phi thương mại nội dung có quyền truy "
                      "cập hợp pháp thì KHÔNG cần giấy phép, nhưng mọi việc dùng với AI (gồm RAG) cần giấy phép",
        "duong_hop_le": "giấy phép AI của Sage — permissions@sagepub.com"},
    "BMJ Publishing Group": {
        "ket_luan": "cam", "doi": ("10.1136/",), "mien": ("bmj.com", "bmjgroup.com"),
        "nguon": "https://bmjgroup.com/text-and-data-mining-tdm-policy/", "doc_luc": "2026-10-03",
        "trich": "development, training, fine-tuning or validation of AI systems or models",
        "loai_nguon": "TDM policy and licence (06/01/2026) — đọc qua WebFetch: cho TDM PHI THƯƠNG MẠI nội dung có quyền truy cập "
                      "hợp pháp, cấm TDM để phát triển/huấn luyện/kiểm định hệ AI; im lặng về dùng công cụ AI để đọc–tóm tắt "
                      "⇒ «không rõ ⇒ xử như cấm»",
        "ngoai_le": "bài Open Access theo đúng giấy phép CC của bài",
        "duong_hop_le": "TDM phi thương mại theo chính sách BMJ (không dùng cho phát triển AI); dùng với AI cần BMJ cho phép"},
    "American College of Physicians (Annals)": {
        "ket_luan": "cam", "doi": ("10.7326/",), "mien": ("acpjournals.org", "annals.org", "acponline.org"),
        "nguon": "https://www.acpjournals.org/journal/aim/conditions-of-use", "doc_luc": "2026-10-03",
        "trich": "YOU MAY NOT USE CONTENT TO TRAIN AI MODELS OR USE CONTENT FOR OTHER PURPOSES",
        "loai_nguon": "Conditions of Use của Annals.org (đọc bằng Chrome): nội dung «for personal noncommercial use», cấm rõ "
                      "huấn luyện AI; không nói về công cụ AI đọc–tóm tắt ⇒ «không rõ ⇒ xử như cấm»",
        "duong_hop_le": "permissions@acponline.org"},
    "Wolters Kluwer Health (LWW · AHA journals · Neurology)": {
        "ket_luan": "cam", "doi": ("10.1097/", "10.1161/", "10.1212/"),
        "mien": ("journals.lww.com", "lww.com", "ovid.com", "ahajournals.org", "neurology.org"),
        "nguon": "https://www.ovid.com/global/terms", "doc_luc": "2026-10-03",
        "trich": "any commercial use of any Site Materials … without the prior written consent of WKH",
        "loai_nguon": "Terms and Conditions của WKH (journals.lww.com nay chuyển sang ovid.com — đo 03/10/2026; đọc bằng Chrome): "
                      "không có điều về AI/TDM; hướng dẫn tác giả của WK và trang AHA journals (chỉ qua kết quả tìm kiếm, chưa đọc "
                      "nguyên văn) cấm tải bài vào AI tạo sinh/cào để huấn luyện AI ⇒ «không rõ ⇒ xử như cấm»; 10.1161 = AHA, 10.1212 = AAN",
        "ngoai_le": "bài Open Access theo giấy phép CC của bài (vd JAHA)",
        "duong_hop_le": "TDM qua CCC RightFind XML for Mining (Wolters Kluwer Health tham gia); dùng với AI cần WKH cho phép"},
    "The Journal of Rheumatology": {
        "ket_luan": "cam", "doi": ("10.3899/",), "mien": ("jrheum.org", "jrheum.com"),
        "nguon": "https://www.jrheum.com/terms_of_use", "doc_luc": "2026-10-04",
        "trich": "reproduce, republish, download, post, transmit, distribute, copy, publicly display, or otherwise use any Content",
        "loai_nguon": "Terms of Use của jrheum.com (cập nhật 08/12/2016; đọc 04/10/2026 bằng tải trang, 9.601 ký tự): cấm sao "
                      "chép/tải/dùng nội dung dưới mọi hình thức; không có điều nào về AI/TDM ⇒ «không rõ ⇒ xử như cấm». Trang "
                      "điều khoản của jrheum.org trả 403 cho máy",
        "duong_hop_le": "xin phép The Journal of Rheumatology Publishing Co. Ltd. (mục Permissions của jrheum.org)"},
    "CMAJ (Canadian Medical Association)": {
        "ket_luan": "cam", "doi": ("10.1503/",), "mien": ("cmaj.ca", "cma.ca"),
        "nguon": "https://www.cmaj.ca/page/copyright", "doc_luc": "2026-10-04",
        "trich": "may only be copied or shared for non-commercial educational purposes",
        "loai_nguon": "Trang «Copyright, open access, and permission to reuse» của CMAJ + Terms and Conditions của CMA (cma.ca; "
                      "đọc trên Chrome 04/10/2026; Crossref: tiền tố 10.1503 của CMA Impact Inc.): bài trước 01/01/2021 chỉ được "
                      "sao bản đơn lẻ dùng giáo dục phi thương mại, không tác phẩm phái sinh; bài từ 2021 mang CC BY-NC-ND/CC BY "
                      "(đi đường OA theo giấy phép của bài); không có điều nào về AI/TDM ⇒ «không rõ ⇒ xử như cấm»",
        "duong_hop_le": "xin phép CMA (mục Copyright and Permissions của cmaj.ca)"},
    "Wiley (Wiley Online Library · Cochrane Library)": {
        "ket_luan": "cam", "doi": ("10.1002/", "10.1111/", "10.1046/", "10.1034/"),
        "mien": ("onlinelibrary.wiley.com", "wiley.com", "cochranelibrary.com"),
        "nguon": "https://onlinelibrary.wiley.com/terms-and-conditions", "doc_luc": "2026-10-04",
        "trich": "Use or enable artificial intelligence technologies and tools to ingest, train, test, analyze, process",
        "loai_nguon": "Terms of Use của Wiley Online Library (đọc 04/10/2026 bằng Chrome sau khi bác sĩ tự qua Cloudflare): bảo lưu "
                      "mọi quyền TDM/huấn luyện AI; CẤM dùng công cụ AI phân tích, xử lý, sinh đầu ra từ nội dung — kể cả qua "
                      "plugin/tiện ích bên thứ ba; cấm công cụ tự động; TDM chỉ theo Thoả thuận TDM của Wiley. Cochrane Library do "
                      "Wiley xuất bản (điều khoản riêng của cochranelibrary.com chưa đọc). Hindawi (10.1155/) toàn OA CC BY nên KHÔNG "
                      "chặn theo tiền tố",
        "ngoai_le": "bài Open Access theo giấy phép CC của bài",
        "duong_hop_le": "Wiley TDM API theo Thoả thuận TDM (token của bác sĩ, SRC-042) + Wiley Scholar Gateway (kênh AI có giấy phép)"},
}
# Tiêu đề guideline của ESC (cả guideline đồng chủ trì «ESC/EAS…», «ESC/ERS…») — xem mục ESC ở trên.
_TIEU_DE_ESC_GUIDELINE = re.compile(r"\bESC(?:/[A-Z][A-Za-z]*)*\b[^.\n]{0,40}\bGuidelines?\b")
_KET_LUAN_DIEU_KHOAN_NHAN = {"cho_phep", "giay_phep_cc"}

# BÁC SĨ UỶ QUYỀN MÁY ĐỌC (03/10/2026 — bác sĩ quyết trong chat: «Vậy hãy chỉnh sửa lại để máy đọc toàn văn và tóm tắt cho tôi»).
# Bác sĩ là chủ hệ thống có thể quyết cho Claude đọc toàn văn bài của một NXB «cam» mà bác sĩ CÓ quyền truy cập (qua Chrome của
# bác sĩ). Điều khoản của NXB KHÔNG đổi — Elsevier chỉ cho dùng Content với AI khi có giấy phép/thuê bao/sự cho phép; đây là
# QUYẾT ĐỊNH và TRÁCH NHIỆM của bác sĩ, KHÔNG phải «NXB cho phép». Tệp quyết định nằm NGOÀI git (dữ liệu của bác sĩ); công cụ chỉ
# ghi nó qua `--ghi-uy-quyen … --ghi` bằng ĐÚNG lời bác sĩ. Tệp vắng/hỏng/hết hạn ⇒ KHÔNG có uỷ quyền (fail-closed).
TEN_TEP_UY_QUYEN = "dieu-khoan-bac-si-uy-quyen.json"
KET_LUAN_UY_QUYEN = "bac_si_uy_quyen"   # CHỈ nhận ở nhánh NXB «cam» có uỷ quyền — NXB chưa kiểm vẫn chỉ cho_phep | giay_phep_cc
CAN_CU_UY_QUYEN_MIN = 10
DONG_QUYET_DINH = ("Đọc theo QUYẾT ĐỊNH của bác sĩ ngày {ngay} (điều khoản {nxb} chỉ cho dùng với AI khi có giấy phép/thuê bao/"
                   "sự cho phép — trách nhiệm điều khoản thuộc bác sĩ).")
_ABOUT_UY_QUYEN = ("Quyết định của BÁC SĨ (chủ hệ thống) cho Claude đọc toàn văn bài của NXB «cấm» trong DIEU_KHOAN_NXB mà bác sĩ CÓ "
                   "quyền truy cập, chỉ qua Chrome của bác sĩ, để tóm tắt và lập hồ sơ trích xuất có cấu trúc (trích ≤ 15 từ, không "
                   "lưu toàn văn). Điều khoản của NXB KHÔNG đổi; đây KHÔNG phải «NXB cho phép» — trách nhiệm điều khoản thuộc bác sĩ. "
                   "Ghi bằng tools/doc_toan_van_co_nguoi.py --ghi-uy-quyen (đúng lời bác sĩ, có ngày); agent KHÔNG tự ghi khi bác sĩ "
                   "chưa nói rõ trong chat. Xoá một mục (hoặc thêm het_han) = rút uỷ quyền.")


def tep_uy_quyen_mac_dinh() -> Path:
    """Đường dẫn tệp quyết định — tính LÚC GỌI từ `DASH` (test đổi được `DASH`; không chốt lúc import)."""
    return DASH / TEN_TEP_UY_QUYEN


def _ngay_iso(s) -> date | None:
    s = str(s or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def uy_quyen_bac_si(nxb: str | None, hom_nay: date | None = None, tep: Path | None = None) -> dict | None:
    """Uỷ quyền CÒN HIỆU LỰC của bác sĩ cho đúng NXB «cam» `nxb` (khoá của DIEU_KHOAN_NXB), hoặc None.

    Fail-closed: tệp vắng / không đọc được / sai cấu trúc ⇒ None; mục khác NXB, ngày sai dạng hay ở tương lai, căn cứ quá ngắn,
    `het_han` sai dạng hoặc đã qua (hôm nay > het_han) ⇒ bỏ qua mục đó. Nhiều mục hợp lệ ⇒ mục ngày mới nhất (bằng ngày: mục sau)."""
    hom_nay = hom_nay or date.today()
    if not nxb or (DIEU_KHOAN_NXB.get(nxb) or {}).get("ket_luan") != "cam":
        return None
    tep = Path(tep) if tep else tep_uy_quyen_mac_dinh()
    try:
        d = json.loads(tep.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    muc = d.get("muc") if isinstance(d, dict) else None
    if not isinstance(muc, list):
        return None
    tot: dict | None = None
    for m in muc:
        if not isinstance(m, dict) or m.get("nxb") != nxb:
            continue
        ngay = _ngay_iso(m.get("ngay"))
        if ngay is None or ngay > hom_nay or len(str(m.get("can_cu") or "").strip()) < CAN_CU_UY_QUYEN_MIN:
            continue
        if m.get("het_han") not in (None, ""):
            hh = _ngay_iso(m.get("het_han"))
            if hh is None or hom_nay > hh:
                continue
        if tot is None or ngay >= _ngay_iso(tot["ngay"]):
            tot = m
    return dict(tot) if tot else None


def nxb_cua(doi: str = "", url: str = "", tieu_de: str = "") -> tuple[str | None, dict | None]:
    """(tên NXB, mục điều khoản) theo TIÊU ĐỀ guideline ESC trước, rồi tiền tố DOI, rồi miền; không khớp ⇒ (None, None) = CHƯA KIỂM.

    Tiêu đề ESC đứng TRƯỚC (03/10/2026): từ khi OUP (nơi đăng EHJ) vào bảng, xét tiền tố trước sẽ gán guideline ESC cho OUP và
    mất luật cấp phép AI riêng của ESC (cùng là «cấm», nhưng đường hợp lệ và uỷ quyền theo khoá khác nhau)."""
    if tieu_de and _TIEU_DE_ESC_GUIDELINE.search(tieu_de):
        ten = "ESC (European Society of Cardiology)"
        return ten, DIEU_KHOAN_NXB[ten]
    doi, h = (doi or "").lower(), _mien(url)
    for ten, d in DIEU_KHOAN_NXB.items():
        if any(doi.startswith(t) for t in d["doi"]) or (h and any(h == m or h.endswith("." + m) for m in d["mien"])):
            return ten, d
    return None, None


def lech_doctrine(van_ban: str) -> list[str]:
    """So bảng `DIEU_KHOAN_NXB` với doctrine `.claude/agents/_CONNECTOR-CHUNG-CU.md` §2septies (03/10/2026).

    Cổng (`kiem_ho_so`) chỉ chặn hồ sơ SAU khi agent đã đọc bài; doctrine mới là chỗ dạy agent dừng TRƯỚC khi mở bài
    (CLAUDE.md §6.4). Thêm một NXB «cấm» vào bảng mà quên doctrine ⇒ agent vẫn mở bài đó. Trả danh sách chỗ lệch (rỗng = khớp)."""
    i = van_ban.find("## 2septies. ")
    if i < 0:
        return ["doctrine mất §2septies (điều khoản NXB trước toàn văn)"]
    j = van_ban.find("\n## ", i + 5)
    muc = van_ban[i:j if j > 0 else len(van_ban)]
    # Tên so phần TRƯỚC « (»: chữ đầu một mình quá lỏng — tên mở đầu bằng từ phổ biến («The Journal of Rheumatology») «khớp»
    # chỉ cần chữ «The» có ở chỗ khác trong mục (04/10/2026).
    lech = [f"§2septies không nêu NXB «cấm» {ten} kèm tiền tố DOI {d['doi']}"
            for ten, d in DIEU_KHOAN_NXB.items()
            if d.get("ket_luan") == "cam"
            and (ten.split(" (")[0].strip() not in muc or any(f"`{t}`" not in muc for t in d["doi"]))]
    if "tools/doc_toan_van_co_nguoi.py" not in muc:
        lech.append("§2septies không trỏ công cụ tools/doc_toan_van_co_nguoi.py")
    if "8. **ĐIỀU KHOẢN NXB TRƯỚC TOÀN VĂN.**" not in van_ban:
        lech.append("mất luật §0.8 «ĐIỀU KHOẢN NXB TRƯỚC TOÀN VĂN»")
    return lech


_TIEU_DE_DANG_NHAP = re.compile(r"\b(sign in|sign-in|log in|login|access through your institution|purchase (pdf|article|access)|"
                                r"subscribe|đăng nhập|institutional login|get access|buy article|mua bài|truy cập qua tổ chức)\b", re.I)
_TIEU_DE_CAM_DU_PHONG = re.compile(r"automated request|not a bot|robot|captcha|just a moment|attention required|access denied|"
                                   r"forbidden|page not found|not found|\b40[1346]\b|\berror\b|please wait|one moment|"
                                   r"chờ một chút|xác minh bạn là con người|xác minh bảo mật|không phải là bot|truy cập bị từ chối|"
                                   r"không tìm thấy trang|\blỗi\b|vui lòng chờ", re.I)
_KHOA_CAM = {"toan_van", "full_text", "fulltext", "noi_dung", "noi_dung_trang", "van_ban", "text", "html"}
_NGUON_TRUY_CAP = {"trinh_duyet_co_nguoi", "tai_khoan_bac_si", "trang_mo"}
_LOAI = {"rct", "sr_ma", "guideline", "cohort", "case_control", "cat_ngang", "chan_doan", "khac"}
_TY_SO = {"HR", "RR", "OR", "IRR", "SHR", "AHR", "AOR", "ARR_RATIO", "PR", "SRR", "RATE RATIO"}
_PII = (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), re.compile(r"(?<![\w])0\d{9,10}(?![\w])"), re.compile(r"(?<![A-Za-z\d])\d{12}(?!\d)"))
# Mục bắt buộc để hồ sơ được tính «full» (thiếu ⇒ partial: vẫn ghi, nhưng thẻ giữ trần «Cân nhắc»).
_MUC_DU = {
    "rct": ("thiet_ke", "quan_the", "can_thiep_so_sanh", "ket_cuc_chinh", "ngau_nhien_lam_mu"),
    "sr_ma": ("thiet_ke", "quan_the", "ket_cuc_chinh", "nguy_co_sai_lech", "di_bien"),
    "guideline": ("thiet_ke",),
}
_MUC_DU_MAC_DINH = ("thiet_ke", "quan_the", "ket_cuc_chinh")

HUONG_DAN = """QUY TRÌNH «ĐỌC TOÀN VĂN QUA TRÌNH DUYỆT CÓ BÁC SĨ» (Claude làm; bác sĩ chỉ vượt chặn/đăng nhập trên trang):
  0. `python3 tools/gom_toan_van_dashboard.py --queue <tệp>` trước — bài có bản OA thì dây chuyền OA lấy, KHÔNG cần làn này.
  1. `python3 tools/doc_toan_van_co_nguoi.py --queue queue/tuan-<W>.md` → phiếu: bài nào chưa có toàn văn, mở ở URL nào,
     nhóm theo MIỀN (bác sĩ vượt chặn MỘT lần cho mỗi miền là đọc được cả nhóm).
  2a. ĐIỀU KHOẢN NHÀ XUẤT BẢN trước tiên (03/10/2026). NXB trong `DIEU_KHOAN_NXB` với kết luận «cấm» (Elsevier — DOI 10.1016/…,
     ADA — 10.2337/…, EBSCO/DynaMed) ⇒ Claude KHÔNG mở bài; phiếu đã xếp chúng vào «BÁC SĨ ĐỌC TRỰC TIẾP».
     Bác sĩ đọc trực tiếp xong ⇒ `python3 tools/doc_toan_van_co_nguoi.py --bac-si-da-doc <PMID> --ghi-chu "<kết luận của bác sĩ>"`
     (chạy thử) rồi thêm `--ghi`. Ghi chú là KẾT LUẬN bằng lời bác sĩ ({GHI_CHU_MIN}–{GHI_CHU_MAX} ký tự, không PII), KHÔNG chép nội
     dung bài. Bác sĩ KHÔNG dán nội dung bài Elsevier/ADA vào chat — Claude không được đọc nó. Thẻ thành «BÁC SĨ ĐÃ ĐỌC TRỰC TIẾP»
     (đã phủ, không hết hạn); máy vẫn KHÔNG có toàn văn bài đó.
     NGOẠI LỆ — BÁC SĨ UỶ QUYỀN MÁY ĐỌC (03/10/2026): bác sĩ nói rõ trong chat là cho máy đọc bài của một NXB «cấm» mà bác sĩ có
     quyền truy cập ⇒ phiên Claude ghi ĐÚNG lời bác sĩ: `--ghi-uy-quyen "<khoá NXB>" --can-cu "<nguyên văn lời bác sĩ>"` (chạy
     thử) rồi thêm `--ghi` (vào EBM-Dashboards/dieu-khoan-bac-si-uy-quyen.json). Phiếu xếp bài NXB đó vào làn trình duyệt có
     người, nhãn «BÁC SĨ UỶ QUYỀN MÁY ĐỌC (<ngày>)»; chỉ qua Chrome của bác sĩ; hồ sơ khai `dieu_khoan` {ket_luan:
     bac_si_uy_quyen, ngay_uy_quyen: <đúng ngày trong tệp>}. Điều khoản NXB KHÔNG đổi — quyết định và trách nhiệm của bác sĩ,
     KHÔNG phải «NXB cho phép». Agent KHÔNG tự ghi uỷ quyền khi bác sĩ chưa nói rõ trong chat.
  2b. NXB CHƯA KIỂM ⇒ Claude đọc trang ĐIỀU KHOẢN (không phải bài) của NXB, tìm điều về AI / text-and-data mining. Cấm hoặc không rõ
     ⇒ dừng, bác sĩ đọc trực tiếp. Cho phép rõ, hoặc bài mang giấy phép CC ⇒ ghi vào hồ sơ `dieu_khoan` {url, doc_luc, ket_luan:
     cho_phep | giay_phep_cc, trich ≤ 15 từ}; NXB đã kiểm thì đề xuất thêm vào DIEU_KHOAN_NXB bằng PR.
  2. Với từng bài được phép: Claude mở URL bằng Claude in Chrome (Chrome thật của bác sĩ, đã đăng nhập sẵn — bác sĩ dặn
     03/10/2026); vắng Chrome thì dùng trình duyệt trong app (Claude_Browser → navigate); chụp màn hình.
     • Trang chặn bot («Just a moment…», «I am not a bot», CAPTCHA) hoặc trang đăng nhập ⇒ Claude DỪNG, nhờ BÁC SĨ tự bấm/đăng
       nhập ngay trong khung trình duyệt rồi nói «xong». Claude KHÔNG bấm, KHÔNG giải CAPTCHA, KHÔNG gõ tài khoản/mật khẩu,
       KHÔNG giả dạng trình duyệt.
     • Trang đòi MUA bài / «Access through your institution» mà bác sĩ không có quyền ⇒ không đọc;
       `--khong-truy-cap <PMID> --ly-do "<…>"` (không nhắc lại 90 ngày). Thẻ giữ «chỉ tóm tắt».
     • DynaMed/UpToDate là bản tổng hợp có bản quyền ⇒ chỉ dùng để tìm nghiên cứu gốc (tools/tra_cuu_co_tai_khoan.py).
  3. Trang toàn văn đã hiện: Claude đọc bằng get_page_text (max_chars đủ lớn) — bài dài (guideline hàng trăm nghìn ký tự) thì
     lọc đoạn cần (khuyến cáo/kết quả/hạn chế) bằng javascript_tool — và tính dấu văn bản NGAY TRONG trình duyệt:
       const t=document.body.innerText; const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t));
       ({title:document.title, len:t.length, sha_parts:[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')
         .match(/.{8}/g).join(' ')})
     (Claude in Chrome che chuỗi hex 64 ký tự liền thành «[BLOCKED: Base64 encoded data]» — đo 03/10/2026; trả theo nhóm 8 rồi
     bỏ dấu cách khi điền `sha256_toan_van`.)
  4. Claude điền hồ sơ theo `--mau`: con số CHÉP ĐÚNG như bài báo cáo (không quy đổi HR/RR/OR), mỗi số kèm `vi_tri` (Bảng 2,
     Hình 3, Kết quả ¶4…) để bác sĩ đối chiếu; phương pháp/hạn chế/tài trợ viết bằng LỜI CỦA CLAUDE; trích nguyên văn chỉ khi
     cần và ≤ 15 từ/lần, ≤ 6 lần. KHÔNG dán toàn văn vào tệp, chat hay repo.
  5. `python3 tools/doc_toan_van_co_nguoi.py --nap <hồ sơ>.json` (chạy thử) → sửa đến khi đạt → thêm `--ghi`. Công cụ xác minh
     định danh qua cơ quan đăng ký (Crossref/PubMed), chặn bài đã rút, kiểm con số/CI, từ chối tiêu đề trang chặn/đăng nhập.
  6. Gói tuần đọc `EBM-Dashboards/toan_van_oa/doc_sau/PMID-<n>.md` như bản OA; hồ sơ «partial» (thiếu mục) vẫn giữ trần
     «Cân nhắc». Toàn văn KHÔNG tự nâng đề xuất — nâng/hạ là thẩm quyền bác sĩ. Cần bác sĩ kiểm chứng.""".replace(
    "{GHI_CHU_MIN}", str(GHI_CHU_BAC_SI_MIN)).replace("{GHI_CHU_MAX}", str(GHI_CHU_BAC_SI_MAX))

MAU = {
    "pmid": "42377292", "doi": "10.1016/j.jacc.2026.05.033",
    "tieu_de_bai": "<tiêu đề bài như trên trang>",
    "url_doc": "<URL trang toàn văn đã đọc>",
    "tieu_de_trang": "<document.title lúc đọc>",
    "doc_luc": date.today().isoformat(),
    "nguon_truy_cap": "trinh_duyet_co_nguoi | tai_khoan_bac_si | trang_mo",
    "gap_chan": True, "nguoi_vuot_chan": "bac_si",
    "so_ky_tu_toan_van": 0, "sha256_toan_van": "<64 ký tự hex tính trong trình duyệt>",
    "loai_tai_lieu": "rct | sr_ma | guideline | cohort | case_control | cat_ngang | chan_doan | khac",
    "phuong_phap": {"thiet_ke": "", "quan_the": "", "can_thiep_so_sanh": "", "ket_cuc_chinh": "", "ngau_nhien_lam_mu": "",
                    "dang_ky": "", "nguy_co_sai_lech": "", "di_bien": ""},
    "ket_qua": [{"ket_cuc": "", "chi_so": "HR", "gia_tri": 0.0, "ci_duoi": 0.0, "ci_tren": 0.0, "p": "", "nhom": "",
                 "vi_tri": "Bảng 2", "trich_ngan": ""}],
    "khuyen_cao": [{"tom_tat": "", "muc": "Class I, LOE A", "vi_tri": ""}],
    "han_che": "", "tai_tro_coi": "", "ghi_chu": "",
    "dieu_khoan": {"url": "<trang điều khoản NXB đã đọc>", "doc_luc": date.today().isoformat(),
                   "ket_luan": "cho_phep | giay_phep_cc | bac_si_uy_quyen (CHỈ NXB «cấm» có uỷ quyền của bác sĩ còn hiệu lực)",
                   "trich": "<≤ 15 từ nguyên văn điều cho phép / tên giấy phép CC>",
                   "ngay_uy_quyen": "<chỉ khi bac_si_uy_quyen: đúng ngày của mục trong EBM-Dashboards/dieu-khoan-bac-si-uy-quyen.json>"},
}


# ── tiện ích ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _nap_mo_dun(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parent / tep)
    m = importlib.util.module_from_spec(sp)
    sys.modules[ten] = m
    sp.loader.exec_module(m)
    return m


def _tu(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").casefold()) if len(w) >= 3}


def do_giong(a: str, b: str) -> float:
    """Jaccard theo từ (≥3 ký tự) — đủ để bắt «nhầm bài», không phải đo ngữ nghĩa."""
    x, y = _tu(a), _tu(b)
    return len(x & y) / len(x | y) if x and y else 0.0


def _mien(url: str) -> str:
    return (urlparse(url or "").hostname or "").lower()


def phan_loai_mien(url: str) -> str:
    """Mô tả miền theo SỐ ĐO 02/10/2026; miền con chưa đo thì SUY từ miền mẹ và ghi rõ là suy."""
    h = _mien(url)
    if not h:
        return "không có URL"
    if h in MIEN_DO_DUOC:
        return MIEN_DO_DUOC[h] + " — đo 02/10/2026"
    goc = h.split(".", 1)[-1] if h.count(".") >= 2 else h
    for m, mo_ta in MIEN_DO_DUOC.items():
        if m.removeprefix("www.") in (goc, h.removeprefix("www.")):
            return f"chưa đo riêng — suy từ {m}: {mo_ta}"
    return "chưa đo — mở thử trong trình duyệt"


def pmid_cua_queue(tep: Path) -> list[str]:
    """PMID trên các THẺ của gói tuần (khối «⓶ … THẺ» tới khối kế); không có khối thẻ thì cả tệp — giống doc_sau_toan_van."""
    vb = tep.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^## [^\n]*THẺ[^\n]*$", vb, re.M)
    if m:
        sau = vb[m.end():]
        k = re.search(r"^## ", sau, re.M)
        vb = sau[:k.start()] if k else sau
    return list(dict.fromkeys(re.findall(r"PMID[ :]?(\d{6,9})", vb)))


def _khong_truy_cap(kho: Path, hom_nay: date) -> dict[str, dict]:
    tep = kho / "trinh_duyet" / "khong-truy-cap.jsonl"
    ra: dict[str, dict] = {}
    if not tep.exists():
        return ra
    for dong in tep.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(dong)
            if (hom_nay - date.fromisoformat(d["ngay"])).days <= HAN_KHONG_TRUY_CAP_NGAY:
                ra[str(d["pmid"])] = d
        except (ValueError, KeyError, TypeError):
            continue
    return ra


def _bac_si_da_doc(kho: Path) -> dict[str, dict]:
    """Sổ «bác sĩ đã đọc trực tiếp» (`trinh_duyet/bac-si-da-doc.jsonl`) — KHÔNG hết hạn; dòng hỏng bỏ qua; dòng sau của cùng PMID thắng."""
    tep = kho / "trinh_duyet" / "bac-si-da-doc.jsonl"
    ra: dict[str, dict] = {}
    if not tep.exists():
        return ra
    for dong in tep.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(dong)
            ra[str(d["pmid"])] = d
        except (ValueError, KeyError, TypeError):
            continue
    return ra


_GOM_TV = None


def _upw_la_toan_van(kho: Path, pm: str) -> bool:
    """Có bản `_UPW` là TOÀN VĂN thật: PDF, hoặc HTML qua cổng nội dung của `gom_toan_van_dashboard.la_toan_van_html` (BH160 —
    04/10/2026: 15/27 `_UPW.html` trong kho là TRANG GIỚI THIỆU kho lưu trữ, từng bị tính «oa_khac»). Không nạp được cổng nội dung
    ⇒ HTML không được tính (fail-closed: chưa biết ≠ có toàn văn)."""
    global _GOM_TV
    for q in kho.glob(f"PMID-{pm}_UPW.*"):
        if q.suffix.lower() != ".html":
            return True
        if _GOM_TV is None:
            try:
                _GOM_TV = _nap_mo_dun("_gom_tv_bpcb", "gom_toan_van_dashboard.py")
            except Exception:  # noqa: BLE001
                _GOM_TV = False
        if _GOM_TV and _GOM_TV.la_toan_van_html(_GOM_TV._van_ban_tho(q.read_bytes()))[0]:
            return True
    return False


def bao_phu_cuc_bo(pmids: list[str], kho: Path | None = None, hom_nay: date | None = None) -> dict[str, str]:
    """Trạng thái từng PMID chỉ từ kho cục bộ (NGOẠI TUYẾN): oa_xml · oa_khac · tdm_nxb · phien_chrome · da_doc_trinh_duyet · bac_si_da_doc_truc_tiep ·
    khong_truy_cap · chua_co. «bac_si_da_doc_truc_tiep» xét TRƯỚC «khong_truy_cap»: bác sĩ đã đọc thì không còn là «không có quyền»."""
    kho, hom_nay = kho or KHO, hom_nay or date.today()
    ktc = _khong_truy_cap(kho, hom_nay)
    bsd = _bac_si_da_doc(kho)
    ra = {}
    for pm in pmids:
        if list(kho.glob(f"PMID-{pm}_*.xml")):
            ra[pm] = "oa_xml"
        elif _upw_la_toan_van(kho, pm):
            ra[pm] = "oa_khac"
        elif list(kho.glob(f"PMID-{pm}_WTDM.*")):
            ra[pm] = "tdm_nxb"
        elif list(kho.glob(f"PMID-{pm}_CHR.*")):
            ra[pm] = "phien_chrome"
        elif (kho / "trinh_duyet" / f"PMID-{pm}.json").exists():
            ra[pm] = "da_doc_trinh_duyet"
        elif pm in bsd:
            ra[pm] = "bac_si_da_doc_truc_tiep"
        elif pm in ktc:
            ra[pm] = "khong_truy_cap"
        else:
            ra[pm] = "chua_co"
    return ra


# ── mạng (tiêm được trong test) ─────────────────────────────────────────────────────────────────────────────────────────
def _lay_json(url: str, lan: int = 3) -> dict:
    """GET JSON với User-Agent TRUNG THỰC + thử lại lùi dần (5xx/429/mạng); 4xx khác thì báo ngay. Nghỉ 0,35 s trước mỗi lời gọi."""
    import urllib.error  # noqa: PLC0415
    import urllib.request  # noqa: PLC0415
    loi: Exception | None = None
    for i in range(lan):
        time.sleep(0.35)
        try:
            rq = urllib.request.Request(url, headers={"User-Agent": "EBM-Copilot/1.0 (doc_toan_van_co_nguoi; bac si ca nhan)"})
            with urllib.request.urlopen(rq, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code != 429:   # 429 = bị giới hạn tốc độ ⇒ thử lại như lỗi tạm
                raise
            loi = e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            loi = e
        time.sleep(1.5 * (i + 1))
    raise loi if loi else RuntimeError("không lấy được")


def tra_epmc(pmid: str = "", doi: str = "") -> dict:
    """Europe PMC (công khai): pmcid, isOpenAccess, doi, fullTextUrlList — KHÔNG đọc trang nhà xuất bản."""
    q = f"EXT_ID:{pmid} AND SRC:MED" if pmid else f'DOI:"{doi}"'
    d = _lay_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search?resultType=core&format=json&pageSize=1&query="
                  + quote(q))
    kq = (d.get("resultList") or {}).get("result") or []
    return kq[0] if kq else {}


def tra_doi_dich(doi: str) -> str:
    """URL đích của DOI qua API handle của doi.org — không tải trang nhà xuất bản."""
    d = _lay_json("https://doi.org/api/handles/" + quote(doi, safe="/"))
    for v in d.get("values") or []:
        if v.get("type") == "URL":
            return (v.get("data") or {}).get("value", "")
    return ""


def duong_doc(pm: str, trang_thai: str, epmc: Callable[..., dict] = tra_epmc,
              doi_dich: Callable[[str], str] = tra_doi_dich, *, hom_nay: date | None = None,
              tep_uy_quyen: Path | None = None) -> dict:
    """Đường đọc của MỘT bài chưa có toàn văn: OA chưa gom / trình duyệt (URL + miền đã đo) / chưa rõ (lỗi mạng ≠ «không có»).

    NXB «cam» ⇒ «bác sĩ đọc trực tiếp», TRỪ KHI bác sĩ có uỷ quyền máy đọc còn hiệu lực cho đúng NXB đó ⇒ làn trình duyệt có người,
    gắn nhãn «BÁC SĨ UỶ QUYỀN MÁY ĐỌC (<ngày>)» (điều khoản NXB không đổi — quyết định của bác sĩ)."""
    if trang_thai != "chua_co":
        return {"pmid": pm, "cach": trang_thai}
    try:
        r = epmc(pmid=pm)
    except Exception as e:  # noqa: BLE001 — lỗi mạng phải hiện ra, không đọc thành «không có toàn văn»
        return {"pmid": pm, "cach": "chua_ro", "ly_do": f"Europe PMC lỗi {type(e).__name__}"}
    doi = (r.get("doi") or "").lower()
    tieu_de = r.get("title") or ""
    if r.get("pmcid") and r.get("isOpenAccess") == "Y":
        return {"pmid": pm, "doi": doi, "tieu_de": tieu_de, "cach": "oa_chua_gom", "pmcid": r["pmcid"],
                "ly_do": "có bản OA — chạy gom_toan_van_dashboard.py, không cần trình duyệt"}
    urls = ((r.get("fullTextUrlList") or {}).get("fullTextUrl")) or []
    mien_phi = [u for u in urls if u.get("availabilityCode") in ("F", "OA") and u.get("url")]
    url = mien_phi[0]["url"] if mien_phi else ""
    if not url and doi:
        try:
            url = doi_dich(doi)
        except Exception as e:  # noqa: BLE001
            return {"pmid": pm, "doi": doi, "tieu_de": tieu_de, "cach": "chua_ro", "ly_do": f"doi.org lỗi {type(e).__name__}"}
    if not url:
        return {"pmid": pm, "doi": doi, "tieu_de": tieu_de, "cach": "chua_ro", "ly_do": "không có DOI/URL toàn văn trong Europe PMC"}
    ten_nxb, dk = nxb_cua(doi, url, tieu_de)
    if dk and dk["ket_luan"] == "cam":
        uq = uy_quyen_bac_si(ten_nxb, hom_nay, tep_uy_quyen)
        if not uq:
            return {"pmid": pm, "doi": doi, "tieu_de": tieu_de, "cach": "bac_si_doc_truc_tiep", "url": url, "nxb": ten_nxb,
                    "ly_do": f"điều khoản {ten_nxb} cấm xử lý nội dung bằng AI/TDM — bác sĩ đọc trực tiếp; đường hợp lệ: {dk['duong_hop_le']}"}
        return {"pmid": pm, "doi": doi, "tieu_de": tieu_de, "cach": "trinh_duyet", "url": url, "mien": _mien(url),
                "mien_do_duoc": phan_loai_mien(url), "mien_phi": bool(mien_phi), "dieu_khoan": KET_LUAN_UY_QUYEN,
                "nxb": ten_nxb, "ngay_uy_quyen": uq["ngay"], "nhan_dieu_khoan": f"BÁC SĨ UỶ QUYỀN MÁY ĐỌC ({uq['ngay']})"}
    return {"pmid": pm, "doi": doi, "tieu_de": tieu_de, "cach": "trinh_duyet", "url": url, "mien": _mien(url),
            "mien_do_duoc": phan_loai_mien(url), "mien_phi": bool(mien_phi),
            "dieu_khoan": "da_kiem" if dk else "chua_kiem"}


def lap_phieu(pmids: list[str], *, ngoai_tuyen: bool, kho: Path | None = None, hom_nay: date | None = None,
              epmc: Callable[..., dict] = tra_epmc, doi_dich: Callable[[str], str] = tra_doi_dich,
              tep_uy_quyen: Path | None = None) -> list[dict]:
    bp = bao_phu_cuc_bo(pmids, kho, hom_nay)
    if ngoai_tuyen:
        return [{"pmid": pm, "cach": t} for pm, t in bp.items()]
    return [duong_doc(pm, t, epmc, doi_dich, hom_nay=hom_nay, tep_uy_quyen=tep_uy_quyen) for pm, t in bp.items()]


def in_phieu(phieu: list[dict]) -> None:
    da = [p for p in phieu if p["cach"] in TRANG_THAI_MAY_CO_TOAN_VAN]
    bs = [p for p in phieu if p["cach"] == "bac_si_da_doc_truc_tiep"]
    # Trung thực: bài bác sĩ đọc trực tiếp được tính ĐÃ PHỦ nhưng máy KHÔNG có toàn văn — đếm tách riêng, không cộng vào «máy có».
    print(f"Đã có toàn văn: {len(da)}/{len(phieu)} bài máy có toàn văn"
          + (f" + {len(bs)} bài bác sĩ đọc trực tiếp (máy KHÔNG có toàn văn các bài này)" if bs else "") + ".")
    if bs:
        print("\nBÁC SĨ ĐÃ ĐỌC TRỰC TIẾP (kết luận của bác sĩ ở toan_van_oa/trinh_duyet/bac-si-da-doc.jsonl): "
              + " · ".join(p["pmid"] for p in bs))
    doc_truc_tiep = [p for p in phieu if p["cach"] == "bac_si_doc_truc_tiep"]
    if doc_truc_tiep:
        print("\nBÁC SĨ ĐỌC TRỰC TIẾP — điều khoản NXB cấm xử lý nội dung bằng AI/TDM (Claude KHÔNG mở bài):")
        for ten in sorted({p.get("nxb", "?") for p in doc_truc_tiep}):
            dk = DIEU_KHOAN_NXB.get(ten, {})
            print(f"  ▸ {ten} — đường hợp lệ: {dk.get('duong_hop_le', '?')}")
            for p in (x for x in doc_truc_tiep if x.get("nxb", "?") == ten):
                print(f"      PMID {p['pmid']} · {p.get('tieu_de', '')[:80]}\n        {p.get('url', '')}")
    for nhan, cach in (("BÀI OA CHƯA GOM — chạy gom_toan_van_dashboard.py", "oa_chua_gom"),
                       ("CHƯA RÕ (lỗi mạng/thiếu định danh — KHÔNG phải «không có toàn văn»)", "chua_ro"),
                       ("ĐÃ BÁO KHÔNG CÓ QUYỀN ĐỌC (≤ 90 ngày)", "khong_truy_cap"),
                       ("CHƯA CÓ (chế độ ngoại tuyến — chạy lại có mạng để biết đường đọc)", "chua_co")):
        nhom = [p for p in phieu if p["cach"] == cach]
        if nhom:
            print(f"\n{nhan}: " + " · ".join(p["pmid"] + (f" ({p['ly_do']})" if p.get("ly_do") else "") for p in nhom))
    can = [p for p in phieu if p["cach"] == "trinh_duyet"]
    if can:
        print("\nCẦN TRÌNH DUYỆT CÓ BÁC SĨ (vượt chặn/đăng nhập MỘT lần mỗi miền):")
        for mien in sorted({p["mien"] for p in can}):
            nhom = [p for p in can if p["mien"] == mien]
            print(f"  ▸ {mien} — {nhom[0]['mien_do_duoc']}")
            for p in nhom:
                print(f"      PMID {p['pmid']}{' (miễn phí)' if p['mien_phi'] else ''} · {p['tieu_de'][:80]}\n        {p['url']}")
                if p.get("dieu_khoan") == "chua_kiem":
                    print("        ⚠ điều khoản NXB về AI/TDM CHƯA KIỂM — Claude đọc trang điều khoản trước (--huong-dan bước 2b)")
                elif p.get("dieu_khoan") == KET_LUAN_UY_QUYEN:
                    print(f"        ⚖ {p.get('nhan_dieu_khoan', 'BÁC SĨ UỶ QUYỀN MÁY ĐỌC')} — điều khoản {p.get('nxb', '?')} KHÔNG đổi; "
                          "quyết định và trách nhiệm điều khoản của bác sĩ. Chỉ qua Chrome của bác sĩ; hồ sơ khai `dieu_khoan` "
                          f"{{ket_luan: {KET_LUAN_UY_QUYEN}, ngay_uy_quyen: {p.get('ngay_uy_quyen', '?')}}}")
        print("\nQuy trình: python3 tools/doc_toan_van_co_nguoi.py --huong-dan")
    print("Cần bác sĩ kiểm chứng.")


# ── kiểm hồ sơ ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def _so(x) -> float | None:
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _duyet_chuoi(x, duong: str = ""):
    if isinstance(x, str):
        yield duong, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from _duyet_chuoi(v, f"{duong}.{k}" if duong else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _duyet_chuoi(v, f"{duong}[{i}]")


def _duyet_khoa(x):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k
            yield from _duyet_khoa(v)
    elif isinstance(x, list):
        for v in x:
            yield from _duyet_khoa(v)


def kiem_ho_so(hs: dict, hom_nay: date | None = None, kiem_tieu_de: Callable[[str], str | None] | None = None,
               tep_uy_quyen: Path | None = None) -> tuple[list[str], list[str], dict]:
    """(lỗi chặn, cảnh báo, thông tin) — CHỈ cấu trúc/nội dung, chưa gọi mạng. Lỗi ⇒ không ghi.

    NXB «cam»: CHỈ nhận khi (a) bác sĩ có uỷ quyền máy đọc còn hiệu lực cho ĐÚNG NXB đó (`uy_quyen_bac_si`, tệp `tep_uy_quyen`,
    mặc định EBM-Dashboards/dieu-khoan-bac-si-uy-quyen.json) VÀ (b) hồ sơ khai `dieu_khoan.ket_luan == "bac_si_uy_quyen"` kèm
    `dieu_khoan.ngay_uy_quyen` đúng ngày của mục uỷ quyền. Thiếu một ⇒ từ chối. Mọi kiểm khác không đổi."""
    hom_nay = hom_nay or date.today()
    loi: list[str] = []
    cb: list[str] = []
    uy_quyen: dict | None = None
    if not isinstance(hs, dict):
        return ["hồ sơ không phải đối tượng JSON"], [], {}
    pm, doi = str(hs.get("pmid") or "").strip(), str(hs.get("doi") or "").strip().lower()
    if pm and not re.fullmatch(r"\d{6,9}", pm):
        loi.append(f"pmid «{pm}» sai dạng")
    if doi and not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
        loi.append(f"doi «{doi}» sai dạng")
    if not pm and not doi:
        loi.append("thiếu cả pmid lẫn doi — không truy nguyên được")
    if len((hs.get("tieu_de_bai") or "").strip()) < 15:
        loi.append("thiếu tieu_de_bai (để đối chiếu đúng bài)")
    url = hs.get("url_doc") or ""
    if not re.match(r"https?://", url):
        loi.append("url_doc phải là http(s)")
    elif any(_mien(url).endswith(m) for m in MIEN_TONG_HOP):
        loi.append("url_doc là bản TỔNG HỢP có bản quyền (DynaMed/UpToDate…) — chỉ dùng để tìm nghiên cứu gốc, không phải toàn văn")
    ten_nxb, dk = nxb_cua(doi, url, " ".join(str(hs.get(k) or "") for k in ("tieu_de_bai", "tieu_de_trang")))
    if dk and dk["ket_luan"] == "cam":
        kd = hs.get("dieu_khoan") if isinstance(hs.get("dieu_khoan"), dict) else {}
        uq = uy_quyen_bac_si(ten_nxb, hom_nay, tep_uy_quyen)
        if uq and kd.get("ket_luan") == KET_LUAN_UY_QUYEN and str(kd.get("ngay_uy_quyen") or "") == uq["ngay"]:
            uy_quyen = {"nxb": ten_nxb, "ngay": uq["ngay"], "can_cu": uq.get("can_cu", ""), "pham_vi": uq.get("pham_vi", ""),
                        "het_han": uq.get("het_han") or ""}
        elif uq:
            loi.append(f"điều khoản {ten_nxb} cấm dùng nội dung với công cụ AI/TDM trừ khi có giấy phép/thuê bao/sự cho phép — bác sĩ "
                       f"ĐÃ uỷ quyền máy đọc ngày {uq['ngay']} nhưng hồ sơ phải khai `dieu_khoan` {{ket_luan: {KET_LUAN_UY_QUYEN}, "
                       f"ngay_uy_quyen: {uq['ngay']}}} (đúng ngày trong {TEN_TEP_UY_QUYEN}) — KHÔNG nạp")
        else:
            loi.append(f"điều khoản {ten_nxb} cấm dùng nội dung với công cụ AI/TDM (đọc {dk['doc_luc']}: {dk['nguon']}) — KHÔNG nạp; "
                       f"bác sĩ đọc trực tiếp, đường hợp lệ: {dk['duong_hop_le']}")
            if kd.get("ket_luan") == KET_LUAN_UY_QUYEN:
                loi.append(f"hồ sơ khai `{KET_LUAN_UY_QUYEN}` nhưng KHÔNG có uỷ quyền còn hiệu lực của bác sĩ cho {ten_nxb} trong "
                           f"EBM-Dashboards/{TEN_TEP_UY_QUYEN} — agent KHÔNG tự ghi uỷ quyền khi bác sĩ chưa nói rõ trong chat")
    elif not dk:
        kd = hs.get("dieu_khoan") if isinstance(hs.get("dieu_khoan"), dict) else {}
        if kd.get("ket_luan") not in _KET_LUAN_DIEU_KHOAN_NHAN or not re.match(r"https?://", str(kd.get("url") or "")) \
                or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(kd.get("doc_luc") or "")):
            loi.append("nhà xuất bản CHƯA KIỂM điều khoản về AI/TDM — đọc trang điều khoản trước rồi khai `dieu_khoan` "
                       "{url, doc_luc, ket_luan: cho_phep | giay_phep_cc, trich ≤ 15 từ}; cấm hoặc không rõ ⇒ dừng, bác sĩ đọc trực tiếp")
    td = (hs.get("tieu_de_trang") or "").strip()
    ly = (kiem_tieu_de(td) if kiem_tieu_de else None) or (
        None if len(td) >= 10 and not _TIEU_DE_CAM_DU_PHONG.search(td) else f"tiêu đề trang «{td[:60]}» là trang chặn/lỗi/quá ngắn")
    if ly:
        loi.append(ly)
    if _TIEU_DE_DANG_NHAP.search(td):
        loi.append(f"tiêu đề trang «{td[:60]}» là trang ĐĂNG NHẬP/MUA BÀI — toàn văn chưa hiện")
    try:
        dl = date.fromisoformat(str(hs.get("doc_luc") or "")[:10])
        if dl > hom_nay:
            loi.append("doc_luc ở tương lai")
        elif (hom_nay - dl).days > HAN_DOC_LUC_NGAY:
            loi.append(f"doc_luc cũ hơn {HAN_DOC_LUC_NGAY} ngày — đọc lại trang rồi nạp")
    except ValueError:
        loi.append("doc_luc phải là ngày ISO (YYYY-MM-DD)")
    if hs.get("nguon_truy_cap") not in _NGUON_TRUY_CAP:
        loi.append(f"nguon_truy_cap phải thuộc {sorted(_NGUON_TRUY_CAP)}")
    if hs.get("gap_chan") and hs.get("nguoi_vuot_chan") != "bac_si":
        loi.append("gap_chan=true thì nguoi_vuot_chan phải là «bac_si» — Claude KHÔNG tự vượt kiểm tra chống bot")
    if not re.fullmatch(r"[0-9a-f]{64}", str(hs.get("sha256_toan_van") or "")):
        loi.append("sha256_toan_van phải là 64 ký tự hex (tính trong trình duyệt)")
    n = _so(hs.get("so_ky_tu_toan_van"))
    if n is None or n < TOI_THIEU_KY_TU:
        loi.append(f"so_ky_tu_toan_van < {TOI_THIEU_KY_TU} — gần như chắc chỉ là trang đích/tóm tắt, chưa phải toàn văn")
    loai = hs.get("loai_tai_lieu")
    if loai not in _LOAI:
        loi.append(f"loai_tai_lieu phải thuộc {sorted(_LOAI)}")
    # Bản quyền: không chép nguyên văn dài, không có khoá chứa toàn văn.
    cam = sorted({k for k in _duyet_khoa(hs) if str(k).casefold() in _KHOA_CAM})
    if cam:
        loi.append(f"hồ sơ có khoá chứa toàn văn {cam} — chỉ ghi trích xuất có cấu trúc")
    for duong, s in _duyet_chuoi(hs):
        if len(s) > TRAN_CHUOI:
            loi.append(f"{duong} dài {len(s)} ký tự (> {TRAN_CHUOI}) — nghi chép nguyên văn; viết lại bằng lời của Claude")
        if any(p.search(s) for p in _PII) and duong not in ("url_doc", "doi", "pmid", "sha256_toan_van", "doc_luc"):
            loi.append(f"{duong} có chuỗi giống thông tin định danh (email/điện thoại/số 12 chữ) — KHÔNG PII")
    trich = [x for x in (hs.get("ket_qua") or []) if isinstance(x, dict) and (x.get("trich_ngan") or "").strip()]
    if len(trich) > TRAN_SO_TRICH:
        loi.append(f"{len(trich)} lần trích nguyên văn (> {TRAN_SO_TRICH})")
    for i, x in enumerate(trich):
        if len(x["trich_ngan"].split()) > TRAN_TU_TRICH:
            loi.append(f"ket_qua[{i}].trich_ngan > {TRAN_TU_TRICH} từ")
    # Con số.
    kq = hs.get("ket_qua") or []
    if not isinstance(kq, list):
        loi.append("ket_qua phải là danh sách")
        kq = []
    for i, x in enumerate(kq):
        if not isinstance(x, dict):
            loi.append(f"ket_qua[{i}] không phải đối tượng")
            continue
        if not (x.get("ket_cuc") or "").strip():
            loi.append(f"ket_qua[{i}] thiếu ket_cuc")
        if not (x.get("vi_tri") or "").strip():
            loi.append(f"ket_qua[{i}] thiếu vi_tri (Bảng/Hình/đoạn) — bác sĩ không đối chiếu được")
        cs = str(x.get("chi_so") or "").strip().upper()
        g, lo, hi = _so(x.get("gia_tri")), _so(x.get("ci_duoi")), _so(x.get("ci_tren"))
        if not cs or g is None:
            loi.append(f"ket_qua[{i}] thiếu chi_so hoặc gia_tri (số)")
            continue
        if (lo is None) != (hi is None):
            loi.append(f"ket_qua[{i}] CI thiếu một đầu")
        if lo is not None and hi is not None and not lo <= g <= hi:
            loi.append(f"ket_qua[{i}] gia_tri {g} nằm ngoài CI [{lo}; {hi}] — chép sai số?")
        if cs in _TY_SO and (g <= 0 or (lo is not None and lo <= 0)):
            loi.append(f"ket_qua[{i}] tỷ số {cs} phải > 0")
        p = x.get("p")
        if p not in (None, ""):
            ps = _so(p)
            if ps is not None:
                if not 0 <= ps <= 1:
                    loi.append(f"ket_qua[{i}] p={ps} ngoài [0;1]")
            elif not re.fullmatch(r"\s*[<>≤≥=]?\s*0?[.,]\d+\s*", str(p)):
                loi.append(f"ket_qua[{i}] p «{p}» sai dạng")
    kc = hs.get("khuyen_cao") or []
    for i, x in enumerate(kc if isinstance(kc, list) else []):
        if not isinstance(x, dict) or not (x.get("tom_tat") or "").strip() or not (x.get("muc") or "").strip() \
                or not (x.get("vi_tri") or "").strip():
            loi.append(f"khuyen_cao[{i}] cần đủ tom_tat · muc (mức/lớp khuyến cáo NGUYÊN BẢN) · vi_tri")
        elif len(x["tom_tat"]) > TRAN_TOM_TAT_KC:
            loi.append(f"khuyen_cao[{i}].tom_tat > {TRAN_TOM_TAT_KC} ký tự")
    # Độ đầy đủ (không chặn — quyết định trần đề xuất).
    pp = hs.get("phuong_phap") if isinstance(hs.get("phuong_phap"), dict) else {}
    thieu = [k for k in _MUC_DU.get(loai, _MUC_DU_MAC_DINH) if not (pp.get(k) or "").strip()]
    if loai == "guideline":
        if not kc:
            thieu.append("khuyen_cao")
    elif not kq:
        thieu.append("ket_qua")
    for k in ("han_che", "tai_tro_coi"):
        if not (hs.get(k) or "").strip():
            thieu.append(k)
    if thieu:
        cb.append(f"thiếu {', '.join(thieu)} ⇒ độ đầy đủ «partial» (thẻ giữ trần «Cân nhắc»)")
    if td and do_giong(td, hs.get("tieu_de_bai") or "") < 0.2:
        cb.append("tiêu đề trang ít trùng tiêu đề bài — kiểm lại đã mở đúng bài chưa")
    tt = {"do_day_du": "partial" if thieu else "full", "thieu_muc": thieu}
    if uy_quyen:
        tt["uy_quyen"] = uy_quyen
    return loi, cb, tt


def xac_minh_dinh_danh(hs: dict, xac_minh: Callable[[dict], dict]) -> tuple[str | None, dict]:
    """Định danh phải XÁC MINH ĐƯỢC qua cơ quan đăng ký và khớp tiêu đề; bài đã rút ⇒ chặn. Trả (lỗi hoặc None, kết quả)."""
    b = {"_nguon": "doc_toan_van_co_nguoi", "title": hs.get("tieu_de_bai") or "", "tac_gia": "", "journal": "",
         "year": None, "doi": (hs.get("doi") or "").lower(), "pmid": str(hs.get("pmid") or ""), "loai": ""}
    kq = xac_minh(b)
    if kq.get("ket_qua") == "bi_rut_bai":
        return "🔴 bài ĐÃ BỊ RÚT theo cơ quan đăng ký — không nạp; báo bác sĩ (alerts/)", kq
    if kq.get("ket_qua") != "xac_minh_duoc":
        return f"định danh không xác minh được ({kq.get('ket_qua')}: {kq.get('ly_do', '')}) — không nạp", kq
    tieu_de_dk = kq.get("title") or ""
    if tieu_de_dk and do_giong(tieu_de_dk, b["title"]) < 0.5:
        return f"tieu_de_bai lệch tiêu đề cơ quan đăng ký («{tieu_de_dk[:70]}») — nhầm bài?", kq
    return None, kq


def _ten_tep(hs: dict) -> str:
    pm = str(hs.get("pmid") or "").strip()
    return f"PMID-{pm}" if pm else "DOI-" + re.sub(r"[^0-9a-z]+", "_", (hs.get("doi") or "").lower()).strip("_")


def ban_doc_md(hs: dict, kiem: dict) -> str:
    pp = hs.get("phuong_phap") or {}
    nhan = {"thiet_ke": "Thiết kế", "quan_the": "Quần thể", "can_thiep_so_sanh": "Can thiệp / so sánh", "ket_cuc_chinh": "Kết cục chính",
            "ngau_nhien_lam_mu": "Ngẫu nhiên hoá / làm mù", "dang_ky": "Mã đăng ký", "nguy_co_sai_lech": "Nguy cơ sai lệch",
            "di_bien": "Dị biệt (heterogeneity)"}
    d = [f"# Đọc sâu toàn văn — {_ten_tep(hs).replace('-', ' ', 1)}"]
    uq = kiem.get("uy_quyen") or {}
    if uq:
        # Hồ sơ của NXB «cam» chỉ tới được đây qua uỷ quyền của bác sĩ ⇒ dòng ĐẦU của thân bản đọc nói rõ căn cứ (không viết như NXB cho phép).
        d.append("\n> " + DONG_QUYET_DINH.format(ngay=uq["ngay"], nxb=uq["nxb"]))
    d += [f"\n> Đọc qua TRÌNH DUYỆT CÓ BÁC SĨ ngày {hs['doc_luc']} (bài KHÔNG có bản OA; trang «{hs['tieu_de_trang'][:90]}»). "
          "Trích xuất CÓ CẤU TRÚC do phiên Claude ghi — KHÔNG nguyên văn (bản quyền nhà xuất bản); mỗi con số kèm vị trí trong bài "
          f"để đối chiếu. SHA-256 văn bản trang (tính trong trình duyệt): `{hs['sha256_toan_van'][:16]}…` · "
          f"{int(hs['so_ky_tu_toan_van'])} ký tự. Độ đầy đủ: **{kiem['do_day_du']}**"
          + (f" (thiếu: {', '.join(kiem['thieu_muc'])})" if kiem["thieu_muc"] else "") + ". **Cần bác sĩ kiểm chứng.**\n",
          f"**{hs['tieu_de_bai']}**" + (f" · doi:{hs['doi']}" if hs.get("doi") else "") + f"  \nNguồn đọc: {hs['url_doc']}"]
    co_pp = [(nhan.get(k, k), v) for k, v in pp.items() if (v or "").strip()]
    if co_pp:
        d.append("\n## Phương pháp (lời Claude, không nguyên văn)\n")
        d += [f"- **{k}:** {v}" for k, v in co_pp]
    if hs.get("ket_qua"):
        d.append("\n## Hiệu số — chép đúng như bài báo cáo\n")
        for x in hs["ket_qua"]:
            ci = f" (95% CI {x['ci_duoi']}–{x['ci_tren']})" if _so(x.get("ci_duoi")) is not None else ""
            p = f", p {x['p']}" if x.get("p") not in (None, "") else ""
            tr = f" — «{x['trich_ngan']}»" if (x.get("trich_ngan") or "").strip() else ""
            d.append(f"- {x['ket_cuc']}{' · ' + x['nhom'] if x.get('nhom') else ''}: {x['chi_so']} {x['gia_tri']}{ci}{p} "
                     f"[{x['vi_tri']}]{tr}")
    if hs.get("khuyen_cao"):
        d.append("\n## Khuyến cáo — mức/lớp NGUYÊN BẢN của nguồn\n")
        d += [f"- {x['tom_tat']} — **{x['muc']}** [{x['vi_tri']}]" for x in hs["khuyen_cao"]]
    for k, t in (("han_che", "Hạn chế"), ("tai_tro_coi", "Tài trợ & xung đột lợi ích"), ("ghi_chu", "Ghi chú")):
        if (hs.get(k) or "").strip():
            d.append(f"\n## {t}\n\n{hs[k]}")
    d.append("\n---\n*Bản trích phục vụ thẩm định — quyết định lâm sàng qua Cổng A của bác sĩ. Toàn văn KHÔNG tự nâng đề xuất. "
             "Không PII.*\n")
    return "\n".join(d)


def _tuong_doi(tep: Path) -> str:
    try:
        return str(tep.relative_to(REPO))
    except ValueError:
        return str(tep)


def _ghi_nguyen_tu(tep: Path, noi_dung: str) -> None:
    tep.parent.mkdir(parents=True, exist_ok=True)
    tam = tep.with_name(tep.name + f".tam-{os.getpid()}")
    tam.write_text(noi_dung, encoding="utf-8", newline="\n")
    os.replace(tam, tep)


def nap(hs: dict, *, ghi: bool, xac_minh: Callable[[dict], dict] | None, kho: Path | None = None,
        hom_nay: date | None = None, kiem_tieu_de: Callable[[str], str | None] | None = None,
        tep_uy_quyen: Path | None = None) -> tuple[int, list[str]]:
    """Kiểm → xác minh → (nếu --ghi) ghi JSON + bản đọc. Trả (mã thoát, dòng báo)."""
    kho, hom_nay = kho or KHO, hom_nay or date.today()
    loi, cb, kiem = kiem_ho_so(hs, hom_nay, kiem_tieu_de, tep_uy_quyen)
    bao = [f"✗ {x}" for x in loi] + [f"🟡 {x}" for x in cb]
    if not loi and kiem.get("uy_quyen"):
        uq = kiem["uy_quyen"]
        bao.append(f"⚖ {uq['nxb']}: nạp theo QUYẾT ĐỊNH của bác sĩ ngày {uq['ngay']} — điều khoản NXB không đổi; trách nhiệm điều "
                   "khoản thuộc bác sĩ")
    pm = str(hs.get("pmid") or "").strip() if isinstance(hs, dict) else ""
    if pm and (list(kho.glob(f"PMID-{pm}_*.xml")) or list(kho.glob(f"PMID-{pm}_UPW.*"))):
        loi.append("đã có toàn văn OA trong kho — dùng doc_sau_toan_van.py, không cần làn trình duyệt")
        bao.append(f"✗ {loi[-1]}")
    elif pm and list(kho.glob(f"PMID-{pm}_WTDM.*")):
        loi.append("đã có toàn văn qua kênh TDM của NXB (PMID-<n>_WTDM.pdf) — đọc tệp đó, không mở bài bằng trình duyệt")
        bao.append(f"✗ {loi[-1]}")
    if loi:
        return 3, bao + ["TỪ CHỐI — chưa ghi gì."]
    if xac_minh is None:
        bao.append("⚪ chưa xác minh định danh (engine vắng) — chạy thử dừng ở đây" + (", KHÔNG ghi" if ghi else ""))
        return (2 if ghi else 0), bao
    try:
        ly, kq = xac_minh_dinh_danh(hs, xac_minh)
    except Exception as e:  # noqa: BLE001 — không xác minh được ≠ đạt
        bao.append(f"⚪ xác minh lỗi {type(e).__name__} — KHÔNG ghi")
        return 2, bao
    if ly:
        return 3, bao + [f"✗ {ly}", "TỪ CHỐI — chưa ghi gì."]
    kiem = {**kiem, "ngay_nap": hom_nay.isoformat(), "cong_cu": "tools/doc_toan_van_co_nguoi.py",
            "xac_minh": {"ket_qua": kq.get("ket_qua"), "ly_do": kq.get("ly_do", ""), "pmid": kq.get("pmid", ""),
                         "doi": kq.get("doi", "")}}
    bao.append(f"✓ đạt kiểm · xác minh {kq.get('ket_qua')} · độ đầy đủ {kiem['do_day_du']}")
    if not ghi:
        return 0, bao + ["(chạy thử — thêm --ghi để ghi vào kho)"]
    ban = {**hs, "pmid": pm, "doi": (hs.get("doi") or kq.get("doi") or "").lower(), "kiem": kiem, "trang_thai": "CANDIDATE",
           "can_bac_si_kiem_chung": True}
    ten = _ten_tep(ban)
    tep = kho / "trinh_duyet" / f"{ten}.json"
    if tep.exists():
        cu = tep.with_name(f"{ten}.{datetime.now():%Y%m%d-%H%M%S}.json.cu")
        os.replace(tep, cu)
        bao.append(f"  (bản cũ giữ ở {cu.name})")
    _ghi_nguyen_tu(tep, json.dumps(ban, ensure_ascii=False, indent=2) + "\n")
    md = (kho / "doc_sau" / f"{ten}.md") if pm else (kho / "trinh_duyet" / f"{ten}.md")
    _ghi_nguyen_tu(md, ban_doc_md(ban, kiem))
    bao.append(f"✓ đã ghi {_tuong_doi(tep)}")
    bao.append(f"✓ bản đọc {md.name} — gói tuần bước 4b đọc như bản OA")
    return 0, bao


def danh_dau_khong_truy_cap(pm: str, ly_do: str, kho: Path | None = None, hom_nay: date | None = None) -> None:
    kho, hom_nay = kho or KHO, hom_nay or date.today()
    tep = kho / "trinh_duyet" / "khong-truy-cap.jsonl"
    tep.parent.mkdir(parents=True, exist_ok=True)
    with open(tep, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"pmid": pm, "ngay": hom_nay.isoformat(), "ly_do": ly_do}, ensure_ascii=False) + "\n")


def kiem_ghi_chu_bac_si(ghi_chu: str | None) -> list[str]:
    """Lỗi chặn của ghi chú «bác sĩ đã đọc trực tiếp» (rỗng = đạt). Ghi KẾT LUẬN của bác sĩ, không chép nội dung bài."""
    s = (ghi_chu or "").strip()
    loi = []
    if len(s) < GHI_CHU_BAC_SI_MIN:
        loi.append(f"--ghi-chu bắt buộc, ≥ {GHI_CHU_BAC_SI_MIN} ký tự — kết luận bằng lời của bác sĩ")
    elif len(s) > GHI_CHU_BAC_SI_MAX:
        loi.append(f"--ghi-chu dài {len(s)} ký tự (> {GHI_CHU_BAC_SI_MAX}) — chỉ ghi KẾT LUẬN của bác sĩ, KHÔNG chép nội dung bài")
    if any(p.search(s) for p in _PII):
        loi.append("--ghi-chu có chuỗi giống thông tin định danh (email/điện thoại/số 12 chữ) — KHÔNG PII")
    return loi


def danh_dau_bac_si_da_doc(pm: str, ghi_chu: str | None, *, ghi: bool, kho: Path | None = None,
                           hom_nay: date | None = None) -> tuple[int, list[str]]:
    """Ghi nối «bác sĩ đã đọc trực tiếp» vào `trinh_duyet/bac-si-da-doc.jsonl`. Mặc định chạy thử; `ghi=True` mới ghi.

    Mã: 0 đạt (đã ghi / chạy thử) · 2 kho vắng (KHÔNG ĐO ĐƯỢC, không tự tạo kho) · 3 từ chối. Bản ghi KHÔNG hết hạn."""
    kho, hom_nay = kho or KHO, hom_nay or date.today()
    pm = str(pm or "").strip()
    loi = ([] if re.fullmatch(r"\d{6,9}", pm) else [f"PMID «{pm}» sai dạng (6–9 chữ số)"]) + kiem_ghi_chu_bac_si(ghi_chu)
    if loi:
        return 3, [f"✗ {x}" for x in loi] + ["TỪ CHỐI — chưa ghi gì."]
    ban = {"pmid": pm, "ngay": hom_nay.isoformat(), "ghi_chu": (ghi_chu or "").strip(), "nguon": "bac_si_doc_truc_tiep"}
    bao = [f"✓ PMID {pm}: ghi chú đạt kiểm ({len(ban['ghi_chu'])} ký tự) — thẻ sẽ thành «BÁC SĨ ĐÃ ĐỌC TRỰC TIẾP» "
           "(máy vẫn KHÔNG có toàn văn; không hết hạn)"]
    if not ghi:
        return 0, bao + ["(chạy thử — thêm --ghi để ghi vào kho)"]
    if not kho.is_dir():
        return 2, bao + [f"⚪ KHÔNG ĐO ĐƯỢC — không thấy kho {kho} (EBM-Dashboards/ vắng ở cây này) — KHÔNG ghi"]
    tep = kho / "trinh_duyet" / "bac-si-da-doc.jsonl"
    tep.parent.mkdir(parents=True, exist_ok=True)
    with open(tep, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ban, ensure_ascii=False) + "\n")
    return 0, bao + [f"✓ đã ghi {_tuong_doi(tep)}"]


def ghi_uy_quyen(nxb: str, can_cu: str | None, *, pham_vi: str | None = None, het_han: str | None = None, ghi: bool = False,
                 tep: Path | None = None, hom_nay: date | None = None) -> tuple[int, list[str]]:
    """Ghi QUYẾT ĐỊNH của bác sĩ cho máy đọc toàn văn bài của một NXB «cam» (mặc định chạy thử; `ghi=True` mới ghi).

    `can_cu` = NGUYÊN VĂN lời bác sĩ trong chat (≥ 10 ký tự, không PII). Chỉ nhận khoá «cam» của DIEU_KHOAN_NXB. Mã: 0 đạt (đã ghi /
    chạy thử) · 2 thư mục EBM-Dashboards vắng (không tự tạo) · 3 từ chối (kể cả tệp quyết định có mà hỏng — KHÔNG ghi đè)."""
    hom_nay = hom_nay or date.today()
    tep = Path(tep) if tep else tep_uy_quyen_mac_dinh()
    cam = [k for k, v in DIEU_KHOAN_NXB.items() if v.get("ket_luan") == "cam"]
    loi: list[str] = []
    dk = DIEU_KHOAN_NXB.get(nxb or "")
    if not dk or dk.get("ket_luan") != "cam":
        loi.append(f"NXB «{nxb}» không phải khoá «cấm» của DIEU_KHOAN_NXB — chỉ nhận đúng một trong: " + " · ".join(f"«{k}»" for k in cam))
    cc = (can_cu or "").strip()
    if len(cc) < CAN_CU_UY_QUYEN_MIN:
        loi.append(f"--can-cu bắt buộc, ≥ {CAN_CU_UY_QUYEN_MIN} ký tự — NGUYÊN VĂN lời bác sĩ trong chat (agent không tự soạn)")
    elif any(p.search(cc) for p in _PII):
        loi.append("--can-cu có chuỗi giống thông tin định danh (email/điện thoại/số 12 chữ) — KHÔNG PII")
    hh = None
    if het_han not in (None, ""):
        hh = _ngay_iso(het_han)
        if hh is None or hh < hom_nay:
            loi.append(f"--het-han «{het_han}» phải là ngày ISO (YYYY-MM-DD) từ hôm nay trở đi")
    if loi:
        return 3, [f"✗ {x}" for x in loi] + ["TỪ CHỐI — chưa ghi gì."]
    muc = {"nxb": nxb, "ngay": hom_nay.isoformat(), "can_cu": cc,
           "pham_vi": (pham_vi or "").strip() or (f"Claude đọc toàn văn bài {nxb} mà bác sĩ có quyền truy cập, chỉ qua Chrome của bác "
                                                  "sĩ, để tóm tắt và lập hồ sơ trích xuất có cấu trúc (trích ≤ 15 từ, không lưu toàn văn)")}
    if hh:
        muc["het_han"] = hh.isoformat()
    muc["dieu_khoan_nxb_khong_doi"] = {"nguon": dk.get("nguon", ""), "doc_luc": dk.get("doc_luc", ""), "trich": dk.get("trich", "")}
    muc["ghi_boi"] = "tools/doc_toan_van_co_nguoi.py --ghi-uy-quyen"
    bao = [f"⚖ Đây là quyết định của bác sĩ — trách nhiệm điều khoản thuộc bác sĩ. Điều khoản {nxb} KHÔNG đổi "
           f"(«{dk.get('trich', '')}» — {dk.get('nguon', '')}); đây KHÔNG phải «NXB cho phép».",
           "  mục sẽ ghi: " + json.dumps(muc, ensure_ascii=False)]
    if not ghi:
        return 0, bao + [f"(chạy thử — thêm --ghi để ghi vào {_tuong_doi(tep)})"]
    if not tep.parent.is_dir():
        return 2, bao + [f"⚪ KHÔNG ĐO ĐƯỢC — không thấy thư mục {tep.parent} — KHÔNG ghi (không tự tạo thư mục)"]
    if tep.exists():
        try:
            d = json.loads(tep.read_text(encoding="utf-8"))
            if not isinstance(d, dict) or not isinstance(d.get("muc"), list):
                raise ValueError("sai cấu trúc (cần {\"muc\": [...]})")
        except (OSError, ValueError) as e:
            return 3, bao + [f"✗ tệp quyết định {tep.name} có mà KHÔNG đọc được ({type(e).__name__}) — KHÔNG ghi đè; bác sĩ xem lại tệp"]
    else:
        d = {"_about": _ABOUT_UY_QUYEN, "muc": []}
    d["muc"].append(muc)
    _ghi_nguyen_tu(tep, json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    return 0, bao + [f"✓ đã ghi {_tuong_doi(tep)} — phiếu xếp bài {nxb} vào làn trình duyệt có người, nhãn "
                     f"«BÁC SĨ UỶ QUYỀN MÁY ĐỌC ({muc['ngay']})»"]


def _kiem_tieu_de_cua_cong():
    try:
        return _nap_mo_dun("_dtv_xntd", "xac_nhan_trinh_duyet.py").kiem_tieu_de
    except Exception:  # noqa: BLE001 — vắng thì dùng mẫu dự phòng trong kiem_ho_so
        return None


def _xac_minh_engine():
    try:
        return _nap_mo_dun("_dtv_tctk", "tra_cuu_co_tai_khoan.py").tao_xac_minh_engine()
    except Exception:  # noqa: BLE001 — engine vắng ⇒ None (chạy thử được, --ghi bị từ chối mã 2)
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đọc toàn văn bài KHÔNG mở qua trình duyệt có bác sĩ (phiếu · quy trình · nạp hồ sơ)")
    ap.add_argument("--queue", nargs="*", default=[], help="gói tuần queue/tuan-*.md — lấy PMID trên thẻ")
    ap.add_argument("--pmid", nargs="*", default=[])
    ap.add_argument("--ngoai-tuyen", action="store_true", help="chỉ soi kho cục bộ, không gọi Europe PMC/doi.org")
    ap.add_argument("--huong-dan", action="store_true")
    ap.add_argument("--mau", action="store_true")
    ap.add_argument("--nap", type=Path, help="hồ sơ trích xuất JSON do phiên Claude soạn")
    ap.add_argument("--ghi", action="store_true",
                    help="cùng --nap / --bac-si-da-doc / --ghi-uy-quyen: ghi thật (mặc định chạy thử)")
    ap.add_argument("--khong-truy-cap", metavar="PMID")
    ap.add_argument("--ly-do", default="")
    ap.add_argument("--bac-si-da-doc", metavar="PMID",
                    help="NXB cấm AI/TDM: bác sĩ đã tự đọc bài — ghi kết luận (cần --ghi-chu; mặc định chạy thử)")
    ap.add_argument("--ghi-chu", default=None,
                    help=f"kết luận bằng lời bác sĩ, {GHI_CHU_BAC_SI_MIN}–{GHI_CHU_BAC_SI_MAX} ký tự, không PII, KHÔNG chép nội dung bài")
    ap.add_argument("--ghi-uy-quyen", metavar="NXB",
                    help="ghi QUYẾT ĐỊNH của bác sĩ cho máy đọc bài của một NXB «cấm» (đúng khoá DIEU_KHOAN_NXB; cần --can-cu; "
                         "mặc định chạy thử) — trách nhiệm điều khoản thuộc bác sĩ")
    ap.add_argument("--can-cu", default=None, help=f"NGUYÊN VĂN lời bác sĩ trong chat (≥ {CAN_CU_UY_QUYEN_MIN} ký tự)")
    ap.add_argument("--pham-vi", default=None, help="phạm vi uỷ quyền (mặc định: đọc qua Chrome của bác sĩ, chỉ hồ sơ tóm lược)")
    ap.add_argument("--het-han", default=None, help="ngày hết hạn uỷ quyền YYYY-MM-DD (tuỳ chọn)")
    a = ap.parse_args(argv)
    if a.huong_dan:
        print(HUONG_DAN)
        return 0
    if a.mau:
        print(json.dumps(MAU, ensure_ascii=False, indent=2))
        return 0
    if a.khong_truy_cap:
        if not re.fullmatch(r"\d{6,9}", a.khong_truy_cap) or not a.ly_do.strip():
            print("✗ cần PMID đúng dạng và --ly-do (vd «tạp chí đòi mua bài, bác sĩ không có quyền»)")
            return 3
        danh_dau_khong_truy_cap(a.khong_truy_cap, a.ly_do.strip())
        print(f"✓ PMID {a.khong_truy_cap}: ghi «không có quyền đọc» — không nhắc lại {HAN_KHONG_TRUY_CAP_NGAY} ngày.")
        return 0
    if a.bac_si_da_doc is not None:
        ma, bao = danh_dau_bac_si_da_doc(a.bac_si_da_doc, a.ghi_chu, ghi=a.ghi)
        print("\n".join(bao))
        print("Cần bác sĩ kiểm chứng.")
        return ma
    if a.ghi_uy_quyen is not None:
        ma, bao = ghi_uy_quyen(a.ghi_uy_quyen, a.can_cu, pham_vi=a.pham_vi, het_han=a.het_han, ghi=a.ghi)
        print("\n".join(bao))
        return ma
    if a.nap:
        try:
            hs = json.loads(a.nap.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"✗ không đọc được hồ sơ: {type(e).__name__}: {e}")
            return 3
        if not KHO.is_dir():
            print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy kho {KHO} (EBM-Dashboards/ vắng ở cây này)")
            return 2
        ma, bao = nap(hs, ghi=a.ghi, xac_minh=_xac_minh_engine(), kiem_tieu_de=_kiem_tieu_de_cua_cong())
        print("\n".join(bao))
        print("Cần bác sĩ kiểm chứng.")
        return ma
    pmids = list(a.pmid)
    for q in a.queue:
        p = Path(q)
        if not p.exists():
            print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy {q}")
            return 2
        pmids += pmid_cua_queue(p)
    pmids = list(dict.fromkeys(pmids))
    if not pmids:
        print("✗ không có PMID đầu vào (--queue hoặc --pmid). Quy trình: --huong-dan")
        return 2
    if not KHO.is_dir():
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy kho {KHO}")
        return 2
    phieu = lap_phieu(pmids, ngoai_tuyen=a.ngoai_tuyen)
    in_phieu(phieu)
    if not a.ngoai_tuyen:
        _ghi_nguyen_tu(PHIEU_DIR / f"phieu-{date.today():%Y%m%d}.json",
                       json.dumps({"ngay": date.today().isoformat(), "nguon": a.queue or a.pmid, "phieu": phieu},
                                  ensure_ascii=False, indent=2) + "\n")
    return 1 if any(p["cach"] in ("trinh_duyet", "oa_chua_gom", "chua_ro", "chua_co", "bac_si_doc_truc_tiep") for p in phieu) else 0


if __name__ == "__main__":
    raise SystemExit(main())
