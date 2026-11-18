# 18/11/2026 — Đo sống sau khi gộp: BTM thiếu mục «Hạn chế», SL-09 báo sai việc, «Đn2» bị hạ chữ, A12 không thử lại lô JSON hỏng

## Bối cảnh

Bác sĩ hỏi hệ đã hoàn thiện tự động và các cổng đã đồng bộ chưa, rồi giao ba việc: thêm mục «Hạn chế» cho đề cương BTM,
sửa thông điệp SL-09, chạy lại kiểm máy Claude API. Đo sống trên bản đã gộp #307/#308 (y khoa):
- BTM: 23/26 trục nhất quán khớp;
- C1a: 26/28 trục khớp; chữ ký G4 và G10 hết hiệu lực vì kế hoạch phân tích (1.5) và gói G10 đổi sau khi ký.

## Lỗi hệ lộ ra và đã sửa (PR y khoa #310, dữ liệu #311)

1. **Đề cương BTM không có mục «Hạn chế»** dù G1 chốt 3 «hạn chế mở» và văn bản hai lần hứa «nêu rõ trong hạn chế».
   - Nguyên nhân che lỗi: SL-09 báo «chưa khai neo_han_che» (3 lỗi), nên người đọc tưởng chỉ cần điền bảng.
   - Đã sửa: SL-09 nay báo MỘT lỗi «CHƯA CÓ mục Hạn chế» kèm tên từng hạn chế.
   - Dữ liệu: thêm mục 4.11, dựng từ đúng dữ kiện đã chốt.
2. **Bộ sinh hạ «ĐN2» thành «Đn2».** `_ha_hoa_nhan_manh` hạ mọi cụm IN HOA không phải ASCII; chữ «Đ» làm «ĐN2» lọt vào.
   Đề cương ghi «Đn1…Đn9», kế hoạch phân tích ghi «ĐN1…ĐN9».
   - Đã sửa: cụm có chữ số giữ nguyên; K8 chặn «Đn<số>».
3. **A12: một lô trả JSON hỏng làm 12/51 cặp «không kiểm được», công cụ không thử lại.**
   - Đã sửa: gửi lại đúng lô đó một lần. Cắt cụt không gửi lại; câu trả lời tốt không gửi thêm lượt.
   - Chạy lại trên BTM: 0 lô hỏng.
4. **A12 gắn cờ «số không thấy: 4.9» cho «mục 4.9»** (lặp ở cả ba lượt hôm nay). Đã sửa: bỏ qua số đứng sau
   mục/bảng/phụ lục/hình/sơ đồ/chương/§.
5. **K8 bỏ sót** «(= descriptive)» và «(quyết định 28/10/2026)». Đã thêm cả hai mẫu.
   - Đo: BTM cũ 1 dòng; BTM đã sửa, C1a và 31 đề cương giả lập: 0.

## Kiểm máy lượt 3 (≈ 0,37 USD gồm cả lượt chạy lại A12)

- **A12:** 9 cặp cần xem. Một cặp là việc đã biết: dải «15,32–31,1%» chưa có nguồn, chờ hỗ trợ TLTK chỉ có DOI (B2).
  Các cặp còn lại máy đòi abstract nêu chi tiết chỉ có ở toàn văn hoặc ở metadata (tác giả, năm) — kiểu nhầm bác sĩ
  đã gắn nhãn sáng nay. Cặp còn lại là cờ giả «mục 4.9».
- **Phản biện máy:** 17 phát hiện.
  - 7 mục máy đúng, đều là lỗi biên tập, đã sửa ở #311.
  - 1 mục cần PI quyết: «cân nhắc đăng ký công khai đề cương» trong khi G2 ghi không đăng ký.
  - Còn lại máy nhầm: mốc thời gian vốn khớp; cắt ngang trong cửa sổ 12 tháng; 39 hồ sơ trích lại khác 10 hồ sơ tập;
    16 tham số; danh sách mã loại trừ «ví dụ» so với codebook; mã biến ở phiếu thu thập.

## Ranh giới đã giữ

- Không gắn nhãn phiếu thay bác sĩ; nhãn đề nghị trình trong câu trả lời.
- Quyết định đăng ký công khai và việc có ghi «KDIGO 2022» vào tên đề tài hay không để chủ nhiệm quyết.
- Không chạy lại kiểm máy lần thứ tư. Báo cáo lượt 3 gắn với bản trước 7 sửa biên tập; chính sách «tự chạy khi đề cương
  đổi» sẽ chạy lại sau khi #311 gộp.

## Bài học

- **Thông điệp lỗi phải nói việc cần làm, không nói triệu chứng.** «Chưa khai neo» khiến một lỗ nội dung nằm 3 ngày.
- **Mỗi lượt máy đọc lại lại tìm thêm vài lỗi biên tập nhỏ.** Dừng theo ngân sách và theo việc bác sĩ duyệt nhãn,
  không chạy vòng vô hạn.
- **Một phép đo «không kiểm được» do lỗi kênh phải được thử lại trước khi báo,** nếu không 23% số cặp mất trắng.
