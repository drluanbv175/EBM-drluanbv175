# 03/10/2026 — Bài NXB cấm AI: chưa có cách ghi «bác sĩ đã đọc trực tiếp»

**Nguyên nhân.** Với NXB mà điều khoản cấm AI/TDM (`DIEU_KHOAN_NXB`: Elsevier, ADA, EBSCO), phiếu của
`tools/doc_toan_van_co_nguoi.py` xếp bài vào «BÁC SĨ ĐỌC TRỰC TIẾP» và Claude không mở bài. Đọc xong thì bác sĩ chỉ còn
lệnh `--khong-truy-cap <PMID> --ly-do`. Lệnh này sai nghĩa (ghi là «không có quyền đọc») và bản ghi hết hạn sau 90 ngày. Tới
lúc đó giác quan ⑦i (`tu_de_xuat_viec.py::giac_quan_toan_van_the_tuan`) lại đếm thẻ vào «chỉ có tóm tắt» và nhắc lại một việc
bác sĩ đã làm xong.

**Cách vá.**
- `--bac-si-da-doc <PMID> --ghi-chu "<kết luận của bác sĩ>" [--ghi]`: mặc định chạy thử, thêm `--ghi` mới ghi. Ghi chú phải có
  5–300 ký tự sau khi bỏ khoảng trắng hai đầu và không khớp mẫu `_PII`. Đây là KẾT LUẬN bằng lời bác sĩ, không phải nội dung
  bài: tệp không có hàm kiểm trích nguyên văn dùng chung, nên trần 300 ký tự là rào chặn việc chép bài. Lệnh ghi nối vào
  `toan_van_oa/trinh_duyet/bac-si-da-doc.jsonl`, nguồn `bac_si_doc_truc_tiep`, KHÔNG hết hạn. Kho vắng thì trả mã 2 và không tự
  tạo kho.
- `bao_phu_cuc_bo`: thêm trạng thái `bac_si_da_doc_truc_tiep` («BÁC SĨ ĐÃ ĐỌC TRỰC TIẾP»), xét TRƯỚC `khong_truy_cap`. Cố ý
  KHÔNG dùng lại `bac_si_doc_truc_tiep`: chuỗi đó đã là `cach` của phiếu cho bài CHỜ bác sĩ đọc, và một test khoá nghĩa ấy. Nếu
  dùng chung thì bài đã đọc sẽ rơi vào nhóm chờ và phiếu trả mã 1.
- Hằng `TRANG_THAI_DA_PHU` là nguồn sự thật duy nhất cho tập trạng thái «đã phủ», dùng chung giữa phiếu và giác quan ⑦i. Dòng
  phiếu tách hai con số «x bài máy có toàn văn + z bài bác sĩ đọc trực tiếp», vì máy KHÔNG có toàn văn những bài sau.
- `HUONG_DAN` bước 2a và doctrine `_CONNECTOR-CHUNG-CU.md` §2septies trỏ tới lệnh mới. Hai chỗ cùng nhắc: không dán nội dung
  bài Elsevier/ADA vào chat.

**Kiểm hồi quy.** `tools/test_doc_toan_van_co_nguoi_20261002.py` có thêm 15 test (tổng 76). Kiểm đột biến chạy `python -B`, xoá
`__pycache__`, sao lưu rồi `cmp` sau mỗi phép. Các đột biến làm test đỏ: bỏ kiểm độ dài tối thiểu, bỏ kiểm độ dài tối đa, bỏ kiểm
PII, không tính là đã phủ, giác quan vẫn đếm, ghi khi chạy thử, để `khong_truy_cap` thắng, cộng bác sĩ vào «máy có». Đột biến
«hết hạn» ban đầu sống sót vì lỗi phép thử: đột biến dùng `date.today()`, còn test chỉ dời `hom_nay` truyền vào. Đã bổ sung một
bản ghi thật sự cũ 400 ngày; sau đó cả hai dạng hết hạn đều bị bắt.
