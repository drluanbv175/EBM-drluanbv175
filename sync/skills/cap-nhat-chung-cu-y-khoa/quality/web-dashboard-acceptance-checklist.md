# Acceptance checklist — Web Dashboard "Evidence Workbench" theo vấn đề cụ thể

## Nội dung và độ tin cậy
- [ ] Dashboard chỉ chứa kết luận đã trình bày trong bản cập nhật EBM tương ứng.
- [ ] Từng item có nguồn, tổ chức, ngày/phiên bản và quần thể được xác minh.
- [ ] Nội dung chưa đủ để thay đổi được tách riêng, không gắn nhãn áp dụng.
- [ ] Không đưa liều, cut-off, thời gian điều trị hoặc cảnh báo nhãn chưa xác minh.

## Cấu trúc và khả dụng (mô hình Evidence Workbench 3 cột)
- [ ] Dùng template `web-dashboard-evidence-workbench.html`; chỉ thay khối `DATA`, không sửa HTML/CSS.
- [ ] Bố cục 3 cột: bộ lọc (trái) · Quick View + bảng item (giữa) · Evidence Detail (phải).
- [ ] Băng `Clinical Quick View` là tab/màn hình mặc định (làm ngay, tránh, cờ đỏ, nhóm đặc biệt).
- [ ] Bộ lọc facet theo Quyết định / Nhóm đặc biệt / Thiết kế / Mức chứng cứ, có số đếm.
- [ ] Tìm kiếm toàn cục; click dòng → mở Evidence Detail (cột phải).
- [ ] Có nút xuất `CSV` và `JSON` cho item đang lọc.
- [ ] Hiệu số (HR/RR/OR…) hiển thị kèm forest plot mini, đúng như nguồn báo cáo.
- [ ] Có tab `Kiểm chứng thao tác` với 4 nhiệm vụ ≤30–60 giây.

## Quản trị
- [ ] Mã `ITEM-xx` được ghi rõ không phải ID Master.
- [ ] Không hiển thị hoặc tuyên bố đã cập nhật Master nếu bác sĩ chưa yêu cầu.
- [ ] Nếu có yêu cầu tích hợp Master, xử lý theo quy trình Dashboard riêng.
