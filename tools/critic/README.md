# tools/critic — CRITIC THẬT NGOÀI PHIÊN (Hạng mục A)

**[PROTOTYPE — cần môi trường hỗ trợ subagent + BS duyệt governance trước khi chạy trên dữ liệu thật]**

Biến agent `tham-dinh-dau-ra` (chốt kiểm 2 lớp: liêm chính R1–R7 + chất lượng Med-PaLM Q1–Q7 cho gói lâm sàng) thành critic có thể chạy ở
**NGỮ CẢNH TÁCH** (một phiên Claude thứ hai), thay vì chỉ self-check trong cùng phiên.

## File trong thư mục
| File | Vai trò |
|---|---|
| `tham-dinh-dau-ra.standalone.md` | Bản TỰ CHỨA của agent — chạy được một mình; chỉ cần dán `BẢN_NHÁP`. Hợp đồng I/O cứng. |
| `critic-protocol.md` | Quy trình gọi critic như subagent/phiên tách (Task tool) + giới hạn "giảm mù chung, không khử". |
| `PATCH-nhac-truong.md` | Dòng cần dán thêm vào 2 nhạc trưởng (vì `.claude/agents/` bị khóa ghi trong phiên này). |

## Vì sao cần thư mục này (vượt "trần .md")
Bản gốc `tham-dinh-dau-ra.md` là chốt kiểm **cùng phiên/cùng mô hình** → "độc lập về vai, không về tiến trình".
Critic ngoài phiên giảm **mù chung (shared blind spots)** bằng cách bỏ ngữ cảnh phiên soạn gói.
**Giới hạn thẳng:** cùng họ mô hình → **GIẢM, KHÔNG KHỬ** thiên lệch hệ thống. Chốt kiểm thật sự độc lập
cần bộ máy khác họ/người duyệt — đó là **[CẦN MÔI TRƯỜNG HỖ TRỢ]**, chưa khẳng định đã có.

## Cách chạy NGAY (không cần cài gì)
Cách chắc chắn có "ngữ cảnh tách" nhất hiện nay, không phụ thuộc runtime:
1. Mở **một phiên Claude MỚI** (Cowork/Claude Code/Claude.ai).
2. Dán **toàn bộ** `tham-dinh-dau-ra.standalone.md`.
3. Dán `BẢN_NHÁP = <gói đầu ra cần soi>`.
4. Nhận lại khối R1–R7 (+ Q1–Q7 nếu gói lâm sàng) + PHÁN ĐỊNH + danh sách 🔴 (Q2/Q5 đỏ → chuyển bác sĩ).

Khi runtime có **Task tool/subagent** (Claude Code/Cowork): nhạc trưởng tự phát lệnh Task gọi critic —
phần này **[CẦN MÔI TRƯỜNG HỖ TRỢ]**, xem `critic-protocol.md` §4.

## Governance bất biến
- Critic CHỈ kiểm; không sửa hộ; không tạo nội dung mới; **KHÔNG PII**.
- "ĐẠT" ≠ được áp dụng cho BN: vẫn dừng **Cổng A/B** (lâm sàng) hoặc **G2/G4/liêm chính tác giả** (nghiên cứu).
- Kết mọi đầu ra: **"Cần bác sĩ kiểm chứng."**

## Trạng thái
Prototype CHẠY ĐƯỢC (spec tự chứa + protocol). CHƯA vận hành tự động ở phiên tách — cần Task tool/subagent
của runtime + bác sĩ duyệt cơ chế. Không thay đổi số đếm agent (không thêm agent .md mới vào `.claude/agents/`).
