---
name: tao-video-tiktok
description: >-
  Tạo video TikTok dọc (9:16, 1080x1920) từ nội dung do người dùng cung cấp, có
  GIỌNG ĐỌC tiếng Việt mềm mại, ngắt nghỉ tự nhiên (edge-tts HoaiMy nữ / NamMinh
  nam, tự lùi về giọng macOS "Linh" khi mất mạng) và PHỤ ĐỀ ĐỘNG karaoke đồng bộ
  từng chữ. Dùng skill này khi người dùng muốn "làm video TikTok", "dựng video có
  giọng đọc / lồng tiếng / thuyết minh", "biến bài viết/kịch bản thành video ngắn",
  "video reels/shorts có phụ đề chạy", hoặc tạo nội dung cho kênh TikTok cá nhân.
  Hỗ trợ 3 chế độ: chữ động trên nền (mặc định), trình chiếu ảnh, bảng trắng viết
  tay; tuỳ chọn nhạc nền. Không tự đăng lên TikTok — chỉ xuất file mp4 + caption
  để người dùng tự duyệt và đăng.
---

# Tạo video TikTok có giọng đọc mềm mại

Skill biến **nội dung người dùng cung cấp** thành **video dọc TikTok hoàn chỉnh**:
giọng đọc tiếng Việt dịu, ngắt nghỉ tự nhiên + phụ đề chạy theo giọng + nền/hình.
Đầu ra là `video.mp4` (1080×1920) kèm `mo-ta.txt` (caption + hashtag) để người dùng
tự đăng.

## Khi nào dùng
Khi người dùng muốn dựng video ngắn dạng TikTok/Reels/Shorts có lời đọc từ nội dung
của họ (bài viết, kịch bản, mẹo, kiến thức…). KHÔNG dùng để tự đăng bài.

## Môi trường
Chạy bằng Python của venv có sẵn **`~/.ebm-venv/bin/python`** (đã có `edge-tts`,
`imageio-ffmpeg`, `Pillow` — không cần cài thêm). Nếu môi trường khác, xem
`scripts/setup.sh`. Luôn kiểm tra trước bằng:
```bash
~/.ebm-venv/bin/python <SKILL>/scripts/kiem_tra.py
```

## Quy trình (Claude làm theo các bước này)

1. **Lấy nội dung** từ người dùng. Nếu họ chỉ đưa chủ đề/ý thô, hãy soạn giúp thành
   kịch bản TikTok có nhịp: **hook 3 giây đầu → thân bài 2–4 ý → kêu gọi (CTA)**.
   Giữ câu ngắn, đời thường, dễ nghe.

2. **Viết file kịch bản** `.md` theo cú pháp ở `references/cu-phap-kich-ban.md`.
   Những điểm quan trọng để giọng "mềm mại, ngắt nghỉ":
   - Chèn `||` ở chỗ cần **nghỉ lấy hơi** (giữa các ý lớn, trước câu chốt).
   - Dùng `…` cho **nhấn nhá nhẹ**; `[0.6s]` khi cần **nghỉ chính xác** N giây.
   - Mỗi đoạn (cách nhau dòng trống) tự có một nhịp nghỉ.
   - Câu ngắn, dấu phẩy đặt đúng chỗ → edge-tts tự ngắt nghỉ tự nhiên.
   - Đặt `::voice nu` (mặc định, mềm) hoặc `nam`; `::rate -10%` (âm = chậm/mềm hơn).
   - Thêm `::hashtag ...` để có sẵn caption khi đăng.

3. **Chọn chế độ hình** qua `::che-do`:
   - `kinetic` (mặc định): chữ động trên nền gradient/màu/ảnh — không cần ảnh.
   - `slide`: trình chiếu ảnh người dùng cấp (mỗi block một ảnh bằng `::slide ĐƯỜNG_DẪN`).
   - `whiteboard`: nền giấy + chữ tay, cảm giác dịu, thủ công.

4. **Dựng video**:
   ```bash
   ~/.ebm-venv/bin/python <SKILL>/scripts/tao_video.py KICH_BAN.md --out THƯ_MỤC_RA
   ```
   Cờ hay dùng: `--voice nam`, `--rate -12%`, `--che-do slide`,
   `--nen anh.jpg`, `--nhac nhac.mp3`, `--tieu-de "..."`, `--khong-zoom`.

5. **Giao kết quả**: đưa đường dẫn `video.mp4` và nội dung `mo-ta.txt`. Nhắc người
   dùng **xem trước rồi tự đăng**. Nếu nội dung **y khoa**, skill tự thêm khuyến cáo
   "Cần bác sĩ kiểm chứng" và chỗ ghi nguồn (đặt `::nguon PMID:... / DOI:...`).

## Lưu ý kỹ thuật
- edge-tts (giọng mềm) **cần mạng** và đôi khi bị **chặn tần suất** → engine đã có
  retry/backoff; nếu vẫn không được sẽ tự lùi về giọng "Linh" (macOS, offline).
- Mỗi lần chạy xuất: `video.mp4`, `voice.wav`, `captions.ass`, `mo-ta.txt`, `loi-doc.txt`.
- Video không tự đăng; tuân thủ CLAUDE.md (không lưu PII, nội dung y khoa kèm nguồn +
  disclaimer).

## Tài liệu kèm theo
- `references/cu-phap-kich-ban.md` — đầy đủ cú pháp directive `::` và dấu nghỉ.
- `references/huong-dan-su-dung.md` — ví dụ chi tiết từng chế độ, mẹo giọng đọc.
- `templates/vi-du-kich-ban.md` — kịch bản mẫu chạy được ngay.
- `scripts/kiem_tra.py` — kiểm tra môi trường.
