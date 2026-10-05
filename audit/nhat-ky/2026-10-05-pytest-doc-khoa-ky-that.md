# 05/10/2026 — Bộ test repo y khoa đọc khoá ký THẬT (HMAC + Ed25519) của bác sĩ

**Phát hiện:** 04/10/2026 khi soát cổng G4 — `tools/gate_contract.py::_base_key_path()` trả
`~/.ebm-secrets/gate_approval_key` khi `EBM_GATE_KEY_PATH` vắng, kể cả dưới pytest; `tests/conftest.py`
không đặt biến đó. `_ed_private_dir()` cũng rơi về `~/.ebm-secrets/` (khoá riêng Ed25519). CLAUDE.md §0.5:
agent không đọc/chép khoá riêng.

**Đo trước khi vá (05/10/2026, Mac, medical-ebm-automation @ 6503375, `python -B -m pytest -q -p no:cacheprovider`):**
đầu dò TẠM (không commit) — `sitecustomize.py` nạp qua PYTHONPATH ở mọi tiến trình, móc audit PEP 578 CHẶN trước
khi mở nên không byte khoá nào được đọc; tự tiêm vào cả `env=` tường minh của tiến trình con; bọc
`_base_key_path`/`_ed_private_dir` để thấy cả lần chỉ tính đường dẫn.
- **78 test / 22 tệp** cố mở khoá thật: 71 ngay trong tiến trình pytest, 7 qua tiến trình con
  (`approve_gate.py`, `run_g9_auto.py`, `g4_quality_gate.py` — kế thừa môi trường, có `PYTEST_CURRENT_TEST`
  nhưng không có `EBM_GATE_KEY_PATH`).
- Khoá HMAC chung `gate_approval_key`: 555 lần. Khoá riêng Ed25519 `gate_ed25519_<VAI>.key` của CẢ 5 vai:
  10 lần (PI 5, INDEPENDENT_PEER_REVIEWER 2, STATISTICIAN/IRB/DATA_MANAGER 1).
- Bộ test vẫn **7261 đạt / 44 bỏ qua** (8 phút 32) khi mọi lần mở khoá bị chặn ⇒ không test nào CẦN khoá thật
  (khớp CI, nơi không có khoá). Danh sách tĩnh (grep 33 tệp «có ký mà không đặt biến») lệch danh sách đo được
  (22 tệp): nhiều test chạm khoá gián tiếp qua hàm kiểm sổ cái — chỉ phép đo động mới đúng.
- Tệp biến môi trường mà app/config nạp lúc import: 36 lần đọc (mọi tiến trình) — để ngoài phạm vi bản vá này.

**Vá (PR y khoa drluanbv175/medical-ebm-automation#91, commit `9f6f832`):**
1. `tests/conftest.py`: khoá GIẢ cho cả phiên đặt lúc import (ÉP, tiến trình con kế thừa) + fixture autouse
   cấp khoá giả MỚI cho từng test (khoá vai trò `<khoá>_<NHÓM>` và khoá Ed25519 nằm cạnh khoá giả, không lây
   giữa test). Test tự `monkeypatch.setenv` khoá khác vẫn thắng.
2. `tests/canh_bi_mat_that.py` (mới): chốt canh móc audit — CHẶN + ghi sổ mọi lần tiến trình pytest chạm
   `~/.ebm-secrets` (đọc, ghi, xoá, đổi tên, liệt kê, sao chép, liên kết); test chạm ⇒ đỏ lúc teardown; chạm
   ngoài test ⇒ phiên đỏ. Ghi sổ TRƯỚC khi ném vì `gate_contract._read_key` bọc `except OSError` (nuốt lỗi chặn).
   Miễn trừ duy nhất: ĐỌC tệp biến môi trường của app/config.
3. `tests/test_gate_ed25519_20260815.py`: fixture `ed_env` chỉ vá `_ED_PRIVATE_DIR`, nhưng `_ed_private_dir()`
   lấy thư mục CHA của `EBM_GATE_KEY_PATH` — với khoá giả toàn cục, 2 test đỏ và 3 test XANH NHẦM qua đường HMAC.
   Nay trỏ biến vào `priv/` và khẳng định `_ed_private_dir()`.
4. KHÔNG đổi `tools/gate_contract.py` (ranh giới thẩm quyền: hành vi ký thật giữ nguyên).

**Kiểm:**
- Đo lại bằng cùng đầu dò sau vá: 7284 đạt / 44 bỏ qua (9 phút 04, 231 tiến trình có đầu dò) — **0 lần mở tệp
  khoá**, kể cả ở tiến trình con; chỉ còn 1 test CỐ Ý tính đường mặc định
  (`test_env_key_override_ignored_outside_test_context`, mô phỏng ngoài pytest, không mở tệp).
- Test canh gác `tests/test_khoa_gia_va_canh_bi_mat_20261005.py`: 23 test, gồm 3 canary pytest con.
- Kiểm đột biến 14 phép trong worktree bản sao (sao lưu + cmp mỗi phép): **14/14 bị bắt**. Đáng ghi nhất: gỡ hẳn
  khoá giả (M3) ⇒ chốt canh đánh đỏ đúng **71/71** test trong tiến trình của danh sách đo trước vá (không thiếu,
  không thừa); 7 test qua tiến trình con KHÔNG bị chốt trong tiến trình thấy (đầu dò chặn ở con) — đúng giới hạn
  đã khai. Bỏ miễn trừ đọc (M6): Mac có tệp biến môi trường ⇒ phiên pytest từ chối chạy ngay khi nạp conftest
  (thông điệp chốt canh); máy không có tệp đó (HOME giả, như CI) ⇒ 2 test miễn trừ đỏ.

**Giới hạn còn lại (nói thẳng):** tiến trình con dựng `env=` từ đầu mà bỏ cả `EBM_GATE_KEY_PATH` lẫn
`PYTEST_CURRENT_TEST` thì gate_contract trong con coi là ngoài test và dùng khoá thật — không chốt nào trong
tiến trình pytest thấy được (đo trước vá: 0 trường hợp như vậy).

**Bác sĩ quyết:** (a) thêm chốt trong `gate_contract._base_key_path()`/`_ed_private_dir()` — dưới pytest mà
thiếu biến thì báo lỗi (phủ thêm tiến trình con kế thừa `PYTEST_CURRENT_TEST`); không đổi hành vi ngoài pytest
nhưng đụng gate_contract.py nên chờ duyệt. (b) app/config vẫn nạp khoá API thật từ kho secrets dưới pytest.
