# Giao thức gọi CRITIC ngoài phiên (subagent tách) — `tham-dinh-dau-ra`

> **[PROTOTYPE — cần cài deps/môi trường hỗ trợ subagent + BS duyệt governance trước khi coi là chốt kiểm thật]**
> Tài liệu này MÔ TẢ cách gọi `tham-dinh-dau-ra` như một **phiên Claude THỨ HAI** (ngữ cảnh tách) khi runtime hỗ trợ (Claude Code / Cowork có **Task tool / subagent**). Phần phụ thuộc runtime được đánh dấu **[CẦN MÔI TRƯỜNG HỖ TRỢ]** — KHÔNG khẳng định đã tự động.

## 1. Vì sao "ngữ cảnh tách" — và giới hạn thẳng thắn
- **Lợi:** phiên tách KHÔNG mang theo ngữ cảnh/quán tính của phiên soạn gói → **giảm mù chung (shared blind spots)**: critic không ""biết" lý do tác giả bỏ qua một bước, nên dễ bắt thiếu sót hơn self-check nội phiên.
- **GIỚI HẠN CỐT LÕI:** vẫn là **CÙNG HỌ MÔ HÌNH** → **GIẢM, KHÔNG KHỬ** thiên lệch hệ thống (cùng điểm mù kiến trúc, cùng xu hướng tự tin sai). Đây KHÔNG phải kiểm định độc lập bằng bộ máy khác họ/người khác. **[CẦN MÔI TRƯỜNG HỖ TRỢ]** để thật sự có phiên tách; nơi không có Task tool thì rơi về self-check nội phiên (yếu hơn — ghi rõ).

## 2. Luồng gọi (khi môi trường hỗ trợ subagent / Task tool)
```
Nhạc trưởng (dieu-phoi-lam-sang | dieu-phoi-nghien-cuu)
  └─ soạn xong GÓI NHÁP + tự-rà nội phiên
       └─ [CẦN MÔI TRƯỜNG HỖ TRỢ] gọi Task tool → subagent "tham-dinh-dau-ra(-standalone)"
            • Input  = chỉ BẢN_NHÁP (+ LOẠI, CỔNG nếu biết)   ← ngữ cảnh TÁCH
            • Output = khối R1–R7 (+ Q1–Q7 nếu lâm sàng) + PHÁN ĐỊNH + danh sách 🔴
       └─ nếu TRẢ-VỀ-SỬA → giao lại agent phụ trách → lặp đến ĐẠT
  └─ chỉ phát hành cho bác sĩ khi PHÁN ĐỊNH = ĐẠT (vẫn dừng Cổng A/B hoặc G2/G4)
```

## 3. Hợp đồng I/O (máy đọc được)
- **Đầu vào bắt buộc:** `BẢN_NHÁP` (toàn văn). Tùy chọn: `LOẠI` (lâm sàng|nghiên cứu), `CỔNG/BƯỚC`.
- **Đầu ra cố định:** bảng R1–R7 (+ Q1–Q7 Med-PaLM nếu LOẠI=lâm sàng; mỗi mục ✅/🟡/🔴 + trích vị trí) → `PHÁN ĐỊNH:` → `DANH SÁCH 🔴` → cờ chuyển bác sĩ (Q2/Q5 đỏ) → `"Cần bác sĩ kiểm chứng."`
- Spec đầy đủ: `tham-dinh-dau-ra.standalone.md` (cùng thư mục).

## 4. Cách gọi cụ thể theo môi trường
- **Claude Code / Cowork có subagent:** nhạc trưởng phát một lệnh Task tool, subagent_type ≈ general/critic, prompt = nội dung `tham-dinh-dau-ra.standalone.md` + khối `BẢN_NHÁP=<dán gói>`. [CẦN MÔI TRƯỜNG HỖ TRỢ]
- **Phiên Claude rời (thủ công):** bác sĩ mở một phiên MỚI, dán toàn bộ `tham-dinh-dau-ra.standalone.md` rồi dán `BẢN_NHÁP`. Đây là cách chắc chắn có "ngữ cảnh tách" nhất hiện nay, không phụ thuộc runtime.
- **Không có subagent:** rơi về self-check nội phiên trong chính nhạc trưởng (khối bắt buộc đã có sẵn) — ghi rõ "chưa chạy ở phiên tách".

## 5. Bất biến governance
- Critic CHỈ kiểm, không sửa hộ, không tạo nội dung mới, KHÔNG PII.
- Critic ĐẠT **không** = được áp dụng cho BN: vẫn dừng **Cổng A/B** (lâm sàng) hoặc **G2/G4/liêm chính tác giả** (nghiên cứu) chờ **bác sĩ** duyệt.
- Mọi đầu ra kết: **"Cần bác sĩ kiểm chứng."**
