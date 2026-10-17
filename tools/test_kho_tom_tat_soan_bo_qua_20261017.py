# -*- coding: utf-8 -*-
"""Kho tóm tắt máy nhận hai trường SIÊU DỮ LIỆU `soan` và `bo_qua` (17/10/2026) — `tom_tat_endnote_vi.py`.

Đo thật 17/10/2026 trên `EBM-Dashboards/tom-tat-abstract-vi.json` (165 mục):
  • 164 mục mang `soan` («Claude (máy) · 13/10/2026 · từ abstract …») ⇒ mỗi lượt nạp in «trường lạ soan» cho từng mục
    (và chỉ in 8 dòng đầu, phần còn lại bị cắt im lặng) — nhiễu che lỗi khuôn thật.
  • 2 mục chỉ có `bo_qua` (trường Abstract của bản ghi là GHI CHÚ của bác sĩ, không phải abstract PubMed — quyết định có chủ ý
    13/10) ⇒ vẫn bị liệt kê «CHƯA có tóm tắt máy — cần một phiên Claude soạn», tức mời phiên sau soạn trái quyết định.
Ngoại tuyến hoàn toàn: dashboard là dict giả, EndNote là đối tượng giả.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _nap(rel: str, ten: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


tt = _nap("tools/tom_tat_endnote_vi.py", "_tt_soan_bo_qua")
N = _nap("tools/nap_endnote_chu_de.py", "_nap_soan_bo_qua")

SOAN = "Claude (máy) · 13/10/2026 · từ abstract PubMed trong thư viện EndNote"
BO_QUA = "Trường Abstract là ghi chú tiếng Việt của bác sĩ, không phải abstract PubMed — giữ nguyên, không tóm tắt máy"
TOM_TAT = {"thiet_ke": "RCT, n = 1234", "P": "Người lớn ≥ 40 tuổi", "I": "Thuốc", "C": "Giả dược", "O": "Kết cục chính",
           "ket_qua": "9.1% so với 12.0%"}
GOC = "Methods: We randomly assigned 1,234 adults aged 40 years or older. Findings: 9·1% vs 12·0%."
GHI_CHU_BS = "[NEJM 2022] Rất quan trọng tại VN. Với rung nhĩ do hẹp hai lá thấp tim: VKA vẫn tốt hơn NOAC."

MUC = {"id": "ITEM-01", "title": "Mục chính", "pmid": "31111111", "decision": "consider", "gradeLevel": "mod",
       "references": ["Phụ lục: Smith J. Stroke 2020. PMID 32222222", "Phụ lục: Lee K. NEJM 2022. PMID 33333333",
                      "Phụ lục: Wu L. BMJ 2021. PMID 34444444"]}
DASH = Path("/khong-ton-tai/WebDashboard_X_20261017.html")


def _doc(p):
    return {"meta": {"question": "Q"}, "items": [MUC]} if Path(p).name == DASH.name else None


class _EndNoteGia:
    def __init__(self, abstract: dict[str, str], khop: dict[str, list[str]]):
        self.abstract, self.khop = dict(abstract), khop
        self.thu_vien = Path("/khong-ton-tai/tv.enl")

    def tim_khop(self, gia_tri, truong):
        return {v: self.khop[v] for v in gia_tri if v in self.khop}

    def doc_truong(self, ids, truong):
        return {m: self.abstract.get(m, "") for m in ids}

    def ghi_truong(self, cap, truong):
        for m, gt in cap:
            self.abstract[m] = gt.replace("\n", "\r")
        return {m: "" for m, _ in cap}


# ── Bộ kiểm khuôn ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test_soan_va_bo_qua_la_truong_hop_le_khong_bao_loi():
    kho = {"PMID 1": {**TOM_TAT, "soan": SOAN}, "PMID 2": {"bo_qua": BO_QUA, "soan": SOAN}, "DOI 10.1000/abc": {"bo_qua": BO_QUA}}
    assert tt.kiem_kho_tom_tat(kho) == [], "trường siêu dữ liệu hợp lệ không được báo «trường lạ»"


def test_truong_la_khac_van_bao_loi_va_neu_ten_sieu_du_lieu():
    loi = tt.kiem_kho_tom_tat({"PMID 1": {**TOM_TAT, "soan": SOAN, "soan2": "x", "design": "RCT"}})
    assert len(loi) == 1 and "soan2" in loi[0] and "design" in loi[0], "nới khuôn chỉ cho ĐÚNG hai trường, không nới mọi khoá"
    assert "siêu dữ liệu (không in): soan, bo_qua" in loi[0]


def test_bo_qua_rong_bao_loi_can_ly_do():
    for gia_tri in ("", "  ", "—"):
        loi = tt.kiem_kho_tom_tat({"PMID 1": {"bo_qua": gia_tri, "soan": SOAN}})
        assert len(loi) == 1 and "«bo_qua» rỗng" in loi[0], f"bo_qua={gia_tri!r} không có lý do phải bị báo"


def test_bo_qua_cung_truong_tom_tat_la_mau_thuan():
    loi = tt.kiem_kho_tom_tat({"PMID 1": {**TOM_TAT, "bo_qua": BO_QUA}})
    assert len(loi) == 1 and "mâu thuẫn" in loi[0]


def test_tom_tat_cho_muc_bo_qua_khong_bao_gio_in_ke_ca_khi_lo_co_truong():
    ds = tt.ngu_canh([DASH], _doc)
    muc = ds["pmid:32222222"]
    assert tt.tom_tat_cho(muc, {"PMID 32222222": {**TOM_TAT, "soan": SOAN}}, GOC) == ({**TOM_TAT, "soan": SOAN}, []), \
        "mục có soan vẫn in tóm tắt như thường"
    assert tt.tom_tat_cho(muc, {"PMID 32222222": {**TOM_TAT, "bo_qua": BO_QUA}}, GOC) == (None, []), \
        "bo_qua thắng: không in tóm tắt máy dù mục lỡ có đủ trường"


def test_mau_mo_ta_hai_truong_sieu_du_lieu(capsys):
    assert tt.main(["--mau"]) == 0
    mau = json.loads(capsys.readouterr().out)
    assert "«soan»" in mau["_about"] and "«bo_qua»" in mau["_about"] and "KHÔNG soạn đè" in mau["_about"]
    assert tt.kiem_kho_tom_tat(mau["muc"]) == []


# ── Ghi vào EndNote + danh sách «chưa tóm tắt» ──────────────────────────────────────────────────────────────────────────
def test_ghi_tom_tat_tach_bo_qua_khoi_chua_tom_tat_va_giu_ghi_chu_bac_si(tmp_path):
    en = _EndNoteGia({"r1": "A.", "r2": GOC, "r3": GHI_CHU_BS, "r4": "Some abstract."},
                     {"31111111": ["r1"], "32222222": ["r2"], "33333333": ["r3"], "34444444": ["r4"]})
    kho_tt = {"PMID 32222222": {**TOM_TAT, "soan": SOAN}, "PMID 33333333": {"bo_qua": BO_QUA, "soan": SOAN}}
    bc = tt.ghi_tom_tat(en, [DASH], kho=tmp_path, ap_dung=True, doc_data=_doc, sao_luu=lambda: "/s", tom_tat_abs=kho_tt)
    assert bc["loi"] == [], "kho có soan/bo_qua hợp lệ không sinh lỗi khuôn"
    assert bc["tham_khao_bo_qua"] == ["PMID 33333333"]
    assert bc["tham_khao_chua_tom_tat"] == ["PMID 34444444"], "bo_qua không bị tính «chưa tóm tắt»; mục vắng thật thì có"
    assert bc["tom_tat_may"] == 1 and "TÓM TẮT MÁY" in en.abstract["r2"]
    assert "TÓM TẮT MÁY" not in en.abstract["r3"], "mục bo_qua không có khối tóm tắt máy"
    assert en.abstract["r3"].replace("\r", "\n").endswith(GHI_CHU_BS), "ghi chú của bác sĩ giữ NGUYÊN dưới dấu phân cách"
    assert SOAN not in en.abstract["r2"] and BO_QUA not in en.abstract["r3"], "siêu dữ liệu không bao giờ in vào EndNote"


def test_chay_tom_tat_in_dong_bo_qua_va_dem_canh_bao_bi_an(capsys):
    loi = [f"lỗi {i}" for i in range(11)]

    class _TT:
        TEP_TOM_TAT_ABS = tt.TEP_TOM_TAT_ABS

        @staticmethod
        def nap_tom_tat_abstract(dash):
            return {}

        @staticmethod
        def ghi_tom_tat(endnote, files, **kw):
            return {"trich_dan": 3, "co_ban_ghi": 3, "da_ghi": 0, "se_ghi": 0, "khong_doi": 3, "khong_co_ban_ghi": [],
                    "loi": loi, "tom_tat_may": 0, "tom_tat_lech_so": [], "tham_khao_chua_tom_tat": ["PMID 4"],
                    "tham_khao_bo_qua": ["PMID 3"]}

    N._nap_doc_data = lambda: None
    N.chay_tom_tat(object(), [DASH], None, False, tt=_TT)
    ra = capsys.readouterr().out
    assert "… và 3 cảnh báo khác chưa in" in ra, "phần cảnh báo bị cắt phải được đếm, không cắt im lặng"
    dong_chua = next(x for x in ra.splitlines() if "CHƯA có tóm tắt máy" in x)
    dong_bo = next(x for x in ra.splitlines() if "Cố ý KHÔNG tóm tắt máy" in x)
    assert "PMID 4" in dong_chua and "PMID 3" not in dong_chua
    assert "PMID 3" in dong_bo and "KHÔNG soạn đè" in dong_bo


def test_kiem_kho_dem_bo_qua_rieng_khong_tinh_rong(tmp_path, capsys):
    kho = {"muc": {"PMID 1": {**TOM_TAT, "soan": SOAN}, "PMID 2": {"bo_qua": BO_QUA, "soan": SOAN}, "PMID 3": {"soan": SOAN}}}
    (tmp_path / tt.TEP_TOM_TAT_ABS).write_text(json.dumps(kho, ensure_ascii=False), encoding="utf-8")
    assert tt.main(["--kiem", str(tmp_path)]) == 0
    ra = capsys.readouterr().out
    assert "«PMID 2»" not in ra and "«PMID 3»: không có trường hợp lệ" in ra
    assert "0 lỗi khuôn · 1 mục rỗng · 1 mục cố ý bỏ qua (bo_qua)" in ra


# ── Hai skill dạy khuôn kho (luật «thêm luật ở cổng thì dạy agent cùng lúc») ────────────────────────────────────────────
@pytest.mark.parametrize("ten", ("cap-nhat-chung-cu-y-khoa", "dark-analyst"))
def test_skill_day_soan_bo_qua_va_bo_cau_loi_thoi(ten: str) -> None:
    van_ban = (REPO / "sync" / "skills" / ten / "SKILL.md").read_text(encoding="utf-8")
    i = van_ban.index("SOẠN mục cho kho")
    khoi = van_ban[i:i + 2000]
    assert '`"soan"`' in khoi and '`"bo_qua"`' in khoi, f"{ten}: chưa dạy hai trường siêu dữ liệu"
    assert "KHÔNG soạn tóm tắt đè" in khoi, f"{ten}: chưa dạy luật không soạn đè mục bo_qua"
    assert "bỏ qua IM LẶNG" not in van_ban, f"{ten}: còn câu lỗi thời — từ TT-08 khoá/trường sai đã bị BÁO, không im lặng"
