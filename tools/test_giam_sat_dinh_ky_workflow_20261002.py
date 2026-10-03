#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy F8 (02/10/2026): workflow `giam-sat-dinh-ky.yml` bỏ qua 3 verifier mọi lượt mà vẫn xanh.

Đo: bước lấy repo anh em chỉ chạy khi có secret SIBLING_REPO_TOKEN (chưa ai đặt) dù repo anh em CÔNG KHAI ⇒ 3 verifier
(verify_research_gate_contracts · verify_controlled_research_automation · verify_lessons_rubric_alignment) bị bỏ qua MỌI lượt;
issue «🔴 Giám sát đỏ» #20 mở từ 21/09 không bao giờ được đóng dù hai lượt sau đã xanh; cron 00:00 UTC trúng đỉnh tải (trễ 3,9–5,4 giờ).
Kiểm bằng văn bản (không phụ thuộc PyYAML — runner trần chỉ có thư viện chuẩn)."""
from __future__ import annotations

import re
from pathlib import Path

TEP = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "giam-sat-dinh-ky.yml"


def _doc() -> str:
    return TEP.read_text(encoding="utf-8")


def _buoc(ten_chua: str) -> str:
    """Văn bản của MỘT bước (từ dòng `- name:` chứa chuỗi tới bước kế tiếp)."""
    khoi = re.split(r"(?m)^      - ", _doc())
    for k in khoi:
        if k.startswith("name:") and ten_chua in k.splitlines()[0]:
            return k
    raise AssertionError(f"không thấy bước «{ten_chua}»")


def _thu_tu() -> list[str]:
    return [m.group(1) for m in re.finditer(r"(?m)^      - name: (.+)$", _doc())]


def test_lay_repo_anh_em_khong_phu_thuoc_secret():
    b = _buoc("Lấy repo anh em")
    assert not re.search(r"(?m)^\s+if:\s*env\.SIBLING_TOKEN", b), "bước lấy repo anh em lại chỉ chạy khi có secret ⇒ 3 verifier bị bỏ qua mọi lượt"
    assert "repository: drluanbv175/medical-ebm-automation" in b
    assert "github.token" in b, "repo công khai: phải có token mặc định làm lối lùi khi không có secret"
    assert "SIBLING_TOKEN" in b, "repo chuyển riêng tư thì secret vẫn phải được dùng"


def test_lay_repo_anh_em_that_bai_khong_lam_do_nhung_phai_canh_bao():
    assert re.search(r"(?m)^        continue-on-error:\s*true", _buoc("Lấy repo anh em"))
    c = _buoc("Cảnh báo — không lấy được repo anh em")
    assert "steps.anh_em.outcome" in c and "::warning" in c and "BỎ QUA" in c, "bỏ qua không được im lặng"


def test_11_verifier_chay_truoc_khi_co_repo_anh_em():
    ds = _thu_tu()
    i11 = next(i for i, t in enumerate(ds) if t.startswith("11 verifier"))
    iae = next(i for i, t in enumerate(ds) if t.startswith("Lấy repo anh em"))
    i3 = next(i for i, t in enumerate(ds) if t.startswith("3 verifier"))
    assert i11 < iae < i3, "11 verifier phải đo trên BẢN SAO TRẦN; 3 verifier phải sau khi có repo anh em"


def test_ba_verifier_van_chay_theo_hashfiles_khong_theo_secret():
    b = _buoc("3 verifier cần repo anh em")
    assert "hashFiles('medical-ebm-automation/tools/audit_research_gates.py')" in b
    for t in ("verify_research_gate_contracts", "verify_controlled_research_automation", "verify_lessons_rubric_alignment"):
        assert t in b


def test_luot_xanh_tu_dong_dong_issue_giam_sat_cu():
    b = _buoc("Tự đóng issue giám sát cũ")
    assert re.search(r"(?m)^        if:\s*success\(\)", b) and "gh issue close" in b and "--label giam-sat" in b
    assert "permissions:" in _doc() and re.search(r"(?m)^  issues:\s*write", _doc()), "đóng issue cần quyền issues: write"


def test_bao_dong_khi_do_van_con():
    b = _buoc("Báo động khi đỏ")
    assert re.search(r"(?m)^        if:\s*failure\(\)", b) and "gh issue create" in b


def test_cron_khong_o_dinh_tai_00_00_utc():
    cron = re.findall(r'(?m)^\s+- cron:\s*"([^"]+)"', _doc())
    assert len(cron) == 2, cron
    for c in cron:
        phut, gio = c.split()[:2]
        assert not (phut == "0" and gio == "0"), f"cron {c!r} trúng đỉnh tải 00:00 UTC (đo: trễ 3,9–5,4 giờ)"


def test_hanh_dong_van_ghim_sha_khong_ghim_the():
    dung = re.findall(r"(?m)^\s+(?:- )?uses:\s*(\S+)", _doc())   # có cả dạng `- uses:` (đầu bước) lẫn `uses:` (trong bước đặt tên)
    assert len(dung) >= 3, dung
    for u in dung:
        assert re.search(r"@[0-9a-f]{40}$", u), f"hành động không ghim SHA: {u}"
