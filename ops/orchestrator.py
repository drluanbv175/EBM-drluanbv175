#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ORCHESTRATOR MỘT CỬA cho dây chuyền chứng cứ — LÔ 4 PHA 2 (15/08/2026).

Driver MỎNG: gọi các hiện thân A2→B5 ĐÚNG THỨ TỰ, dừng đúng chỗ khi một bước
FAIL, ghi log máy đọc được — và KHÔNG chứa một dòng logic y khoa nào. Mọi phán
đoán nằm trong từng công cụ (chúng đã có cổng riêng); mọi quyết định lâm sàng
nằm ở bác sĩ (Cổng A/B, I4).

Vì sao B1 (dựng dashboard) là "PHIÊN LÀM VIỆC" chứ không phải lệnh: dựng nội
dung lâm sàng cần skill `cap-nhat-chung-cu-y-khoa` + bác sĩ chốt phạm vi —
tự động hoá bước đó là vi phạm BH10. Orchestrator dừng lại và in "việc cần
phiên" thay vì làm bừa.

Các bước máy chạy được (mỗi bước = một hiện thân đã có, T4 — không viết lại):
  A2  quét ứng viên        surveillance_scan.py --topic <t>
  A3  ưu tiên toàn kho     uu_tien_cap_nhat.py            (chạy 1 lần, không theo topic)
  A4  sổ xác minh nguồn    so_xac_minh_nguon.py --quet <dashboard mới nhất của chủ đề>
  B2  cổng liêm chính      verify_dashboard.py <dashboard>   (exit 0/1/2 — BH48)
  B4  BỘ NĂM               xuat_goi_cap_nhat.py (CHỈ khi --xuat — nặng, sinh 5 sản phẩm)
  B5  hàng chờ bác sĩ      trinh_muc_can_duyet.py

Log: `logs/<run_id>.jsonl` — mỗi dòng {run_id, buoc, lenh, rc, giay, luc}.
Resume: `--resume <run_id>` đọc log cũ, BỎ QUA bước đã rc=0, chạy lại phần còn lại.
Khoá: `ops/lock.py` trên `EBM-Dashboards/.orchestrator.lock` (không đụng khoá
riêng `.quet.lock` của A2 — hai tầng độc lập có chủ ý).
Cursor: thuộc A2 (`EBM-Dashboards/.quet-cursor.json`) — orchestrator KHÔNG ghi
(lệch đề bài "state/cursors.json" CÓ GHI LÝ DO: cursor đã sống ở chỗ của chủ
ghi nó từ LÔ 1, dời đi là tạo 2 nguồn sự thật).

Mã thoát: 0 = mọi bước chạy đều sạch · 1 = có bước FAIL NỘI DUNG (rc=1)
· 2 = hạ tầng (khoá bận / rc=2 / không chạy được lệnh).

Dùng:
  python3 ops/orchestrator.py --topic "Suy tim" --dry-run
  python3 ops/orchestrator.py --topic "Suy tim" --online --xuat
  python3 ops/orchestrator.py --resume 20260815T070102-suy-tim
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[1]
DASH = GOC / "EBM-Dashboards"
LOGS = GOC / "logs"
PY = sys.executable  # BH05: không gọi "python3" cứng — Windows không có


def _nap_khoa():
    spec = importlib.util.spec_from_file_location("ops_lock", GOC / "ops" / "lock.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["ops_lock"] = m
    spec.loader.exec_module(m)
    return m


def _slug(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "toan-kho"


def _dashboards_cua_chu_de(topic: str) -> list[Path]:
    """MỌI lát cắt của chủ đề, xếp theo NGÀY trong tên file (mới nhất cuối).

    Vì sao trả danh sách chứ không «bản mới nhất»: một chủ đề có nhiều LÁT CẮT
    (SuyTim_TongHop · TienLuongSuyTim…) — chúng BỔ SUNG nhau, không thay nhau
    (BH30). Chọn một bản «mới nhất» xuyên lát cắt là lặp đúng lỗi đã vá 12/08.
    Cùng một lát cắt nhiều phiên bản thì chỉ giữ bản ngày mới nhất.
    """
    tu = [t for t in _slug(topic).split("-") if len(t) > 2]
    khop = [p for p in DASH.glob("WebDashboard_*.html")
            if all(t in _slug(p.name) for t in tu)]

    def _ngay(p: Path) -> str:
        m = re.search(r"(\d{8})", p.name)
        return m.group(1) if m else "00000000"

    # nhóm theo LÁT CẮT = tên bỏ ngày; mỗi lát cắt lấy phiên bản mới nhất
    lat_cat: dict[str, Path] = {}
    for p in sorted(khop, key=_ngay):
        lat_cat[re.sub(r"_?\d{8}", "", p.name)] = p
    return sorted(lat_cat.values(), key=_ngay)


def ke_hoach(topic: str | None, online: bool, xuat: bool) -> list[dict]:
    """Dựng danh sách bước. Mỗi bước: {buoc, lenh (list) | phien (str)}."""
    vd = str(DASH / "tools" / "verify_dashboard.py")
    buoc: list[dict] = []
    if topic:
        buoc.append({"buoc": "A2-quet", "lenh": [PY, str(DASH / "tools" / "surveillance_scan.py"),
                                                 "--topic", topic]})
    buoc.append({"buoc": "A3-uu-tien", "lenh": [PY, str(GOC / "tools" / "uu_tien_cap_nhat.py")]})
    cac_db = _dashboards_cua_chu_de(topic) if topic else []
    for db in cac_db:  # TỪNG lát cắt — chúng bổ sung nhau, không thay nhau (BH30)
        lat = re.sub(r"^WebDashboard_EBM_VanDeCuThe_|_?\d{8}|\.html$", "", db.name)
        buoc.append({"buoc": f"A4-so-xac-minh[{lat}]",
                     "lenh": [PY, str(GOC / "tools" / "so_xac_minh_nguon.py"),
                              "--quet", str(db), "--vong", "1"]})
        # `--strict-sources` ĐI KÈM `--online` (vá 02/09/2026, BH96). Đây là ĐÚNG lỗi mà
        # bác sĩ đã vá một lần ở `tools/xuat_goi_cap_nhat.py:298` ngày 11/08 — nhóm luật
        # MẠNH NHẤT (chặn `decision='apply'` trên gradeLevel na/low, hoặc chỉ dựa
        # `Consensus`) chỉ bật khi có cờ này; thiếu nó thì nhóm luật ấy NẰM IM và cổng vẫn
        # in "PASS". Tuyến `xuat_goi_cap_nhat` đã được vá, nhưng tuyến NÀY (đường
        # «cập nhật chứng cứ chủ đề X», dựng 15/08) sinh sau và lặp lại y nguyên lỗi cũ.
        # Cùng họ với `return` sớm 12/08 vốn che 73 mục `apply` nguy hiểm trên 47 dashboard.
        # An toàn về mã thoát: verify_dashboard trả 3 khi CHẶN XUẤT; nhánh `rc != 0` bên
        # dưới bắt được và DỪNG ngay ở B2, nên gói bị chặn KHÔNG bao giờ đi tiếp sang B4.
        # GIỚI HẠN CÒN LẠI, nói rõ: chạy KHÔNG `--online` thì vẫn không có strict-sources —
        # giữ đúng khuôn đã chứng minh ở xuat_goi_cap_nhat, không tự mở rộng sang nhánh
        # offline khi chưa kiểm được `verify_dashboard.py` (cây EBM-Dashboards ngoài git).
        buoc.append({"buoc": f"B2-cong-liem-chinh[{lat}]",
                     "lenh": [PY, vd, str(db)]
                             + (["--online", "--strict-sources"] if online else [])})
        if xuat:
            buoc.append({"buoc": f"B4-bo-nam[{lat}]",
                         "lenh": [PY, str(GOC / "tools" / "xuat_goi_cap_nhat.py"), str(db)]
                                 + (["--online"] if online else [])})
    if topic and not cac_db:
        buoc.append({"buoc": "B1-dung-dashboard",
                     "phien": f"chủ đề «{topic}» CHƯA có dashboard — cần PHIÊN skill "
                              f"cap-nhat-chung-cu-y-khoa (bác sĩ chốt phạm vi; BH10)"})
    buoc.append({"buoc": "B5-hang-cho-bac-si",
                 "lenh": [PY, str(GOC / "tools" / "trinh_muc_can_duyet.py")]})
    return buoc


def main() -> int:
    ap = argparse.ArgumentParser(description="Orchestrator một cửa A2→B5")
    ap.add_argument("--topic", help="một chủ đề trong watchlist; bỏ trống = việc toàn kho")
    ap.add_argument("--dry-run", action="store_true", help="chỉ in kế hoạch, không chạy")
    ap.add_argument("--online", action="store_true", help="B2/B4 chạy chế độ --online")
    ap.add_argument("--xuat", action="store_true", help="chạy cả B4 BỘ NĂM (nặng)")
    ap.add_argument("--resume", metavar="RUN_ID", help="chạy tiếp run cũ, bỏ qua bước đã rc=0")
    a = ap.parse_args()

    run_id = a.resume or f"{time.strftime('%Y%m%dT%H%M%S')}-{_slug(a.topic or '')}"
    log_f = LOGS / f"{run_id}.jsonl"
    da_xong: set[str] = set()
    if a.resume:
        if not log_f.exists():
            print(f"🔴 không thấy log run {a.resume}")
            return 2
        for dong in log_f.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(dong)
                if r.get("rc") == 0:
                    da_xong.add(r["buoc"])
            except ValueError:
                continue
        # resume không truyền topic → đọc lại từ log cũ
        if not a.topic:
            for dong in log_f.read_text(encoding="utf-8").splitlines():
                r = json.loads(dong)
                if r.get("topic"):
                    a.topic = r["topic"]
                    break

    cac_buoc = ke_hoach(a.topic, a.online, a.xuat)
    print(f"KẾ HOẠCH run {run_id} — {len(cac_buoc)} bước"
          + (f" (bỏ qua {len(da_xong)} đã xong)" if da_xong else ""))
    for b in cac_buoc:
        dau = "⏭" if b["buoc"] in da_xong else "▸"
        print(f"  {dau} {b['buoc']}: " + (" ".join(b["lenh"][1:]) if "lenh" in b
                                          else f"[PHIÊN NGƯỜI] {b['phien']}"))
    if a.dry_run:
        print("(dry-run — chưa chạy gì, chưa giành khoá)")
        return 0

    Khoa = _nap_khoa().Khoa
    KhoaBanRon = _nap_khoa().KhoaBanRon
    LOGS.mkdir(exist_ok=True)
    tong_rc = 0
    try:
        with Khoa(DASH / ".orchestrator.lock"):
            with log_f.open("a", encoding="utf-8") as lf:
                for b in cac_buoc:
                    if b["buoc"] in da_xong:
                        continue
                    if "phien" in b:
                        print(f"⏸ {b['buoc']}: {b['phien']}")
                        lf.write(json.dumps({"run_id": run_id, "topic": a.topic,
                                             "buoc": b["buoc"], "rc": None,
                                             "phien": b["phien"],
                                             "luc": time.strftime("%FT%T")},
                                            ensure_ascii=False) + "\n")
                        continue
                    t0 = time.time()
                    print(f"\n══ {b['buoc']} ══")
                    rc = subprocess.run(b["lenh"], cwd=GOC).returncode
                    lf.write(json.dumps({"run_id": run_id, "topic": a.topic,
                                         "buoc": b["buoc"], "lenh": b["lenh"][1:],
                                         "rc": rc, "giay": round(time.time() - t0, 1),
                                         "luc": time.strftime("%FT%T")},
                                        ensure_ascii=False) + "\n")
                    lf.flush()
                    if rc == 2:
                        print(f"🔴 {b['buoc']} FAIL HẠ TẦNG (rc=2) — dừng; chạy lại khi "
                              f"mạng ổn: --resume {run_id}")
                        return 2
                    if rc != 0:
                        # rc=1 nội dung: A3/B5 chỉ là báo cáo (rc=1 nghĩa CÓ mục cần đọc,
                        # không phải hỏng) — đi tiếp; B2 rc=1 là gói SAI — dừng.
                        tong_rc = max(tong_rc, 1)
                        if b["buoc"].startswith("B2"):
                            print(f"🔴 {b['buoc']} FAIL NỘI DUNG — sửa gói rồi "
                                  f"--resume {run_id}")
                            return 1
    except KhoaBanRon as e:
        print(f"🔴 {e}")
        return 2
    print(f"\n{'🟠 xong, CÓ mục cần bác sĩ đọc' if tong_rc else '🟢 xong, sạch'} "
          f"— log: logs/{run_id}.jsonl")
    return tong_rc


if __name__ == "__main__":
    raise SystemExit(main())
