# 08/11/2026 — Hàng chờ tóm tắt Word ⑨ chỉ nhận chứng cứ ★ Áp dụng – tin cậy cao, mới nhất trước

**Yêu cầu bác sĩ (nguyên văn):** «tóm tắt Word tiếng Việt chỉ với các chứng cứ áp dụng cho thực hành lâm sàng với độ tin cậy cao
và mới nhất».

**Vì sao:** đo 08/11 trên thư viện thật, hàng chờ ⑨ có 1.145 bài (1.124 trích dẫn mới + 21 bản ghi cũ ngoại lệ mốc). Mỗi bài tốn
≈ 0,6–0,9 triệu token cả kiểm chéo, nên hàng chờ không bao giờ cạn; phần lớn là bài tham khảo hoặc mục «Cân nhắc», trong khi bài
nguồn của khuyến cáo «Áp dụng» có chứng cứ mạnh lại nằm lẫn trong đó.

**Vá:** `tools/tom_tat_chung_cu_word.py`
- Chính sách «chỉ ★»: `chi-sao --loi "<nguyên văn>"` ghi `TomTatChungCu/_chi_sao.json` cạnh thư viện (đi theo OneDrive); `--tat` tắt.
  Tệp vắng, hỏng, thiếu lời bác sĩ hoặc `bat` khác `true` ⇒ không lọc (luật 19/10 + ngoại lệ 24/10 giữ nguyên).
- `hang_cho()` khi bật: chỉ giữ bản ghi đạt `gan_tag_endnote.dat_ap_dung_tin_cay` — CÙNG một hàm với tag «★ Áp dụng – tin cậy cao»
  (nguồn chính mục `apply` ở phiên bản dashboard hiện hành, high/moderate, hoặc `na` khi là guideline/nhãn thuốc; không consensus,
  low/vlow, bản cũ). Áp cho cả bản ghi cũ của ngoại lệ mốc. Xếp năm xuất bản giảm dần, rồi recNum giảm dần. Mục mang `sao=True`.
- Bật mà không đọc được dashboard nào ⇒ `ChiSaoKhongDoDuoc` (lớp con của `NgoaiLeKhongDoDuoc`) ⇒ `hang-cho` mã 2, hòm việc ⚪ —
  không bao giờ «0 chờ» xanh giả. Hàng chờ rỗng thì không cần đọc dashboard.
- `hang-cho` in «N trích dẫn ★ Áp dụng – tin cậy cao … mới nhất trước» kèm năm; `tien-do` in dòng chính sách.
- `tools/tu_de_xuat_viec.py`: câu 🛎 ghi «★ Áp dụng – tin cậy cao (mới nhất trước)» khi mọi mục mang `sao`.

**Số đo 08/11 (chạy khô, chưa ghi tệp chính sách):** 1.145 → 105 bài (87 mới + 18 cũ); năm 2026: 20, 2025: 18, 2024: 12.
Bài ngoài ★ vẫn nhận tóm tắt tiếng Việt từ abstract (`tom_tat_endnote_vi.py`, `--tom-tat-vi`) và vẫn phải có toàn văn (bác sĩ 24/10).

**Kiểm:** `tools/test_tom_tat_chi_sao_20261108.py` (15 ca). Đột biến 8/8 đỏ: bỏ lọc ★ · xếp cũ trước · không dashboard ⇒ 0 chờ ·
không đòi lời bác sĩ khi đọc · ★ không áp bản cũ · luật ★ bản sao riêng (không gọi gan_tag_endnote) · hòm việc luôn ghi ★ · ghi
không đòi lời bác sĩ. Bộ test liên quan (tóm tắt, hàng chờ đề tài, hòm việc, gắn tag) 398 đạt.
