# 25/10/2026 — Trích dẫn đề tài nghiên cứu: không lấy được toàn văn thì loại, chỉ giữ bài phù hợp nhất

**Loại:** luật thường trực mới do bác sĩ giao (không phải lỗi mã). Không có mã BH.

## Bối cảnh

Đề tài `btm-dtd2-ngoai-tru-BVQY175` (G0, chăm sóc thận ở người ĐTĐ típ 2 ngoại trú BVQY175). Danh mục trích
dẫn gom từ sàng lọc G0 có 66 bài, nạp vào nhóm EndNote «NC · Chăm sóc thận ĐTĐ típ 2 ngoại trú BVQY175
(btm-dtd2-ngoai-tru-BVQY175)». Sau làn Chrome có uỷ quyền (phiên 20261025-175303), đo trên thư viện thật:
62/66 có toàn văn; 4 bài không lấy được — SAGE (PMID 38647229) và OUP (PMID 41950426) chỉ có trang tóm tắt,
Semergen (PMID 41512580) chỉ cho xem trước, bài Tạp chí Y Dược Thực hành 175 (DOI 10.59354/ydth175.2023.227)
bị Kaspersky chặn vì chứng chỉ TLS sai miền.

Bác sĩ, nguyên văn: «Với các trích dẫn cho nghiên cứu không thể lấy được toàn văn hãy loại bỏ luôn cho tôi,
trích dẫn phải đảm bảo phù hợp nhất với nghiên cứu».

## Luật (khác kho chứng cứ)

- Danh mục trích dẫn ĐỀ TÀI là tài liệu tham khảo của đề cương/bài báo: chỉ giữ bài đọc được toàn văn VÀ
  gắn trực tiếp với một việc của đề tài (định nghĩa/chuẩn đo; số liệu đối chiếu cho đúng một kết cục; bối
  cảnh trong nước/khu vực; tổng quan đặt khoảng trống). Loại: thử hết OA/Unpaywall → làn Chrome → ghi sổ
  không truy cập mà vẫn thiếu toàn văn; lệch quần thể/kết cục; đề cương hay mô tả can thiệp chưa có số liệu;
  tóm tắt hội nghị; tổng quan trùng ý.
- KHÁC quy tắc kho chứng cứ (bác sĩ 23/10/2026, CLAUDE.md §6.2): ở kho chứng cứ, bài không có toàn văn được
  GIỮ ở dạng tóm tắt từ abstract (tối đa «cân nhắc»). Hai quy tắc không thay nhau.

## Cách làm (áp dụng lần đầu 25/10/2026)

1. `exports/<mã>/DANH_MUC_TRICH_DAN_<mã>.json`: sao lưu trước (`…bak-<ngày>-truoc-loai-bo.json`), chuyển mục bị
   loại sang khoá `loai_bo` (giữ `id`, thêm `nhom_ly_do` ∈ {`khong_lay_duoc_toan_van`, `it_phu_hop_voi_de_tai`},
   `ly_do`, `ngay`), ghi `quyet_dinh_loai_bo` (lời bác sĩ nguyên văn + tiêu chí). Không xoá hẳn — khôi phục bằng
   cách chuyển mục về `trich_dan`.
2. EndNote: CHỈ gỡ khỏi nhóm đề tài — bản ghi có thể thuộc chủ đề chứng cứ khác (lần này PMID 38712604, rec
   4310). Không thùng rác, không `endnote_loai_tru` (khoá `bo_qua` chặn nhập lại toàn thư viện — sai phạm vi).
3. KHÔNG sửa nhật ký sàng lọc G0 (`G0_TONG_HOP_BANG_CHUNG_<mã>.json`, A1): cổng G0 đòi đủ mọi PMID đã sàng;
   danh mục trích dẫn mới là danh sách dùng cho đề cương/bài báo.

Kết quả: loại 19 (4 không toàn văn + 15 ít phù hợp), giữ 47; đo lại trên thư viện thật 47/47 có toàn văn;
`g0_quality_gate.py` vẫn `DRAFT_READY_NEEDS_HUMAN_REVIEW` như trước khi loại.

## Bài học về điều khiển EndNote 2025 chạy nền (computer-use, app_*)

- Gỡ khỏi nhóm: bấm nhóm ở khung trái → app_click một dòng → app_zoom tiêu đề khung phải để kiểm «#rec» →
  app_menu Groups › Remove References From Group (không có hộp xác nhận).
- Ô «Search» của danh sách KHÔNG nhận phím Enter khi EndNote ở nền ⇒ không lọc theo PMID được; phải chọn
  theo dòng.
- Sau mỗi lần gỡ, danh sách tự cuộn lại ⇒ vị trí dòng đổi. Hai lần chọn trúng bài phải GIỮ (KDIGO 2022, bài
  Tây Ban Nha PMID 41741270) và đã KHÔNG gỡ nhờ kiểm #rec. Luôn zoom lại danh sách trước dòng kế và kiểm #rec.
- Giữ khoá ghi EndNote bằng một tiến trình nền (`nap_endnote_chu_de.nap_khoa_ghi().giu_khoa_ghi(...)`) suốt
  lúc thao tác giao diện, nhả bằng tệp dừng khi xong.
- Kiểm sau cùng bằng `endnote_nhom` (đọc `sdb.eni` theo group_id): đúng 47 bản ghi, `chua_co_tep` 0, không bản
  ghi nào trong 19 rec đã gỡ.
