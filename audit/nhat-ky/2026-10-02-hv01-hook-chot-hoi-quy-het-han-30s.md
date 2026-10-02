# 02/10/2026 — Hook chốt hồi quy hết hạn 30 giây ở 18/19 phiên: «bị cắt giữa chừng» đọc giống hệt «mọi chốt xanh» (HV-01, BH147)

**Triệu chứng.** Kiểm toàn diện 02/10: hook `SessionStart` chạy `chot_hoi_quy_bai_hoc.py --im-khi-on` với `timeout: 30`, nhưng bộ chốt cần
46–55 giây trên máy thật ⇒ hook hết hạn ở 18/19 phiên từ 24/09 (lưới an toàn mù ~8 ngày). Lệnh hook kết thúc bằng `; true` và chế độ
`--im-khi-on` im lặng khi không có gì đỏ, nên «bị cắt giữa chừng» và «mọi chốt xanh» cho CÙNG một đầu ra rỗng — không ai thấy.

**Nguyên nhân gốc.** Một cơ chế báo động mà trạng thái «không chạy xong» và «chạy xong, không có gì» in ra giống nhau (CLAUDE.md §0.2:
không đo được ≠ ổn). Độ trễ thật của bộ chốt tăng dần theo số chốt (nay 145 chốt) mà trần hook đứng yên.

**Vá.** `tools/chot_hoi_quy_nen.py` + `sync/hooks-sessionstart.json`: hook chỉ ĐỌC `state/chot-hoi-quy-gan-nhat.json` (<1 giây đo thật)
và phóng một lượt `--chay` NỀN (tách tiến trình; khoá `state/` chống chạy chồng, quá 20 phút coi là mồ côi) khi kết quả cũ hơn 6 giờ hoặc
HEAD git đã đổi. Ba trạng thái hiển thị: xanh THẬT còn mới (≤72 giờ) ⇒ im lặng; có chốt đỏ ⇒ in nguyên báo cáo + giờ đo (mã 1); chưa có kết
quả/hỏng/cũ/lượt nền LỖI/dấu thời gian tương lai ⇒ 🟡 «CHƯA ĐO ĐƯỢC… KHÔNG đọc là xanh» (mã 2). Hook cloud (`.claude/hooks/session-start.sh`)
giữ nguyên: nó chạy trọn bộ chốt trong `| head -20` và không dùng nhánh này.

**Đo trên máy thật (worktree).** Lượt đọc đầu: 🟡 CHƯA ĐO ĐƯỢC, mã 2, 0 giây, phóng nền; lượt nền chạy xong sau 21 giây, ghi XANH mã 0; lượt đọc
thứ hai: im lặng, mã 0, 0 giây.

**Chốt BH147** (`tools/chot_hoi_quy_bai_hoc.py`): (a) bản khai hook trong git — đúng MỘT hook chốt hồi quy, gọi bản đọc nền, không gọi trực tiếp bộ chốt trọn,
timeout ≤30; (b) 6 ca `danh_gia`; (c) 5 ca `chay_tron_bo_chot` trên bộ chốt GIẢ (mã lạ/quá hạn ⇒ LOI, không bao giờ XANH; khoá được gỡ; đang có lượt khác ⇒
mã 3 và không ghi đè). Kèm 32 ca pytest `tools/test_chot_hoi_quy_nen.py`. **Kiểm đột biến:** 9/9 bị BH147 bắt (bỏ ngưỡng 72 giờ · chưa đo ⇒ im lặng · mã lạ ⇒ xanh ·
quá hạn ⇒ xanh · bỏ khoá · tin dấu thời gian tương lai · lượt LỖI ⇒ xanh · xoá khoá bất kể còn hạn · hook quay lại chạy trọn); pytest 6/6 đột biến đầu bị bắt;
phục hồi `cmp` đúng. Một lỗi thật bắt được khi viết test: tham số mặc định `TEP_KET_QUA` chốt lúc nạp mô-đun nên test vá hằng không có tác dụng (đọc nhầm tệp thật) —
đổi thành tra lúc gọi.

**Việc của bác sĩ (cài lên máy).** Sau khi merge: `python3 tools/dong_bo_hook_sessionstart.py --ap-dung` (có sao lưu) để `.claude/settings.local.json` nhận hook mới;
máy Windows chạy cùng lệnh. Chưa chạy lệnh này trong PR vì sửa cấu hình hook của máy là quyết định của bác sĩ.
