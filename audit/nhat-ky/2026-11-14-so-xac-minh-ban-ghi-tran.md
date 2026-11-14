# 14/11/2026 — Sổ xác minh nguồn gọi 80 bản ghi TRẦN là «xem tay» (CAN_XEM_TAY), trong khi máy tự sửa được

## Đo (14/11/2026, chỉ đọc)

- `python3 tools/so_xac_minh_nguon.py --bao-cao`: còn hiệu lực 6652/6746. Có 89 mục chưa/hết hạn, trong đó 80 mục được
  in là «lý do khác — không đọc được ngày xác minh — [MA] CAN_XEM_TAY». Chạy `--vong 3` không gỡ được các mục này.
  Nhật ký `2026-11-14-dinh-chinh-lich-nen-tien-kiem.md` ghi lại đúng nhận định đó.
- Đọc từng bản ghi trong `EBM-Dashboards/.so-xac-minh-nguon.json`: cả 80/80 đều VẮNG hẳn khoá `xac_minh_luc`. Không bản
  ghi nào có ngày sai khuôn. Theo nguồn gốc, chúng chia thành hai nhóm:
  - **52 thẻ `(hub-only)`** (28 PMID + 24 DOI). `--quet-ledger` tạo các bản ghi này ngày 12–13/11. Lệnh đó chỉ kiểm RÚT
    BÀI (`kiem_rut_luc` còn hạn, `ghi_chu_rut: ok`), không xác minh tồn tại. Không lượt nào chạy `--phu-mo-coi` sau đó:
    lượt đầy đủ gần nhất của `chu_trinh_chung_cu` là ngày 04/11.
  - **28 PMID `NC:<đề tài>`** (2 đề tài thật). Cầu NC⇄LS (`tools/cau_noi_nghien_cuu_lam_sang.py`) tạo bản ghi trần, chỉ
    có `loai`/`gia_tri`/`cac_dashboard`.
- Chạy khô `xac_minh_mot` trên cả 80 mục, không ghi sổ: **80/80 xác minh tồn tại THÀNH CÔNG** (PubMed 56, Crossref 24).
  Vậy nhóm này không phải việc rà tay. Đúng lệnh để sửa là `--phu-mo-coi`, công cụ có từ 16/08. Lượt đầy đủ của chu trình
  đã gọi lệnh này (BH120). Còn `--vong 3` chỉ tái kiểm định danh gom từ dashboard, nên không bao giờ chạm tới nhóm này.

## Gốc

`con_hieu_luc()` dùng chung một lý do «không đọc được ngày xác minh» cho hai ca. Ca thứ nhất: VẮNG ngày, tức bản ghi trần,
máy sửa được. Ca thứ hai: ngày HỎNG, tức dữ liệu sổ hỏng hoặc bị ghi tay, phải xem tay. `bao_cao()` xếp lý do đó vào nhóm
«khác» rồi gắn `[MA] CAN_XEM_TAY`. Nhóm này lại chỉ in lý do của mục ĐẦU TIÊN, nên một nhóm lẫn nhiều lý do bị đọc thành
một lý do duy nhất. Hệ quả là bác sĩ được khuyên rà tay một việc máy làm được, đúng lớp lỗi BH14 (lời khuyên lệch đòn bẩy).

Lỗi phụ phát hiện khi viết test: `_tuoi_ngay()` gặp giá trị ngày không phải chuỗi (số, danh sách) thì ném `TypeError` ở
`iso[:10]`, làm sập cả `--bao-cao`.

## Vá (`claude/so-xac-minh-can-xem-tay-20261114b`)

- `tools/so_xac_minh_nguon.py`:
  - Thêm hai hằng `LY_DO_CHUA_XAC_MINH_TON_TAI` («chưa xác minh tồn tại lần nào») và `LY_DO_NGAY_HONG` (giữ chuỗi cũ).
    Cả hai vẫn trả HẾT hiệu lực (fail-closed). Không nới hạn 180/30 ngày.
  - `bao_cao()` tách thêm nhóm «bản ghi TRẦN» cho PMID/DOI vắng ngày. Nhóm này có số đếm theo nguồn gốc (thẻ hub, đề tài
    NC, dashboard, không liên kết), lệnh sửa `--phu-mo-coi --vong 3` và mã mới `[MA] CAN_PHU_MO_COI`. URL trần vẫn ở nhóm
    xem tay vì `--phu-mo-coi` chỉ phủ PMID/DOI. Nhóm xem tay nay liệt kê MỌI lý do kèm số đếm.
  - `_tuoi_ngay()`: giá trị không phải chuỗi ⇒ None, nghĩa là hết hiệu lực, không sập.
  - `quet_ledger_hub()`: cuối lượt, nếu vừa tạo bản ghi trần thì in số lượng và nhắc chạy `--phu-mo-coi`.
- `tools/chu_trinh_chung_cu.py`: đọc `CAN_PHU_MO_COI` và nêu đúng việc cần làm, thay cho câu chung «xem phần ③④».
- Test mới `tools/test_so_xac_minh_can_xem_tay_20261114.py` (14 ca).

## Kiểm

- Đột biến: bắt 9/9, mỗi phép đều có lượt nền xanh, sao lưu `cp -p` và khôi phục khớp `cmp`. Chín phép gồm: bỏ nhánh vắng
  ngày · vắng ngày thành còn hạn (fail-open) · bỏ nhóm trần · nhóm trần nhận cả URL · xem tay chỉ in lý do đầu · bỏ rào
  kiểu trong `_tuoi_ngay` · bỏ nhánh chu trình · bỏ lời nhắc `--quet-ledger` · mất mã `CAN_PHU_MO_COI`.
- Test sổ/chu trình liên quan: 278 qua, 1 bỏ qua. Bộ chốt bài học: 178/178, không tái phát (có nối cây dữ liệu tạm).
- Sổ thật đo bằng mã mới (chỉ đọc): 80 mục chuyển từ `CAN_XEM_TAY` sang `CAN_PHU_MO_COI`, `CAN_XEM_TAY` còn 0. Độ phủ
  chưa đổi (6656/6750 lúc 13:18) vì chưa chạy lượt ghi.
- KHÔNG chạy `--phu-mo-coi` ghi thật lúc 13:22. Khi đó một phiên khác đang chạy bộ năm (`xuat_goi_cap_nhat.py --online` →
  `verify_dashboard`) và ghi sổ (13:09, 13:18). `--phu-mo-coi` đọc–sửa–ghi CẢ sổ, nên chạy song song có thể làm mất bản
  ghi của nhau, kể cả dương tính rút bài. Việc chạy được để lại cho lúc không có lượt nào ghi sổ.

## Bài học

Một mã «xem tay» phải nghĩa là máy THẬT SỰ không sửa được. Trước khi gắn nhãn đó, thử chạy khô bước sửa của chính công cụ
trên vài mẫu. Gộp «vắng» với «hỏng» làm mất thông tin về cách sửa, dù cả hai đều đúng là «hết hiệu lực».
