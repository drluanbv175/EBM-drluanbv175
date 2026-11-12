# 13/11/2026 — Bỏ tác vụ lịch quý kiểm rút bài 32 thang điểm lâm sàng

Lời bác sĩ (nguyên văn, 13/11/2026): «Kiểm rút bài 32 thang điểm lâm sàng đã không còn ý nghĩa».

- Bỏ tác vụ `kiem-thang-diem-quy` (ngày 2 tháng 1/4/7/10, 18:00) khỏi `sync/scheduled-tasks/` và `sync/lich-nen-ky-vong.json`.
  Tác vụ này không có khoá trong `sync/quyen-lich-nen.json`.
- Công cụ `medical-ebm-automation/tools/kiem_do_tuoi_thang_diem.py` giữ nguyên để chạy tay (định tuyến `intent.py` vẫn trỏ tới nó).
- Tái kiểm rút bài cho mọi PMID/DOI trong kho dashboard vẫn do tác vụ tháng `kiem-rut-bai-kho-thang` đảm nhận.
- Test: thêm `kiem-thang-diem-quy` vào danh sách tác vụ đã bỏ (`test_lich_nen_ky_cu`); hạ sàn số SKILL 12 → 11.
  Ràng buộc «mọi tác vụ kỳ vọng có SKILL» vẫn giữ.
- Còn treo: `CLAUDE.md` §10 còn ghi «(QUÝ, tác vụ `kiem-thang-diem-quy`)». Agent không sửa `CLAUDE.md`.
