"""Hai quyết định ngày 15/10/2026 về làn toàn văn: bản thảo tác giả PMC «TDM» + ba tổ chức guideline hô hấp.

VÌ SAO.
(1) Bác sĩ quyết 15/10/2026: bản thảo tác giả NIH trên PMC (`license_code: "TDM"`, Europe PMC `authMan: "Y"`) được máy TẢI và
    ĐỌC toàn văn, KỂ CẢ bài của NXB «cam» (ca đo PMID 22591294, NEJM 2012). Trước đó `duong_doc` thấy NXB «cam» là xếp
    «BÁC SĨ ĐỌC TRỰC TIẾP» dù `gom_toan_van_dashboard.py` tải được đúng bài đó từ PMC — phiếu bảo bác sĩ đọc tay một bài máy
    đã có quyền tải. Doctrine §2septies cũng ghi «ngoại lệ duy nhất là CC», lệch mã gom (#174).
(2) Rà làn toàn văn 15/10 (G3-D5): GOLD, GINA, BTS có làn toàn văn ở engine nhưng chưa được kiểm điều khoản theo §2septies
    mục 4. Đọc 15/10: cả ba im lặng về AI/TDM ⇒ «không rõ ⇒ xử như cấm», khớp theo MIỀN.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCTRINE = REPO / ".claude" / "agents" / "_CONNECTOR-CHUNG-CU.md"


def _nap(ten: str, tep: str):
    spec = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


DTV = _nap("dtv_pmc_tdm_20261015", "doc_toan_van_co_nguoi.py")

_NEJM_DOI = "10.1056/nejmoa1112421"


def _epmc(auth_man: str):
    def tra(pmid: str = "", doi: str = "") -> dict:
        return {"pmid": "22591294", "pmcid": "PMC3374857", "isOpenAccess": "N", "authMan": auth_man,
                "doi": _NEJM_DOI, "title": "Azithromycin and the risk of cardiovascular death"}
    return tra


def _doi_dich(doi: str) -> str:
    return f"https://www.nejm.org/doi/full/{doi}"


def test_ban_thao_tac_gia_pmc_cua_nxb_cam_di_duong_gom(tmp_path):
    """NEJM là «cam», nhưng bài có bản thảo tác giả trên PMC ⇒ «có bản PMC — chạy gom», không bắt bác sĩ đọc tay."""
    kq = DTV.duong_doc("22591294", "chua_co", _epmc("Y"), _doi_dich, tep_uy_quyen=tmp_path / "vang.json")
    assert kq["cach"] == "oa_chua_gom", kq
    assert kq["pmcid"] == "PMC3374857"
    assert "bản thảo tác giả" in kq["ly_do"] and "15/10/2026" in kq["ly_do"]


def test_doi_chung_khong_co_ban_thao_van_la_bac_si_doc(tmp_path):
    """Đối chứng: cùng bài NEJM mà KHÔNG có bản thảo tác giả ⇒ vẫn «bác sĩ đọc trực tiếp» (ngoại lệ chỉ cho bản PMC)."""
    kq = DTV.duong_doc("22591294", "chua_co", _epmc("N"), _doi_dich, tep_uy_quyen=tmp_path / "vang.json")
    assert kq["cach"] == "bac_si_doc_truc_tiep", kq


def test_ba_to_chuc_ho_hap_la_cam_khop_theo_mien():
    for url, ten in (("https://goldcopd.org/2025-gold-report/", "GOLD"),
                     ("https://ginasthma.org/2024-report/", "GINA"),
                     ("https://www.brit-thoracic.org.uk/quality-improvement/guidelines/", "BTS")):
        nxb, dk = DTV.nxb_cua("", url, "")
        assert nxb and nxb.startswith(ten), (url, nxb)
        assert dk["ket_luan"] == "cam" and dk["doc_luc"] == "2026-10-15", (url, dk)
        assert len(dk["trich"].split()) <= 15, f"{ten}: câu trích quá 15 từ"


def test_doctrine_day_hai_ngoai_le_pmc_va_khop_bang():
    van_ban = DOCTRINE.read_text(encoding="utf-8")
    i = van_ban.index("## 2septies. ")
    j = van_ban.find("\n## ", i + 5)
    muc = van_ban[i:j if j > 0 else len(van_ban)]
    muc1 = next(d for d in muc.splitlines() if d.startswith("1. **NXB"))
    muc7 = next(d for d in muc.splitlines() if d.startswith("7. **Bất biến"))
    assert "Ngoại lệ duy nhất" not in muc1, "mục 1 còn ghi «ngoại lệ duy nhất» là CC — lệch quyết định 15/10/2026"
    for cum in ("bản thảo tác giả trên PMC", '`license_code: "TDM"`', "bác sĩ quyết 15/10/2026", "KHÔNG phải «NXB cho phép»"):
        assert cum in muc1, f"mục 1 thiếu «{cum}»"
    assert "bản thảo tác giả PMC «TDM»" in muc7 and "PHIÊN UỶ QUYỀN LƯU BẢN SAO" in muc7, "mục 7 phải nêu ĐỦ hai ngoại lệ lưu"
    assert DTV.lech_doctrine(van_ban) == []
