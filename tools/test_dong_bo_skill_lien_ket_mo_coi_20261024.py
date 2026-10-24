#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `don_lien_ket_mo_coi()` trong dong_bo_skill_claude_codex.py — ngoại tuyến (24/10/2026).

Bối cảnh: bác sĩ quyết gỡ plugin aipoch, skill nguồn `sync/skills/dieu-phoi-aipoch` bị gỡ, nhưng liên kết
`~/.claude/skills/dieu-phoi-aipoch` và `~/.codex/skills/dieu-phoi-aipoch` vẫn còn (treo) — `ensure_link` chỉ đi
theo skill NGUỒN đang có nên không bao giờ dọn nó; BH44 (`kiem_dieu_phoi` ③ «skill runtime KHÔNG CÓ NGUỒN») đỏ.
Ca thử kiểm HÀNH VI: chỉ gỡ liên kết treo trỏ VÀO nguồn; thư mục thật, liên kết còn sống, liên kết treo trỏ nơi
khác đều giữ nguyên; chạy khô chỉ báo. Liên kết dựng bằng `LK.tao` (symlink trên Mac/Linux, junction trên Windows).
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import dong_bo_skill_claude_codex as DB  # noqa: E402
import lien_ket_da_nen as LK  # noqa: E402


def _skill(goc: Path, ten: str) -> Path:
    thu_muc = goc / ten
    thu_muc.mkdir(parents=True)
    (thu_muc / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    return thu_muc


def _runtime(tmp_path: Path) -> tuple[Path, Path, Path]:
    """nguon/ có skill «con-song»; runtime/ có: liên kết sống, liên kết treo vào nguồn (mồ côi),
    liên kết treo trỏ NGOÀI nguồn, và một thư mục thật."""
    nguon = tmp_path / "sync" / "skills"
    song = _skill(nguon, "con-song")
    da_go = _skill(nguon, "da-go")
    ngoai = _skill(tmp_path / "noi-khac", "ngoai-nguon")
    runtime = tmp_path / ".claude" / "skills"
    runtime.mkdir(parents=True)
    LK.tao(song, runtime / "con-song")
    LK.tao(da_go, runtime / "da-go")
    LK.tao(ngoai, runtime / "ngoai-nguon")
    (runtime / "that").mkdir()
    for thu_muc in (da_go, ngoai):  # skill nguồn bị gỡ ⇒ hai liên kết thành treo
        (thu_muc / "SKILL.md").unlink()
        thu_muc.rmdir()
    return nguon, runtime, song


def test_chay_kho_chi_bao_lien_ket_mo_coi_khong_go(tmp_path):
    nguon, runtime, _ = _runtime(tmp_path)
    kq = DB.don_lien_ket_mo_coi(nguon, runtime, apply=False)
    assert [(r.skill, r.status) for r in kq] == [("da-go", "MO_COI")]
    assert LK.la_lien_ket(runtime / "da-go")


def test_ap_dung_chi_go_lien_ket_treo_tro_vao_nguon(tmp_path):
    nguon, runtime, song = _runtime(tmp_path)
    kq = DB.don_lien_ket_mo_coi(nguon, runtime, apply=True)
    assert [(r.skill, r.status) for r in kq] == [("da-go", "DA_GO")]
    assert not LK.la_lien_ket(runtime / "da-go") and not (runtime / "da-go").exists()
    assert LK.tro_dung(runtime / "con-song", song), "liên kết còn sống phải giữ"
    assert LK.la_lien_ket(runtime / "ngoai-nguon"), "liên kết treo trỏ NGOÀI nguồn không thuộc công cụ này"
    assert (runtime / "that").is_dir()


def test_runtime_vang_thi_khong_loi(tmp_path):
    assert DB.don_lien_ket_mo_coi(tmp_path / "sync" / "skills", tmp_path / "khong-co", apply=True) == []
