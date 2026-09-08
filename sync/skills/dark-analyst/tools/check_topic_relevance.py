#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_topic_relevance.py — Kiểm mỗi item trong Web Dashboard EBM có THỰC SỰ thuộc chủ đề/
chuyên khoa đã khai báo hay không, bằng cách gọi Claude API chấm điểm.

BỐI CẢNH — lỗ hổng thật đã phát hiện: `verify_dashboard.py` (cổng liêm chính hiện có) chỉ xác
minh TÍNH TOÀN VẸN KỸ THUẬT (PMID có thật, đã dịch tiếng Việt, có disclaimer) — KHÔNG xác minh
NỘI DUNG mục có đúng thuộc chủ đề dashboard hay không. Dashboard "Tim mạch" từng lọt 8/20 mục
thực chất về sản khoa, nhi khoa, hô hấp, thận học — chỉ phát hiện được bằng cách ĐỌC TAY từng
mục, không có công cụ tự động nào bắt được. Module này lấp khoảng trống đó.

NGUYÊN TẮC AN TOÀN:
- CHỈ CẢNH BÁO, KHÔNG TỰ Ý XÓA/SỬA mục nào — phân loại LLM có sai số, quyết định cuối luôn
  thuộc về bác sĩ (giống mọi cổng khác trong hệ thống này).
- 3 mức phán quyết (in_topic/off_topic/uncertain) thay vì nhị phân — "uncertain" khi LLM không
  đủ tin cậy để kết luận, tránh ép buộc phân loại sai vào 1 trong 2 cực.
- Gộp TOÀN BỘ item của 1 dashboard vào MỘT lượt gọi API (batch) — vừa rẻ vừa tránh nhiễu ngữ
  cảnh khi chấm từng item riêng lẻ (mất khả năng so sánh chéo giữa các mục).
- Không có ANTHROPIC_API_KEY -> bỏ qua ÊM (status='skipped'), KHÔNG chặn pipeline hiện có
  (đúng khuôn mẫu claude_llm() trong app/integrations/ambient_scribe.py).

Cách dùng:
    python3 check_topic_relevance.py <dashboard.html>
    python3 check_topic_relevance.py <dashboard.html> --json   # in JSON thô để tool khác đọc
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_dashboard import extract_data_block, field, split_items  # noqa: E402

# Windows: stdout mặc định là cp1252 → mọi print() tiếng Việt hoặc ký hiệu (✓ ⚠ →)
# ném UnicodeEncodeError và GIẾT tiến trình, thường SAU KHI công việc đã xong.
# Vá 14/08/2026: hai tool này bị bỏ sót vì chốt BH11 cũ chỉ liệt cứng 4 tên tool.
import sys as _sys_utf8
for _s in (_sys_utf8.stdout, _sys_utf8.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

VALID_VERDICTS = {"in_topic", "off_topic", "uncertain"}


class TopicCheckError(Exception):
    pass


def _extract_meta_question(data_block: str) -> Optional[str]:
    """Lấy meta.question (câu hỏi/chủ đề khai báo của dashboard) từ khối DATA."""
    m = re.search(r"\bquestion\s*:\s*['\"]([^'\"]*)['\"]", data_block)
    return m.group(1) if m else None


def _items_for_prompt(data_block: str) -> List[Dict[str, str]]:
    """Trích (id, title, action) từng item — đủ ngữ cảnh để chấm chủ đề mà không cần toàn văn."""
    out = []
    for chunk in split_items(data_block):
        iid = field(chunk, "id")
        title = field(chunk, "title")
        action = field(chunk, "action")
        if iid and title:
            out.append({"id": iid, "title": title, "action": action or ""})
    return out


def build_prompt(dashboard_topic: str, items: List[Dict[str, str]]) -> str:
    lines = [
        "Bạn đang kiểm tra xem các mục chứng cứ y khoa dưới đây có THỰC SỰ thuộc "
        f"chủ đề/chuyên khoa đã khai báo của dashboard hay không.",
        "",
        f'Chủ đề dashboard đã khai báo: "{dashboard_topic}"',
        "",
        "Với MỖI mục, đánh giá theo đúng 1 trong 3 mức:",
        '- "in_topic": nội dung CHÍNH của bài liên quan trực tiếp đến chủ đề trên (kể cả '
        "khi có góc nhìn liên chuyên khoa thật sự, ví dụ bài về biến chứng tim mạch của "
        "bệnh thận vẫn tính in_topic cho chủ đề Tim mạch nếu nội dung THỰC SỰ bàn về mối "
        "liên hệ đó).",
        '- "off_topic": nội dung CHÍNH không liên quan đến chủ đề trên (ví dụ bài về thai '
        "kỳ/nhi khoa/hô hấp/phương pháp luận guideline nói chung xuất hiện trong dashboard "
        "Tim mạch mà không có liên hệ tim mạch rõ ràng trong nội dung).",
        '- "uncertain": tiêu đề/tóm tắt không đủ thông tin để kết luận chắc chắn.',
        "",
        "Các mục:",
    ]
    for it in items:
        extra = f" — {it['action']}" if it["action"] else ""
        lines.append(f"[{it['id']}] {it['title']}{extra}")
    lines += [
        "",
        "CHỈ trả lời bằng JSON hợp lệ theo đúng định dạng sau, không thêm chữ nào khác, "
        "không thêm markdown code fence:",
        '{"ITEM-01": {"verdict": "in_topic", "reason": "một câu ngắn giải thích"}, ...}',
    ]
    return "\n".join(lines)


def call_claude(prompt: str, *, model: Optional[str] = None, max_tokens: int = 2000) -> str:
    """Gọi Claude API. Đúng khuôn mẫu claude_llm() trong app/integrations/ambient_scribe.py."""
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise TopicCheckError(
            "Thiếu ANTHROPIC_API_KEY — đặt trong .env (ngoài OneDrive) để bật kiểm chủ đề."
        )
    try:
        import anthropic  # type: ignore
    except ImportError as exc:  # pragma: no cover - phụ thuộc môi trường
        raise TopicCheckError("Chưa cài SDK: `pip install anthropic`.") from exc
    mdl = model or os.getenv("TOPIC_CHECK_MODEL", "claude-sonnet-4-6")
    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(  # pragma: no cover - cần mạng + key
        model=mdl, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(getattr(b, "text", "") for b in resp.content)


def parse_verdicts(raw_response: str) -> Dict[str, Dict[str, str]]:
    """Parse JSON trả về từ model. Ném TopicCheckError nếu không phải JSON hợp lệ hoặc verdict
    lạ — KHÔNG đoán mò/tự sửa để tránh diễn giải sai ý model."""
    text = raw_response.strip()
    # Model đôi khi vẫn bọc ```json...``` dù đã dặn không làm vậy -> gỡ an toàn trước khi parse.
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TopicCheckError(f"Model không trả JSON hợp lệ: {exc}. Raw: {text[:200]}") from exc
    if not isinstance(parsed, dict):
        raise TopicCheckError(f"Model trả JSON không phải object: {type(parsed)}")
    for iid, v in parsed.items():
        if not isinstance(v, dict) or v.get("verdict") not in VALID_VERDICTS:
            raise TopicCheckError(f"Verdict không hợp lệ cho {iid}: {v!r}")
    return parsed


def check_dashboard_topic_relevance(html_path: str) -> Dict:
    """Điểm vào chính: đọc dashboard, gọi Claude chấm chủ đề, trả kết quả có cấu trúc.

    Trả về dict {"status": "ok"|"skipped"|"error", ...}. KHÔNG BAO GIỜ raise ra ngoài —
    lỗi/thiếu cấu hình đều trả về status rõ ràng để caller (vd verify_dashboard.py) tự quyết
    định có chặn hay chỉ cảnh báo.
    """
    html = Path(html_path).read_text(encoding="utf-8")
    data_block = extract_data_block(html)
    if not data_block:
        return {"status": "error", "message": "Không tìm thấy khối DATA."}

    topic = _extract_meta_question(data_block)
    if not topic:
        return {"status": "error", "message": "Không tìm thấy meta.question (chủ đề dashboard)."}

    items = _items_for_prompt(data_block)
    if not items:
        return {"status": "skipped", "message": "Không có item nào để chấm."}

    prompt = build_prompt(topic, items)
    try:
        raw = call_claude(prompt)
        verdicts = parse_verdicts(raw)
    except TopicCheckError as exc:
        return {"status": "skipped", "message": str(exc)}

    off_topic = [
        {"id": iid, "title": next((it["title"] for it in items if it["id"] == iid), ""),
         "reason": v.get("reason", "")}
        for iid, v in verdicts.items() if v.get("verdict") == "off_topic"
    ]
    uncertain = [iid for iid, v in verdicts.items() if v.get("verdict") == "uncertain"]

    return {
        "status": "ok",
        "topic": topic,
        "total_items": len(items),
        "off_topic": off_topic,
        "uncertain": uncertain,
        "verdicts": verdicts,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dashboard", help="Đường dẫn file dashboard .html")
    ap.add_argument("--json", action="store_true", help="In JSON thô thay vì báo cáo đọc được")
    args = ap.parse_args()

    result = check_dashboard_topic_relevance(args.dashboard)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] != "error" else 1

    print("================================================================")
    print("KIỂM ĐỘ LIÊN QUAN CHỦ ĐỀ — (bổ sung cho verify_dashboard.py)")
    print("================================================================")
    if result["status"] == "skipped":
        print(f"  ⏭  BỎ QUA: {result['message']}")
        return 0
    if result["status"] == "error":
        print(f"  ⛔ LỖI: {result['message']}")
        return 1

    print(f"  Chủ đề dashboard: {result['topic']}")
    print(f"  Tổng số mục đã chấm: {result['total_items']}")
    if result["off_topic"]:
        print(f"  ⚠ {len(result['off_topic'])} mục CÓ THỂ lạc chủ đề (bác sĩ rà lại, KHÔNG tự động gỡ):")
        for it in result["off_topic"]:
            print(f"     - [{it['id']}] {it['title'][:70]}")
            print(f"       Lý do model nêu: {it['reason']}")
    else:
        print("  ✓ Không mục nào bị nghi lạc chủ đề.")
    if result["uncertain"]:
        print(f"  ⚠ {len(result['uncertain'])} mục KHÔNG chắc chắn: {', '.join(result['uncertain'])}")
    print("----------------------------------------------------------------")
    print("LƯU Ý: đây là gợi ý từ LLM, có sai số — không thay thế thẩm định của bác sĩ.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
