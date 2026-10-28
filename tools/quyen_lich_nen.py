#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QUYỀN CHO LƯỢT LỊCH NỀN — khai đúng lệnh, áp vào máy, báo TRƯỚC khi lượt lịch hỏng (28/10/2026, BH173).

VÌ SAO CÓ
=========
Lượt lịch (app Claude, tác vụ `scheduled-tasks`) chạy ở chế độ quyền «default» và KHÔNG có ai bấm «cho phép». Lệnh nào chưa
nằm sẵn trong `permissions.allow` thì lượt bị cắt ngang («Tool permission request failed: AbortError…») mà bộ lập lịch VẪN ghi
«succeeded». Đo 28/10/2026: gói tuần W44 (kỳ 26/10) không có — lượt chết sau 73 giây ở `python3 tools/tu_de_xuat_viec.py`;
16/17 lệnh của gói tuần chưa được phép, không có quyền ghi tệp nào (19–23/10 đã chết 4 lượt liền cùng kiểu). Cảm biến
`kiem_lich_nen.py` chỉ thấy SAU khi kỳ đã lỡ.

LÀM GÌ
======
Nguồn khai DUY NHẤT: `sync/quyen-lich-nen.json` (đi qua git, bác sĩ duyệt «khai đúng lệnh» 28/10/2026) — mỗi tác vụ: `lenh`
(Y NHƯ trong SKILL.md, «*» thay tham số), `khong_chay` (lệnh SKILL.md chỉ IN cho bác sĩ tự chạy — không vào allow), `ghi`
(thư mục lượt lịch được ghi tệp bằng Write/Edit).
  · `--kiem` (mặc định): (1) mọi lệnh trong backtick của `sync/scheduled-tasks/<tác vụ>/SKILL.md` phải được một mục `lenh`
    phủ (thiếu ⇒ SKILL.md có lệnh mới mà chưa khai ⇒ lượt sẽ hỏng); (2) mọi quy tắc khai phải có trong
    `.claude/settings.local.json` của máy (thiếu ⇒ máy chưa áp).
  · `--ap-dung`: sao lưu `settings.local.json` rồi CHỈ THÊM các quy tắc khai còn thiếu (không xoá, không sửa mục khác).
Mã thoát: 0 = đủ · 1 = thiếu (in danh sách) · 2 = KHÔNG đo được (máy không phải nền tảng đã khai, thiếu/hỏng tệp) — ⚪, không
bao giờ là «đủ».

Ranh giới: chỉ khai lệnh ĐO/BÁO/DỰNG GÓI; không khai lệnh ghi quyết định thay bác sĩ (xem `_ranh_gioi` trong tệp khai).
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import re
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
KHAI = GOC / "sync" / "quyen-lich-nen.json"
NGUON_TAC_VU = GOC / "sync" / "scheduled-tasks"
SETTINGS = GOC / ".claude" / "settings.local.json"

# Lệnh trong backtick bắt đầu bằng trình chạy — đúng thứ lượt lịch sẽ gõ vào Bash.
_LENH_RE = re.compile(r"`((?:python3|~/\.ebm-venv/bin/python|bash) [^`\n]+)`")


def lenh_trong_skill(van_ban: str) -> list[str]:
    """Các lệnh (trong backtick) của một SKILL.md, giữ thứ tự, bỏ trùng."""
    ra: list[str] = []
    for m in _LENH_RE.finditer(van_ban):
        c = " ".join(m.group(1).split())
        if c not in ra:
            ra.append(c)
    return ra


def duoc_phu(lenh: str, quy_tac: list[str]) -> bool:
    """Lệnh SKILL.md (tham số viết «<…>») có được một quy tắc khai phủ không — «*» của quy tắc khớp mọi chuỗi, kể cả «<W>»."""
    return any(fnmatch.fnmatchcase(lenh, q) for q in quy_tac)


def quy_tac_may(khai: dict, goc: Path = GOC) -> list[str]:
    """Danh sách quy tắc permissions.allow (đúng cú pháp Claude Code) cho máy có gốc `goc`."""
    ra: list[str] = []
    tuyet_doi = "//" + str(goc).lstrip("/")
    for tv in khai.get("tac_vu", {}).values():
        for c in tv.get("lenh", []):
            r = f"Bash({c})"
            if r not in ra:
                ra.append(r)
        for g in tv.get("ghi", []):
            r = f"Edit({tuyet_doi}/{g})"
            if r not in ra:
                ra.append(r)
    return ra


def kiem(goc: Path = GOC, khai: dict | None = None, settings: Path | None = None, nen_tang: str | None = None) -> dict:
    """{'khong_do': [lý do], 'thieu_khai': [(tác vụ, lệnh)], 'thieu_may': [quy tắc]}. Thuần đọc."""
    ra: dict = {"khong_do": [], "thieu_khai": [], "thieu_may": []}
    if khai is None:
        try:
            khai = json.loads((goc / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            ra["khong_do"].append(f"không đọc được sync/quyen-lich-nen.json ({type(e).__name__})")
            return ra
    for ten, tv in khai.get("tac_vu", {}).items():
        skill = goc / "sync" / "scheduled-tasks" / ten / "SKILL.md"
        try:
            vb = skill.read_text(encoding="utf-8")
        except OSError:
            ra["khong_do"].append(f"{ten}: không đọc được {skill.relative_to(goc)}")
            continue
        phu = list(tv.get("lenh", [])) + list(tv.get("khong_chay", []))
        for c in lenh_trong_skill(vb):
            if not duoc_phu(c, phu):
                ra["thieu_khai"].append((ten, c))
    nt = nen_tang or sys.platform
    if nt != khai.get("nen_tang", "darwin"):
        ra["khong_do"].append(f"quy tắc khai cho nền tảng {khai.get('nen_tang')} — máy này là {nt}, chưa đối chiếu settings")
        return ra
    st = settings or (goc / ".claude" / "settings.local.json")
    try:
        allow = json.loads(st.read_text(encoding="utf-8")).get("permissions", {}).get("allow", [])
    except (OSError, ValueError) as e:
        ra["khong_do"].append(f"không đọc được {st.name} ({type(e).__name__})")
        return ra
    co = set(allow)
    ra["thieu_may"] = [q for q in quy_tac_may(khai, goc) if q not in co]
    return ra


def ap_dung(goc: Path = GOC, settings: Path | None = None) -> int:
    """Sao lưu rồi THÊM quy tắc khai còn thiếu vào settings.local.json. Trả số quy tắc đã thêm."""
    khai = json.loads((goc / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))
    st = settings or (goc / ".claude" / "settings.local.json")
    d = json.loads(st.read_text(encoding="utf-8"))
    allow = d.setdefault("permissions", {}).setdefault("allow", [])
    them = [q for q in quy_tac_may(khai, goc) if q not in set(allow)]
    if not them:
        return 0
    shutil.copy2(st, st.with_name(f"{st.name}.bak-quyen-lich-{dt.datetime.now():%Y%m%d-%H%M%S}"))
    allow.extend(them)
    st.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(them)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Quyền cho lượt lịch nền: khai đúng lệnh, áp vào máy, báo trước khi hỏng")
    ap.add_argument("--ap-dung", action="store_true", help="thêm quy tắc khai còn thiếu vào .claude/settings.local.json")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--im-khi-on", action="store_true", help="không in gì khi đủ")
    a = ap.parse_args(argv)
    if a.ap_dung:
        n = ap_dung()
        print(f"✓ Đã thêm {n} quy tắc vào .claude/settings.local.json (sao lưu *.bak-quyen-lich-*)." if n
              else "✓ settings.local.json đã đủ quy tắc khai — không ghi gì.")
    kq = kiem()
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
    if kq["thieu_khai"] or kq["thieu_may"]:
        if not a.json:
            print("🔴 LƯỢT LỊCH SẼ BỊ CẮT NGANG — có lệnh chưa được phép (lượt vẫn ghi «succeeded»):")
            for ten, c in kq["thieu_khai"]:
                print(f"   ✗ {ten}: SKILL.md có lệnh chưa khai ở sync/quyen-lich-nen.json — {c}")
            for q in kq["thieu_may"]:
                print(f"   ✗ máy chưa áp: {q}")
            print("   → khai lệnh mới ở sync/quyen-lich-nen.json (bác sĩ duyệt) rồi: python3 tools/quyen_lich_nen.py --ap-dung")
        return 1
    if kq["khong_do"]:
        if not a.json:
            print("⚪ Quyền lượt lịch: KHÔNG đo được trọn — không phải «đủ»:")
            for x in kq["khong_do"]:
                print(f"   ⚪ {x}")
        return 2
    if not (a.json or a.im_khi_on):
        print("🟢 Mọi lệnh của lượt lịch đã khai đều đã được phép trên máy này.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
