# 10/10/2026 — G6-T3 diễn giải không có tệp để kiểm · sổ trạng thái đề tài ghi chung vào tệp doctrine

Bác sĩ quyết: «G6-T3 (diễn giải kết quả) đảm bảo các kết quả được diễn giải và trình bày một cách tốt nhất (bao gồm số
liệu, văn phong và bảng biểu)» · «G10-T3 (sổ cái đề tài): đảm bảo mỗi đề tài sẽ lưu trong thư mục riêng».

## Đo (10/10)

- G6-T3 (`dien-giai-ket-qua`) khai đầu ra là `G6_A7_ANALYSIS_SCRIPTS_<mã>.md` (tệp script của G6-T1) ⇒ bản diễn giải không
  có tệp riêng; `gen_research_docx --artifact interpretation` dựng docx từ JSON tự do; C1a có sẵn một G6b khuôn rỗng từ
  02/09. Không có gì máy kiểm được về số liệu, văn phong hay bảng biểu.
- G10-T3 (`so-cai-ghi-nho`) khai `G10_checkpoint.json` (sản phẩm của `run_g10_assemble`, không phải của agent sổ cái).
  Sổ trạng thái checkpoint của MỌI đề tài được dạy ghi vào tệp doctrine dùng chung `.claude/agents/_SO-TRANG-THAI-CHECKPOINT.md`
  (`dieu-phoi-nghien-cuu` dòng 55/100/107/144, `_VONG-LAP-KHEP-KIN.md`); hiện tệp chỉ có một khối kiểm thử, không khối đề
  tài thật nào ⇒ không cần chuyển dữ liệu.
- `clinical_checkpoint.py` chỉ kiểm ĐỊNH DẠNG ngày (`\d{4}-\d{2}-\d{2}`) — «2026-13-40» vẫn qua (test của lượt này bắt).

## Vá

Repo y khoa (PR xếp chồng trên drluanbv175/medical-ebm-automation#107):
- `tools/dien_giai_ket_qua.py` (mới): `mau --study` dựng `G6_DIEN_GIAI_<mã>.md` (5 mục cố định, Bảng kết quả chính 7 cột
  có cột «Nguồn kết quả»); `kiem --study [--thiet-ke] [--json]` kiểm SỐ LIỆU (ước lượng + hai cận KTC đọc được, cận dưới
  ≤ ước lượng ≤ cận trên, p hợp lệ, < 0,001 ghi «< 0,001», mỗi số CÓ trong tệp kết quả được dẫn — chỉ nhận tệp trong
  `06_ket_qua/` hoặc `06_phan_tich_R/output/`, đọc txt/csv/tsv/json/md/log/xlsx; một dấu thập phân thống nhất), VĂN PHONG
  («đã chứng minh», «chứng minh rằng», «khẳng định chắc chắn», «xu hướng/gần có ý nghĩa», «rất có ý nghĩa thống kê»,
  «p = 0,000»; ngôn ngữ nhân quả «gây ra»/«là nguyên nhân» với thiết kế không can thiệp; mục 2 nói ý nghĩa lâm sàng, mục 3
  có PMID/DOI, mục 4 nêu hạn chế), BẢNG BIỂU (chú thích «Bảng N.», hàng gạch, đủ cột, không ô trống, hết «[CẦN»).
- `hoi_dong_cong`: G6-T3 đầu ra `G6_DIEN_GIAI_<mã>.md` + kiểm máy gọi ĐÚNG `dien_giai_ket_qua.kiem`; G10-T3 đầu ra
  `SO_TRANG_THAI_<mã>.md` + kiểm máy: đúng schema bằng `clinical_checkpoint.parse_checkpoint_log/validate_entries`, mọi khối
  mở đầu bằng mã đề tài, `loai_nhiem_vu` nghiên cứu, cổng G0–G10, ngày có thật trên lịch và không lùi, mọi cổng có bản ghi
  APPROVED trong `approval_ledger.json` đều có khối (chỉ đối chiếu mốc — không xác minh chữ ký).

Repo gốc (PR này): `dien-giai-ket-qua.md` dạy hợp đồng; `so-cai-ghi-nho.md`, `dieu-phoi-nghien-cuu.md` (4 chỗ),
`_SO-TRANG-THAI-CHECKPOINT.md`, `_VONG-LAP-KHEP-KIN.md` chuyển tuyến NGHIÊN CỨU sang sổ riêng
`medical-ebm-automation/exports/<mã>/SO_TRANG_THAI_<mã>.md` (tuyến lâm sàng giữ tệp chung); `viet-ban-thao.md` viết Kết
quả/Bàn luận từ `G6_DIEN_GIAI_<mã>.md`; bảng §3 `dieu-phoi-g6/g10`; `_HOI-DONG-CONG.md` §1b mục 11.

## Kiểm

- `tests/test_dien_giai_so_trang_thai_20261010.py`: 46 ca.
- Đột biến CÓ lượt nền xanh: lượt 1 **14/16** — R5 (bỏ nhánh riêng cho «p = 0,000») lọt vì nhánh chung đã bắt (p = 0 <
  0,001) ⇒ bỏ nhánh thừa; R6 (bỏ rào «nguồn phải trong thư mục kết quả») lọt vì thiếu ca tệp nguồn CÓ THẬT ngoài thư mục
  kết quả ⇒ thêm ca test; lượt 2 **2/2**.
- Đo C1a (chỉ đọc, SHA-256 trước = sau): chưa có `SO_TRANG_THAI_<mã>.md` và `G6_DIEN_GIAI_<mã>.md` — đúng, đề tài chưa
  qua cổng nào và chưa tới G6; khối đầu tiên của sổ riêng ghi khi G0 PASS.
