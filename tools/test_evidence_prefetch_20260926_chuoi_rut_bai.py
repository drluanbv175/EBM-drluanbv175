"""Hồi quy #14 (26/09/2026): biên lai trích dẫn của control plane không được ghi
``complete=True`` khi chuỗi rút bài 3 tầng (tool A12 canonical) KHÔNG chạy trọn.

Trước bản vá: đường tool A12 ghép cứng ``ROOT/medical-ebm-automation/...`` (chỉ bố cục
LỒNG) nên trên phiên Cloud (repo y khoa là ANH EM) biên lai lùi về MỘT truy vấn pubtype
PubMed mà vẫn ghi ``complete=True``; A12 chạy mà thiếu một PMID cũng cho ``complete=True``.

Ngoại tuyến hoàn toàn: mạng được mock (``_request_bytes``), tool A12 giả là một script
Python in JSON cố định trong ``tmp_path``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from orchestrator import evidence_prefetch as EP  # noqa: E402

PMID = "9500320"
PUBMED_XML = f"""<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>{PMID}</PMID>
<Article><Journal><JournalIssue><PubDate><Year>1998</Year></PubDate></JournalIssue>
<Title>Lancet</Title></Journal><ArticleTitle>Synthetic fixture title.</ArticleTitle>
<AuthorList><Author><LastName>Fixture</LastName><Initials>A</Initials></Author></AuthorList>
<PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList>
</Article></MedlineCitation><PubmedData><ArticleIdList>
<ArticleId IdType="doi">10.1016/fixture.0001</ArticleId>
</ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>""".encode()
CROSSREF = {
    "message": {
        "DOI": "10.1016/fixture.0001", "title": ["Synthetic fixture title."],
        "container-title": ["Lancet"], "author": [], "type": "journal-article",
        "publisher": "Fixture",
    }
}


def _mang_gia(url: str, **_kw) -> bytes:
    """Mạng giả: PubMed efetch/esearch (không cờ) + Crossref."""
    if "efetch.fcgi" in url:
        return PUBMED_XML
    if "esearch.fcgi" in url:
        return json.dumps({"esearchresult": {"idlist": []}}).encode()
    return json.dumps(CROSSREF).encode()


@pytest.fixture
def mang(monkeypatch):
    monkeypatch.setattr(EP, "_request_bytes", _mang_gia)


def _dung_a12_gia(repo_y_khoa: Path, ket_qua: dict) -> Path:
    """Dựng tools/check_citation_retraction.py giả in đúng JSON `ket_qua`."""
    tool = repo_y_khoa / "tools" / "check_citation_retraction.py"
    tool.parent.mkdir(parents=True, exist_ok=True)
    tool.write_text("print(" + repr(json.dumps(ket_qua)) + ")\n", encoding="utf-8", newline="\n")
    return tool


# ---------------------------------------------------------------- (a) dò đường
def test_do_duoc_tool_a12_o_bo_cuc_anh_em(tmp_path):
    root = tmp_path / "EBM-drluanbv175"
    root.mkdir()
    tool = _dung_a12_gia(tmp_path / "medical-ebm-automation", {})
    assert EP._canonical_retraction_tool(root) == tool


def test_uu_tien_bo_cuc_long_khi_ca_hai_co(tmp_path):
    root = tmp_path / "EBM-drluanbv175"
    long_ = _dung_a12_gia(root / "medical-ebm-automation", {})
    _dung_a12_gia(tmp_path / "medical-ebm-automation", {})
    assert EP._canonical_retraction_tool(root) == long_


def test_khong_co_a12_o_dau_ca_thi_bao_thieu_khong_goi_subprocess(tmp_path, monkeypatch):
    root = tmp_path / "EBM-drluanbv175"
    root.mkdir()

    def cam_goi(*_a, **_k):  # pragma: no cover — chạy tới đây là lỗi
        raise AssertionError("không được gọi subprocess khi tool vắng")

    monkeypatch.setattr(EP.subprocess, "run", cam_goi)
    assert EP._canonical_retraction_results([PMID], root) == ({}, "không tìm thấy tool A12 canonical")


def test_chay_dung_tool_anh_em_voi_cwd_repo_y_khoa(tmp_path):
    root = tmp_path / "EBM-drluanbv175"
    root.mkdir()
    y_khoa = tmp_path / "medical-ebm-automation"
    _dung_a12_gia(y_khoa, {PMID: {"status": "retracted", "source": "fixture"}})
    ket, loi = EP._canonical_retraction_results([PMID], root)
    assert loi == ""
    assert ket == {PMID: {"status": "retracted", "source": "fixture"}}


# ------------------------------------------------ (b)(c) complete theo chuỗi 3 tầng
def test_a12_vang_thi_complete_false_du_rest_khong_co_co(mang, monkeypatch):
    monkeypatch.setattr(
        EP, "_canonical_retraction_results",
        lambda pmids, root=None: ({}, "không tìm thấy tool A12 canonical"),
    )
    rec = EP.prefetch_citation_receipts("kiem-chung-trich-dan", f"PMID {PMID}")
    assert rec["errors"] == []
    assert rec["complete"] is False
    assert rec["retraction_chain_complete"] is False
    row = rec["records"][0]
    assert row["retraction_chain_complete"] is False
    # Nhãn trung thực của bản lùi giữ nguyên — không đổi sang "ok"/"chưa bị rút".
    assert row["retraction_check"]["status"] == "not_flagged_by_pubmed_query"


def test_a12_chay_nhung_thieu_pmid_thi_complete_false(mang, monkeypatch):
    monkeypatch.setattr(
        EP, "_canonical_retraction_results",
        lambda pmids, root=None: ({"11111111": {"status": "ok"}}, ""),
    )
    rec = EP.prefetch_citation_receipts("kiem-chung-trich-dan", f"PMID {PMID}")
    assert rec["complete"] is False
    assert rec["retraction_chain_complete"] is False
    assert any("không trả kết quả cho PMID này" in w["warning"] for w in rec["warnings"])


@pytest.mark.parametrize(
    "status", ["unresolved", "unknown_fetch_error", "unknown_mock_or_no_email", "rate_limited", None],
)
def test_a12_trang_thai_khong_ket_luan_thi_complete_false(mang, monkeypatch, status):
    monkeypatch.setattr(
        EP, "_canonical_retraction_results",
        lambda pmids, root=None: ({PMID: {"status": status}}, ""),
    )
    rec = EP.prefetch_citation_receipts("kiem-chung-trich-dan", f"PMID {PMID}")
    assert rec["complete"] is False
    assert rec["records"][0]["retraction_chain_complete"] is False
    assert any(e["source"] == "A12 retraction chain" for e in rec["errors"])


@pytest.mark.parametrize("status", ["ok", "retracted", "expression_of_concern"])
def test_a12_ket_luan_duoc_thi_chuoi_tron(mang, monkeypatch, status):
    monkeypatch.setattr(
        EP, "_canonical_retraction_results",
        lambda pmids, root=None: ({PMID: {"status": status}}, ""),
    )
    rec = EP.prefetch_citation_receipts("kiem-chung-trich-dan", f"PMID {PMID}")
    assert rec["retraction_chain_complete"] is True
    assert rec["complete"] is True
    assert rec["records"][0]["retraction_check"]["status"] == status


def test_hai_pmid_mot_thieu_a12_thi_complete_false(mang, monkeypatch):
    monkeypatch.setattr(
        EP, "_canonical_retraction_results",
        lambda pmids, root=None: ({PMID: {"status": "ok"}}, ""),
    )
    rec = EP.prefetch_citation_receipts("kiem-chung-trich-dan", f"PMID {PMID} và PMID 22222222")
    co = {r["identifier"]: r["retraction_chain_complete"] for r in rec["records"]}
    assert co == {f"PMID:{PMID}": True, "PMID:22222222": False}
    assert rec["complete"] is False


def test_chi_co_doi_thi_ghi_chua_kiem_rut_bai_va_complete_false(mang, monkeypatch):
    monkeypatch.setattr(
        EP, "_canonical_retraction_results",
        lambda pmids, root=None: ({}, "không tìm thấy tool A12 canonical"),
    )
    rec = EP.prefetch_citation_receipts("kiem-chung-trich-dan", "DOI 10.1016/fixture.0001")
    assert rec["records"], rec
    row = rec["records"][0]
    assert row["identifier"].startswith("DOI:")
    assert row["retraction_chain_complete"] is False
    assert row["retraction_check"]["status"] == "not_checked"
    assert rec["complete"] is False


# -------------------------------------------------- đầu–cuối trên bố cục anh em
def test_dau_cuoi_bo_cuc_anh_em_chay_a12_that(mang, monkeypatch, tmp_path):
    """ROOT thay bằng repo gốc trong tmp; repo y khoa ANH EM có A12 giả báo retracted."""
    root = tmp_path / "EBM-drluanbv175"
    root.mkdir()
    _dung_a12_gia(tmp_path / "medical-ebm-automation", {PMID: {"status": "retracted"}})
    monkeypatch.setattr(EP, "ROOT", root)
    rec = EP.prefetch_citation_receipts("kiem-chung-trich-dan", f"PMID {PMID}")
    row = rec["records"][0]
    assert row["retraction_check"]["status"] == "retracted"
    assert "check_citation_retraction.py" in row["retraction_check"]["checked_with"]
    assert "citation-retraction" in rec["executed_tools"]
    assert rec["retraction_chain_complete"] is True


def test_dau_cuoi_khong_co_repo_y_khoa_thi_complete_false(mang, monkeypatch, tmp_path):
    root = tmp_path / "EBM-drluanbv175"
    root.mkdir()
    monkeypatch.setattr(EP, "ROOT", root)
    rec = EP.prefetch_citation_receipts("kiem-chung-trich-dan", f"PMID {PMID}")
    assert rec["complete"] is False
    assert rec["retraction_chain_complete"] is False
    assert "citation-retraction" not in rec["executed_tools"]
