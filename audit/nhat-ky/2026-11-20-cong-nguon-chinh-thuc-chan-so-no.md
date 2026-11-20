# 20/11/2026 — Cổng «đọc nguồn chính thức» chuyển sang CHẶN, có sổ nợ; cách ly tệp Unpaywall cũ không giấy phép mở

**Bối cảnh.** Bác sĩ hỏi «Hệ thống cập nhật chứng cứ y khoa có còn vấn đề gì hoàn thiện không», rồi ra lệnh «Hoàn thiện tất cả vấn
đề trên». Ba quyết định thuộc thẩm quyền bác sĩ được hỏi bằng thẻ chọn, bác sĩ chọn cả ba phương án khuyến nghị:
- «Chặn, có sổ nợ (Khuyến nghị)»;
- «Dời ra kho cách ly (Khuyến nghị)»;
- «Soạn phiếu đối chiếu (Khuyến nghị)».

**1 — Cổng nguồn chính thức (mục apply không PMID) chỉ cảnh báo.**
- PR #447 dựng bảo đảm đọc nguồn chính thức ở mức CẢNH BÁO.
- Đo 20/11 trên MỌI bản dashboard: 375 mục, 128 nguồn, 126 có bằng chứng đã đọc, 0 mục không có khoá nguồn.
- Còn 2 nguồn chưa đọc, ở 9 mục:
  - trang chủ GOLD `goldcopd.org/` ở COPD_20260610 (ITEM-01..03) và COPD_20261020 ITEM-01;
  - NICE NG56 ở 5 bản «Người cao tuổi đa bệnh» (ITEM-02).
- Vá — `verify_dashboard.kiem_doc_nguon_chinh_thuc_apply`, cùng khuôn bánh cóc với BH161:
  - nguồn chưa có bằng chứng ⇒ LỖI;
  - mục không có cả DOI lẫn URL hợp lệ ⇒ LỖI;
  - mục trong sổ nợ `EBM-Dashboards/no-nguon-chinh-thuc-apply.json` còn hạn ⇒ cảnh báo; quá hạn ⇒ lỗi;
  - sổ hỏng ⇒ coi như vắng (fail-closed).
- Khoá sổ gồm dashboard + item + KHOÁ NGUỒN: đổi URL/DOI là nguồn mới, bản dashboard mới không thừa hưởng nợ.
- Công cụ: `doc_nguon_chinh_thuc.py so-no` báo cáo; `--tao` lập sổ MỘT lần, chỉ gồm mục đang chưa đọc; `--gia-han` giữ nguyên
  danh sách. Cả hai đòi nguyên văn lời bác sĩ ≥ 20 ký tự, hạn ≤ 90 ngày.
- Đã lập sổ: 9 mục, 2 nguồn, hạn 20/12/2026, căn cứ ghi nguyên văn hai câu của bác sĩ.
- `so_toan_van.py` và hòm việc (`tu_de_xuat_viec.giac_quan_no_toan_van`):
  - mục bị chặn ⇒ ưu tiên 1;
  - nợ trong hạn ⇒ ưu tiên 2, thành ưu tiên 1 khi còn ≤ 7 ngày;
  - bỏ dòng «hiện chỉ CẢNH BÁO».
- Đã dạy SKILL `cap-nhat-chung-cu-y-khoa`, agent `cap-nhat-guideline` và CLAUDE.md (1 câu).
- Đo trên dashboard thật:
  - NguoiCaoTuoi_20261112: PASS, kèm cảnh báo «NỢ NGUỒN CHÍNH THỨC … còn 30 ngày»;
  - COPD_20261114 (URL PDF GOLD 2026): PASS, 1/1 đã đọc.

**2 — Tệp `_UPW` cũ không giấy phép mở vẫn nằm trong kho (việc dữ liệu treo từ nhật ký 04/10, BH160).**
- Phạm vi: 42 tệp `_UPW` tạo trước bản vá BH160 (04/10/2026 13:47). Tệp sau mốc đã qua cổng giấy phép lúc lưu.
- Kiểm dấu Creative Commons trong chính tệp (PDF đọc chữ bằng pypdf) rồi đối chiếu bản ghi Unpaywall:
  - 35 tệp không giấy phép mở — NXB «cấm» bản đọc-miễn-phí, đúng như Unpaywall;
  - PMID 42343056 (Springer, Unpaywall chỉ ghi CC BY) bị bộ dò chữ PDF bỏ sót ⇒ giữ bằng `--giu`.
- Công cụ mới `tools/cach_ly_upw_khong_giay_phep.py`:
  - mặc định chạy khô; `--ap-dung` CHUYỂN, không xoá, vào `EBM-Dashboards/_cach_ly_toan_van/upw-khong-giay-phep-mo-20261120/`;
  - kèm `MANIFEST.json` (sha256, kích thước, ngày tạo, lý do); không ghi đè đích;
  - **chốt bảo phủ:** không dời tệp là bằng chứng toàn văn DUY NHẤT của mục «Áp dụng ngay» (cùng định nghĩa
    `co_toan_van_trong_kho`), trừ khi có `--ca-muc-apply`.
- Kết quả: đã chuyển 29 tệp (14,2 MB).
  - «Áp dụng ngay» giữ 314/314.
  - «Cân nhắc» 1763 → 1750/1929; «Chưa đủ» 298 → 296/349 (bản cách ly không còn tính là đã đọc).
- 6 tệp còn GIỮ chờ lấy lại bản hợp lệ qua làn Chrome có uỷ quyền:
  - 15042359 Springer;
  - 17005808 ASM (chưa kiểm điều khoản);
  - 23235577 và 34932836 Cochrane/Wiley;
  - 32446323 Lancet/Elsevier;
  - 41358886 ADA.
- Năm bài có PMCID nhưng không thuộc tập giấy phép mở. Sổ `khong-oa.txt` ghi «không lấy được» 26–30/10.

**Kiểm:**
- `tools/test_cong_nguon_chinh_thuc_chan_20261120.py` (9 test) và `tools/test_cach_ly_upw_khong_giay_phep_20261120.py` (5 test).
- Sửa `test_doc_nguon_chinh_thuc_20261120` cho đúng mức CHẶN.
- Đột biến cổng/sổ/hòm việc: 13/13 làm test đỏ đúng chỗ. Đột biến công cụ cách ly: 7/7.
- Phục hồi xanh, chạy `python -B`, xoá `__pycache__` trước mỗi phép.

**Chưa làm (việc của người / phiên khác):**
- Trả 9 mục nợ trước 20/12/2026:
  - NICE NG56: bác sĩ đọc NBK409224 rồi `bac-si-da-doc`;
  - trang chủ GOLD ở hai bản COPD cũ: đổi URL sang PDF GOLD, hoặc để bản nối tiếp COPD GOLD 2027 thay thế.
- Làn Chrome cho 6 bài bị giữ, rồi chạy lại `cach_ly_upw_khong_giay_phep.py --giu 42343056 --ap-dung`.
