# 20/10/2026 — K4 bỏ lọt mọi câu «khuyến cáo chống» của guideline (GRADE «against», USPSTF D)

**Phát hiện.** Bộ vàng K1–K4 vừa gắn nhãn (20 mục, bác sĩ xác nhận 20/10/2026) không có mục nào sai chiều, nên chưa đo
được độ nhạy. Đo bù trên câu nguồn THẬT: quét kho toàn văn (767 tệp) và tóm tắt bộ vàng, được 85 câu ngược chiều theo cách
nói chuẩn của guideline/thử nghiệm. K4 bắt 70/85, nhưng:
- 0/8 câu «(strong|conditional) recommendation against», «recommend against»;
- 0/3 câu USPSTF D («recommends against… (D recommendation)», «harms… outweigh the benefits»).

Đây đúng là kiểu tín hiệu «nguồn khuyến cáo KHÔNG làm» quan trọng nhất. Ngay trong bộ vàng có ca thật: mục 2 dựa trên USPSTF
«recommends against screening», nhưng K4 không thấy. Nếu một mục ghi «nên tầm soát» dựa trên nguồn đó, K4 sẽ bỏ lọt.

**Cách vá** (`tools/kiem_quan_the_chieu.py`):
1. `_NGUOC` nhận thêm `recommend/suggest/advise against`, `recommendation against`, `harms … outweigh the benefits`,
   `(D recommendation)`, `grade D recommendation`. Các mẫu này vào `_LUON_BAO`, nên không bị lọc như câu kết cục phụ/an toàn.
2. K4 nhận biết chiều của CHÍNH mục qua `muc_phu_dinh(it)`: tiêu đề hoặc hành động mở đầu bằng «không / tránh / ngừng /
   chống chỉ định». Khi đó tín hiệu ngược chiều của nguồn là cùng chiều ⇒ «khớp»; câu nguồn giữ ở `cau_bo_qua`. Trường hợp
   loại trừ: «không chỉ / không những» (câu khẳng định); «bỏ» không tính vì «Bỏ thuốc lá» là khuyến cáo NÊN làm.
3. `bo_vang_kiem_ngu_nghia.do` truyền thêm `action` vào `kiem_muc`.

**Số đo sau vá.**
- Câu thật: 81/85; câu «against» 8/8; USPSTF D 3/3.
- Bộ vàng: mục 2 nay «khớp». Báo động giả từ 0/20 lên 1/20: mục 9 có câu «recommend against» nói về corticosteroid, không
  phải kháng sinh. Đánh đổi có chủ ý: đọc thêm một câu rẻ hơn bỏ lọt một khuyến cáo chống. K4 vẫn chỉ CẢNH BÁO.

**Kiểm hồi quy.** `tools/test_k4_khuyen_cao_chong_20261020.py` gồm 20 ca, câu thử tự viết theo khuôn GRADE/USPSTF, không chép
nguyên văn. 7 phép đột biến đều đỏ. Lần đầu chạy, test bắt chính lỗi của bản vá: «Bỏ qua…» và «Không chỉ…» bị nhận là phủ
định; đã siết lại luật.
