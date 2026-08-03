---
name: antifacts
description: "Sử dụng skill này khi bác sĩ muốn MỞ hoặc CẬP NHẬT \"Antifacts\" — Trung tâm EBM theo chuyên khoa (mặt tiền gom mọi sản phẩm EBM trong thư mục \"Claude AI\" theo chuyên khoa: cập nhật chứng cứ + thang điểm lâm sàng + công cụ nghiên cứu). Kích hoạt khi nghe \"Antifacts\", \"mở Antifacts\", \"cập nhật Antifacts\", \"trung tâm EBM theo chuyên khoa\", \"hub EBM theo chuyên khoa\". KHÔNG dùng để tạo dashboard chứng cứ MỚI cho một vấn đề (dùng cap-nhat-chung-cu-y-khoa); KHÔNG phải Dashboard Master; KHÔNG phải hệ giám sát định kỳ."
metadata:
  version: 1.0.0
---

# Skill: Antifacts — Trung tâm EBM theo chuyên khoa

<!-- EBM-VN-GUARD -->
**QUY TẮC EBM BẮT BUỘC:** đầu ra tiếng Việt; **KHÔNG bịa dữ liệu** (Antifacts chỉ GOM + trình bày lại nguồn đã có, không sinh nội dung lâm sàng mới); mỗi mục y khoa giữ nguyên nguồn (PMID/DOI) sẵn trong dashboard và phân hạng GRADE gốc; kèm disclaimer "⚠️ Cần bác sĩ kiểm chứng"; **KHÔNG lưu PII**.

## 1. Antifacts là gì
"Antifacts" là **mặt tiền (HTML tĩnh) gom mọi sản phẩm EBM** đã có trong thư mục "Claude AI", sắp theo **chuyên khoa** (Tim mạch · Hô hấp · Tiêu hóa–Gan mật · Nội tiết · Thận · Thần kinh–Đột quỵ · Cơ xương khớp · Nhiễm · Tâm thần · Lão khoa · Cấp cứu · Thuốc · Tổng hợp). 4 tab: **Theo chuyên khoa** (mặc định) · **Cập nhật** · **Thang điểm** · **Nghiên cứu**.
File kết quả: `Antifacts.html` ở **gốc thư mục "Claude AI"**, sinh bằng `tools/build_antifacts.py` (chỉ dùng stdlib, KHÔNG cần venv).

## 2. Khi nào dùng skill này
- "Mở Antifacts" / "cho tôi xem trung tâm EBM theo chuyên khoa" → mục **3A**.
- "Cập nhật Antifacts" / "làm mới Antifacts" → mục **3B** (mặc định: làm giàu thư viện trước rồi dựng lại).

## 3. Quy trình
> Chạy ở **thư mục gốc "Claude AI"** (Windows: `C:\Users\<user>\OneDrive\Claude AI`; Mac: `~/OneDrive/Claude AI`).
> **Windows BẮT BUỘC** đặt `PYTHONUTF8=1` trước `python`, nếu không script crash `UnicodeEncodeError` khi in tiếng Việt qua console cp1252.
> Nguyên tắc: **KHÔNG sửa tay `Antifacts.html`** — muốn đổi bố cục/bản đồ chuyên khoa thì sửa `tools/build_antifacts.py` rồi chạy lại.

### 3A. Mở nhanh (chỉ xem)
Mở file `Antifacts.html` ở gốc "Claude AI" trong trình duyệt (hoặc bấm "Mở Antifacts.command").

### 3B. Cập nhật ĐẦY ĐỦ rồi mở (mặc định)
1. **Làm giàu thư viện** (để mọi dashboard có badge Áp dụng/Cân nhắc/PMID, không chỉ tiêu đề) — chạy trong `EBM-Dashboards/`:
   `PYTHONUTF8=1 python tools/build_library.py add WebDashboard_*.html`
   (idempotent; sau đó nên gỡ entry trỏ tới file đã archive nếu có).
2. **Dựng lại hub** — ở gốc "Claude AI":
   `PYTHONUTF8=1 python tools/build_antifacts.py`
3. **Mở** `Antifacts.html` và báo bác sĩ số liệu (X cập nhật · 45 thang điểm · 19 công cụ NC) + cảnh báo dashboard nào rơi vào "Tổng hợp / Đa khoa" (nếu generator in ra).

## 4. Nguồn dữ liệu Antifacts gom (chỉ đọc)
- **Cập nhật chứng cứ** ← `EBM-Dashboards/WebDashboard_*.html` (+ enrich từ `EBM-Dashboards/library.json`).
- **Thang điểm lâm sàng** ← `medical-ebm-automation/data/reference/clinical_scores_45.json`.
- **Công cụ nghiên cứu** ← danh mục chuẩn (RoB2/GRADE/CONSORT/STROBE/PRISMA…) trong generator, trỏ về agent tương ứng.

## 5. Liên kết với hub EBM trung tâm
Antifacts nối **2 chiều** với hub `EBM_MASTER/`: nút "🛡️ Antifacts ↗" có ở header 3 trang hub (EBM_WEBAPP/DANH_MUC/EBM_LIENKET), và Antifacts có link "↩ Hub EBM". Các nút này nằm trong **generator** (gen_*.py, build_antifacts.py), bền qua mỗi lần sync. Khi đồng bộ toàn hệ `python EBM_MASTER/tools/sync_all.py`, bước cuối cũng tự dựng lại Antifacts.

## 6. Giới hạn
- KHÔNG tạo chứng cứ/khuyến cáo mới ở đây. Muốn thêm một chủ đề lâm sàng mới vào kho → dùng skill **`cap-nhat-chung-cu-y-khoa`** (tạo dashboard), rồi chạy lại skill này để Antifacts gom vào.
- Cần môi trường **thấy được thư mục "Claude AI"** (Claude Code / phiên có quyền thư mục OneDrive). Trong Cowork sandbox thuần không thấy OneDrive thì không chạy được lệnh build — khi đó chỉ giải thích/điều hướng, không bịa kết quả.
