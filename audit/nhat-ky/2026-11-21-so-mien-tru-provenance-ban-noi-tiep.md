# 21/11/2026 — Sổ miễn trừ: bản nối tiếp tháng 10–11 vẫn khai provenanceUnknown vì doctrine không nói gì về bản nối tiếp

**Bối cảnh.** Bác sĩ 21/11/2026: «Giải quyết vấn đề ở ý 2 và 3 nếu làm cho hệ thống tôi hoàn thiện thì thực hiện giúp
tôi». Ý 2 = đo tỷ lệ miễn trừ / vượt cổng theo thời gian (ý tưởng của plugin research-superpowers — KHÔNG cài). Ý 3
(khuôn kiểm wiki Obsidian) không làm: hệ chưa có kho Obsidian nào, công cụ không ai gọi thì không tồn tại.

**Số đo 21/11/2026** (`python3 tools/so_mien_tru.py`, nhóm lát cắt bằng `dang_ky_chu_de.tach_ten`, loại bản tin gộp bằng
`kiem_do_tuoi_chung_cu.la_khong_can`):
- 63/304 tệp dashboard mang `provenanceUnknown: true`; 18/114 bản HIỆN HÀNH; **9/102** lát cắt làm mới được (12 bản tin
  gộp không tính). Phiên trước đếm 19/115 → 11: lệch vì nhóm theo cả tên nhóm — `CongCuKeDon_ThuocTamThanKinh_20260620`
  đã bị `VanDeCuThe_ThuocTamThanKinh_20261021` thay theo đúng logic đăng ký chủ đề, `CapNhatTuan_NgoaiTru` là bản tin gộp
  (`khong_can: NgoaiTru`).
- Theo tháng dựng (ngày trong tên tệp, miễn trừ/tổng): 06/2026 29/32 · 07 10/15 · 08 4/19 · 09 1/5 · 10 8/40 · 11 11/193.
- Marker trong mã (đứng ngay sau `#`, có lý do): gốc `bh10-mien` 5 · `bimat-mien` 2; y khoa `bimat-mien` 13.

**Nguyên nhân gốc.** Không công cụ nào ghi cờ: grep `tools/`, `ops/`, `EBM-Dashboards/tools/`, repo y khoa — không nơi
nào sinh câu «bản sinh trước khi khối DATA.standards thành bắt buộc». Orchestrator không dựng dashboard (B1 là phiên làm
việc — docstring `ops/orchestrator.py`). Bản nối tiếp do PHIÊN Claude dựng bằng cách chép khối `DATA` của bản cũ, kể cả
`standards`. Skill `cap-nhat-chung-cu-y-khoa` chỉ dạy «dashboard MỚI phải luôn khai `DATA.standards`», không nói gì về
bản nối tiếp của một gói đã mang cờ ⇒ mỗi phiên tự chọn một cách. Hai lớp, phân được bằng máy:
- **Kế thừa có ghi lượt mới** — 4 bản hiện hành (NhiKhoa_SocPhanVe, RA_EULAR2024 05/11; CKM_TimThanChuyenHoa,
  VKDT_TongHop 14/11): giữ cờ vì mục kế thừa, lượt tìm của chính bản nằm ở `searchSources`/`currency`/`searchStrategy`.
  Đúng tinh thần «không hồi tố được, nhưng gói MỚI phải khai đủ». Cờ chỉ gỡ được khi mục kế thừa được tìm lại.
- **Chỉ có cờ** — 5 bản hiện hành: COPD_TimMachNoiTiet 25/10 (+ITEM-21), CAP_ATS2025 26/10 (+ITEM-06), LaoKhoa_Deprescribing
  26/10 (+ITEM-05/06) chép NGUYÊN câu cũ (sai với tệp dựng tháng 10) và không một dòng chiến lược cho mục mới;
  DaLieu_HS, SuyTim_NoiTiet 07/11 viết chiến lược tìm bằng văn xuôi trong `provenanceUnknownLyDo` — trường cổng không đọc
  như hợp đồng nguồn. Đây là lỗ thật của luật PRISMA-S.

**Mốc (b) 15/08/2026.** Luật «mọi gói MỚI phải khai đủ» chiến lược tìm theo PRISMA-S vào kho 14/08/2026: commit `8c469c1f`
(BH42, 21:53 — `audit/NHAT-KY-SU-CO.md`, đoạn «PRISMA-S gắn vào lỗ hổng provenance») và commit `18b878d0` (19:22, cổng thêm
miễn trừ `provenanceUnknown` kèm câu «gói mới BẮT BUỘC khai DATA.standards đầy đủ»). Tệp mang ngày 14/08 có thể dựng trước
giờ commit nên không tính. Sau mốc: 20 tệp vẫn khai miễn trừ (13 chỉ có cờ · 7 kế thừa có ghi).

**Vá (chỉ ĐO và BÁO; không sửa dashboard, không đổi cổng).**
- `tools/so_mien_tru.py`: (a) bản hiện hành mang cờ + n/N lát cắt khai hợp đồng nguồn; (b) tệp sau mốc còn miễn trừ, tách
  hai lớp và bản hiện hành; (c) marker trong tệp git track hai repo; (d) ảnh chụp `state/so-mien-tru.json` chỉ ghi khi số
  đổi (BH153), mỗi ngày một dòng, sổ hỏng không ghi đè. Không đo được ⇒ ⚪ mã 2. Đọc cờ bằng parser của chính cổng.
- `tools/tu_de_xuat_viec.py` giác quan ⑦r3: 🟠 bản hiện hành sau mốc CHỈ CÓ CỜ (lớp kế thừa không lên 🟠 — báo động không
  gỡ được dạy người đọc bỏ qua màu); 🟡 lát cắt mang cờ kèm `ops/orchestrator.py --topic "<lát cắt>" --online` cho lát cắt
  cũ nhất CÓ ánh xạ watchlist (kiểm bằng `chu_de_resolver`); ⓘ marker tăng so với ảnh chụp ≥ 7 ngày.
- `tools/do_dai_hoan_thien.py`: thước đo E-TAILAP «chủ đề có bản hiện hành khai hợp đồng nguồn» n/N.
- Skill `cap-nhat-chung-cu-y-khoa`: một đoạn dạy cách làm bản nối tiếp của gói mang cờ (lớp «kế thừa có ghi lượt mới»).

**Đề xuất cho bác sĩ (đã quyết — xem mục cuối).** «Chặn có sổ nợ» theo khuôn cổng nguồn chính thức 20/11: sổ nợ ghi các lát cắt
đang mang cờ (chỉ giảm, gia hạn cần lời bác sĩ); cổng chặn gói dựng sau ngày áp dụng khai `provenanceUnknown` mà KHÔNG có
`searchSources`/`currency` — mục kế thừa vẫn được miễn.

**Kiểm.** `tools/test_so_mien_tru_20261121.py` 29 test (kho dashboard giả, repo git tạm, ngoại tuyến); kiểm đột biến 13/13
bị bắt đúng chỗ (tự chế regex lát cắt, bỏ loại bản tin gộp, gộp hai lớp, lệch mốc, ghi ảnh chụp khi số không đổi, ghi đè
sổ hỏng, marker không cần `#`, bỏ ngưỡng 7 ngày, `main()` không truyền `dash=DASH`, 🟠 gộp lớp kế thừa, ghi ảnh chụp khi chưa
đo, Đài luôn «đạt», không đo được thành xanh) rồi phục hồi xanh.

**Bắt được trong lúc làm.** Bản đầu để giác quan tự dò EBM-Dashboards ⇒ `test_tu_de_xuat_gradeby_thong_tin` (gọi
`main()` với `DASH` trỏ thư mục tạm) vẫn đọc dữ liệu thật và GHI `state/so-mien-tru.json` thật. Vá: `main()` truyền
`dash=DASH` như mọi giác quan khác; tái hiện bằng gốc tạm có liên kết tới dashboard thật — trước vá có ghi, sau vá không.

**Bác sĩ quyết 21/11/2026: «chặn có sổ nợ».** Triển khai cùng PR:
- `verify_dashboard.kiem_provenance_goi_moi` (chạy dưới `--strict-sources`, hai bản git trùng byte): gói dựng từ 15/08/2026
  (ngày trong tên tệp; vắng thì `meta.updated`; vắng cả hai ⇒ coi là gói mới) mang cờ mà thiếu `searchSources` ≥ 1 hoặc
  `currency` có ngày ⇒ LỖI; tệp trong sổ nợ còn hạn ⇒ cảnh báo; quá hạn ⇒ lỗi; sổ hỏng ⇒ coi như vắng. Gói CŨ giữ miễn trừ
  chỉ-cảnh-báo. `phan_loai_provenance` là định nghĩa duy nhất — `so_mien_tru.py` gọi chính hàm này (BH20). Định nghĩa
  «có ghi lượt mới» chặt hơn bản đo đầu (cần CẢ nguồn lẫn ngày); trên kho thật số không đổi (13 chỉ có cờ · 7 kế thừa).
- `so_mien_tru.py --so-no [--tao|--gia-han]`: khuôn `doc_nguon_chinh_thuc.py so-no` (lập MỘT lần, nguyên văn lời bác sĩ
  ≥ 20 ký tự, hạn ≤ 90 ngày, chạy khô mặc định). Sổ thật đã lập: `EBM-Dashboards/no-provenance-goi-moi.json` — 13 tệp (5 bản
  hiện hành: COPD_TimMachNoiTiet, CAP_ATS2025, LaoKhoa_Deprescribing, DaLieu_HS, SuyTim_NoiTiet), hạn **21/12/2026** (30
  ngày, theo sổ nguồn chính thức 20/11 — bác sĩ không nêu hạn; gia hạn bằng `--gia-han`). Bản đã bị thay không cần trả nợ.
- Hòm việc: 🟠 cổng ĐANG CHẶN bản hiện hành · NỢ trong hạn (🟡, ≤ 7 ngày ⇒ 🟠) · 🟡 chủ đề còn mục kế thừa mang cờ — mỗi dòng
  một lệnh orchestrator.
- Dạy: skill `cap-nhat-chung-cu-y-khoa`, agent `thu-thu-tai-lieu` + `tong-quan-y-van` (PR cặp sang repo y khoa), câu §6.3 CLAUDE.md
  (viết lại gọn, 59997/60000 ký tự).
- Bản chạy ngoài git (`EBM-Dashboards/tools/`, `EBM_MASTER/skill_assets/verify_dashboard.py`) phải chép sau khi gộp.
- Kiểm: 19 test cổng + 37 test sổ miễn trừ; đột biến 24/24 (17 sổ miễn trừ/sổ nợ + 7 cổng: bỏ miễn trừ gói cũ, bỏ qua hạn, nguồn
  HOẶC ngày, `main()` không gọi luật, sổ hỏng thành miễn, tệp không ngày bỏ qua luật, lệch mốc); canary 12/12; bộ chốt bài
  học 146 ✓; thử đầu–cuối trên dashboard thật: bản nợ → cảnh báo kèm hạn, bản kế thừa → đạt, bản cũ → không đổi, bản mới
  giả lập 22/11 ngoài sổ → CHẶN.

