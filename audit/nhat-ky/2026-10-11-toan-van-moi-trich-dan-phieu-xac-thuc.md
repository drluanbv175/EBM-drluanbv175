# 11/10/2026 — Bảo đảm toàn văn cho MỌI trích dẫn + phiếu xác thực cho bác sĩ

Bác sĩ yêu cầu: «đảm bảo tất cả phải được kiểm tra, đọc và tải toàn văn giúp tôi, nếu tài liệu không tải và đọc toàn văn
được thì sẽ đưa ra giải pháp để tôi xác thực».

## Khoảng hở đo được
- `toan_van_theo_chu_de.py` (bước TV, 04/10) chỉ xét ứng viên A2 + mục `apply` chưa có toàn văn; bộ năm không chạy nó. Chủ đề
  COPD: 24 PMID mục chính + 2 PMID chỉ nằm trong phần tham khảo — hai bài sau chưa từng được xét toàn văn.
- Phiếu làn trình duyệt in thô (đuôi 60 dòng stdout), không có trạng thái TỪNG trích dẫn, không có lối xác thực cho bài «không
  có quyền đọc» hay trích dẫn chỉ có DOI.

## Vá
- `--moi-trich-dan`: mọi trích dẫn (mục + tham khảo — cùng tập định danh với nhóm EndNote), không trần PMID (trừ `--tran`).
- «PHIẾU XÁC THỰC»: một dòng mỗi trích dẫn — đã đọc toàn văn (nguồn nào, đã đọc sâu chưa) hay cần bác sĩ, kèm giải pháp theo
  đúng đường đọc (`duong_doc`): làn Chrome uỷ quyền · bác sĩ đọc rồi `--bac-si-da-doc` · Find Full Text · xin tác giả/thư viện
  · giữ trần «Cân nhắc» khi chỉ có tóm tắt; trích dẫn chỉ có DOI có dòng riêng (chuỗi toàn văn theo PMID — nói thẳng).
- Bộ năm: bước ⑦ «toàn văn mọi trích dẫn» (cần `--online`) chạy TRƯỚC bước ⑧ EndNote để PDF gom được gắn ngay lúc nhập.
- Kiểm: `tools/test_toan_van_moi_trich_dan_20261011.py` 10 ca; 7/7 phép đột biến đỏ đúng chỗ.

## Chạy thật (COPD)
- Lần 1: 26 trích dẫn — 19 đã đọc toàn văn (15 đọc sâu), 7 cần bác sĩ. Hai bài tham khảo mới lấy ngay trong phiên Chrome
  uỷ quyền: Chest 2025 (bản VoR Gold OA ở kho KCL, CC BY-NC-ND) và Sleep Med 2023 (ScienceDirect qua Mahidol) — cả hai TỰ GẮN
  vào EndNote lúc `--nhan` (nối từ PR #161 chạy thật).
- Lần 2: 21/26 đã đọc toàn văn (17 đọc sâu), 5 cần bác sĩ (2 NEJM cần đăng nhập, Lancet Respir Med — Mahidol không mua,
  Thorax — đòi mua bài, 1 bài đã ghi «không có quyền»), mỗi bài có giải pháp trong phiếu.
- Bẫy: kho Pure (KCL) trả 403 cho `fetch` từ trang bản ghi; bấm liên kết tệp mở tab PDF rồi lấy từ chính tab đó thì được.
