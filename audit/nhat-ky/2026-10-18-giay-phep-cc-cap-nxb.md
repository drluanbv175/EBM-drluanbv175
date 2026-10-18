# 18/10/2026 — Cổng Unpaywall chặn bản OA của NXB đã khai CC ở trang điều khoản (giấy phép mở cấp NXB)

## Bác sĩ yêu cầu
«Sửa cổng để chấp nhận giấy phép CC khai ở cấp NXB khi đã đọc trang điều khoản».

## Ca thật
PMID 33798049 (*Heart Surgery Forum* 2021, DOI 10.1532/hsf.3547): Unpaywall trỏ tới bản PDF trên `storage.imrpress.com` nhưng
trường `license` để trống ⇒ `quyet_dinh_unpaywall` trả «chua_kiem» (tầng 2 chỉ lưu bản mang giấy phép mở — BH160). Trang
Copyright & License của IMR Press khai CC BY 4.0; số HSF trước tập 28 số 8 (2025) do NXB cũ đăng theo CC BY-NC, IMR Press lưu hộ.
Tiền tố DOI 10.1532 thuộc Carden Jennings Publishing trên Crossref ⇒ không khớp được theo DOI.

## Sửa
- `tools/doc_toan_van_co_nguoi.py`: bảng mới `GIAY_PHEP_MO_CAP_NXB` (TÁCH khỏi `DIEU_KHOAN_NXB` — bảng đó chỉ chứa «cấm», test
  khoá) + `giay_phep_mo_cap_nxb(url)` khớp theo MIỀN của bản OA (đúng miền hoặc miền con; «imrpress.com.<khác>» không khớp).
  Mỗi mục bắt buộc: nguồn https, ngày đọc, trích ≤ 15 từ, mọi giấy phép liệt kê đều mở. Mục đầu tiên: IMR Press.
- `tools/gom_toan_van_dashboard.py::quyet_dinh_unpaywall`: xét SAU nhánh «cấm» — bản nằm trên miền của chính NXB trong bảng,
  Unpaywall không ghi giấy phép ⇒ được lưu, lý do ghi «giấy phép mở cấp NXB … điều khoản đọc <ngày>». Bản ở kho khác (Europe
  PMC, kho trường) vẫn «chua_kiem». Không áp cho `--nap` (hồ sơ làn trình duyệt vẫn phải khai `dieu_khoan`).
- Doctrine `_CONNECTOR-CHUNG-CU.md` §2septies mục 4: ngoại lệ hẹp, quy trình thêm NXB (đọc trang điều khoản → PR bảng).

## Kiểm
`tools/test_giay_phep_mo_cap_nxb_20261018.py` (11 ca); 4 đột biến (bỏ nhánh · khớp chuỗi con · bỏ kiểm mọi giấy phép mở ·
doctrine thiếu tên bảng) đều đỏ, phục hồi xanh. Bộ test điều khoản/Unpaywall liên quan + `chot_hoi_quy_bai_hoc.py` xanh.

## Bài học
Giấy phép mở có thể khai ở CẤP NXB thay vì trên từng bản ghi Unpaywall; khớp phải theo miền nơi bản nằm (bằng chứng NXB chịu
trách nhiệm bản đó), không theo tiền tố DOI (NXB đổi chủ, tiền tố cũ còn nguyên).
