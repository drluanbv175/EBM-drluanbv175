#!/usr/bin/env bash
# NHẬN BẢN CHUẨN (macOS) — bấm đúp file này sau khi master có bản mới.
# Chạy TRỌN chuỗi nhận bản: kéo master → an toàn đồng bộ (🔴 là DỪNG) → đồng bộ
# 8 làn → dò + bật trạm web hội → chốt bài học lần cuối làm mốc đạt.
# Dựng 30/08/2026 theo yêu cầu «chạy luôn» của bác sĩ — chuỗi 6 lệnh phải nhớ
# là chuỗi sẽ bị bỏ sót bước (cùng bài học đã sinh ra dong_bo_tat_ca/BH71).
# Lần đầu dùng, nếu macOS chặn: chuột phải → Open, hoặc chmod +x file này.
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

echo "── ① Kéo bản chuẩn master ──"
if ! git pull origin master; then
  echo "🔴 git pull hỏng — DỪNG. Kiểm mạng/xung đột rồi chạy lại."
  read -r _; exit 2
fi

echo "── ② An toàn đồng bộ (🔴 là DỪNG toàn bộ) ──"
python3 tools/sync_safety_check.py
if [ $? -ge 2 ]; then
  echo "🔴 An toàn đồng bộ báo ĐỎ — DỪNG. Đồng bộ khi cây đang hỏng là nhân bản cái hỏng."
  read -r _; exit 2
fi

echo "── ③ Đồng bộ 8 làn (tự sao lưu trước khi ghi) ──"
python3 tools/dong_bo_tat_ca.py --ap-dung
echo "(mã thoát $? — 0 khớp · 1 còn việc · 2 phải dừng)"

echo "── ④ Dò trạm web hội (chỉ đo, không ghi) ──"
python3 tools/giam_sat_to_chuc.py --kiem-tra
echo "── ⑤ Bật trạm dò đạt (not-covered→active, tự sao lưu sổ) ──"
python3 tools/giam_sat_to_chuc.py --bat-neu-ok

echo "── ⑥ MỐC ĐẠT: bộ chốt bài học với đầy đủ nguyên liệu ──"
python3 tools/chot_hoi_quy_bai_hoc.py
ma=$?

echo ""
echo "Xong. Mốc đạt của hai hệ: 0 bài học tái phát với 0 mục ⚪ trên CẢ HAI máy."
echo "Cần bác sĩ kiểm chứng. Nhấn Enter để đóng."
read -r _
exit $ma
