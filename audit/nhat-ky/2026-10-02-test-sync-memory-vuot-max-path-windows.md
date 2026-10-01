# 02/10/2026 — `test_sync_memory_repo_con_20261001` đỏ trên Windows: tmp_path mặc định đẩy đường dẫn bộ nhớ vượt MAX_PATH 259 (lỗi của TEST, không phải công cụ; không cấp BH mới)

**Triệu chứng (đo 02/10/2026, máy Windows 11, Python 3.12.10).** `python -B -m pytest -q -p no:cacheprovider
tools/test_sync_memory_repo_con_20261001.py` ⇒ 1 đỏ / 42 xanh (43 ca). Ca đỏ:
`test_other_machine_pulls_child_memory_into_exact_slug_dir`, dòng `assert SM.sync_all(...) == 0` nhận mã 1 vì
`✗ pytest-tren-mac.md: không đồng bộ được (FileNotFoundError: [WinError 3] The system cannot find the path specified)`.
Cùng lệnh thêm `--basetemp` đường dẫn ngắn ⇒ 43/43 đạt (tự đo lại trên bản gốc `origin/master` a7f1914). CI Ubuntu xanh
nên không ai thấy; test và tính năng thuộc PR #79 (BH143), nhưng PR đó ghi «chưa chạy trên Windows thật».

**Nguyên nhân gốc.** Tên thư mục bộ nhớ Claude Code được TÍNH TỪ đường dẫn dự án (`claude_project_slug`: mỗi ký tự ngoài
`[a-zA-Z0-9]` ⇒ `-`, giữ nguyên độ dài khi ≤ 200). Test dựng cả cây trong `tmp_path` nên đường dẫn tmp xuất hiện HAI
lần trong đích một tệp bộ nhớ: ở phần đầu và trong tên thư mục dự án ⇒ độ dài đích ≈ 2·L + 64 + độ dài tên tệp (L = độ
dài thư mục tmp; công thức khớp số đo). `tmp_path` mặc định là `<temp>\pytest-of-<user>\pytest-<N>\<tên test cắt 30 ký
tự>`: L = 92 ở ca đỏ (`...\pytest-186\test_other_machine_pulls_child0`) ⇒ `pytest-tren-mac.md` dài **266** ký tự,
`MEMORY.md` **257** (vừa lọt), thư mục cha 247. Ranh là MAX_PATH 259 của Windows; `LongPathsEnabled = 0` trên máy này
(mặc định Windows, chỉ đọc, KHÔNG đổi — CLAUDE.md §0.5). Ca đỏ nằm sát ranh nên còn phụ thuộc tên người dùng và chữ số
của bộ đếm `pytest-<N>`: lỗi sẽ xuất hiện/biến mất theo máy.

**Vì sao KHÔNG sửa công cụ.** Đo trên bộ nhớ THẬT của máy này (02/10, chỉ đọc): `~/.claude/projects` 205 tệp, đường dẫn
dài nhất **144** ký tự; `memory-sync/` 200 tệp, dài nhất **117** — cách ranh hơn 100 ký tự. Không có ca thật nào vỡ nên
không thêm tiền tố `\\?\` (sẽ chạm `_real()`/chốt chống trộn, chưa đo ảnh hưởng).

**Vá (chỉ test).** Trong `tools/test_sync_memory_repo_con_20261001.py` ghi đè fixture `tmp_path` bằng
`tmp_path_factory.mktemp("s")` (docstring nêu công thức và số đo). L còn 63–64; đường dẫn dài nhất do test sinh ra đo được
**210** ký tự (dư 49). Diff +15 dòng, 0 dòng bị sửa/xoá — không đổi assertion nào, không đụng `tools/sync_memory.py`.

**Kiểm.** (1) basetemp mặc định: trước vá 1 đỏ/42 xanh, sau vá **43/43**. (2) `--basetemp=C:\Users\Admin\.ebm-worktrees\_t-sm20261002`
(tên mới: pytest XOÁ thư mục basetemp nên không dùng lại `_t` có sẵn): **43/43**. (3) ruff đích py311: sạch (cả bản gốc).
(4) `python -B tools/chot_hoi_quy_bai_hoc.py`: mã 0, BH143 ✓ trên Windows (chốt tự dựng cây bằng `tempfile` nên đường dẫn
ngắn, không tham chiếu tệp test này ⇒ không đột biến chốt); 36 mục ⚪ vì cây này là bản sao git trần — ⚪ không phải ĐẠT.
(5) Đột biến (`python -B`, xoá `__pycache__`, sao lưu + SHA-256 trước, tự phục hồi trong `finally`, khớp SHA sau từng phép):
**A** đảo bản vá (tmp tên 30 ký tự như mặc định) ⇒ 6 đỏ, ca gốc đỏ lại đúng `assert 1 == 0` ở dòng `sync_all` — chứng minh
fixture ngắn là nguyên nhân khiến test xanh; **B** máy mới kéo bộ nhớ repo y khoa vào thư mục bộ nhớ GỐC ⇒ 4 đỏ, đều bằng assertion
(hai ca mã thoát `2 == 0` vì chốt chống trộn bắt vụ trộn, hai ca so sánh thư mục dò) — không phải lỗi đường dẫn; **C** tắt chiều KÉO ⇒ 3 đỏ (`(2, 1, 3, 0) == (2, 2, 2, 0)`);
**D** bỏ chốt từ chối chồng thư mục ⇒ 1 đỏ (`assert 0 == 2`). Sau phục hồi 43/43. Tức ca từng đỏ vì lý do môi trường nay
bắt được lỗi thật của công cụ bằng assertion.

**Chưa làm / giới hạn.** Chưa chạy trên Mac/Linux (fixture dùng API chuẩn `tmp_path_factory.mktemp`; CI Ubuntu của PR sẽ
chạy). Chưa có làn CI Windows, nên lớp lỗi «test tự dựng đường dẫn dài theo tên máy/người dùng» chỉ lộ trên máy Windows —
thêm làn là quyết định của bác sĩ. Chỉ dư 49 ký tự: thêm tên tệp rất dài trong test này hoặc đặt `--basetemp` dài trên
Windows sẽ gặp lại. Công cụ vẫn báo `WinError 3` mơ hồ nếu một đường dẫn THẬT vượt 259 — chưa thêm gợi ý MAX_PATH vì máy
thật còn dư xa. Chưa chạy `sync_memory.py` thật trên Windows (chỉ bộ test).

**Ghi vào đâu.** `audit/nhat-ky/` theo quy ước «mỗi sự cố một tệp»; không sửa `audit/NHAT-KY-SU-CO.md`. Không cấp mã BH
mới (chỉ sửa test; BH143 giữ nguyên).
