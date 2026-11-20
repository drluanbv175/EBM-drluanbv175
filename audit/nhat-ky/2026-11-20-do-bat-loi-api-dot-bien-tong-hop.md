# 20/11/2026 — Bộ kiểm ngữ nghĩa Claude API chưa từng đo độ bắt lỗi; tóm tắt PubMed thiếu thông tin ở một nửa số trục

**Bối cảnh.** Bác sĩ (20/11/2026): «Kiểm ngữ nghĩa chưa đo được độ bắt lỗi. Bộ kiểm Claude API hãy hoàn thiện; giải quyết vấn đề này một cách triệt để». Hòm việc báo: «chưa xong thì luật cứng K1–K4 lẫn bộ kiểm API chưa đo được bỏ lọt».

**Nguyên nhân.**
1. **Hai bộ kiểm không được đo bằng cùng thước.**
   - Luật cứng đã có thước đo không cần nhãn: đột biến tổng hợp tất định (`do_nhay_kiem_ngu_nghia.py`, báo cáo 14/11).
   - Bộ kiểm API chỉ chạy trên 56 đột biến tự do đang chờ bác sĩ duyệt, nên vẫn ở trạng thái «chưa đo».
   - Số tạm của lượt 19/11 (chiều 14/18, điều kiện 7/16) lấy trên đột biến do Claude soạn, nên dễ hơn thực tế.
2. **Đo thật bằng cùng thước (prompt v1, 316 lượt, ~2,1 USD) cho thấy:**
   - K3b (rụng điều kiện trong mục): 0/36.
   - K4 (nguồn nói ngược): 1/27.
   - K4b (mục đảo «không làm»): 20%.
3. **Nguyên nhân gốc là tóm tắt PubMed không đủ để phán:**
   - Ở 51% trục chiều và 59% trục điều kiện của mục gốc. Đa số là guideline mà tóm tắt chỉ có tiêu đề.
   - Mô hình còn bỏ qua mâu thuẫn ngay trong mục (tiêu đề khuyên làm, hành động ghi «KHÔNG…»).
   - Mô hình tin số liệu hơn câu kết luận khi hai thứ trái nhau.

**Cách vá** (PR gốc #448):
- **`tools/do_nhay_api_ngu_nghia.py`** — đặt bộ kiểm API lên CÙNG đột biến tất định với luật cứng (hạt giống 20261114).
  - Mẫu phân tầng 40 đột biến/lớp, có đối chứng ghép cặp với mục gốc.
  - Đột biến chỉ tính «bắt» khi bản gốc không bị nghi ở trục đó.
  - Chia DEV/TEST theo mục: chỉ soạn prompt mới trên DEV, số để quyết lấy trên TEST.
  - So cặp với luật cứng bằng McNemar chính xác; có độ bắt lỗi **kết hợp** (luật cứng HOẶC API), vì bộ năm chạy cả hai.
  - Có cột «phần nguồn đủ thông tin».
  - Báo cáo `quality/eval/kiem-cheo-ngu-nghia/do-nhay-api-*.md` không chép văn bản nguồn hay lý do của mô hình.
- **Prompt v2 `2026-11-20b`, nay là mặc định.**
  - Bước 0: phát hiện mục tự mâu thuẫn.
  - Căn chiều theo câu kết luận/khuyến cáo của nguồn; nguồn tự mâu thuẫn thì báo `false`.
  - Đối chiếu từng điều kiện và ngưỡng số.
  - Ghép **đoạn toàn văn** của chính nguồn qua cổng quyền từng tệp (fail-closed):
    - PMC giấy phép CC;
    - bản thảo tác giả NIH (bác sĩ quyết 15/10);
    - Unpaywall giấy phép mở;
    - bản Chrome chỉ khi NXB «cấm» còn uỷ quyền lúc gọi, hoặc NXB cho phép TDM.
  - Bộ chọn đoạn có bảng Việt→Anh và lọc đoạn chú giải viết tắt.
  - Kết quả trên mẫu: 107/114 mục gốc có đoạn toàn văn.
- **Bộ vàng.** `kiem_ngu_nghia_api.py --phien-ban --chi-co-nhan`, và `bo_vang … do --api --phien-ban`.
- **Cảm biến hòm việc.** In số đo thay cho «chưa đo được»; chưa có báo cáo cho prompt hiện hành thì hiện 🛎.
- **Bước xuất gói.** Lệch chỉ ở trục điều kiện thì hiện 🟡 (mức gợi ý).

**Số đo** (20/11/2026; đột biến TỔNG HỢP, không thay nhãn bác sĩ):

| Lớp đột biến (tập TEST) | API v1 | API v2 | Kết hợp v2 (luật cứng HOẶC API) |
|---|---|---|---|
| K1 đổi quần thể | 82% | 82% | 100% |
| K2 đổi ngưỡng quần thể | 87% | 80% | 100% |
| K2 đổi ngưỡng trong hành động | 45% | 33% (n=6) | 33% (n=6) |
| K3b rụng điều kiện trong mục | 0% | 9% | 9% |
| K4 nguồn nói ngược | 0% | 18% | 100% |
| K4b mục đảo «không làm» | 7% | 53% | 67% |

- Số trục «không phán được» trên mục gốc (48 mục), từ v1 sang v2: quần thể 19 → 3, chiều 24 → 6, điều kiện 29 → 9.
- API báo trên mục gốc: 12% → 46%, gần hết ở trục điều kiện.
- Trên 20 mục bộ vàng có nhãn (v2):
  - chiều báo giả 0/20, quần thể 1/20;
  - điều kiện bắt 1/1, nhưng 7/17 bất đồng với nhãn.
  - Soi kỹ thì nhiều ca là điểm lâm sàng có thật (ví dụ insulin −35–50% chỉ áp cho típ 2), nên có thể nhãn cần sửa. Phiếu phân xử nằm ngoài git: `EBM-Dashboards/derivatives/PHAN-XU-API-V2-BO-VANG_20261120.md`.
- Chi phí đo trong ngày: khoảng 4,0 USD.

**Giới hạn nói trước.**
- K3b và K4 tổng hợp có nhiễu nhãn khi đem đo bộ kiểm đọc ngữ nghĩa: điều kiện bị cắt khỏi hành động thường vẫn còn ở tiêu đề; đột biến chỉ lật một câu trong tóm tắt thì trái với toàn văn.
- Báo động trên mục gốc là cận trên của báo động giả.
- Bỏ lọt trên LỖI THẬT vẫn cần 40 mục phần B do bác sĩ gắn nhãn. Phần B chưa từng được chấm hay xem, nên vẫn là tập kiểm độc lập.

**Kiểm hồi quy.**
- Test: `test_do_nhay_api_ngu_nghia_20261120.py` (11), `test_kiem_ngu_nghia_api_toan_van_20261120.py` (17), cùng các test bộ vàng và bộ năm đã cập nhật.
- Kiểm đột biến 13/13 bắt (cổng quyền ×4, bộ chọn đoạn ×3, khoá có đoạn, bước xuất bỏ cổng quyền, cột kết hợp, phần phán được, `--chi-tap`, cảm biến). Hai ca LỌT ở lượt đầu (K9 nhãn, T13 cảm biến) đã được siết test.
