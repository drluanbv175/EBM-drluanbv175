"""Hồi quy 30/09/2026 — `sources_health.py` trên BẢN SAO GIT TRẦN của máy thật (BH140).

Đo thật 30/09: chạy công cụ trong một worktree git của repo gốc — nơi không có `medical-ebm-automation/`
(không lồng, không anh em) — cho «SRC-003 … → BROKEN», vì thư mục Retraction Watch nằm trong engine. Không
kèm `--khong-ghi` thì nhãn sai đó được GHI vào sổ tracked của worktree. «Không đo được» bị đọc thành «hỏng».

Các ca dưới đây dựng CÂY GIẢ trong tmp_path rồi trỏ `GOC`/`SO` của công cụ vào đó; hai phép dò («bản sao
trần» · «gốc engine») là HÀM THẬT của `tools/ban_sao_tran.py`, không bị thay bằng giả. Không ca nào gọi mạng:
`--khong-mang`, và `urlopen` bị khoá (ca cần một nguồn API hỏng thì thay `urlopen` bằng kịch bản lỗi).
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
import urllib.error
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]

RW = {"id": "SRC-003", "name": "Retraction Watch DB ngoại tuyến", "status": "active", "access": "file",
      "scan_frequency": "monthly", "endpoint_or_url": "medical-ebm-automation/data/retraction_watch/",
      "last_success_at": "2026-09-20"}
API = {"id": "SRC-004", "name": "Crossref", "status": "active", "access": "api", "scan_frequency": "weekly",
       "endpoint_or_url": "https://api.crossref.org/"}


def _nap():
    spec = importlib.util.spec_from_file_location("sh_engine_vang_test", GOC / "tools" / "sources_health.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cam_mang(*a, **kw):
    raise AssertionError("ca ngoại tuyến mà công cụ vẫn mở kết nối mạng")


def _loi_that(*a, **kw):
    raise urllib.error.URLError(OSError("[Errno 111] Connection refused"))


def _proxy_tu_choi(*a, **kw):
    raise urllib.error.URLError(OSError("Tunnel connection failed: 403 Forbidden"))


class _TraLoi200:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _ok(*a, **kw):
    return _TraLoi200()


def _cay(tmp_path: Path, *, engine: str | None = None, kho_rw: bool = False, goc_du_lieu: bool = False) -> Path:
    """Dựng gốc repo giả. `engine`: None = vắng · "long" = lồng trong repo · "anh_em" = cạnh repo.
    `kho_rw`: có thư mục Retraction Watch (kèm một tệp vừa ghi). `goc_du_lieu`: có `EBM-Dashboards/`
    — tức máy thật, không phải bản sao trần."""
    repo = tmp_path / "cha" / "repo"
    (repo / "data").mkdir(parents=True)
    if goc_du_lieu:
        (repo / "EBM-Dashboards").mkdir()
    if engine:
        goc_engine = (repo if engine == "long" else repo.parent) / "medical-ebm-automation"
        goc_engine.mkdir()
        if kho_rw:
            kho = goc_engine / "data" / "retraction_watch"
            kho.mkdir(parents=True)
            (kho / "retraction_watch.csv").write_text("pmid\n1\n", encoding="utf-8")
    return repo


@pytest.fixture()
def chay(monkeypatch, capsys):
    """Trả hàm `chay(repo, nguon, *argv, cloud=False, urlopen=_cam_mang)` → (mã thoát, stdout, sổ đã
    bị ghi chưa, sổ sau khi chạy)."""
    def _chay(repo: Path, nguon: list[dict], *argv: str, cloud: bool = False, urlopen=_cam_mang):
        mod = _nap()
        so = repo / "data" / "sources.json"
        so.write_text(json.dumps({"updated": "2000-01-01", "sources": nguon}, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
        truoc = so.read_bytes()
        monkeypatch.setattr(mod, "GOC", repo)
        monkeypatch.setattr(mod, "SO", so)
        monkeypatch.setattr(mod.urllib.request, "urlopen", urlopen)
        if cloud:
            monkeypatch.setenv("CLAUDE_CODE_REMOTE", "true")
        else:
            monkeypatch.delenv("CLAUDE_CODE_REMOTE", raising=False)
        monkeypatch.setattr(sys, "argv", ["sources_health", *argv])
        ma = mod.main()
        sau = so.read_bytes()
        return ma, capsys.readouterr().out, sau != truoc, json.loads(sau)
    return _chay


def _nhan(so: dict, sid: str = "SRC-003") -> str:
    return next(s for s in so["sources"] if s["id"] == sid)["status"]


# ── Lỗi gốc: bản sao trần không mang engine ─────────────────────────────────────────────────────────────

def test_ban_sao_tran_khong_engine_la_khong_do_duoc_khong_phai_broken(chay, tmp_path):
    ma, out, da_ghi, so = chay(_cay(tmp_path), [dict(RW)], "--khong-mang")
    assert ma == 0, "engine vắng trên bản sao trần không được làm mã thoát thành 1"
    assert "KHÔNG ĐO ĐƯỢC — engine vắng" in out and "SRC-003" in out
    assert "BROKEN" not in out and "✗" not in out
    assert not da_ghi and _nhan(so) == "active", "trạng thái trong sổ phải giữ nguyên"


def test_ban_sao_tran_khong_ghi_so_ke_ca_khi_mot_nguon_api_hong_that(chay, tmp_path):
    """Thăm sống hỏng thật ⇒ vẫn BÁO degraded (mã 1), nhưng bản sao trần không ghi nhãn vào sổ tracked."""
    ma, out, da_ghi, so = chay(_cay(tmp_path), [dict(API), dict(RW)], urlopen=_loi_that)
    assert ma == 1 and "SRC-004" in out and "→ DEGRADED" in out
    assert ("🟠 SỔ NGUỒN: 0 active · ⚪ 1 active KHÔNG đo được lượt này (nhãn theo sổ) · 1 degraded/broken"
            " · 0 not-covered") in out
    assert not da_ghi and _nhan(so, "SRC-004") == "active"
    # Khớp đúng DÒNG lý do (dòng ⚪ engine vắng cũng có chữ «bản sao git trần» — khớp lỏng là xanh giả).
    assert "KHÔNG ghi sổ data/sources.json (bản sao git trần —" in out and "(--khong-ghi)" not in out


def test_khong_ghi_tuong_minh_tren_ban_sao_tran_noi_dung_ly_do(chay, tmp_path):
    ma, out, da_ghi, _ = chay(_cay(tmp_path), [dict(RW)], "--khong-mang", "--khong-ghi")
    assert ma == 0 and not da_ghi
    assert "KHÔNG ghi sổ data/sources.json (--khong-ghi)." in out and "(bản sao git trần —" not in out


def test_im_khi_on_van_neu_nguon_khong_do_duoc(chay, tmp_path):
    """Chế độ hook: im khi ổn, nhưng «không đo được» không phải «ổn» — dòng ⚪ vẫn phải hiện."""
    ma, out, _, _ = chay(_cay(tmp_path), [dict(RW)], "--khong-mang", "--im-khi-on")
    assert ma == 0 and "KHÔNG ĐO ĐƯỢC — engine vắng" in out and "🟢" not in out


def test_dong_tong_ket_khong_dem_nguon_chua_do_la_khoe(chay, tmp_path):
    ma, out, _, _ = chay(_cay(tmp_path), [dict(API), dict(RW)], "--khong-mang")
    assert ma == 0
    assert "🟢 SỔ NGUỒN: 1 active khoẻ · ⚪ 1 active KHÔNG đo được lượt này" in out


def test_dong_tong_ket_cung_tru_nguon_bi_proxy_tu_choi(chay, tmp_path):
    """Cùng luật cho loại ⚪ có từ 24/09 (proxy môi trường từ chối): chưa tới được nguồn thì không phải «khoẻ»."""
    repo = _cay(tmp_path, goc_du_lieu=True)
    ma, out, da_ghi, so = chay(repo, [dict(API)], urlopen=_proxy_tu_choi)
    assert ma == 0 and "proxy môi trường từ chối" in out
    assert "🟢 SỔ NGUỒN: 0 active khoẻ · ⚪ 1 active KHÔNG đo được lượt này" in out
    # Máy thật đi nhánh GHI (bản vá 24/09) — từ 03/10/2026 nhánh đó ghi dấu thăm ra state/ và CHỈ ghi sổ tracked khi nội dung
    # đổi; nhãn giữ nguyên nên sổ tracked không bị viết lại.
    assert not da_ghi and _nhan(so, "SRC-004") == "active"
    assert (repo / "state" / "tham-song-nguon.json").exists(), "máy thật phải đi nhánh ghi (dấu thăm)"


def test_tham_song_ok_khong_viet_lai_so_tracked_chi_ghi_dau_tham(chay, tmp_path):
    """03/10/2026 (N11/PM-14): lượt đo chỉ đổi `last_probe_at` ⇒ sổ tracked GIỮ NGUYÊN BYTE; dấu thăm vào state/."""
    repo = _cay(tmp_path, goc_du_lieu=True)
    ma, _out, da_ghi, so = chay(repo, [dict(API)], urlopen=_ok)
    dau = json.loads((repo / "state" / "tham-song-nguon.json").read_text(encoding="utf-8"))
    assert ma == 0 and not da_ghi and so["updated"] == "2000-01-01"
    assert dau["last_probe_at"]["SRC-004"] == dau["cap_nhat"]


def test_chu_ky_so_bo_dau_ngay_nhung_giu_noi_dung():
    mod = _nap()
    a = {"updated": "2026-10-01", "sources": [{"id": "S", "status": "active", "last_probe_at": "2026-10-01", "last_success_at": "x"}]}
    b = {"updated": "2026-10-03", "sources": [{"id": "S", "status": "active", "last_probe_at": "2026-10-03", "last_success_at": "x"}]}
    assert mod.chu_ky_so(a) == mod.chu_ky_so(b)
    for khoa, gt in (("status", "degraded"), ("last_success_at", "y")):
        c = json.loads(json.dumps(b))
        c["sources"][0][khoa] = gt
        assert mod.chu_ky_so(c) != mod.chu_ky_so(a), f"đổi {khoa} phải là thay đổi NỘI DUNG"


# ── Răng phải còn: thiếu THẬT vẫn là BROKEN ─────────────────────────────────────────────────────────────

def test_may_con_goc_du_lieu_ma_mat_engine_van_broken_va_ghi_so(chay, tmp_path):
    """Còn `EBM-Dashboards/` = máy thật (có thể đang hỏng dở cây OneDrive) — mất engine là thiếu THẬT."""
    ma, out, da_ghi, so = chay(_cay(tmp_path, goc_du_lieu=True), [dict(RW)], "--khong-mang")
    assert ma == 1 and "SRC-003" in out and "→ BROKEN" in out
    assert "KHÔNG ĐO ĐƯỢC" not in out, "máy còn gốc dữ liệu thì mất engine không được ⚪ hoá"
    assert da_ghi and _nhan(so) == "broken" and so["updated"] != "2000-01-01"


@pytest.mark.parametrize("vi_tri, ghi_so", [("long", True), ("anh_em", False)])
def test_engine_co_mat_ma_thieu_dung_thu_muc_nguon_van_broken(chay, tmp_path, vi_tri, ghi_so):
    """Engine lồng ⇒ không phải bản sao trần, nhãn được ghi. Engine anh em trên cây không có gốc dữ liệu
    nào ⇒ vẫn là bản sao trần (không ghi sổ), nhưng đã thấy engine thì thiếu thư mục là thiếu THẬT."""
    ma, out, da_ghi, so = chay(_cay(tmp_path, engine=vi_tri), [dict(RW)], "--khong-mang")
    assert ma == 1 and "→ BROKEN" in out and "KHÔNG ĐO ĐƯỢC — engine vắng" not in out
    assert "không thấy" in out and "retraction_watch" in out, "BROKEN phải nói đã tìm thư mục ở đâu"
    assert da_ghi is ghi_so
    assert _nhan(so) == ("broken" if ghi_so else "active")


@pytest.mark.parametrize("vi_tri, ghi_so", [("long", True), ("anh_em", False)])
def test_engine_co_mat_kho_con_tuoi_thi_do_duoc_va_khoe(chay, tmp_path, vi_tri, ghi_so):
    ma, out, da_ghi, so = chay(_cay(tmp_path, engine=vi_tri, kho_rw=True), [dict(RW)], "--khong-mang")
    assert ma == 0 and "KHÔNG ĐO ĐƯỢC" not in out
    assert "🟢 SỔ NGUỒN: 1 active khoẻ ·" in out
    assert da_ghi is ghi_so and _nhan(so) == "active"


def test_kho_qua_chu_ky_van_ha_degraded_tren_may_that(chay, tmp_path):
    repo = _cay(tmp_path, engine="long", kho_rw=True, goc_du_lieu=True)
    kho = repo / "medical-ebm-automation" / "data" / "retraction_watch"
    cu = time.time() - 40 * 86400
    for p in (kho / "retraction_watch.csv", kho):
        os.utime(p, (cu, cu))
    ma, out, da_ghi, so = chay(repo, [dict(RW, last_success_at=None)], "--khong-mang")
    assert ma == 1 and "→ DEGRADED" in out and "ngày tuổi > chu kỳ 31ng" in out
    assert "🟠 SỔ NGUỒN: 0 active · 1 degraded/broken · 0 not-covered" in out, "không có nguồn ⚪ thì dòng tổng như cũ"
    assert da_ghi and _nhan(so) == "degraded"


def test_nguon_file_trong_git_mat_thi_van_broken_tren_ban_sao_tran(chay, tmp_path):
    """⚪ chỉ dành cho nguồn trỏ vào ENGINE. Nguồn file nằm trong phần git track mà mất là lỗi thật ở mọi cây."""
    trong_git = dict(RW, id="SRC-900", name="Nguồn file trong git", endpoint_or_url="data/kho-trong-git/")
    ma, out, da_ghi, _ = chay(_cay(tmp_path), [trong_git], "--khong-mang")
    assert ma == 1 and "SRC-900" in out and "→ BROKEN" in out
    assert "KHÔNG ĐO ĐƯỢC — engine vắng" not in out and not da_ghi


# ── Nhãn có sẵn trong sổ: không che, không leo thang ────────────────────────────────────────────────────

def test_nhan_degraded_co_san_khong_bi_che_va_khong_leo_thanh_broken(chay, tmp_path):
    """Sổ đã ghi degraded (đo thật ở cây chính) thì bản sao trần vẫn nêu — đó là lời của SỔ. Nhưng không
    được leo thành broken bằng luật «quá 2 chu kỳ»: mốc `last_success_at` của nguồn file suy từ chính thư
    mục đang vắng, không làm tươi được ở đây."""
    cu = dict(RW, status="degraded", last_success_at="2020-01-01")
    ma, out, da_ghi, so = chay(_cay(tmp_path), [cu], "--khong-mang")
    assert ma == 1 and "SRC-003" in out and "→ DEGRADED" in out and "nhãn của SỔ" in out
    assert "→ BROKEN" not in out and "KHÔNG ĐO ĐƯỢC — engine vắng" in out
    assert "active khoẻ" not in out and "0 active" in out
    assert not da_ghi and _nhan(so) == "degraded"


# ── Phiên Cloud: cùng luật ──────────────────────────────────────────────────────────────────────────────

def test_cloud_mot_repo_khong_engine_la_khong_do_duoc(chay, tmp_path):
    ma, out, da_ghi, _ = chay(_cay(tmp_path), [dict(RW)], "--khong-mang", cloud=True)
    assert ma == 0 and "KHÔNG ĐO ĐƯỢC — engine vắng" in out and "BROKEN" not in out
    assert not da_ghi and "phiên Cloud" in out


def test_cloud_da_noi_engine_ma_thieu_nen_rut_bai_van_broken(chay, tmp_path):
    """Trên Cloud «bản sao trần» chỉ xét EBM-Dashboards/EBM_MASTER: engine lồng có mặt vẫn là bản sao trần,
    nhưng đã có engine thì thiếu thư mục Retraction Watch là thiếu THẬT (chưa chạy nap_nen_rut_bai_cloud)."""
    ma, out, da_ghi, _ = chay(_cay(tmp_path, engine="long"), [dict(RW)], "--khong-mang", cloud=True)
    assert ma == 1 and "→ BROKEN" in out and "KHÔNG ĐO ĐƯỢC — engine vắng" not in out
    assert not da_ghi


# ── Hai phép dò là của ban_sao_tran.py, và mọi chỗ trong tệp dùng CÙNG một gốc ──────────────────────────

def test_hai_phep_do_uy_quyen_cho_ban_sao_tran(monkeypatch, tmp_path):
    mod = _nap()
    goi: list[tuple] = []
    monkeypatch.setattr(mod, "GOC", tmp_path)
    monkeypatch.setattr(mod._bst_sh, "ban_sao_git_tran", lambda repo: goi.append(("tran", repo)) or True)
    monkeypatch.setattr(mod._bst_sh, "duong_goc", lambda ten, repo: goi.append((ten, repo)))
    assert mod.la_ban_sao_tran() is True and mod._goc_engine() is None
    assert goi == [("tran", tmp_path), ("medical-ebm-automation", tmp_path)]


def test_duong_file_va_moc_thanh_cong_theo_goc_engine_luc_goi(monkeypatch, tmp_path):
    mod = _nap()
    repo = _cay(tmp_path, engine="anh_em", kho_rw=True)
    monkeypatch.setattr(mod, "GOC", repo)
    kho = repo.parent / "medical-ebm-automation" / "data" / "retraction_watch"
    assert mod._duong_file("medical-ebm-automation/data/retraction_watch/") == kho
    assert mod.lay_thanh_cong_that("SRC-003") is not None, "mốc chạy thật của SRC-003 phải đọc từ CÙNG gốc engine"
    monkeypatch.setattr(mod, "GOC", _cay(tmp_path / "khac"))
    assert mod.lay_thanh_cong_that("SRC-003") is None


# ── Bảng điểm thăm không chứa mục chết ──────────────────────────────────────────────────────────────────

def test_moi_diem_tham_la_nguon_api_trong_so():
    """Nhánh thăm chỉ chạy cho `access: api`. Mục `DIEM_THAM` trỏ vào nguồn kiểu khác là mục CHẾT: trông như
    được thăm mà không bao giờ được thăm (SRC-020 kcb.vn, `html-watch`, nằm đó từ 22/09 tới 30/09/2026)."""
    mod = _nap()
    so = {s["id"]: s for s in json.loads((GOC / "data" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    la = sorted(sid for sid in mod.DIEM_THAM if sid not in so)
    assert not la, f"DIEM_THAM có mã không tồn tại trong sổ nguồn: {la}"
    chet = sorted(sid for sid in mod.DIEM_THAM if so[sid]["access"] != "api")
    assert not chet, (f"DIEM_THAM có mục không bao giờ được thăm (không phải access=api): "
                      f"{[(sid, so[sid]['access']) for sid in chet]}")


def test_thuc_tham_dung_moi_muc_cua_bang_diem_tham(monkeypatch, tmp_path):
    """Đo HÀNH VI: chạy `main()` trên bản sao sổ thật với `_tham` ghi lại lời gọi — mọi mục của bảng (trừ
    nguồn đang not-covered, vốn bị bỏ qua có chủ ý) phải thật sự được thăm, không thừa không thiếu."""
    mod = _nap()
    so = tmp_path / "sources.json"
    so.write_bytes((GOC / "data" / "sources.json").read_bytes())
    du = json.loads(so.read_text(encoding="utf-8"))
    da_tham: list[str] = []
    monkeypatch.setattr(mod, "SO", so)
    monkeypatch.setattr(mod, "_tham", lambda url: da_tham.append(url) or mod.OK)
    monkeypatch.setattr(mod, "lay_thanh_cong_that", lambda sid: None)
    monkeypatch.setattr(sys, "argv", ["sources_health", "--khong-ghi", "--im-khi-on"])
    mod.main()
    mong_doi = [mod.DIEM_THAM[s["id"]] for s in du["sources"]
                if s["id"] in mod.DIEM_THAM and s["status"] != "not-covered"]
    assert mong_doi, "sổ thật không còn nguồn nào có điểm thăm — test đang đo nhầm chỗ"
    assert da_tham == mong_doi, "bảng điểm thăm có mục không được thăm (hoặc thăm thừa)"
