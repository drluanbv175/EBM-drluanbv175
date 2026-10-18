# 18/10/2026 — EndNote: bước ⑧ nhập lại bản ghi bác sĩ đã bỏ vào thùng rác

**Phát hiện (bác sĩ, 18/10/2026):** lệnh
`python3 tools/xuat_goi_cap_nhat.py EBM-Dashboards/WebDashboard_EBM_VanDeCuThe_ViemGanB_DieuTri_20260716.html --online`
chạy bước ⑧ `tools/nap_endnote_chu_de.py` và báo «24 trích dẫn · đã có trong thư viện 23 · nhập mới 1».

- Bản ghi nhập mới (recNum 7327) là DOI 10.1001/jamaoncol.2018.4070 — Choi, «Risk of Hepatocellular Carcinoma in Patients
  Treated With Entecavir vs Tenofovir for Chronic Hepatitis B».
- Bác sĩ đã CHỦ Ý bỏ bản ghi này vào thùng rác EndNote và dặn không nhập lại.

**Đo (18/10/2026, CHỈ ĐỌC, trên bản chép nhất quán của `sdb.eni` thư viện thật):**
- Bảng `refs`: 1956 bản ghi ở thư viện, 2 bản trong thùng rác (`trash_state` = 1).
- Cả hai bản trong thùng rác (recNum 7249, 7324) đều là DOI trên; 7327 lúc đó đang ở thư viện ⇒ sự cố đã lặp ít nhất HAI lần.
- Trường «Accession Number» của cả ba bản rỗng: dashboard chỉ ghi DOI, metadata lấy từ Crossref.
- Sau đó bác sĩ tự chuyển 7327 vào thùng rác (đo lại cùng ngày: 7249, 7324, 7327 đều `trash_state` = 1).

**Nguyên nhân:**
- `nap_chu_de` coi «chưa có» = không có bản ghi khớp qua `find` của EndNote.
- `find` không trả bản ghi trong thùng rác ⇒ bài bác sĩ đã bỏ trông như bài mới ⇒ nhập lại ở MỖI lượt bộ năm.
- Từ điển AppleScript của EndNote 2025 (`EndNote.sdef`) không có lệnh nào cho thùng rác; công cụ cũng không có chỗ nào để
  bác sĩ khai «đừng nạp bài này».

**Cách vá (`tools/nap_endnote_chu_de.py`, `tools/tom_tat_endnote_vi.py`):**
- **Danh sách loại trừ của bác sĩ:** khoá `bo_qua` trong `~/.ebm-endnote.json`, mỗi mục {doi|pmid, ly_do, ngay}.
  - Định danh trong danh sách: KHÔNG nhập, KHÔNG đăng vào nhóm, KHÔNG gắn PDF, KHÔNG ghi khối tóm tắt. Bản ghi khác không
    bị ảnh hưởng.
  - Xét theo định danh của dashboard (trước khi tra metadata), rồi xét LẠI theo định danh của metadata (dashboard chỉ ghi
    PMID mà bác sĩ loại theo DOI, hoặc ngược lại).
  - Bản ghi bị loại mà còn ở thư viện chỉ được BÁO kèm recNum; công cụ không bao giờ xoá.
  - In «⊘ bỏ qua theo danh sách loại trừ của bác sĩ: <định danh> — «lý do» (ngày)».
  - `bo_qua` sai khuôn (không phải danh sách, thiếu định danh/lý do/ngày, DOI/PMID gõ sai) = cấu hình HỎNG, đọc qua đúng
    `doc_cau_hinh`/`ly_do_cau_hinh_hong` ⇒ không nhập gì, có báo. Bộ năm (`--im-khi-chua-cau-hinh`) in ⚪ kèm lý do.
  - `--xuat-xml` (máy không phải Mac) cũng áp danh sách; cấu hình hỏng ⇒ không ghi tệp nhập.
  - `ghi_cau_hinh` giữ `bo_qua` cả khi đổi thư viện (quyết định về bài báo, không về thư viện).
- **Lệnh khai:** `--loai-tru <DOI|PMID> --ly-do "<…>"` — chạy khô mặc định; `--ap-dung` chép tệp cũ sang
  `.sao-luu-<ngày giờ>` rồi mới ghi; định danh đã có ⇒ không ghi; tệp hỏng/vắng ⇒ từ chối. Agent chỉ ghi khi bác sĩ yêu cầu.
- **Thùng rác:** `doc_thung_rac()` đọc `<thư viện>.Data/sdb/sdb.eni` ở chế độ `mode=ro` (cùng cách `sao_luu_thu_vien`),
  lấy `accession_number`/`electronic_resource_number` của bản ghi `trash_state <> 0`.
  - Trích dẫn chưa có bản sống mà nằm trong thùng rác ⇒ không nhập lại, in «⊘ Đang nằm trong THÙNG RÁC EndNote».
  - Còn một bản sống ⇒ bản sống là của bác sĩ, xử lý như cũ.
  - Không đọc được (thiếu tệp, lược đồ khác) ⇒ ⚪ «Chưa đo được thùng rác», KHÔNG coi là thùng rác rỗng; chỉ đo khi có bài mới.
  - Không bao giờ ghi `sdb.eni`, không dùng `close document`.
- **Bước tóm tắt:** bài bị loại / chỉ còn trong thùng rác không vào danh sách «Chưa có bản ghi (nạp chủ đề trước)» nữa —
  danh sách đó mời nhập lại chính bài bác sĩ đã bỏ.

**Kiểm hồi quy:**
- `tools/test_endnote_loai_tru_thung_rac_20261018.py` — 33 test ngoại tuyến (EndNote giả, `sdb.eni` sqlite giả trong
  tmp_path, đường dẫn có dấu cách/dấu tiếng Việt/«#»); test đọc thùng rác kiểm băm tệp trước/sau (không ghi).
- 15 phép đột biến đều đỏ đúng test rồi phục hồi xanh:
  - bỏ lọc loại trừ trước metadata; bỏ xét lại theo metadata;
  - bỏ lọc thùng rác trước/sau metadata;
  - khuôn `bo_qua` luôn coi là đúng; bước tóm tắt không bỏ qua;
  - `--loai-tru` không sao lưu; chạy khô vẫn ghi;
  - «không đo được thùng rác» coi là rỗng; đọc cả bản ghi không ở thùng rác;
  - `ghi_cau_hinh` làm mất `bo_qua`; thùng rác chặn cả bản đang sống (tóm tắt);
  - `--xuat-xml` bỏ lọc trước/sau metadata;
  - `main` nhập dù không đọc được danh sách (nhánh phòng thủ: tệp hỏng giữa hai lần đọc).
- Bộ test EndNote/tóm tắt cũ: 180 test vẫn xanh.
- Đo thật (chạy khô, dashboard Viêm gan B, thư viện thật đang mở):
  - cấu hình thật chưa có `bo_qua`: «24 trích dẫn · bỏ qua 1 · đã có 23 · sẽ nhập mới 0» + «⊘ Đang nằm trong THÙNG RÁC
    EndNote — không nhập lại: DOI 10.1001/jamaoncol.2018.4070»;
  - bản chép cấu hình có `bo_qua` (scratchpad, không ghi tệp thật): «⊘ bỏ qua theo danh sách loại trừ của bác sĩ: DOI …».

**Giới hạn:** `~/.ebm-endnote.json` là tệp RIÊNG MÁY (ngoài OneDrive) — danh sách loại trừ không tự sang máy khác. Bản ghi
khớp theo PMID trong thư viện mà bác sĩ loại theo DOI (và ngược lại) chỉ được nhận ra khi bài cần nhập mới (lúc đó mới tra
metadata).

**Việc của bác sĩ:** muốn chặn hẳn kể cả sau khi dọn thùng rác thì tự chạy (hoặc dặn agent chạy)
`python3 tools/nap_endnote_chu_de.py --loai-tru 10.1001/jamaoncol.2018.4070 --ly-do "<lý do>" --ap-dung`.
