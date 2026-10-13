# 13/10/2026 — EndNote: trích dẫn chỉ là tài liệu tham khảo chưa có nội dung đọc nhanh ⇒ «Tóm tắt MÁY» từ abstract gốc

## Vấn đề

- Sau PR #168/#169, 155 trích dẫn CHỈ là tài liệu tham khảo của một mục dashboard chỉ có dòng «Tài liệu tham khảo bổ trợ»:
  dashboard không có nội dung riêng cho các bài này, và luật «không gán kết quả của nguồn chính cho bài tham khảo» là đúng.
  Bác sĩ (13/10): «Gộp và hoàn thiện với các trích dẫn còn lại».

## Cách làm

- Tóm tắt MÁY tiếng Việt (thiết kế · P · I · C · O · kết quả) rút từ ABSTRACT GỐC trong thư viện, lưu ở kho riêng ngoài git
  `EBM-Dashboards/tom-tat-abstract-vi.json` (khoá «PMID <n>» hoặc «DOI <doi chữ thường>»). Khối in nhãn «chưa qua cổng
  dashboard — không phải khuyến nghị», không mức chứng cứ; dòng chân đổi sang `CHAN_MAY` cho đúng nguồn gốc nội dung.
- Chốt cứng `so_khong_khop`: MỌI con số trong tóm tắt phải có nguyên văn trong abstract gốc của CHÍNH bản ghi (chuẩn hoá
  «0·85» của Lancet và dấu phân cách hàng nghìn; dấu phẩy thập phân KHÔNG chuẩn hoá) — lệch một số ⇒ không in, báo
  `tom_tat_lech_so`. Mục chính ở bất kỳ dashboard nào không bao giờ nhận tóm tắt máy. Kho hỏng ⇒ cảnh báo, lượt vẫn chạy
  không có tóm tắt máy.
- Chốt số đã bắt thật 3 lỗi soạn: số năm/số bài có trong tiêu đề nhưng không có trong abstract (GRADE «26», ATA «2016»…).
  Số viết bằng chữ trong abstract («Fourteen RCTs») thì tóm tắt cũng viết bằng chữ.

## Chạy thật

- Kho 153 mục (140 có abstract + 13 không có abstract: đính chính, thông báo rút và thay, hướng dẫn, thư — chỉ ghi loại bài).
  Ghi 192 bản ghi (152 tóm tắt máy + dòng trạng thái toàn văn của các bài vừa tải qua phiên Chrome), sao lưu trước, 0 lỗi,
  0 lệch số. Đọc lại: 152/152 khoá có bản ghi theo PMID đã in. PMID 37952131 (SELECT) nằm trên bản ghi khớp theo DOI đã mang
  khối mục chính từ dashboard CKM — đúng thứ tự ưu tiên.
- Giữ nguyên, không tóm tắt: PMID 36036525 và 39190340 — trường Abstract chứa ghi chú tiếng Việt chứ không phải abstract
  PubMed.

## Phát hiện kèm (chưa sửa ở đây)

- Abstract nhập qua Europe PMC bị cắt khi chữ có dấu «<» (vd «<140 mm Hg»): `_bo_the_html` coi «<» là đầu thẻ và xoá tới thẻ
  thật kế tiếp (`<h4>`). Gặp ở ≥ 15 bài trong 155 (INTERACT2, AβYSS, ROSIER…); tóm tắt máy ghi rõ «abstract bị cắt — xem toàn
  văn». Sửa bộ lọc + nạp lại abstract là việc riêng.
- `ngu_canh` không gộp khoá «doi:» (trích dẫn chỉ có DOI) với khoá «pmid:» khi trích dẫn có PMID đến SAU — bản ghi SELECT mất
  dòng toàn văn theo PMID.

## Kiểm

- `tools/test_tom_tat_may_tham_khao_20261013.py` 11 ca; 11/11 phép đột biến đỏ đúng chỗ (bỏ chốt số, không chuẩn hoá «·»,
  mục chính nhận tóm tắt máy, chân luôn CHAN, không in, DOI không chữ thường, kho hỏng làm sập, dùng abstract của bản ghi
  khác, chuẩn hoá dấu phẩy thập phân, ô trống vẫn in, kho sai khuôn coi như hợp lệ).

## Bổ sung cùng ngày: nhấn mạnh — chữ đậm và màu

- Bác sĩ: «nội dung cần nhấn mạnh hãy in đậm», «có thể hiện được màu sắc không». Đo trên EndNote 2025 (sao lưu trước, chỉ
  thử trên MỘT bản ghi): `set field` chỉ nhận chữ thường; `set record contents` (XML có `<style face="bold">`) chạy không lỗi
  nhưng bị BỎ QUA (xuất lại trùng y bản trước, 3 lần thử, số bản ghi giữ 1928); `import` tạo bản ghi MỚI; sửa thẳng cột
  `text_styles` của `sdb.eni` kích hoạt trigger `refs__refs_ord_AU` dùng hàm `EN_MAKE_SORT_KEY` và collation `ENCIN_Base` riêng
  của EndNote — bên ngoài không tái tạo được ⇒ nguy cơ hỏng chỉ mục, thư viện lại đang đồng bộ EndNote Online ⇒ KHÔNG làm.
  Thanh định dạng trường chỉ có Đậm/Nghiêng/Gạch chân/chỉ số trên–dưới; 391 bản ghi có định dạng, 0 bản ghi có màu.
- Giải pháp: nhãn IN HOA + biểu tượng màu trong BMP (✅ áp dụng/thực hành · ⚠️ cân nhắc/lưu ý · ⏸️ chưa đủ · ⛔ an toàn ·
  ▶️ kết quả/VN · ⭐ điểm nhấn · ❗ khuyến nghị lệch · ❌ rút và thay · ↔️ đặt cạnh · ℹ️ tham khảo/tóm tắt máy). Đã nhìn
  thật trong EndNote: hiện có màu. Ghi 850 bản ghi, 0 lỗi, sao lưu trước.
- Kiểm: `tools/test_tom_tat_trinh_bay_20261013.py` 4 ca (mọi nhãn trong BMP · mỗi phần có dấu màu + IN HOA · an toàn mang dấu
  đỏ, ba mức quyết định phân biệt · tham khảo không mang dấu quyết định); 9/9 đột biến đỏ (gồm chạy lại M1/M3/M5).
