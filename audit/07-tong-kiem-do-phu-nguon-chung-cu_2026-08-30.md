# Tổng kiểm độ phủ NGUỒN CHỨNG CỨ — thư viện · hiệp hội · tạp chí (30/08/2026)

> Trả lời câu hỏi của bác sĩ: «các nguồn đã đủ chưa, chưa thì hoàn thiện». Mọi con số
> dưới đây đếm từ CODE VÀ SỔ đang sống trong repo (không kê từ trí nhớ); chỗ nào không
> đo được từ phiên cloud thì nói rõ. Cần bác sĩ kiểm chứng.

## Kết luận ngắn

- **Tầng thư viện/API: ĐỦ cho nguyên tắc «chỉ nguồn miễn phí»** — 8 nguồn máy-đọc đang
  active (sau đính chính hôm nay), phủ tra cứu, xác minh, rút bài, đăng ký thử nghiệm,
  preprint và lớp Crossref-nhanh.
- **Tầng hiệp hội: phủ GIÁN TIẾP đầy đủ qua PubMed-lane** (4 kênh thẩm quyền + nhãn 28
  nhóm tổ chức/tạp chí); phủ TRỰC TIẾP (web hội, sớm hơn PubMed hàng tuần–tháng) đã dựng
  8 trạm nhưng **đang chờ bật** — hôm nay đã làm xong công cụ bật MỘT LỆNH, việc còn lại
  bắt buộc chạy trên máy thật vì mọi kênh mạng của sandbox đều bị chính sách chặn (đã đo).
- **Tầng tạp chí: 7 tạp chí đa khoa lớn + ~15 tạp chí chuyên khoa** đã nằm trong nhãn
  nguồn-tin-cậy. Ba bổ sung đáng cân nhắc (thẩm quyền bác sĩ — xem §3).
- **Thiếu CÓ CHỦ Ý, không phải lỗ hổng:** UpToDate/DynaMed/Embase (trả phí — nguyên tắc
  P5 cấm), BYT/Cục Quản lý Dược VN (không API — kênh thủ công của bác sĩ).

## 1. Tầng THƯ VIỆN & API máy-đọc (data/sources.json — 8 active)

| Nguồn | Vai trò | Trạng thái |
|---|---|---|
| PubMed E-utilities (×2 cấu hình) | tra cứu 4 tầng + xác minh PMID + elink vượt-qua | active (đo 15/08 máy thật) |
| Europe PMC REST | đối chiếu + tầng 3 chuỗi rút bài + làn preprint (PPR) | active |
| Crossref API | metadata DOI + `updated-by` (rút bài theo DOI) | active |
| Retraction Watch (Crossref CC0, NGOẠI TUYẾN) | nền rút bài 30.851 PMID — tầng ① | active |
| openFDA | nhãn thuốc/Boxed Warning (normativeBasis drug-label) | active |
| OpenAlex | làn đối chiếu Crossref-nhanh (bài chưa vào PubMed) | active |
| ClinicalTrials.gov API v2 + preprint | làn thử nghiệm + tín hiệu sớm trong MỖI lượt quét A2 | **active — ĐÍNH CHÍNH hôm nay** |

**Đính chính SRC-031 (sổ nói khác code):** sổ ghi `not-covered/ad-hoc` trong khi
`surveillance_scan.py` đã nối `search_trials_lane` + `search_preprint_lane` vào MỌI lượt
`run_scan` từ 15/08 (fail-soft từng làn); bằng chứng chạy thật: CI run #89 ngày 28/08 hai
làn kéo ứng viên thật về. Cùng họ «lá cờ nói hộ» BH61 — sổ đã sửa, kèm bằng chứng.

## 2. Tầng HIỆP HỘI

**(a) Phủ gián tiếp qua PubMed — ĐANG CHẠY:** 4 kênh thẩm quyền gọi tên (Cochrane · NICE
· USPSTF · WHO) + tìm kiếm 3 tầng (guideline→SR/MA→RCT) + tầng `edat` chống bỏ sót bài
chưa đánh chỉ mục (BH38) + nhãn `TRUSTED_SOURCE_ALIASES` nhận diện **28 nhóm**: WHO, NICE,
USPSTF, CDC, FDA, EMA, MHRA, ACC/AHA, ESC, ADA/EASD, KDIGO, GINA, GOLD, IDSA, EULAR/ACR,
ACG/AGA/ASGE, AASLD/EASL, ASH/ISTH, AGS, ATS/ERS/BTS, Cochrane + 7 tạp chí đa khoa.

**(b) Phủ trực tiếp web hội — DỰNG XONG, CHỜ BẬT (8 trạm):** GOLD · GINA · KDIGO · ADA
Standards of Care · ESC · ACC/AHA · EMA/MHRA Drug Safety Update (RSS) · IDSA (kèm
AGS/USPSTF/WHO/NICE web). Giá trị: guideline lên web hội TRƯỚC PubMed hàng tuần–tháng.

**Đo 29–30/08 từ phiên cloud (ghi vào sổ nguồn để không ai thử lại mù):** mọi host hội
bị chính sách mạng của môi trường chặn (CONNECT 403) — kể cả eutils/crossref/ebi/openalex/
openfda và kênh WebFetch ⇒ **không kênh nào của sandbox xác minh sống được URL hội**.

**Hoàn thiện hôm nay:** `giam_sat_to_chuc.py` có thêm hai chế độ (4 test ngoại tuyến,
đã kiểm đột biến):
```bash
python3 tools/giam_sat_to_chuc.py --kiem-tra    # dò sống 8 trạm bằng chính fetch+parser của trạm — chỉ đo
python3 tools/giam_sat_to_chuc.py --bat-neu-ok  # bật (not-covered→active) đúng trạm dò đạt, tự sao lưu sổ
```
Chạy trên **máy thật, ngoài sandbox** (terminal thường) — trạm nào fetch được và parser
đọc ≥1 tiêu đề sẽ bật kèm bằng chứng `kich_hoat`; trạm trượt giữ nguyên kèm lý do.

## 3. Tầng TẠP CHÍ (lớp nhãn nguồn-tin-cậy)

Đang có: **NEJM · Lancet · JAMA · BMJ · Annals of Internal Medicine · Nature Medicine ·
Cochrane** + tạp chí chính thức của các hội ở §2a (Circulation, JACC, Eur Heart J,
Diabetes Care, Diabetologia, Kidney Int, Clin Infect Dis, Ann Rheum Dis, Gastroenterology,
Gut, Hepatology, J Hepatol, Thorax…).

**Đề xuất bổ sung — chờ bác sĩ duyệt** (đây là lớp GÁN NHÃN TIN CẬY, thêm tên là quyết
định biên tập; alias ngắn dễ khớp nhầm sang tiêu đề bài nên phải thêm cẩn thận):
1. **AAN / Neurology®** — kho hiện có 2 dashboard đau đầu + chóng mặt; nguồn SNNOOP10
   nằm ở Neurology. Alias an toàn: "american academy of neurology".
2. **Stroke / JAMA Neurology** — HINTS, BE-FAST đều ở Stroke. Alias "stroke" TRÙNG từ
   thường gặp trong tiêu đề — nếu thêm phải vào nhóm alias-cẩn-trọng.
3. **American Family Physician (AAFP)** — nguồn sụt cân đang dùng (Gaddey 2021); sát
   thực hành ngoại trú.

## 4. Tầng LIÊM CHÍNH nguồn (đã chạy, kể để trọn bức tranh)

Chuỗi rút bài 3 tầng bất đối xứng (Retraction Watch ngoại tuyến → NCBI → Europe PMC) +
Crossref `updated-by` cho DOI (BH33) + sổ xác minh nguồn tích luỹ theo PMID/DOI +
cổng A12 fail-closed (BH27) + đối chiếu OpenAlex.

## 5. Việc còn lại & phân quyền

| Việc | Ai | Cách |
|---|---|---|
| Bật 8 trạm web hội | Bác sĩ (máy thật, ngoài sandbox) | `--kiem-tra` rồi `--bat-neu-ok` (1 lệnh, có sao lưu) |
| BYT / Cục Quản lý Dược VN | Bác sĩ (thủ công quý) | không API công khai; sổ giữ `manual`, không bịa endpoint |
| 3 nhãn tạp chí đề xuất §3 | Bác sĩ duyệt | tôi thêm alias sau khi duyệt |
| UpToDate/DynaMed/Embase | KHÔNG làm | trả phí, cấm cào (P5) — loại trừ có chủ ý |
| Đo độ phủ watchlist 63 chủ đề | Máy thật | watchlist nằm trên OneDrive — phiên cloud không đọc được |

*Soạn 30/08/2026 từ code + sổ đang sống; phép đo mạng thực hiện 29–30/08 từ phiên cloud.
Cần bác sĩ kiểm chứng.*
