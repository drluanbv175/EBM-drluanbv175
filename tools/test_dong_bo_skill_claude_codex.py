from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dong_bo_skill_claude_codex as S  # noqa: E402
import lien_ket_da_nen as LK  # noqa: E402


def _make_source(tmp_path, name="scientific-writing"):
    source = tmp_path / "sync-skills" / name
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    return source


def test_ensure_link_dry_run_reports_conflict_without_touching_symlink(tmp_path):
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    stray = tmp_path / "nowhere"
    stray.mkdir()
    (destination / source.name).symlink_to(stray, target_is_directory=True)

    result = S.ensure_link(source, destination, apply=False)

    assert result.status == "XUNG_DOT"
    assert LK.dich_cua(destination / source.name) == stray.resolve()


def test_ensure_link_self_heals_symlink_pointing_to_wrong_real_dir(tmp_path):
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    stray = tmp_path / "somewhere-else"
    stray.mkdir()
    (destination / source.name).symlink_to(stray, target_is_directory=True)

    result = S.ensure_link(source, destination, apply=True)

    assert result.status == "DA_NOI"
    assert LK.tro_dung(destination / source.name, source)
    # stray target itself must be untouched -- LK.go() only unlinks the link
    assert stray.is_dir()


def test_ensure_link_self_heals_dangling_symlink(tmp_path):
    """Bug goc: lien ket cu tro toi mot duong dan KHONG con ton tai (repo doi
    cho, OneDrive ghi de). Truoc ban va, nhanh nay tra XUNG_DOT vinh vien du
    da truyen apply=True, vi khong co else-if nao goi LK.go()+LK.tao()."""
    source = _make_source(tmp_path)
    destination = tmp_path / ".codex" / "skills"
    destination.mkdir(parents=True)
    (destination / source.name).symlink_to(tmp_path / "da-bi-xoa" / source.name)

    result = S.ensure_link(source, destination, apply=True)

    assert result.status == "DA_NOI"
    assert LK.tro_dung(destination / source.name, source)


def test_ensure_link_dangling_symlink_apply_false_leaves_it_dangling(tmp_path):
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    target = destination / source.name
    target.symlink_to(tmp_path / "da-bi-xoa" / source.name)

    result = S.ensure_link(source, destination, apply=False)

    assert result.status == "XUNG_DOT"
    assert not target.exists()  # van con treo (broken), khong tu sua
    assert LK.la_lien_ket(target)  # nhung van la mot lien ket, chua bi xoa


def test_ensure_link_self_heal_is_idempotent_on_second_run(tmp_path):
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    (destination / source.name).symlink_to(tmp_path / "da-bi-xoa" / source.name)

    first = S.ensure_link(source, destination, apply=True)
    second = S.ensure_link(source, destination, apply=True)

    assert first.status == "DA_NOI"
    assert second.status == "KHOP"
    assert LK.tro_dung(destination / source.name, source)


def test_ensure_link_self_heal_does_not_create_a_backup(tmp_path):
    """Khac voi nhanh 'target la thu muc that' (co sao luu), tu phuc hoi mot
    lien ket sai KHONG duoc de lai .bak nao -- LK.go() chi go diem noi."""
    source = _make_source(tmp_path)
    destination = tmp_path / ".claude" / "skills"
    destination.mkdir(parents=True)
    (destination / source.name).symlink_to(tmp_path / "da-bi-xoa" / source.name)

    S.ensure_link(source, destination, apply=True)

    assert not (destination.parent / f"{destination.name}-backup").exists()
