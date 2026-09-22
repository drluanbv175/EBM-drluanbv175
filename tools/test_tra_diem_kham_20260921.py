#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`tra_diem_kham.py` — vá 21/09/2026 (đánh giá hoàn thiện, việc #1). Ngoại tuyến, không PII.

Ca thật đo sống trên 1.100 thẻ: 6/6 câu thường gặp trả thẻ SAI CHỦ ĐỀ («tăng huyết áp mới chẩn đoán» → thẻ cơn tăng đường
huyết/H. pylori; «hen bậc 3» → thẻ chẹn beta; «gút cấp» → thẻ phù mạch). Đó là lỗi nguy hiểm hơn «chưa giám sát» vì người khám
tin thẻ đã qua duyệt. Phần A dùng thẻ giả (chạy ở mọi máy); phần B chạy bộ vàng trên sổ thẻ THẬT và tự bỏ qua khi máy không có sổ.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
spec = importlib.util.spec_from_file_location("tdk_test_0921", TOOLS / "tra_diem_kham.py")
tdk = importlib.util.module_from_spec(spec)
sys.modules["tdk_test_0921"] = tdk
spec.loader.exec_module(tdk)

BO_VANG = REPO / "quality" / "eval" / "tra-diem-kham" / "bo-vang.json"


def the(i: int, topic: str, rec: str = "", decision: str = "apply", pmid: str = "", ngay: str = "2026-01-01") -> dict:
    return {"id": f"T{i}", "topic": topic, "pico_question": "", "recommendation": rec or topic, "decision": decision,
            "provenance": "from_doctor_master", "verification_status": "đã xác minh", "date_added": ngay,
            "source": {"pmid": pmid or str(1000 + i)}, "gradeLevel": "na"}


KHO = [
    the(1, "Tiêu chuẩn phân loại đau đầu ICHD-3"),
    the(2, "Dự phòng migraine nhóm cổ điển (AAN)"),
    the(3, "ESC 2024: mô hình xác suất và chụp cắt lớp vi tính ban đầu ở bệnh nhân đau ngực ổn định", "chụp CT ban đầu cho người đau ngực"),
    the(4, "Đích huyết áp tâm thu dưới 130 mmHg ở người tăng huyết áp"),
    the(5, "Tăng sinh tuỷ xương và cơn tăng đường huyết ở người dùng corticoid"),
    the(6, "H. pylori: diệt trừ ở người viêm dạ dày mạn tăng nguy cơ ung thư"),
    the(7, "GINA 2026 — Mọi bệnh nhân hen dùng phác đồ có ICS"),
    the(8, "Chẹn beta chọn lọc an toàn ở COPD (Cochrane)"),
    the(9, "Oxy dài hạn không có lợi ở người chỉ giảm bão hòa mức trung bình", "COPD"),
    the(10, "Sàng lọc lao tiềm ẩn trước thuốc sinh học"),
    the(11, "Đái tháo đường quanh phẫu thuật: hiệu chỉnh thuốc theo giai đoạn tiền lâm sàng"),
    the(12, "Đợt khen thưởng tái khám ở người bệnh gút mạn"),
    the(13, "Lịch hẹn tái khám sau xuất viện"),
]


def tra(q: str, kho=None):
    return tdk.tra_chi_tiet(q, kho if kho is not None else KHO)


def ids(ket):
    return {c["id"] for c in ket}


class GapDauVaTuNguyen(unittest.TestCase):
    def test_gap_d_thanh_d(self):
        self.assertEqual(tdk._bo_dau("Đau đầu điều trị"), "dau dau dieu tri")

    def test_dau_dau_khong_tra_the_dau_nguc_vi_ban_dau(self):
        ket, _ = tra("đau đầu cờ đỏ cần chụp gì")
        self.assertNotIn("T3", ids(ket), "«đau»+«ban đầu» ở thẻ đau NGỰC không được trả lời câu hỏi đau ĐẦU")

    def test_dau_dau_van_ra_the_dung(self):
        ket, _ = tra("đau đầu")
        self.assertIn("T1", ids(ket))

    def test_khop_tu_nguyen_khong_khop_chuoi_con(self):
        ket, _ = tra("hen")
        self.assertNotIn("T12", ids(ket), "«hen» không được khớp chuỗi con của «khen»")
        self.assertIn("T7", ids(ket))

    def test_go_khong_dau_van_khop_bien_the_co_dau_nhung_dang_dung_xep_truoc(self):
        # «hen» gõ không dấu khớp cả «hen» lẫn «hẹn» (cố ý, cho người gõ nhanh) — thẻ mang ĐÚNG «hen» phải đứng trước.
        ket, _ = tra("hen")
        thu_tu = [c["id"] for c in ket]
        self.assertIn("T13", thu_tu)
        self.assertLess(thu_tu.index("T7"), thu_tu.index("T13"))

    def test_tang_khong_khop_tang_sinh(self):
        ket, _ = tra("tăng huyết áp mới chẩn đoán chọn thuốc gì")
        self.assertEqual(ids(ket), {"T4"}, "thẻ tăng SINH tuỷ / tăng đường huyết không được lọt")


class TokenNganCoDau(unittest.TestCase):
    def test_gut_co_dau_khong_khop_gut_khong_dau_khac_nghia(self):
        kho = [the(1, "Gut microbiome và bệnh viêm ruột"), the(2, "Thuốc hạ urat ở người bệnh gút mạn")]
        ket, _ = tra("gút", kho)
        self.assertEqual(ids(ket), {"T2"})

    def test_nguoi_go_khong_dau_van_ra_the_co_dau(self):
        ket, _ = tra("gut man", [the(1, "Thuốc hạ urat ở người bệnh gút mạn")])
        self.assertEqual(ids(ket), {"T1"}, "gõ không dấu là cách dùng bình thường ở phòng khám")


class TuGhepKeNhau(unittest.TestCase):
    def test_tien_dai_thao_duong_khong_ra_the_dai_thao_duong_tien_lam_sang(self):
        ket, _ = tra("tiền đái tháo đường")
        self.assertNotIn("T11", ids(ket), "thẻ «đái tháo đường… tiền lâm sàng» chứa đủ chữ nhưng KHÔNG phải tiền đái tháo đường")

    def test_khong_dau_cung_khong_lot(self):
        ket, _ = tra("tien dai thao duong")
        self.assertNotIn("T11", ids(ket))

    def test_cum_co_tu_dem_van_giu_cap(self):
        kho = [the(1, "Metformin trong bệnh thận mạn: chỉnh liều theo eGFR")]
        ket, _ = tra("metformin và bệnh thận mạn", kho)
        self.assertEqual(ids(ket), {"T1"}, "«và» bị lọc không được làm gãy cặp kề nhau")

    def test_the_khong_co_chu_copd_o_tieu_de_van_duoc_xet(self):
        ket, _ = tra("oxy dài hạn COPD")
        self.assertIn("T9", ids(ket))


class NgoaiPhamViVaChuaGiamSat(unittest.TestCase):
    def test_tu_dac_hieu_vang_toan_kho_la_khong_co(self):
        ket, loai = tra("sốt xuất huyết dengue")
        self.assertEqual((ket, loai), ([], "khong_co"))

    def test_cau_rong_va_vo_nghia(self):
        for q in ("", "   ", "zzzz qqqq"):
            ket, _ = tra(q)
            self.assertEqual(ket, [], q)

    def test_the_lac_de_khop_mot_tu_chung_bi_tu_choi_va_bao_khop_yeu(self):
        ket, loai = tra("hen phế quản bậc 3 điều trị")
        self.assertEqual(ket, [])
        self.assertIn(loai, ("khop_yeu", "khong_co"))


class GomTheTrungKhongTuChonBanMoi(unittest.TestCase):
    def test_cung_khuyen_cao_cung_quyet_dinh_gop_mot_the(self):
        a = the(1, "Bộ ba ICS/LABA/LAMA giảm đợt cấp COPD", "rec X", "apply", "111", "2026-01-01")
        b = the(2, "Bộ ba ICS/LABA/LAMA giảm đợt cấp COPD", "rec X", "apply", "111", "2026-03-01")
        ket, _ = tra("bộ ba ICS LABA LAMA COPD", [a, b])
        self.assertEqual(len(ket), 1)
        self.assertFalse(ket[0]["_xung_dot"])

    def test_cung_khuyen_cao_khac_quyet_dinh_bao_xung_dot_va_khong_chon_ban_moi_hon(self):
        cu = the(1, "Bộ ba ICS/LABA/LAMA giảm đợt cấp COPD", "rec X", "apply", "111", "2026-01-01")
        moi = the(2, "Bộ ba ICS/LABA/LAMA giảm đợt cấp COPD", "rec X", "consider", "111", "2026-03-01")
        ket, _ = tra("bộ ba ICS LABA LAMA COPD", [cu, moi])
        self.assertEqual(len(ket), 1)
        self.assertTrue(ket[0]["_xung_dot"], "hai bản nói ngược nhau ⇒ phải nói ra, không chọn âm thầm bản ngày mới")

    def test_khuyen_cao_khac_nhau_khong_bi_gop(self):
        a = the(1, "Bộ ba ICS/LABA/LAMA giảm đợt cấp COPD", "rec X", "apply", "111")
        b = the(2, "Bộ ba ICS/LABA/LAMA giảm đợt cấp COPD", "rec Y KHÁC HẲN", "apply", "222")
        ket, _ = tra("bộ ba ICS LABA LAMA COPD", [a, b])
        self.assertEqual(len(ket), 2, "hai khuyến cáo khác nhau của cùng chủ đề (vd IMPACT: hai kết cục) không được gộp")


class CoLapStateVaLoaiMiss(unittest.TestCase):
    def test_ghi_nhat_ky_di_vao_STATE_da_tro_lai_khong_dung_state_that(self):
        thuc = tdk.STATE
        with tempfile.TemporaryDirectory() as td:
            tdk.STATE = Path(td)
            try:
                tdk._ghi_nhat_ky_tac_dong([], 0.01, "khop_yeu")
                tdk._ghi_nhat_ky_tac_dong([{"id": "T1"}], 0.01, "khong_co")
                dong = [json.loads(x) for x in (Path(td) / "nhat-ky-tac-dong.jsonl").read_text(encoding="utf-8").splitlines()]
            finally:
                tdk.STATE = thuc
        self.assertEqual([r["loai"] for r in dong], ["khop_yeu", "khop"])
        self.assertEqual([r["miss"] for r in dong], [True, False])
        self.assertNotIn("cau_hoi", dong[0], "nhật ký tác động KHÔNG được lưu câu hỏi thô (PII)")

    def test_in_quick_view_khong_cham_state_that(self):
        thuc = tdk.STATE
        ban_dau = {p: p.stat().st_mtime_ns for p in (REPO / "state").glob("*.jsonl")} if (REPO / "state").exists() else {}
        with tempfile.TemporaryDirectory() as td:
            tdk.STATE = Path(td)
            try:
                import contextlib
                import io
                with contextlib.redirect_stdout(io.StringIO()):
                    tdk.in_quick_view("câu thử không có thẻ", [], set(), 0.0, "khop_yeu", None)
                self.assertTrue((Path(td) / "cau-hoi-chua-giam-sat.jsonl").exists())
                ghi = json.loads((Path(td) / "cau-hoi-chua-giam-sat.jsonl").read_text(encoding="utf-8").splitlines()[0])
                self.assertEqual(ghi["loai"], "khop_yeu")
            finally:
                tdk.STATE = thuc
        sau = {p: p.stat().st_mtime_ns for p in (REPO / "state").glob("*.jsonl")} if (REPO / "state").exists() else {}
        self.assertEqual(ban_dau, sau, "test không được ghi vào state/ THẬT")

    def test_nguoi_tieu_thu_khong_dem_khop_yeu_la_khoang_trong_giam_sat(self):
        nguon = (TOOLS / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
        self.assertIn('r.get("miss") and r.get("loai") != "khop_yeu"', nguon)
        nguon2 = (TOOLS / "do_tac_dong.py").read_text(encoding="utf-8")
        self.assertIn('r.get("loai") == "khop_yeu"', nguon2)


# ── PHẦN B — bộ vàng trên sổ thẻ THẬT ─────────────────────────────────────────────────────────────────────
def _the_that():
    if not tdk.LEDGER.exists():
        return None
    d = json.loads(tdk.LEDGER.read_text(encoding="utf-8"))
    return [c for c in d["evidence_cards"] if c.get("provenance") in tdk.NGUON_DUYET
            and str(c.get("verification_status", "")).startswith("đã xác minh")]


def _van_ban_the(c: dict) -> str:
    """Chỉ TIÊU ĐỀ (topic + pico_question): từ khoá phải có ở tiêu đề thẻ, không chỉ đâu đó trong khuyến cáo — phản biện 21/09
    chỉ ra phép kiểm chuỗi-con-toàn-văn cho mọi câu «đúng» kể cả khi thẻ lạc đề."""
    return " ".join(tdk._tach(f"{c.get('topic', '')} {c.get('pico_question', '')}"))


class BoVangTrenSoThat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = _the_that()
        cls.vang = json.loads(BO_VANG.read_text(encoding="utf-8"))

    def _can_so(self):
        if self.cards is None:
            self.skipTest("máy không có EBM_MASTER/EBM_MASTER.json (ngoài git) — CHƯA KIỂM bộ vàng, không phải ĐẠT")

    def test_bo_vang_hop_le_va_du_lop(self):
        cau = self.vang["cau_hoi"]
        self.assertGreaterEqual(len(cau), 40)
        loai = {c["ky_vong"] for c in cau}
        self.assertEqual(loai, {"trung", "chua_giam_sat", "khong_tra_the_lac_de"})
        for c in cau:
            if c["ky_vong"] == "trung":
                self.assertTrue(c["the_phai_chua_mot_trong"], c["q"])
            if c["ky_vong"] == "khong_tra_the_lac_de":
                self.assertTrue(c["cam_tra_the_chua"], c["q"])
        self.assertEqual(len({c["q"] for c in cau}), len(cau), "câu trùng")
        trung_da_biet = {c["q"] for c in cau} & {c["q"] for c in self.vang["da_biet_chua_dat"] if
                                                 any(x["q"] == c["q"] and x["ky_vong"] == "trung" for x in cau)}
        self.assertEqual(trung_da_biet, set(), "một câu không thể vừa được khẳng định vừa là khoảng trống đã biết")

    def test_moi_cau_trong_bo_vang(self):
        self._can_so()
        loi = []
        for c in self.vang["cau_hoi"]:
            ket, _ = tdk.tra_chi_tiet(c["q"], self.cards)
            k = c["ky_vong"]
            if k == "chua_giam_sat" and ket:
                loi.append(f"«{c['q']}» phải CHƯA GIÁM SÁT nhưng ra {[x['topic'][:50] for x in ket]}")
            elif k == "trung":
                if not ket:
                    loi.append(f"«{c['q']}» phải ra thẻ nhưng ra rỗng")
                for x in ket:
                    vb = " " + _van_ban_the(x) + " "
                    if not any(f" {kw} " in vb for kw in c["the_phai_chua_mot_trong"]):
                        loi.append(f"«{c['q']}» ra thẻ LẠC ĐỀ: {x['topic'][:70]}")
            elif k == "khong_tra_the_lac_de":
                for x in ket:
                    vb = " " + " ".join(tdk._tach(str(x.get("topic", "")))) + " "
                    for cam in c["cam_tra_the_chua"]:
                        if f" {cam} " in vb:
                            loi.append(f"«{c['q']}» ra thẻ CẤM «{cam}»: {x['topic'][:70]}")
        self.assertEqual(loi, [], "\n" + "\n".join(loi))

    def test_do_chinh_xac_tong_the_khong_tut_duoi_100_phan_tram_tren_bo_vang(self):
        """Đo và IN ra để theo dõi: tỉ lệ câu 'trung' ra đúng chủ đề & tỉ lệ 'chưa giám sát' đúng."""
        self._can_so()
        dung = tong = 0
        for c in self.vang["cau_hoi"]:
            ket, _ = tdk.tra_chi_tiet(c["q"], self.cards)
            tong += 1
            if c["ky_vong"] == "chua_giam_sat":
                dung += 0 if ket else 1
            elif c["ky_vong"] == "trung":
                ok = bool(ket) and all(any(f" {kw} " in " " + _van_ban_the(x) + " " for kw in c["the_phai_chua_mot_trong"]) for x in ket)
                dung += ok
            else:
                dung += all(all(f" {cam} " not in " " + " ".join(tdk._tach(str(x.get('topic', '')))) + " " for cam in c["cam_tra_the_chua"]) for x in ket)
        print(f"\n[bộ vàng tra_diem_kham] {dung}/{tong} đúng ({dung * 100 // tong}%) trên {len(self.cards)} thẻ đã duyệt")
        self.assertEqual(dung, tong)

    def test_khoang_trong_da_biet_khong_gay_nguy_hiem_khong_dam_khang_dinh_nhung_phai_khong_crash(self):
        self._can_so()
        for c in self.vang["da_biet_chua_dat"]:
            ket, loai = tdk.tra_chi_tiet(c["q"], self.cards)
            self.assertIn(loai, ("khop", "khong_co", "khop_yeu"))
            self.assertLessEqual(len(ket), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
