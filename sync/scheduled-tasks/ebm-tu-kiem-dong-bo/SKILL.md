---
name: ebm-tu-kiem-dong-bo
description: Tự kiểm + tự sửa đồng bộ đội agent EBM (CN hằng tuần)
---

Bạn là routine TỰ KIỂM ĐỒNG BỘ đội agent EBM. Thư mục dự án: /Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/Claude AI (thư mục "Claude AI" trong OneDrive; nếu khác, liệt kê ~/Library/CloudStorage/ để tìm).

Đọc và thực thi ĐÚNG đặc tả: Scheduled/tu-kiem-dong-bo/SKILL.md.

Quy trình: vào .claude/agents → đọc _TU-SUA-CHUA-PROTOCOL.md + _BAN-DO-KET-NOI.md + _KIEM-TOAN-DAY-DU-NGHIEN-CUU.md → chạy BỘ KIỂM TỰ ĐỘNG (bash) trong protocol. TỰ SỬA chỉ các lệch AN-TOÀN–XÁC-ĐỊNH (đếm số agent ở README.md header + CLAUDE.md cho khớp số file *.md thật loại README/_; con trỏ còn thiếu; viết tắt tên agent→tên đầy đủ khi map 1-1) — backup .bak vào _archive/ TRƯỚC khi sửa, đọc lại xác minh. CHỈ BÁO CÁO (không tự sửa) lệch cần phán đoán: ngữ nghĩa/định tuyến/thêm-xóa agent/sửa description/tham chiếu treo nghi vấn/vi phạm cổng A-B-G/thiếu 4 trụ cột-disclaimer.

APPEND một khối kết quả vào Scheduled/tu-kiem-dong-bo/nhat-ky.md (ngày · kết quả bộ kiểm N/N · đã tự sửa gì kèm file · 🔴 cần bác sĩ · connector) — KHÔNG xóa/sửa khối cũ.

Liêm chính: tuân _HIEN-PHAP-LIEM-CHINH.md + _NGUYEN-TAC-TRUNG-THUC-BAO-MAT-PHAP-LY-LIEM-CHINH.md. KHÔNG bịa; KHÔNG PII; append-only + backup; chỉ tự sửa khi CHẮC CHẮN & ĐẢO NGƯỢC ĐƯỢC. Routine NỘI BỘ → dùng bộ kiểm trong protocol làm chốt, KHÔNG cần tham-dinh-dau-ra. Kết: "Cần bác sĩ kiểm chứng."