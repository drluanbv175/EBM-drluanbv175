# 01/10/2026 — Agent kê đơn chưa dạy dòng miễn trừ NLM; BH108 bỏ qua khối kiểm agent ở MỌI nơi vắng engine (đóng giới hạn (b) của mục «30/09/2026 (tối)» về RxNorm)
Giới hạn (b) của mục 30/09 (tối): `ke-don-an-toan.md` mục 8 tự liệt kê luật đọc kết quả `tra_thuoc_quoc_te.py` và chỉ trỏ §1ter ở
cuối — CHƯA nhắc dòng miễn trừ NLM, mà đây là agent DUY NHẤT gọi công cụ (BH108 kiểm điều đó) ⇒ §1ter luật 5 có thể không bao giờ
được áp dụng (họ BH41: luật không ai đọc coi như không tồn tại). Nhánh `claude/ke-don-mien-tru-nlm-20261001` ở cả hai repo.
**Vá — agent (hai repo, khớp từng byte):** MỘT mệnh đề ở mục 8 — câu trả lời nào dùng kết quả RxNorm thì in ĐÚNG MỘT lần, nguyên văn,
dòng ở trường `mien_tru_nlm` của đầu ra (không dịch, không gõ lại từ trí nhớ); không chép vào artifact có cổng; `ema` không kèm; trỏ
§1ter luật 5. KHÔNG chép câu tiếng Anh vào agent — nguồn câu chữ duy nhất vẫn là hằng `MIEN_TRU_NLM` + doctrine.
`enforce_agent_guardrails.py` đổi 0 tệp; `sync_agents_to_codex.py --check` PASS 50 TOML. Repo y khoa: `.codex/agents/ke-don-an-toan.toml`
sinh lại bằng công cụ gốc cho đích `.codex/agents` (`expected_files(".codex/agents")`) — bản cũ 10.950 ký tự so với 17.271 (vốn nằm
trong nhóm mirror lệch); nhãn chữ thường theo chuẩn mà phiên đồng bộ mirror chạy song song báo bác sĩ đã chọn; CHỈ sửa đúng tệp này.
Tái khoá manifest agent: đúng 1 hàng `agent_source_manifest.csv` đổi, `MANIFEST_SELF_CHECK_SHA256` `e5b25222…422d` → `978aa1d3…65c32`
(bác sĩ duyệt trước khi commit — bước script ghi là cần NGƯỜI xác nhận).
**BH108 có điểm mù (đo được; bác sĩ đồng ý vá):** bước dò engine (`tra_thuoc_quoc_te.py` có tồn tại không) đứng TRƯỚC khối kiểm agent,
nên ở mọi nơi vắng engine — CI, Cloud một-repo, worktree gốc trần — chốt trả ⚪ ngay tại đó và khối kiểm agent không bao giờ chạy: đo
trên bản sao tạm, agent mất hẳn «`gan_dung`» mà chốt vẫn ⚪ «ngoài phạm vi». **Vá:** khối kiểm agent (5 chuỗi cũ + `khoang-trong`) lên
TRƯỚC bước dò engine; thêm đòi «`mien_tru_nlm`» NGAY trên dòng gọi `tra_thuoc_quoc_te.py chuan-hoa` (không khớp cả tệp — §0.8);
thông điệp đỏ mới không nêu tên engine (luật hẹp của `phan_loai`). Không lấy số BH mới (phiên đồng bộ mirror giữ BH143).
**Kiểm.** Repo y khoa: 305/305 test (16 tệp agent/manifest + `tests/test_rxnorm_mien_tru_nlm_20260930.py`); đột biến «quên đổi hằng»
đỏ đúng `test_regenerate_agent_manifest_check_mode_matches_locked_manifest`. Repo gốc: 5 test mới
(`tools/test_chot_bh108_20261001_khoi_agent_truoc_engine.py`) đạt cả khi có engine lẫn trần; trên bộ chốt `origin/master` đỏ ĐÚNG 3 ca
(thiếu miễn trừ · dời sang dòng khác · mất `gan_dung` khi vắng engine), đối chứng và ca «engine có mà mất CLI» vẫn đạt. Mức hàm, 6 đột
biến + 2 đối chứng: mã mới đúng 8/8, mã cũ chỉ bắt 1/6 đột biến (mất CLI). Đột biến TỆP THẬT (bỏ chuỗi ở mục 8): bộ chốt mã 1, BH108 ✗
đúng thông điệp mới ở cả hai chế độ — kéo theo BH91 (và BH83 khi trần) đỏ vì mirror Codex lệch agent bị đột biến, đúng việc của hai chốt
đó; phục hồi khớp `cmp`. Trọn bộ chốt sau phục hồi, chạy bằng `~/.ebm-venv/bin/python` (`python3` hệ thống thiếu `httpx` ⇒ phần hành vi
adapter của BH108 chỉ ⚪): nối engine (symlink lồng + nền Retraction Watch + log tuần, chỉ đọc) 116/142 ✓ · 26 ⚪ · 0 ✗ (BH108 kiểm
THẬT); trần 105/142 · 37 ⚪ · 0 ✗ (BH108 ⚪ sau khi khối agent đã chạy và đạt). `pytest tools/` trần 1.851 đạt · 31 bỏ qua · 0 lỗi;
`compileall`, chốt đa nền (🔴 0) và smoke `tu_de_xuat_viec --gon` như CI; ruff bộ chốt 56 lỗi sẵn có (trước = sau), tệp test mới sạch.
**Giới hạn nói thẳng:** (a) agent được DẠY in dòng miễn trừ — vẫn không kiểm được một phiên cụ thể có in khi trình cho bác sĩ (giới
hạn kiểm doctrine-text, họ BH39/BH42); BH108 chỉ đòi chuỗi có mặt trên dòng mục 8, không hiểu nghĩa câu. (b) Khớp theo DÒNG: tách mục 8
thành nhiều dòng sau này có thể làm BH108 đỏ — đỏ lộ ra và sửa được, chọn thay cho xanh im lặng. (c) 81 tệp `.codex/agents` còn lại của
repo y khoa chưa đụng (việc của phiên đồng bộ mirror); giữa hai PR, PR nào merge SAU phải sinh lại `ke-don-an-toan.toml` từ `.md` mới.
**Bài học:** trong một chốt, mọi phép kiểm tệp TRONG git phải đứng TRƯỚC bước dò nguyên liệu NGOÀI git — đặt ngược thì ở mọi nơi vắng
nguyên liệu (đúng những nơi CI chạy) phần kiểm trong-git thành ⚪, xanh mà chưa đo.
