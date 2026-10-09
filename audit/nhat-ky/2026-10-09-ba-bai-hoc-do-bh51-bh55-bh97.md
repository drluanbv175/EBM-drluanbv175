# 09/10/2026 — Ba bài học đỏ BH51 · BH55 · BH97: một báo nhầm của luật R6, hai chốt lạc hậu sau đợt siết G4/G6 04/10

Bác sĩ giao: «Tiếp tục hoàn thiện hệ thống nghiên cứu của tôi». Lượt chốt hồi quy nền (đo 07/10 → 09/10) báo
🔴 ba bài học tái phát. Soát từng mục: KHÔNG mục nào là lỗi engine quay lại — một mục là công cụ đo báo nhầm, hai
mục là chốt còn khẳng định hành vi mà đợt hoàn thiện cổng 04/10 đã CỐ Ý đổi.

## 1. BH55 — luật R6 của `kiem_tuong_thich_da_nen.py` báo nhầm 24/24

**Triệu chứng:** 🔴 «R6 write_text thiếu newline='\n' trong vùng chuỗi-ký» tại `tests/test_g10_hoan_thien_20261005.py:331`,
`:624`, `tests/test_g5_hoan_thien_20261004.py:116`…

**Nguyên nhân:** R6 là regex THEO DÒNG. Ở mẫu
`p.write_text(p.read_text(encoding="utf-8") + "…",` ⏎ `encoding="utf-8", newline="\n")`, dòng đầu có
`write_text(` và `encoding="utf-8")` — nhưng `encoding=` đó thuộc lời gọi `read_text(...)` LỒNG trong đối số; `newline=`
nằm ở dòng kế nên regex không thấy. Ngược lại, lời gọi `write_text(` trải nhiều dòng (encoding và dấu đóng ngoặc ở dòng
khác) thì regex BỎ SÓT vi phạm thật.

**Đo (09/10, 752 tệp vùng ký):** regex 24 🔴 — đọc tay cả 24 đều có `newline="\n"` (báo nhầm 24/24); bản đọc cú pháp 0 🔴.

**Vá:** `dong_r6_vi_pham()` đọc bằng `ast`: một `Call` có `.write_text`, có encoding (từ khoá hoặc ≥2 đối số vị trí), thiếu
newline (từ khoá hoặc ≥4 đối số vị trí) ⇒ vi phạm; `*args`/`**kwargs` không phán (có thể mang newline); miễn trừ
`# da-nen: bo-qua` ở BẤT KỲ dòng nào của lời gọi; dòng báo là dòng chứa `.write_text`. Tệp lỗi cú pháp ⇒ lùi về luật
theo dòng cũ, kèm nhãn «[đọc theo dòng: tệp lỗi cú pháp]» — không bao giờ đọc «parse hỏng» thành «sạch».
Chốt BH55 nay in TỔNG số 🔴 (bản cũ chỉ in 3 dòng đầu nên 24 báo nhầm trông như 3).

**Kiểm:** `tools/test_kiem_tuong_thich_da_nen_r6_ast_20261009.py` (10 ca, gồm ca regex cũ bỏ sót); bộ test cũ của công cụ
vẫn xanh. Đột biến 7/7 bị bắt (bỏ kiểm newline · luôn dùng regex cũ · miễn trừ chỉ xét dòng đầu · lỗi cú pháp coi là
sạch · bỏ đối số vị trí · phán cả `**kwargs` · báo dòng đầu biểu thức thay vì dòng `.write_text`).

## 2. BH51 — chốt khớp chuỗi đã lạc hậu với thông điệp G6-AUTO-01

**Triệu chứng:** «G6-AUTO-01 không còn lấy bằng chứng từ ledger — điểm gọi ledger_approved hỏng (đảo tham số?)».

**Nguyên nhân:** từ 04/10, G6-AUTO-01 (`_g4_da_khoa`) đòi HAI điều: chữ ký G4 trong sổ cái khớp SAP hiện tại VÀ G4 chấm
trực tiếp `PASS_G4_SAP_LOCKED`. SAP của đề tài demo (15/08) không còn qua bộ chấm G4 chặt hơn, nên G6 in nhánh
«có chữ ký nhưng G4 chấm trực tiếp KHÔNG phải PASS_G4_SAP_LOCKED» thay vì «sổ cái (chữ ký thật)…». Chốt chỉ nhận chuỗi sau
⇒ đỏ, dù điểm gọi `ledger_approved` vẫn đúng (G6 vẫn tìm thấy chữ ký).

**Vá:** chốt đòi G6 NHẬN RA chữ ký sổ cái — một trong hai nhánh «sổ cái (chữ ký thật)» hoặc «có chữ ký nhưng G4 chấm trực
tiếp» — và đỏ khi gặp «sổ cái không có chữ ký G4 hợp lệ» (đúng chữ ký điểm gọi bị đảo tham số / sai gốc repo).
Nhánh «có chữ ký nhưng…» qua kèm ghi chú: SAP demo chưa đạt khoá là việc của G4, ngoài bài học này.

**Kiểm:** đột biến trên worktree engine tách rời — B1 đảo tham số `ledger_approved`, B2 sai `repo_root` — cả hai ĐỎ.

## 3. BH97 — vế ② của chốt khẳng định một nhượng bộ G4 đã bị bỏ CÓ CHỦ Ý

**Triệu chứng:** «SAP ĐỦ MỤC, đã điền mà vẫn bị chặn — dương tính giả: ['§4 … VẮNG', '§9 … VẮNG']».

**Nguyên nhân:** fixture của chốt dựng SAP 4 mục và khẳng định «vắng một mục bắt buộc vẫn khoá được» (nhượng bộ cho biến
thể thiết kế, 02/09). G4-01 ngày 04/10 đảo ngược CÓ CHỦ Ý: SAP phải có đủ §1/§2/§4/§5/§9/§10 (`_G4_REQUIRED_SECTIONS`),
được bảo vệ bởi `tests/test_g4_hoan_thien_20261004.py` của repo y khoa. Chốt lạc hậu, không phải engine hỏng.

**Vá:** vế ① giữ nguyên (SAP rỗng phải bị chặn). Vế ② viết lại theo luật hiện hành: lấy danh mục mục bắt buộc từ chính
`_g4_muc_bat_buoc`; sàn §1/§2/§4/§5/§9/§10 phải nằm trong danh mục; SAP đủ mục đã điền ⇒ qua; thiếu BẤT KỲ mục nào ⇒ bị chặn
ĐÚNG mục đó («VẮNG»); placeholder `[CẦN BÁC SĨ]` vẫn chặn. Docstring có khối «ĐÍNH CHÍNH 09/10/2026».

**Kiểm:** đột biến A1 SAP rỗng lọt · A2 trả lại nhượng bộ vắng-một-mục · A3 bỏ kiểm `[CẦN` · A4 chặn oan SAP đủ ·
A5 thu nhỏ danh mục — cả năm ĐỎ; tổng BH51+BH97 7/7, engine khôi phục byte-y-hệt.

## Kiểm tổng (09/10)

- `python3 tools/chot_hoi_quy_bai_hoc.py` trên worktree nối engine: BH51 ✓ (⚪ «kiểm yếu hơn» như cũ — ledger demo ký bằng
  khoá máy khác), BH55 ✓, BH97 ✓. Ba mục khác đỏ CHỈ trong worktree vì thiếu dữ liệu ngoài git (BH43 nền Retraction
  Watch, BH50 log weekly_safety, BH91 mirror `.Codex/agents` bị `.gitignore`) — lượt nền trên cây chính đo chúng xanh.
- `pytest tools/` cấu hình trần (không engine): 2679 qua, 33 bỏ qua.

## Bài học

Một chốt khớp CHUỖI thông điệp sẽ đỏ khi engine đổi lời mà không đổi hành vi — trước khi «vá lại engine», đọc nhánh nào
của engine đã in ra và hỏi «đợt sửa nào đổi nó, có chủ ý không» (`git log -S '<chuỗi>'`). Khi engine đảo một nhượng bộ có
chủ ý, chốt phải được ĐÍNH CHÍNH theo luật mới, không được nới cho xanh và không được kéo engine về luật cũ.
