# 18/11/2026 — Trích dẫn đề tài phải có toàn văn: từ quy trình thành chốt máy G10-AUTO-12

**Lời bác sĩ (18/11/2026):** «Và xây dựng đảm bảo tất cả trích dẫn cho nghiên cứu trong hệ thống nghiên cứu phải luôn
là toàn văn, nếu không phải toàn văn và không thể lấy được toàn thì loại bỏ». Luật này đã có từ 25/10/2026 (BTM,
`DANH_MUC_TRICH_DAN_<mã>.json → quyet_dinh_loai_bo`) nhưng chỉ là QUY TRÌNH.

## Nguyên nhân (đo 18/11, chạy khô trên thư viện EndNote thật)
- BTM: 42/42 TLTK có toàn văn (đã áp luật 25/10).
- C1a: 24/58 TLTK có toàn văn trong EndNote (+1 PDF ở kho chờ gắn) — **không cổng nào báo**. Biên nhận
  `ENDNOTE_TLTK_<mã>.json` chỉ ghi TỔNG số (và đã cũ: 52 TLTK ngày 25/10, nay 58) nên không cổng nào đọc được từng TLTK.
- 3 TLTK C1a (38, 42, 52) đã có ghi nhận làn trình duyệt «Wiley chỉ tóm tắt — không quyền» trong sổ
  `trinh_duyet/khong-truy-cap.jsonl`, nhưng không nơi nào nối sổ đó với đề tài.

## Cách vá
- **Repo y khoa** `tools/toan_van_trich_dan.py` (PR y khoa): đọc biên nhận `TOAN_VAN_TLTK_<mã>.json`
  (`de_tai/toan_van_tltk/v1`), kết luận từng TLTK của đề cương nộp + bản thảo G7: có · chưa thử hết làn · KHÔNG lấy được
  (đã thử đủ truy cập mở + trình duyệt có uỷ quyền) · chưa đo. Khớp theo khoá PMID/DOI/băm câu — đánh số lại không làm
  mất biên nhận. `loai-bo --ap-dung` ghi `loai_bo` của danh mục trích dẫn (sao lưu trước) ⇒ sinh lại đề cương nộp là TLTK
  rút khỏi văn bản. Cổng **G10-AUTO-12**: còn trích bài không lấy được / bài đã loại ⇒ BLOCK; chưa đo / còn làn chưa
  thử ⇒ REVIEW; gói đã khoá chỉ cảnh báo. Hội đồng gán cho G10-T2 (`kiem-chung-trich-dan`), biên nhận vào đầu ra G10-T2.
  Bộ giả lập ghi biên nhận (việc đúng vai của thủ thư).
- **Repo gốc** `tools/nap_endnote_de_tai.py --ghi-bien-nhan-toan-van` (PR này): đo TỪNG TLTK trên EndNote thật (rồi kho
  toàn văn / `toan_van_tltk/`), nối làn đã thử (`--gom-toan-van` cùng lượt ⇒ truy cập mở; sổ «không truy cập» ⇒ trình
  duyệt; giữ làn cũ), dùng CHÍNH mô-đun y khoa cho khoá/khuôn. EndNote chưa mở ⇒ không ghi (không đo được ≠ thiếu).
- Dạy agent: `kiem-chung-trich-dan`, `thu-thu-tai-lieu`, `dieu-phoi-g10`.

## Kiểm hồi quy
- Y khoa: 25 test mới, **16/16 đột biến đỏ** (một đột biến sống sót lượt đầu — dòng phụ lục trùng số bị `setdefault` che
  — sửa phép thử); 82 test G10 + 482 test liên quan xanh; chuỗi thật G0→G10 cần bước thủ thư ghi biên nhận.
- Gốc: 7 test (1 dùng mô-đun y khoa thật, skip có khai báo khi CI không có cây OneDrive), **7/7 đột biến đỏ**.
- Đo thật trên bản sao thư mục đề tài: BTM ⇒ ĐẠT; C1a ⇒ CÒN VIỆC (25 có, 33 còn làn chưa thử).

## Việc còn lại (chưa làm — cần chạy trên máy có EndNote, sau khi hai PR gộp)
C1a: chạy `--gom-toan-van --ghi-bien-nhan-toan-van`, làn trình duyệt cho bài thuê bao còn thiếu, rồi `loai-bo` bài không
lấy được và sinh lại đề cương nộp — PR dữ liệu riêng. Ghi biên nhận cho BTM (42/42) để G10-AUTO-12 của BTM ĐẠT.
