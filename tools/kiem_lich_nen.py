#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CẢM BIẾN NGƯỜI CHẾT cho lịch nền — mỗi KỲ lịch phải để lại dấu vết đầu ra (T2-01/T2-04, 20/09/2026).

Vì sao có (đo 20/09/2026): 3/4 tác vụ nền bị XOÁ khỏi bộ lập lịch từ 07/09 và kỳ thứ Hai 14/09 không nổ, nhưng
mọi cảm biến đều im: `giac_quan_lich_nen` chỉ so «ngày PASS cuối» trong log thu thập — lượt chạy TAY 16/09 làm PASS
cuối mới hơn kỳ lỡ nên kỳ lỡ vô hình; `kiem_do_tuoi_chung_cu` in «🟢 còn hoạt động» theo tuổi dashboard; ESD05 chấm
PASS chỉ vì tệp `SKILL.md` tồn tại (tệp vẫn còn sau khi tác vụ bị xoá). Phải kiểm toán tay mới thấy.

Nguyên tắc: (1) tính THEO TỪNG KỲ — dựng danh sách lần nổ kỳ vọng từ cron rồi tìm dấu vết ĐỦ GẦN kỳ đó; một lượt chạy
tay chen giữa KHÔNG xoá dấu vết «kỳ không nổ đúng hẹn»; (2) dấu vết đọc THỜI ĐIỂM GHI TRONG NỘI DUNG (dòng KẾT THÚC,
tên tệp theo tuần ISO), không dùng mtime (OneDrive/chạy tay làm mtime tươi giả); (3) thiếu nguyên liệu (bản sao git
trần: không có log/queue) ⇒ ⚪ không đo được, KHÔNG đỏ (BH08); (4) CHỈ ĐO và BÁO — không tự tạo/xoá tác vụ.

Sổ khai kỳ vọng: `sync/lich-nen-ky-vong.json` (đi qua git). Python không gọi được MCP `scheduled-tasks`, nên đây là
đo GIÁN TIẾP qua đầu ra; muốn biết chắc trạng thái bộ lập lịch, phiên Claude gọi `list_scheduled_tasks`.

Mức: 🔴 (0) kỳ gần nhất LỠ hẳn (không dấu vết) · 🟠 (1) chỉ có lượt trễ/chạy bù ngoài hạn (lịch không nổ đúng hẹn)
· 🟡 (2) kỳ cũ hơn đã lỡ nhưng kỳ sau đã chạy lại (còn trong cửa sổ).
Mã thoát: 0 = mọi kỳ đến hạn đều có dấu vết đúng hẹn · 1 = có 🔴/🟠.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
SO_KHAI = GOC / "sync" / "lich-nen-ky-vong.json"


def _tap(f: str, lo: int, hi: int) -> set[int]:
    if f == "*":
        return set(range(lo, hi + 1))
    return {int(x) for x in f.split(",")}


def cac_ky(cron: str, tu: dt.date, den: dt.date) -> list[dt.datetime]:
    """Các lần nổ kỳ vọng của `cron` (5 trường; hỗ trợ `*`, số, danh sách) trong [tu, den]. dow: 0/7=CN, 1=T2."""
    ph, gio, dom, thang, dow = cron.split()
    f_ph, f_gio = int(ph), int(gio)
    s_dom, s_thang = _tap(dom, 1, 31), _tap(thang, 1, 12)
    s_dow = {x % 7 for x in _tap(dow, 0, 7)}
    ra: list[dt.datetime] = []
    d = tu
    while d <= den:
        thu_cron = (d.weekday() + 1) % 7  # T2=1 … CN=0
        ok_dom, ok_dow = d.day in s_dom, thu_cron in s_dow
        # cron chuẩn: cả dom lẫn dow bị hạn chế ⇒ khớp MỘT trong hai; ngược lại phải khớp cả hai (phần `*` luôn đúng)
        ngay_ok = (ok_dom or ok_dow) if (dom != "*" and dow != "*") else (ok_dom and ok_dow)
        if d.month in s_thang and ngay_ok:
            ra.append(dt.datetime(d.year, d.month, d.day, f_gio, f_ph))
        d += dt.timedelta(days=1)
    return ra


def _ket_thuc(duong: Path) -> list[dt.datetime] | None:
    """Thời điểm các dòng `===== YYYY-MM-DD HH:MM:SS : KẾT THÚC …` trong log; None = không đọc được."""
    try:
        van = duong.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return [dt.datetime.strptime(f"{a} {b}", "%Y-%m-%d %H:%M:%S")
            for a, b in re.findall(r"=+ (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) : KẾT THÚC", van)]


def kiem(hom_nay: dt.datetime | None = None, so_khai: dict | None = None, goc: Path = GOC) -> dict:
    """Trả {'phat_hien': [{id, ky, muc, uu, thong_diep}], 'khong_do_duoc': [...], 'ok': n}. Thuần đọc."""
    bay_gio = hom_nay or dt.datetime.now()
    if so_khai is None:
        try:
            so_khai = json.loads(SO_KHAI.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"phat_hien": [], "khong_do_duoc": ["thiếu/hỏng sync/lich-nen-ky-vong.json — không có gì để đối chiếu"],
                    "ok": 0}
    cua_so = dt.timedelta(days=int(so_khai.get("cua_so_ngay", 21)))
    ra: dict = {"phat_hien": [], "khong_do_duoc": [], "ok": 0}
    for tv in so_khai.get("tac_vu", []):
        dv = tv.get("dau_vet", {})
        loai = dv.get("loai")
        tu = max(dt.date.fromisoformat(tv["tu_ngay"]), (bay_gio - cua_so).date())
        grace = dt.timedelta(hours=int(tv.get("grace_gio", 30)))
        cac = [s for s in cac_ky(tv["cron"], tu, bay_gio.date()) if s + grace <= bay_gio]
        if not cac:
            continue
        if loai == "khong-co" or loai is None:
            ra["khong_do_duoc"].append(f"{tv['id']}: chưa khai dấu vết máy-đọc-được — không canh được")
            continue
        ket: list[dt.datetime] | None = None
        if loai == "log-ket-thuc":
            ket = _ket_thuc(goc / dv["path"])
            if ket is None:
                ra["khong_do_duoc"].append(f"{tv['id']}: không đọc được {dv['path']} (bản sao trần/máy khác)")
                continue
        elif loai == "file-tuan-iso":
            if not (goc / Path(dv["path"]).parent).exists():
                ra["khong_do_duoc"].append(f"{tv['id']}: thư mục {Path(dv['path']).parent}/ vắng mặt (bản sao trần)")
                continue
        else:
            ra["khong_do_duoc"].append(f"{tv['id']}: loại dấu vết «{loai}» không hỗ trợ")
            continue
        thieu: list[tuple[dt.datetime, str, str]] = []  # (kỳ, mức, mô tả)
        for i, s in enumerate(cac):
            ky_sau = cac_ky(tv["cron"], s.date() + dt.timedelta(days=1), s.date() + dt.timedelta(days=400))
            han_tre = ky_sau[0] if ky_sau else s + dt.timedelta(days=400)
            if loai == "log-ket-thuc":
                dung_han = [e for e in ket if s <= e <= s + grace]
                tre = [e for e in ket if s + grace < e < han_tre]
                if dung_han:
                    continue
                thieu.append((s, "tre" if tre else "lo",
                              f"có lượt chạy TRỄ {tre[0]:%d/%m %H:%M} (ngoài hạn {tv.get('grace_gio', 30)}h) — lịch không nổ "
                              "đúng hẹn, lượt sau là chạy tay/bù" if tre else "KHÔNG có dấu vết nào"))
            else:
                iso = s.isocalendar()
                f = goc / dv["path"].format(iso_nam=iso[0], iso_tuan=iso[1])
                if f.exists():
                    continue
                thieu.append((s, "lo", f"thiếu {f.relative_to(goc)}"))
        if not thieu:
            ra["ok"] += 1
            continue
        moi_nhat_hong = thieu[-1][0] == cac[-1]
        for s, muc, mo_ta in thieu:
            uu = (0 if muc == "lo" else 1) if (s == cac[-1] and moi_nhat_hong) else 2
            ra["phat_hien"].append({
                "id": tv["id"], "ky": s.strftime("%Y-%m-%d %H:%M"), "muc": muc, "uu": uu,
                "thong_diep": f"«{tv['id']}» kỳ {s:%d/%m/%Y %H:%M}: {mo_ta}"})
    return ra


def main() -> int:
    ap = argparse.ArgumentParser(description="Cảm biến người chết cho lịch nền")
    ap.add_argument("--im-khi-on", action="store_true", help="không in gì khi mọi kỳ đến hạn đều có dấu vết")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    kq = kiem()
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=2))
    hong = [p for p in kq["phat_hien"] if p["uu"] <= 1]
    if a.json:
        return 1 if hong else 0
    if not kq["phat_hien"]:
        if not a.im_khi_on:
            print(f"🟢 Mọi kỳ lịch nền đến hạn đều có dấu vết đúng hẹn ({kq['ok']} tác vụ có dấu vết).")
            for x in kq["khong_do_duoc"]:
                print(f"   ⚪ {x}")
        return 0
    print("🔴 LỊCH NỀN CÓ KỲ KHÔNG NỔ ĐÚNG HẸN" if hong else "🟡 Lịch nền: có kỳ cũ đã lỡ (kỳ sau đã chạy lại)")
    for p in sorted(kq["phat_hien"], key=lambda x: (x["uu"], x["ky"])):
        print(f"   {'🔴' if p['uu'] == 0 else '🟠' if p['uu'] == 1 else '🟡'} {p['thong_diep']}")
    print("   → phiên Claude: gọi list_scheduled_tasks + list_task_runs (tác vụ bị xoá/tắt?), rồi «Run now» hoặc "
          "bash medical-ebm-automation/scripts/weekly_safety.sh để bù. Máy KHÔNG tự tạo/xoá tác vụ.")
    for x in kq["khong_do_duoc"]:
        print(f"   ⚪ {x}")
    return 1 if hong else 0


if __name__ == "__main__":
    raise SystemExit(main())
