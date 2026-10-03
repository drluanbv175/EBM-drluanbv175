# 03/10/2026 — Chốt bí mật trước commit (AN-06) mù nội dung: tên tệp tiếng Việt, tiền tố diff, dòng «++ », \r giữa dòng

**Phát hiện.** Lượt kiểm độc lập ngay sau khi gộp PR gốc #99 và y khoa #73 tìm ra lỗi; tôi đo lại tại chỗ.
- Stage một tệp tên `thử_bí_mật.txt` chứa khối khoá riêng giả: cả hai repo đều trả mã 0 và in «🟢 Không thấy bí mật/PII».
- Nguyên nhân: `core.quotepath` mặc định bằng true, nên git bọc nháy và mã hoá bát phân tên không-ASCII thành
  `+++ "b/th\341\273\255…"`. Hàm `dong_them_da_stage()` chỉ nhận dòng bắt đầu bằng `+++ b/`, nên nó bỏ qua NỘI DUNG của cả
  tệp. Luật theo TÊN tệp (`.pem`…) vẫn chạy, vì phần đó dùng `-z`.
- Repo gốc có 1 và repo y khoa có 4 tệp đã track mang tên không-ASCII. Kiểu tên này là chuyện thường ngày trong repo tiếng Việt.

**Đọc lại hàm thì thấy thêm ba đường lọt cùng gốc** (chốt tin vào định dạng HIỂN THỊ của `git diff`):
1. Người dùng bật `diff.mnemonicPrefix` hoặc `diff.noprefix` ⇒ dòng đầu tệp không còn tiền tố `b/` ⇒ bỏ qua cả tệp.
2. Một dòng THÊM có nội dung bắt đầu bằng `++ ` hiện ra thành `+++ …` và bị đọc nhầm là đầu một tệp mới, nên dòng đó không
   được quét.
3. `splitlines()` cắt dòng cả ở `\r`, ` `, `\x0c`, `\x1c`… nên phần đứng sau ký tự đó mất dấu `+` và không được quét.
- Phụ: tên có dấu cách thì git thêm một TAB vào cuối tên. Tên in ra sai, và tệp nhị phân có dấu cách trong tên bị quét như văn
  bản (quét thừa, không lọt).

**Vá** (`tools/kiem_bi_mat_truoc_commit.py`):
- Ép `-c core.quotepath=false -c diff.mnemonicPrefix=false -c diff.noprefix=false`, cùng `--src-prefix=a/ --dst-prefix=b/
  --no-ext-diff`.
- Giải tên bọc nháy kiểu C bằng `_bo_nhay_c`; cắt TAB cuối tên.
- Chỉ đọc dòng `+++ ` trong phần ĐẦU của mỗi tệp, tức sau `diff --git` và trước `@@`.
- Tách dòng đúng bằng `\n`.
- Fail-closed: tên không đọc được thì quét với tên tạm `<?>`, không bỏ qua.

Hook y khoa gọi đúng công cụ này nên được vá luôn.

**Kiểm.**
- 13 test mới chạy trên repo git thật: tên tiếng Việt, tên có dấu cách, `"`, `\`; ba cấu hình git; dòng `++ `; bốn ký tự ngắt
  dòng; tệp sạch tên tiếng Việt cho qua; giải nháy C.
- Cả 13 test đều ĐỎ trên bản cũ và XANH trên bản vá. 6 phép đột biến (bỏ ép quotepath + giải nháy, bỏ giải nháy, bỏ cắt TAB,
  đọc «+++ » cả trong hunk, `splitlines`, bỏ fail-closed + tiền tố) đều bị bắt.
- BH155 kiểm hành vi trên repo tạm, dùng cấu hình git thật của máy: đỏ trên bản cũ, xanh trên bản vá, chạy 0,35 giây.

**Bài học.** Một chốt đọc đầu ra của công cụ khác phải ép định dạng đầu ra mà nó tin, không dựa vào cấu hình mặc định. Kiểm đột
biến trước khi gộp chỉ thử các mẫu khoá, chưa thử TÊN tệp hay cấu hình git. Lỗ chỉ lộ ra khi một agent độc lập thử từ ngoài vào
với tên tệp tiếng Việt, đúng kiểu dữ liệu của repo này.
