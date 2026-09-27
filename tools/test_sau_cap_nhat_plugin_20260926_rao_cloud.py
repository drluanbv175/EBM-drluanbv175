"""Nghi thức sau-cập-nhật-plugin KHÔNG ghi đè danh mục gộp hai máy từ nơi thiếu dữ liệu — 26/09/2026 (#25).

Ca tái lập: trên Cloud, `sau_cap_nhat_plugin.py --ghi-moc` (mục 🤖 của hệ tự đề xuất) dựng lại
DANH-MUC-CONG-CU.md (1876 → 1032 mục) và INDEX-CONG-CU.md (865 → 236 dòng) — hai tệp ĐANG TRACK —
từ catalog_may/ chỉ có bản chụp của container; rồi so kho Cloud với mốc WINDOWS («4→9 plugin»).
Test khoá:
  (i)  phiên Cloud ⇒ mã 2, KHÔNG gọi bước nào (không extract/build_*);
  (ii) máy thật mà catalog_may/ chỉ có MỘT máy ⇒ mã 2 sau ①, không gọi build_danh_muc/build_trang_tra_cuu;
  (iii) đủ Mac + Windows (xét trường `may` BÊN TRONG tệp) ⇒ chạy đủ ①②③;
  (iv) `de_xuat_plugin`: Cloud không có mục 🤖 «ghi mốc», rc=2 trên Cloud không gợi ý sau_cap_nhat_plugin;
       máy thật giữ nguyên lệnh cũ.
Ngoại tuyến: `_buoc` giả ghi nhận, catalog_may/ giả trong thư mục tạm.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_THU_MUC = Path(__file__).resolve().parent


def _nap(ten: str, bi_danh: str):
    sp = importlib.util.spec_from_file_location(bi_danh, _THU_MUC / ten)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


S = _nap("sau_cap_nhat_plugin.py", "sau_cap_nhat_plugin_rao_cloud")
T = _nap("tu_de_xuat_viec.py", "tu_de_xuat_viec_de_xuat_plugin")


def _chup(snap: Path, ten_tep: str, may: str | None) -> None:
    snap.mkdir(parents=True, exist_ok=True)
    d = {"ngay_quet": "2026-09-26", "muc": []}
    if may is not None:
        d["may"] = may
    (snap / ten_tep).write_text(json.dumps(d), encoding="utf-8")


@pytest.fixture
def goi(monkeypatch, tmp_path):
    """`_buoc` giả: ghi nhận lệnh, luôn thành công; catalog_may/ trỏ vào thư mục tạm."""
    da_goi: list[str] = []

    def buoc_gia(ten, lenh):
        da_goi.append(lenh[0])
        return True
    monkeypatch.setattr(S, "_buoc", buoc_gia)
    monkeypatch.setattr(S, "SNAP_DIR", tmp_path / "catalog_may")
    return da_goi


def test_i_phien_cloud_ma_2_khong_goi_buoc_nao(goi, monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
    _chup(tmp_path / "catalog_may", "Mac.json", "Mac")
    _chup(tmp_path / "catalog_may", "Windows.json", "Windows")   # đủ hai máy vẫn phải chặn trên Cloud
    assert S.main(["--ghi-moc"]) == 2
    assert goi == []


def test_ii_catalog_mot_may_ma_2_khong_dung_danh_muc(goi, monkeypatch, tmp_path):
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    _chup(tmp_path / "catalog_may", "Mac.json", "Mac")
    assert S.main([]) == 2
    assert goi == ["tools/vietnamize/extract_catalog.py"]
    assert not any("build_" in x for x in goi)


def test_ii_ten_tep_khong_phai_danh_tinh_may(goi, monkeypatch, tmp_path):
    """Tệp tên «Windows.json» nhưng trường `may` là Linux ⇒ vẫn là THIẾU Windows."""
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    _chup(tmp_path / "catalog_may", "Mac.json", "Mac")
    _chup(tmp_path / "catalog_may", "Windows.json", "Linux")
    assert S.main([]) == 2
    assert not any("build_" in x for x in goi)


def test_iii_du_hai_may_chay_du_buoc(goi, monkeypatch, tmp_path):
    monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
    _chup(tmp_path / "catalog_may", "Mac-DESKTOP-XYZ.json", "Mac")   # bản trùng OneDrive
    _chup(tmp_path / "catalog_may", "Windows.json", "Windows")
    assert S.main([]) == 0
    assert goi == ["tools/vietnamize/extract_catalog.py", "tools/vietnamize/build_danh_muc.py",
                   "tools/vietnamize/build_trang_tra_cuu.py"]


def test_moc_so_nhay_vot_dung_ten_may_cua_nhan_dien_may():
    """Dòng thi hành chọn mốc phải dùng ten_may() — không còn «Darwin ⇒ Mac, còn lại ⇒ Windows»."""
    nguon = (_THU_MUC / "sau_cap_nhat_plugin.py").read_text(encoding="utf-8")
    dong = [x.split("#")[0] for x in nguon.splitlines() if x.strip().startswith("may = ")]
    assert dong and all("ten_may()" in x for x in dong)
    assert not any("platform.system()" in x for x in dong)


# ---------- (iv) de_xuat_plugin ----------

def test_iv_cloud_lech_phien_ban_khong_co_muc_may():
    dong = T.de_xuat_plugin(1, cloud=True)
    assert not any("🤖" in d[1] or "sau_cap_nhat_plugin" in d[3] for d in dong)


def test_iv_cloud_thieu_plugin_van_canh_bao_nhung_khong_goi_nghi_thuc():
    dong = T.de_xuat_plugin(2, cloud=True)
    assert dong, "THIẾU plugin trên Cloud vẫn phải cảnh báo"
    assert not any("sau_cap_nhat_plugin" in d[3] for d in dong)
    assert any("cai_plugin_phien_cloud.py" in d[3] for d in dong)


@pytest.mark.parametrize("rc, uu", [(1, 2), (2, 1)])
def test_iv_may_that_giu_nguyen_lenh_cu(rc, uu):
    dong = T.de_xuat_plugin(rc, cloud=False)
    assert len(dong) == 1 and dong[0][0] == uu and dong[0][1] == "🤖"
    assert "sau_cap_nhat_plugin.py --ghi-moc" in dong[0][3]


@pytest.mark.parametrize("cloud", [True, False])
def test_iv_kho_du_khong_de_xuat(cloud):
    assert T.de_xuat_plugin(0, cloud=cloud) == []


def test_iv_main_noi_day_de_xuat_plugin_voi_la_phien_cloud():
    """Khớp DÒNG thi hành: main() phải đưa kết quả qua de_xuat_plugin(..., la_phien_cloud())."""
    nguon = (_THU_MUC / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    dong = [x for x in nguon.splitlines() if "de_xuat_plugin(" in x and not x.lstrip().startswith("def ")]
    assert any("r_pl.returncode" in x and "la_phien_cloud()" in x for x in dong)
