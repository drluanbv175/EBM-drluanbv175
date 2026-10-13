# -*- coding: utf-8 -*-
"""Đường dự phòng PMC Cloud S3 của `gom_toan_van_dashboard.py` (13/10/2026) — bản thảo tác giả NIH khi NCBI chặn IP.

Ca thật: PMID 22591294 (Ray, NEJM 2012, azithromycin), PMC3374857, NIHMS381524. NCBI chặn IP ⇒ tầng PMC đổi PMID→PMCID qua
Europe PMC, Europe PMC ghi `isOpenAccess="N"` cho bản thảo tác giả ⇒ `tai_jats` trả «khong_oa_epmc», không lưu gì — dù bucket
`pmc-oa-opendata` có `PMC3374857.1/` với `license_code: "TDM"`. Ngoại tuyến hoàn toàn: bucket là một từ điển URL → byte.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("_gom_pmc_s3", REPO / "tools" / "gom_toan_van_dashboard.py")
g = importlib.util.module_from_spec(sp)
sp.loader.exec_module(g)

S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
PMC = "3374857"
# Đầu tệp giống bản thật (DOCTYPE JATS, không phải HTML)
JATS = (b'<?xml version="1.0"?>\n<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Archiving and Interchange DTD '
        b'v1.4//EN" "JATS-archivearticle1-4-mathml3.dtd">\n<article article-type="research-article"><front/><body><sec>'
        b"<title>Methods</title><p>Azithromycin</p></sec></body></article>")


def _md5(b: bytes) -> str:
    return hashlib.md5(b, usedforsecurity=False).hexdigest()


def _danh_muc(pmcid: str, phien_ban: list[str], cat: bool = False) -> bytes:
    tien_to = "".join(f"<CommonPrefixes><Prefix>{p}</Prefix></CommonPrefixes>" for p in phien_ban)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
            f"<Name>pmc-oa-opendata</Name><Prefix>PMC{pmcid}.</Prefix><KeyCount>{len(phien_ban)}</KeyCount>"
            f"<MaxKeys>1000</MaxKeys><Delimiter>/</Delimiter><IsTruncated>{'true' if cat else 'false'}</IsTruncated>"
            f"{tien_to}</ListBucketResult>").encode()


def _meta(n: int = 1, *, pmcid: str = PMC, license_code="TDM", rut=False, ban_thao=True, md5: str | None = None,
          xml_url: str | None = None, bo: tuple[str, ...] = ()) -> dict:
    """Siêu dữ liệu đúng khuôn tệp thật `PMC3374857.1.json` (đọc 13/10/2026)."""
    md = {"pmcid": f"PMC{pmcid}", "version": n, "pmid": 22591294, "doi": "10.1056/NEJMoa1003833", "mid": "NIHMS381524",
          "is_pmc_openaccess": False, "is_manuscript": ban_thao, "is_historical_ocr": False, "is_retracted": rut,
          "license_code": license_code,
          "xml_url": xml_url or f"s3://pmc-oa-opendata/PMC{pmcid}.{n}/PMC{pmcid}.{n}.xml?md5={md5 or _md5(JATS)}"}
    for k in bo:
        md.pop(k, None)
    return md


def _bucket(pmcid: str = PMC, ban: dict[int, tuple[dict, bytes | Exception]] | None = None,
            danh_muc: bytes | Exception | None = None):
    """`lay` giả: danh mục + JSON + XML từng phiên bản; URL lạ ⇒ OSError (mạng không tới). Trả (lay, danh sách URL đã gọi)."""
    ban = {1: (_meta(), JATS)} if ban is None else ban
    kho: dict[str, bytes | Exception] = {
        f"{S3}/?list-type=2&prefix=PMC{pmcid}.&delimiter=/":
            danh_muc if danh_muc is not None else _danh_muc(pmcid, [f"PMC{pmcid}.{n}/" for n in ban])}
    for n, (md, xml) in ban.items():
        kho[f"{S3}/PMC{pmcid}.{n}/PMC{pmcid}.{n}.json"] = json.dumps(md).encode()
        kho[f"{S3}/PMC{pmcid}.{n}/PMC{pmcid}.{n}.xml"] = xml
    goi: list[str] = []

    def lay(url, timeout=60):
        goi.append(url)
        v = kho.get(url, OSError(f"không mô phỏng: {url}"))
        if isinstance(v, Exception):
            raise v
        return v
    return lay, goi


def _xml_da_goi(goi: list[str]) -> list[str]:
    return [u for u in goi if u.endswith(".xml")]


def _gom_ncbi():
    goi: list[str] = []

    def tai_toan_van(pmcid):
        goi.append(pmcid)
        return JATS
    return types.SimpleNamespace(tai_toan_van=tai_toan_van, lien_ket_pmc=lambda pmids: {}), goi


# ── Nhánh 1: lấy được ────────────────────────────────────────────────────────────────────────────────────────────────


def test_ncbi_chan_va_epmc_khong_oa_thi_lay_ban_thao_tdm_tu_s3():
    gom, goi_ncbi = _gom_ncbi()
    lay, goi = _bucket()
    assert g.tai_jats(gom, PMC, False, {"ncbi_chan": True}, lay=lay) == (JATS, "ok")
    assert goi[0] == f"{S3}/?list-type=2&prefix=PMC{PMC}.&delimiter=/", "phải tra DANH MỤC trước, không đoán phiên bản"
    assert goi_ncbi == [], "NCBI đang chặn — không gọi lại"


def test_ncbi_khong_chan_giu_hanh_vi_cu_khong_goi_s3():
    gom, goi_ncbi = _gom_ncbi()
    lay, goi = _bucket()
    assert g.tai_jats(gom, PMC, False, {}, lay=lay) == (None, "khong_oa_epmc")
    assert goi == [] and goi_ncbi == []


def test_phien_ban_tra_tu_danh_muc_khong_doan_ban_1():
    lay, goi = _bucket(ban={2: (_meta(2), JATS)})
    assert g.tai_jats_pmc_s3(PMC, lay) == (JATS, "ok")
    assert not any(f"PMC{PMC}.1/" in u for u in goi), "danh mục chỉ có .2 — không được gọi .1"


def test_danh_muc_khong_lan_pmcid_dai_hon():
    """Tiền tố «PMC3374857.» có dấu chấm; một mục lạ «PMC33748570.1/» (nếu có) không phải phiên bản của bài này."""
    lay, _ = _bucket(ban={}, danh_muc=_danh_muc(PMC, [f"PMC{PMC}0.1/"]))
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "khong_oa_epmc")


@pytest.mark.parametrize("lic", ["TDM", "tdm", "CC BY", "CC BY-NC-ND", "CC0", "cc_by-nc_license"])
def test_giay_phep_cho_phep(lic):
    assert g.giay_phep_pmc_s3_cho_phep(lic)


def test_nhieu_ban_uu_tien_ban_cong_bo_khong_theo_so_lon_nhat():
    cong_bo = JATS.replace(b"Azithromycin", b"Ban cong bo")
    lay, _ = _bucket(ban={1: (_meta(1, license_code="CC BY", ban_thao=False, md5=_md5(cong_bo)), cong_bo),
                          2: (_meta(2), JATS)})
    assert g.tai_jats_pmc_s3(PMC, lay) == (cong_bo, "ok"), "số phiên bản lớn hơn KHÔNG có nghĩa là bản nên lấy"


# ── Nhánh 2: giấy phép không cho phép ⇒ «khong_oa_epmc» như cũ ──────────────────────────────────────────────────────────


@pytest.mark.parametrize("lic", ["", None, "NO-CC CODE", "Other", "ALL RIGHTS RESERVED"])
def test_giay_phep_khong_cho_phep_khong_tai_xml(lic):
    lay, goi = _bucket(ban={1: (_meta(license_code=lic), JATS)})
    assert g.tai_jats(_gom_ncbi()[0], PMC, False, {"ncbi_chan": True}, lay=lay) == (None, "khong_oa_epmc")
    assert _xml_da_goi(goi) == [], "giấy phép không cho phép — không mở tệp XML"


def test_bai_khong_co_trong_bucket_la_khong_oa_epmc():
    lay, _ = _bucket(ban={})
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "khong_oa_epmc")


# ── Nhánh 3: is_retracted ───────────────────────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("rut", [True, "yes"])
def test_da_rut_khong_luu(rut):
    lay, goi = _bucket(ban={1: (_meta(rut=rut), JATS)})
    assert g.tai_jats(_gom_ncbi()[0], PMC, False, {"ncbi_chan": True}, lay=lay) == (None, "rut_bai_pmc")
    assert _xml_da_goi(goi) == []


def test_mot_phien_ban_da_rut_thi_khong_luu_ban_nao():
    lay, goi = _bucket(ban={1: (_meta(1, license_code="CC BY", ban_thao=False), JATS), 2: (_meta(2, rut=True), JATS)})
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "rut_bai_pmc") and _xml_da_goi(goi) == []


@pytest.mark.parametrize("hong", ["thieu", None, "unknown"])
def test_co_rut_bai_khong_ro_la_khong_biet_khong_phai_chua_rut(hong):
    md = _meta(bo=("is_retracted",)) if hong == "thieu" else _meta(rut=hong)
    lay, goi = _bucket(ban={1: (md, JATS)})
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "loi") and _xml_da_goi(goi) == []


# ── Nhánh 4: md5 lệch ───────────────────────────────────────────────────────────────────────────────────────────────────


def test_md5_lech_khong_luu_va_la_loi():
    lay, goi = _bucket(ban={1: (_meta(md5="0" * 32), JATS)})
    assert g.tai_jats(_gom_ncbi()[0], PMC, False, {"ncbi_chan": True}, lay=lay) == (None, "loi")
    assert len(_xml_da_goi(goi)) == 1, "đã tải tệp nhưng md5 lệch ⇒ không lưu"


@pytest.mark.parametrize("url", [
    f"s3://pmc-oa-opendata/PMC{PMC}.1/PMC{PMC}.1.xml",                       # thiếu md5 — không kiểm được
    f"s3://bucket-khac/PMC{PMC}.1/PMC{PMC}.1.xml?md5={'a' * 32}",            # bucket khác
    f"s3://pmc-oa-opendata/PMC999.1/PMC999.1.xml?md5={'a' * 32}",            # bài khác
    f"https://vi-du.invalid/PMC{PMC}.1.xml?md5={'a' * 32}",                  # máy chủ khác
])
def test_xml_url_la_khong_tai(url):
    lay, goi = _bucket(ban={1: (_meta(xml_url=url), JATS)})
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "loi") and _xml_da_goi(goi) == []


# ── Lỗi mạng / dữ liệu lạ ⇒ «loi» (lượt sau thử lại) ────────────────────────────────────────────────────────────────────


def test_loi_mang_o_danh_muc_json_hay_xml_la_loi():
    lay, _ = _bucket(danh_muc=OSError("hết giờ"))
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "loi")
    lay2, _ = _bucket()

    def lay_json_chet(url, timeout=60):
        if url.endswith(".json"):
            raise OSError("500")
        return lay2(url)
    assert g.tai_jats_pmc_s3(PMC, lay_json_chet) == (None, "loi")
    lay3, _ = _bucket(ban={1: (_meta(), OSError("đứt kết nối"))})
    assert g.tai_jats_pmc_s3(PMC, lay3) == (None, "loi")


@pytest.mark.parametrize("danh_muc", [_danh_muc(PMC, [f"PMC{PMC}.1/"], cat=True),
                                      b"<!DOCTYPE html><html><body>Access Denied</body></html>"],
                         ids=["danh-muc-bi-cat", "khong-phai-danh-muc"])
def test_danh_muc_khong_tin_duoc_la_loi_khong_phai_khong_co(danh_muc):
    lay, _ = _bucket(danh_muc=danh_muc)
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "loi")


@pytest.mark.parametrize("khoa, gia_tri", [("pmcid", "PMC999"), ("version", 2)])
def test_sieu_du_lieu_lech_khoa_la_loi(khoa, gia_tri):
    """Chỉ lệch MỘT khoá, `xml_url` vẫn đúng bài — để chốt khoá được kiểm riêng, không nhờ chốt `xml_url` đỡ hộ."""
    md = _meta()
    md[khoa] = gia_tri
    lay, goi = _bucket(ban={1: (md, JATS)})
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "loi") and _xml_da_goi(goi) == []


def test_md5_khop_nhung_khong_phai_jats_la_loi():
    html = b"<!DOCTYPE html><html><body><article>trang</article></body></html>"
    lay, _ = _bucket(ban={1: (_meta(md5=_md5(html)), html)})
    assert g.tai_jats_pmc_s3(PMC, lay) == (None, "loi")


# ── Đầu–cuối qua main() ─────────────────────────────────────────────────────────────────────────────────────────────────


def _main(monkeypatch, tmp_path, argv, lay):
    def elink_bi_chan(pmids):   # NCBI trả trang chặn HTML ⇒ JSONDecodeError, như đo thật 11/10/2026
        raise json.JSONDecodeError("x", "<html>", 0)
    gom = types.SimpleNamespace(tai_toan_van=lambda p: JATS, lien_ket_pmc=elink_bi_chan)
    monkeypatch.setattr(g, "KHO", tmp_path)
    monkeypatch.setattr(g, "_nap_gom", lambda: gom)
    monkeypatch.setattr(g, "_lay", lay)
    monkeypatch.setattr(g.time, "sleep", lambda s: None)
    monkeypatch.setattr(sys, "argv", ["gom_toan_van_dashboard.py", *argv])
    return g.main()


def _lay_epmc_va_s3(ket_qua: list[dict], s3):
    def lay(url, timeout=60):
        if "/search?" in url:
            return json.dumps({"resultList": {"result": ket_qua}}).encode()
        return s3(url)
    return lay


def test_main_ncbi_chan_luu_ban_thao_tac_gia_va_khong_ghi_so(monkeypatch, tmp_path):
    s3, _ = _bucket()
    kq = [{"pmid": "22591294", "pmcid": f"PMC{PMC}", "isOpenAccess": "N"}]
    assert _main(monkeypatch, tmp_path, ["--pmid", "22591294"], _lay_epmc_va_s3(kq, s3)) == 0
    assert (tmp_path / f"PMID-22591294_PMC{PMC}.xml").read_bytes() == JATS
    so = (tmp_path / "khong-oa.txt").read_text(encoding="utf-8")
    assert "22591294" not in so


def test_main_bai_da_rut_bao_trong_do_phu_va_khong_luu(monkeypatch, tmp_path):
    s3, _ = _bucket(ban={1: (_meta(rut=True), JATS)})
    kq = [{"pmid": "22591294", "pmcid": f"PMC{PMC}", "isOpenAccess": "N"}]
    assert _main(monkeypatch, tmp_path, ["--pmid", "22591294"], _lay_epmc_va_s3(kq, s3)) == 0
    assert not list(tmp_path.glob("PMID-22591294_*"))
    assert "ĐÃ RÚT" in (tmp_path / "DO-PHU-OA.md").read_text(encoding="utf-8")
