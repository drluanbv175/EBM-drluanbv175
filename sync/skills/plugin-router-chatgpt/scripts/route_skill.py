#!/usr/bin/env python3
"""Xếp hạng skill cài sẵn cho một yêu cầu bằng thuật toán minh bạch, ngoại tuyến."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path


STOP = {
    "va", "voi", "cho", "cua", "la", "mot", "nhung", "cac", "toi", "giup", "hay",
    "the", "and", "for", "with", "this", "that", "from", "into", "use", "using",
}

PLUGIN_CUES = {
    "pubmed-search": {"pubmed", "medline", "pmid", "truy van", "tim bai"},
    "meta-pipe": {"meta analysis", "phan tich gop", "forest plot", "prisma"},
    "academic-research-skills": {"ban thao", "abstract", "phan bien", "revision", "hoc thuat"},
    "aipoch-medical-research": {"omics", "single cell", "faers", "mendelian", "qtl", "biomarker"},
    "codex": {"code", "lap trinh", "sua loi", "test", "repository"},
    "claude-code-harness": {"harness", "agent", "workflow", "kiem thu"},
    "humanizer": {"tu nhien hon", "van phong", "humanize"},
    "openmed-skills": {"lam sang", "thuoc", "benh nhan", "y khoa"},
    "medsci-project": {"du an khoa hoc", "nghien cuu", "phan tich du lieu"},
}


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    plain = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", plain).strip()


def tokens(text: str) -> set[str]:
    return {token for token in normalize(text).split() if len(token) > 1 and token not in STOP}


def rank(query: str, catalog: dict, top: int) -> list[dict]:
    q_norm = normalize(query)
    q_tokens = tokens(query)
    ranked: list[dict] = []
    for skill in catalog.get("skills", []):
        name_norm = normalize(str(skill.get("name", "")))
        desc_norm = normalize(str(skill.get("description", "")))
        name_tokens = tokens(name_norm)
        desc_tokens = tokens(desc_norm)
        score = 5 * len(q_tokens & name_tokens) + len(q_tokens & desc_tokens)
        if name_norm and name_norm in q_norm:
            score += 12
        plugin = str(skill.get("plugin_name", ""))
        for cue in PLUGIN_CUES.get(plugin, set()):
            if cue in q_norm:
                score += 4
        if score <= 0:
            continue
        ranked.append(
            {
                "score": score,
                "plugin": plugin,
                "skill": skill.get("name", ""),
                "invoke": f"@{plugin}:{skill.get('name', '')}",
                "description": skill.get("description", ""),
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["plugin"], item["skill"]))
    return ranked[:top]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "references/plugin-catalog.json",
    )
    args = parser.parse_args()
    if not args.catalog.is_file():
        parser.error(f"Chưa có catalog: {args.catalog}; chạy scripts/build_catalog.py trước.")
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    result = rank(args.query, data, max(1, min(args.top, 20)))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif not result:
        print("Không tìm thấy skill đủ khớp; giữ owner nội bộ và yêu cầu làm rõ nếu cần.")
    else:
        for index, item in enumerate(result, 1):
            print(f"{index}. {item['invoke']} · điểm {item['score']} · {item['description']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
