# 30/10/2026 — Trần 50 chủ đề giết lượt quét tuần; nâng trần suông sẽ đổi sang lỗi khoá (BH174)

**Mã:** BH174. **Phát hiện:** phiên cập nhật Sleep Psychiatry 30/10 tình cờ đo khi dùng watchlist tạm.

## Chuyện gì đã xảy ra

Tối 29/10 (tệp sửa 19:57) watchlist lên 53 chủ đề active, trong khi `load_watchlist()` chặn cứng trên 50. Trần này có từ
01/08 (`325ec70`), lý do duy nhất là chuỗi «cần thu hẹp để giảm nhiễu», không có số đo nào. Lượt W44 (29/10, 15:00 giờ VN,
`08:00+00:00` trong JSON) chạy 47 chủ đề nên chưa dính; lượt kế (thứ Hai 02/11, 18:30) sẽ chết.

## Đo hành vi trước khi sửa (hộp cát, 30/10)

| Đường chạy | Kết quả |
|---|---|
| `weekly_safety.sh` | KHÔNG dính: chạy `run.py live-update`, không đọc watchlist |
| Gói tuần `goi-duyet-tuan-ebm` bước 1 | rc=2, chỉ stderr, 0 tệp `alerts/`; `state/tuan.json` của W44 nằm nguyên cho bước 2 đọc |
| `surveillance_scan --topic` | chết dù chỉ quét 1 chủ đề (trần kiểm TRƯỚC bộ lọc `--topic`) |
| `ops/orchestrator.py --topic` | rc=64, chẩn đoán SAI «tên chủ đề không khớp watchlist?»; lỗi thật không có trong jsonl/phiếu |

Canary ESD07 và các công cụ đọc thẳng `watchlist.json` (`kiem_san_luong_giam_sat`, `doi_chieu_openalex`) không dính.

## Vì sao nâng trần, không gộp chủ đề

- **Nhiễu không nằm ở trần:** W44 có 363 ứng viên nhưng gói tuần chỉ trình ≤ 7 thẻ.
- **Tiền không tăng theo số chủ đề:** bậc thang Consensus/SerpApi có trần theo TUẦN ISO (2), không theo chủ đề.
- **Gộp không chữa gốc:** `kiem_phu_giam_sat` đo 5 chủ đề còn chờ khai báo; 73 chủ đề dashboard là trần trên nếu phủ 1:1.
- Thứ thật sự tăng theo số chủ đề là THỜI GIAN.

Trần mới `TRAN_CHU_DE_ACTIVE = 100` chỉ còn là rào chống watchlist bị sinh sai, và chỉ áp cho lượt quét toàn danh sách.
Quyết định `active` vẫn của bác sĩ; không có chủ đề nào bị tắt hay gộp.

## Hai lỗi nấp sau trần (nâng trần suông sẽ đẩy ra)

1. **Khoá hết hạn giữa lượt.** Đo 10 lượt W34–W44: W36/W37 29,8 phút với 47 chủ đề (38 giây/chủ đề), W44 25,1 phút. Hạn khoá
   30 phút ⇒ 53 chủ đề ở tốc độ đó ≈ 33,6 phút: tiến trình khác coi khoá của lượt còn sống là mồ côi, gỡ rồi quét chồng,
   ghi đè con trỏ/sổ dự phòng. Có 6 chủ đề mới chưa từng có con trỏ nên lượt kế còn quét trọn cửa sổ 90 ngày cho chúng.
2. **Bản runtime không nhận được bản vá.** `dong_bo_scanner_giam_sat.py --ap-dung` từ chối ghi đè khi bản đích có dòng không có
   trong nguồn — mà mọi bản vá SỬA/XOÁ dòng đều tạo ra đúng tình huống đó. Trước nay người vá chép tay. Lần này nghĩa là PR gộp
   xong, `EBM-Dashboards/tools/surveillance_scan.py` (bản thật sự chạy) vẫn trần 50, `tu_sua_chua` chỉ báo ⛔ mỗi phiên.

## Cách vá

- `kiem_tran_chu_de()` tách khỏi `load_watchlist()`: trần là của một LƯỢT, không phải của schema; `--topic` không dính.
- Vượt trần hoặc watchlist không nạp được ⇒ ghi `alerts/<ngày>.md` (chỉ cho watchlist thật, không cho `--watchlist` tệp tạm).
- `lam_moi_khoa()`: nhịp khoá trước mỗi chủ đề, chỉ đụng khoá của chính tiến trình, trong `_mutex_khoa`, ghi thưa ≥ 5 phút
  vì tệp khoá đi qua OneDrive. Lượt chết thì hết nhịp, khoá vẫn mồ côi sau 30 phút như cũ.
- `dong_bo_scanner_giam_sat.py` luật (c): bản đích trùng khít một phiên bản ĐÃ COMMIT của nguồn ⇒ chỉ tụt hậu ⇒ chép đè. Bản
  có dòng riêng thật vẫn giữ; không hỏi được git hoặc lệch CRLF ⇒ về luật thận trọng cũ.
- Chẩn đoán A2 của orchestrator nói đúng hai khả năng; SKILL gói tuần bước 1: lượt không chạy ⇒ không dựng thẻ từ tệp cũ.

## Kiểm hồi quy

- BH174 kiểm HÀNH VI qua `main()`, ngoại tuyến, 0,47 giây; gồm đo watchlist THẬT nên lần sau vượt trần là đỏ ngay ở chốt nền
  mỗi phiên, không phải chờ tới thứ Hai. CI không chạy bộ chốt ⇒ `tools/test_tran_watchlist_nhip_khoa_20261030.py` đưa BH174 vào pytest.
- Kiểm đột biến 16/16 đỏ đúng chỗ, phục hồi xanh, chạy trên bản sao trong hộp cát. Một đột biến ban đầu đỏ sai nhánh (lỗi phép
  thử: dùng số 50 nên dừng ở nhánh 53 chủ đề) đã sửa để chạm đúng nhánh `load_watchlist`.
- Chốt trọn bộ: 136/174, 0 tái phát, 38 ⚪ ngoài phạm vi bản sao trần. Hai mục BH83/BH91 đỏ lượt đầu là do mirror `.Codex/agents`
  cục bộ (không track) của worktree cũ 28 ngày; `master` sạch đối chứng 0 tái phát; sinh lại mirror là hết, không đổi diff.
- pytest 29 tệp liên quan: 347 đạt, 2 bỏ qua.
- Đầu–cuối với mạng thật, watchlist 53 mục thật, hộp cát không engine: `--topic «Hen phế quản»` PASS rc=0 (17 ứng viên, 17 giây),
  `--topic «NICE — hướng dẫn mới»` PASS rc=0. Chưa chạy lượt toàn danh sách thật: lượt đó có con trỏ và tiêu hạn mức.

## Giới hạn và việc còn lại

- Bản runtime chỉ nhận vá sau khi PR gộp, cây chính kéo về và `tu_sua_chua` hoặc `python3 tools/dong_bo_scanner_giam_sat.py --ap-dung` chạy.
  Chép trước khi gộp sẽ lệch ESD02 và pre-commit chặn mọi commit ở cây chính.
- CLAUDE.md còn 13 ký tự ngân sách (59.987/60.000) nên không thêm luật; câu «phải chép sang» ở §6.4 nay do luật (c) tự lo.
- Lỗi RIÊNG, chưa vá: thẻ `[MeSH Major Topic]` chưa có bản dịch Europe PMC ⇒ khi NCBI lỗi, 20/53 chủ đề FAIL cứng thay vì suy
  giảm. W42 có đúng 20 FAIL vì lỗi này, W43 có 1, và lượt thử 30/10 gặp lại một lần. Cần việc riêng.

Cần bác sĩ kiểm chứng.
