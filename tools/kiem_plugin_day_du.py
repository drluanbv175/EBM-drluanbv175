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

import sys as _s_ds, pathlib as _p_ds
_s_ds.path.insert(0, str(_p_ds.Path(__file__).resolve().parents[0]))
from doc_settings import doc_settings as _doc_settings, duong_dan_ghi as _dd_ghi  # noqa: E402


# Windows mặc định stdout=cp1252 → mọi print() tiếng Việt sẽ làm script chết giữa
# chừng. Đây là lỗi đã làm hỏng 7 script trong tools/vietnamize/ ngày 03/08/2026.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HOME = Path.home()
REPO = Path(__file__).resolve().parents[1]
REG = HOME / ".claude/plugins/installed_plugins.json"
SETTINGS = HOME / ".claude/settings.json"   # giữ để báo cáo; ĐỌC bằng _doc_settings()
MOC = REPO / "tools/moc_chuan_plugin.json"

# Ngưỡng cảnh báo: cache đang nạp lại có thể làm số skill hụt tạm thời. Dưới ngưỡng
# này coi là dao động bình thường (vàng), tụt sâu hơn mới coi là mất thật (đỏ).
NGUONG_HUT_VANG = 0.90   # còn ≥90% so với mốc → chỉ cảnh báo
NGUONG_HUT_DO = 0.50     # còn <50% so với mốc → gần như chắc chắn hỏng

# Cửa sổ ngữ cảnh quy ra KÝ TỰ (~200k token × 4). Dùng để quy đổi
# skillListingBudgetFraction — vốn khai theo phân số của cửa sổ — ra số ký tự thật.
CUA_SO_KY_TU = 800_000


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
    cfg = _doc_settings(nghiem=False, goc=SETTINGS)
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


def kiem_ngan_sach(hien: dict) -> list[str]:
    """Kiểm ngân sách DANH SÁCH SKILL — nguyên nhân thật của "gọi mà không có".

    Claude Code chỉ dành `skillListingBudgetFraction` (MẶC ĐỊNH 0.01 = 1% cửa sổ
    ngữ cảnh) cho danh sách skill gửi cho model. Vượt ngân sách thì nó CẮT: rụng mô
    tả trước, rồi rụng luôn skill. Kho 869 skill của máy này cần ~45.000 ký tự chỉ
    để hiện đủ TÊN — vượt mặc định 5,6 lần. Hệ quả đúng như bác sĩ mô tả: gõ gọi
    một plugin thì "không có", và danh sách "lúc đủ lúc không đủ" tuỳ những gì lọt
    vào ngân sách của phiên đó.

    Đây là chỗ hỏng KHÁC HẲN với đường dẫn treo hay cache vơi: file vẫn đủ trên đĩa,
    chỉ là model không được cho biết chúng tồn tại.
    """
    canh_bao: list[str] = []
    cfg = _doc_settings(nghiem=False, goc=SETTINGS)
    phan = cfg.get("skillListingBudgetFraction")
    if phan is None:
        phan = 0.01                      # mặc định của Claude Code
        mac_dinh = True
    else:
        mac_dinh = False

    can, tong_skill = do_ky_tu_can(hien)
    ngan_sach = int(CUA_SO_KY_TU * phan)

    if can > ngan_sach:
        canh_bao.append(
            f"DANH SÁCH SKILL VƯỢT NGÂN SÁCH: cần ~{can:,} ký tự để hiện đủ tên "
            f"{tong_skill} skill, nhưng skillListingBudgetFraction={phan} chỉ cho "
            f"{ngan_sach:,} ký tự (vượt {can/ngan_sach:.1f} lần)"
            + (" — ĐANG DÙNG MẶC ĐỊNH, chưa đặt trong ~/.claude/settings.json" if mac_dinh else "")
            + f". Hệ quả: gọi skill sẽ báo KHÔNG CÓ dù file vẫn đủ trên đĩa. "
              f"Đặt skillListingBudgetFraction ≈ {min(0.3, round(can/CUA_SO_KY_TU + 0.02, 2))}."
        )
    return canh_bao


def do_ky_tu_can(hien: dict) -> tuple[int, int]:
    """ĐO số ký tự cần để hiện đủ TÊN skill, và tổng số skill.

    Tách riêng khỏi `kiem_ngan_sach` (22/08/2026) để công cụ khác hỏi được phép ĐO
    mà không phải đọc ngược chuỗi cảnh báo — chuỗi đó chỉ tồn tại khi ĐÃ vượt, nên
    ai muốn kiểm «giá trị đã khai còn đủ không» sẽ không có gì để hỏi.

    ĐO thật độ dài từng dòng "- plugin:ten-skill" thay vì nhân một con số ước
    lượng: tên skill dài ngắn rất khác nhau (`esm` vs
    `active-comparator-single-soc-faers-safety-comparison`), ước lượng sẽ lệch.
    """
    can = 0
    tong_skill = 0
    for khoa, m in hien.items():
        pl = khoa.split("@")[0]
        goc = Path(m["duong_dan"])
        if not goc.is_dir():
            continue
        for root, _d, fs in os.walk(goc):
            if "SKILL.md" not in fs:
                continue
            can += len(f"- {pl}:{os.path.basename(root)}\n")
            tong_skill += 1
    # + skill và lệnh riêng của bác sĩ (~/.claude/skills, ~/.claude/commands)
    for thu_muc, hau_to in ((HOME / ".claude/skills", "SKILL.md"), (HOME / ".claude/commands", None)):
        if not thu_muc.is_dir():
            continue
        if hau_to:
            for root, _d, fs in os.walk(thu_muc):
                if hau_to in fs:
                    can += len(f"- {os.path.basename(root)}\n"); tong_skill += 1
        else:
            for f in thu_muc.glob("*.md"):
                can += len(f"- {f.stem}\n"); tong_skill += 1
    can += 8000          # ~14 skill dựng sẵn của Claude Code, mô tả rất dài
    return can, tong_skill


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
        # Phiên bản có ĐỔI hay không quyết định cách đọc con số hụt. Cùng một phiên bản
        # mà hụt skill là bất thường (cache nạp dở hoặc mất thật); ĐỔI phiên bản mà hụt
        # skill thì thường chỉ là nhà phát hành đổi bố cục file — đo thật 21/08/2026:
        # humanizer 2.11.1 có 2 `SKILL.md` (một cái lồng trong `skills/`), 2.11.2 bỏ cái
        # lồng còn 1. Gộp hai tình huống vào một câu «có thể cache đang nạp lại» là ĐOÁN
        # SAI nguyên nhân, và nó đẩy người đọc tới hai lựa chọn đều dở: hoặc chờ mãi một
        # thứ sẽ không bao giờ đổi, hoặc ghi mốc mới mà không biết mình đang ghi cái gì.
        doi_ban = m0.get("phien_ban") not in ("?", None) and m0["phien_ban"] != m["phien_ban"]
        if cu_n and moi_n < cu_n:
            ty = moi_n / cu_n
            loi = (f"{khoa}: {moi_n}/{cu_n} skill "
                   f"(hụt {cu_n - moi_n}, còn {ty*100:.0f}%)")
            if doi_ban:
                vang.append(
                    loi + f" — nhưng phiên bản đã đổi {m0['phien_ban']} → {m['phien_ban']}, "
                    "nên nhiều khả năng là nhà phát hành đổi bố cục file chứ không phải mất; "
                    "đối chiếu cache của HAI phiên bản rồi mới `--ghi-moc`")
            elif ty < NGUONG_HUT_DO:
                do.append(loi + " — hụt sâu mà phiên bản KHÔNG đổi: cache chưa nạp xong hoặc mất thật")
            elif ty < NGUONG_HUT_VANG:
                vang.append(loi + " — phiên bản không đổi, có thể cache đang nạp lại, đợi rồi kiểm lại")
        if doi_ban and moi_n >= cu_n:
            vang.append(f"{khoa}: đổi phiên bản {m0['phien_ban']} → {m['phien_ban']} "
                        f"— danh sách skill có thể đổi theo")

    them = set(hien) - set(cu)
    for khoa in sorted(them):
        goi_y = "chạy `--ghi-moc` nếu đây là chủ ý"
        # Bộ trùng quay lại KHÔNG BAO GIỜ là «chủ ý»: đó là dấu app vừa ghi đè
        # settings.json và xoá cờ `false`. Ghi mốc lúc đó sẽ nuốt luôn chỗ phồng,
        # và từ đó chốt này không còn báo được nữa (đo thật 17/08 và 21/08/2026).
        if khoa.startswith("medsci-"):
            goi_y = ("ĐỪNG `--ghi-moc` — nhiều khả năng app vừa xoá cờ `false`; "
                     "chạy `python3 tools/kiem_co_tat_plugin_trung.py --ap-dung` trước")
        vang.append(f"{khoa}: MỚI so với mốc — {goi_y}")

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

    # Ngân sách danh sách skill: vượt là skill "biến mất" với model dù file vẫn đủ.
    # Xếp mức ĐỎ vì hậu quả giống hệt mất plugin — bác sĩ gọi thì báo không có.
    thieu_ngan_sach = kiem_ngan_sach(hien)
    if thieu_ngan_sach:
        do.extend(thieu_ngan_sach)
        verdict = "🔴"

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
