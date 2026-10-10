# 10/10/2026 — 4 agent nghiên cứu không điều phối nào giao việc · 2 agent lâm sàng không bị nhạc trưởng kiểm đầu ra

Bác sĩ giao: «Tiếp tục hoàn thiện từng Agent, mỗi agent phải có nhiệm vụ rõ ràng, có sự kiểm soát của điều phối và từng
điều phối».

## Đo (10/10, 64 agent)

- **Phía nghiên cứu** (danh mục máy `hoi_dong_cong.NHIEM_VU` — nhiệm vụ cổng + người chấm chéo): `mo-hinh-tien-luong`,
  `nghien-cuu-dinh-tinh`, `kinh-te-y-te`, `trich-xuat-y-van` KHÔNG làm cũng không chấm nhiệm vụ cổng nào ⇒ không điều phối
  cổng nào giao việc hay đòi đầu ra; `huong-dan-lam-sang` (trong danh sách agent nghiên cứu) không có vai nào ở hội đồng
  cổng.
- **Phía lâm sàng** (`dieu-phoi-lam-sang`: bảng bước tự chạy 0–5 + bảng tự-rà hoàn chỉnh C1–C9): cả 20 agent lâm sàng có
  bước chạy, nhưng `ket-qua-hoc-tap` và `cap-nhat-guideline` (bước 5) KHÔNG có hạng mục tự-rà nào ⇒ nhạc trưởng không kiểm
  đầu ra của họ trước khi trả gói. Không có cơ chế máy nào giữ hai bảng khớp với tài liệu từng agent.

## Vá

Repo y khoa (PR xếp chồng trên drluanbv175/medical-ebm-automation#106):
- `hoi_dong_cong.NHIEM_VU` thêm 6 nhiệm vụ có điều kiện, đầu ra là sản phẩm công cụ thật: G1-T6/G6-T4
  `mo-hinh-tien-luong` (thiết kế `prediction`; G1 kiểm dòng «Yếu tố dự báo ứng viên» + «Khung thời gian dự báo»), G1-T7/G6-T5
  `nghien-cuu-dinh-tinh` (thiết kế `qualitative`; G1 kiểm ba dòng định tính), G1-T8 `kinh-te-y-te` (điều phối KHAI «có cấu
  phần kinh tế»; đầu ra `G7c_HEALTH-ECONOMICS_<mã>.docx` của `gen_research_docx --artifact health-economics`), G5-T2
  `trich-xuat-y-van` (SR/MA; `06_phan_tich_R/study_level_extraction.csv` — đúng tệp script gộp G6 đọc; kiểm cột study/year +
  (TE, seTE) hoặc 2x2, ≥ 2 nghiên cứu, nhãn không trùng, seTE > 0, 0 ≤ biến cố ≤ cỡ nhóm). `huong-dan-lam-sang` chấm chéo
  G6-T3. G6-AUTO-09 «G6-T2|G6-T4|G6-T5|G6-T1».
- Bộ sinh tài liệu: khối «Nhiệm vụ & kiểm soát trong ca lâm sàng» cho MỖI agent trong hai bảng của nhạc trưởng (bước chạy +
  hạng mục tự-rà nhạc trưởng kiểm); mô tả đủ mọi lựa chọn của ô có điều kiện (bản cũ chỉ đọc lựa chọn đầu + cuối); áp các
  khối TUẦN TỰ trên cùng tệp (agent vừa làm nhiệm vụ cổng vừa chạy trong ca lâm sàng — tính từ bản gốc riêng sẽ đè nhau).
- `tests/test_agent_co_dieu_phoi_20261010.py`: CHỐT CHỐNG MỒ CÔI — mọi agent nghiên cứu có nhiệm vụ/vai ở hội đồng cổng;
  mọi agent lâm sàng có bước chạy VÀ hạng mục tự-rà; mọi tệp agent thuộc ít nhất một điều phối.

Repo gốc (PR này): bảng §3 của `dieu-phoi-g1/g5/g6`; `dieu-phoi-lam-sang` thêm C8c (`ket-qua-hoc-tap` +
`cap-nhat-guideline`), C5 thêm `huong-dan-lam-sang` (đối chiếu hướng dẫn hiện hành/EtD), đoạn «hai bảng là nguồn giao
việc»; khối sinh cho 21 agent lâm sàng + 5 agent nghiên cứu; `_HOI-DONG-CONG.md` §1b mục 10.

## Kiểm

- Test mới 52 ca (+ cập nhật lựa chọn G6-AUTO-09 ở test G6-T2; đồ gá test bộ sinh chép thêm tệp nguồn nhạc trưởng — bộ
  sinh nay ĐỌC tệp đó).
- Đột biến **12/12** bị bắt, CÓ lượt nền xanh (agent mất vai ⇒ mồ côi · bảng tự-rà đọc mọi ô · không bỏ hàng tiêu đề ·
  khối tính từ bản gốc riêng · bỏ kiểm ≥ 2 nghiên cứu · bỏ seTE > 0 · bỏ biến cố ≤ cỡ nhóm · mất điều kiện prediction ·
  đảo thứ tự G6-AUTO-09 · khối lâm sàng bỏ hạng mục · bỏ C8c · kiểm dự báo trỏ nhầm nhãn).
- Đo C1a (chỉ đọc, SHA-256 trước = sau): cắt ngang ⇒ các nhiệm vụ thiết kế mới không áp dụng; G1 nay chờ khai G1-T4 và
  G1-T8; GIAO TRƯỚC vẫn là G0.
