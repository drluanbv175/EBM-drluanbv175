# -*- coding: utf-8 -*-
"""Trình bày khối «EBM · ĐỌC NHANH» trong EndNote (13/10/2026) — nhấn mạnh bằng NHÃN IN HOA + biểu tượng màu BMP.

Bác sĩ: «nội dung cần nhấn mạnh hãy in đậm», «có thể hiện được màu sắc không». Đo 13/10: EndNote 2025 không ghi được chữ đậm
qua AppleScript và trường không có màu chữ; ký tự ngoài BMP bị đổi thành «?». Ngoại tuyến hoàn toàn.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("_tt_trinh_bay", REPO / "tools/tom_tat_endnote_vi.py")
tt = importlib.util.module_from_spec(sp)
sp.loader.exec_module(tt)

MUC = {"id": "ITEM-01", "title": "Điểm nhấn", "source": "X", "design": "RCT", "dateVersion": "2024", "pmid": "31111111",
       "pico": {"P": ["Người lớn", "match"], "I": ["Thuốc A", "match"], "C": ["Giả dược", "match"], "O": ["Tử vong", "match"]},
       "effectText": "Giảm tử vong", "gradeLevel": "high", "decision": "apply", "action": "Dùng thuốc A",
       "safety": "Theo dõi kali máu", "flag": "Không dùng khi thai kỳ", "vn": "Có BHYT",
       "references": ["Phụ lục: Smith J. PMID 32222222"]}


def _doc(bang: dict):
    return lambda p: bang.get(Path(p).name)


def _khoi(pmid: str, **thay) -> str:
    f = Path("/khong-ton-tai/WebDashboard_X_20260614.html")
    d = {"meta": {"question": "Q"}, "items": [dict(MUC, **thay)]}
    return tt.khoi_tieng_viet(tt.ngu_canh([f], _doc({f.name: d}))[f"pmid:{pmid}"], None)


def test_moi_nhan_nam_trong_bmp_vi_endnote_doi_ky_tu_ngoai_bmp_thanh_dau_hoi():
    nhan = [*tt.NHAN_QD.values(), *tt.NHAN_DONG.values(), *tt.NHAN_KHOP.values(), tt.MO_DAU,
            *(n for _, n in tt.NHAN_PICO), *(n for _, n in tt.NHAN_TOM_TAT)]
    ngoai = sorted({c for s in nhan for c in s if ord(c) > 0xFFFF})
    assert not ngoai, f"nhãn có ký tự ngoài BMP: {ngoai}"


def test_moi_phan_co_dau_mau_va_nhan_in_hoa():
    dong = _khoi("31111111").splitlines()
    assert dong[0].startswith(f"{tt.MO_DAU} ✅ ÁP DỤNG NGAY · Chứng cứ: Cao")
    assert dong[1] == "⭐ Điểm nhấn"
    for dau in ("▶️ KẾT QUẢ: Giảm tử vong", "✅ THỰC HÀNH: Dùng thuốc A", "⛔ AN TOÀN: Theo dõi kali máu",
                "⚠️ LƯU Ý: Không dùng khi thai kỳ", "▶️ TẠI VIỆT NAM: Có BHYT", "   P · ĐỐI TƯỢNG: Người lớn"):
        assert dau in dong, dau


def test_an_toan_luon_mang_dau_do_va_quyet_dinh_mang_dau_rieng():
    assert tt.NHAN_DONG["safety"].startswith("⛔"), "an toàn phải nổi màu đỏ"
    dau = {v.split()[0] for v in tt.NHAN_QD.values()}
    assert len(dau) == len(tt.NHAN_QD), "ba mức quyết định phải phân biệt được bằng dấu màu"
    assert _khoi("31111111", decision="consider").splitlines()[0].startswith(f"{tt.MO_DAU} ⚠️ CÂN NHẮC CHỌN LỌC")


def test_tham_khao_co_dau_rieng_khong_mang_dau_quyet_dinh():
    k = _khoi("32222222")
    assert k.startswith(f"{tt.MO_DAU} ℹ️ TÀI LIỆU THAM KHẢO BỔ TRỢ") and "\n⭐ Cho mục «Điểm nhấn»" in k
    for dau in tt.NHAN_QD.values():
        assert dau not in k, "bài tham khảo không mang khuyến nghị của nguồn chính"
