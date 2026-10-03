# 02/10/2026 — Toàn văn bài KHÔNG OA: thẻ tuần thẩm định từ tóm tắt vì nhà xuất bản chặn mọi truy cập tự động (BH152)

**Bác sĩ hỏi (02/10):** đã có cơ chế để các trang chặn bot (Scopus, DynaMed, ADA, ESC…) được bác sĩ xác nhận rồi máy lấy chứng cứ và
đọc toàn văn chưa? **Trả lời trung thực lúc hỏi: CHƯA.** PR #89 chỉ có hai phần.
- Ghi bằng chứng «URL còn sống»: máy chỉ đọc TIÊU ĐỀ trang, và chỉ cho `www.fda.gov`.
- Nhập metadata từ Scopus/WoS export và cảnh báo DynaMed, rồi xác minh.

Chưa có đường nào đọc TOÀN VĂN bài bị chặn. ADA/ESC chỉ nằm trong vòng canh «trang có đổi».

**Số đo.**
- **Gói tuần W40:** 5/7 thẻ «CHỈ TÓM TẮT», tức trần «Cân nhắc». Dây chuyền `gom_toan_van_dashboard.py` → `doc_sau_toan_van.py` chỉ lấy
  bản OA (kho 220 bài, phủ 203/676 PMID dashboard — `toan_van_oa/DO-PHU-OA.md`).
- **Đo truy cập tự động bằng yêu cầu TRUNG THỰC** (User-Agent khai đúng, không giả trình duyệt), 02/10/2026:
  - 403 «Just a moment…» (Cloudflare): diabetesjournals.org (ADA), academic.oup.com (ESC/EHJ), nejm.org, thelancet.com,
    jamanetwork.com, ahajournals.org, jacc.org, onlinelibrary.wiley.com, bmj.com, heart.bmj.com, journals.sagepub.com,
    tandfonline.com, karger.com, journals.lww.com, acpjournals.org, journal-of-hepatology.eu, publications.ersnet.org,
    webofscience.com.
  - Chặn kiểu khác: sciencedirect.com 403 · mdpi.com 403 · atsjournals.org 403 · link.springer.com, kdigo.org, nature.com 406 ·
    cochranelibrary.com 419 · www.fda.gov 401.
  - Mở: PMC, Europe PMC, NICE, GINA, escardio.org, frontiersin.org.
  - Bảng đo nằm trong `MIEN_DO_DUOC` của công cụ, ghi rõ «đo 02/10/2026». Miền con chưa đo được ghi «suy từ <miền mẹ>».
- **Thử trình duyệt trong app** (journals.sagepub.com, PMID 42751933): Cloudflare hiện hộp TƯƠNG TÁC «Xác minh bạn là con người»,
  tiêu đề «Chờ một chút...». Claude KHÔNG bấm; tab để nguyên chờ bác sĩ. Trình duyệt chạy giao diện TIẾNG VIỆT, nên bộ lọc tiêu đề
  của `xac_nhan_trinh_duyet.py` (chỉ mẫu tiếng Anh) đã nhận «Chờ một chút...» là tiêu đề thật. Lỗ này đã vá ở cả hai công cụ.

**Vá.**
- **`tools/doc_toan_van_co_nguoi.py`:**
  - (a) **Phiếu.** Lấy PMID trên THẺ gói tuần hoặc theo `--pmid`, soi kho cục bộ (OA XML/UPW, bản đọc trình duyệt, «không có quyền»
    trong ≤ 90 ngày). Hỏi Europe PMC và API handle của doi.org lấy URL toàn văn mà KHÔNG tải trang nhà xuất bản. Lỗi mạng ⇒ «chưa rõ»,
    không đọc thành «không có toàn văn». Phiếu nhóm theo MIỀN để bác sĩ vượt chặn một lần cho mỗi miền.
  - (b) **Quy trình** `--huong-dan`. Bác sĩ TỰ vượt chặn/đăng nhập; Claude không bấm, không giải CAPTCHA, không gõ tài khoản. Mã băm
    SHA-256 tính TRONG trình duyệt. DynaMed/UpToDate chỉ dùng để tìm nghiên cứu gốc.
  - (c) **`--nap`.** Kiểm hồ sơ trích xuất CÓ CẤU TRÚC rồi mới ghi:
    - Tiêu đề trang chặn/đăng nhập (Việt + Anh) bị từ chối; người vượt chặn phải là bác sĩ.
    - Văn bản < 3.000 ký tự bị coi là chỉ tóm tắt.
    - Bản quyền: không trường nào > 800 ký tự, trích nguyên văn ≤ 15 từ/lần và ≤ 6 lần, không có khoá chứa toàn văn.
    - Con số: trong CI, tỷ số > 0, p ∈ [0;1], mỗi số có `vi_tri`. Không có PII.
    - Định danh xác minh qua engine (`fallback_verification`); bài rút ⇒ chặn; tiêu đề lệch cơ quan đăng ký ⇒ chặn.
    - Chạy thử mặc định, `--ghi` mới ghi vào `toan_van_oa/trinh_duyet/PMID-<n>.json` và bản đọc `toan_van_oa/doc_sau/PMID-<n>.md`.
    - Độ đầy đủ theo loại tài liệu: thiếu mục ⇒ partial ⇒ trần «Cân nhắc». Mọi hồ sơ là CANDIDATE.
- **`tools/doc_sau_toan_van.py`:** đếm bài đã đọc qua trình duyệt, kèm độ đầy đủ; bài «chỉ tóm tắt» in sẵn lệnh làn trình duyệt.
- **`tools/tu_de_xuat_viec.py` ⑦i:** giác quan 👤 «N/M thẻ gói tuần chỉ có TÓM TẮT» (ngoại tuyến; gói > 14 ngày không nhắc; vắng
  queue/kho ⇒ ⚪).
- **`tools/orchestrator/intent.py`:** «toàn văn / full text / bài trả phí / paywall» ⇒ công cụ này, đứng TRƯỚC «chặn bot».
- **Bước 4b của `sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md`:** lượt lịch lập phiếu, KHÔNG mở trình duyệt.
- CLAUDE.md §6.4 thêm một dòng; BH152.

**Kiểm.**
- 46 test mới (ngoại tuyến, mạng và bộ xác minh giả).
- 10 phép đột biến đều bị bắt (sao lưu + so byte lúc phục hồi): bỏ mẫu tiêu đề tiếng Việt, bỏ kiểm người vượt chặn, bỏ kiểm CI, bỏ
  xác minh, `doc_sau` mù bản trình duyệt, giác quan câm, kho mù bản trình duyệt, lỗi mạng thành «không có», cho ghi khi engine vắng,
  bỏ chặn trích dài.
- Bản sao trần: `pytest tools/` 2187 đạt / 32 bỏ qua; `chot_hoi_quy_bai_hoc` 🟢; `kiem_tuong_thich_da_nen` 🔴 0.
- Đo SỐNG bằng symlink tạm tới dữ liệu thật, đã gỡ trước khi commit:
  - Phiếu W40 cho 5 bài qua 3 miền (heart.bmj.com, journals.sagepub.com, linkinghub.elsevier.com).
  - Nạp chạy thử một hồ sơ thử với PMID thật ⇒ engine trả `xac_minh_duoc`, KHÔNG ghi gì.
  - Giác quan in «5/7 thẻ gói tuan-2026-W40 chỉ có TÓM TẮT».

**Chưa làm được trong phiên này (cần bác sĩ có mặt).** Chưa đọc được bài nào qua làn này, vì mọi miền của thẻ W40 đều chặn TƯƠNG TÁC.
Phép đo thật đầu tiên là phiên có bác sĩ:
```
python3 tools/doc_toan_van_co_nguoi.py --queue queue/tuan-2026-W40.md
```

**Phát hiện phụ.** BH137 ĐỎ trên cây chính: PR y khoa #63 thêm `app/sources/ec_union_register.py` mà sổ `data/sources.json` chưa có
mục. Vá ở PR riêng.

## ĐÍNH CHÍNH 03/10/2026 — điều khoản nhà xuất bản về AI/TDM (góp ý của phiên Claude khác)

**Góp ý.** Bản đầu xem mọi nhà xuất bản như nhau: bác sĩ vượt chặn xong thì Claude đọc toàn văn. Nhưng điều khoản của một số NXB cấm
dùng nội dung với công cụ AI:
- **Elsevier.** Phiên này tự đọc lại trang điều khoản website, có câu «may not use Content … in combination with an artificial
  intelligence tool». Elsevier gồm ScienceDirect, Lancet, Cell, JACC, J Hepatol… — DOI 10.1016/.
- **ADA** (diabetesjournals.org, DOI 10.2337/): cấm TDM/ML khi chưa có văn bản cho phép. Phiên khác đọc; máy này gặp 403.
- **EBSCO/DynaMed:** AI phải hỏi phép; TDM bị cấm.

Phiếu W40 của bản đầu có 3/5 bài là Elsevier (JACC, CGH, J Hepatol). Chưa bài nào được đọc hay nạp.

**Sửa.**
- `DIEU_KHOAN_NXB`: chỉ ghi điều ĐÃ ĐỌC (nguồn + ngày + trích ≤ 15 từ + đường hợp lệ). Nhận diện NXB theo TIỀN TỐ DOI trước, miền sau.
- Phiếu: bài của NXB «cấm» ⇒ nhóm «BÁC SĨ ĐỌC TRỰC TIẾP», kể cả khi bài miễn phí. NXB chưa kiểm ⇒ cảnh báo trong phiếu.
- `--nap`: NXB cấm ⇒ từ chối. NXB chưa kiểm ⇒ hồ sơ phải khai `dieu_khoan` {url, doc_luc, ket_luan: cho_phep | giay_phep_cc};
  thiếu, hoặc `cam` ⇒ từ chối.
- Quy trình thêm bước 2a/2b: Claude đọc trang ĐIỀU KHOẢN của NXB, không phải bài, trước khi mở bài.
- Giác quan ⑦i nêu rõ «bài Elsevier/ADA: bác sĩ đọc trực tiếp».
- 11 test mới, 4 đột biến đều bị bắt. Fixture cũ dùng jacc.org làm ví dụ NXB thường, nay đổi sang ahajournals.org vì JACC là
  Elsevier. BH152 thêm hai kiểm.

**Chưa kiểm điều khoản:** NEJM, JAMA, BMJ, OUP, Wiley, Springer, AHA, SAGE, Cochrane… Trước khi đọc bài của các NXB này phải đọc điều
khoản (bước 2b). Bài OA mang giấy phép CC ⇒ khai `giay_phep_cc`.
