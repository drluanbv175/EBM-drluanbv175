# MẪU THẺ CHỨNG CỨ TUẦN — bản chính thức (12/09/2026)

> Trước bản này, định dạng thẻ chỉ tồn tại dưới hai hình thức không chính thức: một dòng mô tả
> "6 dòng/thẻ" trong `SKILL.md` bước 5, và "xem mẫu W33" — một file quá khứ cụ thể. Cả hai đã
> **lỗi thời**: đối chiếu W33 (6 khối) với W35–W37 (8 khối) cho thấy định dạng đã tăng dần qua
> 5 tuần mà không ai viết lại thành mẫu — đúng loại trôi dạt mà repo này đã nhiều lần gọi tên
> ("tài liệu nói một đằng, mã sống chạy một nẻo"). File này chốt lại **cấu trúc đang THẬT SỰ
> chạy** (dựa trên W35–W37, ổn định nhất), không phải cấu trúc lý tưởng chưa ai dùng.
>
> Vì sao đáng làm mẫu chính thức, không phải chỉ ghi trong SKILL.md: so với các khung tóm tắt
> chứng cứ đã công nhận (CAT — Critically Appraised Topic; GRADE Summary-of-Findings; định dạng
> "Practice-Changing Update" của DynaMed/NEJM Journal Watch), cấu trúc 8 khối dưới đây **khớp
> hoặc vượt** — đặc biệt ở khoản **tách RIÊNG "rủi ro nếu áp dụng sai" khỏi "rủi ro nếu bỏ qua"**
> (hai chiều lỗi khác nhau, ít khung nào tách bạch) và **gắn `appraisalCompleteness` vào từng
> thẻ** (CAT/DynaMed thường không phân biệt "đã đọc toàn văn" khỏi "chỉ đọc tóm tắt" ở cấp thẻ).
> Việc cần làm không phải xây lại, mà là **CHỐT LẠI THÀNH VĂN** để không trôi tiếp và để có cái
> mà máy kiểm được (xem `tools/kiem_mau_the_chung_cu_tuan.py`).

## Khối tiêu đề (bắt buộc)

```
**[<Mã thẻ, vd W38-01>] <Chủ đề, súc tích> — <Loại nguồn ngắn> — <Đề xuất>[ (<thẻ ưu tiên>)]**
```

- `<Đề xuất>` CHỈ được là một trong ba: `Áp dụng ngay` · `Cân nhắc` · `Chưa đủ` — đây là ĐỀ XUẤT
  để bác sĩ phản bác, không phải quyết định (mọi thẻ dừng ở `CANDIDATE`).
- `Áp dụng ngay` CHỈ hợp lệ khi `appraisalCompleteness=full` VÀ hiệu số có ý nghĩa lâm sàng rõ —
  luật cứng đã có từ trước (xem SKILL.md), mẫu này không đổi luật, chỉ chốt lại cách viết.
- Thẻ ưu tiên là quy ước ĐÃ DÙNG ổn định, GIỮ NGUYÊN — không phát minh thêm nhãn mới:
  `(ưu tiên đọc #1)` · `(an toàn)` · `(đọc kỹ nếu đang kê <thuốc/nhóm>)`. Nhãn tự do, ngắn, mô tả
  ĐÚNG lý do ưu tiên — không dùng để thay cho nội dung bên dưới.

## 8 khối nội dung (thứ tự CỐ ĐỊNH, không đảo)

1. **`Điều gì thay đổi:`** — 1-3 câu. Câu ĐẦU nên là câu **kết luận thực hành** tự nó đứng được
   (đúng tinh thần "Clinical Bottom Line" của CAT) — bác sĩ chỉ đọc câu này vẫn nắm được điều cốt
   lõi. Ví dụ đã đạt chuẩn này (W37-01): *"đây là lần Cochrane xếp so sánh thuốc lá điện tử chứa
   nicotine với NRT ở mức chứng cứ ĐỘ CHẮC CHẮN CAO... Câu thực hành đổi từ 'có giúp cai không'
   sang 'khi nào hơn NRT'."* KHÔNG lặp lại nguyên văn tiêu đề.
2. **`Nguồn:`** — Loại thiết kế · Tạp chí, năm · **PMID** · **doi** · đăng ký tiền cứu nếu có
   (PROSPERO/NCT) · chuẩn báo cáo nếu nêu (PRISMA/RoB 2) · trạng thái truy cập mở nếu biết. LUẬT
   CỨNG (không đổi): 100% thẻ phải có PMID hoặc DOI đã phân giải — không có thì không lên thẻ.
3. **`Hiệu số như nguồn báo cáo:`** — trích ĐÚNG số liệu, ĐÚNG đơn vị, ĐÚNG chiều như nguồn công bố
   (không tự quy đổi HR/RR/OR, không tự tính lại). Kèm cỡ mẫu, số nghiên cứu, I²/heterogeneity khi
   nguồn có, và **mức GRADE/độ chắc chắn CỦA CHÍNH NGUỒN** (không tự gán — luật R4 chống tự gán
   mức). Tóm tắt không nêu số → ghi rõ *"tóm tắt không nêu"*, không suy diễn.
4. **`Ai bị ảnh hưởng:`** — 1 câu, mô tả đúng quần thể ĐÍCH (tuổi, bệnh nền, ngữ cảnh ngoại trú) —
   không mở rộng ra ngoài quần thể nghiên cứu.
5. **`Rủi ro nếu áp dụng sai: ... | Nếu bỏ qua: ...`** — HAI chiều lỗi TÁCH BẠCH trên cùng một
   dòng, nối bằng ` | `. "Áp dụng sai" = đọc/dùng số liệu SAI CÁCH (đảo chiều, bỏ qua khoảng tin
   cậy cắt qua 1/0, áp sai quần thể). "Bỏ qua" = hậu quả của việc KHÔNG đọc/không cập nhật thực
   hành. Đây là điểm khác biệt lớn nhất so với CAT/DynaMed chuẩn — GIỮ, đừng gộp lại thành một câu.
6. **`⚠️ <Giới hạn/cảnh báo áp dụng>`** (khi có) — mọi giới hạn do CHÍNH nguồn tự khai (cỡ mẫu nhỏ,
   phạm vi loại trừ, thiết kế không đo được cái gì) hoặc do khoảng cách bối cảnh Việt Nam. Đánh dấu
   rõ `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` cho phần chưa tra được — TUYỆT ĐỐI không suy đoán tình trạng pháp
   lý/lưu hành tại Việt Nam từ trí nhớ.
7. **`Thẩm định toàn văn:`** — MỘT trong ba: đã đọc (`full`, dẫn PMCID/đường lấy + phát hiện thêm
   nếu có) · chưa đọc được kèm lý do cụ thể (`partial`, không phải "chưa xong") · xem mục riêng
   (khi gói có mục ⓹ tổng hợp thẩm định của nhiều thẻ — trỏ đúng số mục). LUẬT CỨNG: `partial` ⇒
   KHÔNG được mang nhãn `Áp dụng ngay`, bất kể chứng cứ mạnh đến đâu — giới hạn về QUYỀN TRUY CẬP
   không phải giới hạn về CHẤT LƯỢNG.
8. *(ẩn, không viết ra)* — mọi số liệu ở khối 3 PHẢI khớp đúng chiều với khối 5; đây là điều
   `kiem_mau_the_chung_cu_tuan.py` không kiểm được bằng máy (cần đọc hiểu), bác sĩ tự soát khi duyệt.

## Ví dụ tối giản (điền placeholder)

```markdown
**[W99-01] <Chủ đề> — <Cochrane/RCT/SR-MA/Guideline> — Cân nhắc (ưu tiên đọc #1)**
Điều gì thay đổi: <câu kết luận thực hành tự đứng được>. <1-2 câu bối cảnh thêm nếu cần>.
Nguồn: <thiết kế> · *<Tạp chí>* <năm> · PMID <số> · doi:<doi> · <đăng ký/chuẩn báo cáo nếu có>
Hiệu số như nguồn báo cáo: <số liệu nguyên văn, kèm CI/I²/cỡ mẫu, kèm mức GRADE của nguồn>.
Ai bị ảnh hưởng: <quần thể đích, ngữ cảnh ngoại trú>.
Rủi ro nếu áp dụng sai: <cách hiểu sai cụ thể> | Nếu bỏ qua: <hậu quả cụ thể của việc không cập nhật>.
⚠️ <giới hạn tự khai của nguồn, hoặc [CẦN XÁC NHẬN TẠI ĐƠN VỊ] cho phần Việt Nam chưa tra được>.
Thẩm định toàn văn: <full, dẫn PMCID + phát hiện thêm | partial, lý do cụ thể>.
```

## KHÔNG làm (có chủ ý, để mẫu này không phình to hơn cần thiết)

- KHÔNG thêm khối PICO tách riêng — "Điều gì thay đổi" + "Ai bị ảnh hưởng" đã phủ đủ P/I/C/O,
  thêm một khối PICO hình thức sẽ lặp lại thông tin dưới dạng khác, không tăng khả năng đọc.
- KHÔNG thêm tag chuyên khoa hình thức (vd `[Hô hấp]`) — thẻ ưu tiên tự do đã làm việc này đủ tốt
  qua 5 tuần thực tế; ép vào một danh mục cứng sẽ có ngày không khớp chủ đề liên chuyên khoa.
- KHÔNG bắt buộc mọi thẻ cũ (W33–W36) phải viết lại theo mẫu 8 khối — mẫu áp dụng cho thẻ MỚI từ
  tuần này; `kiem_mau_the_chung_cu_tuan.py` chấm thẻ cũ ở mức khoan dung hơn (xem docstring tool).

**Cần bác sĩ kiểm chứng.** Mẫu này ghi lại thực hành ĐÃ CÓ, không phải áp đặt thực hành mới.
