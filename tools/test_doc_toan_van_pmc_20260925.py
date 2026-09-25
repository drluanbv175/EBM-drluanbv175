"""Kiểm `tools/doc_toan_van_pmc.py` (25/09/2026) — ngoại tuyến: E-utilities và connector đều giả lập."""
from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "doc_toan_van_pmc.py"
_sp = importlib.util.spec_from_file_location("doc_toan_van_pmc", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


def _gia_eutils(ban_do: dict):
    def get_json(url: str) -> dict:
        for khoa, tra in ban_do.items():
            if khoa in url:
                if isinstance(tra, Exception):
                    raise tra
                return tra
        raise AssertionError(f"URL không mong đợi: {url}")
    return get_json


_ELINK_CO = {"linksets": [{"linksetdbs": [{"linkname": "pubmed_pmc", "links": ["1234567"]}]}]}
_ELINK_KHONG = {"linksets": [{"dbfrom": "pubmed", "ids": ["1"]}]}


def test_phan_giai_ca_ba_loai_dinh_danh():
    assert M.phan_giai_pmcid("pmc42", _gia_eutils({})) == "PMC42"            # không gọi mạng
    assert M.phan_giai_pmcid("111", _gia_eutils({"elink": _ELINK_CO})) == "PMC1234567"
    assert M.phan_giai_pmcid("111", _gia_eutils({"elink": _ELINK_KHONG})) is None
    g = _gia_eutils({"esearch": {"esearchresult": {"idlist": ["111"]}}, "elink": _ELINK_CO})
    assert M.phan_giai_pmcid("10.2337/dc26-S009", g) == "PMC1234567"
    assert M.phan_giai_pmcid("10.1234/x", _gia_eutils({"esearch": {"esearchresult": {"idlist": []}}})) is None


def test_khong_ket_luan_duoc_la_chua_biet_khong_phai_khong_co():
    with pytest.raises(M.ChuaBiet):
        M.phan_giai_pmcid("khong-phai-dinh-danh", _gia_eutils({}))
    with pytest.raises(M.ChuaBiet):
        M.phan_giai_pmcid("111", _gia_eutils({"elink": {"loi": "rate limit"}}))
    with pytest.raises(M.ChuaBiet):
        M.phan_giai_pmcid("10.1234/x", _gia_eutils({"esearch": {"error": "x"}}))


def test_tim_doan_gop_doan_chong_lan_va_khong_phan_biet_hoa_thuong():
    vb = "aaa eGFR 20 bbb EGFR 25 " + "x" * 1000 + " egfr 30"
    ds = M.tim_doan(vb, "egfr", gian=20)
    assert len(ds) == 2                                   # hai lần đầu gần nhau ⇒ gộp
    assert ds[0]["vi_tri"] == 4 and "30" in ds[1]["doan"]
    assert M.tim_doan(vb, "   ") == []


@dataclass
class _Kq:
    thanh_cong: bool
    url_nguon: str = "s3://x"
    van_ban_trich: str | None = None
    ghi_chu: str | None = None
    ghi_chu_ban_quyen: str = "nội bộ"


class _Client:
    def __init__(self, kq):
        self.kq = kq

    def tai_toan_van(self, pmcid):
        return self.kq


def _chay(capsys, kq, dinh_danh="PMC1"):
    rc = M.main([dinh_danh, "--tim", "sglt2", "--json"], client_factory=lambda: _Client(kq),
                get_json=_gia_eutils({}))
    return rc, json.loads(capsys.readouterr().out)


def test_ma_thoat_phan_biet_doc_duoc_khong_co_chua_biet(capsys):
    rc, out = _chay(capsys, _Kq(True, van_ban_trich="Use SGLT2 inhibitors when eGFR >= 20."))
    assert rc == 0 and out["trang_thai"] == "doc_duoc" and out["ket_qua_tim"]["sglt2"]
    rc, out = _chay(capsys, _Kq(False, ghi_chu="PMC1 KHÔNG có trong PMC Open Access Subset (bucket S3)"))
    assert rc == 1 and out["trang_thai"] == "khong_co"
    rc, out = _chay(capsys, _Kq(False, ghi_chu="Không liệt kê được bucket — CHƯA BIẾT"))
    assert rc == 2 and out["trang_thai"] == "chua_biet"


def test_thieu_engine_la_chua_biet(capsys):
    rc = M.main(["PMC1", "--json"], client_factory=lambda: None, get_json=_gia_eutils({}))
    out = json.loads(capsys.readouterr().out)
    assert rc == 2 and out["trang_thai"] == "chua_biet"
    rc = M.main(["111", "--json"], client_factory=lambda: None,
                get_json=_gia_eutils({"elink": M.ChuaBiet("proxy 403")}))
    assert rc == 2
