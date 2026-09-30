"""Vá 30/09/2026 (cùng họ BH136) — lượt ĐẾM của `uu_tien_cap_nhat` không được tiêu hạn mức dự phòng tính phí.

`uu_tien_cap_nhat` gọi bộ quét với `--khong-cursor` và ghi báo cáo vào thư mục TẠM (chỉ dùng số đếm). Từ 27/09 bộ quét
có sổ dự phòng tính phí, sổ này KHÔNG phụ thuộc `--khong-cursor` ⇒ lượt đếm tiêu trần 2 chủ đề/tuần của gói tuần và ghi
«đã trình» cho bài nằm ở thư mục tạm không ai đọc (bị lọc 400 ngày). Nay lệnh gọi kèm `--tran-du-phong 0`.
Offline: `subprocess.run` được thay bằng hàm ghi lại lệnh và tự viết một báo cáo tối thiểu.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_sp = importlib.util.spec_from_file_location("uu_tien_khong_tieu_du_phong_3009", ROOT / "tools" / "uu_tien_cap_nhat.py")
M = importlib.util.module_from_spec(_sp)
sys.modules["uu_tien_khong_tieu_du_phong_3009"] = M
_sp.loader.exec_module(M)


class _TuoiGia:
    @staticmethod
    def lau_chua_xem_lai():
        return [("A_20260101", 40)]


def test_luot_dem_goi_bo_quet_khong_con_tro_va_khong_leo_thang_du_phong(monkeypatch, tmp_path, capsys):
    ban_do = tmp_path / "giam-sat-chu-de.json"
    ban_do.write_text(json.dumps({"muc": {}}), encoding="utf-8", newline="\n")
    lenh_da_goi: list[list[str]] = []

    def chay_gia(lenh, **kw):
        lenh_da_goi.append([str(x) for x in lenh])
        dich = Path(lenh[lenh.index("--json-report") + 1])
        dich.write_text(json.dumps({"status": "PASS", "topics": []}), encoding="utf-8", newline="\n")
        return type("KQ", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(M, "BANDO", ban_do)
    monkeypatch.setattr(M, "_nap", lambda *a, **k: _TuoiGia)
    monkeypatch.setattr(M.subprocess, "run", chay_gia)
    monkeypatch.setattr(sys, "argv", ["uu_tien_cap_nhat.py"])
    assert M.main() == 0
    capsys.readouterr()
    (lenh,) = lenh_da_goi
    assert "--khong-cursor" in lenh, "lượt đếm không được đọc/ghi con trỏ dùng chung"
    assert lenh[lenh.index("--tran-du-phong") + 1] == "0", "lượt đếm không được leo thang dự phòng TÍNH PHÍ"
