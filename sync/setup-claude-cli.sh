#!/usr/bin/env bash
# =============================================================
# setup-claude-cli.sh
# Cài / cập nhật claude-code-harness cho Claude Code CLI.
# Chạy được trên: macOS, Linux, Windows (Git Bash).
# Idempotent: chạy lại nhiều lần đều an toàn.
#
# Dùng để đồng bộ cấu hình CLI giữa Windows và MacBook:
#   - clone/cập nhật repo harness (đã có binary cho mọi nền tảng)
#   - mirror skills  -> ~/.claude/skills/
#   - mirror agents  -> ~/.claude/agents/
# =============================================================
set -euo pipefail

REPO_URL="https://github.com/Chachamaru127/claude-code-harness.git"
CLAUDE_DIR="${HOME}/.claude"
PLUGIN_DIR="${CLAUDE_DIR}/plugins/claude-code-harness"
SKILLS_DIR="${CLAUDE_DIR}/skills"
AGENTS_DIR="${CLAUDE_DIR}/agents"

echo "==> Claude dir: ${CLAUDE_DIR}"
mkdir -p "${CLAUDE_DIR}/plugins" "${SKILLS_DIR}" "${AGENTS_DIR}"

# 1) Clone hoặc cập nhật repo harness
if [ -d "${PLUGIN_DIR}/.git" ]; then
  echo "==> Cập nhật harness repo..."
  git -C "${PLUGIN_DIR}" pull --ff-only
else
  echo "==> Clone harness repo..."
  rm -rf "${PLUGIN_DIR}"
  git clone --depth 1 "${REPO_URL}" "${PLUGIN_DIR}"
fi

# 2) Mirror skills (mỗi skill = thư mục có SKILL.md)
echo "==> Mirror skills -> ${SKILLS_DIR}"
count=0
for d in "${PLUGIN_DIR}/skills"/*/; do
  [ -f "${d}SKILL.md" ] || continue
  name="$(basename "$d")"
  rm -rf "${SKILLS_DIR}/${name}"
  cp -R "$d" "${SKILLS_DIR}/${name}"
  count=$((count+1))
done
# file chia sẻ
[ -f "${PLUGIN_DIR}/skills/routing-rules.md" ] && cp -f "${PLUGIN_DIR}/skills/routing-rules.md" "${SKILLS_DIR}/routing-rules.md"
echo "    -> ${count} skills"

# 3) Mirror agents
echo "==> Mirror agents -> ${AGENTS_DIR}"
cp -f "${PLUGIN_DIR}/agents/"*.md "${AGENTS_DIR}/" 2>/dev/null || true
ls "${AGENTS_DIR}" | sed 's/^/    -> /'

# 4) Tự kiểm tra binary đúng nền tảng
echo "==> Kiểm tra harness binary..."
"${PLUGIN_DIR}/bin/harness" --version 2>/dev/null || echo "    (cảnh báo: binary không chạy trên nền tảng này)"

# 5) Đồng bộ Memory (trí nhớ Claude) qua OneDrive
#    Trỏ ~/.claude/projects/<encoded>/memory -> sync/memory bằng symlink (Mac/Linux).
SYNC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "$(uname -s)" in
  Darwin|Linux)
    echo "==> Liên kết Memory -> hub OneDrive..."
    bash "${SYNC_DIR}/link-memory.sh" || echo "    (bỏ qua: link-memory.sh lỗi)"
    ;;
  *)
    echo "==> Windows: hãy bấm đúp 'sync/link-memory.cmd' để liên kết Memory (junction)."
    ;;
esac

echo ""
echo "HOÀN TẤT. Mở 'claude' trong một thư mục git và gõ /harness-plan để kiểm tra."
