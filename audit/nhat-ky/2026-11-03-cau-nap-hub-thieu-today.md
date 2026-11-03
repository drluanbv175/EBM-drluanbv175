# 03/11/2026 — Cầu nạp hub gọi tay thiếu `--today` sinh thẻ «EVID-0000» không có ngày

## Chuyện gì đã xảy ra

Phiên cập nhật «người cao tuổi đa bệnh» nạp bản nối tiếp dashboard `…NguoiCaoTuoi_DaBenhLy_NgoaiTru_20261102.html`
vào sổ cái hub bằng `EBM_MASTER/tools/ingest_dashboard.py <dashboard> --noi-tiep --ap-dung` (bác sĩ đã duyệt kế
hoạch chạy khô), nhưng quên `--today`. Cầu nạp khi đó có `--today` mặc định là chuỗi rỗng, nên:

- 31 thẻ mới mang mã `EVID-0000-1903…1933` (mã ghép năm từ `(args.today or "0000")[:4]`);
- `date_added` rỗng, dòng `history` không có ngày;
- bản sao lưu tên `EBM_MASTER_manual_pre-noi-tiep.json`.

Phiên đó phát hiện ngay khi kiểm sổ cái sau nạp, khôi phục từ bản sao lưu (SHA-256 khớp trạng thái trước lượt
ghi), nạp lại có `--today 2026-11-03` (AL-2026-000544, thẻ `EVID-2026-1903…1933`) và ghi dòng hoàn nguyên
AL-2026-000545. Bản ghi sai giữ ở `EBM_MASTER/BACKUPS/EBM_MASTER_thieu-today-EVID0000-20261103.json`.

Đo cùng ngày: sổ cái thật còn **58 thẻ `EVID-0000-1777…1861`** do các lượt gọi tay 20–26/10/2026 cùng lỗi
(`date_added` rỗng; nhật ký kiểm toán có mốc nạp cho cả 58). `sync_all.py` luôn truyền `--today` nên không gây lỗi
này — chỉ lệnh gọi tay (đúng cách CLAUDE.md §6.2 hướng dẫn cho nạp nối tiếp) mới dính.

## Cách vá

- `sync/ebm-master-tools/ingest_dashboard.py`: thiếu `--today` ⇒ dùng ngày hôm nay theo giờ máy; có `--today` mà
  không đúng dạng `YYYY-MM-DD` ⇒ từ chối (mã 2), không ghi gì.
- 58 thẻ cũ: CHƯA sửa. Báo cáo chỉ đọc `EBM_MASTER/AUDITS/THE-EVID-0000_2026-11-03.{md,json}` liệt kê từng thẻ,
  dashboard nguồn, mốc nạp trong `AUDIT_LOG.jsonl` và ngày đề xuất; hai cách sửa (giữ mã, bù ngày — hay cấp mã mới
  kèm ánh xạ) chờ bác sĩ chọn.

## Kiểm hồi quy

- `tools/test_ingest_ngay_mac_dinh_20261103.py` (4 test): nạp thường và nạp nối tiếp `--ap-dung` không kèm
  `--today` ⇒ mã không mang «0000», `date_added`/ngày history là hôm nay, tên bản sao lưu mang ngày; `--today`
  sai dạng bị từ chối và không ghi; `--today` truyền vào vẫn được dùng.
- Đột biến (chạy `python -B`, xoá `__pycache__`): bỏ dòng gán ngày mặc định ⇒ 2 test đỏ; bỏ kiểm dạng ⇒ 1 test
  đỏ; phục hồi ⇒ 4/4 xanh. `test_ingest_noi_tiep_20261018.py` (luôn truyền `--today`, nên không bắt được lỗi này)
  vẫn xanh.
