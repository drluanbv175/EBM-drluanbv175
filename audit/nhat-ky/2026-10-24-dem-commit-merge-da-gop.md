# 24/10/2026 — Hòm việc/Đài báo «commit chưa có trên remote» cho commit MERGE trên nhánh PR đã gộp squash

**Hiện tượng.** Đài hoàn thiện (V06/V07) và hòm việc báo «Repo gốc: 3 commit chưa có trên remote» và «Repo y khoa: 6 commit…»,
nhưng danh sách nhánh giữ chúng RỖNG. Cả 9 là commit «Merge remote-tracking branch 'origin/…' into <nhánh PR>» — đồng bộ nhánh
chính vào nhánh PR trước khi GitHub gộp squash rồi xoá nhánh đầu.

**Nguyên nhân.** `dem_commit_chua_co_tren_remote` (vá 09/10) lọc ① bản vá trùng (`git cherry` «-») và ② gộp squash (theo tiêu
đề). `git cherry` bỏ qua commit merge, nên commit merge không bao giờ vào ① hay ②.

**Đo (24/10/2026).** 5/9 commit merge trộn SẠCH (`git show --remerge-diff` rỗng); 4/9 có giải xung đột tay (59c340e, 94f718b,
b58ae87, 5cca089) — GitHub ghi cả 4 thuộc PR ĐÃ GỘP (#157, #115, #156 repo y khoa; #164 repo gốc), tạo trước lúc gộp.
So nội dung tệp của nhánh với nhánh chính HIỆN TẠI không dùng được: PR sau sửa tiếp các tệp đó (0/6 qua).

**Đính chính trong lúc đo.** Một phép kiểm tay `git diff --quiet <nhánh> origin/… -- $files` trong zsh báo «nội dung đã có»
cho cả 56 nhánh — SAI: zsh không tách từ biến (`$files` thành MỘT đường dẫn không tồn tại ⇒ diff luôn rỗng). Đã gặp trong
bộ nhớ (`feedback-zsh-bien-nhieu-duong-dan-khong-tach-tu`); dùng `${=files}` hoặc Python.

**Vá.** Lớp ③ `_commit_merge_nhanh_da_gop`: loại commit merge khi ⓐ trộn sạch VÀ mọi nhánh cục bộ chứa nó không còn commit
thật nào chưa lọc, hoặc ⓑ GitHub ghi nó thuộc PR đã gộp và có trước lúc gộp (`gh api repos/<chủ>/commits/<sha>/pulls`). Remote
không phải GitHub / gh lỗi / đầu ra lạ ⇒ vẫn đếm (không biết ≠ đã gộp). Đo lại: repo gốc 3 → 0, repo y khoa 6 → 0.

**Kiểm.** `tools/test_tu_de_xuat_viec_20261024_commit_merge_da_gop.py` 6 ca (merge sạch trên nhánh đã squash · merge có sửa tay
không thuộc PR ⇒ vẫn đếm · nhánh chưa gộp ⇒ vẫn đếm · sửa tay thuộc PR đã gộp ⇒ không đếm · remote không phải GitHub · nhận
diện sửa tay); 21 ca cảm biến commit cũ + chung vẫn xanh. Đột biến: tắt lớp ③ · `_merge_sach` luôn đúng · tra PR luôn đúng
⇒ đỏ 2/2/4 ca; phục hồi ⇒ xanh.
