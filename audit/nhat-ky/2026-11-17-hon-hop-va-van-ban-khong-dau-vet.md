# 17/11/2026 — Thiết kế hỗn hợp chạy được trên chuỗi G0–G10; văn bản nộp không còn dấu vết soạn thảo hay dấu vết máy

## Bối cảnh
Sau đợt đề cương nộp sinh từ quyết định đã chốt (16/11), bác sĩ giao hai việc:
1. «Hãy giải quyết loại bỏ những giới hạn trên đảm bảo sự hoàn thiện, tính tự động và chuẩn mực nhất». Đó là sáu giới hạn
   đã báo: đặt vấn đề/tổng quan ngắn; chưa có hướng dẫn phỏng vấn định tính; chưa có phiếu đồng ý tiếng Anh; biểu mẫu
   nội bộ còn «(GIẢ LẬP — hồ sơ chưa có)»; bộ đếm «hỏi lặp» nhiễu; thiết kế hỗn hợp chưa được hỗ trợ.
2. «Tất cả đề cương hay nội dung văn bản hãy loại bỏ những dấu vết của một nội dung soạn thảo hay dấu vết của máy thực
   hiện; Hãy đóng vai trò là người nghiên cứu, điều phối và thực hiện các vấn đề của hệ thống».

## Quyết định kiến trúc (thiết kế hỗn hợp)
Hợp đồng 8 mã thiết kế của `gate_contract` giữ nguyên. Đề tài hỗn hợp mang MÃ CỦA CẤU PHẦN ĐỊNH LƯỢNG, nên G3, G4 và G6
chạy như mọi đề tài. Cấu phần định tính và kế hoạch tích hợp khai ở `gate_params.G1.mixed_methods` (repo y khoa
`tools/hon_hop.py`), theo ba mô hình Creswell & Plano Clark và bốn nhóm mục GRAMMS (O'Cathain 2008, PMID 18416914). Không
thêm mã thứ 9: một mã mới phải chạy được G3/G4/G6 riêng, mà cấu phần định lượng của đề tài hỗn hợp chính là một trong 8
thiết kế đã có.

## Đã làm (repo y khoa, nhánh `claude/gia-lap-bien-the-kho-20261116`)
- `hon_hop.py` (mới): kiểm khối theo GRAMMS; mã thiết kế phải là mã định lượng; dữ kiện cho đề cương; dòng của bảng tích
  hợp (joint display); PMID chuẩn GRAMMS + COREQ đã tra PubMed.
- G1: G1-AUTO-02e chặn khi khối hỗn hợp thiếu mục. G1-AUTO-02c, khi chặn một thiết kế ngoài 8 mã, chỉ đường cho thiết kế
  hỗn hợp. Hội đồng cổng gán G1-AUTO-02e cho G1-T1 (tổng tiêu chí 210 → 211).
- G2: phiếu đồng ý VI/EN có bước «Phỏng vấn sâu (chỉ những người được mời)»: chỉ ghi âm khi đồng ý, từ chối phỏng vấn vẫn
  tham gia. ICF tiếng Anh: phần suy được máy tự điền; phần chữ tự do lấy từ `gate_params.G2.icf_en`, máy không dịch máy.
  Số điện thoại/email liên hệ để dòng kẻ cho người điền tay.
- G4: SAP §17 khoá kế hoạch phân tích định tính và cách tích hợp.
- G7: Phương pháp §1 dẫn GRAMMS/COREQ kèm PMID, nên A12 kiểm rút bài trước khi đề cương nộp dẫn hai chuẩn này.
- Đề cương nộp:
  - câu thiết kế hỗn hợp; mục «Cấu phần định tính và tích hợp dữ liệu»; bảng tích hợp ở mục 5;
  - Phụ lục C chia C1 phiếu thu thập, C2 hướng dẫn phỏng vấn;
  - tổng quan tài liệu dựng từ chiến lược tìm G0 (số bài theo tầng, tra registry, kiểm rút bài, bảng bằng chứng chính);
  - hướng dẫn phỏng vấn cho đề tài định tính (COREQ mục 14).
- Văn bản không dấu vết:
  - dấu nguồn gốc máy dời ra `_dau_may_sinh/<tệp>.json` (sha256). Văn bản không còn dòng `<!-- … -->`, ghi chú giả lập ở
    bìa hay nhãn «bản nháp»;
  - K8 của `kiem_de_cuong_nop_hoi_dong` chặn các cụm DRAFT/bản nháp/AI soạn/máy sinh/«cần bác sĩ kiểm chứng»/GIẢ LẬP
    theo từng dòng;
  - bộ giả lập bỏ nhãn «DỮ LIỆU MÔ PHỎNG» khỏi bản diễn giải, bản phản biện, A12, bảng kiểm, và câu «dữ liệu mô phỏng»
    trong lời văn;
  - tính tổng hợp ghi MỘT lần ở HƯỚNG-DẪN của gói bàn giao.
- Bộ giả lập: kịch bản biến thể thứ 8 `rct_hon_hop` (RCT tin nhắn + phỏng vấn giải thích tuần tự). Bộ đếm «hỏi lặp» chỉ
  đếm nhãn có nghĩa (≥ 2 từ thực, không phải ô lồng).

## Ranh giới giữ nguyên
Lời nhắc «Cần bác sĩ kiểm chứng» của hệ KHÔNG bị bỏ, chỉ chuyển chỗ. Nó vẫn ở checkpoint và báo cáo cổng, ở dấu
`_dau_may_sinh/`, ở HƯỚNG-DẪN gói bàn giao và trong lời báo ở khung chat. Văn bản người đọc (đề cương nộp, phiếu đồng ý
trong phụ lục, bản thảo, bản phản biện) không mang nó. Khai báo dùng AI theo ICMJE trong bản thảo/bản phản biện là nội
dung bắt buộc của văn bản thật, nên được giữ, chỉ đổi «bản nháp» thành «bản thảo».

## Phát hiện: nhãn của bộ giả lập che ô trống
Ô mà hồ sơ giả lập không có câu trả lời từng được điền «(GIẢ LẬP — hồ sơ chưa có)». Nhãn này vừa là dấu vết máy trong
văn bản, vừa lọt qua `placeholder_contract`, nên bị đọc như ô đã có nội dung. Khi đổi sang lời trung tính «chưa có
thông tin» (hợp đồng ô trống nhận đúng là chưa điền), ba thiết kế định tính · dự báo · tổng quan gộp dừng ở G7
(G7-AUTO-05). G6 của chúng không sinh Bảng 1 nên G7 không chép được số. Như vậy kết quả «15/15 PASS_G10» trước đó
của ba thiết kế này là đạt giả do nhãn che. Khoảng trống G6/G7 tách thành việc riêng; đề cương nộp không bị ảnh hưởng
(ô hồ sơ chưa có thành dòng chấm điền tay).

## Kiểm
- `tests/test_hon_hop_20261117.py` (23 phép); đột biến 13/13 đỏ đúng chỗ rồi phục hồi xanh. Lượt đầu một đột biến
  sống sót vì nó không chạm phần phép thử khẳng định; đột biến gỡ hẳn câu chỉ đường thì đỏ.
- Lượt sạch 16 kịch bản từ G0 (khoá giả):
  - 13 tới `PASS_G10_RELEASE_PACKAGE_LOCKED`, kể cả `rct_hon_hop`; 3 dừng ở G7 như trên;
  - 0 ô lỗi máy (hỏi lại điều đã chốt/hỏi lặp) ở cả 16;
  - 16/16 đề cương nộp mã 0 (K1–K8), không còn «GIẢ LẬP»/«mô phỏng»/«bản nháp»;
  - đề cương `rct_hon_hop` 637 dòng, COREQ [17] + GRAMMS [18] đã qua A12.
- CI PR #292: một phép thử dùng đối tượng giả thiếu `_gia_tri_kinh_te` (10612 đạt / 1 hỏng); đã sửa.
