# Hướng dẫn sử dụng — skill tạo video TikTok

## 0. Một dòng để chạy
```bash
~/.ebm-venv/bin/python scripts/tao_video.py KICH_BAN.md --out THƯ_MỤC_RA
```
Đầu ra trong `THƯ_MỤC_RA/`: `video.mp4` (1080×1920), `mo-ta.txt` (caption + hashtag),
`voice.wav`, `captions.ass`, `loi-doc.txt`.

## 1. Quy trình khuyến nghị
1. **Soạn kịch bản** (xem `cu-phap-kich-ban.md`). Cấu trúc TikTok hiệu quả:
   - **Hook (3 giây đầu):** câu khiến người xem dừng lại — câu hỏi, con số, điều bất ngờ.
   - **Thân bài:** 2–4 ý, mỗi ý 1–2 câu ngắn, cách nhau bằng `||` để lấy hơi.
   - **CTA:** kêu gọi lưu/lượt theo dõi/bình luận.
2. **Kiểm tra môi trường** (lần đầu): `~/.ebm-venv/bin/python scripts/kiem_tra.py`.
3. **Dựng video** bằng lệnh ở mục 0.
4. **Xem trước** `video.mp4`, **tự đăng** lên TikTok kèm `mo-ta.txt`.

## 2. Ba chế độ hình ảnh

### a) `kinetic` (mặc định) — chữ động trên nền
Không cần ảnh. Phụ đề lớn karaoke nổi trên nền gradient/màu/ảnh.
```bash
... tao_video.py kb.md --nen gradient        # nền chuyển sắc tối (đẹp, an toàn)
... tao_video.py kb.md --nen "#0B132B"        # nền 1 màu
... tao_video.py kb.md --nen ./background.jpg  # ảnh nền (tự làm tối + zoom mềm)
```

### b) `slide` — trình chiếu ảnh
Mỗi đoạn (mở bằng `::slide ĐƯỜNG_DẪN`) hiện một ảnh đúng lúc đọc.
```bash
... tao_video.py kb.md --che-do slide
```

### c) `whiteboard` — bảng trắng viết tay
Nền giấy, chữ tay (font Bradley Hand), zoom rất chậm → cảm giác dịu.
```bash
... tao_video.py kb.md --che-do whiteboard
```

## 3. Tinh chỉnh GIỌNG ĐỌC (mềm mại, ngắt nghỉ)
- Giọng: `--voice nu` (mặc định, HoaiMy dịu) hoặc `--voice nam` (NamMinh trầm).
- Tốc độ: `--rate -10%` (mặc định). Muốn **mềm/chậm hơn** → `-14%`, `-18%`.
- Ngắt nghỉ: thêm `||`, `…`, `[0.8s]` vào kịch bản (xem cú pháp).
- Cao độ: `--pitch -2Hz` cho giọng trầm/ấm hơn (tuỳ chọn).

> edge-tts (giọng mềm) cần MẠNG. Khi gọi nhiều video liên tiếp, Microsoft có thể
> CHẶN TẦN SUẤT tạm thời — engine tự retry/backoff; nếu vẫn không được sẽ dùng giọng
> "Linh" (offline). Nếu thấy báo "dùng giọng Linh", hãy **chờ 1–2 phút rồi chạy lại**
> để có giọng HoaiMy mềm.

## 4. Nhạc nền
```bash
... tao_video.py kb.md --nhac ./nhac-nhe.mp3
```
Nhạc tự hạ nhỏ (≈12%) và fade dần ở cuối, lặp đủ độ dài video. Hãy dùng nhạc bạn có
quyền sử dụng (TikTok có thư viện nhạc miễn phí bản quyền cho nội dung không thương mại).

## 5. Mẹo độ dài & nhịp
- TikTok tốt nhất 20–60 giây. ~150 từ tiếng Việt ≈ 60 giây ở `--rate -10%`.
- Đừng nhồi chữ; chừa khoảng nghỉ để người nghe "thở".
- Một ý = một câu hoặc hai câu ngắn.

## 6. Nội dung Y KHOA
- Đặt `::nguon PMID: ... / DOI: ...` → ghi nguồn lên video (dòng chân) và mô tả.
- Skill tự thêm khuyến cáo "Cần bác sĩ kiểm chứng" khi phát hiện nội dung y khoa.
- Muốn tắt: `::disclaimer off`. Muốn ép câu riêng: `::disclaimer "..."`.
- Không đưa thông tin định danh bệnh nhân (PII) vào kịch bản.

## 7. Khắc phục sự cố
- **Phụ đề trống / chỉ vài chữ:** cần `boundary="WordBoundary"` — đã bật trong engine;
  nếu chỉnh sửa code đừng bỏ tham số này.
- **Báo "No audio received" liên tục:** đang bị chặn tần suất → chờ rồi chạy lại,
  hoặc tách video dài thành phần nhỏ hơn.
- **Sai font/thiếu dấu tiếng Việt:** đảm bảo có font Arial (Supplemental) trên macOS;
  engine đã trỏ `fontsdir` tới `/System/Library/Fonts/Supplemental`.
- **Chạy môi trường khác máy này:** xem `scripts/setup.sh`.
