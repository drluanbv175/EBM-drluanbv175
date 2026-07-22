#!/usr/bin/env python3
"""Cấy cổng guardrail bắt buộc vào mọi agent nguồn Claude.

Nguồn biên tập chính là `.claude/agents/*.md`; sau khi chạy script này cần chạy:
  python3 tools/sync_agents_to_codex.py
  python3 tools/sync_agents_to_codex.py --check

Script chỉ chèn block chuẩn nếu file agent chưa có marker, không đụng tài liệu hạ tầng `_*.md`.
Dùng `--refresh` để CẬP NHẬT block đã cấy trước đó về đúng nội dung BLOCK hiện tại (khớp
chính xác OLD_BLOCK_V1 cũ mới thay — không đụng file nào đã bị sửa tay khác bản gốc).
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
MARKER = "<!-- EBM-MANDATORY-FINAL-GUARDRAIL -->"

# SỬA 2026-07-22 (vòng lặp kiểm tra-hoàn thiện vòng 7, phát hiện LOW): dòng
# "Lớp 2 CHẤT LƯỢNG Med-PaLM Q1-Q7 cho gói lâm sàng" trước đây được cấy Y HỆT
# vào MỌI agent không phân biệt lâm sàng/nghiên cứu — tự mâu thuẫn với các
# agent thuần nghiên cứu tự khai "Lớp 2 N/A cho gói NGHIÊN CỨU" ngay trong
# thân bài (vd dieu-phoi-nghien-cuu.md, phan-tich-thong-ke.md, co-mau-nghien-
# cuu.md, viet-ban-thao.md). Đổi câu này thành ĐIỀU KIỆN tự nhất quán — không
# còn khẳng định trơn "cho gói lâm sàng" mà nêu rõ N/A cho gói thuần nghiên
# cứu, để không mâu thuẫn với bất kỳ agent nào cấy vào.
OLD_BLOCK_LOP2_LINE = (
    "   - Lớp 2 CHẤT LƯỢNG Med-PaLM Q1-Q7 cho gói lâm sàng: dễ đọc, đúng đắn, đầy đủ-an toàn,\n"
    "     không thiên kiến, không gây hại, cập nhật, nguồn có thẩm quyền.\n"
)
NEW_BLOCK_LOP2_LINE = (
    "   - Lớp 2 CHẤT LƯỢNG Med-PaLM Q1-Q7: áp dụng khi gói CÓ yếu tố lâm sàng (khuyến cáo\n"
    "     điều trị/an toàn thuốc cho bệnh nhân cụ thể) — dễ đọc, đúng đắn, đầy đủ-an toàn,\n"
    "     không thiên kiến, không gây hại, cập nhật, nguồn có thẩm quyền. N/A cho gói THUẦN\n"
    "     nghiên cứu/thống kê (dùng chuẩn báo cáo CONSORT/STROBE/PRISMA + completeness-critic\n"
    "     A1-A18 thay thế).\n"
)

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
{NEW_BLOCK_LOP2_LINE}2. Nếu còn lỗi đỏ, thiếu nguồn, nghi sai guideline, thiếu cảnh báo nguy cơ hại, hoặc có PII:
   không phát hành như khuyến cáo; trả về dạng `[CẦN BÁC SĨ PHÁN ĐỊNH]` / `[CẦN KIỂM CHỨNG]`.
3. Kết thúc mọi đầu ra y khoa bằng: "Cần bác sĩ kiểm chứng."
"""


def is_agent(path: Path) -> bool:
    return path.suffix == ".md" and path.name != "README.md" and not path.name.startswith("_")


def _refresh(path: Path) -> bool:
    """Thay ĐÚNG dòng Lớp 2 cũ bằng bản mới trong file ĐÃ có marker — bỏ qua
    im lặng nếu không khớp chính xác (file có thể đã bị sửa tay khác bản gốc,
    KHÔNG ép ghi đè)."""
    text = path.read_text(encoding="utf-8")
    if MARKER not in text or OLD_BLOCK_LOP2_LINE not in text:
        return False
    path.write_text(text.replace(OLD_BLOCK_LOP2_LINE, NEW_BLOCK_LOP2_LINE), encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true",
                         help="Cập nhật dòng Lớp 2 đã cấy trước đó về bản mới (khớp chính xác, không ép ghi đè).")
    args = parser.parse_args()

    if args.refresh:
        refreshed: list[Path] = []
        for path in sorted(AGENTS.glob("*.md")):
            if not is_agent(path):
                continue
            if _refresh(path):
                refreshed.append(path)
        print("Agent guardrail refresh: done")
        print(f"- refreshed files: {len(refreshed)}")
        for path in refreshed:
            print(f"  {path.relative_to(ROOT)}")
        return 0

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
