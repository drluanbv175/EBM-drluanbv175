# PROMPT PHA R2 — VỀ ĐÍCH G10: đề tài synthetic đi TRỌN chuỗi cổng (tự soạn 15/08/2026)

Nối PHA R (đã tới G5-từ-chối-đúng-thiết-kế). Đề tài `ZZPHA-R-AUTO-DEMO`
(`synthetic_test`, mọi chữ ký ghi danh DEMO-SYNTHETIC-ADMIN).

**Bất biến:** không nới cổng; nội dung demo phải THOẢ luật nội dung của từng
quality-gate (không sửa luật cho dễ đậu); dữ liệu TỔNG HỢP sinh máy, ghi rõ; mỗi
trạm kẹt là một PHÁT HIỆN về ma sát vận hành — ghi lại làm bài học cho đề tài thật.

R2-1 SAP: điền hết placeholder theo đúng đòi hỏi G4-AUTO (seed nguyên · phần mềm
 +phiên bản · imputation · §7 subgroup) → `PASS_G4_SAP_LOCKED` (ledger đã ký).
R2-2 G5: sinh CSV tổng hợp đúng codebook → khoá dữ liệu → ký admin → LOCKED.
R2-3 G6: sinh script từ SAP + CSV → `g6_quality_gate` MỚI chấm lần đầu trên đề
 tài sống (kỳ vọng khớp seed/alpha/kết cục — chính là phép thử tích hợp của R1).
R2-4 G6.5→G7: kết quả + bản thảo draft.
R2-5 G8→G9→G10: ký admin từng cổng + `run_g10_assemble` ra GÓI; mọi quality
 report lưu trong exports/.
R2-6 Báo cáo: bảng 11 cổng × trạng thái cuối + danh sách MA SÁT vận hành đã gặp
 (giá trị thật cho đề tài thật đầu tiên của bác sĩ) + commit.
