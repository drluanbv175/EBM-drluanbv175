#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hồi quy phát hiện #36 (26/09/2026): `xuat_trang_thai_cloud.py` ghi đè gương
`cloud-mirror/trang-thai-chung-cu.json` (đang track) bằng trạng thái RỖNG khi máy không
có EBM-Dashboards/ — tái lập thật 19.717 → 1.038 byte, mất bản sao 38 quyết định đã
duyệt, mã 0 — và không chốt pre-commit nào canh.

Hai tầng vá, test cả hai:
  (1) Công cụ: vắng EBM-Dashboards/ ⇒ KHÔNG ghi, in ⚪ (kể cả --im-khi-on), mã 2; chỉ
      ghi trạng thái rỗng khi có cờ tường minh `--ghi-du-rong`.
  (2) tools/kiem_o_nhiem_artifact.py: luật RIÊNG chặn gương đi XUỐNG
      (co_du_lieu_dashboard_that true→không-true, so_da_duyet.* có→null/lỗi đọc, rỗng);
      cho qua chiều LÊN và làm mới bình thường Mac↔Windows. Soi bản ĐÃ STAGE.

Không mạng; ba bộ đếm con bị thay bằng bản giả để test nhanh và không phụ thuộc máy.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _nap(ten: str, duong: Path):
    spec = importlib.util.spec_from_file_location(ten, duong)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ten] = mod
    spec.loader.exec_module(mod)
    return mod


XC = _nap("xuat_trang_thai_cloud_t20260926", HERE / "xuat_trang_thai_cloud.py")
K = _nap("kiem_o_nhiem_artifact_t20260926", HERE / "kiem_o_nhiem_artifact.py")

GUONG_THAT = {
    "sinh_luc": "2026-09-20T08:00:00",
    "may": "Mac",
    "co_du_lieu_dashboard_that": True,
    "bo_dem": {"do_tuoi_chung_cu": {"ma_thoat": 0, "stdout": "trung vị 40 ngày", "stderr": ""}},
    "so_da_duyet": {
        "quyet_dinh_da_duyet": {"quyet_dinh": [{"ma": "QD-%02d" % i} for i in range(38)]},
        "mau_thuan_da_duyet": {"mau_thuan": []},
    },
}
# Đúng hình dạng công cụ sinh ra trên máy KHÔNG có EBM-Dashboards/ (xay_trang_thai()).
GUONG_RONG = {
    "sinh_luc": "2026-09-26T10:00:00",
    "may": "Cloud",
    "co_du_lieu_dashboard_that": False,
    "bo_dem": {"do_tuoi_chung_cu": {"ma_thoat": 0, "stdout": "⚪ chưa có dữ liệu", "stderr": ""}},
    "so_da_duyet": {"quyet_dinh_da_duyet": None, "mau_thuan_da_duyet": None},
}


def _j(d) -> str:
    return json.dumps(d, ensure_ascii=False, indent=2) + "\n"


# ───────────────────────── (1) công cụ xuat_trang_thai_cloud ─────────────────────────

def _gan_duong_tam(monkeypatch, tmp_path: Path, co_dash: bool) -> Path:
    dash = tmp_path / "EBM-Dashboards"
    if co_dash:
        dash.mkdir()
        (dash / "quyet-dinh-da-duyet.json").write_text('{"quyet_dinh": [{"ma": "QD-01"}]}',
                                                       encoding="utf-8")
    mdir = tmp_path / "cloud-mirror"
    monkeypatch.setattr(XC, "DASH", dash)
    monkeypatch.setattr(XC, "MIRROR_DIR", mdir)
    monkeypatch.setattr(XC, "MIRROR_FILE", mdir / "trang-thai-chung-cu.json")
    monkeypatch.setattr(XC, "_chay_bo_dem",
                        lambda ten, doi: {"ma_thoat": 0, "stdout": "gia", "stderr": ""})
    monkeypatch.setattr(XC, "_ten_may", lambda: "May-Test")
    return mdir / "trang-thai-chung-cu.json"


def _chay_xc(monkeypatch, *co: str) -> int:
    monkeypatch.setattr(sys, "argv", ["xuat_trang_thai_cloud.py", *co])
    return XC.main()


def test_vang_dash_khong_ghi_giu_nguyen_guong_ma_2(monkeypatch, tmp_path, capsys):
    f = _gan_duong_tam(monkeypatch, tmp_path, co_dash=False)
    f.parent.mkdir()
    f.write_text(_j(GUONG_THAT), encoding="utf-8")
    truoc = f.read_bytes()
    rc = _chay_xc(monkeypatch, "--im-khi-on")
    out = capsys.readouterr().out
    assert rc == 2, out
    assert f.read_bytes() == truoc, "gương giá trị thật bị ghi đè khi máy thiếu EBM-Dashboards/"
    assert "⚪" in out and "KHÔNG GHI" in out, "phải in ⚪ kể cả dưới --im-khi-on"


def test_vang_dash_khong_tao_tep_moi(monkeypatch, tmp_path, capsys):
    f = _gan_duong_tam(monkeypatch, tmp_path, co_dash=False)
    rc = _chay_xc(monkeypatch)
    assert rc == 2
    assert not f.exists()


def test_co_dash_van_ghi_ma_0(monkeypatch, tmp_path, capsys):
    f = _gan_duong_tam(monkeypatch, tmp_path, co_dash=True)
    rc = _chay_xc(monkeypatch)
    assert rc == 0, capsys.readouterr().out
    d = json.loads(f.read_text(encoding="utf-8"))
    assert d["co_du_lieu_dashboard_that"] is True
    assert d["so_da_duyet"]["quyet_dinh_da_duyet"] == {"quyet_dinh": [{"ma": "QD-01"}]}


def test_ghi_du_rong_la_lua_chon_tuong_minh(monkeypatch, tmp_path, capsys):
    f = _gan_duong_tam(monkeypatch, tmp_path, co_dash=False)
    rc = _chay_xc(monkeypatch, "--ghi-du-rong")
    assert rc == 0
    assert json.loads(f.read_text(encoding="utf-8"))["co_du_lieu_dashboard_that"] is False


def test_in_thu_khong_ghi_du_vang_dash(monkeypatch, tmp_path, capsys):
    f = _gan_duong_tam(monkeypatch, tmp_path, co_dash=False)
    rc = _chay_xc(monkeypatch, "--in-thu")
    assert rc == 0
    assert not f.exists()
    assert '"co_du_lieu_dashboard_that": false' in capsys.readouterr().out


# ───────────────────────── (2) luật riêng trong kiem_o_nhiem_artifact ─────────────────────

def test_luat_chan_ha_cap_that_dung_du_lieu_tai_lap():
    loi = K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_THAT), _j(GUONG_RONG))
    s = " | ".join(loi)
    assert "co_du_lieu_dashboard_that ĐI LÙI" in s
    assert "so_da_duyet.quyet_dinh_da_duyet" in s
    assert "so_da_duyet.mau_thuan_da_duyet" in s


def test_luat_chan_rieng_co_du_lieu_true_sang_false():
    moi = copy.deepcopy(GUONG_THAT)
    moi["co_du_lieu_dashboard_that"] = False
    loi = K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_THAT), _j(moi))
    assert len(loi) == 1 and "co_du_lieu_dashboard_that" in loi[0], loi


def test_luat_chan_rieng_so_da_duyet_sang_null_hoac_loi_doc():
    moi = copy.deepcopy(GUONG_THAT)
    moi["so_da_duyet"]["quyet_dinh_da_duyet"] = None
    loi = K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_THAT), _j(moi))
    assert len(loi) == 1 and "quyet_dinh_da_duyet" in loi[0], loi
    moi["so_da_duyet"]["quyet_dinh_da_duyet"] = {"loi_doc": "JSONDecodeError: x"}
    assert K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_THAT), _j(moi))


def test_luat_chan_rong_hoac_json_hong():
    assert K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_THAT), "  \n")
    assert K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_THAT), '{"co_du_lieu_dashboard_that": tr')


def test_luat_cho_qua_chieu_len_va_lam_moi_binh_thuong():
    # rỗng → thật (máy vừa có dữ liệu): HOAN NGHÊNH.
    assert K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_RONG), _j(GUONG_THAT)) == []
    # Mac → Windows làm mới bình thường: vẫn true, sổ vẫn có (nội dung khác).
    moi = copy.deepcopy(GUONG_THAT)
    moi["may"] = "Windows"
    moi["sinh_luc"] = "2026-09-26T09:00:00"
    moi["so_da_duyet"]["mau_thuan_da_duyet"] = {"mau_thuan": [{"ma": "MT-01"}]}
    assert K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_THAT), _j(moi)) == []
    # rỗng → rỗng: không có gì để mất.
    assert K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_RONG), _j(GUONG_RONG)) == []
    # Bản cũ vốn không mang dữ liệu thật ⇒ bản mới rỗng cũng không làm mất gì (không
    # chặn ồn — một cổng ồn là cổng sẽ bị tắt; JSON hỏng là việc của chốt khác).
    assert K.soi_guong_cloud(K.GUONG_CLOUD, _j(GUONG_RONG), "") == []


def test_luat_chung_khong_bat_duoc_nen_can_luat_rieng():
    """Bằng chứng vì sao phải có luật riêng: soi_mot_file trả [] trên đúng diff này."""
    assert K.soi_mot_file(K.GUONG_CLOUD, _j(GUONG_THAT), _j(GUONG_RONG)) == []


def _repo_git_tam(tmp_path: Path, noi_dung_cu: str) -> Path:
    repo = tmp_path / "repo"
    (repo / "cloud-mirror").mkdir(parents=True)
    for lenh in (["git", "init", "-q"], ["git", "config", "user.email", "t@t.t"],
                 ["git", "config", "user.name", "t"]):
        subprocess.run(lenh, cwd=repo, check=True)
    (repo / K.GUONG_CLOUD).write_text(noi_dung_cu, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    return repo


def _chay_k(monkeypatch, repo: Path, *co: str) -> int:
    goc = K._git
    monkeypatch.setattr(K, "_git", lambda *args, cay=None: goc(*args, cay=repo))
    monkeypatch.setattr(K, "REPO", repo)
    monkeypatch.setattr(sys, "argv", ["kiem_o_nhiem_artifact.py", *co])
    return K.main()


def test_pre_commit_staged_chan_guong_ha_cap(monkeypatch, tmp_path, capsys):
    repo = _repo_git_tam(tmp_path, _j(GUONG_THAT))
    (repo / K.GUONG_CLOUD).write_text(_j(GUONG_RONG), encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    rc = _chay_k(monkeypatch, repo, "--staged")
    out = capsys.readouterr().out
    assert rc == 1, out
    assert "CHẶN COMMIT" in out and "cloud-mirror" in out


def test_pre_commit_staged_cho_qua_lam_moi_binh_thuong(monkeypatch, tmp_path, capsys):
    repo = _repo_git_tam(tmp_path, _j(GUONG_THAT))
    moi = copy.deepcopy(GUONG_THAT)
    moi["may"] = "Windows"
    (repo / K.GUONG_CLOUD).write_text(_j(moi), encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    rc = _chay_k(monkeypatch, repo, "--staged")
    assert rc == 0, capsys.readouterr().out


def test_pre_commit_soi_ban_da_stage_khong_phai_working_tree(monkeypatch, tmp_path, capsys):
    """Stage bản hạ cấp rồi khôi phục working tree: thứ VÀO COMMIT vẫn là bản hạ cấp."""
    repo = _repo_git_tam(tmp_path, _j(GUONG_THAT))
    f = repo / K.GUONG_CLOUD
    f.write_text(_j(GUONG_RONG), encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    f.write_text(_j(GUONG_THAT), encoding="utf-8")   # working tree trông «sạch»
    rc = _chay_k(monkeypatch, repo, "--staged")
    assert rc == 1, capsys.readouterr().out


def test_guong_that_trong_git_neu_co_cung_bi_bat():
    """Nếu repo có gương thật ở HEAD (máy thật), hạ cấp nó bằng đúng hình dạng máy thiếu
    dữ liệu sinh ra phải bị chặn. Không có (clone lạ) thì kiểm bằng fixture ở trên."""
    r = subprocess.run(["git", "show", "HEAD:" + K.GUONG_CLOUD], cwd=HERE.parent,
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return
    d = json.loads(r.stdout)
    if d.get("co_du_lieu_dashboard_that") is not True:
        return
    assert K.soi_guong_cloud(K.GUONG_CLOUD, r.stdout, _j(GUONG_RONG))
