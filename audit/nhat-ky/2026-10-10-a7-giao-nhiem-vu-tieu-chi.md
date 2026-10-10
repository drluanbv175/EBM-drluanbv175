# 10/10/2026 — «Mỗi agent và điều phối đã được giao nhiệm vụ và tiêu chí kết quả phải đạt» chưa đo được cho 16 vai

Bác sĩ hỏi: «Mỗi Agent và điều phối đã giao nhiệm vụ và tiêu chí kết quả phải đạt được».

## Đo (10/10)

- Tiêu chuẩn hoàn thiện (A1–A6) báo 64/64 · 13/13, nhưng câu hỏi của bác sĩ chỉ được đo một phần: A4 («mọi nhiệm vụ có
  kiểm máy») ghi «—» (không áp dụng) cho 38/64 vai, A2 ghi «—» cho 16 vai (11 điều phối cổng, nhạc trưởng lâm sàng, điều
  phối tổng, giám khảo, phản biện, trọng tài). Không có hạng mục nào trả lời thẳng «vai này được giao NHIỆM VỤ gì, TIÊU CHÍ
  KẾT QUẢ nào, AI kiểm».
- Bảng giao việc dựng từ nguồn máy đọc: 25 agent có nhiệm vụ cổng nghiên cứu (mọi nhiệm vụ có tiêu chí); 21 agent lâm sàng
  có bước + mã tự-rà của nhạc trưởng; 2 vai chỉ chấm chéo; 16 điều phối/vai hội đồng nằm ngoài bảng. Ba vai hội đồng có
  khuôn JSON và `hoi_dong_cong.py ghi` THẬT SỰ kiểm đầu ra (`_kiem_danh_gia`, `_kiem_tranh_bien`) nhưng tài liệu không
  nói điều đó cho chính agent.

## Vá

- Repo y khoa: `tools/tieu_chuan_hoan_thien.py` thêm **A7 giao nhiệm vụ + tiêu chí kết quả** — đo cho MỌI vai, không có
  «—»: agent nhiệm vụ cổng (mỗi nhiệm vụ có tiêu chí máy) · người chấm chéo (rubric RQ1–RQ8 + JSON kiểm bằng
  `hoi_dong_cong.py ghi`) · agent lâm sàng (bước + mã tự-rà) · giám khảo/phản biện/trọng tài (khuôn JSON + tài liệu nói
  rõ bộ kiểm) · thẩm định đầu ra (R1–R7 + Q1–Q7 + TRẢ-VỀ-SỬA) · điều phối cổng (danh mục nhiệm vụ + bảng phân công + dạy
  `trach-nhiem … --gate GN`) · nhạc trưởng lâm sàng (bảng bước/tự-rà + Cổng A/B) · điều phối tổng (N1/N2). `--json` trả
  thêm «giao_viec» (loại vai, nhiệm vụ, tiêu chí, người kiểm) cho bảng của bác sĩ.
- Repo gốc (PR này) + bản cặp y khoa: `giam-khao-cong.md`, `phan-bien-tranh-bien.md`, `trong-tai-tranh-bien.md` thêm
  dòng «Tiêu chí đầu ra phải đạt» — đúng khuôn JSON, bị kiểm khi điều phối chạy `hoi_dong_cong.py ghi`, sai khuôn/thiếu
  căn cứ/PII ⇒ trả lại.

## Kiểm

- Sau vá: A7 đạt 64/64; tổng vẫn agent 64/64 · điều phối 13/13. Loại vai đo được: nghiên cứu 26 · lâm sàng 20 · nghiên cứu
  + lâm sàng 1 · điều phối cổng 11 · vai hội đồng 3 · nhạc trưởng lâm sàng 1 · điều phối tổng 1 · chốt kiểm đầu ra 1;
  «chưa giao» 0.
- 7 test mới trong `tests/test_tieu_chuan_hoan_thien_20261010.py`; đột biến 8/8 bị bắt (có lượt nền xanh).
