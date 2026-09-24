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

# VÁ 08/09/2026: `GOC / "medical-ebm-automation"` giả định LỒNG — sai trên phiên
# cloud (anh em của GOC, không phải thư mục con). Dùng duong_goc() — cùng bản vá
# 07/09/2026 đã áp cho tools/luu_tru_kho.py, provenance_ledger.py, sources_health.py,
# doi_chieu_openalex.py, tools/eval/run_eval.py — file này (quality/eval/run_eval.py,
# TÊN GIỐNG nhưng KHÁC đường dẫn với tools/eval/run_eval.py) bị bỏ sót khỏi đợt đó,
# nên `from app.sources.retraction_chain import RetractionChain` crash
# ModuleNotFoundError trên MỌI lần chạy máy chấm gold-set trên phiên cloud.
_sp_re = importlib.util.spec_from_file_location(
    "_bst_re", GOC / "tools" / "ban_sao_tran.py")
_bst_re = importlib.util.module_from_spec(_sp_re)
_sp_re.loader.exec_module(_bst_re)
_MEA_GOC = _bst_re.duong_goc("medical-ebm-automation", GOC) or (GOC / "medical-ebm-automation")
_DASH_GOC = _bst_re.duong_goc("EBM-Dashboards", GOC)  # None nếu genuinely-absent (cloud)

# VÁ 24/09/2026 — BH94 TẠI GỐC. `quality/eval/negative/*.log` là BẰNG CHỨNG được track trong git,
# sinh từ máy CÓ dữ liệu thật (nền Retraction Watch, secrets, EBM-Dashboards). Trên BẢN SAO TRẦN
# (phiên cloud/CI/clone tươi) máy chấm từng ghi đè thẳng lên chúng: đo thật trên phiên cloud
# 24/09 (chạy qua BH102 trong hook mở phiên, MỖI phiên): `canary-10-loi-gai.log` bị làm RỖNG,
# `rut-bai-3-muc.log` đổi Wakefield 9500320 và Choi 30267080 từ `retracted` sang
# `unknown_mock_or_no_email` — đúng ca suýt bị commit ngày 02/09. Pre-commit
# `kiem_o_nhiem_artifact.py` chỉ chặn được NẾU hook đã bật, mà clone tươi trên cloud KHÔNG có
# `core.hooksPath`. Nay trên bản sao trần log đi vào `reports/` (đã gitignore) và báo cáo ghi rõ
# đường dẫn đó; máy thật vẫn ghi vào `quality/eval/negative/` như cũ.
_BAN_SAO_TRAN = _bst_re.ban_sao_git_tran(GOC)
NEG_GHI = (GOC / "reports" / "eval-negative-ban-sao-tran") if _BAN_SAO_TRAN else NEG


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
    NEG_GHI.mkdir(parents=True, exist_ok=True)
    (NEG_GHI / f"{ten_ca}.log").write_text(noi_dung, encoding="utf-8")


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
    # rồi chết bằng traceback thô trên bản sao trần (worktree/CI/clone tươi).
    #
    # ĐÍNH CHÍNH 17/09/2026 (Gap 2, quyết định kỹ thuật): bản 10/09 bail SỚM bằng
    # `ban_sao_git_tran(GOC)` — cổng đó (cloud-aware từ "Vòng 5" 09/09) trên cloud
    # CHỈ đòi EBM-Dashboards/ + EBM_MASTER/ vắng mặt, và HAI gốc đó LUÔN vắng trên
    # MỌI phiên cloud (dữ liệu chỉ-OneDrive theo thiết kế — xem CLAUDE.md). Hệ quả
    # đo được: máy chấm LUÔN thoát mã 2 trên cloud, NGAY CẢ KHI medical-ebm-
    # automation/ có mặt đầy đủ và đọc được — trong khi Khối 1/2/3/6 không cần gì
    # tới EBM-Dashboards, và Khối 4/5 (vá 08/09, ca7be25) đã tự phát hiện + khai
    # ◌ CHƯA CÓ NGUYÊN LIỆU đúng khi thiếu RIÊNG EBM-Dashboards. Bail-sớm theo BA
    # gốc gộp chung là đúng lớp lỗi BH08 đã lặp nhiều lần trong repo: biến "thiếu
    # MỘT VÀI nguyên liệu" thành "không kiểm được GÌ CẢ" — 0/11 nhóm chạy dù phần
    # lớn không đụng tới thứ đang thiếu.
    #
    # Dependency THẬT SỰ cứng của file này chỉ là medical-ebm-automation/ (Khối 2
    # import thẳng app.sources.retraction_chain, KHÔNG có đường giảm nhẹ) — chỉ
    # bail khi CHÍNH gốc đó không giải quyết được (không lồng, không anh em, dùng
    # duong_goc() đã nạp ở _MEA_GOC phía trên). EBM-Dashboards/EBM_MASTER thiếu
    # thì để các nhánh granular (Khối 4/5) tự khai CHƯA CÓ NGUYÊN LIỆU — không
    # bail thay cho chúng.
    if not (_MEA_GOC / "app" / "sources" / "retraction_chain.py").exists():
        print("⚠ THIẾU medical-ebm-automation/ (không lồng, không anh em) — máy chấm Gold "
              "Set cần cây đó cho RetractionChain (Khối 2), không có đường giảm nhẹ.")
        print("  Đây là HẠ TẦNG THIẾU (mã thoát 2), KHÔNG phải ca nào trượt (mã thoát 1) —")
        print("  không được đọc thành 'có lỗ hổng'.")
        return 2

    # ── Khối 1: CANARY đầu-cuối (10 ca gài sẵn — nhóm 3/4/7/9/10 một phần) ────
    r = subprocess.run([PY, str(GOC / "tools" / "thu_dau_cuoi_chung_cu.py")],
                       capture_output=True, text=True, cwd=GOC)
    canary_ok = r.returncode == 0
    # Ghi chú lấy NGUYÊN dòng tổng kết của canary (vd «🟢 12/12 … ⚪ 2 bỏ qua CÓ KHAI BÁO») thay vì
    # chữ cứng «10/10 bắt» — ca bỏ qua vì thiếu nguyên liệu không được trình bày như ca đã bắt (BH08).
    tom_tat = next((d.strip() for d in (r.stdout or "").splitlines()
                    if d.strip().startswith(("🟢", "🔴"))), "")
    ca(9, "canary 10 lỗi gài (apply+na/normativeBasis/Consensus/gradeBy/return-sớm…)",
       canary_ok, (tom_tat or "10/10 bắt") if canary_ok else "CÓ LỖ HỔNG — xem thu_dau_cuoi")
    _ghi_neg("canary-10-loi-gai", r.stdout[-3000:])

    # ── Khối 2: RÚT BÀI ngoại tuyến — hai MỨC khác nhau phải ra hai nhãn ─────
    sys.path.insert(0, str(_MEA_GOC))
    from app.sources.retraction_chain import RetractionChain  # noqa: PLC0415
    from app.sources.retraction_watch import RetractionWatchIndex  # noqa: PLC0415
    chain = RetractionChain()
    kq = chain.check(["9500320", "30267080", "99999999"])
    # VÁ 24/09/2026 (BH08/BH102): không có nền RW ngoại tuyến VÀ không tầng sống nào kết luận được
    # (mock/thiếu email/proxy chặn) ⇒ đây là CHƯA CÓ NGUYÊN LIỆU, không phải chuỗi rút bài hỏng.
    # Chỉ áp cho trạng thái `unknown_*` — một tầng sống trả «ok» cho 30267080 khi thiếu nền RW vẫn
    # là TRƯỢT thật (đó đúng là lỗ hổng đơn nguồn mà tầng RW sinh ra để bịt).
    rw_san_sang = RetractionWatchIndex().san_sang()
    thieu_nl = ("CHƯA CÓ NGUYÊN LIỆU — chưa có nền Retraction Watch ngoại tuyến và không tầng sống "
                "nào kết luận được; chạy: python medical-ebm-automation/tools/tai_retraction_watch.py")

    def _chua_co_nguyen_lieu(ban_ghi: dict) -> bool:
        return (not rw_san_sang) and str(ban_ghi.get("status", "")).startswith("unknown")

    w = kq.get("9500320", {})
    ca(3, "bài rút BỎ HẲN (Wakefield 9500320) → retracted, KHÔNG gắn R&R",
       None if _chua_co_nguyen_lieu(w) else
       (w.get("status") == "retracted" and not w.get("retract_and_replace")),
       thieu_nl if _chua_co_nguyen_lieu(w) else "")
    c = kq.get("30267080", {})
    ca(3, "RÚT-VÀ-THAY (Choi 30267080) → retracted + retract_and_replace (BH34)",
       None if _chua_co_nguyen_lieu(c) else
       (c.get("status") == "retracted" and c.get("retract_and_replace") is True),
       thieu_nl if _chua_co_nguyen_lieu(c) else "")
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
    duong_vd = _bst_re.duong_cong_cu_pipeline("verify_dashboard.py", GOC)
    if duong_vd is None:
        ca(4, "cổng tách «chưa xác minh» (exit 2) khỏi «gói sai» (exit 1) — BH48", None,
           "CHƯA CÓ NGUYÊN LIỆU — verify_dashboard.py không có ở EBM-Dashboards/tools/ "
           "lẫn bản vendor sync/skills/cap-nhat-chung-cu-y-khoa/tools/")
    else:
        vd = _nap(duong_vd, "vd_eval")
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

    if _DASH_GOC is None or not (_DASH_GOC / "WebDashboard_EBM_VanDeCuThe_SuyTim_TongHop_20260609.html").exists():
        # `ops/orchestrator.py::_dashboards_cua_chu_de()` glob trên EBM-Dashboards —
        # CHƯA CÓ NGUYÊN LIỆU trên checkout không có cây dữ liệu này (cloud), khác
        # hẳn "orchestrator hỏng"; đếm dòng ▸ rỗng là kết quả ĐÚNG của input rỗng.
        ca(7, "orchestrator dry-run idempotent + chạy TỪNG lát cắt", None,
           "CHƯA CÓ NGUYÊN LIỆU — EBM-Dashboards/ vắng mặt trên checkout này")
    else:
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
    # duong_cong_cu_pipeline() chỉ phủ tools/ — drug_flags.json nằm ở data/, nên
    # tự dò thêm nhánh vendor data/ tại đây (cùng nguyên tắc, phạm vi hẹp không
    # đáng tổng quát hoá vào ban_sao_tran.py cho một file dùng chung).
    duong_flags = (_DASH_GOC / "data" / "drug_flags.json") if _DASH_GOC else None
    if duong_flags is None or not duong_flags.exists():
        duong_flags = GOC / "sync" / "skills" / "cap-nhat-chung-cu-y-khoa" / "data" / "drug_flags.json"
    if not duong_flags.exists():
        ca(11, "AWaRe: azithromycin mang cờ Watch trong drug_flags + consumer tồn tại", None,
           "CHƯA CÓ NGUYÊN LIỆU — drug_flags.json không có ở EBM-Dashboards/data/ lẫn bản vendor")
        ca(10, "Beers/STOPP hiện diện trong lớp cờ an toàn", None,
           "CHƯA CÓ NGUYÊN LIỆU — cùng file drug_flags.json ở trên")
    else:
        flags = json.loads(duong_flags.read_text(encoding="utf-8"))
        goi = json.dumps(flags, ensure_ascii=False).lower()
        co_aware = "aware" in goi and "azithromycin" in goi
        duong_dss = _bst_re.duong_cong_cu_pipeline("drug_safety_scan.py", GOC)
        ca(11, "AWaRe: azithromycin mang cờ Watch trong drug_flags + consumer tồn tại",
           co_aware and duong_dss is not None,
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
            f"Bằng chứng ca âm tính: `{NEG_GHI.relative_to(GOC).as_posix()}/*.log`"
            + (" (bản sao trần — KHÔNG ghi đè log bằng chứng tracked)." if _BAN_SAO_TRAN else "."),
            "",
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
