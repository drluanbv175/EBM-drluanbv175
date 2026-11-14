"""Sổ xác minh nguồn — bốn việc còn mở sau #355 (thẩm định 14/11/2026).

(1) Đột biến M4 của người duyệt SỐNG SÓT: bỏ bước làm mới ảnh gốc cuối `ghi_so` mà 83 test vẫn xanh, trong khi hành vi sai
    thật — bản ghi/trường một tiến trình đã XOÁ «hồi sinh» khi nó (hoặc tiến trình khác xen giữa) ghi lần sau.
(2) Hai bên cùng dương tính: docstring nói «phán quyết của ta (mới hơn) thắng» nhưng mã không so `kiem_rut_luc` ⇒ một
    «rút & thay» CŨ đè được «rút bỏ hẳn» MỚI. Nay so mốc; không xác định được bên mới hơn ⇒ giữ bên nghiêm trọng hơn.
(3) Lượt vừa thấy dương tính MỚI rồi hết hạn chờ khoá ⇒ trước chỉ có mã 3 + ⚪ «khoá bận» (dương tính mất im lặng). Nay in
    danh sách + «[MA] DUONG_TINH_CHUA_VAO_SO», mã 2; chu trình nêu 🔴.
(4) Cầu NC⇄LS gặp `SoDangKhoaLoi` thoát bằng traceback; orchestrator xếp mã 3 của A4 chung «sổ xác minh chưa đủ». Nay cả hai
    nhận mã SO_DANG_KHOA, báo «sổ đang khoá — chạy lại sau», không traceback, không xanh giả.

Ngoại tuyến: sổ tạm trong tmp_path, tiến trình con chỉ dùng sổ tạm, không gọi mạng, không đọc dữ liệu thật ngoài git.
"""
from __future__ import annotations

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
_GOC = _THU_MUC.parent
_TEP = _THU_MUC / "so_xac_minh_nguon.py"
_CU = "2026-11-10T09:00:00"
_MOI = "2026-11-14T09:00:00"


def _nap(ten: str, duong: Path):
    sp = importlib.util.spec_from_file_location(ten, duong)
    mod = importlib.util.module_from_spec(sp)
    sys.modules[ten] = mod
    sp.loader.exec_module(mod)
    return mod


@pytest.fixture()
def M(tmp_path, monkeypatch):
    mod = _nap("so_xac_minh_tiep_20261114d", _TEP)
    monkeypatch.setattr(mod, "SO", tmp_path / ".so-xac-minh-nguon.json")
    monkeypatch.setattr(mod, "DASH", tmp_path)
    monkeypatch.setattr(mod, "_nap_verify_dashboard", lambda: None)
    monkeypatch.setattr(mod, "kiem_rut_bai", lambda ds: {})
    monkeypatch.setattr(mod, "kiem_rut_doi", lambda ds: {})
    return mod


def _bg(gt: str, **them) -> dict:
    bg = {"loai": "pmid", "gia_tri": gt, "cac_dashboard": ["A.html"], "xac_minh_luc": _MOI,
          "kiem_rut_luc": _MOI, "ghi_chu_rut": "ok", "tieu_de": "t", "nguon_xac_minh": "pubmed"}
    bg.update(them)
    return bg


def _rut(**them) -> dict:
    """Nhóm phán quyết «đã rút» (mặc định rút bỏ hẳn)."""
    pq = {"da_rut": True, "ghi_chu_rut": "retracted", "rut_va_thay": False}
    pq.update(them)
    return pq


def _dat_so(M, muc: dict) -> None:
    M.SO.write_text(json.dumps({"phien_ban": 1, "muc": muc}, ensure_ascii=False), encoding="utf-8")


def _tren_dia(M) -> dict:
    return json.loads(M.SO.read_text(encoding="utf-8"))["muc"]


# ── (1) ẢNH GỐC phải được làm mới sau mỗi lần ghi — đột biến M4 ─────────────────────────────────────────────────────

def test_xoa_sau_lan_ghi_truoc_khong_hoi_sinh_cung_tien_trinh(M):
    """doc_so → thêm khoá + trường → ghi_so → xoá cả hai → ghi_so ⇒ cả hai KHÔNG còn trên đĩa lẫn trong bộ nhớ."""
    _dat_so(M, {"pmid:1": _bg("1")})
    so = M.doc_so()
    so["muc"]["pmid:2"] = _bg("2")
    so["muc"]["pmid:1"]["tam"] = "x"
    M.ghi_so(so)
    assert "pmid:2" in _tren_dia(M) and _tren_dia(M)["pmid:1"].get("tam") == "x"
    del so["muc"]["pmid:2"]
    del so["muc"]["pmid:1"]["tam"]
    M.ghi_so(so)
    tren = _tren_dia(M)
    assert "pmid:2" not in tren, "bản ghi chính tiến trình này vừa xoá «hồi sinh» từ đĩa — ảnh gốc không được làm mới"
    assert "tam" not in tren["pmid:1"], "trường chính tiến trình này vừa xoá «hồi sinh» từ đĩa"
    assert "pmid:2" not in so["muc"] and "tam" not in so["muc"]["pmid:1"]


_CON_A = r'''
import importlib.util, sys, time
from pathlib import Path
tep, so, thu_muc = sys.argv[1:4]
sp = importlib.util.spec_from_file_location("sxm_con_a", tep)
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)
m.SO = Path(so)
d = Path(thu_muc)
so_mem = m.doc_so()
so_mem["muc"]["pmid:2"] = {"loai": "pmid", "gia_tri": "2", "cac_dashboard": ["A.html"],
                           "xac_minh_luc": "2026-11-14T09:00:00"}
so_mem["muc"]["pmid:1"]["tam"] = "x"
m.ghi_so(so_mem)                     # lần ghi 1: thêm pmid:2 + trường tam
(d / "a_da_ghi_1").touch()
while not (d / "b_xong").exists():   # chờ tiến trình B ghi xen giữa
    time.sleep(0.01)
del so_mem["muc"]["pmid:2"]
del so_mem["muc"]["pmid:1"]["tam"]
m.ghi_so(so_mem)                     # lần ghi 2: xoá cả hai — đĩa đã đổi (B ghi) ⇒ đi đường GỘP
'''

_CON_B = r'''
import importlib.util, sys
from pathlib import Path
tep, so = sys.argv[1:3]
sp = importlib.util.spec_from_file_location("sxm_con_b", tep)
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)
m.SO = Path(so)
so_mem = m.doc_so()
so_mem["muc"]["pmid:3"] = {"loai": "pmid", "gia_tri": "3", "cac_dashboard": ["B.html"],
                           "xac_minh_luc": "2026-11-14T09:00:00"}
m.ghi_so(so_mem)
'''


def test_hai_tien_trinh_ban_ghi_da_xoa_khong_hoi_sinh_khi_tien_trinh_khac_ghi_xen(M, tmp_path):
    """Hai TIẾN TRÌNH thật trên sổ tạm: A ghi (thêm pmid:2 + trường), B ghi xen (thêm pmid:3), A xoá rồi ghi lại.

    Đúng: sổ còn pmid:1 (không có trường đã xoá) + pmid:3; pmid:2 đã bị A xoá. Đột biến M4 (không làm mới ảnh gốc) ⇒ A gộp
    với ảnh gốc CŨ, thấy pmid:2/«tam» là «tiến trình khác thêm» và giữ lại ⇒ hồi sinh."""
    _dat_so(M, {"pmid:1": _bg("1")})
    ka, kb = tmp_path / "con_a.py", tmp_path / "con_b.py"
    ka.write_text(_CON_A, encoding="utf-8")
    kb.write_text(_CON_B, encoding="utf-8")
    pa = subprocess.Popen([sys.executable, "-B", str(ka), str(_TEP), str(M.SO), str(tmp_path)])
    try:
        han = time.monotonic() + 30
        while not (tmp_path / "a_da_ghi_1").exists():
            assert pa.poll() is None, "tiến trình A chết trước lần ghi 1"
            assert time.monotonic() < han, "tiến trình A không ghi lần 1 trong 30 giây"
            time.sleep(0.01)
        assert subprocess.run([sys.executable, "-B", str(kb), str(_TEP), str(M.SO)], timeout=60).returncode == 0
        (tmp_path / "b_xong").touch()
        assert pa.wait(timeout=60) == 0
    finally:
        if pa.poll() is None:
            pa.kill()
    tren = _tren_dia(M)
    assert "pmid:3" in tren, "mất bản ghi tiến trình B ghi xen"
    assert "pmid:2" not in tren, "bản ghi tiến trình A đã xoá «hồi sinh» khi gộp với ghi xen của B (ảnh gốc cũ)"
    assert "tam" not in tren["pmid:1"], "trường tiến trình A đã xoá «hồi sinh» khi gộp với ghi xen của B"
    assert not list(tmp_path.glob("*.tmp"))


# ── (2) Hai bên cùng dương tính: so `kiem_rut_luc`; không biết bên nào mới hơn ⇒ giữ bên nghiêm trọng hơn ───────────────

def _hai_ben(M, *, toi: dict, dia: dict):
    """Cả hai lượt đọc cùng một bản ghi dương tính gốc rồi cùng đổi NHÓM phán quyết; đĩa ghi trước, ta ghi sau (đi gộp)."""
    _dat_so(M, {"pmid:9": _bg("9", **_rut(kiem_rut_luc="2026-11-01T08:00:00", thong_bao_ids=["pmid:goc"]))})
    a, b = M.doc_so(), M.doc_so()
    b["muc"]["pmid:9"].update(dia)
    M.ghi_so(b)
    a["muc"]["pmid:9"].update(toi)
    M.ghi_so(a)
    return _tren_dia(M)["pmid:9"]


def test_rut_va_thay_cu_cua_ta_khong_de_rut_bo_han_moi_tren_dia(M):
    """Ca thẩm định nêu: «rút & thay» (True) CŨ của ta không được hạ «rút bỏ hẳn» (False) MỚI trên đĩa xuống mã 1."""
    bg = _hai_ben(M, toi=_rut(rut_va_thay=True, kiem_rut_luc=_CU, thong_bao_ids=["pmid:cu"]),
                  dia=_rut(rut_va_thay=False, kiem_rut_luc=_MOI, thong_bao_ids=["pmid:moi"]))
    assert bg["rut_va_thay"] is False, "«rút & thay» cũ của ta đè «rút bỏ hẳn» mới trên đĩa"
    assert bg["kiem_rut_luc"] == _MOI and bg["thong_bao_ids"] == ["pmid:moi"], "nhóm phán quyết bị trộn giữa hai lần kiểm"
    assert M._hang_nghiem_trong(bg) == 4


def test_ben_moi_hon_thang_ke_ca_khi_nhe_hon_tinh_chinh_hop_le(M):
    """Lần kiểm SAU (của ta) phát hiện bản sửa đăng lại ⇒ «rút & thay» mới hơn thắng «rút bỏ hẳn» cũ trên đĩa (theo mốc)."""
    bg = _hai_ben(M, toi=_rut(rut_va_thay=True, kiem_rut_luc=_MOI, thong_bao_ids=["pmid:moi"]),
                  dia=_rut(rut_va_thay=False, kiem_rut_luc=_CU, thong_bao_ids=["pmid:cu"]))
    assert bg["rut_va_thay"] is True and bg["kiem_rut_luc"] == _MOI and bg["thong_bao_ids"] == ["pmid:moi"]
    assert bg["da_rut"] is True, "dương tính không bao giờ được rơi mất"


def test_dia_moi_hon_thang_ke_ca_khi_nhe_hon(M):
    """Đối xứng: lần kiểm trên đĩa MỚI hơn và tinh chỉnh thành «rút & thay» ⇒ đĩa thắng (không chỉ «bên nghiêm hơn thắng»)."""
    bg = _hai_ben(M, toi=_rut(rut_va_thay=False, kiem_rut_luc=_CU, thong_bao_ids=["pmid:cu"]),
                  dia=_rut(rut_va_thay=True, kiem_rut_luc=_MOI, thong_bao_ids=["pmid:moi"]))
    assert bg["rut_va_thay"] is True and bg["kiem_rut_luc"] == _MOI and bg["thong_bao_ids"] == ["pmid:moi"]


@pytest.mark.parametrize("moc_toi, moc_dia", [
    (_MOI, _MOI),                         # bằng nhau
    (None, _MOI),                         # ta vắng mốc
    ("không-phải-ngày", _CU),             # ta mốc hỏng
    ("2026-11-14T09:00:00+07:00", _CU),   # có/không múi giờ — không so được
])
def test_khong_biet_ben_nao_moi_hon_thi_giu_ben_nghiem_trong_hon(M, moc_toi, moc_dia):
    toi = _rut(rut_va_thay=True, thong_bao_ids=["pmid:toi"])
    toi["kiem_rut_luc"] = moc_toi
    bg = _hai_ben(M, toi=toi, dia=_rut(rut_va_thay=False, kiem_rut_luc=moc_dia, thong_bao_ids=["pmid:dia"]))
    assert bg["rut_va_thay"] is False, "không xác định được bên mới hơn mà vẫn hạ «rút bỏ hẳn» xuống «rút & thay»"
    assert bg["thong_bao_ids"] == ["pmid:dia"]


def test_khong_biet_ben_nao_moi_hon_ta_nghiem_hon_thi_giu_cua_ta(M):
    bg = _hai_ben(M, toi=_rut(rut_va_thay=False, kiem_rut_luc=_MOI, thong_bao_ids=["pmid:toi"]),
                  dia=_rut(rut_va_thay=True, kiem_rut_luc=_MOI, thong_bao_ids=["pmid:dia"]))
    assert bg["rut_va_thay"] is False and bg["thong_bao_ids"] == ["pmid:toi"]


def test_khong_biet_moc_dinh_chinh_bi_rut_nghiem_hon_rut_va_thay(M):
    """Thứ bậc: rút bỏ hẳn > đính chính bị rút (cổng vẫn chặn) > rút & thay."""
    bg = _hai_ben(M, toi=_rut(rut_va_thay=True, kiem_rut_luc=_MOI),
                  dia=_rut(rut_va_thay=False, sua_loi_bi_rut=True, kiem_rut_luc=_MOI))
    assert bg["rut_va_thay"] is False and bg["sua_loi_bi_rut"] is True


def test_da_rut_thang_eoc_bat_ke_moc(M):
    """Đĩa chỉ EoC nhưng MỚI hơn, ta «đã rút» cũ hơn ⇒ «đã rút» vẫn giữ (bất đối xứng), cờ EoC cũng dính."""
    _dat_so(M, {"pmid:5": _bg("5", quan_ngai=True, ghi_chu_rut="expression_of_concern", kiem_rut_luc=_CU)})
    a, b = M.doc_so(), M.doc_so()
    b["muc"]["pmid:5"].update(kiem_rut_luc=_MOI, ghi_chu_rut="expression_of_concern", thong_bao_ids=["pmid:eoc"])
    M.ghi_so(b)
    a["muc"]["pmid:5"].update(_rut(kiem_rut_luc="2026-11-12T09:00:00", thong_bao_ids=["pmid:rut"]))
    M.ghi_so(a)
    bg = _tren_dia(M)["pmid:5"]
    assert bg.get("da_rut") is True, "«đã rút» cũ hơn bị một lần kiểm chỉ thấy EoC (mới hơn) gỡ mất"
    assert bg["thong_bao_ids"] == ["pmid:rut"] and bg.get("quan_ngai") is True


def test_ham_ben_thang_truc_tiep(M):
    f = M._ben_thang_khi_ca_hai_duong_tinh
    assert f(_rut(kiem_rut_luc=_MOI), _rut(kiem_rut_luc=_CU)) == "toi"
    assert f(_rut(kiem_rut_luc=_CU), _rut(kiem_rut_luc=_MOI)) == "dia"
    assert f(_rut(rut_va_thay=True), _rut()) == "dia"
    assert f({"quan_ngai": True, "kiem_rut_luc": _MOI}, _rut(kiem_rut_luc=_CU)) == "dia"


# ── (3) Dương tính MỚI + hết hạn chờ khoá ⇒ danh sách + [MA] DUONG_TINH_CHUA_VAO_SO, mã 2 ───────────────────────────────

_CON_GIU_KHOA = r'''
import importlib.util, sys, time
from pathlib import Path
tep, so, san_sang = sys.argv[1:4]
sp = importlib.util.spec_from_file_location("sxm_con_giu_khoa_d", tep)
m = importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)
m.SO = Path(so)
with m._KhoaSo():
    Path(san_sang).touch()
    time.sleep(60)
'''


@contextlib.contextmanager
def _tien_trinh_giu_khoa(so: Path, tmp_path: Path):
    kich_ban = tmp_path / "con_giu_khoa.py"
    kich_ban.write_text(_CON_GIU_KHOA, encoding="utf-8")
    san_sang = tmp_path / "da_giu_khoa"
    p = subprocess.Popen([sys.executable, "-B", str(kich_ban), str(_TEP), str(so), str(san_sang)])
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


def test_ghi_so_het_han_khoa_gan_danh_sach_duong_tinh_chua_vao_so(M, tmp_path, monkeypatch):
    _dat_so(M, {"pmid:1": _bg("1"), "pmid:7": _bg("7", **_rut()), "pmid:8": _bg("8", **_rut(rut_va_thay=True))})
    truoc = M.SO.read_bytes()
    so = M.doc_so()
    so["muc"]["pmid:2"] = _bg("2", **_rut())                                    # dương tính MỚI
    so["muc"]["pmid:3"] = _bg("3")                                              # bản ghi mới KHÔNG dương tính
    so["muc"]["pmid:4"] = _bg("4", quan_ngai=True, ghi_chu_rut="expression_of_concern")  # EoC mới
    so["muc"]["pmid:8"]["rut_va_thay"] = False                                  # nâng «rút & thay» → «rút bỏ hẳn»
    monkeypatch.setattr(M, "HAN_CHO_KHOA_GIAY", 0.3)
    with _tien_trinh_giu_khoa(M.SO, tmp_path):
        with pytest.raises(M.SoDangKhoaLoi) as ei:
            M.ghi_so(so)
    ds = dict(ei.value.duong_tinh_chua_vao_so)
    assert set(ds) == {"pmid:2", "pmid:4", "pmid:8"}, "danh sách dương tính chưa vào sổ sai (thừa bản đã có trên đĩa?)"
    assert ds["pmid:2"] == "ĐÃ BỊ RÚT" and ds["pmid:4"] == "EXPRESSION OF CONCERN"
    assert M.SO.read_bytes() == truoc, "ghi khi CHƯA cầm khoá"


def test_cli_duong_tinh_moi_gap_khoa_tra_2_va_in_danh_sach(M, tmp_path, monkeypatch, capsys):
    _dat_so(M, {"pmid:1": _bg("1")})
    truoc = M.SO.read_bytes()
    monkeypatch.setattr(M, "HAN_CHO_KHOA_GIAY", 0.3)
    monkeypatch.setattr(M, "kiem_rut_bai", lambda ds: {p: {"status": "retracted"} for p in ds})
    with _tien_trinh_giu_khoa(M.SO, tmp_path), \
            mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--kiem-rut-lai", "pmid:123"]):
        rc = M.main()
    ra = capsys.readouterr()
    loi = ra.err
    assert "🔴 pmid:123: ĐÃ BỊ RÚT" in ra.out, "phép thử không đi qua nhánh phát hiện dương tính"
    assert rc == 2, "dương tính vừa thấy mà không vào sổ không được ra mã 3 (⚪ «khoá bận»)"
    assert "[MA] DUONG_TINH_CHUA_VAO_SO" in loi and "[MA] SO_DANG_KHOA" in loi
    assert "pmid:123 — ĐÃ BỊ RÚT" in loi, "không in danh sách dương tính chưa vào sổ"
    assert M.SO.read_bytes() == truoc


def test_cli_khoa_khong_co_duong_tinh_moi_van_tra_3(M, tmp_path, monkeypatch, capsys):
    _dat_so(M, {"pmid:1": _bg("1", **_rut())})                               # dương tính CŨ đã có trong sổ
    monkeypatch.setattr(M, "HAN_CHO_KHOA_GIAY", 0.3)
    monkeypatch.setattr(M, "kiem_rut_bai", lambda ds: {p: {"status": "ok"} for p in ds})
    with _tien_trinh_giu_khoa(M.SO, tmp_path), \
            mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--kiem-rut-lai", "pmid:55"]):
        rc = M.main()
    loi = capsys.readouterr().err
    assert rc == 3 and "[MA] SO_DANG_KHOA" in loi
    assert "DUONG_TINH_CHUA_VAO_SO" not in loi, "dương tính đã có trong sổ bị báo là «chưa vào sổ»"


def test_in_loi_khoa_cat_danh_sach_dai(M):
    e = M.SoDangKhoaLoi("khoá bận")
    e.duong_tinh_chua_vao_so = [(f"pmid:{i}", "ĐÃ BỊ RÚT") for i in range(M.TRAN_IN_DUONG_TINH_CHUA_VAO_SO + 7)]
    buf = io.StringIO()
    assert M.in_loi_khoa(e, file=buf) == 2
    out = buf.getvalue()
    assert "… và 7 mục nữa" in out and out.count(" — ĐÃ BỊ RÚT") == M.TRAN_IN_DUONG_TINH_CHUA_VAO_SO


def _chu_trinh(argv: list[str], tra_loi):
    sys.path.insert(0, str(_THU_MUC))
    import chu_trinh_chung_cu as ctcc  # noqa: PLC0415

    class _P:
        def __init__(self, rc, out):
            self.returncode, self.stdout, self.stderr = rc, out, ""

    da_goi: list[list[str]] = []

    def _goi(cmd, **kw):
        cmd = [str(c) for c in cmd]
        da_goi.append(cmd)
        return _P(*tra_loi(cmd))

    with mock.patch.object(sys, "argv", ["chu_trinh_chung_cu.py", *argv]), \
            mock.patch.object(ctcc.subprocess, "run", side_effect=_goi), \
            mock.patch.object(ctcc, "_co_dashboard_that", return_value=True):
        rc = ctcc.main()
    return rc, da_goi


_RA_DUONG_TINH = ("⛔ … khoá ghi …\n🔴 1 dương tính …\n   • pmid:123 — ĐÃ BỊ RÚT\n[MA] DUONG_TINH_CHUA_VAO_SO\n"
                  "[MA] SO_DANG_KHOA — không ghi gì vào sổ\n")


def test_chu_trinh_duong_tinh_chua_vao_so_la_do_khong_phai_trang(capsys):
    def tra_loi(cmd):
        if len(cmd) > 1 and "so_xac_minh_nguon.py" in cmd[1] and "--vong" in cmd and "--quet-ledger" not in cmd \
                and "--phu-mo-coi" not in cmd:
            return 2, _RA_DUONG_TINH
        return 0, ""
    rc, da_goi = _chu_trinh([], tra_loi)
    out = capsys.readouterr().out
    assert rc == 1
    assert "🔴 DƯƠNG TÍNH RÚT BÀI MỚI CHƯA VÀO SỔ" in out, "dương tính mới vướng khoá không được ra ⚪"
    assert "⚪ Sổ xác minh nguồn đang bị" not in out
    assert "CÓ NGUỒN RÚT BỎ HẲN" not in out, "nhánh dương tính chưa vào sổ phải chặn trước nhánh rc=2 chung"
    assert not any("--quet-ledger" in c or "--phu-mo-coi" in c for c in da_goi), \
        "sổ đang khoá mà vẫn chạy ③a/③b (mỗi lệnh lại chờ khoá tới hạn)"


def test_chu_trinh_3a_3b_duong_tinh_chua_vao_so_la_do(capsys):
    def tra_loi(cmd):
        if len(cmd) > 1 and "so_xac_minh_nguon.py" in cmd[1] and "--quet-ledger" in cmd:
            return 2, _RA_DUONG_TINH
        return 0, ""
    rc, _ = _chu_trinh([], tra_loi)
    out = capsys.readouterr().out
    assert rc == 1
    assert "🔴 Bước ③a/③b thấy DƯƠNG TÍNH" in out
    assert "⚪ Bước ③a/③b không ghi được" not in out


# ── (4) Cầu NC⇄LS và orchestrator nhận mã SO_DANG_KHOA ───────────────────────────────────────────────────────────────

@pytest.fixture()
def cau(M, tmp_path, monkeypatch):
    """Cầu NC⇄LS với exports/ tạm (một đề tài giả), sổ tạm của M, chuỗi rút bài KHÔNG nạp được (không gọi mạng)."""
    c = _nap("cau_noi_tiep_20261114d", _THU_MUC / "cau_noi_nghien_cuu_lam_sang.py")
    exports = tmp_path / "exports"
    (exports / "de-tai-gia").mkdir(parents=True)
    (exports / "de-tai-gia" / "DE_CUONG.md").write_text("Nền: PMID: 12345678\n", encoding="utf-8")
    monkeypatch.setattr(c, "EXPORTS", exports)
    monkeypatch.setattr(c, "_nap", lambda ten, duong: M)
    # `from app.sources.retraction_chain import …` ⇒ ImportError ⇒ «chưa kiểm», KHÔNG gọi mạng — chặn CẢ tên đầy đủ: một test
    # khác trong cùng lượt có thể đã nạp module thật, và import tên đầy đủ có trong sys.modules thì không xét gói cha.
    for ten in ("app", "app.sources", "app.sources.retraction_chain"):
        monkeypatch.setitem(sys.modules, ten, None)
    return c


def test_cau_noi_so_dang_khoa_khong_traceback_tra_3(cau, M, tmp_path, monkeypatch, capsys):
    _dat_so(M, {"pmid:1": _bg("1")})
    truoc = M.SO.read_bytes()
    monkeypatch.setattr(M, "HAN_CHO_KHOA_GIAY", 0.3)
    with _tien_trinh_giu_khoa(M.SO, tmp_path), mock.patch.object(sys, "argv", ["cau_noi_nghien_cuu_lam_sang.py"]):
        rc = cau.main()  # bản cũ: SoDangKhoaLoi thoát ra ngoài ⇒ test ĐỎ bằng traceback
    out = capsys.readouterr().out
    assert rc == 3, "sổ khoá phải ra mã riêng (3), không phải 0 (chạy trọn) hay traceback"
    assert "[MA] SO_DANG_KHOA" in out and "Sổ đang khoá — chạy lại sau" in out
    assert "Đã ghi sổ xác minh" not in out, "xanh giả: báo đã ghi trong khi khoá chặn"
    assert M.SO.read_bytes() == truoc
    assert not list((tmp_path / "exports" / "de-tai-gia").glob("CANH-BAO-*")), "chuỗi giả không được sinh cảnh báo"


def test_cau_noi_chay_binh_thuong_van_ghi_lien_ket(cau, M, capsys):
    _dat_so(M, {"pmid:1": _bg("1")})
    with mock.patch.object(sys, "argv", ["cau_noi_nghien_cuu_lam_sang.py"]):
        assert cau.main() == 0
    assert _tren_dia(M)["pmid:12345678"]["cac_dashboard"] == ["NC:de-tai-gia"]
    assert "Đã ghi sổ xác minh" in capsys.readouterr().out


def test_cau_noi_so_hong_khong_traceback_tra_2(cau, M, capsys):
    hong = b'{"phien_ban": 1, "muc": {"pmid:1": {"lo'
    M.SO.write_bytes(hong)
    with mock.patch.object(sys, "argv", ["cau_noi_nghien_cuu_lam_sang.py"]):
        rc = cau.main()
    assert rc == 2 and "[MA] SO_HONG" in capsys.readouterr().out
    assert M.SO.read_bytes() == hong


@pytest.fixture()
def op():
    return _nap("orch_tiep_20261114d", _GOC / "ops" / "orchestrator.py")


def test_orchestrator_a4_ma_3_la_so_dang_khoa_khong_phai_so_chua_du(op):
    muc, msg = op.phan_loai("A4-so-xac-minh[X]", 3)
    assert muc == "so_dang_khoa" and "SO_DANG_KHOA" in msg and "chạy lại" in msg
    assert "chưa đủ" not in msg
    assert muc not in op.DUNG_HET, "sổ khoá ở A4 không được dừng cả lô"
    assert op.phan_loai("A4-so-xac-minh[X]", 1)[0] == "noi_dung"
    assert op.phan_loai("A4-so-xac-minh[X]", 2)[0] == "rut"


def test_orchestrator_thuc_thi_a4_khoa_di_tiep_khong_xanh_va_vao_phieu(op):
    ke = [{"buoc": "A4-so-xac-minh[X]", "lat": "X", "lenh": ["py", "a4x"]},
          {"buoc": "B2-cong-liem-chinh[X]", "lat": "X", "lenh": ["py", "b2x"]},
          {"buoc": "B5-hang-cho-bac-si", "lenh": ["py", "b5"]}]
    da_chay: list[str] = []

    def chay(lenh, _t):
        da_chay.append(lenh[1])
        return 3 if lenh[1] == "a4x" else 0
    res = op.thuc_thi(ke, chay=chay, in_=lambda *_: None)
    assert da_chay == ["a4x", "b2x", "b5"], "A4 vướng khoá không được dừng lô"
    assert res["tong_rc"] == 1, "sổ khoá không được ra 🟢 (mã 0)"
    assert res["so_dang_khoa"] == ["X"] and res["ket_qua"]["A4-so-xac-minh[X]"] == ("so_dang_khoa", 3)
    for tt in ({"loai": "watchlist", "a2_arg": "W"}, {"loai": "khong_can"}):
        viec = op.phieu_can_phien("x", tt, [], res, frozenset())
        assert any("SO_DANG_KHOA" in v and "--resume" in v for v in viec), f"phiếu không nói sổ đang khoá ({tt['loai']})"


def test_hop_dong_ma_thoat_cli_so_voi_orchestrator(M, op, tmp_path, monkeypatch, capsys):
    """Mã thoát THẬT của CLI sổ khi vướng khoá ⇒ orchestrator xếp đúng nhãn (3 → so_dang_khoa, 2 → rut)."""
    _dat_so(M, {"pmid:1": _bg("1")})
    monkeypatch.setattr(M, "HAN_CHO_KHOA_GIAY", 0.3)
    with _tien_trinh_giu_khoa(M.SO, tmp_path):
        monkeypatch.setattr(M, "kiem_rut_bai", lambda ds: {p: {"status": "ok"} for p in ds})
        with mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--kiem-rut-lai", "pmid:5"]):
            rc_khoa = M.main()
        monkeypatch.setattr(M, "kiem_rut_bai", lambda ds: {p: {"status": "retracted"} for p in ds})
        with mock.patch.object(sys, "argv", ["so_xac_minh_nguon.py", "--kiem-rut-lai", "pmid:6"]):
            rc_duong = M.main()
    capsys.readouterr()
    assert op.phan_loai("A4-so-xac-minh[X]", rc_khoa)[0] == "so_dang_khoa"
    assert op.phan_loai("A4-so-xac-minh[X]", rc_duong)[0] == "rut"
