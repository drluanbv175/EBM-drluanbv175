#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_hard_gate_count_consistency.py — chặn TÁI DIỄN lớp lỗi "thêm 1 cổng cứng
mới, quên cập nhật hết doctrine mô tả nó" (tìm thấy 2026-07-15 qua audit đối
kháng: cổng G8 — bình duyệt độc lập — thêm 2026-07-14, nhưng 11 file
`.claude/agents/*.md` vẫn liệt kê cổng cứng KHÔNG có G8, 16+ ngày sau).

Nguồn sự thật DUY NHẤT: tools/gate_contract.py::_GATE_REQUIRED_STAKEHOLDERS (trong
medical-ebm-automation/) — tập gate_id có yêu cầu stakeholder cứng (hiện
G2/G4/G5/G8/G9/G10).

Cơ chế: quét mọi dòng trong .claude/agents/*.md có nhắc "cổng cứng" (hoặc đồng
nghĩa — xem _HARD_GATE_PHRASE) VÀ nhắc ÍT NHẤT 2 gate_id trong bộ nguồn sự thật
(dấu hiệu dòng đó đang LIỆT KÊ cổng cứng, không phải chỉ nhắc 1 gate rời rạc) —
nếu dòng đó KHÔNG nhắc ĐỦ mọi gate_id trong bộ nguồn sự thật, coi là LỆCH, báo
file+dòng+gate còn thiếu.

GIỚI HẠN THẬT (không giấu): đây là kiểm tra HEURISTIC trên văn bản tự do tiếng
Việt, không phải parser ngữ nghĩa — có thể có dương tính giả (dòng nhắc 2 gate vì
lý do khác, không phải đang liệt kê cổng cứng) hoặc âm tính giả (dòng liệt kê cổng
cứng nhưng viết theo cách công cụ chưa nhận ra, vd chỉ ghi SỐ LƯỢNG "5 cổng cứng"
mà không liệt kê từng mã G, hoặc dùng một từ đồng nghĩa khác chưa có trong
_HARD_GATE_PHRASE — đã xảy ra thật 1 lần với "điểm dừng cứng", vá 2026-07-16, xem
tests/ cho case cụ thể). Dùng như LƯỚI AN TOÀN bổ sung — không thay thế đọc kỹ
khi patch thêm/bớt cổng cứng.

Dùng:
    python3 tools/verify_hard_gate_count_consistency.py          # in báo cáo
    python3 tools/verify_hard_gate_count_consistency.py --check  # exit 1 nếu lệch (dùng cho CI)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / ".claude" / "agents"
GATE_CONTRACT_TOOLS_DIR = ROOT / "medical-ebm-automation" / "tools"

# 28/08/2026 — repo y khoa nằm ngoài bản sao git gốc; thiếu thì khai báo rõ
# thay vì ModuleNotFoundError trần (trông như lỗi mã, thật ra thiếu nguyên liệu).
if not (GATE_CONTRACT_TOOLS_DIR / "gate_contract.py").exists():
    _THIEU_NGUYEN_LIEU = ("FAIL (bỏ qua CÓ KHAI BÁO): thiếu medical-ebm-automation/tools/gate_contract.py — "
                          "repo y khoa không có trên bản sao git này; chạy trên máy có đủ hai repo.")
    # Chạy CLI thì thoát sạch một dòng; bị IMPORT (pytest) thì raise ModuleNotFoundError
    # để bộ thu thập test xử lý như thiếu module bình thường, không chết INTERNALERROR.
    if __name__ == "__main__":
        raise SystemExit(_THIEU_NGUYEN_LIEU)
    raise ModuleNotFoundError(_THIEU_NGUYEN_LIEU)
if str(GATE_CONTRACT_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(GATE_CONTRACT_TOOLS_DIR))
import gate_contract as GC  # noqa: E402

# Bộ gate_id NGUỒN SỰ THẬT — mọi dòng "liệt kê cổng cứng" phải nhắc ĐỦ bộ này.
GATE_SET = sorted(GC._GATE_REQUIRED_STAKEHOLDERS.keys())

# "điểm dừng cứng" thêm 2026-07-16 — đồng nghĩa THẬT đã lọt lưới bản đầu (xem
# _KHUNG-DANH-GIA-KHA-THI.md, phát hiện qua audit đối kháng vòng 2).
_HARD_GATE_PHRASE = re.compile(r"cổng cứng|điểm dừng cứng|hard gate", re.IGNORECASE)


def _gates_mentioned_on_line(line: str) -> set[str]:
    return {g for g in GATE_SET if re.search(rf"\b{g}\b", line)}


def scan(agents_dir: Path = AGENTS_DIR, gate_set: list[str] = None) -> list[dict]:
    """Trả danh sách {file, line_no, line, missing} cho mọi dòng lệch.

    agents_dir/gate_set: chỉ để TEST tự (fixture thư mục giả lập) — mặc định
    dùng đúng AGENTS_DIR/GATE_SET thật của dự án khi gọi không tham số."""
    gate_set = gate_set if gate_set is not None else GATE_SET
    findings = []
    if not agents_dir.exists():
        return findings
    for path in sorted(agents_dir.glob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, start=1):
            if not _HARD_GATE_PHRASE.search(line):
                continue
            mentioned = {g for g in gate_set if re.search(rf"\b{g}\b", line)}
            if len(mentioned) < 2:
                continue  # dòng chỉ nhắc 0-1 gate — không đủ dấu hiệu đang LIỆT KÊ
            missing = set(gate_set) - mentioned
            if missing:
                try:
                    rel = str(path.relative_to(ROOT))
                except ValueError:
                    rel = str(path)
                findings.append({
                    "file": rel,
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
