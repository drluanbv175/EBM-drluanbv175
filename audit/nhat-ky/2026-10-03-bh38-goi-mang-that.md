# 03/10/2026 — BH38 gọi mạng THẬT qua nhánh dự phòng Europe PMC ⇒ đỏ giả khi DNS chập chờn

**Triệu chứng.** Chạy bộ chốt trên cây ghép 13 PR (dữ liệu thật qua symlink): BH38 ✗ «chốt lỗi: RuntimeError: Europe PMC fallback thất
bại sau 3 lần: URLError: … nodename nor servname provided». Chạy lại riêng BH38 hai lần: đạt cả hai, trên cây chính lẫn cây ghép.

**Nguyên nhân.** Phản hồi giả của BH38 là `{"esearchresult": {"idlist": []}}`. Từ vá 22/09 (review:thu-nhan #3), bộ quét coi
esearchresult THIẾU `idlist`/`count` là LỖI NCBI, rơi xuống `search_europe_pmc` và gọi mạng THẬT, vì BH38 không truyền
`fallback_fetch_json`. Chốt «ngoại tuyến» hoá ra phụ thuộc DNS/Europe PMC.

**Vá (chỉ fixture, không đổi assertion).**
- Phản hồi giả hợp lệ: thêm `"count": "0"`.
- Truyền `fallback_fetch_json=cam_mang`: hàm văng `AssertionError` nếu nhánh dự phòng bị gọi.

**Kiểm.**
- Tắt mạng bằng cách vá `socket.getaddrinfo`: bản cũ ⇒ `RuntimeError … URLError`; bản mới ⇒ ✓.
- `chot_hoi_quy_bai_hoc` 🟢; `pytest tools/` xanh.
