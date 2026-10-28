#!/usr/bin/env python3
"""Hook UserPromptSubmit — nhắc ĐỊNH TUYẾN ngay khi bác sĩ gõ câu hỏi (28/10/2026, bác sĩ chọn «Một cửa vào»).

Vì sao có hook này: `tools/orchestrator/intent.py` có sẵn từ lâu nhưng KHÔNG ai gọi lúc bác sĩ gõ — model tự chọn skill theo
danh sách mô tả bị cắt còn 80 ký tự. Đo chiều 28/10: hai phiên hỏi «tiếp cận chẩn đoán điều trị … toàn diện dựa trên chứng cứ
mới nhất» rẽ sang skill tổng thuật (không dashboard, không cổng liêm chính, không bộ năm, không hub), một phiên trả lời thẳng từ
trí nhớ (tự bắt 3 trích dẫn sai). Hook đưa kết quả của bộ định tuyến vào ngữ cảnh lượt đó.

Chỉ nói khi câu là CHỦ ĐỀ chứng cứ hoặc CA lâm sàng; câu khác (gộp PR, «đã bấm G10», tin của agent…) ⇒ im lặng, không tốn
token. Mọi lỗi ⇒ im lặng và mã 0: hook nhắc không bao giờ được chặn lượt gõ của bác sĩ.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent

NHAC_CHU_DE = (
    "ĐỊNH TUYẾN (tools/orchestrator/intent.py, luật «một cửa vào» 28/10/2026): câu này là CHỦ ĐỀ CHỨNG CỨ ⇒ gọi Skill "
    "`cap-nhat-chung-cu-y-khoa` NGAY, chạy đúng dây chuyền CLAUDE.md §6.2: chủ đề đã có dashboard/watchlist ⇒ "
    "`ops/orchestrator.py --topic \"<chủ đề>\" --online` trước (dashboard mới thành bản nối tiếp); dashboard Evidence Workbench → "
    "`verify_dashboard.py` → `xuat_goi_cap_nhat.py <dashboard> --online` (bộ năm: toàn văn, EndNote, ⑨) → hub. "
    "KHÔNG trả lời từ trí nhớ. KHÔNG dùng `tong-thuat-chung-cu` làm cửa vào: bài đọc liền mạch chỉ dựng TỪ dashboard đã qua cổng "
    "(`tools/xuat_tong_thuat.py <TT>.md --dashboard <dashboard>`)."
)
NHAC_CA = (
    "ĐỊNH TUYẾN (tools/orchestrator/intent.py): câu có dấu hiệu CA lâm sàng ⇒ `dieu-phoi-lam-sang` (cờ đỏ nêu NGAY, 5 bước EBM, "
    "dừng ở Cổng A/B). Nếu thực ra là câu hỏi CHỦ ĐỀ chung (không phải một người bệnh cụ thể) ⇒ Skill `cap-nhat-chung-cu-y-khoa`. "
    "KHÔNG trả lời từ trí nhớ: mọi khẳng định y khoa phải có PMID/DOI đã tra và đã kiểm rút bài."
)


def loi_nhac(cau: str) -> str:
    """Trả lời nhắc cho một câu bác sĩ gõ, hoặc chuỗi rỗng khi không cần nhắc."""
    cau = (cau or "").strip()
    # «/lệnh» là bác sĩ đã chọn đường; «<…>» là tin hệ thống/agent khác, không phải câu hỏi của bác sĩ.
    if not cau or cau.startswith(("/", "<")):
        return ""
    if str(GOC) not in sys.path:
        sys.path.insert(0, str(GOC))
    from tools.orchestrator.intent import SKILL_CAP_NHAT_CHUNG_CU, route

    kq = route(cau)
    if kq.kind == "cong_cu" and kq.target == SKILL_CAP_NHAT_CHUNG_CU:
        return NHAC_CHU_DE
    if kq.kind == "clinical_case":
        return NHAC_CA
    return ""


def main() -> int:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        du_lieu = json.loads(sys.stdin.read() or "{}")
        nhac = loi_nhac(du_lieu.get("prompt", "") if isinstance(du_lieu, dict) else "")
        if nhac:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": nhac}},
                             ensure_ascii=False))
    except Exception:  # noqa: BLE001 — hook nhắc tuyệt đối không được chặn lượt gõ
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
