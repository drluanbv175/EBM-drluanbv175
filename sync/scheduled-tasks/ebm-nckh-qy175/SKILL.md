---
name: ebm-nckh-qy175
description: Rà soát đồng bộ hồ sơ đề tài QY175 (uỷ thác cụm Agent NC) — chạy tay (ad-hoc)
---

Bạn đang chạy ROUTINE RÀ SOÁT ĐỒNG BỘ HỒ SƠ NGHIÊN CỨU (đề tài QY175 — hài lòng người bệnh, BV Quân y 175) cho BS Luân — tự động, KHÔNG hỏi lại, KHÔNG bịa, KHÔNG PII. Đây là routine AD-HOC (chạy tay khi bác sĩ yêu cầu), không tự lên lịch.

BƯỚC 1 — Đọc và thực thi ĐÚNG file routine canonical (nguồn sự thật duy nhất):
`/Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI/Scheduled/nckh/SKILL.md`
Ủy thác cho cụm Agent Nghiên cứu theo cổng G0–G9, gác cổng bởi `dieu-phoi-nghien-cuu`: `viet-ban-thao`/`binh-duyet` (văn bản), `quan-ly-du-lieu` (CRF/data dictionary), `dao-duc-dang-ky` (G2), `thiet-ke-nghien-cuu`+`co-mau-nghien-cuu` (thiết kế/cỡ mẫu), `phan-tich-thong-ke` (sau khóa dữ liệu).

BƯỚC 2 — Tuân chuẩn `.claude/agents/_ROUTINE-AGENT-WIRING.md` + `_HIEN-PHAP-LIEM-CHINH.md`. KHÓA BẮT BUỘC: tên đề tài + 02 mục tiêu chính thức KHÔNG đổi; Giai đoạn 1 CHỈ rà soát, CHƯA sửa/CHƯA xuất file khi chủ nhiệm chưa phê duyệt (cổng người duyệt của routine).

BƯỚC 3 — KIỂM TOÁN ĐẦY ĐỦ (bắt buộc trước khi tuyên bố "xong"): đối chiếu hồ sơ với `.claude/agents/_KIEM-TOAN-DAY-DU-NGHIEN-CUU.md` (đề tài = cắt ngang phân tích); nêu rõ artifact 🔴 còn thiếu. KHÔNG kết luận hồ sơ hoàn chỉnh khi còn 🔴 bắt buộc.

GUARDRAIL: chốt kiểm chính = `_KIEM-TOAN-DAY-DU-NGHIEN-CUU.md`; khi xuất bản thảo/sản phẩm cho chủ nhiệm thì thêm `tham-dinh-dau-ra` (Lớp 1 LIÊM CHÍNH R1–R7; gói nghiên cứu KHÔNG áp Lớp 2 Med-PaLM) trước khi giao.

Nếu subagent không gọi được trong phiên nền, tự làm theo đặc tả file.