#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỒNG BỘ CÔNG CỤ SỔ CÁI HUB — nguồn git `sync/ebm-master-tools/` → bản chạy `EBM_MASTER/tools/` (18/10/2026).

VÌ SAO CÓ
=========
`EBM_MASTER/tools/` nằm NGOÀI git (luật `/*` của .gitignore), nên mọi sửa cầu nạp sổ cái hub
(`ingest_dashboard.py`) trước nay đi thẳng vào bản chạy — không PR, không diff, không test chạy
trên CI. Ngày 18/10/2026 thêm chế độ phiên bản nối tiếp cho cầu nạp: nguồn chuẩn chuyển vào git ở
`sync/ebm-master-tools/`, bản chạy được chép sang bằng công cụ này — cùng luật «chỉ tua nhanh» của
`tools/dong_bo_tac_vu_lich.py`, cộng một rào: chỉ chép mã ĐÃ GỘP.

Mỗi tệp trong DANH_SACH xếp một trong:
  • khop        — bản chạy trùng nguồn;
  • tut_hau     — bản chạy trùng khít MỘT phiên bản đã biết của nguồn (lịch sử git của tệp nguồn
                  hoặc sổ `PHIEN-BAN-DA-BIET.json`) ⇒ tự chép được (`--ap-dung`, sao lưu trước);
  • khac_rieng  — bản chạy khác MỌI phiên bản đã biết (có người sửa thẳng bản chạy) ⇒ KHÔNG chép
                  đè, in số dòng riêng cho bác sĩ xem — chép đè có thể xoá bản vá chưa hồi nguồn;
  • chua_co     — thư mục EBM_MASTER/tools/ có mà thiếu tệp ⇒ chép được (`--ap-dung`).
Không thấy EBM_MASTER/ (bản sao git trần, worktree không lồng cây OneDrive, CI) ⇒ ⚪ không đo
được, mã 0 — thiếu nguyên liệu không phải nguy hiểm (BH08).

RÀO «CHỈ MÃ ĐÃ GỘP» khi --ap-dung: cây đang chạy phải ở nhánh master/main VÀ tệp nguồn không có
sửa chưa commit — một phiên đang làm nhánh tính năng (hay cây chính lỡ checkout nhánh khác) không
được đẩy mã CHƯA DUYỆT vào bản chạy của sổ cái thật.

So NỘI DUNG (CRLF → LF, bỏ khoảng trắng cuối tệp), không so mtime.

Dùng:  python3 tools/dong_bo_cong_cu_hub.py [--im-khi-on]    # mã 1 nếu còn tụt hậu/khác riêng
       python3 tools/dong_bo_cong_cu_hub.py --ap-dung          # chép nguồn → bản chạy cho tệp tụt hậu
Mã thoát: 0 = khớp hết / đã chép xong / không đo được · 1 = còn lệch · 2 = lỗi vận hành.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
NGUON_REL = Path("sync") / "ebm-master-tools"
DANH_SACH = ("ingest_dashboard.py", "ledger_ids.py", "manage_ledger.py")
SO_PHIEN_BAN = "PHIEN-BAN-DA-BIET.json"
SO_LUONG_PHIEN_BAN = 40          # số phiên bản gần nhất trong lịch sử git đem so
NHANH_DA_GOP = ("master", "main")


def _nap_ban_sao_tran():
    spec = importlib.util.spec_from_file_location("_bst_dong_bo_hub", Path(__file__).resolve().parent / "ban_sao_tran.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _chuan(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n").rstrip()


def _sha(b: bytes) -> str:
    return hashlib.sha256(_chuan(b)).hexdigest()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None


def phien_ban_da_biet(repo: Path, ten: str) -> set[str]:
    """SHA (đã chuẩn hoá) của mọi phiên bản đã biết của nguồn: sổ PHIEN-BAN-DA-BIET.json (giữ mốc
    nguyên trạng TRƯỚC khi nguồn vào git — gộp kiểu squash sẽ làm mất commit đó khỏi master) ∪
    các phiên bản trong lịch sử git của tệp nguồn."""
    ra: set[str] = set()
    so = repo / NGUON_REL / SO_PHIEN_BAN
    if so.is_file():
        try:
            ra |= {str(x) for x in (json.loads(so.read_text(encoding="utf-8")).get(ten) or [])}
        except (OSError, ValueError, AttributeError):
            pass
    rel = (NGUON_REL / ten).as_posix()
    r = _git(repo, "log", f"-n{SO_LUONG_PHIEN_BAN}", "--format=%H", "--", rel)
    if r is not None and r.returncode == 0:
        for commit in r.stdout.decode().split():
            s = _git(repo, "show", f"{commit}:{rel}")
            if s is not None and s.returncode == 0:
                ra.add(_sha(s.stdout))
    return ra


def kiem_da_gop(repo: Path) -> str:
    """Chuỗi lý do TỪ CHỐI chép (rỗng = được chép): nhánh phải là master/main và mọi tệp nguồn
    không có sửa chưa commit."""
    r = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    if r is None or r.returncode != 0:
        return "không đọc được nhánh git của cây này"
    nhanh = r.stdout.decode().strip()
    if nhanh not in NHANH_DA_GOP:
        return (f"cây đang ở nhánh «{nhanh}», không phải master/main — chỉ chép mã ĐÃ GỘP "
                "(gộp PR rồi chạy ở cây chính)")
    for ten in DANH_SACH:
        d = _git(repo, "diff", "--quiet", "HEAD", "--", (NGUON_REL / ten).as_posix())
        if d is None or d.returncode not in (0, 1):
            return f"không kiểm được sửa chưa commit của {ten}"
        if d.returncode == 1:
            return f"{(NGUON_REL / ten).as_posix()} có sửa CHƯA commit — chỉ chép mã đã gộp"
    return ""


def phan_loai(repo: Path, ban_chay: Path) -> dict[str, str]:
    """{tên tệp: khop · tut_hau · khac_rieng · chua_co · thieu_nguon}."""
    ra: dict[str, str] = {}
    for ten in DANH_SACH:
        nguon = repo / NGUON_REL / ten
        dich = ban_chay / ten
        if not nguon.is_file():
            ra[ten] = "thieu_nguon"
        elif not dich.is_file():
            ra[ten] = "chua_co"
        else:
            sha_dich = _sha(dich.read_bytes())
            if sha_dich == _sha(nguon.read_bytes()):
                ra[ten] = "khop"
            elif sha_dich in phien_ban_da_biet(repo, ten):
                ra[ten] = "tut_hau"
            else:
                ra[ten] = "khac_rieng"
    return ra


def _so_dong_rieng(nguon: Path, dich: Path) -> int:
    dong_nguon = set(nguon.read_text(encoding="utf-8", errors="replace").splitlines())
    return sum(1 for d in dich.read_text(encoding="utf-8", errors="replace").splitlines()
               if d.strip() and d not in dong_nguon)


def ap_dung(repo: Path, hub: Path, loai: dict[str, str]) -> list[str]:
    """Chép nguồn → bản chạy cho tệp tut_hau/chua_co; sao lưu bản chạy cũ vào BACKUPS/tools/."""
    ban_chay = hub / "tools"
    sao_luu = hub / "BACKUPS" / "tools"
    nhan = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    da_chep = []
    for ten, trang_thai in loai.items():
        if trang_thai not in ("tut_hau", "chua_co"):
            continue
        nguon, dich = repo / NGUON_REL / ten, ban_chay / ten
        if dich.is_file():
            sao_luu.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dich, sao_luu / f"{Path(ten).stem}_{nhan}_truoc-dong-bo{Path(ten).suffix}")
        shutil.copyfile(nguon, dich)
        if _chuan(dich.read_bytes()) != _chuan(nguon.read_bytes()):
            raise OSError(f"chép {ten} xong nhưng nội dung không khớp nguồn")
        da_chep.append(ten)
    return da_chep


NHAN = {
    "khop": "✅ khớp nguồn chuẩn",
    "tut_hau": "🟡 tụt hậu nguồn git (trùng một phiên bản đã biết — tự chép được, --ap-dung)",
    "chua_co": "🟡 bản chạy chưa có (chép được, --ap-dung)",
    "khac_rieng": "⛔ KHÁC mọi phiên bản đã biết — có người sửa thẳng bản chạy; GIỮ LẠI chờ bác sĩ",
    "thieu_nguon": "⛔ thiếu tệp nguồn trong git",
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ công cụ sổ cái hub: sync/ebm-master-tools → EBM_MASTER/tools")
    ap.add_argument("--ap-dung", action="store_true", help="chép thật cho tệp tụt hậu (mặc định chỉ báo)")
    ap.add_argument("--im-khi-on", action="store_true", help="im lặng khi mọi tệp đã khớp")
    ap.add_argument("--goc", default=None,
                    help="thư mục gốc repo (chứa sync/ và EBM_MASTER/) — chỉ dùng cho kiểm thử")
    args = ap.parse_args()

    repo = Path(args.goc).resolve() if args.goc else REPO
    hub = (repo / "EBM_MASTER") if args.goc else _nap_ban_sao_tran().duong_goc("EBM_MASTER", repo)
    if hub is None or not (Path(hub) / "tools").is_dir():
        if not args.im_khi_on:
            print("⚪ Không thấy EBM_MASTER/tools/ cạnh repo này (bản sao trần/worktree) — không đo được, "
                  "không phải lỗi. Chạy ở cây chính trên máy có OneDrive.")
        return 0
    hub = Path(hub)

    try:
        loai = phan_loai(repo, hub / "tools")
    except OSError as e:
        print(f"⛔ Không đọc được tệp: {e}")
        return 2
    can_chep = [t for t, v in loai.items() if v in ("tut_hau", "chua_co")]
    da_chep: list[str] = []
    ly_do_tu_choi = ""
    if args.ap_dung and can_chep:
        ly_do_tu_choi = kiem_da_gop(repo)
        if not ly_do_tu_choi:
            try:
                da_chep = ap_dung(repo, hub, loai)
            except OSError as e:
                print(f"⛔ Chép thất bại: {e}")
                return 2
            loai = phan_loai(repo, hub / "tools")

    on_het = all(v == "khop" for v in loai.values())
    if args.im_khi_on and on_het and not da_chep:
        return 0
    print(f"ĐỒNG BỘ CÔNG CỤ SỔ CÁI HUB — nguồn {NGUON_REL.as_posix()}/ → {(hub / 'tools').as_posix()}/")
    for ten, v in loai.items():
        dong = f"  {ten}: {NHAN[v]}"
        if v == "khac_rieng":
            dong += f" ({_so_dong_rieng(repo / NGUON_REL / ten, hub / 'tools' / ten)} dòng không có ở nguồn)"
        print(dong)
    if da_chep:
        print(f"  🔧 Đã chép {', '.join(da_chep)} (bản cũ sao lưu ở {(hub / 'BACKUPS' / 'tools').as_posix()}/).")
    if ly_do_tu_choi:
        print(f"  ⛔ KHÔNG chép: {ly_do_tu_choi}.")
    print("Cần bác sĩ kiểm chứng.")
    return 0 if on_het else 1


if __name__ == "__main__":
    raise SystemExit(main())
