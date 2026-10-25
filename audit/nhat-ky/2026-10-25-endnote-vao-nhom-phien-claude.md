# 25/10/2026 — Đưa bản ghi vào nhóm EndNote ĐÃ có: phiên Claude làm được, không còn là việc của bác sĩ

## Hiện tượng

Từ BH170 (24/10), bản ghi mới thuộc một nhóm EndNote ĐÃ có không được `post … as` (luôn sinh nhóm trùng tên) mà vào hàng chờ
`~/.ebm-endnote-cho-vao-nhom.json`; hòm việc ghi «👤 bác sĩ kéo tay». Sau bộ năm 6 gói ngày 25/10, hàng chờ có 11 bản ghi/6 nhóm
trong khi bác sĩ đang ở máy Windows.

## Đo

- Phiên Claude làm trọn bằng điều khiển giao diện nền (computer-use) trên EndNote 2025:
  `nap_endnote_chu_de.py --cho-vao-nhom "<tên>"` hiện đúng các bài chờ → chọn từng dòng → menu **Groups › Add References To › <tên>**
  → `--cho-vao-nhom` đo lại theo group_id trong `sdb.eni`: «✓ Không còn bản ghi nào chờ đưa vào nhóm EndNote».
- ⌘A bị chặn khi điều khiển nền ⇒ chọn TỪNG dòng (đã biết từ bộ nhớ `endnote-dieu-khien-nen-tung-ban-ghi`).
- Lời nhắn cũ của công cụ chỉ «References → Add References To»: menu References KHÔNG có mục này (đo bằng danh sách menu) — đúng
  là Groups › Add References To.

## Sửa

- `tools/tu_de_xuat_viec.py::giac_quan_endnote` trả (ưu tiên, nhãn, mô tả, lệnh); việc «chờ đưa vào nhóm» mang nhãn 🛎 (máy làm
  được, cần một phiên chạy hộ), các việc khác giữ 👤 (thùng rác, gộp nhóm trùng tên).
- `tools/nap_endnote_chu_de.py`: lời nhắn chỉ đúng menu Groups › Add References To, nêu cách phiên Claude làm.
- CLAUDE.md §6.2 (dòng BH170) thêm một vế: phiên Claude làm thay được.
- Test cập nhật: `tools/test_endnote_khong_post_nhom_da_co_20261024.py`, `tools/test_endnote_ket_noi_20261019.py`.
