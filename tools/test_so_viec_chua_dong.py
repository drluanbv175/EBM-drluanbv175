#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy cho `so_viec_chua_dong.py` — ngoại tuyến, không PII, không mạng.

Ba luật khi thêm ca thử (theo `chot_hoi_quy_bai_hoc.py`):
  (1) chỉ kiểm HÀNH VI bằng cách gọi vào mã đang sống, không đếm chuỗi trong file;
  (2) mỗi ca gắn với một rủi ro THẬT đã nêu trong docstring của công cụ;
  (3) nhanh và ngoại tuyến.

Chạy:  python3 tools/test_so_viec_chua_dong.py
"""
from __future__ import annotations

import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import so_viec_chua_dong as sv  # noqa: E402

HOM_NAY = "2026-08-22"


def chay(*argv: str, so: Path) -> tuple[int, str, str]:
    """Gọi CLI thật, trả (mã thoát, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        ma = sv.main(["--so", str(so), "--hom-nay", HOM_NAY, *argv])
    return ma, out.getvalue(), err.getvalue()


class Nen(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.so = Path(self.tmp.name) / "viec.jsonl"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def mo_viec(self, **kw) -> tuple[int, str, str]:
        args = ["--them", "--loai", kw.pop("loai", "xet-nghiem"),
                "--mo-ta", kw.pop("mo_ta", "HbA1c + creatinin, hẹn xem kết quả")]
        for k, v in kw.items():
            args += [f"--{k.replace('_', '-')}", str(v)]
        return chay(*args, so=self.so)


class ThemVaDoc(Nen):
    def test_them_roi_doc_lai(self):
        ma, out, _ = self.mo_viec(han_sau=14, ma="BN-K12")
        self.assertEqual(ma, 0)
        self.assertIn("V001", out)
        ds = sv.doc_so(self.so)
        self.assertEqual(len(ds), 1)
        self.assertEqual(ds[0]["trang_thai"], "mo")
        self.assertEqual(ds[0]["han"], "2026-09-05")
        self.assertEqual(ds[0]["ma_noi_bo"], "BN-K12")

    def test_ma_tang_dan_khong_trung(self):
        for _ in range(3):
            self.mo_viec(han_sau=7)
        self.assertEqual([r["id"] for r in sv.doc_so(self.so)], ["V001", "V002", "V003"])

    def test_loai_la_bi_chan(self):
        ma, _, err = chay("--them", "--loai", "xet-nghiem", "--mo-ta", "x",
                          "--han-sau", "7", so=self.so)
        self.assertEqual(ma, 0)
        # argparse chặn giá trị ngoài choices trước khi vào hàm
        with self.assertRaises(SystemExit):
            chay("--them", "--loai", "khong-co-that", "--mo-ta", "x",
                 "--han-sau", "7", so=self.so)


class ChanPII(Nen):
    """PII là ranh giới CỨNG — nguyên tắc bắt buộc số 4 của dự án."""

    def test_chan_so_dien_thoai(self):
        ma, _, err = self.mo_viec(mo_ta="gọi lại số 0912345678 khi có kết quả", han_sau=7)
        self.assertEqual(ma, 2)
        self.assertIn("số điện thoại", err)
        self.assertFalse(self.so.exists(), "KHÔNG được ghi gì khi đã chặn")

    def test_chan_day_so_dinh_danh(self):
        ma, _, err = self.mo_viec(mo_ta="đối chiếu 001203004567 trên thẻ", han_sau=7)
        self.assertEqual(ma, 2)
        self.assertIn("CMND/CCCD", err)

    def test_chan_email_va_ngay_sinh(self):
        self.assertEqual(self.mo_viec(mo_ta="gửi a.b@mail.com", han_sau=7)[0], 2)
        self.assertEqual(self.mo_viec(mo_ta="sinh 12/03/1958", han_sau=7)[0], 2)

    def test_chan_tu_khoa_dinh_danh(self):
        ma, _, err = self.mo_viec(mo_ta="ghi rõ họ tên vào phiếu", han_sau=7)
        self.assertEqual(ma, 2)
        self.assertIn("từ khoá định danh", err)

    def test_chan_ca_trong_ma_noi_bo_va_ket_qua(self):
        self.assertEqual(self.mo_viec(han_sau=7, ma="0987654321")[0], 2)
        self.mo_viec(han_sau=7)
        ma, _, _ = chay("--dong", "V001", "--ket-qua", "báo qua 0912345678", so=self.so)
        self.assertEqual(ma, 2)
        self.assertEqual(sv.doc_so(self.so)[0]["trang_thai"], "mo", "không được đổi khi chặn")

    def test_khong_chan_oan_mo_ta_lam_sang_binh_thuong(self):
        """BH08: biến CHƯA BIẾT thành CÓ VẤN ĐỀ sẽ dạy người ta bỏ qua cảnh báo."""
        sach = [
            "HbA1c 7,1% — hẹn xem lại sau 3 tháng",
            "eGFR 48 mL/phút/1,73m2, cần nhắc lại creatinin",
            "X-quang ngực thẳng, nghi thâm nhiễm thuỳ dưới phải",
            "Chuyển tuyến khám chuyên khoa Nội tiết, chờ phản hồi",
            "Thử tăng liều, đánh giá đáp ứng sau 4 tuần",
        ]
        for t in sach:
            self.assertEqual(sv.soi_pii(t), [], f"chặn oan: {t!r}")


class BatBuocCoHan(Nen):
    def test_thieu_han_bi_chan(self):
        ma, _, err = chay("--them", "--loai", "tai-kham", "--mo-ta", "hẹn 3 tháng",
                          so=self.so)
        self.assertEqual(ma, 2)
        self.assertIn("quá hạn", err)

    def test_khong_cho_vua_han_vua_han_sau(self):
        ma, _, _ = self.mo_viec(han="2026-09-01", han_sau=7)
        self.assertEqual(ma, 2)

    def test_han_sai_dinh_dang_bi_chan(self):
        ma, _, err = self.mo_viec(han="01/09/2026")
        self.assertEqual(ma, 2)
        self.assertIn("YYYY-MM-DD", err)


class PhatHienQuaHan(Nen):
    def test_qua_han_tra_ma_thoat_1(self):
        self.mo_viec(han="2026-08-01")          # quá hạn 21 ngày
        self.mo_viec(han="2026-12-01")          # còn hạn
        ma, out, _ = chay(so=self.so)
        self.assertEqual(ma, 1)
        self.assertIn("V001", out)
        self.assertNotIn("V002", out)

    def test_dung_han_hom_nay_chua_tinh_la_qua_han(self):
        self.mo_viec(han=HOM_NAY)
        self.assertEqual(chay(so=self.so)[0], 0)

    def test_muc_do_theo_so_ngay_tre(self):
        self.mo_viec(han="2026-08-19")   # trễ 3  → 🟡
        self.mo_viec(han="2026-08-08")   # trễ 14 → 🟠
        self.mo_viec(han="2026-07-01")   # trễ 52 → 🔴
        _, out, _ = chay(so=self.so)
        for dau in ("🟡", "🟠", "🔴"):
            self.assertIn(dau, out)

    def test_ban_ghi_thieu_han_bi_xep_vao_nhom_phai_xem(self):
        """Fail-closed: dữ liệu hỏng KHÔNG được rơi vào nhóm 'ổn'."""
        self.so.parent.mkdir(parents=True, exist_ok=True)
        self.so.write_text(json.dumps(
            {"id": "V001", "trang_thai": "mo", "mo_ta": "x", "loai": "khac",
             "ma_noi_bo": "", "han": None}, ensure_ascii=False) + "\n", encoding="utf-8")
        ma, out, _ = chay(so=self.so)
        self.assertEqual(ma, 1)
        self.assertIn("THIẾU HẠN", out)

    def test_im_khi_on_thi_im_that(self):
        self.mo_viec(han="2026-12-01")
        ma, out, _ = chay("--im-khi-on", so=self.so)
        self.assertEqual(ma, 0)
        self.assertEqual(out.strip(), "")

    def test_im_khi_on_van_noi_khi_qua_han(self):
        self.mo_viec(han="2026-08-01")
        ma, out, _ = chay("--im-khi-on", so=self.so)
        self.assertEqual(ma, 1)
        self.assertIn("QUÁ HẠN", out)


class DongVaHuy(Nen):
    def test_dong_doi_trang_thai(self):
        self.mo_viec(han_sau=7)
        ma, _, _ = chay("--dong", "V001", "--ket-qua", "HbA1c 7,1% — giữ phác đồ", so=self.so)
        self.assertEqual(ma, 0)
        r = sv.doc_so(self.so)[0]
        self.assertEqual(r["trang_thai"], "dong")
        self.assertEqual(r["ngay_dong"], HOM_NAY)

    def test_khong_dong_hai_lan(self):
        self.mo_viec(han_sau=7)
        chay("--dong", "V001", so=self.so)
        ma, _, err = chay("--dong", "V001", so=self.so)
        self.assertEqual(ma, 2)
        self.assertIn("không mở", err)

    def test_dong_id_khong_ton_tai(self):
        ma, _, err = chay("--dong", "V999", so=self.so)
        self.assertEqual(ma, 2)
        self.assertIn("Không tìm thấy", err)

    def test_huy_bat_buoc_co_ly_do(self):
        self.mo_viec(han_sau=7)
        ma, _, err = chay("--huy", "V001", so=self.so)
        self.assertEqual(ma, 2)
        self.assertIn("ly-do", err)
        self.assertEqual(sv.doc_so(self.so)[0]["trang_thai"], "mo")

    def test_huy_co_ly_do_thi_duoc(self):
        self.mo_viec(han_sau=7)
        ma, _, _ = chay("--huy", "V001", "--ly-do", "bệnh nhân chuyển tuyến trên", so=self.so)
        self.assertEqual(ma, 0)
        self.assertEqual(sv.doc_so(self.so)[0]["trang_thai"], "huy")

    def test_viec_da_dong_khong_con_bi_tinh_qua_han(self):
        self.mo_viec(han="2026-08-01")
        chay("--dong", "V001", so=self.so)
        self.assertEqual(chay(so=self.so)[0], 0)


class DuLieuHong(Nen):
    def test_dong_json_hong_bao_so_dong_khong_nuot_im_lang(self):
        self.so.parent.mkdir(parents=True, exist_ok=True)
        self.so.write_text('{"id":"V001"}\nKHONG-PHAI-JSON\n', encoding="utf-8")
        ma, _, err = chay(so=self.so)
        self.assertEqual(ma, 2)
        self.assertIn("dòng 2", err)


class NoiDungThongDiep(Nen):
    def test_so_trong_khong_tuyen_bo_khong_bo_sot(self):
        """BH32: một chỉ số gộp không được trình bày như kết luận về toàn bộ."""
        ma, out, _ = chay(so=self.so)
        self.assertEqual(ma, 0)
        self.assertIn("chưa ai ghi", out)

    def test_khong_qua_han_van_noi_ro_pham_vi(self):
        self.mo_viec(han_sau=30)
        _, out, _ = chay(so=self.so)
        self.assertIn("ĐÃ ghi vào sổ", out)

    def test_bang_tuan_neu_thuoc_do(self):
        self.mo_viec(han="2026-08-01")
        ma, out, _ = chay("--tuan", so=self.so)
        self.assertEqual(ma, 1)
        self.assertIn("BẢNG TUẦN", out)
        self.assertIn("phải = 0", out)


class KhongVuotThamQuyen(Nen):
    def test_khong_ghi_decision_hay_gradelevel(self):
        """BH10: không công cụ nào được ghi `decision`/`gradeLevel`."""
        self.mo_viec(han_sau=7)
        chay("--dong", "V001", "--ket-qua", "đã báo bệnh nhân", so=self.so)
        raw = self.so.read_text(encoding="utf-8")
        for cam in ("decision", "gradeLevel", "gradeBy", "normativeBasis"):
            self.assertNotIn(cam, raw, f"sổ không được mang trường {cam}")

    def test_khong_tu_dong_dong_viec_qua_han(self):
        self.mo_viec(han="2026-01-01")
        chay(so=self.so)
        chay("--tuan", so=self.so)
        self.assertEqual(sv.doc_so(self.so)[0]["trang_thai"], "mo",
                         "công cụ TUYỆT ĐỐI không được tự đóng việc")


if __name__ == "__main__":
    unittest.main(verbosity=2)
