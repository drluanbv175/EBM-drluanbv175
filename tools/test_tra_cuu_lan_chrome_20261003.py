"""Làn Chrome có bác sĩ cho Scopus / Web of Science (03/10/2026 — bác sĩ quyết: «Scopus,Web of Science giữ nguyên và kết hợp mở Chrome
để tôi đăng nhập sau đó thực hiện theo tác vụ yêu cầu»).

Làn Export giữ nguyên; làn Chrome chỉ MỞ khi tệp quyết định có uỷ quyền còn hiệu lực cho ĐÚNG khoá «Scopus (Elsevier)» /
«Clarivate (Web of Science)». Uỷ quyền đọc toàn văn bài Elsevier KHÔNG tự lan sang Scopus. Vắng/hỏng/hết hạn ⇒ làn ĐÓNG.
"""
from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("tctk_chrome_t", REPO / "tools" / "tra_cuu_co_tai_khoan.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
_spec2 = importlib.util.spec_from_file_location("dtv_chrome_t", REPO / "tools" / "doc_toan_van_co_nguoi.py")
D = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(D)

HOM_NAY = date(2026, 10, 3)
CAN_CU = "Scopus,Web of Science giữ nguyên và kết hợp mở Chrome để tôi đăng nhập sau đó thực hiện theo tác vụ yêu cầu"
SCOPUS, WOS = "Scopus (Elsevier)", "Clarivate (Web of Science)"
CHU_DE = [{"topic": "Viêm khớp dạng thấp (RA)", "truy_van_du_phong": "rheumatoid arthritis"}]


def _tep(tmp_path, *muc, noi_dung: str | None = None) -> Path:
    t = tmp_path / "dieu-khoan-bac-si-uy-quyen.json"
    t.write_text(noi_dung if noi_dung is not None else json.dumps({"muc": list(muc)}, ensure_ascii=False), encoding="utf-8")
    return t


def _muc(nxb: str, **sua) -> dict:
    m = {"nxb": nxb, "ngay": "2026-10-03", "can_cu": CAN_CU, "pham_vi": "Claude thao tác Chrome sau khi bác sĩ đăng nhập"}
    m.update(sua)
    return m


def test_hai_khoa_uy_quyen_la_khoa_cam_cua_bang_dieu_khoan() -> None:
    for nguon, khoa in T.KHOA_UY_QUYEN.items():
        assert D.DIEU_KHOAN_NXB.get(khoa, {}).get("ket_luan") == "cam", (nguon, khoa)


def test_mien_scopus_va_wos_nhan_dien_dung_khoa() -> None:
    assert D.nxb_cua("", "https://www.scopus.com/results/results.uri")[0] == SCOPUS
    assert D.nxb_cua("", "https://www.webofscience.com/wos/woscc/summary/x")[0] == WOS
    # Bài báo Elsevier (DOI 10.1016) vẫn thuộc khoá Elsevier, kể cả khi trang mở là Scopus — tiền tố DOI xét trước.
    assert D.nxb_cua("10.1016/j.jacc.2026.05.033", "https://www.scopus.com/record/x")[0] == "Elsevier"


def test_khong_co_tep_uy_quyen_thi_ca_hai_lan_dong(tmp_path) -> None:
    vb = T.phieu(CHU_DE, 2026, HOM_NAY, tmp_path / "khong-co.json")
    assert vb.count("Làn Chrome có bác sĩ: ĐÓNG") == 2
    assert "LÀN CHROME CÓ BÁC SĨ —" not in vb


def test_uy_quyen_scopus_chi_mo_lan_scopus(tmp_path) -> None:
    tep = _tep(tmp_path, _muc(SCOPUS))
    assert T.uy_quyen_lan_chrome("scopus", HOM_NAY, tep)["nxb"] == SCOPUS
    assert T.uy_quyen_lan_chrome("wos", HOM_NAY, tep) is None
    vb = T.phieu(CHU_DE, 2026, HOM_NAY, tep)
    assert vb.count("LÀN CHROME CÓ BÁC SĨ —") == 1 and vb.count("Làn Chrome có bác sĩ: ĐÓNG") == 1
    i_scopus, i_wos = vb.index("SCOPUS (https"), vb.index("WEB OF SCIENCE (https")
    assert i_scopus < vb.index("LÀN CHROME CÓ BÁC SĨ —") < i_wos, "làn mở phải nằm dưới mục Scopus, không dưới WoS"


def test_uy_quyen_elsevier_doc_toan_van_khong_lan_sang_scopus(tmp_path) -> None:
    tep = _tep(tmp_path, _muc("Elsevier", can_cu="Vậy hãy chỉnh sửa lại để máy đọc toàn văn và tóm tắt cho tôi"))
    assert T.uy_quyen_lan_chrome("scopus", HOM_NAY, tep) is None


@pytest.mark.parametrize("muc, noi_dung, mo_ta", [
    ([_muc(WOS, het_han="2026-10-02")], None, "hết hạn"),
    ([_muc(WOS, ngay="2026-10-09")], None, "ngày tương lai"),
    ([_muc(WOS, can_cu="ok")], None, "căn cứ quá ngắn"),
    ([], "{hỏng", "tệp hỏng"),
])
def test_uy_quyen_khong_hop_le_thi_lan_dong(tmp_path, muc, noi_dung, mo_ta) -> None:
    tep = _tep(tmp_path, *muc, noi_dung=noi_dung)
    assert T.uy_quyen_lan_chrome("wos", HOM_NAY, tep) is None, mo_ta
    assert "Làn Chrome có bác sĩ: ĐÓNG" in T.huong_dan_lan_chrome("wos", T.uy_quyen_lan_chrome("wos", HOM_NAY, tep))


def test_lan_mo_giu_bat_bien_an_toan() -> None:
    vb = T.huong_dan_lan_chrome("wos", _muc(WOS))
    for cum in ("TỰ đăng nhập", "không gõ tài khoản/mật khẩu", "không giải CAPTCHA", "MỘT câu hỏi", "không chạy theo lịch",
                "KHÔNG chép/lưu nội dung trang kết quả", "--nhap", "KHÔNG đổi"):
        assert cum in vb, cum


def test_nap_cong_cu_hong_thi_lan_dong(monkeypatch, tmp_path) -> None:
    tep = _tep(tmp_path, _muc(SCOPUS))

    def hong():
        raise ImportError("giả lập công cụ hỏng")

    monkeypatch.setattr(T, "_doc_toan_van", hong)
    assert T.uy_quyen_lan_chrome("scopus", HOM_NAY, tep) is None


@pytest.mark.parametrize("khoa", [SCOPUS, WOS])
def test_ghi_uy_quyen_nhan_hai_khoa_moi(tmp_path, khoa) -> None:
    tep = tmp_path / "dieu-khoan-bac-si-uy-quyen.json"
    ma, bao = D.ghi_uy_quyen(khoa, CAN_CU, pham_vi="thao tác Chrome sau khi bác sĩ đăng nhập", ghi=True, tep=tep, hom_nay=HOM_NAY)
    assert ma == 0, bao
    muc = json.loads(tep.read_text(encoding="utf-8"))["muc"]
    assert muc[-1]["nxb"] == khoa and muc[-1]["dieu_khoan_nxb_khong_doi"]["trich"]
