#!/usr/bin/env python3
"""verify_agent_routing.py — KIỂM CHỨNG đồ thị định tuyến agent (S1 kiến trúc rõ ràng
· S2 phối hợp giữa các agent).

Vá khoảng trống đã xác nhận (đánh giá độc lập 2026-07-04): tuyên bố "không agent mồ
côi, không tham chiếu treo" trong `_BAN-DO-KET-NOI.md`/README.md là VĂN XUÔI THỦ CÔNG,
chưa có công cụ nào KIỂM LẠI bằng máy. Module này parse THẬT hai nhạc trưởng
(`dieu-phoi-nghien-cuu.md`, `dieu-phoi-lam-sang.md`), trích mọi tham chiếu tên-agent
dạng backtick, đối chiếu với danh sách file `.claude/agents/*.md` THẬT, báo:
  - agent MỒ CÔI: có file nhưng KHÔNG nhạc trưởng nào tham chiếu.
  - tham chiếu TREO: backtick tên trông như agent nhưng KHÔNG khớp file nào.

AN TOÀN CHỐNG DƯƠNG TÍNH GIẢ: hai file nhạc trưởng backtick-wrap CẢ tên file hạ tầng
(`_SO-TRANG-THAI-CHECKPOINT.md`), tên script (`run_g0_auto.py`), mã artifact/cổng
(`A1`, `G10`), VÀ tên skill (`nghien-cuu-y-khoa-chuan-quoc-te`) — naive regex sẽ báo
sai các token này là "tham chiếu treo". Bộ lọc dưới đây loại các loại token đó TRƯỚC
khi tính dangling_references.

CHẾ ĐỘ: mặc định CHỈ BÁO CÁO (không hard-fail) — vì đây là lần đầu chạy, cần xác nhận
KHÔNG dương tính giả trước khi biến thành cổng cứng. Dùng --strict để exit 1 khi còn
dangling_references (orphan_agents KHÔNG BAO GIỜ hard-fail — một agent chưa được nhạc
trưởng nào gọi trực tiếp có thể vẫn hợp lệ, vd gọi thủ công bởi bác sĩ).

Dùng:
  python tools/verify_agent_routing.py                # báo cáo văn bản
  python tools/verify_agent_routing.py --json          # JSON
  python tools/verify_agent_routing.py --strict        # exit 1 nếu còn dangling_references
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Set

# Windows: stdout mặc định cp1252 giết print() tiếng Việt — ép UTF-8 (chốt BH55/R4)
import sys as _sys_r4
for _s_r4 in (_sys_r4.stdout, _sys_r4.stderr):
    try:
        _s_r4.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / ".claude" / "agents"
ORCHESTRATORS = [
    AGENTS_DIR / "dieu-phoi-nghien-cuu.md",
    AGENTS_DIR / "dieu-phoi-lam-sang.md",
]

# Skill thật (từ danh mục skill khả dụng trong phiên — cập nhật nếu danh mục đổi).
# Đây là allowlist THỦ CÔNG có chủ đích: skill sống ở kho riêng, KHÔNG phải file
# .claude/agents/*.md, nên không thể tự phát hiện bằng cách quét thư mục agent.
KNOWN_SKILL_NAMES: Set[str] = {
    "antifacts", "cap-nhat-chung-cu-y-khoa", "citation-management",
    "clinical-evidence-rag", "consolidate-memory", "dao-tao-slide-tai-lieu-y-khoa",
    "dark-analyst", "dashboard-master-ebm-ngoai-tru", "docx", "ebm-master",
    "ehospital-mini", "giao-tiep-quyet-dinh-soap", "ke-don-an-toan-benh-man",
    "kham-ngoai-tru-ebm", "literature-review", "nghien-cuu-ebm-tong-hop",
    "nghien-cuu-y-khoa-chuan-quoc-te", "nguoi-cao-tuoi-da-benh-da-thuoc",
    "paper-lookup", "pdf", "peer-review", "pptx", "quan-ly-cap-nhat-ebm",
    "research-lookup", "schedule", "scientific-writing", "setup-cowork",
    "statistical-analysis", "tao-video-tiktok", "tham-dinh-chung-cu-grade-nnt",
    "tiep-can-chan-doan-co-do-chuyen-tuyen", "tuan-thu-dieu-tri", "xlsx",
}

# 2026-07-05: khoảng trống phát hiện thủ công — tiêu đề của _BAN-DO-KET-NOI.md/
# README.md ghi số đếm agent CỨNG ("(48 agent: ...)") mà không công cụ nào đối
# chiếu lại với số thật sau mỗi lần thêm/bớt agent → tiêu đề trôi âm thầm (xảy
# ra ít nhất 2 lần: 48→49→50 hôm 2026-07-04, phải người phát hiện tay). Bắt
# lớp bug này tự động thay vì chờ audit thủ công lần sau.
_TITLE_COUNT = re.compile(r"\((\d+)\s+agent", re.IGNORECASE)
_TITLE_COUNT_DOCS = ["_BAN-DO-KET-NOI.md", "README.md"]

_BACKTICK_TOKEN = re.compile(r"`([^`]+)`")
_ARTIFACT_ID = re.compile(r"^[AG]\d+[a-z]?$")           # A1, A13b, G0, G10...
# SỬA (kiểm chứng lần đầu trên hệ THẬT phát hiện 2 vòng): mọi agent thật đều hợp
# TỪ ≥2 ĐOẠN (≥1 gạch nối) — `binh-duyet` là agent DUY NHẤT chỉ 1 gạch nối, mọi
# agent khác ≥2. Ngưỡng ≥1 gạch nối (không phải ≥2 — vòng đầu quá chặt, làm mất
# đúng "binh-duyet") vẫn loại được từ tiếng Việt đơn lẻ trong code span nhấn mạnh
# (`bash`, `ghi`, `khi`, `nay`... — KHÔNG gạch nối) mà không bỏ sót tham chiếu thật.
_KEBAB_IDENT = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)+$")
_FENCED_BLOCK = re.compile(r"```.*?```", re.DOTALL)


def real_agent_slugs() -> Set[str]:
    """Tên (slug, không .md) của mọi agent CHUYÊN TRÁCH thật — loại hạ tầng `_*` + README."""
    return {
        p.stem for p in AGENTS_DIR.glob("*.md")
        if p.name != "README.md" and not p.name.startswith("_")
    }


def _first_word(token: str) -> str:
    """Cắt token backtick tại khoảng trắng đầu tiên — xử lý kiểu `verify_x.py --flag`."""
    return token.strip().split()[0] if token.strip() else ""


def classify_token(token: str, agents: Set[str]) -> str:
    """Phân loại 1 token backtick: 'agent' | 'infra_or_script' | 'artifact_id' |
    'skill' | 'dangling_candidate' | 'other' (không phải định dạng tên agent)."""
    t = _first_word(token)
    if not t:
        return "other"
    if t.endswith(".md") or t.endswith(".py") or "/" in t or "\\" in t:
        return "infra_or_script"
    if _ARTIFACT_ID.match(t):
        return "artifact_id"
    if not _KEBAB_IDENT.match(t):
        return "other"
    if t in agents:
        return "agent"
    if t in KNOWN_SKILL_NAMES:
        return "skill"
    return "dangling_candidate"


def extract_references(md_path: Path, agents: Set[str]) -> Dict[str, Set[str]]:
    """Trích tham chiếu từ 1 file nhạc trưởng — trả {agent, dangling, filtered}."""
    if not md_path.exists():
        return {"agent": set(), "dangling": set(), "filtered": set()}
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    # Bỏ khối code rào 3-backtick TRƯỚC khi quét — chúng chứa lệnh shell/code, không
    # phải tham chiếu agent; quét lẫn vào sẽ vỡ ranh giới backtick đơn (đã xác nhận
    # bằng chạy thật: "```bash" bị hiểu nhầm thành token backtick đơn "bash").
    text = _FENCED_BLOCK.sub(" ", text)
    out = {"agent": set(), "dangling": set(), "filtered": set()}
    for m in _BACKTICK_TOKEN.finditer(text):
        t = _first_word(m.group(1))
        if not t:
            continue
        kind = classify_token(t, agents)
        if kind == "agent":
            out["agent"].add(t)
        elif kind == "dangling_candidate":
            out["dangling"].add(t)
        elif kind in ("infra_or_script", "artifact_id", "skill"):
            out["filtered"].add(t)
    return out


def check_title_counts_fresh(total_agents: int) -> list:
    """Đối chiếu số đếm agent NÊU TRONG TIÊU ĐỀ (3 dòng đầu) của các sổ hạ tầng
    chủ chốt với tổng số agent THẬT hiện có. Trả list rỗng nếu khớp hết."""
    mismatches = []
    for name in _TITLE_COUNT_DOCS:
        doc = AGENTS_DIR / name
        if not doc.exists():
            continue
        header = "\n".join(doc.read_text(encoding="utf-8", errors="ignore").splitlines()[:3])
        m = _TITLE_COUNT.search(header)
        if m and int(m.group(1)) != total_agents:
            mismatches.append({"file": name, "claimed": int(m.group(1)), "actual": total_agents})
    return mismatches


def audit_routing() -> Dict:
    """Chạy kiểm chứng đầy đủ trên hệ THẬT — trả dict báo cáo."""
    agents = real_agent_slugs()
    referenced: Set[str] = set()
    dangling: Set[str] = set()
    filtered_examples: Set[str] = set()
    per_file: Dict[str, Dict] = {}

    for orch in ORCHESTRATORS:
        r = extract_references(orch, agents)
        referenced |= r["agent"]
        dangling |= r["dangling"]
        filtered_examples |= r["filtered"]
        per_file[orch.name] = {
            "agents_referenced": sorted(r["agent"]),
            "dangling_candidates": sorted(r["dangling"]),
        }

    orphan_agents = agents - referenced
    # Loại khỏi "mồ côi": (a) guardrail chung tham-dinh-dau-ra — được GỌI BỞI các
    # nhạc trưởng ở bước cuối nhưng không nhất thiết bằng backtick trong chính file
    # đó; (b) CHÍNH 2 nhạc trưởng — chúng không (và không cần) tự tham chiếu tên
    # mình, "mồ côi" ở đây vô nghĩa cho chủ thể điều phối.
    orchestrator_slugs = {p.stem for p in ORCHESTRATORS}
    orphan_agents -= {"tham-dinh-dau-ra"} | orchestrator_slugs

    return {
        "total_agents": len(agents),
        "referenced_by_orchestrators": sorted(referenced),
        "orphan_agents": sorted(orphan_agents),
        "dangling_references": sorted(dangling),
        "filtered_out_examples": sorted(filtered_examples)[:20],
        "per_file": per_file,
        "title_count_mismatches": check_title_counts_fresh(len(agents)),
    }


def print_report(rep: Dict) -> None:
    print("\n=== KIỂM CHỨNG ĐỊNH TUYẾN AGENT (S1/S2) ===")
    print(f"  Tổng agent chuyên trách: {rep['total_agents']}")
    print(f"  Được nhạc trưởng tham chiếu: {len(rep['referenced_by_orchestrators'])}")
    if rep["orphan_agents"]:
        print("  🟡 Agent MỒ CÔI (không nhạc trưởng nào gọi trực tiếp — có thể vẫn hợp lệ nếu bác sĩ gọi tay):")
        for a in rep["orphan_agents"]:
            print(f"      - {a}")
    else:
        print("  ✅ Không agent nào mồ côi.")
    if rep["dangling_references"]:
        print("  🔴 THAM CHIẾU TREO (tên trông như agent nhưng KHÔNG khớp file nào):")
        for a in rep["dangling_references"]:
            print(f"      - {a}")
    else:
        print("  ✅ Không tham chiếu treo.")
    print(f"  (đã lọc {len(rep['filtered_out_examples'])} token không phải agent — vd: "
          f"{', '.join(rep['filtered_out_examples'][:5])}...)")
    if rep["title_count_mismatches"]:
        print("  🔴 TIÊU ĐỀ GHI SỐ CŨ (trôi khỏi tổng agent thật):")
        for mm in rep["title_count_mismatches"]:
            print(f"      - {mm['file']}: ghi {mm['claimed']} agent, thật là {mm['actual']}")
    else:
        print(f"  ✅ Tiêu đề {'/'.join(_TITLE_COUNT_DOCS)} khớp tổng agent thật ({rep['total_agents']}).")


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm chứng đồ thị định tuyến agent (S1/S2).")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="Exit 1 nếu còn dangling_references (orphan_agents KHÔNG hard-fail)")
    args = ap.parse_args()

    rep = audit_routing()
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print_report(rep)

    if args.strict and (rep["dangling_references"] or rep["title_count_mismatches"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
