#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hard_gate_count_consistency.py — chặn TÁI DIỄN lớp lỗi "thêm 1 cổng cứng
mới, quên cập nhật hết doctrine mô tả nó" (tìm thấy 2026-07-15 qua audit đối
kháng: cổng G8 — bình duyệt độc lập — thêm 2026-07-14, nhưng 11 file
`.claude/agents/*.md` vẫn liệt kê cổng cứng KHÔNG có G8, 16+ ngày sau).

Nguồn sự thật DUY NHẤT: tools/gate_contract.py::_GATE_REQUIRED_STAKEHOLDERS (trong
medical-ebm-automation/) — tập gate_id có yêu cầu stakeholder cứng (hiện G2/G4/G8/G9).

Cơ chế: quét mọi dòng trong .claude/agents/*.md có nhắc "cổng cứng" VÀ nhắc ÍT NHẤT
2 gate_id trong bộ nguồn sự thật (dấu hiệu dòng đó đang LIỆT KÊ cổng cứng, không
phải chỉ nhắc 1 gate rời rạc) — nếu dòng đó KHÔNG nhắc ĐỦ mọi gate_id trong bộ
nguồn sự thật, coi là LỆCH, báo file+dòng+gate còn thiếu.

GIỚI HẠN THẬT (không giấu): đây là kiểm tra HEURISTIC trên văn bản tự do tiếng
Việt, không phải parser ngữ nghĩa — có thể có dương tính giả (dòng nhắc 2 gate vì
lý do khác, không phải đang liệt kê cổng cứng) hoặc âm tính giả (dòng liệt kê cổng
cứng nhưng viết theo cách công cụ chưa nhận ra, vd chỉ ghi SỐ LƯỢNG "5 cổng cứng"
mà không liệt kê từng mã G). Dùng như LƯỚI AN TOÀN bổ sung — không thay thế đọc kỹ
khi patch thêm/bớt cổng cứng.

Dùng:
    python3 tools/verify_hard_gate_count_consistency.py          # in báo cáo
    python3 tools/verify_hard_gate_count_consistency.py --check  # exit 1 nếu lệch (dùng cho CI)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / ".claude" / "agents"
GATE_CONTRACT_TOOLS_DIR = ROOT / "medical-ebm-automation" / "tools"

if str(GATE_CONTRACT_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(GATE_CONTRACT_TOOLS_DIR))
import gate_contract as GC  # noqa: E402

# Bộ gate_id NGUỒN SỰ THẬT — mọi dòng "liệt kê cổng cứng" phải nhắc ĐỦ bộ này.
GATE_SET = sorted(GC._GATE_REQUIRED_STAKEHOLDERS.keys())

_HARD_GATE_PHRASE = re.compile(r"cổng cứng|hard gate", re.IGNORECASE)


def _gates_mentioned_on_line(line: str) -> set[str]:
    return {g for g in GATE_SET if re.search(rf"\b{g}\b", line)}


def scan() -> list[dict]:
    """Trả danh sách {file, line_no, line, missing} cho mọi dòng lệch."""
    findings = []
    if not AGENTS_DIR.exists():
        return findings
    for path in sorted(AGENTS_DIR.glob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, start=1):
            if not _HARD_GATE_PHRASE.search(line):
                continue
            mentioned = _gates_mentioned_on_line(line)
            if len(mentioned) < 2:
                continue  # dòng chỉ nhắc 0-1 gate — không đủ dấu hiệu đang LIỆT KÊ
            missing = set(GATE_SET) - mentioned
            if missing:
                findings.append({
                    "file": str(path.relative_to(ROOT)),
                    "line_no": i,
                    "line": line.strip(),
                    "missing": sorted(missing),
                })
    return findings


def main() -> int:
    check_mode = "--check" in sys.argv
    findings = scan()
    print(f"Nguồn sự thật (gate_contract.py::_GATE_REQUIRED_STAKEHOLDERS): {GATE_SET}")
    print(f"Quét: {AGENTS_DIR} — {len(list(AGENTS_DIR.glob('*.md')))} file .md")
    if not findings:
        print("✅ Không tìm thấy dòng nào liệt kê cổng cứng mà thiếu gate.")
        return 0
    print(f"⚠️  {len(findings)} dòng LỆCH (liệt kê cổng cứng nhưng thiếu ít nhất 1 gate):\n")
    for f in findings:
        print(f"  {f['file']}:{f['line_no']} — thiếu {f['missing']}")
        print(f"    {f['line'][:160]}")
    if check_mode:
        print("\n✗ FAIL (--check): sửa các dòng trên trước khi coi doctrine đồng bộ với gate_contract.py.")
        return 1
    print("\n(Chạy lại với --check để dùng trong CI/pre-commit — exit 1 khi còn lệch.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
