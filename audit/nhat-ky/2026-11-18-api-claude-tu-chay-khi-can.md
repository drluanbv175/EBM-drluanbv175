# 18/11/2026 — Cơ chế tự chạy API Claude khi cần

Bác sĩ: «Những vấn đề chưa tự động hãy xây dựng … cơ chế tự động giúp tôi».

**Bác sĩ chọn:**
- Việc được TỰ CHẠY (nguyên văn): «Khi hệ thống nghiên cứu y khoa và cập nhật chứng cứ cần, Quét lạc chủ đề phần đổi,
  Kiểm đề cương khi đổi, CAFÉ-S khi agent an toàn đổi».
- Trần chi tiêu: «Tôi đã cài đặt trên Claude Console».

Lời duyệt được ghi vào `sync/api-khi-can.json`.

## Trước khi xây — đo, không đoán

| Công cụ dùng API | Trước 18/11 |
|---|---|
| Cổng kiểm lạc chủ đề | Tự động trong mỗi lượt xuất gói `--online` |
| Quét lạc chủ đề toàn kho | Tay; ~2 USD/lượt; chấm lại cả 114 dashboard dù không đổi |
| Kiểm máy đề cương (A12, phản biện máy) | Tay; ~0,15 + 0,13 USD/đề tài |
| CAFÉ-S | Tay; ~2–4 USD/lượt |
| Hội đồng cổng, ambient scribe, đọc ảnh | Cố ý giữ tay — triệu tập hội đồng phải hỏi bác sĩ; dữ liệu từng ca |

**Phiên song song:**
- Repo gốc #421 (đã gộp) và repo y khoa #306 (mở) đã làm phần phát hiện «báo cáo kiểm máy cũ» (`duyet_kiem_may_api.py`)
  và trần chi phí tháng trong cầu nối y khoa.
- Cơ chế này DÙNG LẠI công cụ đó, không viết bộ phát hiện thứ hai.
- Trước khi #306 gộp, việc «kiểm đề cương» báo ⚪ (không đo được), không đọc thành «không có việc».

## Xây

**`tools/api_khi_can.py`** — một lối vào cho ba việc:
- **Quét lạc chủ đề phần đổi:**
  - Phạm vi: bản mới nhất của mỗi chủ đề.
  - Phát hiện «đổi»: vân tay = sha256 của ĐÚNG prompt mà cổng gửi (chủ đề + id · tiêu đề · hành động), so với sổ
    `~/.ebm-kiem-chu-de.json`. Sổ do CHÍNH cổng ghi, nên lượt chấm trong xuất gói và trong quét toàn kho đều tính.
  - Tệp chưa có trong sổ: lượt quét toàn kho gần nhất phủ được nếu tệp không sửa sau đó.
  - Chấm bằng chính cổng, tối đa 60 dashboard/lượt. Ba lỗi liền hoặc thiếu khoá ⇒ dừng.
  - Có mục nghi lạc ⇒ báo cáo `KIEM-CHU-DE-KHI-CAN_*.md` cho bác sĩ rà; máy không gỡ mục.
- **Kiểm đề cương khi đổi:**
  - Chỉ chạy lại báo cáo mà `duyet_kiem_may_api` KHẲNG ĐỊNH là cũ. «Không khẳng định được» không tự chi tiền.
  - Mã thoát 0/1 = chạy xong (1 = có phát hiện cần duyệt).
  - Chạm trần chi phí tháng của cầu nối y khoa ⇒ dừng.
- **CAFÉ-S khi agent an toàn đổi:** vân tay agent khác lượt đo gần nhất, và lượt đó cách ≥ 30 ngày.

**Hai lối kích hoạt:**
- Hook đầu phiên `--nen --im-khi-on`: chỉ đọc chính sách và sổ. Đủ 6 giờ từ lần xét trước ⇒ phóng `--chay` ở nền rồi trả
  lại ngay. Phiên Cloud không phóng.
- Bước 6b của tác vụ tháng `cap-nhat-thang-ebm`, đã khai quyền ở `sync/quyen-lich-nen.json`.

**Rào:**
- Chính sách vắng/hỏng/sai kiểu ⇒ TẮT HẲN.
- Khoá chống chạy chồng; coi là treo sau 3 giờ.
- Dưới pytest không gọi thật, không phóng nền, không đụng sổ thật (rào BH181).

**Hòm việc:**
- Giác quan mới ⑦u:
  - chính sách hỏng / chưa xét lần nào / quá 8 ngày không xét ⇒ ⚪;
  - lượt có việc lỗi ⇒ 👤;
  - báo cáo có mục nghi lạc ≤ 14 ngày ⇒ 👤.
- Hai giác quan CAFÉ-S và kiểm máy: chính sách cho tự chạy ⇒ 🛎 «máy sẽ tự chạy», không còn đòi bác sĩ quyết.
- Không báo trùng một việc ở hai giác quan.

## Đo

- **Phát hiện trên dữ liệu thật (miễn phí, 0,1 giây):**
  - đúng 4 dashboard sửa sau lượt quét toàn kho 17/11 (Đau đầu, VKDT thần kinh, VKDT tổng hợp, Viêm gan B), ước
    ~0,18 USD. 110 dashboard còn lại không chấm lại;
  - CAFÉ-S: agent chưa đổi;
  - đề cương: ⚪ chờ #306.
- **Test:**
  - `tools/test_api_khi_can_20261118.py`: 41 chốt, gồm 5 chốt ★ rào tiền.
  - Hai test cũ của giác quan được ghim chính sách «tắt» để vẫn khoá nhánh «chỉ báo», thêm test cho nhánh tự chạy.
- **Đột biến:** 22/22 bị bắt.
- Không tệp thật nào ở thư mục nhà bị tạo hay sửa sau lượt test.

## Sau khi gộp

1. `python3 tools/dong_bo_scanner_giam_sat.py --ap-dung` — đưa cổng có sổ vân tay tới hai bản chạy ngoài git.
2. Chép `sync/scheduled-tasks/cap-nhat-thang-ebm/SKILL.md` sang bản chạy của tác vụ (CLAUDE.md §9).
3. BÁC SĨ chạy (đổi cài đặt máy):
   - `python3 tools/dong_bo_hook_sessionstart.py --ap-dung` — hook đầu phiên;
   - `python3 tools/quyen_lich_nen.py --ap-dung` — quyền lượt lịch, gồm cả lệnh canary đang treo từ trước.
