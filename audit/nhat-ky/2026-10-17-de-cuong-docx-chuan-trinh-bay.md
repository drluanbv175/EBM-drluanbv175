# 17/10/2026 — Đề cương nộp Hội đồng xuất Word ra bảng 12pt và giữ «☐»: bộ chuyển của repo gốc chưa đi qua chuẩn trình bày

**Triệu chứng:** trục ④ của `medical-ebm-automation/tools/kiem_chi_tiet_he_nghien_cuu.py` báo
`DE_CUONG_NOP_HOI_DONG_<mã>.docx` của C1a sai chuẩn. Đo lại 17/10 trên bản dựng bằng
`tools/md_sang_docx_times.py --co-chu 13 --trang-de-cuong`: thân 13pt đúng, **bảng 12pt** (chuẩn 11), **267 ký tự
trang trí** — toàn bộ là «☐» U+2610 (Times New Roman không có hình chữ, in ra ô rỗng). Cùng ngày đã vá tay tệp bằng
`chuan_trinh_bay.ap_dinh_dang_tai_lieu(doc, co_chu=13)`.

## Nguyên nhân

- Chế độ `--trang-de-cuong` (thêm 15/10, gốc #179) đặt cỡ bảng = cỡ thân − 1 và không làm sạch ký tự.
- Gốc sâu hơn: `md_sang_docx_times.py` nằm ở repo GỐC nên là một điểm `doc.save` ngoài danh sách 11 bộ sinh .docx
  (`BO_SINH_DOCX`) mà chuẩn bắt phải đi qua `chuan_trinh_bay.py` — cổng đo đúng, bộ sinh thì không ai buộc.

## Đã vá (`tools/md_sang_docx_times.py`)

- Chế độ đề cương nạp `medical-ebm-automation/tools/chuan_trinh_bay.py` (dò qua `ban_sao_tran.duong_goc()`, nạp
  theo đường dẫn tệp, không chèn sys.path) và gọi `ap_dinh_dang_tai_lieu` — bảng ký tự giữ một nguồn, không chép.
  Bảng 11pt (`CO_CHU_BANG_DE_CUONG`, test canh khớp `CO_CHU_BANG`).
- **Phát hiện kèm — mũi tên mang nghĩa:** gọi nguyên khối thì `lam_sach_van_ban` còn đổi 21 «→» của đề cương C1a thành
  « đến »: mục DAG «Tuổi → BHYT → thời gian chờ → hài lòng» thành «Tuổi đến BHYT đến…», ô sơ đồ luồng «→ Từ chối»
  thành « đến Từ chối». «→» không thuộc tập trục ④ đếm và Times New Roman có hình chữ ⇒ ký tự nào bộ làm sạch đổi mà
  trục ④ không coi là trang trí được thay tạm bằng ký tự PUA quanh lời gọi rồi trả lại (tập suy tự động từ
  chuan_trinh_bay, không liệt kê tay). Kết quả đo: chỉ 267 «☐» → «[ ]» đổi; 1.885/1.885 đoạn còn lại giống từng ký tự.
- Cỡ đề mục > cỡ thân (tên đề cương 19pt, đề mục 14–16pt) được trả lại sau lời gọi — hàm chung ghi cỡ thân lên mọi run.
- Không nạp được repo y khoa ⇒ vẫn ghi tệp, bảng 11pt, nhưng báo 🟡 «CHƯA làm sạch» và **mã thoát 1** (không dấu xanh
  giả). Chế độ thường không đổi.

## Kiểm hồi quy (17/10/2026)

- Đề cương C1a dựng lại (vào scratchpad, KHÔNG ghi đè `exports/`): `kiem_docx` ⇒ Times New Roman · thân 13 · bảng 11 ·
  0 ký tự lạ; lề 3/2/2/2 cm, 15 ngắt trang, 372 đoạn căn đều, trường PAGE — y hệt bản cũ; K1/K2 của
  `kiem_de_cuong_nop_hoi_dong.py` đạt.
- `tools/test_md_sang_docx_times_chuan_trinh_bay_20261017.py` (5 test): đo bằng chính `kiem_docx` (tiến trình con),
  đối chiếu bản không áp chuẩn (thước đo không mù, bố cục giữ nguyên, chỉ «☐»/«☑» đổi). Đột biến 9/9 bị bắt đúng
  test (`python -B`, xoá `__pycache__`, phục hồi + `cmp`). Bản sao trần: 3 test skip có lý do, 2 test dự phòng vẫn chạy.
- Trọn bộ `tools/`: 3.135 qua · 37 skip · 0 lỗi.

**Còn mở (repo y khoa):** 11 bộ sinh của cổng gọi `ap_dinh_dang_tai_lieu` nguyên khối nên «→»/«⇒» trong bản Word
G1/SAP… cũng bị đổi thành « đến »/« suy ra » — chưa đo, cần bác sĩ quyết có giữ mũi tên ở đó không.
Cần bác sĩ kiểm chứng.
