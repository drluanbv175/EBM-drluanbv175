# 02/10/2026 — MCP `pubmed-search` trên Windows khởi chạy chập chờn vì lớp bọc kết thúc bằng `os.execvpe`, mà `os.exec*` Windows không thay tiến trình (BH146)

**Triệu chứng.** Sau khi cài `uv` trên máy Windows (01/10) và kiểm MCP `pubmed-search` bằng bắt tay thật qua stdio
(`initialize` → `tools/list`, đúng lệnh khai trong `.mcp.json`), có lượt nối được, có lượt đứt sau ~4–5 s (EOF), không đổi gì giữa
các lượt. Đo 6 lượt mỗi cách trên máy Windows thật: qua lớp bọc bằng python **3/6**, qua `uv run` đúng `.mcp.json` **5/6**, trong
khi `uvx pubmed-search-mcp` chạy thẳng **6/6**. Máy chủ khi lên được: 0.7.5, 41 công cụ.

**Nguyên nhân gốc.** `tools/mcp/chay_pubmed_search_mcp.py` kết thúc bằng `os.execvpe(lenh[0], lenh, env)` (viết cho macOS, nơi nó
thay hẳn tiến trình). Trên Windows `os.exec*` KHÔNG thay tiến trình: nó tạo một tiến trình MỚI rồi cho tiến trình hiện tại thoát
ngay với mã 0 (đo: cha `poll()` = 0 sau vài giây trong khi con vẫn chạy) và không bọc dấu nháy đối số có dấu cách. Với MCP, bên
gọi (`uv run`, Claude Code) thấy lớp bọc «đã xong» trong khi stdio vẫn cần nối vào máy chủ ⇒ lúc nối được, lúc mất. *Cơ chế từng lượt
hỏng chưa tách riêng* (cái nào mất stdio, cái nào bị kéo theo) — chỉ có hai thứ đo được: trước vá hỏng chập chờn, sau vá không.

**Vá.** `chay_may_chu(lenh, env, *, la_windows=None)`: POSIX giữ `os.execvpe`; Windows chạy máy chủ như tiến trình CON
(`subprocess.call`, stdin/stdout/stderr kế thừa nguyên — không chèn lớp đệm vào kênh JSON-RPC), chờ nó và trả ĐÚNG mã thoát; tệp
thực thi phân giải theo PATH của `env` truyền cho con (`shutil.which(..., path=env["PATH"])`) vì CreateProcess tìm theo PATH của
tiến trình CHA; không chạy được ⇒ mã 1 + một dòng ở stderr. `la_windows` là tham số để ca thử Windows chạy được ở mọi nền (CI Ubuntu
lẫn Windows). `main()` gọi `chay_may_chu`. Đo lại sau vá: qua lớp bọc bằng python **15/15**, qua `uv run` từ thư mục lồng
`tools/mcp` **12/12**.

**Chốt BH146** (`tools/chot_hoi_quy_bai_hoc.py`): hợp đồng tĩnh bằng ast (mọi lời gọi `os.exec*` nằm TRONG `chay_may_chu`; `main()`
gọi nó — khớp dòng THI HÀNH, không khớp chữ trong docstring) + hành vi ngoại tuyến trên tệp thật: Windows chờ con rồi trả đúng mã 7
và không gọi `os.execvpe` · stdio nối thẳng · đối số có dấu cách nguyên vẹn · phân giải theo PATH của `env` · POSIX vẫn `os.execvpe`
đúng đối số và không chạy con · lỗi ⇒ mã 1 + stderr · mặc định theo `os.name` hai chiều. Kèm 8 ca pytest
`tools/test_chay_pubmed_search_mcp_windows_20261001.py` (đạt 3/3 lượt, ruff sạch).

**Kiểm đột biến** (`python -B`, xoá `__pycache__`, sao lưu + `cmp` trước/sau mỗi phép): 10/10 bị chốt BH146 bắt — Windows quay lại
`execvpe` · POSIX đi đường con · bỏ phân giải PATH · không trả mã thoát · không chờ con (`Popen`) · lỗi trả 0 · mặc định không theo
`os.name` · nối đối số thành một chuỗi · chuyển hướng stdout · `main()` gọi `os.execvpe` trần. Lần đầu **M3 (bỏ phân giải PATH) LỌT**
chốt (pytest có ca đó, chốt chưa) ⇒ bổ sung ca (g) rồi đo lại mới đủ 10/10. Pytest: 9/9 đột biến đầu bị bắt, phục hồi `cmp` đúng.
Ruff `chot_hoi_quy_bai_hoc.py`: 56 lỗi tồn trước = sau (không thêm lỗi).

**Cài `uv` (việc của máy, không phải lỗi).** `uv` 0.12.21 cài ở `C:\Users\Admin\.local\bin` (tải bản phát hành chính thức, khớp
SHA-256), bản sao lưu PATH ở `C:\Users\Admin\ebm-backup-truoc-dong-bo-20261001\`; app Claude phải khởi động lại mới thấy PATH mới.

**Không phải lỗi của lớp bọc — còn treo.** Gọi tra cứu thật (`unified_search`) trả «pubmed error» vì NCBI chặn IP của mạng máy này
(chuyển hướng `misuse.ncbi.nlm.nih.gov`, CLAUDE.md §5: gỡ chặn chỉ bằng liên hệ `info@ncbi.nlm.nih.gov` hoặc chờ; mặc định của
bác sĩ là VPN BẬT). Việc phê duyệt máy chủ MCP của dự án trong giao diện app và khởi động lại app là của bác sĩ; `claude` CLI không
có trong PATH máy này nên chưa chạy được `claude mcp get pubmed-search`.

**Số hiệu.** Tôi định dùng BH143 nhưng PR #79 (đã merge) lấy BH143, #80 lấy BH144, #81 lấy BH145 ⇒ BH146. Chốt BH68 (mã bài học
phải duy nhất) sẽ bắt nếu một PR khác cũng lấy BH146 — rà lại trước khi gộp.
