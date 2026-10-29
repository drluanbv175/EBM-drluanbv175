# 29/10/2026 — Mục «Áp dụng» đã cập nhật bản nối tiếp không bao giờ rời hòm việc (kết luận `da_cap_nhat`)

**Bác sĩ yêu cầu:** «Hoàn thiện 2 việc còn lại» — việc 1 là «55 mục 'apply' có nguồn tổng hợp MỚI HƠN» trên hòm việc.

**Đo:**
- Gom lại 29/10 (`state/gom-vuot-qua-day-du-20261029.py`, cùng hàm của `dat_canh_chung_cu_moi.py`): 165 mục `apply`,
  58 đã xét xong, 63 còn mở = 55 mục ĐÃ có trong phiếu sàng lọc 25/10 (không thêm nguồn mới nào từ đó) + 8 mục mới của hai
  dashboard dựng 29/10 (polyp, u gan — phiên khác đang sửa, để nguyên).
- Trong 55 mục: 48 nhóm G (lô 1–2 bác sĩ đã ghi 27–28/10, còn G21–G68) và 7 nhóm U. Cả 7 mục U ĐÃ được cập nhật bằng phiên
  bản nối tiếp ngày 25/10: nguồn đề xuất chính có trong bản dashboard hiện hành.
- Bác sĩ chọn (AskUserQuestion 29/10): ghi cả 7 mục U «đã xét — đã cập nhật» và giữ cả 48 mục G. Ghi 55 mục, 0 lỗi.
- Chạy lại `dat_canh_chung_cu_moi.py`: 7 mục U VẪN được đếm. Nguyên nhân: sổ chỉ có `can_cap_nhat`, loại KHÔNG đóng, chỉ rời
  danh sách khi PMID đang dùng đổi. Cập nhật bằng phiên bản nối tiếp (bộ nhớ «sàng lọc vượt qua — nhóm U») cố ý giữ mục cũ
  `apply` + `flag` sang mục mới `consider` ⇒ PMID cũ không bao giờ đổi ⇒ mục nằm mãi trong hòm việc dù đã cập nhật xong.

**Vá:**
- `tools/ghi_vuot_qua_da_xet.py`: thêm kết luận ĐÓNG `da_cap_nhat`. Máy chỉ nhận khi ĐO ĐƯỢC gói đã cập nhật: một bản
  dashboard HIỆN HÀNH (bỏ bản đã bị phiên bản nối tiếp thay, theo đúng `chi_ban_moi_nhat`) vừa dùng PMID đó vừa chứa ít nhất
  một nguồn mới đã xét (khớp nguyên số, không khớp chuỗi con). Không thấy ⇒ mã 2, không ghi, hướng dùng `can_cap_nhat`.
  Bản ghi lưu tên gói làm bằng chứng ở `de_xuat_tu`.
- `tools/dat_canh_chung_cu_moi.py`: `KET_LUAN_DONG` thêm `da_cap_nhat`. Nguồn mới chưa xét xuất hiện ⇒ mục tự mở lại như cũ.
- `can_cap_nhat` giữ nguyên nghĩa (bác sĩ thấy cần cập nhật, gói chưa cập nhật).

**Kiểm:** `tools/test_vuot_qua_da_cap_nhat_20261029.py` (8 ca: đóng/mở lại; ghi khi gói hiện hành có nguồn mới; từ chối khi
gói chưa cập nhật; bản cũ đã bị thay không được tính; nguồn mới ở gói khác không tính; chuỗi con của nguồn mới; chuỗi con của
PMID đang dùng; `can_cap_nhat` không đổi). 6 đột biến đều đỏ đúng chỗ — lần đầu đột biến «khớp chuỗi con» sống sót vì một ca
gộp hai phép khớp, đã tách thành hai ca. Bộ test cũ `test_vuot_qua_da_xet_20261018.py` + `test_dat_canh_chung_cu_moi_ban_moi`
vẫn xanh.

**Sau khi gộp:** ghi lại 7 mục U bằng `da_cap_nhat` theo đúng lời bác sĩ đã ghi (câu hỏi đã nêu «đã xét — đã cập nhật»).
