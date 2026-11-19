"""Luật «từ ghép bắt buộc kề nhau» không được mong manh khi kho lớn (kiểm toàn diện hệ chứng cứ 19/11/2026).

Đo trên sổ thật 3.248 thẻ: bộ vàng tra điểm khám tụt 80/80 → 73/80. Một nguyên nhân là hồi quy THUẬT TOÁN: MỘT tiêu đề
«CHỈ ĐỊNH KHÁNG ĐÔNG: rung nhĩ lâm sàng…» làm cặp vắt ranh giới cụm «đông | rung» thành «từ ghép» (luật cũ: kề nhau ở
≥1 tiêu đề) ⇒ thẻ «Kháng đông đường uống cho rung nhĩ (DOAC ưu tiên)» bị loại, câu «chống đông rung nhĩ DOAC» ra rỗng.
Luật mới (`_la_tu_ghep`): kề nhau ≥50% số tiêu đề có cả hai vế, HOẶC ≥3 tiêu đề với tỉ lệ ≥10%.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tra_diem_kham as tdk  # noqa: E402
from test_tra_diem_kham_20260921 import the  # noqa: E402

# Kho dựng theo đúng hình dạng sổ thật: nhiều thẻ có «rung nhĩ» + «kháng/chống đông» KHÔNG kề nhau, MỘT thẻ «bẫy» kề nhau.
KHO_RUNG_NHI = [
    the(1, "CHỈ ĐỊNH KHÁNG ĐÔNG: rung nhĩ lâm sàng có nguy cơ huyết khối"),          # bẫy: «đông rung» kề nhau 1 lần
    the(2, "Kháng đông đường uống cho rung nhĩ (DOAC ưu tiên)"),                       # thẻ ĐÚNG cho câu hỏi
    the(3, "Đột quỵ do rung nhĩ: khởi đầu kháng đông sớm (≤4 ngày)"),
    the(4, "Nối lại kháng đông sau xuất huyết não ở bệnh nhân rung nhĩ"),
    the(5, "Rung nhĩ ở người cao tuổi: kháng đông vẫn có lợi ròng"),
    the(6, "Phối hợp chống đông và kháng tiểu cầu sau đặt stent ở rung nhĩ"),
    the(7, "Thuốc chống đông khi nhổ răng: không cần ngừng"),
    the(8, "Thuốc chống đông quanh phẫu thuật: bắc cầu không cần thiết"),
    the(9, "Đảo ngược thuốc chống đông khi chảy máu nặng"),
    the(10, "Liều thuốc chống đông theo chức năng thận"),
    the(11, "Tăng huyết áp: đích dưới 130 mmHg"),
    the(12, "Tăng huyết áp ở người cao tuổi"),
    the(13, "Tăng huyết áp kháng trị: thêm spironolacton"),
    the(14, "Tăng nguy cơ huyết khối tĩnh mạch khi dùng estrogen"),
    # «tăng cân»: từ ghép thật có thành phần PHỔ BIẾN — kề nhau 3 lần nhưng tỉ lệ < 50% (như sổ thật 11/69)
    the(15, "Tăng cân do corticoid kéo dài"),
    the(16, "Tăng cân khi dùng insulin"),
    the(17, "Tăng cân do thuốc chống loạn thần"),
    the(18, "Tăng liều levothyroxin theo cân nặng"),
    the(19, "Tăng liều heparin theo cân nặng ở người béo phì"),
    the(20, "Tăng liều kháng sinh theo cân nặng ở trẻ"),
    the(21, "Tăng thời gian theo dõi và cân nhắc chuyển tuyến"),
    the(22, "Tăng tần suất đo đường huyết khi cân nặng thay đổi"),
]


def test_cap_vat_ranh_gioi_cum_khong_thanh_tu_ghep():
    ci = tdk._dung_chi_muc(KHO_RUNG_NHI)
    assert ci["df_cap"].get(("dong", "rung")) == 1                     # có một tiêu đề kề nhau (bẫy)
    assert tdk._la_tu_ghep(("dong", "rung"), ci) is False              # 1/7 tiêu đề có cả hai vế ⇒ không phải từ ghép
    assert tdk._la_tu_ghep(("rung", "nhi"), ci) is True                # luôn kề nhau ⇒ từ ghép thật
    assert tdk._la_tu_ghep(("chong", "dong"), ci) is True              # 5/5
    assert tdk._la_tu_ghep(("tang", "huyet"), ci) is True              # 3/4 — «tăng … huyết khối» không phá
    assert tdk._la_tu_ghep(("dau", "dau"), {"df_cap": {("dau", "dau"): 1}, "the": []}) is True  # a = b: luật cũ
    assert tdk._la_tu_ghep(("abc", "xyz"), ci) is False                # chưa từng kề nhau


def test_chong_dong_rung_nhi_doac_ra_dung_the():
    ket, loai = tdk.tra_chi_tiet("chống đông rung nhĩ DOAC", KHO_RUNG_NHI)
    assert loai == "khop" and "T2" in {c["id"] for c in ket}, (loai, [c["topic"] for c in ket])


def test_tu_ghep_that_van_bat_buoc_ke_nhau():
    """«tăng huyết áp» là từ ghép thật (≥3 tiêu đề) ⇒ thẻ «Tăng nguy cơ huyết khối…» (hai vế rời nhau) không được ra."""
    ket, _ = tdk.tra_chi_tiet("tăng huyết áp người cao tuổi", KHO_RUNG_NHI)
    assert "T14" not in {c["id"] for c in ket}, [c["topic"] for c in ket]
    assert "T12" in {c["id"] for c in ket}


def test_tu_ghep_thanh_phan_pho_bien_giu_nho_nhanh_ba_tieu_de():
    ci = tdk._dung_chi_muc(KHO_RUNG_NHI)
    ke, cung = ci["df_cap"].get(("tang", "can")), sum(1 for x in ci["the"] if {"tang", "can"} <= x["chinh"])
    assert ke == 3 and ke / cung < 0.5, (ke, cung)
    assert tdk._la_tu_ghep(("tang", "can"), ci) is True
    ket, _ = tdk.tra_chi_tiet("tăng cân", KHO_RUNG_NHI)
    assert ket and all(c["id"] in {"T15", "T16", "T17"} for c in ket), [c["topic"] for c in ket]
