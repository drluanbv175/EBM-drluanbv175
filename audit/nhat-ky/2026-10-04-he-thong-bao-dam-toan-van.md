# 04/10/2026 — Hệ thống DẶN đọc toàn văn nhưng không KIỂM ⇒ dựng BẢO ĐẢM ĐỌC TOÀN VĂN bốn lớp (BH161)

**Bác sĩ:** «hệ thống hiện tại đã đảm bảo việc phủ chứng cứ và đọc toàn văn cho tôi chưa» → «hệ thống hiện tại chưa bảo đảm
được việc đọc toàn văn; Hãy xây dựng đảm bảo việc đọc toàn văn cho tôi».

**Đo trên mã sống (04/10):**
- Luật «TẦNG TOÀN VĂN» (15/08) chỉ chặn `apply` khi mục TỰ KHAI `appraisalCompleteness:'partial'`.
  - Chỉ 6/342 mục apply có khai.
  - 27 mục apply (20 PMID) không có toàn văn trong kho vẫn qua cổng.
- `ops/orchestrator.py --topic` (A2 → A4 → B2 → B5) không có bước toàn văn nào.
- `doc_toan_van_co_nguoi.bao_phu_cuc_bo` (nguồn trạng thái toàn văn) tính mọi `_UPW.*` là «oa_khac», kể cả trang giới thiệu kho
  lưu trữ (BH160).

**Dựng bốn lớp:**
1. **Nguồn sự thật** `bao_phu_cuc_bo`: chỉ tính `_UPW.html` thật (cổng nội dung BH160). Đã đọc gồm:
   - toàn văn máy đọc (XML · `_UPW` thật · TDM · `_CHR`);
   - hồ sơ làn trình duyệt có bác sĩ;
   - «bác sĩ đã đọc trực tiếp» (`trinh_duyet/bac-si-da-doc.jsonl`, `--bac-si-da-doc`).
2. **Cổng bánh cóc** — `verify_dashboard.kiem_toan_van_apply`, cùng định nghĩa với nguồn sự thật, gọi trong `main()` khi
   `--strict-sources`:
   - mục apply chưa đọc ⇒ LỖI (chặn);
   - mục có trong SỔ NỢ `no-toan-van-apply.json` (cạnh dashboard) ⇒ cảnh báo tới hạn, quá hạn ⇒ lỗi;
   - sổ hỏng ⇒ coi như vắng (chặn) và báo;
   - tự khai `full` không thay bằng chứng;
   - không thấy kho ⇒ ⚪ không đo.
3. **Sổ** `tools/so_toan_van.py`:
   - báo độ phủ theo mức quyết định, danh sách nợ, cách trả (máy lấy · làn trình duyệt · bác sĩ đã đọc · hạ «Cân nhắc»);
   - `--tao-no` lập sổ MỘT lần, cần nguyên văn lời bác sĩ, hạn ≤ 90 ngày;
   - `--gia-han` giữ nguyên danh sách và ghi lịch sử.
4. **Giác quan** `tu_de_xuat_viec.giac_quan_no_toan_van`: hòm việc nhắc nợ mỗi phiên — chặn hoặc ≤ 7 ngày tới hạn ⇒ ưu tiên 1.

Thêm **bước «TV»** cho chuỗi theo chủ đề (`tools/toan_van_theo_chu_de.py`, giữa A2 và A4/B2, phụ trợ):
- gom bản hợp lệ;
- đọc sâu;
- lập phiếu làn trình duyệt cho bài còn thiếu.

**Sổ nợ đã lập (dữ liệu, ngoài git):**
- 27 mục / 20 PMID, hạn 2026-11-03.
- Căn cứ: nguyên văn hai câu của bác sĩ ở trên.

**Đo sau khi dựng:**
- 72 dashboard: 27 cảnh báo «NỢ TOÀN VĂN», 0 lỗi mới, 0 dashboard đổi mã thoát.
- Dashboard thật đặt cạnh kho mà không có sổ nợ ⇒ 3 lỗi, mã thoát 1 (đúng thiết kế).

**Kiểm:**
- `tools/test_toan_van_bao_dam_20261004.py`: 17 test, có test chạy `main()` thật. Đột biến 9/9 làm test đỏ.
- BH161: đột biến 5/5 làm BH161 đỏ (bánh cóc, hạn, bác sĩ đã đọc, dòng thi hành, bước TV).
- 649 test liên quan xanh.

**Giới hạn còn lại (quyền truy cập, không phải mã):**
- Bài tường phí hoặc bị trang NXB chặn máy: bác sĩ mở theo phiếu (làn trình duyệt).
- Bài không có quyền truy cập: bác sĩ hạ «Cân nhắc» hoặc tự đọc rồi ghi `--bac-si-da-doc`.
- Mục không có PMID (guideline chỉ có URL/DOI) chưa nằm trong phạm vi đo của sổ.
- Sau khi gộp: chép cổng sang `EBM-Dashboards/tools` + `EBM_MASTER/skill_assets`. Cổng mới chạy được ngay vì sổ nợ đã lập trước.
