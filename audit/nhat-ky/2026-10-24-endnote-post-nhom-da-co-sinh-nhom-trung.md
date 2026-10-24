# 24/10/2026 — EndNote: bước ⑧ post vào nhóm ĐÃ có ⇒ sinh nhóm trùng tên; nay không post, bài thiếu vào hàng chờ (BH170)

## Sự cố
- Bộ năm bước ⑧ (`tools/xuat_goi_cap_nhat.py` → `nap_endnote_chu_de.py --file <dashboard> --ap-dung`) chạy cho
  «Tiên lượng suy tim» và «VKDT tổng hợp» (bản 20261024) ⇒ thư viện có thêm hai nhóm trùng tên: group 133 (3 bài, tạo
  24/10 12:25 UTC) cạnh 145 (14 bài, tạo 11/10); group 135 (1 bài) cạnh 150 (41 bài). Công cụ chỉ in «⚠ … gộp tay».
- Nguyên nhân: `EndNoteMac.dang_vao_nhom` gọi `post records in ids in window … as "<tên>" of type "CUSTOM"` cho bài chưa
  nằm trong nhóm. Docstring (đo 11/10) ghi post «CỘNG THÊM vào nhóm đã có» — SAI với EndNote hiện hành. MCP
  `endnote_dua_vao_nhom` (BH167) chỉ chặn khi tên đích có ≥2 nhóm; có đúng MỘT nhóm thì vẫn post.

## Đo (24/10/2026)
- Từ điển AppleScript: máy không có Xcode nên `sdef` báo lỗi; đọc thẳng `EndNote 2025.app/Contents/Resources/EndNote.sdef`
  (bản 22.4.1.23104). Lệnh nhóm chỉ có `post records in` (theo TÊN, «Post the specified list of records as a group»),
  `get records in` (theo tên), `get groups` (danh sách tên). Không có lớp group, không có định danh nhóm, KHÔNG có lệnh thêm
  bản ghi vào nhóm đã có.
- Đo trên BẢN SAO thư viện (`.enl` + `.Data/sdb`, không PDF; ngoài OneDrive; mở bằng `open -g`, cửa sổ riêng tên
  «BanSaoDoNhom-Claude-20261024.enl»; thư viện thật không bị ghi), đếm lại sdb.eni theo group_id sau mỗi lệnh:
  - post 1 bài vào tên đã có nhóm từ phiên trước (group 171) ⇒ nhóm MỚI 146 (1 bài); 171 không đổi.
  - post bài khác vào CÙNG tên, cùng phiên, 25 giây sau ⇒ nhóm MỚI 158; 146 và 171 không đổi.
  - tên mới: post ⇒ tạo 159; post lần hai 25 giây sau ⇒ nhóm MỚI 160.
  - `get groups` đếm 3 lần tên đầu, 2 lần tên mới.
  ⇒ post vào tên đã có LUÔN sinh nhóm mới, kể cả nhóm vừa do post tạo trong cùng phiên. Việc «đợi nhóm đăng ký»
  (`cho_nhom_dang_ky`, 11/10) không cứu được.
- Giả thuyết bộ nhóm (group set) bị loại: mọi nhóm «EBM · …» đều nằm ở gốc (không thành viên của bộ nhóm nào trong
  `misc` code 17).

## Đã làm
- `tools/nap_endnote_chu_de.py`:
  - CHỐT TRUNG TÂM: `EndNoteMac.dang_vao_nhom` đo sdb.eni theo group_id (`EndNoteMac.nhom_theo_ten` → `endnote_suc_khoe`).
    Tên đích đã có nhóm ⇒ `NhomDaCo`; không đọc được hoặc thành viên không giải được ⇒ `KhongDoDuocNhom`. Không post trong
    cả hai trường hợp.
  - `xep_vao_nhom` (bước ⑧): chưa có nhóm ⇒ post (tạo đúng một), đo lại sdb.eni tới khi thấy (`cho_nhom_dang_ky`, ≤30 giây).
    Đã có ⇒ KHÔNG post; bài chưa nằm trong nhóm nào cùng tên vào HÀNG CHỜ `~/.ebm-endnote-cho-vao-nhom.json` (riêng máy,
    biến `EBM_ENDNOTE_CHO_VAO_NHOM`). Bài bác sĩ đã kéo vào nhóm được dọn khỏi hàng chờ ở lượt sau. Không đo được ⇒ không
    post, không ghi hàng chờ. Nhóm vừa post trong CÙNG lượt `nap_nhieu` mà chưa hiện trên đĩa ⇒ bản kế tiếp không post lần hai.
  - `--cho-vao-nhom ["<tên>"]`: liệt kê, đo lại và dọn hàng chờ. Có tên ⇒ EndNote chỉ hiện các bài chờ (`show records in`)
    để bác sĩ ⌘A rồi kéo vào nhóm.
  - Báo cáo: dòng «🛎 Nhóm đã có (group_id …) — KHÔNG post … recNum …».
  - Docstring đính chính phép đo 11/10.
- `tools/mcp/endnote_ebm_mcp.py`: `endnote_dua_vao_nhom` với tên đã có MỘT nhóm ⇒ KHÔNG post (chạy khô báo
  `se_ghi_hang_cho`; `ap_dung` ghi hàng chờ). ≥2 nhóm / không đo được vẫn từ chối như BH167.
- `tools/endnote_suc_khoe.py`: `doc_cho_vao_nhom` (tệp hỏng ⇒ lỗi, không coi là rỗng), `cho_vao_nhom_con_lai` (đo theo
  group_id), `tinh_trang.cho_vao_nhom` (None khi không đo được).
- `tools/tu_de_xuat_viec.py` (hòm việc): 👤 «N bản ghi EndNote chờ bác sĩ kéo vào nhóm …» và «nhóm … đang tách N nhóm
  cùng tên — gộp tay».

## Đo trước/sau (`endnote_suc_khoe.nhom_trung_ten`)
- Thư viện THẬT (chỉ đọc, bản sao tạm): 160 nhóm, 2 tên trùng: «Tiên lượng suy tim…» (133: 3 · 145: 14), «VKDT…»
  (135: 1 · 150: 41). Thư viện thật KHÔNG bị ghi trong phiên này.
- Bản sao, chạy công cụ đã vá (`--ap-dung --khong-tom-tat`, cấu hình và hàng chờ trỏ sang bản sao):
  - «Tiên lượng suy tim» 20261024 và «THA ngoại trú» 20261019: nhóm đã đủ bài ⇒ không post.
  - Tái hiện đúng sự cố: `--ten-nhom` trỏ vào nhóm đơn 144 «Cập nhật chứng cứ — Thận» ⇒ «🛎 … KHÔNG post», 17 recNum vào
    hàng chờ.
  - Số nhóm 164 → 164; group 144 vẫn 7 bài; danh sách `nhom_trung_ten` trước = sau.

## Kiểm hồi quy
- `tools/test_endnote_khong_post_nhom_da_co_20261024.py` (14 test): EndNoteMac thật trên sdb.eni giả; bước ⑧ với EndNote
  giả mà post luôn sinh nhóm mới; hàng chờ (khớp tên theo khoá, dọn khi nhóm được tạo lại), trạng thái, hòm việc, CLI;
  dưới pytest không ghi tệp thật.
- Sửa fixture theo hành vi đo (KHÔNG nới assertion): `_EndNoteGia` (test 11/10), `_EnGia` (test 18/10, 21/10) bỏ mô hình
  «post cộng thêm»; EndNoteMac dựng tay trong test khoá ghi/kết nối và BH169 khai `nhom_theo_ten` (tên nhóm mới).
- Đột biến 11/11 bị bắt đúng test: bỏ chốt EndNoteMac · bước ⑧ luôn post · bỏ cả hai lớp (test tích hợp đỏ) · MCP post
  vào nhóm đã có · không đo được coi rỗng · không dọn hàng chờ · bỏ chốt pytest · không nhớ nhóm vừa tạo · hàng chờ bỏ qua
  thành viên · hòm việc bỏ hàng chờ · thành viên hỏng coi rỗng.
- Chốt BH170 bắt 4/4: bỏ chốt EndNoteMac · bước ⑧ luôn post · không đo được coi rỗng · không ghi hàng chờ.

## Còn lại cho bác sĩ
- Gộp 2 tên trùng trên thư viện thật bằng giao diện EndNote: kéo nhóm ít bài (133, 135) vào nhóm kia (145, 150), rồi xoá
  nhóm rỗng. Xoá nhóm không xoá bài.
- Đóng cửa sổ thư viện thử «BanSaoDoNhom-Claude-20261024.enl» trong EndNote (⌘W). Công cụ không đóng tài liệu vì
  `close document` làm EndNote sập.
