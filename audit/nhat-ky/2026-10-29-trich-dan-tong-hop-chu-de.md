# 29/10/2026 — Trích dẫn tự tạo «★ TÓM TẮT THỰC HÀNH» cho mỗi nhóm EndNote chủ đề

**Bác sĩ yêu cầu:** «bây giờ bổ sung cho tôi một trích dẫn tự tạo giúp tổng hợp lại những vấn đề áp dụng cho thực hành lâm sàng
hay là bản tóm tắt vấn đề chính» — cho mỗi chủ đề đã cập nhật chứng cứ và trích dẫn.

**Làm:** `tools/trich_dan_tong_hop_chu_de.py` — mỗi nhóm «EBM · <chủ đề>» thêm MỘT bản ghi Report «★ TÓM TẮT THỰC HÀNH · <câu
hỏi>», tác giả tập thể «EBM Copilot», nhãn «EBM · TÓM TẮT CHỦ ĐỀ», khoá bền `EBM-TT:<khoá chủ đề>` ở Accession Number (mọi công cụ
khác so khớp NGUYÊN với PMID thuần số ⇒ không nhầm; `dung_xml` nhận `so_truy_cap`, không link PubMed). Abstract chép NGUYÊN khối
DATA của bản dashboard mới nhất: ⛔ cờ đỏ · ✅ làm ngay · ✖️ không nên (đứng trước, như bản đọc ②) · ⭐ vấn đề chính · mục theo
quyết định (áp dụng: tiêu đề + hành động + PMID/DOI; cân nhắc/chưa đủ: tiêu đề + định danh) — không cắt câu, chỉ ký tự BMP.
Chân «đã qua cổng» CHỈ khi bản Word cùng bộ năm ghi câu PASS của `verify_dashboard.py --online` VÀ sidecar `.data-sha256` trùng
băm DATA hiện tại (dashboard sửa sau lượt xuất ⇒ «CHƯA xác minh», không đính PDF cũ). Đính PDF tài liệu chi tiết ③⑤. Chạy lại
không đổi ⇒ không ghi (dấu trong Notes); đổi ⇒ ghi đè Title/Year/Abstract rồi Notes cuối; nhập hụt ⇒ dọn PDF; PDF mới chỉ THAY
khi mọi tệp đang gắn là của công cụ.

**Nhóm (BH170):** bước ⑧ (`nap_endnote_chu_de.py --kem-tong-hop`, `xuat_goi_cap_nhat.lenh_endnote` luôn truyền) đưa mã bản ghi
vào CÙNG lượt đăng nhóm, chỉ cho bản dashboard MỚI NHẤT của chủ đề ⇒ chủ đề MỚI có bản ghi tổng hợp ngay trong lần post tạo
nhóm. Nhóm ĐÃ có (39 chủ đề lúc làm) ⇒ không post được (post luôn sinh nhóm trùng tên) ⇒ bản ghi vào hàng chờ, bác sĩ hoặc phiên
Claude kéo MỘT lần (`--cho-vao-nhom "<tên>"`); các lần cập nhật sau sửa tại chỗ. Lỗi của bản ghi tổng hợp chỉ được báo, không
chặn đăng nhóm các bài.

**Kiểm:** `tools/test_trich_dan_tong_hop_chu_de_20261029.py` 27 ca (EndNote giả, ngoại tuyến); 15 đột biến đều đỏ đúng chỗ (lần
đầu M8 «nhập hụt không dọn PDF» sống vì phép thử đặt `tm = None` SAU lệnh dọn — lỗi phép thử, đã viết lại nhắm thẳng lệnh dọn);
433 test EndNote/bộ năm liên quan xanh.
