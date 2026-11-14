# 14/11/2026 — Bình duyệt độc lập trước mốc nộp/khoá: cảm biến 🛎 trong hòm việc

**Bài học gốc (29/10/2026):** MỘT agent `binh-duyet` đọc trọn gói nộp Hội đồng của C1a (`DE_CUONG_NOP_HOI_DONG_…md`) và tìm
4 lỗi 🔴 + 10 🟠 (ngày ký khoá SAP còn trống, thiếu mục Helsinki 2024 đoạn 26, vai «nhà thống kê», đồng ý cho pha phỏng vấn)
mà mọi cổng máy G0–G10 và hội đồng cổng đều đã cho qua. Bác sĩ duyệt cố định bước «bình duyệt độc lập trước mốc nộp/khoá».
Chưa có gì nhắc khi gói đổi sau lần bình duyệt — bước đó sống nhờ trí nhớ.

**Vá:** `tools/tu_de_xuat_viec.py` mục ⑥b `giac_quan_binh_duyet_doc_lap` — mỗi đề tài THẬT trong
`medical-ebm-automation/exports/` (có `study_meta.json`, không phải thư mục hệ thống, không `study_kind=synthetic_test`) đã lắp
G10: gói (`DE_CUONG_NOP_HOI_DONG_<mã>.md`, `DE_CUONG_THONG_NHAT_<mã>.md`) đổi SAU bản bình duyệt mới nhất
(`PHAN_BIEN_*_<YYYYMMDD>_<mã>.md`, `G8_PEER_REVIEW_REPORT_<mã>.md`), hoặc chưa có bản nào ⇒ một dòng 🛎 kèm ước tính ≈0,4 triệu
token. So theo NỘI DUNG, không theo mtime: bản bình duyệt ghi đủ sha256 hiện hành của gói ⇒ đã phủ; nếu không thì so ngày ghi
trong tên/phần đầu bản bình duyệt với `G10_checkpoint.generated_at`, và băm tệp gói với `release_manifest` (lệch ⇒ đã sửa sau
lúc lắp). Cùng ngày, tệp lệch manifest mà bình duyệt sau ngày lắp, bản không định được ngày ⇒ ⚪ (không đo được), không bao giờ
«ổn». Chỉ đọc — không đụng sổ cái, con dấu, tệp trong manifest G10. `--van-tay-goi <mã>` in các dòng sha256 để người bình duyệt
dán vào bản của mình.

**Đo trên dữ liệu thật (14/11/2026):** C1a — G10 lắp 28/10 19:19, hai tệp gói khớp manifest, bình duyệt 29/10 ⇒ không có việc;
BTM — chưa có G10_checkpoint ⇒ không báo.

**Kiểm:** `tools/test_cam_bien_binh_duyet_20261114.py` 28 ca trên thư mục tạm. Đột biến (10 phép: cùng ngày thành «đổi», bỏ
bằng chứng băm, bỏ loại synthetic, bỏ điều kiện đã lắp G10, coi lệch manifest là khớp, bỏ qua bản không ngày, gỡ nối dây
`main()`, một băm là đủ, bỏ loại thư mục hệ thống, lấy bản cũ nhất) ⇒ mỗi phép đỏ đúng ca dự kiến, khôi phục `cmp` khớp, xanh
28/28.

**Giới hạn còn lại:** agent `binh-duyet` chưa được dạy ghi sha256 gói vào bản của mình (sửa agent cần PR cặp hai repo) — tới
lúc đó, bình duyệt cùng ngày lắp G10 sẽ ra ⚪. Sửa tay thẳng vào `.docx` không được canh (`.docx` dựng lại từ md đổi byte mà
không đổi nội dung).
