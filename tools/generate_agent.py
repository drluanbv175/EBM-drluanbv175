#!/usr/bin/env python3
"""generate_agent.py — TỰ SINH AGENT (an toàn, đúng chuẩn nhà) khi hệ nghiên cứu
thiếu một năng lực chuyên biệt chưa có trong đội agent hiện tại.

TRIẾT LÝ (đóng vai trong vòng lặp khép kín):
  - Bộ điều phối (LLM `dieu-phoi-nghien-cuu`) PHÁT HIỆN khoảng trống năng lực và
    soạn SPEC (vai trò · trigger · phương pháp · ranh giới · cổng · nguồn bắt buộc).
  - Script này (xác định, không LLM) DỰNG agent .md ĐÚNG KHUNG NHÀ + CẤY guardrail
    + ĐĂNG KÝ (enforce → sync → audit) + GHI SỔ registry. Nhờ tách vai này, agent
    tự sinh AN TOÀN THEO CẤU TRÚC: luôn có luật nền, self-check, disclaimer, và
    cổng guardrail bắt buộc — bất kể nội dung chuyên môn.

BẤT BIẾN LIÊM CHÍNH:
  - Agent tự sinh là ĐỀ XUẤT: gắn nhãn [TỰ SINH — CHỜ BÁC SĨ DUYỆT], KHÔNG tự
    coi là "đã tin cậy". Bác sĩ duyệt (đổi nhãn) mới thành agent chính thức.
  - KHÔNG ghi đè agent đã có (trừ --force). KHÔNG bịa nguồn/thang điểm trong nội
    dung (spec phải nêu nguồn hoặc để [CẦN KIỂM CHỨNG]).
  - Mọi agent y khoa: chỉ ĐỀ XUẤT, bác sĩ duyệt mới "áp dụng"; kèm PMID/DOI +
    "Cần bác sĩ kiểm chứng" (cấy tự động qua enforce_agent_guardrails.py).

DÙNG:
  # Từ file spec JSON (bộ điều phối soạn — cách chính, giàu thông tin):
  python tools/generate_agent.py --spec spec.json [--register]

  # Nhanh bằng cờ CLI:
  python tools/generate_agent.py --name "vi-sinh-lam-sang" \\
      --description "..." --role "..." --cluster research --gate G3 [--register]

  # Kiểm khô (in nội dung, không ghi file):
  python tools/generate_agent.py --spec spec.json --dry-run

SPEC JSON (khóa; * = bắt buộc):
  {
    "name": "slug-khong-dau",            *  # a-z0-9- ; khớp tên file
    "description": "1 câu mô tả ...",     *  # dùng cho định tuyến (Agent tool)
    "role": "Bạn là Agent ... nhiệm vụ",  *  # câu mở đầu thân agent
    "cluster": "research|clinical",          # mặc định research
    "gate": "G3",                            # cổng NC (nếu thuộc pipeline)
    "when_to_use": ["trigger 1", ...],       # khi nào kích hoạt
    "method_steps": ["Bước 1 ...", ...],     # phương pháp có hệ thống
    "sources_required": true,                # buộc nêu PMID/DOI cho khẳng định
    "boundaries": "KHÔNG làm X (→ agent Y)", # ranh giới, chống chồng lấn
    "gate_criteria": "Đạt khi ...",          # tiêu chí qua cổng
    "base_laws": ["_HIEN-PHAP-LIEM-CHINH.md", "..."],  # mặc định 2 hiến pháp
    "origin": "auto|manual",                 # nguồn (mặc định auto)
    "requested_by": "dieu-phoi-nghien-cuu"   # ai yêu cầu sinh
  }
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
REGISTRY = AGENTS / "_TU-SINH-AGENT-REGISTRY.json"
TOOLS = ROOT / "tools"

# Cấy guardrail bắt buộc NGAY trong template (không chỉ dựa enforce chạy sau) →
# agent tự sinh có rào chắn kể cả khi CHƯA --register. Lấy từ nguồn canon để
# không lệch; enforce thấy MARKER rồi sẽ bỏ qua (idempotent).
sys.path.insert(0, str(TOOLS))
try:
    from enforce_agent_guardrails import BLOCK as _GUARDRAIL_BLOCK, MARKER as _GUARDRAIL_MARKER
except Exception:  # noqa: BLE001
    _GUARDRAIL_MARKER = "<!-- EBM-MANDATORY-FINAL-GUARDRAIL -->"
    _GUARDRAIL_BLOCK = (
        f"\n\n{_GUARDRAIL_MARKER}\n## Cổng bắt buộc trước khi trả lời\n\n"
        "Trước mọi đầu ra y khoa: tự áp guardrail `tham-dinh-dau-ra` 2 lớp "
        "(liêm chính R1–R7 + chất lượng Med-PaLM Q1–Q7); còn lỗi đỏ/thiếu nguồn/"
        "PII → trả `[CẦN BÁC SĨ PHÁN ĐỊNH]`; kết bằng: \"Cần bác sĩ kiểm chứng.\"\n")

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DEFAULT_BASE_LAWS = [
    "_HIEN-PHAP-LIEM-CHINH.md",
    "_NGUYEN-TAC-TRUNG-THUC-BAO-MAT-PHAP-LY-LIEM-CHINH.md",
]


class SpecError(ValueError):
    """Spec không hợp lệ (thiếu khóa bắt buộc / slug sai)."""


def _norm_slug(name: str) -> str:
    s = name.strip().lower().replace(" ", "-").replace("_", "-")
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def validate_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Kiểm + chuẩn hoá spec; raise SpecError nếu thiếu khóa bắt buộc."""
    for key in ("name", "description", "role"):
        if not str(spec.get(key, "")).strip():
            raise SpecError(f"Spec thiếu khóa bắt buộc '{key}'.")
    slug = _norm_slug(spec["name"])
    if not SLUG_RE.match(slug):
        raise SpecError(f"Tên '{spec['name']}' → slug '{slug}' không hợp lệ "
                        "(chỉ a-z, 0-9, gạch nối; không dấu).")
    if slug.startswith("_") or slug in ("readme",):
        raise SpecError(f"Slug '{slug}' trùng vùng dành cho hạ tầng/README.")
    out = dict(spec)
    out["name"] = slug
    out.setdefault("cluster", "research")
    out.setdefault("origin", "auto")
    out.setdefault("requested_by", "dieu-phoi-nghien-cuu")
    out.setdefault("sources_required", True)
    out.setdefault("base_laws", list(_DEFAULT_BASE_LAWS))
    return out


def _bullets(items: Optional[List[str]], empty: str) -> str:
    items = [str(x).strip() for x in (items or []) if str(x).strip()]
    if not items:
        return empty
    return "\n".join(f"- {x}" for x in items)


def render_agent_md(spec: Dict[str, Any]) -> str:
    """Dựng nội dung agent .md ĐÚNG KHUNG NHÀ (chưa gồm cổng guardrail — enforce cấy)."""
    name = spec["name"]
    desc = spec["description"].strip()
    role = spec["role"].strip()
    gate = str(spec.get("gate", "")).strip()
    cluster = spec.get("cluster", "research")
    base_laws = spec.get("base_laws") or _DEFAULT_BASE_LAWS
    laws = " và ".join(f"`.claude/agents/{b}`" for b in base_laws)
    gate_tag = f" (cổng {gate})" if gate else ""
    src_rule = ("KHÔNG bịa số liệu/thang điểm/trích dẫn — mọi khẳng định y khoa "
                "kèm PMID/DOI hoặc nhãn `[CẦN KIỂM CHỨNG]`. ") if spec.get(
                    "sources_required", True) else ""

    when = _bullets(spec.get("when_to_use"),
                    "- Khi bộ điều phối định tuyến tới năng lực này.")
    method = _bullets(spec.get("method_steps"),
                      "- [CẦN BỔ SUNG — bộ điều phối/bác sĩ mô tả các bước phương pháp]")
    boundaries = spec.get("boundaries") or (
        "[CẦN BỔ SUNG — nêu rõ việc KHÔNG làm để tránh chồng lấn agent khác]")
    gate_crit = spec.get("gate_criteria") or (
        "[CẦN BỔ SUNG — tiêu chí đạt cổng/hoàn thành cho agent này]")
    today = datetime.now().strftime("%Y-%m-%d")

    return f"""---
name: {name}
description: {desc}
model: inherit
---

> ⚠️ **[TỰ SINH — CHỜ BÁC SĨ DUYỆT]** (sinh {today}, nguồn: `{spec.get('requested_by')}`).
> Agent này do cơ chế `_TU-SINH-AGENT.md` tạo tự động khi hệ phát hiện KHOẢNG TRỐNG
> năng lực. Nó là **ĐỀ XUẤT**: bác sĩ rà nội dung, sửa/bổ nguồn, rồi XOÁ dòng cảnh
> báo này để "chuyển chính thức". Trước khi duyệt, coi đầu ra là **[DỰ THẢO]**.

{role}

## Luật nền
Tuân thủ {laws}. {src_rule}KHÔNG PII. Agent chỉ **ĐỀ XUẤT**, bác sĩ duyệt mới "áp dụng".

## Khi nào kích hoạt{gate_tag}
{when}

## Phương pháp có hệ thống
{method}

## Ranh giới
{boundaries}

## Tiêu chí hoàn thành / qua cổng
{gate_crit}

## BƯỚC TỰ KIỂM — trước khi trả đầu ra
1. Đối chiếu với **TIÊU CHÍ HOÀN THÀNH** của agent này.
2. Thiếu sót tự giải được → sửa ngay trong lần trả này.
3. Thiếu sót phụ thuộc input thật (IRB/data/SAP lock/nguồn) → gắn `[CẦN BỔ SUNG]`.
4. Chỉ trả khi self-check PASS; còn 🔴 → áp vòng tự sửa (`_TU-CHINH-SUA-PROTOCOL.md` §4).

```
✦ SELF-CHECK {name}:
  ĐÃ ĐẠT: [liệt kê tiêu chí đã đáp ứng]
  CÒN THIẾU: [liệt kê hoặc "không có"]
  KẾT: ĐẠT TỰ KIỂM / CÒN 🔴 → [hành động cụ thể]
```
{_GUARDRAIL_BLOCK}"""


def _load_registry() -> Dict[str, Any]:
    if REGISTRY.exists():
        try:
            return json.loads(REGISTRY.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"generated": []}


def _append_registry(spec: Dict[str, Any], path: Path) -> None:
    reg = _load_registry()
    reg.setdefault("generated", [])
    reg["generated"] = [g for g in reg["generated"] if g.get("name") != spec["name"]]
    reg["generated"].append({
        "name": spec["name"],
        "description": spec["description"],
        "cluster": spec.get("cluster"),
        "gate": spec.get("gate", ""),
        "origin": spec.get("origin", "auto"),
        "requested_by": spec.get("requested_by"),
        "created": datetime.now().isoformat(timespec="seconds"),
        "status": "PROPOSED — CHỜ BÁC SĨ DUYỆT",
        "file": str(path.relative_to(ROOT)),
    })
    REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")


def _run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=300)


def register_and_sync() -> Dict[str, Any]:
    """Chạy enforce (cấy guardrail) → sync Codex → check → audit. Trả tóm tắt."""
    py = sys.executable
    steps = {
        "enforce": [py, str(TOOLS / "enforce_agent_guardrails.py")],
        "sync": [py, str(TOOLS / "sync_agents_to_codex.py")],
        "check": [py, str(TOOLS / "sync_agents_to_codex.py"), "--check"],
        "audit": [py, str(TOOLS / "audit_ebm_system.py")],
    }
    result: Dict[str, Any] = {}
    for stage, cmd in steps.items():
        if not Path(cmd[1]).exists():
            result[stage] = {"skipped": f"không thấy {cmd[1]}"}
            continue
        proc = _run(cmd)
        result[stage] = {"rc": proc.returncode,
                         "tail": "\n".join(proc.stdout.splitlines()[-4:])}
    return result


def generate(spec: Dict[str, Any], *, register: bool = False,
             force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    spec = validate_spec(spec)
    path = AGENTS / f"{spec['name']}.md"
    md = render_agent_md(spec)

    if dry_run:
        print(md)
        return {"name": spec["name"], "dry_run": True, "path": str(path)}

    if path.exists() and not force:
        raise SpecError(f"Agent '{spec['name']}' đã tồn tại tại {path} — dùng "
                        "--force nếu THỰC SỰ muốn ghi đè (cẩn trọng: mất nội dung cũ).")

    AGENTS.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")
    _append_registry(spec, path)
    out: Dict[str, Any] = {"name": spec["name"], "path": str(path.relative_to(ROOT)),
                           "registered": False}
    print(f"✅ Đã sinh agent (ĐỀ XUẤT): {path.relative_to(ROOT)}")
    print(f"   Ghi registry: {REGISTRY.relative_to(ROOT)}")

    if register:
        print("🔧 Đăng ký: enforce → sync → check → audit ...")
        res = register_and_sync()
        out["registered"] = True
        out["register_result"] = res
        for stage, r in res.items():
            rc = r.get("rc")
            mark = "✅" if rc in (0, None) else "❌"
            print(f"   {mark} {stage}: rc={rc}")
    else:
        print("   ↪ Chưa đăng ký. Chạy lại với --register, hoặc thủ công:")
        print("       python tools/enforce_agent_guardrails.py")
        print("       python tools/sync_agents_to_codex.py && "
              "python tools/sync_agents_to_codex.py --check")
        print("       python tools/audit_ebm_system.py")
    print("   ⚠ Agent ở trạng thái [TỰ SINH — CHỜ BÁC SĨ DUYỆT]. "
          "Bác sĩ rà + xoá dòng cảnh báo để chuyển chính thức.")
    print("   Cần bác sĩ kiểm chứng.")
    return out


def _spec_from_args(a: argparse.Namespace) -> Dict[str, Any]:
    if a.spec:
        data = json.loads(Path(a.spec).read_text(encoding="utf-8"))
        # cho phép ghi đè bằng cờ CLI nếu có
        for k in ("name", "description", "role", "cluster", "gate"):
            v = getattr(a, k.replace("-", "_"), None)
            if v:
                data[k] = v
        return data
    return {
        "name": a.name, "description": a.description, "role": a.role,
        "cluster": a.cluster, "gate": a.gate,
        "when_to_use": a.when or [], "method_steps": a.method or [],
        "boundaries": a.boundaries, "gate_criteria": a.gate_criteria,
        "origin": a.origin, "requested_by": a.requested_by,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Tự sinh agent đúng chuẩn nhà + đăng ký.")
    ap.add_argument("--spec", help="Đường dẫn file spec JSON")
    ap.add_argument("--name")
    ap.add_argument("--description")
    ap.add_argument("--role")
    ap.add_argument("--cluster", default="research", choices=["research", "clinical"])
    ap.add_argument("--gate", default="")
    ap.add_argument("--when", action="append", help="Trigger (lặp nhiều lần)")
    ap.add_argument("--method", action="append", help="Bước phương pháp (lặp)")
    ap.add_argument("--boundaries", default="")
    ap.add_argument("--gate-criteria", dest="gate_criteria", default="")
    ap.add_argument("--origin", default="auto")
    ap.add_argument("--requested-by", dest="requested_by", default="dieu-phoi-nghien-cuu")
    ap.add_argument("--register", action="store_true",
                    help="Chạy enforce+sync+check+audit sau khi sinh")
    ap.add_argument("--force", action="store_true", help="Ghi đè agent trùng tên")
    ap.add_argument("--dry-run", action="store_true", help="In nội dung, không ghi file")
    a = ap.parse_args()

    if not a.spec and not (a.name and a.description and a.role):
        ap.error("Cần --spec HOẶC đủ (--name --description --role).")

    try:
        spec = _spec_from_args(a)
        generate(spec, register=a.register, force=a.force, dry_run=a.dry_run)
    except (SpecError, json.JSONDecodeError, OSError) as e:
        print(f"❌ LỖI: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
