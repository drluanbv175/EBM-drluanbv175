#!/usr/bin/env bash
# XUẤT MIRROR CHỨNG CỨ CHO CLOUD (macOS) — bấm đúp file này.
# Chạy tools/xuat_trang_thai_cloud.py: đọc lại 3 bộ đếm đã có sẵn (độ tươi ·
# quyết định đã duyệt · việc-còn-lại) + 2 sổ quyết định, ghi MỘT JSON nhỏ vào
# cloud-mirror/ — để phiên Claude Code trên Cloud thấy được trạng thái mới nhất
# của EBM-Dashboards/ (thứ nằm ngoài git, Cloud không có).
# CHỈ ghi file — KHÔNG tự commit/push (cùng nguyên tắc dong-bo-tat-ca.command:
# đẩy hộ là quyết định thay bác sĩ về thứ được công bố). Bước git ở cuối là TAY.
# Lần đầu dùng, nếu macOS chặn: chuột phải → Open, hoặc chmod +x file này.
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
python3 tools/xuat_trang_thai_cloud.py
ma=$?
echo ""
if [ $ma -eq 0 ]; then
  echo "Xong. Muốn Cloud thấy trạng thái này, chạy 3 lệnh (bác sĩ tự soát trước khi đẩy):"
  echo "  git add cloud-mirror/"
  echo "  git commit -m \"chore(cloud): cập nhật mirror trạng thái chứng cứ\""
  echo "  git push"
fi
echo "(mã thoát $ma)"
echo "Nhấn Enter để đóng cửa sổ."
read -r _
exit $ma
