#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spss_r_ebm_mcp.py — Máy chủ MCP «spss-r-ebm»: một cửa giữa SPSS · R/RStudio · nhập liệu và MỌI nơi dùng Claude (14/11/2026).

Bác sĩ hỏi kết nối SPSS/R «đã tự động như EndNote đã xây dựng với MCP chưa», rồi chọn «Dựng MCP + cài vào Claude Desktop».
Cùng khuôn với `endnote_ebm_mcp.py`: Claude Code (qua `.mcp.json`) và Claude Desktop/khung chat (qua `--cai-claude-desktop`)
gọi CHÍNH các công cụ đã đo của repo y khoa (`medical-ebm-automation/tools/`):

  • nhap_lieu_excel.py — mẫu nhập (Excel / SPSS .sav), kiểm từng ô, nhập kép, cổng tiếp nhận;
  • mo_trong_phan_mem.py — xuất .sav/.rds có kiểm (khứ hồi từng ô, ba chiều) rồi mở SPSS/RStudio;
  • kiem_cheo_g6.py — kiểm chéo G6 bằng SPSS + R;
  • run_stats_analysis.py — PHÂN TÍCH CHÍNH G6 đúng đặc tả SAP, CHỈ trên dữ liệu ĐÃ KHOÁ (G5), rồi kiểm chéo SPSS + R
    (F2/F3 14/11/2026: Poisson vững `poisson_pr`, hiệp biến phân loại → biến giả, lọc quần thể `loc`);
  • (F4, 14/11/2026) clean_research_dataset.py — LÀM SẠCH bản sao sau cổng tiếp nhận (query log, không sửa nguồn, không
    khoá); g5_quality_gate.evaluate_study(write=False) — «còn thiếu gì để khoá G5» CHỈ ĐỌC; bien_phai_sinh.py — kiểm/tính/
    đối chiếu biến phái sinh; chay_sap_g6.py — chạy TRỌN đặc tả SAP G6 (mỗi phân tích một gate) trên dữ liệu đã khoá;
  • (15/11/2026) doi_chieu_bien_de_cuong.py — biến máy ↔ đề cương/bộ biến đã duyệt (CHỈ ĐỌC; lệch nhập liệu thì công cụ
    chuẩn tự từ chối sinh mẫu/tiếp nhận, lệch phân tích thì từ chối tính biến phái sinh).

Rào chắn (không có ngoại lệ):
  • Công cụ CÓ TÁC DỤNG (sinh mẫu, tiếp nhận, xuất/mở, chạy kiểm chéo) CHẠY KHÔ mặc định — `ap_dung: true` mới làm.
  • KHÔNG có công cụ khoá dữ liệu (G5), ký cổng, sửa giá trị dữ liệu, đóng query, duyệt công thức/đặc tả hay xoá tệp —
    việc của người có thẩm quyền (cột `nguoi_duyet`, `G6_DAC_TA_SAP.json → nguoi_duyet` do thống kê viên/PI ghi).
  • Phân tích chính KHÔNG BAO GIỜ truyền cờ ghi đè cổng (`--i-confirm-sap-locked`, `--i-confirm-irb-approved`), không chạy
    trên dữ liệu chưa khoá (không «xem trước kết quả» trước khi khoá SAP/dữ liệu) và không tự chọn biến — đặc tả lấy từ
    lời gọi (theo SAP) hoặc dùng lại đúng đặc tả của lượt G6 trước.
  • Mọi bước đi qua công cụ chuẩn (tiến trình con bằng Python của môi trường dự án ~/.ebm-venv) — không đường tắt bỏ kiểm.
  • Dữ liệu chưa qua cổng tiếp nhận ở NGOÀI repo (công cụ chuẩn tự từ chối thư mục ra trong repo); giá trị ô chữ tự do
    không in ra (báo cáo của công cụ chuẩn đã che).

Giao thức: MCP qua stdio — JSON-RPC 2.0, mỗi thông điệp một dòng. Chỉ dùng thư viện chuẩn. stdout là KÊNH GIAO THỨC: tiến
trình con chạy với stdin=DEVNULL và bị bắt đầu ra; mọi dòng chữ khác đi stderr.

Cài cho Claude Desktop: `python3 tools/mcp/spss_r_ebm_mcp.py --cai-claude-desktop` (chạy khô) → `--ap-dung` (sao lưu tệp
cấu hình trước khi ghi, chỉ thêm/cập nhật đúng khoá `spss-r-ebm`). Cần bác sĩ kiểm chứng.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

for _s in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

GOC = Path(__file__).resolve().parents[2]  # repo gốc — thư mục chứa .mcp.json
TEN_MAY_CHU = "spss-r-ebm"
PHIEN_BAN = "1.2.0"
GIAO_THUC = ("2025-06-18", "2025-03-26", "2024-11-05")
CAN_KIEM = "Cần bác sĩ kiểm chứng."
DUOI_NHAP = (".xlsx", ".xlsm", ".sav")
TRAN_PHAT_HIEN = 40
KIEU_CHU = {
    "chu",
    "van_ban",
    "id",
}  # giá trị chữ tự do/mã nghiên cứu — không trả nguyên văn qua MCP


def thu_muc_y_khoa() -> Path:
    """Repo y khoa (biến môi trường EBM_MEDICAL_ROOT đè — dùng cho test)."""
    env = os.environ.get("EBM_MEDICAL_ROOT")
    return Path(env) if env else GOC / "medical-ebm-automation"


def python_du_an() -> str:
    """Python của môi trường dự án (có openpyxl/pandas) — KHÔNG phải python3 hệ thống. EBM_VENV_PYTHON đè."""
    env = os.environ.get("EBM_VENV_PYTHON")
    if env:
        return env
    for p in (
        Path.home() / ".ebm-venv" / "bin" / "python",
        Path.home() / ".ebm-venv" / "Scripts" / "python.exe",
    ):
        if p.exists():
            return str(p)
    return sys.executable


def _cuoi(chu: str, n: int) -> str:
    dong = (chu or "").strip().splitlines()
    return "\n".join(dong[-n:])


TRAN_JSON = 400_000  # ký tự — đầu ra --json của công cụ chuẩn đọc TRỌN (80 dòng cuối sẽ cắt giữa JSON nhiều dòng)


def chay_cong_cu(tep: str, doi_so: list[str], thoi_han: int = 900, *, tron: bool = False) -> dict:
    """Chạy một công cụ chuẩn của repo y khoa (tiến trình con, không đụng kênh giao thức stdout). `tron=True`: giữ TRỌN
    stdout (lệnh --json) thay vì 80 dòng cuối."""
    yk = thu_muc_y_khoa()
    cc = yk / "tools" / tep
    if not cc.exists():
        raise RuntimeError(
            f"không thấy {cc} — repo y khoa chưa có công cụ này (kéo bản mới)"
        )
    try:
        k = subprocess.run(
            [python_du_an(), str(cc), *doi_so],
            cwd=yk,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=thoi_han,
            stdin=subprocess.DEVNULL,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ma_thoat": None,
            "het_thoi_han_giay": thoi_han,
            "dau_ra": "",
            "loi": "quá thời hạn",
        }
    return {
        "ma_thoat": k.returncode,
        "dau_ra": (k.stdout or "").strip()[:TRAN_JSON] if tron else _cuoi(k.stdout, 80),
        "loi": _cuoi(k.stderr, 20),
    }


def _ma_de_tai(a: dict) -> str:
    s = str(a.get("study") or "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", s):  # chữ/số đầu: chặn «..», «.ẩn»
        raise ValueError(f"mã đề tài không hợp lệ: {s!r}")
    if not (thu_muc_y_khoa() / "exports" / s).is_dir():
        raise ValueError(f"không có thư mục đề tài exports/{s}")
    return s


def _tep(a: dict, khoa: str) -> Path:
    v = a.get(khoa)
    if not v:
        raise ValueError(f"thiếu «{khoa}» (đường dẫn tệp đã nhập .xlsx/.xlsm/.sav)")
    p = Path(str(v)).expanduser().resolve()
    if p.suffix.lower() not in DUOI_NHAP:
        raise ValueError(
            f"{khoa}: chỉ nhận {', '.join(DUOI_NHAP)} — nhận {p.suffix or '(không đuôi)'}"
        )
    if not p.exists():
        raise ValueError(f"không thấy tệp: {p}")
    return p


def _ra(a: dict, tep: Path, mac_dinh: str) -> Path:
    return (
        Path(str(a["ra"])).expanduser().resolve()
        if a.get("ra")
        else tep.parent / mac_dinh
    )


def _doc_json(p: Path) -> dict | list | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _co_khoa(study: str) -> bool:
    """Có manifest khoá dữ liệu G5 (công cụ chuẩn mới kiểm SHA-256/trạng thái khi xuất — đây chỉ là gợi ý nhanh)."""
    d = thu_muc_y_khoa() / "exports" / study
    meta = _doc_json(d / "study_meta.json") or {}
    rel = ((meta.get("real_data_lock") or {}) if isinstance(meta, dict) else {}).get(
        "manifest"
    )
    return (d / rel).exists() if rel else (d / "DATA_LOCK_manifest.json").exists()


# ─────────────────────────── công cụ ───────────────────────────

_MA_TRANG_THAI = """import json, sys
sys.path.insert(0, 'tools')
kq = {}
try:
    import cau_noi_spss as S
    kq['spss'] = str(S.tim_spss())
except Exception as e:
    kq['spss'] = None; kq['spss_ly_do'] = str(e)[:200]
try:
    import cau_noi_r as R
    kq['rscript'] = str(R.tim_r())
except Exception as e:
    kq['rscript'] = None; kq['r_ly_do'] = str(e)[:200]
try:
    import openpyxl
    kq['openpyxl'] = openpyxl.__version__
except Exception:
    kq['openpyxl'] = None
print(json.dumps(kq, ensure_ascii=False))
"""


def cc_trang_thai(_a: dict) -> dict:
    yk = thu_muc_y_khoa()
    kq: dict = {
        "repo_y_khoa": str(yk),
        "python_du_an": python_du_an(),
        "co_repo_y_khoa": (yk / "tools").is_dir(),
    }
    if kq["co_repo_y_khoa"]:
        try:
            k = subprocess.run([python_du_an(), "-c", _MA_TRANG_THAI], cwd=yk, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=60, stdin=subprocess.DEVNULL, check=False)  # fmt: skip
            kq.update(
                json.loads(k.stdout.strip().splitlines()[-1])
                if k.stdout.strip()
                else {"loi": _cuoi(k.stderr, 5)}
            )
        except (subprocess.TimeoutExpired, ValueError, OSError) as e:
            kq["loi_do_phan_mem"] = f"{type(e).__name__}: {e}"[:200]
    kq["rstudio"] = (
        (
            str(Path("/Applications/RStudio.app"))
            if Path("/Applications/RStudio.app").exists()
            else None
        )
        if sys.platform == "darwin"
        else "chưa kiểm (không phải macOS)"
    )
    de_tai = []
    for d in sorted((yk / "exports").glob("*")) if (yk / "exports").is_dir() else []:
        if not d.is_dir() or not (
            (d / "study_meta.json").exists()
            or list(d.glob("G5_REDCap_dictionary_*.csv"))
        ):
            continue
        meta = _doc_json(d / "study_meta.json") or {}
        nl = d / "nhap_lieu"
        de_tai.append(
            {
                "study": d.name,
                "loai": meta.get("study_kind") if isinstance(meta, dict) else None,
                "tu_dien_g5": (d / f"G5_REDCap_dictionary_{d.name}.csv").exists(),
                "mau_excel": (nl / f"MAU_NHAP_LIEU_{d.name}.xlsx").exists(),
                "mau_spss": (nl / f"MAU_NHAP_LIEU_{d.name}.sav").exists(),
                "co_manifest_khoa": _co_khoa(d.name),
            }
        )
    kq["de_tai"] = de_tai
    kq["ghi_chu"] = (
        "Chỉ đọc. «co_manifest_khoa» là gợi ý nhanh — công cụ xuất mới kiểm SHA-256 của bản khoá. "
        + CAN_KIEM
    )
    return kq


def cc_mau(a: dict) -> dict:
    study = _ma_de_tai(a)
    dang = a.get("dang") or "xlsx"
    if dang not in ("xlsx", "sav"):
        raise ValueError("dang: xlsx (Excel) hoặc sav (nhập thẳng trong SPSS)")
    dich = (
        thu_muc_y_khoa()
        / "exports"
        / study
        / "nhap_lieu"
        / f"MAU_NHAP_LIEU_{study}.{dang}"
    )
    if not a.get("ap_dung"):
        return {"chay_kho": True, "se_tao": str(dich), "da_co": dich.exists(),
                "ghi_chu": "Mẫu KHÔNG chứa dữ liệu; tệp đã có dữ liệu không bao giờ bị ghi đè. ap_dung: true để tạo."}  # fmt: skip
    doi_so = (
        ["mau", "--study", study]
        + (["--dang", "sav"] if dang == "sav" else [])
        + (["--ghi-de"] if a.get("ghi_de") else [])
    )
    return {**chay_cong_cu("nhap_lieu_excel.py", doi_so, 300), "tep": str(dich)}


def _tom_bao_cao(bc: dict | None) -> dict:
    if not isinstance(bc, dict):
        return {"bao_cao": None}
    ph = bc.get("phat_hien") or []
    return {
        "trang_thai": bc.get("trang_thai"),
        "so_ma_nghien_cuu": bc.get("so_ma_nghien_cuu"),
        "so_loi": bc.get("so_loi"),
        "so_truy_van": bc.get("so_truy_van"),
        "so_canh_bao": bc.get("so_canh_bao"),
        "tu_kiem_csv": bc.get("tu_kiem_csv"),
        "csv": bc.get("csv"),
        "phat_hien": [
            {
                k: x.get(k)
                for k in (
                    "muc",
                    "ma",
                    "trang",
                    "o",
                    "cot",
                    "ma_nc",
                    "chi_tiet",
                    "gia_tri",
                )
            }
            for x in ph[:TRAN_PHAT_HIEN]
        ],
        "con_lai": max(0, len(ph) - TRAN_PHAT_HIEN),
    }


def cc_kiem(a: dict) -> dict:
    study = _ma_de_tai(a)
    tep = _tep(a, "tep")
    ra = _ra(a, tep, f"{tep.stem}_csv")
    kq = chay_cong_cu(
        "nhap_lieu_excel.py",
        ["nhap", "--study", study, "--excel", str(tep), "--ra", str(ra)],
        600,
    )
    return {**kq, **_tom_bao_cao(_doc_json(ra / f"{tep.stem}_bao_cao_nhap.json")), "thu_muc_ra": str(ra),
            "ghi_chu": "Kiểm từng ô như REDCap, KHÔNG gọi cổng tiếp nhận. CSV/báo cáo ở thư mục ra (ngoài repo). " + CAN_KIEM}  # fmt: skip


def cc_so_sanh(a: dict) -> dict:
    study = _ma_de_tai(a)
    t1, t2 = _tep(a, "tep1"), _tep(a, "tep2")
    ra = _ra(a, t1, f"nhap_kep_{t1.stem}_{t2.stem}")
    kq = chay_cong_cu("nhap_lieu_excel.py", ["so-sanh", "--study", study, "--excel1", str(t1), "--excel2", str(t2),
                                              "--ra", str(ra)], 600)  # fmt: skip
    lech = []
    try:
        with open(ra / "NHAP_KEP_chi_tiet.csv", encoding="utf-8", newline="") as f:
            for r in list(csv.DictReader(f))[:TRAN_PHAT_HIEN]:
                chu = r.get("kieu") in KIEU_CHU
                lech.append({**r, "gia_tri_lan1": "«chữ»" if chu else r.get("gia_tri_lan1"),
                             "gia_tri_lan2": "«chữ»" if chu else r.get("gia_tri_lan2")})  # fmt: skip
    except OSError:
        pass
    return {**kq, "tom_tat": _doc_json(ra / "NHAP_KEP_tom_tat.json"), "o_lech": lech, "thu_muc_ra": str(ra),
            "ghi_chu": "Đối chiếu PHIẾU GỐC cho từng ô lệch; giá trị ô chữ tự do bị che. " + CAN_KIEM}  # fmt: skip


def cc_tiep_nhan(a: dict) -> dict:
    study = _ma_de_tai(a)
    tep = _tep(a, "tep")
    ra = _ra(a, tep, f"{tep.stem}_csv")
    doi_so = ["nhap", "--study", study, "--excel", str(tep), "--ra", str(ra)]
    if not a.get("ap_dung"):
        kq = chay_cong_cu("nhap_lieu_excel.py", doi_so, 600)
        tom = _tom_bao_cao(_doc_json(ra / f"{tep.stem}_bao_cao_nhap.json"))
        return {"chay_kho": True, **tom, "se_tiep_nhan": tom.get("trang_thai") == "SACH", "ma_thoat_kiem": kq["ma_thoat"],
                "se_lam_sach_sau": bool(a.get("lam_sach", True)),
                "ghi_chu": "Chỉ khi SẠCH cổng tiếp nhận (quét PII, chép bản chỉ đọc vào exports/<mã>) mới chạy; tiếp nhận xong "
                           "tự LÀM SẠCH bản sao (lam_sach=false để tắt). ap_dung: true để chạy thật."}  # fmt: skip
    kq = chay_cong_cu("nhap_lieu_excel.py", [*doi_so, "--tiep-nhan"], 900)
    if kq.get("ma_thoat") == 0 and a.get("lam_sach", True):
        try:
            kq["lam_sach"] = cc_lam_sach({"study": study, "ap_dung": True})
        except (ValueError, RuntimeError) as e:  # tiếp nhận đã xong — làm sạch lỗi thì báo, không phủ kết quả tiếp nhận
            kq["lam_sach"] = {"loi": f"{type(e).__name__}: {e}"[:400], "goi_y": "chạy lại công cụ lam_sach"}
    return kq


def cc_xuat(a: dict) -> dict:
    study = _ma_de_tai(a)
    pm = a.get("phan_mem")
    if pm not in ("spss", "r"):
        raise ValueError("phan_mem: spss hoặc r")
    khoa = _co_khoa(study)
    tep = None if khoa or not a.get("tep") else _tep(a, "tep")
    mo = bool(a.get("mo", True))
    if not a.get("ap_dung"):
        nguon = (
            "bản ĐÃ KHOÁ"
            if khoa
            else (f"BẢN NHÁP từ {tep.name} (chỉ khi sạch)" if tep else None)
        )
        return {"chay_kho": True, "phan_mem": pm, "nguon": nguon or "chưa khoá dữ liệu — cần «tep» (tệp đã nhập)",
                "se_mo_ung_dung": mo, "ghi_chu": "Xuất có kiểm (khứ hồi từng ô · ba chiều); bước nào lỗi thì không mở. "
                                                 "ap_dung: true để chạy."}  # fmt: skip
    doi_so = (
        [pm, "--study", study]
        + (["--excel", str(tep)] if tep else [])
        + ([] if mo else ["--khong-mo"])
    )
    return chay_cong_cu("mo_trong_phan_mem.py", doi_so, 1800)


def cc_kiem_cheo(a: dict) -> dict:
    study = _ma_de_tai(a)
    if not a.get("ap_dung"):
        kq = chay_cong_cu(
            "kiem_cheo_g6.py", ["trang-thai", "--study", study, "--json"], 120
        )
        try:
            kq["trang_thai"] = json.loads(kq["dau_ra"]) if kq.get("dau_ra") else None
        except ValueError:
            pass
        return {
            **kq,
            "ghi_chu": "Chỉ đọc trạng thái kiểm chéo G6. ap_dung: true để CHẠY SPSS + R (vài phút).",
        }
    return chay_cong_cu("kiem_cheo_g6.py", ["chay", "--study", study], 3600)


_MA_DU_LIEU_KHOA = """import json, sys
sys.path.insert(0, 'tools')
import cau_noi_spss as S
try:
    p, m = S.tim_du_lieu_khoa(sys.argv[1])
    print(json.dumps({"tep": str(p), "lock_date": m.get("lock_date"), "sap_version": m.get("sap_version")}))
except Exception as e:
    print(json.dumps({"tep": None, "ly_do": str(e)[:300]}, ensure_ascii=False))
"""
KHOA_DAC_TA = (
    "outcome",
    "group",
    "covariates",
    "outcome_type",
    "time",
    "event",
    "cot_cum",
    "don_vi_phoi_nhiem",
    "hiep_bien_phan_loai",
    "loc",
)


def du_lieu_khoa(study: str) -> dict:
    """Bộ dữ liệu ĐÃ KHOÁ — kiểm bằng ĐÚNG hàm của cổng (cau_noi_spss.tim_du_lieu_khoa → gate_contract): trạng thái
    LOCKED_FOR_ANALYSIS · analysis_allowed · khớp SHA-256. Không khoá ⇒ {"tep": None, "ly_do": …}."""
    yk = thu_muc_y_khoa()
    try:
        k = subprocess.run([python_du_an(), "-c", _MA_DU_LIEU_KHOA, study], cwd=yk, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60, stdin=subprocess.DEVNULL, check=False)  # fmt: skip
        return json.loads(k.stdout.strip().splitlines()[-1])
    except (subprocess.TimeoutExpired, ValueError, IndexError, OSError) as e:
        return {"tep": None, "ly_do": f"không đo được ({type(e).__name__})"}


def _dac_ta(a: dict, study: str) -> dict:
    """Đặc tả phân tích: từ lời gọi (theo SAP đã khoá) hoặc ĐÚNG đặc tả của lượt G6 trước (dung_dac_ta_truoc)."""
    if a.get("dung_dac_ta_truoc"):
        tom = _doc_json(
            thu_muc_y_khoa() / "exports" / study / "G6_analysis_summary.json"
        )
        dt = (tom or {}).get("dac_ta_phan_tich") if isinstance(tom, dict) else None
        if not dt:
            raise ValueError(
                "chưa có lượt G6 trước để dùng lại đặc tả — truyền outcome/group… theo SAP"
            )
        return {k: dt.get(k) for k in KHOA_DAC_TA}
    if not a.get("outcome") and not (a.get("time") and a.get("event")):
        raise ValueError(
            "cần đặc tả theo SAP đã khoá (outcome, hoặc time+event…) — máy chủ KHÔNG tự chọn biến"
        )
    return {k: a.get(k) for k in KHOA_DAC_TA}


def _gia_tri(v) -> str:
    """Một giá trị đặc tả (tên biến, đơn vị…) đi thẳng vào argv: cấm rỗng, cấm bắt đầu bằng «-» (chèn cờ), cấm xuống dòng."""
    s = str(v).strip()
    if not s or s.startswith("-") or any(c in s for c in "\n\r\x00"):
        raise ValueError(f"giá trị đặc tả không hợp lệ: {s[:40]!r} (không được rỗng hay bắt đầu bằng «-»)")
    return s


def _doi_so_phan_tich(study: str, tep: str, dt: dict, a: dict) -> list[str]:
    ds = ["--data", tep, "--study", study, "--gate", "G6"]
    for k, co in (("outcome", "--outcome"), ("group", "--group"), ("time", "--time"), ("event", "--event"),
                  ("outcome_type", "--outcome-type"), ("cot_cum", "--cot-cum")):  # fmt: skip
        if dt.get(k):
            ds += [co, _gia_tri(dt[k])]
    for k, co in (("covariates", "--covariates"), ("hiep_bien_phan_loai", "--hiep-bien-phan-loai")):
        v = dt.get(k) or []
        if v:
            ds += [co, ",".join(_gia_tri(c) for c in v) if isinstance(v, list) else _gia_tri(v)]
    if dt.get("loc"):
        ds += ["--loc", _gia_tri(dt["loc"])]
    if dt.get("don_vi_phoi_nhiem") not in (None, ""):
        ds += ["--don-vi-phoi-nhiem", _gia_tri(dt["don_vi_phoi_nhiem"])]
    if a.get("vars"):
        ds += ["--vars", _gia_tri(a["vars"])]
    if a.get("kiem_cheo", True):
        ds.append("--kiem-cheo")
    # rào cứng: không bao giờ truyền cờ ghi đè cổng qua MCP (assert sẽ mất khi chạy python -O — dùng lệnh chặn thật)
    if any(x.startswith("--i-confirm") for x in ds):
        raise RuntimeError("cờ ghi đè cổng bị cấm qua MCP")
    return ds


def cc_phan_tich(a: dict) -> dict:
    study = _ma_de_tai(a)
    khoa = du_lieu_khoa(study)
    if not khoa.get("tep"):
        return {"tu_choi": True, "ly_do": "chưa có dữ liệu ĐÃ KHOÁ (G5) — phân tích chính chỉ chạy sau khi SAP (G4) và dữ "
                "liệu (G5) được NGƯỜI có thẩm quyền khoá; máy chủ không có cờ ghi đè. Chi tiết: " + str(khoa.get("ly_do")),
                "goi_y": "Trước khi khoá chỉ nên kiểm chất lượng nhập (nhap_lieu_kiem), không xem kết quả phân tích."}  # fmt: skip
    dt = _dac_ta(a, study)
    ds = _doi_so_phan_tich(study, khoa["tep"], dt, a)
    _can_ban_moi("run_stats_analysis.py", ds)
    if not a.get("ap_dung"):
        return {"chay_kho": True, "du_lieu_khoa": khoa, "dac_ta": dt, "se_chay": ["run_stats_analysis.py", *ds],
                "ghi_chu": "Đặc tả phải đúng SAP đã khoá. ap_dung: true để chạy (kèm kiểm chéo SPSS + R)."}  # fmt: skip
    kq = chay_cong_cu("run_stats_analysis.py", ds, 3600)
    return {**kq, "ket_qua": cc_ket_qua({"study": study}).get("ket_qua")}


# Cờ chỉ có từ bản F2/F3 của repo y khoa — bản cũ (argparse) sẽ báo «unrecognized arguments» khó hiểu: chặn sớm, nói rõ.
_CO_BAN_MOI = {"--hiep-bien-phan-loai": "F2 (Poisson vững + hiệp biến phân loại)", "--loc": "F3 (lọc quần thể)",
               "poisson_pr": "F2 (Poisson vững)"}  # fmt: skip


def _can_ban_moi(tep: str, ds: list[str]) -> None:
    try:
        nguon = (thu_muc_y_khoa() / "tools" / tep).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return  # chay_cong_cu sẽ báo «không thấy công cụ»
    thieu = [mo_ta for co, mo_ta in _CO_BAN_MOI.items() if co in ds and f'"{co}"' not in nguon]  # khớp chuỗi có nháy: «--loc» ≠ «--locked»
    if thieu:
        raise RuntimeError(f"repo y khoa chưa có bản {', '.join(thieu)} của {tep} — kéo bản mới (PR đã gộp) rồi chạy lại")


def _gon(x, tran: int = 3000):
    chu = json.dumps(x, ensure_ascii=False, default=str)
    return (
        x
        if len(chu) <= tran
        else chu[:tran] + " …(đã cắt — xem tệp G6_analysis_summary.json)"
    )


def cc_ket_qua(a: dict) -> dict:
    study = _ma_de_tai(a)
    p = thu_muc_y_khoa() / "exports" / study / "G6_analysis_summary.json"
    tom = _doc_json(p)
    if not isinstance(tom, dict):
        return {"ket_qua": None, "ly_do": f"chưa có {p.name} — chưa chạy phân tích G6"}
    khoa = ("study", "generated", "n_total", "data_lock", "dac_ta_phan_tich", "primary_outcome", "multivariate",
            "survival", "kaplan_meier", "table1", "missing_data", "ordinal", "icc_cluster")  # fmt: skip
    kc = chay_cong_cu(
        "kiem_cheo_g6.py", ["trang-thai", "--study", study, "--json"], 120
    )
    try:
        kiem_cheo = json.loads(kc.get("dau_ra") or "null")
    except ValueError:
        kiem_cheo = kc.get("dau_ra")
    return {"ket_qua": {k: _gon(tom[k]) for k in khoa if k in tom}, "kiem_cheo_g6": kiem_cheo, "tep": str(p),
            "ghi_chu": "Kết quả TƯ VẤN — thống kê viên xác nhận ở G6 (G6-HUMAN-01). " + CAN_KIEM}  # fmt: skip


# ─────────────────────── F4 (14/11/2026): làm sạch · G5 · biến phái sinh · SAP ───────────────────────

_ID = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*")


def _trong(goc: Path, p: Path) -> bool:
    try:
        p.resolve().relative_to(goc.resolve())
        return True
    except ValueError:
        return False


def _tep_trong_de_tai(study: str, v, ten: str, duoi: tuple[str, ...]) -> Path:
    """Tệp nằm TRONG exports/<mã> (bản sao sau cổng tiếp nhận) — không nhận tệp thô ngoài đề tài."""
    d = thu_muc_y_khoa() / "exports" / study
    p = Path(str(v)).expanduser()
    p = (p if p.is_absolute() else d / p).resolve()
    if not _trong(d, p):
        raise ValueError(f"{ten}: chỉ nhận tệp trong exports/{study}/ (bản sao đã qua cổng tiếp nhận)")
    if p.suffix.lower() not in duoi:
        raise ValueError(f"{ten}: chỉ nhận {', '.join(duoi)}")
    if not p.exists():
        raise ValueError(f"không thấy tệp: {p}")
    return p


def _tom_lam_sach(bc: dict | None) -> dict:
    if not isinstance(bc, dict):
        return {"bao_cao_lam_sach": None}
    return {k: bc.get(k) for k in ("status", "cleaned_at", "source_filename", "clean_dataset_path", "query_log", "row_count",
                                    "column_count", "dictionary_loaded", "dictionary_blocker", "safe_action_counts",
                                    "open_query_count", "n_query_resolved", "query_summary", "query_resolution_errors",
                                    "blocker", "ready_for_lock")}  # fmt: skip


def _ke_lam_sach(a: dict, study: str) -> tuple[list[str], dict]:
    d = thu_muc_y_khoa() / "exports" / study
    meta = _doc_json(d / "study_meta.json") or {}
    if a.get("data"):
        data = _tep_trong_de_tai(study, a["data"], "data", (".csv",))
    else:
        rel = ((meta.get("real_data_intake") or {}) if isinstance(meta, dict) else {}).get("raw_readonly_path")
        if not rel:
            raise ValueError("chưa có bản sao sau cổng tiếp nhận (study_meta.real_data_intake) — chạy nhap_lieu_tiep_nhan "
                             "trước, hoặc truyền «data» (CSV trong exports/<mã>/)")
        data = _tep_trong_de_tai(study, rel, "raw_readonly_path", (".csv",))
    td = a.get("tu_dien")
    tu_dien = (_tep_trong_de_tai(study, td, "tu_dien", (".csv", ".json")) if td
               else (d / f"G5_REDCap_dictionary_{study}.csv" if (d / f"G5_REDCap_dictionary_{study}.csv").exists() else None))
    ds = ["--study", study, "--data", str(data)] + (["--dictionary", str(tu_dien)] if tu_dien else [])
    if a.get("cot_ma_nc"):
        ds += ["--id-column", _gia_tri(a["cot_ma_nc"])]
    if a.get("giai_quyet_query"):
        ds += ["--query-resolutions", str(_tep_trong_de_tai(study, a["giai_quyet_query"], "giai_quyet_query",
                                                            (".csv", ".json")))]  # fmt: skip
    return ds, {"data": str(data), "tu_dien": str(tu_dien) if tu_dien else None}


def cc_lam_sach(a: dict) -> dict:
    study = _ma_de_tai(a)
    ds, nguon = _ke_lam_sach(a, study)
    bc_p = thu_muc_y_khoa() / "exports" / study / "DATA_CLEANING_report.json"
    if not a.get("ap_dung"):
        return {"chay_kho": True, **nguon, "se_chay": ["clean_research_dataset.py", *ds],
                "lan_truoc": _tom_lam_sach(_doc_json(bc_p)),
                "ghi_chu": "Làm sạch trên BẢN SAO (03_clean_working): chỉ thao tác an toàn (bỏ khoảng trắng, chuẩn hoá mã "
                           "thiếu); giá trị mơ hồ thành query mở, KHÔNG tự sửa. Không khoá dữ liệu. ap_dung: true để chạy."}  # fmt: skip
    kq = chay_cong_cu("clean_research_dataset.py", ds, 1800)
    tom = _tom_lam_sach(_doc_json(bc_p))
    buoc = ("Sẵn sàng để NGƯỜI có thẩm quyền khoá (lock_analysis_dataset.py — máy chủ không khoá)." if tom.get("ready_for_lock")
            else "Còn query mở: PI/quản lý dữ liệu đối chiếu phiếu gốc, ghi tệp giải quyết (giai_quyet_query) rồi làm sạch "
                 "lại." if tom.get("open_query_count") else "Xem «blocker» trong báo cáo.")  # fmt: skip
    return {**kq, **nguon, **tom, "buoc_tiep": buoc, "ghi_chu": "Báo cáo/query log không chứa giá trị thô. " + CAN_KIEM}


_MA_G5 = """import json, sys
from pathlib import Path
sys.path.insert(0, 'tools')
import g5_quality_gate as Q
s = sys.argv[1]
r = Q.evaluate_study(s, Path('exports') / s, repo_root=Path('.').resolve(), write=False)
print(json.dumps(r, ensure_ascii=False, default=str))
"""


def cc_g5_con_thieu(a: dict) -> dict:
    """«Còn thiếu gì để khoá G5» — chấm bằng ĐÚNG hàm của cổng với write=False: không ghi báo cáo, study_meta, checkpoint."""
    study = _ma_de_tai(a)
    yk = thu_muc_y_khoa()
    if not (yk / "tools" / "g5_quality_gate.py").exists():
        raise RuntimeError("repo y khoa chưa có tools/g5_quality_gate.py")
    k = None
    try:
        k = subprocess.run([python_du_an(), "-c", _MA_G5, study], cwd=yk, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=300, stdin=subprocess.DEVNULL, check=False,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})  # fmt: skip
        bc = json.loads(k.stdout.strip().splitlines()[-1])
        if not isinstance(bc, dict):
            raise ValueError("đầu ra không phải báo cáo")
    except (subprocess.TimeoutExpired, ValueError, IndexError, OSError) as e:
        return {"trang_thai": None, "khong_do_duoc": type(e).__name__, "loi": _cuoi(k.stderr, 8) if k is not None else None,
                "ghi_chu": "KHÔNG đo được ≠ đạt. " + CAN_KIEM}  # fmt: skip
    tieu_chi = bc.get("automatic_criteria") or []
    chua = [{k: x.get(k) for k in ("id", "label", "status", "action")} for x in tieu_chi if x.get("status") != "PASS"]
    return {"trang_thai": bc.get("status"), "so_tieu_chi": len(tieu_chi), "chua_dat": chua,
            "viec_can_lam": bc.get("actions") or [], "khoa_ky_thuat_hop_le": bc.get("technical_lock_valid"),
            "phe_duyet_nguoi_hop_le": bc.get("human_approval_valid"), "vai_da_ky": bc.get("vai_da_ky"),
            "dong_ky_du": bc.get("dong_ky_du"), "co_du_lieu_that": bc.get("real_data_present"),
            "ghi_chu": "CHỈ ĐỌC (không ghi báo cáo/study_meta/checkpoint). Khoá dữ liệu và ký G5 (DATA_MANAGER + PI) là việc "
                       "của người — máy chủ không có công cụ đó. " + CAN_KIEM}  # fmt: skip


def cc_doi_chieu_bien(a: dict) -> dict:
    """Biến máy (từ điển nhập liệu, biến phái sinh, đặc tả SAP) ↔ đề cương/bộ biến đã duyệt — chỉ đọc."""
    study = _ma_de_tai(a)
    kq = chay_cong_cu("doi_chieu_bien_de_cuong.py", ["--study", study, "--json"], 300, tron=True)
    bc = _json_dau_ra(kq)
    if not isinstance(bc, dict):
        return {**kq, "trang_thai": None, "ghi_chu": "KHÔNG đọc được kết quả đối chiếu — không đo được ≠ đồng bộ. " + CAN_KIEM}
    ph = bc.get("phat_hien") or []
    gon = lambda x: {k: x.get(k) for k in ("luat", "pham_vi", "bien", "chi_tiet")}  # noqa: E731
    return {"trang_thai": bc.get("trang_thai"), "ma_thoat": kq.get("ma_thoat"), "nguon_nguoi_duyet": bc.get("nguon_nguoi_duyet"),
            "ban_may": bc.get("ban_may"), "so_bien_nguon": bc.get("so_bien_nguon"), "khong_do_duoc": bc.get("khong_do_duoc"),
            "lech_nhap_lieu": [gon(x) for x in ph if x.get("muc") == "LECH" and x.get("pham_vi") == "nhap_lieu"],
            "lech_phan_tich": [gon(x) for x in ph if x.get("muc") == "LECH" and x.get("pham_vi") == "phan_tich"],
            "can_xem": [gon(x) for x in ph if x.get("muc") != "LECH"][:TRAN_PHAT_HIEN],
            "dat_canh": _gon(bc.get("dat_canh"), 6000),
            "ghi_chu": "Chỉ đọc. Nguồn chuẩn là đề cương/bộ biến ĐÃ DUYỆT — sửa bản máy cho khớp; nguồn cần đổi thì chủ nhiệm "
                       "duyệt sửa đề cương/bộ biến trước, agent KHÔNG tự thêm biến vào bản máy. Lệch nhập liệu ⇒ sinh mẫu/tiếp "
                       "nhận bị từ chối; lệch phân tích ⇒ tính biến phái sinh ở G6 bị từ chối. " + CAN_KIEM}  # fmt: skip


def _ds_ten(v, ten: str) -> str:
    ds = v if isinstance(v, list) else str(v).split(",")
    ds = [str(x).strip() for x in ds if str(x).strip()]
    if not ds or any(not _ID.fullmatch(x) for x in ds):
        raise ValueError(f"{ten}: danh sách tên/mã không hợp lệ (chữ, số, «_ . -», không bắt đầu bằng «-»)")
    return ",".join(ds)


def _json_dau_ra(kq: dict):
    """Đọc JSON của lệnh --json; đọc được thì bỏ «dau_ra» thô khỏi kq (khỏi trả hai lần), không đọc được thì giữ để chẩn đoán."""
    try:
        v = json.loads(kq.get("dau_ra") or "null")
    except ValueError:
        return None
    kq.pop("dau_ra", None)
    return v


def cc_bien_phai_sinh(a: dict) -> dict:
    study = _ma_de_tai(a)
    lenh = a.get("lenh") or "kiem"
    if lenh == "kiem":
        kq = chay_cong_cu("bien_phai_sinh.py", ["kiem", "--study", study, "--json"], 300, tron=True)
        v = _json_dau_ra(kq)  # gọi TRƯỚC khi trải kq — hàm bỏ «dau_ra» thô khỏi kq
        return {**kq, "ket_qua": _gon(v, 20000), "ghi_chu": "Chỉ đọc: công thức hợp lệ không, đã duyệt chưa (dấu khớp "
                "công thức), thứ tự tính. Người duyệt ghi cột nguoi_duyet — máy chủ không ghi. " + CAN_KIEM}  # fmt: skip
    if lenh not in ("tinh", "doi_chieu"):
        raise ValueError("lenh: kiem · tinh · doi_chieu")
    if not a.get("data"):
        raise ValueError("thiếu «data» (CSV đã khoá hoặc CSV nhập liệu ngoài repo)")
    data = Path(str(a["data"])).expanduser().resolve()
    if data.suffix.lower() != ".csv" or not data.exists():
        raise ValueError(f"data: cần tệp .csv có thật — nhận {data}")
    ds = ["tinh" if lenh == "tinh" else "doi-chieu", "--study", study, "--data", str(data)]
    if lenh == "tinh":
        ra = Path(str(a["ra"])).expanduser().resolve() if a.get("ra") else data.parent / f"{data.stem}_bien_phai_sinh"
        if _trong(thu_muc_y_khoa(), ra):
            raise ValueError("ra: thư mục ra phải NGOÀI repo y khoa")
        ds += ["--ra", str(ra)]
    else:
        ds += (["--khong-spss"] if a.get("khong_spss") else []) + (["--khong-r"] if a.get("khong_r") else [])
    if a.get("chi"):
        ds += ["--chi", _ds_ten(a["chi"], "chi")]
    if not a.get("ap_dung"):
        return {"chay_kho": True, "se_chay": ["bien_phai_sinh.py", *ds],
                "ghi_chu": ("Tính biến phái sinh tất định, ghi CSV ra NGOÀI repo." if lenh == "tinh" else
                            "SPSS và R tự tính lại ĐỘC LẬP từ công thức rồi so từng ô (vài phút).")
                           + " Chỉ biến ĐÃ DUYỆT mới tính. ap_dung: true để chạy."}  # fmt: skip
    return {**chay_cong_cu("bien_phai_sinh.py", ds, 3600), "ghi_chu": CAN_KIEM}


def cc_chay_sap(a: dict) -> dict:
    study = _ma_de_tai(a)
    lenh = a.get("lenh") or "kiem"
    if lenh in ("kiem", "ket_qua"):
        kq = chay_cong_cu("chay_sap_g6.py", ["kiem" if lenh == "kiem" else "ket-qua", "--study", study, "--json"], 300,
                          tron=True)
        v = _json_dau_ra(kq)
        return {**kq, "ket_qua": _gon(v, 6000),
                "ghi_chu": ("Chỉ đọc: đặc tả G6_DAC_TA_SAP.json hợp lệ không, SAP còn khớp sha256_sap không, đã duyệt chưa."
                            if lenh == "kiem" else "Chỉ đọc: kết quả từng phân tích của lượt chạy SAP gần nhất.") + " "
                           + CAN_KIEM}  # fmt: skip
    if lenh != "chay":
        raise ValueError("lenh: kiem · chay · ket_qua")
    khoa = du_lieu_khoa(study)
    if not khoa.get("tep"):
        return {"tu_choi": True, "ly_do": "chưa có dữ liệu ĐÃ KHOÁ (G5) — chạy SAP chỉ sau khi SAP (G4) và dữ liệu (G5) được "
                "NGƯỜI có thẩm quyền khoá. Chi tiết: " + str(khoa.get("ly_do"))}  # fmt: skip
    ds = ["chay", "--study", study] + (["--chi", _ds_ten(a["chi"], "chi")] if a.get("chi") else [])
    if a.get("kiem_cheo", True):
        ds.append("--kiem-cheo")
    if not a.get("ap_dung"):
        kt = chay_cong_cu("chay_sap_g6.py", ["kiem", "--study", study, "--json"], 300, tron=True)
        return {"chay_kho": True, "du_lieu_khoa": khoa, "dac_ta": _gon(_json_dau_ra(kt), 4000), "ma_thoat_kiem": kt["ma_thoat"],
                "se_chay": ["chay_sap_g6.py", *ds],
                "ghi_chu": "Đặc tả phải ĐÃ DUYỆT (thống kê viên/PI) và khớp SAP đã khoá — công cụ tự chặn nếu không. Mỗi phân "
                           "tích một gate (G6 cho vai «chinh», G6_<id> cho mục khác); mục «chua_tu_dong» liệt kê để làm tay. "
                           "ap_dung: true để chạy (có kiểm chéo: lâu)."}  # fmt: skip
    kq = chay_cong_cu("chay_sap_g6.py", ds, 14400)
    return {**kq, "ket_qua": cc_chay_sap({"study": study, "lenh": "ket_qua"}).get("ket_qua")}


def _sc(props: dict, bat_buoc: list[str] | None = None) -> dict:
    return {
        "type": "object",
        "properties": props,
        "required": bat_buoc or [],
        "additionalProperties": False,
    }


_AP = {
    "type": "boolean",
    "description": "true = LÀM thật; mặc định chạy khô (chỉ báo sẽ làm gì)",
}
_ST = {"type": "string", "description": "mã đề tài (thư mục exports/<mã>)"}
_TP = {
    "type": "string",
    "description": "đường dẫn tệp đã nhập (.xlsx/.xlsm Excel hoặc .sav nhập trong SPSS) — NGOÀI repo",
}
_RA = {
    "type": "string",
    "description": "thư mục ra (NGOÀI repo; mặc định cạnh tệp nhập)",
}
CONG_CU = [
    (
        "spss_r_trang_thai",
        "Tình trạng: SPSS (đường dẫn Python của SPSS), Rscript, RStudio, Python dự án; từng đề tài có từ "
        "điển G5, mẫu nhập Excel/SPSS, manifest khoá dữ liệu chưa. Chỉ đọc.",
        _sc({}),
        cc_trang_thai,
    ),
    (
        "nhap_lieu_mau",
        "Sinh MẪU nhập liệu từ từ điển G5: dang=xlsx (Excel có kiểm tra nhập) hoặc sav (nhập thẳng trong SPSS — "
        "SPSS không chặn lỗi lúc gõ). Mẫu không chứa dữ liệu; tệp đã có dữ liệu không bị ghi đè. Chạy khô mặc định.",
        _sc(
            {
                "study": _ST,
                "dang": {"type": "string", "enum": ["xlsx", "sav"]},
                "ghi_de": {"type": "boolean"},
                "ap_dung": _AP,
            },
            ["study"],
        ),
        cc_mau,
    ),
    (
        "nhap_lieu_kiem",
        "KIỂM tệp đã nhập (Excel hoặc .sav) từng ô như REDCap: lỗi cấu trúc, truy vấn giá trị, logic nhánh, luật "
        "DQ, mã thiếu trang; ghi CSV + báo cáo ở thư mục ra NGOÀI repo; KHÔNG gọi cổng tiếp nhận. Trả trạng thái + phát hiện "
        "(trang!ô · cột · mã NC; giá trị ô chữ đã che).",
        _sc({"study": _ST, "tep": _TP, "ra": _RA}, ["study", "tep"]),
        cc_kiem,
    ),
    (
        "nhap_lieu_so_sanh",
        "NHẬP KÉP: so hai lần nhập độc lập từng ô theo mã nghiên cứu; trả tóm tắt (không giá trị — bằng chứng "
        "G5) + các ô lệch (giá trị ô chữ đã che) để đối chiếu phiếu gốc.",
        _sc(
            {"study": _ST, "tep1": _TP, "tep2": _TP, "ra": _RA},
            ["study", "tep1", "tep2"],
        ),
        cc_so_sanh,
    ),
    (
        "nhap_lieu_tiep_nhan",
        "Đưa tệp đã nhập qua CỔNG TIẾP NHẬN chuẩn (quét PII, chép bản chỉ đọc vào exports/<mã>) — CHỈ khi "
        "kiểm SẠCH; tiếp nhận xong tự LÀM SẠCH bản sao (như công cụ lam_sach). Chạy khô mặc định (chỉ kiểm và báo có đủ "
        "điều kiện không).",
        _sc({"study": _ST, "tep": _TP, "ra": _RA, "ap_dung": _AP,
             "lam_sach": {"type": "boolean", "description": "tiếp nhận xong tự làm sạch bản sao (mặc định true)"}},
            ["study", "tep"]),
        cc_tiep_nhan,
    ),
    (
        "spss_r_xuat",
        "Xuất dữ liệu sang SPSS (.sav, khứ hồi từng ô + so từ điển) hoặc R (.rds có nhãn, ba chiều) rồi MỞ SPSS/"
        "RStudio trên máy (mo=false: chỉ xuất). Đã khoá ⇒ bản khoá; chưa khoá ⇒ cần «tep», chỉ xuất BẢN NHÁP khi kiểm sạch. "
        "Bước nào lỗi thì không mở. Chạy khô mặc định.",
        _sc(
            {
                "study": _ST,
                "phan_mem": {"type": "string", "enum": ["spss", "r"]},
                "tep": _TP,
                "mo": {"type": "boolean"},
                "ap_dung": _AP,
            },
            ["study", "phan_mem"],
        ),
        cc_xuat,
    ),  # fmt: skip
    (
        "kiem_cheo_g6",
        "Kiểm chéo kết quả G6 bằng SPSS + R: mặc định ĐỌC trạng thái (khớp/lệch/cũ/chưa chạy); ap_dung: true để "
        "chạy lại (vài phút). Tư vấn — không đổi trạng thái cổng.",
        _sc({"study": _ST, "ap_dung": _AP}, ["study"]),
        cc_kiem_cheo,
    ),
    (
        "phan_tich_g6",
        "PHÂN TÍCH CHÍNH G6 (run_stats_analysis.py): mô tả, Bảng 1, kết cục chính, hồi quy đa biến, sống còn, "
        "dữ liệu thiếu/MI… CHỈ trên dữ liệu ĐÃ KHOÁ (G5, kiểm bằng hàm của cổng) — chưa khoá ⇒ từ chối, không có cờ ghi đè. Đặc "
        "tả theo SAP đã khoá (outcome, group, covariates, hiep_bien_phan_loai, outcome_type kể cả poisson_pr, loc, time/event, "
        "cot_cum, don_vi_phoi_nhiem) hoặc "
        "dung_dac_ta_truoc=true để dùng lại đúng đặc tả lượt trước; KHÔNG tự chọn biến. Mặc định kèm kiểm chéo SPSS + R. Chạy "
        "khô mặc định.",
        _sc(
            {
                "study": _ST,
                "outcome": {"type": "string"},
                "group": {"type": "string"},
                "covariates": {"type": "array", "items": {"type": "string"}},
                "outcome_type": {
                    "type": "string",
                    "enum": ["auto", "binary", "continuous", "ordinal", "poisson_pr"],
                    "description": "poisson_pr = Poisson vững (tỷ số tỷ lệ hiện mắc PR) cho kết cục nhị phân phổ biến",
                },
                "hiep_bien_phan_loai": {"type": "array", "items": {"type": "string"},
                                        "description": "hiệp biến PHÂN LOẠI (mã nguyên ≥ 0) → biến giả, tham chiếu mã nhỏ nhất"},
                "loc": {"type": "string", "description": "quần thể phân tích theo SAP, ngôn ngữ công thức biến phái sinh "
                        "(vd «PhieuHopLe == 1») — giữ ca = 1; SPSS/R lọc y hệt"},
                "time": {"type": "string"},
                "event": {"type": "string"},
                "cot_cum": {"type": "string"},
                "don_vi_phoi_nhiem": {"type": "number"},
                "vars": {"type": "string"},
                "dung_dac_ta_truoc": {"type": "boolean"},
                "kiem_cheo": {"type": "boolean"},
                "ap_dung": _AP,
            },
            ["study"],
        ),
        cc_phan_tich,
    ),  # fmt: skip
    (
        "phan_tich_ket_qua",
        "Đọc kết quả G6 đã chạy (G6_analysis_summary.json, rút gọn): đặc tả, cỡ mẫu, khoá dữ liệu, kết cục "
        "chính, đa biến, sống còn, Bảng 1, dữ liệu thiếu + trạng thái kiểm chéo SPSS/R. Chỉ đọc.",
        _sc({"study": _ST}, ["study"]),
        cc_ket_qua,
    ),
    (
        "lam_sach",
        "LÀM SẠCH bản sao sau cổng tiếp nhận (clean_research_dataset.py): mặc định dữ liệu = bản tiếp nhận ghi trong "
        "study_meta, từ điển = G5_REDCap_dictionary; chỉ thao tác an toàn (bỏ khoảng trắng, chuẩn hoá mã thiếu), giá trị mơ hồ "
        "thành QUERY mở (không tự sửa); giai_quyet_query = tệp giải quyết query do PI/quản lý dữ liệu ghi. Không khoá dữ "
        "liệu. Trả trạng thái, số query mở, ready_for_lock. Chạy khô mặc định.",
        _sc({"study": _ST, "data": {"type": "string", "description": "CSV trong exports/<mã>/ (mặc định: bản tiếp nhận)"},
             "tu_dien": {"type": "string", "description": "từ điển .csv/.json trong exports/<mã>/"},
             "cot_ma_nc": {"type": "string", "description": "cột mã nghiên cứu (kiểm trùng)"},
             "giai_quyet_query": {"type": "string", "description": "tệp giải quyết query .csv/.json trong exports/<mã>/"},
             "ap_dung": _AP}, ["study"]),
        cc_lam_sach,
    ),  # fmt: skip
    (
        "doi_chieu_bien",
        "ĐỐI CHIẾU BIẾN ↔ ĐỀ CƯƠNG (doi_chieu_bien_de_cuong.py): từ điển nhập liệu, biến phái sinh, đặc tả SAP so với bảng "
        "biến số của đề cương nộp và bộ biến G3 đã duyệt — thiếu biến, sai mã, biến phái sinh ngoài đề cương, trường calc không "
        "có công thức, G3 ≠ G5, đặc tả dùng biến lạ. Tách lệch nhập liệu / lệch phân tích; định nghĩa đặt cạnh công thức. Chỉ "
        "đọc — chạy TRƯỚC nhap_lieu_mau và sau mọi lần sửa bộ biến.",
        _sc({"study": _ST}, ["study"]),
        cc_doi_chieu_bien,
    ),
    (
        "g5_con_thieu",
        "CÒN THIẾU GÌ ĐỂ KHOÁ G5: chấm bằng đúng hàm của cổng G5 (g5_quality_gate) ở chế độ KHÔNG GHI — trả trạng "
        "thái, các tiêu chí chưa đạt kèm việc cần làm, khoá kỹ thuật/phê duyệt người đã hợp lệ chưa, vai đã ký. Chỉ đọc.",
        _sc({"study": _ST}, ["study"]),
        cc_g5_con_thieu,
    ),
    (
        "bien_phai_sinh",
        "BIẾN PHÁI SINH (bien_phai_sinh.py, công thức máy đọc ở exports/<mã>/_bien-phai-sinh.csv): lenh=kiem (chỉ đọc — "
        "công thức hợp lệ, đã duyệt chưa, thứ tự tính) · tinh (tính tất định trên CSV, ghi ra NGOÀI repo) · doi_chieu (SPSS "
        "và R tự tính lại độc lập, so từng ô). Chỉ biến ĐÃ DUYỆT mới tính; duyệt (cột nguoi_duyet) là việc của thống kê "
        "viên/PI. tinh/doi_chieu chạy khô mặc định.",
        _sc({"study": _ST, "lenh": {"type": "string", "enum": ["kiem", "tinh", "doi_chieu"]},
             "data": {"type": "string", "description": "CSV (đã khoá hoặc nhập liệu) cho tinh/doi_chieu"},
             "ra": {"type": "string", "description": "thư mục ra NGOÀI repo (tinh)"},
             "chi": {"type": "array", "items": {"type": "string"}, "description": "chỉ các biến này"},
             "khong_spss": {"type": "boolean"}, "khong_r": {"type": "boolean"}, "ap_dung": _AP}, ["study"]),
        cc_bien_phai_sinh,
    ),  # fmt: skip
    (
        "chay_sap_g6",
        "CHẠY TRỌN SAP G6 một lệnh (chay_sap_g6.py) theo đặc tả exports/<mã>/G6_DAC_TA_SAP.json: lenh=kiem (chỉ đọc — đặc "
        "tả hợp lệ, khớp SAP đã khoá, đã duyệt chưa) · chay (mọi phân tích; mỗi mục một gate; CHỈ trên dữ liệu ĐÃ KHOÁ, đặc "
        "tả ĐÃ DUYỆT; mặc định kèm kiểm chéo SPSS + R) · ket_qua (chỉ đọc). Mục «chua_tu_dong» được liệt kê để làm tay. "
        "chay chạy khô mặc định.",
        _sc({"study": _ST, "lenh": {"type": "string", "enum": ["kiem", "chay", "ket_qua"]},
             "chi": {"type": "array", "items": {"type": "string"}, "description": "chỉ chạy các id phân tích này"},
             "kiem_cheo": {"type": "boolean"}, "ap_dung": _AP}, ["study"]),
        cc_chay_sap,
    ),  # fmt: skip
]
_BANG = {ten: ham for ten, _mt, _sc_, ham in CONG_CU}


# ─────────────────────────── giao thức ───────────────────────────


def xu_ly(tin: dict) -> dict | None:
    """Một thông điệp JSON-RPC → phản hồi (None cho thông báo không cần trả lời)."""
    pt, ma = tin.get("method"), tin.get("id")
    if ma is None:
        return None
    if pt == "initialize":
        ban = (tin.get("params") or {}).get("protocolVersion")
        kq = {"protocolVersion": ban if ban in GIAO_THUC else GIAO_THUC[0], "capabilities": {"tools": {"listChanged": False}},
              "serverInfo": {"name": TEN_MAY_CHU, "version": PHIEN_BAN},
              "instructions": "SPSS · R/RStudio · nhập liệu của bác sĩ: mọi bước đi qua công cụ chuẩn của repo y khoa; công cụ "
                              "có tác dụng CHẠY KHÔ mặc định (ap_dung: true mới làm); KHÔNG có công cụ khoá dữ liệu, ký cổng, "
                              "duyệt công thức/đặc tả, đóng query, sửa giá trị hay xoá. Thứ tự đề tài: doi_chieu_bien → nhap_lieu_mau → nhap_lieu_kiem → "
                              "nhap_lieu_tiep_nhan (tự lam_sach) → g5_con_thieu → [người khoá G5] → bien_phai_sinh kiem → "
                              "chay_sap_g6 (hoặc phan_tich_g6) → kiem_cheo_g6. Trả lời bác sĩ bằng tiếng Việt, kèm «Cần bác sĩ kiểm chứng»."}  # fmt: skip
    elif pt == "ping":
        kq = {}
    elif pt == "tools/list":
        kq = {
            "tools": [
                {"name": t, "description": mt, "inputSchema": sc}
                for t, mt, sc, _h in CONG_CU
            ]
        }
    elif pt == "tools/call":
        p = tin.get("params") or {}
        ham = _BANG.get(p.get("name"))
        if ham is None:
            return {"jsonrpc": "2.0", "id": ma, "result": {"isError": True, "content": [
                {"type": "text", "text": f"không có công cụ «{p.get('name')}» (máy chủ không có công cụ khoá/ký/xoá)"}]}}  # fmt: skip
        try:
            ra = ham(p.get("arguments") or {})
            kq = {"content": [{"type": "text", "text": json.dumps(ra, ensure_ascii=False, indent=1, default=str)}],
                  "isError": False}  # fmt: skip
        except Exception as e:  # noqa: BLE001 — lỗi công cụ trả về như kết quả lỗi, máy chủ sống tiếp
            print(traceback.format_exc(), file=sys.stderr)
            kq = {
                "content": [{"type": "text", "text": f"{type(e).__name__}: {e}"[:800]}],
                "isError": True,
            }
    else:
        return {
            "jsonrpc": "2.0",
            "id": ma,
            "error": {"code": -32601, "message": f"không hỗ trợ phương thức {pt}"},
        }
    return {"jsonrpc": "2.0", "id": ma, "result": kq}


def chay(vao=sys.stdin, ra=sys.stdout) -> None:
    for dong in vao:
        dong = dong.strip()
        if not dong:
            continue
        try:
            tin = json.loads(dong)
        except ValueError:
            ra.write(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "JSON hỏng"},
                    }
                )
                + "\n"
            )
            ra.flush()
            continue
        for t in tin if isinstance(tin, list) else [tin]:
            tl = xu_ly(t) if isinstance(t, dict) else None
            if tl is not None:
                ra.write(json.dumps(tl, ensure_ascii=False) + "\n")
                ra.flush()


# ─────────────────────────── cài cho Claude Desktop ───────────────────────────


def tep_cau_hinh_desktop() -> Path:
    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    return (
        Path(os.environ.get("APPDATA", Path.home()))
        / "Claude"
        / "claude_desktop_config.json"
    )


def cai_claude_desktop(ap_dung: bool, tep: Path | None = None) -> dict:
    """Thêm/cập nhật ĐÚNG khoá `mcpServers.spss-r-ebm` (giữ nguyên mọi khoá khác), sao lưu trước khi ghi."""
    tep = tep or tep_cau_hinh_desktop()
    cu: dict = {}
    if tep.exists():
        cu = json.loads(tep.read_text(encoding="utf-8"))
        if not isinstance(cu, dict):
            raise ValueError(f"{tep} không phải đối tượng JSON — không ghi")
    muc = {"command": sys.executable, "args": [str(Path(__file__).resolve())]}
    may_chu = dict(cu.get("mcpServers") or {})
    da_co = may_chu.get(TEN_MAY_CHU)
    may_chu[TEN_MAY_CHU] = muc
    moi = {**cu, "mcpServers": may_chu}
    kq = {"tep": str(tep), "da_co": da_co, "se_ghi": muc, "khong_doi": da_co == muc}
    if ap_dung and da_co != muc:
        tep.parent.mkdir(parents=True, exist_ok=True)
        if tep.exists():
            sao = tep.with_name(
                f"{tep.name}.sao-luu-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            shutil.copy2(tep, sao)
            kq["sao_luu"] = str(sao)
        tep.write_text(
            json.dumps(moi, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        kq["da_ghi"] = True
    return kq


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Máy chủ MCP spss-r-ebm (stdio)")
    ap.add_argument(
        "--cai-claude-desktop",
        action="store_true",
        help="khai máy chủ này cho Claude Desktop (chạy khô)",
    )
    ap.add_argument("--ap-dung", action="store_true")
    ap.add_argument(
        "--liet-ke", action="store_true", help="in danh sách công cụ rồi thoát"
    )
    a = ap.parse_args(argv)
    if a.cai_claude_desktop:
        print(
            json.dumps(cai_claude_desktop(a.ap_dung), ensure_ascii=False, indent=1),
            file=sys.stderr,
        )
        return 0
    if a.liet_ke:
        for t, mt, _sc_, _h in CONG_CU:
            print(f"{t}: {mt}", file=sys.stderr)
        return 0
    chay()
    return 0


if __name__ == "__main__":
    sys.exit(main())
