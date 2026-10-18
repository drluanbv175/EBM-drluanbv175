# 18/10/2026 — Bản đặt-cạnh không có sổ «bác sĩ đã xét»: con số «mục apply có tổng hợp mới hơn» không bao giờ giảm

**Triệu chứng.** Hòm việc / Đài hoàn thiện báo «117 mục 'apply' có nguồn tổng hợp MỚI HƠN» (bản đặt-cạnh 29/09) suốt ba tuần;
chỉ số E-MOI không có đường nào để giảm ngoài việc dựng lại gói.

**Nguyên nhân.** `tools/dat_canh_chung_cu_moi.py` đếm mọi mục `apply` mà `elink pubmed_pubmed_reviews` trả bài tổng hợp
mới hơn — kể cả bài LẠC CHỦ ĐỀ (chính công cụ đã ghi: không lọc máy được) — và không có chỗ ghi kết luận của bác sĩ.

**Đo 18/10/2026** (quét đủ bằng chính hàm của công cụ): 155 PMID `apply` · 112 mục có bài mới hơn · 358 cặp · 0 lỗi mạng.
Sàng lọc theo TIÊU ĐỀ (máy đề xuất, chưa phải quyết định): 60 mục cùng câu hỏi (A) · 19 liên quan gián tiếp (B) · 29 mục mọi
nguồn lạc chủ đề (L, vd tầm soát hẹp ĐM cảnh ↔ tầm soát herpes/trầm cảm) · 4 mục là chính nguồn hoặc tổng quan nền (S).
Phát hiện kèm: mục AIS đang trích AHA/ASA 2019 trong khi đã có AHA 2026 (PMID 41582814); mục CAP đang trích bài tóm tắt thứ
cấp thay vì guideline ATS gốc (PMID 40679934).

**Vá phụ cùng lượt.** «Không mục nào có ứng viên» từng bị báo «Không hỏi được PubMed» (mã 2) ngay cả khi PubMed đã trả lời
đủ — lỗi sẽ lộ ra khi sổ đã xét lọc hết mục. Nay chỉ mã 2 khi MỌI PMID không hỏi được; PMID không hỏi được được in rõ trong
tiêu đề bản đặt-cạnh.

**Cách vá.** Sổ `EBM-Dashboards/vuot-qua-da-xet.json` (ngoài git) — {pmid đang dùng: pmid_moi_da_xet, ket_luan, ngay,
loi_bac_si}. Kết luận đóng: lac_chu_de · chinh_nguon · da_so_giu; `can_cap_nhat` vẫn được đếm. Nguồn MỚI chưa xét ⇒ mục tự
mở lại. Chỉ `tools/ghi_vuot_qua_da_xet.py` ghi: bắt buộc `--loi` (nguyên văn bác sĩ), chạy khô mặc định, sao lưu trước khi
ghi, đóng hàng loạt chỉ cho nhóm L/S; nhóm A/B phải đọc so từng mục.

**Kiểm hồi quy.** `tools/test_vuot_qua_da_xet_20261018.py` (9 test, ngoại tuyến, đầu–cuối với mạng giả); kiểm đột biến 3/3
(bỏ lọc đã xét; khôi phục điều kiện mã 2 cũ; cho đóng hàng loạt nhóm A) ⇒ đỏ đúng chỗ, phục hồi xanh.
