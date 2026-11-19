# 19/11/2026 — Kiểm toàn diện hệ nghiên cứu: 4 lỗi máy bộ phán CI không thấy

**Bối cảnh.** Bác sĩ giao «kiểm tra toàn diện hệ thống nghiên cứu, giả lập toàn diện các đề tài». Đo trên mã mới nhất:
- 24 đề tài giả lập chạy trọn G0→G10: cả 24 khoá được gói G10, 0 ô lỗi máy;
- C1a, BTM;
- các bộ kiểm chung.

Mọi bộ phán đều xanh, vậy mà đọc chi tiết từng bước vẫn ra 4 lỗi thật.

**Lỗi.**
1. **7 «lỗi chặn» DOI giả.** `verify_exports_integrity` quét đủ báo `EXP-DOI-FORMAT` ở `kiem_may_api/` của C1a/BTM. Thủ phạm là câu ghi chú cố định «bài chỉ có DOI: Europe PMC/Crossref» của `kiem_tong_quan_g0_api` / `kiem_noi_dung_trich_dan`, bị luật «doi:» đọc thành DOI sai. Hệ quả: commit thư mục này sẽ bị chặn oan.
2. **Hai luật ngược nhau.** K8 cấm «Cần bác sĩ kiểm chứng» trong đề cương nộp, nhưng `EXP-NO-DISCLAIMER` lại cảnh báo khi đề cương nộp thiếu đúng câu đó.
3. **SPSS từ chối biến phân loại.** `cau_noi_spss` chặn theo TÊN cột với trường phân loại có mã (`tc_dien_thoai`, kiểu yesno), trong khi cổng tiếp nhận, làm sạch và khoá đã miễn từ 17/11. Hệ quả: `xuat-sav` trả mã 3, nửa SPSS của kiểm chéo G6 bị «TU_CHOI» ở cả 5 phân tích (nửa R khớp 8/8). CI xanh vì kiểm chéo SPSS không phải điều kiện cổng.
4. **Bản sao `.Codex/agents` trên Mac lệch.** Hai PR gộp hôm nay có sửa agent nhưng bản sao trên máy chưa sinh lại. Hệ quả: `check_claude_codex_sync_health` FAIL, BH91 đỏ.

**Đã vá.**
- PR y khoa #334: lỗi 1 và 2, kèm sửa đúng câu trong 7 báo cáo đã có.
- PR y khoa #335: lỗi 3.
- Lỗi 4: sinh lại bản sao. Đo lại thì bộ chốt 182/182.

Mỗi bản vá có test, và kiểm đột biến làm test đỏ.

**Bài học.** Bộ phán CI (`kiem_gia_lap_16`) chỉ phán khoá G10, ô lỗi máy và K1–K8. Mã thoát khác 0 của bước KHÔNG phải điều kiện cổng (kiểm chéo SPSS, quét liêm chính đủ) vẫn lọt. Mỗi lượt kiểm toàn diện phải đọc lại các bước có mã khác 0 trong `state/gia-lap-tron-vong/*.json`.
