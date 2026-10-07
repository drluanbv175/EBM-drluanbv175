# 07/10/2026 — Hội đồng cổng: chạy khô, họp thí điểm G0 của C1a, trọng tài bằng Codex

Bác sĩ hỏi hệ hội đồng G0–G10 đã hoàn thiện chưa. Đo cùng ngày:
- Đủ 15 thành phần ở cả hai repo; danh mục 29 nhiệm vụ, 18 điểm quyết định (8 bắt buộc tranh biện), rubric RQ1–RQ8.
- Bộ test hội đồng 99/99 qua.
- Nhưng CHƯA họp thật lần nào: 0 biên bản trong `exports/`; C1a «CHƯA HỌP» cả 11 cổng.
- Chế độ trọng tài `codex` mới có khung: công cụ nhận biên bản `codex`, chưa có gì chạy được.

Bác sĩ giao: «chạy 3 vấn đề được đề xuất».

## 1. Chạy khô

Workflow `hoi-dong-cong` với `chay_thu: true` cho G0 của C1a: 0 agent, 0 token. Kế hoạch: 1 hồ sơ cổng, 2 người chấm
mỗi nhiệm vụ có đầu ra, mỗi điểm quyết định phản biện + trọng tài, 1 ghi biên bản; trần 16 agent.

## 2. Họp thí điểm G0 của C1a

**Kết quả** (lượt họp đầu: 16 agent, ≈ 6,15 triệu token, 80 phút):
- Chấm sống G0 = `DRAFT_READY_NEEDS_HUMAN_REVIEW`, còn REVIEW G0-HUMAN-05/06/07/08. Nhãn «đạt» LƯU trong
  `G0_checkpoint.json` và `G0_QUALITY_REPORT.md` đã lạc hậu so với chấm sống.
- Đánh giá chéo 4 đầu ra: G0-T3, G0-T4 đồng thuận «trả về sửa»; G0-T1, G0-T2 BẤT ĐỒNG (người chấm chuyên môn ≠ giám
  khảo).
- DP-G0-1 → chuyển bác sĩ, 3 vấn đề thuộc PI:
  - MT2 là câu hỏi một phơi nhiễm hay nhiều yếu tố;
  - với thời gian chờ: giả thuyết định trước hay chỉ ước lượng;
  - độ chính xác d = 0,05 (G3) hay 0,031 (đề cương), và khung cỡ mẫu MT2 Whitehead hay EPV.
  Giải pháp khuyến nghị: MT2 hai tầng (PMID 23371353, 34017606 — đã kiểm rút bài).
- DP-G0-2 → sửa kết luận: thu hẹp tuyên bố «tính mới», vì đã có dữ liệu hài lòng công bố ở bối cảnh tương tự.
- Hồ sơ C1a: 143 tệp KHÔNG ĐỔI (so mã băm trước/sau) — hội đồng không sửa gì của đề tài.

**Ghi biên bản — hai trục trặc:**
1. Bước ghi bị bỏ vì chạm trần (lỗi thiết kế bên dưới, đã vá).
2. Tiếp tục (resume) lượt họp để ghi lại: bộ nhớ đệm chỉ dùng lại ĐOẠN ĐẦU không đổi của chuỗi lời gọi; các lượt song song
   khởi động theo thứ tự khác ⇒ gần như mọi agent CHẠY LẠI (thêm ≈ 3,65 triệu token), rồi chạm giới hạn phiên ⇒ vẫn
   không ghi. Bài học: đừng resume một lượt song song để «vá» một bước.

Cuối cùng 6 biên bản (4 đánh giá chéo + 2 tranh biện DP) được CHUYỂN NGUYÊN VĂN từ đầu ra có cấu trúc của lượt đầu qua
`hoi_dong_cong` (kiểm luật từng biên bản, không mở agent); mỗi biên bản mang trường `nguon_ghi` nói rõ điều đó. Hai tranh
biện bất đồng (BD-G0-T1 thiếu trọng tài, BD-G0-T2 thiếu phản biện) chưa có phán quyết ⇒ không ghi; tóm tắt G0 =
«BẤT ĐỒNG — CẦN TRANH BIỆN», đúng thực trạng.

**Chi phí thật ≈ 9,8 triệu token cho G0** (6,15 + 3,65) — ước lượng cũ «1–3 triệu/cổng» trong doctrine, CLAUDE.md và
workflow đã sửa theo số đo.

**Lỗi thiết kế lộ ra (đã vá):** bước GHI BIÊN BẢN là lời gọi cuối và cũng tính vào trần agent. 4 nhiệm vụ × 2 người
chấm + 2 điểm quyết định + đầu ra bất đồng (mỗi cái cần đề xuất + phản biện + trọng tài) vượt trần mặc định 16 ⇒ bước
ghi bị bỏ ⇒ kết quả cả hội đồng không vào sổ. Vá: giữ chỗ một suất cho bước ghi (các vai khác dùng tối đa trần − 1).
Tái hiện bằng node với agent giả: bản chưa vá bỏ bước ghi (`ghi_bien_ban = null`), bản vá vẫn ghi và liệt kê lượt bị bỏ.

## 3. Trọng tài bằng Codex

`medical-ebm-automation/tools/trong_tai_codex.py`:
- Hồ sơ gửi Codex: doctrine trọng tài (bản Codex sinh từ agent Claude), trạng thái cổng chấm sống, trích đoạn CÓ SỐ DÒNG
  đúng tệp/dòng căn cứ.
- Chỉ gửi tệp văn bản cấp đầu thư mục đề tài và `tools/`, thư mục agent. KHÔNG gửi tệp ẩn/khoá/`.env`/«secret», dữ liệu
  hay bản gỡ băng ở thư mục con. Dữ liệu đề tài bọc khối KHÔNG TIN CẬY.
- `codex exec --ephemeral --ignore-user-config --sandbox read-only` trong thư mục tạm rỗng, môi trường lọc (không truyền
  khoá), `--output-schema` chặt; lỗi tạm thời thử lại 1 lần.
- Ghép biên bản `che_do: codex` (trọng tài «codex:trong-tai-tranh-bien» + nguồn trọng tài), kiểm bằng CHÍNH luật biên
  bản; vi phạm ⇒ mã 3, không ghi.
- Workflow: `args.trong_tai: "codex"` — vai trọng tài Claude chỉ CHUYỂN TIẾP (chạy trình, trả nguyên văn), lỗi ⇒ bỏ biên
  bản DP đó, không phán thay.
- Máy này không có `codex` trong PATH; trình tìm được bản `~/.codex/plugins/.plugin-appserver/codex`
  (`codex-cli 0.155.0-alpha.9.2`).

**Một mâu thuẫn tự phát hiện:** đoạn doctrine «chế độ codex: bạn KHÔNG tự phán, hãy chạy trình chạy» (viết cho agent
Claude chuyển tiếp) cũng đi vào prompt gửi CHÍNH Codex. Sửa: doctrine ghi rõ đoạn đó dành cho agent Claude; prompt Codex có
chỉ thị tin cậy «bạn chính là trọng tài, phán trực tiếp».

**Kiểm:**
- 16 test (Codex thay bằng bản giả); đột biến 15/15 (lượt đầu 13/15 — hai phép thử chưa cô lập đúng luật, đã cô lập).
- Codex THẬT 2 lượt trên đề tài TỔNG HỢP: 37 s và 26 s; cả hai chấp nhận phản đối có căn cứ, biên bản hợp lệ. Lượt 2 dùng
  doctrine mới: Codex vẫn phán trực tiếp. Hai lượt ra kết quả khác nhau (sửa kết luận / chuyển bác sĩ), đều hợp luật —
  độ dao động tự nhiên của mô hình.
- Toàn bộ bộ test y khoa: 8285 qua · 44 bỏ qua · 0 đỏ.

**Sự cố quy trình nhỏ:** sửa tệp mới (chưa stage) bằng script heredoc với `newline` sai ⇒ `write_text` mở tệp ở chế độ
ghi (cắt về 0 byte) TRƯỚC khi báo lỗi. Phục hồi từ ngữ cảnh phiên; từ đó tệp mới được `git add` ngay khi viết xong.

Cần bác sĩ kiểm chứng.
