# Kiểm đồng bộ xuyên cổng — giả lập một đề tài qua từng cổng (15/11/2026)

> Bác sĩ giao 15/11/2026: «Phải đạt sự đồng bộ giữa các cổng, từ vấn đề nghiên cứu, câu hỏi, tổng quan tài liệu, mục
> tiêu, thiết kế, cỡ mẫu, chọn mẫu, biến, công cụ nghiên cứu và đề cương… kiểm tra lại sự hoàn thiện một cách chi tiết
> và trung thực nhất khi chạy giả lập hoàn thiện một đề tài với từng cổng.»
>
> Phạm vi đo: mã sống `origin/feat/r1-1-2-design-gap-remediation` @ 5fcf4310, worktree tách rời
> `~/.ebm-worktrees/kiem-dong-bo-cong-20261115`. Đề tài giả lập **ZZSIM-DONGBO-TUANTHU-THA-20261115**: «Tỷ lệ tuân thủ
> dùng thuốc hạ áp và các yếu tố liên quan ở người bệnh tăng huyết áp điều trị ngoại trú: nghiên cứu cắt ngang dùng bộ
> câu hỏi». Vai PI giả lập ghi quyết định vào `study_meta.json` của bản sao. Không đụng đề tài thật. Không ký bằng khoá
> thật. Không có dữ liệu bệnh nhân (20 dòng dữ liệu mô phỏng).
>
> Nhật ký thô: `~/.ebm-worktrees/kiem-dong-bo-cong-20261115/_kiem_dong_bo/`.

## 1. Kết luận

**Hệ CHƯA đồng bộ được chuỗi từ vấn đề nghiên cứu tới biến số, rồi tới SPSS/R.** Mỗi cổng tự kiểm tốt phần bên trong
của nó. Nhưng mối nối từ mục tiêu sang biến, từ biến sang công cụ, rồi sang từ điển dữ liệu và SAP **không có phép kiểm
máy nào**.

Mã G10 tự ghi rằng việc ánh xạ mục tiêu sang biến CRF *«không bao giờ tự động hoá được»*. Vì thế ma trận truy xuất chỉ
gắn nhãn «đối chiếu thủ công» cho từng mục tiêu (`run_g10_assemble.py`, ma trận mục tiêu–biến–công cụ).

**Vì sao các báo cáo trước ghi «hoàn thiện».** Giả lập lần 2 (14/11) dùng một bộ biến **do chính tệp test viết sẵn**
(`_BIEN` trong `test_gia_lap_rct_chi_tiet_tam.py`). Cũng tệp đó viết luôn tên biến vào SAP (`kiem_soat_t6`…). Tệp đó
còn thay mọi ô `[CẦN…]` bằng nhãn «GIẢ LẬP». Kết quả «Python = SPSS = R, 3.052/3.052 ô khớp» là đúng, nhưng nó chỉ
chứng minh **bên trong khớp với nhau**: dữ liệu ↔ từ điển ↔ `.sav` ↔ `.rds`. Nó không chứng minh **biến đúng với mục
tiêu**. Đây đúng là chỗ bác sĩ gặp lỗi khi nhập liệu SPSS/R.

## 2. Kết quả từng mắt xích (đo trên giả lập)

| # | Mắt xích | Hệ có tự mang sang cổng sau? | Có máy kiểm khớp? | Kết quả đo |
|---|---|---|---|---|
| 1 | Vấn đề → tổng quan tài liệu (G0) | Truy vấn PubMed tự dịch từ chủ đề tiếng Việt | **Không** kiểm truy vấn phủ khái niệm PICO | Từ điển dịch 84 mục **không có «tuân thủ»**. Chủ đề rút thành `hypertension treatment`. 86 bài duy nhất, chỉ **1** bài nói về tuân thủ. Hệ vẫn gắn nhãn chứng cứ «MẠNH», gợi ý thiết kế «thử nghiệm thực dụng», đếm «2.413 thử nghiệm đang tuyển». **8/8 tiêu chí máy G0 PASS**, PI chốt xong thì `PASS_G0_CONFIRMED`. |
| 2 | Câu hỏi/PICO (G0) → G1 | **Không.** A2 của G1 để «[CẦN BỔ SUNG]» cho quần thể, PICO, kết cục chính, công cụ đo, thời điểm. `g1_quality_gate` đọc `primary_outcome_measure` từ G1, không từ G0 | Một phần | PI phải gõ lại lần 2. |
| 3 | Kết cục chính G0 ↔ G1 ↔ đăng ký G2 | Đăng ký G2 (TRDS mục 19) lấy từ G0 | **Có** (`nhat_quan_xuyen_cong`) | Lệch diễn đạt cài cố ý («tuân thủ *dùng thuốc*» → «tuân thủ *điều trị*») ⇒ 🟠 bắt được. |
| 4 | Quần thể G0 ↔ G1 | Không | Có, nhưng **chỉ đo một chiều** | G1 bỏ «đang điều trị ≥3 tháng… tại phòng khám nội tim mạch» ⇒ vẫn **🟢 khớp** («độ bao hàm 1.00»). Mất tiêu chí chọn mà không bị báo. |
| 5 | Mục tiêu (G1) → biến | Không | **Không có** ở bất kỳ cổng nào | `g3/g4/g5/g6/g10_quality_gate.py` và `gate_contract.py` **không đọc** `_bo-bien-rieng.csv`, kể cả G3 là cổng mang tên «Cỡ mẫu & bộ biến số». |
| 6 | Thiết kế ↔ cỡ mẫu ↔ chọn mẫu (G1/G3) | Mã thiết kế và N truyền đúng | Có cho N/α/thiết kế | Thiết kế `cross_sectional` đúng. N = 482 khớp 3 nơi (p = 0,5 mặc định, chờ PI). **Không kiểm**: cỡ mẫu chỉ tính cho Mục tiêu 1, không xét đủ cho mô hình đa biến của Mục tiêu 2. Chọn mẫu «thuận tiện liên tiếp» trong khi công thức Cochran giả định chọn ngẫu nhiên, cũng không có cảnh báo. |
| 7 | G1 → SAP (G4) | **Không.** SAP nháp để «Tiêu chí nhận: [CẦN — từ đề cương]». Kết cục chính là ví dụ không liên quan («tỷ lệ nhập viện tim mạch trong 12 tháng»). «Biến độc lập: [CẦN]» | Chỉ kết cục chính và N | Lần thứ 3 PI/thống kê viên phải gõ lại. Không có kiểm tên biến trong SAP có trong từ điển hay không. |
| 8 | Biến → công cụ (bộ câu hỏi) | Không | **Không** | Câu «dùng bộ câu hỏi» không kích hoạt mô-đun công cụ (`prom_tool` chỉ bật khi *xây/kiểm định* thang đo). Không có phép kiểm «mỗi câu của công cụ có một biến», hay «điểm tổng có công thức». |
| 9 | Biến → từ điển G5 (**đường A: không có bộ biến riêng**) | G5 rơi về **bộ mẫu chung theo chuyên khoa**, nhận diện `generic`, 22 trường, chỉ in cảnh báo | Chỉ kiểm cấu trúc | Từ điển **không có** 8 câu tuân thủ, điểm tuân thủ, BHYT, số thuốc hạ áp, số lần dùng/ngày, tác dụng phụ, kiến thức, hỗ trợ gia đình (6/9 yếu tố Mục tiêu 2 mất). Có biến thừa: `ethnicity`, `bmi`, `heart_rate`, `htn` (ai cũng THA), `follow_time_months` cho nghiên cứu cắt ngang. «Kết cục chính» là ô chữ giữ chỗ `primary_outcome`. |
| 10 | Từ điển → mẫu nhập Excel → **SPSS `.sav`** → **R `.rds`** | Có, trung thành tuyệt đối | Chỉ kiểm khớp **bên trong** | `nhap_lieu_excel mau` dựng 7 trang theo bộ mẫu chung, không cảnh báo. `cau_noi_spss xuat-sav --ban-nhap`: **«✓ 400 ô khớp nguồn · từ điển .sav khớp kế hoạch»**. `cau_noi_r xuat-rds`: **«ba chiều từ điển ↔ .sav ↔ .rds ✓ khớp»**. Tất cả xanh trên một bộ biến sai, nhãn biến còn «[CẦN] Tên biến phơi nhiễm…». |
| 11 | Biến (**đường B: có bộ biến riêng nhưng lỗi**) | G5 nạp đúng 17 biến | Chỉ cấu trúc và PII | Cài 2 lỗi thường gặp: thiếu «số lần dùng thuốc/ngày» và «hỗ trợ gia đình» mà Mục tiêu 2 nêu; kết cục chính nhị phân khai kiểu `text`. **Không công cụ nào bắt được** (G3-T2 của hội đồng, `nap_bo_bien_rieng`, `nhat_quan_xuyen_cong`). Ngược lại, G3-T2 **báo nhầm** biến `bhyt` (có BHYT hay không) là «định danh trực tiếp». `_la_ten_bien_dinh_danh`: `bhyt`, `co_bhyt` ⇒ True; `cobhyt` ⇒ False. |
| 12 | Từ điển → G6 (phân tích) | `detect_variables_from_redcap` **đoán** vai trò biến theo từ khoá | Không đối chiếu SAP §5 | Trên bộ biến riêng (đường B): kết cục = `primary_outcome`, phơi nhiễm = `exposure`, thời gian = `follow_time`. Cả ba đều là biến dự phòng **không tồn tại** trong từ điển (biến thật là `tuan_thu`). Hiệp biến chỉ nhận `tuoi`, `gioi`. Cú pháp SPSS/R (`cu-phap`) nhận đặc tả từ G6 hoặc từ tham số người gõ, không từ SAP có cấu trúc. |
| 13 | Đề cương (G10) | StudySpec đọc G0/G1 (đã vá 06/10) | Ma trận truy xuất: **đối chiếu thủ công** | Khi CRF là bộ mẫu chung, ma trận nhận luôn biến giữ chỗ `` `primary_outcome` `` làm «kết cục chính». |
| 14 | Công cụ trong hồ sơ G2 ↔ từ điển G5 | Không | **Không** | G5 chỉ dựng từ điển **sau khi G4 đã ký**, tức là sau IRB và sau khoá SAP. Không có phép băm/đối chiếu phiếu nộp IRB với từ điển nhập liệu. C1a làm phần này bằng tay (`pha_cong_cu/bang_truy_xuat_cau_hoi.csv`). |

## 3. Đề tài thật C1a (soi CHỈ ĐỌC)

- `_bo-bien-rieng.csv` 71 biến ≡ `G5_REDCap_dictionary` 71 biến, 0 lệch thuộc tính.
- 58 mục của phiếu (`bang_truy_xuat_cau_hoi.csv`) đều có biến.
- Biến SAP nhắc tới đều có trong từ điển. Hai ngoại lệ là `chuyenkhoa` và `doituong_qd`, mà SAP đã ghi rõ là đã loại.
- C1a khớp ở mức tên biến **nhờ nhiều vòng làm tay** (pha công cụ, codebook bổ sung, quyết định bộ biến), **không phải
  nhờ hệ kiểm**.
- Còn treo: 12 biến phái sinh (`_bien-phai-sinh.csv`) có cột `nguoi_duyet` **trống**, tức công thức chưa được thống kê
  viên/PI duyệt (#253).
- Chỉ 21/71 biến có «Tên SPSS:». 50 biến còn lại vào SPSS bằng tên REDCap.
- Chưa chạy lại xuất SPSS/R của C1a trong lượt này.

## 4. Chưa đo trong lượt này (nói rõ, không suy diễn)

- Ký G2/G4 và khoá G5 bằng khoá giả: đã đo ở giả lập lần 2, không làm lại. Từ điển đường A dựng bằng **chính hàm**
  `run_g5_auto` gọi khi thiếu bộ biến riêng (`build_redcap_rows` + `generate_csv`). G5 thật từ chối chạy khi G4 chưa ký.
- G6 chạy phân tích thật, cú pháp SPSS/R chạy thật, G7–G10 của đề tài này: chưa, vì cần khoá dữ liệu.
- Workflow R10 đang chạy (việc A6 sửa `run_g6_auto` đọc biến phân nhóm/hiệp biến từ SAP cho RCT) có thể vá **một phần**
  mắt xích 12. «Giả lập lần 3» của workflow vẫn dùng bộ biến viết sẵn, nên **không được đọc** như bằng chứng đồng bộ
  xuyên cổng.

## 5. Đề xuất sửa (chờ bác sĩ chọn — là thay đổi luật cổng)

1. **Một nguồn sự thật cho khung đề tài.** A2 (G1), SAP (G4) và đề cương dựng sẵn từ G0 đã chốt: quần thể, kết cục
   chính, công cụ đo, thời điểm, tiêu chí chọn. PI sửa thì hệ hiện chênh lệch, thay vì phải gõ lại 3 lần.
2. **Ma trận mục tiêu–biến bắt buộc** `_ma-tran-muc-tieu-bien.csv`, do `bien-so-nghien-cuu` soạn ở G3: mục tiêu → biến
   → câu hỏi/công cụ → phân tích SAP §. Công cụ máy kiểm:
   - mỗi mục tiêu có ít nhất 1 biến;
   - mỗi yếu tố nêu trong mục tiêu và SAP §5 có biến trong từ điển;
   - kiểu biến kết cục khớp kiểu đã chốt ở G1 (nhị phân ⇒ radio/yesno, không `text`);
   - mỗi câu của công cụ có biến; điểm tổng/biến phái sinh có công thức và nguồn.

   Gắn vào G3, G4, G5, G10. Đề tài đã ký giữ nguyên trạng thái (luật mới không hạ cấp quyết định đã ký).
3. **G5 thôi rơi về bộ mẫu chung một cách im lặng.** Thiếu bộ biến riêng ⇒ DỪNG; bộ mẫu chỉ là gợi ý nháp có nhãn. Cầu
   nối SPSS/R chặn từ điển còn `[CẦN…]` hoặc có nguồn gốc bộ mẫu, và thêm phép kiểm **nội dung**: biến của ma trận/SAP
   có mặt trong `.sav`/`.rds`.
4. **G6 lấy vai trò biến từ ma trận/SAP, không đoán.** Biến dự phòng không tồn tại ⇒ lỗi, không chạy tiếp.
5. **G0 kiểm truy vấn phủ PICO.** Khái niệm kết cục/phơi nhiễm vắng trong truy vấn ⇒ cảnh báo và đòi PI xác nhận
   `query_en`. Bổ sung từ điển dịch (tuân thủ → adherence…).
6. **`nhat_quan_xuyen_cong` so quần thể hai chiều.** Mất tiêu chí ⇒ «cần xem».
7. **Sửa báo nhầm PII** cho biến «có BHYT» (`bhyt`, `co_bhyt`).
8. **Phiếu nộp IRB (G2) ↔ từ điển G5.** Băm và đối chiếu từng câu, như C1a đang làm tay.

Cần bác sĩ kiểm chứng.

## 6. Sau sửa — giả lập đầy đủ lần 3 (15/11/2026, mã PR y khoa #268 @ d5e588c4)

> Bác sĩ duyệt cả 8 đề xuất ở §5, rồi yêu cầu thêm: E5 thuộc tính từng biến · 11 thuộc tính Variable View ở SPSS và R ·
> khai báo biến theo định nghĩa · lưu biến ngày đúng kiểu. Sau đó bác sĩ giao «chạy giả lập một cách đầy đủ của một đề tài
> để có một đánh giá trung thực». Đo bằng hai lượt độc lập, không đụng đề tài thật, không ký bằng khoá thật:
>
> - **Nửa đầu, G0 → G5** — `tools/gia_lap_dinh_ky.py --truc-tuyen`, hai kịch bản (RCT nhị phân · cắt ngang mô tả):
>   - G0 tra PubMed và ClinicalTrials.gov thật;
>   - «PI giả lập» làm đúng việc của PI;
>   - đếm mọi lần máy phải can thiệp.
> - **Nửa sau, G2 → G7** — trong pytest, khoá GIẢ của conftest, trên bản sao Phần A của đề tài RCT 14/11:
>   - ký G2/G4/G5;
>   - sinh 218 ca mô phỏng;
>   - nhập kép qua Excel, có cài lỗi;
>   - làm sạch + khoá;
>   - G6 phân tích bằng Python, kiểm chéo bằng SPSS 31 và R 4.6.2 thật;
>   - G6.5 diễn giải, G7 viết.

### 6.1 Kết quả từng mắt xích (so §2)

| # | Mắt xích | Lần 1 (§2) | Lần 3 |
|---|---|---|---|
| 1 | Truy vấn G0 phủ PICO | Không kiểm; truy vấn lạc đề vẫn PASS | **G0-AUTO-08 bắt được** khái niệm vắng. Truy vấn máy tự dịch vẫn lạc đề, nên PI phải viết `query_en` (khiếm khuyết K4 còn, nay bị chặn chứ không trôi qua). Lượt đầu G0-AUTO-08 **báo thiếu oan** «SMS» — đã sửa (chữ viết tắt Latinh là thuật ngữ tìm kiếm). |
| 2 | PICO G0 → G1/SAP | PI gõ lại 3 lần | Kế thừa có nhãn nguồn; SAP điền sẵn từ ma trận. |
| 4 | Quần thể G0 ↔ G1 | Một chiều, mất tiêu chí vẫn 🟢 | Hai chiều (test). |
| 5 | Mục tiêu → biến | Không cổng nào đọc bộ biến | **G3-AUTO-19**: G3 PASS chỉ khi có bộ biến + ma trận ĐẠT. Lần đầu, canary kẹt ở đây (đúng luật) vì kịch bản thiếu bước G3-T2 — đã dạy. |
| 9–11 | Bộ biến → từ điển G5 | Rơi về bộ mẫu chung | G5 dừng nếu thiếu bộ biến; từ điển dựng từ bộ biến riêng; G5-AUTO-12/13; từ điển ≡ bộ biến ở **mọi thuộc tính**. |
| 10 | Từ điển → mẫu nhập → SPSS/R | «✓ khớp» trên bộ biến sai | Đề tài RCT 14 biến:<br>• khứ hồi **3.052/3.052 ô**;<br>• **14/14 biến đủ 11 thuộc tính** ở SPSS (đọc lại bằng SPSS 31) và R (đọc lại bằng R);<br>• `.sav` ↔ `.rds` khớp;<br>• kiểm chéo G6 «SPSS ✓ khớp · R ✓ khớp».<br>Khai báo theo định nghĩa: «khác, ghi rõ» → String/NONE; mã hoá có 0 số lẻ; Missing khai đủ; ngày lưu kiểu ngày. |
| 12 | G6 vai trò biến | Đoán biến không tồn tại | Lấy từ SAP/ma trận. Phân tích chính chạy được; R theo SAP cho RD 0,248 · RR 1,52 · OR 2,90 · RD (MI) 0,240. |
| 14 | Phiếu nộp HĐĐĐ ↔ từ điển | Không | G5-AUTO-11 (#266) + G5-AUTO-13, nay đọc CÙNG một phiếu `PHIEU_THU_THAP_SO_LIEU_<mã>.md`. |

Pytest đầu–cuối G0→G10 đạt 9/9, cho đủ 8 thiết kế. Canary trực tuyến (sau sửa): cả hai kịch bản dừng đúng ở G5, 0 crash.

### 6.2 Khoảng hở giả lập lần 3 TÌM THÊM

1. **Hai cách khai cho cùng một phiếu thu thập.**
   - G5-AUTO-11 (#266) đọc `PHIEU_THU_THAP_SO_LIEU_<mã>.md`.
   - G5-AUTO-13 đọc `gate_params.G2.phieu_nop_hoi_dong`.

   ⇒ **Đã sửa** (d5e588c4): G5-AUTO-13 đọc cả nguồn chuẩn của #266.
2. **«Nguồn người duyệt» của G5-AUTO-11 không ai sinh, không ai dạy.**
   - G5-AUTO-11 đòi bảng biến số trong đề cương nộp Hội đồng, hoặc `G3_BO_BIEN_SO_<mã>.md`.
   - Không agent hay công cụ G3 nào sinh hoặc dạy tệp này; G3-T2 chỉ xuất `_bo-bien-rieng.csv` + ma trận.
   - Đề tài mới đi đúng quy trình hiện hành sẽ **kẹt ở G5** (không ký được ⇒ G6 bị chặn). C1a không kẹt nhờ đề cương nộp làm tay.
   - Giả lập đi tiếp được khi PI giả lập tự soạn bảng biến số G3.
   - Hai phương án đã trình:
     - (a) G3-T2 thêm sản phẩm `G3_BO_BIEN_SO_<mã>.md` dạng người đọc, PI duyệt; dạy agent và thêm vào danh mục hội đồng;
     - (b) G5-AUTO-11 nhận bộ biến + ma trận đã qua G3 (dấu vân tay PI) làm nguồn người duyệt.

   ⇒ **Bác sĩ chọn (a) — đã làm** (PR y khoa nhánh `claude/thuoc-tinh-bien-dinh-nghia-20261115`):
     - `tools/bang_bien_g3.py` soạn bảng từ bộ biến máy, theo đúng khuôn bộ đọc của G5-AUTO-11. Bảng gồm: bảng trường «Tên biến | Nhãn | Loại | Giá trị hợp lệ …», biến phái sinh có định nghĩa đặt cạnh công thức, ma trận và mã thiếu. Mục «Điểm PI cần xem tay» do máy tự dò.
     - Bảng máy soạn **chỉ** là nguồn người duyệt khi PI ghi `gate_params.G3.bo_bien_so_duyet` gắn dấu nội dung (cùng cơ chế G3-HUMAN-06). Bản nháp chưa duyệt bị loại, vì máy so với bảng do chính nó soạn thì luôn ra «đồng bộ» giả (đo được trước khi sửa). Sửa bảng sau khi duyệt ⇒ xác nhận mất hiệu lực. Bảng người soạn (không dấu máy, như bảng btm 28/10) vẫn tính như #266.
     - MT-11 (chỉ cảnh báo) báo sớm ở G3. Bảng được thêm vào đầu ra G3-T2 của danh mục hội đồng; canary giả lập có bước soạn bảng + PI duyệt.
     - Dạy `bien-so-nghien-cuu`, `dieu-phoi-g3`, `quan-ly-du-lieu`, `dieu-phoi-g5`.
3. **N4 — pipeline không tự chạy lại G1** sau khi PI điền (mỗi kịch bản 1 lần can thiệp). Có từ trước; thuộc R10.
4. **K4 — bộ dịch chủ đề VI→EN của G0** vẫn làm rơi khái niệm chính. G0-AUTO-08 nay chặn được, nhưng PI vẫn phải tự viết `query_en`.
5. **G7 chưa dựng Kết quả từ G6**: còn 51 ô «[CẦN KẾT QUẢ THẬT]» dù đã có `G6_analysis_summary.json`. Đây là mục tiêu của R10.
6. **Lỗi trình bày có sẵn:**
   - `G1_A13b_RISK_REGISTER` dùng cỡ thân bài 11pt (chuẩn 13pt) — máy sửa được;
   - ký tự 🟠 không có trong font của docx G7.
7. **Khuôn `03_analysis.R`** do test «hoàn thiện» báo `object 'fit_rr' not found`. Kịch bản R theo SAP (`04`) chạy đúng. Cần soi xem lỗi nằm ở khuôn hay ở bước điền của test.

### 6.3 Kết luận trung thực

- **Đã nối được:** mục tiêu ↔ biến ↔ công cụ ↔ từ điển ↔ SAP ↔ SPSS/R, và **khai báo biến ở SPSS/R đủ, đúng, đồng bộ** (đo bằng phần mềm thật).
- **Đã nối sau lượt này:** nguồn người duyệt của bộ biến (§6.2 mục 2, bác sĩ chọn (a)). Đề tài mới vẫn phải có PI đọc và duyệt bảng trước G5 — đó là việc của người, máy không làm thay.
- Các mục còn lại (N4, K4, G7 Kết quả) là khiếm khuyết sẵn có thuộc lộ trình R10.

Cần bác sĩ kiểm chứng.
