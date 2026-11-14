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
from pathlib import Path

import pytest

_TEP = Path(__file__).resolve().parent / "tu_de_xuat_viec.py"
_sp = importlib.util.spec_from_file_location("tu_de_xuat_viec_binh_duyet", _TEP)
M = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(M)

MA = "de-tai-that-X1"
G10_LUC = "2026-10-28T19:19:08.041909"  # mốc lắp G10 thật của C1a (G10_checkpoint.generated_at)
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


def _de_tai(exports: Path, ma: str = MA, *, g10: str | None = G10_LUC, meta: dict | str | None = None,
            nop: str | None = NOI_DUNG_NOP, tn: str | None = NOI_DUNG_TN, sua_sau_g10: bool = False,
            trong_manifest: bool = True) -> Path:
    """Dựng một thư mục đề tài: tệp gói + G10_checkpoint.json mang manifest băm ĐÚNG nội dung lúc lắp."""
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
              "release_manifest": {"algorithm": "SHA-256", "files": files}}
        (d / "G10_checkpoint.json").write_text(json.dumps(ck), encoding="utf-8", newline="\n")
    return d


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


def test_de_tai_synthetic_test_bo_qua(tmp_path):
    _de_tai(tmp_path, meta={"study_kind": "synthetic_test"})
    assert M.giac_quan_binh_duyet_doc_lap(tmp_path) == [] and M._GIAC_QUAN_CHET == []


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
