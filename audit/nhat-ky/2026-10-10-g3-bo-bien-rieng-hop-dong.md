# 10/10/2026 — G3-T2/G3-T3: đầu ra khai SAI tệp (cỡ mẫu A4) · agent biến số không biết tệp hợp đồng `_bo-bien-rieng.csv` · kiểm máy cấp nhiệm vụ

Bác sĩ giao: «Gộp PR và tiếp tục hoàn thiện từng Agent và từng điều phối». Đã gộp 9 PR (gốc #141 #138 #139 #140 #142 ·
y khoa #98 #99 #100 #101 — #101 sau khi CI Windows xanh). Vòng hoàn thiện kế tiếp đo «nhiệm vụ không có tiêu chí máy».

## Phát hiện (đo 10/10)

- Lệnh/cờ, tên đầu ra danh mục, mã trạng thái trong mọi tài liệu agent/điều phối: khớp công cụ (0 lệch có thật).
- **G3-T2 «Đặc tả bộ biến số»** (`bien-so-nghien-cuu`) và **G3-T3 «CRF kỹ thuật, từ điển dữ liệu dự kiến, luật kiểm
  tra»** (`quan-ly-du-lieu`) khai đầu ra `G3_A4_SAMPLE_SIZE_<mã>.md` — tệp cỡ mẫu chỉ có 5 phần về cỡ mẫu, KHÔNG có biến
  số/CRF ⇒ bảng trách nhiệm coi hai nhiệm vụ «có đầu ra» chỉ vì tệp cỡ mẫu tồn tại.
- Hợp đồng THẬT đã có từ 01/09/2026: `run_g5_auto.nap_bo_bien_rieng` nạp `exports/<mã>/_bo-bien-rieng.csv` (REDCap 18 cột)
  làm nguồn biến DUY NHẤT của G5 (vắng ⇒ G5 rơi về bộ biến mẫu theo chuyên khoa; hỏng ⇒ G5 DỪNG). Nhưng agent
  `bien-so-nghien-cuu` KHÔNG được dặn lưu tệp này (không tài liệu agent nào nhắc tên tệp). C1a có tệp này (lập tay).

## Vá

Repo y khoa (drluanbv175/medical-ebm-automation#102):
- Danh mục: đầu ra G3-T2/G3-T3 = `_bo-bien-rieng.csv` (test chốt bằng hằng `run_g5_auto.BO_BIEN_RIENG_TEN_FILE`).
- `hoi_dong_cong.KIEM_NHIEM_VU` — kiểm máy CẤP NHIỆM VỤ (không phải tiêu chí cổng, không đổi trạng thái cổng; chỉ cấu
  trúc): G3-T2 = bộ biến nạp được bằng ĐÚNG hàm G5 dùng + không biến định danh trực tiếp (luật G5-AUTO-02); G3-T3 = luật
  kiểm tra CRF (danh sách lựa chọn, công thức calc, khoảng min/max cho trường số, có trường bắt buộc). Lỗi ⇒
  `AGENT_CON_VIEC` của đúng agent; thiếu tệp ⇒ «thiếu đầu ra», không ghi «đã kiểm máy».
- Bộ sinh tài liệu trách nhiệm ghi chú nhiệm vụ có kiểm máy cấp nhiệm vụ.

Repo gốc (PR này): `bien-so-nghien-cuu.md` + `quan-ly-du-lieu.md` dạy tệp hợp đồng (10 cột bắt buộc, quy tắc tên biến,
`record_id` đầu tiên, không định danh; G5 nạp làm nguồn duy nhất); `dieu-phoi-g3.md` §3 sửa cột đầu ra; khối trách nhiệm
3 agent sinh lại; `_HOI-DONG-CONG.md` §1b mục 7 thêm kiểm máy cấp nhiệm vụ.

## Kiểm

- Đo C1a (chỉ đọc, SHA-256 trước = sau): `_bo-bien-rieng.csv` qua cả hai kiểm; G3 vẫn chỉ còn G3-AUTO-09/12 của agent.
- `tests/test_g3_bo_bien_rieng_hop_dong_20261010.py`: 12 ca. Đột biến **9/9** bị bắt (lượt đầu «chạy kiểm khi thiếu tệp»
  lọt ⇒ thêm khẳng định không ghi «đã kiểm máy»).

## Bổ sung cùng ngày — «từng điều phối»: bảng trách nhiệm TOÀN ĐỀ TÀI cho điều phối tổng

`python3 tools/hoi_dong_cong.py trach-nhiem --study <mã> --gate ALL` (repo y khoa): bảng 11 cổng (kết luận phần agent ·
việc agent · chờ người · chờ cổng trước · chất lượng chưa bảo đảm) + dòng «GIAO TRƯỚC» = cổng ĐẦU TIÊN G0→G10 còn việc
agent/chưa phân công; mã 1 nếu còn cổng có việc agent, 2 nếu không còn việc nhưng có cổng không đo được; `--ghi` lưu đủ 11
bảng. `dieu-phoi-nghien-cuu.md` dạy mở đầu mỗi lượt resume/march bằng lệnh này; `_HOI-DONG-CONG.md` §1b, `CLAUDE.md` §1.
Đo C1a (chỉ đọc): GIAO TRƯỚC cổng G0 cho `dieu-phoi-g0` — G0-T3 trả về sửa theo biên bản đánh giá chéo 07/10. 7 test;
đột biến 3/3 (chọn cổng cuối · «không đo được» át «còn việc» · coi «chờ cổng trước» là cần giao).
