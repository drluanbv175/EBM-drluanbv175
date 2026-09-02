#!/usr/bin/env python3
"""Canh các cờ TẮT của plugin trùng trong ~/.claude/settings.json — và khôi phục.

VÌ SAO CÓ CÔNG CỤ NÀY
---------------------
Bộ `medsci-skills` phát hành 9 plugin nhưng CÙNG một bộ skill byte-identical.
Bác sĩ đã chọn giữ đúng một bộ (`medsci-project`) và ghi RÕ `false` cho 8 bộ còn
lại. Đây là thứ duy nhất giữ danh sách skill khỏi phồng gấp rưỡi.

App Claude **ghi đè `settings.json`** sau một số đợt cập nhật và **xoá sạch các cờ
`false`** đó. Đã xảy ra hai lần trên máy Mac: 17/08/2026 (kho 839 → 1311 skill) và
21/08/2026 (870 → 1319). Cả hai lần đều phải sửa tay.

Nguy hiểm nằm ở chỗ chốt `kiem_plugin_day_du.py` nhìn hiện tượng này thành «plugin
MỚI so với mốc» và gợi ý `--ghi-moc`. Làm theo gợi ý đó sẽ **đóng băng chính chỗ
phồng vào mốc chuẩn**, và từ đó không chốt nào còn báo nữa — hỏng đúng cái giác
quan sinh ra để canh.

LUẬT NỀN, ĐỪNG ĐẢO
------------------
**Vắng mặt trong `enabledPlugins` nghĩa là BẬT, không phải tắt.** Ngày 11/08/2026
một lời khuyên sai ở CLAUDE.md bảo «gỡ hẳn khỏi enabledPlugins» đã khiến Claude
Code CÀI LẠI cả 8 bộ (278 MB). Nên công cụ này chỉ bao giờ GHI `false`, không xoá.

CÁCH XÁC ĐỊNH BỘ NÀO PHẢI TẮT
-----------------------------
Không viết cứng 8 cái tên. Đọc mốc chuẩn của CHÍNH máy này
(`tools/moc_chuan_plugin.json` — mỗi máy tự ghi riêng): trong một HỌ plugin cùng
marketplace, nếu mốc có giữ ít nhất một thành viên thì các thành viên KHÁC phải
`false`. Thành viên có trong mốc thì không bao giờ bị đụng tới.

Ranh giới: chỉ chạm `enabledPlugins`, không đổi khoá nào khác, luôn sao lưu trước
khi ghi, và không bao giờ đụng tới nội dung y khoa.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import sys
from pathlib import Path

import sys as _s_ds, pathlib as _p_ds
_s_ds.path.insert(0, str(_p_ds.Path(__file__).resolve().parents[0]))
from doc_settings import doc_settings as _doc_settings, duong_dan_ghi as _dd_ghi  # noqa: E402


# Windows mặc định stdout=cp1252 → mọi print() tiếng Việt làm script chết giữa
# chừng. Đúng lỗi đã giết 7 script trong tools/vietnamize/ ngày 03/08/2026, và
# công cụ này chạy trên CẢ HAI máy nên phải có. (Chốt đa nền R4 gắn cờ 21/08.)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
SETTINGS = Path.home() / ".claude" / "settings.json"
MOC = GOC / "tools" / "moc_chuan_plugin.json"


def _ho(ten: str) -> str:
    """Họ plugin = phần sau '@' (tên marketplace). 'medsci-data@medsci-skills' → 'medsci-skills'."""
    return ten.split("@", 1)[1] if "@" in ten else ""


def _ten_trong_moc() -> set[str]:
    """Tên plugin mà mốc chuẩn của MÁY NÀY đang giữ.

    Mốc có thể lồng theo tên máy hoặc phẳng — chấp nhận cả hai, và bỏ qua mọi khoá
    không phải tên plugin (tên plugin luôn có '@').
    """
    if not MOC.exists():
        return set()
    try:
        d = json.loads(MOC.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()

    ten: set[str] = set()

    def _quet(o: object) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, str) and "@" in k:
                    ten.add(k)
                _quet(v)
        elif isinstance(o, list):
            for v in o:
                _quet(v)

    _quet(d)
    return ten


def do() -> tuple[list[str], str]:
    """Trả (danh sách plugin ĐÁNG LẼ phải tắt mà đang bật, ghi chú)."""
    if not SETTINGS.exists() and not (SETTINGS.parent / "settings.local.json").exists():
        return [], f"không thấy {SETTINGS}"
    try:
        d = _doc_settings(nghiem=True, goc=SETTINGS)
    except (OSError, json.JSONDecodeError) as e:
        return [], f"đọc settings.json lỗi: {type(e).__name__}"

    ep = d.get("enabledPlugins")
    if not isinstance(ep, dict):
        return [], "settings.json không có enabledPlugins"

    giu = _ten_trong_moc()
    if not giu:
        return [], "chưa có mốc chuẩn — không suy đoán bộ nào nên tắt"

    ho_co_nguoi_giu = {_ho(t) for t in giu if _ho(t)}

    thieu_co = []
    for ten, bat in ep.items():
        if ten in giu:                       # mốc đang giữ → không bao giờ đụng
            continue
        if _ho(ten) not in ho_co_nguoi_giu:   # họ này mốc không giữ ai → không phải ca trùng
            continue
        if bat is False:                      # đã ghi rõ false → đúng rồi
            continue
        thieu_co.append(ten)                  # vắng mặt hoặc true đều là ĐANG BẬT

    return sorted(thieu_co), f"mốc giữ {len(giu)} plugin"


def sua(thieu_co: list[str]) -> str:
    """Ghi `false` cho các plugin trùng. Sao lưu trước. KHÔNG xoá khoá nào."""
    dau = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = SETTINGS.with_suffix(f".json.bak-{dau}-khoi-phuc-co-tat")
    shutil.copy2(SETTINGS, bak)

    d = _doc_settings(nghiem=True, goc=SETTINGS)
    for ten in thieu_co:
        d["enabledPlugins"][ten] = False      # GHI false, không del — vắng mặt = BẬT
    SETTINGS.write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return bak.name


def main() -> int:
    ap = argparse.ArgumentParser(description="Canh cờ TẮT của plugin trùng")
    ap.add_argument("--ap-dung", action="store_true", help="thật sự ghi lại cờ false")
    ap.add_argument("--im-khi-on", action="store_true", help="chỉ nói khi có vấn đề")
    a = ap.parse_args()

    thieu_co, ghi_chu = do()

    if not thieu_co:
        if not a.im_khi_on:
            print(f"🟢 Cờ tắt plugin trùng còn nguyên ({ghi_chu}).")
        return 0

    print(f"🔴 {len(thieu_co)} plugin TRÙNG đang BẬT — cờ `false` đã bị xoá khỏi settings.json")
    for t in thieu_co:
        print(f"   • {t}")
    print("\n   Đây là dấu hiệu app vừa ghi đè settings.json (đã xảy ra 17/08 và 21/08/2026).")
    print("   ⚠️ ĐỪNG chạy `--ghi-moc`: làm vậy sẽ đóng băng chỗ phồng vào mốc chuẩn,")
    print("      và từ đó không chốt nào còn báo nữa.")

    if not a.ap_dung:
        print("\n   (thêm --ap-dung để khôi phục)")
        return 2

    bak = sua(thieu_co)
    print(f"\n✓ Đã ghi lại `false` cho {len(thieu_co)} plugin. Sao lưu: {bak}")
    print("   Khởi động lại app để danh sách skill trở về đúng mốc.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
