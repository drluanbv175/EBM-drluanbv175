#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BENCHMARK MÙ ba hệ — biến «có vẻ tốt hơn» thành SỐ ĐO (20/08/2026).

VÌ SAO CÓ
=========
Mọi so sánh Hệ vs Gemini vs ChatGPT tới nay đều do CHÍNH TÔI chấm — người xây hệ
tự chấm hệ, đúng xung đột *grader = generator* đã ghi trong sổ bài học 08/07/2026.
Tool này bỏ hẳn phần chấm chất lượng khỏi tay máy:

  · máy ẨN DANH ba bản trả lời (nhãn A/B/C, xáo theo seed ghi sổ → mở lại được);
  · máy dựng PHIẾU CHẤM MÙ cho bác sĩ (5 tiêu chí × thang 1–5);
  · máy KIỂM CHÉO TRÍCH DẪN của cả ba bằng cùng một thước: định danh có phân giải
    thật không · tiêu đề khớp không · đã bị rút bài chưa;
  · máy KHÔNG chấm điểm chất lượng lâm sàng — điểm là của bác sĩ.

Không có định danh nào trong một bản → ghi «0 định danh, KHÔNG kiểm được»,
TUYỆT ĐỐI không đọc thành «sạch» (bản chia sẻ của chatbot thường rụng hết trích dẫn).

Dùng:
  python3 tools/bench_mu.py --khoi-tao              # dựng thư mục + chép bài của hệ
  python3 tools/bench_mu.py --dung                  # ẩn danh + phiếu chấm + kiểm trích dẫn
  python3 tools/bench_mu.py --mo-nhan               # mở nhãn A/B/C sau khi chấm xong
Mã thoát: 0 · 1 thiếu dữ liệu đầu vào. Cần bác sĩ kiểm chứng.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import random
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[1]
GOC = REPO / "EBM-Dashboards" / "bench"
TT = REPO / "EBM-Dashboards" / "tong_thuat"
HE_THONG = {"he": "Hệ EBM (bài tổng thuật)", "gemini": "Gemini", "chatgpt": "ChatGPT"}
TIEU_CHI = [
    ("dung_nguon", "Đúng nguồn — khẳng định có truy được về nguồn thật không"),
    ("day_du", "Đầy đủ — có bỏ sót khía cạnh quan trọng của câu hỏi không"),
    ("moi", "Mới — có phản ánh guideline/chứng cứ hiện hành không"),
    ("doc_duoc", "Đọc được — trình bày có dùng ngay giữa hai bệnh nhân được không"),
    ("tin_duoc", "Tin được — mức khẳng định có tương xứng chất lượng chứng cứ không"),
]


def _python_venv() -> str:
    """Trình thông dịch venv theo NỀN TẢNG — Windows dùng Scripts\\python.exe, không
    phải bin/python (lớp lỗi đường-dẫn-macOS-cứng đã làm chết công cụ dùng chung
    nhiều lần: ensure_strict_source · docx_sang_pdf · run_retraction_and_med_safety)."""
    goc = Path.home() / ".ebm-venv"
    ung = (goc / "Scripts" / "python.exe") if sys.platform.startswith("win") \
        else (goc / "bin" / "python")
    return str(ung) if ung.exists() else sys.executable


def _nap_tra_dinh_danh():
    sp = importlib.util.spec_from_file_location("_tdd", REPO / "tools" / "tra_dinh_danh.py")
    m = importlib.util.module_from_spec(sp)
    sys.modules["_tdd"] = m
    sp.loader.exec_module(m)
    return m


def _thu_muc_dot() -> Path:
    return GOC / date.today().isoformat()


def khoi_tao() -> int:
    d = _thu_muc_dot()
    bai = sorted(TT.glob("TT_bench-*.md"))
    if not bai:
        print("✗ Chưa có bài benchmark nào của hệ (TT_bench-*.md).")
        return 1
    for i, f in enumerate(bai, 1):
        vb = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^#\s+(.+)$", vb, re.M)
        cau_hoi = m.group(1).strip() if m else f.stem
        thu = d / f"cau-{i:02d}"
        thu.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, thu / "he.md")
        (thu / "CAU-HOI.txt").write_text(cau_hoi + "\n", encoding="utf-8")
        (thu / "HUONG-DAN.txt").write_text(
            "BENCHMARK MÙ — cách dùng thư mục này\n"
            "=" * 44 + "\n\n"
            f"CÂU HỎI: {cau_hoi}\n\n"
            "1. Hỏi CÙNG câu trên ở Gemini và ChatGPT.\n"
            "2. Chép nguyên văn câu trả lời vào hai file trong chính thư mục này:\n"
            "     gemini.md      và      chatgpt.md\n"
            "   (chép cả phần trích dẫn/nguồn nếu có — thiếu thì cứ để nguyên như nó trả,\n"
            "    máy sẽ ghi trung thực «0 định danh» chứ không suy diễn.)\n"
            "3. Chạy:  python3 tools/bench_mu.py --dung\n"
            "4. Chấm phiếu (không thấy tên hệ nào), rồi:  python3 tools/bench_mu.py --mo-nhan\n",
            encoding="utf-8")
        print(f"  ✓ {thu.relative_to(REPO)} — đã có he.md, chờ gemini.md + chatgpt.md")
    print(f"\n✓ Dựng {len(bai)} câu tại {d.relative_to(REPO)}")
    print("Cần bác sĩ kiểm chứng.")
    return 0


def _dinh_danh(vb: str) -> tuple[list[str], list[str]]:
    pmids = sorted(set(re.findall(r"PMID[:\s]*(\d{6,9})", vb, re.I)))
    dois = sorted({d.rstrip(".,;)") for d in re.findall(r"10\.\d{4,9}/\S+", vb)})
    return pmids, dois


def _kiem_trich_dan(vb: str, tdd) -> dict:
    pmids, dois = _dinh_danh(vb)
    kq = {"so_pmid": len(pmids), "so_doi": len(dois), "phan_giai": 0,
          "khong_phan_giai": [], "rut_bai": [], "ghi_chu": ""}
    if not pmids and not dois:
        kq["ghi_chu"] = ("0 định danh trích dẫn trong bản này — KHÔNG kiểm được "
                         "(không đọc thành «sạch»)")
        return kq
    if pmids:
        try:
            bg = tdd.ban_ghi(pmids)
            for r in bg:
                if r.get("loi"):
                    kq["khong_phan_giai"].append(r["pmid"])
                else:
                    kq["phan_giai"] += 1
        except Exception as exc:  # noqa: BLE001
            kq["ghi_chu"] = f"không tra được định danh ({type(exc).__name__}) — chưa kiểm"
            return kq
        try:
            r = subprocess.run(
                [_python_venv(),
                 "medical-ebm-automation/tools/check_citation_retraction.py",
                 "--pmids", ",".join(pmids)],
                cwd=REPO, capture_output=True, text=True, timeout=300, encoding="utf-8", errors="replace")
            for m in re.finditer(r"PMID (\d+):\s*(🔴|⚠️|❗)?\s*(ĐÃ BỊ RÚT|EXPRESSION|"
                                 r"KHÔNG KIỂM ĐƯỢC)", r.stdout):
                kq["rut_bai"].append(f"{m.group(1)} ({m.group(3)})")
        except Exception as exc:  # noqa: BLE001
            kq["ghi_chu"] += f" · chưa kiểm rút bài ({type(exc).__name__})"
    return kq


def dung() -> int:
    d = _thu_muc_dot()
    if not d.exists():
        print("✗ Chưa dựng đợt benchmark nào hôm nay — chạy --khoi-tao trước.")
        return 1
    tdd = _nap_tra_dinh_danh()
    seed = int(date.today().strftime("%Y%m%d"))
    khoa: dict[str, dict[str, str]] = {}
    phan_html: list[str] = []
    for thu in sorted(d.glob("cau-*")):
        cau_hoi = (thu / "CAU-HOI.txt").read_text(encoding="utf-8").strip() \
            if (thu / "CAU-HOI.txt").exists() else thu.name
        ban: dict[str, str] = {}
        for he in HE_THONG:
            for ext in (".md", ".txt", ".html"):
                f = thu / f"{he}{ext}"
                if f.exists():
                    ban[he] = f.read_text(encoding="utf-8", errors="replace")
                    break
        if len(ban) < 2:
            print(f"  ⚠ {thu.name}: mới có {len(ban)}/3 bản — cần ít nhất 2 để so mù")
            continue
        rng = random.Random(f"{seed}-{thu.name}")
        ten = sorted(ban)
        rng.shuffle(ten)
        nhan = dict(zip("ABC", ten))
        khoa[thu.name] = nhan
        muc = [f"<h2>{html.escape(thu.name.upper())} — {html.escape(cau_hoi)}</h2>"]
        for k in sorted(nhan):
            vb = ban[nhan[k]]
            kt = _kiem_trich_dan(vb, tdd)
            (thu / f"ban-{k}.md").write_text(vb, encoding="utf-8", newline="\n")
            canh = []
            if kt["khong_phan_giai"]:
                canh.append(f"<b>{len(kt['khong_phan_giai'])} định danh KHÔNG phân giải "
                            f"được</b> ({', '.join(kt['khong_phan_giai'][:5])})")
            if kt["rut_bai"]:
                canh.append(f"<b>nguồn có vấn đề rút bài:</b> {', '.join(kt['rut_bai'][:5])}")
            if kt["ghi_chu"]:
                canh.append(html.escape(kt["ghi_chu"]))
            muc.append(
                f"<div class='ban'><h3>Bản {k}</h3>"
                f"<p class='so'>Định danh: {kt['so_pmid']} PMID · {kt['so_doi']} DOI · "
                f"phân giải được {kt['phan_giai']}/{kt['so_pmid']}</p>"
                + (f"<p class='canh'>{' · '.join(canh)}</p>" if canh else
                   "<p class='ok'>Không thấy vấn đề định danh</p>")
                + f"<p class='mo'>Đọc bản đầy đủ: <code>{thu.name}/ban-{k}.md</code></p>"
                + "<table class='cham'><tr><th>Tiêu chí</th><th>Điểm 1–5</th></tr>"
                + "".join(f"<tr><td>{html.escape(mo)}</td><td class='o'></td></tr>"
                          for _, mo in TIEU_CHI)
                + "</table></div>")
        phan_html.append("<section>" + "".join(muc) + "</section>")
    if not phan_html:
        print("✗ Chưa câu nào đủ bản để so mù.")
        return 1
    (d / "khoa-mo-nhan.json").write_text(
        json.dumps({"seed": seed, "khoa": khoa, "ngay": date.today().isoformat()},
                   ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    ra = d / "phieu-cham-mu.html"
    ra.write_text(f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<title>Phiếu chấm mù — {date.today():%d/%m/%Y}</title><style>
body{{font-family:'Times New Roman',Times,serif;background:#f4f1e8;color:#1c1a15;
font-size:16px;line-height:1.6;padding:30px 16px}}
main{{max-width:900px;margin:0 auto;background:#fffdf7;border:1px solid #e2dccb;padding:38px 44px}}
h1{{font-size:1.5rem;text-align:center}} .mo{{color:#6d675a;font-style:italic;font-size:.9rem}}
h2{{font-size:1.05rem;margin:26px 0 10px;border-bottom:1px solid #c9c2b2;padding-bottom:5px}}
h3{{font-size:1rem;margin:14px 0 4px}}
.ban{{border:1px solid #e2dccb;padding:12px 16px;margin:10px 0;background:#faf8f1}}
.so{{font-size:.9rem;margin:2px 0}} .canh{{color:#b91c1c;font-size:.9rem}}
.ok{{color:#15803d;font-size:.9rem}}
table.cham{{border-collapse:collapse;width:100%;margin-top:8px}}
table.cham th,table.cham td{{border:1px solid #c9c2b2;padding:6px 10px;font-size:.92rem;text-align:left}}
td.o{{width:110px;height:26px}}
@media print{{body{{background:#fff}}main{{border:none}}}}
</style></head><body><main>
<h1>Phiếu chấm mù — Hệ vs Gemini vs ChatGPT</h1>
<p class="mo" style="text-align:center">{date.today():%d/%m/%Y} · nhãn A/B/C do máy xáo,
máy KHÔNG biết bản nào hơn và KHÔNG chấm chất lượng — điểm là của bác sĩ.<br>
Thang 1–5 cho mỗi tiêu chí: 1 = kém, 3 = tạm dùng, 5 = tốt.</p>
{''.join(phan_html)}
<p class="mo">Chấm xong chạy <code>python3 tools/bench_mu.py --mo-nhan</code> để lộ nhãn.
Phần kiểm định danh áp CÙNG một thước cho cả ba bản. Cần bác sĩ kiểm chứng.</p>
</main></body></html>""", encoding="utf-8", newline="\n")
    print(f"✓ {ra.relative_to(REPO)}")
    print(f"  {len(phan_html)} câu · nhãn đã niêm ở khoa-mo-nhan.json (mở sau khi chấm)")
    print("Cần bác sĩ kiểm chứng.")
    return 0


def mo_nhan() -> int:
    d = _thu_muc_dot()
    f = d / "khoa-mo-nhan.json"
    if not f.exists():
        print("✗ Chưa có khoá nhãn cho đợt hôm nay.")
        return 1
    js = json.loads(f.read_text(encoding="utf-8"))
    print(f"MỞ NHÃN — đợt {js['ngay']}\n")
    for cau, nhan in sorted(js["khoa"].items()):
        print(f"■ {cau}")
        for k in sorted(nhan):
            print(f"   Bản {k} = {HE_THONG.get(nhan[k], nhan[k])}")
    print("\nSo điểm bác sĩ đã chấm với nhãn này. Cần bác sĩ kiểm chứng.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Benchmark mù ba hệ trả lời chứng cứ")
    ap.add_argument("--khoi-tao", action="store_true")
    ap.add_argument("--dung", action="store_true")
    ap.add_argument("--mo-nhan", action="store_true")
    a = ap.parse_args()
    if a.khoi_tao:
        return khoi_tao()
    if a.dung:
        return dung()
    if a.mo_nhan:
        return mo_nhan()
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
