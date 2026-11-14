"""Cảm biến «bình duyệt độc lập trước mốc nộp/khoá» của `tu_de_xuat_viec.py` — 14/11/2026.

Bài học 29/10/2026: một agent `binh-duyet` tìm 4 lỗi 🔴 + 10 🟠 trong gói nộp Hội đồng của C1a mà mọi cổng máy đều cho
qua; bác sĩ duyệt cố định bước bình duyệt độc lập trước mốc nộp/khoá. Cảm biến báo 🛎 khi gói G10 đổi SAU bản bình duyệt
mới nhất (hoặc đã lắp G10 mà chưa có bản nào), so theo NỘI DUNG (băm + mốc ghi trong tệp), không theo mtime.
Ngoại tuyến, chỉ dùng thư mục tạm — không đọc exports/ thật.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import unicodedata
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_binh_duyet", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

MA = "de-tai-that-X1"
G10_LUC = "2026-10-28T19:19:08.041909"  # mốc lắp G10 thật của C1a (G10_checkpoint.generated_at, giờ máy VN không múi)
CHAM_LUC = "2026-10-28T13:51:46.967735+00:00"  # lượt chấm G10 thật của C1a (G10_QUALITY_REPORT.generated_at = 20:51 giờ VN)
NOI_DUNG_NOP = "# Đề cương nộp Hội đồng\nN = 1.000\n"
NOI_DUNG_TN = "# Đề cương thống nhất\n18 mục\n"


@pytest.fixture(autouse=True)
def _reset():
    M._GIAC_QUAN_CHET.clear()
    M._SO_GIAC_QUAN["chay"] = 0
    yield
    M._GIAC_QUAN_CHET.clear()


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _goi(files: dict) -> str:
    """package_sha256 đúng thuật toán `g10_quality_gate._manifest`."""
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _ghi_bao_cao(d: Path, goi: str, cham: str) -> None:
    (d / "G10_QUALITY_REPORT.json").write_text(
        json.dumps({"kind": "g10_quality_report", "generated_at": cham, "package_sha256": goi}),
        encoding="utf-8", newline="\n")


def _cham_lai(d: Path, cham: str) -> None:
    """Mô phỏng `g10_quality_gate.py` (ghi, G10 CHƯA ký): băm lại gói hiện hành vào release_manifest, GIỮ NGUYÊN
    generated_at (PF.ghi_checkpoint_giu_moc_sinh) và ghi G10_QUALITY_REPORT.json mang package_sha256 mới."""
    tep_ck = d / "G10_checkpoint.json"
    ck = json.loads(tep_ck.read_text(encoding="utf-8"))
    files = {k: {"path": v["path"], "sha256": hashlib.sha256((d / v["path"]).read_bytes()).hexdigest()}
             for k, v in ck["release_manifest"]["files"].items()}
    ck["release_manifest"] = {"algorithm": "SHA-256", "files": files, "package_sha256": _goi(files)}
    tep_ck.write_text(json.dumps(ck), encoding="utf-8", newline="\n")
    _ghi_bao_cao(d, _goi(files), cham)


def _de_tai(exports: Path, ma: str = MA, *, g10: str | None = G10_LUC, meta: dict | str | None = None,
            nop: str | None = NOI_DUNG_NOP, tn: str | None = NOI_DUNG_TN, sua_sau_g10: bool = False,
            trong_manifest: bool = True, cham: str | None = CHAM_LUC) -> Path:
    """Dựng một thư mục đề tài: tệp gói + G10_checkpoint.json mang manifest băm ĐÚNG nội dung lúc lắp + (mặc định)
    G10_QUALITY_REPORT.json của lượt chấm ghi manifest đó — đúng dòng chảy thật (bộ lắp gọi bộ chấm ngay sau khi lắp)."""
    d = exports / ma
    d.mkdir(parents=True)
    meta_txt = meta if isinstance(meta, str) else json.dumps(meta or {"topic": "x"}, ensure_ascii=False)
    (d / "study_meta.json").write_text(meta_txt, encoding="utf-8", newline="\n")
    tep = {}
    if nop is not None:
        tep["irb_protocol_md"] = (f"DE_CUONG_NOP_HOI_DONG_{ma}.md", nop)
    if tn is not None:
        tep["final_protocol_md"] = (f"DE_CUONG_THONG_NHAT_{ma}.md", tn)
    for ten, nd in tep.values():
        (d / ten).write_text(nd + ("\nSửa sau khi lắp G10.\n" if sua_sau_g10 else ""), encoding="utf-8", newline="\n")
    if g10 is not None:
        files = {k: {"path": ten, "sha256": _sha(nd)} for k, (ten, nd) in tep.items()} if trong_manifest else {}
        ck = {"gate": "G10", "study": ma, "generated_at": g10,
              "release_manifest": {"algorithm": "SHA-256", "files": files, "package_sha256": _goi(files)}}
        (d / "G10_checkpoint.json").write_text(json.dumps(ck), encoding="utf-8", newline="\n")
        if cham is not None:
            _ghi_bao_cao(d, _goi(files), cham)
    return d


def _gate_contract(goc: Path, noi_dung: str) -> Path:
    """`<goc>/tools/gate_contract.py` giả — đúng chỗ mặc định cảm biến tìm (`<exports>/../tools/gate_contract.py`)."""
    p = goc / "tools" / "gate_contract.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(noi_dung, encoding="utf-8", newline="\n")
    return p


def _denylist(*ten: str) -> str:
    """Khuôn giống gate_contract thật: chú thích, AnnAssign `frozenset({...})`, hàm phía sau."""
    dong = "".join(f"    {t!r},\n    # chú thích giữa các mục\n" for t in ten)
    return ("import unicodedata\n\n# Danh sách đề tài THẬT\nREAL_STUDY_DENYLIST: frozenset = frozenset({\n" + dong
            + "})\n\n\ndef is_real_study_denylisted(study):\n    return False\n")


def _binh_duyet(d: Path, ngay: str | None = "20261029", noi_dung: str = "> Bình duyệt độc lập.\n# Báo cáo\n",
                ten: str | None = None) -> Path:
    if ten is None:
        ten = f"PHAN_BIEN_DE_CUONG_NOP_{ngay}_{d.name}.md" if ngay else f"PHAN_BIEN_DE_CUONG_NOP_{d.name}.md"
    p = d / ten
    p.write_text(noi_dung, encoding="utf-8", newline="\n")
    return p


# ── chưa tới G10 / không phải đề tài thật ⇒ không báo ──────────────────────────────────────────────────────────────────

def test_chua_lap_g10_khong_bao_khong_chet(tmp_path):
    _de_tai(tmp_path, g10=None)
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert M._GIAC_QUAN_CHET == [] and M._SO_GIAC_QUAN["chay"] == 1


def test_de_tai_synthetic_test_ngoai_danh_sach_that_bo_qua(tmp_path):
    _gate_contract(tmp_path, _denylist("hai-long-benh-nhan-C1a-BVQY175", "KKB-HAI-LONG-2026"))
    _de_tai(tmp_path / "exports", meta={"study_kind": "synthetic_test"})
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path / "exports") == [] and M._GIAC_QUAN_CHET == []


def test_thu_muc_he_thong_va_thu_muc_khong_study_meta_bo_qua(tmp_path):
    _de_tai(tmp_path, ma="phase_2b")              # thư mục hệ thống dù có study_meta + G10
    (tmp_path / "chatgpt_project").mkdir()
    (tmp_path / "rac").mkdir()                    # không study_meta ⇒ không phải đề tài
    (tmp_path / "rac" / "G10_checkpoint.json").write_text("{}", encoding="utf-8", newline="\n")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == [] and M._GIAC_QUAN_CHET == []


def test_vang_exports_la_giac_quan_chet(tmp_path):
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path / "khong-co") == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "exports" in M._GIAC_QUAN_CHET[0]


# ── đã lắp G10 ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def test_lap_g10_chua_co_binh_duyet_nao_bao_chuong(tmp_path):
    _de_tai(tmp_path)
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and kq[0][0] == 1
    assert f"Đề tài {MA}" in kq[0][1] and "CHƯA có bản bình duyệt độc lập" in kq[0][1] and "0,4 triệu token" in kq[0][1]
    assert f"--van-tay-goi {MA}" in kq[0][2] and "binh-duyet" in kq[0][2]


def test_ca_that_c1a_binh_duyet_sau_ngay_lap_g10_la_da_phu(tmp_path):
    # C1a 14/11/2026: G10 lắp 28/10 19:19, gói khớp manifest, bình duyệt 29/10 ⇒ không còn việc.
    d = _de_tai(tmp_path)
    _binh_duyet(d, "20261029")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == [] and M._GIAC_QUAN_CHET == []


def test_g10_lap_lai_sau_binh_duyet_bao_chuong(tmp_path):
    d = _de_tai(tmp_path)
    _binh_duyet(d, "20261025")
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and "gói nộp đổi sau lần bình duyệt độc lập gần nhất" in kq[0][1]
    assert "25/10/2026" in kq[0][1] and "28/10/2026" in kq[0][1]
    assert M._GIAC_QUAN_CHET == []


def test_lay_ban_binh_duyet_moi_nhat(tmp_path):
    d = _de_tai(tmp_path)
    _binh_duyet(d, "20261020")
    _binh_duyet(d, "20261030", ten=f"PHAN_BIEN_DE_CUONG_20261030_{MA}.md")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == [] and M._GIAC_QUAN_CHET == []


def test_cung_ngay_lap_g10_khong_do_duoc(tmp_path):
    d = _de_tai(tmp_path)
    _binh_duyet(d, "20261028")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "cùng ngày" in M._GIAC_QUAN_CHET[0] and "--van-tay-goi" in M._GIAC_QUAN_CHET[0]


def test_sua_goi_sau_g10_ma_binh_duyet_truoc_g10_bao_chuong(tmp_path):
    d = _de_tai(tmp_path, sua_sau_g10=True)
    _binh_duyet(d, "20261020")
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and "sửa sau G10" in kq[0][1]


def test_sua_goi_sau_g10_ma_binh_duyet_sau_g10_khong_do_duoc(tmp_path):
    # Tệp lệch manifest ⇒ đã sửa SAU lúc lắp, nhưng không có mốc nội dung để biết trước hay sau bình duyệt 30/10.
    d = _de_tai(tmp_path, sua_sau_g10=True)
    _binh_duyet(d, "20261030")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "lệch manifest G10" in M._GIAC_QUAN_CHET[0]


def test_tep_goi_khong_co_trong_manifest_khong_do_duoc(tmp_path):
    d = _de_tai(tmp_path, trong_manifest=False)
    _binh_duyet(d, "20261030")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "không có trong manifest" in M._GIAC_QUAN_CHET[0]


# ── bằng chứng NỘI DUNG: bản bình duyệt ghi sha256 gói ─────────────────────────────────────────────────────────────────

def test_ban_binh_duyet_ghi_du_sha256_goi_hien_hanh_la_da_phu_du_ngay_cu(tmp_path):
    d = _de_tai(tmp_path, sua_sau_g10=True)
    bam = M.van_tay_goi(d)
    _binh_duyet(d, "20261020", noi_dung="# Báo cáo\n" + "".join(f"sha256 {h}  {t}\n" for t, h in bam.items()))
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == [] and M._GIAC_QUAN_CHET == []


def test_chi_ghi_sha256_mot_tep_khong_du_lui_ve_so_ngay(tmp_path):
    d = _de_tai(tmp_path)
    mot = M.van_tay_goi(d)[f"DE_CUONG_NOP_HOI_DONG_{MA}.md"]
    _binh_duyet(d, "20261020", noi_dung=f"# Báo cáo\nsha256 {mot}\n")
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and "gói nộp đổi sau" in kq[0][1]


def test_sha256_cu_cua_goi_da_sua_khong_phai_bang_chung(tmp_path):
    d = _de_tai(tmp_path, sua_sau_g10=True)
    cu = "".join(f"sha256 {_sha(nd)}\n" for nd in (NOI_DUNG_NOP, NOI_DUNG_TN))  # băm LÚC LẮP, gói nay đã sửa
    _binh_duyet(d, "20261020", noi_dung="# Báo cáo\n" + cu)
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and "sửa sau G10" in kq[0][1]


# ── ngày bình duyệt: chỉ từ tên/nội dung tệp, không bao giờ từ mtime ───────────────────────────────────────────────────

def test_mtime_khong_anh_huong_phan_quyet(tmp_path):
    d = _de_tai(tmp_path)
    p = _binh_duyet(d, "20261029")
    os.utime(p, (0, 0))                                        # mtime 1970 — OneDrive trôi
    os.utime(d / "G10_checkpoint.json", (4_000_000_000, 4_000_000_000))
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == [] and M._GIAC_QUAN_CHET == []


def test_bao_cao_g8_co_dong_ngay_duoc_tinh(tmp_path):
    d = _de_tai(tmp_path)
    _binh_duyet(d, ten=f"G8_PEER_REVIEW_REPORT_{MA}.md", noi_dung="# Báo cáo phản biện\n**Ngày:** 30/10/2026\n")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == [] and M._GIAC_QUAN_CHET == []


def test_ngay_trong_dong_dau_khi_ten_khong_mang_ngay(tmp_path):
    d = _de_tai(tmp_path)
    _binh_duyet(d, None, noi_dung="> Bình duyệt độc lập ngày 25/10/2026 do một agent.\n# Báo cáo\n")
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and "25/10/2026" in kq[0][1]


def test_ban_khong_dinh_duoc_ngay_la_khong_do_duoc(tmp_path):
    d = _de_tai(tmp_path)
    _binh_duyet(d, ten=f"G8_PEER_REVIEW_REPORT_{MA}.md", noi_dung="# Báo cáo phản biện\nkhông ghi ngày\n")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "không định được ngày" in M._GIAC_QUAN_CHET[0]


def test_ban_khong_ngay_canh_ban_cu_khong_ket_luan_doi_sau(tmp_path):
    # Bản cũ 20/10 chứng minh «đổi sau» — nhưng bản G8 không ngày có thể MỚI hơn gói ⇒ chỉ «không đo được».
    d = _de_tai(tmp_path)
    _binh_duyet(d, "20261020")
    _binh_duyet(d, ten=f"G8_PEER_REVIEW_REPORT_{MA}.md", noi_dung="# Báo cáo phản biện\n")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "có thể mới hơn gói" in M._GIAC_QUAN_CHET[0]


def test_phan_hoi_va_quyet_dinh_cua_tac_gia_khong_phai_ban_binh_duyet(tmp_path):
    d = _de_tai(tmp_path)
    _binh_duyet(d, ten="PHAN-HOI-BINH-DUYET_X1.md", noi_dung="Bình duyệt ngày 30/10/2026\n")
    _binh_duyet(d, ten="QUYET-DINH-BINH-DUYET_X1.md", noi_dung="Bình duyệt ngày 30/10/2026\n")
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and "CHƯA có bản bình duyệt độc lập" in kq[0][1]


# ── hỏng / thiếu ⇒ ⚪, không bao giờ «ổn» ────────────────────────────────────────────────────────────────────────────

def test_g10_thieu_generated_at_co_binh_duyet_la_khong_do_duoc(tmp_path):
    d = _de_tai(tmp_path, g10="")
    _binh_duyet(d, "20261029")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "generated_at" in M._GIAC_QUAN_CHET[0]


def test_g10_hong_ma_chua_binh_duyet_van_bao_chuong(tmp_path):
    d = _de_tai(tmp_path)
    (d / "G10_checkpoint.json").write_text("{hỏng", encoding="utf-8", newline="\n")
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and "CHƯA có bản bình duyệt độc lập" in kq[0][1]


def test_study_meta_hong_khi_da_lap_g10_la_khong_do_duoc(tmp_path):
    _de_tai(tmp_path, meta="{hỏng")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "study_meta" in M._GIAC_QUAN_CHET[0]


def test_lap_g10_ma_khong_thay_tep_goi_la_khong_do_duoc(tmp_path):
    _de_tai(tmp_path, nop=None, tn=None)
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "không thấy" in M._GIAC_QUAN_CHET[0]


def test_hai_de_tai_doc_lap_nhau(tmp_path):
    d1 = _de_tai(tmp_path, ma="de-tai-A")
    _binh_duyet(d1, "20261029")
    _de_tai(tmp_path, ma="de-tai-B")
    _de_tai(tmp_path, ma="de-tai-C", g10=None)
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert [x[1].split(":")[0] for x in kq] == ["Đề tài de-tai-B"] and M._GIAC_QUAN_CHET == []


# ── nối dây: main() thật sự GỌI cảm biến với exports của repo y khoa, nhãn 🛎 ────────────────────────────────────────────

def test_main_goi_cam_bien_voi_exports_y_khoa_va_nhan_chuong():
    cay = ast.parse(_TEP.read_text(encoding="utf-8"))
    main = next(n for n in cay.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    vong = [n for n in ast.walk(main) if isinstance(n, ast.For) and isinstance(n.iter, ast.Call)
            and getattr(n.iter.func, "id", "") == "giac_quan_binh_duyet_doc_lap"]
    assert len(vong) == 1, "main() phải lặp trên kết quả giac_quan_binh_duyet_doc_lap(...)"
    assert "exports" in ast.unparse(vong[0].iter.args[0])
    assert "🛎" in ast.unparse(vong[0])


def test_van_tay_goi_cli(tmp_path, monkeypatch, capsys):
    d = _de_tai(tmp_path / "exports")
    monkeypatch.setattr(M, "_GOC_MEA", tmp_path)
    monkeypatch.setattr("sys.argv", ["tu_de_xuat_viec.py", "--van-tay-goi", MA])
    assert M.main() == 0
    ra = capsys.readouterr().out
    for ten, h in M.van_tay_goi(d).items():
        assert f"sha256 {h}  {ten}" in ra
    monkeypatch.setattr("sys.argv", ["tu_de_xuat_viec.py", "--van-tay-goi", "../ngoai"])
    assert M.main() == 2


# ── manifest G10 bị bộ chấm GHI ĐÈ mà giữ generated_at (người duyệt PR #337, 14/11/2026) ─────────────────────────────────

def test_manifest_lam_moi_sau_binh_duyet_giu_generated_at_khong_bao_gio_ok(tmp_path):
    # Tái hiện của người duyệt: lắp 28/10, bình duyệt 29/10, SỬA gói 31/10 rồi chấm lại G10 (G10-AUTO-10 dặn «trước ký: chạy
    # lại g10_quality_gate.py») ⇒ manifest khớp gói đã sửa mà generated_at vẫn 28/10. Bản đầu trả ('ok','') — xanh giả.
    d = _de_tai(tmp_path)
    _binh_duyet(d, "20261029")
    nop = d / f"DE_CUONG_NOP_HOI_DONG_{MA}.md"
    nop.write_text(NOI_DUNG_NOP + "\nSửa 31/10 sau bình duyệt.\n", encoding="utf-8", newline="\n")
    _cham_lai(d, "2026-10-31T03:00:00+00:00")
    ck = json.loads((d / "G10_checkpoint.json").read_text(encoding="utf-8"))
    assert ck["generated_at"] == G10_LUC                                       # tự kiểm: mốc lắp GIỮ NGUYÊN
    assert ck["release_manifest"]["files"]["irb_protocol_md"]["sha256"] == M.van_tay_goi(d)[nop.name]  # và tệp KHỚP manifest
    assert M.xet_binh_duyet_de_tai(d)[0] != "ok"
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1
    assert "chấm lại 31/10/2026 sau bình duyệt 29/10/2026" in M._GIAC_QUAN_CHET[0] and "--van-tay-goi" in M._GIAC_QUAN_CHET[0]


@pytest.mark.parametrize("hong", ["vang", "goi_lech", "gio_khong_mui", "json_hong"])
def test_khong_rang_buoc_duoc_bao_cao_voi_manifest_la_khong_do_duoc(tmp_path, hong):
    # Tệp khớp manifest + bình duyệt sau ngày lắp, nhưng không neo được lúc manifest được viết ⇒ ⚪, không «ổn».
    d = _de_tai(tmp_path)
    _binh_duyet(d, "20261029")
    bc = d / "G10_QUALITY_REPORT.json"
    if hong == "vang":
        bc.unlink()
    elif hong == "goi_lech":      # vd báo cáo của lượt chấm SAU KÝ thấy gói khác (lượt đó không ghi manifest)
        _ghi_bao_cao(d, "0" * 64, "2026-10-28T13:51:46+00:00")
    elif hong == "gio_khong_mui":  # không biết giờ UTC hay giờ VN ⇒ không lấy làm cận trên
        _ghi_bao_cao(d, json.loads((d / "G10_checkpoint.json").read_text(encoding="utf-8"))
                     ["release_manifest"]["package_sha256"], "2026-10-28T13:51:46")
    else:
        bc.write_text("{hỏng", encoding="utf-8", newline="\n")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "không ràng buộc được G10_QUALITY_REPORT" in M._GIAC_QUAN_CHET[0]


def test_moc_cham_utc_quy_ve_gio_vn_truoc_khi_lay_ngay(tmp_path):
    # 28/10 18:30Z = 29/10 01:30 giờ VN ⇒ cùng ngày bình duyệt 29/10 ⇒ ⚪. Lấy .date() của giờ UTC (28/10) sẽ ra «ổn» giả.
    d = _de_tai(tmp_path, cham="2026-10-28T18:30:00+00:00")
    _binh_duyet(d, "20261029")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "cùng ngày 29/10/2026" in M._GIAC_QUAN_CHET[0]


def test_sua_goi_sau_lan_cham_lai_ma_lan_cham_sau_binh_duyet_bao_chuong(tmp_path):
    # Lắp 28/10, bình duyệt 29/10, chấm lại 31/10 (gói chưa đổi), rồi SỬA gói ⇒ tệp lệch manifest mà lượt chấm 31/10 còn thấy
    # gói đúng manifest ⇒ chắc chắn sửa sau 31/10 > 29/10 ⇒ 🛎 (bản đầu chỉ biết mốc 28/10 ⇒ ⚪).
    d = _de_tai(tmp_path)
    _binh_duyet(d, "20261029")
    _cham_lai(d, "2026-10-31T03:00:00+00:00")
    (d / f"DE_CUONG_THONG_NHAT_{MA}.md").write_text(NOI_DUNG_TN + "\nSửa sau lần chấm 31/10.\n", encoding="utf-8",
                                                    newline="\n")
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path)
    assert len(kq) == 1 and f"DE_CUONG_THONG_NHAT_{MA}.md sửa sau G10 31/10/2026" in kq[0][1]
    assert M._GIAC_QUAN_CHET == []


# ── ngày bình duyệt chỉ lấy ở PHẦN ĐẦU nội dung (1.500 ký tự) ───────────────────────────────────────────────────────────

def test_ngay_o_than_bai_sau_1500_ky_tu_khong_phai_ngay_binh_duyet(tmp_path):
    # Thân bài nhắc ngày của sự kiện KHÁC (vòng phản biện trước, ngày ký…) — không được coi là ngày bình duyệt.
    d = _de_tai(tmp_path)
    noi_dung = ("> Báo cáo bình duyệt độc lập (không ghi ngày ở đầu).\n# Báo cáo\n" + "Nhận xét chi tiết.\n" * 120
                + "Theo phản biện vòng trước ngày 30/10/2026, mục 4 đã sửa.\nNgày: 30/10/2026\n")
    assert len(noi_dung) > 1600 and "30/10/2026" not in noi_dung[:1500]   # tự kiểm fixture
    _binh_duyet(d, None, noi_dung=noi_dung)
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "không định được ngày" in M._GIAC_QUAN_CHET[0]


# ── đề tài thật theo HAI lớp của repo y khoa: study_kind + REAL_STUDY_DENYLIST ─────────────────────────────────────────

_MA_DAU = "khảo-sát-thật-Y2"


@pytest.mark.parametrize("ma,ten_trong_danh_sach", [
    (MA, f"  {MA.upper()}  "),                                  # khác hoa/thường + khoảng trắng
    (_MA_DAU, unicodedata.normalize("NFD", _MA_DAU)),           # cùng chữ, khác dạng tổ hợp Unicode
])
def test_synthetic_trong_danh_sach_that_van_do_nhu_de_tai_that(tmp_path, ma, ten_trong_danh_sach):
    # Lỗi chép study_meta giữa các đề tài: đề tài THẬT mang nhầm study_kind=synthetic_test ⇒ vẫn đo, kèm cảnh báo cờ.
    _gate_contract(tmp_path, _denylist("de-tai-khac", ten_trong_danh_sach))
    _de_tai(tmp_path / "exports", ma=unicodedata.normalize("NFC", ma), meta={"study_kind": "synthetic_test"})
    kq = M.giac_quan_binh_duyet_doc_lap(tmp_path / "exports")
    assert len(kq) == 1 and "CHƯA có bản bình duyệt độc lập" in kq[0][1]
    assert "REAL_STUDY_DENYLIST" in kq[0][1] and "cờ đặt nhầm" in kq[0][1]


def test_synthetic_trong_danh_sach_that_da_binh_duyet_van_hien_canh_bao(tmp_path):
    _gate_contract(tmp_path, _denylist(MA))
    d = _de_tai(tmp_path / "exports", meta={"study_kind": "synthetic_test"})
    _binh_duyet(d, "20261029")
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path / "exports") == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "REAL_STUDY_DENYLIST" in M._GIAC_QUAN_CHET[0]


@pytest.mark.parametrize("gate_contract", [None, "def f(:\n", "X = 1\n", "REAL_STUDY_DENYLIST: frozenset = frozenset()\n"])
def test_synthetic_khi_khong_doc_duoc_danh_sach_that_la_khong_do_duoc(tmp_path, gate_contract):
    if gate_contract is not None:
        _gate_contract(tmp_path, gate_contract)
    _de_tai(tmp_path / "exports", meta={"study_kind": "synthetic_test"})
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path / "exports") == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "không đọc được REAL_STUDY_DENYLIST" in M._GIAC_QUAN_CHET[0]


def test_doc_danh_sach_that_tu_gate_contract_that_cua_repo_y_khoa():
    # Bộ đọc ast phải hiểu đúng khuôn tệp THẬT (AnnAssign + frozenset({...}) + chú thích). Vắng repo y khoa (Cloud/CI) ⇒ bỏ.
    tep = M._GOC_MEA / "tools" / "gate_contract.py"
    if not tep.is_file():
        pytest.skip("không có medical-ebm-automation/tools/gate_contract.py ở cây này")
    ds = M.doc_danh_sach_de_tai_that(tep)
    assert ds is not None and "hai-long-benh-nhan-c1a-bvqy175" in ds
