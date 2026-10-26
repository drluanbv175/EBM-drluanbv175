# 27/10/2026 — Tóm tắt ⑨ chấm AMSTAR-2 «Có một phần» ở mục chỉ có Có/Không

**Phát hiện.** Kiểm chéo độc lập lần 2 cho PMID 38770818 (Cochrane, SGLT2i ở bệnh thận mạn có đái tháo đường) bắt hai lỗi:
- mục 14 bị chấm «Có một phần», trong khi theo Shea 2017 (BMJ 358:j4008) «Có một phần» chỉ có ở mục 2, 4, 7, 8, 9;
- mục 3 bị chấm «Có» dù bài không nêu lý do chỉ nhận RCT.

Hai lỗi này đưa mức tổng thể lên «cao»; mức đúng là «trung bình», vì có hai điểm yếu không then chốt (mục 3, mục 16).

Lỗi lọt qua cả người soạn lẫn người chấm lượt đầu. Thang trả lời ghi trong yêu cầu kiểm chéo («chỉ mục 11 và 15 không có Có một phần») cũng sai so với Shea. Quét toàn kho (44 tóm tắt AMSTAR-2) thấy thêm 3 bài chấm «Có một phần» sai mục:
- 42248063: mục 16;
- 42724101: mục 16;
- 42836514: mục 5 và 12.

Ba bài này đều đã có lỗi then chốt, nên mức tổng thể (thấp hoặc rất thấp) không đổi.

**Cách vá.**
- Cổng `kiem_tom_tat` có luật `_amstar2_sai_thang`: miền AMSTAR-2 có `ten` mở đầu «Mục n» hoặc «Mục n–m» mà chấm «một phần» ngoài mục 2, 4, 7, 8, 9 ⇒ chặn.
  - Mục gộp chỉ hợp lệ khi mọi mục trong khoảng đều cho phép «Có một phần».
  - Tên không đánh số thì bỏ qua.
- Cùng lúc dạy agent, ghi vào hai hướng dẫn:
  - `HUONG_DAN_DOC` luật 3: thang trả lời và quy tắc mức tổng thể theo Shea 2017;
  - `HUONG_DAN_KIEM_CHEO`: chấm phán quyết miền theo đúng thang của công cụ.

**Kiểm hồi quy.** Test `test_amstar2_co_mot_phan_chi_o_muc_2_4_7_8_9`.
- 3 đột biến đều làm test đỏ đúng chỗ rồi xanh lại: bỏ lời gọi luật · nới tập mục cho phép · bỏ rào «chỉ AMSTAR-2».
- 46 test đạt; ruff sạch.

**Việc kèm theo (ngoài repo, kho `~/.ebm-cache/tom-tat-chung-cu`).**
- Đã sửa và kiểm chéo lại PMID 38770818 (mục 3 «Không», mục 14 «Có», mức «trung bình») và 39465893 (câu quy ước trong mức tổng thể).
- Ba bài 42248063, 42724101, 42836514 sẽ bị cổng chặn khi dựng lại; mức tổng thể của chúng không đổi.
