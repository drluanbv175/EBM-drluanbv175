# 15/10/2026 — Rà đồng bộ làn Chrome đọc toàn văn + EndNote: 36 phát hiện, 2 quyết định của bác sĩ

**Câu hỏi của bác sĩ:** «kiểm tra xem đã đồng bộ về làn Chrome giúp đọc toàn văn, kết nối với EndNote tất cả đã được đồng bộ
chưa». Trả lời đo được: **CHƯA** — rà chỉ đọc 4 chiều (đấu dây · dạy agent/skill · đa nền · trạng thái giữa máy), mỗi phát hiện
qua một người phản biện cố bác bỏ: 36 phát hiện đứng vững (0 bị bác bỏ) + 3 khoảng trống do phê bình độ phủ tìm thêm.

## Nguyên nhân chung

Làn Chrome (BH152/BH158/BH159), tầng Unpaywall (BH160), bảo đảm toàn văn (BH161) và EndNote (11–13/10) được thêm theo từng
đợt, mỗi đợt sửa đúng công cụ của mình; các chỗ dùng chung (doctrine, skill, phiếu ⑦, bộ đếm phủ, khối ĐỌC NHANH) không được
sửa cùng lúc. Kết quả: ba định nghĩa «có toàn văn» khác nhau, doctrine dạy «không lưu toàn văn» trong khi phiên uỷ quyền lưu
`_CHR`, lệnh trong skill không chạy được, và vài lỗi đa nền/fail-closed.

## Đã vá (PR gốc + PR engine #134)

- **Dạy agent/skill (g1):** §2septies mục 7–8 có ngoại lệ có tên «PHIÊN UỶ QUYỀN LƯU BẢN SAO»; §0.8 trỏ bảng `DIEU_KHOAN_NXB`
  thay vì liệt kê 15/28 NXB; `tong-thuat-chung-cu` tra điều khoản TRƯỚC WebFetch/Browser/luu_guideline và bỏ `_MCP.md`;
  `cap-nhat-guideline` mã 1 đi theo §2septies; CLAUDE.md §6.4 ngoại lệ Scopus/WoS qua làn Chrome có uỷ quyền; hai skill sửa
  lệnh `nap_endnote_chu_de.py --file <dashboard> --tom-tat-vi --ap-dung` + khuôn khoá kho tóm tắt; gói tuần thêm `--unpaywall`;
  `tra_cuu_co_tai_khoan.py` thôi dạy Claude đọc trang DynaMed.
- **Dây chuyền (g2):** bước TV quá giờ không còn dừng cả lô (TV 3300 s ≥ 3×900; ⑦ có trần riêng 3000 s, B4 6600 s); báo cáo TV
  và số bài thiếu vào phiếu cuối lượt; phiếu ⑦ tách «chưa đo được (lỗi mạng)» khỏi «cần bác sĩ»; «Claude lưu bản sao» chỉ in
  cho NXB có uỷ quyền; ⑧ truyền `--chua-xac-minh` khi cổng chưa PASS sống; `intent.py` định tuyến EndNote / phiên uỷ quyền /
  sổ nợ toàn văn.
- **Kho & trạng thái (g3):** một nguồn sự thật `bao_phu_cuc_bo` cho cổng, sổ DO-PHU-OA và khối ĐỌC NHANH; chỉ nhận tên tệp
  khớp NGUYÊN (tệp tạm `.tam-*` không còn thành «đã đọc»); `_CHR.html` qua cổng nội dung như `_UPW.html`; sổ phiên lưu trữ
  phiên cũ, sổ hỏng ⇒ mã 2; kho vắng ⇒ ⚪ mã 2, không tự dựng thư mục ma; `tom_tat_endnote_vi.py --mau`.
- **EndNote & đa nền (g4):** luật R7 (subprocess `text=True` thiếu `encoding`) + vá mọi vị trí 🔴; ngoài Mac báo `--xuat-xml`
  trước khi đòi cấu hình; kiểm EndNote đang chạy bằng `is running` trước `tell application` (không tự bật EndNote, có trần thời
  gian); so thư viện bằng `samefile`; cấu hình hỏng ≠ vắng (không xoá bảng `nhom_theo_chu_de`).
- **Ghép:** `doc_cau_hinh` cùng điều kiện `ly_do_cau_hinh_hong`; khối ĐỌC NHANH nói «chưa xét» khi không đo được độ phủ;
  `tra_cuu_co_tai_khoan` thấy engine ở bố cục anh em; engine: `run_g0_auto` giải mã UTF-8, `.gitignore` bắt `toan_van_oa/`.

## Hai quyết định của bác sĩ (15/10/2026)

1. **Bản thảo tác giả PMC «TDM»** (NIH Public Access; gói PMC Cloud `license_code: "TDM"`, Europe PMC `authMan: "Y"`) — câu hỏi
   đặt ra vì `gom_toan_van_dashboard.py` (#174) đã tải loại bản này kể cả của NXB «cấm» (ca PMID 22591294, NEJM) trong khi
   doctrine ghi «ngoại lệ duy nhất là CC». Nguyên văn bác sĩ: «Điều chỉnh để đọc và tải toàn văn,máy đọc toàn văn cho tôi».
   ⇒ §2septies mục 1 ngoại lệ (b) + mục 5 + mục 7; `duong_doc` xếp bài có bản thảo tác giả vào «có bản PMC — chạy gom» thay cho
   «BÁC SĨ ĐỌC TRỰC TIẾP». Quyết định và trách nhiệm của bác sĩ theo giấy phép TDM của PMC — KHÔNG phải «NXB cho phép».
2. **GOLD · GINA · BTS** (G3-D5): đọc trang pháp lý 15/10 qua WebFetch — cả ba IM LẶNG về AI/TDM (GOLD/GINA cấm tái bản khi chưa
   có văn bản cho phép; BTS Terms 05/2023 chỉ cho dùng cá nhân phi thương mại) ⇒ «không rõ ⇒ xử như cấm», ba khoá theo MIỀN
   trong `DIEU_KHOAN_NXB`. Theo uỷ quyền THƯỜNG TRỰC 04/10/2026 (§2septies mục 8): ghi `--ghi-uy-quyen` cho ba khoá trên máy có
   `EBM-Dashboards/` (phiên Cloud không có thư mục đó).

## Kiểm

- Mỗi chốt mới kiểm đột biến (gỡ bản vá ⇒ đỏ đúng chỗ ⇒ phục hồi ⇒ xanh); 4 nhóm có phản biện độc lập, 2 nhóm qua một vòng sửa.
- `pytest tools/` trên cây ghép: 3110 đạt trước bước ghép cuối; đỏ có sẵn từ trước (đỏ y hệt trên `master` sạch):
  `test_research_practical_readiness.py::test_practical_readiness_verifier_runs_end_to_end` — phụ thuộc engine trên Cloud,
  không liên quan PR này.

## Để lại (thẩm quyền bác sĩ / máy thật)

- Ghi uỷ quyền 3 khoá GOLD/GINA/BTS (`doc_toan_van_co_nguoi.py --ghi-uy-quyen`) trên Mac.
- TT-04 đổi dữ liệu thật: `_CHR.html` thân bài ngắn (research letter) có thể rơi từ «phiên Chrome» về «chưa có» — đo
  `python3 tools/so_toan_van.py` trên Mac trước/sau khi gộp.
- Chép `sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md` sang runtime tác vụ lịch (§9); tải lại skill tài khoản
  (`dong_goi_skill_tai_khoan.py`).
- Khoá orchestrator ghi mốc MỘT lần lúc giành (không làm mới) ⇒ lô dài vượt `HAN_KHOA_GIAY` (4 giờ) có thể bị coi mồ côi —
  có từ trước, cần thiết kế làm mới khoá theo bước.
- `luu_guideline.py` chưa tự gọi `nxb_cua` (cổng điều khoản hiện ở skill).
