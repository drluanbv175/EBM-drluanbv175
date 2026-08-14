# PHA 1 — BẢNG KHOẢNG TRỐNG (đối chiếu prompt v2.0 với hiện trạng đo được 15/08/2026)

> Mỗi dòng: khoảng trống THẬT (đã xác minh, không suy đoán) · rủi ro · mức · nơi xử lý.
> Không liệt kê thứ đã có (xem `00-hien-trang.md` — ~80% biên chế đích đã tồn tại).

| # | Khoảng trống | Rủi ro | Mức | Xử lý ở |
|---|---|---|---|---|
| K1 | **VA CHẠM TÊN CỔNG**: prompt định nghĩa "G0–G6" MỚI, trong khi hệ đã có G0–G10 nghiên cứu (`gate_contract.py`, 6 cổng ký cứng, chữ ký HMAC) VÀ bộ cổng dashboard riêng. Du nhập "G2/G4 (cứng)" nghĩa MỚI sẽ tạo HAI hệ tên cổng — người đọc lệnh "qua G2 chưa?" không biết là cổng nào | Liêm chính — nhầm cổng đạo đức nghiên cứu với cổng truy nguyên dashboard; đúng lớp lỗi hai-sổ-đăng-ký (BH39) | **Cao** | Lô 0 — bác sĩ chốt: GIỮ tên hiện có, ánh xạ khái niệm prompt→cổng thật trong `quality/gates.md` (đề xuất ở `02`) |
| K2 | **SỰ THẬT LỊCH CHẠY ≠ KỲ VỌNG**: launchd 2 job `runs=0` (chưa từng nổ); 6 tác vụ nền prompt nêu **không tồn tại trên máy này** (scheduler trả rỗng). Cơ chế thật = hook SessionStart + `tu_khoi_dong` phóng-khi-quá-hạn | Vận hành — "hợp nhất 6 tác vụ chồng chéo" là hợp nhất thứ không chạy; kỳ vọng tự động sai chỗ | **Cao** | Lô 0 — bác sĩ xác nhận 6 tác vụ có ở claude.ai web không `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]`; lịch tối giản đề xuất ở `02` |
| K3 | **Không khoá ghi khi quét 2 máy**: `surveillance_scan`/`so_xac_minh_nguon` không có lock; OneDrive 2 máy + ghi sổ JSON cùng lúc = mất bản ghi (điều kiện dừng khẩn của chính prompt) | Vận hành/dữ liệu | **Cao** | Lô 1 |
| K4 | **Chưa đo ĐỘ TRỄ** — định nghĩa vận hành "mới nhất" (≤14ng guideline, ≤7ng an toàn thuốc) chưa có phép đo nào; hiện chỉ đo độ tươi GÓI và tuổi CHỦ ĐỀ | Không chứng minh được "mới nhất" bằng số | **Cao** | Lô 4 — `ops/metrics.py`: pubdate/ngày-vào-PubMed vs ngày vào sổ |
| K5 | `vn-guidelines/registry.json` **[KHÔNG TÌM THẤY]** — A8 không có sổ nguồn BYT/BHYT chính thức; lớp VN đang chạy bằng field `vn` + nhãn `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` (đúng luật cấm bịa, nhưng không tra được gì) | Lâm sàng — bản địa hoá mỏng | TB | Lô 3 — skeleton registry, KHÔNG bịa số quyết định BYT |
| K6 | **Máy trạng thái item chưa hình thức hoá**: prompt đòi `NEW→VERIFIED→APPRAISED→CANDIDATE→APPROVED→APPLIED`; hiện có tương đương NGẦM (sổ xác minh=VERIFIED · hàng chờ EBM_MASTER=CANDIDATE · bác sĩ duyệt=APPROVED · UNRESOLVED=verify FAIL) nhưng không có field `status` thống nhất, không cấm-bằng-máy chuyển thẳng APPROVED | Kiểm toán — trạng thái phải suy ra từ 3 chỗ | TB | Lô 2 — `contracts/` hình thức hoá TỪ schema đang chạy, KHÔNG migrate dữ liệu cũ |
| K7 | **Kênh `alerts/` chưa có**: retraction mới, guideline bị thay thế, cổng FAIL đang nằm trong stdout/báo cáo từng tool — chưa có `alerts/YYYY-MM-DD.md` gom một chỗ | Vận hành — tín hiệu khẩn trộn với tín hiệu thường | TB | Lô 1 |
| K8 | **Chưa có `last_run_cursor`**: quét theo cửa sổ `--days` — chạy dày thì trùng lặp công (dedup chặn được bản ghi trùng nhưng không chặn được công quét lại), chạy thưa thì hở khe giữa 2 cửa sổ | Vận hành/chi phí + nguy cơ HỞ KHE bỏ sót | TB | Lô 1 |
| K9 | **Gold set 8/20–30**: canary có 8 lỗi gài; thiếu các ca prompt yêu cầu: guideline bị thay thế · SR chất lượng thấp · RCT outcome-switching · guideline mâu thuẫn · ca cao tuổi đa thuốc | Bảo chứng — C1 phủ chưa đủ lớp lỗi | TB | Lô 4 |
| K10 | **AWaRe (kháng sinh) chưa tường minh** trong `drug_flags.json`/overlay | Lâm sàng (kháng sinh ngoại trú) | TB | Lô 3 |
| K11 | `--dry-run` thiếu ở hầu hết tool ghi file (`build_library`, `make_derivatives`, ledger) | Vận hành | Thấp | Lô 1 |
| K12 | A1 Curator chưa nuôi bằng **log câu hỏi thực tế** — watchlist sửa tay | Độ khớp thực hành | Thấp | Lô 5 |
| K13 | Trùng vai skill↔agent (`tham-dinh-chung-cu-grade-nnt` skill v1.0 vs agent `tham-dinh-grade-nnt` giàu hơn) — nguồn chân lý kép | Trôi doctrine | Thấp | Lô 5 — tuyên bố agent là chân lý, skill trỏ về |
| K14 | Kiểm "guideline **đã bị thay thế**" mới chạy THEO YÊU CẦU (`kiem_chung_cu_vuot_qua`), chưa vào nhịp quý trên toàn ledger như prompt đòi | "Đang dùng bản đã bị thay" = 0 chưa được canh定 kỳ | TB | Lô 4 |

## Xung đột prompt ↔ invariant/hiện trạng (ghi theo luật mục 1 & 10.4 — không tự nới)

1. **K1 ở trên là xung đột lớn nhất** — giải bằng ánh xạ, không đổi tên hệ cổng đang có chữ ký.
2. Prompt Phụ lục A gán `citation-management` làm A4 — thực tế A4 mạnh nhất đang là
   `so_xac_minh_nguon` + chuỗi 3 tầng (có cả ca PubMed/EuropePMC cùng trả `ok` mà vẫn bắt được
   rút bài). Đề xuất: giữ chuỗi 3 tầng làm A4, `citation-management` là worker phụ.
3. Prompt yêu cầu QUADAS-2 — doctrine hiện hành đã lên **QUADAS-3** (Ann Intern Med 2026,
   doi:10.7326/ANNALS-25-02104), QUADAS-2 chỉ để tương thích ngược. Giữ QUADAS-3.

*Cần bác sĩ kiểm chứng.*
