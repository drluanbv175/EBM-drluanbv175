"""Nút nhập kênh cảnh báo (đóng ESD10) — 26/09/2026. Ngoại tuyến, chỉ ghi tệp tạm."""
from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "nhap_kenh_canh_bao.py"
_sp = importlib.util.spec_from_file_location("nhap_kenh_canh_bao", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

MK = "abcd efgh ijkl mnop"          # mật khẩu ứng dụng giả, đúng khuôn 16 chữ + dấu cách
MK_GON = "abcdefghijklmnop"


def _chay(monkeypatch, tmp_path, dong: list[str], co_san: str = "") -> tuple[int, str, str]:
    f = tmp_path / "secrets.env"
    if co_san:
        f.write_text(co_san, encoding="utf-8", newline="\n")
    monkeypatch.setattr(sys, "stdin", io.StringIO("\n".join(dong) + "\n"))
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    rc = M.main(["--file", str(f)])
    return rc, (f.read_text(encoding="utf-8") if f.exists() else ""), out.getvalue()


def test_gmail_ghi_du_khoa_esd10_giu_dong_khac_khong_in_mat_khau(monkeypatch, tmp_path):
    rc, nd, out = _chay(monkeypatch, tmp_path, ["1", "bs@gmail.com", MK, ""],
                        co_san="NCBI_EMAIL=bs@gmail.com\nSCOPUS_API_KEY=giu-nguyen\n")
    assert rc == 0
    for k, v in {"ENABLE_EMAIL_ALERTS": "true", "SMTP_HOST": "smtp.gmail.com", "SMTP_PORT": "587",
                 "SMTP_FROM": "bs@gmail.com", "ALERT_EMAIL_TO": "bs@gmail.com",
                 "SMTP_PASSWORD": MK_GON}.items():
        assert M.doc_gia_tri(nd, k) == v
    assert "SCOPUS_API_KEY=giu-nguyen" in nd and "NCBI_EMAIL=bs@gmail.com" in nd
    assert MK_GON not in out and "<đã ẩn>" in out


def test_ghi_de_khoa_cu_khong_nhan_doi(monkeypatch, tmp_path):
    rc, nd, _ = _chay(monkeypatch, tmp_path, ["1", "bs@gmail.com", MK, "a@x.vn, b@y.vn"],
                      co_san="SMTP_PASSWORD=cu\nALERT_EMAIL_TO=cu@x.vn\n")
    assert rc == 0
    assert nd.count("SMTP_PASSWORD=") == 1 and M.doc_gia_tri(nd, "SMTP_PASSWORD") == MK_GON
    assert M.doc_gia_tri(nd, "ALERT_EMAIL_TO") == "a@x.vn, b@y.vn"


@pytest.mark.parametrize("dong", [
    ["1", "bs@gmail.com", "matkhaudangnhap123"],     # không phải mật khẩu ứng dụng
    ["1", "khong-phai-email", MK, ""],
    ["1", "bs@gmail.com", MK, "a@x.vn, sai"],        # một địa chỉ nhận sai ⇒ không ghi nửa vời
    ["3", "http://hooks.example.org/x"],             # webhook không https
    ["9"],
])
def test_dau_vao_sai_khong_ghi_gi(monkeypatch, tmp_path, dong):
    rc, nd, _ = _chay(monkeypatch, tmp_path, dong, co_san="GIU=1\n")
    assert rc == 1 and nd == "GIU=1\n"


def test_webhook_https_duoc_ghi_va_an(monkeypatch, tmp_path):
    url = "https://hooks.example.org/services/T0/B0/bimat"
    rc, nd, out = _chay(monkeypatch, tmp_path, ["3", url])
    assert rc == 0 and M.doc_gia_tri(nd, "ALERT_WEBHOOK_URL") == url
    assert "bimat" not in out


def test_smtp_khac_kiem_cong(monkeypatch, tmp_path):
    rc, nd, _ = _chay(monkeypatch, tmp_path, ["2", "smtp.office365.com", "99999"])
    assert rc == 1 and nd == ""
    rc, nd, _ = _chay(monkeypatch, tmp_path, ["2", "smtp.office365.com", "", "a@b.vn", "mk-bat-ky", ""])
    assert rc == 0 and M.doc_gia_tri(nd, "SMTP_PORT") == "587"


def test_du_khoa_esd10_voi_cau_hinh_engine():
    """Tên khoá phải KHỚP đúng tên app/config.py của engine đọc — lệch một chữ là ESD10 vẫn FAIL."""
    goc = Path(__file__).resolve().parents[1]
    ung_vien = [g / "medical-ebm-automation" / "app" / "config.py" for g in (goc, goc.parent)]
    cfg = next((c for c in ung_vien if c.is_file()), None)  # bố cục lồng (Mac) hoặc anh em (Cloud)
    if cfg is None:
        pytest.skip("engine không nằm cạnh repo gốc trên máy này")
    nguon = cfg.read_text(encoding="utf-8")
    for k in ("ENABLE_EMAIL_ALERTS", "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD",
              "SMTP_FROM", "ALERT_EMAIL_TO", "SMTP_USE_TLS", "ALERT_WEBHOOK_URL"):
        assert f'"{k}"' in nguon, k
