# 17/11/2026 — Ba đề xuất hoàn thiện hệ nghiên cứu: đọc máy lặp tới khi cạn, 16 kịch bản vào CI, diễn tập G4→G5 trên khung BTM

## Bối cảnh
Bác sĩ hỏi hệ nghiên cứu đã hoàn thiện sau giả lập chưa. Câu trả lời: chưa thể nói vậy. Lượt Claude API thật đầu tiên đã tìm ra 11 dấu vết máy trong đề cương BTM, mà đề cương này đã «ĐẠT K1–K8». Bác sĩ yêu cầu chạy cả ba đề xuất, kèm kế hoạch và kết quả rõ ràng, «chứ cứ đi vòng mãi».

Mỗi đề xuất có một điểm dừng đo được:

| # | Việc | Xong khi |
|---|---|---|
| 1 | Claude đọc 16 đề cương giả lập (phản biện máy + kiểm nội dung trích dẫn) | một vòng không còn lỗi máy mới lặp lại; tối đa 3 vòng |
| 2 | 16 kịch bản vào CI | PR làm vỡ bất kỳ kịch bản nào ⇒ CI đỏ |
| 3 | Diễn tập trên khung thật của BTM | chạy tới bước xa nhất làm được mà không có dữ liệu thật |

## Kết quả đề xuất 1 — ba vòng đọc
Tổng chi phí ≈ 7,0 USD.

| Vòng | Phát hiện (cao/vừa) | Nhóm lặp ≥ 2 đề tài | Chi phí |
|---|---|---|---|
| 1 | 366 (281) | 53 | 2,42 USD |
| 2 | 343 (263) | 59 | 2,28 USD |
| 3 | 319 (248) | 42 | 2,31 USD |

Lỗi máy đã sửa:
- **Vòng 1:**
  - khuôn SAP §9 «±1 SD» áp cho biến nhị phân (9 đề tài);
  - phiếu đồng ý hứa «bằng chứng cấp độ cao nhất» (6) và ghi chú cho người soạn «ghi rõ chính sách» (7);
  - «EXPEDITED REVIEW» tiếng Anh;
  - «tỷ lệ tỷ lệ»;
  - tiêu đề bảng bị cắt giữa chữ;
  - Phụ lục C đánh số «PHẦN» nhảy;
  - mã biến bọc dấu `;
  - Bảng 3.1: tiêu đề lệch nội dung, tài liệu chuẩn chiếm suất «hướng dẫn»;
  - «Nguồn số liệu» liệt kê lặp.
- **Vòng 2:** lộ một lỗi do chính bản vá vòng 1 gây ra. Nhãn ô trống «[CẦN CHỦ NHIỆM CHỌN MỘT]» khiến bộ giả lập tự điền tên chủ nhiệm vào phiếu đồng ý (9 đề tài). Đã trả về «[CẦN XÁC NHẬN]».
- **Vòng 3:** còn đúng một nhóm lỗi máy mới. Câu ở mục cỡ mẫu gọi chuẩn báo cáo (SPIRIT 2025) là «hướng dẫn phương pháp học» (3 đề tài). Đã sửa lời.
  - Một nhóm thấp mức còn lại: cột «Hiệu ứng» của bảng giả, ghi nhận, không sửa.

Phần còn lại của ba vòng là nội dung do bộ giả lập điền thay người, không phải lỗi hệ, nên không tính vào tiêu chí dừng:
- tiến độ 18 tháng so với thời gian thực hiện 12 tháng;
- quyết định xin miễn đồng ý;
- dữ liệu thiếu;
- thiết kế giấu phân bổ…

**Bài học:** đổi chữ một khuôn SAP mà không đổi neo của đặc tả G6 làm 14/16 kịch bản sập. Cổng phán của CI (đề xuất 2) bắt được ngay: 2/16. Khuôn và neo phải đổi cùng nhau.

## Kết quả đề xuất 2 — 16 kịch bản vào CI
- Workflow `.github/workflows/gia-lap-16.yml`: ma trận 16 job, mỗi job chạy trọn G0→G10.
- `tools/kiem_gia_lap_16.py` PHÁN đạt khi đủ ba điều: khoá được gói G10, 0 ô lỗi máy, đề cương nộp đạt.
- Chạy offline:
  - nền G0 đặt ở `tests/fixtures/gia_lap_nen_g0/` (2,5 MB);
  - kết quả A12 theo từng PMID đặt ở `tests/fixtures/gia_lap_a12/a12_theo_pmid.json`;
  - `GIA_LAP_A12_CHI_KHO=1`: PMID chưa có trong kho là lỗi nói rõ cách bổ sung.
- Đã thử chế độ CI trên máy: 2/2 kịch bản đạt mà không gọi mạng.
- Lượt cuối có mạng: 16/16 đạt.

## Kết quả đề xuất 3 — diễn tập trên khung thật của BTM
Làm trong bản sao ngoài repo, ký bằng khoá giả, dữ liệu mô phỏng. Không đụng `exports/` thật.

| Bước | Kết quả |
|---|---|
| G4 | khoá SAP được |
| G5 | sinh đủ bộ công cụ (phiếu 73 dòng, guardrail đạt); mẫu nhập liệu Excel và SPSS |
| SPSS/R | **ĐẠT**: 24 ca × 94 biến, khứ hồi `.sav`, đối chiếu ba chiều `.rds`, tính thử 41 biến phái sinh (`xn_du`, `phan_loai_btm`…) |
| Tiếp nhận dữ liệu | dừng đúng chỗ: dữ liệu mô phỏng điền vào câu mà logic nhánh của phiếu BTM đang ẩn, ngày ngoài cửa sổ 2026; bộ kiểm G5 bắt được |

Vì vậy chưa tới G6–G9 riêng cho BTM. Các công cụ G6–G9 đã chạy qua kịch bản cắt ngang giả lập.

Việc tiếp theo để đi hết G6–G9 trên khung BTM: bộ sinh dữ liệu mô phỏng phải theo logic nhánh và khoảng ngày của từ điển REDCap. Dữ liệu thật của BTM chỉ có sau khi Hội đồng duyệt, sớm nhất 19/01/2027.

## Luật rút ra
- Mọi điểm dừng phải đo được. Tiêu chí của đọc máy là «không còn nhóm lỗi máy mới lặp ≥ 2 đề tài».
- Một bản vá phải chạy lại cả 16 kịch bản trước khi coi là xong, vì bản vá có thể làm vỡ chỗ khác (vòng 1 → 2/16, vòng 2 → lỗi phiếu đồng ý).
