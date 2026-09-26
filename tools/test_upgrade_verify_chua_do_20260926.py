"""upgrade_verify.py: bước ⚪ «không đo được» trên bản sao git trần — không FAIL giả, không PASS giả. 26/09/2026."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "upgrade_verify.py"
_sp = importlib.util.spec_from_file_location("upgrade_verify_t", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)


@pytest.mark.parametrize("label", ["19. Pipeline", "21. Standards", "22. CP", "23. Audit tổng thể", "24. Bảng chứng cứ"])
def test_ma_2_cua_buoc_khai_bao_la_chua_do_tren_ban_sao_tran(label):
    assert M.phan_loai_buoc(label, 2, True) == M.CHUA_DO


def test_ma_2_tren_may_that_van_la_hong():
    assert M.phan_loai_buoc("23. Audit tổng thể", 2, False) == M.HONG


def test_ma_2_cua_buoc_khong_khai_bao_van_la_hong():
    """Nhiều công cụ dùng mã 2 cho lỗi thật — không được suy rộng."""
    assert M.phan_loai_buoc("10. Thực tiễn dữ liệu", 2, True) == M.HONG


def test_ma_0_dat_ma_1_hong_none_chua_do():
    assert M.phan_loai_buoc("19. x", 0, True) == M.DAT
    assert M.phan_loai_buoc("19. x", 1, True) == M.HONG
    assert M.phan_loai_buoc("13. x", None, True) == M.CHUA_DO


def test_buoc_can_tep_onedrive(monkeypatch, tmp_path):
    monkeypatch.setattr(M, "ROOT", tmp_path)
    assert M.thieu_dau_vao_onedrive("13. Đồng bộ Hub", True) == "EBM_MASTER/tools/sync_all.py"
    assert M.thieu_dau_vao_onedrive("13. Đồng bộ Hub", False) is None      # máy thật: chạy và để nó FAIL thật
    assert M.thieu_dau_vao_onedrive("10. Khác", True) is None
    (tmp_path / "EBM_MASTER" / "tools").mkdir(parents=True)
    (tmp_path / "EBM_MASTER" / "tools" / "sync_all.py").write_text("", encoding="utf-8", newline="\n")
    assert M.thieu_dau_vao_onedrive("13. Đồng bộ Hub", True) is None


def test_ket_qua_khong_bao_gio_pass_khi_con_chua_do():
    dong = [x.strip() for x in _TEP.read_text(encoding="utf-8").splitlines() if x.strip() and not x.strip().startswith("#")]
    assert "return 1 if fails else (2 if chua_do else 0)" in dong
