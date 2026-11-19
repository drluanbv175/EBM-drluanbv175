#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KIỂM SỨC KHOẺ ĐỘI AGENT `.claude/agents` — chỉ đọc (19/11/2026).

VÌ SAO CÓ
=========
Bác sĩ (19/11/2026): «Codex nếu không cần thiết hãy loại bỏ ra cho tôi vì tôi cũng không còn dùng nữa». Trước đó hai công cụ
`sync_agents_to_codex.py --check` và `check_claude_codex_sync_health.py` vừa kiểm BẢN SAO Codex (`.Codex/agents/*.toml`) vừa
kiểm NGUỒN `.claude/agents`. Bản sao Codex đã gỡ; phần kiểm NGUỒN thì vẫn cần — nó là thứ bắt được frontmatter hỏng (bài học
«YAML agent hỏng», 10/08/2026), agent thiếu khối guardrail bắt buộc hay thiếu disclaimer. Công cụ này giữ ĐÚNG phần đó:

  1. Mỗi `.claude/agents/<tên>.md` (trừ README và tệp `_*`) có YAML frontmatter đọc được, có `name` + `description`,
     và `name` trùng tên tệp.
  2. Đủ agent cốt lõi (`AGENT_BAT_BUOC`) và đủ sổ hạ tầng (`HA_TANG_BAT_BUOC`).
  3. Mọi agent mang khối `EBM-MANDATORY-FINAL-GUARDRAIL` và câu «Cần bác sĩ kiểm chứng» (khối do
     `tools/enforce_agent_guardrails.py` chèn — thiếu thì chạy công cụ đó).

Dùng:
    python3 tools/kiem_suc_khoe_agent.py [--json]
Mã thoát: 0 = PASS · 1 = FAIL (in rõ từng lỗi) · 2 = không thấy thư mục `.claude/agents`.
Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[1]
THU_MUC_NGUON = ROOT / ".claude" / "agents"
DAU_GUARDRAIL = "EBM-MANDATORY-FINAL-GUARDRAIL"
DISCLAIMER = "Cần bác sĩ kiểm chứng"

AGENT_BAT_BUOC = {
    "dieu-phoi-lam-sang", "dieu-phoi-nghien-cuu", "tham-dinh-dau-ra", "pico-lam-sang", "chan-doan-xac-suat",
    "thu-thu-tai-lieu", "tong-quan-y-van", "viet-ban-thao", "binh-duyet",
}
HA_TANG_BAT_BUOC = {
    "README.md", "_BAN-DO-KET-NOI.md", "_HIEN-PHAP-LIEM-CHINH.md", "_KIEM-DUYET-DOC-LAP.md",
    "_CHUAN-CHAT-LUONG-MEDPALM.md", "_NGUYEN-TAC-TRUNG-THUC-BAO-MAT-PHAP-LY-LIEM-CHINH.md",
    "_SO-TRANG-THAI-CHECKPOINT.md", "_KIEM-TOAN-DAY-DU-NGHIEN-CUU.md", "_PLUGIN-ROUTING-CONTRACT.md",
}
_FRONTMATTER = re.compile(r"\A---\n(?P<meta>.*?)\n---\n?(?P<body>.*)\Z", re.DOTALL)


@dataclass
class BaoCao:
    trang_thai: str = "PASS"
    so_agent: int = 0
    so_ha_tang: int = 0
    co_guardrail: int = 0
    co_disclaimer: int = 0
    loi: list[str] = field(default_factory=list)


def duong_agent(thu_muc: Path | None = None) -> list[Path]:
    thu_muc = thu_muc or THU_MUC_NGUON
    return sorted(p for p in thu_muc.glob("*.md") if p.name != "README.md" and not p.name.startswith("_"))


def duong_ha_tang(thu_muc: Path | None = None) -> list[Path]:
    thu_muc = thu_muc or THU_MUC_NGUON
    return sorted(p for p in thu_muc.glob("*.md") if p.name == "README.md" or p.name.startswith("_"))


def doc_frontmatter(p: Path) -> dict[str, str]:
    """{name, description, …} của một agent. Hỏng khuôn ⇒ ValueError kèm tên tệp (không đoán)."""
    m = _FRONTMATTER.match(p.read_text(encoding="utf-8"))
    if not m:
        raise ValueError(f"{p.name}: không có YAML frontmatter")
    meta: dict[str, str] = {}
    for dong in m.group("meta").splitlines():
        d = dong.strip()
        if not d or d.startswith("#"):
            continue
        if ":" not in d:
            raise ValueError(f"{p.name}: dòng frontmatter không hợp lệ: {dong!r}")
        k, v = d.split(":", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in {"'", '"'}:
            v = v[1:-1]
        meta[k.strip()] = v
    if not meta.get("name", "").strip() or not meta.get("description", "").strip():
        raise ValueError(f"{p.name}: thiếu name hoặc description")
    if p.stem != meta["name"].strip():
        raise ValueError(f"{p.name}: tên tệp khác name ({p.stem!r} ≠ {meta['name'].strip()!r})")
    return meta


def danh_gia(thu_muc: Path | None = None) -> BaoCao:
    thu_muc = thu_muc or THU_MUC_NGUON
    bc = BaoCao()
    agents, ha_tang = duong_agent(thu_muc), duong_ha_tang(thu_muc)
    bc.so_agent, bc.so_ha_tang = len(agents), len(ha_tang)
    for p in agents:
        try:
            doc_frontmatter(p)
        except (OSError, ValueError) as exc:
            bc.loi.append(str(exc))
        van_ban = p.read_text(encoding="utf-8", errors="ignore")
        if DAU_GUARDRAIL in van_ban:
            bc.co_guardrail += 1
        else:
            bc.loi.append(f"{p.name}: thiếu khối {DAU_GUARDRAIL} — chạy tools/enforce_agent_guardrails.py")
        if DISCLAIMER in van_ban:
            bc.co_disclaimer += 1
        else:
            bc.loi.append(f"{p.name}: thiếu câu «{DISCLAIMER}»")
    thieu_agent = sorted(AGENT_BAT_BUOC - {p.stem for p in agents})
    thieu_ha_tang = sorted(HA_TANG_BAT_BUOC - {p.name for p in ha_tang})
    if thieu_agent:
        bc.loi.append("thiếu agent cốt lõi: " + ", ".join(thieu_agent))
    if thieu_ha_tang:
        bc.loi.append("thiếu sổ hạ tầng: " + ", ".join(thieu_ha_tang))
    bc.trang_thai = "PASS" if not bc.loi else "FAIL"
    return bc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm sức khoẻ đội agent .claude/agents (chỉ đọc)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not THU_MUC_NGUON.is_dir():
        print(f"⚪ không thấy {THU_MUC_NGUON}")
        return 2
    bc = danh_gia()
    if a.json:
        print(json.dumps(asdict(bc), ensure_ascii=False, indent=2))
    else:
        print(f"Sức khoẻ agent: {bc.trang_thai}")
        print(f"- {bc.so_agent} agent · guardrail {bc.co_guardrail}/{bc.so_agent} · disclaimer "
              f"{bc.co_disclaimer}/{bc.so_agent} · hạ tầng {bc.so_ha_tang}")
        for x in bc.loi:
            print(f"- {x}")
    return 0 if bc.trang_thai == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
