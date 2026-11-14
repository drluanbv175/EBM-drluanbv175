"""Dọn mức thấp lịch nền (14/11/2026, việc I sau tầng 3 — bác sĩ «Tiếp tục» ~14:50).

Khoá bốn lỗ đo được trên mã sống:
  (1) `kiem_lich_nen` tính MỌI dòng KẾT THÚC trong hạn là kỳ đúng hẹn, không đọc «(mã N)» ⇒ lượt ghi «KẾT THÚC (mã 2)» (dừng
      giữa chừng, mảng không đo được, nguồn giả) hiện xanh. Nay: mã ∈ `MA_TRON` (0/1) hoặc «tổng thể=PASS» ⇒ trọn; mã khác hoặc
      «tổng thể=CÓ BƯỚC LỖI» ⇒ 🟠 «lượt không trọn»; không đọc được mã ⇒ ⚪.
  (2) `tu_de_xuat_viec` giác quan ⑦f-bis (quyền lượt lịch) IM khi `quyen_lich_nen.kiem()` trả `khong_do` ⇒ nay ⚪ giác quan chết.
  (4) SKILL tác vụ rút bài ngày 4 `kiem-rut-bai-kho-thang` chưa có bước 0 tiền kiểm quyền như hai tác vụ tháng kia.
  (5) Quy ước soạn SKILL lịch chưa có văn bản — nay ở `sync/scheduled-tasks/README.md`, mỗi khẳng định ở đó đối chiếu MÃ SỐNG.
(3) — khe test chốt `doctrine_tac_vu_lich` — nằm ở `test_verify_doctrine_tac_vu_lich_20261114.py` và `test_lich_nen_ky_cu_20261002.py`.
Không gọi mạng, không đọc settings/log thật (thư mục tạm).
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TV_RUT_BAI = "kiem-rut-bai-kho-thang"


def _nap(ten: str, tep: str):
    sp = importlib.util.spec_from_file_location(ten, REPO / "tools" / tep)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


K = _nap("_lndmt_kln", "kiem_lich_nen.py")
Q = _nap("_lndmt_qln", "quyen_lich_nen.py")


def _ghi(p: Path, nd: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(nd, encoding="utf-8", newline="\n")


# ── (1) cảm biến đọc MÃ KẾT THÚC ──────────────────────────────────────────────────────────────────────────────────────

SO_THANG = {"cua_so_ngay": 40, "tac_vu": [{"id": "tv", "cron": "30 18 4 * *", "tu_ngay": "2026-09-01", "grace_gio": 30,
                                           "dau_vet": {"loai": "log-ket-thuc", "path": "state/tv.log"}}]}
XET = dt.datetime(2026, 11, 6, 9, 0)   # kỳ gần nhất 04/11 18:30 đã quá hạn 30 giờ; kỳ 04/10 còn trong cửa sổ 40 ngày
KY_10 = "===== 2026-10-04 19:00:00 : KẾT THÚC tv (mã 0)\n"


@pytest.mark.parametrize("sau, tron, nhan", [
    (" chu_trinh_chung_cu (mã 0)", True, "mã 0"),
    (" kiem-tra-hoan-thien-he-thong-thang (mã 1)", True, "mã 1"),
    (" chu_trinh_chung_cu (mã 2)", False, "mã 2"),
    (" tv (mã 75)", False, "mã 75"),
    (" — bước (1)=0 (2)=0 (3)=0 (4)=0, tổng thể=PASS =====", True, "tổng thể=PASS"),
    (" tổng thể=PASS", True, "tổng thể=PASS"),
    (" — bước (1)=0 (2)=3, tổng thể=CÓ BƯỚC LỖI =====", False, "tổng thể=CÓ BƯỚC LỖI"),
    (" tv (mã 2) — tổng thể=PASS", False, "mã 2"),          # «(mã N)» thắng «tổng thể=…»
    (" tv", None, "không đọc được mã"),
    (" tổng thể=PASSX", None, "không đọc được mã"),
])
def test_phan_xu_ma_ket_thuc(sau, tron, nhan):
    assert K.phan_xu_ket_thuc(sau) == (tron, nhan)


def test_ma_tron_dung_hop_dong_bo_ghi():
    """0 và 1 đều là lượt ĐI HẾT với cả hai bộ ghi (ghi_dau_vet_lich --ma, chu_trinh_chung_cu) — 1 chỉ nói có việc cho người."""
    assert K.MA_TRON == frozenset({0, 1})
    g = (REPO / "tools" / "ghi_dau_vet_lich.py").read_text(encoding="utf-8")
    c = (REPO / "tools" / "chu_trinh_chung_cu.py").read_text(encoding="utf-8")
    assert "0 sạch · 1 có việc cho bác sĩ/đã tự sửa · 2 có mảng KHÔNG đo được" in g
    assert "Mã thoát: 0 = mọi chốt đạt · 1 = có việc cần bác sĩ làm · 2 = nền tảng không đáng tin." in c


@pytest.mark.parametrize("duoi", ["tv (mã 0)", "tv (mã 1)", "— tổng thể=PASS ====="])
def test_luot_tron_trong_han_la_dung_hen(tmp_path, duoi):
    _ghi(tmp_path / "state" / "tv.log", KY_10 + f"===== 2026-11-04 19:06:01 : KẾT THÚC {duoi}\n")
    assert K.kiem(XET, SO_THANG, tmp_path) == {"phat_hien": [], "khong_do_duoc": [], "ok": 1}


@pytest.mark.parametrize("duoi, nhan", [("tv (mã 2)", "mã 2"), ("— bước (2)=1, tổng thể=CÓ BƯỚC LỖI =====", "CÓ BƯỚC LỖI")])
def test_luot_khong_tron_ky_gan_nhat_la_cam(tmp_path, duoi, nhan):
    _ghi(tmp_path / "state" / "tv.log", KY_10 + f"===== 2026-11-04 19:06:01 : KẾT THÚC {duoi}\n")
    kq = K.kiem(XET, SO_THANG, tmp_path)
    assert kq["ok"] == 0 and kq["khong_do_duoc"] == []
    assert [(p["ky"], p["muc"], p["uu"]) for p in kq["phat_hien"]] == [("2026-11-04 18:30", "khong_tron", 1)], kq
    assert nhan in kq["phat_hien"][0]["thong_diep"] and "KHÔNG TRỌN" in kq["phat_hien"][0]["thong_diep"]


def test_chay_lai_tron_trong_han_xoa_luot_khong_tron(tmp_path):
    """Lượt mã 2 rồi bác sĩ áp quyền + «Run now» TRONG hạn (mã 0) ⇒ kỳ đúng hẹn."""
    _ghi(tmp_path / "state" / "tv.log", KY_10 + "===== 2026-11-04 18:31:00 : KẾT THÚC tv (mã 2)\n"
         "===== 2026-11-05 08:00:00 : KẾT THÚC tv (mã 0)\n")
    assert K.kiem(XET, SO_THANG, tmp_path) == {"phat_hien": [], "khong_do_duoc": [], "ok": 1}


def test_khong_tron_trong_han_roi_chay_tre_van_cam_va_noi_ca_hai(tmp_path):
    _ghi(tmp_path / "state" / "tv.log", KY_10 + "===== 2026-11-04 18:31:00 : KẾT THÚC tv (mã 2)\n"
         "===== 2026-11-06 08:00:00 : KẾT THÚC tv (mã 0)\n")
    kq = K.kiem(dt.datetime(2026, 11, 7, 9, 0), SO_THANG, tmp_path)
    assert [(p["muc"], p["uu"]) for p in kq["phat_hien"]] == [("khong_tron", 1)], kq
    assert "TRỄ 06/11 08:00" in kq["phat_hien"][0]["thong_diep"]


def test_khong_tron_ky_cu_khi_ky_sau_da_tron_la_vang(tmp_path):
    _ghi(tmp_path / "state" / "tv.log", "===== 2026-10-04 19:00:00 : KẾT THÚC tv (mã 2)\n"
         "===== 2026-11-04 19:06:01 : KẾT THÚC tv (mã 1)\n")
    kq = K.kiem(XET, SO_THANG, tmp_path)
    assert kq["ok"] == 0 and [(p["ky"][:10], p["muc"], p["uu"]) for p in kq["phat_hien"]] == [
        ("2026-10-04", "khong_tron", 2)], kq


def test_ket_thuc_khong_doc_duoc_ma_la_trang_khong_phai_xanh_cung_khong_phai_lo(tmp_path):
    _ghi(tmp_path / "state" / "tv.log", KY_10 + "===== 2026-11-04 19:06:01 : KẾT THÚC tv\n")
    kq = K.kiem(XET, SO_THANG, tmp_path)
    assert kq["ok"] == 0 and kq["phat_hien"] == [], kq
    assert len(kq["khong_do_duoc"]) == 1 and "không đọc được mã" in kq["khong_do_duoc"][0]


def test_main_in_tieu_de_khong_tron_va_ma_1(tmp_path, monkeypatch, capsys):
    _ghi(tmp_path / "state" / "tv.log", KY_10 + "===== 2026-11-04 19:06:01 : KẾT THÚC tv (mã 2)\n")
    kq = K.kiem(XET, SO_THANG, tmp_path)
    monkeypatch.setattr(K, "kiem", lambda: kq)
    assert K.main(["--im-khi-on"]) == 1
    ra = capsys.readouterr().out
    assert "KHÔNG CHẠY TRỌN" in ra and "🟠" in ra and "lượt KHÔNG TRỌN (mã 2)" in ra


def test_ham_cu_ket_thuc_van_tra_moc_gio(tmp_path):
    """`_ket_thuc()` là khuôn mà bộ ghi khác dẫn chiếu (chu_trinh_chung_cu, ghi_dau_vet_lich) — giữ nguyên kiểu trả."""
    _ghi(tmp_path / "x.log", "===== 2026-11-04 19:06:01 : KẾT THÚC tv (mã 2)\n")
    assert K._ket_thuc(tmp_path / "x.log") == [dt.datetime(2026, 11, 4, 19, 6, 1)]
    assert K._ket_thuc_co_ma(tmp_path / "vang.log") is None


# ── (2) giác quan quyền lượt lịch: «không đo được» ⇒ ⚪, không im ────────────────────────────────────────────────────────

M = _nap("_lndmt_tdxv", "tu_de_xuat_viec.py")


@pytest.fixture()
def _sach():
    M._GIAC_QUAN_CHET.clear()
    M._SO_GIAC_QUAN["chay"] = 0
    yield
    M._GIAC_QUAN_CHET.clear()


def test_giac_quan_quyen_khong_do_la_trang(_sach):
    kq = {"khong_do": ["quy tắc khai cho nền tảng darwin — máy này là win32, chưa đối chiếu settings"],
          "thieu_khai": [], "thieu_may": []}
    assert M.giac_quan_quyen_lich_nen(lambda: kq) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "quyền lượt lịch" in M._GIAC_QUAN_CHET[0]
    assert "không đo được" in M._GIAC_QUAN_CHET[0] and "darwin" in M._GIAC_QUAN_CHET[0]
    assert M._SO_GIAC_QUAN["chay"] == 1


def test_giac_quan_quyen_du_thi_im(_sach):
    assert M.giac_quan_quyen_lich_nen(lambda: {"khong_do": [], "thieu_khai": [], "thieu_may": []}) == []
    assert M._GIAC_QUAN_CHET == []


def test_giac_quan_quyen_thieu_khai_va_thieu_may_van_bao_nhu_cu(_sach):
    kq = {"khong_do": ["không đọc được settings.local.json (FileNotFoundError)"],
          "thieu_khai": [("tv", "python3 tools/moi.py")], "thieu_may": ["Bash(python3 tools/a.py)"]}
    ra = M.giac_quan_quyen_lich_nen(lambda: kq)
    assert [(u, ai) for u, ai, _v, _l in ra] == [(0, "👤"), (0, "🤖")]
    assert "python3 tools/moi.py" in ra[0][2] and ra[1][3] == "python3 tools/quyen_lich_nen.py --ap-dung"
    assert len(M._GIAC_QUAN_CHET) == 1  # thiếu khai + máy chưa áp vẫn kèm ⚪ khi phần còn lại không đo được


def test_giac_quan_quyen_cong_cu_hong_la_trang(_sach):
    def hong():
        raise KeyError("x")
    assert M.giac_quan_quyen_lich_nen(hong) == []
    assert len(M._GIAC_QUAN_CHET) == 1 and "KeyError" in M._GIAC_QUAN_CHET[0]


def test_bang_tu_de_xuat_goi_giac_quan_quyen():
    """Có công cụ mà không ai gọi thì như không có (BH41): luồng chính phải gọi hàm, chốt BH173 dò `_qln.kiem()`."""
    van = (REPO / "tools" / "tu_de_xuat_viec.py").read_text(encoding="utf-8")
    dong = [x for x in van.splitlines() if not x.lstrip().startswith("#")]
    assert any("de_xuat += giac_quan_quyen_lich_nen()" in x for x in dong)
    assert any("_qln.kiem()" in x for x in dong)


# ── (4) bước 0 tiền kiểm của tác vụ rút bài ngày 4 ───────────────────────────────────────────────────────────────────

SKILL_RUT_BAI = REPO / "sync" / "scheduled-tasks" / TV_RUT_BAI / "SKILL.md"
LENH_TIEN_KIEM = f"python3 tools/quyen_lich_nen.py --tac-vu {TV_RUT_BAI}"


def test_skill_rut_bai_tien_kiem_truoc_buoc_1_va_dung():
    sk = SKILL_RUT_BAI.read_text(encoding="utf-8")
    i_q, i_1 = sk.index(f"`{LENH_TIEN_KIEM}`"), sk.index("`python3 tools/sync_safety_check.py`")
    assert i_q < i_1
    khoi = sk[i_q:i_1]
    for cum in ("mã 1", "mã 2", "DỪNG LƯỢT NGAY", "KHÔNG chạy bước 1–4", "`python3 tools/quyen_lich_nen.py --ap-dung`",
                "alerts/<YYYY-MM-DD>.md", "Windows", "KHÔNG tự gõ dòng vào log"):
        assert cum in khoi, cum
    # Lệnh tiền kiểm là lệnh việc ĐẦU TIÊN mà SKILL nêu (trước đó chỉ có lệnh --ap-dung IN cho bác sĩ).
    lenh = Q.lenh_trong_skill(sk)
    assert lenh.index(LENH_TIEN_KIEM) < lenh.index("python3 tools/sync_safety_check.py")
    assert [c for c in lenh[:lenh.index(LENH_TIEN_KIEM)] if c != "python3 tools/quyen_lich_nen.py --ap-dung"] == []


def test_khai_quyen_rut_bai_co_lenh_tien_kiem_va_ap_dung_chi_in():
    khai = json.loads((REPO / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))["tac_vu"][TV_RUT_BAI]
    assert LENH_TIEN_KIEM in khai["lenh"]
    assert "python3 tools/quyen_lich_nen.py --ap-dung" in khai["khong_chay"]
    assert not [c for c in khai["lenh"] if "--ap-dung" in c]
    assert "alerts/**" in khai["ghi"]  # dòng alerts khi dừng ở bước 0 ghi bằng Write/Edit


def test_dong_bo_runtime_nhan_tap_tien_kiem_cua_rut_bai():
    """Runtime giữ SKILL cũ tới khi quyền của ĐÚNG tác vụ này 🟢 — `dong_bo_tac_vu_lich` đọc tập --tac-vu từ SKILL nguồn."""
    D = _nap("_lndmt_dbtvl", "dong_bo_tac_vu_lich.py")
    assert D._TIEN_KIEM_RE.search(SKILL_RUT_BAI.read_text(encoding="utf-8")).group(1) == TV_RUT_BAI


def test_tien_kiem_rut_bai_bat_dung_quy_tac_moi_chua_ap(tmp_path):
    """Hành vi: máy đã áp mọi quy tắc CŨ của tác vụ rút bài ⇒ tiền kiểm báo đúng MỘT quy tắc mới (lệnh tiền kiểm) chưa áp."""
    khai = json.loads((REPO / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))
    _ghi(tmp_path / "sync" / "quyen-lich-nen.json", json.dumps(khai, ensure_ascii=False))
    _ghi(tmp_path / "sync" / "scheduled-tasks" / TV_RUT_BAI / "SKILL.md", SKILL_RUT_BAI.read_text(encoding="utf-8"))
    moi = f"Bash({LENH_TIEN_KIEM})"
    cu = [q for q in Q.quy_tac_may({"tac_vu": {TV_RUT_BAI: khai["tac_vu"][TV_RUT_BAI]}}, tmp_path) if q != moi]
    _ghi(tmp_path / ".claude" / "settings.local.json", json.dumps({"permissions": {"allow": cu}}))
    kq = Q.kiem(tmp_path, nen_tang="darwin", tac_vu=[TV_RUT_BAI])
    assert kq == {"khong_do": [], "thieu_khai": [], "thieu_may": [moi]}, kq
    _ghi(tmp_path / ".claude" / "settings.local.json", json.dumps({"permissions": {"allow": cu + [moi]}}))
    assert Q.kiem(tmp_path, nen_tang="darwin", tac_vu=[TV_RUT_BAI]) == {"khong_do": [], "thieu_khai": [], "thieu_may": []}


# ── (5) quy ước soạn SKILL lịch: văn bản tồn tại và khớp MÃ SỐNG ──────────────────────────────────────────────────────

README = REPO / "sync" / "scheduled-tasks" / "README.md"


def test_readme_quy_uoc_co_mat_va_duoc_track():
    vb = README.read_text(encoding="utf-8")
    assert "## Quy ước soạn SKILL tác vụ lịch" in vb
    gi = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "!/sync/" in gi and "!/sync/scheduled-tasks/" in gi  # luật `/*` không nuốt README


def test_readme_khop_phep_do_lenh_cua_quyen_lich_nen():
    """README nói phép dò xét python3/venv/bash/git/gh/cd — đúng regex của `quyen_lich_nen` (đổi một bên ⇒ đỏ)."""
    vb = README.read_text(encoding="utf-8")
    for dau in ("python3", "~/.ebm-venv/bin/python", "bash", "git", "gh", "cd"):
        assert f"`{dau}`" in vb, dau
        assert Q._LENH_RE.search(f"`{dau} x`"), dau
    assert Q.ly_do_ghep("git status | head") and Q.ly_do_ghep("cd x") and Q.ly_do_ghep("a && b")
    assert "khong_chay" in vb and "_ranh_gioi" in vb and "--ap-dung" in vb


def test_readme_khop_hop_dong_ma_ket_thuc_va_danh_sach_da_bo():
    vb = README.read_text(encoding="utf-8")
    assert "`MA_TRON`" in vb and K.MA_TRON == frozenset({0, 1})
    assert re.search(r"0 sạch · 1 đi hết, có việc cho bác sĩ · 2 ", vb)
    V = _nap("_lndmt_vcra", "verify_claude_code_repo_alignment.py")
    assert "`TAC_VU_LICH_DA_BO`" in vb and V.TAC_VU_LICH_DA_BO
    assert "doctrine_tac_vu_lich" in vb and "doctrine_tac_vu_lich" in [c["name"] for c in V.run_verification()["checks"]]
    D = (REPO / "tools" / "dong_bo_tac_vu_lich.py").read_text(encoding="utf-8")
    assert "cho_quyen" in vb and "cho_quyen" in D
    assert "BH173 (13)" in vb


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
