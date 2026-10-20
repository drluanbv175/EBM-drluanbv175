# 20/10/2026 — Sửa hai mục rụng điều kiện, sửa nhãn bộ vàng mục 17, gỡ chủ đề «Người lớn khó phát âm phụ âm»

**Bối cảnh.** Bộ vàng K1–K4 (20 mục, gắn nhãn 20/10) chỉ ra hai mục bị đánh dấu «rụng điều kiện»: mục 10 (CKM, AHA 2023)
và mục 17 (JBDS 2026, đái tháo đường quanh phẫu thuật chuyển hoá). Đối chiếu bằng toàn văn trong kho:
- **Mục 10 — S đứng vững.** Giai đoạn 2 gồm cả người chỉ có tăng triglyceride, tăng huyết áp hay hội chứng chuyển hoá.
  SGLT2i được ưu tiên cho bệnh thận mạn (nguy cơ trung bình trở lên theo KDIGO) và đái tháo đường típ 2. Mục lại ghi
  «Stage 2 (SGLT2i + RAAS)» cho mọi người.
- **Mục 17 — S là sai.** Nhãn S do Claude soạn dựa trên tóm tắt. Toàn văn PMC13074134 cho thấy:
  - típ 2 giảm 50% khi bắt đầu chế độ ăn giảm thể tích gan (Bảng 2);
  - típ 2 sau mổ giảm 35–50% (Bảng 4);
  - típ 1 «có thể cần» giảm 30–50% và không bao giờ ngừng (Bảng 5).

  Câu «giảm insulin còn 50%» khớp Bảng 2. Bài học: nhãn bộ vàng dựa trên tóm tắt cần đối chiếu toàn văn khi kho có sẵn.

**Bác sĩ 20/10/2026: «Sửa nhãn và duyệt bản dựa».**
- Bộ vàng: mục 17 từ «Đ Đ S» thành «Đ Đ Đ» (`--ghi-de`, ghi kèm căn cứ toàn văn và nguyên văn lời bác sĩ). Số mục rụng điều
  kiện: 1/18.
- Dashboard (ngoài git, có sao lưu `.bak-20261020-sua-dieu-kien`), chỉ sửa trường `action`; cổng `verify_dashboard` mã 0
  trước và sau:
  - CKM ITEM-01: thay «Stage 2 (SGLT2i + RAAS)» bằng điều kiện đầy đủ theo toàn văn;
  - JBDS ITEM-14: thay «giảm insulin còn 50%» bằng mức theo típ và giai đoạn.
- Sổ cái hub: thẻ EVID-2026-0217 và EVID-2026-1328 sửa cùng câu (`recommendation`, `practice.action`), có dòng lịch sử, sao
  lưu qua `manage_ledger.backup_and_save`.

**Gỡ chủ đề «Người lớn khó phát âm phụ âm»** (bác sĩ: «Loại bỏ…»). Chủ đề vốn đã được đánh dấu «không phải chủ đề chứng cứ
lâm sàng» trong `giam-sat-chu-de.json`, nhưng 20/10 Claude nạp nhầm 6 trích dẫn vào EndNote khi bù phần thiếu. Đã gỡ:
- 6 thẻ hub (EVID-2026-0092 → 0097, `drop-nhieu` có sao lưu);
- dashboard và 9 bản phái sinh dời vào `EBM-Dashboards/_archive/PhatAmPhuAm_loai-bo_20261020/`;
- `library.json` từ 75 còn 74 mục;
- 6 PMID thêm vào `bo_qua` của EndNote;
- 6 bản ghi EndNote: bác sĩ tự chuyển vào thùng rác;
- dựng lại Antifacts. Lượt tuần dựng trang lúc 16:28, vài giây trước khi dời, nên trang dính một liên kết hỏng.

Bài học: khi bù «trích dẫn dashboard chưa có trong EndNote», phải loại trước các dashboard mà `giam-sat-chu-de.json` đánh
dấu không phải chủ đề lâm sàng.
