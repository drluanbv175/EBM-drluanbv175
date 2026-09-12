#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `kiem_tuong_thich_da_nen.py` — ngoại tuyến, không phụ thuộc
`medical-ebm-automation/` có mặt hay không (tự dựng fixture bằng tempfile),
để chạy được cả trên bản sao git trần (cloud/CI).

VÌ SAO CÓ (12/09/2026): `_mask_khong_phai_code()` (bản cũ, tách chuỗi con thô
trên `\"\"\"`/`'''`) mất khả năng phân biệt "ba ký tự nháy là DẤU MỞ/ĐÓNG
docstring thật" với "ba ký tự nháy chỉ là NỘI DUNG của một chuỗi một-nháy
khác" — ca thật: `medical-ebm-automation/tools/kiem_newline_vung_ky.py`,
hàm `_la_chuoi_ba_nhay()`, có dòng mã
`return phan_con_lai.startswith('\"\"\"') or phan_con_lai.startswith("'''")`.
Chuỗi một-nháy `'\"\"\"'` bị hiểu nhầm là MỞ một docstring mới, làm lệch pha
trạng thái "đang trong docstring" cho TOÀN BỘ phần còn lại của file — một
docstring THẬT ở xa hơn (câu ví dụ minh hoạ `.write_text(...,
encoding=\"utf-8\")` cho một bug CŨ đã vá) bị coi là mã thật nên không được
che, khiến luật R6 báo 🔴 tại dòng văn xuôi đó thay vì một lời gọi
`write_text()` thật đang thiếu `newline=`.

Đã vá bằng cách thay `_mask_khong_phai_code()` sang `tokenize` chuẩn của
Python (bản tách-chuỗi-thô cũ đổi tên thành `_mask_khong_phai_code_ngay_tho`,
giữ lại làm dự phòng khi tokenize thất bại — file lỗi cú pháp từ trước).

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`):
  (1) chỉ kiểm HÀNH VI bằng cách gọi vào mã đang sống, không đếm chuỗi trong file;
  (2) mỗi ca gắn với một rủi ro THẬT đã nêu trong docstring của công cụ;
  (3) nhanh và ngoại tuyến — KHÔNG cần medical-ebm-automation/ tồn tại.

Kiểm bằng đột biến (thực hiện thủ công khi vá, không mã hoá lại ở đây — xem
mô tả trong PR/commit): gọi `_mask_khong_phai_code_ngay_tho()` (bản CŨ) trên
CHÍNH fixture tái hiện bug ở `test_ban_cu_ngay_tho_van_con_loi_lech_pha_da_biet`
để chứng minh bản cũ vẫn sinh đúng báo động giả nếu ai đó lỡ dùng lại nó cho
đường đi chính — tức test này tự làm luôn vai trò "đột biến ngược" (quay về
mã cũ) mà không cần sửa file nguồn.

Chạy:  python3 tools/test_kiem_tuong_thich_da_nen.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem_tuong_thich_da_nen as ktd  # noqa: E402


# Fixture tái hiện Y NGUYÊN dòng mã thật đã gây báo động giả (rút gọn, không
# cần toàn bộ file kiem_newline_vung_ky.py) — một hàm CÓ dòng mã chứa chuỗi
# một-nháy mang nội dung ba-ký-tự-nháy, theo sau bởi MỘT docstring thật chứa
# câu ví dụ write_text(...) thiếu newline=. Dựng bằng chr()/nối chuỗi thay vì
# viết literal — viết trực tiếp `'\'\'\''`/`"\"\"\""` lồng trong một chuỗi
# triple-quote của CHÍNH file test này sẽ mắc đúng cái bẫy đang kiểm (ba ký
# tự nháy trần làm Python đóng nhầm chuỗi bao ngoài).
_SQ = "'"
_DQ = '"'
_TRIPLE_DQ = _DQ * 3
_TRIPLE_SQ = _SQ * 3

_NOI_DUNG_TAI_HIEN_BUG = "\n".join([
    "def _la_chuoi_ba_nhay(nguyen_van_token):",
    "    " + _TRIPLE_DQ + "Chuoi mot dong, khong phai nguon cua bug." + _TRIPLE_DQ,
    "    phan_con_lai = nguyen_van_token",
    "    return phan_con_lai.startswith(" + _SQ + _TRIPLE_DQ + _SQ + ") or "
    "phan_con_lai.startswith(" + _DQ + _TRIPLE_SQ + _DQ + ")",
    "",
    "",
    "def _mask_ngay_tho(dong):",
    "    " + _TRIPLE_DQ + "Ban CU - CHI dung khi tokenize khong doc duoc. KHONG dung",
    "    cho duong di binh thuong: no chinh la nguon cua bug da va - cat nham tai",
    "    '#' NAM TRONG mot string literal (vd",
    '    `.write_text("# Script phan tich\\\\n(placeholder)\\\\n", encoding="utf-8")`),',
    "    lam mat luon phan `encoding=`/`newline=` phia sau." + _TRIPLE_DQ,
    "    return dong",
    "",
])

# Một lời gọi write_text() THẬT (không phải ví dụ trong docstring), thiếu
# newline= — phải VẪN bị luật R6 bắt sau khi vá, để chứng minh bản vá không
# đơn thuần "im lặng hoá" toàn bộ luật R6.
_NOI_DUNG_VI_PHAM_THAT = '''\
def ghi_that(dst, noi_dung):
    dst.write_text(noi_dung, encoding="utf-8")
'''


def _dung_file_trong_vung_ky(tmp_path: Path, ten_file: str, noi_dung: str) -> Path:
    """Đặt `noi_dung` vào `<tmp_path>/medical-ebm-automation/tools/<ten_file>`
    — đường dẫn tương đối phải khớp một mục của `VUNG_KY` thì luật R6 mới
    được xét tới (xem `quet_file()`)."""
    thu_muc = tmp_path / "medical-ebm-automation" / "tools"
    thu_muc.mkdir(parents=True, exist_ok=True)
    p = thu_muc / ten_file
    p.write_text(noi_dung, encoding="utf-8")
    return p


class TestKhongBaoDongGiaTrenChuoiMotNhayBaKyTuNhay(unittest.TestCase):
    """Vá 12/09/2026 — chuỗi một-nháy `'\"\"\"'` không còn bị hiểu nhầm là mở
    docstring, nên docstring thật đứng SAU nó (chứa câu ví dụ write_text())
    không còn bị coi là mã thật."""

    def setUp(self) -> None:
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_path = Path(self._tmp.name)

    def test_mask_moi_che_dung_docstring_du_co_dong_ma_chua_ba_ky_tu_nhay(self):
        dong = _NOI_DUNG_TAI_HIEN_BUG.splitlines()
        code = ktd._mask_khong_phai_code(dong)
        # Số dòng phải giữ nguyên (chỉ số dòng báo cáo dựa trên điều này).
        self.assertEqual(len(code), len(dong))
        # Câu ví dụ write_text(...) nằm TRONG docstring phải đã bị che —
        # không còn xuất hiện nguyên văn trong bản đã mask.
        van_ban_da_mask = "\n".join(code)
        self.assertNotIn('encoding="utf-8"', van_ban_da_mask,
                          "docstring chứa câu ví dụ write_text() KHÔNG được để lọt "
                          "sau khi che — bản vá phải nhận đúng đây là docstring")
        # Dòng mã thật `return ....startswith('"""') ...` KHÔNG bị che mất
        # (nó là code thật, không phải docstring) — vẫn còn "startswith" trong
        # bản mask.
        self.assertIn("startswith", van_ban_da_mask)

    def test_quet_file_khong_con_bao_dong_gia_tai_vi_du_trong_docstring(self):
        p = _dung_file_trong_vung_ky(self.tmp_path, "mo_phong_kiem_newline.py",
                                      _NOI_DUNG_TAI_HIEN_BUG)
        ktd.REPO = self.tmp_path
        do, _vang = ktd.quet_file(p)
        r6 = [x for x in do if "R6" in x]
        self.assertEqual(r6, [], f"vẫn còn báo động giả R6: {r6}")

    def test_r6_van_bat_duoc_write_text_thieu_newline_that(self):
        """Đối chứng bắt buộc: bản vá không được đánh đổi bằng cách làm câm
        luôn luật R6 cho vi phạm THẬT."""
        p = _dung_file_trong_vung_ky(self.tmp_path, "co_loi_that.py",
                                      _NOI_DUNG_VI_PHAM_THAT)
        ktd.REPO = self.tmp_path
        do, _vang = ktd.quet_file(p)
        r6 = [x for x in do if "R6" in x]
        self.assertEqual(len(r6), 1, f"phải bắt đúng 1 vi phạm R6 thật, được: {r6}")

    def test_mien_tru_da_nen_bo_qua_van_hoat_dong_tren_vi_pham_that(self):
        """R6 vẫn tôn trọng miễn trừ tường minh `# da-nen: bo-qua` — bản vá
        không được phá vỡ cơ chế miễn trừ đã có."""
        noi_dung = (
            'def ghi_that(dst, noi_dung):\n'
            '    dst.write_text(noi_dung, encoding="utf-8")  # da-nen: bo-qua (test)\n'
        )
        p = _dung_file_trong_vung_ky(self.tmp_path, "mien_tru.py", noi_dung)
        ktd.REPO = self.tmp_path
        do, _vang = ktd.quet_file(p)
        r6 = [x for x in do if "R6" in x]
        self.assertEqual(r6, [], f"miễn trừ không được tôn trọng: {r6}")

    def test_ban_cu_ngay_tho_van_con_loi_lech_pha_da_biet(self):
        """Khoá lại NGUYÊN NHÂN: nếu ai đó lỡ gọi bản cũ
        (`_mask_khong_phai_code_ngay_tho`) trên CHÍNH fixture này, lỗi lệch
        pha PHẢI còn tái hiện được — nếu test này bắt đầu FAIL (tức bản cũ
        không còn lỗi), đó là dấu hiệu ai đó đã âm thầm sửa cả hai hàm giống
        nhau, cần soát lại tại sao còn giữ hai bản song song."""
        dong = _NOI_DUNG_TAI_HIEN_BUG.splitlines()
        code = ktd._mask_khong_phai_code_ngay_tho(dong)
        van_ban_da_mask = "\n".join(code)
        self.assertIn(
            'encoding="utf-8"', van_ban_da_mask,
            "bản cũ (_ngay_tho) được kỳ vọng VẪN mắc lỗi lệch pha trên fixture "
            "này — nếu nó đã hết mắc lỗi, tài liệu hoá trong docstring của "
            "_mask_khong_phai_code_ngay_tho đã lỗi thời, cần rà lại")


if __name__ == "__main__":
    unittest.main()
