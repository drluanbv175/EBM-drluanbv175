# -*- coding: utf-8 -*-
"""BH108 kiểm agent TRƯỚC bước dò engine, và đòi dòng miễn trừ NLM ở mục 8 (01/10/2026).

Lỗi đo được: bước dò engine (`tra_thuoc_quoc_te.py` có tồn tại không) đứng trước khối kiểm `ke-don-an-toan.md`,
nên ở mọi nơi vắng engine — CI, phiên Cloud một-repo, worktree gốc trần — chốt trả ⚪ ngay tại đó và khối kiểm
agent không bao giờ chạy: agent mất hẳn «`gan_dung`» mà chốt vẫn chỉ ra ⚪ «ngoài phạm vi».

Cùng đợt: `_CONNECTOR-CHUNG-CU.md` §1ter luật 5 dạy in một lần, nguyên văn dòng `mien_tru_nlm` của NLM khi trình
kết quả `chuan-hoa`; agent duy nhất gọi công cụ phải nhắc luật đó NGAY trên dòng gọi lệnh chuẩn hoá (không khớp
cả tệp — luật §0.8 của CLAUDE.md).

Kiểm trên bản sao tạm của ba tệp agent/doctrine, không đụng repo thật; engine vắng là trạng thái tự nhiên của
thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

_TEP = Path(__file__).resolve().parent / "chot_hoi_quy_bai_hoc.py"
_TEN = "chot_bh108_20261001"
_sp = importlib.util.spec_from_file_location(_TEN, _TEP)
C = importlib.util.module_from_spec(_sp)
sys.modules[_TEN] = C
_sp.loader.exec_module(C)

_AGENTS = C.REPO / ".claude" / "agents"
_BA_TEP = ("_CONNECTOR-CHUNG-CU.md", "ke-don-an-toan.md", "khoang-trong-nghien-cuu.md")
_LENH = "tra_thuoc_quoc_te.py chuan-hoa"
_VANG = SimpleNamespace(duong_goc=lambda g, r: None, GOC_DU_LIEU_NGOAI_GIT=("medical-ebm-automation",))
_CO = SimpleNamespace(duong_goc=lambda g, r: r / g, GOC_DU_LIEU_NGOAI_GIT=("medical-ebm-automation",))


def _dung(tmp_path: Path, monkeypatch, sua_agent=None) -> Path:
    """Repo tạm chỉ có ba tệp agent/doctrine + `tools/ban_sao_tran.py` (phép dò engine THẬT của `_goc_mea`);
    engine VẮNG cả lồng lẫn anh em. `sua_agent` đột biến ke-don-an-toan.md."""
    repo = tmp_path / "goc"
    (repo / ".claude" / "agents").mkdir(parents=True)
    (repo / "tools").mkdir()
    shutil.copy2(_TEP.parent / "ban_sao_tran.py", repo / "tools" / "ban_sao_tran.py")
    for ten in _BA_TEP:
        shutil.copy2(_AGENTS / ten, repo / ".claude" / "agents" / ten)
    if sua_agent is not None:
        p = repo / ".claude" / "agents" / "ke-don-an-toan.md"
        cu = p.read_text(encoding="utf-8")
        moi = sua_agent(cu)
        assert moi != cu, "đột biến không đổi gì — phép thử sai"
        p.write_text(moi, encoding="utf-8", newline="\n")
    monkeypatch.setattr(C, "REPO", repo)
    return repo


def _chay(ban_sao_tran) -> tuple[bool, str, str]:
    ok, ct = C.bh108_medical_mcp_chon_loc_va_cong_cu_thuoc_co_agent_goi()
    return ok, ct, C.phan_loai("BH108", ok, True, ct, ban_sao_tran)


def _bo_mien_tru_o_muc_8(t: str) -> str:
    return "\n".join(d.replace("`mien_tru_nlm`", "mien-tru-nlm") if _LENH in d else d for d in t.split("\n"))


def test_ban_that_vang_engine_chi_ra_trang_khong_do_gia(tmp_path, monkeypatch):
    """Đối chứng: ba tệp thật qua trọn khối kiểm agent; vắng engine ⇒ ⚪ có khai báo, không ✗ giả trên CI."""
    _dung(tmp_path, monkeypatch)
    ok, ct, loai = _chay(_VANG)
    assert ok is False
    assert "tra_thuoc_quoc_te.py biến mất" in ct, ct
    assert loai == "ngoai_pham_vi"


def test_vang_engine_mat_mien_tru_o_muc_8_thi_do(tmp_path, monkeypatch):
    _dung(tmp_path, monkeypatch, _bo_mien_tru_o_muc_8)
    ok, ct, loai = _chay(_VANG)
    assert ok is False
    assert "`mien_tru_nlm`" in ct and "§1ter luật 5" in ct, ct
    assert loai == "tai_phat", "lỗi trong-repo bị ⚪ hoá khi vắng engine"


def test_doi_mien_tru_sang_dong_khac_van_do(tmp_path, monkeypatch):
    """Cả tệp vẫn có chuỗi, nhưng không ở dòng gọi lệnh chuẩn hoá ⇒ đỏ (không khớp cả tệp)."""
    _dung(tmp_path, monkeypatch,
          lambda t: _bo_mien_tru_o_muc_8(t).rstrip("\n") + "\n\nGhi chú lạc chỗ: dòng `mien_tru_nlm`.\n")
    ok, ct, loai = _chay(_VANG)
    assert ok is False
    assert "mục 8" in ct, ct
    assert loai == "tai_phat"


def test_vang_engine_mat_gan_dung_thi_do_khong_con_trang(tmp_path, monkeypatch):
    """Đúng ca đo được 01/10/2026: trước vá, bước dò engine đứng trước nên ca này ra ⚪."""
    _dung(tmp_path, monkeypatch, lambda t: t.replace("`gan_dung`", "gan-dung"))
    ok, ct, loai = _chay(_VANG)
    assert ok is False
    assert "luật đọc gan_dung" in ct, ct
    assert loai == "tai_phat"


def test_engine_co_mat_ma_mat_cong_cu_van_do(tmp_path, monkeypatch):
    """Đổi thứ tự không được làm mất phép dò công cụ: engine có mặt mà thiếu CLI ⇒ ✗."""
    repo = _dung(tmp_path, monkeypatch)
    (repo / "medical-ebm-automation" / "tools").mkdir(parents=True)
    ok, ct, loai = _chay(_CO)
    assert ok is False
    assert "tra_thuoc_quoc_te.py biến mất" in ct, ct
    assert loai == "tai_phat"
