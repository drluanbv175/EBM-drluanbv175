"""Bản đọc phải nói CÙNG điều với cổng liêm chính về sổ ký rút bài (BH109).

Ca thật 24/09/2026: bác sĩ ký miễn trừ ITEM-11 của TienLuongSuyTim_20260914 (thông báo rút bài
gắn vào guideline CCS/CHFS 2025 là của một BẢN ĐÍNH CHÍNH bị rút). Cổng đọc sổ ký và cho PASS,
nhưng bản đọc vẫn in dải đỏ «Nguồn đã bị rút — không dùng kết luận này», vì `khoi_rut_bai` chưa
bao giờ đọc sổ ký. Các test dưới đây dùng HÀM KIỂM CHỮ KÝ THẬT của cổng (không giả lập) để khoá:
  • ký hợp lệ ⇒ rời dải đỏ, sang khung trung tính có người ký · ngày · lý do (không bị giấu);
  • chưa ký / vân tay lệch / điền cho có ⇒ vẫn đỏ, nhãn «cần bác sĩ xem» như cổng;
  • rút bài THẬT không bao giờ hạ được qua sổ này;
  • không nạp được cổng ⇒ coi như chưa ký (fail-closed).
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_sp = importlib.util.spec_from_file_location("ban_doc_rut_bai_2409", REPO / "tools" / "build_ban_doc_chung_cu.py")
B = importlib.util.module_from_spec(_sp)
sys.modules["ban_doc_rut_bai_2409"] = B
_sp.loader.exec_module(B)

KY_HOP_LE = {
    "khoa": "pmid:41110921",
    "thong_bao_ids": ["41422828"],
    "da_xem_boi": "Bác sĩ Kiểm Thử",
    "ngay": "2026-09-20",
    "ly_do": "Đã đọc thông báo rút: đó là một bản đính chính trùng lặp; các đính chính còn hiệu lực không đổi khuyến cáo.",
}


def _ban_ghi(khoa="pmid:41110921", ids=("41422828",), sua_loi=True, tinh_trang="retracted", rut_va_thay=False,
             tieu_de="Guideline thử nghiệm"):
    loai, gia_tri = khoa.split(":", 1)
    return {"khoa": khoa, "loai": loai, "gia_tri": gia_tri, "tinh_trang": tinh_trang,
            "tieu_de": tieu_de, "kiem_luc": "2026-09-20", "nguon": "pubmed",
            "rut_va_thay": rut_va_thay, "thong_bao": "", "sua_loi_bi_rut": sua_loi,
            "thong_bao_ids": list(ids)}


@pytest.fixture
def dung(tmp_path, monkeypatch):
    """Dựng dashboard giả + sổ ký trong tmp; trả hàm chạy `khoi_rut_bai` với danh sách bản ghi cho trước."""
    def _chay(ban_ghi, so_ky=None):
        src = tmp_path / "WebDashboard_EBM_Thu_20260924.html"
        src.write_text("<html></html>", encoding="utf-8")
        if so_ky is not None:
            (tmp_path / "rut-bai-da-xem-xet.json").write_text(json.dumps({"muc": so_ky}, ensure_ascii=False),
                                                                encoding="utf-8")
        gia = types.ModuleType("so_xac_minh_nguon")
        gia.nguon_da_rut = lambda ten: [dict(r) for r in ban_ghi]
        monkeypatch.setitem(sys.modules, "so_xac_minh_nguon", gia)
        return B.khoi_rut_bai(src)
    return _chay


def test_ky_hop_le_roi_dai_do_sang_khung_trung_tinh_khong_bi_giau(dung):
    html = dung([_ban_ghi()], [KY_HOP_LE])
    assert 'class="rutbai"' not in html, "đã ký hợp lệ mà vẫn in dải đỏ — đúng lỗi 24/09"
    assert "không dùng kết luận" not in html
    assert "Cờ rút bài đã được bác sĩ xem xét (1 định danh)" in html
    for manh in ("Bác sĩ Kiểm Thử", "2026-09-20", "bản đính chính trùng lặp", "41422828"):
        assert manh in html, f"mục đã ký phải còn liệt kê kèm «{manh}» để rà lại được"


def test_chua_ky_van_do_voi_nhan_can_bac_si_xem_nhu_cong(dung):
    html = dung([_ban_ghi()])
    assert 'class="rutbai"' in html
    assert "CẦN BÁC SĨ XEM" in html and "cần bác sĩ xem" in html
    assert "<em>đã bị rút</em>" not in html, "thông báo rút là bản đính chính — chưa chắc bài chính bị rút"


def test_van_tay_lech_thi_van_do(dung):
    ky = dict(KY_HOP_LE, thong_bao_ids=["99999999"])
    html = dung([_ban_ghi()], [ky])
    assert 'class="rutbai"' in html and "đã được bác sĩ xem xét" not in html


@pytest.mark.parametrize("sua", [
    {"ly_do": "[CẦN BÁC SĨ ĐIỀN]"},
    {"da_xem_boi": "N/A"},
    {"ngay": "2099-01-01"},
])
def test_dien_cho_co_thi_van_do(dung, sua):
    html = dung([_ban_ghi()], [dict(KY_HOP_LE, **sua)])
    assert 'class="rutbai"' in html and "đã được bác sĩ xem xét" not in html


def test_rut_bai_that_khong_ha_duoc_qua_so_ky(dung):
    html = dung([_ban_ghi(sua_loi=False)], [KY_HOP_LE])
    assert "Nguồn đã bị rút — không dùng kết luận này" in html
    assert "<em>đã bị rút</em>" in html and "đã được bác sĩ xem xét" not in html


def test_hai_dinh_danh_ky_rieng_tung_khoa(dung):
    ghi = [_ban_ghi(), _ban_ghi(khoa="doi:10.1016/j.cjca.2025.07.027", ids=("10.1016/j.cjca.2025.12.001",))]
    html = dung(ghi, [KY_HOP_LE])
    assert "Cờ rút bài đã được bác sĩ xem xét (1 định danh)" in html
    assert "CẦN BÁC SĨ XEM — chưa dùng kết luận này cho tới khi xem xét (1 nguồn)" in html
    assert "doi:10.1016/j.cjca.2025.07.027" in html.split('class="xungdot daxem"')[0], "DOI chưa ký phải ở dải đỏ"


def test_khong_nap_duoc_cong_la_chua_ky(dung, monkeypatch):
    monkeypatch.setattr(B, "_ham_kiem_so_ky_rut_bai", lambda: None)
    html = dung([_ban_ghi()], [KY_HOP_LE])
    assert 'class="rutbai"' in html and "không kiểm được sổ ký" in html
    assert "đã được bác sĩ xem xét" not in html


def test_ly_do_duoc_escape(dung):
    ky = dict(KY_HOP_LE, ly_do="Đã đọc thông báo <script>alert(1)</script> và các đính chính còn hiệu lực kỹ càng.")
    html = dung([_ban_ghi()], [ky])
    assert "<script>" not in html and "&lt;script&gt;" in html


@pytest.mark.parametrize("so_ky", [None, [KY_HOP_LE]], ids=["dai-do", "khung-da-xem"])
def test_tieu_de_luu_dang_thuc_the_chi_escape_mot_lan(dung, so_ky):
    """Sổ lưu «(LVEF &gt; 40%)» như nguồn trả về — escape thẳng thành «&amp;gt;» và trang in nguyên «&gt;»."""
    html = dung([_ban_ghi(tieu_de="Heart Failure (LVEF &gt; 40%) &lt;script&gt;")], so_ky)
    assert "(LVEF &gt; 40%)" in html and "&amp;gt;" not in html
    assert "<script>" not in html, "giải thực thể không được mở đường chèn mã"


def test_dung_dung_ham_kiem_cua_cong_khong_chep_luat():
    """Bản đọc phải dùng CHÍNH hàm của cổng — chép luật sang đây là mầm của lần lệch tiếp theo."""
    ham = B._ham_kiem_so_ky_rut_bai()
    assert ham is not None and ham.__name__ == "_da_xem_xet_thong_bao_dinh_chinh"
    goc = REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "tools" / "verify_dashboard.py"
    sp = importlib.util.spec_from_file_location("vd_goc_2409", goc)
    vd = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(vd)
    assert inspect.getsource(ham) == inspect.getsource(vd._da_xem_xet_thong_bao_dinh_chinh)
    assert "_da_xem_xet_thong_bao_dinh_chinh" not in inspect.getsource(B.khoi_rut_bai), \
        "khoi_rut_bai phải gọi qua _ham_kiem_so_ky_rut_bai, không tự định nghĩa lại"
