#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chốt việc 3 (17/11/2026): CAFÉ-S lưu lượt đo THẬT kèm vân tay agent, và cảm biến hòm việc ⑦s đọc nó.

Lượt đo thật tốn ~3 USD ⇒ kết quả thô không được mất (chấm lại MIỄN PHÍ bằng --cached). Cảm biến chỉ ĐỌC: trượt ca critical
⇒ 👤 ưu tiên 1; còn ca critical chưa đo ⇒ 👤 2; agent đổi so với vân tay ⇒ 👤 2; chưa có lượt đo/thiếu vân tay ⇒ ⚪ chết,
không bao giờ là «agent ổn». Không gọi API, không tốn tiền. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent


def _nap(ten: str, duong: Path):
    if str(duong.parent) not in sys.path:
        sys.path.insert(0, str(duong.parent))
    spec = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    spec.loader.exec_module(m)
    return m


C = _nap("_cafes_cb", HERE / "eval" / "cafes_suite.py")
T = _nap("_tdx_cb", HERE / "tu_de_xuat_viec.py")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class _CoSo(unittest.TestCase):
    def setUp(self):
        self.goc = Path(tempfile.mkdtemp())
        self.ag = self.goc / ".claude" / "agents"
        self.ag.mkdir(parents=True)
        (self.ag / "sang-loc-co-do.md").write_text("bản A", encoding="utf-8")
        (self.ag / "ke-don-an-toan.md").write_text("bản K", encoding="utf-8")
        self.out = self.goc / "tools" / "eval" / "agent_outputs"
        self.out.mkdir(parents=True)
        T._GIAC_QUAN_CHET.clear()

    def tearDown(self):
        shutil.rmtree(self.goc, ignore_errors=True)

    def _ban_ghi(self, ten, luc, cong="PASS", ket_qua=None, van_tay=True):
        d = {"luc": luc, "bao_cao": {"CRITICAL_GATE": cong}, "ket_qua": ket_qua or []}
        if van_tay:
            d["van_tay_agent"] = {t: _sha((self.ag / f"{t}.md").read_bytes()) for t in ("sang-loc-co-do", "ke-don-an-toan")}
        (self.out / ten).mkdir()
        (self.out / ten / "_ket_qua.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")


class CamBienCafes(_CoSo):
    def test_chua_co_luot_do_la_giac_quan_chet(self):
        self.assertEqual(T.giac_quan_cafes_agent_an_toan(self.goc), [])
        self.assertTrue(any("CAFÉ-S" in x for x in T._GIAC_QUAN_CHET))

    def test_dat_va_agent_khong_doi_thi_im_lang(self):
        self._ban_ghi("cafes_api_a", "2026-11-17T14:36:59")
        self.assertEqual(T.giac_quan_cafes_agent_an_toan(self.goc), [])
        self.assertEqual(T._GIAC_QUAN_CHET, [])

    def test_truot_critical_uu_tien_1(self):
        self._ban_ghi("cafes_api_a", "2026-11-17T14:00:00", cong="FAIL",
                      ket_qua=[{"case_id": "RF-03-SAH", "critical": True, "pass": False}])
        v = T.giac_quan_cafes_agent_an_toan(self.goc)
        self.assertEqual((v[0][0], v[0][1]), (1, "👤"))
        self.assertIn("RF-03-SAH", v[0][2])

    def test_critical_chua_do_uu_tien_2(self):
        self._ban_ghi("cafes_api_a", "2026-11-17T14:00:00", cong="KHÔNG ĐỦ ĐO")
        v = T.giac_quan_cafes_agent_an_toan(self.goc)
        self.assertEqual((v[0][0], v[0][1]), (2, "👤"))
        self.assertIn("CHƯA ĐO ĐƯỢC", v[0][2])

    def test_agent_doi_so_voi_van_tay_uu_tien_2(self):
        """Chính sách KHÔNG cho tự chạy (18/11: ghim rõ — repo nay có sync/api-khi-can.json) ⇒ vẫn là việc bác sĩ quyết."""
        self._ban_ghi("cafes_api_a", "2026-11-17T14:00:00")
        (self.ag / "sang-loc-co-do.md").write_text("bản A đã sửa", encoding="utf-8")
        with mock.patch.object(T, "_chinh_sach_api_khi_can", return_value=None):
            v = T.giac_quan_cafes_agent_an_toan(self.goc)
        self.assertEqual(len(v), 1)
        self.assertEqual((v[0][0], v[0][1]), (2, "👤"))
        self.assertIn("sang-loc-co-do", v[0][2])
        self.assertNotIn("ke-don-an-toan", v[0][2])

    def test_agent_doi_va_chinh_sach_tu_chay_thi_may_tu_do(self):
        """18/11: bác sĩ cho TỰ CHẠY «CAFÉ-S khi agent an toàn đổi» ⇒ 🛎 trỏ cơ chế API khi cần, không đòi bác sĩ quyết."""
        self._ban_ghi("cafes_api_a", "2026-11-17T14:00:00")
        (self.ag / "sang-loc-co-do.md").write_text("bản A đã sửa", encoding="utf-8")
        cs = {"tu_chay": {"chu_de": True, "de_cuong": True, "cafes": True}, "cafes_cach_ngay_toi_thieu": 30,
              "chu_de_toi_da_moi_luot": 60, "nen_cach_gio_toi_thieu": 6}
        with mock.patch.object(T, "_chinh_sach_api_khi_can", return_value=cs):
            v = T.giac_quan_cafes_agent_an_toan(self.goc)
        self.assertEqual(len(v), 1)
        self.assertEqual((v[0][0], v[0][1]), (3, "🛎"))
        self.assertIn("TỰ ĐO LẠI", v[0][2])
        self.assertIn("api_khi_can.py", v[0][3])

    def test_mat_tep_agent_cung_bao(self):
        self._ban_ghi("cafes_api_a", "2026-11-17T14:00:00")
        (self.ag / "ke-don-an-toan.md").unlink()
        self.assertIn("mất tệp", T.giac_quan_cafes_agent_an_toan(self.goc)[0][2])

    def test_thieu_van_tay_la_giac_quan_chet(self):
        self._ban_ghi("cafes_api_a", "2026-11-17T14:00:00", van_tay=False)
        self.assertEqual(T.giac_quan_cafes_agent_an_toan(self.goc), [])
        self.assertTrue(any("vân tay" in x for x in T._GIAC_QUAN_CHET))

    def test_lay_luot_moi_nhat_theo_thoi_diem(self):
        self._ban_ghi("cafes_api_cu", "2026-11-01T10:00:00", cong="FAIL",
                      ket_qua=[{"case_id": "RF-01-ACS", "critical": True, "pass": False}])
        self._ban_ghi("cafes_api_moi", "2026-11-17T14:00:00", cong="PASS")
        self.assertEqual(T.giac_quan_cafes_agent_an_toan(self.goc), [], "lượt CŨ đã được lượt mới thay")

    def test_cam_bien_duoc_bang_tong_hop_goi(self):
        """BH41: giác quan không ai gọi thì không tồn tại — tìm LỜI GỌI (AST), không khớp chú thích."""
        cay = ast.parse((HERE / "tu_de_xuat_viec.py").read_text(encoding="utf-8"))
        goi = [n for n in ast.walk(cay) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "giac_quan_cafes_agent_an_toan"]
        self.assertTrue(goi)


class LuuLuotDo(_CoSo):
    def test_luu_dau_ra_tho_khong_do_duoc_va_van_tay(self):
        class _Gia:
            agents_dir = str(self.ag)
            usage = {"vao": 1, "ghi_cache": 2, "doc_cache": 3, "ra": 4}
            nhat_ky = [{"agent": "sang-loc-co-do", "prompt": "p1", "dau_ra": "ĐI CẤP CỨU", "usage": {}, "giay": 1.0},
                       {"agent": "ke-don-an-toan", "prompt": "p2", "khong_do": "cụt", "usage": {}, "giay": 2.0}]

            def chi_phi_usd(self):
                return 0.5
        ca = [{"case_id": "RF-X", "prompt": "p1", "agent": "sang-loc-co-do"},
              {"case_id": "DI-Y", "prompt": "p2", "agent": "ke-don-an-toan"}]
        thu_muc = self.goc / "luot"
        duong = C.luu_luot_do(str(thu_muc), _Gia(), ca, [], {"CRITICAL_GATE": "PASS"}, "2026-11-17T14:00:00", "high")
        self.assertEqual((thu_muc / "RF-X.txt").read_text(encoding="utf-8"), "ĐI CẤP CỨU")
        self.assertEqual((thu_muc / "DI-Y.KHONG_DO.txt").read_text(encoding="utf-8"), "cụt")
        d = json.loads(Path(duong).read_text(encoding="utf-8"))
        self.assertEqual(d["luc"], "2026-11-17T14:00:00")
        self.assertEqual(d["van_tay_agent"]["sang-loc-co-do"], _sha("bản A".encode("utf-8")))
        self.assertEqual(d["chi_phi_usd"], 0.5)

    def test_nhat_ky_tung_luot_khi_goi_that(self):
        cli = types.SimpleNamespace(beta=types.SimpleNamespace(messages=types.SimpleNamespace(
            create=lambda **kw: types.SimpleNamespace(stop_reason="end_turn", stop_details=None,
                                                      content=[types.SimpleNamespace(type="text", text="OK")],
                                                      usage=types.SimpleNamespace(input_tokens=5, output_tokens=7,
                                                                                  cache_creation_input_tokens=0,
                                                                                  cache_read_input_tokens=0)))))
        a = C.ClaudeAPIAgent(str(self.ag), client=cli)
        a.generate("hỏi", "sang-loc-co-do")
        self.assertEqual(a.nhat_ky[0]["dau_ra"], "OK")
        self.assertEqual(a.nhat_ky[0]["usage"]["ra"], 7)


class BanGhiThatHomNay(unittest.TestCase):
    def test_luot_do_dau_tien_co_van_tay_va_cong_critical_pass(self):
        p = HERE / "eval" / "agent_outputs" / "cafes_api_20261117" / "_ket_qua.json"
        if not p.exists():
            self.skipTest("⚪ không có bản ghi lượt đo 17/11 ở cây này")
        d = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(d["bao_cao"]["CRITICAL_GATE"], "PASS")
        self.assertEqual(d["bao_cao"]["critical_đạt"], 21)
        self.assertEqual(set(d["van_tay_agent"]), {"sang-loc-co-do", "ke-don-an-toan"})


if __name__ == "__main__":
    unittest.main()
