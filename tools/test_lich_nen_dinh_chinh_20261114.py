"""Đính chính PR #339 (lịch nền tiền kiểm + dấu vết) theo người duyệt độc lập — 14/11/2026.

Bốn lỗi có thật, đo trên cây/máy thật:
  (1) Bước 4b của tác vụ tháng đọc «`so_xac_minh_nguon` mã 2 không kèm SO_HONG» thành CÓ NGUỒN ĐÃ RÚT ⇒ ghi 🔴 vào alerts/.
      Đo 14/11: `--bao-cao` trả 2 mà chỉ in khối «✅ BẢN ĐÍNH CHÍNH bị rút — bác sĩ ĐÃ KÝ» (mã 2 gồm cả ca đính chính đã ký) —
      đúng lỗi chu_trinh_chung_cu đã vá 27/09 (BH122, họ BH115) tái phát. (2) Tiền đề «chưa có nhịp làm mới định kỳ» sai: tác vụ
      `kiem-rut-bai-kho-thang` (ngày 4) là owner DUY NHẤT, chạy cùng lệnh + phủ hub/mồ côi. ⇒ GỠ 4b, giao phân xử cho owner.
  (3) Cảm biến in «⚪ không đọc được log (bản sao trần/máy khác)» trên chính máy chạy lịch khi log chưa từng được tạo — lệnh
      `--bat-dau` đầu tiên bị cắt (chưa áp quyền) thì đứng ⚪ mãi. ⇒ mốc `dau_vet.tu_ngay` + máy có bản chạy ⇒ 🔴 từ mốc.
  (4) `tu_sua_chua --ap-dung` tua nhanh master rồi `dong_bo_tac_vu_lich --ap-dung` chép SKILL mới vào runtime TRƯỚC khi bác sĩ áp
      quyền ⇒ lượt tháng bị cắt ngay bước 0, mất bộ thu thập an toàn thuốc. ⇒ chỉ chép khi `quyen_lich_nen --tac-vu` 🟢.
"""

from __future__ import annotations

import ast
import contextlib
import datetime as dt
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import kiem_lich_nen as K  # noqa: E402
import quyen_lich_nen as Q  # noqa: E402

SKILL_DIR = REPO / "sync" / "scheduled-tasks"


def _nap(ten: str, bi_danh: str):
    sp = importlib.util.spec_from_file_location(bi_danh, REPO / "tools" / ten)
    mod = importlib.util.module_from_spec(sp)
    sys.modules[bi_danh] = mod
    sp.loader.exec_module(mod)
    return mod


def _ghi(p: Path, noi_dung: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(noi_dung, encoding="utf-8", newline="\n")


# ── (1)+(2) tác vụ tháng KHÔNG tự đọc mã sổ xác minh; owner ngày 4 phân xử đúng ca đính chính đã ký ─────────────────────────


def test_tac_vu_thang_khong_chay_so_xac_minh_owner_la_tac_vu_ngay_4():
    sk = (SKILL_DIR / "cap-nhat-thang-ebm" / "SKILL.md").read_text(encoding="utf-8")
    assert not [c for c in Q.lenh_trong_skill(sk) if "so_xac_minh_nguon" in c], \
        "tác vụ tháng lại chạy sổ xác minh — lặp owner ngày 4 và tự đọc mã 2 thành «nguồn đã rút» (đỏ giả cho đính chính đã ký)"
    khai = json.loads((REPO / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))["tac_vu"]
    assert not [c for c in khai["cap-nhat-thang-ebm"]["lenh"] if "so_xac_minh_nguon" in c]
    assert "kiem-rut-bai-kho-thang" in sk, "SKILL tháng phải trỏ owner duy nhất của sổ xác minh/rút bài"
    # owner thật sự chạy: SKILL ngày 4 gọi chu_trinh, chu_trinh gọi đủ ba lượt sổ xác minh (dashboard · hub · mồ côi)
    owner = (SKILL_DIR / "kiem-rut-bai-kho-thang" / "SKILL.md").read_text(encoding="utf-8")
    assert "python3 tools/chu_trinh_chung_cu.py --vong 3 --ghi-log state/kiem-rut-bai-kho.log" in Q.lenh_trong_skill(owner)
    co: set[str] = set()
    for n in ast.walk(ast.parse((REPO / "tools" / "chu_trinh_chung_cu.py").read_text(encoding="utf-8"))):
        if isinstance(n, ast.List):
            hang = [x.value for x in n.elts if isinstance(x, ast.Constant) and isinstance(x.value, str)]
            if "tools/so_xac_minh_nguon.py" in hang:
                co.update(hang)
    assert {"--vong", "--quet-ledger", "--phu-mo-coi"} <= co, co


def _so_fixture(tmp_path: Path, rut_that: bool) -> Path:
    hom_nay = dt.date.today().isoformat()
    muc = {
        "pmid:41110921": {"loai": "pmid", "gia_tri": "41110921", "da_rut": True, "sua_loi_bi_rut": True,
                          "thong_bao_ids": ["pmid:41000001"], "ghi_chu_rut": "retracted (notice)",
                          "cac_dashboard": ["WebDashboard_A.html"]},
        "pmid:12345678": {"loai": "pmid", "gia_tri": "12345678", "xac_minh_luc": hom_nay, "kiem_rut_luc": hom_nay,
                          "cac_dashboard": ["WebDashboard_A.html"]},
    }
    if rut_that:
        muc["pmid:7777777"] = {"loai": "pmid", "gia_tri": "7777777", "da_rut": True, "ghi_chu_rut": "retracted",
                               "cac_dashboard": ["WebDashboard_B.html"]}
    so = tmp_path / ".so-xac-minh-nguon.json"
    so.write_text(json.dumps({"phien_ban": 1, "muc": muc}), encoding="utf-8", newline="\n")
    return so


def _bao_cao_that(tmp_path: Path, monkeypatch, rut_that: bool) -> tuple[int, str]:
    """Đầu ra THẬT của `so_xac_minh_nguon.bao_cao()` trên sổ fixture (chữ ký đính chính coi như đã khớp sổ ký)."""
    sx = _nap("so_xac_minh_nguon.py", "_sxmn_dinh_chinh_20261114")
    monkeypatch.setattr(sx, "SO", _so_fixture(tmp_path, rut_that))
    monkeypatch.setattr(sx, "_dinh_chinh_da_ky", lambda khoa, bg: khoa == "pmid:41110921")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = sx.bao_cao()
    return rc, buf.getvalue()


def _chu_trinh_tren(rc_so: int, out_so: str, cho_ky: str, tat_ca: str) -> str:
    """Chạy `chu_trinh_chung_cu.main(--nhanh)` với bước ③④ trả đúng (rc, đầu ra) của sổ — phần phân xử là mã thật."""
    C = _nap("chu_trinh_chung_cu.py", "_ctcc_dinh_chinh_20261114")

    class _P:
        def __init__(self, rc, out):
            self.returncode, self.stdout, self.stderr = rc, out, ""

    def _goi(cmd, **_kw):
        cmd = [str(c) for c in cmd]
        if len(cmd) > 1 and "so_xac_minh_nguon.py" in cmd[1]:
            return _P(rc_so, out_so)
        if len(cmd) > 2 and "mau_ky_rut_bai.py" in cmd[1]:
            return _P(0, {"--dem": cho_ky, "--dem-tat-ca": tat_ca}.get(cmd[2], ""))
        return _P(0, "")
    buf = io.StringIO()
    with mock.patch.object(C.subprocess, "run", side_effect=_goi), contextlib.redirect_stdout(buf):
        C.main(["--nhanh"])
    return buf.getvalue()


def test_dinh_chinh_da_ky_khong_sinh_do_qua_owner(tmp_path, monkeypatch):
    """Đúng ca đo 14/11: sổ trả 2 mà chỉ có khối «✅ … ĐÃ KÝ». Owner (chu_trinh) không được kéo 🔴 «rút bỏ hẳn»."""
    rc, out = _bao_cao_that(tmp_path, monkeypatch, rut_that=False)
    assert rc == 2, "giả định của ca đo đổi — xem lại bước phân xử mã 2"
    assert "✅ BẢN ĐÍNH CHÍNH" in out and "🔴" not in out
    tong = _chu_trinh_tren(rc, out, cho_ky="0", tat_ca="1")
    assert "CÓ NGUỒN RÚT BỎ HẲN" not in tong, "đính chính bác sĩ đã ký bị đọc thành rút bỏ hẳn — còi đỏ giả (họ BH115)"
    assert "ℹ 1 nguồn mang cờ rút bài là BẢN ĐÍNH CHÍNH" in tong


def test_rut_that_ben_canh_dinh_chinh_da_ky_van_do(tmp_path, monkeypatch):
    rc, out = _bao_cao_that(tmp_path, monkeypatch, rut_that=True)
    assert rc == 2 and "🔴 NGUỒN ĐÃ BỊ RÚT" in out and "7777777" in out
    assert "CÓ NGUỒN RÚT BỎ HẲN" in _chu_trinh_tren(rc, out, cho_ky="0", tat_ca="1")


# ── (3) cảm biến: mốc dấu vết + máy có bản chạy mà thiếu log ⇒ 🔴, không «⚪ bản sao trần» ─────────────────────────────────


SO_MOC = {"cua_so_ngay": 60, "tac_vu": [
    {"id": "tv", "cron": "0 18 3 * *", "tu_ngay": "2026-10-01", "grace_gio": 30,
     "dau_vet": {"loai": "log-ket-thuc", "path": "state/tv.log", "ghi_boi": "tools/ghi_dau_vet_lich.py",
                 "tu_ngay": "2026-12-03"}}]}


def _ban_chay(tmp_path: Path, co_tac_vu: bool) -> Path:
    bc = tmp_path / "scheduled-tasks"
    (bc / ("tv" if co_tac_vu else "tac-vu-khac")).mkdir(parents=True)
    return bc


@pytest.mark.parametrize("co_tac_vu", [True, False])
def test_ky_truoc_moc_khong_do_va_khong_gan_nhan_ban_sao_tran(tmp_path, co_tac_vu):
    (tmp_path / "state").mkdir()
    kq = K.kiem(dt.datetime(2026, 11, 14, 9, 0), SO_MOC, tmp_path, _ban_chay(tmp_path, co_tac_vu))
    assert kq["phat_hien"] == [] and kq["ok"] == 0
    assert len(kq["khong_do_duoc"]) == 1 and "03/12/2026" in kq["khong_do_duoc"][0]
    assert "bản sao trần/máy khác" not in kq["khong_do_duoc"][0]


def test_may_chay_lich_thieu_log_tu_moc_la_ky_lo(tmp_path):
    """Lệnh `--bat-dau` đầu tiên bị cắt (chưa áp quyền) ⇒ log không tồn tại. Từ mốc, đó là kỳ lỡ — gãy ồn."""
    (tmp_path / "state").mkdir()
    kq = K.kiem(dt.datetime(2026, 12, 5, 9, 0), SO_MOC, tmp_path, _ban_chay(tmp_path, True))
    assert [(p["ky"], p["muc"], p["uu"]) for p in kq["phat_hien"]] == [("2026-12-03 18:00", "lo", 0)]
    assert "chưa từng được tạo" in kq["phat_hien"][0]["thong_diep"]
    assert kq["khong_do_duoc"] == []


def test_may_khong_chay_lich_thieu_log_van_khong_do(tmp_path):
    kq = K.kiem(dt.datetime(2026, 12, 5, 9, 0), SO_MOC, tmp_path, _ban_chay(tmp_path, False))
    assert kq["phat_hien"] == [] and len(kq["khong_do_duoc"]) == 1
    assert "không có bản chạy" in kq["khong_do_duoc"][0] and "bản sao trần/máy khác" not in kq["khong_do_duoc"][0]


def test_co_log_dung_hen_tu_moc_thi_xanh(tmp_path):
    _ghi(tmp_path / "state" / "tv.log", "===== 2026-12-03 18:01:00 : BẮT ĐẦU tv\n===== 2026-12-03 18:40:00 : KẾT THÚC tv (mã 0)\n")
    kq = K.kiem(dt.datetime(2026, 12, 5, 9, 0), SO_MOC, tmp_path, _ban_chay(tmp_path, True))
    assert kq["phat_hien"] == [] and kq["ok"] == 1


def test_tac_vu_tu_ghi_dau_vet_tren_repo_that_deu_khai_moc():
    """Tác vụ ghi log bằng `ghi_dau_vet_lich` mà không khai mốc thì log vắng trên máy chạy lịch lại thành ⚪ mãi."""
    ky = json.loads((REPO / "sync" / "lich-nen-ky-vong.json").read_text(encoding="utf-8"))
    thieu = [t["id"] for t in ky["tac_vu"] if (t.get("dau_vet") or {}).get("ghi_boi") and not t["dau_vet"].get("tu_ngay")]
    assert thieu == []


# ── (4) đồng bộ tác vụ lịch: không chép SKILL mới khi quyền của nó chưa 🟢 ─────────────────────────────────────────────────


def _git(repo: Path, *lenh: str) -> None:
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org",
                    "-c", "commit.gpgsign=false", *lenh], check=True, capture_output=True)


TIEN_KIEM = "`python3 tools/quyen_lich_nen.py --tac-vu thang,quy-trinh`"
KHAI_Q = {"nen_tang": "darwin", "tac_vu": {
    "thang": {"lenh": ["python3 tools/quyen_lich_nen.py --tac-vu thang,quy-trinh", "python3 tools/a.py",
                       "python3 tools/moi.py"], "khong_chay": [], "ghi": []},
    "quy-trinh": {"lenh": ["python3 tools/q.py"], "khong_chay": [], "ghi": []},
}}
DU = ["Bash(python3 tools/quyen_lich_nen.py --tac-vu thang,quy-trinh)", "Bash(python3 tools/a.py)",
      "Bash(python3 tools/moi.py)", "Bash(python3 tools/q.py)"]


@pytest.fixture()
def M():
    return _nap("dong_bo_tac_vu_lich.py", "_dbtvl_cong_quyen_20261114")


@pytest.fixture()
def moi_truong(tmp_path):
    """`thang`: v1 cũ → v2 thêm tiền kiểm + lệnh mới; `le`: tác vụ KHÔNG có hợp đồng quyền; `quy-trinh`: quy trình SKILL
    `thang` thi hành (không phải tác vụ lịch riêng — như goi-duyet-tuan-ebm)."""
    repo, bc = tmp_path / "repo", tmp_path / "scheduled-tasks"
    _ghi(repo / "sync" / "lich-nen-ky-vong.json", json.dumps({"tac_vu": [{"id": "thang"}, {"id": "le"}]}))
    _ghi(repo / "sync" / "quyen-lich-nen.json", json.dumps(KHAI_Q))
    _ghi(repo / "sync" / "scheduled-tasks" / "quy-trinh" / "SKILL.md", "`python3 tools/q.py`\n")
    _git(tmp_path, "init", "-q", str(repo))
    for ban in ("v1", "v2"):
        _ghi(repo / "sync" / "scheduled-tasks" / "thang" / "SKILL.md", "`python3 tools/a.py`\n" if ban == "v1" else
             f"{TIEN_KIEM}\n`python3 tools/a.py`\n`python3 tools/moi.py`\n")
        _ghi(repo / "sync" / "scheduled-tasks" / "le" / "SKILL.md", f"le {ban}\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", ban)
    _ghi(bc / "thang" / "SKILL.md", "`python3 tools/a.py`\n")
    _ghi(bc / "le" / "SKILL.md", "le v1\n")
    return repo, bc


def _allow(repo: Path, allow: list[str]) -> None:
    _ghi(repo / ".claude" / "settings.local.json", json.dumps({"permissions": {"allow": allow}}))


@pytest.mark.parametrize("allow", [
    [q for q in DU if "moi.py" not in q],   # lệnh mới của chính tác vụ chưa áp
    [q for q in DU if "q.py" not in q],     # quy trình nó thi hành (tập --tac-vu của SKILL) chưa áp
    None,                                   # settings không đọc được ⇒ không đo được ⇒ giữ (fail-closed)
])
def test_quyen_chua_xanh_thi_giu_ban_chay_cu(M, moi_truong, allow):
    repo, bc = moi_truong
    if allow is not None:
        _allow(repo, allow)
    loai = M.phan_loai(repo, bc, nen_tang="darwin")
    assert loai == {"thang": "cho_quyen", "le": "tut_hau"}
    da_chep, _sl = M.ap_dung(repo, bc, loai, nen_tang="darwin")
    assert da_chep == ["le"], "tác vụ không có hợp đồng quyền vẫn chép như cũ"
    assert (bc / "thang" / "SKILL.md").read_text(encoding="utf-8") == "`python3 tools/a.py`\n", \
        "SKILL mới bị chép vào runtime khi lệnh của nó chưa được phép — lượt lịch kế tiếp bị cắt ngang"
    # người gọi truyền phân loại cũ («tut_hau») — ap_dung vẫn phải tự kiểm cổng trước khi chép
    assert M.ap_dung(repo, bc, {"thang": "tut_hau"}, nen_tang="darwin")[0] == []


def test_quyen_xanh_thi_chep(M, moi_truong):
    repo, bc = moi_truong
    _allow(repo, DU)
    loai = M.phan_loai(repo, bc, nen_tang="darwin")
    assert loai == {"thang": "tut_hau", "le": "tut_hau"}
    assert sorted(M.ap_dung(repo, bc, loai, nen_tang="darwin")[0]) == ["le", "thang"]
    assert "moi.py" in (bc / "thang" / "SKILL.md").read_text(encoding="utf-8")


def test_khai_cho_nen_tang_khac_hoac_khong_co_tep_khai_thi_khong_chan(M, moi_truong):
    repo, bc = moi_truong
    assert M.cong_quyen(repo, "thang", nen_tang="win32")[0] == "khong_ap"
    (repo / "sync" / "quyen-lich-nen.json").unlink()
    assert M.cong_quyen(repo, "thang", nen_tang="darwin")[0] == "khong_ap"
    assert M.phan_loai(repo, bc, nen_tang="darwin")["thang"] == "tut_hau"


def test_tep_khai_hong_thi_giu(M, moi_truong):
    repo, bc = moi_truong
    _allow(repo, DU)
    _ghi(repo / "sync" / "quyen-lich-nen.json", "{hỏng")
    assert M.cong_quyen(repo, "thang", nen_tang="darwin")[0] == "khong_do"
    assert M.phan_loai(repo, bc, nen_tang="darwin")["thang"] == "cho_quyen"


def test_main_cho_quyen_la_viec_bac_si_khong_phai_viec_may(M, moi_truong, monkeypatch, capsys):
    repo, bc = moi_truong
    _allow(repo, [q for q in DU if "moi.py" not in q])
    _ghi(bc / "le" / "SKILL.md", "le v2\n")
    monkeypatch.setattr(M, "REPO", repo)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setenv("EBM_TAC_VU_LICH_DIR", str(bc))
    monkeypatch.setattr(sys, "argv", ["x", "--im-khi-on"])
    assert M.main() == 0, "giữ bản chạy chờ quyền không phải việc máy tự sửa — bước sửa của tu_sua_chua chạy lại vô ích"
    monkeypatch.setattr(sys, "argv", ["x", "--can-bac-si", "--im-khi-on"])
    assert M.main() == 1
    monkeypatch.setattr(sys, "argv", ["x", "--ap-dung"])
    M.main()
    out = capsys.readouterr().out
    assert "quyen_lich_nen.py --ap-dung" in out and "máy chưa áp: Bash(python3 tools/moi.py)" in out
    assert (bc / "thang" / "SKILL.md").read_text(encoding="utf-8") == "`python3 tools/a.py`\n"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
