#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`rebuild_router()` không báo lỗi khi máy thiếu plugin mà sổ khai nói máy này KHÔNG cần (01/10/2026) — ngoại tuyến.

Bối cảnh: catalog router cần đủ 9 plugin (hằng `PLUGIN_IDS` của build_catalog.py), nhưng máy Windows chỉ được khai 4 —
`sync/plugin-manifest.json` ghi codex · humanizer · openmed-skills · meta-pipe · pubmed-search là `can_o_may: [Mac, Cloud]`.
build_catalog.py ở đó ném «Plugin thiếu trong cache» ⇒ `rebuild_router` trả 1 ⇒ hook SessionStart in
«⚠ Đồng bộ Claude–Codex còn lỗi» ở MỌI phiên Windows dù nối skill đạt. Bản vá: bỏ qua dựng catalog (giữ bản đã commit, không
dựng bản thiếu đè lên) CHỈ khi MỌI plugin thiếu đều được sổ khai xác nhận không cần ở máy này. Mọi trường hợp còn lại —
thiếu plugin máy này ĐƯỢC KHAI là cần, plugin vắng trong sổ khai, `can_o_may` rỗng, không đọc được dữ kiện — vẫn chạy
build_catalog.py và fail-closed. Bằng chứng «đã gọi» là tệp đánh dấu do script giả ghi (không suy từ mã thoát).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dong_bo_skill_claude_codex as DB  # noqa: E402

CAN_DU = ("a@x", "b@x", "c@x")          # 3 plugin giả mà router «cần»


def _dung(tmp_path, monkeypatch, *, cai=(), khai=None, may="Windows", ma_router=None, so_khai_raw=None,
          installed_raw=None, exit_code=1):
    """Dựng cây tạm: nguồn router giả + HOME giả + sổ khai giả. Trả (source_root, marker)."""
    source_root = tmp_path / "sync" / "skills"
    scripts = source_root / DB.ROUTER_NAME / "scripts"
    scripts.mkdir(parents=True)
    marker = tmp_path / "da-goi.marker"
    if ma_router is None:
        ma_router = f"PLUGIN_IDS = {CAN_DU!r}\n"
    (scripts / "build_catalog.py").write_text(
        ma_router + f"from pathlib import Path\nPath({str(marker)!r}).write_text('x')\nraise SystemExit({exit_code})\n",
        encoding="utf-8")
    home = tmp_path / "home"
    (home / ".claude" / "plugins").mkdir(parents=True)
    if installed_raw is None:
        bang = {}
        for pid in cai:
            thu_muc = tmp_path / "cache" / pid
            thu_muc.mkdir(parents=True)
            bang[pid] = [{"installPath": str(thu_muc)}]
        installed_raw = json.dumps({"version": 2, "plugins": bang})
    (home / ".claude" / "plugins" / "installed_plugins.json").write_text(installed_raw, encoding="utf-8")
    so_khai = tmp_path / "plugin-manifest.json"
    if so_khai_raw is None:
        so_khai_raw = json.dumps({"plugin": {pid: {"can_o_may": can} for pid, can in (khai or {}).items()}})
    so_khai.write_text(so_khai_raw, encoding="utf-8")
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr(DB, "SO_KHAI", so_khai)
    monkeypatch.setattr(DB, "_ten_may", lambda: may)
    monkeypatch.setattr(DB, "co_codex_tren_may", lambda: False)
    return source_root, marker


def test_thieu_het_plugin_ma_so_khai_noi_may_nay_khong_can_thi_bo_qua_ma_thoat_0(tmp_path, monkeypatch, capsys):
    """Ca thật trên Windows: thiếu plugin khai `[Mac, Cloud]` ⇒ 0, KHÔNG chạy build_catalog.py, nói rõ vì sao."""
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",),
                                khai={"a@x": ["Mac", "Windows"], "b@x": ["Mac", "Cloud"], "c@x": ["Mac", "Cloud"]})
    rc = DB.rebuild_router(source_root, quiet=False)
    ra = capsys.readouterr().out
    assert rc == 0
    assert not marker.exists(), "build_catalog.py KHÔNG được chạy — chạy sẽ dựng bản thiếu đè catalog đầy đủ đã commit"
    assert "⚪" in ra and "b@x" in ra and "c@x" in ra and "a@x" not in ra.split("(")[1], ra


def test_installpath_da_chet_van_tinh_la_thieu(tmp_path, monkeypatch, capsys):
    """Mục có trong installed_plugins.json nhưng `installPath` trỏ thư mục không còn (cache bị dọn) là THIẾU — đúng định nghĩa
    của build_catalog.py tầng ba. Đoán «có mục là có» sẽ coi `b@x` là đang cài và chạy build_catalog.py vô ích."""
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",), khai={"a@x": ["Windows"], "b@x": ["Mac"], "c@x": ["Mac"]},
                                installed_raw=json.dumps({"plugins": {
                                    "a@x": [{"installPath": str(tmp_path)}],
                                    "b@x": [{"installPath": str(tmp_path / "khong-con")}]}}))
    assert DB.rebuild_router(source_root, quiet=False) == 0
    ra = capsys.readouterr().out
    assert not marker.exists() and "b@x" in ra and "c@x" in ra, ra


def test_im_lang_khi_quiet_nhu_hook(tmp_path, monkeypatch, capsys):
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",),
                                khai={"a@x": ["Windows"], "b@x": ["Mac"], "c@x": ["Mac"]})
    assert DB.rebuild_router(source_root, quiet=True) == 0
    cap = capsys.readouterr()
    assert cap.out == "" and cap.err == "", "hook chạy với --im-khi-on: thành công phải im lặng"
    assert not marker.exists()


def test_thieu_plugin_ma_may_nay_duoc_khai_la_can_thi_van_chay_va_fail_closed(tmp_path, monkeypatch):
    """Mất thật (máy ĐƯỢC KHAI là cần `b@x`) ⇒ build_catalog.py vẫn chạy; mã thoát của nó được giữ nguyên (1)."""
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x", "c@x"),
                                khai={"a@x": ["Windows"], "b@x": ["Mac", "Windows"], "c@x": ["Windows"]})
    rc = DB.rebuild_router(source_root, quiet=True)
    assert marker.exists(), "thiếu plugin máy này ĐƯỢC KHAI là cần phải tới build_catalog.py, không bị bỏ qua"
    assert rc == 1


def test_thieu_lan_loai_khong_can_va_loai_can_thi_khong_bo_qua(tmp_path, monkeypatch):
    """`b@x` không cần nhưng `c@x` CẦN ⇒ không được bỏ qua chỉ vì MỘT phần plugin thiếu là hợp lệ."""
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",),
                                khai={"a@x": ["Windows"], "b@x": ["Mac"], "c@x": ["Windows", "Mac"]})
    assert DB.rebuild_router(source_root, quiet=True) == 1
    assert marker.exists()


def test_plugin_vang_trong_so_khai_thi_khong_bo_qua(tmp_path, monkeypatch):
    """Chưa ai khai ý định cho `c@x` ⇒ «không biết» ⇒ không được coi là «không cần»."""
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",), khai={"a@x": ["Windows"], "b@x": ["Mac"]})
    assert DB.rebuild_router(source_root, quiet=True) == 1
    assert marker.exists()


@pytest.mark.parametrize("can", [[], None, "Mac", {"Mac": True}])
def test_can_o_may_rong_hoac_sai_kieu_thi_khong_bo_qua(tmp_path, monkeypatch, can):
    khai = {"a@x": ["Windows"], "b@x": can, "c@x": ["Mac"]}
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",), khai=None,
                                so_khai_raw=json.dumps({"plugin": {p: ({"can_o_may": c} if c is not None else {})
                                                                   for p, c in khai.items()}}))
    assert DB.rebuild_router(source_root, quiet=True) == 1
    assert marker.exists()


def test_may_la_mac_thi_cung_bo_thieu_phai_chay(tmp_path, monkeypatch):
    """Cùng bộ thiếu nhưng đứng ở Mac (nơi được khai là cần) ⇒ chạy: quyết định theo TÊN MÁY, không theo bộ plugin."""
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",), may="Mac",
                                khai={"a@x": ["Mac", "Windows"], "b@x": ["Mac", "Cloud"], "c@x": ["Mac", "Cloud"]})
    assert DB.rebuild_router(source_root, quiet=True) == 1
    assert marker.exists()


def test_khong_thieu_gi_thi_chay_binh_thuong(tmp_path, monkeypatch):
    source_root, marker = _dung(tmp_path, monkeypatch, cai=CAN_DU, khai={p: ["Mac"] for p in CAN_DU}, exit_code=0)
    assert DB.rebuild_router(source_root, quiet=True) == 0
    assert marker.exists()


def test_so_khai_hong_hoac_vang_thi_khong_bo_qua(tmp_path, monkeypatch):
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",), so_khai_raw="{không phải json")
    assert DB.rebuild_router(source_root, quiet=True) == 1
    assert marker.exists()


def test_installed_plugins_json_hong_thi_khong_bo_qua(tmp_path, monkeypatch):
    """Không đọc được cache ⇒ không biết thiếu gì ⇒ để build_catalog.py tự kết luận."""
    source_root, marker = _dung(tmp_path, monkeypatch, installed_raw="{hong",
                                khai={p: ["Mac"] for p in CAN_DU})
    assert DB.rebuild_router(source_root, quiet=True) == 1
    assert marker.exists()


def test_khong_doc_duoc_PLUGIN_IDS_thi_khong_bo_qua(tmp_path, monkeypatch):
    """PLUGIN_IDS không còn là literal đọc được bằng ast (vd sinh động) ⇒ () ⇒ không quyết được ⇒ chạy."""
    # Sổ khai khai MỌI plugin còn lại là «không cần ở Windows»: nếu mã tự suy danh sách khi ast bó tay thì nó sẽ bỏ qua
    # (mã 0, không gọi script) — ca này phải đỏ trước một đột biến như vậy.
    source_root, marker = _dung(tmp_path, monkeypatch, cai=("a@x",), ma_router="PLUGIN_IDS = tuple(['a@x', 'b@x'])\n",
                                khai={"a@x": ["Windows"], "b@x": ["Mac"], "c@x": ["Mac"]})
    assert DB.rebuild_router(source_root, quiet=True) == 1
    assert marker.exists()


def test_doc_PLUGIN_IDS_khong_chay_ma_cua_build_catalog(tmp_path):
    """Đọc danh sách bằng ast: mã có tác dụng phụ lúc import KHÔNG được chạy (chốt này chạy ở MỌI phiên mở máy)."""
    dau = tmp_path / "tac-dung-phu.marker"
    script = tmp_path / "build_catalog.py"
    script.write_text(f"from pathlib import Path\nPath({str(dau)!r}).write_text('x')\nPLUGIN_IDS = ('p@q',)\n",
                      encoding="utf-8")
    assert DB.plugin_id_router(script) == ("p@q",)
    assert not dau.exists()


def test_doc_duoc_PLUGIN_IDS_that_cua_repo_va_moi_plugin_deu_co_trong_so_khai():
    """Khóa hợp đồng trên TỆP THẬT: (1) hằng còn đọc được bằng ast — nếu ai đổi thành biểu thức động, tính năng này im lặng
    vô hiệu; (2) mỗi plugin router đều có mục trong sổ khai với `can_o_may` là danh sách không rỗng — thiếu mục thì «không
    biết» và nhánh bỏ qua không bao giờ kích hoạt (báo động giả quay lại)."""
    script = DB.DEFAULT_SOURCE / DB.ROUTER_NAME / "scripts" / "build_catalog.py"
    assert script.is_file(), f"nguồn router được git theo dõi phải có mặt ở mọi cây: {script}"
    ids = DB.plugin_id_router(script)
    assert len(ids) >= 9, f"không đọc được PLUGIN_IDS thật bằng ast: {ids}"
    muc = json.loads(DB.SO_KHAI.read_text(encoding="utf-8"))["plugin"]
    chua_khai = [p for p in ids if not (isinstance(muc.get(p), dict) and isinstance(muc[p].get("can_o_may"), list)
                                        and muc[p]["can_o_may"])]
    assert not chua_khai, f"plugin router chưa khai `can_o_may` trong sổ khai: {chua_khai}"
