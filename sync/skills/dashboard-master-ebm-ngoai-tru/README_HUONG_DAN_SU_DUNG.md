# Hướng dẫn sử dụng Skill Dashboard Master EBM ngoại trú

## Mục đích
Skill này dùng để tạo và cập nhật Dashboard quản trị chứng cứ cho 5 scheduled tasks trong Claude:
`Updateebm`, `Guideline`, `Updatethuoc`, `Thangdiemls`, `Tonghopcapnhat`.

## Cài đặt
1. Upload file ZIP của skill vào Claude Custom Skills.
2. Bật skill.
3. Dùng file Excel mẫu kèm theo làm Dashboard Master ban đầu nếu cần.
4. Mở từng scheduled task và dán câu lệnh trong `prompts/01_prompt_bo_sung_cho_5_tasks.md`.

## Nguyên tắc quan trọng
- Dashboard là sổ theo dõi chứng cứ và hành động, không tự chứng minh hiệu quả chăm sóc.
- Mọi cập nhật quan trọng phải truy nguyên được nguồn.
- Không ghi KPI lâm sàng hoặc hiệu quả triển khai khi chưa có dữ liệu thật.
- Nếu scheduled task không có quyền cập nhật file Master, yêu cầu task xuất GÓI CẬP NHẬT DASHBOARD để nhập sau.

## File Excel mẫu
`assets/EBM_Dashboard_Master_Template.xlsx` chứa cấu trúc sheet, công thức tóm tắt, dropdown và bảng dữ liệu trống để sử dụng ngay.
