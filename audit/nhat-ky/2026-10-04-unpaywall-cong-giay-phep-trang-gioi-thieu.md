# 04/10/2026 — Tầng 2 Unpaywall lưu bản không giấy phép mở và trang giới thiệu kho lưu trữ; sổ phủ chỉ đếm XML (BH160)

**Bối cảnh.** Bác sĩ hỏi: việc hoàn thiện nguồn chứng cứ đã bảo đảm phủ đầy đủ và đọc toàn văn chưa. Lượt đo sống
`EBM-Dashboards/toan_van_oa/` cho câu trả lời bằng số, không trích số cũ. Lượt này lộ ba lỗi của
`tools/gom_toan_van_dashboard.py`.

**Lỗi 1 — tầng 2 không xét giấy phép hay điều khoản NXB.**
- `tang_unpaywall` lưu mọi `best_oa_location` có `is_oa`.
- Đo 04/10: 32/42 tệp `_UPW` trong kho không mang giấy phép mở.
  - 25 tệp của NXB «cấm» (NEJM, JAMA, Elsevier, Wiley, OUP, Springer, ADA…) — uỷ quyền 03/10 của bác sĩ là uỷ quyền ĐỌC, ghi rõ
    «KHÔNG lưu toàn văn»;
  - 7 tệp của NXB chưa kiểm điều khoản (ASM, CHEST, Taylor & Francis, Thieme, RSNA, Clin Exp Rheumatol).
- Vá — `quyet_dinh_unpaywall`, xét TRƯỚC khi mở nội dung:
  - chỉ LƯU TỰ ĐỘNG bản mang giấy phép mở (CC BY*, CC0, phạm vi công cộng);
  - bản không giấy phép mở không lưu. Lý do được phân loại để định tuyến: «cam_co_uq» → làn trình duyệt có phiên uỷ quyền lưu bản
    sao; «cam_khong_uq» → bác sĩ đọc trực tiếp; «chua_kiem» → đọc trang điều khoản trước;
  - không nạp được bảng điều khoản ⇒ đóng.

**Lỗi 2 — trang giới thiệu kho lưu trữ được tính là «toàn văn».**
- Cổng nội dung cũ chỉ đòi ≥ 500 từ. Trang Pure/Research Explorer của kho đại học (tóm tắt + metadata + nút tải) vượt ngưỡng đó.
- Đo 04/10: 15/27 tệp `_UPW.html` là loại này. Trong đó có 4 mục apply: CHA₂DS₂-VASc 19762550, HAS-BLED 20299623, EMPOWER 24733354,
  SUMMIT 27203508.
- Hệ quả: phủ toàn văn mục apply thật là 140/160, không phải 144/160.
- Vá — `la_toan_van_html`:
  - toàn văn khi ≥ 3 đề mục IMRaD và ≥ 2500 từ, hoặc ≥ 6000 từ (guideline dài không có IMRaD, vd Tiêu chuẩn ADA 18–26 nghìn từ);
  - mang dấu trang kho («Fingerprint», «Access to Document», «Link to publication»…) mà dưới 6000 từ ⇒ không phải toàn văn.
- Trên 27 tệp thật: nhận 12, loại 15, khớp kiểm tay.

**Lỗi 3 — sổ phủ chỉ đếm `*.xml`.**
- `DO-PHU-OA.md` báo «203/676», trong khi 337/676 PMID đã có toàn văn hoặc đã được đọc toàn văn qua làn trình duyệt.
- Vá — `dem_toan_van`:
  - đếm mọi loại tệp ở gốc kho cùng `trinh_duyet/`, báo theo loại;
  - không đếm `doc_sau/` (ghi chú đọc sâu, không phải toàn văn);
  - liệt kê bài bị cổng điều khoản chặn kèm lý do.

**Kiểm:**
- `tools/test_gom_unpaywall_cong_20261004.py`: 18 test ngoại tuyến (mạng giả, bảng điều khoản giả).
- Đột biến 5/5 làm test đỏ đúng chỗ.
- BH160 kiểm HÀNH VI. Đột biến 6/6 làm BH160 đỏ. Lần đầu M4 lọt vì mẫu trang giới thiệu thiếu đề mục IMRaD, tức đã bị loại sẵn. Đã
  thay bằng mẫu giống ca thật SUMMIT: tóm tắt có cấu trúc > 2500 từ.

**Chưa làm (việc dữ liệu, chờ bác sĩ):**
- 15 tệp trang giới thiệu vẫn nằm trong kho và còn làm sai số phủ của các công cụ quét `PMID-*`.
- 32 tệp không giấy phép mở do tầng 2 cũ lưu: bác sĩ quyết giữ (theo uỷ quyền thường trực 04/10) hay chuyển ra khỏi kho.
- Hai lịch nền (`weekly_safety.sh` bước 5, gói tuần bước 4b) chỉ dùng tầng PMC Open Access ⇒ không chạm lỗi 1–2. Lỗi chỉ xảy ra khi
  skill `tong-thuat-chung-cu` bật `--unpaywall`.
