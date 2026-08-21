#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đồng bộ skill từ NGUỒN biên tập sang nơi Claude THẬT SỰ CHẠY.

VÌ SAO CÓ (13/08/2026)
======================
Bác sĩ sửa skill ở `sync/skills/` (nguồn biên tập, có git). Nhưng lệnh
`/anthropic-skills:<tên>` chạy một bản KHÁC nằm ở

    ~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/
        <uuid>/<uuid>/skills/<tên>/

và **không có cơ chế nào tự đẩy** từ nguồn sang đó. Hậu quả đo được ngày
13/08/2026: **20/22 skill riêng của bác sĩ đang chạy bản khác với nguồn**, chỉ 2
khớp. `cap-nhat-chung-cu-y-khoa` chạy v1.12.0 trong khi nguồn đã v1.15.0 —
tức toàn bộ bản vá cổng nguồn, bài học "73 mục bị che" và tài liệu source
universe đều CHƯA tới nơi bác sĩ thật sự gọi.

Điều này giải thích một lớp bực bội lặp lại: gọi skill và nhận hành vi cũ,
trong khi tài liệu nói về bản mới.

QUYẾT ĐỊNH CHIỀU: THEO NỘI DUNG, KHÔNG THEO mtime
==================================================
Cạm bẫy đã đo: 6 skill có mtime runtime MỚI HƠN nguồn (đều đúng mốc
`21/06 18:12`) — nhưng đó là dấu thời gian DỰNG LẠI HÀNG LOẠT, không phải nội
dung mới. Kiểm theo nội dung thì `tham-dinh-chung-cu-grade-nnt` runtime có **0
dòng riêng** trong khi nguồn nhiều hơn 1388 byte. Tin mtime sẽ chặn nhầm, hoặc
tệ hơn nếu đảo chiều thì ghi đè mất bản đầy đủ.

Nên luật là:
  • runtime KHÔNG có dòng nào riêng  → nguồn là bản bao trùm → ĐẨY (an toàn)
  • runtime CÓ dòng riêng            → phân kỳ hai chiều → CHẶN, chờ người xem
Không bao giờ tự hợp nhất hai chiều: mất nội dung y khoa nguy hiểm hơn nhiều
so với việc phải xem tay vài file.

Dùng:
    python3 tools/dong_bo_skill.py              # xem trước, KHÔNG ghi gì
    python3 tools/dong_bo_skill.py --ap-dung    # thật sự đẩy (có sao lưu)
    python3 tools/dong_bo_skill.py --im-khi-on  # chỉ nói khi lệch (dùng cho hook)

Mã thoát: 0 = mọi skill khớp · 1 = có skill lệch · 2 = có skill phân kỳ hai chiều.
"""
from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import hashlib
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
NGUON = REPO / "sync/skills"
GOC_RUNTIME = Path.home() / "Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"

BO_QUA = {".DS_Store", "__pycache__", ".claude"}

# VÁ 14/08/2026 — BỎ QUA THEO MẪU TÊN, không chỉ theo thành phần đường dẫn.
# `BO_QUA` so trên `f.parts` nên không bao giờ bắt được một TÊN FILE như
# `verify_dashboard.py.bak-20260814-005720`. Hệ quả đo được: **8 file sao lưu do
# CHÍNH quy trình đồng bộ này tạo ra đã bị đẩy vào thư mục skill ĐANG CHẠY**, nằm
# ngay cạnh bản sống. Không gây lỗi chạy (đuôi `.bak-*` không import được), nhưng
# kho sẽ phình mãi và một bản CŨ của công cụ an toàn nằm cạnh bản mới là thứ gây
# hiểu nhầm cho bất kỳ ai mở thư mục đó ra xem.
BO_QUA_MAU = ("*.bak-*", "*.orig", "*.rej", "*~")


def _bi_bo_qua(f: Path, goc: Path) -> bool:
    import fnmatch
    if any(x in f.parts for x in BO_QUA):
        return True
    return any(fnmatch.fnmatch(f.name, m) for m in BO_QUA_MAU)


def tim_runtime() -> Path | None:
    """Tìm thư mục skills đang chạy. Đường dẫn có 2 tầng UUID do Claude sinh ra,
    nên dò thay vì viết cứng — UUID đổi khi bác sĩ nạp lại bộ skill."""
    if not GOC_RUNTIME.is_dir():
        return None
    ung_vien = sorted(GOC_RUNTIME.glob("*/*/skills"),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    return ung_vien[0] if ung_vien else None


def _bam(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _dong_rieng(a: Path, b: Path) -> tuple[int, int]:
    """Trả (số dòng CHỈ có ở a, số dòng CHỈ có ở b). So theo TẬP DÒNG nên không
    bị ảnh hưởng bởi việc di chuyển đoạn — điều duy nhất cần biết ở đây là
    'có nội dung nào sẽ MẤT nếu ghi đè không'."""
    try:
        ta = set(a.read_text(encoding="utf-8", errors="replace").splitlines())
        tb = set(b.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return (0, 0)
    return (len(ta - tb), len(tb - ta))


def _doc_ver(p: Path) -> tuple[int, ...] | None:
    """Đọc `version:` trong frontmatter SKILL.md, trả tuple so sánh được."""
    import re
    try:
        t = p.read_text(encoding="utf-8", errors="replace")[:3000]
    except OSError:
        return None
    m = re.search(r'^\s*version:\s*"?(\d+(?:\.\d+)*)', t, re.M)
    if not m:
        return None
    return tuple(int(x) for x in m.group(1).split("."))


def nguon_moi_hon_theo_ver(nguon: Path, runtime: Path) -> bool:
    """Nguồn có số phiên bản CAO HƠN runtime không?

    VÌ SAO CẦN LUẬT NÀY: khi nguồn là bản nâng cấp (1.12.0 → 1.15.0), câu chữ cũ
    của runtime đương nhiên là "dòng riêng" — nhưng đó là nội dung ĐÃ ĐƯỢC VIẾT
    LẠI, không phải nội dung sẽ mất. Nếu chỉ đếm dòng riêng thì mọi lần nâng cấp
    đều bị chặn oan, và skill sẽ mãi không bao giờ được cập nhật.

    Một lần tăng số phiên bản là lời tuyên bố "bản này thay bản kia". Tôn trọng
    tuyên bố đó, NHƯNG vẫn sao lưu trước khi ghi — để nếu sai còn lấy lại được.
    Không có số phiên bản ở một trong hai bên → không suy đoán, giữ nguyên chặn.
    """
    vn, vr = _doc_ver(nguon / "SKILL.md"), _doc_ver(runtime / "SKILL.md")
    return bool(vn and vr and vn > vr)


def so_mot_skill(nguon: Path, runtime: Path) -> dict:
    """So một skill. Trả trạng thái + danh sách file cần đẩy."""
    can_day: list[Path] = []
    phan_ky: list[tuple[Path, int]] = []      # (file, số dòng runtime sẽ mất)
    for f in sorted(nguon.rglob("*")):
        if not f.is_file() or _bi_bo_qua(f, nguon):
            continue
        rel = f.relative_to(nguon)
        dich = runtime / rel
        if not dich.exists():
            can_day.append(rel)
            continue
        if filecmp.cmp(f, dich, shallow=False):
            continue
        _, rieng_runtime = _dong_rieng(f, dich)
        if rieng_runtime > 0:
            phan_ky.append((rel, rieng_runtime))
        else:
            can_day.append(rel)
    if phan_ky:
        # Nguồn là bản NÂNG CẤP có tuyên bố rõ → câu chữ cũ của runtime là nội
        # dung đã được viết lại, không phải nội dung bị mất. Đẩy cả, có sao lưu.
        if nguon_moi_hon_theo_ver(nguon, runtime):
            return {"trang_thai": "CAN_DAY_NANG_CAP",
                    "day": can_day + [r for r, _ in phan_ky], "phan_ky": []}
        return {"trang_thai": "PHAN_KY", "day": can_day, "phan_ky": phan_ky}
    if can_day:
        return {"trang_thai": "CAN_DAY", "day": can_day, "phan_ky": []}
    return {"trang_thai": "KHOP", "day": [], "phan_ky": []}


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ skill nguồn → nơi chạy")
    ap.add_argument("--ap-dung", action="store_true",
                    help="thật sự ghi (mặc định chỉ xem trước)")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi mọi skill đã khớp (dùng cho hook)")
    ap.add_argument("--don-bak", action="store_true",
                    help="dọn *.bak-* còn sót trong NƠI CHẠY (BH22: app có thể "
                         "nạp nhầm; sao lưu đúng chỗ là nguồn/git, không phải runtime)")
    ap.add_argument("--nguon-la-chuan", action="store_true",
                    help="phân kỳ hai chiều thì NGUỒN thắng (vẫn sao lưu trước khi "
                         "ghi). Mặc định KHÔNG bật: chạy riêng thì phân kỳ phải chặn "
                         "để bác sĩ xem. Chỉ bộ hợp nhất dong_bo_skill_claude_codex.py "
                         "mới truyền cờ này — đúng hợp đồng đã ghi ở AGENTS.md §Đồng bộ "
                         "skill/plugin: «nguồn OneDrive thắng runtime Cowork nhưng bản "
                         "cũ luôn được sao lưu».")
    a = ap.parse_args()

    runtime = tim_runtime()
    if a.don_bak and runtime:
        rac = list(runtime.rglob("*.bak-*"))
        for f in rac:
            f.unlink()
        print(f"✓ dọn {len(rac)} file .bak khỏi nơi chạy (BH22)")
        if not a.ap_dung:
            return 0
    if runtime is None:
        if not a.im_khi_on:
            print("⚠ Không tìm thấy thư mục skill đang chạy — bỏ qua.")
        return 0

    ket: dict[str, dict] = {}
    for d in sorted(NGUON.iterdir()):
        if not d.is_dir() or not (d / "SKILL.md").exists():
            continue
        rt = runtime / d.name
        if not rt.is_dir():
            ket[d.name] = {"trang_thai": "THIEU_HAN", "day": [], "phan_ky": []}
            continue
        ket[d.name] = so_mot_skill(d, rt)

    khop = [k for k, v in ket.items() if v["trang_thai"] == "KHOP"]
    can_day = [k for k, v in ket.items() if v["trang_thai"] in ("CAN_DAY", "CAN_DAY_NANG_CAP", "THIEU_HAN")]
    phan_ky = [k for k, v in ket.items() if v["trang_thai"] == "PHAN_KY"]

    if a.im_khi_on and not can_day and not phan_ky:
        return 0

    print(f"ĐỒNG BỘ SKILL — nguồn: sync/skills · nơi chạy: …/{runtime.parent.name[:8]}/skills")
    print(f"  khớp {len(khop)} · cần đẩy {len(can_day)} · phân kỳ hai chiều {len(phan_ky)}")

    if can_day:
        print("\n▸ CẦN ĐẨY (nguồn bao trùm, runtime không có nội dung riêng):")
        for k in can_day:
            n = len(ket[k]["day"]) or "toàn bộ"
            print(f"   {k:44s} {n} file")

    if phan_ky:
        if a.nguon_la_chuan:
            print("\n▸ PHÂN KỲ HAI CHIỀU — nguồn được chọn làm chuẩn, sao lưu trước khi ghi:")
        else:
            print("\n⚠ PHÂN KỲ HAI CHIỀU — KHÔNG tự đẩy, cần bác sĩ xem:")
        for k in phan_ky:
            for rel, mat in ket[k]["phan_ky"]:
                print(f"   {k}/{rel}: runtime có {mat} dòng sẽ MẤT nếu ghi đè")

    if not a.ap_dung:
        if can_day or phan_ky:
            print("\n(Chưa ghi gì. Thêm --ap-dung để đẩy nhóm an toàn.)")
        return 2 if phan_ky else (1 if can_day else 0)

    # --- Ghi thật, có sao lưu ---
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    da_day = 0
    # Skill phân kỳ chỉ vào danh sách ghi khi bác sĩ (hoặc bộ hợp nhất) đã chọn
    # nguồn làm chuẩn. Chúng được đẩy TRỌN nguồn: danh sách "day" của một skill
    # phân kỳ chỉ là phần giao, đẩy phần giao thì runtime vẫn giữ dòng riêng và
    # lần chạy sau lại báo phân kỳ y như cũ.
    if a.nguon_la_chuan:
        for k in phan_ky:
            ket[k]["day"] = []
        can_day = can_day + phan_ky
    for k in can_day:
        src, dst = NGUON / k, runtime / k
        if dst.exists():
            shutil.copytree(dst, dst.parent / f"{k}.bak-{stamp}", dirs_exist_ok=True)
        for rel in (ket[k]["day"] or [p.relative_to(src) for p in src.rglob("*") if p.is_file()]):
            f, d = src / rel, dst / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)
            da_day += 1
    print(f"\n✓ Đã đẩy {da_day} file cho {len(can_day)} skill (sao lưu đuôi .bak-{stamp}).")
    if phan_ky and not a.nguon_la_chuan:
        print(f"⚠ Bỏ qua {len(phan_ky)} skill phân kỳ hai chiều — chưa đụng tới.")
        return 2
    if phan_ky:
        print(f"  Trong đó {len(phan_ky)} skill phân kỳ đã bị nguồn ghi đè theo "
              f"--nguon-la-chuan; bản runtime cũ nằm ở .bak-{stamp}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
