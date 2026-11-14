# 14/11/2026 — Chốt doctrine tác vụ lịch báo oan gạch đầu dòng và «tác vụ vào `x`» (sau #363)

**Bối cảnh:** bổ sung cho `2026-11-14-hom-viec-trang-chua-do-va-doctrine-lich.md` (#363, đã gộp 14/11 bản squash 536180b).
Thẩm định đối kháng của #363 chỉ ra hai đường báo oan MỚI do lượt mở rộng regex `_NGU_CANH_TAC_VU`
(`tools/verify_claude_code_repo_alignment.py`, chốt `doctrine_tac_vu_lich`, chạy ở pre-commit cho CLAUDE.md và AGENTS.md).
PR được gộp trước khi lượt sửa kịp đẩy, nên vá đi qua PR mới.

**Nguyên nhân (đã tái hiện trên master 536180b):**
1. Dấu ngăn viết `\s*(?:[:(]|[—–]|-{1,2})?\s*`. `\s*` trước gạch ăn cả xuống dòng, nên gạch đầu dòng markdown «- `tên`» ở dòng
   SAU một dòng kết thúc bằng «tác vụ [từ vựng lịch]» bị đọc thành «tác vụ — `tên`». «Quy trình này không còn là tác vụ⏎⏎-
   `goi-duyet-tuan-ebm`: …» cho FAIL «gọi `goi-duyet-tuan-ebm` là tác vụ lịch nhưng ĐÃ BỎ», trong khi câu nói điều ngược lại.
   «Danh sách tác vụ lịch⏎- `goi-duyet-tuan-ebm`» cũng bị bắt.
2. «lúc|vào» được tính là từ vựng lịch cả khi là cụm CUỐI, ngay trước tên. Ở vị trí đó «vào `x`» nghĩa là «vào trong `x`»:
   «gộp tác vụ vào `goi-duyet-tuan-ebm`», «chép tác vụ lịch vào `x`», «chép tác vụ lúc `x`» đều bị bắt.

Regex trước #363 (`\s*[:(]?\s*`, không có «lúc|vào») không bắt cả hai loại câu ⇒ lỗi do #363. Kho hiện tại chưa dính: so regex
bản #363 và bản vá trên 1802 tệp văn bản đang track, chỉ hai tệp khác (chính tệp test và chú thích trong mã, vì chứa ca thử).

**Vá:**
1. Dấu ngăn thành `(?:\s*[:(]|[^\S\n]*(?:[—–]|-{1,2}))?\s*`: gạch chỉ là dấu ngăn khi CÙNG DÒNG với «tác vụ …»; «:»/«(» giữ
   hành vi cũ (được qua dòng như trước #363). «tác vụ mới —⏎`x`» (gạch cùng dòng, tên ở dòng sau) vẫn bị bắt.
2. «lúc|vào» thành `(?:lúc|vào)(?!\s*(?:[:(—–-]\s*)?`)`: chỉ là từ vựng lịch khi còn một cụm nữa theo sau. «tác vụ lịch vào
   (thứ Hai) `x`», «… lúc 7h `x`», «… vào thứ Hai `x`» vẫn bị bắt.

**Kiểm hồi quy:** `tools/test_hom_viec_trang_va_doctrine_lich_20261114.py` thêm 2 câu âm tính giả (phải bắt) và 5 câu dương
tính (không được bắt): 49 test đạt. 4 đột biến (gạch qua dòng như bản #363; bỏ lookahead của «lúc|vào»; bỏ nhánh gạch cùng dòng;
bỏ hẳn «lúc|vào») đều ĐỎ đúng test rồi khôi phục khớp byte (`cp -p` + `cmp`). Quét tuyến tính: chuỗi 600 nghìn ký tự 0,04 giây;
khối 200 nghìn khoảng trắng/xuống dòng ≤ 0,1 giây. `verify_claude_code_repo_alignment.py` PASS (CLAUDE.md, AGENTS.md hiện tại
không bị báo oan).

**Bài học:** mở rộng một chốt khớp chuỗi phải có ca thử NHIỀU DÒNG trong bộ dương tính; `\s` trong regex đọc văn bản markdown
ăn cả xuống dòng, nên mọi dấu ngăn mới phải hỏi «có được qua dòng không».
