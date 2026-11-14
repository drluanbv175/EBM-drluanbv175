# 14/11/2026 — K4 xanh giả vì luật «mệnh đề giả định» bắt quá rộng (sửa sau thẩm định PR #359)

Bổ sung cho `2026-11-14-va-lop-kiem-ngu-nghia-k3b-k4b.md`. PR #359 đã được gộp trước khi bản thẩm định đối kháng
về tới nơi, nên phần sửa đi thành PR nháp mới từ `master`. Mọi phép vẫn ở mức CẢNH BÁO. Chuyển sang CHẶN là việc của
bác sĩ.

**Nguyên nhân (mức vừa).** PR #359 thêm luật: tín hiệu ngược chiều đứng sau «if/whether/unless/in whom/when» là mệnh
đề giả định, K4 bỏ qua. Chỉ cần dấu đó xuất hiện ở BẤT KỲ đâu phía trước trong câu là đủ, kể cả khi nó thuộc một mệnh đề
phụ đã đóng bằng dấu phẩy. Hệ quả là K4 trấn an sai (xanh giả) đúng trên kiểu câu kết luận phổ biến nhất của thử nghiệm
âm tính. Bốn câu tái hiện đều bị bỏ:
- «When added to guideline-directed therapy, drug X did not reduce…»;
- «In patients in whom PCI was performed, drug X did not reduce MACE.»;
- «Whether given early or late, drug X did not improve the primary outcome.»;
- «When used as first-line therapy, drug X was not superior to placebo for the primary outcome.»

Luật này còn đi vòng qua `_CHINH`: câu nói về kết cục CHÍNH không bị bộ lọc kết cục phụ bỏ, nhưng vẫn bị luật giả định
bỏ. Dòng in ✓ thì ghi lý do bỏ là «kết cục phụ/an toàn», tức là sai lý do. Trên bộ đệm 298 nguồn thật, luật bỏ 6 câu và
cả 6 đều là giả định thật, nên số đo của PR không lộ lỗi.

**Cách vá** (`tools/kiem_quan_the_chieu.py`, `tools/kiem_cheo_ngu_nghia.py`):
1. `_nguoc_sau_gia_dinh`: chỉ bỏ câu khi tín hiệu nằm TRONG mệnh đề điều kiện, tức là không có dấu phẩy giữa dấu điều
   kiện gần nhất và tín hiệu. Câu có `_CHINH` (primary outcome/end point/composite) không bao giờ bị bỏ.
2. Nhãn in: «bỏ qua N câu chỉ về kết cục phụ/an toàn hoặc mệnh đề giả định». Mục phủ định («KHÔNG tầm soát…») có dòng in
   riêng: «câu ngược chiều của nguồn CÙNG chiều với mục». Trước đây dòng này cũng mang nhãn «kết cục phụ».
3. `_PHU` (mức thấp): bỏ nhánh thừa «secondary analyses of (the) secondary». Nhánh này không bắt thêm kết cục phụ nào,
   nhưng lại làm câu thiết kế «secondary analyses of secondary prevention trials» bị coi là kết cục phụ.
4. `doan_cua_muc` (mức thấp): đoạn của mục CUỐI đóng ở tiêu đề phần đuôi «NGUỒN VÀ LIÊM CHÍNH DỮ LIỆU». Đó là phần mà
   `build_dashboard_docx.py` in ngay sau mục cuối. Đo trên 303 Word HTML thật: tiêu đề có mặt ở 303/303, đúng một lần,
   luôn sau mốc mục cuối. Tiêu đề «Tài liệu tham khảo»/«Phụ lục» không dùng làm mốc được, vì chúng nằm trong bảng của
   từng mục (299 và 29 tệp). Mốc chỉ được tìm SAU mốc mục cuối, nên mục lục có nhắc tên phần đuôi cũng không cắt nhầm.
   Giới hạn: sản phẩm không có tiêu đề đó thì đoạn mục cuối vẫn kéo tới hết tài liệu. Giới hạn này đã ghi ở docstring.

**Số đo 14/11/2026** (cùng hạt giống 20261114, 115 dashboard PASS, bộ đệm 298 nguồn, ngoại tuyến):
- `do_nhay_kiem_ngu_nghia.py` cho mọi con số TRÙNG với báo cáo `do-nhay-dot-bien-20261114c` của PR #359. Chỉ băm mã ở đầu
  báo cáo đổi; báo cáo đã ghi lại theo mã mới. Cụ thể: K4 106/107, K4b 145/581, đối chứng mức dashboard K1/K2/K4 45/97,
  K3 102/115 (888/3530 dòng). Bốn câu phản ví dụ không có trong bộ đệm thật, nên lỗ hổng không làm lệch số đo. Bản vá bịt
  một đường lọt im, không đổi báo động trên mục thật.
- Luật giả định trên bộ đệm thật vẫn bỏ đủ 6/6 câu giả định.
- Bộ vàng (`bo_vang_kiem_ngu_nghia.py do`, mã c248fbb so với bản vá): đầu ra giống hệt. K1 báo động giả 0/20, K4 1/20,
  K3b 0/18 (bỏ lọt 1/1), K4b n=1.

**Kiểm hồi quy.**
- Thêm 6 test ngoại tuyến vào `tools/test_lop_kiem_ngu_nghia_20261114c.py`. Cả 6 đỏ trên mã c248fbb và xanh sau bản vá.
- Bộ test `tools/` (python -B, đã xoá `__pycache__`): 4806 passed, 38 skipped. ruff sạch.
- Kiểm đột biến 7 phép, 7/7 đỏ đúng test đích. Có sao lưu `cp -p`, `cmp` khớp trước, khôi phục xong `cmp` khớp sau mỗi
  phép. Các phép:
  - bỏ kiểm dấu phẩy;
  - bỏ rào `_CHINH`;
  - khôi phục nhánh thừa `_PHU`;
  - nhãn in cũ;
  - bỏ dòng in mục phủ định;
  - đoạn mục cuối kéo tới hết tài liệu;
  - tìm mốc kết thúc từ đầu tài liệu.

_Cần bác sĩ kiểm chứng._
