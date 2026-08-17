---
name: ebm-antifacts-weekly
description: Digest EBM 13 chuyên khoa (PubMed 7 ngày) + rà phiên bản thang điểm/guideline cho Antifacts — Thứ 2 07:00
---

Bạn đang chạy ROUTINE ANTIFACTS WEEKLY cho BS Luân — tự động, KHÔNG hỏi lại, mặc định an toàn, append-only, KHÔNG bịa, KHÔNG PII.

BƯỚC 1 — Đọc và thực thi ĐÚNG file routine canonical (nguồn sự thật duy nhất):
`/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI/Scheduled/antifacts-weekly-ebm/SKILL.md`
Quét chứng cứ mới 13 chuyên khoa (PubMed 7 ngày) + rà soát phiên bản thang điểm/guideline cho dashboard "Antifacts Live" (`tools/build_antifacts.py`).

⚠️ Lưu ý còn treo (CẦN BÁC SĨ QUYẾT — chưa tự ý giải quyết): có thư mục trùng nội dung `Scheduled/antifacts-weekly-update` (tên cũ hơn, SKILL.md gần như y hệt). Routine này đăng ký theo tên đã chuẩn hoá `antifacts-weekly-ebm` (theo `_BAN-DO-KET-NOI.md` §8); nếu bác sĩ quyết định hợp nhất/xoá bản trùng, chỉ cần sửa đường dẫn canonical ở BƯỚC 1 — KHÔNG tự hợp nhất mà không hỏi.

BƯỚC 2 — Tuân chuẩn wiring dùng chung `.claude/agents/_ROUTINE-AGENT-WIRING.md` + hiến pháp liêm chính `.claude/agents/_HIEN-PHAP-LIEM-CHINH.md`. KHÔNG tự đổi ngưỡng thang điểm — chỉ đề xuất.

BƯỚC 3 — Ghi sổ cái đúng quy trình routine; backup trước khi ghi.

BƯỚC 4 — GUARDRAIL ĐẦU RA (bắt buộc): gọi agent `tham-dinh-dau-ra` soi gói theo 2 LỚP — Lớp 1 LIÊM CHÍNH R1–R7 + Lớp 2 CHẤT LƯỢNG Med-PaLM Q1–Q7; còn lỗi đỏ → TRẢ-VỀ-SỬA; Q2/Q5 đỏ → chuyển bác sĩ.

Nếu subagent không gọi được trong phiên nền, tự thực hiện theo đặc tả file canonical. Kết "Cần bác sĩ kiểm chứng." Chạy trên MỘT máy (Mac) để tránh xung đột OneDrive.