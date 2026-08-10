#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt kiểm KHO CÔNG CỤ: bảo đảm plugin và skill có ĐỦ trước khi bác sĩ vào việc.

VÌ SAO CÓ (10/08/2026, sau khi bác sĩ hỏi "sao lúc gọi thì đủ lúc lại không đủ"):
kho công cụ trên máy này KHÔNG đứng yên trong một phiên làm việc. Đã đo được 4 cơ chế
làm danh sách thay đổi:

  1. Cache plugin bị dọn rồi tự nạp lại NGAY GIỮA PHIÊN. Đo trực tiếp: số skill của
     aipoch đi qua 605 → 360 → 438 → 475 → 605 trong MỘT phiên. Bộ máy gây ra là
     marker `.in_use` của từng plugin + `.last-cleanup` + `.last_inuse_sweep`.
  2. Plugin cài kiểu "directory" (aipoch · pubmed-search · meta-pipe) đồng bộ lại cache
     từ repo nguồn ở `~/Documents/GitHub/`, cũng giữa phiên.
  3. Phiên bản được chọn có thể đổi (mattpocock 1.2.0 → 1.2.3 sau khi dọn bản mồ côi),
     kéo theo danh sách skill đổi.
  4. Đường dẫn treo: `installed_plugins.json` trỏ vào thư mục cache không tồn tại →
     plugin BIẾN MẤT IM LẶNG. Đã xảy ra thật 05/08/2026 với 12 plugin.

Công cụ này KHÔNG sửa được cơ chế trên (nó thuộc về Claude Code). Việc nó làm là
PHÁT HIỆN SỚM: so trạng thái hiện tại với MỐC CHUẨN đã ghi, và nói rõ thiếu cái gì —
thay vì để bác sĩ vào việc rồi mới phát hiện thiếu công cụ giữa chừng.

Cố ý BI QUAN: chỉ báo động khi thiếu so với mốc, KHÔNG bao giờ tự nói "đã đủ mọi thứ"
cho những gì nó không đo được (ví dụ danh sách Claude Code thực sự nạp — xem GIỚI HẠN).

GIỚI HẠN PHẢI NHỚ: công cụ đếm file `SKILL.md` TRÊN ĐĨA. Con số đó KHÁC với số skill
Claude Code thật sự chào ra, vì mỗi plugin khai báo một kiểu trong `.claude-plugin/
plugin.json` (`claude-code-harness` khai `["./skills/"]` cả thư mục; `medsci-project`
khai 6 đường dẫn nhưng 58 skill vẫn gọi được; `mattpocock-skills` khai 25 mà chỉ 11
từng xuất hiện). Vì vậy đây là chốt kiểm TÍNH TOÀN VẸN CỦA KHO, không phải bản kiểm kê
những gì gọi được.

Dùng:
    python3 tools/kiem_plugin_day_du.py              # kiểm đầy đủ, in báo cáo
    python3 tools/kiem_plugin_day_du.py --ghi-moc    # ghi mốc chuẩn cho máy này
    python3 tools/kiem_plugin_day_du.py --im-khi-on  # chỉ nói khi CÓ VẤN ĐỀ (dùng cho hook)
    python3 tools/kiem_plugin_day_du.py --json       # xuất máy đọc

Mã thoát: 0 = đủ (🟢) · 1 = cảnh báo (🟡) · 2 = THIẾU, nên dừng (🔴)

Thuần thư viện chuẩn Python, không cần venv, không cần mạng.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path

# Windows mặc định stdout=cp1252 → mọi print() tiếng Việt sẽ làm script chết giữa
# chừng. Đây là lỗi đã làm hỏng 7 script trong tools/vietnamize/ ngày 03/08/2026.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HOME = Path.home()
REPO = Path(__file__).resolve().parents[1]
REG = HOME / ".claude/plugins/installed_plugins.json"
SETTINGS = HOME / ".claude/settings.json"
MOC = REPO / "tools/moc_chuan_plugin.json"

# Ngưỡng cảnh báo: cache đang nạp lại có thể làm số skill hụt tạm thời. Dưới ngưỡng
# này coi là dao động bình thường (vàng), tụt sâu hơn mới coi là mất thật (đỏ).
NGUONG_HUT_VANG = 0.90   # còn ≥90% so với mốc → chỉ cảnh báo
NGUONG_HUT_DO = 0.50     # còn <50% so với mốc → gần như chắc chắn hỏng


def ten_may() -> str:
    """Cùng quy ước với tools/vietnamize/extract_catalog.py để hai bộ không lệch nhau."""
    return {"Darwin": "Mac", "Windows": "Windows"}.get(
        platform.system(), platform.system() or "Khac")


def doc_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def dem_skill(goc: Path) -> int:
    """Đếm file SKILL.md. Dùng os.walk chứ không glob('**'): glob BỎ QUA thư mục ẩn,
    mà một số plugin để nội dung dưới thư mục có dấu chấm."""
    if not goc.is_dir():
        return 0
    return sum(1 for _r, _d, fs in os.walk(goc) if "SKILL.md" in fs)


def quet() -> dict:
    """Chụp trạng thái kho công cụ hiện tại."""
    reg = doc_json(REG)
    cfg = doc_json(SETTINGS)
    bat = {k for k, v in (cfg.get("enabledPlugins") or {}).items() if v}
    tat = {k for k, v in (cfg.get("enabledPlugins") or {}).items() if v is False}

    ra: dict[str, dict] = {}
    for khoa, muc in (reg.get("plugins") or {}).items():
        # Plugin vắng mặt trong enabledPlugins vẫn được Claude Code nạp (chỉ khi ghi
        # RÕ false mới là tắt) — cùng quy ước với extract_catalog.py.
        if khoa in tat:
            continue
        e = muc[0] if muc else {}
        p = Path(e.get("installPath", ""))
        ra[khoa] = {
            "duong_dan": str(p),
            "ton_tai": p.is_dir(),
            "phien_ban": e.get("version", "?"),
            "so_skill": dem_skill(p),
            "khai_bat": khoa in bat,
        }
    return ra


def so_moc(hien: dict, moc: dict) -> tuple[str, list[str], list[str]]:
    """So hiện tại với mốc chuẩn. Trả (verdict, lỗi đỏ, cảnh báo vàng)."""
    do: list[str] = []
    vang: list[str] = []

    for khoa, m in hien.items():
        if not m["ton_tai"]:
            do.append(f"{khoa}: ĐƯỜNG DẪN TREO — {m['duong_dan']} không tồn tại "
                      f"(đúng kiểu hỏng làm 12 plugin biến mất im lặng 05/08)")
            continue
        if m["so_skill"] == 0:
            vang.append(f"{khoa}: 0 skill trên đĩa (plugin có thể chỉ cấp lệnh/agent/MCP)")

    if not moc:
        vang.append("CHƯA CÓ MỐC CHUẨN cho máy này — chạy `--ghi-moc` khi kho đang đủ, "
                    "để lần sau có cái mà so.")
        return ("🟡" if vang else "🟢"), do, vang

    cu = moc.get("plugin", {})
    for khoa, m0 in cu.items():
        m = hien.get(khoa)
        if m is None:
            do.append(f"{khoa}: BIẾN MẤT khỏi kho (mốc có, nay không) — "
                      f"kiểm enabledPlugins và installed_plugins.json")
            continue
        cu_n, moi_n = m0.get("so_skill", 0), m["so_skill"]
        if cu_n and moi_n < cu_n:
            ty = moi_n / cu_n
            loi = (f"{khoa}: {moi_n}/{cu_n} skill "
                   f"(hụt {cu_n - moi_n}, còn {ty*100:.0f}%)")
            if ty < NGUONG_HUT_DO:
                do.append(loi + " — hụt sâu, nhiều khả năng cache chưa nạp xong hoặc mất thật")
            elif ty < NGUONG_HUT_VANG:
                vang.append(loi + " — có thể cache đang nạp lại, đợi rồi kiểm lại")
        if m0.get("phien_ban") not in ("?", None) and m0["phien_ban"] != m["phien_ban"]:
            vang.append(f"{khoa}: đổi phiên bản {m0['phien_ban']} → {m['phien_ban']} "
                        f"— danh sách skill có thể đổi theo")

    them = set(hien) - set(cu)
    for khoa in sorted(them):
        vang.append(f"{khoa}: MỚI so với mốc — chạy `--ghi-moc` nếu đây là chủ ý")

    return ("🔴" if do else "🟡" if vang else "🟢"), do, vang


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm kho plugin/skill có đủ không")
    ap.add_argument("--ghi-moc", action="store_true",
                    help="ghi trạng thái HIỆN TẠI thành mốc chuẩn cho máy này")
    ap.add_argument("--im-khi-on", action="store_true",
                    help="không in gì khi 🟢 (dùng cho hook, tránh nhiễu mỗi phiên)")
    ap.add_argument("--json", action="store_true", help="xuất JSON máy đọc")
    args = ap.parse_args()

    may = ten_may()
    hien = quet()

    if args.ghi_moc:
        moc = doc_json(MOC)
        moc.setdefault("_ghi_chu", (
            "Mốc chuẩn kho plugin theo TỪNG MÁY. Ghi lại bằng "
            "`python3 tools/kiem_plugin_day_du.py --ghi-moc` khi kho đang ĐỦ. "
            "Mac và Windows có bộ plugin khác nhau nên phải ghi riêng trên mỗi máy."))
        moc[may] = {"plugin": {k: {"so_skill": v["so_skill"],
                                   "phien_ban": v["phien_ban"]}
                               for k, v in hien.items()}}
        MOC.write_text(json.dumps(moc, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        tong = sum(v["so_skill"] for v in hien.values())
        print(f"✓ Đã ghi mốc chuẩn cho máy {may}: {len(hien)} plugin, {tong} skill.")
        print(f"  → {MOC}")
        return 0

    moc_may = doc_json(MOC).get(may, {})
    verdict, do, vang = so_moc(hien, moc_may)

    if args.json:
        print(json.dumps({"may": may, "verdict": verdict, "loi_do": do,
                          "canh_bao": vang, "plugin": hien},
                         ensure_ascii=False, indent=2))
        return 2 if do else (1 if vang else 0)

    if args.im_khi_on and verdict == "🟢":
        return 0

    tong = sum(v["so_skill"] for v in hien.values())
    print(f"{verdict} KHO CÔNG CỤ ({may}): {len(hien)} plugin, {tong} skill trên đĩa")

    if do:
        print("\n🔴 THIẾU — nên xử lý trước khi vào việc:")
        for x in do:
            print(f"   • {x}")
    if vang:
        print("\n🟡 Cần để ý:")
        for x in vang:
            print(f"   • {x}")

    if not do and not vang:
        print("   Khớp mốc chuẩn. (Chỉ nói về TÍNH TOÀN VẸN CỦA KHO trên đĩa — "
              "không khẳng định thay Claude Code là mọi skill đều gọi được.)")

    if do:
        print("\n   Cách xử lý thường dùng:")
        print("   • Đường dẫn treo → sửa `installPath` trong "
              "~/.claude/plugins/installed_plugins.json, hoặc cài lại plugin đó.")
        print("   • Hụt skill sâu → đợi 1-2 phút rồi chạy lại: cache có thể đang nạp lại.")
        print("   • Vẫn thiếu → kiểm `enabledPlugins` trong ~/.claude/settings.json.")

    return 2 if do else (1 if vang else 0)


if __name__ == "__main__":
    raise SystemExit(main())
