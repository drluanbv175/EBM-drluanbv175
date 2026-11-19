# 20/11/2026 — Nối bộ kiểm ngữ nghĩa Claude API vào bước xuất gói (cảnh báo, chưa hiệu chuẩn)

**Bối cảnh.** Bác sĩ (20/11/2026, «Làm 2,3,6» — mục 3) yêu cầu nối `tools/kiem_ngu_nghia_api.py` vào `xuat_goi_cap_nhat.py` ở mức CẢNH BÁO.
- Theo đề xuất của tôi, việc này nên đợi bộ vàng phần B (40 mục thật) có nhãn độc lập. Bác sĩ chọn làm ngay.
- Vì vậy mọi đầu ra mang nhãn CHƯA HIỆU CHUẨN.
- Số đo tạm trên đột biến (19/11, nhãn dự kiến), API so với luật cứng:

  | Trục | API | Luật cứng |
  |---|---|---|
  | Quần thể | 18/22 | 4/22 |
  | Chiều | 14/18 | 2/18 |
  | Điều kiện | 7/16 | 0/16 |

- Trên 20 mục thật, API báo giả ở trục điều kiện 4/17.

**Thay đổi.**
- **`kiem_ngu_nghia_api.py --dashboard <tệp> [--online] [--goi-api]`** chấm các mục `apply` có PMID của một dashboard.
  - Prompt và bộ tách câu trả lời giữ nguyên như lượt đo 19/11.
  - Bộ đệm `derivatives/ngu-nghia-api-xuat-goi.json` dùng lại; bộ đệm của bộ vàng được đọc nhưng không ghi.
  - Tóm tắt PubMed lưu đệm ở `derivatives/ngu-nghia-api-tom-tat.json`, ngoài git.
  - Tối đa 40 lượt gọi mới mỗi dashboard.
  - Chạm trần chi phí, lỗi khoá hay lỗi mạng thì dừng gửi. Kết quả hỏng ở một mục thì bỏ mục đó, đi tiếp.
- **Chính sách.** Thêm `sync/api-khi-can.json` → `tu_chay.ngu_nghia_xuat_goi: true`.
  - Tệp vắng, hỏng, hoặc giá trị không phải bool thì không gọi, không in kết quả cũ.
  - `api_khi_can.doc_chinh_sach` vẫn đọc được chính sách (có test chốt).
- **GIỮ MÙ bộ vàng.** Mục `apply` trùng `(dashboard, id)` hoặc trùng PMID với một mục THẬT của bộ vàng chưa có nhãn bác sĩ thì không gọi, không in.
  - Bản đầu khớp theo PMID cộng tiêu đề. Siết lại thành chỉ theo PMID, để bản nối tiếp đổi chữ cũng bị ẩn.
- **Bộ năm.** Thêm bước ④-quinquies (chỉ chạy khi `--online`, có cờ `--khong-api`).
  - Không đổi `rc_final`, không chặn xuất.
  - Chỉ in dòng «Tổng:», dòng này mang nhãn CHƯA HIỆU CHUẨN.
- **Dạy agent.** Cập nhật `cap-nhat-chung-cu-y-khoa/SKILL.md`.

**Kiểm hồi quy.**
- `tools/test_kiem_ngu_nghia_api_xuat_goi_20261120.py`: 11 test, ngoại tuyến, dùng cầu nối giả.
- Thêm test bộ năm ở `test_xuat_goi_cap_nhat_20260926_ngoai_tuyen.py`: bộ giả lập nhận lệnh mới; mã 1 không đổi mã thoát; có cờ `--khong-api`; không chạy khi thiếu `--online`.
- Kiểm đột biến 11/11 bắt: bỏ giữ mù, bỏ chính sách, chấm cả consider, bỏ bộ đệm, bỏ trần, trần chi phí vẫn gửi tiếp, cảnh báo đổi mã thoát, bỏ cờ, bỏ nhãn chưa hiệu chuẩn, không online vẫn tải, bỏ bước.
  - Đột biến «bỏ nhãn» LỌT ở lượt đầu, vì chữ «CHƯA HIỆU CHUẨN» còn ở dòng Tổng. Đã siết test để đòi cả nhãn đầy đủ lẫn nhãn trên dòng Tổng.
- Chạy khô trên dữ liệu thật (không gọi API):
  - CKD 07/06: 4 mục, 1 kết quả lấy từ bộ đệm lượt đo thật 19/11.
  - Suy tim tổng hợp 13/11: 20 mục, ẩn 2 mục bộ vàng chờ nhãn.

**Còn treo.** Chuyển từ cảnh báo sang chặn là quyết định của bác sĩ sau khi gắn nhãn phần B và xem `bo_vang_kiem_ngu_nghia.py do --api`.
