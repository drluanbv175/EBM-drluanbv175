"""`audit_ebm_system.py` trên bản sao git trần: «thiếu đầu vào OneDrive» là ⚪, không phải FAIL — 26/09/2026.

Trước đây mọi phiên Cloud ra `KẾT QUẢ: FAIL` vì 4 nhóm kiểm có đầu vào chỉ nằm trên OneDrive (template,
file mặc định, CHATGPT_EXPORT, Antifacts.html), che mất lỗi thật. Ngoại tuyến.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "audit_ebm_system.py"
_sp = importlib.util.spec_from_file_location("audit_ebm_system_bst", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

_THIEU_TEMPLATE = "thiếu template a.html hoặc b.html"
_LECH_TEMPLATE = "a.html lệch với b.html"


def _la_thieu(m):
    return m.startswith("thiếu template ")


def test_ban_sao_tran_ha_loi_thieu_dau_vao_thanh_khong_do_duoc():
    cung, kd = M.tach_loi_thieu_dau_vao(True, [_THIEU_TEMPLATE], _la_thieu)
    assert cung == [] and kd == [_THIEU_TEMPLATE]


def test_ban_sao_tran_van_giu_loi_lech_noi_dung_la_loi_cung():
    cung, kd = M.tach_loi_thieu_dau_vao(True, [_THIEU_TEMPLATE, _LECH_TEMPLATE], _la_thieu)
    assert cung == [_LECH_TEMPLATE] and kd == [_THIEU_TEMPLATE]


@pytest.mark.parametrize("loi", [[_THIEU_TEMPLATE], [_THIEU_TEMPLATE, _LECH_TEMPLATE]])
def test_may_that_moi_loi_deu_cung(loi):
    """Máy thật thiếu template là cây OneDrive hỏng — phải ĐỎ như cũ."""
    cung, kd = M.tach_loi_thieu_dau_vao(False, loi, _la_thieu)
    assert cung == loi and kd == []


def _dong_thi_hanh(nguon: str) -> list[str]:
    return [x for x in nguon.splitlines() if x.strip() and not x.strip().startswith("#")]


def test_bon_nhom_onedrive_deu_di_qua_bo_tach():
    """Khớp DÒNG THI HÀNH (không khớp chú thích): cả 4 nhóm phải gọi bộ tách/nhánh bản sao trần."""
    dong = "\n".join(_dong_thi_hanh(_TEP.read_text(encoding="utf-8")))
    for goi in ("template_sync_failures()", "default_file_failures()", "chatgpt_integration_failures()"):
        assert f"ban_sao_tran, {goi}" in dong, goi
    assert 'ban_sao_tran and antifacts_msg == "thiếu Antifacts.html"' in dong


def test_ket_qua_chua_ket_luan_khong_bao_gio_la_pass():
    dong = _dong_thi_hanh(_TEP.read_text(encoding="utf-8"))
    i = next(k for k, x in enumerate(dong) if "if khong_do_duoc:" in x and "KẾT QUẢ: CHƯA KẾT LUẬN" in "".join(dong[k:k + 4]))
    khoi = dong[i:i + 8]
    assert any(x.strip() == "return 2" for x in khoi)
    assert not any("KẾT QUẢ: PASS" in x for x in khoi)
