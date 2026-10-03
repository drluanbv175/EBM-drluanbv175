# 03/10/2026 — Bác sĩ uỷ quyền máy đọc toàn văn bài NXB «cấm» (ghi quyết định minh bạch)

**Căn cứ: QUYẾT ĐỊNH của bác sĩ, KHÔNG phải sự cho phép của NXB.** Ngày 03/10/2026 bác sĩ (chủ hệ thống) nói rõ trong chat:
«Vậy hãy chỉnh sửa lại để máy đọc toàn văn và tóm tắt cho tôi». Ý là cho Claude đọc toàn văn bài Elsevier mà bác sĩ có quyền
truy cập, qua Chrome của bác sĩ, để tóm tắt và lập hồ sơ. Điều khoản website Elsevier (sửa 12/03/2026) vẫn cấm dùng Content với
công cụ AI, TRỪ khi có giấy phép, thoả thuận thuê bao hay sự cho phép. Điều khoản đó không đổi. Đây là quyết định của bác sĩ dựa
trên quyền truy cập của mình, và trách nhiệm điều khoản thuộc bác sĩ. Hệ phải ghi đúng như vậy.

**Trước khi vá.** Với mọi NXB «cam» trong `DIEU_KHOAN_NXB`, phiếu luôn xếp bài vào «BÁC SĨ ĐỌC TRỰC TIẾP» và `kiem_ho_so` từ chối
mọi hồ sơ. Hệ không có chỗ ghi quyết định này của bác sĩ.

**Cách vá** (`tools/doc_toan_van_co_nguoi.py`, xếp chồng trên #106):
- Tệp quyết định `EBM-Dashboards/dieu-khoan-bac-si-uy-quyen.json` nằm ngoài git: `{_about, muc: [{nxb, ngay, can_cu, pham_vi,
  het_han?}]}`. Hàm `uy_quyen_bac_si(nxb, hom_nay, tep=None)` tính đường dẫn LÚC GỌI và fail-closed: tệp vắng hay hỏng, mục khác
  NXB, ngày sai dạng hoặc ở tương lai, căn cứ dưới 10 ký tự, `het_han` sai dạng hoặc đã qua ⇒ không có uỷ quyền.
- `--ghi-uy-quyen "<khoá NXB>" --can-cu "<nguyên văn lời bác sĩ>" [--pham-vi …] [--het-han …] [--ghi]` mặc định chạy thử. Lệnh chỉ
  nhận khoá «cam», in «quyết định của bác sĩ — trách nhiệm điều khoản thuộc bác sĩ», ghi kèm câu trích điều khoản NXB (không đổi).
  Tệp đã có mà hỏng thì không ghi đè. Thư mục vắng thì trả mã 2 và không tự tạo. Công cụ không tự tạo tệp này ở đường nào khác.
- Phiếu: NXB «cam» có uỷ quyền còn hiệu lực ⇒ vào làn trình duyệt có người, nhãn «BÁC SĨ UỶ QUYỀN MÁY ĐỌC (<ngày>)».
- `kiem_ho_so` chỉ nhận khi đủ hai điều kiện: (a) có uỷ quyền đúng NXB, (b) hồ sơ khai `dieu_khoan.ket_luan = bac_si_uy_quyen`
  kèm `ngay_uy_quyen` trùng ngày trong tệp. Không có uỷ quyền thì thông điệp cũ giữ nguyên văn. `bac_si_uy_quyen` không thêm vào
  `_KET_LUAN_DIEU_KHOAN_NHAN`, nên NXB chưa kiểm vẫn chỉ nhận `cho_phep` | `giay_phep_cc`. Mọi kiểm khác giữ nguyên.
- Bản đọc `doc_sau/PMID-<n>.md` của hồ sơ uỷ quyền mở đầu thân bài bằng dòng «Đọc theo QUYẾT ĐỊNH của bác sĩ ngày …».
- Doctrine `_CONNECTOR-CHUNG-CU.md` §2septies có thêm mục 8 (bản y khoa giống từng byte, BH107). Tệp quyết định THẬT chưa được
  ghi trong PR này: phiên chính ghi sau khi PR gộp.

**Kiểm hồi quy.** Thêm 32 test (tổng 108). Một fixture tự dùng trỏ `DASH` vào thư mục tạm, để test không đọc tệp quyết định thật.
BH152 có thêm kiểm: hồ sơ Elsevier tự khai `bac_si_uy_quyen` mà không có tệp, hoặc tệp chỉ uỷ quyền ADA, vẫn bị từ chối (dùng tệp
tạm). Kiểm đột biến: sao lưu ngoài cây, `python -B`, xoá `__pycache__`, `cmp` sau mỗi phép. Cả 8 đột biến đều làm test đỏ: bỏ (a),
bỏ (b), bỏ khớp ngày, uỷ quyền mở cho mọi NXB, bỏ hết hạn, bỏ dòng quyết định, phiếu bỏ qua uỷ quyền, nhận `bac_si_uy_quyen` cho
NXB chưa kiểm. BH152 cũng đỏ ở «bỏ (a)» và «mở cho mọi NXB».
