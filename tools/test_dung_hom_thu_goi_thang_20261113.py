"""Hòm thư phải nhúng gói MỚI NHẤT kể cả khi gói tháng nằm ở tệp riêng `tuan-<W>-thang.md` (13/11/2026)."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("dht_gt", GOC / "tools" / "dung_hom_thu.py")
dht = importlib.util.module_from_spec(sp)
sys.modules["dht_gt"] = dht
sp.loader.exec_module(dht)


def _ghi(p: Path, mtime: int) -> None:
    p.write_text("# gói\n", encoding="utf-8")
    os.utime(p, (mtime, mtime))


def test_goi_thang_moi_hon_duoc_chon_du_ten_xep_truoc(tmp_path):
    _ghi(tmp_path / "tuan-2026-W46.md", 1_000)
    _ghi(tmp_path / "tuan-2026-W46-thang.md", 2_000)
    # sắp theo tên: «-thang» đứng TRƯỚC «.md» ⇒ cách cũ chọn nhầm W46.md
    assert sorted(tmp_path.glob("tuan-*.md"))[-1].name == "tuan-2026-W46.md"
    assert dht.chon_goi_moi_nhat(tmp_path).name == "tuan-2026-W46-thang.md"


def test_goi_tuan_moi_hon_van_duoc_chon(tmp_path):
    _ghi(tmp_path / "tuan-2026-W46-thang.md", 1_000)
    _ghi(tmp_path / "tuan-2026-W47.md", 2_000)
    assert dht.chon_goi_moi_nhat(tmp_path).name == "tuan-2026-W47.md"


def test_khong_co_goi(tmp_path):
    assert dht.chon_goi_moi_nhat(tmp_path) is None
