# 03/11/2026 — EndNote giữ giao dịch ghi treo ~22 giờ, cuộn lại khi khởi động lại (BH177)

**Mã:** BH177 · **Thư viện:** `OneDrive-Personal/EndNote/My EndNote Library.enl` (EndNote 2025, 22.4.1, macOS).
Số đo dưới đây là ẢNH CHỤP ngày 03/11/2026, đo chỉ-đọc trên bản sao.

## Diễn biến

| Thời điểm | Sự việc (đo) |
|---|---|
| 02/11 ~19:00:59 | EndNote mở một giao dịch ghi và KHÔNG commit. `sdb.nal` là rollback journal của SQLite (magic `d9d505f9 20a163d7`). Tên lạ nên SQLite đọc từ ngoài không coi đó là nhật ký nóng. Từ đây mọi thay đổi của mọi phiên (nhập bài, đưa vào nhóm, ghi tóm tắt, gắn PDF) chỉ nằm trong giao dịch. |
| 02/11 19:01 → 03/11 | Mọi bản sao lưu `~/.ebm-endnote-sao-luu/` (`tom_tat_endnote_vi.sao_luu_thu_vien`, `backup()` chỉ đọc sdb.eni) là ảnh chụp giữa giao dịch: quick_check 21 rồi 101 dòng lỗi («invalid page number», «2nd reference to page»). Bước ⑨ sập vì lỗi giải mã UTF-8 ở `accession_number` (rec 4682 mang mẩu chữ của bản ghi khác). |
| 03/11 sáng | Phiên Bệnh van tim kết luận NHẦM «sdb.eni hỏng cấu trúc». Phiên cập nhật hàng loạt EndNote đo đúng: giao dịch đang mở. Bản lành cuối và bản «hỏng» đầu (19:00:26 / 19:01:40 ngày 02/11) khớp mốc mở giao dịch. |
| 03/11 07:09 | Bác sĩ Sync thành công ⇒ bản EndNote online nhận các thay đổi trong giao dịch. Sync KHÔNG commit giao dịch xuống đĩa. |
| 03/11 16:56:25 | EndNote khởi động lại (pid mới), `sdb.nal` biến mất. sdb.eni quay về trạng thái 19:00 ngày 02/11: `record_last_updated` mới nhất toàn thư viện = 19:00 02/11; 7 nhóm về số cũ (vd 152: 57→54); rec 7985–7994 mất; nhóm 169 còn 0 bài. quick_check = ok (giao dịch đã cuộn lại, không hỏng). |
| 03/11 17:02–17:05 | EndNote tự Sync kéo bản online về (usn 27220→27813): các nhóm về đúng số, 10 bản ghi thật sự được cứu, nạp khô `--tat-ca` báo 0 bài thiếu. Nhưng 88 bản ghi nhập ~19:00 02/11 (id 7892–7984) đã mất dòng `sync` khi cuộn lại ⇒ Sync kéo bản online của chính chúng về thành bản thứ hai ⇒ 88 cặp trùng (trước đó 2 cặp). |
| 03/11 17:24–19:03 | 88 bản cũ (không thuộc nhóm nào, không có tệp/khối ĐỌC NHANH mà bản mới thiếu) được gom vào nhóm «_Cho thung rac 2026-11-03 88 ban trung» (group 172). Bác sĩ chuyển vào thùng rác, Sync 19:03:06. Hàng chờ nhóm 77/78 đổi sang bản mới (70 mục). |

## Nguyên nhân gốc

- EndNote giữ một giao dịch ghi suốt ~22 giờ (vì sao thì chưa rõ; tối 02/11 nhiều phiên cùng ghi qua AppleScript, thư viện nằm trong OneDrive).
- Không giác quan nào đo TUỔI giao dịch. `giao_dich_mo()` của #287 chỉ dùng để chẩn đoán khi việc đọc đã thất bại.
- Khoá ghi vẫn cho các phiên ghi tiếp vào giao dịch dở, làm phình phần có thể mất.
- Bản sao lưu không thấy nhật ký nên không dùng được để khôi phục, và còn dẫn tới kết luận sai «hỏng».

## Vá (BH177)

- `tools/endnote_suc_khoe.py`: `giao_dich_treo()` đo tuổi theo giờ TẠO `sdb.nal` (EndNote xoá tệp khi giao dịch xong ⇒ giờ tạo = giờ mở). Ngưỡng `NGUONG_TREO_GIAY` 30 phút; `tinh_trang` để khoá riêng `giao_dich_mo`; `main` in 🔴, mã 1. Lời khuyên chung `HUONG_DAN_GIAO_DICH_TREO`: Sync TRƯỚC rồi mới thoát EndNote êm. Lời khuyên cũ «File › Close» không nhắc Sync, mà chính bản online đã cứu dữ liệu lần này.
- `tools/tu_de_xuat_viec.py`: giao dịch treo là ưu tiên 0 (🔴) của hòm việc.
- `tools/khoa_ghi_endnote.py`: `cho_phep_ghi` gọi `kiem_giao_dich_treo` TRƯỚC khi chờ/lấy khoá ⇒ `GiaoDichEndNoteTreo` (một `RuntimeError`, bên gọi bỏ lượt ghi như khi bác sĩ đang dùng EndNote). Không đo được ⇒ cho qua kèm cảnh báo. `EndNoteMac._truoc_khi_ghi` truyền đúng thư viện đang ghi.
- `tools/tom_tat_endnote_vi.py`: `sao_luu_thu_vien` có giao dịch mở ⇒ chép nguyên byte sdb.eni + sdb.nal (đặt tên `sdb.eni-journal`), để SQLite CUỘN LẠI về trạng thái đã commit, kiểm quick_check, ghi `GIAO-DICH-MO.txt`. Chỉ tin bản `backup()` khi không có giao dịch cả trước lẫn sau lúc sao lưu.

## Kiểm hồi quy

- `tools/test_endnote_giao_dich_treo_20261103.py`: 13 test. Fixture là một giao dịch SQLite THẬT bị tràn bộ đệm, nhật ký đổi tên `sdb.nal`. Đọc riêng sdb.eni thấy dữ liệu CHƯA commit mà quick_check vẫn «ok»: ảnh chụp dở có thể sai mà không báo lỗi.
- Chốt `BH177` trong `tools/chot_hoi_quy_bai_hoc.py`.
- 8 phép đột biến đều làm cả chốt lẫn test đỏ:
  - ngưỡng quá cao;
  - ngưỡng bằng 0;
  - hòm việc hạ ưu tiên;
  - khoá ghi bỏ bước kiểm;
  - `kiem_giao_dich_treo` không ném;
  - sao lưu như cũ;
  - sao lưu không cuộn lại;
  - EndNoteMac không truyền thư viện.

## Còn mở (03/11/2026)

- 5 cặp trùng cùng kiểu thuộc chủ đề Suy tim người cao tuổi (7918/8085, 7938/8086, 7939/8083, 7940/8084, 7941/8087). Một phiên khác đã gom chúng vào nhóm «_Cho thung rac 2026-11-03 5 ban trung Suy tim NCT», chờ bác sĩ chuyển vào thùng rác.
- Nhóm rỗng 170.
- Chưa biết thoát EndNote êm khi đang có giao dịch treo thì giao dịch được commit hay bị cuộn lại. Vì vậy hướng dẫn luôn bắt Sync trước.
- Clarivate khuyến cáo không đặt thư viện đang dùng trong thư mục OneDrive. Đổi vị trí là quyết định của bác sĩ (đã chọn OneDrive ngày 19/10/2026).
- Hướng dẫn cho bác sĩ: `EBM-Dashboards/derivatives/HUONG-DAN-XU-LY-ENDNOTE_20261103.md` (ngoài git).
