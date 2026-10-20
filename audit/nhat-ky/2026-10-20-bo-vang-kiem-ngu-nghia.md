# 20/10/2026 — Bộ vàng kiểm chéo ngữ nghĩa: phiếu gắn nhãn · ghi nhãn từ lời bác sĩ · đo báo động giả

**Bối cảnh.** Bác sĩ hỏi hệ cập nhật chứng cứ đã đạt chuẩn chưa; đo sống báo ba điểm chưa đạt, điểm thứ ba: K1–K4
(`kiem_cheo_ngu_nghia.py`, `kiem_quan_the_chieu.py`) chỉ CẢNH BÁO vì thiết kế `audit/16` (duyệt 25/09/2026) đòi đo tỉ lệ
báo động giả trên bộ vàng có nhãn bác sĩ trước khi tính chặn — mà tới 20/10 bộ vàng chưa từng được soạn. Bác sĩ: «Giải quyết
3 vấn đề chưa đạt».

**Nguyên nhân gốc.** Có lệnh soạn ứng viên (`--ung-vien-bo-vang`) nhưng KHÔNG có đường nào đưa ứng viên tới bác sĩ, nhận
nhãn về, và đo — một công cụ không ai gọi thì với dây chuyền nó không tồn tại (CLAUDE.md §6.4).

**Cách vá.** `tools/bo_vang_kiem_ngu_nghia.py`:
- `phieu [--online]` — Word Times New Roman ở `EBM-Dashboards/derivatives/` (ngoài git): quần thể · khuyến cáo · nguồn ·
  tóm tắt PubMed (bỏ khối thông tin tác giả, che email). Phiếu MÙ: không in K1/K4, `co_dieu_kien`, `gradeLevel`.
- `ghi --loi "<nguyên văn>" [--ap-dung] [--ghi-de]` — đọc «N: Đ Đ Đ ghi chú»; chạy khô mặc định; lưu nguyên văn lời bác sĩ
  vào từng nhãn; không ghi đè nhãn đã có; phần nào không đọc được (thiếu chữ, trùng số, ngoài phạm vi) ⇒ mã 1, không ghi gì.
- `do [--online]` — K1 so «đúng quần thể», K4 so «đúng chiều» bằng CHÍNH `kiem_quan_the_chieu.kiem_muc`; mẫu số 0 ⇒ CHƯA ĐO.
  K3 không đo bằng nhãn «đủ điều kiện» (K3 hỏi bản xuất có giữ cụm điều kiện của MỤC; nhãn hỏi mục có giữ đủ điều kiện của
  BÀI GỐC) — nhãn đó đếm lỗi «rụng điều kiện» mà hiện chưa phép kiểm nào bắt.
- Tệp ứng viên `quality/eval/kiem-cheo-ngu-nghia/bo-vang.cho-duyet.json` (20 mục, nhãn null) vào git cạnh bộ vàng
  tra-điểm-khám. Chuyển K1/K4 sang CHẶN vẫn là quyết định của bác sĩ sau khi xem số đo; công cụ không tự chuyển.

**Kiểm hồi quy.** `tools/test_bo_vang_kiem_ngu_nghia_20261020.py` (24 ca) — gồm bất biến «mọi nhãn khác null trong tệp
đã commit phải kèm `loi_bac_si`». 12 phép đột biến đều đỏ (lần đầu 3 sống sót: một tương đương, hai là lỗ thật của bộ test
— mục chưa nhãn bị đếm thêm vào «chưa có nguồn»; lời lẫn phần đọc được và phần rác vẫn ghi phần đọc được — đã thêm ca).
Đo thật 20/10: `phieu --online` ⇒ 20 mục, 15/15 PMID có tóm tắt; `do` ⇒ CHƯA ĐO (20 mục chưa nhãn).
