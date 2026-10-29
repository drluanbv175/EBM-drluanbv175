# 29/10/2026 — Cổng số tóm tắt ⑨ tách sai số lớn có dấu cách U+2008/U+2007

**Hiện tượng.** Lô ⑨ ngày 28–29/10: bài PINCER (Lancet 2012, PMID 22357106, văn bản in từ XML PMC) viết phân cách nghìn bằng dấu
cách chấm câu U+2008 («480 942», «£14 641·20»). `_chuan_so` chỉ nhận dấu phẩy, U+2009, U+202F, U+00A0 làm phân cách nghìn, nên
cổng `kiem` tách «480 942» thành hai số «480» và «942» — không có trong bài. Agent đọc phải chép đúng ký tự lạ U+2008 vào
`tom_tat.json` mới qua cổng. Bài JAMA Netw Open (PMID 40577011) gặp chuyện tương tự với U+2009 (đã được hỗ trợ, nhưng agent không
biết nên cũng chép tay).

**Sửa.** Thêm U+2007 (dấu cách chữ số) và U+2008 (dấu cách chấm câu) vào lớp phân cách nghìn của `_chuan_so`. Dấu cách THƯỜNG giữa
hai số vẫn không gộp (giữ luật 19/10 cho bảng PDF).

**Kiểm.** `test_phan_cach_nghin_dau_cach_dac_biet_van_khop` (5 ký tự phân cách, số tiền có phần thập phân «·», ca dấu cách thường
không gộp). Hai đột biến (bỏ U+2008, bỏ U+2007) đều làm test đỏ; khôi phục xanh; 48 test tệp tóm tắt đạt.

**Quyết định kèm theo.** Cổng cũng bắt nhãn «[Cần kháng đông…]» như cụm cấm «[CẦN…» (mẫu không phân biệt hoa/thường). Giữ nguyên:
dương tính giả này rẻ (agent đổi chữ), còn nới mẫu sẽ mở kẽ hở cho nhãn «[Cần …]» chưa chắc lọt vào thân văn bản.
