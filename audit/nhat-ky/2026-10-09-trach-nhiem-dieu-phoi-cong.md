# 09/10/2026 — Trách nhiệm hoàn chỉnh của điều phối cổng: 203 tiêu chí bộ chấm có chủ · lệnh `trach-nhiem` · `cham-song` hết bỏ sót

Bác sĩ giao: «Từng cổng hãy đảm bảo với các Agent thực hiện một cách hoàn chỉnh các vấn đề của cổng đó và điều phối của
cổng đó chịu trách nhiệm về kết quả thực hiện nhiệm vụ của chính cổng đó».

## Hiện trạng trước khi vá (đo 09/10)

- Danh mục hội đồng (`medical-ebm-automation/tools/hoi_dong_cong.py`) có 2–5 nhiệm vụ THÔ mỗi cổng; 11 bộ chấm có **203**
  tiêu chí AUTO/HUMAN (đo bằng cây cú pháp, khớp tập mã phát ra khi chấm động 34 đề tài trong `exports/`) — **không tiêu chí
  nào gán cho ai**. Không công cụ nào trả lời «vấn đề nào của cổng còn hở, việc của agent nào hay người nào».
- 11 `dieu-phoi-gN.md` tự nhận «Bạn không phải owner» — không ai chịu trách nhiệm kết quả CỔNG.
- **Lỗi thật:** `hoi_dong_cong.cham_song` chỉ đọc `automatic_criteria` + `human_criteria`, trong khi báo cáo G2 dùng
  `human_approval_criteria`, G4/G8 `approval_criteria`, G6 `checks` (pass True/None/False) ⇒ điều phối G2/G4/G8 không thấy
  tiêu chí phê duyệt chưa đạt, điều phối G6 thấy «không còn tiêu chí chưa đạt» dù cổng BLOCKED.

## Vá

Repo y khoa (drluanbv175/medical-ebm-automation#100, xếp chồng trên #99):
- `PHAN_CONG`: mỗi tiêu chí ĐÚNG MỘT bên — nhiệm vụ agent (`G3-T1`) · vai NGƯỜI kèm nhiệm vụ agent chuẩn bị hồ sơ + lệnh
  (`STATISTICIAN@G3-T1`) · cổng tiền đề (`^G0,G1`; G10 `^*` = theo mục đích phát hành).
- `hang_tieu_chi`: chuẩn hoá 4 khuôn báo cáo; trạng thái lạ ⇒ REVIEW (không bao giờ «đạt»). `cham_song` dùng nó.
- Lệnh `trach-nhiem --study <mã> --gate GN [--json] [--ghi]` (chỉ đọc): chấm sống, gán từng tiêu chí chưa đạt, kiểm đầu ra
  từng nhiệm vụ áp dụng (điều kiện RCT/SR suy từ thiết kế đã chốt; điều kiện khác ⇒ điều phối khai), kết luận
  `DAT_TIEU_CHI` · `AGENT_XONG_CHO_NGUOI` (mã 0) · `AGENT_CON_VIEC` · `CHO_CONG_TRUOC` · `CHUA_PHAN_CONG` (mã 1) ·
  `KHONG_DO_DUOC` (mã 2). Cổng BLOCKED mà cổng tiền đề chưa PASS ⇒ `CHO_CONG_TRUOC` (bộ chấm dừng sớm ⇒ tự chấm cổng tiền
  đề theo bảng). `--ghi` lưu `hoi_dong/GN/trach_nhiem/TN-<mốc>.json` (thư mục con — không bị đọc thành biên bản hỏng) kèm
  SHA-256 hồ sơ `GN_*` và câu cam kết của điều phối cổng.

Repo gốc (PR này): 11 `dieu-phoi-gN.md` — vai «CHỊU TRÁCH NHIỆM kết quả thực hiện mọi nhiệm vụ của cổng», mục **4b** chép
bảng phân công của cổng (sinh từ `PHAN_CONG`, test đối chiếu) + 6 quy tắc, bước bàn giao kèm dòng «Trách nhiệm cổng», mục
Cấm, bước tự kiểm 5; `_HOI-DONG-CONG.md` §1b + khối bàn giao; `dieu-phoi-nghien-cuu.md` «giao cổng — nhận cổng» (chỉ nhận
khi mã 0, mã 1 trả về đúng điều phối cổng); workflow `hoi-dong-cong.js` bước 7 chạy `trach-nhiem --ghi`; `CLAUDE.md` §1 một
dòng luật. Ranh giới không đổi: không ký, không bật cờ, không sửa artifact cổng khác cho «xanh»; đo trách nhiệm không tốn
agent (không cần triệu tập hội đồng).

## Đo trên C1a (chỉ đọc — SHA-256 toàn thư mục đề tài trước = sau)

| Cổng | Kết luận phần agent | Việc agent còn lại (ví dụ) |
|---|---|---|
| G0 | AGENT_XONG_CHO_NGUOI | — (chỉ còn HUMAN-05..08 của PI) |
| G1 | AGENT_CON_VIEC | G1-AUTO-07 khoá đề cương lõi ở `gate_params.G1` |
| G2 | AGENT_CON_VIEC | G2-AUTO-03b ICF tiếng Anh lệch ICF tiếng Việt |
| G3 | AGENT_CON_VIEC | G3-AUTO-09 bảng độ nhạy chưa neo vào N · G3-AUTO-12 thiếu khai `n_clusters` |
| G4 | AGENT_CON_VIEC | G4-AUTO-10 §1/§2/§4/§5/§9/§10 SAP còn trống |
| G5–G10 | CHO_CONG_TRUOC | (G2/G4 chưa ký, chưa có dữ liệu thật) |

## Kiểm

- `tests/test_trach_nhiem_cong_20261009.py` (repo y khoa): 50 ca — phủ đúng tập mã từng bộ chấm (AST), tổng 203, ô phân
  công hợp lệ (tiền đề là cổng TRƯỚC; tiêu chí người của cổng cứng thuộc đúng vai ký), mục 4b chép đúng bảng, 4 khuôn báo
  cáo, lỗi `cham-song` cũ, phân loại/ưu tiên/mã thoát, nhiệm vụ có điều kiện, bản lưu `--ghi`, CLI.
- Đột biến **16/16** bị bắt (lượt đầu M14 «không đo được thành đạt» lọt ⇒ thêm ca bộ chấm lỗi mà còn dòng PASS).
- Nhóm test hội đồng/trọng tài/mirror/manifest: 224 qua.

**Đính chính trong phiên:** báo cáo giữa phiên ghi «~240 tiêu chí» rồi «213» — đếm cả dòng tiêu đề của tệp trích; số đúng
là 203 (test chốt).
