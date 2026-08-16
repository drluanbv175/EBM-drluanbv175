#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HỆ TỰ ĐỀ XUẤT VIỆC — đóng vòng meta: danh sách «nâng cấp tiếp theo» tự sinh (16/08/2026).

Vì sao: suốt các vòng «đề xuất để tôi chọn», danh sách việc luôn do NGƯỜI/agent
ngồi gom tay từ hàng chục bộ đếm. Các bộ đếm đã sống sẵn — mảnh thiếu là một chỗ
ĐỌC CHÚNG CÙNG LÚC và xếp hạng thành việc kèm LỆNH chạy ngay. Từ nay «hệ còn gì
để hoàn thiện?» có câu trả lời tự động, chạy được mỗi sáng thứ Bảy trong gói tuần.

Ba luật của bảng đề xuất — kế thừa toàn bộ bài học BH:
  1. Mỗi dòng phải có SỐ ĐO THẬT đứng sau (không đề xuất từ cảm giác).
  2. Việc thuộc thẩm quyền BÁC SĨ ghi rõ «👤» — máy không bao giờ tự làm nhóm đó.
  3. «Không còn gì» là kết quả hợp lệ và PHẢI in ra được — một bộ tự-đề-xuất
     không biết nói «đủ rồi» sẽ chế việc để tồn tại.

Dùng:  python3 tools/tu_de_xuat_viec.py [--gon]
Mã thoát: 0 luôn (bảng đề xuất là sản phẩm, không phải phán quyết).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
DASH = REPO / "EBM-Dashboards"


def _chay(lenh: list[str], giay: int = 120) -> str:
    try:
        r = subprocess.run(lenh, capture_output=True, text=True, timeout=giay, cwd=REPO)
        return (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.SubprocessError):
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Bảng đề xuất việc tự sinh từ bộ đếm sống")
    ap.add_argument("--gon", action="store_true", help="chỉ in bảng, bỏ phần giải thích")
    a = ap.parse_args()
    de_xuat: list[tuple[int, str, str, str]] = []  # (ưu tiên, ai, việc+số đo, lệnh)

    # ① Sổ xác minh — độ phủ & rút bài
    out = _chay([sys.executable, "tools/so_xac_minh_nguon.py", "--bao-cao"])
    m = re.search(r"Còn hiệu lực\s*:\s*(\d+)/(\d+)", out)
    if m and int(m.group(1)) < int(m.group(2)):
        thieu = int(m.group(2)) - int(m.group(1))
        de_xuat.append((2, "🤖", f"Phủ sổ xác minh: còn {thieu} mục chưa/hết hạn "
                        f"({m.group(1)}/{m.group(2)})",
                        "~/.ebm-venv/bin/python tools/so_xac_minh_nguon.py --vong 3"))
    if re.search(r"ĐÃ BỊ RÚT\s*:\s*[1-9]", out):
        de_xuat.append((0, "👤", "CÓ nguồn rút-bỏ-hẳn đang được trích — xử lý trước "
                        "khi dùng gói chứa nó", "python3 tools/so_xac_minh_nguon.py --bao-cao"))

    # ② gradeBy tồn kho
    out = _chay([sys.executable, "tools/kiem_phan_hang.py"])
    m = re.search(r"(\d+) CHƯA khai `gradeBy` \((\d+)", out)
    if m and int(m.group(1)):
        de_xuat.append((1, "👤", f"{m.group(1)} item chưa khai gradeBy "
                        f"({m.group(2)} đang apply) — duyệt đề xuất theo nhóm",
                        "python3 tools/de_xuat_gradeby.py"))

    # ③ Hai bản nói ngược
    out = _chay([sys.executable, "tools/dang_ky_chu_de.py"])
    m = re.search(r"(\d+) MỤC HAI BẢN NÓI NGƯỢC", out)
    if m and int(m.group(1)):
        de_xuat.append((0, "👤", f"{m.group(1)} cặp hai-bản-nói-ngược cùng PMID — "
                        "bác sĩ quyết bản đúng", "python3 tools/dang_ky_chu_de.py"))

    # ④ Độ tươi chứng cứ (trung vị + báo động 120 ngày — BH32: không dùng max)
    out = _chay([sys.executable, "tools/kiem_do_tuoi_chung_cu.py"])
    m = re.search(r"trung vị\s*(\d+)", out)
    if m and int(m.group(1)) > 60:
        de_xuat.append((2, "🤖", f"Trung vị tuổi gói {m.group(1)} ngày — chạy cập nhật "
                        "chủ đề lâu nhất", "python3 ops/orchestrator.py --topic <chủ đề> --online"))

    # ⑤ Kho toàn văn + chỉ mục RAG
    kho = DASH / "toan_van_oa"
    xmls = list(kho.glob("PMID-*.xml"))
    vec = kho / ".rag" / "vec.npy"
    if xmls and vec.exists() and max(f.stat().st_mtime for f in xmls) > vec.stat().st_mtime:
        de_xuat.append((2, "🤖", "Chỉ mục RAG cũ hơn kho toàn văn — dựng lại",
                        "~/.ebm-venv/bin/python tools/rag_toan_van.py --dung-index"))

    # ⑥ Đề tài thật — việc người gần nhất (đọc readiness C1a)
    out = _chay(["~/.ebm-venv/bin/python".replace("~", str(Path.home())),
                 str(REPO / "medical-ebm-automation" / "tools" / "study_readiness.py"),
                 "--study", "hai-long-benh-nhan-C1a-BVQY175"])
    if "CHƯA được bác sĩ chốt" in out:
        de_xuat.append((1, "👤", "C1a: G0 chờ 5 cờ FINER — một cú đúp",
                        "mở «Chot FINER C1a.command» (Mac) / .ps1 (Windows)"))
    if "0/4" in out:
        de_xuat.append((1, "👤", "C1a: 0/4 cổng cứng có chữ ký — bước tiếp là hồ sơ "
                        "G2 nộp IRB thật", "xem exports/.../HO-SO-KHOI-DONG-2026-08-15.md"))

    # ⑦ Nhật ký tác động — miss dồn cụm
    log = REPO / "state" / "nhat-ky-tac-dong.jsonl"
    if log.exists():
        try:
            dong = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x]
            miss = sum(1 for r in dong if r.get("miss"))
            if miss >= 3:
                de_xuat.append((1, "🤖", f"{miss} lượt điểm-khám NGOÀI giám sát — rà "
                                "ứng viên mở watchlist",
                                "đọc state/cau-hoi-chua-giam-sat.jsonl trong gói tuần"))
        except (json.JSONDecodeError, OSError):
            pass

    hom_nay = dt.date.today().isoformat()
    print("=" * 66)
    print(f"  HỆ TỰ ĐỀ XUẤT VIỆC — {hom_nay} (sinh từ bộ đếm sống, không cảm giác)")
    print("=" * 66)
    if not de_xuat:
        print("  🟢 KHÔNG CÒN VIỆC NÀO các bộ đếm nhìn thấy — «đủ rồi» là kết quả")
        print("     hợp lệ; nghỉ cũng là một trạng thái đúng của hệ.")
    else:
        de_xuat.sort(key=lambda x: x[0])
        for uu, ai, viec, lenh in de_xuat:
            print(f"  {'🔴' if uu == 0 else '🟠' if uu == 1 else '🟡'} {ai} {viec}")
            print(f"       → {lenh}")
    if not a.gon:
        print("-" * 66)
        print("  👤 = thẩm quyền bác sĩ, máy không tự làm · 🤖 = máy chạy được ngay")
        print("  Mỗi dòng đều có SỐ ĐO đứng sau. Cần bác sĩ kiểm chứng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
