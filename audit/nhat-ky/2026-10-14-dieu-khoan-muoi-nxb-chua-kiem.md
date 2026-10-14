# 14/10/2026 — Mười NXB «chưa kiểm điều khoản» chặn phiên uỷ quyền Chrome: đọc điều khoản, thêm vào DIEU_KHOAN_NXB

Tiếp nối BH158/BH159 (phiên uỷ quyền lưu bản sao, 04/10) và uỷ quyền THƯỜNG TRỰC 04/10/2026 (doctrine
`_CONNECTOR-CHUNG-CU.md` §2septies mục 8).

## Đo được
- `tools/phien_uy_quyen_chrome.py --kiem` từ chối mọi bài của NXB vắng `DIEU_KHOAN_NXB`: «NXB của bài (chưa kiểm điều khoản)
  KHÔNG thuộc phạm vi phiên». Hàng chờ toàn văn có bài của 10 NXB như vậy (số bài theo bác sĩ báo): Taylor & Francis 14 ·
  Thieme 2 · ASH 2 · Karger 1 · Bioscientifica 1 · American Psychiatric Association 1 · ERS 1 · Minerva Medica 1 ·
  COPD Foundation 1 · PCR/EuroIntervention 1.
- Crossref `/prefixes` (đọc trên Chrome 14/10/2026): 10.1080 + 10.3109 Informa UK Limited · 10.1055 Georg Thieme Verlag KG ·
  10.1182 American Society of Hematology · 10.1159 S. Karger AG · 10.1530 Bioscientifica · 10.1176 American Psychiatric
  Association Publishing · 10.1183 European Respiratory Society · 10.23736 Edizioni Minerva Medica · 10.15326 COPD Foundation ·
  10.4244 Europa Digital & Publishing.
- DOI `10.1530/EJE-16-0657` phân giải sang `academic.oup.com/ejendo/…` (European Journal of Endocrinology chuyển sang OUP từ
  01/01/2023) ⇒ bài EJE thuộc điều khoản OUP (đã «cấm» trong bảng), không phải Bioscientifica.
- Bash bị hook chặn gọi mạng ra ngoài ⇒ mọi trang đọc bằng Claude in Chrome. tandfonline.com, ashpublications.org, karger.com,
  journals.bioscientifica.com, psychiatryonline.org, minervamedica.it hiện ô Cloudflare «Verify you are human» — Claude KHÔNG
  bấm; các tab qua được lớp kiểm trên Chrome của bác sĩ rồi mới đọc. Thieme Connect treo ở trang chờ chống bot; chân trang
  của nó chỉ trỏ Imprint + Privacy ⇒ đọc Imprint trên thieme.com.

## Điều khoản đã đọc (14/10/2026) — kết luận
| NXB (khoá bảng) | Trang | Kết luận |
|---|---|---|
| Taylor & Francis (Informa UK) | tandfonline.com/terms-and-conditions | cấm RÕ đưa nội dung vào công cụ AI/LLM; dùng AI Tool để TDM cũng cấm |
| Edizioni Minerva Medica | minervamedica.it/en/sales-terms.php | bảo lưu RÕ quyền TDM + huấn luyện AI; cấm tải/lưu khi chưa có văn bản |
| American Society of Hematology (Blood) | hematology.org/about/terms-of-service + dòng bản quyền bài Blood 2025 | dòng bản quyền bảo lưu RÕ TDM/huấn luyện AI («Published by Elsevier Inc.»); ToS chỉ dùng cá nhân |
| Thieme (Georg Thieme Verlag) | thieme.com Imprint | cấm phát triển/huấn luyện AI; im lặng về công cụ AI đọc ⇒ không rõ |
| Karger | karger.com terms-of-use (11/2021) + AI Principles | quyền AI chỉ cho thuê bao TỔ CHỨC HỌC THUẬT ⇒ với tài khoản bác sĩ không rõ |
| Bioscientifica | journals.bioscientifica.com/pages/terms | thuê bao: dùng cá nhân phi thương mại, không có điều AI ⇒ không rõ; tạp chí OA theo CC từng bài |
| American Psychiatric Association (PsychiatryOnline) | psychiatryonline.org/termsofuse | cấm huấn luyện/kiểm định AI; im lặng về công cụ đọc ⇒ không rõ |
| European Respiratory Society | publications.ersnet.org/tdm (29/05/2026) | TDM học thuật phải báo trước; cấm dùng cho mô hình AI ⇒ không rõ |
| COPD Foundation | copdfoundation.org Disclaimer + trang nộp bài JCOPDF | đọc miễn phí nhưng KHÔNG CC, giữ bản quyền; không có điều AI ⇒ không rõ |
| Europa Group (PCR · EuroIntervention) | eurointervention.pcronline.com/pages/legal-notice | cấm sao chép, cấm scraping; không có điều AI ⇒ không rõ |

Kết luận là cách đọc của agent, không phải ý kiến pháp lý (doctrine §2septies mục 6).

## Vá
- `tools/doc_toan_van_co_nguoi.py`: 10 mục «cam» mới theo khuôn (nguon · doc_luc · trich ≤ 15 từ · loai_nguon · ngoai_le ·
  duong_hop_le); khoá OUP thêm tiền tố `10.1530/eje-` (đứng TRƯỚC Bioscientifica nên EJE chỉ-có-DOI vẫn ra OUP).
- **NXB «không rõ» ghi `ket_luan: "cam"`, KHÔNG ghi một giá trị `khong_ro` riêng:** `kiem_ho_so` chỉ đòi khai điều khoản khi
  NXB VẮNG bảng; NXB có trong bảng mà không «cam» thì được cho qua không cần khai ⇒ `khong_ro` sẽ là lỗ hở fail-open. Test cũ
  `test_bang_chi_co_muc_cam_va_cau_trich_toi_da_15_tu` đã khoá điều này; test mới tái hiện lỗ hở để giải thích.
- Doctrine §2septies mục 1 thêm «Đợt đọc 14/10/2026» (đủ tên + tiền tố DOI cho `lech_doctrine`); mục 4 bỏ Karger/T&F/
  Bioscientifica/CMAJ khỏi danh sách ví dụ «chưa kiểm».
- Fixture `tools/test_doc_toan_van_co_nguoi_20261002.py` dùng T&F và Karger làm ví dụ «NXB chưa kiểm» ⇒ 19 test đỏ sau khi hai
  NXB vào bảng. Theo §0.8 sửa FIXTURE (không nới assertion): đổi sang NXB GIẢ (tiền tố `10.99999/`, miền `.invalid`) để không
  bao giờ vào bảng; ca cần nhãn «Cloudflare» gắn tạm số đo cho miền giả bằng `monkeypatch`.

## Kiểm hồi quy
- `tools/test_dieu_khoan_nxb_dot_20261014.py` (42 ca): DOI thật trong hàng chờ + URL trang bài ⇒ đúng khoá; EJE ⇒ OUP kể cả
  URL miền cũ; trường đủ; doctrine khớp và bắt được khi mất tiền tố/tên; đi trọn đường thật tới `--kiem` của phiên (chưa có
  uỷ quyền ⇒ vẫn từ chối; có ⇒ nhận).
- Đột biến: bỏ `10.1530/eje-` khỏi OUP ⇒ 4 ca đỏ; bỏ miền `tandfonline.com` ⇒ 1 ca đỏ; phục hồi ⇒ 42/42 xanh. Phép đột biến
  tên COPD ban đầu KHÔNG đỏ vì tên xuất hiện hai lần trong mục — lỗi của phép thử, đã sửa (xoá mọi lần xuất hiện).
- 10 tệp test điều khoản/phiên/gom toàn văn: 260 xanh. `chot_hoi_quy_bai_hoc.py` trọn bộ: 🟢 (BH150/152/158/159/160/161 ✓;
  38 mục ⚪ vì worktree thiếu cây dữ liệu ngoài git). enforce guardrails: 0 tệp đổi; sync Codex `--check` PASS (64 agent).

## Còn treo
- Ghi uỷ quyền `--ghi-uy-quyen` cho 10 khoá mới, căn cứ câu thường trực 04/10/2026 — CHỈ SAU KHI PR được bác sĩ gộp.
- Reproduction (10.1530/REP-) chuyển OUP từ 2026 theo trang thư viện Bioscientifica — CHƯA đo DOI REP phân giải về đâu; hiện
  vẫn mang khoá Bioscientifica (cùng «cấm»).
- Bài OA mang CC (Endocrine Connections, European Thyroid Journal, ERJ Open Research…) bị chặn theo tiền tố như Springer/BMJ:
  đi đường OA (PMC/Unpaywall) theo giấy phép của bài, hoặc làn trình duyệt qua uỷ quyền.
