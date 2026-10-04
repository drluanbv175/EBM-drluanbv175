# -*- coding: utf-8 -*-
"""Test hồi quy: làn đối chiếu skill tài khoản ↔ repo phải SO skill của bác sĩ dù manifest ghi `source` = «plugin» (04/10/2026).

Lỗi thật: bộ lọc cũ chỉ giữ `source == "custom"`; manifest thật ghi skill của bác sĩ là «plugin» ⇒ mọi skill bị loại khỏi phép so,
`dong_bo_tat_ca.py` báo «giống 0 · lệch bản 0» trong khi 20/25 skill của bác sĩ trên tài khoản đã cũ (cap-nhat-chung-cu-y-khoa
v1.15.0 so với repo v1.53.0). Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("_dcbb_t", REPO / "tools" / "doi_chieu_ba_ben.py")
dc = importlib.util.module_from_spec(sp)
sys.modules["_dcbb_t"] = dc
sp.loader.exec_module(dc)


def _skill(goc: Path, ten: str, than: str):
    (goc / ten).mkdir(parents=True)
    (goc / ten / "SKILL.md").write_text(f"---\nname: {ten}\ndescription: mô tả {ten}\n---\n{than}\n", encoding="utf-8")


def _du_lieu(tmp_path):
    cloud, repo = tmp_path / "cloud", tmp_path / "repo"
    noi_dung_cu = "\n".join(f"Dòng hướng dẫn số {i} về cập nhật chứng cứ." for i in range(30))
    noi_dung_moi = noi_dung_cu + "\n" + "\n".join(f"Dòng bổ sung {i} của phiên bản mới." for i in range(10))
    _skill(cloud, "cap-nhat-chung-cu-y-khoa", noi_dung_cu)
    _skill(cloud, "docx", "Skill của Anthropic.")
    _skill(cloud, "ky-nang-khong-ghi-nguon", noi_dung_cu)
    _skill(repo, "cap-nhat-chung-cu-y-khoa", noi_dung_moi)
    _skill(repo, "ky-nang-khong-ghi-nguon", noi_dung_moi)
    _skill(repo, "tong-thuat-chung-cu", "Skill chỉ có trong repo.")
    (cloud / "manifest.json").write_text(json.dumps({"skills": [
        {"name": "cap-nhat-chung-cu-y-khoa", "source": "plugin"},
        {"name": "docx", "source": "anthropic"},
        {"name": "ky-nang-khong-ghi-nguon"},
    ]}), encoding="utf-8")
    return dc.quet_thu_muc(cloud), dc.quet_thu_muc(repo), dc.doc_manifest(cloud)


def test_skill_nguon_plugin_duoc_so_va_bao_lech_ban(tmp_path):
    cloud, repo, man = _du_lieu(tmp_path)
    kq = dc.doi_chieu(cloud, repo, man, chi_custom=True)
    lech = {m["ten"] for m in kq["lech_ban"]}
    assert "cap-nhat-chung-cu-y-khoa" in lech, "skill «plugin» của bác sĩ bị loại khỏi phép so — báo «0 lệch bản» giả"
    assert "ky-nang-khong-ghi-nguon" in lech, "skill không ghi nguồn phải coi là của bác sĩ"
    assert kq["chi_repo"] == ["tong-thuat-chung-cu"]


def test_skill_anthropic_khong_tinh(tmp_path):
    cloud, repo, man = _du_lieu(tmp_path)
    kq = dc.doi_chieu(cloud, repo, man, chi_custom=True)
    assert "docx" not in kq["chi_cloud"] and all(m["ten"] != "docx" for m in kq["lech_ban"] + kq["giong"])
    assert "docx" in dc.doi_chieu(cloud, repo, man, chi_custom=False)["chi_cloud"], "--tat-ca vẫn thấy skill Anthropic"
