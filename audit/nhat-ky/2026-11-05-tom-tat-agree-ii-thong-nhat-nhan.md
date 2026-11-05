# 05/11/2026 — Bản tóm tắt ⑨: nhãn mức miền AGREE II viết ~60 kiểu — thống nhất khi in

**Đo (282 gói):** AGREE II cho điểm % theo miền, không có mức chữ, nên mỗi lượt tóm tắt tự đặt nhãn: «trung bình» 231 · «cao» 156 ·
«thấp» 70 cạnh «đạt một phần tiêu chí (định tính, không quy ra điểm % AGREE II)» 21, «tốt» 14, «khá» 12, «Mô tả hạn chế (…)» 8,
«trung bình–cao» / «trung bình – cao» / «trung bình – khá» / «cao – trung bình», «chất lượng thấp (nhận định…)»… — khoảng 60
kiểu cho cùng ba bậc. Kiểm chéo bù 04/11 còn bắt «không rõ» (AGREE II: mục không có thông tin nhận điểm thấp nhất) — đã sửa
từng bản qua kiểm chéo lần 2.

**Bác sĩ chọn «Thống nhất khi in»** (không sửa dữ liệu từng bản, không kiểm chéo lại).

**Vá:** `muc_chuan()` nhánh AGREE II (`_AGREE_DAU`, `_muc_agree`): bước DỰNG in thấp / trung bình / cao hoặc khoảng «thấp – trung
bình» / «trung bình – cao»; «tốt» → cao, «khá» → trung bình – cao; nhãn MÔ TẢ («đạt một phần tiêu chí», «Mô tả rõ»…) in mức
chuẩn rồi giữ nguyên chữ gốc sau «—» để không mất ý người tóm tắt; nhãn đã chuẩn và «không rõ» giữ nguyên. `tom_tat.json` không
đổi. HUONG_DAN_DOC mục 3 dặn bản mới ghi AGREE II đúng ba bậc, không «không rõ». Không thêm cổng (cổng sẽ chặn ~150 bản cũ).

**Kiểm:** `tools/test_tom_tat_agree_ii_20261105.py` 26 ca (kể cả bảng Word thật); 6 đột biến đều đỏ, phục hồi xanh; bộ test ⑨
232 xanh. Chạy thử trên toàn bộ nhãn AGREE II của kho: mọi nhãn ra một trong ba bậc/khoảng hoặc giữ nguyên khi đã chuẩn.
