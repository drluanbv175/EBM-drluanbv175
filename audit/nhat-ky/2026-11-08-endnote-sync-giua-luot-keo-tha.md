# 08/11/2026 — EndNote Sync giữa lượt kéo-thả: đè mất tag vừa gắn + giữ giao dịch mở làm sdb.eni đọc như hỏng

**Bối cảnh:** bác sĩ giao «Làm 1, 2 và 3» → nhóm 3 = lượt EndNote: đưa 239 bản ghi «rời nhóm» vào 7 nhóm (ILD, Vasculitis,
MS, PTSD, Bipolar, OCD, Somatic — 7 chủ đề phiên «Cập nhật vấn đề Endnote» nạp 07–08/11), gắn 15 tag «★ Áp dụng – tin cậy cao»
và 9 tag theo nhóm. Làm ở chế độ nền (app_drag), có cờ tạm dừng + khoá `--giu-khoa` + sao lưu
`~/.ebm-endnote-sao-luu/sdb.eni.truoc-luot-nhom-20261108`. Kết quả: 7 nhóm +239 (không gỡ bản ghi nào), 10 tag đúng số kỳ vọng.

**Bẫy 1 — Sync đè thay đổi vừa làm:** EndNote Sync tự chạy ~13–16 phút/lần (10:34 · 10:50 · 11:03). Lượt 10:50 rơi ~1 phút sau
lần gắn tag «Multiple Sclerosis» ⇒ 33/35 bản ghi MẤT tag đó; danh sách trở về đủ 3.811 nên lần thả «Thần kinh» ngay sau chỉ trúng
2 bản ghi. Thay đổi làm trước đó vài phút (7 nhóm, ★, Hô hấp, ILD, Khớp) còn nguyên. Đã gắn lại; lượt sync 11:03 không đè gì
(«All changes have been sent», cục bộ = trực tuyến 3.833 bản ghi · 167 nhóm · 91 tag).

**Bẫy 2 — giao dịch ghi mở sau sync:** từ 10:50 `sdb.eni` không còn được ghi sau mỗi thay đổi (thay đổi nằm ở `sdb.nal`); từ 11:03
mọi lần đọc bản sao sdb.eni (`gan_tag_endnote.py`, `endnote_suc_khoe.kiem_cau_truc`) báo «database disk image is malformed» /
`GiaoDichDangMo` suốt ≥ 15 phút — ảnh chụp giữa giao dịch, không phải hỏng (công cụ sức khoẻ nói rõ). Xác nhận bằng SỐ ĐẾM thanh bên
(mỗi tag tăng đúng +N so với bản sao lưu). Không đóng/khởi động lại EndNote, không sửa sdb.eni.

**Bẫy 3 — lần thả «trượt»:** một lần kéo 132 bản ghi lên «Tâm thần» không có tác dụng (danh sách giữ 132, thanh bên tự cuộn về đầu,
số đếm không đổi) ⇒ `--hien` lại rồi kéo lại thì đạt. Dòng tô xám lạ trên thanh bên là dấu kéo dở, không phải vùng chọn.

**Vá:** đoạn hướng dẫn kéo-thả trong `tools/gan_tag_endnote.py` (`--huong-dan`) thêm luật: đọc giờ «Synced at» trước khi kéo, làm
giữa hai lượt sync, đo lại sau lượt kế tiếp; giao dịch mở ⇒ xác nhận bằng số đếm thanh bên; lần thả trượt ⇒ `--hien` lại.

**Còn mở (bác sĩ):** kiểm lần cuối bằng `python3 tools/gan_tag_endnote.py` khi EndNote đã ghi giao dịch xuống (thường sau lượt
sync kế tiếp hoặc khi đóng thư viện bình thường) — kỳ vọng: không thiếu, không thừa, 0 rời nhóm.
