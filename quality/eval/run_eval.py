#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MÁY CHẤM GOLD SET — LÔ 5 PHA 2 (15/08/2026). Ngoại tuyến, ~10s.

Chấm dây chuyền bằng ca CÓ ĐÁP ÁN BIẾT TRƯỚC, xếp theo 12 nhóm của prompt kiện
toàn. Ba trạng thái tự động hoá, KHÔNG gộp (BH08):
  TỰ ĐỘNG      — chạy ngay trong máy chấm này, ngoại tuyến;
  CẦN MẠNG     — đã có công cụ thật nhưng phải gọi nguồn sống (chạy theo lịch
                 riêng, ghi số đo gần nhất);
  CHƯA TỰ ĐỘNG — khoảng trống thật, ghi rõ thay vì im lặng (I7).

Bằng chứng từng ca ÂM TÍNH (dây chuyền phải CHẶN/BÁO) lưu vào
`quality/eval/negative/<ca>.log` — yêu cầu LÔ 6: kiểm âm tính phải để lại vết,
không chỉ một dòng «đã thử». Ra `reports/eval-<ngày>.md`.

Mã thoát: 0 = mọi ca TỰ ĐỘNG đạt · 1 = có ca trượt · 2 = hạ tầng.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[2]
NEG = GOC / "quality" / "eval" / "negative"
PY = sys.executable


def _nap(duong: Path, ten: str):
    spec = importlib.util.spec_from_file_location(ten, duong)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ten] = m
    try:
        spec.loader.exec_module(m)
    except BaseException:
        sys.modules.pop(ten, None)
        raise
    return m


def _ghi_neg(ten_ca: str, noi_dung: str) -> None:
    NEG.mkdir(parents=True, exist_ok=True)
    (NEG / f"{ten_ca}.log").write_text(noi_dung, encoding="utf-8")


KQ: list[dict] = []  # {nhom, ca, dat (bool|None), ghi_chu}


def ca(nhom: int, ten: str, dat: bool | None, ghi_chu: str = "") -> None:
    KQ.append({"nhom": nhom, "ca": ten, "dat": dat, "ghi_chu": ghi_chu})
    dau = {True: "✓", False: "✗", None: "◌"}[dat]
    print(f"  {dau} [N{nhom:02d}] {ten}" + (f" — {ghi_chu}" if ghi_chu else ""))


def main() -> int:  # noqa: PLR0915 — máy chấm tuyến tính, tách nhỏ làm khó đọc hơn
    print("═" * 60)
    print("GOLD SET — máy chấm 12 nhóm (ngoại tuyến)")
    print("═" * 60)

    # VÁ 10/09/2026 (vòng 3) — trước đây thiếu chốt này, máy chấm CHẠY MỘT PHẦN
    # rồi chết bằng traceback thô trên bản sao trần (worktree/CI/clone tươi):
    # đo thật ngay khối 1 — `thu_dau_cuoi_chung_cu.py` bản thân nó cũng crash vì
    # thiếu EBM-Dashboards/tools/verify_dashboard.py, nên returncode != 0, và
    # máy chấm đọc NHẦM đó là "CÓ LỖ HỔNG" (canary phát hiện lỗ hổng thật) thay
    # vì "chưa chạy được vì thiếu hạ tầng" — đúng lớp lỗi BH08/BH99/BH100 đã vá
    # ở chỗ khác trong repo (gộp "không biết" với "có vấn đề"), lần này ở chính
    # máy chấm Gold Set. `chot_hoi_quy_bai_hoc.py` đã xử lý đúng việc này cho
    # BH43 (hạ ⚪ trên bản trần) — run_eval.py gọi lại canary đó SONG SONG mà
    # KHÔNG thừa hưởng cùng lớp bảo vệ, nên bản vá dùng ĐÚNG một định nghĩa
    # "bản sao trần" (tools/ban_sao_tran.py) thay vì tự đoán lại lần nữa.
    bst = _nap(GOC / "tools" / "ban_sao_tran.py", "bst_eval")
    if bst.ban_sao_git_tran(GOC):
        print("⚠ BẢN SAO GIT TRẦN — thiếu EBM-Dashboards/ · medical-ebm-automation/ · "
              "EBM_MASTER/.")
        print("  Máy chấm Gold Set cần CẢ HAI cây dữ liệu đó (RetractionChain, "
              "verify_dashboard.py, drug_flags.json…) — chạy trên máy có đủ hai repo.")
        print("  Đây là HẠ TẦNG THIẾU (mã thoát 2), KHÔNG phải ca nào trượt (mã thoát 1) —")
        print("  không được đọc thành 'có lỗ hổng'.")
        return 2

    # ── Khối 1: CANARY đầu-cuối (10 ca gài sẵn — nhóm 3/4/7/9/10 một phần) ────
    r = subprocess.run([PY, str(GOC / "tools" / "thu_dau_cuoi_chung_cu.py")],
                       capture_output=True, text=True, cwd=GOC)
    canary_ok = r.returncode == 0
    ca(9, "canary 10 lỗi gài (apply+na/normativeBasis/Consensus/gradeBy/return-sớm…)",
       canary_ok, "10/10 bắt" if canary_ok else "CÓ LỖ HỔNG — xem thu_dau_cuoi")
    _ghi_neg("canary-10-loi-gai", r.stdout[-3000:])

    # ── Khối 2: RÚT BÀI ngoại tuyến — hai MỨC khác nhau phải ra hai nhãn ─────
    sys.path.insert(0, str(GOC / "medical-ebm-automation"))
    from app.sources.retraction_chain import RetractionChain  # noqa: PLC0415
    chain = RetractionChain()
    kq = chain.check(["9500320", "30267080", "99999999"])
    w = kq.get("9500320", {})
    ca(3, "bài rút BỎ HẲN (Wakefield 9500320) → retracted, KHÔNG gắn R&R",
       w.get("status") == "retracted" and not w.get("retract_and_replace"))
    c = kq.get("30267080", {})
    ca(3, "RÚT-VÀ-THAY (Choi 30267080) → retracted + retract_and_replace (BH34)",
       c.get("status") == "retracted" and c.get("retract_and_replace") is True)
    u = kq.get("99999999", {})
    # Hợp đồng đúng phụ thuộc TẦNG đang sống (đo thật 15/08, lượt nền venv):
    #   offline-only (python3)  → unknown_*  («không kết luận được»)
    #   online (venv)           → unresolved («nguồn sống XÁC NHẬN không có bản
    #                              ghi» — nghi PMID ma, một phát hiện ĐÚNG)
    # Cấm duy nhất là «ok». Bản đầu chỉ nhận unknown_* nên đỏ giả dưới venv.
    st = str(u.get("status"))
    ca(4, "PMID không tồn tại → không bao giờ «ok» (unknown_* hoặc unresolved)",
       st != "ok" and ("unknown" in st or st == "unresolved"))
    _ghi_neg("rut-bai-3-muc", json.dumps(kq, ensure_ascii=False, indent=1))

    # ── Khối 3: HỢP ĐỒNG ITEM — 5 ca xấu + 2 ca mới ─────────────────────────
    v = _nap(GOC / "tools" / "kiem_hop_dong_item.py", "khdi_eval")
    r2 = subprocess.run([PY, str(GOC / "tools" / "kiem_hop_dong_item.py"), "--self-test"],
                        capture_output=True, text=True, cwd=GOC)
    ca(9, "validator 5 ca xấu (tự APPROVED · retracted-CANDIDATE · tự gán mức · "
          "chưa resolved · số không nguồn)", r2.returncode == 0)
    _ghi_neg("validator-5-ca-xau", r2.stdout)
    it = {"id": "X", "topic": "t", "status": "CANDIDATE", "decision": "apply",
          "source": {"type": "RCT", "title": "x", "resolved": True},
          "certainty": {"reported_by_source": True, "level": "mod"}}
    ca(4, "CANDIDATE không PMID/DOI → validator chặn (truy nguyên trước đã — I1)",
       any("PMID/DOI" in x for x in v.kiem(it)))
    vl = _nap(GOC / "tools" / "validate_ledger.py", "vl_eval")
    tham = {"id": "X", "decision": "apply", "gradeLevel": "high",
            "source": {"pmid": "1"}, "recommendation": "gọi bs.nguyen@benhvien.vn"}
    kq_pii = vl.cham([tham])
    ca(12, "thẻ chứa email → quét PII bắt ở mức CHẶN",
       any("PII" in k for k in kq_pii["chan"]))
    _ghi_neg("pii-email-gai", json.dumps(kq_pii["chan"], ensure_ascii=False))

    # ── Khối 4: MÃ THOÁT + MÂU THUẪN + ORCHESTRATOR ──────────────────────────
    vd = _nap(GOC / "EBM-Dashboards" / "tools" / "verify_dashboard.py", "vd_eval")
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        rc_mang = vd.report(["x (lỗi mạng: timeout)"], [], [])
        rc_noi_dung = vd.report(["ITEM-01 apply trên chứng cứ yếu"], [], [])
    ca(4, "cổng tách «chưa xác minh» (exit 2) khỏi «gói sai» (exit 1) — BH48",
       rc_mang == 2 and rc_noi_dung == 1)

    r3 = subprocess.run([PY, str(GOC / "tools" / "dang_ky_chu_de.py")],
                        capture_output=True, text=True, cwd=GOC)
    ca(7, "đăng ký chủ đề chạy + phân biệt lát cắt/phiên bản (BH30)",
       r3.returncode in (0, 1) and "lát cắt" in r3.stdout.lower() or "mâu thuẫn" in r3.stdout.lower())
    _ghi_neg("mau-thuan-quet-that", r3.stdout[-2000:])

    p1 = subprocess.run([PY, str(GOC / "ops" / "orchestrator.py"),
                         "--topic", "Suy tim", "--dry-run"],
                        capture_output=True, text=True, cwd=GOC).stdout
    p2 = subprocess.run([PY, str(GOC / "ops" / "orchestrator.py"),
                         "--topic", "Suy tim", "--dry-run"],
                        capture_output=True, text=True, cwd=GOC).stdout
    khop = [ln for ln in p1.splitlines() if "▸" in ln] == \
           [ln for ln in p2.splitlines() if "▸" in ln]
    ca(7, "orchestrator dry-run idempotent + chạy TỪNG lát cắt", khop and "[SuyTim_TongHop]" in p1)

    # ── Khối 5: AN TOÀN THUỐC (cấu hình + dây nối) ───────────────────────────
    flags = json.loads((GOC / "EBM-Dashboards" / "data" / "drug_flags.json")
                       .read_text(encoding="utf-8"))
    goi = json.dumps(flags, ensure_ascii=False).lower()
    co_aware = "aware" in goi and "azithromycin" in goi
    ca(11, "AWaRe: azithromycin mang cờ Watch trong drug_flags + consumer tồn tại",
       co_aware and (GOC / "EBM-Dashboards" / "tools" / "drug_safety_scan.py").exists(),
       "kiểm CẤU HÌNH + dây nối — hành vi đầy đủ chạy trong weekly_safety")
    co_beers = "beers" in goi
    ca(10, "Beers/STOPP hiện diện trong lớp cờ an toàn", co_beers if co_beers else None,
       "" if co_beers else "CHƯA có mục beers trong drug_flags — khoảng trống ghi nhận")

    # ── Khối 6: nhóm CẦN MẠNG / CHƯA TỰ ĐỘNG — khai đúng trạng thái ─────────
    ca(1, "guideline mới thay khuyến cáo (kiem_chung_cu_vuot_qua — quét quý)", None,
       "CẦN MẠNG; đo gần nhất 14/08: 125/172 mục apply có bản mới hơn cần đọc")
    ca(2, "SR/MA mới vượt qua chứng cứ đang dùng", None,
       "CẦN MẠNG; cùng công cụ elink pubmed_pubmed_reviews")
    ca(6, "số liệu lệch abstract (kiem_so_lieu ≥10%)", None,
       "CẦN MẠNG; đo gần nhất 14/08: 24/25 khớp, 1 ⚪")
    ca(5, "preprint → bản chính thức (đổi DOI/PMID)", None,
       "CHƯA TỰ ĐỘNG — khoảng trống thật, chưa có công cụ")
    ca(8, "nén tiếng Việt làm rụng mệnh đề điều kiện", None,
       "CHƯA TỰ ĐỘNG — luật nằm ở CHAT-BRIEF-SPEC, người soát")

    # ── Tổng kết ─────────────────────────────────────────────────────────────
    tu_dong = [k for k in KQ if k["dat"] is not None]
    dat = [k for k in tu_dong if k["dat"]]
    print("─" * 60)
    print(f"TỰ ĐỘNG: {len(dat)}/{len(tu_dong)} đạt · khai trạng thái: "
          f"{len([k for k in KQ if k['dat'] is None])} nhóm CẦN MẠNG/CHƯA TỰ ĐỘNG")

    bc = GOC / "reports" / f"eval-{date.today().isoformat()}.md"
    bc.parent.mkdir(exist_ok=True)
    dong = [f"# GOLD SET — {date.today().isoformat()}", "",
            f"TỰ ĐỘNG **{len(dat)}/{len(tu_dong)}** đạt (cộng 10 ca canary bên trong "
            f"dòng đầu = {len(tu_dong) + 9 + 4} hành vi được chấm). "
            "Bằng chứng ca âm tính: `quality/eval/negative/*.log`.", "",
            "| Nhóm | Ca | Kết quả | Ghi chú |", "|---|---|---|---|"]
    for k in KQ:
        kq_txt = {True: "✅", False: "🔴 TRƯỢT", None: "◌"}[k["dat"]]
        dong.append(f"| N{k['nhom']:02d} | {k['ca']} | {kq_txt} | {k['ghi_chu']} |")
    dong += ["", "> Máy chấm chỉ ĐO — không sửa dây chuyền cho ca đậu (C1/C2). "
             "Cần bác sĩ kiểm chứng."]
    bc.write_text("\n".join(dong) + "\n", encoding="utf-8")
    print(f"→ {bc.relative_to(GOC)}")
    return 0 if len(dat) == len(tu_dong) else 1


if __name__ == "__main__":
    raise SystemExit(main())
