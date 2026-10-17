# 17/10/2026 — Kho tóm tắt máy: bộ kiểm khuôn coi «soan»/«bo_qua» là trường lạ, mời phiên sau soạn đè quyết định

**Phát hiện:** khi đo lại kết nối EndNote (17/10), mỗi lượt `nap_endnote_chu_de.py --tom-tat-vi` in loạt
«⚠ kho tóm tắt máy: «PMID …» có trường lạ soan». Cùng lúc nó in «ℹ Trích dẫn tham khảo CHƯA có tóm tắt máy: 2 — cần một phiên
Claude soạn…» cho PMID 36036525 và 39190340.

**Số đo (kho thật `EBM-Dashboards/tom-tat-abstract-vi.json`, 165 mục, 17/10/2026):**
- `tom_tat_endnote_vi.py --kiem` (mã cũ): ✗ 164 lỗi khuôn · 2 mục rỗng.
- 164 mục mang trường `soan`, ghi nguồn soạn («Claude (máy) · 13/10/2026 · từ abstract …»).
- 2 mục chỉ có `bo_qua` + `soan`. Lý do ghi trong `bo_qua`: trường Abstract của bản ghi là GHI CHÚ tiếng Việt của bác sĩ, không
  phải abstract PubMed — giữ nguyên, không tóm tắt máy. Đây là quyết định có chủ ý ngày 13/10
  (`2026-10-13-endnote-nhan-manh-va-ngu-canh-buoc-8.md`).
- Lượt nạp chỉ in 8 dòng cảnh báo đầu rồi cắt IM LẶNG, nên không ai thấy con số 164.

**Nguyên nhân:**
1. TT-08 (15/10) thêm bộ kiểm khuôn `kiem_kho_tom_tat` chỉ nhận đúng 6 trường của `NHAN_TOM_TAT`. Kho thật đã mang `soan`/`bo_qua`
   từ 13/10 ⇒ mọi mục bị báo «trường lạ». Nhiễu này che mất lỗi khuôn thật.
2. Danh sách «chưa tóm tắt» tính mọi mục không có trường hợp lệ, kể cả mục `bo_qua` ⇒ công cụ mời phiên sau soạn trái với quyết định
   đã ghi.
   - Ngày 17/10 một phiên đã soạn sẵn tóm tắt cho hai PMID này. Chốt `assert k not in d["muc"]` trong chính script của phiên đó chặn
     lại, nên kho không đổi.
   - Ghi chú của bác sĩ KHÔNG bị xoá trong mọi trường hợp: công cụ luôn giữ nội dung cũ dưới dấu phân cách. Hơn nữa bước kiểm số
     sẽ chặn in, vì ghi chú không có con số. Rủi ro thật là làm trái quyết định `bo_qua`.
3. Hai skill (`cap-nhat-chung-cu-y-khoa`, `dark-analyst`) còn câu lỗi thời từ trước TT-08: «khoá định danh/trường sai bị bỏ qua IM
   LẶNG».

**Cách vá:**
- `tools/tom_tat_endnote_vi.py`:
  - `TRUONG_SIEU_DU_LIEU = ("soan", "bo_qua")` — hai trường hợp lệ nhưng không bao giờ in. Trường lạ KHÁC vẫn báo lỗi.
  - `bo_qua` rỗng ⇒ lỗi «cần lý do». `bo_qua` cùng trường tóm tắt ⇒ lỗi «mâu thuẫn».
  - `tom_tat_cho` không bao giờ in tóm tắt cho mục `bo_qua`.
  - `ghi_tom_tat` tách mục `bo_qua` sang `tham_khao_bo_qua`, không tính vào «chưa tóm tắt».
  - `--kiem` đếm mục bo_qua riêng; `--mau` mô tả hai trường.
- `tools/nap_endnote_chu_de.py`: in dòng «ℹ Cố ý KHÔNG tóm tắt máy (bo_qua) — KHÔNG soạn đè» và đếm phần cảnh báo bị cắt
  («… và N cảnh báo khác chưa in»).
- Hai skill: thay câu lỗi thời; dạy `"soan"`/`"bo_qua"` và luật không soạn đè.

**Kiểm hồi quy:**
- `tools/test_kho_tom_tat_soan_bo_qua_20261017.py` — 11 test.
- 12 phép đột biến đều đỏ đúng test rồi phục hồi xanh:
  - bỏ `soan` / `bo_qua` khỏi tập hợp lệ; nới khuôn `and→or`;
  - bỏ kiểm bo_qua rỗng / mâu thuẫn;
  - bỏ chặn in ở `tom_tat_cho`; không tách danh sách;
  - `--kiem` tính bo_qua là rỗng;
  - bỏ dòng đếm cảnh báo ẩn / dòng bo_qua;
  - `_about` không nhắc bo_qua; skill trả lại câu lỗi thời.
- Kho thật sau vá: ✓ 165 mục · 0 lỗi khuôn · 0 mục rỗng · 2 mục cố ý bỏ qua.
- Chạy khô toàn bộ dashboard (`--kho-toan-van` chỉ rõ): «sẽ ghi 0 · không đổi 877» — bản vá không đổi nội dung nào trong EndNote.

**Còn mở (không thuộc bản vá này):**
- PMID 28898390 (Cochrane CD006211.pub3, mục thêm 16/10 bởi phiên khác) viết «9 nước». Abstract gốc nhiều khả năng viết bằng chữ ⇒
  bị chặn in đúng luật. Viết lại là việc của phiên soạn hoặc bác sĩ.
- Chạy `--file … --tom-tat-vi --ap-dung` từ worktree/bản sao trần thì không thấy kho toàn văn ⇒ dòng «Toàn văn» của mọi bản ghi sẽ
  thành «chưa xét» (đo: «sẽ ghi 877»). Đã mở việc riêng.
