#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`kiem_chung_cu_vuot_qua.py` — vá 21/09/2026 (đánh giá hoàn thiện, việc #2b). Ngoại tuyến, không PII.

Ca thật: báo cáo 16/09 dài 476 byte, in 🟢 «đã dò 163 PMID, không thấy bài mới hơn» — nhưng NCBI trả JSON HỢP LỆ
mang bản LỖI (khoá 'error' / thiếu 'linksets') mà bản 14/09 chỉ vá cho trường hợp trả HTML/None. `tra_diem_kham` lấy đúng
tệp đó làm căn cứ và TẮT mọi cờ 🟠 «có bản tổng hợp mới hơn». Luật: không hỏi được ⇒ không xanh; mẫu ⇒ không xanh.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
spec = importlib.util.spec_from_file_location("kcv_test_0921", TOOLS / "kiem_chung_cu_vuot_qua.py")
kcv = importlib.util.module_from_spec(spec)
sys.modules["kcv_test_0921"] = kcv
spec.loader.exec_module(kcv)

ELINK_RONG = {"linksets": [{"linksetdbs": []}]}
ELINK_CO_ID = {"linksets": [{"linksetdbs": [{"links": ["99999999"]}]}]}
ESUM_CO = {"result": {"uids": ["99999999"], "99999999": {"pubdate": "2025 Jan", "title": "Tong quan moi",
                                                        "source": "J", "pubtype": ["Systematic Review"]}}}


def _goc_vd() -> Path | None:
    for goc in (REPO / "EBM-Dashboards", REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa"):
        if (goc / "tools" / "verify_dashboard.py").exists():
            return goc
    return None


class BanLoiHopLeKhongDuocDocThanhKhongCoGi(unittest.TestCase):
    def test_elink_json_co_khoa_error(self):
        with mock.patch.object(kcv, "_goi", lambda url, cho=25: {"error": "rate limit exceeded"}):
            self.assertIsNone(kcv.tong_quan_moi_hon("11111111", 2020, None))

    def test_elink_json_thieu_linksets(self):
        with mock.patch.object(kcv, "_goi", lambda url, cho=25: {"header": {"type": "elink"}}):
            self.assertIsNone(kcv.tong_quan_moi_hon("11111111", 2020, None),
                              "thiếu 'linksets' = bản lỗi/rỗng, KHÔNG phải «không có tổng quan»")

    def test_esummary_thieu_result_hoac_co_error(self):
        for ban_loi in ({"error": "x"}, {"header": {}}):
            def gia(url, cho=25, _b=ban_loi):
                return ELINK_CO_ID if "elink.fcgi" in url else _b
            with mock.patch.object(kcv, "_goi", gia):
                self.assertIsNone(kcv.tong_quan_moi_hon("11111111", 2020, None))

    def test_ban_hop_le_van_tra_du_lieu(self):
        def gia(url, cho=25):
            return ELINK_CO_ID if "elink.fcgi" in url else ESUM_CO
        with mock.patch.object(kcv, "_goi", gia):
            r = kcv.tong_quan_moi_hon("11111111", 2020, None)
        self.assertTrue(r and r[0]["pmid"] == "99999999", "đường dương tính THẬT không được bị vá hỏng")


class MainInThamSoVaKhongXanhChoMau(unittest.TestCase):
    def _chay(self, goi_gia, *them):
        goc = _goc_vd()
        if goc is None:
            self.skipTest("không có verify_dashboard.py — CHƯA KIỂM, không phải ĐẠT")
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "WebDashboard_EBM_VanDeCuThe_ThuNghiem_20260921.html"
            db.write_text(
                '<script>\nconst DATA = {\n  meta: { updated: "2026-09-21" },\n  items: [\n'
                '    { id: "ITEM-01", title: "A", decision: "apply", pmid: "11111111", dateVersion: "01/2020" },\n'
                '    { id: "ITEM-02", title: "B", decision: "apply", pmid: "22222222", dateVersion: "01/2021" },\n'
                '    { id: "ITEM-03", title: "C", decision: "apply", pmid: "33333333", dateVersion: "01/2022" }\n'
                '  ]\n};\n/* ▲▲▲  HẾT KHỐI DATA  ▲▲▲ */\n</script>\n', encoding="utf-8")
            man = Path(td) / "manifest.json"
            out = io.StringIO()
            argv = ["kiem_chung_cu_vuot_qua.py", "--json-ra", str(man), *them] if "--file" in them else \
                   ["kiem_chung_cu_vuot_qua.py", "--file", str(db), "--json-ra", str(man), *them]
            with mock.patch.object(kcv, "DASH", goc), mock.patch.object(kcv, "_goi", goi_gia), \
                 mock.patch.object(kcv.time, "sleep", lambda s: None), \
                 mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(out):
                rc = kcv.main()
            manifest = json.loads(man.read_text(encoding="utf-8")) if man.exists() else None
        return rc, out.getvalue(), manifest

    def test_ban_loi_http200_khong_in_xanh_va_manifest_ghi_khong_hoi_duoc(self):
        rc, van, man = self._chay(lambda url, cho=25: {"error": "API rate limit exceeded"})
        self.assertNotIn("🟢", van, "đúng lỗi 16/09: bản lỗi JSON đọc thành sạch")
        self.assertEqual(rc, 2)
        self.assertEqual(man["ket_luan"], "KHONG_HOI_DUOC")
        self.assertEqual(man["so_pmid_hong"], 3)

    def test_in_tham_so_dau_bao_cao(self):
        _rc, van, _m = self._chay(lambda url, cho=25: ELINK_RONG)
        self.assertIn("tham số:", van)
        self.assertIn("MỘT FILE", van)

    def test_lan_do_mau_gioi_han_khong_in_xanh(self):
        rc, van, man = self._chay(lambda url, cho=25: ELINK_RONG, "--gioi-han", "1")
        self.assertNotIn("🟢", van, "dò 1/3 PMID không được nói như đã dò toàn kho")
        self.assertIn("MẪU", van)
        self.assertEqual(man["ket_luan"], "MAU")
        self.assertFalse(man["pham_vi"]["toan_kho"])

    def test_do_du_khong_bai_moi_van_xanh_va_manifest_SACH(self):
        rc, van, man = self._chay(lambda url, cho=25: ELINK_RONG)
        self.assertIn("🟢", van)
        self.assertEqual(rc, 0)
        self.assertEqual(man["ket_luan"], "SACH")
        self.assertEqual(man["so_pmid_do"], 3)

    def test_co_bai_moi_manifest_liet_ke_pmid(self):
        def gia(url, cho=25):
            return ELINK_CO_ID if "elink.fcgi" in url else ESUM_CO
        rc, van, man = self._chay(gia)
        self.assertEqual(rc, 1)
        self.assertEqual(man["ket_luan"], "CO_BAI_MOI")
        self.assertEqual(man["pmid_co_bai_moi"], ["11111111", "22222222", "33333333"])


if __name__ == "__main__":
    unittest.main(verbosity=2)


# ── Vòng phản biện độc lập 21/09: manifest THIẾU/THU HẸP không được đọc thành hợp lệ ─────────────────────
def _man(**ghi_de):
    m = {"phien_ban": 2, "ket_luan": "SACH", "ma_thoat": 0,
         "pham_vi": {"decision": ["apply"], "file": None, "gioi_han": None, "tu_nam": None, "toan_kho": True},
         "so_pmid_tong": 3, "so_pmid_do": 3, "so_pmid_hong": 0, "pmid_da_do": ["1", "2", "3"], "pmid_co_bai_moi": []}
    m.update(ghi_de)
    return m


class DocBaoCaoChatChe(unittest.TestCase):
    def _doc(self, cac_man: dict):
        with tempfile.TemporaryDirectory() as td:
            g = Path(td)
            for ten, m in cac_man.items():
                (g / f"CHUNG-CU-VUOT-QUA_{ten}.json").write_text(json.dumps(m), encoding="utf-8")
                (g / f"CHUNG-CU-VUOT-QUA_{ten}.txt").write_text("▸ PMID 1 (2020)\n", encoding="utf-8")
            return kcv.doc_bao_cao_vuot_qua(g)

    def test_manifest_du_thi_hop_le_va_tra_tap_da_do(self):
        r = self._doc({"20260921": _man()})
        self.assertTrue(r["hop_le"])
        self.assertEqual(r["da_do"], {"1", "2", "3"})

    def test_co_bai_moi_voi_pmid_hong_khong_hop_le(self):
        r = self._doc({"20260921": _man(ket_luan="CO_BAI_MOI", so_pmid_hong=100, pmid_co_bai_moi=["1"])})
        self.assertFalse(r["hop_le"], "CO_BAI_MOI mà còn PMID không hỏi được = dò THIẾU, không được nhận là hợp lệ")

    def test_tu_nam_thu_hep_khong_hop_le(self):
        r = self._doc({"20260921": _man(pham_vi={"decision": ["apply"], "file": None, "gioi_han": None, "tu_nam": 2026, "toan_kho": True})})
        self.assertFalse(r["hop_le"])

    def test_manifest_khong_liet_ke_tap_da_do_khong_hop_le(self):
        m = _man()
        del m["pmid_da_do"]
        self.assertFalse(self._doc({"20260921": m})["hop_le"], "không biết PMID nào CHƯA dò ⇒ không được kết luận «không có cờ»")

    def test_do_mot_phan_so_pmid_khac_tong_khong_hop_le(self):
        self.assertFalse(self._doc({"20260921": _man(so_pmid_tong=10)})["hop_le"])

    def test_co_bai_moi_ma_danh_sach_rong_khong_hop_le(self):
        self.assertFalse(self._doc({"20260921": _man(ket_luan="CO_BAI_MOI", pmid_co_bai_moi=[])})["hop_le"])

    def test_chi_co_txt_khong_manifest_khong_hop_le(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "CHUNG-CU-VUOT-QUA_20260814.txt").write_text("▸ PMID 1 (2020)\n", encoding="utf-8")
            self.assertFalse(kcv.doc_bao_cao_vuot_qua(Path(td))["hop_le"], "tệp .txt có thể là lượt dò MẪU — không rõ phạm vi")

    def test_ban_moi_nhat_hong_khong_am_tham_lui_ve_ban_cu_hop_le(self):
        r = self._doc({"20260810": _man(ket_luan="CO_BAI_MOI", pmid_co_bai_moi=["2"]),
                       "20260921": _man(ket_luan="KHONG_HOI_DUOC", so_pmid_hong=3)})
        self.assertFalse(r["hop_le"], "bản mới nhất hỏng ⇒ không được nói hợp lệ nhờ bản cũ")
        self.assertIn("20260921", r["ly_do"])
        self.assertEqual(r["pmids"], {"2"}, "dương tính CŨ vẫn được giữ làm cờ (cu=True) — chỉ âm tính cũ là hết hạn")
        self.assertTrue(r["cu"])


class ManifestCuBiXoaVaMoiDuongThoatDeuGhi(unittest.TestCase):
    def test_manifest_cu_bi_xoa_dau_luot_neu_luot_nay_khong_co_cong_cu(self):
        with tempfile.TemporaryDirectory() as td:
            man = Path(td) / "m.json"
            man.write_text(json.dumps(_man()), encoding="utf-8")            # manifest HỢP LỆ của lượt trước
            out = io.StringIO()
            with mock.patch.object(kcv._bst_kcvq, "duong_cong_cu_pipeline", lambda *a, **k: None), \
                 mock.patch.object(sys, "argv", ["kcv", "--json-ra", str(man)]), contextlib.redirect_stdout(out):
                rc = kcv.main()
            self.assertEqual(rc, 2)
            moi = json.loads(man.read_text(encoding="utf-8"))
            self.assertEqual(moi["ket_luan"], "KHONG_CO_CONG_CU", "thiếu công cụ vẫn phải GHI manifest mới, không để manifest cũ sống")


class TxtMoiHonManifestLaLuotDoDang(unittest.TestCase):
    def test_txt_moi_nhat_khong_manifest_khong_lui_ve_manifest_cu_de_noi_hop_le(self):
        with tempfile.TemporaryDirectory() as td:
            g = Path(td)
            (g / "CHUNG-CU-VUOT-QUA_20251215.json").write_text(json.dumps(_man()), encoding="utf-8")
            (g / "CHUNG-CU-VUOT-QUA_20260921.txt").write_text("dở dang\n", encoding="utf-8")
            r = kcv.doc_bao_cao_vuot_qua(g)
        self.assertFalse(r["hop_le"], "lượt mới nhất chết giữa chừng — manifest cũ 9 tháng không được làm nó «hợp lệ»")
        self.assertIn("20260921", r["ly_do"])


# ── Vòng phản biện độc lập 22/09: cổng tất-cả-hoặc-không vứt dương tính THẬT của chính lượt mới ─────────
class DuongTinhKhongMatKhiManifestMoiKhongHopLe(unittest.TestCase):
    """review:cong-rut-bai #1 (MEDIUM). Một PMID hỏng thoáng qua (vd rate-limit) trong 163 lượt
    hỏi làm CẢ manifest bị đánh «không hợp lệ» — nhưng 2 PMID dương tính THẬT đã dò được trong
    CHÍNH lượt đó không được vứt theo. Bất đối xứng: hop_le chỉ cần cho ÂM TÍNH."""

    def test_khong_co_ban_cu_van_giu_duoc_duong_tinh_cua_ban_moi_khong_hop_le(self):
        with tempfile.TemporaryDirectory() as td:
            g = Path(td)
            (g / "CHUNG-CU-VUOT-QUA_20260921.json").write_text(json.dumps(_man(
                ket_luan="CO_BAI_MOI", so_pmid_tong=10, so_pmid_do=10, so_pmid_hong=1,
                pmid_da_do=[str(i) for i in range(1, 11)], pmid_co_bai_moi=["3", "4"],
            )), encoding="utf-8")
            r = kcv.doc_bao_cao_vuot_qua(g)
        self.assertFalse(r["hop_le"], "còn 1 PMID hỏng ⇒ vẫn KHÔNG được coi là đủ để kết luận âm tính")
        self.assertEqual(r["pmids"], {"3", "4"}, "dương tính của chính lượt này không được vứt theo")

    def test_co_ban_cu_sach_van_hop_nhat_duong_tinh_ban_moi_khong_hop_le(self):
        with tempfile.TemporaryDirectory() as td:
            g = Path(td)
            (g / "CHUNG-CU-VUOT-QUA_20260810.json").write_text(json.dumps(_man()), encoding="utf-8")  # SACH, hợp lệ
            (g / "CHUNG-CU-VUOT-QUA_20260921.json").write_text(json.dumps(_man(
                ket_luan="CO_BAI_MOI", so_pmid_tong=10, so_pmid_do=10, so_pmid_hong=1,
                pmid_da_do=[str(i) for i in range(1, 11)], pmid_co_bai_moi=["3", "4"],
            )), encoding="utf-8")
            r = kcv.doc_bao_cao_vuot_qua(g)
        self.assertTrue(r["cu"], "bản mới không hợp lệ ⇒ cu=True (dùng bản cũ cho hop_le/da_do)")
        self.assertEqual(r["pmids"], {"3", "4"}, "dương tính mới hơn của bản KHÔNG hợp lệ vẫn được hợp nhất, "
                                                 "không bị bản SACH cũ hơn 'xoá' mất")

    def test_pmid_ngoai_tap_da_do_cua_chinh_manifest_bi_loai(self):
        """Dương tính phải nằm trong tập PMID mà CHÍNH manifest đó tự khai đã dò — không suy đoán
        rộng hơn những gì manifest nói (chống bịa/khớp lỏng)."""
        with tempfile.TemporaryDirectory() as td:
            g = Path(td)
            (g / "CHUNG-CU-VUOT-QUA_20260921.json").write_text(json.dumps(_man(
                ket_luan="CO_BAI_MOI", so_pmid_tong=10, so_pmid_do=10, so_pmid_hong=1,
                pmid_da_do=["1", "2"], pmid_co_bai_moi=["3", "4"],  # "3","4" KHÔNG nằm trong pmid_da_do
            )), encoding="utf-8")
            r = kcv.doc_bao_cao_vuot_qua(g)
        self.assertEqual(r["pmids"], set(), "dương tính ngoài tập tự khai đã dò không được nhận")

    def test_ket_luan_khong_phai_co_bai_moi_khong_bi_hop_nhat(self):
        """Đối chứng: manifest không hợp lệ mà ket_luan KHÔNG PHẢI CO_BAI_MOI (vd MOT_PHAN, không có
        pmid_co_bai_moi thật) không được tự nhiên sinh ra dương tính."""
        with tempfile.TemporaryDirectory() as td:
            g = Path(td)
            (g / "CHUNG-CU-VUOT-QUA_20260921.json").write_text(json.dumps(_man(
                ket_luan="MOT_PHAN", so_pmid_tong=10, so_pmid_do=9, so_pmid_hong=1,
                pmid_da_do=[str(i) for i in range(1, 10)], pmid_co_bai_moi=[],
            )), encoding="utf-8")
            r = kcv.doc_bao_cao_vuot_qua(g)
        self.assertFalse(r["hop_le"])
        self.assertEqual(r["pmids"], set())
