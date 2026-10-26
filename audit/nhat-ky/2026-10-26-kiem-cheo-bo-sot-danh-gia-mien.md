# 26/10/2026 — Kiểm chéo ⑨ không giao phán quyết từng miền (RoB/AMSTAR-2) và kết cục chính cho người chấm

**Phát hiện.** Tóm tắt Word ⑨ PMID 37142273 (Cochrane, 163 trang): bản tóm tắt chấm mục 11 AMSTAR-2 «có một phần» — mức không
hợp lệ (mục 11 chỉ có Có/Không) — rồi kết luận «không có lỗi then chốt». Người kiểm chéo độc lập chỉ bắt được GIÁN TIẾP qua câu
`tong_the`, và báo: `_KHOA_META` của `tools/tom_tat_chung_cu_word.py` loại khoá `danh_gia` và `chinh` ⇒ `nguy_co_sai_lech.mien[].
danh_gia` (phán quyết từng miền) và `ket_cuc.chinh` (kết cục chính — chuỗi) chưa từng nằm trong `kiem_cheo_can_kiem.json`.

**Nguyên nhân.** Hai khoá được coi là «siêu dữ liệu» vì ở dòng bảng `ket_qua`/`tac_hai` chúng là cờ/nhãn đã gộp vào chuỗi dòng; nhưng
cùng tên khoá ở chỗ khác lại là nội dung cần chấm.

**Cách vá.** Bỏ `chinh`, `danh_gia` khỏi `_KHOA_META`. `danh_gia` của một miền thành mục riêng `<đường>.danh_gia` mang tên miền
(«<tên miền> → đánh giá: <mức>») để người chấm đối chiếu đúng tiêu chí công cụ; `ket_cuc.chinh` thành mục như mọi chuỗi. Cờ
`chinh: true` của dòng bảng không phải chuỗi nên vẫn tự bị bỏ; dòng bảng vẫn là MỘT mục.

**Kiểm hồi quy.** Test `test_kiem_cheo_giao_ca_phan_quyet_tung_mien_va_ket_cuc_chinh` (tools/test_tom_tat_chung_cu_word_20261019.py);
3 đột biến (trả `danh_gia` vào META, trả `chinh` vào META, bỏ tên miền) đều đỏ đúng chỗ rồi xanh lại. Gói kiểm chéo dựng TRƯỚC bản
vá phải dựng lại (`kiem-cheo <mã>`) trước khi `dung` — tập mục đổi.
