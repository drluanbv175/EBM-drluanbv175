# PATCH — 1 dòng khuyến nghị critic ngoài phiên cho 2 nhạc trưởng

> **VÌ SAO LÀ PATCH (không sửa trực tiếp):** trong phiên dựng prototype này, thư mục `.claude/agents/` bị
> **khóa ghi** (đúng tinh thần governance "không đụng agent thật"). Hai dòng dưới đây để **bác sĩ tự dán**
> vào file thật khi muốn kích hoạt — đây là thay đổi prompt nên cần BS duyệt (nhất quán với rào auto-prompt).
> Cả hai chỉ THÊM 1 dòng cạnh khối chặn cứng đã có; KHÔNG đổi logic, KHÔNG thêm agent mới.

## 1) `.claude/agents/dieu-phoi-lam-sang.md`
Chèn dòng sau **ngay dưới** đoạn mở khối (sau dòng "…`_KIEM-DUYET-DOC-LAP.md`." ở §"🛡️ KẾT QUẢ THẨM ĐỊNH ĐẦU RA", ~dòng 62), TRƯỚC khối "⛔ CHẶN PHÁT HÀNH":

```markdown
> 🔎 **Khuyến nghị (khi môi trường hỗ trợ):** chạy `tham-dinh-dau-ra` ở **subagent/phiên TÁCH** (ngữ cảnh độc lập) để đối kháng mạnh hơn self-check nội phiên — dùng bản `tools/critic/tham-dinh-dau-ra.standalone.md`, quy trình `tools/critic/critic-protocol.md`. Đây là **[CẦN MÔI TRƯỜNG HỖ TRỢ]** (giảm mù chung, KHÔNG khử thiên lệch — cùng họ mô hình); nơi không có subagent thì giữ self-check nội phiên như cũ.
```

## 2) `.claude/agents/dieu-phoi-nghien-cuu.md`
Chèn dòng tương tự **ngay dưới** đoạn mở khối (~dòng 105), TRƯỚC khối "⛔ CHẶN PHÁT HÀNH":

```markdown
> 🔎 **Khuyến nghị (khi môi trường hỗ trợ):** chạy `tham-dinh-dau-ra` ở **subagent/phiên TÁCH** (ngữ cảnh độc lập) cho gói bàn giao — dùng `tools/critic/tham-dinh-dau-ra.standalone.md`, quy trình `tools/critic/critic-protocol.md`. **[CẦN MÔI TRƯỜNG HỖ TRỢ]** (giảm mù chung, KHÔNG khử thiên lệch); không có subagent → giữ self-check nội phiên.
```

## Kiểm sau khi dán
- Không thêm/bớt agent .md → số đếm vẫn 37.
- Khối "⛔ CHẶN PHÁT HÀNH" và rubric 2 lớp (R1–R7 + Q1–Q7 Med-PaLM cho gói lâm sàng) giữ nguyên.
- Dòng mới chỉ là **khuyến nghị có điều kiện**, không phải bắt buộc runtime (tránh tuyên bố sai "đã tự động").
