# -*- coding: utf-8 -*-
"""BH137/BH138 — sổ nguồn phải nói thật về CÁI GÌ tồn tại và nó ĐANG ra sao (30/09/2026).

Lượt đo sống 30/09 lộ ba client nguồn của engine (RxNorm, EMA medicines, Scite public) có từ 20/09 mà `data/sources.json`
không có mục, thêm Unpaywall khi đối chiếu cả tập module — «nguồn không khai báo thì với hệ nó không tồn tại», nên
`sources_health.py` không bao giờ thấy chúng (EMA trả 403 mà không dòng nào báo). BH137 buộc mọi `app/sources/*.py` của
engine phải trỏ tới một mục sổ (hoặc khai miễn có lý do); nhánh có engine không chạy được trên bản sao trần nên các ca
dưới đây dựng thư mục nguồn tạm để biết chốt còn cắn. BH138: xem `test_giam_sat_to_chuc_20260930_nhan_theo_luot_quet.py`.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "chot_hoi_quy_bai_hoc.py"
_TEN = "chot_bh137_20260930"
_sp = importlib.util.spec_from_file_location(_TEN, _TEP)
C = importlib.util.module_from_spec(_sp)
sys.modules[_TEN] = C
_sp.loader.exec_module(C)

BANG = C._BH137_MODULE_NGUON


def _ma_so_that() -> set:
    return {s["id"] for s in json.loads((C.REPO / "data" / "sources.json").read_text(encoding="utf-8"))["sources"]}


def _dung_engine(tmp_path: Path, ten_tep) -> Path:
    nguon = tmp_path / "medical-ebm-automation" / "app" / "sources"
    nguon.mkdir(parents=True)
    for ten in ten_tep:
        (nguon / ten).write_text("", encoding="utf-8")
    return nguon


def test_bh137_va_bh138_dat_tren_repo_that() -> None:
    ok, ct = C.bh137_so_nguon_phu_module_engine_va_do_phu_khong_noi_qua()
    assert ok, ct
    ok, ct = C.bh138_nhan_tram_web_hoi_theo_luot_quet_gan_nhat()
    assert ok, ct


def test_hai_chot_da_dang_ky_trong_bai_hoc() -> None:
    """Hàm chốt không nằm trong BAI_HOC thì không lượt nào gọi — viết ra mà không chạy (BH41)."""
    theo_ma = {ma: ham for ma, _ngay, _ten, ham in C.BAI_HOC}
    assert theo_ma["BH137"] is C.bh137_so_nguon_phu_module_engine_va_do_phu_khong_noi_qua
    assert theo_ma["BH138"] is C.bh138_nhan_tram_web_hoi_theo_luot_quet_gan_nhat


def test_engine_khop_du_bang_thi_dat_that_khong_phai_kiem_yeu(tmp_path: Path) -> None:
    ok, ct = C._bh137_kiem_module(_dung_engine(tmp_path, BANG), BANG)
    assert ok and not ct.startswith("⚪"), ct


def test_module_nguon_moi_cua_engine_chua_khai_thi_do(tmp_path: Path) -> None:
    """Đúng ca 20/09: engine thêm `rxnorm.py`/`ema_medicines.py`/`scite_public.py` mà sổ không có mục."""
    ok, ct = C._bh137_kiem_module(_dung_engine(tmp_path, [*BANG, "nguon_moi_tinh.py"]), BANG)
    assert ok is False
    assert "nguon_moi_tinh.py" in ct and "CHƯA khai trong sổ" in ct


def test_bo_mot_nguon_khoi_bang_thi_engine_that_lam_chot_do(tmp_path: Path) -> None:
    """Gỡ dòng `rxnorm.py` khỏi bảng (tức quay về trạng thái trước 30/09) ⇒ engine có tệp đó phải làm chốt đỏ."""
    thieu = {k: v for k, v in BANG.items() if k != "rxnorm.py"}
    ok, ct = C._bh137_kiem_module(_dung_engine(tmp_path, BANG), thieu)
    assert ok is False and "rxnorm.py" in ct


def test_bang_nhac_module_da_go_khoi_engine_thi_do(tmp_path: Path) -> None:
    ok, ct = C._bh137_kiem_module(_dung_engine(tmp_path, [t for t in BANG if t != "unpaywall.py"]), BANG)
    assert ok is False
    assert "unpaywall.py" in ct and "KHÔNG còn trong engine" in ct


def test_engine_vang_thi_dat_nhung_phai_khai_kiem_yeu_hon(tmp_path: Path) -> None:
    """Bản sao trần/CI không có engine: không đỏ giả, nhưng «đạt» không được ngầm nói đã đối chiếu (khuôn BH107)."""
    ok, ct = C._bh137_kiem_module(tmp_path / "khong-co" / "app" / "sources", BANG)
    assert ok is True and ct.startswith("⚪ KIỂM YẾU HƠN")


def test_moi_ma_src_trong_bang_co_that_trong_so() -> None:
    ok, ct = C._bh137_kiem_bang(BANG, _ma_so_that())
    assert ok, ct


def test_bang_tro_toi_ma_src_khong_co_trong_so_thi_do() -> None:
    ok, ct = C._bh137_kiem_bang({**BANG, "rxnorm.py": ("SRC-999",)}, _ma_so_that())
    assert ok is False and "rxnorm.py" in ct and "SRC-999" in ct


def test_muc_so_bi_xoa_thi_module_tro_toi_no_lam_chot_do() -> None:
    """Xoá mục RxNorm khỏi sổ (SRC-047) mà engine còn client ⇒ bảng phải chỉ ra đúng module mất mục."""
    ok, ct = C._bh137_kiem_bang(BANG, _ma_so_that() - {"SRC-047"})
    assert ok is False and "rxnorm.py" in ct and "SRC-047" in ct


@pytest.mark.parametrize("gia_tri", ["miễn:", "miễn: x", "bỏ qua: tệp này không quan trọng lắm đâu", "", ()])
def test_mien_phai_co_ly_do_doc_duoc(gia_tri) -> None:
    ok, ct = C._bh137_kiem_bang({**BANG, "zotero.py": gia_tri}, _ma_so_that())
    assert ok is False and "zotero.py" in ct


def test_bh137_do_khi_tuyen_bo_do_phu_quay_ve_cach_dem_cu(monkeypatch) -> None:
    """Chốt phải NỐI tới hành vi của `tuyen_bo_do_phu.tra_khoi()`: thay công cụ bằng bản đếm kiểu cũ (mọi nguồn active
    nằm dưới «Đang giám sát tự động», không có dòng «gọi theo yêu cầu») thì cả bước kiểm lẫn BH137 phải đỏ."""
    nap_that = C._nap

    class _CongCuCu:
        GOC = C.REPO

        @staticmethod
        def _ten(s: dict) -> str:
            return s["name"].split("—")[0].strip()

        @staticmethod
        def tra_khoi() -> str:
            return ("ĐỘ PHỦ NGUỒN (cập nhật 2026-09-30)\n"
                    "Đang giám sát tự động: 3 nguồn — PubMed; GOLD; RxNorm; nhịp tuần/tháng.")

    def _nap_gia(duong_dan, ten):
        return _CongCuCu if Path(duong_dan).name == "tuyen_bo_do_phu.py" else nap_that(duong_dan, ten)

    monkeypatch.setattr(C, "_nap", _nap_gia)
    ok, ct = C._bh137_kiem_do_phu()
    assert ok is False and "Đang giám sát tự động" in ct
    ok, ct = C.bh137_so_nguon_phu_module_engine_va_do_phu_khong_noi_qua()
    assert ok is False and "Đang giám sát tự động" in ct


def test_muc_manual_mang_endpoint_may_bi_chi_ra() -> None:
    """Đúng ca 22/09→30/09: connector MCP (`mcp:…`) và API chờ token (`https://…`) khai `access: manual` ⇒ bị tuyên bố độ
    phủ đếm là làn nhập tay. Làn nhập tay thật (endpoint null) không bị bắt nhầm; sổ thật hiện không còn mục nào như vậy."""
    gia = [
        {"id": "SRC-021", "access": "manual", "endpoint_or_url": None},
        {"id": "SRC-041", "access": "manual", "endpoint_or_url": "mcp:wiley-scholar-gateway (semanticSearch)"},
        {"id": "SRC-036", "access": "manual", "endpoint_or_url": "https://api.epistemonikos.org/v1/documents/search"},
        {"id": "SRC-038", "access": "api", "endpoint_or_url": "https://www.cochranelibrary.com"},
        {"id": "SRC-0XX", "access": "manual"},
    ]
    assert C._bh137_manual_co_endpoint_may(gia) == ["SRC-041", "SRC-036"]
    so = json.loads((C.REPO / "data" / "sources.json").read_text(encoding="utf-8"))["sources"]
    assert C._bh137_manual_co_endpoint_may(so) == []


def test_bh137_do_khi_so_co_muc_manual_mang_endpoint_may(monkeypatch) -> None:
    """Phép kiểm trên phải NẰM TRONG BH137 (nối dây): giả lập sổ thật có một mục như vậy ⇒ BH137 đỏ, nêu đúng mã."""
    monkeypatch.setattr(C, "_bh137_manual_co_endpoint_may", lambda so: ["SRC-999"])
    ok, ct = C.bh137_so_nguon_phu_module_engine_va_do_phu_khong_noi_qua()
    assert ok is False and "SRC-999" in ct and "access: manual" in ct


def test_bh137_do_khi_dong_nhap_thu_cong_quay_ve_nhan_viet_cung(monkeypatch) -> None:
    """Công cụ THẬT nhưng dòng «Nhập thủ công» bị trả về dạng cũ (nhãn «(BYT · Cục QLD)» viết cứng + con số gộp mọi mục
    `manual`) ⇒ BH137 phải đỏ ở đúng phép kiểm dòng đó — các phép kiểm khác của tuyên bố vẫn đạt nên đây là phép DUY NHẤT
    giữ chuyện này."""
    nap_that = C._nap

    def _nap_cu(duong_dan, ten):
        mod = nap_that(duong_dan, ten)
        if Path(duong_dan).name == "tuyen_bo_do_phu.py":
            mod._dong_nhap_thu_cong = lambda manual: (
                f"Nhập thủ công (VN): {len(manual)} làn (BYT · Cục QLD) — số văn bản đã nhập: "
                f"{sum(1 for s in manual if s.get('last_success_at'))}; còn [CẦN XÁC NHẬN TẠI ĐƠN VỊ].")
        return mod

    monkeypatch.setattr(C, "_nap", _nap_cu)
    ok, ct = C._bh137_kiem_do_phu()
    assert ok is False and "Nhập thủ công" in ct and "BYT · Cục QLD" in ct


def test_bh137_noi_du_cac_buoc_kiem(monkeypatch, tmp_path: Path) -> None:
    """Mỗi bước phải thật sự NẰM TRONG BH137 — một bước viết ra mà không được gọi thì không canh gì (đột biến «bỏ bước
    tự kiểm răng» từng sống sót trước khi có ca này)."""
    monkeypatch.setattr(C, "_bh137_tu_kiem_rang", lambda: (False, "răng giả lập hỏng"))
    assert C.bh137_so_nguon_phu_module_engine_va_do_phu_khong_noi_qua() == (False, "răng giả lập hỏng")
    monkeypatch.undo()

    monkeypatch.setattr(C, "_BH137_MODULE_NGUON", {**BANG, "rxnorm.py": ("SRC-999",)})
    ok, ct = C.bh137_so_nguon_phu_module_engine_va_do_phu_khong_noi_qua()
    assert ok is False and "SRC-999" in ct
    monkeypatch.undo()

    # Bước cuối: đối chiếu với thư mục nguồn của ENGINE mà `_goc_mea()` chỉ tới — dựng engine tạm có một module lạ.
    nguon = _dung_engine(tmp_path, [*BANG, "nguon_moi_tinh.py"])
    monkeypatch.setattr(C, "_goc_mea", lambda repo=None: nguon.parents[1])
    ok, ct = C.bh137_so_nguon_phu_module_engine_va_do_phu_khong_noi_qua()
    assert ok is False and "nguon_moi_tinh.py" in ct


def test_bon_nguon_dang_ky_30_09_co_muc_va_trang_thai_dung_so_do() -> None:
    """Bốn nguồn engine đăng ký muộn ngày 30/09 phải CÓ mục; EMA ghi đúng số đo (403 ⇒ degraded, không phải active)."""
    so = {s["id"]: s for s in json.loads((C.REPO / "data" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    for ten, ma in (("rxnorm.py", "SRC-047"), ("ema_medicines.py", "SRC-048"), ("scite_public.py", "SRC-049"),
                    ("unpaywall.py", "SRC-051")):
        assert BANG[ten] == (ma,)
        assert so[ma]["scan_frequency"] == "ad-hoc", ma
        assert so[ma]["endpoint_or_url"].startswith("https://"), ma
        assert so[ma].get("last_probe_at"), ma
    assert so["SRC-048"]["status"] in {"degraded", "broken", "active"}
    if so["SRC-048"]["status"] != "active":
        assert so["SRC-048"]["known_gap"] and "403" in so["SRC-048"]["known_gap"]


def test_doi_chieu_voi_engine_that_khi_co_mat() -> None:
    """Trên máy có engine (lồng hoặc anh em): TẬP module thật phải khớp bảng.

    Cùng quy ước với `tools/conftest.py`: CHỈ bản sao git trần (cả ba gốc dữ liệu vắng — CI, worktree tươi) mới được bỏ
    qua, và phải nói rõ lý do; máy còn cây dữ liệu mà thiếu thư mục nguồn của engine là sự cố thật ⇒ ĐỎ, không bỏ qua."""
    nguon = C._goc_mea() / "app" / "sources"
    if not nguon.is_dir():
        bst = C._nap(C.REPO / "tools" / "ban_sao_tran.py", "bst_test_bh137")
        if bst.ban_sao_git_tran(C.REPO):
            pytest.skip("bản sao git trần — không có medical-ebm-automation để đối chiếu module thật; phép này chỉ chạy "
                        "ở máy có engine (các ca fixture phía trên vẫn canh logic)")
        pytest.fail(f"máy còn cây dữ liệu nhưng không thấy {nguon} — engine hỏng dở, không phải bản sao trần")
    ok, ct = C._bh137_kiem_module(nguon, BANG)
    assert ok and not ct.startswith("⚪"), ct
