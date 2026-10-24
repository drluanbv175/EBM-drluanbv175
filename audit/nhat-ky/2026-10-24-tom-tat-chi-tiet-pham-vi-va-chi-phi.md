# 24/10/2026 — Tóm tắt chứng cứ: chỉ T1 đọc toàn văn; T2/T3/T4 tóm tắt từ abstract; agent lỗi bị đếm nhầm «chưa đạt»

**Quyết định của bác sĩ (24/10, chiều).** «…với những chứng cứ áp dụng cho thực hành lâm sàng có độ tin cậy cao nhất và mới nhất hãy
hoàn thiện đầy đủ (toàn văn và tóm tắt) còn với những chứng cứ chưa đạt chuẩn thì hãy tóm tắt tiếng việt một cách chi tiết vào phần
Abstract của trích dẫn» — chọn «Chỉ T1» và «Từ abstract gốc, có cổng số liệu»; tiếp đó «nhớ luôn phải tải toàn văn».

**Số đo chi phí (để quyết lần sau).** Workflow T1 (viết → kiểm chéo độc lập → sửa ≤3 vòng): lượt 1 ≈ 54 triệu token cho ≈ 55 bài, lượt 2
≈ 64 triệu; ≈ 0,7 triệu token/bài. Hai lần chạm trần chi tiêu tháng giữa lượt. Tóm tắt từ abstract ≈ 10 nghìn token/bài.

**Lỗi phân loại trong kịch bản workflow.** Agent kiểm chéo lỗi (trần chi tiêu, TLS tự ký, DNS) trả `null` ⇒ `so_sai = null` ⇒ kịch bản
xếp «chua_dat» như bài sai thật (lượt 1: 6 bài, lượt 2: 9 bài). Đọc kết quả workflow phải tách `so_sai is None` (agent lỗi — chạy lại)
khỏi `so_sai > 0` (sai thật). Chạy lại bằng `resumeFromRunId`: agent đã xong phát lại từ bộ nhớ đệm, chỉ agent lỗi chạy lại; thêm mục
mới ở CUỐI danh sách không làm lệch bộ nhớ đệm.

**Đã nối vào hệ thống.**
- `tom_tat_endnote_vi.py` (#242): kho thêm `han_che`, `ket_luan`; tóm tắt máy cho mục chính (dưới khối đã qua cổng, dòng chân riêng);
  `--tom-tat-thu-vien` cho bài ngoài dashboard.
- `tom_tat_chung_cu_word.py ngoai-le-moc --tang 1` (thu ngoại lệ mốc từ T1+T2 về T1).
- CLAUDE.md §6.2 (câu EndNote) cập nhật phạm vi + luật luôn gom toàn văn.
- Bộ nhớ: `tom-tat-chi-tiet-ban-ghi-cu-t1-t2`, `luon-tai-toan-van-moi-trich-dan`.

Cần bác sĩ kiểm chứng.
