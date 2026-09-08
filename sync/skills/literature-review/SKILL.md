---
name: literature-review
description: Quy trình TỔNG QUAN Y VĂN HỆ THỐNG theo PRISMA 2020 — câu hỏi PICO → đăng ký PROSPERO → chiến lược tìm tái lặp → sàng lọc (sơ đồ dòng chảy) → trích xuất → đánh giá nguy cơ sai lệch → tổng hợp định tính/meta + GRADE. Dùng khi cần làm tổng quan hệ thống đầy đủ, tái lặp, cho công bố/đề tài. Chỉ nguồn miễn phí; mỗi bài kèm PMID/DOI; ghi ngày tra + CSDL.
---

<!-- EBM-VN-GUARD -->
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


# Skill: Tổng quan y văn hệ thống (literature-review)

Dùng cho `tong-quan-y-van`, `thu-thu-tai-lieu`. Khung chuẩn **PRISMA 2020**.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG bịa trích dẫn**; mỗi bài kèm **PMID/DOI** đã kiểm; ghi **ngày tra + CSDL** để tái lặp.
- CHỈ nguồn miễn phí (PubMed/PMC, Europe PMC, Cochrane CENTRAL/CDSR nếu truy cập được, OpenAlex, Crossref, bioRxiv/medRxiv — ghi "tiền ấn phẩm").
- Đăng ký PROSPERO **TRƯỚC sàng lọc** để chống thay đổi hồi tố; đăng ký muộn → ghi rõ. Connector lỗi → PARTIAL.

## Quy trình PRISMA 2020
**BƯỚC 0 — Tiền đề:** kiểm connector; xác định đây là SR chính thức → đăng ký PROSPERO; đối chiếu xem đã có SR tương tự chưa.
1. **Câu hỏi & tiêu chí:** PICO/PECO; tiêu chí nhận/loại; loại thiết kế.
2. **Đăng ký PROSPERO:** câu hỏi, tiêu chí, chiến lược tìm, phương pháp tổng hợp, kết cục.
3. **Chiến lược tìm:** chuỗi tìm nguyên văn cho TỪNG CSDL (tái lặp) + ngày tra (dùng skill `paper-lookup`/`research-lookup`).
4. **Sàng lọc:** lưu số lượng từng bước → **sơ đồ dòng chảy PRISMA** (nhận diện → sàng lọc → đủ điều kiện → đưa vào); 2 người sàng độc lập nếu có (ghi κ đồng thuận).
5. **Trích xuất dữ liệu:** bảng đặc điểm (thiết kế, n, dân số, can thiệp, kết cục, hiệu ứng) — dùng skill trích xuất nếu có.
6. **Nguy cơ sai lệch:** RoB 2 (RCT)/ROBINS-I (quan sát)/QUADAS-2 (chẩn đoán)/AMSTAR-2 (SR).
7. **Tổng hợp:** định tính; nếu đồng nhất đủ → meta (skill `statistical-analysis`: pooled + I²/forest/funnel); **GRADE** Summary of Findings.

## Mẫu đầu ra
```
PICO + tiêu chí | PROSPERO: [ID / [CẦN BỔ SUNG] / đăng ký muộn]
Chiến lược tìm (mỗi CSDL + chuỗi + ngày tra): ____
Sơ đồ PRISMA: nhận diện __ → sàng lọc __ → đủ điều kiện __ → đưa vào __
| Bài (PMID/DOI) | Thiết kế | n | Kết cục | Hiệu ứng (CI) | RoB |
GRADE SoF + khoảng trống/giới hạn (heterogeneity, publication bias)
[⚠ PARTIAL — CSDL chưa tra: ____]
```
Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG tự gộp số phức tạp (→ `statistical-analysis`); KHÔNG viết bản thảo (→ `scientific-writing`). Connector thiếu → PARTIAL, ghi rõ CSDL nào chưa tra.
