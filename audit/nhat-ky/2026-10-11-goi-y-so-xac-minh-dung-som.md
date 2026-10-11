# 11/10/2026 — Lời gợi ý «Phủ sổ xác minh» nối bằng «&&» nên hai bước sửa mục mồ côi/hub không bao giờ chạy

## Đo

- `tu_de_xuat_viec.py` gợi ý 🤖 «Phủ sổ xác minh: N mục chưa/hết hạn» kèm lệnh
  `--vong 3 && --quet-ledger --vong 3 && --phu-mo-coi --vong 3`.
- Chạy đúng lệnh đó ngày 11/10: chỉ bước đầu chạy. Lượt quét trả **mã 2** vì sổ có mục bị cờ rút bài — ở đây là 2
  bản đính chính bị rút mà bác sĩ ĐÃ ký xem xét. Mã 1 (còn thiếu) cũng là chuyện thường. Với «&&», `--quet-ledger` và
  `--phu-mo-coi` không bao giờ được gọi.
- Hệ quả: 25 thẻ `(hub-only)` treo ở «không đọc được ngày xác minh». Danh sách việc gợi ý mãi một lệnh không chạm tới
  chúng, dù máy xác minh được ngay: chạy `--phu-mo-coi` riêng thì +25 xác minh, 0 chưa tra được.
- Chẩn đoán đầu của phiên SAI: phiên cho rằng «`--quet-ledger` theo thiết kế chỉ kiểm rút bài nên không bao giờ có
  ngày xác minh» và đề xuất đổi cách đếm. Thực ra `--phu-mo-coi` có xác minh tồn tại cho thẻ hub (test
  `test_so_xac_minh_phu_mo_coi_20260927.py`), nhưng chưa bao giờ được chạy tới. Nếu đổi cách đếm thì sẽ che một lỗi
  thật. Bài học: soi xem lệnh gợi ý có thật sự CHẠY TỚI bước sửa không, trước khi đổi thước đo.

## Vá

- `tools/tu_de_xuat_viec.py`: ba bước nối bằng «;». Mỗi bước tự chỉ ghi THÀNH CÔNG, nên chạy tiếp sau bước trả mã
  ≠ 0 là an toàn. «;» cũng chạy được trên PowerShell của máy Windows.
- `tools/chot_hoi_quy_bai_hoc.py` BH120: thêm điều kiện — hằng chuỗi trong `main()` có `so_xac_minh_nguon.py` thì
  không được chứa «&&».

## Kiểm

- Sổ xác minh sau khi chạy hai bước bị bỏ sót: 2128/2132 (99%), «Chưa/hết hạn: 0». Gợi ý lặp tự hết.
- Đột biến bắt 3/3: nối lại «&&» ở bước 1; nối lại «&&» ở bước 2; bỏ bước `--phu-mo-coi`. Có lượt nền xanh, mã
  phục hồi y hệt từng byte.
- Bộ chốt bài học trọn bộ: không tái phát. Test liên quan 161 qua.
