#!/usr/bin/env python3
"""run_orchestrator.py — CLI cho Orchestrator EBM (chế độ dry-run/plan mặc định).

Dùng:
  python tools/run_orchestrator.py "Tôi có bệnh nhân nam 68 tuổi ĐTĐ2 + eGFR 40, thêm thuốc gì?"
  python tools/run_orchestrator.py "Đề tài hiệu quả metformin ở PCOS ngoại trú"
  python tools/run_orchestrator.py "Đơn này an toàn không, thuốc có đánh nhau không?"
  python tools/run_orchestrator.py --capabilities        # in 7 năng lực + số liệu
  python tools/run_orchestrator.py --plugins             # tóm tắt registry quyền sở hữu plugin
  python tools/run_orchestrator.py --resolve-capability research_lifecycle
  python tools/run_orchestrator.py --validate            # tự kiểm điều phối ⇄ registry
  python tools/run_orchestrator.py --resume <session_id> # khôi phục một phiên
  python tools/run_orchestrator.py --list                # liệt kê phiên đã lưu
  thêm --json để in máy đọc.

Mã thoát = mã hợp đồng DỪNG (0 released · 1 returned · 2 gate_pending · 3 blocked · 4 unknown).
"Cần bác sĩ kiểm chứng." — orchestrator chỉ ĐỀ XUẤT + dừng ở cổng bác sĩ duyệt.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Cho phép `import orchestrator` khi chạy từ bất kỳ thư mục nào
sys.path.insert(0, str(Path(__file__).resolve().parent))

from orchestrator.context import ContextStore  # noqa: E402
from orchestrator.orchestrator import Orchestrator  # noqa: E402

# Ép stdout/stderr UTF-8 an toàn (kể cả Python cũ hơn không có PYTHONUTF8=1) — vá crash
# UnicodeEncodeError THẬT đã tái hiện trên Windows khi console dùng codepage không phải UTF-8
# (vd cp1252/cp437) và output có tiếng Việt có dấu/ký hiệu (─, ⛔, ✓…).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

BAR = "─" * 68


def _print_session(session, orch) -> None:
    it = session.intent
    print("═" * 68)
    print("  ORCHESTRATOR EBM · dry-run/plan")
    print("═" * 68)
    print(f"  Request : {session.request[:90]}")
    print(f"  Intent  : {it.get('kind')} → `{it.get('target')}`")
    print(f"            {it.get('reason')}")
    if it.get("matches"):
        print(f"  Khớp lẻ : {', '.join(it['matches'][:4])}")
    pr = session.plugin_routing or {}
    owner = pr.get("owner") or {}
    if owner.get("unit"):
        print(f"  Owner   : `{owner['unit']}` ({pr.get('capability')})")
        workers = [f"{w['provider']}:{w['unit']}" for w in pr.get("workers", [])]
        print(f"  Plugin  : {', '.join(workers) if workers else '(không dùng; agent nội bộ xử lý)'}")
    print(BAR)
    print("  KẾ HOẠCH ĐIỀU PHỐI (bước · agent · công cụ · cổng; ○=nhánh không áp dụng):")
    last_step = None
    n_skipped = 0
    for e in session.trace:
        if e["step"] != last_step:
            last_step = e["step"]
            gate = f"  ⛔ CỔNG {e['gate']}" if e.get("gate") else ""
            print(f"  ┌ [{e['step']}] {e['title']}{gate}")
        tools = f"  ⚙ {', '.join(e['tool_calls'])}" if e.get("tool_calls") else ""
        flag = {"planned": "✓", "error": "✗", "skipped": "○"}.get(e["status"], "•")
        cond = f"  [nhánh: {e['condition']}]" if e.get("condition") else ""
        if e["status"] == "skipped":
            n_skipped += 1
        print(f"  │   {flag} {e['agent']} — {e['summary'][:70]}{tools}{cond}")
    if n_skipped:
        print(f"  ({n_skipped} agent nhánh bỏ qua — không phát hiện tín hiệu tương ứng trong request)")
    print(BAR)
    if session.gates_pending:
        print(f"  🔒 DỪNG chờ bác sĩ ở cổng: {', '.join(session.gates_pending)}")
    lc = next((c["lifecycle"] for c in session.checkpoints if "lifecycle" in c), {})
    print(f"  Vòng đời: {' → '.join(lc.get('history', []))}")
    print(f"  KẾT: {session.status}  (mã thoát {session.exit_code})")
    print(f"  Phiên đã lưu: {session.session_id}")
    if it.get("kind") == "research_topic":
        print(BAR)
        print("  ℹ Đây là KẾ HOẠCH (dry-run) — chưa chạy thật. Để tự động chạy THẬT chuỗi")
        print("    G0→G10 (PubMed thật, tính cỡ mẫu, checkpoint, freshness guard, dừng")
        print("    đúng cổng chờ bác sĩ), dùng orchestrator SẢN XUẤT của dự án nghiên cứu:")
        print('    python medical-ebm-automation/tools/run_pipeline.py --study "<MÃ>" \\')
        print('           --topic "<chủ đề>"')
    print("  → Cần bác sĩ kiểm chứng.")
    print("═" * 68)


def main() -> int:
    ap = argparse.ArgumentParser(description="Orchestrator EBM (dry-run)")
    ap.add_argument("request", nargs="?", default="", help="Câu yêu cầu (ca / đề tài / câu hỏi)")
    ap.add_argument("--json", action="store_true", help="In JSON máy đọc")
    ap.add_argument("--capabilities", action="store_true", help="In 7 năng lực")
    ap.add_argument("--plugins", action="store_true", help="In tóm tắt registry quyền sở hữu plugin")
    ap.add_argument("--resolve-capability", metavar="ID",
                    help="Phân giải owner/worker cho một capability")
    ap.add_argument("--worker", action="append", default=None,
                    help="Giới hạn worker muốn dùng; lặp cờ để yêu cầu nhiều worker")
    ap.add_argument("--validate", action="store_true", help="Tự kiểm điều phối ⇄ registry")
    ap.add_argument("--resume", metavar="ID", help="Khôi phục một phiên")
    ap.add_argument("--list", action="store_true", help="Liệt kê phiên đã lưu")
    ap.add_argument("--gate-output", metavar="FILE",
                    help="Chấm output THẬT (.md) qua cổng rule-based → cắt bản ghi APPRAISAL "
                         "+ re-route nếu TRẢ-VỀ-SỬA (D1+D3 operational, không cần LLM)")
    args = ap.parse_args()

    orch = Orchestrator()

    if args.capabilities:
        caps = orch.capabilities()
        print(json.dumps(caps, ensure_ascii=False, indent=2) if args.json
              else "\n".join(f"  {k}: {v}" for k, v in caps.items()))
        return 0

    if args.plugins:
        summary = orch.plugin_ownership.summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json
              else "\n".join(f"  {key}: {value}" for key, value in summary.items()))
        return 0

    if args.resolve_capability:
        decision = orch.plugin_ownership.resolve(args.resolve_capability, args.worker)
        data = decision.as_dict()
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            owner = data["owner"]
            print(f"Capability: {data['capability']} · risk={data['risk']} · {data['status']}")
            print(f"Owner: {owner['provider']}:{owner['unit']}")
            for worker in data["workers"]:
                print(f"Worker: {worker['provider']}:{worker['unit']} · {worker['mode']}")
            if data["blocked_requests"]:
                print("Bị chặn: " + ", ".join(data["blocked_requests"]))
        return 0 if not decision.status.startswith("BLOCKED") and not decision.blocked_requests else 1

    if args.validate:
        warns = orch.validate()
        if args.json:
            print(json.dumps({"ok": not warns, "warnings": warns}, ensure_ascii=False, indent=2))
        else:
            print("✅ Điều phối ⇄ registry SẠCH — không tham chiếu treo." if not warns
                  else "⚠ CẢNH BÁO:\n" + "\n".join("  - " + w for w in warns))
        return 0 if not warns else 1

    if args.list:
        ids = ContextStore().list_ids()
        print(json.dumps(ids, ensure_ascii=False, indent=2) if args.json else "\n".join(ids) or "(chưa có phiên)")
        return 0

    if args.resume:
        s = orch.resume(args.resume)
        if s is None:
            print(f"Không tìm thấy phiên: {args.resume}")
            return 4
        if args.json:
            print(json.dumps(s.as_dict(), ensure_ascii=False, indent=2))
        else:
            _print_session(s, orch)
        return s.exit_code

    if not args.request:
        ap.print_help()
        return 4

    # D1+D3 operational: nếu có --gate-output, chấm nội dung THẬT bằng cổng rule-based →
    # cắt bản ghi APPRAISAL bền + re-route thật khi TRẢ-VỀ-SỬA (không cần LLM).
    verdict_fn = None
    if args.gate_output:
        gp = Path(args.gate_output)
        if not gp.exists():
            print(f"Không thấy file --gate-output: {args.gate_output}")
            return 4
        from datetime import datetime
        from orchestrator.guardrail_bridge import make_run_eval_verdict
        verdict_fn = make_run_eval_verdict(
            gp.read_text(encoding="utf-8", errors="ignore"),
            target=args.gate_output, source="orchestrator",
            at=datetime.now().isoformat(timespec="seconds"))

    session = orch.handle(args.request, guardrail_verdict=verdict_fn)
    if args.json:
        print(json.dumps(session.as_dict(), ensure_ascii=False, indent=2))
    else:
        _print_session(session, orch)
    return session.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
