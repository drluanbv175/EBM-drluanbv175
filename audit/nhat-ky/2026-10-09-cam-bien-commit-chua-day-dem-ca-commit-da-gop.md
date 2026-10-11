# 09/10/2026 — Cảm biến «commit chưa đẩy» đếm cả commit mà nội dung đã gộp (trùng bản vá · gộp squash)

Bác sĩ giao: «Tiếp tục hoàn thiện hệ thống nghiên cứu của tôi». Hòm việc (`tools/tu_de_xuat_viec.py`, khối ⑦c) nhắc mỗi phiên
«Repo …: N commit chưa có trên remote nào — soi rồi commit/push», kể cả khi việc đã xong từ lâu.

## Đo (09/10)

`git rev-list --branches --not --remotes` ở hai repo: 6 commit. Soi tay từng commit với nhánh chính remote:

| Repo | Commit | Thật ra |
|---|---|---|
| gốc | `2bc10f9` (nhánh `claude/tin-hieu-chu-de-mu-20261003`) | `git cherry` «-»: bản vá đã có trên `origin/master` (rebase) |
| y khoa | `18decf9`, `b6ce823` | `git cherry` «-»: bản vá đã có trên nhánh chính |
| y khoa | `ab0f233`, `6bd5beb` (nhánh `claude/g2-o-mau-chung-icf-20261003`) | gộp kiểu SQUASH ở PR #78 (`33d3ef3`): thông điệp gộp liệt kê «* <tiêu đề>» của cả hai |
| y khoa | `4465a31` (nhánh `claude/g3-do-nhay-cum-20261009`) | việc DỞ THẬT của một phiên đang chạy |

5/6 là báo nhầm. Cảm biến vá 27/09 (BH119) đã nhìn đúng MỌI nhánh, nhưng «không có trên remote» được hiểu theo SHA — commit
đổi SHA khi rebase/cherry-pick/squash thì mãi mãi «chưa đẩy».

## Vá

`dem_commit_chua_co_tren_remote(duong, chi_tiet=None)` — giữ chữ ký và ngữ nghĩa trả về (số commit, nhánh), trừ đi:

1. **Trùng bản vá:** `git cherry <nhánh chính remote> <đỉnh nhánh>` đánh «-».
2. **Gộp squash** (`_commit_gop_squash`): một commit trên nhánh chính remote có dòng thông điệp (bóc «* » đầu, «(#n)» cuối)
   TRÙNG tiêu đề commit cục bộ, với ngày commit KHÔNG sớm hơn commit cục bộ (commit sửa SAU khi gộp mà giữ tiêu đề vẫn bị
   đếm); tiêu đề < 20 ký tự («wip») không dùng để suy.
3. **Nền** (`_nen_nhanh_chinh_remote`): nhánh chính khai báo (`kiem_cay_lam_viec.NHANH_CHINH`) → `origin/HEAD`; KHÔNG đoán
   `main`/`master` (repo y khoa có `origin/main` là nhánh bỏ). Không dò được nền, hoặc đầu ra `git cherry`/`git log` lạ ⇒
   KHÔNG lọc gì — báo như cũ (thừa an toàn hơn thiếu).

Commit đã gộp hiện thành MỘT dòng ⓘ («… NỘI DUNG đã có trên origin/… — không còn việc»), không tính vào danh sách việc.
Nhánh cục bộ cũ không bị xoá — xoá hay giữ là việc của bác sĩ/phiên chủ nhánh.

## Kiểm

- Đo lại trên hai repo thật: gốc (0, []) · y khoa (1, [`claude/g3-do-nhay-cum-20261009`]) — khớp bảng soi tay.
- `tools/test_tu_de_xuat_viec_20261009_commit_da_gop.py` — 8 ca (squash nhiều commit, squash PR một commit «(#n)», cherry-pick,
  sửa sau gộp cùng tiêu đề, tiêu đề ngắn, nhánh lẫn commit gộp + commit dở, vắng nền ⇒ không lọc, không đoán `main`);
  test 27/09 (BH119) vẫn xanh. Đồ gá: git ≥ 2.48 tự dựng lại `origin/HEAD` ở mỗi `fetch` — ca «vắng nền» đặt
  `remote.origin.followRemoteHEAD=never`.
- Đột biến 9/9 bị bắt (bỏ trừ trùng bản vá · bỏ dò squash · bỏ rào ngày · bỏ rào độ dài · liệt kê mọi nhánh · đoán
  `origin/main` · đảo dấu cherry · không bóc «* » · không bóc «(#n)»); tệp khôi phục byte-y-hệt. Lượt đầu D9 lọt ⇒ thêm ca PR
  một commit.
- `pytest tools/` cấu hình trần: 2677 qua, 33 bỏ qua; `ruff` sạch.
