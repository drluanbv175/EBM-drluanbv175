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


def giac_quan_lich_nen(log_tuan: Path,
                       hom_nay: dt.date | None = None) -> list[tuple[int, str]]:
    """Kỳ lịch tuần có NỔ thật không — đọc dòng «KẾT THÚC … tổng thể=PASS» trong log.

    Trả [(ưu tiên, mô tả)]. Ba mức theo tuổi lượt PASS cuối: ≤7 ngày mà kỳ T7
    06:30 vừa qua không nổ → 2 (nhắc, dữ liệu vẫn tươi nhờ watchdog mở-phiên);
    8–10 ngày → 1 (chạy bù); >10 hoặc không đọc được lượt PASS nào → 0.
    Hàm thuần nhận đường log + ngày để chốt BH đột biến được bằng file tạm.
    """
    hom_nay = hom_nay or dt.date.today()
    try:
        dong = log_tuan.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return [(0, "Log giám sát tuần KHÔNG ĐỌC ĐƯỢC — chưa từng chạy trên máy này?")]
    ngay_pass = None
    for ln in reversed(dong):
        if "KẾT THÚC" in ln and "tổng thể=PASS" in ln:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", ln)
            if m:
                ngay_pass = dt.date.fromisoformat(m.group(1))
            break
    if ngay_pass is None:
        return [(0, "Log tuần không có lượt PASS nào — giám sát chưa từng chạy trọn")]
    tuoi = (hom_nay - ngay_pass).days
    # thứ Bảy gần nhất đã qua (weekday: T2=0 … T7=5); đúng T7 thì chính hôm nay
    t7 = hom_nay - dt.timedelta(days=(hom_nay.weekday() - 5) % 7)
    lo_ky = ngay_pass < t7 <= hom_nay
    if tuoi > 10:
        return [(0, f"Giám sát tuần quá hạn {tuoi} ngày (PASS cuối {ngay_pass}) — chạy bù NGAY")]
    if tuoi > 7:
        return [(1, f"Giám sát tuần {tuoi} ngày tuổi (PASS cuối {ngay_pass}) — kỳ lịch đã lỡ, chạy bù")]
    if lo_ky:
        return [(2, f"Kỳ lịch T7 vừa qua KHÔNG nổ (máy không thức?) — dữ liệu vẫn tươi "
                    f"(PASS {ngay_pass}, {tuoi} ngày), nhưng lịch nền đang không tự chạy")]
    return []


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

    # ⑦b GIÁC QUAN CI (thêm 16/08 — bài học «CI đỏ 13 tháng không ai nhìn»):
    # đọc phán quyết run mới nhất; đỏ = việc ưu tiên 0. Fail-soft khi thiếu gh/mạng.
    out = _chay(["gh", "run", "list", "--workflow", "offline-ci.yml", "--limit", "1",
                 "--json", "conclusion,headBranch", "--jq",
                 ".[0].conclusion + \" \" + .[0].headBranch"], giay=30)
    kq_ci = out.strip().split()[0] if out.strip() else ""
    if kq_ci == "failure":
        de_xuat.append((0, "🤖", "CI GitHub FAILURE trên nhánh làm việc — đọc log, "
                        "sửa tới xanh, đừng để đỏ qua đêm",
                        "cd medical-ebm-automation && gh run view --log-failed"))
    elif kq_ci != "success":
        # đang chạy / gh lỗi / mạng — KHÔNG BIẾT ≠ CÓ VẤN ĐỀ (BH08): mức nhắc
        de_xuat.append((2, "🤖", f"Chưa đọc được phán quyết CI (thấy: {kq_ci or 'rỗng'}) — "
                        "kiểm tay khi tiện", "gh run list --workflow offline-ci.yml --limit 3"))

    # ⑦c GIÁC QUAN GIT (bài «40 file chưa commit mà tưởng cây sạch»): đếm file
    # bẩn + commit chưa đẩy ở cả hai repo. Chỉ ĐẾM và BÁO — không tự add của ai.
    for ten_repo, duong in (("gốc", REPO), ("y khoa", REPO / "medical-ebm-automation")):
        st = _chay(["git", "-C", str(duong), "status", "--porcelain"], giay=20)
        n_ban = len([x for x in st.splitlines() if x.strip()])
        ab = _chay(["git", "-C", str(duong), "rev-list", "--count", "@{u}..HEAD"], giay=20)
        n_chua_day = int(ab.strip()) if ab.strip().isdigit() else 0
        if n_ban or n_chua_day:
            de_xuat.append((2, "🤖", f"Repo {ten_repo}: {n_ban} file chưa commit · "
                            f"{n_chua_day} commit chưa đẩy — soi rồi commit/push "
                            "(file của phiên khác thì ĐỂ NGUYÊN)",
                            f"git -C \"{duong.name}\" status -sb"))

    # ⑦d GIÁC QUAN LỊCH-NỀN (16/08 — ngay kỳ đầu của kiến trúc lịch mới đã LỠ:
    # tác vụ Claude 06:30 T7 không nổ vì máy/app không chạy, nextRunAt nhảy thẳng
    # tuần sau, không lastRunAt — không bộ đếm nào nhìn thấy). Đo ĐẦU RA THẬT
    # trong log (bài học launchd: đăng ký ≠ nổ), không đọc đăng ký lịch.
    for uu, dong in giac_quan_lich_nen(
            REPO / "medical-ebm-automation" / "data" / "archive" / "launchd_weekly.log"):
        de_xuat.append((uu, "🤖" if uu < 2 else "👤", dong,
                        "bash medical-ebm-automation/scripts/weekly_safety.sh  # chạy bù"
                        if uu < 2 else "bấm «Run now» tác vụ thu-thap-tuan-an-toan-thuoc "
                        "hoặc đổi giờ sang lúc máy thường thức"))

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
