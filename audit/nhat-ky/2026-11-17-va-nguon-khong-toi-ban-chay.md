# 17/11/2026 — Vá ở nguồn không tới bản chạy: cổng kiểm lạc chủ đề trơ dù PR đã gộp (BH179)

**Mã:** BH179 · cùng họ BH09 («Skill sửa ở nguồn tới được nơi chạy»), BH11 (phát hiện), BH41
(công cụ không ai gọi thì không tồn tại).

## Chuyện gì xảy ra

PR #402 bật cổng kiểm lạc chủ đề (`--check-topic`) trong `xuat_goi_cap_nhat.py` và vá
`check_topic_relevance.py` ở nguồn chuẩn `sync/skills/cap-nhat-chung-cu-y-khoa/tools/` (đọc
`ANTHROPIC_API_KEY` từ kho bí mật, model `claude-sonnet-5-5`); PR #405 thêm nhật ký sức khoẻ
`~/.ebm-api-claude.json` + giác quan ⑦r. Cả hai đã gộp, và phiên báo bác sĩ «chuỗi đã khép kín».

Sai trên máy thật. Đo 17/11/2026 13:2x:

- `tools/ban_sao_tran.py::duong_cong_cu_pipeline` ƯU TIÊN `EBM-Dashboards/tools/` (ngoài git),
  chỉ lùi về bản `sync/skills/` khi bản kia vắng.
- `EBM-Dashboards/tools/verify_dashboard.py` (~dòng 2045) chèn `dirname(__file__)` vào đầu
  `sys.path` rồi `import check_topic_relevance` ⇒ luôn nạp bản cạnh nó.
- Bản đó còn cũ (229 dòng, khác nguồn 91 dòng): chỉ `os.getenv("ANTHROPIC_API_KEY")`, khoá trên
  máy này không có trong môi trường shell ⇒ chạy thật in
  `⚠ Kiểm chủ đề (--check-topic): BỎ QUA — Thiếu ANTHROPIC_API_KEY`. Model còn `claude-sonnet-4-6`.
- `~/.ebm-api-claude.json` (chỉ bản mới ghi được) CHƯA HỀ tồn tại ⇒ bản mới chưa từng được gọi.
- `EBM_MASTER/skill_assets/check_topic_relevance.py` cũng cũ.

Bằng chứng «đã bật» của phiên trước là lượt chạy THẲNG vào bản `sync/skills/`, không qua dây chuyền.

## Vì sao không ai thấy

- BH11 ĐÃ phát hiện: lượt chốt nền 12:49 (HEAD `f400e17c`) báo `✗ BH11` — 40 phút trước khi vá tay.
  Nhưng hook đầu phiên in kết quả CŨ 49 giờ («đang đo lại»), kết quả mới chỉ nằm trong
  `state/chot-hoi-quy-gan-nhat.json`.
- Chỉ `surveillance_scan.py` có đường TỰ VÁ (`tools/dong_bo_scanner_giam_sat.py`, gọi trong
  `tu_sua_chua.py`). 15 tool còn lại của nguồn: lệch thì BH11 báo, không gì vá.

## Cách vá

1. Vá tay ngay (13:30): chép nguồn sang hai bản chạy, sao lưu `.bak-20261117-133018`. Bản chạy chỉ
   có 4 dòng riêng — đúng bản cũ của 4 chỗ #402 sửa; nguồn là tập cha ⇒ ghi đè an toàn. Chạy lại qua
   dây chuyền: nhật ký `ok`, `✓ Kiểm chủ đề: 13/13 item đều khớp chủ đề dashboard.`, cổng PASS.
2. Vá cấu trúc: `tools/dong_bo_scanner_giam_sat.py` (giữ tên vì `tu_sua_chua`, BH174, CLAUDE.md,
   agents/A2·A10 gọi tên này) đổi từ MỘT tệp viết cứng sang TỰ DÒ mọi `*.py` của nguồn chuẩn, đích là
   ĐÚNG hai nơi BH11 canh (`EBM-Dashboards/tools`, `EBM_MASTER/skill_assets`) + riêng
   `surveillance_scan.py` → dark-analyst (hợp đồng ESD02). Giữ nguyên luật (a)/(b)/(c); luật (c) nay
   hỏi `git log` theo ĐÚNG tệp nguồn tương ứng (trước viết cứng đường dẫn surveillance_scan).
   Kiểm trong repo thật: bản chạy cũ (blob `c62f60e4…`) chính là một phiên bản đã commit của nguồn ⇒
   luật (c) tự vá. Có công cụ này từ trước thì ca #402 đã tự lành ở đầu phiên kế tiếp.

Không thêm chặn commit cho bản ngoài git: ca 01/09 (bác sĩ bị chặn commit khoá Ed25519 vì một bản
OneDrive lệch) cho thấy chặn commit vì tệp không thuộc commit là tốn kém; tự vá mỗi phiên + BH11 đỏ là đủ.

## Kiểm hồi quy

- `tools/test_dong_bo_cong_cu_ban_chay_20261117.py` — 12 chốt, gồm dựng lại ca #402 trong kho git tạm
  (tool không phải surveillance_scan, một dòng có sẵn bị SỬA), phạm vi trùng BH11 (đọc `NOI` bằng AST),
  `tu_sua_chua` gọi `--ap-dung` (AST trên `VIEC_MAY`).
- BH179 trong `tools/chot_hoi_quy_bai_hoc.py` — khoá ĐƯỜNG TỰ VÁ; phần phát hiện vẫn là BH11.
- Đột biến 6/6 bị bắt (luật c cứng theo surveillance · bỏ EBM_MASTER · luật b không giữ dòng riêng ·
  dark-analyst đồng bộ đại trà · tu_sua_chua bỏ --ap-dung · danh sách viết cứng); phục hồi khớp byte,
  xanh lại.
- Trọn bộ chốt bài học trên worktree: 140 ✓ · 39 ⚪ (thiếu engine y khoa) · 0 ✗. 31 tệp kiểm liên quan:
  292 đạt, 1 bỏ qua.

## Bài học

Bằng chứng «đã bật» phải là lượt chạy QUA DÂY CHUYỀN (đúng resolver, đúng `sys.path`), không phải
qua bản nguồn. Dấu hiệu rẻ nhất là thứ CHỈ bản mới sinh ra được (ở đây: `~/.ebm-api-claude.json`).
