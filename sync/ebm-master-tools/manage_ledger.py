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
  python3 tools/manage_ledger.py drop-nhieu ID [ID...]  # loại NHIỀU thẻ, MỘT lần ghi + MỘT bản sao lưu
  python3 tools/manage_ledger.py drop-nhieu --tu-bao-cao AUDITS/THE-TRUNG-HUB_<ngày>.json --cum 1,3|all
        # chạy khô mặc định; thêm --ap-dung --ly-do "<lời duyệt nguyên văn của bác sĩ>" để ghi
  python3 tools/manage_ledger.py regen                 # sinh lại EBM_WEBAPP.html từ sổ cái

NGUỒN CHUẨN (18/10/2026): tệp này sống trong git ở sync/ebm-master-tools/ của repo gốc; bản chạy
EBM_MASTER/tools/ được chép bằng tools/dong_bo_cong_cu_hub.py — KHÔNG sửa thẳng bản chạy.
"""
import contextlib
import datetime
import os
import sys
import json
import shutil
import unicodedata

# EBM_MASTER_HUB_DIR: thư mục hub khác (kiểm thử). Mặc định: thư mục cha của tools/.
HUB = os.environ.get("EBM_MASTER_HUB_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


# ---------------------------------------------------------------------------------------------
# LOẠI NHIỀU THẺ MỘT LẦN (thêm 18/10/2026)
# ---------------------------------------------------------------------------------------------
# VÌ SAO: `drop <ID>` sao lưu TRỌN sổ cái (~4,8 MB đo 18/10/2026) cho MỖI thẻ. Báo cáo
# tools/liet_ke_the_trung_hub.py (18/10/2026) có 193 thẻ trùng cần loại ⇒ 193 bản sao ≈ 0,9 GB
# thêm vào BACKUPS/ trên OneDrive (từng có sự cố OneDrive kẹt vòng lặp log/đầy đĩa). drop-nhieu
# loại cả lô trong MỘT lần ghi với MỘT bản sao lưu.
# AN TOÀN: chạy khô mặc định; --ap-dung bắt buộc --ly-do (lời duyệt nguyên văn của bác sĩ — máy
# KHÔNG tự loại thẻ); có lỗi nào là KHÔNG loại gì cả (fail-closed cho cả lô). Chế độ báo cáo kiểm
# LẠI từng cụm trên sổ cái SỐNG: báo cáo là ảnh chụp, sổ cái có thể đã đổi (nạp nối tiếp, phiên
# khác) — thẻ bị loại phải VẪN trùng khoá + tiêu đề và cùng decision với thẻ giữ.


def _chuan_tieu_de(s):
    """Cùng chuẩn hoá với tools/liet_ke_the_trung_hub.py::chuan_tieu_de (NFC, không phân biệt
    hoa/thường, gộp khoảng trắng) — luật gom cụm của báo cáo."""
    return " ".join(unicodedata.normalize("NFC", str(s or "")).casefold().split())


def _key_of():
    """key_of của CHÍNH cầu nạp (cùng thư mục) — không chép luật chống trùng sang đây."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    from ingest_dashboard import key_of
    return key_of


def _chon_cum(n_cum, cum_chon):
    """Danh sách số cụm (1-based) từ '1,3,5' / 'all'; chuỗi lỗi nếu không hợp lệ."""
    if cum_chon.strip().lower() == "all":
        return list(range(1, n_cum + 1)), ""
    try:
        so = [int(x) for x in cum_chon.split(",") if x.strip()]
    except ValueError:
        return [], "--cum phải là danh sách số cụm cách nhau bởi dấu phẩy hoặc 'all' (nhận «%s»)" % cum_chon
    if not so:
        return [], "--cum rỗng"
    sai = [x for x in so if not 1 <= x <= n_cum]
    if sai:
        return [], "cụm %s nằm ngoài báo cáo (có %d cụm)" % (", ".join(map(str, sai)), n_cum)
    return list(dict.fromkeys(so)), ""


def chon_tu_bao_cao(data, bao_cao, cum_chon):
    """→ (ids cần loại, dòng giải thích, lỗi[]) cho các cụm đã chọn của báo cáo THE-TRUNG-HUB_*.json."""
    ds = bao_cao.get("cum") or []
    chi_so, loi_cum = _chon_cum(len(ds), cum_chon)
    if loi_cum:
        return [], [], [loi_cum]
    key_of = _key_of()
    by_id = {c.get("id"): c for c in data.get("evidence_cards") or []}
    ids, giai_thich, loi = [], [], []
    for i in chi_so:
        cum = ds[i - 1]
        giu = cum.get("giu")
        if not giu or cum.get("can_bac_si"):
            loi.append("cụm %d: báo cáo KHÔNG đề xuất thẻ giữ (%s) — bác sĩ chọn rồi loại theo ID"
                       % (i, cum.get("ly_do") or "—"))
            continue
        the_giu = by_id.get(giu)
        if the_giu is None:
            loi.append("cụm %d: thẻ giữ %s không còn trong sổ cái — lập lại báo cáo" % (i, giu))
            continue
        loai_cum = []
        for cid in cum.get("loai") or []:
            c = by_id.get(cid)
            if c is None:
                loi.append("cụm %d: %s không còn trong sổ cái — lập lại báo cáo" % (i, cid))
            elif cid == giu:
                loi.append("cụm %d: %s vừa là thẻ giữ vừa nằm trong danh sách loại" % (i, cid))
            elif (key_of(c) != key_of(the_giu)
                  or _chuan_tieu_de(c.get("topic")) != _chuan_tieu_de(the_giu.get("topic"))):
                loi.append("cụm %d: %s KHÔNG còn trùng khoá + tiêu đề với thẻ giữ %s (sổ cái đã đổi "
                           "sau báo cáo) — lập lại báo cáo" % (i, cid, giu))
            elif c.get("decision") != the_giu.get("decision"):
                loi.append("cụm %d: %s khác decision với thẻ giữ %s (%s ≠ %s) — bác sĩ quyết"
                           % (i, cid, giu, c.get("decision"), the_giu.get("decision")))
            else:
                loai_cum.append(cid)
        ids += loai_cum
        giai_thich.append("cụm %d «%s»: giữ %s, loại %s"
                          % (i, (the_giu.get("topic") or "")[:60], giu, ", ".join(loai_cum) or "—"))
    return ids, giai_thich, loi


@contextlib.contextmanager
def _khoa_so_cai():
    """Khoá ghi sổ cái của sync_all.py (best-effort, như ingest_dashboard). Hub khác (kiểm thử)
    hoặc tiến trình cha đã giữ khoá ⇒ không khoá."""
    cm = None
    if not os.environ.get("EBM_MASTER_HUB_DIR") and os.environ.get("EBM_MASTER_LEDGER_LOCK_HELD") != "1":
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            if here not in sys.path:
                sys.path.insert(0, here)
            from sync_all import ledger_lock
            cm = ledger_lock()
        except Exception:  # noqa: BLE001 — thiếu sync_all/fcntl ⇒ chạy không khoá như drop cũ
            cm = None
    if cm is None:
        yield
    else:
        with cm:
            yield


def cmd_drop_nhieu(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="manage_ledger.py drop-nhieu",
                                 description="Loại NHIỀU thẻ trong MỘT lần ghi với MỘT bản sao lưu")
    ap.add_argument("ids", nargs="*", metavar="EVID-ID")
    ap.add_argument("--tu-bao-cao", default="", metavar="THE-TRUNG-HUB_*.json",
                    help="báo cáo của tools/liet_ke_the_trung_hub.py")
    ap.add_argument("--cum", default="", help="số cụm (vd 1,3,5) hoặc all — bắt buộc với --tu-bao-cao")
    ap.add_argument("--ly-do", default="", help="lời duyệt NGUYÊN VĂN của bác sĩ (bắt buộc khi --ap-dung)")
    ap.add_argument("--ap-dung", action="store_true", help="ghi thật (mặc định chạy khô)")
    a = ap.parse_args(argv)
    if bool(a.ids) == bool(a.tu_bao_cao):
        print("⛔ Chọn MỘT trong hai: danh sách ID, hoặc --tu-bao-cao <json> --cum <số|all>.")
        return 2
    if a.tu_bao_cao and not a.cum.strip():
        print("⛔ --cum bắt buộc với --tu-bao-cao (không ngầm định 'all' — bác sĩ chọn cụm đã duyệt).")
        return 2
    if a.ap_dung and not a.ly_do.strip():
        print("⛔ --ap-dung cần --ly-do \"<lời duyệt nguyên văn của bác sĩ>\" — máy không tự loại thẻ.")
        return 2
    bao_cao = None
    if a.tu_bao_cao:
        try:
            bao_cao = json.load(open(a.tu_bao_cao, encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print("⛔ Không đọc được báo cáo %s: %s" % (a.tu_bao_cao, exc))
            return 2

    def lap_ke_hoach(data):
        if bao_cao is not None:
            return chon_tu_bao_cao(data, bao_cao, a.cum)
        ids, loi = [], []
        for x in dict.fromkeys(i.strip() for i in a.ids):
            c = find(data, x)
            if c is None:
                loi.append("không thấy thẻ %s" % x)
            elif c["id"] not in ids:
                ids.append(c["id"])
        return ids, [], loi

    data = load()
    ids, giai_thich, loi = lap_ke_hoach(data)
    print("LOẠI NHIỀU THẺ — %d thẻ (một lần ghi, MỘT bản sao lưu khi --ap-dung):" % len(ids))
    for dong in giai_thich:
        print("  " + dong)
    for cid in ids:
        print(row(find(data, cid)))
    if loi:
        print("⛔ KHÔNG loại thẻ nào — sửa %d lỗi sau rồi chạy lại:" % len(loi))
        for dong in loi:
            print("   • " + dong)
        return 2
    if not ids:
        print("  Không có thẻ nào để loại.")
        return 0
    if not a.ap_dung:
        print("  (CHẠY KHÔ — chưa ghi gì. Bác sĩ xem danh sách trên rồi chạy lại kèm "
              "--ap-dung --ly-do \"<lời duyệt nguyên văn>\".)")
        return 0
    with _khoa_so_cai():
        data = load()                       # đọc LẠI trong khoá: phiên khác có thể vừa ghi sổ cái
        ids2, _gt, loi2 = lap_ke_hoach(data)
        if loi2 or ids2 != ids:
            print("⛔ Sổ cái đã đổi giữa lúc lập kế hoạch và lúc ghi — KHÔNG loại thẻ nào; chạy lại.")
            return 2
        bo = set(ids)
        data["evidence_cards"] = [c for c in data["evidence_cards"] if c["id"] not in bo]
        backup_and_save(data, "drop-nhieu-%d" % len(ids))
    print("  ✓ Đã loại %d thẻ trong MỘT lần ghi (một bản sao lưu trong BACKUPS/). Lý do: %s"
          % (len(ids), a.ly_do.strip()))
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        from audit_log import append as _log_append
        _log_append(
            HUB,
            event_type="LEDGER_DROP_BATCH",
            actor="manage_ledger.py drop-nhieu (bác sĩ duyệt)",
            description="Loại %d thẻ: %s. Lý do (nguyên văn): %s" % (len(ids), ", ".join(ids), a.ly_do.strip()),
            affected_files=["EBM_MASTER.json"],
            source_files_modified=[os.path.basename(a.tu_bao_cao)] if a.tu_bao_cao else [],
            pii_present=False,
            notes="Một bản sao lưu trước ghi trong BACKUPS/ (EBM_MASTER_manage_*_drop-nhieu-%d.json)." % len(ids),
            session_id="",
        )
    except Exception as exc:  # noqa: BLE001 — log lỗi không được chặn kết quả
        print("  ⚠ Không ghi được AUDIT_LOG.jsonl (%s)." % exc)
    return 0


def set_field(data, cid, field, value, label):
    c = find(data, cid)
    if not c:
        print("Không thấy thẻ", cid); return False
    old = c.get(field)
    c[field] = value
    # 27/10/2026: ngày của lần SỬA, không phải `meta.last_updated` (ngày nạp gần nhất của sổ) — đổi quyết định 27/10 từng ghi
    # lịch sử «2026-10-26».
    c.setdefault("history", []).append({"date": datetime.date.today().isoformat(),
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

    if cmd == "drop-nhieu":
        return cmd_drop_nhieu(args)
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
