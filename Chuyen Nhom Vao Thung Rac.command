#!/bin/bash
# Chuyển một nhóm «_Cho thung rac…» của EndNote vào THÙNG RÁC — 19/10/2026 (việc 5, kết nối EndNote ↔ Claude).
# Bác sĩ bấm đúp. Công cụ chỉ HIỆN đúng các bản ghi của nhóm trong EndNote; bác sĩ tự bấm ⌘A → References →
# Move References to Trash; công cụ đọc cơ sở dữ liệu (chỉ đọc) để báo đã vào thùng rác chưa.
# KHÔNG xoá hẳn bản ghi nào, KHÔNG bấm menu thay bác sĩ.

GOC="$(cd "$(dirname "$0")" && pwd)"
if [ -x "$HOME/.ebm-venv/bin/python" ]; then
  PY="$HOME/.ebm-venv/bin/python"
else
  PY="$(command -v python3 || command -v python)"
fi
cd "$GOC" || exit 2
"$PY" tools/chuyen_nhom_vao_thung_rac.py
echo ""
read -r -p "Nhấn Enter để đóng cửa sổ này…" _
