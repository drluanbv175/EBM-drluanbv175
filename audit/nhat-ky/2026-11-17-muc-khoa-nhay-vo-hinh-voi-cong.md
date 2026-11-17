# 17/11/2026 — 6 mục vô hình với cổng liêm chính 12 ngày vì viết khoá có nháy (BH182)

**Mã:** BH182 · cùng họ BH21/BH62 (parser là nơi lỗi an toàn ẩn), BH08 («không kiểm được» ≠ «đạt»).

## Phát hiện

Đang chuyển ITEM-62 từ `VKDT_TamThanKinh_20261113` sang `VKDT_TongHop_20261113` theo quyết định bác sĩ: «khối» ITEM-62 do
`split_items` tách dài 16.428 ký tự trong khi đối tượng thật chỉ 1.872 — vì sau nó còn 6 mục ITEM-63…68 viết kiểu JSON
`{"id": "ITEM-63", "title": …}` (thêm 05/11). `split_items` chỉ nhận `{id:` không nháy, nên 6 mục đó:

- vẫn HIỆN trên trang (trình duyệt đọc được kiểu nào cũng xong) và trong Word / bản đọc (bộ dựng Word có parser riêng);
- nhưng KHÔNG qua bất kỳ luật cấp mục nào của cổng (PMID có thật, DOI khớp PubMed, rút bài, `apply` trên chứng cứ yếu…),
  không có trong lượt quét lạc chủ đề 17/11, không có trong sổ cái hub — và cổng vẫn báo PASS suốt 12 ngày.

Đo toàn kho: 1/303 dashboard, 6 mục (2 `consider`, 4 `notyet`, không mục nào `apply`; cả 6 khai `gradeLevel: na`).

Suýt thêm một hậu quả: gỡ ITEM-62 theo «khối» sẽ xoá luôn 6 mục. Phép kiểm «sau ITEM-62 phải là `]`» chặn kịp, trước khi ghi.
Hai dashboard gỡ mục trước đó (Đau đầu, Viêm gan B) đã kiểm lại trên bản sao lưu: 0 mục khoá nháy, mỗi khối gỡ đúng một đối tượng.

## Cách vá

- **Cổng (luật 2b, `verify_dashboard.py` 2 bản khớp byte):** CHẶN CỨNG mục khoá nháy (`{"id": …}` / `{'id': …}`), nêu đích
  danh mục. Không dạy riêng `split_items` đọc thêm kiểu nháy, vì còn nhiều bộ parse khác (cầu nạp hub, quét chủ đề…) cùng giả
  định — buộc dữ liệu về MỘT kiểu mà mọi công cụ đều đọc. Không báo oan trên dashboard lành (đo cạnh sổ đối chiếu thật).
- **Dữ liệu:** 6 mục chuẩn hoá bằng parse JSON chuẩn rồi viết lại khoá không nháy (không thay chuỗi bằng biểu thức chính quy);
  đối chiếu từng trường chuỗi: 0 lệch. Sao lưu `.bak-20261117-truoc-chuan-hoa-6-muc-khoa-nhay`. Cổng thấy 61 mục (trước 55).
- **Lần đầu được kiểm:** cổng `--online` PASS, cả 6 PMID có thật khớp tiêu đề, 6 DOI tra được, 0 lỗi cứng.
- **Dạy agent:** `cap-nhat-chung-cu-y-khoa/SKILL.md` (v1.63.0) — mục trong `items` viết khoá không nháy.

## Kiểm hồi quy

- `tools/test_cong_muc_khoa_nhay_20261117.py` — CLI thật của cổng: nháy kép, nháy đơn bị chặn; không nháy không báo oan.
- BH182 — như trên, cộng quét DỮ LIỆU SỐNG toàn kho: không dashboard nào còn mục khoá nháy.
- Đột biến 3/3 bị bắt (bỏ luật · chỉ bắt nháy kép · bắt cả không nháy).

## Bài học

Một dashboard «PASS» chỉ nói về những mục cổng NHÌN THẤY. Bất biến đáng canh: mọi đối tượng có khoá `id` trong DATA phải được
bộ tách nhận — đếm bằng một phép KHÔNG phụ thuộc bộ tách. Khi một thao tác cấu trúc (gỡ/chuyển mục) cho kết quả kích thước bất
thường, dừng lại đo, đừng ghi.
