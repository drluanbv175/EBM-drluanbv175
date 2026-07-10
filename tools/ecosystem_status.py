#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ecosystem_status.py — TỔNG HỢP TRẠNG THÁI HỆ SINH THÁI EBM (một cửa nhìn).

Đọc-CHỈ-đọc khắp các mặt của folder "Claude AI" (đội Agent · sổ cái chứng cứ ·
thương hiệu Dr Luân · dashboard · routine theo lịch) rồi kết xuất MỘT bức tranh
trạng thái. Không sửa gì trong hệ thống — chỉ sinh 2 tệp phái sinh ở gốc:
  • _trang-thai-he-sinh-thai.json  (máy đọc / lưu vết)
  • _trang-thai.js                 (window.EBM_STATUS = {...} cho bảng điều khiển HTML)
và in tóm tắt ra màn hình.

LỚP ĐIỀU HƯỚNG CỘNG THÊM — an toàn cho đồng bộ Mac↔Windows: chỉ tạo tệp mới,
không di chuyển/đổi tên/xóa; đường dẫn tương đối; chạy giống nhau trên 2 máy.

Chạy:  PYTHONUTF8=1 python3 tools/ecosystem_status.py
(Script tự ép stdout UTF-8 nên vẫn chạy đúng trên Windows nếu quên PYTHONUTF8.)
"""
from __future__ import annotations
import json
import sys
import re
from pathlib import Path
from datetime import datetime, timezone

# Ép UTF-8 để tiếng Việt không vỡ trên Windows (cp1252)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]  # gốc "Claude AI"


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def count_agents() -> dict:
    """Đếm agent thật (bỏ tệp meta _*.md và README)."""
    d = ROOT / ".claude" / "agents"
    if not d.is_dir():
        return {"total": 0, "meta_docs": 0}
    md = list(d.glob("*.md"))
    real = [f for f in md if not f.name.startswith("_") and f.name.lower() != "readme.md"]
    meta = [f for f in md if f.name.startswith("_") or f.name.lower() == "readme.md"]
    return {"total": len(real), "meta_docs": len(meta)}


def _load_ledger() -> dict | None:
    p = ROOT / "EBM_MASTER" / "EBM_MASTER.json"
    if not p.is_file():
        return None
    return _safe(lambda: json.loads(p.read_text(encoding="utf-8")))


# Tệp hàng chờ do cầu nối tự sinh — PHẢI bỏ qua khi quét PMID, nếu không sẽ tự
# đếm PMID ứng viên là "đã phủ" và làm thiếu số ứng viên.
BACKLOG_NAME = "_HANG-CHO-NOI-DUNG-TU-SO-CAI.md"


def _video_pmids() -> set[str]:
    """Mọi PMID đã xuất hiện trong kịch bản/hàng chờ thương hiệu (để chống trùng)."""
    pmids: set[str] = set()
    tk = ROOT / "EBM-TikTok"
    if not tk.is_dir():
        return pmids
    for f in tk.rglob("*.md"):
        if f.name == BACKLOG_NAME:  # đừng đọc chính đầu ra của cầu nối
            continue
        t = _safe(lambda: f.read_text(encoding="utf-8"), "") or ""
        for m in re.findall(r"PMID[:\s]*([0-9]{5,9})", t):
            pmids.add(m)
    return pmids


CHRONIC_HINTS = (
    "Tim mạch", "Nội tiết", "Thận", "Hô hấp", "Thần kinh", "Tiêu hóa",
    "Cơ xương khớp", "Lão khoa", "Tuân thủ", "Chăm sóc ban đầu",
)


def _is_verified(card: dict) -> bool:
    return str(card.get("verification_status", "")).strip().startswith("đã xác minh")


def _candidate(card: dict, video_pmids: set[str]) -> bool:
    """Thẻ chứng cứ ĐỦ ĐIỀU KIỆN thành ý tưởng nội dung công chúng (chất lượng cao).

    Cùng bộ lọc với EBM-TikTok/tools/goi-y-noi-dung-tu-so-cai.py để số liệu khớp.
    """
    src = card.get("source") or {}
    pmid = str(src.get("pmid") or "").strip()
    if not _is_verified(card):
        return False
    if not (pmid or str(src.get("doi") or "").strip()):
        return False
    if pmid and pmid in video_pmids:
        return False
    if card.get("decision") not in ("apply", "consider"):
        return False
    if card.get("gradeLevel") not in ("high", "mod"):
        return False
    rec = str(card.get("recommendation") or "").strip()
    if len(rec) < 40 or rec.startswith("("):  # cần khuyến cáo nguồn rõ
        return False
    if rec.lower() == str(card.get("topic") or "").strip().lower():
        return False  # chỉ lặp lại tiêu đề, không phải câu khuyến cáo thật
    sp = str(card.get("specialty", ""))
    return any(h in sp for h in CHRONIC_HINTS)


def summarize_ledger(ledger: dict | None) -> dict:
    if not ledger:
        return {"available": False}
    cards = ledger.get("evidence_cards") or []
    meta = ledger.get("meta") or {}
    vpm = _video_pmids()
    by_decision = {"apply": 0, "consider": 0, "notyet": 0}
    verified = with_pmid = with_doi = 0
    for c in cards:
        d = c.get("decision")
        if d in by_decision:
            by_decision[d] += 1
        if _is_verified(c):
            verified += 1
        src = c.get("source") or {}
        if str(src.get("pmid") or "").strip():
            with_pmid += 1
        if str(src.get("doi") or "").strip():
            with_doi += 1
    candidates = sum(1 for c in cards if _candidate(c, vpm))
    return {
        "available": True,
        "total_cards": len(cards),
        "verified": verified,
        "with_pmid": with_pmid,
        "with_doi": with_doi,
        "by_decision": by_decision,
        "content_candidates": candidates,
        "last_updated": meta.get("last_updated"),
        "last_backup": meta.get("last_backup"),
    }


def summarize_brand() -> dict:
    tk = ROOT / "EBM-TikTok"
    if not tk.is_dir():
        return {"available": False}
    verify_dir = tk / "_0_kich-ban-da-verify"
    verified_scripts = 0
    if verify_dir.is_dir():
        verified_scripts = sum(
            1 for sub in verify_dir.iterdir()
            if sub.is_dir() and (sub / "kich-ban.md").is_file()
        )

    def _n(name):
        d = tk / name
        return len([x for x in d.iterdir() if x.is_dir()]) if d.is_dir() else 0

    return {
        "available": True,
        "verified_scripts": verified_scripts,
        "queue_cho_duyet": _n("_1_cho_duyet"),
        "queue_da_duyet": _n("_2_da_duyet"),
        "queue_da_dang": _n("_3_da_dang"),
        "has_lead_magnet": (tk / "lead-magnet" / "cam-nang-7-lam-tuong.html").is_file(),
    }


def summarize_dashboards() -> dict:
    d = ROOT / "EBM-Dashboards"
    if not d.is_dir():
        return {"available": False}
    htmls = [f for f in d.glob("*.html")]
    lib = (d / "evidence-library.html").is_file()
    return {"available": True, "html_files": len(htmls), "has_library_index": lib}


def summarize_scheduled() -> dict:
    """Đếm routine THẬT — có SKILL.md (loại thư mục cấu hình ẩn như .claude,
    thư mục backup _*, và placeholder rỗng chưa có SKILL.md)."""
    d = ROOT / "Scheduled"
    if not d.is_dir():
        return {"available": False}
    routines = [
        x.name for x in d.iterdir()
        if x.is_dir() and not x.name.startswith(("_", ".")) and (x / "SKILL.md").is_file()
    ]
    return {"available": True, "routines": len(routines), "names": sorted(routines)}


def build_status() -> dict:
    ledger = _load_ledger()
    return {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        # KHÔNG nhúng đường dẫn tuyệt đối máy cụ thể ("root") — 2 file kết xuất
        # này nằm ở gốc OneDrive, sync cả 2 máy; path Windows/Mac khác nhau
        # gây khác biệt nội dung không cần thiết giữa các lần làm mới.
        "agents": count_agents(),
        "evidence": summarize_ledger(ledger),
        "brand": summarize_brand(),
        "dashboards": summarize_dashboards(),
        "scheduled": summarize_scheduled(),
    }


def render_text(s: dict) -> str:
    ag = s["agents"]
    ev = s["evidence"]
    br = s["brand"]
    db = s["dashboards"]
    sc = s["scheduled"]
    L = []
    L.append("╔══════════════════════════════════════════════════════════╗")
    L.append("║   TRẠNG THÁI HỆ SINH THÁI EBM — một cửa nhìn             ║")
    L.append("╚══════════════════════════════════════════════════════════╝")
    L.append(f"  Cập nhật: {s['generated_at']}")
    L.append(f"  🧠 Đội Agent      : {ag['total']} agent  (+{ag['meta_docs']} tài liệu chuẩn/meta)")
    if ev.get("available"):
        d = ev["by_decision"]
        L.append(f"  📚 Sổ cái chứng cứ: {ev['total_cards']} thẻ · {ev['verified']} đã xác minh · "
                 f"{ev['with_pmid']} có PMID · {ev['with_doi']} có DOI")
        L.append(f"       └ đề xuất: áp dụng {d['apply']} · cân nhắc {d['consider']} · chưa {d['notyet']}")
        L.append(f"       └ 🔗 ứng viên nội dung công chúng (chất lượng cao, chưa lên video): "
                 f"{ev['content_candidates']}")
    if br.get("available"):
        L.append(f"  🎬 Thương hiệu    : {br['verified_scripts']} kịch bản đã verify · "
                 f"chờ duyệt {br['queue_cho_duyet']} · đã duyệt {br['queue_da_duyet']} · "
                 f"đã đăng {br['queue_da_dang']}")
    if db.get("available"):
        L.append(f"  📊 Dashboard      : {db['html_files']} tệp"
                 + ("  (có chỉ mục thư viện)" if db.get("has_library_index") else ""))
    if sc.get("available"):
        L.append(f"  ⏱️  Routine lịch   : {sc['routines']} (chạy trên MỘT máy)")
    if ev.get("available"):
        L.append("")
        L.append(f"  ▶ Biến {ev['content_candidates']} chứng cứ thành ý tưởng nội dung an toàn:")
        L.append("    PYTHONUTF8=1 python3 EBM-TikTok/tools/goi-y-noi-dung-tu-so-cai.py")
    L.append("")
    L.append("  Bất biến: KHÔNG bịa · PMID/DOI · 'Cần bác sĩ kiểm chứng' · KHÔNG PII · bác sĩ duyệt.")
    return "\n".join(L)


def main() -> int:
    status = build_status()
    # JSON (máy đọc)
    (ROOT / "_trang-thai-he-sinh-thai.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # JS cho bảng điều khiển HTML (chạy được qua file://)
    js = "/* Tự sinh bởi tools/ecosystem_status.py — KHÔNG sửa tay */\n" \
         "window.EBM_STATUS = " + json.dumps(status, ensure_ascii=False) + ";\n"
    (ROOT / "_trang-thai.js").write_text(js, encoding="utf-8")
    # Tóm tắt màn hình
    print(render_text(status))
    print("\n  ✔ Đã ghi: _trang-thai-he-sinh-thai.json + _trang-thai.js (bảng điều khiển tự cập nhật).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
