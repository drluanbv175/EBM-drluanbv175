# PROMPT PHA R — CỔNG NGHIÊN CỨU G0–G10: TỰ ĐỘNG TỐI ĐA, NGƯỜI GIỮ ĐÚNG 6 CHỮ KÝ

**Tự soạn theo yêu cầu bác sĩ 15/08/2026; tự thi công ngay trong phiên.**
**Nền:** audit cùng ngày — 2 verifier lớn PASS · quality-gate phủ 10/11 (thiếu G6) ·
8 cổng tự chấm trong `run_gX_auto` · lệnh tài liệu dùng `python` (máy chỉ có `python3`).

## 0. VAI TRÒ & BẤT BIẾN
Bạn là Kỹ sư tự động hoá cổng nghiên cứu. **Tự động tối đa = máy làm MỌI THỨ
trừ 6 chữ ký người thật** (G2 IRB · G4 SAP · G5 khoá dữ liệu · G8 phản biện ·
G9 liêm chính · G10 PI). CẤM: mở/nới cổng ký, tự điền xác nhận đời thực, mock
làm dữ liệu thật (I1–I8 + BH01–BH50 giữ nguyên). Mỗi lô: báo cáo 6 dòng; lô sau
chỉ chạy khi lô trước không FAIL.

## LÔ R1 — ĐÓNG LỖ G6 (việc chính)
`g6_quality_gate.py` theo đúng khuôn anh em (G3/G8): nhóm AUTO đối chiếu
**kết quả ↔ SAP ĐÃ KHOÁ** — (a) DB lock có trước mọi artifact phân tích;
(b) MỌI kết cục chính/phụ của SAP có mặt trong kết quả (chống selective
reporting); (c) tham số khớp SAP (alpha/model); (d) phân nhóm NGOÀI SAP phải
mang nhãn post-hoc (chống HARKing); (e) effect phải đủ cặp ước lượng+CI;
(f) guardrail nền chạy lại trên artifact thật. Nhóm HUMAN: thống kê viên xác
nhận. 3–4 trạng thái rời nghĩa như G3. Tự chạy cuối `run_g6_auto` (không đổi
exit-code hợp đồng cũ). Test + mutation ≥2 phép. Đăng ký `audit_research_gates`
(required=False như G3/G8 — nâng phải sửa đồng thời fixture).

## LÔ R2 — VỆ SINH VẬN HÀNH
Sửa mục "Lệnh" CLAUDE.md `python` → `python3` (đúng máy thật). Hai thư mục
exports rỗng (`T-G5`, `test-study-tmp`) → dời `exports/_rac/` (không xoá — giữ
truy vết), ghi chú lý do.

## LÔ R3 — MỘT CỬA NGHIÊN CỨU (march tự động tới cổng người)
`tools/research_march.py --study <mã>`: đọc trạng thái thật (ledger + checkpoint
+ study_readiness), chạy LIÊN TIẾP mọi `run_gX_auto` máy-làm-được kế tiếp, DỪNG
ĐÚNG cổng người kế tiếp và in "VIỆC CẦN NGƯỜI" (role + lệnh approve chính xác).
`--dry-run` in kế hoạch. Không bao giờ gọi `approve_gate` hộ người. Đây là bản
nghiên cứu của `ops/orchestrator.py` bên lâm sàng.

## LÔ R4 — ĐỐI CHIẾU AI SciSpace (học breadth, giữ cổng)
So 6 năng lực SciSpace-class (hỏi-đáp y văn có trích dẫn · đọc/moi PDF · bảng
trích xuất đa bài · viết có trích dẫn · paraphrase · tìm bài liên quan) với hệ
agent hiện có; ghi bảng tương đương + khoảng trống THẬT vào báo cáo. Chỉ bổ
khuyết thứ có giá trị nghiên cứu thật, không nhân bản tính năng thương mại.

## LÔ R5 — CHỨNG MINH ĐẦU-CUỐI: một nghiên cứu HOÀN CHỈNH qua các cổng
Đề tài `synthetic_test` (cơ chế admin synthetic-only 15/07 — CHỈ hợp lệ cho đề
tài thử): march G0→G10, dữ liệu TỔNG HỢP, ký bằng khoá synthetic đúng cơ chế;
mọi artifact + ledger + gói G10 phải sinh THẬT. Đây là bằng chứng "thực hiện
được một nghiên cứu hoàn chỉnh theo các cổng" — và phải ghi RÕ: đề tài thật vẫn
cần IRB/PI/thống kê viên/phản biện THẬT ký từng cổng.

## LÔ R6 — KHOÁ & GIAO
BH mới cho hành vi G6 (mutation-tested) · chạy lại 2 verifier + pytest liên quan
· commit 2 repo · báo cáo cuối theo bảng nghiệm thu.

**Nghiệm thu:** 11/11 cổng có quality-gate tự chạy · march dừng đúng cổng người
· 1 đề tài synthetic đi trọn G0→G10 có gói · 0 chốt BH đỏ · Ed25519 ghi nhận là
việc CHỜ BÁC SĨ duyệt riêng (đổi quy trình ký — ngoài phạm vi tự động hoá).
