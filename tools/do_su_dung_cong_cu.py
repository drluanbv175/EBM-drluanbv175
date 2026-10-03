#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SỔ ĐO SỬ DỤNG CÔNG CỤ DÀI HẠN — chỉ ĐẾM TÊN, không giữ nội dung hội thoại (Q7, kiểm toàn diện 02/10/2026).

VÌ SAO CÓ. Transcript phiên ở `~/.claude/projects` chỉ giữ ~26 ngày (cũ nhất 06/09 lúc đo 02/10; 586 tệp, 1,4 GB) nên mọi kết luận
«công cụ X không ai dùng» chỉ bảo đảm cho 26 ngày — công cụ dùng theo QUÝ (ACC/AHA, thang điểm) dễ bị coi nhầm là bỏ không. Công cụ này
chạy mỗi tháng, đếm số lần gọi theo TÊN (tool · skill · agent con · máy chủ MCP · mô hình) và ghi vào `state/su-dung-cong-cu-<YYYY-MM>.json`
(vài KB) — sau 2–3 tháng có bằng chứng dài hạn thật để quyết tắt/giữ.

    python3 tools/do_su_dung_cong_cu.py                  # tháng hiện tại, chỉ in
    python3 tools/do_su_dung_cong_cu.py --thang 2026-09 --ghi
    python3 tools/do_su_dung_cong_cu.py --tong-hop       # gộp mọi tháng đã ghi: tên nào 0 lượt qua ≥ 2 tháng

QUYỀN RIÊNG TƯ: chỉ đọc khoá `type`, `timestamp`, `sessionId`, `message.model`, `content[].name` và đúng hai trường tên trong `input`
(`skill` của Skill, `subagent_type` của Agent/Task); với tin nhắn người dùng chỉ TÊN lệnh `/…` trong thẻ <command-name>. KHÔNG
giữ lời nhắc, đầu ra công cụ, đường dẫn hay tham số nào khác. Ghi
theo TỪNG phiên (khoá = mã phiên) nên chạy lại không đếm trùng. Mã thoát 0 · 2 không đo được (thiếu thư mục transcript). Cần bác sĩ
kiểm chứng.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
GOC_TRANSCRIPT = Path.home() / ".claude" / "projects"
STATE = REPO / "state"
NHOM = ("tool", "skill", "lenh", "agent", "mcp", "model")


_RE_LENH = re.compile(r"<command-name>/?([\w:.-]{1,80})</command-name>")


def dem_mot_dong(d: dict, thang: str) -> tuple[str, Counter] | None:
    """(mã phiên, bộ đếm) của MỘT dòng transcript thuộc `thang`; None nếu không liên quan. Chỉ đọc các trường tên — với tin nhắn
    người dùng chỉ lấy TÊN lệnh gạch chéo trong thẻ <command-name>, không giữ chữ nào khác."""
    if not isinstance(d, dict) or not str(d.get("timestamp", "")).startswith(thang):
        return None
    m = d.get("message") if isinstance(d.get("message"), dict) else {}
    c: Counter = Counter()
    if d.get("type") == "user":
        noi = m.get("content")
        chu = noi if isinstance(noi, str) else " ".join(x.get("text", "") for x in (noi or []) if isinstance(x, dict))
        for ten in _RE_LENH.findall(chu or ""):
            c[f"lenh:{ten}"] += 1
        return (str(d.get("sessionId") or ""), c) if c else None
    if d.get("type") != "assistant":
        return None
    if m.get("model"):
        c[f"model:{m['model']}"] += 1
    for it in m.get("content") or []:
        if not isinstance(it, dict) or it.get("type") != "tool_use" or not it.get("name"):
            continue
        ten = str(it["name"])
        c[f"tool:{ten}"] += 1
        if ten.startswith("mcp__"):
            c[f"mcp:{ten.split('__')[1] if ten.count('__') >= 2 else ten}"] += 1
        inp = it.get("input") if isinstance(it.get("input"), dict) else {}
        if ten == "Skill" and inp.get("skill"):
            c[f"skill:{inp['skill']}"] += 1
        if ten in ("Agent", "Task"):
            c[f"agent:{inp.get('subagent_type') or 'general-purpose'}"] += 1
    return str(d.get("sessionId") or ""), c


def dem_thang(thang: str, goc: Path | None = None) -> dict[str, dict[str, int]]:
    """{mã phiên: {khoá: số lần}} cho mọi transcript (kể cả agent con) trong tháng."""
    goc = goc or GOC_TRANSCRIPT
    phien: dict[str, Counter] = {}
    for tep in goc.rglob("*.jsonl"):
        try:
            # Bỏ nhanh tệp không chạm tháng này theo mtime (tệp cũ hơn tháng ⇒ không có dòng của tháng).
            if date.fromtimestamp(tep.stat().st_mtime).strftime("%Y-%m") < thang:
                continue
            with open(tep, encoding="utf-8", errors="replace") as fh:
                for dong in fh:
                    if thang not in dong or ('"assistant"' not in dong and "<command-name>" not in dong):
                        continue
                    try:
                        kq = dem_mot_dong(json.loads(dong), thang)
                    except ValueError:
                        continue
                    if kq and kq[1]:
                        phien.setdefault(kq[0] or tep.stem, Counter()).update(kq[1])
        except OSError:
            continue
    return {k: dict(v) for k, v in phien.items()}


def tong(phien: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    t: Counter = Counter()
    for v in phien.values():
        t.update(v)
    ra: dict[str, dict[str, int]] = {n: {} for n in NHOM}
    for k, so in t.most_common():
        nhom, _, ten = k.partition(":")
        ra.setdefault(nhom, {})[ten] = so
    return ra


def ghi(thang: str, phien: dict, state: Path | None = None) -> Path:
    state = state or STATE
    tep = state / f"su-dung-cong-cu-{thang}.json"
    cu: dict = {}
    try:
        cu = json.loads(tep.read_text(encoding="utf-8")).get("phien", {})
    except (OSError, ValueError, AttributeError):
        cu = {}
    gop = {**cu, **phien}  # khoá theo phiên: chạy lại thay số của phiên đó, không cộng dồn
    state.mkdir(parents=True, exist_ok=True)
    tam = tep.with_name(tep.name + f".tam-{os.getpid()}")
    tam.write_text(json.dumps({"thang": thang, "so_phien": len(gop), "tong": tong(gop), "phien": gop}, ensure_ascii=False, indent=1)
                   + "\n", encoding="utf-8", newline="\n")
    os.replace(tam, tep)
    return tep


def tong_hop(state: Path | None = None) -> dict:
    """Gộp các tháng đã ghi: {nhom: {ten: {thang: so}}}."""
    state = state or STATE
    ra: dict = {}
    for tep in sorted(state.glob("su-dung-cong-cu-*.json")):
        try:
            d = json.loads(tep.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for nhom, bang in (d.get("tong") or {}).items():
            for ten, so in bang.items():
                ra.setdefault(nhom, {}).setdefault(ten, {})[d.get("thang", tep.stem[-7:])] = so
    return ra


def in_bang(t: dict, thang: str, so_phien: int) -> None:
    print(f"SỬ DỤNG CÔNG CỤ — tháng {thang}: {so_phien} phiên có lượt gọi")
    for nhom, nhan in (("lenh", "Lệnh gạch chéo"), ("skill", "Skill"), ("agent", "Agent con"), ("mcp", "Máy chủ MCP"), ("model", "Mô hình"), ("tool", "Tool")):
        bang = t.get(nhom) or {}
        if bang:
            dau = list(bang.items())[:12]
            print(f"  {nhan} ({len(bang)}): " + " · ".join(f"{k} {v}" for k, v in dau) + (" …" if len(bang) > 12 else ""))
    print("Chỉ đếm TÊN; không giữ nội dung hội thoại. Cần bác sĩ kiểm chứng.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sổ đo sử dụng công cụ dài hạn (chỉ đếm tên)")
    ap.add_argument("--thang", default=date.today().strftime("%Y-%m"), help="YYYY-MM (mặc định tháng hiện tại)")
    ap.add_argument("--ghi", action="store_true", help="ghi state/su-dung-cong-cu-<YYYY-MM>.json")
    ap.add_argument("--tong-hop", action="store_true", help="gộp mọi tháng đã ghi")
    ap.add_argument("--goc", type=Path, default=None, help="thư mục transcript (mặc định ~/.claude/projects)")
    a = ap.parse_args(argv)
    if a.tong_hop:
        th = tong_hop()
        if not th:
            print("⚪ chưa có tháng nào được ghi (state/su-dung-cong-cu-*.json)")
            return 2
        cac_thang = sorted({m for bang in th.values() for v in bang.values() for m in v})
        print(f"TỔNG HỢP {len(cac_thang)} tháng: {', '.join(cac_thang)}")
        for nhom in ("lenh", "skill", "agent", "mcp"):
            bang = th.get(nhom) or {}
            print(f"  {nhom}: {len(bang)} tên có lượt gọi")
        print("(Tên KHÔNG xuất hiện trong bảng = 0 lượt qua mọi tháng đã đo — đối chiếu danh mục công cụ trước khi quyết tắt.)")
        return 0
    goc = a.goc or GOC_TRANSCRIPT
    if not goc.is_dir():
        print(f"⚪ KHÔNG ĐO ĐƯỢC — không thấy thư mục transcript {goc}")
        return 2
    phien = dem_thang(a.thang, goc)
    in_bang(tong(phien), a.thang, len(phien))
    if a.ghi:
        print(f"✓ đã ghi {ghi(a.thang, phien)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
