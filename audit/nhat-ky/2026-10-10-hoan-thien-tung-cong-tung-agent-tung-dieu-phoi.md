# 10/10/2026 — Hoàn thiện từng cổng · từng agent · từng điều phối: trách nhiệm cấp agent, đánh giá chéo trong bảng trách nhiệm, hai lệnh agent gãy, một test hẹn giờ

Bác sĩ giao: «Tiếp tục hoàn thiện từng cổng từng Agent và từng điều phối» (tiếp theo «điều phối cổng chịu trách nhiệm
kết quả cổng», `2026-10-09-trach-nhiem-dieu-phoi-cong.md`).

## Đo trước khi sửa (10/10)

1. **Từng điều phối:** đối chiếu mọi lệnh `python3 tools/…` trong 11 `dieu-phoi-gN.md` với argparse thật — 0 lệch.
2. **Từng agent:** quét mọi tài liệu agent (kể cả lệnh viết nhiều dòng):
   - `quan-ly-du-lieu.md` dạy khoá dữ liệu bằng `--approved-by <PI>` — `lock_analysis_dataset.py` KHÔNG có cờ này
     (lệnh chết ở argparse), lại thiếu `--reviewer-role/--reviewer-ref` và 6/10 cờ `--confirm-*`.
   - Guardrail BẮT BUỘC của cả 65 tài liệu agent (`enforce_agent_guardrails.NEW_RUT_BAI`) + skill cập nhật chứng cứ
     dạy `check_citation_retraction.py --pmid <PMID…>`; công cụ chỉ có `--pmids` nhận MỘT chuỗi nối phẩy ⇒
     `--pmid 1 2` chết «unrecognized arguments» (mã 2) — đúng ở bước tra rút bài bắt buộc (đo: mã 2).
   - 23 agent làm/chấm chéo nhiệm vụ cổng KHÔNG biết mình chịu tiêu chí nào (chỉ điều phối có bảng 4b).
3. **Từng cổng:** 10 nhiệm vụ KHÔNG gắn tiêu chí máy nào (G1-T4, G1-T5, G2-T2, G3-T2, G3-T3, G4-T2, G6-T2, G6-T3, G7-T2,
   G10-T3) — chất lượng đầu ra chỉ có thể bảo đảm bằng đánh giá chéo, nhưng bảng trách nhiệm không đọc biên bản đánh giá.

## Vá

Repo y khoa (drluanbv175/medical-ebm-automation#101, xếp chồng trên #100):
- `check_citation_retraction.py`: `--pmids`/`--pmid`, nhiều giá trị cách trắng và/hoặc nối phẩy, khử trùng giữ thứ tự.
- `hoi_dong_cong.py`: ô chủ CÓ ĐIỀU KIỆN «A|B» (G2-AUTO-07 kế hoạch an toàn: RCT ⇒ `an-toan-nghien-cuu`, còn lại ⇒
  `dao-duc-dang-ky`); `trach-nhiem` đọc biên bản đánh giá chéo hợp lệ mới nhất — «trả về sửa» ⇒ `AGENT_CON_VIEC`;
  nhiệm vụ không có tiêu chí máy liệt kê kèm trạng thái đánh giá; chưa «qua» ⇒ «CHẤT LƯỢNG CHƯA ĐƯỢC BẢO ĐẢM» (nói
  thật, không đổi kết luận máy).
- `tools/sinh_tai_lieu_trach_nhiem.py` (mới): SINH mục 4b của 11 điều phối + khối «Trách nhiệm trong hội đồng cổng» của
  23 agent (nhiệm vụ làm · đầu ra · tiêu chí phải đưa tới ĐẠT · hồ sơ chuẩn bị cho người · đầu ra chấm chéo) giữa dấu
  mốc; chế độ kiểm mã 1 khi lệch. Test: tài liệu khớp bản sinh, idempotent, từng agent thấy đúng nhiệm vụ/tiêu chí.
- `tests/test_lenh_trong_tai_lieu_agent_20261010.py` (mới): mọi cờ của lệnh `python3 tools/…` trong tài liệu agent phải
  có trong argparse của công cụ (AST, nối dòng «\\», bỏ dấu trích dẫn) — bắt đúng bản `quan-ly-du-lieu.md` cũ.

Repo gốc (PR này): 34 tài liệu agent sinh lại (nguồn biên tập), `quan-ly-du-lieu.md` sửa lệnh khoá dữ liệu (10 cờ xác
nhận là lời xác nhận SỰ THẬT của người quản lý dữ liệu/PI — agent soạn lệnh, người tự chạy), `_HOI-DONG-CONG.md` §1b
mục 6–8, và bản vá test hẹn giờ (dưới).

**Test hẹn giờ (phát hiện khi chạy bộ test gốc):** `tools/test_do_khong_ban_cay_20261003.py::
test_main_khong_ghi_khi_chi_thoi_gian_troi` đỏ từ 09/10 23:28 — `main()` so với GIỜ THẬT, gương mẫu cố định 02/10 ⇒ đủ
7 ngày thì nhánh làm mới định kỳ bật. Chốt «bây giờ» = 1 ngày sau gương. Tách PR riêng từ master
(drluanbv175/EBM-drluanbv175#141) để gộp trước — từ nay mọi PR gốc chạy lại CI đều đỏ nếu chưa có bản vá.

## Đo trên C1a (chỉ đọc)

Bảng trách nhiệm nay đọc biên bản hội đồng: G0 chuyển `AGENT_XONG_CHO_NGUOI` → `AGENT_CON_VIEC` vì biên bản đánh giá
chéo 07/10 còn hiệu lực TRẢ VỀ SỬA G0-T3/G0-T4 (G0-T1/T2 bất đồng) — việc hội đồng giao chưa ai làm. «Chất lượng chưa
được bảo đảm»: G1-T4 · G3-T2 · G3-T3 · G6-T3 · G7-T2 · G10-T3 (chưa đánh giá chéo).

## Kiểm

- Test mới: 37 (bộ sinh + đánh giá chéo + chủ có điều kiện) · 4 (lệnh tài liệu agent) · 7 (PMID nhiều giá trị).
- Đột biến **14/14** bị bắt (chủ có điều kiện chọn sai ×2 · bỏ lựa chọn khỏi tập có tiêu chí · bỏ việc khi trả về sửa ·
  liệt kê nhiệm vụ không áp dụng · «qua» vẫn cảnh báo · lấy biên bản cũ nhất · không tìm dấu mốc · bỏ cột hồ sơ người ·
  không thoát «|» · công cụ rút bài một giá trị · bỏ khử trùng · máy quét không nối dòng · máy quét bỏ qua cờ sai).
- `pytest tools/` gốc: 2679 qua (sau vá hẹn giờ).
