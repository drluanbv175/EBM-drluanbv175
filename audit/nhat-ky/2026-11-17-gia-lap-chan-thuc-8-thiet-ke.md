# 17/11/2026 — Giả lập chân thực cho cả 8 thiết kế: phiếu như đề tài thật, dữ liệu sinh từ từ điển, kiểm hệ tìm lại đúng tham số

## Bối cảnh

Bác sĩ yêu cầu: «Giả lập chân thực trên tất cả các đề tài nghiên cứu để hệ thống hoàn chỉnh có thể thực hiện được tất
cả các nghiên cứu y khoa».

16 kịch bản cũ đều dùng bộ biến 7–12 trường, một biểu mẫu, mọi câu bắt buộc, không sàng lọc, không logic nhánh, và dữ
liệu sinh phẳng. Buổi diễn tập trên khung thật BTM cùng ngày lộ 9 lỗi hệ mà các kịch bản cũ không chạm tới (nhật ký
`2026-11-17-gia-lap-du-lieu-that-btm-g2-g10.md`).

## Đã làm

Thêm `tools/gia_lap_chan_thuc.py` gồm 8 kịch bản chân thực: RCT, cắt ngang, thuần tập hồi cứu, bệnh–chứng, chẩn đoán, dự
báo, tổng quan gộp, định tính. Mỗi kịch bản kế thừa kịch bản gốc (cùng đề tài, nền G0, quyết định G0/G1/G3) nhưng có phiếu
nhiều phần như đề tài thật:
- phần sàng lọc ghi mọi người/hồ sơ đã xét, kèm calc «đủ tiêu chuẩn» làm cổng nhánh;
- nhánh theo dõi (mất dấu, rút lui, tử vong);
- câu chọn nhiều bắt buộc, có ô loại trừ;
- ngày nối tiếp nhau;
- mã câu đánh theo phần.

Dữ liệu sinh bằng chính từ điển G5 của từng đề tài. `sinh_du_lieu_redcap` có thêm mô hình tuyến tính, logistic, công
thức, sống còn có kiểm duyệt (nguy cơ tỷ lệ, tử vong/mất dấu cạnh tranh), nhị thức kèm hiệu ứng ngẫu nhiên theo nghiên
cứu, ô loại trừ và mã thiếu. Bộ sinh tuyển/trích tới khi đủ N của G3, và tham số khớp giả định G3 của kịch bản gốc.

**Kiểm độ chính xác (mới).** Tham số thật được tính ĐỘC LẬP với engine phân tích: sinh 30.000 bản ghi bằng cùng mô hình
rồi đo bằng Python thuần. Phép kiểm so tham số thật với ước lượng và KTC 95% mà hệ báo ở G6:

| Kết luận | Điều kiện |
|---|---|
| ĐẠT | tham số thật nằm trong KTC 95% |
| CẢNH BÁO | ngoài KTC 95% nhưng trong KTC 99,9% |
| SAI | ngoài KTC 99,9% — dấu hiệu lỗi hệ (lọc sai quần thể, mã hoá sai…) |

`kiem_gia_lap_16.py` chặn khi kết luận là SAI hoặc khi không đo được. Workflow CI `gia-lap-16` nay chạy 24 job.

## Kết quả đo

| Kịch bản | G10 | Ô lỗi máy | Ước lượng · KTC 95% | Tham số thật |
|---|---|---|---|---|
| RCT | khoá | 0 | RD 0,153 (0,009–0,298) | 0,197 |
| Cắt ngang | khoá | 0 | tỷ lệ 42,1% (37,5–46,8) | 41,0% |
| Thuần tập | khoá | 0 | RD 0,051 (0,029–0,074) | 0,036 |
| Bệnh–chứng | khoá | 0 | OR 2,08 (1,38–3,14) | 1,76 |
| Chẩn đoán | khoá | 0 | AUC 0,64 (0,46–0,81) | 0,69 |
| Dự báo | khoá | 0 | C 0,688 (0,639–0,736) | 0,686 |
| Tổng quan gộp | khoá | 0 | RR 0,75 (0,69–0,82) | 0,70 |
| Định tính | khoá | 0 | — | — |

8/8 kịch bản khoá gói G10, và cả 7 kịch bản định lượng đều ĐẠT phép kiểm độ chính xác. Lượt chạy RCT đi qua 27 trường
có nhánh, 1.909 ô trống đúng do nhánh ẩn, calc được tính lại, nhập kép bắt đủ 4 ô lệch cài sẵn, làm sạch 0 query mở, G6
phân tích đúng 218 người được ngẫu nhiên hoá và đa trị cho 37 người mất dấu.

## Lỗi hệ lộ ra và đã sửa

1. **Báo động giả PII theo tên cột.** Cổng nạp, làm sạch, khoá, giả danh và G5-AUTO-02 chặn cột `tc_dien_thoai` («có
   điện thoại nhận tin nhắn — Có/Không») vì tên chứa «dien_thoai». Nay trường phân loại có mã đã khai trong từ điển G5
   được miễn chặn theo tên. Giá trị ô vẫn quét đủ mẫu SĐT/CCCD/email/BHYT, và trường `text` vẫn bị chặn như cũ.
2. **Bộ giả lập sập khi G5 không dựng được mẫu nhập** (FileNotFoundError che mất cổng thật đang chặn). Nay dừng gọn kèm
   lý do.
3. **Kịch bản kế thừa tự ghi nền G0 riêng**, trùng với nền của kịch bản gốc. Nếu thư mục riêng chưa có, lệnh ghi còn
   xoá và ghi đè nền của kịch bản gốc. Nay kịch bản kế thừa chỉ đọc nền gốc.

## Lỗi của chính kịch bản, đã bị hệ bắt

- Ma trận dùng kiểu «danh_muc» không hợp lệ: G3-AUTO-19 bắt.
- Mã câu của ma trận gốc trùng mã tự đánh của phiếu.
- Trường số không khai min/max bị bộ sinh ép vào 0–100: thêm chốt.
- Kịch bản cắt ngang có câu phỏng vấn nhưng chưa khai công cụ: G10 đòi đúng.
- Chú thích hệ số RCT sai so với số đo (chạy khô 400 người lệch ±0,1). Nay hiệu chỉnh trên 20.000 người: RR 1,465, khớp
  G3.

## Kiểm

- `tests/test_gia_lap_chan_thuc_20261117.py`: 35 phép kiểm. Kiểm đột biến 20/20 đỏ đúng chỗ.
- Hồi quy 18/11/2026 trên Mac, cùng biến môi trường với CI, chạy bằng mã mới: 24/24 kịch bản (16 cũ + 8 chân thực) khoá
  gói G10, 0 ô lỗi máy, đề cương nộp đạt. Mỗi kịch bản mất 3–7 phút.

## Bài học

- **Một kịch bản giả lập chỉ có giá trị khi nó buộc dữ liệu đi qua đúng các lớp mà dữ liệu thật đi qua.** Lớp đó gồm
  sàng lọc, nhánh, calc, câu chọn nhiều, mất dấu. «Khoá gói G10» chưa đủ: phải đo xem con số cuối có ĐÚNG không, bằng
  một tham số thật tính độc lập với engine.
- **Tham số thật phải tính trên quần thể lớn, không ước tính nhẩm.** Lượt chạy khô 400 người lệch ±0,1, đủ để ghi sai
  chú thích.
