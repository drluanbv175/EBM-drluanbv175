# 14/11/2026 — Sổ xác minh nguồn không có khoá ghi: hai lượt chạy song song xoá mất bản ghi của nhau

## Bối cảnh

PR #349 (bản ghi TRẦN, mã `CAN_PHU_MO_COI`) phải HOÃN chạy `--phu-mo-coi --vong 3` lúc 13:22. Khi đó một phiên khác đang
chạy bộ năm và đang ghi sổ (13:09, 13:18). Lý do hoãn: `--phu-mo-coi` đọc–sửa–ghi CẢ sổ, nên chạy song song có thể làm mất
bản ghi của nhau, kể cả dương tính rút bài. Trong lúc đo cho bản vá này, sổ thật cũng đổi từ 6750 lên 6752 bản ghi giữa hai
lần đọc cách nhau vài phút. Việc ghi đồng thời là chuyện xảy ra thật, không phải giả định.

## Gốc

`tools/so_xac_minh_nguon.py` có năm đường ghi sổ: `--quet`/`--vong` (`lenh_quet`, ghi mỗi 10 mục), `--quet-ledger`,
`--phu-mo-coi`, `--kiem-rut-lai`, cùng cầu NC⇄LS (`tools/cau_noi_nghien_cuu_lam_sang.py` gọi `ghi_so` của module). Cả năm
đường làm giống nhau: `doc_so()` một lần lúc đầu, chạy mạng nhiều phút, rồi `ghi_so(so)` GHI ĐÈ cả sổ bằng bản trong bộ nhớ.
Từ 26/09 lệnh ghi đã nguyên tử (tệp tạm rồi `os.replace`), nên sổ không còn bị cắt cụt. Nhưng lệnh ghi không có khoá và
không gộp, nên lượt ghi sau xoá mọi thứ lượt kia ghi trong lúc nó chạy mạng. Đo bằng test 6 tiến trình thật trên sổ tạm,
với bản `ghi_so` bỏ phần gộp: **mất 100/120 bản ghi**, chỉ còn bản ghi của tiến trình ghi sau cùng.

`xuat_goi_cap_nhat.py` và `verify_dashboard.py` chỉ ĐỌC sổ (`nguon_da_rut`, `dinh_danh_da_rut`), không ghi.
`surveillance_scan.py` cũng chỉ đọc. Vì vậy chỉ cần sửa một chỗ là `ghi_so`.

## Vá (`claude/so-xac-minh-khoa-20261114c`)

- `ghi_so` cầm khoá tệp `.so-xac-minh-nguon.json.lock` đặt cạnh sổ. Trên POSIX dùng `fcntl.flock`, trên Windows dùng
  `msvcrt.locking`. Đây là khoá của hệ điều hành nên tự nhả khi tiến trình chết, không bao giờ để lại khoá mồ côi. Hạn chờ
  `HAN_CHO_KHOA_GIAY = 60`. Quá hạn thì ném `SoDangKhoaLoi`, không ghi gì; CLI in «[MA] SO_DANG_KHOA» và thoát mã 3.
- Dưới khoá, `ghi_so` ĐỌC LẠI sổ trên đĩa. Nếu sổ đã đổi so với ẢNH GỐC (các byte `doc_so` đã đọc, giữ trong `_SoDaDoc`),
  nó GỘP BA CHIỀU theo từng bản ghi:
  - Chỉ trường mà chính lượt này đổi mới được đè lên đĩa.
  - `cac_dashboard` gộp theo tập.
  - Bất đối xứng: dương tính trên đĩa (`da_rut`/EoC) thắng bản không dương tính của ta, chép NGUYÊN nhóm phán quyết. Có
    thêm lưới cuối cho `da_rut` và cờ EoC dính.
  - Không xoá khoá nào, trừ khi chính ta xoá và đĩa không đổi khoá đó.
  - Dict thường (không qua `doc_so`) gộp với ảnh gốc rỗng, nên không xoá bản ghi nào trên đĩa.
  - Sổ trên đĩa HỎNG lúc ghi ⇒ `SoHongLoi`, không ghi. Ngoại lệ duy nhất là `--cuu-so-hong` (`ghi_de_so_hong=True`).
  - Sau khi ghi, `so` và mọi bản ghi con được cập nhật TẠI CHỖ, vì caller vẫn giữ `muc = so["muc"]` và `bg = muc[k]`.
- `chu_trinh_chung_cu.py` đọc «SO_DANG_KHOA» và báo ⚪ «lượt khác giữ khoá». Mã này không rơi vào nhánh «thiếu
  EBM-Dashboards». Bước ③a/③b vướng khoá cũng được báo.
- Đo trên BẢN SAO sổ thật (6752 bản ghi, ~4,3 MB, chép vào thư mục tạm, không đụng sổ thật): ghi khi đĩa không đổi giữ khoá
  0,03 giây; ghi CÓ gộp giữ khoá 0,07 giây.

Ba góp ý mức thấp khi rà #349 cũng được sửa trong bản vá này:

1. Câu «`--vong 3` KHÔNG chạm tới nhóm này» từng in vô điều kiện. Câu đó sai với bản ghi trần có liên kết dashboard. Nay
   `bao_cao` tách số đếm theo nguồn gốc. `chu_trinh` bỏ câu này và chỉ nói `--phu-mo-coi` phủ mọi bản ghi trần.
2. Thêm test cho bộ lọc `k not in khoa_truoc`: bản ghi trần CŨ không được đếm là «MỚI».
3. `moi_tran` không còn đếm bản ghi `da_rut`. `--phu-mo-coi` bỏ qua các bản ghi này, nên nhắc chạy lệnh đó là vô ích (BH14).

Skill `cap-nhat-chung-cu-y-khoa` (v1.60.0) có thêm vào bảng mã: `CAN_KIEM_RUT_LAI`, `CAN_PHU_MO_COI` và mã cấp lượt
`SO_HONG` · `KHONG_DO_DUOC` · `SO_DANG_KHOA`.

## Kiểm

- Test mới `tools/test_so_xac_minh_khoa_ghi_20261114.py` (18 ca), trong đó có:
  - 6 tiến trình thật cùng đọc trước rồi ghi xen kẽ vào một sổ tạm;
  - một tiến trình con giữ khoá để kiểm hết hạn chờ, không ghi, và CLI trả mã 3.
- `tools/test_so_xac_minh_can_xem_tay_20261114.py` thêm 6 ca cho ba góp ý của #349.
- Đột biến bắt **17/17**. Có lượt nền xanh trước và sau. Mỗi phép sao lưu `cp -p`, kiểm `cmp`, khôi phục khớp `cmp`. Các phép:
  bỏ gộp · khoá no-op · bỏ chép nhóm dương tính · bỏ lưới cuối `da_rut` · bỏ cờ EoC dính · `cac_dashboard` theo bản của ta ·
  thay đối tượng thay vì sửa tại chỗ · bỏ/nuốt ngoại lệ sổ hỏng (2 phép) · bỏ bắt `SoDangKhoaLoi` · bỏ hai nhánh chu trình ·
  câu `--vong 3` vô điều kiện (2 phép) · `moi_tran` đếm `da_rut` · bỏ `k not in khoa_truoc` · đĩa mất bản ghi dương tính.

## Giới hạn còn lại

- Khoá chỉ có tác dụng giữa các tiến trình trên CÙNG một máy. Mac và Windows qua OneDrive vẫn theo luật «một máy tại một thời
  điểm» (CLAUDE.md §0.7).
- Cầu NC⇄LS gặp `SoDangKhoaLoi` thì thoát bằng traceback (mã khác 0, không ghi gì) chứ chưa in mã đẹp. Tệp đó không thuộc
  phạm vi bản vá này.

Cần bác sĩ kiểm chứng.
