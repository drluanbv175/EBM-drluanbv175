"""Chỗ sót do phản biện nêu khi ghép bốn nhóm sửa làn Chrome/EndNote — 15/10/2026.

VÌ SAO (mỗi ca một chỗ người phản biện độc lập chỉ ra sau khi các nhóm sửa xong):
- `nap_endnote_chu_de.doc_cau_hinh` nhận `{"thu_vien": 123}` (truthy, không phải chuỗi) trong khi `ly_do_cau_hinh_hong` coi là
  hỏng ⇒ main gọi Path(123) và ném TypeError không ai bắt.
- `tom_tat_endnote_vi.trang_thai_toan_van` nay đi qua nguồn sự thật `doc_toan_van_co_nguoi.bao_phu_cuc_bo`; nạp/đo lỗi thì cả
  khối ĐỌC NHANH sập (trước chỉ là một glob) — phải nói «chưa xét», không sập.
- `tra_cuu_co_tai_khoan.tao_xac_minh_engine` chỉ nhìn bố cục LỒNG ⇒ phiên Cloud có engine clone cạnh repo bị báo «engine vắng».
- Skill `tong-thuat-chung-cu` xếp `doc_toan_van_pmc.py` vào làn «ghi nhận đã đọc» dù công cụ đó chỉ IN đoạn, không ghi vào kho;
  bản PMC (CC hoặc bản thảo tác giả «TDM», quyết định 15/10/2026) phải đi `gom_toan_van_dashboard.py` để cổng thấy.
- `references/13-source-universe.md` liệt «publisher full text» là nguồn toàn văn hợp pháp mà không kèm điều khoản AI/TDM (G3-D7).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _nap(ten: str, tep: str):
    spec = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


NAP = _nap("nap_ghep_20261015", "nap_endnote_chu_de.py")
TTV = _nap("ttv_ghep_20261015", "tom_tat_endnote_vi.py")
TCTK = _nap("tctk_ghep_20261015", "tra_cuu_co_tai_khoan.py")


def test_cau_hinh_thu_vien_khong_phai_chuoi_la_hong_o_ca_hai_ham(tmp_path):
    tep = tmp_path / "ebm-endnote.json"
    tep.write_text(json.dumps({"thu_vien": 123}), encoding="utf-8")
    assert NAP.doc_cau_hinh(tep) is None, "doc_cau_hinh nhận «thu_vien» không phải chuỗi ⇒ main sẽ ném TypeError"
    assert NAP.ly_do_cau_hinh_hong(tep), "ly_do_cau_hinh_hong phải nói tệp hỏng"
    tep.write_text(json.dumps({"thu_vien": "/x/Thu vien.enl"}), encoding="utf-8")
    assert NAP.doc_cau_hinh(tep)["thu_vien"] == "/x/Thu vien.enl"


def test_trang_thai_toan_van_noi_chua_xet_khi_nguon_su_that_loi(tmp_path, monkeypatch):
    def _hong():
        raise ImportError("giả lập không nạp được doc_toan_van_co_nguoi")
    monkeypatch.setattr(TTV, "_dtv", _hong)
    kq = TTV.trang_thai_toan_van("12345", tmp_path)
    assert kq.startswith("chưa xét") and "ImportError" in kq, kq


def test_goc_engine_nhan_bo_cuc_anh_em(tmp_path, monkeypatch):
    goc = tmp_path / "EBM-drluanbv175"
    goc.mkdir()
    fv = tmp_path / "medical-ebm-automation" / "app" / "services" / "fallback_verification.py"
    fv.parent.mkdir(parents=True)
    fv.write_text("", encoding="utf-8")
    monkeypatch.setattr(TCTK, "REPO", goc)
    assert TCTK._goc_engine() == tmp_path / "medical-ebm-automation"
    # Bố cục LỒNG vẫn được ưu tiên khi có cả hai.
    fv2 = goc / "medical-ebm-automation" / "app" / "services" / "fallback_verification.py"
    fv2.parent.mkdir(parents=True)
    fv2.write_text("", encoding="utf-8")
    assert TCTK._goc_engine() == goc / "medical-ebm-automation"


def test_tong_thuat_ban_pmc_di_gom_khong_coi_doc_pmc_la_ghi_nhan():
    sk = (REPO / "sync" / "skills" / "tong-thuat-chung-cu" / "SKILL.md").read_text(encoding="utf-8")
    assert "bản thảo tác giả «TDM»" in sk and "gom_toan_van_dashboard.py" in sk
    assert "chỉ IN đoạn để đọc, không ghi nhận" in sk, "skill vẫn coi doc_toan_van_pmc.py là làn ghi nhận đã đọc"


def test_nguon_toan_van_nxb_kem_dieu_khoan_ai_tdm():
    ref = (REPO / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "references" / "13-source-universe.md").read_text(
        encoding="utf-8")
    dong = next(d for d in ref.splitlines() if d.startswith("7. **Full text"))
    assert "publisher full text (CHỈ khi điều khoản AI/TDM" in dong and "DIEU_KHOAN_NXB" in dong, dong
