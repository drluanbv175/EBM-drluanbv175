# 10/10/2026 — Họp hội đồng chưa nuôi được vòng hoàn thiện hệ thống: biên bản trộn lỗi đầu ra với lỗi của hệ

Bác sĩ: «Việc họp như vậy sẽ như hoàn thiện đề tài nghiên cứu của tôi, mỗi ngày họp một cổng và với lần họp này sẽ đảm
bảo hệ thống được hoàn thiện tự động tốt nhất từ vấn đề hệ thống, Agent và các điều phối», rồi «Bắt đầu từ 18h ngày
mai».

## Đo (10/10)

- Biên bản hội đồng chỉ có hai chỗ ghi việc: rubric RQ1–RQ8 và `phan_quyet.viec_sua`. Cả hai đều nói về ĐẦU RA của một
  đề tài.
- Biên bản không có chỗ ghi lỗi của HỆ: bộ chấm đọc sai, tài liệu agent thiếu chỉ dẫn, điều phối giao sai, doctrine
  lệch mã sống. Vì vậy lỗi hệ chỉ được sửa nếu ai đó đọc lại biên bản bằng tay. Ví dụ: biên bản 07/10 của G0 C1a, phải
  tới 10/10 mới thành PR #110/#111.
- Không có công cụ chọn «hôm nay họp cổng nào». Năm lịch họp đêm 10→11/10 bị viết cứng cổng và giờ, nên phải tắt bằng
  tay.

## Vá

- Repo y khoa `tools/hoi_dong_cong.py`:
  - Biên bản có thêm `bai_hoc_he_thong` (không bắt buộc), ghi được ở mỗi người chấm và ở phán quyết trọng tài. Mỗi bài
    học có `pham_vi` ∈ cong_cu · agent · dieu_phoi · doctrine · quy_trinh_hoi_dong, kèm đối tượng, vấn đề, đề xuất và
    căn cứ kiểm được. Lệnh `ghi` kiểm các trường này: thiếu căn cứ hoặc có PII ⇒ không ghi.
  - `bai-hoc` gom bài học của mọi biên bản hợp lệ, kể cả biên bản đã cũ. Mã bài học là `<id biên bản>#<n>`.
  - Sổ `hoi_dong/BAI_HOC_XU_LY.json` ghi kết quả xử lý. Có ba loại: `da_sua` phải kèm URL PR thật của hai repo,
    `khong_sua` phải có lý do ≥ 10 ký tự, `trung` phải trỏ sang một bài học khác.
  - `lich-hop` chọn cổng ĐẦU TIÊN theo thứ tự G0→G10 còn phần cần họp theo hồ sơ máy. Cổng `nen_cho_cong_truoc` vẫn
    được chọn khi tới lượt, đúng nhịp bác sĩ chọn, và mang theo khuyến nghị đó. Không còn cổng nào thì không mở agent.
- Repo gốc:
  - Workflow `hoi-dong-cong.js` thêm `bai_hoc_he_thong` vào schema chấm và phán quyết, kèm lời nhắc «không thấy thì
    bỏ trống, không bịa». Kết quả trả về có `so_bai_hoc_he_thong`.
  - Thêm tác vụ lịch `sync/scheduled-tasks/hoi-dong-c1a-hang-ngay/SKILL.md`, chạy 18:00 mỗi ngày từ 11/10:
    1. Kiểm an toàn và kéo cây chính.
    2. Thiếu công cụ (PR chưa gộp) thì không họp, chỉ báo.
    3. `lich-hop` chọn cổng.
    4. Họp một cổng với `args.ho_so`.
    5. Sửa đầu ra bị trả về và bài học hệ thống bằng PR.
    6. Ghi báo cáo `hoi_dong/BAO_CAO_NGAY_<ngày>.md`.
    7. Không gộp PR.
  - Khai trong `sync/lich-nen-ky-vong.json`, dấu vết `file-ngay`.
- Doctrine `_HOI-DONG-CONG.md` (bản cặp y hệt): §3 thêm bài học hệ thống; §5 thêm nhịp hằng ngày và vòng hoàn thiện
  5 bước.

## Kiểm

- C1a, chỉ đọc: `lich-hop` ⇒ hôm nay họp G0 (`hop_duoc`), 10–19 agent ≈ 3,8–7,2 triệu token. Bài học chưa xử lý: 0.
- `tests/test_hoi_dong_hang_ngay_20261010.py` có 25 ca. Đột biến bị bắt 15/15 (có lượt nền xanh, phục hồi y hệt từng
  byte).
- Workflow chạy bằng giàn agent GIẢ: bài học của người chấm và trọng tài vào đúng biên bản, số đếm khớp, chế độ cũ
  không đổi.
- `kiem_tac_vu_lich_da_nen.py`: 16/16. `sync/lich-nen-ky-vong.json` đọc được.
