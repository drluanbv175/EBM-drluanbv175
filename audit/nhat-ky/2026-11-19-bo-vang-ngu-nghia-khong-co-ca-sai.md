# 19/11/2026 — Bộ vàng kiểm chéo ngữ nghĩa không có ca SAI nào ⇒ không đo được bỏ lọt; thêm đột biến có kiểm soát, mục thật phân tầng và bộ kiểm API

## Bối cảnh
Bác sĩ hỏi có cần API Claude cho hệ cập nhật chứng cứ. Câu trả lời đưa ra: nên dùng cho kiểm chéo ngữ nghĩa mục `apply`
(K1–K4), nhưng phải có bộ vàng do bác sĩ gắn nhãn trước. Bác sĩ: «Bộ vàng này hiện chưa có. Hãy giải quyết vấn đề này
giúp tôi».

**Đính chính trong phiên:** câu «bộ vàng chưa có» là SAI. Lỗi đến từ phép đếm nhãn đọc nhầm khoá (`nhan` thay vì
`nhan_bac_si`). Bộ vàng đã có từ 20/10/2026: 20 mục có nhãn, tức 16 mục khác nhau vì 4 cặp trùng giữa các bản dashboard.
Vấn đề thật nằm ở chất lượng bộ vàng: (1) cả 20 nhãn đều do máy soạn sẵn rồi bác sĩ xác nhận (`de_xuat_boi`), chưa có nhãn
nào bác sĩ gắn độc lập; (2) ở trục quần thể và trục chiều, cả 20 mục đều ĐÚNG; ở trục điều kiện chỉ có 1 mục sai (mục 10).
Vì vậy K1, K4 và K4b không đo được bỏ lọt, chỉ đo được báo động giả, và K3b chỉ có đúng 1 ca sai để đo.
Đột biến tổng hợp ngày 14/11 (`do_nhay_kiem_ngu_nghia.py`) đo độ nhạy trên lỗi sinh theo khuôn:

| Phép | Độ nhạy |
|---|---|
| K1 | 99% |
| K3b | 1% |
| K4b | 25% |

Đó không phải lỗi do người soạn và chưa có bác sĩ duyệt.

## Bác sĩ chọn
«Kết hợp hai cách (Khuyến nghị)»:
- (a) máy soạn đột biến có kiểm soát, bác sĩ duyệt danh sách một lượt;
- (b) thêm 40 mục thật rút theo tầng, bác sĩ gắn nhãn ĐỘC LẬP trên phiếu không in kết quả máy;
- (c) dựng bộ kiểm dùng Claude API, đo cạnh luật cứng; bác sĩ quyết có bật hay không.

## Đã làm
- **(a)** `quality/eval/kiem-cheo-ngu-nghia/dot-bien.de-xuat.json` gồm 56 đột biến từ 16 mục gốc:
  - phân bổ: 22 sai quần thể · 18 sai chiều · 16 rụng điều kiện;
  - mỗi biến thể sai đúng MỘT trục, nhãn dự kiến suy từ phép sửa;
  - `kiem_de_xuat` chốt các bất biến: trục bị đột biến = false; trục khác chỉ kế thừa đúng nhãn gốc hoặc null; chỉ sửa trường thuộc kiểu; phải thật sự đổi nội dung.
  - Lời duyệt: `bo_vang_kiem_ngu_nghia.py duyet-dot-bien --loi "<nguyên văn>"`. Chạy khô mặc định. Lời mơ hồ (vừa «tất cả» vừa liệt kê mã, mã lạ, thiếu lời duyệt) thì không ghi gì.
  - Kết quả ghi vào `bo-vang.dot-bien.json`, kèm `de_xuat_boi` để số đo luôn nói rõ nguồn gốc nhãn.
- **(b)** `them-muc-that --so-muc 40`: rút từ bản ĐÃ PASS mới nhất của mỗi chủ đề, dùng đúng luật của `do_nhay`.
  - hạn ngạch theo tầng: phủ định 10 · có điều kiện 12 · nhóm đặc biệt 12 · khác 6;
  - tối đa 2 mục mỗi dashboard; loại mục trùng định danh + hành động;
  - đã thêm 40 mục (mục 21–60), cả 40 có tóm tắt PubMed, nhãn để trống.
  - Phiếu Word: phần A (đột biến, bản gốc cạnh bản sửa) và phần B (chỉ in mục chưa nhãn, vẫn mù với máy).
- **(c)** `tools/kiem_ngu_nghia_api.py` đi qua cầu nối `api_claude_nc.py`, nên có sẵn: trần chi phí tháng, `stop_reason`, khoá, sổ chi phí theo nguồn, nhật ký sức khoẻ.
  - Mô hình chỉ thấy tiêu đề · quần thể · hành động của mục và tóm tắt nguồn; không thấy nhãn, mã mục, dashboard, cũng không biết mục là đột biến.
  - Kết quả lưu ở bộ đệm ngoài git, khoá theo prompt + model + mục + tóm tắt.
  - `do --api` đặt API cạnh luật cứng theo ba trục, trên cùng các mục.
  - Công cụ KHÔNG nối vào dây chuyền xuất gói.
- **Hòm việc:** thêm `giac_quan_bo_vang_ngu_nghia` (👤), báo số đột biến chờ duyệt và số mục chưa nhãn.

## Kiểm hồi quy
`tools/test_bo_vang_mo_rong_20261119.py` có 57 phép, OFFLINE. Một phép dùng đúng `api_claude_nc.goi` với khách giả; phép này bỏ qua khi không có repo y khoa.
Kiểm đột biến bắt 9/9:
1. bỏ chốt «trục bị đột biến phải false»;
2. bỏ chốt «tất cả + liệt kê mã»;
3. bỏ trần 2 mục/dashboard;
4. phiếu in cả mục đã nhãn;
5. trộn đột biến vào số mục thật;
6. lộ mã mục vào prompt;
7. không dừng khi chạm trần;
8. chạy khô vẫn gọi;
9. ghi bộ đệm thật dưới pytest.

Chạy thật một lượt nhỏ (3 mục, ≈ 0,02 USD): JSON đúng khuôn; prompt cache đọc 1.101 token ở lượt 2–3; mục 3 nhận null ở trục điều kiện, khớp nhãn «?» của bác sĩ.

## Còn lại (việc của bác sĩ)
Duyệt phần A, gắn nhãn phần B, rồi chạy `python3 tools/bo_vang_kiem_ngu_nghia.py do --api`. Bật bộ kiểm API (cảnh báo hay
chặn) là quyết định của bác sĩ sau khi xem số đo (audit/16 §4).
