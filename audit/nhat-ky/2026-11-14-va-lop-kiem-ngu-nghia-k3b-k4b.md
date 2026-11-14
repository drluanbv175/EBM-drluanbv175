# 14/11/2026 — Vá bốn lỗ hổng K1–K4 đo được và thêm K3b/K4b (vẫn CẢNH BÁO)

**Bối cảnh.** Báo cáo đột biến tổng hợp `quality/eval/kiem-cheo-ngu-nghia/do-nhay-dot-bien-20261114` (nhật ký
`2026-11-14-do-nhay-k1k4-dot-bien.md`) chỉ ra bốn lỗ hổng của lớp kiểm ngữ nghĩa và hai lớp lỗi không phép nào bắt.
Bác sĩ nói «Tiếp tục» (14/11/2026, ~14:50) sau khi phiên chính đề xuất vá. Quyết định chuyển K1–K4 sang CHẶN vẫn là của
bác sĩ: lượt này giữ MỌI phép ở mức CẢNH BÁO (bước ④-bis/④-ter của `xuat_goi_cap_nhat.py` không đổi mã thoát).

**Đã vá.**
1. `chuan_hoa()` (`kiem_cheo_ngu_nghia.py`) chỉ bỏ thẻ HTML THẬT («<» liền tên thẻ). Tóm tắt nguồn đi qua
   `kiem_quan_the_chieu.chuan_hoa_nguon()` (chỉ bỏ thẻ định dạng nội dòng). Số nguồn bị xoá chữ: 7/298 → 0/298.
2. K1/K2/K4/K3b/K4b chỉ đọc tiêu đề + THÂN tóm tắt (`than_nguon`). Không còn đọc dòng trích dẫn, tác giả cá nhân hay tổ
   chức, cơ quan, ©, COI, DOI/PMID.
3. Từ vựng:
   - K1 nhận «bệnh nhi», «(trẻ) vị thành niên», «người trưởng thành», «ĐTĐ1/ĐTĐ2», «PSTM giảm/bảo tồn», «thai phụ»…;
     phía nguồn cố ý KHÔNG có «child» trần (Child-Pugh).
   - K4 nhận «does not reduce», «did not result in», «was not lower», «not effective», «not non-inferior»,
     «should not be considered».
   - Bộ lọc «kết cục phụ» chỉ bỏ câu nói về kết cục phụ, không bỏ câu chứa «secondary analysis/prevention».
   - Chặn mới: câu mà tín hiệu ngược chiều đứng SAU «if/whether/in whom/when» (trừ «when compared») là mệnh đề giả định,
     không báo. Đo trên mục thật: 5/7 báo động K4 mới sinh ra từ từ vựng mở rộng thuộc dạng này.
4. K3 so theo TỪNG MỤC, nhưng chỉ ở sản phẩm in theo mục (Word: «ITEM-xx. <tiêu đề>»). Bản đọc vẫn so cả tài liệu, vì nó
   sắp nội dung theo chủ đề và chỉ trích «(item-47, item-48)» trong ngoặc.
   - Lần thử đầu cắt đoạn theo tiêu đề: 80 dòng trên mục thật chuyển ✓→🟠, tất cả đều ở bản đọc.
   - Lần thử hai dựa vào việc định danh có mặt: vẫn còn 40 dòng, vì bản đọc trích định danh.
   - Bản cuối dựa vào mốc «định danh liền tiêu đề»: 0 dòng chuyển trên mục thật.

**Thêm (ở `kiem_quan_the_chieu.py`, chạy cùng bước ④-ter):**
- **K3b.** Tìm câu khuyến cáo CÓ ĐIỀU KIỆN của nguồn (động từ khuyến cáo + dấu điều kiện, không phải câu mô tả phạm vi tài
  liệu) có chung thuật ngữ La-tinh với hành động của mục. Báo 🟠 khi một trong hai điều sau xảy ra:
  - câu nguồn có ngưỡng kèm toán tử mà mục không nhắc chỉ số đó;
  - hành động của mục không còn dấu điều kiện nào.
- **K4b.** Mục là khuyến cáo «KHÔNG làm» thật (loại phủ định kép «không từ chối/không ngừng…» và từ mô tả «không dung
  nạp/không triệu chứng…»). Kết luận của nguồn có câu ủng hộ và không có câu chống/hại ⇒ 🟠.

**Số đo 14/11/2026** (cùng hạt giống 20261114, 115 dashboard PASS, 663 mục có tóm tắt;
`do-nhay-dot-bien-20261114c.{json,md}`):

| Phép | Trước | Sau | Báo động trên mục thật (cận trên): trước → sau |
|---|---|---|---|
| K1 | 99/187 (53%) | 186/187 (99%) | 19 → 13 |
| K2 | 166/169 (98%) | 168/171 (98%) | 14 → 12 |
| K3 | 322/602 (53%) | 374/604 (62%) | dòng 🟠 889/3504 → 888/3530 |
| K3b (rụng trong mục) | 0/602 | 7/604 (1%; riêng phần phán được 7/26) | — → 4 |
| K4 | 66/107 (62%) | 106/107 (99%) | 51 → 52 |
| K4b (mục đảo «không làm») | 0/582 | 145/581 (25%; riêng phần phán được 145/258) | — → 0 |

- **Bộ vàng 20 mục** (`bo_vang_kiem_ngu_nghia.py do`, nay đo cả K3b/K4b):
  - K1 vẫn báo động giả 0/20, K4 vẫn 1/20.
  - K3b báo động giả 0/18 nhưng BỎ LỌT mục duy nhất bác sĩ gắn «rụng điều kiện».
  - K4b chỉ có 1 mục để chấm, không báo giả.

**Đánh đổi và giới hạn — đọc trước khi dùng số.**
- K1/K4 tăng vọt chủ yếu vì lượt này thêm vào từ điển ĐÚNG những cách viết mà bộ sinh dùng. Con số đó đo CƠ CHẾ trên các
  cách viết ấy. Cách viết ngoài cả hai danh sách CHƯA được đo; cần một danh sách biến thể giữ riêng.
- K3b rất yếu: tóm tắt tiếng Anh, mục tiếng Việt, mệnh đề định tính không so được nội dung. Thiết kế chọn «thà im còn hơn
  báo giả». Ba phương án đã đo trên mục thật:
  - đối chiếu ngưỡng/quần thể cho mọi câu nguồn: 62 báo động, gần hết là giả, bắt 2 đột biến;
  - mệnh đề điều kiện KHÔNG neo thuật ngữ: 25 báo động, bắt 28;
  - bản chọn (có neo thuật ngữ): 4 báo động, bắt 7.
- K4b cho ⚪ khi nguồn không có câu ủng hộ rõ (320/581, đa số là tóm tắt guideline chỉ mô tả phạm vi). Khi Kết luận có bất kỳ
  câu chống/hại nào thì K4b coi là cùng chiều (113 lần lọt); bộ lọc rộng có chủ ý để tránh báo giả.
- Các lỗ hổng còn lại:
  - ngưỡng số nằm trong `action` (0/40, K1/K2 không đọc action);
  - cụm điều kiện ngoài từ điển K3 («ở người…», ngưỡng đứng trần): 116 lần K3 không trích được cụm nào.
- K1–K4/K3b/K4b vẫn CẢNH BÁO. Chuyển sang CHẶN là việc của bác sĩ sau khi xem số đo.

**Kiểm hồi quy.**
- `tools/test_lop_kiem_ngu_nghia_20261114c.py`: 31 test ngoại tuyến, fixture tự dựng.
- 7 test cũ của `test_do_nhay_kiem_ngu_nghia_20261114.py` được sửa theo hành vi mới:
  - ánh xạ lớp sang K3b/K4b;
  - từ điển đã mở rộng;
  - chẩn đoán chuẩn hoá đo theo mẫu mới.
- Bộ test `tools/`: 4721 passed, 38 skipped.
- Kiểm đột biến, 34 phép (sao lưu `cp` + `cmp` trước, khôi phục xong `cmp` khớp mọi tệp):
  - Lượt đầu 30/33 đỏ. Ba phép sống sót đều do lỗi FIXTURE, không phải lỗi cơ chế:
    - tác giả cá nhân cũng bị bộ nhận danh sách tác giả bỏ ⇒ cần fixture tác giả TỔ CHỨC;
    - bộ nhận danh sách tác giả chỉ cần cho khuôn «RETRACTED ARTICLE»;
    - fixture Child-Pugh có nêu «adults» nên cả hai vế đều khớp.
  - Sửa fixture xong: 33/33 đỏ.
  - Sau khi đổi thiết kế mốc K3, thêm phép M16b (bỏ cổng «một nửa số mục»). M16b sống sót vì fixture không có mục nào mang
    mốc; thêm fixture 1/3 mục có mốc ⇒ 34/34 đỏ.

_Cần bác sĩ kiểm chứng._
