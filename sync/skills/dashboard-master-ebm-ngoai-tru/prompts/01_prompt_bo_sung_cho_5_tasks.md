# Prompt bổ sung cho 5 Scheduled Tasks trong Claude

Sau khi upload và bật skill `dashboard-master-ebm-ngoai-tru`, thêm câu lệnh phù hợp dưới đây vào từng task.

## Updateebm

Sử dụng skill `dashboard-master-ebm-ngoai-tru` để tạo gói cập nhật cho Dashboard Master EBM từ kết quả rà soát tuần này. Chỉ đưa vào Change Log nội dung đã xác minh có khả năng ảnh hưởng thực hành ngoại trú; nếu chưa đủ căn cứ, đưa vào Not_For_Change. Không tạo KPI hoặc số liệu triển khai giả.

## Guideline

Sử dụng skill `dashboard-master-ebm-ngoai-tru` để cập nhật Dashboard từ guideline/focused update/pathway chính thức đã xác minh. Ghi rõ tổ chức, tên tài liệu, năm/phiên bản, đối tượng, khuyến cáo liên quan và grading nguyên bản nếu có. Kiểm tra trùng với các bản ghi Updateebm trước khi tạo Change ID mới.

## Updatethuoc

Sử dụng skill `dashboard-master-ebm-ngoai-tru` để cập nhật Medication_Safety, Evidence_Register và Action_Register từ các cảnh báo thuốc/kháng sinh đã xác minh. Ưu tiên official safety alert và WHO AWaRe khi phù hợp; đánh dấu ưu tiên khẩn nếu có nguy cơ nghiêm trọng cho người bệnh ngoại trú.

## Thangdiemls

Sử dụng skill `dashboard-master-ebm-ngoai-tru` để cập nhật Clinical_Tools từ các thang điểm/công cụ lâm sàng đã xác minh. Chỉ ghi công cụ khi xác định được đối tượng áp dụng, cách diễn giải/cut-off, hành động liên quan và giới hạn áp dụng; không tự ngoại suy.

## Tonghopcapnhat

Sử dụng skill `dashboard-master-ebm-ngoai-tru` để tổng hợp Dashboard theo tháng từ các bản ghi đã xác minh của Updateebm, Guideline, Updatethuoc và Thangdiemls. Loại trùng, phân loại ưu tiên và lập Action Register; không tạo cập nhật hoặc KPI giả nếu không có dữ liệu nguồn.
