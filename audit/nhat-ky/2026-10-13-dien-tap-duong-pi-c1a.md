# 13/10/2026 — Diễn tập trọn đường PI C1a (G3→G4→G2→G10) lộ 4 lỗi mà thước đo hoàn thiện không thấy

## Đo

- Thước đo trước diễn tập đều xanh: `tieu_chuan_hoan_thien` 64/64 · 13/13; `trach-nhiem --gate ALL` mã 0;
  `kiem_chi_tiet_he_nghien_cuu` 🔴 0.
- Diễn tập: chạy 4 nút một chạm (`chot_g3/g4/g2/g10_c1a.py`) ở CHẾ ĐỘ THẬT trên worktree tách rời (`--detach`, không
  commit/đẩy), đầu vào giả lập theo câu hỏi (câu ngoài kịch bản ⇒ dừng), không ký, không khoá.
- Lộ ra:
  1. Hồ sơ G2 (ICF Việt/Anh + DMP) không nhắc việc ghép thời gian chờ từ HIS mà G1 đã chốt; DMP §3 còn câu khuôn
     «bảng liên kết ID–tên do chủ nhiệm giữ» (agent điền 16/08). Doctrine 4b/4d có luật nhưng không phép kiểm nào.
  2. Danh mục tài liệu tham khảo của gói G10 trước dữ liệu luôn rỗng: StudySpec và bộ lắp đọc `g0.pmids_used_as_seed`
     mà `run_g0_auto` không bao giờ ghi (PMID G0 ở `pubmed_results.all_pmids`); chỉ còn đường PI khai `study_meta.pmids`.
  3. Đề cương lõi G10 chỉ phủ 15/24 mục ⇒ G10-AUTO-06 không bao giờ PASS dù đã bù đủ mục StudySpec D08…D18.
  4. Nút G10 (gốc) bỏ sót `mtime_khong_tin_duoc` (cổng «*») ⇒ báo «tươi» trong khi G10-AUTO-03 chặn; và đưa bản ĐÁNH GIÁ
     vào hàm soạn nháp thay cho StudySpec.

## Vá

- Repo y khoa #125: ICF/DMP C1a nêu việc ghép HIS (mọi câu `[BÁC SĨ RÀ]` để PI duyệt), kiểm máy cấp nhiệm vụ G2-T1
  cho mọi đề tài, doctrine `dao-duc-dang-ky` 4e + `dieu-phoi-g2` §7; bản cặp ở PR gốc này.
- Nút `Chot G10 C1a` (gốc, ngoài git): coi mtime dàn phẳng là việc phải làm tươi; thêm VIỆC 2b bù mục đề cương lõi
  P01…P24 trên study_meta ẢO (bản hiện tại + nháp đang chờ), nháp chỉ từ nội dung đã chốt và chỉ khi câu nguồn còn
  nguyên văn; danh mục PMID (đã trích + G0 «trực tiếp») và tài liệu tiếng Việt đi qua đường PI khai.
- Diễn tập lại trên sandbox sạch: đề cương lõi 24/24, không mục StudySpec thiếu, G0–G4 không tụt; dừng đúng ở A12 (NCBI
  đang misuse-chặn IP).

## Bài học

- Thước đo hoàn thiện đo CẤU TRÚC (có agent, có tiêu chí, có đầu ra); chỉ đi trọn đường người dùng trên dữ liệu thật
  mới thấy nội dung lệch giữa các cổng. Trước khi báo «cổng đã hoàn thiện», diễn tập đường PI trên worktree bỏ đi được.
- Khoá dữ liệu mà không bộ sinh nào ghi (`pmids_used_as_seed` của G0) là chỗ rơi im lặng — đối chiếu bên đọc với bên ghi.
