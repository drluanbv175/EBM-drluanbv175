# tao-video-tiktok

Skill biến **nội dung bạn cung cấp** thành **video TikTok dọc 1080×1920** có:
- 🎙️ **Giọng đọc tiếng Việt mềm mại, ngắt nghỉ tự nhiên** (edge-tts HoaiMy nữ /
  NamMinh nam; tự lùi về giọng macOS "Linh" khi mất mạng).
- 📝 **Phụ đề động karaoke** — chữ sáng lên đúng lúc đọc.
- 🖼️ 3 chế độ hình: chữ động trên nền (mặc định), trình chiếu ảnh, bảng trắng viết tay.
- 🎵 Nhạc nền tuỳ chọn (tự nhỏ tiếng + fade).

Không tự đăng lên TikTok — chỉ xuất `video.mp4` + `mo-ta.txt` để bạn tự duyệt và đăng.

## Chạy nhanh
```bash
# 1) kiểm tra môi trường (lần đầu)
~/.ebm-venv/bin/python scripts/kiem_tra.py

# 2) dựng video từ kịch bản mẫu
~/.ebm-venv/bin/python scripts/tao_video.py templates/vi-du-kich-ban.md --out ./ra
```

## Cấu trúc
```
tao-video-tiktok/
├── SKILL.md                      # mô tả skill + quy trình cho Claude
├── README.md                     # file này
├── scripts/
│   ├── tao_video.py              # engine chính (TTS + phụ đề + ghép video)
│   ├── kiem_tra.py               # kiểm tra môi trường
│   └── setup.sh                  # cài phụ thuộc cho môi trường mới
├── templates/
│   └── vi-du-kich-ban.md         # kịch bản mẫu chạy được ngay
└── references/
    ├── cu-phap-kich-ban.md       # cú pháp directive :: và dấu nghỉ
    └── huong-dan-su-dung.md      # hướng dẫn chi tiết + mẹo
```

## Phụ thuộc (đã có sẵn trong `~/.ebm-venv`)
`edge-tts` · `imageio-ffmpeg` (ffmpeg có libass/freetype/fontconfig) · `Pillow`.
macOS có giọng `Linh` (vi_VN) làm fallback offline.

Xem `references/huong-dan-su-dung.md` để biết đầy đủ tuỳ chọn.
