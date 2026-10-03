# 01/10/2026 — Mục 1 chốt an toàn quét KHÔNG hết cây (chạm trần 25 s / 1.000.000 tệp) vẫn báo 🟢 — lỗ hổng tiềm ẩn, chưa đo được lần xảy ra
Rà lại `tools/sync_safety_check.py` sau #66/#69: `_iter_files` chạm trần thời gian hay trần số tệp thì `return` IM LẶNG, nên
`check_conflict_copies` không phân biệt «quét hết, sạch» với «chưa quét tới» ⇒ 🟢. Mục 5 (`.git`) gặp đúng tình huống ấy đã báo 🟡
«chưa soi hết» từ BH133; bản vá cap 16/09 sửa cùng họ âm tính giả nhưng cho trần SỐ LƯỢNG. **Theo số đo thì chưa từng xảy ra:** Mac
01/10 đi hết 180.498–180.501 tệp trong 0,9–3,6 s (hai phiên đo độc lập), xa trần 25 s; máy Windows chưa đo. **Vá:** `_iter_files(trang_thai=…)`
fail-closed — `du=True` chỉ đặt khi os.walk kết thúc tự nhiên, bị cắt thì kèm `ly_do` («quá 25s», «quá N tệp»); mục 1 quét chưa hết mà
chưa thấy bản sao chặn ⇒ 🟡 kèm lý do; đã thấy ⇒ vẫn 🔴, thêm dòng «chưa soi hết». Mục 4 giữ nguyên (tín hiệu tham khảo, docstring đã
chấp nhận quét một phần). Nơi gọi chỉ DỪNG ở mã 2 (`phai_dung_som` của `dong_bo_tat_ca.py`, `Chay Viec Mac.command`) nên 🟡 mới không
chặn làn nào. **Kiểm:** 3 test mới (27/27 đạt), BH133 ✓, `ruff` sạch; 9 đột biến (`python -B`, xoá `__pycache__`, chạy trên bản chép
NGOÀI OneDrive để khỏi đẻ bản sao xung đột, phục hồi khớp SHA-256) đều đỏ đúng chỗ: bỏ qua cờ · luôn 🟡 · khởi đầu `du=True` · hai trần
không ghi lý do · bị cắt mà vẫn `du=True` · có bản sao chặn mà hạ 🟡 · 🔴 nuốt dòng «chưa soi hết» · mục 1 quên truyền `trang_thai`.
Không thêm mục BH: chốt bài học chỉ nhận lỗi ĐÃ xảy ra.
