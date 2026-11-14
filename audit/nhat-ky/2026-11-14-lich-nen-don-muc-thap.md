# 14/11/2026 — Dọn mức thấp lịch nền: cảm biến đọc mã KẾT THÚC, ⚪ quyền lượt lịch, bước 0 tác vụ rút bài, khe test chốt doctrine

**Bối cảnh:** «Hướng hoàn thiện tiếp theo» (2) sau tầng 3; bác sĩ trả lời «Tiếp tục» (~14:50 ngày 14/11/2026). Bổ sung cho
`2026-11-14-lich-nen-tien-kiem-va-dau-vet.md`, `2026-11-14-tien-kiem-tac-vu-ky-thuat-lenh-ghep.md` và
`2026-11-14-chot-doctrine-tac-vu-lich-da-bo.md`. Mã BH: mở rộng BH173 (mục 13, 14).

**Năm lỗ đo trên mã sống (origin/master a151b1e):**
1. `tools/kiem_lich_nen.py` tính MỌI dòng KẾT THÚC trong hạn là kỳ đúng hẹn, không đọc «(mã N)». Lượt ghi «KẾT THÚC (mã 2)»
   (mảng không đo được, nguồn giả, dừng giữa chừng) hiện «đúng hẹn».
2. Giác quan ⑦f-bis của `tools/tu_de_xuat_viec.py` im khi `quyen_lich_nen.kiem()` trả `khong_do`. Máy khác nền tảng, tệp khai
   hoặc settings hỏng thì bảng không nói gì, đọc như «quyền đủ».
3. Chốt `doctrine_tac_vu_lich` (#348): quét đột biến lại được 10/12 phép SỐNG SÓT (bỏ lọc kebab, luật 1 chỉ xét thư mục, luật 2
   nhận sổ, bỏ lookbehind luật 3, bỏ IGNORECASE, bỏ `[:(]?`, bỏ dấu nối «hoặc/·//», bỏ KeyError/TypeError, tài liệu vắng im,
   thư mục nguồn vắng im). Thêm âm tính giả: «tác vụ lịch tuần thứ Hai `goi-duyet-tuan-ebm`» lọt vì regex chỉ nhận
   lịch|nền|tháng|quý|tuần|ngày xen giữa. `test_lich_nen_ky_cu` giữ bộ ba tên riêng, không đọc `TAC_VU_LICH_DA_BO`.
4. SKILL `kiem-rut-bai-kho-thang` (ngày 4) không có bước 0 tiền kiểm quyền như hai tác vụ tháng kia. Lượt thiếu quyền bị cắt
   giữa lệnh chu trình chạy 20+ phút mà vẫn «succeeded».
5. Chưa có văn bản quy ước soạn SKILL lịch (lệnh đơn, git/gh phải khai, bỏ tác vụ ⇒ `TAC_VU_LICH_DA_BO` cùng PR).

**Vá:**
1. Hợp đồng mã CHUNG `MA_TRON = {0, 1}` (`ghi_dau_vet_lich --ma` và `chu_trinh_chung_cu` cùng định nghĩa 1 = đi hết, có việc
   cho bác sĩ). Mã khác hoặc «tổng thể=CÓ BƯỚC LỖI» ⇒ 🟠 «lượt KHÔNG TRỌN (mã N)», không đếm đúng hẹn (kỳ cũ: 🟡). KẾT THÚC
   không đọc được mã ⇒ ⚪. Lệch có chủ ý so với lời giao «mã ≠ 0 ⇒ 🟠»: log thật có kỳ rút bài 04/11 mã 1 (lượt trọn, có việc).
   Coi mã 1 là không trọn sẽ ra 🟠 giả ở mọi kỳ có việc.
2. Tách `giac_quan_quyen_lich_nen()`. `khong_do` ⇒ ⚪ giác quan chết, kể cả khi đi cùng 👤/🤖.
3. Regex «tác vụ …» nhận TỪ VỰNG LỊCH (thứ trong tuần, giờ, «ngày N», đầu/cuối, kỹ thuật/nội dung…), tối đa 6 cụm. Cố ý
   không nhận từ bất kỳ: «tác vụ tháng gọi agent `x`» không bị bắt nhầm, vì chốt chặn commit. 13 test mới. `test_lich_nen_ky_cu`
   đọc `TAC_VU_LICH_DA_BO`.
4. Bước 0 `python3 tools/quyen_lich_nen.py --tac-vu kiem-rut-bai-kho-thang` đứng trước bước 1, có DỪNG LƯỢT NGAY và ghi
   alerts/. Khai lệnh ở `sync/quyen-lich-nen.json`, lệnh `--ap-dung` để ở `khong_chay`. Chốt BH173 (13) thành luật CHUNG: mọi
   tác vụ trong sổ kỳ vọng tiền kiểm chính nó trước lệnh việc đầu tiên. Luật này bắt được một lệnh đo
   (`git branch --show-current`) đứng trước bước 0 ở phần giới thiệu SKILL kỹ thuật tháng. Lệnh đó đã dời xuống mảng ⑥.
5. `sync/scheduled-tasks/README.md` có mục «Quy ước soạn SKILL tác vụ lịch» (8 luật). Test đối chiếu từng khẳng định với mã
   sống: regex phép dò, `MA_TRON`, `TAC_VU_LICH_DA_BO`, `cho_quyen`.

**Kiểm:**
- `tools/test_lich_nen_don_muc_thap_20261114.py`: 34 test.
- `test_verify_doctrine_tac_vu_lich_20261114.py`: 15 → 28 test. `test_tien_kiem_ky_thuat` và `test_lich_nen_ky_cu`: cập nhật.
- 63 tệp test liên quan: 999 đạt, 6 bỏ qua.
- `python3 tools/chot_hoi_quy_bai_hoc.py` trên worktree: 141 ✓, 38 ⚪ (bản sao trần), 0 ✗.
- Đột biến (sao lưu `cp -p`, `cmp` khớp sau mỗi phép):
  - việc I: 24/24 đỏ đúng test hoặc đúng mục BH173;
  - chốt doctrine sau vá: 17/17 đỏ, trước vá 2/12.
- Cảm biến mới chạy trên log thật (chỉ đọc): 2 tác vụ đúng hẹn. Tác vụ kỹ thuật tháng ⚪ vì trước mốc dấu vết 03/12.

**Việc của bác sĩ:** sau khi gộp, chạy `python3 tools/quyen_lich_nen.py --ap-dung`. Đo trên máy: đúng 1 quy tắc mới,
`Bash(python3 tools/quyen_lich_nen.py --tac-vu kiem-rut-bai-kho-thang)`. Chưa áp thì `dong_bo_tac_vu_lich` giữ SKILL rút bài cũ
ở runtime (`cho_quyen`), kỳ 04/12 vẫn chạy bản không có bước 0.
