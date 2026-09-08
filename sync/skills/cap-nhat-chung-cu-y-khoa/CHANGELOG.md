# Changelog

## v1.48.5 — 2026-09-08 (bác sĩ báo: mỗi lần một kiểu, không đọc trực tiếp được trong chat)

**Nguyên nhân xác định qua đối chiếu lịch sử CHANGELOG:** v1.1.0 (2026-06-02) từng "Không bắt buộc
Dashboard... trong câu trả lời EBM thông thường" và có 2 template nhanh/chuyên sâu làm khung chat
CHÍNH. Từ v1.2.0 → v1.10.0, Web Dashboard trở thành "đầu ra bắt buộc" + "TỰ ĐỘNG chạy trọn dây
chuyền" mỗi lần gọi skill — nhưng KHÔNG chỗ nào nói rõ câu trả lời văn xuôi trong chat vẫn phải
viết ĐẦY ĐỦ dù có tạo file hay không (mục 5A cũ chỉ bắt buộc điều đó KHI "môi trường không tạo file
được" — một điều kiện gần như không bao giờ đúng trong Claude Code). Đồng thời "Chế độ chuyên sâu"
(mục 3) mô tả bằng LỜI VĂN không trích khung mục cụ thể, khác với khung 8 mục nội tuyến của mục 5
("Cấu trúc đầu ra mặc định") VÀ khác cả khung 11 mục của chính `templates/mau-cap-nhat-chuyen-sau.md`
— ba khung gần giống nhưng không giống hệt nhau cho cùng một khái niệm, không có luật nào nói dùng
khung nào — đúng nguyên nhân "mỗi lần một kiểu".

**Đã vá — không đổi nội dung 2 file template, chỉ nối dây rõ ràng:**
- Mục 3: thêm câu mở đầu bắt buộc — bất kể chế độ nào, bất kể có tạo Dashboard/bộ năm hay không,
  câu trả lời văn xuôi LUÔN viết đầy đủ trực tiếp trong chat trước; Dashboard/file là bổ sung.
- "Chế độ nhanh" trỏ đích danh `templates/mau-cap-nhat-nhanh.md` làm khung DUY NHẤT.
- "Chế độ chuyên sâu" trỏ đích danh `templates/mau-cap-nhat-chuyen-sau.md` làm khung DUY NHẤT
  (liệt kê đủ 11 mục nguyên văn ngay trong mục 3, không phải đoán/đọc file riêng), và nói rõ
  KHÔNG dùng khung 8 mục của mục 5 cho chế độ này.
- Mục 5: ghi chú khung 8 mục chỉ dành cho "Chế độ mặc định", trỏ hai template kia cho hai chế độ còn lại.
- Mục 1 + 5A "Mục đích": bỏ điều kiện "nếu môi trường không tạo file được" — nội dung EBM đầy đủ
  trong chat nay là mặc định KHÔNG điều kiện; Dashboard nói rõ là sản phẩm bổ sung, không phải nơi
  duy nhất chứa nội dung.

Chưa sửa (ngoài phạm vi vá lần này): 4 lần bump version không ghi changelog (v1.48.1→v1.48.4).

## v1.48.0 — 2026-08-15 (đề xuất #6 — bác sĩ duyệt «làm #6»)

**Làn ĐỐI CHIẾU OpenAlex** `tools/doi_chieu_openalex.py`: corpus lớp AnswerThis
(Crossref-nhanh, 250M+ công trình) bên cạnh PubMed-lane — dedup DOI/PMID với sổ+kho,
nhãn «⚡ chỉ-OpenAlex» cho bài chưa/không vào PubMed. Chạy thật: Suy tim cửa sổ 30
ngày → **+15 ứng viên ngoài mọi thứ hệ đã biết, 10/15 chỉ-OpenAlex**. SRC-007 active
trong sổ nguồn (probe + artifact mapping); lịch tuần thêm bước 1b. Rút bài theo DOI
trong làn ghi «chưa kiểm» trung thực (fail-closed) — nối tầng kiểm ở vòng sau.
Học breadth của AnswerThis, giữ cổng của mình: ứng viên vẫn dừng CANDIDATE.


## v1.47.0 — 2026-08-15

**Bước 0 định tuyến «nêu vấn đề là tự giải quyết»** — khe hở cuối: CLAUDE.md chỉ định
tuyến ca lâm sàng + đề tài nghiên cứu, tuyến CHỨNG CỨ chưa có dòng tường minh. Nay:
điểm khám (`tra_diem_kham`, <1s, chỉ thẻ đã duyệt) → chuỗi máy (`orchestrator --topic`)
→ ngoài phạm vi thì «chưa giám sát» + tín hiệu watchlist. Kèm 4 quyết định bác sĩ duyệt
cùng ngày: watchlist 44 chủ đề (+Dengue, token-AND GOLD/SoC — phrase-index PubMed không
có các cụm đó) · lịch tuần goi-duyet-tuan-ebm T7 07:07 · ledger v2 1193/1193 + alt_id ·
4 hội lõi URL xác minh sống qua trình duyệt.


## v1.46.0 — 2026-08-15 (vòng «tự động tốt nhất + trung thực»)

- **Bản đọc nhúng TUYÊN BỐ ĐỘ PHỦ** ở footer (sinh sống từ data/sources.json;
  sinh lỗi thì in rõ, không im lặng — I7).
- **Nhịp THÁNG tự động** — chủ sở hữu thứ tư `evidence_integrity_monthly.sh`
  (validate ledger · truy nguyên toàn sổ · sức khoẻ nguồn · eval) qua tu_khoi_dong;
  lượt nền đầu tự khai «CÓ BƯỚC LỖI» (bug shift nhãn) → vá → PASS.
- **Vá trung thực sources_health**: ping chỉ ghi `last_probe_at`; `last_success_at`
  SUY TỪ ARTIFACT thật (log weekly_safety · sổ xác minh · mtime RW) — ngày bịa bị
  tự sửa (**BH50**, mutation-tested). Eval N04 nhận đúng hợp đồng cả hai ngữ cảnh
  (offline→unknown_* · online→unresolved; cấm duy nhất là «ok»).


## v1.45.0 — 2026-08-15 (PHA 4 — độ phủ, đo bỏ sót, chống sai trích số)

- **Sổ đăng ký nguồn** `data/sources.json` (18 nguồn: 6 active đã thăm sống · 12
  not-covered CÓ khai known_gap) + `tools/sources_health.py` (nguồn hỏng >2 chu kỳ → báo).
- **Trạm tổ chức** `tools/giam_sat_to_chuc.py` (content-hash + so tiêu đề, đổi giao diện
  → im; guideline mới → bắt trong 1 chu kỳ — self-test). NẰM CHỜ bác sĩ duyệt egress/URL.
- **Làn nhập tay VN** `tools/add_vn_source.py` — TỪ CHỐI thiếu số hiệu/tệp gốc; verified_by_human.
- **Tầng toàn văn**: `appraisalCompleteness:'partial'` × `apply` → cổng CHẶN (fixture chứng minh).
- **Rút bài theo ĐỊNH DANH** `dinh_danh_da_rut()`: dashboard MỚI trích DOI đã-rút bị bắt
  ngay cả khi chưa từng qua vòng quét A4 (lỗ hổng tìm bằng fixture đối kháng — đã vá).
- **Chống sai trích số**: lớp so NHÃN quanh trị số (`kiem_so_lieu.py --self-test`: đổi HR→RR
  → bắt) + 7 trường checklist 9.1 vào schema; validator chặn apply thiếu outcome_role/source_location.
- **Đối chứng ngoài Q3**: BẮT 7/10; 3 bỏ sót (ADA SoC ch.9, GOLD 2026 ×2) — hồ sơ MISS +
  đề xuất sửa watchlist/egress ở `reports/de-xuat-thay-doi.md`. Ước lượng có thiên lệch,
  KHÔNG phải độ phủ.
- **Tuyên bố độ phủ tự sinh** `tools/tuyen_bo_do_phu.py` (tự kiểm chuỗi cấm P1).
- Doctrine G-1…G-5 chống thiên lệch cái mới (khối cuối SKILL).


## v1.44.0 — 2026-08-15

**LÔ 4/6 PHA 2 — quét theo MỘT chủ đề + chạy thật đầu-cuối:**
- `surveillance_scan.py` thêm `--topic <tên>` (khớp không dấu 2 chiều; không khớp
  → NỔ, không lặng lẽ quét cả kho). Sinh ra cho `ops/orchestrator.py` (một cửa
  A2→B5, log JSONL, `--resume`, khoá `ops/lock.py`).
- Chạy THẬT chủ đề «Bệnh thận mạn (CKD)» --online: A2 1/1 PASS (trễ trung vị
  2 ngày) → A3 (84 ứng viên/34 chủ đề) → A4 sổ vòng 1 → B2 PASS 0 lỗi → B5.
  Toàn tuyến ~135s, log `logs/20260815T064642-*.jsonl`.

## v1.43.0 — 2026-08-15

**LÔ 2 PHA 2 — mã thoát cổng tách «gói sai» khỏi «chưa xác minh được»:**
- `verify_dashboard.py` `report()` nay trả **0** sạch · **1** có ≥1 lỗi NỘI DUNG ·
  **2** khi TOÀN BỘ lỗi cứng là máy/mạng (DNS/timeout). Cả 1 lẫn 2 đều nonzero —
  cổng vẫn fail-closed, không caller nào bị mở nhầm; chỉ máy gọi phân biệt được
  «phải sửa gói» với «chạy lại khi mạng ổn / dùng sổ xác minh». Đo gốc 12/08:
  cùng dashboard `--online` 4 lần cho 13→3→6→1 lỗi vì DNS. Khoá bằng **BH48**
  (mutation-tested: xoá nhánh exit-2 → chốt đỏ).
- Hạ tầng cùng đợt (ngoài skill, ghi để truy vết): `tools/validate_ledger.py` +
  `tools/migrate_ledger.py` (dry-run, chờ bác sĩ) + `tools/provenance_ledger.py`
  (quét truy nguyên toàn sổ 1193 thẻ, offline-first, alert APPLY×đã-rút).

## v1.42.0 — 2026-08-15

**PHA 2 kế hoạch kiện toàn (bác sĩ duyệt LÔ 0)** — bộ quét thêm 3 mảnh an toàn vận hành:
- **Khoá `.quet.lock`** chống 2 máy/2 tiến trình cùng quét (OneDrive 2 máy) — tiến trình sau
  FAIL rõ, exit 3; khoá mồ côi tự hết hạn 30'. **BH47**.
- **Con trỏ tăng dần `.quet-cursor.json`** theo chủ đề: lượt sau hỏi `mindate = cursor−3ng`
  (lùi 3 ngày chống hở khe), `--days` vẫn là trần; `--since`/`--khong-cursor` để ghi đè.
- **Đo ĐỘ TRỄ ngay trong báo cáo** (khối `do_tre`): trung vị + số mục quá ngưỡng 14 ngày —
  định nghĩa vận hành của «mới nhất» lần đầu ĐO ĐƯỢC (lượt đầu: trung vị 3ng, 0 quá ngưỡng).
- **Kênh `alerts/YYYY-MM-DD.md`**: CHỈ sự kiện khẩn (ứng viên ĐÃ RÚT/EoC lọt lượt quét, cổng
  quét FAIL); không có sự kiện → không sinh file (chống nhờn màu đỏ, BH32).
Kèm hệ mới cùng đợt: cổng **E0–E6** (quality/gates.md — KHÔNG đụng G0–G10 nghiên cứu) ·
hợp đồng item + máy trạng thái (contracts/, validator `kiem_hop_dong_item.py`, **BH46**) ·
AWaRe vào drug_flags · registry VN skeleton · quét BỊ-VƯỢT-QUA theo QUÝ (`tu_khoi_dong` chủ
sở hữu thứ ba) · canary 8→10 ca.

## v1.41.0 — 2026-08-15

**Luồng THEO-YÊU-CẦU thừa hưởng bài học của luồng định kỳ.** Bác sĩ nêu vấn đề → Bước 2 nay
có "CÁCH TÌM CỤ THỂ — 4 lượt": (1) guideline/HTA gọi TÊN nguồn (hiệp hội chuyên khoa +
Cochrane/NICE/USPSTF/WHO + FDA/EMA/MHRA); (2) SR/MA rồi RCT lớn, tạp chí đỉnh gọi tên
(`"N Engl J Med"[ta]` · Lancet · JAMA · BMJ · Annals); (3) **lượt MỚI-VÀO-PUBMED bắt buộc** —
`edat`, KHÔNG lọc publication type, vì MEDLINE gán loại SAU khi bài vào PubMed (BH38);
(4) lượt VƯỢT-QUA cho mọi mục định `apply` (`kiem_chung_cu_vuot_qua.py`). Kèm kiểm rút bài
từng PMID qua chuỗi 3 tầng. Trước bản này, luồng theo-yêu-cầu KHÔNG thừa hưởng gì — tìm theo
lối cũ, dính lại đúng các lỗi luồng định kỳ đã vá.

## v1.40.0 — 2026-08-14

**Bộ lọc loại thiết kế đang vứt đi chính thứ mới nhất** — lỗi "mới nhất" lớn nhất tìm được.

- `search()` luôn AND thêm bộ lọc `[ptyp]`. Nhưng publication type do **MEDLINE gán TRONG
  LÚC lập chỉ mục**, việc xảy ra hàng tuần đến hàng tháng SAU khi bài vào PubMed. Lọc theo
  nó = chỉ thấy thứ đã đánh chỉ mục xong, tức thứ **không còn mới**.
- Đo 40 bài mới vào PubMed 45 ngày (suy tim): **30 bài chưa gán loại nào ngoài "Journal
  Article"**, trong đó có PMID 42552200 — *"Prevalence of orthostatic hypotension in heart
  failure: a systematic review"* — một tổng quan hệ thống bị vứt vì chưa kịp đánh chỉ mục.
- Đếm theo chủ đề (45 ngày, `edat`): CÓ lọc **1 · 8 · 0** — KHÔNG lọc **46 · 49 · 22**.
  CKD trả **0** trong khi thực có 22 bản ghi mới; "0 ứng viên" bị đọc thành "không có gì
  mới" — biến KHÔNG BIẾT thành SỰ THẬT.
- **Sửa:** thêm tầng thứ tư `moi_vao_pubmed` — đi bằng `edat` (ngày vào PubMed, đúng câu hỏi
  "có gì mới so với lần quét trước") và **không lọc** publication type. Ba tầng cũ giữ
  nguyên. Loại thiết kế nay dùng để **gắn nhãn và xếp hạng**, không dùng để loại bỏ.
  Bài chưa gán loại được ghi rõ *"⚡ mới vào PubMed — chưa gán loại thiết kế"*: đó là dấu
  hiệu MỚI, không phải khiếm khuyết. **BH38**.

**Đo trước/sau (43 chủ đề · 45 ngày):** 87 → **165 ứng viên** · chủ đề "0 ứng viên"
**22 → 7** · 48/165 là bài chưa gán loại (nhóm trước đây bị lọc sạch) · 165/165 đã kiểm rút
bài. 15 chủ đề từng báo "không có chứng cứ mới" thực ra **có** — gồm RA · viêm gan B · hen
phế quản · đột quỵ dự phòng thứ phát · lão khoa · GDMT nội trú.

## v1.39.0 — 2026-08-14

**Cổng NHẬN chứng cứ** — nâng đúng chỗ chứng cứ đi vào hệ, không đụng kho cũ.

- **Độ tin cậy gắn NGAY lúc nhận.** Đo trước đó trong `surveillance_scan.py`: **0 lần kiểm
  rút bài · 0 lần đọc loại thiết kế · 0 lần đối chiếu kho**. Ứng viên chỉ mang tiêu đề ·
  tạp chí · ngày · nhãn `authority` **suy từ tên tạp chí** — một bài đã bị rút vẫn có thể
  vào thẳng hàng ứng viên. Nay mỗi ứng viên mang `rut_bai` (chuỗi 3 tầng) · `pubtype` (loại
  thiết kế THẬT từ PubMed) · `da_co_trong_kho` · `chua_binh_duyet`, và nhãn **in ra** trong
  báo cáo. Không kiểm được ⇒ `chua_kiem`, không mặc định `ok`. **BH37**.
- **4 nguồn thẩm quyền được gọi TÊN:** Cochrane · NICE · USPSTF · WHO — trước đó watchlist
  không nhắc tên nguồn nào trong nhóm này. Tra qua chính PubMed, không cần API mới.
- **Đo sau khi nối** (43 chủ đề · 45 ngày): PASS · 87 ứng viên · 0 lỗi · **87/87 đã kiểm rút
  bài** (trước 0) · **87/87 có loại thiết kế** (trước 0) · 41 SR · 24 practice guideline ·
  12 meta-analysis · 26 RCT · 1 mục đã có trong kho được lọc.
- Chuỗi rút bài dùng lại **một instance** cho cả lượt quét — trước đó nạp lại chỉ mục 30.851
  dòng cho MỖI chủ đề (43 lần nạp thừa, đủ chậm để người ta tắt lịch nền).
- Vá `_nap()` của bộ chốt: không đăng ký `sys.modules` trước `exec_module` ⇒ mọi module có
  `@dataclass` nạp hỏng ⇒ chốt báo "BÀI HỌC TÁI PHÁT" giả.

⚠️ **Chưa làm có chủ ý:** preprint (medRxiv/bioRxiv) và ClinicalTrials.gov chưa nối vào
routine — thêm dòng tài liệu chưa bình duyệt khi nhãn độ tin cậy vừa mới có sẽ làm hỏng
chính mục tiêu.

## v1.38.0 — 2026-08-14

Năm việc của đề xuất "chứng cứ tốt nhất · mới nhất · tin cậy nhất".

- **#1 `gradeBy` — ai đã chấm mức này?** Đo: 530 item có `gradeLevel` khác `na`, **249
  (47%) không truy được về tổ chức nào**; 128 lấy MÔ TẢ THIẾT KẾ làm lý do; **56 mục tự
  khai "nguồn không cung cấp phân hạng" mà vẫn mang mức** — vi phạm chính DESIGN-SPEC §6.
  56 mục đó đã đưa về `na`. Thêm trường `gradeBy` + luật cổng (mức CẢNH BÁO) và công cụ
  `tools/kiem_phan_hang.py` để xử lý dần. **BH36**.
- **#2 Chứng cứ đã bị VƯỢT QUA** — `tools/kiem_chung_cu_vuot_qua.py`: với mỗi PMID đang
  `apply`, hỏi PubMed các tổng quan/gộp/guideline MỚI HƠN. Lần chạy đầu: **125/172 mục có
  chứng cứ tổng hợp mới hơn**, bắt được KDIGO 2026 và guideline đột quỵ 2026. Chỉ liệt kê
  để đọc — không phán chiều, không đổi `decision`.
- **#3 Tìm kiếm theo TẦNG** — watchlist có `queries` 3 tầng: guideline/đồng thuận → tổng
  quan/gộp → RCT lớn; bộ quét chạy đúng thứ tự đó và gắn nhãn `tang` cho ứng viên. Nhóm
  cảnh báo cơ quan quản lý cố ý KHÔNG áp thứ bậc (lọc theo publication type sẽ giết sạch
  kết quả đúng). Tương thích ngược: thiếu `queries` thì lùi về `query` cũ.
- **#4 Kiểm CON SỐ** — `tools/kiem_so_lieu.py` đối chiếu `effect{hr,lo,hi}` với tóm tắt
  bài (đọc được cả `0.72` · `0·72` · `0,72`). Ba mức, **cố ý không có mức "SAI"**: vắng
  mặt trong tóm tắt KHÔNG phải bằng chứng trích sai — nhiều bài chỉ để số ở toàn văn.
  Thử 25 mục `apply`: 24 khớp đủ.
- **#5 `provenanceUnknown`** — 44/62 gói chưa từng ghi nhận chiến lược tìm kiếm, rải đều
  06→08/2026 (không có mốc ngày để suy). Trước đây chúng sinh 10 lỗi cứng GIỐNG HỆT gói
  lẽ ra phải có mà cố tình bỏ ⇒ cổng không phân biệt **chưa khai** với **có vấn đề**
  (BH08). Nay gói khai thẳng `provenanceUnknown: true` + lý do → một CẢNH BÁO nói rõ gói
  không tái lập/kiểm toán được, thay cho 10 dòng đỏ. Miễn trừ **chỉ** bỏ phần hợp đồng
  nguồn; **mọi luật an toàn cấp item vẫn chạy** (**BH35** khoá điều này).

**Kết quả cổng: 15/62 → 51/62 gói PASS.** 11 gói còn lại đều vì đúng 26 mục `apply` trên
chứng cứ mà nguồn chưa từng phân hạng — chờ bác sĩ quyết (hạ `decision` hoặc neo vào một
tổ chức có chấm).

## v1.37.0 — 2026-08-14

- **Kiểm rút bài nay phủ cả DOI** (trước chỉ PMID). 540 DOI trong kho — gần nửa số định danh —
  chưa từng được kiểm rút bài lần nào, mà sổ vẫn xếp là "còn hiệu lực". Bị chạm vào thật:
  ITEM-05 của `ViemGanB_DieuTri` đổi từ PMID 30267080 (đã rút) sang DOI
  `10.1001/jamaoncol.2018.4070` — tra PubMed + Crossref xác nhận **cùng một bài** — nên cổng
  thôi cảnh báo trong khi rủi ro còn nguyên. Thêm tầng Crossref (`updated-by`, không cần khoá).
  **BH33**.
- Áp cho cả **DOI ghi dạng URL** (lý lẽ BH24); **không** áp cho URL thuần → tránh báo động giả.
  `correction`/`erratum` cố ý không tính là rút bài.
- Luật mới: *một định danh mang bảo đảm nào thì phải chịu đúng phép kiểm của bảo đảm đó, bất kể
  được ghi bằng kiểu gì.* Đổi kiểu ghi không được là đường thoát cổng.
- Cách sửa đúng cho *retract-and-replace*: đối chiếu số liệu với **bản đã thay** rồi trích đúng
  bản đó — không đổi sang định danh khác của chính bài đã rút, cũng không xoá mục.

## v1.36.0 — 2026-08-14

Vòng lặp kiểm tra–hoàn thiện (3 vòng). Ba lỗi cùng một họ: **con số không đo thứ nó tự nhận
là đang đo** — công cụ vẫn chạy, vẫn in kết quả trông hợp lệ, nên không chốt nào bắt được.

- **Cổng liêm chính nay CHẶN nguồn đã bị rút** (trước đó không kiểm). Đọc lại kết luận dương
  tính trong sổ xác minh qua `so_xac_minh_nguon.nguon_da_rut()`; sổ im lặng **không** thành
  tín hiệu "đã kiểm, sạch". Phát hiện thật: PMID 30267080 (JAMA Oncology, rút 2019,
  retract-and-replace) trong `ViemGanB_DieuTri` đi qua cổng sạch sẽ suốt. **BH31**.
- **Bản đọc mang 2 dải cảnh báo** ngay dưới đầu trang: đỏ "Nguồn đã bị rút", cam "Bản khác
  cùng chủ đề đang kết luận ngược". Phép dò mâu thuẫn đã có từ 12/08 nhưng chỉ nói ra khi gõ
  lệnh; tại phòng khám thứ được mở là bản đọc. Không đổi `decision` nào, không đoán bên nào đúng.
- **Sửa lỗi bỏ sót mâu thuẫn**: `tach_ten()` trả tên chủ đề ở vị trí ngày ⇒ 3 bản
  `SuyTim_TongHop` sập vào một khoá cache, cặp 04/08⟷05/08 hoá thành so bản 11/08 với chính nó.
  Khoá lại theo **đường dẫn** (ngày cũng va chạm: `RA_Than` và `RA_TimMach` đều 30/06). **BH30**.
- **Độ tươi đo theo TỪNG chủ đề**, không còn suy từ `max(ngày)` toàn kho. Đo được: gói mới nhất
  1 ngày tuổi trong khi 37/59 chủ đề quá 35 ngày, trung vị 45. Ngưỡng báo động riêng 120 ngày
  để chống nhờn cảnh báo. **BH32**.
- Độ phủ xác minh nguồn: **51% → 99%** (1154/1155), 0 mục chưa kiểm.

## v1.15.0 — 2026-08-13

- **Quét theo TÊN TẠP CHÍ, không chỉ theo chủ đề.** Watchlist cũ có 11 nhóm/45 từ khoá, tất cả
  theo chủ đề — một bài NEJM/Lancet quan trọng về chủ đề ngoài 45 từ khoá đó sẽ không bao giờ
  được tìm thấy. Thêm 2 nhóm/8 truy vấn PubMed: **"Tạp chí hàng đầu"** (NEJM · Lancet · JAMA ·
  BMJ · Annals of Internal Medicine, lọc theo `[ta]` + publication type đổi thực hành) và
  **"Tổng quan hệ thống & khuyến cáo"** (Cochrane · NICE · USPSTF). Watchlist: 13 nhóm/53 truy vấn.
  Cả 8 truy vấn đã kiểm chạy thật.
- **Vì sao KHÔNG dùng RSS cho các nguồn này:** đã kiểm 10 feed ứng viên ngày 13/08 — tất cả bị
  chặn (Lancet/Annals/Cochrane/NICE/CHEST 403; USPSTF/Circulation/Diabetes Care/Blood 404). Nhà
  xuất bản chặn truy cập tự động. Ghi vào `references/13-source-universe.md` để không ai "sửa"
  bằng cách thêm lại RSS.
- **Lọc nhiễu cảnh báo cơ quan quản lý.** Feed `fda_recalls` trả toàn bộ thu hồi của FDA (thực
  phẩm, thiết bị, mỹ phẩm, thức ăn thú cưng, thuốc) nhưng gắn nhãn "An toàn thuốc" cho CẢ FEED.
  Đo bản tin 13/08: 40 mục "cảnh báo an toàn thuốc" gồm 6 thực phẩm + 4 thiết bị; cảnh báo thật
  đáng đọc (domperidone — chống chỉ định mới ở u tuỷ thượng thận, MHRA) bị chôn giữa thu hồi
  salsa. Nay `phan_loai_canh_bao()` phân loại TỪNG MỤC theo đường dẫn rồi từ khoá, tách 25% nhiễu.
  Nguyên tắc: **không chắc thì giữ là THUỐC** — có phép thử chống bỏ sót cho domperidone,
  morphine, valsartan/NDMA, montelukast.

## v1.14.0 — 2026-08-12

- **Cổng nguồn `--strict-sources` nay CHẠY THẬT trong dây chuyền một lệnh.** Trước đây
  `DESIGN-SPEC.md` §6 đòi `--online --strict-sources` từ đầu, nhưng `xuat_goi_cap_nhat.py` chỉ chạy
  `--online`, nên nhóm luật mạnh nhất nằm im. Nay bước ①-bis chạy thêm `--strict-sources` và tách
  hai loại lỗi: lỗi AN TOÀN (`decision='apply'` trên chứng cứ yếu/không phân hạng) ⇒ CHẶN XUẤT, mã
  thoát 3; thiếu `DATA.standards` ⇒ chỉ cảnh báo (bản cũ ra đời trước khi có khối này; bịa hợp đồng
  nguồn cho một lần tìm kiếm đã xảy ra chính là bịa provenance).
- **Vá lỗi che 73 mục nguy hiểm.** `verify_dashboard.py` `return` NGAY khi thiếu `DATA.standards`,
  nên toàn bộ luật an toàn cấp item CHƯA TỪNG chạy trên 47 dashboard. Cổng báo đúng "1 lỗi cứng" và
  người đọc kết luận "chỉ thiếu siêu dữ liệu, nội dung không sai" — một ảo ảnh của return sớm. Sau
  khi bỏ return, đo lại 61 dashboard: **73 mục `apply` trên chứng cứ yếu/không phân hạng, trên 16
  dashboard** (trước chỉ thấy 4). Bài học ghi vào SKILL.md: đọc kết quả cổng phải hỏi "cổng đã chạy
  tới luật nào", không chỉ đếm số lỗi.
- Đồng bộ `tools/verify_dashboard.py` cho khớp `EBM-Dashboards/tools/` và `EBM_MASTER/skill_assets/`
  (topology 3 bản — trước đó bản vá chỉ nằm ở một nơi, nên skill chạy bản chưa vá).

## v1.12.5 — 2026-07-15

- **Siết cổng nguồn chứng cứ để giảm nhu cầu bác sĩ tự dò từng nguồn.** Thêm `--strict-sources` cho
  `tools/verify_dashboard.py`: bắt `DATA.standards`, ngày tìm kiếm/cập nhật còn mới, ≥2 nguồn tìm
  kiếm, thứ bậc nguồn, chuẩn báo cáo, công cụ thẩm định, `references[]`, và chặn `decision='apply'`
  nếu chứng cứ yếu/không phân hạng/chỉ dựa đồng thuận. Khi chạy `--online --strict-sources`, cảnh báo
  PMID lạc đề/sai năm hoặc DOI chưa xác minh được được nâng thành lỗi cứng.
- Evidence Workbench hiển thị rõ trạng thái "Xác minh tự động nguồn" và yêu cầu
  `verify_dashboard.py --online --strict-sources` PASS trước phát hành. Lưu ý: cổng này giảm việc dò
  nguồn thủ công, nhưng không thay bác sĩ duyệt áp dụng cho bệnh nhân thật.

## v1.12.3 — 2026-07-11

- **Sửa `drug_safety_scan.py` gán nhầm cảnh báo đặc hiệu tramadol cho opioid khác (audit đối kháng
  2026-07-10).** Vòng lặp in chỉ hiển thị tên thuốc CANONICAL (`drug`), không hiển thị bí danh THỰC SỰ
  khớp (`found`) — dashboard nhắc đến fentanyl/morphine/oxycodone/codeine bị báo là "⚑ tramadol" kèm
  cảnh báo hạ ngưỡng co giật & hạ natri/serotonin CHỈ đặc hiệu cho tramadol (cơ chế serotonergic kép),
  không áp dụng cho các opioid thuần mu-agonist khác.
  - `drug_flags.json`: tách entry "tramadol" (giữ cảnh báo đặc hiệu) khỏi entry mới "opioid (khác
    tramadol)" (codeine/morphine/oxycodone/fentanyl — chỉ giữ cảnh báo CHUNG nhóm opioid: té ngã/sảng/táo bón).
  - `drug_safety_scan.py`: in kèm bí danh thực khớp khi khác tên canonical, vd "opioid (khác tramadol)
    (khớp: fentanyl)".
  - Đồng bộ 4 bản (`sync/skills/cap-nhat-chung-cu-y-khoa`, `sync/skills/dark-analyst`,
    `EBM-Dashboards/tools+data`, `EBM_MASTER/skill_assets`) — md5 khớp tuyệt đối.

## v1.12.2 — 2026-07-11

- **Vá doc-drift (audit đối kháng 2026-07-10):** README.md "## Phiên bản" đứng yên ở v1.3.0 trong khi
  SKILL.md đã v1.12.1 — bỏ danh sách phiên bản tay, trỏ về CHANGELOG.md (một nguồn duy nhất); mục
  "Web Dashboard kèm theo" còn mô tả mô hình cũ Clinical Quick View → cập nhật đúng mẫu mặc định
  hiện hành "Evidence Workbench" + chuỗi tự động 5D/5E. SKILL.md §9 bổ sung `EBM_MASTER/tools/sync_all.py`
  và `EBM-Dashboards/tools/reskin_dashboards.py` (2 phụ thuộc ngoài thư mục skill, đã được §5D/§4 dẫn
  chiếu là bắt buộc nhưng chưa từng liệt kê trong tài nguyên kèm theo).
- Đồng bộ luôn `sync/skills/dark-analyst/tools/verify_dashboard.py` (lệch sha256 từ 2026-06-21, thiếu
  toàn bộ `--check-topic`) + bổ sung `check_topic_relevance.py` còn thiếu ở đó.

## v1.12.1 — 2026-07-05

- **Đồng bộ verifier lệch giữa bản chạy thật và bản phân phối skill.** Kiểm tính đồng bộ phát hiện `tools/verify_dashboard.py` bản RUNTIME (`EBM-Dashboards/tools/`, 2026-07-02) đã được nâng cấp thêm cờ opt-in `--check-topic` + module phụ `check_topic_relevance.py`, nhưng bản trong skill (`sync/skills/.../tools/`) và hub (`EBM_MASTER/skill_assets/`) vẫn là snapshot cũ 2026-06-21 → cùng một dashboard có thể qua cổng liêm chính này nhưng khác kết quả ở cổng kia.
  - Back-port bản mới về **cả 3 nơi** (skill/tools · skill_assets · runtime) → md5 khớp tuyệt đối; bổ sung `check_topic_relevance.py` vào skill + skill_assets (trước chỉ có ở runtime).
  - `--check-topic`: LLM chấm item có lạc chủ đề/chuyên khoa dashboard không (lấp khoảng trống cổng kỹ thuật — vd bài sản/nhi lọt vào dashboard Tim mạch, sự cố thật `TimMach_20260609`). CHỈ cảnh báo, không chặn cứng; thiếu `ANTHROPIC_API_KEY` → bỏ qua êm.
  - Cập nhật SKILL.md §5D(a) + §9 khai báo cờ mới và tool mới. py_compile PASS; audit tổng PASS.
  - Ghi nhận điểm mù: `tools/audit_ebm_system.py` chỉ so template HTML, CHƯA so khớp các bản `.py` tool giữa 3 nơi — drift này lọt qua "Template sync: PASS".

## v1.12.0 — 2026-06-10

- **Sửa mất cân đối bố cục dọc** (bác sĩ báo: dashboard hiện tại vẫn chưa cân đối). Nguyên nhân thật: khối **GRADE Evidence-to-Decision là băng LUÔN hiển thị, rất cao ở đầu trang** → ép bảng chứng cứ (nội dung chính) thành dải mỏng ở đáy. (grep markers PASS nhưng mắt thấy lệch → đã kiểm chứng bằng ảnh chụp thực tế.)
  - *Evidence Workbench:* chuyển GRADE EtD từ băng đầu trang → **một TAB "⚖ GRADE EtD"** ở khu giữa (chỉ hiện khi có `etd`). Bảng giờ chiếm phần lớn màn hình. Thêm trần chiều cao thẻ tóm tắt (`max-height:188px;overflow:auto`) chống dữ liệu dài làm phình băng Quick View.
  - *Dark Analyst:* bọc GRADE EtD trong `<details>` **thu gọn mặc định** (bấm để mở) → còn 1 dòng thay vì băng to.
- Đồng bộ 2 template (EW+DA) qua 4 bản skill; **ghép lại 11 dashboard đã xuất** trong `EBM-Dashboards/` (giữ nguyên `DATA`); dựng lại 2 zip.
- Verify trực quan (1440×900): bảng chứng cứ là khu vực chính, EtD truy cập qua tab/details. Mặc định vẫn **Evidence Workbench**.

## v1.11.0 — 2026-06-09

- **Bố cục Dashboard responsive (cân đối mọi bề ngang)** — khắc phục "phần dưới hẹp, khó xem" trên màn ~1000px.
  - *Evidence Workbench:* lưới `clamp()`+`minmax(0,1fr)` (cột giữa `min-width:0`); ≤1199px panel thẩm định thành **ngăn kéo (drawer)** trượt từ phải (nền mờ + nút ✕) → bảng dùng trọn bề ngang; ≤820px bộ lọc thành dải ngang + ẩn cột Forest; ≤540px dồn 1–2 cột. Thêm `select`→`openDrawer`/`closeDetail`.
  - *Dark Analyst:* KPI/EtD/Quick-View tự giãn cột theo breakpoint; ≤860px chi tiết bung DỌC (`exp-in` 1 cột).
- Đồng bộ CẢ HAI template (EW + DA) qua 4 bản: `sync/skills/{cap-nhat,dark-analyst}` + bản live; dựng lại zip.
- Đã ghép layout mới cho các dashboard EW đã xuất trong `EBM-Dashboards/` (giữ nguyên khối `DATA`).
- Mặc định vẫn là **Evidence Workbench**. Verify trực quan ở 1000/1280/1440px PASS.

## v1.10.0 — 2026-06-07

- **Đổi mẫu MẶC ĐỊNH về "Evidence Workbench"** (nền sáng) theo lựa chọn của bác sĩ; **Dark Analyst** (nền tối) chỉ dùng KHI bác sĩ yêu cầu.
- **Thêm khối GRADE Evidence-to-Decision (EtD) vào template Evidence Workbench** (light theme) — nay CẢ HAI mẫu đều có EtD (field `etd`); tách rõ hàng chứng cứ-từ-nguồn vs đánh giá-vận-hành. JS cân bằng, gate PASS.
- **TỰ ĐỘNG khi gọi skill:** mỗi lần skill được gọi → tự chạy trọn dây chuyền (dựng Dashboard EW → cổng liêm chính `--online` → an toàn thuốc nếu liên quan → thư viện → 3 phái sinh), không cần yêu cầu từng bước. Ghi trong SKILL.md 5A + CLAUDE.md.
- Cập nhật checklist, danh mục tài nguyên, DESIGN-SPEC; đồng bộ template (mockup + skill).

## v1.9.0 — 2026-06-07

- **Sản phẩm phái sinh TỰ ĐỘNG mỗi lần chạy:** `tools/make_derivatives.py` sinh tờ dặn người bệnh + dàn ý slide (faithful, giữ PMID/GRADE) + kịch bản TikTok vào `EBM-Dashboards/derivatives/`. Video TikTok thật để bác sĩ gọi skill `tao-video-tiktok` khi cần. (Đã test trên ca thần kinh ĐTĐ.)
- **GRADE Evidence-to-Decision (EtD) trong Dashboard Dark Analyst:** thêm field tùy chọn `etd` (vấn đề · lợi ích · tác hại · độ chắc chắn · giá trị · cân bằng · nguồn lực · công bằng · chấp nhận · khả thi → khuyến cáo + độ mạnh). Tách rõ **hàng chứng cứ (từ nguồn) vs hàng đánh giá vận hành**; tương thích ngược (không có `etd` thì không hiển thị). Đã thêm CSS + render + ví dụ thật; JS cân bằng; gate vẫn PASS.
- Cập nhật SKILL.md (5D), checklist, tài nguyên; đồng bộ template (mockup + skill + standalone).

## v1.8.0 — 2026-06-07

- **Mục 5E + 3 nâng cấp** (theo yêu cầu bác sĩ):
  - **#5 Lớp phủ an toàn thuốc:** `tools/drug_safety_scan.py` + `data/drug_flags.json` (cờ Beers 2023/STOPP-START v3 cô đọng, có nguồn, KHÔNG đầy đủ) → quét thuốc trong dashboard, sinh prompt rà soát đầy đủ bằng skill `nguoi-cao-tuoi-da-benh-da-thuoc`. Ref 09. (Đã test: bắt amitriptyline/gabapentin/opioid.)
  - **#6 Giám sát định kỳ (Track B):** `tools/surveillance_scan.py` + `EBM-Dashboards/watchlist.json` → quét PubMed tìm guideline/SR/meta/RCT mới theo chủ đề lõi, báo cáo ứng viên để thẩm định. Ref 10. (Đã test: trả về chứng cứ 2026 thật.)
  - **#7 Bản địa hóa BYT:** `EBM-Dashboards/vn-guidelines/registry.json` + README → đối chiếu quốc tế ↔ hướng dẫn Bộ Y tế (do bác sĩ cung cấp, không bịa số QĐ), nối `clinical-evidence-rag`. Ref 11.
- Cập nhật checklist (lớp phủ an toàn thuốc) và danh mục tài nguyên.

## v1.7.1 — 2026-06-07

- **Thư mục chung tích lũy `EBM-Dashboards/`** (mục 5D-d + CLAUDE.md): mọi dashboard xuất vào một thư mục duy nhất trong OneDrive (tự đồng bộ Mac↔Windows), kèm `evidence-library.html` + `library.json` + bản sao `tools/` + `README.md`. Quy trình mỗi cập nhật: lưu vào thư mục → `verify_dashboard.py --online` PASS → `build_library.py add` để tích lũy vào chỉ mục.

## v1.7.0 — 2026-06-07

- **Thêm mục 5D + bộ công cụ `tools/`** (3 nâng cấp workflow theo yêu cầu bác sĩ):
  - **Cổng kiểm liêm chính** `tools/verify_dashboard.py`: kiểm mọi item có PMID/DOI, `gradeLevel`/`decision` hợp lệ, có disclaimer, quét PII; `--online` **tự xác minh mỗi PMID phân giải đúng trên PubMed** (chống trích dẫn ảo). Đã test: PASS/FAIL/âm tính + online xác minh thật.
  - **Thư viện cập nhật** `tools/build_library.py`: gom mọi dashboard vào `library.json` + sinh `evidence-library.html` (chỉ mục có tìm/lọc, mở thẳng từng bản).
  - **Sản phẩm phái sinh**: `references/08-xuat-san-pham-phai-sinh.md` + mẫu `templates/phai-sinh-to-dan-nguoi-benh.md`, `templates/phai-sinh-kich-ban-tiktok.md` (tờ dặn người bệnh / slide / TikTok — giữ liêm chính, không liều cho người bệnh/TikTok, có disclaimer, không PII).
- Cập nhật checklist (chạy cổng liêm chính trước khi giao) và danh mục tài nguyên.

## v1.6.0 — 2026-06-07

- **Đổi mẫu Web Dashboard MẶC ĐỊNH sang "Dark Analyst"** (nền tối, dày dữ liệu) theo lựa chọn của bác sĩ; Evidence Workbench (nền sáng) trở thành mẫu THAY THẾ.
- **Sản phẩm hóa Dark Analyst thành template tham số hóa** `templates/web-dashboard-dark-analyst.html`: chrome (tiêu đề, PICO chips, KPI, băng Clinical Quick View, verdict, bộ lọc, ô tìm) **tự sinh từ `DATA`**; bảng có cột Quyết định; click bung 3 cột thẩm định; hỗ trợ mọi loại thiết kế & mức GRADE.
- **Hai mẫu DÙNG CHUNG một schema `DATA`** (meta/summary/items[]) → một khối dữ liệu chạy được cả hai. Dark Analyst thêm field tùy chọn `effectText` (hiệu số phi-tỷ-số) và `rob` (RoB 2, chỉ RCT); giữ `frame`/`frameLabels`.
- Cập nhật SKILL.md (mục 5A, checklist, danh mục tài nguyên), `CLAUDE.md`, `DESIGN-SPEC.md` và đóng gói lại.

## v1.5.0 — 2026-06-07

- **Thêm mục 5C "Tự chọn khung câu hỏi"**: skill tự nhận diện loại câu hỏi lâm sàng và chọn khung phù hợp — ngoài **PICO(T)(S)** còn **PECO** (tác hại), **PIRT/QUADAS-2** (chẩn đoán), **PROGRESS/PICOTS** (tiên lượng), **CoCoPop** (tần suất), **SPIDER** (định tính), **ECLIPSE** (dịch vụ), PICO+chi phí (kinh tế).
- Bổ sung **mô hình tổng hợp bổ trợ**: phân tầng nguồn 6S, cân lợi ích–tác hại NNT/NNH, GRADE Evidence-to-Decision (EtD), bảng Tóm tắt phát hiện (SoF), tam giác liêm chính.
- Thêm tài liệu `references/07-mo-hinh-cau-hoi-va-khung-thay-the.md` (bảng chọn khung + cách ánh xạ vào Evidence Workbench + ví dụ).
- **Nâng template Evidence Workbench** (tương thích ngược): hỗ trợ field tùy chọn `frame` (nhãn khung) và `frameLabels` để đổi tên 4 ô P/I/C/O cho khung không phải PICO; không đặt thì hiển thị như cũ.
- Cập nhật checklist (nhận diện & nêu rõ khung đã dùng) và danh mục tài nguyên.

## v1.4.0 — 2026-06-07

- **Đổi mô hình Web Dashboard mặc định sang "Evidence Workbench"** (bố cục 3 cột: bộ lọc · Quick View + bảng điểm chứng cứ · panel thẩm định) theo lựa chọn của bác sĩ.
- Thêm template mặc định `templates/web-dashboard-evidence-workbench.html` (chỉ cần thay khối `DATA`); giữ template một-cột cũ làm fallback.
- Ba lớp nội dung bắt buộc giữ nguyên, ánh xạ vào bố cục: Clinical Quick View = băng tóm tắt + tab mặc định; Evidence Detail View = cột phải; Safety/Limits/VN = các tab riêng.
- Cập nhật bảng màu mặc định (nền sáng, dày dữ liệu) + màu ngữ nghĩa theo Quyết định/GRADE/Thiết kế; bổ sung forest plot mini và xuất CSV/JSON.
- Cập nhật mục 5A, frontmatter, checklist, danh mục tài nguyên, `references/05-…md` và `quality/web-dashboard-acceptance-checklist.md`.

## v1.3.0 — 2026-06-06

- Bổ sung **chế độ PICO**: chuẩn hóa trình bày chứng cứ theo P–I–C–O cho câu hỏi về hiệu quả/an toàn của can thiệp, kèm khối PICO 5 dòng (PICO + chứng cứ tốt nhất + grading từ nguồn + kết luận).
- Thêm mục 5B trong SKILL.md và tài liệu `references/06-pico-va-trich-dan.md` với mẫu, ví dụ và quy tắc liêm chính (trích hiệu số đúng nguồn, không tự gán GRADE, nêu cả hai chiều khi chứng cứ không đồng nhất).
- Thêm **quy tắc ghi nguồn sạch**: ghi nguồn dạng văn bản (tác giả/tổ chức + năm + tạp chí) và Vancouver/NLM; tuyệt đối không chèn thẻ markup trích dẫn thô/mã kỹ thuật vào câu trả lời; bắt buộc rà soát trước khi gửi.
- Bổ sung mục checklist tương ứng và cập nhật danh mục tài nguyên.

## v1.2.0 — 2026-06-02

- Bắt buộc tạo Web Dashboard HTML độc lập cho mỗi cập nhật EBM theo vấn đề cụ thể khi môi trường hỗ trợ tạo file.
- Áp dụng kiến trúc 3 lớp: Clinical Quick View mặc định, Evidence Detail View, Safety/Limits/Vietnam.
- Thêm schema record `ITEM-xx` cục bộ; không đồng nghĩa với ID Dashboard Master.
- Thêm template HTML tương tác có tìm kiếm, lọc, panel chi tiết, xuất CSV và tab kiểm chứng thao tác.
- Giữ nguyên nguyên tắc: chỉ tích hợp Dashboard Master/CỔNG A-B khi bác sĩ yêu cầu rõ.


## v1.1.0 — 2026-06-02

- Định nghĩa lại phạm vi: cập nhật chứng cứ cho **vấn đề lâm sàng cụ thể khi bác sĩ yêu cầu**.
- Không bắt buộc Dashboard, Web Dashboard, CỔNG A/B hoặc mã quản trị trong câu trả lời EBM thông thường.
- Bổ sung 4 tài liệu reference nội bộ còn thiếu.
- Bổ sung hai template đầu ra: nhanh và chuyên sâu.
- Bổ sung checklist nghiệm thu chất lượng.
- Tách chế độ an toàn thuốc, antibiotic stewardship, thang điểm/công cụ và thẩm định nguồn.
