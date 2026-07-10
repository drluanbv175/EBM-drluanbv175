#!/usr/bin/env python3
"""Cấy cổng guardrail bắt buộc vào mọi agent nguồn Claude.

Nguồn biên tập chính là `.claude/agents/*.md`; sau khi chạy script này cần chạy:
  python3 tools/sync_agents_to_codex.py
  python3 tools/sync_agents_to_codex.py --check

Script chỉ chèn block chuẩn nếu file agent chưa có marker, không đụng tài liệu hạ tầng `_*.md`.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
MARKER = "<!-- EBM-MANDATORY-FINAL-GUARDRAIL -->"

BLOCK = f"""

{MARKER}
## Cổng bắt buộc trước khi trả lời

Trước mọi đầu ra cuối cùng có yếu tố lâm sàng, nghiên cứu y khoa, dashboard chứng cứ,
khuyến cáo điều trị, an toàn thuốc, thống kê y khoa hoặc tài liệu cho người bệnh:

1. Tự áp dụng guardrail `tham-dinh-dau-ra` theo 2 lớp:
   - Lớp 1 LIÊM CHÍNH R1-R7 (+ phụ lục R8 thống kê / R14 an toàn kê đơn khi áp dụng):
     nguồn PMID/DOI/URL, không PII, không vượt cổng bác sĩ duyệt,
     không tự gán GRADE khi nguồn không cấp, tách độ chắc chứng cứ với độ mạnh khuyến cáo,
     gắn nhãn `[CẦN...]` khi thiếu dữ liệu, có disclaimer. R14 HARD-RED khi gói CÓ
     khuyến cáo/điều chỉnh thuốc mà thiếu rà tương tác/CCĐ/chỉnh liều (2026-07-07).
   - Lớp 2 CHẤT LƯỢNG Med-PaLM Q1-Q7 cho gói lâm sàng: dễ đọc, đúng đắn, đầy đủ-an toàn,
     không thiên kiến, không gây hại, cập nhật, nguồn có thẩm quyền.
2. Nếu còn lỗi đỏ, thiếu nguồn, nghi sai guideline, thiếu cảnh báo nguy cơ hại, hoặc có PII:
   không phát hành như khuyến cáo; trả về dạng `[CẦN BÁC SĨ PHÁN ĐỊNH]` / `[CẦN KIỂM CHỨNG]`.
3. Kết thúc mọi đầu ra y khoa bằng: "Cần bác sĩ kiểm chứng."
"""


def is_agent(path: Path) -> bool:
    return path.suffix == ".md" and path.name != "README.md" and not path.name.startswith("_")


def main() -> int:
    changed: list[Path] = []
    for path in sorted(AGENTS.glob("*.md")):
        if not is_agent(path):
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        path.write_text(text.rstrip() + BLOCK + "\n", encoding="utf-8")
        changed.append(path)

    print("Agent guardrail enforcement: done")
    print(f"- checked agents: {len([p for p in AGENTS.glob('*.md') if is_agent(p)])}")
    print(f"- changed files: {len(changed)}")
    for path in changed:
        print(f"  {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
