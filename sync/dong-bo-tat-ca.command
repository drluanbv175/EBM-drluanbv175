#!/usr/bin/env bash
# ĐỒNG BỘ TẤT CẢ (macOS) — bấm đúp file này.
# Chạy tools/dong_bo_tat_ca.py --ap-dung: an toàn → git → skill → agent → plugin
# → hook → bộ nhớ → kho công cụ. Công cụ luôn SAO LƯU trước khi ghi, không cài/gỡ
# plugin qua mạng, và KHÔNG đụng nội dung y khoa.
# Lần đầu dùng, nếu macOS chặn: chuột phải → Open, hoặc chmod +x file này.
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
python3 tools/dong_bo_tat_ca.py --ap-dung
ma=$?
echo ""
echo "(mã thoát $ma — 0 khớp · 1 còn việc · 2 phải dừng)"
echo "Nhấn Enter để đóng cửa sổ."
read -r _
exit $ma
