# 18/11/2026 — Lần đầu đo được độ đúng của kiểm máy Claude API (41%) và sửa lời dặn theo nhãn bác sĩ

## Bối cảnh

Kiểm máy Claude API (A12 nội dung trích dẫn, phản biện máy đề cương) chạy tự động từ 17/11 nhưng chưa ai biết máy đúng
bao nhiêu phần.

- Phiếu 17 phát hiện của đề cương BTM được trình dạng danh mục.
- Mỗi mục kèm bằng chứng máy kiểm được: dòng đề cương, siêu dữ liệu tài liệu, phiên bản phần mềm thật.
- Bác sĩ chọn nhãn; nhãn ghi bằng `duyet_kiem_may_api.py ghi --ap-dung`.

## Số đo (nhãn bác sĩ)

- Tổng 7 đúng / 10 nhầm ⇒ **41%**.
- A12: 1/5. Riêng loại «hỗ trợ một phần»: 0/4 — cả 4 cùng kiểu: đòi tác giả/năm có trong abstract; đòi một tài liệu
  chống đỡ phần câu đã trích cho tài liệu khác; câu chung «được tham khảo».
- Phản biện máy: 6/12. Nhầm vì: không tự cộng lại số; cho phiên bản phần mềm «không có thật» (thật ra đúng phiên bản
  đang chạy); lẫn cỡ mẫu với khung mẫu; coi cột mã biến CRF là dấu vết máy; báo thiếu chữ viết tắt mà bảng đã có.

## Đã sửa (PR y khoa drluanbv175/medical-ebm-automation#321)

- Thêm vào lời dặn của hai công cụ các quy tắc rút từ đúng những kiểu nhầm trên.
- Báo cáo JSON ghi `loi_dan_sha256`, để đo độ đúng theo từng phiên bản lời dặn.
- Chạy lại cùng đề cương (0,26 USD):
  - A12 khớp 5/5 nhãn, 0 nhầm mới trên 52 cặp.
  - Phản biện máy hết 4/6 kiểu nhầm; giữ 3/6 mục đúng (3 mục đúng không xuất hiện lượt này — tập phát hiện thay đổi
    giữa các lượt); 9 phát hiện mới chưa có nhãn.

## Bài học

- Đo trên chính đề cương dùng để rút quy tắc là phép đo LẠC QUAN. Độ đúng thật phải đo bằng nhãn bác sĩ ở lượt sau,
  tách theo `loi_dan_sha256`.
- Phản biện máy chọn một tập phát hiện khác nhau mỗi lượt. So hai lượt phải tính cả mục đúng bị rơi, không chỉ đếm mục
  nhầm đã hết.
- Danh mục chọn nhãn kèm bằng chứng kiểm được giúp bác sĩ gắn 17 nhãn trong một lượt; đề xuất đánh dấu
  «(Recommended)» chỉ là gợi ý — nhãn ghi theo lựa chọn của bác sĩ.
