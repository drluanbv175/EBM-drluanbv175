"""Bài dự phòng TÍNH PHÍ đã lấy mà báo cáo chưa tới nơi phải được TRÌNH BÙ, không gọi lại nguồn (30/09/2026).

BH136 dời việc ghi «đã trình» xuống sau khi báo cáo tới nơi, nhưng mốc leo thang (hạn mức đã tiêu) vẫn ghi ngay ⇒ bài
dự phòng của lượt sập không bị đánh dấu sai, song cũng KHÔNG được trình lại khi chạy lại cùng tuần (trần tuần đã tiêu):
nó chỉ trở lại khi chủ đề tới lượt xoay vòng (~17–21 tuần với watchlist thật), có thể không bao giờ. Bác sĩ chọn đóng
hẳn khe: lần ghi sớm cất luôn bài vừa lấy vào `cho_trinh`; lượt sau trình bù và gỡ khỏi hàng chờ khi báo cáo tới nơi.

Kèm quyết định về trần tuần: MỘT trần dùng chung cho mọi lượt có sổ (gói tuần lẫn lượt `--topic` của orchestrator A2) —
chính trần chung này chặn `--cu-nhat N` đốt N lượt tính phí trong một ngày.

Offline hoàn toàn: làn mạng bị chặn, watchlist/con trỏ/khoá/sổ/alerts ở thư mục tạm; làn dự phòng là hàm đếm lời gọi.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
NGUON = ROOT / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "surveillance_scan.py"
_sp = importlib.util.spec_from_file_location("ss_cho_trinh_3009", NGUON)
S = importlib.util.module_from_spec(_sp)
sys.modules["ss_cho_trinh_3009"] = S  # @dataclass tra sys.modules lúc dựng lớp — đăng ký TRƯỚC exec
_sp.loader.exec_module(S)

TEN = ("Alpha", "Beta", "Gamma")
CHU_DE = [{"topic": t, "query": f"q {t}", "active": True, "truy_van_du_phong": f"{t.lower()} treatment"} for t in TEN]


@pytest.fixture()
def kho(monkeypatch, tmp_path):
    goc = tmp_path / "kho"
    goc.mkdir()
    wl = goc / "watchlist.json"
    wl.write_text(json.dumps({"topics": CHU_DE}), encoding="utf-8", newline="\n")
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", wl)
    for ten in ("search_preprint_lane", "search_trials_lane", "search_scopus_lane", "search_core_lane"):
        monkeypatch.setattr(S, ten, lambda *a, **k: [])
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda ds: list(ds))
    monkeypatch.setattr(S, "_pmid_da_co_trong_kho", lambda: set())
    # mỗi chủ đề một PMID riêng (suy từ truy vấn) — bài thường, KHÔNG đủ mạnh ⇒ chủ đề đủ điều kiện leo thang
    monkeypatch.setattr(S, "search", lambda query, days, retmax, **kw: [str(100 + sum(map(ord, query)) % 800)])
    monkeypatch.setattr(S, "summarize", lambda ids: [S.Candidate(
        pmid=p, publication_date="2026 Sep 20", title="Bài thường", url=f"https://pubmed.ncbi.nlm.nih.gov/{p}/")
        for p in ids])
    goi_tinh_phi: list[str] = []

    def lan_du_phong(truy_van, unique, retmax, **kw):
        goi_tinh_phi.append(truy_van)
        return [S.Candidate(pmid="", publication_date=2026, title=f"Bài dự phòng {truy_van}",
                            url=f"https://doi.org/10.1/{truy_van.split()[0]}", tang="du_phong_bac_thang")], ""
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lan_du_phong)
    S._NCBI_CHAN["bi_chan"] = False
    S._SUY_GIAM.clear()
    S._VUOT_TRAN.clear()
    return SimpleNamespace(goc=goc, wl=wl, con_tro=goc / ".quet-cursor.json", so=goc / ".du-phong-trang-thai.json",
                           bao_cao=tmp_path / "ra" / "bao-cao.json", goi=goi_tinh_phi)


def _chay(kho, *them):
    return S.main(["--watchlist", str(kho.wl), "--days", "30", "--json-report", str(kho.bao_cao), *them])


def _no(*a, **k):
    raise RuntimeError("hỏng ở khâu hậu xử lý")


def _chay_sap(kho, monkeypatch, *them):
    with monkeypatch.context() as m:
        m.setattr(S, "markdown_report", _no)
        with pytest.raises(RuntimeError):
            _chay(kho, *them)


def _so(kho) -> dict:
    return json.loads(kho.so.read_text(encoding="utf-8"))


def _bc(kho) -> dict:
    return json.loads(kho.bao_cao.read_text(encoding="utf-8"))


def _du_phong(kho) -> list[str]:
    return sorted(c["title"] for t in _bc(kho)["topics"] for c in t["candidates"] if c["tang"] == "du_phong_bac_thang")


A, B = "Bài dự phòng alpha treatment", "Bài dự phòng beta treatment"


# ---------- lượt sập: bài đã lấy vào hàng chờ; chạy lại trình bù, không gọi lại nguồn tính phí ----------

def test_luot_sap_cat_bai_da_lay_vao_hang_cho(kho, monkeypatch):
    _chay_sap(kho, monkeypatch)
    so = _so(kho)
    assert kho.goi == ["alpha treatment", "beta treatment"] and so["da_trinh"] == {}
    assert {k: [u["title"] for u in v["ung_vien"]] for k, v in so["cho_trinh"].items()} == {"Alpha": [A], "Beta": [B]}
    assert all(v["ngay"] == dt.datetime.now(dt.timezone.utc).date().isoformat() for v in so["cho_trinh"].values())
    assert all(isinstance(u["publication_date"], str) for v in so["cho_trinh"].values() for u in v["ung_vien"])


def test_chay_lai_trinh_bu_khong_goi_lai_nguon_tinh_phi(kho, monkeypatch, capsys):
    _chay_sap(kho, monkeypatch)
    capsys.readouterr()
    assert _chay(kho) == 0
    assert kho.goi == ["alpha treatment", "beta treatment"], "chạy lại KHÔNG được gọi thêm nguồn tính phí"
    bc = _bc(kho)
    assert _du_phong(kho) == [A, B] and bc["du_phong_trinh_bu"] == {"Alpha": 1, "Beta": 1}
    assert bc["du_phong_da_leo_thang"] == [] and bc["candidate_count"] == 5
    assert "trình BÙ 2 bài" in capsys.readouterr().out
    assert all("trình bù 1 bài" in t["error"] for t in bc["topics"][:2])
    so = _so(kho)
    assert so["cho_trinh"] == {} and len(so["da_trinh"]) == 2
    # Lượt thứ ba: không còn gì chờ, bài đã trình không trình lại.
    assert _chay(kho) == 0
    assert _du_phong(kho) == [] and _bc(kho)["du_phong_trinh_bu"] == {}


def test_sap_lien_tiep_bai_van_nam_trong_hang_cho(kho, monkeypatch):
    _chay_sap(kho, monkeypatch)
    truoc = _so(kho)
    _chay_sap(kho, monkeypatch)   # lượt trình bù cũng sập: chưa tới nơi ⇒ vẫn chờ, không ghi «đã trình»
    assert _so(kho) == truoc and kho.goi == ["alpha treatment", "beta treatment"]
    assert _chay(kho) == 0 and _du_phong(kho) == [A, B]


def test_luot_lanh_khong_de_lai_hang_cho(kho):
    assert _chay(kho) == 0
    so = _so(kho)
    assert so["cho_trinh"] == {} and len(so["da_trinh"]) == 2 and _bc(kho)["du_phong_trinh_bu"] == {}


# ---------- ranh giới: lượt nào được trình bù, lượt nào phải để nguyên hàng chờ ----------

def test_luot_dem_tran_0_khong_trinh_bu_va_de_nguyen_hang_cho(kho, monkeypatch):
    """`uu_tien_cap_nhat` gọi `--khong-cursor --tran-du-phong 0`, báo cáo vào thư mục tạm không ai đọc."""
    _chay_sap(kho, monkeypatch)
    truoc = _so(kho)
    assert _chay(kho, "--khong-cursor", "--tran-du-phong", "0") == 0
    assert _du_phong(kho) == [] and _so(kho) == truoc and kho.goi == ["alpha treatment", "beta treatment"]


def test_luot_mot_chu_de_chi_trinh_bu_chu_de_do(kho, monkeypatch):
    _chay_sap(kho, monkeypatch)
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    assert _du_phong(kho) == [A] and sorted(_so(kho)["cho_trinh"]) == ["Beta"]


def test_chu_de_fail_giu_bai_cho_luot_sau(kho, monkeypatch):
    _chay_sap(kho, monkeypatch)
    tim_that = S.search

    def tim(query, days, retmax, **kw):
        if "Beta" in query:
            raise RuntimeError("nguồn hỏng cho Beta")
        return tim_that(query, days, retmax, **kw)
    with monkeypatch.context() as m:
        m.setattr(S, "search", tim)
        assert _chay(kho) == 2
    assert _du_phong(kho) == [A] and sorted(_so(kho)["cho_trinh"]) == ["Beta"]
    assert _chay(kho) == 0 and _du_phong(kho) == [B] and _so(kho)["cho_trinh"] == {}


def test_bai_cho_da_co_qua_lan_chinh_thi_khong_trinh_doi(kho):
    """Trong lúc chờ, bài đã vào PubMed và làn chính tự tìm ra ⇒ không trình hai lần, vẫn gỡ khỏi hàng chờ."""
    pmid_alpha = S.search("q Alpha", 30, 5)[0]
    kho.so.write_text(json.dumps({"cho_trinh": {"Alpha": {"ngay": "2026-09-29", "ung_vien": [
        {"pmid": pmid_alpha, "publication_date": "2026", "title": "Bài dự phòng trùng", "url": "https://doi.org/10.1/t",
         "tang": "du_phong_bac_thang"}]}}}), encoding="utf-8", newline="\n")
    assert _chay(kho, "--tran-du-phong", "1") == 0
    bc = _bc(kho)
    assert [c["pmid"] for c in bc["topics"][0]["candidates"]].count(pmid_alpha) == 1
    assert "Bài dự phòng trùng" not in _du_phong(kho) and "Alpha" not in bc["du_phong_trinh_bu"]
    assert "Alpha" not in _so(kho)["cho_trinh"]


def test_muc_hong_trong_so_bi_bo_khong_lam_sap(kho):
    hong = [None, 7, {"title": "thiếu pmid/url"}, {"pmid": "", "url": "", "publication_date": "", "title": "rỗng khoá"},
            {"pmid": "", "url": "https://doi.org/10.1/pt", "publication_date": "2026", "title": "pubtype hỏng", "pubtype": 5},
            {"pmid": 5, "url": "https://x", "publication_date": "2026", "title": "pmid sai kiểu"},
            {"pmid": "", "url": "https://doi.org/10.1/tot", "publication_date": 2026, "title": "Bài tốt",
             "pubtype": ["Review"], "truong_la": 1}]
    kho.so.write_text(json.dumps({"cho_trinh": {"Alpha": {"ngay": "2026-09-29", "ung_vien": hong},
                                                "Beta": "không phải dict", "Gamma": {"ngay": "2026-09-29"}}}),
                      encoding="utf-8", newline="\n")
    assert _chay(kho, "--tran-du-phong", "1") == 0
    bc = _bc(kho)
    assert bc["du_phong_trinh_bu"] == {"Alpha": 1}
    (tot,) = [c for c in bc["topics"][0]["candidates"] if c["title"] == "Bài tốt"]
    assert tot["publication_date"] == "2026" and tot["tang"] == "du_phong_bac_thang" and tot["pubtype"] == ["Review"]


def test_hang_cho_qua_400_ngay_cua_chu_de_da_roi_watchlist_bi_tia(kho):
    cu = (dt.date.today() - dt.timedelta(days=500)).isoformat()
    moi = (dt.date.today() - dt.timedelta(days=30)).isoformat()
    bai = [{"pmid": "", "url": "https://doi.org/10.1/x", "publication_date": "2025", "title": "Bài"}]
    kho.so.write_text(json.dumps({"cho_trinh": {"Đã rời cũ": {"ngay": cu, "ung_vien": bai},
                                                "Đã rời mới": {"ngay": moi, "ung_vien": bai}}}),
                      encoding="utf-8", newline="\n")
    assert _chay(kho) == 0
    assert sorted(_so(kho)["cho_trinh"]) == ["Đã rời mới"]


def test_leo_thang_moi_cung_chu_de_dang_co_bai_cho_thi_gop_khi_sap(kho, monkeypatch):
    cu = {"pmid": "", "url": "https://doi.org/10.1/cu", "publication_date": "2026", "title": "Bài chờ cũ"}
    kho.so.write_text(json.dumps({"cho_trinh": {"Alpha": {"ngay": "2026-09-22", "ung_vien": [cu]}}}),
                      encoding="utf-8", newline="\n")
    _chay_sap(kho, monkeypatch)
    cho = _so(kho)["cho_trinh"]
    assert sorted(u["title"] for u in cho["Alpha"]["ung_vien"]) == ["Bài chờ cũ", A] and sorted(cho) == ["Alpha", "Beta"]
    assert _chay(kho) == 0
    assert _du_phong(kho) == sorted([A, B, "Bài chờ cũ"]) and _so(kho)["cho_trinh"] == {}


def test_so_cu_chua_co_khoa_cho_trinh_van_doc_duoc(kho):
    kho.so.write_text(json.dumps({"lan_cuoi_leo_thang": {}, "da_trinh": {}}), encoding="utf-8", newline="\n")
    so, loi = S._doc_so_du_phong()
    assert so == {"lan_cuoi_leo_thang": {}, "da_trinh": {}, "cho_trinh": {}, "leo_thang_loi": {}} and loi == ""


# ---------- trần tuần dùng CHUNG: lượt một-chủ-đề (orchestrator A2) và gói tuần cùng một hạn mức ----------

def test_cac_luot_mot_chu_de_va_goi_tuan_dung_chung_mot_tran_tuan(kho):
    """`ops/orchestrator.py --cu-nhat N` chạy N lượt `--topic … --khong-cursor` liên tiếp; nếu mỗi lượt có trần riêng
    thì N chủ đề đều gọi nguồn tính phí trong một ngày (đúng kiểu đốt hạn mức của W40)."""
    for ten in TEN:
        assert _chay(kho, "--topic", ten, "--khong-cursor") == 0
    assert kho.goi == ["alpha treatment", "beta treatment"], "lượt thứ ba cùng tuần không được gọi thêm nguồn tính phí"
    bc = _bc(kho)
    assert bc["du_phong_da_leo_thang"] == [] and bc["du_phong_da_dung_tuan"] == 2
    assert bc["du_phong_khong_leo_thang"] == {"cho_luot_xoay_vong": 1}
    assert _chay(kho) == 0 and kho.goi == ["alpha treatment", "beta treatment"], "gói tuần cùng tuần cũng hết lượt"


def test_chay_lap_cung_chu_de_trong_tuan_khong_goi_lai_nguon_tinh_phi(kho):
    """Trần tuần đếm số chủ đề KHÁC NHAU ⇒ lặp lượt một-chủ-đề từng gọi nguồn tính phí mỗi lần mà bộ đếm đứng yên
    (đo 30/09: 3 lượt = 3 lời gọi, kết quả lần 2–3 bị bỏ vì trùng)."""
    for _ in range(3):
        assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    assert kho.goi == ["alpha treatment"]
    bc = _bc(kho)
    assert bc["du_phong_khong_leo_thang"] == {"da_leo_thang_tuan_nay": 1} and bc["du_phong_da_dung_tuan"] == 1
    assert "đã leo thang trong tuần này" in bc["topics"][0]["error"]


def test_tuan_sau_chu_de_do_lai_duoc_toi_luot(kho):
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    so = _so(kho)
    so["lan_cuoi_leo_thang"] = {k: (dt.date.fromisoformat(v) - dt.timedelta(days=7)).isoformat()
                                for k, v in so["lan_cuoi_leo_thang"].items()}
    kho.so.write_text(json.dumps(so), encoding="utf-8", newline="\n")
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    assert kho.goi == ["alpha treatment", "alpha treatment"], "sang tuần ISO khác thì chủ đề được tra lại"


def test_sap_roi_chay_lai_khi_con_suat_cung_khong_goi_lai(kho, monkeypatch):
    """Lượt một-chủ-đề sập (mới dùng 1/2 suất) rồi chạy lại: trình bù từ hàng chờ, KHÔNG dùng suất còn lại để gọi lại."""
    _chay_sap(kho, monkeypatch, "--topic", "Alpha", "--khong-cursor")
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    assert kho.goi == ["alpha treatment"] and _du_phong(kho) == [A] and _bc(kho)["du_phong_trinh_bu"] == {"Alpha": 1}


def test_lan_ghi_som_giu_hang_cho_cua_chu_de_ngoai_luot_nay(kho, monkeypatch):
    """Lượt một-chủ-đề sập sau khi leo thang: bài chờ của chủ đề KHÁC (không nằm trong lượt này) không được mất."""
    cho_gamma = {"ngay": "2026-09-22", "ung_vien": [
        {"pmid": "", "url": "https://doi.org/10.1/g", "publication_date": "2026", "title": "Bài chờ của Gamma"}]}
    kho.so.write_text(json.dumps({"cho_trinh": {"Gamma": cho_gamma}}), encoding="utf-8", newline="\n")
    _chay_sap(kho, monkeypatch, "--topic", "Alpha", "--khong-cursor")
    cho = _so(kho)["cho_trinh"]
    assert sorted(cho) == ["Alpha", "Gamma"] and cho["Gamma"] == cho_gamma


def test_hang_cho_khong_ro_ngay_khong_bi_tia(kho):
    """Không biết tuổi ≠ đã quá hạn: mục thiếu ngày (sổ sửa tay) được giữ, không bị xoá lặng lẽ."""
    bai = [{"pmid": "", "url": "https://doi.org/10.1/x", "publication_date": "2025", "title": "Bài"}]
    kho.so.write_text(json.dumps({"cho_trinh": {"Đã rời": {"ung_vien": bai}}}), encoding="utf-8", newline="\n")
    assert _chay(kho) == 0
    assert sorted(_so(kho)["cho_trinh"]) == ["Đã rời"]


# ═══════════ Vòng 2 (sau phản biện đối kháng 30/09): ba trạng thái của một lần leo thang ═══════════

def _lan(monkeypatch, kich_ban):
    """Thay làn dự phòng bằng hàm theo kịch bản: {truy vấn: hàm()} trả KetQuaDuPhong/2-tuple hoặc ném lỗi."""
    goi: list[str] = []

    def lan(truy_van, unique, retmax, **kw):
        goi.append(truy_van)
        return kich_ban[truy_van]()
    monkeypatch.setattr(S, "bo_sung_du_phong_lane", lan)
    return goi


def _bai(truy_van):
    return S.Candidate(pmid="", publication_date="2026", title=f"Bài dự phòng {truy_van}",
                       url=f"https://doi.org/10.1/{truy_van.split()[0]}", tang="du_phong_bac_thang")


def _ok(truy_van, so_goi=1):
    return lambda: S.KetQuaDuPhong([_bai(truy_van)], "", so_goi)


def _nem(loi):
    def _k():
        raise loi
    return _k


def test_nguon_khong_duoc_goi_thi_khong_tieu_suat_va_trao_suat_cho_chu_de_ke_tiep(kho, monkeypatch):
    """Engine vắng/cờ tắt/engine thấy đã đủ ⇒ `so_goi == 0`: không ghi mốc, không tính suất; suất chuyển cho chủ đề sau."""
    goi = _lan(monkeypatch, {"alpha treatment": lambda: S.KetQuaDuPhong([], "", 0),
                             "beta treatment": _ok("beta treatment"), "gamma treatment": _ok("gamma treatment")})
    assert _chay(kho) == 0
    bc, so = _bc(kho), _so(kho)
    assert goi == ["alpha treatment", "beta treatment", "gamma treatment"]
    assert bc["du_phong_da_leo_thang"] == ["Beta", "Gamma"] and bc["du_phong_khong_leo_thang"] == {"nguon_khong_goi": 1}
    assert sorted(so["lan_cuoi_leo_thang"]) == ["Beta", "Gamma"], "chủ đề không được gọi thì không mất lượt xoay vòng"
    assert "KHÔNG được gọi" in bc["topics"][0]["error"]


def test_may_khong_co_engine_khong_dot_suat_tuan(kho, monkeypatch):
    """Dùng làn THẬT với engine vắng: trước đây mỗi lượt «leo thang» 2 chủ đề, ghi mốc và tiêu suất mà không gọi gì."""
    monkeypatch.undo()   # bỏ stub làn của fixture…
    # …rồi dựng lại phần còn lại của fixture (trừ làn dự phòng) để chạy làn thật ngoại tuyến
    monkeypatch.setattr(S, "DEFAULT_WATCHLIST", kho.wl)
    for ten in ("search_preprint_lane", "search_trials_lane", "search_scopus_lane", "search_core_lane"):
        monkeypatch.setattr(S, ten, lambda *a, **k: [])
    monkeypatch.setattr(S, "gan_do_tin_cay", lambda ds: list(ds))
    monkeypatch.setattr(S, "_pmid_da_co_trong_kho", lambda: set())
    monkeypatch.setattr(S, "search", lambda query, days, retmax, **kw: [str(100 + sum(map(ord, query)) % 800)])
    monkeypatch.setattr(S, "summarize", lambda ids: [S.Candidate(p, "2026 Sep 20", "Bài thường", f"u{p}") for p in ids])
    monkeypatch.setattr(S, "_tim_medical_ebm_automation", lambda: None)
    kq = S.bo_sung_du_phong_lane("alpha treatment", [], 5)
    assert kq.so_goi == 0 and tuple(kq) == ([], ""), "làn thật phải báo «chắc chắn không gọi»; vẫn tách được thành cặp"
    assert _chay(kho) == 0
    bc = _bc(kho)
    assert bc["du_phong_da_leo_thang"] == [] and bc["du_phong_khong_leo_thang"] == {"nguon_khong_goi": 3}
    assert not kho.so.exists() or _so(kho)["lan_cuoi_leo_thang"] == {}


@pytest.mark.parametrize("tom_tat, mong_doi", [
    ({"active": True, "tang": {"consensus": {"da_goi": 1}, "serpapi_scholar": {"da_goi": 2}}}, 3),
    ({"active": True, "tang": {"consensus": {"da_goi": 0}}}, 0),      # có tầng bật nhưng cổng đủ-chứng-cứ của engine đóng
    ({"active": False, "tang": {}}, 0),                               # chế độ mock / không tầng nào bật
    ({}, None),                                                       # hàm tiêm sẵn không báo ⇒ không rõ
])
def test_lan_doc_so_loi_goi_tu_tom_tat_cua_engine(tom_tat, mong_doi):
    assert S.bo_sung_du_phong_lane("x", [], 5, bo_sung_fn=lambda *a, **k: ([], tom_tat)).so_goi == mong_doi


@pytest.mark.parametrize("hong", [_nem(ConnectionError("mất mạng")),
                                  lambda: S.KetQuaDuPhong([], "bậc thang dự phòng lỗi nội bộ: KeyError", 1)])
def test_leo_thang_loi_van_tinh_suat_nhung_duoc_thu_lai_trong_tuan(kho, monkeypatch, hong):
    goi = _lan(monkeypatch, {"alpha treatment": hong})
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    bc, so = _bc(kho), _so(kho)
    assert bc["du_phong_da_leo_thang"] == ["Alpha"] and bc["du_phong_loi"] == ["Alpha"]
    assert sorted(so["lan_cuoi_leo_thang"]) == ["Alpha"] and sorted(so["leo_thang_loi"]) == ["Alpha"]
    assert "du_phong_bac_thang" in bc["topics"][0]["lan_phu_loi"]
    # Chạy lại cùng tuần khi nguồn đã trả lời: ĐƯỢC thử lại (lần trước chưa có kết quả), xong thì gỡ dấu lỗi.
    goi2 = _lan(monkeypatch, {"alpha treatment": _ok("alpha treatment")})
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    bc, so = _bc(kho), _so(kho)
    assert goi == ["alpha treatment"] and goi2 == ["alpha treatment"] and _du_phong(kho) == [A]
    assert bc["du_phong_loi"] == [] and so["leo_thang_loi"] == {} and bc["du_phong_da_dung_tuan"] == 1
    # Lần thứ ba: đã xong trong tuần ⇒ không gọi nữa.
    goi3 = _lan(monkeypatch, {"alpha treatment": _ok("alpha treatment")})
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0 and goi3 == []


def test_leo_thang_loi_het_suat_thi_khong_thu_lai(kho, monkeypatch):
    """Lỗi vẫn tính suất: hai chủ đề lỗi trong gói tuần (trần 2) ⇒ chạy lại cùng tuần không gọi thêm."""
    _lan(monkeypatch, {"alpha treatment": _nem(TimeoutError()), "beta treatment": _nem(TimeoutError())})
    assert _chay(kho) == 0
    goi2 = _lan(monkeypatch, {k: _ok(k) for k in ("alpha treatment", "beta treatment", "gamma treatment")})
    assert _chay(kho) == 0 and goi2 == []
    assert _bc(kho)["du_phong_khong_leo_thang"] == {"cho_luot_xoay_vong": 3}


def test_dau_loi_cua_tuan_truoc_bi_don(kho, monkeypatch):
    tuan_truoc = (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=7)).isoformat()
    kho.so.write_text(json.dumps({"lan_cuoi_leo_thang": {"Alpha": tuan_truoc}, "leo_thang_loi": {"Alpha": tuan_truoc}}),
                      encoding="utf-8", newline="\n")
    assert _chay(kho, "--topic", "Beta", "--khong-cursor") == 0
    assert "Alpha" not in _so(kho)["leo_thang_loi"]


def test_nguon_tra_0_bai_roi_luot_sap_thi_moc_leo_thang_van_da_ghi(kho, monkeypatch):
    """Hạn mức đã tiêu dù không có bài mới: mốc phải nằm trên đĩa ngay, không chờ «đã trình» đổi."""
    goi = _lan(monkeypatch, {"alpha treatment": lambda: ([], ""), "beta treatment": lambda: ([], "")})
    _chay_sap(kho, monkeypatch)
    so = _so(kho)
    assert sorted(so["lan_cuoi_leo_thang"]) == ["Alpha", "Beta"] and so["cho_trinh"] == {} and so["da_trinh"] == {}
    assert _chay(kho) == 0 and goi == ["alpha treatment", "beta treatment"], "chạy lại không gọi thêm"


def test_bi_ngat_giua_hai_loi_goi_tinh_phi_van_giu_duoc_loi_goi_dau(kho, monkeypatch):
    """Tiến trình bị ngắt (Ctrl-C/kill) ở lời gọi thứ hai: mốc và bài của lời gọi thứ nhất đã nằm trong sổ."""
    _lan(monkeypatch, {"alpha treatment": _ok("alpha treatment"), "beta treatment": _nem(KeyboardInterrupt())})
    with pytest.raises(KeyboardInterrupt):
        _chay(kho)
    so = _so(kho)
    assert sorted(so["lan_cuoi_leo_thang"]) == ["Alpha"] and sorted(so["cho_trinh"]) == ["Alpha"] and so["da_trinh"] == {}
    assert not kho.con_tro.exists() and not (kho.goc / ".quet.lock").exists()
    goi2 = _lan(monkeypatch, {"beta treatment": _ok("beta treatment")})
    assert _chay(kho) == 0
    assert goi2 == ["beta treatment"], "Alpha trình bù từ hàng chờ; chỉ Beta (chưa gọi được) mới gọi"
    assert _du_phong(kho) == [A, B] and _bc(kho)["du_phong_trinh_bu"] == {"Alpha": 1}


# ═══════════ Sổ không đọc được: tắt làn dự phòng lượt đó, KHÔNG ghi đè ═══════════

@pytest.mark.parametrize("noi_dung", ['{"lan_cuoi_leo_thang": {"Alpha"', "", "[]", "\ufffd\x00rác"])
def test_so_hong_thi_tat_lan_du_phong_va_khong_ghi_de(kho, capsys, noi_dung):
    kho.so.write_text(noi_dung, encoding="utf-8")
    truoc = kho.so.read_bytes()
    assert _chay(kho) == 0
    bc = _bc(kho)
    assert kho.so.read_bytes() == truoc, "sổ không đọc được thì KHÔNG được ghi đè"
    assert kho.goi == [] and _du_phong(kho) == [] and bc["du_phong_da_leo_thang"] == []
    assert bc["du_phong_tat_vi"] and bc["du_phong_khong_leo_thang"] == {"so_khong_doc_duoc": 3}
    assert "Bậc thang dự phòng TẮT lượt này" in capsys.readouterr().out
    assert all("TẮT lượt này" in t["error"] for t in bc["topics"])
    assert kho.con_tro.exists(), "làn chính vẫn quét và tiến con trỏ bình thường"


def test_doc_so_loi_he_thong_cung_tat_lan_du_phong(kho, monkeypatch):
    """Tệp OneDrive chưa tải về: đọc ném OSError (không phải «vắng») ⇒ không được coi là sổ rỗng."""
    kho.so.write_text(json.dumps({"lan_cuoi_leo_thang": {}, "da_trinh": {"k": "2026-09-29"},
                                  "cho_trinh": {"Gamma": {"ngay": "2026-09-29", "ung_vien": [
                                      {"pmid": "", "url": "https://doi.org/10.1/g", "publication_date": "2026", "title": "G"}]}}}),
                      encoding="utf-8", newline="\n")
    truoc = kho.so.read_bytes()
    doc_that = Path.read_text

    def doc(self, *a, **k):
        if self == kho.so:
            raise OSError(11, "Resource deadlock avoided")
        return doc_that(self, *a, **k)
    with monkeypatch.context() as m:
        m.setattr(Path, "read_text", doc)
        assert _chay(kho) == 0
        assert "OSError" in _bc(kho)["du_phong_tat_vi"]
    assert kho.so.read_bytes() == truoc and kho.goi == []
    assert _chay(kho) == 0 and "Gamma" in _bc(kho)["du_phong_trinh_bu"], "đọc lại được thì hàng chờ còn nguyên"


def test_so_vang_la_so_rong_hop_le(kho):
    assert not kho.so.exists()
    assert _chay(kho) == 0 and _bc(kho)["du_phong_tat_vi"] == "" and len(kho.goi) == 2


# ═══════════ Trình bù không phụ thuộc cổng leo thang ═══════════

def _cho(ten):
    return {ten: {"ngay": "2026-09-29", "ung_vien": [
        {"pmid": "", "url": f"https://doi.org/10.1/{ten.lower()}-cho", "publication_date": "2026", "title": f"Bài chờ {ten}"}]}}


def test_trinh_bu_ca_khi_chu_de_da_du_bai_manh(kho, monkeypatch):
    kho.so.write_text(json.dumps({"cho_trinh": _cho("Alpha")}), encoding="utf-8", newline="\n")
    monkeypatch.setattr(S, "summarize", lambda ids: [S.Candidate(
        pmid=f"{p}{k}", publication_date="2026 Sep 20", title="Hướng dẫn", url=f"u{p}{k}", pubtype=("Practice Guideline",))
        for p in ids for k in range(3)])
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    bc = _bc(kho)
    assert bc["du_phong_khong_leo_thang"] == {"du_bai_manh": 1} and kho.goi == []
    assert bc["du_phong_trinh_bu"] == {"Alpha": 1} and _so(kho)["cho_trinh"] == {}


def test_trinh_bu_ca_khi_chu_de_suy_giam(kho, monkeypatch):
    kho.so.write_text(json.dumps({"cho_trinh": _cho("Alpha")}), encoding="utf-8", newline="\n")
    tim_that = S.search

    def tim(query, days, retmax, **kw):
        S._SUY_GIAM.append("NCBI lỗi — dùng Europe PMC dự phòng")
        return tim_that(query, days, retmax, **kw)
    monkeypatch.setattr(S, "search", tim)
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 2
    bc = _bc(kho)
    assert bc["topics"][0]["status"] == "PASS_DEGRADED" and bc["du_phong_khong_leo_thang"] == {"ncbi_loi": 1}
    assert bc["du_phong_trinh_bu"] == {"Alpha": 1} and _so(kho)["cho_trinh"] == {}


def test_bai_cho_da_mang_dau_da_trinh_thi_khong_trinh_lai(kho):
    cho = _cho("Alpha")
    khoa = cho["Alpha"]["ung_vien"][0]["url"]
    kho.so.write_text(json.dumps({"cho_trinh": cho, "da_trinh": {khoa: dt.date.today().isoformat()}}),
                      encoding="utf-8", newline="\n")
    assert _chay(kho, "--tran-du-phong", "1") == 0
    assert "Bài chờ Alpha" not in _du_phong(kho) and "Alpha" not in _so(kho)["cho_trinh"]


def test_lan_bi_tat_thi_run_scan_khong_dung_so_du_co_noi_dung(kho, monkeypatch):
    """Gọi thẳng `run_scan` với sổ CÓ nội dung + cờ tắt: không trình bù, không leo thang, sổ không bị sửa một khoá nào."""
    so = {"lan_cuoi_leo_thang": {"Beta": "2026-01-05"}, "da_trinh": {"k": "2026-01-05"}, "cho_trinh": _cho("Alpha"),
          "leo_thang_loi": {"Beta": "2026-01-05"}}
    truoc = json.loads(json.dumps(so))
    da_luu: list[dict] = []
    rep = S.run_scan(CHU_DE, days=30, max_results=5, cursor={}, search_fn=S.search, summarize_fn=S.summarize,
                     tran_leo_thang_du_phong=2, trang_thai_du_phong=so, luu_so_du_phong=da_luu.append,
                     du_phong_tat_vi="sổ không đọc được")
    assert so == truoc and da_luu == [] and kho.goi == []
    assert rep["du_phong_trinh_bu"] == {} and rep["du_phong_tat_vi"] == "sổ không đọc được"


def test_co_du_phong_tat_thi_lan_that_bao_chac_chan_khong_goi(monkeypatch, tmp_path):
    """Nhánh «engine có nhưng cờ dự phòng TẮT» của làn thật, chạy bằng engine GIẢ nằm trong sys.modules (không chạm
    engine thật, không gọi mạng; sys.path/sys.modules được trả về nguyên trạng sau test)."""
    import types
    mea = tmp_path / "mea"
    for rel in ("app/sources/base.py", "app/services/fallback_ladder.py"):
        (mea / rel).parent.mkdir(parents=True, exist_ok=True)
        (mea / rel).write_text("", encoding="utf-8")

    def _mo_dun(ten, **thuoc_tinh):
        m = types.ModuleType(ten)
        m.__dict__.update(thuoc_tinh)
        monkeypatch.setitem(sys.modules, ten, m)

    da_goi: list = []
    _mo_dun("app")
    _mo_dun("app.sources")
    _mo_dun("app.sources.base", RawRecord=SimpleNamespace)
    _mo_dun("app.services")
    _mo_dun("app.services.fallback_ladder", du_phong_dang_bat=lambda: False,
            bo_sung_neu_thieu=lambda *a, **k: da_goi.append(a) or ([], {}))
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(S, "_tim_medical_ebm_automation", lambda: mea)
    kq = S.bo_sung_du_phong_lane("alpha treatment", [], 5)
    assert kq.so_goi == 0 and tuple(kq) == ([], "") and da_goi == [], "cờ tắt ⇒ chắc chắn không gọi nguồn tính phí"


# ═══════════ Vòng 3 (sau kiểm chứng độc lập): lỗi của chính nguồn, giới hạn thử lại, sổ sai kiểu ═══════════

def _tang(**kw):
    """Một tầng trong tóm tắt của engine (`fallback_ladder._tang_rong`)."""
    return {"da_goi": 0, "tim_thay": 0, "so_loi": 0, "loi_cuoi": None, "loi_chot": None, **kw}


def _lan_that(tom_tat, co_bai=False):
    ban_ghi = [SimpleNamespace(pmid=None, doi="10.1/x", url=None, title="Bài", publication_date="2026",
                               journal_or_organization="T", source="consensus")] if co_bai else []
    return S.bo_sung_du_phong_lane("alpha treatment", [], 5, bo_sung_fn=lambda *a, **k: (ban_ghi, tom_tat))


def test_loi_cua_chinh_nguon_tinh_phi_duoc_nhan_la_loi():
    """Timeout/5xx/401 nằm ở `tang[…]["so_loi"/"loi_cuoi"]`, không ở `loi_noi_bo` — trước đó trôi qua im lặng."""
    kq = _lan_that({"active": True, "tang": {"consensus": _tang(da_goi=1, so_loi=1, loi_cuoi="khac"),
                                             "serpapi_scholar": _tang(da_goi=1, so_loi=1, loi_cuoi="key_sai",
                                                                      loi_chot="key_sai")}})
    assert kq.so_goi == 2 and kq[1] == "bậc thang dự phòng: nguồn dự phòng lỗi: consensus=khac; serpapi_scholar=key_sai"


def test_mot_tang_loi_tang_kia_co_bai_thi_la_canh_bao_khong_phai_lan_goi_loi():
    kq = _lan_that({"active": True, "tang": {"consensus": _tang(da_goi=1, so_loi=1, loi_cuoi="khac"),
                                             "serpapi_scholar": _tang(da_goi=1, tim_thay=1)}}, co_bai=True)
    assert kq[1] == "" and "consensus=khac" in kq.canh_bao and len(kq[0]) == 1 and kq.so_goi == 2


def test_het_han_muc_khong_phai_loi_goi_va_khong_phai_loi():
    """Engine vẫn đếm `da_goi` cho `het_quota` do cờ (không gửi request) — bộ quét phải trừ ra."""
    kq = _lan_that({"active": True, "tang": {"consensus": _tang(da_goi=1, so_loi=1, loi_cuoi="het_quota",
                                                                loi_chot="het_quota"),
                                             "serpapi_scholar": _tang(so_loi=1, loi_cuoi="het_ngan_sach",
                                                                      loi_chot="het_ngan_sach")}})
    assert kq.so_goi == 0 and kq[1] == "" and kq.canh_bao == ""


def test_canh_bao_mot_phan_van_la_da_goi_nhung_co_ghi_chu(kho, monkeypatch):
    _lan(monkeypatch, {"alpha treatment": lambda: S.KetQuaDuPhong(
        [_bai("alpha treatment")], "", 2, "bậc thang dự phòng: nguồn dự phòng lỗi: consensus=khac (tầng khác vẫn trả bài)")})
    assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
    bc = _bc(kho)
    assert bc["du_phong_da_leo_thang"] == ["Alpha"] and bc["du_phong_loi"] == [] and _du_phong(kho) == [A]
    assert "consensus=khac" in bc["topics"][0]["error"] and "du_phong_bac_thang" in bc["topics"][0]["lan_phu_loi"]
    assert _so(kho)["leo_thang_loi"] == {}


def test_loi_lap_lai_chi_duoc_thu_lai_mot_lan_moi_tuan(kho, monkeypatch):
    """Không giới hạn thì 5 lượt cùng lỗi = 5 lời gọi có thể đã bị tính tiền, bộ đếm tuần vẫn đứng yên."""
    goi = _lan(monkeypatch, {"alpha treatment": _nem(TimeoutError())})
    bao_cao = []
    for _ in range(5):
        assert _chay(kho, "--topic", "Alpha", "--khong-cursor") == 0
        bao_cao.append(_bc(kho))
    assert goi == ["alpha treatment"] * (1 + S.TRAN_THU_LAI_DU_PHONG), "1 lần gọi + đúng số lần thử lại cho phép"
    assert bao_cao[0]["du_phong_thu_lai"] == [] and bao_cao[1]["du_phong_thu_lai"] == ["Alpha"]
    assert "không thử lại nữa" in bao_cao[1]["topics"][0]["error"]
    assert bao_cao[2]["du_phong_khong_leo_thang"] == {"loi_het_luot_thu_lai": 1} and bao_cao[2]["du_phong_da_leo_thang"] == []
    assert all(b["du_phong_da_dung_tuan_sau_luot"] == 1 for b in bao_cao), "thử lại không tính thêm suất"
    assert _so(kho)["leo_thang_loi"] == {"Alpha": {"ngay": dt.datetime.now(dt.timezone.utc).date().isoformat(), "so_lan": 2}}


def test_so_da_dung_sau_luot_la_con_so_lenh_nang_tran_phai_vuot(kho):
    assert _chay(kho) == 0
    bc = _bc(kho)
    assert bc["du_phong_da_dung_tuan"] == 0 and bc["du_phong_da_dung_tuan_sau_luot"] == 2


def test_lenh_nang_tran_trong_phieu_leo_thang_dung_chu_de_va_khong_dung_con_tro(kho):
    """Tuần đã dùng 4 với trần 2 (sổ thật 30/09): đúng lệnh phiếu in — `--topic X --khong-cursor --tran-du-phong 5`."""
    hom_nay = dt.datetime.now(dt.timezone.utc).date().isoformat()
    kho.so.write_text(json.dumps({"lan_cuoi_leo_thang": {f"Khác {k}": hom_nay for k in range(4)}}),
                      encoding="utf-8", newline="\n")
    for tran in ("3", "4"):
        assert _chay(kho, "--topic", "Gamma", "--khong-cursor", "--tran-du-phong", tran) == 0
    assert kho.goi == [], "3 hay 4 đều chưa vượt số đã dùng"
    assert _bc(kho)["du_phong_da_dung_tuan_sau_luot"] == 4
    assert _chay(kho, "--topic", "Gamma", "--khong-cursor", "--tran-du-phong", "5") == 0
    assert kho.goi == ["gamma treatment"] and _bc(kho)["du_phong_da_leo_thang"] == ["Gamma"]
    assert not kho.con_tro.exists(), "`--khong-cursor`: không đụng con trỏ của gói tuần"


@pytest.mark.parametrize("khoa", ["lan_cuoi_leo_thang", "da_trinh", "cho_trinh", "leo_thang_loi"])
@pytest.mark.parametrize("gia_tri", [[], "x", 5, True, 0, ""])
def test_so_co_khoa_sai_kieu_thi_tat_lan_khong_sap_khong_ghi_de(kho, khoa, gia_tri):
    """`dict("x")` từng ném lỗi làm sập cả lượt; `[]`/`0`/`""` từng bị ép thành rỗng rồi ghi đè."""
    kho.so.write_text(json.dumps({"da_trinh": {"k": "2026-09-29"}, khoa: gia_tri}), encoding="utf-8")
    truoc = kho.so.read_bytes()
    assert _chay(kho) == 0
    bc = _bc(kho)
    assert kho.so.read_bytes() == truoc and kho.goi == []
    assert f"«{khoa}» sai kiểu" in bc["du_phong_tat_vi"] and "đổi tên tệp" in bc["du_phong_tat_vi"]


def test_so_co_bom_van_la_so_hop_le(kho):
    hom_nay = dt.datetime.now(dt.timezone.utc).date().isoformat()
    kho.so.write_bytes(b"\xef\xbb\xbf" + json.dumps({"lan_cuoi_leo_thang": {"Alpha": hom_nay, "Beta": hom_nay}}).encode())
    assert _chay(kho) == 0
    bc = _bc(kho)
    assert bc["du_phong_tat_vi"] == "" and bc["du_phong_da_dung_tuan"] == 2 and kho.goi == []


def test_so_hong_duoc_dua_vao_canh_bao_khan(kho):
    """Tệp hỏng không tự hết: mọi lượt sau đều tắt làn dự phòng mà mã thoát vẫn 0 ⇒ phải vào alerts/."""
    kho.so.write_text("{hỏng", encoding="utf-8")
    assert _chay(kho) == 0
    (tep,) = (kho.goc.parent / "alerts").glob("*.md")
    noi_dung = tep.read_text(encoding="utf-8")
    assert "BẬC THANG DỰ PHÒNG TẮT" in noi_dung and "đổi tên tệp" in noi_dung


def test_so_lanh_khong_sinh_canh_bao_khan(kho):
    assert _chay(kho) == 0
    assert not list((kho.goc.parent / "alerts").glob("*.md"))
