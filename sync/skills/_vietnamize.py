#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_vietnamize.py — Việt hóa & gắn quy tắc EBM cho bộ skill khoa học (K-Dense).

Thao tác cho từng SKILL.md:
  1) Thay trường `description:` trong YAML frontmatter bằng mô tả tiếng Việt
     (điều khiển việc kích hoạt skill cho bác sĩ EBM).
  2) Chèn khối "QUY TẮC EBM BẮT BUỘC" (tiếng Việt) ngay sau frontmatter,
     khối này ghi đè hành vi: tiếng Việt, disclaimer, không PII, ghi PMID/DOI,
     chỉ dùng PubMed miễn phí.

Idempotent: chạy lại nhiều lần không nhân đôi khối quy tắc (nhận diện bằng marker).
"""
from pathlib import Path

HUB = Path(__file__).resolve().parent
MARKER = "<!-- EBM-VN-GUARD -->"

# ĐỔI TÊN KHOÁ 06/09/2026 — ĐỌC TRƯỚC KHI SỬA
# Bảy skill K-Dense (citation-management, literature-review, paper-lookup,
# peer-review, research-lookup, scientific-writing, statistical-analysis) đã được
# đổi thư mục thành "<tên>-kdense", nhường tên gốc cho bảy skill EBM bản tài khoản
# (bản đang chạy trong Routine và mọi phiên claude.ai). Hai họ skill này TRÙNG TÊN
# nhưng nội dung chỉ giống nhau 6-19% — chúng là hai skill khác nhau.
#
# Vì `process()` chỉ xử lý thư mục có tên nằm trong DESCRIPTIONS, khoá ở đây PHẢI
# mang hậu tố -kdense. Nếu bỏ hậu tố đi, lần chạy `_vietnamize.py` kế tiếp sẽ ghi đè
# mô tả và chèn khối EBM-VN-GUARD lên bảy skill EBM bản tài khoản — tức phá đúng
# những skill mang cổng liêm chính của hệ.

# Mô tả tiếng Việt cho từng skill (trường `description` của frontmatter)
DESCRIPTIONS = {
    "literature-review-kdense":
        "Thực hiện tổng quan y văn có hệ thống (systematic review, tổng quan, "
        "meta-analysis) bằng các CSDL học thuật MIỄN PHÍ (PubMed E-utilities, PMC, "
        "bioRxiv, medRxiv, OpenAlex, Crossref, Semantic Scholar). Dùng khi cần tổng "
        "hợp bằng chứng cho một câu hỏi lâm sàng/PICO, rà soát y văn hoặc viết phần "
        "tổng quan. Tạo tài liệu Markdown/PDF có trích dẫn đã kiểm chứng "
        "(Vancouver/APA), kèm PMID/DOI và disclaimer 'Cần bác sĩ kiểm chứng'. "
        "KHÔNG dùng API trả phí.",
    "paper-lookup-kdense":
        "Tra cứu bài báo khoa học qua REST API MIỄN PHÍ của nhiều CSDL: PubMed, PMC "
        "(toàn văn), bioRxiv, medRxiv, arXiv, OpenAlex, Crossref, Semantic Scholar, "
        "CORE, Unpaywall. Dùng khi cần tìm bài theo chủ đề, tra DOI/PMID, lấy "
        "abstract/toàn văn, tìm bản open access, đồ thị trích dẫn hoặc tìm theo tác "
        "giả. Mọi kết quả ghi rõ PMID/DOI.",
    "citation-management-kdense":
        "Quản lý trích dẫn học thuật: tìm bài trên PubMed (E-utilities miễn phí) và "
        "Google Scholar, trích xuất metadata chính xác, kiểm chứng trích dẫn, sinh "
        "BibTeX đúng chuẩn. Dùng khi cần tìm bài, xác minh thông tin trích dẫn, đổi "
        "DOI→BibTeX hoặc bảo đảm độ chính xác tài liệu tham khảo. Luôn kèm PMID/DOI.",
    "research-lookup-kdense":
        "Tra cứu thông tin nghiên cứu hiện hành qua PubMed E-utilities (MIỄN PHÍ, "
        "không cần API key). Dùng để tìm bài báo, thu thập dữ liệu nghiên cứu, kiểm "
        "chứng thông tin khoa học cho câu hỏi lâm sàng. Đã LOẠI BỎ mọi backend trả "
        "phí (parallel.ai/Perplexity/OpenRouter). Kết quả kèm PMID/DOI và disclaimer "
        "'Cần bác sĩ kiểm chứng'.",
    "clinical-decision-support":
        "Tạo tài liệu hỗ trợ quyết định lâm sàng (CDS): phân tích nhóm bệnh nhân "
        "(cohort) theo dấu ấn sinh học, báo cáo khuyến cáo điều trị dựa trên bằng "
        "chứng kèm thuật toán quyết định và phân độ GRADE; phân tích thống kê (HR, "
        "đường sống còn); xuất LaTeX/PDF. Dùng cho nghiên cứu/tổng hợp bằng chứng. "
        "Mọi đầu ra y khoa kèm nguồn PMID/DOI, disclaimer 'Cần bác sĩ kiểm chứng', "
        "KHÔNG lưu PII.",
    "clinical-reports":
        "Viết báo cáo lâm sàng: case report (chuẩn CARE), báo cáo chẩn đoán "
        "(X-quang/giải phẫu bệnh/xét nghiệm), báo cáo thử nghiệm lâm sàng (ICH-E3) và "
        "hồ sơ bệnh án (SOAP, H&P, tóm tắt xuất viện). Kèm template và công cụ kiểm "
        "tra. Mọi đầu ra kèm nguồn PMID/DOI, disclaimer 'Cần bác sĩ kiểm chứng', "
        "KHÔNG lưu thông tin định danh bệnh nhân (PII).",
    "treatment-plans":
        "Soạn kế hoạch điều trị y khoa ngắn gọn (3-4 trang) xuất LaTeX/PDF cho nhiều "
        "chuyên khoa: nội khoa chung, phục hồi chức năng, sức khỏe tâm thần, quản lý "
        "bệnh mạn, chu phẫu, giảm đau. Dùng khung mục tiêu SMART, can thiệp dựa bằng "
        "chứng. Kèm nguồn PMID/DOI, disclaimer 'Cần bác sĩ kiểm chứng', KHÔNG lưu PII.",
    "scientific-writing-kdense":
        "Viết bản thảo khoa học theo cấu trúc IMRAD, văn xuôi liền mạch (không gạch "
        "đầu dòng), trích dẫn Vancouver/APA/AMA, tuân thủ chuẩn báo cáo "
        "(CONSORT/STROBE/PRISMA). Dùng khi viết bài báo nghiên cứu hoặc bản thảo nộp "
        "tạp chí. Quy trình 2 bước: dàn ý → văn xuôi. Trích dẫn kèm PMID/DOI.",
    "statistical-analysis-kdense":
        "Hướng dẫn phân tích thống kê: chọn test phù hợp với dữ liệu, kiểm tra giả "
        "định, tính cỡ mẫu (power), trình bày kết quả chuẩn APA. Dùng khi cần chọn "
        "kiểm định hoặc báo cáo thống kê cho nghiên cứu y khoa. (Để chạy mô hình cụ "
        "thể bằng code, dùng statsmodels.)",
    "peer-review-kdense":
        "Bình duyệt bản thảo/đề cương theo checklist: đánh giá phương pháp, tính hợp "
        "lệ thống kê, tuân thủ chuẩn báo cáo (CONSORT/STROBE) và góp ý mang tính xây "
        "dựng. Dùng khi viết phản biện chính thức hoặc rà soát bản thảo trước khi nộp.",
    # --- Đợt 2 (2026-07-04): 8 skill phương pháp nghiên cứu, bổ sung cho cụm G0-G9 ---
    "statistical-power":
        "Tính CỠ MẪU / LỰC THỐNG KÊ (power analysis) TRƯỚC khi thu thập dữ liệu — "
        "bằng công thức đóng (t-test, ANOVA, tỷ lệ, tương quan, chi-square, hồi quy) "
        "VÀ mô phỏng Monte Carlo cho thiết kế không có công thức chuẩn (hồi quy "
        "logistic/Poisson, mixed model, cluster-RCT, sống còn, có tương tác). Dùng "
        "khi cần trả lời 'cần bao nhiêu bệnh nhân', biện minh cỡ mẫu cho đề cương/IRB, "
        "hoặc vẽ đường cong power. Bổ sung công cụ tính chạy được cho agent "
        "co-mau-nghien-cuu (G3) — chạy offline bằng Python, không cần API.",
    "experimental-design":
        "Thiết kế thí nghiệm/nghiên cứu TRƯỚC khi thu thập dữ liệu — chọn thiết kế, "
        "ngẫu nhiên hóa (randomization), phân khối (blocking/stratification), bố trí "
        "factorial/fractional-factorial, crossover, split-plot, Latin square, kiểm "
        "soát hiệu ứng thứ tự/đợt chạy. Dùng khi cần phân nhóm bệnh nhân/mẫu vào các "
        "nhánh, tránh nhiễu (confounding), hoặc lập kế hoạch thử nghiệm nhiều yếu tố. "
        "Bổ sung công cụ sinh sơ đồ phân nhóm chạy được cho thiet-ke-nghien-cuu (G1) "
        "— chạy offline bằng Python, không cần API.",
    "statsmodels":
        "Chạy mô hình thống kê THẬT bằng thư viện statsmodels: OLS, GLM, mô hình "
        "hỗn hợp (mixed-effects), ARIMA/chuỗi thời gian — kèm bảng hệ số, chẩn đoán "
        "giả định, phân tích residual. Dùng khi ĐÃ có dữ liệu và cần fit một mô hình "
        "cụ thể (khác statistical-analysis vốn chỉ hướng dẫn CHỌN test phù hợp). Bổ "
        "sung động cơ tính toán cho phan-tich-thong-ke (G6) — chạy offline, không "
        "cần API.",
    "scikit-survival":
        "Phân tích SỐNG CÒN / thời gian-đến-biến-cố (time-to-event) bằng "
        "scikit-survival: mô hình Cox, Random Survival Forest, Gradient Boosting, "
        "Survival SVM; xử lý dữ liệu KIỂM DUYỆT (censoring) và NGUY CƠ CẠNH TRANH "
        "(competing risks); đánh giá bằng c-index/Brier score. Dùng khi kết cục "
        "nghiên cứu là thời gian tới biến cố (tử vong, tái phát, biến chứng...). Bổ "
        "sung cho phan-tich-thong-ke (G6) — chạy offline bằng Python, không cần API.",
    "scientific-critical-thinking":
        "Khung THẨM ĐỊNH chất lượng chứng cứ và tính hợp lệ của thiết kế nghiên cứu "
        "— áp dụng GRADE, Cochrane Risk of Bias, nhận diện thiên kiến/nhiễu/ngụy "
        "biện logic và các lỗi thống kê thường gặp. Dùng để dạy hoặc tự kiểm tra tư "
        "duy phản biện khoa học, bổ trợ cho tham-dinh-phe-binh và "
        "tham-dinh-grade-nnt. Thuần hướng dẫn, chạy offline không cần API — bản này "
        "đã gỡ tính năng vẽ sơ đồ bằng AI trả phí, dùng markdown-mermaid-writing "
        "(miễn phí) nếu cần minh họa.",
    "venue-templates":
        "Template LaTeX + yêu cầu định dạng cho các tạp chí/hội nghị khoa học lớn "
        "(Nature, Science, PLOS, Elsevier...), poster nghiên cứu, và đề cương xin "
        "tài trợ — kèm chuẩn báo cáo CONSORT/STROBE/PRISMA cho bài y khoa. Dùng khi "
        "chuẩn bị bản thảo nộp tạp chí, poster hội nghị, hoặc đề cương. Bổ sung cho "
        "viet-ban-thao/nop-bai-phan-hoi (G7). ĐÃ GỠ tính năng vẽ sơ đồ bằng AI trả "
        "phí (Nano Banana/OpenRouter) — nếu cần sơ đồ, dùng markdown-mermaid-writing "
        "(miễn phí).",
    "exploratory-data-analysis":
        "Khảo sát nhanh cấu trúc, chất lượng và đặc điểm của MỘT file dữ liệu khoa "
        "học (200+ định dạng: bảng tính, gen học, hóa học, ảnh vi mô, phổ, "
        "proteomics...) — tự nhận diện định dạng, sinh báo cáo markdown về chất "
        "lượng dữ liệu và gợi ý bước phân tích tiếp theo. Dùng ở bước làm sạch/khóa "
        "dữ liệu (quan-ly-du-lieu, G5) trước khi phân tích chính thức. Chạy offline "
        "bằng Python, không cần API. Không lưu PII.",
    "database-lookup":
        "Truy vấn 78+ CƠ SỞ DỮ LIỆU khoa học/y khoa công khai qua API đã tài liệu "
        "hóa rõ endpoint, bộ lọc, phân trang và nguồn gốc dữ liệu (PubChem, ChEMBL, "
        "UniProt, ClinicalTrials.gov, FDA, dbSNP, ClinVar, COSMIC, GWAS Catalog, "
        "OMIM... phần lớn MIỄN PHÍ, một số cần đăng ký khóa MIỄN PHÍ của chính CSDL "
        "đó). Dùng khi cần lấy một sự kiện/số liệu khoa học có thể TÁI LẶP từ nguồn "
        "được nêu tên, thay vì suy đoán. Bổ sung nguồn tra cứu có provenance cho "
        "tra-cuu-chung-cu và các agent nghiên cứu. Không dùng dịch vụ AI trả phí "
        "trung gian.",
    # --- Đợt 3 (2026-07-04): 3 skill Nhóm B, bổ sung định lượng/giả thuyết/ML lâm sàng ---
    "scholar-evaluation":
        "Chấm điểm ĐỊNH LƯỢNG chất lượng học thuật của bản thảo/đề cương/tổng quan "
        "theo khung ScholarEval — 8 chiều (đặt vấn đề, tổng quan y văn, phương "
        "pháp, thu thập dữ liệu, phân tích, kết quả, văn phong, trích dẫn), mỗi "
        "chiều chấm 0-5 có trọng số riêng (methodology 20%...), ra điểm trung bình "
        "có trọng số + xếp 6 mức chất lượng (Exceptional→Poor) + bar chart. Dùng "
        "SONG SONG với bình duyệt định tính (binh-duyet, G8) để theo dõi tiến bộ "
        "qua các lần sửa bản thảo — KHÔNG thay thế bình duyệt định tính. Chạy "
        "offline bằng Python (scripts/calculate_scores.py), không cần API.",
    "hypothesis-generation":
        "Hình thức hóa GIẢ THUYẾT khoa học từ quan sát/dữ liệu — sinh 3-5 giả "
        "thuyết CẠNH TRANH kèm CƠ CHẾ, chấm chất lượng theo 7 tiêu chí (khả kiểm "
        "định, khả bác bỏ theo Popper, tính đơn giản, sức giải thích, phạm vi, "
        "nhất quán, tính mới), rồi gợi ý pattern thiết kế thí nghiệm phân biệt "
        "giữa các giả thuyết. Dùng SAU khi đã có câu hỏi PICO/H0-H1 thô "
        "(cau-hoi-nghien-cuu, G0) và TRƯỚC khi chọn thiết kế (thiet-ke-nghien-cuu, "
        "G1) — lấp khoảng trống hình thức hóa giả thuyết mà 2 agent đó chưa có. "
        "Thuần tài liệu tham khảo + template LaTeX, chạy offline không cần API.",
    "pyhealth":
        "Xây dựng pipeline học máy lâm sàng bằng thư viện PyHealth: tải dữ liệu "
        "EHR (MIMIC-III/IV, eICU, OMOP), định nghĩa tác vụ (tử vong, tái nhập "
        "viện, gợi ý thuốc, giai đoạn ngủ, mã hóa ICD), huấn luyện mô hình "
        "(Transformer, RETAIN, GAMENet, SafeDrug...), và TRA/ĐỐI CHIẾU mã y khoa "
        "(ICD-9/10-CM, ATC, NDC, RxNorm, CCS — offline, không cần API) qua "
        "InnerMap/CrossMap. Dùng cho nhánh HỌC MÁY của mo-hinh-tien-luong (khi hồi "
        "quy cổ điển không đủ) và để tra/đối chiếu mã THUỐC ATC/NDC/RxNorm cho "
        "ke-don-an-toan/ke-don-an-toan-benh-man (mã BỆNH ICD đã có MCP riêng, mã "
        "thuốc thì chưa). Yêu cầu Python ≥3.12,<3.14 + cài PyTorch (nặng, cần "
        "mạng) — chỉ dùng khi thực sự cần xây mô hình ML, không phải thống kê cổ "
        "điển (đã có statsmodels/scikit-survival).",
}

GUARD = """{marker}
> **⚕️ Bản điều chỉnh cho bác sĩ EBM ngoại trú (Việt Nam).** Skill gốc của K-Dense Inc. đã được chỉnh để phù hợp quy ước trong `CLAUDE.md` của người dùng.
>
> **QUY TẮC BẮT BUỘC — đọc trước, GHI ĐÈ mọi hướng dẫn tiếng Anh bên dưới:**
> 1. **Ngôn ngữ:** Mọi trao đổi và đầu ra cho người dùng viết bằng **tiếng Việt** (giữ thuật ngữ y khoa tiếng Anh khi cần; tên thuốc theo INN).
> 2. **Disclaimer:** Mọi đầu ra y khoa kết thúc bằng câu **"⚠️ Cần bác sĩ kiểm chứng trước khi áp dụng lâm sàng."**
> 3. **Nguồn:** Mọi nhận định/khuyến cáo phải **ghi nguồn (PMID/DOI)**; không có nguồn thì không khẳng định. **Tuyệt đối không bịa dữ liệu hay nguồn.**
> 4. **Không PII:** **KHÔNG** lưu hay tạo thông tin định danh bệnh nhân (tên, ngày sinh, số hồ sơ, địa chỉ...). Dùng mã ẩn danh.
> 5. **Chỉ nguồn miễn phí:** Khi tra cứu y văn dùng **PubMed E-utilities** (miễn phí, không cần API key) và các CSDL mở. **KHÔNG** dùng dịch vụ trả phí (parallel.ai, Perplexity, OpenRouter...). Nếu một lệnh gốc gọi `parallel-cli`/Perplexity, thay bằng `python scripts/pubmed_lookup.py "..."` hoặc REST miễn phí.
> 6. **Bối cảnh:** Bỏ qua phần chỉ phục vụ ngữ cảnh dược phẩm/pháp lý Mỹ (HIPAA/FDA/ICH-CSR) khi không liên quan ngoại trú VN; ưu tiên guideline quốc tế mới nhất rồi hiệu chỉnh theo Bộ Y tế VN.
>
> Phần kỹ thuật chi tiết (template, script, references) giữ nguyên tiếng Anh nhưng phải tạo ra **đầu ra tiếng Việt** theo các quy tắc trên.
"""


def split_frontmatter(text):
    """Trả về (dòng frontmatter, chỉ số dòng kết thúc '---', danh sách dòng)."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, None, lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], i, lines
    return None, None, lines


def replace_description(fm_lines, vi_desc):
    """Thay (các) dòng `description:` trong frontmatter bằng mô tả tiếng Việt 1 dòng."""
    out = []
    i = 0
    replaced = False
    while i < len(fm_lines):
        line = fm_lines[i]
        if line.startswith("description:"):
            # Bỏ qua các dòng tiếp theo thuộc về description (nếu description nhiều dòng)
            i += 1
            while i < len(fm_lines):
                nxt = fm_lines[i]
                # dòng key mới (vd "name:", "metadata:") thì dừng
                if nxt[:1] not in (" ", "\t") and ":" in nxt.split(" ")[0]:
                    break
                if nxt.strip() == "":
                    break
                i += 1
            # description tiếng Việt, escape dấu " bằng cách dùng nháy đơn YAML
            safe = vi_desc.replace("'", "''")
            out.append(f"description: '{safe}'\n")
            replaced = True
            continue
        out.append(line)
        i += 1
    return out, replaced


def process(skill_dir):
    skill = skill_dir.name
    md = skill_dir / "SKILL.md"
    if not md.exists() or skill not in DESCRIPTIONS:
        return f"BỎ QUA {skill}"
    text = md.read_text(encoding="utf-8")
    fm, end_idx, lines = split_frontmatter(text)
    if fm is None:
        return f"LỖI frontmatter: {skill}"

    new_fm, ok = replace_description(fm, DESCRIPTIONS[skill])
    # dựng lại file
    head = "---\n" + "".join(new_fm) + "---\n"
    body = "".join(lines[end_idx + 1:])

    guard = GUARD.format(marker=MARKER)
    if MARKER in text:
        # đã có guard -> chỉ cập nhật frontmatter, giữ guard cũ
        # tách guard cũ khỏi body để tránh nhân đôi
        body_lines = body.splitlines(keepends=True)
        # bỏ block guard cũ: từ dòng chứa MARKER tới dòng trống đầu tiên sau block
        cleaned = []
        skip = False
        for ln in body_lines:
            if MARKER in ln:
                skip = True
                continue
            if skip:
                if ln.strip() == "" or not ln.startswith(">"):
                    skip = False
                    if ln.strip() == "":
                        continue
                else:
                    continue
            cleaned.append(ln)
        body = "".join(cleaned)

    new_text = head + "\n" + guard + "\n" + body
    md.write_text(new_text, encoding="utf-8")
    return f"OK {skill} (description {'đã thay' if ok else 'KHÔNG thấy'})"


if __name__ == "__main__":
    for d in sorted(HUB.iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            print(process(d))
