# 17/11/2026 — Bộ kiểm ghi đè nhật ký sức khoẻ API THẬT và đọc kho khoá THẬT qua tiến trình con (BH181)

**Mã:** BH181 · cùng họ hai lỗi bộ kiểm sáng 17/11 (đọc kho khoá thật, ghi nhật ký thật — xem
`2026-11-17-api-claude-cat-cut-im-lang-do-sai.md`), nhưng qua đường GIÁN TIẾP mà lần vá trước không phủ.

## Phát hiện

Đang kiểm sức khoẻ khoá API cho bác sĩ: bản ghi cuối của `~/.ebm-api-claude.json` là
`14:24:51 · skipped · «Không có item nào để chấm.» · 0 mục` — không phải lượt chạy thật nào; nó đã GHI ĐÈ bản
`ok` thật lúc 13:30. Mọi chốt gọi thẳng `check_dashboard_topic_relevance` đều đã chuyển hướng `NHAT_KY_API`,
nên thủ phạm phải là đường gián tiếp.

Đo bằng `HOME` tạm cho từng tệp chạy `xuat_goi_cap_nhat.py --online` (5 ứng viên): chỉ
`tools/test_xuat_goi_cap_nhat_workflow_20260904.py` để lại nhật ký ở HOME tạm; nhật ký thật không đổi trong lúc đo.
Cơ chế: từ #402, `--online` kéo theo `--check-topic`; tiến trình con của `verify_dashboard` nạp
`check_topic_relevance`, đọc kho khoá THẬT (`_khoa_tu_kho`, có từ #402) và ghi nhật ký THẬT (có từ #405).
Dashboard mẫu không có mục nên CHƯA gọi API — chỉ cần mẫu có một mục là mỗi lượt CI/kiểm trên máy bác sĩ gọi
API thật bằng khoá thật, tốn tiền, và nhật ký hòm việc bị bóp méo.

## Cách vá

`check_topic_relevance.py` (2 bản khớp byte): `_cham_trang_thai_that(duong, that)` — dưới pytest
(`PYTEST_CURRENT_TEST`, được tiến trình con KẾ THỪA) mà đường đọc/ghi trùng tệp THẬT ⇒ từ chối: `_khoa_tu_kho`
trả rỗng, `ghi_nhat_ky_api` không ghi. Chủ động đo thật: `EBM_KIEM_API_THAT=1`. `_KHO_THAT`/`_NK_THAT` là bản
chụp đường thật lúc nạp, nên chốt vá `KHO_BI_MAT`/`NHAT_KY_API` sang tệp tạm vẫn chạy như cũ. Cùng luật CLAUDE.md
§4 cho khoá ký cổng G («dưới pytest khoá trỏ vào ~/.ebm-secrets ⇒ từ chối»). `cafes_suite._khoa_api` dùng chính
`_khoa_tu_kho` nên được rào theo.

## Kiểm hồi quy

- Đo lại thủ phạm với HOME tạm sau vá: không còn ghi nhật ký.
- `tools/test_check_topic_relevance_20261117.py::KiemThuKhongChamTrangThaiThat` — 4 chốt, gồm tiến trình con có
  HOME chứa kho khoá + nhật ký «thật».
- BH181 — đặt tạm biến kiểm thử, SDK giả ⇒ không client nào được dựng, nhật ký nguyên vẹn; mở rào đọc được.
- Đột biến 4/4 bị bắt (bỏ rào đọc · bỏ rào ghi · không mở được bằng EBM_KIEM_API_THAT · rào dựa «pytest đã
  import» — qua mọi chốt trong tiến trình, chỉ chốt tiến trình con và BH181 bắt).

## Bài học

Rào kiểm thử cho trạng thái ngoài repo phải dựa vào thứ tiến trình con KẾ THỪA (biến môi trường), không dựa vào
trạng thái trong tiến trình (`sys.modules`). Đường gián tiếp — một lệnh CLI được bộ kiểm chạy thật — là nơi rào
trong tiến trình không với tới. Khi một lệnh vốn ngoại tuyến bắt đầu kéo theo một lượt gọi mạng (ở đây `--online`
kéo `--check-topic`), phải rà lại MỌI bộ kiểm đang chạy lệnh đó.
