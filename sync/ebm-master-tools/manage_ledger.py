#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manage_ledger.py — BẢNG ĐIỀU KHIỂN quản lý sổ cái EBM_MASTER ngay trong Claude.

Dùng để bác sĩ XEM · TÌM · LỌC · THỐNG KÊ và DUYỆT các cập nhật đã lưu, không cần mở file tay.
Mọi thao tác SỬA đều BACKUP sổ cái trước + ghi history (append-only, không mất dấu).

Cách dùng (chạy trong thư mục EBM_MASTER/):
  python3 tools/manage_ledger.py stats                 # tổng quan: đếm theo quyết định/nguồn/trạng thái
  python3 tools/manage_ledger.py queue                 # HÀNG ĐỢI DUYỆT: thẻ "chưa xác minh" (từ engine)
  python3 tools/manage_ledger.py list [N]              # N thẻ mới nhất (mặc định 20)
  python3 tools/manage_ledger.py search <từ khóa>      # tìm theo chủ đề/chuyên khoa/nguồn/PMID
  python3 tools/manage_ledger.py show <EVID-ID>        # xem chi tiết 1 thẻ
  python3 tools/manage_ledger.py approve <ID> [ID...]  # đánh dấu "đã xác minh" (bác sĩ đã đối chiếu nguồn)
  python3 tools/manage_ledger.py apply <ID>            # nâng quyết định → "áp dụng" (sau khi duyệt)
  python3 tools/manage_ledger.py consider <ID>         # đổi quyết định → "cân nhắc"
  python3 tools/manage_ledger.py notyet <ID>           # đổi quyết định → "chưa áp dụng"
  python3 tools/manage_ledger.py drop <ID> [lý do]     # loại bỏ 1 thẻ (vd nhiễu từ engine), có backup
  python3 tools/manage_ledger.py regen                 # sinh lại EBM_WEBAPP.html từ sổ cái
"""
import os
import sys
import json
import shutil

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(HUB, "EBM_MASTER.json")

DEC_VI = {"apply": "ÁP DỤNG", "consider": "Cân nhắc", "notyet": "Chưa áp dụng"}


def load():
    return json.load(open(MASTER, encoding="utf-8"))


def backup_and_save(data, tag):
    bdir = os.path.join(HUB, "BACKUPS")
    os.makedirs(bdir, exist_ok=True)
    n = len([f for f in os.listdir(bdir) if f.startswith("EBM_MASTER_")])
    shutil.copy(MASTER, os.path.join(bdir, "EBM_MASTER_manage_%03d_%s.json" % (n + 1, tag)))
    data["meta"]["counts"]["evidence_cards"] = len(data["evidence_cards"])
    json.dump(data, open(MASTER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def find(data, cid):
    for c in data["evidence_cards"]:
        if c["id"].lower() == cid.lower():
            return c
    return None


def row(c):
    st = "⚠" if "chưa" in (c.get("verification_status") or "") else "✓"
    return "  %-16s [%s] %-11s %-16s %s" % (
        c["id"], st, DEC_VI.get(c.get("decision"), c.get("decision", "")),
        (c.get("specialty") or "")[:16], (c.get("topic") or "")[:52])


def cmd_stats(data):
    from collections import Counter
    c = data["evidence_cards"]
    print("SỔ CÁI EBM_MASTER — tổng %d thẻ (cập nhật %s)" % (len(c), data["meta"].get("last_updated", "?")))
    print("  Quyết định :", {DEC_VI.get(k, k): v for k, v in Counter(x.get("decision") for x in c).items()})
    print("  Xác minh   :", dict(Counter(x.get("verification_status") for x in c)))
    print("  Nguồn gốc  :", dict(Counter(x.get("provenance") for x in c)))
    print("  Chuyên khoa:", dict(Counter((x.get("specialty") or "(trống)") for x in c).most_common(8)))
    nq = sum(1 for x in c if "chưa" in (x.get("verification_status") or ""))
    print("  → %d thẻ CHỜ DUYỆT (xem: queue)" % nq)


def cmd_queue(data):
    q = [c for c in data["evidence_cards"] if "chưa" in (c.get("verification_status") or "")]
    print("HÀNG ĐỢI DUYỆT — %d thẻ chưa xác minh (bác sĩ đối chiếu nguồn rồi 'approve'):" % len(q))
    for c in q[:40]:
        print(row(c))
    if len(q) > 40:
        print("  … và %d thẻ nữa (dùng search để lọc)." % (len(q) - 40))


def cmd_list(data, n):
    cs = data["evidence_cards"][-n:][::-1]
    print("%d thẻ mới nhất:" % len(cs))
    for c in cs:
        print(row(c))


def cmd_search(data, kw):
    kw = kw.lower()
    hits = [c for c in data["evidence_cards"] if kw in json.dumps(c, ensure_ascii=False).lower()]
    print("Tìm '%s' — %d kết quả:" % (kw, len(hits)))
    for c in hits[:40]:
        print(row(c))


def cmd_show(data, cid):
    c = find(data, cid)
    if not c:
        print("Không thấy thẻ", cid); return
    print("=" * 60)
    print(c["id"], "·", DEC_VI.get(c.get("decision")), "·", c.get("verification_status"), "·", c.get("provenance"))
    print("Chủ đề   :", c.get("topic"))
    print("Chuyên khoa:", c.get("specialty"), "| GRADE:", c.get("gradeLevel"))
    s = c.get("source", {})
    print("Nguồn    :", s.get("agency"), "| PMID", s.get("pmid"), "| DOI", s.get("doi"))
    p = c.get("pico", {})
    print("PICO     :", c.get("pico_question"))
    print("  P:", p.get("population"), "| I:", p.get("intervention"), "| C:", p.get("comparison"), "| O:", p.get("outcome"))
    print("Khuyến cáo:", c.get("recommendation"))
    print("Bối cảnh VN:", c.get("vietnam_context"))
    print("Tham khảo :", "; ".join(c.get("references", [])))
    print("Lịch sử  :", c.get("history"))


DEC_ICON = {"apply": "🟢 Áp dụng", "consider": "🟠 Cân nhắc", "notyet": "🔵 Chưa áp dụng"}
DEC_ORDER = ["apply", "consider", "notyet"]


def cmd_tree(data):
    """Sinh DANH MỤC dạng cây: Chuyên khoa → Quyết định → từng thẻ. In ra + ghi DANH_MUC.md."""
    cards = data["evidence_cards"]
    # gom theo chuyên khoa
    by_spec = {}
    for c in cards:
        by_spec.setdefault(c.get("specialty") or "(Chưa phân loại)", []).append(c)
    specs = sorted(by_spec, key=lambda s: (-len(by_spec[s]), s))

    lines = [
        "# 📚 DANH MỤC CẬP NHẬT EBM — cây thư mục",
        "",
        "> Sổ cái EBM_MASTER · tổng **%d thẻ** · cập nhật %s" % (len(cards), data["meta"].get("last_updated", "?")),
        "> Cấu trúc: **Chuyên khoa → Quyết định → thẻ**. ✓ = đã xác minh · ⚠ = chờ bác sĩ duyệt.",
        "> Sinh lại: `python3 tools/manage_ledger.py tree`. Quản lý từng thẻ: `show/approve/apply/drop`.",
        "",
    ]
    for s in specs:
        cs = by_spec[s]
        lines.append("## 📁 %s  (%d)" % (s, len(cs)))
        by_dec = {}
        for c in cs:
            by_dec.setdefault(c.get("decision") or "notyet", []).append(c)
        for d in DEC_ORDER:
            if d not in by_dec:
                continue
            lines.append("  - **%s** (%d)" % (DEC_ICON.get(d, d), len(by_dec[d])))
            for c in sorted(by_dec[d], key=lambda x: x["id"]):
                mark = "✓" if "chưa" not in (c.get("verification_status") or "") else "⚠"
                src = c.get("source", {})
                ref = ("PMID %s" % src["pmid"]) if src.get("pmid") else (("DOI %s" % src["doi"]) if src.get("doi") else "—")
                lines.append("      - %s `%s` %s  ·  %s" % (mark, c["id"], (c.get("topic") or "")[:70], ref))
        lines.append("")
    out = "\n".join(lines)
    path = os.path.join(HUB, "DANH_MUC.md")
    open(path, "w", encoding="utf-8").write(out)
    # đồng thời sinh bản HTML tương tác (cây thu/mở được)
    try:
        import subprocess
        subprocess.run([sys.executable, os.path.join(HUB, "tools", "gen_catalog_html.py")],
                       cwd=HUB, capture_output=True, text=True)
        print("  + Bản HTML tương tác: DANH_MUC.html (mở bằng trình duyệt)")
    except Exception:
        pass
    # in bản rút gọn ra màn hình
    print("DANH MỤC (cây) — %d thẻ / %d chuyên khoa → đã ghi %s\n" % (len(cards), len(specs), path))
    for s in specs:
        cs = by_spec[s]
        nap = sum(1 for c in cs if c.get("decision") == "apply")
        nq = sum(1 for c in cs if "chưa" in (c.get("verification_status") or ""))
        print("  📁 %-26s %2d thẻ  (áp dụng %d · chờ duyệt %d)" % (s, len(cs), nap, nq))


def set_field(data, cid, field, value, label):
    c = find(data, cid)
    if not c:
        print("Không thấy thẻ", cid); return False
    old = c.get(field)
    c[field] = value
    c.setdefault("history", []).append({"date": data["meta"].get("last_updated", ""),
                                        "change": "%s: %s → %s (quản lý)" % (label, old, value)})
    print("  ✓ %s: %s — %s: %s → %s" % (c["id"], c.get("topic", "")[:40], label, old, value))
    return True


def main():
    # Chạy được trên console Windows mặc định (cp1252) — CLI này in tiếng Việt
    # có dấu; không reconfigure sẽ UnicodeEncodeError. Vô hại nếu đã UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (ValueError, OSError, AttributeError):
        pass
    if not os.path.exists(MASTER):
        print("Không thấy EBM_MASTER.json. Chạy trong thư mục EBM_MASTER/."); return 1
    if len(sys.argv) < 2:
        print(__doc__); return 0
    data = load()
    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "stats":
        cmd_stats(data)
    elif cmd == "queue":
        cmd_queue(data)
    elif cmd == "list":
        cmd_list(data, int(args[0]) if args else 20)
    elif cmd == "search" and args:
        cmd_search(data, " ".join(args))
    elif cmd == "show" and args:
        cmd_show(data, args[0])
    elif cmd == "approve" and args:
        ch = any(set_field(data, i, "verification_status", "đã xác minh", "Duyệt") for i in args)
        if ch:
            backup_and_save(data, "approve")
    elif cmd in ("apply", "consider", "notyet") and args:
        if set_field(data, args[0], "decision", cmd, "Quyết định"):
            backup_and_save(data, cmd)
    elif cmd == "drop" and args:
        c = find(data, args[0])
        if c:
            data["evidence_cards"] = [x for x in data["evidence_cards"] if x["id"] != c["id"]]
            backup_and_save(data, "drop")
            print("  ✓ Đã loại %s (%s). Lý do: %s" % (c["id"], c.get("topic", "")[:40], " ".join(args[1:]) or "—"))
        else:
            print("Không thấy thẻ", args[0])
    elif cmd in ("tree", "catalog", "danh-muc"):
        cmd_tree(data)
    elif cmd == "regen":
        import subprocess
        r = subprocess.run([sys.executable, os.path.join(HUB, "tools", "gen_webapp_html.py")],
                           cwd=HUB, capture_output=True, text=True)
        print(" ", r.stdout.strip() or r.stderr.strip())
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
