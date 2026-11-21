# 21/11/2026 — K17 «đạt giả» và «đòi sai» lộ ra khi bộ sinh đề cương dựng đủ mục chuẩn

**Bối cảnh.** Bác sĩ: mọi đề tài, mọi thiết kế phải đạt từng mục chuẩn quốc tế và Việt Nam. K17
(`medical-ebm-automation/tools/kiem_chuan_de_cuong_theo_muc.py`) lúc đầu chỉ chặn đề cương theo khuôn BVQY175
vì bộ sinh `sinh_de_cuong_nop_hoi_dong.py` tạo đề cương thiếu khoảng 50 mục STROBE/RECORD/TT43 trên 8 đề cương giả
lập (đo 21/11/2026). Khi nâng bộ sinh để dựng từng mục từ quyết định đã chốt và gỡ điều kiện khuôn (K17 chặn cả bản
nháp), việc soát bằng chứng TỪNG mục đạt lộ ra các lỗi của chính bộ kiểm.

**Nguyên nhân (mỗi dòng một lỗi thật, có số đo trên đề cương giả lập/fixture):**
- Nhãn có mặt được tính là nội dung có mặt: «Lý do chọn nhóm bệnh và nhóm chứng: ………» đủ cho yếu tố «lý do»; nhãn
  «Nhóm chứng (… ghép cặp): ………» kích hoạt điều kiện ghép cặp dù PI chưa khai.
- Hàng TIÊU ĐỀ bảng làm bằng chứng: bảng «| Hạn chế | Chiều hướng sai lệch |» với mọi ô để trống vẫn đạt STROBE 19.
- Điều kiện «có mục tiêu phân tích» quét CẢ văn bản: chữ «OR» của chuỗi tìm PubMed, «liên quan đến» của câu đạo đức
  biến đề tài cắt ngang MÔ TẢ thành đề tài phân tích ⇒ đòi phơi nhiễm, ước lượng thô/hiệu chỉnh.
- Phần «đối tượng» khớp cả «Đặc điểm đối tượng nghiên cứu» của chương kết quả ⇒ STROBE 6a lấy «lý do loại» của ghi
  chú sơ đồ làm «lý do chọn ca và chứng».
- Điều kiện ghép cặp chỉ nhận chữ «ghép cặp» ⇒ đề tài viết «ghép theo giới…, 2 chứng : 1 ca» bị coi là không ghép.

**Cách vá (PR y khoa nhánh `claude/sinh-de-cuong-dat-k17-20261121`):** mệnh đề còn ô trống không là bằng chứng
(`o_trong_quanh`, áp cả cho điều kiện; câu thật kèm ô số quyết định ở câu SAU vẫn tính); hàng tiêu đề bảng (ngay sau
là hàng ngăn) chỉ cho nghĩa cột; điều kiện phân tích chỉ đọc phần Mục tiêu/Câu hỏi/Giả thuyết (`MUC_TIEU_PHAN_TICH`);
phần đối tượng neo đầu đề mục; ghép cặp nhận «ghép theo…» và «n chứng : 1 ca».

**Kiểm hồi quy:** test `test_k17_chuan_de_cuong_theo_muc_20261121.py`, `test_sinh_de_cuong_dat_k17_20261121.py`;
kiểm đột biến 13/13 chốt mới bị bắt (đỏ đúng chỗ, khôi phục xanh) — một đột biến lọt lần đầu vì phép thử chứa cả hai
nhánh của điều kiện ghép cặp, đã tách phép thử từng nhánh. Giả lập trọn vòng 24 kịch bản khoá gói G10 với K17 chặn
bản nháp; hai đề cương thật (BTM, C1a) vẫn đạt K1–K17.

**Bài học:** soát bằng chứng của TỪNG mục đạt, không chỉ mục thiếu — mỗi lần bộ sinh viết thêm nhãn/bảng mới là một
cơ hội để bộ kiểm «đạt giả» bằng chính chữ của nhãn.
