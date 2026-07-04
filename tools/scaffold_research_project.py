#!/usr/bin/env python3
"""Sinh khung 20-file cho MỘT đề tài nghiên cứu y khoa mới ("Medical Research OS").

Dựng cấu trúc thư mục chuẩn `Projects/<slug>/` gồm file 00–20 theo bản hợp nhất
`.claude/agents/_CROSSWALK-NGHIEN-CUU.md` (file SPEC ↔ mã A ↔ cổng ↔ agent). Mỗi file là
KHUNG RỖNG có tiêu đề, mã artifact, cổng (gọi theo TÊN), agent phụ trách và nhãn trạng thái —
để chủ nhiệm/agent ĐIỀN nội dung, KHÔNG bịa số liệu.

Triết lý "sửa template không sửa từng file": muốn đổi bố cục khung cho MỌI đề tài → sửa script
này (nguồn duy nhất), KHÔNG sửa tay từng file đã sinh.

Cách dùng:
    python3 tools/scaffold_research_project.py "Tỷ lệ kiểm soát huyết áp kém ở BN ngoại trú"
    python3 tools/scaffold_research_project.py "Tên đề tài" --slug ten-rut-gon --force

Nguyên tắc cứng: KHÔNG PII; mọi số liệu/phê duyệt để [CẦN BỔ SUNG]/[CẦN CHỦ NHIỆM ẤN ĐỊNH];
nhãn mặc định NOT VERIFIED cho mọi khẳng định chưa kiểm; kết file y khoa: "Cần bác sĩ kiểm chứng."
"""

from __future__ import annotations

import argparse
import datetime
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "Projects"
TODAY = datetime.date.today().isoformat()

DISCLAIMER = "\n---\n_Trạng thái: VERIFIED / PARTIALLY VERIFIED / NOT VERIFIED — mặc định **NOT VERIFIED** tới khi đối chiếu nguồn._\n**Cần bác sĩ kiểm chứng.**\n"


def slugify(text: str) -> str:
    """Chuyển tên đề tài tiếng Việt thành slug an toàn cho tên thư mục."""
    nkfd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nkfd if not unicodedata.combining(c))
    ascii_text = ascii_text.replace("đ", "d").replace("Đ", "D")
    out = []
    for ch in ascii_text.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_/":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")[:60] or "de-tai"


def md_header(title: str, acode: str, gate: str, agent: str, de_tai: str) -> str:
    """Khối tiêu đề chuẩn cho file .md."""
    return (
        f"# {title}\n\n"
        f"> **Đề tài:** {de_tai}  \n"
        f"> **Mã artifact:** {acode} · **Cổng:** {gate} · **Agent phụ trách:** `{agent}`  \n"
        f"> **Ngày tạo khung:** {TODAY} · **Trạng thái:** [DỰ THẢO] (NOT VERIFIED)\n\n"
    )


def build_files(de_tai: str) -> dict[str, str]:
    """Trả về dict {tên_file: nội_dung} cho trọn bộ 00–20 (+ syntax .R)."""
    f: dict[str, str] = {}

    # 00 — ENTRY POINT (Research Intake & Feasibility Audit) — _CROSSWALK §5
    f["00_Research_Intake_Feasibility_Audit.md"] = (
        md_header("Research Intake & Feasibility Audit", "BƯỚC 0", "G0 Câu hỏi", "dieu-phoi-nghien-cuu", de_tai)
        + "> Sản phẩm BẮT BUỘC đầu mỗi đề tài (entry point). Điền nhãn theo `_CROSSWALK §3`.\n\n"
        "| # | Mục | Nội dung | Trạng thái |\n|---|---|---|---|\n"
        "| 1 | Vấn đề & khoảng trống | [CẦN BỔ SUNG] | NOT VERIFIED |\n"
        "| 2 | Câu hỏi (PICO/PECO/PIRD) | [CẦN BỔ SUNG] | NOT VERIFIED |\n"
        "| 3 | Kết cục chính / phụ + giả thuyết | [CẦN BỔ SUNG] | NOT VERIFIED |\n"
        "| 4 | Giả định loại thiết kế (1 dòng) | [CẦN BỔ SUNG] | NOT VERIFIED |\n"
        "| 5 | Tính mới · ý nghĩa · khả thi (FINER) | [CẦN BỔ SUNG] | NOT VERIFIED |\n"
        "| 6 | Dữ liệu (chưa có/pilot/thật/thứ cấp/đã khóa) | [CẦN BỔ SUNG] | NOT VERIFIED |\n"
        "| 7 | Rủi ro đạo đức–dữ liệu (can thiệp? nhóm dễ tổn thương? PII? AI?) | [CẦN BỔ SUNG] | NOT VERIFIED |\n"
        "| 8 | Cổng hiện tại (trục AGENT) + RESUME từ sổ cái | G0 | — |\n"
        "| 9 | Sản phẩm cần tạo (chiếu 20-file) | [CẦN BỔ SUNG] | — |\n"
        "| 10 | 🚩 Cờ liêm chính/an toàn cần nêu NGAY | [CẦN BỔ SUNG] | — |\n\n"
        "**KẾT:** cổng kế tiếp = G__ ; CHÍNH XÁC cần chủ nhiệm cấp gì: [CẦN CHỦ NHIỆM ẤN ĐỊNH]\n"
        + DISCLAIMER
    )

    # 01 — Project Charter (A1b)
    f["01_Project_Charter.md"] = (
        md_header("Project Charter", "A1b", "G1 Thiết kế", "ke-hoach-trien-khai", de_tai)
        + "## Bối cảnh & lý do\n[CẦN BỔ SUNG]\n\n"
        "## Mục tiêu (SMART)\n- **Mục tiêu chính:** [CẦN BỔ SUNG]\n- **Mục tiêu phụ:** [CẦN BỔ SUNG]\n\n"
        "## Phạm vi\n- Trong phạm vi: [CẦN BỔ SUNG]\n- Ngoài phạm vi: [CẦN BỔ SUNG]\n\n"
        "## Governance & trách nhiệm\n- Chủ nhiệm đề tài: [CẦN CHỦ NHIỆM ẤN ĐỊNH] · Nhóm nghiên cứu: [CẦN BỔ SUNG]\n"
        "- _Agent chỉ HỖ TRỢ; chủ nhiệm + nhóm chịu trách nhiệm cuối (không là tác giả)._\n\n"
        "## Mốc lớn (milestone theo cổng)\n| Cổng | Sản phẩm | Mốc dự kiến |\n|---|---|---|\n"
        "| G2 Đạo đức 🔒 | IRB+ICF+đăng ký | [CẦN BỔ SUNG] |\n| G4 SAP 🔒 | SAP khóa | [CẦN BỔ SUNG] |\n"
        "| G9 Nghiệm thu 🔒 | Báo cáo + bản thảo | [CẦN BỔ SUNG] |\n\n"
        "## Liên kết\n→ `02_Research_Question_and_PICO.md` · `05_Protocol.md` · `18_Risk_Register.csv`\n"
        + DISCLAIMER
    )

    # 02 — Research Question & PICO (A1)
    f["02_Research_Question_and_PICO.md"] = (
        md_header("Câu hỏi nghiên cứu & PICO/PECO", "A1", "G0 Câu hỏi", "cau-hoi-nghien-cuu", de_tai)
        + "## Câu hỏi nghiên cứu\n[CẦN BỔ SUNG]\n\n"
        "## Khung PICO/PECO/PIRD\n| Thành phần | Nội dung |\n|---|---|\n"
        "| P (Population) | [CẦN BỔ SUNG] |\n| I/E (Intervention/Exposure) | [CẦN BỔ SUNG] |\n"
        "| C (Comparison) | [CẦN BỔ SUNG] |\n| O (Outcome) | [CẦN BỔ SUNG] |\n| (T) Time/Setting | [CẦN BỔ SUNG] |\n\n"
        "## Kết cục\n- **Chính** (định nghĩa vận hành · nguồn · thời điểm đo): [CẦN BỔ SUNG]\n- **Phụ:** [CẦN BỔ SUNG]\n\n"
        "## Giả thuyết\n[CẦN BỔ SUNG]\n\n"
        "## Khả thi (FINER)\nFeasible · Interesting · Novel · Ethical · Relevant — [CẦN BỔ SUNG]\n"
        + DISCLAIMER
    )

    # 03 — Evidence Ledger (A2b) — CSV
    f["03_Evidence_Ledger.csv"] = (
        "# Evidence Ledger (A2b) — sổ chứng cứ; G0/G1; agent: tong-quan-y-van+trich-xuat-y-van+tham-dinh-phe-binh\n"
        "# KHÔNG citation ma: mọi dòng phải có PMID/DOI thật, đã đối chiếu metadata. Trạng thái mặc định NOT VERIFIED.\n"
        "STT,Trich dan (tac gia-nam),PMID/DOI,Loai thiet ke,Co mau,Ket cuc,Hieu ung + 95% CI,Nguy co sai lech (RoB),GRADE,Lien quan/Gap,Trang thai kiem chung\n"
        "1,[CAN BO SUNG],,,,,,,,,NOT VERIFIED\n"
    )

    # 04 — Literature Review (A2 cơ sở)
    f["04_Literature_Review.md"] = (
        md_header("Tổng quan y văn", "A2 (cơ sở lý luận)", "G0/G1", "thu-thu-tai-lieu + tong-quan-y-van + khoang-trong-nghien-cuu", de_tai)
        + "## Chiến lược tìm kiếm\nNguồn (PubMed/Cochrane/Europe PMC…) · từ khóa/MeSH · giới hạn: [CẦN BỔ SUNG]\n\n"
        "## Tổng hợp bằng chứng (phân loại nguồn)\nGuideline · SR/meta · RCT · cohort · bệnh-chứng — [CẦN BỔ SUNG] (chi tiết ở `03_Evidence_Ledger.csv`)\n\n"
        "## Khoảng trống nghiên cứu (research gap) & biện minh tính mới\n[CẦN BỔ SUNG]\n\n"
        "> Nếu đề tài LÀ tổng quan hệ thống → theo PRISMA + đăng ký PROSPERO (chuyển `tong-quan-y-van`).\n"
        + DISCLAIMER
    )

    # 05 — Protocol (A2)
    f["05_Protocol.md"] = (
        md_header("Đề cương / Protocol", "A2", "G1 Thiết kế", "thiet-ke-nghien-cuu (+viet-ban-thao)", de_tai)
        + "## Thiết kế nghiên cứu\nLoại thiết kế + lý do + phương án thay thế: [CẦN BỔ SUNG] _(thử nghiệm → theo SPIRIT)_\n\n"
        "## Dân số\n- Dân số đích / dân số nghiên cứu: [CẦN BỔ SUNG]\n- Tiêu chuẩn chọn / loại trừ: [CẦN BỔ SUNG]\n- Phương pháp chọn mẫu: [CẦN BỔ SUNG]\n\n"
        "## Biến số & confounder\n[CẦN BỔ SUNG] (chi tiết ở `09_Data_Dictionary.csv`)\n\n"
        "## Kế hoạch phân tích (tóm tắt — bản đầy đủ ở SAP)\n[CẦN BỔ SUNG]\n\n"
        "## Chuẩn báo cáo dự kiến\n[CẦN BỔ SUNG] (STROBE/CONSORT/PRISMA/STARD/TRIPOD+AI…)\n"
        + DISCLAIMER
    )

    # 06 — Ethics Package Checklist (A3/A4) — CỔNG CỨNG
    f["06_Ethics_Package_Checklist.md"] = (
        md_header("Hồ sơ Đạo đức + Đăng ký (checklist)", "A3 · A4", "G2 Đạo đức 🔒", "dao-duc-dang-ky", de_tai)
        + "> 🔒 **CỔNG CỨNG.** KHÔNG ghi 'đã được hội đồng đạo đức phê duyệt' khi CHƯA có bằng chứng. KHÔNG chạm dữ liệu thật trước khi cổng này ĐÓNG.\n\n"
        "| Hạng mục | Trạng thái |\n|---|---|\n"
        "| Hồ sơ IRB (Helsinki/ICH-GCP/CIOMS; TT 43/2024/TT-BYT) | [CẦN BỔ SUNG] / NOT VERIFIED |\n"
        "| Phiếu đồng thuận (ICF) | [CẦN BỔ SUNG] |\n"
        "| Đánh giá rủi ro–lợi ích · nhóm dễ tổn thương | [CẦN BỔ SUNG] |\n"
        "| Đăng ký nghiên cứu (bắt buộc nếu CAN THIỆP; quan sát: nêu quyết định) | [CẦN BỔ SUNG] |\n"
        "| Kế hoạch bảo vệ dữ liệu (Luật 91/2025/QH15 + NĐ 356/2025/NĐ-CP) | [CẦN BỔ SUNG] |\n"
        "| Số phê duyệt IRB | [CẦN CHỦ NHIỆM ẤN ĐỊNH — KHÔNG bịa] |\n"
        "| Mã đăng ký | [CẦN CHỦ NHIỆM ẤN ĐỊNH — KHÔNG bịa] |\n"
        + DISCLAIMER
    )

    # 07 — CRF / Questionnaire (A6/A7)
    f["07_CRF_or_Questionnaire.md"] = (
        md_header("CRF / Phiếu khảo sát", "A6 · A7", "G3 Biến/CRF", "bien-so-nghien-cuu + quan-ly-du-lieu (+cong-cu-do-luong)", de_tai)
        + "## Cấu trúc phiếu (khớp `09_Data_Dictionary.csv`)\n[CẦN BỔ SUNG]\n\n"
        "## Pilot/pre-test (A16) — TRƯỚC thu chính thức\nThử cỡ nhỏ · chỉnh item khó hiểu/lỗi logic/thời lượng · biên bản pilot: [CẦN BỔ SUNG]\n\n"
        "> Nếu dùng PROM/thang đo đã kiểm định → COSMIN + dịch–thích nghi văn hóa (`cong-cu-do-luong`). KHÔNG bịa thang/điểm cắt.\n"
        + DISCLAIMER
    )

    # 08 — SOP Data Collection (A17a)
    f["08_SOP_Data_Collection.md"] = (
        md_header("SOP thu thập dữ liệu", "A17a", "G5 Thu thập", "quan-ly-du-lieu", de_tai)
        + "## Quy trình chuẩn\nNhập liệu · kiểm tra · khử định danh · khóa: [CẦN BỔ SUNG]\n\n"
        "## Đào tạo người thu thập · giám sát · deviation log\n[CẦN BỔ SUNG]\n\n"
        "> ALCOA+ · làm trên BẢN SAO · KHÔNG sửa dữ liệu gốc · KHÔNG PII.\n"
        + DISCLAIMER
    )

    # 09 — Data Dictionary (A6) — CSV
    f["09_Data_Dictionary.csv"] = (
        "# Data Dictionary / Codebook (A6) — G3/G5; agent: quan-ly-du-lieu\n"
        "# Mỗi biến: khớp CRF + biến phân tích trong SAP. KHÔNG thừa biến khó thu.\n"
        "Ten bien,Nhan,Loai (dinh tinh/dinh luong),Don vi,Mien gia tri hop le,Ma thieu,Nguon,Vai tro (doc lap/phu thuoc/nhieu),Thoi diem do\n"
        "id,Ma giả danh,định danh,,,,he thong,,T0\n"
        "[CAN BO SUNG],,,,,,,,\n"
    )

    # 10 — Sample Size (A5)
    f["10_Sample_Size_Calculation.md"] = (
        md_header("Tính cỡ mẫu / Power", "A5", "G3 Cỡ mẫu", "co-mau-nghien-cuu", de_tai)
        + "## Tham số\n- Thiết kế: [CẦN BỔ SUNG] · alpha: 0,05 · power: 0,80 (hoặc [CẦN BỔ SUNG])\n"
        "- **Effect size:** [CẦN BỔ SUNG — CÓ NGUỒN: pilot/y văn (ghi PMID/DOI) hoặc MCID do chủ nhiệm ấn định; KHÔNG bịa]\n"
        "- Tỷ lệ biến cố/SD: [CẦN BỔ SUNG] · dropout: [CẦN BỔ SUNG] · design effect (nếu cụm): [CẦN BỔ SUNG]\n\n"
        "## Công thức & kết quả\nCông thức: [CẦN BỔ SUNG] → cỡ mẫu từng nhóm + tổng: [CẦN BỔ SUNG]\n\n"
        "## Bảng độ nhạy (theo effect size)\n[CẦN BỔ SUNG]\n"
        + DISCLAIMER
    )

    # 11 — SAP (A8) — CỔNG CỨNG
    f["11_Statistical_Analysis_Plan.md"] = (
        md_header("Kế hoạch phân tích thống kê (SAP)", "A8 (+A10)", "G4 SAP 🔒", "thiet-ke-nghien-cuu + phan-tich-thong-ke", de_tai)
        + "> 🔒 **CỔNG CỨNG — KHÓA TRƯỚC khi xem dữ liệu.** Sau khi xem dữ liệu KHÔNG đổi kết cục chính/cỡ mẫu/SAP (chống p-hacking/HARKing).\n\n"
        "## Phân tích chính / phụ / thăm dò (phân biệt rõ ĐỊNH TRƯỚC vs THĂM DÒ)\n[CẦN BỔ SUNG]\n\n"
        "## Kiểm định · ước lượng\nMỗi kết quả: **effect size + 95% CI** (KHÔNG p-value đơn độc — R8/P6). Xử lý missing: [CẦN BỔ SUNG]\n\n"
        "## Kiểm giả định mô hình · confounder · mô hình đa biến\n[CẦN BỔ SUNG]\n\n"
        "## Trạng thái khóa SAP\n[ ] Đã khóa ngày: ____ — **[CẦN CHỦ NHIỆM XÁC NHẬN]**\n"
        + DISCLAIMER
    )

    # 12 — Data Cleaning Plan (A9)
    f["12_Data_Cleaning_Plan.md"] = (
        md_header("Kế hoạch làm sạch & quản lý dữ liệu (DMP)", "A9", "G5", "quan-ly-du-lieu", de_tai)
        + "## Luật kiểm tra (validation)\nRange · logic/skip · nhất quán · trùng lặp · ngày hợp lý → BÁO CÁO BẤT THƯỜNG + NHẬT KÝ TRUY VẤN (gắn cờ, KHÔNG tự sửa): [CẦN BỔ SUNG]\n\n"
        "## Dữ liệu thiếu\nCơ chế (MCAR/MAR/MNAR) + kế hoạch (khớp SAP): [CẦN BỔ SUNG]\n\n"
        "## Khử định danh · access control · backup\n[CẦN BỔ SUNG] — KHÔNG PII; làm trên BẢN SAO.\n"
        + DISCLAIMER
    )

    # 13 — Data Lock Memo (A9b)
    f["13_Data_Lock_Memo.md"] = (
        md_header("Data Lock Memo (biên bản khóa dữ liệu)", "A9b", "G5/G6", "quan-ly-du-lieu", de_tai)
        + "> Chỉ lập khi đã giải quyết hết truy vấn VÀ **SAP đã khóa (G4) TRƯỚC**.\n\n"
        "| Mục | Giá trị |\n|---|---|\n"
        "| Ngày/giờ khóa | [CẦN BỔ SUNG] |\n| Phiên bản dataset (hash/checksum) | [CẦN BỔ SUNG] |\n"
        "| Số bản ghi | [CẦN BỔ SUNG] |\n| Số biến | [CẦN BỔ SUNG] |\n"
        "| Truy vấn đã đóng | [CẦN BỔ SUNG] |\n| Người khóa | [CẦN CHỦ NHIỆM ẤN ĐỊNH] |\n"
        "| SAP đã khóa TRƯỚC? | [ ] Có — ngày: ____ |\n| QC hậu-khóa sạch? | [ ] Có (xem báo cáo QC) |\n"
        + DISCLAIMER
    )

    # 14 — Analysis Syntax (A17b) — .sps + .R skeleton
    f["14_Analysis_Syntax.sps"] = (
        "* ============================================================\n"
        f"* Analysis Syntax (A17b) — TÁI LẬP — Đề tài: {de_tai}\n"
        f"* Cổng: G6 Phân tích · Agent: phan-tich-thong-ke · Tạo khung: {TODAY}\n"
        "* NGUYÊN TẮC: chạy ĐÚNG SAP đã khóa (11_) trên DB đã khóa (13_); KHÔNG sửa SAP sau khi xem dữ liệu.\n"
        "* Báo cáo: effect size + 95% CI, KHÔNG p-value đơn độc.\n"
        "* ============================================================.\n"
        "SET SEED 20260620.   /* cố định seed để tái lập */.\n"
        "* GET FILE='[CẦN BỔ SUNG — đường dẫn DB đã khóa, bản sao]'.\n"
        "* === Mô tả mẫu (Bảng 1) ===.\n"
        "* === Phân tích chính (theo SAP) ===.\n"
        "* === Kiểm giả định mô hình ===.\n"
        "* [CẦN BỔ SUNG].\n"
    )
    f["14_Analysis_Syntax.R"] = (
        "# ============================================================\n"
        f"# Analysis Syntax (A17b) — TÁI LẬP — Đề tài: {de_tai}\n"
        f"# Cổng: G6 Phân tích · Agent: phan-tich-thong-ke · Tạo khung: {TODAY}\n"
        "# Chạy ĐÚNG SAP đã khóa (11_) trên DB đã khóa (13_). Báo cáo effect size + 95% CI.\n"
        "# ============================================================\n"
        "set.seed(20260620)            # cố định seed\n"
        "# sessionInfo() ghi ở cuối log để versioned môi trường\n"
        "# library(...)                # [CẦN BỔ SUNG: ghi rõ phiên bản gói]\n"
        "# dat <- readRDS('[CẦN BỔ SUNG — DB đã khóa, bản sao]')\n"
        "# === Bảng 1: mô tả mẫu ===\n"
        "# === Phân tích chính (theo SAP) — xuất est + 95% CI ===\n"
        "# === Kiểm giả định ===\n"
        "# [CẦN BỔ SUNG]\n"
        "# writeLines(capture.output(sessionInfo()), 'sessionInfo.txt')\n"
    )

    # 15 — Table Shells (A10) — CSV
    f["15_Table_Shells.csv"] = (
        "# Table Shells / Dummy tables (A10) — G4; agent: thiet-ke-nghien-cuu+phan-tich-thong-ke\n"
        "# Bảng TRỐNG cho từng phân tích ĐỊNH TRƯỚC; ô số liệu để trống cho tới khi chạy SAP trên DB đã khóa.\n"
        "Bang,Dac trung,Nhom 1 (n=),Nhom 2 (n=),Hieu ung + 95% CI,Ghi chu\n"
        "Bang 1 - Mo ta mau,[CAN BO SUNG],,,,\n"
        "Bang 2 - Ket cuc chinh,[CAN BO SUNG],,,(effect size + 95% CI; khong p don doc),\n"
    )

    # 16 — IMRAD Manuscript (A11)
    f["16_IMRAD_Manuscript.md"] = (
        md_header("Bản thảo IMRAD", "A11", "G7 Viết", "viet-ban-thao (+hieu-dinh-song-ngu)", de_tai)
        + "## Introduction\n[CẦN BỔ SUNG]\n\n## Methods\n[CẦN BỔ SUNG] _(khớp `05_Protocol.md` + `11_SAP`)_\n\n"
        "## Results\n[CẦN BỔ SUNG] _(chỉ điền sau khi có dữ liệu thật + chạy SAP; effect size + 95% CI)_\n\n"
        "## Discussion\n[CẦN BỔ SUNG] _(KHÔNG kết luận vượt thiết kế; phân biệt ý nghĩa thống kê vs lâm sàng)_\n\n"
        "> Mọi trích dẫn kèm PMID/DOI đã kiểm (`19_Research_Integrity_Audit.md`). Khai báo dùng AI + tác giả ICMJE + COI.\n"
        + DISCLAIMER
    )

    # 17 — Reporting Checklist (A11)
    f["17_Reporting_Checklist.md"] = (
        md_header("Checklist chuẩn báo cáo", "A11", "G7 Viết", "viet-ban-thao", de_tai)
        + "## Chuẩn áp dụng (theo thiết kế)\n[CẦN BỔ SUNG] — chọn 1: STROBE (quan sát) · CONSORT+SPIRIT (RCT) · PRISMA (SR) · STARD (chẩn đoán) · TRIPOD+AI (dự báo) · COREQ/SRQR (định tính) · SQUIRE (QI) · CHEERS (kinh tế)\n\n"
        "| Mục checklist | Trang/Mục | Đạt |\n|---|---|---|\n| [CẦN BỔ SUNG] | | [ ] |\n"
        + DISCLAIMER
    )

    # 18 — Risk Register (A13b) — CSV
    f["18_Risk_Register.csv"] = (
        "# Risk Register SỐNG + CAPA (A13b) — G1+G7; agent: ke-hoach-trien-khai (+dao-duc-dang-ky)\n"
        "# Sổ SỐNG: ra soat lai sau MOI cong; luu phien ban qua so-cai-ghi-nho.\n"
        "STT,Rui ro,Loai (dao duc/du lieu/thong ke/tien do/liem chinh),Muc (xac suat x hau qua),Giam thieu,CAPA,Trang thai,Ngay,Chu tri\n"
        "1,Tuyen cham,tien do,[CAN BO SUNG],mo rong thoi gian/nguon,,Mo,," + TODAY + "\n"
        "2,Lo PII,du lieu,cao,khu dinh danh + lam tren ban sao,,Mo,," + TODAY + "\n"
    )

    # 19 — Research Integrity Audit
    f["19_Research_Integrity_Audit.md"] = (
        md_header("Kiểm toán Liêm chính Nghiên cứu", "completeness-critic + A12 + A14", "G7/G9", "dieu-phoi-nghien-cuu + binh-duyet + kiem-chung-trich-dan", de_tai)
        + "## Traceability\nMục tiêu → biến số → CRF → dữ liệu → SAP → bảng → kết luận: [CẦN KIỂM]\n\n"
        "## Citation validity (A12) 🔒\nMọi PMID/DOI xác minh thật + đúng nội dung; bắt trích dẫn ma/retracted: [CẦN KIỂM]\n\n"
        "## Consistency chéo\nĐề cương ↔ phân tích ↔ báo cáo khớp nhau: [CẦN KIỂM]\n\n"
        "## Đạo đức · bảo mật · quyền tác giả (A14) 🔒\nCOI · tài trợ · đóng góp tác giả (ICMJE) · khai báo AI — **chủ nhiệm xác nhận**: [CẦN CHỦ NHIỆM ẤN ĐỊNH]\n"
        + DISCLAIMER
    )

    # 20 — Final Readiness Report (A18) — 3 hạng
    f["20_Final_Readiness_Report.md"] = (
        md_header("Báo cáo Sẵn sàng Nghiệm thu (Final Readiness)", "A18", "G9 Nghiệm thu 🔒", "dieu-phoi-nghien-cuu + viet-ban-thao", de_tai)
        + "## Đối chiếu Definition of Done (14 điểm — `_KIEM-TOAN §0bis`)\n[CẦN KIỂM] — bảng 14 điểm\n\n"
        "## GAP REGISTER + CAPA\n| # | Khoảng trống (🔴) | Mức | Điểm DoD | Agent | CAPA | Hạn | TT |\n|---|---|---|---|---|---|---|---|\n| 1 | [CẦN BỔ SUNG] | | | | | | |\n\n"
        "## KẾT LUẬN NGHIỆM THU (chọn 1)\n"
        "- [ ] **READY** — đủ 14/14 DoD; không 🔴; 3 cổng cứng đã ĐÓNG\n"
        "- [ ] **PARTIALLY READY** — chỉ còn Medium/Low; mọi Critical/High đã khắc phục\n"
        "- [ ] **NOT READY** — còn ≥1 Critical/High\n\n"
        "> KHÔNG kết luận READY khi còn Critical/High. Mức nặng 🔴: xem `_KIEM-TOAN §D`.\n"
        + DISCLAIMER
    )

    return f


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh khung 20-file cho một đề tài nghiên cứu y khoa.")
    ap.add_argument("title", help="Tên/mô tả đề tài (đặt trong dấu ngoặc kép).")
    ap.add_argument("--slug", help="Tên thư mục rút gọn (mặc định sinh từ title).")
    ap.add_argument("--force", action="store_true", help="Ghi đè nếu thư mục đã tồn tại.")
    args = ap.parse_args()

    slug = slugify(args.slug or args.title)
    target = PROJECTS_DIR / slug

    if target.exists() and not args.force:
        print(f"⛔ Thư mục đã tồn tại: {target}\n   Dùng --force để ghi đè, hoặc --slug để đổi tên.", file=sys.stderr)
        return 1

    target.mkdir(parents=True, exist_ok=True)
    files = build_files(args.title)
    for name, content in files.items():
        (target / name).write_text(content, encoding="utf-8")

    print(f"✅ Đã sinh {len(files)} file khung cho đề tài:\n   '{args.title}'")
    print(f"   → {target}")
    print("   Bắt đầu ở 00_Research_Intake_Feasibility_Audit.md. Mọi số liệu để [CẦN BỔ SUNG]; KHÔNG PII.")
    print("   Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
