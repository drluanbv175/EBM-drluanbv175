"""Hồi quy 24/09/2026 — `nap_nen_rut_bai_cloud.py`: phiên Cloud tự nạp nền Retraction Watch.
Không gọi mạng: subprocess tải được thay bằng kịch bản; gốc engine là tmp."""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]


def _nap():
    spec = importlib.util.spec_from_file_location("nrb_test", GOC / "tools" / "nap_nen_rut_bai_cloud.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ghi_nen(mea: Path, so_dong: int) -> None:
    d = mea / "data" / "retraction_watch"
    d.mkdir(parents=True, exist_ok=True)
    (d / "retraction_watch.csv").write_text("h\n" + "x\n" * so_dong, encoding="utf-8", newline="\n")


@pytest.fixture()
def moi(monkeypatch, tmp_path):
    mod = _nap()
    mea = tmp_path / "medical-ebm-automation"
    (mea / "tools").mkdir(parents=True)
    monkeypatch.setattr(mod, "goc_engine", lambda: mea)
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    goi = []

    def gia_run(cmd, **kw):
        goi.append(cmd)
        _ghi_nen(mea, 2000)
        return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(mod.subprocess, "run", gia_run)
    return mod, mea, goi


def _chay(mod, monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["nap_nen_rut_bai_cloud", *argv])
    return mod.main()


def test_may_that_khong_lam_gi(moi, monkeypatch):
    mod, _mea, goi = moi
    monkeypatch.delenv("CLAUDE_CODE_REMOTE")
    assert _chay(mod, monkeypatch, "--ap-dung") == 0 and goi == []


def test_cloud_thieu_nen_thi_kiem_bao_1(moi, monkeypatch):
    mod, _mea, goi = moi
    assert _chay(mod, monkeypatch, "--im-khi-on") == 1 and goi == []


def test_cloud_ap_dung_tai_qua_cong_cu_engine(moi, monkeypatch):
    mod, mea, goi = moi
    assert _chay(mod, monkeypatch, "--ap-dung") == 0
    assert goi and goi[0][1].endswith("tai_retraction_watch.py") and "tu-dong" in goi[0]
    assert mod.nen_san_sang(mea)


def test_nen_bi_cat_cut_khong_duoc_coi_la_san_sang(moi, monkeypatch):
    mod, mea, _goi = moi
    _ghi_nen(mea, 10)
    assert not mod.nen_san_sang(mea)
    assert _chay(mod, monkeypatch, "--im-khi-on") == 1


def test_tai_that_bai_bao_2(moi, monkeypatch):
    mod, _mea, _goi = moi
    monkeypatch.setattr(mod.subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(returncode=2, stdout="", stderr="mất mạng"))
    assert _chay(mod, monkeypatch, "--ap-dung") == 2


def test_da_noi_vao_tu_sua_chua_pham_vi_cloud():
    spec = importlib.util.spec_from_file_location("tsc_test", GOC / "tools" / "tu_sua_chua.py")
    tsc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tsc)
    muc = [v for v in tsc.VIEC_MAY if "nap_nen_rut_bai_cloud.py" in " ".join(map(str, v[1]))]
    assert len(muc) == 1 and muc[0][3] is True and muc[0][2] and "--ap-dung" in muc[0][2]
