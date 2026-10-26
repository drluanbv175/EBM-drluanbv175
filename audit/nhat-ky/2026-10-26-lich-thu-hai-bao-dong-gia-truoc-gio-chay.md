# 26/10/2026 — Hòm việc báo «kỳ lịch thứ Hai KHÔNG nổ» GIẢ khi chính ngày thứ Hai chưa tới giờ chạy

**Phát hiện.** 17:18 thứ Hai 26/10/2026, `tools/hom_viec_mot_cua.py` và `tools/tu_de_xuat_viec.py` báo
«🟡 👤 Kỳ lịch thứ Hai vừa qua KHÔNG nổ (máy không thức?)». Đo sống: tác vụ `thu-thap-tuan-an-toan-thuoc` chạy
lúc 18:00 thứ Hai (lượt gần nhất 19/10, `succeeded`); lúc báo mới 17:18 — kỳ hôm nay CHƯA tới giờ.
`python3 tools/kiem_lich_nen.py` cùng lúc báo 🟢 (cảm biến theo kỳ có tính giờ), nên hai bộ đo nói ngược nhau.

**Nguyên nhân.** `giac_quan_lich_nen()` tính «kỳ gần nhất đã qua» theo NGÀY: đúng ngày lịch thì lấy chính hôm nay
⇒ từ 00:00 thứ Hai tới lúc lượt 18:00 ghi xong dòng «KẾT THÚC … tổng thể=PASS» (đo 12/10: 1 giờ 48 phút) hàm luôn
coi kỳ hôm nay là đã lỡ. Cùng họ với đính chính 12/09/2026 (hằng số thứ Bảy cũ) — giác quan lịch nền báo động giả
dạy người ta bỏ qua cảnh báo thật.

**Cách vá.** Thêm tham số `bay_gio`: khi hàm tự lấy giờ máy (không truyền `hom_nay`), kỳ của CHÍNH ngày lịch chỉ đến
hạn khi ngày đó đã hết ⇒ trong ngày lịch xét kỳ tuần trước. Chỉ truyền `hom_nay` (chốt BH57, test thuần) = đánh giá
lúc hết ngày — giữ hành vi cũ, BH57 vẫn ✓. Đánh đổi có chủ ý: lượt thứ Hai không nổ thì cảnh báo hiện từ thứ Ba.

**Kiểm hồi quy.** `tools/test_tu_de_xuat_lich_nen_ngay_lich_20261026.py` (7 ca: trước giờ chạy · lượt đang chạy ·
thứ Ba sau kỳ lỡ · lượt hôm nay đã PASS · chỉ truyền ngày · ca thứ Bảy của BH57). Hai đột biến (bỏ dịch kỳ; dịch cả
khi chỉ truyền ngày) đều đỏ đúng chỗ rồi xanh lại. Bộ chốt bài học: không mục nào tái phát.
