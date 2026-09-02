#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM Ô NHIỄM ARTIFACT — chặn commit khi bằng chứng bị máy THIẾU DỮ LIỆU làm hỏng.

VÌ SAO CÓ (02/09/2026, BH94) — ca thật, suýt commit trong chính phiên dựng công cụ này.
Một phiên cloud chạy các công cụ chứng cứ trong container KHÔNG có `~/.ebm-secrets/`
(nên `USE_MOCK_SOURCES=true`) và KHÔNG có nền Retraction Watch ngoại tuyến. Ba artifact
bị ghi đè, và cả ba đều là ĐI LÙI:

  1. `quality/eval/negative/canary-10-loi-gai.log`  17 dòng «🟢 10/10 lỗi gài đều bị
     bắt» → **0 byte**. Một bản ghi PASS thật bị xoá trắng.
  2. `quality/eval/negative/rut-bai-3-muc.log`  PMID 9500320 (Wakefield) đi từ
     `"status": "retracted"` kèm đúng thông báo rút bài Lancet 2010 → `"status":
     "unknown_mock_or_no_email"`. Một phán quyết ĐÚNG biến thành «không biết».
  3. `exports/<đề-tài-thật>/G3_checkpoint.json`  đường dẫn tuyệt đối trong
     `artifact_manifest` bị viết lại từ OneDrive trên Mac của bác sĩ sang
     `/home/user/...` của container.

Không lỗi nào trong ba lỗi này làm công cụ báo động. Mọi thứ «chạy thành công»; JSON
vẫn hợp lệ; git chỉ thấy «file đã đổi». Đúng họ lỗi nền của repo này — *công cụ vẫn
chạy, vẫn in kết quả hợp lệ, nhưng thứ cần bảo vệ thì không ai canh* — và lần này nạn
nhân là chính SỔ BẰNG CHỨNG.

Luật nền bị vi phạm nếu commit: **một máy THIẾU dữ liệu thật không được phép ghi đè
artifact do máy CÓ dữ liệu thật sinh ra.** Kèm BH08: `unknown` là «chưa biết», ghi đè
một phán quyết `retracted` bằng `unknown` là hạ cấp bằng chứng an toàn thành vô tri.

BẤT ĐỐI XỨNG CÓ CHỦ Ý (đừng đảo): đi LÊN thì cho qua, đi XUỐNG mới chặn.
`unknown → retracted` là máy vừa biết thêm ⇒ HOAN NGHÊNH. `retracted → unknown` là
máy vừa quên ⇒ CHẶN. Chặn cả hai chiều sẽ khiến bác sĩ không cập nhật được sổ khi
chạy trên máy thật, và một cổng cản trở việc đúng là cổng sẽ bị tắt.

Mã thoát: 0 = sạch · 1 = có ô nhiễm (CHẶN commit) · 2 = không chạy được.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]

# Chỉ soi nơi CHỨA BẰNG CHỨNG. Cố ý HẸP: mở rộng sang mã nguồn sẽ tạo dương tính giả
# hàng loạt (mã đổi là chuyện bình thường), và một cổng ồn là một cổng sẽ bị tắt.
VUNG_BANG_CHUNG = ("quality/eval/", "exports/", "EBM-Dashboards/")

# Trạng thái mang NGHĨA XÁC ĐỊNH (máy đã kết luận được). Mọi thứ bắt đầu bằng
# "unknown"/"chua_kiem" là KHÔNG BIẾT — xem `_la_vo_tri`.
def _la_vo_tri(tt: str) -> bool:
    t = (tt or "").strip().lower()
    return t.startswith("unknown") or t.startswith("chua_kiem") or t in ("", "unresolved")


def _git(*args: str, cay: Path = REPO) -> tuple[int, str]:
    try:
        r = subprocess.run(["git", *args], cwd=cay, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout or ""
    except (OSError, subprocess.SubprocessError):
        return 99, ""


def _trang_thai_theo_khoa(noi_dung: str) -> dict[str, str]:
    """Bóc {định danh: status} từ một sổ bằng chứng JSON. Không parse được ⇒ {} (im lặng).

    KHÔNG đoán khi JSON hỏng: một file hỏng là việc khác, không phải việc của cổng này.
    """
    try:
        d = json.loads(noi_dung)
    except (json.JSONDecodeError, ValueError):
        return {}
    if not isinstance(d, dict):
        return {}
    ra: dict[str, str] = {}
    for k, v in d.items():
        if isinstance(v, dict) and isinstance(v.get("status"), str):
            ra[str(k)] = v["status"]
    return ra


_DUONG_TUYET_DOI = re.compile(r'"((?:/|[A-Za-z]:[\\/])[^"]{8,})"')


def _goc_may(duong: str) -> str:
    """Phần ĐẦU của một đường dẫn tuyệt đối, dùng để phát hiện đổi MÁY.

    Lấy 3 đoạn đầu là đủ phân biệt `/Users/<ai>/Library` với `/home/user` mà không
    nhạy cảm với việc đổi tên thư mục con của đề tài.
    """
    phan = [p for p in re.split(r"[\\/]+", duong) if p]
    return "/".join(phan[:3])


def soi_mot_file(ten: str, cu: str, moi: str) -> list[str]:
    """So bản CŨ (HEAD) với bản MỚI (staged) của một file bằng chứng."""
    loi: list[str] = []

    # (1) Sổ bằng chứng bị XOÁ TRẮNG. Cố ý chỉ bắt cũ-có→mới-rỗng.
    if cu.strip() and not moi.strip():
        loi.append(f"{ten}: sổ bằng chứng {len(cu)} byte bị ghi thành RỖNG "
                   f"— một bản ghi kết quả thật bị xoá trắng")

    # (2) Phán quyết ĐI LÙI: xác định → vô tri (KHÔNG chặn chiều ngược lại).
    tt_cu, tt_moi = _trang_thai_theo_khoa(cu), _trang_thai_theo_khoa(moi)
    for khoa, cu_tt in tt_cu.items():
        moi_tt = tt_moi.get(khoa)
        if moi_tt is None:
            continue
        if not _la_vo_tri(cu_tt) and _la_vo_tri(moi_tt):
            loi.append(f"{ten}: [{khoa}] phán quyết ĐI LÙI '{cu_tt}' → '{moi_tt}' "
                       f"— máy này không kết luận được, không được ghi đè kết luận của máy có dữ liệu")

    # (3) Đường dẫn tuyệt đối bị viết lại sang MÁY KHÁC.
    goc_cu = {_goc_may(m) for m in _DUONG_TUYET_DOI.findall(cu)}
    goc_moi = {_goc_may(m) for m in _DUONG_TUYET_DOI.findall(moi)}
    them = goc_moi - goc_cu
    mat = goc_cu - goc_moi
    if them and mat:
        loi.append(f"{ten}: đường dẫn tuyệt đối bị viết lại sang MÁY KHÁC "
                   f"({sorted(mat)} → {sorted(them)}) — artifact của đề tài sẽ trỏ sai trên máy bác sĩ")
    return loi


def main() -> int:
    ap = argparse.ArgumentParser(description="Chặn commit khi artifact bằng chứng bị hạ cấp")
    ap.add_argument("--staged", action="store_true", help="soi thay đổi đã stage (dùng cho pre-commit)")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có ô nhiễm")
    a = ap.parse_args()

    ma, ra = _git("diff", "--cached" if a.staged else "", "--name-only", "--diff-filter=M")
    if ma != 0:
        if not a.im_khi_on:
            print("⚠ không chạy được git diff — bỏ qua (thiếu công cụ KHÔNG phải bằng chứng nguy hiểm)")
        return 0

    ten_files = [t for t in ra.splitlines() if t.strip()
                 and any(t.startswith(v) for v in VUNG_BANG_CHUNG)]
    loi: list[str] = []
    for ten in ten_files:
        ma_cu, cu = _git("show", f"HEAD:{ten}")
        if ma_cu != 0:
            continue
        try:
            moi = (REPO / ten).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        loi.extend(soi_mot_file(ten, cu, moi))

    if not loi:
        if not a.im_khi_on:
            print(f"🟢 Không thấy hạ cấp bằng chứng ({len(ten_files)} file bằng chứng đã soi).")
        return 0

    print("🔴 CHẶN COMMIT — ARTIFACT BẰNG CHỨNG BỊ HẠ CẤP")
    for x in loi:
        print(f"   • {x}")
    print("\n   Máy này nhiều khả năng THIẾU dữ liệu thật (USE_MOCK_SOURCES / nền Retraction")
    print("   Watch / secrets). Kiểm bằng: python3 tools/kiem_nguon_that.py --nhanh")
    print("   Cách xử lý ĐÚNG: hoàn nguyên các file trên (git checkout -- <file>), rồi chạy lại")
    print("   trên máy CÓ dữ liệu thật. KHÔNG commit bản đã hạ cấp.")
    print("   Cần bác sĩ kiểm chứng.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
