# 13/11/2026 — Gộp lịch nền nội dung thành MỘT tác vụ tháng; bỏ hai tác vụ giám sát guideline

## Lời bác sĩ (nguyên văn, 13/11/2026)
- «có 2 tác vụ cập nhật tháng hãy kiểm tra lại và gộp lại chỉ 1 tác vụ»
- «các tác vụ giám sát Guideline cũng không cần nữa»
- «Gói thu thập an toàn thuốc và duyệt chứng cứ hãy gộp vào một tác vụ tháng»

## Trước / sau
Trước có 7 tác vụ nội dung:
- `thu-thap-tuan-an-toan-thuoc` (thứ Hai 18:00);
- `goi-duyet-tuan-ebm` (thứ Hai 18:30);
- `giam-sat-9-tram-web-hoi-tuan` (thứ Hai 18:45);
- `cap-nhat-thang-ebm` (ngày 1, 18:30);
- `cap-nhat-thang-thu-muc-endnote` (ngày 5, vừa tạo ở #326);
- `giam-sat-acc-aha-quy` (quý).

Sau còn MỘT tác vụ `cap-nhat-thang-ebm` (ngày 1, 18:30). Các bước chạy tuần tự:
1. `sync_safety_check`
2. `weekly_safety.sh` — an toàn thuốc + quét nguồn thật
3. `monthly_update.sh`
4. `evidence_integrity_monthly.sh`
5. Gói duyệt chứng cứ: đọc và làm theo quy trình `sync/scheduled-tasks/goi-duyet-tuan-ebm/SKILL.md`
6. `cap_nhat_thang_thu_muc_endnote.py --quet --toi-da 3 --hoan-thien --ghi`
7. Báo cáo

Hai tác vụ giám sát guideline bị bỏ hẳn. Công cụ `tools/giam_sat_to_chuc.py` vẫn giữ để chạy tay.

Các tác vụ không phải nội dung giữ nguyên: `kiem-rut-bai-kho-thang`, `kiem-tra-hoan-thien-he-thong-thang`, `kiem-thang-diem-quy`.

## Đo trước khi gộp — chạy tháng có làm SÓT dữ liệu không?
- `weekly_safety.sh` → `run.py live-update`: lấy theo mốc lần chạy LIVE ok gần nhất (watermark, `app/services/run_state.py`), không theo cửa sổ cố định 7 ngày.
- Bản tin cảnh báo (`export_alert_digest(days=7)`): lọc theo lượt THẤY LẦN ĐẦU (`first_seen_run_id`), không theo ngày xuất bản. Mục thu trong lượt tháng vẫn vào bản tin của chính lượt đó.
- Bộ quét gói duyệt (`surveillance_scan.py`): con trỏ tăng dần.

⇒ Không sót, chỉ CHẬM: tín hiệu an toàn thuốc tới tay bác sĩ chậm tới khoảng một tháng. Đây là quyết định của bác sĩ.

## Chỗ phải đổi theo nhịp tháng
Không đổi thì sẽ báo động giả hoặc tắt nhắc giữa tháng:
- `tools/kiem_do_tuoi_chung_cu.py` `HAN_AN_TOAN_NGAY` 10 → 35.
- `tools/tu_de_xuat_viec.py`:
  - ⑦d (độ tươi log tuần, >10 ngày = mức 0) không gọi nữa; ⑦f canh kỳ tác vụ tháng.
  - Nhắc thẻ «chỉ tóm tắt»: ≤14 → ≤35 ngày.
  - Nhắc thẻ chưa quyết: ≤21 → ≤35 ngày.
- Quy trình gói duyệt:
  - `doi_chieu_openalex --ngay 10` → 35;
  - `do_tac_dong --ngay 7` → 31;
  - đặt cạnh chứng cứ: mỗi 2 tuần → mỗi lượt.
- `sync/quyen-lich-nen.json`:
  - khoá `goi-duyet-tuan-ebm` giữ làm khoá QUY TRÌNH, để chốt BH173 vẫn đối chiếu lệnh trong tệp quy trình;
  - khoá `cap-nhat-thang-ebm` khai thêm 3 script bash.
- Tác vụ gọi bash nên phải khai CHỈ-MAC (chốt BH130).

## Còn treo / cần bác sĩ
- Sau khi gộp:
  - xoá 5 tác vụ lịch trong app;
  - chép SKILL mới sang bản chạy của `cap-nhat-thang-ebm` và `kiem-tra-hoan-thien-he-thong-thang`;
  - bác sĩ chạy `python3 tools/quyen_lich_nen.py --ap-dung` cho 9 quy tắc mới.
- `CLAUDE.md` §1(c) còn ghi «gói duyệt tuần tự nằm sẵn tối thứ Hai (tác vụ lịch `goi-duyet-tuan-ebm`)». Agent không sửa `CLAUDE.md`; bác sĩ quyết định có sửa dòng đó không.
