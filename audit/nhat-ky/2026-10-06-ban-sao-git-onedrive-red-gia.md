# 06/10/2026 — 🔴 GIẢ «bản sao packed-refs giữ ref đã mất» chặn kéo cây chính; công cụ dọn bản sao trong .git

## Sự cố

Sau khi gộp y khoa #92/#93 + gốc #130/#131, `tools/sync_safety_check.py` báo **🔴 DỪNG** ở mục 5. Theo luật §0.7, không
được kéo cây chính về.

Nguyên nhân 🔴: `.git/packed-refs-C010000PK16BSL` của repo gốc — bản sao xung đột do máy Windows để lại (05/10) — được
báo là «giữ 4 ref mà bản đang dùng KHÔNG có».

## Đo (06/10/2026, Mac, chỉ đọc)

Cả 4 ref là **báo động giả**. Không có gì bị mất.

- **3 ref Codex** (`refs/codex/turn-diffs/checkpoints/…`):
  - Ba ref này trỏ thẳng vào đối tượng **tree**, không phải commit.
  - Bộ ref đang dùng có **đúng cùng giá trị**.
  - Bản cũ kiểm bằng `git merge-base --is-ancestor`. Lệnh này báo lỗi với tree («not a commit»), nên chốt coi là «mất».
- **1 nhánh** `claude/sad-blackwell-78627e`:
  - Nhánh đã gộp rồi xoá; commit `02c54cf` nằm trong `origin/master` và nhiều nhánh khác.
  - Bản cũ chỉ so với ref CÙNG TÊN, không xét commit đã nằm trong ref thật khác.

Ngoài ra còn rác — dấu vết hai máy từng ghi `.git` cùng lúc:
- Repo gốc: 27 tệp (FETCH_HEAD, reflog nhánh máy chủ).
- Repo y khoa: 16 tệp (index, FETCH_HEAD, ORIG_HEAD, reflog).

## Vá (gốc)

**`sync_safety_check.py` mục 5:**
- Một bản sao chỉ 🔴 khi **không ref thật nào giữ** đối tượng.
  - Commit ⇒ xét `for-each-ref --contains`.
  - Đối tượng khác ⇒ xét `--points-at`.
- Ref ma của chính bản sao (git đọc như ref thật) **không được tính** là nơi giữ.
- Thông báo chỉ thẳng tới công cụ dọn.

**`tools/don_ban_sao_git.py` (mới)** — mặc định chạy thử; thêm `--ap-dung` thì làm theo trình tự:
1. Quét như mục 5. Quét dở ⇒ mã 2, không làm gì.
2. CỨU ref chỉ bản sao giữ:
   - commit ⇒ nhánh `rescue/<ngày>/…`;
   - tree ⇒ `refs/rescue/<ngày>/…`;
   - bỏ nhánh máy chủ, cùng chính sách mục 5.
3. Bản sao `config`/`HEAD` khác bản đang dùng ⇒ bỏ qua, mã 1.
4. DỜI ra ngoài OneDrive, so SHA-256, ghi `manifest.json`.
5. KIỂM SAU: tập ref thật, HEAD, bản gốc còn nguyên, quét lại sạch.

Không xoá gì. Không đụng tệp đang dùng.

**CLAUDE.md §0.7** thêm một vế trỏ tới công cụ.

## Áp dụng trên cây chính (06/10/2026)

1. Sao lưu `git bundle --all` hai repo vào `~/ebm-backup-truoc-dong-bo-20261006/` (12 MB + 15 MB, đã verify).
2. Chạy công cụ:
   - repo gốc: dời 28 bản sao (27 rác + bản sao packed-refs, không ref nào cần cứu);
   - repo y khoa: dời 16 bản sao.
   - Bản dời nằm ở `~/ebm-backup-truoc-dong-bo-20261006/ban-sao-git/` (manifest.json).
3. Kiểm độc lập:
   - tập ref repo gốc trước/sau trùng khớp;
   - `git fsck --connectivity-only` sạch cả hai repo;
   - `git status` không đổi;
   - chốt an toàn mục 5 🟢, không còn 🔴.

## Kiểm

- `tools/test_sync_safety_check.py`: thêm 5 test (32 qua).
- `tools/test_don_ban_sao_git.py`: 10 test.
- Đột biến 13/13 bị bắt.

## Còn lại

- Máy Windows: sau khi OneDrive xanh, chạy `python3 tools/don_ban_sao_git.py` (chạy thử) rồi `--ap-dung`.
- Gốc rễ (hai máy cùng ghi `.git`) vẫn là luật «một máy tại một thời điểm».
