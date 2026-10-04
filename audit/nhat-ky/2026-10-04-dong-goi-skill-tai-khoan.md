# 04/10/2026 — Skill tài khoản claude.ai: đối chiếu chỉ so SKILL.md, không có đường đóng gói, không giác quan nhắc (BH163)

**Bác sĩ:** «Gộp 124 và đóng gói các skill để cập nhật».

**Đo sau khi gộp #124:**
- Làn «Cloud ↔ repo» báo «giống 5 · lệch bản 20 · chỉ repo 25».
- So cả thư mục skill: `nghien-cuu-y-khoa-chuan-quoc-te` trùng SKILL.md nhưng 7 tệp phụ khác + 1 tệp mới ⇒ thật ra là 4 giống,
  21 cần cập nhật. Bộ skill tài khoản giữ CẢ thư mục đã tải lên (đối chiếu tệp-theo-tệp: 4 skill khớp từng tệp).
- Bộ tài khoản chỉ đổi khi bác sĩ tự tải lên. Repo không có công cụ đóng gói đúng cấu trúc tải lên, và không giác quan nào nhắc
  ⇒ 21/25 skill trên tài khoản đã cũ suốt 25 ngày (cap-nhat-chung-cu-y-khoa v1.15.0 so với v1.53.0).

**Luật tải lên** — nguồn: skill-creator của Anthropic (`scripts/quick_validate.py` + `package_skill.py`, có sẵn trong bộ skill
tài khoản):
- gốc ZIP là thư mục `<tên>/`; đúng MỘT SKILL.md;
- `name` kebab-case ≤ 64 ký tự;
- `description` ≤ 1024 ký tự, không có dấu < >.

Thực nghiệm trên chính bộ tài khoản:
- claude.ai đã nhận khoá `author` và frontmatter YAML không chặt (mô tả có «: » không bọc nháy) ⇒ khoá lạ chỉ cảnh báo.
- `EBM-MASTER` được nhận và lưu tên `ebm-master`.

**Dựng:**
1. `tools/dong_goi_skill_tai_khoan.py`:
   - so cả thư mục; kiểm luật; chỉ tệp git track; ZIP tất định vào `CLAUDE_AI_SKILLS/` (ngoài git);
   - ghi `name` = tên thư mục trong bản đóng gói — 7 skill `*-kdense` mang name trùng skill tiếng Việt sẽ ĐÈ nhau;
   - `DANH-SACH-TAI-LEN.md` + sổ lượt (lượt sau chỉ xoá ZIP do chính nó ghi).
2. `doi_chieu_ba_ben.doi_chieu`: «SKILL.md trùng + tệp phụ khác» ⇒ lệch bản (`tep_phu_khac`), dùng chung `tep_skill` với công cụ
   đóng gói.
3. Hòm việc `giac_quan_skill_tai_khoan`:
   - tài khoản cũ ⇒ ưu tiên 2;
   - chỉ còn skill chưa từng lên (tuỳ chọn) ⇒ ưu tiên 3;
   - thiếu bộ tài khoản ⇒ giác quan chết, không phải «đã khớp».
4. Làn đồng bộ in lệnh đóng gói. `pyhealth`: mô tả «Python ≥3.12,<3.14» ⇒ «Python 3.12 hoặc 3.13» (dấu < bị luật tải lên chặn).

**Kiểm:**
- `tools/test_dong_goi_skill_tai_khoan_20261004.py`: 15 test. Đột biến 11/11 bị bắt.
- BH163: đột biến 6/6 bị bắt (đối chiếu chỉ SKILL.md, đóng gói chỉ SKILL.md, ZIP mất gốc, không ghi lại name, giác quan im
  lặng, main() không gọi giác quan).

**Chưa làm (việc của bác sĩ):**
- Tải ZIP lên claude.ai.
- Hai skill `plugin-router-chatgpt` và `dieu-phoi-aipoch` chỉ có nghĩa trong Claude Code nên không đóng mặc định (`--skill` vẫn
  đóng được).
