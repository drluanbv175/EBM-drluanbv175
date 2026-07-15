# Acceptance checklist — Web Dashboard "Evidence Workbench" theo vấn đề cụ thể

## Nội dung và độ tin cậy
- [ ] Dashboard chỉ chứa kết luận đã trình bày trong bản cập nhật EBM tương ứng.
- [ ] Từng item có nguồn, tổ chức, ngày/phiên bản và quần thể được xác minh.
- [ ] Nội dung chưa đủ để thay đổi được tách riêng, không gắn nhãn áp dụng.
- [ ] Không đưa liều, cut-off, thời gian điều trị hoặc cảnh báo nhãn chưa xác minh.
- [ ] Khối `DATA.standards` khai báo khung câu hỏi, thứ bậc nguồn, ngày/nguồn tìm kiếm, chuẩn báo cáo và công cụ thẩm định.
- [ ] Tab `Chuẩn & chất lượng` hiển thị CONSORT/STROBE/PRISMA/STARD/TRIPOD khi phù hợp và AGREE II/AMSTAR 2/RoB 2/ROBINS-I/QUADAS-2/PROBAST/JBI cho thẩm định.
- [ ] Cổng liêm chính trước phát hành ghi rõ truy nguyên nguồn, tách độ chắc chắn với quyết định thực hành, không PII, an toàn và tính phù hợp Việt Nam.
- [ ] `python3 tools/verify_dashboard.py <dashboard>.html --online --strict-sources` PASS: PMID/DOI phân giải, nguồn còn mới, ≥2 nguồn tìm kiếm, references[] đủ, không `apply` trên chứng cứ yếu/không phân hạng/chỉ đồng thuận.

## Cấu trúc và khả dụng (mô hình Evidence Workbench 3 cột)
- [ ] Dùng template `web-dashboard-evidence-workbench.html`; chỉ thay khối `DATA`, không sửa HTML/CSS.
- [ ] Bố cục 3 cột: bộ lọc (trái) · Quick View + bảng item (giữa) · Evidence Detail (phải).
- [ ] Băng `Clinical Quick View` là tab/màn hình mặc định (làm ngay, tránh, cờ đỏ, nhóm đặc biệt).
- [ ] Có tab `Chuẩn & chất lượng` để rà câu hỏi, nguồn, chuẩn thẩm định, độ cập nhật, an toàn, Việt Nam và truy nguyên từng item.
- [ ] Bộ lọc facet theo Quyết định / Nhóm đặc biệt / Thiết kế / Mức chứng cứ, có số đếm.
- [ ] Tìm kiếm toàn cục; click dòng → mở Evidence Detail (cột phải).
- [ ] Có nút xuất `CSV` và `JSON` cho item đang lọc.
- [ ] Hiệu số (HR/RR/OR…) hiển thị kèm forest plot mini, đúng như nguồn báo cáo.
- [ ] Có tab `Kiểm chứng thao tác` với 5 nhiệm vụ ≤30–60 giây, gồm nhiệm vụ rà tab `Chuẩn & chất lượng`.

## Quản trị
- [ ] Mã `ITEM-xx` được ghi rõ không phải ID Master.
- [ ] Không hiển thị hoặc tuyên bố đã cập nhật Master nếu bác sĩ chưa yêu cầu.
- [ ] Nếu có yêu cầu tích hợp Master, xử lý theo quy trình Dashboard riêng.
