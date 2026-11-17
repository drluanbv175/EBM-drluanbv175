# 18/11/2026 — Hoàn thiện kết nối Claude API cho hệ nghiên cứu: báo cáo cũ, đo độ đúng, lấy kết quả batch, trần chi phí, prompt caching

## Bối cảnh

Bác sĩ hỏi: «Vấn đề kết nối API Claude với hệ thống nghiên cứu y khoa có đề xuất giúp hoàn thiện cho tôi không».

Tôi đo hiện trạng trên đề tài BTM, nơi ba công cụ đã chạy thật ngày 17/11, rồi đề xuất 5 mục. Bác sĩ chọn cả 5.

## Năm khoảng hở đo được

1. **Báo cáo cũ mà không ai biết.** Lượt kiểm A12 và phản biện máy chạy 17/11 lúc 17:58–17:59. Đề cương nộp được sinh
   lại lúc 20:14. Báo cáo không ghi mã băm của tệp đã kiểm, nên không cách nào biết nó đã cũ.
2. **Chưa đo độ đúng của máy.** Có 24 phát hiện phản biện máy và 9 cặp A12 cần xem, nhưng chưa ai duyệt. Vì vậy chưa
   biết máy đúng bao nhiêu phần.
3. **Batch hội đồng G3 nộp 17/11 nhưng chưa lấy kết quả.** Ngoài ra, `buoc --goi-api` lấy kết quả xong sẽ TỰ NỘP ngay
   batch kế tiếp (tính phí). Tức là không có cách «chỉ lấy».
4. **Không có trần chi phí tháng.** SerpApi và Consensus đều có trần, Claude API thì không.
5. **Không dùng prompt caching.** Hội đồng batch gửi lại nguyên tệp agent làm system prompt cho mỗi yêu cầu.

## Đã làm

Ở repo y khoa:

- **Trần chi phí tháng** (`api_claude_nc.kiem_ngan_sach`):
  - Mọi lượt gọi và mọi batch được ước chi phí TỐI ĐA trước khi gửi (token vào ước + toàn bộ `max_tokens`).
  - Nếu số đã tiêu trong tháng cộng ước tối đa vượt trần ⇒ `HetNganSach`, không gửi.
  - Mặc định 20 USD/tháng; đổi bằng `EBM_API_CLAUDE_TRAN_USD_THANG`. Giá trị ≤ 0 nghĩa là khoá hẳn; gõ nhầm (không
    đọc được) cũng tính là khoá.
- **Sổ chi phí** `~/.ebm-api-claude-chi-phi.json`:
  - Ghi số tiêu THẬT theo `usage`, gồm cả token ghi cache và đọc cache.
  - Lượt bị cắt cụt hay bị từ chối vẫn được ghi, vì API vẫn tính phí.
  - Mỗi batch chỉ ghi MỘT lần theo id.
  - Sổ hỏng ⇒ chặn, không ghi đè. Sang tháng mới ⇒ đếm lại từ 0.
- **Bảng giá**: đủ các model hiện hành và đời trước, lấy từ tài liệu Claude API (skill `claude-api`, bảng chụp
  03/11/2026). Model chưa có giá ⇒ không gọi, vì không kiểm được trần.
- **Prompt caching**:
  - Bật `cache_control` cho system prompt của hội đồng batch (tệp agent) và của kiểm A12 (cùng lời dặn cho mọi lô).
  - KHÔNG bật cho phản biện máy: chỉ một lượt, ghi cache tính 1,25× mà không ai đọc lại.
- **`hoi_dong_cong_batch.py buoc --goi-api --chi-lay`**: chỉ lấy kết quả, không nộp batch kế tiếp. Phần bị chặn vì
  «tài liệu đổi sau khi khởi tạo» được in rõ và trả mã 1. Lần chạy thật đầu tiên in «0 yêu cầu: không còn gì» và che
  mất phần bị chặn; lỗi này đã được vá cùng đợt.
- **Mã băm đề cương**: báo cáo A12 và phản biện máy ghi thêm `tep_sha256`.
- **`tools/duyet_kiem_may_api.py`** (mới; chỉ dùng thư viện chuẩn):
  - `tinh-trang`: báo báo cáo cũ hay còn hiệu lực. Báo cáo chưa có mã băm thì suy theo thời điểm sửa tệp; không
    khẳng định được thì báo ⚪, không báo xanh.
  - `phieu`: dựng phiếu đánh số các mục cần duyệt.
  - `ghi --loi "<nguyên văn bác sĩ>"`: ghi nhãn đúng/sai/không rõ, chạy khô mặc định. Từ chối khi phiếu cũ hơn báo
    cáo, khi số nằm ngoài phiếu, hoặc khi một mục có hai nhãn khác nhau.
  - `do`: tỷ lệ đúng = đúng / (đúng + sai), theo công cụ và mức. Máy KHÔNG tự gắn nhãn.

Ở repo gốc:

- Giác quan hòm việc `giac_quan_kiem_may_api` (⑦t):
  - báo cáo cũ hoặc hỏng ⇒ 👤 ưu tiên 2; lệnh in ra chỉ chạy khô;
  - còn mục chưa duyệt ⇒ 👤 ưu tiên 3.
- Agent `kiem-chung-trich-dan`, `binh-duyet` và `_HOI-DONG-CONG.md` được dạy phần mới.

## Kết quả đo thật

- **Mục 3 (bác sĩ duyệt lấy kết quả):** batch `msgbatch_01MxYCZtmAPQngMQM2ZEzMoE` trả 8/8 kết quả đạt khuôn. Tổng
  502.999 token vào và 24.697 token ra, ≈ 0,63 USD theo giá Batch, đã ghi vào sổ. Không nộp batch nào mới.
  - G3-T1 và G3-T3: biên bản hợp lệ; cả người chấm chuyên môn lẫn giám khảo đều kết luận «đạt có lưu ý». Chưa ghi
    `--ap-dung`, chờ bác sĩ.
  - G3-T2 và DP-G3-1/2: bị chặn đúng luật, vì đề cương nộp đã đổi sau khi khởi tạo. Khởi tạo lại (`--lam-lai`) là một
    lượt tính phí mới, phải hỏi bác sĩ.
  - Lượt batch này nộp trước khi có cache nên 0 token cache. Từ lượt sau, yêu cầu cùng vai sẽ đọc từ cache.
- **Mục 1:** `tinh-trang --tat-ca` nhận ra cả hai báo cáo BTM là CŨ (suy theo thời điểm, vì chưa có mã băm). Giác quan
  hòm việc báo 2 việc 👤 ưu tiên 2.

## Kiểm

- Repo y khoa: `tests/test_api_claude_hoan_thien_20261118.py` có 40 phép kiểm; tính cả test API cũ là 115 phép kiểm.
  Kiểm đột biến 31/31 đỏ đúng chỗ. Hai đột biến sống sót ở lượt đầu đã được vá bằng cách siết phép kiểm: nhánh trần ≤ 0
  bị phép so «vượt trần» che, và cờ «số không thấy trong abstract» chưa có ca phủ.
- Repo gốc: `tools/test_giac_quan_kiem_may_api_20261118.py` có 7 phép kiểm. Kiểm đột biến 5/5 đỏ.

## Bài học

- **Một lệnh «tiếp tục» gộp cả việc miễn phí lẫn việc tính phí thì không dùng được khi bác sĩ mới duyệt phần miễn phí.**
  `buoc --goi-api` vừa lấy kết quả vừa nộp bước sau. Mỗi bước tính phí phải tách được thành một lệnh riêng.
- **Báo cáo của máy phải ghi mã băm của thứ nó đã đọc.** Không có mã băm, báo cáo cũ trông y hệt báo cáo mới.
- **«0 việc còn lại» không được che phần bị chặn.** Phần không đi tiếp được phải in ra kèm lý do và đổi mã thoát.
