# 13/11/2026 — Chốt số của tóm tắt máy tách sai số có dấu nghìn U+2008 (PUNCTUATION SPACE)

**Phát hiện:** `nap_endnote_chu_de.py --tom-tat-vi --ap-dung` báo «⚠ … số không có trong abstract gốc (152, 16, 18, 812) — không
in tóm tắt máy» cho PMID 35219395 (EndNote recNum 9342). Abstract PubMed efetch viết «18 152 participants» với dấu nghìn là
U+2008; tóm tắt máy chép đúng ký tự đó ⇒ `_cac_so` tách thành 18 và 152, trong khi abstract trong EndNote lưu dấu cách thường
⇒ «18152». Phiên phát hiện đã sửa tạm dữ liệu kho (`EBM-Dashboards/tom-tat-abstract-vi.json`, mục PMID 35219395: U+2008 → dấu
cách thường).

**Nguyên nhân:** lớp ký tự dấu nghìn trong `tools/tom_tat_endnote_vi.py::_cac_so` viết bằng KÝ TỰ TRẦN, chỉ có dấu phẩy,
U+0020, U+00A0, U+2009, U+202F — thiếu U+2008 cùng các dấu cách Zs khác (U+1680, U+2000–U+2007, U+200A, U+205F, U+3000). Ký tự
vô hình trong mã nguồn nên không ai thấy lớp đã thiếu gì. Đo trước khi vá (13/11): U+2008, U+2007, U+205F, U+3000, U+1680 đều
lệch theo CẢ hai chiều (tóm tắt đặc biệt / gốc thường ⇒ báo 18, 152; tóm tắt thường / gốc đặc biệt ⇒ báo 18152).

**Vá:** hằng `_DAU_CACH_UNICODE` (viết bằng mã thoát) đổi MỌI dấu cách loại Zs về dấu cách thường TRƯỚC khi tách số; hàm chạy
cho cả tóm tắt lẫn văn bản gốc nên hai phía luôn so cùng một dạng. Luật «số phải có nguyên văn trong gốc» không nới; bẫy đã biết
(năm «2024 120» bị gộp thành 2024120) giữ nguyên cho mọi loại dấu cách. Bản sửa tạm dữ liệu kho của phiên trước vẫn hợp lệ, không
cần đảo lại.

**Kiểm:** `tools/test_tom_tat_may_dau_cach_unicode_20261113.py` (13 ca: hai chiều U+2008, U+202F/U+2009/U+00A0/U+3000, số lệch
thật vẫn bị bắt, ghép nhầm hai số riêng của gốc, bẫy năm + dấu phẩy liệt kê, lớp ký tự phủ ĐÚNG tập Zs của `unicodedata`). Đột
biến: bỏ dòng chuẩn hoá ⇒ 8/13 đỏ; thu hẹp lớp (bỏ U+2000–U+200A) ⇒ 8/13 đỏ; `so_khong_khop` luôn rỗng ⇒ 4/13 đỏ; phục hồi ⇒
xanh. `tools/test_tom_tat_may_tham_khao_20261013.py` + `tools/test_tom_tat_endnote_vi_20261013.py` vẫn đạt.

**Bẫy khi vá (cho agent):** công cụ ghi tệp/lệnh Bash của phiên Claude đổi chuỗi `\uXXXX` trong nội dung thành KÝ TỰ THẬT, kể
cả trong heredoc có nháy — tệp test đầu tiên vì vậy chứa ký tự trần dù soạn bằng mã thoát, và một đột biến đầu tiên «không áp
được» (chuỗi tìm đã bị đổi). Sau khi ghi, kiểm bằng `unicodedata.category(c) == "Zs"` trên tệp; dựng dấu gạch ngược bằng
`chr(92)` khi cần viết mã thoát qua lệnh.

**Cùng họ với 29/10** (`2026-10-29-phan-cach-nghin-u2008.md`): lần đó vá U+2007/U+2008 ở `_chuan_so` của cổng ⑨
(`tools/tom_tat_chung_cu_word.py`) nhưng KHÔNG soát công cụ anh em có chốt số tương tự ⇒ `_cac_so` của tóm tắt máy giữ lỗi thêm
hai tuần. Bài học: vá một bộ tách số thì grep mọi bộ tách số khác (`re.sub(r"(?<=\d)[`) trong `tools/`. Cổng ⑨ không đổi lần này
(cố ý KHÔNG gộp dấu cách thường — luật 19/10 cho bảng PDF; lớp của nó vẫn thiếu U+1680, U+2000–U+2006, U+200A, U+205F, U+3000 —
chưa gặp trong abstract/toàn văn đã đo).
