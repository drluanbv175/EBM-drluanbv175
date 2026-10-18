# 18/10/2026 — Cầu nạp sổ cái hub: phiên bản nối tiếp + 193 thẻ trùng do nạp lặp 13/07

## Hai lỗ hổng

**(1) Phiên bản nối tiếp.** `EBM_MASTER/tools/ingest_dashboard.py` chống trùng theo `key_of` (DOI > PMID
> topic) + độ giống chủ đề ≥ 0,95. Đúng cho dashboard mới, sai cho bản nối tiếp cùng lát cắt
(`..._HopNhat_20260614` → `..._HopNhat_20261018`): mục giữ tiêu đề bị coi là trùng ⇒ hub giữ nội dung
/decision CŨ; mục đổi tiêu đề/nguồn thành thẻ song song. Phiên 18/10 đã cập nhật tay mạch máu não.
Đo 18/10 trên BẢN SAO sổ cái: một lượt `sync_all.py` kế tiếp (nạp cả hai bản) vẫn hồi sinh 2 thẻ nội
dung cũ từ bản 20260614 (ITEM-02 đổi nguồn, ITEM-03 đổi tiêu đề).

**(2) Thẻ trùng tồn đọng.** 77 cụm cùng khoá + trùng tiêu đề, 270 thẻ, 193 thẻ thừa — TẤT CẢ thẻ thừa
tạo 13/07/2026. AUDIT_LOG ghi bốn lượt `sync_all.py` liên tiếp 12–13/07 mỗi lượt +72/+59/+61/+59 thẻ
rồi +0 từ lượt thứ năm. Nguyên nhân: bản cầu nạp 11–13/07 (ngưỡng 0,5 — dấu vết «topic similarity <
0.5» trong history) so thẻ mới với MỘT thẻ cho mỗi khoá; guideline trích nhiều khuyến cáo cùng DOI nên
thẻ đem so thường là khuyến cáo khác ⇒ mỗi lượt nạp lặp sinh thêm một bản sao. Mã hiện hành so với
MỌI thẻ cùng khoá (đã vá từ 13/07, chưa có test chốt) — chỉ phần thẻ thừa chưa ai dọn.

## Cách vá

- Nguồn chuẩn cầu nạp vào git: `sync/ebm-master-tools/` (commit 1 = nguyên trạng, commit 2 = sửa).
  Bản chạy chép bằng `tools/dong_bo_cong_cu_hub.py` (chỉ tua nhanh từ phiên bản đã biết, chỉ từ
  master sạch, sao lưu trước), gắn vào `tu_sua_chua.py`. Hook chặn sửa thẳng cây chính từ worktree —
  chính là lý do phải có đường git → bản chạy.
- `ingest_dashboard.py --thay-ban <cũ>` / `--noi-tiep` (chạy khô mặc định, `--ap-dung` để ghi): ghép
  mục theo ITEM-id, cập nhật TẠI CHỖ thẻ thuộc dòng phiên bản (giữ id/date_added/specialty/provenance,
  nối history), mục mới nạp thường, mục biến mất chỉ BÁO. **Trộn ba chiều** (gốc = bản cũ): đo trên sổ
  thật, so thẳng sổ ↔ bản mới sẽ trả `apply` cho thẻ integrity_guard đã hạ và ghi đè recommendation đã
  điền bằng bản tổng hợp — nên trường sổ đã sửa ngoài dashboard được GIỮ (decision/gradeLevel/PMID/DOI/
  URL không bao giờ tự giải); chữ trống hoặc bị bộ tách cũ cắt cụt («Quy trình») thì được bù.
- Nạp thường: bỏ qua bản cũ khi đã có bản mới hơn cùng lát cắt (sổ cái hoặc cùng lô); không nạp bản
  mới khi bản trước đã có thẻ mà chưa nối tiếp. Lát cắt lấy từ `tools/dang_ky_chu_de.py::tach_ten`.
- `tools/liet_ke_the_trung_hub.py` (CHỈ ĐỌC): mọi cụm + đề xuất thẻ giữ (tham chiếu sống → cập nhật có
  bác sĩ → ID gốc), cờ «thẻ giữ thiếu trường thẻ loại có», lệnh `manage_ledger.py drop` chờ bác sĩ duyệt.

## Kiểm hồi quy

31 test (`tools/test_ingest_noi_tiep_20261018.py`, `test_dong_bo_cong_cu_hub_20261018.py`,
`test_liet_ke_the_trung_hub_20261018.py`), chạy cả trên CI. 23 đột biến đều bị bắt đúng test đích, lượt
nền/sau khôi phục xanh, SHA ba tệp khớp. Một đột biến TƯƠNG ĐƯƠNG đã thay (thêm `specialty` vào danh
sách trường — trộn ba chiều vẫn giữ nó vì hai bản dashboard đều để trống). Mô phỏng nạp đủ 76 dashboard
trên bản sao: mã cũ +10 thẻ (2 thẻ cũ hồi sinh), mã mới +8; 11 bản cũ bỏ qua, 0 bản mới bị chặn.
