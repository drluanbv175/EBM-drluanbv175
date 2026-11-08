"""Hướng dẫn đọc của tóm tắt Word ★ mang luật 12 — năm lỗi kiểm chéo hay bắt (08/11/2026).

Vì sao có. Năm bản ★ đầu tiên (PMID 41540779, 42593701, 42481270, 42642341, 42673560) mỗi bản cần 2–3 lượt kiểm chéo độc lập
(~0,25 triệu token mỗi lượt) vì cùng năm loại lỗi: mất mức lời, tự thêm «chỉ khi», gộp sai quần thể của từng khuyến cáo, câu
«bài không nêu X» rộng hơn phạm vi, ghi sai nơi chứa dữ liệu. Ví dụ thật: «Chỉ khi không đáp ứng … mới đề nghị thuốc độ tin
cậy thấp» (AAN/AHS 2026 không có «chỉ khi» — câu đó có thể khiến bác sĩ từ chối amitriptyline cho người đau xơ cơ, trái khuyến
cáo 10). Luật nằm ngay trong HUONG-DAN-DOC.md mà agent đọc trước khi viết.
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import tom_tat_chung_cu_word as T  # noqa: E402


def test_huong_dan_doc_co_luat_12_va_du_nam_loi():
    hd = T.huong_dan_doc()
    assert "12. NĂM LỖI KIỂM CHÉO HAY BẮT" in hd
    for cum in ("MỨC LỜI", "«chỉ khi»", "QUẦN THỂ TỪNG KHUYẾN CÁO", "PHẠM\n   VI CÂU", "NƠI CHỨA DỮ LIỆU"):
        assert cum in hd, cum


def test_luat_12_dung_truoc_khuon_json():
    hd = T.huong_dan_doc()
    assert hd.index("12. NĂM LỖI") < hd.index("Khuôn JSON")
