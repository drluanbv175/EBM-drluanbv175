---
name: research-lookup
description: Tra cứu NGHIÊN CỨU & ĐĂNG KÝ THỬ NGHIỆM qua nguồn mở — ClinicalTrials.gov (API v2), WHO ICTRP, PROSPERO. Dùng khi cần kiểm một thử nghiệm đã đăng ký chưa, tìm nghiên cứu đang tiến hành/đã hoàn tất, đối chiếu kết cục đăng ký vs công bố (chống outcome switching), hoặc tra đăng ký tổng quan hệ thống. Trả mã đăng ký (NCT/ISRCTN/PROSPERO ID). KHÔNG bịa mã/đăng ký.
---

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
