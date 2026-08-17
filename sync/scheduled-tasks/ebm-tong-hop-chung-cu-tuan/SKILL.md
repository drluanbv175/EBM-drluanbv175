---
name: ebm-tong-hop-chung-cu-tuan
description: Giám sát ứng viên chứng cứ/thử nghiệm 8 bệnh mạn (Track B, chưa thẩm định) — Chủ nhật 20:00
---

Bạn đang chạy ROUTINE GIÁM SÁT ỨNG VIÊN CHỨNG CỨ tuần (Track B) cho BS Luân — tự động, KHÔNG hỏi lại, mặc định an toàn, append-only, KHÔNG bịa thử nghiệm/PMID/DOI, KHÔNG PII.

BƯỚC 1 — Đọc và thực thi ĐÚNG file routine canonical (nguồn sự thật duy nhất):
`/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI/Scheduled/tong-hop-chung-cu-hang-tuan/SKILL.md`
Quét ClinicalTrials.gov + y văn cho 8 bệnh mạn ngoại trú, ra DANH SÁCH ỨNG VIÊN chưa thẩm định (Track B — KHÔNG tự gán GRADE/độ mạnh, KHÔNG kết luận đổi thực hành).

BƯỚC 2 — Tuân chuẩn wiring dùng chung `.claude/agents/_ROUTINE-AGENT-WIRING.md` + hiến pháp liêm chính `.claude/agents/_HIEN-PHAP-LIEM-CHINH.md`. Với chủ đề có ứng viên đáng giá, gợi ý bác sĩ chạy skill `cap-nhat-chung-cu-y-khoa` (Track A) để thẩm định đầy đủ.

BƯỚC 3 — Ghi sổ cái đúng quy trình routine; backup trước khi ghi.

BƯỚC 4 — GUARDRAIL ĐẦU RA (bắt buộc): gọi agent `tham-dinh-dau-ra` soi gói theo 2 LỚP — Lớp 1 LIÊM CHÍNH R1–R7 + Lớp 2 CHẤT LƯỢNG Med-PaLM Q1–Q7; còn lỗi đỏ → TRẢ-VỀ-SỬA; Q2/Q5 đỏ → chuyển bác sĩ.

Nếu subagent không gọi được trong phiên nền, tự thực hiện theo đặc tả file canonical. Kết luận: "Đây là danh sách ứng viên giám sát — chưa thẩm định, KHÔNG thay phán đoán lâm sàng. Cần bác sĩ kiểm chứng." Chạy trên MỘT máy (Mac) để tránh xung đột OneDrive.