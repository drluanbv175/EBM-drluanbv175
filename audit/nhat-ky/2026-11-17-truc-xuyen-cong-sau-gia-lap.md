# 17/11/2026 — Các trục nhất quán xuyên cổng còn «cần xem/chưa đủ» sau giả lập 16 đề tài; câu vỡ trong phiếu đồng ý

## Bối cảnh
Bác sĩ hỏi: «Bỏ 2 vấn đề của đề tài thật thì hệ thống đã đạt trạng thái hoàn thiện sau giả lập để hoàn thiện». Câu trả
lời trung thực lúc đó là «chưa hoàn toàn». `nhat_quan_xuyen_cong` trên 16 đề tài giả lập (lượt mã 3ad7989a) còn nhiều
trục «cần xem/chưa đủ»; mỗi trục được truy tới nguyên nhân trước khi sửa.

## Đo được — nguyên nhân ở mã, không ở dữ liệu giả lập
1. `ky_thuat_chon_mau` ⚪ ở 15/16: cách chọn ngoài 5 mã chỉ khai được qua `khac:<mô tả>`. Trục coi mọi «khac:» là chưa
   khai, nên đề tài tuyển liên tiếp hay chọn chủ đích mãi «chưa đủ».
2. `cau_hoi_gia_thuyet` (dự báo): chữ «nguy cơ» trong tên mô hình xếp mục tiêu phát triển mô hình thành mục tiêu phân
   tích cần giả thuyết định trước.
3. `loai_gia_thuyet`/`power` ⚪ ở tổng quan–gộp, dự báo, định tính: các thiết kế này không kiểm định theo lực, nên chỉ có
   một nơi ghi. Thêm vào đó, `canonical_design_code` đổi «sr_ma» thành «systematic_review», làm `loai_muc_12` rơi về
   nhánh «power».
4. `quan_the` ở 13/16: đăng ký TRDS mục 14 chỉ liệt kê tiêu chí, mất câu quần thể G1 («người trưởng thành quản lý ngoại
   trú»).
5. `trich_dan_tong_quan` ở 7/16: bộ sinh đề cương và A12 không đọc thiết kế G1 (A2) với bộ biến G3. DOI của Piaggio 2012,
   van Smeden 2016, Ogundimu 2016… chỉ có ở bảng căn cứ cỡ mẫu G3 nên không được quy về PMID.
6. `ma_tran_muc_tieu`:
   - MT-09: SAP không gọi tên biến cụm, biến sự kiện, biến mô tả.
   - MT-12: thống kê viên ký duyệt công thức phái sinh làm đổi dấu nguồn bảng G3, dù định nghĩa biến không đổi.
   - MT-12: mã thiếu khai lúc nhập liệu (sau khi PI duyệt bảng) là đổi bộ biến thật nhưng bảng không được soạn lại.

## Lộ ra sau khi sửa (lượt chạy lại)
Phép đo phải chạy hết mới thấy, vì trước đó các trục này «chưa đủ» nên không so.
- **Câu vỡ trong phiếu đồng ý G2, ở 11/16 đề tài:** «Dữ liệu nhận dạng được xoá/ẩn danh hoá trong vòng Bảng nối mã nghiên
  cứu… huỷ sau khi khoá dữ liệu năm sau khi kết thúc nghiên cứu». Khuôn chỉ có ô «trong vòng [CẦN] năm», còn người điền
  theo quy trình dữ liệu đã chốt lại nhét cả câu huỷ bảng nối vào ô số năm. Nay dòng này dựng từ quy trình đã chốt
  (`huy_bang_noi` + `luu_tru`); chưa chốt thì vẫn để ô cho PI.
- **Trục lệch cứng `mo_ta_thiet_ke` TK-02 ở 3 kịch bản:** câu cách thu thập tả «trích hồ sơ bệnh án» trong khi G2 khai
  tuyển mới tiến cứu. Trục bắt đúng. Lỗi nằm ở lời kịch bản, nay viết theo quy ước «Thu mới: …» như hai đề tài thật.
- **Trục lệch cứng `chon_mau_co_mau` ở RCT cụm:** SAP viết «biến cụm `…`», nhưng trục chỉ nhận chữ «chùm». Nay trục nhận
  «chùm|cụm|cluster», cùng tập từ với `_KY_THUAT`.
- **Phép thử trọn vòng là phép MÔ TẢ:** «16 passed» không có nghĩa G10 PASS. Trạng thái cổng, ô lỗi máy và lệch trục phải
  đọc từ báo cáo `state/gia-lap-tron-vong/*.json`.

## Đã sửa (repo y khoa)
- `nhat_quan_xuyen_cong`:
  - mã «khac:» liên tiếp/chủ đích/thuận tiện; «khac:không áp dụng» ⇒ bỏ trục;
  - loại trừ mục tiêu mô hình dự báo;
  - bỏ `loai_gia_thuyet` khi «chưa đủ» ở thiết kế không theo lực (hai nơi lệch vẫn báo);
  - TRDS 14 kèm quần thể;
  - biến chùm nhận «cụm».
- `g4_quality_gate.loai_muc_12` nhận mã chuẩn hoá `systematic_review`/`meta_analysis`.
- `g2_quality_gate`: TRDS 14 thêm khoá `population` khi G1 có quần thể (không có thì giữ nguyên khoá cũ).
- `danh_muc_trich_dan.VAN_BAN_CONG_TRICH`: một danh sách văn bản cổng dùng chung cho trục, bộ sinh đề cương và A12.
- `protocol_checklist_items.cap_doi_pmid_he_thong`: cặp chuẩn đề cương + bảng căn cứ G3, 22 cặp đối chiếu PubMed.
  `cap_doi_pmid_tai_lieu_chuan` giữ bất biến ⊆ `pmid_tai_lieu_chuan()` mà `check_de_cuong` R4 dựa vào.
- Đề cương nộp: tài liệu phương pháp chưa được nhắc tự nhiên thì dẫn một câu ở mục cỡ mẫu.
- `run_g4_auto`: SAP tự nêu «Biến cấu trúc của phân tích» (§4) và «Biến mô tả đặc điểm mẫu» (§3) từ ma trận đạt.
- `bang_bien_g3.dau_nguon` bỏ cột `nguoi_duyet` của `_bien-phai-sinh.csv`, vẫn nhận dấu kiểu cũ (bảng BTM không bị báo đỏ
  giả).
- `run_g2_auto`: dòng dữ liệu nhận dạng của phiếu đồng ý dựng từ quy trình đã chốt.
- Bộ giả lập:
  - PI soạn lại và duyệt lại bảng G3 khi bộ biến đổi;
  - ghi `_quy-trinh-du-lieu.csv` ở G2;
  - kịch bản khai `sampling_design`, `data_collection_method` theo quy ước của đề tài thật.

## Dạy agent (repo gốc)
- `viet-ban-thao`, `kiem-chung-trich-dan`: phạm vi TLTK/A12 theo `VAN_BAN_CONG_TRICH` và `cap_doi_pmid_he_thong`.
- `bien-so-nghien-cuu`: ký duyệt công thức không đổi dấu nguồn; mã thiếu/công thức mới ⇒ soạn lại bảng và PI duyệt lại.
- `thiet-ke-nghien-cuu`: SAP tự nêu biến cấu trúc và biến mô tả.
- `co-mau-nghien-cuu`: mã «khac:» được nhận.
- `dao-duc-dang-ky`: TRDS 14 có dòng «Population:».

## Kiểm
- `tests/test_truc_xuyen_cong_sau_gia_lap_20261117.py` 27 phép. Kiểm đột biến 20/20 đỏ đúng chỗ rồi phục hồi xanh:
  17 luật trục/sinh/bảng G3, 1 luật biến chùm, 2 luật phiếu đồng ý.
- Hai phép thử cũ khoá đúng hành vi vừa đổi có chủ ý:
  - Bất biến «cặp DOI→PMID ⊆ tập PMID chuẩn đề cương» được GIỮ, bằng cách tách hàm `cap_doi_pmid_he_thong`.
  - Phép thử trục giả thuyết định tính chấp nhận trục vắng; ý «không đem G3 ra so» giữ nguyên.
- Lượt sạch 16 kịch bản từ G0, khoá giả, số đọc từ báo cáo JSON:
  - 16/16 `PASS_G10_RELEASE_PACKAGE_LOCKED`;
  - 0 ô lỗi máy;
  - 16/16 đề cương nộp mã 0 (K1–K8);
  - **377/377 trục `nhat_quan_xuyen_cong` khớp** (20–25 trục mỗi đề tài).
- Lượt giữa (trước khi sửa phiếu đồng ý và trục chùm) chỉ có 12/16 G10 PASS, với 11 ô lỗi máy; lệnh test vẫn báo
  «16 passed».
- Ô «chưa có thông tin» (chỉ người thật điền: ký, xác nhận đời thực, số liệu sàng lọc…) còn 1217:
  G9 417 · G2 303 · G5 193 · G7 169 · G4 84 · G10 32 · G8 17 · G6 2. Bộ giả lập không bịa các ô này.

## Bài học
Khi một trục đang «chưa đủ», nó không kiểm gì cả. Sửa cho trục đủ dữ kiện thì phải chạy lại hết dây chuyền: lệch thật mà
trục đó lẽ ra phải bắt (câu vỡ trong phiếu đồng ý, lời kịch bản sai lộ trình đồng thuận) chỉ hiện ra lúc ấy. Và kết luận
về trạng thái cổng phải đọc từ báo cáo, không đọc từ việc phép thử mô tả «passed».
