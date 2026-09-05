#!/bin/bash
# =============================================================
# session-start.sh — chuẩn bị phiên Claude Code TRÊN WEB (cloud).
#
# VÌ SAO CÓ (01/09/2026). Phiên cloud dựng container MỚI mỗi lần và chỉ clone repo
# — nó KHÔNG có `~/.claude/skills`, KHÔNG có plugin, KHÔNG có venv `~/.ebm-venv`
# của máy bác sĩ. Đo trên chính phiên này: `~/.claude/skills` chỉ có 2 thư mục,
# `~/.claude/plugins` 1 mục, và 26/41 skill riêng có mặt (15 thiếu, trong đó có
# `tong-thuat-chung-cu`). Repo lại KHÔNG có `.claude/settings.json`, nên 8 chốt
# `SessionStart` bác sĩ đã xuất (sync/hooks-sessionstart.json) **chưa từng chạy
# một lần nào trên cloud**.
#
# RANH GIỚI CỨNG: thoát ngay khi KHÔNG phải môi trường remote. Hook này tuyệt đối
# không được đụng vào máy Mac/Windows của bác sĩ — ở đó `~/.claude` là cấu hình
# thật, có bản vá ngân sách skill và cờ enabledPlugins mà một script tự động không
# có quyền chạm.
# =============================================================
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0                       # máy cá nhân: không làm gì
fi

# Tự định vị gốc repo qua ĐƯỜNG DẪN CHÍNH SCRIPT NÀY trước, chỉ lùi về
# CLAUDE_PROJECT_DIR/$PWD khi không tự định vị được (BH99, 05/09/2026). Phiên
# Claude Code Remote đính kèm NHIỀU repo (add_repo) có thể gọi script này bằng
# đường dẫn tuyệt đối/tương đối từ một $PWD thuộc repo KHÁC (VD: đang đứng ở
# medical-ebm-automation — repo LIỀN KỀ dưới /home/user/ trong container cloud,
# KHÔNG lồng bên trong repo này như trên OneDrive thật của bác sĩ). Nếu chỉ
# dựa `${CLAUDE_PROJECT_DIR:-$PWD}`, `cd "$D"` nhảy sai chỗ và mọi bước sau lặng
# lẽ báo "thiếu tools/…" dù file đang nằm ngay cạnh, không có dòng lỗi rõ ràng.
SRC="${BASH_SOURCE[0]:-$0}"
SELF_ROOT="$(cd "$(dirname "$SRC")/../.." 2>/dev/null && pwd)"
if [ -n "$SELF_ROOT" ] && [ -f "$SELF_ROOT/.claude/hooks/session-start.sh" ]; then
  D="$SELF_ROOT"
else
  D="${CLAUDE_PROJECT_DIR:-$PWD}"
fi
cd "$D" || exit 0
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

echo "── Chuẩn bị phiên cloud cho EBM ──"

# ① Skill riêng của bác sĩ → hai runtime. Gọi ĐÚNG làn ③ của dong_bo_tat_ca
#    (`dong_bo_skill_claude_codex.py`) thay vì tự viết vòng `ln -s`: bản đầu của hook
#    (01/09) chỉ nối `~/.claude/skills`, nên cổng plugin vẫn FAIL «router runtime không
#    tồn tại: ~/.codex/skills/plugin-router-chatgpt» + thiếu ZIP router. Một cơ chế nối
#    skill thứ hai là chỗ để hai bản lệch nhau (BH70). Làn này nối cả `~/.claude/skills`
#    lẫn `~/.codex/skills`, đóng gói ZIP router; Cowork/plugin store vắng thì tự bỏ qua có
#    lời nhắc; máy không có Codex thì giữ catalog đã commit (02/09).
if [ -f tools/dong_bo_skill_claude_codex.py ]; then
  ra=$(python3 tools/dong_bo_skill_claude_codex.py --ap-dung --im-khi-on 2>&1); ma=$?
  co=$(find sync/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d " ")
  if [ $ma -eq 0 ]; then
    echo "   ✓ $co skill riêng nối vào ~/.claude/skills + ~/.codex/skills"
  else
    echo "   ⚠ làn skill thoát $ma:"; echo "$ra" | tail -3 | sed 's/^/      /'
  fi
else
  echo "   ⚠ KHÔNG CHẠY nối skill: thiếu tools/dong_bo_skill_claude_codex.py"
fi

# ② NGÂN SÁCH DANH SÁCH SKILL — nếu không có bước này thì bước ① phần lớn vô ích.
#    Đo trên chính phiên này: 41 skill riêng cần ~21.626 ký tự để hiện đủ mô tả,
#    trong khi cloud KHÔNG có `~/.claude/settings.json` nên Claude Code lùi về mặc
#    định 0,01 ≈ 8.000 ký tự ⇒ CẮT. Đúng triệu chứng bác sĩ mô tả nhiều tháng
#    («skill cài rồi mà gọi không được»), và đo được: 4 trong 6 skill không chào ra
#    nằm trong top-8 mô tả DÀI nhất — thứ bị cắt trước tiên.
#    Giá trị KHÔNG viết cứng ở đây: lấy từ `sync/cau-hinh-nguoi-dung.json` — cùng
#    bản khai mà hai máy của bác sĩ đang dùng, nên cloud không thể trôi khỏi local.
#    `--tao-neu-thieu` chỉ có tác dụng ở đây; trên máy bác sĩ công cụ vẫn bỏ qua khi
#    thiếu file (vắng mặt ở đó là dấu hiệu bất thường, không phải chuyện bình thường).
if [ -f tools/kiem_cau_hinh_nguoi_dung.py ]; then
  python3 tools/kiem_cau_hinh_nguoi_dung.py --ap-dung --tao-neu-thieu 2>&1 \
    | grep -E "^(•|✓|✗|⚠)" || true
fi

# ②b LỆNH TIẾNG VIỆT — 53 lệnh `/…` do bác sĩ sở hữu, nguồn sync/commands-vi/ (đi qua git).
#    Dùng đúng script bác sĩ dùng trên máy (idempotent, chỉ chép file trong commands-vi/).
if [ -f sync/copy-commands-vi.sh ]; then
  if bash sync/copy-commands-vi.sh >/dev/null 2>&1; then
    echo "   ✓ $(ls sync/commands-vi/*.md 2>/dev/null | wc -l | tr -d ' ') lệnh tiếng Việt → ~/.claude/commands"
  else
    echo "   ⚠ không chép được lệnh tiếng Việt (xem sync/copy-commands-vi.sh)"
  fi
fi

# ②c PLUGIN — quyết định bác sĩ 02/09/2026: cloud phải ĐỦ plugin như local. Cài theo
#    CÙNG sổ khai hai máy đang dùng (sync/plugin-manifest.json, trường `nguon`) bằng chính
#    CLI `claude plugin`. Chạy ở NỀN vì đo được lần đầu ~60 giây (aipoch chép 808 MB vào
#    cache), đã đủ thì 0,1 giây — chặn phiên 1 phút mỗi lần mở là dạy người ta tắt hook.
#    Skill plugin xuất hiện giữa phiên (Claude Code dựng lại danh sách skill khi kho đổi —
#    đã quan sát 01/09 với skill riêng). Công cụ tự từ chối khi không phải cloud, nên máy
#    bác sĩ không bao giờ bị cài qua mạng (bài học 11/08).
if [ -f tools/cai_plugin_phien_cloud.py ] && command -v claude >/dev/null 2>&1; then
  LOG_PLUGIN="$HOME/.claude/ebm-cai-plugin-cloud.log"
  mkdir -p "$HOME/.claude"
  if command -v setsid >/dev/null 2>&1; then
    ( setsid nohup python3 tools/cai_plugin_phien_cloud.py --ap-dung --im-khi-on >"$LOG_PLUGIN" 2>&1 </dev/null & )
  else
    ( nohup python3 tools/cai_plugin_phien_cloud.py --ap-dung --im-khi-on >"$LOG_PLUGIN" 2>&1 </dev/null & )
  fi
  echo "   ⏳ plugin theo sổ khai đang cài ở NỀN — xem: python3 tools/cai_plugin_phien_cloud.py · log $LOG_PLUGIN"
fi

# ③ Thư viện các công cụ trong repo cần. Cố ý HẸP và nhanh: hook chạy đồng bộ nên
#    nó chặn lúc mở phiên. Đây đúng ba thứ đo được là thiếu trên container
#    (python-docx · beautifulsoup4 · lxml) — không cài trọn requirements của repo
#    y khoa vì bộ đó nặng và phần lớn không dùng tới trong một phiên soát tài liệu.
if command -v pip3 >/dev/null 2>&1; then
  thieu=""
  python3 -c "import docx" 2>/dev/null || thieu="$thieu python-docx"
  python3 -c "import bs4"  2>/dev/null || thieu="$thieu beautifulsoup4"
  python3 -c "import lxml" 2>/dev/null || thieu="$thieu lxml"
  if [ -n "$thieu" ]; then
    echo "   • cài:$thieu"
    pip3 install --quiet --disable-pip-version-check $thieu 2>&1 | tail -2 || \
      echo "   ⚠ không cài được (mạng?) — công cụ .docx sẽ không chạy trong phiên này"
  fi
fi

# ④ Mirror Codex (.codex/agents · .Codex/agents) là file SINH từ .claude/agents/*.md và
#    bị gitignore ⇒ bản clone tươi KHÔNG có ⇒ `verify_claude_code_repo_alignment`
#    (agent_sync_health) FAIL ⇒ BH83 đỏ ở MỌI phiên cloud (đo 01/09). Không phải
#    «thiếu nguyên liệu ngoài git» — sinh lại được từ nguồn trong repo, <1 giây,
#    ngoại tuyến, chỉ ghi file đã ignore. CỐ Ý không chạy enforce_agent_guardrails:
#    nó SỬA file tracked .claude/agents/*.md — hook mở phiên không có quyền đó.
if [ -f tools/sync_agents_to_codex.py ]; then
  python3 tools/sync_agents_to_codex.py >/dev/null 2>&1 \
    && echo "   ✓ mirror Codex sinh lại từ .claude/agents" \
    || echo "   ⚠ không sinh được mirror Codex — alignment sẽ báo agent_sync_health"
fi

# ⑤ Chốt hồi quy bài học — chốt DUY NHẤT trong 8 chốt của bác sĩ đủ nhanh và đủ
#    ngoại tuyến để chạy lúc mở phiên (đo: <1 giây, im khi mọi thứ ổn). Bảy chốt
#    còn lại đọc dữ liệu ngoài git (EBM-Dashboards, kho plugin, venv) nên trên
#    cloud chúng chỉ báo thiếu — chạy chúng ở đây là dựng một bức tường đỏ mà
#    không ai xử lý được, đúng thứ làm người ta quen bỏ qua cảnh báo.
#    ĐO 01/09 thì giả định «im khi ổn» SAI trên cây chỉ có MỘT PHẦN gốc dữ liệu:
#    32/83 chốt đỏ vì thiếu EBM-Dashboards/, và dòng tổng kết nói «32 BÀI HỌC TÁI
#    PHÁT» — sai sự thật, chúng không tái phát mà là KHÔNG KIỂM ĐƯỢC (đúng thứ BH08
#    cấm gộp). Bộ chốt đã có đường ⚪ «ngoài phạm vi» (BH82) nhưng nó CHỈ mở trên bản
#    sao TRẦN. Nên chỉ chạy đúng ở đó; cây nửa vời thì nói ra và không dựng tường đỏ.
if [ -f tools/chot_hoi_quy_bai_hoc.py ] && [ -f tools/ban_sao_tran.py ]; then
  if python3 -c "import sys; sys.path.insert(0, 'tools'); import ban_sao_tran as b; sys.exit(0 if b.ban_sao_git_tran() else 1)" 2>/dev/null; then
    python3 tools/chot_hoi_quy_bai_hoc.py --im-khi-on 2>&1 | head -20 || true
  else
    echo "   ℹ Cây có MỘT PHẦN gốc dữ liệu ngoài git — bỏ chốt bài học (sẽ toàn đỏ giả)."
  fi
fi

# ⑤b TỰ SỬA CHỮA (system self-repair) — trước 02/09/2026 KHÔNG BAO GIỜ chạy trên cloud.
#    `tools/tu_sua_chua.py` là bộ tự vá lỗi máy móc mà Mac/Windows chạy MỖI PHIÊN qua
#    `SessionStart` cục bộ — nhưng hook cloud này (dựng 01/09) chưa từng gọi nó, nên phần
#    "tự sửa chữa" của "nhạc trưởng tự sửa chữa, tự gọi Agent, tự cập nhật" mà bác sĩ yêu
#    cầu 02/09 KHÔNG hoạt động trên cloud. Ca thật đã bắt được ngay lần chạy đầu: 924 mô tả
#    skill/lệnh bị các plugin vừa cài (②c) trả về tiếng Anh — đúng loại lỗi mà `apply_vi.py
#    --tu-quet` sinh ra để tự vá, và trên cloud mỗi phiên là một container MỚI nên lỗi này
#    xảy ra ở MỌI phiên, không phải một lần.
#    Cờ `--pham-vi-cloud` (mới, xem tools/tu_sua_chua.py::VIEC_MAY) lọc CHỈ 3/9 mục an toàn
#    và có ý nghĩa trên container dựng mới (khoá guard skill · đồng bộ nguồn skill · Việt
#    hoá lại mô tả plugin) — KHÔNG chạy 6 mục còn lại: chúng cần `moc_chuan_plugin.json`/
#    `EBM-Dashboards`/`.env` riêng của máy sống lâu dài mà container này không có, chạy sẽ
#    chỉ in báo động giả «cần bác sĩ» cho những thứ cloud không thể sửa (đúng lỗi BH08 cấm:
#    biến "không áp dụng ở đây" thành "có vấn đề").
if [ -f tools/tu_sua_chua.py ]; then
  ra=$(python3 tools/tu_sua_chua.py --pham-vi-cloud --ap-dung 2>&1); ma=$?
  if [ $ma -eq 0 ]; then
    echo "   ✓ tự sửa chữa (phạm vi cloud): không còn việc máy"
  else
    echo "   ⚠ tự sửa chữa còn việc — xem: python3 tools/tu_sua_chua.py --pham-vi-cloud"
    echo "$ra" | grep -E "^   •" | sed 's/^/     /'
  fi
fi

# ⑤c TƯ CÁCH CỦA CÂY MÃ (thêm 02/09/2026, BH93). Phiên cloud clone NÔNG và có thể đứng
#    trên nhánh lạc hậu — đo được hôm dựng: medical-ebm-automation HEAD 17/08, shallow,
#    KHÔNG có ref master, LẠC HẬU 55 commit. Trên cây đó một kiểm toán 11 agent kết luận
#    cổng G8 «không có chốt chất lượng nào» và bản vá 24/08 «chưa từng tồn tại» — cả hai
#    SAI; `git fetch origin master` cho thấy G8Q nối dây ở approve_gate.py:76,567. Cây lạc
#    hậu sinh ÂM TÍNH GIẢ: tuyên bố một cơ chế an toàn không tồn tại trong khi nó đang chạy.
#    Chỉ ĐO, KHÔNG tự fetch (kéo hàng trăm MB hộ bác sĩ là quyết định của bác sĩ). Cây nông
#    = 🟡 im lặng (mọi phiên cloud đều nông; báo đỏ mỗi phiên là tường đỏ vô ích — BH08),
#    chỉ LẠC HẬU mới lên tiếng vì đó mới có việc để làm.
if [ -f tools/kiem_cay_lam_viec.py ]; then
  python3 tools/kiem_cay_lam_viec.py --im-khi-on || true
fi

# ⑥ Nói ra GIỚI HẠN còn lại, không để người đọc tưởng cloud = local tuyệt đối:
#    plugin nào sổ khai còn «chua-ro» (chỉ Mac biết nguồn) thì cloud chưa có cho tới khi
#    bác sĩ chạy --xuat-nguon trên Mac; 38 skill mồ côi trong ~/.claude/skills của Mac
#    không nằm trong git nên cloud không có. Theo bảng định tuyến ở CLAUDE.md, plugin
#    chỉ là worker và KHÔNG BAO GIỜ là chủ của việc có cổng — thiếu chúng không chặn
#    việc gì có cổng.
# ⑥b NGUỒN CHỨNG CỨ CỦA MÁY NÀY LÀ THẬT HAY GIẢ (thêm 02/09/2026, BH94). Container cloud
#    không có ~/.ebm-secrets ⇒ USE_MOCK_SOURCES về mặc định true ⇒ mọi lời gọi nguồn y văn
#    trả DỮ LIỆU BỊA. Hôm dựng mục này, chính điều đó đã làm hai phán quyết "retracted"
#    (PMID 9500320 · 30267080) tụt xuống "unknown" trong sổ bằng chứng và suýt được commit.
#    CỐ Ý chỉ in MỘT DÒNG thay vì khối đỏ của kiem_nguon_that: trên cloud đây là trạng thái
#    BÌNH THƯỜNG VĨNH VIỄN và không sửa được trong container ⇒ khối đỏ mỗi phiên là tường đỏ
#    vô ích (BH08). Chốt CHẶN thật nằm ở pre-commit (kiem_o_nhiem_artifact).
if [ -f tools/kiem_nguon_that.py ]; then
  if ! python3 tools/kiem_nguon_that.py --nhanh >/dev/null 2>&1; then
    echo "   ⚠ Nguồn y văn của máy này là DỮ LIỆU GIẢ (không có secrets) — KHÔNG dùng số"
    echo "     liệu quét/giám sát ở đây cho quyết định lâm sàng. Chi tiết: python3 tools/kiem_nguon_that.py"
  fi
fi

echo "   ℹ Plugin: theo sổ khai sync/plugin-manifest.json (mục chua-ro chờ --xuat-nguon từ Mac)."
echo "     Việc có cổng vẫn chạy đủ: chủ của mọi việc có cổng là agent/skill trong repo."
exit 0
