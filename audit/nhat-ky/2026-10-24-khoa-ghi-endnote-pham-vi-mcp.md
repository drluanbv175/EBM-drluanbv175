# 24/10/2026 — Khoá ghi EndNote kẹt 15 phút sau MỘT lệnh ghi của máy chủ MCP (BH169)

**Mã BH:** BH169 · **Tệp:** `tools/khoa_ghi_endnote.py`, `tools/mcp/endnote_ebm_mcp.py`, `tools/nap_endnote_chu_de.py`

## Hiện tượng (đo 24/10/2026)

Bộ năm `VKDT_TongHop_20261024` lúc ~19:15 bị bỏ bước ⑧ (`nap_endnote_chu_de.py`):
`DangCoTienTrinhKhacGhi: tiến trình 5186 đang ghi EndNote — bỏ lượt ghi này`. Pid 5186 là máy chủ MCP
`endnote-ebm`, giữ `~/.ebm-endnote-dang-ghi.json` từ ~19:05 sau MỘT lệnh ghi. `tom_tat_endnote_vi.py` và
`tom_tat_chung_cu_word.py dung --gan-endnote` cũng bị chặn như vậy.

## Nguyên nhân

1. Khoá giữ THEO TIẾN TRÌNH: lấy ở lần ghi đầu, nhả bằng `atexit`. Đúng cho script ngắn; sai cho máy chủ MCP sống
   cả phiên Claude ⇒ khoá chỉ hết khi quá `HAN_KHOA` (15 phút).
2. `luc_epoch` chỉ ghi lúc lấy khoá; tiến trình đang giữ khoá ghi tiếp không làm mới ⇒ sau 15 phút, tiến trình khác
   coi khoá của một tiến trình ĐANG ghi dở là treo và ghi chen.
3. Bẫy ẩn: máy chủ MCP nạp `khoa_ghi_endnote.py` một bản RIÊNG (`_mcp_kg`) khác bản `EndNoteMac` dùng. Trạng thái
   khoá là biến của mô-đun ⇒ một phạm vi mở trên bản riêng không thấy (và không nhả) khoá do lệnh ghi lấy.

## Cách vá

- `giu_khoa_ghi(ung_dung=None, ly_do=None)` (lõi `pham_vi_ghi()`): phạm vi MỘT thao tác. Khoá lấy trong khối được nhả
  khi khối NGOÀI CÙNG kết thúc, kể cả khi lỗi; có `ly_do` thì lấy khoá ngay khi vào khối; chạy khô không đụng tệp khoá;
  khoá theo tiến trình đã giữ từ trước giữ nguyên hành vi cũ (script ngắn không đổi).
- Mỗi lệnh ghi khi đang giữ khoá LÀM MỚI `luc_epoch`. Tệp khoá ghi nguyên tử (tệp tạm + `os.replace`).
- Thông báo macOS: một lần mỗi LẦN LẤY khoá (trước: một lần mỗi tiến trình — máy chủ MCP chỉ báo lần ghi đầu phiên).
- `nap_endnote_chu_de.nap_khoa_ghi()`: MỘT bản mô-đun khoá cho cả tiến trình (`sys.modules["_khoa_ghi_endnote"]`).
  Máy chủ MCP bọc MỖI `tools/call` trong `pham_vi_cong_cu()` trên chính bản đó ⇒ mọi công cụ ghi (hiện có và sau này)
  nhả khoá khi trả về. `endnote_loai_tru` ghi `~/.ebm-endnote.json`, không qua khoá EndNote.

## Kiểm hồi quy

- `tools/test_khoa_ghi_pham_vi_20261024.py` (12 ca), có TIẾN TRÌNH KHÁC thật thử lấy khoá: bị chặn trong lúc ghi,
  lấy được ngay sau lời gọi MCP; khoá làm mới không bị coi là treo sau 16 phút.
- Kiểm đột biến 8/8 đỏ đúng chỗ rồi phục hồi xanh: bỏ nhả khoá · bỏ làm mới `luc_epoch` · MCP không mở phạm vi · MCP
  nạp bản khoá riêng · không đăng ký `sys.modules` · bỏ `finally` · phạm vi nhả cả khoá tiến trình · ghi không nguyên tử.
- Chốt BH169: 4/4 đột biến đỏ (bỏ nhả · bỏ làm mới · MCP không mở phạm vi · MCP nạp bản riêng).
- Máy chủ MCP đang chạy trong phiên Claude chỉ nhận mã mới khi khởi động lại (mở phiên mới hoặc kết nối lại MCP).
