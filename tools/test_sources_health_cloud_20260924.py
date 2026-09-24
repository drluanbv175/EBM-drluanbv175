"""Hồi quy 24/09/2026 — `sources_health.py` trên phiên Cloud (audit/15 §8).

Đo thật: proxy môi trường Cloud «Trusted» từ chối (CONNECT 403) mọi host API y văn; bản cũ đọc
thành nguồn hỏng và GHI DEGRADED vào sổ tracked `data/sources.json`. Các test không gọi mạng:
`urllib.request.urlopen` được thay bằng kịch bản, sổ là bản sao trong tmp."""
from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]


def _nap():
    spec = importlib.util.spec_from_file_location("sh_cloud_test", GOC / "tools" / "sources_health.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tu_choi(*a, **kw):
    raise urllib.error.URLError(OSError("Tunnel connection failed: 403 Forbidden"))


def _loi_that(*a, **kw):
    raise urllib.error.URLError(OSError("[Errno 111] Connection refused"))


@pytest.fixture()
def sh(monkeypatch, tmp_path):
    mod = _nap()
    so = tmp_path / "sources.json"
    so.write_text(json.dumps({"updated": "2000-01-01", "sources": [
        {"id": "SRC-004", "name": "Crossref", "status": "active", "access": "api",
         "scan_frequency": "weekly", "endpoint_or_url": "https://api.crossref.org/"},
    ]}, ensure_ascii=False), encoding="utf-8", newline="\n")
    monkeypatch.setattr(mod, "SO", so)
    monkeypatch.setattr(mod, "lay_thanh_cong_that", lambda sid: None)
    return mod, so


def _chay(mod, monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["sources_health", *argv])
    return mod.main()


def test_tham_phan_biet_proxy_tu_choi_voi_loi_that(monkeypatch):
    mod = _nap()
    monkeypatch.setattr(mod.urllib.request, "urlopen", _tu_choi)
    assert mod._tham("https://api.crossref.org/works?rows=0") == mod.CHAN_MOI_TRUONG
    monkeypatch.setattr(mod.urllib.request, "urlopen", _loi_that)
    assert mod._tham("https://api.crossref.org/works?rows=0") == mod.LOI


def test_cloud_khong_ghi_so_va_khong_ha_trang_thai(sh, monkeypatch, capsys):
    mod, so = sh
    truoc = so.read_bytes()
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    monkeypatch.setattr(mod.urllib.request, "urlopen", _tu_choi)
    assert _chay(mod, monkeypatch, "--im-khi-on") == 0
    assert so.read_bytes() == truoc, "phiên Cloud không được ghi sổ tracked"
    out = capsys.readouterr().out
    assert "KHÔNG ĐO ĐƯỢC" in out and "SRC-004" in out and "KHÔNG ghi sổ" in out


def test_may_that_bi_proxy_chan_van_ghi_nhung_giu_trang_thai(sh, monkeypatch):
    mod, so = sh
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.setattr(mod.urllib.request, "urlopen", _tu_choi)
    assert _chay(mod, monkeypatch, "--im-khi-on") == 0
    du = json.loads(so.read_text(encoding="utf-8"))
    assert du["sources"][0]["status"] == "active" and du["updated"] != "2000-01-01"


def test_loi_that_van_ha_degraded(sh, monkeypatch):
    mod, so = sh
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.setattr(mod.urllib.request, "urlopen", _loi_that)
    assert _chay(mod, monkeypatch, "--im-khi-on") == 1
    assert json.loads(so.read_text(encoding="utf-8"))["sources"][0]["status"] == "degraded"


def test_khong_ghi_ep_o_may_that(sh, monkeypatch):
    mod, so = sh
    truoc = so.read_bytes()
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    monkeypatch.setattr(mod.urllib.request, "urlopen", _loi_that)
    _chay(mod, monkeypatch, "--khong-ghi", "--im-khi-on")
    assert so.read_bytes() == truoc


def test_nguon_file_engine_phan_giai_qua_duong_goc():
    mod = _nap()
    f = mod._duong_file("medical-ebm-automation/data/retraction_watch/")
    assert f == mod._MEA_GOC / "data/retraction_watch/"
    assert mod._duong_file("EBM-Dashboards/x.json") == mod.GOC / "EBM-Dashboards/x.json"
