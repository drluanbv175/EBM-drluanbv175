# 17/11/2026 — Kiểm lạc chủ đề tắt câm khi chạy bằng `python3`; nhật ký sức khoẻ API chỉ giữ một ô

Bác sĩ hỏi «còn vấn đề gì về kết nối API Claude», rồi duyệt «làm cả 2 mục». Cả hai lỗ hổng đều thuộc họ
«luật tắt mà không ai biết» (`2026-11-17-api-claude-cat-cut-im-lang-do-sai.md`, BH180).

## Mục 1 — cổng kiểm lạc chủ đề tắt câm dưới `python3` mặc định

**Đo 17/11/2026, máy Mac:**
- `python3` (python.org 3.14.6) KHÔNG có SDK `anthropic`;
- `~/.ebm-venv/bin/python` (3.14.6) có anthropic 2.9.0;
- `/usr/bin/python3` (3.9.6) có SDK nhưng thấp hơn sàn 3.11.

Skill `cap-nhat-chung-cu-y-khoa`, tác vụ lịch `goi-duyet-tuan-ebm` và CLAUDE.md đều gọi
`python3 tools/xuat_goi_cap_nhat.py …`. Cổng kiểm chủ đề chạy TRONG tiến trình đó (`verify_dashboard` nhập nó), nên dùng
đúng trình Python không có SDK.

**Chạy thử trên VKDT_TamThanKinh_20261113:**
- kết quả `skipped — Chưa cài SDK: pip install anthropic`, ghi vào tệp tạm, không tốn tiền;
- giác quan ⑦r trả `[]`: nó chỉ báo `skipped` khi lý do nhắc tên khoá, nên luật tắt câm dù khoá tốt;
- lượt bỏ qua còn GHI ĐÈ nhật ký sức khoẻ.

Kết quả của các lượt xuất gói trước không được lưu lại, nên KHÔNG đo được đã có bao nhiêu lượt bị bỏ qua kiểu này.

**Vá:**
- `check_dashboard_topic_relevance`: trình đang chạy thiếu SDK mà `~/.ebm-venv` có Python ⇒ chấm bằng tiến trình con chạy
  chính tệp này `--json` bằng Python của venv (`bin/python` hoặc `Scripts/python.exe`);
- nhận diện «đang ở venv» bằng `sys.prefix`, không bằng realpath tệp thực thi — Python của venv là symlink tới chính
  `python3` hệ thống;
- chống đệ quy bằng cờ `EBM_KIEM_CHU_DE_QUA_VENV`;
- tiến trình con lỗi, quá 900 giây hay trả rác ⇒ `error`, không bao giờ im thành `skipped`;
- dưới pytest KHÔNG BAO GIỜ chuyển tiếp: venv máy bác sĩ có SDK + kho khoá thật, chuyển tiếp ở đó là gọi API thật (rào
  BH181);
- thông điệp thiếu SDK nêu đúng trình Python;
- giác quan: lượt nào (`skipped` hay `error`) mang «cài SDK» ⇒ 🤖 ưu tiên 2. Cầu nối y khoa ghi thiếu SDK là `error`,
  trước đây bị đọc thành «kiểm khoá và tín dụng» — sai hướng sửa.

## Mục 2 — nhật ký sức khoẻ chỉ giữ MỘT lượt

`~/.ebm-api-claude.json` chỉ giữ một bản ghi. Có 8 công cụ ghi vào nó qua ba nơi ghi: cổng skill,
`tools/nhat_ky_api_claude.py` và cầu nối y khoa `tools/api_claude_nc.py`. Công cụ A lỗi 401, rồi công cụ B chạy ổn ngay
sau ⇒ lỗi của A bị xoá trước khi hòm việc kịp đọc.

**Vá:**
- khoá `theo_nguon` giữ lượt gần nhất của TỪNG công cụ; khoá cấp cao vẫn là lượt gần nhất, nên bản đọc cũ đọc như trước;
- nhật ký kiểu cũ được giữ làm mục của nguồn đã ghi nó;
- ghi qua tệp tạm rồi `os.replace`, để hai công cụ ghi cùng lúc không để lại tệp cụt;
- cổng nay ghi `nguon: check_topic_relevance` và bỏ tên cũ `«»` của chính nó.

**Giác quan xét từng công cụ:**

| Tình huống | Báo |
|---|---|
| Lỗi mà chưa ai gọi được sau đó | 👤 ưu tiên 1 — có thể là khoá/tín dụng |
| Lỗi mà công cụ khác gọi được SAU đó | 👤 ưu tiên 2 — khoá còn sống, lỗi riêng của công cụ |
| Thiếu khoá mà sau đó đã có lượt thành công | Im |
| Nguồn lạ | Nêu đúng tên, không đổ cho cổng kiểm chủ đề |

Tuổi ⚪ tính theo lượt MỚI NHẤT của mọi công cụ.

## Kiểm hồi quy

- **Test mới:**
  - `tools/test_api_nhat_ky_theo_nguon_20261117.py`: 30 chốt, kể cả một chốt chạy tiến trình con THẬT trên dashboard
    không có mục (dừng trước bước đọc khoá) và một chốt đối chiếu khuôn với cầu nối y khoa khi hai repo nằm cạnh nhau;
  - `medical-ebm-automation/tests/test_api_nhat_ky_theo_nguon_20261117.py`: 5 chốt.
- **Hai chốt khớp chặt khuôn cũ đã cập nhật** sang khuôn mới, vẫn khớp chặt.
- **Đột biến:**
  - gốc 16/16. M8 lần đầu LỌT vì lỗi phép thử (chỉ xoá nửa đầu thông điệp, nửa sau vẫn nêu trình Python), viết lại
    thành thông điệp cũ ⇒ bắt;
  - y khoa 4/4.
- Ba nơi ghi cho cùng kết quả trộn trên 3 đầu vào: nhật ký một lượt, nhật ký theo nguồn, tệp vắng.
- Nhật ký thật ở thư mục nhà không đổi sau mọi lượt test.

**Sau khi gộp:** `python3 tools/dong_bo_scanner_giam_sat.py --ap-dung` để đưa cổng mới tới hai bản chạy ngoài git
(`EBM-Dashboards/tools`, `EBM_MASTER/skill_assets`).
