# 16 · Thiết kế kiểm chéo ngữ nghĩa cho mục `decision:'apply'` (25/09/2026) — [BÁC SĨ ĐÃ DUYỆT HƯỚNG 25/09/2026 — K3, K1, K4 đã thi công ở mức CẢNH BÁO; xem §7–§8]

> Đề xuất #7 trong đợt «đo lại nguồn chứng cứ» 24–25/09/2026. Tài liệu này là **thiết kế**, chưa có mã.
> Mọi ngưỡng/từ điển dưới đây là đề xuất của máy — cần bác sĩ duyệt trước khi thi công.

## 1. Khoảng trống cần đóng

Các cổng hiện có kiểm **hình thức** và **nguồn có thật** (PMID tồn tại, tiêu đề khớp, chưa bị rút, hiệu số
HR có trong tóm tắt — `tools/kiem_so_lieu.py`). Chúng **không kiểm nội dung có đúng không**:

| Loại sai | Ví dụ | Cổng hiện tại |
|---|---|---|
| Sai quần thể | Mục ghi «HFpEF» nhưng trích thử nghiệm chỉ HFrEF; ghi «eGFR ≥ 20» trong khi nguồn là ≥ 25 | Không bắt (`pico.P:'match'` là lời NGƯỜI SOẠN tự khai) |
| Rụng mệnh đề điều kiện | DATA ghi «nếu không có chống chỉ định», bản đọc/Word/tin chat mất vế này | Không bắt |
| Sai chiều khuyến cáo | `apply` trên nguồn nói «not recommended» / Class III | Không bắt (chỉ kiểm `gradeLevel`) |
| Sai con số ngoài HR | Cỡ mẫu, ngưỡng tuổi/eGFR/EF/HbA1c | Chỉ HR/CI được kiểm |

## 2. Bốn phép kiểm đề xuất (đều CHỈ BÁO, không đổi `decision`)

Cùng triết lý `kiem_so_lieu.py`: ba mức **✓ khớp · 🟠 cần đọc lại · ⚪ nguồn không nêu (chưa kiểm được)** —
cố ý KHÔNG có mức «SAI», vì vắng mặt trong tóm tắt không chứng minh trích sai (BH08).

- **K1 — Quần thể.** Trích từ `population` + `pico.P` các ngưỡng số (EF, eGFR, tuổi, HbA1c, BMI, LDL…)
  và nhãn quần thể; đối chiếu với tiêu đề + tóm tắt nguồn (PubMed efetch). Thêm bảng **cặp loại trừ nhau**
  (HFrEF↔HFpEF · típ 1↔típ 2 · người lớn↔trẻ em · thai kỳ↔ngoài thai kỳ · CKD lọc máu↔không lọc máu):
  mục mang một vế mà nguồn chỉ nêu vế kia ⇒ 🟠.
- **K2 — Con số mở rộng.** Mở rộng `kiem_so_lieu.py` sang ngưỡng của K1 và cỡ mẫu `n=` ghi trong mục.
- **K3 — Bảo toàn mệnh đề điều kiện (NGOẠI TUYẾN, rẻ nhất, giá trị ngay).** Trích từ `action`/`summary`/
  `dontDo` các cụm điều kiện («nếu…», «trừ khi…», «khi eGFR…», «ngoài thai kỳ», «không dùng khi…») rồi
  kiểm từng cụm có còn trong **bộ năm** (bản đọc, Word HTML) và bản tin chat. Không cần mạng.
- **K4 — Chiều khuyến cáo.** `apply` mà tóm tắt/tiêu đề nguồn có tín hiệu ngược chiều («not recommended»,
  «no benefit», «harm», «Class III», «should not») ⇒ 🟠 kèm câu nguyên văn để bác sĩ đọc.

## 3. Nối vào dây chuyền

- Công cụ mới `tools/kiem_cheo_ngu_nghia.py` (repo gốc), đọc khối `DATA`, chạy K1–K4, in bảng + JSON.
- Gọi ở bước ①-ter của `tools/xuat_goi_cap_nhat.py`, **mức CẢNH BÁO** (không đổi mã thoát) — in vào
  bản đọc như dải vàng «Cần đọc lại N mục» cạnh dải đỏ/cam hiện có.
- Chỉ chuyển sang CHẶN khi bác sĩ duyệt, sau khi đo tỉ lệ báo động giả trên bộ vàng (mục 4).
- Dạy agent cùng lúc (luật §6.4): `tham-dinh-dau-ra` thêm R1d; `trich-xuat-y-van` gọi K1/K2.

## 4. Cách đo trước khi tin (bắt buộc)

Bộ vàng ~20 mục `apply` thật lấy từ các dashboard hiện có, **bác sĩ gắn nhãn tay** (đúng quần thể/đúng
chiều/đủ điều kiện hay không). Chạy K1–K4, đo: số 🟠 trên mục bác sĩ nói «đúng» (báo động giả) và số mục
bác sĩ nói «sai» mà công cụ bỏ lọt. Báo động giả cao ⇒ giữ mức cảnh báo, không chặn (bức tường đỏ giả làm
người ta bỏ qua cả cảnh báo thật).

## 5. Giới hạn nói trước

- Chỉ đọc **tóm tắt** (toàn văn có bản quyền) ⇒ ⚪ sẽ nhiều; ⚪ ≠ sai.
- Khớp từ vựng không hiểu phủ định phức tạp và đồng nghĩa hiếm; K4 chỉ bắt tín hiệu ngược chiều rõ ràng.
- Không thay việc bác sĩ đọc nguồn gốc; mục tiêu là **chỉ ra mục đáng đọc lại**, không phán quyết.

## 6. Quyết định của bác sĩ (25/09/2026)

1. **Thi công K3 trước** (rồi mới tới K1).
2. **Mức CẢNH BÁO**; chỉ cân nhắc chuyển sang CHẶN sau khi đo tỉ lệ báo động giả trên bộ vàng và bác sĩ
   duyệt lại.
3. **Máy soạn ứng viên bộ vàng**, bác sĩ gắn nhãn. Máy không tự gắn nhãn.

## 7. Trạng thái thi công (25/09/2026)

- **K3 đã có:** `tools/kiem_cheo_ngu_nghia.py`, ngoại tuyến. Nối vào bước **④-bis** của
  `tools/xuat_goi_cap_nhat.py`. Không đổi mã thoát, không chặn xuất. Có 5 test
  (`tools/test_kiem_cheo_ngu_nghia_20260925.py`), cả 5 phép đột biến đều đỏ đúng chỗ.
- **Chạy thử trên template Evidence Workbench cùng bản đọc sinh thật: 1 ✓, 1 🟠.** Cụm «khi xây phác đồ khoa»
  (action của ITEM-02) không có trong bản đọc. Lý do: bản đọc không in `action` của từng mục, và cụm này là bối
  cảnh sử dụng chứ không phải điều kiện lâm sàng. Đây là loại **báo động giả** mà bộ vàng phải đo trước khi tính
  chuyện chặn.
- **Ứng viên bộ vàng:** chạy `python3 tools/kiem_cheo_ngu_nghia.py --ung-vien-bo-vang` trên máy có
  `EBM-Dashboards/`. Công cụ ghi `quality/eval/kiem-cheo-ngu-nghia/bo-vang.cho-duyet.json`: 20 mục `apply`, chia
  đều giữa các dashboard, mỗi mục có `nhan_bac_si` = null. Công cụ không bao giờ ghi đè tệp đã có nhãn. Trên Cloud
  chưa soạn được vì `EBM-Dashboards/` nằm ngoài git.
- **Chưa làm (lúc đó):** K1, K2, K4. Nhắc R1d cho `tham-dinh-dau-ra` để lại tới khi có số đo bộ vàng. Hiện K3 mới chỉ cảnh
  báo, chưa phải luật cổng.

## 8. Thi công K1 · K4 (+ K2 rút gọn) — 25/09/2026, phiên trên máy Mac

Theo quyết định §6.1 («K3 trước, rồi tới K1»), mức CẢNH BÁO. K4 dùng chung đường tải tóm tắt với K1 nên làm cùng lượt.

- **Mã:** `tools/kiem_cheo_ngu_nghia.py --nguon` (một dashboard) · `--toan-kho` (cả kho, JSON vào `logs/`) · nối vào
  bước **④-bis** của `tools/xuat_goi_cap_nhat.py` khi chạy `--online`. Không đổi mã thoát của bộ năm, không chặn xuất.
- **Tải nguồn:** PubMed efetch XML theo lô 150 PMID; PMID còn thiếu lùi sang Europe PMC. NCBI trả trang HTML ⇒ lỗi
  của lô đó. Không tải được ⇒ ⚪ và mã 2 — **đã thấy chạy thật** lúc mạng máy mất (18:31 ngày 25/09): cả hai nguồn lỗi
  bắt tay SSL, công cụ trả mã 2, không in xanh.
- **K1a — cặp loại trừ nhau** (5 cặp ở §2). 🟠 chỉ khi nguồn không nêu vế của mục mà nêu vế kia ở **tiêu đề** hoặc
  ở **≥ 2 câu phần phương pháp**; nhắc một lần ⇒ ⚪ «thoáng qua» (guideline hay nhắc nhóm đặc biệt). Câu nêu tiêu
  chuẩn loại trừ («… were excluded») không tính là quần thể. Cụm phủ định/dạng thứ ba bị che trước khi dò
  («ngoài thai kỳ», «non-pregnant», «non-dialysis», «mildly reduced EF»).
- **K1b — ngưỡng số** (EF, eGFR, tuổi, HbA1c, BMI, LDL-C, NT-proBNP, HBV DNA, CrCl). Số phải **dính mỏ neo**
  («EF ≤ 40%», «≥ 65 tuổi», «aged 65 years or older»); «trung bình/trung vị» tách khỏi ngưỡng. 🟠 chỉ khi **mâu
  thuẫn hai chiều**: mục có số tóm tắt không có, **và** phần phương pháp của tóm tắt có số mục không có. Số ở phần
  kết quả/kết luận chỉ dùng để xác nhận. Toàn văn OA đã gom chỉ được nâng ⚪ → ✓, không bao giờ tạo 🟠.
- **K2 rút gọn — cỡ mẫu:** chỉ ✓/⚪ (tóm tắt nêu nhiều con số; vắng ≠ sai).
- **K4 — chiều khuyến cáo:** chỉ xét mục khuyến cáo LÀM (câu đầu của `action` không chứa «không dùng/ngừng/giảm
  liều/dừng…»). Câu hiệu quả phủ định («did not reduce», «no benefit»…) chỉ xét ở tiêu đề + mục kết luận (không
  cấu trúc: 2 câu cuối). Câu khuyến cáo phủ định («not recommended», «recommend against»…) xét ở mọi câu nhưng
  phải nhắc đúng can thiệp của mục (mỏ neo lấy từ `pico.I` + `title`, đã lọc chữ Việt viết hoa theo cấu trúc âm
  tiết và tên tổ chức/bệnh). Kèm câu nguyên văn của nguồn.
- **Bộ vàng:** ứng viên nay kèm `pico` để tính lại được từ chính tệp. `--lam-giau` lấy tối đa một nửa bộ vàng từ các
  mục K1/K4 báo 🟠 (đo được độ chính xác của cảnh báo); tệp **không** ghi mục nào thuộc nhóm nào, để gắn nhãn mù.
  `--do-bo-vang` tính báo động giả/bỏ lọt trên mục đã có nhãn; chưa có nhãn ⇒ mã 2 «chưa đo».
- **Kiểm:** 24 test ngoại tuyến (`tools/test_kiem_cheo_ngu_nghia_k1k4_20260925.py`) + 5 test K3 cũ đều xanh.
  **19/19 phép đột biến** đỏ đúng test đích rồi xanh lại (một phép lần đầu «sống sót» vì đánh nhầm nhánh — lọc
  câu loại trừ có ở hai chỗ; đã thêm ca cho cả hai nhánh).

**Đo trên toàn kho (72 dashboard · 345 mục `apply` · 163 PMID) — BẢN ĐẦU, trước khi siết luật:**
K1 128 ✓ · 18 🟠 · 120 ⚪ · 79 không áp; K4 241 ✓ · 10 🟠 · 84 ⚪ · 10 không áp. Máy tự soi 28 cảnh báo, thấy
phần lớn là **báo động giả có quy luật**, đã sửa trong bản cuối:

| Họ báo động giả (bản đầu) | Ví dụ thật | Sửa |
|---|---|---|
| Cửa sổ số vét nhầm cỡ mẫu/ĐLC/thời gian | «LVEF ≤ 40% (n = 5988)» ⇒ EF {40, 5988}; «3.619 người, tuổi TB 74,2 (ĐLC 6,99)» | số phải dính mỏ neo |
| Ngưỡng tuổi so với tuổi trung bình | «≥ 50 tuổi» vs «mean age 61» (TRACE RA) | tách loại «mô tả» |
| Mục chi tiết hơn tóm tắt | PARADIGM-HF «LVEF ≤ 40% (sau sửa ≤ 35%)» vs tóm tắt chỉ «≤ 40%» | chỉ 🟠 khi mâu thuẫn hai chiều; toàn văn nâng ⚪ → ✓ |
| Phủ định kép | «beta-blockers should not be routinely withheld» | bỏ «routinely» trơ trọi khỏi mẫu |
| Khuyến cáo phủ định về can thiệp KHÁC | CAP ITEM-01 (kháng sinh ≥ 3 ngày) bị gắn câu «recommend against corticosteroids» | câu khuyến cáo phủ định phải nhắc mỏ neo |
| Mỏ neo rác | «ATS», «CAP», chữ Việt in hoa «KHUNG» | lọc tổ chức/bệnh + âm tiết Việt |
| Mục «làm ít đi» | «giảm liều BZD» vs «recommend against benzodiazepines» | câu đầu chứa «giảm/ngừng/dừng…» ⇒ không áp |

**Còn lại, biết trước (không sửa được bằng khớp từ):** câu kết luận phủ định về **nhánh so sánh** (vd «siêu âm
mỗi 3 tháng không cải thiện…» cho mục khuyến cáo giữ 6 tháng; «parenteral không hơn đường uống» cho mục theo dõi
đường huyết khi dùng corticoid). Đây là loại bác sĩ đọc một lần là rõ — đúng nghĩa «cần đọc lại», không phải «sai».
Có một cảnh báo đáng giữ: Cochrane phục hồi chức năng sau đợt cấp COPD — «some recent studies showed no benefit of
rehabilitation on hospital readmissions and mortality».

**Chưa đo được bản cuối trên toàn kho:** mạng máy mất từ 18:31 (NCBI, Europe PMC, GitHub đều timeout). Chạy lại khi
có mạng: `~/.ebm-venv/bin/python tools/kiem_cheo_ngu_nghia.py --toan-kho`. Ứng viên bộ vàng làm giàu:
`… --ung-vien-bo-vang --lam-giau` (cần mạng; không có mạng thì bản vòng tròn thường).

**Việc của bác sĩ:** gắn nhãn 20 mục trong `quality/eval/kiem-cheo-ngu-nghia/bo-vang.cho-duyet.json`
(`dung_quan_the` · `dung_chieu` · `du_dieu_kien` = true/false), rồi `--do-bo-vang` để biết tỉ lệ báo động giả trước khi
tính chuyện chặn. Máy không tự gắn nhãn.

_Cần bác sĩ kiểm chứng._
