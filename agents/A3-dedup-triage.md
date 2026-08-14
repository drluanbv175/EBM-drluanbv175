# A3 — dedup-triage

## 1. Định danh & vai trò
**Hiện thân thật:** tools/uu_tien_cap_nhat.py + khối dedup trong surveillance_scan (`da_co_trong_kho`)

## 2. Đầu vào
ứng viên A2 + kho dashboard hiện có

## 3. Đầu ra
xếp hạng chủ đề cần cập nhật (tuổi × ứng viên mới); đánh dấu trùng

## 4. Công cụ được phép
so khớp PMID/DOI với kho

## 5. File được GHI (quan trọng nhất — xem ma trận ở README)
KHÔNG GHI state — chỉ báo cáo stdout/derivatives

## 6. Cổng phải qua
E1 (idempotency DOI‖PMID)

## 7. Điều kiện dừng khẩn
—

## 8. Giới hạn (negative capability)
không xoá ứng viên; trùng chỉ ĐÁNH DẤU, không lặng lẽ bỏ (BH23)

## 9. Một ca chuẩn
chạy sau quét tuần → 'VKDT: 8 mới, 3 đã có trong kho, ưu tiên #2'

## 10. Số đo chất lượng
tỷ lệ trùng phát hiện đúng (kiểm tay mẫu 14/08: 100%)

> Con trỏ biên chế — doctrine/tham số thật nằm ở hiện thân nêu trên. Sửa ở NGUỒN.
