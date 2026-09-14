#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test NGOẠI TUYẾN cho chế độ dò/bật trạm của giam_sat_to_chuc (29/08/2026).

Vì sao có: trạm hội «dựng xong nằm chờ» từ 15/08 vì không ai xác minh sống được
URL; hai chế độ --kiem-tra/--bat-neu-ok là đường kích hoạt một-lệnh trên máy
thật. Test này khoá hợp đồng của chúng bằng fixture — không gọi mạng."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gstc_test_mod", ROOT / "tools" / "giam_sat_to_chuc.py")
assert SPEC and SPEC.loader
G = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = G
SPEC.loader.exec_module(G)

HTML_CO_TIEU_DE = "<html><h2>GOLD Report 2026 — Global Strategy</h2><a href=/x>Pocket Guide 2026</a></html>"
HTML_KHONG_TIEU_DE = "<html><p>chỉ văn xuôi giới thiệu hội, không mục lục</p></html>"


def _nguon(sid: str, status: str = "not-covered", url: str | None = "https://vi.du/x") -> dict:
    return {"id": sid, "org": "X", "domain": ["d"], "access": "html-watch",
            "endpoint_or_url": url, "status": status}


def test_kiem_tra_phan_biet_ba_ket_cuc(monkeypatch) -> None:
    """fetch hỏng ✗ · fetch OK nhưng 0 tiêu đề ✗ (kèm lý do) · có tiêu đề ✓."""
    noi_dung = {"https://vi.du/hong": None,
                "https://vi.du/rong": HTML_KHONG_TIEU_DE,
                "https://vi.du/tot": HTML_CO_TIEU_DE}
    monkeypatch.setattr(G, "_fetch", lambda url: noi_dung[url])
    kq = G.kiem_tra_tram([_nguon("A", url="https://vi.du/hong"),
                          _nguon("B", url="https://vi.du/rong"),
                          _nguon("C", url="https://vi.du/tot")])
    assert kq["A"]["ok"] is False and "fetch hỏng" in kq["A"]["ly_do"]
    assert kq["B"]["ok"] is False and "0 tiêu đề" in kq["B"]["ly_do"]
    assert kq["C"]["ok"] is True and kq["C"]["so_tieu_de"] >= 1


def test_kiem_tra_bo_qua_nguon_khong_phai_tram(monkeypatch) -> None:
    """Nguồn access=api/manual hoặc thiếu endpoint KHÔNG được dò — tránh gọi mạng thừa."""
    monkeypatch.setattr(G, "_fetch", lambda url: HTML_CO_TIEU_DE)
    kq = G.kiem_tra_tram([
        {"id": "API", "access": "api", "endpoint_or_url": "https://vi.du", "status": "active"},
        _nguon("THIEU-URL", url=None),
        _nguon("TRAM"),
    ])
    assert set(kq) == {"TRAM"}


def test_bat_neu_ok_chi_bat_tram_dat_va_dang_not_covered() -> None:
    """Chỉ trạm dò ĐẠT + đang not-covered mới bật; trạm active sẵn và trạm dò
    trượt giữ nguyên — bật trạm trượt là ghi «active» suông, đúng thứ sổ cấm."""
    du = {"sources": [_nguon("DAT"), _nguon("TRUOT"),
                       _nguon("DA-BAT", status="active")]}
    kq = {"DAT": {"ok": True, "so_tieu_de": 3, "ly_do": None},
          "TRUOT": {"ok": False, "so_tieu_de": 0, "ly_do": "fetch hỏng"},
          "DA-BAT": {"ok": True, "so_tieu_de": 2, "ly_do": None}}
    bat = G.bat_neu_ok(du, kq)
    assert bat == ["DAT"]
    trang_thai = {s["id"]: s["status"] for s in du["sources"]}
    assert trang_thai == {"DAT": "active", "TRUOT": "not-covered", "DA-BAT": "active"}
    dat = next(s for s in du["sources"] if s["id"] == "DAT")
    assert dat["kich_hoat"]["so_tieu_de_luc_do"] == 3
    assert "DA-BAT" not in [s["id"] for s in du["sources"] if "kich_hoat" in s]


def test_bat_neu_ok_khong_ghi_dia() -> None:
    """bat_neu_ok là hàm THUẦN sửa dict — caller sao lưu rồi mới ghi; hàm tự ghi
    đĩa sẽ vòng qua bước sao lưu."""
    import inspect
    nguon = inspect.getsource(G.bat_neu_ok)
    assert "write_text" not in nguon and "open(" not in nguon


# ---------------------------------------------------------------------------
# --nap-van-ban (09/09/2026) — SRC-015 ACC/AHA bị Cloudflare bot-challenge
# chặn urllib nhưng Browser thật tải được; luồng này nạp nội dung ĐÃ TẢI SẴN
# (văn bản thuần, không HTML) và chạy CÙNG logic so-sánh/ghi-state với luồng
# quét chính, chỉ khác nguồn nội dung.
# ---------------------------------------------------------------------------

VAN_BAN_CO_TIEU_DE = (
    "Trang chủ Guidelines and Statements\n"
    "\n"
    "2026 Guideline for the Prevention of Stroke in Patients With Stroke\n"
    "\n"
    "Fifth Universal Definition of Myocardial Infarction (2026)\n"
    "\n"
    "giới thiệu hội, không phải tiêu đề — quá ngắn hoặc không có năm/từ khoá\n"
)


def test_rut_tieu_de_tu_van_ban_loc_dung_va_khop_loc_html() -> None:
    """Bộ lọc văn bản thuần phải nhận đúng 3 dòng hợp lệ (kể cả dòng tiêu đề
    trang «Guidelines and Statements» — CHỨA đúng 2 từ khoá luật cho phép,
    khớp thực tế đã đo trên trang ACC/AHA thật 09/09/2026), loại dòng tiếng
    Việt không có năm/từ khoá — VÀ cho kết quả giống hệt khi đưa CÙNG 3 dòng
    đó qua rut_tieu_de(html) (chứng minh hai đường dùng chung một tiêu chí)."""
    ba_dong = {
        "Trang chủ Guidelines and Statements",
        "2026 Guideline for the Prevention of Stroke in Patients With Stroke",
        "Fifth Universal Definition of Myocardial Infarction (2026)",
    }
    tu_van_ban = G.rut_tieu_de_tu_van_ban(VAN_BAN_CO_TIEU_DE)
    assert tu_van_ban == ba_dong
    tu_html = G.rut_tieu_de("".join(f"<h2>{d}</h2>" for d in ba_dong))
    assert tu_van_ban == tu_html


# Trang thật ACC/AHA 09/09/2026 (rút gọn) — lần chạy đầu KHÔNG lọc rác cho
# 20/20 dòng "qua", 17 là rác. Fixture này tái hiện ĐÚNG ca đó để khoá bản vá.
VAN_BAN_TRANG_THAT_LAN_ACC_AHA = """Title: Guidelines and Statements - Professional Heart Daily | American Heart Association
URL: https://professional.heart.org
Source element: <main>
---
Home Guidelines and Statements
Guidelines & Statements
About Guidelines & Statements

Heart Disease and Stroke Statistics — 2026 Update
2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack
A Guideline From the American Heart Association/American Stroke Association
Guidelines Pocketcards
FEATURED NEWS
Sep 08, 2026 | Circulation
ESC 2026 Science News
Aug 31, 2026
Fifth Universal Definition of Myocardial Infarction (2026)
Aug 28, 2026 | Circulation
Search Guidelines and Statements

Tab Context:
- Executed on tabId: seed
- Available tabs:
  • tabId seed: "Guidelines and Statements" (https://professional.heart.org)
"""


def test_rut_tieu_de_tu_van_ban_loc_rac_trang_that_09_09() -> None:
    """Ca thật đo được khi vá: dòng khung get_page_text (Title:/URL:/---/Tab
    Context:/tabId…) và dòng <4 từ (ngày-tháng đơn độc, breadcrumb, nhãn nút)
    phải bị loại — chỉ còn tiêu đề guideline/statement thật."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_LAN_ACC_AHA)
    assert ket == {
        "Heart Disease and Stroke Statistics — 2026 Update",
        "2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack",
        "A Guideline From the American Heart Association/American Stroke Association",
        "Fifth Universal Definition of Myocardial Infarction (2026)",
    }
    # Rác đã bị loại — khẳng định TƯỜNG MINH, không chỉ suy từ độ dài tập kết quả.
    rac = {"Home Guidelines and Statements", "Guidelines & Statements",
           "About Guidelines & Statements", "Guidelines Pocketcards",
           "Sep 08, 2026 | Circulation", "ESC 2026 Science News",
           "Aug 31, 2026", "Aug 28, 2026 | Circulation",
           "Search Guidelines and Statements"}
    assert not (ket & rac)


# Trang thật USPSTF 13/09/2026 (rút gọn, lấy qua Browser tool thật — get_page_text
# tại https://www.uspreventiveservicestaskforce.org/uspstf/recommendation-topics).
# Khác ACC/AHA: mỗi tiêu đề khuyến cáo và ngày cập nhật nằm TRÊN HAI DÒNG RIÊNG,
# ngày không có số ngày (chỉ "Mon YYYY") — cả hai dòng đều KHÔNG đủ điều kiện một
# mình, phải ghép mới ra tiêu đề hợp lệ.
VAN_BAN_TRANG_THAT_USPSTF = (
    "Latest Final Recommendations\n"
    "Intimate Partner Violence and Caregiver Abuse of Older or Vulnerable Adults: Screening\n"
    "Jun 2025\n"
    "Syphilis Infection During Pregnancy: Screening\n"
    "May 2025\n"
    "Breastfeeding: Primary Care Behavioral Counseling Interventions\n"
    "Apr 2025\n"
)


def test_rut_tieu_de_tu_van_ban_ghep_tieu_de_va_ngay_rieng_dong_uspstf() -> None:
    """Vá 13/09/2026: tiêu đề + "Mon YYYY" trên hai dòng liền kề phải được GHÉP
    thành một tiêu đề hợp lệ (mang năm nên qua RE_TIEU_DE); dòng tiêu đề trang
    "Latest Final Recommendations" (3 từ, không năm/từ khoá) phải bị loại."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_USPSTF)
    assert ket == {
        "Intimate Partner Violence and Caregiver Abuse of Older or Vulnerable Adults: Screening Jun 2025",
        "Syphilis Infection During Pregnancy: Screening May 2025",
        "Breastfeeding: Primary Care Behavioral Counseling Interventions Apr 2025",
    }
    assert "Latest Final Recommendations" not in ket


def test_rut_tieu_de_tu_van_ban_khong_ghep_khi_khong_can_uspstf() -> None:
    """Đối kháng bản vá: nếu gỡ bước ghép (mô phỏng bằng cách tự cắt văn bản
    thành các dòng đã ghép sẵn thủ công) thì kết quả PHẢI giống hệt — chứng
    minh _loc_tieu_de_hop_le không tự "sửa hộ" thiếu sót của bước tách dòng."""
    da_ghep_tay = (
        "Intimate Partner Violence and Caregiver Abuse of Older or Vulnerable Adults: Screening Jun 2025\n"
        "Syphilis Infection During Pregnancy: Screening May 2025\n"
        "Breastfeeding: Primary Care Behavioral Counseling Interventions Apr 2025\n"
    )
    assert G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_USPSTF) == G.rut_tieu_de_tu_van_ban(da_ghep_tay)


# Trang thật KDIGO 13/09/2026 (rút gọn, lấy qua Browser tool thật — get_page_text
# tại https://kdigo.org/guidelines/ SAU KHI cuộn xuống — khối 18 chủ đề chỉ render
# lười biếng, không có trong lượt chụp đầu tiên trước khi cuộn). 18 tên bệnh VIẾT
# HOA không năm/từ khoá; boilerplate đứng cạnh (nút CTA cuối trang) cũng ALL-CAPS
# ≥2 từ nhưng chỉ thành chuỗi liên tiếp ngắn (3), khác khối chủ đề (18).
VAN_BAN_TRANG_THAT_KDIGO = """Title: Guidelines – KDIGO
URL: https://kdigo.org
Source element: <body>
---
ABOUT
GUIDELINES
CONTROVERSIES CONFERENCES
EVENTS
RESOURCES
NEWS
SEARCH
 Guidelines

KDIGO guidelines focus on topics related to the prevention or management of individuals with kidney diseases.

Criteria used by KDIGO for topic prioritization include the burden of illness based on prevalence and scope of the condition or clinical problem; amenability of a particular condition to prevention or treatment and expected impact; existence of a body of evidence of sufficient breadth and depth to enable the development of evidence-based guidelines; potential of guidelines to reduce variations in practices, improve health outcomes, or lower treatment costs.

 KDIGO Guidelines KDIGO guidelines are created, reviewed, published following a rigorous scientific process.
ACUTE KIDNEY INJURY (AKI) AND ACUTE KIDNEY DISEASE (AKD)
ANEMIA IN CKD
ANTINEUTROPHILIC CYTOPLASMIC ANTIBODY (ANCA)-ASSOCIATED VASCULITIS
AUTOSOMAL DOMINANT POLYCYSTIC KIDNEY DISEASE (ADPKD)
BLOOD PRESSURE IN CKD
CKD EVALUATION AND MANAGEMENT
CKD-MINERAL AND BONE DISORDER (CKD-MBD)
DIABETES AND CKD
GLOMERULAR DISEASES (GD)
HEART FAILURE IN CKD
HEPATITIS C IN CKD
IGA NEPHROPATHY (IGAN) / IGA VASCULITIS (IGAV)
LIPIDS IN CKD
LIVING KIDNEY DONOR
LUPUS NEPHRITIS (LN)
NEPHROTIC SYNDROME IN CHILDREN
TRANSPLANT CANDIDATE
TRANSPLANT RECIPIENT

Interested in providing feedback on KDIGO guidelines before publication?

Sign up for our newsletter!

 JOIN THE KDIGO MAILING LIST

SIGN UP

IMPROVING GLOBAL OUTCOMES

ABOUT
GUIDELINES
CONTROVERSIES CONFERENCES
EVENTS
RESOURCES
NEWS
CONTACT

TWITTER

FACEBOOK

INSTAGRAM

LINKEDIN
© 2016 KDIGO

Tab Context:
- Executed on tabId: tab-1
- Available tabs:
  • tabId tab-1: "Guidelines – KDIGO" (https://kdigo.org)
"""

_18_TIEU_DE_KDIGO_THAT = {
    "ACUTE KIDNEY INJURY (AKI) AND ACUTE KIDNEY DISEASE (AKD)",
    "ANEMIA IN CKD",
    "ANTINEUTROPHILIC CYTOPLASMIC ANTIBODY (ANCA)-ASSOCIATED VASCULITIS",
    "AUTOSOMAL DOMINANT POLYCYSTIC KIDNEY DISEASE (ADPKD)",
    "BLOOD PRESSURE IN CKD",
    "CKD EVALUATION AND MANAGEMENT",
    "CKD-MINERAL AND BONE DISORDER (CKD-MBD)",
    "DIABETES AND CKD",
    "GLOMERULAR DISEASES (GD)",
    "HEART FAILURE IN CKD",
    "HEPATITIS C IN CKD",
    "IGA NEPHROPATHY (IGAN) / IGA VASCULITIS (IGAV)",
    "LIPIDS IN CKD",
    "LIVING KIDNEY DONOR",
    "LUPUS NEPHRITIS (LN)",
    "NEPHROTIC SYNDROME IN CHILDREN",
    "TRANSPLANT CANDIDATE",
    "TRANSPLANT RECIPIENT",
}


def test_rut_tieu_de_tu_van_ban_nhan_khoi_toan_hoa_kdigo() -> None:
    """Vá 13/09/2026: 18 tên chủ đề guideline VIẾT HOA (không năm/từ khoá) phải
    được nhận diện đủ qua ngưỡng chuỗi liên tiếp — kể cả 2 tên chỉ 2 từ
    ("TRANSPLANT CANDIDATE"/"TRANSPLANT RECIPIENT", dưới sàn ≥5 từ của luật
    khác trong cùng hàm) và các tên chứa dấu gạch ngang/ngoặc/dấu gạch chéo."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_KDIGO)
    assert _18_TIEU_DE_KDIGO_THAT <= ket


def test_rut_tieu_de_tu_van_ban_khong_nhan_cta_toan_hoa_ngan_kdigo() -> None:
    """CTA cuối trang ("JOIN THE KDIGO MAILING LIST"/"SIGN UP"/
    "IMPROVING GLOBAL OUTCOMES") cũng ALL-CAPS ≥2 từ nhưng chỉ thành chuỗi
    liên tiếp NGẮN (3, dưới ngưỡng 4) — không được lẫn vào tiêu đề thật."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_KDIGO)
    rac = {"JOIN THE KDIGO MAILING LIST", "SIGN UP", "IMPROVING GLOBAL OUTCOMES",
           "CONTROVERSIES CONFERENCES"}
    assert not (ket & rac)


def test_la_toan_hoa_nhieu_tu_phan_biet_van_xuoi_va_nut_don_tu() -> None:
    """Đơn vị: dòng có chữ thường (văn xuôi) hoặc chỉ 1 từ (nút điều hướng)
    không được coi là ứng viên khối ALL-CAPS."""
    assert G._la_toan_hoa_nhieu_tu("ANEMIA IN CKD") is True
    assert G._la_toan_hoa_nhieu_tu("TRANSPLANT CANDIDATE") is True
    assert G._la_toan_hoa_nhieu_tu("Anemia in CKD") is False
    assert G._la_toan_hoa_nhieu_tu("EVENTS") is False
    assert G._la_toan_hoa_nhieu_tu("123") is False


# Trích đoạn thật trang IDSA A-Z List 13/09/2026 (get_page_text qua Browser
# tool — trang này KHÔNG cần cuộn, tải đủ ngay). Giữ nguyên cấu trúc thật: mục
# lục chữ cái đơn (A/B/C), NHIỀU nhãn trạng thái xếp chồng trước một tiêu đề
# ("Archived\nIn Development\n<tên>"), và các tiêu đề NGẮN 2-4 từ + năm cuối
# dòng — đúng ca bị sàn ≥5 từ cũ loại oan.
VAN_BAN_TRANG_THAT_IDSA = """Title: All Practice Guidelines: A-Z List
URL: https://idsociety.org
Source element: <body>
---
IDSA clinical practice guidelines are developed by a panel of experts who perform a systematic review of the available evidence and use the GRADE process to develop evidence-based recommendations to assist practitioners and patients in making decisions about appropriate health care for specific clinical circumstances.

A
Current
Acute Bacterial Arthritis in Pediatrics 2023
Current
AMR Guidance 2026
Archived
In Development
Antimicrobial Prophylaxis in Surgery 2013
Current
In Development
Aspergillosis 2016
B
Current
Babesiosis 2020
Archived
Bacterial Meningitis 2004
Archived
Blastomycosis 2008
M
Archived
MRSA 2011
V
Current
Vancomycin 2020

©2026 Infectious Diseases Society of America
"""

_TIEU_DE_NGAN_IDSA_CAN_TRICH = {
    "AMR Guidance 2026",
    "Antimicrobial Prophylaxis in Surgery 2013",
    "Aspergillosis 2016",
    "Babesiosis 2020",
    "Bacterial Meningitis 2004",
    "Blastomycosis 2008",
    "Vancomycin 2020",
}


def test_rut_tieu_de_tu_van_ban_nhan_tieu_de_ngan_ket_thuc_bang_nam_idsa() -> None:
    """Vá 13/09/2026: tiêu đề NGẮN (2-4 từ) + năm ở CUỐI DÒNG phải được nhận,
    dù dưới sàn ≥5 từ cũ — đo sống trên trang IDSA thật: sàn cũ làm rớt 47/114
    tiêu đề thật (41%), toàn bộ đều thuộc dạng này."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_IDSA)
    assert _TIEU_DE_NGAN_IDSA_CAN_TRICH <= ket


def test_rut_tieu_de_tu_van_ban_khong_nhan_muc_luc_va_trang_thai_idsa() -> None:
    """Chữ cái mục lục đơn (A/B/M/V) và nhãn trạng thái (Current/Archived/
    In Development) — kể cả khi XẾP CHỒNG nhiều nhãn liên tiếp trước một tiêu
    đề — không được lẫn vào kết quả."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_IDSA)
    rac = {"A", "B", "M", "V", "Current", "Archived", "In Development"}
    assert not (ket & rac)


def test_rut_tieu_de_tu_van_ban_van_loai_tieu_de_ket_thuc_bang_nam_giua_dong_idsa() -> None:
    """Đối chứng: nới sàn ≥5 từ CHỈ áp cho dòng KẾT THÚC bằng năm — dòng chứa
    năm ở GIỮA (không phải cuối, kiểu «ESC 2026 Science News» của ACC/AHA) vẫn
    phải rớt như cũ, không được nới oan."""
    assert G.rut_tieu_de_tu_van_ban("ESC 2026 Science News") == set()


# Trích đoạn thật trang WHO Guidelines 13/09/2026 (get_page_text qua Browser
# tool, khối "Latest WHO guidelines approved…") — mỗi tiêu đề có một dòng ngày
# kiểu "DD Month YYYY" (tên tháng ĐẦY ĐỦ, ngày đứng TRƯỚC) đứng ngay trước nó.
# Đây là HỒI QUY do chính bản vá IDSA (mục (5) ở trên) gây ra: 6 dòng ngày này
# đều 3 từ + kết thúc bằng năm nên bị luật OR-kết-thúc-bằng-năm nhận nhầm.
VAN_BAN_TRANG_THAT_WHO = """Title: WHO Guidelines
URL: https://who.int
Source element: <section>
---
Latest WHO guidelines approved by the Guidelines Review Committee
All →
10 September 2026
WHO guidelines for malaria
Download Read More
22 July 2026
Consolidated HIV guidelines: service delivery
Download Read More
18 December 2025
WHO guidelines on the management of advanced HIV disease
Download Read More
3 November 2025
Selected practice recommendations for contraceptive use, 4th ed.
Download Read More
"""

_NGAY_RAC_WHO = {"10 September 2026", "22 July 2026", "18 December 2025", "3 November 2025"}


def test_rut_tieu_de_tu_van_ban_loai_ngay_kieu_who_ngay_truoc_thang() -> None:
    """Vá 13/09/2026 (hồi quy tự gây ra khi vá IDSA): dòng ngày «DD Month
    YYYY» tên tháng đầy đủ (WHO) không được nhận nhầm thành tiêu đề, dù 3 từ
    và kết thúc bằng năm — đúng dạng lẽ ra bị luật OR bắt nhầm."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_WHO)
    assert not (ket & _NGAY_RAC_WHO)
    assert "Consolidated HIV guidelines: service delivery" in ket
    assert "WHO guidelines on the management of advanced HIV disease" in ket
    assert "Selected practice recommendations for contraceptive use, 4th ed." in ket


# Trích đoạn thật trang GINA Reports 13/09/2026 — dòng ngày kiểu "Month DD,
# YYYY" tên tháng đầy đủ (khác WHO: có dấu phẩy, tháng đứng TRƯỚC ngày).
VAN_BAN_TRANG_THAT_GINA = """Title: Reports - Global Initiative for Asthma - GINA
URL: https://ginasthma.org
Source element: <div>
---
News
GINA 2026 SUMMARY GUIDE – NOW AVAILABLE!

July 21, 2026

    The 2026 update of the Summary Guide for Asthma Management and Prevention is now available for FREE. Click HERE[...]

GINA 2026 Severe Asthma Guide – Now Available!

June 23, 2026

    The 2026 update of the Difficult-to-Treat & Severe Asthma in adolescent and adult patients: Diagnosis and Management Guide,[...]
"""

_NGAY_RAC_GINA = {"July 21, 2026", "June 23, 2026"}


def test_rut_tieu_de_tu_van_ban_loai_ngay_thang_day_du_thang_truoc_ngay_gina() -> None:
    """Vá 13/09/2026 (cùng hồi quy, dạng thứ hai): dòng ngày «Month DD, YYYY»
    tên tháng đầy đủ có dấu phẩy (GINA) cũng không được nhận nhầm."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_GINA)
    assert not (ket & _NGAY_RAC_GINA)


# Trích đoạn thật trang gov.uk/drug-safety-update (SRC-016 MHRA) 14/09/2026 —
# mỗi cảnh báo an toàn thuốc in ĐÚNG 3 dòng liên tiếp: tiêu đề, mô tả, rồi
# «Therapeutic area: … Published: DD Month YYYY» — xác nhận 14/14 cảnh báo
# thật trên trang, không ngoại lệ.
VAN_BAN_TRANG_THAT_MHRA = """Title: Drug Safety Update - GOV.UK
URL: https://gov.uk
Source element: <main>
---
Drug Safety Update
From:
Medicines and Healthcare products Regulatory Agency
Alerts, recalls and safety information: medicines and medical devices
Search
Drug Safety Update
Search
Filter
 results
Skip to results
867 updates
Skip to results
Filters should be used during the administration of Parenteral Nutrition for patients in all care settings

Administration of parenteral nutrition without a filter has been associated with a number of adverse incidents including an embolism which resulted in a fatal outcome.

Therapeutic area: Anaesthesia and intensive care and 12 others Published: 2 September 2026
Domperidone: new contraindication in patients with phaeochromocytoma due to the risk of severe hypertension

The product information has been updated for all domperidone products, to include a contraindication for patients with confirmed or suspected phaeochromocytoma (a rare tumour of the adrenal gland), due to the risk of episode...

Therapeutic area: Cardiovascular disease and lipidology and 6 others Published: 21 July 2026
Botulinum toxin type A products: updated warnings regarding risk of iatrogenic botulism

Cases of iatrogenic botulism have been reported following the therapeutic or cosmetic use of botulinum toxin containing products where the toxin's effect extends beyond the area of treatment. Patients should seek immediate m...

Therapeutic area: Cosmetic surgery and 4 others Published: 15 July 2026
ACE-inhibitors: Be aware of the distinction between bradykinin- and histamine-mediated angioedema, as treatment strategies differ significantly

Healthcare professionals should be aware of the potential for delayed onset of angioedema and the distinction between bradykinin- and histamine-mediated cases, as treatment strategies differ significantly and bradykinin-medi...

Therapeutic area: Cardiovascular disease and lipidology and 4 others Published: 16 June 2026
Amiodarone: reminder of risks of treatment and need for patient monitoring and supervision

Amiodarone has been associated with serious and potentially life-threatening side effects, particularly of the lung, liver, and thyroid gland. We remind healthcare professionals that patients should be supervised and reviewe...

Therapeutic area: Cardiovascular disease and lipidology and 1 others Published: 15 March 2022
Finasteride and Dutasteride - updated safety warnings for psychiatric side effects and sexual dysfunction

The MHRA has reviewed the evidence for finasteride and dutasteride and the risk of suicidal thoughts and behaviours and has recommended further measures to minimise this risk.

Therapeutic area: Dermatology and 7 others Published: 11 May 2026
Nasal decongestant sprays and drops containing xylometazoline hydrochloride / oxymetazoline hydrochloride: increased risk of rebound congestion, rhinitis medicamentosa, and tachyphylaxis with overuse

There have been reports of worsening nasal congestion (rebound congestion) when the effects of nasal decongestant sprays or drops containing xylometazoline hydrochloride and oxymetazoline hydrochloride, wear off.

Therapeutic area: Dispensing GP practices and 5 others Published: 30 April 2026
Falsified Mounjaro KwikPen 15mg pre-filled pens

A falsified version of Mounjaro (tirzepatide) KwikPen 15mg solution for injection has been found supplied through one online pharmacy in the UK. The falsified product is labelled with batch D873576 and applies to Mounjaro Kw...

Therapeutic area: Dispensing GP practices and 5 others Published: 24 February 2026
IXCHIQ Chikungunya vaccine: temporary suspension in people aged 65 years or older

The Commission on Human Medicines (CHM) has temporarily restricted use of the IXCHIQ Chikungunya vaccine in people aged 65 years and over following very rare fatal reactions reported globally. This is a precautionary measure...

Therapeutic area: Immunology and vaccination and 2 others Published: 18 June 2025
IXCHIQ Chikungunya vaccine: updates to restrictions of use following safety review

Following the completion of a safety review and the recommendations of the Commission on Human Medicines (CHM), the IXCHIQ Chikungunya vaccine is no longer indicated for adults over the age of 60 years, and is contraindicate...

Therapeutic area: Immunology and vaccination and 2 others Published: 11 February 2026
Semaglutide (Wegovy, Ozempic and Rybelsus): risk of Non-arteritic Anterior Ischemic Optic Neuropathy (NAION)

Non-arteritic anterior ischemic optic neuropathy (NAION), a condition that can cause sudden deterioration in vision, usually in one eye at a time, has been very rarely reported in association with semaglutide in the treatmen...

Therapeutic area: Emergency medicine and 5 others Published: 5 February 2026
GLP-1 receptor agonists and dual GLP-1/GIP receptor agonists: strengthened warnings on acute pancreatitis, including necrotising and fatal cases

The product information for all Glucagon-Like Peptide-1 (GLP-1) receptor agonists and dual GLP-1/glucose-dependent insulinotropic polypeptide (GIP) receptor agonists has been further updated to highlight the potential risk o...

Therapeutic area: Emergency medicine and 5 others Published: 29 January 2026
Isotretinoin - changes to prescribing guidance and additional risk minimisation measures

The Commission on Human Medicines (CHM) has endorsed changes to the risk minimisation measures for isotretinoin, following a review of the impact of the measures implemented in 2023. We ask healthcare professionals to review...

Therapeutic area: Dermatology and 4 others Published: 22 January 2026
Improving Information Supplied with Gabapentinoids (Pregabalin/Gabapentin), Benzodiazepines and Z-Drugs

The MHRA has reviewed the warnings regarding addiction, dependence, withdrawal, and tolerance for gabapentin, pregabalin, benzodiazepines, and z-drugs. The findings (detailed in the Public Assessment Report) were that it wa...

Therapeutic area: General practice and 2 others Published: 8 January 2026
"""

_14_TIEU_DE_MHRA_THAT = {
    "Filters should be used during the administration of Parenteral Nutrition for patients in all care settings",
    "Domperidone: new contraindication in patients with phaeochromocytoma due to the risk of severe hypertension",
    "Botulinum toxin type A products: updated warnings regarding risk of iatrogenic botulism",
    "ACE-inhibitors: Be aware of the distinction between bradykinin- and histamine-mediated angioedema, as treatment strategies differ significantly",
    "Amiodarone: reminder of risks of treatment and need for patient monitoring and supervision",
    "Finasteride and Dutasteride - updated safety warnings for psychiatric side effects and sexual dysfunction",
    "Nasal decongestant sprays and drops containing xylometazoline hydrochloride / oxymetazoline hydrochloride: increased risk of rebound congestion, rhinitis medicamentosa, and tachyphylaxis with overuse",
    "Falsified Mounjaro KwikPen 15mg pre-filled pens",
    "IXCHIQ Chikungunya vaccine: temporary suspension in people aged 65 years or older",
    "IXCHIQ Chikungunya vaccine: updates to restrictions of use following safety review",
    "Semaglutide (Wegovy, Ozempic and Rybelsus): risk of Non-arteritic Anterior Ischemic Optic Neuropathy (NAION)",
    "GLP-1 receptor agonists and dual GLP-1/GIP receptor agonists: strengthened warnings on acute pancreatitis, including necrotising and fatal cases",
    "Isotretinoin - changes to prescribing guidance and additional risk minimisation measures",
    "Improving Information Supplied with Gabapentinoids (Pregabalin/Gabapentin), Benzodiazepines and Z-Drugs",
}

_METADATA_RAC_MHRA = {
    "Therapeutic area: Anaesthesia and intensive care and 12 others Published: 2 September 2026",
    "Therapeutic area: Cardiovascular disease and lipidology and 6 others Published: 21 July 2026",
    "Therapeutic area: Dermatology and 7 others Published: 11 May 2026",
}


def test_rut_tieu_de_tu_van_ban_nhan_du_14_tieu_de_mhra() -> None:
    """Vá 14/09/2026: 14/14 tiêu đề cảnh báo an toàn thuốc thật trên trang MHRA
    phải được nhận đủ — trước bản vá, hầu hết bị rớt vì không chứa năm/từ khoá
    (chỉ 1/14 lọt qua tình cờ nhờ chứa "updated")."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_MHRA)
    assert _14_TIEU_DE_MHRA_THAT <= ket


def test_rut_tieu_de_tu_van_ban_khong_nhan_metadata_therapeutic_area_mhra() -> None:
    """Dòng metadata «Therapeutic area: … Published: …» kết thúc bằng năm nên
    trước bản vá lọt qua RE_TIEU_DE thành "tiêu đề" giả — không được lẫn vào
    kết quả dù đứng ngay sau mỗi tiêu đề thật."""
    ket = G.rut_tieu_de_tu_van_ban(VAN_BAN_TRANG_THAT_MHRA)
    assert not (ket & _METADATA_RAC_MHRA)


def _don_dep(monkeypatch, tmp_path: Path) -> Path:
    """Trỏ 3 đường dẫn module-level (SO_NGUON/STATE/RA) vào tmp_path — không
    đụng file dự án thật khi chạy test."""
    so_nguon = tmp_path / "sources.json"
    monkeypatch.setattr(G, "SO_NGUON", so_nguon)
    monkeypatch.setattr(G, "STATE", tmp_path / "state" / "giam-sat-to-chuc.json")
    monkeypatch.setattr(G, "RA", tmp_path / "surveillance")
    return so_nguon


def test_nap_van_ban_qua_ngan_khong_ghi_gi(monkeypatch, tmp_path: Path) -> None:
    """Nội dung <200 ký tự (trang chưa tải xong/bị chặn) phải KHÔNG ghi gì —
    tránh hiểu nhầm 'chặn' thành 'không có tin mới' (họ lỗi BH08/BH27)."""
    so_nguon = _don_dep(monkeypatch, tmp_path)
    du = {"sources": [_nguon("SRC-X", status="not-covered")]}
    so_nguon.write_text(json.dumps(du), encoding="utf-8")
    ngan = tmp_path / "ngan.txt"
    ngan.write_text("quá ngắn", encoding="utf-8")
    ma = G._nap_van_ban("SRC-X", str(ngan))
    assert ma == 2
    assert json.loads(so_nguon.read_text())["sources"][0]["status"] == "not-covered"
    assert not G.STATE.exists()


def test_nap_van_ban_id_khong_ton_tai(monkeypatch, tmp_path: Path) -> None:
    so_nguon = _don_dep(monkeypatch, tmp_path)
    so_nguon.write_text(json.dumps({"sources": []}), encoding="utf-8")
    f = tmp_path / "noi_dung.txt"
    f.write_text(VAN_BAN_CO_TIEU_DE * 20, encoding="utf-8")
    assert G._nap_van_ban("KHONG-CO", str(f)) == 2


def test_nap_van_ban_bat_not_covered_va_ghi_ung_vien(monkeypatch, tmp_path: Path) -> None:
    """Đường chính: trạm not-covered, nội dung đủ dài có tiêu đề mới ⇒ tự BẬT
    active + ghi state + ghi file ứng viên đánh dấu 'nạp qua Browser thật'."""
    so_nguon = _don_dep(monkeypatch, tmp_path)
    du = {"sources": [_nguon("SRC-015", status="not-covered")]}
    du["sources"][0]["org"] = "ACC/AHA"
    so_nguon.write_text(json.dumps(du), encoding="utf-8")
    f = tmp_path / "noi_dung.txt"
    f.write_text(VAN_BAN_CO_TIEU_DE * 5, encoding="utf-8")

    ma = G._nap_van_ban("SRC-015", str(f))
    assert ma == 1

    du2 = json.loads(so_nguon.read_text())
    s2 = du2["sources"][0]
    assert s2["status"] == "active"
    assert s2["kich_hoat"]["so_tieu_de_luc_do"] == 3
    assert "Browser" in s2["kich_hoat"]["bang"]
    assert s2["last_success_at"] == G.date.today().isoformat()

    state = json.loads(G.STATE.read_text())
    assert len(state["SRC-015"]["titles"]) == 3

    file_ung_vien = list(G.RA.glob("to-chuc-*.md"))
    assert len(file_ung_vien) == 1
    noi_dung_file = file_ung_vien[0].read_text()
    assert "ACC/AHA" in noi_dung_file and "nạp qua Browser thật" in noi_dung_file


def test_ghi_ung_vien_tu_tao_thu_muc_cha_con_thieu(monkeypatch, tmp_path: Path) -> None:
    """Vá 14/09/2026: RA.mkdir() cũ dùng exist_ok=True nhưng KHÔNG parents=True
    — chỉ tạo được cấp lá, còn thư mục CHA (EBM-Dashboards/) vắng mặt thì crash
    FileNotFoundError. Bắt được thật khi kích hoạt SRC-019 trên một checkout
    git-thuần (EBM-Dashboards/ nằm ngoài git, không tồn tại): sources.json/
    state ĐÃ ghi đúng nhưng lệnh thoát mã lỗi ở bước ghi ứng viên cuối cùng.
    Test cũ (test_nap_van_ban_bat_not_covered_va_ghi_ung_vien) không bắt được
    vì trỏ RA = tmp_path/"surveillance" — cha của nó (tmp_path) LUÔN có sẵn do
    pytest tự tạo, che mất đúng tình huống lỗi thật (thư mục cha vắng mặt)."""
    monkeypatch.setattr(G, "RA", tmp_path / "EBM-Dashboards-chua-tung-tao" / "surveillance")
    f = G._ghi_ung_vien(["- test candidate"])
    assert f is not None and f.exists()


def test_nap_van_ban_nhieu_tram_cung_ngay_khong_de_ghi_de(monkeypatch, tmp_path: Path) -> None:
    """Vá 13/09/2026: gọi --nap-van-ban cho HAI trạm khác nhau trong CÙNG một
    ngày (ca thật xảy ra khi nạp lần lượt GOLD/GINA/KDIGO/ADA/ESC cùng buổi)
    trước đây làm file to-chuc-<ngày>.md bị GHI ĐÈ — chỉ trạm chạy SAU CÙNG
    còn xuất hiện, dù state/giam-sat-to-chuc.json vẫn lưu đúng cho cả hai.
    Nay file phải GIỮ ứng viên của CẢ HAI trạm."""
    so_nguon = _don_dep(monkeypatch, tmp_path)
    du = {"sources": [_nguon("SRC-A", status="not-covered"),
                      _nguon("SRC-B", status="not-covered")]}
    du["sources"][0]["org"] = "GOLD"
    du["sources"][1]["org"] = "ESC"
    so_nguon.write_text(json.dumps(du), encoding="utf-8")
    fa = tmp_path / "a.txt"
    fa.write_text(VAN_BAN_CO_TIEU_DE * 5, encoding="utf-8")
    fb = tmp_path / "b.txt"
    fb.write_text(VAN_BAN_TRANG_THAT_LAN_ACC_AHA * 5, encoding="utf-8")

    G._nap_van_ban("SRC-A", str(fa))
    G._nap_van_ban("SRC-B", str(fb))

    file_ung_vien = list(G.RA.glob("to-chuc-*.md"))
    assert len(file_ung_vien) == 1
    noi_dung_file = file_ung_vien[0].read_text()
    assert "GOLD" in noi_dung_file, "ứng viên của trạm CHẠY TRƯỚC bị mất — đúng lỗi đã vá"
    assert "ESC" in noi_dung_file


def test_nap_van_ban_da_active_khong_ghi_de_kich_hoat(monkeypatch, tmp_path: Path) -> None:
    """Trạm ĐÃ active thì lần nạp sau chỉ cập nhật state, KHÔNG được tự thêm
    khối kich_hoat mới (đó là bằng chứng của LẦN BẬT ĐẦU TIÊN, không phải mỗi
    lần quét) — cùng luật bat_neu_ok đã khoá cho DA-BAT ở test phía trên."""
    so_nguon = _don_dep(monkeypatch, tmp_path)
    du = {"sources": [_nguon("SRC-015", status="active")]}
    du["sources"][0]["org"] = "ACC/AHA"
    so_nguon.write_text(json.dumps(du), encoding="utf-8")
    f = tmp_path / "noi_dung.txt"
    f.write_text(VAN_BAN_CO_TIEU_DE * 5, encoding="utf-8")

    G._nap_van_ban("SRC-015", str(f))
    s2 = json.loads(so_nguon.read_text())["sources"][0]
    assert s2["status"] == "active"
    assert "kich_hoat" not in s2
