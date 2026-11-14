#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GHI DẤU VẾT LƯỢT LỊCH cho tác vụ không có script riêng ghi log (14/11/2026).

VÌ SAO CÓ
=========
Cảm biến người chết `tools/kiem_lich_nen.py` chỉ canh được tác vụ để lại dấu vết MÁY-ĐỌC-ĐƯỢC. Tác vụ kỹ thuật tháng
`kiem-tra-hoan-thien-he-thong-thang` là một phiên agent thuần (không có script bash ghi log như bộ thu thập, không có
`chu_trinh_chung_cu --ghi-log` như tác vụ rút bài kho) ⇒ sổ kỳ vọng khai `dau_vet: khong-co` và cảm biến chỉ in
«⚪ không canh được» (đo 14/11/2026): lượt bị xoá/tắt/cắt ngang giữa chừng đều vô hình. Lượt lịch không ghi được dòng log
bằng `echo >>` (mỗi lệnh Bash phải được phép sẵn, không chuyển hướng), và không nên tự gõ dòng log bằng Write/Edit (mô hình
không biết giờ thật — dấu vết tự khai giờ là dấu vết giả).

LÀM GÌ
======
    python3 tools/ghi_dau_vet_lich.py <id tác vụ> --bat-dau      # lệnh ĐẦU TIÊN của lượt
    python3 tools/ghi_dau_vet_lich.py <id tác vụ> --ma <0|1|2>   # lệnh CUỐI CÙNG của lượt

Tra `sync/lich-nen-ky-vong.json`: tác vụ phải khai `dau_vet.loai = "log-ket-thuc"`, `dau_vet.ghi_boi =
"tools/ghi_dau_vet_lich.py"` và `dau_vet.path` nằm dưới `state/`. Nối MỘT dòng, giờ do MÁY lấy:
    ===== YYYY-MM-DD HH:MM:SS : BẮT ĐẦU <id>
    ===== YYYY-MM-DD HH:MM:SS : KẾT THÚC <id> (mã N)
— đúng khuôn `kiem_lich_nen._ket_thuc()` đọc. Lượt bị cắt ngang sau BẮT ĐẦU, trước KẾT THÚC ⇒ cảm biến báo 🔴 «lượt bị
cắt ngang». Đính chính 14/11/2026: nếu chính lệnh BẮT ĐẦU đầu tiên bị cắt (chưa áp quyền) thì tệp log KHÔNG tồn tại — vì
vậy sổ kỳ vọng khai thêm `dau_vet.tu_ngay`: từ mốc đó, máy CÓ bản chạy của tác vụ mà thiếu log ⇒ cảm biến báo 🔴 kỳ lỡ
(gãy ồn), không còn «⚪ không đọc được log» mãi mãi (gãy âm thầm).
`--ma`: 0 = mọi mảng sạch · 1 = có việc cho bác sĩ / đã tự sửa · 2 = có mảng KHÔNG đo được.

Rào (không giả dấu vết): chỉ ghi cho tác vụ tự khai `ghi_boi` là công cụ này — log của script thu thập
(`launchd_monthly.log`) hay log rút bài kho (do `chu_trinh_chung_cu` ghi) không bao giờ bị công cụ này ghi chen: một dòng
KẾT THÚC giả ở đó làm cảm biến người chết xanh giả cho kỳ không nổ.
Mã thoát: 0 = đã ghi · 2 = KHÔNG ghi (tác vụ chưa khai/khai sai, đường dẫn ngoài state/, lỗi ghi) — luôn in lý do.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path, PurePosixPath

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
TEN_CONG_CU = "tools/ghi_dau_vet_lich.py"


class KhongGhiLoi(Exception):
    """Không ghi dấu vết — kèm lý do in cho người đọc."""


def duong_log(tac_vu: str, goc: Path | None = None) -> Path:
    """Đường log của `tac_vu` theo sổ kỳ vọng; ném KhongGhiLoi khi tác vụ không giao cho công cụ này ghi.

    `goc` mặc định đọc `GOC` LÚC GỌI (không chốt lúc định nghĩa hàm) để test chạy `main` trên bản sao tạm — test gọi `main`
    trên repo thật mà rào hỏng sẽ GHI dòng KẾT THÚC giả vào log thật (đo được khi kiểm đột biến 14/11/2026)."""
    goc = GOC if goc is None else goc
    so = goc / "sync" / "lich-nen-ky-vong.json"
    try:
        khai = json.loads(so.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise KhongGhiLoi(f"không đọc được sync/lich-nen-ky-vong.json ({type(e).__name__})") from e
    tv = next((t for t in khai.get("tac_vu", []) if t.get("id") == tac_vu), None)
    if tv is None:
        raise KhongGhiLoi(f"tác vụ «{tac_vu}» không có trong sync/lich-nen-ky-vong.json")
    dv = tv.get("dau_vet") or {}
    if dv.get("loai") != "log-ket-thuc":
        raise KhongGhiLoi(f"«{tac_vu}» khai dấu vết loại «{dv.get('loai')}», không phải log-ket-thuc")
    if dv.get("ghi_boi") != TEN_CONG_CU:
        raise KhongGhiLoi(f"«{tac_vu}» không giao log cho {TEN_CONG_CU} (ghi_boi={dv.get('ghi_boi')!r}) — "
                          "không ghi chen log của chủ khác")
    p = PurePosixPath(str(dv.get("path", "")))
    if p.is_absolute() or not p.parts or p.parts[0] != "state" or ".." in p.parts or len(p.parts) < 2:
        raise KhongGhiLoi(f"«{tac_vu}» khai log ngoài state/: {dv.get('path')!r}")
    return goc.joinpath(*p.parts)


def ghi(tac_vu: str, ma: int | None, goc: Path | None = None, luc: dt.datetime | None = None) -> Path:
    """Nối dòng BẮT ĐẦU (ma=None) hoặc KẾT THÚC (ma=0/1/2) vào log của tác vụ. Trả đường log đã ghi."""
    goc = GOC if goc is None else goc
    tep = duong_log(tac_vu, goc)
    luc = luc or dt.datetime.now()
    dong = (f"===== {luc:%Y-%m-%d %H:%M:%S} : BẮT ĐẦU {tac_vu}\n" if ma is None
            else f"===== {luc:%Y-%m-%d %H:%M:%S} : KẾT THÚC {tac_vu} (mã {ma})\n")
    try:
        tep.parent.mkdir(parents=True, exist_ok=True)
        with tep.open("a", encoding="utf-8", newline="\n") as f:
            f.write(dong)
    except OSError as e:
        raise KhongGhiLoi(f"không ghi được {tep}: {e}") from e
    return tep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ghi dòng BẮT ĐẦU/KẾT THÚC của lượt lịch vào log khai ở sync/lich-nen-ky-vong.json")
    ap.add_argument("tac_vu", help="id tác vụ lịch (khoá `id` trong sync/lich-nen-ky-vong.json)")
    nhom = ap.add_mutually_exclusive_group(required=True)
    nhom.add_argument("--bat-dau", action="store_true", help="dòng BẮT ĐẦU — lệnh đầu tiên của lượt")
    nhom.add_argument("--ma", type=int, choices=(0, 1, 2),
                      help="dòng KẾT THÚC: 0 sạch · 1 có việc cho bác sĩ/đã tự sửa · 2 có mảng KHÔNG đo được")
    a = ap.parse_args(argv)
    try:
        tep = ghi(a.tac_vu, None if a.bat_dau else a.ma)
    except KhongGhiLoi as e:
        print(f"⚪ KHÔNG ghi dấu vết lượt lịch: {e}", file=sys.stderr)
        return 2
    try:
        hien = tep.relative_to(GOC).as_posix()  # GOC đọc lúc gọi — cùng gốc ghi() vừa dùng
    except ValueError:
        hien = tep.as_posix()
    print(f"✓ Đã ghi dòng {'BẮT ĐẦU' if a.bat_dau else f'KẾT THÚC (mã {a.ma})'} vào {hien}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
