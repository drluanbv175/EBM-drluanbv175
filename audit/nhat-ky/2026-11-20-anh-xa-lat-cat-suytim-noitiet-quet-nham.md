# 20/11/2026 — Lát cắt SuyTim_NoiTiet bị quét nhầm watchlist chung (ánh xạ chỉ có cấp gốc)

**Hiện tượng.** Phiếu tháng EndNote 2026-11 (`cap_nhat_thang_thu_muc_endnote.py`) xếp «Tiếp cận chẩn đoán và điều trị suy
tim» vào nhóm ƯU TIÊN với lý do «SuyTim_NoiTiet: 2 guideline/đồng thuận mới; 11 tổng quan/RCT mới». Bác sĩ duyệt chạy bản
nối tiếp. `ops/orchestrator.py --topic "SuyTim_NoiTiet" --online` (run `20261120T121255-suytim-noitiet`) quét A2 theo
watchlist «Suy tim — tiên lượng & điều trị»: 24 ứng viên, **0 bài về suy tim + nội tiết**. Quét lại đúng mục watchlist
riêng «Suy tim + bệnh nội tiết (tuyến giáp, thượng thận, cường aldosteron, u tủy thượng thận)» (đã có, đang bật): 90 ngày
ra 0 guideline, 0 RCT, 1 scoping review dịch tễ, còn lại là ca lâm sàng. Tín hiệu «2 guideline mới» là của lượt quét sai.

**Nguyên nhân.** `EBM-Dashboards/giam-sat-chu-de.json → muc` chỉ ánh xạ CHỦ ĐỀ GỐC → watchlist. Gốc của
`SuyTim_NoiTiet` là `SuyTim` → watchlist chung. `tools/chu_de_resolver.py` tra `muc.get(<gốc>)`, không có đường khai riêng
một lát cắt. Orchestrator và phiếu tháng đều đi qua resolver nên cùng sai.

**Vá.**
- `chu_de_resolver.resolve()`: khoá trong `muc` trùng TÊN LÁT CẮT (không phải tên gốc) thắng ánh xạ của gốc; khi phân giải
  theo gốc hoặc theo tên watchlist, chỉ trả lát cắt có watchlist HIỆU LỰC khớp (lát cắt khai riêng không bị A4/B2 của
  watchlist chung kéo theo, và gõ tên watchlist riêng ra đúng lát cắt của nó).
- `kiem_phu_giam_sat.py`: khoá lát cắt trỏ tới watchlist không tồn tại/đã tắt ⇒ báo TRỎ SAI như khoá gốc.
- Dữ liệu (ngoài git, bác sĩ duyệt «Có, khai ánh xạ»): `giam-sat-chu-de.json` thêm `SuyTim_NoiTiet` → mục watchlist nội
  tiết; sao lưu `giam-sat-chu-de.json.bak-20261120-anh-xa-lat-cat`. Resolver cũ bỏ qua khoá này nên dòng dữ liệu vô hại
  tới khi PR gộp.

**Kiểm.** `tools/test_orchestrator_ops.py` thêm 3 ca (55 xanh). Đột biến: (1) bỏ ưu tiên khoá lát cắt ⇒ 1 ca đỏ; (2) bỏ lọc
lát cắt theo watchlist hiệu lực ⇒ 1 ca đỏ; phục hồi ⇒ xanh. So resolver cũ/mới trên 319 truy vấn thật (mọi tên watchlist,
lát cắt, gốc): khác đúng 4, cả 4 là SuyTim_NoiTiet chuyển sang watchlist nội tiết.

**Bài học.** Tín hiệu «có guideline mới» của phiếu tháng phải truy về ĐÚNG lượt quét của lát cắt đó trước khi đề xuất
token. Hai lát cắt khác chủ đề (NoiTiet · ChanDoan_DieuTri_DongMac) mang con số ứng viên giống hệt nhau (2/8/3) là dấu hiệu
chúng đang dùng chung một lượt quét.
