# 01/10/2026 — Mirror `.codex/agents` mà repo y khoa TRACK lệch 79/84 tệp ngay từ ngày commit, không chốt nào canh; Codex nạp agent dự án từ đây (BH144)
> Ban đầu nối vào `audit/NHAT-KY-SU-CO.md` (mục «SAU 24/09/2026») theo chỉ thị của phiên; bác sĩ chọn dời sang tệp riêng
> theo quy ước một-sự-cố-một-tệp của PR gốc #78 (01/10/2026).

**Đo (chỉ đọc)** trên nhánh mặc định repo y khoa (`23648ac`) bằng đúng `expected_files(".codex/agents")` của `tools/sync_agents_to_codex.py`
gốc, `SOURCE_DIR` trỏ `.claude/agents` của repo y khoa, nội dung thực đọc từ blob git: kỳ vọng 84 tệp (50 agent `.toml` + 34 sổ hạ tầng
`.md`) · khớp 3 (`_CONNECTOR-CHUNG-CU.md`, `_HO-SO-NGUOI-DUNG.md`, `_QUAN-TRI-DU-LIEU-PII.md`) · lệch NỘI DUNG 79 (cả 50/50 agent + 29 sổ)
· thiếu 2 (`_KHUNG-DANH-GIA-KHA-THI.md`, `_PLUGIN-ROUTING-CONTRACT.md` — tệp sau nằm trong `REQUIRED_INFRA` của chính bộ sinh gốc) · thừa 0.
**Lệch chỉ do nhãn: 0** — quy nhãn `.Codex/agents` về `.codex/agents` rồi so vẫn còn: mirror thiếu 2.943 dòng của nguồn, mang 801 dòng nguồn
đã bỏ (vd README mirror còn QUADAS-2 và «Ba cổng nghiên cứu», nguồn đã là QUADAS-3 và «Năm cổng cứng» có G8; câu Cổng B trong
`_HIEN-PHAP-LIEM-CHINH.md` là bản cũ; `dao-duc-dang-ky.toml` thiếu 182 dòng nguồn). `.claude/agents` hai repo: 84/84 `.md` trùng byte.
**Gốc.** Commit 20660c0 (08/09, «theo yêu cầu bác sĩ») đưa vào git một ẢNH CHỤP sinh trên Mac (nhãn `.Codex/agents`, 56 tệp mang nhãn này)
từ nguồn GIỮA THÁNG 7: quét 80 commit y khoa + 200 commit gốc chạm `.claude/agents`, từng tệp mirror khớp lần CUỐI với nguồn ngày 15/07
(35 tệp) và 18/07 (40 tệp), muộn nhất 26/07 ⇒ cũ ~7 tuần ngay lúc commit. Sau đó 12 commit đổi 57 tệp nguồn; chỉ `_CONNECTOR-CHUNG-CU.md`
được chép tay theo (3f35bbb, de7e24f, daa6c34). Repo y khoa không có bộ sinh, và `.gitignore` dòng `.codex/` làm tệp agent MỚI phải
`git add -f` mới vào được git.
**Không chốt nào canh:** hook pre-commit y khoa chỉ chạy `regenerate_agent_manifest.py --check` (băm `.claude/agents`, bỏ `_*`) rồi ủy
quyền hook gốc (canh mirror ĐÃ IGNORE của repo gốc); BH107 chỉ so `.claude/agents/_CONNECTOR-CHUNG-CU.md` — đổi một chữ trong mirror `.codex`
thì mọi chốt vẫn xanh. Lúc đo trên macOS phải nhớ: bộ sinh gốc gộp `.Codex`≡`.codex` và chọn nhãn `.Codex/agents`, trên Linux ghi cả hai
⇒ 57/84 tệp kỳ vọng đổi theo nhãn; phải chốt MỘT nhãn cho bản track.
**Khẳng định «không runtime nào đọc mirror» chỉ đúng một nửa** (kiểm trước khi đề xuất phương án «thôi track»): mã của repo y khoa không
đọc `.codex/agents` của chính nó (git grep 14 dòng nhắc; `app/chatgpt_app/agents.py::sync_status()` đọc `<thư mục cha>/.Codex|.codex/agents`
= mirror của repo GỐC). Nhưng **Codex có đọc**: tài liệu OpenAI «Subagents» — agent dự án đặt ở `.codex/agents/` (TOML bắt buộc `name`,
`description`, `developer_instructions`); máy có Codex trong ChatGPT.app (codex-cli 0.155.0-alpha.9.2, `multi_agent` stable = bật; nhị
phân có `agent-roles/src/discovery.rs`) và có worktree Codex của repo y khoa (`~/.codex/worktrees/e0ca`, 10/09). CHƯA kiểm được hành vi
nạp thật: `codex debug prompt-input` không dựng danh sách vai trò (thử cả dự án tạm tin cậy + tệp vai trò hỏng: không báo gì); issue
openai/codex#15250 (03/2026, đã đóng) ghi app/CLI CÓ thấy agent trong `.codex/agents`, chỉ phiên «tool-backed» không gọi đích danh được. Hệ quả:
«thôi track» = checkout tươi (worktree Codex, Codex Cloud, Windows) mất cả đội agent, và cây chính kéo commit xoá về thì git XOÁ luôn 82
tệp trên đĩa — tức tắt hẳn đội agent Codex trong repo y khoa.
**Bác sĩ chọn (01/10):** đồng bộ lại cả bộ + chốt canh HAI LỚP.
**Vá — repo y khoa (drluanbv175/medical-ebm-automation#62):** `tools/sinh_mirror_codex.py` (sinh `--ghi` / kiểm mặc định; phần dựng chép từ bộ sinh gốc, nhãn CỐ
ĐỊNH `.codex/agents` vì bản track chỉ có thư mục chữ thường và CI/Codex Cloud chạy Linux — `.Codex/agents/...` trỏ thư mục không tồn tại ở
đó; đối chiếu 84/84 trùng byte bộ sinh gốc ở CẢ HAI nhãn) · sinh lại 81 tệp (`check_target` của bộ sinh gốc PASS) · `.gitignore`
`.codex/` → `.codex/*` + `!.codex/agents/` · lớp 1 `tests/test_mirror_codex_agents_20261001.py` (khớp bản sinh · mọi tệp đã git track ·
trùng byte bộ sinh gốc khi tìm thấy repo gốc, skip có khai báo trên CI · răng trên fixture) · 1 dòng luật trong `CLAUDE.md` y khoa.
**Vá — repo gốc (PR này):** lớp 2 BH144 — đối chiếu mirror engine với ĐÚNG bộ sinh gốc, chạy mỗi lần mở phiên trên máy thật ⇒ bắt phần lọt
SAU merge (CI y khoa không phải check bắt buộc) VÀ bản chép ở repo y khoa trôi khỏi bộ sinh gốc. Vắng engine ⇒ ⚪ qua `_CAN_ENGINE_NEU_TEN`
(khác BH107 «✓ kèm ghi chú»: ở đây vắng engine là không kiểm được gì); engine có mà chưa có `tools/sinh_mirror_codex.py` ⇒ «⚪ CHƯA KÍCH
HOẠT» (đo thật trên cây chính y khoa hiện tại) — không báo động giả trong khoảng giữa hai PR. Có phép tự kiểm răng trên fixture.
**Kiểm.** Đột biến (`python -B`, xoá `__pycache__`, sao lưu ở `~/.ebm-worktrees/_saoluu_dotbien_mirror_codex_20261001`, cmp trước/sau):
lớp 1 7/7 đỏ đúng chỗ rồi xanh lại (một ký tự · nhãn `.Codex` · thiếu tệp · mồ côi · sửa nguồn không sinh lại · gỡ khỏi index · bản chép
trôi), cây index trùng mốc; lớp 2 9/9 (5 trên mirror/nguồn thật + 3 trên chính mã BH144: bỏ phép so nội dung · đổi nhãn hợp đồng · gỡ khỏi
`_CAN_ENGINE_NEU_TEN` + phép bản chép trôi: sinh lại mirror bằng bản chép đã đột biến ⇒ test 1–2 lớp 1 XANH (đúng lỗ hổng CI không có
repo gốc) mà BH144 đỏ «LỆCH 50» và test 3 đỏ). Bộ chốt trọn: vắng engine 107/144 · ⚪ 37 · 0 ✗; engine = worktree y khoa (symlink tạm)
116/144 · ⚪ 26 · ✗ BH43 + BH50 — đỏ MÔI TRƯỜNG, đo lại bằng bản `origin/master` trong cùng điều kiện cũng đỏ y hệt (engine trần thiếu nền
Retraction Watch và log `weekly_safety`). `pytest tools/` gốc (sau rebase lên master có PR #79) 1889 đạt · 31 bỏ qua có khai báo · 0 lỗi; pytest TOÀN BỘ repo y khoa (môi trường CI offline) 6728 đạt · 37 bỏ qua · 0 lỗi; ruff: phần thêm
0 lỗi mới (`chot_hoi_quy_bai_hoc.py` 56 lỗi tồn trước = sau).
**Phối hợp:** phiên «Dạy agent kê đơn in dòng miễn trừ NLM» cùng ngày sửa `ke-don-an-toan.md` và sinh lại riêng `ke-don-an-toan.toml` —
đã đổi sang nhãn `.codex/agents` theo kế hoạch này nên hai PR hội tụ về cùng byte; PR nào merge SAU thì giải xung đột bằng
`python3 tools/sinh_mirror_codex.py --ghi` trong repo y khoa.
**Còn treo:** (1) chưa kiểm hành vi Codex nạp `.codex/agents` (chỉ có tài liệu + chuỗi trong nhị phân); (2) bộ sinh gốc trên Mac vẫn
chọn nhãn `.Codex/agents` cho mirror ĐÃ IGNORE của chính repo gốc — ngoài phạm vi lần này.
**Số hiệu:** lúc bắt đầu, dò mọi nhánh remote + nhánh cục bộ + worktree đang mở đều chưa có BH143 nên tôi giữ số đó và báo phiên kê đơn;
trong lúc thi công, PR #79 (sync bộ nhớ repo con, làm từ máy/phiên khác chưa đẩy nhánh lúc tôi dò) merge với BH143 ⇒ đổi sang BH144
trước khi commit (bộ sinh và test y khoa trong drluanbv175/medical-ebm-automation#62 đổi theo). Dò số lúc bắt đầu chỉ là ảnh chụp — đo lại ngay
trước khi commit.
