"""Lịch nền phải GÃY ỒN, không gãy âm thầm (14/11/2026).

Đo 14/11/2026: (1) `python3 tools/quyen_lich_nen.py` báo 🔴 «máy chưa áp: Bash(python3 tools/xuat_goi_cap_nhat.py … --khong-endnote)»
— lượt tháng 01/12 sẽ bị cắt ngang ở bước gói duyệt mà bộ lập lịch vẫn ghi «succeeded», bước 1–4 đã chạy dở (watermark dịch);
(2) `python3 tools/kiem_lich_nen.py`: tác vụ `kiem-tra-hoan-thien-he-thong-thang` khai `dau_vet: khong-co` ⇒ «⚪ không canh
được»; (3) sổ xác minh nguồn 97 mục chưa/hết hạn, không có nhịp làm mới định kỳ.

Khoá: bước 0 tiền kiểm của tác vụ tháng (quyền chỉ của lệnh lượt đó — `--tac-vu`), dấu vết BẮT ĐẦU/KẾT THÚC của
tác vụ kỹ thuật qua `tools/ghi_dau_vet_lich.py`, mọi tác vụ lịch đều canh được, mọi lệnh đã khai quyền.
Đính chính 14/11/2026 (người duyệt độc lập): (3) là tiền đề SAI — owner tái kiểm sổ là tác vụ `kiem-rut-bai-kho-thang`; bước
4b đã gỡ (đọc mã 2 thành «nguồn đã rút» là đỏ giả cho đính chính đã ký). Khoá mới ở `test_lich_nen_dinh_chinh_20261114.py`.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import ghi_dau_vet_lich as G  # noqa: E402
import kiem_lich_nen as K  # noqa: E402
import quyen_lich_nen as Q  # noqa: E402

TV_THANG = "cap-nhat-thang-ebm"
TV_GOI = "goi-duyet-tuan-ebm"
TV_KY_THUAT = "kiem-tra-hoan-thien-he-thong-thang"
SKILL_DIR = REPO / "sync" / "scheduled-tasks"


def _skill(ten: str) -> str:
    return (SKILL_DIR / ten / "SKILL.md").read_text(encoding="utf-8")


def _khai_quyen() -> dict:
    return json.loads((REPO / "sync" / "quyen-lich-nen.json").read_text(encoding="utf-8"))


def _ky_vong() -> dict:
    return json.loads((REPO / "sync" / "lich-nen-ky-vong.json").read_text(encoding="utf-8"))


# ── quyen_lich_nen --tac-vu: chỉ xét lệnh của CHÍNH lượt ─────────────────────────────────────────────────────────────

KHAI_HAI = {
    "nen_tang": "darwin",
    "tac_vu": {
        "a": {"lenh": ["python3 tools/a.py"], "khong_chay": [], "ghi": []},
        "b": {"lenh": ["python3 tools/b.py"], "khong_chay": [], "ghi": []},
    },
}


def _goc_hai(tmp_path: Path, allow: list[str]) -> Path:
    for ten, lenh in (("a", "python3 tools/a.py"), ("b", "python3 tools/b.py")):
        (tmp_path / "sync" / "scheduled-tasks" / ten).mkdir(parents=True)
        (tmp_path / "sync" / "scheduled-tasks" / ten / "SKILL.md").write_text(f"`{lenh}`\n", encoding="utf-8", newline="\n")
    (tmp_path / "sync" / "quyen-lich-nen.json").write_text(json.dumps(KHAI_HAI), encoding="utf-8", newline="\n")
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.local.json").write_text(json.dumps({"permissions": {"allow": allow}}),
                                                              encoding="utf-8", newline="\n")
    return tmp_path


def test_tac_vu_chi_xet_quy_tac_cua_tac_vu_neu_ten(tmp_path):
    goc = _goc_hai(tmp_path, ["Bash(python3 tools/a.py)"])
    assert Q.kiem(goc, nen_tang="darwin")["thieu_may"] == ["Bash(python3 tools/b.py)"]  # đo cả tập: có thiếu
    assert Q.kiem(goc, nen_tang="darwin", tac_vu=["a"]) == {"khong_do": [], "thieu_khai": [], "thieu_may": []}
    assert Q.kiem(goc, nen_tang="darwin", tac_vu=["b"])["thieu_may"] == ["Bash(python3 tools/b.py)"]


def test_tac_vu_lenh_skill_chua_khai_van_bao_trong_pham_vi(tmp_path):
    goc = _goc_hai(tmp_path, ["Bash(python3 tools/a.py)", "Bash(python3 tools/b.py)"])
    (goc / "sync" / "scheduled-tasks" / "a" / "SKILL.md").write_text("`python3 tools/a.py`\n`python3 tools/moi.py`\n",
                                                                     encoding="utf-8", newline="\n")
    assert Q.kiem(goc, nen_tang="darwin", tac_vu=["a"])["thieu_khai"] == [("a", "python3 tools/moi.py")]
    assert Q.kiem(goc, nen_tang="darwin", tac_vu=["b"])["thieu_khai"] == []


@pytest.mark.parametrize("ds", [["khong-ton-tai"], ["a", "go-sai"], []])
def test_tac_vu_chua_khai_la_khong_do_khong_bao_gio_du(tmp_path, ds):
    goc = _goc_hai(tmp_path, ["Bash(python3 tools/a.py)", "Bash(python3 tools/b.py)"])
    kq = Q.kiem(goc, nen_tang="darwin", tac_vu=ds)
    assert kq["khong_do"] and not kq["thieu_khai"] and not kq["thieu_may"]


@pytest.mark.parametrize("kq, ma", [
    ({"khong_do": [], "thieu_khai": [], "thieu_may": []}, 0),
    ({"khong_do": [], "thieu_khai": [], "thieu_may": ["Bash(python3 tools/a.py)"]}, 1),
    ({"khong_do": ["tác vụ chưa khai"], "thieu_khai": [], "thieu_may": []}, 2),
])
def test_main_tac_vu_chuyen_dung_danh_sach_va_ma_thoat(monkeypatch, kq, ma):
    goi: list = []
    monkeypatch.setattr(Q, "kiem", lambda **kw: goi.append(kw) or kq)
    assert Q.main(["--tac-vu", f"{TV_THANG}, {TV_GOI}"]) == ma
    assert goi == [{"tac_vu": [TV_THANG, TV_GOI]}]


# ── ghi_dau_vet_lich: dấu vết đọc được bằng CHÍNH cảm biến, không giả log chủ khác ────────────────────────────────────

SO_KY = {"cua_so_ngay": 40, "tac_vu": [
    {"id": "tv", "cron": "0 18 3 * *", "tu_ngay": "2026-11-01", "grace_gio": 30,
     "dau_vet": {"loai": "log-ket-thuc", "path": "state/tv.log", "ghi_boi": "tools/ghi_dau_vet_lich.py"}},
    {"id": "chu-khac", "cron": "0 18 3 * *", "tu_ngay": "2026-11-01", "grace_gio": 30,
     "dau_vet": {"loai": "log-ket-thuc", "path": "state/chu-khac.log"}},
    {"id": "ngoai-state", "cron": "0 18 3 * *", "tu_ngay": "2026-11-01", "grace_gio": 30,
     "dau_vet": {"loai": "log-ket-thuc", "path": "medical-ebm-automation/data/archive/launchd_monthly.log",
                 "ghi_boi": "tools/ghi_dau_vet_lich.py"}},
    {"id": "leo-thu-muc", "cron": "0 18 3 * *", "tu_ngay": "2026-11-01", "grace_gio": 30,
     "dau_vet": {"loai": "log-ket-thuc", "path": "state/../alerts/x.md", "ghi_boi": "tools/ghi_dau_vet_lich.py"}},
    {"id": "khong-co", "cron": "0 18 3 * *", "tu_ngay": "2026-11-01", "grace_gio": 30, "dau_vet": {"loai": "khong-co"}},
]}


def _goc_ky(tmp_path: Path) -> Path:
    (tmp_path / "sync").mkdir()
    (tmp_path / "sync" / "lich-nen-ky-vong.json").write_text(json.dumps(SO_KY), encoding="utf-8", newline="\n")
    return tmp_path


def test_bat_dau_ket_thuc_doc_duoc_bang_cam_bien(tmp_path):
    goc = _goc_ky(tmp_path)
    bd, kt = dt.datetime(2026, 11, 3, 18, 1, 5), dt.datetime(2026, 11, 3, 18, 40, 0)
    tep = G.ghi("tv", None, goc, bd)
    assert G.ghi("tv", 1, goc, kt) == tep == goc / "state" / "tv.log"
    assert K._moc(tep, "BẮT ĐẦU") == [bd]
    assert K._ket_thuc(tep) == [kt]
    assert tep.read_bytes().count(b"\r") == 0
    so = {"cua_so_ngay": 40, "tac_vu": [SO_KY["tac_vu"][0]]}
    kq = K.kiem(dt.datetime(2026, 11, 14, 9, 0), so, goc)
    assert kq["ok"] == 1 and kq["phat_hien"] == []


@pytest.mark.parametrize("tac_vu", ["chu-khac", "ngoai-state", "leo-thu-muc", "khong-co", "khong-khai"])
def test_tu_choi_ghi_log_khong_giao_hoac_ngoai_state(tmp_path, tac_vu):
    goc = _goc_ky(tmp_path)
    with pytest.raises(G.KhongGhiLoi):
        G.ghi(tac_vu, 0, goc)
    assert not (goc / "state").exists() and not (goc / "medical-ebm-automation").exists() and not (goc / "alerts").exists()


def test_main_voi_so_ky_vong_that_khong_ghi_chen_log_chu_khac(tmp_path, monkeypatch):
    """Log rút bài kho do chu_trinh_chung_cu ghi, log tháng do script launchd ghi — dòng KẾT THÚC giả ở đó làm cảm biến
    xanh giả. Chạy trên BẢN SAO TẠM của sổ kỳ vọng THẬT: rào hỏng thì test ghi vào tmp, không bao giờ vào state/ thật."""
    (tmp_path / "sync").mkdir()
    (tmp_path / "sync" / "lich-nen-ky-vong.json").write_bytes((REPO / "sync" / "lich-nen-ky-vong.json").read_bytes())
    monkeypatch.setattr(G, "GOC", tmp_path)
    assert G.main(["kiem-rut-bai-kho-thang", "--ma", "0"]) == 2
    assert G.main(["cap-nhat-thang-ebm", "--ma", "0"]) == 2
    assert G.main(["tac-vu-khong-ton-tai", "--bat-dau"]) == 2
    assert not (tmp_path / "state").exists() and not (tmp_path / "medical-ebm-automation").exists()
    assert G.main([TV_KY_THUAT, "--bat-dau"]) == 0 and G.main([TV_KY_THUAT, "--ma", "2"]) == 0
    tep = tmp_path / "state" / "kiem-tra-hoan-thien-he-thong.log"
    assert len(K._moc(tep, "BẮT ĐẦU")) == 1 and len(K._ket_thuc(tep)) == 1
    assert tep.read_text(encoding="utf-8").rstrip().endswith(f"KẾT THÚC {TV_KY_THUAT} (mã 2)")


def test_cam_bien_noi_ro_luot_bi_cat_ngang(tmp_path):
    goc = _goc_ky(tmp_path)
    so = {"cua_so_ngay": 40, "tac_vu": [SO_KY["tac_vu"][0]]}
    G.ghi("tv", 0, goc, dt.datetime(2026, 10, 3, 18, 30))  # tệp tồn tại từ lượt tháng trước
    G.ghi("tv", None, goc, dt.datetime(2026, 11, 3, 18, 2))  # kỳ 03/11: nổ nhưng không tới KẾT THÚC
    kq = K.kiem(dt.datetime(2026, 11, 14, 9, 0), so, goc)
    assert [(p["muc"], p["uu"]) for p in kq["phat_hien"]] == [("lo", 0)]
    assert "cắt ngang" in kq["phat_hien"][0]["thong_diep"] and "03/11 18:02" in kq["phat_hien"][0]["thong_diep"]
    (goc / "state" / "tv.log").write_text("===== 2026-10-03 18:30:00 : KẾT THÚC tv (mã 0)\n", encoding="utf-8", newline="\n")
    kq = K.kiem(dt.datetime(2026, 11, 14, 9, 0), so, goc)
    assert "KHÔNG có dấu vết nào" in kq["phat_hien"][0]["thong_diep"]


# ── trên repo thật ─────────────────────────────────────────────────────────────────────────────────────────────────────


def test_moi_tac_vu_lich_deu_canh_duoc():
    """Tác vụ khai `khong-co` là tác vụ chết mà không ai biết — cảm biến chỉ in ⚪."""
    for tv in _ky_vong()["tac_vu"]:
        assert (tv.get("dau_vet") or {}).get("loai") not in (None, "khong-co"), tv["id"]
    ky_thuat = next(t for t in _ky_vong()["tac_vu"] if t["id"] == TV_KY_THUAT)
    assert ky_thuat["dau_vet"]["loai"] == "log-ket-thuc"
    assert G.duong_log(TV_KY_THUAT, REPO) == REPO / "state" / "kiem-tra-hoan-thien-he-thong.log"


def _dong_thi_hanh(van_ban: str, lenh: str) -> list[int]:
    """Chỉ số các dòng có `lenh` đứng TRONG backtick (dòng thi hành, không phải lời bình nhắc tên)."""
    return [i for i, d in enumerate(van_ban.splitlines()) if f"`{lenh}`" in d]


def test_tac_vu_ky_thuat_ghi_bat_dau_dau_luot_va_ket_thuc_cuoi_luot():
    sk = _skill(TV_KY_THUAT)
    dong = sk.splitlines()
    bd = _dong_thi_hanh(sk, f"python3 tools/ghi_dau_vet_lich.py {TV_KY_THUAT} --bat-dau")
    kt = _dong_thi_hanh(sk, f"python3 tools/ghi_dau_vet_lich.py {TV_KY_THUAT} --ma <0|1|2>")
    assert bd and kt, "SKILL kỹ thuật thiếu lệnh ghi dấu vết BẮT ĐẦU/KẾT THÚC"
    viec = next(i for i, d in enumerate(dong) if d.startswith("VIỆC CẦN KIỂM MỖI LẦN CHẠY"))
    cuoi = next(i for i, d in enumerate(dong) if d.startswith("BƯỚC CUỐI BẮT BUỘC"))
    assert bd[0] < viec, "dòng BẮT ĐẦU phải được dặn trước các mảng kiểm"
    assert cuoi > next(i for i, d in enumerate(dong) if d.startswith("BÁO CÁO:")), "bước ghi KẾT THÚC phải ở cuối lượt"
    assert "ĐẦU TIÊN" in dong[bd[0]] and "CUỐI CÙNG" in "\n".join(dong[kt[0] - 1:kt[0] + 1])


def _khoi_buoc(sk: str, dau: str, ke: str) -> str:
    i = sk.index(dau)
    return sk[i:sk.index(ke, i)]


def test_tac_vu_thang_tien_kiem_buoc_0_truoc_buoc_1_va_dung_khi_thieu_quyen():
    sk = _skill(TV_THANG)
    lenh_q = f"python3 tools/quyen_lich_nen.py --tac-vu {TV_THANG},{TV_GOI}"
    i_q = sk.index(f"`{lenh_q}`")
    i_k = sk.index("`python3 tools/kiem_lich_nen.py`")
    i_1 = sk.index("`python3 tools/sync_safety_check.py`")
    assert i_q < i_k < i_1, "tiền kiểm phải chạy TRƯỚC bước 1"
    khoi = _khoi_buoc(sk, "0. TIỀN KIỂM", "\n1. ")
    for cum in ("mã 1", "mã 2", "DỪNG LƯỢT NGAY", "KHÔNG chạy bước 1", "alerts/<YYYY-MM-DD>.md", "--ap-dung"):
        assert cum in khoi, cum
    # tên trong --tac-vu là tác vụ có thật trong tệp khai, và phủ đúng các SKILL lượt tháng sẽ thi hành
    khai = _khai_quyen()["tac_vu"]
    ds = re.search(r"--tac-vu (\S+)`", sk).group(1).split(",")
    assert all(t in khai for t in ds) and set(ds) == {TV_THANG, TV_GOI}
    assert f"sync/scheduled-tasks/{TV_GOI}/SKILL.md" in sk


@pytest.mark.parametrize("ten", [TV_THANG, TV_GOI, TV_KY_THUAT])
def test_moi_lenh_bash_cua_skill_da_khai_quyen(ten):
    """Lượt tháng thi hành SKILL tháng + SKILL quy trình gói duyệt; tác vụ kỹ thuật thi hành SKILL của nó."""
    tv = _khai_quyen()["tac_vu"][ten]
    phu = list(tv["lenh"]) + list(tv["khong_chay"])
    thieu = [c for c in Q.lenh_trong_skill(_skill(ten)) if not Q.duoc_phu(c, phu)]
    assert thieu == [], f"{ten}: lệnh chưa khai ở sync/quyen-lich-nen.json — lượt lịch sẽ bị cắt ngang: {thieu}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
