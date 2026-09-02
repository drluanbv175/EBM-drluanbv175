#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""don_bong_tieng_anh.py — Dọn «bóng tiếng Anh» trong ~/.claude/skills/.

VẤN ĐỀ. `~/.claude/skills/` tích lại các bản SAO của skill plugin: **trùng TÊN nhưng
nội dung tiếng Anh**, trong khi bản nằm trong plugin đã được Việt hoá. Mỗi skill vì thế
hiện HAI lần khi gõ `/`, và bản tiếng Anh không mang tiền tố nên thường thắng. Đo trên
Mac 26/08/2026: 707 thư mục, 643 trùng tên với plugin đang bật ⇒ mục gọi được
1720 → 1092, `INDEX-CONG-CU.md` 128 KB → 35 KB.

**Máy Windows CHƯA dọn** — bản chụp 28/08 còn **706 mục `user-skills`, 666 tiếng Anh**
(Mac sau khi dọn còn 145). Đây là một phần của lớp bực bội «Việt hoá lại bị lỗi».

🔴 BẪY ĐÃ MẮC KHI DỌN TAY 26/08 — lý do công cụ này tồn tại thay vì làm bằng tay:
phân loại theo TÊN đã cuốn nhầm **15 skill RIÊNG của bác sĩ** chỉ vì trùng tên skill
plugin (`literature-review`, `peer-review`, `statistical-analysis`, `treatment-plans`…).
Luật cứng: **loại trừ mọi tên có trong `sync/skills/` TRƯỚC, không xét theo tên plugin.**

BA NHÓM, xử lý khác nhau:
  ① CỦA BÁC SĨ  — tên có trong `sync/skills/`        → GIỮ, tuyệt đối không đụng
  ② BÓNG        — trùng tên skill của plugin ĐANG BẬT → CHUYỂN vào kho sao lưu
  ③ MỒ CÔI      — không plugin nào có                 → GIỮ (xoá là mất hẳn)

Chuyển chứ KHÔNG xoá: muốn lùi thì chuyển ngược thư mục là xong.

Chạy:
  python3 tools/don_bong_tieng_anh.py              # chỉ xem, không đụng gì
  python3 tools/don_bong_tieng_anh.py --ap-dung    # làm thật
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

for _l in (sys.stdout, sys.stderr):          # Windows: cp1252 giết print() tiếng Việt
    try:
        _l.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from doc_settings import doc_settings                      # noqa: E402

HOME = Path.home()
SKILLS = HOME / ".claude" / "skills"
REPO = Path(__file__).resolve().parents[1]
NGUON_BAC_SI = REPO / "sync" / "skills"
VN = re.compile(r"[àáâãèéêìíòóôõùúýăđĩũơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)


def ten_cua_bac_si() -> set[str]:
    """Tên skill do bác sĩ tự viết — LOẠI TRỪ TRƯỚC MỌI THỨ KHÁC (bẫy 26/08)."""
    if not NGUON_BAC_SI.is_dir():
        return set()
    return {d.name for d in NGUON_BAC_SI.iterdir() if (d / "SKILL.md").is_file()}


def ten_cua_plugin_dang_bat() -> set[str]:
    """Tên skill mà plugin ĐANG BẬT cung cấp. Plugin tắt không tính — bóng của một
    plugin đã tắt thì không che khuất gì cả."""
    cfg = doc_settings(nghiem=False)
    tat = {k.split("@")[0] for k, v in (cfg.get("enabledPlugins") or {}).items() if v is False}
    f = HOME / ".claude" / "plugins" / "installed_plugins.json"
    if not f.is_file():
        return set()
    duong: list[str] = []

    def di(o):
        if isinstance(o, dict):
            p = o.get("installPath")
            if isinstance(p, str) and not any(f"/{t}/" in p or f"\\{t}\\" in p for t in tat):
                duong.append(p)
            for v in o.values():
                di(v)
        elif isinstance(o, list):
            for v in o:
                di(v)

    try:
        di(json.loads(f.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return set()
    ten = set()
    for p in duong:
        d = Path(p)
        if d.is_dir():
            ten |= {s.parent.name for s in d.rglob("SKILL.md")}
    return ten


def la_tieng_anh(d: Path) -> bool | None:
    f = d / "SKILL.md"
    if not f.is_file():
        return None
    m = re.match(r"---\s*\n(.*?)\n---", f.read_text("utf-8", errors="replace"), re.S)
    if not m:
        return None
    mt = re.search(r"^description:\s*(.+)$", m.group(1), re.M)
    return None if not mt else not bool(VN.search(mt.group(1)))


def main() -> int:
    ap = argparse.ArgumentParser(description="Dọn bóng tiếng Anh trong ~/.claude/skills")
    ap.add_argument("--ap-dung", action="store_true", help="chuyển thật (mặc định chỉ xem)")
    ap.add_argument("--im-khi-on", action="store_true", help="im khi không có bóng nào")
    a = ap.parse_args()

    if not SKILLS.is_dir():
        if not a.im_khi_on:
            print(f"⚠ Máy này chưa có {SKILLS} — không có gì để dọn.")
        return 0

    bac_si, plugin = ten_cua_bac_si(), ten_cua_plugin_dang_bat()
    if not plugin:
        # Không đọc được danh sách plugin ⇒ KHÔNG BIẾT cái nào là bóng. Thiếu nguyên
        # liệu không phải bằng chứng có vấn đề (BH08) — và dọn mù ở đây là xoá nhầm.
        if not a.im_khi_on:
            print("⚠ Chưa đọc được danh sách skill của plugin đang bật — DỪNG, không dọn mù.")
        return 0

    giu_bac_si, bong, mo_coi = [], [], []
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if d.name in bac_si:
            giu_bac_si.append(d)
        elif d.name in plugin:
            bong.append(d)
        else:
            mo_coi.append(d)

    if a.im_khi_on and not bong:
        return 0

    print(f"BÓNG TIẾNG ANH trong {SKILLS}")
    print(f"  ① của bác sĩ (GIỮ)        : {len(giu_bac_si)}")
    print(f"  ② bóng của plugin (DỌN)   : {len(bong)}")
    print(f"  ③ mồ côi (GIỮ)            : {len(mo_coi)}")
    if not bong:
        print("\n🟢 Không có bóng nào — không cần dọn.")
        return 0

    en = sum(1 for d in bong if la_tieng_anh(d) is True)
    print(f"\n  Trong nhóm ② có {en}/{len(bong)} mục mô tả còn TIẾNG ANH.")
    for d in bong[:12]:
        print(f"     {d.name}")
    if len(bong) > 12:
        print(f"     … và {len(bong)-12} mục nữa")

    if not a.ap_dung:
        print("\n(Chưa đụng gì. Thêm --ap-dung để chuyển vào kho sao lưu.)")
        return 1

    kho = HOME / ".claude" / "skills-backup" / f"bong-tieng-anh-{datetime.now():%Y%m%d-%H%M%S}"
    kho.mkdir(parents=True, exist_ok=True)
    n = 0
    for d in bong:
        try:
            shutil.move(str(d), str(kho / d.name))
            n += 1
        except OSError as e:
            print(f"   ✗ {d.name}: {e}")
    print(f"\n✓ Đã chuyển {n} mục vào {kho}")
    print("  Muốn lùi: chuyển ngược thư mục là xong.")
    print("  Chạy lại danh mục: python3 tools/vietnamize/extract_catalog.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
