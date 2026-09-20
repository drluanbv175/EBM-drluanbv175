# Đánh giá hệ thống toàn diện — 20/09/2026

> Phương pháp: chạy các công cụ TỰ ĐO của chính hệ (không nhận định cảm tính), đối chiếu chéo với nguồn ngoài khi có phát hiện bất thường.
> Mọi số liệu dưới đây là số đo tại thời điểm chạy. **Cần bác sĩ kiểm chứng.** Hệ chỉ ĐO và ĐỀ XUẤT; quyết định lâm sàng/cấu hình là của bác sĩ.

## 1. Bảng điểm theo tầng

| Tầng | Đánh giá | Bằng chứng đo được |
|---|---|---|
| Toàn vẹn chứng cứ (fail-closed) | 🟢 mạnh — có **1 báo động giả** cần xử lý | audit tổng 16/17 trục PASS; cổng liêm chính chặn đúng; xem §2.1 |
| Tự động hoá nền | 🔴 **ĐANG CHẾT** | 3/4 tác vụ nền bị xoá khỏi bộ lập lịch (§2.2) |
| Cấu hình môi trường | 🔴 lệch | ngân sách danh sách skill 0,08 (khai báo 0,1); phiên này mở ở thư mục tạm nên hook tự vá không chạy (§2.3) |
| Đồng bộ nhiều nhánh/máy | 🟡 phân kỳ | nhánh gốc đi trước 20, lạc hậu 52 commit so với `origin/master`; dry-run hợp nhất chỉ 3 xung đột (§2.4) |
| Chất lượng kỹ thuật | 🟢 | engine 5.713 test đạt · 15 bỏ qua · 0 lỗi; ruff sạch; 105 chốt bài học xanh; CI repo y khoa có run thành công liên tiếp; Dependabot 0 cảnh báo mở ở cả 2 repo |
| Kết nối nguồn | 🟢/🟡 | 7/8 nguồn lõi chạy thật; Semantic Scholar bị 429 (không khoá); PubMed trực tiếp chạy lại nhờ VPN |
| Độ tươi chứng cứ | 🟡 tiến sát ngưỡng | 64 chủ đề, trung vị 82 ngày, 55 chủ đề > 35 ngày, lâu nhất 105 ngày (ngưỡng đỏ 120) |
| Khối nghiên cứu (G0–G10) | 🟢 kỹ thuật · 🟡 người thật | verifier chuẩn nghiên cứu 6/6 PASS; C1a 40 xanh · 39 việc người thật · 0 đỏ; 0/4 cổng cứng có chữ ký |
| Tầng lâm sàng an toàn | 🟡 | safety-net 8/8 hội chứng có nguồn, lời dặn bệnh nhân 7/8 (bác sĩ tự viết) |
| Tài liệu | 🟡 lệch | CLAUDE.md từng khẳng định 4 tác vụ nền đang chạy — đã đính chính |

## 2. Phát hiện chi tiết

### 2.1 🔴→🟡 «Nguồn bị rút» trong `TienLuongSuyTim_20260914` ITEM-11 rất có thể là BÁO ĐỘNG GIẢ
- Audit tổng báo **FAIL chỉ vì dashboard này**; đó là hành vi đúng của cổng fail-closed.
- ITEM-11 (`decision: apply`) dựa trên guideline CCS/CHFS 2025 (PMID 41110921, doi:10.1016/j.cjca.2025.07.027).
- Cơ chế cờ: PubMed gắn `Retracted Publication` + `RetractionIn` → PMID 41422828. Nguyên văn thông báo (Europe PMC): *«this article is an
  accidental duplication of an article that has already been published, https://doi.org/10.1016/j.cjca.2025.12.030. The duplicate article has
  therefore been withdrawn.»* Tiêu đề thông báo: «WITHDRAWN: **Corrigendum** to …». Tức thứ bị rút là **bản đính chính trùng lặp**, không phải guideline.
- Guideline còn nhận hai «Author Correction» (10.1016/j.cjca.2025.12.030 và 10.1016/j.cjca.2026.03.026, tháng 9/2026). **Nội dung hai bản này CHƯA đọc
  được** (trả phí, trang nhà xuất bản chặn) — chúng có thể đổi khuyến cáo nên bác sĩ cần đọc trước khi bỏ cờ.
- **Bài học kiến trúc:** chuỗi 3 tầng rút bài (Retraction Watch → NCBI → Europe PMC) KHÔNG độc lập với loại lỗi này — cả ba dựa trên cùng một liên kết
  NLM gắn nhầm nên cùng nói «đã rút».
- Giải pháp: xem §3 mục A.

### 2.2 🔴 Tự động hoá nền đã chết
- `list_scheduled_tasks` chỉ trả 1 tác vụ (`kiem-thang-diem-quy`, chưa từng chạy). `thu-thap-tuan-an-toan-thuoc`, `goi-duyet-tuan-ebm`, `cap-nhat-thang-ebm`
  đều `taskDeleted: true` (chạy lần cuối 07/09 · 07/09 · 01/09); `giam-sat-acc-aha-quy` không còn.
- `SKILL.md` của cả 13 tác vụ vẫn còn trong `~/.claude/scheduled-tasks/` ⇒ tạo lại rẻ. Chưa biết việc xoá là chủ ý hay do sự cố.
- Hệ quả: chuỗi giám sát tuần không tự chạy từ sau 07/09; đây là nguyên nhân sâu của độ tươi trượt (§2.5).

### 2.3 🔴 Cấu hình người dùng bị ghi đè và hook tự vá không chạy
- `kiem_cau_hinh_nguoi_dung.py`: `skillListingBudgetFraction` đang **0,08**, bản khai là **0,1** (kho 1.668 mục cần ~68.000 ký tự, 0,08 chỉ cho 64.000 ⇒ danh sách skill bị cắt ⇒ «skill cài rồi mà gọi không được»).
- Phiên này mở ở thư mục tạm nên 8 hook `SessionStart` (gồm `tu_sua_chua`) báo «KHÔNG CHẠY» — cơ chế tự vá không có cơ hội chạy. Mở Claude **trong thư mục repo** để hook chạy.

### 2.4 🟡 Nhánh gốc phân kỳ với `origin/master`
- 20 commit chỉ có ở nhánh làm việc; 52 commit chỉ có ở master (108 tệp, +6.703/−455 dòng: sửa cascade `duong_goc()`, vá `verify_vi.py`, vá chốt BH30/BH39…).
- Dry-run `git merge-tree` (chỉ đọc): **3 xung đột** — `cloud-mirror/trang-thai-chung-cu.json`, `tools/chot_hoi_quy_bai_hoc.py`, `tools/kiem_dieu_phoi.py`; còn lại tự hợp nhất.
- Rủi ro nếu để lâu: hai «sự thật» song song (đã từng dẫn tới kết luận âm tính giả — BH93).

### 2.5 🟡 Độ tươi chứng cứ
- 55/64 chủ đề quá 35 ngày; 5 chủ đề lâu nhất 104–105 ngày (BienChungThanKinh_DTD, AnToanThuoc_MHRA, Uptodate, BenhThanMan_CKD, W24) — còn ~15 ngày tới ngưỡng đỏ 120.
- Sổ xác minh: 1.582/1.710 (92%) còn hiệu lực; 125 mục chưa/hết hạn (62 chưa kiểm rút bài; 63 lý do khác).
- Retraction Watch offline 37 ngày tuổi (giới hạn 30).
- 114 mục `apply` có tổng hợp MỚI HƠN — bản đặt-cạnh đã có sẵn (`DAT-CANH-CHUNG-CU-MOI_2026-08-27.md`), bác sĩ tự so.

### 2.6 Việc nhỏ đã xử lý trong lượt này
- `HO_SO_CHO_KY_…C1a.docx` sai chuẩn trình bày (12pt, 21 ký tự trang trí) → dựng lại từ chính `.md` (nguồn không đổi) → C1a **0 đỏ**.
- `CLAUDE.md`: đính chính đoạn «4 tác vụ nền đang chạy».

### 2.7 Quan sát khác
- Semantic Scholar: 429 vì không có khoá (nguồn không lõi). openFDA test-live trả 404 = «không có kết quả» theo quy ước openFDA cho truy vấn thử đó — nên đổi truy vấn thử sang thuốc có sự kiện đã biết để phép đo có ý nghĩa.
- Sổ việc chưa đóng (tầng cuộc gặp, dựng 22/08) **chưa từng có bản ghi nào**: công cụ tồn tại nhưng chưa vào thói quen.
- Plugin: `claude-code-harness` 5.14.1→5.15.0; `cochrane` mới so với mốc — chạy `sau_cap_nhat_plugin.py --ghi-moc` sau khi sửa §2.3.
- C1a: chưa cổng cứng nào có chữ ký; nút thắt là ký IRB/PI/thống kê/phản biện thật và khoá Ed25519 vai `DATA_MANAGER` (G5), không phải công cụ.

## 3. Giải pháp đề xuất (theo thứ tự)

**A. Xử lý loại báo động giả «thông báo đính chính bị rút» (đề xuất tốt nhất, gồm cả người và máy)**
1. 👤 Bác sĩ mở 2 Author Correction (DOI ở §2.1), xác nhận không đổi khuyến cáo → quyết định giữ/hạ ITEM-11.
2. 🤖 Máy: phân loại riêng trạng thái «thông báo đính chính bị rút» (tiêu đề bắt đầu `WITHDRAWN:` + `Corrigendum|Erratum|Correction`, hoặc nguyên văn «accidental duplication»). **Không tự bỏ cờ:** giữ chặn mặc định, chỉ chuyển thành «cần bác sĩ xem» kèm nguyên văn thông báo.
3. 🤖 Sổ miễn trừ do BÁC SĨ ký (`rut-bai-da-xem-xet.json`), gắn với **dấu vân tay của tập thông báo**: miễn trừ mất hiệu lực nếu xuất hiện thông báo mới — một lần rút bài thật sau này vẫn chặn.
4. 🤖 Chốt hồi quy (BH106) + đột biến; áp cho cả 3 bản `verify_dashboard.py` (skill × 2 + EBM-Dashboards).

**B. Khôi phục tự động hoá nền** — tạo lại 3–4 tác vụ từ `SKILL.md` còn trên đĩa (T2 18:00 thu thập · T2 18:30 gói duyệt · mùng 1 cập nhật tháng · quý ACC/AHA). Cần bác sĩ đồng ý (cấu hình bền).

**C. Sửa cấu hình:** `python3 tools/kiem_cau_hinh_nguoi_dung.py --ap-dung` (sao lưu trước, chỉ ghi đúng khoá đã khai). Cần bác sĩ đồng ý (ghi vào `~/.claude/settings.json`).

**D. Hợp nhất nhánh:** hợp nhất `origin/master` vào nhánh làm việc trong nhánh tạm, giải 3 xung đột (mirror: sinh lại; registry chốt: hợp hai phía; `kiem_dieu_phoi`: xem tay), chạy đủ chốt + test, rồi mở PR. Rủi ro thấp (đã dry-run).

**E. Tải mới Retraction Watch (63 MB)** — cần bác sĩ cho phép tải.

**F. Chạy ngay các việc máy làm được** (không cần quyết định): `so_xac_minh_nguon.py --vong 3` (NCBI đã chạy lại nhờ VPN); cập nhật 5 chủ đề lâu nhất bằng `ops/orchestrator.py --topic <X> --online`.

**G. Việc thuần của bác sĩ:** lời dặn bệnh nhân 1/8 hội chứng còn thiếu; ký cổng cứng C1a; khoá `DATA_MANAGER`; đọc bản đặt-cạnh 114 mục.

## 4. Chưa kiểm được (nói thẳng)
- Nội dung hai Author Correction của guideline CCS/CHFS (trả phí; trình duyệt tích hợp bị từ chối các trang này).
- Việc xoá 3 tác vụ nền là chủ ý hay sự cố.
- Chưa chạy lại toàn bộ 64 chủ đề với `--online` (tốn nhiều lượt gọi); độ tươi ở đây là tuổi gói, không phải tuổi chứng cứ bên trong.
