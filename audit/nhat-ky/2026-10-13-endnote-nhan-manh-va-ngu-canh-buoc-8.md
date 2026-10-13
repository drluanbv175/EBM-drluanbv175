# 13/10/2026 — EndNote: nhấn mạnh bằng biểu tượng màu; bước ⑧ một dashboard ghi đè khối mục chính của chủ đề khác

## 1. Nhấn mạnh — chữ đậm và màu

- Bác sĩ: «nội dung cần nhấn mạnh hãy in đậm», «có thể hiện được màu sắc không». Đo trên EndNote 2025 (sao lưu trước, chỉ
  thử trên MỘT bản ghi): `set field` chỉ nhận chữ thường; `set record contents` (XML có `<style face="bold">`) chạy không lỗi
  nhưng bị BỎ QUA (xuất lại trùng y bản trước, 3 lần thử, số bản ghi giữ 1928); `import` tạo bản ghi MỚI; sửa thẳng cột
  `text_styles` của `sdb.eni` kích hoạt trigger `refs__refs_ord_AU` dùng hàm `EN_MAKE_SORT_KEY` và collation `ENCIN_Base` riêng
  của EndNote — bên ngoài không tái tạo được ⇒ nguy cơ hỏng chỉ mục, thư viện lại đang đồng bộ EndNote Online ⇒ KHÔNG làm.
  Thanh định dạng trường chỉ có Đậm/Nghiêng/Gạch chân/chỉ số trên–dưới; 391 bản ghi có định dạng, 0 bản ghi có màu.
- Giải pháp: nhãn IN HOA + biểu tượng màu trong BMP (✅ áp dụng/thực hành · ⚠️ cân nhắc/lưu ý · ⏸️ chưa đủ · ⛔ an toàn ·
  ▶️ kết quả/VN · ⭐ điểm nhấn · ❗ khuyến nghị lệch · ❌ rút và thay · ↔️ đặt cạnh · ℹ️ tham khảo/tóm tắt máy). Đã nhìn
  thật trong EndNote: hiện có màu. `tools/test_tom_tat_trinh_bay_20261013.py` 4 ca; 9/9 đột biến đỏ.
- Commit này lỡ PR #171 (PR gộp lúc 19:40 với commit đầu) — lặp lại ca #168/#169: đẩy commit bổ sung lên nhánh của PR đang
  mở thì kiểm `gh pr view --json state` NGAY trước khi đẩy.

## 2. Bước ⑧ của dây chuyền chỉ nạp MỘT dashboard ⇒ khối EndNote dựng từ ngữ cảnh thiếu

- `xuat_goi_cap_nhat.py` ⑧ gọi `nap_endnote_chu_de.py --file <một dashboard> --ap-dung`, tóm tắt tự chạy sau đó với ĐÚNG tệp
  đó làm ngữ cảnh. Ca thật: SELECT là MỤC CHÍNH (trích theo DOI) ở chủ đề CKM, là THAM KHẢO (kèm PMID) ở chủ đề GLP-1 — chạy
  dây chuyền cho GLP-1 sẽ ghi đè khối mục chính đã qua cổng bằng khối «tham khảo», mất «Cũng dùng trong»/«Đặt cạnh».
- Sửa: `ghi_tom_tat(..., boi_canh=)` dựng ngữ cảnh từ MỌI dashboard cùng thư mục nhưng CHỈ GHI trích dẫn có trong `files`;
  `chay_tom_tat` tự truyền `WebDashboard_*.html` của thư mục. `ngu_canh` gộp khoá «doi:» (gặp trước, chỉ có DOI) vào khoá
  «pmid:» (gặp sau kèm PMID), đổi tên cả trong tập «đã thấy» của từng chủ đề.
- Đo sau sửa: chạy toàn bộ ghi 41 bản ghi (khoá gộp + trích dẫn mới), 0 lỗi; mô phỏng ⑧ cho từng dashboard GLP-1, CKM, COPD
  mới, Mạch máu não ⇒ «sẽ ghi 0» (không ghi đè gì).
- `tham_khao_chua_tom_tat`: trích dẫn chỉ là tham khảo mà kho tóm tắt máy chưa có mục ⇒ dây chuyền in dòng «ℹ … CHƯA có tóm
  tắt máy: N» — máy không tự sinh, cần một phiên Claude soạn (skill `cap-nhat-chung-cu-y-khoa` đã ghi cách). Lượt này soạn 9
  bài của dashboard COPD tạo hôm nay; 2 bản ghi có ghi chú tiếng Việt của bác sĩ trong Abstract ghi `bo_qua` trong kho.
- `tools/test_tom_tat_ngu_canh_day_du_20261013.py` 5 ca; 6/6 đột biến đỏ (N5 «không đổi tên khoá trong tập» lúc đầu SỐNG —
  thêm ca hai phiên bản cùng chủ đề mới bắt được).
