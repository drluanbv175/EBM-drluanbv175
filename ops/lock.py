#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Khoá ghi dùng chung cho mọi công cụ đụng SỔ/STATE — LÔ 0 PHA 2 (15/08/2026).

Vì sao: hai phiên Claude (hoặc hai máy qua OneDrive) từng ghi đè lẫn nhau trên
cây dùng chung — hiểm hoạ đã ghi thành memory riêng. `surveillance_scan.py` đã
có khoá nội bộ chứng minh chạy được (`gianh_khoa`/`tra_khoa`: pid+host+mốc giờ,
hết hạn 30'); module này đóng gói ĐÚNG mẫu đó thành API dùng lại cho
`ops/orchestrator.py` và công cụ mới. KHÔNG thay khoá nội bộ của
surveillance_scan (nguyên tắc T4 — không đập thứ đang chạy tốt).

Thuần stdlib — chạy được bằng python3 hệ thống lẫn venv (bài học BH05).

Dùng:
    from ops.lock import Khoa, KhoaBanRon
    with Khoa("EBM-Dashboards/.quet.lock"):
        ...                       # vùng ghi — tự trả khoá kể cả khi lỗi
    # hoặc điều khiển tay:
    k = Khoa(duong_dan);  k.gianh() -> bool;  k.tra()

Tự kiểm: python3 ops/lock.py --self-test
"""
from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Khoá quá tuổi này coi như MỒ CÔI (tiến trình chết không kịp trả) và được
# chiếm lại. 30 phút = đúng ngưỡng surveillance_scan đang dùng.
HAN_GIAY = 30 * 60


class KhoaBanRon(RuntimeError):
    """Khoá đang thuộc về tiến trình khác còn sống trong hạn."""


class Khoa:
    def __init__(self, duong_dan: str | Path, han_giay: int = HAN_GIAY) -> None:
        self.duong = Path(duong_dan)
        self.han_giay = han_giay
        self._cua_minh = False
        self._token = None  # (pid, epoch) đã ghi lúc giành — dùng để tự-xác-nhận trước khi xoá

    # ------------------------------------------------------------------
    def _doc(self) -> dict:
        try:
            return json.loads(self.duong.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def ai_giu(self) -> dict:
        """Trả thông tin chủ khoá hiện tại (rỗng nếu không ai giữ)."""
        return self._doc()

    def gianh(self) -> bool:
        """Thử giành khoá. True = được; False = người khác đang giữ trong hạn.

        Dùng O_CREAT|O_EXCL để việc TẠO file là nguyên tử — hai tiến trình cùng
        lúc chỉ một bên thắng; bên thua chỉ được chiếm lại khi khoá đã QUÁ HẠN.
        """
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        pid = os.getpid()
        epoch = time.time()
        noi_dung = json.dumps({
            "pid": pid,
            "host": socket.gethostname(),
            "luc": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "epoch": epoch,
        })
        try:
            fd = os.open(self.duong, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            cu = self._doc()
            tuoi = time.time() - float(cu.get("epoch", 0))
            if tuoi < self.han_giay:
                return False
            # Khoá mồ côi → chiếm lại, ghi đè có chủ ý (không xoá-rồi-tạo để
            # thu hẹp cửa sổ đua giữa hai bên cùng phát hiện mồ côi).
            self.duong.write_text(noi_dung, encoding="utf-8")
            self._cua_minh = True
            self._token = (pid, epoch)
            return True
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(noi_dung)
        self._cua_minh = True
        self._token = (pid, epoch)
        return True

    def tra(self) -> None:
        """Trả khoá — chỉ xoá khi chính mình đang giữ (không phá khoá người khác).

        Tự xác nhận nội dung TRÊN ĐĨA vẫn đúng token đã ghi lúc giành trước khi
        unlink — không tin suông cờ `_cua_minh` trong bộ nhớ. Lý do: nếu tiến
        trình này giữ khoá QUÁ han_giay (vd một bước B4 chậm hơn dự kiến), một
        tiến trình khác có thể đã coi khoá là mồ côi và chiếm lại — lúc đó
        unlink vô điều kiện sẽ xoá NHẦM khoá của bên đang giữ hợp lệ, đúng thứ
        module này sinh ra để ngăn (BH: tự-xác-nhận trước-xoá, 2026-09-08)."""
        if self._cua_minh:
            try:
                if self._token is not None:
                    hien_tai = self._doc()
                    if (hien_tai.get("pid"), hien_tai.get("epoch")) != self._token:
                        self._cua_minh = False
                        self._token = None
                        return
                self.duong.unlink()
            except OSError:
                pass
            self._cua_minh = False
            self._token = None

    # ------------------------------------------------------------------
    def __enter__(self) -> "Khoa":
        if not self.gianh():
            chu = self.ai_giu()
            raise KhoaBanRon(
                f"khoá {self.duong.name} đang do pid={chu.get('pid')}@{chu.get('host')} "
                f"giữ từ {chu.get('luc')} — chờ hoặc kiểm tra tiến trình đó")
        return self

    def __exit__(self, *_bo_qua) -> None:
        self.tra()


# ---------------------------------------------------------------------------
def _self_test() -> int:
    import tempfile
    goc = Path(tempfile.mkdtemp(prefix="khoa-test-"))
    p = goc / "thu.lock"
    loi = 0

    k1 = Khoa(p)
    assert k1.gianh(), "giành lần đầu phải được"
    k2 = Khoa(p)
    if k2.gianh():
        print("✗ khoá thứ hai giành ĐƯỢC trong khi khoá 1 còn sống — SAI")
        loi += 1
    else:
        print("✓ khoá thứ hai bị chặn khi khoá 1 còn trong hạn")
    k1.tra()
    assert not p.exists(), "trả khoá phải xoá file"
    print("✓ trả khoá xoá file")

    # Khoá mồ côi: ghi mốc epoch cũ 31 phút → bên mới phải chiếm lại được.
    p.write_text(json.dumps({"pid": 1, "host": "x", "epoch": time.time() - 31 * 60}),
                 encoding="utf-8")
    k3 = Khoa(p)
    if k3.gianh():
        print("✓ chiếm lại khoá mồ côi quá hạn 30'")
        k3.tra()
    else:
        print("✗ KHÔNG chiếm lại được khoá mồ côi — SAI")
        loi += 1

    # Context manager: bận phải nổ KhoaBanRon, không im lặng.
    k4 = Khoa(p)
    k4.gianh()
    try:
        with Khoa(p):
            pass
        print("✗ context manager KHÔNG nổ khi khoá bận — SAI")
        loi += 1
    except KhoaBanRon:
        print("✓ context manager nổ KhoaBanRon khi bận")
    k4.tra()

    # Tự-xác-nhận trước-xoá: A giữ khoá quá hạn (mô phỏng bước chậm), B chiếm
    # lại đúng thiết kế mồ côi — A gọi tra() SAU đó KHÔNG được xoá khoá của B.
    k5 = Khoa(p)
    assert k5.gianh(), "k5 giành ban đầu phải được"
    gia = json.loads(p.read_text(encoding="utf-8"))
    gia["epoch"] = time.time() - 31 * 60  # giả lập k5 đã giữ quá 31 phút
    p.write_text(json.dumps(gia), encoding="utf-8")
    k6 = Khoa(p)
    assert k6.gianh(), "k6 phải chiếm lại được khoá của k5 (đã quá hạn)"
    token_k6 = k6._token
    k5.tra()  # k5 KHÔNG còn biết mình đã bị chiếm lại — tra() phải tự nhận ra
    con = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    if con is not None and (con.get("pid"), con.get("epoch")) == token_k6:
        print("✓ tra() của khoá đã-bị-chiếm-lại KHÔNG xoá khoá hiện hành của bên khác")
    else:
        print("✗ tra() của khoá đã-bị-chiếm-lại đã XOÁ/GHI ĐÈ NHẦM khoá của bên khác — SAI")
        loi += 1
    k6.tra()
    assert not p.exists(), "k6 tự trả khoá của chính mình phải xoá file"

    print("🟢 lock self-test ĐẠT" if not loi else f"🔴 {loi} lỗi")
    return 1 if loi else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print(__doc__)
