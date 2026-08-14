---
name: dao-tao-slide-tai-lieu-y-khoa
description: Tạo và chuẩn hóa sản phẩm đào tạo y khoa và tài liệu chuyên môn — bài giảng, slide PowerPoint (.pptx), tài liệu Word (.docx), PDF, infographic/poster, bảng tóm tắt, bảng quyết định, thuật toán lâm sàng (Mermaid), checklist cờ đỏ, bảng thuốc, kế hoạch theo dõi, dặn dò người bệnh, báo cáo chuyên môn và bản cập nhật guideline. Dùng skill này bất cứ khi nào ĐẦU RA là một sản phẩm để giảng dạy, trình bày, phát tay hoặc lưu hồ sơ — kể cả khi người dùng không nói rõ chữ "slide" hay "bài giảng" mà chỉ nói "soạn bài dạy về…", "làm tài liệu/poster/infographic về…", "xuất file Word/PowerPoint/PDF về…", "tạo bảng/thuật toán/checklist để dạy", hay "chuẩn hóa tài liệu chuyên môn này". Áp dụng cả khi cần xuất file thật (.pptx/.docx/.pdf) cho nội dung y khoa. KHÔNG dùng cho việc ra quyết định lâm sàng trên một người bệnh cụ thể khi đầu ra chỉ là câu trả lời tư vấn (các skill lâm sàng khác lo việc đó); skill này được kích hoạt khi cần BIẾN nội dung đó thành sản phẩm đào tạo/tài liệu có định dạng.
---

# Đào tạo y khoa, slide và tài liệu chuyên môn

## Mục đích

Tạo tài liệu đào tạo y khoa và sản phẩm chuyên môn **chính xác, an toàn, dễ đọc,
áp dụng được**, với phong cách thị giác nhất quán và khả năng xuất ra file thật.

## Quy trình

1. **Xác định đầu ra**: sản phẩm cần là gì — bài giảng đầy đủ, slide deck, tài
   liệu Word, PDF, infographic/web, hay chỉ một bảng/thuật toán/checklist trả lời
   trong hội thoại? Điều này quyết định độ sâu và việc có cần tạo file hay không.

2. **Áp dụng quy tắc chứng cứ & an toàn** (mục "Quy tắc cốt lõi" bên dưới). Khi
   nội dung có khuyến cáo, mức chứng cứ hoặc cần tài liệu tham khảo, đọc
   `references/chung-cu-trich-dan.md`.

3. **Soạn nội dung theo cấu trúc phù hợp**. Với bài giảng/slide đầy đủ hoặc khi
   cần chọn định dạng trình bày, đọc `references/mau-bai-giang.md`.

4. **Tạo file thật khi được yêu cầu** (xem mục "Xuất file" bên dưới). Áp dụng màu
   sắc, font và mẫu trực quan theo `references/phong-cach-thi-giac.md`.

5. **Rà checklist chất lượng** trước khi giao sản phẩm.

## Quy tắc cốt lõi (bắt buộc)

Đây là các ràng buộc an toàn và liêm chính — ưu tiên trên hình thức:

- Trả lời bằng tiếng Việt, trừ khi người dùng yêu cầu ngôn ngữ khác.
- Ưu tiên an toàn người bệnh, độ tin cậy của chứng cứ và khả năng áp dụng thực hành.
- **Không bịa** guideline, nghiên cứu, chỉ số, liều thuốc, chống chỉ định hoặc tài
  liệu tham khảo. Khi thiếu thông tin, đưa khung xử trí an toàn và đánh dấu rõ dữ
  kiện cần bổ sung (`[CẦN BỔ SUNG]`, `[CẦN KIỂM CHỨNG]`, `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]`,
  `[DỰ THẢO]`).
- Luôn phân biệt: chẩn đoán chắc chắn · chẩn đoán có khả năng · chẩn đoán phân biệt
  · cờ đỏ · xử trí ngoại trú · chuyển tuyến · theo dõi.
- Với khuyến cáo quan trọng: ghi nguồn chính + năm/phiên bản; tách độ chắc chắn
  chứng cứ với độ mạnh khuyến cáo; **không tự gán/quy đổi GRADE**. Chi tiết:
  `references/chung-cu-trich-dan.md`.
- Với kháng sinh, đánh giá có thực sự cần dùng không và xem xét phân nhóm WHO AWaRe.
- Với điều trị ngoại trú, luôn nêu thời điểm tái khám, tiêu chí thất bại điều trị
  và dấu hiệu cần quay lại ngay/đến cấp cứu (safety-netting).
- Không thay thế khám trực tiếp, phác đồ bệnh viện, quy định địa phương hoặc xử
  trí cấp cứu.

## Nguyên tắc nội dung

- Một slide/khối một thông điệp chính; tiêu đề nên chính là thông điệp đó.
- Ưu tiên bảng, sơ đồ, thuật toán, checklist hơn đoạn văn dài.
- Có tóm tắt thực hành (take-home) và cảnh báo an toàn khi phù hợp.
- Không nhồi chữ; không hy sinh ý an toàn quan trọng để "cho đẹp".

## Xuất file (.pptx / .docx / .pdf / web)

Khi người dùng cần một **file** chứ không chỉ nội dung trong hội thoại, hãy đọc
SKILL.md tương ứng TRƯỚC khi viết code hoặc tạo file — các skill đó chứa ràng buộc
môi trường (thư viện, đường dẫn, cách render) không nằm trong skill này:

- Slide PowerPoint → `/mnt/skills/public/pptx/SKILL.md`
- Tài liệu Word → `/mnt/skills/public/docx/SKILL.md`
- PDF → `/mnt/skills/public/pdf/SKILL.md`
- Infographic / poster / trang web / HTML → `/mnt/skills/public/frontend-design/SKILL.md`

Sau khi đọc skill định dạng, áp dụng bảng màu theo vai trò (cam = cảnh báo/cờ đỏ/
điểm mới; xanh dương = chẩn đoán/quy trình; xanh lá = điều trị/theo dõi) và font
(tiêu đề Poppins/Arial, nội dung Lora/Georgia) theo `references/phong-cach-thi-giac.md`.

## Checklist chất lượng

- [ ] Có mục tiêu học tập (nếu là bài giảng)?
- [ ] Mỗi slide/khối có một thông điệp chính rõ?
- [ ] Có bảng/thuật toán/checklist khi cần thay cho văn bản dài?
- [ ] Khuyến cáo quan trọng đã ghi nguồn + năm và grading nguyên bản đúng cách?
- [ ] Đã đánh dấu rõ chỗ thiếu/cần kiểm chứng thay vì bịa?
- [ ] Có cảnh báo an toàn, cờ đỏ và safety-netting khi phù hợp?
- [ ] Có take-home messages?
- [ ] Màu/font áp dụng đúng vai trò ngữ nghĩa (nếu là file có định dạng)?
- [ ] Dễ đọc và dùng được trong thực hành/đào tạo?

## File tham khảo

- `references/mau-bai-giang.md` — cấu trúc bài giảng 8 mục, mẫu ca lâm sàng, thư
  viện định dạng đầu ra ngắn, quy ước storyboard slide.
- `references/phong-cach-thi-giac.md` — bảng màu + vai trò, font, cách áp dụng theo
  loại file, mẫu bảng quyết định có mã màu, mẫu thuật toán Mermaid.
- `references/chung-cu-trich-dan.md` — thứ tự ưu tiên nguồn, quy tắc GRADE, nhãn
  đánh dấu thiếu thông tin, mẫu trích dẫn Vancouver/NLM.
