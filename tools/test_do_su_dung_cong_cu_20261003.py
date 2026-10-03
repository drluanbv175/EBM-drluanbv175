#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy Q7 (03/10/2026): sổ đo sử dụng công cụ dài hạn — chỉ đếm TÊN, chạy lại không đếm trùng, không giữ nội dung hội thoại.
Transcript giả trong thư mục tạm; ngoại tuyến."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location("_t_dsd", TOOLS / "do_su_dung_cong_cu.py")
D = importlib.util.module_from_spec(sp)
sys.modules["_t_dsd"] = D
sp.loader.exec_module(D)

BI_MAT = "NOI DUNG RIENG TU CUA BENH NHAN 0912345678"


def _tl(sid, ts, *tool, model="claude-opus-5-5"):
    return {"type": "assistant", "sessionId": sid, "timestamp": ts,
            "message": {"model": model, "content": [{"type": "text", "text": BI_MAT}, *tool]}}


def _tu(name, **inp):
    return {"type": "tool_use", "name": name, "input": {"command": BI_MAT, **inp}}


def test_dem_mot_dong_chi_lay_ten():
    d = _tl("s1", "2026-09-10T01:00:00Z", _tu("Bash"), _tu("Skill", skill="cap-nhat-chung-cu-y-khoa"),
            _tu("Agent", subagent_type="tham-dinh-dau-ra"), _tu("mcp__plugin_healthcare_PubMed__search_articles"))
    sid, c = D.dem_mot_dong(d, "2026-09")
    assert sid == "s1" and c["tool:Bash"] == 1 and c["skill:cap-nhat-chung-cu-y-khoa"] == 1
    assert c["agent:tham-dinh-dau-ra"] == 1 and c["mcp:plugin_healthcare_PubMed"] == 1 and c["model:claude-opus-5-5"] == 1
    assert BI_MAT not in json.dumps(c, ensure_ascii=False) and "0912345678" not in json.dumps(c)


def test_lenh_gach_cheo_chi_lay_ten():
    d = {"type": "user", "sessionId": "s2", "timestamp": "2026-09-11T00:00:00Z",
         "message": {"content": f"<command-name>/cap-nhat-chung-cu-y-khoa</command-name> {BI_MAT}"}}
    _sid, c = D.dem_mot_dong(d, "2026-09")
    assert dict(c) == {"lenh:cap-nhat-chung-cu-y-khoa": 1}
    assert D.dem_mot_dong({**d, "message": {"content": BI_MAT}}, "2026-09") is None, "tin nhắn thường không đếm gì"


def test_khac_thang_khong_dem():
    assert D.dem_mot_dong(_tl("s1", "2026-08-31T23:00:00Z", _tu("Bash")), "2026-09") is None


def _viet(goc: Path, ten: str, dong: list[dict], mtime: float | None = None) -> Path:
    tep = goc / ten
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in dong) + "\n{hỏng\n", encoding="utf-8", newline="\n")
    if mtime:
        os.utime(tep, (mtime, mtime))
    return tep


def test_dem_thang_ke_ca_agent_con_va_ghi_khong_dem_trung(tmp_path):
    goc = tmp_path / "projects"
    _viet(goc, "duan/a.jsonl", [_tl("s1", "2026-09-02T00:00:00Z", _tu("Bash"), _tu("Read")),
                                 _tl("s1", "2026-09-03T00:00:00Z", _tu("Bash"))])
    _viet(goc, "duan/a/subagents/agent-1.jsonl", [_tl("s1", "2026-09-02T01:00:00Z", _tu("Grep"))])
    _viet(goc, "duan/cu.jsonl", [_tl("s9", "2026-09-05T00:00:00Z", _tu("Bash"))], mtime=time.mktime((2026, 8, 1, 0, 0, 0, 0, 0, -1)))
    phien = D.dem_thang("2026-09", goc)
    assert phien == {"s1": {"tool:Bash": 2, "tool:Read": 1, "tool:Grep": 1, "model:claude-opus-5-5": 3}}, \
        "tệp có mtime trước tháng bị bỏ qua (nhanh); dòng hỏng không làm sập"
    st = tmp_path / "state"
    D.ghi("2026-09", phien, st)
    tep = D.ghi("2026-09", phien, st)
    d = json.loads(tep.read_text(encoding="utf-8"))
    assert d["tong"]["tool"]["Bash"] == 2 and d["so_phien"] == 1, "chạy lại không cộng dồn"
    assert BI_MAT not in tep.read_text(encoding="utf-8")
    th = D.tong_hop(st)
    assert th["tool"]["Bash"] == {"2026-09": 2}


def test_main_khong_thay_thu_muc_la_khong_do_duoc(tmp_path):
    assert D.main(["--goc", str(tmp_path / "khong-co")]) == 2


def test_tac_vu_thang_goi_cong_cu():
    sk = (TOOLS.parent / "sync" / "scheduled-tasks" / "kiem-tra-hoan-thien-he-thong-thang" / "SKILL.md").read_text(encoding="utf-8")
    assert "tools/do_su_dung_cong_cu.py --thang" in sk and "--ghi" in sk
