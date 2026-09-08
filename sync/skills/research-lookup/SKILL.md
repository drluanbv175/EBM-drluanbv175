---
name: research-lookup
description: Tra cứu NGHIÊN CỨU & ĐĂNG KÝ THỬ NGHIỆM qua nguồn mở — ClinicalTrials.gov (API v2), WHO ICTRP, PROSPERO. Dùng khi cần kiểm một thử nghiệm đã đăng ký chưa, tìm nghiên cứu đang tiến hành/đã hoàn tất, đối chiếu kết cục đăng ký vs công bố (chống outcome switching), hoặc tra đăng ký tổng quan hệ thống. Trả mã đăng ký (NCT/ISRCTN/PROSPERO ID). KHÔNG bịa mã/đăng ký.
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


# Skill: Tra cứu nghiên cứu & đăng ký thử nghiệm (research-lookup)

Dùng cho `thu-thu-tai-lieu`, `tra-cuu-chung-cu`. Bổ trợ `paper-lookup` (bài báo) — skill này lo phần **đăng ký nghiên cứu**.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG bịa mã đăng ký/NCT/PROSPERO ID.** Chỉ nêu sau khi tra ra; không tra được → ghi rõ.
- Đối chiếu **kết cục đăng ký vs kết cục công bố** để cảnh báo outcome switching — chỉ nêu khi có bằng chứng.
- Connector lỗi → PARTIAL.

## Nguồn mở dùng được
- **ClinicalTrials.gov API v2** — `https://clinicaltrials.gov/api/v2/studies?query.term=...` (JSON; lọc theo điều kiện, pha, trạng thái; trả NCT ID, kết cục, ngày). API công khai, miễn phí.
- **WHO ICTRP** — cổng tìm `https://trialsearch.who.int/` (gộp nhiều registry: ISRCTN, ANZCTR, CTRI…). *Lưu ý:* ICTRP **không có REST API JSON ổn định công khai** — tra qua giao diện web/xuất file; ghi rõ nguồn + ngày, KHÔNG bịa endpoint.
- **PROSPERO** (đăng ký tổng quan hệ thống) — `https://www.crd.york.ac.uk/prospero/` — **không có API công khai**; tra bằng web search/giao diện; ghi rõ ID + ngày tra.

## Quy trình
**BƯỚC 0 — Tiền đề:** kiểm connector — thiếu → PARTIAL. Xác định cần: thử nghiệm can thiệp (ClinicalTrials/ICTRP) hay SR (PROSPERO).
1. **Dựng truy vấn:** bệnh/can thiệp/dân số + bộ lọc (pha, trạng thái, năm, quốc gia).
2. **Tra:** ClinicalTrials.gov API v2 trước (có JSON); bổ sung ICTRP/PROSPERO qua web nếu cần. Ghi **ngày tra**.
3. **Trích:** mã đăng ký (NCT/ISRCTN/PROSPERO), tiêu đề, trạng thái, pha, kết cục chính đăng ký, ngày, nhà tài trợ.
4. **Đối chiếu (nếu có bài công bố):** kết cục/thời điểm đăng ký vs công bố → cảnh báo lệch nếu có (nêu bằng chứng).

## Mẫu đầu ra
```
Truy vấn + nguồn + ngày tra: ____
| Mã đăng ký | Tiêu đề | Trạng thái/Pha | Kết cục chính (đăng ký) | Nguồn |
Cảnh báo outcome switching (nếu có + bằng chứng): ____
[⚠ PARTIAL — nguồn chưa tra: ____]
```
Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG soạn hồ sơ đăng ký (việc của agent `dao-duc-dang-ky`); KHÔNG thẩm định chất lượng. Chỉ TRA + XÁC MINH đăng ký. Nguồn không có API → tra web, ghi rõ, KHÔNG bịa endpoint/ID.
