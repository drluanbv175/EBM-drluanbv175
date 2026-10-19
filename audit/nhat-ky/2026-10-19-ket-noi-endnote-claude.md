# 19/10/2026 — Kết nối EndNote ↔ Claude: thư viện trong iCloud, `delete record` xoá hẳn, lệnh nhập AppleScript không ghi

## Bác sĩ yêu cầu
«Có giải pháp nào giúp cho sự kết nối giữa Endnote và Claude được thông suốt…» → «Hãy làm tất cả 6 việc giúp tôi» → «Lưu tất cả
vào Onedrive cho tôi» (chọn đặt thẳng thư viện đang dùng vào OneDrive sau khi được báo rủi ro).

## Đo
- Thư viện `~/Documents/My EndNote Library.enl` (+ `.Data` 1,1 GB) TRÙNG INODE với bản trong `iCloud Drive/Documents` — iCloud
  «Desktop & Documents» đang đồng bộ thư viện mà không ai biết. Đã chép sang `OneDrive/EndNote/` (882 tệp trùng byte, `diff -rq`
  sạch), đổi tên bản iCloud thành «… (CU-iCloud 19-10-2026)» làm dự phòng, cập nhật `~/.ebm-endnote.json` (giữ 96 mục loại trừ).
- **`delete record` (AppleScript) XOÁ HẲN**: thử trên BẢN SAO thư viện — hàng recNum 257 biến khỏi `refs` (1978 → 1977), không đặt
  `trash_state`. Thùng rác chỉ qua menu References → «Move References to Trash» (tên đổi thành «Delete References…» khi đang xem
  Trash); mục này chỉ bật khi danh sách bản ghi có tiêu điểm bàn phím.
- **Lệnh nhập AppleScript không ghi vào thư viện** (cả thư viện OneDrive lẫn bản sao đặt ngoài vùng đồng bộ): `import x into
  document …` và `create record` đưa bản ghi vào một «database» tạm (2, 4…), không vào `sdb.eni`, mất khi khởi động lại; `record
  contents` trả rỗng. Hôm 18/10 cùng phiên bản EndNote (22.4, không cập nhật từ 08/10) vẫn nhập được recNum 7327. CHƯA RÕ nguyên
  nhân — việc mở, để điều tra riêng (bước ⑧ của bộ năm hiện không nhập được bài MỚI; bài đã có vẫn gắn PDF/ghi trường bình thường).
- Nhóm «_Cho thung rac 18-10 (khong toan van)» thực ra là HAI nhóm trùng tên (85 + 3) — EndNote tạo nhóm thứ hai khi đăng lần hai.

## Đã làm (PR này)
- `tools/endnote_suc_khoe.py`: đọc `sdb.eni` chỉ-đọc (bản ghi, tệp đính kèm `file_res`, thùng rác, NHÓM — giải cột `groups.members`:
  4 byte phiên bản + số lượng + recNum uint32 LE), phát hiện bản sao xung đột OneDrive/iCloud và tệp chỉ còn trên mây (dataless).
- `tools/khoa_ghi_endnote.py` + `EndNoteMac._truoc_khi_ghi`: mọi lệnh GHI chờ khi bác sĩ đang thao tác trên EndNote (ứng dụng ở
  trước + bàn phím/chuột < 20 giây), giữ khoá giữa tiến trình, báo một lần.
- `tools/mcp/endnote_ebm_mcp.py` (khai trong `.mcp.json`; `--cai-claude-desktop` cho Claude Desktop): 8 công cụ, KHÔNG công cụ xoá,
  ghi chạy khô mặc định; thùng rác chỉ CHUẨN BỊ + KIỂM.
- `Chuyen Nhom Vao Thung Rac.command` + `tools/chuyen_nhom_vao_thung_rac.py`: chỉ hiện đúng bản ghi của nhóm, bác sĩ bấm ⌘A → Move
  References to Trash, công cụ kiểm từng bản ghi qua `sdb.eni`.
- Giác quan hòm việc `giac_quan_endnote` (bản sao xung đột · tệp chỉ còn trên mây · nhóm chờ thùng rác).

## Kiểm
`tools/test_endnote_ket_noi_20261019.py` (20 ca, gồm chốt AST: không chuỗi lệnh nào ngoài docstring chứa `delete record`); 15 đột biến
đều đỏ, phục hồi xanh; 309 test EndNote/hòm việc/MCP liên quan xanh; `chot_hoi_quy_bai_hoc.py` xanh.

## Bài học
Thử một lệnh AppleScript lạ của EndNote luôn trên BẢN SAO `.enl` + `.Data/sdb` đặt ngoài vùng đồng bộ và đo bằng `sdb.eni`
`mode=ro` — tên lệnh («delete») không nói nó vào thùng rác hay xoá hẳn.
