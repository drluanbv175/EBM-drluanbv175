#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỒNG BỘ TÁC VỤ LỊCH — nguồn git `sync/scheduled-tasks/` → bản chạy của app (`~/.claude/scheduled-tasks/`), 29/09/2026.

VÌ SAO CÓ
=========
Đo 29/09: 13/14 bản chạy SKILL.md trên Mac tụt hậu nguồn git — phần lớn là bản 17/08. Hệ quả: PR #58 (tác vụ chạy đa
nền) và các sửa sau đó KHÔNG có hiệu lực trên máy này suốt 6 tuần mà không ai biết, còn tác vụ mới
`kiem-rut-bai-kho-thang` (PR #57) chưa từng được tạo. CLAUDE.md §9 đã có luật «chép SKILL.md từ NGUỒN GIT sang runtime,
không chép ngược» — nhưng không gì chạy luật đó (họ BH41: công cụ/luật không ai gọi thì như không có).

PHẠM VI: chỉ các tác vụ PHẢI hoạt động theo `sync/lich-nen-ky-vong.json`. Mỗi tác vụ xếp một trong:
  • khop      — bản chạy trùng nguồn hiện tại;
  • tut_hau   — bản chạy trùng khít MỘT phiên bản CŨ của nguồn trong git ⇒ tự chép được (`--ap-dung`, sao lưu trước);
  • khac_rieng — bản chạy khác MỌI phiên bản nguồn (có sửa riêng) ⇒ KHÔNG chép đè, cần bác sĩ xem;
  • chua_tao  — có nguồn, không có bản chạy ⇒ tạo tác vụ trong app là việc của bác sĩ (máy KHÔNG tự tạo/xoá tác vụ).
  • cho_quyen — (14/11/2026) bản chạy tụt hậu NHƯNG lệnh của SKILL mới chưa được phép trên máy (`quyen_lich_nen --tac-vu`
                chưa 🟢) ⇒ GIỮ bản chạy cũ, KHÔNG chép; việc của bác sĩ: `python3 tools/quyen_lich_nen.py --ap-dung`.
Không có thư mục bản chạy (Cloud, máy chưa cài app) ⇒ ⚪ không đo được, mã 0 — không báo đỏ giả.

CỔNG QUYỀN TRƯỚC KHI CHÉP (đính chính PR #339, 14/11/2026): hook SessionStart gọi `tu_sua_chua --ap-dung` — bước tua nhanh
master (`day_do_song_cloud`) chạy TRƯỚC bước chép này ⇒ SKILL vừa gộp vào runtime ngay phiên Mac kế tiếp, TRƯỚC khi bác sĩ áp
quyền. SKILL mới thêm lệnh chưa được phép (vd bước 0 tiền kiểm của tác vụ tháng) thì lượt lịch kế tiếp bị cắt ngay lệnh đó — mất
cả phần trước đó vẫn chạy được ở bản cũ (bộ thu thập an toàn thuốc). Vì vậy tác vụ có hợp đồng quyền (khoá trong
`sync/quyen-lich-nen.json`, hoặc SKILL tự gọi `quyen_lich_nen.py --tac-vu …`) chỉ được chép khi đúng tập quyền đó 🟢 trên máy;
không đo được quyền ⇒ cũng giữ (fail-closed). Tác vụ không có hợp đồng quyền, hoặc tệp khai dành cho nền tảng khác máy này ⇒
chép như cũ.

Dùng:  python3 tools/dong_bo_tac_vu_lich.py [--im-khi-on]      # mã 1 nếu có tác vụ tụt hậu
       python3 tools/dong_bo_tac_vu_lich.py --ap-dung            # chép nguồn → bản chạy cho tác vụ tụt hậu
       python3 tools/dong_bo_tac_vu_lich.py --can-bac-si         # mã 1 nếu có tác vụ chưa tạo / có sửa riêng
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
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
SO_LUONG_PHIEN_BAN = 40          # số phiên bản nguồn gần nhất đem so khi tìm bản chạy tụt hậu


def thu_muc_ban_chay() -> Path:
    return Path(os.environ.get("EBM_TAC_VU_LICH_DIR") or (Path.home() / ".claude" / "scheduled-tasks"))


def tac_vu_ky_vong(repo: Path) -> list[str]:
    d = json.loads((repo / "sync" / "lich-nen-ky-vong.json").read_text(encoding="utf-8"))
    return [str(t["id"]) for t in d.get("tac_vu", []) if t.get("id")]


def _phien_ban_cu(repo: Path, rel: str) -> list[bytes] | None:
    """Nội dung các phiên bản của `rel` trong lịch sử git (mới → cũ), hoặc None nếu không đọc được git."""
    try:
        r = subprocess.run(["git", "-C", str(repo), "log", f"-n{SO_LUONG_PHIEN_BAN}", "--format=%H", "--", rel],
                           capture_output=True, timeout=60, check=True)
        ra = []
        for c in r.stdout.decode().split():
            s = subprocess.run(["git", "-C", str(repo), "show", f"{c}:{rel}"], capture_output=True, timeout=60)
            if s.returncode == 0:
                ra.append(s.stdout)
        return ra
    except (OSError, subprocess.SubprocessError):
        return None


def _chuan(b: bytes) -> bytes:
    """So NỘI DUNG, không so cách app ghi tệp: app tạo tác vụ ghi SKILL.md KHÔNG có dòng trống cuối (đo 29/09 với
    `kiem-rut-bai-kho-thang`) ⇒ so thô sẽ báo «sửa riêng» giả. Bỏ khoảng trắng cuối tệp, CRLF → LF."""
    return b.replace(b"\r\n", b"\n").rstrip()


_TIEN_KIEM_RE = re.compile(r"`python3 tools/quyen_lich_nen\.py --tac-vu ([^`\s]+)`")


def _nap_quyen():
    """Nạp `quyen_lich_nen.py` nằm CẠNH công cụ này — cùng hàm `kiem()` mà bước 0 tiền kiểm của lượt lịch dùng."""
    sp = importlib.util.spec_from_file_location("_dbtvl_quyen_lich_nen", Path(__file__).resolve().parent / "quyen_lich_nen.py")
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def cong_quyen(repo: Path, ma: str, nen_tang: str | None = None) -> tuple[str, list[str]]:
    """Quyền của SKILL NGUỒN tác vụ `ma` trên máy: ('khong_ap'|'du'|'thieu'|'khong_do', các dòng lý do).

    Tập quyền xét = danh sách trong lệnh tiền kiểm `quyen_lich_nen.py --tac-vu …` của chính SKILL nguồn (nếu có), ngược lại
    khoá `ma` trong `sync/quyen-lich-nen.json`. 'khong_ap' = tác vụ không có hợp đồng quyền / tệp khai vắng / khai cho nền
    tảng khác ⇒ không chặn. 'khong_do' = có hợp đồng mà không đo được (tệp khai hỏng, settings không đọc được…) ⇒ chặn."""
    try:
        khai = json.loads((repo / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "khong_ap", []
    except (OSError, ValueError) as e:
        return "khong_do", [f"không đọc được sync/quyen-lich-nen.json ({type(e).__name__})"]
    if (nen_tang or sys.platform) != khai.get("nen_tang", "darwin"):
        return "khong_ap", []
    try:
        vb = (repo / "sync" / "scheduled-tasks" / ma / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return "khong_do", [f"không đọc được SKILL nguồn của {ma}"]
    m = _TIEN_KIEM_RE.search(vb)
    if m:
        ds = [t for t in m.group(1).split(",") if t]
    elif ma in khai.get("tac_vu", {}):
        ds = [ma]
    else:
        return "khong_ap", []
    kq = _nap_quyen().kiem(repo, khai=khai, nen_tang=nen_tang or sys.platform, tac_vu=ds)
    if kq["thieu_khai"] or kq["thieu_may"]:
        return "thieu", ([f"SKILL có lệnh chưa khai: {c}" for _t, c in kq["thieu_khai"]]
                         + [f"máy chưa áp: {q}" for q in kq["thieu_may"]])
    if kq["khong_do"]:
        return "khong_do", list(kq["khong_do"])
    return "du", []


def phan_loai(repo: Path, ban_chay: Path, nen_tang: str | None = None) -> dict[str, str]:
    """{id tác vụ: khop · tut_hau · cho_quyen · khac_rieng · chua_tao · thieu_nguon · khong_do_duoc}."""
    ra: dict[str, str] = {}
    for ma in tac_vu_ky_vong(repo):
        nguon = repo / "sync" / "scheduled-tasks" / ma / "SKILL.md"
        dich = ban_chay / ma / "SKILL.md"
        if not nguon.exists():
            ra[ma] = "thieu_nguon"
        elif not dich.exists():
            ra[ma] = "chua_tao"
        elif _chuan(dich.read_bytes()) == _chuan(nguon.read_bytes()):
            ra[ma] = "khop"
        else:
            cu = _phien_ban_cu(repo, nguon.relative_to(repo).as_posix())
            if cu is None:
                ra[ma] = "khong_do_duoc"
            else:
                ra[ma] = "tut_hau" if _chuan(dich.read_bytes()) in {_chuan(b) for b in cu} else "khac_rieng"
        if ra[ma] == "tut_hau" and cong_quyen(repo, ma, nen_tang)[0] in ("thieu", "khong_do"):
            ra[ma] = "cho_quyen"
    return ra


def ap_dung(repo: Path, ban_chay: Path, loai: dict[str, str], nen_tang: str | None = None) -> tuple[list[str], Path | None]:
    """Chép nguồn → bản chạy cho tác vụ tụt hậu; sao lưu CẢ thư mục bản chạy (ngoài OneDrive) trước khi ghi.

    Kiểm lại cổng quyền NGAY trước khi chép (người gọi có thể truyền `loai` tính từ trước/ở nơi khác): quyền của SKILL mới
    chưa 🟢 ⇒ không chép tác vụ đó."""
    can = [ma for ma, v in loai.items()
           if v == "tut_hau" and cong_quyen(repo, ma, nen_tang)[0] not in ("thieu", "khong_do")]
    if not can:
        return [], None
    sao_luu = ban_chay.parent / f"{ban_chay.name}-backup-{dt.datetime.now():%Y%m%d-%H%M%S}"
    shutil.copytree(ban_chay, sao_luu)
    for ma in can:
        shutil.copyfile(repo / "sync" / "scheduled-tasks" / ma / "SKILL.md", ban_chay / ma / "SKILL.md")
    return can, sao_luu


_NHAN = {
    "tut_hau": "🟡 tụt hậu nguồn git (tự chép được, --ap-dung)",
    "cho_quyen": ("👤 tụt hậu nhưng GIỮ bản chạy cũ — lệnh của SKILL mới chưa được phép (hoặc không đo được quyền) trên máy; "
                  "chép vào thì lượt lịch bị cắt ngang: bác sĩ chạy python3 tools/quyen_lich_nen.py --ap-dung, phiên sau tự chép"),
    "khac_rieng": "🔴 bản chạy có sửa riêng — KHÔNG chép đè, cần bác sĩ xem",
    "chua_tao": "👤 chưa tạo trong app — bác sĩ tạo tác vụ (máy không tự tạo)",
    "thieu_nguon": "⚪ kỳ vọng có nhưng không thấy nguồn trong git",
    "khong_do_duoc": "⚪ không đọc được lịch sử git — không phân loại được",
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Đồng bộ tác vụ lịch: nguồn git → bản chạy của app")
    ap.add_argument("--ap-dung", action="store_true", help="chép nguồn → bản chạy cho tác vụ tụt hậu (sao lưu trước)")
    ap.add_argument("--can-bac-si", action="store_true", help="mã 1 nếu có tác vụ chưa tạo hoặc có sửa riêng")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có việc")
    a = ap.parse_args()

    ban_chay = thu_muc_ban_chay()
    if not ban_chay.is_dir():
        if not a.im_khi_on:
            print(f"⚪ Không có thư mục tác vụ lịch của app ({ban_chay}) — máy này không chạy tác vụ lịch, không đo được.")
        return 0
    loai = phan_loai(REPO, ban_chay)
    if a.ap_dung:
        da_chep, sao_luu = ap_dung(REPO, ban_chay, loai)
        if da_chep:
            print(f"✓ Đã chép nguồn → bản chạy: {', '.join(da_chep)} (sao lưu: {sao_luu})")
        loai = phan_loai(REPO, ban_chay)

    # cho_quyen là việc của BÁC SĨ (áp quyền), không phải việc máy tự sửa: chỉ làm `--can-bac-si` đỏ — để bước sửa của
    # tu_sua_chua không chạy lại vô ích mỗi phiên rồi báo «chưa sửa được».
    viec_bac_si = ("chua_tao", "khac_rieng", "cho_quyen")
    can_bac_si = {ma: v for ma, v in loai.items() if v in viec_bac_si}
    quan_tam = can_bac_si if a.can_bac_si else {ma: v for ma, v in loai.items() if v != "khop"}
    if quan_tam:
        print(f"ĐỒNG BỘ TÁC VỤ LỊCH — nguồn: sync/scheduled-tasks · bản chạy: {ban_chay}")
        for ma, v in sorted(quan_tam.items()):
            print(f"   {ma}: {_NHAN[v]}")
            if v == "cho_quyen" and not a.im_khi_on:
                for dong in cong_quyen(REPO, ma)[1][:8]:
                    print(f"      ✗ {dong}")
    elif not a.im_khi_on:
        print(f"🟢 {len(loai)}/{len(loai)} tác vụ kỳ vọng khớp nguồn git.")
    if a.can_bac_si:
        return 1 if any(v in viec_bac_si for v in loai.values()) else 0
    return 1 if any(v == "tut_hau" for v in loai.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
