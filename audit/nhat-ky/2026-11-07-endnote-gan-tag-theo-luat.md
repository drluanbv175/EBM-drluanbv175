# 07/11/2026 — EndNote: gắn tag theo luật sau mỗi lượt nạp + tag «★ Áp dụng – tin cậy cao»; vùng chọn bị phiên khác đổi giữa lúc kéo

**Yêu cầu bác sĩ (07/11/2026):** «Trong Endnote tôi đã có nhiều tab hãy gắn tab tất cả cho phù hợp», rồi «Cập nhật để mỗi lần
đưa trích dẫn vào Endnote sẽ gắn Tab luôn cho tôi; … hãy gắn tab với những chứng cứ có độ tin cậy cao và áp dụng cho thực hành
lâm sàng». Bác sĩ chọn tiêu chí «Thêm guideline không chấm GRADE» và «Gắn ngay sau mỗi lần nạp».

**Đo:**
- EndNote 2025 không có lệnh AppleScript nào cho tag (EndNote.sdef); chế độ điều khiển nền không bấm được Select All. Chỉ kéo-thả
  toàn màn hình chạy được. Tag nằm ở `tag_groups` + `tag_members_content` (c0 = mã tag hex) của `sdb.eni` — luật dự án cấm ghi thẳng.
- Gắn tay 164 nhóm (307 cặp nhóm×tag): 3.330/3.440 bản ghi có tag, đối chiếu bản sao lưu `sdb.eni.truoc-gan-tag-20261107`:
  0 tag thừa, 0 tag mất. Chờ cmd+A quá ngắn (0,3 s) ⇒ có lượt chỉ dòng đầu được gắn; số đếm cạnh tag trên giao diện làm mới
  chậm một nhịp nên KHÔNG lộ lỗi — chỉ đo `sdb.eni` mới thấy (14 cặp thiếu, đã làm bù).
- **Sự cố:** ~07:34 một phiên khác nhập bản ghi tóm tắt bệnh ruột viêm (rec 9046) bằng AppleScript đúng lúc đang kéo-thả; EndNote
  đổi vùng chọn sang bản ghi mới ⇒ 9046 bị gắn nhầm tag «CAD». Phát hiện bằng đối chiếu tag ngoài dự kiến so với bản sao lưu; gỡ
  qua Manage Tags. Phiên kia đã tạm dừng ghi theo tin nhắn.
- Tiêu chí tag Áp dụng: 278 bản ghi là nguồn của mục `apply` (theo `tang_uu_tien`, có lùi về bản cũ) — 102 high, 71 moderate,
  82 `na` guideline, 23 low/vlow. Bỏ ngữ cảnh bản cũ (bản mới đã bỏ trích dẫn) loại thêm 9 bài «apply/high/Guideline» chỉ còn ở bản
  cũ của dashboard tuần Tim mạch 09/06/2026 — đều lạc đề (vd «Retrospective comparison of ChatGPT-4…»). Kết quả: 254 bản ghi đạt.

**Vá:**
- `tools/gan_tag_endnote.py` (chỉ đọc): tag «★ Áp dụng – tin cậy cao» = nguồn chính của mục `apply` ở phiên bản HIỆN HÀNH, gradeLevel
  high/moderate, hoặc `na` khi design là guideline/nhãn thuốc/chống chỉ định (consensus không đủ; low/vlow không nhận); tag theo nhóm
  từ `sync/endnote-tag-theo-nhom.json` (164 nhóm đã duyệt), nhóm mới «EBM ·/TT ·» suy chuyên khoa bằng luật Antifacts, «NC ·» ⇒
  Nghiên cứu khoa học, nhóm lạ ⇒ báo, không đoán. `--hien "<tag>"` cho EndNote chỉ hiện + tô sáng bản ghi thiếu tag (show/highlight
  — không ghi) ⇒ mỗi tag một lần kéo. Chỉ đề xuất gỡ tag Áp dụng thừa; không bao giờ đề xuất gỡ tag khác.
- `nap_endnote_chu_de.py`: lượt nạp `--ap-dung` in dòng việc gắn tag (`bao_gan_tag`); đo hỏng không làm sập lượt nạp, không in «đủ».
- `tu_de_xuat_viec.py`: giác quan ⑦o — 🛎 cặp thiếu/thừa/tag chưa tạo, 👤 nhóm chưa ánh xạ; không đo được ⇒ chết (⚪).
- Skill `cap-nhat-chung-cu-y-khoa` ⑧ và CLAUDE.md §6.2: phiên Claude kéo-thả NGAY sau lượt nạp; trước đó ListAgents và nhắn phiên
  khác tạm dừng ghi EndNote.

**Kiểm:** `tools/test_gan_tag_endnote_20261107.py` 31 ca; 11 đột biến (bỏ lọc bản cũ, nhận low, bỏ chặn consensus, thừa tính cả
thùng rác, ánh xạ thua luật suy, luật suy trả tag chung, nhóm lạ bị đoán, không đo được in ✓, bỏ gọi ở lượt nạp, bỏ giác quan, nhãn
👤→🛎) đều đỏ, phục hồi xanh.
