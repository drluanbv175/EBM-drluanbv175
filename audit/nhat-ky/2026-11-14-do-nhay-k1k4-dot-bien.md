# 14/11/2026 — Đo độ nhạy K1–K4 bằng đột biến tổng hợp: bốn lỗ hổng của bộ kiểm lộ ra

**Bối cảnh.** Bộ vàng 20 mục (`tools/bo_vang_kiem_ngu_nghia.py do`) chỉ đo được báo động giả (K1 0/20, K4 1/20).
Độ nhạy chưa đo vì 20 mục đó không có ca sai nào. Chuyển K1–K4 từ CẢNH BÁO sang CHẶN là quyết định của bác sĩ (audit/16 §4),
nên cần số đo cả hai chiều.

**Công cụ mới** `tools/do_nhay_kiem_ngu_nghia.py`, không đổi hành vi `kiem_cheo_ngu_nghia.py` / `kiem_quan_the_chieu.py`:
- Đầu vào: mục `apply` thật từ dashboard ĐÃ PASS (luật `trang_thai_phai_sinh`), mỗi chủ đề lấy bản PASS mới nhất.
- Sinh đột biến có nhãn theo cấu trúc, tất định (hạt giống 20261114).
- Chạy đúng hàm kiểm thật và báo độ nhạy kèm KTC 95% Wilson.
- Đối chứng không đột biến cho báo động trên mục thật (cận trên của báo động giả).
- Báo cáo: `quality/eval/kiem-cheo-ngu-nghia/do-nhay-dot-bien-20261114.{json,md}`.

**Số đo 14/11/2026** (115 dashboard PASS · 826 mục apply · 663 mục có tóm tắt PubMed):

| Phép | n | Bắt | Độ nhạy (KTC 95%) |
|---|---|---|---|
| K1 | 187 | 99 | 53% (46–60%) |
| K2 | 169 | 166 | 98% (95–99%) |
| K3 | 602 | 322 | 53% (49–57%) |
| K4 | 107 | 66 | 62% (52–70%) |

- **Ngoài phạm vi thiết kế, 0% bắt:**
  - rụng điều kiện NGAY TRONG MỤC so với nguồn: 0/602;
  - mục đảo sang «không làm» khi nguồn ủng hộ: 0/582;
  - ngưỡng số nằm trong `action`: 0/40.
- **Đối chứng mức dashboard (nếu chuyển sang CHẶN):** K1/K2/K4 chặn 46/97 dashboard đã PASS; K3 chặn 102/115.

**Lỗ hổng lộ ra** (chưa vá trong lượt này, vì công cụ đo không được đổi hành vi bộ kiểm):

1. **`chuan_hoa()` xoá chữ trong tóm tắt văn bản thuần.** Hàm coi mọi đoạn «<…>» là thẻ HTML. Trong bản efetch, «<» là dấu
   so sánh («LNM risk < 3 %»), nên chữ từ đó tới dấu «>» kế tiếp bị xoá trước khi K1/K2/K4 đọc.
   - 7/298 nguồn bị cắt, trong đó 3 nguồn mất đoạn dài hơn 200 ký tự.
   - Có 3 lần K4 lọt vì câu «is not recommended» nằm trong đoạn bị xoá.
2. **K1/K4 đọc cả dòng tác giả và cơ quan.** «Children's Hospital» hay «Department of Paediatrics» khiến K1 tưởng nguồn có nêu
   «trẻ em», nên báo ✓ trên mục đã bị đổi quần thể (4 lần lọt ✓).
3. **Từ vựng.**
   - K1 không nhận «bệnh nhi», «trẻ vị thành niên», «người trưởng thành», «ĐTĐ1», «PSTM giảm», «phân suất tống máu còn bảo tồn»
     (84 lần lọt im).
   - K4 không nhận các dạng phủ định sau (35 lần lọt): thì hiện tại «does not reduce», «not effective», «did not result in»,
     «was not lower», «should not be considered», «not non-inferior».
   - Bộ lọc «kết cục phụ» bỏ cả «secondary analysis» và «secondary prevention» (3 lần lọt).
4. **K3 so khớp cấp TÀI LIỆU.**
   - 193/280 lần lọt là vì cùng cụm điều kiện còn ở chỗ khác trong bản xuất.
   - Khi cụm không còn ở chỗ khác, K3 bắt 79%.
   - K3 không coi giới hạn quần thể («ở người…», «ở bệnh nhân…»: 2/98 bắt) và ngưỡng số đứng trần (0/62) là điều kiện.

**Kiểm hồi quy:**
- `tools/test_do_nhay_kiem_ngu_nghia_20261114.py`: 20 test, ngoại tuyến, fixture tự dựng.
- Kiểm đột biến chính công cụ đo: 14/14 phép đỏ đúng chỗ, phục hồi xong `cmp` khớp.
- Phép M14 («thứ tự mức ở phần tử đích») sống sót lần đầu, vì với bộ kiểm thật nó là đột biến tương đương. Đã thêm test có
  hai dòng cho cùng phần tử đích; chạy lại thì đỏ.

**Giới hạn.**
- Đây là đột biến TỔNG HỢP: không thay bộ vàng do bác sĩ gắn nhãn, và không tự đổi chế độ chặn.
- Độ nhạy gộp của K1 phụ thuộc tỉ lệ cách viết mà bộ sinh chọn (chia đều). Nên đọc bảng theo biến thể trong báo cáo.

_Cần bác sĩ kiểm chứng._
