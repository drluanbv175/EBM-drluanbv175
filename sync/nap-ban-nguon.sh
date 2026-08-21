#!/usr/bin/env bash
# =============================================================
# NẠP BẢN NGUỒN — chạy MỘT LẦN trên máy ĐANG CHẠY ĐÚNG (thường là MacBook).
#
# Hai thứ chỉ máy đó mới biết, và không công cụ nào được phép soạn hộ:
#   · hook SessionStart thật  → sync/hooks-sessionstart.json
#   · kho plugin thật         → sync/plugin-manifest.json
# Soạn theo trí nhớ tài liệu là sai cờ, sai đường dẫn, và hỏng IM LẶNG.
#
# Script này CHỈ ĐỌC máy và GHI hai file trên vào repo. Nó KHÔNG commit, KHÔNG
# push, KHÔNG sửa ~/.claude/settings.json, KHÔNG cài/gỡ plugin. Dừng ngay nếu
# cây làm việc còn thay đổi chưa lưu.
# =============================================================
set -uo pipefail

NHANH="${1:-claude/multi-platform-plugin-sync-cslwb0}"
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

# Trên macOS `python3` luôn có; giữ nhánh lùi cho máy đặt tên khác.
PY=$(command -v python3 || command -v python) || { echo "✗ Không tìm thấy Python."; exit 2; }
command -v git >/dev/null || { echo "✗ Không tìm thấy git."; exit 2; }

echo "================================================================"
echo "  NẠP BẢN NGUỒN — máy $(uname -s) — repo $(pwd)"
echo "================================================================"

# ① Cây làm việc phải sạch. Đổi nhánh khi còn việc dở là cách mất việc dở.
if [ -n "$(git status --porcelain)" ]; then
  echo ""
  echo "⛔ DỪNG — cây làm việc còn thay đổi chưa lưu:"
  git status --short | sed 's/^/     /'
  echo ""
  echo "   Commit hoặc cất (git stash) rồi chạy lại. Script cố ý KHÔNG tự"
  echo "   quyết định thay bác sĩ về những thay đổi này."
  exit 2
fi

# ② Lấy nhánh có công cụ. Ghi rõ nhánh cũ để bác sĩ quay lại được.
NHANH_CU=$(git rev-parse --abbrev-ref HEAD)
echo ""
echo "── Đang ở nhánh: $NHANH_CU"
if [ "$NHANH_CU" != "$NHANH" ]; then
  echo "── Lấy nhánh có công cụ: $NHANH"
  git fetch origin "$NHANH" || { echo "✗ Không lấy được nhánh (mạng?)."; exit 2; }
  git checkout "$NHANH" || { echo "✗ Không chuyển được nhánh."; exit 2; }
  echo "   (quay lại bằng: git checkout $NHANH_CU)"
else
  git pull --ff-only origin "$NHANH" || echo "   ⚠ không kéo được bản mới (mạng?) — dùng bản đang có"
fi

# ③ Hai bước nạp. Mỗi bước tự nói ra khi thiếu nguyên liệu.
ma=0
echo ""
echo "── ① Hook SessionStart của máy này → git"
"$PY" tools/dong_bo_hook_sessionstart.py --xuat || ma=1

echo ""
echo "── ② Kho plugin của máy này → sổ khai chung"
"$PY" tools/dong_bo_plugin_claude_codex.py --tao-so-khai || ma=1

# ④ Cho thấy hiện trạng 8 làn, KHÔNG ghi gì.
echo ""
echo "── ③ Hiện trạng đồng bộ (chỉ kiểm, không ghi)"
"$PY" tools/dong_bo_tat_ca.py || true

echo ""
echo "================================================================"
git status --short | sed 's/^/  /'
echo "================================================================"
echo "  CÒN LẠI — phần chỉ bác sĩ quyết được:"
echo "  1. Mở sync/plugin-manifest.json:"
echo "     · điền ô \"ly_do\" còn nhãn [CẦN BÁC SĨ]"
echo "     · sửa \"can_o_may\" cho ĐÚNG Ý ĐỊNH (plugin nào cần ở máy nào)"
echo "     · bật \"da_xac_nhan\": true cho mục đã chắc"
echo "       (còn false thì công cụ chỉ CẢNH BÁO, không báo đỏ — cố ý)"
echo "  2. git add -A && git commit && git push"
echo "  3. Sang máy kia: git pull rồi bấm nút Đồng bộ tất cả."
echo ""
echo "  Script KHÔNG commit hộ: đẩy hộ là quyết định thay bác sĩ về thứ"
echo "  được công bố sang máy kia."
echo "  Nhấn Enter để đóng."
read -r _ 2>/dev/null || true
exit $ma
