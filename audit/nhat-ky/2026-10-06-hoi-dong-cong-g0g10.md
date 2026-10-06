# 06/10/2026 — Hội đồng cổng G0–G10: điều phối cổng · đánh giá chéo giữa các agent · tranh biện trước kết luận

Bác sĩ yêu cầu: mỗi cổng G0–G10 có agent cho từng nhiệm vụ cụ thể, mỗi cổng có điều phối và có điều phối tổng, có cơ
chế đánh giá chất lượng đầu ra giữa các agent và cơ chế tranh biện trước kết luận cuối. Xếp chồng trên gốc #130 / y
khoa #92.

**Dựng:** 14 agent nghiên cứu (50 → 64): 11 điều phối cổng `dieu-phoi-g0`…`dieu-phoi-g10` dưới điều phối tổng
`dieu-phoi-nghien-cuu` (vẫn là owner DUY NHẤT); `giam-khao-cong` (rubric RQ1–RQ8); `phan-bien-tranh-bien` +
`trong-tai-tranh-bien` (≤2 vòng). Hạ tầng `_HOI-DONG-CONG.md`. Tầng máy-kiểm-được ở repo y khoa
`tools/hoi_dong_cong.py`: danh mục nhiệm vụ/ma trận chấm chéo/điểm quyết định (nguồn sự thật — test đối chiếu bảng trong
từng `dieu-phoi-gN.md`), kiểm LUẬT biên bản (vai tách bạch, căn cứ kiểm được, trần vòng, chấp nhận phản đối thì không
giữ kết luận, không tự tuyên bố qua cổng, không PII, băm tài liệu được xét), `cham-song` chỉ đọc, tóm tắt theo cổng —
nối vào `study_readiness` và đài kiểm soát như TƯ VẤN (không đổi trạng thái cổng). Workflow Claude Code
`.claude/workflows/hoi-dong-cong.js` + `dieu-phoi-tong-hoi-dong.js` (trần vòng, trần agent, không cắt im lặng; biên bản
dựng từ đầu ra có cấu trúc, không diễn giải lại).

**Số đo chi phí (dùng để đặt chính sách §5):** một subagent mới mang ~250 nghìn token nền (lỗi «Prompt is too long»
của agent tra tài liệu: ~263 nghìn token yêu cầu, hội thoại chỉ ~18 nghìn) ⇒ hội đồng đủ vai ≈ 1–3 triệu token/cổng ⇒
triệu tập phải hỏi bác sĩ (`CLAUDE.md` §0.6); chạy thử `chay_thu` của workflow: 0 agent, 0 token.

**Lộ khi dựng (bài học):**
1. Bộ đọc README của control plane chỉ lấy agent ĐẦU TIÊN mỗi dòng bảng ⇒ dòng gộp nhiều agent làm 9 điều phối cổng
   thành «unknown» — mỗi agent một dòng.
2. Viết tắt «`dieu-phoi-g0` … `dieu-phoi-g10`» trong doctrine nhạc trưởng làm `verify_agent_routing` báo g1–g9 MỒ CÔI
   (bộ quét chỉ thấy token trong backtick) — liệt kê đủ.
3. Biên bản có căn cứ tệp:dòng bị báo «HỎNG» khi tài liệu được xét đổi — đúng ra là «CŨ»: so băm TRƯỚC, biên bản cũ
   vẫn kiểm cấu trúc/thẩm quyền/PII nhưng không đo lại dòng.
4. Ký cổng cứng: `approve_gate.py` đòi artifact theo cổng (G5 = `G5_checkpoint.json`, không phải manifest khoá) — tra mã
   trước khi viết doctrine.

**Kiểm:** đột biến 52/56 + bù 6/6 (lọt: mã rubric lạ, «cần sửa» thiếu nhận xét, «..»/liên kết ra ngoài, biên bản đánh
giá cũ có căn cứ dòng — đã thêm test); governance 64 agent 0 lỗi; mirror Codex khớp; định tuyến 0 mồ côi.

Cần bác sĩ kiểm chứng.
