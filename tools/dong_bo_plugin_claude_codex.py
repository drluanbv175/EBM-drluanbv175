#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ĐỐI CHIẾU KHO PLUGIN — giữa hai MÁY, và giữa Claude với Codex.

VÌ SAO CÓ (21/08/2026). `tools/dong_bo_skill_claude_codex.py --dong-bo-plugin` gọi
đúng tên file này từ ngày 20/08 và AGENTS.md đã tài liệu hoá nó, nhưng **file chưa
bao giờ tồn tại trong repo**: mọi lượt chạy có cờ đó đều thoát mã 2 kèm dòng
`can't open file`. Đây là chân «đồng bộ Plugin» — thứ duy nhất trong bộ ba
skill·plugin·agent chưa từng có công cụ.

CÂU HỎI NÓ TRẢ LỜI, mà không công cụ nào trước đó trả lời được:

  1. **«Máy kia có gì mà máy này không có?»** `kiem_plugin_day_du.py` cố ý chỉ so
     máy hiện tại với MỐC CHUẨN CỦA CHÍNH NÓ (`moc_chuan_plugin.json`, ghi riêng
     mỗi máy). Đó là thiết kế đúng cho câu hỏi «kho có vơi đi không», nhưng nó
     KHÔNG bao giờ nhìn sang máy kia. Đo trên chính hai mốc đang có: Mac 9 plugin
     / 839 skill, Windows 3 plugin / 668 skill — **6 plugin chỉ có ở Mac**.
  2. **«Chỗ thiếu đó là CỐ Ý hay TRÔI DẠT?»** Hai thứ này nhìn giống hệt nhau
     trong mọi bản kiểm cũ, mà xử lý thì ngược nhau: cố ý thì để yên, trôi dạt thì
     phải cài lại. Trả lời được nhờ SỔ KHAI Ý ĐỊNH `sync/plugin-manifest.json` —
     đi qua git nên hai máy đọc CÙNG một bản.
  3. **«Codex có với tới được không?»** Codex không có trình quản lý plugin; nó chỉ
     đọc `~/.codex/skills`. Nên một plugin bật ở Claude KHÔNG tự nghĩa là Codex
     dùng được.

BA VIỆC NÓ TUYỆT ĐỐI KHÔNG LÀM:
  · **Không cài/gỡ plugin qua mạng.** CLAUDE.md ghi rõ bài học 11/08: gỡ mục khỏi
    `enabledPlugins` khiến Claude Code CÀI LẠI 278 MB và 464 skill trùng tràn vào
    danh sách. Vắng mặt trong `enabledPlugins` = BẬT, không phải tắt.
  · **Không tự sửa `enabledPlugins`.** Đó là ý định của bác sĩ, không phải trạng
    thái máy móc để công cụ đồng bộ.
  · **Không chiếu skill sang Codex nếu sổ khai không cho phép.** Đổ cả 839 skill
    vào `~/.codex/skills` là làm hại: vừa nặng, vừa lặp lại đúng thế vượt ngân sách
    danh sách skill đã hành bác sĩ nhiều tháng.

Mã thoát: 0 = khớp sổ khai (🟢) · 1 = có chênh cần để ý (🟡) · 2 = trôi dạt/mâu
thuẫn sổ khai (🔴). Thuần thư viện chuẩn, không mạng.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lien_ket_da_nen as LK           # noqa: E402  (cần sau khi chỉnh sys.path)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

HOME = Path.home()
REPO = Path(__file__).resolve().parents[1]
REG = HOME / ".claude/plugins/installed_plugins.json"
SETTINGS = HOME / ".claude/settings.json"
CODEX_SKILLS = HOME / ".codex/skills"
MOC = REPO / "tools/moc_chuan_plugin.json"
SO_KHAI = REPO / "sync/plugin-manifest.json"


def ten_may() -> str:
    """Cùng quy ước với kiem_plugin_day_du.py và vietnamize/extract_catalog.py."""
    return {"Darwin": "Mac", "Windows": "Windows"}.get(
        platform.system(), platform.system() or "Khac")


def doc_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def dem_skill(goc: Path) -> int:
    """Đếm SKILL.md bằng os.walk — glob('**') bỏ qua thư mục ẩn, mà một số plugin
    để nội dung dưới thư mục có dấu chấm (cùng lý do đã ghi ở kiem_plugin_day_du)."""
    if not goc.is_dir():
        return 0
    return sum(1 for _r, _d, fs in os.walk(goc) if "SKILL.md" in fs)


def quet_claude() -> dict:
    """Chụp kho plugin Claude trên máy này.

    Giữ NGUYÊN quy ước «vắng mặt trong enabledPlugins = BẬT»: chỉ mục ghi RÕ
    `false` mới là tắt. Đảo quy ước này là tái diễn sự cố 11/08 (cài lại 278 MB).
    """
    reg = doc_json(REG)
    cfg = doc_json(SETTINGS)
    khai = cfg.get("enabledPlugins") or {}
    tat = {k for k, v in khai.items() if v is False}

    ra: dict[str, dict] = {}
    for khoa, muc in (reg.get("plugins") or {}).items():
        e = muc[0] if muc else {}
        duong_dan = Path(e.get("installPath", ""))
        ra[khoa] = {
            "bat": khoa not in tat,
            "khai_tat_ro": khoa in tat,
            "duong_dan": str(duong_dan),
            "ton_tai": duong_dan.is_dir(),
            "phien_ban": e.get("version", "?"),
            "so_skill": dem_skill(duong_dan),
        }
    return ra


def tao_so_khai(hien: dict, may: str) -> dict:
    """Dựng sổ khai LẦN ĐẦU từ dữ liệu ĐO ĐƯỢC, không phải từ trí nhớ.

    Nguồn: mốc chuẩn đã ghi của CẢ HAI máy (`moc_chuan_plugin.json`) hợp với ảnh
    chụp máy đang chạy. Mọi ô «ý định» mà máy không thể biết đều để trống kèm nhãn
    [CẦN BÁC SĨ] — công cụ không được đoán hộ bác sĩ điều gì là chủ ý.
    """
    moc = doc_json(MOC)
    cu = doc_json(SO_KHAI)
    cu_plugin = cu.get("plugin", {})
    may_biet = [m for m in moc if not m.startswith("_")]

    gop: dict[str, dict] = {}
    for m in may_biet:
        for khoa, v in (moc[m].get("plugin") or {}).items():
            gop.setdefault(khoa, {})[m] = v
    for khoa, v in hien.items():
        gop.setdefault(khoa, {})[may] = {"so_skill": v["so_skill"],
                                         "phien_ban": v["phien_ban"]}

    plugin: dict[str, dict] = {}
    for khoa in sorted(gop):
        giu = cu_plugin.get(khoa, {})
        co_o = sorted(gop[khoa])
        tat_ro = khoa in hien and hien[khoa]["khai_tat_ro"]
        # `can_o_may` khởi tạo từ nơi ĐO ĐƯỢC là suy diễn «hiện trạng = chủ ý» —
        # đúng thứ công cụ này sinh ra để chống. Nên nó đi kèm `da_xac_nhan: false`
        # và chừng nào còn false thì đối chiếu chỉ CẢNH BÁO, không bao giờ báo đỏ.
        # Giữ nguyên ô bác sĩ đã sửa tay ở lần dựng trước.
        plugin[khoa] = {
            "can_o_may": giu.get("can_o_may", [] if tat_ro else co_o),
            "da_xac_nhan": giu.get("da_xac_nhan", False),
            "chieu_sang_codex": giu.get("chieu_sang_codex", False),
            "ly_do": giu.get("ly_do", (
                "[CẦN BÁC SĨ] plugin đang TẮT rõ trong enabledPlugins — khai vì sao"
                if tat_ro else "[CẦN BÁC SĨ] vì sao cần plugin này, và cần ở máy nào")),
            "do_duoc_luc_ghi": {m: gop[khoa][m].get("so_skill", 0) for m in co_o},
        }
    return {
        "_ghi_chu": (
            "SỔ KHAI Ý ĐỊNH về kho plugin — đi qua git nên HAI MÁY đọc cùng một bản. "
            "Khác moc_chuan_plugin.json (ảnh chụp TRẠNG THÁI riêng từng máy): file này "
            "khai Ý ĐỊNH — plugin nào CẦN có ở máy nào, và vì sao. Nhờ vậy mới tách "
            "được «thiếu vì cố ý» khỏi «thiếu vì trôi dạt», hai thứ trông giống hệt "
            "nhau nhưng xử lý ngược nhau. Sửa TAY file này; công cụ chỉ đọc."),
        "_cach_dung": (
            "python3 tools/dong_bo_plugin_claude_codex.py            # đối chiếu, chỉ đọc\n"
            "python3 tools/dong_bo_plugin_claude_codex.py --ap-dung  # nối skill sang Codex\n"
            "python3 tools/dong_bo_plugin_claude_codex.py --tao-so-khai  # dựng lại khung"),
        "_truong": {
            "can_o_may": "danh sách máy PHẢI có plugin này (Mac/Windows)",
            "chieu_sang_codex": "true = nối skill của plugin vào ~/.codex/skills",
            "ly_do": "vì sao — để người đọc sau biết đây là chủ ý, không phải sót",
            "do_duoc_luc_ghi": "số skill ĐO ĐƯỢC lúc dựng sổ, chỉ để tham chiếu",
        },
        "phien_ban_so_khai": 1,
        "plugin": plugin,
    }


def doi_chieu(hien: dict, so_khai: dict, may: str) -> tuple[list[str], list[str], list[str]]:
    """So kho thật với sổ khai. Trả (đỏ, vàng, xanh-thông-tin)."""
    do: list[str] = []
    vang: list[str] = []
    tin: list[str] = []
    khai = so_khai.get("plugin", {})

    chua_xac_nhan = 0
    for khoa, m in sorted(khai.items()):
        can = m.get("can_o_may") or []
        co = khoa in hien and hien[khoa]["bat"]
        chac = bool(m.get("da_xac_nhan"))
        if not chac:
            chua_xac_nhan += 1
        if may in can and not co:
            if khoa in hien and hien[khoa]["khai_tat_ro"]:
                loi = (f"{khoa}: sổ khai nói CẦN ở {may} nhưng enabledPlugins đang "
                       f"ghi rõ false — sổ khai và cấu hình máy MÂU THUẪN")
            else:
                loi = (f"{khoa}: sổ khai nói CẦN ở {may} nhưng kho KHÔNG có — "
                       f"trôi dạt, cần cài lại (lý do khai: {m.get('ly_do', '?')})")
            # Ô «cần ở máy nào» chưa được bác sĩ xác nhận thì nó mới chỉ là SUY từ
            # hiện trạng lúc dựng sổ. Báo đỏ dựa trên một suy đoán là biến CHƯA BIẾT
            # thành CÓ VẤN ĐỀ — đúng bài học BH08, và bức tường đỏ giả sẽ dạy người
            # ta bỏ qua cả cảnh báo thật.
            (do if chac else vang).append(loi if chac else loi + " [sổ khai CHƯA xác nhận]")
        elif may not in can and co:
            vang.append(f"{khoa}: có trên {may} nhưng sổ khai không đòi — "
                        f"bổ sung vào sổ nếu đây là chủ ý")
    if chua_xac_nhan:
        tin.append(f"{chua_xac_nhan}/{len(khai)} mục trong sổ khai CHƯA xác nhận "
                   f"(`da_xac_nhan: false`) — đang suy từ hiện trạng lúc dựng sổ, "
                   f"nên chỉ cảnh báo chứ không báo đỏ. Xác nhận xong thì chúng "
                   f"thành cổng thật.")

    for khoa in sorted(set(hien) - set(khai)):
        vang.append(f"{khoa}: CHƯA có trong sổ khai — máy kia sẽ không biết plugin này tồn tại")

    for khoa, m in sorted(hien.items()):
        if m["bat"] and not m["ton_tai"]:
            do.append(f"{khoa}: ĐƯỜNG DẪN TREO — {m['duong_dan']} không tồn tại "
                      f"(đúng kiểu hỏng làm 12 plugin biến mất im lặng 05/08)")

    thieu_may = [k for k, m in sorted(khai.items())
                 if may in (m.get("can_o_may") or []) and len(m.get("can_o_may") or []) == 1]
    if thieu_may:
        tin.append(f"{len(thieu_may)} plugin cố ý CHỈ có ở {may} — không phải thiếu ở máy kia")
    return do, vang, tin


def chieu_codex(hien: dict, so_khai: dict, ap_dung: bool) -> tuple[list[str], list[str]]:
    """Nối skill của plugin ĐƯỢC KHAI sang ~/.codex/skills.

    Codex không có trình quản lý plugin — `~/.codex/skills` là đường DUY NHẤT nó
    thấy được năng lực của một plugin Claude. Chỉ chiếu plugin mà sổ khai bật
    `chieu_sang_codex`; mặc định tắt để không đổ cả kho vào Codex.

    Tên đích mang tiền tố plugin (`<plugin>__<skill>`) để hai plugin có skill trùng
    tên không đè nhau — và để nhìn tên là biết skill đến từ đâu.
    """
    lam: list[str] = []
    loi: list[str] = []
    khai = so_khai.get("plugin", {})
    for khoa, m in sorted(khai.items()):
        if not m.get("chieu_sang_codex"):
            continue
        trang_thai = hien.get(khoa)
        if not trang_thai or not trang_thai["ton_tai"]:
            loi.append(f"{khoa}: sổ khai đòi chiếu sang Codex nhưng plugin không có trên máy này")
            continue
        goc = Path(trang_thai["duong_dan"])
        ten_plugin = khoa.split("@")[0]
        for thu_muc, _d, fs in os.walk(goc):
            if "SKILL.md" not in fs:
                continue
            nguon = Path(thu_muc)
            dich = CODEX_SKILLS / f"{ten_plugin}__{nguon.name}"
            if LK.la_lien_ket(dich):
                if LK.tro_dung(dich, nguon):
                    continue
                loi.append(f"{dich.name}: {LK.kieu()} đang trỏ nơi khác — không đè")
                continue
            if dich.exists():
                loi.append(f"{dich.name}: đang là thư mục thật trong ~/.codex/skills — "
                           f"không đè, bác sĩ tự xử lý")
                continue
            if not ap_dung:
                lam.append(f"{dich.name} (sẽ nối)")
                continue
            try:
                LK.tao(nguon, dich)
                lam.append(dich.name)
            except OSError as exc:
                loi.append(f"{dich.name}: {exc}")
    return lam, loi


def main() -> int:
    ap = argparse.ArgumentParser(description="Đối chiếu kho plugin giữa 2 máy và với Codex")
    ap.add_argument("--ap-dung", action="store_true",
                    help="nối skill sang ~/.codex/skills cho plugin đã khai chieu_sang_codex")
    ap.add_argument("--tao-so-khai", action="store_true",
                    help="dựng/làm mới khung sync/plugin-manifest.json từ dữ liệu ĐO ĐƯỢC")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có vấn đề (dùng cho hook)")
    ap.add_argument("--json", action="store_true", help="xuất JSON máy đọc")
    args = ap.parse_args()

    may = ten_may()
    hien = quet_claude()

    if args.tao_so_khai:
        so = tao_so_khai(hien, may)
        SO_KHAI.parent.mkdir(parents=True, exist_ok=True)
        SO_KHAI.write_text(json.dumps(so, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
        print(f"✓ Đã dựng sổ khai: {len(so['plugin'])} plugin → {SO_KHAI}")
        print("  Mở file và điền ô `ly_do` còn nhãn [CẦN BÁC SĨ] — đó là phần máy không đoán được.")
        return 0

    so_khai = doc_json(SO_KHAI)
    if not so_khai:
        print("⚠ Chưa có sync/plugin-manifest.json — chạy `--tao-so-khai` một lần để dựng.",
              file=sys.stderr)
        return 1

    do, vang, tin = doi_chieu(hien, so_khai, may)
    lam, loi_codex = chieu_codex(hien, so_khai, args.ap_dung)
    do.extend(loi_codex)
    verdict = "🔴" if do else ("🟡" if vang else "🟢")

    if args.json:
        print(json.dumps({"may": may, "verdict": verdict, "loi_do": do, "canh_bao": vang,
                          "thong_tin": tin, "codex": lam, "plugin": hien},
                         ensure_ascii=False, indent=2))
        return 2 if do else (1 if vang else 0)

    if args.im_khi_on and verdict == "🟢":
        return 0

    bat = [k for k, v in hien.items() if v["bat"]]
    print(f"{verdict} KHO PLUGIN ({may}): {len(bat)} plugin đang bật, "
          f"{sum(hien[k]['so_skill'] for k in bat)} skill trên đĩa")
    for nhan, muc, dau in (("🔴 TRÔI DẠT / MÂU THUẪN SỔ KHAI", do, "•"),
                           ("🟡 Cần để ý", vang, "•"),
                           ("ℹ Ghi chú", tin, "·")):
        if muc:
            print(f"\n{nhan}:")
            for x in muc:
                print(f"   {dau} {x}")
    if lam:
        print(f"\n▸ Codex ({LK.kieu()}): {len(lam)} skill "
              f"{'đã nối' if args.ap_dung else 'sẽ nối — thêm --ap-dung'}")
    if verdict == "🟢" and not lam:
        print("   Khớp sổ khai. (Chỉ nói về kho TRÊN ĐĨA — không khẳng định thay "
              "Claude Code là mọi skill đều được chào ra cho model.)")
    return 2 if do else (1 if vang else 0)


if __name__ == "__main__":
    raise SystemExit(main())
