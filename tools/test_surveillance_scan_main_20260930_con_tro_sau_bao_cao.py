"""Vá 30/09/2026 — hoàn thiện bản vá «ngày kiểu số» của lượt quét tuần W40 (29/09).

Bản vá 29/09 chỉ chặn ở MỘT nơi tiêu thụ (đo độ trễ). Còn hai thứ chưa sửa:

1. GỐC RỄ: ba làn lấy bản ghi từ engine (Scopus · CORE · dự phòng) chép thẳng `rec.publication_date` — có thể là
   số — vào `Candidate.publication_date: str`. Nay `Candidate` tự ép về chuỗi tại một điểm nghẽn.
2. CẤU TRÚC: con trỏ và dấu «đã trình» của sổ dự phòng được ghi TRƯỚC khi báo cáo tới nơi ⇒ mọi lỗi ở khâu hậu xử
   lý làm mất lượt quét trong khi con trỏ đã nhảy (đúng sự cố 29/09: 47 chủ đề «đã quét» mà không ai thấy ứng viên
   nào, bài dự phòng mang dấu «đã trình» mà chưa ai đọc). Nay: báo cáo tới nơi rồi mới ghi hai thứ đó; riêng mốc leo
   thang (hạn mức tính phí đã tiêu) vẫn ghi ngay.

Offline hoàn toàn: mọi làn mạng bị chặn, watchlist/con trỏ/khoá/sổ dự phòng/alerts đều ở thư mục tạm.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_con_tro_sau_bao_cao_3009", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_con_tro_sau_bao_cao_3009"] = S  # @dataclass tra sys.modules lúc dựng lớp — đăng ký TRƯỚC exec
_sp.loader.exec_module(S)


# ---------- 1. Gốc rễ: ngày công bố luôn là chuỗi ở biên ứng viên ----------

@pytest.mark.parametrize("dau_vao, mong_doi", [(2026, "2026"), (None, ""), ("2026 Sep 20", "2026 Sep 20"), ("", "")])
def test_candidate_ep_ngay_ve_chuoi(dau_vao, mong_doi):
    c = S.Candidate("1", dau_vao, "Bài", "https://x")
    assert c.publication_date == mong_doi and isinstance(c.publication_date, str)


def test_replace_cung_di_qua_diem_nghen():
    c = replace(S.Candidate("1", "2026", "Bài", "https://x"), publication_date=2025)
    assert c.publication_date == "2025"


def _ban_ghi_engine(**kw):
    """Bản ghi kiểu `RawRecord` của engine với ngày chỉ có NĂM kiểu số (đúng thủ phạm W40)."""
    goc = dict(pmid=None, doi="10.1/x", url=None, title="Bài từ engine", publication_date=2026,
               journal_or_organization="Tạp chí", source="consensus")
    return SimpleNamespace(**{**goc, **kw})


def _nha_may(ban_ghi):
    return lambda: SimpleNamespace(use_mock=True, search=lambda *a, **k: [ban_ghi])


@pytest.mark.parametrize("lan", ["search_scopus_lane", "search_core_lane"])
def test_lan_engine_tra_ngay_so_van_ra_chuoi(lan):
    (c,) = getattr(S, lan)("suy tim", 30, 5, client_factory=_nha_may(_ban_ghi_engine()))
    assert c.publication_date == "2026" and isinstance(c.publication_date, str)


def test_lan_du_phong_tra_ngay_so_van_ra_chuoi():
    ds, _ = S.bo_sung_du_phong_lane("suy tim", [], 5, bo_sung_fn=lambda *a, **k: ([_ban_ghi_engine()], {}))
    assert [c.publication_date for c in ds] == ["2026"]


# ---------- 2. Đo độ trễ: lớp phòng thủ của bản vá 29/09, nay kiểm được trực tiếp ----------

def test_do_do_tre_bo_qua_ngay_khong_doc_duoc_khong_sap():
    bc = {"candidate_count": 5, "topics": [{"candidates": [
        {"publication_date": 2026}, {"publication_date": None}, {}, {"publication_date": "2026"},
        {"publication_date": "2026 Sep 20"}]}]}
    kq = S.do_do_tre(bc, hom_nay=dt.date(2026, 9, 30))
    assert kq["n_do_duoc"] == 1 and kq["n_tong"] == 5 and kq["trung_vi_ngay"] == 10 and kq["qua_14_ngay"] == 0


def test_do_do_tre_tinh_dung_trung_vi_va_nguong_tren_nhieu_chu_de():
    """Trễ 29·1·14·15·60 ngày (không xếp sẵn, rải 2 chủ đề, có giá trị ĐÚNG ngưỡng 14) + 2 ngày không đọc được."""
    bc = {"candidate_count": 7, "topics": [
        {"candidates": [{"publication_date": d} for d in ("2026 Sep 01", "2026 Sep 29", "2026 Sep 16", 2026)]},
        {"candidates": [{"publication_date": d} for d in ("2026 Sep 15", "2026 Aug 01", None)]}]}
    kq = S.do_do_tre(bc, hom_nay=dt.date(2026, 9, 30))
    assert (kq["n_do_duoc"], kq["n_tong"], kq["trung_vi_ngay"], kq["qua_14_ngay"]) == (5, 7, 15, 3)


def test_do_do_tre_khong_do_duoc_gi_thi_khong_bia_so():
    assert S.do_do_tre({"candidate_count": 1, "topics": [{"candidates": [{"publication_date": 2026}]}]}) is None


# ---------- 3. Thứ tự trong main(): báo cáo tới nơi rồi mới tiến con trỏ / ghi «đã trình» ----------

CHU_DE = [{"topic": t, "query": f"q {t}", "active": True, "truy_van_du_phong": f"{t.lower()} treatment"}
          for t in ("Alpha", "Beta")]


@pytest.fixture()
def kho(monkeypatch, tmp_path):
    """Kho tạm lồng một cấp (alerts/ ghi ở thư mục CHA của kho ⇒ vẫn trong tmp_path); làn dự phòng trả một bài cố
    định cho mỗi truy vấn; PubMed trả một bài thường ⇒ chủ đề thiếu bài mạnh ⇒ được leo thang."""
    goc = tmp_path / "kho"
    goc.mkdir()
    wl = goc / "watchlist.json"
    wl.write_text(json.dumps({"topics": CHU_DE}), encoding="utf-8", newline="\n")
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", wl)
    for ten in ("search_preprint_lane", "search_trials_lane", "search_scopus_lane", "search_core_lane"):
        monkeypatch.setattr(S, ten, lambda *a, **k: [])
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda ds: list(ds))
    monkeypatch.setattr(S, "_pmid_da_co_trong_kho", lambda: set())
    monkeypatch.setattr(S, "search", lambda query, days, retmax, **kw: ["555"])
    monkeypatch.setattr(S, "summarize", lambda ids: [S.Candidate(
        pmid=p, publication_date="2026 Sep 20", title="Bài thường", url=f"https://pubmed.ncbi.nlm.nih.gov/{p}/")
        for p in ids])
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lambda truy_van, unique, retmax, **kw: ([S.Candidate(
        pmid="", publication_date="2026", title=f"Bài dự phòng {truy_van}",
        url=f"https://doi.org/10.1/{truy_van.split()[0]}", tang="du_phong_bac_thang")], ""))
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()
    S._VUOT_TRAN.clear()
    return SimpleNamespace(goc=goc, wl=wl, con_tro=goc / ".quet-cursor.json", khoa=goc / ".quet.lock",
                           so=goc / ".du-phong-trang-thai.json", bao_cao=tmp_path / "ra" / "bao-cao.json")


def _chay(kho, *them):
    return S.main(["--watchlist", str(kho.wl), "--days", "30", "--json-report", str(kho.bao_cao), *them])


def _no(*a, **k):
    raise RuntimeError("hỏng ở khâu hậu xử lý")


def _du_phong_trong(bao_cao: Path) -> list[str]:
    bc = json.loads(bao_cao.read_text(encoding="utf-8"))
    return [c["title"] for t in bc["topics"] for c in t["candidates"] if c["tang"] == "du_phong_bac_thang"]


@pytest.mark.parametrize("buoc_hong", ["markdown_report", "ghi_alert", "do_do_tre"])
def test_hong_truoc_khi_bao_cao_toi_noi_thi_con_tro_khong_tien(kho, monkeypatch, buoc_hong):
    with monkeypatch.context() as m:
        m.setattr(S, buoc_hong, _no)
        with pytest.raises(RuntimeError):
            _chay(kho)
    assert not kho.con_tro.exists(), f"{buoc_hong} hỏng ⇒ chưa ai thấy ứng viên ⇒ con trỏ KHÔNG được tiến"
    assert not kho.khoa.exists(), "khoá phải được trả dù lượt sập"
    # Lượt sau quét lại ĐÚNG cửa sổ đó: ứng viên tới nơi, lúc này con trỏ mới tiến.
    assert _chay(kho) == 0
    bc = json.loads(kho.bao_cao.read_text(encoding="utf-8"))
    assert {c["pmid"] for t in bc["topics"] for c in t["candidates"]} >= {"555"}
    assert sorted(json.loads(kho.con_tro.read_text(encoding="utf-8"))) == ["Alpha", "Beta"]


def _so(kho) -> dict:
    return json.loads(kho.so.read_text(encoding="utf-8"))


@pytest.mark.parametrize("tep_hong", ["md", "json"])
def test_ghi_tep_bao_cao_hong_thi_chua_tien_con_tro_va_chua_ghi_da_trinh(kho, monkeypatch, tep_hong):
    """Hỏng ĐÚNG ở khâu ghi tệp báo cáo (không phải ở lần ghi sổ sớm — `ghi_trang_thai_du_phong` cũng dùng
    `write_atomic`, nên làm hỏng cả hàm thì lỗi nổ trước khi tới báo cáo và ca test xanh cả trên mã cũ)."""
    md = kho.bao_cao.with_suffix(".md")
    dich = md if tep_hong == "md" else kho.bao_cao
    ghi_that = S.write_atomic

    def ghi(path, content):
        if Path(path) == dich:
            raise OSError("đĩa đầy")
        ghi_that(path, content)

    with monkeypatch.context() as m:
        m.setattr(S, "write_atomic", ghi)
        with pytest.raises(OSError):
            _chay(kho, "--report", str(md))
    assert not dich.exists() and not kho.con_tro.exists() and not kho.khoa.exists()
    so = _so(kho)
    assert sorted(so["lan_cuoi_leo_thang"]) == ["Alpha", "Beta"] and so["da_trinh"] == {}


def test_stdout_khong_day_duoc_thi_con_tro_khong_tien(kho, monkeypatch):
    """stdout là kênh báo cáo DUY NHẤT và là ống đã đóng: `print` chỉ nạp bộ đệm, lỗi chỉ lộ lúc đẩy."""
    class _OngDaDong:
        encoding = "utf-8"

        def write(self, s):
            return len(s)

        def flush(self):
            raise BrokenPipeError("đầu đọc đã đóng")

    with monkeypatch.context() as m:
        m.setattr(sys, "stdout", _OngDaDong())
        with pytest.raises(BrokenPipeError):
            S.main(["--watchlist", str(kho.wl), "--days", "30"])
    assert not kho.con_tro.exists() and not kho.khoa.exists() and _so(kho)["da_trinh"] == {}


def test_moi_lan_ghi_so_va_con_tro_deu_nam_trong_khoa(kho, monkeypatch):
    thay: list[tuple[str, bool]] = []
    ghi_so, ghi_con_tro = S.ghi_trang_thai_du_phong, S.ghi_cursor
    monkeypatch.setattr(S, "ghi_trang_thai_du_phong", lambda so: (thay.append(("so", kho.khoa.exists())), ghi_so(so))[1])
    monkeypatch.setattr(S, "ghi_cursor", lambda cur: (thay.append(("con_tro", kho.khoa.exists())), ghi_con_tro(cur))[1])
    assert _chay(kho) == 0
    assert thay == [("so", True), ("so", True), ("con_tro", True)], "ghi sớm mốc leo thang · ghi «đã trình» · ghi con trỏ"


def test_lan_ghi_som_giu_nguyen_da_trinh_da_co(kho, monkeypatch):
    cu = {"https://doi.org/10.1/cu": (dt.date.today() - dt.timedelta(days=10)).isoformat()}
    kho.so.write_text(json.dumps({"lan_cuoi_leo_thang": {}, "da_trinh": cu}), encoding="utf-8", newline="\n")
    with monkeypatch.context() as m:
        m.setattr(S, "markdown_report", _no)
        with pytest.raises(RuntimeError):
            _chay(kho)
    assert _so(kho)["da_trinh"] == cu, "lượt sập không được làm mất dấu «đã trình» của các lượt trước"


def test_con_tro_chi_ghi_sau_khi_bao_cao_da_nam_tren_dia(kho, monkeypatch):
    thay: list[bool] = []
    ghi_that = S.ghi_cursor
    monkeypatch.setattr(S, "ghi_cursor", lambda cur: (thay.append(kho.bao_cao.exists()), ghi_that(cur))[1])
    assert _chay(kho) == 0
    assert thay == [True], "ghi_cursor phải chạy đúng một lần, SAU khi báo cáo JSON đã được ghi"


def test_luot_sap_khong_danh_dau_da_trinh_nhung_van_ghi_han_muc_da_tieu(kho, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(S, "markdown_report", _no)
        with pytest.raises(RuntimeError):
            _chay(kho)
    so = json.loads(kho.so.read_text(encoding="utf-8"))
    assert sorted(so["lan_cuoi_leo_thang"]) == ["Alpha", "Beta"], "hạn mức tính phí đã tiêu ⇒ mốc leo thang phải ghi"
    assert so["da_trinh"] == {}, "báo cáo chưa tới nơi ⇒ chưa bài nào được coi là «đã trình»"

    # Cùng tuần: trần tuần đã hết (không đốt thêm hạn mức), bài dự phòng chưa được trình.
    assert _chay(kho) == 0
    assert _du_phong_trong(kho.bao_cao) == []
    # Tuần sau tới lượt lại ⇒ bài dự phòng của lượt sập PHẢI được trình (trước bản vá: bị lọc vì «đã trình»).
    so = json.loads(kho.so.read_text(encoding="utf-8"))
    so["lan_cuoi_leo_thang"] = {k: (dt.date.fromisoformat(v) - dt.timedelta(days=7)).isoformat()
                                for k, v in so["lan_cuoi_leo_thang"].items()}
    kho.so.write_text(json.dumps(so), encoding="utf-8", newline="\n")
    assert _chay(kho) == 0
    assert sorted(_du_phong_trong(kho.bao_cao)) == ["Bài dự phòng alpha treatment", "Bài dự phòng beta treatment"]
    assert len(json.loads(kho.so.read_text(encoding="utf-8"))["da_trinh"]) == 2, "trình xong mới ghi «đã trình»"


def test_luot_thanh_cong_ghi_du_so_va_con_tro(kho):
    assert _chay(kho) == 0
    so = json.loads(kho.so.read_text(encoding="utf-8"))
    assert sorted(so["lan_cuoi_leo_thang"]) == ["Alpha", "Beta"] and len(so["da_trinh"]) == 2
    assert kho.con_tro.exists() and not kho.khoa.exists()
    assert len(_du_phong_trong(kho.bao_cao)) == 2


def test_khong_cursor_khong_doc_khong_ghi_con_tro_dung_chung(kho):
    """`--khong-cursor` = quét trọn cửa sổ, KHÔNG đụng con trỏ dùng chung — kể cả sau khi việc ghi đã dời xuống cuối."""
    assert _chay(kho, "--khong-cursor") == 0
    assert not kho.con_tro.exists()
    kho.con_tro.write_text(json.dumps({"Alpha": "2026-01-01"}), encoding="utf-8", newline="\n")
    assert _chay(kho, "--khong-cursor") == 0
    assert json.loads(kho.con_tro.read_text(encoding="utf-8")) == {"Alpha": "2026-01-01"}
