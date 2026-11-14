"""Sổ xác minh nguồn: KHOÁ GHI + GỘP BA CHIỀU — hai lượt ghi song song không còn xoá mất bản ghi của nhau (14/11/2026).

Trước vá: `--quet`/`--vong`, `--quet-ledger`, `--phu-mo-coi`, `--kiem-rut-lai` và cầu NC⇄LS cùng ĐỌC cả sổ, chạy mạng
nhiều phút, rồi GHI ĐÈ cả sổ ⇒ lượt ghi sau xoá mất bản ghi của lượt ghi trước, kể cả dương tính rút bài (PR #349 đã phải
hoãn `--phu-mo-coi` vì một phiên khác đang ghi sổ). Nay `ghi_so` cầm khoá tệp, đọc lại sổ trên đĩa, gộp ba chiều rồi mới
ghi nguyên tử; hết hạn chờ khoá ⇒ `SoDangKhoaLoi`, không ghi gì, CLI mã 3 + «[MA] SO_DANG_KHOA».

Ngoại tuyến: sổ tạm trong tmp_path, không gọi mạng, không đọc dữ liệu thật ngoài git.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import time
from pathlib import Path
from unittest import mock

import pytest

_THU_MUC = Path(__file__).resolve().parent
_TEP = _THU_MUC / "so_xac_minh_nguon.py"
_BAY_GIO = "2026-11-14T10:00:00"


@pytest.fixture()
def M(tmp_path, monkeypatch):
    sp = importlib.util.spec_from_file_location("so_xac_minh_khoa_ghi_20261114", _TEP)
    mod = importlib.util.module_from_spec(sp)
    sys.modules["so_xac_minh_khoa_ghi_20261114"] = mod
    sp.loader.exec_module(mod)
    monkeypatch.setattr(mod, "SO", tmp_path / ".so-xac-minh-nguon.json")
    monkeypatch.setattr(mod, "DASH", tmp_path)
    monkeypatch.setattr(mod, "_nap_verify_dashboard", lambda: None)
    monkeypatch.setattr(mod, "kiem_rut_bai", lambda ds: {})
    monkeypatch.setattr(mod, "kiem_rut_doi", lambda ds: {})
    return mod


def _bg(gt: str, **them) -> dict:
    bg = {"loai": "pmid", "gia_tri": gt, "cac_dashboard": ["A.html"], "xac_minh_luc": _BAY_GIO,
          "kiem_rut_luc": _BAY_GIO, "ghi_chu_rut": "ok", "tieu_de": "t", "nguon_xac_minh": "pubmed"}
    bg.update(them)
    return bg


def _dat_so(M, muc: dict) -> None:
    M.SO.write_text(json.dumps({"phien_ban": 1, "muc": muc}, ensure_ascii=False), encoding="utf-8")


def _tren_dia(M) -> dict:
    return json.loads(M.SO.read_text(encoding="utf-8"))["muc"]


# ── 1. Gộp ba chiều trong MỘT tiến trình (hai lượt đọc trước, ghi xen kẽ) ────────────────────────────────────────────

def test_hai_luot_xen_ke_khong_mat_ban_ghi(M):
    _dat_so(M, {"pmid:1": _bg("1")})
    a, b = M.doc_so(), M.doc_so()
    a["muc"]["pmid:2"] = _bg("2")
    b["muc"]["pmid:3"] = _bg("3")
    M.ghi_so(a)
    M.ghi_so(b)  # bản cũ: ghi đè cả sổ ⇒ mất pmid:2 của lượt A
    assert set(_tren_dia(M)) == {"pmid:1", "pmid:2", "pmid:3"}
    assert set(b["muc"]) == {"pmid:1", "pmid:2", "pmid:3"}, "sổ trong bộ nhớ phải được cập nhật thành bản vừa ghi"


def test_duong_tinh_tren_dia_khong_bi_ok_cu_de(M):
    """Lượt B ghi «đã rút» cho pmid:9; lượt A (đọc TRƯỚC đó) ghi lại kiểm «ok» cũ + xác minh tồn tại mới ⇒ giữ «đã rút»."""
    _dat_so(M, {"pmid:9": _bg("9")})
    a, b = M.doc_so(), M.doc_so()
    b["muc"]["pmid:9"].update(da_rut=True, ghi_chu_rut="retracted", rut_va_thay=False, kiem_rut_luc="2026-11-14T11:00:00",
                              thong_bao_ids=["pmid:999"], sua_loi_bi_rut=False)
    M.ghi_so(b)
    a["muc"]["pmid:9"] = _bg("9", xac_minh_luc="2026-11-14T12:00:00", kiem_rut_luc="2026-11-14T12:00:00", tieu_de="moi")
    M.ghi_so(a)
    bg = _tren_dia(M)["pmid:9"]
    assert bg["da_rut"] is True and bg["ghi_chu_rut"] == "retracted", "dương tính rút bài bị một «ok» cũ đè mất"
    assert bg["thong_bao_ids"] == ["pmid:999"] and bg["kiem_rut_luc"] == "2026-11-14T11:00:00"
    assert bg["xac_minh_luc"] == "2026-11-14T12:00:00" and bg["tieu_de"] == "moi", "mất thay đổi tồn tại của lượt A"
    assert M.con_hieu_luc(bg) == (False, "ĐÃ BỊ RÚT")


def test_co_eoc_tren_dia_dinh_lai(M):
    _dat_so(M, {"pmid:8": _bg("8")})
    a, b = M.doc_so(), M.doc_so()
    b["muc"]["pmid:8"].update(quan_ngai=True, ghi_chu_rut="expression_of_concern")
    M.ghi_so(b)
    a["muc"]["pmid:8"]["kiem_rut_luc"] = "2026-11-14T12:00:00"  # lượt A ghi lại phán quyết «ok» của nó
    M.ghi_so(a)
    bg = _tren_dia(M)["pmid:8"]
    assert bg.get("quan_ngai") is True and M._la_duong_tinh(bg), "cờ EoC trên đĩa bị mất"


def test_luoi_cuoi_da_rut_tren_dia_khong_mat_ke_ca_khi_ban_cua_ta_duong_tinh_eoc(M):
    """Ta (dương tính EoC) lỡ bỏ `da_rut` trong khi lượt kia vừa đổi bản ghi ⇒ «đã rút» của đĩa vẫn giữ (lưới cuối)."""
    _dat_so(M, {"pmid:7": _bg("7", da_rut=True, ghi_chu_rut="retracted")})
    a, b = M.doc_so(), M.doc_so()
    b["muc"]["pmid:7"]["tieu_de"] = "B sua"
    M.ghi_so(b)
    bg_a = a["muc"]["pmid:7"]
    del bg_a["da_rut"]
    bg_a.update(quan_ngai=True, ghi_chu_rut="expression_of_concern")
    M.ghi_so(a)
    bg = _tren_dia(M)["pmid:7"]
    assert bg.get("da_rut") is True, "«đã rút» trên đĩa bị mất khi gộp"
    assert bg["tieu_de"] == "B sua"


def test_eoc_chi_ghi_bang_ghi_chu_rut_van_dinh_khi_ta_ghi_da_rut(M):
    """Đĩa mang EoC qua `ghi_chu_rut` (không cờ), ta ghi «retracted» ⇒ kết quả vẫn mang cờ EoC (không trộn mất)."""
    _dat_so(M, {"pmid:6": _bg("6")})
    a, b = M.doc_so(), M.doc_so()
    b["muc"]["pmid:6"]["ghi_chu_rut"] = "expression_of_concern"
    M.ghi_so(b)
    a["muc"]["pmid:6"].update(da_rut=True, ghi_chu_rut="retracted")
    M.ghi_so(a)
    bg = _tren_dia(M)["pmid:6"]
    assert bg["da_rut"] is True and bg.get("quan_ngai") is True


def test_dia_bi_thay_mat_ban_ghi_duong_tinh_thi_giu_ban_cua_ta(M):
    """Lượt khác ghi một sổ THIẾU bản ghi ta không đổi: bản dương tính được giữ lại, bản thường theo đĩa."""
    _dat_so(M, {"pmid:1": _bg("1"), "pmid:2": _bg("2", da_rut=True, ghi_chu_rut="retracted")})
    a = M.doc_so()
    M.SO.write_text(json.dumps({"phien_ban": 1, "muc": {"pmid:5": _bg("5")}}), encoding="utf-8")
    a["muc"]["pmid:3"] = _bg("3")
    M.ghi_so(a)
    tren = _tren_dia(M)
    assert tren.get("pmid:2", {}).get("da_rut") is True, "dương tính rút bài rơi khỏi sổ"
    assert set(tren) == {"pmid:2", "pmid:3", "pmid:5"}


def test_cac_dashboard_gop_tap_ba_chieu(M):
    _dat_so(M, {"pmid:5": _bg("5", cac_dashboard=["X.html", "Y.html"])})
    a, b = M.doc_so(), M.doc_so()
    a["muc"]["pmid:5"]["cac_dashboard"] = ["X.html"]          # A gỡ Y (dashboard thôi trích)
    b["muc"]["pmid:5"]["cac_dashboard"] = ["X.html", "Y.html", "Z.html"]  # B thêm Z
    b["muc"]["pmid:5"]["tieu_de"] = "cua B"
    M.ghi_so(b)
    M.ghi_so(a)
    bg = _tren_dia(M)["pmid:5"]
    assert bg["cac_dashboard"] == ["X.html", "Z.html"], "phải giữ Z của B và áp việc gỡ Y của A"
    assert bg["tieu_de"] == "cua B", "trường A không đổi phải theo đĩa"


def test_bi_danh_muc_va_ban_ghi_van_dung_sau_khi_gop(M):
    """Caller giữ `muc = so["muc"]` và `bg = muc[k]` (đúng như lenh_quet/--phu-mo-coi) — gộp phải sửa TẠI CHỖ."""
    _dat_so(M, {"pmid:1": _bg("1"), "pmid:2": _bg("2")})
    a, b = M.doc_so(), M.doc_so()
    muc = a["muc"]
    bg1 = muc["pmid:1"]
    b["muc"]["pmid:1"]["tieu_de"] = "B sua"
    M.ghi_so(b)
    muc["pmid:2"]["tieu_de"] = "A sua"
    M.ghi_so(a)
    assert a["muc"] is muc and muc["pmid:1"] is bg1, "gộp đã thay đối tượng — bí danh của caller trỏ vào bản cũ"
    assert bg1["tieu_de"] == "B sua"
    bg1["nam"] = "2026"  # caller tiếp tục sửa qua bí danh cũ
    M.ghi_so(a)
    tren = _tren_dia(M)
    assert tren["pmid:1"]["nam"] == "2026" and tren["pmid:1"]["tieu_de"] == "B sua"
    assert tren["pmid:2"]["tieu_de"] == "A sua"


def test_dict_thuong_khong_xoa_ban_ghi_tren_dia(M):
    _dat_so(M, {"pmid:1": _bg("1"), "pmid:2": _bg("2", da_rut=True, ghi_chu_rut="retracted")})
    M.ghi_so({"phien_ban": 1, "muc": {"pmid:3": _bg("3")}})
    assert set(_tren_dia(M)) == {"pmid:1", "pmid:2", "pmid:3"}
    assert _tren_dia(M)["pmid:2"]["da_rut"] is True


def test_khong_ai_doi_thi_ghi_dung_noi_dung_cua_toi(M):
    _dat_so(M, {"pmid:1": _bg("1")})
    a = M.doc_so()
    del a["muc"]["pmid:1"]
    a["muc"]["pmid:4"] = _bg("4")
    M.ghi_so(a)
    assert set(_tren_dia(M)) == {"pmid:4"}, "khi đĩa không đổi, việc chính ta xoá vẫn phải có hiệu lực"


def test_so_hong_luc_ghi_khong_ghi_gi(M):
    _dat_so(M, {"pmid:1": _bg("1")})
    a = M.doc_so()
    hong = b'{"phien_ban": 1, "muc": {"pmid:1": {"loai": "pm'
    M.SO.write_bytes(hong)
    a["muc"]["pmid:2"] = _bg("2")
    with pytest.raises(M.SoHongLoi):
        M.ghi_so(a)
    assert M.SO.read_bytes() == hong, "sổ hỏng bị ghi đè — dương tính trong phần còn đọc được có thể mất"


# ── 2. Khoá: tiến trình khác giữ khoá ⇒ hết hạn chờ, KHÔNG ghi ───────────────────────────────────────────────────────

_CON_GIU_KHOA = r'''
import importlib.util, sys, time
from pathlib import Path
tep, so, san_sang = sys.argv[1:4]
sp = importlib.util.spec_from_file_location("sxm_con_giu_khoa", tep)
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)
m.SO = Path(so)
with m._KhoaSo():
    Path(san_sang).touch()
    time.sleep(60)
'''


@contextlib.contextmanager
def _tien_trinh_giu_khoa(M, tmp_path):
    kich_ban = tmp_path / "con_giu_khoa.py"
    kich_ban.write_text(_CON_GIU_KHOA, encoding="utf-8")
    san_sang = tmp_path / "da_giu_khoa"
    p = subprocess.Popen([sys.executable, "-B", str(kich_ban), str(_TEP), str(M.SO), str(san_sang)])
    try:
        han = time.monotonic() + 20
        while not san_sang.exists():
            assert p.poll() is None, "tiến trình giữ khoá chết sớm"
            assert time.monotonic() < han, "tiến trình con không cầm được khoá trong 20 giây"
            time.sleep(0.02)
        yield p
    finally:
        p.kill()
        p.wait(timeout=10)


def test_khoa_dang_bi_giu_thi_het_han_bao_loi_va_khong_ghi(M, tmp_path, monkeypatch):
    _dat_so(M, {"pmid:1": _bg("1")})
    truoc = M.SO.read_bytes()
    a = M.doc_so()
    a["muc"]["pmid:2"] = _bg("2")
    monkeypatch.setattr(M, "HAN_CHO_KHOA_GIAY", 0.4)
    with _tien_trinh_giu_khoa(M, tmp_path):
        t0 = time.monotonic()
        with pytest.raises(M.SoDangKhoaLoi) as ei:
            M.ghi_so(a)
        assert time.monotonic() - t0 >= 0.35, "báo hết hạn quá sớm — không thật sự chờ khoá"
        assert "KHÔNG ghi gì" in str(ei.value)
        assert M.SO.read_bytes() == truoc, "ghi khi CHƯA cầm khoá"
        assert not list(M.SO.parent.glob("*.tmp"))
    M.ghi_so(a)  # tiến trình kia thoát ⇒ khoá hệ điều hành tự nhả, ghi bình thường
    assert set(_tren_dia(M)) == {"pmid:1", "pmid:2"}


def test_cli_het_han_khoa_tra_3_va_ma_so_dang_khoa(M, tmp_path, monkeypatch, capsys):
    _dat_so(M, {"pmid:111": {"loai": "pmid", "gia_tri": "111", "cac_dashboard": ["NC:x"]}})
    truoc = M.SO.read_bytes()
    monkeypatch.setattr(M, "HAN_CHO_KHOA_GIAY", 0.3)
    monkeypatch.setattr(M, "xac_minh_mot", lambda khoa, vd: {"loai": "pmid", "gia_tri": "111",
                                                             "xac_minh_luc": _BAY_GIO, "tieu_de": "t"})
    with _tien_trinh_giu_khoa(M, tmp_path), \
            mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--phu-mo-coi", "--vong", "1"]):
        rc = M.main()
    err = capsys.readouterr().err
    assert rc == 3, "hết hạn chờ khoá không được là 0 (sạch), 1 (thiếu) hay 2 (rút bài)"
    assert "[MA] SO_DANG_KHOA" in err
    assert M.SO.read_bytes() == truoc


def test_chu_trinh_doc_ma_so_dang_khoa_khong_goi_la_thieu_dashboard(capsys):
    sys.path.insert(0, str(_THU_MUC))
    import chu_trinh_chung_cu as ctcc  # noqa: PLC0415

    class _P:
        def __init__(self, rc, out):
            self.returncode, self.stdout, self.stderr = rc, out, ""

    def _goi(cmd, **kw):
        cmd = [str(c) for c in cmd]
        if len(cmd) > 1 and "so_xac_minh_nguon.py" in cmd[1]:
            return _P(3, "⛔ … khoá ghi …\n[MA] SO_DANG_KHOA — không ghi gì vào sổ\n")
        return _P(0, "")

    with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", "--nhanh"]), \
            mock.patch.object(ctcc.subprocess, "run", side_effect=_goi), \
            mock.patch.object(ctcc, "_co_dashboard_that", return_value=True):
        rc = ctcc.main()
    out = capsys.readouterr().out
    assert rc == 1, "không ghi được sổ không bao giờ là 🟢"
    assert "giữ khoá ghi" in out
    assert "thiếu EBM-Dashboards/" not in out


def test_chu_trinh_bao_khi_buoc_3a_3b_vuong_khoa(capsys):
    sys.path.insert(0, str(_THU_MUC))
    import chu_trinh_chung_cu as ctcc  # noqa: PLC0415

    class _P:
        def __init__(self, rc, out):
            self.returncode, self.stdout, self.stderr = rc, out, ""

    def _goi(cmd, **kw):
        cmd = [str(c) for c in cmd]
        if len(cmd) > 1 and "so_xac_minh_nguon.py" in cmd[1] and "--quet-ledger" in cmd:
            return _P(3, "[MA] SO_DANG_KHOA — không ghi gì vào sổ\n")
        return _P(0, "")

    with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py"]), \
            mock.patch.object(ctcc.subprocess, "run", side_effect=_goi), \
            mock.patch.object(ctcc, "_co_dashboard_that", return_value=True):
        ctcc.main()
    out = capsys.readouterr().out
    assert "③a/③b không ghi được" in out


# ── 3. Nhiều TIẾN TRÌNH thật ghi cùng một sổ tạm ─────────────────────────────────────────────────────────────────────

_CON_GHI = r'''
import importlib.util, sys, time
from pathlib import Path
tep, so, cho, idx = sys.argv[1:5]
sp = importlib.util.spec_from_file_location("sxm_con_ghi", tep)
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)
m.SO = Path(so)
so_mem = m.doc_so()                       # MỌI tiến trình đọc TRƯỚC khi ai ghi — đúng ca chạy mạng song song
Path(cho + ".san-sang-" + idx).touch()
while not Path(cho).exists():
    time.sleep(0.005)
muc = so_mem["muc"]
for j in range(20):
    gt = idx + "%03d" % j
    muc["pmid:" + gt] = {"loai": "pmid", "gia_tri": gt, "cac_dashboard": ["D" + idx + ".html"],
                         "xac_minh_luc": "2026-11-14T10:00:00", "kiem_rut_luc": "2026-11-14T10:00:00",
                         "ghi_chu_rut": "ok"}
    if j % 5 == 4:
        m.ghi_so(so_mem)                  # ghi từng chặng như lenh_quet
gt = "9" + idx
muc["pmid:" + gt] = {"loai": "pmid", "gia_tri": gt, "cac_dashboard": ["D" + idx + ".html"], "da_rut": True,
                     "ghi_chu_rut": "retracted", "xac_minh_luc": "2026-11-14T10:00:00",
                     "kiem_rut_luc": "2026-11-14T10:00:00"}
chung = muc["pmid:1"]
chung["cac_dashboard"] = sorted(set(chung["cac_dashboard"]) | {"D" + idx + ".html"})
m.ghi_so(so_mem)
'''


def test_nhieu_tien_trinh_ghi_dong_thoi_khong_mat_ban_ghi(M, tmp_path):
    so_tien_trinh = 6
    _dat_so(M, {"pmid:1": _bg("1", cac_dashboard=["goc.html"])})
    kich_ban = tmp_path / "con_ghi.py"
    kich_ban.write_text(_CON_GHI, encoding="utf-8")
    cho = tmp_path / "bat_dau"
    ps = [subprocess.Popen([sys.executable, "-B", str(kich_ban), str(_TEP), str(M.SO), str(cho), str(i + 1)])
          for i in range(so_tien_trinh)]
    try:
        han = time.monotonic() + 30
        while len(list(tmp_path.glob("bat_dau.san-sang-*"))) < so_tien_trinh:
            assert all(p.poll() is None for p in ps), "một tiến trình con chết trước khi tới vạch xuất phát"
            assert time.monotonic() < han, "tiến trình con không sẵn sàng trong 30 giây"
            time.sleep(0.02)
        cho.touch()
        for p in ps:
            assert p.wait(timeout=60) == 0
    finally:
        for p in ps:
            if p.poll() is None:
                p.kill()
    muc = _tren_dia(M)
    mong_doi = {f"pmid:{i}{j:03d}" for i in range(1, so_tien_trinh + 1) for j in range(20)}
    assert mong_doi <= set(muc), f"mất {len(mong_doi - set(muc))} bản ghi do ghi đè lẫn nhau"
    for i in range(1, so_tien_trinh + 1):
        assert muc.get(f"pmid:9{i}", {}).get("da_rut") is True, f"mất dương tính rút bài của tiến trình {i}"
    assert muc["pmid:1"]["cac_dashboard"] == sorted({"goc.html"} | {f"D{i}.html" for i in range(1, so_tien_trinh + 1)})
    assert not list(tmp_path.glob("*.tmp"))


# ── 4. --cuu-so-hong vẫn ghi được sổ mới đè lên bản hỏng (đường duy nhất được phép) ───────────────────────────────────

def test_cuu_so_hong_van_ghi_de_ban_hong(M):
    M.SO.write_bytes(b'{"phien_ban": 1, "muc": {"pmid:7": {"da_rut": true, "loai": "pmid"}, "pmid:6": {"lo')
    with contextlib.redirect_stdout(io.StringIO()):
        assert M.cuu_so_hong() == 0
    muc = M.doc_so()["muc"]
    assert set(muc) == {"pmid:7"} and muc["pmid:7"]["da_rut"] is True


def test_phu_mo_coi_van_chay_qua_khoa(M, monkeypatch):
    """Đường CLI thật (--phu-mo-coi) đi qua ghi_so có khoá và vẫn hội tụ như trước."""
    _dat_so(M, {"pmid:111": {"loai": "pmid", "gia_tri": "111", "cac_dashboard": ["NC:x"]}})
    monkeypatch.setattr(M, "xac_minh_mot", lambda khoa, vd: {"loai": "pmid", "gia_tri": "111",
                                                             "xac_minh_luc": "2026-11-14T10:00:00", "tieu_de": "t"})
    with contextlib.redirect_stdout(io.StringIO()):
        rc = M._chay_lenh(argparse.Namespace(phu_mo_coi=True, vong=1, kiem_rut_lai=None, quet_ledger=False,
                                             bao_cao=False, quet=None, cuu_so_hong=False))
    assert rc == 0
    bg = _tren_dia(M)["pmid:111"]
    assert bg["xac_minh_luc"] == "2026-11-14T10:00:00" and bg["cac_dashboard"] == ["NC:x"]
    assert M.SO.with_name(M.SO.name + ".lock").exists(), "ghi_so không đi qua khoá tệp"
