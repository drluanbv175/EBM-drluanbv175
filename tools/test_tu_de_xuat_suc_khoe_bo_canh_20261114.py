"""Giác quan BỘ CANH NỀN của hòm việc (14/11/2026) — `tu_de_xuat_viec.giac_quan_bo_canh_nen`.

Hai giác quan CHỈ ĐỌC: ① ba bộ canh nền (canh_dia_onedrive · canh_mang_vpn · canh_lich_nen_email) đã có plist launchd chưa
— gộp MỘT dòng 👤; ② sức khoẻ bộ canh lịch nền qua `canh_lich_nen_email.suc_khoe()` — mã 1 ⇒ 🛎 (riêng kênh chưa bật ⇒ 👤
nhập kênh bằng `nhap_kenh_canh_bao.py`, lý do khác kèm theo vẫn 🛎 riêng), mã 3 ⇒ 👤 chỉ khi ĐO ĐƯỢC là chưa cài. «Không đo
được» ⇒ giác quan chết (⚪), KHÔNG BAO GIỜ 🟢.

Mọi phép thử chạy trên thư mục tạm (LaunchAgents giả, sổ giả) — KHÔNG đọc ~/Library thật. Nhãn launchd đọc từ mã nguồn
THẬT của ba công cụ (đúng đường giác quan đi trên máy thật).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("tu_de_xuat_viec_bo_canh_20261114", _TOOLS / "tu_de_xuat_viec.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

_BAY_GIO = 1_800_000_000.0  # mốc cố định — không phụ thuộc giờ máy
_BA_TEP = ("canh_dia_onedrive.py", "canh_mang_vpn.py", "canh_lich_nen_email.py")


@pytest.fixture(autouse=True)
def _so_giac_quan_rieng(monkeypatch):
    """Mỗi phép thử một bộ đếm giác quan riêng; vá cả hằng LAUNCH_AGENTS để lỡ quên tham số cũng không đọc ~/Library thật."""
    monkeypatch.setattr(T, "_SO_GIAC_QUAN", {"chay": 0})
    monkeypatch.setattr(T, "_GIAC_QUAN_CHET", [])
    monkeypatch.setattr(T, "LAUNCH_AGENTS", Path("/khong-ton-tai/LaunchAgents-test"))


def _nhan(tep: str) -> str:
    nhan = T._nhan_launchd(_TOOLS / tep)
    assert nhan, f"không đọc được NHAN_LAUNCHD của {tep} — phép thử không đo được"
    return nhan


def _cai(thu_muc: Path, *teps: str) -> Path:
    thu_muc.mkdir(parents=True, exist_ok=True)
    for tep in teps:
        (thu_muc / f"{_nhan(tep)}.plist").write_bytes(b"<plist/>")
    return thu_muc


def _so(tmp_path: Path, ket_qua: str | None = None, cach_giay: float = 3600) -> Path:
    tep = tmp_path / "state" / "canh-lich-nen-email.json"
    tep.parent.mkdir(parents=True, exist_ok=True)
    noi_dung = {} if ket_qua is None else {
        "lan_chay_cuoi": {"luc": round(_BAY_GIO - cach_giay), "ket_qua": ket_qua, "so_loi_do": 0}}
    tep.write_text(json.dumps(noi_dung), encoding="utf-8", newline="\n")
    return tep


def _goi(la: Path, tep_so: Path, nen_tang: str = "darwin", tools: Path | None = None):
    return T.giac_quan_bo_canh_nen(thu_muc_la=la, thu_muc_tools=tools if tools is not None else _TOOLS,
                                   tep_so_email=tep_so, bay_gio=_BAY_GIO, nen_tang=nen_tang)


def _khong_xanh(ra) -> None:
    assert not any("🟢" in v or "🟢" in lenh for _, _, v, lenh in ra), "giác quan bộ canh in 🟢 — cấm"


# ---------------------------------------------------------------------------------------------------------------------
# ① launchd
# ---------------------------------------------------------------------------------------------------------------------
def test_nhan_launchd_doc_tu_ma_nguon_ba_cong_cu() -> None:
    for tep in _BA_TEP:
        assert _nhan(tep).startswith("vn.drluan.ebm-"), tep


def test_chua_cai_ca_ba_la_mot_dong_bac_si_gop_kem_lenh_cai(tmp_path) -> None:
    la = tmp_path / "LaunchAgents"
    la.mkdir()
    ra = _goi(la, tmp_path / "khong-co-so.json")
    assert len(ra) == 1, f"phải đúng MỘT dòng gộp (không nhân đôi dòng «chưa cài» của bộ canh email): {ra}"
    uu, ai, viec, lenh = ra[0]
    assert ai == "👤" and "3/3" in viec and "CHƯA cài" in viec
    for tep in _BA_TEP:
        assert tep.removesuffix(".py") in viec
        assert f"python3 tools/{tep} --cai-launchd --ap-dung" in lenh
    assert "&&" not in lenh, "nối bằng «&&» thì bước đầu hỏng là các bước sau không chạy"
    assert T._GIAC_QUAN_CHET == []
    _khong_xanh(ra)


def test_vang_thu_muc_launchagents_la_do_duoc_chua_cai(tmp_path) -> None:
    ra = _goi(tmp_path / "khong-co-thu-muc", tmp_path / "khong-co-so.json")
    assert [r[1] for r in ra] == ["👤"] and "3/3" in ra[0][2]
    assert T._GIAC_QUAN_CHET == []


def test_ban_disabled_khong_tinh_la_da_cai(tmp_path) -> None:
    la = tmp_path / "LaunchAgents"
    la.mkdir()
    for tep in _BA_TEP:
        (la / f"{_nhan(tep)}.plist.disabled-20260815").write_bytes(b"<plist/>")
    ra = _goi(la, tmp_path / "khong-co-so.json")
    assert len(ra) == 1 and "3/3" in ra[0][2]


def test_hai_bo_chua_cai_email_da_cai_va_khoe(tmp_path) -> None:
    la = _cai(tmp_path / "LaunchAgents", "canh_lich_nen_email.py")
    ra = _goi(la, _so(tmp_path, "xanh"))
    assert len(ra) == 1 and ra[0][1] == "👤" and "2/3" in ra[0][2]
    assert "canh_lich_nen_email" not in ra[0][2] and "canh_lich_nen_email" not in ra[0][3]


def test_da_cai_ca_ba_va_so_khoe_thi_khong_co_viec(tmp_path) -> None:
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    ra = _goi(la, _so(tmp_path, "da_gui"))
    assert ra == []
    assert T._GIAC_QUAN_CHET == []
    assert T._SO_GIAC_QUAN["chay"] == 2, "hai giác quan phải được đếm (launchd + sức khoẻ)"


def test_loi_quyen_doc_plist_la_khong_do_duoc_khong_phai_chua_cai(tmp_path, monkeypatch) -> None:
    la = tmp_path / "LaunchAgents"
    la.mkdir()
    goc = T.Path.stat

    def stat_gia(self, *a, **k):
        if str(self).startswith(str(la)):
            raise PermissionError(13, "Operation not permitted", str(self))
        return goc(self, *a, **k)

    monkeypatch.setattr(T.Path, "stat", stat_gia)
    ra = _goi(la, tmp_path / "khong-co-so.json")
    assert any("bộ canh nền launchd" in c and "không đọc được" in c for c in T._GIAC_QUAN_CHET), T._GIAC_QUAN_CHET
    assert not any("CHƯA cài agent launchd" in v for _, _, v, _ in ra), "lỗi quyền bị đọc thành «chưa cài»"
    _khong_xanh(ra)


def test_khong_doc_duoc_nhan_launchd_la_khong_do_duoc(tmp_path) -> None:
    tools_gia = tmp_path / "tools"
    tools_gia.mkdir()
    for tep in _BA_TEP:
        (tools_gia / tep).write_text("# công cụ giả, không có hằng nhãn\nX = 1\n", encoding="utf-8")
    la = tmp_path / "LaunchAgents"
    la.mkdir()
    ra = _goi(la, tmp_path / "khong-co-so.json", tools=tools_gia)
    assert any("không đọc được NHAN_LAUNCHD" in c for c in T._GIAC_QUAN_CHET), T._GIAC_QUAN_CHET
    # Công cụ giả không có suc_khoe ⇒ giác quan ② cũng phải hiện ra là chết, không im lặng.
    assert any("sức khoẻ bộ canh lịch nền" in c for c in T._GIAC_QUAN_CHET), T._GIAC_QUAN_CHET
    assert not any("CHƯA cài agent launchd" in v for _, _, v, _ in ra)
    _khong_xanh(ra)


def test_khong_phai_macos_la_giac_quan_chet(tmp_path) -> None:
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)  # có plist cũng KHÔNG được coi là đã cài trên nền tảng không có launchd
    ra = _goi(la, _so(tmp_path, "xanh"), nen_tang="win32")
    assert any("bộ canh nền launchd" in c for c in T._GIAC_QUAN_CHET), "nền tảng không có launchd phải là ⚪"
    assert ra == []
    # Chưa từng chạy mà KHÔNG biết đã cài hay chưa (suc_khoe mã 3, da_cai None): ⚪ của ① đã nói «không đo được» — không
    # thêm dòng 👤 «chưa cài» kèm lệnh --cai-launchd lặp lại mỗi phiên (docstring suc_khoe: «không nhắc giả mỗi phiên»).
    for nen_tang in ("linux", "win32"):
        T._GIAC_QUAN_CHET.clear()
        ra2 = _goi(la, tmp_path / "khong-co-so.json", nen_tang=nen_tang)
        assert ra2 == [], f"{nen_tang}: không biết đã cài mà vẫn nhắc «chưa cài»: {ra2}"
        assert any("bộ canh nền launchd" in c for c in T._GIAC_QUAN_CHET), f"{nen_tang}: phải còn ⚪ — không im lặng"


def test_mac_khong_doc_duoc_nhan_email_va_chua_co_luot_khong_nhac_chua_cai(tmp_path) -> None:
    """macOS nhưng không đọc được nhãn của bộ canh email (da_cai None) + sổ trống ⇒ ⚪ ở ①, không dòng 👤 «chưa cài»."""
    tools_gia = tmp_path / "tools"
    tools_gia.mkdir()
    for tep in ("canh_dia_onedrive.py", "canh_mang_vpn.py"):
        (tools_gia / tep).write_text((_TOOLS / tep).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    goc = (_TOOLS / "canh_lich_nen_email.py").read_text(encoding="utf-8")
    assert "\nNHAN_LAUNCHD = " in goc, "mã nguồn bộ canh email đổi cách khai nhãn — phép thử không đo được"
    (tools_gia / "canh_lich_nen_email.py").write_text(goc.replace("\nNHAN_LAUNCHD = ", "\nNHAN_LAUNCHD: str = ", 1),
                                                      encoding="utf-8", newline="\n")
    la = _cai(tmp_path / "LaunchAgents", "canh_dia_onedrive.py", "canh_mang_vpn.py")
    ra = _goi(la, tmp_path / "khong-co-so.json", tools=tools_gia)
    assert any("canh_lich_nen_email.py: không đọc được NHAN_LAUNCHD" in c for c in T._GIAC_QUAN_CHET), T._GIAC_QUAN_CHET
    assert ra == [], f"không biết đã cài mà vẫn nhắc «chưa cài»: {ra}"


def test_thu_muc_ten_plist_khong_tinh_la_da_cai(tmp_path) -> None:
    """Một THƯ MỤC tên «<nhãn>.plist» không phải agent launchd — vẫn là «chưa cài» (khoá S_ISREG)."""
    la = tmp_path / "LaunchAgents"
    la.mkdir()
    for tep in _BA_TEP:
        (la / f"{_nhan(tep)}.plist").mkdir()
    ra = _goi(la, tmp_path / "khong-co-so.json")
    assert len(ra) == 1 and ra[0][1] == "👤" and "3/3" in ra[0][2], ra
    assert T._GIAC_QUAN_CHET == []


@pytest.mark.parametrize("ma_gia", [7, 3])
def test_ma_la_tu_suc_khoe_la_giac_quan_chet_khong_nuot_im_lang(tmp_path, ma_gia) -> None:
    """`suc_khoe` trả mã ngoài {0, 1, 3} — hoặc mã 3 trong khi ① đo được là ĐÃ cài (công cụ không bao giờ trả thế) ⇒ giác
    quan chết «mã lạ», không dòng việc, không im lặng."""
    tools_gia = tmp_path / "tools"
    tools_gia.mkdir()
    for tep in ("canh_dia_onedrive.py", "canh_mang_vpn.py"):
        (tools_gia / tep).write_text((_TOOLS / tep).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    (tools_gia / "canh_lich_nen_email.py").write_text(
        f'NHAN_LAUNCHD = "{_nhan("canh_lich_nen_email.py")}"\n'
        "TEP_STATE = None\n"
        "def doc_state(duong_dan=None):\n    return {}\n"
        f"def suc_khoe(st, bay_gio, da_cai):\n    return {ma_gia}, \"x\"\n",
        encoding="utf-8", newline="\n")
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    ra = _goi(la, tmp_path / "khong-co-so.json", tools=tools_gia)
    assert ra == [], ra
    assert any("sức khoẻ bộ canh lịch nền" in c and f"mã lạ {ma_gia}" in c for c in T._GIAC_QUAN_CHET), T._GIAC_QUAN_CHET


# ---------------------------------------------------------------------------------------------------------------------
# ② sức khoẻ bộ canh lịch nền (đã cài launchd)
# ---------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("ket_qua", ["kenh_khong_do_duoc", "khong_thay_repo", "khong_do_duoc", "khong_gui_error"])
def test_luot_cuoi_khong_toi_kenh_la_chuong(tmp_path, ket_qua) -> None:
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    ra = _goi(la, _so(tmp_path, ket_qua))
    assert len(ra) == 1 and ra[0][1] == "🛎", ra
    assert "KHÔNG đưa được cảnh báo tới email" in ra[0][2]
    assert "canh_lich_nen_email.py" in ra[0][3]
    _khong_xanh(ra)


def test_kenh_chua_bat_la_viec_bac_si(tmp_path) -> None:
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    ra = _goi(la, _so(tmp_path, "kenh_chua_bat"))
    assert len(ra) == 1 and ra[0][1] == "👤", ra
    uu, ai, viec, lenh = ra[0]
    # Lệnh khắc phục phải là công cụ nhập kênh chuyên trách (bác sĩ tự chạy, ô nhập ẩn). `--xem-truoc` KHÔNG đo kênh: lịch
    # xanh thì nó in «🟢 Không có lỗi đỏ» — làm theo hòm việc sẽ nhận một dòng xanh giả ngay trên đường khắc phục.
    assert "python3 tools/nhap_kenh_canh_bao.py" in lenh, lenh
    assert "--xem-truoc" not in lenh, lenh
    assert "giờ không có lượt mới" not in viec, "dòng 👤 chỉ được mang lý do kênh"
    _khong_xanh(ra)


def test_kenh_chua_bat_va_agent_qua_48_gio_tach_hai_dong(tmp_path) -> None:
    """Hai lý do khác chủ: kênh chưa bật (👤 bác sĩ nhập kênh) + agent đã cài mà > 48 giờ không có lượt (🛎 máy chẩn được)."""
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    ra = _goi(la, _so(tmp_path, "kenh_chua_bat", cach_giay=50 * 3600))
    assert sorted(r[1] for r in ra) == sorted(["👤", "🛎"]), ra
    bac_si = next(r for r in ra if r[1] == "👤")
    chuong = next(r for r in ra if r[1] == "🛎")
    assert "nhap_kenh_canh_bao.py" in bac_si[3] and "giờ không có lượt mới" not in bac_si[2], bac_si
    assert "giờ không có lượt mới" in chuong[2] and "nhap_kenh_canh_bao" not in chuong[3], chuong
    _khong_xanh(ra)


def test_so_hong_mang_nhan_kenh_chua_bat_la_chuong_khong_phai_viec_bac_si(tmp_path) -> None:
    """Sổ thiếu mốc lượt cuối thì suc_khoe báo «sổ hỏng» — nhãn kenh_chua_bat còn sót không được đẩy thành việc bác sĩ."""
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    tep = tmp_path / "state" / "canh-lich-nen-email.json"
    tep.parent.mkdir(parents=True, exist_ok=True)
    tep.write_text(json.dumps({"lan_chay_cuoi": {"ket_qua": "kenh_chua_bat"}}), encoding="utf-8", newline="\n")
    ra = _goi(la, tep)
    assert len(ra) == 1 and ra[0][1] == "🛎" and "hỏng" in ra[0][2], ra


def test_da_cai_ma_qua_48_gio_khong_co_luot_moi_la_chuong(tmp_path) -> None:
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    ra = _goi(la, _so(tmp_path, "xanh", cach_giay=50 * 3600))
    assert len(ra) == 1 and ra[0][1] == "🛎" and "giờ không có lượt mới" in ra[0][2], ra


def test_da_cai_ma_so_trong_la_chuong(tmp_path) -> None:
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    ra = _goi(la, _so(tmp_path, None))
    assert len(ra) == 1 and ra[0][1] == "🛎" and "chưa có lượt chạy nào" in ra[0][2], ra


def test_dong_khong_mang_bieu_tuong_trang_thai_cua_cong_cu(tmp_path) -> None:
    la = _cai(tmp_path / "LaunchAgents", *_BA_TEP)
    ra = _goi(la, _so(tmp_path, "kenh_khong_do_duoc"))
    assert not ra[0][2].startswith(("🟡", "⚪", "🟢")), "bảng tự in 🔴/🟠/🟡 theo ưu tiên — không lặp biểu tượng"


# ---------------------------------------------------------------------------------------------------------------------
# Nối dây: main() thật phải gọi giác quan và đưa dòng vào bảng hòm việc (--json)
# ---------------------------------------------------------------------------------------------------------------------
def test_main_dua_dong_bo_canh_vao_bang_hom_viec(monkeypatch, tmp_path) -> None:
    moc = (2, "👤", "DÒNG-MỐC-BỘ-CANH-20261114", "lệnh mốc")
    goi: list[int] = []

    def gia(*a, **k):
        goi.append(1)
        return [moc]

    monkeypatch.setattr(T, "giac_quan_bo_canh_nen", gia)
    monkeypatch.setattr(T, "_chay", lambda lenh, giay=120, cwd=None: "")
    monkeypatch.setattr(T, "DASH", tmp_path / "EBM-Dashboards-khong-ton-tai")
    monkeypatch.setattr(T, "_THONG_TIN", [])
    tep = tmp_path / "hom-viec.json"
    monkeypatch.setattr(sys, "argv", ["tu_de_xuat_viec.py", "--gon", "--json", str(tep)])
    t0 = time.time()
    try:
        T.main()
    except SystemExit:
        pass
    assert goi, "main() không gọi giac_quan_bo_canh_nen"
    assert tep.exists(), f"main() không chạy tới bước ghi bảng việc ({time.time() - t0:.0f}s) — phép thử không đo được"
    viec = json.loads(tep.read_text(encoding="utf-8"))["viec"]
    assert any(v["viec"] == moc[2] and v["ai"] == "👤" for v in viec), "dòng bộ canh không vào bảng hòm việc"
