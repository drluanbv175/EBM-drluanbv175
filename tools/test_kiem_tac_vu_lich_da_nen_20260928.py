#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28/09/2026 (N3): SKILL tác vụ lịch phải chạy được trên Mac lẫn Windows, hoặc khai rõ CHỈ-MAC khi gọi bash. Ngoại tuyến."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import kiem_tac_vu_lich_da_nen as K  # noqa: E402

DA = ('NỀN TẢNG: macOS + Windows. THƯ MỤC\n- macOS: "$HOME/x"\n- Windows: "%USERPROFILE%\\x"\n'
      "Trên Windows đổi lệnh: `python3` → `py -3`; tệp tạm vào state/, không dùng `/tmp`.\n")
MAC = "NỀN TẢNG: CHỈ CHẠY TRÊN MAC — gọi bash. Windows: DỪNG ngay.\n"


def _ma(vb: str) -> list[str]:
    return sorted({x[:2] for x in K.kiem_van_ban(vb)})


def test_hai_khoi_chuan_dat():
    assert _ma(DA + "python3 tools/a.py") == []
    assert _ma(MAC + "cd x && bash scripts/weekly_safety.sh") == []


def test_neo_may_va_tmp_bi_bat():
    # Ghép lúc chạy: nguyên văn đường dẫn máy trong mã sẽ bị chính BH06/BH55 chặn.
    nha_mac, nha_linux = "/" + "Users/bacsi", "/" + "home/bacsi/"
    assert _ma(DA + f'cd "{nha_mac}/Library/CloudStorage/x"') == ["L1"]
    assert _ma(DA + f"ghi {nha_linux}x") == ["L1"]
    assert _ma(DA + "--json-report /tmp/tuan.json") == ["L1"]


def test_khoi_nen_tang_thieu_hoac_trung():
    assert _ma("python3 tools/a.py") == ["L2"]
    assert _ma(DA + MAC + "bash a.sh") == ["L2"]
    assert _ma(DA.replace("- Windows:", "Windows:") + "x") == ["L2"]
    assert _ma(DA.replace("py -3", "py") + "x") == ["L2"]
    assert _ma(MAC.replace("Windows: DỪNG", "Windows bỏ qua") + "bash a.sh") == ["L2"]


def test_bash_phai_chi_mac_va_chi_mac_phai_co_bash():
    assert _ma(DA + "bash scripts/monthly_update.sh") == ["L3"]
    assert _ma(MAC + "python3 tools/a.py") == ["L4"]


def test_repo_that_dat_va_thu_muc_rong(tmp_path, capsys):
    kq = K.kiem_thu_muc()
    assert len(kq) >= 14 and not any(kq.values()), {k: v for k, v in kq.items() if v}
    assert K.main([str(tmp_path)]) == 2
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "SKILL.md").write_text("---\nname: x\n---\npython3 a.py\n", encoding="utf-8", newline="\n")
    assert K.main([str(tmp_path)]) == 1 and "🔴 x" in capsys.readouterr().out
