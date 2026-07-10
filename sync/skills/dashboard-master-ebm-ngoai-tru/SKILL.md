---
name: dashboard-master-ebm-ngoai-tru
description: Tạo, cập nhật hoặc kiểm định Dashboard Master EBM ngoại trú và các sổ Change Log, Evidence Register, Medication Safety, Action Register; xác minh nguồn, loại trùng, lập báo cáo điều hành tháng.
---

# Dashboard Master EBM ngoại trú

## Mục đích

Skill này tạo mới, cập nhật hoặc kiểm định Dashboard Master EBM phục vụ bác sĩ khám bệnh ngoại trú và quản lý bệnh nhân đa bệnh lý dựa trên chứng cứ.

Skill dùng khi người dùng yêu cầu:
- tạo Dashboard EBM;
- cập nhật Dashboard từ scheduled tasks;
- nhập các cập nhật guideline, thuốc, kháng sinh, thang điểm hoặc tổng hợp tháng;
- loại trùng bản ghi;
- tạo Change Log, Evidence Register, Action Register hoặc báo cáo điều hành;
- cập nhật file `EBM_Dashboard_Master_Template.xlsx` hoặc một file Dashboard Master do người dùng cung cấp.

## Khi không dùng skill này

Skill này quản trị *sổ theo dõi chứng cứ và hành động*, không phải công cụ ra quyết định trên một người bệnh cụ thể. Không kích hoạt skill khi:
- người dùng hỏi tiếp cận chẩn đoán/điều trị cho một ca bệnh cụ thể (dùng skill lâm sàng phù hợp);
- chỉ cần thẩm định một bài báo hoặc tính NNT/NNH đơn lẻ mà không nhập vào Dashboard;
- tạo slide/bài giảng hoặc tài liệu đào tạo (dùng skill tài liệu/đào tạo);
- làm dashboard cho lĩnh vực ngoài quản trị chứng cứ EBM ngoại trú.

Khi một nội dung vừa cần đưa vào Dashboard vừa cần xử trí lâm sàng, tách rõ vai trò: phần ghi nhận – truy nguyên chứng cứ thuộc skill này; phần khuyến cáo lâm sàng giao cho skill lâm sàng tương ứng.

## Nguyên tắc bất biến

1. Ưu tiên độ tin cậy, độ đặc hiệu và khả năng truy nguyên nguồn hơn số lượng cập nhật.
2. Không tạo dữ liệu lâm sàng, dữ liệu triển khai, KPI hiệu quả, tỷ lệ tuân thủ, số người bệnh hưởng lợi hoặc chi phí tiết kiệm khi chưa có dữ liệu thực tế.
3. Chỉ phân loại `Nên thay đổi thực hành` khi đã xác minh nguồn, năm/phiên bản, quần thể áp dụng, khuyến cáo và mức độ liên quan thực hành ngoại trú.
4. Không tự gán GRADE. Phân biệt độ chắc chắn chứng cứ và độ mạnh khuyến cáo; nếu nguồn không báo cáo grading, ghi rõ.
5. Không xóa bản ghi lịch sử. Nếu cần sửa, tạo bản ghi hiệu chỉnh có liên kết tới bản ghi trước.
6. Nếu không truy cập được file Master trong phiên hiện tại, xuất `GÓI CẬP NHẬT DASHBOARD` theo template thay vì khẳng định đã ghi vào file.
7. Khi cập nhật workbook, giữ nguyên dữ liệu đã có, thêm dòng mới hoặc hiệu chỉnh có kiểm soát; không ghi đè tùy tiện.
8. Nếu nội dung liên quan thực hành bệnh viện hoặc quy trình/danh mục thuốc tại đơn vị, dùng trạng thái `Cần xác nhận tại đơn vị`.

## Các task nguồn được hỗ trợ

| Task nguồn | Phạm vi | Sheet đích chính |
|---|---|---|
| `Updateebm` | Chứng cứ mới có khả năng thay đổi thực hành | `Change_Log`, `Evidence_Register`, `Not_For_Change` |
| `Guideline` | Guideline/focused update/official pathway mới | `Change_Log`, `Evidence_Register` |
| `Updatethuoc` | Cảnh báo thuốc, stewardship, WHO AWaRe, tương tác | `Medication_Safety`, `Evidence_Register`, `Action_Register` |
| `Thangdiemls` | Thang điểm/công cụ quyết định lâm sàng | `Clinical_Tools`, `Evidence_Register`, `Action_Register` |
| `Tonghopcapnhat` | Tổng hợp tháng, loại trùng, ưu tiên triển khai | `Dashboard_Summary`, `Action_Register`, `Task_Run_Log` |

Ngoài sheet đích chính, **mọi task đều ghi `Task_Run_Log`** sau mỗi lần chạy; các task sàng lọc chứng cứ (`Updateebm`, `Guideline`, `Updatethuoc`, `Thangdiemls`) dùng thêm `Not_For_Change` cho tín hiệu chưa đủ căn cứ thay đổi thực hành.

Không tự đưa task trùng nội dung vào nguồn dữ liệu Master nếu chưa xác định vai trò riêng.

## Quy trình bắt buộc

### Bước 1. Xác định đầu vào

Xác định rõ:
- task nguồn;
- kỳ rà soát;
- tài liệu đã tìm thấy;
- có hay không file Dashboard Master để cập nhật;
- mục tiêu là tạo mới, cập nhật, hay kiểm định.

### Bước 2. Xác minh nguồn

Mỗi cập nhật tiềm năng phải có tối thiểu:
- loại nguồn;
- tổ chức/tác giả;
- tên tài liệu;
- năm/phiên bản;
- đối tượng/quần thể áp dụng;
- nội dung ảnh hưởng thực hành;
- URL hoặc thông tin truy nguyên nguồn khi có.

Ưu tiên:
1. Guideline hoặc cập nhật chính thức mới nhất.
2. Official safety alert.
3. Systematic review/meta-analysis chất lượng cao.
4. RCT lớn, đa trung tâm.
5. Cohort/real-world evidence lớn.
6. Consensus chỉ khi thiếu chứng cứ mạnh hơn.

### Bước 3. Quyết định có đưa vào Dashboard hay không

Chỉ đưa vào Dashboard khi thuộc một trong các nhóm:
- thay đổi tiêu chuẩn chẩn đoán/phân tầng nguy cơ;
- thay đổi điều trị nền tảng, mục tiêu điều trị hoặc theo dõi;
- cảnh báo an toàn thuốc có ý nghĩa thực hành;
- kháng sinh/WHO AWaRe/stewardship có tác động ngoại trú;
- công cụ/thang điểm đã xác minh và có hành động lâm sàng;
- tiêu chí chuyển tuyến/nhập viện hoặc safety-netting quan trọng.

Nếu chưa đủ căn cứ, đưa vào `Not_For_Change`, không đưa thành hành động thay đổi thực hành.

### Bước 4. Loại trùng

Trước khi thêm bản ghi mới:
- so khớp chủ đề, khuyến cáo, nguồn chính, năm/phiên bản và đối tượng áp dụng;
- nếu nội dung đã có, bổ sung Evidence ID hoặc tạo ghi chú xác minh; không tạo Change ID mới trùng;
- nếu guideline mới thay thế khuyến cáo cũ, tạo bản ghi hiệu chỉnh/liên kết và không xóa lịch sử.

### Bước 5. Cập nhật sheet đúng mục đích

Đọc `references/01_cau_truc_dashboard_va_quy_tac_du_lieu.md` và `workflows/01_cap_nhat_dashboard_tu_tasks.md` trước khi thêm dữ liệu.

### Bước 6. Kết thúc mỗi lần cập nhật

Luôn xuất:
1. Tóm tắt kỳ cập nhật.
2. Các dòng mới đã thêm hoặc gói dữ liệu chờ nhập.
3. Nội dung chưa nên thay đổi thực hành.
4. Cảnh báo an toàn nếu có.
5. Các mục cần xác nhận tại đơn vị.
6. Nhật ký task run.

## Trạng thái chuẩn

Chỉ sử dụng các trạng thái sau:
- `Mới phát hiện – cần xác minh`
- `Đã xác minh – cần đánh giá áp dụng`
- `Nên thay đổi thực hành`
- `Theo dõi thêm – chưa thay đổi thực hành`
- `Không áp dụng hiện tại`
- `Đã đưa vào kế hoạch triển khai`
- `Cần xác nhận tại đơn vị`

## Mức ưu tiên hành động

Chỉ sử dụng:
- `Khẩn – liên quan an toàn người bệnh`
- `Cao – có khả năng thay đổi điều trị`
- `Trung bình – cần cập nhật quy trình/tư vấn`
- `Theo dõi`

## Tài nguyên cần đọc theo nhiệm vụ

| Khi cần làm gì | Đọc file |
|---|---|
| Hiểu cấu trúc workbook và quy tắc dữ liệu | `references/01_cau_truc_dashboard_va_quy_tac_du_lieu.md` |
| Xác minh chứng cứ và grading | `references/02_xac_minh_nguon_va_phan_loai_chung_cu.md` |
| Cập nhật từ scheduled task | `workflows/01_cap_nhat_dashboard_tu_tasks.md` |
| Tổng hợp và loại trùng hàng tháng | `workflows/02_tong_hop_thang_va_loai_trung.md` |
| Tạo workbook mới | `workflows/03_tao_file_dashboard_master.md` |
| Dùng prompt cho 5 tasks | `prompts/01_prompt_bo_sung_cho_5_tasks.md` |
| Kiểm định trước khi sử dụng | `quality/01_checklist_kiem_dinh.md` |
| Dùng bảng nhập liệu chuẩn | `templates/01_goi_cap_nhat_dashboard.md` |

## File mẫu kèm theo

Nếu cần tạo mới hoặc cập nhật Dashboard dạng Excel, sử dụng mẫu:
`assets/EBM_Dashboard_Master_Template.xlsx`.

Không tuyên bố đã cập nhật file nếu file chưa được mở, chỉnh sửa và xuất lại trong phiên làm việc.
