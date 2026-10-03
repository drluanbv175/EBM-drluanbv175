# 04/10/2026 — «Có tệp toàn văn» khác «đã đọc»: bộ đọc sâu bỏ sót PDF Wiley TDM và gần như mọi PMID dashboard

**Đo 03/10/2026 trên 72 dashboard:** chỉ 18/163 PMID của mục `decision='apply'` có bản đọc sâu
(`toan_van_oa/doc_sau/`), trong khi kho đã có sẵn tệp toàn văn cho 68 PMID apply chưa ai đọc: 39 XML PMC, 11 `_UPW.*` và
18 `_WTDM.pdf`. Toàn kho có 21/674 PMID được đọc sâu.

**Nguyên nhân ở `tools/doc_sau_toan_van.py`:**
- Công cụ không nhận `PMID-<n>_WTDM.pdf`, tức PDF tải qua kênh TDM của Wiley bằng token của bác sĩ. Vì vậy gói tuần
  (bước 4b) vẫn báo «CHỈ TÓM TẮT» dù PDF hợp lệ nằm trong kho.
- Công cụ chỉ chạy theo `--queue`/`--pmid`, nên PMID của dashboard không bao giờ qua bộ bóc.
- Lỗi tiềm ẩn: XML được xét TRƯỚC hồ sơ trình duyệt. Nếu bản OA về kho sau lượt đọc trình duyệt có bác sĩ, bộ bóc JATS
  sẽ ghi đè im lặng `doc_sau/PMID-<n>.md`. Đo 04/10: 42/42 bản đọc trình duyệt còn nguyên, 0 PMID đang có cả hồ sơ
  trình duyệt lẫn XML. Lỗi chưa gây hại.

**Cách vá:**
- **PDF kênh TDM:** đọc bằng pypdf; máy thiếu thư viện thì báo rõ, không gãy, không xếp «chỉ tóm tắt». Bài có bản
  quyền nên bản đọc chỉ ghi dữ kiện (bản đồ mục, mã đăng ký, dấu hiệu phương pháp), vị trí trang và trích ≤ 15 từ mỗi
  lần, cùng trần với làn trình duyệt. PDF dưới 3000 ký tự chữ thì báo lỗi, không sinh bản đọc giả.
- **Mục ngắn có trần ký tự** (Tài trợ 2500, Hạn chế 4000): quá trần thì trả về mục đứng trước. Trần được xét TRƯỚC
  khi nhận dòng, vì pypdf có khi trả cả đoạn trên một dòng. Đo 03/10: dòng «Funding information» ở cột bên trang 2
  của PMID 34343358 từng biến 13 trang thân bài thành «tài trợ».
- **Chế độ dashboard:** `--dashboard [tệp…]` và `--chi-apply` lấy PMID bằng chính bộ tách mục của cổng
  `verify_dashboard`, đếm theo đơn vị PMID. Bản đọc máy đã có được giữ, trừ khi dùng `--lam-lai`.
- `--dash` cho phép chạy từ worktree. Kho vắng thì báo KHÔNG ĐO ĐƯỢC (mã 2), không kết luận «chỉ tóm tắt».
- **Bản đọc của làn trình duyệt có bác sĩ không bao giờ bị ghi đè.** Hồ sơ có mà thiếu bản đọc thì báo lỗi; máy không
  sinh thay.
- Bước 4b của `sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md` dạy agent: thẩm định bài TDM thì mở chính PDF ở
  trang ghi kèm, không chép đoạn văn. Chỉ dựa bản đọc máy thì xếp `partial`.

**Kiểm hồi quy:**
- `tools/test_doc_sau_tdm_dashboard_20261003.py` có 18 test. Kiểm đột biến 14/14 đỏ đúng chỗ rồi phục hồi xanh.
- Fixture của `test_doc_sau_dem_ban_doc_trinh_duyet` được sửa cho khớp trạng thái thật: `--nap --ghi` luôn ghi cả hồ
  sơ lẫn bản đọc. Assertion giữ nguyên.

**Bài học:** đếm «có tệp» không phải đếm «đã đọc». Một bộ bóc chỉ chạy theo hàng chờ tuần thì với kho dashboard nó coi
như không tồn tại (CLAUDE.md §6.4: công cụ không ai gọi thì không tồn tại).
