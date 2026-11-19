# 19/11/2026 — G7 chọn trích dẫn hạt giống bỏ qua sàng lọc G0-T3; giả lập chưa mô phỏng ba văn bản agent

**Bối cảnh.** Sáng 19/11/2026 tôi đo 24 đề tài giả lập bằng bảng trách nhiệm cổng (`hoi_dong_cong.py trach-nhiem`). Mọi trục máy đều sạch, nhưng còn 72 lượt «agent còn việc». Cả 72 thuộc ba văn bản do agent soạn mà bộ giả lập chưa mô phỏng, lặp ở 24 đề tài:
- G0-T3: tổng hợp bằng chứng;
- G0-T4: khoảng trống;
- G10-T3: sổ trạng thái.

Bác sĩ đồng ý bổ sung phần sinh ba văn bản này.

**Sự cố lộ ra.** Khi giả lập đã có G0-T3, trục `trich_dan_tong_quan` của `nhat_quan_xuyen_cong` báo «TLTK trích bài G0 đã sàng là lạc đề». Ở kịch bản RCT, TLTK đề cương nộp trích 10 bài lạc đề.

Nguyên nhân: `run_g7_auto.py` lấy 10 PMID đầu của mọi nhánh trong `G0_pubmed_raw.json` làm `pmids_used_as_seed`, kể cả nhánh không lọc, mà không đọc `G0_TONG_HOP_BANG_CHUNG_<mã>.json`. StudySpec dùng danh sách hạt giống này, nên bài lạc đề đi tiếp vào TLTK của đề cương nộp. Đề tài thật (C1a, BTM) chưa tới G7 nên chưa gặp, nhưng chắc chắn sẽ gặp.

**Cách vá** (repo y khoa, PR giả lập ba văn bản agent):
- Thêm `run_g7_auto.uu_tien_theo_sang_loc_g0()`:
  - bỏ bài sàng «khong», kể cả `sang_loc_khong_loc`;
  - xếp theo thứ tự trực tiếp → gián tiếp → chưa sàng;
  - tệp tổng hợp vắng hoặc hỏng thì giữ hành vi cũ.
- Bộ giả lập soạn ba văn bản bằng `tools/gia_lap_van_ban_tac_tu.py`. Đầu ra qua đúng bộ kiểm của hệ, không nới bộ kiểm nào.
- Luật G0-T3 đòi sàng đủ nhánh không lọc vượt trần, nên nhánh đầy đủ (53–875 bản ghi mỗi truy vấn) được tải một lần và lưu ở `tests/fixtures/gia_lap_nen_g0/_khong_loc_day_du/`.

**Kiểm hồi quy.**
- `tests/test_gia_lap_van_ban_tac_tu_20261119.py`: 56 ca, gồm một ca chạy `run_g7_auto.main()` thật.
- Kiểm đột biến 19/19 đỏ đúng chỗ.
- 24 kịch bản chạy kiểu CI:
  - 0 «agent còn việc»;
  - G0–G8 và G10 «đạt tiêu chí» 24/24;
  - G9 «agent xong, chờ người» 24/24;
  - 0 lệch, 0 cần xem trên các trục xuyên cổng;
  - gói G10 khoá 24/24.

**Còn mở, chờ bác sĩ quyết.**
1. Luật G0-T3 không có trần cho nhánh không lọc. Truy vấn rộng buộc agent sàng mọi hit; ở giả lập là tới 875 tiêu đề, còn C1a chỉ 35 và BTM 60.
2. `nhat_quan_xuyen_cong._da_kiem_rut_bai` coi mọi số 7–8 chữ số trong văn bản `rut_bai` của G0-T3 là «đã kiểm rút bài». Một câu kiểu «PMID x chưa kiểm» vì thế cũng bị tính là đã kiểm. Cách sửa gợi ý: thêm danh sách có cấu trúc `pmid_da_kiem`.
