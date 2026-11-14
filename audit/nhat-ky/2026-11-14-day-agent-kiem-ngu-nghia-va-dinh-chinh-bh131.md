# 14/11/2026 — Kiểm chéo ngữ nghĩa K1–K4 chạy 7 tuần mà skill/agent chưa dạy; đính chính BH131 sau #356

**Phát hiện.** PR #359 thêm K3b/K4b vào bước ④-ter của bộ năm. Khi đi dạy hai phép mới, grep cả
`sync/skills/cap-nhat-chung-cu-y-khoa/**` lẫn `.claude/agents/*.md` (các cụm `kiem_cheo_ngu_nghia`,
`kiem_quan_the_chieu`, `bo_vang_kiem_ngu_nghia`, `do_nhay_kiem_ngu_nghia`, «kiểm chéo ngữ nghĩa», «K1–K4», «④-ter»)
ra **0 kết quả**. Nghĩa là K1–K4 (④-bis/④-ter, có trong `xuat_goi_cap_nhat.py` từ 25/09/2026) chưa từng được dạy
cho skill hay agent nào. Agent đọc dòng 🟠 của bộ năm không biết phép nào báo, phải đọc lại cái gì, và không biết
«không có 🟠» chưa phải là «đúng». Chỉ CLAUDE.md §6.4 có một dòng nhắc. Đây là lại đúng kiểu lỗi «thêm luật ở cổng
mà không dạy agent cùng lúc», lần này với các phép CẢNH BÁO.

**Vá (doctrine, không đổi mã kiểm).**
- SKILL `cap-nhat-chung-cu-y-khoa` v1.61.0 có thêm một khối ngay sau danh sách bộ năm. Khối nêu nghĩa K1/K2/K3/K3b/K4/K4b
  và mức CẢNH BÁO (chuyển sang CHẶN là việc của bác sĩ). Nó dạy cách đọc dòng `Tổng: … (🟠 theo phép: …)`. Gặp 🟠 thì
  đọc lại nguồn; không tự đổi `decision`/`gradeLevel`. Độ nhạy đo bằng `tools/do_nhay_kiem_ngu_nghia.py`.
- Agent `trich-xuat-y-van` (người đọc lại nguồn) và `tham-dinh-dau-ra` (một hàng mới trong bảng định tuyến: 🟠 ngữ nghĩa
  KHÔNG phải 🔴, giao `trich-xuat-y-van`). Bản cặp y hệt ở repo y khoa.
- Số đo độ nhạy là ẢNH CHỤP lượt 14/11/2026c (`quality/eval/kiem-cheo-ngu-nghia/do-nhay-dot-bien-20261114c.md`).
  K3b đạt 7/604 ≈ 1% (27% trong phần phép phán được). K4b đạt 145/581 ≈ 25% (56% trong phần phán được). Vì vậy văn bản
  dạy agent ghi rõ: «không cảnh báo» KHÔNG được đọc thành «đúng».

**Đính chính BH131.** Sau #356, `kiem_lich_nen.py` đọc cả mã của dòng KẾT THÚC, nhưng chỉ để phân xử lượt TRỌN hay
KHÔNG TRỌN (`MA_TRON` = {0, 1}). Mã 1 (phát hiện rút bài) vẫn được tính là kỳ đúng hẹn. Docstring
`tools/doc_ket_qua_rut_bai_kho.py` và mô tả chốt BH131 vẫn ghi «kiem_lich_nen không đọc MÃ». Đã sửa cho đúng; lý do
công cụ tồn tại không đổi.

Chốt BH131 có thêm vế (c), kiểm HÀNH VI: `kiem_lich_nen._ket_thuc_co_ma` phải đọc dòng do
`chu_trinh_chung_cu.ghi_dau_vet` ghi ra đúng một dòng, đúng thời điểm, nhãn «mã N» với các mã 0/1/2/130. Hai bộ đọc của
cùng một log phải hiểu cùng một mã.

Kiểm đột biến 2/2 đỏ đúng vế (c): `_MA_SO` đọc «(ma N)»; `_DONG_KET_THUC` đòi «KẾT THÚC:». Mỗi phép đều sao lưu
`cp -p`, `cmp` khớp trước và sau khi khôi phục.

_Cần bác sĩ kiểm chứng._
