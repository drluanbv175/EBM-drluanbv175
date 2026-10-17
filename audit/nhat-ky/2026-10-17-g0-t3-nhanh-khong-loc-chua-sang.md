# 17/10/2026 — G0-T3: kiểm máy «0 lỗi» trong khi 13 PMID nhánh KHÔNG lọc chưa ai sàng

**Phát hiện:** hội đồng G0 đề tài C1a (biên bản `G0-DG-20261017T100649-43a39c66`). Người chấm chuyên môn kết luận «đạt có lưu ý», giám khảo «trả về sửa», nên biên bản ghi bất đồng. Nhưng cả hai cùng nêu một bộ lỗi.

**Nguyên nhân:**
1. Từ 14/10, `run_g0_auto.py` ghi thêm nhánh KHÔNG lọc thiết kế vào `G0_pubmed_raw.json` (C1a: 35 hit, lấy về 30, bộ lọc thiết kế đã loại 17). Tuy vậy:
   - `g0_tong_hop.kiem_tong_hop` chỉ đòi sàng nền CÓ lọc (16 PMID);
   - hợp đồng agent `tong-quan-y-van` chưa nhắc nhánh này;
   - kết quả: 13 PMID không ai sàng, trong đó PMID 42582692 liên quan trực tiếp; 5 hit vượt trần chưa lấy về.
2. `dung_lai_a1` không nạp `search_provenance.nhanh`. Vì vậy A1 dựng lại luôn in «Nhánh KHÔNG lọc thiết kế: chưa có…», và PI mất lời nhắc rà bài bị bộ lọc loại.
3. Mức bằng chứng trong A1 tính từ SỐ HIT. Một SR lạc đề đủ biến nó thành «TRUNG BÌNH — có 1 SR/MA, có thể cập nhật SR/MA hiện có», trong khi bảng sàng lọc ngay bên dưới xếp SR đó là «không liên quan».

**Cách vá (repo y khoa, PR dữ liệu C1a #155 cùng các commit công cụ):**
- `kiem_tong_hop(…, khong_loc)` đòi mọi PMID trong `pmid_bo_loc_da_loai` nằm ở một trong ba nơi:
  - `sang_loc`;
  - `nguon_bo_sung`;
  - khoá mới `sang_loc_khong_loc` (bài lạc đề kèm lý do; khoá riêng nên không vào dấu vân tay G0).
- Số hit lớn hơn số lấy về thì đòi `khong_loc_vuot_tran`.
- Thêm khoá bắt buộc `muc_bang_chung_sau_sang_loc`.
- `hoi_dong_cong._kiem_tong_hop_g0` đọc nhánh KHÔNG lọc từ raw.
- `dung_lai_a1` nạp provenance.
- Mức theo số hit nay ghi rõ «CHƯA sàng lọc», và in kèm mức sau sàng lọc.
- Repo gốc: hợp đồng G0-T3 của `tong-quan-y-van` thêm nhánh KHÔNG lọc và mức sau sàng lọc. Bản cặp ở repo y khoa giống hệt.

**Kiểm:**
- `tests/test_g0_t3_khong_loc_muc_sau_sang_loc_20261017.py`: 8 test.
- Đột biến 5/5 bị bắt.
- Bộ test G0 và hội đồng sẵn có (378 test) vẫn đạt sau khi bổ sung fixture cho hợp lệ.
- Chạy trên dữ liệu thật C1a TRƯỚC khi sửa nội dung: bộ kiểm mới báo đúng 3 lỗi mà hội đồng nêu.

**Bài học:** thêm một nhánh dữ liệu cho cổng (ở đây là `khong_loc`) thì phải nối dây cùng lúc ở ba nơi: bộ kiểm cấp nhiệm vụ, đường dựng lại, và hợp đồng agent. Thiếu một nơi thì kiểm máy «xanh» trên một tập dữ liệu không ai đọc.
